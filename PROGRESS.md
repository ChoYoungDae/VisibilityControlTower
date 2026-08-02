# Pantos View — Visibility Control Tower · 진행 상황

마지막 갱신: 2026-08-02 (화물 탭 1차 마무리, 업무 탭으로 이동 예정)

새 대화 세션에서 이어갈 때는 이 파일을 먼저 읽으면 됩니다. 콘텐츠의 상세 근거는
[`PantosView_VisibilityControlTower_기획.md`](PantosView_VisibilityControlTower_기획.md)에 있습니다.

## 프로젝트 개요

Pantos View(포워딩 Visibility 서비스) 고객이 로그인 직후 보는 화면 —
**Visibility Control Tower**. "대시보드"라는 명칭은 쓰지 않는다.

## 지금까지 결정된 콘텐츠 (요약)

- **백본**: 고객 PO → 부킹 → 선적 → 트래킹(해상 주력+항공) → 하역 → Inland Routing → Final Destination
  - PO 확보 프로세스에서 Item/SKU 정보가 이미 들어오므로 별도 입력 요청 없이 Item 단위 트래킹 가능
- **3가지 관점(Lens)**
  - **화물**: 아래 "화물 탭 — 확정된 콘텐츠 모델" 참고 (기획서 §5.1보다 세부적으로 갱신됨)
  - **업무**: PO/부킹 진행, Cut-off 통합 타임라인(SI/VGM/게이트인), 항로별 스페이스 타이트 신호(계약 allocation 대신 Pantos 부킹 성공률 기반으로 대체 확정), Inland Routing(트럭/철도 비교 후 선택→실행) — **아직 화면 설계 시작 안 함**
  - **비용**: D&D(체화료), PCS(항만혼잡할증 — 선사 공지 크롤링으로 사전 알림, 성수기형+지정학 위기형 둘 다 발생) — **아직 화면 설계 시작 안 함**
- **AI의 역할**: 화면에 뜬 데이터에 답하는 수준을 넘어, 여러 데이터 소스가 상충할 때 이를 탐지하고 인과관계로 설명하는 분석가 역할
- **제외/보류한 것**: 수배송·창고, 철도/트럭(내륙운송 제외한 본선), 고객 세그먼트별 화면 분기, 액션 처리시간(SLA) 측정, 역할별(마케팅/물류담당 등) 화면 재구성(지금 단계에서는 안 함)

## 화물 탭 — 확정된 콘텐츠 모델

기획서 §5.1(위치/상태, 지연 계보, 확률적 ETA, 재고 투영)을 이번 세션에서 훨씬 구체화함.
`cargo_tab_mockup.html`이 이 모델을 반영한 최신 목업.

- **리스트 단위**: 해상=컨테이너(없으면 HBL), 항공=HBL. 컨테이너 번호는 11자리 붙여쓰기, 하이픈 없음(예: `TCLU5520134`).
- **해상/항공 배치**: 한 리스트로 섞지 않고, 같은 화면에 **순차 배치**(해상 섹션 → 항공 섹션). 상단 "Jump to Sea/Air" 버튼은 필터가 아니라 해당 섹션으로 스크롤 이동만 함. 상단 요약 통계는 해상+항공 합산과 모드별 분리를 같이 보여줌.
- **상태 3단계**: Pre-carriage / Main-carriage / On-carriage. 상태 탭을 바꾸면 컬럼 자체가 바뀜(행 필터링이 아니라 컬럼 구성이 다름):
  - Pre-carriage: 예정 Vessel/Flight, POL ETD, TS(예정)
  - Main-carriage: 현재 Vessel/Flight, 도착예정(POD) Vessel/Flight, TS, **Carrier ETA / PTA**
  - On-carriage: FDEST ETA, D&D LFD, TS(실적)
