# Working a Capture Batch

The method for taking a large batch of captures to a resolution, and the record of
what each sweep family settled.

**The method is the durable part.** The per-family reasoning trails live in
`RESOLVED_QUESTIONS.md` and the constants they produced live in `MEMORY_MODEL.md` —
this file is how the work is organised, not a second copy of the findings.

---

## The method: one segment at a time

A batch of several hundred files is not one problem. **Group it by sweep family,
give each family the open question it was built for, and work one family to a
resolution before starting the next.**

Every segment ends in exactly one of:

| status | meaning |
|---|---|
| **CLOSED** | The question is resolved. Moves to `RESOLVED_QUESTIONS.md`. |
| **WIRED** | The engine changed and the change was verified against the corpus. |
| **DEFERRED** | Has errored rows. Worked at the end, after the clean families. |
| **BLOCKED** | Cannot be resolved by this data, with the reason stated. |

Nothing is left in an unstated state. A family with no verdict is a family that
will be silently skipped next time.

### Per segment

1. **Recompute every row live against the current engine.** Never read a stored
   delta — it goes stale the moment any constant moves, which is exactly how a
   clean, answered measurement hides in plain sight.
2. **Check the error count before reading any residual pattern.** A row that built
   with errors is suspect, and an exact-looking fit on errored rows has already
   produced one wrong wired constant.
3. **Difference within the family**, against the pair or control the family was
   designed around — not against a model.
4. **State the verdict and the count behind it.** "Closed, 54 of 54 clean" is a
   verdict. "Closed" is not.
5. **Re-run the corpus census after wiring anything.** A constant that fixes one
   family can move hundreds of previously-exact rows.

### Order of work

**Clean families first, errored families last.** An errored family needs its build
error root-caused before its numbers mean anything, and that is a different kind of
work from reading a residual. Mixing the two means the diagnosis gets rushed.

**Families answering the same question are worked together.** Several pairs in the
record below only resolved because one family's arm discriminated a form the other
family could not.

---

## What each family settled

The record of one large batch, worked this way. Counts are files, captures and
errored rows.

| segment | files | capt | err | question | outcome |
|---|---:|---:|---:|---|---|
| `aoialgn_*` | 71 | 71 | 0 | AOI instance-array packing | CLOSED — two laws wired |
| `asmclose_*` | 71 | 69 | 0 | Module overhead | WIRED — repeat discount for 10 catalogs |
| `aoilt_*` | 54 | 54 | 0 | AOI definition itemisation | CLOSED — 54/54 clean |
| `dscale2_*` | 39 | 39 | 0 | Definition cost at scale | CLOSED — five laws wired |
| `aoimix_*` | 34 | 34 | 0 | AOI BOOL/atomic mix | CLOSED — definition cost re-derived from scratch |
| `addit_*` | 33 | 33 | 0 | Category additivity | CLOSED — the categories are additive, 24/24 exactly |
| `stx_*` | 30 | 30 | 0 | Structured Text | CLOSED — one law replaces a five-entry table |
| `genem_*` | 27 | 24 | 0 | Generic Ethernet connections | CLOSED for that profile — 2 arms invalid, rebuilt |
| `ntag_*` | 25 | 25 | 0 | Unweighted instructions | CLOSED — 20/20 exact; the other 5 killed a competing candidate |
| `identnamelen_*` | 24 | 19 | 5 | Identifier name cost | CLOSED — the cost is a STEP, not linear; 19/19 exact, was 7/19 |
| `udtmn_*` | 24 | 24 | 0 | UDT member names | CLOSED — its length arm is what discriminated the form |
| `udtmn2_*` | 23 | 23 | 0 | UDT member names | CLOSED — largest single real-file gain of the batch |
| `cpttier_*` | 22 | 22 | 0 | CPT operator tiers | CLOSED — the tier-2 rate had been a tier-1 rate applied universally |
| `modmarg_*` | 19 | 19 | 6 | Module marginal cost | DEFERRED — errored rows |
| `aoishape_*` | 17 | 17 | 0 | AOI internal logic | CLOSED and WIRED — 27/27 exact |
| `axmarg_*` | 16 | 16 | 9 | Axis marginal cost | DEFERRED — errored rows |
| `platform_*` | 15 | 10 | 0 | 5069 versus 1756 | CLOSED — byte-identical at every density |
| `cmpfl_*` | 13 | 13 | 0 | CMP float literals | Reviewed — single-rung points, not derivable |
| `cptpow_*` | 12 | 12 | 0 | CPT power operator | Reviewed — `**` adjacency worth 40; tier 3 left alone deliberately |
| `cptdest_*` | 12 | 12 | 0 | CPT destination type | CLOSED — two type-mismatch costs found, not fitted |
| `alarmbits_*` | 12 | 12 | 0 | Alarm bit backing | CLOSED — flat in tag count |
| `cptpos_*` | 9 | 9 | 0 | CPT operator position | CLOSED — position is free, 7 of 8 byte-identical |
| `pool*` | 9 | 9 | 0 | Shell constants | CLOSED — 9/9 in band, 6 byte-exact |
| `v3abl_*` | 8 | 8 | 0 | Generator-bug ablation | **BLOCKED — the ablation is not single-variable, so it cannot be differenced** |
| `albool_*` | 8 | 8 | 0 | AOI array LocalTags | CLOSED — all rows in band bar one |
| `altype_*` | 6 | 6 | 0 | AOI array LocalTags | CLOSED — MOTION_INSTRUCTION is the one gap |
| `almult_*` | 3 | 3 | 0 | AOI array LocalTags | CLOSED — +8 flat, in band |
| `aldim_*` | 3 | 3 | 0 | AOI array LocalTags | CLOSED — dimension is free |
| `uwclose_*` | 3 | 0 | 0 | Unweighted instructions | Awaiting first capture |
| `aoi_logic_scale_*` | 4 | 4 | 3 | AOI internal logic | DEFERRED — errored rows |
| `aoi_multiroutine_*` | 2 | 2 | 2 | AOI internal logic | DEFERRED — errored rows |

