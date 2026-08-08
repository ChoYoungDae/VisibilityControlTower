# Visibility Control Tower PRD

- 작성일: 2026-08-03 (Inventory 도메인 추가·목업 반영: 2026-08-04 / 지연 사유 분석 목적 재정의: 2026-08-05 / §8 Inventory를 `ItemLevel_InventoryManagement_PRD.md`와 통합·raw data 검증 반영: 2026-08-07)
- 버전: v1.4 (§8 Inventory 기능요구사항을 별도 트랙이던 Item 단위 통합재고관리 PRD와 통합, 실 raw data 검증 결과 반영)
- 근거 문서: [`VisibilityControlTower_기획.md`](VisibilityControlTower_기획.md), [`PROGRESS.md`](PROGRESS.md)
- 상태: 화물/업무/비용/재고 탭 모두 `visibility_control_tower_mockup.html`에 반영, 사용자 리뷰 진행 중. 지연 사유 분석은 실 raw data 기반 파일럿 착수 단계. 재고 탭은 `raw data/Tracking.xlsx` 실제 Item 6종 + `synthetic-data/` 합성 W&D로 목업 반영 완료.

---

## 1. 개요

본 서비스는 고객의 국제운송·통관 화물 정보와 재고 정보를 결합해 보여주는
Visibility 서비스다(재고 정보가 화물 정보로부터 파생되는 것이 아니라, 서로
다른 소스(Transportation·W&D 등)의 정보를 Item 단위로 결합하는 관계 —
§8.4 재고 계산식 참고). 현재 고객이 로그인 직후 자신의 전체 화물 상황과
그것이 재고에 미치는 영향을 한눈에 파악할 통합 진입점이 없거나 파편화되어
있다.

이 문서는 그 진입점을 **"대시보드"가 아니라 Visibility Control Tower**로
정의하고, 제품 요구사항을 정리한다.

## 2. 문제 정의

- 고객은 화물 위치를 전체 구간에 걸쳐 실시간으로 파악하기 어렵고, 파악한다
  해도 정확한 ETA를 예측하기는 아직 쉽지 않다. 트래킹 정보 자체에 오류가
  섞이기 쉬워, 서로 다른 소스 간 정보가 상충할 때 어느 쪽을 신뢰하거나
  어떻게 보정할지 판단이 필요하다.
- 업무(부킹/서류/Cut-off) 진행 상황과 비용(D&D 등) 리스크도 화물 상태와
  분리되어 있어, 담당자가 여러 화면·이메일·엑셀을 오가며 직접 종합해야 한다.
- W&D는 현재 재고(On-hand)는 관리하지만, 운송 중 재고(Inbound)까지 결합한
  **미래 재고(Projected Inventory)** 와 예상 Shortage를 Item 단위로 보여주지
  못한다. 담당자는 운송 상황과 재고 상황을 별도로 확인하고 머릿속에서
  직접 조합해야 한다.

## 3. 컨셉

> 가시성은 화물 상태에 국한하지 않는다. 그 화물이 만들어내는 업무(부킹·
> 서류·통관)와 비용(D&D 등) 리스크까지 함께 봐야 완결된 그림이 된다. 또한
> 물류 현장은 컨테이너·B/L 같은 운송 단위로 움직이지만, 고객이 실제로
> 궁금한 것은 결국 Item/SKU 단위다. 이 서비스는 운송 단위 가시성을 Item
> 단위 가시성으로 변환해, Transportation과 W&D 재고를 하나로 잇는
> 관제탑(Control Tower)이다.

## 4. 대상 사용자

- 본 서비스를 이용하는 화주(고객사) 담당자, 로그인 계정 기준 단일 유형 고객군.
- 화물량·업종별 세분화된 페르소나나 역할별(마케팅/물류담당 등) 화면 분기는
  현재 범위에서 다루지 않는다 — 모든 사용자가 같은 화면 전체(Transportation+
  Inventory)에 접근한다.
- 참고로 도메인 실무상 화물/업무/비용은 물류·수출입 운영 담당자에게, 재고
  (Projected Inventory/Shortage)는 Demand Planner·자재·구매 계획 담당자에게
  더 직접적으로 도움이 될 것으로 예상된다. 이는 화면 분기 근거가 아니라
  콘텐츠 우선순위·설명 톤을 잡을 때 참고하는 설명일 뿐이다.

## 5. 백본 구조 (Backbone)

```
부킹 → 선적 준비(CI/PL 확보) → 선적 → 트래킹(해상/항공) → 하역 → Inland Routing → Final Destination
                                                                          ↓
                                                                W&D Inventory(On-hand)
```

- **Item/SKU 단위 트래킹의 출발점은 PO가 아니라 CI/PL 확보 시점이다**
  (2026-08-05 세션에서 전환 확정). PO는 이상적인 소스지만, 포워더가 화주로
  부터 PO를 직접 받는 사례는 현실적으로 드물다 — PO는 화주-공급업체 간
  문서라 포워더가 당사자가 아니고, 단가·결제조건 등 상업 기밀이 담겨 있어
  화주가 제3자에 공유하길 꺼린다. 반면 CI/PL은 수출통관에 필수라 포워더가
  정상적인 업무 흐름 안에서 이미 받는 문서다.
- **트레이드오프**: PO 기반이었다면 **부킹 이전**부터 Item 단위 가시성이
  가능했겠지만, CI/PL 기반에서는 **부킹 이후, 선적 준비(수출통관·Cut-off
  즈음) 단계부터**만 Item 단위 가시성이 시작된다. 부킹 전 단계는 Item
  단위가 아니라 부킹/화물 단위 정보로만 다룰 수 있다 — §7.2 업무 탭 최상위
  리스트 구조, §8.1 Inventory 도메인 모델 루트 노드를 이 전제로 다시 정리
  해야 한다(아직 미반영, 해당 섹션 리뷰 시 처리).
- 운송 모드: 해상(주력) + 항공. 철도/트럭은 내륙구간(Inland Routing)에서만 다룬다.
- Final Destination 도착 이후 W&D의 On-hand 재고와 결합되면서, 같은 백본이
  Transportation(운송 운영) 관점과 Inventory(재고 계획) 관점 두 가지로
  갈라져 나간다 — §6 참고.

