# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md`. One line each here — full derivation is in
the matching footnote at the bottom, not inline.

1. **OQ-INSTRFIRSTPASS** — 34/36 instruction weights confirmed and wired.
   SCP/FBC/PID deprioritized (no 2nd real example to test against);
   effort redirected to safety work per James.[^instrfirstpass]

2. **OQ-BASELINE-PROCFW** — partially wired 2026-08-29. Firmware-version
   (v30/v31/v32/v33), 5069-safety-capable-model, and (found the same day
   via a full manifest.csv audit) 1769-series per-catalog baseline deltas
   are now real, confirmed, and wired into `report.py`/`memory_model.yaml`
   — validated against all 50 real (untainted) `fw_catalog_matrix` rows
   plus 8 real 1769-series and 2 more `fw_baseline` points, every one now
   predicts within 32 bytes (was off by up to 80,832 for 1769). Still
   genuinely open: v38 (only real capture is WINDOW-TITLE-MISMATCH-
   flagged, awaiting the batch script's automatic retry), v36/v37 (no real
   sample at all), and any 1769 catalog beyond the 9 exact ProcessorType
   strings now confirmed (real data shows a single suffix character
   changes the value by 13,000+ bytes, so unconfirmed catalogs correctly
   stay unmodeled rather than guessed). L7x/L8xES catalogs in the matrix
   still await their own
   capture.[^baseline]

3. **OQ-CMPCPTLAYOUT** — down to one thread. Uniform, T1+T2, T1T3/T2T3,
   and (as of 2026-08-29) the all-3-tier mix are ALL solved and wired,
   confirmed exact on every real data point on file. Only the REAL-
   operand/float-literal interaction remains open, and it's now a harder
   problem than "assumed linear, awaiting more points" — real new data
   shows it's genuinely NOT monotonic in operand count, ruling out any
   simple per-count model.[^cmpcpt]

4. **OQ-AOIDEF** — CLOSED 2026-08-30. Required/Visible flags closed (no
   real effect). AOI type-name-length step formula wired and verified
   7/7 exact, plus a real off-by-one bucket-boundary bug found and fixed
   via cross-validation against two same-shape files that only differed by
   name length (len=19 was landing one bucket too high).[^aoidef]

4b. **OQ-AOIBOOLPACK-PAIRING** — new 2026-08-30, split off OQ-AOIDEF's old
    "BOOL-array-packing-boundary" thread once its 27 already-captured
    points got reconciled. The `aoi_array` per-instance formula was tagged
    KNOWN ("confirmed exact... 15 real points") but that claim was only
    ever checked at 3 widely-spaced instance counts per shape (n=1/10/25)
    — real dense data disproves it. Confidence downgraded to FITTED.
    Genuinely open, new dense/isolating test files generated (not yet
    captured).[^aoiboolpackpairing]

5. **OQ-PREDEFINED — CLOSED for all 195 known types, corrected 2026-08-29.**
   James's own conversion+capture pipeline ran the full 184-file
   `gen_predefined_probe.py` blank-tag discovery batch; 174 imported clean
   and got a real Capacity delta. Wired all 174 into `memory_model.yaml`
   in one batch (ASSUMED, n=1 real capture each). MESSAGE (688 bytes) and
   ALARM_DIGITAL (973 bytes) — the two longest-standing genuinely-blocked
   types — are now resolved with real totals. SFC_STOP (wired 2026-08-28
   from real L5K data) matched the new real capture EXACTLY (0 residual),
   independently confirming the derivation method itself, not just that
   one type. **`CONFIGURABLE_ROUT` was WRONGLY documented here as
   unmodeled** — its real capture (`predefprobe_configurable_rout`,
   actual 18,264) was on file in manifest.csv the whole time and IS wired
   (52 bytes, same value as `BUS_OBJ`'s real capture, plausible for a
   small structure, not a data-entry error — cross-checked directly).
   The commit that wired the other 174 said "CONFIGURABLE_ROUT remains
   unmodeled" while its own diff actually included it correctly — the
   prose was wrong, the code wasn't. James is also right that
   `CONFIGURABLE_ROUT` is very likely Safety-family (its name root
   matches `CROUT`, the already-confirmed Safety-only instruction
   requiring a GuardLogix/Safety CPU — see RESOLVED_QUESTIONS.md
   OQ-CROUT-MAPC-BUILDFAIL) — added to the Safety-Instructions-family
   list below, subject to the same pending Safety-scope inclusion
   decision as DCI_STOP and the rest of that list. See [^predefined] for
   the full derivation method and the complete per-type real-value table.

6. **OQ-AOIARRAYDIMENSION** — real parser bug fixed 2026-08-27:
   `<Parameter>`/`<LocalTag>` array size is a "Dimensions" (plural)
   attribute, not "Dimension" (singular, correct only for a plain UDT
   `<Member>`) — was silently sizing every array-dimensioned AOI local/
   param as a scalar. 5 existing test files need a fresh real capture;
   their prior "confirmed" numbers almost certainly tested scalar
   behavior by coincidence, not the array behavior they were meant
   to.[^aoiarraydimension]

7. **OQ-MODULEIO** — mostly closed 2026-08-29. 126 real module captures
   were sitting unreconciled in manifest.csv; 51 catalogs now have a real
   per-catalog overhead value (exact-match rate on real data went from
   1/126 to 54/126). Two real sub-threads remain, both needing
   architecture work not more generation: multi-module marginal cost
   (adding a 2nd/3rd of the same module doesn't cost the same as the
   1st), and a handful of catalogs with real connection-variant-dependent
   overhead.[^moduleio]

8. **OQ-BRANCHDEPTH** — confirmed real (branch structure costs memory
   beyond leg instructions). Two independent test batches — leg-count
   width and staggered/nested depth — await capture.[^branchdepth]

9. **OQ-LEGACYNETOVERHEAD** — reminder flag only. No real corpus, no
   capture data, nothing to size against yet.

10. **OQ-JSRPARAMCOST** — reopened 2026-08-29 for one small residual.
    Output/return-param call-site cost is now wired and confirmed
    (see RESOLVED_QUESTIONS.md). The callee's own one-time `A(n)`
    Parameters-block cost almost certainly ALSO needs an output-param
    term (real Parameters blocks include both Input and Output entries)
    — `jsr_multiret_n04` still off by +332 after the call-site fix, too
    small relative to a 1-distinct-target sample to isolate from noise.
    Needs a dedicated small file (2+ distinct targets with different
    output-param counts, input count held constant) to isolate A(n)'s
    real output term cleanly.

11. **OQ-EVENTTRIGGER** — new, real. task_extra (+700) was derived only
    from CONTINUOUS+PERIODIC tasks; EVENT-type tasks are completely
    untested, and so is trigger-source (Axis Watch vs. EVENT-instruction)
    within EVENT. Two files built, awaiting capture.[^eventtrigger]

---

[^instrfirstpass]: CROUT (safety-only) and MAPC resolved separately
(RESOLVED_QUESTIONS.md). Still untested: SCP (no 2nd real example), FBC
(0 real examples), PID (0 real examples, needs its own structure tag) —
deprioritized 2026-08-25 (James: "move to safety related feature"), no
point manufacturing synthetic points with nothing real to validate
against. Also open, low priority: a flat **+12** byte gap (corrected from
a misrecorded +6) across all 64 clean `instrfirst_*` files, independent
of instruction and rung count — narrowed to an interaction effect among
the 7 distinct tag types the shared pool declares (each individually
confirmed exact on its own; likely a per-distinct-type registry cost).
Needs one reduced-pool variant to isolate which type, ~0.06% of file
total.

