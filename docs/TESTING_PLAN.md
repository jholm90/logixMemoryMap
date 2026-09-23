# Testing and Validation

How a prediction becomes a measured number, and every validity rule that governs
whether a captured row may be used.

**The whole feedback loop runs on this.** Get the procedure right before
generating files against it, or the batch has to be redone.

---

## The procedure

No download and no emulator. **Logix Designer shows memory usage in Controller
Properties as soon as a project successfully compiles offline.**

1. Convert the sample L5X to ACD — `scripts/batch_l5x_to_acd.ps1`, batched.
2. Open in Logix Designer and verify. **A sample that does not compile is not
   valid data.**
3. Read memory used: Controller Properties → Memory tab.
   `scripts/batch_memory_capture.ps1` opens each ACD in turn and captures this so
   the file-hunting and row formatting are not manual, even though the read itself
   always will be.
4. The result lands in `samples/captures.csv`. Predicted-versus-actual is computed
   live, never stored.

**There is no programmatic memory read, online or offline.** GSV has no memory
attribute on any Logix 5000 platform, and Rockwell's documented MSG/CIP path is
explicitly unsupported across the current controller lineup. Controller Properties,
read by eye, is the only method.

Each ACD compile is independent — nothing is downloaded, so there is no shared
physical resource to reset between samples.

> **Worth doing periodically:** spot-check against real hardware with an actual
> download, to confirm the offline compiled figure matches what a running
> controller reports. Assumed identical, not proven.

### What the SDK can and cannot do

Rockwell publishes a Logix Designer SDK (.NET, `RockwellAutomation.LogixDesigner`)
plus the `l5xplode` / `l5xgit` CLI tools built on it.
`l5xgit l5x2acd --l5x <file> --acd <file>` converts headlessly with no UI
interaction, and `batch_l5x_to_acd.ps1` wraps it over a folder. The l5xgit source is
vendored in `tools/ra-logix-designer-vcs-custom-tools` and built by
`scripts/build_l5xgit.ps1`; see `tools/README.md`.

Beyond that the SDK exposes `SaveAsync`, `DownloadAsync`,
`SetCommunicationsPathAsync` and per-type tag get/set once online, and FactoryTalk
Logix Echo can spin up an emulated chassis from an ACD file. **Neither is needed**
now that offline compile is enough.

The one thing that would close the loop with no hardware at all is a scripted
"verify project, read compiled memory stat" call that works offline. **Not yet
researched** — flagged rather than assumed.

---

## Capture validity: the rules that decide whether a row may be used

All of these are enforced by `scripts/accuracy_report.py::is_valid_capture` so
they cannot be forgotten. **Every one of them exists because it already went
wrong.**

### A row that built with errors is never a valid fitting point

`error_count > 0` means the project did not fully compile, so the reading is of an
**incomplete** project. These rows are not merely noisy — they manufacture a
**systematic, directional** false signal, because whatever failed to build is
missing from the actual figure while the engine still predicts it. **That reads
exactly like "we over-predict," and it pulls a fitted constant the wrong way.**

> This cost a real wrong model change. An 18-file axis sweep carried
> `error_count = drives + 1` on every single file, and its residuals were almost
> perfectly linear in drive count — so it looked like an exact "each additional
> drive on a shared DC bus is over-charged" finding, was derived to zero residual
> on 18 of 18 points, and was wired and committed. It was an artifact of the
> drives failing to build. Reverted the same session.

**A clean, exact-looking linear fit is not evidence of validity. Check the error
count first, before believing any residual pattern.**

Such a row is **suspect, not wrong**. Never quietly use one, and **never quietly
drop one either** — both are how a real double-digit error hides for days. Say in
any report which questions are carrying suspect rows and how many.
`scripts/capture_errors.py` enforces that.

### A capture below the empty-project baseline is a bad read

**No Logix project can report using less memory than an empty project on the same
controller.** `is_valid_capture()` rejects anything below
`empty_project_baseline_bytes`, read from the model rather than hardcoded so the
floor tracks it.

