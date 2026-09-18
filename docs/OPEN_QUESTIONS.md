# Open Questions

**FIVE. Down from forty on 2026-09-18, and the other thirty-five were not
abandoned — they were bounded.**

An eight-parameter per-category fit, fitted directly on the held-out real
programs (cheating, an upper bound), reaches mean 1.0149% / max 2.5919% and
still fails the stopping rule. Under leave-one-out it is worth **0.007
points**, with half the files getting worse. So every question whose
mechanism was "a category cost constant is slightly wrong" has a measured
maximum payoff of approximately zero, however cleanly it would answer. Those
are in `RESOLVED_QUESTIONS.md` with their reasoning intact and the closing
rationale at the top of that section.

What is left is what that experiment does NOT bound:

- **OQ-REALUNDER** — the residual itself. Not a sub-question of the gap -- it IS the gap.
- **OQ-CTLSHELL** — the only measured evidence of content the engine does not count at all.
- **OQ-RUNGSHAPE** — a per-rung term the model does not have. Still untested; 5-file spec written.
- **OQ-EXPORTSCOPE** — a correctness requirement, not an accuracy question.
- **OQ-BUILDFAIL-OPEN** — a defect log for files that do not build. Kept visible on purpose.

**The bar for opening a new one:** state, before any file is built, how many
percentage points it should move on the seventeen real programs and by what
mechanism. If the mechanism is a category scale, the ceiling result already
answers it and the question does not get opened.

---

1. **OQ-EXPORTSCOPE** — new, 2026-09-04. The estimation path has to handle
    controller, UDT, AOI, program, routine and rung-logic exports.
    Anything that is not a controller export cannot use the base load, but
    rungs, routines and
    programs might contain controller tags"*). The scope machinery is now
    WIRED (`parser/export_scope.py`): a partial export gets no project base
    load, no firmware/catalog/safety baseline delta and no task/program
    shell, and its total is reported split three ways — target / context /
    project. What remains genuinely open is what a partial export costs
    **on import**, which is not the same question and has no data at all:

    - **A Program export's own shell.** Importing a program into a
      controller creates a program, and `task_program_overhead.program_extra`
      is the marginal cost of an extra program in a whole project — but
      that constant was fitted across whole-project captures and has never
      been checked against "import one program into an existing project".
      Charging it here would be a guess, so nothing is charged.
    - **A Routine export's own shell**, same argument with `routine_extra`.
    - **A Rung export** creates no structural container at all, so
      arguably zero — untested.
    - **The context/target boundary in bytes.** Context declarations are
      reported separately because they cost their bytes only if the
      destination controller does not already have them. Whether Logix
      charges anything extra for reconciling an already-present declaration
      on import is unknown.

    Test shape needed: export one program from a known project, import it
    into a second known project, and read Capacity before and after. That
    is a controller-in-the-loop test, not a file-generation one, so it
    needs a controller at the bench rather than a generator run.


2. **OQ-BUILDFAIL-OPEN** — the 11 sample files that genuinely still fail to
    build, 2026-09-05. Audited down from 138 `error_count > 0` rows: 72 were
    stale captures against files regenerated after the fact (cleared, they
    re-run automatically), 13 were superseded by exact `realscale_*` tests,
    40 were obsolete composite v1/v2, 2 no longer exist. These 11 are real,
    and **nothing in this repo diagnoses any of them** — the generators'
    own comments are silent, so the cause has to come from the Studio
    5000 error log rather than from a guess (guessing is what produced the
    invented alarm `ConditionType` names that all four failed on).

    | file | errors | why it still matters |
    |---|---:|---|
    | `almd_minimal`, `almd_realtext` | 1 ea | **ALMD instruction cost — now high value.** Alarms turned out to be the single biggest unpriced item in the model (OQ-ALARMCOND); ALMD is the *other* alarm mechanism and is still completely unmeasured. |
    | `modulesweep_2198_{d012,d020,d032,d057,s086,s130}_ers3*` | 2 ea | The 2198 drive catalogs, all failing identically at 2 errors — one shared cause, six files. OQ-MODULEIO's per-catalog table has no entry for any of them. |
    | `modulerack_kinetix_full_bus` | 4 | Same family, full Kinetix bus. |
    | `predefprobe_axis_generic` | 1 | AXIS predefined-structure probe (OQ-AXISCOMBO). |
    | `eventtask_axiswatch` | 1 | EVENT-task trigger cost. |

    **What is needed:** the real error line for one 2198 file (all six fail
    the same way, so one diagnosis fixes six) and one for `almd_minimal`.
    That is two error messages for 9 of the 11 files.

    **2026-09-12: the 2198 half is CLOSED and needed no error log.** The six
    `modulesweep_2198_*_variant_2conn` / `s130_ers3` files **no longer exist**,
    and the `asmclose_2198_*` sweep superseded them with **18 clean captures**
    (`error_count = 0`) covering all six of the same catalogs at three module
    counts each. The entry's "one diagnosis fixes six" ask is obsolete — the
    measurement was already on disk. What it showed is below. Remaining in this
    entry: `almd_minimal` / `almd_realtext` (ALMD cost, still the ask),
    `modulerack_kinetix_full_bus` (never captured at all — the "4 errors" in
    the table above has no row behind it), `predefprobe_axis_generic` (file
    gone), `eventtask_axiswatch`. The two `aoi_multiroutine_*` rows moved to
    OQ-AOIINTERNALLOGIC, which is the question they actually invalidate.



    **CAPTURE ERRORS: 7 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    Was 13; 6 went with the discarded zero-real-usage `predefprobe_*` probes on
    2026-09-14 -- see the conversion-status audit in `docs/TASKS.md`.
    6 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `almd_minimal`, `aoi_multiroutine_control`, `aoi_multiroutine_real`, `instrfirst_crout_x10`, `instrfirst_mapc_x10`, `predefprobe_axis_generic`
    9 committed file(s) attempted and never reached `ok` in
    `convert_log.csv`: `predefprobe_opcua_server_address`, `predefprobe_ref_to_axis_cip_drive`, `predefprobe_ref_to_axis_consumed`, `predefprobe_ref_to_axis_general_drive`, `predefprobe_ref_to_axis_servo`, `predefprobe_ref_to_axis_servo_drive` (+3 more)


