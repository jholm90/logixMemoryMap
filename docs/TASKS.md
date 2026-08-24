# Task List

Checkbox per phase from PROJECT_PLAN.md. Keep granular enough that each item is
a single commit-sized unit of work.

Legend: ✅ done — 🟡 partially resolved (real, confirmed piece landed; a
genuinely separate remaining piece stays open, not just paperwork) — 🔴 open

## Phase 0 — Setup
- ✅ Decide stack (OQ-STACK) — parser language, UI framework
- ✅ Repo skeleton: `src/parser`, `src/sizing`, `src/ui`
- ✅ Get real production L5X files into `samples/local/` (gitignored) as dev
      fixtures — 2026-08-20, 4 real files (unsanitized, local-only). See
      docs/OPEN_QUESTIONS.md OQ-PREDEFINED for what running the sizing engine
      against them turned up.
- ✅ `samples/manifest.csv` created with columns (see SAMPLE_GENERATION.md)
- ✅ XML load + basic namespace/schema sanity check for whatever L5X version(s)
      in use (OQ-L5XVERSION) — `parser/load.py` validates root tag, records
      SchemaRevision/SoftwareRevision without enforcing a version yet

## Phase 1 — Tag / UDT / AOI sizing engine
- ✅ Atomic type size table (BOOL, SINT, INT, DINT, LINT, REAL, STRING) in
      MEMORY_MODEL.md, referenced not hardcoded — `sizing/memory_model.yaml`
      + `sizing/constants.py`
- ✅ BOOL packing rule implemented (bits-per-byte within DINT/SINT-backed
      storage, per OQ-BOOLPACK resolution) — standalone tag (4 bytes,
      unpacked), UDT member (hidden-SINT + BIT-alias, read directly off the
      L5X shape), array (32-per-DINT bit-packing, OQ-BOOLARRAY)
