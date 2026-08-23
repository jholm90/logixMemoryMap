# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md` — this file stays scannable, open items only.
Items marked **[test built]** don't need a decision from James — a
generator already covers them, just waiting on the next capture batch.

1. **OQ-INSTRFIRSTPASS [test built, 2026-08-24].** James: "Everything that
   has more than one usage needs to be tested... one copy for all of the
   outstanding instructions, one per file properly compiled." 36 new
   single-rung files, one per instruction, `gen_instruction_firstpass.py`
   — full list and real-corpus citation per instruction in that
   generator's own docstring. All 36 lint-clean and valid XML. Two new
   completely-unmodeled predefined structures discovered building this:
   - **MESSAGE (used by MSG).** Real shape is a single self-closed
     `<MessageParameters>` element (much simpler than TIMER/COUNTER),
     copied verbatim from a real CIP Generic get-attribute message
     (`BaillieLeitchField_Edger_20260812_r00.L5X`, `MESSAGE_Alarms`) —
     `builders.py`'s new `message_tag_xml`. Byte size completely unknown,
     `instrfirst_msg.L5X` uses `write_sample_unmodeled`.
   - **CAM (used by MCCP/MAPC) — NOT the same as CAM_PROFILE.** Real shape
     fully visible (unlike CAM_PROFILE's hidden fields): array of
     `{Master:REAL, Slave:REAL, SegmentType:DINT}` structures, confirmed
     against `samples/local/L5X_Samples/RobbinsGrn_2026_05_13r00.L5X`
     (`NewCI2Cam`) — `builders.py`'s new `cam_tag_xml`. Byte size
     completely unknown, `instrfirst_mccp.L5X`/`instrfirst_mapc.L5X` use
     `write_sample_unmodeled`.

   **Deliberately skipped, not guessed** (see the generator's own
   docstring for full reasoning): **SCP** (2 real occurrences, one real
   example shows 3 args but official Rockwell docs describe 6 — unresolved
   without a second real example), **FBC** (8 occurrences, 0 real
   examples, 6-operand signature too complex to risk), **PID** (3
   occurrences, 0 real examples, needs a whole dedicated structure tag).
   These 3 remain genuinely untested — flag if a real reference sample
   ever turns up for any of them.

   **NEAR_VERBATIM entries needing extra scrutiny before trusting their
   build result:** CROUT and MAPC were reproduced as close to a literal
   real corpus call as possible (only tag names substituted) rather than
   independently understood operand-by-operand — see the generator
   docstring's CORPUS_CONFIRMED/INFERRED/NEAR_VERBATIM tier definitions.
   If either fails to Build, that's real information (means even the
   literal real shape doesn't transplant cleanly with substituted tag
   names), not just "try again."

   **2026-08-24, ALL 36 captured clean.** Every file converted "ok" and
   returned real `actual_bytes`, including every NEAR_VERBATIM/unmodeled
   one (MAPC, CROUT, MCCP, MSG) — the higher-risk shapes all held up.
   n=1 marginal weight per instruction (`actual - engine_prediction`,
   isolates each instruction's real per-rung cost since nothing here is
   in `logic_instructions.weights` yet so the engine's own contribution is
   always 0): NOT (46), TRN (58), NEG (46), OSR (62), OSF (62), UID (46),
   UIE (46), MCR (22), TND (30), ATN (66), DEG (70), RAD (122), TAN (66),
   SQR (58), SWPB (82), XOR (46), FIND (106), INSERT (122), BSL (66),
   BSR (66), FFL (78), FFU (78), SRT (122), AVE (182), FAL (110),
   FSC (110), MAFR/MASR/MDW/MASD (66 each), MGSD/MGSR (62 each),
   CROUT (34). MCCP (362), MAPC (158), MSG (826) each entangle the new
   unmodeled CAM/MESSAGE structure's own byte cost with the instruction's
   weight — can't be split from n=1 alone. **These are all preliminary —
   James: "let's to a 10-count test for each. If something comes out of
   line then we can do more per instruction testing as required."**
   `main()` now also emits a parallel `_x10` file per instruction (10
   identical rungs, same shape/pool) specifically to check whether each
   n=1 number really is a flat per-rung rate before anything gets wired
   into `memory_model.yaml` — do NOT treat the numbers above as confirmed
   weights yet, they're one data point each. Once `_x10` data lands: for
   the 33 plain instructions, weight = gap_10 (since fixed costs are
   already subtracted out by the engine's own baseline+routine-base
   prediction, a truly flat per-rung weight means gap_1 == gap_10/10 ==
   the per-rung rate — any instruction where gap_1 ≠ gap_10/10 is exactly
   James's "something comes out of line," flag it here for a dedicated
   deeper sweep same as CPT/LBL-JMP got). For MCCP/MAPC/MSG specifically,
   the two count points let the structure cost and the instruction weight
   be solved simultaneously: `weight = (gap_10 - gap_1) / 9`,
   `structure_cost = gap_1 - weight`.

   Once these 36 (now 72, n=1 + n=10) are fully confirmed, the THIRD pass
   (James: "once we have all valid data for all instructions then we can
   do the 5/10 usage per file for each" — meaning per-file instance/call-
   site multiplicity, not rung count, for whichever instructions still
   need it) is the natural follow-up — not started yet, intentionally,
   per James's explicit sequencing.

