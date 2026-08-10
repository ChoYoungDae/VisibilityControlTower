"""
Transportation 도메인(화물/업무/비용 탭) 합성 데이터 생성.
VisibilityControlTower_PRD.md §8 대응. `generate_synthetic_data.py`가 Inventory
도메인(재고 탭)만 다루는 것과 짝을 이룬다.

이 스크립트는 새로운 시나리오를 창작하지 않는다 — `visibility_control_tower_mockup.html`에
이미 하드코딩되어 있는 화물/업무/비용 탭의 표시값을 그대로 CSV로 옮겨적은 것이다
(rowData/VESSEL_MMSI/sectionStats/bookingData/arrivalData/dndData/월별 비용 SVG 차트/
Port-to-Port 스케줄 조회 예시). 목적은 화면에 이미 나온 숫자와 향후 DB 시딩값이
어긋나지 않게 만드는 것 — 화면을 바꾸면 이 스크립트도 같이 갱신해야 한다.

실행: python generate_synthetic_data_transportation.py
출력: synthetic-data/*.csv (source_type=SYNTHETIC 명시)
"""
import pandas as pd

OUT_DIR = "."
YEAR = 2026  # 목업 날짜(예: "8/13")는 전부 이 해 기준

def d(md):
    """'8/13' -> '2026-08-13', '8/03, 14:20' -> '2026-08-03 14:20', None -> None"""
    if md is None:
        return None
    parts = md.split(",")
    date_part = parts[0].strip()
    mm, dd = date_part.split("/")
    out = f"{YEAR}-{int(mm):02d}-{int(dd):02d}"
    if len(parts) > 1:
        out += " " + parts[1].strip()
    return out

