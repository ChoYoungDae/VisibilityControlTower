"""
Visibility Control Tower — API (컨셉 데모).

`db/visibility_control_tower.db`(SQLite)를 읽어서 목업(`visibility_control_
tower_mockup.html`)이 지금까지 하드코딩해서 쓰던 JS 데이터 객체(rowData/
VESSEL_MMSI/sectionStats/bookingData/arrivalData/dndData/itemCatalog 등)와
동일한 모양으로 JSON을 돌려준다 — 프런트엔드 렌더링 로직은 최대한 그대로
두고 "데이터 출처만" 하드코딩에서 API로 바꾸는 것이 이번 연동의 목표다.

실행(로컬, SQLite): uvicorn main:app --reload --port 8000  (이 폴더에서)
실행(Vercel, Supabase): DATABASE_URL 환경변수가 있으면 자동으로 Postgres를 씀.
문서: http://localhost:8000/docs (FastAPI 자동 생성)
"""
import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = Path(__file__).parent.parent / "db" / "visibility_control_tower.db"
DATABASE_URL = os.environ.get("DATABASE_URL")  # 있으면 Supabase(Postgres), 없으면 로컬 SQLite

app = FastAPI(title="Visibility Control Tower API", version="0.1.0")

# 로컬에서는 목업 정적 서버(8123)와 API(8000)가 오리진이 다르고, Vercel에서는
# 같은 오리진(/api)이라 CORS가 관여하지 않는다 — 컨셉 데모라 어차피 전체 허용.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


_pg_conn = None  # Vercel 서버리스 함수가 warm 상태로 재사용될 때 커넥션도 같이 재사용(요청마다 새로 열면 느림)


def _get_pg_conn():
    global _pg_conn
    import psycopg2

    if _pg_conn is None or _pg_conn.closed:
        _pg_conn = psycopg2.connect(DATABASE_URL)
        _pg_conn.autocommit = True  # 읽기 전용 API — 트랜잭션을 열어두지 않아야 pooler가 커넥션을 바로 회수 가능
    return _pg_conn


def query(sql, params=()):
    """sql은 SQLite 방언(? 플레이스홀더)으로 작성 — Postgres 백엔드일 땐 %s로 바꿔서 실행."""
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras

        global _pg_conn
        try:
            conn = _get_pg_conn()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql.replace("?", "%s"), params)
                return [dict(r) for r in cur.fetchall()]
        except psycopg2.OperationalError:
            # 재사용하던 커넥션이 유휴 타임아웃 등으로 끊겼을 수 있음 — 한 번만 재연결 재시도.
            _pg_conn = None
            conn = _get_pg_conn()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql.replace("?", "%s"), params)
                return [dict(r) for r in cur.fetchall()]

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/api/health")
def health():
    if DATABASE_URL:
        return {"status": "ok", "db": "supabase (postgres)"}
    if not DB_PATH.exists():
        raise HTTPException(500, "DB 파일이 없습니다 — db/build_db.py를 먼저 실행하세요.")
    return {"status": "ok", "db": str(DB_PATH)}


# =============================================================
# 화물 탭 (Transportation — Cargo)
# =============================================================

@app.get("/api/cargo/tracking")
def cargo_tracking():
    """구 rowData — id를 key로 하는 dict로 재구성해서 반환(프런트가 바로 lookup 가능하게)."""
    rows = query("SELECT * FROM cargo_tracking")
    return {r["id"]: r for r in rows}


@app.get("/api/cargo/section-stats")
def cargo_section_stats():
    """구 sectionStats — {scope: {stage: {t, d}}} 모양으로 재구성."""
    rows = query("SELECT * FROM cargo_section_stats")
    out = {}
    for r in rows:
        out.setdefault(r["scope"], {})[r["stage"]] = {"t": r["total"], "d": r["delayed"]}
    return out


@app.get("/api/cargo/vessel-mmsi")
def vessel_mmsi():
    rows = query("SELECT vessel_name, mmsi FROM vessel_mmsi")
    return {r["vessel_name"]: r["mmsi"] for r in rows}


# =============================================================
# 업무 탭 (Transportation — Operation)
# =============================================================

BOOKING_BADGE_COLOR = {"진행중": "warn", "롤오버": "crit", "확정 · 서류 완료": "ok"}


