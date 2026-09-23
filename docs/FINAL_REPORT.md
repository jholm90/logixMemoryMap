# Final Report

The closing review of the L5X Memory Analyzer: what it does, how well, what was won,
what was lost, what is still open, and how to get more accuracy out of it.

Everything here is measured on real production exports, not on the generated corpus.
Real exports are referred to by number (`export NN`) or, for the six that have no
controller reading yet, by `blind_NN`. The mapping to real file names never leaves
the gitignored `samples/local/`.

---

## 1. Summary

**What it is.** A WinDirStat for Logix controller memory. It parses an L5X export,
prices every tag, UDT, AOI, module, alarm condition and routine against the
controller's memory budget, and draws the result as a drillable treemap, so a user
can find the array, UDT or routine that is about to cause "memory full" before a
download fails.

**How accurate it is.**

| measure | value |
|---|---|
| Mean absolute error, seventeen real programs | **1.60%** |
| Worst case | **3.63%** — read it as "up to 4%" |
| Weighted bias | **+1.49% under-prediction** (ten under, seven over) |
| The one blind test on record | **+2.15%** low, predicted before its reading was used |
| Re-verified in the final review | twelve of the seventeen, every one within 0.01 pp of its recorded figure |
| Stopping rule (mean < 1% and max < 2%) | **not met**, and shown unreachable by correcting constants |

**How confident it is.** Across all eighteen real exports now available, the
byte-weighted confidence is **92.0% – 98.2% per file, mean 96.7%**, with 84.5% –
96.5% of each program's bytes in the Exact or Measured bands.

**What the final review changed.** Per-element confidence is hidden unless the URL
carries `?ConfidenceMode=true`; the Errors tab always shows the file-level figure.
AOI definitions and the task/program shell are closed as KNOWN. Three bugs that
made the confidence display wrong were found and fixed — one of them meant compiled
AOI ladder was shown as *exact*, against the project's core rule. Real-program
evaluation now works in any checkout, and six blind predictions are on record.

**What is left.** Capture the six blind programs. Capture the six
`jsr_callerdist_*` files. Then attack the real residual with the method in
section 8, which is the only lever that has not been exhausted.

---

## 2. What the project set out to do, and the constraint it lives under

Rockwell does not publish the compiled memory layout, so two very different
confidence levels exist and the tool must never blur them:

- **Data space is calculable exactly.** Atomic sizes are known, and packing,
  alignment and per-tag overhead are inferable and have been verified against real
  controller readings. Tags, UDTs, AOI definitions, predefined structures, axes,
  alarm conditions and the project baseline are all KNOWN.
- **Compiled logic is not calculable from L5X.** L5X is the human-readable form. Every
  instruction weight is fitted against captured controller readings, and every
  logic number is drawn with a dashed "estimated" outline in the UI.

The method is iterative and empirical: build a generated file that isolates one
thing, have Studio compile it, read Capacity, and difference it against its
neighbour. Over the life of the project that produced **3,646 specified samples,
3,611 with a controller reading**.

---

## 3. Results

### 3.1 Accuracy on real programs

Sign convention: positive means the tool predicted too much.

| program | processor | actual | error | re-verified |
|---|---|---:|---:|:---:|
| export 30 | 5069-L330ERM | 3,129,275 | −3.63% | not supplied |
| export 27 | 1756-L81E | 2,255,773 | −3.52% | ✓ |
| export 16 | 1756-L82E | 4,044,994 | −2.50% | ✓ |
| export 06 | 1756-L82E | 5,217,440 | −2.31% | ✓ |
| export 07 | 1756-L83E | 7,891,612 | −2.14% | ✓ (blind) |
| export 25 | 1756-L83ES | 4,634,308 | −2.04% | not supplied |
| export 10 | 1756-L81E | 1,703,932 | +1.79% | ✓ |
| export 09 | 1756-L83E | 7,136,625 | −1.76% | ✓ |
| export 17 | 1756-L81E | 2,281,316 | −1.48% | ✓ |
| export 13 | 5069-L320ERMS3 | 1,074,245 | +1.43% | ✓ |
| export 01 | 1756-L83E | 5,999,972 | −1.20% | ✓ |
| export 18 | 1756-L81E | 923,320 | +1.18% | ✓ |
| export 29 | 5069-L330ERM | 1,362,000 | +1.05% | not supplied |
| export 28 | 1756-L81E | 2,502,336 | +0.56% | ✓ |
| export 08 | 5069-L330ERM | 1,147,896 | +0.24% | not supplied |
| export 26 | 1756-L81E | 1,763,760 | −0.19% | not supplied |
| export 14 | 1756-L81E | 2,362,176 | +0.12% | ✓ |

