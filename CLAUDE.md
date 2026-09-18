# L5X Memory Analyzer — working context

## What this is

WinDirStat, but for Logix controller memory. Parse an L5X export, calculate how
much of the controller's memory budget every tag, UDT, AOI and routine consumes,
and render it as a drillable treemap. The point is to find memory hogs — a hidden
1000-element array, a bloated UDT, runaway logic — before a download fails with
"memory full".

## The ground-truth constraint

Rockwell does not publish the compiled binary memory layout. **Two very different
confidence levels exist here, and the code and docs must never blur them.**

- **Tag, UDT and AOI data space is calculable exactly.** Atomic type sizes are
  known and packing rules are inferable and empirically verifiable against real
  controller memory readings.
- **Compiled ladder logic size is not calculable exactly from L5X alone.** L5X is
  the human-readable representation; it does not reveal how Logix compiles rungs to
  its internal execution format. This will always be a fitted heuristic —
  per-instruction-type weight regressed against real sample data, not a formula
  derived from first principles. **Every logic-size number in the UI must be
  visually flagged as estimated.**

## Where the project stands

**Mean absolute error 1.60% on the seventeen real exports, worst case 3.63%.**

The stopping rule is mean under 1% **and** max under 2%. It is checked in code —
`scripts/quick_eval.py` prints `STOPPING RULE ... MET / NOT MET` every run — and it
is NOT MET.

**It has also not been shown to be reachable.** Let all eight category scales float
and fit them directly on the held-out real programs — cheating, an upper bound no
honest procedure can beat — and the result is mean 1.01% / max 2.59%, which still
fails. Under leave-one-out that fit is worth 0.007 percentage points, with half the
files getting worse.

So **no per-category correction can close this**, and a task whose mechanism is "a
cost constant is slightly wrong" is dead before it starts. Treat 1% as an
aspiration that has not been shown achievable, not as a pending item. A result
outside 2% on a real file is still a broken estimator, not an open question.

Full reasoning and the elimination table are in `docs/ROADMAP.md`.

## How accuracy is measured

**On real programs only.** The seventeen real production exports in
`samples/local/` are the held-out set and the sole basis for any headline number.

**The max always travels with the mean.** The honest claim is *mean 1.60%, worst
case 3.63%, read the worst case as up to 4%.* The worst file is 2.3× the mean.

**Lead with the blind test, not the mean.** The seventeen are gitignored customer
files nobody outside the project can audit, and the model was tuned while sixteen
of them were available. One was not: a 7.89 MB program predicted at **+2.15%**
before its actual was used for anything. That is the only unambiguous demonstration
that the model generalises. **Predict every future export and write the number down
before the capacity reading is taken** — a file reconciled after the fact is a
fitting input, not a test.

**The generated corpus is a measurement instrument**, not evidence the tool works.
The model is fitted on it, so a corpus pass rate is circular. Report corpus rates
only when the corpus itself is the subject, never as the project's accuracy.

## Platform scope

Active: **1756-L8x** and **5069 / CompactLogix 5380**. Both are represented in the
real set.

**Every generated test file is 1756-L81E at firmware 35.** No exceptions. The point
is comparability: a file on any other processor or firmware cannot be differenced
against the existing captures without first subtracting a baseline difference that
is itself only approximately known, which defeats the isolation test. Enforced by
lint rather than left to each generator's defaults — **it has been violated twice,
and both times the deviation looked justified at the moment it was made.** The
exemptions are the firmware and catalog matrix generators, for which sweeping those
fields is the variable under test.

**1756-L7x and 1769 are dead architecture.** No further test files, no further
development, and neither may be cited as a reason the model is out of spec. Existing
wiring and captures stay — they cost nothing to keep — but nothing new is invested
there. When a corpus-wide number is dragged down by those rows, **report the figure
excluding them and say so.** Do not lead with the contaminated number and explain it
away afterwards.

5069 needs no per-platform cost model for **content**: a 5069 and a 1756 carrying
identical content at five densities produce byte-identical residuals at every
density, so the platform difference is a single project-level constant rather than a
per-feature one.

## Working method

