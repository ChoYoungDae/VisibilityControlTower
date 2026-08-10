# Synthetic Data — `visibility_control_tower_mockup.html` 백업 데이터

`VisibilityControlTower_PRD.md` §8(Transportation)·§9(Inventory) 대응 데이터.
목업(`visibility_control_tower_mockup.html`)의 4개 탭(화물/업무/비용/재고)에
하드코딩되어 있던 값들을 CSV로 옮겨 담아, 향후 DB 시딩 시 화면에 이미 나온
숫자와 어긋나지 않게 하는 것이 목적이다. **화면(mockup) 값이 정본이고, 이
CSV들은 그 값을 그대로 옮긴 것** — 화면을 바꾸면 이 스크립트들도 같이
갱신해야 한다(반대 방향 아님).

두 개의 생성 스크립트가 있고, 재실행하면 동일하게 재생성된다:
- `python generate_synthetic_data.py` — Inventory 도메인(재고 탭)
- `python generate_synthetic_data_transportation.py` — Transportation
  도메인(화물/업무/비용 탭, 2026-08-10 세션 신규)

기준일(base_date) = 2026-08-07, 분석기간 = 2026-08-07 ~ 2026-09-30.

## 목적

1. **화면(목업) 데모용** — `raw data/Tracking.xlsx`의 실제 Model(=Item)
   값과 FDEST ETA/QTY를 그대로 쓰고, 그 위에 On-hand/Outbound/Safety
   Stock만 합성해서 Normal/Risk/Shortage/Recovery 4가지 상태가 모두
   나오도록 설계함(아래 표).
2. **Inventory Engine 단위테스트용** — 2026-08-07 raw data 스냅샷엔 없는
   케이스(Pre-carriage, 완료건+버퍼, 완전동일 중복, QTY 결측)를
   `tracking_synthetic_edge_cases.csv`로 보완.
3. **DB 시딩용 소스** — 화물/업무/비용 탭의 컨테이너·부킹·D&D·월별비용
   등 하드코딩 값을 구조화된 CSV로 확보해, DB 스키마를 잡을 때 화면과
   1:1로 대조 가능하게 함(2026-08-10 세션 신규 목적).

## 파일 — Inventory 도메인 (재고 탭, `generate_synthetic_data.py`)

| 파일 | 내용 |
|---|---|
| `wd_item_master.csv` | Item 7종(6종은 실제 Model 값, TEMPERATURE SENSOR 1종은 "정상" 대비 사례로 목업에 추가된 신규 Item — `source=SYNTHETIC_ITEM`) |
| `wd_onhand.csv` | 기준일 On-hand 스냅샷 |
| `wd_safety_stock.csv` | Item별 Safety Stock |
| `wd_outbound.csv` | 기준일~9/30 매일 일정량 Outbound(단순 등차, 데모용) |
| `pipeline_precarriage.csv` | MICROWAVE OVEN Pre-carriage 예시(계산 제외 대상) |
| `item_shipments.csv` | Item별 Inbound 화물 49건(Container-Item Mapping) — container_no/po_no/qty/Init.ETA/ETA/delayed. `itemCatalog.shipments`를 그대로 옮김(2026-08-10 신규) |
| `tracking_synthetic_edge_cases.csv` | Pre-carriage 제외/입고버퍼 우선순위/완전동일 중복/QTY 결측 — 5개 케이스, `expected_behavior` 컬럼에 기대 동작 명시 |

## 파일 — Transportation 도메인 (화물/업무/비용 탭, `generate_synthetic_data_transportation.py`, 2026-08-10 신규)

