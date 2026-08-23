# Open Build / Conversion Errors

James, 2026-08-25 (first pass): high priority to work through while
l5x→acd conversion is running. Every item from the first pass has now
either been root-caused and fixed by James's own explanations, or
confirmed as a scope decision (Safety) rather than a bug. **Nothing left
needs an error code from you right now** — every fix below is generated,
lint-clean, and just needs a recapture to confirm. New items will be added
here the moment anything else shows up as FAILED/nonzero `error_count`.

Two different failure stages, kept separate below:
- **L5X→ACD conversion failure** — the `l5x2acd` tool couldn't even open
  the project (fails before any build/verify step runs).
- **Build/verify error** — the project opened fine, but Studio 5000's own
  verify step reported N errors on import/build.

## All fixed, awaiting recapture

**`stringoverhead_namelen32_n050.L5X`** — L5X→ACD conversion failure
- James: "looks like you have a double underscore and that is forbidden."
- Root cause confirmed: the name-length padding filler
  (`"_LONGNAME" * k`, truncated to hit an exact target length) happened to
  end in `_` right where it abuts the tag's own `_NN` numeric suffix, at
  `pad_needed mod 9 == 1` — 32 is the only one of the 5 name lengths
  tested (4/8/16/32/40) where that remainder occurs.
- Fixed in 3 places sharing the same filler-truncation pattern (`cli.py`'s
  `_padded_tag_name`, `gen_string_tagoverhead.py` and
  `gen_string_batch2.py`'s namelen groups) — all now guard against a
  trailing `_`, swapping it for a non-underscore character so the exact
  requested length is still hit. Regenerated, lint-clean.

**`axis_aoi_inout_1_instance.L5X`** / **`axis_full_combo.L5X`** —
build/verify errors (2 each)
- James: "your AOI has the tag name and the inout as required/visible,
  but the calling routine has tagName,FaultResetVal,Axis_Cip_Drive. the
  3rd tag has no where to go. you need to have as many tags on the
  calling routine as required parameters in the aoi definition."
- Root cause confirmed: the AOI's BOOL Input param (`FaultReset`) was
  declared with `Required=False/Visible=False` (hidden — real semantics:
  no slot on the calling rung at all), but the rung text wired
  `FaultResetVal` into it anyway.
- Fixed by marking `FaultReset` `Required=True/Visible=True` in
  `gen_axis_composite.py` (both files share the exact same bug, both
  fixed together) — keeps the call-site wiring as originally intended.
  Regenerated, lint-clean; stale `actual_bytes`/`error_count` from the
  broken version cleared from the manifest so they don't read as current.

**`motioninstr_mam_n00010`/`_n00100`, `motioninstr_maj_n00010`/`_n00100`,
`motioninstr_mas_n00010`/`_n00100`, `motioninstr_mrp_n00010`/`_n00100`**
(8 files) — build/verify errors, `error_count` == rung count (every rung
failed)
- James: "You need to put parameters in for motion instructions. right
  now you are calling MAM(Axis_Cip_Drive,MotionInstr1) but you need to
  have all of the parameters populated... See samples for details."
- Root cause confirmed: the bare 2-operand call these 4 used is MAH/MSO's
  own real shape, not theirs. Reading the real corpus directly confirmed
  four genuinely different real operand counts: MAM=20, MAJ=17, MAS=9,
  MRP=5.
- Fixed in `gen_motion_instructions.py`: MAM uses James's own corrected
  template verbatim; MAJ/MAS/MRP built as position-for-position
  transplants from one real corpus example each (same method as the MAPC
  fix below), real keywords/literals kept verbatim, only tag names
  substituted. MAH/MSO's own call is untouched. All 12 files regenerated,
  lint-clean, stale error data cleared from the manifest.

**`instrfirst_mapc_x10`** — 20 errors (2/rung × 10 rungs)
- James: "you forgot to make the tag for the axis. also you need to have
  a unique tag for master/slave they cannot cam to itself. duh." — matches
  the root cause found independently: `Axis_Cip_Drive` was never declared
  as a tag in the file, and the same axis tag was reused for both
  slave/master. James also clarified the axis-type constraint is looser
  than first assumed: "Mapc can use two axis of any type (virtual
  master/virtual slave is ok)" — just needs two distinct tags, not a
  required CIP-Drive/Virtual pairing.
- Fixed in `instrfirst_mapc_v2`/`_v2_x10` (generated, lint-clean,
  awaiting capture). Original buggy files kept for the audit trail.

## Resolved, not a bug

**`instrfirst_crout_x10`** — 80 errors (8/rung × 10 rungs)
- James: "you fixed it -- needs a safety processor." Confirmed: CROUT is
  a Safety-only instruction (GuardLogix CPU required), this project's
  test corpus is all standard controllers. Reclassified OUT OF SCOPE
  alongside DCS. Nothing to fix, nothing to retest on a standard
  controller.