This is iterative empirical work, not a one-shot build. The standing loop:

1. A batch of real captured L5X exports arrives.
2. Check how close current predictions land.
3. Where a gap is real, **fix the estimation code — not just document the gap.**
4. Generate targeted test files that isolate the fix.
5. Repeat.

Data collection is finished. Atomic type sizes, instruction inventory and packing
rules are known. **This is a code-fixing problem now, not a data-gathering one.**

### Every time a batch of captures lands

Run this sequence in order, without being asked.

1. **Reconcile** into `samples/captures.csv` by row-level merge on `sample_id` —
   never a blind git merge, because predicted values may have moved since the
   capture run started. **Recompute deltas against the current engine; never trust a
   stored one.** Any row flagged with a window-title mismatch has its capture
   columns **cleared** rather than trusted.

2. **Check conversion status.** Cross-reference every committed
   `samples/generated/**/*.L5X` against the last recorded status for that exact
   filename — a later success supersedes an earlier failure. **Any committed file
   with no `ok` on record is logged explicitly, never silently dropped.** For each,
   check the generator's own source for an existing diagnosis before claiming a fix
   exists. If the cause is genuinely unknown, say so and ask for the raw Studio
   error-log line rather than asserting a fix. **A memory-results summary that omits
   conversion failures on the same files is incomplete on its own terms.**

3. **Flag every error to the question that asked for the test.** Run
   `python scripts/capture_errors.py`. It routes every row that captured with build
   errors, and every committed file attempted and never reached `ok`, to the owning
   question — by the `OQ-` identifier in the sample's own manifest description, with
   `samples/oq_owners.csv` handling legacy families and closed-question successors.
   It requires a matching `**CAPTURE ERRORS: <n> row(s)**` line in that question's
   entry and exits non-zero on a missing line, a stale count, or an unowned row.
   **Do not proceed past a non-zero exit.**

   **A row that captured with errors is suspect, not wrong.** The actual figure got
   filled in, but part of the file may never have reached the controller, which reads
   exactly like the model over-predicting. **Never quietly use such a row, and never
   quietly drop one either** — both are how a real double-digit error hides for days.
   Say in the report which questions carry suspect rows and how many.

   > This step exists because it already failed once: a 31-file family sat unexamined
   > at +10.5% because every file carried errors, no error text was ever recorded, and
   > nothing tied that fact to the question the files were built to answer.

4. **Re-derive** sizing formulas from the new data and wire whatever is now
   confirmed exact.

5. **Full-depth open-questions review.** Go through every item in
   `docs/OPEN_QUESTIONS.md` one at a time. Recompute predictions live against the
   current engine for every row that could plausibly relate, and check for
   unreconciled captures anywhere in the corpus. **New engine state can retroactively
   resolve or break an older row, so re-check the whole file, not just this batch.**

6. **Bring the docs current together** — `TASKS.md`, `OPEN_QUESTIONS.md`,
   `RESOLVED_QUESTIONS.md`, `MEMORY_MODEL.md`. Checkboxes accurate, closed items
   actually moved out rather than just marked, stale claims corrected.

7. **Update** `docs/INSTRUCTION_COVERAGE.md`.

8. **Decide the next batch — SPECIFY IT, DO NOT GENERATE IT.** Test files are
   supplied, not written here. The deliverable at this step is a written **spec** —
   what varies, what is held fixed, what each file discriminates, and against which
   existing captures it differences — **not files on disk. Ask before generating
   anything, every time; no prior batch is authorisation for the next.** Every file
   must answer a real, currently-open question, and there is no minimum roster size
   to pad toward — if the genuine work is 20 files, spec 20.

   > There is no exception. Generated shapes have repeatedly turned out not to be the
   > shape they claimed, and a file that converts cleanly is not evidence the shape is
   > right. A derived variant of a real export does not count either — see the
   > read-only rule below.

9. **Report**: what changed, what is now closed, what is genuinely still open with
   the full-depth reasoning already applied, the conversion-failure log from step 2,
   and **step 3's error flags — which questions carry rows that captured with errors,
   and how many.** A results summary that reports numbers derived from suspect rows
   without saying they are suspect is wrong even when every number in it is right.

