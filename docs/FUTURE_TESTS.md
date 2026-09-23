# Future Tests

Tests that would improve the model, kept as a standing list. Ordered by expected
impact on real-file error.

This is the **wish list**. The ranked queue of what is actually being worked is
`TASKS.md`; individual questions are in `OPEN_QUESTIONS.md`.

**A test only counts once it comes back with zero errors, no window-title mismatch
and no zero-capacity flag.** Check that before reading any residual pattern — see
`TESTING_PLAN.md`.

**State up front how many percentage points a test should move.** A test that
cannot state that is not worth running. And if the mechanism is "a category cost
constant is slightly wrong," the ceiling result in `ROADMAP.md` already answers it.

---

## 1. More real captured programs

**The only thing that can settle anything at real scale, and nothing synthetic
substitutes for it.**

Two or three more previously-unseen exports with actual capacity readings would do
more than any generated batch. The reason is specific: **real programs sit 16× to
54× outside the range the synthetic composites cover** on JSR-target and AOI
content. A law fitted on the synthetic range behaves completely differently in the
real one.

**Predict each new file and write the number down before the capacity reading is
taken.** That is the only procedure that adds auditable evidence rather than
another fitting input. It has been done once, and that blind test is the strongest
evidence the project has.

## 2. The literal-operand rate table

A 29-file batch is built and awaiting capture. **This is the one candidate with
measured support that the ceiling result does not bound**, and the only one so far
that moves the max rather than the mean.

What it needs to return: the per-type rate for integer literals, which are 98% of
the exposure and completely unmeasured. See `OQ-LITERALOPERAND` and the arm
descriptions in `SAMPLE_GENERATION.md`.

## 3. A structural module model

**The blocker for ever predicting an unseen catalog.** Today module overhead is a
per-catalog lookup with a flat fallback, which cannot generalise to a catalog
nobody has captured.

What would fit `class_base + per_point × points` instead:

- **Point-count ladder within one class.** Same family, only point count moving:
  digital input at 8/16/32, digital output at 8/16/32, analog input at 4/8/16,
  analog output at 4/8. Gives `per_point` per class directly.
- **Same point count, different class.** 16-point digital input versus digital
  output versus analog, point count held fixed — isolates `class_base`.
- **Same class across series.** The same nominal module on 1756 versus 1769 versus
  5069 versus 1734. **This is what decides whether one table generalises across
  platforms.**
- **Diagnostic and specialty classes** — high-speed counter, serial, motion
  diagnostics, safety I/O. Each likely has its own base; all are currently lumped
  into the flat default.

## 4. Module multi-instance marginal cost

Whether the Nth copy of a catalog costs the same as the first is measured for ten
catalogs and open for the rest.

- **Same catalog repeated at N = 1/2/4/8/16**, on a simple discrete module with no
  motion or safety content so the build is error-free.
- **N distinct catalogs versus N copies of one catalog** at the same N — separates
  "repeated catalog" from "more modules on the bus."
- **The with-axis drive rate.** Every attempt so far captured with build errors.
  The bare-drive rate is measured and deliberately excluded from the table because
  no real program contains a drive with no axis tag. **Root-cause the build error
  first — that is a prerequisite, not an analysis task.**

## 5. REAL-destination CPT coverage gaps

Exact on every captured row, but only at operator counts 1, 2 and 5.

- **3, 4, 6 and 8 operators** — resolves whether the five-plus-operator extra is a
  step at 5, a per-operator term, or tied to tier mixing. It currently rests on
  n=5 alone.
- **Multi-operator expressions containing `**`** — the single-power extra is
  confirmed at one operator only, and `**` adjacency is already known to be its own
  unmodelled term.
- **BOOL and LINT operands inside a REAL-destination CPT.** BOOL is deliberately
  uncharged because no real example exists.
- **STRING operand or destination**, if legal at all. Untested.

## 6. JSR threads

Two effects are visible on valid data and neither is wired, for the same reason:

- **Distinct-target count** gives an exact +125 bytes per additional target across
  six points.
- **Target-name length** gives an exact +80 per 8 characters across five points.

**Neither is wired because one cell is missing: a crossed test with name length and
target count varied together.** Without it there is no way to tell whether the name
cost is per-target or per-file. That single missing cell is the whole blocker.

Also open:

- **STRING and UDT-typed JSR parameters** are real, unmodelled and non-linear in
  parameter count. Needs the even counts to resolve the shape.
- **The target content-scale sweep must be re-run error-free** before its rate can
  be trusted.

## 7. Composite-file residual

- **A composite generator whose feature schedule is not aliased.** Every feature in
  the current one is `i % k`, so UDT count, array count, string count and drive
  count are **perfectly collinear** and no regression can separate them. Vary
  features independently — latin square, or random per feature.
- **Composite files with no motion content** — isolates whether the residual tracks
  drive and axis content or module and tag content.
- **A ladder between an isolation file and a full composite**: 2, then 5, then 10
  feature types combined, so the point where per-feature additivity breaks down
  becomes visible.

## 8. Alarm conditions inside real content

The per-condition formula is derived from a generated batch and lands within 0.16%
on one real program and 8.8% short on another. Since alarms are 19–21% of total
memory on those files, that 8.8% matters.

- **Alarms on a UDT-scalar host.** A handful of real conditions sit on a UDT rather
  than a BOOL array; the batch only covers array hosts.
- **AlarmSet membership.** The operator and rollup inclusion flags are true on
  every real condition and no file varies them. Whether alarm **sets** carry their
  own cost is untested and unrepresented.
- The clean confirmation would be **one real file captured twice, once with its
  alarm definitions deleted in Logix Designer and re-exported by Studio itself.**
  Not by editing the XML — see the read-only rule in `CLAUDE.md`.

## 9. Housekeeping

- **Rows whose capture predates a regeneration of the file** need re-capture. Their
  recorded numbers are against content that no longer exists.
- **Rows with build errors** need each error root-caused and a clean re-run, or
  explicit skip-listing. Never leave one silently in the corpus either way.

---

## Superseded — do not re-run

Recorded so these are not mistaken for open work.

| test | outcome |
|---|---|
| Composite surcharge cap versus real scale | The cap was found to suppress over a million bytes on a real file while barely trimming the synthetic files it was fitted on. Resolved; the surcharge model was rebuilt. |
| Structured Text sizing | Was completely unmodelled. Now one measured law covering the base ladder, operator premiums, source conversion and AOI calls from ST. |
| Tag-based alarm conditions | Were priced at zero across thousands of real elements. Now a measured formula. |
| Per-instruction weights for the corpus instruction mix | 99.72% of real occurrences carry a weight. |
| Branch arrangement | Byte-exact at every leg count. Not an error source. |
| Tag declaration order | Free. |
| 2-D array subscripts | Cost zero. |
