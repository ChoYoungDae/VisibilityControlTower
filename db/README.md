# DB + API (컨셉 데모)

**2026-08-10 세션에 API 계층(`api/main.py`, FastAPI) 추가 완료** — 목업
(`visibility_control_tower_mockup.html`)이 이제 이 DB를 실제로 읽어서
렌더링한다. 아래는 DB 자체 설명이고, API/화면 연동은 `api/README.md`
참고.


`synthetic-data/*.csv` 전체를 SQLite 하나에 적재하고, "재고 투영 + 노선별
리드타임 P95를 결합한 발주 시점/수량 추천"을 계산해 보여주는 컨셉 데모다.
프로덕션 스키마가 아니라, 이 조합이 실제로 동작한다는 걸 증명하는 게 목적.

## 실행

```bash
cd db
python build_db.py
```

`visibility_control_tower.db`(SQLite 파일)를 매번 새로 만든다(기존 파일은
삭제 후 재생성 — 재실행해도 안전). `synthetic-data/reorder_recommendation.csv`도
같이 갱신된다.

## 구성

- `schema.sql` — 3개 도메인 테이블 정의
  1. Inventory(재고 탭, §9): `item`/`inventory_onhand`/`inventory_safety_stock`/`inventory_outbound`/`item_shipment`
  2. Transportation(화물/업무/비용 탭, §8): `cargo_tracking`/`booking`/`arrival_prep`/`dnd`/`monthly_cost` 등
  3. 리드타임/발주 추천(신규 컨셉): `shipment_history`/`lead_time_stats`/`item_primary_lane`/`reorder_recommendation`
- `build_db.py` — CSV 적재 후 `reorder_recommendation`을 계산해 채움:
  1. Item별 Projected Inventory를 §9.4 공식 그대로 일자별 계산(결정론적, ML 아님)
  2. 처음으로 Safety Stock 이하(Risk) 또는 0 이하(Shortage)가 되는 날짜·부족 수량을 찾음
  3. 그 Item의 대표 노선(`item_primary_lane`) 리드타임 P95를 그 날짜에서 역산 → 권장 발주 시점
  4. 오늘(기준일) 기준으로 이미 그 시점을 지났으면 `urgency=urgent`

## 컨셉 데모로서의 한계 (다음 단계에서 다듬을 것)

- **Item→노선 매핑이 가정값**이다(`item_primary_lane.csv`) — 실제로는 Item마다
  여러 노선/공급처가 섞여 있을 수 있고, PRD §9.1의 실제 Container-Item
  Mapping을 써야 한다.
- **리드타임이 Transportation 구간(POL ATD→FDEST ATA)만 반영**한다 — 실제
  "발주"부터 도착까지는 여기에 공급처 생산·부킹 리드타임이 더 붙는다.
- **부족 수량 계산이 "처음 임계값 아래로 내려가는 순간의 부족분"만 본다** —
  이후 추가로 벌어지는 부족(예: REFRIGERATOR처럼 Risk 진입 시점엔 부족분이
  0이지만 이후 계속 벌어지는 경우)까지는 반영하지 않는 단순화 버전이다.
- 지금 mock 시나리오는 전부 "기준일(2026-08-07)로부터 며칠 안에 Risk/Shortage"
  로 설계돼 있어서, 리드타임(25~45일)보다 훨씬 짧다 — 그 결과 대부분 Item이
  `urgent`(이미 발주 시점을 지남)로 나온다. 실제 데이터라면 이보다 다양한
  분포가 나올 것 — 이 자체가 "버그"는 아니고 데모 데이터의 설계 특성이다.
