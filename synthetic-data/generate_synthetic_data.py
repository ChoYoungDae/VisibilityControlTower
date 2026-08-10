"""
Item 단위 통합재고관리 — VisibilityControlTower_PRD.md §8(Inventory 기능요구사항,
구 ItemLevel_InventoryManagement_PRD.md, 2026-08-07 §8로 통합됨) 용 합성 데이터 생성.

실제 raw data(raw data/Tracking.xlsx)의 Model(=Item) 값과 FDEST ETA/QTY를 그대로 재사용하고,
그 위에 W&D(On-hand/Outbound/Safety Stock) 합성 데이터를 얹어 Normal/Risk/Shortage/Recovery
4가지 상태가 모두 나오도록 설계했다. 화면(목업) 데모용.

별도로 Inventory Engine 단위테스트용 Tracking 예외 케이스(Pre-carriage, 입고버퍼 우선순위,
완전 동일 중복)도 함께 생성한다 (§8.4/§8.10 대응).

실행: python generate_synthetic_data.py
출력: synthetic-data/*.csv (source_type=SYNTHETIC 명시)
"""
import pandas as pd
import numpy as np
from datetime import date, timedelta

OUT_DIR = "."
BASE_DATE = date(2026, 8, 7)   # 기준일 (오늘)
HORIZON_END = date(2026, 9, 30)

# ---------------------------------------------------------------------------
# 1. Item Master — 실제 Tracking.xlsx의 Model 값 그대로 사용
# ---------------------------------------------------------------------------
ITEMS = {
    "REFRIGERATOR":                     {"scenario": "Shortage -> Recovery", "product_type": "CSKD"},
    "RO COMPRESSOR(ROTARY COMPRESSOR)": {"scenario": "Risk only (no Shortage)", "product_type": "CSKD"},
    "MOTOR":                            {"scenario": "Normal 전체 기간", "product_type": "CSKD"},
    "PARTS FOR REFRIGERATOR":           {"scenario": "Shortage(기준일부터) -> Recovery", "product_type": "CSKD"},
    "REFRIGERATORS COMPRESSOR":         {"scenario": "Risk, 간발의 Recovery", "product_type": "SET"},
    "MICROWAVE OVEN":                   {"scenario": "Normal, Pre-carriage Pipeline 데모", "product_type": "CSKD"},
    "TEMPERATURE SENSOR":               {"scenario": "Normal 전체 기간 (대비 사례)", "product_type": "CSKD"},
}

item_master = pd.DataFrame([
    {
        "item_id": k,
        "item_name": k,
        "product_type": v["product_type"],
        # TEMPERATURE SENSOR는 raw data/Tracking.xlsx의 실제 Model 값이 아니라
        # "항상 Normal인 대비 사례"를 보여주기 위해 목업에 추가한 항목이다.
        "source": "REAL_MODEL_VALUE" if k != "TEMPERATURE SENSOR" else "SYNTHETIC_ITEM",
    } for k, v in ITEMS.items()
])
item_master.to_csv(f"{OUT_DIR}/wd_item_master.csv", index=False)

# ---------------------------------------------------------------------------
# 2. On-hand (기준일 스냅샷 1건씩) + Safety Stock
# ---------------------------------------------------------------------------
# 아래 세 딕셔너리는 `visibility_control_tower_mockup.html`의 itemCatalog와 정확히
# 일치해야 한다 — 2026-08-04 최초 생성 이후 목업 쪽 값이 여러 세션에 걸쳐 손으로
# 더 현실적인 비율(입고/출고 규모 정합)로 다듬어지면서 이 CSV와 어긋나 있었다
# (예: REFRIGERATOR on-hand 60,000 → 100,000). 2026-08-10 세션에 목업 기준으로 재동기화.
ONHAND = {
    "REFRIGERATOR": 100000,
    "RO COMPRESSOR(ROTARY COMPRESSOR)": 78000,
    "MOTOR": 30000,
    "PARTS FOR REFRIGERATOR": 9500,
    "REFRIGERATORS COMPRESSOR": 3100,
    "MICROWAVE OVEN": 1800,
    "TEMPERATURE SENSOR": 12000,
}
SAFETY_STOCK = {
    "REFRIGERATOR": 90000,
    "RO COMPRESSOR(ROTARY COMPRESSOR)": 60000,
    "MOTOR": 28000,
    "PARTS FOR REFRIGERATOR": 10500,
    "REFRIGERATORS COMPRESSOR": 2400,
    "MICROWAVE OVEN": 1500,
    "TEMPERATURE SENSOR": 8000,
}
DAILY_OUTBOUND = {
    "REFRIGERATOR": 2500,
    "RO COMPRESSOR(ROTARY COMPRESSOR)": 7800,
    "MOTOR": 3600,
    "PARTS FOR REFRIGERATOR": 1300,
    "REFRIGERATORS COMPRESSOR": 220,
    "MICROWAVE OVEN": 60,
    "TEMPERATURE SENSOR": 180,
}

