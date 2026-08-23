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

   Once these 36 build clean and capture real Capacity data, the SECOND
   pass (James: "once we have all valid data for all instructions then we
   can do the 5/10 usage per file for each") is the natural follow-up —
   not started yet, intentionally, per James's explicit sequencing.

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

3. **OQ-AXISDEEP [test built].** CIP/virtual axis, used everywhere in real
   programs, 0.01%-tolerance target. `gen_axis_composite.py` covers the
   `ts_CIPAxis`-shaped composite UDT + AOI-with-InOut-axis call + full
   combo. Awaiting capture. **Partially resolved 2026-08-23** — the pure
   predefined-structure constants (AXIS_CIP_DRIVE, AXIS_SERVO, AXIS_VIRTUAL,
   COORDINATE_SYSTEM, MOTION_GROUP) are now derived and wired in, see
   RESOLVED_QUESTIONS.md OQ-PREDEFINED. What's still open here specifically
   is the *composite* case — a UDT/AOI that embeds an axis as a member
   alongside other stuff, not a standalone axis tag — still awaiting its
   own capture to confirm no extra interaction cost.

4. **OQ-MIXEDUDT [test built].** Realistic messy/nested UDTs (not
   homogeneous arrays) — `gen_axis_composite.py`'s composite UDT covers
   this too. Awaiting capture.

5. **OQ-ARRAYPACK [test built].** Does a UDT's total size round to a 32-bit
   boundary? `gen_arraypack_boolarray.py` group C. Awaiting capture. See
   also OQ-UDTARRAYALIGN below — the odd-byte-count case below is this
   same question, partially answered.

6. **OQ-ALIASSIZE [test built].** Alias tag cost at 1/10/1000 scale.
   `gen_tagscope_alias.py` group B. Awaiting capture.

7. **OQ-CMPCPTLAYOUT [test built, new 2026-08-22, extended same day,
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

8. **OQ-AOIDEF (new, 2026-08-23, MAJOR — real cost currently modeled as
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

9. **OQ-PREDEFINED, remaining piece [test built].** MOTION_INSTRUCTION,
   AXIS_CIP_DRIVE/AXIS_SERVO/AXIS_VIRTUAL/COORDINATE_SYSTEM, and
   MOTION_GROUP are now derived and wired in (see RESOLVED_QUESTIONS.md
   OQ-PREDEFINED). What's still open: `CAM` (the drive/cam-instruction
   wrapper, not `CAM_PROFILE` the array structure, which IS resolved) is
   still untested. Awaiting capture.

10. **OQ-XPROGREF [test built].** Real Logix has no direct cross-program
    tag-addressing syntax in logic (confirmed: searched all 47 real corpus
    files, no `Program:Tag`-style reference exists anywhere in rung Text).
    The real mechanism is what you described earlier — a Controller-scoped
    global with each program declaring its own Local alias to it. Built
    `gen_xprogref.py`: single-program alias baseline vs two programs each
    aliasing the same global, same 1000-rung XIC/OTE pattern, comparable
    directly against the confirmed 20-blocks/rung XIC weight. Needed a new
    `build_l5x(extra_programs_xml=...)` wrapper hook for a second Program.
    Awaiting capture.

11. **Motion instructions [test built]** (MAM/MAJ/MAH/MAS/MSO/MRP).
    `gen_motion_instructions.py` — MAH/MSO's 2-operand call syntax is
    corpus-confirmed, the rest use the same documented signature but
    aren't independently confirmed for that exact mnemonic. MAPC/MCCP
    camming skipped, no real call-syntax reference found. **2026-08-23:**
    MAH/MSO's real per-rung logic weight is now derivable (60 blocks/rung,
    from `motioninstr_mah_n00010`/`n00100` once AXIS_CIP_DRIVE+
    MOTION_GROUP+MOTION_INSTRUCTION were known) but NOT yet wired into
    `logic_instructions.weights` in memory_model.yaml — still needs that
    one-line addition next session. MAM/MAJ/MAS/MRP remain untested.

12. **Per-Task overhead [test built].** `gen_task_overhead.py` — 2nd/3rd
    Task, isolating pure Task/Program scaffolding cost from logic content.
    Also the only way to disambiguate whether the logic-sizing engine's
    `fixed_base_per_routine` is really per-routine, per-program, or
    per-task (every calibration sample had exactly one of each). Awaiting
    capture.

13. **Indirect addressing overhead [test built, extended 2026-08-22].**
    `gen_indirect_addressing.py` — direct vs. tag-driven array index, plus
    (James: "Does tag[idx+1] take up the same space as tag[Idx]?") a third
    variant with an arithmetic offset inside the index. Same
    instruction/count throughout. **2026-08-23 rebase-check note:**
    `indirect_direct_index_n01000` (1000 rungs) now shows only a 4-block
    gap against the current engine, i.e. already effectively explained by
    the existing indexed-array-tag handling — no separate direct-vs-
    indirect cost found. The arithmetic-offset (`tag[idx+1]`) variant is
    still untested; leaving this open for that specifically.
