"""
Visibility Control Tower — SQLite DB 빌드 스크립트 (컨셉 데모).

synthetic-data/*.csv 전체를 schema.sql 구조로 적재하고, 마지막 단계에서
"재고 투영(Projected Inventory) + 노선별 리드타임 P95"를 결합해
reorder_recommendation 테이블을 계산·채운다.

이 스크립트가 증명하려는 것: Inventory 도메인(§9)과 Transportation 도메인(§8)
데이터가 하나의 DB에 같이 들어가면, "이 Item은 언제까지 얼마나 발주해야
Safety Stock을 유지하는지"를 자동으로 뽑아낼 수 있다는 것. Shortage/부족수량
계산은 §9.4 결정론적 공식 그대로이고, 리드타임 P95만 통계(§7 방법론과 같은
축의 P50/P95 개념)를 쓴다 — AI/ML이 수요를 예측하거나 발주를 실행하지 않는다.

실행: python build_db.py
출력: visibility_control_tower.db (같은 폴더)
"""
import sqlite3
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

DB_DIR = Path(__file__).parent
DATA_DIR = DB_DIR.parent / "synthetic-data"
DB_PATH = DB_DIR / "visibility_control_tower.db"
SCHEMA_PATH = DB_DIR / "schema.sql"

BASE_DATE = date(2026, 8, 7)
HORIZON_END = date(2026, 9, 30)

# CSV 파일 -> 테이블명 매핑 (컬럼명은 CSV와 schema.sql이 이미 일치하도록 맞춰둠)
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


def build_schema(conn):
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_csvs(conn):
    for csv_name, table in CSV_TABLE_MAP:
        df = pd.read_csv(DATA_DIR / csv_name)
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"  적재: {csv_name} -> {table} ({len(df)}행)")


def compute_reorder_recommendations(conn):
    """재고 투영(§9.4) + 노선별 리드타임 P95를 결합해 발주 추천을 계산한다."""
    items = pd.read_sql("SELECT * FROM item", conn)
    onhand = pd.read_sql("SELECT * FROM inventory_onhand", conn).set_index("item_id")
    safety = pd.read_sql("SELECT * FROM inventory_safety_stock", conn).set_index("item_id")
    outbound = pd.read_sql("SELECT item_id, outbound_date, outbound_qty FROM inventory_outbound", conn)
    inbound = pd.read_sql(
        "SELECT item_id, fdest_eta, qty FROM item_shipment WHERE container_no IS NOT NULL AND fdest_eta IS NOT NULL",
        conn,
    )
    lanes = pd.read_sql("SELECT * FROM item_primary_lane", conn).set_index("item_id")
    lane_stats = pd.read_sql("SELECT * FROM lead_time_stats", conn).set_index("lane_id")

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
    df_reco.to_sql("reorder_recommendation", conn, if_exists="append", index=False)
    df_reco.to_csv(DATA_DIR / "reorder_recommendation.csv", index=False)
    print(f"  계산: reorder_recommendation ({len(df_reco)}행) -> DB + synthetic-data/reorder_recommendation.csv")
    return df_reco


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        print("스키마 생성...")
        build_schema(conn)
        print("CSV 적재...")
        load_csvs(conn)
        print("발주 추천 계산...")
        df_reco = compute_reorder_recommendations(conn)
        conn.commit()
    finally:
        conn.close()

    print(f"\n완료: {DB_PATH}")
    print("\n=== 발주 추천 결과 미리보기 ===")
    with pd.option_context("display.width", 160, "display.max_columns", 20):
        print(df_reco[["item_id", "target_event", "target_date", "recommended_qty",
                        "lane_id", "lead_time_p95_days", "recommended_order_by_date", "urgency"]])


if __name__ == "__main__":
    main()