onhand_rows = [
    {"item_id": k, "snapshot_date": BASE_DATE.isoformat(), "on_hand_qty": v, "source_type": "SYNTHETIC"}
    for k, v in ONHAND.items()
]
pd.DataFrame(onhand_rows).to_csv(f"{OUT_DIR}/wd_onhand.csv", index=False)

ss_rows = [
    {"item_id": k, "effective_date": BASE_DATE.isoformat(), "safety_stock_qty": v, "source_type": "SYNTHETIC"}
    for k, v in SAFETY_STOCK.items()
]
pd.DataFrame(ss_rows).to_csv(f"{OUT_DIR}/wd_safety_stock.csv", index=False)

# ---------------------------------------------------------------------------
# 3. Outbound — 기준일부터 매일 일정량 차감 (단순 등차, 데모 목적)
# ---------------------------------------------------------------------------
outbound_rows = []
d = BASE_DATE
while d <= HORIZON_END:
    for item, qty in DAILY_OUTBOUND.items():
        outbound_rows.append({
            "item_id": item, "outbound_date": d.isoformat(),
            "outbound_qty": qty, "source_type": "SYNTHETIC",
        })
    d += timedelta(days=1)
pd.DataFrame(outbound_rows).to_csv(f"{OUT_DIR}/wd_outbound.csv", index=False)

# ---------------------------------------------------------------------------
# 4. MICROWAVE OVEN 전용 — Pre-carriage Pipeline 데모(계산 제외 대상)
# ---------------------------------------------------------------------------
pipeline_rows = [{
    "item_id": "MICROWAVE OVEN",
    # 2026-08-10 세션에 목업 기준 재동기화: 20,000 -> 1,200 (주간 소비량의 19배로
    # 비현실적이었던 규모를 현실화), PO는 아직 미배정(TBD)이라 ETD도 미정.
    "planned_qty": 1200,
    "planned_pol_etd": None,
    "planned_vessel": "(TBD)",
    "on_board": "Not confirmed",
    "inventory_inclusion": "Excluded",
    "source_type": "SYNTHETIC",
}]
pd.DataFrame(pipeline_rows).to_csv(f"{OUT_DIR}/pipeline_precarriage.csv", index=False)

# ---------------------------------------------------------------------------
# 4.5 Item별 Inbound 화물 목록 (itemCatalog.shipments) — Container-Item Mapping
#     + FDEST ETA 근거. qty/Init.ETA/ETA는 raw data/Tracking.xlsx 기반이되, 여러
#     세션에 걸쳐 입고/출고 규모가 현실적이도록 손으로 다듬어졌다(§8 코멘트 참고).
#     TEMPERATURE SENSOR는 신규 추가 "정상" 대비 사례라 전량 SYNTHETIC.
# ---------------------------------------------------------------------------
def _md(md):
    """'8/10' -> '2026-08-10' (연도는 BASE_DATE 기준 2026 고정), None은 그대로."""
    if md is None:
        return None
    mm, dd = md.split("/")
    return f"2026-{int(mm):02d}-{int(dd):02d}"

