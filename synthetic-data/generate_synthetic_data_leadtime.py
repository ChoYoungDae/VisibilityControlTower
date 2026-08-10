"""
발주 시점·수량 추천(reorder recommendation) 컨셉 데모용 리드타임 이력 합성데이터.

배경: 재고 투영(§9.4)이 Shortage/Risk 발생일과 부족 수량을 이미 계산해준다.
여기에 "노선×캐리어별 과거 리드타임 분포(P50/P95)"를 결합하면 "언제까지 얼마나
발주해야 하는지"를 추천할 수 있다(대화 세션 합의 사항 — 우리가 책임지는 Inbound
리드타임 영역과 고객이 이미 준 Outbound/Safety Stock을 결합한 파생 계산이며,
수요예측이나 발주 실행 자체는 하지 않는다).

문제는 지금 synthetic-data(`cargo_tracking.csv`, `item_shipments.csv`)가 전부
"현재 진행 중인 화물의 스냅샷"이라 리드타임 분포를 낼 과거 완료 이력이 없다는
것 — 이 스크립트가 그 이력을 채운다.

**컨셉 데모라는 한계를 명시한다**:
1. 노선(Lane)은 실제 raw data 조인이 아니라 목업에 이미 나온 실제 노선·캐리어
   6개를 그대로 재사용해 합성 이력(과거 완료 화물)을 만든 것이다.
2. Item→Lane 매핑(`item_primary_lane.csv`)은 실제 조달 관계 데이터가 없어
   "이 Item은 이 노선으로 들어온다"고 데모용으로 가정한 것이다(실제로는
   Container-Item Mapping의 POL/POD를 그대로 써야 함 — §9.1).
3. 여기서 "리드타임"은 POL ATD → FDEST ATA(Transportation 구간)만 의미한다.
   실제 발주부터 도착까지는 여기에 공급처 생산·부킹 리드타임이 추가로 붙지만
   이번 데모 범위는 아니다.

실행: python generate_synthetic_data_leadtime.py
출력: shipment_history.csv, item_primary_lane.csv, lead_time_stats.csv
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta

OUT_DIR = "."
RNG = np.random.default_rng(20260810)  # 재현 가능하도록 시드 고정
BASE_DATE = date(2026, 8, 7)
HISTORY_START = date(2026, 2, 1)  # 과거 약 6개월치 완료 화물 이력

# ---------------------------------------------------------------------------
# 1. 노선(Lane) 정의 — 목업(cargo_tracking.csv/booking.csv)에 이미 나온 실제
#    노선·캐리어를 그대로 재사용한다(새 노선을 지어내지 않음).
# ---------------------------------------------------------------------------
LANES = {
    "L1-BUSAN-LONGBEACH-ONE":     dict(pol="Busan", pod="Long Beach", carrier="ONE",     mode="sea", mean_days=25, std_days=3.0, n=22),
    "L2-SHANGHAI-HAMBURG-ONE":    dict(pol="Shanghai", pod="Hamburg", carrier="ONE",     mode="sea", mean_days=33, std_days=4.0, n=22),
    "L3-NINGBO-ANTWERP-MSC":      dict(pol="Ningbo", pod="Antwerp", carrier="MSC",       mode="sea", mean_days=34, std_days=4.0, n=20),
    "L4-QINGDAO-ROTTERDAM-CMACGM": dict(pol="Qingdao", pod="Rotterdam", carrier="CMA CGM", mode="sea", mean_days=32, std_days=3.5, n=20),
    "L5-NINGBO-BUSAN-HYUNDAI":    dict(pol="Ningbo", pod="Busan", carrier="HYUNDAI",     mode="sea", mean_days=4,  std_days=1.0, n=24),
    "L6-INCHEON-FRANKFURT-LH":    dict(pol="Incheon", pod="Frankfurt", carrier="LH",     mode="air", mean_days=3,  std_days=0.8, n=24),
}

# ---------------------------------------------------------------------------
# 2. 과거 완료 화물 이력 생성 — 정규분포 + 약 12% 이상치(혼잡·롤오버 등으로
#    크게 지연된 케이스)를 섞어서, P50과 P95가 유의미하게 벌어지도록 구성.
# ---------------------------------------------------------------------------
rows = []
hid = 1
for lane_id, cfg in LANES.items():
    span_days = (BASE_DATE - HISTORY_START).days
    for i in range(cfg["n"]):
        pol_atd = HISTORY_START + timedelta(days=int(RNG.integers(0, span_days)))
        is_outlier = RNG.random() < 0.12
        if is_outlier:
            lead = cfg["mean_days"] + abs(RNG.normal(cfg["mean_days"] * 0.6, cfg["mean_days"] * 0.25))
        else:
            lead = RNG.normal(cfg["mean_days"], cfg["std_days"])
        lead = max(1, round(lead))
        fdest_ata = pol_atd + timedelta(days=int(lead))
        if fdest_ata >= BASE_DATE:
            continue  # 아직 "완료"가 아니면 이력에서 제외
        rows.append(dict(
            history_id=f"SH-{hid:04d}", lane_id=lane_id,
            pol=cfg["pol"], pod=cfg["pod"], carrier=cfg["carrier"], mode=cfg["mode"],
            pol_atd=pol_atd.isoformat(), fdest_ata=fdest_ata.isoformat(),
            lead_time_days=int(lead), is_outlier=is_outlier,
        ))
        hid += 1

df_hist = pd.DataFrame(rows)
df_hist["source_type"] = "SYNTHETIC"
df_hist.to_csv(f"{OUT_DIR}/shipment_history.csv", index=False)

# ---------------------------------------------------------------------------
# 3. 노선별 리드타임 통계 (P50/P95) — reorder 추천 계산의 입력값
# ---------------------------------------------------------------------------
stats_rows = []
for lane_id, g in df_hist.groupby("lane_id"):
    vals = g["lead_time_days"].to_numpy()
    stats_rows.append(dict(
        lane_id=lane_id, pol=g["pol"].iloc[0], pod=g["pod"].iloc[0],
        carrier=g["carrier"].iloc[0], mode=g["mode"].iloc[0],
        n=len(vals), mean_days=round(float(np.mean(vals)), 1),
        std_days=round(float(np.std(vals)), 1),
        p50_days=int(np.percentile(vals, 50)), p95_days=int(np.percentile(vals, 95)),
    ))
df_stats = pd.DataFrame(stats_rows)
df_stats["source_type"] = "SYNTHETIC"
df_stats.to_csv(f"{OUT_DIR}/lead_time_stats.csv", index=False)

# ---------------------------------------------------------------------------
# 4. Item -> 대표 Lane 매핑 (데모 가정 — 실제 Container-Item Mapping 아님)
# ---------------------------------------------------------------------------
ITEM_PRIMARY_LANE = {
    "REFRIGERATOR": ("L1-BUSAN-LONGBEACH-ONE", "실제 shipment(TCLU5520134)가 이 노선과 일치"),
    "RO COMPRESSOR(ROTARY COMPRESSOR)": ("L2-SHANGHAI-HAMBURG-ONE", "실제 shipment(MSKU7712901)가 이 노선과 일치"),
    "MOTOR": ("L2-SHANGHAI-HAMBURG-ONE", "데모 가정 — 실제 노선 데이터 없음"),
    "PARTS FOR REFRIGERATOR": ("L1-BUSAN-LONGBEACH-ONE", "데모 가정 — REFRIGERATOR와 동일 계열로 추정"),
    "REFRIGERATORS COMPRESSOR": ("L3-NINGBO-ANTWERP-MSC", "데모 가정 — 실제 노선 데이터 없음"),
    "MICROWAVE OVEN": ("L4-QINGDAO-ROTTERDAM-CMACGM", "데모 가정 — 실제 Pre-carriage 예시(CMAU0488226)와 같은 방향"),
    "TEMPERATURE SENSOR": ("L6-INCHEON-FRANKFURT-LH", "데모 가정 — 소형 부품이라 항공 노선으로 가정"),
}
df_lane = pd.DataFrame([
    dict(item_id=k, lane_id=v[0], assumption_note=v[1], source_type="SYNTHETIC_ASSUMPTION")
    for k, v in ITEM_PRIMARY_LANE.items()
])
df_lane.to_csv(f"{OUT_DIR}/item_primary_lane.csv", index=False)

print("생성 완료 (리드타임 이력):")
for f in ["shipment_history.csv", "lead_time_stats.csv", "item_primary_lane.csv"]:
    print(" -", f)
print(f"\n총 이력 건수: {len(df_hist)}건 / {len(LANES)}개 노선")
print(df_stats[["lane_id", "n", "mean_days", "p50_days", "p95_days"]].to_string(index=False))
