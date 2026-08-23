# Open Build / Conversion Errors

Every generated file that currently shows an L5X→ACD conversion failure
or a Studio 5000 build/verify error, and doesn't yet have a confirmed fix
sitting in the manifest awaiting recapture. James, 2026-08-25: high
priority to work through while l5x→acd conversion is running — reply
inline under each item with the real error code/description from Studio
5000's own error log if you have it (or can grab it on the next capture
pass), and I'll wire the fix into the generator.

Two different failure stages, kept separate below:
- **L5X→ACD conversion failure** — the `l5x2acd` tool couldn't even open
  the project (fails before any build/verify step runs).
- **Build/verify error** — the project opened fine, but Studio 5000's own
  verify step reported N errors on import/build.

Sourced from `samples/convert_log.csv` (latest attempt per file only —
older superseded failures for the same file aren't included) and
`samples/manifest.csv`'s `error_count` column.

## 1. L5X→ACD conversion failure — genuinely unexplained, zero data

**`samples/generated/tags/stringoverhead_namelen32_n050.L5X`**
- Part of the original built-in STRING name-length cross-check
  (`stringoverhead_namelen{04,08,16,32,40}_n050`) — the other 4 name
  lengths (4/8/16/40) all captured cleanly with real data; **32 is the
  only one that failed to even open**, and was never retried. No real
  Capacity data exists for this file at all.
- Reported error: `OperationFailedException: XMLSrv_E_IMPORT_ABORTED_NO_CHANGES
  - The Import was cancelled due to errors. No changes were made to the
  open project. See error log.` — this is the l5x2acd tool's own wrapper
  message, not Studio 5000's actual import error log (which the tool
  doesn't currently capture/forward). **I don't have the real underlying
  error** — if your capture tooling's own log ("See error log") has more
  detail from that run, or if you re-run the conversion and can grab
  Studio 5000's actual error dialog/log text, that would tell us whether
  this is a real name-length-32-specific issue or an unrelated one-off
  (stale file, transient tool error, etc).
- File content is otherwise identical in structure to the 4 name lengths
  that worked (same generator, `gen_string_tagoverhead.py`
  `group_namelen`) — nothing structurally different stands out from a
  read of the L5X itself.

## 2. Build/verify errors — never previously investigated

**`samples/generated/axis/axis_aoi_inout_1_instance.L5X`** — 2 errors
- Real `AXIS_CIP_DRIVE` tag + an AOI (`DriveAxisTest`) with a BOOL Input
  param and an InOut `AXIS_CIP_DRIVE` param, called from a rung:
  `DriveAxisTest(DriveAxisInst,FaultResetVal,Axis_Cip_Drive);`
- The project still opened and reported a real Capacity number (43,680)
  despite the 2 errors — so whatever's wrong didn't block conversion,
  only flagged during verify.
- No error text captured (`notes`/`message_value` columns are empty) —
  only the count. This is a real gap in what the capture tooling logs;
  if your side has access to Studio 5000's actual error list for this
  import, that's exactly what's needed here.

**`samples/generated/axis/axis_full_combo.L5X`** — 2 errors
- Same real `AXIS_CIP_DRIVE` tag + a `ts_CIPAxis`-shaped composite UDT (1
  instance) + the same AOI-with-InOut-axis call, all together — an
  additivity check against the individually-confirmed axis constants.
- Same signature as the file above: opened fine (Capacity=44,792
  reported), 2 errors, no error text captured. Given it shares the exact
  same AOI-InOut-axis call as `axis_aoi_inout_1_instance` above, this is
  likely the *same* underlying error occurring twice (once per file), not
  two different problems — but that's unconfirmed without the actual
  error text from either one.

## 3. Build/verify errors — already have a working theory, still open

**`motioninstr_mam_n00010` / `_n00100`, `motioninstr_maj_n00010` /
`_n00100`, `motioninstr_mas_n00010` / `_n00100`, `motioninstr_mrp_n00010`
/ `_n00100`** — `error_count` exactly equals rung count for all 8 (10 and
100, respectively) — every single rung failed.
- Current theory: these 4 mnemonics use the same documented 2-operand
  `(Axis,MotionInstruction)` call shape already confirmed working for
  MAH/MSO/MAFR/MASR/MDW/MASD, but real Studio 5000 rejects it for MAM/
  MAJ/MAS/MRP specifically. If you have the real error text/code from
  these 4 (or a real corpus example showing the correct call shape for
  any of them), that would let this get fixed rather than staying a
  confirmed-but-unexplained negative result.

**`instrfirst_mapc_x10`** — 20 errors (2/rung × 10 rungs)
- Root-caused 2026-08-25 (not a mystery any more, but the ORIGINAL file
  still shows the error and hasn't been superseded by a confirmed-good
  capture yet): the file never declared the `Axis_Cip_Drive` tag it
  referenced, and reused the same axis tag for both slave/master
  positions when real corpus MAPC calls always use two distinct axis
  tags. Fixed in `instrfirst_mapc_v2`/`_v2_x10` (generated, awaiting
  capture) — if you have the actual Studio 5000 error text from the
  original `instrfirst_mapc_x10` capture, it would be good confirmation
  that "undeclared tag" was really the error raised (vs. something else
  entirely), but this one isn't blocking on that to proceed.

## 4. Build/verify error — resolved, not actually a bug

**`instrfirst_crout_x10`** — 80 errors (8/rung × 10 rungs)
- Resolved 2026-08-25: CROUT is a Safety-only instruction (needs a
  GuardLogix CPU), and this project's test corpus is all standard
  controllers. Not a generator bug, nothing to fix — included here only
  for completeness of "every file with a nonzero error_count." If you
  have the real error code Studio 5000 raised for this one, it's still
  worth a line since it'd confirm the Safety-CPU explanation directly
  (should be something like an instruction-not-supported-on-this-
  controller-type error), but no action is planned regardless.