@app.get("/api/operation/bookings")
def bookings():
    """구 bookingData — key를 목업 HTML의 data-detail 값(소문자 booking_no)에 맞춘다."""
    rows = query("SELECT * FROM booking")
    po_rows = query("SELECT * FROM booking_po")
    po_by_booking = {}
    for p in po_rows:
        po_by_booking.setdefault(p["booking_no"], []).append(p["po_no"])

    out = {}
    for r in rows:
        key = r["booking_no"].lower()
        out[key] = {
            "title": r["booking_no"],
            "route": f"{r['route']} · {r['cid']} · {r['stage']}",
            "badge": {"c": BOOKING_BADGE_COLOR.get(r["status"], "neutral"), "t": r["status"]},
            "pos": po_by_booking.get(r["booking_no"], []),
            "cutoff": [
                {"l": "SI Cut-off", "v": r["si_cutoff"], "note": r["si_note"], "cls": r["si_class"] or ""},
                {"l": "VGM Cut-off", "v": r["vgm_cutoff"], "note": r["vgm_note"], "cls": r["vgm_class"] or ""},
                {"l": "CY(게이트인) Cut-off", "v": r["cy_cutoff"], "note": r["cy_note"], "cls": r["cy_class"] or ""},
            ],
            "docs": [
                {"l": "수출통관", "v": r["export_customs"]},
                {"l": "B/L", "v": r["bl_status"] + (f" — {r['bl_no']}" if r["bl_no"] else "")},
            ],
        }
    return out


ARRIVAL_BADGE_COLOR = {
    "통관 대기 — Inland Routing 잠김": "neutral",
    "비교 가능": "accent",
    "실행완료": "ok",
    "비교 가능 (통관 해당없음)": "accent",
}
# 목업 HTML의 data-detail 코드(arr-mksu 등)는 cid에서 기계적으로 못 뽑아서
# 컨셉 데모용으로 고정 매핑한다(§9.1 실제 Container-Item Mapping과 무관).
ARRIVAL_ID_TO_CID = {
    "arr-mksu": "MSKU7712901", "arr-tclu": "TCLU5520134",
    "arr-hlxu": "HLXU3308719", "arr-sel": "SEL-AIR-88231",
}


@app.get("/api/operation/arrivals")
def arrivals():
    """구 arrivalData."""
    rows = {r["cid"]: r for r in query("SELECT * FROM arrival_prep")}
    options = query("SELECT * FROM inland_routing_option")
    options_by_cid = {}
    for o in options:
        options_by_cid.setdefault(o["cid"], []).append({
            "mode": o["mode"], "lead": o["lead_time"], "cost": o["cost"] or "-",
            "free": o["free_time"] or "-", "rec": o["recommendation"], "selected": bool(o["selected"]),
        })

    out = {}
    for key, cid in ARRIVAL_ID_TO_CID.items():
        r = rows.get(cid)
        if not r:
            continue
        customs = [{"l": "수입통관 상태", "v": r["import_customs"]}]
        if r["customs_expected_or_done"]:
            customs.append({"l": "완료일", "v": r["customs_expected_or_done"]})
        elif r["customs_expected"]:
            customs.append({"l": "예상 완료", "v": r["customs_expected"]})
        else:
            customs.append({"l": "-", "v": "-"})

        entry = {
            "title": r["cid"], "route": f"{r['po']} · {r['route']}",
            "badge": {"c": ARRIVAL_BADGE_COLOR.get(r["status"], "neutral"), "t": r["status"]},
            "customs": customs, "locked": bool(r["locked"]), "lockedMsg": r["locked_msg"],
            "inland": options_by_cid.get(cid, []),
        }
        if cid == "HLXU3308719":
            entry["note"] = "이 결과가 화물 탭의 FDEST ETA 재계산에 반영되었습니다."
        out[key] = entry
    return out


@app.get("/api/operation/schedule-search")
def schedule_search():
    return query("SELECT * FROM schedule_search_result")


# =============================================================
# 비용 탭 (Transportation — Cost)
# =============================================================

