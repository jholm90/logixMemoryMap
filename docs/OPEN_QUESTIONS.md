# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md`. One line each here — full derivation is in
the matching footnote at the bottom, not inline.

1. **OQ-INSTRFIRSTPASS** — 34/36 instruction weights confirmed and wired.
   SCP/FBC/PID deprioritized (no 2nd real example to test against);
   effort redirected to safety work per James.[^instrfirstpass]

2. **OQ-BASELINE-PROCFW** — real, large, genuinely open. Baseline varies
   hugely by processor/firmware; 28 of 29 staged files have valid data
   points now, 20 still await capture — that's the next step.[^baseline]

3. **OQ-CMPCPTLAYOUT** — mostly closed. Uniform, T1+T2, and T1T3/T2T3
   mixed-tier CPT are solved and wired. Two threads left, both narrowed
   substantially this pass; new diagnostic files await capture.[^cmpcpt]

4. **OQ-AOIDEF** — wired for the common case. Required/Visible flags
   closed (no real effect). Name-length and BOOL-array-packing-boundary
   probes await capture.[^aoidef]

5. **OQ-PREDEFINED (MESSAGE)** — 8-MessageType test batch built, awaiting
   capture to test the axis-tag-style flat-size hypothesis.[^predefined]

6. **OQ-MODULEIO** — wired, LOW CONFIDENCE (n=2). 141 files awaiting
   capture; that's the next step, not more generation.[^moduleio]

7. **OQ-BRANCHDEPTH** — confirmed real (branch structure costs memory
   beyond leg instructions). Two independent test batches — leg-count
   width and staggered/nested depth — await capture.[^branchdepth]

8. **OQ-LEGACYNETOVERHEAD** — reminder flag only. No real corpus, no
   capture data, nothing to size against yet.

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

[^moduleio]: `module_overhead = 1,672 bytes/module` (flat, mean of 2 real
deltas), wired as ESTIMATED tier. 141 files in `samples/generated/modules/`:
per-catalog sweep (119/119 real corpus catalogs), rack-level tests, a full
Kinetix 2-bus/8-axis subgraph, and a full-fidelity replica of James's real
Bender program (69 modules incl. GuardLogix Safety Partner). GuardLogix
SIL2/SIL3 handling is a reusable `build_l5x(..., safety_level=...)`
capability. Real Studio 5000 conversion errors from the 2026-08-24/25
batch all root-caused and fixed: module-level `SafetyEnabled="true"` vs a
non-safety controller; CIP Safety connections needing a safety controller
even without that attribute (1734-OB8S/A/B, 442G-MABLB); 5069 modules
needing `Port Type="5069"`; User-Defined-Catalog devices needing their
real `ExtendedProperties/UdcAopVersion` schema (150 SMC Flex-E, PowerFlex
525-EENET — PF755 confirmed NOT affected); duplicate Ethernet IPs/AxisIDs;
a slot collision; `ParentModPortId` mismatches. Rack slot-address gaps
("a module in slot 10" concern) audited and confirmed NOT a bug — module
size reads exclusively from `ArrayMember/@Dimensions`, never slot number.
Deliberately not charged `module_overhead`: rack-aliased modules,
`CatalogNumber="Embedded"` I/O. Produced/consumed tags untouched
(OQ-PRODCONS). PowerFlex 525 has multiple real I/O payload UDTs beyond
the one profile covered — needs more real corpus examples, not guessed.

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