> Found in a batch that passed every check the project then had. 24 rows came back
> at 2,976 bytes and 6 more at 6,640, for controllers whose empty baseline is
> 69,600 to 98,944. Every one had zero errors, no warning, blank notes, and a
> window title matching the expected file exactly. Left in, those 30 rows alone
> moved the corpus mean error from **0.68% to 32.17%**.

The floor only stops bad rows reaching a fit. **It does not fix the underlying
tooling bug** — a capacity dialog read before the project finished loading is the
obvious suspect, unconfirmed.

### Window-title mismatch — retried automatically

The capture loop cross-checks the Studio window title against the file it asked
to be opened. A mismatch means the automation may have read stale data — a real
confirmed case had a request for one file come back with the previous file's title
still showing, the switch not yet having happened.

That row's value is untrustworthy and gets flagged. **The subtle part:** an
"already logged" check that only asks whether the value is non-empty will treat a
mismatched row as done forever, because it does have a value — a wrong one. The
filter now also excludes any row still flagged, so it is picked back up
automatically on the next run.

No rebuild is needed: the conversion succeeded and only the read was suspect, so a
retry re-opens the existing ACD. A successful retry overwrites the flag, so this
self-heals with no manual bookkeeping. On reconciliation, such rows have their
capture columns **cleared** rather than their stale values trusted.

### Zero capacity — retried automatically

A real capacity reading is never 0 — every project carries the empty-project floor
at minimum. A literal `0` is a bad-read symptom: wrong dialog or field focused, or
a timing glitch. Same flag-and-exclude mechanism, same automatic retry.

### A blank error count is weaker evidence than an explicit zero

A few hundred captured rows have a **blank** error count rather than a `0` — they
were captured before the column existed, so nobody recorded the build status
either way.

`is_valid_capture()` counts them, and should: measured both ways the difference on
the corpus headline is small, so discarding hundreds of real rows on a hunch would
be its own unforced error. `accuracy_report.py --strict` excludes them when that
needs re-checking.

**Where it does matter is anchoring.** When a single row is the pair or control for
a new measurement, a blank means the whole comparison rests on a build nobody
verified. **Prefer an explicit-zero row for that job**, or test more than one
instruction so a single soft anchor cannot carry the conclusion alone.

### Build counts above 999 are abbreviated

Studio abbreviates the error and warning counts on its count buttons and can render
a thousands separator. A naive `^(\d+)` read gives:

| button text | naive read | actual |
|---|---:|---:|
| `1K Errors` | 1 | ≥1,000 |
| `1.2K Errors` | 1 | ~1,200 |
| `1,234 Errors` | 1 | 1,234 |
| `12K Errors` | 12 | ~12,000 |

**A build with thousands of errors logged as one error** and read downstream as
very nearly clean. The validity filter rejected it either way, so it was never
silently used — but it looked like a trivial blip rather than a total failure,
which is how it would get triaged last instead of first.

Two fixes. The count parser now handles the comma and K/M forms. And **Studio's own
summary line is the authority** — `Complete - N error(s), M warning(s)` carries the
count unabbreviated however large, and nothing was reading it. It is parsed off the
raw pane text, because the error-log reader keeps only the leading characters and
the summary sits at the end. **When the buttons and the summary disagree, the
summary wins** and the disagreement is recorded. When a count is abbreviated and no
summary is available, the expansion is a rounded floor and is labelled as one.

> One consequence for existing data: any row captured before this fix reading
> exactly `1` error is ambiguous — a genuine single error, or a `1K` misread. Only
> a file large enough to plausibly reach 1,000 errors is in doubt.

### Firmware the SDK cannot open is skipped automatically

The SDK refuses some firmware revisions outright, with a permanent rather than
transient error, so retrying every pass is pure waste. A failed row carrying that
message is skipped on future passes **as long as its content hash has not changed**.
Regenerate the sample at a supported revision and the hash differs, so it is tried
again automatically.

Same self-healing pattern as the capture-side flags, on the conversion side.

The generated corpus is one processor at one firmware throughout, enforced by lint,
so in normal operation nothing should reach this path.

---

## Auditing rows with errors: stale versus genuine, before anything else

Every capture run skips files, and each one has to be dealt with. **The first cut
is not "what is broken" — it is whether the failing capture is even about the file
that exists today:**

    the file's last write time   vs   the row's capture date

