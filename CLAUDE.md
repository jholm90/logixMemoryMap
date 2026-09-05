# L5X Memory Analyzer — Claude Code Context

## What this is
WinDirStat, but for CompactLogix controller memory. Parse an L5X export, calculate
how much of the 4MB memory budget every tag/UDT/AOI/routine consumes, render as a
drillable treemap. Goal: find memory hogs (hidden 1000-element arrays, bloated UDTs,
runaway logic) before you're staring at a "memory full" download error.

## Ground truth constraint
Rockwell does not publish the compiled binary memory layout. Two very different
confidence levels exist here and the code/docs must never blur them:

- **Tag / UDT / AOI data space**: calculable exactly. Atomic type sizes are known
  (see docs/MEMORY_MODEL.md), packing rules are inferable and empirically
  verifiable by downloading test projects and reading controller memory stats.
- **Compiled ladder logic size**: NOT calculable exactly from L5X alone. L5X is the
  decompiled/human-readable XML representation; it does not reveal how Logix
  compiles rungs to the internal execution format. This will always be a fitted
  heuristic model (per-instruction-type weight × operand count, regressed against
  real sample data), not a formula derived from first principles. Every UI number
  for logic size must be visually flagged as "estimated."

## North star (James, 2026-08-31, "draw a line in the sand" — supersedes any
## other priority framing in this file)
**#1 and only real goal: any real controller-exported L5X, run through this
tool, predicts total memory used within <1% of the real value.** Everything
else is a distant #10, not worth time until #1 is met. Before doing ANY task,
ask: does this move total prediction error toward <1% on a real file? If not,
it waits. Anything outside 2% on a real file is not "an open question," it's
a broken estimator that needs fixing now.

Standing loop, no other shape: James pushes a batch of real captured L5X
(complex, realistic programs) → Claude checks how close current predictions
already land on them → if a gap is real, find and fix the actual estimation
code (not just document the gap) → generate new targeted test files that
isolate the fix → repeat. Data collection is over — atomic type sizes,
instruction inventory, and packing rules are known. This is now a code-fixing
problem, not a data-gathering one.

James, 2026-08-31: responses in chat should be SHORT. Spend the effort on
getting the estimator right and on keeping docs/OPEN_QUESTIONS.md,
docs/RESOLVED_QUESTIONS.md, and docs/TASKS.md honestly current — not on long
chat explanations. Before repeating any investigation, check those docs first
— repeating a mistake or a check already documented there wastes James's time
and is called out explicitly as a real problem, not a hypothetical one.

## Platform scope — 1756-L7x and 1769 are DEAD ARCHITECTURE
James, 2026-09-05: *"I'll run these tests you've made for the L7/1769 but
please consider it dead architecture and I'm happy to leave it where it
stands after these final tests. There will be no further development with
that platform and I'd rather not burn resources on it anymore. Make note of
this and don't complain it's the reason why your model is out of spec."*

Binding. After the currently-queued L7x/1769 captures land:
- **Do not generate further test files for 1756-L7x or any 1769 catalog.**
- **Do not cite either platform as a reason the model is out of spec.**
  Accuracy claims are measured on the L8x/5069 platforms that matter. If a
  corpus-wide number is dragged down by L7x/1769 rows, report the number
  EXCLUDING them and say so — don't lead with the contaminated figure and
  then explain it away.
- Leave what is already wired in place (it costs nothing to keep and the
  captures are real); just stop investing in it.

## Accuracy is measured on REAL programs, not generated files
James, 2026-09-05: *"I don't like you toting the metrics of 93% within 1%
error — your self generated files don't matter at all for these final
tests, only the sample large programs that came from real life."*

Correct, and binding. The generated corpus is a MEASUREMENT INSTRUMENT for
isolating one variable at a time; it is not evidence the tool works. A
headline accuracy number means the nine real production exports in
`samples/local/` and nothing else. Report corpus-level pass rates only when
they are the direct subject (e.g. "this refit fixed family X"), never as
the project's accuracy.

