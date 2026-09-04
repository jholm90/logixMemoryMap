# Future Tests To Improve Modelling / Algorithms

James, 2026-09-04: *"make note of future tests that should be done to
improve your modelling/algorithms for testing."*

Standing rule for everything below: a test only counts once it comes back
with `error_count = 0`, no `WINDOW TITLE MISMATCH`, no `ZERO CAPACITY` —
see docs/TESTING_PLAN.md's "A row that BUILT WITH ERRORS is never a valid
fitting point". Check that BEFORE reading any residual pattern.

Ordered by expected impact on the <1%-on-a-real-file North Star.

---

## 1. Structural module model (OQ-MODULESTRUCTURAL) — highest value

The blocker for ever predicting an UNSEEN catalog. Needs single-module
isolation captures spanning module CLASS and POINT COUNT, so overhead can
be fitted as `class_base + per_point * points` instead of a per-catalog
lookup.

- **Point-count ladder within one class.** Same family/series, only the
  point count changing: 1756 digital input at 8/16/32 points
  (1756-IA8D, IA16, IB16, IB32), digital output at 8/16/32, analog input
  at 4/8/16 (1756-IF4, IF8, IF16), analog output at 4/8. Gives
  `per_point` per class directly.
- **Same point count, different class.** 16-pt digital input vs 16-pt
  digital output vs 16-pt analog — isolates `class_base` with point count
  held constant.
- **Same class across series.** 1756-IB16 vs 1769-IQ16 vs 5069-IB16 vs
  1734-IB8 — tests whether class_base is per-series or universal. This is
  what decides if one table generalizes across platforms.
- **Already generated, awaiting capture:** the 12
  `rack_5069_single_*` files (one 5069 catalog each) — these are the 5069
  half of the "same class across series" axis.
- **Diagnostic/specialty classes:** HSC, SERIAL, motion diagnostics,
  safety I/O — likely their own class_base, currently all lumped into the
  flat default.

## 2. REAL-destination CPT coverage gaps

`cpt_expression.real_dest` (wired 2026-09-04) is exact on 29/29 real rows
but only at operator counts 1, 2 and 5.

- REAL-destination CPT at **3, 4, 6, 8 operators** — resolves whether
  `five_plus_operator_extra` (currently +4, resting on n=5 alone) is a
  step at 5, a per-operator term, or tied to tier mixing.
- **Multi-operator expressions containing `**` with a REAL destination** —
  `single_pow_extra` is confirmed at n_ops=1 only.
- **BOOL and LINT operands inside a REAL-destination CPT** —
  `_CPT_INTEGER_OPERAND_TYPES` currently converts SINT/INT/DINT/LINT and
  deliberately ignores BOOL (no real example exists).
- **STRING operand / STRING destination CPT**, if legal — untested.

## 3. Module multi-instance marginal cost (OQ-MODULEIO's open sub-thread)

Whether the 2nd/3rd/Nth copy of a module costs the same as the 1st is
still genuinely open — and the one apparently-clean answer we had turned
out to be from files that built with errors (see TESTING_PLAN.md). Needs
a clean re-run:

- **Same catalog repeated N times**, N = 1/2/4/8/16, on a simple discrete
  module with no motion/safety content (so the build is error-free).
- **N distinct catalogs vs N copies of one catalog** at the same N —
  separates "repeated catalog" from "more modules on the bus".
- **Re-run the whole `axis_scale_*` sweep error-free.** Every one of the
  18 files currently has `error_count = drives + 1`. Until the drive/axis
  content builds clean, nothing about multi-drive scaling can be fitted.
  Root-cause the per-drive error first — that is a prerequisite test, not
  an analysis task.

## 4. JSR threads

Two effects are visible on VALID data and one is already exact:

- **Distinct-target count**: `jsr_multi_distinct_targets_n01..n50` gives
  an exact `+125 bytes per additional distinct JSR target` (6/6 points,
  `d = 125n - 280`). Not yet wired — wanted a cross-check first.
- **Target-name length**: `namelen04/08/16/32/40` at fixed n=10 gives an
  exact `+80 bytes per 8 characters` (5/5 points). Needs a **crossed
  test** — name length AND target count varied together (e.g. n=20 with
  len=32) — to tell whether the name cost is per-target or per-file. That
  single missing cell is why neither is wired yet.
- **STRING/UDT-typed JSR parameters**: real, unmodeled, and non-linear in
  param count (n=1 → +271, n=3 → +2,307, n=5 → +3,939 at 100 calls).
  Needs n = 2, 4, 6, 8, 10 to resolve the shape.
- **`jsr_target_content_scale_*` must be re-run error-free** (currently
  5/26/50/75 errors) before its content-scaling rate can be trusted.

## 5. Composite / realistic-file residual

`composite` is the North Star proxy and sits at 2.50% mean on valid rows.
Known: it is NOT the composite surcharge (removing it entirely moves v4
only ~0.5%), and NOT a per-element error on the filler array (residual is
roughly constant ~-50k regardless of filler size).

- **A composite generator whose feature schedule is not aliased.** Every
  v4 feature is `i % k`, so `udt_count`, `n_arrays`, `string_count` and
  `n_drives` are perfectly collinear (identical correlation, -0.567) and
  no regression can separate them. Vary features INDEPENDENTLY (e.g.
  latin-square or random-per-feature) so residual can be attributed.
- **Composite files with NO motion content** — isolates whether the
  residual tracks the drive/axis content or the module/tag content.
- **Ladder between "isolation file" and "full composite"**: 2, then 5,
  then 10 feature types combined, so the point where per-feature
  additivity breaks down becomes visible.

## 6. Housekeeping / re-captures

- 132 of 1,978 captured rows are invalid (`error_count > 0`), 87 of them
  in `composite` and 28 in `modules`. Each needs its build error
  root-caused and a clean re-run, or explicit skip-listing.
- The three `axis_scale_*_regen` files carry captures that predate the
  ExtendedProperties/ConfigID regeneration — stale content, needs
  re-capture.
- `rack_pointio_n05`'s capture predates the Bus Size fix regeneration.
