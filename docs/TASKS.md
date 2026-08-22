# Task List

Checkbox per phase from PROJECT_PLAN.md. Keep granular enough that each item is
a single commit-sized unit of work.

## Phase 0 — Setup
- [x] Decide stack (OQ-STACK) — parser language, UI framework
- [x] Repo skeleton: `src/parser`, `src/sizing`, `src/ui`
- [x] Get real production L5X files into `samples/local/` (gitignored) as dev
      fixtures — 2026-08-20, 4 real files (unsanitized, local-only). See
      docs/OPEN_QUESTIONS.md OQ-PREDEFINED for what running the sizing engine
      against them turned up.
- [x] `samples/manifest.csv` created with columns (see SAMPLE_GENERATION.md)
- [x] XML load + basic namespace/schema sanity check for whatever L5X version(s)
      in use (OQ-L5XVERSION) — `parser/load.py` validates root tag, records
      SchemaRevision/SoftwareRevision without enforcing a version yet

## Phase 1 — Tag / UDT / AOI sizing engine
- [x] Atomic type size table (BOOL, SINT, INT, DINT, LINT, REAL, STRING) in
      MEMORY_MODEL.md, referenced not hardcoded — `sizing/memory_model.yaml`
      + `sizing/constants.py`
- [x] BOOL packing rule implemented (bits-per-byte within DINT/SINT-backed
      storage, per OQ-BOOLPACK resolution) — standalone tag (4 bytes,
      unpacked), UDT member (hidden-SINT + BIT-alias, read directly off the
      L5X shape), array (32-per-DINT bit-packing, OQ-BOOLARRAY)