**Four inside 1%, eleven inside 2%, none beyond 3.63%.** Both platforms in scope are
represented, 1756-L8x and 5069, and the 5069 difference is a single project-level
constant rather than a per-feature one.

### 3.2 Blind predictions

The seventeen are customer exports nobody outside the project can audit, and the
model was tuned while sixteen of them were available. **The blind test is the only
externally meaningful evidence**: export 07 was predicted at 7,722,352 against an
actual of 7,891,612 — 2.15% low — before its reading was used for anything, landing
inside the existing error spread rather than outside it.

Six more real exports arrived in the final review with **no reading on record**.
They are predicted, and the numbers written down, before any reading exists:

| ID | processor | firmware | predicted | expected | range |
|---|---|---|---:|---:|---:|
| blind_01 | 1756-L83E | 32.04 | **9,090,346** | 9,227,338 | 8,930,356 – 9,433,052 |
| blind_02 | 1756-L83E | 35.05 | **7,970,364** | 8,090,477 | 7,830,086 – 8,270,847 |
| blind_03 | 1756-L83E | 33.01 | **7,399,658** | 7,511,171 | 7,269,424 – 7,678,625 |
| blind_04 | 1756-L83E | 32.04 | **6,418,673** | 6,515,402 | 6,305,704 – 6,660,657 |
| blind_05 | 1756-L83E | 35.05 | **5,939,350** | 6,028,856 | 5,834,817 – 6,163,263 |
| blind_06 | 1756-L83E | 35.05 | **3,704,851** | 3,760,683 | 3,639,646 – 3,844,524 |

"Expected" applies the seventeen's +1.49% bias; the range is their spread. `blind_02`
is a later revision of export 07, so it doubles as the project's first
within-program drift test. **Reading Capacity on these six is worth more than any
generated batch that could be built.**

### 3.3 Confidence on real programs

Byte-weighted confidence as the Errors tab shows it, computed by the client and
cross-checked to the decimal against an independent Python mirror.

| program | confidence | Exact + Measured | Unverified |
|---|---:|---:|---:|
| export 07 | 98.2% | 96.5% | 2.8% |
| blind_04 | 98.0% | 96.2% | 3.2% |
| export 01 | 98.0% | 96.3% | 3.5% |
| blind_02 | 98.0% | 96.2% | 3.0% |
| export 09 | 98.0% | 96.3% | 3.2% |
| export 14 | 97.8% | 95.7% | 3.8% |
| export 17 | 97.6% | 95.7% | 3.9% |
| blind_05 | 97.5% | 94.2% | 3.1% |
| blind_03 | 97.0% | 93.7% | 4.6% |
| export 27 | 96.8% | 93.8% | 5.4% |
| export 28 | 96.7% | 92.6% | 4.4% |
| export 16 | 96.6% | 93.4% | 5.7% |
| export 06 | 96.0% | 91.9% | 6.7% |
| blind_06 | 95.8% | 89.5% | 4.8% |
| blind_01 | 95.8% | 89.8% | 5.6% |
| export 10 | 95.7% | 91.5% | 7.4% |
| export 18 | 94.3% | 85.7% | 7.1% |
| export 13 | 92.0% | 84.5% | 14.1% |

**What the Unverified bytes are, on every file:** Subroutine Overhead (the open
JSR caller-base question, 1–6% of a program), program logic containing instructions
no isolation file has tested, and a few module catalogs priced by the flat fallback.
The 5069 safety program (export 13) is the outlier because it is small: its fixed
per-caller subroutine overhead is 5.6% of it, modules on the flat fallback are
another 4.0%, and logic with untested instructions 3.0%. Capturing
`jsr_callerdist_*` alone would lift it by nearly three points.

