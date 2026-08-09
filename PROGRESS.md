# Visibility Control Tower · 진행 상황

마지막 갱신: 2026-08-08 (같은 세션 이어서 — "재고 탭 Inbound 신뢰도 설명
Agent"를 프로토타입 검증 → 화면 텍스트/트리거 정책 확정 → **실제
`visibility_control_tower_mockup.html`에 구현까지 완료**(재고 탭 입고
예정 리스트에 등급 배지·리스크 포인트·근거 드릴다운, Shortage 자동분석
vs on-demand 구분). 이어서 **화면을 Full HD(1920×1080) 기준으로 확대
(zoom 1.25, 본문 폭 1500px)**하고 **상단 검색창을 복원**(B/L·Container
No·Item 검색 placeholder, mock 동작)까지 완료. 상세 경과는 아래 세션
기록 섹션 참고. **아직 커밋 안 됨.**

**세션 마지막에 나온 새 논의(다음 세션에서 이어갈 것)**: 사용자가 "그래프
DB에 올리면 더 정확해지지 않냐"고 질문 → 결론은 그래프DB 자체보다 **"합성
데이터가 아니라 더 폭넓은 실제 tracking data로 Inbound 신뢰도 파이프라인을
다시 검증해보자"**는 제안이었음(§8.6.1 파이프라인은 유지, 입력 데이터를
교체/확장). 사용자가 **완전히 새로운 tracking data를 제공할 예정** —
필요하면 그 안의 선박에 대한 CP_Vessel_List 정보, Port Congestion 연결,
뉴스 검색까지 같이 하자는 것. **다음 세션은 이 새 데이터를 받는 것부터
시작.** 목업의 itemCatalog(합성 On-hand/Outbound/Safety Stock)를 이걸로
교체할지는 아직 미정 — 사용자가 지난 질문에서 "일단 분석부터, 목업 반영은
그 다음"이라는 뉘앙스였으나 확정 답변 전에 세션이 끝남. **다음 세션 시작
시 이것부터 다시 확인**: (1) 새 데이터가 어떤 형태/경로로 오는지, (2) 이번
에도 프로토타입 스크립트로 분석만 먼저 할지 목업까지 반영할지.

**커밋 여부 미확인** — 이번 세션 변경분(`visibility_control_tower_
mockup.html`, `VisibilityControlTower_PRD.md`, 이 파일)을 커밋할지 아직
사용자에게 확답 못 받음. 다음 세션 시작 시 먼저 물어볼 것(CLAUDE.md 규칙
— 명시적 요청 시에만 커밋).

**그 외 남은 것** (위 새 논의보다 우선순위 낮음, 사용자와 상의 후 진행):
1. Item 상세의 "Inbound Schedule" 서브리스트에는 아직 근거/신뢰도
   드릴다운을 안 붙였음(§8.7상 필요, top-level Inbound 리스트에만 붙음).
2. 지금 구현은 목업 데이터의 Init ETA vs 현재 FDEST ETA 비교만 쓰는
   단순화 버전(패널에 "프로토타입" 캐비어트 문구로 명시) — 실제
   raw data 연동은 위 "새 데이터" 작업과 합쳐질 가능성.
3. §7.3(비용 탭)부터 PRD 리뷰 계속 — 아래 "다음 단계" 섹션 참고.

**화면 텍스트 구조/트리거 정책 확정 사항**(구현에 반영 완료):
1. `🟢/🟡 등급 배지 → 한 줄 결론 → 리스크 포인트(있으면 목록, 없으면
   "없음") → 근거`. CP_Vessel_List를 가리킬 땐 "실제 선박의 기항지 운항
   데이터"라는 표현 사용.
2. Shortage Item은 AI 분석 자동 실행(⚡), 그 외(Normal/Risk)는 "근거
   보기" 클릭 시 on-demand.
3. "당겨짐" 케이스는 원인을 추측하지 않고 "정상 변동 범위" 여부만 표시
   (목업에서는 실제 항로별 통계 계산 없이 문구로만 단순화).

새 대화 세션에서 이어갈 때는 이 파일을 먼저 읽으면 됩니다. 콘텐츠의 상세 근거는
[`VisibilityControlTower_기획.md`](VisibilityControlTower_기획.md)에 있습니다.

## 프로젝트 개요

포워딩 Visibility 서비스 고객이 로그인 직후 보는 화면 —
**Visibility Control Tower**. "대시보드"라는 명칭은 쓰지 않는다.

## 지금까지 결정된 콘텐츠 (요약)

- **백본**: 고객 PO → 부킹 → 선적 → 트래킹(해상 주력+항공) → 하역 → Inland Routing → Final Destination
  - PO 확보 프로세스에서 Item/SKU 정보가 이미 들어오므로 별도 입력 요청 없이 Item 단위 트래킹 가능
- **3가지 관점(Lens)**
  - **화물**: 아래 "화물 탭 — 확정된 콘텐츠 모델" 참고 (기획서 §5.1보다 세부적으로 갱신됨)
  - **업무**: PO/부킹 진행, Cut-off 통합 타임라인(SI/VGM/게이트인), 항로별 스페이스 타이트 신호(계약 allocation 대신 Pantos 부킹 성공률 기반으로 대체 확정), Inland Routing(트럭/철도 비교 후 선택→실행) — **아직 화면 설계 시작 안 함**
  - **비용**: 월별 물류비 현황(항목별+물동량 대비 추이) + D&D(체화료 — Free Time 임박/발생중 두 상태). PCS(항만혼잡할증)는 확정 항목에서 제외하고 후보로 재분류(아래 "비용 탭" 섹션 참고) — **아직 화면 설계 시작 안 함**
- **AI의 역할**: 화면에 뜬 데이터에 답하는 수준을 넘어, 여러 데이터 소스가 상충할 때 이를 탐지하고 인과관계로 설명하는 분석가 역할
- **제외/보류한 것**: 수배송·창고, 철도/트럭(내륙운송 제외한 본선), 고객 세그먼트별 화면 분기, 액션 처리시간(SLA) 측정, 역할별(마케팅/물류담당 등) 화면 재구성(지금 단계에서는 안 함)

## 화물 탭 — 확정된 콘텐츠 모델

기획서 §5.1(위치/상태, 지연 계보, 확률적 ETA, 재고 투영)을 이번 세션에서 훨씬 구체화함.
`visibility_control_tower_mockup.html`이 이 모델을 반영한 최신 목업.

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
  - **재고 부족 시뮬레이션 (신규, `visibility_control_tower_mockup.html` Item 통합 뷰에 반영 완료)**: 창고 탭을 새로 만드는 게 아니라 위 입고 누적(In)에 Onhand·Out을 얹은 확장. 공식: `투영재고(t) = Onhand + Σ In(≤t, P95 기준) − Σ Out(≤t)`. Out(예상출고량)은 **수요예측(Demand Forecast) 시스템 연동**을 전제로 함(사용자 결정). 투영재고가 0 밑으로 내려가는 첫 날짜를 "예상 재고 소진일"로 강조 표시. In=P95(보수적)와 Out의 비관성 방향을 맞출지(Out도 상단값 사용 시 "최악의 경우" 시나리오)는 미해결 — 상세는 기획서 §6.1 참고. **미해결 의존성**: 수요예측 시스템 연동 필요(PTA·Item연결·Inland 스케줄 마스터와 같은 "데이터가 있다는 전제" 패턴).
- **선박 위치 연동**: 선박명 클릭 → 실제 AIS 위치를 지도에 표시 (아래 "vessel-tracker" 참고). 항공 편명은 AIS 대상이 아니라 미연동.
- **폰트**: Pretendard(한글+영문 통일 폰트)를 CDN(`jsdelivr`)으로 로드하도록 수정 — 이전엔 CSS에 이름만 적혀 있고 실제 로드가 안 돼 시스템 폰트로 조용히 대체되고 있었음.
  - **버그 수정**: 숫자 전용 모노스페이스 클래스(`.num`, Consolas 등)에 "확정", "(이 컨테이너분)", "해당없음" 같은 한글 텍스트가 같이 섞여 들어가 있어서, 한글 글리프 없는 그 폰트가 시스템 폰트(굴림)로 조용히 대체되던 문제 발견·수정. 숫자만 `.num`으로 감싸고 한글은 분리. 앞으로 `.num` 클래스엔 순수 숫자/날짜/ID만 넣을 것.

## vessel-tracker (실제 AIS 연동 프로토타입)

- 위치: [`vessel-tracker/`](vessel-tracker/) — Node/Express + WebSocket 프록시 + Mapbox GL JS 지도
- 목적: 실시간 선박 위치 API 인증정보를 브라우저에 노출하지 않고, 서버가 중계해서 지도에 표시
- 실행: `cd vessel-tracker && npm start` (최초 1회만 `npm install`) → `http://localhost:8787`
  - **재부팅/터미널 종료 후에는 매번 다시 `npm start` 필요** — 상시 켜져 있는 서버가 아님
  - `.env`에 실제 계정정보 보관(gitignore 대상). `.env.example`은 빈 템플릿만 커밋
- `visibility_control_tower_mockup.html`의 선박명 6개(ONE INNOVATION, MSC BRUNELLA, ONE COMMITMENT, HYUNDAI FAITH, CMA CGM AQUILA, MSC ISABELLA)는 실제 선박이라 MMSI 확인 후 매핑 완료. 클릭하면 vessel-tracker가 새 탭으로 열림.

### 2026-08-06 세션 — API를 aisstream.io → SeaVantage(SVMP)로 교체

- **교체 사유**: aisstream.io는 한국 해역 AIS 수신 커버리지가 없어(자원봉사자 지상 수신국 기반) 국내 물류 서비스에 부적합 — 아래 "폐기된 aisstream.io 관련 이력" 참고. SeaVantage는 유료 상용 AIS 데이터 제공사라 한국 커버리지를 기대할 수 있음.
- **API 조사 경로 (다음 세션 참고용)**: 사용자가 준 Notion 링크 → `insight.seavantage.com/api` Swagger 문서 확인, 이 API의 `/ship/snapshot`은 파라미터가 아예 없이 전체 데이터를 반환해서 브라우저(Swagger UI)가 렌더링하다 멈출 정도로 응답이 컸음(사용자가 우려했고 실제로 확인됨) → 단일 선박 조회 전용 엔드포인트를 찾다가 **별도의, 더 잘 정리된 문서 사이트 `developer.seavantage.com`(Postman 기반, `svmp.seavantage.com/api/v1`)**을 발견 — 이쪽이 실제로 채택한 API. `insight.seavantage.com`과 `svmp.seavantage.com`은 서로 다른 SeaVantage API 두 벌이니 혼동 주의.
- **채택한 엔드포인트** (`svmp.seavantage.com/api/v1`, Basic Auth):
  1. `GET /ship/search?keyword=<MMSI/IMO/선명>` — 선박 메타정보 + `shipId`(UUID) 조회. 위치 정보는 없음.
  2. `GET /ship/snapshot/:shipId?dateTime=<ISO>&range=<정수>` — **그 배 하나만**의 최신 위치, 지역 제한 없이 전세계 어디든 조회 가능. `server.js`가 MMSI→shipId를 캐싱해두고 이 엔드포인트를 주기적으로(기본 15초) 폴링.
  - **미해결/미검증**: `/ship/snapshot/:shipId`의 `range` 파라미터 단위가 문서에 없음 — 분(minute)으로 가정하고 기본값 60 사용(`SEAVANTAGE_SNAPSHOT_RANGE` env로 조정 가능). 실제 계정으로 테스트해서 맞는지 확인 필요.
  - REST 폴링 방식이라 aisstream.io의 WebSocket push와 달리 실시간성이 폴링 주기(기본 15초)에 묶임.
  - `/ship/position/:fromDate/:toDate?lowerLeftLatitude=...`(기간+bounding box 내 선박들) 엔드포인트도 있지만, 단일 MMSI를 지역 제한 없이 바로 조회할 수 있어서 **채택 안 함** — 처음엔 이걸로 "한국 해역 실시간 트래픽 데모" 모드를 만들었다가, 지역 제한 자체가 aisstream.io 시절의 커버리지 문제를 우회하려던 것이었지 SeaVantage에는 필요 없다는 사용자 지적으로 코드에서 제거함.
- **환경변수 변경**: `AISSTREAM_API_KEY` 제거 → `SEAVANTAGE_USERNAME`/`SEAVANTAGE_PASSWORD`(Basic Auth) + `SEAVANTAGE_BASE_URL`(기본 `https://svmp.seavantage.com/api/v1`) + `SEAVANTAGE_SNAPSHOT_RANGE` 추가. `.env`는 아직 사용자가 실제 계정정보로 안 채운 상태 — 채운 뒤 `npm start`로 직접 테스트 필요(브라우저 프리뷰만으로는 계정정보를 다룰 수 없어 확인 못 함).
- **프런트엔드(`public/index.html`)도 단순화**: "실시간 트래픽 보기(지역 데모)" 버튼·fallback 15초 타이머·live 모드(복수 마커) 전부 제거하고, 항상 MMSI 하나를 직접 추적하는 단일 흐름으로 정리. `track`/`stop` 메시지 타입만 남음(`track-live`/`track-in-region` 삭제).

#### 폐기된 aisstream.io 관련 이력 (참고용, 더 이상 유효하지 않음)

- 좌표 필드 케이싱 버그, race condition 크래시 버그 등은 aisstream.io 전용 코드에 있던 것으로 이번 교체로 해당 코드 자체가 삭제됨.
- "한국 해역 커버리지 없음 → 도버해협/싱가포르해협 실시간 데모로 대체" 방식이었으나, SeaVantage는 지역 제한 없이 MMSI 직접 조회가 되므로 이 우회 자체가 통째로 불필요해짐.

## 업무 탭 — 논의 중인 콘텐츠 모델 (아직 목업 없음, 구조 논의 단계)

기획서 §5.2를 기준으로 화물 탭 설계 순서(리서치 병행)를 그대로 따라가는 중. 아직 화면(목업)으로는 안 옮김 — 구조/컬럼 논의 단계.

- **PO ↔ 부킹은 N:M 관계** — PO 여러 개가 컨테이너 하나로 콘솔리데이션되거나, PO 하나가 여러 부킹(분할선적)으로 쪼개질 수 있음. 자동 1:1 전환 아님.
- **리스트는 2단 구조로 확정**:
  1. **PO 리스트**(최상위, 입구 역할): PO No, Item/수량, **부킹 여부만** 표시. 부킹 이후 단계(Cut-off/통관/B/L)는 PO 행에 안 붙임 — 그건 부킹 단위이기 때문.
  2. **부킹 리스트**: 부킹No, 연결 PO(들), 부킹 상태(요청/확정/롤오버), Cut-off(SI/VGM/CY 통합 카운트다운), 수출통관, B/L 발급 — 실제 프로세스 진행 상황은 전부 여기 담김.
