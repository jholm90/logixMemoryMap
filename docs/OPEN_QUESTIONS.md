# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md`. One line each here — full derivation is in
the matching footnote at the bottom, not inline.

1. **OQ-INSTRFIRSTPASS** — 34/36 instruction weights confirmed and wired.
   SCP/FBC/PID deprioritized (no 2nd real example to test against);
   effort redirected to safety work per James.[^instrfirstpass]

2. **OQ-BASELINE-PROCFW** — real, large, genuinely open. Baseline varies
   hugely by processor/firmware; a full 152-file catalog x firmware matrix
   (19 catalogs × v31-38) now covers this, all awaiting capture — that's
   the next step, not more generation.[^baseline]

3. **OQ-CMPCPTLAYOUT** — mostly closed. Uniform, T1+T2, and T1T3/T2T3
   mixed-tier CPT are solved and wired. Two threads left, both narrowed
   substantially this pass; new diagnostic files await capture.[^cmpcpt]

4. **OQ-AOIDEF** — wired for the common case. Required/Visible flags
   closed (no real effect). Name-length and BOOL-array-packing-boundary
   probes await capture.[^aoidef]

5. **OQ-PREDEFINED (MESSAGE + siblings)** — 8-MessageType + 2-ALMD test
   batches built, both awaiting capture. SFC_STEP/SFC_ACTION/FBD_TIMER/
   RATE_LIMITER/SCALE/FBD_ONESHOT/FBD_MATH wired 2026-08-27 (real, ASSUMED —
   read directly off real Decorated-XML L5K data, not yet capture-confirmed);
   closed 523 of 1,277 real tag-sizing errors. MESSAGE and ALARM_DIGITAL's
   full real member lists are now sourced directly from RM018A (2026-08-27,
   see below) — genuinely new, primary-source information — but neither has
   an exact byte TOTAL yet: both are confirmed dead ends for the L5K-array
   technique (every real instance in `samples/local/` uses a specialized
   semantic `Data Format="Message"`/`"Alarm"` view, never raw Decorated/L5K),
   so a real capture is the only path forward, same as TIMER/COUNTER/CONTROL.
   COUNTER cross-checked exact against RM018A — no change, already correct.
   DCI_STOP/CONFIGURABLE_ROUT remain fully unmodeled.[^predefined]

6. **OQ-AOIARRAYDIMENSION** — real parser bug fixed 2026-08-27:
   `<Parameter>`/`<LocalTag>` array size is a "Dimensions" (plural)
   attribute, not "Dimension" (singular, correct only for a plain UDT
   `<Member>`) — was silently sizing every array-dimensioned AOI local/
   param as a scalar. 5 existing test files need a fresh real capture;
   their prior "confirmed" numbers almost certainly tested scalar
   behavior by coincidence, not the array behavior they were meant
   to.[^aoiarraydimension]

7. **OQ-MODULEIO** — wired, LOW CONFIDENCE (n=2). 141 files awaiting
   capture; that's the next step, not more generation.[^moduleio]

8. **OQ-BRANCHDEPTH** — confirmed real (branch structure costs memory
   beyond leg instructions). Two independent test batches — leg-count
   width and staggered/nested depth — await capture.[^branchdepth]

9. **OQ-LEGACYNETOVERHEAD** — reminder flag only. No real corpus, no
   capture data, nothing to size against yet.

10. **OQ-EVENTTRIGGER** — new, real. task_extra (+700) was derived only
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
confirmed from the existing v31-35/v38 samples — v36/v37 specifically are
flagged ASSUMED in every file's own manifest note (real firmware majors
confirmed to exist, but no real v31-38-range L5X sample for either exists
yet to confirm their exact attribute shape). Files sorted
`fwmatrix_v{NN}_{catalog}` so a plain directory listing groups all of v31
together, then v32, etc. Structural parse-check: 0 errors across all 1533
generated files (up from 1453). Content spot-checked directly (v38 L71,
v38 L81ES) — ProductCode/Bus Size/Safety shape all render as intended.

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

[^cmpcpt]: T1T3/T2T3 wired 2026-08-25: real capture data existed
unreconciled since 2026-08-24; `pow_tier_mix_base=160,
pow_tier_mix_per_operator=64` is exact at 4 of 5 points, and T1T3/T2T3
give IDENTICAL real bytes at every point (T1-vs-T2 stops mattering once
POW is present). See `sizing/constants.py` `CptExpressionModel.cost_for`.
**All-3-tier mixes**: a per-tier-count linear model
(`delta = 44*T1 - 116*T2 + 76*T3 + 72`, fit from 4 points) lands EXACT on
5 of 6 real points (n=3/5/8/10/11) — only n=15 misses, by 144. n=15 is the
only point at operator-cycle remainder 2 (every other point is remainder
0 or 1); `cptmix_threetier_rem2_n06/n09/n12` (3 points, not 2 — enough to
tell a flat remainder-2 bonus apart from one that scales with count in
one capture round) test whether that specific remainder is the trigger.
**REAL-operand/float-literal interaction**: isolated per-factor rates
from existing captures (~118/REAL-operand, ~122/float-literal, both
assuming linearity across n=2); combining both terms additively over-
predicts the real corpus shape by 158 (a genuine negative interaction).
`cptmix_disentangle_real1_noliteral/float1_noreal/real2_float2_noint` get
the missing n=1 points and a full 2-REAL+2-float point to fit the
2-variable surface; `real1_float1` (1 of each, not 2) is a genuine cross-
check point none of the fitting data directly tests. 7 diagnostic files
total, all built and awaiting capture — additive fallback stays the
honest default until each formula lands.

[^aoidef]: Per-type declared-item rate table (BOOL=16, SINT/INT=18,
DINT/REAL=20, LINT=24/item, base=1184) wired for single-type defs;
mixed-type defs use the flat rate (confirmed non-additive once BOOL sits
next to another type). Live-verified against 85 captured AOI rows: 32
exact, 52 within 1%, 1 at 2.10%. Full derivation: `docs/AOI_KNOWLEDGE_MAP.md`.
Required/Visible/Hidden flag combinations: CLOSED 2026-08-25 — real
2026-08-23 capture data was sitting unreconciled, deltas land within a
32-block band with no direction tied to flag config (noise, not a real
effect). Still open: AOI type-name length doesn't follow the uniform
`8*ceil(len/8)` step other formulas use (`aoiname_len09/16/25` probe the
gap, awaiting capture). AOI-instance-array element cost: 3 distinct real
per-element rates depending on member composition (pure-atomic ≈124,
pure-BOOL ≈4 not cleanly linear across an unresolved n=32 boundary, 50/50
mix = exactly 64) — `aoipack_bool_dense_array_n16-40` (brackets n=32) and
`aoipack_mix25_75/mix75_25` (new BOOL:non-BOOL ratios) await capture.

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
wording) before it's just silently changed. **CONFIGURABLE_ROUT** remains
fully unmodeled — not yet read in RM018A, no real corpus evidence either.

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
`CatalogNumber="Embedded"` I/O. Produced/consumed tags untouched
(OQ-PRODCONS). PowerFlex 525 has multiple real I/O payload UDTs beyond
the one profile covered — needs more real corpus examples, not guessed.

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