- [x] UDT parser: recurse `Controller/DataTypes/DataType/Members`
- [x] UDT alignment/padding rule implemented (OQ-ALIGN) — 2026-08-22,
      confirmed KNOWN (real Capacity data across the whole per-tag/per-UDT-
      definition sweep, not just James's field opinion). `udt.
      alignment_confidence` flipped UNKNOWN→KNOWN; tight-packing was
      already what the code computed, this just stopped tainting every
      UDT-derived size with UNKNOWN.
- [x] Per-tag flat overhead + UDT DataType-definition cost landed in code
      2026-08-22 (`tag_overhead`/`udt_definition` in memory_model.yaml,
      wired into `report.py`) — the empirically-confirmed formulas from
      the Phase 3 sweep were sitting in RESOLVED_QUESTIONS.md prose only
      until now.
- [x] Array-of-atomic sizing (dimension × element size)
- [x] Array-of-UDT sizing (dimension × recursive UDT size, padding per-element
      vs whole-array — OQ-ARRAYPACK) — formula implemented, confidence tagged
      UNKNOWN pending that OQ
- [x] STRING (built-in) sizing: 4-byte LEN + configurable DATA array
- [x] Custom STRING type sizing (user-defined max length UDTs) — separate path
      from generic UDT recursion — `Family="StringFamily"` special-cased so it
      doesn't inherit the UDT-alignment UNKNOWN taint
- [ ] Module/IO parser: `Controller/Modules` → connection tag sizing (Local I/O
      first, produced/consumed second — OQ-PRODCONS)
- [x] Controller-scope vs program-scope tag separation in output
- [x] Flat output contract finalized: `{path, category, bytes, pct_of_total,
      confidence: exact|estimated}` — `sizing/report.py`'s `SizeEntry`
      (`tier` = exact/estimated, plus a finer-grained `basis` =
      KNOWN/ASSUMED/FITTED/UNKNOWN so exact-tier numbers still carry their
      MEMORY_MODEL.md confidence)
- [x] Unit tests against hand-calculated small UDT (nested, 2 levels, mixed
      BOOL/DINT/STRING members) — `tests/test_sizing.py`, `tests/test_parser.py`
- [x] Validated against 4 real production L5X files (2026-08-20, 3394 tags
      total). Found and fixed two real gaps this way, not from theory:
      Alias tags (`TagType="Alias"`, no DataType, 294 occurrences / ~21% of
      all sizing errors) now correctly size as 0 bytes/KNOWN instead of
      erroring — they're a pointer onto another tag's memory, not unsized
      data. TIMER/COUNTER/CONTROL (well-documented 12-byte AB structures)
      now modeled as `predefined_structures` in memory_model.yaml. Error
      rate on the real corpus dropped 41.6% → 29.5%. Remaining errors are
      AOI-instance tags (46.8% of what's left, confirms Phase 2b priority)
      and a long tail of other firmware-native structures (motion/axis/
      safety) deliberately left unsized rather than guessed — cataloged in
      OQ-PREDEFINED for real research, not silently zeroed or estimated.

## Phase 2 — UI v1
Stack decided 2026-08-20 (OQ-STACK closed): local Flask server, vanilla JS/SVG
squarified treemap in the browser, zero CDN/external-JS dependency (engineering
workstations on OT networks are frequently airgapped — a public tool can't
assume runtime internet access). `l5x-memory-analyzer ui <path>` serves it.
Verified 2026-08-20 against both the Phase-0 fixture and a richer synthetic
multi-program/multi-UDT fixture, screenshotted via headless Chromium — not
just "code compiles," actually rendered and clicked through.

- [x] Treemap component (squarified algorithm, hand-rolled in
      `ui/static/app.js` — no D3/external lib)
- [x] Root view: controller tags / program tags (per program), sized by bytes
- [ ] UDT defs pool / module overhead as their own root-level groups — not
      built. A UDT still only appears sized-in-place at each tag that uses
      it, no separate "all UDT definitions" browsable pool. Module overhead
      has nothing to show yet regardless (Module/IO parser still
      unimplemented, see Phase 1).
- [x] Click-to-drill: program → its tags (drilling into a "Program: X" group
      node shows that program's tags)
- [x] **Click-to-drill: infinite depth, down to individual BOOL bits and
      individual array elements — 2026-08-20, James: "masking a 1000
      element array because its inside something else is bad practice."**
      `sizing/tree.py` computes exactly one level of children at a time, on
      demand, via a new `/api/node` endpoint — never materializes the whole
      tree eagerly (would be enormous for a 40k-tag/multi-MB real project
      with 10k-element arrays), but drilling itself has no depth limit.
      Verified live to 4 levels deep on a real file (array tag → element →
      UDT member → STRING LEN/DATA breakdown) via headless-Chromium
      click-through, not just code review.
- [x] Breadcrumb / back navigation
- [x] Sortable list view (name / type / bytes / %) — click column header to
      sort. Still a top-level rollup only (not the deep tree) — see
      `app.js` comment on why: expanding every array/UDT eagerly for the
      list view would defeat the whole point of the lazy /api/node design.
- [x] Type-utilization summary pane (% of budget per data type across whole
      project, not just top-level categories) — now with a color swatch
      per type matching the treemap.
- [x] **Color/confidence redesign — 2026-08-20, James: "colors reserved for
      data types only," confidence shown as solid (100%) vs. hatched
      (unsure) instead.** Replaces the earlier basis-coded-by-color scheme.
      Curated colors for common atomic/predefined types, deterministic
      hash-to-HSL for arbitrary UDT/AOI type names so every distinct type
      gets a stable, distinct color across a session. Non-KNOWN basis nodes
      get a diagonal-hatch SVG pattern overlaid on their solid type color
      rather than being recolored.
- [x] Load Phase-0 dev fixture, sanity-check against manual spot-checks
- [x] **File → Open in the browser, no command prompt needed — 2026-08-20.**
      `l5x-memory-analyzer ui` (no path arg) starts with an empty state and
      a File Open… button; upload posts to a new `/api/load` endpoint that
      parses the bytes server-side (no filesystem path needed from the
      browser). `scripts/LaunchUI.pyw` + a desktop shortcut to it gives a
      genuine double-click launch (`.pyw` runs via pythonw.exe, no console
      window) straight to the browser.
- [x] **Processor part number in the header — 2026-08-20.** `load.py` now
      parses `Controller/@ProcessorType`; shown alongside Schema/Software
      revision.
- [x] **Export-type detection/warning — 2026-08-20.** `L5XDocument` now
      exposes `target_type`/`is_controller_export`; the UI shows an amber
      warning banner for any non-`Controller` export (Program/DataType/
      AOI-only) rather than silently presenting a partial file's totals as
      if complete. Full first-class support for those export types is a
      **backlog feature request** (see OPEN_QUESTIONS.md OQ-EXPORTSCOPE),
      not built now — today's focus stays full Controller exports per
      James's explicit scoping.
- [x] **List/Type Summary scoped to current tree level — 2026-08-20,
      James: "if im down branches then those should represent the current
      level."** Both tabs now render `CURRENT_NODE`'s direct children
      (percentages relative to that node's own total) instead of always
      showing the whole file's top-level entries, and re-render on every
      navigation so they stay in sync with wherever the treemap is even
      when not the active tab.
- [x] **Breadcrumb sibling browser — 2026-08-20, James: "I want to browse
      to neighbors as well if mouse over."** Hovering a non-root breadcrumb
      segment shows a popup of (up to 10) sibling nodes under its parent,
      click one to jump sideways without backing all the way up and
      re-drilling down. Entirely client-side, no new endpoint needed —
      every ancestor on the breadcrumb already has its full children list
      cached in memory from having been drilled through.

## Phase 2b — AOI sizing (deferred from Phase 1)
- [x] AOI definition parser: `AddOnInstructionDefinitions` local tags + params
      — `parser/aoi.py`, 2026-08-20. Turned out NOT to need logic parsing:
      real production data confirmed every AOI-typed tag is a plain named
      Tag, sized exactly like a UDT-typed tag by merging AOI definitions
      into the same `data_types` dict `compute_udt_size` already recurses.
      `Input`/`Output` Parameters + `LocalTags` = members; `InOut` Parameters
      excluded (reference, not storage). Nested AOI-in-AOI recurses with the
      same cycle detection as nested UDTs. Dropped sizing-engine error rate
      on the real corpus from 29.5% → 8.8%.
- [ ] UI: click-to-drill into an AOI defs pool node → locals+params breakdown
      — still not built, same report-contract gap as the UDT-member-drill
      item in Phase 2 (no member-level entries in the flat SizeEntry list yet)
- [ ] AOI instance multiplication for inline/anonymous instances with no
      backing tag (if Logix even permits that) — still needs call-site count
      from logic parse, still a Phase 1/4 dependency (OQ-AOIINSTANCE,
      narrowed 2026-08-20 — real sample data didn't turn up an example of
      this actually happening, worth checking whether it's even possible
      before investing more here)

## Phase 3 — Sample validation round 1
- [x] Generate: 1000 standalone BOOL controller tags vs. 0-tag baseline
      (`src/sample_gen/gen_boolpack_test.py`, 2026-08-20) — direct isolating
      test for OQ-BOOLPACK, since James's own hunch contradicts the current
      4-bytes/tag model. Predicted delta: 4000 bytes (4.0 bytes/tag) if the
      current model is right. **Awaiting actual bytes from James** —
      compile both `samples/generated/boolpack/sample_000{1,2}_*.L5X` in
      Studio 5000, read Controller Properties → Memory tab, report both
      numbers (no download needed, see TESTING_PLAN.md).
- [ ] Generate: 10k-element BOOL array (controller tag)
- [ ] Generate: 10k-element DINT array
- [ ] Generate: 10k-element UDT array (UDT = mix of BOOL/DINT/REAL, ~20 bytes/ea)
- [ ] Generate: 10k-element array of a deliberately NOT-4-byte-aligned UDT
      (e.g. `DINT, BOOL, BOOL` = 5 bytes tight-packed, per OQ-ALIGN) —
      the ~20-byte UDT sample above is already a multiple of 4 and can't
      distinguish "array stride rounds up to 4-byte boundary" (OQ-ARRAYPACK,
      James's hunch) from "no rounding, tight stride" — this sample can
- [ ] Generate: nested UDT (UDT containing UDT containing UDT, 3 levels)
- [ ] Generate: STRING array (default 82-byte) ×1000
- [ ] Generate: custom string type (250-char) ×1000
- [ ] Generate: produced tag + matching consumed tag pair
- [ ] Generate: AOI with 5 local tags, called 50 times vs called 1 time (isolate
      per-instance cost)
- [ ] Generate: program-scope vs controller-scope identical tag (confirm no
      difference, or document the difference)
- [ ] For each: import → verify/compile (no download needed, see
      TESTING_PLAN.md) → record actual bytes → log in manifest.csv
- [ ] Reconcile predicted vs actual, update MEMORY_MODEL.md constants
- [ ] Re-run full sample set after each constant change until stable
- [ ] Document final confidence/tolerance achieved

## Phase 4 — Logic sizing round 1 (bit logic)
Real data note (2026-08-20): 126 of 560 real routines (~22%) are Structured
Text, not RLL — significant enough that Phase 4/5 logic parsing can't be
RLL-only. ST uses different syntax (no rung/Text-per-rung shape) and its
compiled-size characteristics vs. equivalent RLL are completely unknown —
worth its own explicit sample set once RLL bit logic is fitted, don't just
assume ST scales the same way rung-based logic does.

- [ ] Generate: N rungs (10/100/1000) of single XIC + single OTE, empty branches
- [ ] Generate: same counts for XIO, OTL, OTU
- [ ] Generate: branch depth variations (1, 3, 5 parallel branches) at fixed
      rung count
- [ ] Generate: rung comment presence vs absence, sample pair specified by
      James (2026-08-20) — 10k rungs of XIC/OTE with no comments vs. 10k
      rungs of XIC/OTE with a 100-char comment per rung (OQ-COMMENTS)
- [ ] Generate: empty rungs (comment-only, no instructions) at scale
- [ ] Record actual memory delta per sample
- [ ] Fit initial per-instruction weight, log residuals

## Phase 4b — Logic sizing round 2 (other instructions)
Scope set from real instruction-frequency data (OQ-INSTRUCTIONSCOPE,
2026-08-20), not a guessed list — 24,941 real instruction instances counted
across James's 4 production files. Ordered by real-world priority below;
PID and ASCII-module instructions dropped entirely (zero occurrences found).

**Status note, 2026-08-22 — this checklist is stale below and hasn't been
walked line-by-line yet, but the real position is far ahead of what's
checked:** the 244-file per-instruction sweep (`gen_logic_sweep.py`)
already covers bit logic, timers/counters (TON/TOF/RTO/CTU), math/compare
(ADD/SUB/MUL/DIV/MOD/CPT/MVM/MEQ/EQU/NEQ/GRT/GEQ/LES/LEQ/LIM/MOV),
array/file (COP/FLL/CLR/BTD/CPS), string (CONCAT/DTOS/SIZE/MID/DELETE),
GSV/SSV, and JSR — 42 instructions fitted at 0.00% residual, table now in
`docs/MEMORY_MODEL.md`. Still genuinely open: motion instructions
(generators built 2026-08-22, `gen_motion_instructions.py`, awaiting
capture), MAPC/MCCP camming (no real call-syntax reference yet), per-Task
overhead (generator built, `gen_task_overhead.py`), indirect addressing
(generator built, `gen_indirect_addressing.py`), MSG (deprioritized, 4 real
uses). **The weight table is data only — no logic-sizing engine code
exists yet** (no parser walks Routines/Rungs and applies these weights);
that's the actual remaining Phase 4/4b implementation work.

- [x] **Process full-directory AHK build/verify batch results, 2026-08-22.**
      Reviewed against James's two real Studio 5000-verified samples
      (`COP_Samples.L5X`, `categoryB.L5X`) plus direct code inspection —
      not a blind mnemonic dump. Findings:
      - **SIZE (5 rows, real bug, fixed):** generator used a bracketed
        `.DATA[0]` subscript; James's sample proved SIZE takes the bare
        array tag with no subscript at all (`SIZE(COP_Source,0,COP_Size);`).
        Fixed in `gen_logic_sweep.py` + `lint.py`'s SIZE exception,
        regenerated, no new sample needed.
      - **xic_ote_1000_comment100/nocomment (2 rows, real bug, fixed):**
        `sample_gen.cli rungs` never declared the tags referenced by
        `--instr` (passed `tags_xml=""` unconditionally) — exactly James's
        catch. Added `--decl-tag` to auto-declare them, regenerated both
        files (2000 declared BOOL tags), no new sample needed.
      - **CPS/COP/FLL/BTD (21 rows) + LBL/JMP (5 rows):** every rung in
        each file errored (error_count == rung count) — the same signature
        already traced to the stale-ACD-conversion-cache bug fixed in
        `batch_l5x_to_acd.ps1` (`l5x_mtime` tracking), which James hasn't
        re-run yet. Very likely false alarms against pre-fix ACD binaries,
        not real syntax bugs. LBL/JMP is new since the last review pass —
        logged as OQ-LBLJMP-STALE in OPEN_QUESTIONS.md in case it's a real,
        separate bug once reconversion rules out staleness.
      - **CMP compound (3 rows, real bug, fixed):** James's categoryB.L5X
        only exercises a single CMP condition, so a new sample wasn't
        needed — instead pulled every real CMP/CPT call out of
        `samples/local/` (docs/CMP_CPT_REFERENCE.md, 421 CMP + 1533 CPT
        calls) per James's direction ("make a table... instead of
        reengineering the wheel"). Found one real compound-CMP file
        (`EmporiumEdger_20250905r1.L5X`, 12 instances) using `&&`
        (double ampersand, not the generator's bare `&`), first clause
        unparenthesized, second wrapped in its own parens. Fixed
        `gen_cmpcpt_layout.py` to match, regenerated. `||` (OR) has zero
        real corpus examples — assumed valid by symmetry, not confirmed.
      - **LBL/JMP (5 rows, real bug, fixed):** James confirmed directly —
        a bare `LBL(x);` with nothing after it fails; `LBL(x)NOP();`
        passes. Fixed `group_lbl_jmp` to always pair LBL with a trailing
        NOP, regenerated.
      **Net "samples needed" list, corrected from the original blind scan:
      zero.** Every real error class from this batch is now either fixed
      in the generator or explained by the stale-ACD-cache bug pending
      James's reconversion — nothing needs a brand new hand-built sample.
- [ ] **Re-capture genuine title-bar mismatch rows from the same batch.**
      6 rows still flagged in manifest.csv `notes` as `WINDOW TITLE
      MISMATCH` (real ones, not the false-positive extension-matching bug
      already fixed): `paramcount_n04_def_only`, `paramcount_n08_def_only`,
      `array_dint_00001`, `array_dint_00002`, `array_dint_00005`,
      `udttagcomment_len000` (this last one's captured title was literally
      "Snap Assist" — a Windows OS element, so focus was fully off Logix
      Designer for that capture). Confirm this is the complete/correct
      list with James, then wipe just those rows for re-capture, not the
      whole batch.
- [ ] **Re-run `batch_l5x_to_acd.ps1` + `batch_memory_capture.ps1` for
      CPS/COP/FLL/BTD (21 rows), SIZE (5 rows), xic_ote_1000 (2 rows),
      LBL-JMP (5 rows), and CMP compound (3 rows)** — all 36 rows had
      their manifest actual_bytes/error data cleared pending re-capture
      against the now-fixed L5X sources. Also picks up a second fix in
      `batch_l5x_to_acd.ps1` (James, 2026-08-22: "you will need to append
      V2 onto the ACD files you are regenerating as youre probably not
      overwriting them") — added an explicit delete of the old `.ACD`
      before every reconversion, since it was never verified that
      `l5xgit` itself overwrites an existing destination file.
- [ ] Timer instructions (TON/TOF/RTO) at scale — no CTU/CTD-heavy usage seen
      but include CTU (25 real uses; CTD had zero, low priority)
- [ ] Math/compare instructions (MOV/EQU/ADD/NEQ/GRT/MUL/GEQ/LES/SUB/LIM/LEQ/
      DIV/CPT with expression length variation) — by far the highest-volume
      category after bit logic (5,000+ real uses combined)
- [ ] **Motion instructions (MAM/MAS/MAJ/MAH/MSO/MSF/MDW/MAW/MASR/MAFR) and
      cam/route (DCS/CROUT)** — NOT in original scope, added after real data
      showed ~90 real uses across 12 distinct instructions; James: "we use
      lots of motion instructions, camming." Also motion/axis structures
      (AXIS_CIP_DRIVE etc, OQ-PREDEFINED) are the single highest-frequency
      unsized structure category in real tag data, so this pairs with that.
- [ ] **GSV/SSV instruction overhead** — NOT in original scope, added after
      real data showed 101/47 real uses; James called these out explicitly.
      Different sizing question than tag-level GSV memory reads (that's a
      dead end, see OQ-MEMREADMETHOD) — this is about the *instruction's own*
      compiled logic footprint in a rung, unrelated.
- [ ] Array/file instructions (COP/CLR/FLL/BTD/MVM) at varying array size
- [ ] String instructions (CONCAT/DTOS/SIZE/MID/TRUNC) — some real usage,
      not ASCII-module instructions specifically (zero of those seen)
- [ ] Indirect addressing overhead (compare direct vs indirect same logic)
- [ ] JSR/subroutine call overhead (call site cost vs routine body cost,
      separate these two numbers) — 238 real JSR uses, matters
- [ ] MSG instruction overhead — only 4 real uses total, low priority, don't
      over-invest here relative to everything else on this list
- [ ] Consolidate full instruction-weight table into MEMORY_MODEL.md
- [ ] Hold out 3-5 samples, validate fitted model against them, log residual

## Phase 5 — UI v2 (logic browsing)
- [ ] Extend data contract: routines/rungs feed the same
      `{path, bytes, confidence}` shape as tags
- [ ] Treemap drill: Task → Program → Routine → (rung-level list, not
      individual-rung treemap nodes — too granular to be useful visually)
- [ ] Subroutine call-tree rollup (JSR chains sum correctly, no double-counting
      shared subroutines called from multiple places — OQ-JSRSHARED)
- [ ] "Estimated" badge/color on every logic-derived number in both treemap and
      list views
- [ ] Combined root view merging tags + logic + module overhead into one map

## Phase 6 — Polish
- [ ] Safety task scope decision implemented (OQ-SAFETY)
- [ ] Alarm instance (ALMD/ALMA) overhead if in scope (OQ-ALARM)
- [x] **Per-part-number memory budget — 2026-08-20, James: "why are you
      assuming 4MB for all processor types... this should be based on
      blocks and total should be part number based."** Was hardcoded to a
      flat 4MB; real capacity ranges 0.6MB-40MB by catalog number.
      `sizing/controller_budgets.yaml` + `controller_budgets.py`: looks up
      `Controller/@ProcessorType` (prefix-matched, so safety/motion/coating
      suffixes like "1756-L81ES" still resolve) against a sourced table.
      Also confirmed James's "blocks" instinct against Rockwell's own docs:
      legacy ControlLogix 5570 (1756-L6x/L7x) really does divide memory
      into separate I/O and Data/Logic pools, but CompactLogix 5380 and
      ControlLogix 5580/5590 (his actual target hardware) use one unified
      pool per Rockwell's own Logix5000 I/O and Tag Data manual. Unknown
      processor types show "budget unknown" rather than a fake number —
      table is deliberately incomplete (e.g. 5069-L340ER/L350ER weren't
      confirmed by any source, left out rather than guessed from the
      naming pattern) and 1769-Lxx CompactLogix 5370 isn't covered yet.
- [ ] Export report (CSV/XLSX — reuse ControlsAutomation XLAM patterns if useful)