[^baseline]: `empty_project_baseline=13,296` only confirmed for
1756-L81E/fw 35.05 — real variance found so far: firmware 30→33 adds a
real, distinct step (29,272 → 32,376 at fw33); 1769-series runs
69,600-98,944, far above the flat prediction; 5069-L306ER family sits at
18,144 base. An "M motion processor costs more" hypothesis was tested and
answered NO (2 identical base-vs-M pairs). The 8 files previously flagged
"contaminated" (named `SafetyTask`/`SafetyProgram` but carrying no real
safety marker — no `Class="Safety"`, empty `<SafetyInfo/>`) are now
corrected and included: subtracting the known task/program/routine shell
overhead (1,456) gives a clean baseline of 18,112 for 4 of them (exact
match to the already-confirmed reference point) and 18,120-18,144 for the
other 4 (small real per-model variance, not error) — see `manifest.csv`
notes on `v35_l82e/l83e/l84e/l85e/l3100erm/l320er/l330er/l340er`. 20 files
remain awaiting capture.

**Full catalog x firmware matrix built 2026-08-25, expanded same day**
(`gen_fw_catalog_matrix.py`, 232 files, `fw_catalog_matrix` category).
Every real catalog number sourced from Rockwell literature/distributor
documentation via web search (not guessed), cross-checked against this
project's own already-confirmed ProductCodes before generating anything:
29 catalogs × 8 firmware versions (31-38, v30 excluded — SDK confirmed
unable to build it at all):
- 5× ControlLogix 5580 (1756-L8x), 14× CompactLogix 5380 (5069-Lxxx) —
  original 152-file batch.
- 5× ControlLogix 5570 (1756-L7x, L71/L72/L75 real ProductCode 92/93/96,
  L73/L74 INFERRED 94/95 from the sequential pattern — flagged per-file).
- 5× GuardLogix 5580 safety-rated (1756-L8xES, L81ES real ProductCode 164,
  L82ES-L85ES INFERRED 165-168 from the single confirmed ES/E pairing —
  flagged per-file). Each gets a real `SafetyTask`/`SafetyProgram` pair
  with `Class="Safety"` on both elements (the real marker, confirmed
  against Gormley/Bender corpus — NOT the element name) plus a populated
  `<SafetyInfo SafetyLevel="SIL2/PLd" .../>`.

Firmware attribute shape (SoftwareRevision, AutoDiagsEnabled/
WebServerEnabled presence, v38's DataExchangeId) is real per version,
confirmed from the existing v31-35/v38 samples. **v36/v37 removed
entirely 2026-08-28** (James: not asked for, told to leave out) — they
were the only two ASSUMED/unconfirmed firmware majors in the table (no
real v36/v37 L5X sample ever existed in this project); the batch is now
174 files (6 firmware x 29 catalogs), all on real-confirmed firmware
attribute shapes. Files sorted `fwmatrix_v{NN}_{catalog}` so a plain
directory listing groups all of v31 together, then v32, etc.

**Real, systemic structural bug found and fixed 2026-08-28** (James:
"your controller firmware tests are really really bad. very high failure
rate. you obviously have missed something" — followed by a fresh real
Studio 5000 export of 1756-L71 sent for direct comparison; the exact same
evidence was ALSO already sitting unused in `samples/local/
L7_v21_Sample.L5X`, meaning this generator was built without ever
cross-checking against corpus evidence that was already available).
ControlLogix 5570 (1756-L7x) has NO embedded Ethernet interface on the
CPU module itself — real shape is exactly ONE Local Port (`Type="ICP"`,
`Bus Size="4"`, not the L8x-style 17) and no top-level `<EthernetPorts>`
element at all. This generator applied the L8x shape (second Ethernet
Port + EthernetPorts element describing a port that doesn't physically
exist) to all 5 L7x catalogs across every firmware version — a real
structural error, not a cosmetic one, plausible root cause for a large
share of the reported high failure rate. Fixed: `_local_ports_xml` now
branches for `_L7X_PRODUCT_CODES`, and the top-level `<EthernetPorts>`
is conditionally omitted for that family. Only L71 is directly
corpus-confirmed; L72-L75 are the same ControlLogix 5570 physical form
factor so treated identically, not independently confirmed per-catalog.
Also added two real Controller/RedundancyInfo attributes confirmed by
both real references (`TimeSlice="20" ShareUnusedTimeSlice="1"`,
`IOMemoryPadPercentage="90" DataTablePadPercentage="50"`) — `build_l5x`'s
own already-working template omits both and still imports fine across
~1300 tested files, so these are almost certainly Studio-5000-optional
rather than the actual failure cause, but added for fidelity now that
real values exist. All 174 files regenerated — awaiting real
re-conversion to confirm the L7x fix actually resolves the failure rate,
not just structurally plausible like the module fixes earlier today.

**Sourced but deliberately NOT generated, real ProductCode still
unconfirmed:** ControlLogix 5590 (1756-L9x, "TS" suffix — L902TS/L905TS/
L908TS/L915TS/L925TS/L950TS/L980TS) — a brand-new family (FactoryTalk
Design Studio only added support in v2.03, Nov 2025) with zero real L5X
corpus examples anywhere, and zero real ProductCode/Module-signature data
found anywhere publicly accessible despite thorough web search (Rockwell's
own domains are all blocked by this environment's egress proxy; even
distributor/3rd-party sites carry catalog numbers but never the internal
ProductCode). James asked for one L9 sample minimum v38 — still blocked on
this, needs either a real sample from him or explicit sign-off on a
flagged best-effort placeholder. CompactLogix 5480 (5069-L4xx process
controllers — L430ERMW/L450ERMW/L4100ERMW/L4200ERMW) — also zero real
corpus examples, not yet requested by James. Building either without a
real sample risks fabricating a ProductCode/Module shape that fails
Studio 5000 import outright.

**1769-series real per-catalog baseline + v30 wired 2026-08-29** (found
during a full manifest.csv audit, James: "make another in-depth pass" —
these 9 real points had been sitting in the `fw_baseline` category,
MANUAL ENTRY, since before this project even had a `firmware_baseline_
delta` mechanism to wire them into, and were never revisited). 8 real
1769-series (CompactLogix 5370) blank-baseline captures, all v35.05 —
real total baseline runs 69,600-98,944 against a flat 18,112 predicted
for everything else, previously documented as "not modeled at all."
Wired as `catalog_baseline_delta` (memory_model.yaml), keyed by the
EXACT `ProcessorType` string (not prefix/suffix-matched like
`safety_capable_baseline_delta`) — real data shows a single expansion-
module suffix character changes the value by 13,000+ bytes
(`1769-L24ER-QB1B`=67,160 vs `1769-L24ER-QBFC1B`=80,832), so any
catalog beyond the 9 exact strings now confirmed correctly stays
unmodeled. Firmware-independence assumed (same convention as
`firmware_baseline_delta`) but genuinely unconfirmed — zero 1769 data
exists at any firmware besides v35. Separately, `l81_v30` (real MANUAL
ENTRY point, James read Capacity directly off a real v30 controller —
this project's SDK can't build/convert v30 exports at all) added to
`firmware_baseline_delta` at +11,160, ASSUMED confidence (single point).
All 29 real `fw_baseline`-category rows now checked: 17 exact, 6 within
the small per-file noise band (<=16 bytes), 3 already-documented small
per-model variance (+32 bytes, `l306er`/`l306erm`/`l320er`), and 3
already-documented Safety-Task-bearing-file gap (`l306erms2`/`erms3`/
`ers2`, -1,424 — real Safety Task/Program content this tool doesn't
size, see this same footnote's `v35_l306erms2`/`v35_l306erms3` note
further below for the root cause).

[^cmpcpt]: T1T3/T2T3 wired 2026-08-25: real capture data existed
unreconciled since 2026-08-24; `pow_tier_mix_base=160,
pow_tier_mix_per_operator=64` is exact at 4 of 5 points, and T1T3/T2T3
give IDENTICAL real bytes at every point (T1-vs-T2 stops mattering once
POW is present). See `sizing/constants.py` `CptExpressionModel.cost_for`.
**All-3-tier mixes: CLOSED 2026-08-29.** The 3
`cptmix_threetier_rem2_n06/n09/n12` files (plus the 4 disentangle files
below) had real capture data from 2026-08-27 sitting unreconciled in
manifest.csv this whole time — found and fixed the same day James pushed
on why this wasn't closed already. The earlier `44*T1-116*T2+76*T3+72`
attempt was wrong (not just "misses n=15" — checked directly, it doesn't
reproduce the n=3/5/8/10/11 points it was supposedly fit from either).
Correct formula, confirmed 0 residual across ALL 9 real all-3-tier points
on file (operator counts 4-14): `base_by_remainder[operator_count % 3] +
4 * pow_operand_count`, `base_by_remainder = {0: 72, 1: 116, 2: 144}`.
remainder=1 exact at 3/3 points, remainder=2 exact at 4/4 points
(including the original n=15 outlier AND the 3 new rem2 probe files —
confirms the remainder-2 trigger hypothesis exactly, and that it's NOT a
flat bonus, it scales at +4/POW-operand same as the other two remainder
classes). remainder=0 rests on a single point (n=10) — same slope,
extrapolated base, one point short of independent confirmation. Wired in
`sizing/constants.py` `CptExpressionModel.cost_for` / `memory_model.yaml`
cpt_expression.

**REAL-operand/float-literal interaction: investigated 2026-08-29, still
open — now for a more specific and more interesting reason than "not
enough points."** The 4 disentangle files' real data (also from
2026-08-27, also unreconciled) rules out any simple per-operand-count
model: extra cost at R=1 REAL operand (276) is HIGHER than at R=2 (236),
and the same pattern holds for float literals (F=1: 280, F=2: 244) — going
from 1 to 2 of the same factor makes the file SMALLER, not bigger. That's
not sub-linear/saturating, it's genuinely non-monotonic, and it holds
identically for both factors, which rules out coincidence/noise. No
formula wired — CLAUDE.md's ground-truth discipline means not force-
fitting a linear or bilinear surface onto data that demonstrably isn't
one. Real hypothesis worth testing next: cost may track the number of
DINT→REAL type-PROMOTION points in the expression tree (a structural
property of where mixed-type sub-expressions meet), not the raw REAL-
operand/float-literal COUNT — needs files that vary operand/literal
POSITION at a fixed count, not just count alone. Additive fallback (no
surcharge) stays the honest default. Full data: 9 total points across the
`cptmix_stacked_*` (5, already on file 2026-08-24) and `cptmix_
disentangle_*` (4, captured 2026-08-27) sample sets.

