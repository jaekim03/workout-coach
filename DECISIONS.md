# Decisions

One entry per decision (DESIGN §11). One-way decisions are jaekim03's; two-way
decisions are builder defaults and can be changed in a normal PR. Entries contain
no personal training information (D6).

A locked one-way entry may only change together with a new `Answered:` line,
which the `/decisions` command writes (D-38).

D-1 to D-6 are DESIGN §2 D1–D6. D-7 to D-16 are DESIGN §9 Q1–Q10.

## D-1: What does the agent plan, and what does the engine generate?
Status: locked
Type: one-way
Choice: The agent plans a fixed 4-week block (3 build weeks + 1 deload). The engine generates the sessions inside it. Re-plan only at block end or on a §6.1 trigger.
Rationale: DESIGN §2 D1.

## D-2: What is done in code and what by the LLM?
Status: locked
Type: one-way
Choice: Code: progression, e1RM, rounding, caps, exclusions, volume counting, validation, flags. LLM: split, exercise selection, set/rep scheme, target RIR, interpreting notes and pain, rationale text. The LLM never outputs a load.
Rationale: DESIGN §2 D2.

## D-3: Are prescribed and actual values both stored?
Status: locked
Type: one-way
Choice: Every set row stores both prescribed and actual values.
Rationale: DESIGN §2 D3.

## D-4: How does the agent exchange data with the app?
Status: locked
Type: one-way
Choice: The agent reads precomputed summaries and returns JSON validated against a schema. It never writes to the database; app code writes after validation.
Rationale: DESIGN §2 D4.

## D-5: What is the deployment scope?
Status: locked
Type: one-way
Choice: Single user, one platform, SQLite.
Rationale: DESIGN §2 D5.

## D-6: What may reach GitHub?
Status: locked
Type: one-way
Choice: Code, docs, prompts and synthetic test data only. No personal training information in files, history, commit messages, PRs, issues or Actions logs. Enforced in layers (DESIGN §13.2).
Rationale: DESIGN §2 D6.

## D-7: Which logging platform (Q1)?
Status: open
Type: one-way
Choice: undecided (PWA, native iOS, or chat bot)
Rationale: Needs phone access at the gym. Blocks build step 6 (UI) only.

## D-8: Hosting and sync for the chosen platform (Q2)?
Status: open
Type: one-way
Choice: undecided
Rationale: Depends on D-7. Blocks deployment only.

## D-9: Which LLM model and per-call cost ceiling (Q3)?
Status: open
Type: two-way
Choice: Default: Claude via the Anthropic API; exact model and ceiling to be set in build step 4.
Rationale: DESIGN §9 default; blocks nothing before step 4.

## D-10: Daily readiness signals for autoregulation (Q4)?
Status: open
Type: two-way
Choice: Not in v1.
Rationale: DESIGN §1 non-goal; revisit for v2.

## D-11: Supersets, drop sets and cardio (Q5)?
Status: open
Type: two-way
Choice: Not in v1.
Rationale: DESIGN §1 non-goal; revisit for v2 as time-savers.

## D-12: Conversational onboarding (Q6)?
Status: open
Type: two-way
Choice: Not in v1; onboarding is a deterministic CLI form.
Rationale: DESIGN §7.

## D-13: Reopen D-1 for 5–6 week blocks or a conditional deload (Q7)?
Status: open
Type: one-way
Choice: Default: keep 3 build weeks + 1 deload.
Rationale: The schema already supports longer blocks; blocks nothing in v1.

## D-14: Does a gap of 7+ days overlapping the deload week count as the deload (Q8)?
Status: open
Type: one-way
Choice: Default: not applied.
Rationale: D-1-adjacent; blocks nothing in v1.

## D-15: Within-block RIR ramp (Q9)?
Status: open
Type: two-way
Choice: Not in v1; target RIR is constant within a block.
Rationale: Needs effort-normalized progression triggers; revisit for v2.

## D-16: Repo visibility (Q10)?
Status: locked
Type: one-way
Choice: Public.
Rationale: jaekim03's choice over the documented default (private); gives free branch protection and secret scanning, and makes any leak permanent.
Answered: 2026-10-05 via /decisions

