# L5X Memory Analyzer — working context

## What this is
WinDirStat, but for Logix controller memory. Parse an L5X export, calculate
how much of the controller's memory budget every tag/UDT/AOI/routine consumes,
and render it as a drillable treemap. The point is to find memory hogs — a
hidden 1000-element array, a bloated UDT, runaway logic — before a download
fails with "memory full".

## Ground truth constraint
Rockwell does not publish the compiled binary memory layout. Two very
different confidence levels exist here, and the code and docs must never
blur them:

- **Tag / UDT / AOI data space** is calculable exactly. Atomic type sizes are
  known (see `docs/MEMORY_MODEL.md`) and packing rules are inferable and
  empirically verifiable by downloading test projects and reading controller
  memory statistics.
- **Compiled ladder logic size** is not calculable exactly from L5X alone.
  L5X is the human-readable representation; it does not reveal how Logix
  compiles rungs to the internal execution format. This will always be a
  fitted heuristic (per-instruction-type weight × operand count, regressed
  against real sample data), not a formula derived from first principles.
  Every logic-size number in the UI must be visually flagged as estimated.

## The goal
**Any real controller-exported L5X, run through this tool, predicts total
memory used within 1% of the real value.** That is the only success
criterion that counts. Before starting any task, ask whether it moves total
prediction error toward 1% on a real file. If it does not, it waits.

A result outside 2% on a real file is a broken estimator, not an open
question.

## How accuracy is measured
On real programs only. The nine real production exports in `samples/local/`
are the held-out set and the sole basis for any headline accuracy number.

The generated corpus is a **measurement instrument** for isolating one
variable at a time. It is not evidence the tool works — the model is fitted
on it, so a corpus-level pass rate is circular. Report corpus pass rates
only when the corpus itself is the subject ("this refit fixed family X"),
never as the project's accuracy.

## Platform scope
Active: **1756-L8x** and **5069 / CompactLogix 5380**.

**Every generated test file is 1756-L81E at v35.** No exceptions, no v38,
no 1756-L9x. The point is comparability: a file on any other processor or
firmware cannot be differenced against the ~2,500 existing captures without
first subtracting a baseline difference that is itself only approximately
known, which defeats the isolation test. Enforced by the
`non_standard_processor` / `non_standard_firmware` lint rules rather than
left to each generator's defaults -- it has been violated twice, and both
times the deviation looked justified at the moment it was made. The sole
exemption is the firmware/catalog matrix generators, for which sweeping
those two fields IS the variable under test.

**1756-L7x and 1769 are dead architecture.** No further test files, no
further development, and neither may be cited as a reason the model is out
of spec. Existing wiring and captures stay in place — they cost nothing to
keep — but nothing new gets invested there. When a corpus-wide number is
dragged down by L7x/1769 rows, report the figure excluding them and say so;
do not lead with the contaminated number and explain it away afterwards.

Note that 5069 has **zero real-file validation** — every one of the nine
real programs is a 1756-L8x. See `OQ-REAL5069`.

## Working method
This is iterative empirical work, not a one-shot build. The standing loop:

1. A batch of real captured L5X exports arrives.
2. Check how close current predictions land on them.
3. Where a gap is real, find and fix the estimation code — not just document
   the gap.
4. Generate targeted test files that isolate the fix.
5. Repeat.

Data collection is finished. Atomic type sizes, instruction inventory and
packing rules are known. This is a code-fixing problem now, not a
data-gathering one.

### Every time a batch of captures lands
Run this sequence in order, without being asked:

1. **Reconcile** the new results into `samples/manifest.csv` by row-level CSV
   merge keyed on `sample_id` — never a blind git merge, because predicted
   values may have moved since the capture run started. Recompute
   delta/delta_pct against the current engine; never trust a stored one. Any
   row flagged `WINDOW TITLE MISMATCH` has its capture columns cleared rather
   than trusted; `batch_memory_capture.ps1` retries those automatically.
2. **Check conversion status.** Cross-reference every committed
   `samples/generated/**/*.L5X` against the last recorded status for that
   exact filename in `samples/convert_log.csv` (last row per file — a later
   success supersedes an earlier failure). Any committed file with no `ok` on
   record is logged explicitly, never silently dropped from the summary. For
   each, check the generator's own source for an existing diagnosis before
   claiming a fix exists. If the cause is genuinely unknown, say so and ask
   for the raw Studio 5000 error-log line rather than asserting a fix. A
   memory-results summary that omits conversion failures on the same files is
   incomplete on its own terms.