- **부킹 상태 정정**: 롤오버 = "확정 안 된 대기 상태"가 아니라 **이미 확정된 부킹이 선사 사정(스페이스 부족·blank sailing 등)으로 다음 항차로 밀려나는 예외 이벤트**. 순서: 요청 → 확정 → (예외) 롤오버 → 재확정 → …
- **Cut-off(SI/VGM/CY)는 부킹 단위**(=같은 sailing에 걸린 화물 전체에 동일 시각 적용). VGM만 그 안에서 컨테이너별 개별 제출 필요("VGM 3/5 제출완료" 식 진행률로 표현). 롤오버 발생 시 그 부킹의 cut-off 세트 전체가 새 sailing 기준으로 리셋됨 — 화면에 표시 필요.
- **게이트인/On-board/공컨테이너 픽업 = 화물 탭 소관** (Pre-carriage에서 이미 물리적 이동으로 추적 중). 업무 탭에서 중복 표시하지 않음. 판단 기준: **업무 탭 = 능동적 행정 액션(제출·승인·결정), 화물 탭 = 그 결과로 발생하는 물리적 이동/위치**.
- **B/L 발급은 업무 탭 소관** — 서류이지 물리적 이동이 아니므로. (On-board 이후에 나온다고 단순화했던 건 정정 — 시점보다 "성격이 행정 액션"이라는 게 분류 기준.) 화물 탭 리스트의 "BL No"는 식별 라벨로만 유지, 발급 여부/시점 추적은 업무 탭이 담당.
- **통관 2곳 추가** (기존 §5.2에 빠져있던 항목): 수출통관(선적 준비 섹션, 부킹 리스트에 포함) / 수입통관(도착 준비 섹션, Inland Routing 실행의 전제조건이라 그보다 앞서 배치·의존관계로 표현).
- **섹션 2분할 확정**: "선적 준비"(PO→부킹→Cut-off→수출통관→B/L, 전부 Pre-carriage 시점) / "도착 준비"(수입통관→Inland Routing, Main-carriage 후반~On-carriage 시점). 하나의 시간순 리스트로 억지로 안 잇고 성격별 섹션으로 분리.
- **스페이스 타이트 신호 — 업계 리서치 반영**: Freightos Terminal의 Booking Index/Supply Index 사례처럼 절대 수치가 아니라 **등급(원활~매우타이트) + 추세 화살표**로 표현하는 쪽으로 방향 확정. 정밀 퍼센트 수치는 화물 탭 PTA 때와 같은 이유로 지양.
- **Inland Routing 리드타임 — 업계 리서치 반영**: 드레이지(트럭) 기준 POD 도착 5~7일 전 예약 권장, 철도는 스케줄 고정이라 더 이른 시점(7~10일+) 필요할 수 있음. 화면상 POD ETA 기준 D-7 트리거로 "도착 준비" 섹션이 활성화되는 방식 제안.
- **미해결 의존성 (신규, PTA와 같은 성격)**: **Item 단위 연결(PO Item 수량 → 부킹 → B/L → 컨테이너)이 성립하려면 적입/장입 확정 데이터(Stuffing List/Loading Plan)가 있어야 함.** 이건 대부분 **고객 제공이 아니라 Pantos 내부 시스템 연동 문제**(부킹 시스템 ↔ CFS/오퍼레이션 시스템 ↔ 게이트 기록이 서로 이어져 있어야 함) — 단, FCL을 고객이 직접 자가적입(Shipper's Own Stuffing)하는 경우엔 고객이 Packing List를 제공해야 하는 예외가 있음. **PTA와 동일하게 "데이터가 있다는 전제 하에" 설계는 계속 진행**하기로 함. 화물 탭의 "Item 단위 통합 뷰"도 이 데이터가 있어야 실제로 성립 — 두 탭이 공유하는 의존성.
- **스케줄 조회 — 별도 화면(컴포넌트), 진입점 2곳으로 확정**: Port-to-Port 조회 화면 하나(입력: POL/POD/기간, 결과: 선사·선박·POL ETD·POD ETA·Lead Time·TS·탄소배출)를 두 경로에서 재사용.
  1. **PO 리스트 행의 "스케줄 조회" 액션** — 그 PO의 POL/POD가 프리필된 채 열리고, 결과 리스트에 "이 스케줄로 부킹 요청" 액션이 붙어 그 PO에 연결됨.
  2. **업무 탭 상단 고정 진입점** — PO와 무관하게 언제든 독립 조회 가능(부킹 요청 액션 없거나, 누르면 PO 선택 단계 추가).
  - Overview에 진입점 추가하는 건 Overview 재구성 시점으로 보류(후보로만 기록).
  - 탄소배출 축은 기획서 §7 "대안 루트 추천"과 동일 축 재사용 — 나중에 그 기능과 자연스럽게 연결됨.
- **"도착 준비" 섹션 확정 — 화물 탭과 같은 데이터, 다른 렌즈**:
  - **리스트 단위**: 컨테이너 우선, LCL/항공은 HBL — 화물 탭과 완전히 같은 단위.
  - **별도 데이터가 아니라 같은 컨테이너/HBL 레코드의 필터+액션 뷰**: 화물 탭은 상태 3단계 전체를 "위치/일정" 관점으로, 업무 탭 도착 준비는 그중 POD ETA 임박한 것만 걸러 "통관 여부·Inland Routing 실행" 액션 관점으로 재구성. 화물 탭에 이미 있는 FDEST ETA/D&D LFD는 중복 표시 안 하고, 통관상태·Inland Routing처럼 화물 탭에 없는 컬럼만 추가.
  - **노출 기간**: 기본값은 넉넉하게(예: POD ETA 기준 D-14 이내, 철도의 더 이른 리드타임까지 커버) 노출하고, 사용자가 기간을 좁혀볼 수 있는 필터 제공.
  - **수입통관은 화물마다 필수 여부가 다름** — "통관 필요여부/상태" 플래그(해당없음/진행중/완료) 컬럼 필요. 필요한 화물만 통관 미완료 시 Inland Routing 액션이 잠기는 의존관계.
  - **역방향 연동**: 업무 탭에서 Inland Routing 실행(트럭/철도 선택)하면, 그 결과가 화물 탭의 FDEST ETA 재계산 입력값으로 들어감 — 같은 레코드라 별도 동기화 없이 즉시 반영되는 구조.
  - **신규 미해결 의존성**: Inland Routing 옵션 비교(리드타임/비용/프리타임)가 성립하려면 **트럭/철도 스케줄 마스터 데이터**가 시스템에 등록되어 있어야 함(선박 스케줄처럼 별도 마스터 데이터 필요). PTA·Item연결과 같은 패턴 — "데이터가 있다는 전제"로 설계 계속 진행.

## 비용 탭 — 논의 중인 콘텐츠 모델 (아직 목업 없음, 구조 논의 단계)

기획서 §5.3 참고. 화물/업무 탭과 같은 순서(콘텐츠 모델 확정 → 목업)로 진행 중.

- **월별 물류비 현황 (신규 확정)**: 항목별(운임/D&D/기타) 구성 + **물동량 대비 비용 추이** 비교. "현재 발생분/추이"를 보는 현황형 콘텐츠.
- **D&D(체화료) — 사전 알림형 콘텐츠**: 월별 현황과 성격이 다름(예정/진행중 상태 알림). **Free Time 임박과 체화료
  발생중을 하나의 리스트로 통합**(신규 확정) — 별도 리스트 두 개로 안 쪼개고, 리스크 진행 순서(임박 → 1주 → 2주 →
  3주 → 4주 이상)로 한 화면에 표시:
  - 임박(발생 전, D-day 카운트다운) — 아직 비용 없음
  - 체화료 발생중 — **경과 주 단위 구간**: 1주 이내 / 2주 이내 / 3주 이내 / 4주 이상.
    구간이 길어질수록 리스크가 커지므로 4주 이상 구간은 강조 표시.
  - `visibility_control_tower_mockup.html`에 반영 완료(아래 "산출물 이력" 참고).
- **PCS(항만혼잡할증) — 확정 항목에서 제외, 후보로 재분류**: 이유 두 가지 —
  1. 선사 공지가 비정형·선사별 상이해서 크롤링 구현·유지보수 부담이 만만치 않음
  2. 상시 비용이 아니라 특정 항로·시기에만 터지는 이벤트성 비용이라 대부분 고객·달엔 해당 없음
  → 전용 알림/카드 없이, 발생 시 월별 물류비 현황의 항목 중 하나로만 반영.
- 그 외(할증료 일반, 서류오류 정정료, 롤오버 간접비용, CFS 보관료, FX)는 여전히 후보 상태(우선순위 근거 부족).

## 지금까지 결정된 UI/구조 (Overview 전반)

- **탭 구조**: `Overview` + `화물` + `업무` + `비용` — Dashboard 대신 Control Tower 컨셉으로 요약→드릴다운
- **Overview 구성 방식(미정, 다음 논의 필요)**: 화물/업무/비용 탭을 각각 먼저 상세 설계한 뒤, 그중 중요한 항목을 뽑아 Overview를 재구성한다. 방식은 두 가지 후보 — (a) 설계자가 우선순위로 선정, (b) 사용자가 직접 선택. **아직 결정 안 됨.**
- **AI Q&A**: 상시 도킹 패널이 아니라 우측 하단 플로팅 아이콘 버튼 → 클릭 시 팝업. 탭 전환 시 해당 탭 범위 질의응답으로 전환
- **표기 규칙**: 모든 수치에 단위 표기, "총 N건 중 M건" 형태로 전체 대비 이슈 건수 표시 (화물 탭에선 Total/Delayed 형태로 구체화됨)
- **명칭/톤**: 제목줄에 실제 서비스 **브랜드명**은 노출 안 함(브랜드 마크 CI만) — 단 "Visibility Control Tower"처럼 **컨셉/제품 성격을 나타내는 이름**은 이 규칙 대상이 아님, 브랜드 마크 옆에 텍스트로 노출하기로 확정(`visibility_control_tower_mockup.html`, `visibility_control_tower_mockup.html` 상단 topnav에 반영 완료). 고객사명에 "귀하" 등 존칭 표현 사용 안 함
- **화면 텍스트 언어 규칙 (프로젝트 공통, `CLAUDE.md`에 기록됨)**: 물류 업계 용어(Pre-carriage/Main-carriage/On-carriage, ETA/PTA/TS/D&D/LFD/MMSI 등)는 영어, 그 외 일반 설명·상태값·안내문은 한글. 상단 탭바(Overview/화물/업무/비용)는 기존 결정대로 한글 유지.

## 산출물 이력

1. `고객대시보드_PRD.md` (구 버전, 1차 범위만 다룸) → 이후 통합 비전으로 전면 개정
2. `VisibilityControlTower_기획.md` — 통합 비전 확정본 (화물 탭 세부는 위 "확정된 콘텐츠 모델" 섹션이 더 최신)
3. `control_tower_mockup.html` — 초기 화면 시안. 더는 참조하지 않는 폐기 목업이라 저장소에서 삭제함(과거 커밋 히스토리에서만 확인 가능).
4. `vessel-tracker/` — 실제 AIS 연동 프로토타입 (위 설명 참고)
5. `visibility_control_tower_mockup.html` — **현재 유일한 작업 목업 파일, 화물+업무+비용 통합 (신규 확정)**. 원래 화물/업무/비용 탭을 각각 별도 파일(`cargo_tab_mockup.html`/`operation_tab_mockup.html`/`cost_tab_mockup.html`)로 만들었다가, 이번 세션에 하나의 HTML로 합치면서 그 3개 파일은 삭제하고 `control_tower_unified_mockup.html`이라는 중간 이름을 거쳐 최종적으로 이 이름으로 확정함.
   - 상단 topnav/tabs가 실제로 클릭 전환되게 만듦(Overview는 아직 placeholder), 각 탭 콘텐츠는 `.tab-panel`로 감싸 표시/숨김.
   - CSS는 3개 파일에 중복되던 공통 컴포넌트(topnav, summary/stat, list/pill, detail, subblock 등)를 한 번만 정의하도록 정리.
   - **JS 통합 시 주의한 점**: 세 파일이 각각 `.jump-btn`, `.stat[data-jump]`, `selectedRow`, `showToast` 같은 클래스/변수명을 독립적으로 재사용하고 있어서, 단순 결합 시 한 탭의 클릭이 다른 탭 요소까지 잘못 건드리는 충돌이 있었음 — 각 탭 스크립트를 IIFE로 스코프 분리하고 `document.querySelectorAll` 호출을 각 탭 루트 요소(`#tab-cargo`/`#tab-operation`/`#tab-cost`) 기준으로 스코프 지정해서 해결. FAB·toast는 탭과 무관하게 앱 전역에서 공유(탭 이동 시에도 유지).
   - 화물 탭: 리스트/상태/PTA/재고 부족 시뮬레이션 등 위 "화물 탭 — 확정된 콘텐츠 모델" 섹션 전체 반영.
   - 업무 탭: PO 2단 리스트, Cut-off 카운트다운, 스페이스 신호, 도착 준비, Port-to-Port 스케줄 조회 등 위 "업무 탭 — 논의 중인 콘텐츠 모델" 섹션 전체 반영.
   - 비용 탭: 월별 물류비 현황(스택 바 차트+물동량 라인 오버레이+breakdown 테이블), 체화료(D&D) 통합 리스트(임박→1주→2주→3주→4주 이상) 등 위 "비용 탭" 섹션 전체 반영.
   - 브라우저로 3개 탭 전환 + 각 탭의 클릭 인터랙션(상세 패널, 스케줄 조회, jump 버튼) 모두 확인 완료, 콘솔 에러 없음.

## Git

- `D:\AI_VisibilityControlTower`에 로컬 저장소 초기화 완료
- 최초 커밋(`94bb9a5`): 기획 문서 + 초기 목업
- `visibility_control_tower_mockup.html`, `vessel-tracker/`는 아직 커밋 안 됨 (사용자가 명시적으로 요청할 때 커밋)

## Inventory 도메인 신설 (2026-08-04 세션, 신규 확정)

기존에는 재고 투영이 **화물 탭 안의 Item 통합 뷰** 기능이었으나, 이번 세션에서
**Transportation과 나란한 별도 최상위 도메인 Inventory**로 분리하기로 확정.
`VisibilityControlTower_PRD.md` §6/§8에 전체 반영 완료 — 상세 근거는 그 문서 참고.

- **도메인 분리 원칙**: Transportation = 컨테이너/B/L 단위(운송 운영), Inventory = Item 단위(재고 계획). 같은 이벤트를 다른 집계 단위로 재사용, 데이터 파이프라인은 안 바뀜.
- **IA 2단 구조**: Overview(Transportation+Inventory 통합, 도메인별 개별 Overview는 없음) → Transportation(화물/업무/비용) / Inventory(Projection/Inbound + Item 드릴다운). Shortage는 별도 탭이 아니라 Projection의 필터 뷰로 흡수.
- **Inbound 인식 시점**: POD Container ETA가 아니라 **FDEST ETA(P95, 내륙운송 포함 최종 목적지 도착 기준)** — 화물 탭에서 이미 확정한 PTA/FDEST ETA 개념을 그대로 재사용.
- **Outbound 데이터**: 특정 시스템(수요예측/ERP Outbound Plan 등)에 고정하지 않고 "고객 시스템에서 주어지는 입력값"으로 일반화.
- 화물 탭의 기존 "재고 투영(Item 단위)" 서브섹션(위 "화물 탭 — 확정된 콘텐츠 모델" 문단들)은 **Inventory 도메인으로 이관됨** — 화물 탭에는 더 이상 Item 토글/재고 부족 시뮬레이션을 두지 않음.
- **하위 탭 한글 명칭 확정**: `Projection`/`Inbound`는 업계 관용 영어가 아니라고 판단해 **"재고 투영" / "입고 예정"**으로 확정(화면 텍스트 언어 규칙 적용). 최상위 탭명은 "Inventory"가 아니라 기존 화물/업무/비용과 톤을 맞춰 **"재고"**로 확정.

## `visibility_control_tower_mockup.html` — 재고 탭 반영 완료 (2026-08-04)

Inventory 도메인을 실제 목업에 반영함. 상단 탭바에 `Overview | 화물 | 업무 | 비용 | (구분선) | 재고` 구조 추가(플랫 탭바 유지, "재고"만 시각적 구분선으로 살짝 분리 — Transportation 산하 3탭과 Inventory를 완전히 별도 2단 내비게이션으로 만들지는 않음, 목업 단순화).

- **화물 탭**: Item 토글/Item 통합 뷰(재고 부족 시뮬레이션 포함) 완전 제거. 컨트롤바는 Container/HBL 리스트 안내 문구만 남기고, 컨테이너 상세의 "Item / SKU" 블록은 "재고 투영에서 보기 ›" 링크로 재고 탭에 연결.
- **재고 탭 — 재고 투영**: Item 리스트(On-hand / Inbound 합계·Safety Stock / 상태뱃지, Shortage 임박 순 아님 — 현재는 데이터 순, 정렬 로직은 추후 다듬을 것) → 클릭 시 Item 상세로 이동. Item 상세는 `Projected(t) = On-hand + Σ Inbound(≤t, FDEST ETA P95) − Σ Outbound(≤t)` 공식 그대로 계산한 Projected Inventory Timeline을 표로 보여주고, **Safety Stock 이하(주의, 노랑)와 0 미만(Shortage, 빨강) 2단계로 색 구분**(사용자 확정 사항 반영). Inbound Schedule 서브리스트에서 화물 클릭 시 화물 탭의 해당 컨테이너로 드릴다운(Item → Inbound → B/L → Container → Transportation Tracking).
- **재고 탭 — 입고 예정**: Item×입고건 단위 리스트(Item, Qty, FDEST ETA P95/P50, Delay Status), FDEST ETA 기준 정렬. 클릭 시 화물 탭 드릴다운은 재고 투영과 동일 로직 재사용.
- **드릴다운 왕복 확인 완료**: 화물 탭 컨테이너 상세 → 재고 투영 Item 상세, 재고 투영/입고예정 → 화물 탭 컨테이너 상세, 양방향 모두 브라우저로 테스트 완료(콘솔 에러 없음). 상태 탭(Pre/Main/On-carriage) 자동 전환까지 확인.
- **Mock 데이터**: 기존 화물 탭에 있던 itemCatalog 3종(SKU-8841-BLK/8842-BLK/9010-GRY)을 재고 탭으로 옮기고 `safetyStock`, `delayed` 필드 추가. 손으로 계산한 결과와 화면 렌더링 결과 일치 확인(SKU-8841=Shortage 8/04, SKU-8842=정상, SKU-9010=Safety Stock 이하 7/29) — 세 가지 상태(정상/주의/Shortage)를 모두 보여주도록 의도적으로 구성한 예시 데이터.
- **아직 안 한 것**: Overview 재구성(재고 탭 KPI를 Overview에 반영하는 작업), 재고 투영 Item 리스트의 정렬 로직(현재는 데이터 순서 그대로 — Shortage 임박 순 정렬이 아님).

## `visibility_control_tower_mockup.html` — 1차 리뷰 피드백 반영 (2026-08-04, 같은 세션 이어서)

재고 탭 1차 반영 직후, 사용자가 화면을 직접 보며 준 피드백을 그 자리에서 반영함.

- **상단 topnav 틀고정(sticky)**: 스크롤해도 topnav(탭바+검색)가 상단에 고정되도록 `position:sticky; top:0` 적용.
- **탭 그룹 구분선**: `Overview | (구분선) | 화물 업무 비용 | (구분선) | 재고` — Overview와 Transportation 3탭, 그리고 재고(Inventory)를 시각적으로 구분. (중간에 한 번 "구분선 없애 달라"로 오해해서 지웠다가, 사용자가 "Overview와 화물 사이에도 넣어달라는 거였다"고 정정 — 다시 추가함. 구분선 요청은 "없애기"가 아니라 "위치 추가"였다는 점 주의.)
- **화물 탭 Pre-carriage 컬럼 변경**: TS 컬럼 제거, 그 자리에 **Initial POL ETD**를 POL ETD 앞에 추가해서 최초 예정 대비 지연 여부를 비교(지연 시 POL ETD 셀에 "+N일 지연" 빨간 텍스트로 표시). 해상·항공 Pre-carriage 섹션 둘 다 적용.
- **날짜 현실화**: 위 Pre-carriage 예시 날짜가 9월로 되어 있던 것을 현재 시점(2026-08) 기준 8월로 수정(Initial POL ETD 8/13, POL ETD 8/13 정상 / 8/13→8/16 +3일 지연 예시).
- **재고 탭 "Projected Inventory Timeline"을 표에서 차트로 전환**: 가로축=날짜, 세로축=Inbound(양수)/Outbound(음수)를 **하나의 공유 스케일**로 표현하는 다이버징 바 차트 + Projected 잔량 추세선(꺾은선) 오버레이. 상세 수치 표는 차트 아래에 보조 자료로 유지.
  - Safety Stock 기준선(노란 점선), Projected가 0 밑으로 가면 Shortage로 자동 강조(빨간 점).
  - 같은 날짜에 Inbound/Outbound가 동시에 있는 사례를 mock 데이터에 추가(SKU-8841-BLK, 8/05에 입고 1,200 + 출고 150 동시 발생) — 그 날짜의 두 막대와 Projected 점이 **같은 x축 위치(같은 열)에 정렬**되도록 좌우 오프셋을 없앰.
  - 막대·점에 네이티브 `<title>` 툴팁 추가 + hover 시 막대 진하게/점 커지는 인터랙션 추가 — "이미지처럼 안 움직인다"는 피드백에 대응(차트 라이브러리 없이도 순수 SVG로 인터랙션 가능하다는 점 확인시켜줌).
  - 색상은 처음엔 원색(진한 초록/빨강/파랑 3색 경쟁)이라 "안 깔끔하다"는 피드백 → 막대는 `fill-opacity` 낮춰 톤 다운, 추세선/기본 점은 회색조(`--ink-muted`)로 바꾸고 warn/crit 상태일 때만 색(노랑/빨강)이 튀도록 정리.
  - 막대 두께 20% 축소, 모서리 각짐(rounded corner 제거, `rx` 속성 삭제)으로 마무리.

## 2026-08-05 세션 — PRD 재정의(개요~7.2) + 목업 반영

`VisibilityControlTower_PRD.md`를 처음부터(§1) 사용자와 함께 문장 단위로 리뷰하며
여러 구조적 결정을 새로 내림. 아래는 그 결과이자 최신 상태 — 이전 세션 기록(§8
Inventory 도메인 신설 등)과 배치되는 부분은 이 섹션이 우선한다.

- **§1 개요**: "재고 정보가 화물 정보로부터 파생된다"는 표현 정정 — 재고는
  Transportation·W&D 등 **서로 다른 소스를 결합**한 것이지 화물 정보의 파생물이
  아님(근거: §8.4 재고 계산식 `On-hand + Inbound − Outbound`, Inbound만
  Transportation 유래).
- **§2 문제 정의**: "화물이 어디 있는지는 안다"는 전제가 비현실적이라는 지적 반영
  — 위치 파악 자체가 간접 추정(AIS 등)이라 불확실하고 항만 운영 역량·정보
  비공개에 좌우된다는 점을 명시. 비용 예시는 "D&D, PCS" → "D&D 등"으로 단순화.
- **§3 컨셉**: 화물 상태에 국한하지 않고 업무·비용까지 아우르며, 운송 단위
  (컨테이너/B/L) 가시성을 고객이 실제 관심 있는 **Item/SKU 단위**로 변환해
  Transportation·W&D를 잇는다는 방향으로 재작성.
- **§4 대상 사용자**: 단일 유형 고객군·화면 미분기 원칙은 유지하되, "화물/업무/
  비용은 물류·수출입 운영 담당자에게, 재고는 Demand Planner·자재·구매 계획
  담당자에게 더 직접적으로 도움될 것"이라는 참고 설명(화면 분기 근거 아님) 추가.
- **PO → CI/PL 전환 (핵심 결정)**: 포워더가 화주로부터 PO를 직접 받는 경우는
  현실적으로 드묾(상업기밀·화주-공급업체 간 문서라 포워더가 당사자 아님).
  Item/SKU 정보 소스를 **PO에서 CI/PL로 전환**. 트레이드오프: Item 단위
  가시성 시작 시점이 "부킹 이전"에서 "부킹 이후·선적 준비(CI/PL 확보) 시점"으로
  늦춰짐. §5 백본 다이어그램 시작점을 "부킹 → 선적 준비(CI/PL 확보) → ..."로
  수정.
- **§7.2 업무 탭 구조 변경**: 위 전환에 따라 "PO 리스트(최상위)+부킹 리스트"
  2단 구조를 **부킹 리스트 단일 최상위**로 재구성. PO No는 CI/PL에 찍힌
  참조번호로 부킹 행에 참고 표시만(별도 엔티티 추적 안 함). Item/수량은 부킹
  시점엔 "미확정", 수출통관 준비(CI/PL 확보) 시 채워짐. Port-to-Port 스케줄
  조회 진입점도 "PO 행 프리필" → "기존 부킹 재조회(롤오버 등)"로 변경.
  **§8.1 Inventory 도메인 모델의 `PO→PO Line→Item` 트리는 아직 이 전환을
  반영 안 함 — §8 리뷰 시 처리 필요.**
- **지연 사유 분석 목적 재정의 (§7.1)**: "지연 원인을 서술하는 것"이 목표가
  아니라, 화물 도착일(FDEST ETA)을 알려주는 **여러 소스가 상충할 때 이번 건은
  어느 소스를 더 신뢰할지 판단하는 정황 증거 수집**이 실제 역할. 2단 구조 —
  ① 소스별 과거 정확도 이력 기반 정적 신뢰도(통계, AI 불필요), ② 건별 상충
  시 항만혼잡도·뉴스 등 독립 신호로 신뢰도 동적 보정(AI/LLM 추론이 필요한
  유일한 지점). 원인 서술(그래프/체인형)은 핵심 산출물이 아니라 최종
  신뢰도 판단의 근거·투명성 표시로 격하.
- **AI Q&A 제외**: 내용이 전혀 정의 안 된 placeholder였음(질의 범위·응답
  데이터·다른 AI 기능과의 관계 전부 미정) — §6 IA에서 빼고 §10 미해결
  이슈로 이관.
- **§7.1 화물 탭 세부 수정**: On-carriage 단계는 이미 환적이 끝난 시점이라
  TS 컬럼 불필요 → 제거(TS 칩 표기는 Pre/Main-carriage로 범위 한정). ETA는
  대부분 선사 공지값이지만 담당자 수기 업데이트 소스도 있다는 점 명시.
- **§7 탭 서브헤딩 변경**: 화물 "어디에 있고, 왜 그런가"→"어디에 있고, 언제
  도착할 것인가" / 업무 "앞으로 잘 진행될 것인가"→"현재 어느 단계에 있고,
  업무 지연은 없는가" / 비용 "돈이 새고 있거나 샐 위험이 있는가"→"불필요한
  비용이 발생하고 있지는 않는가".
- **`visibility_control_tower_mockup.html` 반영 완료**: 위 결정 중 화면에
  영향 있는 것 전부 적용 — 업무 탭 PO 리스트 subblock 삭제, 부킹 리스트에
  "관련 PO No"·"Item/수량"(미확정/확정 두 상태) 컬럼 추가(`cols-booking`
  grid-template 9열로 조정), 상단 요약의 "PO" stat → "Item 확정(CI/PL
  확보)" stat로 교체, note box·section-sub 문구 갱신, Port-to-Port 진입점
  1번을 "기존 부킹 재조회"로 변경. 화물 탭 On-carriage 테이블(해상·항공)
  TS 컬럼 제거(`cols-arrived` 6열로 조정). AI Q&A FAB(`.fab`) 및 관련 CSS
  삭제. 정적 서버(`.claude/launch.json`에 `mockup-static` 항목 추가, python
  http.server 8123)로 브라우저 로드해 콘솔 에러 없음·부킹 리스트 4건 렌더링·
  Item 셀 미확정/확정 값 정상 표시 확인 완료.