**If the L5X was regenerated after the capture, the recorded errors were against a
version that no longer exists.** In one audit, 72 of 138 error rows were exactly
that — captures taken before a generator fix, on files rewritten hours later.
Nothing was wrong with them; they needed their capture columns cleared so the next
pass would pick them up. **Diagnosing any of those as a live bug would have been
chasing a ghost.**

Do this check first, every time, before reading a single error message.

What remains splits three ways:

- **Superseded** — the question has since been answered exactly by a
  better-designed test. Delete the files and the rows; a broken original has no
  remaining value once its question is closed with zero residual.
- **Obsolete** — a synthetic composite is a proxy for a real program. **Once real
  programs are on file the proxy stops earning its keep, and a broken proxy never
  did.**
- **Genuinely unfixed** — kept and listed in `OPEN_BUILD_ERRORS.md`. These need the
  real Studio error text. **Guessing is what produced the invented alarm condition
  types**, all four of which were rejected.

---

## Platform notes

**1769-series requires clicking Estimate first.** 1756 and 5069 processors show a
real capacity figure immediately; 1769-series does not — the Estimate button has to
be clicked before the tab shows anything meaningful. **The AHK loop does not do
this**, so it would silently read a stale or blank value. Existing 1769 points were
manually reported for this reason. 1769 is dead architecture, so this is not being
fixed; any future 1769 file needs manual reporting or an extra AHK step.

**Keep controller model and firmware consistent across a comparison set.** Memory
reporting granularity may differ between families, and a file on a different
processor or firmware cannot be differenced against the existing captures without
first subtracting a baseline difference that is itself only approximately known —
which defeats the isolation test.

---

## Sample design principles

### One variable

**Every sample changes exactly one variable from its pair.** Testing whether UDT
member order affects size means two files identical in every respect except order —
same member types, same count, only the order differs.

This is what makes the corpus usable for regression later instead of a pile of
unreproducible one-offs. `scripts/confound_check.py` checks it mechanically, across
18 dimensions, and has found six blind spots in itself doing so.

### Scale until the delta is unambiguous

A single tag's byte difference can be lost in reporting granularity. 10,000-element
arrays exist for exactly that reason. For logic, generate the same pattern at 10,
100 and 1,000 instances — both to get a measurable delta and **to confirm the
relationship is linear before fitting a weight from two points.**

### Hold the source tag declared and referenced

When a pair moves an operand from a tag to something else, **keep the tag both
declared and referenced in both members**. Otherwise the term under test is
confounded with per-tag declaration cost, which is 84+ bytes and swamps most
effects being measured.

---

## Tolerance

| tier | good | acceptable | a real gap |
|---|---|---|---|
| Tag / UDT / AOI (exact) | within 1% | 3% | above 5% |
| Logic (estimated) | not held to the same bar | | |

Compiled logic size is a fitted heuristic by nature of the problem, so it carries
more slop. That is not a target to force down.

**Do not defer an open discrepancy in the exact tier because the logic tier is
more interesting.** An error in the tier the tool calls exact undermines its whole
value proposition more than an acknowledged estimate does.

The project-wide noise floor is **±8 bytes**. Treat a residual inside it as
agreement.

---

## The standing loop

When a batch of captures lands, run this in order:

1. **Reconcile** into `samples/captures.csv` by row-level merge on `sample_id`.
   Recompute deltas against the current engine — never trust a stored one.
2. **Check conversion status.** Cross-reference every committed file against the
   last recorded status for that exact filename. Any committed file with no `ok`
   on record is logged explicitly, never silently dropped.
3. **Run `capture_errors.py`** and do not proceed past a non-zero exit.
4. **Re-derive** sizing formulas from the new data and wire what is now confirmed.
5. **Full-depth open-questions review.** Recompute every question's rows live
   against the current engine. New engine state can retroactively resolve or break
   an older row, so re-check everything, not just this batch.
6. **Bring the docs current together.**
7. **Specify the next batch — do not generate it.** Ask first, every time.
8. **Report**, including which questions carry suspect rows and how many.
