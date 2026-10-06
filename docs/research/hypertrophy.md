# Volume and Effort Should Drive the Engine

The 2025–2026 evidence points to one main lever for muscle growth: **weekly hard sets per muscle**, counted fractionally (1.0 for direct work, 0.5 for synergists) and taken to roughly **0–3 reps in reserve**. Returns are largest up to about **10 sets/week**, still worthwhile from **10–20**, and small beyond that ([Pelland 2025](https://www.fisiologiadelejercicio.com/wp-content/uploads/2025/12/The-Resistance-Training-Dose-Response.pdf); [ACSM 2026](https://www.fisiologiadelejercicio.com/wp-content/uploads/2026/03/Resistance-Training-Prescription-for-Muscl.pdf)). Several variables barely change hypertrophy when volume and effort are equal: load across about 5–30 reps, frequency, split, exercise order, periodization model, tempo, and rest beyond about 90 s. The engine should therefore enforce volume, effort and frequency bounds in code and treat everything else as agent preference. DESIGN.md's core choices are compatible with this evidence: double progression, a fixed template within each block, and a deload every 4th week. As written, though, §5 has **five mechanical bugs**:
- small dumbbell loads can never increase (a deadlock);
- a "miss" fires on normal set-to-set rep drop-off;
- repeated −10% cuts spiral downward;
- gap rules are stricter than the detraining data justify, and they stack with the deload;
- `isolation` swaps can turn a leg curl into a lateral raise.

The schema also has no exercise→muscle map, so per-muscle volume cannot be computed at all. Two proposals touch locked decisions (D1 block length; D2 if split templates or volume suggestions became binding). They are flagged below, not applied. Main caveat: most trials studied young, mostly male, often untrained people for 8–12 weeks. Many numeric thresholds below are therefore conventions or design choices, and each one is labelled.

**Tag legend (used throughout):**

| Tag | Meaning |
|---|---|
| **E-high** | Consistent meta-analyses and/or a position stand |
| **E-mod** | One meta-analysis, several RCTs, or a meta-analysis with real limitations |
| **E-low** | Single RCT, preprint, secondary-summary-only source, or extrapolation from another population |
| **PC** | Practitioner convention or expert consensus (Delphi, coaching frameworks); no outcome trial |
| **DC** | Design choice: an engineering threshold with no source; log in DECISIONS.md as two-way |

## Weekly hard sets near failure drive growth; most other variables are preference

The table below is the evidence base the engine rules and agent principles rest on. Read the "Implication" column as the bridge to §5/§6.

| Variable | What current evidence says | Tag | Implication |
|---|---|---|---|
| **Weekly volume** | Square-root dose-response; ~0.24% more growth per extra fractional set. Minimum effective dose ≈ **4 sets/wk**. Efficiency drops after ~10 and again after ~18–19 sets. Data are sparse above ~25 ([Pelland 2025](https://link.springer.com/article/10.1007/s40279-025-02344-w)). ACSM: hypertrophy "enhanced by higher volumes (≥10 sets/wk)" ([ACSM 2026](https://www.fisiologiadelejercicio.com/wp-content/uploads/2026/03/Resistance-Training-Prescription-for-Muscl.pdf)) | E-high | Target 10–16/muscle; reject <4 on major muscles; hard cap 24 |
| **More volume in trained lifters** | Keeping ~12 quad sets/wk matched +30% and +60% for growth ([Barsuhn 2024](https://journals.physiology.org/doi/full/10.1152/japplphysiol.00476.2024)). 18 vs 33 sets/wk gave similar CSA, with no harm from the higher dose ([Camargo 2026](https://journals.physiology.org/doi/full/10.1152/japplphysiol.00284.2026)) | E-mod | Hold volume flat by default; raise only on a stall |
| **Set counting** | "Fractional" counting (indirect = 0.5) beat "total" counting for hypertrophy ([Pelland 2025](https://www.fisiologiadelejercicio.com/wp-content/uploads/2025/12/The-Resistance-Training-Dose-Response.pdf); [Remmert 2025](https://sportrxiv.org/index.php/server/preprint/view/537)). The 0.5 weight itself is a modelling convention | E-mod | New `exercise_muscle` table with weights 1.0/0.5 |
| **Per-session volume** | Returns flatten at **~11 fractional sets/muscle/session** (preprint; no evidence that more harms) ([Remmert 2025](https://sportrxiv.org/index.php/server/preprint/view/537)). Expert meta-regression puts the inflection at 6–8 sets with ≥2 min rest ([Krieger](https://weightology.net/the-members-area/evidence-based-guides/set-volume-for-muscle-size-the-ultimate-evidence-based-bible/)) | E-low | Reject >11, warn >8 |
| **Frequency** | At equal volume, frequency has negligible effect on growth. Strength gains ~3.3% per extra weekly session ([Pelland 2025](https://www.fisiologiadelejercicio.com/wp-content/uploads/2025/12/The-Resistance-Training-Dose-Response.pdf)). ACSM: train each major muscle **≥2×/wk** ([Newswise](https://www.newswise.com/articles/acsm-unveils-landmark-2026-resistance-training-guidelines-first-update-in-17-years)) | E-high | ≥2 days/wk per major muscle, mainly to stay under the session cap |
| **Effort (RIR)** | Growth rises as sets end closer to failure ([Robinson 2024](https://link.springer.com/article/10.1007/s40279-024-02069-2), exploratory, RIR estimated). In trained lifters, 1–2 RIR ≈ failure for growth, while failure caused more fatigue and rep loss ([Refalo 2024](https://www.tandfonline.com/doi/full/10.1080/02640414.2024.2321021)). Single-set failure training was only modestly better ([Hermann preprint](https://sportrxiv.org/index.php/server/preprint/view/484)) | E-mod | `target_rir` 0–3; default 2 for compounds, 1 for isolation |
| **RIR accuracy** | Lifters underpredict reps left by **~0.95 reps**. Accuracy is much worse above 12 reps and slightly better near failure and on later sets. Training status does not matter ([Halperin 2022](https://link.springer.com/article/10.1007/s40279-021-01559-x)) | E-high | ±1 RIR deadband; prompt RIR on the last set; RIR from sets >12 reps is unreliable |
| **Load / reps** | Hypertrophy is load-independent from low to high loads; strength favours ≤15RM ([Lopez 2021](https://research-repository.uwa.edu.au/en/publications/resistance-training-load-effects-on-muscle-hypertrophy-and-streng/)). ACSM: ~30–100% 1RM works if effort is sufficient ([secondary](https://www.moveyourbonespt.com/blog/2026-acsm-resistance-training-guidelines)) | E-high | Rep range is chosen for practical reasons; rep_min ≥5 for hypertrophy |
| **e1RM accuracy** | Linear equations are accurate from ~5RM; error grows at 10–20RM. Recommendation: use "no more than 10 repetitions" ([Reynolds 2006](https://www.unm.edu/~rrobergs/478RMStrengthPrediction.pdf)) | E-mod | Keep reps ≤12 gate; compounds rep_max ≤12 |
| **Rest** | >60 s has a small edge; no detectable benefit beyond 90 s ([Singer 2024](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2024.1429789/full)) | E-mod | 60 s floor; longer rest on compounds is for performance, not growth |
| **Tempo** | 0.5–8 s per rep gives similar growth; >10 s per rep looks inferior ([Schoenfeld 2015](https://d.docksci.com/effect-of-repetition-duration-during-resistance-training-on-muscle-hypertrophy-a_5a6b9767d64ab2c8cd817bde.html)) | E-mod | No tempo field |
| **ROM / muscle length** | Lengthened partials ≈ full ROM in trained lifters ([Wolf 2025 RCT](https://pubmed.ncbi.nlm.nih.gov/39959841/)). A systematic review "consistently" favours longer muscle lengths, but certainty is low ([Wolf 2025 SR](https://pmc.ncbi.nlm.nih.gov/articles/PMC12869050)). Another 2025 meta-analysis found only trivial differences ([Varovic 2025, secondary](https://www.potentiaworkout.com/en/blog/does-training-in-the-stretched-position-build-more-muscle-a-new-2025-meta-analysis)) | E-low | Full ROM by default; "stretch bias" only as a tie-breaker |
| **Progression model** | Adding load and adding reps gave equal growth ([Plotkin 2022](https://peerj.com/articles/14142/)). ACSM: add 2–10% load once the target is exceeded by 1–2 reps ([ACSM 2009](https://www.medscape.com/viewarticle/717047)) | E-mod | Keep double progression; size steps in % |
| **Autoregulation** | RPE-based loading gave similar growth and a small strength edge ([Helms 2018](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2018.00247/full)). Only one study in the autoregulation meta-analysis measured hypertrophy ([Hickmott 2022](https://sportsmedicine-open.springeropen.com/articles/10.1186/s40798-021-00404-9)) | E-mod | Optional RIR gate only; no RPE engine |
| **Periodization** | No hypertrophy benefit from periodized vs non-periodized (ES 0.13, n.s.) or linear vs undulating (ES 0.05) training ([Moesgaard 2022](https://link.springer.com/article/10.1007/s40279-021-01636-1); [Grgic 2017](https://peerj.com/articles/3695/)) | E-high | Flat template; constant RIR within a block |
| **Deloads** | Delphi consensus: every 4–6 wk, ~7 days, cut volume, raise RIR ([Bell 2023](https://link.springer.com/article/10.1186/s40798-023-00633-0)). Practical guidance: cut volume 40–60% for moderate need, intensity ~−10% ([Bell 2025](https://shura.shu.ac.uk/35313/3/Bell-APracticalApproach(AM).pdf)). One week off had no effect on hypertrophy and slightly blunted strength ([Coleman 2024](https://peerj.com/articles/16777/)). A reduced-volume deload was neutral for growth in untrained lifters ([Pancar 2026](https://www.nature.com/articles/s41598-026-40612-5)) | PC + E-low | Keep week-4 deload (neutral for growth); add RIR ≥3; never full rest |
| **Detraining / retraining** | Strength held after 2 wk off in trained men ([Hwang 2017](https://pubmed.ncbi.nlm.nih.gov/28328712/), title-level only). Losses scale with time off and are larger in inactive people ([Bosquet 2013](https://www.inigomujika.com/en/2013/02/effect-of-training-cessation-on-muscular-performance-a-meta-analysis-2/)). After a 10-wk break, pre-break levels returned in ~5 wk ([Halonen 2024](https://www.jyu.fi/en/news/breaks-in-resistance-training-do-not-impair-long-term-development-in-strength-and-muscle-size), press release) | E-low | No load cut under 14 days; graded cuts after; fast return |
| **Compound vs isolation** | Similar growth in the muscles studied, mostly arms ([Rosa 2022 via Schoenfeld](https://www.lookgreatnaked.com/blog/do-you-need-to-perform-single-joint-exercises-for-optimal-muscle-building/)). Squats and hip thrusts grow hamstrings negligibly; squat ≈ hip thrust for glute max ([Plotkin 2023](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1279170/full)). Presses miss side and rear delts | E-mod | Coverage warnings for gap muscles |
| **Specific picks** | Overhead triceps extension beat pushdowns: long head +28.5% vs +19.6% ([Maeo 2023](https://www.tandfonline.com/doi/full/10.1080/17461391.2022.2100279)). Seated leg curl beat lying, ~14% vs 9% hamstring volume ([Maeo 2021 via Henselmans](https://mennohenselmans.com/stretch-mediated-hypertrophy-rom/)) | E-low | Agent preferences, not hard rules |
| **Machines vs free weights** | No difference in hypertrophy ([Haugen 2023](https://bmcsportsscimedrehabil.biomedcentral.com/articles/10.1186/s13102-023-00713-4)). EMG does not predict growth ([Plotkin 2023](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1279170/full)) | E-mod | Choose on comfort, stability and load increments |
| **Variation** | Varied training gives growth comparable to fixed exercise selection ([Kassiano 2022](https://journals.lww.com/nsca-jscr/fulltext/2022/06000/does_varying_resistance_exercises_promote_superior.40.aspx)). Rotate deliberately every 3–4 wk; keep the main lifts fixed ([Strengthshop](https://strengthshop.eu/blogs/news/variation-in-training-part-2-exercise-variation)) | E-low + PC | Rotate accessories only at block boundaries |
| **Splits** | Full-body ≈ split routines for size and strength ([Ramos-Campo 2024](https://biolayne.com/reps/issue-25/full-body-vs-split-routine-wars/)) | E-mod | Choose the split that fits days and minutes |
| **Exercise order** | No effect on hypertrophy (ES 0.03); strength favours whichever lift comes first ([Nunes 2021 via FitChef](https://fitchef.com/studies/exercise-order-strength-hypertrophy/)) | E-mod | Order rules are warnings only |
| **Drop sets / supersets** | Similar growth in less time: drop sets ½–⅓ of the time ([Sødal 2023](https://link.springer.com/article/10.1186/s40798-023-00620-5)); supersets ~36% less time ([Burke 2024](https://sportrxiv.org/index.php/server/preprint/view/419)) | E-mod | v2 only, as time-savers (Q5) |
| **Pain** | Pain up to ~5/10 during loading is acceptable if it settles by the next morning and does not trend up week to week ([Silbernagel 2007](http://www.thehealthrooms.co.uk/wp-content/uploads/2019/01/Continued-Sports-Activity-Using-a-Pain-Monitoring-Model-During-Rehabilitation-in-Patients-with-Achillies-Tendinopathy.pdf), tendinopathy rehab). Traffic-light bands ([SRALab](https://www.sralab.org/sites/default/files/2017-04/Pain%20Activity%20Traffic%20Light%202017.pdf)). Red flags call for referral ([London Bridge Orthopaedics](https://www.londonbridgeorthopaedics.co.uk/general-red-flags-to-consider-across-all-msk-presentations/)) | PC (rehab, extrapolated) | Pain scale 0–10; modify the exercise before removing it |
| **Training status** | ACSM 2026 reportedly no longer tiers its recommendations ([secondary](https://getfitcraft.com/science/acsm-2026-resistance-training-guidelines)). Progression-speed tiers reflect how much adaptation is left plus measurement noise, not a biological switch ([Barbell Medicine](https://www.barbellmedicine.com/blog/novice-intermediate-advanced-strength-training/)) | PC | Same rules for everyone; tier sets only starting volume and step size |

**Where the evidence is thin or conflicting (state this honestly in agent output):**
- Per-session ceiling: 6–8 sets (Krieger, direct counting, long rest) vs ~11 (Remmert, fractional counting, preprint). No reconciliation exists, and no trial shows "junk volume" *harms* growth.
- Long-length training: one 2025 meta-analysis finds a small advantage; another finds trivial differences. Treat it as a tie-breaker only.
- Several ACSM 2026 specifics come from secondary summaries: the 2–3 RIR wording, 30–100% 1RM, and ≥2 sets per exercise. The "18–20 sets plateau" phrase could not be verified and is excluded here.
- Barbalho et al. studies were excluded from the compound-vs-isolation meta-analysis for "research improprieties". Never cite them ([Schoenfeld](https://www.lookgreatnaked.com/blog/do-you-need-to-perform-single-joint-exercises-for-optimal-muscle-building/)).
- The engine never observes hypertrophy. e1RM and reps-at-load are **strength proxies** used to steer volume, which is pragmatic but indirect.

## Five mechanical bugs sit in the current §5 draft

Each draft rule was checked against the evidence and simulated. The double-progression trigger, the hold rule, the deload magnitude and the baseline discount survive. The sizing, miss, gap and swap mechanics do not.

| Draft rule (DESIGN §5/§6.5) | Verdict | Problem (verified) | Fix | Tag |
|---|---|---|---|---|
| All sets ≥ rep_max → `round_load(last + inc)`, capped +10% | **CHANGE** | **Deadlock:** 8 kg DB with a 2 kg increment gives `round_load(min(10, 8.8)) = 8`, so the load never rises. A fixed +1 increment is also 1.8% on a 140 kg squat but 25% on an 8 kg DB | Relative step + Epley range guard + rep-extension mode (§5.1 R4) | E-mod (ACSM 2–10%) + DC |
| Miss = any working set < rep_min | **CHANGE** | Near-failure multi-set work normally loses reps across sets (Refalo 2024: −16% to −30%), so this fires on normal sessions and over-triggers `session_review` | Miss = set 1 < rep_min OR total reps < sets × rep_min, on evaluable exposures only | DC |
| 2 consecutive misses → ×0.9 | **KEEP magnitude, FIX mechanics** | No counter reset: misses keep matching, so loads go 100 → 90 → 81 → 72.9 | Reset the counter after each reduction; add a `stalled` flag | PC (Bell ~10%) + DC |
| Gap 7–13 d → load ×0.9 | **CHANGE** | Stricter than the evidence (1 wk off: no hypertrophy cost; 2 wk off: strength held). Stacks with the deload to ×0.81. Measured globally, so a single exercise can go 14 d unseen without any adjustment | No cut ≤13 d; graded cuts per exercise (`d_ex`); never stack | E-low + DC |
| Gap ≥14 d → re-plan, no session | **CHANGE** | Re-planning after 2 weeks discards a still-valid template | Resume at 14–20 d; re-plan at ≥21 d | DC |
| Swap = same `movement_pattern` | **CHANGE** | `isolation` is a catch-all, so leg curl → lateral raise passes validation | Isolation/core swaps must also keep the same 1.0-weight muscles | DC |
| Deload: ceil(sets/2), load ×0.9 | **KEEP + ADD** | Cuts 33–50% of sets, inside Bell's 40–60% band (slightly lighter for 3-set slots). No RIR target | Add `presc_rir = max(target_rir + 2, 3)`; never full rest | PC + E-low |
| e1RM: Epley + RIR, NULL → 0, reps ≤12 | **KEEP + clamp** | Accuracy is adequate for trend use. RIR estimates are least accurate far from failure (Halperin), so large logged RIR values inflate e1RM | `rir_eff` clamped 0–5; reps + rir = 1 → e1RM = weight | E-mod + DC (clamp) |
| Baseline discount 10% | **KEEP + ADD** | Slow climb when the baseline is far off | First-exposure recalibration (±3-rep deadband) | PC + DC |
| `pain INTEGER DEFAULT 0` | **CHANGE** | Undefined scale, so the agent cannot grade severity | `CHECK (pain BETWEEN 0 AND 10)` | PC |
| `working sets/day ≤ session_minutes/3` | **REPLACE (optional)** | Charges isolation sets like compound sets | Class-weighted time estimate (§6.5 V10) | PC + DC |

**Conflict in the underlying research, resolved here: e1RM gate.** One analysis proposed changing eligibility to `reps + RIR ≤ 12` (per Reynolds, linear equations work best at ≤10RM). Another said to keep `reps ≤ 12`. Recommendation: **keep `reps ≤ 12`**. The engine uses e1RM only for (a) trends within one exercise and rep range and (b) conversions to nearby rep targets. In both cases formula bias largely cancels. The stricter gate would also null the e1RM on most top-of-range sets (e.g., 12 reps @ RIR 2). Instead, cap external-load compounds at `rep_max ≤ 12` via a validator warning. (E-mod + DC)

**Conflict in the underlying research, resolved here: within-block RIR ramp.** One analysis proposed engine-applied weekly RIR offsets (+1/0/−1). Another warned that a ramp makes users hit `rep_max` through effort rather than strength, so raw double progression would over-progress in week 3. No RCT shows a ramp beats constant RIR for hypertrophy. **v1: constant RIR within a block.** A ramp can come in v2, with effort-normalized triggers. (PC + DC)

## Paste-ready §5 engine rules

Every threshold carries a tag. Rules tagged DC or PC are reversible defaults: log each one in DECISIONS.md as two-way. All functions are pure, per DESIGN §0.

---

### 5. Engine (deterministic)

#### 5.0 Definitions
- **Tier** from `training_age_months`: `novice < 6`, `intermediate 6–35`, `advanced ≥ 36`. *(PC: anchored to ACSM 2009 definitions; ACSM 2026 does not tier. Cut-points DC.)*
- **Effort class** (derived in code, no column; *PC*):
  - `HEAVY` = `squat` or `hinge` pattern with equipment = barbell.
  - `COMPOUND` = any other `squat, hinge, h_push, v_push, h_pull, v_pull, lunge`.
  - `ISOLATION` = `isolation, core`.
  - Flag `stable = equipment ∈ {machine, cable}`.
- **Region**: `lower` = `squat, hinge, lunge`; everything else is `upper`.
- **`step_pct`**: `lower` 5%, `upper` and ISOLATION 2.5%. Novice: `lower` 7.5%, `upper` 5%. *(E-mod band: ACSM 2009 2–10%; split PC.)*
- **`rir_eff`** = `clamp(actual_rir ?? 0, 0, 5)`. *(E-mod: underprediction ~1 rep makes NULL→0 conservative, Halperin 2022.)*
- **`e1RM(set)`** = `w × (1 + (reps + rir_eff)/30)`; if `reps + rir_eff = 1` → `w`.
  - Eligible only if `set_type = 'working'`, `load_type = 'external'`, `w > 0` and `1 ≤ reps ≤ 12`.
  - Exposure e1RM = max over eligible sets, else NULL. *(E-mod: Reynolds 2006, Halperin 2022.)*
- **Exposure**: the latest non-deload session (completed or partial) with ≥1 logged working set of the slot's exercise.
- **Evaluable exposure** (*DC*): all of the following hold:
  - `load_modifier = 'none'` on its sets (not deload, gap, recalibrate or review_reduce);
  - max `pain < 4`;
  - logged working sets ≥ prescribed working sets;
  - actual weight = prescribed weight ± 1 increment;
  - exercise not swapped.

  A non-evaluable exposure → **hold**, and it counts as neither success nor miss.
- **Miss** (evaluable only): `set1_reps < rep_min` OR `Σ working reps < sets × rep_min`. *(DC.)*
- **Early stop**: any set with `reps < rep_min` AND `actual_rir ≥ presc_rir + 2` → exposure non-evaluable; flag `early_stop`. *(DC on Halperin ±1 noise.)*
- **`min_set_reps`** = min `actual_reps` across the exposure's working sets.
- **`reps_needed(c)`** = `ceil(30 × ((c / last) × (1 + (rep_min + t)/30) − 1) − t)`, where `t = target_rir`. This is the reps at `last` that imply `rep_min` is achievable at `c` with `t` in reserve. *(Arithmetic from Epley.)*
- **RIR deadband**: never act on `|actual_rir − presc_rir| ≤ 1`. *(E-high: Halperin 2022.)*

#### 5.1 Next-session load (external load)
1. **No history, no baseline** → `presc_weight_kg = NULL` (calibration). *(keep)*
2. **Baseline only** → `round_load(0.9 × e1RM_baseline / (1 + (rep_min + target_rir)/30))`. *(keep; PC)*
3. **Recalibrate** (sets `load_modifier = 'recalibrate'`).
   - **When:**
     - the first exposure after calibration, a baseline, or a ≥56-day gap has `set1_reps ≥ presc_reps_max + 3` or `≤ rep_min − 3`; or
     - any evaluable exposure has `set1_reps ≥ presc_reps_max + 3`; or
     - last-set `actual_rir ≥ presc_rir + 3`.
   - **New load:** `r = round_load(e1RM_x / (1 + (rep_mid + target_rir)/30))`, with `rep_mid = floor((rep_min + rep_max)/2)`. `e1RM_x` may use the exposure's best set even above 12 reps, because source and target rep counts are close.
   - **Bounds:** clamp `r` to ±20% of `last` on a first exposure, and to `≤ last × 1.10` otherwise.
   - **Downward case:** use `r`.
   - **Upward case:** use `max(r, R4 result)`. If `r ≤ last`, R4 applies alone, including rep-extension.
   - *(DC; ±3-rep deadband from Halperin.)*
4. **Increase** when the last evaluable exposure has every working set `actual_reps ≥ rep_max` AND (last-set RIR not logged OR `actual_rir ≥ presc_rir − 1`). *(E-mod: ACSM 2009, Plotkin 2022; RIR gate DC.)*
   - `k_max = max(1, floor(step_pct × last / inc))`.
   - For `k = k_max … 1`:
     - `c = last + k × inc`;
     - skip if `k ≥ 2` and `c > 1.10 × last`;
     - accept the first `c` with `reps_needed(c) ≤ min_set_reps`.
   - A single increment is **never** blocked by the 10% cap. This fixes the deadlock.
   - **Rep-extension:** if no `k` passes, compute `rn = reps_needed(last + inc)`.
     - `rn ≤ 30` → hold load; prescribe `presc_reps_max = rn`.
     - `rn > 30` → hold; flag `increment_too_coarse`.
   - *(E-mod: rep progression is a valid stimulus, Plotkin 2022.)*
   - Never round a candidate down to `≤ last`.
5. **Miss handling.**
   - 1 miss → hold.
   - 2 consecutive evaluable misses at the same load → `round_load(last × 0.90)`, then **reset the miss counter** so only misses at the new load count. *(PC: Bell 2025 ~10%; reset DC.)*
   - Non-evaluable exposures between two misses are skipped: they neither count nor reset.
6. **Otherwise hold.** Prescribed reps = `rep_min–rep_max` (or `rep_min–rn` in rep-extension) at `presc_rir`.

Worked examples (verified by simulation):

| Slot | Last exposure | Result |
|---|---|---|
| Barbell squat 6–10 @2, inc 2.5, step 5% | 100 kg, all sets 10 | **105 kg** (k=2; reps_needed 8 ≤ 10) |
| Bench 8–12 @2, inc 2.5, step 2.5% | 60 kg, all sets 12 | **62.5 kg** (reps_needed 10) |
| Leg press 8–12 @2, inc 5, step 5% | 200 kg, all sets 12 | **210 kg** |
| DB curl 12–20 @2, inc 2/hand | 8 kg, all sets 20 | Hold; **rep-extension to 23** (current draft: stuck forever) |
| Cable pushdown 10–15 @1, inc 5 | 20 kg, all sets 15 | Hold; **rep-extension to 21** |
| Lateral raise 12–20 @1, inc 2/hand | 4 kg, all sets 20 | Hold; **`increment_too_coarse`** (needs 34 reps) |

#### 5.2 Bodyweight exercises
- Progress reps only. `rep_max` may go up to 30.
- Flag `rep_cap` after 2 consecutive evaluable exposures with all sets ≥ `rep_max`. *(keep; E-mod: Plotkin 2022; ACSM 2026 load range.)*

#### 5.3 Prescribed effort
- **Build weeks:** `presc_rir = target_rir`, constant within the block. *(E-high that periodization doesn't matter for hypertrophy, Moesgaard 2022; constant RIR DC.)*
- **Deload week:** `presc_rir = min(4, max(target_rir + 2, 3))`. *(PC: Bell 2023/2025.)*
- **Gap first exposure:** `presc_rir + 1` (see 5.4).
- **v2 option (not v1):**
  - Ramp offsets: week 1 +1, week 2 0, week 3 −1. Floors: compounds 1, isolation 0.
  - Requires effort-normalized triggers: `rep_max_eff = rep_max − (target_rir − presc_rir_w)`.
  - *(PC: Graham & Cleather 2021 design.)*

#### 5.4 Modifiers (applied after 5.1)
**No stacking:** at most one load reduction per set; apply the single largest, never the product. *(DC)*

| Modifier | Sets | Load | RIR | `load_modifier` | Tag |
|---|---|---|---|---|---|
| Deload week | `ceil(sets/2)` | last build load × 0.90 | per 5.3 | `deload` | PC (Bell); E-low (Coleman, Pancar: neutral for growth) |
| `d_ex` ≤ 13 days | — | no change | — | `none` | E-low (Coleman 1 wk; Hwang 2 wk) |
| `d_ex` 14–27 | — | ×0.95 | +1 | `gap` | PC/DC |
| `d_ex` 28–55 | −1 (min 1) | ×0.90 | +1 | `gap` | PC/DC; E-mod dose-response (Bosquet) |
| `d_ex` ≥ 56 | −1 (min 1) | ×0.80; ≥180 days → NULL (calibrate) | +1 | `gap` | PC/DC; E-low (Halonen) |
| Agent `reduce_load` | — | ×0.90 | — | `review_reduce` | keep |

- `d_ex` = days since this exercise's last completed exposure. It replaces the global "since last session" gap for load purposes. *(DC)*
- **Fast return:** after a `gap` exposure, if the next evaluable exposure meets the 5.1 R4 trigger, the next load is `max(R4 result, min(pre_gap_load, last × 1.10))`. *(E-low: Halonen 2024 rapid regain; DC.)*
- **Global gap** `d_any` (days since the last completed session):
  - 14–20 → resume the block where it stopped.
  - ≥ 21 → re-plan trigger (§6.1). No session is generated until the new block exists. *(DC)*
- **Gap counts as deload:** a gap of ≥ 7 days that overlaps the deload week or ends at its start → mark the remaining deload sessions `skipped`, set the block to `completed`, and call `block_plan`. *(E-low: Coleman 2024; ⚑ D1-adjacent, see flags.)*
- **Exclusions:** unchanged. Any slot matching an active `limitation` is dropped.

#### 5.5 Session sequencing
Unchanged: sessions run through `(week, day_index)` in order. Two additions:
- the gap-as-deload rule (5.4);
- the `fatigue` review trigger (5.6) does not alter sequencing.

#### 5.6 Flags emitted to summaries (§6.3)

| Flag | Rule | Tag |
|---|---|---|
| `stalled` (exercise) | **(a)** e1RM-eligible exercise: best exposure e1RM not ≥1% above its prior best for 4 consecutive evaluable exposures. **(b)** Otherwise: no load increase and no rise in total reps at that load for 4 evaluable exposures. **(c)** Or: 2 miss-reductions within 42 days | PC/DC |
| `increment_too_coarse` | 5.1 R4, `rn > 30` | DC |
| `rep_cap` | 5.2 | keep |
| `early_stop` | 5.0 | DC |
| `fatigue` (session) | During build weeks: ≥2 slots with evaluable misses in the same week, OR ≥2 exercises with exposure e1RM ≥5% below their block best on 2 consecutive exposures | PC (Bell: reactive deloads allowed; triangulate performance); thresholds DC |
| `pain_recurrent` | Same exercise with pain ≥4 in ≥2 sessions within 14 days | DC on PC bands |
| `red_flag` | Session note matches a red-flag keyword list (see §6.5 S4) | PC (London Bridge) + DC |
| Per-muscle status (block end) | **progressing:** any 1.0-weight exercise for the muscle improved best e1RM vs last block, or progressed reps-at-load, or has `rep_cap`. **stalled:** not progressing for 2 consecutive blocks AND adherence ≥0.9 AND no pain ≥4 AND no reductions. **overreached:** ≥50% of the muscle's direct slots had a reduction, OR adherence <0.8, OR `pain_recurrent` | DC |
| `volume_suggestion` (advisory) | progressing → hold; stalled → `+max(2, round(0.2 × weekly_sets))` up to the soft max; overreached → `−max(2, round(0.2 × weekly_sets))` down to the hard min. Two raises in a row without progress → `volume_ceiling_reached`; stop raising | EXP (Krieger ~20%); E-mod hold-when-progressing (Barsuhn, Camargo); thresholds DC |

---

## Schema, validator and default changes the rules require

### §4 data model

```sql
-- 1. Fractional volume needs an exercise -> muscle map (Pelland 2025). New table.
CREATE TABLE exercise_muscle (
  exercise_id INTEGER NOT NULL REFERENCES exercise(id),
  muscle TEXT NOT NULL CHECK (muscle IN ('chest','back','quads','hamstrings','glutes',
         'side_delts','rear_delts','front_delts','biceps','triceps','calves','abs')),
  weight REAL NOT NULL CHECK (weight IN (1.0, 0.5)),
  PRIMARY KEY (exercise_id, muscle)
);

-- 2. Agent tie-breaker for long-muscle-length variants (low-certainty evidence).
ALTER TABLE exercise ADD COLUMN stretch_bias INTEGER NOT NULL DEFAULT 0;

-- 3. Define the pain scale (in CREATE TABLE set_entry):
--    pain INTEGER NOT NULL DEFAULT 0 CHECK (pain BETWEEN 0 AND 10)

-- 4. Record which modifier shaped each prescription (D3-consistent; drives "evaluable").
ALTER TABLE set_entry ADD COLUMN load_modifier TEXT NOT NULL DEFAULT 'none'
  CHECK (load_modifier IN ('none','deload','gap','recalibrate','review_reduce'));

-- 5. Non-blocking validator output.
ALTER TABLE agent_call ADD COLUMN warnings TEXT;
```

The existing `set_entry.presc_reps_max` already carries rep-extension targets, and the existing `block.weeks` / `block.deload_week` already support longer blocks if D1 is ever reopened.

**Seed mapping for `exercise_muscle`** (PC/DC except where noted):

| Exercise family | 1.0 | 0.5 |
|---|---|---|
| Flat/incline press, push-up, dip, chest fly (fly: chest only) | chest | triceps, front_delts |
| Overhead press | front_delts | triceps, side_delts |
| Row, pulldown, pull-up | back | biceps, rear_delts |
| Squat, lunge, split squat | quads, **glutes** | — |
| Leg press, hack squat | quads | glutes |
| RDL, deadlift, good morning | hamstrings | glutes |
| Hip thrust | glutes | — (**no hamstrings**) |
| Leg curl / leg extension / calf raise / lateral raise / rear fly, face pull / curl / triceps extension / core | the target muscle only | — |

The squat→glutes 1.0 weight and the hip thrust→no-hamstrings choice follow [Plotkin 2023](https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2023.1279170/full): squat matched hip thrust for glute max growth, and neither grew the hamstrings. That evidence is **E-low** (a single RCT in untrained participants).

### §6.1 triggers
- `block_plan`: gap ≥ **21** days (was 14); the other triggers are unchanged.
- `session_review`: fires on any of:
  - pain ≥ **4** (was any pain);
  - any note;
  - a miss (new definition);
  - `early_stop`;
  - an unplanned exercise;
  - `fatigue`;
  - `pain_recurrent`;
  - `red_flag`.

  Pain 1–3 is logged and summarized but does not call the LLM. *(DC; consistent with Silbernagel's "≤5 acceptable if it settles".)*

### §6.2 / §6.4 actions
- Add a `drop_slot` action (scope `next_session` or `rest_of_block`). The current fallback already drops painful slots, but the agent has no way to do the same. *(DC)*

### §6.3 summary additions
- **Lifter:** tier.
- **Per muscle:**
  - planned and achieved weekly fractional sets (last block);
  - status (progressing / stalled / overreached);
  - `volume_suggestion`;
  - `volume_ceiling_reached`.
- **Per exercise:**
  - all §5.6 flags;
  - `d_ex`;
  - max pain over the last 14 days;
  - `stretch_bias`;
  - its `exercise_muscle` rows;
  - effort class.
- **Per day of the last template:** estimated minutes.

### §6.5 validators

`block_plan` checks run on **build weeks**. Fractional sets = `Σ sets × weight` per muscle. "Tier-A" muscles are chest, back, quads, hamstrings, glutes and side_delts.

| ID | Rule | On fail | Tag |
|---|---|---|---|
| V1 | Tier-A weekly fractional sets ≥ 4 (warn instead if no candidate can train that muscle) | reject | E-mod (Pelland MED ≈ 4) |
| V2 | Tier-A weekly ≥ 10 (novice: ≥ 6) | warn | E-high (ACSM ≥10); novice exception PC |
| V3 | Any muscle > soft max (table below) → warn; > 24 → reject | warn / reject | PC soft max; DC hard cap anchored to sparse data >25 (Pelland) |
| V4 | Per session per muscle: > 11 → reject; > 8 → warn | reject / warn | E-low (Remmert preprint); EXP (Krieger 6–8) |
| V5 | Each Tier-A muscle hit (≥ 1.0 fractional) on ≥ 2 distinct days; non-Tier-A muscles with ≥ 6/wk on only 1 day → warn | reject / warn | E-high (ACSM ≥2×/wk) |
| V6 | Sets per slot outside 1–6 → reject; 1 or 6 → warn | reject / warn | keep; PS (≥2 sets/exercise, secondary) |
| V7 | `rep_min ≥ 5` unless goal = strength; `rep_max ≤ 30`; `2 ≤ rep_max − rep_min ≤ 8` | reject | E-high (Lopez); span PC/DC |
| V8 | External-load compound `rep_max` > 15 → reject; > 12 → warn (no e1RM). Isolation `rep_max` > 20 → warn (RIR unreliable) | reject / warn | E-mod (Reynolds, Halperin) |
| V9 | Goal ∈ {hypertrophy, general}: `target_rir ≤ 3` (deload RIR is engine-applied). Outside the class range → warn: HEAVY 1–3, COMPOUND 1–3 (stable 0–3), ISOLATION 0–2 | reject / warn | E-mod (Robinson, Refalo); class split PC |
| V10 | `est_min = 6 + Σ sets × m + n_slots + 2 × max(0, n_compound_slots − 1)`, with `m` = HEAVY 3.25, COMPOUND 2.75, ISOLATION 2.0. Reject if `est_min > 1.1 × session_minutes` or working sets > 30. Replaces `sets ≤ session_minutes/3` | reject | PC (RP 30-set cap); DC (`m` = default rest + ~45 s set) |
| V11 | 3–8 slots per day | warn | PC |
| V12 | Coverage, each warn only if an eligible candidate exists: no leg curl; no side-delt isolation; no overhead triceps extension; no calf raise; no leg extension | warn | E-low (Plotkin 2023, Maeo 2021/2023); EC (Schoenfeld) |
| V13 | Weekly pull sets ≥ 0.9 × push sets | warn | PC |
| V14 | An isolation/core slot before a compound on the same day; barbell squat and hinge in adjacent positions with `target_rir ≤ 2` | warn | E-mod that order is irrelevant for growth (Nunes) → warn only |
| V15 | Versus the previous block: < 60% of exercises kept (excluding limitation removals); > 1 compound changed per day; a progressing exercise rotated out | warn | E-low (Kassiano 2022) + PC |
| V16 | Every slot's exercise has `exercise_muscle` rows | reject | DC (seed integrity) |

**Per-muscle volume table** (weekly fractional sets; used by V2/V3 and as agent defaults; **PC**, built from meta-analytic ranges plus RP landmarks [RP](https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth), never tested per muscle):

| Muscle | Tier | Novice | Intermediate | Advanced | Soft max |
|---|---|---|---|---|---|
| chest | A | 8 | 12 | 14 | 20 |
| back | A | 10 | 14 | 16 | 22 |
| quads | A | 8 | 12 | 14 | 18 |
| hamstrings | A | 6 | 10 | 12 | 16 |
| glutes | A | 6 | 8 | 10 | 20 |
| side_delts | A | 6 | 10 | 12 | 22 |
| rear_delts | B | 4 | 6 | 8 | 16 |
| front_delts | B | 0 direct | 0 direct | 0 direct | 12 total |
| biceps | B | 6 | 10 | 12 | 20 |
| triceps | B | 6 | 10 | 12 | 18 |
| calves | B | 6 | 8 | 10 | 16 |
| abs | B | 4 | 6 | 8 | 16 |

`session_review` validators:

| ID | Rule | Tag |
|---|---|---|
| S1 | Swap keeps `movement_pattern`; for `isolation` and `core` it must also keep an identical set of 1.0-weight muscles | DC |
| S2 | Pain 4–5 on a slot → action ∈ {`hold_load`, `reduce_load`, `swap`, `drop_set`}. Pain ≥ 6 → {`swap`, `drop_slot`}. `pain_recurrent` → scope must be `rest_of_block` | PC (Silbernagel, SRALab bands); cut-points DC |
| S3 | Never increase load (keep) | keep |
| S4 | `red_flag` (code keyword match: numb, tingl, weak, night pain, swell, lock, giving way, pop, tear, chest pain, dizz, faint, bladder, bowel) → code drops affected slots for the next session regardless of agent output, and the app shows a fixed "see a qualified clinician" message. The agent's message must not diagnose | PC (London Bridge) + DC |
| Fallback | Unchanged, plus: slots with pain ≥ 4 are dropped for the next session | DC |

Warnings never trigger a retry. They are stored in `agent_call.warnings` and shown with the rationale. *(DC)*

### §8 defaults diff
- RIR stays optional, but the UI prompts for it on the **last working set** of each slot. *(E-mod: later sets and sets near failure are rated more accurately, Halperin.)*
- Double progression with a relative step, the Epley guard and rep-extension.
- Constant target RIR within a block; deload RIR ≥ 3.
- Fractional set counting (1.0 / 0.5).
- Pain scale 0–10; review at pain ≥ 4.
- Per-exercise gap thresholds; re-plan at 21 days.
- Rest shown per class: HEAVY 150 s, COMPOUND 120 s, ISOLATION 75 s, floor 60 s. Display only. *(E-mod floor, Singer; defaults PC, chosen within each class's range because >90 s adds no growth.)*
- No tempo field. The agent may give the cue "control the lowering, lift with intent" *(E-mod, Schoenfeld 2015)*.
- Drop sets and supersets stay non-goals; in v2 they would be time-savers only.

### Locked-decision flags (do not apply without jaekim03)

| Proposal | Touches | Conflict | Recommendation |
|---|---|---|---|
| Block length 5–6 weeks, or a deload that is conditional for novices without fatigue flags | **D1** | D1 fixes the block at 3 build + 1 deload | **Keep 3+1 for v1.** The evidence says deloads are neutral for growth, and the consensus cadence is 4–6 or 4–8 weeks. The fixed deload costs 8–12.5% of block sets (simulated: 3-set slots −8.3%, 4-set slots −12.5%). Open this as a one-way question; the schema already supports it |
| Gap ≥ 7 days at the deload week counts as the deload | **D1** (adjacent) | Skips the scheduled deload sessions | Low risk and evidence-aligned (Coleman). jaekim03 to confirm |
| Code-enforced split templates by days/week | **D2**, §6.2 | Split choice belongs to the agent | Keep templates as **agent defaults**. Validators enforce outcomes only (V4, V5, V10) |
| Binding `volume_suggestion` | **D2** | The set scheme belongs to the agent | Keep it **advisory**. Code enforces only the bounds (V1, V3) |
| Within-block RIR ramp | D2 (code side) | No conflict, but adds effort-confounded progression | Not in v1 |
| Readiness-based deloads | Q4 / non-goals | Daily readiness is out of scope | The `fatigue` flag uses logged performance only |

**DECISIONS.md two-way entries to log:**
- tier cut-points
- `step_pct`
- evaluable/miss/early-stop definitions
- miss-counter reset
- recalibration ±3 / ±20%
- gap table
- re-plan at 21 days
- no-stacking
- stall thresholds (4 exposures, 1%, 42 days)
- fatigue thresholds (≥2 slots, 5%)
- volume status thresholds (0.9 / 0.8 adherence, 2 blocks, ±20%)
- per-muscle volume table
- session caps (8 warn / 11 reject / 24 hard)
- time-estimate `m` values
- coverage, order and carry-over warnings
- pain bands and the review threshold
- `exercise_muscle` seed weights
- `drop_slot` action

## Agent principles for the system prompt

The block below is written to paste directly into the agent's system prompt. It cites by author-year (the agent should not emit URLs). It separates hard constraints, which code enforces, from evidence and from conventions, so that the agent's rationale text keeps the same epistemic labels as this report.

```text
ROLE
You are an evidence-based hypertrophy coach for one lifter. You plan 4-week blocks
(3 build weeks + 1 deload) and review sessions that need interpretation. You choose
exercises, sets, rep ranges and target RIR. Code computes every load: never output a
load, percentage or e1RM. Return JSON only, matching the schema.

HARD CONSTRAINTS (code rejects violations)
- Exercises only from the candidate list. Swaps keep movement_pattern; isolation/core
  swaps also keep the same primary (1.0) muscles.
- Count weekly fractional sets: 1.0 per primary muscle, 0.5 per secondary (given per
  candidate). Chest, back, quads, hamstrings, glutes, side delts: >=4/week and trained on
  >=2 days. No muscle >24/week or >11 in one session.
- Build-week slots: target_rir 0-3, rep_min >=5, rep_max <=30, rep span 2-8, sets 1-6,
  estimated session time <= 1.1 x session_minutes. Deload changes are applied by code.
- Session review: never increase load. Pain 4-5 -> hold_load, reduce_load, swap or
  drop_set. Pain >=6 -> swap or drop_slot. Recurrent pain -> scope rest_of_block and
  suggest the user add a limitation. Never diagnose.

WHAT THE EVIDENCE SAYS (strongest first; cite author-year when you use it)
1. Weekly hard sets per muscle drive growth with diminishing returns: most gain by ~10,
   still worthwhile 10-20, little per set beyond ~20 (Pelland 2025; ACSM 2026).
   Trained lifters grow as well holding ~12-18 sets as adding many more (Barsuhn 2024;
   Camargo 2026). Do not add volume to someone who is progressing.
2. Effort: end sets at 0-3 RIR. 1-2 RIR grows about as well as failure with less
   fatigue (Robinson 2024; Refalo 2024). Failure is for the last set of isolation or
   machine work, not heavy barbell squats or hinges.
3. Load is flexible: ~5-30 reps all grow muscle near failure (Lopez 2021; ACSM 2026).
   Heavier compound work (<=10 reps) adds strength.
4. At equal volume, frequency, split, exercise order and periodization model barely
   matter for growth (Pelland 2025; Ramos-Campo 2024; Nunes 2021; Moesgaard 2022).
   Use them to fit volume into the schedule and to keep each session <=8 sets/muscle.
5. Rest >=60 s; beyond ~90 s adds little growth (Singer 2024). Tempo 0.5-8 s/rep is
   equivalent; never prescribe >10 s reps (Schoenfeld 2015).
6. Full ROM by default. Lengthened partials ~ full ROM (Wolf 2025). Long-muscle-length
   variants are a LOW-certainty tie-breaker (Wolf 2025 review; Varovic 2025 found
   trivial differences). Prefer stretch_bias candidates only when otherwise equal.
7. Compounds leave gaps: squats/hip thrusts barely grow hamstrings (Plotkin 2023);
   presses miss side/rear delts; overhead triceps work beat pushdowns (Maeo 2023);
   seated beat lying leg curls (Maeo 2021).
8. Machines ~ free weights for growth (Haugen 2023). EMG and pump do not predict
   growth: never justify a choice with them.
9. Deloads neither add nor cost growth (Coleman 2024; Pancar 2026). 1-2 weeks off
   costs little; lost size returns quickly (Halonen 2024).
10. Conventions, not evidence (label them as such if used): MEV/MAV/MRV landmarks,
   weekly +1-2 set ramps, RIR ramps, 3-4 week accessory rotation, push:pull >=1.

BLOCK PLANNING
1. Read the summaries: tier, days, minutes, equipment, limitations, per-muscle status
   and volume_suggestion, per-exercise flags, last block's template.
2. Split by days (default; deviate only with a stated reason): 2 = full body x2;
   3 = full body x3 (or FB/upper/lower); 4 = upper/lower x2; 5 = U/L/push/pull/legs;
   6 = push/pull/legs x2.
3. Weekly fractional sets per muscle: start from last block, adjusted by
   volume_suggestion; on a first or post-gap block use tier defaults:
   chest 8/12/14, back 10/14/16, quads 8/12/14, hamstrings 6/10/12, glutes 6/8/10,
   side delts 6/10/12, rear delts 4/6/8, biceps 6/10/12, triceps 6/10/12,
   calves 6/8/10, abs 4/6/8, front delts 0 direct (novice/intermediate/advanced).
   Hold if progressing; +~20% (>=2 sets) only if stalled with good adherence and no
   pain; -~20% if overreached; stop raising after two raises without progress.
4. Distribute: every major muscle on >=2 days, <=8 fractional sets per session.
5. Exercises: one main compound per pattern, then fill gaps (leg curl - seated if
   available; leg extension; lateral raise; rear fly/face pull; overhead triceps
   extension; curl; full-stretch calf raise). Prefer stable, comfortable, finely
   loadable options, and respect stated dislikes.
6. Order: main compound first, secondary compounds, isolation, calves/core last.
   A priority muscle may lead.
7. Rep ranges and RIR: barbell squat/hinge 6-10 @2; other compounds 8-12 @2
   (machines/cables @1); isolation 10-15 or 12-20 @1. Typically 2-4 sets per slot.
   Keep external-load compounds at rep_max <=12 so progress can be tracked.
8. Carry-over: keep >=60% of exercises and every exercise still progressing; change
   <=1 compound per day; rotate 1-3 accessories when stalled, rep_cap,
   increment_too_coarse, pain or boredom. For increment_too_coarse, pick a heavier rep
   range or a finer-increment variant (cable/machine).
9. Short on time: trim abs, calves, rear delts, direct front delts, glutes, then arms,
   then major muscles. Never take a major muscle below 4.
10. Rationale (<=120 words): split, weekly sets for each major muscle, what changed
   versus last block and why, pain-driven changes, and the confidence of any
   non-obvious choice.

SESSION REVIEW
- One miss: no action (code holds). Two misses: code reduces; consider a swap only
  if the exercise is stalled.
- early_stop or a time/equipment note: no adjustment; acknowledge it.
- fatigue flag: drop_set + reduce_load, scope next_session (a one-session deload).
- Pain 1-3 that settles: no change. Pain 4-5: hold_load or reduce_load next_session,
  or swap to a tolerated variant (different implement, grip, angle or ROM). Pain >=6,
  pain that changed technique, or recurring pain: swap or drop_slot for rest_of_block
  and suggest recording a limitation. Pain that persists or worsens week to week ->
  recommend seeing a clinician.
- red_flag: code drops the slots; your message tells the user to see a qualified
  clinician and contains nothing diagnostic.
- Unplanned exercise: acknowledge it; consider it at the next block if it fits.
- stalled: no in-block change unless pain; plan a rotation or rep-range change at the
  next block.

COMMUNICATION
Be brief and specific, with numbers first. Label evidence vs convention. State
uncertainty plainly: most data come from young, mostly male lifters over 8-12 weeks.
Never promise results, never prescribe complete rest for mild pain, and never
diagnose.
```

## Conclusion

The evidence supports a simpler training model than the draft assumes. Volume stays flat within a block, RIR stays constant, there is no periodization scheme, and frequency and split are tools for distributing volume. Doing this well therefore depends less on exercise science and more on **bookkeeping**: counting fractional sets per muscle, deciding which exposures are evaluable, and keeping one load reduction from stacking on another. That bookkeeping is where the current spec breaks. Its failures are not science errors but arithmetic and state-machine errors: a deadlock, a reduction spiral, stacked reductions and an over-broad swap rule. Unit tests on the worked examples above would have caught each one.

Two structural limits remain. First, the engine steers hypertrophy volume through strength proxies (e1RM, reps-at-load), because it cannot observe muscle size; per-muscle volume decisions will be noisiest exactly where they matter most, in trained lifters on flat curves. Second, the decision with the most leverage is block cadence: the fixed 4th-week deload costs up to 12.5% of block sets and buys no growth. That cadence is locked under D1, so whether to reopen it is a question only jaekim03 can answer.