- **아직 미반영**: §8.1 Inventory 도메인 모델 트리(PO 루트 → CI/PL 루트로
  교체 필요), §8.2 데이터 소스 표의 PO 관련 서술, §10 관련 행 일부(§7.2 PO
  Item 표기는 CI/PL로 이미 정정함). 화물 탭 PO No 서브라인 표기는 그대로
  두되 "CI/PL 참조 라벨"이라는 성격 명시는 아직 안 함.

## 다음 단계 (여기서부터 이어가면 됨)

**(2026-08-09 세션 기준 최신)** `PRD_수정지침.md` 1·2단계 + 사용자 리뷰
피드백(2차 + §9.8 삭제)까지 반영해 `VisibilityControlTower_PRD.md`를
**v1.4 → v2.3**로 올림. 최종적으로 PRD는 **§1~§12까지만** 남고, 예전
§13(진행현황)·§14(다음단계)는 통째로 삭제해 이 파일로 이관했다(아래가
그 통합본 — PRD 자체 status/다음단계 섹션은 더 이상 없음, 성격상 이
파일이 정본이 맞다는 사용자 판단). PRD 현재 목차: §1 개요·§2 문제정의·
§3 컨셉·§4 대상 사용자·§5 백본·§6 IA·**§7 도착 시점 정확도(신설)**·§8
Transportation 기능요구사항·§9 Inventory 기능요구사항(§9.1~§9.7, 로드맵
§9.8은 삭제)·§10 vessel-tracker·§11 미해결 이슈·§12 범위 제외. 상세
경과는 아래 "2026-08-09 세션" 기록들 참고.

**커밋·배포 완료** — `PROGRESS.md`/`VisibilityControlTower_PRD.md`/
`PRD_수정지침.md` 3개 파일을 커밋(`21518af`)하고 `origin/master`에
푸시 완료(밀려 있던 이전 세션 커밋 2개도 함께 나감:
`0b8b37f`/`5b022aa` → `21518af`). **단, 아래는 이번 커밋 범위에서
일부러 제외했다** — 오늘 세션(PRD 문서 정리)과 무관한 별개 작업이라
같은 커밋에 섞지 않음, 각각 별도로 커밋할지 사용자 확인 필요:
- `vessel-tracker/*`(SeaVantage 전환, 2026-08-06 세션) 및
  `visibility_control_tower_mockup.html`(Inbound 신뢰도 Agent 프로토타입
  반영, 2026-08-08 세션) — 여전히 미커밋 상태.
- `raw data/`(Tracking.xlsx 등 실 고객 데이터 4개 파일, 1.2MB) —
  **아직 Git에 추가 안 함**. 이 리포지토리가 공개(public) GitHub
  저장소인데, 이 폴더는 실제 고객 샘플 데이터([[raw_data_not_representative]]
  참고)라 커밋 전에 공개해도 되는지 사용자에게 반드시 확인 필요
  (`.gitignore`에도 아직 대상으로 안 걸려 있음).

**다음 탭/영역별 상태 요약** (구 PRD §13, 이관):

| 탭/영역 | 상태 | 산출물 |
|---|---|---|
| 화물 | 콘텐츠 모델 확정, 목업 리뷰 진행 중 | `visibility_control_tower_mockup.html` |
| 업무 | 콘텐츠 모델 확정, 목업 리뷰 진행 중 | `visibility_control_tower_mockup.html` |
| 비용 | 콘텐츠 모델 확정, 목업 리뷰 진행 중 | `visibility_control_tower_mockup.html` |
| 재고 | 콘텐츠 모델 확정, 목업에 실 raw data 반영 완료, 리뷰 진행 중 | `visibility_control_tower_mockup.html`, `synthetic-data/` |
| Overview | 설계 착수 전(다른 탭 완료 후 진행) | — |
| vessel-tracker | 프로토타입 완료(데모 목적) | `vessel-tracker/` |

**다음으로 할 것** (우선순위는 사용자와 상의, 구 PRD §14 항목을 아래
기존 목록과 합쳐 중복 제거):
1. **[구현] 재고 탭 Inbound 신뢰도 설명 Agent** (PRD §7.5) — 입고 예정
   리스트 전체 건에 근거 텍스트 생성, CP_Vessel_List 미매칭 건 fallback
   동작 확인, WebSearch 결과 기준일 표시·2주 필터 적용. 검증되면 화물 탭
   지연 사유 분석 화면 구현으로 확장.
2. **[결정] CI/PL Intake Agent 착수 여부** (PRD §8.5) — Pantos 실제 CI/PL
   입수 경로(구조화 파일 vs 이미지/PDF) 확인 후, 경로 A(컬럼 매핑) 선행
   구현 여부 결정.
3. **[설계] 재고관리 Agent 범위 설계** (PRD §9) — 입력 신호(Port
   Congestion/News/ETA Confidence/Supply Pipeline)·판단 로직·출력 형태
   정의. 1·2번과 데이터/설계 재사용.
4. **[구현] Inventory Engine 단위테스트** (PRD §9.4) — `synthetic-data/`를
   입력으로 재고 계산식 검증.
5. **[설계] 신뢰도 노출 강화 화면 설계** (PRD §9.5 "신뢰도 노출 강화") —
   Inbound 건별 신뢰도 1차 노출, Init ETA 대비 갭 분포 위치, 소스 상충 시
   채택값 표시 3요소의 화면 사양 확정.
6. **[운영] PRD §11 미해결 이슈 정기 재점검** — 사용자 제안(2026-08-09):
   `[가정]` 태그가 붙은 영역이 언제 `[검증]`/`[설계]`로 "실현화"될 수
   있는지 지속 모니터링하는 게 중요하다는 지적 반영. PRD §11 표의 "데이터
   확보" 행이 곧 이 승격 조건 목록이라고 PRD에 명시해둠(§11 인트로 참고) —
   새 데이터·시스템 연동이 생길 때마다 이 표부터 훑어 승격 가능한 항목이
   있는지 확인할 것. 세션 시작 루틴에 넣을지는 다음에 상의.
7. **vessel-tracker/mockup/raw data 커밋 여부 확인** — 위 "커밋·배포 완료"
   참고. 문서 정리 커밋과 별개로 언제 커밋할지, `raw data/`는 공개
   저장소에 올려도 되는지 확인 필요.
8. (선택) Item 상세 "Inbound Schedule" 서브리스트에도 근거/신뢰도
   드릴다운 붙이기 — PRD §9.5 명시 사항, 지금은 top-level Inbound
   리스트에만 붙어있음.