**Position-probe files built 2026-08-29** (`gen_cpt_mixed_operators.py`
`group_real_float_position_probe`, James: "generate new tests... they
have been dragging on for far too long" -- fair, the hypothesis above had
sat undertested since it was written). 4 new files, all built/lint-clean/
zero engine errors, awaiting real capture: `cptmix_real1_pos_first`/
`cptmix_real1_pos_last` (1 REAL operand at slot 1 vs slot 6 of the same
6-operand T1+T2 shape, "middle" position already on file as
`cptmix_disentangle_real1_noliteral`) and `cptmix_float1_pos_first`/
`cptmix_float1_pos_divisor` (1 float literal at slot 1 vs the divisor
slot, "last" position already on file as `cptmix_disentangle_
float1_noreal`). Once captured: if all 3 positions per factor land on the
same real delta, position is ruled out (points back to an unexplained
pure-count effect); if they differ, the pattern across first/middle/last
tells us whether edge positions (fewer operator-adjacency "boundaries")
cost less, which would directly support the type-promotion-point
hypothesis.

**Cross-validated at scale, 2026-08-29** (full manifest.csv audit):
`randommix_07_n19811rungs_24types` (`logic_random_mix` category, real
capture) was off by +39,959 -- traced to its 208 real CPT calls, which
all use `gen_logic_sweep.py`'s exact `(D+D)*R-R/2+1.5` shape (2 REAL
operands, 1 float literal) -- the SAME `original_shape` this thread
already covers. 208 x the already-known ~200/call gives ~41,600, close
to the real 39,959 (the small gap is plausibly the rotating tag pool's
per-call operand variety, not a new effect). Confirms this is the same
open thread recurring at volume, not a separate bug -- no new formula
needed or wired, consistent with the additive-fallback default already
in place.

[^aoidef]: Per-type declared-item rate table (BOOL=16, SINT/INT=18,
DINT/REAL=20, LINT=24/item, base=1184) wired for single-type defs;
mixed-type defs use the flat rate (confirmed non-additive once BOOL sits
next to another type). Live-verified against 85 captured AOI rows: 32
exact, 52 within 1%, 1 at 2.10%. Full derivation: `docs/AOI_KNOWLEDGE_MAP.md`.
Required/Visible/Hidden flag combinations: CLOSED 2026-08-25 — real
2026-08-23 capture data was sitting unreconciled, deltas land within a
32-block band with no direction tied to flag config (noise, not a real
effect).

**Name-length CLOSED 2026-08-30**: `aoiname_len08/09/13/16/20/25/30_def_only`
(7 real points, all sitting unreconciled) confirmed exact against
`8*max(0,(len-8)//4) - 8` — wired into `AoiDefinitionModel.name_length_bytes`.
A real off-by-one bug was found and fixed along the way: the first version
wired (divisor `(len-7)//4`, chosen because it also reproduces all 7 of the
same points) put len=19 one bucket too high. Caught by cross-checking two
real AOI-array-packing captures that only differ in AOI type name length —
`AoiPureBoolDense` (16 chars) and `AoiPureBoolBoundary` (19 chars), both 10
BOOL In/10 BOOL Out/10 BOOL Local, both array of 16 instances — which must
land on the identical total byte count if the shared shape is identical,
but disagreed by exactly 8 bytes under the old divisor. `(len-8)//4`
reproduces all 7 originally-tested lengths identically (none of them sit at
len%4==3, the only residue class where the two divisors disagree) and
resolves the cross-check to 0 bytes apart. AOI-instance-array element cost
split off as its own item, OQ-AOIBOOLPACK-PAIRING, below.

[^aoiboolpackpairing]: The `aoi_array` model's "confirmed exact, 15 real
points" claim (mc=10/20/30/60, but only ever checked at n=1/10/25 per
shape) doesn't survive dense n. Reconciling 27 already-captured points that
were sitting unreconciled proved it: for a single-packed-word AOI
(bool_count<=32), real array bytes follow `8*ceil(n/2) + B` — an odd-length
array costs 4 bytes MORE than the even-length prediction the current
formula makes, a term the formula has no place for at all. B itself is
real and flat per shape but does NOT extrapolate cleanly across bool_count:
B=20 for 10-BOOL-all-Input (`aoipack_mc10_b10_array_n01/10/25`, 3/3 exact),
B=44 for 20-BOOL-all-Input (`aoipack_mc20_b20_array_n01/10/25`, 3/3 exact),
B=28 for the original 30-BOOL/3-way-split shape — 10 In+10 Out+10 Local —
(`aoipack_bool_array_n01/05/10/25/50` + `aoipack_bool_boundary_n16-96` +
`aoipack_bool_dense_array_n16-40`, 18/18 exact). Since B doesn't scale
linearly with bool_count across those three, and the only structural
difference between the 30-BOOL case and the 10/20-BOOL cases is the 3-way
section split (the current parser only tracks a flat total bool_count, not
per-section In/Out/Local counts), the section split itself may be what
actually drives B — untested directly until now.

The 60-BOOL case (2 packed words/instance, `aoipack_mc60_b60_array_n01/10/25`)
is worse: all 3 points show a flat +148-byte miss with **no** odd/even
signal at all against the old formula, but do not fit `8*ceil(n/2)+const`
either when checked directly — multi-word packing is a materially
different, still-open shape from the 3 points on file.

Confidence downgraded `aoi_array`: KNOWN → FITTED (`memory_model.yaml`,
2026-08-30) — the formula is left un-replaced rather than guessing a
generalized fix from underdetermined data (this project already ate one
overfit formula this session, the CPT three-tier bug — not repeating it).
New dense/isolating test files generated instead, not yet captured:
`gen_aoi_boolpack_pairing.py` → `aoibp_dense_bc{10,20,60}_n{02,03,04,06,08,12}`
(18 files, dense n right where the pairing period would show, including
the FIRST dense points at all for bool_count=60) and
`aoibp_split_allinput30_n{01,05,10,16,25}` (5 files, same bool_count=30 as
the already-solved 3-way-split shape but all-Input/single-section, at the
same n values, to directly test the section-split hypothesis). 23 files
total — not padded to the 60-file floor (James, 2026-08-25: not a quota).

