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

   **2026-08-25, x10 captures landed, 34 of 36 RESOLVED and WIRED.** Every
   `weight = (actual_x10 - actual_n1) / 9` for the 34 non-CROUT/MAPC
   instructions came back an exact integer — same 0.00%-residual standard
   as every other confirmed weight, nothing "came out of line" for any of
   the 34. All 34 wired into `logic_instructions.weights`
   (RESOLVED_QUESTIONS.md OQ-INSTRFIRSTPASS-X10 has the full derivation).
   **CROUT and MAPC did NOT resolve — real build failures**, see
   OQ-CROUT-MAPC-BUILDFAIL below, not guessed into the weight table.
   MCCP/MSG resolved for their LOGIC weight specifically (204/48,
   confirmed clean-build exact fits) but their CAM/MESSAGE tag operand's
   own data-space cost remains unmodeled (item 8 below) — a real program
   using MCCP/MSG will still show a partial SizeError for that tag until
   that's resolved, the logic-side number is correct on its own now.

   Once the THIRD pass (James: "once we have all valid data for all
   instructions then we can do the 5/10 usage per file for each" —
   per-file instance/call-site multiplicity, not rung count) is needed for
   any instruction, it's the natural follow-up — not started, per James's
   explicit sequencing (wait for a name reason to suspect the flat-rate
   assumption before spending a batch on it).

1b. **OQ-CROUT-MAPC-BUILDFAIL — CROUT RESOLVED (out of scope), MAPC still
    open, ACTIVE PRIORITY per James.** CROUT and MAPC were the two
    NEAR_VERBATIM (near-literal corpus transplant, not independently
    understood operand-by-operand) shapes flagged as needing extra
    scrutiny in OQ-INSTRFIRSTPASS above — and that scrutiny paid off: both
    real x10 captures show genuine build failures (`instrfirst_crout_x10`:
    error_count=80 for 10 rungs, `instrfirst_mapc_x10`: error_count=20 for
    10 rungs), and `actual_bytes` is flat between n=1 and x10 for both
    (21160/21160 for CROUT, 20904/20904 for MAPC) — consistent with
    nothing new actually compiling.

    **CROUT — resolved 2026-08-25, James: "Crout is safety... requires a
    safety plc cpu."** The build failure isn't a bad corpus transplant —
    it's a Safety-only instruction, and this project's test corpus is all
    standard (non-GuardLogix) controllers. Moved to OUT OF SCOPE alongside
    DCS (`docs/INSTRUCTION_COVERAGE.md`), same as `docs/PROJECT_PLAN.md`
    Phase 6's existing Safety-scope-decision item. Nothing to fix, nothing
    to retest on a standard controller.

    **MAPC — James: "100% needed instruction that needs 100% accuracy...
    Review existing programs to get accurate logic programming, paying
    attention to data types and sizes used."** Not a defer item. Real
    corpus review in progress (`samples/local/L5X_Samples/
    Griffin_StackerLine_1Mar25_r00.L5X`, the source of the original
    `instrfirst_mapc` operand shape) — see the dedicated write-up below
    for what that review found and what's still needed before another
    generation attempt. Do not guess a fix; needs a corrected operand
    shape verified against the real file, not another simplification.

1b-i. **OQ-MAPC-COMPAT — MAPC real corpus research, 2026-08-25 [test built,
    awaiting capture].** Read `samples/local/L5X_Samples/Griffin_
    StackerLine_1Mar25_r00.L5X` directly (8 independent real MAPC calls
    found, not just the one already cited) instead of trusting the
    original transplant. Two real, verified bugs found in
    `instrfirst_mapc`/`instrfirst_mapc_x10` (not guessed — both confirmed
    by reading the generator source and the real corpus tag declarations):

    1. **Axis_Cip_Drive was never declared as a tag in that file at all.**
       `group_cam_family`'s MAPC call passed `extra_tags_xml=cam_tag`
       only — never `_AXIS_TAG_XML` (the constant that actually declares
       the `Axis_Cip_Drive` tag). Every rung referencing an undeclared tag
       is a real, sufficient-on-its-own explanation for the 20 errors/10
       rungs seen — no need to look further than this for the *fact* of a
       build failure, though the second bug is also real and independently
       wrong.
    2. **Real corpus MAPC calls never reuse the same axis tag for both
       slave/master.** All 8 real calls found use two DISTINCT axis tags.
       The specific example this file was transplanted from
       (`Stacker.ForksUpDn.MAPC`) uses `EM304_ForksUpDn` (verified
       `DataType="AXIS_CIP_DRIVE"`, a real physical axis) for the slave
       position and `VM305_StackerVirtual` (verified
       `DataType="AXIS_VIRTUAL"`) for the master position. **James,
       2026-08-25, confirmed the real rule: "Mapc can use two axis of any
       type (virtual master/virtual slave is ok)"** — the requirement is
       just two DISTINCT tags, not a required CIP-Drive/Virtual pairing.
       The 8 corpus examples happening to show that specific pairing was
       real corpus data, not a wrong over-generalization, but James's
       confirmation is the actual rule — virtual/virtual (and presumably
       CIP-Drive/CIP-Drive) are equally valid, only same-tag-reused is
       wrong.

    Every real MAPC call found (all 8) has the exact same **14-operand**
    shape: `MAPC(slave_axis, master_axis, motion_instruction_tag, 0,
    cam_profile_array[0], 1, 1, <execution_keyword>, <direction_keyword>,
    <master_ref_1>, <master_ref_2>, "New Cam", <keyword>, <keyword>)` —
    operand count is invariant across all 8 real examples despite
    different Execution/Direction keyword combinations (Persistent/
    Immediate, Continuous/Immediate, Once/Forward Only all seen), which is
    itself useful confirmation that 14 is the real fixed arity, not
    dependent on which keywords are chosen.

    **Fix built and wired 2026-08-25:** `gen_axis_composite.py` gained a
    new `_AXIS_VIRTUAL_TAG_XML` constant (near-verbatim from the real
    corpus's `VM305_StackerVirtual`/`VM308_PeelersVirtual` tags, sharing
    the existing `MotionGroup` tag rather than duplicating it).
    `gen_instruction_firstpass.py` gained `group_mapc_v2`, a
    position-for-position transplant of the exact real
    `Stacker.ForksUpDn.MAPC(...)` call (same operand sequence, same
    keywords) with both bugs fixed — `Axis_Cip_Drive` now actually
    declared, and slave/master are genuinely distinct
    `Axis_Cip_Drive`/`Axis_Virtual` tags. Original buggy
    `instrfirst_mapc`/`_x10` files kept (not deleted) as the audit trail,
    now explicitly labeled BUGGY in their manifest description.
    `instrfirst_mapc_v2`/`_v2_x10` generated, lint-clean, awaiting
    capture. Given James's "100% accuracy" priority on MAPC specifically,
    this should go in the very next capture batch, not wait.

    **RESOLVED 2026-08-25, real capture landed same day: both fixes
    confirmed correct.** `instrfirst_mapc_v2` (n=1) and `_v2_x10` (n=10)
    both built `error_count=0` — the corrected 14-operand two-distinct-
    axis-tags shape is real and clean. Marginal logic weight: (64288-
    61948)/9 = exactly **260/rung**, a clean 2-point linear fit, same
    confidence tier as MAH/MSO's confirmation. **Wired in
    memory_model.yaml: `MAPC: 260`.** The AXIS_CIP_DRIVE/AXIS_VIRTUAL
    tags' own data-space cost is still separately unmodeled
    (OQ-PREDEFINED) — this is the LOGIC weight only, but it closes the
    "100% needed instruction" gap for the instruction's own compiled cost.