9. 재고 탭(재고 투영/입고 예정) 화면 리뷰 계속 — 남은 문구/인터랙션 피드백 반영.
10. 재고 투영 Item 리스트 정렬 로직 정하기(Shortage 임박 순 등).
11. 화물/업무/비용/재고 탭이 다 정리되면 → 마지막으로 통합 Overview 재구성.

> PRD 도메인 모델 트리의 PO→CI/PL 전환은 이미 처리 완료(§9.1 루트가
> `Commercial Invoice / Packing List`). PRD를 참조할 때 번호는 §1~§12
> 범위이며 예전 §13/§14는 더 이상 존재하지 않는다(이 섹션이 그 대체).

**화물 탭에서 나온 패턴 중 업무 탭에도 참고할 만한 것**: 언어 규칙(CLAUDE.md), Total/Delayed 같은 통계 표기, "정밀 수치 대신 등급/구간으로 표현"(PTA의 P50/P95 ↔ 업무 탭 스페이스 신호의 등급+추세).

**화물 탭에 남아있는 미해결 항목** (나중에 돌아올 것):
1. **"리스크" 상태 정의** — 환적 있음=리스크는 아님. 어떤 조건이면 리스크로 볼지 아직 미정.
2. **PTA 방법론** — "과거 예측 정확도 이력 데이터 필요"라는 의존성은 이번
   세션에서 지연 사유 분석의 "정적 신뢰도" 산출에 그대로 쓰인다고 명확해짐
   (`VisibilityControlTower_PRD.md` §7.1, §10). 실 raw data(컨테이너
   트래킹/선사 스케줄/항만 혼잡도) 확보되면 파일럿 착수 가능.
3. ~~재고 부족 시뮬레이션~~ — Inventory 도메인으로 이관됨(위 "Inventory 도메인 신설" 참고). Out의 낙관/비관 방향 미해결 이슈는 `VisibilityControlTower_PRD.md` §10로 옮겨서 계속 추적.
4. 화물/업무/비용/Inventory 탭이 다 정리되면 → 마지막으로 **통합 Overview 재구성** (기존 계획 유지, 범위가 Transportation+Inventory로 확장됨).

**업무 탭에 남아있는 미해결 의존성**:
1. **Item 단위 연결 의존성** — CI/PL Item 수량 → 부킹 → B/L → 컨테이너 매핑에 적입/장입 확정 데이터(Stuffing List) 필요(2026-08-05: 소스를 PO에서 CI/PL로 전환). 대부분 Pantos 내부 시스템 연동 문제(예외: FCL 자가적입 시 고객 Packing List 필요). "데이터가 있다는 전제"로 설계 계속 진행 중. 화물 탭 Item 통합 뷰와 공유하는 의존성.
2. **Inland 스케줄 마스터 의존성** — Inland Routing 트럭/철도 옵션 비교(리드타임/비용/프리타임)가 성립하려면 별도 스케줄 마스터 데이터 등록이 필요. "데이터가 있다는 전제"로 설계 계속 진행 중.

새 세션에서는 이 파일을 먼저 읽고, "`visibility_control_tower_mockup.html` 리뷰부터 이어가자"고 이어가면 됩니다.

---

## Item 단위 통합재고관리 — 신규 별도 트랙 (2026-08-07 세션 시작, 같은 세션에 다시 통합됨)

기존 Visibility Control Tower는 범위가 넓어서, 그중 재고관리 하나로
압축한 **별도 PRD**를 새로 시작함. 산출물:
`ItemLevel_InventoryManagement_PRD.md`(현재는 삭제됨 — 아래 "PRD 재통합"
참고). **당시엔 위 Visibility Control Tower 트랙과 독립적으로 진행**하기로
했었음.

- **제목 확정**: "Item 단위 통합재고관리" — On-hand와 In-transit(운송중
  재고)을 같은 관리 기준으로 통합한다는 의미로 여러 후보 중 선택.
- **v0.1(이 세션에서 Claude가 작성)**: CI/PL 확보 → 부킹/PCP 관리 →
  국제운송관리(CP/TS/POD ETA) → POD 양하·Route Planning → FDEST
  도착·재고계산, 5블록 구조로 초안 작성.
- **v0.2(사용자가 별도 작업물을 docx→md로 전달)**: raw data(Tracking.xlsx/
  CP_Vessel_List/Port Congestion) 구조를 반영한 개발 기준본. Entity
  Model, Inventory Engine 규칙(Grain=Item×Date, Normal/Risk/Shortage
  3단계 판정), UI 요구사항(Screen A/B), Acceptance Criteria, 테스트
  시나리오까지 포함된 상세 스펙 — v0.1보다 훨씬 구체적이라 이 버전을
  기준으로 프로젝트 PRD를 재작성함.
- **v0.2 리뷰에서 사용자가 내린 3가지 결정** — 전부
  `ItemLevel_InventoryManagement_PRD.md`에 반영 완료:
  1. POD 양하/Route Planning(Shortage 임박도 기반 하역 우선순위) → MVP
     제외, Phase 2 이관.
  2. POD ETA 자체 보정 로직(선사 ETA가 비합리적일 때 자체 수정) →
     Phase 2에서 확정할 사항으로 명시.
  3. 입고버퍼시간 → 되살림. raw data에 실제로 `W/H In Date`(실입고일)
     컬럼이 존재하는 걸 발견해서, 이 필드를 1순위로 쓰는 우선순위
     로직으로 §10.1 재정의(§10.1: W/H In Date → 없으면 ATA+버퍼 →
     없으면 ETA+버퍼).
- **raw data 실사 검증 완료** (`raw data/Tracking.xlsx`, 155건, 110컬럼):
  - 전량 On-board 이후 상태(POL ATD 결측 0건) — Pre-carriage 케이스가
    이 스냅샷엔 없음.
  - 완료건(F.DEST ATA 존재)도 0건 — 입고버퍼 로직을 실측 검증할
    데이터가 아직 없음.
  - 완전 동일 키(Container+Item+Model+QTY+HouseBL+Invoice) 중복 행
    0건 — §10.2에서 우려했던 중복 케이스가 이 데이터에서는 발생하지
    않음, Open Issue 우선순위 하향.
  - → 부족한 케이스는 합성 데이터로 보완하기로 사용자가 확정.
- **`synthetic-data/` 폴더 신규 생성**: 실제 Tracking.xlsx의 Model(=Item)
  6종과 실제 Inbound 수치는 그대로 쓰고, On-hand/Outbound/Safety
  Stock만 합성해서 Normal/Risk/Shortage/Recovery 4개 상태가 모두
  나오도록 구성(REFRIGERATOR=Shortage→Recovery, RO
  COMPRESSOR=Risk only, MOTOR=전기간 Normal 등). 실제 엔진 계산식으로
  결과를 검증 완료. 엔진 단위테스트용 예외 케이스(Pre-carriage 제외,
  입고버퍼 우선순위, 완전동일 중복, QTY 결측) 5건도 별도 생성.
  `generate_synthetic_data.py`로 재생성 가능, `README.md`에 시나리오
  표 정리.
- 사용자가 Claude Design(이 세션과 별개의 새 대화)에서 화면을
  만들어보고 싶어함 — PRD와 함께 넘길 **압축 이벤트 테이블**(REFRIGERATOR
  Shortage→Recovery, RO COMPRESSOR Risk only 두 시나리오)을 이 세션에서
  만들어 전달함. 그 새 대화의 결과물은 이 세션 기록에는 없음 — 다음
  세션에서 사용자가 결과를 가져오면 리뷰.

### v0.2 → v0.2-lite로 축소 (같은 세션 이어서)

사용자가 "v0.2에 너무 많은 내용이 포함된 것 같다"며 별도로 정리한
**lite 버전**을 전달, 이걸로 `ItemLevel_InventoryManagement_PRD.md`를
교체함. lite 버전은 Entity Model 상세, DB 스키마, API Contract, AC
리스트, 테스트 시나리오, raw data 필드 매핑 테이블, Open Issues
테이블 등 **구현 스펙 성격의 내용을 전부 제거**하고, "지금까지 논의에서
명확히 합의한 내용만" 담은 개념/제품 수준 문서다(19개 섹션 — Product
Vision, 핵심 가치, Forwarding/W&D 역할, Item 정의, Inventory 계산
개념, 3단계 상태, 핵심 화면, Drill-down, ETA Confidence, AI 역할,
발전 방향, 미확정 사항 등).

- 위 3가지 결정(POD 양하/Route Planning 제외, ETA 자체보정 제외,
  입고버퍼시간 반영)은 무거운 스펙 형태가 아니라 **한두 문장으로
  가볍게** 문서에 남김 — §8(입고버퍼 개념), §14(ETA 자체보정 제외),
  §17(Next 단계에 우선순위 배정 한 줄), §18(미확정 사항 리스트에 3개
  추가).
- **제거된 상세 내용(AC, DB 스키마, raw data 검증 수치 등)은 삭제된
  게 아니라 이 PROGRESS.md와 `synthetic-data/README.md`에 이미 기록되어
  있음** — 필요하면 거기서 다시 찾을 수 있음. `synthetic-data/` 폴더
  자체(합성 데이터·재생성 스크립트)는 그대로 유지, 화면 데모용으로
  계속 사용 가능.
- v0.2(무거운 버전)는 더 이상 프로젝트 파일로 남아있지 않음(교체됨) —
  필요하면 이 PROGRESS.md 위쪽 기록으로 세부 내용을 복원 가능.

### Item 단위 통합재고관리 — 다음 단계 (2026-08-07 세션 후반에 아래 "PRD 재통합"으로 처리됨, 이 목록은 기록용)

