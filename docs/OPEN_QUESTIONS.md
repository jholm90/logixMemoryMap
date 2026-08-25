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
   priority, no reason yet to suspect it's needed. **Deprioritized
   2026-08-25 (James: "move to safety related feature")** — none of the
   3 remaining instructions have a 2nd real corpus example to test
   against anyway, so effort redirects to Phase 6's OQ-SAFETY (safety
   task scope decision) instead of manufacturing synthetic SCP/FBC/PID
   points with no real data to validate against.

   1a. **OQ-INSTRFIRSTPASS-FLATOFFSET — corrected to +12 (was misrecorded
   as +6), narrowed to the shared tag pool, 2026-08-25.** Live-recomputed
   all 74 `instrfirst_*` manifest rows against the current engine: the
   real number is a flat **+12**, not +6 — every one of the 64 "clean"
   files (32 instructions × n=1/n=10, everything except CROUT/MAPC/MCCP/
   MSG, each of which has its own already-known separate gap) shows
   exactly +12, no exceptions. Confirmed independent of both instruction
   choice and rung count (n=1 and n=10 match exactly), which rules out
   any per-instruction weight or per-rung effect and narrows this
   entirely to the shared tag pool every `instrfirst_*` file declares
   (4 REAL, 4 BOOL, 3× DINT[20] array, 3× built-in STRING(82), 1 CONTROL,
   1 MOTION_INSTRUCTION, 1 CAM_PROFILE[5]) — every one of those 7 types
   is independently confirmed EXACT in its own dedicated isolation test
   elsewhere in this project, so the +12 is most likely a real
   interaction effect from having many DISTINCT tag types coexist in one
   file (plausibly a small per-distinct-type registry/metadata cost),
   not a miscalibration of any single type's own formula. Isolating which
   specific type (or the interaction itself) needs one more real point —
   a reduced-pool variant of an already-confirmed `instrfirst_*` file —
   not more analysis of data already on hand. Small (~0.06% of file
   total), low priority, doesn't affect any confirmed weight (marginal-
   delta derivation is immune to a fixed offset).

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

3. **OQ-CMPCPTLAYOUT — mixed-tier CPT, half closed 2026-08-25.** Uniform-
   tier CPT, the T1(ADD/SUB)+T2(MUL/DIV/MOD) mixed case, and now
   **T1T3/T2T3 (POW alongside exactly one other tier)** are all resolved
   and wired. The T1T3/T2T3 real capture data (`group_t1t3_t2t3_scaling`,
   10 files) had actually already landed 2026-08-24 but was never
   reconciled — `pow_tier_mix_base=160, pow_tier_mix_per_operator=64`,
   exact at 4 of 5 operand-count points (k=2,4,10,14 operators), k=7 off
   by the same +16 this project's other CPT formulas also miss by at that
   specific operator count. T1T3 and T2T3 give IDENTICAL real bytes at
   every tested point — once POW is present, T1-vs-T2 makes no measurable
   difference. See `sizing/constants.py` `CptExpressionModel.cost_for`.

   Still open, real data exists but no formula:
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

5. **OQ-PREDEFINED, MESSAGE structure — test batch built 2026-08-25,
   awaiting capture.** CAM is resolved and wired (RESOLVED_QUESTIONS.md).
   MESSAGE's own byte cost stays unmodeled for now, but James reversed
   the earlier deprioritization: "Generate messages to satisfy this
   question? Message instructions are just like axis tags, lots of
   config but always the same data size." `gen_msg_typesweep.py` built 7
   new isolated-MSG files, one per real MessageType found by grepping the
   full `samples/local/` corpus (CIP Data Table Read/Write, PLC5 Typed
   Read/Write, PLC5 Word Range Write, SLC Typed Read/Write — every
   attribute copied verbatim from a real element, never guessed), on top
   of the already-existing CIP Generic file (`instrfirst_msg.L5X`). 8
   MessageTypes now covered total. Once captured, a flat size across all
   8 confirms James's axis-tag-style hypothesis; any spread ties the cost
   to attribute-set complexity instead. MSG's own LOGIC weight (48/rung)
   is separately resolved and wired.

6. **OQ-JSRPARAMCOST — formula CONFIRMED general 2026-08-25, blocked on
   wiring effort now, not data.** JSR's own flat weight (72/rung) is
   confirmed. Per-param cost decomposes as `delta(n,R) = A(n) + B(n)*R`.
   The 3rd disentangle point (n=8 at r=1000,
   `jsr_paramcount_n08_r01000_decompose`) already had real capture data
   on hand (2026-08-24) that was never reconciled. Solved from the
   matching r=100/r=1000 pair the same way n=5/n=10 were: raw marginal
   rate = (256072-43672)/900 = 236/rung; subtracting the already-confirmed
   72/rung JSR base gives `B(8) = 164` — **exact match** to the
   `B(n) = 4 + 20*n` prediction (4+20*8=164). A 3rd independent point
   landing exactly on a 2-point-derived line is real evidence the linear-
   in-n model generalizes, not a coincidence. `A(8)` wasn't independently
   re-solved this pass (the intercept extraction needs the tag-storage
   contribution from each n's own `2n` declared DINT tags controlled for,
   which the original A(5)/A(10) derivation must have done but isn't
   documented step-by-step) — B(n) alone being confirmed exact is the
   operationally important half (it's the per-call-site marginal cost
   that dominates total cost for any routine with multiple call sites).

   **Not wired yet — this is now a parser task, not a capture task.**
   `parser/logic.py`'s `_JSR_TARGET` regex only extracts the target
   routine name, not the call's argument list, so per-call param count
   isn't available to the sizing engine at all yet. Wiring needs: (1)
   parse each JSR call's full arg list to get `n` per call site, (2) a
   `JsrParamCostModel` (mirroring `CptExpressionModel`'s shape) applying
   `B(n)` per call site, (3) `A(n)` charged once per distinct target
   routine regardless of call-site count (needs call-site deduplication
   already partially present via `jsr_target_names`). Real architecture
   work, not a rush-wire.

7. **OQ-MODULEIO — WIRED, LOW CONFIDENCE (n=2), real gap remains, 141
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

8. **OQ-BRANCHDEPTH — real, sizeable, not modeled, closeout batch built
    2026-08-25.** James: "Does bst/bnd ([,]) branches take memory? If I
    have 30 deep or condition it must cost more than 30 xic." **Already
    answered by existing data, confirmed real:** legs01 (no branch,
    control) is an exact 0.00% match, but legs03 is under-predicted by
    16/rung and legs05 by 24/rung — the branch bracket structure itself
    (compiled internally to BST/NXB/BND, not modeled at all by this
    project's regex-based per-instruction-mnemonic parser) DOES cost real
    memory beyond the sum of each leg's own instruction weight. Confirmed,
    not hypothesized. Not linear in leg count (legs01→03 is 8/leg,
    legs03→05 is 4/leg — the per-leg rate is dropping).
    `gen_branchdepth_closeout.py` adds 8 more leg-count points
    (2/4/6/8/10/15/20/30 — legs=30 is a literal real data point for
    James's own "if I have 30 deep" example, not an extrapolation) to fit
    the real curve shape once captured. Branching rungs are extremely
    common in real ladder logic — a genuine gap worth prioritizing.

9. **OQ-LEGACYNETOVERHEAD — reminder flag, not implemented.** Legacy
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