## 6. 정보 구조 (IA)

### 도메인 분리 원칙

같은 Supply Chain Event(부킹→선적→트래킹→하역→Inland→Final Destination)를
**서로 다른 관리 단위(Granularity)로 보는 두 개의 View**로 나눈다.

| 도메인 | 관리 단위 | 목적 |
|---|---|---|
| **Transportation** | 컨테이너 / B/L (해상), HBL (항공) | 운송 운영 — 어디에 있고, 왜 그런 상태인가 |
| **Inventory** | Item (W&D SKU와 동일 단위) | 재고 계획 — 앞으로 재고가 얼마나 있을 것인가 |

Transportation 데이터를 변경하지 않고 Inventory에서 그대로 재사용한다
(동일 이벤트, 다른 집계 단위일 뿐 별도 데이터 파이프라인이 아님).

### 탭 구조 (2단)

```
Overview  (Transportation + Inventory 통합, 최상위 단일 화면 — 도메인별 개별 Overview 없음)
├── Transportation
│    ├── 화물   (컨테이너/B/L 단위 — 위치·상태·지연 원인·확률적 ETA)
│    ├── 업무   (컨테이너/B/L 단위 — 부킹·서류·통관·Inland Routing 진행)
│    └── 비용   (D&D·PCS 등 비용 리스크)
└── Inventory
     ├── Projection  (Item별 일자별 재고 타임라인, Shortage는 이 안의 필터 뷰로 흡수)
     └── Inbound     (Item별 입고 예정 리스트)
          └── Item 상세 (드릴다운 — 별도 탭 아님, Projection/Inbound에서 클릭 진입)
```

- **Overview 하나만 존재**: Transportation·Inventory 각각에 별도 Overview를 두지
  않고, 최상위 Overview가 두 도메인의 핵심 KPI를 함께 보여준다. 구성 방식
  (설계자 우선순위 선정 vs 사용자 커스터마이즈)은 두 도메인 설계가 끝난 뒤 논의.
- **표기 규칙**: 모든 수치에 단위 표기. "총 N건 중 M건" 형태로 전체 대비 이슈
  건수 표시 (화물 탭에선 Total/Delayed 형태로 구체화).
- **명칭/톤**: 제목줄에 서비스 브랜드명은 노출하지 않는다(브랜드 마크
  CI만). "Visibility Control Tower"는 컨셉/제품 성격을 나타내는 이름이라 이
  규칙 대상이 아니며, 브랜드 마크 옆에 텍스트로 노출한다. 고객사명에 존칭
  표현("귀하" 등)은 사용하지 않는다.
- **화면 텍스트 언어 규칙**: 물류 업계 용어(Pre-carriage/Main-carriage/
  On-carriage, ETA/PTA/TS/D&D/LFD/MMSI 등)는 영어, 그 외 일반 설명·상태값·
  안내문은 한글. 상단 탭바(Overview/화물/업무/비용)는 한글 유지. Inventory
  최상위 탭명은 "재고", 하위 탭명은 "재고 투영"(Projection)/"입고 예정"(Inbound)으로
  확정(업계 관용 영어가 아니라고 판단해 한글 명칭 채택).

## 7. Transportation 기능요구사항

### 7.1 화물 탭 — 어디에 있고, 언제 도착할 것인가

**목적**: 화물 상태·위치와 지연 원인, 확률적 도착 예측을 컨테이너/B/L 단위로
한 화면에서 보여준다. (Item 단위 재고 투영은 Inventory 도메인으로 이관 — §8 참고.)

**리스트 구조**
- 리스트 단위: 해상=컨테이너(없으면 HBL), 항공=HBL. 컨테이너 번호는 11자리
  붙여쓰기, 하이픈 없음(예: `TCLU5520134`).
- 해상/항공은 한 리스트로 섞지 않고 같은 화면에 순차 배치(해상 섹션 → 항공
  섹션). 상단 "Jump to Sea/Air"는 필터가 아니라 스크롤 이동만 수행.
- 상단 요약 통계는 해상+항공 합산과 모드별 분리를 함께 표시.
- 리스트 첫 컬럼: Container No(굵게) 아래 BL No, PO No 서브라인(LCL/HBL은
  ID 자체가 BL이라 PO No만). 우측은 POL → POD 구간으로 표기(PO 컬럼 중복
  표기 안 함).
- 좌측 상단: 단위 토글(Container/HBL). 우측 상단: Search(B/L·Container·
  PO No 통합 검색). 기존 "Item" 토글은 삭제하고 Inventory 도메인으로 이동.

**상태 3단계** (탭 전환 시 컬럼 자체가 바뀜, 행 필터링 아님)
| 단계 | 표시 컬럼 |
|---|---|
| Pre-carriage | 예정 Vessel/Flight, POL ETD, TS(예정) |
| Main-carriage | 현재 Vessel/Flight, 도착예정(POD) Vessel/Flight, TS, Carrier ETA/PTA |
| On-carriage | FDEST ETA, D&D LFD |

**지연 표시**
- 지연 유형을 선적 지연 / 운송 지연 / 도착 지연으로 구간별 분리.
- 상단 요약과 각 섹션 모두 Total/Delayed 병기(Delayed는 빨간색 강조).
- TS(환적) 횟수는 해상·항공 Pre-carriage/Main-carriage 단계에서 칩으로
  표기(On-carriage는 이미 환적이 종료된 시점이라 표기 대상 아님).

**ETA / PTA**
- **ETA**: 대부분 선사가 공지하는 값 그대로(POL ETD, Carrier ETA 등)를
  쓰지만, 전부는 아니다 — 선사 공지가 없거나 늦는 구간은 담당자가 수기로
  확인해 업데이트하는 경우도 있다. 소스가 선사 공지든 수기 입력이든 화면에
  보이는 값은 "ETA"로 동일하게 취급한다(PTA처럼 소스별로 신뢰도를 구분해
  보여주진 않음).