[^predefined]: CAM is resolved and wired. MESSAGE's own byte cost stays
unmodeled — `gen_msg_typesweep.py` built 7 new files (one per real
MessageType found grepping the full `samples/local/` corpus: CIP Data
Table Read/Write, PLC5 Typed Read/Write, PLC5 Word Range Write, SLC Typed
Read/Write, every attribute copied verbatim, never guessed), plus the
existing CIP Generic file — 8 types total. A flat size across all 8 would
confirm James's axis-tag-style hypothesis ("lots of config, always the
same data size"); a spread ties cost to attribute-set complexity instead.
MSG's own LOGIC weight (48/rung) is separately resolved and wired.

**Sibling native-structure gap, found 2026-08-27** verifying drill-down
completeness (James: "confirm we can browse down to base structure level
for all UDT/AOI"). Drill-down itself is fully confirmed for everything the
engine CAN size — a recursive walk of all 2,780 UDT/AOI definitions across
James's real 64-file corpus reached 4,502,812 true leaves with zero bad
leaves and zero silent dead-ends. A real, separate gap surfaced along the
way: any tag whose type transitively includes a member typed SFC_STEP/
SFC_ACTION/FBD_TIMER/SCALE/CAM_PROFILE/DCI_STOP/RATE_LIMITER/
CONFIGURABLE_ROUT/ALARM_DIGITAL/FBD_ONESHOT/FBD_MATH — confirmed present
in 0 of 64 real files' own `<DataType>`/`<AddOnInstructionDefinition>`
blocks, same as MESSAGE — couldn't be sized at all (`UnknownDataTypeError`,
caught cleanly by report.py, so the whole file doesn't break, but that tag
was silently excluded from the treemap/list, only showing up in the small
errors footer). 1,277 tag-sizing errors across 24/64 real files traced to
this.

**Wired 2026-08-27** (James: "You should know all of those native
instructions data types ... look for Rockwell instruction manual for data
layout"): rather than trust an instruction-manual citation blind (this
project's own ground-truth discipline — CLAUDE.md — wants a real capture
or real corpus evidence first), checked whether the real corpus itself
already reveals the layout via `Data Format="Decorated"` — it does.
Bender134053_201104.L5X alone has 272 real `SFC_STEP` and 97 real
`SFC_ACTION` tag instances with full decorated field lists; other files
had real (if sparser) evidence for the rest. The mechanism: a predefined
structure's real `Data Format="L5K"` raw value array is one scalar per
DINT-sized field (same convention that already gives TIMER's 3-element/
12-byte L5K array its real shape) — so the array's length × 4 bytes IS
the real total, independent of how many of those DINTs are further
bit-packed status flags. Confirmed zero-variance across every real
instance checked: 272/272 SFC_STEP (28 bytes: Status+PRE+T+TMax+Count+
LimitLow+LimitHigh, 7 DINT), 97/97 SFC_ACTION (16 bytes: Status+PRE+T+
Count, 4 DINT), 5/5 FBD_TIMER (48 bytes), 4/4 FBD_ONESHOT (12 bytes), 2/2
FBD_MATH (16 bytes); RATE_LIMITER (92 bytes) and SCALE (52 bytes) only
1 real instance each so far. Wired into `memory_model.yaml`
`predefined_structures` at ASSUMED confidence (real and zero-variance,
but not yet independently confirmed against an actual controller
memory-capture delta the way TIMER/COUNTER/CONTROL are) — closed 523 of
the 1,277 errors. `sizing/tree.py` deliberately does NOT extend the
generic TIMER/COUNTER/CONTROL 3-way-split drill-down to these — their
field counts vary (SFC_STEP has 7, SFC_ACTION has 4, RATE_LIMITER has
23) and only the TOTAL is confirmed, not a per-field byte attribution,
so a fabricated even split would be worse than staying a correctly-sized,
non-drillable leaf (`_THREE_FIELD_PREDEFINED` set).

**DCI_STOP** (35 errors) has real decorated evidence (SJ_Gormley_20251112_
r02.L5X, 80 bytes/20 DINT) but is deliberately NOT wired yet — every real
instance found carries `Class="Safety"` on the Tag itself, and this
project's Safety content is currently NOT sized by design (OQ-SAFETY, the
UI's red warning banner) even though nothing in the code actually enforces
that exclusion per-tag today — it just happens that Safety AOI types are
mostly unresolvable native structures. Wiring DCI_STOP would make
Safety-scoped totals partially counted for the first time, which needs
a decision from James (exclude Safety-class tags by design everywhere,
or size everything resolvable including Safety and adjust the warning
wording) before it's just silently changed. **CONFIGURABLE_ROUT** —
CORRECTED 2026-08-29, this was wrong: it DOES have real capture data and
IS wired (52 bytes, see item 5 above) — not read in RM018A, but that's
moot now that a real Capacity-based value exists directly. Falls under
the same Safety-scope decision as DCI_STOP (name root matches `CROUT`,
the confirmed Safety-only instruction).

**MESSAGE and ALARM_DIGITAL member lists sourced from RM018A, 2026-08-27**
(James: "you need to size all of these instruction data types... look for
Rockwell instruction manual for data layout", scoped down to 1756-RM018A
specifically per his follow-up clarification). Read directly from the real
manual PDF James pushed (`samples/1756-rm018_-en-p.pdf`, 927 pages, via
`pdftotext -layout` + form-feed page-indexed navigation), not guessed.

*MESSAGE* (RM018A pages 142-147): real member list — `.FLAGS` INT (bit-
mapped status word: bit 2=.EW, 4=.ER, 5=.DN, 6=.ST, 7=.EN, 8=.TO, 9=.EN_CC —
confirmed by the manual's own bit table that these 7 BOOL "members" are
aliased VIEWS into `.FLAGS`, not separate storage, exactly the same pattern
already established for TIMER's `.EN`/`.TT`/`.DN`), `.ERR`/`.EXERR`/
`.REQ_LEN`/`.DN_LEN` INT, `.ERR_SRC` SINT, `.DestinationLink`/
`.DestinationNode`/`.SourceLink`/`.Class`/`.Attribute` INT, `.Instance`/
`.LocalIndex` DINT, `.Channel`/`.Rack`/`.Group`/`.Slot` SINT, `.Path` STRING,
`.RemoteIndex` DINT, `.RemoteElement` STRING, `.UnconnectedTimeout`/
`.ConnectionRate` DINT, `.TimeoutMultiplier` SINT. Non-STRING fields sum to
a KNOWN 46 bytes (10 INT×2 + 6 SINT×1 + 5 DINT×4) under this project's
already-confirmed tight-packing/no-alignment rule for structure members —
**but the total stays unwired**: RM018A never states `.Path`/
`.RemoteElement`'s real STRING capacity (searched the manual text directly,
not found), and guessing the default 82-char built-in STRING size would be
exactly the kind of fabrication CLAUDE.md forbids. `gen_msg_typesweep.py`'s
8 files (already built, awaiting capture) are still the right path to the
real total — once captured, the confirmed 46-byte non-STRING subtotal lets
the STRING length be backed out exactly rather than assumed.