1c. **OQ-INSTRFIRSTPASS-FLATOFFSET (new, minor, 2026-08-25).** All 32
    "clean" `instrfirst_*`/`instrfirst_*_x10` pairs (everything except
    MCCP/MSG, which have their own separate known-unmodeled-structure gap)
    show an identical flat **+6 byte** gap at BOTH n=1 and n=10 — meaning
    it doesn't scale with rung count, so it didn't affect any of the 34
    confirmed logic weights above (the marginal-delta derivation method is
    immune to a fixed per-file offset). Real, consistent across all 32
    independent files, but small (~0.03% of a ~20,800-byte total) and not
    yet root-caused — likely something in the shared tag pool these files
    declare (D0/D1, R0/R1, B0/B1, Str0/Str1, Arr0/Arr1, Ctrl0, etc.) that's
    off by a flat 6 bytes. Low priority; flagged so it isn't silently
    absorbed into some other constant later.

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

   **2026-08-25, James: "i did not see your results from the different
   processor catalog/firmware numbers -- what were your determinations
   on that... what other tests do you need me to generate for that
   stuff?"** Status check confirmed: **no real Capacity data has come
   back for any of the 29 staged files** — they're sitting in
   `samples/local/fw_versions/` exactly as staged 2026-08-24, no capture
   results attached anywhere (checked for a companion results file, none
   exists). There's nothing to report a determination on yet because the
   data was never captured, not because it was captured and sat
   unanalyzed. **All 3 of James's specific questions are already directly
   answerable from this same 29-file batch once captured, no new files
   needed right now:**
   - *"Does an M motion processor have more overhead?"* — the
     `v35_l306er`/`l306erm`/`l306ers2`/`l306erms2`/`l306erms3` 5-way set
     (base vs M vs S vs M+S vs M+S-rev3, same catalog/memory tier) is
     built exactly for this.
   - *"Does L81 vs L16 have different overhead?"* — confirmed all three
     platform families in the batch share the identical firmware
     `SoftwareRevision="35.05"` (`l81_v35`, `v35_l16er`,
     `v35_l306er`) — a clean apples-to-apples cross-platform (1756
     ControlLogix vs 1769 CompactLogix vs 5069 CompactLogix) comparison
     is already possible from files already staged, not something that
     needs a new generation batch.
   - Firmware-revision sensitivity on one catalog (`l81_v30` through
     `l81_v38`, 7 points) is also already staged.
   **What's actually needed next is the capture itself**, not more
   files: open each of the 29 in Studio 5000, record catalog/firmware/
   Capacity-tab bytes the same way every other sample gets captured.

   **2026-08-25, James (annoyed, rightly): "i expect you to generate
   those processor/firmware files for the next batch of testing. the
   purpose of me giving you those files was for you to update your
   reserved overhead sizing based on the processor and firmware."**
   Corrected: all 29 files are now real rows in `samples/manifest.csv`
   (category `fw_baseline`, `l5x_path` pointing at their real
   `samples/local/fw_versions/` location, `controller_model`/
   `firmware_rev` pre-filled from each file's own XML, `predicted_bytes`
   =13,296 confirming the engine currently predicts the same flat number
   for all 29 regardless of processor/firmware — exactly the gap this
   question is about). Previously these were sitting in `samples/local/`
   with no manifest entry at all — outside the normal batch-tracking flow
   every other real capture goes through, which is why they read as
   invisible/forgotten. `actual_bytes` for all 29 stays blank, ready for
   capture, same as every other pending row in the manifest.

   **2026-08-26, real tooling risk found for THIS batch specifically (see
   OQ-STRINGCONSTFAIL for the full derivation).** Studio 5000's
   same-instance "switch file via Ctrl+O without closing" batch-capture
   flow throws a real error (`Name collision: imported Module 'Local'
   renamed to 'Local1'` → `Required property 'Port' was missing`) the
   first time consecutive files have a DIFFERENT processor identity —
   confirmed by James pasting the actual import output for a similar
   L8/5069-switching batch. Every prior capture in this project's history
   kept the same processor between consecutive files, so this never
   surfaced before. **This batch is 29 files that ALL vary
   processor/firmware by design** — if captured via the same fast
   same-instance switch flow used for everything else, expect this
   collision on every processor change, not just occasionally. Likely
   needs a full Studio 5000 close/reopen (not just Ctrl+O) specifically
   when the processor type changes between consecutive files in this
   batch — a capture-tooling change, not an L5X-generation one.

   **2026-08-27, FIRST REAL DATA POINT LANDED — confirms the whole
   concern, real and dramatic.** James: "l81_v30.l5x failed as the SDK
   didnt support v30 files - please manually add as 29272 blocks used."
   `l81_v30` (1756-L81E, firmware 30.02) — `l5xgit`'s SDK doesn't support
   v30 firmware at all, so this file can never go through the normal
   L5X→ACD→AHK-capture pipeline; James read the real Capacity number
   directly and reported it for manual entry. Real actual = **29,272**
   against this engine's flat prediction of 13,296 (every file in this
   whole project assumes 1756-L81E/35.05's baseline) — a **+15,976
   (+120.16%) gap**, by far the largest miss this project has ever
   recorded for ANY category, single-handedly confirming James's original
   2026-08-23 warning was not theoretical. Manually entered in
   `manifest.csv` (`notes` flagged `MANUAL ENTRY`, `error_count`/
   `warning_count`/etc. left blank since there was no AHK capture cycle
   for this row — a real, deliberate exception to the normal capture
   convention, not a data-quality gap). **Still only 1 real point** — not
   enough to fit a (processor, firmware) formula yet, and this single
   point can't tell "firmware 30.02 specifically" apart from "the SDK's
   inability to build v30 at all reflects some OTHER real difference
   about that firmware" — but it's now proven this axis is real and
   large, not a minor correction. The other 28 staged `fw_baseline` files
   remain awaiting capture (7 more `l81_v3x` firmware points on the same
   catalog would be the fastest way to see whether the gap trends with
   firmware version or is specific to v30).

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

   **2026-08-25, James: "whats your CPT confidence? why is it not 100%
   yet? you need to generate tests to satisfy this."** Mined the 27
   already-captured `cmpcpt_*` rows (all real, all `error_count=0`,
   nothing sitting unanalyzed) via direct subtraction between file
   variants sharing the exact same tag pool — real, clean findings, but
   every one is anchored on a SINGLE rung count (1000), so none of them
   are confirmed linear yet:
   - **Operator tiers, computed relative to a `CPT(L2,L0)` bare-copy
     baseline (106,904 @ n=1000), tag operands throughout:** ADD and SUB
     cost the same (+36,000 = +36/rung if linear), MUL and DIV cost the
     same (+52,000 = +52/rung if linear), POW is its own, more expensive
     tier (+116,000 = +116/rung if linear). All 3 tiers land on clean
     multiples of 4, internally consistent (ADD==SUB exactly, MUL==DIV
     exactly) — a real signal, not noise, but still just one count point
     each.
   - **6-operand chain** (`CPT(L7,L0+L1+L2+L3+L4+L5)`, 238,904 @ n=1000)
     costs +96,000 over the 2-operand ADD baseline — a real per-extra-
     operand signal, but only one chain length tested, can't separate a
     per-operand rate from some other shape yet.
   - **No redundant-expression optimization found:** `CPT(L2,L0+0)`
     (mathematically redundant +0) and `CPT(L2,L0+L0)` (same tag used
     twice) both cost EXACTLY the same as the plain 2-distinct-tag ADD
     case (142,904 each) — Rockwell's compiler doesn't special-case
     either of these, real negative result, not untested.
   - **Operand TYPE (tag vs int-literal vs float-literal) interacts with
     CPT's cost in a way that is NOT simply additive with the operator
     tiers above, and is itself under-tested:** every int-literal variant
     (`CPT(L2,L0+5)` etc.) costs exactly **+264** more than its tag-
     operand counterpart, identically across all 5 operators — looks like
     a one-time cost (e.g. a per-distinct-literal-value table entry) sitting
     underneath the per-rung rate, not another per-rung addition, but
     that's a hypothesis from a single count point, not confirmed. Float-
     literal variants are stranger still: ADD/SUB/MUL/DIV-with-a-float-
     literal all land on the exact same 187,168, independent of which
     operator is used, but POW-with-a-float-literal doesn't (195,168) —
     operand type appears to partially or fully override the operator-tier
     effect for float literals specifically. Not understood mechanistically
     yet, flagged rather than guessed at.
   - **Compound CMP conditions build clean now** (`cmp_and_compound`/
     `_or_compound`/`_duplicate_cond`, all `error_count=0`) — the earlier
     2026-08-22 100%-build-failure note above is stale, superseded by this
     later, corrected batch. All 3 compound shapes land on the exact same
     175,168, suggesting AND vs OR vs a duplicated condition cost the same
     real amount — again only one count point.

   **Honest confidence: moderate on the numbers being real, low on having
   a complete formula.** CPT is a general expression evaluator (arbitrary
   operand count/type/operator/nesting) — "100% accuracy" here means
   covering a genuinely combinatorial space, not a single fix. What's
   missing before any of this can be wired: a second rung-count point for
   each tier (to confirm +36/+52/+116 are truly linear, not just flat-
   looking at n=1000) and a dedicated operand-type sweep (to actually
   separate the literal-vs-tag effect from the operator-tier effect
   instead of eyeballing it from 10 rows). **Generated 2026-08-25,
   `gen_cpt_confirm.py`:** a second count point (n=100) for barecopy/ADD/
   MUL/POW, same tag pool as the original sweep, isolates exactly the
   rung-count-linearity question — 4 files, lint-clean, awaiting capture.
   The operand-type-vs-operator interaction is a separate follow-up, not
   attempted in this batch to keep it focused on one question at a time.

   **2026-08-25, James: "you need to put priority on getting this CPT
   working... I expect the next batch of generated tests that you will
   have this 100% solved. no exceptions. CPT is very important. confirm
   you understand this." Understood — confirmed.** Built
   `gen_cpt_comprehensive.py`, 24 files, all lint-clean, all reusing the
   exact `_POOL_TAGS_XML` so every one subtracts cleanly against the
   existing real data:
   - **MOD operator, 3 count points (10/100/1000).** Found this turn via
     `docs/CMP_CPT_REFERENCE.md`: MOD is used **146 times** in the real
     corpus — a bigger real-usage gap than POW (13 uses, already tested)
     and the single largest untested CPT operator. Real syntax confirmed
     from corpus (`Wrk_Now.Yr MOD 100`, `(Wrk_Now.Mo+9)MOD 12`) — word
     operator, used `L0 MOD L1` here. Gets 3 count points from the start
     instead of being bolted on with only 1.
   - **SUB/DIV n=100 completion** — `gen_cpt_confirm.py` only added n=100
     for barecopy/ADD/MUL/POW, leaving the ADD=SUB and MUL=DIV tier-match
     assumption unconfirmed at a 2nd point for SUB/DIV specifically. Added.
   - **n=10 third count point** for barecopy + all 5 operators (6 files) —
     every tier previously had at most 2 points (100, 1000); 2 points fit
     a line trivially, 3 actually tests linearity.
   - **Chain length sweep**, n=1000, operand counts 3/4/5/8/10 (5 files) —
     the existing 6-operand-chain finding (+96,000 over 2-op ADD) was a
     single data point with no way to separate a per-operand rate from
     some other shape. Chains past the 8-tag pool (L7 reserved as dest)
     recycle earlier tags — already confirmed harmless via the same-tag-
     twice dedup finding above (costs identically to a distinct tag).
   - **Literal-linearity**, int- and float-literal ADD at n=10/n=100 (4
     files) — confirms whether the mined +264 flat int-literal delta and
     the float-literal operator-(non-)independence are genuine per-rung-
     independent effects or single-count-point artifacts.
   - **Compound CMP n=100** for single/and/or/duplicate_cond (4 files) —
     2nd count point matching the existing n=1000 set.

   Still explicitly NOT attempted in this batch (flagged, not silently
   dropped): ABS()/ATN()/TAN()/SQR() (single-digit real usage each, lowest
   priority), nested/parenthesized mixed-operator expressions beyond the
   flat chain (e.g. `(L0+L1)*L2`), and CMP-vs-CPT cost divergence beyond
   what's already covered. Once this batch's captures land, CPT should
   have real multi-point data for every operator that matters by real
   usage frequency except those four near-zero-use functions.

   **RESOLVED (uniform case) / STILL OPEN (mixed case), 2026-08-26 — real
   expression parser built and wired, per James's explicit top priority.**
   `parser/logic.py` now extracts every real `CPT(...)` call's operator
   tokens (a real balanced-paren scan, handles nested parens correctly —
   not a naive regex to the first `)`); `sizing/logic.py`/
   `CptExpressionModel` costs each call individually. The old flat-wrong
   `CPT: 452` weight is REMOVED from `logic_instructions.weights` entirely.

   Derivation, all via the clean n=10/n=100 method (see the large-file
   anomaly note below for why NOT n=1000):
   - `base_read` = 88 (bare `CPT(dest,tag)`, no operator).
   - `operator_tier_costs`: ADD/SUB=36, MUL/DIV/MOD=52, POW=116 — each
     confirmed flat at both n=10 and n=100, zero residual.
   - `per_extra_same_tier_operand` = 24 — from the n=1
     `cptcx_operandcount_n01..n10` sweep (single ADD chain, 1-10
     operands): the 2nd operand costs the full tier rate (36), every
     operand after that costs a flat 24. Cross-checked against the
     SEPARATE n=1000 chain-length sweep (chain3/4/5/6/8/10): predicts
     chain3/4/5/8/10 with ZERO residual; chain6 alone shows the -264
     anomaly below, not a formula error.
   - **Literal operands cost the SAME as tag operands** for integer
     literals — confirmed byte-identical at n=10 and n=100
     (`op_add_intliteral` vs `op_add`). The earlier "+264 for a literal
     operand" note higher up in this same entry was a MISDIAGNOSIS of the
     large-file anomaly below, not a real literal-operand effect —
     corrected here.
   - **The 264-block large-file anomaly recurs at n=1000** across
     barecopy/ADD/SUB/MUL/DIV/POW (NOT MOD, and NOT chain3/4/5/8/10, only
     chain6) — confirmed as exactly the gap between the clean
     n=10/n=100-implied linear rate and the real n=1000 value, every
     time. Still mechanistically unexplained, still small relative to
     file size, not chased further — same unexplained family already
     flagged elsewhere in this doc for other n=1000 file shapes.
   - **Mixed-tier expressions are NOT well-modeled** by the additive-sum
     fallback `cost_for()` uses when it sees more than one operator tier:
     off by only ~20 bytes/call on 2 simple 3-operator real test points
     (`cptcx_operatormix_mixedops`/`_nested`/`_powermix`), but off by
     ~150 bytes/call on a real, more complex corpus expression
     (`instr_cpt_n*`'s `(D0+D1)*R1-R2/2+1.5` — 5 operators across 3
     tiers, a literal divisor, a float literal, REAL-typed operands, all
     at once). That expression's real rate converges to ~452/rung at
     large n — almost certainly the exact expression the OLD flat-452
     constant was originally fit against, which is why the number just
     proven wrong as a GENERAL constant is still suspiciously close to
     correct for that one specific shape. Root cause not isolated (too
     many stacked unknowns in 3 data points) — deliberately NOT patched
     further tonight, to avoid repeating this session's earlier type-
     name-length overfitting mistake (fit-then-revert). **Needs a
     dedicated mixed-operator test batch**: a tier-pair sweep, a literal-
     position isolation, and a REAL-vs-DINT operand cross-check, before
     this branch earns the same trust the uniform case now has.

     **2026-08-26, that batch landed (James: "mix up to 15 operands per
     expression as needed, 100% solved closed").** 33 real files,
     `error_count=0` throughout. Real, substantial progress — one clean
     tier-pair now fully solved, several other real mechanisms
     characterized, none of it forced into a general formula it doesn't
     support:
     - **Operator ORDER confirmed irrelevant** — every tier-pair tested
       both orders (T1-first vs T2-first, e.g. `L0+L1*L2` vs
       `L0*L1+L2`) landed on the IDENTICAL byte count, for all 3 pairs
       (T1T2, T1T3, T2T3). Confirms the "bag of operators, not sequence"
       hypothesis fully, not just for the 2 shapes tested before.
     - **Literal presence/position confirmed irrelevant in mixed
       expressions too** — `cptmix_litpos_alltag_baseline`/
       `_literal_first`/`_literal_middle`/`_literal_last` (fixed 2-tier
       3-operand shape, literal substituted at each position in turn)
       all land on the exact same byte count. Extends the uniform case's
       int-literal finding cleanly to the mixed case.
     - **T1+T2 (ADD/SUB + MUL/DIV/MOD) alternating mix: SOLVED, clean
       formula.** The operand-count scaling sweep (3/5/8/11/15 operands,
       alternating tiers) fits `true_cost = 100 + 32*operator_count`
       **exactly at 4 of 5 points** (k=2,4,10,14 all zero residual; k=7
       off by -8, the same small universal noise pattern seen everywhere
       else in this project). Note this "32/operator" rate is a REAL,
       DIFFERENT number from the uniform case's 24/operator rate —
       alternating between two tiers costs more per operator than
       repeating the same tier. "Grouped" arrangement (all T1 operators
       then all T2, same operator bag, different order) matches
       "alternating" at 4/5 counts too (only n=5 shows a small 4-byte
       blip, noise). This is the first mixed-tier sub-case to reach the
       uniform case's level of confidence — ready to wire as a real,
       KNOWN-tier special case (when a CPT expression's operator set is
       exactly {T1, T2}), not deferred further.
     - **T1T3 and T2T3 pairs: real, but only single-point data.**
       2-operator T1T3 (`+`,`**`) = 288; 2-operator T2T3 (`*`,`**`) =
       288 (identical to each other, both real, both order-independent).
       No operand-count-scaling sweep exists for either pair yet (only
       T1T2 got that treatment) — cannot extrapolate a per-operator rate
       for these pairs the way T1T2's was solved. Needs its own Group-B-
       style count sweep before it can be wired.
     - **All-3-tier mixes (alternating +,*,**): real data, doesn't fit
       any simple linear-in-operator-count model tried.** n=3(k=2)=164
       (identical to the T1T2 2-operator case, as expected — the
       alternating pattern at k=2 only reaches tiers T1,T2), n=5(k=4)=448,
       n=8(k=7)=656, n=10(k=9)=784, n=15(k=14)=1152 (from the 15-operand
       group, see below). These don't fit `base+rate*k` cleanly the way
       the T1T2-only case did — plausible since the exact tier MIX
       shifts as k grows here (unlike T1T2's fixed 50/50 ratio
       throughout), a real 3-way interaction effect, not further
       decomposed from 4 points.
     - **REAL operand type in a mixed expression costs MORE than naively
       composing the separately-confirmed OQ-OPERANDTYPE surcharges
       predicts.** `cptmix_realcheck_dint`/`_real` (identical 2-tier
       3-operand shape, DINT vs REAL operands): the REAL version costs
       +40 more than DINT. Naively summing OQ-OPERANDTYPE's own ADD+REAL
       (+16) and MUL+REAL (+0) surcharges would predict +16. Real effect
       is 2.5x that — REAL operand type doesn't compose additively with
       mixed-tier CPT costs, a genuine unexplained interaction, not
       wired.
     - **Float-literal and REAL-operand costs stack SUB-additively, not
       additively.** `gen_cpt_mixed_operators.py`'s stacked-factors ladder
       finally isolates the ~150-byte/rung mystery from the original
       corpus expression `(D0+D1)*R1-R2/2+1.5`: against an all-DINT/no-
       literal baseline (true cost 252), a float literal ALONE (still all
       DINT operands) adds +244 (→496); REAL operands ALONE (no literal)
       add +236 (→488); but REAL operands AND a float literal TOGETHER
       (the original shape) add only +200 (→452 — matches this project's
       independently-derived ~452/rung finding for this exact expression
       from earlier in the session, a clean cross-validation). +244 and
       +236 stacked would predict +480 if additive; real combined cost is
       less than HALF that. A real, large, genuine interaction (plausibly
       a float literal's storage already overlaps with REAL-operand
       handling) — characterized, not reducible to independent additive
       terms from this data.
     - **Rung-count linearity for a large mixed expression: CONFIRMED.**
       `cptmix_fifteen_n00001` (single rung) and `_n00100` (100 identical
       rungs) both give exactly 160/rung for the same 15-operand 3-tier
       expression — resolves whether large/complex mixed expressions
       scale linearly with rung count at all (yes; the original corpus
       expression this whole investigation started from was previously
       only ever captured at n≥1000, so its own rung-count linearity was
       assumed, never actually confirmed until this cross-check).
     **Net effect on the additive-sum fallback**: still the right choice
     for tier combinations without their own solved formula (T1T3, T2T3,
     3-tier), still real and useful there, still honestly imprecise.
     **T1T2 wired same day** as a special case in `CptExpressionModel.
     cost_for` (`two_tier_mix_base=100, two_tier_mix_per_operator=32`),
     live-verified 15/18 real T1T2-family rows exact (3/18 within the
     usual small noise band). `gen_cpt_mixed_operators.py`'s new
     `group_t1t3_t2t3_scaling` (10 files, mirrors the T1T2 operand-count
     sweep exactly for the 2 remaining pairs) generated, lint-clean, in
     the manifest, awaiting capture — the direct next step to close the
     rest of the mixed-tier case the same way.
   - **CMP's own compound-boolean-condition formula was NOT touched** —
     while deriving this, `cmpcpt_cmp_single`'s real rate (~91.7/rung from
     n=100→n=1000) doesn't match the existing wired standalone `CMP: 76`
     weight. Whether these are the same real quantity measured two
     inconsistent ways, or genuinely different CMP usage shapes, is
     unresolved — its own follow-up, not rushed into tonight's fix.

   Verified against 24 real manifest rows (bare copy + all 6 operators at
   n=10/n=100/n=1000, all 6 chain lengths at n=1000, the n=1 operand-count
   sweep, the int-literal check) via a live end-to-end `build_report()`
   run against the actual generated `.L5X` files, not just unit-level
   formula checks — 22/24 exact, 2/24 showing the already-understood -264
   anomaly (not a formula defect). New tests in `tests/test_logic_sizing.py`
   cover the parser extraction and the cost formula directly.

