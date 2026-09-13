# Capture-batch segment tracker

The 594 `.L5X` files pushed 2026-09-12, grouped by generator family, each worked
to a resolution on the open question it was built for. Marked off one segment at
a time. Status values are CLOSED (question resolved), WIRED (engine changed and
verified), or the specific thing still blocking.

Counts are from the 616-capture merge of 2026-09-13. `band` is rows within the
project's ±8 universal-residual band.

| # | segment | files | capt | err | owning question | status |
|---|---|---:|---:|---:|---|---|
| 1 | `aoialgn_*` | 71 | 71 | 0 | OQ-AOIBOOLPACK-PAIRING | **CLOSED — 2 laws wired** |
| 2 | `aoilt_*` | 54 | 54 | 0 | OQ-AOIDEFITEMIZE | **CLOSED — 54/54 clean** |
| 3 | `dscale2_*` | 39 | 39 | 0 | OQ-DEFSCALE | **CLOSED — 5 laws wired, biggest find of the project** |
| 4 | `aoimix_*` | 34 | 34 | 0 | OQ-AOIBOOLPACK-PAIRING | **CLOSED — AOI definition cost re-derived from scratch** |
| 5 | `addit_*` | 33 | 33 | 0 | OQ-COMPOSITESCALE | **CLOSED — the categories are additive, 24/24 exactly** |
| 6 | `stx_*` | 30 | 30 | 0 | OQ-STEXPR | **CLOSED — one law replaces a five-entry table** |
| 7 | `genem_*` | 27 | 24 | 0 | OQ-MODULESTRUCTURAL | **CLOSED for ETHERNET-MODULE — 2 arms invalid, rebuilt** |
| 8 | `ntag_*` | 25 | 25 | 0 | OQ-VERIFINSTR | **CLOSED — 20/20 exact; the other 5 kill a OQ-SERIESOUTPUT candidate** |
| 9 | `identnamelen_*` | 24 | 19 | 5 | OQ-IDENTNAMELEN | DEFERRED — has errored rows, worked at the end |
| 10 | `udtmn2_*` | 23 | 23 | 0 | OQ-UDTMEMBERNAME | **CLOSED — with 11; biggest real-file gain of the day** |
| 11 | `udtmn_*` | 24 | 24 | 0 | OQ-UDTMEMBERNAME | **CLOSED — its length arm is what discriminated the form** |
| 12 | `cpttier_*` | 22 | 22 | 0 | OQ-CMPCPTLAYOUT | **CLOSED — tier-2 extra-operand rate was a tier-1 rate** |
| 13 | `modmarg_*` | 19 | 19 | 6 | OQ-MODULEMARGINAL | DEFERRED -- has errored rows, worked at the end |
| 14 | `asmclose_*` | 71 | 69 | 0 | OQ-MODULEIO | **WIRED — repeat discount on for 10 catalogs, 2 rows cleared, 4 flagged bad** |
| 15 | `aoishape_*` | 17 | 17 | 0 | OQ-AOIINTERNALLOGIC | pending |
| 16 | `axmarg_*` | 16 | 16 | 9 | OQ-AXISMARGINAL | DEFERRED -- has errored rows, worked at the end |
| 17 | `platform_*` | 15 | 10 | 0 | OQ-REAL5069 | pending |
| 18 | `cmpfl_*` | 13 | 13 | 0 | OQ-CMPCPTLAYOUT | reviewed with 12 — 13 single-rung points, not derivable |
| 19 | `cptpow_*` | 12 | 12 | 0 | OQ-CMPCPTLAYOUT | reviewed with 12 — ** adjacency worth 40, tier 3 left alone |
| 20 | `cptdest_*` | 12 | 12 | 0 | OQ-CPTARRANGE | pending |
| 21 | `alarmbits_*` | 12 | 12 | 0 | OQ-ALARMDEF | pending |
| 22 | `cptpos_*` | 9 | 9 | 0 | OQ-CPTARRANGE | pending |
| 23 | `pool*` | 9 | 9 | 0 | OQ-SHELLCONST | pending |
| 24 | `v3abl_*` | 8 | 8 | 0 | OQ-V3GENBUGS | pending |
| 25 | `albool_*` | 8 | 8 | 0 | OQ-AOIARRAYLOCALTAG | pending |
| 26 | `altype_*` | 6 | 6 | 0 | OQ-AOIARRAYLOCALTAG | pending |
| 27 | `almult_*` | 3 | 3 | 0 | OQ-AOIARRAYLOCALTAG | pending |
| 28 | `aldim_*` | 3 | 3 | 0 | OQ-AOIARRAYLOCALTAG | pending |
| 29 | `uwclose_*` | 3 | 0 | 0 | OQ-VERIFINSTR | not captured |
| 30 | `aoi_logic_scale_*` | 4 | 4 | 3 | OQ-AOIINTERNALLOGIC | DEFERRED -- has errored rows, worked at the end |
| 31 | `aoi_multiroutine_*` | 2 | 2 | 2 | OQ-AOIINTERNALLOGIC | DEFERRED -- has errored rows, worked at the end |

## Segment 1 — `aoialgn_*`, OQ-AOIBOOLPACK-PAIRING: CLOSED

71 files, all captured, zero build errors. Three groups, all three resolved.