# ---------------------------------------------------------------------------
# 1. 화물 탭 — 컨테이너/HBL 단위 트래킹 리스트 (rowData + 리스트 HTML 값)
# ---------------------------------------------------------------------------
CARGO_ROWS = [
    # id, mode, stage, container_or_hbl, bl_no, po_no, service_note, pol, pod,
    # planned_vf, current_vf, pod_vf, initial_pol_etd, pol_etd, ts_count,
    # carrier_eta, pta_p50, pta_p95, fdest_eta, dnd_lfd, status_label, delayed
    dict(id="s-l1", mode="sea", stage="pre", cid="CMAU0488226", bl="CMDU0488226A", po="PO-25011",
         service_note=None, pol="Qingdao", pod="Rotterdam",
         planned_vf="CMA CGM AQUILA", current_vf=None, pod_vf=None,
         initial_pol_etd=d("8/13"), pol_etd=d("8/13"), ts_count=None,
         carrier_eta=None, pta_p50=None, pta_p95=None, fdest_eta=None, dnd_lfd=None,
         status_label="Pre-carriage", delayed=False),
    dict(id="s-l2", mode="sea", stage="pre", cid="TEMU9012334", bl="MEDUN9012334", po="PO-25050",
         service_note=None, pol="Ningbo", pod="Antwerp",
         planned_vf="MSC ISABELLA", current_vf=None, pod_vf=None,
         initial_pol_etd=d("8/13"), pol_etd=d("8/16"), ts_count=None,
         carrier_eta=None, pta_p50=None, pta_p95=None, fdest_eta=None, dnd_lfd=None,
         status_label="지연", delayed=True),
    dict(id="s-t1", mode="sea", stage="main", cid="TCLU5520134", bl="ONEYSEL0552013", po="PO-24815",
         service_note="ONE 서비스", pol="Busan", pod="Long Beach",
         planned_vf=None, current_vf="ONE INNOVATION", pod_vf="MSC BRUNELLA",
         initial_pol_etd=None, pol_etd=None, ts_count=1,
         carrier_eta=d("8/02"), pta_p50=d("8/01"), pta_p95=d("8/03"), fdest_eta=None, dnd_lfd=None,
         status_label="지연", delayed=True),
    dict(id="s-t2", mode="sea", stage="main", cid="MSKU7712901", bl="ONEYSHA0771290", po="PO-24902",
         service_note="ONE 서비스", pol="Shanghai", pod="Hamburg",
         planned_vf=None, current_vf="ONE COMMITMENT", pod_vf="ONE COMMITMENT",
         initial_pol_etd=None, pol_etd=None, ts_count=0,
         carrier_eta=d("8/13"), pta_p50=d("8/13"), pta_p95=d("8/16"), fdest_eta=None, dnd_lfd=None,
         status_label="정상", delayed=False),
    dict(id="s-t3", mode="sea", stage="main", cid="HBL-SE-330871", bl=None, po="PO-24770",
         service_note="LCL", pol="Ningbo", pod="Busan",
         planned_vf=None, current_vf="HYUNDAI FAITH", pod_vf="HYUNDAI FAITH",
         initial_pol_etd=None, pol_etd=None, ts_count=0,
         carrier_eta=d("7/28"), pta_p50=d("7/28"), pta_p95=d("7/29"), fdest_eta=None, dnd_lfd=None,
         status_label="정상", delayed=False),
    dict(id="s-a1", mode="sea", stage="on", cid="HLXU3308719", bl="HDMUBUS0330871", po="PO-24650",
         service_note=None, pol="Long Beach", pod="Phoenix DC",
         planned_vf=None, current_vf=None, pod_vf=None,
         initial_pol_etd=None, pol_etd=None, ts_count=None,
         carrier_eta=None, pta_p50=None, pta_p95=None, fdest_eta=d("7/26"), dnd_lfd=d("7/31"),
         status_label="LFD 임박", delayed=False),
    dict(id="s-a2", mode="sea", stage="on", cid="FSCU1180042", bl="OOLUHAM0118004", po="PO-24511",
         service_note=None, pol="Hamburg", pod="Munich DC",
         planned_vf=None, current_vf=None, pod_vf=None,
         initial_pol_etd=None, pol_etd=None, ts_count=None,
         carrier_eta=None, pta_p50=None, pta_p95=None, fdest_eta=d("7/24"), dnd_lfd=d("8/02"),
         status_label="정상", delayed=False),
    dict(id="a-l1", mode="air", stage="pre", cid="SEL-AIR-88301", bl=None, po="PO-25102",
         service_note=None, pol="Incheon", pod="Chicago",
         planned_vf="KE 037", current_vf=None, pod_vf=None,
         initial_pol_etd=d("8/03, 14:20"), pol_etd=d("8/03, 14:20"), ts_count=None,
         carrier_eta=None, pta_p50=None, pta_p95=None, fdest_eta=None, dnd_lfd=None,
         status_label="Pre-carriage", delayed=False),
    dict(id="a-t1", mode="air", stage="main", cid="SEL-AIR-88231", bl=None, po="PO-24960",
         service_note=None, pol="Incheon", pod="Frankfurt",
         planned_vf=None, current_vf="LH 8286", pod_vf="LH 0712",
         initial_pol_etd=None, pol_etd=None, ts_count=1,
         carrier_eta=d("8/05, 10:00"), pta_p50=d("8/04, 21:40"), pta_p95=d("8/06, 09:00"),
         fdest_eta=None, dnd_lfd=None, status_label="지연", delayed=True),
    dict(id="a-t2", mode="air", stage="main", cid="SEL-AIR-88410", bl=None, po="PO-25033",
         service_note=None, pol="Incheon", pod="Tokyo",
         planned_vf=None, current_vf="OZ 108", pod_vf="OZ 108",
         initial_pol_etd=None, pol_etd=None, ts_count=0,
         carrier_eta=d("7/29, 11:05"), pta_p50=d("7/29, 11:05"), pta_p95=d("7/29, 18:00"),
         fdest_eta=None, dnd_lfd=None, status_label="정상", delayed=False),
    dict(id="a-a1", mode="air", stage="on", cid="SEL-AIR-87990", bl=None, po="PO-24700",
         service_note=None, pol="Narita", pod="Tokyo DC",
         planned_vf=None, current_vf=None, pod_vf=None,
         initial_pol_etd=None, pol_etd=None, ts_count=None,
         carrier_eta=None, pta_p50=None, pta_p95=None, fdest_eta=d("7/25, 09:10"), dnd_lfd="해당없음",
         status_label="정상", delayed=False),
]
# API가 상세 패널(구 rowData)을 그대로 재현할 수 있도록, 파생 로직으로
# 흔들리기 쉬운 두 표시값(뱃지 색상, 노선 문구)은 목업 원본 문구를 그대로
# 컬럼으로 박아둔다 — status_label/service_note 조합만으로 역산하면 s-t3의
# "LCL", a-t1의 "항공" 같은 불규칙한 접미사를 못 맞춘다.
CARGO_BADGE_COLOR = {
    "s-l1": "neutral", "s-l2": "crit", "s-t1": "crit", "s-t2": "ok", "s-t3": "ok",
    "s-a1": "warn", "s-a2": "ok", "a-l1": "neutral", "a-t1": "warn", "a-t2": "ok", "a-a1": "ok",
}
CARGO_ROUTE_DISPLAY = {
    "s-l1": "Qingdao → Rotterdam · Pre-carriage",
    "s-l2": "Ningbo → Antwerp · Pre-carriage 지연",
    "s-t1": "Busan → Long Beach · ONE 서비스",
    "s-t2": "Shanghai → Hamburg · ONE 서비스",
    "s-t3": "Ningbo → Busan · LCL",
    "s-a1": "Long Beach → Phoenix DC · On-carriage",
    "s-a2": "Hamburg → Munich DC · On-carriage",
    "a-l1": "Incheon → Chicago · Pre-carriage",
    "a-t1": "Incheon → Frankfurt · 항공",
    "a-t2": "Incheon → Tokyo · 항공",
    "a-a1": "Narita → Tokyo DC · On-carriage",
}
for row in CARGO_ROWS:
    row["badge_color"] = CARGO_BADGE_COLOR[row["id"]]
    row["route_display"] = CARGO_ROUTE_DISPLAY[row["id"]]
    row["source_type"] = "SYNTHETIC"
