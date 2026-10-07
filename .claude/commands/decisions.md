---
description: Ask jaekim03 the open one-way decisions and record the answers as locked
---

Resolve open one-way decisions in `DECISIONS.md`.

1. Read `DECISIONS.md`. Collect every entry with `Status: open` and
   `Type: one-way`. If `$ARGUMENTS` names decision IDs, restrict to those; an ID
   that is already locked may be named to reopen it.
2. If there are none, say so and stop.
3. Ask each one as a multiple-choice question, at most four per round. For each
   question give the options from the entry and DESIGN.md, what each option costs,
   and which one you recommend. Do not ask two-way decisions: the builder picks
   those.
4. For each answer, rewrite the entry:
   - `Status: locked`
   - `Choice:` the selected option, in jaekim03's words where they wrote their own
   - `Rationale:` one line
   - `Answered: <YYYY-MM-DD> via /decisions` (add or replace this line;
     `scripts/check_decisions.py` requires a new one whenever a one-way entry
     is locked or changed). If the entry already has a line with today's
     date, append a counter: `Answered: <YYYY-MM-DD> via /decisions (2)`.
5. An unanswered or dismissed question stays `open`. Never infer an answer.
6. If an answer contradicts another locked entry, stop and flag both IDs.
7. List the entries you changed and any build steps they unblock.

Entries must not contain personal training information (D6).
