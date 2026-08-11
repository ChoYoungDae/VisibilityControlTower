-- Visibility Control Tower — Postgres(Supabase) 스키마 (컨셉 데모)
-- db/schema.sql(SQLite)을 Postgres 문법으로 옮긴 버전. 테이블 구조는 동일하고
-- AUTOINCREMENT만 GENERATED ALWAYS AS IDENTITY로 바꿨다. 자세한 배경은
-- db/schema.sql 상단 주석 참고.
--
-- 도메인 3개:
--   1) Inventory   (재고 탭 — PRD §9)
--   2) Transportation (화물/업무/비용 탭 — PRD §8)
--   3) Reorder Recommendation (신규 컨셉)

-- =============================================================
-- 1. Inventory 도메인
-- =============================================================

CREATE TABLE item (
  item_id      TEXT PRIMARY KEY,
  item_name    TEXT NOT NULL,
  product_type TEXT,
  source       TEXT NOT NULL  -- REAL_MODEL_VALUE | SYNTHETIC_ITEM
);

CREATE TABLE inventory_onhand (
  item_id       TEXT NOT NULL REFERENCES item(item_id),
  snapshot_date TEXT NOT NULL,
  on_hand_qty   INTEGER NOT NULL CHECK (on_hand_qty >= 0),
  source_type   TEXT NOT NULL,
  PRIMARY KEY (item_id, snapshot_date)
);

CREATE TABLE inventory_safety_stock (
  item_id           TEXT NOT NULL REFERENCES item(item_id),
  effective_date    TEXT NOT NULL,
  safety_stock_qty  INTEGER NOT NULL CHECK (safety_stock_qty >= 0),
  source_type       TEXT NOT NULL,
  PRIMARY KEY (item_id, effective_date)
);

CREATE TABLE inventory_outbound (
  item_id       TEXT NOT NULL REFERENCES item(item_id),
  outbound_date TEXT NOT NULL,
  outbound_qty  INTEGER NOT NULL CHECK (outbound_qty >= 0),
  source_type   TEXT NOT NULL,
  PRIMARY KEY (item_id, outbound_date)
);

-- Item 단위 Inbound 화물(Container-Item Mapping). container_no가 NULL이면
-- Pre-carriage 플레이스홀더(계산 제외 대상, §9.3).
CREATE TABLE item_shipment (
  shipment_row_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  item_id         TEXT NOT NULL REFERENCES item(item_id),
  container_no    TEXT,
  po_no           TEXT,
  mode            TEXT NOT NULL,        -- sea | air
  stage_label     TEXT NOT NULL,        -- Pre-carriage | Main-carriage | On-carriage
  qty             INTEGER NOT NULL CHECK (qty >= 0),
  fdest_init_eta  TEXT,
  fdest_eta       TEXT,
  wh_in_date      TEXT,
  delayed         INTEGER NOT NULL DEFAULT 0,  -- 0/1
  source_type     TEXT NOT NULL
);
CREATE INDEX idx_item_shipment_item_eta ON item_shipment(item_id, fdest_eta);

-- =============================================================
-- 2. Transportation 도메인
-- =============================================================

CREATE TABLE vessel_mmsi (
  vessel_name TEXT PRIMARY KEY,
  mmsi        TEXT NOT NULL,
  source_type TEXT NOT NULL
);

CREATE TABLE cargo_tracking (
  id                TEXT PRIMARY KEY,
  mode              TEXT NOT NULL,   -- sea | air
  stage             TEXT NOT NULL,   -- pre | main | on
  cid               TEXT NOT NULL,   -- Container No 또는 HBL
  bl                TEXT,
  po                TEXT,
  service_note      TEXT,
  pol               TEXT,
  pod               TEXT,
  planned_vf        TEXT,
  current_vf        TEXT,
  pod_vf            TEXT,
  initial_pol_etd   TEXT,
  pol_etd           TEXT,
  ts_count          INTEGER,
  carrier_eta       TEXT,
  pta_p50           TEXT,
  pta_p95           TEXT,
  fdest_eta         TEXT,
  dnd_lfd           TEXT,
  status_label      TEXT,
  delayed           INTEGER NOT NULL DEFAULT 0,
  badge_color       TEXT,      -- 화면 뱃지 색상(neutral/ok/warn/crit) — 원본 표시값 그대로 보존
  route_display     TEXT,      -- 목업 detail 패널의 원본 노선 문구 그대로 보존
  source_type       TEXT NOT NULL
);

CREATE TABLE cargo_section_stats (
  scope       TEXT NOT NULL,  -- sea | air
  stage       TEXT NOT NULL,  -- pre | main | on
  total       INTEGER NOT NULL,
  delayed     INTEGER NOT NULL,
  source_type TEXT NOT NULL,
  PRIMARY KEY (scope, stage)
);

CREATE TABLE booking (
  booking_no      TEXT PRIMARY KEY,
  cid             TEXT,
  route           TEXT,
  stage           TEXT,
  status          TEXT,
  si_cutoff       TEXT, si_note TEXT, si_class TEXT,
  vgm_cutoff      TEXT, vgm_note TEXT, vgm_class TEXT,
  cy_cutoff       TEXT, cy_note TEXT, cy_class TEXT,
  export_customs  TEXT,
  bl_status       TEXT,
  bl_no           TEXT,
  rollover        INTEGER NOT NULL DEFAULT 0,
  source_type     TEXT NOT NULL
);

CREATE TABLE booking_po (
  booking_no  TEXT NOT NULL REFERENCES booking(booking_no),
  po_no       TEXT NOT NULL,
  source_type TEXT NOT NULL,
  PRIMARY KEY (booking_no, po_no)
);