ITEM_SHIPMENTS = [
    # REFRIGERATOR
    ("REFRIGERATOR", "TCLU5520134", "PO-24815", "sea", "Main-carriage", 9000, "8/10", "8/17", True),
    ("REFRIGERATOR", "HAMU1769015", "DNPX26001925", "sea", "Main-carriage", 9000, "8/17", "8/17", False),
    ("REFRIGERATOR", "TGBU6371452", "DNPX26001925", "sea", "Main-carriage", 8500, "8/17", "8/17", False),
    ("REFRIGERATOR", "HAMU2277719", "DNPX26001767", "sea", "Main-carriage", 1000, "8/06", "8/19", True),
    ("REFRIGERATOR", "HAMU2954023", "DNPX26002011", "sea", "Main-carriage", 9500, "8/24", "8/24", False),
    ("REFRIGERATOR", "HLBU2379670", "DNPX26001927", "sea", "Main-carriage", 9000, "8/31", "8/31", False),
    ("REFRIGERATOR", "UETU6404866", "DNPX26002073", "sea", "Main-carriage", 8500, "9/07", "9/07", False),
    ("REFRIGERATOR", "HAMU1442362", "DNPX26001923", "sea", "Main-carriage", 9000, "9/14", "9/14", False),
    ("REFRIGERATOR", "MRSU2270118", "DNPX26002102", "sea", "Main-carriage", 8500, "9/21", "9/21", False),
    ("REFRIGERATOR", "TGHU4487723", "DNPX26002115", "sea", "Main-carriage", 9000, "9/28", "9/28", False),
    # RO COMPRESSOR(ROTARY COMPRESSOR)
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "MSKU7712901", "PO-24902", "sea", "Main-carriage", 38000, "8/17", "8/17", False),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "HLXU8606341", "DNPU26000102", "sea", "Main-carriage", 40000, "8/17", "8/17", False),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "HAMU2277719", "DNPU26000226", "sea", "Main-carriage", 8000, "8/06", "8/19", True),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "HAMU1196588", "DNPU26000167", "sea", "Main-carriage", 42000, "8/24", "8/24", False),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "UACU6014729", "DNPU26000201", "sea", "Main-carriage", 20000, "8/06", "8/19", True),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "HLXU8223445", "DNPU26000154", "sea", "Main-carriage", 44000, "8/31", "8/31", False),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "MNBU3223845", "DNPU26000209", "sea", "Main-carriage", 40000, "9/07", "9/07", False),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "HAMU1442362", "DNPU26000121", "sea", "Main-carriage", 42000, "9/14", "9/14", False),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "MRSU6261538", "DNPU26000211", "sea", "Main-carriage", 40000, "9/21", "9/21", False),
    ("RO COMPRESSOR(ROTARY COMPRESSOR)", "TIIU5329544", "DNPU26000212", "sea", "Main-carriage", 38000, "9/28", "9/28", False),
    # MOTOR
    ("MOTOR", "MNBU4623804", "DNPU26000219", "sea", "Main-carriage", 30000, "8/17", "8/17", False),
    ("MOTOR", "MMAU1453201", "DNPU26000219", "sea", "Main-carriage", 26000, "8/24", "8/24", False),
    ("MOTOR", "MRSU5514781", "DNPU26000214", "sea", "Main-carriage", 27000, "8/31", "8/31", False),
    ("MOTOR", "MNBU4345869", "DNPU26000225", "sea", "Main-carriage", 26000, "9/07", "9/07", False),
    ("MOTOR", "MRSU2703204", "DNPU26000224", "sea", "Main-carriage", 27000, "9/14", "9/14", False),
    ("MOTOR", "TLLU1194925", "DNPU26000225", "sea", "Main-carriage", 26000, "9/21", "9/21", False),
    ("MOTOR", "SUDU8244764", "DNPU26000219", "sea", "Main-carriage", 28000, "9/28", "9/28", False),
    # PARTS FOR REFRIGERATOR
    ("PARTS FOR REFRIGERATOR", "CSNU6277348", "DNPX26001820", "sea", "Main-carriage", 1300, "9/02", "8/17", False),
    ("PARTS FOR REFRIGERATOR", "GCXU5289239", "DNPX26001682", "sea", "Main-carriage", 5000, "8/24", "8/24", False),
    ("PARTS FOR REFRIGERATOR", "OOCU5724864", "DNPX26001411", "sea", "Main-carriage", 4500, "8/31", "8/31", False),
    ("PARTS FOR REFRIGERATOR", "OOCU7510938", "DNPX26001820", "sea", "Main-carriage", 5500, "9/07", "9/07", False),
    ("PARTS FOR REFRIGERATOR", "OOLU9603260", "DNPX26001679", "sea", "Main-carriage", 5000, "9/14", "9/14", False),
    ("PARTS FOR REFRIGERATOR", "TEMU7702724", "DNPX26001820", "sea", "Main-carriage", 5500, "9/21", "9/21", False),
    ("PARTS FOR REFRIGERATOR", "UETU5751053", "DNPX26001682", "sea", "Main-carriage", 5000, "9/28", "9/28", False),
    # REFRIGERATORS COMPRESSOR
    ("REFRIGERATORS COMPRESSOR", "HAMU4427485", "DNPX26001553", "sea", "Main-carriage", 1200, "8/21", "8/21", False),
    ("REFRIGERATORS COMPRESSOR", "HLBU3339646", "DNPX26000232", "sea", "Main-carriage", 1000, "8/28", "8/28", False),
    ("REFRIGERATORS COMPRESSOR", "TLLU5217320", "DNPX26001552", "sea", "Main-carriage", 1300, "9/04", "9/04", False),
    ("REFRIGERATORS COMPRESSOR", "UASU1026462", "DNPX26000232", "sea", "Main-carriage", 1100, "9/11", "9/11", False),
    ("REFRIGERATORS COMPRESSOR", "MRSU2201194", "DNPX26001619", "sea", "Main-carriage", 1300, "9/18", "9/18", False),
    ("REFRIGERATORS COMPRESSOR", "TLLU5217999", "DNPX26001600", "sea", "Main-carriage", 1200, "9/25", "9/25", False),
    # MICROWAVE OVEN (마지막 행은 pipeline_precarriage.csv와 같은 Pre-carriage 건 — 계산 제외)
    ("MICROWAVE OVEN", "HAMU1263259", "DNPY26001211", "sea", "Main-carriage", 500, "8/06", "8/19", True),
    ("MICROWAVE OVEN", "HAMU2719723", "DNPY26001214", "sea", "Main-carriage", 400, "8/06", "8/19", True),
    ("MICROWAVE OVEN", "TLLU2209983", "DNPY26001240", "sea", "Main-carriage", 450, "9/02", "9/02", False),
    ("MICROWAVE OVEN", "MRSU4471982", "DNPY26001255", "sea", "Main-carriage", 500, "9/16", "9/16", False),
    ("MICROWAVE OVEN", None, "(TBD)", "sea", "Pre-carriage", 1200, None, None, False),
    # TEMPERATURE SENSOR (신규, "정상" 대비 사례 — 전량 SYNTHETIC)
    ("TEMPERATURE SENSOR", "MSKU4471029", "DNPX26001901", "sea", "Main-carriage", 2200, "8/15", "8/15", False),
    ("TEMPERATURE SENSOR", "HLXU7734021", "DNPX26001902", "sea", "Main-carriage", 1800, "8/22", "8/22", False),
    ("TEMPERATURE SENSOR", "MRSU3390221", "DNPX26001955", "sea", "Main-carriage", 3600, "9/05", "9/03", False),
    ("TEMPERATURE SENSOR", "TCNU5561884", "DNPX26001988", "sea", "Main-carriage", 2400, "9/12", "9/12", False),
]
df_ship = pd.DataFrame(ITEM_SHIPMENTS, columns=[
    "item_id", "container_no", "po_no", "mode", "stage_label", "qty",
    "fdest_init_eta", "fdest_eta", "delayed",
])
df_ship["fdest_init_eta"] = df_ship["fdest_init_eta"].map(_md, na_action="ignore")
df_ship["fdest_eta"] = df_ship["fdest_eta"].map(_md, na_action="ignore")
df_ship["wh_in_date"] = None
df_ship["source_type"] = df_ship["item_id"].map(
    lambda x: "SYNTHETIC" if x == "TEMPERATURE SENSOR" else "REAL_MODEL_VALUE"
)
# Pre-carriage 플레이스홀더 행(컨테이너 미배정)은 항상 SYNTHETIC — pipeline_precarriage.csv와 동일 취급.
df_ship.loc[df_ship["container_no"].isna(), "source_type"] = "SYNTHETIC"
df_ship.to_csv(f"{OUT_DIR}/item_shipments.csv", index=False)

