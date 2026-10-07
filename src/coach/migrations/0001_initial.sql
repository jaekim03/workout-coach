-- Initial schema (DESIGN §4). Never edit a merged migration; add a new one.

CREATE TABLE profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  goal TEXT NOT NULL CHECK (goal IN ('strength','hypertrophy','general')),
  training_age_months INTEGER NOT NULL,
  days_per_week INTEGER NOT NULL CHECK (days_per_week BETWEEN 2 AND 6),
  session_minutes INTEGER NOT NULL,
  display_unit TEXT NOT NULL DEFAULT 'kg' CHECK (display_unit IN ('kg','lb')),
  priority_muscles TEXT,              -- JSON array of muscle names (§4 muscle list), optional
  sex TEXT, birth_year INTEGER, height_cm REAL, bodyweight_kg REAL,
  updated_at TEXT NOT NULL
);

CREATE TABLE equipment (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,          -- barbell, dumbbell, cable, machine, pullup_bar, bench, rack (seed adds more: D-56)
  available INTEGER NOT NULL DEFAULT 1,
  increment_kg REAL                   -- smallest load jump (dumbbell: per hand)
);

CREATE TABLE exercise (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  movement_pattern TEXT NOT NULL CHECK (movement_pattern IN
    ('squat','hinge','h_push','v_push','h_pull','v_pull','lunge','core','isolation')),
  equipment_id INTEGER REFERENCES equipment(id),
  load_type TEXT NOT NULL CHECK (load_type IN ('external','bodyweight')),
  unilateral INTEGER NOT NULL DEFAULT 0,
  stretch_bias INTEGER NOT NULL DEFAULT 0   -- 1 = loads the muscle at long length; agent tie-breaker only (E-low)
);

CREATE TABLE exercise_muscle (        -- fractional volume map (E-mod: Pelland 2025)
  exercise_id INTEGER NOT NULL REFERENCES exercise(id),
  muscle TEXT NOT NULL CHECK (muscle IN ('chest','back','quads','hamstrings','glutes',
         'side_delts','rear_delts','front_delts','biceps','triceps','calves','abs')),
  weight REAL NOT NULL CHECK (weight IN (1.0, 0.5)),
  PRIMARY KEY (exercise_id, muscle)
);

CREATE TABLE exercise_alias (
  alias TEXT PRIMARY KEY COLLATE NOCASE,
  exercise_id INTEGER NOT NULL REFERENCES exercise(id)
);

CREATE TABLE limitation (             -- injuries AND disliked exercises
  id INTEGER PRIMARY KEY,
  description TEXT NOT NULL,
  excluded_pattern TEXT,              -- e.g. 'v_push'
  excluded_exercise_id INTEGER REFERENCES exercise(id),
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE baseline (               -- onboarding self-reports
  id INTEGER PRIMARY KEY,
  exercise_id INTEGER NOT NULL REFERENCES exercise(id),
  weight_kg REAL NOT NULL,
  reps INTEGER NOT NULL,
  rir INTEGER,
  reported_at TEXT NOT NULL
);

CREATE TABLE agent_call (             -- audit + reproducibility
  id INTEGER PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('block_plan','session_review')),
  model TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  input_json TEXT NOT NULL,
  output_json TEXT,
  status TEXT NOT NULL CHECK (status IN ('accepted','rejected','error')),
  errors TEXT,
  warnings TEXT,                      -- non-blocking validator output (§6.5)
  created_at TEXT NOT NULL
);

CREATE TABLE block (
  id INTEGER PRIMARY KEY,
  start_date TEXT NOT NULL,
  weeks INTEGER NOT NULL DEFAULT 4,
  deload_week INTEGER NOT NULL DEFAULT 4,
  status TEXT NOT NULL CHECK (status IN ('active','completed','abandoned')),
  rationale TEXT,
  agent_call_id INTEGER REFERENCES agent_call(id)
);

CREATE TABLE block_slot (             -- fixed template for the block
  id INTEGER PRIMARY KEY,
  block_id INTEGER NOT NULL REFERENCES block(id),
  day_index INTEGER NOT NULL,         -- 0 .. days_per_week-1
  position INTEGER NOT NULL,
  exercise_id INTEGER NOT NULL REFERENCES exercise(id),
  sets INTEGER NOT NULL,
  rep_min INTEGER NOT NULL,
  rep_max INTEGER NOT NULL,
  target_rir INTEGER NOT NULL,
  UNIQUE (block_id, day_index, position)
);

CREATE TABLE session (
  id INTEGER PRIMARY KEY,
  block_id INTEGER NOT NULL REFERENCES block(id),
  week INTEGER NOT NULL,
  day_index INTEGER NOT NULL,
  date TEXT,
  status TEXT NOT NULL CHECK (status IN ('planned','completed','partial','skipped')),
  notes TEXT
);

CREATE TABLE set_entry (
  id INTEGER PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES session(id),
  slot_id INTEGER REFERENCES block_slot(id),   -- NULL = unplanned exercise added by user
  exercise_id INTEGER NOT NULL REFERENCES exercise(id),
  set_index INTEGER NOT NULL,
  set_type TEXT NOT NULL DEFAULT 'working' CHECK (set_type IN ('warmup','working')),
  presc_weight_kg REAL,               -- NULL = calibration: user picks load
  presc_reps_min INTEGER,
  presc_reps_max INTEGER,             -- may exceed slot rep_max under rep-extension (§5.1)
  presc_rir INTEGER,
  load_modifier TEXT NOT NULL DEFAULT 'none'
    CHECK (load_modifier IN ('none','deload','gap','recalibrate','review_reduce')),
  actual_weight_kg REAL,
  actual_reps INTEGER,
  actual_rir INTEGER,
  pain INTEGER NOT NULL DEFAULT 0 CHECK (pain BETWEEN 0 AND 10),
  logged_at TEXT
);