**Group A (36 files) — the DWORD per-instance term, MECHANISM FOUND.** The
engine's packed-word count was `ceil(bool_count / 32)`. The real count is
`ceil((bool_count + 2) / 32)`: EnableIn and EnableOut occupy two bits in the
same words, and `bool_count` deliberately excludes them because they are not
declared members — an exclusion that was correct for the member sum and got
carried into the word arithmetic by accident.

Confirmed 12 of 12 across three consecutive 32-bit boundaries, with the slope
measured twice per family (n=2→4 and n=4→8):

| bool_count | ceil(bc/32) | ceil((bc+2)/32) | predicted | observed |
|---:|---:|---:|---|---|
| 30 | 1 | 1 | flat | flat |
| 31 | 1 | 2 | sloped | −4.0/instance |
| 32 | 1 | 2 | sloped | −4.0/instance |
| 33 | 2 | 2 | flat | flat |
| 62 | 2 | 2 | flat | flat |
| 63 | 2 | 3 | sloped | −4.0/instance |
| 64 | 2 | 3 | sloped | −4.0/instance |
| 65 | 3 | 3 | flat | flat |
| 94 | 3 | 3 | flat | flat |
| 95 | 3 | 4 | sloped | −4.0/instance |
| 96 | 3 | 4 | sloped | −4.0/instance |
| 97 | 4 | 4 | flat | flat |

Wired as `aoi_array.enable_bits_packed_with_bools: 2`. All 12 families are now
flat in instance count. This supersedes the earlier reading — "only the
32-bit/DWORD boundary specifically also carries a real per-instance term" —
which was the right observation with no mechanism, and could not have predicted
63/64 or 95/96 because it treated 32 as special rather than as the first place
two extra bits spill a word.

**Group C (8 files) — the array-tag flat cost, WIRED.** Each `def_only` control
carries the same AOI definition with no instance tag. Across 24 measurements
the array file sits exactly 4 bytes further under its own twin in 18, at bool
counts 0, 5, 10, 18 and 30. The 6 that read −12 are both `mc60` families (bool
counts 54 and 60) and are a separate 8-byte effect.

This term was fitted and REJECTED on 2026-09-12 because it cost five exact
predictions. Those five are now explained: every one is a `b02` file —
bool_count = 2, exactly the number of enable bits — so the engine's BOOL term
cancels its own error at that one degenerate count and the row was exact by
coincidence. Wired as `aoi_array.array_tag_flat_bytes: 4`; it moves 26 rows
into the ±8 band and cuts total absolute residual over the 283 AOI-array rows
by 204 bytes.

**Group B (27 files) — a different law than expected, HANDED OFF.** The 8-byte
block alignment is inert here: the engine's per-instance size is already
8-aligned for all nine shapes. What is wrong is the per-instance size itself
when members are narrow types. Real per-instance is `8 × ceil(member_bytes / 4)`,
fitting all 9 shapes:

| shape | members | member bytes | engine/inst | real/inst |
|---|---|---:|---:|---:|
| `s01` | 1 SINT | 1 | 0 | 8 |
| `s02` | 2 SINT | 2 | 8 | 8 |
| `s03` | 3 SINT | 3 | 8 | 8 |
| `s05` | 5 SINT | 5 | 8 | **16** |
| `s01i01` | 1 SINT + 1 INT | 3 | 8 | 8 |
| `s03i01` | 3 SINT + 1 INT | 5 | 8 | **16** |
| `s01i03` | 1 SINT + 3 INT | 7 | 16 | 16 |
| `i01` | 1 INT | 2 | 8 | 8 |
| `i03` | 3 INT | 6 | 8 | **16** |

Not wired here because it is an AOI *element-size* law, not an array law —
changing it moves every AOI instance in the corpus, scalar included. Handed to
OQ-AOIDEFITEMIZE (segment 2) where the element size is the subject.

Effect: `aoialgn` rows within ±8 went 22 → 29 of 71, and the remaining residual
is a per-family CONSTANT in every one of the 12 bool-count families — the
definition-cost question, not the array question. Real programs unchanged at
3.65% mean (real files use scalar AOI instances, not arrays).


## Segment 2 — `aoilt_*`, OQ-AOIDEFITEMIZE: CLOSED

54 files, all captured, zero build errors. Two arms.

**`aoilt_dim_{dint,timer}` (14 files) — CONFIRMED EXACT, no change needed.**
Dimensions 2 / 4 / 16 / 32 / 128 / 256 / 1024 on an array-dimensioned declared
member, for a plain atomic (DINT) and a predefined structure (TIMER). All 14
reconcile at exactly 0 across a 512x range. The array-member data-space law
wired 2026-09-11 is correct as it stands, including for a predefined element
type at 1024 elements.

**`aoilt_swap_*` (40 files) — ONE LAW WIRED, zero residual.** Each file swaps k
of 8 DINT LocalTags for another type with the member count held at 8, so the
per-TYPE rate separates from the per-ITEM rate. Eight counts per type, where
only two existed before.

    extra_bytes = 8 * floor(sum(count_T * rate_T) / 8)

| type | rate | shape of the residual before wiring |
|---|---:|---|
| REAL | 0 | flat -8 at every k -- REAL costs what DINT costs |
| TIMER | 8 | -16, -24, -32 ... -72, a clean -8/swap |
| COUNTER | 8 | identical to TIMER |
| MOTION_INSTRUCTION | 12 | -16, -32, -40, -56 ... alternating -16/-8 |
| STRING | 84 | -88, -176, -256, -344 ... alternating -88/-80 |