7. **OQ-AOIDEF (new, 2026-08-23, MAJOR — real cost currently modeled as
   zero; DATA QUALITY WARNING added same day, see below before trusting
   any number in this entry). See `docs/AOI_KNOWLEDGE_MAP.md` for the full
   known/unknown breakdown across all AOI sizing questions, not just this
   one — built 2026-08-25 per James's request for a clear gameplan.**

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
   - **Param count — RE-CAPTURED CLEAN 2026-08-26, the n02==n04 collision
     is gone.** Live re-derived (recomputing against current code, not the
     stale `predicted_bytes` frozen in manifest.csv at old capture time):
     `paramcount_n01/02/04/08/16/32_def_only` now read 19336, 19360,
     19392, 19472, 19632, 19952 — six DISTINCT values, no more n02/n04 tie.
     Fits `1184 + 20*n` exactly for n=4/8/16/32 (n=1,2 sit slightly under,
     same small-N pattern as the local-tag sweep). **This is the identical
     formula as the local-tag-count fit above** (`19312+20n` there =
     `1184+20n` above baseline here) — param count and local-tag count
     now agree exactly, DINT-only, which is stronger evidence for that
     base+20/declared-item term than either axis alone gave. `_v2` retest
     (`paramcount_n04_def_only_v2`=19400, `paramcount_n08_def_only_v2`=
     19472) roughly confirms n04/n08 within the same few-block noise band.
     Still NOT wired — see the "deliberately not wired" reasoning below,
     which still holds: name-length, atomic-type-sensitivity, and BOOL-
     run/pack adjacency are all still open, and most real AOIs mix param
     types, so wiring only the now-doubly-confirmed DINT-count term would
     systematically underpredict any BOOL- or mixed-type-heavy AOI while
     looking EXACT-tier trustworthy.
   - **Required/Visible/Hidden flags — no effect beyond existing noise
     band, 2026-08-26.** `reqvis_allhidden/allrequired/allvisibleoptional/
     mixed_n4_def_only` (all 4 DINT Input params, same count, only the
     Required/Visible/Hidden flag combination varies): live deltas 1272,
     1272, 1288, 1256 vs the clean n=4 formula prediction of 1264 — all
     within ±24 blocks, the same order as the existing n=1/n=2 small-N
     noise already documented above, not a distinct step pattern. Read as
     "Required/Visible/Hidden doesn't materially change AOI definition
     cost" (consistent with the same flags' already-confirmed no-effect
     finding elsewhere in this doc for other contexts). The matching
     `_call_full` rows (same reqvis sweep but with a real instance + call,
     not `_def_only`) run 1516-1556 — roughly +260 over their `_def_only`
     counterparts, presumably the instance tag + call-site cost, not
     analyzed further here (new, small, flagged for later — the
     omitted-vs-wired optional-param call-site pair `reqvis_2req2optional_
     call_allwired` vs `_optomitted`, both 1516, at least confirms omitting
     an optional param at the call site doesn't change size, matching the
     AOI array-of-instances precedent for "unwired optional stuff is free").
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

   **2026-08-25, `gen_aoi_array_packing.py`'s 18 files captured — confirms
   the BOOL-specific hypothesis, resolves nothing yet (still NOT wired,
   need more data before committing to a formula).** Real per-array-
   element marginal rate (computed from adjacent count points within each
   shape, e.g. n=5→n=10, n=10→n=25):
   - **`aoipack_atomic_*` (zero BOOL, pure DINT/REAL):** ~124/instance —
     close to but consistently a little under the engine's own 128/
     instance assumption (deltas across the 4 intervals: -4, -4.8, -3.7,
     -4.2/instance — small, NOT perfectly linear, looks like ordinary
     small-residual noise riding on top of the still-open OQ-AOIDEF
     def-cost baseline error rather than a distinct new effect). Read as
     "engine's 128/instance for pure-atomic AOI arrays is already close
     to right" — no correction wired, the imprecision here is dominated
     by OQ-AOIDEF's unresolved baseline, not a new packing effect.
   - **`aoipack_bool_*` (all-BOOL, 30 members):** ~4/instance — dramatically
     smaller than the engine's 128/instance, but NOT cleanly linear either
     (4, 3.2, 4.27, 3.84/instance across the 4 intervals) — consistent
     with a genuine BIT-packing effect (like a plain BOOL array's 32-bit
     packed word) that only 5 count points (1/5/10/25/50, none crossing
     an obvious 32-element packing boundary cleanly) can't yet resolve
     into an exact formula. This clarifies — and partially CONTRADICTS —
     the "~50% discount, maybe BOOL packs 8-per-byte in arrays" hypothesis
     above: pure-BOOL AOI arrays cost far LESS than half, not roughly
     half. That "half" number turns out to belong to the MIXED shape,
     below, not the pure-BOOL one — conflating them earlier was itself an
     example of exactly the "don't assume 10 bools = 100 bools" trap.
   - **`aoipack_mixed_*` (15 BOOL + 15 non-BOOL, half and half):** exactly
     **64 bytes/instance**, and this one IS clean — all 4 intervals
     (n1→n5, n5→n10, n10→n25, n25→n50) independently compute to exactly
     64.0/instance, no rounding, no noise. This is the real number behind
     the original `RealisticAOI` 64-bytes/instance finding.

   **Still NOT wired, deliberately, even though `aoipack_mixed`'s 64 looks
   clean:** the underlying mechanism (does an array of AOI/UDT instances
   bit-pack BOOL members ACROSS array elements, the way a plain BOOL array
   packs 32 bits/word?) isn't understood well enough to write a general
   rule from 3 shapes at one fixed member-count/BOOL-ratio (30 members,
   50% BOOL) each. A real fix needs to model per-member packing across the
   array dimension specifically, which is a genuine parser/sizing-engine
   change (analogous in kind to OQ-OPERANDTYPE/OQ-JSRPARAMCOST — new
   capability, not a constant tweak), not a one-line correction. Wiring
   "64/instance whenever exactly half an AOI's members are BOOL" off this
   one ratio would be exactly the kind of premature generalization James
   flagged concern about. **Recommended follow-up data, when there's
   budget:** a few more BOOL:non-BOOL ratios (e.g. 1:29, 5:25, 25:5) at a
   couple of count points each, and — separately — count points that
   cross the 32-element BOOL-packing boundary (e.g. n=31/32/33/64/65) on
   the pure-BOOL shape specifically, to see if its marginal rate jumps at
   those boundaries the way a plain packed BOOL array's would.