CREATE TABLE arrival_prep (
  cid                     TEXT PRIMARY KEY,
  po                      TEXT,
  route                   TEXT,
  status                  TEXT,
  import_customs          TEXT,
  customs_expected_or_done TEXT,
  customs_expected        TEXT,
  locked                  INTEGER NOT NULL DEFAULT 0,
  locked_msg              TEXT,
  source_type             TEXT NOT NULL
);

CREATE TABLE inland_routing_option (
  option_row_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cid            TEXT NOT NULL REFERENCES arrival_prep(cid),
  mode           TEXT NOT NULL,
  lead_time      TEXT,
  cost           TEXT,
  free_time      TEXT,
  recommendation TEXT,
  selected       INTEGER NOT NULL DEFAULT 0,
  source_type    TEXT NOT NULL
);

CREATE TABLE schedule_search_result (
  result_row_id       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  carrier             TEXT NOT NULL,
  vessel              TEXT NOT NULL,
  pol_etd             TEXT,
  pod_eta             TEXT,
  lead_time_days      INTEGER,
  ts_count            INTEGER,
  carbon_tco2e_per_teu REAL,
  source_type         TEXT NOT NULL
);

CREATE TABLE dnd (
  id             TEXT PRIMARY KEY,
  cid            TEXT,
  po             TEXT,
  route          TEXT,
  status         TEXT,
  free_time_expiry TEXT,
  days_remaining INTEGER,
  days_elapsed   INTEGER,
  daily_rate     INTEGER,
  pending        INTEGER NOT NULL DEFAULT 0,
  badge_color    TEXT,
  source_type    TEXT NOT NULL
);

CREATE TABLE dnd_weekly_bucket (
  dnd_id      TEXT NOT NULL REFERENCES dnd(id),
  week_index  INTEGER NOT NULL,
  days        INTEGER NOT NULL,
  source_type TEXT NOT NULL,
  PRIMARY KEY (dnd_id, week_index)
);

CREATE TABLE monthly_cost (
  month       TEXT PRIMARY KEY,  -- 'YYYY-MM'
  freight     INTEGER NOT NULL,
  dnd         INTEGER NOT NULL,
  other       INTEGER NOT NULL,
  teu         INTEGER,
  total       INTEGER NOT NULL,
  note        TEXT,
  source_type TEXT NOT NULL
);

-- =============================================================
-- 3. 리드타임 / 발주 추천 (신규 컨셉)
-- =============================================================

CREATE TABLE shipment_history (
  history_id     TEXT PRIMARY KEY,
  lane_id        TEXT NOT NULL,
  pol            TEXT NOT NULL,
  pod            TEXT NOT NULL,
  carrier        TEXT NOT NULL,
  mode           TEXT NOT NULL,
  pol_atd        TEXT NOT NULL,
  fdest_ata      TEXT NOT NULL,
  lead_time_days INTEGER NOT NULL,
  is_outlier     INTEGER NOT NULL DEFAULT 0,
  source_type    TEXT NOT NULL
);
CREATE INDEX idx_shipment_history_lane ON shipment_history(lane_id);

CREATE TABLE lead_time_stats (
  lane_id     TEXT PRIMARY KEY,
  pol         TEXT NOT NULL,
  pod         TEXT NOT NULL,
  carrier     TEXT NOT NULL,
  mode        TEXT NOT NULL,
  n           INTEGER NOT NULL,
  mean_days   REAL NOT NULL,
  std_days    REAL NOT NULL,
  p50_days    INTEGER NOT NULL,
  p95_days    INTEGER NOT NULL,
  source_type TEXT NOT NULL
);

-- Item -> 대표 Lane 매핑 (컨셉 데모 가정, §9.1의 실제 Container-Item Mapping을
-- 대체하지 않음 — synthetic-data/README.md 참고)
CREATE TABLE item_primary_lane (
  item_id         TEXT PRIMARY KEY REFERENCES item(item_id),
  lane_id         TEXT NOT NULL REFERENCES lead_time_stats(lane_id),
  assumption_note TEXT,
  source_type     TEXT NOT NULL
);

-- 계산 결과 (seed_supabase.py가 재고 투영 + 리드타임 통계를 결합해 채움).
-- 결정론적 계산 결과이며 별도 ML 모델 학습 결과가 아니다(§9.6 원칙과 동일:
-- 핵심 계산은 결정론적으로, AI/통계는 리드타임 분포 산출에만 관여).
CREATE TABLE reorder_recommendation (
  item_id                  TEXT PRIMARY KEY REFERENCES item(item_id),
  target_event             TEXT NOT NULL,   -- Risk | Shortage | None
  target_date              TEXT,
  recommended_qty          INTEGER,
  lane_id                  TEXT REFERENCES lead_time_stats(lane_id),
  lead_time_p50_days       INTEGER,
  lead_time_p95_days       INTEGER,
  recommended_order_by_date TEXT,
  days_until_order_by       INTEGER,  -- 음수면 이미 발주 시점을 지났다는 뜻(urgent)
  urgency                  TEXT NOT NULL,  -- urgent | normal | none
  -- "오늘(기준일) 발주하면 언제 도착하나" — urgent(이미 권장 시점을 지난 경우)여도
  -- 답할 수 있어야 해서 별도로 계산해 저장한다(§9.4 target_date와는 별개 값).
  if_ordered_today_arrival_p50 TEXT,
  if_ordered_today_arrival_p95 TEXT,
  computed_at              TEXT NOT NULL
);