The FLOOR is the half that two data points could not have shown. TIMER and
COUNTER are 8/member and land on the 8-byte boundary, so they look perfectly
linear; MOTION_INSTRUCTION (12) and STRING (84) alternate because odd counts
lose the remainder. A slope fitted to either from two points gives 12 and 84
and is wrong at every odd count. All 40 rows now sit at exactly -8, the
universal per-file residual.

Only types absent from `per_type_rate` may appear in this table or the cost
lands twice; a test pins that. REAL is listed at 0 to record that it was
measured -- and it independently agrees with `per_type_rate`'s REAL == DINT.

ASSUMED, not measured: that the rates ADD when one definition mixes two
non-atomic types. Every file here mixes exactly one non-atomic type with DINT.
Sum-then-floor is the natural reading and is what is wired.

The UI drill-down gained a `Non-atomic member types (...)` line. The extra is
floored over the whole member set, so it cannot be divided among the per-member
rows without the parts failing to sum to the whole -- it is one line for that
reason, and a test pins that the breakdown still totals the charge.

**Segment 1's group-B law did NOT land here.** That one is about AOI *instance*
element size for narrow members (`8 x ceil(member_bytes / 4)`, 9/9). This
segment's law is about the *definition*. They are separate costs and the
definition fix does not touch the instance sizing, so group B stays open and
carries forward.

Effect: `aoilt` within +-8 went 22 -> **54 of 54**. Real programs improved from
3.65% to **3.61%** mean absolute error, worst -6.06% -> **-5.97%** -- small, but
it is movement in the right direction on the held-out set, which most wiring
this session has not produced. Corpus exact 1,150 -> 1,143: seven rows that were
exact lost it, which is the expected sign of other AOI families having carried a
compensating error.


## Segment 3 — `dscale2_*`, OQ-DEFSCALE: CLOSED, and it answers OQ-REALUNDER

39 files, all captured, zero build errors. Five laws, each exact over its own
sweep. One of them is the largest unmodelled item this project has found.

### An AOI CALL SITE cost nothing at all

`parser/logic.py` matched instruction calls with `[A-Z][A-Z0-9_]*\(`, under a
comment claiming it "also matches AOI/UDT instance calls". **It does not.** Real
AOI names are mixed-case -- `fbDebounce`, `AnalogSensor`, `HomeToTorque` -- and
that pattern cannot match them. **288 of the 331 AOI definitions in the real
corpus are mixed-case**, so 87% of real AOI definitions and **3,918 real call
sites** were invisible to the counter and cost zero bytes.

Measured from `dscale2_aoi_d001_t001_c{005,020,060}` and `_call` -- the same
instance called 1, 5, 20, 60 times:

| calls | 1 | 5 | 20 | 60 |
|---|---:|---:|---:|---:|
| delta | −421 | −1,093 | −3,613 | −10,333 |

−168 per call at every step, and **all four files agree on the same intercept
(−253)**, which is what says 168 is the rate rather than a per-file artifact.
Cross-checked on a second, independent axis: `_t*_call` runs t instances each
called once, t = 1..100, slope −160/instance = the −168 call plus the +8
per-instance over-charge below. Two sweeps varying different things return the
same number.

### The other four, all exact

| item | correction | evidence |
|---|---|---|
| UDT definition | **+16** | `delta = −16·n_udt − 3·n_tags`, 14 of 14 rows |
| UDT tag instance | **+3** | same law, 1..25 definitions x 1..500 tags |
| AOI instance | **−8** | `delta = 3·n_def + 8·n_inst`, 7 of 7 rows |
| AOI definition | **−3** | the residual `3·n_def` term once the −8 lands |

3 is not 4-aligned, which is unusual here. It is what 14 rows spanning a 500x
tag count say, at −3.000 per tag at every one of the nine count points in the
`u001` sweep alone, so it is not a rounding artifact. The two AOI corrections
are in the opposite direction to everything else found today, which is why they
are stated separately rather than folded into one "instances cost more".

### Effect on the held-out real set

This is the OQ-REALUNDER answer, or most of it.

| | before | after |
|---|---:|---:|
| mean absolute error | 3.65% | **2.16%** |
| worst | −6.06% | **−4.28%** |
| inside 1% | 0 of 16 | **3 of 16** |

| program | before | after |
|---|---:|---:|
| `griffin_stackerline` | −1.67% | **−0.01%** |
| `horizon_edger` | −2.57% | **−0.38%** |
| `salamanca` | −0.98% | **+0.37%** |
| `emporiumedger` | −3.63% | −1.07% |
| `pukall_gang` | −4.09% | −1.71% |
| `emporium` | −3.63% | −1.95% |

`griffin_stackerline` is now 394 bytes out on a 2.3 MB program. Three files are
inside the 1% North Star for the first time.

`dscale2` itself went 3 -> 28 of 39 within +-8; the 14 UDT rows are at exactly 0
and the call families collapsed from −10,333 to a flat −253.

### What is still open from this segment

The **−253 intercept** on every call family. It is identical across all four
call-count files, so it is the one-time cost of a routine that contains AOI
calls at all, not a per-call term. Not wired -- one number from one shape is not
enough to tell a routine-shell cost from a first-call cost, and this segment has
no file that varies the containing routine while holding calls fixed.

