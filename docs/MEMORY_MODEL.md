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

**Unsigned atomic types, added 2026-08-30.** James, reviewing a real
confidential customer project (not committed, never named here) that
this engine couldn't fully size: "UINT is the same as INT with the last
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
2026-08-25).** Chasing James's "strings must be 100% closed" directive
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
from James's own conversion+capture pipeline against `gen_predefined_probe.py`'s
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

**CAVEAT, James 2026-08-23: "your empty project baseline is not a constant
and will change based on processor and firmware. You need to be aware of
this."** Confirmed true, and **partially wired 2026-08-29** -- see
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
  ASSUMED).** James (100% confident from field experience): `BOOL, DINT,
  BOOL` = 8+32+8 = 6 bytes; `DINT, BOOL, BOOL` = 32+8 = 5 bytes — i.e. no
  4-byte alignment padding at all, and a run of consecutive BOOLs shares one
  backing byte but a non-BOOL member breaks the run, forcing the next
  BOOL(s) onto a fresh backing byte. `compute_udt_size` already produced
  this unchanged (`tests/test_sizing.py::
  test_bool_packing_run_broken_by_non_bool_member`). Now backed by real
  Capacity-tab data too — every real UDT test across the whole per-tag/
  per-UDT-definition sweep (dozens of samples, see per-tag/definition
  sections above) landed on predictions consistent with tight-packing, not
  just James's field opinion. `udt.alignment_confidence` in
  `memory_model.yaml` flipped UNKNOWN→KNOWN.
- Nested UDT: recursive — a UDT member's size is that UDT's total computed
  size. James also believes (stated with less certainty, "I also assume")
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

**AOI definition cost (FITTED, wired 2026-08-27, OQ-AOIDEF):** an AOI's own
Parameters/LocalTags declaration (independent of any instance tag) has a
real, separate one-time cost — `base + rate * declared_item_count`, same
relationship a UDT definition has to a UDT-typed tag. `base = 1184`.
`declared_item_count` excludes `EnableIn`/`EnableOut`; `InOut` params are
already excluded upstream (reference, not storage). Rate is per-type when
every declared item shares the SAME type — `BOOL=16, SINT=18, INT=18,
DINT=20, REAL=20, LINT=24` bytes/item — falling back to the flat `20`
rate for a mixed-type AOI definition. That fallback is deliberate, not a
placeholder: real data (`aoi_boolpack_interspersed20_def_only`, 20 BOOL +
20 DINT) shows the per-type rates do NOT compose additively once BOOL sits
alongside another type — a naive per-type sum under-predicts that file by
80 bytes, while the flat rate matches it exactly. Live-recomputed against
all 85 captured AOI manifest rows: 32 exact, 52 within 1%, 1 at 2.10%
(a separate array-vs-definition-cost interaction, not a def-cost miss —
see AOI_KNOWLEDGE_MAP.md item 3).

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

## Module / I/O tag sizing

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

All originally-excluded instructions are now resolved. SIZE, BTD, COP,
CPS, and FLL all had the same real array-subscript bug (see below);
all five are now fixed, re-captured, and in the table with exact fits.
The EQU n=100/CMP n=10 garbled-value glitch this used to also flag is
long since fixed and re-captured.

**Root cause of the CPS/COP/FLL/SIZE/BTD glitch, found 2026-08-22 (James
spot-checked and caught it):** these instructions take an array-typed
operand, and the generator was emitting the bare tag name (`Arr`) instead
of a subscripted reference (`Arr[0]`) — real Rockwell syntax always
requires `[index]` on an array-typed operand (confirmed against the real
corpus, e.g. `BTD(CNET_ENTRY_STATUS[11],12,...)`). SIZE has the same bug
via its STRING operand, which needs `.DATA[0]`, matching the real corpus
`SIZE(_DisplayBuffer.szString[0],0,...)`. A file with this bug still
converts "ok" through `l5xgit l5x2acd` (see the SDK-verification note
below) — that's why it wasn't caught earlier and why every instance came
back at an identical byte count regardless of rung count (the program
never actually compiled at scale, per James). Fixed in `gen_logic_sweep.py`;
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

**SDK-verification finding (James asked, 2026-08-22): does `l5xgit
l5x2acd` catch bad programs before James burns real capture time on
them?** No. Confirmed empirically via `samples/convert_log.csv` (398 "ok"
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

**JSR target routines are skipped entirely by the engine, not charged
their own fixed_base.** Found the same day as the paired-instruction fix
above, same root cause: the JSR sweep's target routine ("SubTest", always
exactly one `NOP();` rung, never varying across the whole 10-5000 count
sweep) had its entire cost absorbed into the calling routine's `5,096`
constant, since it was the same constant across every calibration point.
Charging SubTest its *own* independent `fixed_base_per_routine` on top
(what an early version of `report.py` did) overcounted every JSR-using
program by ~4,832 blocks. `parser/logic.py`'s `RoutineLogic.is_jsr_target`
flags any routine that some other routine in the same program calls via
JSR; `report.py` skips those entirely when building logic entries.
Verified against real data for all 5 JSR count points, exact match. Only
confirmed for a trivial (1-NOP-rung) target — a JSR target with
*substantial* content is untested territory, same caveat as OQ-JSRSHARED.

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
tag wrongly reused for both slave/master positions. James confirmed the
real rule: MAPC's slave/master just need to be two DISTINCT axis tags --
any combination of types works (virtual/virtual is fine), not a required
CIP-Drive/Virtual pairing. Both fixed,
corrected `instrfirst_mapc_v2`/`_v2_x10` files generated and awaiting
capture -- James called this a 100%-accuracy priority, not a defer item.
CROUT's build failure is NOT a generator bug -- James, 2026-08-25: "Crout
is safety... requires a safety plc cpu." Reclassified OUT OF SCOPE
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

## Change log

Log every constant change here with date + which sample(s) drove the change, so
there's a record of *why* a number is what it is, not just what it currently is.

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
- **2026-08-29, same day, full manifest.csv audit** (James: "make another
  in-depth pass"). Re-ran every category with real capture data through
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