pd.DataFrame(CARGO_ROWS).to_csv(f"{OUT_DIR}/cargo_tracking.csv", index=False)

# 화물 탭 상단 요약 통계 — 실제 배후 모집단(128건)은 별도 원본이 없고 이 요약
# 숫자만 화면에 하드코딩되어 있음. 위 CARGO_ROWS 11건은 그중 상세 정보가 있는
# 표본일 뿐, 이 통계와 1:1로 집계되지 않는다(모집단 크기 불일치는 목업 자체의 한계).
CARGO_SECTION_STATS = [
    dict(scope="sea", stage="pre",  total=22, delayed=3),
    dict(scope="sea", stage="main", total=46, delayed=7),
    dict(scope="sea", stage="on",   total=28, delayed=3),
    dict(scope="air", stage="pre",  total=6,  delayed=1),
    dict(scope="air", stage="main", total=15, delayed=2),
    dict(scope="air", stage="on",   total=11, delayed=1),
]
for row in CARGO_SECTION_STATS:
    row["source_type"] = "SYNTHETIC"
pd.DataFrame(CARGO_SECTION_STATS).to_csv(f"{OUT_DIR}/cargo_section_stats.csv", index=False)

VESSEL_MMSI = [
    dict(vessel_name="ONE INNOVATION", mmsi="311001939"),
    dict(vessel_name="MSC BRUNELLA", mmsi="255806491"),
    dict(vessel_name="ONE COMMITMENT", mmsi="431332000"),
    dict(vessel_name="HYUNDAI FAITH", mmsi="538007480"),
    dict(vessel_name="CMA CGM AQUILA", mmsi="215217000"),
    dict(vessel_name="MSC ISABELLA", mmsi="353590000"),
]
for row in VESSEL_MMSI:
    row["source_type"] = "REAL_VESSEL_VALUE"  # 실제 선박의 실제 MMSI (VesselFinder/MarineTraffic 확인)
pd.DataFrame(VESSEL_MMSI).to_csv(f"{OUT_DIR}/vessel_mmsi.csv", index=False)

