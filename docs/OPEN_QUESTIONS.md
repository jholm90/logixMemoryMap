# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md` — this file stays scannable, open items only.

1. **OQ-AXISDEEP (elevated priority, 2026-08-22).** James: CIP/virtual axis
   structures are used *everywhere* in real programs and this needs
   0.01%-tolerance accuracy, not the single-sample-per-type coverage that
   exists today. Confirmed in the real corpus: axis usage is never the raw
   `AXIS_CIP_DRIVE` predefined type alone — it's wrapped in custom UDTs like
   `ts_CIPAxis` (found in `BaillieLeitchField_Edger_20260812_r00.L5X` and
   `SJ_Gormley_20251112_r02.L5X`), which nests a real AOI (`DriveAxis`,
   tagged "Motion Control AOI") plus other nested UDTs (`AutoSpeeds`,
   `udtServo`) plus a hidden-bit-backed BOOL plus a STRING member, on top of
   the axis tag itself. Needs: (a) many more real data points per axis type,
   not one; (b) a combined CIP+Virtual file (subsumes old OQ-AXISCOMBO);
   (c) a direct test of an `AXIS_CIP_DRIVE`-wrapping composite UDT shaped
   like `ts_CIPAxis` to validate the nested-AOI-in-UDT-with-axis-member
   composition math specifically, since axis structures are structurally
   unlike anything else tested (flat `AxisParameters` attribute list, not
   Members/StructureMember).
   *(AXIS_CIP_DRIVE/AXIS_VIRTUAL/AXIS_SERVO/COORDINATE_SYSTEM single-point
   values are already resolved, see RESOLVED_QUESTIONS.md — this item is
   about accuracy/coverage, not first discovery.)*

2. **OQ-MIXEDUDT (new, 2026-08-22, reopens/expands OQ-LARGEMIXED).** James:
   "majority of our in use programs are not bool[1000] but are mixed and
   garbled udts" — the 3 existing composite-file validations (0.3-2.6%
   accuracy) used artificial homogeneous-ish compositions, not real-shaped
   messy UDTs. Need dedicated tests matching what's actually in the corpus:
   UDTs nesting AOIs, UDTs nesting other UDTs several levels deep, hidden
   bit-backed BOOL members mixed with STRING/DINT/nested-struct members in
   one type (`ts_CIPAxis` above is a real example of exactly this shape).
   Goal: confirm the composable formulas still hold at real-world
   messiness, not just in controlled homogeneous sweeps.

3. **L5X version cross-check** (spin-off of OQ-L5XVERSION). v20/v30 schema
   differences vs the primary v35 target are completely unvalidated — no
   sample data for either version. Revisit if a v20/v30 project shows up in
   the real corpus.

4. **OQ-ARRAYPACK.** Does a UDT's total size round up to a 32-bit boundary?
   Still open.

5. **OQ-BOOLARRAY.** Strong indirect evidence, no clean isolated test yet —
   need a dedicated real-data test for array-of-BOOL sizing specifically.

6. **OQ-PREDEFINED.** Motion/cam structures other than AXIS_* — MOTION_
   INSTRUCTION, CAM_PROFILE, CAM, MOTION_GROUP, etc. — still unresolved.

7. **OQ-AOIINSTANCE.** Can an AOI instance be inline/anonymous (no backing
   tag)? Unclear if that's even possible in real Logix. Untested.

8. **OQ-AOIBOOLPACK.** Real data collected but confounded — the
   interspersed-BOOL comparison file also added 20 extra DINT params vs the
   consecutive-BOOL file, so the raw delta isn't a clean isolation of
   packing behavior. Needs a same-total-param-count re-test.

9. **OQ-ALARMPROPBYTES.** Memory cost of extended tag properties (alarm
   config, etc.) — untested.

10. **OQ-JSRSHARED.** Does a JSR'd subroutine's compiled logic get counted
    once (shared) or duplicated per call site? Pending James's current
    244-file logic-sweep capture run.

11. **OQ-LOGICVISIBILITY.** The big one: does the Capacity tab reflect
    compiled logic size at all, and if so how? Only 2 logic samples existed
    before the 244-file sweep, both showed zero Capacity movement — method
    validity for logic is still unconfirmed. Pending James's current run.

12. **OQ-UDTARRAYALIGN.** Does an array of an already-tight (4/8-byte
    aligned) UDT get any extra per-element padding? Needs an isolating test.

13. **OQ-TAGSCOPE.** Program-scoped tag `Usage="Local"` vs `Usage="Public"`
    — does scope affect storage cost? Real XML shape now confirmed, test
    not yet built.

14. **OQ-ALIASSIZE.** Cost of an Alias tag at scale (1/10/1000 aliases) —
    real XML shape now confirmed (self-closed `TagType="Alias"
    AliasFor="..."`), test not yet built.

15. **OQ-XPROGREF.** Cross-program tag reference — any logic-size cost
    beyond ordinary operand cost? Parked, Phase 4 scope.

16. **Motion instructions** (MAM/MAJ/MAH/MAS/MSO/MRP/MAPC/MCCP). Deferred to
    Phase 4d — needs real Axis tag setup before these can be tested.