- **지연 유형**: 선적 지연 / 운송 지연 / 도착 지연으로 구간별 분리. 상단 요약과 각 섹션 모두 **Total / Delayed**를 같이 표기(Delayed는 빨간색).
- **TS(환적) 횟수**: 해상·항공 모든 단계에 칩으로 표기.
- **ETA/PTA 구분** (중요한 개념 정리):
  - **ETA** = 선사가 공지하는 값 그대로 (POL ETD, Carrier ETA 등)
  - **PTA(Predictive ETA)** = 그래프DB·AIS·항만혼잡도 + **과거 "예측 vs 실제 도착" 정확도 이력 데이터**를 결합해 자체적으로 예측한 값. **P50(중앙값)과 P95(보수적 기준선, percentile) 두 값으로 표현**하고, 근거 불명확한 임의의 "72%" 같은 단일 확률 수치는 쓰지 않음.
  - PTA는 **Main-carriage(국제운송 중) 구간에만 적용**. 선적전은 POL ETD, 하역후는 FDEST ETA가 기준.
  - **미해결 의존성**: PTA가 실제로 성립하려면 선사·항로·선박타입별 "과거 예측 정확도 이력" 데이터가 있어야 함 — 지금은 "데이터가 있다면"이라는 전제.
- **"리스크" 상태**: 기준 미정(환적 있음 = 리스크는 아님, 노이즈 너무 많음). **화면에 아직 반영 안 함** — 다음에 정의 필요.
- **최상단 컨트롤**: 좌측에 단위 토글(Container/HBL 기본 ↔ Item), 우측에 Search(B/L·Container·Item·PO No 통합 검색, 아직 동작 안 하는 UI만).
- **리스트 첫 컬럼 구조**: Container No(굵게) 아래 BL No, PO No를 서브라인으로 표기 (LCL/HBL 화물은 ID 자체가 BL이라 PO No만). 우측엔 더 이상 PO 컬럼을 중복 표기하지 않고 **POL → POD** 구간으로 대체.
- **지연 사유 분석** (구 "지연 계보/Delay Lineage" — 용어가 어색하다는 피드백으로 개명): 시각화 형태 **확정 — 그래프/체인형 하나만 사용**. 비교 후보였던 타임라인/스텝형은 탈락, 목업에서 제거함.
- **재고 투영 — Item 단위로 재설계** (컨테이너 단위 집계는 의미가 적다는 피드백 반영):
  - 컨테이너 상세의 Item 목록에는 "이 컨테이너분" 수량만 참고 표시, 클릭하면 **Item 단위 통합 뷰**로 이동
  - Item 단위 뷰(상단 Item 토글 클릭 → 드롭다운에서 SKU 선택): 그 Item이 포함된 **모든 화물**(해상+항공 통합, Pre-carriage 포함)을 리스트로 보여주고, 서로 다른 Item끼리는 합산하지 않음(수량 단위가 달라 의미 없음)
  - **FDEST ETA는 Pre-carriage를 제외한 Main-carriage·On-carriage 전 구간에서 내부적으로 계속 계산**되고 있어야 함(화면에 노출은 안 함, 집계에만 사용). Pre-carriage 화물은 아직 계산 근거가 너무 약해 리스트엔 나오되 "미정"으로 표시.
  - 일자별 재고 도착 현황은 **FDEST ETA의 P95(보수적 추정)** 기준으로 날짜별 입고량을 누적 표시. 미정 수량은 누적에서 제외하고 총 발주수량 대비 각주로 표기.
- **선박 위치 연동**: 선박명 클릭 → 실제 AIS 위치를 지도에 표시 (아래 "vessel-tracker" 참고). 항공 편명은 AIS 대상이 아니라 미연동.
- **폰트**: Pretendard(한글+영문 통일 폰트)를 CDN(`jsdelivr`)으로 로드하도록 수정 — 이전엔 CSS에 이름만 적혀 있고 실제 로드가 안 돼 시스템 폰트로 조용히 대체되고 있었음.

## vessel-tracker (실제 AIS 연동 프로토타입)