*ALARM_DIGITAL/ALMD* (RM018A pages 53-64): real member list — 23 Input
BOOL (EnableIn/In/InFault/Condition/AckRequired/Latched/ProgAck/OperAck/
ProgReset/OperReset/ProgSuppress/OperSuppress/ProgUnsuppress/
OperUnsuppress/OperShelve/ProgUnshelve/OperUnshelve/ProgDisable/
OperDisable/ProgEnable/OperEnable/AlarmCountReset/UseProgTime), 1 Input
LINT (ProgTime), 4 Input DINT (Severity/MinDurationPRE/ShelveDuration/
MaxShelveDuration), 8 Output BOOL (EnableOut/InAlarm/Acked/InAlarmUnack/
Suppressed/Shelved/Disabled/Commissioned), 3 Output DINT (MinDurationACC/
AlarmCount/Status — Status.0/.1/.2 = InstructFault/InFaulted/SeverityInv
are bit-aliases of the Status word, same pattern as MESSAGE/TIMER, NOT
separate storage), 6 Output LINT (InAlarmTime/AckTime/RetToNormalTime/
AlarmCountResetTime/ShelveTime/UnshelveTime). Cross-validated exactly
against the real `Comms_Bus1_ALMD` tag in `samples/local/L5X_Samples/
MRFP_Edger_2026_06_01_r00.L5X` — every real `<AlarmDigitalParameters>`
attribute name matches the manual's Input Parameter table verbatim.
**Two genuine unknowns block a total**: (1) whether the 31 scalar BOOL
members bit-pack 8-per-hidden-SINT (the confirmed convention for ordinary
UDTs) or take a full byte/word each in this controller-native structure —
unconfirmed, native structures go through different firmware than user
UDTs; (2) real ALMD tags always carry an `<AlarmConfig>` message/class-text
block alongside the base structure (confirmed: both real corpus files with
ALMD tags have it) — unknown whether that text counts toward the tag's own
byte cost or is stored/compiled separately. `gen_almd_singletag.py` built
2026-08-27 (2 files: `almd_minimal` isolates the base structure with
1-char message/class text, `almd_realtext` uses real-length text copied
from `Comms_Bus1_ALMD` to test question (2) directly) — awaiting capture,
mirrors the MESSAGE sweep's isolate-one-variable-at-a-time approach.

*COUNTER cross-check* (RM018A pages 92-93): `.CD`/`.DN`/`.OV`/`.UN` BOOL
(bit-aliased status word) + `.PRE`/`.ACC` DINT — matches the already-wired
3-DINT/12-byte model exactly. No change needed; first time this project's
COUNTER model has been confirmed against a real Rockwell primary source
rather than only empirical black-box capture.

