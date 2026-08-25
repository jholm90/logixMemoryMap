# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md` — this file stays scannable, open items only.
Items marked **[test built]** don't need a decision from James — a
generator already covers them, just waiting on the next capture batch.

1. **OQ-INSTRFIRSTPASS — mostly resolved, small pieces still open.** 34 of
   36 single-instruction weights from the original 36-instruction sweep are
   confirmed and wired (RESOLVED_QUESTIONS.md OQ-INSTRFIRSTPASS-X10); CROUT
   (out of scope, safety-only) and MAPC (fixed, wired at 260/rung) resolved
   separately (RESOLVED_QUESTIONS.md OQ-CROUT-MAPC-BUILDFAIL). Still
   genuinely untested — deliberately not guessed: **SCP** (6-operand
   signature, no 2nd real example), **FBC** (6-operand, 0 real examples),
   **PID** (0 real examples, needs its own structure tag). Also not
   started: a "third pass" for per-file instance/call-site multiplicity
   (rung count is confirmed flat-rate; call-site count is not) — low
   priority, no reason yet to suspect it's needed.

   1a. **OQ-INSTRFIRSTPASS-FLATOFFSET (minor, 2026-08-25).** All 32 clean
   `instrfirst_*` file pairs (everything except MCCP/MSG) show an
   identical flat +6 byte gap at both n=1 and n=10 — doesn't scale with
   rung count, so didn't affect any confirmed weight (marginal-delta
   derivation is immune to a fixed offset). Real, consistent across 32
   independent files, small (~0.03% of file total), not yet root-caused —
   likely something in the shared tag pool these files declare. Low
   priority.

