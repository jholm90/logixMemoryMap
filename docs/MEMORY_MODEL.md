# Memory Model

Single source of truth for every sizing constant, formula, and packing rule.
Parser/calculator code must reference this file's values (as named constants in
whatever config format Phase 0 picks), never hardcode a byte size inline.

Every entry is tagged with a confidence level:
- **KNOWN** — documented AB behavior or trivially derivable, no validation needed
- **ASSUMED** — standard Logix behavior per general knowledge, not yet empirically
  confirmed by this project's own test data (Phase 3/4)
- **FITTED** — derived from regression against sample data, includes residual error
- **UNKNOWN** — placeholder, blocked on an open question

## Atomic data types (KNOWN)

| Type | Bytes | Notes |
|---|---|---|
| BOOL (standalone tag) | 4 | ASSUMED — allocated as DINT, not bit-packed. See OQ-BOOLPACK. |
| BOOL (UDT member) | 1/8 (bit-packed) | Packs 8 per backing SINT byte. See UDT rules below. |
| SINT | 1 | |
| USINT | 1 | Unsigned counterpart of SINT -- same storage width, sign interpretation only. |
| INT | 2 | |
| UINT | 2 | Unsigned counterpart of INT -- same storage width, sign interpretation only. |
| DINT | 4 | |
| UDINT | 4 | Unsigned counterpart of DINT -- same storage width, sign interpretation only. |
| LINT | 8 | |
| ULINT | 8 | Unsigned counterpart of LINT -- same storage width, sign interpretation only. |
| REAL | 4 | |
| STRING (built-in) | 4 + 82 = 86 | 4-byte LEN (DINT) + 82-byte DATA (SINT[82]) default |
| Custom string type (scalar) | 4 + nearest8(N) | 4-byte LEN + DATA rounded to the NEAREST multiple of 8 (round DOWN at the tie, remainder 4) -- see below, KNOWN 2026-08-25 |

**Unsigned atomic types, added 2026-08-30**, after a real confidential
customer project (not committed, never named here) that this engine could
not fully size. From field knowledge: "UINT is the same as INT with the last
bit being unsigned and disabling the INT from having a negative value.
you should assume INT/UINT are the same size SINT/USINT same size
DINT/UDINT same size." Real corpus confirmation: that same project's own
logic used a UDT with UINT and ULINT members directly -- these are real,
in-use native atomic types, not something to keep leaving unmodeled.

**Custom string type-definition cost (KNOWN, re-derived 2026-08-25, made
name-length-aware 2026-08-26).** Separate from the per-instance size
above, a custom STRING type declaration itself costs a one-time
`custom_definition_cost_for(type_name_length) = custom_definition_base(208)
+ custom_definition_namelen_bucket(8) * floor((type_name_length -
custom_definition_namelen_offset(5)) / custom_definition_namelen_bucket(8))`
-- a clean step function, confirmed exact against 22/22 real dense
name-length-sweep points (lengths 1-16 plus 20/24/28/32/36/40, maxlen
held fixed at 100) plus a 3-point UDT-member cross-check showing no
separate nesting tax exists beyond this same formula. `208` was itself
re-derived from `206` alongside the padding fix below (the original value
silently absorbed part of the old padding bug). Plus a further
`custom_mod4eq1_definition_bonus = 8` when the type's maxlen ≡ 1 mod 4
(confirmed exact, 3/3 real points: 49, 101, 501). Neither term depends on
the DATA length otherwise. Wired into `report.py`'s UDT-definition loop
and `tree.py`'s definition drill-down.

**Built-in STRING tag-overhead correction (KNOWN, resolved 2026-08-25).**
A built-in STRING tag costs 2 bytes LESS than the ordinary flat
`tag_overhead` formula (below) predicts -- confirmed exact across a dense
9-point count sweep (n=1 to 1000) plus a 4-point name-length cross-check,
all landing on exactly `gap = -2 * count`, independent of both count and
name length. Wired as `string.builtin_tag_overhead_correction = -2`,
applied in `report.py` only when `tag.data_type == "STRING"`.