# ---------------------------------------------------------------------------
# 2. 업무 탭 — 부킹 리스트 (bookingData)
# ---------------------------------------------------------------------------
BOOKINGS = [
    dict(booking_no="BK-6011", cid="CMAU0488226", route="Busan → Rotterdam", stage="Pre-carriage",
         status="진행중", si_cutoff="D-2 (2026-08-05 18:00)", si_note="선적서류 제출 마감", si_class="warn",
         vgm_cutoff="2/3 컨테이너 제출", vgm_note="SOLAS 필수 — D-3 (2026-08-06)", vgm_class="",
         cy_cutoff="D-4 (2026-08-07 12:00)", cy_note="물리적 반입 마감", cy_class="",
         export_customs="진행중 (심사 대기)", bl_status="미발급 — SI 승인 후 발급 예정", bl_no=None,
         rollover=False),
    dict(booking_no="BK-6012", cid="TEMU9012334", route="Ningbo → Antwerp", stage="롤오버",
         status="롤오버", si_cutoff="재산정 중", si_note="블랭크 세일링으로 다음 항차 배정 대기", si_class="crit",
         vgm_cutoff="재산정 중", vgm_note="새 sailing 확정 시 갱신", vgm_class="crit",
         cy_cutoff="재산정 중", cy_note="새 sailing 확정 시 갱신", cy_class="crit",
         export_customs="대기 (재부킹 이후 진행)", bl_status="미발급", bl_no=None,
         rollover=True),
    dict(booking_no="BK-5567", cid="TCLU5520134", route="Busan → Long Beach", stage="Main-carriage",
         status="확정 · 서류 완료", si_cutoff="완료", si_note="2026-07-22 제출 완료", si_class="done",
         vgm_cutoff="3/3 컨테이너 제출", vgm_note="완료", vgm_class="done",
         cy_cutoff="완료", cy_note="2026-07-23 게이트인 완료", cy_class="done",
         export_customs="완료", bl_status="발급완료", bl_no="ONEYSEL0552013",
         rollover=False),
    dict(booking_no="BK-5568", cid="MSKU7712901", route="Shanghai → Hamburg", stage="Main-carriage",
         status="확정 · 서류 완료", si_cutoff="완료", si_note="2026-08-01 제출 완료", si_class="done",
         vgm_cutoff="1/1 컨테이너 제출", vgm_note="완료", vgm_class="done",
         cy_cutoff="완료", cy_note="2026-08-02 게이트인 완료", cy_class="done",
         export_customs="완료", bl_status="발급완료", bl_no="ONEYSHA0771290",
         rollover=False),
]
for row in BOOKINGS:
    row["source_type"] = "SYNTHETIC"
pd.DataFrame(BOOKINGS).to_csv(f"{OUT_DIR}/booking.csv", index=False)

BOOKING_PO = [
    ("BK-6011", "PO-25011"), ("BK-6011", "PO-25090"),
    ("BK-6012", "PO-25050"),
    ("BK-5567", "PO-24815"),
    ("BK-5568", "PO-24902"),
]
df_bp = pd.DataFrame(BOOKING_PO, columns=["booking_no", "po_no"])
df_bp["source_type"] = "SYNTHETIC"
df_bp.to_csv(f"{OUT_DIR}/booking_po.csv", index=False)

# ---------------------------------------------------------------------------
# 3. 업무 탭 — 도착 준비 (arrivalData)
# ---------------------------------------------------------------------------
ARRIVALS = [
    dict(cid="MSKU7712901", po="PO-24902", route="Shanghai → Hamburg",
         status="통관 대기 — Inland Routing 잠김", import_customs="심사 대기 중 (전자신고 완료)",
         customs_expected_or_done=None, customs_expected=d("8/11"), locked=True,
         locked_msg="수입통관이 완료되어야 Inland Routing 옵션을 비교·선택할 수 있습니다."),
    dict(cid="TCLU5520134", po="PO-24815", route="Busan → Long Beach",
         status="비교 가능", import_customs="완료",
         customs_expected_or_done=d("7/30"), customs_expected=None, locked=False, locked_msg=None),
    dict(cid="HLXU3308719", po="PO-24650", route="Long Beach → Phoenix DC",
         status="실행완료", import_customs="완료",
         customs_expected_or_done=d("7/26"), customs_expected=None, locked=False, locked_msg=None),
    dict(cid="SEL-AIR-88231", po="PO-24960", route="Incheon → Frankfurt",
         status="비교 가능 (통관 해당없음)", import_customs="해당없음 (해당 화물 유형은 통관 절차 불필요)",
         customs_expected_or_done=None, customs_expected=None, locked=False, locked_msg=None),
]
for row in ARRIVALS:
    row["source_type"] = "SYNTHETIC"
pd.DataFrame(ARRIVALS).to_csv(f"{OUT_DIR}/arrival_prep.csv", index=False)