2. **OQ-BASELINE-PROCFW — genuinely open, real and large.**
   `empty_project_baseline=13,296` (RESOLVED_QUESTIONS.md OQ-BASELINE) is
   only confirmed for 1756-L81E/firmware 35.05 — James: "not a constant,
   will change based on processor and firmware." Goal: turn this into a
   (processor_type, firmware_rev)-keyed lookup, likely in
   `controller_budgets.yaml`.

   29 blank files are staged in `samples/manifest.csv` (category
   `fw_baseline`) to isolate the effect across 3 axes (same catalog/
   different firmware; same series/different memory tier; M/S
   feature-suffix variants). **8 of the 29 are contaminated** (real
   `SafetyTask`/`SafetyProgram` despite non-safety-rated hardware —
   `v35_l3100erm`, `v35_l320er/l330er/l340er`, all 4 of
   `v35_l82e/l83e/l84e/l85e`) and flagged `EXCLUDE FROM PROCESSOR/FIRMWARE
   BASELINE COMPARISON` in `notes` — never use their capture data for this
   formula. Capture tooling gotchas found along the way, now standing
   rules: a same-instance Studio 5000 file-switch throws a real
   "Local"-module collision the first time consecutive files change
   PROCESSOR (needs full close/reopen, not just Ctrl+O); 1769-series
   processors show no Capacity number until "Estimate" is clicked first; a
   literal `0` `actual_bytes` is a bad-read symptom
   (`batch_memory_capture.ps1` now auto-flags/retries `ZERO CAPACITY`,
   never counts it as valid).

   **Real data landed so far, all live-recomputed:**
   - `l81_v30` (fw 30.02, manual entry — SDK can't build v30 at all):
     actual 29,272 vs the flat 13,296 prediction, **+120% gap** — proves
     this axis is real and large.
   - `l81_v31=l81_v32`=29,368; `l81_v33`=32,376 (a real, distinct
     +3,000-ish jump — firmware 33.01 carries extra baseline overhead
     v30-v32 don't); `l81_v34`=18,112 (exact match to 35.05/38.02's
     self-closing-routine baseline).
   - 1769-L1x/L2x/L3x family: 69,600-98,944 depending on tier/QBFC1B I/O
     variant — far above both the flat prediction and the L81E family's
     own baseline; not yet decomposed into firmware/family/tier
     components.
   - 5069-L306ER family: base/M-suffix = 18,144; the 3 legitimately-safety
     catalogs (erms2/erms3/ers2) = 18,440 — a real +296 SafetyTask
     overhead signal, only 1 data point at this delta.
   - **"Does an M motion processor need more overhead?" — ANSWERED, no**
     (2 independent base-vs-M pairs, both exactly identical).
   The other 20 non-contaminated `fw_baseline` files remain awaiting
   capture — that capture, not more file generation, is the next step.

3. **OQ-CMPCPTLAYOUT — mixed-tier CPT, still open.** Uniform-tier CPT and
   the T1(ADD/SUB)+T2(MUL/DIV/MOD) mixed case are resolved and wired
   (RESOLVED_QUESTIONS.md OQ-CPT). Still open, real data exists but no
   formula:
   - **T1T3 and T2T3 pairs** (`+`/`**` and `*`/`**`): only single-point
     data (both = 288 for 2 operators, order-independent) — no
     operand-count-scaling sweep like T1T2 got, so no per-operator rate to
     extrapolate. `gen_cpt_mixed_operators.py`'s `group_t1t3_t2t3_scaling`
     (10 files, mirrors the T1T2 sweep) is generated and awaiting capture
     — the direct next step.
   - **All-3-tier mixes**: real data (5 points, n=3/5/8/10/15 operands)
     doesn't fit any simple `base+rate*k` model — the tier mix itself
     shifts as k grows, a real 3-way interaction not decomposed from 4
     points.
   - **REAL operand type inside a mixed expression costs MORE than
     composing the separately-confirmed OQ-OPERANDTYPE surcharges
     predicts** (+40 real vs +16 naive) — genuine unexplained interaction.
   - **Float-literal + REAL-operand together cost LESS than either alone
     would predict if additive** (+200 combined vs +480 if summed) —
     characterized (isolates the original corpus expression's ~150-byte/
     rung mystery exactly) but not reducible to independent terms from
     this data.
   Additive-sum fallback (`CptExpressionModel.cost_for`'s default path)
   stays the right choice for all of the above until each gets its own
   solved formula — real but honestly imprecise there.

4. **OQ-AOIDEF — WIRED for the common case, 2 small threads + array-BOOL-
   packing still open.** Per-type declared-item rate table (BOOL=16,
   SINT/INT=18, DINT/REAL=20, LINT=24 per item, base=1184) is wired for
   single-type AOI defs; mixed-type AOI defs keep the flat rate (real data
   shows per-type rates don't compose additively once BOOL sits next to
   another type). Live-verified against all 85 captured AOI manifest rows:
   32 exact, 52 within 1%, 1 at 2.10%. Full derivation in
   `docs/AOI_KNOWLEDGE_MAP.md`.

   **Still open (both small, <2% of file total):**
   - **AOI name length** doesn't follow the uniform `8*ceil(len/8)` step
     pattern the UDT-name and tag_overhead formulas both use
     (`aoiname_len08/13/20/30`: +8, +16, +16) — needs more name-length
     points.
   - **Required/Visible/Hidden flag combinations**: real deltas land
     within ±24 blocks of the n=4 formula prediction — inside the existing
     small-N noise band, likely genuinely no effect, but a recap batch is
     still awaiting capture to confirm rather than assume.

   **Separately open: AOI-instance-ARRAY element cost, real, not wired.**
   `gen_aoi_array_packing.py`'s 18 real captures show 3 distinct real
   per-element rates depending on member composition: pure-atomic
   (DINT/REAL) ≈124/instance (close to the engine's own 128/instance
   assumption, no correction needed); pure-BOOL ≈4/instance (NOT cleanly
   linear across 5 count points, consistent with a real bit-packing-
   across-array-elements effect crossing an unresolved 32-element
   boundary); 50/50 BOOL/non-BOOL mix = exactly 64/instance (clean across
   all 4 intervals, but only tested at this one ratio). Not wired — the
   mechanism (does an array of AOI/UDT instances bit-pack BOOL members
   across elements?) isn't understood well enough from one member-count/
   ratio to write a general rule. Needs more BOOL:non-BOOL ratios and
   count points crossing n=32 on the pure-BOOL shape specifically.

5. **OQ-PREDEFINED, MESSAGE structure — open, deprioritized.** CAM is
   resolved and wired (RESOLVED_QUESTIONS.md). MESSAGE's own byte cost
   stays unmodeled — James, 2026-08-25: "Message size is fine for the 90%
   accuracy as it's not a common usage instruction," no sweep planned.
   Real research on file if it's ever picked back up: shape is a single
   self-closed `<MessageParameters>` element, but the attribute SET varies
   by `MessageType` (CIP Generic=12 attrs, the type currently modeled, vs
   PLC5 Typed Read=7 attrs) — testing only CIP Generic risks badly
   generalizing to the other 5 real MessageTypes in the corpus. MSG's own
   LOGIC weight (48/rung) is separately resolved and wired.

6. **OQ-XPROGREF — captured, negative gap, unexplained.** Real Logix has
   no direct cross-program tag-addressing syntax; the mechanism is a
   Controller-scoped global with each program declaring its own Local
   alias to it. Single-program alias baseline shows the expected small +64
   gap, but the two-program shared-alias case shows a NEGATIVE gap
   (-3,948, engine over-predicts) — opposite direction from every other
   finding in this project. Hypothesis (unconfirmed): the second program's
   alias to the same Controller-scoped tag may not carry its own full
   `alias_overhead` cost. Needs a 3rd/4th program data point before
   touching code.

7. **OQ-STRINGUDTMEMBER, builtin-as-UDT-member piece — real, not yet
   closeable.** (Custom-type-as-UDT-member is resolved, see
   RESOLVED_QUESTIONS.md OQ-STRINGUDTMEMBER.) At a fixed instance count of
   1, correction as a function of member count m fits `correction(m,n=1) =
   2m - 4`; at a fixed member count of 1, correction as a function of
   instance count n fits `-2n`. These are two 1-D slices through what must
   be a 2-D surface — no combination tried reproduces both without a data
   point at m>1 AND n>1 simultaneously. Needs a 2- or 3-member UDT at n=3
   or n=10 (not yet generated) to disentangle.

8. **OQ-JSRPARAMCOST — decomposition mechanism solved, not yet confirmed
   general, not wired.** JSR's own flat weight (72/rung) is confirmed.
   Per-param cost decomposes as `delta(n,R) = A(n) + B(n)*R` — solved from
   2 param counts (n=5, n=10) where both r=100 and r=1000 data exist:
   `B(n) = 4 + 20*n` (true per-rung, per-call rate), `A(n) = 104 + 20*n` (a
   real one-time cost, likely the subroutine's own Parameters-block
   declaration, paid once regardless of call count). A 2-point linear fit
   is trivially exact and doesn't by itself prove A(n)/B(n) are linear in
   n generally — applying it to the original r=100-only sweep (n=3,4,6,
   8,12) leaves a flat +8 residual, real evidence it might not generalize
   cleanly. `gen_jsr_decompose.py`'s `group_jsr_third_disentangle_point`
   (n=8 at r=1000, matching the existing n=8 at r=100) is generated and
   awaiting capture — the cheapest way to get a 3rd (A,B) solve.

9. **Two generator bugs fixed 2026-08-25, awaiting recapture.** Double
   underscores are forbidden in Rockwell tag names — a name-length padding
   filler could produce one; fixed in 3 places (`cli.py`,
   `gen_string_tagoverhead.py`, `gen_string_batch2.py`) to avoid a
   trailing `_`. AOI call-site tag count must match the definition's
   Required/Visible parameter count — 2 files (`axis_aoi_inout_1_instance`,
   `axis_full_combo`) wired a value into a param declared hidden by
   default; fixed by marking it `required=True, visible=True`. Both
   regenerated, lint-clean, stale capture data cleared, no real data yet.

10. **OQ-MODULEIO — WIRED, LOW CONFIDENCE (n=2), real gap remains, 141
    files awaiting capture.** `module_overhead = 1,672 bytes/module` (flat,
    mean of 2 real deltas: 1756-IB16=1,684, 1734-AENTR/C=1,660), wired in
    `report.py` as ESTIMATED tier. Whether it's really flat or scales with
    connection/point count/module family is unconfirmed off 2 points. 141
    files now in `samples/generated/modules/`: per-catalog sweep (119/119
    real corpus catalogs individually covered, incl. all 13 real Kinetix
    5700 catalogs), rack-level tests (Point I/O rack, 1756-local-rack,
    1756-local-to-1756-remote-via-Ethernet — the last one is a synthesis
    of 2 independently-real pieces, not one literal corpus chain, flagged
    at lower confidence than the rest), a full Kinetix 2-bus/8-axis
    subgraph, and a full-fidelity replica of James's real Bender program
    (69 modules incl. GuardLogix Safety Partner). GuardLogix SIL2/SIL3
    safety-controller handling is a reusable `build_l5x(...,
    safety_level="SIL2"|"SIL3")` capability (real: SIL3 = redundant
    partner beside the CPU + `Width="2"` ICP port; SIL2 = single
    safety-capable primary, no partner). EDS-less devices represented via
    Rockwell's real Generic Ethernet Module mechanism rather than dropped.
    Most of this batch is awaiting real capture — that's the actual next
    step, not more generation.

    Real Studio 5000 conversion errors from the 2026-08-24/25 test batch,
    root-caused and fixed: (a) module-level `SafetyEnabled="true"`
    against a non-safety controller ("Controller is not a Safety
    Controller") — fixed on 8 catalogs (PF527-STO, FANUC robot, 5 Kinetix
    4conn variants, 2× 5069 safety I/O) via `safety_level`; (b) CIP
    Safety `Type="SafetyInput"/"SafetyOutput"` Connections without
    `SafetyEnabled="true"` on the module tag still require a safety
    controller to actually establish — silently failed as "input module
    not present" in the I/O tree despite the L5X importing "ok"; fixed on
    `1734-OB8S/A`, `1734-OB8S/B`, `442G-MABLB-UR-E0JP4679/A`; (c) 5069
    modules need `Port Type="5069"` — placing them on the default 1756/ICP
    backplane threw "Child module incompatible with parent module", fixed
    via `processor_type` switching; (d) User-Defined-Catalog devices
    (150 SMC Flex-E, PowerFlex 525-EENET) need their real
    `ExtendedProperties/UdcAopVersion` schema — it's functionally
    required for Decorated Data validation, not boilerplate like standard
    AB catalog modules; stripping it threw "Data type mismatch", fixed by
    restoring verbatim. PowerFlex 755-EENET does NOT share this (fixed,
    non-hashed DataType names, no UdcAopVersion) — confirmed untouched.
    Also fixed: duplicate Ethernet IP across drive+power-supply pairs,
    non-unique `AxisID` on 2+ coexisting `AXIS_CIP_DRIVE` tags (now
    SHA-256-derived per tag name), a real slot collision in the EN2T
    downstream prototype, and `ParentModPortId="4"` (real source has more
    physical ports than the wrapper synthesizes) on 9 catalogs.

    James also flagged the 1734/1756 rack-level test files as having
    non-tight-packed slot addressing ("a 1734 module you placed in slot
    10" concern) — audited both the sizing engine
    (`l5x_memory_analyzer/parser/modules.py::_structure_size`) and the
    rack generators: **verified not a bug.** Module data size is read
    exclusively from the module's own real `ArrayMember/@Dimensions` in
    its Connection Structure; `Port/@Address` (slot number) is parsed
    into `ModuleInfo.slot` for display only and never feeds size math.
    The rack generators' slot gaps are real captured addresses kept
    as-is from source programs (real point-bus positions, not
    synthesized) — cosmetically loose, not a sizing defect.

    **Deliberately NOT charged `module_overhead`, flagged not guessed:** a
    rack-aliased module (`RackConnection`/`InAliasTag` — zero real data on
    whether its cost resembles a module with its own Connection) and
    `CatalogNumber="Embedded"` modules (CompactLogix 5370 "ER" built-in
    I/O). Produced/consumed tags remain untouched (OQ-PRODCONS). Still
    open: PowerFlex 525 has multiple real I/O data-payload UDTs beyond
    the one profile currently covered — needs more real corpus examples
    before building a variant sweep, not guessed.

11. **OQ-BRANCHDEPTH — real, sizeable, not modeled.** A parallel branch
    bracket has its own real structural cost beyond the sum of its legs'
    instruction weights: legs01 (no branch) is an exact match; legs03 is
    under-predicted by 16/rung; legs05 by 24/rung. Not linear in leg count
    (legs01→03 is 8/leg, legs03→05 is 4/leg — the per-leg rate is
    dropping). Only 2 non-trivial points — needs at least one more (e.g.
    legs02, legs04, legs07/10) to see whether it's log-ish/diminishing-
    marginal or something else. Branching rungs are extremely common in
    real ladder logic — a genuine gap worth prioritizing.

12. **OQ-LEGACYNETOVERHEAD — reminder flag, not implemented.** Legacy
    chassis/remote-I/O platforms (SLC/PLC-5/RIO/DH+/ControlNet) are
    deliberately out of the current module sweep. James: "allocate as
    controller tag size plus some arbitrary overhead value... this is a
    reminder flag to see what average overhead values are on these
    isolated Ethernet style networks to be updated once you have more
    networking knowledge." Approach when picked up: size the I/O side the
    same way a modern module already works (`_structure_size` member-sum),
    add a flat placeholder overhead constant, ASSUMED basis not FITTED,
    clearly tagged as a rough placeholder in `memory_model.yaml` pending
    real RIO/DH+/ControlNet capture data. No real corpus, no capture data,
    nothing to size against yet.