2. **OQ-BASELINE-PROCFW (new, 2026-08-23, James).** `empty_project_baseline`
   (13,296, see RESOLVED_QUESTIONS.md OQ-BASELINE) is **not a universal AB
   constant** — James: "Keep in mind your empty project baseline is not a
   constant and will change based on processor and firmware. You need to
   be aware of this." Confirmed by inspection: virtually every sample this
   project has generated uses `wrapper.py`'s single default processor
   (1756-L81E, SoftwareRevision 35.05) — the 200+ "independent" data points
   behind the 13,296 confirmation are independent in test CONTENT, not in
   processor/firmware, so what's actually confirmed is "13,296 for
   1756-L81E rev 35.05," not "13,296 for any CompactLogix/ControlLogix."
   James: another test batch is coming — roughly 30 blank (no tags/logic)
   files, one per processor model, to isolate the per-processor baseline,
   plus a same-processor/different-firmware-revision set to isolate the
   per-firmware component separately. **Action needed once that data
   lands:** `empty_project_baseline` needs to become a lookup keyed on
   (processor_type, firmware_rev) rather than a single scalar — likely
   sourced from `controller_budgets.yaml` alongside the existing per-
   processor memory-budget table, not a bare constant in memory_model.yaml.
   Until then, treat 13,296 as valid ONLY for 1756-L81E/35.05-class
   projects; flag this prominently in the UI once the UI surfaces this
   number, not just in docs.

   **2026-08-24, batch received and staged, awaiting real capture.** 29
   blank L5X files (`samples/local/fw_versions/`, gitignored, real James
   exports) — confirmed clean (0 tags, 0 DataTypes, 0 errors through the
   current engine, every one currently predicts the flat 13,296 regardless
   of processor/firmware, exactly the gap this question is about). **L5X
   itself carries no memory-usage/Capacity-tab data at all** — confirmed
   by inspecting every file's raw XML; the real numbers can only come from
   Studio 5000 (Controller Properties → Memory tab / the existing AHK
   capture pipeline), same workflow as every other sample. Organized into
   James's own 3 comparison axes, ready for real capture:
   - **Same catalog, different firmware:** `l81_v30` through `l81_v38` (7
     files, 1756-L81E, SoftwareRevision 30.02→38.02, otherwise identical).
   - **Same series, different memory capacity:** three separate families —
     `v35_l82e`/`l83e`/`l84e`/`l85e` (1756-L8xE, ControlLogix 5580);
     `v35_l16er`/`l18er`/`l19er` (1769-L1xER, CompactLogix 5370);
     `v35_l306er`/`l320er`/`l330er`/`l340er`/`l3100erm` (5069-LxxxER,
     Compact 5000) — each family same firmware (35.05), same base
     hardware line, escalating memory tier only.
   - **Same catalog family, M(otion)/S(afety) feature suffix:**
     `v35_l306er` (base) / `l306erm` (M) / `l306ers2` (S) / `l306erms2`
     (M+S) / `l306erms3` (M+S, rev 3) — a clean 5-way isolation of M vs S
     vs both, same base catalog/memory tier throughout. Also
     `v35_l18er`/`l18erm` (base vs M) and `v35_l24er`/`l24er_qbfc1b`/
     `l27erm_qbfc1b` (base vs a QBFC1B I/O variant vs M+QBFC1B) as smaller
     secondary examples.
   Not yet in `samples/manifest.csv` (that CSV only ever tracks
   `samples/generated/` files per existing convention, real `samples/
   local/` files never have been) — once James reports real Capacity
   numbers per file, do the actual 3-way comparison directly, then decide
   the right place to persist the per-(processor,firmware) baseline table.

3. **OQ-AXISDEEP — FULLY RESOLVED 2026-08-25.** CIP/virtual axis, used
   everywhere in real programs, 0.01%-tolerance target. **Partially
   resolved 2026-08-23** — the pure predefined-structure constants
   (AXIS_CIP_DRIVE, AXIS_SERVO, AXIS_VIRTUAL, COORDINATE_SYSTEM,
   MOTION_GROUP) derived and wired in, see RESOLVED_QUESTIONS.md
   OQ-PREDEFINED. The remaining composite case (a UDT/AOI that embeds an
   axis as a member alongside other stuff) is now also resolved — see
   RESOLVED_QUESTIONS.md OQ-AXISDEEP for the `axis_composite_udt_*` real
   data. No open piece remains.

4. **OQ-MIXEDUDT [test built].** Realistic messy/nested UDTs (not
   homogeneous arrays) — `gen_axis_composite.py`'s composite UDT covered
   the axis-embedding case specifically (now resolved, see OQ-AXISDEEP
   above), but the broader "realistic messy/nested UDT, arbitrary member
   mix" question is still open pending its own dedicated capture.

5. **OQ-ALIASSIZE — RESOLVED 2026-08-25.** See RESOLVED_QUESTIONS.md
   OQ-ALIASSIZE. Real formula `56 + 8*floor(namelen/8)` derived and wired
   into `memory_model.yaml`/`report.py`.

