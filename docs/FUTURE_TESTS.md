# Future Tests To Improve Modelling / Algorithms

James, 2026-09-04: *"make note of future tests that should be done to
improve your modelling/algorithms for testing."*

Standing rule for everything below: a test only counts once it comes back
with `error_count = 0`, no `WINDOW TITLE MISMATCH`, no `ZERO CAPACITY` —
see docs/TESTING_PLAN.md's "A row that BUILT WITH ERRORS is never a valid
fitting point". Check that BEFORE reading any residual pattern.

Ordered by expected impact on the <1%-on-a-real-file North Star.

---

## 0. Composite surcharge cap vs REAL-program scale — now the #1 error source

**First real virgin-file measurement, 2026-09-04.** James supplied
`Cardin_TrimSortStack_20260624r00` (1756-L83E, fw 35.13, 35 MB L5X, never
seen by this project). Predicted **7,162,455**, actual **8,178,556** —
**12.4% UNDER**, a miss of 1,016,101 bytes. That is the honest North Star
number and it is nowhere near <1%.

Root cause, measured not guessed: `logic_instructions.composite_surcharge_cap`
(12,000 bytes, file-wide) suppresses **1,551,065 bytes** on this file.
The cap was fitted against the synthetic composite corpus, which is not
remotely representative of a real program's JSR-target content:

| file | aoi_instr | jsr_instr | uncapped surcharge | vs the 12,000 cap |
|---|---:|---:|---:|---:|
| REAL Cardin_TrimSortStack | 6,255 | 30,595 | 1,563,065 | **130.3x** |
| synthetic v4_074 | 450 | 1,899 | 98,253 | 8.2x |
| synthetic v4_001 | 146 | 564 | 29,428 | 2.5x |
| synthetic v2_25 | 111 | 120 | 7,860 | 0.7x |

The real file has **16x to 54x more JSR-target instructions** than any
synthetic composite. So the cap behaves completely differently in the two
regimes: mild trimming on the files it was fitted against, total
annihilation on a real program. With the cap the model ignores JSR-target
content almost entirely — which is exactly the "JSR target content is NOT
free" finding OQ-JSRPARAMCOST already proved and this cap silently undoes
at real scale.

Neither setting is right on its own: capped gives -12.4%, fully uncapped
would give **+6.5%** (predicted 8,713,520). The value that lands exactly on
this file is a surcharge of ~1,028,000, i.e. ~66% of uncapped. That is ONE
data point and must not be fitted on its own — the axis_scale lesson.

**Tests needed:**
- **More real captured programs, of varying size.** STILL OPEN, and still
  the only thing that can fit a cap/scale law that holds at real scale.
  Two or three more virgin files with actual Capacity readings would
  settle the shape (constant? proportional? saturating?). Nothing
  synthetic substitutes for this.
- ~~A generator with REAL-scale JSR-target content~~ — **BUILT
  2026-09-04**, `src/sample_gen/gen_realscale_surcharge.py`, 23 files,
  awaiting capture:
  - `realscale_jsrtgt_xic_n{10,50,100,1000,5000,10000,15000,22500}` — the
    identical rung text and tag pool as the existing valid `instr_xic_n*`
    captures, moved from MainRoutine into a single JSR target. Five of the
    eight pair exactly with an existing error-free capture, so the
    JSR-target cost falls out as a direct paired difference with no model
    in between. Top end reaches 45,000 target instructions, past the real
    file's 30,595. Uncapped surcharge spans 0.08x to 176x the cap.
  - `realscale_jsrsplit_k{10,50,250}` — 20,000 target instructions held
    constant, split across K distinct targets. First test of whether the
    cap is really FILE-WIDE (as modelled) or per-routine.
  - `realscale_aoiint_n{0,50,500,2000,6000,12000}` — the AOI half of the
    surcharge with no JSR target in the file at all. There is no valid
    nonzero AOI-content point in the corpus today (`aoi_logic_scale_*`
    stopped at 100 instructions and errored at every nonzero point).
  Every file is built from rung text taken verbatim from
  `gen_logic_sweep.INSTRUCTIONS` — the only large-scale shape with a
  proven error-free build (`randommix_05`, 27,267 rungs, 0 errors) —
  precisely because the previous attempt at this question
  (`jsr_target_content_scale_*`) used a hand-rolled mix and came back
  5/26/50/75 errors, still undiagnosed.
- ~~Structured Text is completely unmodeled~~ — **FIRST DATA GENERATED
  2026-09-04** (OQ-STSIZING). `realscale_st_n{0,25,100,400,1000}` (plain
  assignment lines) + `realscale_st_forloop_n00075` (the FOR ... DO ...
  END_FOR shape copied from the real file's own ST routines). The engine
  predicts an identical 23,277 across the whole flat ladder, so whatever
  comes back IS the per-ST-line cost. Still unmodeled in code until that
  capture lands.

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
