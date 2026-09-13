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
| 4 | `aoimix_*` | 34 | 34 | 0 | OQ-AOIBOOLPACK-PAIRING | pending |
| 5 | `addit_*` | 33 | 33 | 0 | OQ-COMPOSITESCALE | pending |
| 6 | `stx_*` | 30 | 30 | 0 | OQ-STEXPR | pending |
| 7 | `genem_*` | 27 | 24 | 0 | OQ-MODULESTRUCTURAL | pending |
| 8 | `ntag_*` | 25 | 25 | 0 | OQ-VERIFINSTR | pending |
| 9 | `identnamelen_*` | 24 | 19 | 5 | OQ-IDENTNAMELEN | pending |
| 10 | `udtmn2_*` | 23 | 23 | 0 | OQ-UDTMEMBERNAME | pending |
| 11 | `udtmn_*` | 24 | 24 | 0 | OQ-UDTMEMBERNAME | pending |
| 12 | `cpttier_*` | 22 | 22 | 0 | OQ-CMPCPTLAYOUT | pending |
| 13 | `modmarg_*` | 19 | 19 | 6 | OQ-MODULEMARGINAL | pending |
| 14 | `asmclose_*` | 71 | 71 | 0 | OQ-MODULEIO | pending |
| 15 | `aoishape_*` | 17 | 17 | 0 | OQ-AOIINTERNALLOGIC | pending |
| 16 | `axmarg_*` | 16 | 16 | 9 | OQ-AXISMARGINAL | pending |
| 17 | `platform_*` | 15 | 10 | 0 | OQ-REAL5069 | pending |
| 18 | `cmpfl_*` | 13 | 13 | 0 | OQ-CMPCPTLAYOUT | pending |
| 19 | `cptpow_*` | 12 | 12 | 0 | OQ-CMPCPTLAYOUT | pending |
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
| 30 | `aoi_logic_scale_*` | 4 | 4 | 3 | OQ-AOIINTERNALLOGIC | pending |
| 31 | `aoi_multiroutine_*` | 2 | 2 | 2 | OQ-AOIINTERNALLOGIC | pending |

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