**One blocked segment is worth reading as a lesson rather than a status.** An
ablation batch built to isolate several generator bugs at once **cannot be
differenced, because it is not single-variable** — turning off several things
together measures their sum. That is a design failure, not a capture failure, and
no amount of recapturing fixes it.

---

## The errored-row review

Done once, over every row in the corpus carrying a build error. **The distribution
matters more than the individual rows.**

### Only a handful carried any error text

The capture tooling's error-log reader was added late, so almost every errored row
before that point recorded **a count and nothing else.**

**A count alone is still diagnostic.** In one family the counts were exactly
2, 4, 8, 12 and 20 against drive counts of 2, 4, 8, 12 and 20, and in a parallel
family exactly `n/2 + 1` — which together said the fault was **per drive module**,
not per axis or per file. That identified the cause where the text was missing: a
2198 drive needs its bus supply module **and** that supply's converter axis.

Consequence: four generators fixed, two lint rules added, dozens of rows cleared
for recapture, and **six first-instance module values downgraded from KNOWN to
ASSUMED because they rested on the same broken captures.**

### The largest block of errored rows had never touched a number

Every errored composite row came from a **superseded** generation. Not one came from
the current one, which was clean throughout. And they were never feeding anything:
the validity filter already rejects a row with a non-zero error count, so all of
them sat outside every accuracy figure already.

**What those numbers did blend was a superseded generator:**

| generation | clean rows | mean \|error\| |
|---|---:|---:|
| current | 74 | **1.548%** |
| two generations back | 3 | 1.138% |
| older | 14 | 2.511% |
| all | 91 | 1.683% |

**The honest figure is the current generation's 1.548%.** The older rows at 2.511%
are what pull the blended number to 1.683%. So a reported "this got worse" was real
but was a statement about a metric a quarter of which was superseded.

**This is the general rule:** when a corpus-wide number is dragged down by
superseded or dead-architecture rows, report the figure **excluding** them and say
so. Do not lead with the contaminated number and explain it away afterwards.

### Rows whose error status was never recorded

A few hundred rows were captured before the tooling logged an error count at all,
so a blank there means **unknown**, not clean. A strict mode that excludes them
already existed and is off by default — see `TESTING_PLAN.md` for why counting them
is the right default and where it is not.