Corpus exact fell 1,150 -> 1,123. Expected: five corrections landed at once and
rows that were previously exact by cancellation lose it. The held-out real set
is the metric that counts, and it improved by a third.


## Segment 4 — `aoimix_*`, OQ-AOIBOOLPACK-PAIRING: CLOSED

34 files, all captured, zero build errors. The grid's own question closed on the
array side, and the residual it was kept for turned into the largest single
model correction of the batch.

**The array side: 17 of 17 mixes, zero exceptions.** Every grid point was built
at an even AND an odd array length, and the even and odd deltas are IDENTICAL at
all 17 points. That reads the per-instance law directly at each mix instead of
inheriting it from a neighbour:

    per_instance = align8(4 * atomic_count + 4 * ceil((bool_count + 2) / 32))

confirmed at per-instance sizes from 8 to 136 bytes, including two points past
the second packed-word boundary (`t32_b32`, `t64_b32`) and one past the third
(`t64_b64`). The premise this grid was built for -- "a two-variable surface in
(bool_count, atomic_count), sampled far too sparsely" -- is dead for the reason
segment 1 found: BOOL/atomic mix only ever moved the per-instance size.
OQ-AOIBOOLPACK-PAIRING is closed and moved to `docs/RESOLVED_QUESTIONS.md`.