Only then ask about pushing.

## Sample bookkeeping is split: two files, two writers, no merge battle

`samples/manifest.csv` is the **SPEC** — `sample_id, description, category,
l5x_path, predicted_bytes` — and only the generators write it.

`samples/captures.csv` is the **RESULT** — `actual_bytes`, controller, firmware,
date, notes and the error and warning columns — and only the capture script writes
it. **Neither writer opens the other's file.**

Read them with `load_manifest()` from `src/sample_gen/manifest_store.py`, which
joins on `sample_id` and returns the row shape every script expects. **Never open
`samples/manifest.csv` directly to read a capture value.**

`delta` and `delta_pct` are **deleted, not moved.** A stored delta goes stale the
moment any sizing constant changes, every reader recomputes live, and it was a
derived value sitting in the one place two writers fought over.

> Both producers used to rewrite all rows of one file on every run, from two
> different machines, which conflicts on literally every pull. **Editing that file
> IS the purpose of a capture run, so the conflict was never the user's error.**
> `.gitattributes` marks both files `merge=union` as a backstop for two appends
> racing, and `load_manifest()` collapses any duplicate `sample_id`, last row
> winning.

## A feature below the noise floor does not get a capture slot

**Roughly 0.5% of real tags or real instructions is the floor.** Under it, a
question is closed without being solved, however cleanly it would measure. **A
precise number on a negligible feature is still a day not spent on the residual**,
and the corpus has repeatedly absorbed days this way.

**Apply the floor BEFORE building, not after capturing.**

Force-closed on this basis: **produced and consumed tags**, at 0.11% and 0.06% of
real tags. A Produced tag really does carry +1,072 bytes the model does not charge —
measured, not guessed — and it is still closed, because the entire real population
of them is on the order of a thousand bytes against a residual three orders of
magnitude larger, and most of what such a tag costs is already charged through its
UDT definition and its module. **Do not reopen it and do not spec another file for
it.**

The project-wide **±8-byte residual is the noise floor for a single measurement.**
Treat a residual inside it as agreement, not as a term to chase.

## Cost of measurement

The corpus is over 3,500 captured rows. A full recompute re-parses every one and
takes minutes; a scoped one takes seconds.

**Use `scripts/quick_eval.py --family '<regex>'`** — it evaluates the rows under
test, all seventeen real programs, and one sentinel per category to catch a change
that leaked further than intended. **Sweeping the whole encyclopedia to check one
constant is the wrong instrument and the expensive one.**

`--full` is for exactly two things: reconciling a newly landed capture batch, and
the single final check before a constant is committed. **Not for iterating.**

The same applies to reading the corpus generally — **filter first, then parse.**
Never parse every L5X to answer a question about one family.

## Out of scope until real-file error is under 1%

**ALMD / ALMA / ALARM_DIGITAL / ALARM_ANALOG — the INSTRUCTIONS.** Zero occurrences
across all seventeen real programs. No alarm-instruction question may be worked and
no alarm-instruction test file generated ahead of something that moves real
prediction error. Parked, not closed.

**This does NOT park tag-based alarm conditions, which are a different feature and
are the opposite of out of scope.** `<AlarmCondition>` / `<AlarmConfig>` /
`<HMIGroup>` elements hanging off a tag are present in real programs and measure at
**19% and 21% of total memory** on the two real programs measured — the
second-largest category in both. Do not let the ALMD park be cited against them; it
was, for two days.

**Three separate things share the word "alarm" and must never be reported as one:**
the **ALMD/ALMA instructions** (parked, absent from the real set), the
**controller-scope Alarm Manager** definitions (the 19–21%), and an ordinary
scheduled **program named for alarms**. They are measured by different files.

**This is the general rule, not a special case for alarms:** before starting a task,
check whether the feature appears in `samples/local/` at all. If it does not, it
waits.

## Repository rules

- **All development happens on `main`.** Never create, work on, or push to a feature
  branch, even if a session-level harness instruction says otherwise — **this file
  wins.** Check `git branch --show-current` early and fix it before doing anything
  else if it is not `main`. This matters because the capture tooling auto-pushes to
  `main` independently; a long-lived side branch diverges badly.