6. **OQ-CMPCPTLAYOUT [test built, new 2026-08-22, extended same day,
   MAJOR CORRECTION 2026-08-23].** Operator/layout/optimization sweep for
   CPT and CMP (`tag**tag` vs `tag*tag` vs `tag-tag`, a 6-operand chain,
   same-tag-vs-distinct-tag and redundant-literal dedup probes, compound
   boolean expressions) — plus, per James's follow-up ("are you testing
   these with tags only? You might want to test with float/decimal
   constants as well"), an integer-literal and float-literal operand
   variant for every operator, both CPT and CMP, against the existing
   tag-vs-tag baseline. `gen_cmpcpt_layout.py`. Awaiting capture.

   **2026-08-22 batch result:** the 3 compound-CMP files (`cmpcpt_cmp_
   and_compound`, `_or_compound`, `_duplicate_cond` — expressions like
   `L0>L1&L2<L3`, no parens around each comparison) failed Build 100% of
   rungs. James's own verified `categoryB.L5X` only exercises a *single*
   CMP condition (`CMP(ThisVal >= (ThatVal+1))`, matches the already-
   passing `cmpcpt_cmp_single` variant) so it doesn't confirm or deny the
   compound case. Hypothesis, NOT yet confirmed against real corpus or a
   real sample per this project's rule against guessing instruction
   syntax: each comparison sub-clause may need its own parens, e.g.
   `CMP((L0>L1)&(L2<L3))`. Needs a real Studio 5000-verified sample
   before `gen_cmpcpt_layout.py`'s `group_cmp_layout` gets touched.

   **2026-08-23, MAJOR: the existing "CPT = 452 blocks/rung, 0.00%
   residual" claim in MEMORY_MODEL.md is WRONG as a general constant.**
   That number was fit against exactly one complex CPT expression shape
   from the original 244-file calibration sweep — it is not CPT's cost,
   it's *that expression's* cost. The `cmpcpt_cpt_*` sweep (simple
   2-operand expressions like `CPT(L2,L0+L1)` against a small 12-tag pool:
   8 DINT L0-L7, 3 REAL, 1 BOOL) shows the engine wildly over-predicting
   when it applies 452/rung — e.g. `cmpcpt_cpt_op_add_n01000` (1000 rungs):
   engine says +452,000 blocks of CPT cost, real delta is only ~123,736
   (452/rung over-predicts by 328,264 blocks on this one file). CPT's real
   per-rung cost is clearly expression-complexity-dependent (operand count,
   operator count, or both) — a single flat rung-weight cannot model it.
   **Not fixed in code tonight** — this needs a genuine per-operand/
   per-operator cost model (parse the CPT expression string, count
   operators/operands, fit weights per token type), which is a real
   architecture change to `sizing/logic.py`, not a constant edit. Until
   that lands, treat any CPT-heavy program's estimated-tier logic number
   as unreliable, and the 452/rung constant currently in
   `memory_model.yaml` as **known-wrong, not yet removed** because nothing
   better has replaced it and leaving it 0 would be worse. Flagged loudly
   here so this doesn't quietly stay believed "exact."