**The definition side: four fitted terms replaced by one itemised form.** The
grid held the member total constant while sweeping the BOOL fraction, which is
the axis the definition-cost model handled worst. Its residual ran -105 to +69
across the 34 rows. Differencing the t32 series against the engine's own
definition component gave

    true_definition = 1163
                    + 12 per declared member
                    + that member's OWN data bytes
                    + 24 per 32-bit word the declared BOOLs occupy, counting
                      EnableIn/EnableOut as two further bits
                    + the members' names, pooled with one byte per name and
                      rounded up to 8
                    + name_length_bytes(the AOI's own type name)

then checked against a purpose-built instrument: **124 captured def-only files**
-- an AOI definition with no instance tag anywhere and no internal rungs, so the
definition is the only AOI cost in the file -- spanning 1 to 128 declared
members, six atomic types, BOOL fractions 0 to 100%, and Input, Output and
LocalTag usages. **70 land exactly, 122 of 124 within ±8, worst 11.**

This supersedes `per_declared_item`, `per_type_rate`, the linear member-name
rate and the whole `aoi_member_type_extra` table. Each of those fitted its own
sweep exactly and was still the wrong shape, and the itemised form says what
each was really measuring -- see OQ-AOIDEFSHAPE and `memory_model.yaml
aoi_definition`. The mixed-versus-single-type split went with them: per-type
rates "did not compose additively once BOOL sat alongside another type" because
the name-pool error was showing up as a composition effect.

Measured effect, live-recomputed over every valid capture:

| | before | after |
|---|---:|---:|
| corpus rows landing exactly | 1,120 | **1,198** |
| corpus rows inside ±8 | 1,690 | **1,907** |
| `aoi_array_packing` within 1% | 35 of 283 inside ±8 | **283/283** |
| `aoi` within 1% | 115 of 160 inside ±8 | **160/160** |
| `axis` / `driveaxis` / `aoi_reqvis` within 1% | 23/61, 1/15, 3/9 | **61/61, 15/15, 9/9** |
| real programs, mean abs error | 2.16% | **2.13%** |
| `griffin_stackerline` | 394 bytes out | **94 bytes out** |

The real-file residual also went one-sided: 14 of 16 now under-predict, where it
used to be split between over and under. That is the shape OQ-REALUNDER's
category differencing can attack; a two-sided residual could not be.

**What is left is one 8-byte term**, exactly 0 on 70 instrument files and
exactly +8 on 35, confounded three ways between the type-name bucket boundary,
a fixed offset inside the name pool, and member order. Filed as
**OQ-AOIDEFSHAPE** with 54 files built to break the confound
(`gen_aoidefshape_closeout.py`) -- not fitted, because fitting a three-variable
confound is how this cost acquired four separate terms in the first place.


## Segment 5 — `addit_*`, OQ-COMPOSITESCALE: CLOSED

33 files, all captured, zero build errors. The question was whether formulas each
fitted by scaling ONE thing at a time stay correct when a real project mixes
categories, and whether an INTERACTION explains the composite sign-flip.

**There is no interaction. 24 of 24 residuals are exactly zero.** The grid builds
a 3x3 (none / mid / high) for each of the six pairs from D = UDT-typed tags,
L = rungs, A = AOI instances, M = 1756-IB16 modules, with everything unnamed held
at zero, so additivity is a subtraction rather than a fit:

    residual(a,b) = cost(a,b) - cost(a,0) - cost(0,b) + cost(0,0)

Six pairs at four level combinations each, measured interaction EXACTLY equal to
predicted in every cell. The composite sign-flip is therefore not an interaction,
and every remaining error is in the four marginal costs — which this grid then
measures exactly, because the all-zero corner is exact at 18,392 both ways.

| axis | engine | real | error |
|---|---:|---:|---|
| D, one UDT tag (40-byte UDT) | 135 | 128 | −7.000/tag over 360 tags |
| L, one `XIC MOV ADD OTE` rung | 96 | 72 | −24.000/rung over 3,600 rungs |
| A, one AOI instance + one 2-param call | 272 | 256 | −16.000/unit over 180 units |
| M, one 1756-IB16 | 1,712 | 1,704 / 904 | −808 after the first |

**Two wired.** The A axis resolves against `dscale2`, which measured the same
thing with 3 parameters instead of 2: the call site is `120 + 16 per parameter`,
two independent generators, both exact — superseding segment 3's flat 168, which
was one point on a line. The D axis resolves against `dscale2_udt`, exact on a
9-byte UDT over 500 tags where this is 7 high on a 40-byte one: pad the
standalone tag's data slot to 8, `udt_tag_extra` −4.

| | before | after |
|---|---:|---:|
| corpus mean abs error | 1.853% | **1.833%** |
| corpus rows within 1% | 2,661 | **2,667** |
| real programs, mean abs error | 2.133% | **2.073%** |
| real programs within 1% | 3 of 16 | **4 of 16** |

**Two measured, exact, and rejected by the real programs** — recorded with files
built rather than fitted. The L axis's 12-per-extra-series-output is confirmed
independently by `UID()UIE();` at a different count and takes the real files from
2.07% to 2.90%, every one worse (OQ-SERIESOUTPUT, 16 files). The M axis's 808
repeat discount stays gated off (OQ-MODULEMARGINAL), now with the constant
measured on a file containing nothing but modules.

**The pattern is itself the result.** On isolated synthetic files the engine
consistently OVER-charges; on real programs it UNDER-charges by 2%. Those are not
one error with two signs. Something present in real programs and absent from
every isolated file is unpriced, and it is larger than all four of these
corrections put together — and the additivity result narrows OQ-REALUNDER
usefully: whatever it is, it is not an interaction between these categories.


## Segment 6 — `stx_*`, OQ-STEXPR: CLOSED

30 files, all captured, zero build errors. The expression-cost thread is closed
and in `docs/RESOLVED_QUESTIONS.md`; four narrower assumptions carry forward under
the same identifier with 21 files built.

**One law replaces a five-entry table** whose confidence was literally
MEASURED_SPARSE and whose fallback over-predicted a one-operator assignment
threefold:

    per_statement = base(n_operators, destination type)
                  + each operator's own CPT tier premium above tier 1
                  + 48 per INTEGER-typed NAMED source read into a REAL destination

| operators | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DINT dest | 36 | 40 | 148 | 172 | 196 | 220 | 244 | 292 | 340 | 388 |
| REAL dest | 60 | 56 | 204 | 244 | 284 | 324 | 364 | 444 | 524 | 604 |

Both rows step once at two operators and are dead linear after, exact at all eight
higher counts. **All three of the old table's non-trivial entries come back from
the law** — 152, 164 and 452 — which is what says it was mis-parameterised rather
than incomplete: each had been measured on a different expression and then keyed on
operator count alone.

**The operator premium is the CPT tier table, unchanged.** `stx_opkind_*` holds the
count at four: `+`/`AND`/`XOR` all read 196, `*`/`/`/`MOD` all read 260. 16 each,
which is exactly that table's tier-1-to-tier-2 step. AND and XOR are now measured
at tier 1, which it did not cover at all.

**An AOI called from ST cost nothing, and costs `120 + 16 per parameter`** — the
same two constants as a call from a rung, same mixed-case invisibility as segment
3. A first pass fitted `136 + 16p` by trusting the filename's parameter count; it
fit all four points just as exactly and was wrong, which is on the record in
`memory_model.yaml` as a warning about two constants against four collinear points.

42 of the 48 ST corpus rows now land exactly. Corpus mean absolute error
**1.833% → 1.545%**.

**The honest headline: this moved the sixteen real programs by nothing**
(2.073% → 2.074%). The figure that sized the call-statement arm — "2,094 real ST
call statements, the single largest shape" — was wrong. The held-out set has 26 ST
routines, 3,994 lines, 2,499 assignments and **zero** AOI call statements; all 91
files in `samples/local` have 307 / 24,745 / 8,099 / 82, and 690 of the 758 bare
call statements there are built-in instructions the RLL table already priced. The
parser finds every ST routine the raw XML holds, so this is not a detection gap —
the claim was simply never checked before it was used to size a batch. Corrected in
the generator docstring.


## Segment 7 — `genem_*`, OQ-MODULESTRUCTURAL: ETHERNET-MODULE CLOSED

27 files, 24 captured, 3 failed conversion. Two of the four arms are solved
exactly; the other two measured nothing and have been rebuilt.

**The connection law.** ETHERNET-MODULE is 109 of the 438 non-CPU modules in the
sixteen real programs, 25% of them, and had no per-catalog entry at all. A
connection's data costs **4x its declared bytes**:

    W = ceil(input_bytes / 4) + ceil(output_bytes / 4)
    connection_bytes = 16 * W - 8 * (W % 2)

Exact on all 14 points from W=2 to W=114, with the catalog overhead at 1,592.
**The two directions are interchangeable** — `genem_in032`/`genem_out032` are
byte-identical captures and so are `genem_in064`/`genem_out064` — which no real
instance could show, because real devices vary both at once. The repeat discount
is 710 (first instance 2,056, every one after 1,376, exact at all four counts),
recorded as the 17th catalog and inert while the gate is off.

| | before | after |
|---|---:|---:|
| `genem_*` rows landing exactly | 0 of 24 | **20 of 24** |
| corpus mean abs error | 1.545% | **1.536%** |
| real programs, mean abs error | 2.074% | **2.025%** |

**Two arms measured nothing, same root cause: a composed rather than
transplanted shape.** The generator hardcoded `CommMethod="536870915"` for every
variant, and CommMethod encodes the comm format. Across 183 real instances:
536870915↔INT (109), 536870916↔SINT (57), 536870932↔no connection (11),
536870913↔DINT (4), 536870914↔REAL (2).

- Arm E's three SINT files **failed import**. The DINT and REAL files imported
  and captured *byte-identical to the INT file* — Studio resolved the
  contradiction from CommMethod and built all three as INT connections. I read
  that as "cost follows byte count, not element count" before checking. It is
  not evidence of anything: all three files were the same connection. That
  question stays open.
- Arm D's `genem_noconn` used the connected method with the size attributes
  removed; all 11 real no-connection instances use 536870932. Its +3,976 reading
  measures an inconsistent CommMethod, not a no-connection module.

Generator corrected, six files rebuilt, and the three captures whose content
changed had their capture columns voided rather than carried against a file they
no longer describe. The lesson is the one already in the project's rules and it
cost a whole arm anyway: **transplant, never compose** — and a file that converts
cleanly is not evidence that the shape is right.


## Segment 8 — `ntag_*`, OQ-VERIFINSTR: CLOSED

25 files, all captured, zero build errors, **no engine change needed** — which is
the result, not an absence of one.

**The four zero-operand instructions are exact at every count.** MCR, TND, UID
and UIE each land at zero residual at 10, 50, 100, 1,000 and 5,000 rungs — 20 of
20 rows. Those weights are confirmed across three orders of magnitude and the
zero-operand half of OQ-VERIFINSTR is closed.

**The other five rows are the PAIRED shape, and they sharpen OQ-SERIESOUTPUT more
than a new batch would have.** The law is now measured on three independently
generated shapes at three output counts, all exact:

| shape | outputs | per rung |
|---|---:|---:|
| `UID()UIE();` | 2 | **−12** at n = 1, 10, 100, 1,000 |
| `XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);` | 3 | **−24** at n = 400, 4,000 |
| `UID()XIC(B0)OTE(B1)MOV(D0,D1)UIE();` | 4 | **−36** at n = 100 |

−12 × (outputs − 1), nothing fitted.

**And `ntag_uidpair_n00001` kills the candidate I thought most likely.** It is a
ONE-RUNG file and it pays the full −12. There is no repetition in a one-rung
file, so the discount cannot be deduplication or amortisation of an identical
repeated rung. The `withbody` rung also weakens the type-distinctness candidate:
its four outputs are four different instructions and it pays the same 12 each as
`UID()UIE();`'s two.

So the discount needs no repetition, ignores instruction type, exempts parallel
branches, is exact at three output counts — and the sixteen real programs still
reject it (2.07% → 2.90%). Taken with OQ-REALUNDER's finding that real logic is
9–22% SHORT, the coherent reading is that **the discount is real and universal
and a larger unpriced positive term in real ladder swamps it** — one missing term
explaining both, rather than two opposite-signed errors in one category. That
makes `strip_ladder.py`'s L2 rung the decisive measurement for this entry too.

Nothing wired, nothing generated. Four constants confirmed, one candidate
eliminated, and the two open logic questions joined into one.


## Segments 10 and 11 — `udtmn2_*` and `udtmn_*`, OQ-UDTMEMBERNAME: CLOSED

47 files between them, all captured, zero build errors. Worked together because
they own the same question and **neither one alone could settle it**.

A UDT definition charged NOTHING for its members' own names. They cost the same
8-aligned pool as an AOI definition's member names — the same thing in the same
file format, so one law now serves both:

    member_name_pool = 8 * ceil(sum(len(name) + 1) / 8)

**Segment 11's length arm is what discriminated the form.**
`udtmn_bool_len{02,04,07,08,12,16,24,32}_b04` varies only the name length across
eight values, and its increments are +8 +8 +8 +16 +16 +32 +32 — exactly the
pool's. A raw 1-byte-per-character rate fits five of the seven and misses 04→07
and 07→08. **Nothing in segment 10 could have made that call**: every name length
in `udtmn2_*` lands on the same residue mod 8, so both forms fit it identically.
Segment 10 supplied what segment 11 could not — the tag-count control
(`_t{01,05,25}` flat at every length, so the cost is per definition, not per
instance), a second and third member count, and the AOI control that was already
correct.

| | before | after |
|---|---:|---:|
| `udt` category within 1% | — | **108 of 108** (mean 0.148%) |
| real programs, mean abs error | 2.025% | **1.605%** |
| real programs, sum-weighted | +2.145% | **+1.245%** |
| worst real file | +4.22% | **+3.28%** |
| corpus mean abs error | 1.536% | 1.544% |

Largest single real-file gain of the day: real UDT member names average about 12
characters and a real program carries 174 UDT definitions. The real residual also
went two-sided again — five programs now over-predict, and `pukall_gang` is
−0.06%.

**What is left is deliberately not fitted.** Every family now collapses to a
per-shape constant, and `−(4m − 8r + 16)` fits five of seven — which would mean
changing `per_member` 16→12, `bool_run_bonus` 32→40 and adding a −16, three
constants on five points, in the one family where member count and hidden backing
SINTs cannot be separated. That is the move that gave the AOI definition four
overlapping terms. It needs a member-count sweep with no BOOL members; the corpus
has exactly one such point.


## Segment 12 — `cpttier_*`, OQ-CMPCPTLAYOUT: CLOSED

22 files, all captured. Reviewed alongside segments 18 (`cmpfl_*`) and 19
(`cptpow_*`), which own the same question, because the three only make sense read
together.

**`per_extra_same_tier_operand` was only ever a TIER-1 rate.** Its 24 came from
`cptcx_operandcount_n01..n10`, which uses the same ADD operator throughout, and it
was applied to every uniform-tier expression. The same pattern as five other
constants this batch has corrected: measured on one arm, applied to all.

| MUL/DIV/MOD operators | engine (24) | real | under-charge |
|---:|---:|---:|---:|
| 1 | 140 | 140 | 0 |
| 3 | 188 | 220 | **+32** |
| 4 | 212 | 260 | **+48** |

16 per operator beyond the first, and a single tier-2 operator is already exact,
which pins the intercept: the tier-2 rate is 24 + 16 = **40**. Exact at both
counts and both rung counts.

| | before | after |
|---|---:|---:|
| `cpttier_*` exact | 10 of 22 | **14 of 22** |
| `cpttier_*` within ±8 | 14 | **18** |
| corpus mean abs error | 1.544% | 1.538% |
| real programs, mean abs error | 1.605% | 1.601% |

**Tier 3 is deliberately left on the tier-1 fallback**, and segment 19 is why:
`cptpow_p2` reads −16/rung and `cptpow_p3` −12/rung while `cptpow_p2_adjacent`
reads **+24/rung** — the same two `**` operators, differing only in adjacency. Two
shapes at one operator count 40 bytes apart means adjacency of `**` is its own
unmodelled term, and any uniform tier-3 rate would fit one and break the other.
`cptpow_p1`, `p1_t1x1` and `p1_t2x1` are exact, so one `**` alone or mixed with one
other tier is already right.

**What is left in the two-tier mix is ±4 and below the band.** The only non-exact
rows sit at exactly +4/rung: the two non-nested mixes with tier-1 count exactly 2,
plus one nested shape whose twin is 0 and one whose twin is also +4. As a
tier-1-count effect that is 2 of 5 shapes; as a nesting effect 1 of 2. Four bytes,
two shapes each way — recorded, not fitted.

**Segment 18 is not derivable from what exists.** All 13 `cmpfl_*` rows are
single-rung files, so each is one point with no slope: 0, 0, +8, +16, +16, +32,
+32, +48, +52, +52, +92, +108, +116. Thirteen isolated points cannot separate
operand type from operator tier from literal count, which is exactly what this
entry already says needs dedicated architecture rather than more raw points.


## Segment 14 — `asmclose_*`, OQ-MODULEIO: WIRED

The repeat-instance module discount was measured exactly on 2026-09-12 and then
gated off, because applying it made all sixteen held-out real programs worse.
The recorded reason was a hypothesis — that whatever gets shared is shared per
rack rather than per project — and the recorded discriminator was the
`modmarg_*` batch. Both have now been measured, and neither the hypothesis nor
the blanket conclusion survives.

### The discount is per catalog, not per file

`modmarg_mixq{1,2,3}_{x1,x2,x2rev}` were built for exactly this and are
captured. Three disjoint quadruples of catalogs with well-separated discounts,
each at one and two copies per catalog, plus a reversed-order build:

| quadruple | sum(d) | over-prediction at x2 | x2rev | at x1 |
|---|---:|---:|---:|---:|
| mixq1 | 2,744 | 2,834 | 2,834 | 33 |
| mixq2 | 7,472 | 7,424 | 7,424 | −32 |
| mixq3 | 7,080 | 7,048 | 7,048 | 24 |

Three independent arms, same answer:

1. `x2rev` is byte-identical to `x2` in all three. Per-file requires the total
   to move by `d_first − d_last`, which is 1,224 / 3,704 / 3,312 here.
2. `x1` sits at ~0 against a per-file prediction of `sum(d) − d_first`, i.e.
   1,224 to 6,944 bytes.
3. `x2` equals `sum(d)` to within 90 bytes, on five-module files whose own
   baseline residual is already ~30.

Per-catalog is what the engine already did, so no code changed — but it was an
assumption until now.

### Flat through n=8

`asmclose_*_n08` was the first point that could falsify `d × (n − 1)`, since
n=1 and n=2 define it. It does not: the marginal is flat at every one of
n=1/2/4/8 on 13 catalog families, and with the discount applied **64 of the 71
`asmclose_*` rows land byte-exact, against 16 without it.**

### Per-rack versus per-project: implemented, measured, irrelevant

`ModuleOverheadModel.repeat_scope` (`project | parent`) now implements both.
They produce **byte-identical totals on all sixteen real programs.** Not luck:
in every one of the sixteen, no catalog carrying a measured repeat rate ever
appears under more than one parent module. Exactly one export in
`samples/local/` splits one at all (`BAI10048_TrimmerTally`, a 1756-IB32/B
across two parents) and it is not in the held-out sixteen.

So the scope question is genuinely undecided — nothing in the corpus
discriminates, because every copy in every captured sweep sits under `Local` —
and it cannot be what made the real files worse. Kept as a model field, default
`project`, because it is a real unresolved behaviour rather than a formatting
detail.

### What the regression actually was

Attributing the project-wide reduction on the sixteen real programs catalog by
catalog — which had never been done — puts 95% of it in two families:

| catalog | repeats | bytes removed |
|---|---:|---:|
| ETHERNET-MODULE | 95 | 67,450 |
| 2198-*-ERS3 (six) | 114 | 112,176 |
| the other ten | 7 | 9,944 |
| **total** | **216** | **189,570** |

| variant | mean \|%\| | sum-weighted |
|---|---:|---:|
| discount off | 1.6009 | +1.2370% |
| all 17 catalogs | 1.7492 | +1.6298% |
| without ETHERNET-MODULE and 2198-*-ERS3 | 1.6289 | +1.2579% |

The ten ordinary I/O and adapter catalogs are neutral on real files to within
noise — 10,464 bytes across 47.4 MB — while fixing 47 corpus rows. Both
exclusions are on shape grounds, decided from the shapes rather than from which
way they moved the number:

- **ETHERNET-MODULE is not a catalog.** It is a placeholder whose cost is driven
  by connection sizes typed in by hand; 109 instances across the sixteen real
  programs carry 40 distinct connection shapes, which is why
  `module_connection_data` exists. The `genem_n{01,02,04,08}` sweep cloned ONE
  shape, so its 710-byte rate is the cost of a second identical clone.
- **2198-*-ERS3 was measured on bare drives with no axis tag,** which no real
  program contains — a drive with nothing pointed at it does nothing. Arm C
  exists to fix that and all six of its rows captured with Studio build errors,
  so the with-axis rate is still unmeasured.

### Seven rows in this segment are bad reads

- `asmclose_1756_ob32_rackaliased_n02` / `_n04` — duplicate module names. The
  copier renamed only the first element of a 2-deep chain, so Studio merged the
  copies and the files measured N adapters sharing ONE output card at zero
  import errors. **The 2026-09-11 note saying these were cleared was written but
  the values were never removed**, so both rows kept feeding every
  reconciliation for two days. Emptied now.
  `lint.duplicate_module_name` has caught this class since 2026-09-11, one day
  after these files were generated, and
  `gen_assumed_closeout._place_copies` now renames every `<Module>` in a block
  and repoints each internal `ParentModule` while leaving references outside the
  block alone. `modmarg_ob32chain_*` is the correctly-built replacement.
- `asmclose_al1222_1conn_n{01,02,04,08}` — **18,128 at all four counts**,
  distinct names, zero errors. A module cannot cost the same at n=8 as at n=1,
  so the AL1222 modules never reached the controller. Left in place because the
  observation is consistent and reproduced four times, but nothing may be
  derived from them. This also **voids the "AL1222 discount = 0 is the control"
  claim** that OQ-MODULEMARGINAL rested the per-catalog reading on: a catalog
  contributing nothing has a zero discount trivially.
- `asmclose_1756_ob32_rackaliased_n01` is fine and is the pair's only clean
  point, at 88 bytes over.

### Still open out of this segment

- **1756-EN2T and rack-aliased 1756-OB32 do not separate.** Arm D
  (`modmarg_ob32chain_*`) gives 21,760 / 24,080 / 28,720 / 38,000 — a flat
  2,320 per additional chain against a modelled 3,544, so a 1,224 discount per
  chain, exact at three counts. One equation, two unknowns. The missing file is
  an **EN2T-only count sweep** (n=1/2/4/8, every copy under `Local`, no
  downstream child); differenced against Arm D it gives EN2T's own rate and
  leaves OB32 by subtraction.
- **1756-EN2T's first-instance rate is also wrong, in both directions.**
  `modulesweep_1756_en2t_variant_1conn` is 1,248 over and `..._noconn` 1,872
  over, while `..._1conn2` is 908 under. A single per-catalog constant is the
  wrong shape for it, for the same reason it was the wrong shape for
  ETHERNET-MODULE: the cost tracks the connection configuration. Same EN2T-only
  sweep answers this.
- **A 16-byte disagreement on 1756-IB16.** The additivity M axis gives 1,704
  first / 904 after; `asmclose_1756_ib16_1conn_n*` gives 1,684 / 892, which is
  what is wired. Both are byte-exact on their own zero points, so the two file
  shapes differ by 8 outside the module term. Flagged, not chased.

### Effect

| | before | after |
|---|---:|---:|
| real programs, mean \|%\| | 1.6009 | 1.6289 |
| real programs, sum-weighted | +1.2370% | +1.2579% |
| corpus rows byte-exact | 1,190 | 1,220 |
| corpus rows within ±8 | 1,870 | 1,900 |
| corpus mean \|%\| | 1.5383 | 1.2757 |
| `modules` category, mean \|%\| | 7.591 | 5.642 |

The real-file headline moves the wrong way by 0.028pp and that is the honest
cost of the change: five of the sixteen move at all, and the shift is 1/57th of
a systematic error the model already carries. What it buys is that the module
term is no longer knowingly wrong where it was measured, and that the real
under-prediction OQ-REALUNDER has to close is now sized at +1.2579% with the
clean catalogs in, nearer +1.63% once the two suspect families are resolved.
