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
- [ ] UDT alignment/padding rule implemented (OQ-ALIGN) — still tight-packing
      only; every UDT-derived size is tagged confidence=UNKNOWN until this
      lands
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
      built. Right now a UDT only appears sized-in-place at each tag that
      uses it; there's no separate "all UDT definitions" browsable pool.
      Module overhead has nothing to show yet regardless (Module/IO parser
      still unimplemented, see Phase 1).
- [x] Click-to-drill: program → its tags (drilling into a "Program: X" group
      node shows that program's tags)
- [ ] Click-to-drill: UDT → members — NOT built. `sizing/report.py`'s flat
      SizeEntry only carries a UDT tag's *total* size, not a member-level
      breakdown, so there's nothing for the UI to drill into yet. Needs a
      report-contract change (nested entries or a members sub-list per UDT
      tag), not just a frontend change.
- [x] Breadcrumb / back navigation
- [x] Sortable list view (name / type / bytes / %) — click column header to sort
- [x] Type-utilization summary pane (% of budget per data type across whole
      project, not just top-level categories)
- [x] Color coding — reinterpreted: coded by `basis` (KNOWN/ASSUMED/FITTED/
      UNKNOWN) rather than `tier` (exact/estimated), since every entry is
      tier=exact until Phase 4/5 adds logic sizing and a tier-based scheme
      would have nothing to distinguish yet. Basis-coding is live now and
      immediately useful (e.g. a UDT-containing tag renders red/UNKNOWN
      because of the still-open OQ-ALIGN taint). Revisit/extend to tier once
      Phase 5 gives it something to encode.
- [x] Load Phase-0 dev fixture, sanity-check against manual spot-checks

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
- [ ] Generate: 10k-element BOOL array (controller tag)
- [ ] Generate: 10k-element DINT array
- [ ] Generate: 10k-element UDT array (UDT = mix of BOOL/DINT/REAL, ~20 bytes/ea)
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
- [ ] Generate: rung comment presence vs absence at fixed rung count (OQ-COMMENTS)
- [ ] Generate: empty rungs (comment-only, no instructions) at scale
- [ ] Record actual memory delta per sample
- [ ] Fit initial per-instruction weight, log residuals

## Phase 4b — Logic sizing round 2 (other instructions)
Scope set from real instruction-frequency data (OQ-INSTRUCTIONSCOPE,
2026-08-20), not a guessed list — 24,941 real instruction instances counted
across James's 4 production files. Ordered by real-world priority below;
PID and ASCII-module instructions dropped entirely (zero occurrences found).

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
- [ ] Selectable controller memory budget (750KB/1MB/2MB/4MB/8MB) instead of
      hardcoded 4MB denominator
- [ ] Export report (CSV/XLSX — reuse ControlsAutomation XLAM patterns if useful)