| 파일 | 내용 |
|---|---|
| `cargo_tracking.csv` | 화물 탭 컨테이너/HBL 리스트 11건(해상 7 + 항공 4) — POL/POD, 현재/도착예정 Vessel·Flight, Carrier ETA/PTA(P50·P95), TS, FDEST ETA, D&D LFD |
| `cargo_section_stats.csv` | 화물 탭 상단 요약 통계(scope×stage별 total/delayed) — **주의: 배후 모집단(총 128건) 자체의 원본 데이터는 없음, 화면에 하드코딩된 요약 숫자만 옮김. `cargo_tracking.csv`의 11건과 집계가 1:1로 맞지 않음(목업 자체의 한계)** |
| `vessel_mmsi.csv` | 목업에 나오는 실제 선박 6척의 실제 MMSI(VesselFinder/MarineTraffic 확인) |
| `booking.csv` | 업무 탭 부킹 리스트 4건 — 상태, SI/VGM/CY Cut-off, 수출통관, B/L |
| `booking_po.csv` | 부킹↔PO N:M 매핑(참고 표시용) |
| `arrival_prep.csv` | 업무 탭 도착 준비 4건 — 수입통관 상태, Inland Routing 잠금 여부 |
| `inland_routing_option.csv` | 도착 준비 건별 트럭/철도 옵션 비교(리드타임/비용/Free Time/선택여부) |
| `schedule_search_result.csv` | Port-to-Port 스케줄 조회 결과 예시 3건(ONE/MSC/CMA CGM) |
| `dnd.csv` | 비용 탭 체화료(D&D) 통합 리스트 7건(임박 3 + 발생중 4) |
| `dnd_weekly_bucket.csv` | 발생중 4건의 경과 주 단위(1~4주+) 일수 breakdown |
| `monthly_cost.csv` | 월별 물류비 현황(3월~8월, 운임/D&D/기타 + TEU) — **7월은 breakdown 테이블의 정확한 금액, 나머지는 SVG 차트 픽셀 좌표 역산 근사치**(`note` 컬럼에 구분 표시) |

## 검증된 시나리오 (재고 탭 — 실제 Tracking Inbound + 합성 W&D 결합 결과)

| Item | Risk Start | Shortage Start | Recovery | 의도 |
|---|---|---|---|---|
| REFRIGERATOR | 8/10 | 8/14 | 8/17(Shortage·Normal 동시) | Shortage → Recovery |
| RO COMPRESSOR(ROTARY COMPRESSOR) | 8/10 | 없음(최저 5,000) | 8/17(Normal) | Risk only, Shortage 없음 |
| MOTOR | 없음 | 없음 | — | 전 기간 Normal |
| PARTS FOR REFRIGERATOR | 8/7(기준일부터) | 8/11 | 8/17(동시) | 기준일부터 이미 Risk인 케이스 |
| REFRIGERATORS COMPRESSOR | 8/7 | 없음(최저 200) | 8/21 | 0에 근접했다 회복하는 간발의 케이스 |
| MICROWAVE OVEN | 9/29 근처 | 없음 | — | 대부분 Normal, Pipeline(Pre-carriage) 데모용 |
| TEMPERATURE SENSOR | 없음 | 없음 | — | 전 기간 Normal(대비 사례, 2026-08-10 신규) |

> **위 표는 2026-08-04 최초 생성 당시 값 기준이다.** 이후 여러 세션에 걸쳐
> 목업의 On-hand/Safety Stock/Outbound 수치가 입고·출고 규모 정합을 위해
> 손으로 더 현실적으로 조정되었는데(예: REFRIGERATOR on-hand 60,000 →
> 100,000), 이 CSV들은 2026-08-10 세션까지 그 변경을 반영하지 못하고
> **구버전 수치로 어긋나 있었다** — 이번 세션에 `generate_synthetic_data.py`의
> `ONHAND`/`SAFETY_STOCK`/`DAILY_OUTBOUND` 딕셔너리를 목업 기준으로
> 재동기화했다. 다만 위 Risk/Shortage/Recovery 날짜 표 자체는 재계산하지
> 않았으므로(Inventory Engine 미구현 상태), 실제 계산 로직을 붙일 때 다시
> 검증할 것.

`wd_outbound.csv`의 Item별 1일 차감량은 스크립트 상단 `DAILY_OUTBOUND`에서
조정 가능 — 값을 바꾸면 위 표의 날짜도 달라지므로, 화면에 반영한 뒤엔
재계산 결과를 다시 확인할 것.

## 파일 — 리드타임/발주 추천 (신규 컨셉, `generate_synthetic_data_leadtime.py`, 2026-08-10 신규)

