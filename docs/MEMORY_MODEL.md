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
| INT | 2 | |
| DINT | 4 | |
| LINT | 8 | |
| REAL | 4 | |
| STRING (built-in) | 4 + 82 = 86 | 4-byte LEN (DINT) + 82-byte DATA (SINT[82]) default |
| Custom string type | 4 + N | 4-byte LEN + N-byte DATA, N = user-defined max length |

## Predefined structure types (KNOWN)

Firmware-native structures referenced by name in L5X Tag/Member DataType
attributes but never given a member list in `Controller/DataTypes` --
Logix Designer resolves them internally, so there's nothing to recurse.
Only types with a well-documented, version-stable layout are modeled here;
everything else found in real samples (MESSAGE, PID, AXIS_CIP_DRIVE and
other motion/safety structures) is deliberately left unsized rather than
guessed -- see OQ-PREDEFINED.

| Type | Bytes | Notes |
|---|---|---|
| TIMER | 12 | 1 status DINT (EN/TT/DN bits) + PRE (DINT) + ACC (DINT) |
| COUNTER | 12 | 1 status DINT (CU/CD/DN/OV/UN bits) + PRE (DINT) + ACC (DINT) |
| CONTROL | 12 | 1 status DINT (EN/EU/DN/EM/ER/UL/IN/FD bits) + LEN/PRE-equivalent (DINT) + POS (DINT) |

## Alias tags (KNOWN)

A Tag with `TagType="Alias"` carries no `DataType` of its own in the L5X
(only an `AliasFor` pointing at another tag or a module I/O point) and
consumes no memory beyond what that target already accounts for. Sized as
0 bytes, tagged `data_type=ALIAS`, confidence KNOWN -- not an error, not a
guess, just genuinely zero-cost. Confirmed against real production L5X data
(2026-08-20): 294 of 3394 tags across 4 real files were Alias tags with no
DataType, ~21% of everything that failed to size before this was handled.

## UDT packing (ASSUMED, pending OQ-ALIGN / OQ-BOOLPACK confirmation)

- Recurse members in declared order.
- BOOL members: pack 8 to a backing SINT byte, per the existing BIT-member
  generation convention (one hidden SINT per byte of BOOL members, incrementing
  BitNumber 0–7, new SINT for bits 8–15, etc).
- Non-BOOL members: size = atomic/nested-UDT size, per table above.
- Alignment/padding between members: **ASSUMED tight/no padding, confidence
  raised 2026-08-20 but still not KNOWN.** James (100% confident from field
  experience, not yet Phase-3-measured): `BOOL, DINT, BOOL` = 8+32+8 = 6
  bytes; `DINT, BOOL, BOOL` = 32+8 = 5 bytes — i.e. no 4-byte alignment
  padding at all, and a run of consecutive BOOLs shares one backing byte
  but a non-BOOL member breaks the run, forcing the next BOOL(s) onto a
  fresh backing byte. Verified this is exactly what `compute_udt_size`
  already produces, unchanged (`tests/test_sizing.py::
  test_bool_packing_run_broken_by_non_bool_member`) — the code was already
  correct because it trusts Logix Designer's own hidden-SINT-per-run XML
  shape rather than re-deriving the rule, and that shape already encodes
  this behavior. Confidence raised from "pure guess" to "confident field
  opinion, matches implementation exactly" but this is still not the same
  evidentiary bar as a real controller memory measurement — stays ASSUMED,
  not KNOWN, until Phase 3 actually confirms it.
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
- Array of UDT: `dimension × udt_size`, formula pending OQ-ARRAYPACK (per-element
  vs whole-block padding).
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

Confidence: inherits `udt.alignment_confidence` (currently UNKNOWN) via the
same `compute_udt_size` path, since an AOI instance structure is internally
UDT-shaped. One AOI-specific sub-question doesn't reduce to OQ-ALIGN/
OQ-BOOLPACK though — see OQ-AOIBOOLPACK: unlike UDT members, AOI
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

## Module / I/O tag sizing

- Local (backplane) I/O: **UNKNOWN**, not yet modeled. Depends on module type
  (input/output point count, analog vs digital) — needs its own type table,
  likely sourced from module EDS/catalog data rather than computed generically.
- Produced/Consumed: **UNKNOWN — OQ-PRODCONS**. Overhead formula not yet
  isolated from base connection cost vs. payload cost vs. consumer count.

## Logic instruction weights (FITTED — empty until Phase 4)

Table to be populated during Phase 4/4b. Format once populated:

| Instruction | Base bytes | Per-operand bytes | Sample size (n) | Residual error |
|---|---|---|---|---|
| _(none yet)_ | | | | |

Do not estimate these ahead of data. No placeholder numbers — an empty table is
more honest than a guessed one that gets silently treated as real later.

## Change log

Log every constant change here with date + which sample(s) drove the change, so
there's a record of *why* a number is what it is, not just what it currently is.

- (none yet — populate starting Phase 3)