3. **OQ-REALUNDER** — new 2026-09-12, and it is still the single biggest
    thing between this project and its North Star.


    **IN-DEPTH REVIEW 2026-09-18 — the strongest correlate was tested with a
    MEASURED constant rather than a fitted one, and it does not work. Recorded
    because it is the most tempting wrong turn left in this question.**

    Correlating each real program's residual against every category and every
    structural counter, with the engine as it stands today:

    | driver | corr(residual bytes) | implied per-unit |
    |---|---:|---:|
    | **routine count** | **+0.888** | +656 |
    | routine_logic bytes | +0.853 | +0.163 |
    | rung count | +0.785 | +38 |
    | program count | +0.773 | +4,934 |
    | tag count | +0.704 | +26 |

    Routine count is the strongest single correlate in the whole set, and it
    survives normalising for file size better than size itself does:
    `corr(residual%, routine count) = +0.699` against
    `corr(residual%, file bytes) = +0.575`. On its face that is a missing
    per-routine cost of roughly 650 bytes.

    **And there is an independently MEASURED per-routine constant available to
    test it with**: OQ-DEFSCALE's +260 one-time for a routine containing AOI
    calls, which the RLL path does not charge and which 764 real routines would
    carry. This is the rare case where a correlation can be checked against a
    number that was not fitted to it.

    It fails:

        subtracted per routine-with-AOI-calls    mean |%|     sum-weighted
        nothing (as wired)                        1.5607        +1.3750%
        200                                       1.5458        +1.0536%
        260  (the measured value)                 1.5484        +0.9572%
        400                                       1.5546        +0.7322%
        656  (the fitted value)                   1.5659        +0.3208%

    **The BIAS collapses and the SPREAD does not move at all.** Every value from
    200 to 656 leaves mean absolute error within 0.02 points of where it started,
    while the aggregate bias goes from +1.375% to +0.32%. The correction pushes
    the seven already-over-predicting programs further over by exactly as much as
    it pulls the nine under-predicting ones back: murraybros −1.17% -> −1.62%,
    pukall −0.55% -> −1.23%, emporiumedger −1.79% -> −2.15%, salamanca −1.05% ->
    −1.51%, griffin −0.11% -> −0.63%.

    **So routine count explains the sign of the aggregate error and nothing about
    which programs are wrong.** The +0.888 is what a per-unit correlation looks
    like when the unit count and the file size both span 10x across sixteen
    points: it explains most of the variance in BYTES while explaining none of it
    in percent, because the byte variance is dominated by the largest files.
    This is the same collinearity trap `memory_model.yaml` already records for
    the 52/21 AOI/JSR refit, arrived at from a different direction.

    **What this rules out, concretely.** Any per-routine, per-rung, per-program
    or per-tag constant fitted to the real set will move the bias and leave the
    spread, because all four are collinear with size. The remaining error is not
    a missing per-unit cost.

    **And the per-FILE alternative is ruled out too, the same day and the same
    way.** OQ-CTLSHELL's measured controller-shell constant (+7,800 on 1756,
    +4,072 on 5069, from two real Empty exports) was charged to all sixteen
    programs: mean absolute error **1.5607% -> 1.6527%**, worse, and every flat
    per-file constant from 2,000 to 10,000 is monotonically worse still. Bias
    improves, spread does not — because a per-file term moves all sixteen
    equally.

    **So both remaining shapes are eliminated. The residual is
    CONTENT-DEPENDENT.** Neither counting structural units nor charging every
    file the same can reach it, and no amount of refitting either will. What is
    left has to come from differencing real content — the strip ladder — not
    from correlating totals.

    **It also stands as real-set evidence on OQ-DEFSCALE's open carrier
    question**, though not proof: if the 260 were genuinely per routine, applying
    it to 764 real routines should have tightened the spread rather than only
    shifting the bias. It did not. That is consistent with per-file, and
    consistent with per-routine plus a compensating error elsewhere, so the
    two-calling-routine probe is still the thing that settles it.

    **STATE AS OF 2026-09-14 (recomputed live, not read from the manifest):
    mean |error| 1.6112%, sum-weighted +1.2417%, worst 3.264%. Eleven files
    under-predict, five now OVER-predict.** The name of this entry is now half
    wrong and is kept only because everything downstream cites it.

    | real program | delta (actual − predicted) | % |
    |---|---:|---:|
    | `superior_2025_02_21` | +102,142 | +3.264% |
    | `ipc_edgerline_20251217r1` | +69,886 | +3.098% |
    | `elmsdale_20251017r01` | +30,432 | +2.651% |
    | `k3m16_edgers_20220808r00` | +85,468 | +2.113% |
    | `emporiumedger_20250905r1` | −35,395 | −2.077% |
    | `cmu_2025_10_14r00` | +103,446 | +1.983% |
    | `eastperry_2025_02_21` | +86,249 | +1.861% |
    | `salamanca_20250425r00` | −20,092 | −1.475% |
    | `emporium_2025_05_28r01` | +101,039 | +1.416% |
    | `flarefunction_311d_1074245` | −14,090 | −1.312% |
    | `murraybros_20260122r1` | +11,386 | +1.233% |
    | `accutally_20260803` | +71,266 | +1.188% |
    | `mrfp_edger_2026_06_01_r00` | +22,653 | +0.993% |
    | `griffin_stackerline_1mar25` | −15,540 | −0.658% |
    | `horizon_edger_march18` | −6,904 | −0.391% |
    | `pukall_gang_20260414_r00` | −1,648 | −0.066% |

    The original 2026-09-12 reading, retained because the reasoning below was
    written against it: **every one of the 16 under-predicted, mean |error|
    3.65%, worst 6.06%** — outside the 2% CLAUDE.md calls a broken estimator,
    and the first time the real set had read that way.

    | real program | delta | % |
    |---|---:|---:|
    | `ipc_edgerline_20251217r1` | −136,783 | **−6.06%** |
    | `superior_2025_02_21` | −182,948 | −5.85% |
    | `murraybros_20260122r1` | −47,002 | −5.09% |
    | `elmsdale_20251017r01` | −55,734 | −4.86% |
    | `eastperry_2025_02_21` | −206,650 | −4.46% |
    | `cmu_2025_10_14r00` | −224,522 | −4.30% |
    | `k3m16_edgers_20220808r00` | −170,926 | −4.23% |
    | `pukall_gang_20260414_r00` | −102,226 | −4.09% |
    | `emporium_2025_05_28r01` | −258,789 | −3.63% |
    | `emporiumedger_20250905r1` | −61,775 | −3.63% |
    | `mrfp_edger_2026_06_01_r00` | −64,130 | −2.81% |
    | `horizon_edger_march18` | −45,310 | −2.57% |
    | `accutally_20260803` | −152,116 | −2.54% |
    | `griffin_stackerline_1mar25` | −39,542 | −1.67% |
    | `flarefunction_311d_1074245` | −17,779 | −1.66% |
    | `salamanca_20250425r00` | −13,327 | −0.98% |

    **This is not a regression. It is an unmasking, and the arithmetic is
    exact.** The six `2198-*-ERS3` drive overheads were ASSUMED guesses of
    10,497 / 7,377 / 7,341 against a measured 4,624 — over-predicting a single
    drive by up to 2.4×. Correcting them removed 6,384 bytes of over-charge per
    drive, and `realprog_ipc_edgerline` contains exactly **12** ERS3 drives:
    12 × 6,384 = **76,608**, which is precisely how far that file's residual
    moved (−60,175 → −136,783). The same cancellation was running in every real
    program with drives.

    So the real-file accuracy this project has been quoting was **propped up by
    a wrong constant** — a large over-charge on drives cancelling a large
    under-charge elsewhere, two errors in opposite directions hiding each other,
    the same failure mode the JSR target/call refit already hit once.

    What the under-charge actually is, is now the question. It is large, it
    scales with program size, and it is NOT the drives. Candidates in rough
    order of size, all with data already pending capture:

    - **AOI internal logic** (OQ-AOIINTERNALLOGIC) — its weighting is fitted to
      five rows that captured with build errors, and errored rows under-state
      cost, so the fitted weight is likely too low. Real AOIs are logic-dense:
      39 definitions carrying 573 rungs in one of these very programs.
    - **Repeated module catalogs** — measured discount of 432..3,768 bytes per
      repeat, deliberately NOT applied because applying it project-wide made
      every one of these 16 files worse (it only ever reduces a prediction).
      That it moves them the wrong way is itself evidence the real gap is an
      under-charge somewhere else.
    - **Axis content** (OQ-AXISMARGINAL) — +3,288/axis single-drive,
      +2,600/axis dual, perfectly linear, ~650 KB of real exposure, not wired.
    - **`ETHERNET-MODULE`** (OQ-MODULESTRUCTURAL) — 109 of 438 real non-CPU
      modules, no table entry, flat 1,672 default; 161 of 438 on that default.

    The right next move is NOT another fitted constant. It is to difference one
    real program's own report against its real Capacity by CATEGORY, so the
    under-charge is attributed to tags / logic / modules / AOI definitions
    before anything is tuned. Every fix above is a guess until that split
    exists.


    **CATEGORY DIFFERENCING DONE 2026-09-13 (task #128). The result is a
    narrowing, not a fix, and it rules out a whole class of explanation.**

    Every feature countable from the L5X was tested against the residual on all
    sixteen programs, as a per-unit cost (`residual / feature`) and scored by how
    CONSISTENT that ratio is across files rather than by correlation:

    | feature | mean ratio | coefficient of variation |
    |---|---:|---:|
    | routines (all) | 337/routine | 0.66 |
    | RLL routines | 412 | 0.69 |
    | rungs | 26.8 | 0.74 |
    | AOI call parameters | 80.5 | 0.75 |
    | UDT definitions | 661 | 0.75 |
    | programs | 3,630 | 0.78 |
    | instructions | 4.6 | 0.79 |
    | AOI definitions | 2,759 | 0.79 |
    | operand references in rungs | 3.1 | 0.73 |
    | distinct tags referenced | 13.0 | 0.73 |

    Nothing is below 0.66. **There is no single missing per-unit cost**, which is
    what every segment so far has implicitly been hoping for. Tags, modules,
    tasks, ST statements, alarms, aliases, arrays, UDT and AOI member counts all
    score worse than the above.

    **Scaling one whole CATEGORY cannot fix it either, and the best candidate is
    compiled logic.** Fitting `residual = k x category_bytes` one category at a
    time:

    | category | k | mean abs residual | max |
    |---|---:|---:|---:|
    | (no model) | — | 64,236 | 149,961 |
    | routine_logic | +0.128 | **24,869** | **42,837** |
    | task_program_shell | +4.218 | 28,723 | 113,550 |
    | controller_tag | +0.033 | 31,101 | 90,751 |
    | udt_definition | +0.422 | 35,341 | 58,852 |
    | module_io | +0.603 | 37,496 | 107,456 |
    | alarm_condition | +0.206 | 39,258 | 108,967 |
    | program_tag | +0.398 | 42,722 | 113,434 |

    `routine_logic` is the only one whose MAXIMUM comes down materially -- every
    other candidate leaves a 90,000-byte outlier standing. The best pair adds
    almost nothing (controller_tag + task_program_shell, 23,712).

    **AND THE KEY FINDING: `residual / routine_logic_bytes` IS BIMODAL.** Five
    programs sit between −0.023 and +0.029; eleven sit between +0.086 and +0.224.
    There is no file in between:

        salamanca      -0.023      murraybros     +0.151
        griffin        +0.006      elmsdale       +0.212
        horizon        +0.021      mrfp           +0.096
        flarefunction  +0.027      pukall         +0.086
        emporiumedger  +0.029      ipc            +0.224
                                   k3m16          +0.150
                                   eastperry      +0.144
                                   emporium       +0.116
                                   accutally      +0.191
                                   superior       +0.174
                                   cmu            +0.128

    That is a PROPERTY eleven programs have and five do not -- worth 9% to 22% of
    their compiled ladder -- not a rate that everything pays. Tested and does NOT
    split the two groups: processor family (both groups mix 1756-L8x and 5069),
    firmware (both have v32 and v35), task count, program count, EVENT-task
    count, Safety class, coverage-gap count, file size.

    **A global logic scale-up is ruled out independently.** The 578 captured
    `logic_instr` rows are 545 of 578 within 1%, and the single-shape sweeps are
    exact at 10 through 5,000 rungs. Adding 12.8% to compiled logic would destroy
    all of them. So the per-instruction weights are right for the shapes measured
    and something about REAL ladder composition is unpriced -- which is the same
    conclusion from the other direction as OQ-SERIESOUTPUT, where a law that is
    exact on two synthetic shapes makes every real program worse. Real and
    synthetic rungs differ in something that costs real bytes in one direction
    and saves them in the other.

    **The engine CAN hit a real program**, so this is not a systemic floor:
    `griffin_stackerline` is +1,908 on 2,362,176 bytes (0.08%) and
    `salamanca` −3,978 on 1,362,000 (−0.29%), and those two are also the only
    two files with ZERO coverage gaps.

    **WHAT TO DO NEXT, and the instrument already existed and had never been
    run.** `scripts/strip_ladder.py` emits a descending ladder of one real
    program -- L0 full, then minus alarms, minus all rung and ST content, minus
    motion, minus modules, minus AOIs, minus tags, minus UDTs -- so consecutive
    captures difference each category's cost INSIDE REAL CONTENT. Zero manifest
    rows have ever come from it. Its own docstring records the same dead ends
    re-derived above, from an older engine state, and its headline numbers are
    now stale in a way that matters: it says "−5.16% and −5.03% on the two
    worst", i.e. OVER-prediction, and after seven segments of wiring fourteen of
    sixteen programs now UNDER-predict by up to +4.22%. Corrected in the script.

    **24 ladder files generated 2026-09-13** into the gitignored
    `samples/local/stripped/`, for three programs chosen to bracket the split:
    `superior` (+0.174, the worst of the eleven), `ipc_edgerline` (+0.224, the
    highest ratio) and `griffin_stackerline` (+0.006, a control from the five).
    **L2 (minus all rung and ST content) is the decisive rung** -- if the missing
    bytes are in compiled ladder, L0−L2 differs between superior/ipc and griffin
    by the predicted amount, and if it does not the bimodality is somewhere else
    entirely. These are production content with pieces missing and must never be
    committed; the script is the committed artifact.

    Also fixed en route: the ST sizer was reporting AND/OR/XOR as unpriced
    operators, which fired four times on `accutally` and is stale since segment 6
    measured AND and XOR at exactly the tier-1 rate. That file now reports zero
    coverage gaps.

    ---

    **LADDER CAPTURED 2026-09-14, TWO PROGRAMS, AND IT OVERTURNS THIS ENTRY'S
    CENTRAL HYPOTHESIS.** Seven-rung descending ladders were built and captured
    for `elmsdale_20251017r01` (5069-L330ERM v35) and
    `griffin_stackerline_1mar25` (1756-L81E v35) — full, then minus alarms,
    minus programs+logic, minus modules, minus axis/motion, minus tags, minus
    UDT and AOI definitions, down to the bare controller shell. Sign convention
    below is the manifest's: **positive = the engine UNDER-charged that
    category.**

    | category removed | Elmsdale | Griffin |
    |---|---:|---:|
    | controller-scope Alarm Manager alarms | **+21,440** | +728 |
    | programs + program tags + routines + rungs | **−29,676** | **−9,220** |
    | modules | +18,076 | **−15,580** |
    | axis / motion | +7,928 | **0 — exact** |
    | controller tags | −8,075 | −2,745 |
    | UDT + AOI definitions | +16,667 | +3,477 |
    | bare controller shell | +4,072 | +7,800 |
    | **whole file** | **+30,432** | **−15,540** |

    The step errors sum to the whole-file residual, but that is telescoping
    bookkeeping and is true by construction — it is not independent evidence
    that the split is right. What IS evidence is that the two files were
    stripped identically and disagree in sign on three of seven categories.

    **COMPILED LADDER IS OVER-CHARGED ON BOTH FILES.** This entry has spent
    five segments assuming the missing bytes were in `routine_logic`, on the
    strength of a bimodal `residual / routine_logic_bytes` ratio. The ladder
    says the opposite: removing all program content over-recovers by 29,676 on
    Elmsdale and 9,220 on Griffin. The bimodality was a correlation — real
    programs with more ladder also have more of whatever the real term is — not
    a cause. **Do not fit a logic scale-up. The hypothesis is dead.**

    Program tags are NOT a confound on Griffin, and the source file says so:
    `Griffin_StackerLine_1Mar25_r00.L5X` has **zero program tags in all 11
    programs** — every tag in that program is controller-scoped. Elmsdale does
    carry 63 program tags across 3 of its 9 programs (`InfeedData` 33,
    `TiltHoist` 21, `PlanerInterface` 9).

    **THE LOGIC STEP IS NOW SPLIT, captured 2026-09-14.**
    `Elmsdale_NoProgramLogic.L5X` keeps all 9 programs and all 63 program tags
    and cuts routines 59 → 3, and it reads **760,800 against 722,288 predicted**.
    That places an intermediate rung inside the bundled step:

    | | actual | predicted | residual |
    |---|---:|---:|---:|
    | `NoAlarms` | 904,856 | 895,864 | +8,992 |
    | `NoProgramLogic` | 760,800 | 722,288 | **+38,512** |
    | `NoLogic` | 733,988 | 695,320 | +38,668 |

    | sub-step | what it removes | actual | predicted | engine |
    |---|---|---:|---:|---:|
    | A | 56 routines, 962 rungs | 144,056 | 173,576 | **−29,520** |
    | B | 9 program shells, 63 program tags, 3 routines, 114 rungs | 26,812 | 26,968 | **−156** |

    **Sub-step B is effectively exact — 0.6% on a 26,812-byte step — and it
    carries every program shell and every program tag in the file.** The 3
    routines it removes are the `AlarmsAndMessages` **program's** routines —
    ordinary scheduled ladder, unrelated to the controller-scope Alarm Manager
    definitions removed by the `NoAlarms` rung. The
    engine charges 6,688 for the 63 program tags, 20,280 of `routine_logic` for
    the 3 routines, and **zero for the 9 program shells**. Landing within 156
    says program shells really are free at this level and program-tag pricing is
    right. Neither is where the error is.

    **All of the over-charge is in sub-step A, and it is content-dependent, not
    a scale factor.** Per rung:

        sub-step A (56 machine-logic routines)          180.4 pred   149.7 act   +20.5%
        sub-step B (AlarmsAndMessages' 3 routines)      177.9 pred   176.5 act    +0.8%

    Per instruction use, 42.5 predicted against 34.8 actual in A, and 33.3
    against 33.0 in B. Two sets of real rungs out of one real program, one
    priced almost exactly and the other 20% over. **That kills a global
    `routine_logic` multiplier for the third time** — after the 578 `logic_instr`
    rows and after the two-file ladder — because any multiplier that fixes A
    breaks B.

    The instruction mixes do not obviously explain it; both sets are dominated
    by XIC/MOV/OTE/XIO. What differs: A averages 3.98 instruction uses per rung
    against B's 5.34, and A contains all 54 JSRs and all 65 NOPs in the file
    while B contains none. A also holds every `_SBR_*` subroutine and the cam
    routines (`_SBR_LevellingCalcs` alone is 13,924 predicted, the largest
    single routine in the program).

    **What this says about the next instrument.** Another category ladder adds
    one equation. A **per-program** strip of Elmsdale adds nine, over nine
    different real logic mixes with per-routine predicted bytes already known
    for each. That is the discriminating measurement now, and it is the same
    export cut a different way rather than anything generated.

    **TAG-BASED ALARMS ARE THE SECOND-LARGEST CATEGORY IN BOTH REAL FILES, and
    they are not the parked ALMD/ALMA question.** The alarms step removes
    `<AlarmCondition>` / `<AlarmConfig>` / `<HMIGroup>` elements hanging off a
    single BOOL array tag — 200 on Elmsdale, 400 on Griffin — and an exhaustive
    element-tag diff of full-vs-NoAlarms shows those are the ONLY elements that
    differ, so the step is clean. It is worth **243,040 bytes on Elmsdale (21%
    of the whole program) and 443,128 on Griffin (19%)**.

        per condition   Elmsdale  actual 1,215.2   predicted 1,108.0
                        Griffin   actual 1,107.8   predicted 1,106.0

    `alarm_conditions` (800 + 500n + associated-tag costs) is within 0.16% on
    Griffin and 8.8% short on Elmsdale. Two files, one nearly exact and one not,
    on a category this large, is the highest-value open thread this ladder
    produced. See OQ-ALARMCONDREAL.

    **THE BARE CONTROLLER SHELL IS UNDER-CHARGED ON BOTH, AND IT IS NOT THE
    BASELINE CONSTANT.** Both `Empty` files are genuine: one Task, zero
    Programs, zero Tags, zero DataTypes, zero AOIs, one Module (the controller).
    Griffin_Empty is 1756-L81E v35 — the exact platform every generated test
    file uses — and reads **21,096 against a predicted 13,296**. But
    `emptyroutine_n01`, a GENERATED 1756-L81E v35 file that carries a program
    and a routine the shell does not, reads 18,884 and the engine is
    byte-exact on it, as it is on `emptyrungs_*`, `aoishape_control_empty` and
    `axis_baseline_motiongroup_only`. The baseline constant is therefore right;
    a real export's controller shell carries ~2,400+ bytes of content the
    generated files do not have and the engine prices at zero. Candidates, none
    of them yet priced: the controller's own `Module` element with real
    `EKey` / `Ports` / `Bus` / `EthernetPorts` config, `SafetyInfo`,
    `RedundancyInfo`, `Security`, `Trends`, `DataLogs`, `TimeSynchronize`,
    `CST`, `WallClockTime`, `QuickWatchLists`. See OQ-CTLSHELL.

    **MODULES DISAGREE IN SIGN**, +18,076 under on Elmsdale against −15,580
    over on Griffin — and the two machines are built differently in exactly the
    way that would cause it. Griffin is a **Kinetix 5700 shared DC bus**: two
    `2198-P208` supplies feeding ten `2198-*-ERS3` drives on one bus, plus five
    generic `ETHERNET-MODULE`, 18 non-CPU modules total. Elmsdale is
    **distributed discrete devices**: 22 POINT I/O modules behind three 1734
    adapters, four PowerFlex 525 and three PowerFlex 755, 28 non-CPU modules
    total, each its own Ethernet connection.

        Elmsdale  +18,076 under / 28 modules  =  +645 per module
        Griffin   −15,580 over  / 18 modules  =  −866 per module
                  −15,580 over  / 10 ERS3 drives = −1,558 per drive

    So this is not one constant that is slightly wrong in both directions; it is
    a bus-connected drive costing less than the table charges and a discrete
    device costing more. Directly implicated: `repeat_bytes` was removed from
    all six `2198-*-ERS3` catalogs on 2026-09-13 and their confidence downgraded
    KNOWN → ASSUMED, which raised the per-drive charge — and Griffin is the real
    program with ten of them. That is a specific, testable regression rather
    than a general module question. See OQ-MODULEMARGINAL.

    **AXIS IS EXACTLY RIGHT ON GRIFFIN** — 0 bytes of error across 37 axis tags
    and 778,728 bytes, the largest single category in that file — and +7,928 on
    Elmsdale across 8 axis tags. That is a strong result for the axis model and
    it retires the "axis is unwired exposure" line in the candidate list above.

    **What the ladder does NOT resolve, and why nothing is being wired from it
    yet.** Two files is two data points. Three of seven categories disagree in
    sign between them, which is exactly the shape of a constant that is really
    a function of something not yet identified. Every constant this project has
    fitted from a collinear or two-point measurement has had to be unwound
    later. The next move is the missing third arm and the logic/shell split,
    specified in TASKS.md, not a refit.


4. **OQ-CTLSHELL** — new 2026-09-14, from the strip ladder. **A real export's
    bare controller shell costs ~2,400+ bytes that the engine prices at zero,
    and it is NOT the empty-project baseline constant.**

    | | actual | predicted | under |
    |---|---:|---:|---:|
    | `Griffin_Empty` (1756-L81E v35) | 21,096 | 13,296 | **+7,800** |
    | `Elmsdale_Empty` (5069-L330ERM v35) | 17,360 | 13,288 | **+4,072** |

    Both are genuinely empty: one Task, zero Programs, zero Tags, zero
    DataTypes, zero AOIs, one Module (the controller itself).

    **The baseline constant is right and must not be touched.** `Griffin_Empty`
    is 1756-L81E v35 — the exact platform every generated test file uses — yet
    `emptyroutine_n01`, a generated file on that same platform that carries a
    program and a routine `Griffin_Empty` does not, reads 18,884 and the engine
    is **byte-exact** on it, as it is on `emptyrungs_n00010/00100/01000`,
    `aoishape_control_empty` and `axis_baseline_motiongroup_only`. Raising the
    baseline by 7,800 would break every one of those.

    So the cost is in content a real export carries and a generated one does
    not. Present in both `Empty` files and priced at zero today: the
    controller's own `Module` element with real `EKey` / `Ports` / `Bus` /
    `EthernetPorts` configuration, `SafetyInfo`, `RedundancyInfo`, `Security`,
    `Trends`, `DataLogs`, `TimeSynchronize`, `CST`, `WallClockTime`, and (5069
    only) `QuickWatchLists`.

    The two platforms differ by **3,736** at empty where the engine has them 8
    apart. That does not contradict OQ-REAL5069's finding that a 5069 and a
    1756 carrying identical *content* have byte-identical residuals — that test
    used generated files, which carry none of the above — but it does mean the
    platform difference is larger on real exports than the wired constant, and
    OQ-REAL5069's conclusion should be re-read as "no per-platform *content*
    model is needed", not "the platform difference is fully wired".

    **Next measurement:** this is the cheapest high-value item on the board and
    it needs only two or three generated files, not a batch — a 1756-L81E v35
    empty project with (a) nothing added, (b) the controller's real
    `EthernetPorts`/`Bus` block copied in, (c) `Trends` + `DataLogs` +
    `QuickWatchLists` populated. If (b) or (c) moves the number, the term is
    identified in one capture round. This affects all sixteen real files
    uniformly. **The "worth 0.2–0.6% of real error" that used to end this
    sentence is withdrawn — measured 2026-09-18, charging it COSTS 0.09 points.
    Its value is ATTRIBUTION and the 3,736-byte platform gap, not the headline.**


5. **OQ-RUNGSHAPE** — new 2026-09-18, and it is the largest measured
    evidence gap in the project. **The compiled-logic weights were fitted on
    a rung shape that real ladder almost never has.**

    Measured across all sixteen real programs (41,136 rungs, 255,027
    instruction occurrences) against the 733 captured corpus files the logic
    weights were fitted on (525,936 rungs):

    | | real | fitted corpus |
    |---|---:|---:|
    | rungs containing a branch | **68.7%** | **9.4%** |
    | single-instruction rungs | **7%** | **62%** |
    | two-instruction rungs | 17% | 26% |
    | three-or-more-instruction rungs | **70%** | **12%** |

    Every instruction weight in the model is therefore calibrated on
    essentially unbranched, one-instruction rungs and then applied to a
    population where seven rungs in ten branch and seven in ten carry three
    or more instructions.

    **Every one of the top 25 real instructions is `FITTED`. None is
    `KNOWN`.** XIC, MOV, OTE and XIO alone are **160,469 of 255,027**
    occurrences (**63%**), and a 4-byte error across those four is **1.35
    percentage points** — the whole +1.375% residual.

    **CORRECTION, same day.** This entry first claimed a per-instruction
    operand-count gap — `TON` at 29% four-operand, `COP` across three, four
    and five, and a tail on eight others. **That finding was an artefact and
    is withdrawn.** It came from splitting operands on every comma, which
    counts `COP(Hist[0,0],Tmp[0,0],800)` as five operands and
    `TON(System_Fault_TMR[0,0],?,?)` as four. With bracket-aware splitting,
    **19 of the top 20 real instructions have operand counts the corpus
    already covers exactly** — every one is a single count at 100% on both
    sides. The only survivor is `JSR`, whose real calls run 2 to 16 operands
    against a corpus that is 100% two, and that is already the subject of
    `OQ-JSRPARAMCOST`. The splitter is fixed in `scripts/confound_check.py`
    and locked by a test.

    **What the corrected sweep does show, and it is a clean gap: 2-D array
    subscripts as instruction operands.** 2,364 of 254,703 real operand
    references (**0.93%**) carry a `[i,j]` subscript. The corpus has **zero**,
    across 942,157 operand references. That matches the tag survey in
    `OQ-TAGSHAPE`, where 2-D arrays are 0.16% of real tags and 0.00% of
    corpus tags. It is small, but unlike the withdrawn claim it is real.

    **What this does NOT yet explain.** Branch density cannot be the residual
    carrier: it is nearly flat across the sixteen (58.6%–76.1%) and correlates
    at only r = −0.250. The discriminating variable is the fraction of
    instructions sitting *inside* branches, which ranges 26.1%–45.2% and
    correlates at **r = −0.732** against residual bytes — the second-strongest
    correlate in the file after routine count.

    **A two-term fit reaches the target and MUST NOT BE WIRED.** Adding +11
    bytes per series instruction and −15 per in-branch instruction takes the
    sixteen from mean 1.5607 / max 3.6309 / 4 inside 1% to **mean 1.0820 /
    max 2.8894 / 10 inside 1% / 13 inside 2%**. It is recorded here only so
    it is not rediscovered and mistaken for a result. It is two free
    parameters fitted to sixteen points, the per-unit costs it rests on have
    CV **1.87** and **1.55** — neither identifies a value — and no mechanism
    predicts a negative cost for being inside a branch. Wiring it would be
    fitting the held-out set, which destroys the only accuracy evidence the
    project has.

    **THE MEASUREMENT THAT SETTLES IT — a spec, not files.** What is needed is
    a rung-shape sweep at the real population's shape, holding instruction
    inventory fixed and varying only the arrangement:

    - Fix the multiset of instructions per file (same opcodes, same counts,
      same operand types) and vary ONLY how they are arranged: all-series,
      all-parallel, and the real 68.7%/70% mix. Differencing consecutive
      points isolates the arrangement term with the inventory cancelled.
    - Sweep branch leg count at fixed total instruction count, so leg count
      and instruction count are not confounded.
    - Sweep instructions-per-rung at fixed total instruction count (1,000
      instructions as 1,000 rungs, 500, 200, 100), which prices the per-rung
      term separately from the per-instruction term.
    - Include the untested operand shapes above, one per file: four-operand
      `TON`, four- and five-operand `COP`.

    Every file must still be 1756-L81E at v35 per the platform rule, and
    every consecutive pair must differ in exactly one dimension. **Do not
    generate these without asking** — CLAUDE.md step 7.

    **This supersedes the strip-ladder route.** Attribution by subtraction
    from a real export is dead (see the read-only rule in `CLAUDE.md`), so a
    built-from-scratch sweep at the real shape is now the only way to price
    arrangement.

    **BATCH GENERATED 2026-09-18 — 14 files, `rshape_*`, all 1756-L81E v35,
    all lint clean, every consecutive pair differencing on exactly one
    dimension (`python scripts/confound_check.py --family '^rshape_'`).**
    Predictions PRE-REGISTERED below, before any capture, so the batch can
    falsify the engine rather than be fitted to it.

    | file | predicted | step | what the step prices |
    |---|---:|---:|---|
    | `rshape_arr_legs01_n00500` | 42,904 | — | 8 XIC in series + OTE, 500 rungs |
    | `rshape_arr_legs02_n00500` | 48,904 | +6,000 | 2 legs of 4 → **+12/rung** |
    | `rshape_arr_legs04_n00500` | 52,904 | +4,000 | 4 legs of 2 → **+8/rung** |
    | `rshape_arr_legs08_n00500` | 60,904 | +8,000 | 8 legs of 1 → **+16/rung** |
    | `rshape_pack_i{01,02,04,08,16}` | **434,112 each** | **0** | 4,000 OTEs at 1/2/4/8/16 per rung |
    | `rshape_mix_series_n00500` | 39,312 | — | real composition, all series |
    | `rshape_mix_branch_n00500` | 44,712 | +5,400 | same multiset in legs → +10.8/rung |
    | `rshape_sub2d_a_flat_n00500` | 37,884 | — | flat `DINT[400]`, `[i]` |
    | `rshape_sub2d_b_decl_n00500` | 39,568 | +1,684 | 2-D declaration, unreferenced |
    | `rshape_sub2d_c_ref_n00500` | 39,568 | **0** | `[i,j]` subscript instead of `[i]` |

    **Two of those are the sharp ones.** Group B says the engine charges
    **nothing** for rung count at a fixed instruction inventory — all five
    files predict the identical 434,112 over 4,000 OTEs packed from 1 to 16
    per rung. If the captures differ at all, there is a per-rung term the
    model does not have, and that is the 62%-versus-7% gap turned into a
    number. Group D says the engine charges **nothing** for a 2-D subscript
    over a 1-D one; the declaration alone is 1,684.

    Group A's own steps are already non-monotone under the current model —
    +12, +8 then +16 bytes per rung for 2, 4 and 8 legs — which is the
    `branch_bracket_cost_per_instruction` term extrapolating outside the
    9.4%-branched corpus it was fitted on. A smooth measured curve there
    would falsify it directly.

    **CAPTURED 2026-09-18. Three of the four groups came back BYTE-EXACT, and
    the fourth is confounded by my own design error.**

    | group | result |
    |---|---|
    | **A** arrangement at fixed inventory | **all four exact, delta 0** at 1, 2, 4 and 8 legs |
    | **B** rung packing | **−12 per unit at all four points — but see below** |
    | **C** real rung composition | **both exact, delta 0**; the series/branch step of −5,400 is predicted to the byte |
    | **D** 2-D subscripts | +4 / +8 / +8 — inside the universal ±8; the subscript step is **exactly 0** |

    **GROUP A CLOSES THE BRANCH QUESTION, NEGATIVELY.** The predicted steps of
    +12, +8 and +16 bytes per rung looked like a term extrapolating badly
    outside its 9.4%-branched calibration. They are correct to the byte at
    every leg count. Group C confirms it at a realistic rung composition
    rather than a uniform 8-condition rung. **So the 68.7%-versus-9.4% branch
    coverage gap is real as a coverage fact and is NOT an error**: the
    arrangement terms already in the model price real-shaped ladder exactly.
    That removes the largest suspected error source in compiled logic.

    **GROUP B DOES NOT MEASURE WHAT IT WAS BUILT TO MEASURE.** It was supposed
    to isolate a per-rung term by holding the instruction inventory fixed at
    4,000 OTEs and varying only how many rungs they sit in. OTE was chosen
    because its isolated weight is confirmed exact — but **OTE is an OUTPUT
    instruction**, so packing more per rung builds a series-output cascade,
    which `OQ-SERIESOUTPUT` already prices at −12 per output beyond the first.
    In this design the two are not merely correlated, they are the same
    number: extra series outputs equals the rung-count drop **identically in
    every file**.

    | file | rungs | OTE/rung | extra outputs | rung-count drop | delta | per unit |
    |---|---:|---:|---:|---:|---:|---:|
    | `i01` | 4,000 | 1 | 0 | 0 | 0 | — |
    | `i02` | 2,000 | 2 | 2,000 | 2,000 | −24,000 | **−12.000** |
    | `i04` | 1,000 | 4 | 3,000 | 3,000 | −36,000 | **−12.000** |
    | `i08` | 500 | 8 | 3,500 | 3,500 | −42,000 | **−12.000** |
    | `i16` | 250 | 16 | 3,750 | 3,750 | −45,000 | **−12.000** |

    The series-output reading is much the likelier of the two, because −12 is
    the value `OQ-SERIESOUTPUT` already measured on two unrelated shapes; a
    per-rung term would have to coincide with it exactly. Either way **the
    rung-packing question stays open**, and the confound-checker did not catch
    this one because both readings are the same single dimension in the
    profile — a reminder that the checker verifies that one thing moves, not
    that the one thing moving is the thing you meant.

    **THE CORRECTED SPEC, 5 files, not yet generated.** Hold the total
    instruction count fixed and keep the output count fixed at one per rung,
    so no cascade can form: each rung is `XIC(a)...XIC(z)OTE(out_r)`, with
    4,000 XICs distributed 1, 2, 4, 8 and 16 to a rung. The OTE count then
    tracks the rung count rather than being held fixed, so the pair must be
    differenced against group A — which prices XIC arrangement exactly — to
    subtract it. Failing that, a two-arm design varying XIC-per-rung at fixed
    rung count in one arm and rung count at fixed XIC-per-rung in the other.