**Every element laid out individually** — export 07, every tag, member, array
element, axis, definition row, routine and module the tree can reach:

| band | elements | share of elements | share of bytes |
|---|---:|---:|---:|
| 100 Exact | 1,546,693 | 95.2% | 79.9% |
| 98 Measured | 357 | 0.02% | 11.8% |
| 90 Close | 102 | 0.01% | 3.0% |
| 75 Approximate | 50 | < 0.01% | 2.6% |
| 50 Unverified | 25 | < 0.01% | 2.7% |
| no bytes of their own (aliases, empty) | 77,026 | 4.7% | — |

**177 elements out of 1.6 million read below 98%.** The impression of guesswork on
the first screen came from a handful of large aggregate tiles, not from the model —
which is why per-element confidence is now an opt-in analysis view and the
file-level figure is always one click away.

**Confidence is not accuracy.** Across the twelve re-verified programs the file
confidence does not predict the size of the error at all (r = +0.01). It predicts the
*direction* moderately (r = −0.58, n = 12): the programs whose bytes are mostly
exactly-priced data space under-predict, and the ones heavy in logic and AOIs
over-predict. The confidence figure is an honest statement of how well each
*component* is known in isolation. It is not, and cannot be, a forecast of the
whole-program residual. The UI says so.

### 3.4 Coverage

Twelve of the eighteen real exports have **no coverage gap at all**. Across all
eighteen, the engine charges nothing for 2 FBD routines, 1 alarm-definition
routine, 4 SCP, 2 IOT and 1 ALMD — a negligible fraction. **99.72% of real
instruction occurrences carry a weight.**

---

## 4. Wins

**The data-space model is exact.** Tag storage, UDT packing and alignment, AOI
definitions and instances, predefined structures, axes, alarm conditions and the
project baseline all reproduce controller readings to the byte on isolation files
and hold on real programs. That is most of every real program's bytes.

**The instrument is good.** A generator that isolates one variable per file pair, a
Studio pipeline that captures Capacity unattended, and roughly 1,500 captured rows
that predict exactly. It is the reason every constant in `memory_model.yaml` has a
derivation behind it rather than a guess.

**The process tooling enforces its own lessons.** Each of these exists because its
failure happened first:

| tool | stops |
|---|---|
| `sample_gen/lint.py` | a file that converts but will not build — now including AOI call arity |
| `scripts/confound_check.py` | a batch that moves two things at once and measures their sum |
| `scripts/capture_errors.py` | a capture with build errors silently used, or silently dropped |
| `scripts/quick_eval.py` | an accuracy claim made on the wrong files; prints the stopping rule every run |
| `tests/test_measured_known_constants.py` | a measured constant drifting away from its evidence |
| split `manifest.csv` / `captures.csv` | two machines rewriting one file and conflicting on every pull |

**The UI is usable by someone who has never seen the code.** A drillable treemap
with nested depth, a list view with filters, a type summary, cross-reference, rung
view, CSV/XLSX export, a cached load so browsing is instant, and now a file-level
confidence figure that sums to the file.

**Honest bookkeeping.** Seven open questions, down from forty; closed ones carry their
reasoning, including the fits that were exact and wrong. The stopping rule and the
proof that constant-tweaking cannot meet it are written down, so nobody spends a
month re-deriving either.

**In the final review specifically:**

- `?ConfidenceMode=true` URL switch; per-element confidence hidden by default. The
  estimated outline on compiled logic stays in every mode.
- File-level confidence on the Errors tab, always shown, summing to the file total.
- AOI definition cost closed as **KNOWN**: an 8-byte total alignment took the
  AOI-bearing captures from 38 exact to **201**, with no non-AOI capture moving.
- AOI internal ladder split out of the definition: correct tier, correct tree,
  measured confidence. Totals byte-identical on every real program present.
- Task/program shell closed as **KNOWN** on evidence already in the corpus.
- The fifteen real-shape AOI captures reconciled for the first time: the
  per-definition cost holds at real scale, the axis-parameter charge is right, and
  the AOI population is refuted as the cause of the AOI-dense programs' error.