1. ~~Claude Design(별도 대화)에서 화면 결과가 나오면 가져와서 리뷰~~ —
   대신 같은 세션에서 기존 `visibility_control_tower_mockup.html`의 재고
   탭을 직접 수정하는 쪽으로 결정(아래 "재고 탭을 실제 raw data 기반으로
   교체" 참고).
2. 입고버퍼시간 구체적 일수, POD 양하 우선순위, ETA 자체보정 방법론 —
   `VisibilityControlTower_PRD.md` §10(미해결 이슈 표)으로 이관됨.
   개발 착수 시 순서대로 확정 필요.
3. Inventory Engine 실제 구현 착수 시 `synthetic-data/`를 입력으로
   단위테스트 작성(위 v0.2 상세 내용 — raw data 검증 결과, 엔진 규칙
   등 — 참고).

### 2026-08-07 세션 이어서 — 재고 탭을 실제 raw data 기반으로 교체

Claude Design 등 별도 자리에 새로 만드는 대신, 기존
`visibility_control_tower_mockup.html`의 재고 탭을 직접 수정하는 쪽으로
결정(사용자 선택 — 이미 Item 리스트/Projected 차트/드릴다운 인프라가
갖춰져 있어 처음부터 새로 만드는 것보다 빠름). Mock 3-SKU 데이터를
`raw data/Tracking.xlsx` 실제 6개 Item(REFRIGERATOR 등)과
`synthetic-data/`(On-hand/Outbound/Safety Stock)로 전면 교체.

- **Inbound 데이터**: `Tracking.xlsx`에서 Container+P/O 단위로 QTY 합산,
  Item당 6~33개 컨테이너(REFRIGERATOR 10 / RO COMPRESSOR 33 / MOTOR 28 /
  PARTS FOR REFRIGERATOR 9 / REFRIGERATORS COMPRESSOR 6 / MICROWAVE OVEN
  2). 전량 On-board 확인 상태라 그대로 Inbound 후보로 반영, MICROWAVE
  OVEN에만 `pipeline_precarriage.csv`의 Pre-carriage 20,000 EA를 계산
  제외 pending 항목으로 추가.
- **P95/P50 표기 제거**: 실제 raw data엔 확률 개념이 없어(화물 탭 PTA와는
  다른 개념) `ItemLevel_InventoryManagement_PRD.md` §7 정의대로 "현재
  FDEST ETA" 단일값 + "Init. ETA"(최초 예상, 지연 비교용)로 단순화.
  관련 텍스트(노트박스·컬럼헤더·서브텍스트) 전부 갱신.
- **Outbound 합성 데이터를 자연스럽게 개선**: 기존엔 Item당 매일 동일
  수량이라 Projected 추세선이 완전 직선으로 나와 사용자 피드백("어색함")을
  받음 → 요일 가중치(주말 감소) + 시드 고정 의사난수 jitter로 매번
  같은 결과가 나오되 지그재그 형태가 되도록 수정. 원래 검증된
  Risk/Shortage/Recovery 날짜(README 표)와 거의 동일하게 재현됨(우연히
  REFRIGERATOR 8/14 등 그대로 일치 확인).
- **화물 탭과의 드릴다운 정합** (사용자 결정 — "컨테이너/BL번호만 정합,
  화물 탭 3단계 시나리오는 그대로 유지"): 화물 탭에 이미 존재하는
  Main-carriage 컨테이너 2건(TCLU5520134/PO-24815, MSKU7712901/PO-24902)을
  REFRIGERATOR·RO COMPRESSOR의 대표 shipment 1건씩에 재사용해서 그
  2건만 클릭 시 실제로 화물 탭 상세로 연결되도록 함. 나머지 실제
  컨테이너(86건)는 원래 번호 그대로 두고, 클릭하면 기존에 있던 graceful
  fallback(toast: "이 목업 데이터엔 상세가 없습니다")으로 처리 — 화물/업무/
  비용 탭에 이미 깊게 얽혀있는 기존 컨테이너 ID(TCLU5520134 등)를 실제
  raw data 번호로 통째로 rename하는 건 다른 탭(업무 탭 부킹, 비용 탭 D&D
  리스트 등)까지 대규모로 건드리는 위험이 있어 하지 않음 — 대신 재고
  탭 쪽에서 기존 ID를 "재사용"하는 방향으로 최소 침습적으로 처리함.
- **버그 발견·수정 (이번 작업과 무관한 기존 이슈)**: 파일에
  `<meta charset="UTF-8">`이 아예 없어서 로컬 정적 서버로 열면 한글이
  깨지는 문제 발견(브라우저 검증 중 실제로 깨진 화면 확인) — `<title>`
  앞에 charset 메타 태그 추가로 수정. 화물/업무/비용 탭도 이 수정으로
  더 이상 안 깨짐(회귀 없음 확인).
- **UI 보강**: 일자별 상세 수치 테이블(최대 55일치)과 Inbound Schedule
  리스트(최대 33건)가 길어져서 `#inv-d-timeline-rows`/
  `#inv-d-shipment-rows`에 `max-height:380px; overflow-y:auto` 추가.
  차트 x축 라벨도 촘촘해지지 않도록 최대 12개만 샘플링해서 표시.
- **브라우저 검증 완료**: 6개 Item 리스트, REFRIGERATOR 상세(차트+일자별
  표+Shortage 배너 8/14), MICROWAVE OVEN pending 표시, Inbound 88건
  리스트, 화물 탭 드릴다운 성공 케이스(TCLU5520134)와 실패 fallback
  케이스(HAMU2277719) 모두 확인, 콘솔 에러 없음, 다른 탭 회귀 없음.
- **아직 안 한 것**: 나머지 84건의 실제 컨테이너도 화물 탭에 완전히
  연결하려면 화물 탭 쪽에 새 detail 데이터를 만들어야 함(이번엔 범위에서
  제외). 아직 커밋 안 됨.

### 같은 세션 이어서 — 합성 W&D 수치 재조정 (사용자 피드백 3건 반영)

재고 탭을 실데이터 기반으로 바꾼 뒤 사용자가 화면을 보고 준 연속 피드백을
반영해 On-hand/Safety Stock/Outbound 합성 수치를 다시 조정함.

1. **"Outbound 물량이 너무 적어 보임"**: 기존 W&D 합성 수치(§v0.2, On-hand
   2~6만/Safety Stock 1.5~3만)가 실제 raw data의 입고 Lot 크기(한 번에
   3만~40만 EA)에 비해 지나치게 작아서, 입고 1건이 재고를 10배 이상
   튀어오르게 만들고 그 뒤로는 계속 우하향만 하는 그림이 나왔음 —
   Outbound가 상대적으로 무의미하게 작아 보이는 원인이었음.
2. **"Inbound가 가끔씩 들어와서 회복하는 모습이어야 하는데 한 번 왕창
   들어왔다가 계속 떨어지기만 함"**: `Tracking.xlsx`의 실제 FDEST ETA
   분포를 확인해보니 REFRIGERATOR/PARTS FOR REFRIGERATOR는 입고가 사실상
   1~2개 날짜에 몰려있고(대량 벌크 발주 패턴), RO COMPRESSOR/MOTOR는
   3~5개 날짜에 분산되어 있어 — 이건 데이터 자체의 특성이라 없는 입고를
   지어내지 않는 선에서, Outbound 스케일을 실제 총 입고량에 비례하게
   재계산(요일 가중치+고정 시드 의사난수로 자연스러운 지그재그 추가)해서
   해결.
3. **"재고 과다도 문제 아니냐(창고보관료)"**: 위 대응 과정에서 On-hand를
   과도하게 높여(Safety Stock의 2배 이상) 아예 안 떨어지게 만들었던 것을,
   Safety Stock의 약 1.3배 수준으로 다시 낮춰서 큰 입고 이후에도 계속
   여유재고로 남지 않고 자연스럽게 다시 내려오도록 조정.

최종 결과(6개 Item 중): **Shortage(문제) 2개**(MOTOR, REFRIGERATORS
COMPRESSOR), **Safety Stock 이하(잠깐 타이트했다가 회복)** 4개 — 전부
문제처럼 보이지도, 전부 과잉재고로 보이지도 않는 균형점. REFRIGERATOR/
RO COMPRESSOR처럼 입고 1건이 40만 EA대로 유독 큰 Item은 입고 직후 한동안
여유재고 구간이 남는데, 이는 실제 대량 벌크 발주 패턴을 정직하게 반영한
것이라 데이터를 더 조작하지 않고 그대로 둠(사용자에게 설명 완료).

### 같은 세션 이어서 — `ItemLevel_InventoryManagement_PRD.md`를 `VisibilityControlTower_PRD.md`로 재통합

사용자가 "재고 탭이 이미 같은 목업 파일에 구현돼 있는데 PRD만 계속
별도로 유지할 이유가 있냐"고 문제 제기 → 동의하고 병합 진행.

- `VisibilityControlTower_PRD.md` §8(Inventory 기능요구사항)을
  `ItemLevel_InventoryManagement_PRD.md`(v0.2-lite, 19개 섹션) 최신
  내용으로 전면 교체. §8.1(도메인 모델)은 CI/PL 루트를 유지하되 raw
  data의 `Model`=Item 매핑 설명을 추가. §8.4(Inbound 인식 시점)에
  On-board 확인 물량만 반영, 입고버퍼 우선순위(W/H In Date → ATA+버퍼 →
  ETA+버퍼), Confirmed/Planning Projection 분리 개념을 새로 추가.
  §8.6(ETA Confidence), §8.8(AI 역할), §8.9(MVP 검증 목적),
  §8.10(raw data 검증 결과), §8.11(발전 방향)은 신규 섹션.
- §10 미해결 이슈 표에 ItemLevel PRD §18의 미확정 사항(입고버퍼 일수,
  POD 양하 우선순위, ETA 자체보정, News 연결 방식 등) 전부 이관.
- §1 상태·버전(v1.3→v1.4), §13 진행 현황, §14 다음 단계도 갱신.
- `ItemLevel_InventoryManagement_PRD.md` 파일은 삭제. 이제 프로젝트에
  Visibility Control Tower 트랙 하나만 존재 — 새 세션 시작 시 더 이상
  "어느 트랙을 이어갈지" 물어볼 필요 없음(이 문서 상단 안내 갱신 완료).
- 아직 커밋 안 됨.

### 같은 세션 이어서 — 재고 탭 6개 Item에 서로 다른 시나리오 아키타입 부여

사용자 피드백: "지금은 6개 Item이 다 8/10 이후에 Safety Stock 이하나
Shortage가 나오는 비슷한 모양이다 — 관리 잘되는 사례/왕창 입고 후 소진되는
사례/입고만 있고 출고가 적어 계속 늘어나는 사례처럼 다양하게 만들어달라."
→ 6개 Item을 2개씩 3가지 아키타입으로 재배정(각 Item의 실제 Inbound
클러스터 개수·크기 패턴에 맞춰 배정 — 없는 입고를 지어내지 않는 원칙
유지):

| 아키타입 | Item | 근거 |
|---|---|---|
| **관리 잘됨** (주기적 입고+꾸준한 소진, Shortage 없이 SS 근처 유지) | RO COMPRESSOR(ROTARY COMPRESSOR), REFRIGERATORS COMPRESSOR | RO COMPRESSOR는 실제 입고가 8/17·19·24·26·31 총 5개 클러스터로 분산돼 있어 주기적 보충 그림이 자연스러움 |
| **부족** (왕창 입고 후 소진 → Shortage, 이후 추가 입고 없어 재차 악화) | MOTOR, PARTS FOR REFRIGERATOR | 마지막 실제 입고(MOTOR 8/31, PARTS 8/26) 이후 9월엔 입고가 없어 그대로 두면 자연히 소진되는 real raw data 특성을 그대로 살림 |
| **과잉** (입고는 크게 들어오는데 Outbound가 상대적으로 작아 계속 누적) | REFRIGERATOR, MICROWAVE OVEN | 실제 입고 1건이 압도적으로 큰(REFRIGERATOR 40만+ EA) Item — Outbound 배율을 의도적으로 낮게 잡아 "발주는 컸는데 소진이 느린" 과잉재고 신호를 보여줌 |

각 아키타입은 On-hand/Safety Stock/일일 출고량(dailyOutbound)만 조정해서
만들었고(Inbound 자체는 실데이터 그대로), "관리 잘됨" 2종은 절대 Shortage로
안 내려가게(최소 잔량이 항상 양수) 파라미터를 확인 후 미세조정함. 최종
상태: Shortage 2종(MOTOR·PARTS FOR REFRIGERATOR), 나머지 4종은 Safety
Stock 이하 배지가 잠깐 뜨지만 그 뒤 궤적이 서로 다름(관리형은 SS 근처로
안정, 과잉형은 SS 대비 5배 이상으로 계속 높게 유지) — 브라우저로 4개 Item
차트 직접 확인해 의도한 모양대로 나오는 것 검증 완료.

사용자가 "리스트 배지 자체는 왜 다 8/10 근처로 비슷해 보이냐"고 재차
질문 → 배지는 "지금까지 한 번이라도 SS 밑으로 내려간 적 있는가"만
판정하는 구조라 6개 다 기준일~첫 입고(대부분 8/17 이후) 사이 공백에서
비슷하게 한 번씩 걸릴 수밖에 없고, 실제 차이는 그 이후 회복 모양(차트를
열어야 보임)에 있다고 설명함. 리스트 단계에서부터 구분하려면 "과잉재고"를
Normal/Risk/Shortage 3단계와 별도인 4번째 상태로 추가해야 하는데, 이번
세션에서는 반영 안 하고 다음에 필요하면 결정하기로 함(`VisibilityControlTower_PRD.md`
§8.5 상태 판정 로직 변경이 필요한 사항).

### 같은 세션 이어서 — 재고관리 Agent 논의 시작 (설계 착수 전, 다음 세션으로 이관)

"재고 상태 보고 발주/발주중단 판단하는 에이전트 만들면 어떨지" 질문에
대한 논의. 결론(상세는 `VisibilityControlTower_PRD.md` §10 "재고관리
Agent의 필요 범위" 행 참고): 단순 임계값 판단(재고<SS→발주, 과다재고→중단)은
룰 베이스로 충분하고 에이전트가 필요 없다(§8.5 Normal/Risk/Shortage
판정이 이미 그 역할). 에이전트가 값어치를 하는 지점은 Port Congestion·
News·ETA Confidence·Supply Pipeline처럼 정형화 안 된 신호를 종합해 발주
의사결정을 권고하는 한 단계 위 — 이는 §8.10 Advanced/Target Vision에
방향만 있고 설계 전인 영역과 일치. **다음 세션에서 이 에이전트를 새로
설계하기로 함** — 이번 세션에서는 방향성 합의만 하고 입력 신호·판단
로직·출력 형태 등 구체 설계는 시작하지 않았음.

### 같은 세션 이어서 — PRD와 PROGRESS의 역할 재정리 (사용자 지적 반영)

사용자가 "PRD에 PROGRESS 성격의 내용(날짜 박힌 검증 이력 등)이 들어갈
필요 없지 않냐"고 지적 → 동의하고 `VisibilityControlTower_PRD.md`에서
PROGRESS-log 성격 내용을 정리함:
- §8.10 "raw data 검증 결과 (2026-08-07)" 서브섹션(155건/110컬럼 등
  세션 로그성 통계) 전체 삭제 — 내용 자체는 이 PROGRESS.md에 이미
  있으므로 중복이었음. 핵심 결론(입고버퍼 로직 실측 검증 불가 상태)만
  §8.4에 한 줄로 남기고 "검증 이력은 PROGRESS.md 참고"로 연결.
- §8.12 "재고관리 Agent — 논의 시작 (2026-08-07 세션...)" 서브섹션도
  세션 서술("이 세션에서는...", "다음 세션에서...") 위주라 삭제,
  결론만 §10 미해결 이슈 표에 한 행으로 압축.
- §8 도입부의 통합 경위 설명 블록도 세션 날짜·서술을 걷어내고 사실
  1~2문장으로 축소.
- 결과: §8이 8.1~8.10(구 8.9까지 그대로, 8.10은 발전방향으로 재배치)로
  재번호, 관련 참조(§8.11→§8.10 등) 전부 수정. §14 다음 단계의 참조도 갱신.

### 커밋

위 모든 변경사항(재고 탭 실데이터 반영, 아키타입 다양화, PRD 통합,
`.md` 문서 갱신)을 하나의 커밋으로 정리함 — 커밋 메시지·해시는 `git log`
참고.

## 2026-08-08 세션 — "지연 사유 분석" Agent 실현 가능성 검토

사용자 문제 제기: "우리가 mockup 화면만 만들었지 AI나 Agent로 구동할 수 있는
기능을 만든 게 없다" → PRD 전체를 AI/Agent 구현 후보 관점에서 재검토.

### 1차 검토 — PRD 기준 후보 서베이

§8.8(Inventory AI 역할)과 §10 미해결 이슈를 훑어 후보를 실현 가능성 순으로
정리: (1) 화물 탭 지연 사유 분석 실제 Agent화, (2) 재고관리 Agent(발주 추천,
PROGRESS 2026-08-07 세션에서 이미 "다음 설계 대상"으로 합의됨), (3)
vessel-tracker를 알림형으로 확장, (4) PTA(예측 ETA, 과거 정확도 이력 데이터
없어 낮은 우선순위). 근거: PRD가 "데이터가 있다면"이라는 전제로 미정 처리해둔
Port Congestion/News 데이터가 `raw data/`에 실제로 이미 있다는 걸 발견 —
지금까지 활용 안 하고 있었음.

### 2차 검토 — raw data 실조인 검증

사용자가 "raw data 폴더에 실데이터를 추출해 넣어뒀는데 그걸로 분석 가능한지
검토해달라"고 요청 → `python`(pandas/openpyxl)으로 4개 파일 실제 조인 테스트:

- **`Tracking.xlsx`**(155건, 110컬럼) × **`CP_Vessel_List.xlsx`**(선박별
  항차 스케줄, 실측 `Gap`/`Risk Alert` 포함): `Current Vessel` + `POD Port`로
  조인 시 **126건(81%) 매칭 성공**. 선박명 12척 중 8척이 직접 겹침(예:
  MAERSK EMERALD, XIN DA LIAN, MSC PROCIDA 등).
- **`Port Congestion.xlsx`**(1,350행, 주간 항구별 Dwell/Waiting/Working
  일수): Tracking의 POD 항구 2곳(MXZLO/MXLZC) 모두 W26~W31(6월말~8월초,
  Tracking ETA 시기와 일치) 데이터 커버 확인.
- **`Incident List.xlsx`**(7,681행, HBL 6,829건 실연결된 진짜 뉴스성
  사고 데이터): 파일 자체는 진짜지만 커버 항로가 PH/GB/GH/ZA 등(주로 항공)
  이라 이번 Tracking의 KR/CN/ID→MX 해상 항로와 **0건 겹침** — 이번
  데이터셋에는 못 씀(다른 프로젝트/기간 산출물로 추정, 나중에 맞는 항로
  데이터 들어오면 같은 구조로 재사용 가능하게 설계는 유지).

### 3차 검토 — WebSearch로 정성적 원인 보강 가능성

사용자가 "관련 항구를 직접 웹에서 찾아보는 건 어떤지, 크롤링 스킬이
필요한지" 질문 → 답은 "크롤링 스킬 불필요, 기존 `WebSearch` 도구로 충분"
(단, 이건 지금 이 세션에서 Claude가 직접 조회하는 것과 제품에 상시
크롤링/조회 기능을 넣는 것은 별개 — 후자는 서버가 검색 API(Brave/Serper
등)를 호출하는 백엔드가 필요해 별도 구현·계약 필요, 이번 세션 범위 아님).
실제로 Manzanillo/Lazaro Cardenas/Busan 세 항구를 WebSearch로 검색해본 결과:
- Manzanillo: 2025년 통관 파업 여파로 물류비 20% 상승, 하역 후 야드 반출까지
  최대 2주 대기(FreightWaves, Mexico Business News 보도)
- Lazaro Cardenas: 트럭커 봉쇄 이력, 2026년 1월 대기 4.33일→7월 1.2일로
  변동 폭 큼(FreightWaves, Kuehne+Nagel 보도)
- Busan: 현재 저혼잡(대부분 터미널 12시간 내, PNIT만 메가벌크선 정체로
  20시간)(Portcast)

raw data(정형 Gap/Dwell 수치)에는 없는 "왜 지연됐는지" 정성적 맥락을
WebSearch가 보강해준다는 것을 확인 — FreightWaves/Kuehne+Nagel/Everstream/
Portcast/GoComet 등 물류 전문 매체가 실제로 검색됨.

### 결론 — 다음 구현 대상 확정

"지연 사유 분석"(§7.1)을 **CP_Vessel_List(실측 Gap/Risk Alert) +
Port Congestion(항만 혼잡 추세) + WebSearch(정성적 원인 뉴스)** 3-소스
결합 기능으로 구현하는 것을 다음 세션 최우선 작업으로 확정.
`VisibilityControlTower_PRD.md` §10(지연 사유 분석 행 추가)과 §14(다음
단계 1번으로 승격) 갱신 완료. 아직 실제 코드 구현은 시작 안 함(이번
세션은 검토·문서화까지) — 커밋 안 됨.

### 같은 세션 이어서 — WebSearch 결과의 신선도(freshness) 문제 발견·정책 반영

사용자가 "지금 찾은 정보가 지금도 지속되고 있다고 볼 수 있냐"고 질문 →
방금 검색한 Manzanillo(2월 데이터를 "최근"이라 표방)/Lazaro Cardenas(7월,
가장 최신)/Busan(기준일 표기 자체 없음) 사례를 다시 보니 GoComet/Portcast
같은 사이트가 "실시간"이라 표방해도 실제 스냅샷 나이가 몇 주~몇 달로 섞여
있고 기준일 표기가 없는 경우도 있음을 확인. 사용자 판단: **기사 종류에
따라 다르지만 2주 이상 지난 정보는 사용 시 주의(신뢰도 하향/배제)** —
정확한 임계값·기사 유형별 차등은 미정. §10 "지연 사유 분석" 행과 §14
다음 단계 1번에 이 정책 반영 완료(WebSearch 결과는 기준일을 추출해 표시,
2주 이상은 신뢰도 하향/배제).

### 같은 세션 이어서 — 업계(해상 국제운송 Visibility) AI/Agent 적용 사례 조사

사용자 요청: "우리 PRD/데이터로 판단하지 말고, 업계에서 해상 국제운송
Visibility 영역에 AI/Agent를 쓰는 부분이 있는지 조사해달라." WebSearch로
6개 카테고리 확인(상세 출처는 이 세션의 대화 로그 참고, 요약만 기록):

1. **Exception/Roll Risk Agent** — project44의 "AI Ocean Exceptions Agent"(환적
   롤오버 위험 상시 모니터링→선사 확인→대체 스케줄 제시)
2. **Predictive ETA** — DHL Smart ETA/Shippeo/ShipsGo/Windward/Portcast/BuyCo/
   Blume 등 다수 상용화. "선사 정적 스케줄 55~70% vs AI 예측 90~96%" 주장 다수.
   방법론(AIS+과거 오차 이력+항만혼잡도)이 우리 PRD의 PTA(P50/P95) 설계와 유사.
3. **Control Tower 자동화 성숙도 단계** — Level 2(진단형, 룰 기반 알림) →
   Level 4(자율 실행형). 우리 "지연 사유 분석"=Level 2, "재고관리 Agent"
   (발주 추천)=Level 3(권고형)에 해당.
4. **서류(BOL/CI/PL) GenAI 추출** — OCR+LLM으로 PDF 서류에서 필드 추출.
   사용자가 "이거 우리 CI/PL Item 추출과 같은거 아니냐"고 질문 → 다른 층위임을
   확인: 우리 PRD(§8.1)는 Item/QTY가 **이미 구조화됐다는 전제**에서 도메인
   모델링만 다루는데, 이 카테고리는 **그 구조화 자체(원본이 PDF일 때 추출)**를
   다룸. 사용자가 명시적으로 정정: "raw data는 확보 가능했던 데이터를 끌고
   온 것일 뿐(우연히 `Tracking.xlsx`가 Item/QTY를 `Model`/`QTY` 컬럼으로 이미
   구조화해서 갖고 있음), 대부분 실제 고객은 CI/PL이 비구조화 문서로만 온다
   — raw data에 있다고 가능하다고 판단하면 안 됨." → §8.2/§10에 이 주의사항과
   "CI/PL 원본에서 Item/QTY 추출 자체가 미해결" 신규 행 추가, Pantos 실제
   CI/PL 입수 경로(시스템 연동 vs PDF) 확인이 선행 과제로 필요함을 명시.
   (일반화된 교훈은 Claude 메모리에도 별도 저장 — "raw data 샘플은 대표성
   없음", 향후 세션에서도 유효)
5. **대화형 Copilot/챗봇** — Maersk "Captain Peter" 등. 우리 PRD §10에서
   범위 미정으로 IA 제외된 "AI Q&A" 항목이 업계엔 이미 상용화되어 있음.
6. **운임 조달/협상 Agent** — project44 "AI Freight Procurement Agent". 우리
   비용 탭은 현황 표시만 다루고 협상/조달 액션은 스코프 밖.

**결론**: 지금까지 합의한 "지연 사유 분석"(Level 2)·"재고관리 Agent"
(Level 3)는 업계 성숙도 기준으로도 타당한 출발점. 반면 (4) CI/PL 문서
추출과 (5) 대화형 Q&A는 PRD에 아직 없거나 범위 미정인 채로 남아있는
항목 — 다음에 논의할지는 미정, 이번 세션에서는 조사·기록까지만.

### 같은 세션 이어서 — CI/PL 원본 형태, "이미지"로 단정한 것도 정정

사용자 지적: Claude가 CI/PL 추출 문제를 설명하며 "PDF 등 비구조화 문서"로만
좁혀 말한 게 편향됐다 — 실제로는 고객이 이메일로 엑셀 같은 구조화 파일을
보낼 수도 있고, 이미지/스캔으로 보낼 수도 있다(둘 다 가능, 하나로 단정
불가). 두 경우 필요한 기술이 다름: 엑셀이면 컬럼 매핑/파싱(고객마다
컬럼명이 달라 "이 컬럼이 Item이다" 판단 로직 필요, OCR 불필요), 이미지/PDF면
업계 카테고리 4의 OCR+LLM 문서 추출이 필요. §10 CI/PL 행에 이 두 갈래를
명시하고 "형태 확정 전엔 하나로 단정 금지"로 갱신 완료. 원본 형태 확인
자체가 여전히 선행 과제.

### 같은 세션 이어서 — CI/PL 두 경로 기술 설계(§7.5 신설)

사용자 요청으로 "정리하자" — 경로 A(구조화 파일: 운영담당자가 지정 폴더에
업로드 → 파싱은 결정론적, 컬럼 매핑에만 AI 필요·고객사당 최초 1회만 수행
후 룰 재사용)와 경로 B(이미지/PDF: MIME 분기 → 프로토타입은 멀티모달 LLM
직접 추출, 프로덕션은 Document AI+LLM 하이브리드 고려, QTY 등 신뢰도 낮은
필드는 사람 검수 필수)를 구체적으로 설계해 `VisibilityControlTower_PRD.md`
§7.5로 신설. 두 경로 모두 같은 표준 스키마로 정규화해 §8.1 Item 엔티티에
연결하는 공통 원칙, `vessel-tracker/`처럼 목업과 분리된 별도 백엔드
프로세스로 구현한다는 방향도 명시. §10/§14 참조 갱신, 업로드 폴더 형태와
Pantos 실제 입수 경로는 여전히 미정으로 남김.

### 같은 세션 이어서 — 업계 "AI 정확도" 주장에 대한 회의적 검증 (사용자 주도)

**ETA 정확도 조건 문제 제기**: 사용자가 "AI 예측 90% 이상은 어떤 조건인지가
있냐, 바로 직전 항구→다음 항구 수준이면 의미 없다"고 지적 → WebSearch로
검증한 결과 사용자 우려가 맞았음: Shippeo는 "도착 30일 전부터 90% 정확도"라
공언하지만 허용오차(±몇 시간)를 안 밝힘, ShipsGo는 "96% vs 선사 55%"라면서
샘플 크기·측정 방식 전혀 공개 안 함. 그나마 조건이 명시된 수치는 "10일 전
예측이 ±48시간 이내일 확률 87%"뿐. **교훈: 벤더의 정확도 마케팅 수치는
"며칠 전 예측 + 몇 시간 허용오차"라는 조건이 없으면 무의미** — 향후 우리
PTA(§7.1) 정확도를 표현할 때도 이 조건을 반드시 함께 명시해야 함.

**삼성SDS Cello Square "2주전 95%" 검증**: 사용자가 들었다는 이 수치를
WebSearch+WebFetch로 여러 각도로 검증했으나 공식 자료 어디에도 없음 확인.
Cello White Paper에 있는 유일한 구체적 수치는 "독일 유통업체 판매량 예측
정확도 53%→72%"인데 이건 수요예측(재고/판매량) 사례지 ETA 정확도가 아님 —
와전됐을 가능성. 사용자의 "과장 같다"는 판단이 근거 있음을 확인.

**project44 "AI Ocean Exceptions Agent" 재검증**: 사용자가 "이거 결국 TS
항구 입항/출항 스케줄 tight 여부 비교랑 같은 거 아니냐, 굳이 에이전트가
필요한가"라고 문제 제기 → 보도자료를 WebFetch로 파헤친 결과 확인: 롤리스크
"감지" 로직 자체는 사실상 스케줄 비교(입력이 "선사 공지"가 아니라 "실측
운항 이벤트"라는 데이터 소스 차이뿐, 판단 로직은 여전히 결정론적으로 보임).
"AI/Agent"라는 이름이 붙는 진짜 이유는 감지 로직이 아니라 (1) 규모/속도
(초당 수억 건 이벤트 병렬 처리로 선사 공지보다 35시간 먼저 감지), (2) 감지
이후 선사 확인·재예약 옵션 조회라는 워크플로 자동화. project44 자신도
"LLM은 비즈니스 케이스만으로는 불충분, LLM 위에 얹는 맥락 데이터가 진짜
가치"라고 인정 — 이는 우리 §8.8 원칙("MVP 핵심 계산은 AI가 아니라
결정론적으로")과 같은 결론. 사용자 판단이 맞았음을 확인.

### 같은 세션 이어서 — 최종 결론: 다음 구현 대상을 "재고 탭 회복일자 신뢰도
설명 Agent"로 재스코프

위 회의적 검증들을 거친 뒤 사용자가 제안: "재고 탭에서 On-hand/Outbound는
주어진 값이니 AI가 설명할 건 결국 Inbound(FDEST ETA)뿐 — 왜 부족해지는지,
회복 시점을 얼마나 신뢰할 수 있는지, 중간 리스크 요인이 뭔지를 분석해줄 수
있지 않나." → 이건 §7.1 지연 사유 분석의 2단 구조(정적 신뢰도+건별 보정)
및 §8.9 MVP 가설과 정확히 일치하는데, 지금까지 "화물 탭 전체"라는 넓은
스코프로만 얘기해온 것을 "재고 탭 Shortage Item의 회복일자 설명"이라는
좁고 구체적인 첫 구현 대상으로 재스코프하자는 제안. 장점: (1) §8.9 MVP
가설을 직접 검증하는 스코프, (2) 재고 탭은 이미 실데이터 6개 Item·아키타입
구현 완료라 새 기능 붙일 자리가 명확, (3) 화물 탭 전체보다 범위가 작아
먼저 완성·검증 가능. 사용자 승인("진행해줘") 받아
`VisibilityControlTower_PRD.md`에 신규 §8.6.1 "회복일자 신뢰도 설명
Agent"로 반영, §8.7 Item 상세에 연결, §14 다음 단계 1번을 이 스코프로
교체 완료. **다음 세션 시작점은 이 Agent의 실제 구현**(소스: CP_Vessel_List
Gap/Risk Alert + Port Congestion 추세 + WebSearch 정성적 원인, 기준일 2주
이상은 신뢰도 하향/배제). 아직 코드 구현은 시작 안 함 — 이번 세션은 조사·
스코핑까지, 커밋 안 됨.

### 같은 세션 이어서 — 적용 범위를 Shortage Item에서 전체 Inbound로 재확장

사용자 지적: "꼭 Shortage가 아니더라도 Inbound로 들어오고 있는 것들에 대해선
모두 분석할 수 있지 않냐." → 맞는 지적: 분석 파이프라인(Vessel+POD를
CP_Vessel_List/Port Congestion/WebSearch에 조인하는 계산) 자체는 Item의
Normal/Risk/Shortage 상태와 무관하게 동일하게 적용 가능 — Shortage로
좁혔던 건 기술적 제약이 아니라 "어디부터 화면에 노출할지"의 우선순위
문제였을 뿐이었음. §8.7에 이미 있던 "입고 예정(Inbound)" 리스트(전체
Inbound 건을 다룸)가 자연스러운 적용 대상이라 판단해, §8.6.1을
"Inbound 신뢰도 설명 Agent"로 개명하고 적용 범위를 **§8.7 입고 예정
리스트 전체**로 확장, Shortage/Risk Item에 걸린 Inbound는 강조 표시만
하는 것으로 정정. §8.7 Item 상세/입고 예정 섹션, §14 다음 단계 1번도
갱신 완료.

### 같은 세션 이어서 — raw data로 지금 바로 적용 가능한 범위 확인

사용자 질문: "지금 제공되는 raw data로 지금 말한 기능을 적용해볼 수 있는거야?"
→ python으로 실측 확인:
- `Tracking.xlsx` 155건 전부 §8.4 기준 On-board 확인 상태(POL ATD 존재)라
  전부 Inbound 대상.
- 이 중 **126건(81%)이 `CP_Vessel_List.xlsx`와 실제 매칭**(Current
  Vessel+POD Port 기준, 지난 세션에 이미 확인한 수치와 동일) — 실측
  Gap/Risk Alert 바로 적용 가능.
- Item(`Model`) 구성이 재고 탭에 이미 구현된 6개 Item(RO COMPRESSOR,
  REFRIGERATOR, MOTOR, PARTS FOR REFRIGERATOR, REFRIGERATORS COMPRESSOR,
  MICROWAVE OVEN)과 정확히 일치 — `synthetic-data/wd_item_master.csv`와도
  대조 확인함. 즉 재고 탭에 이미 떠 있는 Item들의 Inbound 화물 대부분에
  바로 적용 가능.
- `Port Congestion.xlsx`는 POD 항구(MXZLO/MXLZC) 100% 커버(기존 확인
  재확인), WebSearch도 이 두 항구로 이미 실제 검색해 유의미한 결과
  확인함(위 세션 참고).

**결론**: 나머지 29건(19%, CP_Vessel_List 미매칭)은 fallback 필요하지만,
**126건은 지금 있는 raw data만으로 바로 프로토타입 시험이 가능**함을
확인. 별도 데이터 확보나 조사 없이 다음 세션에서 바로 구현 착수 가능한
상태.

## 2026-08-08 세션(이어서) — Inbound 신뢰도 설명 Agent 프로토타입 실행 + 화면 텍스트 설계 확정

위 raw data 검증 직후 바로 파이썬 프로토타입을 짜서 실제 출력 텍스트를
만들고, 사용자와 함께 여러 번 다듬었음. 스크립트/샘플 출력은 스크래치
패드에만 있고(세션 재생성 시 사라짐, 커밋 안 됨) — **다음 세션에서
실제 목업에 반영할 때는 이 문서의 "확정된 화면 텍스트 구조"를 기준으로
다시 짜면 됨.**

- **파이프라인 실행 확인**: `Tracking.xlsx`(MOTOR Item, 29건 컨테이너
  단위) → Vessel+POD로 `CP_Vessel_List.xlsx`(Gap/Risk Alert) +
  `Port Congestion.xlsx`(MXZLO 최근 4주 추세) 조인 → WebSearch(Manzanillo
  정성적 배경, 기사 최신성 2개월 전이라 신뢰도 하향 처리 확인)까지
  실제로 돌려 근거 텍스트 생성 성공.
- **fallback 케이스 원인 규명**: MAERSK EINDHOVEN 항차가 로컬
  `CP_Vessel_List.xlsx`(2026-08-07 02:10 스냅샷)엔 없어 "매칭 없음"으로
  나왔으나, 사용자가 실제 시스템 화면(2026-08-08 01:14 기준)을 캡처해
  제공 — 그 안엔 존재했고 매칭 로직(Vessel+POD)도 정상 작동함을 확인.
  **"매칭 없음"은 파이프라인 설계 결함이 아니라 로컬 스냅샷 파일의
  갱신 주기 문제** — 프로덕션에서는 이 파일을 더 자주/실시간으로
  받아야 함. 지난 세션 "126/155건(81%) 매칭" 수치도 스냅샷이
  최신화되면 더 올라갈 가능성.
- **화면 텍스트 구조 확정**: 여러 라운드 피드백을 거쳐
  `🟢/🟡 등급 배지 → 한 줄 결론 → 리스크 포인트(있으면 목록, 없으면
  "없음") → 근거`로 확정. 말투는 최대한 쉽게(전문용어 나열 대신
  풀어쓰기). "CP_Vessel_List"를 가리키는 표현은 "실측 운항 데이터"가
  아니라 **"실제 선박의 기항지 운항 데이터"**로 확정.
- **"당겨짐(조기 확정)" 케이스도 Agent 범위에 포함하기로 확정**: 지연만
  다루던 것에서 확장 — FDEST ETA가 Init ETA(선적 시점 예상, **부킹
  시점 아님** — 사용자가 정정)보다 크게 당겨지는 경우도 155건 중 87건
  (56%)으로 흔함. 처음엔 "표준 리드타임보다 넉넉하게 잡아서" 식으로
  원인을 설명하려 했으나, 표준편차가 너무 커서(12.8일) 그 가설이
  실제로는 기각됨 — **"원래 데이터가 그렇다"는 원인 설명은 근거
  없는 추측이라 안 됨(사용자 지적)**. 최종적으로 사용자 제안으로
  **원인 설명 대신 "해당 POD Port 기준 과거 갭 분포와 비교해 정상
  변동 범위인지"만 통계로 판단**하는 방식으로 정리(MXZLO 154건 기준
  평균 -5.0일·표준편차 7.5일, 이번 -7일은 Z-score -0.27로 정상 범위).
  이건 §7.1 "정적 신뢰도"와 같은 성격(AI 불필요, 통계로 미리 계산
  가능) — Item/POD Port 조합별 과거 갭 분포 계산 로직을 파이프라인에
  추가해야 함.
- **실행 트리거 정책 확정**: 모든 Inbound를 상시 자동 분석하지 않음.
  **Shortage 상태 Item은 AI 분석 자동 실행**(화면 열자마자 근거 준비
  돼 있어야 함), **그 외(Normal/Risk)는 사용자가 드릴다운을 열어
  요청했을 때만 그 건에 한해 on-demand 실행**(WebSearch 등 비용 방지).
- **`VisibilityControlTower_PRD.md` §8.6.1 갱신 완료**: 위 실행 트리거
  정책, "당겨짐" 케이스 처리 원칙(원인 추측 금지, 정상범위 통계 비교로
  대체), 정상 범위 안이면 화면에 강조하지 않는다는 원칙까지 반영.

### 같은 세션 이어서 — 목업에 실제 구현

사용자가 "목업 구현까지 진행하자"고 요청 → `visibility_control_tower_
mockup.html`의 재고 탭 "입고 예정(Inbound)" 리스트에 실제로 붙임.

- **CSS**: `.cols-inbound` grid에 근거 버튼 컬럼 추가(6열: Item/Qty/
  FDEST ETA/Delay Status/근거/chev). `.conf-trigger`(일반/자동 두
  스타일), `.conf-list`(리스크 포인트·근거 목록), `.conf-caveat`(하단
  안내 문구) 신규 클래스 추가.
- **HTML**: `#inv-inbound` 섹션 안에 `#inv-conf-detail`(`.detail` 재사용)
  패널 신설 — 등급 배지(`#conf-badge`) → 요약(`#conf-summary`) → 리스크
  포인트(`#conf-risk`) → 근거(`#conf-evidence`) → 캐비어트(`#conf-
  caveat`) 구조. 기존 `inv-item-detail`/`detailBooking`과 같은 열림/
  스크롤 패턴 재사용.
- **JS**: `getItemTier(sku)`(Item의 Normal/Risk/Shortage 상태 메모이즈)
  + `analyzeShipmentConfidence(sku, sp)`(Init ETA vs 현재 FDEST ETA
  비교로 등급/요약/리스크 포인트/근거 생성, delayed 플래그가 true면
  🟡주의, 당겨졌으면 🟢정상+"정상 변동 범위" 문구, 동일하면 🟢정상+
  "예정대로") + `openConfidenceDetail(sku, id)`. `renderInboundList()`를
  수정해 각 행에 Shortage Item이면 `⚡ 근거 보기`(자동 계산된 등급을
  Delay Status 컬럼에도 즉시 반영), 아니면 `근거 보기` 버튼을 추가하고
  `e.stopPropagation()`으로 기존 "행 클릭 → 화물 탭 이동" 동작과
  분리했음.
- **주의 문구**: 패널 하단에 "프로토타입: Init/현재 FDEST ETA 비교 기반
  — 프로덕션에서는 CP_Vessel_List/Port Congestion/WebSearch 근거가
  추가됩니다"라고 명시 — 목업이 실제 raw data 파이프라인과 아직 연결
  안 됐다는 걸 화면에서도 투명하게 표시(과장 방지).
- **브라우저 검증 완료**(`mockup-static` 정적 서버, localhost:8123):
  Shortage Item(MOTOR) 자동분석 버튼 클릭 → 정상 등급 표시 확인,
  일반 Item(REFRIGERATOR, 지연 케이스) "근거 보기" 클릭 → 주의 등급 +
  리스크 포인트 2건 표시 확인, 버튼 클릭이 행의 "화물 탭 이동" 클릭과
  충돌하지 않음 확인(stopPropagation 정상 동작), 기존 행 클릭은 여전히
  화물 탭으로 정상 이동 확인, 콘솔 에러 없음.
- **아직 안 한 것**: Item 상세("재고 투영" → Item 클릭)의 "Inbound
  Schedule" 서브리스트에는 이 드릴다운을 안 붙임 — §8.7에 Item 상세도
  같은 기능이 필요하다고 나와 있어 다음 후보. 실제 raw data(CP_Vessel_
  List/Port Congestion/WebSearch) 연동은 별도 백엔드 작업으로 스코프
  밖. 커밋 여부는 사용자에게 아직 안 물어봄.

### 같은 세션 이어서 — 화면 크기를 Full HD(1920×1080) 기준으로, 폰트 확대

사용자 요청: "대시보드니까 화면을 Full HD 사이즈(1920×1080)로 하고
폰트도 가독성있게 키웠으면 해." 기존 CSS가 폰트 크기를 거의 다 절대
px(11~15px대)로 하드코딩해뒀어서 개별 규칙을 다 고치는 대신:

- `.app`에 `zoom:1.25` 적용 — px로 지정된 폰트/여백/아이콘 전부가 같은
  비율로 커짐(표준 속성은 아니고 Chromium 계열 전용이지만 목업 프리뷰
  용도로는 충분, 주석으로 명시해둠).
- `.main { max-width: 1260px → 1500px }` — 1920 너비를 더 활용하도록
  본문 폭 확대(zoom 1.25 곱하면 실제 렌더 폭 ~1875px로 1920 안에 여유
  있게 들어감, 계산 확인함).
- **브라우저 1920×1080 뷰포트로 실측 확인**: `document.documentElement.
  scrollWidth`(1905) < `window.innerWidth`(1920)로 가로 스크롤 없음
  확인. 텍스트 요소 실제 렌더 크기도 확대 적용된 걸 `getBoundingClientRect`
  로 확인(예: 상단 통계 숫자 "128" 실제 렌더 높이 52.5px).

### 같은 세션 이어서 — 상단 검색창 복원

화면 폭이 넓어지자 사용자가 "원래 제목 줄 오른쪽에 검색창이 있었는데
복원해달라"고 요청(B/L·Container No·Item 조회 가능하도록 placeholder
포함). 확인해보니 현재 파일엔 검색창이 아예 없었음(과거 어느 시점에
빠진 것으로 추정, git 히스토리 미조사) — `.topnav`에 `.topnav-search`
(아이콘+input) 신규 추가, placeholder "B/L, Container No, Item 검색".
다른 mock 기능들과 같은 패턴으로 Enter 입력 시 `showToast`로 "아직
동작하지 않는 UI"라고 안내(실제 조회 로직 없음, §8.7 "화물 탭
controlbar의 통합 검색"과 같은 성격 — 화물 탭 것과 별개로 topnav
전역에도 있던 것을 복원한 것). 브라우저로 존재/placeholder/mock 토스트
동작 확인 완료, 1920px에서 가로 스크롤 없음 재확인.

### 같은 세션 이어서 — "그래프DB로 올리면 더 정확하지 않냐" 논의 → 다음 세션 예고

사용자 질문 "그래프DB에 올려서 분석하면 더 정확할거잖아, RAG와도 비슷한
효과 아니냐, Neo4j 연결할 수 있냐"에 답하면서 PRD §10에 이미 있던
"그래프DB·AIS·과거 정확도 이력 연동"이 "데이터가 있다면"이라는 미해결
전제였다는 걸 재확인시킴 → 그래프DB가 정확도를 높이는 게 아니라
"이미 있는 연결 데이터를 더 잘 탐색하게 해주는 도구"일 뿐이고, 지금
미해결인 건(PTA 이력 데이터, Stuffing List, Inland 마스터 데이터,
"리스크" 정의 등) 그래프DB로 안 풀린다고 설명 → 사용자가 명확히
정정: **"그 가정들은 지금 풀 수 있는 데이터가 없어서 가정한 거라 더
진행할 게 없다"**, 그래프DB 얘기는 별개로 **"합성 데이터가 아니라 더
많은 진짜 tracking data로 이번 세션에 검증한 Inbound 신뢰도 파이프라인을
다시 돌려보자"**는 제안이었음 — 필요한 CP_Vessel_List/뉴스는 사용자가
직접 찾아서 보충해줄 수 있다고 함. **다음 세션에 완전히 새로운 tracking
data를 제공할 예정** → 그 데이터부터 받아서 이어가면 됨(위 파일 맨 위
"세션 마지막에 나온 새 논의" 참고). 이번 세션은 여기서 마무리, 다음
대화창에서 계속하기로 함.

## 2026-08-09 세션 — PRD 1단계 정리 (무손실 중복 제거 + 성숙도 태그)

`PRD_수정지침.md`(사용자 작성)를 받아 `VisibilityControlTower_PRD.md`
v1.4 → **v1.5**로 정리. 지침의 1단계만 수행했고 2단계(논지 재배치)는
사용자 리뷰 대기 상태 — 지침이 두 단계를 한 커밋에 섞지 말라고 명시함.

**한 일**
- **성숙도 태그 도입**: `[검증]`(실데이터 확인) / `[설계]`(사양 확정,
  데이터 확보됨, 미구현) / `[가정]`(데이터 확보 여부 미확인) /
  `[구상]`(방향성만). 문서 맨 앞 "이 문서를 읽는 법"에 판별 기준 표를 둠.
- **중복 (A)~(I) 정본화**: PO 배제 근거→§5, raw data 샘플 한계→§8.2,
  FDEST ETA→Inbound 흐름→§8.4, P95 리스크→§8.4, 지연사유분석 2단
  구조→§7.1, 3-소스+2주 신선도→§8.6.1, AI가 ETA 임의변경 금지→§8.8,
  합성데이터 방침→§8.2. 나머지 위치는 전부 `(→ §X)` 한 줄 참조로 교체.
  각 개념이 문서에 정확히 한 번만 서술되는지 grep으로 확인함.
- **§10 재정의**: `영역 | 이슈(한 줄) | 유형 | 본문 참조` 4컬럼 색인표.
  유형은 `데이터 확보`/`설계 미정`/`범위 제외` 3종. 기존에 셀 하나가
  문단 길이였던 행(지연사유분석 검증 결과 등)의 서술은 §8.6.1 본문
  표로 옮김. 지침 1.3대로 "Items at Risk 지표 정의", "Pre-carriage를
  Planning Projection에 포함하는 규칙", "자체 ETA Prediction 모델" 행은
  본문에 태그로 이미 표시돼 삭제. AI Q&A 행은 §11 범위 제외로 이동.
- **§14 재정의**: 각 항목을 `작업명 + 완료 기준 + 본문 참조` 최대 2줄로.
- **본문 세션 날짜 표기 전부 제거**(헤더 개정 이력만 유지) — 결정 이력은
  이 PROGRESS.md가 담당한다는 원칙을 문서 앞머리에 명시.
- **깨진 상호참조 수정**: §7.1이 Inbound 인식 시점을 §8.3(Item×Date
  계산 원칙)으로 가리키던 것 → §8.4로, §1이 재고 계산식을 §8.4로
  가리키던 것 → §8.5로, §11이 "수요 생성 안 함"을 §8.4로 가리키던 것
  → §8.2로 정정.
- **§9 vessel-tracker 사실 정정 (지침에 없던 항목, 실제 코드와 상충)**:
  PRD가 아직 aisstream.io + Leaflet + "한국 해역 커버리지 없음 →
  도버해협 데모"로 적혀 있었으나 실제 코드는 2026-08-06 세션에 교체한
  **SeaVantage(SVMP) + Mapbox GL JS + 전세계 단일 MMSI 조회**. 현재
  구현 기준으로 다시 씀. 지침이 "§9 알려진 한계를 축약하지 말 것"이라
  했으므로 한계 서술은 같은 밀도로 유지하되 내용을 현재 것(폴링 주기
  종속, `range` 파라미터 단위 미확인, `.env` 미기입으로 실 연결 미검증)
  으로 교체. aisstream 이력은 한 줄 배경으로만 남김.
- **§8.10에 HTML 주석으로 검토 요청 삽입**: 지침 2.6(로드맵이 "발주
  의사결정"을 종착점으로 그리는 게 제품 정체성 선언으로 읽힌다)은
  제품 전략 판단이라 임의 변경하지 말라고 되어 있어 주석으로만 남김.

**목표 대비 결과 — 줄 수는 목표 미달(솔직히 기록)**
- 지침의 1단계 완료 기준은 "771줄 → 550줄 이하"였으나 실제 결과는
  **791줄**. 다만 문자 수 기준으로는 §10 재정의에서만 약 6,000자가
  줄었다(기존 §10은 셀 하나가 1,000자를 넘는 행이 여러 개라 **줄 수가
  아니라 문자 밀도로 비대했음** — 줄 수는 이 문서에서 좋은 지표가 아님).
- 줄 수가 안 줄어든 실제 이유: (1) 제거한 중복 (A)~(I)는 대부분 2~8줄
  단위라 합쳐도 ~60줄, (2) 그만큼을 성숙도 태그·태그 범례(17줄)·§9
  사실 정정(+7줄)·§10 4컬럼화가 도로 채움. 지침 2.1이 지적한 대로
  **남은 중복은 문체가 아니라 구조 문제**(정확도 관련 서술이 §7.1과
  §8.4/§8.6/§8.6.1 두 챕터에 흩어져 서로를 계속 참조)라, 실제 축소는
  2단계 통합에서 나온다. §7.1(72줄)+§8.4(56)+§8.6(12)+§8.6.1(54) =
  194줄이 2단계에서 한 장으로 합쳐질 대상.
- 정보 손실 없음 확인: 지침 0.1대로 판단·근거·수치를 삭제하지 않았고,
  "VGM 3/5", "HBL 6,829건", "MXZLO/MXLZC", "155건 중 87건(56%)",
  "126건(81%)", "Items at Risk 제외", "Booked Pipeline", "드레이지
  5~7일" 등 주요 수치·항목이 모두 남아 있는지 grep으로 확인함.

**미커밋** — 이번 변경분(`VisibilityControlTower_PRD.md`, 이 파일)도
아직 커밋 안 함(CLAUDE.md 규칙).

## 2026-08-09 세션(이어서) — PRD 2단계: 논지 재배치

사용자가 2단계 진행을 승인해 `PRD_수정지침.md` 2단계(논지 재배치)를 실행,
`VisibilityControlTower_PRD.md`를 **v1.5 → v2.0**으로 구조 변경. 정보
손실 없음을 grep으로 재확인(VGM 3/5, HBL 6,829건, MXZLO, 155건 중
87건/56%, 126건/81%, 드레이지, Booked Pipeline, Textract, Items at
Risk 등 전부 유지).

**핵심 변경 — 신설 §7 "도착 시점 정확도 (Arrival Accuracy)"**
기존에 두 챕터(§7 화물 탭, §8 Inventory)에 흩어져 서로를 `(→ §X)`로
참조하던 정확도 관련 5개 서브섹션을 한 장으로 통합:
- 구 §7.1 ETA/PTA → 신 §7.1
- 구 §7.1 지연 사유 분석 → 신 §7.2
- 구 §8.4 Inbound 인식 시점 및 반영 기준(전체) → 신 §7.3
- 구 §8.6 ETA Confidence → 신 §7.4
- 구 §8.6.1 Inbound 신뢰도 설명 Agent(전체) → 신 §7.5

이후 전체 챕터 번호가 밀림: Transportation §7→§8, Inventory §8→§9,
vessel-tracker §9→§10, 미해결 이슈 §10→§11, 범위제외 §11→§12, 벤치마크
§12→§13, 진행현황 §13→§14, 다음단계 §14→§15. 문서 전체의 상호참조
(`→ §X.X` 전부)를 새 번호에 맞게 갱신.

**이동 후 원래 자리 처리**
- 신 §8.1(화물 탭): ETA/PTA·지연 사유 분석 서브섹션 삭제, 리스트 구조·
  상태 3단계·지연 표시·선박 위치 연동만 남기고 방법론은 "(→ §7)" 한 줄.
- 신 §9.4(구 8.4 Inbound 인식 시점 자리): 전체 삭제하지 않고 "계산 참조"
  스텁으로 축소 — 방법론은 §7.3을 따른다는 한 줄 + Container-Item
  Mapping 계산표만 남김(§9.3 Item×Date 합산에서 바로 쓰는 표라 Inventory
  챕터에도 있는 게 실용적이라 지침 2.4가 명시적으로 요구한 예외).
- 신 §9(Inventory 목적 문단 뒤): §8.6/§8.6.1 자리는 완전히 삭제, §9.6
  화면구성에서 "(→ §7.5)"로만 참조.

**§2 문제 정의 재작성** (지침 2.2)
3번째 불릿을 "W&D가 기능이 없다"는 기능부재 서술에서 "그 판단 근거(선사
milestone·AIS·내부 오퍼레이션 상충 판정)가 포워더 안에만 있어 구조적으로
W&D가 못 푸는 문제"라는 서술로 교체.

**§9 도입부 책임 경계 신설** (지침 2.3)
Inventory 목적 문단 뒤에 인용 블록으로 "Projected Inventory 4변수 중
On-hand·Outbound·Safety Stock은 입력값, 본 서비스는 Inbound 시점만
책임진다"는 문장 추가. 이 내용이 흩어져 있던 §8.5(구) Outbound 불릿과
§11(구) 범위제외는 그대로 두되(둘 다 legitimate이라 지침도 완전 삭제를
요구하지 않음), §9.5 Outbound 불릿은 이 책임경계 문단을 참조하도록 축약.

**§9.6 화면 구성 보강** (지침 2.5)
"신뢰도 노출 강화 — 설계 필요" 소단락 신설, `[구상]` 태그로 3항목 기재
(Inbound 건별 신뢰도 1차 노출, Init ETA 갭 분포 위치, 소스 상충 시
채택값 표시). §15 다음 단계에 8번 항목으로 추가.

**§9.9 로드맵(구 §8.10)** — 지침 2.6대로 임의 변경 안 하고 기존 HTML
주석(검토 요청)만 유지.

**줄 수**: 791줄 → **834줄**로 오히려 늘어남(목표는 "450줄 내외"였음).
1단계 때와 같은 이유 — 신설 §7 자체가 헤더·인트로 문단을 새로 갖고,
§9.4 스텁·§9.6 신규 소단락·§15 신규 항목이 추가됨. 다만 이번 결과는
지침 2.7의 정성적 완료 기준(정확도 서술이 §7 한 곳에 모여 있고 §8/§9는
소비처로만 읽힘, §2가 "왜 포워더가 풀어야 하는가"에 답함, §10(구) 약점
중복 없음)은 충족했다고 판단 — grep으로 §8.1/§9에 ETA/PTA·지연사유분석·
ETA Confidence·신뢰도Agent 서술이 안 남아있음을 확인함. 줄 수 목표는
이번에도 미달이지만, 지침이 제시한 두 기준(정성적 구조 vs 줄 수) 중
구조적 기준을 우선 충족시킨 결과로 판단하고 사용자에게 그대로 보고.

**미커밋** — 이번 변경분도 계속 미커밋 상태(CLAUDE.md 규칙).

## 2026-08-09 세션(이어서 3) — PRD 사용자 리뷰 피드백 반영 (v2.0 → v2.1)

사용자가 2단계 재배치본(v2.0)을 직접 읽고 준 피드백을 반영. 확정 지시는
바로 적용, 판단이 필요한 3건(§9.7 가설 문구, §9.8 로드맵 명확성, §13/§14
PRD 존치 여부)은 본문에 HTML 주석으로 재검토 표시만 하고 사용자에게
질문으로 넘김(→ 다음 세션에서 답 받으면 반영).

**적용한 변경**
- **§2 3번째 불릿 표현 수정**: "그 근거가 포워더 안에만 존재하는 정보다"
  → "그 판단은 포워딩 실무를 아는 담당자만 할 수 있다"로. 사용자가
  "포워더 안에만 존재한다"는 표현이 어색하다고 지적 — 데이터 소재
  프레이밍에서 판단 주체 프레이밍으로 바꿈.
- **§5 백본 다이어그램에 Outbound 추가**: 기존엔 Inbound(→On-hand)만
  그려져 있어 비대칭이었음. `↓ Inbound(+)` / `↑ Outbound(−, 고객
  시스템에서 별도 발생)`로 양쪽 다 표기, 설명 문장 추가.
- **§6 탭 구조 다이어그램 "비용" 라인 수정**: "D&D·PCS 등 비용 리스크" →
  "월별 물류비 현황 + D&D 등 비용 리스크". PCS를 헤드라인에서 뺌.
- **§8.3 비용 탭 전면 재작성**: 기존엔 `[구상] — 화면 설계 착수 전`이라고
  써 있었는데 실제로는 PROGRESS.md에 이미 "월별 물류비 현황"·"D&D 통합
  리스트" 목업 반영 완료·"PCS는 확정 항목에서 제외, 후보로 재분류"까지
  결정돼 있었음(2026-08-04 세션 결정, PRD에 반영이 안 돼 있던 것을 이번에
  발견). PROGRESS.md 근거로 정정: 월별 물류비 현황/D&D를 `[설계]`(목업
  반영완료)로, PCS는 `[구상]`(확정 항목 아님, 발생 시 월별 현황의 항목
  하나로만 반영)으로 재작성.
- **§6 화면 텍스트 언어 규칙 축약**: 업계 용어 목록(Pre-carriage 등)을
  풀어 쓴 문단 대신 "상세 기준은 CLAUDE.md에 있다"는 포인터로 축약,
  PRD 고유 결정(하위 탭 한글 명칭)만 남김 — CLAUDE.md가 이미 이 규칙의
  정본이라 PRD에 전문 반복은 불필요하다고 판단.
- **"FDEST Init. ETA" → "Initial FDEST ETA"로 용어 통일**: §7.3, §9.2
  데이터소스 표, §9.5(구 9.6) 드릴다운 체인 3곳 전부 교체. 짧은 구어체
  "Init ETA"(§7.5 당겨짐 케이스 등)는 축약형으로 남김.
- **§9.1 dangling 참조 제거**: "이 샘플의 한계는 → §9.2" 구절 삭제(아래
  §9.2 블록 삭제에 따라).
- **§9.2 데이터 소스 인트로 재작성 + "raw data 샘플의 한계" 블록 삭제**:
  사용자가 "이건 현재 확보 가능한 데이터 전체가 아니라 검증에 필요하다고
  판단해 일부만 가져온 것"이라고 정정 — 인트로 문장을 "현재 시스템에
  존재하는 데이터 전체가 아니라 파일럿 검증에 필요하다고 판단해 선별한
  항목이다"로 교체. raw data 샘플의 대표성 한계를 경고하던 블록쿼트는
  사용자 지시로 전체 삭제(이 안전장치는 이미 내 memory
  `raw_data_not_representative.md`에도 별도로 저장돼 있어 PRD에서 빠져도
  향후 세션에서 잊혀지지 않음).
- **§9.3(구, Item×Date 계산 원칙) 섹션 삭제 → §9.4(재고 계산)에 한 줄로
  병합**: 사용자가 "뻔한 내용 아닌가, 굳이 설명이 필요해?"라고 지적 —
  Σ Inbound(≤t) 표기 자체가 이미 날짜별 합산을 내포하므로 별도 절로 4행
  예시 표까지 쓸 필요는 없다고 판단해 동의, 첫 문장 하나로 축약해 재고
  계산식 절 안에 흡수. 이에 따라 §9.4~§9.9(구)가 §9.3~§9.8로 한 칸씩
  당겨짐 — 문서 전체의 해당 참조를 모두 갱신(§7.3/§7.5/§8.5/§9/§11/§14
  등 총 15곳 이상).
- **§13(시장 벤치마크) 섹션 전체 삭제**: 사용자 지시. 이에 따라 §14(진행
  현황)→§13, §15(다음 단계)→§14로 당겨짐, 관련 참조 갱신.

**질문으로 넘긴 것 (본문에 HTML 주석 표시, 답변 대기)**
1. **§7.2 요약 확인** — 사용자가 "상충 정보 중 상황에 더 부합하는 정황
   증거를 신뢰하는 방향, 이를 위해 지연 사유 분석이 필요"라고 요약한 것에
   동의하되, 2단 구조(정적 신뢰도=과거 이력 통계/AI 불필요 vs 건별
   보정=정황증거 판단/AI 필요) 중 사용자 요약은 주로 건별 보정 쪽을
   설명한다는 점을 답변으로 짚어줌 — §7.2 본문 자체는 이미 이 요약과
   합치해 보여 편집은 안 하고 "핵심은 단순하다" 한 줄만 §7.2 도입부에
   추가.
2. **§9.7(구 9.8) MVP 가설 문구** — "당연한 내용 아닌가, MVP에서 뭘
   한다는거지"라는 지적. 가설이 "결합하면 가치가 있냐"는 자명한 형태라
   실제 검증 대상이 불분명함. HTML 주석으로 후보 3가지(데이터 품질/커버리지
   충분성, 더 이른 가시성이 실제 행동을 바꾸는지, 신뢰도 설명이 믿을 만한지)
   남기고 사용자 확인 후 재작성 예정.
3. **§9.8(구 9.9) 로드맵 명확성** — "9.9도 뭘 한다는 건지 잘 모르겠어"라는
   지적. 기존에 이미 Target Vision 화살표 방향에 대한 검토 요청 주석이
   있었는데(§8.10→§9.9→§9.8), 이번엔 그와 별개로 각 단계(Next/Advanced)
   자체가 구체 산출물이 아니라 방향성 라벨로만 쓰여 불명확하다는 새 지적 —
   별도 HTML 주석 추가.
4. **§13(구 진행현황)/§14(구 다음단계)가 PRD에 필요한가** — 사용자 질문,
   아직 답변 못 받음. 이 둘은 "살아있는 상태/할일" 성격이라 PROGRESS.md와
   역할이 겹친다는 논지일 수 있음 — 다음 세션에서 답 받고 처리.

**버전**: v2.0 → **v2.1**(837줄). 정보 손실 없음 재확인(6,829건/MXZLO/
155건 중 87건/126건/드레이지/Booked Pipeline/Textract 등 grep 확인).

**미커밋** — 계속 미커밋 상태.

## 2026-08-09 세션(이어서 4) — PRD §9.7/§11/§13·§14 후속 처리 (v2.1 → v2.2)

직전 리뷰 피드백 반영(v2.1)에서 질문으로 남겨둔 3건 중 사용자가 2건에
답을 줌 — §9.7 MVP 가설 방향, §13/§14 PRD 존치 여부. §9.8(구 발전방향)
로드맵 명확성은 이번에도 별개 의견(§11 모니터링 제안)만 왔고 직접 답은
아직 없어 그대로 대기 상태로 남김.

- **§9.7(MVP에서 검증하려는 것 → MVP로 증명하려는 것) 재작성**: 사용자
  답변 — "Inbound가 재고관리에 도움이 되는 것을 증명하는 것이고, 고객에게
  더 어필하려면 ETA 정확도를 올리는 게 얼마나 중요한지 주지시키는 것".
  기존 "가설을 검증한다"(불확실성을 확인하는 프레이밍)에서 "가치를
  증명해서 §7(도착 시점 정확도)에 투자할 근거를 만든다"(설득 목적
  프레이밍)로 전환. 재검토 필요 HTML 주석 제거(질문 해소).