**Custom string DATA padding (KNOWN, real bug found and fixed
2026-08-25).** Chasing the "strings must be 100% closed" directive
found a real bug: the DATA member (SINT[maxlen]) was sized RAW with no
rounding at all. Real mechanism, verified EXACT (0 residual) against 9
real maxlen points spanning every mod-4/mod-8 remainder (49, 50, 51, 100,
101, 300, 500, 501, 1000): **DATA rounds to the nearest multiple of 8,
rounding DOWN at the exact tie** (i.e. pad to 4 first, then if that lands
exactly at the 8-byte midpoint, drop back by 4). Example: maxlen=50 and
maxlen=51 measure byte-identical real memory (both round to 48); maxlen=
100 (a 4-mod-8 tie) drops to 96; maxlen=101 (already 0-mod-8) stays at
104. No separate per-tag correction constant is needed -- this one rule
fully explains the real per-tag rate. Wired as
`string.custom_data_padding_multiple = 4` (the 2-step rounding logic
lives in `udt.py`'s `compute_udt_size`).

**RESOLVED 2026-08-25:** builtin STRING (not custom) as a UDT member was
tracked as having a real correction depending on both member count and
instance count -- the m>1-AND-n>1 disentangle points turned out to
already have unreconciled real capture data showing no correction is
needed at all (see RESOLVED_QUESTIONS.md OQ-STRINGUDTMEMBER). Custom-string
type-name length (immediately above) and array-of-STRING padding
(OPEN_QUESTIONS.md OQ-STRINGARRAYPAD) are also both RESOLVED and wired.

## Predefined structure types (KNOWN)

Firmware-native structures referenced by name in L5X Tag/Member DataType
attributes but never given a member list in `Controller/DataTypes` --
Logix Designer resolves them internally, so there's nothing to recurse.
**2026-08-29: 174 more wired in one batch**, real single-capture-each data
from the conversion+capture pipeline against `gen_predefined_probe.py`'s
184-file blank-tag discovery batch (see OPEN_QUESTIONS.md OQ-PREDEFINED for
the full derivation method and per-type table) -- MESSAGE (688 bytes) and
ALARM_DIGITAL (973 bytes) are now resolved, both previously genuinely
blocked. DCI_STOP (76 bytes) and the rest of the Safety-Instructions-family
types also now have real values, but stay subject to the same pending
Safety-scope product decision as before (see OPEN_QUESTIONS.md) -- the
VALUE is real and wired, the display/inclusion POLICY for Safety-scoped
tags is a separate, still-open question. CONFIGURABLE_ROUT -- CORRECTED
2026-08-29, this line was wrong: its probe DID capture real data (actual
18,264) and IS wired (52 bytes) -- also Safety-family (name root matches
`CROUT`), same pending scope decision as DCI_STOP above. All 195 known
predefined types are now wired with a real value. TIMER/COUNTER/
CONTROL below are cross-checked exact against RM018A (pages 92-93 for
COUNTER) -- first time confirmed against a real Rockwell primary source
rather than only empirical capture.

| Type | Bytes | Notes |
|---|---|---|
| TIMER | 12 | 1 status DINT (EN/TT/DN bits) + PRE (DINT) + ACC (DINT) |
| COUNTER | 12 | 1 status DINT (CU/CD/DN/OV/UN bits) + PRE (DINT) + ACC (DINT) |
| CONTROL | 12 | 1 status DINT (EN/EU/DN/EM/ER/UL/IN/FD bits) + LEN/PRE-equivalent (DINT) + POS (DINT) |
| MOTION_GROUP | 1,076 | FITTED, 2026-08-23. Pure empirical constant, same rationale as the axis types below -- Rockwell doesn't publish the layout. Exact residual fit, see RESOLVED_QUESTIONS.md OQ-PREDEFINED. |
| AXIS_CIP_DRIVE | 22,636 | FITTED, 2026-08-23. Same. |
| COORDINATE_SYSTEM | 9,516 | FITTED, 2026-08-23. Same. |
| AXIS_SERVO | 16,796 | FITTED, 2026-08-23. Same. |
| AXIS_VIRTUAL | 16,796 | FITTED, 2026-08-23. Identical to AXIS_SERVO -- confirmed independently, not assumed. |
| MOTION_INSTRUCTION | 12 | FITTED, 2026-08-23. Same 3-DINT-style layout as TIMER/COUNTER/CONTROL; exact fit across a 1/5/50 tag-count sweep. |

**Flagged 2026-09-02, NOT wired -- see OPEN_QUESTIONS.md OQ-AXISCOMBO.** A
second, later real-data note (RESOLVED_QUESTIONS.md OQ-AXISSTRUCT) records
a different set of Capacity totals for the same 4 axis/coordinate types --
AXIS_CIP_DRIVE=22,728, COORDINATE_SYSTEM=9,616, AXIS_SERVO=
AXIS_VIRTUAL=16,888, each ~92-100 blocks HIGHER than the values wired
above -- against a "MotionGroup-only local baseline" of 19,296 blocks that
doesn't itself reconcile against the wired `empty_project_baseline`
(13,296) + `MOTION_GROUP` (1,076) = 14,372. The source file composition
behind that second number set isn't available, so it's flagged here rather
than silently trusted or silently ignored; the table above is what's
actually wired and running today. `axis_scale_*` (18 new files,
single/dual-axis 2198 servo drive counts 1-20 ± regen) was built this same
pass but tests a different question (multi-instance servo-drive-module
marginal cost, OQ-MODULEIO) -- it doesn't by itself resolve this
discrepancy.
| SFC_STEP | 28 | ASSUMED, 2026-08-27. 7 DINT (Status+PRE+T+TMax+Count+LimitLow+LimitHigh), read off real Decorated-XML L5K data, zero variance across 272 real instances. Not yet capture-confirmed. |
| SFC_ACTION | 16 | ASSUMED, 2026-08-27. 4 DINT (Status+PRE+T+Count), zero variance across 97 real instances. |
| FBD_TIMER | 48 | ASSUMED, 2026-08-27. 12 DINT-equivalent, zero variance across 5 real instances. |
| FBD_ONESHOT | 12 | ASSUMED, 2026-08-27. 3 DINT-equivalent, zero variance across 4 real instances. |
| FBD_MATH | 16 | ASSUMED, 2026-08-27. 4 DINT-equivalent, zero variance across 2 real instances. |
| RATE_LIMITER | 92 | ASSUMED, 2026-08-27. 23 DINT-equivalent, only 1 real instance so far. |
| SCALE | 52 | ASSUMED, 2026-08-27. 13 DINT-equivalent, only 1 real instance so far. |
| FBD_BOOLEAN_AND | 12 | ASSUMED, 2026-08-27. Bit-packed 3-DINT shape, decoded exactly (not guessed) against real Decorated values on the same instances -- see OPEN_QUESTIONS.md OQ-PREDEFINED. |
| FBD_BOOLEAN_OR | 12 | ASSUMED, 2026-08-27. Same bit-packed shape, independently confirmed. |
| FBD_BOOLEAN_NOT | 12 | ASSUMED, 2026-08-27. Same bit-packed shape, independently confirmed. |
| SFC_STOP | 20 | ASSUMED, 2026-08-28. 5 DINT-equivalent (4 named Decorated members + 1 hidden field revealed only by the real L5K array), zero variance across 4 real instances. Missed on the first corpus sweep (regex bug), found on re-check. |

None of the SFC/FBD-family rows above are drillable to a per-field
breakdown (unlike TIMER/COUNTER/CONTROL's 3-way split) -- only the TOTAL
is confirmed this way, field counts vary per type (4 to 23), and a
fabricated even split would misrepresent that. See `sizing/tree.py`'s
`_THREE_FIELD_PREDEFINED` set.

## Predefined array structures (FITTED, 2026-08-23)

Structures that are always used dimensioned (array) in real Logix, never
scalar, and whose real per-element cost is `base + per_element × N` rather
than a single flat scalar size -- distinct enough from the table above to
need their own formula shape and their own branch in `compute_array_size`
(`udt.py`). A scalar tag of one of these types still correctly falls
through to `UnknownDataTypeError` rather than silently returning a wrong
number, since that shape realistically never happens.

| Type | base | per_element | Notes |
|---|---|---|---|
| CAM_PROFILE | 4 | 56 | Exact linear fit, 1/5/20/50-element real count sweep. `per_element=56` = 14 fields x 4 bytes -- confirms an earlier corpus-based hypothesis that CAM_PROFILE has 14 real per-element L5K fields, only 1 of which is visible in the Decorated XML shape (Rockwell's own internal "voodoo" layout, not derivable structurally). |

## Empty-project baseline (KNOWN, but processor/firmware-SCOPED -- not a universal constant, see caveat below)

`empty_project_baseline = 13,296` blocks, confirmed **for 1756-L81E /
SoftwareRevision 35.05 specifically** -- `wrapper.py`'s single default
processor, which is what virtually every sample this project has ever
generated uses. A fixed, zero-variance cost within that one processor/
firmware combination that exists in every real program regardless of
content -- controller/module/task/program scaffolding that the L5X format
never directly represents as a sizeable element. Confirmed across 200+
independent real data points spanning wildly different test categories,
all landing on exactly this same number once every other sizeable element
in the file is accounted for -- independent in test CONTENT, not in
processor/firmware. Emitted once per report as a `project_baseline`
SizeEntry (`report.py`), confidence KNOWN *for that one processor/firmware
combo*. See RESOLVED_QUESTIONS.md OQ-BASELINE for the full derivation. A
few categories carry a small amount on top of this floor from their own
separately-modeled cost (custom string definitions, SIZE instruction,
odd-byte UDT array packing) -- not folded into the baseline itself, each
has its own constant.

**SECOND CAVEAT, 2026-09-14: the baseline is exact on GENERATED files and short
on REAL exports, and the difference is unpriced shell content, not a wrong
constant.** The strip ladder read a bare real 1756-L81E v35 export shell (one
Task, zero Programs, zero Tags, zero DataTypes, zero AOIs, one Module) at
**21,096 against 13,296 predicted**, and a 5069-L330ERM shell at **17,360
against 13,288** -- 3,736 apart where the model has them 8 apart. The constant
itself must not be raised: `emptyroutine_n01` is a generated 1756-L81E v35 file
carrying a program and a routine the real shell does not, reads 18,884, and the
engine is byte-exact on it, as it is on `emptyrungs_*`,
`aoishape_control_empty` and `axis_baseline_motiongroup_only`. A real export
carries controller-shell content generated files do not -- the controller's own
`Module` element with real `EKey`/`Ports`/`Bus`/`EthernetPorts`, `SafetyInfo`,
`RedundancyInfo`, `Security`, `Trends`, `DataLogs`, `TimeSynchronize`, `CST`,
`WallClockTime`, `QuickWatchLists` -- all of it priced at zero today. See
OPEN_QUESTIONS.md OQ-CTLSHELL.

**CAVEAT, 2026-08-23: the empty-project baseline is not a constant.** It
changes with processor and firmware. Confirmed true, and **partially wired 2026-08-29** -- see
`docs/OPEN_QUESTIONS.md` OQ-BASELINE-PROCFW for the full derivation. Rather
than replace `empty_project_baseline` itself with a lookup, `report.py`
applies two additional real, additive corrections on top of it (both in
`memory_model.yaml`, ESTIMATED tier like `module_overhead` -- FITTED from
real data, not yet KNOWN-grade):

- **`firmware_baseline_delta`** -- keyed on the L5X root's own
  `SoftwareRevision` major version. v31/v32 add a real +11,240; v33 adds
  +14,248; v34/v35 (the already-confirmed 13,296 baseline itself) and any
  unlisted/unconfirmed major (v36, v37, v38, ...) add 0 (no adjustment).
- **`safety_capable_baseline_delta`** -- +296, applied when
  `Controller/@ProcessorType` ends in `S2`/`S3` (the 5069 Motion+Safety
  catalog suffix), independent of whether real Safety content exists in
  the file at all.

Validated against all 50 real (untainted) `fw_catalog_matrix` capture rows
across v31-v35, 1756/5069, safety and non-safety: every one now predicts
within 16 bytes. **Still genuinely unconfirmed:** v38 (its only capture is
`WINDOW TITLE MISMATCH`-flagged, not trusted), v36/v37 (no real sample at
all), the full 1769-series baseline (real range 69,600-98,944, not modeled
at all), and 1756-L7x/L8xES catalogs in the matrix (built, not yet
captured). **13,296 remains the correct base for 1756-L81E/35.05-class
projects specifically** -- the two deltas above are corrections layered on
top of it for the firmware/catalog combinations they cover, not a
replacement lookup table.

## 2198 drive overheads corrected (2026-09-12, OQ-BUILDFAIL-OPEN)

The six `2198-*-ERS3` servo-drive catalogs carried ASSUMED guesses of 10,497
(D012/D020/D032/D057), 7,377 (S086) and 7,341 (S130). Measured from the
`asmclose_2198_*` sweep — 18 clean captures, all six catalogs at 1 / 2 / 4
modules — the real cost is **4,624 bytes for the first drive and 3,640 for each
additional one, IDENTICAL for all six catalogs**. The per-catalog distinction
between them was itself an artifact of guessing. Overhead set to 4,113 for all
six (4,624 minus their common 511-byte declared structure), promoted ASSUMED →
KNOWN.

Consequence, stated plainly: this removes 6,384 bytes of over-charge per drive,
and it **unmasked a systematic under-prediction on every real program** that the
old guess had been cancelling. `realprog_ipc_edgerline` has 12 ERS3 drives and
its residual moved by exactly 12 × 6,384 = 76,608. See OQ-REALUNDER.

A **repeat-instance discount** applies from the second module of a catalog on:

    overhead(occurrence n) = repeat_bytes   for n > 1

`repeat_bytes` is a second per-catalog number in `module_overhead_by_catalog`,
not a constant and not a ratio (432–3,768 bytes, extra/first 0.24–0.79).
Measured at n = 1 / 2 / 4 / 8 on the `asmclose_*` sweeps with zero variance, and
per **catalog** rather than per file — settled by the `modmarg_mixq*` mixtures,
in which reversing module order leaves the total byte-identical while a per-file
reading requires it to shift by `d_first − d_last`. KNOWN.

`module_overhead_repeat_discount.apply_repeat_discount` is **true** since
2026-09-13 for the **ten** catalogs whose rate was measured on a shape real
programs contain. Seven measured rates are deliberately left out of the table,
each with the reason at its own entry:

- **ETHERNET-MODULE** is a placeholder, not a catalog. Its cost is driven by
  connection sizes typed in by hand — 109 instances in the sixteen real programs
  carry 40 distinct connection shapes, which is why `module_connection_data`
  exists — and the `genem_n*` sweep cloned one shape, so its 710-byte rate is
  the cost of a second identical clone.
- the six **2198-*-ERS3** drives were measured on bare drive modules with no
  axis tag, which no real program contains. The with-axis rate is still
  unmeasured: every `modmarg_drvaxis_*` row captured with Studio build errors.

Those two families were 95% of the 189,570 bytes the full table removed from the
sixteen real programs. The ten that remain are worth 10,464 bytes across 47.4 MB
— neutral on real files to within noise — and take the `asmclose_*` rows from 16
byte-exact to 47.

`module_overhead_repeat_discount.repeat_scope` (`project | parent`) decides
whether the occurrence count runs project-wide or restarts under each parent
module. Both are implemented and produce byte-identical totals on all sixteen
real programs, because in every one of them no catalog carrying a measured
repeat rate appears under more than one parent. The scope is therefore still
undetermined by data — every copy in every captured sweep sits under `Local` —
and cannot change a real-file number until a real file splits a catalog across
racks. Default `project`. See OQ-MODULEMARGINAL.

## Unsigned atomics in module structures (fixed 2026-09-12, OQ-V3GENBUGS)

`USINT` (1), `UINT` (2), `UDINT` (4) and `ULINT` (8) are standard Logix atomics
and have always been in `atomic_types`, but `parser/modules.py` carried its own
hardcoded table listing only the signed ones. Any module member declared with an
unsigned type therefore fell through to `unknown_member_types`, and the module's
`module_defined_bytes` came back as an explicit floor rather than a real total.
Not rare: 109 committed sample files declare them, and all four appear in the
real production corpus (25 `UINT`, 20 `USINT`, 16 `UDINT`, 9 `ULINT` member
declarations). The parser now derives its table from this model, so a type the
model knows is understood there automatically. `BOOL` is not in `atomic_types`
(its cost is context-dependent) and takes the standalone 4-byte size in a module
structure, per the convention documented at that table.

## Identifier names (FITTED, wired 2026-09-12, OQ-IDENTNAMELEN)

A named object's own NAME costs bytes. One shared law, `identifier_name_length`:

    name_bytes(len) = 0               for len <= 4
                    = 2 * (len - 4)   for 4 < len <= 8
                    = len             for len > 8

Two independent sweeps of 10 identifiers each, at name lengths 4/8/16/32/40
(40 is Rockwell's real Logix identifier cap), return the identical
per-identifier cost relative to a 4-character name — JSR target routine names
and Program names both give 0/+8/+16/+32/+40. Above 8 characters it is exactly
1 byte per character with **no bucketing**, which distinguishes it from the AOI
type-name and alias-tag name costs below, both of which bucket.

Applied to the JSR-target declaration (`jsr_target_declaration`, whose earlier
straight `1 x len` fit had the right slope but no floor) and to each extra
Program in the shell aggregate (which had no name term at all). Programs' five
namelen rows went from 0/−80/−160/−320/−400 to exactly 0; the JSR rows
collapsed onto a uniform +200, which is the separate per-target under-charge.

Stays FITTED. The 4 < len < 8 interval is an interpolation between two anchors
with no data of its own, and whether plain Routine and Task names follow the
same law is untested — `identnamelen_*` measures both.

## Alias tags (KNOWN, corrected 2026-08-25)

A Tag with `TagType="Alias"` carries no `DataType` of its own in the L5X
(only an `AliasFor` pointing at another tag or a module I/O point) and has
no data space of its own -- but it DOES still occupy a real entry in the
controller's tag table, and that entry has a real, nonzero cost.

**Prior claim of "0 bytes, genuinely zero-cost" was wrong** -- it correctly
identified that an Alias has no raw *data* size (still true), but
incorrectly assumed that meant zero total cost. Real data
(`aliassize_n00001`/`n00010`/`n01000`, captured 2026-08-25) proves an Alias
tag costs `56 + 8 × floor(name_length / 8)` blocks -- the same per-8-char
name-length-bucket shape as ordinary tag_overhead below, just with its own
flat_base (56, vs ordinary tags' 84) and no separate raw-data term added on
top. Exact match across all 3 name-length buckets tested (gaps 56/560/63200
at n=1/10/1000). Wired as `alias_overhead` in `memory_model.yaml`.
Confirmed against real production L5X data (2026-08-20) that ~21% of a
typical program's tags are Alias tags with no DataType -- this is not an
edge case, it's a large real share of most tag tables.

## Per-tag flat overhead (KNOWN, 2026-08-22)

Every top-level `<Tag>` entry (Controller/Tags or Program/Tags) costs a flat
overhead **additive with** its own raw data size (the atomic/predefined/UDT/
array size computed elsewhere in this file): `84 + 8 × floor(name_length /
8)` blocks. Exact fit across 16 independent real data points (13-point
DINT-50-tag count sweep + 3-point REAL-40-tag cross-check at a different
type/count), plus a separate 8/8-point count sweep from 5 to 1000 tags
landing on exactly the same constant at name_length=8 (92 blocks) — two
independently-derived real measurements agreeing exactly, which is why this
is KNOWN rather than FITTED. Tag names are stored in 8-character-aligned
chunks. Type barely affects it (SINT 95/INT 94/DINT 92/LINT 88/REAL 92/BOOL
92 at name_length=8) — treated as type-independent.

Does **not** apply to Alias tags, which use their own smaller `alias_overhead`
flat_base (56, not 84) instead -- see above.

## UDT DataType-definition cost (KNOWN, landed 2026-08-22, corrected same day)

A **one-time** cost per distinct UDT *type definition* actually declared in
the L5X (not per instance, and regardless of whether any tag currently uses
it — see the "def_only, 0 instances" real data below) — additive with both
the per-tag flat overhead above and the tight-packed instance/member size
computed via UDT packing below.

**`160 + 16 × declared_member_count + 8 × ceil(name_length / 8) +
32 × bool_run_count`**, all in ONE formula, verified exact against every
real `udt`-category manifest row with `declared_member_count ≥ 4`.
`declared_member_count` counts members the way a user would (a run of N
BOOL members is still N members, not N+1 — excludes only the hidden
backing SINT itself, not the visible BIT-alias members it backs).
`bool_run_count` is the number of *separate* BOOL runs (each with its own
hidden backing SINT) — a `BOOL, DINT, BOOL` shape has 2, not 1, since the
DINT breaks the run (per OQ-ALIGN).

**Two real bugs found and fixed the same day this first landed, caught by
running the engine against every real tag/udt-category manifest row and
comparing to actual Capacity data (not just unit tests):**

1. The formula was originally implemented as two SEPARATE additive terms —
   `168 + 16×member_count` (from the member-count sweep, name length held
   at 8 chars) PLUS `224 + 8×ceil(name_len/8)` (from the name-length sweep,
   member count held at 4) — because each fit its own sweep exactly in
   isolation. But they're two different 1-D slices through the same
   2-variable surface, both including the same shared base constant;
   adding them together double-counted it (predicting e.g. 416 blocks for
   a real case where actual was 192). Solved the two slices as simultaneous
   equations instead: one true base of **160**, confirmed exact for
   `declared_member_count ≥ 4` (n=1,2 keep the same small-N anomaly already
   documented for tag count, off by a further ~8-16 blocks — not yet
   understood, low priority given it's irrelevant at real-program scale).
2. `bool_run_count` was originally a boolean (`has_bool_run`, +32 flat
   regardless of how many separate runs existed) and computed backwards —
   excluding BIT-alias members instead of hidden ones, so an all-BOOL UDT
   computed `declared_member_count=0`. Fixed to count real declared members
   correctly and apply the bonus once per separate hidden-SINT-backed run.

Also caught the same day: custom STRING types (`Family="StringFamily"`)
were incorrectly getting a udt_definition entry too (this formula was
fit against ordinary UDTs, doesn't apply) — excluded now, and resolved
2026-08-23 with their own `custom_definition_cost = 206` constant, see
the atomic-types table above.

Applies only to true UDTs — an AOI-typed tag still sizes exactly like a
UDT instance (see AOI sizing below), but AOI *definition* cost isn't a
confirmed formula yet and is NOT emitted as a line item — see
`docs/OPEN_QUESTIONS.md` OQ-AOIDEF (2026-08-23) for the substantial real
data now gathered on this (local-tag-count term is a clean exact fit,
`1,184 + 20×n`, but param-count/name-length/atomic-type/bool-adjacency
terms are all still tangled — wiring only the clean piece would
systematically underpredict param-heavy or BOOL-heavy AOIs while looking
like a trustworthy EXACT number, so nothing is wired in yet). This is
currently the single largest known unmodeled gap in the whole engine —
every real program has AOI definitions, and each one is short by
1,100-3,600+ blocks right now.

## UDT packing (KNOWN, OQ-ALIGN resolved 2026-08-22)

- Recurse members in declared order.
- BOOL members: pack 8 to a backing SINT byte, per the existing BIT-member
  generation convention (one hidden SINT per byte of BOOL members, incrementing
  BitNumber 0–7, new SINT for bits 8–15, etc).
- Non-BOOL members: size = atomic/nested-UDT size, per table above.
- Alignment/padding between members: **KNOWN, confirmed 2026-08-22 (was
  ASSUMED).** From field experience, stated with full confidence: `BOOL, DINT,
  BOOL` = 8+32+8 = 6 bytes; `DINT, BOOL, BOOL` = 32+8 = 5 bytes — i.e. no
  4-byte alignment padding at all, and a run of consecutive BOOLs shares one
  backing byte but a non-BOOL member breaks the run, forcing the next
  BOOL(s) onto a fresh backing byte. `compute_udt_size` already produced
  this unchanged (`tests/test_sizing.py::
  test_bool_packing_run_broken_by_non_bool_member`). Now backed by real
  Capacity-tab data too — every real UDT test across the whole per-tag/
  per-UDT-definition sweep (dozens of samples, see per-tag/definition
  sections above) landed on predictions consistent with tight-packing, not
  just the field opinion. `udt.alignment_confidence` in
  `memory_model.yaml` flipped UNKNOWN→KNOWN.
- Nested UDT: recursive — a UDT member's size is that UDT's total computed
  size. Also believed, with less certainty,
  that a nested UDT-typed member always starts fresh rather than packing
  into a partial leftover byte from an adjacent BOOL run — "only BOOLS
  pack." Already true of the implementation: there is no code path that
  merges a nested UDT's bytes into a preceding member's partial byte, so
  this holds by construction, not by an explicit rule that could drift.

## Array sizing

- Array of atomic type: `dimension × element_size`. KNOWN with confidence, no
  packing ambiguity for a single atomic type (BOOL arrays are a known Logix
  special case — BOOL *arrays* bit-pack into DINT-sized words, unlike standalone
  BOOL tags; confirm this distinction explicitly in Phase 3, don't conflate with
  OQ-BOOLPACK).
  - BOOL array formula (ASSUMED, OQ-BOOLARRAY): `ceil(dimension / 32) × 4`
    bytes — 32 bits packed per DINT-sized word. Implemented now since it's
    standard/documented AB behavior, but not yet validated by this project's
    own sample data.
- Array of UDT (KNOWN, resolved 2026-08-24): `dimension × ceil(udt_size / 4) × 4`
  — each element rounds up to a 4-byte boundary, no padding beyond that.
  Confirmed against real data across n=1/10/100/1000/5000 for a 3-byte-tight
  UDT (rounds to 4 bytes/element, exact fit for n≥10, small-N anomaly at
  n=1 matching the same pattern documented elsewhere) and an already-8-byte
  UDT (already a multiple of 4, rounding is a no-op, confirmed unaffected).
  See RESOLVED_QUESTIONS.md OQ-UDTARRAYALIGN/OQ-ARRAYPACK. Wired into
  `sizing/udt.py`'s `compute_array_size`. Atomic-type arrays are NOT
  affected by this rounding (untested at this question, left unchanged).
- Multi-dimensional arrays: product of all dimensions × element size, no known
  special case, but not yet tested at scale >2D.

## AOI sizing

**Named AOI-instance tags (implemented, Phase 2b, 2026-08-20):** confirmed
against real production L5X data that every AOI-typed tag found there is a
plain named `Tag` with `DataType=<AOIName>`, sized identically to a UDT-typed
tag — no logic/call-site parsing needed for this case, which turned out to be
the overwhelming majority of real usage (660 of 3394 real tags). Recurses the
same as a UDT: `Input`/`Output` usage Parameters + `LocalTags` are storage
members; `InOut` usage Parameters are excluded entirely (a reference to the
caller-scope tag passed in, not a new allocation — this is the one place the
old "confirm params don't duplicate the referenced tag's memory" question
below is actually answered: they don't, because they're not sized at all).
AOI definitions can nest other AOIs as a LocalTag's type, recursed the same
way nested UDTs are, with the same self-reference cycle detection.

Confidence: inherits `udt.alignment_confidence` (now KNOWN, see UDT packing
above) via the same `compute_udt_size` path, since an AOI instance structure
is internally UDT-shaped. One AOI-specific sub-question doesn't reduce to
OQ-ALIGN/OQ-BOOLPACK though — see OQ-AOIBOOLPACK: unlike UDT members, AOI
Parameters/LocalTags of type BOOL show up in L5X as plain `DataType="BOOL"`
with no hidden-SINT/BIT-alias representation, so it's not yet confirmed
whether they pack 8-per-byte like a UDT member or allocate unpacked like a
standalone tag. Implemented as unpacked (4 bytes) since that's what the XML
shape actually shows with no basis to assume otherwise, but this is a real
open question, not a confirmed KNOWN fact.

**Inline/anonymous instances and call-site multiplication (OQ-AOIINSTANCE,
still blocked):** a *separate*, smaller question from the above — whether an
AOI called in logic without ever getting its own named backing tag (does
Logix always require one, or can it be anonymous/inline?) allocates memory
per call site the same way. Needs call-site counting from logic parsing,
which is a genuine Phase 1/4 dependency and stays deferred.

**AOI definition cost (FITTED, re-derived 2026-09-13, OQ-AOIDEFSHAPE):** an
AOI's own Parameters/LocalTags declaration has a real, separate one-time cost,
independent of any instance tag — the same relationship a UDT definition has to
a UDT-typed tag. ONE itemised form:

| term | value |
|---|---|
| base | 1163 |
| per declared member | 12 |
| per declared member | that member's OWN data bytes |
| per 32-bit word the declared BOOLs occupy | 24 |
| the members' names | pooled, one byte per name, rounded up to 8 |
| the AOI's own type name | `name_length_bytes`, below |

A scalar BOOL has no data bytes of its own — it is a bit in the packed words,
and `EnableIn`/`EnableOut` count as two further bits in the same words, so an
AOI with no declared BOOL at all still pays for one word. An array member's
data bytes are element × dimension; a TIMER/STRING/UDT member's are that
structure's own size. `InOut` parameters cost nothing (reference, not storage,
excluded upstream in `parser/aoi.py`), and `EnableIn`/`EnableOut` are not
declared members.

Measured on **124 captured def-only files** — an AOI definition with no
instance tag anywhere and no internal rungs, so the definition is the only AOI
cost in the file and its true value reads straight off the capture. They span 1
to 128 declared members, six atomic types, BOOL fractions from 0 to 100%, and
Input, Output and LocalTag usages. **70 of the 124 land exactly, 122 of 124
within the project's ±8 universal residual, worst 11.**

This replaced four separate fitted terms that had each absorbed part of the
same error. Every one of them fitted its own sweep exactly and was still the
wrong shape, which is the reason to record what each was measuring:

| superseded | was really |
|---|---|
| `per_declared_item: 20` | 12 + the 4 data bytes of the DINT every count sweep used |
| `per_type_rate` BOOL 16 / SINT 18 / INT 18 / LINT 24 | the same 12 + own-size relation, seen through the old linear name term |
| `member_name_char_bytes: 1`, 3 free chars | a pool rounded up to 8, misread as a per-character rate |
| `aoi_member_type_extra` REAL 0 / TIMER 8 / COUNTER 8 | exactly (own size − 4); its floor-to-8 was an artifact of the mis-attribution |

The mixed-versus-single-type split went with them. Per-type rates "did not
compose additively once BOOL sat alongside another type" because the name-pool
error was showing up as a composition effect, not because of any real
interaction.

Effect of wiring it, live-recomputed over every valid capture: corpus rows
landing exactly **1,120 → 1,198**, rows inside ±8 **1,690 → 1,907**, and
within 1% per category `aoi_array_packing` **283/283**, `aoi` **160/160**,
`axis` **61/61**, `driveaxis` **15/15**, `aoi_reqvis` **9/9**. On the sixteen
real programs mean absolute error 2.16% → **2.13%**, with
`griffin_stackerline` at **94 bytes** on 2.36 MB.

`base` is set to the value that centres the residual on zero for the 124-file
instrument. A base 8 higher scores more exact rows corpus-wide and is
deliberately not taken — see OQ-AOIDEFSHAPE, which owns the one 8-byte term
still unexplained (exactly 0 on 70 instrument files, exactly +8 on 35,
confounded between the type-name bucket boundary, a fixed offset inside the
name pool, and member order; 54 files built to break it).

**AOI type-name-length step, CLOSED 2026-08-30 (OQ-AOIDEF):** the AOI type
name itself adds `8*max(0,(len(name)-8)//4) - 8` bytes to the definition
cost, confirmed 7/7 exact against real `aoiname_len08/09/13/16/20/25/30`
points. Wired as `AoiDefinitionModel.name_length_bytes`. See
`docs/RESOLVED_QUESTIONS.md` for the off-by-one bucket-boundary bug found
and fixed while closing this (the first divisor tried, `(len-7)//4`,
reproduced the same 7 points but put len=19 one bucket too high, caught
by cross-checking two AOI-array-packing files that only differed in AOI
type name length).

Required/Visible/Hidden's small ±16 swing was CLOSED 2026-08-25 (confirmed
noise, no real effect tied to flag config). See `memory_model.yaml`'s
`aoi_definition` block for the full derivation and
`docs/AOI_KNOWLEDGE_MAP.md` for history.

**Array-of-AOI-instances element cost (DOWNGRADED KNOWN → FITTED,
2026-08-30, OQ-AOIBOOLPACK-PAIRING):** the `aoi_array` formula's earlier
"confirmed exact, 15 real points" claim was only ever checked at 3 sparse
instance counts per shape (n=1/10/25). Dense/consecutive real data (27
points sitting unreconciled) disproves it: for a single-packed-word AOI
(bool_count≤32), real array bytes follow `8*ceil(n/2) + B` — an odd-length
array costs 4 bytes more than this formula predicts, and B (a flat,
per-shape offset the formula has no term for) doesn't extrapolate cleanly
across bool_count. See `docs/OPEN_QUESTIONS.md` OQ-AOIBOOLPACK-PAIRING for
the full data table; new test files generated (`gen_aoi_boolpack_pairing.py`)
but not yet captured.

**Array-of-AOI-instances block alignment (WIRED 2026-09-12,
OQ-AOIBOOLPACK-PAIRING):** the "odd-length array costs 4 bytes more" term
above is one constant — the WHOLE instance-array block is padded up to an
8-byte boundary (`aoi_array.block_alignment_bytes`):

    array_bytes = 8 * ceil(n * per_instance / 8)

so the extra 4 bytes appear exactly when `per_instance ≡ 4 (mod 8)` and
never otherwise. 48 of 48 captured sweep families agree with zero
exceptions, over per-instance sizes of 4, 8, 12, 20, 24, 32, 40, 44, 48,
64, 76, 84, 104, 120, 124, 220 and 244 bytes. It is NOT per-instance
padding: that would make the residual grow with instance count, and the
real data is flat in n. Same mechanism and same 8-byte constant as
`predefined_array_structures`' element-block padding (CAM's 12-byte
element), which is the independent cross-check.

The earlier reading — that BOOL/atomic composition switched the term on and
off — was wrong. Composition only moved the per-instance size; the residue
mod 8 was doing all the work. 49 of the 52 captured families are now flat
in instance count (was 37), and what remains is a per-family CONSTANT
(−38..+180) that five `def_only`-controlled pairs place on the AOI
DEFINITION, not the array. That residual is what the 2026-09-13 itemised
definition re-derivation above resolved; see OQ-AOIDEFSHAPE for the 8 bytes
of it that are left.
Confidence stays FITTED: the rule is exact on every family that can test
it, but three families still vary with instance count (`bc31`, `bc32`, and
`nonatomic_sint_20b10a`) and the closeout files for those are generated,
not yet captured.

**AOI internal Logic-routine content (WIRED 2026-08-31, OQ-AOIINTERNALLOGIC):**
an AOI's own internal RLL routine(s) — separate from its Parameters/
LocalTags declaration cost above — were priced at $0 until 2026-08-31.
`parse_aoi_internal_logic()` aggregates ALL of an AOI's internal routines
(real data confirms per-routine count doesn't matter, only total content)
into one pseudo-routine, weighed with the same per-instruction-type table
as ordinary routine logic (`charge_shell=False` — the AOI definition's own
`base` already covers its shell). Cut max residual on the isolation
sweep from 12.02% to 0.55%. A further composite-scale surcharge on top of
this (`aoi_logic_composite_surcharge_per_instr=20`, FITTED, see the Logic
instruction weights section below) was found and wired 2026-09-02.

**Array-dimensioned declared member data space (WIRED 2026-09-11,
OQ-AOIARRAYLOCALTAG):** an AOI's array-dimensioned declared member (LocalTag
or Parameter) costs its own DATA SPACE on top of the flat
per-member descriptor rate, which counts the member once regardless of its
dimension. (Since the 2026-09-13 itemised re-derivation the array's data
bytes REPLACE the scalar element size a non-array member of the same type
would pay, rather than stacking on top of a flat rate — all six
`aoi_arraylocal_dim_*` def_only points read +4 under the current engine,
flat in dimension from 10 to 1000.) Measured from the 27-file `aoi_arraylocal_*` sweep, captured
2026-09-03 and reconciled 2026-09-11, against a prediction that was FLAT at
every dimension:

| DINT dimension | 10 | 50 | 100 | 250 | 500 | 1000 |
|---|---:|---:|---:|---:|---:|---:|
| deficit | −41 | −201 | −401 | −1001 | −2001 | −4001 |

Exactly `element_size × dimension` at six of seven dimensions (the
project-wide +1 residual accounts for the rest), and by element type at
dimension 50: SINT 1.0/element, DINT and REAL 4.0/element. Definition-side
only — every `_1_instance` twin carries the same deficit, so an instance does
not pay it again. Computed through `compute_array_size`, not
`element_size × dimension`, because the predefined ARRAY structures
(CAM/CAM_PROFILE) have their own `base + per_element` shape and no scalar
element size at all; real programs declare 10 `CAM_PROFILE` array LocalTags,
and going through `compute_element_size` raised `UnknownDataTypeError` on the
first real file it met. Took the 27 rows from −41..−4001 to inside ±4 on 20 of
them; real-file mean |error| 2.1733% → 2.1504% (the whole category is ~17 KB
across the sixteen real programs, 0.036%).

**BOOL arrays are deliberately NOT priced by this term** and stay unpriced:
`BOOL[50]` measured −13, which is neither the 7-byte packed size nor an
8-byte two-word rounding, and `INT[50]` measured −99 against the 100 its
element size predicts. Two further residuals are recorded rather than fitted:
an 8-byte discount per array member *after the first* (1/2/3 arrays of 50
DINT measured 200/392/592, not 200/400/600), and `dimension=25` landing 4
bytes — exactly one element — off the line through 10 and 50. See
`docs/OPEN_QUESTIONS.md` OQ-AOIARRAYLOCALTAG; `gen_aoi_arraylocaltag2.py`
(20 files) measures all four.

## CPT extra-operand rate is PER TIER (FITTED, WIRED 2026-09-13, OQ-CMPCPTLAYOUT)

`cpt_expression.per_extra_same_tier_operand` of 24 was measured on
`cptcx_operandcount_n01..n10`, which uses the same **ADD** operator throughout --
so it was only ever a TIER-1 rate, and it was being applied to every uniform-tier
expression. Uniform tier-2 (MUL/DIV/MOD):

| operators | engine (24) | real | under-charge |
|---:|---:|---:|---:|
| 1 | 140 | 140 | 0 |
| 3 | 188 | 220 | **+32** |
| 4 | 212 | 260 | **+48** |

16 per operator beyond the first, with a single tier-2 operator already exact to
pin the intercept, so the tier-2 rate is 24 + 16 = **40** -- wired as
`per_extra_same_tier_by_tier_cost`, exact at both counts and both rung counts.
Tier 1 stays 24 (`cpttier_k3_t1x3` and `k4_t1x4` were already exact).

**Tier 3 (POW, 116) deliberately keeps the tier-1 fallback.** `cptpow_p2` reads
-16/rung and `cptpow_p3` -12/rung while `cptpow_p2_adjacent` reads **+24/rung** --
the same two `**` operators, differing only in adjacency. Two shapes at one
operator count 40 bytes apart means adjacency of `**` is its own unmodelled term,
and any uniform tier-3 rate would fit one shape and break the other. One `**`
alone, or mixed with one other tier, is already exact.

Remaining in the two-tier mix path: +4/rung on the two non-nested mixes with
tier-1 count exactly 2, and on one nested shape whose twin reads 0. Four bytes,
two shapes each way, inside the +-8 band -- recorded, not fitted. See
OQ-CMPCPTLAYOUT.

## UDT definition member names (KNOWN, WIRED 2026-09-13, OQ-UDTMEMBERNAME)

**A UDT definition's declared MEMBERS' own names cost the same 8-aligned pool an
AOI definition's do** -- the same thing in the same file format, so one law
serves both:

    member_name_pool = 8 * ceil(sum(len(name) + 1) / 8)

They were charged **nothing** until 2026-09-13. Measured on
`udtmn_bool_len{02,04,07,08,12,16,24,32}_b04` -- four BOOL members with the name
length as the only variable:

| name length | 02 | 04 | 07 | 08 | 12 | 16 | 24 | 32 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| residual before | −8 | 0 | +8 | +16 | +32 | +48 | +80 | +112 |
| increment | | +8 | +8 | +8 | +16 | +16 | +32 | +32 |

The pool's own increments are those same seven numbers. **A raw
1-byte-per-character rate fits five of the seven and misses 04->07 (wants +12)
and 07->08 (wants +4)** -- that pair is the entire discrimination between the two
forms, and the second batch (`udtmn2_*`) could not have made it: every one of its
name lengths lands on the same residue mod 8.

Cross-checks: `udtmn2_bool_len{02,16,32}_b04_t{01,05,25}` is flat in TAG count at
each length, so the cost is per DEFINITION and not per instance;
`udtmn2_dint_len{02,32}_n04` and `udtmn2_nest_len{02,32}` agree at 4 and 8
members; and the six `udtmn2_aoi_*` rows are flat as the control, because the AOI
side was already priced.

Hidden backing SINTs are EXCLUDED, the same convention `declared_member_count`
uses -- their generated names are long (`ZZZZZZZZZZBoolMember00`, 22 characters)
and the member-COUNT arm, which is where that would show, does not come out flat
either way. See OQ-UDTMEMBERNAME for the per-shape constant that remains and for
why it is deliberately not fitted.

Effect: the `udt` category is **108 of 108 within 1%** (mean absolute error
0.148%), and on the sixteen real programs mean absolute error **2.025% ->
1.605%** with sum-weighted **+2.145% -> +1.245%** -- the largest single real-file
gain of 2026-09-13, because real UDT member names average about 12 characters and
a real program carries 174 UDT definitions.

## Generic ETHERNET-MODULE connection data (KNOWN, WIRED 2026-09-13, OQ-MODULESTRUCTURAL)

**A generic `ETHERNET-MODULE` connection's data costs 4x its declared bytes.**
Each direction is rounded up to a 4-byte word, the two word counts are summed,
and the block costs 16 per word less 8 when that total is odd:

    W = ceil(input_bytes / 4) + ceil(output_bytes / 4)
    connection_bytes = 16 * W - 8 * (W % 2)

| W | 2 | 3 | 4 | 5 | 9 | 17 | 33 | 65 | 114 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bytes | 32 | 40 | 64 | 72 | 136 | 264 | 520 | 1032 | 1824 |

Exact on all 14 captured points, with the catalog's own overhead at **1,592** and
its 400-byte config array charged as declared. The −8 on an odd word count is the
same 8-byte granularity seen throughout this project, stated as measured rather
than explained.

**The two directions are interchangeable.** `genem_in032` and `genem_out032` are
byte-identical captures (20,256) and so are `genem_in064` and `genem_out064`
(20,384) -- only the SUM of the two word counts matters. No real instance could
show this, because real devices vary both directions at once.

This matters because the profile is **109 of the 438 non-CPU modules in the
sixteen real programs, 25% of them**, and it had no per-catalog entry at all --
every one fell back to the flat 1,672. A per-catalog constant was never the right
shape for it either: the connection sizes are typed in by hand, so two instances
of the same "catalog" are different devices, and the 109 real instances carry 40
distinct connection shapes with input spanning 2 to 450 bytes.

**Scoped to this profile on purpose.** The rack sweeps point the same way (5069
−992/module, POINT I/O −932/card, both under-charged), so a 4x connection cost
may well be general -- but applying it to all 325 captured module rows on one
profile's evidence is the move this project has had to undo before.

**`CommMethod` encodes the comm format and must agree with the connection's
element type.** Across 183 real ETHERNET-MODULE instances, with no
counter-example: 536870915 is INT (109 instances), 536870916 SINT (57), 536870932
no connection at all (11), 536870913 DINT (4), 536870914 REAL (2). Two arms of
the batch that derived the law above were invalidated by getting this wrong --
see OQ-MODULESTRUCTURAL.

## Structured Text assignment cost (FITTED, WIRED 2026-09-13, OQ-STEXPR)

**One law**, replacing a five-entry table keyed on operator count whose confidence
was `MEASURED_SPARSE` and whose fallback over-predicted a one-operator ST
assignment roughly threefold:

    per_statement = base(n_operators, destination type)
                  + each operator's own CPT tier premium above tier 1
                  + 48 per INTEGER-typed NAMED source read into a REAL destination

| operators | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DINT dest | 36 | 40 | 148 | 172 | 196 | 220 | 244 | 292 | 340 | 388 |
| REAL dest | 60 | 56 | 204 | 244 | 284 | 324 | 364 | 444 | 524 | 604 |

1,000 statements per file, differenced against the routine shell. Both rows step
once at two operators (108 for DINT, 148 for REAL) and are dead linear at 24/40
per operator after -- exact at all eight higher counts. The step is the mechanism:
a single-operator assignment compiles to one instruction and a compound one
reaches for expression evaluation. REAL at one operator costing 4 LESS than REAL
at zero is measured, not a transcription slip.

**All three of the old table's non-trivial entries come back from the law**, which
is what says it was mis-parameterised rather than incomplete -- each had been
measured on a different expression and then keyed on operator count alone:

| old entry | the file it came from | reproduced as |
|---|---|---|
| `1\|true` 152 | `R0 := D0 + D1;` | 56 + 2 DINT sources x 48 |
| `2\|false` 164 | `D0 := D1 + D2 * 2;` | 148 + 1 multiplicative x 16 |
| `5\|true` 452 | `R0 := (D0+D1)*R1 - R2/2 + 1.5;` | 324 + 2 mult x 16 + 2 DINT x 48 |

**The operator premium is the CPT tier table, unchanged.** `stx_opkind_*` holds
the count at four and varies only which operator: `+`, `AND` and `XOR` all read
196/statement and `*`, `/`, `MOD` all read 260. 64 over four operators is 16 each,
and 16 is exactly `cpt_expression.operator_tier_costs`' tier-1-to-tier-2 step
(36 -> 52), so ST asks that table for `tier_cost(op) - tier_cost('+')` rather than
carrying a classification of its own. AND and XOR are now measured at tier 1,
which that table did not cover at all. Integer LITERALS do not pay the conversion
term -- the cpt_mirror's `2` is not counted and the file lands exactly, which is
what fixes the rate at 48.

**An AOI called as a bare statement from ST costs `120 + 16 per parameter`** and
was charged **nothing** until 2026-09-13 -- the same mixed-case invisibility that
hid RLL call sites, and the same two constants as a call from a rung. Measured on
`stx_call_aoi_p{01,02,04,08}`, whose labels count declared *input* parameters
while each call also passes the output, so the parameters passed are 2, 3, 5 and
9: 152, 168, 200, 264 per call, exact at all four. A first pass fitted `136 + 16p`
by trusting the label; it fit all four points just as exactly and was wrong,
because two constants against four collinear points absorb an off-by-one silently.

42 of the 48 ST rows in the corpus now land exactly; corpus mean absolute error
1.833% -> **1.545%**. It moved the sixteen real programs by nothing (2.073% ->
2.074%): the held-out set holds 26 ST routines, 3,994 lines, 2,499 assignments and
**zero** AOI call statements. See OQ-STEXPR for that correction and for the four
assumptions the law still carries.

## Standalone UDT tag data slot (FITTED, WIRED 2026-09-13, OQ-UDTTAGSLOT)

**A standalone (non-array) UDT-typed tag's DATA slot is padded up to 8 bytes** --
the same kind of per-TAG slot rule as the atomic 4 below, one level up, and wired
as `standalone_udt_tag_slot.alignment_bytes` alongside
`definition_scale_correction.udt_tag_extra` of **−4** (was +3).

Derived from the one place two captured families disagreed about what a single
UDT tag costs, and they disagreed only because they sit on opposite sides of the
boundary:

| family | UDT size | tags | per-tag error |
|---|---:|---:|---|
| `dscale2_udt_u001_t001..t500` | 9 bytes | 1 to 500 | **exact** (14 of 18 rows at 0, none outside ±1) |
| `addit_dm_ln` / `addit_dh_ln` | 40 bytes | 40 and 400 | **−7.000/tag**, slope exact over 360 tags |

Padding the slot to 8 makes 40 stay 40 and 9 become 16; with the extra at −4 both
families come out with zero residual, and neither constant is separable from
either family alone. Corpus mean absolute error 1.853% -> 1.841%, and the `udt`
category picked up 7 more rows inside ±8.

**Arrays are deliberately untouched.** `dscale2_udt_arr002/arr010/arr100/arr500`
read +1 at every length against a 12-byte, 4-aligned ELEMENT, so the padding is
on the tag's slot and not on each element. Padding elements instead improves the
sixteen real programs more (2.13% -> 1.88%) and destroys the `tags` category
(0.27% -> 2.03% mean absolute error), so that gain is absorbing some other
missing term -- see OQ-REALUNDER, not this rule.

FITTED and thin: two UDT sizes, one on each side of one boundary, fitting two
constants. 52 files (`gen_udttagslot_closeout.py`) cover every residue mod 8 at
two tag counts.

## AOI call site (FITTED, WIRED 2026-09-13, split from the flat 168)

**One AOI call site costs `120 + 16 per parameter passed`**, the instance tag not
counting as a parameter. The flat 168 wired on 2026-09-13 was one point on that
line; two independently written generators with different AOI shapes fix both
terms:

| family | call | params | per call |
|---|---|---:|---:|
| `dscale2_aoi_d001_t001_c{005,020,060}` | `Aoi_D000(Inst000,0,0,OutBitTag);` | 3 | 168 |
| `addit_dn_a{m,h}` | `AddAoiProbe(AoiInst0000,0,Bit1);` | 2 | 152 |

One parameter, 16 bytes, both exact. The `addit` measurement is a −16.000/unit
slope over 180 units, and `dscale2`'s own `_nocall` arm already proved the
instance TAG is exact at 1, 5, 20 and 60 tags, so the whole 16 sits on the call
rather than on the instance.

The sixteen real programs carry 3,918 call sites passing 15,691 parameters, a
mean of 4.0 -- so the flat rate was under-charging parameter-heavy AOIs and
over-charging small ones. Mean absolute error 2.15% -> **2.06%**, files within 1%
**3 -> 4**.

## Standalone atomic tag data slot (KNOWN, WIRED 2026-09-12, OQ-SHELLCONST)

**A standalone (non-array, non-structure) atomic tag's DATA occupies a fixed
4-byte slot regardless of its declared type.** Six bare tag-count files, 50 tags
each, one type per file, no logic and nothing else in them -- so the residual is
the tag-data error and nothing else:

| file | residual | per tag | reading |
|---|---:|---:|---|
| `type_bool_50tag` | +0 | +0.00 | already 4 |
| `type_dint_50tag` | +0 | +0.00 | already 4 |
| `type_real_50tag` | +0 | +0.00 | already 4 |
| `type_sint_50tag` | −150 | **−3.00** | 1 charged, 4 real |
| `type_int_50tag` | −100 | **−2.00** | 2 charged, 4 real |
| `type_lint_50tag` | +200 | **+4.00** | 8 charged, 4 real |

All six fit that one rule with **zero residual**: SINT and INT are padded up to
the slot, LINT is reported in it rather than the 8 its value needs, and
DINT/REAL/BOOL already match.

**This is what the 69 `typesweep_*` files at exactly −5 were.** Their tag pool is
5 tags each of SINT/INT/DINT/LINT/REAL, so −15 −10 +0 +20 +0 = **−5 exactly**, on
every one of the 69 regardless of instruction or operand type. It was also 15 of
the 23 bytes behind the corpus's largest residual bucket: the 263 files at −23
moved to −8, and what remains there is the non-atomic part of that family's pool
(a DINT[20], a CONTROL, a STRING array and two STRING(82)), which
`gen_pool_residual.py` is built to name.

**Arrays and structure members are deliberately untouched.** An array keeps
`element_size × count` and a structure member keeps its packed size -- both
confirmed across every array and UDT sweep in the corpus -- so this is a per-TAG
slot, not a change to atomic sizes anywhere else. A test asserts `SINT[100]`
stays exactly 300 bytes smaller than `DINT[100]`.

Corpus exact-prediction rate **36.1% → 40.0%** (1,026 of 2,563 clean generated
captures). Real-file mean absolute error 2.1294% → 2.1290%: real programs are
overwhelmingly DINT/REAL/BOOL and UDT tags, so almost none of this lands on them.

## Per-family firmware correction (WIRED 2026-09-12, OQ-BASELINE-PROCFW)

`firmware_baseline_delta` applies ONE ladder to every processor, and the 140
active-platform `fwmatrix_*` captures say that cannot work: each processor's
residual is constant within a firmware band and the bands differ by family. On a
bare-baseline file -- one processor, one firmware, no content at all -- the
residual IS the baseline error by definition, so this is reading a lookup table
off its own measurement rather than fitting free parameters. Every value is a
multiple of 8, with 4 to 9 identical captures behind each cell.

| family | v31/32/33 | v34/35 | v38 |
|---|---:|---:|---:|
| 5069 L306 / L310 / L320 | +48 | +32 | +32 |
| 5069 L330 / L340 | +8 | −8 | +8 |
| 5069 L3100 | +8 | −8 | +32 |

Pattern order is load-bearing: `5069-L3100ERM` also starts with `5069-L310`, so
the L3100 row must precede the L306/L310/L320 row or it is silently swallowed.
A test asserts that specific ordering.

**No 1756-L8x rows, deliberately, and this is the important part.** The L8x
fwmatrix rows do sit at +16 on v34/v35 (and the ES rows at v38 too), and
correcting them here as a baseline error is WRONG. Every generated test file in
this project is a 1756-L81E at v35, so a −16 baseline correction moved **787
previously-exact captures to −16 and dropped the corpus exact-prediction rate
from 32.9% to 6.6%**. That was caught by re-running the residual census
immediately after wiring, which is the only reason it did not ship. The L8x +16
is already diagnosed and is not a baseline term: it is a firmware-dependent
CONTENT gap -- the real MainRoutine content drops to 0 bytes on v34+ hardware
while this engine still predicts 16 -- and it belongs to whatever eventually
prices that content.

Result: active-platform `fwmatrix_*` rows exact **68/140 → 118/140**, with the
22 that remain being exactly the L8x +16 content gap. Corpus exact-prediction
rate **32.9% → 36.1%**. Real-file mean absolute error is unchanged at 2.1294%:
the corrections are 8 to 32 bytes on files of 1 to 7 MB, so roughly 0.0005% --
correct, and not a headline.

## Module / I/O tag sizing

**THE FILE IS THE FINAL DECISION ON MODULE SIZING (rule, 2026-09-12).** A
module costs its per-catalog OVERHEAD plus the SIZE THE L5X STATES, and every
module gets sized -- there is no module shape whose declared data is free. The
catalog number selects the overhead only; it does not and cannot determine the
size, because several catalogs are configurable: `ETHERNET-MODULE`,
`ETHERNET-PANELVIEW` and the generic device profiles have their input and
output sizes typed in by hand, so two instances of the same catalog are
different devices. The 109 real `ETHERNET-MODULE` instances carry 40 distinct
connection shapes with input spanning 2 to 450 bytes; no per-catalog constant
can express that and the file already says it outright.

Two consequences wired the same day:

1. **Rack-aliased, processor-embedded and legacy-network modules are charged
   their own declared `module_defined_bytes`.** They used to be charged exactly
   ZERO. That was right about the OVERHEAD -- it was fitted from two modules
   with their own Connection and there is no data for whether it transfers to
   those shapes, so it is still not charged and the SizeError is still the
   record of that -- and wrong about the data, which the L5X states as plainly
   for them as for anything else. Across the sixteen real programs this is 28
   modules and 1,956 declared bytes that were previously free.
2. **An unresolvable connection or config structure falls back to the file's
   own stated `InputSize`/`OutputSize`/`ConfigSize`** instead of contributing
   nothing. The member walk stays the primary source -- it is finer-grained and
   agrees with the stated attribute wherever both exist -- but a member type
   the walk cannot size no longer silently turns the total into a floor. The
   unresolved type is still reported, now annotated with the stated size that
   replaced it.

**What this does NOT fix, stated so it is not mistaken for closed.** The
`rack_pointio_*` family is still 9-28% under-predicted and `rack_pointio_n02`
is 2,434 bytes short with ZERO rack-aliased modules in it -- so most of that
gap is the priced cards' own ASSUMED per-catalog overheads being too low, which
needs the per-catalog refit under this formula, not these two changes. Real-file
mean absolute error moved 2.1395% -> 2.1294%. See `docs/OPEN_QUESTIONS.md`
OQ-MODULESTRUCTURAL.



**Wired 2026-08-27, per-catalog table added 2026-08-29 — see OQ-MODULEIO
for the full derivation.** `module_defined_bytes` (real, computed from the
module's own auto-generated "Module-Defined" data type — InputTag/
OutputTag/ConfigTag Structure content, sized the same way as any UDT) +
a real per-catalog overhead when one exists (`module_overhead_by_catalog`,
51 catalogs, real range -793 to +10,497, ASSUMED confidence, derived the
same subtraction way as `predefined_structures`), else the flat
`module_overhead` (1,672 bytes/module, the mean of the original 2 real
captured deltas) as a fallback for any catalog with no real data yet.
Both stay ESTIMATED tier, not EXACT. NOT charged to a rack-aliased module
(`RackConnection`/`InAliasTag`) or a `CatalogNumber="Embedded"`
processor-integrated I/O block (CompactLogix 5370 "ER" family) — zero real
data for either shape, stays fully unmodeled rather than guessed. Real,
still-open gaps: a module's 2nd/3rd/... instance of the SAME catalog in
one file costs LESS than the 1st (not flat per-instance — real
`module_1756_ib16_n01/n03/n10` deltas are -4/-1,588/-7,160 against a flat
per-instance assumption), and a handful of catalogs (generic Ethernet
placeholders, a couple of adapter/bridge catalogs) show real
connection-variant-dependent overhead not yet decomposed — see
OPEN_QUESTIONS.md OQ-MODULEIO.
- Produced/Consumed: **RESOLVED — OQ-PRODCONS**. No special connection-
  overhead formula needed — a correctly-built produced/consumed tag's
  DataType already includes a `CONNECTION_STATUS`-typed member, so
  ordinary UDT-member recursion covers it; `CONNECTION_STATUS` itself is
  now a wired `predefined_structures` entry (4 bytes, 2026-08-29 batch).
  Zero produced/consumed tags in the real corpus so far. See
  RESOLVED_QUESTIONS.md.
- Motion/Kinetix (2198-series) and VFD (PowerFlex) module shapes:
  **UNKNOWN**, deliberately untouched — need their own real-shape
  research, not a safe reuse of the backplane/Point-I/O shapes above.
- **Zero-connection modules, visibility fix 2026-09-02.** A module with no
  Connection and no stated size of its own (real shape: a bare
  `ETHERNET-BRIDGE` used purely as an IP-address fan-out for a downstream
  device with no PLC logic connection, per the field description)
  was silently skipped — no SizeEntry, no SizeError. Now flagged with an
  explicit SizeError so it's visible in the report; `"Local"` stays
  excluded from this flag since its overhead is already covered by
  `empty_project_baseline`. No total changed. New test file:
  `bridge_placeholder_*`.
- **CIP-MODULE (generic CIP device / named-EDS-without-AOP), flagged
  2026-09-02, not yet resolved.** Real shape confirmed from
  TitusvilleTrimmer's own `IO_Optm` module: `CatalogNumber="CIP-MODULE"`,
  rides a parent bridge's virtual CIPBus (`ParentModPortId="1"
  Type="CIPBus"`), one "Standard" Connection with matched Input/OutputSize,
  Decorated shape `AB:1756_MODULE_DINT_{n}Bytes:I:0`/`:O:0` (DataType name
  literally encodes the byte count, `Dimensions = n/4`, confirmed exact at
  n=496 = 124 elements). Currently sized with the flat ~1,672-byte
  `module_overhead` default (no per-catalog entry exists for CIP-MODULE) —
  same class of risk already documented above for ETHERNET-MODULE/
  ETHERNET-PANELVIEW ("overhead scales with declared I/O size, not flat").
  New test batch `cipmodule_scale_*` (7 files, 64-2048 byte declared I/O
  sweep + a 3-instance file) built to test this; no real capture data back
  yet.

## Logic instruction weights (FITTED, 2026-08-22 — not yet wired into the engine)

`delta_blocks = fixed_base + weight × rung_count`, baseline-corrected against
an empty-project baseline of 18,128 blocks. **Every routine also carries a
fixed_base cost of 4,816 blocks** (5,096 for a routine containing a JSR —
the extra 280 is presumably the target subroutine's own routine-definition
overhead), confirmed identical across 42 instructions. Fit from the
244-file per-instruction sweep (`gen_logic_sweep.py`), 5 rung-count points
each (10/50/100/1000/5000), **0.00% residual against the raw per-file
measurement** — an exact linear fit, not a loose regression. **Landed in
code 2026-08-22** — `memory_model.yaml`'s `logic_instructions`,
`parser/logic.py` (RLL rung-text tokenizer), `sizing/logic.py`
(`compute_routine_logic_bytes`), wired into `report.py` as `tier=
"estimated"` entries, separate from the tag/UDT `tier="exact"` entries per
CLAUDE.md's ground-truth constraint.

**MAJOR CAVEAT, 2026-08-25: every weight in the table below assumes
DINT/LINT/REAL operands.** Real data (`typesweep_*` sweep, see
`docs/OPEN_QUESTIONS.md` OQ-OPERANDTYPE) proves operand data type changes
the real cost substantially for ADD/SUB/MUL/DIV/MOD/EQU/GEQ/GRT/LEQ/LES/
NEQ/MOV/LIM/CPT — SINT/INT operands cost dramatically more (+88 to +164
blocks/rung depending on instruction), REAL costs somewhat more for some
(+16 to +56/rung) and less for LIM (-8/rung), STRING costs +52/rung for
EQU/NEQ. LINT behaves identically to DINT (no separate handling needed).
This means every "CONFIRMED, 0.00% residual" status elsewhere in this repo
(MEMORY_MODEL.md's own table below, `docs/INSTRUCTION_COVERAGE.md`) is
only proven exact for DINT/LINT/REAL-typed operands — a real program doing
SINT/INT math will be under-predicted, potentially by 100+ blocks/rung.
NOT wired: requires the logic parser to resolve each instruction's operand
tags back to their DataType, which it doesn't do today (occurrence-
counting only). Flagged as the top priority for the next logic-parser
architecture pass, ahead of further per-instruction weight capture.

**Correction, same day as first landed:** several sweep files' rung text
isn't just the named instruction — e.g. XIC's file is literally
`"XIC(tag)OTE(tag);"`, not `"XIC(tag);"` alone, because a bare XIC can't
legally close a rung. The table below shows the raw *per-file* measured
weight (still 0.00% residual, still real) next to the **isolated
per-instruction weight** actually used by the engine — decomposed using
OTE's own clean 16 (its file, `"OTE(tag);"`, has no companion) as the
anchor, so summing occurrences of whatever instructions actually appear in
a real rung reconstructs the right total instead of double-counting a
shared companion. Caught by cross-checking the engine's own prediction
against real data for `instr_xic_n01000` (engine said 40,816 before the
fix; real delta was 24,816 — the corrected engine now matches exactly, see
`tests/test_logic_sizing.py`). Composability across *different*
instruction types sharing a rung is exactly what `gen_logic_random_mix.py`
tests, not yet confirmed by real data at that composed level.

**MAJOR CORRECTION, 2026-08-23: the CPT=452 row below is WRONG as a
general constant.** That number is only valid for the one specific complex
CPT expression shape used in the original 244-file sweep — it is that
expression's cost, not CPT's. Real data (`cmpcpt_cpt_*`, simple 2-operand
expressions against a different, smaller tag pool) shows the engine
wildly over-predicting when 452/rung is applied to a simpler expression —
e.g. one 1000-rung file over-predicted by 328,264 blocks. CPT's real
per-rung cost is expression-complexity-dependent (operand/operator count)
and cannot be modeled as a single flat rung-weight. **Not fixed here** —
needs a genuine per-operand/per-operator cost model, a real architecture
change to `sizing/logic.py`, not a constant edit. The `452` is left in the
table/`memory_model.yaml` for now because removing it (implying 0) would
be worse than a wrong-but-nonzero number, but treat any CPT-heavy
estimated-tier logic number as unreliable until this is properly modeled.
See `docs/OPEN_QUESTIONS.md` OQ-CMPCPTLAYOUT for full detail.

**The paragraph above describes the state on 2026-08-23 and is kept for the
reasoning trail; the architecture change it calls for landed 2026-08-26.**
CPT is priced per call from its own expression's operator tokens
(`cpt_expression`), and 63 of the 65 captured `cptmix_*` rows now reconcile
at exactly 0 (the other two at −4 and −16).

**CMP arithmetic operands share CPT's expression law (WIRED 2026-09-12,
OQ-CMPCPTLAYOUT):** CMP was priced as a flat 76-byte weight plus two boolean
surcharges (compound condition, float literal) and had no expression model at
all, so a CMP whose operands are themselves arithmetic — `CMP(L0+L1>L2)` —
paid nothing for the arithmetic. It now charges

    cpt_expression.cost_for(arithmetic_operators) - cpt_expression.base_read

on top of its own base weight. No separate CMP fit: the tier table fitted on
CPT lands on CMP's measured residuals unchanged, which is the evidence the two
share one law. `L0+L1>L2` went −36 → 0, `L0+L1>5` −36 → 0,
`(L0+L1)*L2>L3-L4` −100 → 0. Comparison operators and the `&&`/`||`
connectives are deliberately not tokenized as arithmetic — the connective is
already priced by `cmp_surcharge.compound_cost`, and double-charging it would
break every bare compound CMP, all of which measure exact.

Two CMP residuals survive: −4 on two 2-operator shapes (shared with
OQ-CPTARRANGE's four −4 rows, and confirmed per-rung by a −400 at n=100), and
−52 on `L0*1.5>L1+2.5`, where `float_literal_cost` is charged once per call as
a boolean but the shape has two float literals inside arithmetic. Closeout
files are generated, not yet captured.

All originally-excluded instructions are now resolved. SIZE, BTD, COP,
CPS, and FLL all had the same real array-subscript bug (see below);
all five are now fixed, re-captured, and in the table with exact fits.
The EQU n=100/CMP n=10 garbled-value glitch this used to also flag is
long since fixed and re-captured.

**Root cause of the CPS/COP/FLL/SIZE/BTD glitch, found by spot-check
2026-08-22:** these instructions take an array-typed
operand, and the generator was emitting the bare tag name (`Arr`) instead
of a subscripted reference (`Arr[0]`) — real Rockwell syntax always
requires `[index]` on an array-typed operand (confirmed against the real
corpus, e.g. `BTD(CNET_ENTRY_STATUS[11],12,...)`). SIZE has the same bug
via its STRING operand, which needs `.DATA[0]`, matching the real corpus
`SIZE(_DisplayBuffer.szString[0],0,...)`. A file with this bug still
converts "ok" through `l5xgit l5x2acd` (see the SDK-verification note
below) — that's why it wasn't caught earlier and why every instance came
back at an identical byte count regardless of rung count (the program
never actually compiled at scale). Fixed in `gen_logic_sweep.py`;
all 5 instructions regenerated and re-flagged for re-capture.

**T_ADD removed entirely, not re-flagged (2026-08-22):** T_ADD is a real
Rockwell-authored `AddOnInstructionDefinition` ("DateTime := DateTime +
Time", found in 18+ real corpus files, Vendor="Rockwell Automation"), not
a native instruction — a misclassification from earlier corpus scanning.
The generated test (`T_ADD(D0,D1,D2,D3)`, four bare DINTs, no AOI
definition, no instance tag) doesn't correspond to any valid real call
shape (real usage: `T_ADD(Wrk_T_ADD5,Wrk_EoDST,Wrk_Offset,Wrk_SoST)`), so
there's no fix that makes the original test meaningful — the 5 files and
their manifest rows were deleted outright rather than queued for
re-capture.

**SDK-verification finding, 2026-08-22: does `l5xgit
l5x2acd` catch bad programs before they burn real capture time?** No. Confirmed empirically via `samples/convert_log.csv` (398 "ok"
/ 27 "FAILED"): every file affected by both bugs above shows status "ok"
— the SDK's L5X→ACD conversion only opens/parses the project (catching
structural/schema failures like an unsupported ProcessorType — all 27 real
FAILED rows are that class) and does not perform ladder-logic
verification. There's no real Studio-5000-grade verify reachable from this
environment. Mitigation: `src/sample_gen/lint.py`, a local heuristic
pre-flight check wired into every generator's write path, catching exactly
these two error classes (missing array subscript on an array-typed
operand; instruction/AOI call with no matching native-instruction entry or
declared AOI definition in the same file). Not a substitute for real
verification — it only catches classes of error already found the hard
way — but a retroactive sweep of all 586 previously-generated files came
back with 0 findings once its native-instruction whitelist was completed,
which is reasonable (not conclusive) evidence these two bug classes are
now contained.

| Instruction | raw per-file weight | isolated weight (used by engine) | fixed_base | n | Residual |
|---|---|---|---|---|---|
| CPT | 452 | 452 (solo rung) | 4,816 | 5 | 0.00% |
| ABS | 120 | 120 (solo rung) | 4,816 | 5 | 0.00% |
| XPY | 116 | 116 (solo rung) | 4,816 | 5 | 0.00% |
| CONCAT | 104 | 104 (solo rung) | 4,816 | 5 | 0.00% |
| MID | 100 | 100 (solo rung) | 4,816 | 5 | 0.00% |
| DELETE | 100 | 100 (solo rung) | 4,816 | 5 | 0.00% |
| CMP | 92 | **76** (CMP+OTE combined) | 4,816 | 4 | 0.00% |
| LBL+JMP (pair, combined) | 120 | **64/40** (independently decomposed, KNOWN — see note below) | 4,816 | 5 | 0.00% |
| SIZE | 128 | 128 (solo rung, resolved 2026-08-23) | 4,816 | 5 | 0.00% |
| COP | 112 | 112 (solo rung, resolved 2026-08-25) | 4,816 | 5 | 0.00% |
| CPS | 112 | 112 (solo rung, resolved 2026-08-25, identical real numbers to COP) | 4,816 | 5 | 0.00% |
| GSV | 84 | 84 (solo rung) | 4,816 | 5 | 0.00% |
| SSV | 84 | 84 (solo rung) | 4,816 | 5 | 0.00% |
| STOD | 80 | 80 (solo rung) | 4,816 | 5 | 0.00% |
| FLL | 68 | 68 (solo rung, resolved 2026-08-25) | 4,816 | 5 | 0.00% |
| DTOS | 72 | 72 (solo rung) | 4,816 | 5 | 0.00% |
| JSR | 72 | 72 (solo rung) | 5,096 | 5 | 0.00% |
| BTD | 64 | 64 (solo rung, resolved 2026-08-25) | 4,816 | 5 | 0.00% |
| MAH | 60 | 60 (solo rung, resolved/wired 2026-08-25) | 4,816 | 2 | 0.00% |
| MSO | 60 | 60 (solo rung, resolved/wired 2026-08-25, identical real numbers to MAH) | 4,816 | 2 | 0.00% |
| NOT | 40 | 40 (solo rung, `instr_firstpass` x10, resolved 2026-08-25) | 4,816 | 2 | 0.00% |
| TRN | 52 | 52 (solo rung, `instr_firstpass` x10) | 4,816 | 2 | 0.00% |
| NEG | 40 | 40 (solo rung, `instr_firstpass` x10, same as NOT/UID/UIE/XOR) | 4,816 | 2 | 0.00% |
| OSR | 56 | 56 (solo rung, `instr_firstpass` x10, same as OSF) | 4,816 | 2 | 0.00% |
| OSF | 56 | 56 (solo rung, `instr_firstpass` x10, same as OSR) | 4,816 | 2 | 0.00% |
| UID | 40 | 40 (solo rung, `instr_firstpass` x10, bare 0-operand) | 4,816 | 2 | 0.00% |
| UIE | 40 | 40 (solo rung, `instr_firstpass` x10, bare 0-operand) | 4,816 | 2 | 0.00% |
| MCR | 16 | 16 (solo rung, `instr_firstpass` x10, bare 0-operand) | 4,816 | 2 | 0.00% |
| TND | 24 | 24 (solo rung, `instr_firstpass` x10, bare 0-operand) | 4,816 | 2 | 0.00% |
| ATN | 60 | 60 (solo rung, `instr_firstpass` x10, same as TAN) | 4,816 | 2 | 0.00% |
| DEG | 64 | 64 (solo rung, `instr_firstpass` x10) | 4,816 | 2 | 0.00% |
| RAD | 116 | 116 (solo rung, `instr_firstpass` x10, same as INSERT/SRT) | 4,816 | 2 | 0.00% |
| TAN | 60 | 60 (solo rung, `instr_firstpass` x10, same as ATN, INFERRED shape) | 4,816 | 2 | 0.00% |
| SQR | 52 | 52 (solo rung, `instr_firstpass` x10, same as TRN, INFERRED shape) | 4,816 | 2 | 0.00% |
| SWPB | 76 | 76 (solo rung, `instr_firstpass` x10) | 4,816 | 2 | 0.00% |
| XOR | 40 | 40 (solo rung, `instr_firstpass` x10, same as NOT/NEG/UID/UIE) | 4,816 | 2 | 0.00% |
| FIND | 100 | 100 (solo rung, `instr_firstpass` x10) | 4,816 | 2 | 0.00% |
| INSERT | 116 | 116 (solo rung, `instr_firstpass` x10, same as RAD/SRT) | 4,816 | 2 | 0.00% |
| BSL | 60 | 60 (solo rung, `instr_firstpass` x10, same as BSR) | 4,816 | 2 | 0.00% |
| BSR | 60 | 60 (solo rung, `instr_firstpass` x10, same as BSL) | 4,816 | 2 | 0.00% |
| FFL | 72 | 72 (solo rung, `instr_firstpass` x10, same as FFU) | 4,816 | 2 | 0.00% |
| FFU | 72 | 72 (solo rung, `instr_firstpass` x10, same as FFL) | 4,816 | 2 | 0.00% |
| SRT | 116 | 116 (solo rung, `instr_firstpass` x10, same as RAD/INSERT) | 4,816 | 2 | 0.00% |
| AVE | 176 | 176 (solo rung, `instr_firstpass` x10) | 4,816 | 2 | 0.00% |
| FAL | 104 | 104 (solo rung, `instr_firstpass` x10, same as FSC) | 4,816 | 2 | 0.00% |
| FSC | 104 | 104 (solo rung, `instr_firstpass` x10, same as FAL) | 4,816 | 2 | 0.00% |
| MAFR | 60 | 60 (solo rung, `instr_firstpass` x10, same (Axis,MotionInstruction) shape as MAH/MSO) | 4,816 | 2 | 0.00% |
| MASR | 60 | 60 (solo rung, `instr_firstpass` x10, same shape as MAH/MSO/MAFR) | 4,816 | 2 | 0.00% |
| MDW | 60 | 60 (solo rung, `instr_firstpass` x10, same shape as MAH/MSO/MAFR) | 4,816 | 2 | 0.00% |
| MASD | 60 | 60 (solo rung, `instr_firstpass` x10, same shape as MAH/MSO/MAFR) | 4,816 | 2 | 0.00% |
| MGSD | 56 | 56 (solo rung, `instr_firstpass` x10, (MotionGroup,MotionInstruction) shape, same as MGSR) | 4,816 | 2 | 0.00% |
| MGSR | 56 | 56 (solo rung, `instr_firstpass` x10, same shape as MGSD) | 4,816 | 2 | 0.00% |
| MCCP | 204 | 204 (solo rung, `instr_firstpass` x10, LOGIC weight only -- CAM operand's own tag data space still unmodeled) | 4,816 | 2 | 0.00% |
| MSG | 48 | 48 (solo rung, `instr_firstpass` x10, LOGIC weight only -- MESSAGE operand's own tag data space still unmodeled) | 4,816 | 2 | 0.00% |

**JSR target routines do NOT charge their own `fixed_base_per_routine`**
(that stays folded into the caller's `5,096` constant — charging it again,
what an early version of `report.py` did, overcounted every JSR-using
program by ~4,832 blocks; `RoutineLogic.is_jsr_target` flags a target
routine and `report.py` passes `charge_shell=False` for it). **But the
target's own instruction CONTENT is no longer skipped** — corrected
2026-08-31 (OQ-JSRPARAMCOST): a JSR target with substantial content was
found to genuinely cost real memory (max 13.37% residual on an isolated
content-scale sweep before the fix), now weighed with the same
per-instruction-type table as any ordinary routine via
`compute_routine_logic_bytes(..., charge_shell=False)`. Cut max residual
to 4.75% in isolation. A further composite-scale surcharge on top of this
per-instruction weight was found and wired 2026-09-02 — see the
`jsr_target_composite_surcharge_per_instr` entry below.

**JSR per-param cost — WIRED 2026-08-25 (OQ-JSRPARAMCOST).** The flat
72/rung JSR weight above only covers the base call; a real per-param cost
on top decomposes as `delta(n,R) = A(n) + B(n)*R` -- `B(n) = 4 + 20*n`
(the per-call-site marginal rate, added by `sizing/logic.py` per real
`JSR(...)` call, `n` read straight off the call's own 2nd argument -- the
declared param count Studio 5000 itself writes there) and `A(n) = 104 +
20*n` (the target routine's own one-time Parameters-block declaration
cost, charged once per distinct target by `report.py`, never per call
site). Verified end-to-end against all 6 real `jsr_paramcount_n05/08/10_
r00100/r01000` points: 4 exact, 2 (both n=8) off by the same small +8
universal noise seen elsewhere in this project.

**Branch bracket cost — WIRED 2026-08-30 (OQ-BRANCHDEPTH).** A branch
(`[...]`) is compiled to real BST/NXB/BND-family instructions -- one BST +
one NXB per extra leg + one BND, i.e. `(leg_count + 1)` instructions per
bracket group -- and every one of those instructions costs a flat **4
bytes**. Nested/staggered branches recurse: a branch nested inside a leg
adds its own `(leg_count + 1)` on top. `parser/logic.py`'s
`_branch_bracket_instruction_count` does a real bracket-matching scan
(not a naive regex) to count these, correctly distinguishing a branch-open
`[` from an array-index `Tag[5]` bracket by the character immediately
before it, and correctly ignores commas inside an instruction's own
argument list (paren-depth tracked) so a multi-arg call inside a leg
doesn't get miscounted as extra legs. Verified exact against all 17 real
`branchdepth_legs01/03/05` / `branchdepthc_legs02-30` /
`branchdepthstag_d01-06` points (10 flat leg-count + 6 nested-depth + the
1 trivial no-branch point) -- the SAME 4-bytes/instruction rate explains
both independently-built datasets, not two separate curve fits. FITTED,
not KNOWN -- only tested at n=1000 rungs and one tag shape (BOOL XIC
legs). See `docs/RESOLVED_QUESTIONS.md` OQ-BRANCHDEPTH for the full
derivation.
| LIM | 68 | **52** (LIM+OTE combined) | 4,816 | 5 | 0.00% |
| ONS | 56 | **36** (XIC+ONS+OTE combined) | 4,816 | 5 | 0.00% |
| MUL | 56 | 56 (solo rung) | 4,816 | 5 | 0.00% |
| DIV | 56 | 56 (solo rung) | 4,816 | 5 | 0.00% |
| MOD | 56 | 56 (solo rung) | 4,816 | 5 | 0.00% |
| MVM | 56 | 56 (solo rung) | 4,816 | 5 | 0.00% |
| MEQ | 48 | **32** (MEQ+OTE combined) | 4,816 | 5 | 0.00% |
| ADD | 40 | 40 (solo rung) | 4,816 | 5 | 0.00% |
| SUB | 40 | 40 (solo rung) | 4,816 | 5 | 0.00% |
| MOV | 36 | 36 (solo rung) | 4,816 | 5 | 0.00% |
| EQU | 36 | **20** (EQU+OTE combined) | 4,816 | 4 | 0.00% |
| NEQ | 36 | **20** (NEQ+OTE combined) | 4,816 | 5 | 0.00% |
| GRT | 36 | **20** (GRT+OTE combined) | 4,816 | 5 | 0.00% |
| GEQ | 36 | **20** (GEQ+OTE combined) | 4,816 | 5 | 0.00% |
| LES | 36 | **20** (LES+OTE combined) | 4,816 | 5 | 0.00% |
| LEQ | 36 | **20** (LEQ+OTE combined) | 4,816 | 5 | 0.00% |
| CLR | 32 | 32 (solo rung) | 4,816 | 5 | 0.00% |
| XIC | 20 | **4** (XIC+OTE combined) | 4,816 | 5 | 0.00% |
| XIO | 20 | **4** (XIO+OTE combined) | 4,816 | 5 | 0.00% |
| AFI | 20 | **4** (AFI+OTE combined) | 4,816 | 5 | 0.00% |
| TON | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| TOF | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| RTO | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| CTU | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| RES | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| OTE | 16 | 16 (solo rung, decomposition anchor) | 4,816 | 5 | 0.00% |
| OTL | 16 | 16 (solo rung) | 4,816 | 5 | 0.00% |
| OTU | 16 | 16 (solo rung) | 4,816 | 5 | 0.00% |
| NOP | 16 | 16 (solo rung) | 4,816 | 5 | 0.00% |

**LBL/JMP, fully resolved 2026-08-25 (MAJOR CORRECTION to the earlier
"104 combined, 52/52 unvalidated split" claim).** The `LBL(thisLabel)
NOP();` syntax fix cleared the real build errors — all 5 `instr_lbljmp_
n*` real captures came back clean. Re-deriving the combined weight from
that same data: exact linear fit at **120** blocks/pair across
n=10/50/100/1000/5000, 0 residual — the previously-documented "104" was
a miscalculation, not a measurement error (the raw data was always 120).
Two more real sweeps (`gen_lbljmp_rules.py`, 2026-08-24) then
independently decomposed it: `lbljmp_lblonly_n01/05/10` (pure LBL+NOP
rungs, zero JMP) isolates LBL+NOP at 80/rung — LBL alone = 80 - NOP's own
confirmed 16 = **64**; `lbljmp_manytoone_n02/05/10` (1 fixed LBL, JMP
count varying) isolates JMP alone at **40**/rung. Cross-check: LBL(64) +
NOP(16) + JMP(40) = 120, exactly reproducing the original 1:1-pair
sweep's combined number — three independent real captures agreeing
exactly. **KNOWN, not FITTED-uncertain, and valid for any LBL:JMP ratio**
(not just 1:1), since LBL and JMP were each isolated independently of the
other. Wired into `logic_instructions.weights` as `LBL: 64, JMP: 40`.

CTD intentionally not tested — zero real usage in the corpus (OQ-INSTRUCTIONSCOPE).

**Known gaps, still open:** MAM/MAJ/MAS/MRP against a real Axis tag —
**real capture 2026-08-25 shows all 4 FAIL to build** (`motioninstr_
mam/maj/mas/mrp_n00010/n00100`, `error_count` exactly equals rung count —
every single rung failed). The documented 2-operand `(Axis,
MotionInstruction)` signature that works for MAH/MSO/MAFR/MASR does NOT
work for these 4 — real, confirmed negative result, not just "untested."
Do not retry with a guessed variant; needs a real corpus or Studio-5000-
verified reference for the correct call shape before trying again.
MCCP camming: LOGIC weight now resolved and wired (204, see table above),
but the CAM operand's own tag data-space cost is a separate, still-
unmodeled predefined structure (OQ-PREDEFINED item below) -- a real
program using MCCP still throws a SizeError for that tag. MAPC did NOT
resolve -- real build failure on its x10 capture (20 errors/10 rungs).
Root-caused 2026-08-25 (see docs/OPEN_QUESTIONS.md OQ-MAPC-COMPAT): two
real generator bugs, an undeclared Axis_Cip_Drive tag and the same axis
tag wrongly reused for both slave/master positions. confirmed the
real rule: MAPC's slave/master just need to be two DISTINCT axis tags --
any combination of types works (virtual/virtual is fine), not a required
CIP-Drive/Virtual pairing. Both fixed,
corrected `instrfirst_mapc_v2`/`_v2_x10` files generated and awaiting
capture -- this is a 100%-accuracy priority, not a defer item.
CROUT's build failure is NOT a generator bug: CROUT is a Safety
instruction and requires a safety PLC CPU. Reclassified OUT OF SCOPE
alongside DCS, not a weight-table gap. Per-Task
overhead (`gen_task_overhead.py`) — real data now captured, see the
dedicated write-up in `docs/OPEN_QUESTIONS.md` (a real, clean, exactly
-1,472-per-extra-task finding, not yet wired pending a parser change to
distinguish per-Task/Program overhead from per-routine-in-the-same-
program, which doesn't exist yet). CMP/CPT operator/layout variance
(`gen_cmpcpt_layout.py` — see the CPT MAJOR CORRECTION above, this is now
confirmed a real, significant gap, not just an untested nice-to-have).

**2026-08-25 updates:** MAH/MSO wired in (see table above). Indirect
addressing (`gen_indirect_addressing.py`'s direct-index variant) shows
only a 4-block gap against the current engine on real data — already
effectively explained by existing indexed-array-tag handling, no separate
cost found. The tag-driven and arithmetic-offset index variants, however,
show large real costs NOT yet modeled — see `docs/OPEN_QUESTIONS.md` for
the raw numbers (~84 blocks/rung for a tag-driven index, ~108 blocks/rung
for an arithmetic-offset tag-driven index, vs. the direct-index case's
~0). Not yet decomposed into a proper weight (needs the base direct-index
rung's own instruction weight subtracted out first, and the instruction
used in that sweep identified) — flagged, not guessed.

Cross-program tag referencing (`gen_xprogref.py`) — **RESOLVED 2026-08-25**:
the -3,948 negative gap this note used to describe on the two-program
shared-alias case no longer exists against the current engine (real
3rd/4th-program data was sitting unreconciled and showed a clean, tiny
-16/rung per additional program instead). See RESOLVED_QUESTIONS.md
OQ-XPROGREF. No formula change needed.

## Tag-based alarm conditions, measured inside real content (2026-09-14)

`alarm_conditions` = 800 file base + 500 per condition + an associated-tag term
keyed on the resolved type of each `AssocTag1/2/3` target (BOOL 88, DINT/REAL
92, STRING 256, unresolved 256). Derived exactly from the 37-file `alarmcond_*`
batch; see memory_model.yaml for the derivation and for what was proved free
(alarm name length, message text, severity, delay values).

**First measurement inside real content, from the strip ladder.** Two real
programs were captured with and without their alarm elements, an exhaustive
element-tag diff confirming `AlarmCondition` / `AlarmConfig` / `HMIGroup` /
`AlarmConditions` were the only elements that moved:

| program | conditions | actual | predicted | per condition actual | per condition predicted |
|---|---:|---:|---:|---:|---:|
| `griffin_stackerline_1mar25` | 400 | 443,128 | 442,400 | 1,107.8 | 1,106.0 |
| `elmsdale_20251017r01` | 200 | 243,040 | 221,600 | **1,215.2** | 1,108.0 |

Within 0.16% on one file, 8.8% short on the other. In both programs every
condition hangs off a single BOOL array tag with `Input="[n]"`.

**Scale matters more than the error does: this is 19% and 21% of total
controller memory respectively — the second-largest category in both files.**

Distinct from a scheduled program named for alarms. Elmsdale carries both: 200
controller Alarm Manager conditions, and an `AlarmsAndMessages` program of
ordinary ladder. They are measured by different strip files and never
double-count.
Any statement that alarms are out of scope applies to the ALMD/ALMA
*instructions* (zero occurrences in the real set) and not to these. The
unexplained 107 bytes per condition is OQ-ALARMCONDREAL.

## The KNOWN register — measurements, not fits (2026-09-18)

`confidence: FITTED` on a block says how MOST of that block was derived. It
under-states the constants inside it that were measured alone, at several counts,
with zero residual — and a constant left reading FITTED gets re-derived, which has
already cost this project whole sessions. These carry their own
`*_confidence: KNOWN` key beside the value in `memory_model.yaml`, and
`tests/test_measured_known_constants.py` pins each one to both its value and its
tier, so changing either without updating the evidence fails the suite.

| constant | value | rows | what those rows span |
|---|---:|---:|---|
| `jsr_param_cost.b_multiparam_extra` | 4 | 13 | call counts 10 / 100 / 1,000 × param counts 1…15, plus `jsr_multiret_n02` as an independent decider on the keying |
| `jsr_target_declaration.per_target` | 160 | 13 | distinct-target counts 1…50, two generators, name lengths 4…40 |
| `jsr_target_declaration.sbr_ret_operand_bytes` | 112 | 16 | target counts 1 / 10 / 50 / 200, plus 12 parameterless `subrtn_*` controls holding at exactly 0 |
| `logic_instructions.weights.DTR` | 40 | 3 | 10 / 100 / 1,000 rungs against a weight of zero |
| `cpt_expression.leading_tier1_run_bytes` / `_length` | 4 / 2 | 28 | four arrangements × operator counts 3…9, tier counts held fixed |
| `structured_text.assignment_one_operator_class_bytes.dint.bitwise` | 124 | 3 | `stc_prem1_{and,or,xor}`, all three at the same +84 over additive |
| `…dint.exponent` | 204 | 1 | `stc_prem1_pow` |
| `structured_text.assignment_operator_premium.dint.exponent` | 38 | 1 | `stc_opkind_pow` at four operators |
| `…real.multiplicative` / `…real.exponent` | 0 / 8 | 2 | `stc_premreal_mul` / `stc_premreal_pow` |
| `structured_text.real_dest_source_conversion_bytes` SINT / INT / LINT | 92 / 104 / 0 | 4 | one file per type, cross-checked exactly by `stc_conv_mixed` |
| `structured_text.st_aoi_call_routine_bytes` | 264 | 7 | three files at ONE call against four at a thousand |
| `logic_instructions.weights` AND / OR / RTOS / LFU / UPPER | 40 / 40 / 72 / 72 / 84 | 15 | 10 / 100 / 1,000 rungs each — **confirmed** by the DTR sweep, not first measured by it |

What stays FITTED, deliberately: `a_base`, `a_per_param` and `b_per_param` in
`jsr_param_cost`; `st_aoi_call_bytes` and `st_aoi_call_per_param_bytes`; the ST
base ladder and the two-tier CPT mix rates. Those were regressed, and marking the
blocks they live in KNOWN would launder them.

## Change log

Log every constant change here with date + which sample(s) drove the change, so
there's a record of *why* a number is what it is, not just what it currently is.

- **2026-09-18** — **The in-depth open-questions review. Seven constants wired,
  all measured with zero residual, and the real set went 1.6894% -> 1.6566%
  mean absolute error over the sixteen held-out programs, every one of them the
  right way.** Two corpus families went from badly wrong to essentially exact:
  Structured Text 8.3291% -> 0.0091% (60 of 69 rows byte-exact) and the
  `unweighted_*` instruction sweep 4.6865% -> 0.1574%.

  1. **`jsr_param_cost.b_multiparam_extra = 4`**, keyed on TOTAL operands
     (inputs plus outputs) at a threshold of 2. Solved by separating the
     per-call slope from the per-file constant across every paramcount row with
     more than one call count: `p = 4, c = -176` reproduces thirteen rows at
     call counts 10, 100 and 1,000. `jsr_multiret_n02_r01000` decides the
     total-operand keying: +3,952 under the input-only reading, -56 under this
     one. (OQ-JSRPARAMCOST)
  2. **`jsr_target_declaration.per_target` 152 -> 160.** The zero-param
     multi-target sweep's residual was exactly `8t - 280` across t = 1..50, two
     generators, name lengths 4..40. (OQ-JSRPARAMCOST)
  3. **`jsr_target_declaration.sbr_ret_operand_bytes = 112`**, once per target
     whose SBR/RET carry operands. `unweighted_sbrret_t{001,010,050,200}` give
     exactly 112 per target at every step; the 12 parameterless `subrtn_*` files
     still measure exactly 0, so `SBR: 0` and `RET: 0` stay correct and the
     OPERANDS are what cost. It also collapses the two JSR file-level constants
     from 96 apart to 16 apart. (OQ-VERIFINSTR)
  4. **`DTR = 40` per rung.** It had NO weight at all, not the 16 the open
     question claimed. `unweighted_dtr_n{10,100,1000}` = +404 / +4,004 /
     +40,004. Its five siblings in the same sweep read the universal +4, so
     AND 40, OR 40, RTOS 72, LFU 72 and UPPER 84 are now confirmed by real data
     rather than assumed. (OQ-VERIFINSTR)
  5. **Structured Text gets its OWN operator classification**, because it
     measurably is not the ladder CPT tier table. One-operator DINT lookups by
     operator class: additive 40, multiplicative 56, bitwise 124, `**` 204.
     Per-operator premiums at two or more operators: DINT bitwise 0 and `**` 38
     (not tier 3's 80); all-floating-point multiplicative 0 and `**` 8. The
     premium follows the OPERANDS, not the destination -- `st_expr_cpt_mirror`
     is the only file in the corpus that separates those two readings.
     (OQ-STEXPR, OQ-STEXPR-OPERATOR)
  6. **ST REAL-destination conversion is per SOURCE, keyed on the source's own
     type**: DINT 48, SINT 92, INT 104, LINT 0. `stc_conv_mixed` is an
     independent additivity check and lands to the byte. Plus
     **`st_aoi_call_routine_bytes = 264`**, once per ST routine containing any
     AOI call -- separated from per-call by three files at one call against four
     at a thousand. (OQ-STEXPR)
  7. **`cpt_expression.leading_tier1_run_length = 2` / `_run_bytes = 4`.**
     Arrangement is real: a two-tier mix costs 4 more iff EXACTLY TWO tier-1
     operators precede the first tier-2 one. The six +4 rows in the 28-file
     `cptarrange_*` sweep are exactly the six run-of-2 rows, and the rule
     retro-explains the alternating/grouped n=5 pair, their agreement at n=11,
     and the three (2,1) files stuck 4 short -- none of which it was fitted to.
     (OQ-CPTARRANGE)

  **Two parser defects found and fixed on the way, both of the
  right-answer-wrong-reason kind.** `_DESTINATION_ARG` gave COP, CPS, FLL, BSL
  and BSR a destination position of -1, which inspects the LENGTH operand; it
  charged correctly only because a literal length does not resolve to BOOL.
  And `sizing/structured_text.py`'s `_NUMBER` matched the digits inside
  identifiers, so `R0 * R1` counted five integer literals -- harmless until the
  ST operator premium started keying on exactly that. Also added five
  word-destination writers the table was missing, GSV among them at 363 real
  occurrences.

  **Measured and deliberately NOT wired, with the count of what each candidate
  fixes and breaks:** the REAL-dest CPT 5-operator base (324 all-REAL against
  328 for three older parenthesised/float-literal families -- every candidate
  change fixes 4 rows and breaks 10); `**` on the REAL-dest path (+8 per extra
  operator, entangled with that base); the integer-destination float literal
  (+120 to +188 per rung, the largest unpriced CPT term in the project, and not
  linear in the literal count over three points); the POINT I/O per-card
  connection-format correction (-1,136 Enhanced, -852 Enhanced Data, Optimized
  flat -- unwireable because 34 of the 45 real POINT I/O cards are structurally
  indistinguishable between the two formats that differ by 1,136); and the
  module-NAME law (8 bytes per 8 characters with the first 8 free, one bucket
  off the KNOWN shared identifier law, whole real exposure 4,816 bytes).

- **2026-09-17** — **Four families taken from badly wrong to byte-exact, and
  the real-set headline moved the WRONG way as a result. Both halves are the
  finding.** Wired, every one measured with zero residual:

  1. **EVENT instruction = 56 bytes.** It had no weight at all.
     `uwclose_event_n{10,100,1000}` = 56n + 8 exactly, three counts over 100x.
  2. **1756-EN2T = 432, not the 1672 fallback.** `closeout_en2t_n{1,2,4,8}`
     gives a flat −1,240 per module with zero curvature; the catalog had been
     force-averaged out of the table and left on the default.
  3. **The six 2198 -ERS3 drives are NOT identical and carry no repeat
     discount.** 24 recaptured rows fit `total = C + n x r` at 23 of 24 points:
     r = 3,640 per copy (3,376 for S130), C = 23,120 except D012/S086 at 19,112.
     The engine had been charging 4,624 per copy at every count. The one
     outlier, `asmclose_2198_d012_ers3_n08`, is excluded rather than fitted.
  4. **A Task's own name costs, with a minimum of 8.** Programs and routines
     are floor(len/8) beyond doubt (`identnamelen_prog_c01..c07` all cost 0);
     a task never costs zero. All five task rows now byte-exact.

  **Real set 1.6112% -> 1.7036% mean.** It got worse because every one of these
  corrections reduces a prediction, and eleven of the sixteen real programs
  UNDER-predict. The five that over-predict all improved --
  `griffin_stackerline` went **−0.658% -> −0.069%**, and Griffin is the program
  whose strip ladder independently measured a module over-charge of 15,580,
  which this removes. Two independent instruments agreeing is worth more than
  the headline. This is the fifth time a measured-exact correction has made the
  headline worse, and it means the honest under-charge is larger than the number
  has ever suggested -- see OQ-REALUNDER. A constant that is exact on 23 of 24
  measured points is not reverted to flatter a mean; that is precisely how the
  6,384-per-drive ERS3 over-charge propped up this project's accuracy for weeks.

- **2026-09-14** — **No constant changed. The strip ladder was captured on two
  real programs and it overturned a standing hypothesis rather than producing a
  number.** Compiled ladder is OVER-charged on both files (−29,676 Elmsdale,
  −9,220 Griffin), killing five segments' worth of the assumption that the
  real-file deficit lives in `routine_logic`. Axis is byte-exact on Griffin over
  778,728 bytes. Tag-based alarms measured at 19–21% of total memory with the
  wired model within 0.16% on one file and 8.8% short on the other
  (OQ-ALARMCONDREAL). A bare real controller shell is 7,800 (L81E) / 4,072
  (5069) above the baseline, which is unpriced shell content and NOT a wrong
  baseline constant (OQ-CTLSHELL). Nothing wired: three of seven ladder
  categories disagree in sign between the two files, which is two data points
  and the shape of a constant that is really a function of something
  unidentified.
- **2026-08-22** — Landed in code (`memory_model.yaml`/`constants.py`/
  `udt.py`/`report.py`): per-tag flat overhead (`84 + 8×floor(len/8)`),
  UDT DataType-definition cost (`168 + 16×member_count` + name cost +
  BOOL-run bonus, one-time per distinct type including nested-only-used
  types), and flipped `udt.alignment_confidence` UNKNOWN→KNOWN (OQ-ALIGN
  resolved).
- **2026-08-22, same day** — Logic instruction weight table also landed in
  code: `parser/logic.py` (RLL rung tokenizer), `sizing/logic.py`
  (`compute_routine_logic_bytes`), wired into `report.py` as
  `tier="estimated"` entries. Caught and fixed a real double-counting bug
  the same day it landed: several sweep files' raw per-file weight was
  really an instruction+companion-OTE combined measurement (e.g. XIC's
  file is `"XIC(tag)OTE(tag);"`, not XIC alone), so naively summing raw
  weights by token occurrence double-counted OTE wherever it appeared as a
  companion. Decomposed 13 instructions (XIC/XIO/AFI/EQU/NEQ/GRT/GEQ/LES/
  LEQ/LIM/MEQ/CMP/ONS) into isolated per-instruction weights using OTE's
  own clean 16 as the anchor. Verified against real captured data for 6
  affected instructions (XIC/ONS/LIM/MEQ/EQU/CMP at n=1000) — engine
  prediction matches real Capacity delta exactly on all 6 after the fix.
  `gen_logic_random_mix.py` (the random-combination validation batch)
  rewritten to predict via the real engine instead of a hand-rolled
  formula, for the same reason.
- **2026-08-22, same day, second fix** — a JSR target routine (e.g.
  "SubTest") was also getting double-counted: the engine charged it its
  own independent `fixed_base_per_routine` on top of the calling routine's
  `jsr_fixed_base_per_routine`, but the target's cost is already folded
  into that constant (confirmed: its content was fixed across the entire
  calibration sweep). Added `RoutineLogic.is_jsr_target` and skip such
  routines entirely in `report.py`. All 205 real logic_instr data points
  (every instruction with real captured data, including all 5 JSR points)
  now match the engine's prediction exactly, 0 mismatches.
- **2026-08-22, same day, tag/UDT side** — ran the same adversarial check
  against the tag/UDT side (every real `tag`/`tags`/`udt`-category manifest
  row) and found three more real bugs, all fixed same-day: (1) the
  udt_definition formula's two halves double-counted a shared base
  constant (see "UDT DataType-definition cost" above for the full fix,
  `160` replacing the old `168`+`224`); (2) `declared_member_count` for an
  all-BOOL UDT computed 0 (excluded bit-aliases instead of hidden backing
  SINTs); (3) the BOOL-run bonus was flat +32 regardless of how many
  separate runs existed, instead of +32 per run. `udt`-category real data
  points went from 103/103 mismatching (most off by 100s-1000s of blocks)
  to 50/103 mismatching, and every one of those 50 is now either an
  already-flagged known gap (array dimension surcharge, small-N count/
  member anomaly, atomic-type micro-variance, OQ-ARRAYPACK/UDTARRAYALIGN)
  or the newly-surfaced custom-string-definition-cost gap noted above.
- **2026-08-23** — Full-corpus rebase batch: re-ran the current engine
  against every clean manifest.csv row (546) and compared to real
  `actual_bytes`. Went from 0 exact matches / 16 engine errors to 77 exact
  matches / 0 engine errors. Landed: `empty_project_baseline` (13,296,
  KNOWN, see OQ-BASELINE), 6 new `predefined_structures` (MOTION_GROUP,
  AXIS_CIP_DRIVE, COORDINATE_SYSTEM, AXIS_SERVO, AXIS_VIRTUAL,
  MOTION_INSTRUCTION), new `predefined_array_structures` section
  (CAM_PROFILE), `custom_definition_cost` (206) for STRING-family UDT
  definitions, SIZE (128/rung) and LBL+JMP (104/pair, unvalidated 52/52
  split) logic weights. Also fixed a real pre-existing UI bug found while
  testing the new baseline entry: `ui/hierarchy.py`'s `build_hierarchy()`
  crashed with `IndexError` on any file with a `udt_definition` entry
  (path has no `:` for the `<scope>/<name>` split it assumed) — would have
  crashed the live UI on most real programs; fixed with a `NON_TAG_GROUPS`
  special case. **Also found, not fixed:** the CPT=452/rung weight is
  confirmed wrong as a general constant (see the MAJOR CORRECTION in the
  logic-instruction-weights section above) — real per-rung CPT cost is
  expression-complexity-dependent. **Also found, not fixed:** AOI
  definition cost is a large (1,100-3,600+ block) unmodeled gap, real
  sweep data now gathered (see OPEN_QUESTIONS.md OQ-AOIDEF) but not clean
  enough across all axes to wire in yet.
- **2026-08-27** — Two more real gaps closed same day, both flagged above
  as "not clean enough yet" / "blocked": (1) AOI definition cost
  (OQ-AOIDEF) — the full real sweep batch had actually landed captured,
  just sat unprocessed; wired a per-type declared-item rate (see "AOI
  sizing" above). (2) Task/Program/Routine shell overhead (OQ-TASKOVERHEAD)
  — `fixed_base_per_routine` was being charged once per emitted routine
  regardless of Task/Program structure, over-predicting any multi-routine
  file; now charged once per file plus real per-extra-Task/Program/routine
  marginal costs (`task_program_overhead`: routine_extra=272,
  program_extra=484, task_extra=700). Verified exact/near-exact against
  the 3-file disentangle batch and the original n02-n04tasks sweep; broad
  regression across all 1,059 captured manifest rows went from 279 to 292
  exact matches with zero real regressions (see OPEN_QUESTIONS.md
  OQ-TASKOVERHEAD for the full derivation and regression numbers).
- **2026-08-29** — Firmware-version + 5069-safety-capable-model baseline
  deltas wired (OQ-BASELINE-PROCFW; see "Empty-project baseline" above for
  the full formula). New `memory_model.yaml` sections
  `firmware_baseline_delta` (v31/v32=+11,240, v33=+14,248, v34/v35/
  unlisted=+0) and `safety_capable_baseline_delta` (+296, gated on
  `ProcessorType` ending `S2`/`S3`), both ESTIMATED tier, read via
  `report.py` off the L5X root's `SoftwareRevision`/`Controller/
  @ProcessorType`. Validated against all 50 real (untainted)
  `fw_catalog_matrix` rows: every one now predicts within 16 bytes, down
  from errors up to 14,552. **Correction, same day:** a prior pass had
  claimed a real "+304 v38 delta" and a real "-1,044 byte AOI-array-
  parameter overshoot anomaly" — both were misreadings of
  `WINDOW TITLE MISMATCH`-flagged manifest rows (contaminated capture
  data, wrong file's numbers), not real engine gaps. Both rows' capture
  columns cleared per CLAUDE.md's standing rule; neither claim is wired,
  both stay open awaiting real (clean) capture.
- **2026-08-29, same day** — Found and fixed a real process gap: 7
  OQ-CMPCPTLAYOUT diagnostic CPT files had real capture data from
  2026-08-27 sitting unreconciled in manifest.csv, never wired. Closed the
  all-3-tier-mix CPT thread: `base_by_remainder[operator_count % 3] +
  4 * pow_operand_count` (`base_by_remainder = {0: 72, 1: 116, 2: 144}`),
  confirmed 0 residual across all 9 real all-3-tier data points on file
  (operator counts 4-14) — corrects and replaces an earlier
  `44*T1-116*T2+76*T3+72` attempt that, checked directly, didn't actually
  reproduce the points it was claimed to fit. Wired in
  `CptExpressionModel.cost_for`/`memory_model.yaml` cpt_expression. The
  REAL-operand/float-literal thread stays open — investigated with the
  other 4 files' real data and found genuinely non-monotonic (1 REAL
  operand costs MORE than 2), ruling out any simple per-count formula; see
  OPEN_QUESTIONS.md OQ-CMPCPTLAYOUT for the full finding and a real
  hypothesis (type-promotion-point count, not operand count) for the next
  probe batch.
- **2026-08-29, same day, full manifest.csv audit.** Re-ran every category with real capture data through
  the live engine, not just the categories a previous pass happened to
  check. Found 90 of 126 `modules`-category rows were never checked
  against the engine at all despite having real data since 2026-08-22.
  Wired `module_overhead_by_catalog` (51 catalogs, real range -793 to
  +10,497, replacing the flat 1,672 FITTED-from-2-points estimate for
  those catalogs) — see "Module / I/O tag sizing" above. Real exact-match
  rate on the 126 real module rows: 1/126 -> 54/126. Two real threads
  left open, both genuine architecture gaps (non-flat multi-module
  marginal cost; a few connection-variant-dependent catalogs), documented
  in OPEN_QUESTIONS.md OQ-MODULEIO rather than force-fit.
- **2026-08-29, same audit, JSR output/return-param cost.** OQ-JSRPARAMCOST
  had been marked "fully wired" (2026-08-25), but that only ever covered
  INPUT params -- the calibration data's RET() was always empty, so
  output/return-value args were never modeled at all. Two real captures
  (`jsr_mixedio_5in_2out_r01000`, `jsr_multiret_n04_r01000`, both from
  2026-08-23) sat unreconciled, off by +40,040 and +40,332. Both isolate
  to ~20/output-arg, matching `b_per_param` exactly -- wired as
  `output_param_cost=20`, charged per output arg per call site.
  `jsr_paramcount_n05/08/10_r01000` (input-only, unaffected) stay exact/
  near-exact; `jsr_mixedio` now off by +40 (noise-band); `jsr_multiret`
  by +332 (the callee's one-time `A(n)` cost almost certainly also needs
  an output-param term, too small to isolate from a single sample --
  reopened as OQ-JSRPARAMCOST in OPEN_QUESTIONS.md rather than left
  silently wrong in RESOLVED_QUESTIONS.md).
- **2026-08-29, same audit, 1769-series real baseline + v30.** 9 more
  real `fw_baseline`-category points (8 real 1769-series CompactLogix
  5370 captures + 1 real v30 point) sat unreconciled. Wired
  `catalog_baseline_delta` (exact-`ProcessorType`-string keyed, real
  range +51,488 to +80,832 -- a single expansion-module suffix character
  changes the value by 13,000+ bytes, e.g. `1769-L24ER-QB1B` vs
  `-QBFC1B`, so kept exact-match only, no prefix/suffix generalization)
  and added `"30"` to `firmware_baseline_delta` (+11,160, single real
  MANUAL ENTRY point -- this project's SDK can't build v30 exports at
  all, so there's no automated capture path). All 29 real `fw_baseline`
  rows now checked: 17 exact, 6 within the small per-file noise band
  (<=16 bytes), 3 already-documented small catalog-model variance
  (+32 bytes), 3 already-documented Safety-Task-bearing-file gap
  (see "Empty-project baseline" above).
- **2026-08-31, JSR target content WIRED.** Real content-scale sweep
  (`jsr_target_content_scale_{010,050,100,150}`) proved a JSR target
  routine's own instructions were priced at $0 (max 13.37% residual).
  `report.py`'s `is_jsr_target` branch now weighs the target's content
  via `compute_routine_logic_bytes(..., charge_shell=False)`, using the
  already-confirmed per-instruction-type table, not a new constant. Cut
  max residual to 4.75%. See OPEN_QUESTIONS.md OQ-JSRPARAMCOST.
- **2026-08-31, AOI internal Logic-routine content WIRED.** Same gap,
  AOI-side: real isolation sweep (`aoi_logic_scale_{000,010,050,100}`,
  `aoi_multiroutine_control/_real`) proved AOI internal routine content
  was priced at $0 (max 12.02% residual) and that per-routine count
  doesn't matter, only total content. New `parser/logic.py`
  `parse_aoi_internal_logic()` aggregates all of an AOI's internal
  routines into one pseudo-routine, weighed the same way. Cut max
  residual to 0.55%. See OPEN_QUESTIONS.md OQ-AOIINTERNALLOGIC.
- **2026-09-02, real per-catalog module overhead for 6 more catalogs.**
  Derived exact via chained-residual solving across real `modulesweep_*`
  captures where multiple unmodeled catalogs stack in one file (subtract
  already-solved catalogs to isolate the next unknown, confirmed exact to
  the byte across 2- and 3-catalog chains): `1756-CNB/D`=448,
  `1756-DHRIO/E`=1392, `1756-DNB`=7536, `1734-OA4/C`=1196,
  `1794-ACN15/C`=1640, `1794-IB16/A`=1536. Also fixed `report.py`'s
  module-overhead exclusion logic: it previously did a BLANKET exclusion
  of any rack-aliased or legacy-network-bridge module regardless of
  catalog; now checks the per-catalog table first
  (`ModuleOverheadModel.has_real_data_for`) and only falls through to
  unmodeled/$0 if that specific catalog has no real entry.
- **2026-09-02, composite-scale content surcharge WIRED (OQ-COMPOSITESCALE).**
  `gen_composite_realistic_v2.py`'s 50-file batch (composites with real
  AOI-internal-logic AND a real JSR-target routine, exercising both gaps
  above together at project scale for the first time) under-predicted by
  a mean +5.16% even with both fixes above already wired. Linear
  regression (no intercept) on the 22 real, error-free, fully-modeled
  files: `residual ≈ 20.155 * aoi_logic_instr_count + 47.331 *
  jsr_target_instr_count`, R²=0.6619511766511494 — beat a flat-%-of-total
  model (R²=0.6015) and a combined model (barely better, R²=0.6631, with
  the flat-% term going slightly negative). Wired as
  `aoi_logic_composite_surcharge_per_instr: 20` and
  `jsr_target_composite_surcharge_per_instr: 47`, additive on top of the
  per-instruction content weight at both sites. Cut mean abs error on
  those 22 files from 5.16% to 1.06% (max 5.66%); all 45 error-free v2
  files average 1.17% mean abs error. FITTED, not KNOWN — R²=0.66 leaves
  real unexplained variance, and the JSR:AOI rate ratio (~2.3x) isn't
  mechanistically understood yet, just what the data shows.

## Export scope: what a partial export may and may not be charged

Wired 2026-09-04 (`parser/export_scope.py`, OQ-EXPORTSCOPE). Studio 5000
exports at six granularities and the root element declares which:
`TargetType` = `Controller` | `Program` | `Routine` | `Rung` |
`AddOnInstructionDefinition` | `DataType`, with `ContainsContext="true"` on
every partial one. Inside a partial export the exported thing is marked
`Use="Target"` and everything it merely references is `Use="Context"`.

**Only a whole-controller export (`TargetType="Controller"` AND
`ContainsContext="false"`) may be charged:**

| constant | why it is project-only |
|---|---|
| `empty_project_baseline` | a controller's fixed scaffolding |
| `firmware_baseline_delta` | there is no "firmware baseline of a rung" |
| `catalog_baseline_delta` | keyed on ProcessorType, a project property |
| `safety_capable_baseline_delta` | same |
| `task_program_overhead` (the whole shell decomposition) | fitted as "one base + per-extra task/program/routine ACROSS A PROJECT"; a partial export's routines are mostly context, so counting them invents a project |

Everything else — tag storage, UDT/AOI definition cost, per-instruction
logic weights — applies normally to whatever the file actually contains.

**Target vs context.** An element is target-scope if it or an ancestor
carries `Use="Target"`. The nesting is not intuitive: in a Rung export the
chain is `Program Use="Context" > Routines Use="Context" > Routine
Use="Context" > RLLContent Use="Context" > Rung Use="TARGET"`, so "is it
inside a context container" is the wrong test — only the nearest `Use`
attribute up the chain decides.

`split_totals()` reports **target** (what was exported), **context**
(declarations it references, which cost their bytes only if the destination
controller does not already have them, since rungs, routines and
programs can reference controller tags) and **project** (base load, zero
on any partial export by construction).

**Two parser bugs this exposed, both real and both fixed:**
1. A rung export's containing `Routine` element carries `Use` and `Name` but
   **no `Type` attribute**, so requiring `Type == "RLL"` parsed every rung
   export to zero routines and never sized the exported rung at all. Routine
   language is now inferred from the content child (`RLLContent` → RLL,
   `STContent` → ST, …) when Type is absent.
2. A target routine inside a context program was classified as context,
   reporting target = 0, because routine and program-tag entry paths share
   the `program:<P>/<X>` prefix and the program was checked first.
