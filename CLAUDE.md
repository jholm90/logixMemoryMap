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
On real programs only. The **sixteen** real production exports in
`samples/local/` are the held-out set and the sole basis for any headline
accuracy number.

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

5069 **is** represented in the real set: four of the sixteen are 5069
(three on 5069-L330ERM, one on 5069-L320ERMS3). The older claim that every real
program is a 1756-L8x was true of the nine-file set and is not true now.

What 5069 does not need is a per-platform cost model for CONTENT. Measured
2026-09-14 (capture-batch segment 17): a 5069-L306ER and a 1756-L81E carrying
identical content at five densities produce **byte-identical residuals at every
density**, so the platform difference is a single project-level constant rather
than a per-feature one. See `OQ-REAL5069`.

That constant is exact on generated files and is NOT exact on real exports. The
strip ladder (2026-09-14) read a bare 1756-L81E v35 real shell at 21,096 against
a predicted 13,296, and a 5069-L330ERM shell at 17,360 against 13,288 — 3,736
apart where the engine has them 8 apart. The gap is unpriced controller-shell
content that generated files do not carry, not the baseline constant, which
remains byte-exact on every generated empty file. See `OQ-CTLSHELL`.

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
7. **Decide the next batch — SPECIFY IT, DO NOT GENERATE IT.** Test L5X files
   are supplied by James, not written by Claude. Agreed and then violated on
   2026-09-13, when 143 files were generated across four segments after the
   agreement was already in place: generated shapes have repeatedly turned out
   not to be the shape they claimed (the 2198 L5K payload, the `genem_*`
   CommMethod that silently made three files the same connection, the
   MOV-writes-to-Input lint rule), and a file that converts cleanly is not
   evidence the shape is right. So the deliverable at this step is a written
   SPEC — what varies, what is held fixed, what each file discriminates, and
   against which existing captures it differences — not files on disk. Ask
   before generating anything, every time; no prior batch is authorization for
   the next. Every file in a batch must still answer a real, currently-open
   question, and there is no minimum roster size to pad toward — if the genuine
   work is 20 files, spec 20.

   The one exception is `scripts/strip_ladder.py`, which derives variants of a
   real export James already supplied rather than inventing a shape.
8. **Report**: what changed, what is now closed, what is genuinely still
   open with the full-depth reasoning already applied, the
   conversion-failure log from step 2, and **step 2b's error flags — which
   questions are carrying rows that captured with errors, and how many**. A
   results summary that reports numbers derived from suspect rows without
   saying they are suspect is wrong even when every number in it is right.

Only then ask about pushing.

## Cost of measurement
The corpus is over 2,500 captured rows. A full recompute re-parses every one of
them and takes minutes; a scoped one takes seconds. **Use
`scripts/quick_eval.py --family '<regex>'`** — it evaluates the rows under test,
all sixteen real programs, and one sentinel per category to catch a change that
leaked further than intended. Sweeping the whole encyclopedia to check one
constant is the wrong instrument and the expensive one.

`--full` is for exactly two things: reconciling a newly landed capture batch, and
the single final check before a constant is committed. Not for iterating.

The same applies to reading the corpus generally — filter first, then parse.
Never parse every L5X to answer a question about one family.

## Out of scope until real-file error is under 1%
**ALMD / ALMA / ALARM_DIGITAL / ALARM_ANALOG — the INSTRUCTIONS.** Verified
2026-09-14: **zero occurrences across all sixteen real programs.** No
alarm-instruction question may be worked, and no alarm-instruction test file
generated, ahead of something that moves real prediction error. `OQ-ALARMDEF`
and the `almd_*` / `alarmbits_*` / `alarmdef_*` / `alarmsep_*` families are
parked on that basis, not closed.

**This does NOT park tag-based alarm conditions, which are a different feature
and are the opposite of out of scope.** `<AlarmCondition>` / `<AlarmConfig>` /
`<HMIGroup>` elements hanging off a tag are present in real programs and the
strip ladder measured them at **19% and 21% of total memory** on the two real
programs stripped (443,128 bytes over 400 conditions, 243,040 over 200). They
are the second-largest category in both files. See `OQ-ALARMCONDREAL`. Do not
let the ALMD park above be cited against them; it was, for two days.

Three separate things share the word "alarm" here and must never be reported as
one: the **ALMD/ALMA instructions** (parked, absent from the real set), the
**controller-scope Alarm Manager** `<AlarmCondition>` definitions (the 19–21%
above), and an ordinary scheduled **program** named for alarms, such as
Elmsdale's `AlarmsAndMessages`. They are measured by different files.

This is the general rule, not a special case for alarms: before starting a task,
check whether the feature appears in `samples/local/` at all. If it does not, it
waits.

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

## The real exports in `samples/local/` are READ-ONLY. No exceptions.
**Never modify a real program export and expect the result to build.** It
will not. A derived variant is not a cheap test file; it is a broken project
that costs a Studio session to discover. This is a hard line, drawn
2026-09-18 after the FlareFunction ladder failed on import with **19 errors**.

The specific reasons, so this is not re-litigated as a tooling problem:

- **An XML round-trip destroys CDATA, and Studio's schema requires it.**
  `<Line>` inside `STContent` fails outright with *"Required CDATA for
  element 'Line' was missing"* — an empty `<![CDATA[]]>` is not the same
  token as an empty element. String `<Data>` and `<DefaultData>` payloads
  fail as *"String invalid"* the same way. FlareFunction carries 10,097
  CDATA sections.
- **Deleting a definition orphans everything typed by it**, and the cascade
  is not local: one failed AOI took out its own `LocalTag`, two controller
  tags and a program tag with *"Data type does not exist"*.
- **Byte-identity is the only acceptable proof, and it is not achievable
  here.** Element-for-element equality is NOT sufficient — the failed ladder
  passed exactly that check (97,211 elements, every rung `Text` matching) and
  still would not import. Anything short of a byte-identical round trip of
  the untouched file is a guess.

So: a real export is an INPUT. It gets parsed and predicted against, never
rewritten. The strip-ladder approach — subtracting categories from a real
program to attribute its residual — is **dead by this rule**, not merely
difficult, and `scripts/strip_ladder.py` may not be revived, reimplemented
with a different XML library, or worked around by text-level surgery.

Whatever a ladder would have measured has to come from files that are built
as valid projects from the start, or from a variant that Studio itself
produced by exporting after a delete made in Logix Designer.

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