- Literal operands closed on real exposure; the queue's first item was worth 1,756
  bytes across eighteen programs.
- Real-program evaluation works in any checkout; six blind predictions on record.
- Real customer file names removed from the committed manifest.

---

## 5. Losses and mistakes

Stated plainly, because every rule in `CLAUDE.md` was paid for by one of these.

**A complete customer program was pushed to the public repository.** Strip-ladder
variants were unpacked into `samples/generated/` and swept up by the capture
tooling's auto-push. History was purged and force-pushed, which does not undo a
disclosure. **Real file names are still in the repository's history** — removed from
the working tree in the final review, but recoverable with `git log -p`. That is the
most serious loss of the project and the only one that cannot be fixed by more work.

**Fits that were exact and wrong.** A definition-cost form that fitted 18 of 18
points to zero residual and was reverted the same session. Four separate AOI
definition terms that each fitted their own sweep exactly and together were the wrong
shape. A per-BOOL law exact at nine points that was a mod-8 artifact. A correction
that looked right and moved 787 exact captures to wrong. These are why
cross-validation decides every fit.

**Compensating errors hid real ones.** Removing a wrong over-charge unmasked a
systematic under-prediction on every real program.

**Days spent below the noise floor.** Produced and consumed tags were measured
precisely at 0.11% and 0.06% of real tags; literal operands were ranked first on an
exposure that turned out to be worth 1,756 bytes across eighteen programs. The
floor rule now applies before building, not after capturing.

**Captures used without checking their build.** A 31-file family sat at +10.5% for
days because every file carried build errors nobody had recorded. A
1,000-rung literal batch failed on every rung because the documented AOI call rule
was backwards, and the lint rule enforcing it was backwards too.

**Work paid for and never read.** The fifteen real-shape AOI captures sat unreconciled
until the final review. The AOI-definition instrument drifted by 4 bytes on 74 files
after some shared change, and nobody re-ran its census.

**The 1% target.** It was set before anyone knew whether it was reachable. The
per-category ceiling shows it is not reachable by correcting constants, and nothing
has yet shown it is reachable at all.

**Found and fixed in the final review** — each existed before it and each distorted
what a user saw:

| defect | effect |
|---|---|
| AOI internal ladder folded into the definition entry | compiled logic shown as exact, drawn as an unexplained ~6% lump, stuck at 50% confidence |
| UDT definition nodes carried their instance's tier mix | a 4 KB definition weighed as a 30 KB instance; group and file figures skewed |
| AOI rungs keyed under the wrong path | AOI ladder never received its rungs' measured confidence |
| `quick_eval.py` needed exact paths | found one real program of seventeen in a fresh checkout |
| `classify_path` ignored AOI context | a dragged-along AOI's routines counted as the exported thing |
| Errors tab inserted file text unescaped | tag and routine names from the L5X rendered as HTML |
| AOI call-arity lint rule allowed a range | passed a batch that failed on 1,000 of 1,000 rungs |
| JSR base constant charged to the JSR instruction | a measured-exact instruction displayed as ±5% |

---

## 6. What is open

### Open questions — seven

| question | what it needs |
|---|---|
| **OQ-JSRCALLERBASE** | capture `jsr_callerdist_*`; per-file versus per-caller differs by up to ~300 KB on a real program |
| **OQ-REALUNDER** | the real residual itself; see section 8 |
| **OQ-RUNGSHAPE** | a per-rung term confounded with every instruction weight; a packing sweep with a non-output instruction |
| **OQ-ALARMCONDREAL** | alarm conditions land 0.16% on one real program and 8.8% short on the other |
| **OQ-EXPORTSCOPE** | what a partial export really costs on import — a correctness requirement |
| **OQ-BUILDFAIL-OPEN** | the defect log of files that do not build |
| **OQ-MODULENAMELEN** | a module's name length costs bytes the engine charges at zero |

### Captures waiting