7. **OQ-AOIDEF (new, 2026-08-23, MAJOR — real cost currently modeled as
   zero; DATA QUALITY WARNING added same day, see below before trusting
   any number in this entry).**

   **Data quality warning, James 2026-08-23:** "I think the sample I gave
   as def_only I accidentally added the controller tag and added it to a
   rung as well." Confirmed in manifest.csv: **7 structurally different
   `*_def_only` AOI files show byte-for-byte identical `actual_bytes`
   (19392)** — `aoiname_len13_def_only`, `localcount_n04_def_only`,
   `localtype_dint_n4_def_only`, `localtype_real_n4_def_only`,
   `paramcount_n08_def_only`, `paramtype_dint_n4_def_only`,
   `paramtype_real_n4_def_only`. These have genuinely different member
   counts/types/name lengths — 7-way exact agreement is not plausible as a
   real coincidence, consistent with James's own explanation: a modified
   (controller-tag-added, rung-referenced) file got captured under
   multiple sample_ids instead of the clean 0-instance definition.
   Generator code itself is NOT the bug — re-read `gen_aoi_sweep.py`'s
   `_def_and_instance`/direct `_write` calls for the def_only case:
   `tags_xml=""` (no controller tag), default single-NOP rung (no
   reference to the AOI at all) — confirmed clean. This is a capture/
   labeling mixup on the capture side, not a generation bug.
   **Consequence: every number derived from this batch of `*_def_only`
   data below is now suspect, including the "clean, confident" local-tag-
   count fit** (its n=4 point, `localcount_n04_def_only`, is one of the 7
   contaminated rows). **These 7 sample_ids need a clean re-capture before
   any of this data is trusted again** — don't backfill or re-derive
   anything from the current values. Keeping the raw numbers and the
   original (now-suspect) sub-findings below for reference/context only,
   not as confirmed real data. AOI *definition* cost (the AOI's own Parameters/LocalTags
   declaration — separate from any tag that instantiates it) is not
   modeled at all right now; `report.py` only emits `udt_definition`
   entries for true UDTs, explicitly skipping AOI definitions pending a
   confirmed formula. Real data says this is NOT negligible: every
   `*_def_only` real sample (an AOI declared with zero tag instances, so
   the entire real Capacity delta is pure definition cost) shows a
   consistent, large unmodeled gap. Baseline reference: engine currently
   predicts 18,128 (empty_project_baseline 13,296 + one empty routine
   4,832) for every one of these files regardless of the AOI's actual
   shape; real `actual_bytes` ranges 18,432 (motorstatus, plain UDT-typed
   AOI param) to 21,760 (deepnest3) — i.e. the engine is short by
   **1,100-3,600+ blocks per distinct AOI definition**, and every real
   program has at least a few AOI definitions. This is the single largest
   remaining unmodeled category found in tonight's rebase.

   Sub-findings from the real sweep data (`samples/manifest.csv`,
   `*_def_only` rows, all `error_count=0`), by how clean each axis is:

   - **Local-tag count — CLEAN, confidently fittable.** `localcount_n01/
     02/04/08/16/32_def_only`: 19336, 19360, 19392, 19472, 19632, 19952.
     Exact linear fit from n=4 upward: `19312 + 20*n` (verified exact at
     n=4,8,16,32). n=1,2 sit slightly below that line (19336 vs predicted
     19332, 19360 vs 19352) — the same small-N-anomaly pattern already
     documented for the ordinary UDT-definition formula, not a new
     mystery. So: base AOI-def cost ≈ 1,184 blocks above the
     baseline+empty-routine floor, plus ≈20 blocks/local tag (at DINT
     size) once n≥4. NOT yet wired into code — see below for why.
   - **Param count — NOT clean.** `paramcount_n01/02/04/08/16/32`: 19336,
     19360, 19360, 19392, 19632, 19952. n02 and n04 are identical (19360),
     which doesn't happen anywhere in the local-tag sweep — either a real
     structural difference (e.g. Rockwell always allocates a minimum
     param-block size that n02 and n04 both fit inside) or a generator
     quirk in how "paramcount" counts the always-present EnableIn/
     EnableOut params. Needs the actual generated XML inspected before
     trusting any fit here.
   - **AOI name length — NOT clean.** `aoiname_len08/13/20/30`: 19384,
     19392, 19408, 19424. Diffs are +8, +16, +16 — not the uniform
     `8*ceil(len/8)` step pattern the UDT-name-length and tag_overhead
     formulas both use. Needs more name-length points to characterize.
   - **Local/param atomic type — real but not cleanly resolved.**
     `localtype_{bool,sint,int,dint,lint,real}_n4_def_only`: 19376, 19376,
     19384, 19392, 19408, 19392. BOOL and SINT tie; INT/DINT step by +8
     each; LINT steps by +16; REAL ties DINT (both 4 bytes, makes sense).
     Looks like local-tag cost is quantized to some coarser unit than raw
     bytes (consistent with "blocks" already being a rounded reporting
     unit), not a simple per-byte scale-up of the 20-blocks/DINT-local
     number above. `paramtype_*_n4` matches `localtype_*_n4` point for
     point, so whatever this is, it's the same effect for params and
     locals. `paramtype_*_n8` (19440-19504) roughly doubles the n4 deltas,
     consistent with linear-in-count once the per-type unit is nailed
     down.
   - **BOOL run/pack adjacency — real, sizable effect, not modeled.**
     `aoi_boolrun_n04/08/12/16/20_def_only`: 19368, 19424, 19488, 19552,
     19616 (roughly +14-16/BOOL local, close to but not identical to the
     DINT-local rate above). `aoi_boolpack_*_def_only` (same 20-param
     total, different BOOL arrangement): consecutive20=19632,
     clean_grouped=19664, clean_alternating=19664, interspersed20=20112.
     Interspersed is **480 blocks more expensive** than consecutive for
     the identical param count — real bit-packing-locality cost, the AOI-
     parameter analog of the UDT `bool_run_bonus` constant, but clearly a
     different (larger, position-sensitive) effect. Not characterized.
   - **Nested/array locals, deepnest, composite — real, large, raw data
     only.** `aoi_array_localtag_def_only`=19328, `aoi_array_param_def_
     only`=19336 (both ~= baseline, arrays-of-0-or-1 elements probably),
     `aoi_nested_array_localtag_def_only`=20528, `nested_aoi_def_only`=
     20536, `aoi_deepnest3_def_only`=21760 (3 levels of AOI-calling-AOI —
     by far the largest single def_only value in the corpus),
     `aoi_inout_dint_def_only`=`aoi_inout_string_def_only`=19336 (InOut
     params cost the same regardless of pointed-to type, consistent with
     InOut being a reference/pointer, matches the existing InOut-excluded
     assumption elsewhere in `udt.py`), `aoi_realistic_composite_def_
     only`=19888. No formula attempted here — flagging the raw numbers so
     a future session doesn't have to re-derive them from manifest.csv.

   **Deliberately NOT wired into code tonight, even the clean local-count
   piece.** Wiring only the local-tag-count term while param-count,
   name-length, atomic-type-sensitivity, and bool-adjacency are all still
   tangled would systematically underpredict any AOI that's param-heavy
   or BOOL-heavy — i.e. most real AOIs — while looking like a real,
   trustworthy EXACT-tier number. That's a worse failure mode than the
   current honest zero (which at least visibly under-predicts by a
   constant-ish amount you can mentally pad for), and it would violate
   CLAUDE.md's ground-truth constraint by presenting a partially-fit
   guess as EXACT-tier alongside the genuinely-exact tag/UDT numbers.
   This needs a dedicated session: inspect the actual generated AOI XML
   for the paramcount/name-length anomalies, get a couple more real
   name-length and param-count points, then build a proper
   `compute_aoi_definition_cost()` mirroring `compute_udt_definition_cost`
   — base + per-param + per-local + name-length + bool-adjacency terms,
   each independently confirmed the way the UDT formula's terms were.

   **2026-08-24, NEW real finding — AOI instances inside an ARRAY may cost
   roughly HALF what the engine currently predicts per element.** 4 clean
   real data points now exist for the exact same AOI shape ("RealisticAOI"
   /"RealisticAOI50", 5 DINT+5 BOOL In / 5 DINT+5 BOOL Out / 5 REAL+5 BOOL
   Local — not contaminated, none of these 4 sample_ids are in the
   7-way-identical list above): `aoi_realistic_composite_def_only` (n=0),
   `_1_instance`/`aoi_realistic_50_instance_1` (n=1, two independent real
   captures of the identical shape agreeing exactly at 20,040 — good cross-
   validation), `_10_instance_array` (n=10), `aoi_realistic_50_instance_
   array` (n=50). Solving the array points (n=10, n=50) as two equations:
   real per-element cost inside the array = **64 bytes/instance**, flat
   array-tag overhead ≈104 — but the engine's own (already-correct,
   already-confirmed) per-instance AOI size for THIS shape is 128 bytes
   (matches the n=1 standalone-tag case exactly: 220 = tag_overhead(~92)
   + 128). **The array case is real-data-confirmed at roughly half that
   per-element rate.** Leading hypothesis: BOOL Parameters/LocalTags
   (OQ-AOIBOOLPACK, still open — currently implemented as unpacked/4-bytes
   since the flat AOI XML shows no hidden-SINT/BIT-alias representation)
   might actually pack 8-per-byte specifically once put into an ARRAY of
   AOI instances, the same way a UDT's BOOL array-of-elements packs
   differently than either a scalar BOOL tag or a UDT member — i.e. this
   could be OQ-AOIBOOLPACK's real answer, but only surfacing in the array
   context. **Not confirmed, only 2 array data points, both using the same
   BOOL-heavy shape** — can't yet separate "AOI arrays pack BOOLs" from
   "AOI arrays are cheaper per-element for some other reason entirely."
   Needs a dedicated follow-up: an AOI-instance array with ZERO BOOL
   members (pure DINT/REAL In/Out/Local) at 2+ array-count points, to
   isolate whether the ~50% reduction is BOOL-specific or a general
   array-of-AOI effect. Not wired into code — this is the opposite failure
   mode risk from the paragraph above (wiring a real-looking-but-
   unisolated array discount could UNDER-predict a real BOOL-free AOI
   array).

   **2026-08-25 [test built], James: "generate as many files as needed to
   resolve all possible scenarios for 100% accuracy."** `gen_aoi_array_
   packing.py`, 18 files, 3 AOI shapes × 6 points each (def_only + array
   counts 1/5/10/25/50): `aoipack_atomic_*` (10 DINT In/10 DINT Out/10
   REAL Local, ZERO BOOL — if this shape's real per-element array rate
   matches the engine's own already-confirmed UDT-style prediction
   exactly, that CONFIRMS the ~50% discount above is BOOL-specific, not a
   general array-of-AOI effect), `aoipack_bool_*` (10/10/10 BOOL, nothing
   else — the cleanest possible read on the BOOL-array-packing question,
   no DINT/REAL confounding the math), `aoipack_mixed_*` (same 5-DINT-5-
   BOOL-per-section composition as the original RealisticAOI finding, but
   with 5 count points instead of 2, to firm up the 64-bytes/element
   reading with a real multi-point linear fit and catch a small-N anomaly
   if one exists, matching this project's established pattern elsewhere).
   Awaiting capture.

8. **OQ-PREDEFINED, remaining piece [test built].** MOTION_INSTRUCTION,
   AXIS_CIP_DRIVE/AXIS_SERVO/AXIS_VIRTUAL/COORDINATE_SYSTEM, and
   MOTION_GROUP are now derived and wired in (see RESOLVED_QUESTIONS.md
   OQ-PREDEFINED). What's still open: `CAM` (the drive/cam-instruction
   wrapper, not `CAM_PROFILE` the array structure, which IS resolved) is
   still untested. Awaiting capture.

9. **OQ-XPROGREF [test built, captured 2026-08-25, NEGATIVE GAP,
    UNEXPLAINED].** Real Logix has no direct cross-program tag-addressing
    syntax in logic (confirmed: searched all 47 real corpus files, no
    `Program:Tag`-style reference exists anywhere in rung Text). The real
    mechanism is what you described earlier — a Controller-scoped global
    with each program declaring its own Local alias to it. `gen_xprogref.py`
    single-program alias baseline vs two-program shared-alias real capture
    now in hand: `xprogref_singleprog_alias_n01000` shows the expected
    small +64 gap (consistent with ordinary alias_overhead once wired),
    but `xprogref_twoprog_shared_alias_n01000` shows a NEGATIVE gap
    (-3948, engine over-predicts) — the opposite direction from every
    other open finding here. Not yet root-caused. Hypothesis (unconfirmed):
    the second program's alias to the same Controller-scoped tag may not
    carry its own full alias_overhead cost (some sharing/dedup at the
    tag-table level for the second reference), but this needs a 3rd/4th
    program data point to confirm before touching code — do not wire
    anything off a single 2-program sample.

10. **Motion instructions — MAH/MSO RESOLVED, MAM/MAJ/MAS/MRP BUILD
    FAILED (real capture 2026-08-25).** `gen_motion_instructions.py` —
    MAH/MSO's real per-rung logic weight (60 blocks/rung each) is now
    confirmed and wired, see RESOLVED_QUESTIONS.md OQ-MAHMSO. MAM/MAJ/MAS/
    MRP were captured using the *same* documented 2-operand
    `(Axis,MotionInstruction)` syntax already confirmed working for
    MAH/MSO/MAFR/MASR — real result: 100% build failure, every rung in
    every `motioninstr_mam*`/`motioninstr_maj*`/`motioninstr_mas*`/
    `motioninstr_mrp*` file errored (`error_count == rung_count`). This is
    a genuine negative result, not "untested" — the documented syntax is
    wrong or incomplete for these 4 specific mnemonics and needs a real
    Studio 5000-verified reference sample before another generator
    attempt (no guessing syntax per CLAUDE.md). MAPC/MCCP camming still
    blocked separately on the unmodeled CAM structure, see
    OQ-PREDEFINED item 8 below.

11. **Per-Task overhead [captured 2026-08-25, real finding, NOT wired —
    needs parser architecture work first].** `gen_task_overhead.py` —
    2nd/3rd Task, isolating pure Task/Program scaffolding cost from logic
    content. `taskoverhead_n02tasks`/`n03tasks` real data gives an exact
    linear marginal cost of **-1472 bytes per extra Task** (engine
    currently over-predicts by that much per additional Task) relative to
    the engine's current `fixed_base_per_routine` assumption. Exact
    linear across the 2 available points, but wiring this correctly
    requires the parser to distinguish per-Task, per-Program, and
    per-routine-within-a-program overhead as three separate quantities —
    that distinction doesn't exist in the current model (every
    calibration sample to date had exactly one Task/one Program/one
    routine, so the three were indistinguishable and got collapsed into
    one `fixed_base_per_routine` constant). Do not patch this as a
    per-routine correction; it needs its own model field and a parser
    change to count Tasks/Programs/Routines separately, which is a real
    (if small) architecture task, not a one-line constant fix. Left open
    deliberately rather than rush-wired.

12. **Indirect addressing overhead [captured 2026-08-25, real findings,
    NOT yet decomposed into weights].** `gen_indirect_addressing.py` —
    direct vs. tag-driven array index, plus (James: "Does tag[idx+1] take
    up the same space as tag[Idx]?") a third variant with an arithmetic
    offset inside the index. **2026-08-23 rebase-check note:**
    `indirect_direct_index_n01000` (1000 rungs) showed only a 4-block gap
    against the current engine — direct indexing needs no separate cost.
    **2026-08-25, tag-driven variants now captured:**
    `indirect_tag_index_n01000` shows ~84 blocks/rung above the direct-
    index baseline, and `indirect_tag_offset_index_n01000` (the
    arithmetic-offset `tag[idx+1]` variant) shows ~108 blocks/rung above
    baseline — so an arithmetic offset inside a tag-driven index costs
    more than a bare tag-driven index, as James's question anticipated.
    Neither number is yet decomposed into a clean weight (both are a
    single-instruction, single-count data point per variant) — needs at
    least one more count point per variant (e.g. n=10) before wiring into
    `logic_instructions.weights`, to confirm linearity and rule out a
    fixed one-time cost being misread as a per-rung weight.

13. **OQ-STRINGTAGOVERHEAD (new, 2026-08-24).** `tag_overhead`'s formula
    (`84 + 8×floor(name_len/8)`) was confirmed type-independent using
    SINT/INT/DINT/LINT/REAL/BOOL — STRING was never separately checked.
    `string_builtin_x1000` (1000 built-in STRING tags) and `customstring_
    250char_x1000` (1000 instances of a 250-char custom string type) both
    now show the engine over-predicting by almost exactly **-2 bytes/tag**
    (-2000/1000 and -1998/1000 respectively — same effect, both STRING
    families, independent of DATA length). Real and consistent across two
    independent large-count captures, but only ONE count point each
    (n=1000) — can't yet tell whether it's a genuine flat -2/tag rate or
    some other count-dependent shape that happens to look flat at this
    scale (same caution as everywhere else in this file: one data point
    isn't a confirmed formula). Small enough (~1% of the STRING-family
    total) that it doesn't invalidate anything, but real enough to log.
    Needs a proper STRING-tag-count sweep (n=1/10/100/1000) before wiring
    a `-2` correction into `tag_overhead` for STRING types specifically.

    **2026-08-25 [test built], James: "generate as many files as needed to
    resolve all possible scenarios for 100% accuracy."** `gen_string_
    tagoverhead.py`, 22 files, 3 axes: `stringoverhead_builtin_n*` (9
    points, n=1/2/5/10/25/50/100/500/1000, dense enough to catch a
    non-linear shape, not just confirm a straight line between 2 points),
    `stringoverhead_custom{50,500}_n*` (8 points, 2 max-lengths × 4 counts
    — confirms the effect is a pure per-tag-declaration thing, not a
    DATA-length effect in disguise), `stringoverhead_namelen*_n050` (5
    points, name length 4/8/16/32/40 at fixed count — confirms whether the
    existing `8×floor(len/8)` name-length term shape still holds for
    STRING with only the flat base needing a correction, or something
    structurally different is going on). Awaiting capture.

14. **OQ-OPERANDTYPE (new, MAJOR, found 2026-08-25 mining already-captured
    but never-analyzed `typesweep_*` data — NOT wired, needs parser
    architecture work).** The entire `logic_instructions.weights` table
    assumes a per-instruction weight is independent of the data type of
    its operands (every existing confirmed weight was fit off DINT-operand
    sweeps). Real data proves this false for a wide instruction set. 69
    `typesweep_<instr>_<type>_n01000` real captures (1000 rungs each,
    `error_count=0` throughout) across ADD/SUB/MUL/DIV/MOD/EQU/GEQ/GRT/
    LEQ/LES/NEQ/MOV/LIM/CPT × DINT/LINT/SINT/INT/REAL/STRING give a
    completely clean, exactly-linear-per-1000-rungs picture:
    - **LINT behaves identically to DINT in every case** (exact byte-for-
      byte match across all 14 instructions) — no separate LINT modeling
      needed, can treat as DINT going forward.
    - **REAL** costs the same as DINT for DIV/MOD/MUL/EQU/NEQ (0 delta),
      but *more* for ADD/SUB (+16/rung), GEQ/GRT/LEQ/LES (+16/rung),
      MOV (+24/rung), CPT (+56/rung) — and *less* for LIM (-8/rung,
      REAL LIM is actually cheaper than DINT LIM).
    - **SINT** costs substantially more than DINT for every instruction
      tested: +132/rung for the arithmetic group (ADD/SUB/DIV/MOD/MUL,
      identical delta across all 5), +88/rung for the comparison group
      (EQU/GEQ/GRT/LEQ/LES/NEQ, identical delta across all 6), +92/rung
      for MOV, +128/rung for LIM.
    - **INT** costs even more than SINT (counter-intuitive — INT is the
      *larger* of the two, 2 bytes vs SINT's 1): +156/rung arithmetic,
      +112/rung comparison, +104/rung MOV, +164/rung LIM.
    - **STRING** (only EQU/NEQ tested, the only two that accept it):
      +52/rung for both.
    Every delta above is a clean, exact multiple of the 1000-rung count
    (e.g. ADD/SINT: 193592-61592=132000, exactly 132.000/rung, not
    131.7ish) — this is not a fitted approximation, these are exact
    per-instruction-type deltas sitting in the manifest right now,
    completely unmined until this pass. Working hypothesis (unconfirmed,
    needs corpus/Rockwell-doc verification before treating as fact): non-
    DINT/LINT/REAL operands in these instructions trigger an implicit
    type-conversion/promotion step at compile time that the L5X text
    doesn't show, and that promotion is itself sized — consistent with
    controls-engineer field knowledge that Logix's execution engine is
    fundamentally DINT/REAL-native and other integer types are a display/
    entry convenience over the same underlying math.
    **Why this is NOT wired yet, deliberately:** every currently-CONFIRMED
    instruction weight in the coverage table implicitly assumes DINT
    operands, because that's what nearly every real sweep used. This
    finding means those weights are only correct when a tag actually IS
    DINT/LINT/REAL — a real program's SINT/INT-typed math tags (common:
    legacy scaled values, small counters) will be systematically
    UNDER-predicted by as much as 150+ blocks/rung today. Wiring this
    correctly requires the logic parser to resolve each rung's operand
    tag(s) back to their declared DataType (it currently only counts
    instruction occurrences, it doesn't cross-reference operand tags
    against the tag table) — a real parser capability that doesn't exist
    yet, not a one-line constant change. This is very likely the single
    largest unmodeled source of logic-size error in the current engine;
    flagged here as the top priority for the next architecture pass on
    the logic sizing engine, ahead of any more instruction-weight capture
    work on the remaining CAPTURED-preliminary instructions.

15. **OQ-JSRPARAMCOST (new, found 2026-08-25 mining already-captured data,
    NOT wired — needs parser architecture work).** JSR is currently
    CONFIRMED at a flat 72 blocks/rung, but that weight was fit against a
    JSR call with a small/fixed parameter count. `jsr_paramcount_n01/n05/
    n10_r01000` (1000-rung JSR calls passing 1/5/10 parameters each) show
    a real, additional, roughly-linear-in-param-count cost NOT explained
    by the flat 72/rung weight or by the separate tag-sizing pass (which
    already correctly sizes the extra parameter tags themselves): n01 gap
    +20044, n05 gap +104044, n10 gap +204044 over the flat-weight
    baseline. Per-parameter marginal cost from n01→n05 (4 extra params):
    (104044-20044)/4/1000 ≈ 21/param/rung; from n05→n10 (5 extra params):
    (204044-104044)/5/1000 ≈ 20/param/rung — close to a consistent ~20-21
    blocks/rung/parameter, though not yet confirmed clean-linear the way
    OQ-OPERANDTYPE's deltas are (only 3 count points, not evenly spaced,
    and the n01 intercept doesn't cleanly back out a 0-param baseline from
    just these three). `jsr_mixedio_5in_2out_r01000` (real gap +143992,
    i.e. ~144/rung above the flat weight for 7 total params) is roughly
    consistent with the ~20/param estimate (7×20=140, close). **Why not
    wired:** same root cause as OQ-OPERANDTYPE — the logic parser
    currently counts JSR occurrences, it doesn't parse the JSR call's own
    parameter list length out of the rung Text. Needs that parsing
    capability plus at least one more count point (e.g. n=2, n=3) to
    firm up the per-param constant before treating ~20/param as confirmed
    rather than approximate.

16. **OQ-CAPTURERACE (new, 2026-08-25, James: "flag results that stand out
    and might need retesting, I don't want to go forward with you assuming
    10 bools is the same size as 100 bools").** Full manifest sweep for
    count-invariant results (same `actual_bytes` across meaningfully
    different counts/sizes within one file family). Two categories came
    back:

    **Legitimate, no retest needed:**
    - `boolarray_n00008/n00016/n00032` all = 18224 — correct, real BOOL
      array packing (32 bits/packed word means 8/16/32 elements all fit in
      1 word). Already confirmed via `n00100`/`n01000`/`n05000` scaling
      correctly from there (RESOLVED_QUESTIONS.md OQ-BOOLARRAY). Not what
      James's "10 vs 100 bools" concern was — a *standalone* BOOL-array
      tag genuinely doesn't grow until you cross a 32-bit boundary. (A
      hidden 1000-element BOOL array, the actual memory-hog scenario the
      tool exists to catch, is fully covered by the n01000/n05000 points.)
    - `motioninstr_ma{m,j,s}_n00010` = `_n00100` (all = 42112, both counts)
      — correct: `error_count == rung_count` for both (100% build
      failure, see OQ-MAMFAMILY-BUILDFAIL/RESOLVED_QUESTIONS.md OQ-MAHMSO)
      — none of the rungs compiled, so Capacity reflects only scaffolding
      regardless of attempted rung count. Contrast MAH (same family,
      works): 42712 → 48112 across the same 10→100 sweep, scales exactly
      as expected. The flatness itself is evidence the build genuinely
      failed, not a capture bug.

    **Real capture-integrity problem, NEEDS RETEST — 6 rows, all
    self-flagged by James's own AHK/PowerShell tooling's window-title
    check (`notes` column, "WINDOW TITLE MISMATCH"):**
    - `array_dint_00001`, `array_dint_00002`, `array_dint_00005` — all
      three show identical `actual_bytes=18240` despite the L5X files on
      disk correctly declaring `Dimensions="1"`, `"2"`, `"5"` respectively
      (verified directly against the generated files — not a generator
      bug). `array_dint_00005`'s own note shows the capture window
      actually read was titled `array_dint_00002`'s project — a stale/
      previous-window race. The clean part of the same sweep
      (`n00010` through `n05000`) scales perfectly linearly at 4
      bytes/element with 0 residual, so this is isolated to the n=1/2/5
      tail, not a systemic array-sizing problem.
    - `paramcount_n04_def_only` (=`paramcount_n02_def_only`'s value,
      19360, note explicitly says the captured window was titled
      "ParamCountN02") and `paramcount_n08_def_only` (note says the
      window read was titled "ParamCountN04", though its own value,
      19392, doesn't exactly match n04's 19360 either — ambiguous, still
      needs a clean recapture rather than assuming it's fine). This is
      the same AOI-definition-cost sweep already carrying a DATA QUALITY
      WARNING for a different reason (OQ-AOIDEF's 7-way-identical-value
      contamination) — this off-by-one window race looks like the same
      underlying automation issue (the capture tool reading Capacity
      before the newly-opened project's window has taken focus/finished
      loading), not a new, separate bug.
    - `udttagcomment_len000` — note says the window actually read was
      titled "Snap Assist" (a Windows overlay, not Logix Designer at
      all). Its `actual_bytes=18416` is almost certainly not a real
      Capacity reading and should be treated as garbage, not just
      suspect.

    **Recommendation for James's capture tooling, not a code change here:**
    all 6 rows share the same signature — the AHK/PowerShell pipeline
    captured a value before the target project's window had actually
    taken focus (previous window, in one case a Windows Snap Assist
    overlay). Given this has now surfaced independently at least 3 times
    across different sweeps (this batch, plus the earlier `*_def_only`
    AOI contamination), a settle/focus-confirm delay before reading the
    Capacity value in the capture script would likely prevent recurrence.

    **Action:** these 6 sample_ids (plus, out of caution, `paramcount_
    n08_def_only`'s neighbor `n16`/`n32` should be spot-checked too since
    the race could plausibly cascade) need a clean recapture. Flagging for
    inclusion in the next test batch rather than silently trusting the
    current values — none of the derived constants in this repo currently
    depend on these 6 rows specifically (array-of-DINT and AOI param-count
    are both already confirmed from their clean data points), so this is
    a data-integrity flag, not a currently-wrong wired constant.