## Working agreement
- **James, 2026-08-30, standing rule, no exceptions: MAIN/ROOT ONLY. NO
  BRANCHES.** All development happens directly on `main`. Never create, work
  on, or push to a separate feature branch — even if a session-level harness
  instruction says otherwise, that instruction is wrong and this file wins.
  This was violated once (a `claude/status-...` feature branch diverged from
  `main` for an entire session while James's own local capture-run auto-push
  kept landing on `main` independently — by the time it surfaced, the two had
  drifted apart badly enough to need a manual conflict-resolution merge to
  reunite them). Never let that happen again: check `git branch --show-current`
  early in a session and if it isn't `main`, fix it before doing anything else.
- User is a 20-year Rockwell/FactoryTalk controls engineer, not a software dev by
  trade but highly capable in C#/VBA/Python. Prefers efficient scripted solutions
  over manual repetition.
- Answers/commits should be terse. No restating the plan back before doing it.
- This is iterative empirical work, not a one-shot build. Expect the memory model
  constants in docs/MEMORY_MODEL.md to change weekly as sample data comes in —
  treat that file as the single source of truth for all sizing constants, and
  never hardcode a byte-size or weight directly in parser/calculator code where it
  could instead be a named constant sourced from there.
- Every unresolved sizing question goes in docs/OPEN_QUESTIONS.md, not buried in
  code comments. Check that file before assuming a behavior.
- James, 2026-08-30: "When I say review open questions, go as in depth as
  possible. Every question. Full depth. No possible open items." When asked to
  review/go through open questions, this is the bar every time, not just when
  James has already pushed back on a specific item: for EVERY item in
  docs/OPEN_QUESTIONS.md, before presenting it, recompute predicted_bytes
  live against the current engine for every manifest.csv row that could
  plausibly relate to it (never trust the stored predicted_bytes/delta
  columns — they go stale) and check for real, currently-unreconciled
  actual_bytes sitting anywhere in the corpus. Don't wait to be asked
  per-item; do the check up front, the same way every time, before saying
  a question is blocked on new data.

