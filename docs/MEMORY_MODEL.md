# Memory Model

The single source of truth for every sizing constant, formula and packing rule.
Parser and calculator code reads these values from
`src/l5x_memory_analyzer/sizing/memory_model.yaml`, which mirrors this file.
Nothing is hardcoded inline.

## How to read this file

Every entry carries a confidence tier:

| tier | meaning |
|---|---|
| **KNOWN** | Measured in isolation, at several counts, with zero residual — or documented Rockwell behaviour. Do not re-derive. |
| **FITTED** | Regressed against capture data. Carries residual error, stated where known. |
| **ASSUMED** | Standard Logix behaviour taken on reasonable grounds, not confirmed by this project's own captures. |
| **UNKNOWN** | Deliberately unpriced. The engine raises rather than guessing. |

Two rules govern the tiers:

- **A constant measured alone, at several counts, with zero residual is KNOWN
  even if the block around it is FITTED.** A block's `confidence` key describes
  how most of it was derived; it under-states the constants inside that were
  measured cleanly. Those carry their own `*_confidence: KNOWN` key in the YAML,
  and `tests/test_measured_known_constants.py` pins each one to both its value
  and its tier. Changing either without new evidence fails the suite. The full
  register is at the end of this file.
- **A ±8-byte residual is the project noise floor.** Almost every formula here
  lands inside it. Treat a residual under 8 bytes as agreement, not as a term to
  chase.

All values are bytes.

---

## Atomic data types — KNOWN

| Type | Bytes | Notes |
|---|---:|---|
| BOOL, standalone tag | 4 | ASSUMED: allocated as a DINT, not bit-packed |
| BOOL, UDT member | ⅛ | Packs 8 per hidden backing SINT — see UDT packing |
| SINT / USINT | 1 | |
| INT / UINT | 2 | |
| DINT / UDINT | 4 | |
| LINT / ULINT | 8 | |
| REAL | 4 | |

Unsigned types are identical in width to their signed counterparts; the sign bit
is an interpretation only. They are real, in-use native types — the production
corpus declares 25 UINT, 20 USINT, 16 UDINT and 9 ULINT members — not an edge
case to leave unmodelled.

`parser/modules.py` derives its own type table from this model rather than
carrying a copy, so a type the model knows is understood there automatically.
BOOL is deliberately absent from `atomic_types` because its cost is
context-dependent; inside a module structure it takes the standalone 4 bytes.

### Standalone atomic tag data slot — KNOWN

**A standalone (non-array, non-structure) atomic tag's data occupies a fixed
4-byte slot regardless of declared type.** SINT and INT are padded up to it;
LINT is reported in it rather than the 8 its value needs.

| type | charged before | real | per tag |
|---|---:|---:|---:|
| SINT | 1 | 4 | +3 |
| INT | 2 | 4 | +2 |
| LINT | 8 | 4 | −4 |
| BOOL / DINT / REAL | 4 | 4 | 0 |

Measured on six bare 50-tag files, one type each, no logic — zero residual on
all six.

**Arrays and structure members are deliberately untouched.** An array keeps
`element_size × count`; a structure member keeps its packed size. This is a
per-TAG slot rule only. A test asserts `SINT[100]` stays exactly 300 bytes
smaller than `DINT[100]`.

---

## Strings

| | Bytes |
|---|---|
| Built-in STRING, per instance | 4 (LEN, DINT) + 82 (DATA, SINT[82]) = **86** |
| Custom string type, per instance | 4 + `nearest8(maxlen)` |

**DATA padding — KNOWN.** DATA rounds to the **nearest multiple of 8, rounding
DOWN at the exact tie**: pad to 4 first, then if that lands on the 8-byte
midpoint, drop back by 4. Verified exact against nine maxlen points spanning
every mod-4 and mod-8 remainder. `maxlen` 50 and 51 measure byte-identical (both
land on 48); 100 is a tie and drops to 96; 101 is already 0-mod-8 and stays at
104. This one rule fully explains the real per-tag rate — no separate correction
constant is needed. Wired as `string.custom_data_padding_multiple = 4`, with the
two-step rounding in `udt.py`.

**Built-in STRING tag overhead correction — KNOWN.** A built-in STRING tag costs
**2 bytes less** than the ordinary per-tag overhead formula predicts. Exact
across a 9-point count sweep (1 to 1000) plus a 4-point name-length cross-check:
the gap is always `−2 × count`, independent of both count and name length. Wired
as `string.builtin_tag_overhead_correction = −2`, applied only when the tag's
declared type is literally `STRING`.

**Custom string type-definition cost — KNOWN.** One-time per declared type,
separate from per-instance size:

    custom_definition_cost(name_len) = 208 + 8 × floor((name_len − 5) / 8)
                                     + 8 if maxlen ≡ 1 (mod 4)

A clean step function, exact against 22 of 22 dense name-length points (lengths
1–16 plus 20/24/28/32/36/40, maxlen held at 100), with a 3-point UDT-member
cross-check confirming no separate nesting tax. The mod-4 bonus is exact at 3 of
3 points (maxlen 49, 101, 501). Neither term otherwise depends on DATA length.

Custom string types are excluded from the ordinary UDT definition cost — that
formula was fitted against true UDTs and does not apply. A built-in STRING as a
UDT member needs no correction at all.

---

## Tags

### Per-tag flat overhead — KNOWN

Every top-level `<Tag>` in `Controller/Tags` or `Program/Tags` costs a flat
overhead **additive with** its own data size:

    tag_overhead(name_len) = 84 + 8 × floor(name_len / 8)

Tag names are stored in 8-character-aligned chunks. Exact across 16 independent
points (a 13-point DINT sweep plus a 3-point REAL cross-check at a different
type and count), plus a separate 8-point count sweep from 5 to 1000 tags landing
on exactly the same constant. Two independently derived measurements agreeing
exactly is why this is KNOWN rather than FITTED.

Type barely affects it — SINT 95, INT 94, DINT 92, LINT 88, REAL 92, BOOL 92 at
`name_len = 8` — and it is treated as type-independent.

### Alias tags — KNOWN

An alias tag carries no `DataType` of its own, only an `AliasFor`, and has no
data space. **It still occupies a real tag-table entry with a real cost:**

    alias_overhead(name_len) = 56 + 8 × floor(name_len / 8)

The same 8-character bucket shape as an ordinary tag, with its own flat base (56
rather than 84) and no data term added. Exact across all three name-length
buckets tested (gaps of 56, 560 and 63,200 at n = 1, 10 and 1000).

This matters at scale: roughly **21% of a typical real program's tags are
aliases**. Not an edge case.

> An earlier claim that aliases cost zero was wrong. It correctly observed that
> an alias has no raw data size and incorrectly concluded that meant no cost.

---

## UDTs

### Definition cost — KNOWN

A **one-time** cost per distinct UDT type declared in the file — not per
instance, and charged whether or not any tag uses it:

    udt_definition = 160
                   + 16 × declared_member_count
                   + 8 × ceil(name_len / 8)
                   + 32 × bool_run_count
                   + member_name_pool

`declared_member_count` counts members the way a user would: a run of N BOOL
members is N members. It excludes the hidden backing SINT but not the visible
BIT-alias members that SINT backs.

`bool_run_count` is the number of **separate** BOOL runs, each with its own
hidden backing SINT. A `BOOL, DINT, BOOL` shape has 2, not 1 — the DINT breaks
the run.

Exact for `declared_member_count ≥ 4`. At 1 and 2 members there is a small-N
anomaly of a further 8–16 bytes, shared with the tag-count sweeps, not
understood, and irrelevant at real-program scale.

> The base of 160 was originally implemented as two separate additive terms,
> `168 + 16 × members` and `224 + 8 × ceil(name_len/8)`, because each fitted its
> own 1-D sweep exactly. They are two slices through the same 2-variable surface
> and both included the shared base, so adding them double-counted it —
> predicting 416 where the real value was 192. Solving the slices as simultaneous
> equations gives the one true base. **This is the canonical example of the
> failure mode in this project: two terms that each fit perfectly in isolation
> and are wrong together.**

### Member names — wired, REOPENED (OQ-UDTMEMBERNAME)

**Re-priced live on 2026-10-19 the law does not fit its own sweeps.** The four-BOOL
length sweep reads a flat −8 at every length, but the four-DINT one reads −16, −8, −16,
−16 at lengths 2, 7, 16 and 32 (not flat), the nested-UDT pair −32 / −32, the BOOL
member-count arm +8, 0, −8, −24, −48 at 1, 2, 4, 8, 16 BOOLs, and the two safety-round
UDTs (members `D, R, B1, B2` and `D0`..`D9`) read 16 and 32 below the engine on a
safety controller and on its 1756-L81E twin alike: their pool reads 0. One candidate,
`8 × ceil(Σ max(0, len − 2) / 8)` (names of up to 2 characters free), fits the DINT arm
and both safety UDTs exactly and misses the BOOL arm by 8. Not wired: the seventeen
real programs are the test of any change here, and the BOOL / DINT disagreement says
the form is not yet known. **Test: batch C `udtpool_*`** (16 one-definition files at name
lengths 1 to 12, TASKS 0zg). As wired:

**A UDT definition's declared members' own names cost an 8-aligned pool**, the
same law an AOI definition's members follow:

    member_name_pool = 8 × ceil(Σ(len(name) + 1) / 8)

Measured on four BOOL members with name length as the only variable:

| name length | 2 | 4 | 7 | 8 | 12 | 16 | 24 | 32 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| residual before | −8 | 0 | +8 | +16 | +32 | +48 | +80 | +112 |

A raw one-byte-per-character rate fits five of those seven points and misses
4→7 (wants +12) and 7→8 (wants +4). **That pair is the entire discrimination
between the two forms.** Any sweep whose name lengths share a residue mod 8
cannot tell them apart.

Cross-checks: flat in tag count at each length, so the cost is per definition and
not per instance; agrees at 4 and 8 members; agrees across DINT and nested-UDT
members.

Hidden backing SINTs are excluded, matching `declared_member_count`.

This was the largest single real-file gain in the project's history — real UDT
member names average about 12 characters and a real program carries on the order
of 174 UDT definitions.

### Packing — KNOWN

- Recurse members in declared order.
- BOOL members pack 8 to a hidden backing SINT, incrementing BitNumber 0–7, then
  a fresh SINT for bits 8–15, and so on.
- **No alignment padding between members at all.** `BOOL, DINT, BOOL` = 1+4+1 =
  6 bytes. `DINT, BOOL, BOOL` = 4+1 = 5 bytes.
- **A non-BOOL member breaks a BOOL run**, forcing the next BOOL onto a fresh
  backing byte.
- A nested UDT member's size is that UDT's own total, computed recursively, with
  self-reference cycle detection. Only BOOLs pack, so a nested UDT always starts
  fresh rather than filling a partial leftover byte. This holds by construction —
  no code path merges a nested UDT into a preceding member's partial byte.

### Standalone UDT tag data slot — FITTED

**A standalone (non-array) UDT-typed tag's data slot is padded up to 8 bytes**,
alongside `definition_scale_correction.udt_tag_extra = −4`.

Derived from the one place two captured families disagreed about what a single
UDT tag costs — and they disagreed only because they sit on opposite sides of the
boundary:

| UDT size | tags | per-tag error before |
|---:|---:|---|
| 9 bytes | 1 to 500 | exact |
| 40 bytes | 40 and 400 | −7.000, slope exact over 360 tags |

Padding the slot to 8 leaves 40 at 40 and lifts 9 to 16; with the extra at −4
both families come out at zero residual. **Neither constant is separable from
either family alone.**

> FITTED and thin: two UDT sizes, one on each side of one boundary, fitting two
> constants. A 52-file closeout covering every residue mod 8 at two tag counts is
> generated and awaiting capture.

**Arrays are deliberately untouched.** UDT array families read +1 at every length
against a 12-byte 4-aligned element, so the padding is on the tag's slot, not on
each element. Padding elements instead improves the real files more and destroys
the `tags` category — that gain is absorbing some other missing term.

### Array sizing

| shape | rule | tier |
|---|---|---|
| Array of atomic | `dimension × element_size` | KNOWN |
| Array of BOOL | `ceil(dimension / 32) × 4` — 32 bits per DINT word | ASSUMED |
| Array of UDT | `dimension × ceil(udt_size / 4) × 4` | KNOWN |
| Multi-dimensional | product of all dimensions × element size | ASSUMED above 2-D |

BOOL *arrays* bit-pack into DINT-sized words; standalone BOOL *tags* do not. Do
not conflate the two.

Array-of-UDT rounding is confirmed at n = 1/10/100/1000/5000 for a 3-byte-tight
UDT (rounds to 4 bytes per element, exact for n ≥ 10, same small-N anomaly at
n = 1) and for an already-8-byte UDT (rounding is a no-op). Atomic-type arrays
are **not** subject to this rounding.

---

## Add-On Instructions

### Instance tags — KNOWN

Every AOI-typed tag in a real export is a plain named `Tag` with
`DataType=<AOIName>`, sized identically to a UDT-typed tag. This is the
overwhelming majority of real usage and needs no logic parsing.

