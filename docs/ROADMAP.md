# Roadmap

Current focus and the next few days of planned work. Structural phases live
in `PROJECT_PLAN.md`; individual open items live in `OPEN_QUESTIONS.md`.

Last updated 2026-09-06.

---

## Where the tool actually stands

Measured on the nine real production exports, which are the only accuracy
evidence that counts:

| file | actual | predicted | delta |
|---|---:|---:|---:|
| `mrfp_edger_2026_06_01_r00` | 2,281,316 | 2,282,655 | +0.06% |
| `k3m16_edgers_20220808r00` | 4,044,994 | 4,009,539 | −0.88% |
| `emporiumedger_20250905r1` | 1,703,932 | 1,685,256 | −1.10% |
| `emporium_2025_05_28r01` | 7,136,625 | 7,018,569 | −1.65% |
| `pukall_gang_20260414_r00` | 2,502,336 | 2,460,139 | −1.69% |
| `cmu_2025_10_14r00` | 5,217,440 | 5,110,641 | −2.05% |
| `accutally_20260803` | 5,999,972 | 5,843,055 | −2.62% |
| `ipc_edgerline_20251217r1` | 2,255,773 | 2,177,942 | −3.45% |
| `murraybros_20260122r1` | 923,320 | 869,030 | −5.88% |

Mean absolute error **2.15%**, five of nine inside 2%, two inside 1%. Every
file still under-predicts, so what remains is a missing cost rather than
noise.

Progress this cycle: 3.51% → 3.34% (Structured Text wiring) → 2.99%
(ST inside AOI definitions) → 2.81% (zero-connection modules) → 2.15%
(JSR per-target/per-call split).

---

## Phase 7 — Close the last 1.15%

The goal is 1% on every real file. The residual is concentrated in AOI-dense
programs, and the correlation is unambiguous: against the current residual,
AOI axis parameters score +0.889, AOI internal rungs +0.848, AOI definition
count +0.838, AOI local tags +0.835.

### Immediate — waiting on capture (363 files queued)

Nothing here needs new design work; it needs the capture run.

| batch | files | closes |
|---|---:|---|
| `asmclose` | 64 | `OQ-MODULEMARGINAL` — every remaining ASSUMED item that reaches a real file |
| `aoistructure` | 56 | `OQ-AOISTRUCT` — the seven unpriced AOI structural properties |
| `defscale` | 30 | `OQ-DEFSCALE` — per-definition cost at real scale |
| `cpt_closeout` | 58 | `OQ-CPTNARROW`, `OQ-CPTARRANGE` |
| `driveaxis` | 16 | axis parameters and nested AOI instances |
| `mbshape` | 14 | AOI-dense composite shapes |
| `verified_instructions` | 33 | `OQ-VERIFINSTR` |
| others | 92 | firmware matrix, module sweeps, shell scaling |

After this run, every ASSUMED constant that touches a real file is either
measured or explicitly out of scope. The one exception is reported rather
than hidden: **150 SMC Flex-E** (0.069% exposure) has no real module XML on
file, so it cannot be tested until a real export exists.

### Day 1–2 after capture
1. Reconcile the manifest and log every conversion failure.
2. Read the `aoistructure` flat lines. Each group is predicted to a single
   byte across every file in it, so any spread is a directly readable
   unpriced cost. Expected order of magnitude, largest first: member name
   length, predefined-structure members, InOut parameters, array dimensions,
   member descriptions, extra internal routines.
3. Wire whichever of those come back with a clean, non-interacting slope.
   Cross-validate every fit on held-out files before keeping it — three
   surcharge fits and one shell hypothesis have already been rejected at
   this step, and all four looked good in sample.
4. Re-measure the nine real files. This is the only number that decides
   whether the work landed.

### Day 3
5. Read the `defscale` sweeps for curvature in per-definition cost at real
   scale. This is the same failure shape that shell scaling already turned
   out to have — a constant fitted at n=2 and applied at n=200.
6. Re-check every open question against the new engine state, not just the
   ones this batch was aimed at.
7. Design the follow-up batch from whatever the residual then points to.

### Known blockers that need external input
- One real **5069** export with a controller capture. Every real file is a
  1756-L8x, so the entire 5069 model rests on generated files the model was
  fitted on (`OQ-REAL5069`). This is the largest untested claim in the tool.
- Two Studio 5000 error-log lines for the remaining build failures (one 2198
  drive catalog, one `almd_minimal`).
- The alarm `ConditionType` dropdown list plus one analog alarm example.

---

## Phase 8 — Make it safe to hand to someone else

The tool is going to people whose code, naming conventions and AOI libraries
are nothing like the corpus it was fitted on. Accuracy on unfamiliar input is
a different property from accuracy on the nine real files, and it is not yet
measured.

1. **Never fit anything to a specific AOI, UDT or tag name.** Cost models
   must be functions of structure. `gen_aoi_structure.py` is built to this
   rule and it is the standard for everything that follows.
2. **Say what is not known.** The UI already warns on a safety project. It
   should do the same for a platform with no real validation behind it (5069
   today), for an export type that is not a full controller export, and for a
   file whose instruction mix falls outside the fitted range.
3. **Fail visibly, not silently.** Any element the model cannot price should
   surface as a coverage notice in the UI, not vanish from the total. The
   plumbing exists; the presentation does not.
4. **First-run experience.** Install, point at a file, get a treemap. No
   `cd src`, no manual dependency steps.

---

## Phase 9 — UI

Deferred until accuracy is settled, but the list is kept current so the work
is ready when the estimator stops moving.

- Confidence shown per node, not just a global "estimated" flag — exact,
  fitted and unpriced should be visually distinct at every level of the
  drill.
- A "what changed" comparison between two exports of the same program, which
  is the question actually asked when a download starts failing.
- Budget selector across CompactLogix memory sizes, with headroom shown
  against the selected target rather than a bare byte total.
- Alarm and axis root groups exist; module I/O should join the summed total
  once its confidence justifies it.
- Export the treemap itself, not only the CSV/XLSX tables.

---

## Standing rules for this phase

- Cross-validation decides every fit. In-sample fit has been wrong four times
  in a row on this project.
- Real files are the scoreboard. The generated corpus is the instrument.
- A capture row with `error_count > 0` is never a valid fitting point.
- Fix the estimator, do not just document the gap.