- ✅ UDT parser: recurse `Controller/DataTypes/DataType/Members`
- ✅ UDT alignment/padding rule implemented (OQ-ALIGN) — 2026-08-22,
      confirmed KNOWN (real Capacity data across the whole per-tag/per-UDT-
      definition sweep, not just James's field opinion). `udt.
      alignment_confidence` flipped UNKNOWN→KNOWN; tight-packing was
      already what the code computed, this just stopped tainting every
      UDT-derived size with UNKNOWN.
- ✅ Per-tag flat overhead + UDT DataType-definition cost landed in code
      2026-08-22 (`tag_overhead`/`udt_definition` in memory_model.yaml,
      wired into `report.py`) — the empirically-confirmed formulas from
      the Phase 3 sweep were sitting in RESOLVED_QUESTIONS.md prose only
      until now.
- ✅ Array-of-atomic sizing (dimension × element size)
- ✅ Array-of-UDT sizing (dimension × recursive UDT size, padding per-element
      vs whole-array — OQ-ARRAYPACK) — formula implemented, confidence tagged
      UNKNOWN pending that OQ
- ✅ STRING (built-in) sizing: 4-byte LEN + configurable DATA array
- ✅ Custom STRING type sizing (user-defined max length UDTs) — separate path
      from generic UDT recursion — `Family="StringFamily"` special-cased so it
      doesn't inherit the UDT-alignment UNKNOWN taint
- 🔴 Module/IO parser: `Controller/Modules` → connection tag sizing (Local I/O
      first, produced/consumed second — OQ-PRODCONS)
- ✅ Controller-scope vs program-scope tag separation in output
- ✅ Flat output contract finalized: `{path, category, bytes, pct_of_total,
      confidence: exact|estimated}` — `sizing/report.py`'s `SizeEntry`
      (`tier` = exact/estimated, plus a finer-grained `basis` =
      KNOWN/ASSUMED/FITTED/UNKNOWN so exact-tier numbers still carry their
      MEMORY_MODEL.md confidence)
- ✅ Unit tests against hand-calculated small UDT (nested, 2 levels, mixed
      BOOL/DINT/STRING members) — `tests/test_sizing.py`, `tests/test_parser.py`
- ✅ Validated against 4 real production L5X files (2026-08-20, 3394 tags
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

- ✅ Treemap component (squarified algorithm, hand-rolled in
      `ui/static/app.js` — no D3/external lib)
- ✅ Root view: controller tags / program tags (per program), sized by bytes
- ✅ **UDT/AOI defs pool as its own root-level group.** Was already built
      (`hierarchy.py`'s `NON_TAG_GROUPS`, 2026-08-23) but stale-flagged
      here as "not built" -- verified live via `build_hierarchy()` against
      a real generated file, group renders correctly. AOI definitions
      weren't appearing in it (report.py never emitted a definition entry
      for them) until 2026-08-26's OQ-AOIDEF wiring, now fixed alongside
      the drill-down item below. Module overhead still has nothing to
      show (Module/IO parser still unimplemented, Phase 1) -- genuinely
      unrelated to this item, stays 🔴, tracked separately.
- ✅ Click-to-drill: program → its tags (drilling into a "Program: X" group
      node shows that program's tags)
- ✅ **Click-to-drill: infinite depth, down to individual BOOL bits and
      individual array elements — 2026-08-20, James: "masking a 1000
      element array because its inside something else is bad practice."**
      `sizing/tree.py` computes exactly one level of children at a time, on
      demand, via a new `/api/node` endpoint — never materializes the whole
      tree eagerly (would be enormous for a 40k-tag/multi-MB real project
      with 10k-element arrays), but drilling itself has no depth limit.
      Verified live to 4 levels deep on a real file (array tag → element →
      UDT member → STRING LEN/DATA breakdown) via headless-Chromium
      click-through, not just code review.
- ✅ Breadcrumb / back navigation
- ✅ Sortable list view (name / type / bytes / %) — click column header to
      sort. Still a top-level rollup only (not the deep tree) — see
      `app.js` comment on why: expanding every array/UDT eagerly for the
      list view would defeat the whole point of the lazy /api/node design.
- ✅ Type-utilization summary pane (% of budget per data type across whole
      project, not just top-level categories) — now with a color swatch
      per type matching the treemap.
- ✅ **Color/confidence redesign — 2026-08-20, James: "colors reserved for
      data types only," confidence shown as solid (100%) vs. hatched
      (unsure) instead.** Replaces the earlier basis-coded-by-color scheme.
      Curated colors for common atomic/predefined types, deterministic
      hash-to-HSL for arbitrary UDT/AOI type names so every distinct type
      gets a stable, distinct color across a session. Non-KNOWN basis nodes
      get a diagonal-hatch SVG pattern overlaid on their solid type color
      rather than being recolored.
- ✅ Load Phase-0 dev fixture, sanity-check against manual spot-checks
- ✅ **File → Open in the browser, no command prompt needed — 2026-08-20.**
      `l5x-memory-analyzer ui` (no path arg) starts with an empty state and
      a File Open… button; upload posts to a new `/api/load` endpoint that
      parses the bytes server-side (no filesystem path needed from the
      browser). `scripts/LaunchUI.pyw` + a desktop shortcut to it gives a
      genuine double-click launch (`.pyw` runs via pythonw.exe, no console
      window) straight to the browser.
- ✅ **Processor part number in the header — 2026-08-20.** `load.py` now
      parses `Controller/@ProcessorType`; shown alongside Schema/Software
      revision.
- ✅ **Export-type detection/warning — 2026-08-20.** `L5XDocument` now
      exposes `target_type`/`is_controller_export`; the UI shows an amber
      warning banner for any non-`Controller` export (Program/DataType/
      AOI-only) rather than silently presenting a partial file's totals as
      if complete. Full first-class support for those export types is a
      **backlog feature request** (see OPEN_QUESTIONS.md OQ-EXPORTSCOPE),
      not built now — today's focus stays full Controller exports per
      James's explicit scoping.
- ✅ **List/Type Summary scoped to current tree level — 2026-08-20,
      James: "if im down branches then those should represent the current
      level."** Both tabs now render `CURRENT_NODE`'s direct children
      (percentages relative to that node's own total) instead of always
      showing the whole file's top-level entries, and re-render on every
      navigation so they stay in sync with wherever the treemap is even
      when not the active tab.
- ✅ **Breadcrumb sibling browser — 2026-08-20, James: "I want to browse
      to neighbors as well if mouse over."** Hovering a non-root breadcrumb
      segment shows a popup of (up to 10) sibling nodes under its parent,
      click one to jump sideways without backing all the way up and
      re-drilling down. Entirely client-side, no new endpoint needed —
      every ancestor on the breadcrumb already has its full children list
      cached in memory from having been drilled through.

## Phase 2b — AOI sizing (deferred from Phase 1)
- ✅ AOI definition parser: `AddOnInstructionDefinitions` local tags + params
      — `parser/aoi.py`, 2026-08-20. Turned out NOT to need logic parsing:
      real production data confirmed every AOI-typed tag is a plain named
      Tag, sized exactly like a UDT-typed tag by merging AOI definitions
      into the same `data_types` dict `compute_udt_size` already recurses.
      `Input`/`Output` Parameters + `LocalTags` = members; `InOut` Parameters
      excluded (reference, not storage). Nested AOI-in-AOI recurses with the
      same cycle detection as nested UDTs. Dropped sizing-engine error rate
      on the real corpus from 29.5% → 8.8%.
- ✅ **UI: click-to-drill into a UDT/AOI defs pool node → locals+params
      breakdown — BUILT 2026-08-26.** `sizing/tree.py`'s new
      `expand_definition_children()` breaks a definition's flat cost
      formula (base + per-member/per-item + name-length [+ bool-run
      bonus]) into one row per declared member/param/local plus flat
      overhead rows, wired through a new `/api/node` branch keyed on the
      `udt_definitions/<Name>` path (not a tag instance) and `app.js`'s
      `annotateTagPaths` generalized to every root group, not just the two
      tag-scope ones. Verified end-to-end via the real Flask app
      (`test_client`) against 2 real generated files (a plain UDT and an
      AOI) — children sum back exactly to the parent defs-pool node's own
      value in both cases. AOI definitions needed OQ-AOIDEF actually wired
      first (below) to have anything real to drill into.
- ✅ **AOI definition cost — WIRED 2026-08-26 (OQ-AOIDEF), FITTED not
      KNOWN.** `sizing/udt.py`'s `compute_aoi_definition_cost()`: base
      1184 + 20/declared Input-Output-param-or-LocalTag (InOut and
      EnableIn/EnableOut excluded). Confirmed exact against 2 independent
      real sweeps (local-tag count, param count) that land on the
      identical formula — but DINT-rate only; real data shows BOOL/LINT
      cost differently (unmodeled), so this is a confirmed floor for
      those, not an exact number. See memory_model.yaml `aoi_definition`
      for the full derivation and limitation.
- ✅ **AOI instance multiplication for inline/anonymous instances —
      RESOLVED 2026-08-26, real corpus evidence, not built (correctly).**
      Scripted a check across all 83 real files in `samples/local/`: 6,075
      real AOI call sites found across 191 distinct AOI definitions, and
      6,075/6,075 (100%) have a plain tag-like first argument (including
      cross-program `\Program.Tag`-style references) — zero anonymous/
      inline instances with no backing tag. Confirms OQ-AOIINSTANCE's
      2026-08-20 narrowing: this scenario doesn't occur in practice (and
      is very likely not legal Logix syntax at all — an AOI instance
      always needs a declared backing Tag, same as a UDT instance). Not
      worth building speculative call-site-count logic for something with
      zero real occurrences in a real, sizeable corpus.

## Phase 3 — Sample validation round 1 — **CLOSED 2026-08-24**

James, 2026-08-24: "we have done lots of stuff in phase 3. I want phase 3
closed now." Every checklist item below is now satisfied — the literal
samples this list originally specified were mostly superseded by broader,
more rigorous family sweeps built over the following days (bigger count
ranges, more axes varied per question, cross-checked against 200+ real
Capacity-tab data points, not just the one-off samples originally
planned) — each item below cites what actually closed it. The 4 items
that had no matching file at all got one today (`gen_phase3_closeout.py`)
specifically to close this out honestly rather than mark it done on a
technicality.

**Exit criterion status:** met. Tag/UDT/AOI predictions match real
Capacity-tab data with 0.00% residual across the confirmed-formula
majority of the real corpus (see `docs/RESOLVED_QUESTIONS.md` for the
full derivation trail); every remaining discrepancy is a *named, tracked*
open question with its own generator already built (`docs/OPEN_
QUESTIONS.md`), not an unexplained fudge factor. `empty_project_baseline`'s
processor/firmware scoping (OQ-BASELINE-PROCFW) and the odd-byte-count
UDT-array residual (OQ-ARRAYPACK/OQ-UDTARRAYALIGN) are the two most
significant open threads carried forward, not closed by this phase.

- ✅ Generate: 1000 standalone BOOL controller tags vs. 0-tag baseline
      (`gen_boolpack_test.py`, 2026-08-20) — superseded by the confirmed
      per-tag flat overhead formula (`84 + 8×floor(name_len/8)`, KNOWN,
      2026-08-22), which resolved OQ-BOOLPACK directly: standalone BOOL
      tags are 4 bytes + the same overhead as every other atomic type.
- ✅ Generate: 10k-element BOOL array (controller tag) — `boolarray_n*`
      family now spans 8 to 5000 elements (`gen_arraypack_boolarray.py`),
      confirmed flat `ceil(dim/32)×4` with only a small ~constant residual
      matching the universal baseline noise band (OQ-BOOLARRAY confidence
      upgrade, 2026-08-23) — the formula's exactness doesn't need a literal
      10k point to be confirmed further, an exact linear fit across 6
      points already is confirmation.
- ✅ Generate: 10k-element DINT array — `array_dint_*` family spans 1 to
      5000 elements (`gen_sweep_batch.py`), exact `dimension×4` fit, same
      reasoning as above.
- ✅ Generate: 10k-element UDT array — `udtarrayalign_tight8b_n*` spans 1
      to 100 instances of an already-tight UDT (`gen_arraypack_boolarray.py`),
      perfectly constant per-element cost across all 3 points (zero
      per-element padding for a tight UDT, resolved).
- ✅ Generate: 10k-element array of a deliberately NOT-4-byte-aligned UDT
      — `arraypack_odd3b_n*` now spans 1 to 5000 instances (extended
      2026-08-24 from the original 1/10/100), still shows a real,
      not-yet-explained growing residual — this is OQ-ARRAYPACK/
      OQ-UDTARRAYALIGN, genuinely open, tracked, not silently closed.
- ✅ Generate: nested UDT (3 levels) — `nested_udt_3level.L5X`
      (`gen_phase3_closeout.py`, 2026-08-24, new). The 2-level version
      (`nested_udt_scalar`, `gen_batch2.py`) already confirmed the
      recursive formula; this fills the literal 3-level gap.
- ✅ Generate: STRING array (82-byte) ×1000 — `string_builtin_x1000.L5X`
      (`gen_phase3_closeout.py`, 2026-08-24, new).
- ✅ Generate: custom string type (250-char) ×1000 —
      `customstring_250char_x1000.L5X` (`gen_phase3_closeout.py`,
      2026-08-24, new). Custom-string-length sensitivity itself (10-2000
      chars) was already separately confirmed via `customstring_len*`.
- ✅ Generate: produced tag + matching consumed tag pair — decided not
      needed (OQ-PRODCONS, resolved): a correctly-built produced/consumed
      tag's DataType already includes a `CONNECTION_STATUS`-typed member,
      so ordinary UDT-member recursion covers it, and zero produced/
      consumed tags exist anywhere in the real corpus anyway.
- ✅ Generate: AOI with 5 local tags, called 50 times vs called 1 time —
      `aoi_realistic_50_instance_1.L5X` / `aoi_realistic_50_instance_array.L5X`
      (`gen_phase3_closeout.py`, 2026-08-24, new; extends the existing
      10-instance-array version from `gen_aoi_sweep.py`).
- ✅ Generate: program-scope vs controller-scope identical tag — resolved
      via OQ-TAGSCOPE (2026-08-23): `tagscope_public_*`/`tagscope_local`
      show zero cost difference between `Usage="Local"` and `"Public"`
      program tags, confirmed against real data.
- ✅ For each: import → verify/compile → record actual bytes → log in
      manifest.csv — this has been the standing per-batch workflow since
      Phase 0, 578+ real rows in `samples/manifest.csv` as of 2026-08-23.
- ✅ Reconcile predicted vs actual, update MEMORY_MODEL.md constants —
      the whole session's rebase-check methodology (0→77 exact matches out
      of 546 clean rows as of 2026-08-23, and rising) is this item, ongoing
      as a permanent practice not a one-time task, not something that ever
      "finishes" in the traditional sense — but the exit-criterion bar
      (tolerance met, discrepancies explained) is cleared.
- ✅ Re-run full sample set after each constant change until stable — same
      as above, this is now just how the project works (see
      `docs/RESOLVED_QUESTIONS.md`'s entire "Sizing-rebase batch" section
      for one concrete example of a full re-run after a constant change).
- ✅ Document final confidence/tolerance achieved — `docs/MEMORY_MODEL.md`
      tags every constant KNOWN/ASSUMED/FITTED/UNKNOWN;
      `docs/INSTRUCTION_COVERAGE.md` (2026-08-23) quantifies it directly:
      95.1% of all real instruction usage across the corpus is an exact
      confirmed fit.

## Phase 4 — Logic sizing round 1 (bit logic)
Real data note (2026-08-20): 126 of 560 real routines (~22%) are Structured
Text, not RLL — significant enough that Phase 4/5 logic parsing can't be
RLL-only. ST uses different syntax (no rung/Text-per-rung shape) and its
compiled-size characteristics vs. equivalent RLL are completely unknown —
worth its own explicit sample set once RLL bit logic is fitted, don't just
assume ST scales the same way rung-based logic does.

- 🔴 Generate: N rungs (10/100/1000) of single XIC + single OTE, empty branches
- 🔴 Generate: same counts for XIO, OTL, OTU
- 🔴 Generate: branch depth variations (1, 3, 5 parallel branches) at fixed
      rung count
- 🔴 Generate: rung comment presence vs absence, sample pair specified by
      James (2026-08-20) — 10k rungs of XIC/OTE with no comments vs. 10k
      rungs of XIC/OTE with a 100-char comment per rung (OQ-COMMENTS)
- 🔴 Generate: empty rungs (comment-only, no instructions) at scale
- 🔴 Record actual memory delta per sample
- 🔴 Fit initial per-instruction weight, log residuals

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

- ✅ **Process full-directory AHK build/verify batch results, 2026-08-22.**
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
- 🔴 **Re-capture genuine title-bar mismatch rows from the same batch.**
      6 rows still flagged in manifest.csv `notes` as `WINDOW TITLE
      MISMATCH` (real ones, not the false-positive extension-matching bug
      already fixed): `paramcount_n04_def_only`, `paramcount_n08_def_only`,
      `array_dint_00001`, `array_dint_00002`, `array_dint_00005`,
      `udttagcomment_len000` (this last one's captured title was literally
      "Snap Assist" — a Windows OS element, so focus was fully off Logix
      Designer for that capture). Confirm this is the complete/correct
      list with James, then wipe just those rows for re-capture, not the
      whole batch.
- 🔴 **Re-run `batch_l5x_to_acd.ps1` + `batch_memory_capture.ps1` for
      CPS/COP/FLL/BTD (21 rows), SIZE (5 rows), xic_ote_1000 (2 rows),
      LBL-JMP (5 rows), and CMP compound (3 rows)** — all 36 rows had
      their manifest actual_bytes/error data cleared pending re-capture
      against the now-fixed L5X sources. Also picks up a second fix in
      `batch_l5x_to_acd.ps1` (James, 2026-08-22: "you will need to append
      V2 onto the ACD files you are regenerating as youre probably not
      overwriting them") — added an explicit delete of the old `.ACD`
      before every reconversion, since it was never verified that
      `l5xgit` itself overwrites an existing destination file.
- ✅ Timer instructions (TON/TOF/RTO) at scale — no CTU/CTD-heavy usage seen
      but include CTU (25 real uses; CTD had zero, low priority) — all
      CONFIRMED, 0.00% residual, see docs/INSTRUCTION_COVERAGE.md
- 🟡 Math/compare instructions (MOV/EQU/ADD/NEQ/GRT/MUL/GEQ/LES/SUB/LIM/LEQ/
      DIV/CPT with expression length variation) — by far the highest-volume
      category after bit logic (5,000+ real uses combined). **Everything
      except CPT is CONFIRMED** (0.00% residual). **CPT: real per-operand
      expression parser BUILT AND WIRED 2026-08-26** (parser/logic.py
      extracts each CPT call's operator tokens, sizing/logic.py costs them
      via `CptExpressionModel`, replacing the old flat-wrong 452/rung).
      The UNIFORM case (every operator in one expression the same tier --
      plain chains like A+B+C+D, the dominant real usage pattern) is
      CONFIRMED exact: 0 residual verified live against 24 real manifest
      rows spanning bare-copy/ADD/SUB/MUL/DIV/MOD/POW at n=10/100/1000 and
      chain lengths 3/4/5/6/8/10. The MIXED case (more than one operator
      tier in one expression, e.g. A+B*C) still falls back to a real-but-
      approximate additive sum — off by only ~20 bytes/call on 2 simple
      test points but off by ~150 bytes/call on a real 5-operator/3-tier
      corpus expression (likely the exact expression the old flat-452 was
      originally fit against). Not patched further — 3 data points can't
      isolate which of several stacked factors (tier mixing, literal
      position, REAL vs DINT operands) drives that gap; `gen_cpt_mixed_
      operators.py` (33 files, James 2026-08-26: "mix up to 15 operands
      per expression as needed") built to isolate each factor
      independently — pairwise tier mixing (both orders), operand-count
      scaling to 15, all-3-tier mixes, literal position, REAL-vs-DINT
      cross-check, a stacked-factors ladder rebuilding the exact
      problematic expression one factor at a time, and a 15-operand
      rung-count linearity check. **Real data landed same day: T1(ADD/SUB)
      +T2(MUL/DIV/MOD)-only mixes are now SOLVED** — `100 + 32*operator_
      count`, 4/5 real operand-count points exact (k=7 within the usual
      small noise band), order/arrangement confirmed irrelevant. Wired as
      a special case in `CptExpressionModel.cost_for`, live-verified
      15/18 real rows exact. T1T3 and T2T3 pairs and all-3-tier mixes
      remain on the additive-sum fallback — real single/few-point data
      exists (e.g. T1T3=T2T3=288 for 2 operators) but no operand-count
      sweep like T1T2 got, so no formula to wire yet; REAL-operand and
      float-literal effects in a mixed expression are real, large, and
      confirmed to NOT compose additively with each other or with
      OQ-OPERANDTYPE's own surcharges (float+REAL together cost LESS than
      either alone would predict if additive) — characterized, not
      forced into a formula. See OQ-CMPCPTLAYOUT for the full derivation
      and the next-batch recommendation (T1T3/T2T3 operand-count sweeps).
      **CMP's own weight — RESOLVED 2026-08-26: the earlier "inconsistency"
      was a manual-arithmetic error, not a real bug.** Live-recomputed:
      `CMP: 76` is exact for a single condition. A real, previously-
      unwired COMPOUND-condition surcharge (+64/rung, KNOWN, exact at both
      n=100/n=1000) and FLOAT-literal surcharge (+72/rung, FITTED, single
      point) are now wired and verified (9/10 real rows exact, 1/10 hits
      the separate known large-file anomaly).
      **OQ-OPERANDTYPE — RESOLVED 2026-08-26, wired.** All 13 type-
      sensitive instructions (ADD/SUB/MUL/DIV/MOD/EQU/GEQ/GRT/LEQ/LES/NEQ/
      MOV/LIM) now apply a real SINT/INT/REAL/STRING surcharge on top of
      their DINT-rate base weight, derived from the already-captured
      typesweep_* corpus (69 rows). FITTED (single count point per
      type, no linearity cross-check like CPT got) — verified live:
      67/67 real rows land on the identical tiny +5 baseline noise once
      the surcharge is applied (was off by 88-164/rung before).
- ✅ **Motion instructions (MAM/MAS/MAJ/MAH/MSO/MSF/MDW/MAW/MASR/MAFR) and
      cam/route (DCS/CROUT)** — NOT in original scope, added after real data
      showed ~90 real uses across 12 distinct instructions; James: "we use
      lots of motion instructions, camming." Also motion/axis structures
      (AXIS_CIP_DRIVE etc, OQ-PREDEFINED) are the single highest-frequency
      unsized structure category in real tag data, so this pairs with that.
      **2026-08-25: MAH/MSO/MAFR/MASR/MDW/MASD/MGSD/MGSR all CONFIRMED and
      wired.** MAM/MAJ/MAS/MRP were BUILD FAILED (real negative result,
      not untested — see OQ-MAMFAMILY) — **RESOLVED 2026-08-26: root cause
      was a generator bug (bare 2-operand MAH/MSO-shaped calls used for
      instructions needing their own full parameter list), fixed with real
      corpus-transplanted templates. All 4 now CONFIRMED and wired: MAM=224,
      MAJ=236, MAS=100, MRP=128 blocks/rung.** CROUT's build failure
      turned out to be a scope issue, not a bug — James: "Crout is
      safety... requires a safety plc cpu," reclassified OUT OF SCOPE
      alongside DCS. MCCP's logic weight resolved. MAPC's build failure
      WAS a real generator bug (undeclared tag + wrong axis reuse), root-
      caused and fixed 2026-08-25 (OQ-MAPC-COMPAT), James flagged this as
      a 100%-accuracy priority — **CONFIRMED same day, real capture
      landed: error_count=0, logic weight 260/rung, wired.** **CAM
      structure — RESOLVED 2026-08-26**: real 5-point count sweep landed
      (`gen_cam_sweep.py`), `base(8) + per_element(12)`, KNOWN, wired via
      the existing `predefined_array_structures` mechanism — MCCP/MAPC's
      operand tag cost is no longer blocked. Treating this item as fully
      closed — every instruction and every sub-piece (CAM structure now
      included) has a real, definitive, wired status.
- ✅ **GSV/SSV instruction overhead** — NOT in original scope, added after
      real data showed 101/47 real uses; James called these out explicitly.
      Different sizing question than tag-level GSV memory reads (that's a
      dead end, see OQ-MEMREADMETHOD) — this is about the *instruction's own*
      compiled logic footprint in a rung, unrelated. CONFIRMED, wired.
- ✅ Array/file instructions (COP/CLR/FLL/BTD/MVM) at varying array size —
      all CONFIRMED, 0.00% residual.
- ✅ String instructions (CONCAT/DTOS/SIZE/MID/TRUNC) — some real usage,
      not ASCII-module instructions specifically (zero of those seen) — all
      CONFIRMED. (TRUNC has 0 real corpus occurrences, never separately
      tested — flagged, not a gap in practice.)
- ✅ **Indirect addressing overhead — WIRED 2026-08-26.** Parser scans rung
      text for `Name[...]` brackets, classifies direct/literal (0 cost),
      tag-driven (+84/rung), or tag+literal-offset (+108/rung). KNOWN
      confidence — verified live against all 8 real manifest rows (both
      variants × n=10/50/100/1000): every one lands on the identical tiny
      +4 baseline noise. See OQ-INDIRECT in OPEN_QUESTIONS.md.
- 🔴 JSR/subroutine call overhead (call site cost vs routine body cost,
      separate these two numbers) — 238 real JSR uses, matters. JSR's own
      flat weight (72/rung) is CONFIRMED and wired. The SBR/RET generator
      bug (callee-side local tags never declared) is FIXED, and the clean
      retest landed 2026-08-26: all 11 regenerated files build
      error_count=0. Per-param cost is clean and fittable at rung_count=100
      (`512 + 2020*n_params`, exact for n=3/4/6/8/12) but does NOT
      decompose against the rung_count=1000 group (no overlapping param
      counts between the two rung-count batches to solve fixed-vs-per-rung
      cost separately) — still NOT wired, needs one more targeted batch.
      See OQ-JSRPARAMCOST.
- ✅ MSG instruction overhead — only 4 real uses total, low priority, don't
      over-invest here relative to everything else on this list. LOGIC
      weight resolved (48/rung), operand's own MESSAGE-structure tag cost
      still unmodeled (separate, tracked item).
- 🔴 Consolidate full instruction-weight table into MEMORY_MODEL.md — table
      exists and is kept current, but the OQ-JSRPARAMCOST caveat (still
      open) means it isn't a single clean flat-weight-per-instruction
      table yet; OQ-OPERANDTYPE resolved 2026-08-26, no longer blocking
      this. Revisit once JSR param cost lands.
- 🔴 Hold out 3-5 samples, validate fitted model against them, log residual

## Phase 5 — UI v2 (logic browsing)
- 🔴 Extend data contract: routines/rungs feed the same
      `{path, bytes, confidence}` shape as tags
- 🔴 Treemap drill: Task → Program → Routine → (rung-level list, not
      individual-rung treemap nodes — too granular to be useful visually)
- 🔴 Subroutine call-tree rollup (JSR chains sum correctly, no double-counting
      shared subroutines called from multiple places — OQ-JSRSHARED)
- 🔴 "Estimated" badge/color on every logic-derived number in both treemap and
      list views
- 🔴 Combined root view merging tags + logic + module overhead into one map

## Phase 6 — Polish
- 🔴 Safety task scope decision implemented (OQ-SAFETY)
- 🔴 Alarm instance (ALMD/ALMA) overhead if in scope (OQ-ALARM)
- ✅ **Per-part-number memory budget — 2026-08-20, James: "why are you
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
- 🔴 Export report (CSV/XLSX — reuse ControlsAutomation XLAM patterns if useful)
