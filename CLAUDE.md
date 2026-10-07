# workout-coach

Single-user workout logger and hypertrophy coach agent. `DESIGN.md` is the spec;
`DECISIONS.md` records every decision. Read both before changing anything.

## This repo is public

Anything pushed is permanent. Treat every rule below as absolute.

## Privacy (D6, DESIGN §13.2)

- Never read `$COACH_DATA_DIR` (`~/.workout-coach/`) or `.env`.
- Never put real values in code, tests, docs, `DECISIONS.md`, commit messages, PR
  text or issues. Real values means anything from jaekim03's actual use of the app:
  profile, loads, reps, RIR, pain, notes, limitations, plans, agent inputs and
  outputs, screenshots.
- Bugs seen with real data: reproduce with synthetic data in a test, then fix.
  Commit only the synthetic test.
- CI and tests never print database contents or LLM inputs/outputs from real use.
- Test data comes from `tests/factories.py`. Never import, sample or transform
  the real database to make fixtures.
- If unsure whether something is personal, treat it as personal and ask.

## Building

- Build only what `DESIGN.md` specifies, in the §10 order. Anything not covered:
  add it to `DECISIONS.md` as `open`, use the documented default if one exists,
  otherwise stop and ask.
- One-way decisions are jaekim03's (`/decisions`). Two-way: pick the default, log
  it, continue. A new decision that contradicts a locked one: stop and flag.
- All load and rep math lives in `src/coach/engine/` as pure functions with unit
  tests. The LLM never outputs a load number.
- Every engine threshold is a named constant in `src/coach/config.py` with a
  `# D-<n>` comment. Engine modules contain no numeric literals except 0, 1 and
  subscript indices.
- No UI until the platform decision (D-7) is locked.

## Workflow (DESIGN §13.1)

- One branch and PR per build step: `step-<n>-<slug>`. Never push to `main`.
- Commits: conventional style with decision IDs, e.g.
  `feat(engine): rep-extension progression [D-18, D-20]`.
- Before opening a PR: run `make check`, then the `decision-auditor` agent.
- jaekim03 merges every PR.

## Commands

- `make setup`: install dependencies and the pre-commit hooks
- `make test`: run pytest
- `make check`: the checks CI runs (privacy guard, decision checker, tests)