@app.get("/api/cost/dnd")
def dnd():
    """구 dndData."""
    rows = query("SELECT * FROM dnd")
    buckets = query("SELECT * FROM dnd_weekly_bucket ORDER BY dnd_id, week_index")
    buckets_by_id = {}
    for b in buckets:
        buckets_by_id.setdefault(b["dnd_id"], []).append(b["days"])

    out = {}
    for r in rows:
        if r["pending"]:
            info = [
                {"l": "Free Time 만료 예정일", "v": r["free_time_expiry"]},
                {"l": "남은 일수", "v": f"D-{r['days_remaining']}"},
                {"l": "발생 시 예상 일일 요율", "v": f"약 ₩{r['daily_rate']:,} / 일"},
            ]
        else:
            info = [
                {"l": "Free Time 만료일", "v": r["free_time_expiry"]},
                {"l": "경과일수", "v": f"{r['days_elapsed']}일"},
                {"l": "일일 요율", "v": f"₩{r['daily_rate']:,} / 일"},
            ]
        out[r["id"]] = {
            "title": r["cid"], "route": f"{r['po']} · {r['route']}",
            "badge": {"c": r["badge_color"], "t": r["status"]},
            "info": info, "pending": bool(r["pending"]),
            "elapsedDays": r["days_elapsed"], "weekBuckets": buckets_by_id.get(r["id"], []),
        }
    return out


@app.get("/api/cost/monthly")
def monthly_cost():
    return query("SELECT * FROM monthly_cost ORDER BY month")


# =============================================================
# 재고 탭 (Inventory)
# =============================================================

@app.get("/api/inventory/items")
def inventory_items():
    """구 itemCatalog — 목업 buildTimeline()이 기대하는 shipments[] 모양 그대로."""
    items = query("SELECT * FROM item")
    onhand = {r["item_id"]: r["on_hand_qty"] for r in query("SELECT * FROM inventory_onhand")}
    safety = {r["item_id"]: r["safety_stock_qty"] for r in query("SELECT * FROM inventory_safety_stock")}
    base_date = query("SELECT MIN(outbound_date) d FROM inventory_outbound")[0]["d"]
    outbound_rows = query(
        "SELECT item_id, outbound_qty FROM inventory_outbound WHERE outbound_date = ?", (base_date,)
    )
    daily_outbound = {r["item_id"]: r["outbound_qty"] for r in outbound_rows}
    shipments = query("SELECT * FROM item_shipment")

    out = {}
    for it in items:
        item_id = it["item_id"]
        item_shipments = [
            {
                "id": s["container_no"], "po": s["po_no"], "mode": s["mode"],
                "stageLabel": s["stage_label"], "qty": s["qty"],
                "fdestInitEta": _md_display(s["fdest_init_eta"]),
                "fdestEta": _md_display(s["fdest_eta"]),
                "whDate": s["wh_in_date"], "delayed": bool(s["delayed"]),
            }
            for s in shipments if s["item_id"] == item_id
        ]
        out[item_id] = {
            "productType": it["product_type"],
            "onhand": onhand.get(item_id, 0),
            "safetyStock": safety.get(item_id, 0),
            "dailyOutbound": daily_outbound.get(item_id, 0),
            "shipments": item_shipments,
        }
    return out


def _md_display(iso_date):
    """'2026-08-17' -> '8/17' (목업 JS의 parseDateMD가 기대하는 M/D 포맷으로 되돌림)."""
    if not iso_date:
        return None
    parts = iso_date.split("-")
    return f"{int(parts[1])}/{int(parts[2])}"


# =============================================================
# 발주 시점/수량 추천 (신규 컨셉)
# =============================================================

@app.get("/api/inventory/reorder-recommendation")
def reorder_recommendation():
    rows = query("""
        SELECT r.*, i.item_name, l.pol, l.pod, l.carrier, l.mode
        FROM reorder_recommendation r
        JOIN item i ON i.item_id = r.item_id
        LEFT JOIN lead_time_stats l ON l.lane_id = r.lane_id
        ORDER BY (r.target_date IS NULL), r.target_date
    """)
    return rows


@app.get("/api/inventory/reorder-recommendation/{item_id}")
def reorder_recommendation_one(item_id: str):
    rows = query("""
        SELECT r.*, i.item_name, l.pol, l.pod, l.carrier, l.mode, l.n, l.mean_days
        FROM reorder_recommendation r
        JOIN item i ON i.item_id = r.item_id
        LEFT JOIN lead_time_stats l ON l.lane_id = r.lane_id
        WHERE r.item_id = ?
    """, (item_id,))
    if not rows:
        raise HTTPException(404, f"item_id={item_id} 추천 없음")
    return rows[0]