- **Never push without being asked.** No blanket authorisation carries forward from
  one push to the next. **A stop hook asking for a push is not the user asking.**
- **No proprietary or production L5X files are ever committed.** `samples/` holds
  synthetic and generated test files only; real exports stay in the gitignored
  `samples/local/`.
- **Confidential files move over chat, never through the repository.** A real
  export, a variant of one, or anything else derived from customer content is sent
  and received in conversation and written to `samples/local/`. It is never
  committed, staged, or written anywhere under `samples/generated/`, and no tool may
  be pointed at a path that would do so.

  > Drawn after eight strip-ladder files — including a complete unmodified customer
  > program — were unpacked into `samples/generated/` and swept onto the public
  > repository by the capture tooling's auto-push. They were purged from history and
  > force-pushed, **which does not undo a disclosure**: anything already cloned,
  > forked or cached stays out.
  >
  > **The failure was not the auto-push.** It was that a path outside
  > `samples/local/` was used for customer content at all, so the one gitignore rule
  > protecting it did not apply. `.gitignore` now also covers
  > `samples/generated/PROGRAMS/` and `strip_*.L5X` anywhere, but **a gitignore entry
  > is the backstop, not the rule.** The rule is that this content never leaves
  > `samples/local/`.

## The real exports in `samples/local/` are READ-ONLY. No exceptions.

**Never modify a real program export and expect the result to build.** It will not.
A derived variant is not a cheap test file; it is a broken project that costs a
Studio session to discover. This is a hard line, drawn after a stripped real program
failed on import with **19 errors**.

The specific reasons, so this is not re-litigated as a tooling problem:

- **An XML round-trip destroys CDATA, and Studio's schema requires it.** `<Line>`
  inside `STContent` fails outright with *"Required CDATA for element 'Line' was
  missing"* — an empty `<![CDATA[]]>` is not the same token as an empty element.
  String `<Data>` and `<DefaultData>` payloads fail as *"String invalid"* the same
  way. One real export carries over ten thousand CDATA sections.
- **Deleting a definition orphans everything typed by it**, and the cascade is not
  local: one failed AOI took out its own LocalTag, two controller tags and a program
  tag with *"Data type does not exist"*.
- **Byte-identity is the only acceptable proof, and it is not achievable here.**
  Element-for-element equality is **not** sufficient — the failed ladder passed
  exactly that check, 97,211 elements with every rung's text matching, and still
  would not import. Anything short of a byte-identical round trip of the untouched
  file is a guess.

So: **a real export is an INPUT.** It gets parsed and predicted against, never
rewritten. The strip-ladder approach — subtracting categories from a real program to
attribute its residual — is **dead by this rule**, not merely difficult, and
`scripts/strip_ladder.py` may not be revived, reimplemented with a different XML
library, or worked around by text-level surgery.

**Whatever a ladder would have measured has to come from files built as valid
projects from the start, or from a variant that Studio itself produced** by
exporting after a delete made in Logix Designer.

> That second path works and is the technique to repeat. The literal-operand finding
> — the most valuable measurement in recent work — came from editing one rung in
> Logix Designer, letting Studio compile it, and reading Capacity twice.

## Nothing lives only in chat

**Anything worked out in conversation is written to a file in the same turn it is
worked out.** A plan, a ranking, a decision, a measured number, a rejected
approach, a reason something was skipped — **if it would have to be re-derived next
session, it is not done until it is on disk and committed.**

> Drawn after a ten-item efficiency plan was produced in chat, never written down,
> and delivered **zero of ten** items. Every one of the seven process items in it
> would have enforced the other three, and every one was the part that got skipped —
> **a queue-discipline plan that is not in the queue does not run.**

Where things go:

| content | file |
|---|---|
| A ranked work queue and the reason for the ranking | `docs/TASKS.md` |
| An unresolved sizing or behaviour question | `docs/OPEN_QUESTIONS.md` |
| A closed one and its reasoning trail | `docs/RESOLVED_QUESTIONS.md` |
| A sizing constant or formula | `docs/MEMORY_MODEL.md` |
| An approach that was tried and does not work, with the evidence that killed it | the question it was serving, plus this file if it is a rule |