## D-17: Training tier cut-points
Status: locked
Type: two-way
Choice: novice < 6 months, intermediate 6–35, advanced ≥ 36.
Rationale: DESIGN §5.0; practitioner convention.

## D-18: Load step size (`step_pct`)
Status: locked
Type: two-way
Choice: Novice: lower 7.5%, upper 5%. Intermediate and advanced: lower 5%, upper (including isolation) 2.5%.
Rationale: DESIGN §5.0; inside the ACSM 2009 2–10% band.

## D-19: Evaluable, miss and early-stop definitions
Status: locked
Type: two-way
Choice: As DESIGN §5.0: evaluable needs no load modifier, pain < 4, all prescribed sets logged, weight within 1 increment and no swap; miss is set 1 below rep_min or total reps below sets × rep_min; early stop is reps < rep_min with RIR ≥ prescribed + 2.
Rationale: Normal set-to-set rep drop near failure must not count as a miss.

## D-20: Miss handling and counter reset
Status: locked
Type: two-way
Choice: 1 miss holds; 2 consecutive evaluable misses at the same load cut the load to 90% and reset the counter. Non-evaluable exposures neither count nor reset.
Rationale: DESIGN §5.1 step 5; without the reset, cuts spiral downward.

## D-21: Recalibration bounds
Status: locked
Type: two-way
Choice: Recalibrate when set-1 reps are ≥ prescribed max + 3 (any evaluable exposure, or a first exposure), when set-1 reps are ≤ rep_min − 3 (first exposure only), or when last-set RIR ≥ prescribed + 3. Clamp the new load to ±20% of the last load on a first exposure and to ≤ last × 1.10 otherwise. A first exposure is the first after calibration, a baseline, or a gap of ≥ 56 days.
Rationale: DESIGN §5.1 step 3; deadband wider than RIR estimation error.

## D-22: Per-exercise gap table and fast return
Status: locked
Type: two-way
Choice: As DESIGN §5.4, by days since the exercise's last exposure: ≤ 13 no change; 14–27 load × 0.95; 28–55 load × 0.90 and −1 set (min 1); ≥ 56 load × 0.80 and −1 set (min 1); ≥ 180 calibrate. RIR +1 on every gap exposure. Fast return: next load = max(step-4 result, min(pre-gap load, last × 1.10)).
Rationale: Short breaks cost little and lost strength returns quickly.

## D-23: Global gap handling
Status: locked
Type: two-way
Choice: 14–20 days since the last session resumes the block; 21 or more triggers a re-plan.
Rationale: DESIGN §5.4; a two-week break does not invalidate the template.

## D-24: Load reductions do not stack
Status: locked
Type: two-way
Choice: At most one load reduction per set: apply the single largest, never the product.
Rationale: DESIGN §5.4.

## D-25: Stall thresholds
Status: locked
Type: two-way
Choice: 4 consecutive evaluable exposures without a 1% e1RM improvement (or without a load or total-rep rise), or 2 miss-reductions within 42 days.
Rationale: DESIGN §5.7.

## D-26: Fatigue thresholds
Status: locked
Type: two-way
Choice: In build weeks: ≥ 2 slots with evaluable misses in the same week, or ≥ 2 exercises with exposure e1RM ≥ 5% below block best on 2 consecutive exposures.
Rationale: DESIGN §5.7.

## D-27: Per-muscle status and volume suggestion thresholds
Status: locked
Type: two-way
Choice: As DESIGN §5.7. Stalled: not progressing for 2 consecutive blocks, adherence ≥ 0.9, no pain ≥ 4, no reductions. Overreached: ≥ 50% of the muscle's direct slots had a reduction, or adherence < 0.8, or recurrent pain. Suggestion: ±max(2, round(0.2 × weekly sets)), bounded by the soft max and hard min; two raises in a row without progress set the ceiling flag.
Rationale: Hold volume while progressing; raise only on a real stall.

## D-28: Per-muscle weekly volume table
Status: locked
Type: two-way
Choice: The tier defaults and soft maxima in the DESIGN §6.5 table; Tier-A muscles are chest, back, quads, hamstrings, glutes and side delts.
Rationale: Practitioner convention built from meta-analytic ranges.