Recursion matches a UDT: `Input` and `Output` parameters plus `LocalTags` are
storage members. **`InOut` parameters are excluded entirely** — they are a
reference to a caller-scope tag, not a new allocation. That also answers whether
a parameter duplicates the referenced tag's memory: it does not, because it is
never sized.

An AOI definition can nest another AOI as a LocalTag's type, recursed the same
way as a nested UDT.

> **Open: AOI BOOL packing.** Unlike UDT members, AOI parameters and LocalTags of
> type BOOL appear in the L5X as plain `DataType="BOOL"` with no hidden-SINT or
> BIT-alias representation. Whether they pack 8 per byte like a UDT member or
> allocate unpacked like a standalone tag is unconfirmed. Implemented as unpacked
> (4 bytes), which is what the XML shape shows, but this is an open question and
> not a KNOWN fact.


**A scalar instance packs its BOOLs (OQ-AOIBOOLINST, 2026-10-21) — KNOWN.** A scalar AOI
instance holds its BOOL parameters and locals packed into 32-bit words beside EnableIn /
EnableOut, exactly as an array element does (Array of instances, below), and its slot
rounds up to 8: `8 × ceil((packed element + tag overhead − 4) / 8)` (`aoi_scalar_instance`).
One AOI with 4 to 65 BOOL bits — one, two, three words — at 1, 25 and 50 instances, locals
or Input parameters: 96 a copy for one word, 104 for two and three, every file exact; the
engine had charged each BOOL 4 bytes (104 / 216 / 220 / 324 / 344 / 348). Re-priced over
the 735 rebuilt AOI-family captures, 75 move: 70 closer, the rest within 4 bytes; it
closes `mbshape_*` (+1,000..+2,300 → within ±40), `aoiint_*` (+12,198 → +4 against the
plant) and `aoilit_*`. Without BOOLs beyond EnableIn / EnableOut it is the old law rounded
up to 8. The real safety programs move −0.01% to −0.80%; the seventeen standard programs,
not in this checkout, by an estimated −100 KB in all, toward under-prediction.

### Definition cost — FITTED

An AOI's own parameter and LocalTag declaration has a real one-time cost,
independent of any instance — the same relationship a UDT definition has to a
UDT-typed tag. **One itemised form:**

| term | value |
|---|---|
| base | 1163 |
| per declared member | 12 |
| per declared member | that member's own data bytes |
| per 32-bit word the declared BOOLs occupy | 24 |
| the members' names | pooled, one byte per name, rounded up to 8 |
| the AOI's own type name | `name_length_bytes`, below |

A scalar BOOL has no data bytes of its own — it is a bit in the packed words, and
`EnableIn`/`EnableOut` are two further bits in those same words, so an AOI with
no declared BOOL still pays for one word. An array member's data bytes are
element × dimension; a TIMER, STRING or UDT member's are that structure's own
size. `InOut` parameters cost nothing. `EnableIn`/`EnableOut` are not declared
members.

Measured on **125 captured definition-only files** — an AOI definition with no
instance tag anywhere and no internal rungs, so the definition is the only AOI
cost in the file and its value reads straight off the capture. They span 1 to 128
declared members, six atomic types, BOOL fractions from 0 to 100%, and Input,
Output and LocalTag usages.

**The whole definition occupies whole 8-byte units** — `total_alignment_bytes: 8`,
around the project-wide 1-byte offset (`total_alignment_offset: 1`). Re-run against
the live engine, the instrument had drifted: every file the unaligned sum put at 4
mod 8 read exactly 4 bytes high, every file at 0 mod 8 read as predicted. Aligned:

| | unaligned | aligned |
|---|---:|---:|
| instrument files exactly 0 | 8 | **68** |
| inside ±8 | 94 / 125 | **117 / 125** |
| mean \|residual\| | 6.99 B | **4.48 B** |
| every clean AOI-bearing capture exactly 0 | 38 | **201** |

The same padding rule, found independently on the instance side, is
OQ-AOIBOOLPACK-PAIRING. **AOI definition cost is KNOWN**, as is the type-name term
(seven lengths, 7/7 exact). What remains — 47 files at +8, no clean discriminator —
is exactly the ±8 single-measurement noise floor and is closed as BOUNDED
(OQ-AOIDEFSHAPE). The per-definition cost also holds at real population shape:
1,231 bytes per definition measured against 1,233 predicted over 5 → 40 definitions
(OQ-AOIREALSHAPE).

> On the real programs the alignment is neutral — tens of bytes a program, mean
> error 1.6634% → 1.6637% on the twelve present. It is wired because it is right on
> every isolation file, not because it moves the headline.

### An AOI's internal ladder is routine logic, not definition cost

An AOI's internal RLL is priced with the ordinary per-instruction model plus the
AOI-internal terms, and is emitted as its **own `routine_logic` entry** at
`aoi_definitions/<AOI>/<routines>`, tier ESTIMATED. It used to be added into the
definition entry, which is tier EXACT, with three consequences: compiled ladder was
displayed **without the estimated flag**; the tree drew it as an unexplained
"Unitemized definition cost" worth roughly 6% of a real file; and it could not carry
its rungs' measured confidence. Totals are unchanged — verified byte-identical on
every real program present.

**This one form replaced four separate fitted terms that had each absorbed part
of the same error.** Every one fitted its own sweep exactly and was still the
wrong shape, which is why what each was really measuring is recorded:

| superseded term | what it actually was |
|---|---|
| `per_declared_item: 20` | 12 plus the 4 data bytes of the DINT every count sweep used |
| `per_type_rate` BOOL 16 / SINT 18 / INT 18 / LINT 24 | the same 12-plus-own-size relation, seen through the old linear name term |
| `member_name_char_bytes: 1` with 3 free chars | a pool rounded up to 8, misread as a per-character rate |
| `aoi_member_type_extra` REAL 0 / TIMER 8 / COUNTER 8 | exactly (own size − 4); its floor-to-8 was an artifact of the mis-attribution |

A mixed-versus-single-type split went with them. Per-type rates appeared not to
compose additively once BOOL sat beside another type because the name-pool error
was surfacing as a composition effect — not because of any real interaction.