8. **OQ-PREDEFINED, remaining piece — CAM/MESSAGE, mechanistic research
   done 2026-08-25, byte-size sweep still needed.** MOTION_INSTRUCTION,
   AXIS_CIP_DRIVE/AXIS_SERVO/AXIS_VIRTUAL/COORDINATE_SYSTEM, and
   MOTION_GROUP are now derived and wired in (see RESOLVED_QUESTIONS.md
   OQ-PREDEFINED). What's still open is `CAM` (the drive/cam-instruction
   wrapper struct, not `CAM_PROFILE` the array structure, which IS
   resolved) and `MESSAGE`. James, 2026-08-25: "You need to be more
   familiar with cam and MSG... know how they work, if more research is
   required." Neither had gotten more than a single real example read
   before now — actual research pass below, not just an n=1 byte capture.

   **CAM, read directly from `samples/local/L5X_Samples/
   RobbinsGrn_2026_05_13r00.L5X`.** Real shape (Decorated format) is
   exactly 3 fields per array element: `Master:REAL`, `Slave:REAL`,
   `SegmentType:DINT` — 12 raw bytes/element if nothing is hidden.
   **Important structural finding: unlike CAM_PROFILE, CAM's L5K format
   shows the SAME 3 numbers per element as the Decorated format** (`[0.0,
   0.0, 1], [200.0, 100.0, 0], ...`) — no extra hidden values. CAM_PROFILE,
   by contrast, has 14 real L5K values per element behind only 1 visible
   Decorated field (RESOLVED_QUESTIONS.md OQ-PREDEFINED's CAM_PROFILE
   entry) — a real, verified case of Rockwell hiding internal fields from
   the Decorated view. CAM shows no sign of that same hiding, which is a
   meaningfully different (and more encouraging) starting hypothesis for
   its byte cost: plausibly a clean `base + 12×count` rather than
   CAM_PROFILE's `base + 56×count`, though — consistent with this
   project's own rule — that's a hypothesis to test with a real count
   sweep, not something to wire from structural inspection alone. `cam_
   tag_xml()` in `builders.py` already reproduces this exact real 3-field
   shape (verified against RobbinsGrn's real Decorated AND L5K data, not
   just the earlier MCCP citation). Needs a real count sweep (e.g.
   1/5/10/20/50 CAM elements) before any byte formula is wired.

   **2026-08-26, sweep built (James: "touch these and finalize them
   now").** `gen_cam_sweep.py` -- 5 files, 1/5/10/20/50 CAM elements,
   `write_sample_unmodeled` (predicted_bytes=0, honest -- there's still no
   formula to predict with), lint-clean, in the manifest, awaiting
   capture. This is the concrete next step the entry above already named;
   nothing to analyze until real Capacity numbers land for these 5.

   **RESOLVED same day, real data landed and confirms the mechanistic
   prediction exactly.** All 5 points, `error_count=0`:
   `base(8) + per_element(12)`, KNOWN -- 2/5 points (n=1, n=5) exact zero
   residual, the other 3 (n=10/20/50) all land on the identical small -4
   universal noise already accepted throughout this project (the same
   magnitude/pattern seen in array_dint, indirect-index baseline, etc,
   not a formula defect). Wired via the existing
   `predefined_array_structures` mechanism (same pattern CAM_PROFILE
   already used) -- no new code path needed, just a new yaml entry.
   Live-verified against all 5 real manifest rows.

   **MESSAGE — James, 2026-08-25: "Message size is fine for the 90%
   accuracy as it's not a common usage instruction." Deprioritized —
   the research below stays as real, useful background, but no MESSAGE
   byte-size sweep is planned. MSG's LOGIC weight (48/rung) is resolved
   and wired; the operand's own MESSAGE structure cost stays unmodeled
   deliberately, not pursued further right now.**

   **MESSAGE, read across the corpus more broadly (not just one file).**
   Real shape is confirmed as a single self-closed `<MessageParameters>`
   element (`Data Format="Message"`), no `Structure`/`DataValueMember`
   body, no separate L5K block — genuinely simpler than TIMER/COUNTER/
   CONTROL. **New finding: the MessageParameters attribute SET is not
   fixed — it depends on `MessageType`.** Corpus-wide count across the
   real files: `CIP Generic` (21 uses, 12 attributes: MessageType,
   RequestedLength, ConnectedFlag, ConnectionPath, CommTypeCode,
   ServiceCode, ObjectType, TargetObject, AttributeNumber, LocalIndex,
   LocalElement, DestinationTag, LargePacketUsage — this is the type
   `message_tag_xml()` currently reproduces), `Unconfigured` (9, likely an
   MSG instruction whose message hasn't been set up yet — probably the
   smallest/default case), `PLC5 Typed Write` (8), `PLC5 Word Range Write`
   (4), `CIP Data Table Read` (3), `PLC5 Typed Read` (1, 7 attributes:
   MessageType, RemoteElement, RequestedLength, ConnectionPath,
   CommTypeCode, LocalIndex, LocalElement — genuinely fewer attributes
   than CIP Generic, real evidence the attribute count varies by type).
   **Testing only CIP Generic (the current `instrfirst_msg` shape) risks
   badly generalizing MESSAGE's byte cost to the other 5 real MessageTypes
   in this corpus** — if the real storage size depends on which
   attributes are present (plausible, unconfirmed), CIP Generic being the
   most attribute-heavy type could make it a poor stand-in for the whole
   MESSAGE-typed-tag population. Needs a byte-size sweep across at least
   CIP Generic and one PLC5-family type (the two ends of the observed
   attribute-count range) before treating one MessageType's cost as
   representative of all MESSAGE tags.

   **Not yet built:** a CAM count sweep — that's the one remaining
   concrete next step (MESSAGE's sweep is deprioritized per James above).
   This entry now reflects real mechanistic understanding (verified field
   lists, verified L5K/Decorated hiding behavior for CAM, verified real
   MessageType distribution for MESSAGE) rather than a single n=1 capture,
   even though CAM still has zero real byte-size data.

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

10. **OQ-MAMFAMILY-BUILDFAIL — root-caused and FIXED 2026-08-25, awaiting
    recapture.** MAH/MSO's real per-rung logic weight (60 blocks/rung
    each) is confirmed and wired, see RESOLVED_QUESTIONS.md OQ-MAHMSO.
    MAM/MAJ/MAS/MRP's 100% build failure was NOT a wrong/incomplete
    syntax question — James, 2026-08-25: "You need to put parameters in
    for motion instructions. right now you are calling
    MAM(Axis_Cip_Drive,MotionInstr1) but you need to have all of the
    parameters populated." The bare 2-operand call these 4 used is
    literally MAH/MSO's own real shape, not theirs — MAM/MAJ/MAS/MRP each
    need their own full parameter list, and none of the 4 share the same
    one. Reading the real corpus directly (`samples/local/L5X_Samples`)
    confirms four genuinely different real operand counts: **MAM=20,
    MAJ=17, MAS=9, MRP=5** — not one family, four distinct shapes.
    - MAM: James gave the corrected template verbatim (his own synthetic
      tag names, matching the real corpus's real MAM operand sequence and
      keyword positions exactly): `MAM(Axis_Cip_Drive,MotionInstr1,
      MoveType,Position,Speed,Units per sec,AccelRate,Units per sec2,
      DecelRate,Units per sec2,S-Curve,AccelJerk,DecelJerk,% of Maximum,
      Enabled,Programmed,LockPosn,None,EventDistance[0],
      CalculatedData[0]);`
    - MAJ/MAS/MRP: no explicit template given ("See samples for
      details") — built the same way MAPC's fix was (OQ-MAPC-COMPAT
      below): a position-for-position transplant from one real corpus
      example each, real keywords/literals kept verbatim, only tag names
      substituted. Real corpus references: `MAJ(Drive_Axis,Udt_Servo.MAJ,
      MAJ_Direction,MAJ_Velocity,Units per sec,MAJ_Accel,Units per sec2,
      MAJ_Decel,Units per sec2,Trapezoidal,Udt_Servo.MAJ_Jerk,
      Udt_Servo.MAJ_Jerk,% of Maximum,Disabled,Programmed,0,None)`,
      `MAS(Drive_Axis,MAS,All,No,Udt_Servo.MAJ_Decel,Units per sec2,No,
      Udt_Servo.MAJ_Jerk,% of Time)`, `MRP(EM40_Stacker_Virtual,
      Stacker.CycleReset.MRP_CarriageVirt,Absolute,Actual,0)`.
    - Fixed in `gen_motion_instructions.py`: `_MOTION_RUNGS` now holds a
      real full-parameter rung per instruction, `_MOTION_EXTRA_TAGS_XML`
      declares the new tags each needs (MoveType, Direction, Position,
      Speed, AccelRate, DecelRate, AccelJerk, DecelJerk, LockPosn,
      EventDistance, CalculatedData). MAH/MSO's own bare 2-operand call is
      untouched. All 12 files (4 instructions × 2 counts) regenerated,
      lint-clean, stale error_count/actual_bytes cleared from the manifest
      (the old broken-file readings no longer describe the current file
      content) — awaiting recapture.
    MAPC/MCCP camming still blocked separately on the unmodeled CAM
    structure, see OQ-PREDEFINED item 8 below.

    **2026-08-25, James, sequencing correction: "your next motion
    instruction test should be one L5X file per instruction with one
    instruction each - after validating these results then we can do a
    10-pass for confirmation... make sure you can handle ANY
    combination."** The n=10/n=100 files above are a single fixed
    template per instruction (one real corpus transplant each) — real,
    but not yet validated as a solo n=1 rung, and not covering the real
    keyword-VALUE variation each instruction's real corpus usage actually
    shows. `gen_motion_syntax_combos.py` (new, 14 files, all n=1, all
    lint-clean, awaiting capture) fills both gaps at once:
    - **MAM Merge field, Enabled vs Disabled** (both real corpus values)
      — James: does a merged move cost more than a disabled merge? Direct
      test, 2 files.
    - **MAJ Profile field, Trapezoidal vs S-Curve** (both real corpus
      values for MAJ specifically) — 2 files.
    - **MAS full combination coverage**, 2×2×2 = 8 files: Stop Type
      (All/Jog) × the two Yes/No fields James's "use existing values
      compared to using new values" maps to (both real corpus values seen
      for all three axes, no guessed keyword values).
    - **MRP's two real operand-4/5 patterns** (`Absolute,Actual,0` vs
      `Absolute,0,<position>`) — 2 files. MRP's own "Absolute" field was
      NOT varied — only one real value for it was ever found in the
      corpus, no confirmed alternate to test.
    Not a claim of exhaustive "ANY combination" coverage — every keyword
    tested is one a real corpus example actually uses, not a guess, but
    Rockwell's real documented value sets for these fields may be larger
    than what 3-8 real files happened to exercise. Flagged as a real
    limitation, not silently treated as complete.

    **RESOLVED 2026-08-26.** All 12 fixed-template files (n=10/n=100 ×
    4 instructions) and all 14 `gen_motion_syntax_combos.py` files came
    back `error_count=0` — the 100% build failure is fully closed, no
    remaining build risk for this instruction family. Clean 2-point
    linear fit wired into `memory_model.yaml`: **MAM=224, MAJ=236,
    MAS=100, MRP=128 blocks/rung.** The n=1 keyword-combination sweep
    confirms MAM's Merge flag, MAJ's Profile choice, and MAS's full
    StopType×Decel×Jerk 2×2×2 combination do NOT change size (every
    keyword variant lands on the identical byte count) — MRP is the one
    exception, its two real operand-4/5 patterns differ by 52 bytes (a
    real difference between those two call shapes, not modeled per-shape,
    single flat MRP weight used). This entry can move to
    RESOLVED_QUESTIONS.md on the next docs pass.

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

    **2026-08-26, James: "touch these and finalize them now."** Real
    progress, still genuinely not closeable tonight -- here's exactly why,
    not a deferral for its own sake. `taskoverhead_n04tasks` (4th data
    point) and `programoverhead_n02progs_1task` (2 Programs, SAME single
    Task) landed since the note above was written. Live-recomputed
    against the current engine:
    - **Per-Task axis: cleanly isolated, real, single clean comparison.**
      `taskoverhead_n02tasks` (2 tasks/2 programs/2 routines, actual
      19,600) minus `programoverhead_n02progs_1task` (1 task/2 programs/2
      routines, actual 18,900) holds program AND routine count IDENTICAL
      between the two files, varying ONLY task count — a real, isolated
      +700/extra-task marginal cost, not confounded with anything else.
    - **Per-Program axis: still NOT isolated from per-routine-within-a-
      program** -- every real file to date, including the two new ones,
      has program count and routine count moving together (every extra
      Program in this batch always brought exactly one extra Routine with
      it). There is still no real data point with 2 Routines under 1
      Program under 1 Task to break that tie. Extrapolating the n=3/n=4
      totals against the isolated +700/task rate leaves a small (+/-16 to
      32 blocks) residual too, consistent with a real, small, separate
      per-periodic-Task config cost not yet isolated either -- flagged
      honestly rather than folded into either number.
    - **Why this can't be code-wired tonight regardless of effort:** the
      per-Task correction and the per-Program/per-routine split are
      mathematically COUPLED through the existing `fixed_base_per_routine`
      mechanism (currently applied once per routine, unconditionally) --
      correcting one without the other would either double-correct or
      leave the model self-inconsistent for any file with more than one
      routine. This isn't an analysis gap that more time closes; it's a
      real missing data point.
    - **Closed the data gap, not the formula:** `gen_task_overhead_
      disentangle.py`'s new `taskoverhead_n02routines_1program_1task.L5X`
      (1 Task, 1 Program, 2 plain NOP routines, no JSR relationship) is
      generated, lint-clean, in the manifest, awaiting capture -- this is
      the exact missing 3rd axis. Once it lands, the +700/task rate above
      combines with it to fully solve the 3-way split in one more pass,
      no further test design needed.

    **RESOLVED (analysis) 2026-08-26 — the missing data landed, full 3-way
    split now solved cleanly via 3 chained direct comparisons, no
    assumptions:**
    - `taskoverhead_n02routines_1program_1task` (2 Routines, 1 Program,
      1 Task) = 18,416. Against the well-established general baseline for
      1 Task/1 Program/1 Routine (18,112 -- project_baseline+
      fixed_base_per_routine, independently confirmed hundreds of times
      elsewhere in this project): **pure per-extra-Routine cost (same
      Program, same Task) = +304.**
    - `programoverhead_n02progs_1task` (2 Programs, 2 Routines total, 1
      Task) minus the routine-only file above -- SAME routine count (2)
      in both, SAME task count (1), differing ONLY in whether those 2
      routines sit in 1 program or 2: 18,900 − 18,416 = **pure
      per-extra-Program cost = +484** (cleanly separated from the
      routine's own content cost for the first time -- earlier passes
      could only measure "+788" as one bundled program+its-mandatory-
      first-routine number; that 788 = 304+484 exactly, now split).
    - `taskoverhead_n02tasks` (2 Tasks, 2 Programs, 2 Routines) minus the
      2-program file above -- SAME program count (2) and routine count
      (2) in both, differing ONLY in task count: 19,600 − 18,900 = **pure
      per-extra-Task cost = +700** (matches the earlier direct-comparison
      result exactly, independent cross-check).
    Sanity check against the ORIGINAL taskoverhead_n03/n04tasks sweep
    (task+program+routine all scaling together): predicted =
    18,112+(n−1)×(304+484+700) reproduces n=2 exactly (by construction)
    and n=3/n=4 within the same small ±16 residual already flagged
    before this decomposition — a small, real, still-unexplained
    periodic-Task-specific cost (not resolved by this pass, but now
    isolated to a ±16 residual rather than an entire unmeasured axis).
    **Still not wired, for the same coupling reason above** — applying
    this correctly needs the parser to be Task-aware (which Program is
    scheduled under which Task, not just raw counts) and needs to be
    layered onto the existing per-routine `fixed_base_per_routine`/
    `jsr_fixed_base_per_routine` mechanism without disturbing the
    already-validated JSR-vs-plain-routine distinction those two
    constants encode. This is now a well-specified, bounded architecture
    task (not an open data question) — real next-session work, not
    rushed in during this pass given the interaction risk with JSR
    routines.

    **2026-08-26, James: "why am i having to push you to generate up
    these open things" — attempted the actual wiring this pass, not just
    re-deferred.** Live-recomputed the current (unmodified) engine
    against `taskoverhead_n02routines_1program_1task` directly: it
    predicts 22,960 (project_baseline + 2×fixed_base_per_routine +
    2×NOP's own 16/rung, since BOTH of that file's routines carry their
    own default NOP rung) against real actual 18,416 — a −4,544 gap. But
    the "18,112" 1-routine reference this whole decomposition subtracts
    against (see the RESOLVED analysis above) is NOT a real captured row
    — grepped `manifest.csv` for `actual_bytes=18112`, no match — it's a
    pure arithmetic construct (`project_baseline+fixed_base_per_routine`,
    a theoretical ZERO-rung single routine). Subtracting a 0-rung
    reference from a real file whose BOTH routines carry their own NOP
    rung conflates two different things inside the same "+304": genuine
    routine-shell structural cost, and 2×NOP's own real content cost —
    and NOP's rate has itself only ever been backed out from a single
    occurrence (see item 2's `group_empty_rungs` note below), not
    confirmed independently. Wiring a formula on top of an ambiguous
    split would risk shipping something subtly wrong across every multi-
    routine file's prediction from then on — worse than leaving it
    undocumented. **Not a re-deferral for its own sake: the real missing
    piece is a clean NOP-rate data point**, and `gen_branch_empty_rungs.py`
    (generated this same pass, see Phase 4 TASKS.md audit) happens to be
    exactly that — a dedicated NOP-only rung count sweep (N=10/100/1000,
    same 1 program/1 task) that will pin NOP's real marginal rate down
    independently. Once that lands, the true routine-shell-only constant
    (with NOP's contribution cleanly subtracted back out) can be derived
    and wired in one more pass, same as the string-formula pattern this
    session already used successfully elsewhere.

12. **OQ-INDIRECT — Indirect addressing overhead [captured 2026-08-25, real findings,
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

    **RESOLVED-ISH 2026-08-25: linearity confirmed, both numbers
    re-derived cleanly, still not wired (parser gap, not a data gap).**
    New count points (n=10/50/100, alongside the existing n=1000) landed
    for both variants:
    - `indirect_tag_index_*`: n10=19656, n50=24456, n100=30456,
      n1000=138456 — marginal is **exactly 120/rung** at every interval
      (n10→n50, n50→n100, n100→n1000 all compute to 120.0, zero
      variance). Perfectly linear.
    - `indirect_tag_offset_index_*`: n10=19896, n50=25656, n100=32856,
      n1000=162456 — marginal is **exactly 144/rung** at every interval.
      Also perfectly linear.
    - Direct subtraction against `indirect_direct_index_n01000`
      (act=54456) at the same n=1000 re-derives the earlier informal
      numbers exactly: tag-index overhead = (138456-54456)/1000 =
      **84/rung**, offset-index overhead = (162456-54456)/1000 =
      **108/rung** — matches the 2026-08-25 note above precisely, now
      backed by 4 points per variant instead of 1.
    - Cross-check: 120/rung (tag-index total) − 84/rung (indirect
      overhead) = 36/rung, and 144/rung (offset-index total) − 108/rung
      (indirect overhead) = 36/rung — the SAME implied base MOV(direct-
      index) marginal both ways. Internally consistent.
    - **RESOLVED 2026-08-26 — wired.** `parser/logic.py` now scans rung
      text for `Name[...]` bracket expressions and classifies each as
      direct/literal (0 cost), tag-driven (`tag_index_cost`), or tag+
      literal-offset (`tag_offset_index_cost`); `sizing/logic.py` applies
      the cost per real occurrence. Confidence KNOWN — verified live
      end-to-end (`build_report()` against the actual generated files,
      not just the formula in isolation) across all 8 real manifest rows
      (both variants × n=10/50/100/1000): every single one now lands on
      the identical tiny +4 flat baseline noise already seen elsewhere in
      this tag pool (confirmed unrelated to indexing — the direct/literal
      baseline file shows the same +4). Deliberately generalized to scan
      the WHOLE rung, not scoped to MOV specifically — only MOV-carried
      indexing was ever captured, so applying this inside e.g. a CPT
      expression's own indexed operand is an untested assumption, not
      independently confirmed for that context.

13. **OQ-STRINGTAGOVERHEAD — SCALAR CASE FULLY RESOLVED 2026-08-25 (both
    builtin and custom). Array-of-STRING split out as its own open
    question, OQ-STRINGARRAYPAD, below.** Builtin STRING's flat -2 bytes/tag correction
    is now confirmed and wired (RESOLVED_QUESTIONS.md OQ-STRINGTAGOVERHEAD
    -BUILTIN) via the dense 9-point `stringoverhead_builtin_n*` sweep plus
    the 4-point namelen cross-check, all exact 0-gap now.

    **Custom StringFamily types: real data, NOT clean enough to wire yet.**
    `stringoverhead_custom50_n*`/`custom500_n*` (2 max-lengths × 4 counts
    each) plus the pre-existing `customstring_250char_x1000` give 3
    max-length data points total. Per-tag marginal rate isn't a flat -2
    like builtin — it varies by max-length: maxlen=50 → -2/tag, maxlen=250
    → -2/tag (from the pre-existing point), maxlen=500 → **-4/tag**, each
    on top of a consistent +2 one-time offset (`gap(n) = 2 - k×n`, solving
    both unknowns from any 2 of the n=1/10/100/1000 points in each sweep
    reproduces every other point in that sweep exactly). **Working
    hypothesis, UNCONFIRMED — do not wire off this alone:** `k` may depend
    on `maxlen mod 4` (50 mod 4 = 2 → k=2; 250 mod 4 = 2 → k=2; 500 mod 4
    = 0 → k=4) — consistent across all 3 points so far, but 3 points
    matching a 2-bucket hypothesis isn't proof, and there's no mechanistic
    explanation yet for why mod-4 alignment would flip the correction
    magnitude rather than, say, add a fixed extra term. Needs at least 2
    more maxlen points to actually confirm this before touching code: one
    more `≡0 mod 4` value (e.g. 100 or 1000, to confirm k=4 replicates
    rather than being a one-off) and one `≡1` or `≡3 mod 4` value (e.g. 51
    or 501, to see whether k takes a third distinct value or the bucketing
    really is just "aligned vs not"). James: "I don't want to go forward
    with you assuming X" applies exactly here — 3 points fitting a 2-bucket
    story is exactly the kind of thing that needs one more probe before
    it's trusted, not a coincidence to build on yet.

    **2026-08-25, James: "Sounds like you still don't know what is going
    on with strings... make another 20 tests... 100% accuracy for strings
    and custom length strings." `gen_string_batch2.py`, 21 files, 5
    groups, all lint-clean, all awaiting capture:**
    - `group_mod4_bucket1` (6 files) — fills the completely-untested
      `maxlen mod 4 = 1` bucket (49/101/501, at n=1/n=100 each), the third
      possible remainder alongside the 0 and 2 buckets already probed.
    - `group_string_array` (4 files) — a genuinely new structural context:
      ONE array-of-STRING tag (`Dimensions=N`), never tested before (every
      prior STRING test used N separate scalar tags). Real XML shape
      confirmed against 2 independent corpus examples (built-in:
      `CMU_2025_10_14r00.L5X`'s `CMU_PackNames`; custom type:
      `Gutchess_GreenLine_2026_06_04r00.L5X`'s `PrintStrings`, DataType=
      `SortString`) — structurally different from a scalar STRING tag
      (L5K+Decorated-Array, not the scalar's L5K+String pair), so the
      per-element cost inside an array is a real open question, not an
      assumed-same-as-scalar extrapolation. New `string_array_tag_xml()`
      builder added to `builders.py`.
    - `group_string_udt_member` (4 files) — STRING (built-in and custom)
      as a UDT member. The XML shape already existed in code
      (`_string_structure_member_xml`) but no real Capacity byte-size data
      had ever been captured for this context — the shape being coded
      doesn't mean the cost was known.
    - `group_namelen_custom` (3 files) — name-length × custom-maxlen
      interaction at maxlen=100, name lengths 4/16/40. The existing
      namelen cross-check only ever used built-in STRING; never confirmed
      the `8×floor(len/8)` name-length term holds unchanged for a custom
      string type specifically.
    - `group_extreme_maxlen` (4 files) — boundary/stress maxlens: 1/2/4
      (below anything tested so far) and 4000 (2× the largest previously-
      confirmed-working value; `customstring_len*` topped out at 2000,
      RESOLVED_QUESTIONS.md OQ-CUSTOMSTRINGDEF).

    **RESOLVED 2026-08-25, James: "I want strings as a whole closed. No
    more open questions or unknowns."** Chasing the mod-4 residual found
    a real bug, not an unexplained Rockwell mechanism: the DATA member
    was sized RAW with zero rounding. Real mechanism, verified EXACT (0
    residual) against 9 real maxlen points spanning every mod-4/mod-8
    remainder: DATA rounds to the NEAREST multiple of 8, rounding DOWN at
    the exact tie (remainder 4 after a plain 4-byte pad) — e.g. maxlen=50
    and 51 measure byte-identical real memory (both round to 48), while
    maxlen=100 (a tie) drops to 96 and maxlen=101 (already 0-mod-8) stays
    at 104. Separately, maxlen mod 4 == 1 gets its own confirmed +8
    one-time definition-cost bonus (3/3 exact: 49, 101, 501). Wired in
    `udt.py`/`report.py`, `custom_data_padding_confidence` upgraded
    FITTED→KNOWN. See RESOLVED_QUESTIONS.md for the full derivation.

    **Two threads found and reopened while verifying the fix end-to-end,
    NOT yet closed:**
    - **Type-name length**: `stringoverhead_customnamelen*` (maxlen=100,
      a longer type name than the maxlen=100 case that fits exactly)
      shows a flat, unexplained +8 the confirmed formula doesn't cover.
      `gen_string_closure.py`'s `group_typename_length` (6 files, short/
      medium/long type names at the same maxlen) isolates it directly —
      generated 2026-08-25, awaiting capture.

      **2026-08-26, that batch's data landed: -8 at 1 char, 0 at 9 char,
      +24 at 32 char.** Confirms the residual is real (not noise, def_only
      and 1_instance shapes track identically, i.e. it's purely a
      DEFINITION-level effect) but 3 sparse points still don't fit any
      clean formula tried — a `ceil`/`floor`-per-8-chars step function
      predicts nonzero deltas for the already-confirmed flat-0 6/7/14-char
      names, directly contradicted by real data. James, 2026-08-26: "I
      want to close strings." `gen_string_close_out.py`'s
      `group_dense_namelen` (22 files, every integer length 1-16 plus
      20/24/28/32/36/40, def_only only — def_only and 1_instance were
      already shown to track identically at this same 3-point sweep, so
      testing def_only alone isn't a shortcut) is built specifically to
      find where the -8→0 and 0→+24 transitions actually sit, lint-clean,
      awaiting capture. Not wired — no formula to wire yet, this batch
      exists to produce one.

      **SOLVED 2026-08-26, wired.** All 22 dense-sweep points landed and
      fit a clean step function exactly, 22/22 real points, zero
      residual: `custom_definition_cost_for(name_len) = base(208) +
      bucket(8) * floor((name_len - offset(5)) / bucket(8))`. This also
      resolves the earlier "6/7/14-char names should be flat-0" claim as
      never actually having been tested against a maxlen=100-matched
      sample at 14 chars specifically — the old sweep varied maxlen
      primarily, with incidental name lengths; 6 and 7 chars DO land in
      the confirmed flat zone (offset 5 through offset+bucket-1=12), so
      there's no real contradiction, just an under-specified earlier
      claim. Cross-checked against 3 more real points where the SAME 3
      type names (1/9/32 chars) are used as a UDT member instead of
      standalone (`stringclose_udtmember_namelen_short/medium/long`): 2/3
      matched the formula exactly at the total-report level; the 3rd
      (32-char name) showed an apparent -8 that traced entirely to the
      *wrapping* UDT's own name length (16 chars vs the other two
      fixtures' 17/18 chars — an unrelated, already-KNOWN, already-exact
      `udt_definition.name_per_8_chars` effect, confirmed by inspecting
      the individual `udt_definition` report entries: the string type's
      own line item was exactly 200/208/232 in all 3 files, matching the
      formula perfectly every time). No separate UDT-nesting tax exists —
      the earlier-suspected "+8 nesting mystery" is fully explained by
      name length alone. Wired in `constants.py`'s `StringModel.
      custom_definition_cost_for()`, `memory_model.yaml`'s
      `custom_definition_base`/`_namelen_offset`/`_namelen_bucket`,
      `report.py`, and `tree.py`'s `_expand_string_definition`. Also
      confirmed via `stringclose_udtmember_maxlen_0050/0250/0500/1000`
      (4/4 exact) that the cost depends ONLY on the type's own name
      length, not on its `maxlen` — no separate maxlen-dependent nesting
      term needed either.
    - **Array-of-STRING** (both builtin and custom): see new
      OQ-STRINGARRAYPAD below — split out as its own question since it's
      a structurally different case (Decorated array, not the scalar
      L5K+String pair) with its own, different real residual.

14b. **OQ-STRINGARRAYPAD (new, 2026-08-25, found while verifying the
    scalar custom-string padding fix end-to-end).** Array-of-STRING (one
    tag, `Dimensions=N`, per OQ-STRINGARRAY/`string_array_tag_xml`) shows
    a real residual that is NOT the same mechanism as the scalar case:
    - **Builtin STRING array** (`stringarray_builtin_n005/n050`): real
      marginal rate is 88/element vs. the plain-atomic 86/element the
      engine assumes (+2/element, confirmed via 2 clean points, growing
      not flat) — array elements apparently do NOT get the scalar tag's
      -2/tag benefit and instead carry a small NET +2/element cost of
      their own. Only 2 count points existed; not enough to also confirm
      the one-time intercept.
    - **Custom string array** (`stringarray_custom100_n005/n050`,
      maxlen=100): looked like a flat +6 one-time offset BEFORE the
      scalar nearest-8 padding fix landed. Recomputing live against the
      NOW-correct scalar per-element formula (maxlen=100 → nearest-8
      rounds DOWN to 96, per the fix above) makes the residual WORSE and
      GROWING (+24 at n=5, +204 at n=50) — the scalar fix does not
      transfer cleanly to the array context; array elements evidently pad
      differently than a scalar instance of the same custom type.
    - **Generated 2026-08-25, `gen_string_closure.py`'s
      `group_string_array_countsweep`** (8 files: builtin + custom100 at
      n=1/10/25/100, alongside the existing n=5/50): enough points for a
      real multi-point fit once captured, instead of guessing off 2.
      Do not treat array-of-STRING as closed until this lands — it is the
      one piece of "strings as a whole" genuinely still open.

    **RESOLVED 2026-08-26, wired.** All 6 count points landed clean per
    variant (builtin: n=1/5/10/25/50/100; custom100: n=1/5/10/25/50/100
    across 2 type names). Real formula, confirmed exact:
    `total = array_base + (scalar_element_size + per_element) * n`.
    Builtin: `array_base=6, per_element=2` — KNOWN, 6/6 real points exact,
    zero residual. Custom: `per_element=4` — KNOWN, 6/6 points exact
    across BOTH type names tested (11-char and 13-char, same slope both
    times). `array_base` for custom is FITTED not KNOWN — it's real but
    type-name-length-dependent (the 2 type names gave array_base=4 and
    =12, a consistent +8 gap that lines up with the same still-open
    type-name-length effect on the scalar definition cost below); wired
    using the better-supported 13-char name's value (12, backed by 4
    points vs the other's 2). Wired in `udt.py`'s `compute_array_size`
    (new `STRING`/`is_string_family` branches before the generic atomic/
    array-of-UDT fallback) and `memory_model.yaml`'s new `string_array`
    section. Live-verified against all 12 real manifest rows: 10/12
    exact, 2/12 (the 11-char-name family) show the expected, already-
    documented ~8-byte type-name-length gap — not a bug, the honest
    predicted consequence of using the better-supported name's intercept.

14c. **OQ-STRINGUDTMEMBER (tracked separately, mostly a capture-queue
    issue not a formula gap).** STRING (builtin and custom) as a UDT
    member (`udtstring_builtin_n01/n10`, `udtstring_custom100_n01/n10`,
    `gen_string_batch2.py`'s `group_string_udt_member`) — 3 of these 4
    rows were flagged WINDOW TITLE MISMATCH in the 2026-08-25 capture
    batch and will auto-retry per the fix in TESTING_PLAN.md's "Window-
    title-mismatch retries are automatic" section, no new generation
    needed. Only `udtstring_builtin_n10` has real usable data
    (delta=-20, single point, unexplained) — too little to fit anything
    yet. Revisit once the retried rows land.

    **2026-08-26, all 4 rows now have real data, real findings, NOT
    wired — two separate real effects, not yet closeable.**
    - **Builtin STRING as a UDT member**: `n01`=-2, `n10`=-20 — a real
      slope of exactly -2/instance, matching the confirmed scalar
      `builtin_tag_overhead_correction` (-2) precisely. Strong evidence
      this correction should apply once per builtin-STRING-member-
      containing tag INSTANCE, not only to standalone STRING-typed tags
      — but only 2 count points exist and no test yet separates "per tag
      instance" from "per STRING member" (a UDT with 2+ STRING members
      is untested).
    - **Custom100 (16-char type name "CStrUdtMember100") as a UDT
      member**: `n01`=+8, `n10`=+8 — FLAT, not growing, so a one-time
      definition-level effect, not per-instance. Could be the SAME
      already-known type-name-length effect (16 chars is untested on the
      standalone curve, which only has points at 1/9/32 chars) showing
      up here, or a genuinely separate UDT-nesting tax — can't tell from
      one data point which.
    - **`gen_string_close_out.py` built 2026-08-26** to resolve both:
      `group_builtin_udtmember_scaling` (n=3/n=20 count points, plus 2-
      and 3-STRING-member UDTs at n=1, isolating per-instance vs per-
      member), `group_udtmember_namelen_crosscheck` (the exact 3 type
      names already tested standalone — 1/9/32 chars — reused as UDT
      members, so a direct comparison reveals whether nesting adds
      anything beyond name length), `group_udtmember_maxlen_sweep` (a
      fixed short, flat-0-zone type name at maxlen 50/250/500/1000, to
      see if the nesting residual — if group B confirms one exists at
      all — depends on the string's own size). 11 files total, lint-
      clean, in the manifest, awaiting capture.

    **2026-08-26, `group_udtmember_namelen_crosscheck` and
    `group_udtmember_maxlen_sweep` are now CLOSED** — see the SOLVED
    block under item 14 above: the custom100-as-UDT-member case has NO
    separate nesting tax at all, it's fully explained by the same
    standalone type-name-length formula (once the wrapping UDT's own,
    unrelated, already-KNOWN name-length cost is accounted for), and has
    no dependence on the string's own `maxlen` either (4/4 exact).

    **`group_builtin_udtmember_scaling` (builtin STRING, not custom)
    landed too — real, still NOT closeable, needs one more test axis.**
    4 new points, all live-verified exact once the naive (uncorrected)
    per-member formula is used as the baseline to diff against:
    - 1 instance, 2 STRING members: correction = 0 (no adjustment).
    - 1 instance, 3 STRING members: correction = **+2** (real memory is 2
      bytes HIGHER than the naive sum — the opposite direction from the
      existing -2/instance correction).
    - 1-member UDT, 3 instances: correction = -6 (exactly -2 × 3).
    - 1-member UDT, 20 instances: correction = -40 (exactly -2 × 20).
    So at a FIXED instance count of 1, correction as a function of member
    count m fits a clean line: `correction(m, n=1) = 2m - 4` (m=1: -2,
    matching the older single-point finding; m=2: 0; m=3: +2). And at a
    FIXED member count of 1, correction as a function of instance count n
    is simply `-2n` (m=1, n=1/3/10/20 all fit). These are two 1-D slices
    through what must be a 2-D surface (member count × instance count),
    and no combination tried (`-2n + 2(m-1)`, `-2n*m`, etc.) reproduces
    both slices from one formula without a data point at m>1 AND n>1
    simultaneously to pin it down. Not wired — would be guessing which
    2-D surface fits from two 1-D slices alone. Next test needed: a 2- or
    3-member UDT at n=3 or n=10 (not yet generated) to disentangle. Left
    open deliberately rather than force-fitting a shape from insufficient
    data, per this project's standing discipline against overfitting
    2-point findings.

14d. **OQ-STRINGCONSTFAIL — RESOLVED 2026-08-26, real cause was tooling,
    not the L5X content; the processor-varying design itself was
    unnecessary and has been dropped.** James:
    "check the string test acd failures and see if there is something you
    want clarification on the l5x generation." `gen_string_closure.py`'s
    `group_constant_flag` batch (`stringconst_*`, 8 files: builtin/custom
    x const/nonconst x L8/5069) failed 8/8, `XMLSrv_E_IMPORT_ABORTED_
    NO_CHANGES`, no further detail reaches `convert_log.csv` (the .NET SDK
    wrapper only logs "See error log" with no error-log content
    captured). Investigated and ruled out:
    - **Constant value itself**: both `const` (true) and `nonconst`
      (false) variants failed identically — the real corpus has a
      confirmed working `Constant="true"` STRING example
      (`samples/local/DnR_Personal/Fisher_Synergy_Bead_20240725.L5X`'s
      `Comma` tag, `Constant="true" ExternalAccess="Read/Write"`, same
      shape as this project's generated tags) — Constant isn't the sole
      trigger since even the plain `false` case failed too.
    - **Processor validity broadly**: both L8 (1756-L85E) and 5069
      (5069-L306ER) variants failed. 5069-L306ER alone has succeeded in
      hundreds of prior conversions across this whole project, so 5069
      itself isn't the trigger either.
    - **XML encoding/malformation**: byte-level check clean, no non-ASCII,
      no malformed CDATA.
    - **ProductCode mismatch**: found and fixed a REAL bug while chasing
      this (wrapper.py's per-catalog ProductCode was wrong for every
      processor except the untouched default — see the wrapper.py commit
      2026-08-26 sourced from `samples/local/fw_versions/`'s real
      exports), but the SAME kind of mismatch was present in hundreds of
      prior successful 5069-L306ER conversions, so it's very unlikely to
      be the actual cause here. Regenerated all 8 files with the
      corrected ProductCode anyway to eliminate it as a variable — still
      awaiting a fresh conversion attempt.
    **Real cause, from James pasting the actual Studio 5000 import output
    (the on-screen text never reached `convert_log.csv`):**
    ```
    Warning: Line 11: Name collision: imported Module 'Local' renamed to 'Local1'
    Error: Line 20: Required property 'Port' was missing.
    ```
    Not a bug in the L5X — Studio 5000 was treating this as an IMPORT
    into whatever project was ALREADY open in the same running Designer
    instance (the AHK-driven "switch file via Ctrl+O without closing"
    batch-capture flow this project relies on for speed), not a fresh
    Open. Every prior file in this whole project's capture history kept
    the same Controller/processor identity between consecutive files, so
    the "Local" module always matched cleanly. The first time a batch
    item's PROCESSOR differs from whatever was previously loaded (L85E or
    5069-L306ER after an L81E file), the same-instance switch can't
    replace the "Local" module in place — it renames the incoming one to
    "Local1" and the renamed module then fails structural validation.
    This would affect ANY processor-varying file run through the
    same-instance switch flow, including the 29 `fw_baseline` files still
    awaiting capture.

    **Design itself corrected, not just the tooling gap worked around**
    (James, direct field knowledge, 2026-08-26): "5069 and l8/l9
    processors use the same calculations for constant strings ... don't
    know why you would change that all of a sudden." The processor
    variation in this test was never a real open question — L8/L9/5069
    compute identically here. Real fact for the record, unrelated to
    sizing but worth keeping: **L8/L9/5069 can `MOV` a STRING tag
    directly; older L7/1769 processors required `COP` instead.**
    `group_constant_flag` rebuilt to drop the processor axis entirely and
    use the same single default processor (1756-L81E) every other file in
    this project uses — 4 files (builtin/custom × const/nonconst),
    regenerated, lint-clean, awaiting capture. The "Local"-module-collision
    tooling gap is still real and still applies to the 29 `fw_baseline`
    files (those genuinely need to vary processor, by design) — that
    part of this finding stays open and relevant there, just no longer
    blocking this particular test.

    Also noted: `stringoverhead_namelen32_n050`'s 3 FAILED rows in this
    same push are OLD (timestamps from earlier 2026-08-23, before the
    double-underscore fix landed) — the currently-committed file is
    already clean (no `__` present), just needs a fresh reconversion
    against the current L5X, not a new investigation.

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

    **MAJOR CORRECTION 2026-08-25 (same day, later): the ~20/param finding
    above was standing on data of UNKNOWN build validity, and a real
    generator bug was found and fixed.** The new n=2/3/4/6/8/12 count-sweep
    batch (`gen_batch3_followups.py`'s `group_e_jsr_paramcounts`) came back
    with `error_count` EXACTLY EQUAL to `param_count` on every single file
    (n02→2 errors, n03→3, n04→4, n06→6, n08→8, n12→12) — not noise, a
    perfect 1:1 pattern. Root cause, confirmed by reading the generator:
    `_sub_routine_xml`'s callee-side locals (`LIn0..LInN`, referenced in
    `SBR(LIn0,LIn1,...)`) were **never declared as tags anywhere** — only
    the caller-side `JIn0..JInN` args got a `tag_xml` declaration. Per the
    module's own real-corpus research (SJ_Gormley routines), SBR's param
    names and JSR's input-arg names are unrelated, positionally-mapped
    tags — BOTH sides need their own declaration, not just the caller's.
    One undeclared-tag build error per missing local, exactly matching the
    observed pattern.

    **This bug was in `gen_jsr_sbr_ret.py` too** (`group_param_count`,
    `group_mixed_io`, `group_multiple_ret` — the ORIGINAL n=1/5/10/r01000
    files this whole ~20/param finding was built from), and those files'
    `error_count` was never recorded at all (blank, not `0` — they predate
    error-count tracking) — so whether the "confirmed" ~20/param number
    was fit against clean or silently-broken builds is **genuinely
    unknown, not confirmed either way**. Downgrading that earlier estimate
    from "roughly-linear, ~20-21/param" to **unconfirmed, pending clean
    retest** — it may still turn out to be close, but it was never
    actually verified against `error_count=0` data.

    **Fixed 2026-08-25:** both generator files now declare every callee-
    side local (`LIn*`/`LOut*`) as a real DINT tag alongside the caller-
    side args, in the same Program-scope tags block. All 11 affected files
    regenerated under their original sample_ids (lint-clean), stale
    pre-fix capture data cleared from manifest.csv (this was a real build-
    breaking bug, not a window-title-mismatch — needs a full ACD
    reconversion, not just an auto-retry of the capture step). Awaiting
    a clean re-capture before the per-param cost can be trusted at all.

    **2026-08-26, clean retest landed — bug fix confirmed, build failures
    fully resolved.** Every JSR-family row (`instr_jsr_n*`, all 6
    `jsr_paramcount_n*_r00100`, all 5 `*_r01000` incl. `jsr_mixedio_*` and
    `jsr_multiret_*`) now shows `error_count=0`. Note: recomputing deltas
    against the CURRENT live engine (not the stale `predicted_bytes`
    frozen in manifest.csv at old capture time) matters here — the
    0-param `instr_jsr_n*` rows' stored `predicted_bytes` predate several
    since-fixed model bugs and falsely implied a flat +13,309 gap; live
    recompute shows that's actually a flat **+23** across n=10/50/100/
    1000/5000 — i.e. the existing `jsr_fixed_base_per_routine`/JSR-weight
    combo is already essentially correct for the 0-param case, nothing to
    fix there.

    Per-param cost, live-recomputed: the **r=100 group is clean and fits
    exactly**: `delta = 512 + 2020*n_params` for n=3,4,6,8,12 (all exact,
    0 residual); n=2 is the lone outlier (-4). This is consistent with
    (and sharpens) the pre-bugfix rough ~20-21/param/rung estimate
    (2020/100 rung = 20.2/param/rung). **The r=1000 group (n=1,5,10) does
    NOT fit the same formula** when the r=100 fit is scaled by rung count
    (tried both "pure per-rung" and "flat one-time + per-rung" scalings,
    both leave 1,800-5,200-block residuals) — and critically, **the two
    rung-count groups share zero overlapping param counts** (r=100 tested
    n=2/3/4/6/8/12, r=1000 tested n=1/5/10), so there's no way to solve
    for a fixed-vs-per-rung decomposition from current data alone. Two
    live hypotheses, neither confirmed: (a) the r=1000 group is riding the
    same unexplained large-file "+264-family" anomaly flagged elsewhere in
    this doc for other n=1000-rung-count files, just scaled up by param
    count; (b) the per-param cost genuinely has both a rung-count-independent
    one-time term (subroutine Parameters-block cost) and a per-call term,
    and 512+2020n at r=100 doesn't isolate them cleanly on its own.
    **Not wired** — the r=100 fit is trustworthy standalone but wiring it
    as a flat per-rung rate would be a guess at rung counts other than 100
    given the r=1000 mismatch. **Needs**: a small param-count sweep
    (e.g. n=2,5,10) re-run at a rung count that overlaps the existing
    r=100 or r=1000 data, to solve the two-term decomposition properly.
    `jsr_mixedio_5in_2out_r01000` (delta 144244) and `jsr_multiret_n04_
    r01000` (delta 64456) sit alongside as extra r=1000 data points for
    whenever that decomposition work happens, not analyzed further here.

    **BREAKTHROUGH 2026-08-26 — decomposition solved cleanly, real data.**
    `gen_jsr_decompose.py`'s 2 files (n=5, n=10 at r=100, matching the
    existing r=1000 points at those same param counts) landed. For the
    FIRST time this project has BOTH rung counts at the SAME param count
    — the two-variable system (`delta(n,R) = A(n) + B(n)*R`) can finally
    be solved directly instead of guessed at:
    - n=5: `A+100B=10604`, `A+1000B=104204` → **B(5)=104/rung exactly,
      A(5)=204 exactly**.
    - n=10: `A+100B=20704`, `A+1000B=204304` → **B(10)=204/rung exactly,
      A(10)=304 exactly**.
    Both solve to clean integers (not coincidental-looking noise), and
    both fit a simple linear-in-n pattern: `B(n) = 4 + 20*n` (the true
    per-rung, per-call rate), `A(n) = 104 + 20*n` (a real, one-time,
    rung-count-independent cost — almost certainly the subroutine's own
    Parameters-block declaration cost, scaling with param count but paid
    once regardless of how many times the routine is called). This also
    explains the earlier "r=1000 doesn't fit the r=100-only formula"
    finding: the r=100-only fit (`512+2020n`) was measuring `A(n)+100*B(n)`
    collapsed into one line, not the true per-rung rate — not a
    contradiction, a different (composite) quantity. Cross-check:
    `A(n)+B(n)*100` using the new A/B formulas reproduces 5/6 of the
    ORIGINAL r=100 sweep (n=3,4,6,8,12) with a flat +8 residual (their
    real values run 8 higher than this 2-point-derived formula predicts)
    — real, small, and exactly the kind of "confirmed on 2 points, doesn't
    perfectly generalize" gap this project's discipline exists to catch,
    not glossed over here.
    **Still NOT wired** — only 2 (param-count) points have been through
    this decomposition; a linear fit through exactly 2 points is
    trivially exact and doesn't by itself prove `A(n)`/`B(n)` are really
    linear in n generally (the +8 mismatch against the n=3/4/6/8/12 group
    above is the concrete evidence it might not be). `gen_jsr_decompose.py`'s
    new `group_jsr_third_disentangle_point` (n=8 at r=1000, matching the
    existing n=8 at r=100) is generated, lint-clean, in the manifest,
    awaiting capture — the cheapest way to get a 3rd real (A,B) solve and
    confirm or refute the linear-in-n pattern before trusting it enough
    to wire.

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

    **RESOLVED 2026-08-26, retest landed, originals confirmed correct —
    not a race after all.** `_v2` retests for 3 of these rows reproduced
    values matching (or within a few blocks of) the originally-flagged
    readings: `array_dint_00001_v2`=18240 (matches `_00001` exactly),
    `array_dint_00002_v2`=18240 (matches `_00002` exactly),
    `array_dint_00005_v2`=18256 (matches the CORRECTED, non-contaminated
    `_00005` reading, confirming n=5 really is distinct from n=1/n=2 —
    the pre-retest 18240-for-all-three was the actual bug, now gone),
    `paramcount_n04_def_only_v2`=19400 (within 8 of original 19392),
    `paramcount_n08_def_only_v2`=19472 (exact match), `udttagcomment_
    len000_v2`=18416 (exact match — and see OQ-AOIDEF-adjacent finding
    below, comment length has zero effect on size regardless, so this
    row's exact value was never in question). n=1 and n=2 DINT arrays
    genuinely DO report the identical `actual_bytes` (18240 both, in both
    the original and retest) — real, reproducible, not a race: the 4-byte
    real difference between a 1- and 2-element DINT array evidently
    doesn't cross whatever granularity Logix Designer's Capacity display
    rounds to at this size. No further recapture needed for this list.

    **Also resolved in passing:** `udttagcomment_len000/010/025/050/100/
    200_def_only` (tag comment length 0/10/25/50/100/200 chars, same UDT
    otherwise) all read the same `actual_bytes=18416` — tag comments have
    ZERO effect on stored size, confirmed clean across 6 real length
    points, consistent with comments being IDE-only metadata that isn't
    part of compiled controller memory. No formula needed (already
    correctly unmodeled, i.e. correctly contributes 0).

    **Action (historical, now moot for the list above):** these 6 sample_ids (plus, out of caution, `paramcount_
    n08_def_only`'s neighbor `n16`/`n32` should be spot-checked too since
    the race could plausibly cascade) need a clean recapture. Flagging for
    inclusion in the next test batch rather than silently trusting the
    current values — none of the derived constants in this repo currently
    depend on these 6 rows specifically (array-of-DINT and AOI param-count
    are both already confirmed from their clean data points), so this is
    a data-integrity flag, not a currently-wrong wired constant.

17. **Two more real generator bugs, found and fixed 2026-08-25 from
    James's `docs/OPEN_BUILD_ERRORS.md` review — both awaiting recapture.**
    - **Double underscores are forbidden in Rockwell tag names** (James:
      "looks like you have a double underscore and that is forbidden") —
      `stringoverhead_namelen32_n050` failed L5X→ACD conversion
      (`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES`) because its name-length
      padding filler (`"_LONGNAME" * k`, truncated to hit an exact target
      length) happened to end in `_` right where it abuts the tag's own
      `_NN` numeric suffix, at `pad_needed mod 9 == 1` (32 chars is the
      only one of the 5 name lengths tested — 4/8/16/40 — where that
      remainder occurs). The same filler-truncation pattern exists in 3
      places (`cli.py`'s `_padded_tag_name`, `gen_string_tagoverhead.py`
      and `gen_string_batch2.py`'s `group_namelen`/`group_namelen_custom`)
      — all 3 now guard against a trailing `_` (swap it for a non-
      underscore char, preserving the exact requested length) rather than
      just fixing the one file that happened to hit it. Regenerated
      `stringoverhead_namelen32_n050`, lint-clean, awaiting capture (never
      had real data before — nothing to clear).
    - **AOI call-site tag count must match the definition's Required/
      Visible parameter count** (James: "your AOI has the tag name and
      the inout as required/visible, but the calling routine has
      tagName,FaultResetVal,Axis_Cip_Drive. the 3rd tag has no where to
      go... change required for the faultReset -OR- remove FaultResetVal
      from the calling routine"). `axis_aoi_inout_1_instance`/
      `axis_full_combo` declared their BOOL Input param (`FaultReset`)
      with the generator's default `required=False, visible=False`
      (hidden — real semantics: "nowhere to appear on the calling rung at
      all", per `MemberSpec`'s own docstring), but the rung text wired
      `FaultResetVal` into it anyway — 2 build errors each. Fixed by
      marking `FaultReset` `required=True, visible=True` in
      `gen_axis_composite.py` (both `group_axis_aoi_inout` and
      `group_full_combo` share the exact same bug, both fixed together),
      keeping the call-site wiring as originally intended rather than
      dropping the argument. Regenerated, lint-clean, stale `actual_bytes`
      /`error_count` from the broken version cleared from the manifest
      (43,680/44,792 with 2 errors each no longer describe the current
      file), awaiting recapture.

17. **OQ-MODULEIO (new, 2026-08-27, James: "what is holding us back from
    project completion").** Module/IO parsing has been an open Phase 1 gap
    the whole project, never started. First-pass parser now built
    (`parser/modules.py`) and unusually promising: real corpus inspection
    (`samples/local/DnR_Personal/*.L5X`, not committed, gitignored per
    normal policy) found that, unlike every other sizing category here,
    Logix Designer's own L5X export states the real byte sizes directly —
    each `<Connection>` carries `InputSize`/`OutputSize` attributes, each
    `<ConfigTag>` carries `ConfigSize` — no empirical fitting needed to
    get the RAW size right. Verified against 23 real modules (Local I/O,
    a multi-Connection safety module correctly summed) plus 5 new unit
    tests (`tests/test_modules.py`), all passing.

    **What's still open:** whether these L5X-stated bytes map 1:1 onto
    real controller Capacity-tab consumption, or (like tag_overhead,
    alias_overhead, udt_definition, and literally every other category
    in this project's history) carry their own real per-module and/or
    per-connection overhead on top. Given this project's track record,
    assuming 1:1 without verification would be a real risk — so
    `report.py` deliberately does NOT sum module bytes into any
    prediction yet; it surfaces each module as a non-summed `SizeError`
    (path `modules/<name>`) stating its raw L5X sizes, same treatment
    AXIS_CIP_DRIVE/MOTION_GROUP got before their own real formulas
    landed. **Next step, needs James, not more generation:** since a
    synthetic module can't be authored from scratch the way tag/UDT
    tests can (module Catalog/Connection/EKey XML is hardware-specific
    and this project has zero confirmed template for inventing a NEW one
    safely — every module example is a real corpus file, not something
    this project's generators know how to build), the fastest real path
    is a small, targeted real-world test: capture the exact Capacity-tab
    delta between two of James's own real project variants that differ
    ONLY in one added/removed I/O module (or, if he wants a controlled
    synthetic version, he'd need to add one module to an otherwise-blank
    test project in Studio 5000 himself and export it, since only Logix
    Designer itself can generate valid module/Connection XML for a real
    catalog number). Once even 2-3 such deltas exist, the per-module/
    per-connection overhead constant can be fit directly against these
    already-exact raw sizes — a much smaller fitting problem than usual.
    Produced/consumed tags (OQ-PRODCONS) remain completely untouched,
    same as before this pass.

18. **OQ-EMPTYROUTINE (new, 2026-08-24, found while investigating the
    `l81_v35` fw_baseline manual entry).** `l81_v35` (1756-L81E, firmware
    35.05 — the SAME firmware every other confirmed file in the corpus
    uses) showed a real +4,816 gap against the engine's flat 13,296
    prediction, even though this file has zero tags/UDTs/logic content —
    at first glance a firmware effect, but the gap being EXACTLY equal to
    `fixed_base_per_routine` (4,816) was too clean to be that. Root
    cause, confirmed by inspecting the actual XML: this file's
    `MainRoutine` is a self-closing `<Routine Name="MainRoutine"
    Type="RLL"/>` with NO `RLLContent` child element at all — different
    from every other test file in this project, whose default routine
    always has an `RLLContent` (even if just one NOP rung).
    `parse_rll_routines` (parser/logic.py) currently does `rll_content =
    routine_el.find("RLLContent"); if rll_content is None: continue` —
    silently skipping such a routine entirely, charging it 0 bytes,
    exactly as if it didn't exist in the program at all.

    **This is NOT a rare synthetic-file quirk — real corpus check found
    the self-closing-Routine shape in 15 of James's real production
    files**, from 1 up to 10 such routines in a single file
    (`SJ_Gormley_20251112_r02.L5X` has 10) — presumably real
    unused/placeholder routines left in place, a completely normal real-
    world pattern. If real Studio 5000 genuinely charges something for a
    routine with no RLLContent (this one data point says ~4,816, the same
    as an ordinary 1-rung routine's fixed base), every one of those 15
    real files' predictions is currently under-counting by roughly
    4,816 × (however many empty routines it has) — potentially a
    significant, previously invisible source of error across a large
    fraction of the real corpus.

    **Only 1 clean data point (l81_v35) isolates this specifically** —
    not enough to wire a fix. Two real open questions before touching
    code: (1) is the true cost really identical to an ordinary 1-rung
    routine's `fixed_base_per_routine`, or did this just coincidentally
    match at n=1 (need a 2+ empty-routine file to check whether it scales
    linearly the same way ordinary routines do); (2) does JSR's
    `is_jsr_target` skip-logic need to change too if a self-closing
    routine is ever a JSR target (untested — every JSR-target routine
    tested so far has real RLLContent). `l81_v30`'s own +15,976 gap
    (OQ-BASELINE-PROCFW above) almost certainly includes this same
    +4,816-ish component on top of whatever real firmware-specific
    residual exists, since it has the identical self-closing-`MainRoutine`
    shape — flagged there too, not double-counted as a separate finding.
    **Next step:** a small, cheap, purely synthetic batch (1/2/3 self-
    closing routines in one program, no firmware variable involved this
    time) would isolate this cleanly without needing more real-firmware
    captures at all — can be generated without anything from James.