## D-29: Volume caps
Status: locked
Type: two-way
Choice: Weekly: reject Tier-A below 4, reject any muscle above 24. Per session per muscle: warn above 8, reject above 11.
Rationale: DESIGN §6.5 V1, V3, V4.

## D-30: Session time estimate
Status: locked
Type: two-way
Choice: The DESIGN §6.5 V10 formula with minutes per set of 3.25 (HEAVY), 2.75 (COMPOUND) and 2.0 (ISOLATION); reject above 1.1 × session minutes or above 30 working sets per day.
Rationale: Default rest plus set time, by effort class.

## D-31: Coverage, order and carry-over warnings
Status: locked
Type: two-way
Choice: DESIGN §6.5 V11–V15, all warn-only.
Rationale: Weak or indirect evidence, so they must not block a plan.

## D-32: Pain bands and review threshold
Status: locked
Type: two-way
Choice: Pain 0–10. 1–3 is logged only; ≥ 4 triggers a review; 4–5 and ≥ 6 restrict the allowed actions (DESIGN §6.5 S2); recurrent means the same exercise with pain ≥ 4 in ≥ 2 sessions within 14 days; the red-flag keyword list is S4.
Rationale: Pain-monitoring convention from rehab practice.

## D-33: `exercise_muscle` seed weights
Status: locked
Type: two-way
Choice: The DESIGN §4 seed mapping table, with weights 1.0 (primary) and 0.5 (secondary).
Rationale: Fractional set counting.

## D-34: `drop_slot` review action
Status: locked
Type: two-way
Choice: `session_review` may drop a slot for the next session or the rest of the block.
Rationale: DESIGN §6.2; the fallback already drops painful slots.

## D-35: Python environment tooling
Status: locked
Type: two-way
Choice: uv with `pyproject.toml` and a committed `uv.lock`; pre-commit is a dev dependency; gitleaks is a system binary.
Rationale: A lockfile gives CI and the local machine identical versions.

## D-36: Package layout
Status: locked
Type: two-way
Choice: The package is `src/coach/`. `config.py` lives at `src/coach/config.py`, not the repo root shown in DESIGN §13.1; engine modules live in `src/coach/engine/`.
Rationale: One import path for tests, CI and the installed CLI.