| what | rows | priority |
|---|---:|---|
| the six blind programs — read Capacity | 6 | **first** |
| `jsr_callerdist_*` | 6 | **second** |
| the five recorded programs missing from this checkout | 5 | drop into `samples/local/` |
| `composite_realistic_*_r2` | 9 | eight need lint findings cleared |
| `fwmatrix_*`, `alarmcond_*`, `cipmodule_*` | 13 | first submission |
| `predefprobe_*` | 3 | needs the Studio error line |
| `litop_bool_*` | 4 | optional — below the floor |

### Smaller items recorded, deliberately not worked

- **Task names round up, the identifier term rounds down** (OQ-TASKNAMEROUND). Under
  8 bytes a task. Whether program and routine names do the same at lengths that are not
  multiples of 8 has never been tested.
- **Real-shape AOIs are 1.8 bytes per member high** (OQ-AOIREALSHAPE). About 0.1% of the
  most AOI-dense program.
- **The AOI definition's remaining +8** on 47 of 125 isolation files — exactly the
  noise floor.
- **A "Type name length" row can be −8** in the AOI definition drill, a real negative
  term the treemap cannot draw. Cosmetic.

### Decisions only the owner can make

- **Whether to rewrite the repository's history** to remove the real file names that
  are still in it. A history rewrite plus a fresh clone is the only remedy, and it does
  not reach copies already made.
- **Whether `CLAUDE.md`'s ground-truth wording should name its two exceptions** — a
  0-parameter JSR reads Exact, and per-element confidence is hidden by default. Both
  are implemented and documented in `MEMORY_MODEL.md`; the rule text itself still
  says "every".

---

## 7. What can be improved beyond accuracy

**Make the tool safe for a stranger's program.** Everything that is not covered is
charged zero and listed on the Errors tab, which is right. What is missing is a
visible warning when a program leans on something the model has never seen — a new
module catalog, an unmeasured instruction, a structure outside the synthetic range.
The structural module model (queue item 6) is the largest part of this.

**Keep one implementation of the confidence walk.** The final review found the client,
the server and the census each computing confidence with subtly different rules, and
two of the three defects above lived in the gaps. The client is now the reference and
the census mirrors it rule for rule; a single server-side computation shipped with
the report would remove the duplication entirely.

**Delete the dead weight.** The dead-architecture captures (1756-L7x, 1769) are kept
at no cost, but they still dominate every corpus-wide average and have to be
filtered out by hand in every report. Moving them to their own manifest would stop
that.

**Put the blind-prediction procedure in the tool.** Today it is a discipline written in
three documents. A `predict --blind` command that writes the prediction and a hash of
the file to a local ledger, and a reconcile step that refuses to accept a reading for
a file it has no prior prediction for, would make it impossible to skip.

---

## 8. How to get more accuracy

What is known for certain:

- **Constants are not the problem.** Every isolation file prices its own content to
  within the noise floor. Letting all eight category scales float and fitting them
  directly on the real programs — an upper bound no honest procedure can beat — only
  reaches mean 1.01% / max 2.59%, and under leave-one-out it is worth 0.007 points.
- **The residual is two-sided and does not scale with any count the engine has.**
  Coefficient of variation 1.74 per instruction, 1.73 per rung. Data-heavy programs
  under-predict and logic-heavy ones over-predict (section 3.3).
- **Real programs sit 16–54× outside the synthetic range** on JSR-target and AOI
  content, so a law fitted on the synthetic range is being extrapolated on every real
  file.
- **Eliminated:** global logic scaling, per-instruction constants, branch fraction,
  any flat per-file/per-routine/per-program/per-tag term, the empty-project baseline,
  axis sizing, tag order, branch arrangement, 2-D subscripts, literal operands, the
  AOI population, documentation (tag, UDT, AOI descriptions; rung and ST comments),
  and produced/consumed tags.

So the missing bytes are an **interaction that only exists at real scale**, not a
wrong constant. Three ways to find it, in order of value:

**1. Attribute the residual on real programs with Studio-made deletions.** This is the
technique that produced the project's most valuable single measurement: edit a real
project in Logix Designer, let Studio compile it, read Capacity twice. Rewriting
exported XML is forbidden and does not build; a deletion made in Studio is neither.
On the worst program (export 27, 79 KB missing), read Capacity after deleting, one
at a time and in Studio: all alarm conditions; all AOI definitions and their
instances; all program logic; all module configuration. Each delta compared with the
engine's own predicted delta tells which category holds the missing bytes, *at real
scale, on a real program*. Five or six readings on each of three programs — two
under-predicted, one over-predicted — would localise the residual more than the last
thousand generated files did.

**2. Grow the real set, and never fit on it in-sample.** Seventeen points cannot
support more than one or two fitted terms. The six blind programs take it to
twenty-three; the owner's own archive may hold more. Any residual model built on real
programs — for example, one extra term per feature the engine does not count, such as
distinct tag names, program count or alarm-set count — must be judged by
leave-one-out only, and must beat the 0.007-point result the per-category fit
managed. Most candidates will not, and that is the point of the test.

**3. Close the known structural gaps, which are small but certain.** The JSR caller
base (item 2 in the queue) is worth up to hundreds of kilobytes on a real program in
one direction or zero in the other — the capture decides. The alarm-condition gap is
8.8% of a 19–21% category on one program. The per-rung term is confounded with every
weight. None of these alone reaches 1%, but each removes a known error rather than
fitting around it.

**What will not work,** stated so it is not re-tried: another category scale, another
per-instruction constant, another generated composite, or a larger version of the same
isolation sweep. The isolation instrument is finished; it measures what it was built to
measure, and the remaining error is not in anything it can build.

**A realistic expectation.** With methods 1–3 the worst case can plausibly come in
under 3% and the mean toward 1.2%. A 1% mean with a 2% worst case has not been shown
to be reachable by anything, and should stay an aspiration until the Studio-deletion
attribution shows where the missing bytes are.

---

## 9. Thoughts on the project

**The engineering is sound where it can be.** The data-space model is genuinely exact
and it is most of every program. The isolation method is the right method, and the
discipline around it — one variable per pair, confound gate, lint, capture-error
routing, the KNOWN register — is more rigorous than most commercial tooling. A 1.6%
mean on real programs with no access to the compiled format is a real result, and the
blind test backs it.

**The project's real risk was never accuracy. It was process.** The failures that cost
the most were a customer program pushed to a public repository, captures used
without checking they built, work captured and never read, and constants that drifted
because a census was not re-run. Every one is a bookkeeping failure, and every one
is now guarded by a tool rather than by memory. That is the right response, and it is
the part to keep if the project continues with anyone else.

**The generated corpus has done its job.** Its marginal value is now close to zero: the
last several batches either confirmed what was known or measured something below the
noise floor. The remaining accuracy lives in real programs at real scale, where the
generator cannot reach. Future effort should go to real programs — blind readings and
Studio-made deletions — and not to another generated family.

**The confidence display should be read for what it is.** It says how well each
component is known, and it is high because most of every program is exact data space.
It does not say how close the total is, and on the twelve re-verified programs it has
no relationship to the size of the error. Hiding the per-element view by default is
reasonable for a user who wants the answer rather than the audit; the file-level figure
and the estimated outline keep the essential honesty visible.

**As a tool, it is ready to use** for its purpose: finding what is consuming memory,
comparing revisions, and getting a total to within a few percent before a download.
For a go/no-go decision within the last 4% of a controller's budget, it is not, and the
headline should always carry the worst case with the mean.

---

## 10. Reproducing every number in this report

```
python scripts/quick_eval.py --real-only                    # section 3.1
python scripts/predict_batch.py samples/local/<file>.L5X    # section 3.2
python scripts/confidence_census.py --summary samples/local/*.L5X   # section 3.3
python scripts/confidence_census.py samples/local/<file>.L5X        # element census
python scripts/coverage_audit.py samples/local/*.L5X        # section 3.4
python scripts/capture_errors.py                            # capture-error gate
python -m pytest -q                                         # 449 passed
```

Real exports resolve by file name anywhere under `samples/local/`; a renamed one is
mapped in the gitignored `samples/local/aliases.csv`. The six blind IDs map to files in
the gitignored `samples/local/blind_predictions.csv`.
