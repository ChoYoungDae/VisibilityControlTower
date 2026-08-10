# API (컨셉 데모)

`db/visibility_control_tower.db`(SQLite)를 읽어서 `visibility_control_tower_
mockup.html`이 지금까지 하드코딩해서 쓰던 JS 데이터 객체와 같은 모양의 JSON을
돌려준다. 목업의 렌더링 로직은 거의 그대로 두고 "데이터 출처만" 하드코딩에서
API로 바꾸는 게 목표였다.

## 실행

```bash
pip install fastapi "uvicorn[standard]"   # 최초 1회
cd api
uvicorn main:app --reload --port 8000
```

`db/build_db.py`를 먼저 실행해 `db/visibility_control_tower.db`가 있어야 한다.
API 문서는 `http://localhost:8000/docs`(FastAPI 자동 생성).

`.claude/launch.json`에도 `"api"` 항목이 등록돼 있어, Claude Code의 미리보기
도구로 목업 정적 서버(`mockup-static`, 8123)와 이 API(8000)를 각각 띄우면 된다
— 순서는 상관없다(목업이 fetch 실패 시 화면에 빨간 경고 배너를 띄우고 콘솔에
안내 메시지를 남기도록 만들어뒀다).

## 엔드포인트

| 엔드포인트 | 목업의 옛 하드코딩 대응 |
|---|---|
| `GET /api/cargo/tracking` | 화물 탭 `rowData` |
| `GET /api/cargo/section-stats` | 화물 탭 `sectionStats` |
| `GET /api/cargo/vessel-mmsi` | 화물 탭 `VESSEL_MMSI` |
| `GET /api/operation/bookings` | 업무 탭 `bookingData` |
| `GET /api/operation/arrivals` | 업무 탭 `arrivalData` |
| `GET /api/operation/schedule-search` | Port-to-Port 스케줄 조회 예시(아직 화면 미연동, 정적 HTML 유지) |
| `GET /api/cost/dnd` | 비용 탭 `dndData` |
| `GET /api/cost/monthly` | 월별 물류비(아직 화면 미연동, SVG 차트는 정적 HTML 유지) |
| `GET /api/inventory/items` | 재고 탭 `itemCatalog` |
| `GET /api/inventory/reorder-recommendation` | 신규 — Item별 발주 시점/수량 추천 |
| `GET /api/inventory/reorder-recommendation/{item_id}` | 위의 단건 조회 |

## 화면 연동 범위 (지금 한 것 / 다음에 할 것)

**연동 완료**: 화물/업무/비용 탭의 detail 패널(클릭 시 열리는 상세 정보)과
재고 탭 전체(`itemCatalog` 기반 Item 리스트·재고 투영 차트·입고 예정 리스트
전부 이 데이터 하나로 구동됨) + 신규 "발주 시점/수량 추천" 배너(Item 상세
화면에 재고 투영 배너 바로 아래 표시).

**아직 정적 HTML로 남아있는 것** (다음 단계 후보, 의도적으로 이번 범위에서
제외함):
- 화물/업무/비용 탭의 **리스트 행 자체**(컨테이너 목록, 부킹 목록, D&D 목록) —
  단계별(Pre/Main/On-carriage)로 컬럼 구성이 달라지는 손으로 짠 HTML 템플릿이라,
  API로 완전히 대체하려면 그 템플릿 로직을 JS로 옮겨야 한다. 지금은 detail
  패널(클릭했을 때 나오는 정보)만 API 기반이고, 행 목록 자체는 그대로 정적.
- 비용 탭 **월별 물류비 SVG 차트**(막대+선) — 픽셀 좌표로 손으로 그려져 있어
  API 데이터(`monthly_cost.csv`)로 재구성하려면 차트를 SVG 생성 로직으로 다시
  짜야 한다.
- 업무 탭 **Port-to-Port 스케줄 조회 결과**(정적 예시 3건) — API는 이미 있음
  (`GET /api/operation/schedule-search`), 화면 연동만 안 함.

이 세 가지는 시각적으로 복잡한 템플릿이라 "컨셉 증명"이라는 이번 목표를 넘어서는
작업량이라 판단해 범위에서 뺐다 — 필요하면 다음 세션에 이어서 하면 된다.

## CORS

목업(8123)과 API(8000)가 다른 오리진이라 CORS를 전체 허용(`allow_origins=["*"]`)
해뒀다 — 컨셉 데모 한정, 프로덕션에서는 좁혀야 한다.