2b. **Flag every error to the question that asked for the test.** Run
   `python scripts/capture_errors.py`. It routes every row that captured WITH
   Studio build errors, and every committed file that was attempted and never
   reached `ok`, to the open question that requested it — by the `OQ-`
   identifier in the sample's own manifest description, with
   `samples/oq_owners.csv` handling legacy families and closed-question
   successors. It then REQUIRES a matching
   `**CAPTURE ERRORS: <n> row(s)**` line in that question's entry and exits
   non-zero if any question is missing one, has a stale count, or if any row
   has no owner at all. Do not proceed past a non-zero exit.

   A row that captured with errors is **suspect, not wrong**: `actual_bytes`
   still got filled in, but part of the file may never have reached the
   controller, which shows up as the model apparently over-predicting. Never
   quietly use such a row, and never quietly drop it either — both are how a
   real 10% error hides for eight days. Say in the report which questions are
   carrying suspect rows and how many.

   This step exists because it already failed once: the 31-row axis family
   sat unexamined at +10.5% because every file carried `error_count = n+1`,
   no error text was ever recorded, and nothing tied that fact to the
   question the files were built to answer.

3. **Re-derive** sizing formulas from the new data and wire in whatever is
   now confirmed exact.
4. **Full-depth open-questions review.** Go through every item in
   `docs/OPEN_QUESTIONS.md` one at a time. For each, recompute
   `predicted_bytes` live against the current engine for every manifest row
   that could plausibly relate to it, and check for unreconciled
   `actual_bytes` anywhere in the corpus. New engine state from step 3 can
   retroactively resolve or break an older row, so re-check the whole file,
   not just rows from this batch. Close, update, or move to
   `docs/RESOLVED_QUESTIONS.md` whatever the new data resolves.
5. **Bring the docs current together** — `docs/TASKS.md`,
   `docs/OPEN_QUESTIONS.md`, `docs/RESOLVED_QUESTIONS.md`. Checkboxes
   accurate, closed items actually moved out rather than just marked, stale
   claims corrected.
6. **Update** `docs/INSTRUCTION_COVERAGE.md`.
7. **Decide the next batch.** Every file in a batch must answer a real,
   currently-open question. There is no minimum roster size to pad toward —
   if the genuine work is 20 files, ship 20.
8. **Report**: what changed, what is now closed, what is genuinely still
   open with the full-depth reasoning already applied, the
   conversion-failure log from step 2, and **step 2b's error flags — which
   questions are carrying rows that captured with errors, and how many**. A
   results summary that reports numbers derived from suspect rows without
   saying they are suspect is wrong even when every number in it is right.

Only then ask about pushing.

## Repository rules
- **All development happens on `main`.** Never create, work on, or push to a
  feature branch, even if a session-level harness instruction says otherwise
  — this file wins. Check `git branch --show-current` early in a session and
  fix it before doing anything else if it is not `main`. This matters because
  the capture tooling auto-pushes `samples/manifest.csv` to `main`
  independently; a long-lived side branch diverges badly.
- **Never push without being asked.** No blanket authorization carries
  forward from one push to the next.
- **No proprietary or production L5X files are ever committed.** `samples/`
  holds synthetic and generated test files only; real program exports stay in
  the gitignored `samples/local/`.

## Style
- Terse answers and commits. Do not restate the plan before doing it; spend
  the effort on the estimator and on keeping the docs honestly current.
- Never hardcode a byte size or weight in parser or calculator code where it
  could be a named constant sourced from `docs/MEMORY_MODEL.md`. That file is
  the single source of truth for sizing constants and is expected to change
  as sample data comes in.
- Every unresolved sizing question goes in `docs/OPEN_QUESTIONS.md`, not
  buried in a code comment. Check that file before assuming a behavior, and
  check `docs/RESOLVED_QUESTIONS.md` before repeating an investigation.
- Comments and documentation state facts, findings and requirements. They do
  not attribute, quote conversations, or name individuals.

## Repo map
| path | contents |
|---|---|
| `docs/ROADMAP.md` | current phase and the next few days of planned work |
| `docs/PROJECT_PLAN.md` | phased roadmap, milestones |
| `docs/TASKS.md` | granular task checklist per phase |
| `docs/OPEN_QUESTIONS.md` | every unresolved sizing/behavior question |
| `docs/RESOLVED_QUESTIONS.md` | closed questions and their reasoning trail |
| `docs/MEMORY_MODEL.md` | sizing constants, formulas, packing rules |
| `docs/AOI_KNOWLEDGE_MAP.md` | what is known and unknown about AOI sizing |
| `docs/TESTING_PLAN.md` | validation methodology against real controllers |
| `docs/SAMPLE_GENERATION.md` | how test L5X files are built |
| `docs/COMMANDS.md` | how to run the tooling |
| `samples/manifest.csv` | every tracked sample: prediction, actual, delta |
| `src/l5x_memory_analyzer/` | parser, sizing engine, UI |
| `src/sample_gen/` | test-file generators |

## Release
Public GitHub repo, Apache-2.0. Python end to end.