- **§11(미해결 이슈) 인트로에 모니터링 문장 추가**: 사용자 제안 — `[가정]`
  영역이 언제 실현화 가능한지 지속 모니터링이 중요하다는 지적. §11의
  "데이터 확보" 유형 행이 곧 `[가정]`→`[검증]`/`[설계]` 승격 조건 목록
  이라는 문장을 추가해, 이 표 자체가 그 모니터링 리스트 역할을 하도록
  명시. 이 습관을 PROGRESS.md "다음 단계"에도 운영 항목으로 기록.
- **§13(진행현황)·§14(다음단계) PRD에서 완전 삭제**: 사용자가 "PROGRESS.md에
  들어가는 게 더 어울리지 않냐"고 묻고 "PRD가 더 어울리면 유지해도 된다"고
  판단을 위임 — 검토 결과 PRD에 남기지 않기로 결정. 근거: (1) 둘 다 자주
  바뀌는 "현재 상태" 정보라 PRD(사양 문서)의 성격과 안 맞음, (2) 특히
  §14 "다음 단계"는 CLAUDE.md가 이미 PROGRESS.md를 그 정본으로 못박아둔
  구조(세션 시작 시 PROGRESS.md "다음 단계"부터 읽는다)라 PRD에 같은
  이름의 섹션을 또 두면 단일 출처 원칙(지침 0.3)에 정면으로 위배됨. PRD는
  이제 §12(범위 제외)에서 끝남 — §9.5 안의 유일한 외부 참조(신뢰도
  노출강화 항목)는 "PROGRESS.md 다음 단계 참고"로 수정. 이관된 두 섹션의
  실제 내용(상태 표 6행 + 다음단계 9항목)은 위 "다음 단계" 섹션에 기존
  목록과 합쳐 중복 없이 통합함(정보 손실 없음).
