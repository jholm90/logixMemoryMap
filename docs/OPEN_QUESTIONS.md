# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md` — this file stays scannable, open items only.
Items marked **[test built]** don't need a decision from James — a
generator already covers them, just waiting on the next capture batch.

1. **OQ-CUSTOMSTRINGDEF (new, 2026-08-22).** Custom STRING types
   (`Family="StringFamily"`) need their own one-time definition-cost
   constant, distinct from the ordinary UDT-definition formula (which
   doesn't apply to them — confirmed by removing it and re-checking real
   data). Every real `customstring_*` manifest row now under-predicts by a
   fairly consistent ~204-208 blocks once the wrong formula was removed.
   Real data already exists (7 points, `customstring_len*`) — this is a
   re-analysis of existing data, not a new capture, just hasn't been done
   yet.

2. **OQ-AXISDEEP [test built].** CIP/virtual axis, used everywhere in real
   programs, 0.01%-tolerance target. `gen_axis_composite.py` covers the
   `ts_CIPAxis`-shaped composite UDT + AOI-with-InOut-axis call + full
   combo. Awaiting capture.

3. **OQ-MIXEDUDT [test built].** Realistic messy/nested UDTs (not
   homogeneous arrays) — `gen_axis_composite.py`'s composite UDT covers
   this too. Awaiting capture.

4. **OQ-ARRAYPACK [test built].** Does a UDT's total size round to a 32-bit
   boundary? `gen_arraypack_boolarray.py` group C. Awaiting capture.

5. **OQ-BOOLARRAY [test built].** Array-of-BOOL sizing, isolated.
   `gen_arraypack_boolarray.py` group A. Awaiting capture.

6. **OQ-AOIBOOLPACK [test built].** Clean re-test, same 20-param total,
   BOOL grouped vs alternating. `gen_aoi_boolpack_clean.py`. Awaiting
   capture.

7. **OQ-UDTARRAYALIGN [test built].** Array of an already-tight UDT — any
   per-element padding? `gen_arraypack_boolarray.py` group B. Awaiting
   capture.

8. **OQ-TAGSCOPE [test built].** Program tag `Usage="Local"` vs `"Public"`
   — cost difference? `gen_tagscope_alias.py` group A. Awaiting capture.

9. **OQ-ALIASSIZE [test built].** Alias tag cost at 1/10/1000 scale.
   `gen_tagscope_alias.py` group B. Awaiting capture.

10. **OQ-CMPCPTLAYOUT [test built, new 2026-08-22, extended same day].**
   Operator/layout/optimization sweep for CPT and CMP (`tag**tag` vs
   `tag*tag` vs `tag-tag`, a 6-operand chain, same-tag-vs-distinct-tag and
   redundant-literal dedup probes, compound boolean expressions) — plus,
   per James's follow-up ("are you testing these with tags only? You might
   want to test with float/decimal constants as well"), an integer-literal
   and float-literal operand variant for every operator, both CPT and CMP,
   against the existing tag-vs-tag baseline. `gen_cmpcpt_layout.py`.
   Awaiting capture.

11. **OQ-PREDEFINED [test built].** Rockwell's own literature site is
    blocked by this session's network proxy, but the real corpus had
    everything needed. `gen_motion_predefined.py`: MOTION_INSTRUCTION (real
    16-member shape from `BAI10048_TrimmerTally_20250704.L5X`, 1/5/50-tag
    sweep) and CAM_PROFILE (real 20-element array from
    `CMU_2025_10_14r00.L5X`, 1/5/20/50-element sweep, built from real
    captured row data — the visible Decorated shape only exposes 1 of the
    14 real per-element L5K fields, confirming your "voodoo... hides stuff
    not visible in the tag browser" call, so there's no way to size this
    one structurally — needs a pure empirical constant same as Axis).
    `CAM`/`MOTION_GROUP` (the group wrapper, not per-axis config) still
    untested. Awaiting capture.

12. **OQ-XPROGREF [test built].** Real Logix has no direct cross-program
    tag-addressing syntax in logic (confirmed: searched all 47 real corpus
    files, no `Program:Tag`-style reference exists anywhere in rung Text).
    The real mechanism is what you described earlier — a Controller-scoped
    global with each program declaring its own Local alias to it. Built
    `gen_xprogref.py`: single-program alias baseline vs two programs each
    aliasing the same global, same 1000-rung XIC/OTE pattern, comparable
    directly against the confirmed 20-blocks/rung XIC weight. Needed a new
    `build_l5x(extra_programs_xml=...)` wrapper hook for a second Program.
    Awaiting capture.

13. **Motion instructions [test built]** (MAM/MAJ/MAH/MAS/MSO/MRP).
    `gen_motion_instructions.py` — MAH/MSO's 2-operand call syntax is
    corpus-confirmed, the rest use the same documented signature but
    aren't independently confirmed for that exact mnemonic. MAPC/MCCP
    camming skipped, no real call-syntax reference found. Awaiting
    capture.

14. **Per-Task overhead [test built].** `gen_task_overhead.py` — 2nd/3rd
    Task, isolating pure Task/Program scaffolding cost from logic content.
    Also the only way to disambiguate whether the logic-sizing engine's
    `fixed_base_per_routine` is really per-routine, per-program, or
    per-task (every calibration sample had exactly one of each). Awaiting
    capture.

15. **Indirect addressing overhead [test built, extended 2026-08-22].**
    `gen_indirect_addressing.py` — direct vs. tag-driven array index, plus
    (James: "Does tag[idx+1] take up the same space as tag[Idx]?") a third
    variant with an arithmetic offset inside the index. Same
    instruction/count throughout. Awaiting capture.