- 위치: [`vessel-tracker/`](vessel-tracker/) — Node/Express + WebSocket 프록시 + Leaflet 지도(OSM, 키 불필요)
- 목적: aisstream.io API 키를 브라우저에 노출하지 않고, 서버가 중계해서 실시간 선박 위치를 지도에 표시
- 실행: `cd vessel-tracker && npm start` (최초 1회만 `npm install`) → `http://localhost:8787`
  - **재부팅/터미널 종료 후에는 매번 다시 `npm start` 필요** — 상시 켜져 있는 서버가 아님
  - `.env`에 실제 API 키 보관(gitignore 대상). `.env.example`은 빈 템플릿만 커밋
- `cargo_tab_mockup.html`의 선박명 6개(ONE INNOVATION, MSC BRUNELLA, ONE COMMITMENT, HYUNDAI FAITH, CMA CGM AQUILA, MSC ISABELLA)는 실제 선박이라 MMSI 확인 후 매핑 완료. 클릭하면 vessel-tracker가 새 탭으로 열림.
- **버그 수정 이력**:
  1. 좌표 필드 케이싱 — `server.js`가 `MetaData.Latitude/Longitude`(대문자)에서 읽고 있었는데, 실제 aisstream.io 응답은 `MetaData`에 소문자(`latitude`/`longitude`)로 옴 → `Message.PositionReport.Latitude/Longitude`(항상 대문자로 옴)를 우선 사용하도록 수정.
  2. 프로세스 크래시 — 클라이언트가 track 요청을 연달아 보내면 이전 WebSocket의 `open` 콜백이 이미 null이 된 `upstream` 변수를 참조해 서버 전체가 죽는 race condition이 있었음 → 각 소켓 인스턴스를 로컬 `ws`로 클로저에 고정하고 `if (upstream !== ws) return;` 가드로 수정.
- **알려진 한계 (중요) 및 최종 아키텍처 결정**:
  1. `FiltersShipMMSI`(특정 선박 하나만 필터링)는 aisstream.io API 자체가 응답을 안 줌(바운딩박스를 좁혀도 동일) — API 이슈로 판단.
  2. **한국 해역은 AIS 수신 커버리지가 없음** — 부산·한국 전역 바운딩박스로 65초 이상 테스트해도 리포트 0건(메시지 타입 필터 없이도 0건). 자원봉사자 지상 수신국 기반 서비스라 한국에 수신국이 없는 것으로 추정. 아시아 전체 문제는 아님(싱가포르 해협은 25초에 14건 정상 수신).
  3. **최종 채택 방식 — "실시간 연결 데모" 모드**: 특정 MMSI를 기다리는 대신, 커버리지가 확인된 지역(도버 해협 + 싱가포르 해협)을 필터 없이 구독해서 **그 순간 실제로 신호를 보내는 아무 선박이나** 지도에 표시. 화물 목업에서 선박명을 클릭하면 "OO 선박의 실제 위치는 한국 해역이라 확인 불가 — 대신 실시간 연결 자체가 살아있음을 다른 실제 선박으로 보여줌"이라는 안내와 함께 이 모드가 뜸. 여러 척이 동시에 마커로 표시되고 "지금까지 N척 수신" 카운터로 살아있는 연결임을 확인시켜줌.
  4. 기존 "MMSI로 직접 조회" 수동 단일-선박 모드도 별도 버튼으로 남겨둠 (교재에서 요구한 개별 MMSI 조회 실습용).
  5. 이번 프로토타입은 **데모/검증 목적** — 실제 서비스에 넣으려면 한국 해역 커버리지가 있는 유료 AIS API(MarineTraffic, VesselFinder, Spire 등) 검토 필요.

## 지금까지 결정된 UI/구조 (Overview 전반)