- **버전**: v2.1 → **v2.2**(804줄). grep으로 §13/§14에 대한 살아있는
  상호참조가 없음을 재확인(버전 헤더의 이관 설명 문구 1건만 남고 실제
  섹션 참조는 0건).

**미커밋** — 계속 미커밋 상태.

## 2026-08-09 세션(이어서 5) — PRD §9.8 삭제 (v2.2 → v2.3)

사용자가 "9.8이 꼭 필요해?"라고 질문 — 직전 세션에서 두 번이나 명확화를
요청했지만 답을 안 준 것 자체가 신호였다고 보고, 필요성을 재검토한 결과
동의해 섹션 자체를 삭제.

**판단 근거**: §9.8("MVP 이후 발전 방향")은 Next/Advanced/Target Vision
3단계를 방향성 라벨로만 나열한 로드맵이었고, 태그 체계상으로도 전부
`[구상]`(방향성만 있음)이라 PRD가 요구사항으로 규정하는 것이 사실상
없었음. 유일하게 실질적인 문장은 "발주 실행(PO 생성·공급처 전달·Booking)
자체는 범위 밖"이라는 스코프 제외 선언 하나뿐이었는데, 이건 애초에
§12(범위 제외)에 있어야 할 내용이 로드맵 다이어그램 안에 잘못 끼어
있었던 것.

