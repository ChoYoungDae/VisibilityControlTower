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
    "REFRIGERATOR":                     {"scenario": "Shortage -> Recovery"},
    "RO COMPRESSOR(ROTARY COMPRESSOR)": {"scenario": "Risk only (no Shortage)"},
    "MOTOR":                            {"scenario": "Normal 전체 기간"},
    "PARTS FOR REFRIGERATOR":           {"scenario": "Shortage(기준일부터) -> Recovery"},
    "REFRIGERATORS COMPRESSOR":         {"scenario": "Risk, 간발의 Recovery"},
    "MICROWAVE OVEN":                   {"scenario": "Normal, Pre-carriage Pipeline 데모"},
}

item_master = pd.DataFrame([
    {"item_id": k, "item_name": k, "source": "REAL_MODEL_VALUE"} for k in ITEMS
])
item_master.to_csv(f"{OUT_DIR}/wd_item_master.csv", index=False)

# ---------------------------------------------------------------------------
# 2. On-hand (기준일 스냅샷 1건씩) + Safety Stock
# ---------------------------------------------------------------------------
ONHAND = {
    "REFRIGERATOR": 60000,
    "RO COMPRESSOR(ROTARY COMPRESSOR)": 20000,
    "MOTOR": 80000,
    "PARTS FOR REFRIGERATOR": 5000,
    "REFRIGERATORS COMPRESSOR": 3000,
    "MICROWAVE OVEN": 15000,
}
SAFETY_STOCK = {
    "REFRIGERATOR": 30000,
    "RO COMPRESSOR(ROTARY COMPRESSOR)": 15000,
    "MOTOR": 20000,
    "PARTS FOR REFRIGERATOR": 10000,
    "REFRIGERATORS COMPRESSOR": 5000,
    "MICROWAVE OVEN": 8000,
}
DAILY_OUTBOUND = {
    "REFRIGERATOR": 8000,
    "RO COMPRESSOR(ROTARY COMPRESSOR)": 1500,
    "MOTOR": 1000,
    "PARTS FOR REFRIGERATOR": 1200,
    "REFRIGERATORS COMPRESSOR": 200,
    "MICROWAVE OVEN": 300,
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
    "planned_qty": 20000,
    "planned_pol_etd": "2026-08-25",
    "planned_vessel": "(TBD)",
    "on_board": "Not confirmed",
    "inventory_inclusion": "Excluded",
    "source_type": "SYNTHETIC",
}]
pd.DataFrame(pipeline_rows).to_csv(f"{OUT_DIR}/pipeline_precarriage.csv", index=False)

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
          "pipeline_precarriage.csv", "tracking_synthetic_edge_cases.csv"]:
    print(" -", f)