- **PTA(Predictive ETA)**: 그래프DB·AIS·항만혼잡도 + 과거 "예측 vs 실제 도착"
  정확도 이력 데이터를 결합한 자체 예측값. **P50(중앙값)과 P95(보수적
  기준선) 두 값으로 표현**하며, 근거 불명확한 임의의 단일 확률 수치(예: "72%")는
  사용하지 않는다.
- PTA는 **Main-carriage 구간에만 적용**. 선적 전은 POL ETD, 하역 후는
  FDEST ETA가 기준.
- 의존성: 선사·항로·선박타입별 "과거 예측 정확도 이력" 데이터 확보 전제.
- Inventory 도메인이 Inbound 인식 시점을 계산할 때도 이 FDEST ETA(의 P95)를
  그대로 재사용한다 — §8.3 참고.

**지연 사유 분석** (구 "지연 계보도/Delay Lineage" — 명칭 변경, 목적 재정의: 2026-08-05)
- **목적 정정**: 지연 원인을 서술하는 것 자체가 최종 목표가 아니다. 화물이
  언제 창고에 도착할지(특히 Inventory의 FDEST ETA 인식 시점, §8.3)를 알려주는
  소스는 여러 개(선사 milestone, AIS 기반 예측 벤더 등)이고, 서로 값이
  다를 때가 있다. 지연 사유 분석의 실제 역할은 **이런 상충 상황에서 이번
  건은 어느 소스를 더 신뢰해야 하는지 판단하는 정황 증거(corroborating
  evidence)를 모으는 것**이다. 그 판단 결과가 PTA(P50/P95, 아래 항목)와
  Inventory Inbound 인식 시점의 정확도로 직결된다.
- **2단 구조**:
  1. 정적 신뢰도 — 소스별·항로별·선사별 **과거 예측 정확도 이력**(누적
     오차 통계)로 계산하는 베이스라인 가중치. 순수 통계이며 AI가 필요
     없다.
  2. 건별 보정 — 이번 건에서 소스 간 값이 상충할 때, 항만 혼잡도·뉴스 등
     독립적인 신호가 어느 쪽 소스를 뒷받침하는지 확인해 신뢰도를 동적으로
     조정한다. 정형화되지 않은 여러 신호를 엮어 판단해야 하므로 **AI/LLM
     추론이 실제로 필요한 지점은 이 단계뿐**이다.
- 시각화 형태: 그래프/체인형으로 확정(타임라인/스텝형은 탈락). 예: 컨테이너
  지연 → 선박 3일 지연 → 부산항 접안 대기 → 항만 혼잡도 "높음". 단, 이
  서술은 화면의 핵심 콘텐츠가 아니라 **최종 산출물(신뢰도 조정된 도착일)의
  근거·투명성 표시**로 쓰인다.
- 환적 있는 경우: 환적선 스케줄 미확정 → 지연은 아니나 리스크로 표시(단,
  "리스크" 판정 기준 자체는 아직 미정 — §10 참고).

**선박 위치 연동**
- 선박명 클릭 → 실제 AIS 위치를 지도에 표시(`vessel-tracker/` 프로토타입,
  §9 참고). 항공 편명은 AIS 대상이 아니라 미연동.

### 7.2 업무 탭 — 현재 어느 단계에 있고, 업무 지연은 없는가 (신규 개척 영역)

**목적**: 부킹부터 서류·통관·Inland Routing까지 능동적 행정 액션(제출·승인·
결정)의 진행 상황을 추적하고 실행까지 연결한다.

**분류 기준**: 업무 탭 = 능동적 행정 액션, 화물 탭 = 그 결과로 발생하는 물리적
이동/위치. (예: 게이트인/On-board/공컨테이너 픽업은 화물 탭 소관, B/L 발급은
서류이므로 업무 탭 소관.)