INLAND_OPTIONS = [
    dict(cid="TCLU5520134", mode="트럭 (드레이지)", lead_time="5~7일", cost="₩620,000", free_time="3일",
         recommendation="권장 예약: D-7", selected=False),
    dict(cid="TCLU5520134", mode="철도 (Inland Rail)", lead_time="9~12일", cost="₩410,000", free_time="5일",
         recommendation="권장 예약: D-10", selected=False),
    dict(cid="HLXU3308719", mode="트럭 (드레이지)", lead_time="5~7일", cost="₩310,000", free_time="4일",
         recommendation="실행됨 · 배차 완료", selected=True),
    dict(cid="HLXU3308719", mode="철도 (Inland Rail)", lead_time="9~12일", cost="₩205,000", free_time="5일",
         recommendation="미선택", selected=False),
    dict(cid="SEL-AIR-88231", mode="트럭 (드레이지)", lead_time="2~3일", cost="€180", free_time="2일",
         recommendation="권장 예약: D-3", selected=False),
    dict(cid="SEL-AIR-88231", mode="철도 (Inland Rail)", lead_time="해당없음", cost=None, free_time=None,
         recommendation="단거리 구간이라 미제공", selected=False),
]
for row in INLAND_OPTIONS:
    row["source_type"] = "SYNTHETIC"
pd.DataFrame(INLAND_OPTIONS).to_csv(f"{OUT_DIR}/inland_routing_option.csv", index=False)

# ---------------------------------------------------------------------------
# 4. 업무 탭 — Port-to-Port 스케줄 조회 결과 예시 (schedule search view)
# ---------------------------------------------------------------------------
SCHEDULE_SEARCH = [
    dict(carrier="ONE", vessel="ONE INNOVATION", pol_etd=d("8/12"), pod_eta=d("8/29"),
         lead_time_days=17, ts_count=1, carbon_tco2e_per_teu=1.8),
    dict(carrier="MSC", vessel="MSC BRUNELLA", pol_etd=d("8/14"), pod_eta=d("8/30"),
         lead_time_days=16, ts_count=0, carbon_tco2e_per_teu=1.6),
    dict(carrier="CMA CGM", vessel="CMA CGM AQUILA", pol_etd=d("8/09"), pod_eta=d("8/31"),
         lead_time_days=22, ts_count=2, carbon_tco2e_per_teu=2.4),
]
for row in SCHEDULE_SEARCH:
    row["source_type"] = "SYNTHETIC"
pd.DataFrame(SCHEDULE_SEARCH).to_csv(f"{OUT_DIR}/schedule_search_result.csv", index=False)

# ---------------------------------------------------------------------------
# 5. 비용 탭 — 체화료(D&D) 통합 리스트 (dndData)
# ---------------------------------------------------------------------------
DND = [
    dict(id="lft-hlxu", cid="HLXU3308719", po="PO-24650", route="Long Beach → Phoenix DC",
         status="임박(발생 전)", free_time_expiry=d("7/31"), days_remaining=2, days_elapsed=None,
         daily_rate=180000, pending=True),
    dict(id="lft-sel", cid="SEL-AIR-87990", po="PO-24700", route="Narita → Tokyo DC",
         status="임박(발생 전)", free_time_expiry=d("7/30"), days_remaining=1, days_elapsed=None,
         daily_rate=90000, pending=True),
    dict(id="lft-fscu", cid="FSCU1180042", po="PO-24511", route="Hamburg → Munich DC",
         status="임박(발생 전)", free_time_expiry=d("8/04"), days_remaining=6, days_elapsed=None,
         daily_rate=165000, pending=True),
    dict(id="dnd-4week", cid="CMAU5588234", po="PO-24390", route="Yantian → Savannah",
         status="4주 이상", free_time_expiry=d("6/29"), days_remaining=None, days_elapsed=33,
         daily_rate=213600, pending=False),
    dict(id="dnd-3week", cid="EISU7765310", po="PO-24870", route="Shanghai → New York",
         status="3주 이내", free_time_expiry=d("7/13"), days_remaining=None, days_elapsed=19,
         daily_rate=230500, pending=False),
    dict(id="dnd-2week", cid="OOLU2201884", po="PO-24988", route="Qingdao → Los Angeles",
         status="2주 이내", free_time_expiry=d("7/21"), days_remaining=None, days_elapsed=11,
         daily_rate=195500, pending=False),
    dict(id="dnd-1week", cid="MSKU4471002", po="PO-25077", route="Ningbo → Rotterdam",
         status="1주 이내", free_time_expiry=d("7/28"), days_remaining=None, days_elapsed=4,
         daily_rate=155000, pending=False),
]
DND_BADGE_COLOR = {
    "lft-hlxu": "warn", "lft-sel": "crit", "lft-fscu": "neutral",
    "dnd-4week": "crit", "dnd-3week": "warn", "dnd-2week": "warn", "dnd-1week": "neutral",
}
for row in DND:
    row["badge_color"] = DND_BADGE_COLOR[row["id"]]
    row["source_type"] = "SYNTHETIC"