**Type-name length — KNOWN:**

    name_length_bytes(len) = 8 × max(0, (len − 8) // 4) − 8

Exact at 7 of 7 points (lengths 8, 9, 13, 16, 20, 25, 30).

> The first divisor tried, `(len − 7) // 4`, reproduced all seven points and put
> length 19 one bucket too high. It was caught by cross-checking two
> AOI-array-packing files that differed only in AOI type-name length. **Seven
> points agreeing does not pin a bucket boundary.**

Required / Visible / Hidden flag configuration has no effect on cost. An apparent
±16 swing was confirmed to be noise.

### Internal logic — FITTED

An AOI's own internal routines are separate from its declaration cost and were
priced at zero until measured. `parse_aoi_internal_logic()` aggregates **all** of
an AOI's internal routines into one pseudo-routine — real data confirms
per-routine count does not matter, only total content — weighted with the same
per-instruction table as ordinary routine logic, with `charge_shell=False`
because the definition's own base already covers the shell.

Cut maximum residual on the isolation sweep from 12.02% to 0.55%. A further
composite-scale surcharge applies on top, `aoi_logic_composite_surcharge_per_instr
= 20`.

On top of the per-instruction weights (OQ-AOICOMPLEX / OQ-AOIROUTINES, 2026-10-04,
`aoicx_*`, `aoiint_*`, `aoistr_routines_*`):

| term | bytes | constant |
|---|---:|---|
| a non-BOOL destination written inside the AOI | +4 per instruction | `aoi_internal_per_word_destination` (KNOWN) |
| an instruction that reads an InOut parameter, or a bit op on one | +8 per instruction | `aoi_internal_inout_operand_bytes` (FITTED) |
| a word written INTO an InOut | +0 beyond the 4 above | — |
| GSV / SSV naming an InOut axis as the instance | +0 | — |
| each RLL scan-mode routine beyond Logic (EnableInFalse, Prescan, Postscan) | +268 per routine | `aoi_extra_routine_bytes` (FITTED) |
| the AOI's own logic calls another AOI | +264 once per calling definition | `st_aoi_call_routine_bytes` |

"Per-routine count does not matter" is superseded: it was read off two rows that
captured with build errors. The InOut term is per instruction, not per operand:
`GRT(IoU.D,IoU.R)` pays 8 once.

### Call site — FITTED

**One AOI call site costs `120 + 16 per parameter passed`**, the instance tag not
counting as a parameter.

| call shape | params | per call |
|---|---:|---:|
| `Aoi_D000(Inst000,0,0,OutBitTag);` | 3 | 168 |
| `AddAoiProbe(AoiInst0000,0,Bit1);` | 2 | 152 |

One parameter, 16 bytes, both exact, from two independently written generators
with different AOI shapes.

**What is passed matters.** Both shapes above pass the literal `0` to their Input
parameters and a tag to a BOOL Output. `litop_bool_*_n01000_r2` call one 3-input AOI
1,000 times, varying only the arguments:

| arguments | per call over the old model |
|---|---:|
| tag, tag, tag | +36 |
| tag, `0` or `1`, tag | +24 |
| tag, tag, `12345` | +36 |

An **Input argument that is anything but the literal 0 or 1 costs 28**, not 16, on BOOL
and DINT parameters alike; `input_ref_extra_bytes = 12` is charged per such argument.
Output arguments stay at 16 (measured), InOut at 16 (not isolated). Real programs pass
a tag to about 90% of their AOI Input arguments. ST call sites are unchanged — only RLL
was measured.

**Into a REAL Input parameter** (OQ-AOILITARG, `aoilit_*`), over a REAL tag there: an
integer literal **+52** — the literal 0 or 1 included, which is not the cheap case on a
REAL parameter, so it also pays back the 12 — a DINT tag **+52**, a float literal **+4**
(`aoi_call_site.real_input`). INT and SINT parameters move too (integer literal −60 vs an
INT tag, +52 vs a SINT tag) and are not wired: about fifty real arguments.

**A file that calls an AOI from ladder carries a one-time 264** beyond its call sites —
`dscale2_aoi_*`, `defscale_aoiinst` and `litop_bool_*` all read exactly +264 (+252)
with every call site priced. It is the ladder twin of `st_aoi_call_routine_bytes`
(264, per ST routine). Every such file has one calling routine, so it is charged once
per file, which is what the data proves; the per-routine reading is worth 0.24% of the
real programs, under the noise floor. The second is a −16.000-per-unit slope over 180 units,
and a separate no-call arm proved the instance tag is exact at 1, 5, 20 and 60
tags — so the whole 16 sits on the call, not on the instance.

Real programs carry thousands of call sites at a mean of about 4 parameters each,
so the flat rate this replaced was under-charging parameter-heavy AOIs and
over-charging small ones.

### Array of instances — FITTED

**The whole instance-array block is padded up to an 8-byte boundary:**

    array_bytes = 8 × ceil(n × per_instance / 8)

wired as `aoi_array.block_alignment_bytes`. The extra 4 bytes appear exactly when
`per_instance ≡ 4 (mod 8)` and never otherwise. **48 of 48 captured sweep
families agree with zero exceptions**, over per-instance sizes of 4, 8, 12, 20,
24, 32, 40, 44, 48, 64, 76, 84, 104, 120, 124, 220 and 244 bytes.

It is **not** per-instance padding: that would make the residual grow with
instance count, and the real data is flat in n. Same mechanism and same 8-byte
constant as the predefined array structures' element-block padding, which is the
independent cross-check.

> An earlier reading held that BOOL and atomic composition switched the term on
> and off. That was wrong — composition only moved the per-instance size, and the
> residue mod 8 was doing all the work.

> Stays FITTED: three families still vary with instance count and their closeout
> files are generated, not captured.

### Array-dimensioned declared members — WIRED

An AOI's array-dimensioned declared member costs its own data space. The array's
data bytes **replace** the scalar element size a non-array member of the same
type would pay rather than stacking on top of it.

Computed through `compute_array_size`, not `element_size × dimension`, because
the predefined array structures have their own `base + per_element` shape and no
scalar element size at all. Real programs declare CAM_PROFILE array LocalTags,
and going through `compute_element_size` raised `UnknownDataTypeError` on the
first real file it met.

> **BOOL arrays are deliberately NOT priced by this term and stay unpriced.**
> `BOOL[50]` measured −13, which is neither the 7-byte packed size nor an 8-byte
> two-word rounding. `INT[50]` measured −99 against the 100 its element size
> predicts. Two further residuals are recorded rather than fitted: an 8-byte
> discount per array member *after the first*, and `dimension = 25` landing
> exactly one element off the line through 10 and 50.

---

## Predefined structure types — KNOWN

Firmware-native structures referenced by name but never given a member list in
`Controller/DataTypes` — Logix resolves them internally, so there is nothing to
recurse. All 195 known predefined types are wired with a real measured value.

| Type | Bytes | Notes |
|---|---:|---|
| TIMER | 12 | status DINT (EN/TT/DN) + PRE + ACC. Cross-checked against Rockwell primary documentation. |
| COUNTER | 12 | status DINT (CU/CD/DN/OV/UN) + PRE + ACC. Same. |
| CONTROL | 12 | status DINT (EN/EU/DN/EM/ER/UL/IN/FD) + LEN + POS. Same. |
| MOTION_INSTRUCTION | 12 | Same 3-DINT layout; exact across a 1/5/50 count sweep. |
| MOTION_GROUP | 1,076 | FITTED — pure empirical constant. |
| AXIS_CIP_DRIVE | 22,636 | FITTED. |
| AXIS_SERVO | 16,796 | FITTED. |
| AXIS_VIRTUAL | 16,796 | FITTED. Identical to AXIS_SERVO — confirmed independently, not assumed. |
| COORDINATE_SYSTEM | 9,516 | FITTED. |
| MESSAGE | 688 | |
| ALARM_DIGITAL | 973 | |
| CONNECTION_STATUS | 4 | |
| DCI_STOP | 76 | Safety family — value is real and wired; inclusion policy is a separate open question. |
| CONFIGURABLE_ROUT | 52 | Safety family, same. |

The axis and motion-group values are empirical because Rockwell does not publish
the layout.

> **A second set of axis totals exists and is deliberately not wired.** One later
> reading records AXIS_CIP_DRIVE 22,728, COORDINATE_SYSTEM 9,616 and
> AXIS_SERVO = AXIS_VIRTUAL 16,888 — each roughly 92–100 bytes higher — measured
> against a motion-group-only baseline of 19,296 that does not itself reconcile
> against the wired project baseline plus MOTION_GROUP. The file composition
> behind that second set is not available, so it is recorded here rather than
> silently trusted or silently dropped. **The table above is what runs.**

### SFC and function-block families — ASSUMED

Read off real decorated-XML data with zero variance across the instances found,
but not capture-confirmed. These are the backing TAGS, priced as data. The chart and
diagram LOGIC is priced at zero: FBD under the noise floor (two routines in the real
programs), SFC out of scope permanently (owner's decision, 2026-10-23).

| Type | Bytes | Instances seen |
|---|---:|---:|
| SFC_STEP | 28 | 272 |
| SFC_ACTION | 16 | 97 |
| SFC_STOP | 20 | 4 |
| FBD_TIMER | 48 | 5 |
| FBD_ONESHOT | 12 | 4 |
| FBD_MATH | 16 | 2 |
| FBD_BOOLEAN_AND / _OR / _NOT | 12 | bit-packed 3-DINT shape, decoded exactly against real values |
| RATE_LIMITER | 92 | 1 |
| SCALE | 52 | 1 |

RATE_LIMITER and SCALE rest on a single instance each — the weakest rows in the
table.

None of these are drillable to a per-field breakdown, unlike TIMER/COUNTER/
CONTROL's 3-way split. Only the total is confirmed, field counts vary from 4 to
23, and a fabricated even split would misrepresent that. See
`sizing/tree.py`'s `_THREE_FIELD_PREDEFINED`.

### Predefined array structures — FITTED

Structures always used dimensioned in real Logix, never scalar, whose cost is
`base + per_element × N` rather than a flat scalar size. A scalar tag of one of
these types correctly raises `UnknownDataTypeError` rather than returning a wrong
number, since that shape does not realistically occur.

| Type | base | per_element |
|---|---:|---:|
| CAM_PROFILE | 4 | 56 |

Exact linear fit across a 1/5/20/50-element sweep. `per_element = 56` is 14
fields × 4 bytes, confirming that CAM_PROFILE has 14 real per-element fields of
which only one is visible in the decorated XML shape.

---

## Project baseline

**A File|New 1756-L81E at firmware 35 reads 18,112 bytes, and the engine predicts
18,112 exactly.** Confirmed twice over: read directly off a fresh Studio project,
and back-solved from captures — an empty-rung sweep gives 16 bytes per empty rung,
so 10-rung 18,272 minus 160 puts the zero-rung base at 18,112.

That total decomposes as:

| component | bytes |
|---|---:|
| `empty_project_baseline` — controller-only scaffolding | 13,296 |
| the MainTask / MainProgram / MainRoutine File|New also creates | 4,816 |
| **total** | **18,112** |

**Quote a whole-file prediction against a whole-file capture, never a component
constant against a total.** Comparing the 13,296 component against a whole-file
reading once manufactured an apparent 7,800-byte hole in the model that did not
exist. The engine's own batch-prediction output is the only figure comparable to
a controller Capacity reading.

`empty_project_baseline` is a fixed, zero-variance cost confirmed across 200+
independent data points spanning wildly different test categories, all landing on
the same number once every other sizeable element is accounted for. It is emitted
once per report as a `project_baseline` entry.

Those points are independent in test **content**, not in processor or firmware —
13,296 is confirmed for **1756-L81E at firmware 35.05 specifically**, which is
what virtually every generated sample uses. The baseline changes with processor
and firmware, and two additive corrections handle that.

### Firmware baseline delta — FITTED

Applied per processor family, keyed on the root element's `SoftwareRevision`
major version. **One ladder cannot serve every processor**: each processor's
residual is constant within a firmware band and the bands differ by family. On a
bare-baseline file — one processor, one firmware, no content — the residual *is*
the baseline error by definition, so this reads a lookup table off its own
measurement rather than fitting free parameters. Every value is a multiple of 8,
with 4 to 9 identical captures behind each cell.

| family | v31–33 | v34–35 | v38 |
|---|---:|---:|---:|
| 5069 L306 / L310 / L320 | +48 | +32 | +32 |
| 5069 L330 / L340 | +8 | −8 | +8 |
| 5069 L3100 | +8 | −8 | +32 |

**Pattern order is load-bearing.** `5069-L3100ERM` also starts with
`5069-L310`, so the L3100 row must precede the L306/L310/L320 row or it is
silently swallowed. A test asserts that ordering.

Generic (non-family) deltas also apply: v31/v32 add +11,240 and v33 adds +14,248
relative to the v34/v35 base; unlisted majors add nothing.

**There are deliberately no 1756-L8x rows, and this is the important part.** The
L8x rows do sit at +16 on v34/v35, and correcting that here as a baseline error
is **wrong**. Every generated test file is a 1756-L81E at v35, so a −16 baseline
correction moved 787 previously-exact captures to −16 and dropped the corpus
exact-prediction rate from 32.9% to 6.6%. The L8x +16 is a firmware-dependent
**content** gap — the real MainRoutine content drops to zero bytes on v34+
hardware while the engine still predicts 16 — and it belongs to whatever
eventually prices that content.

> That near-miss was caught only by re-running the residual census immediately
> after wiring. **Re-run the census after any baseline change.**

### Safety-capable baseline delta — FITTED

**+296** when `ProcessorType` ends in `S2` or `S3` (the 5069 Motion+Safety
catalog suffix) **and the file carries no safety task**. It is the safety
task/program shell (the same 296 the engine charges per safety task): the
firmware-matrix 5069 safety files carried no safety task, and Studio creates one on
import. A file with its own safety task pays the shell once, through
`safety_task_program_shell`; until 2026-10-19 the 5069 also paid this delta on top,
296 too high (round 4's 5069 bases; OQ-SAFETYPARTITION).

### What is genuinely unconfirmed

- **v36 and v37** — no real sample at all.
- **v38** — its only capture is flagged as an unreliable reading.
- **The 1769 series** — real range 69,600 to 98,944, not modelled at all.
- **Dual-IP / DLR controller configuration costs +40 bytes.** One reading, one
  controller, not wired.

---

## Safety memory is a separate partition — KNOWN (OQ-SAFETYPARTITION)

Accuracy is measured on standard processors only; safety-processor rows are excluded
from every accuracy figure (`quick_eval.py`). A safety controller keeps safety tags and
safety logic in its own partition, read on the Capacity tab as **safety used memory**
beside the standard figure. Measured on 299 `safe_*` files in four rounds (1756-L81ES
v35, and round 4's bases on 5069-L330ERMS2 / L320ERMS2 v35 and 1756-L81ES v32 / v34;
2026-10-18 and -19; zero build errors, both readings on every row), each sweep
differenced against its own control. **The engine reproduces the safety reading of all
299 to the byte**; the standard reading's residuals are below.

**A safety tag is a name entry plus a data block.**

    name_entry(len)   = 56 + 8 × floor(len / 8)                         (= alias_overhead)
    block(data)       = 8 × ceil((24 + data) / 8)        scalar, structure, UDT, AOI instance
    block(data)       = 8 × ceil((32 + data) / 8)        array (8 more header)

`data` is the ordinary data size (`compute_array_size`; an AOI instance's less the 8 of
`aoi_instance_extra`). Which partition pays each part depends only on scope:

| tag | standard | safety |
|---|---|---|
| controller scope, `Class="Safety"` | name entry | block |
| any tag of a `Class="Safety"` program | 0 | name entry + block |
| alias of a safety tag, controller scope | name entry | 0 |
| alias inside a safety program | 0 | name entry |

Exact on BOOL/SINT/INT/DINT/REAL/LINT, TIMER/COUNTER/CONTROL, two UDTs, all 39
safety-instruction structures and ten array shapes (`DINT[2]` … `DINT[4,4]`,
`TIMER[4]`, `BOOL[96]`), at both scopes, names of 4 to 40 characters. A UDT's
**definition** costs standard memory only.

**Shells.** The base, 1,394, is File > New's SafetyTask/SafetyProgram/MainRoutine with
no rungs: the same at v34 and v35, and on 5069-L330ERMS2 and L320ERMS2 v35 and 1756-L81ES
v32 (1,410 with the NOP rung on every platform, and one content step of 50 safety DINTs
and 10 RIN rungs +6,544 safety and +3,200 standard on every one). Each further safety
routine costs **264 + 8 × floor(len / 8)** of its name (names of 8 to 15 characters 272,
16 to 23 280, 24 to 31 288, 40 296; 6 and 7 characters 264), called or not. Each further
safety program costs **404** in safety, plus its routines, and **64 + the program-name
law** in standard memory; its name costs nothing in safety. The standard side's 296
safety task/program shell is charged once per safety task in the file. A safety
controller whose file carries no safety task pays the same 296 as
`safety_capable_baseline_delta` (Studio creates the shell on import; the firmware-matrix
5069 S2/S3 files), and a file with its own safety task does not pay it again: the 5069
bases read 296 below the engine until that double charge was removed.

**Safety-routine logic costs nothing in standard memory.** In the safety partition:

- a **safety instruction** costs its measured per-rung figure (table below), wherever its
  operands and backing tag live (ESTOP and RIN measured with inputs on program BOOLs,
  controller BOOLs, array elements and members, backing tags at both scopes: all 360);
- **any other instruction** costs its **standard engine cost** (weights, operand-type,
  literal, mixed-type and index laws, branches, the series-output law, all as standard)
  **plus 8 per bit-instruction operand** (XIC, XIO, OTE, OTL, OTU), **4 per other tag
  operand**, and **8 per tag used as a subscript**; literals, keywords, labels and
  routine names add nothing. Exact on 64 of the 67 round-3 logic files (every compare,
  math, move, timer, counter, one-shot, MCR, JMP/LBL, literal, mixed-type, indexed,
  member, scalar, controller-scope, series, branch, two-output and seal-in shape, at 20
  and 100 rungs). ATAN2 (no standard weight), COP and FLL carry a measured correction
  (+64, +4, −4), exact at 20 and 100 rungs;
- a **JSR** costs 72, its standard weight; the subroutine its shell.

| safety instruction | bytes / rung | | safety instruction | bytes / rung |
|---|---:|---|---|---:|
| ESTOP, RIN, ROUT | 360 | | LC | 436 |
| DIN, ENPEN | 360 | | FPMS | 432 |
| SMAT, DCM | 380 | | CSM | 432 |
| DCSRT | 436 | | DCA | 448 |
| DCAF | 456 | | DCS | 460 |
| THRS | 472 | | CROUT, MVC | 492 |
| DCST | 516 | | THRSe | 568 |
| CBIM | 580 | | CPM | 592 |
| AVC | 600 | | CBSSM | 604 |
| MMVC | 608 | | DCSTM | 676 |
| TSAM | 680 | | DCSTL | 696 |
| TSSM | 700 | | EPMS | 728 |
| CBCM | 744 | | FSBM | 892 |
| SDI, SLS | 140 | | SLP | 148 |
| SS1 | 156 | | SOS | 160 |
| SBC | 176 | | SFX | 180 |
| SS2 | 216 | | NOP | 16 |

**Safety AOIs** (`Class="Safety"`). The total is what the engine prices for the same
AOI as a standard one; the split is its logic and **800** of its definition in safety,
the rest of the definition standard (definition alone: 1,228 against 1,236; with ten
internal rungs and nine locals: 1,560 to the byte). Parameters and locals move only the
standard share: 3/3 and 6/6 BOOL parameters and 9 locals leave the safety reading at
the 1/1 definition's 2,230, and each internal rung adds its logic (10 rungs: +180). A
call in a safety routine costs its standard call cost plus **44**, and a file whose
safety routines call an AOI the standard one-time 264 (exact at 5 and 20 calls;
instances at 5, 20 and 60). A safety AOI exported encoded (sealed, safety-locked) is
priced from its visible parameters, its logic at a minimum, and the engine says so.

**Safety tag mapping** (`SafetyTagMap`, standard -> safety pairs) costs nothing in either
partition: 0, 1, 10, 50 and 200 DINT pairs over the same 200 + 200 tags all read 872,680
standard and 7,810 safety.

**Standard logic reading a safety tag** pays its standard cost plus **8 per safety
bit-instruction operand**, **8 per operand that names a scalar atomic safety tag alone**
(`MOV(SafeDint,…)`; round 4, 50 rungs, and `safe_comp_2`'s twelve), and **4 per other
safety operand** (an element or member: `MOV(SafeArr[i],…)`) (XIC+OTE at 10/50/200, two
safety XICs, a scalar BOOL, MOV from a safety DINT array element and from a scalar safety
DINT, each against its all-standard twin). The safety partition does not move with
standard content. Inside a safety routine a scalar word operand is unmeasured and stays
at 4.

**Standard-side residuals still open** (beyond the realism plant's own −1,794, which every
file shares). Neither of the two larger ones is a safety term: each 1756-L81E twin
reads the same as its safety file.

| residual | where | status |
|---|---|---|
| −8 | a 1/1-parameter safety AOI's definition | noise floor; the 3/3, 6/6 and 9-local ones are exact |
| +4 per standard array tag | `safe_ref_*`, `safe_sref*`, `safe_comp_2`, and `safetwin_sref_ctl` on a 1756-L81E | standard engine, on the plant (OQ-REALUNDER) |
| −16 / −32 per UDT definition | `SafeUdtS` (members D, R, B1, B2), `SafeUdtL` (D0..D9), on both controllers | the member-name pool (OQ-UDTMEMBERNAME, reopened) |
| +16 | 5069-L330ERMS2 v35 base and content step | one catalog; L320ERMS2 exact |
| +16 | 1756-L81ES v32 base and content step | the known L8x v34/v35 +16 (`processor_firmware_correction`) |

### Safety I/O — safety KNOWN per measured type, the device law FITTED (OQ-SAFETYPARTITION)

A CIP Safety device is a module with a Safety* connection; its type family is that
connection's decorated data type without its suffix (`sizing/safety_io.py`). **The safety
partition grows by a fixed amount per device, set by that type, with nothing paid once**
(exact at every count built, 1 / 2 / 4 / 8, each against its control; mixes additive; SIL3
the same as SIL2):

| device | safety connections' types | safety bytes each |
|---|---|---:|
| 1756-IB16S/A | `AB:5000_SDI16` | 6,049 |
| 1756-OBV8S/A | `AB:5000_SDO8` | 4,497 |
| 5069-OBV8S/A, standard data | `AB:5000_DO8+AB:5000_SDO8` | 4,497 |
| 2198-D012 / D020 / D032 / D057-ERS3, integrated safety | `AB:CIP_Motion_Device_Safety2` | 4,717 |
| 2198-S086-ERS3 | `AB:CIP_Motion_Device_Safety1` | 4,123 |
| Balluff BNI00HN (EDS) | `_002B:BNI00HN` | 3,901 |
| FANUC R30iB Plus | `FR:Safety_RobotPlus_8Bytes` | 3,745 |
| generic Ethernet safety device (12 in / 8 out) | `AB:ETHERNET_MODULE_SINT_12Bytes+..._8Bytes` | 3,745 |
| 5069-OBV8S/A, packed | `AB:5000_DO8_Packed+AB:5000_SDO8_Packed` | 3,741 |
| 442G-MABLB-UR-E0JP4679/A | `AB:442G_MABB_E0JP4679` | 3,621 |
| 2198-D032-ERS3 at revision 11, network STO | `AB:CIP_Drive_Safety2` | 3,578 |
| PowerFlex 527-STO, 2198-H008-ERS2 | `AB:CIP_Drive_Safety1` | 3,577 |
| 1734-IB8S/B, with its test-output connection | `AB:1734_IB8S+AB:1734_IB8S_Safety2` | 3,513 |
| 1734-OB8S/B | `AB:1734_OB8S+AB:1734_OB8S_Safety1` | 3,457 |
| 1734-OB8S/A | `AB:1734_OB8S+AB:1734_OB8S_Safety3` | 3,457 |
| 5069-IB8S/A, standard data | `AB:5000_SDI8` | 2,513 |
| 5069-IB8S/A, packed | `AB:5000_SDI8_Packed` | 1,873 |
| 1734-IB8S/B, input connection only | `AB:1734_IB8S_Safety6` | 1,629 |

**The device law — any other safety device** (a custom card, another vendor's device, an
EDS profile), fitted on the 18 types above:

    safety bytes = 1,653 per safety input connection + 1,814 per safety output connection
                 + 16 per byte of the safety connections' data

The data is the connection's stated `InputSize` / `OutputSize` (a DataDriven connection),
else its decorated data's bits / 8 rounded up. It reproduces all 18 within 3.4% (worst the
1,629 one-connection IB8S); each type predicted with itself left out of the fit is within
115 bytes (5.5%), rms 66. Priced from the law alone — every measured table emptied — the
twelve real safety programs' safety figure moves by at most 1.1 points. A device priced by
the law is reported (FITTED), not silent.

**Standard memory** beyond the module's own sizing (`memory_model.yaml` `safety_io`): a
first-device cost and a per-device cost for each measured type, keyed by the device key
where one catalog carries more than one safety shape (the 1734-IB8S/B with and without its
output connection; the 2198-D032-ERS3 at revision 11 against 13) and by the catalog
otherwise, plus a cost shared once by a type family (the 1756 pair 368, the
integrated-safety drives 4,160). The 1734 cards' first-device terms include their test
rack's adapter: a POINT adapter carrying only safety cards reads 634 below its module price
(`safe_io_racks_2x2`), which a real mixed rack never shows, so a real program's first 1734
safety card of a type is priced up to about 630 low. A further 1734 safety card costs 752,
760, 760, then 632 from the fifth, whatever the card (fitted over 1 / 2 / 4 / 8: residual
+75 / +7 / −145 / +63).

For a safety device whose catalog has neither a module entry nor measured terms, the
standard side is the device law too: **600, 162 more with a safety output connection,
1,242 per standard data connection, plus the definitions (UDT law) of its data types the
project has not yet defined** — so a further copy pays only the overhead. On the measured
devices a further copy reads 560..832 (one or two safety connections) and 1,817..2,155 with
a standard connection, and a first copy less a further one equals its types' definitions
within −312..+248 on the nine devices outside the 1734 family (an EDS profile included: 728
against 776). Safety data lives in the safety partition, so the standard side does not
scale with it. A motion device (a drive) is priced by the motion laws instead.

**Produced and consumed safety tags.** A controller-scope safety tag that is produced pays
3,788 in the safety partition beyond its data block, one consumed 1,169 (exact at 1 and 2,
additive; a UDT of CONNECTION_STATUS + DINT produced once, the shape the real programs
carry). In standard memory both cost what any safety tag does, and the peer controller
whose tag is consumed costs 560 standard (a 5069-L306ERS2 in the I/O tree, against the
flat 2,344) and nothing in safety.

**SIL3 costs nothing of its own.** The 1756-L8SP partner of a SIL3 1756-L81ES costs 528
standard (six files, ±8; it was charged the flat 2,344) and nothing in safety; SIL3 safety
cards, drives, the 1756 pair, the empty base and the content step read exactly what SIL2
reads, in both partitions, on the 1756-L81ES and the 5069-L320ERMS3 alike.

## Operand shape — measured, free

A member-path operand costs exactly what a plain tag costs: `U.Bit`, `U.Sub.Bit`,
`UA[2].Bit` and `PD.5` on XIC/OTE, and member source, destination and nested member on
MOV, all exact at 250 and 1,000 rungs (`opshape_*`, 26 files). No operand-shape term.

## Source-protected content — priced at a minimum

A source-protected AOI exports as `<EncodedData EncodedType="AddOnInstructionDefinition">`
with its `<Parameters>` in clear text; a protected routine as `<EncodedData
EncodedType="Routine">` with only its name. `parser/protected.py` gives each protected
AOI a stand-in definition from its visible parameters, so the definition interface,
every instance tag and every call site are priced as for any AOI; each protected
routine pays the ordinary routine shell. Encrypted local tags and logic cannot be
sized: the coverage audit reports them with counts and encrypted size, and the UI
banner states the total is a MINIMUM.

## Modules and I/O

**The file is the final decision on module sizing.** A module costs its
per-catalog **overhead** plus **the size the L5X states**, and every module gets
sized — there is no module shape whose declared data is free.

The catalog number selects the overhead only. It does not and cannot determine
the size, because several catalogs are configurable: `ETHERNET-MODULE`,
`ETHERNET-PANELVIEW` and the generic device profiles have input and output sizes
typed in by hand, so **two instances of the same catalog are different devices**.
Real `ETHERNET-MODULE` instances carry on the order of 40 distinct connection
shapes with input spanning 2 to 450 bytes. No per-catalog constant can express
that, and the file already states it outright.

### Structure

`module_defined_bytes` is computed from the module's own auto-generated
Module-Defined data type — InputTag, OutputTag and ConfigTag structure content,
sized like any UDT.

**An unresolvable connection or config structure falls back to the file's stated
`InputSize` / `OutputSize` / `ConfigSize`** rather than contributing nothing. The
member walk stays primary — it is finer-grained and agrees with the stated
attribute wherever both exist — but a member type the walk cannot size no longer
silently turns the total into a floor. The unresolved type is still reported,
annotated with the stated size that replaced it.

**Rack-aliased, processor-embedded and legacy-network modules are charged their
own declared bytes.** They were previously charged zero. That was right about the
**overhead** — fitted from two modules with their own Connection, with no data on
whether it transfers to those shapes, so it is still not charged and the
reported error is still the record of that — and wrong about the **data**, which
the L5X states as plainly for them as for anything else.

### Per-catalog overhead

`module_overhead_by_catalog` holds 83 catalogs, derived by the same subtraction
method as the predefined structures. A catalog with no entry and module-defined types is
priced by the unseen-catalog law below (a base plus its types); one with neither falls
back to the flat `module_overhead` of **1,672** bytes, the mean of the original two
captured deltas. All stay estimated tier, not exact.

**2198-series servo drives — KNOWN.** The four `2198-D0xx-ERS3` catalogs cost
**4,624 bytes for the first drive and 3,640 for each additional one**: overhead 4,113
first, 3,129 after (4,624 / 3,640 less their common 511-byte declared structure). The
S086 and S130 cost 3,849 / 2,865 overhead. The D012 and S086 were set from round 5's
with-axis captures (`safe_iol_kx_*`, 2026-10-20) where the bare-drive `asmclose_2198_*`
points read 105 for the D012: a drive with its axes is the only shape a real program has.

> The per-catalog distinction previously believed to exist between those six was
> itself an artifact of guessing. The old guesses ran 6,384 bytes high per drive,
> and removing them **unmasked a systematic under-prediction on every real
> program** that the over-charge had been cancelling. One real program with 12
> ERS3 drives moved by exactly 12 × 6,384. A compensating error hides a real one.

### 2198 families share one repeat count — FITTED

A 2198 module's occurrence counts against its **family** — drives (`2198-D/S/C/H`) or
bus supplies (`2198-P/RP`) — not its own catalog. Any later occurrence pays its
first-copy rate less **984** unless its catalog has its own measured repeat rate.
Evidence: `axmarg_1cat_n*` exact with axes on every drive; `modulerack_kinetix_full_bus_r3`
(one P208, three *different* drives) goes from −1,888 to +80 with the discount on the
second and third drive; the Studio-made two-supply file puts its second P208 at 1,000
under the first. An **unseen** 2198 catalog is priced from its family — 4,113 first-copy
for a drive, 3,589 for a supply — rather than the flat 1,672 generic default.

### Module name — measured, not wired

`modname_p208_len*` fit one law exactly: the name is stored twice, each copy rounded up
to 8 bytes, `roundup8(L+3) + roundup8(L+5)`. It also predicts the Kinetix files' +80 and
+72. Real exposure 0.02%; wiring it means re-deriving every per-catalog constant at its
own calibration name length, so it is recorded and not charged (OQ-MODULENAMELEN).

### Repeat-instance discount — KNOWN

From the second module of a catalog onward:

    overhead(occurrence n) = repeat_bytes,  n > 1

`repeat_bytes` is a second per-catalog number, not a constant and not a ratio
(432 to 3,768 bytes, extra-over-first 0.24 to 0.79). Measured at n = 1/2/4/8 with
zero variance, and **per catalog rather than per file** — settled by mixture
files in which reversing module order leaves the total byte-identical, while a
per-file reading requires it to shift.

The discount is enabled for **ten** catalogs whose rate was measured on a shape
real programs actually contain. Seven measured rates are deliberately excluded:

- **ETHERNET-MODULE is a placeholder, not a catalog.** Its cost is driven by
  hand-typed connection sizes, and the sweep that measured it cloned one shape —
  so its rate is the cost of a second identical clone, which no real program has.
- **The six 2198-*-ERS3 drives were measured on bare drive modules with no axis
  tag**, which no real program contains. The with-axis rate is still unmeasured:
  every attempt captured with build errors.

Those two families were 95% of the bytes the full table would have removed from
the real programs. The ten that remain are neutral on real files to within noise
and take the relevant sweep rows from 16 byte-exact to 47.

> `repeat_scope` (`project` or `parent`) decides whether the occurrence count
> runs project-wide or restarts under each parent module. Both are implemented
> and produce byte-identical totals on every real program, because in all of them
> no catalog carrying a measured repeat rate appears under more than one parent.
> **The scope is undetermined by data** and cannot change a real-file number
> until a real file splits a catalog across racks. Default `project`.

### A module-defined type is defined once per project — FITTED (OQ-MODREPEAT)

Every module's connection tags carry Rockwell's own data types (`AB:1756_DI:I:0` and the
structures nested in it), and a project holds each type's definition once. **A module whose
types an earlier module already defined pays its overhead less those definitions**, each
priced with the UDT definition law on the members the module's decorated data lists:

    overhead = catalog overhead − Σ definition(t)   over its types already defined

It reproduces every measured repeat discount: 1734-AENT 520 against 488 of definitions,
1794-AENT 432 / 448, 1756-IB16 792 / 784, 1756-IB32/B 792 / 720, 1756-IB16IF/A 2,208 / 2,312,
842E-CM-M 1,000 / 1,056, PowerFlex 755-EENET-CM-S 976 / 1,048, the 2198 drives 984 / 1,048,
440C-CR30 3,768 / 4,008. The same holds across catalogs (a 1756-OA16I after a 1756-OA16
shares two of its three types) and for any number of copies.

**A type without a vendor prefix is the module's own.** A 5069 Compact I/O card in
standard data format carries channel types named `CHANNEL_DI:I:0`, `CHANNEL_DO_DIAG:I:0`
(two colons where `AB:5000_DI16:I:0` has three). Those are not shared: every module that
carries one defines it again, and a copy an earlier module already defined costs **76**
more on top. Measured on the 34 `rack_5069_*` captures (one to twelve cards a rack, ten
racks with 64 cards in one file): with the prefixed types shared and the channel types
paid by each card, a joint fit of the adapter, the 76 and each catalog's first copy
leaves **rms 17, max 41 bytes**; sharing the channel types too leaves the ten-rack file
29,422 under.

**An unseen catalog** (no entry of its own, no family) is a base plus the definitions of
its types not yet defined in the project: **1,064** for a module with one connection or
none, **2,579** for two or more (the medians of first-copy overhead less type definitions
over 45 and 20 measured catalogs), in place of the flat 1,672. Tested blind on nine 5069
catalogs before their single-card captures were wired: eight within −247 to +329, six
within ±85; the 5069-HSC2XOB4/A at +1,571. ASSUMED.

Not applied: an EDS-profile type (vendor-prefixed name `_0142:...`; an AL1222's second
copy measured its first copy's full cost), a CIP Safety device (priced by its measured
safety_io rows), a rack-aliased card, a module others hang off (an adapter, a bridge), and
any later copy whose own repeat rate is measured (repeat_bytes, the 2198 families).
Census over 251 clean module captures: total |error| 214,854 → 131,710 (every 5069 rack
within ±0.35%), 117 → 128 inside ±8, nothing outside the 5069 racks moved by the
module-scoped rule. Being tested on the realism floor across module
classes by `modrep_*` (TASKS 0zb).


**Batch A, 2026-10-21 (`modrep_*`, 36 files).** Nine catalogs at 1 / 2 / 4 copies on the
realism floor; the first copies were already exact and each further copy costs the same at
2 and at 4, so each now carries its measured `repeat_bytes` (a further copy's total less
its declared data): 1732E-IB16M12R/A 910, 1732E-OB16M12R/A 1,050, 1756-IF8/A 1,063,
1756-OF8/B 1,298, 843E-MIPxxBAx/A 1,438, EX260-SEN1/A 1,014, EX260-SEN3/A 1,016,
PowerFlex 525-EENET 5,618, PowerFlex 755-EENET 1,076. Against those, the law's repeat for
a catalog nobody has measured is right within 1732E +56 / +40, EX260 −72, 843E −40,
PowerFlex 525 −224, 1734-IE2C +221, PowerFlex 755 +632 per copy.

**A prefix-less type is the module's own only on a 5069 card.** The 843E carries two
prefix-less types (`CHANNEL_ENC_DIAG:I:0`, `CHANNEL_ENC:O:0`) beside its prefixed ones; a
further copy reads 1,535 where paying them again charged 2,647, and sharing them leaves it
40 off. `module_scoped_catalog_pattern` = `^5069-`.

**Per-channel configuration is per copy.** The 1756-IF8/A and 1756-OF8/B — specialty
cards with a lot of configuration per channel, which a further copy holds again whatever
type it shares — read 432 and 744 a copy above the law; they are the two whose
configuration tag nests per-channel structures (four and eight, 189.5 and 345 bytes
packed), 2.28 and 2.16 times those bytes, while the five without per-channel configuration
read −221..+72. So a further copy of a catalog without its own measured rate pays
`per_channel_config_factor` (2.2) times its per-channel configuration bytes once its
configuration type is shared: FITTED on two, IF8 −14 and OF8 +15 a copy from the law
alone. The declared data (`module_defined_bytes`) does not count nested structure members
at all — the IF8's per-channel configuration (239 bytes standalone) and the OF8's (628) are
missing from it — which this term does not change; recorded, not altered (every catalog
entry was fitted against the declared data as it is).

### Generic ETHERNET-MODULE connection data — KNOWN

**A generic `ETHERNET-MODULE` connection's data costs 4× its declared bytes.**
Each direction rounds up to a 4-byte word, the two word counts are summed, and
the block costs 16 per word less 8 when that total is odd:

    W = ceil(input_bytes / 4) + ceil(output_bytes / 4)
    connection_bytes = 16 × W − 8 × (W mod 2)

| W | 2 | 3 | 4 | 5 | 9 | 17 | 33 | 65 | 114 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bytes | 32 | 40 | 64 | 72 | 136 | 264 | 520 | 1032 | 1824 |

Exact on all 14 captured points, with the catalog's own overhead at **1,592** and
its 400-byte config array charged as declared.

**The two directions are interchangeable.** A 32-byte input file and a 32-byte
output file are byte-identical captures, and so are the 64-byte pair — only the
**sum** of the word counts matters. No real instance could show this, because
real devices vary both directions at once.

This matters because the profile is **25% of all non-CPU modules in the real
programs** and previously had no per-catalog entry at all.

> **Scoped to this profile on purpose.** The rack sweeps point the same way
> (5069 −992 per module, POINT I/O −932 per card, both under-charged), so a 4×
> connection cost may well be general — but applying it to all captured module
> rows on one profile's evidence is the move this project has had to undo before.

**`CommMethod` encodes the comm format and must agree with the connection's
element type.** Across 183 real instances with no counter-example:

| CommMethod | element type |
|---|---|
| 536870915 | INT |
| 536870916 | SINT |
| 536870914 | REAL |
| 536870913 | DINT |
| 536870932 | no connection at all |

Two arms of the batch that derived the connection law were invalidated by getting
this wrong.

### Module gaps, stated so they are not mistaken for closed

- **POINT I/O racks are still 9–28% under-predicted.** One such file is 2,434
  bytes short with **zero** rack-aliased modules in it, so most of that gap is
  the priced cards' own assumed per-catalog overheads being too low. Needs a
  per-catalog refit under the current formula.
- **CIP-MODULE** (generic CIP device, named EDS without an AOP) is sized with the
  flat 1,672 default. Real shape confirmed: rides a parent bridge's virtual
  CIPBus, one Standard connection with matched input and output size, and a
  decorated type name that literally encodes the byte count. Same risk class as
  ETHERNET-MODULE — overhead probably scales with declared I/O size, not flat.
- **Motion/Kinetix and PowerFlex VFD module shapes** are deliberately untouched.
  They need their own real-shape research, not a safe-looking reuse of the
  backplane or POINT I/O shapes.
- **ControlNet and DeviceNet** are not supported.
- **Zero-connection modules** (no connection, no stated size). An `ETHERNET-BRIDGE`
  with **no child modules** is an IP-address placeholder and costs its node overhead
  only: **320** (KNOWN — exact at 1, 2, 4, 8 and 10 bridges, inhibited or not;
  OQ-BRIDGEPH), charged with no notice. A **5069-AENTR** remote-rack adapter costs
  **625** whatever it carries (FITTED, the 34 `rack_5069_*` captures) and a **5069-SERIAL/A**
  367 (its single-card capture less the adapter). A SIL3 controller's **1756-L8SP** safety
  partner costs **528** and a peer safety controller in the I/O tree (**5069-L306ERS2**)
  **560** (KNOWN, six and four files; OQ-SAFETYPARTITION). Every other zero-connection module — a
  gateway such as a 1756-EN2T, or a bridge with devices beneath it — is charged the
  flat 2,344 (`zero_connection_module`) with a coverage notice. `rack_1756_n12` to `_n16`,
  which add a 1756-CNB/D and a 1756-HYD02 to `_n10`, read +2,384 to +3,458 against +504:
  those modules cost less than the flat rate, by amounts not yet separated. `Local` is
  excluded because its overhead is already in the project baseline. **Under test (batch C,
  `zcm_*`, OQ-MODREPEAT):** the zero-connection catalogs real programs carry on the flat rate —
  an inhibited generic ETHERNET-MODULE placeholder, a 1783-NATR, a 1756-L75 peer controller; one
  real program carries seven, 16,408 bytes at the flat rate.
- **Rack-aliased POINT I/O cards** are priced: declared data plus the
  `rack_aliased_module` overhead from the pioconn_* sweep (OQ-POINTIOCONN). They no
  longer raise a notice; the old one said they were uncharged, which had stopped
  being true.
- **Produced and consumed tags need no special connection formula.** A correctly
  built produced or consumed tag's DataType already includes a
  `CONNECTION_STATUS` member, so ordinary UDT recursion covers it. A Produced tag
  does carry a further +1,072 bytes the model does not charge; this is measured
  and deliberately not wired — see the noise floor rule in `CLAUDE.md`.

---

## Logic instruction weights — FITTED

    delta_bytes = fixed_base + weight × rung_count

**The file carries one routine base of 4,816 bytes** (`fixed_base_per_routine`),
and every extra routine adds `routine_extra` 264 plus its name — a routine that
contains a JSR included (OQ-JSRCALLERBASE). Confirmed identical across 42
instructions.

Fitted from a 244-file per-instruction sweep at five rung-count points each
(10/50/100/1000/5000) with **zero residual against the raw per-file
measurement** — an exact linear fit, not a loose regression.

Logic entries are emitted at estimated tier, separate from the exact tier that
tag and UDT entries use, per the ground-truth constraint in `CLAUDE.md`.

### v36+ instruction names — WIRED

From v36 sixteen ladder instructions are renamed, and a v36+ project rejects the old
name:

| v35 | v36+ | v35 | v36+ | v35 | v36+ | v35 | v36+ |
|---|---|---|---|---|---|---|---|
| EQU | EQ | NEQ | NE | GRT | GT | GEQ | GE |
| LES | LT | LEQ | LE | MOV | MOVE | LIM | LIMIT |
| SQR | SQRT | TRN | TRUNC | XPY | EXPT | ACS | ACOS |
| ASN | ASIN | ATN | ATAN | TOD | TO_BCD | FRD | BCD_TO |

Every weight, surcharge and destination table is keyed by the v35 name, so rung text is
respelled to v35 where it is read and both spellings cost the same. No constant is
involved. OQ-V36MNEMONIC (resolved).

### Two things to understand before using the table

**The raw and isolated columns differ, and the isolated one is what the engine
uses.** Several sweep files' rung text is not just the named instruction — XIC's
file is `XIC(tag)OTE(tag);`, because a bare XIC cannot legally close a rung. The
isolated weights are decomposed using OTE's own clean 16 as the anchor (its file,
`OTE(tag);`, has no companion), so summing occurrences of whatever instructions
actually appear in a real rung reconstructs the right total instead of
double-counting a shared companion.

> Caught by cross-checking the engine's own prediction against real data for a
> 1000-rung XIC file: the engine said 40,816 where the real delta was 24,816.

**The type is the operand's, however it is spelled.** `sizing/operand_types.py`
follows member paths, array elements, aliases, program scope and AOI parameters to
the type the surcharge below keys on. It used to resolve bare controller tag names
only, which left half of all real operands at DINT rate (real set 2.86% → 1.98%).

**Every weight assumes DINT, LINT or REAL operands.** Operand data type changes
the real cost substantially for ADD, SUB, MUL, DIV, MOD, EQU, GEQ, GRT, LEQ, LES,
NEQ, MOV, LIM and CPT. SINT and INT operands cost dramatically more (+88 to +164
per rung depending on instruction); REAL costs somewhat more for some (+16 to
+56) and less for LIM (−8); STRING costs +52 for EQU and NEQ. LINT behaves
identically to DINT. **Every "exact, zero residual" claim in this file and in
`INSTRUCTION_COVERAGE.md` is proven only for DINT/LINT/REAL operands.** The
operand-type surcharge is wired; the narrow-integer widening defect it exposes in
CPT is not fully solved.

### A JSR caller routine is an ordinary routine — KNOWN

`jsrcallers_k{01,02,04,05,10,20}` hold 20 calls and 20 targets fixed while the caller
count runs 1 → 20. Each extra caller routine adds exactly **280** — the plain-routine
increment, `routine_extra` 264 plus a 16-character name — so a caller carries no
dispatch premium at all. The engine counts callers with the ordinary routines in
`task_program_shell`; `jsr_fixed_base_per_routine` (5,096, measured only on files with
one caller) is no longer charged, and the **Subroutine Overhead** tree group it billed
is gone. All six files exact.

**A JSR target written in Structured Text** pays the same declaration as an RLL target,
`jsr_target_declaration` + A(n). It had no charge before; the old per-caller constant
covered it by accident.

> Removing the per-caller constant raised the real-set mean from 1.74% to 3.40%. It
> had been charged 10–87 times per real program on the strength of one-caller files,
> and was cancelling roughly 3% of real content that is still unexplained. See
> OQ-REALUNDER and OQ-OPERANDSHAPE.

**JSR accuracy by parameter kind** (clean captured JSR files, current engine):

| call shape | files | mean error | worst |
|---|---:|---:|---:|
| no parameters | 23 | 0.000% | 0.000% |
| numeric parameters | 20 | 0.049% | 0.190% |
| UDT or STRING parameters | 12 | 7.98% → **0.03%** | 13.05% → **0.09%** |

**Why: a JSR parameter is copied.** With no parameters a JSR is a plain jump to
another routine. With parameters, each input argument is copied into the target's
local parameter on entry and each return value copied back on RET — an atomic value
like MOV, a structure or STRING like COP. The structure copy costs **8 more per
argument per call** and about **12 once per structured parameter on the target**
(`structured_arg_call_extra`, `structured_arg_target_extra`), from
`jsr_paramtype_{udt,string}_n{01..08}_r00100`: +796 per parameter over 100 calls, linear
from 1 to 8 parameters. REAL parameters were already exact. A structured RETURN is
charged the same by the copy-back mechanism; no file isolates one yet.

**What is still not measured, and what it is worth.** Real exposure, standard
processors only (3,582 JSR calls, 0.9% of real instructions):

| case | real count | status |
|---|---:|---|
| no parameters | 3,024 calls (84%) | exact |
| numeric inputs | most of 1,085 input args | 0.05% mean, 0.19% worst |
| UDT/STRING inputs, bare tag | 72 args | 0.03% mean |
| numeric returns | ~480 args | fitted; worst file 296 bytes (0.19%) |
| UDT/STRING returns | 53 args | **measured** (`jsredge_ret_*`): +16/call over a DINT return, +12 on the target |
| member-path or literal args | 604 args | **measured** (`jsredge_in_member_*`): a UDT member costs what a bare UDT tag costs; resolved through the UDT definitions |
| RET that returns values | — | **measured**: 48 per RET + 22 per value, less 72 per target |
| JSR inside an AOI | 0 | untested, no real exposure |

Everything unmeasured totals a few kilobytes across all seventeen programs, under
0.01%. JSR is closed on exposure; it cannot carry the ~3% real residual. Both formerly
unmeasured rows are now measured; 79 JSR files sit at 0.02% mean, 0.29% worst.

### A 0-parameter JSR is EXACT — the first named exception for compiled logic

Compiled ladder size is a fitted heuristic and reads as estimated everywhere
else. `JSR/0` — a JSR whose target takes no parameters — is the first named
exception, because its cost is a measured constant rather than a fitted weight.

**One distinct 0-parameter target plus its call costs exactly 368 bytes**, over
eight independent intervals in two separately built generators, zero residual at
every one:

| pair | interval | per unit |
|---|---:|---:|
| `jsr_multi_distinct_targets_01` → `_03` → `_05` | 2 | 368 |
| `..._n05` → `_n10` → `_n15` → `_n20` | 5 | 368 |
| `..._n20` → `_n50` | 30 | 368 |
| `jsr_crossed_n20_namelen16` → `_n40_namelen16` | 20 | 368 |

Two of those generators produce the identical 25,472 at 20 targets. Target name
length is separately priced and exact at 4 / 8 / 16 / 32 / 40 characters.

**The 280-byte whole-file residual that family used to carry was not this
instruction.** It was `jsr_fixed_base_per_routine` (5,096) exceeding
`fixed_base_per_routine` (4,816) — a shell constant that turned out not to exist; see
the section above. With it removed the family is exact.

**A JSR that carries parameters does not qualify** and stays on the fitted
A(n)/B(n) model — `jsr_paramtype_*` still misses by thousands of bytes on UDT and
STRING parameters. The promotion requires *every* call in scope to be
parameterless: one parameterised call holds the whole rung or routine back,
because a single band is being claimed over all of them.

Wired as `KNOWN_EXACT_CALLS` in `sizing/confidence.py`, mirrored to the client
through the report rather than restated there, and pinned by five tests in
`tests/test_confidence_bands.py`. On the real export this moves **13 routines**
whose only instruction is a 0-parameter JSR from 75% to 100%, and leaves the 20
routines carrying a parameterised JSR at 75%.

> This is a deliberate, named carve-out from the ground-truth constraint's
> blanket "every logic-size number must be flagged as estimated." The constraint
> holds for fitted weights; a measured constant with zero residual across eight
> intervals is not one.

### MAPC is EXACT — the second named exception

**260 bytes per call.** `instrfirst_mapc_v2` (one rung) and `instrfirst_mapc_v2_x10`
(ten rungs) differ only in call count and capture at 61,948 and 64,288:
(64,288 − 61,948) / 9 = **260.000**, equal to the wired weight. Both files sit at the
same flat **+12** of file overhead, so the whole-file residual is the axis and cam
storage around the instruction, not the instruction. Both captured with zero errors.
`instrfirst_mapc_v2_x100` is the third point: predicted 87,676, expected reading
87,688 written down before capture, **captured at 87,688** with zero errors — the same
+12, so the step holds at 1, 10 and 100 calls.

Listed in `KNOWN_EXACT_CALLS` beside `JSR/0` and pinned by `test_mapc_is_exact`.

### Storage-dominated instructions are measured by their step

Twenty-nine instructions — the motion family (MAFR, MAPC, MASD, MASR, MCCP, MDW,
MGSD, MGSR), AVE, FAL, FFL, FFU, FSC, SRT, MSG, FIND, INSERT, OSR, OSF, and ATN, DEG,
NEG, NOT, RAD, SQR, SWPB, TAN, TRN, XOR — have isolation files that are mostly tag,
axis, cam or message storage. They fail the logic-share floor, so their whole-file
error was never credited to them and they read *Unverified*. The step between two
counts of the same family is instruction bytes and nothing else, and all twenty-nine
step at **0.0000%** of their own bytes. `derive_instruction_accuracy.py` now credits
that step; the entries land in `instruction_accuracy` in `memory_model.yaml` and read
*Measured*.

### Bit-shift instructions — BSR and BSL, measured exactly

Both cost **60 bytes per rung**, confirmed over four independent count intervals
(10→50, 50→100, 100→500, 500→1,000) at exactly 60.000 each. BSL and BSR differenced
at equal rung count agree to **+0 at all five counts**, so the shared weight is a
measurement rather than the assumption it used to be.

- **The length operand is free.** Lengths 32 / 64 / 128 / 256 against a fixed DINT[8]
  array capture byte-identically at 24,432.
- **A per-rung CONTROL costs 96 bytes, which is exactly its own tag storage.** There
  is no per-instruction surcharge for a private control structure.

See `RESOLVED_QUESTIONS.md` OQ-BITSHIFT.

### The table

| Instruction | raw | isolated (engine) | fixed_base |
|---|---:|---|---:|
| CPT | 452 | priced per call from its expression, not this weight | 4,816 |
| AVE | 176 | 176 | 4,816 |
| ABS | 120 | 120 | 4,816 |
| LBL+JMP pair | 120 | **64 / 40** decomposed independently | 4,816 |
| XPY | 116 | 116 | 4,816 |
| RAD / INSERT / SRT | 116 | 116 | 4,816 |
| SIZE | 128 | 128 | 4,816 |
| COP / CPS | 112 | 112 | 4,816 |
| CONCAT | 104 | 104 | 4,816 |
| FAL / FSC | 104 | 104 | 4,816 |
| MID / DELETE | 100 | 100 | 4,816 |
| FIND | 100 | 100 | 4,816 |
| CMP | 92 | **76** (CMP+OTE) | 4,816 |
| GSV / SSV | 84 | 84 | 4,816 |
| UPPER | 84 | 84 | 4,816 |
| STOD | 80 | 80 | 4,816 |
| SWPB | 76 | 76 | 4,816 |
| DTOS | 72 | 72 | 4,816 |
| FFL / FFU | 72 | 72 | 4,816 |
| RTOS / LFU | 72 | 72 | 4,816 |
| JSR | 72 | 72 | **5,096** |
| FLL | 68 | 68 | 4,816 |
| LIM | 68 | **52** (LIM+OTE) | 4,816 |
| BTD | 64 | 64 | 4,816 |
| DEG | 64 | 64 | 4,816 |
| MAH / MSO / MAFR / MASR / MDW / MASD | 60 | 60 | 4,816 |
| ATN / TAN | 60 | 60 | 4,816 |
| BSL / BSR | 60 | 60 — **measured, exact** (OQ-BITSHIFT) | 4,816 |
| MGSD / MGSR | 56 | 56 | 4,816 |
| OSR / OSF | 56 | 56 | 4,816 |
| ONS | 56 | **36** (XIC+ONS+OTE) | 4,816 |
| MUL / DIV / MOD / MVM | 56 | 56 | 4,816 |
| TRN / SQR | 52 | 52 | 4,816 |
| MSG | 48 | 48 — logic weight only | 4,816 |
| MEQ | 48 | **32** (MEQ+OTE) | 4,816 |
| ADD / SUB | 40 | 40 | 4,816 |
| NOT / NEG / UID / UIE / XOR | 40 | 40 | 4,816 |
| AND / OR | 40 | 40 | 4,816 |
| DTR | 40 | 40 | 4,816 |
| MOV | 36 | 36 | 4,816 |
| EQU / NEQ / GRT / GEQ / LES / LEQ | 36 | **20** (each + OTE) | 4,816 |
| CLR | 32 | 32 | 4,816 |
| TND | 24 | 24 | 4,816 |
| XIC / XIO / AFI | 20 | **4** (each + OTE) | 4,816 |
| TON / TOF / RTO / CTU / RES | 20 | 20 | 4,816 |
| OTE | 16 | 16 — **decomposition anchor** | 4,816 |
| OTL / OTU / NOP | 16 | 16 | 4,816 |
| MCR | 16 | 16 | 4,816 |
| MCCP | 204 | 204 — logic weight only | 4,816 |

MSG and MCCP carry the logic weight only; the MESSAGE and CAM operands' own tag
data space are separate predefined-structure costs.

**LBL and JMP — KNOWN, valid at any ratio.** The 1:1 pair is an exact linear fit
at 120 per pair across five rung counts. Two further sweeps decomposed it
independently: pure LBL+NOP rungs isolate LBL+NOP at 80, so LBL alone is
80 − 16 = **64**; a fixed-LBL, varying-JMP sweep isolates JMP at **40**. The
cross-check closes exactly: 64 + 16 + 40 = 120. Three independent captures
agreeing, with each instruction isolated from the other, is why this is KNOWN and
valid for any LBL:JMP ratio rather than just 1:1.

### Instructions that will not build

**MAM, MAJ, MAS and MRP fail to build against a real axis tag** with the
2-operand `(Axis, MotionInstruction)` signature that works for MAH, MSO, MAFR and
MASR — every single rung fails. This is a confirmed negative result, not
"untested". Do not retry with a guessed variant; a correct call shape must come
from a real export or a Studio-verified reference.

A verified MAM shape does exist, transplanted from a project Studio compiled:

    MAM(Axis,MotionInstr,1,Position,Speed,% of Maximum,AccelDecel,% of Maximum,
        AccelDecel,% of Maximum,Trapezoidal,Jerk,Jerk,% of Maximum,Disabled,
        Current,0,None,0,0)

**MAPC requires two distinct axis tags** for slave and master. Any type
combination works — virtual paired with virtual is fine; a CIP-Drive/Virtual
pairing is not required. Its original failure was two generator bugs: an
undeclared axis tag, and the same axis tag reused for both positions.

**CROUT and DCS are Safety-family instructions** requiring a safety CPU. Out of
scope, not weight-table gaps, and ignored: no file is built for either and the failed
`instrfirst_crout_x10` build is not pursued.

**CTD is untested deliberately** — zero real usage.

### Array-typed operands need a subscript

Real Rockwell syntax always requires `[index]` on an array-typed operand, and
`SIZE` needs `.DATA[0]` on its STRING operand. Emitting a bare tag name produces
a file that **converts cleanly and never compiles at scale**, which is why every
affected instruction came back at an identical byte count regardless of rung
count.

> **L5X-to-ACD conversion does not catch bad programs.** It only opens and parses
> the project, catching structural and schema failures. It performs no ladder
> verification. `src/sample_gen/lint.py` is a local pre-flight check wired into
> every generator's write path, catching this class and the
> instruction-with-no-definition class. It is not a substitute for real
> verification — it only catches classes of error already found the hard way.

### Branch brackets — FITTED

A branch is compiled to real BST/NXB/BND-family instructions — one BST, one NXB
per extra leg, one BND, so `leg_count + 1` instructions per bracket group — and
each costs a flat **4 bytes**. Nested branches recurse: a branch inside a leg
adds its own `leg_count + 1` on top.

`parser/logic.py`'s `_branch_bracket_instruction_count` does a real
bracket-matching scan, not a naive regex. It distinguishes a branch-opening `[`
from an array index `Tag[5]` by the character immediately before it, and tracks
paren depth so a multi-argument call inside a leg is not miscounted as extra
legs.

Verified exact against all 17 captured points — 10 flat leg-count, 6 nested-depth,
1 trivial no-branch. **The same 4-byte rate explains two independently built
datasets**, not two separate curve fits.

> FITTED, not KNOWN: tested only at 1000 rungs and one tag shape (BOOL XIC legs).

Branch arrangement terms are separately confirmed correct: holding eight XIC
conditions and one OTE fixed and varying only the arrangement across 1, 2, 4 and
8 parallel legs comes back **byte-exact at every leg count**.

### Indirect addressing — WIRED

A direct array index costs nothing beyond existing indexed-tag handling. A
**tag-driven** index costs 84 per index (KNOWN) and an **arithmetic-offset
tag-driven** index 108 (KNOWN) — calibrated on a bare `DINT[20]`.

**What the index selects adds to that** (OQ-INDIRECTUDT, realism floor, each file
against its literal-index twin); the element's size does not matter:

| after the index | extra | confidence |
|---|---:|---|
| a member, `Arr[Idx].M` (elements of 4, 8, 12, 76 bytes; MOV, EQU, XIC on a BOOL member) | **+40** | KNOWN, 6 files |
| nothing, on a BOOL array, `Bits[Idx]` | **+20** | FITTED, 1 file |
| nothing, on a STRING array, `Strs[Idx]` | **+108** | FITTED, 1 file |
| a bit, `Arr[Idx].3` / `Arr[Idx].[Bit]` | 0 (unmeasured) | — |

### Mixed operand types in one call — FITTED

A typed instruction whose operands mix types pays conversions (OQ-MIXEDTYPE):

- **DINT with REAL:** the instruction's REAL surcharge, **+52** per DINT source,
  and a DINT destination **+40** (**+48** on MOV).
- **DINT with INT:** **+52** per INT operand, **+8** when an INT is a source.
- Any other mix: the first resolvable operand's surcharge, as before.

Measured: MOV(D→R) 76, MOV(R→D) 72, ADD(D,R,R) 68, ADD(R,D,D) 108, GRT(R,D) 68,
MOV(I→D) 60, MOV(D→I) 52, GRT(I,D) 60 — all eight exact under the law.

**Literals — KNOWN (2026-10-02, 198 files exact; full table in RESOLVED_QUESTIONS OQ-LITREAL).**
An integer literal against REAL: 52 for the first, 44 for each further one (typed calls and
MAM/MAS REAL parameters). A float literal: +4 over a REAL tag. Against uniform INT/SINT: the
uniform surcharge less 52/40 per literal. REAL with INT/SINT: 108/96 per source, 40 (48 MOV)
per destination. CLR SINT/INT +52; ABS/NEG SINT 92, INT 104, REAL 24/28 (ABS weight 44);
BTD SINT 108, INT 128; TRN REAL destination +52. Constants: `operand_type_surcharge.mixed`,
`single_operand`, `motion_real_params` in memory_model.yaml.

The original finding, kept for its evidence — **literals take the type their spelling implies:** in a typed call,
an integer literal is DINT and a float literal REAL, and the call pays the mixed
conversions above. So `GRT(RealTag,1)` costs a REAL compare plus 52, `MOV(5,IntTag)` 52
(not uniform INT's 104), `MOV(5.0,DintTag)` 72. Evidence: `litop_type_int_lit` (engine
was over by 52 per call, now exact), `litop_form_floatform` (under by 76, now +4), and a
Studio-made edit of one real rung (six `1`/`-1` → `1.0`/`-1.0` against REAL operands
saved 288 beyond the engine, 48 each). A float literal also costs ~4 more than a REAL
tag in MOV (`litop_type_real_lit`, `litop_form_floatform`), not wired. `DINT with SINT`
from a literal is unmeasured (`litop_type_sint_lit` reads −40 per call). Per-instruction
rates: `litreal_*` (47 files).

**Module I/O operands are typed** from each module's Decorated InputTag/OutputTag/ConfigTag
structure (`Mod:I.Data[n]`, `Parent:slot:I.Ch0Data`), so they take part in the mixed-type and
literal rules. 542 of 584 real typed-call module operands resolve (DINT 209, INT 199, SINT 123,
REAL 11); real set 1.29% → 1.27%; no generated row moved (800 module-related rows checked).

**Motion-structure members are typed** for the resolver: axis `ActualPosition`,
`CommandPosition`, `ActualVelocity`, `CommandVelocity`, `AverageVelocity` and the other
numeric attributes REAL, `CIPAxisState` INT, `AxisFault`/`AxisStatus` DINT; CAM `Master`/`Slave`
REAL; MOTION_INSTRUCTION `ERR` INT, `EXERR`/`STATUS`/`STATE` SINT. Types agree with the
instruction-set structure definitions and a controller tag export. 8,800 real typed-call
operands resolved to nothing before; real set 1.74% → 1.41% mean, 3.44% → 3.18% worst. No
generated row moved (836 captured rows across every axis/CAM/motion family checked).

### Cross-program references

A shared alias across programs costs about −16 per rung per additional program.
No formula change needed.

### Task, program and routine shell — KNOWN

`task_program_overhead` is wired and KNOWN: `routine_extra` 264 and `program_extra`
476 exact over real spans, `task_extra` 700 exact at 2, 3 and 6 tasks, and the
per-routine base `fixed_base_per_routine` 4,816 exact on the empty-project baseline
and the `subrtn_shell` control at 1, 5, 25 and 100 routines. The one miss,
`taskoverhead_n04tasks` at +24, is task-name rounding, not the task constant
(OQ-TASKNAMEROUND, below the noise floor). The old "−1,472 per extra task" note that
stood here predated the decomposition and is superseded.

### Composite-scale surcharges — FITTED

Two surcharges apply at real project scale, on top of per-instruction weights:

| constant | value |
|---|---:|
| `aoi_logic_composite_surcharge_per_instr` | 20 |
| `jsr_target_composite_surcharge_per_instr` | (see YAML) |

---

## Expression models

### CPT — FITTED

CPT is priced **per call from its own expression's operator tokens**, not from a
flat rung weight.

> A single flat weight of 452 was wrong as a general constant — it was one
> complex expression's cost, not CPT's. Applied to a simpler expression it
> over-predicted one 1000-rung file by 328,264 bytes. The fix was an architecture
> change, not a constant edit.

**The extra-operand rate is per tier**, not global:

| tier | rate beyond the first operator |
|---|---:|
| 1 (ADD, SUB, AND, OR, XOR) | 24 |
| 2 (MUL, DIV, MOD) | 40 |
| 3 (POW) | falls back to tier 1 — deliberately |

The tier-2 rate was measured against a tier-1 rate that had been applied
universally:

| operators | charged at 24 | real | under-charge |
|---:|---:|---:|---:|
| 1 | 140 | 140 | 0 |
| 3 | 188 | 220 | +32 |
| 4 | 212 | 260 | +48 |

16 per operator beyond the first, with one tier-2 operator already exact to pin
the intercept.

> **Tier 3 keeps the tier-1 fallback on purpose.** Two `**` operators read −16
> and −12 per rung in one arrangement and **+24** in another, differing only in
> adjacency. Two shapes at one operator count 40 bytes apart means adjacency of
> `**` is its own unmodelled term, and any uniform tier-3 rate would fit one
> shape and break the other. One `**` alone, or mixed with one other tier, is
> already exact.

Also wired: `leading_tier1_run_bytes` / `_length` = 4 / 2 (KNOWN, 28 rows).

Residual: +4 per rung on two non-nested two-tier mixes with a tier-1 count of
exactly 2, and on one nested shape whose twin reads 0. Four bytes, two shapes
each way, inside the noise band — recorded, not fitted.

### CMP shares CPT's expression law — FITTED

CMP was priced as a flat 76-byte weight plus two boolean surcharges (compound
condition, float literal) and had **no expression model at all**, so
`CMP(L0+L1>L2)` paid nothing for its arithmetic. It now charges

    cpt_expression.cost_for(arithmetic_operators) − cpt_expression.base_read

on top of its base weight. **No separate CMP fit**: the tier table fitted on CPT
lands on CMP's measured residuals unchanged, which is the evidence the two share
one law. Three shapes went from −36, −36 and −100 to exactly 0.

Comparison operators and the `&&` / `||` connectives are deliberately not
tokenized as arithmetic — the connective is already priced by
`cmp_surcharge.compound_cost`, and double-charging would break every bare
compound CMP, all of which measure exact.

Two residuals survive: −4 on two 2-operator shapes, and −52 on `L0*1.5>L1+2.5`,
where `float_literal_cost` is charged once per call as a boolean but that shape
holds two float literals inside arithmetic.

---

## Structured Text — FITTED

**What the law is measured on, and how an operand is read (OQ-STSHAPE, 2026-10-20).**
Every constant below was measured on bare tags (`D0`, `R1`) and literal array indexes.
Comments of all three forms (`//`, `(* *)`, `/* */`) are free and stripped before
counting. An operand is read whole and typed through the routine's own scope — members,
aliases, program tags, an AOI's parameters and locals — as ladder operands are
(`sizing/operand_types.py`); a subscript is the index, not an operand, operator or
literal of the expression.

**The shapes real ST is written in — KNOWN (OQ-STSHAPE, batch A, 2026-10-21).** 39
`stshape_*` files, each shape 400 statements, 200 IF blocks or 50 FOR blocks against one
control on the realism floor, every residual an exact multiple of its count:

| shape | cost |
|---|---|
| member path (`StU[i].A`), scalar-UDT member, comments | free (already exact) |
| a tag-driven index — destination, source, condition, an instruction's operand (`COP(StD[Ix], …)`), a FOR body, the index spelled as a member path | 84, the rung's `indirect_index` cost |
| an index expression (`StE[Ix + 1]`) | 108 |
| a member after a tag index (`StU[Ix].A`) / a tag-indexed BOOL element | +40 / +20 |
| a second tag index in the same statement (`StD[Ix] := StE[Jx] + 1`; a FOR body indexed twice by its variable) | 8 less (76) |
| IF / ELSIF condition beyond a BOOL or NOT a BOOL: per comparison / AND / OR | +16 / +4 / +16 |
| a comparison on a REAL or against a float literal | 20 more (`StR > 1.5`: +36) |
| ELSE in an IF (a CASE's ELSE is in its branch cost) | +28 |
| BOOL destination from a BOOL or NOT a BOOL, its right-hand side priced as a condition | 28 (AND 32, a comparison 44) |
| BOOL destination from a bare literal | 44 |
| a float literal in a one-operator REAL assignment | +4 (60 where a REAL tag costs 56; OQ-LITREAL's +4) |

Two statements, a nested IF, a literal or tag FOR bound, a literal-indexed COP were exact
before. Wired in `size_st_shapes` and the BOOL-destination branch of
`size_st_assignments`; the 79 earlier ST captures do not move. Inside an AOI's own ST
Logic the same statements read 4 more each, on files whose call rung carried a build
error, so it is not wired (batch B rebuilds them). The real BOOL destinations are 146
literal, 38 copy, 18 comparison; the real conditions comparisons, AND and OR — every real
shape is now a measured one.

**One law**, replacing a five-entry table keyed on operator count whose fallback
over-predicted a one-operator assignment roughly threefold:

    per_statement = base(n_operators, destination type)
                  + each operator's own CPT tier premium above tier 1
                  + 48 per INTEGER-typed NAMED source read into a REAL destination

| operators | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DINT dest | 36 | 40 | 148 | 172 | 196 | 220 | 244 | 292 | 340 | 388 |
| REAL dest | 60 | 56 | 204 | 244 | 284 | 324 | 364 | 444 | 524 | 604 |

Measured at 1,000 statements per file, differenced against the routine shell.
Both rows step once at two operators (108 for DINT, 148 for REAL) and are dead
linear at 24 and 40 per operator after — exact at all eight higher counts.

**The step is the mechanism**: a single-operator assignment compiles to one
instruction; a compound one reaches for expression evaluation. REAL at one
operator costing 4 **less** than REAL at zero is measured, not a transcription
slip.

**All three of the old table's non-trivial entries come back from the law**,
which is what says it was mis-parameterised rather than incomplete. Each had been
measured on a different expression and then keyed on operator count alone:

| old entry | the expression it came from | reproduced as |
|---|---|---|
| 152 | `R0 := D0 + D1;` | 56 + 2 DINT sources × 48 |
| 164 | `D0 := D1 + D2 * 2;` | 148 + 1 multiplicative × 16 |
| 452 | `R0 := (D0+D1)*R1 - R2/2 + 1.5;` | 324 + 2 mult × 16 + 2 DINT × 48 |

**The operator premium is the CPT tier table, unchanged.** Holding the operator
count at four and varying only which operator: `+`, `AND` and `XOR` all read 196
per statement; `*`, `/` and `MOD` all read 260. 64 over four operators is 16
each, which is exactly the CPT tier-1-to-tier-2 step — so ST asks that table for
`tier_cost(op) − tier_cost('+')` rather than carrying a classification of its
own. **AND and XOR are now measured at tier 1**, which the CPT table did not
cover at all.

**Integer literals do not pay the conversion term.** Only named integer sources
do. That is what fixes the rate at 48.

Also wired: the bitwise one-operator class at 124 for DINT (KNOWN, three files),
exponent at 204 DINT, operator premium 38 DINT and 0/8 REAL for
multiplicative/exponent, and real-destination source conversion at 92 SINT,
104 INT, 0 LINT (KNOWN, cross-checked exactly by a mixed file).

### An AOI called as a bare ST statement — FITTED

**`120 + 16 per parameter`**, charged **nothing** until measured — the same
mixed-case invisibility that hid RLL call sites, and the same two constants as a
call from a rung. Measured on four files whose labels count declared *input*
parameters while each call also passes the output, so the parameters passed are
2, 3, 5 and 9: 152, 168, 200 and 264 per call, exact at all four. Plus
`st_aoi_call_routine_bytes = 264` (KNOWN, seven rows).

> A first pass fitted `136 + 16p` by trusting the label. It fit all four points
> **just as exactly** and was wrong: two constants against four collinear points
> absorb an off-by-one silently.

> The real held-out set contains thousands of ST assignments and **zero** AOI call
> statements, so this term moves real files by nothing. It is right anyway.

---

## JSR, SBR and RET

The flat 72-per-rung JSR weight covers the base call only. A real per-parameter
cost decomposes as `delta(n,R) = A(n) + B(n) × R`:

| term | value | what it is |
|---|---|---|
| `B(n)` | `4 + 20n` | per-call-site marginal rate, charged per real call, `n` read from the call's own second argument — the declared parameter count Studio itself writes there |
| `A(n)` | `104 + 20n` | the target routine's one-time parameters-block declaration, charged **once per distinct target**, never per call site |
| `b_multiparam_extra` | 4 | KNOWN, 13 rows |
| `per_target` | 160 | KNOWN, 13 rows |
| `sbr_ret_operand_bytes` | 112 | KNOWN, 16 rows, with 12 parameterless controls holding at exactly 0 |
| `output_param_cost` | per output arg, same rate as input args | |

**A JSR target routine does not charge its own `fixed_base_per_routine`** — that
stays folded into the caller's 5,096. Charging it again overcounted every
JSR-using program by roughly 4,832 bytes. `RoutineLogic.is_jsr_target` flags the
target and `report.py` passes `charge_shell=False`.

**But the target's own instruction content is not skipped.** A JSR target with
substantial content genuinely costs real memory — maximum 13.37% residual on an
isolated content-scale sweep before this was fixed, cut to 4.75% after. It is
weighted with the same per-instruction table as any ordinary routine.

---

## Tag-based alarm conditions — FITTED

    alarm_conditions = 800 file base
                     + 500 per condition
                     + an associated-tag term per AssocTag1/2/3 target

| associated tag type | bytes |
|---|---:|
| BOOL | 88 |
| DINT / REAL | 92 |
| STRING | 256 |
| unresolved | 256 |

Derived exactly from a 37-file batch. Alarm name length, message text, severity
and delay values were all proved **free**.

**Measured inside real content.** Two real programs were captured with and
without their alarm elements, an exhaustive element-tag diff confirming
`AlarmCondition`, `AlarmConfig`, `HMIGroup` and `AlarmConditions` were the only
elements that moved:

| conditions | actual | predicted | actual per condition | predicted per condition |
|---:|---:|---:|---:|---:|
| 400 | 443,128 | 442,400 | 1,107.8 | 1,106.0 |
| 200 | 243,040 | 221,600 | **1,215.2** | 1,108.0 |

Within 0.16% on one file, 8.8% short on the other. In both, every condition hangs
off a single BOOL array tag.

**Scale matters more than the error: this is 19% and 21% of total controller
memory respectively — the second-largest category in both files.**

> Those readings came from files derived from real exports, which were later found
> not to import. Re-derive before citing further. The per-condition formula itself
> rests on the 37-file generated batch and is unaffected.

**Three separate things share the word "alarm" and must never be reported as
one:**

1. The **ALMD / ALMA instructions** — zero occurrences in the real set, parked.
2. **Controller-scope Alarm Manager definitions** — the 19–21% above.
3. An ordinary scheduled **program named for alarms** — plain ladder.

Any statement that alarms are out of scope applies to the first only.

---

## Immediate literal operands — CLOSED ON REAL EXPOSURE

> **Current law (OQ-LITREAL, OQ-MOTIONLIT, OQ-BLOCKSTR, OQ-AOILITARG).** The controller
> handles every immediate as a DINT. Against a REAL operand an integer literal costs 52
> for the first and 44 for each further one, a float literal 4. Wired on the typed math
> and compare instructions, on the REAL parameters of MAM, MAS, MAJ, MAPC, MCCP and MAG
> (`operand_type_surcharge.motion_real_params`), on FLL of an integer literal into REAL
> (+52 once), and on an AOI REAL Input argument (+52, float +4). The weights of MAJ (184),
> MAPC (164) and MCCP (108) are the all-tag cost; their old captured weights had literals
> baked in. The summary below is the earlier, superseded closure.

> **Superseded summary, read this first.** The literal-operand batch and a count
> over eighteen real exports closed this: integer literals (DINT, LINT) are free;
> a REAL literal is +4 per slot (930 real slots, 3,720 bytes); the float literal's
> written form is +76 per rung (one pair); and the engine's INT/SINT over-charge on
> `MOV(<literal>, <narrow tag>)` totals 1,756 bytes across all eighteen programs.
> None is wired; all are below the noise floor. The section below is the original
> hypothesis and bench measurement, kept for the reasoning. See
> `RESOLVED_QUESTIONS.md` OQ-LITERALOPERAND.


**An immediate numeric literal in an instruction operand costs bytes the engine
does not charge.** Literals are priced today **only** inside CPT expressions, CMP
operands and ST statements. Everywhere else they are free, and that is wrong.

| case | cost | tier |
|---|---:|---|
| REAL literal in a REAL-typed motion parameter | **4** | MEASURED — bench, 6 slots in one rung |
| REAL literal inside a CPT expression | 4 | FITTED — 12 files at 1, 2 and 3 literals |
| DINT / INT / SINT / LINT literal, any instruction | **UNKNOWN** | hypothesis: the type's width, inline |

**The measurement.** One rung in one project, edited in Logix Designer, compiled
by Studio, Capacity read twice. Six MAM operand slots changed from a tag
reference to the immediate `99.99`, with the four source tags still declared **and
still referenced** by EQU on the same rung in both versions:

    74,224  →  74,248   = +24 over 6 slots = +4.000 per slot, exactly

**Two independent paths agree on 4.** The CPT model fitted 4 per float literal
across 12 files; MAM measures 4 per float literal on the bench. One constant
appearing in two unrelated instructions priced by two unrelated code paths is
what a general law looks like, not a per-instruction quirk.

**Why nothing is wired.** The 4 is measured for a REAL literal only. Across the
real programs there are **52,195 unpriced literal operand slots — 12.1% of all
432,850 operand slots**, worth 208,780 bytes at 4 each, which is about a quarter
of the total residual. But **51,265 of those are integer literals at an
unmeasured rate** and only 930 are float. Charging the integer slots at 4
extrapolates 55× beyond the evidence. Fitting the rate against the real set gives
mean-optimal 2 and max-optimal 6.5, and that disagreement is itself evidence that
a single flat rate is the wrong shape.

**Hypothesis to measure:** an immediate costs the width of its type, stored
inline — REAL 4 (measured), DINT 4, INT 2, SINT 1, LINT 8, matching the atomic
table. The competing hypothesis is that it follows the **slot's** declared width
rather than the literal's.

A 29-file batch (`litop_*`) is built and awaiting capture. See
`SAMPLE_GENERATION.md` for what each arm discriminates.

---

## Export scope: what a partial export may be charged

Studio exports at six granularities and the root element declares which:
`TargetType` = `Controller`, `Program`, `Routine`, `Rung`,
`AddOnInstructionDefinition` or `DataType`, with `ContainsContext="true"` on every
partial one. Inside a partial export the exported thing is marked `Use="Target"`
and everything it merely references is `Use="Context"`.

**Only a whole-controller export — `TargetType="Controller"` AND
`ContainsContext="false"` — may be charged the project-level constants:**

| constant | why it is project-only |
|---|---|
| `empty_project_baseline` | a controller's fixed scaffolding |
| `firmware_baseline_delta` | there is no firmware baseline of a rung |
| `catalog_baseline_delta` | keyed on ProcessorType, a project property |
| `safety_capable_baseline_delta` | same |
| `task_program_overhead` | fitted as one base plus per-extra task/program/routine **across a project**; a partial export's routines are mostly context, so counting them invents a project |

Everything else — tag storage, UDT and AOI definition cost, per-instruction
weights — applies normally to whatever the file contains.

**Target versus context.** An element is target-scope if it or an ancestor
carries `Use="Target"`. **The nesting is not intuitive**: in a rung export the
chain is `Program Use="Context" > Routines Use="Context" > Routine
Use="Context" > RLLContent Use="Context" > Rung Use="Target"`. So "is it inside a
context container" is the wrong test — only the nearest `Use` attribute up the
chain decides.

`split_totals()` reports **target** (what was exported), **context**
(declarations it references, which cost bytes only if the destination controller
does not already have them) and **project** (base load, zero on any partial
export by construction).

> Two parser bugs this exposed, both fixed, both worth knowing:
> 1. A rung export's containing `Routine` element carries `Use` and `Name` but
>    **no `Type` attribute**, so requiring `Type == "RLL"` parsed every rung
>    export to zero routines and never sized the exported rung. Routine language
>    is now inferred from the content child when `Type` is absent.
> 2. A target routine inside a context program was classified as context,
>    reporting target = 0, because routine and program-tag paths share the
>    `program:<P>/<X>` prefix and the program was checked first.

---

## The KNOWN register

These constants were measured alone, at several counts, with zero residual, and
carry `*_confidence: KNOWN` beside their value in the YAML even where the
surrounding block reads FITTED. `tests/test_measured_known_constants.py` pins each
to both value and tier.

| constant | value | rows | span |
|---|---:|---:|---|
| `jsr_param_cost.b_multiparam_extra` | 4 | 13 | call counts 10/100/1,000 × param counts 1–15 |
| `jsr_target_declaration.per_target` | 160 | 13 | target counts 1–50, two generators, name lengths 4–40 |
| `jsr_target_declaration.sbr_ret_operand_bytes` | 112 | 16 | target counts 1/10/50/200 plus 12 parameterless controls at 0 |
| `logic_instructions.weights.DTR` | 40 | 3 | 10/100/1,000 rungs against a weight of zero |
| `cpt_expression.leading_tier1_run_bytes` / `_length` | 4 / 2 | 28 | four arrangements × operator counts 3–9 |
| `structured_text.…dint.bitwise` | 124 | 3 | AND, OR, XOR all at the same +84 over additive |
| `structured_text.…dint.exponent` | 204 | 1 | |
| `structured_text.assignment_operator_premium.dint.exponent` | 38 | 1 | at four operators |
| `…real.multiplicative` / `…real.exponent` | 0 / 8 | 2 | |
| `structured_text.real_dest_source_conversion_bytes` SINT/INT/LINT | 92/104/0 | 4 | one file per type, cross-checked by a mixed file |
| `structured_text.st_aoi_call_routine_bytes` | 264 | 7 | three files at one call against four at a thousand |
| `logic_instructions.weights` AND/OR/RTOS/LFU/UPPER | 40/40/72/72/84 | 15 | 10/100/1,000 rungs each |

**What stays FITTED, deliberately:** `a_base`, `a_per_param` and `b_per_param` in
`jsr_param_cost`; `st_aoi_call_bytes` and `st_aoi_call_per_param_bytes`; the ST
base ladder; the two-tier CPT mix rates. Those were regressed, and marking their
blocks KNOWN would launder them.

---

## Standing lessons

Each of these cost real time. They are the reason the tiers above are enforced
rather than trusted.

1. **Two terms that each fit their own sweep exactly can be wrong together.** The
   UDT definition base, the four superseded AOI definition terms, and the ST
   operator table were all this failure. Solve slices as simultaneous equations.
2. **A fit that fits every point can still have the wrong shape.** `136 + 16p` fit
   four collinear ST points exactly and was off by one parameter. `(len−7)//4` fit
   seven AOI name-length points and put length 19 in the wrong bucket.
3. **A compensating error hides a real one.** The 2198 drive over-charge was
   masking a systematic under-prediction on every real program.
4. **Re-run the residual census after any change to a shared constant.** A −16
   baseline correction that looked correct moved 787 exact captures to wrong.
5. **A file that converts is not a file that compiles.** Conversion performs no
   ladder verification.
6. **Cross-validate before keeping a fit.** Several surcharge fits looked good in
   sample and were rejected at this step.
