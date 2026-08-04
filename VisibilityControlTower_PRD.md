# Visibility Control Tower PRD

- 작성일: 2026-08-03 (Inventory 도메인 추가·목업 반영: 2026-08-04)
- 버전: v1.2 (Inventory 도메인 목업 1차 반영)
- 근거 문서: [`VisibilityControlTower_기획.md`](VisibilityControlTower_기획.md), [`PROGRESS.md`](PROGRESS.md)
- 상태: 화물/업무/비용/재고 탭 모두 `visibility_control_tower_mockup.html`에 반영, 사용자 리뷰 진행 중

---

## 1. 개요

본 서비스는 고객의 국제운송·통관 화물 정보와 그로부터 파생되는 재고 정보를
통합 제공하는 Visibility 서비스다. 현재 고객이 로그인 직후 자신의 전체 화물
상황과 그것이 재고에 미치는 영향을 한눈에 파악할 통합 진입점이 없거나
파편화되어 있다.

이 문서는 그 진입점을 **"대시보드"가 아니라 Visibility Control Tower**로
정의하고, 제품 요구사항을 정리한다.

## 2. 문제 정의

- 고객은 화물이 지금 어디에 있는지는 알 수 있어도, **왜 그런 상태인지**(지연 원인),
  **앞으로 어떻게 될지**(확률적 ETA)를 한 화면에서 연결해 볼 수 없다.
- 업무(부킹/서류/Cut-off) 진행 상황과 비용(D&D, PCS) 리스크도 화물 상태와
  분리되어 있어, 담당자가 여러 화면·이메일·엑셀을 오가며 직접 종합해야 한다.
- W&D는 현재 재고(On-hand)는 관리하지만, 운송 중 재고(Inbound)까지 결합한
  **미래 재고(Projected Inventory)** 와 예상 Shortage를 Item 단위로 보여주지
  못한다. 담당자는 운송 상황과 재고 상황을 별도로 확인하고 머릿속에서
  직접 조합해야 한다.

## 3. 컨셉

> 고객의 화물이 지금 어디에 있고, 왜 그런 상태인지, 그래서 재고가 앞으로
> 어떻게 될지를 한 화면에서 판단하게 하는 관제탑(Control Tower). 단순 위치
> 조회가 아니라 **원인 추적 + 예측 + 재고 연결**까지 아우른다.

## 4. 대상 사용자

- 본 서비스를 이용하는 화주(고객사) 담당자, 로그인 계정 기준 단일 유형 고객군.
- 화물량·업종별 세분화된 페르소나나 역할별(마케팅/물류담당 등) 화면 분기는
  현재 범위에서 다루지 않는다.

## 5. 백본 구조 (Backbone)

```
고객 PO → 부킹 → 선적 → 트래킹(해상/항공) → 하역 → Inland Routing → Final Destination
                                                              ↓
                                                    W&D Inventory(On-hand)
```

- 출발점은 고객 PO 확보 프로세스. PO 안에 Item/SKU 정보가 이미 포함되어 있어,
  고객에게 별도 데이터 입력을 요구하지 않고도 Item/SKU 단위 트래킹이 가능하다.
- 운송 모드: 해상(주력) + 항공. 철도/트럭은 내륙구간(Inland Routing)에서만 다룬다.
- Final Destination 도착 이후 W&D의 On-hand 재고와 결합되면서, 같은 백본이
  Transportation(운송 운영) 관점과 Inventory(재고 계획) 관점 두 가지로
  갈라져 나간다 — §6 참고.

## 6. 정보 구조 (IA)

### 도메인 분리 원칙

같은 Supply Chain Event(PO→부킹→선적→트래킹→하역→Inland→Final Destination)를
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
- **AI Q&A**: 상시 도킹 패널이 아니라 우측 하단 플로팅 아이콘 → 클릭 시 팝업.
  탭 전환 시 해당 탭 범위 질의응답으로 전환.
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

### 7.1 화물 탭 — 어디에 있고, 왜 그런가

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
| On-carriage | FDEST ETA, D&D LFD, TS(실적) |

