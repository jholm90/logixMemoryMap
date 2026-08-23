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

## Working agreement
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

## Every time James says a batch of tests has been pushed (no exceptions)
Run this exact sequence, in order, every single time — do not skip steps, do not
wait to be re-asked:
1. Pull/read the new results into samples/manifest.csv.
2. Recalculate/re-derive sizing formulas from the new data; wire in anything
   that's now confirmed exact.
3. Review docs/TASKS.md and update checkboxes.
4. Review docs/INSTRUCTION_COVERAGE.md and update it.
5. Review the task/progress list and decide the next batch of tests to generate.
   Group them into one batch of at least 60 files — James does not want short
   test runs.
6. Send James a summary of what changed plus open questions from this run.
7. Wait for his explicit acknowledgement before pushing (standing rule: never
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