**Negative finding, saves future effort**: the L5K-raw-array-length
technique that solved SFC_STEP/SFC_ACTION/FBD_TIMER/etc. (real `Data
Format="L5K"` value-array length × 4 bytes = real total) does NOT work for
either MESSAGE or ALARM_DIGITAL — grepped every real instance of both types
across the full `samples/local/` corpus (not just James's 64-file subset)
and confirmed zero use `Format="Decorated"` or `Format="L5K"`; Rockwell's
export tooling always uses a specialized semantic view (`Format="Message"`/
`Format="Alarm"`) for these two types instead. Don't re-attempt that
technique on these two — go straight to a real capture.

**RESOLVED 2026-08-29, real capture batch closes 174 of 184 probe files.**
James's own conversion+capture pipeline ran the full `gen_predefined_probe.py`
batch. Derivation method: the live engine, run fresh against each probe
file, predicts a uniform `18128` for every still-unmodeled type (real
`empty_project_baseline`(13296) + `task_program_shell`(4816) +
`routine_logic`(16, the file's own default NOP rung) — the unresolvable
`Probe1` tag itself contributes 0 and raises one caught `SizeError`, which
is exactly the uniform "1 error" every one of these rows showed). So
`real_structure_bytes = real_actual_bytes - 18128 - tag_overhead(84,
real "Probe1" 6-char name)`. Validated against `SFC_STOP`, the one type
already wired from real L5K data before this batch landed: the new real
capture matched the live prediction EXACTLY (0 residual) — confirms the
derivation method itself, not just that one type. All 174 resolved values
wired into `memory_model.yaml` `predefined_structures` at ASSUMED
confidence (n=1 real capture each). Full real values, sorted:

```
4:    ALARM_SET_CONTROL, CONNECTION_STATUS, PHASE_INSTRUCTION,
      RAC_ITF_DVC_PWRDISCRETE_CMD/SET, RAC_ITF_DVC_PWRMOTION_CMD/INF/SET,
      RAC_ITF_DVC_PWRVELOCITY_CMD/SET, SEQ_BOOL, SEQ_INT, SEQ_SINT
12:   DATALOG_INSTRUCTION, DOMINANT_RESET, DOMINANT_SET,
      EXT_ROUTINE_PARAMETERS, FBD_BOOLEAN_XOR, FBD_COMPARE, FBD_CONVERT,
      FBD_LIMIT, FBD_LOGICAL, FBD_MASK_EQUAL, FBD_MATH_ADVANCED,
      FBD_TRUNCATE, FLIP_FLOP_D, FLIP_FLOP_JK, ODOMETER,
      P_INTERLOCK_BANK_STATUS, P_STRAPPING_TABLE_ROW, SEQ_DINT, SEQ_REAL,
      SEQ_TRANSITION, SERIAL_PORT_CONTROL, SIGNED_ODOMETER
20-28: CAM_EXTENDED, FBD_COUNTER, FBD_MASKED_MOVE, P_COMMAND_SOURCE,
      SELECT, SELECTABLE_NEGATE, STRING_16 (20); FBD_BIT_FIELD_DISTRIBUTE,
      HMIBC, MANUAL_VALVE_CONTROL, MAXIMUM_CAPTURE, MINIMUM_CAPTURE,
      OUTPUT_CAM, OUTPUT_COMPENSATION, P_LEAD_LAG_STANDBY_MOTOR, PHASE,
      POSITION_DATA, SAFE_DIRECTION, UP_DOWN_ACCUM (28)
MESSAGE: 688. ALARM_DIGITAL: 973 (both previously genuinely blocked --
      see the negative finding above). ALARM_ANALOG: 2461. PID: 180.
      PID_ENHANCED: 396. PIDE_AUTOTUNE: 972.
Full table (all 174): see memory_model.yaml predefined_structures,
      block dated 2026-08-28/29.
```

Note: `ALARM_ANALOG`(2461), `ALARM_DIGITAL`(973), `ENERGY_BASE`/
`ENERGY_ELECTRICAL`(107 each) are the only 4 values not a multiple of 4 —
checked, not a bug in the subtraction (every other value is a clean
multiple of 4/8/12): plausibly genuine odd-byte real internal padding for
those 4 specific structures (several mix SINT/STRING content with DINT
content, unlike the mostly-DINT-uniform structures that land on round
numbers). `CONFIGURABLE_ROUT`: CORRECTED 2026-08-29 — this line was
wrong. `predefprobe_configurable_rout` DID capture real data (actual
18,264, same as `BUS_OBJ`'s real capture) and IS wired at 52 bytes,
already included in the 174-count and the "all 195" total in item 5
above. Full table: 175 real-derived types now, not 174.

**Safety-scope note applies to this whole new batch, not just DCI_STOP.**
Several of the 174 (`DCI_*`, `SAFE_*`/`SAFELY_*`, `MUTING_*`,
`LIGHT_CURTAIN`, `TWO_HAND_RUN_STATION`, `EMERGENCY_STOP`,
`REDUNDANT_INPUT`/`OUTPUT`, `ENABLE_PENDANT`, `DIVERSE_INPUT`,
`SAFETY_MAT`, `SAFETY_FEEDBACK_INTERFACE`, `DOMINANT_SET`/`RESET`, and
`CONFIGURABLE_ROUT` — added 2026-08-29, James: "seems like a safety
instruction," and he's right, its name root matches `CROUT`, the
already-confirmed Safety-only instruction requiring a GuardLogix/Safety
CPU) are Safety-Instructions-family types. The VALUES are real and
wired; whether Safety-scoped tags should be included in the displayed
total at all is the same still-open product decision flagged for
DCI_STOP originally — not re-decided here, just now applying to a much
bigger list of types.

**Two findings from this same batch, WIRED 2026-08-29** (`report.py`
`build_report` now reads `SoftwareRevision`/`ProcessorType` straight off
the L5X root/Controller element; constants in `memory_model.yaml`
`firmware_baseline_delta`/`safety_capable_baseline_delta`, ESTIMATED tier
like `module_overhead`, never hardcoded inline per CLAUDE.md):

1. **Real per-firmware-version baseline deltas.** 1756-L8x/5069 (non-
   safety-suffix) on v34/v35 both confirm the already-known 18,112 exact
   (0 residual, unchanged -- v34/v35 stay on the default/no-adjustment
   path). v31/v32 land IDENTICAL at +11,240 (1756 catalogs; actual
   ≈29,368-29,376) and v33 at +14,248 (actual≈32,376-32,384) -- both now
   wired, keyed off the firmware major parsed from `SoftwareRevision`.
   **Correction:** the "v38 shows a real +304" claim from the prior pass
   was wrong -- that row (`fwmatrix_v38_1756_l81e`) is
   `WINDOW TITLE MISMATCH`-flagged in manifest.csv (its 18,416 actual_bytes
   belongs to a different file, `fwmatrix_v35_5069_l340ers2`), so it was
   never real v38 evidence. Manifest row cleared per CLAUDE.md's standing
   rule; v38 stays unadjusted (default_bytes=0) until a real capture
   lands.
2. **Real 5069-safety-model baseline overhead, independent of SafetyInfo
   content.** The 5069 Motion+Safety-suffix catalogs (`L330ERMS2`,
   `L340ERS2`) show a real +296 byte baseline over their non-safety
   siblings (`L330ER`, `L340ER`) on the SAME firmware (18,416 vs 18,120 at
   v34/v35; the identical +296 gap reproduces independently at v31/v32 and
   v33, confirming no firmware x safety interaction term is needed) --
   the mere fact of being a safety-CAPABLE processor model costs real
   memory before any actual safety configuration exists. n=2 real
   catalogs directly confirmed, now wired and applied to the whole 5069
   safety-suffix family (`ProcessorType` ending `S2`/`S3`) on the same
   "same physical family" extrapolation basis this project already uses
   for L72-L75 vs. L71.

Validated against all 50 real (untainted) `fw_catalog_matrix` rows: every
one now predicts within 16 bytes of its real actual_bytes (the same small
per-file noise band already accepted at v34/v35), down from errors as
large as 14,552 bytes before this fix. Cross-checked against 5 more real
points from an earlier, separate `fw_baseline` batch (different generator,
same real capture discipline): `l81_v31`/`v32`/`v33` (blank 1756-L81E)
land within 16 bytes too, independently confirming the firmware delta
outside the `fw_catalog_matrix` batch it was fitted from.

**One real caveat surfaced by that same cross-check, not a regression:**
`v35_l306erms2`/`v35_l306erms3` (also from the `fw_baseline` batch) are
`5069-L306ERMS2`/`MS3` -- safety-suffix, so they now correctly get the new
+296 delta -- but unlike every `fw_catalog_matrix` safety file, these two
ALSO carry a real populated `SafetyTask`/`SafetyProgram` pair
(`SafetyLevel="SIL2/PLd"`, 0 real rungs). Prediction is now 1,424 off
(was 1,128 off before this fix, so not newly broken, just already
inaccurate) -- `task_program_overhead`'s `task_extra`/`program_extra`
(fitted from ordinary Standard-class extra tasks/programs) doesn't
correctly model a Safety-class task/program pair's real marginal shell
cost, a distinct, already-known, already-out-of-scope gap
(`is_safety_project` fires its red warning banner for both files, so the
user is never shown this total without the caveat). `firmware_baseline_delta`
and `safety_capable_baseline_delta` themselves are validated only against
BLANK safety-capable-processor files (no real Safety Task/Program content)
-- accurate for that case, not claimed accurate once real (unsized)
Safety Task/Program content is also present in the same file.

**Also from this same push: real evidence AlarmConfig message/class text
length adds to ALMD's real cost**, confirming the open question from
`gen_almd_singletag.py`'s own docstring. `almd_minimal` (1-char text):
19,719. `almd_realtext` (real-length text copied from `Comms_Bus1_ALMD`):
19,754 -- a real +35 byte delta for the longer real text, on top of the
instruction-call + real ALMD structure content these two files also
carry (not directly comparable to the bare-tag 973-byte ALARM_DIGITAL
figure above, which isolates the structure alone).

**AOI array "anomaly" investigated 2026-08-29, was contaminated data, not
a real formula problem.** Of the 5 AOI array files re-captured after the
real Dimension/Dimensions bug fix, 4 show a modest positive delta (+400/
+404/+60/+64, plausibly a small remaining formula gap, still genuinely
open) but `aoi_array_param_def_only`'s row was flagged
`WINDOW TITLE MISMATCH` in manifest.csv (window title read back
"ProbeDciStop" -- a completely different file from the predefined-
structure probe batch, not this one) -- the "-1,044 byte overshoot" a
previous pass reported was that mismatched file's real bytes, not this
one's. Per CLAUDE.md's standing rule that row's capture columns are
cleared, not trusted; `aoi_array_param_def_only` is back to needing a
real, clean capture (still in the same NEEDS-RE-CAPTURE bucket the
Dimension/Dimensions bug fix already put it in -- see
[^aoiarraydimension] below, this was never actually re-captured cleanly).
No engine change made or needed here -- AOI array PARAMETER sizing is
UNTESTED, not confirmed broken.

[^aoiarraydimension]: James, 2026-08-27: "be sure you are handling the bit
mapped bools from hidden sints" prompted a broader audit of AOI-local
sizing, which surfaced a real, separate bug (verified via
`compute_udt_size`, `is_bit_alias`/`hidden` in parser/datatypes.py: the
BOOL-hidden-SINT question ITSELF was already correct and directly unit-
tested — `test_udt_mixed_bool_dint_string_with_bit_packing` — 1 byte for
the backing SINT regardless of how many BOOL aliases point into it, 0
extra for each alias, confirmed exact). The real bug found instead:
`parser/aoi.py`'s `_member_from_element` read a `<Parameter>`/`<LocalTag>`
element's array size off a "Dimension" (singular) attribute — correct for
a plain UDT `<Member>` (parser/datatypes.py, unaffected), but real
`<Parameter>`/`<LocalTag>` elements carry it on "Dimensions" (PLURAL) —
confirmed against 80 real `<Parameter Dimensions="N">` and 191 real
`<LocalTag Dimensions="N">` elements across all 64 corpus files, zero
counter-examples for the singular form anywhere. Every array-dimensioned
AOI Parameter/LocalTag was silently sized as a scalar. Real customer-file
impact: 35 tag-sizing errors closed immediately (all CAM_PROFILE, which
was already correctly wired in `predefined_array_structures` but never
reachable through this bug).

Fixed in `parser/aoi.py`. `sample_gen/builders.py` had the IDENTICAL bug
(`Dimension=` instead of `Dimensions=`) generating AOI Parameter/LocalTag
XML — the two bugs self-consistently masked each other for this project's
own synthetic test files (both sides wrong the same way), which is why no
existing test caught it. Fixed there too. 5 existing files (
`aoi_array_localtag_def_only`/`_1_instance`, `aoi_array_param_def_only`,
`aoi_nested_array_localtag_def_only`/`_1_instance`) regenerated with the
corrected attribute — flagged `NEEDS RE-CAPTURE` in manifest.csv, old
actual_bytes/delta cleared rather than trusted. Reasoning: the prior
2026-08-22 capture of these files almost certainly measured SCALAR
behavior, not array behavior — Studio 5000 very likely didn't recognize
the malformed singular attribute either (real syntax requires plural) and
silently coerced it to scalar on import, same as this project's own
buggy parser did. The math backs this out precisely for
`aoi_array_localtag_1_instance`: fixed-engine prediction is 19,832 bytes,
old real capture was 19,424 — a 408-byte gap, matching almost exactly
what a 100-element DINT array minus a scalar DINT should cost (396) plus
the small universal per-file noise (~8-12) seen everywhere else in this
project. Needs a fresh real capture of the corrected files before this
project can claim the AOI-array-local/param formula is confirmed at all
— it currently rests entirely on the already-validated general
array-of-atomic/array-of-UDT member cost formula being assumed to apply
unchanged to an AOI's own Parameter/LocalTag members too, which was never
actually tested end-to-end against a real capture.

**Real import-failure bug found and fixed, 2026-08-29** (James: "the file
does not open, regenerate it"). `aoi_array_param_def_only` itself
wouldn't import into Studio 5000 at all -- a real, separate bug from the
Dimension/Dimensions one above, not just a bad capture read. Root cause:
`sample_gen/builders.py` `_aoi_parameter_xml` used the generic
`Required="false" Visible="false"` default for the array Input Parameter
(`InputBuffer`, `Dimensions="50"`). Zero real corpus evidence supports
false/false on an array Parameter of any Usage -- the only two real
array-Parameter examples this project has (`LOG_HMIDisplay
Dimensions="25"`, `BitArray Dimensions="1024"`, both from real customer
files) are both `Usage="InOut"` and both `Required="true" Visible="true"`,
already-confirmed for InOut specifically but never independently tested
for Input/Output. Fixed by forcing `Required="true" Visible="true"` on
ANY dimensioned Input/Output Parameter, extending the one confirmed
real pattern (this is a hypothesis-driven fix given the available
evidence, not a positively-confirmed Input-array real example --
flagged here, not silently treated as certain). File regenerated,
lint-clean, zero engine errors; Required/Visible flag choice doesn't
affect the sizing formula itself (already confirmed no real effect,
see the Required/Visible closure note above), so predicted_bytes is
unchanged (19,332). Still needs a real capture -- was never actually
captured cleanly (first attempt hit the Dimension/Dimensions bug, second
attempt hit WINDOW TITLE MISMATCH, and the underlying file itself was
broken this whole time under both attempts).

[^moduleio]: `module_overhead = 1,672 bytes/module` (flat, mean of 2 real
deltas), wired as ESTIMATED tier. 141 files in `samples/generated/modules/`:
per-catalog sweep (119/119 real corpus catalogs), rack-level tests, a full
Kinetix 2-bus/8-axis subgraph, and a full-fidelity replica of James's real
Bender program (69 modules incl. GuardLogix Safety Partner). GuardLogix
SIL2/SIL3 handling is a reusable `build_l5x(..., safety_level=...)`
capability. Real Studio 5000 conversion errors from the 2026-08-24/25
batch all root-caused and fixed: module-level `SafetyEnabled="true"` vs a
non-safety controller; 5069 modules needing `Port Type="5069"`; User-
Defined-Catalog devices needing their real `ExtendedProperties/
UdcAopVersion` schema (150 SMC Flex-E, PowerFlex 525-EENET — PF755
confirmed NOT affected); duplicate Ethernet IPs/AxisIDs; a slot collision;
`ParentModPortId` mismatches. Rack slot-address gaps ("a module in slot
10" concern) audited and confirmed NOT a bug — module size reads
exclusively from `ArrayMember/@Dimensions`, never slot number.
Deliberately not charged `module_overhead`: rack-aliased modules,
`CatalogNumber="Embedded"` I/O. Produced/consumed tags: RESOLVED, see
RESOLVED_QUESTIONS.md OQ-PRODCONS. PowerFlex 525 has multiple real I/O
payload UDTs beyond the one profile covered — needs more real corpus
examples, not guessed.

**Real per-catalog overhead table wired 2026-08-29.** The 141-file batch
above had real capture data landing since 2026-08-22 — 126 rows total, of
which 90 were never checked against the live engine and stayed on the
flat 1,672 estimate. Found the same way OQ-CMPCPTLAYOUT was: re-running
every module-category manifest row through the current engine and
diffing against real actual_bytes. Derived `module_overhead_by_catalog`
(memory_model.yaml, `constants.py` `ModuleOverheadModel`) via the same
subtraction methodology as `predefined_structures`:
`real_catalog_overhead = 1,672 + (actual_bytes - engine_predicted)`, ONLY
for real captures where the file's entire module list is exactly
`[Local, one real module]` — strict on purpose, since several
adapter/bridge catalogs (e.g. `1734-AENTR/C`) turned out to be absorbing
a whole rack of aliased child I/O modules into their own single entry,
which would have corrupted a looser per-catalog derivation with
configuration-dependent numbers. 51 catalogs got a clean, unambiguous
real value (real range: -793 to +10,497 — the flat 1,672 mean was a poor
proxy for this much real spread). Real exact-match rate against the 126
real module rows: 1/126 (before) -> 54/126 (after); full-manifest
regression checked (89 rows affected, 12 multi-module files got
marginally worse by 4-68 bytes each — all already inside the "not solved
this pass" bucket below, net effect strongly positive).

**6 catalogs show a real, unmodeled connection-variant effect** and were
deliberately left off the table rather than force-averaged:
`ETHERNET-MODULE`/`ETHERNET-PANELVIEW` (generic-catalog placeholders —
real overhead scales with declared I/O size, not flat at all),
`1734-AENTR/C` and `1756-EN2T` (real 1-conn vs 2-conn/rack-aliased
variance, up to +2,156 apart for the "same" catalog), PowerFlex
525/755-EENET (a smaller ~48-byte gap between two independent
file-generation methods, ambiguous which is representative).

**38 multi-module files reveal a real, distinct architecture gap: the
per-module marginal cost is NOT flat.** `module_1756_ib16_n01/n03/n10`
(1/3/10 identical 1756-IB16 modules in one file) show delta -4, -1,588,
-7,160 against "N x flat-per-catalog-overhead" — the SAME catalog's 2nd,
3rd, ... Nth instance costs LESS than the 1st, not the same. Rack files
(`modulerack_*`) and zero-connection modules (several `_variant_noconn`
files cost real nonzero bytes despite `module_defined_bytes=0` and
getting silently skipped by the current `continue`-on-0/0 check) show the
same class of gap. Needs its own marginal-vs-fixed decomposition, the
same shape task_program_overhead already got for Task/Program/Routine
counts — real architecture work, not a quick constant fix, so not rushed
into this pass.

**CORRECTION, 2026-08-28** (James: "did a super in-depth memory analysis
on the last pushed file? ... review the last batch of l5x conversions,
there was more than 50"): the "1734-OB8S/A/B, 442G-MABLB ... CIP Safety
connections needing a safety controller even without that attribute"
claim above was WRONG/incomplete — the earlier fix (switching to a
safety-rated processor_type) was necessary but not sufficient. These
files, plus 5 more, still failed real conversion in the 226-row
2026-08-27 batch (`53e91d9`, `samples/convert_log.csv`) with a generic
`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES ... See error log` that gave no
detail on its own. Real root cause found by diffing a passing vs. failing
pair that differ by exactly one real config axis (`modulesweep_2198_
d012_ers3_variant_2conn` PASS vs. `_variant_4conn` FAIL — same catalog,
2conn has Integrated Safety off, 4conn has it on): `wrapper.py`'s
`build_l5x(..., safety_level="SIL2")` branch assumed a single non-
redundant safety-capable primary (no CPU partner) needed no
`SafetyNetwork` attribute on its own Local module's ICP/Ethernet ports —
"no adjacent slot to reserve, since there's no partner. Only SafetyInfo
differs for SIL2." That conflated two separate real Rockwell concepts:
`Width="2"` reserves the adjacent slot for a redundant CPU partner
(correctly SIL3-only); `SafetyNetwork` establishes the safety NETWORK
SEGMENT identity that any downstream safety-enabled I/O module's own
`SafetyNetwork` attribute references, needed whenever a descendant module
has `SafetyEnabled="true"`, with or without a redundant partner. Every
one of the affected files had a downstream module correctly declaring
`SafetyNetwork`, referencing a network segment the project never
established — an orphaned reference. Confirmed against real corpus
(`SJ_Gormley_20251112_r02.L5X`): its Local module's ICP port carries
`SafetyNetwork="...cbbc"` and its Ethernet port carries `"...cbbd"`, the
exact value every downstream Kinetix ERS3 safety module in that file
references. The `is_5069` branch (checked BEFORE `safety_level`, so a
5069-family safety project like `5069-L306ERMS2` hosting
`5069-IB8S/A`/`5069-OBV8S/A` never reached the SIL2 logic at all) had the
identical bug via a separate code path — confirmed against a second real
corpus file (`samples/local/L306ERS2_Sample.L5X`, `5069-L306ERS2`): all
THREE Local ports (the local "5069" bus and both Ethernet ports) carry a
real `SafetyNetwork`. Both branches fixed 2026-08-28, regenerated (the
`_r2`-suffixed retest files, matching the existing suffix convention so
James's re-test run doesn't collide with old files): 12 of the 17 real
failures now carry the fix (6× `2198-*-ERS3` 4conn variants,
`1734-OB8S/A`+`B`, `PowerFlex 527-STO`, `442G-MABLB`, `FANUC Robot`,
`5069-IB8S/A`, `5069-OBV8S/A`) — awaiting a real re-conversion to confirm
this actually resolves the import error, not just structurally plausible.
**The 4 remaining 5069 failures ALSO root-caused, 2026-08-28** (James sent
the real Studio 5000 error this time, not just the generic CSV wrapper):
`5069-IB16/A`, `5069-IY4/A`, `5069-OB16/A`, `5069-OB16/B` all real-error
`Failed to set the 'Size' property (Chassis size exceeds the allowable
size for a chassis.)` at `Modules/Module[@Name="Local"]/Ports/Port/Bus` —
a completely different, non-Safety cause from the 13 above, confirming
the earlier guess that these 4 needed a separate diagnosis. `wrapper.py`
used a flat `Bus Size="32"` for every 5069 catalog, sourced from only ONE
real corpus file (5069-L330ERMS2) and silently assumed universal — it's
actually a real per-model maximum local-I/O-slot count, not a constant.
An empty project (no local module attached) never trips this validation
regardless of the declared value (confirmed: `v35_l306er.L5X` passes 8/8
with the same wrong "32"), which is exactly why this stayed hidden until
a real local 5069 I/O module got attached — every one of these 4 failing
files attaches one. Real per-catalog values pulled from 6 separate real
corpus files (never guessed): `5069-L306ERS2`→9 (`L306ERS2_Sample.L5X`),
`5069-L310ERS2`→9 (`PWO_134190.L5X`), `5069-L320ERMS2`/`MS3`→17
(`Fisher_Synergy_Bead_20240725.L5X`, `FlareFunction_311D_240731.L5X`),
`5069-L330ERMS2`→32 (`BT1XX_FFC_20240325.L5X`), `5069-L340ERS2`→32
(`Fisher_P800Sub_20240531.L5X`). The failing files all use
`5069-L306ER` (real max 9, was getting 32) — fixed by keying Bus Size off
the base model number extracted from `processor_type` (the M/MS2/MS3/S2/
ER suffix doesn't change physical backplane capacity within the same
tier), regenerated the 4 `_r2` retest files plus re-verified the 2
already-safety-fixed 5069 files keep their correct value too. All 17 of
the original real failures now have a real, evidenced fix — awaiting
real re-conversion of all 17 affected `_r2` files to confirm.

**A second, separate real 5069 bug found 2026-08-28** (James: "looks
like your 5069-LxxERMSx has issues as well"). `EtherNetIPMode="A1/A2:
Dual-IP"` is a real Controller-level attribute confirmed present, with
the identical value, in EVERY 5069 corpus file checked (6/6, zero
variance) — describes how the CPU's two embedded Ethernet ports are
addressed, something only a 5069 processor has (1756/1769 have at most
one embedded port). It was missing from both `wrapper.py`'s
`build_l5x` (the primary template used across ~1300 already-tested
files) and `gen_fw_catalog_matrix.py`, for every 5069 catalog, not
specifically the ERMSx (motion+safety) subset James happened to be
testing — confirmed by diffing a plain non-motion S2 catalog's real
export against a motion+safety ERMS2 one and finding the attribute
identical in both. Fixed in both generators (conditional on
`processor_type`/`catalog` starting with `"5069"`); regenerated all 90
affected files (`fw_catalog_matrix`'s 15 5069 catalogs x 6 firmware, plus
the module-sweep/variant/bender-full files that call `build_l5x`
directly). Whether this attribute is actually required for import or,
like `TimeSlice`/the `RedundancyInfo` pad percentages, Studio-5000-
optional is still unconfirmed — added regardless now that a real value
exists, same reasoning as those two.

**1769-family had the identical class of bug, found by generalizing**
(James: "the 5069 and 1769 have different backplane sizes based on the
catalog number ordered"). Worse than 5069's case: there was no `is_1769`
branch in `wrapper.py` at all, so every 1769 processor silently fell
through to the generic ICP-chassis `else` branch — wrong Port TYPE
(`"ICP"`), not just a wrong Bus Size number. Real corpus evidence
(`samples/local/DnR_Personal/TOYOTA_135453_20221024.L5X`, `1769-L33ERMS`)
shows a real, distinct `Type="Compact"` (neither 1756's `"ICP"` nor
5069's `"5069"`), single Ethernet port (unlike 5069's dual-Ethernet).
Fixed 2026-08-28: added the missing branch with the correct Port Type
and SafetyNetwork handling (mirroring the SIL2 fix, though not
independently confirmed as required for 1769 the way it was for 5069/
1756 — the one real corpus file has a populated SafetyNetwork but no
downstream safety module to test the orphaned-reference failure mode
against). Only ONE real per-catalog Bus Size data point exists
(`L33ERMS` → 17) — every other 1769 catalog's real max is genuinely
UNCONFIRMED, kept as an explicit fallback rather than guessed model-by-
model the way the 5069 table could be. The 9 existing `fw_baseline`
1769 files predate the current generator scripts (moved in from
elsewhere per `git log`, not reproducible via `python -m`) and already
pass conversion regardless (same "empty project never trips the
validation" pattern already confirmed for 5069) — not regenerated, the
structural fix matters for any NEW 1769 generation going forward.

[^eventtrigger]: James, 2026-08-25: "Does an event task triggered by MAW
cost more than an event task triggered by the EVENT instruction?" Real
corpus grep (12 real `Type="EVENT"` Tasks across SJ_Gormley_20251112_r02
and Sorter1_20260722r00) confirms exactly two real `EventTrigger` values:
"EVENT Instruction Only" (no EventTag) and "Axis Watch" (EventTag pointing
at a real `AXIS_CIP_DRIVE` tag — confirmed against Gormley's
`EM108_GradingLC`). "Axis Watch" is a Task-level config, not the MAW
*instruction* itself, but it's the real mechanism James's "MAW" question
maps to — there's no other real EVENT-trigger shape in the corpus.
Genuinely untested axis: every existing task-overhead calibration file
(`taskoverhead_n0Xtasks`, the ones that produced task_extra=+700) used
only CONTINUOUS/PERIODIC tasks, never EVENT — so it's currently unknown
whether EVENT itself costs differently from PERIODIC, on top of the
trigger-source question. `eventtask_instronly` and `eventtask_axiswatch`
(`gen_event_task_trigger.py`) mirror `taskoverhead_n02tasks` exactly
(1 Continuous + 1 extra Task, 5069-L306ER/fw35.11, NOP-only programs),
changing only the extra Task's Type/trigger, so direct deltas isolate
both questions. `eventtask_axiswatch` also declares a real
`AXIS_CIP_DRIVE` tag (EventTag must reference a real tag) — that tag has
its own separately-modeled cost and will need subtracting from the raw
capture delta before comparing trigger sources.

[^branchdepth]: Real, sizeable, not modeled — the branch bracket
structure itself (BST/NXB/BND, not modeled by this project's regex-based
parser) costs real memory beyond the sum of leg instructions: legs01 (no
branch) is exact, legs03 under-predicted by 16/rung, legs05 by 24/rung,
not linear in leg count. `gen_branchdepth_closeout.py` adds 8 more
leg-count points (2-30, matching James's own "30 deep" example literally)
to fit the WIDTH curve. Separately, `gen_branchdepth_staggered.py` tests
a genuinely different axis James asked for — DEPTH: always 2 legs per
level, but each level's first leg recurses into another 2-leg branch,
cascading (root[2] → leg1 contains nested[2] → nested's leg1 contains
nested-nested[2] → ...), depths 1-6. Real nested-bracket syntax confirmed
against 624 real rungs in `samples/local/`.