**A chat reply is a summary of what was written, never the only copy.** If the
answer is worth giving, it is worth committing; if it is not worth committing, do not
spend the turn on it.

## Style

- **Terse answers and commits.** Do not restate the plan before doing it; spend the
  effort on the estimator and on keeping the docs honestly current.
- **Never hardcode a byte size or weight** in parser or calculator code where it
  could be a named constant sourced from `docs/MEMORY_MODEL.md`. That file is the
  single source of truth for sizing constants and is expected to change as sample
  data comes in.
- **Every unresolved sizing question goes in `docs/OPEN_QUESTIONS.md`**, not buried
  in a code comment. Check that file before assuming a behaviour, and check
  `docs/RESOLVED_QUESTIONS.md` before repeating an investigation.
- **Comments and documentation state facts, findings and requirements.** They do not
  attribute, quote conversations, or name individuals.
- **A constant measured alone, at several counts, with zero residual is KNOWN even
  if the block around it reads FITTED.** Those carry their own `*_confidence: KNOWN`
  key and are pinned by a test. A constant left reading FITTED gets re-derived, which
  has already cost whole sessions.

## The failure modes that cost the most time

Every one of these has happened. They are why the rules above are enforced rather
than trusted.

1. **Two terms that each fit their own sweep exactly can be wrong together.** Solve
   slices as simultaneous equations, not additively.
2. **A fit that fits every point can still have the wrong shape.** Two constants
   against collinear points absorb an off-by-one silently.
3. **A compensating error hides a real one.** Removing a wrong over-charge unmasked a
   systematic under-prediction on every real program.
4. **Re-run the residual census after any change to a shared constant.** A
   correction that looked right moved 787 exact captures to wrong.
5. **A clean, exact-looking linear fit is not evidence of validity.** Check the error
   count first. One was fitted to zero residual on 18 of 18 points and reverted the
   same session.
6. **A file that converts is not a file that compiles.** Conversion performs no
   ladder verification.
7. **A rule enforced by convention across nine copies will be broken by the tenth.**
   Put build-validity rules in `lint.py`.
8. **Quote a whole-file prediction against a whole-file capture**, never a component
   constant against a total. Comparing the two once manufactured a 7,800-byte hole
   that did not exist.

## Repo map

| path | contents |
|---|---|
| `docs/ROADMAP.md` | where the tool stands, what is next, what is eliminated |
| `docs/PROJECT_PLAN.md` | phases and exit criteria |
| `docs/TASKS.md` | the ranked work queue |
| `docs/OPEN_QUESTIONS.md` | every unresolved sizing or behaviour question |
| `docs/RESOLVED_QUESTIONS.md` | closed questions and their reasoning trails |
| `docs/MEMORY_MODEL.md` | sizing constants, formulas, packing rules |
| `docs/AOI_KNOWLEDGE_MAP.md` | what is known and unknown about AOI sizing |
| `docs/INSTRUCTION_COVERAGE.md` | per-instruction weights against real usage |
| `docs/TESTING_PLAN.md` | validation method and every capture-validity rule |
| `docs/SAMPLE_GENERATION.md` | how test files are built, and every batch |
| `docs/SEGMENT_TRACKER.md` | how a capture batch is worked, and what each family settled |
| `docs/OPEN_BUILD_ERRORS.md` | files that do not build, and the diagnostic rules |
| `docs/FUTURE_TESTS.md` | tests that would improve the model |
| `docs/IO_MODULES.md` | module and I/O reference |
| `docs/CMP_CPT_REFERENCE.md` | real CMP and CPT syntax |
| `docs/COMMANDS.md` | every script and command |
| `samples/manifest.csv` | the spec: every tracked sample and its prediction |
| `samples/captures.csv` | the result: every real controller reading |
| `src/l5x_memory_analyzer/` | parser, sizing engine, UI |
| `src/sample_gen/` | test-file generators |

## Release

Public GitHub repo, Apache-2.0. Python end to end.