## D-37: Privacy guard interpretation
Status: locked
Type: two-way
Choice: `check_private.py` exempts exactly three config paths from the structured-file rule (`.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `.claude/settings.json`). Beyond DESIGN §13.2 it also: blocks `.csv` everywhere; matches block rules case-insensitively; blocks archives, dumps, images, video, notebooks and other tabular or pickled formats; allows only `.json` under `seed/`; allows `.sql` only as `src/coach/migrations/NNNN_name.sql`; looks for the SQLite header anywhere in a file; and in CI checks every commit in the range, not the net diff. A migration file may not contain `VALUES` (literal rows); copying between tables uses `INSERT ... SELECT`.
Rationale: DESIGN §13.1 requires those three files; the repo is public, so the guard errs on the strict side and a file added then removed in one PR must still be caught.

## D-38: How a `/decisions` answer is recorded and checked
Status: locked
Type: two-way
Choice: `/decisions` writes an `Answered: <YYYY-MM-DD> via /decisions` line (with a counter for a second answer on one day). `check_decisions.py` fails when a one-way entry is added as locked, becomes locked, changes while locked, is reopened or is removed without a new, well-formed `Answered:` line. Locked two-way entries may change in a normal PR. The check is skipped only when `DECISIONS.md` does not exist at the base commit.
Rationale: DESIGN §11 lets the builder change two-way defaults, so the lock check covers one-way entries only.

## D-39: Secret scanning in CI
Status: locked
Type: two-way
Choice: CI downloads the pinned gitleaks release binary, verifies its SHA-256, and scans the PR's commits; the pre-commit hook uses the locally installed binary. Third-party actions are pinned by commit hash.
Rationale: No third-party action or licence key is needed.

## D-40: Which license does the public repo carry?
Status: locked
Type: one-way
Choice: MIT.
Rationale: The owner's choice; a permissive license cannot be withdrawn for copies already taken.
Answered: 2026-10-05 via /decisions

## D-41: How is the owner named in the public repo?
Status: locked
Type: one-way
Choice: By GitHub handle (jaekim03) in docs and as the commit author, with GitHub's no-reply address as the commit email.
Rationale: The repo is public and its history is permanent.
Answered: 2026-10-05 via /decisions

## D-42: Baseline discount
Status: locked
Type: two-way
Choice: A self-reported baseline is discounted to 0.9 × its e1RM before the first prescription.
Rationale: DESIGN §5.1 step 2; self-reports run high.

## D-43: e1RM estimate
Status: locked
Type: two-way
Choice: Epley with divisor 30; logged RIR is clamped to 0–5 and a missing RIR counts as 0; only working sets of 1–12 reps with external load are eligible.
Rationale: DESIGN §5.0; linear estimates lose accuracy at high reps and RIR far from failure is unreliable.

## D-44: RIR deadband and increase gate
Status: locked
Type: two-way
Choice: Never act on a RIR difference of ≤ 1. An increase needs every working set at the prescribed top and last-set RIR either unlogged or ≥ prescribed − 1.
Rationale: DESIGN §5.0 and §5.1 step 4; lifters misjudge RIR by about one rep.

## D-45: Increase sizing and cap
Status: locked
Type: two-way
Choice: k_max = max(1, floor(step_pct × last / increment)); a jump of 2 or more increments is skipped above 1.10 × last; a single increment is never blocked; candidates are never rounded down to ≤ last; `reps_needed` is rounded to 9 decimals before the ceiling.
Rationale: DESIGN §5.1 step 4; removes the small-dumbbell deadlock.

## D-46: Rep-extension ceiling
Status: locked
Type: two-way
Choice: When no increment passes, hold the load and extend the top of the range to `reps_needed(last + increment)` if that is ≤ 30; above 30 flag `increment_too_coarse`.
Rationale: DESIGN §5.1 step 4; rep progression is a valid stimulus up to about 30 reps.

## D-47: Bodyweight progression
Status: locked
Type: two-way
Choice: Reps only, `rep_max` up to 30; flag `rep_cap` after 2 consecutive evaluable exposures with all sets ≥ `rep_max`.
Rationale: DESIGN §5.2.

## D-48: Deload week
Status: locked
Type: two-way
Choice: Sets = ceil(sets / 2); load = last build load × 0.90, rounded down; prescribed RIR = min(4, max(target RIR + 2, 3)); never full rest.
Rationale: DESIGN §5.3 and §5.4; practitioner consensus.

## D-49: Agent `reduce_load` size
Status: locked
Type: two-way
Choice: The engine applies × 0.90.
Rationale: DESIGN §5.4 and §6.2; the agent never chooses a number.

## D-50: Frequency and minimum-target checks (V2, V5)
Status: locked
Type: two-way
Choice: Warn when a Tier-A muscle is below 10 weekly sets (novice: 6). Reject unless each Tier-A muscle gets ≥ 1.0 fractional sets on ≥ 2 distinct days; warn when another muscle has ≥ 6 weekly sets on only 1 day.
Rationale: DESIGN §6.5 V2 and V5.

## D-51: Slot shape checks (V6–V9)
Status: locked
Type: two-way
Choice: Sets per slot 1–6 (warn at 1 or 6). rep_min ≥ 5 unless the goal is strength; rep_max ≤ 30; span 2–8. External-load compound rep_max: warn > 12, reject > 15; isolation warn > 20. Target RIR 0–3 for hypertrophy and general goals; class ranges (warn): HEAVY 1–3, COMPOUND 1–3 (stable 0–3), ISOLATION 0–2.
Rationale: DESIGN §6.5 V6–V9.

## D-52: Rest timer values
Status: locked
Type: two-way
Choice: Display only: HEAVY 150 s, COMPOUND 120 s, ISOLATION 75 s, floor 60 s.
Rationale: DESIGN §8.

## D-53: Review fallback and retry
Status: locked
Type: two-way
Choice: A rejected agent output is retried once with the errors appended. Second failure: `block_plan` repeats the previous template (or stops if there is none); `session_review` makes no adjustments except dropping slots with pain ≥ 4 for the next session. Warnings never trigger a retry.
Rationale: DESIGN §6.5 failure handling.

## D-54: How are schema changes applied to an existing database?
Status: locked
Type: two-way
Choice: Numbered forward-only `.sql` files in `src/coach/migrations/`, tracked with SQLite's `user_version`. Each runs in its own transaction; the database is copied inside the data directory before pending migrations run; a database newer than the code is refused. A migration that exists on the base branch may not be edited or removed (`check_decisions.py`). Foreign keys are off while a script runs so it can rebuild a referenced table, and `foreign_key_check` must be clean before commit. A script may not contain BEGIN, COMMIT or ROLLBACK. The database file and its backups are readable by the owner only.
Rationale: The owner's choice; no dependency, and plain SQL carries over to whatever platform D-7 selects.

## D-55: Seed data format and default increments
Status: locked
Type: two-way
Choice: One `seed/exercises.json` holding equipment and exercises, each exercise with its aliases and muscle weights. Default increments in kg: barbell 2.5, dumbbell 2 per hand, cable 5, machine 5, smith_machine 2.5, plate_loaded 2.5, fixed_barbell 5; none for pull-up bar, dip station, bench and rack. Re-loading the seed never overwrites existing equipment rows.
Rationale: The owner's choice; real increments and availability are entered at onboarding and stay in the data directory.

## D-56: Equipment names in the seed
Status: locked
Type: two-way
Choice: The seed adds `smith_machine`, `plate_loaded`, `fixed_barbell` and `dip_station` to the seven names in DESIGN §4. The library is general: about 60 exercises, covering every movement pattern and muscle both with and without a free barbell and rack.
Rationale: Each equipment row holds one load increment, and plates, weight stacks and preloaded bars step differently; many commercial gyms have a Smith machine and no free barbell. The `equipment.name` column has no CHECK, so this does not change the schema.

## D-57: Effort class of Smith machine and plate-loaded lifts
Status: locked
Type: two-way
Choice: `HEAVY` = squat or hinge pattern, equipment barbell or smith_machine, and a 1.0 weight on quads or hamstrings; hip thrusts (glutes only) are therefore `COMPOUND`. `stable` = machine, cable or plate_loaded. DESIGN §5.0 is updated to match.
Rationale: The owner's choices: a Smith squat or RDL loads the whole body about as hard as the free-bar lift, and a hip thrust does not. Plate-loaded machines are guided like selectorized ones.

## D-58: Exercises left out of the v1 library
Status: locked
Type: two-way
Choice: No assisted pull-up or dip (more weight makes the rep easier, which the progression rules do not model). No hip adduction or abduction, glute kickback, back extension or timed holds such as planks (the muscle list has no adductors, DESIGN §4's mapping table does not cover them, and holds are not counted in reps). No weighted pull-ups or dips (bodyweight exercises carry no load).
Rationale: The owner's choice for assisted lifts; an "assistance" load type would be a schema change and can be raised later as a one-way decision.

## D-59: What happens when the seed is loaded again?
Status: locked
Type: two-way
Choice: `open_db()` loads the seed on every start. Exercises are matched by exact name and updated; aliases and muscle maps are replaced from the file; an exercise no longer in the file is deleted unless a block slot, set, baseline or limitation refers to it; equipment rows are never overwritten. Aliases are seed-owned and limited to unambiguous spellings and abbreviations: generic names that fit several variants (such as "squat" or "bench press") are left to the step-5 name search. Renaming an exercise creates a new one, and history stays with the old name.
Rationale: The library must be updatable without touching logged data. Changing the pattern or muscle map of an exercise that has shipped alters how past sets are counted, so treat such an edit as one-way and raise it through /decisions.

## D-60: Which lifts does the V14 adjacency warning cover?
Status: locked
Type: two-way
Choice: V14 warns on two adjacent `HEAVY` slots with target RIR ≤ 2, not only barbell squat and hinge.
Rationale: The owner's choice; follows D-57, and otherwise the warning could never fire without a free barbell.

## D-61: Can an exercise require more than one piece of equipment?
Status: open
Type: one-way
Choice: Default: no. The `bench` and `rack` rows are kept as DESIGN §4 lists them but no exercise can require them, so their availability filters nothing; a missing bench is handled with a limitation.
Rationale: A many-to-many exercise-equipment table would change the locked data model. The owner chose to keep the rows for v1.