"재고 투영이 Shortage 시점·부족 수량을 알려준다면, 여기에 노선별 리드타임
분포를 결합해 언제까지 얼마나 발주해야 하는지 추천할 수 있지 않을까"라는
대화에서 나온 컨셉을 데모로 구현하기 위한 데이터. **이 세 파일은 실 raw
data 분석이 아니라 컨셉 증명용 가정 데이터다** — 파일별 상세 한계는 파일
상단 주석 참고.

| 파일 | 내용 |
|---|---|
| `shipment_history.csv` | 6개 노선(목업에 실제 나온 노선·캐리어 재사용)의 과거 완료 화물 116건 — POL ATD/FDEST ATA/리드타임(일) |
| `lead_time_stats.csv` | 노선별 리드타임 통계(n/평균/표준편차/P50/P95) — `shipment_history.csv`에서 집계 |
| `item_primary_lane.csv` | Item → 대표 노선 매핑(데모 가정 — 실제 Container-Item Mapping 아님, `assumption_note` 컬럼에 근거 명시) |
| `reorder_recommendation.csv` | **계산 결과**(`db/build_db.py` 산출물) — Item별 Risk/Shortage 시점, 부족 수량, 권장 발주 시점(P95 리드타임 역산), 긴급도 |

## DB (컨셉 데모, `db/`)

`db/schema.sql`(SQLite 스키마) + `db/build_db.py`(CSV 적재 + 발주 추천 계산)로
위 CSV 전체를 `db/visibility_control_tower.db`에 적재한다. 실행:
`cd db && python build_db.py`. 매번 DB 파일을 지우고 새로 만드므로 재실행해도
안전하다. 상세는 `db/README.md` 참고.

## 아직 합성데이터로 못 채운 것 (알려진 잔여 gap)

- **`liveEvidenceExamples`(화물 탭 AI 근거 패널, 컨테이너 2건: HAMU2277719/
  CSNU6277348)** — 이건 raw data(Tracking.xlsx + CP_Vessel_List.xlsx +
  Port Congestion.xlsx)를 실제로 조인해 계산한 **진짜 분석 결과**라서
  합성데이터로 대체하지 않았다(대체하면 실제 통계적 근거를 조작하는
  꼴이 됨). PROGRESS.md 2026-08-09 세션 기록 참고.
- **Port Congestion / CP_Vessel_List / Incident List** — `raw data/`에 실
  파일이 있으나 아직 정규화된 synthetic-data로 옮기지 않았다.
- **Overview 탭 최상단 KPI 카드**(화물 총 128/지연17, 업무 총 15/액션 7
  등) — 위 `cargo_section_stats.csv`와 같은 한계(배후 모집단 원본 없음).

## 주의

- `source_type`(또는 `source`) 컬럼으로 실데이터/합성데이터 구분 가능
  (§8.2 원칙대로) — `REAL_MODEL_VALUE`/`REAL_VESSEL_VALUE`는 실제
  값, `SYNTHETIC`/`SYNTHETIC_ITEM`은 합성 또는 목업 전용 값.
- `wd_outbound.csv`는 단순 등차 감소로 만든 데모용 수치이며 실제
  수요예측 패턴을 반영한 것이 아니다(§11 Out of Scope — 수요예측 모델
  자체는 플랫폼이 만들지 않음). 참고로 `visibility_control_tower_mockup.html`
  재고 탭에는 이 등차 수치를 요일 가중치+시드 고정 의사난수로 자연스럽게
  가공해서 반영했다(이 CSV 자체는 안 바뀜, PROGRESS.md 2026-08-07 세션
  기록 참고).
- 입고버퍼 기본값(며칠)은 아직 미확정(`VisibilityControlTower_PRD.md`
  §10 미해결 이슈)이라, `SYN-BUFFER-ATA-ONLY` 케이스는 버퍼 로직이 실제로
  구현된 뒤 기대값을 다시 계산해야 한다.
- `monthly_cost.csv`의 3~6월/8월 금액은 SVG 차트 픽셀 좌표 역산 근사치이며,
  비용 탭 상단 stat 카드의 "₩791K/TEU"(7월)·"₩675K/TEU"(6월)와 완전히
  정합하지는 않는다 — 목업 원본 자체가 손으로 그린 SVG라 두 숫자가 100%
  일치하도록 계산되어 있지 않았다.