**지연 표시**
- 지연 유형을 선적 지연 / 운송 지연 / 도착 지연으로 구간별 분리.
- 상단 요약과 각 섹션 모두 Total/Delayed 병기(Delayed는 빨간색 강조).
- TS(환적) 횟수는 해상·항공 모든 단계에서 칩으로 표기.

**ETA / PTA**
- **ETA**: 선사가 공지하는 값 그대로(POL ETD, Carrier ETA 등).
- **PTA(Predictive ETA)**: 그래프DB·AIS·항만혼잡도 + 과거 "예측 vs 실제 도착"
  정확도 이력 데이터를 결합한 자체 예측값. **P50(중앙값)과 P95(보수적
  기준선) 두 값으로 표현**하며, 근거 불명확한 임의의 단일 확률 수치(예: "72%")는
  사용하지 않는다.
- PTA는 **Main-carriage 구간에만 적용**. 선적 전은 POL ETD, 하역 후는
  FDEST ETA가 기준.
- 의존성: 선사·항로·선박타입별 "과거 예측 정확도 이력" 데이터 확보 전제.
- Inventory 도메인이 Inbound 인식 시점을 계산할 때도 이 FDEST ETA(의 P95)를
  그대로 재사용한다 — §8.3 참고.

**지연 사유 분석** (구 "지연 계보도/Delay Lineage" — 명칭 변경)
- 시각화 형태: 그래프/체인형으로 확정(타임라인/스텝형은 탈락).
- 예: 컨테이너 지연 → 선박 3일 지연 → 부산항 접안 대기 → 항만 혼잡도 "높음".
- 환적 있는 경우: 환적선 스케줄 미확정 → 지연은 아니나 리스크로 표시(단,
  "리스크" 판정 기준 자체는 아직 미정 — §10 참고).
- AI 역할: 여러 소스가 상충할 때(선사 스케줄상 정상 vs AIS 위치는 뒤처짐)
  탐지하고, 그래프 상 인과관계를 근거로 원인을 설명. 단순 질의응답 챗봇이
  아니라 데이터 간 불일치를 잡아내는 분석가 역할.

**선박 위치 연동**
- 선박명 클릭 → 실제 AIS 위치를 지도에 표시(`vessel-tracker/` 프로토타입,
  §9 참고). 항공 편명은 AIS 대상이 아니라 미연동.

### 7.2 업무 탭 — 앞으로 잘 진행될 것인가 (신규 개척 영역)

**목적**: PO부터 부킹·서류·통관·Inland Routing까지 능동적 행정 액션(제출·승인·
결정)의 진행 상황을 추적하고 실행까지 연결한다.

**분류 기준**: 업무 탭 = 능동적 행정 액션, 화물 탭 = 그 결과로 발생하는 물리적
이동/위치. (예: 게이트인/On-board/공컨테이너 픽업은 화물 탭 소관, B/L 발급은
서류이므로 업무 탭 소관.)

**리스트 구조 — 2단**
1. **PO 리스트**(최상위, 입구 역할): PO No, Item/수량, 부킹 여부만 표시.
   부킹 이후 단계(Cut-off/통관/B/L)는 부킹 단위이므로 PO 행에 붙이지 않는다.
2. **부킹 리스트**: 부킹No, 연결 PO(들), 부킹 상태(요청/확정/롤오버), Cut-off
   (SI/VGM/CY 통합 카운트다운), 수출통관, B/L 발급.
- PO ↔ 부킹은 N:M 관계(콘솔리데이션 또는 분할선적 가능), 자동 1:1 전환 아님.

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
- **선적 준비**: PO → 부킹 → Cut-off → 수출통관 → B/L (Pre-carriage 시점).
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
  1. PO 리스트 행의 "스케줄 조회" 액션 — 해당 PO의 POL/POD 프리필, 결과에
     "이 스케줄로 부킹 요청" 액션이 붙어 그 PO에 연결됨.
  2. 업무 탭 상단 고정 진입점 — PO와 무관하게 독립 조회(부킹 요청 액션 없거나
     누르면 PO 선택 단계 추가).
- 입력: POL/POD/기간. 결과: 선사·선박·POL ETD·POD ETA·Lead Time·TS·탄소배출.
- 탄소배출 축은 §7.4 대안 루트 추천과 동일 축 재사용, 추후 연결.
- Overview 진입점 추가는 Overview 재구성 시점으로 보류.