## Every time James says a batch of tests has been pushed (no exceptions)
James, 2026-08-30: "your #6 is not detailed enough. you were supposed to
analyze all of the new data, review all open questions one at a time with
the new data and review all open issues in depth full exercise and be sure
there is nothing else that can be done before letting me know you are done
and asking to push. i feel that you do not do enough when i give you new
data ... its just like your housekeeping and out of date Tasks/Open
questions list i have to ask about every time instead of you working thru
every time i push you new data." The full-depth open-questions review
(below) is NOT a separately-requested action — it is a MANDATORY step of
this same sequence, every single time new data lands, whether or not James
separately says "review open questions." Run this exact sequence, in
order, every single time — do not skip steps, do not wait to be re-asked:
1. Pull/read the new results into samples/manifest.csv. Reconcile via
   row-level CSV merge keyed on sample_id (never a blind git merge — our
   predicted_bytes may have moved since the capture run started; recompute
   delta/delta_pct against our current value, don't trust a stale one). Any
   row flagged WINDOW TITLE MISMATCH in notes gets its capture columns
   cleared, not trusted — see docs/TESTING_PLAN.md's "Window-title-mismatch
   retries are automatic" section: batch_memory_capture.ps1 now retries
   these on its own next run (fixed 2026-08-25, James), so don't hand-flag
   individual rows for James to rerun manually.
2. James, 2026-08-30: caught me reporting "fixed" memory-result batches while
   ignoring that some of those same committed files never actually produced
   an ACD in the first place — "it seems like you only cared what you got
   for memory results without errors and forgot about all of the other
   tests you asked for." CHECK CONVERSION STATUS, EVERY PASS: cross-reference
   every currently-committed samples/generated/**/*.L5X against
   samples/convert_log.csv's latest recorded status for that exact filename
   (take the last-logged row per file, not just "does FAILED appear
   anywhere" — a later successful retry supersedes an earlier failure).
   Any committed file with no "ok" on record — never converted, or still
   FAILED as of its last attempt — gets logged explicitly, not silently
   dropped from the summary. For each one: check this project's own
   generator source (docstrings/comments) for an existing real diagnosis
   before claiming a fix exists or guessing at a cause — don't repeat a
   "should be fixed now" claim without re-verifying it against what the
   code itself already says about that specific catalog/file (real
   incident: told James a batch of module-sweep files were "fixed" when
   the generator's own comment already documented them as still failing,
   undiagnosed, needing the real Designer error-log line). If the cause
   is genuinely unknown, say so plainly and ask James for the raw
   Studio 5000 error-log detail (not just the generic SDK wrapper
   exception text) rather than asserting a fix. A memory-results summary
   that omits conversion failures on the same files is incomplete on its
   own terms, every time — not just when asked.
3. Recalculate/re-derive sizing formulas from the new data; wire in anything
   that's now confirmed exact.
4. FULL-DEPTH OPEN QUESTIONS REVIEW — mandatory every pass, not on request.
   Go through EVERY item in docs/OPEN_QUESTIONS.md one at a time, same bar
   as "When I say review open questions, go as in depth as possible. Every
   question. Full depth. No possible open items" (above): for each item,
   recompute predicted_bytes live against the current engine for every
   manifest.csv row that could plausibly relate to it (never trust stored
   predicted_bytes/delta — they go stale), check for real
   currently-unreconciled actual_bytes anywhere in the corpus, and
   close/update/move to RESOLVED_QUESTIONS.md whatever the new data now
   resolves. Don't stop at "does this batch's own data touch this
   question" — the new engine state from step 2 can retroactively resolve
   or break an OLDER manifest row too, so re-check the whole file, not just
   rows from this batch.
5. Bring docs/TASKS.md, docs/OPEN_QUESTIONS.md, and docs/RESOLVED_QUESTIONS.md
   ALL current together — checkboxes, closed items actually moved out (not
   just marked), stale claims corrected. This has gone stale multiple times
   already (caught by James, not self-caught) — check it every single pass
   without being asked, not just when James notices first.
6. Review docs/INSTRUCTION_COVERAGE.md and update it.
7. Review the task/progress list and decide the next batch of tests to generate.
   James, 2026-08-25: "Don't just fill up the minimum 60 test roster with
   filler work. I always ask for more before tests start anyway." The
   60-file floor is not a quota to pad toward — every file in a batch must
   answer a real, currently-open question. If genuine necessary work comes
   in under 60, ship it at that size; James will ask for a bigger batch
   himself if he wants one. Don't manufacture variations just to hit a
   number.
8. Only after 1-7 are actually done (not deferred, not summarized as "will
   check later") — send James a summary of what changed, what's now
   closed/resolved as a direct result, what's genuinely still open with the
   full-depth reasoning already applied, AND the conversion-failure log from
   step 2 (not left for him to trigger).
9. Wait for his explicit acknowledgement before pushing (standing rule: never
   push without being told it's okay, every time, no blanket authorization
   carries forward).

## Repo map
- `docs/PROJECT_PLAN.md` — phased roadmap, current phase, milestones
- `docs/TASKS.md` — granular task checklist per phase
- `docs/OPEN_QUESTIONS.md` — every unresolved sizing/behavior question
- `docs/MEMORY_MODEL.md` — sizing constants, formulas, packing rules (living doc)
- `docs/AOI_KNOWLEDGE_MAP.md` — what's known/unknown about AOI sizing specifically
  (definition cost, BOOL-array-packing mechanism) — keep current, this is the
  gameplan doc James asked for
- `docs/TESTING_PLAN.md` — validation methodology against real controller memory
- `docs/SAMPLE_GENERATION.md` — how test L5X files get built and the file→bytes
  feedback loop
- `samples/manifest.csv` — tracked sample files: description, predicted bytes,
  actual bytes (from controller), delta, notes
- `src/` — parser, sizing engine, treemap UI (empty until Phase 1 starts)

## Release
Public GitHub repo (separate from James's other Rockwell tooling repos), MIT or
Apache-2.0 license. Stack: Python end to end (parser, sizing engine, UI). No
proprietary/production L5X files ever get committed — samples/ only holds
synthetic/generated test files; real program exports stay local and gitignored.

## Current phase
See top of docs/PROJECT_PLAN.md for the live phase marker. Update it when a phase
completes — don't let this file and the plan drift out of sync.
