"""
Visibility Control Tower — Supabase(Postgres) 시딩 스크립트 (컨셉 데모).

db/build_db.py(SQLite 버전)와 로직은 동일하다 — synthetic-data/*.csv를
schema_postgres.sql 구조로 적재하고, 재고 투영(§9.4) + 노선별 리드타임 P95를
결합해 reorder_recommendation을 계산해 채운다. 차이는 대상 DB뿐이다: 로컬
SQLite 파일 대신 DATABASE_URL 환경변수로 지정한 Supabase Postgres에 쓴다.

실행 전: Supabase SQL Editor에서 schema_postgres.sql을 먼저 실행해 테이블을
만들어둘 것 (이 스크립트는 스키마를 새로 만들지 않고 데이터만 적재한다 —
재실행 시 기존 데이터와 충돌하지 않으려면 Supabase에서 테이블을 비우고
다시 실행).

실행:
    pip install sqlalchemy psycopg2-binary pandas
    DATABASE_URL="postgresql://...supabase pooler 연결 문자열..." python seed_supabase.py
"""
import os
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

DB_DIR = Path(__file__).parent
DATA_DIR = DB_DIR.parent / "synthetic-data"

BASE_DATE = date(2026, 8, 7)
HORIZON_END = date(2026, 9, 30)

# CSV 파일 -> 테이블명 매핑 (build_db.py와 동일 — 컬럼명이 CSV와 스키마에 이미 일치)
CSV_TABLE_MAP = [
    ("wd_item_master.csv", "item"),
    ("wd_onhand.csv", "inventory_onhand"),
    ("wd_safety_stock.csv", "inventory_safety_stock"),
    ("wd_outbound.csv", "inventory_outbound"),
    ("item_shipments.csv", "item_shipment"),
    ("vessel_mmsi.csv", "vessel_mmsi"),
    ("cargo_tracking.csv", "cargo_tracking"),
    ("cargo_section_stats.csv", "cargo_section_stats"),
    ("booking.csv", "booking"),
    ("booking_po.csv", "booking_po"),
    ("arrival_prep.csv", "arrival_prep"),
    ("inland_routing_option.csv", "inland_routing_option"),
    ("schedule_search_result.csv", "schedule_search_result"),
    ("dnd.csv", "dnd"),
    ("dnd_weekly_bucket.csv", "dnd_weekly_bucket"),
    ("monthly_cost.csv", "monthly_cost"),
    ("shipment_history.csv", "shipment_history"),
    ("lead_time_stats.csv", "lead_time_stats"),
    ("item_primary_lane.csv", "item_primary_lane"),
]


def load_csvs(engine):
    for csv_name, table in CSV_TABLE_MAP:
        df = pd.read_csv(DATA_DIR / csv_name)
        df.to_sql(table, engine, if_exists="append", index=False)
        print(f"  적재: {csv_name} -> {table} ({len(df)}행)")


