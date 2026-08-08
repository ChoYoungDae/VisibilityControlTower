# Synthetic Data — Item 단위 통합재고관리

`VisibilityControlTower_PRD.md` §8(Inventory 기능요구사항, 구
`ItemLevel_InventoryManagement_PRD.md` — 2026-08-07 세션에 §8로 통합됨)
대응 데이터. 전부 `generate_synthetic_data.py` 실행 결과이며 재실행하면
동일하게 재생성된다(`python generate_synthetic_data.py`).

## 목적

1. **화면(목업) 데모용** — `raw data/Tracking.xlsx`의 실제 Model(=Item)
   값과 FDEST ETA/QTY를 그대로 쓰고, 그 위에 On-hand/Outbound/Safety
   Stock만 합성해서 Normal/Risk/Shortage/Recovery 4가지 상태가 모두
   나오도록 설계함(아래 표).
2. **Inventory Engine 단위테스트용** — 2026-08-07 raw data 스냅샷엔 없는
   케이스(Pre-carriage, 완료건+버퍼, 완전동일 중복, QTY 결측)를
   `tracking_synthetic_edge_cases.csv`로 보완.

기준일(base_date) = 2026-08-07, 분석기간 = 2026-08-07 ~ 2026-09-30.

## 파일

| 파일 | 내용 |
|---|---|
| `wd_item_master.csv` | Item 6종(실제 Model 값) |
| `wd_onhand.csv` | 기준일 On-hand 스냅샷 |
| `wd_safety_stock.csv` | Item별 Safety Stock |
| `wd_outbound.csv` | 기준일~9/30 매일 일정량 Outbound(단순 등차, 데모용) |
| `pipeline_precarriage.csv` | MICROWAVE OVEN Pre-carriage 예시(계산 제외 대상, §14) |
| `tracking_synthetic_edge_cases.csv` | Pre-carriage 제외/입고버퍼 우선순위/완전동일 중복/QTY 결측 — 5개 케이스, `expected_behavior` 컬럼에 기대 동작 명시 |

## 검증된 시나리오 (실제 Tracking Inbound + 합성 W&D 결합 결과)

| Item | Risk Start | Shortage Start | Recovery | 의도 |
|---|---|---|---|---|
| REFRIGERATOR | 8/10 | 8/14 | 8/17(Shortage·Normal 동시) | Shortage → Recovery |
| RO COMPRESSOR(ROTARY COMPRESSOR) | 8/10 | 없음(최저 5,000) | 8/17(Normal) | Risk only, Shortage 없음 |
| MOTOR | 없음 | 없음 | — | 전 기간 Normal |
| PARTS FOR REFRIGERATOR | 8/7(기준일부터) | 8/11 | 8/17(동시) | 기준일부터 이미 Risk인 케이스 |
| REFRIGERATORS COMPRESSOR | 8/7 | 없음(최저 200) | 8/21 | 0에 근접했다 회복하는 간발의 케이스 |
| MICROWAVE OVEN | 9/29 근처 | 없음 | — | 대부분 Normal, Pipeline(Pre-carriage) 데모용 |

`wd_outbound.csv`의 Item별 1일 차감량은 스크립트 상단 `DAILY_OUTBOUND`에서
조정 가능 — 값을 바꾸면 위 표의 날짜도 달라지므로, 화면에 반영한 뒤엔
재계산 결과를 다시 확인할 것.

## 주의

- `source_type=SYNTHETIC`으로 전부 표시되어 있음 — 실데이터와 구분 가능해야
  한다는 §8.2 원칙대로다.
- `wd_outbound.csv`는 단순 등차 감소로 만든 데모용 수치이며 실제
  수요예측 패턴을 반영한 것이 아니다(§11 Out of Scope — 수요예측 모델
  자체는 플랫폼이 만들지 않음). 참고로 `visibility_control_tower_mockup.html`
  재고 탭에는 이 등차 수치를 요일 가중치+시드 고정 의사난수로 자연스럽게
  가공해서 반영했다(이 CSV 자체는 안 바뀜, PROGRESS.md 2026-08-07 세션
  기록 참고).
- 입고버퍼 기본값(며칠)은 아직 미확정(`VisibilityControlTower_PRD.md`
  §10 미해결 이슈)이라, `SYN-BUFFER-ATA-ONLY` 케이스는 버퍼 로직이 실제로
  구현된 뒤 기대값을 다시 계산해야 한다.