### 7.3 비용 탭 — 돈이 새고 있거나 샐 위험이 있는가

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

### 8.1 도메인 모델

```
PO
 └── PO Line
      └── Item ──(Container-Item Mapping, N:M)── Container
           │
           ├── Commercial Invoice  (Item 검증)
           ├── Packing List        (Item ↔ Shipment 연결)
           ├── B/L                 (Item이 속한 선적 단위)
           └── W&D Inventory       (Item의 On-hand)
```

- Item은 W&D SKU와 동일한 관리 단위(Granularity)를 가지는 표준 Business Object.
- **Item ↔ Container는 N:M** — Container-Item Mapping이라는 별도 연결
  엔티티로 표현한다(§7.1의 Item 통합 뷰와 동일하게, 한 Item이 여러 Container·
  여러 화물에 걸쳐 존재할 수 있음).
- Container-Item Mapping이 없는 경우 §8.3의 정책에 따라 BL ETA로 보수적으로
  대체한다.

### 8.2 데이터 소스

| 구분 | 소스 | 비고 |
|---|---|---|
| On-hand | W&D | 특정 스냅샷 시점(예: 기준일 0시) 재고 |
| Inbound | Transportation | §7.1의 FDEST ETA(P95) 재사용, §8.3 참고 |
| Outbound | 고객 ERP/W&D (또는 그에 준하는 출고 계획 값) | §8.4 참고 — 소스를 특정 시스템으로 고정하지 않는다 |
| Safety Stock | 고객 ERP/W&D 마스터 데이터 | Item별 등록값, 미등록 Item은 강조 표시 대상에서 제외 |

플랫폼은 수요를 생성하지 않고, 위 입력 데이터를 이용해 미래 재고를 계산만 한다.

### 8.3 Inbound 인식 시점

| 조건 | 계산 방식 |
|---|---|
| Container-Item Mapping 존재 | Container의 **FDEST ETA(P95, 내륙운송 포함 최종 목적지 도착 기준)** |
| Container-Item Mapping 미존재 | 동일 B/L 내 Container 중 **가장 늦은 FDEST ETA** |

- POD(항만) 도착이 아니라 **Final Destination 도착**(내륙운송 리드타임 포함,
  §7.2 D-7~D-10 참고)을 기준으로 삼는다 — 재고가 실제로 "쓸 수 있는" 시점과
  일치시키기 위함.
- Container-Item Mapping이 없는 경우, 재고 과대 계산을 방지하기 위해
  보수적으로(더 늦은 값 쪽으로) 계산한다.
- Vessel Departure 이전(PO/Booking/Stuffing/Gate-In 단계)에는 Projected
  Inventory 계산을 시작하지 않고, 업무 진행 현황만 제공한다.

### 8.4 재고 계산

```
Projected Inventory(t) = On-hand(기준일) + Σ Inbound(≤t) − Σ Outbound(≤t)
```

- 일자별 누적 계산이며, 단일 스냅샷 값이 아니라 §8.5 Projection 타임라인 전체에
  걸쳐 계산된다.
- **Outbound은 소스를 특정 시스템에 고정하지 않는다** — 수요예측(Demand
  Forecast)이든 확정 출고계획(Outbound Plan)이든 평균 출고량 추정치든,
  고객 시스템에서 "주어지는 입력값"으로 취급한다. 어떤 값을 쓰든 Projected
  Inventory 정확도는 그 입력값의 정확도에 달려있다는 점을 화면에 명시한다.
  (Out의 값 성격에 따라 In(P95, 보수적)과 낙관/비관 방향을 맞출지는 §10
  미해결 이슈로 유지.)

### 8.5 화면 구성

**Projection**
- Item별 일자별 Inventory Timeline: `Date | On-hand | Inbound | Outbound | Projected`
- Safety Stock 이하 및 음수 재고를 강조 표시.
- **Shortage는 별도 탭이 아니라 이 화면의 필터 뷰**: Projected가 Safety Stock
  이하 또는 음수로 내려가는 Item만 걸러서 보여준다(표시 정보: Item, Shortage
  Date, Shortage Qty, Cause).