def compute_reorder_recommendations(engine):
    """재고 투영(§9.4) + 노선별 리드타임 P95를 결합해 발주 추천을 계산한다."""
    items = pd.read_sql("SELECT * FROM item", engine)
    onhand = pd.read_sql("SELECT * FROM inventory_onhand", engine).set_index("item_id")
    safety = pd.read_sql("SELECT * FROM inventory_safety_stock", engine).set_index("item_id")
    outbound = pd.read_sql("SELECT item_id, outbound_date, outbound_qty FROM inventory_outbound", engine)
    inbound = pd.read_sql(
        "SELECT item_id, fdest_eta, qty FROM item_shipment WHERE container_no IS NOT NULL AND fdest_eta IS NOT NULL",
        engine,
    )
    lanes = pd.read_sql("SELECT * FROM item_primary_lane", engine).set_index("item_id")
    lane_stats = pd.read_sql("SELECT * FROM lead_time_stats", engine).set_index("lane_id")

    horizon = [BASE_DATE + timedelta(days=i) for i in range((HORIZON_END - BASE_DATE).days + 1)]
    rows = []

    for item_id in items["item_id"]:
        onhand_qty = int(onhand.loc[item_id, "on_hand_qty"])
        safety_qty = int(safety.loc[item_id, "safety_stock_qty"])

        ob = outbound[outbound["item_id"] == item_id].groupby("outbound_date")["outbound_qty"].sum()
        ib = inbound[inbound["item_id"] == item_id].groupby("fdest_eta")["qty"].sum()

        cum_in, cum_out = 0, 0
        target_date, target_event, projected_at_target = None, "None", None
        for d in horizon:
            iso = d.isoformat()
            cum_in += int(ib.get(iso, 0))
            cum_out += int(ob.get(iso, 0))
            projected = onhand_qty + cum_in - cum_out

            if projected <= 0:
                target_date, target_event, projected_at_target = d, "Shortage", projected
                break
            elif projected <= safety_qty and target_event == "None":
                # Risk는 계속 갱신하지 않고 "처음 진입한 날"만 기록,
                # 이후 Shortage가 나오면 위에서 덮어씀(더 급한 이벤트 우선).
                target_date, target_event, projected_at_target = d, "Risk", projected

        if target_event == "None":
            rows.append(dict(
                item_id=item_id, target_event="None", target_date=None, recommended_qty=None,
                lane_id=None, lead_time_p50_days=None, lead_time_p95_days=None,
                recommended_order_by_date=None, days_until_order_by=None,
                urgency="none",
                if_ordered_today_arrival_p50=None, if_ordered_today_arrival_p95=None,
                computed_at=BASE_DATE.isoformat(),
            ))
            continue

        lane_id = lanes.loc[item_id, "lane_id"]
        stats = lane_stats.loc[lane_id]
        p50, p95 = int(stats["p50_days"]), int(stats["p95_days"])

        recommended_qty = max(0, safety_qty - projected_at_target)
        order_by = target_date - timedelta(days=p95)
        days_until = (order_by - BASE_DATE).days
        urgency = "urgent" if days_until < 0 else "normal"

        # urgent(이미 권장 발주 시점을 지난 경우)여도 "그럼 언제쯤 오나"는 답할 수
        # 있어야 함 — 오늘(기준일) 발주한다고 가정하면 이 노선 리드타임 P50/P95만큼
        # 지난 뒤 도착한다는 뜻이므로 그대로 더해서 보여준다.
        if_ordered_today_p50 = BASE_DATE + timedelta(days=p50)
        if_ordered_today_p95 = BASE_DATE + timedelta(days=p95)

        rows.append(dict(
            item_id=item_id, target_event=target_event, target_date=target_date.isoformat(),
            recommended_qty=int(recommended_qty), lane_id=lane_id,
            lead_time_p50_days=p50, lead_time_p95_days=p95,
            recommended_order_by_date=order_by.isoformat(), days_until_order_by=days_until,
            urgency=urgency,
            if_ordered_today_arrival_p50=if_ordered_today_p50.isoformat(),
            if_ordered_today_arrival_p95=if_ordered_today_p95.isoformat(),
            computed_at=BASE_DATE.isoformat(),
        ))

    df_reco = pd.DataFrame(rows)
    df_reco.to_sql("reorder_recommendation", engine, if_exists="append", index=False)
    df_reco.to_csv(DATA_DIR / "reorder_recommendation.csv", index=False)
    print(f"  계산: reorder_recommendation ({len(df_reco)}행) -> Supabase + synthetic-data/reorder_recommendation.csv")
    return df_reco


def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "DATABASE_URL 환경변수가 필요합니다 — Supabase Project Settings > Database > "
            "Connection pooling(Transaction mode, 포트 6543)에서 복사한 연결 문자열."
        )
    # SQLAlchemy는 postgresql+psycopg2:// 스킴을 기대하지만 Supabase가 주는 값은
    # postgresql://라서 그대로 넣으면 드라이버를 못 찾는다 — 여기서 보정한다.
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    engine = create_engine(database_url)

    print("CSV 적재... (Supabase SQL Editor에서 schema_postgres.sql을 먼저 실행해뒀어야 함)")
    load_csvs(engine)
    print("발주 추천 계산...")
    df_reco = compute_reorder_recommendations(engine)

    print("\n완료: Supabase에 시딩됨")
    print("\n=== 발주 추천 결과 미리보기 ===")
    with pd.option_context("display.width", 160, "display.max_columns", 20):
        print(df_reco[["item_id", "target_event", "target_date", "recommended_qty",
                        "lane_id", "lead_time_p95_days", "recommended_order_by_date", "urgency"]])


if __name__ == "__main__":
    main()