- **탭 구조**: `Overview` + `화물` + `업무` + `비용` — Dashboard 대신 Control Tower 컨셉으로 요약→드릴다운
- **Overview 구성 방식(미정, 다음 논의 필요)**: 화물/업무/비용 탭을 각각 먼저 상세 설계한 뒤, 그중 중요한 항목을 뽑아 Overview를 재구성한다. 방식은 두 가지 후보 — (a) 설계자가 우선순위로 선정, (b) 사용자가 직접 선택. **아직 결정 안 됨.**
- **AI Q&A**: 상시 도킹 패널이 아니라 우측 하단 플로팅 아이콘 버튼 → 클릭 시 팝업. 탭 전환 시 해당 탭 범위 질의응답으로 전환
- **표기 규칙**: 모든 수치에 단위 표기, "총 N건 중 M건" 형태로 전체 대비 이슈 건수 표시 (화물 탭에선 Total/Delayed 형태로 구체화됨)
- **명칭/톤**: 제목줄에 "Pantos View" 노출 안 함(브랜드 마크 CI만), 고객사명에 "귀하" 등 존칭 표현 사용 안 함
- **화면 텍스트 언어 규칙 (프로젝트 공통, `CLAUDE.md`에 기록됨)**: 물류 업계 용어(Pre-carriage/Main-carriage/On-carriage, ETA/PTA/TS/D&D/LFD/MMSI 등)는 영어, 그 외 일반 설명·상태값·안내문은 한글. 상단 탭바(Overview/화물/업무/비용)는 기존 결정대로 한글 유지.

## 산출물 이력

1. `PantosView_고객대시보드_PRD.md` (구 버전, 1차 범위만 다룸) → 이후 통합 비전으로 전면 개정
2. `PantosView_VisibilityControlTower_기획.md` — 통합 비전 확정본 (화물 탭 세부는 위 "확정된 콘텐츠 모델" 섹션이 더 최신)
3. `control_tower_mockup.html` — 초기 화면 시안(폐기됨, 기록용으로만 보관, 참조하지 않음)
4. `cargo_tab_mockup.html` — **화물 탭 현재 작업 목업** (실제 리뷰/작업 기준 파일, 계속 이 파일을 갱신)
5. `vessel-tracker/` — 실제 AIS 연동 프로토타입 (위 설명 참고)

## Git

- `D:\AI_VisibilityControlTower`에 로컬 저장소 초기화 완료
- 최초 커밋(`94bb9a5`): 기획 문서 + 초기 목업
- `cargo_tab_mockup.html`, `vessel-tracker/`는 아직 커밋 안 됨 (사용자가 명시적으로 요청할 때 커밋)

## 다음 단계 (여기서부터 이어가면 됨)

**화물 탭 논의는 1차 마무리, 다음 세션은 업무 탭 설계로 넘어간다.** 화물 탭은 정적 목업(`cargo_tab_mockup.html`) 수준까지 구체화됐고, 아직 "실제 코드로 개발"(실 프론트엔드 구현) 단계로는 안 넘어감 — 이건 화물/업무/비용 다 설계된 뒤 한 번에 갈 수도 있고, 논의가 필요함.

**업무 탭 시작 방법**: 화물 탭 때와 동일한 순서로 — ① `PantosView_VisibilityControlTower_기획.md` §5.2(업무 관점)를 다시 리뷰 → ② 화면 구성 논의 → ③ 확정되면 목업(`business_tab_mockup.html` 같은 새 파일, 프로젝트 루트에 바로 생성)에 반영. 화물 탭에서 나온 언어 규칙(CLAUDE.md), Sea/Air 순차배치, Total/Delayed 표기 같은 패턴은 업무 탭에도 참고할 만함.

**화물 탭에 남아있는 미해결 항목** (나중에 돌아올 것):
1. **"리스크" 상태 정의** — 환적 있음=리스크는 아님. 어떤 조건이면 리스크로 볼지 아직 미정.
2. **PTA 방법론 문서화** — "과거 예측 정확도 이력 데이터 필요"라는 의존성을 기획서에도 반영할지 논의.
3. 화물/업무/비용 탭이 다 정리되면 → 마지막으로 **Overview 재구성** (기존 계획 유지).

새 세션에서는 이 파일을 먼저 읽고, "업무 탭 §5.2 리뷰부터 시작하자"고 이어가면 됩니다.