# ---------------------------------------------------------------------------
# 5. Inventory Engine 단위테스트용 Tracking 예외 케이스
#    (§8.4/§8.10 대응 — Pre-carriage 제외, 입고버퍼 우선순위, 완전동일 중복)
#    실제 Tracking.xlsx와 같은 논리 필드만 최소 구성.
# ---------------------------------------------------------------------------
tracking_edge_cases = [
    # 1) Pre-carriage: POL ATD 없음 -> Projected Inventory 계산 제외(AC-16)
    {
        "case_id": "SYN-PRECARRIAGE-1",
        "Model": "SYN-TEST-ITEM", "QTY": 5000,
        "Container No": None, "House B/L No": "SYNBL0001",
        "Invoice No": "SYNINV0001",
        "POL ATD": None,
        "F.DEST Init. ETA": None, "F.DEST ETA": "2026-09-10",
        "F.DEST ATA": None, "W/H In Date": None,
        "expected_behavior": "On-board 미확정 -> Inbound 후보 제외, Pipeline에만 표시",
    },
    # 2) 완료건 + W/H In Date 있음 -> 1순위(W/H In Date)로 인식(AC-19)
    {
        "case_id": "SYN-BUFFER-WHDATE",
        "Model": "SYN-TEST-ITEM", "QTY": 3000,
        "Container No": "SYNU1234567", "House B/L No": "SYNBL0002",
        "Invoice No": "SYNINV0002",
        "POL ATD": "2026-07-20",
        "F.DEST Init. ETA": "2026-08-01", "F.DEST ETA": "2026-08-03",
        "F.DEST ATA": "2026-08-03", "W/H In Date": "2026-08-06",
        "expected_behavior": "Inbound 인식일 = W/H In Date(2026-08-06), ATA(08-03)와 3일 차이 = 버퍼 실측치",
    },
    # 3) 완료건 + W/H In Date 없음 -> 2순위(ATA + 버퍼 기본값)로 인식
    {
        "case_id": "SYN-BUFFER-ATA-ONLY",
        "Model": "SYN-TEST-ITEM", "QTY": 4000,
        "Container No": "SYNU7654321", "House B/L No": "SYNBL0003",
        "Invoice No": "SYNINV0003",
        "POL ATD": "2026-07-22",
        "F.DEST Init. ETA": "2026-08-02", "F.DEST ETA": "2026-08-04",
        "F.DEST ATA": "2026-08-04", "W/H In Date": None,
        "expected_behavior": "Inbound 인식일 = F.DEST ATA(2026-08-04) + 버퍼 기본값(§10.1 가정, 개발 중 확정)",
    },
    # 4) 완전 동일 키 중복 2건 -> 중복 후보 Flag(§10.2, 우선순위 낮음이지만 테스트 픽스처는 유지)
    {
        "case_id": "SYN-DUP-1",
        "Model": "SYN-TEST-ITEM", "QTY": 1000,
        "Container No": "SYNU1111111", "House B/L No": "SYNBL0004",
        "Invoice No": "SYNINV0004",
        "POL ATD": "2026-07-25",
        "F.DEST Init. ETA": "2026-08-15", "F.DEST ETA": "2026-08-15",
        "F.DEST ATA": None, "W/H In Date": None,
        "expected_behavior": "SYN-DUP-2와 핵심 식별값 완전 동일 -> 중복 후보 Flag",
    },
    {
        "case_id": "SYN-DUP-2",
        "Model": "SYN-TEST-ITEM", "QTY": 1000,
        "Container No": "SYNU1111111", "House B/L No": "SYNBL0004",
        "Invoice No": "SYNINV0004",
        "POL ATD": "2026-07-25",
        "F.DEST Init. ETA": "2026-08-15", "F.DEST ETA": "2026-08-15",
        "F.DEST ATA": None, "W/H In Date": None,
        "expected_behavior": "SYN-DUP-1과 핵심 식별값 완전 동일 -> 중복 후보 Flag",
    },
    # 5) QTY 결측 -> 계산 제외 + Data Quality Error(AC-18). 실제로도 존재하는 케이스지만 명시적 픽스처로 추가.
    {
        "case_id": "SYN-MISSING-QTY",
        "Model": "SYN-TEST-ITEM", "QTY": None,
        "Container No": "SYNU2222222", "House B/L No": "SYNBL0005",
        "Invoice No": "SYNINV0005",
        "POL ATD": "2026-07-25",
        "F.DEST Init. ETA": "2026-08-18", "F.DEST ETA": "2026-08-18",
        "F.DEST ATA": None, "W/H In Date": None,
        "expected_behavior": "QTY 결측 -> Inventory 계산 제외 + Data Quality Error",
    },
]
df_edge = pd.DataFrame(tracking_edge_cases)
df_edge["source_type"] = "SYNTHETIC"
df_edge.to_csv(f"{OUT_DIR}/tracking_synthetic_edge_cases.csv", index=False)

print("생성 완료:")
for f in ["wd_item_master.csv", "wd_onhand.csv", "wd_safety_stock.csv", "wd_outbound.csv",
          "pipeline_precarriage.csv", "item_shipments.csv", "tracking_synthetic_edge_cases.csv"]:
    print(" -", f)