**리스트 구조 — 1단, 부킹이 최상위** (2026-08-05 세션에서 PO 리스트 제거,
구조 변경 — §5 백본의 "Item 단위 트래킹 출발점을 CI/PL 확보 시점으로
전환" 결정에 따름)
- 최상위이자 유일한 리스트: **부킹 리스트**. 부킹No, 관련 PO No(있으면
  서브라인으로 참고 표시만 — §7.1 화물 탭의 PO No 서브라인과 동일하게
  CI/PL에 기재된 참조번호일 뿐 별도 추적 대상 아님), Item/수량(부킹 시점엔
  "미확정"으로 표시, Cut-off 준비 중 CI/PL 확보 시 채워짐), 부킹 상태(요청/
  확정/롤오버), Cut-off(SI/VGM/CY 통합 카운트다운), 수출통관, B/L 발급.
- **PO는 더 이상 별도 엔티티로 추적하지 않는다.** 포워더가 화주로부터 PO를
  직접 받지 못하는 경우가 대부분이라, 부킹 이전 단계에 "고객의 전체 PO
  목록 중 아직 부킹 안 된 것"을 보여주는 입구 화면은 성립하지 않는다 —
  포워더가 아는 첫 이벤트는 부킹 요청이다.
- 콘솔리데이션(여러 PO가 한 부킹으로 묶임)·분할선적(한 PO가 여러 부킹으로
  쪼개짐) 같은 관계는, PO 자체를 추적해서가 아니라 **CI/PL에 찍힌 PO
  참조번호를 부킹 행 아래 여러 줄로 나열**하는 방식으로만 보여준다(실체
  추적이 아니라 표시상의 참고 정보).

**부킹 상태**
- 순서: 요청 → 확정 → (예외) 롤오버 → 재확정 → …
- 롤오버는 "대기 상태"가 아니라 **이미 확정된 부킹이 선사 사정(스페이스
  부족·blank sailing 등)으로 다음 항차로 밀려나는 예외 이벤트**.

**Cut-off (SI/VGM/CY)**
- 부킹 단위(같은 sailing에 걸린 화물 전체에 동일 시각 적용)로 서로 다른
  시점을 하나의 카운트다운 타임라인으로 통합 표시.
- VGM만 컨테이너별 개별 제출 필요 → "VGM 3/5 제출완료" 식 진행률 + 단위
  표기("컨테이너") + 설명 툴팁 + 하단 각주.
- 롤오버 발생 시 해당 부킹의 cut-off 세트 전체가 새 sailing 기준으로 리셋되며,
  화면에 이를 표시해야 함.

**섹션 2분할**
- **선적 준비**: 부킹 → Cut-off → 수출통관(CI/PL 확보로 Item 확정) → B/L
  (Pre-carriage 시점).
- **도착 준비**: 수입통관 → Inland Routing (Main-carriage 후반~On-carriage 시점).

**도착 준비 상세**
- 화물 탭과 동일 컨테이너/HBL 레코드의 필터+액션 뷰(별도 데이터 아님).
  화물 탭에 이미 있는 FDEST ETA/D&D LFD는 중복 표시하지 않고, 통관상태·
  Inland Routing처럼 화물 탭에 없는 컬럼만 추가.
- 노출 기간: 기본 POD ETA 기준 D-14 이내(철도의 더 이른 리드타임까지 커버),
  사용자가 기간 좁혀보기 가능.
- 수입통관은 화물마다 필수 여부가 다름 → "통관 필요여부/상태"(해당없음/
  진행중/완료) 컬럼. 필요한 화물은 통관 미완료 시 Inland Routing 액션 잠김.
- 역방향 연동: Inland Routing 실행(트럭/철도 선택) 결과가 화물 탭 FDEST ETA
  재계산 입력값으로 즉시 반영(같은 레코드, 별도 동기화 불필요). 이 FDEST ETA는
  Inventory 도메인의 Inbound 인식 시점에도 그대로 흘러 들어간다.
- 리드타임 참고: 드레이지(트럭) 기준 POD 도착 5~7일 전 예약 권장, 철도는
  스케줄 고정이라 7~10일+ 필요할 수 있음. POD ETA 기준 D-7 트리거로 섹션
  활성화 제안.

**스페이스 타이트 신호**
- 선사-Pantos 1:1 계약 구조상 고객별 정확한 allocation 잔여는 노출 불가·비선호.
- 대신 **Pantos 항로별 부킹 성공률/거절률 기반 타이트 정도 신호**로 대체.
- 표현 방식: 절대 수치가 아니라 **등급(원활~매우타이트) + 추세 화살표**
  (Freightos Terminal Booking/Supply Index 참고, 정밀 퍼센트 지양).

**Port-to-Port 스케줄 조회**
- 별도 컴포넌트, 진입점 2곳:
  1. 기존 부킹 상세 행의 "스케줄 조회" 액션 — 해당 부킹의 POL/POD 프리필
     (주로 롤오버 등으로 대체 스케줄을 재확인할 때 사용).
  2. 업무 탭 상단 고정 진입점 — 특정 부킹과 무관하게 독립 조회, 결과에
     "이 스케줄로 부킹 요청" 액션이 붙어 신규 부킹 생성으로 이어짐.
- 입력: POL/POD/기간. 결과: 선사·선박·POL ETD·POD ETA·Lead Time·TS·탄소배출.
- 탄소배출 축은 §7.4 대안 루트 추천과 동일 축 재사용, 추후 연결.
- Overview 진입점 추가는 Overview 재구성 시점으로 보류.

### 7.3 비용 탭 — 불필요한 비용이 발생하고 있지는 않는가

- **D&D(체화료·반납지체)**: 화물 탭 트래킹과 밀접, Free Time 카운트다운으로 관리.
- **PCS(항만혼잡할증)**: 선사가 항로별로 "공지"로 부과 — 성수기형(LA/롱비치
  Q3~Q4 등 반복 패턴) + 지정학 위기형(홍해 우회 등 긴급 할증) 모두 해당.
  가시성 가치는 예측이 아니라 **흩어진 선사 공지를 미리 모아 해당 고객에게
  알려주는 것** — Port 혼잡도 패널의 크롤링 소스를 확장해서 구현.
- 후보로만 기록(확정 항목 아님): 할증료 일반, 서류오류 정정료, 롤오버 간접비용,
  CFS 보관료, FX — 담당자 체감상 우선순위 근거 미확보.
- 상태: **화면 설계 착수 전.**

### 7.4 대안 루트 추천 (사고 발생 시)

- 리드타임/운송모드/탄소배출 등 다축으로 평가해 대안을 제시.
- 판단 로직 자체보다 **비교 대상 데이터(대안 스케줄, 실시간 선복, 운임,
  탄소계수) 확보**가 핵심 과제 — "기능 개발"이 아니라 "데이터/제휴 확보"
  문제로 정의.
- 상태: 콘셉트 정의만 된 상태, 설계 착수 전.

## 8. Inventory 기능요구사항

**목적**: WMS를 대체하지 않고, Transportation 이벤트와 W&D 재고 정보를
Item 단위로 결합하여 **미래 재고(Projected Inventory)** 와 예상 **Shortage**를
보여주는 재고 계획(Planning) 뷰. Transportation이 "운송 운영" 관점이라면
Inventory는 "재고 계획" 관점 — 같은 이벤트를 다른 단위(Item)로 재구성한 것.

> 이 §8은 한때 별도 파일(`ItemLevel_InventoryManagement_PRD.md`)로
> 분리되어 있던 Item 단위 재고관리 요구사항을 통합한 것이다. 별도 파일은
> 더 이상 존재하지 않으며, 이 문서 §8이 유일한 기준본이다(통합 경위는
> PROGRESS.md 참고).

핵심은 Forwarding에서 **Item별 Inbound 수량과 FDEST ETA를 최대한 정확하게
제공**하는 것이다. 이를 W&D 재고 데이터와 결합하면 고객은 특정 Item의 재고가
언제 Risk 또는 Shortage 상태가 되는지, 언제 다시 회복되는지를 사전에 확인할
수 있다. 장기적으로는 Shortage 발생 시 기존 Supply Pipeline과 신규 조달
가능성을 함께 검토해 고객의 **발주 의사결정**까지 지원하는 것이 목표지만,
실제 PO 생성·공급처 전달·Booking 등 **발주 실행 자체는 Target Vision 범위
밖**이다(§8.10 발전 방향 참고).

### 8.1 도메인 모델

Item의 출처는 PO가 아니라 **Commercial Invoice(CI) / Packing List(PL)**다
(2026-08-05 세션에서 §5 백본 전환에 맞춰 정정 — 근거는 §5 참고).

```
Commercial Invoice / Packing List  (Item/SKU 출처 — PO No는 참조 라벨로만 포함)
 └── Item ──(Container-Item Mapping, N:M)── Container
      │
      ├── B/L                 (Item이 속한 선적 단위)
      └── W&D Inventory       (Item의 On-hand)
```

- Item은 W&D SKU와 동일한 관리 단위(Granularity)를 가지는 표준 Business Object.
- **Item ↔ Container는 N:M** — Container-Item Mapping이라는 별도 연결
  엔티티로 표현한다(§7.1의 Item 통합 뷰와 동일하게, 한 Item이 여러 Container·
  여러 화물에 걸쳐 존재할 수 있음).
- Container-Item Mapping이 없는 경우 §8.4의 정책에 따라 BL ETA로 보수적으로
  대체한다.
- PO는 별도 엔티티로 추적하지 않는다(§7.2 참고) — CI/PL에 참조번호가
  찍혀 있으면 Item 상세에 참고용 라벨로만 노출한다.
- **현재 확보한 샘플 고객 데이터(`raw data/Tracking.xlsx`)에서는 Item이
  `Model` 컬럼으로 표현되고, 수량은 그 옆의 `QTY`다** — `Model`은 제품
  전체의 고정 용어가 아니라 이 고객 데이터에서 Item을 표현하는 컬럼명일
  뿐이다.

### 8.2 데이터 소스

**Transportation(Forwarding)** — 현재 확보 가능한 실제 데이터:
- B/L 및 Container가 포함된 Tracking 정보, Item 정보, Item별 실제 수량
- POD ETA, FDEST Init. ETA, FDEST ETA, FDEST ATA
- Vessel Calling Port Schedule, PCP/CP로 활용 가능한 Calling 정보
- 주요 Port의 최근 주차별 Dwell Days/Congestion 정보
- Vessel·Port 관련 News 데이터

**W&D**:

| 구분 | 소스 | 비고 |
|---|---|---|
| On-hand | W&D | 특정 스냅샷 시점(예: 기준일 0시) 재고 |
| Inbound | Transportation | §7.1의 FDEST ETA 재사용, §8.4 참고 |
| Outbound | 고객 ERP/W&D (또는 그에 준하는 출고 계획 값) | §8.5 참고 — 소스를 특정 시스템으로 고정하지 않는다 |
| Safety Stock | 고객 ERP/W&D 마스터 데이터 | Item별 등록값, 미등록 Item은 강조 표시 대상에서 제외 |

플랫폼은 수요를 생성하지 않고, 위 입력 데이터를 이용해 미래 재고를 계산만
한다. **MVP에서 W&D 실데이터를 확보하지 못하는 경우 합성데이터(Synthetic
Data, `synthetic-data/`)를 사용**하며, 실제 데이터와 합성데이터는 화면에서
구분 가능하도록 관리한다(`source_type=SYNTHETIC` 등).

Container, Vessel, Port는 하나의 종속 계층이 아니라 각각 독립적인 Entity로
보고 필요한 관계를 연결한다. Port Congestion이 FDEST ETA에 직접 영향을
준다고 단순하게 판단하지 않으며, 기본 영향 관계는 다음 순서로 본다: Port
Congestion/이슈 → Calling Port(CP) → Vessel Schedule → POD ETA → POD
이후 운송 일정 → FDEST ETA → Item Inbound Date → Projected Inventory.
MVP에서는 Port Congestion이나 News가 ETA 변화의 직접적인 원인이라고 자동
단정하지 않는다.

### 8.3 Item 단위 계산 원칙 (Item × Date)

Inventory Engine의 기본 관점은 **Item × Date**다. 같은 Item이 여러 B/L,
Container 또는 Shipment에 존재하더라도 동일한 FDEST ETA 날짜에 도착한다면
해당 날짜의 Inbound 수량으로 합산한다.

예:

| Item | Shipment | FDEST ETA | Qty |
|---|---|---|---|
| ITEM-A | A | Aug 15 | 300 |
| ITEM-A | B | Aug 15 | 500 |
| ITEM-A | C | Aug 15 | 200 |
| ITEM-A | D | Aug 20 | 700 |

재고 계산에서는 Aug 15 = 1,000 / Aug 20 = 700으로 합산해서 사용한다. B/L,
Container, Vessel 등의 정보는 사용자가 해당 Inbound의 상세 근거를 확인할 때
드릴다운(§8.7)으로 보여준다.

### 8.4 Inbound 인식 시점 및 반영 기준

FDEST 관련 날짜는 다음 순서로 정의한다: **On-board 시점의 FDEST Init.
ETA**(최초 예상) → 운송 진행에 따라 갱신되는 **현재 FDEST ETA** → 실제
최종 도착인 **FDEST ATA**. MVP의 미래 재고 계산에는 **현재 FDEST ETA**를
사용하고, FDEST Init. ETA는 최초 예상과 현재 예상의 변화 확인(지연 여부
비교)에만 활용한다 — 화물 탭 PTA(P50/P95)와 달리 이 확률적 표현은 Inventory
계산에는 쓰지 않는다.

| 조건 | 계산 방식 |
|---|---|
| Container-Item Mapping 존재 | Container의 **현재 FDEST ETA(내륙운송 포함 최종 목적지 도착 기준)** |
| Container-Item Mapping 미존재 | 동일 B/L 내 Container 중 **가장 늦은 FDEST ETA** |

**On-board 확인 물량부터 Inbound로 반영**한다. On-board 이전의
Booking/Pre-carriage 물량은 아직 실제 해당 선박에 선적될지 불확실하고 ETA
정확도도 낮기 때문에, Projected Inventory에 바로 포함해 잘못된 재고 안정
신호를 주지 않는다 — 대신 별도의 **Pre-carriage/Booked Pipeline** 정보로
제공할 수 있다(Item, Planned Qty, Expected POL ETD, Planned Vessel,
"On-board: Not Confirmed").

FDEST 도착과 실제 창고 입고 사이에는 시차(버퍼)가 있을 수 있다는 점도 반영
원칙에 포함한다. raw data에 실입고일(**W/H In Date**) 필드가 실제로 존재하는
것을 확인했으므로, **있으면 그 값을 1순위로 쓰고, 없으면 FDEST ATA + 버퍼
(2순위), 그마저 없으면 FDEST ETA + 버퍼(3순위)**로 추정한다. 버퍼의 구체적
일수는 아직 확정하지 않았다 — 확보한 raw data 스냅샷엔 완료건(FDEST ATA
존재)이 아직 없어 실측 검증도 못한 상태다(§10 참고, 검증 이력은
PROGRESS.md).

향후 필요하면 다음 두 Projection을 분리해 제공할 수 있다(현재는 Confirmed
Projection만 계산):

```
Confirmed Projection = On-hand + On-board Inbound − Outbound
Planning Projection   = Confirmed Projection + Pre-carriage/Booked Pipeline
```

두 개를 하나의 재고 숫자로 혼합하지 않는 것이 원칙이다. Vessel Departure
이전(Booking/Stuffing/Gate-In 단계)에는 Projected Inventory 계산을 시작하지
않고, 업무 진행 현황만 제공한다.

### 8.5 재고 계산 및 상태 판정

```
Projected Inventory(t) = On-hand(기준일) + Σ Inbound(≤t) − Σ Outbound(≤t)
```

- 일자별 누적 계산이며, 단일 스냅샷 값이 아니라 §8.7 Projection 타임라인
  전체에 걸쳐 계산된다. Inbound는 §8.4대로 **On-board 이후 물량만** 포함한다.
- **Outbound은 소스를 특정 시스템에 고정하지 않는다** — 수요예측(Demand
  Forecast)이든 확정 출고계획(Outbound Plan)이든 평균 출고량 추정치든,
  고객 시스템에서 "주어지는 입력값"으로 취급한다. 어떤 값을 쓰든 Projected
  Inventory 정확도는 그 입력값의 정확도에 달려있다는 점을 화면에 명시한다.
  (Out의 값 성격에 따라 In과 낙관/비관 방향을 맞출지는 §10 미해결 이슈로 유지.)

Safety Stock을 기준으로 미래 재고 상태를 3단계로 구분한다:

```
Projected Inventory > Safety Stock        → Normal
0 < Projected Inventory ≤ Safety Stock    → Risk
Projected Inventory ≤ 0                   → Shortage
```

단순 Shortage뿐 아니라 실제 재고가 남아 있더라도 Safety Stock 이하로 내려가는
위험 구간을 함께 보여준다. 주요 결과값: Risk 진입 시점, Shortage 발생 시점,
부족 수량, Shortage에서 회복하는 시점, Normal로 복귀하는 시점.

### 8.6 ETA Confidence

ETA에는 날짜 하나만이 아니라 "현재 시점에서 이 ETA를 얼마나 신뢰할 수
있는가"를 함께 전달하는 Confidence 개념이 필요하다. MVP에서 복잡한
Confidence 모델을 반드시 구현할 필요는 없다. 기본 개념: Booking/
Pre-carriage(Provisional/낮은 신뢰) → On-board(FDEST ETA 계산의 본격 시작)
→ 운송 진행(ETA 지속 업데이트) → POD/FDEST 접근(정확도 상승) → FDEST(Actual).
실제 Confidence는 Route·TS·Port 변동성·운송 단계 등 다양한 요소를 반영해
향후 발전시킬 수 있다. **선사 ETA가 선박 위치·스케줄로 볼 때 비합리적으로
보일 때 자체적으로 수정하는 것**은 장기적으로 필요하나 MVP에서는 다루지
않는다(§10).

### 8.7 화면 구성

MVP의 중심 화면은 **Item별 통합 재고 흐름(Inventory Trend)**이다.
Shipment/Transportation 화면을 먼저 보여주는 것이 아니라 사용자가 최종적으로
알고 싶은 재고 결과(Normal → Risk → Shortage → Recovery로 변화하는 과정)를
먼저 보여준다.

**재고 투영(Projection)**
- Item별 일자별 Inventory Timeline: `Date | Inbound | Outbound | Projected`,
  Safety Stock 이하 및 음수 재고를 색으로 강조.
- **Shortage는 별도 탭이 아니라 이 화면의 필터 뷰**: Projected가 Safety
  Stock 이하 또는 음수로 내려가는 Item만 걸러서 보여준다.

**입고 예정(Inbound)**
- 표시 정보: Item, Qty, FDEST ETA, Delay Status.

**결과에서 원인으로 Drill-down** — 사용자는 복잡한 Transportation 정보를
먼저 이해할 필요 없이, 먼저 재고 결과를 보고 필요할 때만 내려간다:

```
Unified Inventory Trend → 특정 Risk/Shortage/변곡점 → 해당 일자의 Inbound/Outbound
→ Item Inbound → B/L/Container/Tracking → FDEST Init. ETA/현재 FDEST ETA
→ 관련 Vessel → Calling Port Schedule/PCP/CP → Port Congestion/관련 정보
```

**Item 상세** (Projection/Inbound에서 드릴다운, 별도 탭 아님)
- Current Inventory, Projected Inventory Timeline, Inbound Schedule,
  Shipment History, B/L, Container Tracking. Transportation Tracking 클릭
  시 §7.1 화물 탭의 해당 컨테이너로 이동.

**Overview KPI** (§6의 통합 Overview에 포함될 후보)
- Current Inventory, Inbound Inventory, Projected Inventory, Shortage Items,
  Today's Expected Receiving.
- ~~Items at Risk~~: Shortage Items와 구분이 불명확해 이번 버전에서는 제외.
  "아직 Shortage는 아니지만 Safety Stock에 근접" 같은 별도 정의가 필요하면
  추후 추가.

### 8.8 MVP에서 AI의 역할

MVP의 핵심 계산(Inbound Qty 합산, Projected Inventory 계산, Safety Stock
비교, Normal/Risk/Shortage 판정) 자체를 AI가 담당할 필요는 없다 — 결정론적
계산으로 처리하는 것이 적합하다. AI는 Forwarding Intelligence를 발전시키는
과정에서 활용할 수 있다: Calling Port 상황 분석, Port Congestion 정보 해석,
Vessel/Port 관련 News 분석, ETA Risk Context 설명, 향후 ETA Confidence
고도화, 향후 Monitoring Agent. **AI가 Port Congestion이나 News를 보고 근거
없이 FDEST ETA를 임의 변경해서는 안 된다.**

### 8.9 MVP에서 검증하려는 것

MVP의 목적은 완성된 시스템을 만드는 것이 아니라 다음 가설을 검증하는
것이다:

> W&D의 On-hand/Outbound/Safety Stock에 Forwarding의 Item-level In-transit
> Inventory를 결합하면, 고객이 미래의 재고 Risk와 Shortage를 더 일찍
> 이해하고 대응 판단을 내리는 데 실질적인 가치가 있는가?

이를 위해 Forwarding 영역은 확보 가능한 실제 Excel 데이터를, W&D 영역은
확보하지 못하는 데이터를 합성해서 쓴다. 완벽한 자동화보다 End-to-End 사용자
경험을 먼저 만들고, 개발 과정에서 실제 데이터의 구조와 한계를 확인하면서
다음 버전을 구체화한다.

### 8.10 MVP 이후 발전 방향

```
MVP: 실제 Forwarding Excel + Synthetic W&D + Current FDEST ETA + Inventory Trend
   ↓
Next: Forwarding Data 자동화, PCP/CP/Port Risk Intelligence, ETA Confidence,
      POD 양하 시 Shortage 임박도 기반 우선순위 배정
   ↓
Advanced: ETA Prediction/Adjustment, Data-driven Confidence, AI/Agent Monitoring
   ↓
Target Vision: Shortage 발생 → 기존 Supply Pipeline 확인 → 추가 조달 필요 판단
      → 공급처/Lead Time, Ocean vs Air → 발주 의사결정 지원
```

Target Vision은 **Recommendation까지**이며 실제 발주 실행은 향후 별도 확장
영역으로 둔다.

## 9. 참고 프로토타입 — vessel-tracker (실 AIS 연동)

- 위치: [`vessel-tracker/`](vessel-tracker/) — Node/Express + WebSocket 프록시 +
  Leaflet 지도(OSM, 키 불필요). aisstream.io API 키를 서버가 중계해 브라우저에
  노출하지 않는다.
- 화물 탭 목업의 선박 6척(ONE INNOVATION, MSC BRUNELLA, ONE COMMITMENT,
  HYUNDAI FAITH, CMA CGM AQUILA, MSC ISABELLA)은 MMSI 매핑 완료.
- **알려진 한계**: 한국 해역은 AIS 수신 커버리지가 없음(자원봉사자 지상 수신국
  기반 서비스 특성). 특정 MMSI 단일 필터링(`FiltersShipMMSI`)도 API 이슈로
  응답이 오지 않음.
- **채택 방식**: 커버리지 확인된 지역(도버 해협+싱가포르 해협)을 필터 없이
  구독해 실시간으로 신호를 보내는 임의 선박을 지도에 표시하는 "실시간 연결
  데모" 모드. 실제 서비스 적용 시 한국 해역 커버리지가 있는 유료 AIS API
  (MarineTraffic, VesselFinder, Spire 등) 검토 필요 — 본 프로토타입은 데모/
  검증 목적.

## 10. 미해결 이슈 / 의존성

| 영역 | 이슈 | 상태 |
|---|---|---|
| 화물 탭 | "리스크" 상태 판정 기준 | 미정 (환적 있음=리스크 아님, 노이즈 우려로 화면 미반영) |
| 화물 탭 | PTA 방법론 — 소스별(선사 milestone/AIS·예측 벤더 등) **과거 예측 정확도 이력** | 지연 사유 분석(§7.1)의 정적 신뢰도 산출에 그대로 필요한 데이터와 동일. 실 raw data(컨테이너 트래킹/선사 스케줄/항만 혼잡도)로 파일럿 착수, 이력 축적 방안은 별도 과제 |
| 업무 탭 | Item 단위 연결(CI/PL Item→부킹→B/L→컨테이너)에 필요한 적입/장입 확정 데이터(Stuffing List) | 대부분 Pantos 내부 시스템 연동 문제(부킹 시스템↔CFS/오퍼레이션 시스템↔게이트 기록), FCL 자가적입 시 고객 Packing List 필요 예외 존재. 데이터가 있다는 전제로 설계 진행 |
| 업무 탭 | Inland Routing 트럭/철도 스케줄 마스터 데이터 | 별도 마스터 데이터 등록 필요, 데이터가 있다는 전제로 설계 진행 |
| Inventory | On-hand 재고 데이터(W&D) 연동 방식 | 미정 |
| Inventory | Outbound 데이터 소스와 정확도(수요예측 vs 확정 출고계획 vs 평균값 등) | 소스 불문 "주어진 입력값"으로 설계 진행, 실제 소스 확정은 고객사별 데이터 확보 상황에 달림 |
| Inventory | In과 Out의 낙관/비관 방향을 맞출지 | 미정 — Outbound 소스가 그 정도 세분화된 값(예: P50/P95)을 주는지에 달려있음(§8.5) |
| Inventory | Safety Stock 데이터 정합성 | ERP/W&D 마스터 데이터 등록 여부에 의존, 미등록 Item 처리 방식은 §8.7 참고 |
| Inventory | "Items at Risk" 지표 정의 | 이번 버전에서는 제외(§8.7), 필요 시 추후 재정의 |
| Inventory | 실제 On-board 상태를 어떤 데이터 필드로 판정할지 | 미정 — 현재 샘플은 POL ATD 존재 여부로 판단 중 |
| Inventory | **입고버퍼시간의 구체적 일수**(§8.4) | 실입고일(W/H In Date) 데이터가 없는 경우 FDEST ATA/ETA에 며칠을 더할지 미확정. raw data 스냅샷엔 완료건(ATA 존재)이 0건이라 실측 검증 불가 상태(검증 이력은 PROGRESS.md) |
| Inventory | **POD 양하 시 Shortage 임박도 기반 우선순위 배정 로직**(§8.10 Next) | MVP 범위에서는 제외, Phase 2 이관 |
| Inventory | **선사 ETA 자체 보정 방법론**(§8.6) | MVP 범위에서는 제외 |
| Inventory | News 데이터의 실제 연결 방식 | 미정 — "이런 데이터가 있다면"이라는 가정 하 화면 컨셉만 정의 |
| Inventory | Port Congestion/Calling Schedule과 ETA 변화의 정량적 인과모델 | 미정 — §8.2 참고, 자동 단정하지 않는다는 원칙만 확정 |
| Inventory | Pre-carriage 데이터를 향후 Planning Projection에 포함하는 상세 규칙 | 미정 — §8.4 Confirmed/Planning Projection 분리 개념만 정의 |
| Inventory | 자체 ETA Prediction 모델, 실제 발주 의사결정 기능의 상세 구조 | 미정 — §8.10 Advanced/Target Vision 단계 과제 |
| Inventory | **재고관리 Agent의 필요 범위** | 단순 임계값 판단(발주 알림/중단)은 §8.5 판정 로직으로 충분, 룰 베이스면 됨. Port Congestion·News·ETA Confidence·Supply Pipeline을 종합해 발주를 권고하는 판단 영역만 Agent가 필요 — §8.10 Advanced/Target Vision과 겹치는 미착수 영역, 다음 세션에서 설계 시작 |
| 공통 | 선박 스케줄·컨테이너 트래킹·AIS·항만 혼잡도 그래프DB 연동 방식 | 상세 설계 안 됨 — "이런 데이터가 있다면"이라는 가정 하 최종 이미지만 정의 |
| 공통 | 대안 루트 추천용 비교 데이터(대안 스케줄, 실시간 선복, 운임, 탄소계수) | 데이터/제휴 확보 과제, 기능 설계 이전 단계 |
| Overview | 구성 방식(설계자 우선순위 선정 vs 사용자 커스터마이즈) | Transportation·Inventory 도메인 설계 완료 후 논의 |
| 공통 | AI Q&A (우측 하단 플로팅 아이콘 팝업) | 2026-08-05 세션에서 §6 IA에서 제외 — 질의 범위·응답 데이터·지연 사유 분석과의 관계 등 내용이 전혀 정의 안 돼 이름만 있는 상태였음. 필요성/범위 재검토 후 다시 넣을지 결정 |

## 11. 범위 제외 (Out of Scope)

- 수배송·창고 관리, WMS 운영 기능(Receiving/Picking/Putaway/Cycle Count)
- 철도/트럭 본선 운송(내륙운송/Inland Routing 제외)
- 고객 세그먼트별 화면 분기, 역할별(마케팅/물류담당 등) 화면 재구성
- 액션 처리시간(SLA) 측정
- 수요예측 모델 자체의 생성(플랫폼이 수요를 만들어내지 않음 — §8.4), 출고계획
  수립, 재고 최적화 엔진

## 12. 시장 벤치마크 (참고, 모방하지 않음)

- **Flexport**: 오더 중심 통합 타임라인. Allocation Management 기능은 원리는
  같으나, 담당 부서 선호로 채택하지 않고 §7.2 "스페이스 타이트 신호" 방식으로 대체.
- **C.H. Robinson**: 예외(Exception) 우선 노출 철학.
- **Freightos Terminal**: Booking Index/Supply Index의 등급+추세 표현 방식을
  스페이스 타이트 신호에 참고.
- 위 벤치마크는 참고 대상일 뿐, 독자적 조합(원인 추적 + 재고 연결 +
  Inland Routing)으로 차별화한다.

## 13. 진행 현황 (Status)

| 탭/영역 | 상태 | 산출물 |
|---|---|---|
| 화물 | 콘텐츠 모델 확정, 목업 리뷰 진행 중 | `visibility_control_tower_mockup.html` |
| 업무 | 콘텐츠 모델 확정, 목업 리뷰 진행 중 | `visibility_control_tower_mockup.html` |
| 비용 | 콘텐츠 모델 확정, 목업 리뷰 진행 중 | `visibility_control_tower_mockup.html` |
| Inventory | 콘텐츠 모델 확정(§8 실 raw data 검증 반영), 목업에 실 데이터 반영 완료, 리뷰 진행 중 | `visibility_control_tower_mockup.html`, `synthetic-data/` |
| Overview | 설계 착수 전(다른 탭 완료 후 진행) | — |
| vessel-tracker | 프로토타입 완료(데모 목적) | `vessel-tracker/` |

## 14. 다음 단계

1. `visibility_control_tower_mockup.html` 리뷰 계속 — 화물/업무/비용/재고 전 탭 화면/문구/
   인터랙션 피드백 반영 (원하는 탭부터).
2. 재고 탭 "재고 투영" Item 리스트 정렬 로직 정하기(현재는 데이터 순서 그대로).
3. §10에 정리된 Inventory 미확정 사항(입고버퍼 일수, POD 양하 우선순위,
   ETA 자체보정 등) 개발 착수 시 순서대로 확정.
4. Inventory Engine 실제 구현 착수 시 `synthetic-data/`를 입력으로 단위테스트
   작성(raw data 검증 이력은 PROGRESS.md 참고).
5. 화물/업무/비용/재고 탭이 다 정리되면 → 통합 Overview 재구성.
6. **재고관리 Agent 설계 — 다음 세션에서 새로 시작**(§10 "재고관리 Agent의
   필요 범위" 행 참고). 입력 신호(Port Congestion/News/ETA Confidence/
   Supply Pipeline)와 판단 로직·출력 형태를 처음부터 논의해야 함.