**Inbound**
- 표시 정보: Item, Qty, FDEST ETA, Delay Status.
- Drill-down: `Item → Inbound → B/L → Container → Transportation Tracking`
  (Transportation Tracking 클릭 시 §7.1 화물 탭의 해당 컨테이너로 이동).

**Item 상세** (Projection/Inbound에서 드릴다운, 별도 탭 아님)
- Current Inventory, Projected Inventory Timeline, Inbound Schedule,
  Shipment History, B/L, Container Tracking.

**Overview KPI** (§6의 통합 Overview에 포함될 후보)
- Current Inventory, Inbound Inventory, Projected Inventory, Shortage Items,
  Today's Expected Receiving.
- ~~Items at Risk~~: Shortage Items와 구분이 불명확해 이번 버전에서는 제외.
  "아직 Shortage는 아니지만 Safety Stock에 근접" 같은 별도 정의가 필요하면
  추후 추가.

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
| 화물 탭 | PTA 방법론(과거 예측 정확도 이력 데이터) | 데이터가 있다는 전제로 설계 진행, 실 확보 방안은 별도 과제 |
| 업무 탭 | Item 단위 연결(PO Item→부킹→B/L→컨테이너)에 필요한 적입/장입 확정 데이터(Stuffing List) | 대부분 Pantos 내부 시스템 연동 문제(부킹 시스템↔CFS/오퍼레이션 시스템↔게이트 기록), FCL 자가적입 시 고객 Packing List 필요 예외 존재. 데이터가 있다는 전제로 설계 진행 |
| 업무 탭 | Inland Routing 트럭/철도 스케줄 마스터 데이터 | 별도 마스터 데이터 등록 필요, 데이터가 있다는 전제로 설계 진행 |
| Inventory | On-hand 재고 데이터(W&D) 연동 방식 | 미정 |
| Inventory | Outbound 데이터 소스와 정확도(수요예측 vs 확정 출고계획 vs 평균값 등) | 소스 불문 "주어진 입력값"으로 설계 진행, 실제 소스 확정은 고객사별 데이터 확보 상황에 달림 |
| Inventory | In(P95, 보수적)과 Out의 낙관/비관 방향을 맞출지 | 미정 — Outbound 소스가 그 정도 세분화된 값(P50/P95 등)을 주는지에 달려있음 |
| Inventory | Safety Stock 데이터 정합성 | ERP/W&D 마스터 데이터 등록 여부에 의존, 미등록 Item 처리 방식은 §8.5 참고 |
| Inventory | "Items at Risk" 지표 정의 | 이번 버전에서는 제외(§8.5), 필요 시 추후 재정의 |
| 공통 | 선박 스케줄·컨테이너 트래킹·AIS·항만 혼잡도 그래프DB 연동 방식 | 상세 설계 안 됨 — "이런 데이터가 있다면"이라는 가정 하 최종 이미지만 정의 |
| 공통 | 대안 루트 추천용 비교 데이터(대안 스케줄, 실시간 선복, 운임, 탄소계수) | 데이터/제휴 확보 과제, 기능 설계 이전 단계 |
| Overview | 구성 방식(설계자 우선순위 선정 vs 사용자 커스터마이즈) | Transportation·Inventory 도메인 설계 완료 후 논의 |

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
| Inventory | 콘텐츠 모델 확정, 1차 목업 반영, 리뷰 진행 중 | `visibility_control_tower_mockup.html` |
| Overview | 설계 착수 전(다른 탭 완료 후 진행) | — |
| vessel-tracker | 프로토타입 완료(데모 목적) | `vessel-tracker/` |

## 14. 다음 단계

1. `visibility_control_tower_mockup.html` 리뷰 계속 — 화물/업무/비용/재고 전 탭 화면/문구/
   인터랙션 피드백 반영 (원하는 탭부터).
2. 재고 탭 "재고 투영" Item 리스트 정렬 로직 정하기(현재는 데이터 순서 그대로).
3. 화물/업무/비용/재고 탭이 다 정리되면 → 통합 Overview 재구성.