pd.DataFrame(DND).to_csv(f"{OUT_DIR}/dnd.csv", index=False)

DND_WEEKLY_BUCKETS = [
    ("dnd-4week", 1, 7), ("dnd-4week", 2, 7), ("dnd-4week", 3, 7), ("dnd-4week", 4, 12),
    ("dnd-3week", 1, 7), ("dnd-3week", 2, 7), ("dnd-3week", 3, 5),
    ("dnd-2week", 1, 7), ("dnd-2week", 2, 4),
    ("dnd-1week", 1, 4),
]
df_wb = pd.DataFrame(DND_WEEKLY_BUCKETS, columns=["dnd_id", "week_index", "days"])
df_wb["source_type"] = "SYNTHETIC"
df_wb.to_csv(f"{OUT_DIR}/dnd_weekly_bucket.csv", index=False)

# ---------------------------------------------------------------------------
# 6. 비용 탭 — 월별 물류비 현황 (SVG 차트 + breakdown 테이블)
# ---------------------------------------------------------------------------
# 차트는 픽셀 좌표(y/height)로 그려져 있어 축 스케일(0~150M ₩, 0~200 TEU, 두
# 축 모두 y:20~200px)로 역산했다. 7월은 breakdown 테이블에 정확한 금액이 별도로
# 명시돼 있어 그 값을 그대로 쓰고, 나머지 달은 차트 픽셀에서 역산한 근사치다
# (근사치라는 점을 note 컬럼에 표시). TEU는 차트 라인의 픽셀 역산치이며, 비용
# 탭 상단 stat 카드의 "₩791K/TEU"(7월)·"₩675K/TEU"(6월)와 완전히 정합하지는
# 않는다 — 목업 원본 자체가 손으로 그린 SVG라 두 숫자가 100% 일치하게
# 계산되어 있지 않았다(향후 실데이터 연동 시 자동 정합됨).
MONTHLY_COST = [
    dict(month="2026-03", freight=81300000, dnd=6000000, other=9000000, teu=164, note="chart_pixel_approx"),
    dict(month="2026-04", freight=88300000, dnd=4000000, other=7000000, teu=172, note="chart_pixel_approx"),
    dict(month="2026-05", freight=91000000, dnd=9000000, other=11000000, teu=168, note="chart_pixel_approx"),
    dict(month="2026-06", freight=95000000, dnd=5000000, other=8000000, teu=187, note="chart_pixel_approx"),
    dict(month="2026-07", freight=101000000, dnd=14400000, other=10000000, teu=183, note="exact_breakdown_table"),
    dict(month="2026-08", freight=68000000, dnd=17000000, other=6000000, teu=127, note="chart_pixel_approx; 진행중(월중 잠정치)"),
]
for row in MONTHLY_COST:
    row["total"] = row["freight"] + row["dnd"] + row["other"]
    row["source_type"] = "SYNTHETIC"
pd.DataFrame(MONTHLY_COST).to_csv(f"{OUT_DIR}/monthly_cost.csv", index=False)

print("생성 완료 (Transportation 도메인):")
for f in ["cargo_tracking.csv", "cargo_section_stats.csv", "vessel_mmsi.csv",
          "booking.csv", "booking_po.csv", "arrival_prep.csv", "inland_routing_option.csv",
          "schedule_search_result.csv", "dnd.csv", "dnd_weekly_bucket.csv", "monthly_cost.csv"]:
    print(" -", f)