**처리**: §9.8 섹션 전체(로드맵 다이어그램 + 재검토 필요 주석 2개) 삭제.
"발주 실행은 범위 밖"이라는 스코프 선언만 §12(범위 제외)에 새 불릿으로
이동. §9 Inventory 도입부·§7.3(PTA 듀얼 표시 유예)·§11(재고관리 Agent
범위, POD 양하 우선순위 두 행)에 있던 `(→ §9.8)` 참조는 각각 §12 또는
"미래 과제" 같은 일반 표현으로, 혹은 그냥 §9(Inventory 도입부 자체)로
갱신. §9는 이제 §9.1~§9.7까지만 있음.

**버전**: v2.2 → **v2.3**(775줄). §9.8/Target Vision 문자열 완전 삭제
확인, 나머지 §X 참조가 전부 실제 존재하는 섹션을 가리키는지 grep 재검증.

**미커밋** — 계속 미커밋 상태.

## 2026-08-09 세션(이어서 6) — 문서 정리 커밋 + 배포

사용자 요청("여기까지 문서 정리하고 배포까지 해줘")에 따라 이번 세션의
PRD 재작업분을 커밋·푸시함(이 프로젝트에서 "배포" = GitHub push, 별도
호스팅 파이프라인 없음).

- **커밋 범위를 의도적으로 좁힘**: `git status`에 이번 세션과 무관한
  변경분(`vessel-tracker/*` — SeaVantage 전환, `visibility_control_tower_
  mockup.html` — Inbound 신뢰도 Agent 프로토타입, 둘 다 이전 세션 작업)이
  같이 잡혀 있었으나 "문서 정리" 범위가 아니라고 판단해 제외. `PROGRESS.md`
  / `VisibilityControlTower_PRD.md` / `PRD_수정지침.md` 3개 파일만 스테이징.
- **`raw data/`는 커밋 자체를 보류**: 이 폴더는 실 고객 샘플 데이터 4개
  Excel 파일(1.2MB, `Tracking.xlsx` 등)이고 origin(`github.com/
  ChoYoungDae/VisibilityControlTower`)이 공개 저장소로 보여서, 확인 없이
  올리면 안 될 수 있다고 판단해 add하지 않음 — 커밋 여부는 사용자 확인
  후 결정.
- **커밋 `21518af`** — "Restructure PRD around a new Arrival Accuracy
  chapter, per PRD_수정지침.md". `git push origin master` 실행, 이전에
  밀려 있던 커밋 2개(`0b8b37f`/`5b022aa`, 2026-08-08 세션에서 이미 커밋만
  하고 안 밀었던 것)도 같이 나감. Fast-forward push, force 불필요.

## 2026-08-09 세션(이어서 7) — vessel-tracker/mockup 커밋 + SeaVantage whitelist 이슈 확인

`vessel-tracker/*`(SeaVantage 전환, 2026-08-06 세션)와
`visibility_control_tower_mockup.html`(Inbound 신뢰도 Agent 프로토타입,
2026-08-08 세션)을 별도 커밋으로 처리. 커밋하면서 사용자가 새 정보 제공:
**SeaVantage API 계정이 whitelist에 등록되지 않아 현재 호출 자체가
불가능**하다 — 단순히 `.env`에 계정정보를 안 채운 상태가 아니라, 계정을
채워도 SeaVantage 측 whitelist 등록이 먼저 돼야 쓸 수 있는 상태.
`VisibilityControlTower_PRD.md` §10(vessel-tracker) "알려진 한계"의 관련
불릿을 이 사실로 정정(v2.3 → v2.4). `raw data/`는 이전 세션에서 확인한
대로 이번에도 커밋하지 않음(공개 저장소 확인 전까지 보류, 사용자가
"잘했어"로 그 판단 확인).
