# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md`. One line each here — full derivation is in
the matching footnote at the bottom, not inline.


2. **OQ-CMPCPTLAYOUT** —
    **A SECOND THREAD FOUND AND WIRED 2026-09-13 (capture-batch segment 12,
    `cpttier_*`): `per_extra_same_tier_operand` was only ever a TIER-1 rate.**
    Its 24 came from `cptcx_operandcount_n01..n10`, which uses the same ADD
    operator throughout, and it was being applied to every uniform-tier
    expression. Uniform tier-2 expressions read:

    | MUL/DIV/MOD operators | engine (24) | real | under-charge |
    |---:|---:|---:|---:|
    | 1 | 140 | 140 | 0 (`cmpcpt_cpt_op_{mul,div,mod}`) |
    | 3 | 188 | 220 | **+32** |
    | 4 | 212 | 260 | **+48** |

    16 per operator beyond the first, with a single tier-2 operator already
    exact to pin the intercept, so the tier-2 rate is 24 + 16 = **40** — exact at
    both counts and both rung counts, four rows, zero residual. Tier 1 stays 24
    (`cpttier_k3_t1x3` and `k4_t1x4` were already exact). `cpttier_*` rows landing
    exactly went **10 of 22 → 14 of 22**, within ±8 **14 → 18**.

    **TIER 3 IS DELIBERATELY LEFT ON THE TIER-1 FALLBACK, because two shapes at
    the same operator count disagree by 40.** `cptpow_p2` reads −16/rung and
    `cptpow_p3` −12/rung, while `cptpow_p2_adjacent` reads **+24/rung** — same
    two `**` operators, different adjacency. So adjacency of `**` is an unmodelled
    term of its own worth 40 bytes, and setting any uniform tier-3 rate would fit
    one of those shapes and break the other. `cptpow_p1`, `p1_t1x1` and `p1_t2x1`
    are all exact, so a single `**`, alone or mixed with one other tier, is right.

    **What is left in the two-tier mix path is ±4 and below the band.** After the
    tier-2 wiring the only non-exact `cpttier_*` rows sit at exactly +4/rung:
    `t1x2_t2x1` and `t1x2_t2x2` (the two non-nested mixes with tier-1 count
    exactly 2), plus `nested_t1x1_t2x2` (whose non-nested twin is 0) and
    `nested_t1x2_t2x1` (whose twin is also +4). Read as a tier-1-count effect it
    is 2 shapes of 5; read as a nesting effect it is 1 of 2. Four bytes, two
    shapes each way, inside the project's ±8 residual band — recorded, not
    fitted.

    **The `cmpfl_*` float-literal arm stays open and is not derivable from what
    exists.** All 13 rows are single-rung files, so each is one point with no
    slope: 0, 0, +8, +16, +16, +32, +32, +48, +52, +52, +92, +108, +116. That is
    the non-monotonic REAL/float-literal interaction this entry already describes
    as needing dedicated architecture rather than more raw points, and 13 isolated
    points cannot separate operand type from operator tier from literal count.

    The original thread, for the record, unchanged below.

2b. **OQ-CMPCPTLAYOUT, the original entry** — down to one thread. Uniform, T1+T2, T1T3/T2T3,
   and (as of 2026-08-29) the all-3-tier mix are ALL solved and wired,
   confirmed exact on every real data point on file. Only the REAL-
   operand/float-literal interaction remains open, and it's now a harder
   problem than "assumed linear, awaiting more points" — real new data
   shows it's genuinely NOT monotonic in operand count, ruling out any
   simple per-count model. 2026-08-30: the 12 `cptmix_*` probe files
   (float1/real1/real2/real3 position/adjacency/nesting variants) got
   real captures in the latest push — all land within 0.7-1.3% (188-272
   bytes on ~20,500-byte totals), small and real but too tight/consistent
   across position/nesting variants on their own to isolate a clean new
   term from; still needs the dedicated architecture work, not more raw
   points.[^cmpcpt]

   **2026-09-12: the thread above is CLOSED, and the entry's numbers were
   stale.** All 65 captured `cptmix_*` rows were live-recomputed against the
   current engine: **63 land at exactly 0**, and the other two at −4
   (`scaling_grouped_n05`) and −16 (`scaling_t1t3/t2t3_alternating_n08`),
   both inside the project's universal small-residual band. The "0.7–1.3%,
   188–272 bytes" figure predates later wiring and no longer describes any
   file. Every REAL-operand and float-literal probe the batch was built for
   — `real1_float1`, `real2/real3_adjacent_float1`, `float1_pos_*`,
   `disentangle_*`, `stacked_dint_floatliteral`, `realcheck_real` — is
   exact. The non-monotonicity that made it look hard was the pre-refit
   two-tier rate, and the 2026-09-04 split-by-tier refit removed it.

   **WIRED 2026-09-12, a different and structural gap found by the same
   reconciliation: CMP had no expression model at all.** CPT has been priced
   from its own expression's operators since 2026-08-23; CMP was priced as a
   flat weight plus two boolean surcharges (compound, float-literal). So a
   CMP whose operands are themselves arithmetic expressions was charged as
   though they were bare tags — `CMP(L0+L1>L2)` paid nothing for the `+`.
   Every bare-tag and bare-literal CMP shape in the corpus measured exact;
   every arithmetic one carried a real negative residual, and nothing
   connected the two facts.

   The fix routes CMP's arithmetic operators through **CPT's own
   operator-tier table with no separate CMP fit** (`cost_for(operators) −
   base_read`, since CMP keeps its own 76-byte base weight). The tiers
   fitted on CPT land on CMP's measured residuals as they are — which is the
   evidence that CMP and CPT share one expression law rather than that a
   constant was tuned:

   | CMP shape | was | now |
   |---|---:|---:|
   | `L0+L1>L2` | −36 | **+0** |
   | `L0+L1>5` | −36 | **+0** |
   | `(L0+L1)*L2>L3-L4` | −100 | **+0** |
   | `L0+L1>L2+L3` | −64 | −4 |
   | `(L0+L1)>L2&&(L3-L4)<L5` | −64 | −4 |
   | `L0*1.5>L1+2.5` | −128 | −52 |

   Comparison operators and the `&&`/`||` connectives are deliberately not
   tokenized as arithmetic — the connective is already priced by
   `compound_cost`, and double-charging it would break every bare compound
   CMP, all of which measure exact. Corpus exact predictions 1,028 → 1,031.

   **Two residuals survive, and 47 files were built for exactly those two**
   (`src/sample_gen/gen_cmpcpt_expr_closeout.py`):

   - **A, `cmpfl_*`** (13 files). The −52 on `L0*1.5>L1+2.5`.
     `cmp_surcharge.float_literal_cost` (72) is charged once per call as a
     BOOLEAN, fitted on one shape (`CMP(L0>5.5)`, no arithmetic, exact). The
     surviving −52 says the boolean breaks once there is more than one float
     literal or once a float sits inside an arithmetic sub-expression, and
     one file cannot say which — nor whether the rate is per-literal (72 is
     then wrong, since 128−76 = 52) or a float-context promotion of the
     operator tiers. Float-literal count is swept 0..3 at fixed arithmetic
     operator count, plus a **REAL-TAG arm** (`CMP(R0+R1>R2)`, no literal
     anywhere) that separates "a float literal costs something" from
     "evaluating in floating point costs something". The corpus has no data
     on the REAL-tag case at all.
   - **B, `cpttier_*`** (22 files). The −4 on `L0+L1-L2*L3` and
     `(L0+L1)*(L2-L3)`, and the matching −4 on two 2-operator CMP shapes.
     4 bytes would be noise except it scales exactly:
     `cptcx_spotcheck_mixedops4op_n100` is 100 rungs of the first shape and
     lands at −400. It is also not simply "mixed tiers" — every
     `cptmix_pair_t1t2_*` file mixes tier 1 with tier 2 and measures exact.
     Tier composition is swept at **fixed operator count** (3 and 4
     operators, every tier split), each shape at n=1 and n=100 so a per-rung
     term shows as −400 and a per-file offset stays at −4. The existing files
     vary count and composition together, which is why this was never
     separable. Shares its answer with **OQ-CPTARRANGE** (now closed and
     archived in `docs/RESOLVED_QUESTIONS.md`), where the same
     four −4 rows are already recorded.
   - **C, `cptpow_*`** (12 files). `CPT(Dest,L0**L1+L2**L3)` is the only
     shape in the corpus that OVER-predicts (+16), and `**` is the only
     tier-3 operator (116 against tier 2's 52), so an error there costs 2–3×
     what one costs anywhere else in the table. Two `**` in one expression is
     untested, and `cptrdpow_k2/k3` (−848/−1648) say repeated `**` is badly
     wrong on the REAL-destination path too. Swept 1..4 `**` operators, alone
     and mixed with tier 1, at n=1 and n=100.

3. **OQ-AOIDEFSHAPE** — one unexplained 8 bytes in the AOI-definition cost.
    Opened 2026-09-13 (capture-batch segment 4), replacing the four separate
    fitted terms that used to absorb it. **54 files built, awaiting capture.**

    The definition cost is now one itemised form (`memory_model.yaml
    aoi_definition`):

        base 1163
        + 12 per declared member
        + that member's OWN data bytes (0 for a scalar BOOL, element x
          dimension for an array, the structure's size for a TIMER/STRING/UDT)
        + 24 per 32-bit word the declared BOOLs occupy, counting
          EnableIn/EnableOut as two further bits
        + the members' names, pooled with one byte per name and rounded up to 8
        + name_length_bytes(the AOI's own type name)

    Measured on 124 captured def-only files -- an AOI definition with no
    instance tag anywhere and no internal rungs, so the definition is the only
    AOI cost in the file and its true value reads straight off the capture.
    They span 1 to 128 declared members, six atomic types, BOOL fractions 0 to
    100%, and Input, Output and LocalTag usages. **70 of the 124 land exactly,
    122 of 124 within the project's ±8 band, worst 11.**

    Effect of wiring it, live-recomputed: corpus rows landing EXACTLY went
    **1,120 → 1,198** and rows inside ±8 went **1,690 → 1,907**. Per category,
    within 1%: `aoi_array_packing` **283/283** (was 35 of 283 inside ±8),
    `aoi` **160/160**, `axis` **61/61**, `driveaxis` **15/15**, `aoi_reqvis`
    **9/9**, `aoistructure` 105/110, `defscale` 60/69. On the sixteen real
    programs mean |error| 2.16% → **2.13%**, and `griffin_stackerline` went
    from 394 bytes out to **94** on 2.36 MB. The real-file residual also went
    one-sided: 14 of 16 now under-predict, where it used to be split.

    **What each superseded term was really measuring**, kept because every one
    of them fitted its own sweep exactly and was still the wrong shape:
    `per_declared_item: 20` was 12 + the 4 data bytes of the DINT every count
    sweep happened to use; `per_type_rate` (BOOL 16, SINT 18, INT 18, LINT 24)
    was the same 12 + own-size relation seen through the old linear name term;
    `member_name_char_bytes: 1` with 3 free chars was a pool rounded to 8
    misread as a per-character rate; and `aoi_member_type_extra`'s REAL 0,
    TIMER 8 and COUNTER 8 are exactly (own size − 4), with its
    sum-then-floor-to-8 shape an artifact of that mis-attribution. The
    mixed-versus-single-type split went with them: per-type rates "did not
    compose additively once BOOL sat alongside another type" because the
    name-pool error showed up as a composition effect.

    **WHAT IS LEFT.** A residual of exactly 0 on 70 of the 124 instrument
    files and exactly +8 on 35 more. It is not usage, not member count, not
    composition and not type. Three candidates remain and every captured file
    confounds at least two of them:

      1. **The AOI type-name bucket boundary.** The wired law
         `8*max(0,(len-8)//4) - 8` was fitted 7/7 on lengths 8, 9, 13, 16, 20,
         25 and 30, leaving 10-12, 14-15 and 17-19 unsampled. Two pairs
         differing only across those gaps disagree by exactly 8:
         `paramcount_n04_def_only` (13 chars) vs `_v2` (15) — the name is the
         ONLY difference in the whole file — and
         `aoidefcost_typeint_n08_def_only` (16) vs
         `paramtype_dint_n8_def_only` (14), same 8 DINT params, same member
         names, 8 bytes apart.
      2. **A fixed offset inside the name pool before it rounds.** On the
         `localcount_*` family the +8 appears exactly when the character total
         is congruent to 0, 6 or 7 mod 8 and not when it is 3 or 4, which is
         what an `8*ceil((chars + 4)/8)` pool would do. That fits all six
         localcount points and then contradicts `aoidefcost_typeint_n08`.
      3. **Member ORDER.** `aoi_boolpack_clean_alternating_def_only` (0) and
         `aoi_boolpack_clean_grouped_def_only` (+8) are the same 10 BOOL + 10
         DINT with the same member names in a different order.

    `base` is set to the value that centres the residual on zero for the
    124-file instrument (total absolute residual 316 bytes). A base 8 higher
    scores about 86 more exact rows corpus-wide and 53 more inside ±8, which is
    recorded here rather than taken: it makes the isolating instrument strictly
    worse, and it would bury the term this question exists to find.

    Two smaller things measured and deliberately not fitted, for the same
    reason: **STRING**'s old rate of 84 is 2 more than its 86 bytes minus 4
    (its capture, `altype_string_n00010_def_only`, reads −2 — inside the
    band), and **MOTION_INSTRUCTION**'s old 12 is 4 more than its 12-byte size
    predicts (`altype_motion_instruction_n00010_def_only` reads **+44**, the
    largest residual left in the array-localtag families).

    **Files built 2026-09-13, awaiting capture** —
    `src/sample_gen/gen_aoidefshape_closeout.py`, 54 files, every one def-only:

    - **A, `aoidshape_tname_len{08..32}`** (25 files). The AOI type name at
      every single length 8 to 32, with 4 DINT Input parameters named P0..P3
      held byte-for-byte identical, and **the controller name pinned to one
      fixed string across all 25** — which the existing `aoiname_len*` sweep
      did not do: there the project name tracked the AOI name, so a
      project-name cost was invisible. Reads candidate 1 directly at every
      length instead of at 7 of them.
    - **B, `aoidshape_pool_c{06..21}`** (16 files). Member-name character
      total growing one character at a time across two complete 8-byte residue
      cycles, with member count, types, data bytes and the type name all
      pinned. Only the pool's input moves, and every residue is read twice.
      Settles candidate 2.
    - **C, `aoidshape_count_n{01..08}`** (8 files). Member count 1 to 8 with
      single-character names, so the character total stays inside one 8-byte
      chunk for n=1..4 and the next for n=5..8. Separates the
      `localcount_n01` (0) vs `localcount_n02` (+8) step from the pool offset.
    - **D, `aoidshape_order_{boolsfirst,dintsfirst,alternating,pairs,
      blocks5}`** (5 files). 10 BOOL + 10 DINT in five arrangements with
      identical names and one pinned type name, so composition, count, pool
      and word count are identical by construction and any spread is
      candidate 3 and nothing else. The current engine predicts the same
      19,664 bytes for all five, which is what makes it a clean instrument.

4. **OQ-SAFETYSCOPE-SIZING** — Task/Program/Routine SHELL sub-thread
   **decided and wired 2026-09-03**: safety tasks and safety programs are
   a separate memory pool and need their own sizing calculation.
   `report.py` now excludes Safety tasks/programs/routines from the
   ordinary `task_program_shell` aggregate entirely and charges a new
   flat `safety_task_program_shell` (296 bytes/file, see
   `memory_model.yaml`) once per file with at least one Safety task
   instead, replacing the old +1,456-byte ordinary-shell overcharge.
   Live-verified against all 24 real L81ES-L84ES fwmatrix rows: exact (0
   delta) at fw v31-v33, a known +16-byte (0.087%) residual at v34-v38
   (real SafetyProgram MainRoutine content apparently drops to 0 bytes on
   that firmware; this engine still predicts a firmware-independent 16 —
   a separate, tiny, content-side gap, not a shell gap, well inside the
   <1% North Star, not chased further).

   **Still genuinely open, separate sub-thread, NOT covered by the above
   decision**: whether resolvable Safety-CLASSED TAG content (`DCI_STOP`,
   real corpus evidence, 80 bytes; `CONFIGURABLE_ROUT`, wired 52 bytes but
   Safety-family by name-root) should be sized at all. The tool already
   warns rather than refuses on a Safety-rated project
   (`is_safety_project`, cli.py/ui/server.py), but these two Safety-classed
   tag types are still left unsized by convention, not by any code that
   enforces the exclusion. the shell decision doesn't resolve this —
   it was specifically about Task/Program/Routine containers, not tag
   content. Still needs a call: exclude Safety-class tags from sizing
   everywhere by design (and wire that exclusion explicitly), or size
   everything resolvable including Safety tag content and adjust the
   warning wording.[^safetyscope]

5. **OQ-AOIARRAYLOCALTAG** (was the open sub-thread of
   OQ-AOIARRAYDIMENSION, whose import-failure thread closed 2026-09-03 and
   is now in RESOLVED_QUESTIONS.md) — an AOI array LocalTag's DIMENSION was
   unpriced. **All 27 sweep files were captured 2026-09-03 and never
   reconciled. Reconciled and the main term WIRED 2026-09-11; four smaller
   things stay open and are measured by a new 20-file batch.**

   `aoi_definition` charged `per_declared_item` once per declared member
   regardless of `dimension`, so an array member's data space cost nothing.
   Against a prediction that was FLAT at every dimension:

       DINT dim   10    50   100    250    500   1000
       deficit   -41  -201  -401  -1001  -2001  -4001

   Exactly `element_size x dimension`, and by element type at dimension 50:
   SINT 1.0/element, DINT and REAL 4.0/element. Definition-side only — every
   `_1_instance` twin carries the same deficit, so an instance does not pay it
   again. Now wired through `compute_array_size` (not element size x
   dimension: CAM_PROFILE is a predefined ARRAY structure with no scalar
   element size, real programs declare ten of them, and it raised
   `UnknownDataTypeError` on the first real file the new term met). 27 rows
   went from -41..-4001 to inside +-4 on 20 of them.

   **Exposure, measured before deciding how much to spend on it:** array
   LocalTags are ~17 KB across the sixteen real programs — **0.036%**, worst
   single file 0.058%. Real-file mean |error| moved 2.1733% -> 2.1504%. This
   category will never be the reason a real file misses 1%, and the 20-file
   batch below is sized accordingly. It exists because unexplained rows sit
   inside a category that otherwise measures exactly, which is how a wrong
   constant gets adopted — not because the bytes are large.

   **Still open, and `gen_aoi_arraylocaltag2.py` (20 files) measures each:**

     - **BOOL, deliberately left unpriced.** `BOOL[50]` measured -13, which
       fits neither the 7-byte packed size nor an 8-byte two-word rounding.
       `albool_n{1,8,16,32,33,50,64,65}` walks the packing boundaries. Real
       programs do declare BOOL array LocalTags (2, 64 elements).
     - **An 8-byte discount per array member after the first.** 1/2/3 arrays
       of 50 DINT measured 200/392/592, not 200/400/600 — 196 per array after
       the first. Two points cannot say whether that is linear;
       `almult_n{04,06,08}` settles it. After wiring, n02/n03 sit at +8.
     - **Structure element types, never tested.** The sweep covered five
       atomics. Two thirds of the real exposure is MOTION_INSTRUCTION (16
       arrays / 112 elements), CAM_PROFILE (10 / 100), STRING (4) and TIMER
       (2). `altype_*_n00010` prices one array of each of six structure types.
       The dimensioned-structure LocalTag shape (no `Radix`, no data body,
       unlike a dimensioned atomic which keeps `Radix="Decimal"`) was taken
       verbatim from the real exports before building any of them.
     - **The dim=25 outlier.** Every other dimension lands at -1 after
       wiring; 25 lands at +3 — four bytes, exactly one element, off the line
       through 10 and 50. The file's XML does declare `Dimensions="25"`, so it
       is not a generator bug. `aldim_n000{24,25,26}` re-measures it with its
       neighbours: either a real granularity effect near there, or the
       original row was a capture artefact.

   `INT[50]` at -99 against its predicted 100 is the fifth loose end and is
   covered by the same wiring note rather than a file of its own: the
   existing INT row already brackets it, and the multiplicity and neighbour
   arms above test the two mechanisms (a per-array term, or 4-byte
   granularity) that could produce it.

    **CLOSED 2026-09-14 (segments 25-28). 20 rows across four families, nineteen
    in or within 12 of the +-8 band, and the model needs no change.**

    - **`aldim_n000{24,25,26}_def_only`** -- array dimensionality is free:
      +4 / 0 / +4.
    - **`almult_n0{4,6,8}_def_only`** -- multiple array local tags are additive:
      +8 flat at all three counts.
    - **`altype_*_n00010_def_only`** -- per element type, all in band: CAM_PROFILE
      0, STRING -2, CONTROL / COUNTER / TIMER +4 each. **MOTION_INSTRUCTION is the
      one real gap at +44**, which is consistent with it being an unmodelled
      predefined structure (OQ-PREDEFINED) rather than anything about array local
      tags.
    - **`albool_n*_def_only`** -- +4 for n = 1..32 and +12 for n = 33..65. One
      8-byte step at the 32-bit word boundary and **no second step at 64**, so it
      is not a per-word term, and a single occurrence of a step cannot be
      generalised. 8 bytes, recorded not wired.


6b. **OQ-MODULESTRUCTURAL** — NEW, 2026-09-04, and it changes the target
   for OQ-MODULEIO below. The target application is testing an unknown
   file, and every catalog module number cannot be captured
   individually — the model has to tell that a 16pt digital
   card has XX overhead + 16pts of data, whereas a 8pt analog card has
   different overhead."*

   The per-catalog `module_overhead_by_catalog` table is the wrong shape
   for the real goal. It can only ever cover catalogs we have personally
   captured; a real customer file will contain catalogs we've never seen,
   and those silently fall back to one flat cross-catalog default (1,672)
   that is badly wrong for whole families (the 5069 family sits +28% to
   +35% under-predicted on that default). The table should become a
   FALLBACK for known-exact catalogs, not the primary mechanism.

   What's needed instead: predict a module's overhead from its own
   STRUCTURE, which is already in the L5X and already parsed. First look
   at the evidence, 2026-09-04:
   * A naive structural regression (constant + module count + connection
     input/output/config bytes + module_defined_bytes) over the 98
     error-free single-module `modulesweep_*` captures lands at MAE 845
     bytes / 3.84% mean — better than nothing but not close to the <1%
     target, because it lumps genuinely different module CLASSES (simple
     discrete I/O, analog, drives, safety, network bridges) into one
     linear model.
   * The missing variable is class, and Rockwell already states it: every
     module carries its own PROFILE string on its Input/Output/Config tag
     (`ModuleInfo.input_profile` etc., already parsed since 2026-08-27).
     `AB:1756_DI:I:0` is "1756 digital input", `AB:1756_DO:C:0` is
     "1756 digital output config", `AB:1734_8SLOT:I:0` is an 8-slot
     PointIO adapter, `AB:MotionDevice_Diagnostics:S:0` a drive. This is
     catalog-INDEPENDENT and exactly the "16pt digital vs 8pt analog"
     axis needed here -- 1756-IA16 and 1756-IB16 are different
     catalogs but both `AB:1756_DI`. Across the 98 valid files there are
     143 distinct profile strings resolving to a much smaller set of
     class tokens (DI, DO, IB, OE, OF, SLOT, ...).
   * Point count is recoverable the same way (the `_16` / `_8SLOT`
     numeric token, cross-checkable against the real connection byte
     counts already parsed).

   Proposed model shape, NOT yet fitted or wired:
       overhead = class_base[profile_class] + per_point[class] * points
                  + per_connection_byte * (in + out + cfg)
   fitted per class from the single-module captures, with the existing
   per-catalog table kept as an exact-match override where we have real
   data. This is the single highest-value remaining architecture change
   for the North Star, because it is what makes an UNSEEN catalog
   predictable at all.


    **THE CONCRETE CASE, found 2026-09-12.** Counting every non-CPU module
    across the sixteen real programs gives 438, and the largest single catalog
    by a wide margin is the GENERIC `ETHERNET-MODULE` profile at **109
    instances -- 25% of them**. It has NO entry in
    `module_overhead_by_catalog`, so all 109 fall back to the flat 1,672-byte
    cross-catalog default.

    A per-catalog constant is not merely imprecise for it, it is the wrong
    SHAPE. ETHERNET-MODULE is the profile used for any EtherNet/IP device with
    no AOP: the connection sizes are typed in by hand, so two instances of the
    same "catalog" are different devices. The 109 real instances carry **40
    distinct connection shapes**, primary input spanning **2 to 450 bytes** (a
    225x range) and output 2 to 64:

        x11  In  10  Out  4        x6   In  6  Out 2
        x10  In 450  Out  8        x5   In 12  Out 2
        x9   In   4  Out  2        x5   In  4  Out 6
        x7   In  64  Out 64        x4   In 14  Out 2
                                   x4   no connections at all

    Five more generic or third-party profiles are missing from the table on the
    same terms: `193-ECM-ETR/B` (20 uses), `PowerFlex 525-EENET` (12),
    `ETHERNET-BRIDGE` (8), `DPI-DRIVE-PERIPHERAL-MODULE` (6),
    `ETHERNET-PANELVIEW` (2). **161 of the 438 real modules -- 37% -- are
    priced by the flat default.**

    **The rack sweeps say the same thing from the other direction.** All 57
    `rack_*` rows captured clean, and none was ever reconciled. Recomputed
    2026-09-12, the per-module error FLIPS SIGN by family:

        1756 chassis cards   +523 per module (over-charged), max resid 1,436
        5069                 -992 per module (under-charged), max resid 5,831
        POINT I/O / Flex     -932 per card   (under-charged), max resid 3,008
        5069 singles          ~0 slope, but per-CATALOG residuals to 4,005

    Worst rows are `rack_pointio_n15_full` at **-27.8%** and
    `rack_5069_rand03` at **-25.4%**, while `rack_1756_n16_full` is
    **+11.8%** -- and `rack_5069_rand_combined10` (74 modules) flips to
    **+7.0%**, so it is not even monotone in count. A flat per-family constant
    does not absorb those residuals either. Those three families are only 14%
    of the real module population, so they are a large CORPUS error and a small
    real-file one; ETHERNET-MODULE is the reverse.

    **Test files built 2026-09-12, `gen_generic_ethernet_module.py`, 19
    files.** The module block is transplanted from a real instance; only
    identity and the swept size differ. Sizes are in BYTES and the connection
    data is INT-typed, so the array dimension is bytes/2 and the
    `AB:ETHERNET_MODULE_INT_<n>Bytes` type name carries the byte count -- all
    three move together in a real export, so they are derived from one number
    rather than settable apart and drifting out of agreement.

      - `genem_in{002..450}` (8) -- primary INPUT size swept
        2/4/10/32/64/128/256/450 bytes at output 4, bracketing the whole real
        range including both extremes.
      - `genem_out{002..064}` (6) -- primary OUTPUT size swept at input 4.
        Separates the two directions, which no real instance can do because
        real devices vary both at once.
      - `genem_n{01,02,04,08}` (4) -- OQ-MODULEMARGINAL's per-module question
        for the one catalog where it matters most on a real file.
      - `genem_dt{sint,int}_008` / `genem_dt{sint,int,dint,real}_064` /
        `genem_dt{sint,int}_450` (8) -- element DATA TYPE crossed with byte
        size, which nothing in the corpus can separate. Real generic modules
        use three element types (INT on 130 connections, SINT on 80, DINT on
        2) and the same byte size appears under different ones -- 450 bytes as
        SINT in 14 real instances, 64 bytes as INT in 14 -- but no real pair
        holds bytes fixed while the type changes. If cost follows ELEMENT
        COUNT rather than byte count, SINT and INT at one size differ by 2x
        and DINT/REAL by 4x: `genem_dtsint_450` declares 450 elements against
        `genem_dtint_450`'s 225 for the identical 450 bytes. The engine
        predicts an identical total for every file in this arm, so the whole
        captured difference is the type effect. REAL is the one type with no
        corpus instance -- a legitimate comm-format choice with mechanical
        `AB:ETHERNET_MODULE_<TYPE>_<n>Bytes` naming, so a conversion failure
        there would be a finding about the shape rather than the cost.
      - `genem_noconn` (1) -- the no-connection shape four real instances have.
        `zero_connection_module_bytes` (2,344, FITTED) claims to cover it and
        has never been tested for this profile.

    The engine currently charges **exactly 1 byte per connection byte** on top
    of the flat overhead (20,206 at input 2 rising to 20,654 at input 450), so
    the input sweep tests that claim directly and the 450-byte case -- ten real
    instances -- is where a wrong rate would show most.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.


    **ETHERNET-MODULE SOLVED 2026-09-13 (capture-batch segment 7), which is the
    single largest slice of this question.** That profile is 109 of the 438
    non-CPU modules in the sixteen real programs — 25% of them — and had no
    entry in `module_overhead_by_catalog` at all, so every one fell back to the
    flat cross-catalog 1,672. A per-catalog constant was never the right SHAPE
    for it: the connection sizes are typed in by hand, and the 109 real
    instances carry 40 distinct connection shapes with input spanning 2 to 450
    bytes.

    **A connection's data costs 4x its declared bytes, not 1x.** Each direction
    is rounded up to a 4-byte word, the two word counts are summed, and the
    block costs 16 per word less 8 when that total is odd:

        W = ceil(input_bytes / 4) + ceil(output_bytes / 4)
        connection_bytes = 16 * W - 8 * (W % 2)

    | W | 2 | 3 | 4 | 5 | 9 | 17 | 33 | 65 | 114 |
    |---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
    | bytes | 32 | 40 | 64 | 72 | 136 | 264 | 520 | 1032 | 1824 |

    EXACT on all 14 points, with the catalog's own overhead at **1,592** and its
    400-byte config array charged as declared. **The two directions are
    interchangeable**, which no real instance could show because real devices
    vary both at once: `genem_in032`/`genem_out032` are byte-identical captures
    (20,256) and so are `genem_in064`/`genem_out064` (20,384). Only the sum of
    the word counts matters.

    20 of the 24 captured `genem_*` rows now land exactly, from none. Corpus mean
    absolute error 1.545% → 1.536%; the sixteen real programs 2.074% → **2.025%**.

    Scoped to this profile deliberately. The rack sweeps point the same way (5069
    −992/module, POINT I/O −932/card, both under-charged), so a 4x connection
    cost may well be general — but applying it to all 325 captured module rows on
    one profile's evidence is the move this project has had to undo before.

    **AND TWO OF THAT BATCH'S FOUR ARMS MEASURED NOTHING, both from the same
    root cause: a composed rather than transplanted module shape.** The
    generator hardcoded `CommMethod="536870915"` for every variant, and
    CommMethod ENCODES the comm format. Across 183 real ETHERNET-MODULE
    instances in `samples/local` the correspondence is unambiguous, with no
    counter-example:

    | CommMethod | connection element type | real instances |
    |---|---|---:|
    | 536870915 | INT | 109 |
    | 536870916 | SINT | 57 |
    | 536870932 | no connection at all | 11 |
    | 536870913 | DINT | 4 |
    | 536870914 | REAL | 2 |

    - **Arm E (`genem_dt*`, element type at fixed byte size).** The three SINT
      files FAILED conversion outright — `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES`,
      `samples/convert_log.csv` 2026-09-12 — because the method said INT and the
      declared type said SINT. Worse, the DINT and REAL files imported and
      captured, and read byte-identical to `genem_dtint_064`: Studio resolved
      the contradiction from CommMethod and built all three as INT connections.
      That was briefly taken as evidence that cost follows byte count rather
      than element count. **It is not evidence of anything — all three files
      were the same connection.** Byte-count versus element-count remains OPEN.
    - **Arm D (`genem_noconn`).** Built as the connected method with the two
      PrimCxn size attributes simply removed. All 11 real no-connection
      instances use 536870932. The file captured "clean" and reads +3,976, which
      measures whatever Studio does with an inconsistent CommMethod.
      `zero_connection_module_bytes` (2,344) stays untested for this profile.

    Generator corrected and all six affected files rebuilt with the real
    per-type CommMethod. The three captures whose file content changed
    (`genem_dtdint_064`, `genem_dtreal_064`, `genem_noconn`) had their capture
    columns VOIDED in `samples/manifest.csv` rather than carried against a file
    they no longer describe; `genem_dtint_*` were already consistent and keep
    theirs. 6 files await recapture.

    **CONVERSION STATUS (step 2), logged explicitly:** 3 committed files with no
    `ok` on record — `genem_dtsint_008`, `genem_dtsint_064`, `genem_dtsint_450`,
    all `FAILED` with `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` on 2026-09-12. Cause
    diagnosed above, not guessed; fix applied.

6. **OQ-MODULEIO** — mostly closed 2026-08-29. 126 real module captures
   were sitting unreconciled in manifest.csv; 51 catalogs now have a real
   per-catalog overhead value (exact-match rate on real data went from
   1/126 to 54/126). Two real sub-threads remain, both needing
   architecture work not more generation: multi-module marginal cost
   (adding a 2nd/3rd of the same module doesn't cost the same as the
   1st), and a handful of catalogs with real connection-variant-dependent
   overhead.[^moduleio]


    **IN-DEPTH REVIEW 2026-09-18 — thirteen catalogs wired off isolation rows
    that had been captured and clean the whole time. Real set 1.6566% ->
    1.5611%, the largest single improvement of this review.**

    `modulesweep_*` is 96 single-variable rows and 54 of them sat outside ±8.
    Each measures one catalog on top of an adapter whose own row is separately
    captured, so the catalog's overhead falls straight out: 1,672 plus the
    file's residual, with the adapter's residual differenced out first. Thirteen
    catalogs derived that way are now in `module_overhead_by_catalog`, and every
    one of their isolation rows lands at **exactly 0** afterwards.

    Largest: PowerFlex 525-EENET +5,346, 1794-VHSC/A +4,280, PowerFlex
    755-EENET +2,436, 1794-IR8/A +2,311, 1734-IE4C/C +1,763.

    **THE THING THAT COST TWO WRONG DERIVATIONS, recorded so the next person
    does not repeat it.** `report.py` handles rack-aliased and zero-connection
    modules in a branch that `continue`s BEFORE `module_overhead_by_catalog` is
    ever consulted. An entry for such a catalog is inert. The first attempt
    wired twenty catalogs without checking which branch each took, and the
    isolation rows did not move; the second attempt read each module's charged
    bytes from the report and mistook `module_defined_bytes + overhead` for the
    overhead alone. Only the third — splitting the catalogs by branch first —
    produced entries that land their own rows at zero. **Check the branch before
    deriving a per-catalog constant.**

    **Six catalogs are measured and NOT wireable from this table**, because they
    take the rack-aliased branch: 1756-OW16I **+4,594**, 1734-8CFG/C +1,308,
    1794-IB16XOB16P/A +1,100, 1794-IA16/A +992, 1794-OA8/A and 1794-OW8/A +905
    each. Every rack-aliased module is charged the same flat 454 regardless of
    catalog (`rack_aliased_module`, wired earlier today), and these say the true
    cost varies by thousands between catalogs. **That flat 454 is an average
    over catalogs that genuinely differ, and it is the same finding as
    OQ-POINTIOCONN's per-card result seen from the other side.** Fixing it means
    giving the rack-aliased branch a per-catalog table of its own, which is a
    code change, not a constant.

    `1783-NATR` was wired and removed the same day: its isolation row did not
    move at all, so it reaches a bypass branch too, and its −2,344 is unfixable
    from here.

    **The caveat that matters, stated because one real file shows it.** Each
    constant is measured on a file containing exactly ONE module of that
    catalog, so it is the FIRST-instance cost. This table already carries a
    `repeat_bytes` discount for 16 catalogs measured the same way, and nothing
    measures one for these thirteen. `realprog_murraybros` carries FOUR
    PowerFlex 525-EENET drives and moves from +1.150% to −1.178% — an
    over-correction of roughly 10,600 across those four, which implies a repeat
    discount near 3,600 per additional drive. Elmsdale, with six affected
    modules of mixed catalogs, moves the other way and lands almost exactly:
    **+1.991% -> −0.247%**.

    **One file settles the discount**: `modulesweep_powerflex_525_eenet` at two
    and four drives, everything else identical. PowerFlex 525-EENET is 12 of the
    21 real occurrences of these catalogs, so it is the one worth measuring.

   **The marginal-cost sub-thread is closed 2026-09-13 (capture-batch segment
   14, 71 `asmclose_*` rows).** The law is `d x (n - 1)` per catalog, flat at
   n=1/2/4/8, and it is wired for the ten catalogs whose rate was measured on a
   shape real programs contain. 64 of the 71 rows land byte-exact with it
   applied against 16 without. Full derivation, the two deliberate exclusions,
   and the per-rack-vs-per-project measurement are in OQ-MODULEMARGINAL.

   Two of the 71 rows are not usable and their capture columns are now actually
   empty: `asmclose_1756_ob32_rackaliased_n02` and `_n04` shipped duplicate
   module names (the copier renamed only the first element of a 2-deep chain),
   so Studio merged the copies and the files measured N adapters sharing ONE
   output card at zero import errors. The 2026-09-11 note saying they had been
   cleared was written but **the values were never removed**, so both rows kept
   feeding every reconciliation for two days. `lint.duplicate_module_name` has
   caught this class since 2026-09-11, one day after these files were generated;
   `gen_assumed_closeout._place_copies` now renames every `<Module>` in a block
   and repoints each internal `ParentModule`, leaving references outside the
   block alone. `modmarg_ob32chain_*` is the correctly-built replacement and is
   captured.

   Four more are a different kind of bad read: `asmclose_al1222_1conn_n*` reads
   **18,128 at all four module counts**, distinct names, zero errors — the
   AL1222 modules never reached the controller. Left in place rather than
   cleared because the observation is consistent and reproduced at four counts,
   but nothing may be derived from them; see the corrected AL1222 note in
   OQ-MODULEMARGINAL.


    **CAPTURE ERRORS: 9 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    Was 39. The other 30 went on 2026-09-14 when the 28 never-converted
    `modulesweep_*` files and both `modulerack_bender_full_program*` were
    DISCARDED -- see the conversion-status audit in `docs/TASKS.md`.
    12 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `modulemotion_d012_dual_axis`, `modulemotion_d012_single_axis`, `modulemotion_s086_safety_axis`, `modulerack_kinetix_full_bus`, `modulesweep_193_ecm_etr_a`, `modulesweep_193_ecm_etr_b` (+6 more)
    30 committed file(s) attempted and never reached `ok` in
    `convert_log.csv`: `modulerack_bender_full_program`, `modulerack_bender_full_program_r2`, `modulesweep_1734_ob8s_a`, `modulesweep_1734_ob8s_a_r2`, `modulesweep_1734_ob8s_b`, `modulesweep_1734_ob8s_b_r2` (+24 more)

7. **OQ-JSRPARAMCOST** — reopened 2026-08-29 for one small residual.
    Output/return-param call-site cost is now wired and confirmed
    (see RESOLVED_QUESTIONS.md). The callee's own one-time `A(n)`
    Parameters-block cost almost certainly ALSO needs an output-param
    term (real Parameters blocks include both Input and Output entries)
    — `jsr_multiret_n04` still off by +332 after the call-site fix, too
    small relative to a 1-distinct-target sample to isolate from noise.
    Needs a dedicated small file (2+ distinct targets with different
    output-param counts, input count held constant) to isolate A(n)'s
    real output term cleanly. 2026-08-30: `jsr_multiret_n02_r01000` came
    back within 0.09% (140/155,272), consistent with the wired call-site
    fix. But two NEW real, larger, param-TYPE-specific gaps showed up in
    the same push: `jsr_paramtype_string_n05_r00100` is off by +4,096
    (9.76%) and `jsr_paramtype_udt_n05_r00100` by +4,048 (9.78%) — both
    5-param/100-call files, both off by almost exactly the same amount,
    while the plain-DINT/REAL paramtype files in the same batch
    (`jsr_paramcount_*`, `jsr_paramtype_real_n05_r00100`) land within
    0.04%. Points at a real, currently-unwired per-call-site surcharge
    specifically for STRING/UDT-typed JSR parameters (not a flat A(n)
    definition-cost issue, since it scales with something in this file
    that plain-atomic-typed params don't have) — genuinely new, not yet
    derived.

    2026-08-31, real, structurally important: `report.py`'s `is_jsr_target`
    branch treats a JSR target's own logic content as fully absorbed into
    the flat `jsr_fixed_base_per_routine`/`A(n)` cost, `continue`s past it,
    and never weighs its instructions at all — confirmed 2026-08-22, but
    only ever tested against a trivial `SBR(...)NOP();RET();` stub target.
    Real AccuTally review (confidential, not committed) found 123 real
    JSR-target routines averaging 85 real instructions each (one has 201)
    — 10,488 total real instructions currently contribute $0. Built
    `jsr_target_content_scale_{010,050,100,150}` (target content as the
    only variable, 13-153 real instructions) to test this directly — the
    engine predicts the identical 19,452 bytes regardless of target size,
    proving the model treats content as irrelevant; awaiting real capture
    to prove whether that's actually true.

    **Real capture landed 2026-08-31 — confirmed, and cleanly linear.**
    File suffix is the real instruction count (010=10, 050=50, 100=100,
    150=150 instructions). Real deltas: n=10 → +76 (0.39%), n=50 → +800
    (4.11%), n=100 → +1,696 (8.72%), n=150 → +2,600 (13.37%) — escalating
    smoothly with content size exactly as hypothesized, proving JSR-target
    logic content is NOT free. Fitting `delta(n) = a + b*n` against the two
    most separated points (n=50, n=150) gives `b=18, a=-100`; checked
    against n=10 and n=100, both land within 4 bytes of that line (a clean
    4-point linear fit, no residual pattern left over). **18 bytes/
    instruction is suspiciously close to this project's own already-
    confirmed weighted-average instruction cost for ordinary routine
    logic** — consistent with the real fix being architectural, not a new
    formula: stop `continue`-ing past JSR target routines in `report.py`
    and weigh their instructions with the SAME per-instruction-type table
    already confirmed for every other routine, rather than treating target
    content as a special zero-cost case.

    **WIRED 2026-08-31.** `report.py`'s `is_jsr_target` branch now calls
    `compute_routine_logic_bytes(routine, model.logic_instructions,
    tag_types, charge_shell=False)` on the target's own content (using the
    REAL per-instruction weight table already confirmed for ordinary
    routines, not a new guessed 18/instr constant) and adds it to the A(n)
    entry, merged into one `logic_entries` tuple per routine path (two
    separate tuples sharing a path would have silently collided in any
    by-path grouping — caught and fixed before committing). `charge_shell=
    False` confirms the target still doesn't pay its own
    `fixed_base_per_routine` — that stays folded into the caller's
    `jsr_fixed_base_per_routine` as before. Re-validated against the real
    capture data with the new code: residuals dropped from 0.39%/4.11%/
    8.72%/13.37% (n=10/50/100/150) to **-0.81%/-2.13%/-3.47%/-4.75%** —
    max error cut from 13.37% to 4.75%, using only already-trusted
    weights, no new constant. `jsr_midchain_real_chain`/`_leaf_control`
    also improved: predicted delta went from 144 (old, wrong) to 276 (new),
    against a real delta of 332 — most of the previously-reported 188-byte
    "midchain" gap was actually THIS SAME target-content gap, not a
    separate outbound-call cost; only 56 bytes remain unexplained now (down
    from 188), too small to isolate a per-outbound-call rate from one data
    point. 3 pre-existing tests in `test_logic_sizing.py` had hardcoded the
    old (now-disproven) "target content is free" expectation — updated to
    the correct values, plus a new dedicated regression test
    (`test_jsr_target_content_scales_with_instruction_count`) added.
    Remaining small negative residual (grows to -4.75% at n=150) is a new,
    much smaller, separate open thread — not urgent at this magnitude.

    Same review also found `is_jsr_target` is checked BEFORE whether that
    routine itself makes further JSR calls (`continue`s immediately) — a
    routine that's both a target and a caller (mid-chain) has its own
    outbound call cost dropped too. 29 real AccuTally routines are
    mid-chain; one makes 10 real JSR calls of its own. Built
    `jsr_midchain_real_chain`/`jsr_midchain_leaf_control` to isolate this
    (predicted delta is 144, fully explained by the leaf's own A(2)
    declaration cost and nothing for the mid-chain call — any real delta
    beyond 144 proves the gap).

    **Real capture landed 2026-08-31 — the gap is real.** Predicted delta
    (real_chain minus leaf_control) = 144, as expected. Real delta = 332
    (19,068 vs 18,736) — **188 bytes beyond what the leaf's own A(2)
    declaration cost explains**, confirming a genuine, previously-
    unmodeled cost for a routine that is both a JSR target AND itself
    issues an outbound JSR call. Only one data point (a single real_chain
    file, one outbound call) — enough to confirm the gap is real, not
    enough to isolate a per-outbound-call rate yet; needs an n-scale sweep
    (2/5/10 outbound calls from the same mid-chain routine, matching the
    real AccuTally routine that makes 10) before this is wireable.

    **STRING/UDT per-call surcharge — extended 2026-08-31 with n=1/3/5
    disentangle points** (`jsr_paramtype_{udt,string}_n{01,03,05}_
    r00100_iso2`, 100 calls each, param count as the only variable). Real
    deltas: UDT n=1→+428 (1.5%), n=3→+2,448 (7.44%), n=5→+4,064 (10.89%);
    STRING n=1→+428 (1.5%), n=3→+2,464 (7.43%), n=5→+4,096 (10.81%). Two
    findings: (1) STRING and UDT deltas are nearly identical at every n
    (within 16-32 bytes) — the surcharge looks like a general "non-atomic-
    typed JSR param" cost, not type-specific. (2) It is NOT cleanly linear
    in n — fitting `a+b*n` off n=1/n=5 predicts 2,246 at n=3 against a real
    2,448 (202 off, 8.3% miss), a real, non-trivial deviation from a
    straight line. Genuine progress (3x the data of the original single-n
    anchor), but the functional form isn't nailed down yet — needs either
    one more n point or the exact per-call-site byte breakdown to
    distinguish a fixed-plus-linear form from something else before
    wiring anything.

    2026-08-31, real, caught reviewing the target-content-scale
    files: "if there was no jsr parameters then there is no sbr/ret
    instructions inside the called subroutine." Checked against all 8
    real customer L5X files in `samples/local/` (2,534 unique real JSR
    targets): 2,314/2,315 zero-param targets have NO SBR at all,
    2,218/2,315 (95.8%) have no RET either — essentially a hard rule.
    Every EXISTING JSR calibration file in this project uses nonzero
    params (1/5/7/8/9/10/15) and correctly includes SBR/RET (126/128 real
    nonzero-param targets DO have SBR, confirming that whole existing
    calibration set is representative). Only the two brand-new
    target-content-scale files (0 params) had this bug — fixed by
    removing the forced SBR()/RET(), now just ordinary logic rungs
    matching the real, dominant, previously-untested case (AccuTally: 77%
    of real JSR calls are 0-param, and all 103 of its real 0-param
    targets have zero SBR/RET, matching the corpus norm exactly).

    **IN-DEPTH REVIEW 2026-09-18 — every SLOPE in this question is now closed
    and wired. What is left is two flat constants.**

    The even-n paramtype files requested on 2026-08-31 have landed, so the
    non-atomic surcharge now has seven param counts instead of three, and the
    whole family was re-derived from scratch against the live engine rather
    than patched.

    **(a) The "non-linear" non-atomic surcharge was never non-linear. It was
    measured against the wrong baseline.** Subtracting each row's own
    atomic-param control at the SAME n — which the earlier pass did not do —
    gives:

    | n | atomic control | non-atomic | surcharge | − 800n |
    |---:|---:|---:|---:|---:|
    | 1 | −180 | +636 | 816 | 16 |
    | 2 | +220 | +1,836 | 1,616 | 16 |
    | 3 | +224 | +2,672 | 2,448 | 48 |
    | 4 | +224 | +3,472 | 3,248 | 48 |
    | 5 | +224 | +4,304 | 4,080 | 80 |
    | 6 | +224 | +5,104 | 4,880 | 80 |
    | 8 | +224 | +6,736 | 6,512 | 112 |

    That last column is exactly `16 + 32 × floor((n − 1) / 2)` at every one of
    the seven counts, with no residual at all. So

        surcharge(n) = 800·n + 16 + 32·floor((n − 1) / 2)     at 100 calls

    fits all 12 rows (7 UDT, 5 STRING) to the byte. The earlier "n=1 → 2.7
    bytes/param, n=3 → 7.7, n=5 → 7.9, something changes between 1 and 3"
    reading was an artifact: n=1's atomic control sits at −180 where every
    n≥2 control sits at +224, a 404-byte baseline shift that was being read
    as curvature in the surcharge.

    STRING and UDT agree to the byte at n=1, 3 and 5 despite an 88-byte
    STRING against an 8-byte 2-DINT UDT, so the cost is keyed on *non-atomic*
    and not on the operand's size. That is now three independent counts'
    worth of confirmation, not one.

    **NOT WIRED, and the reason is a genuine ambiguity, not caution.** Every
    non-atomic row in the corpus has exactly 100 calls, so `800n` is
    indistinguishable from `8 per param per call` (8 × 100) and from `800 per
    param, once per target`. The two readings differ by 100× on real files:
    the sixteen real programs carry **176 non-atomic JSR param operands**
    (resolved through UDT/AOI member chains — `CMU_TrayLayer` ×68, `PosnLug`
    ×32, `Board` ×12, `CMU_Discharge` ×12, `udtServo` ×10, `ts_CIPAxis` ×8,
    the rest in ones and twos), so per-call is **1,408 bytes across sixteen
    files** and per-target is **~140,800 — about 1.4% of the real set, in the
    direction the real set needs.** Wiring the wrong one either does nothing
    or moves the headline by more than a percent for the wrong reason. This is
    the single highest-value-per-file measurement left in the question, and it
    is three files: `jsr_paramtype_udt_n04` at r=10 and r=1000 against the
    existing r=100, plus one STRING r=1000 cross-check.

    **(b) B(n) is not affine in n, and the step keys on TOTAL operands.
    WIRED.** Solving for the per-call slope and the per-file constant
    separately — possible now that several param counts have two or three call
    counts — gives `residual(n, R) = p(n)·R + c(n)` with `p = 4, c = −176` for
    every n ≥ 3 at all three call counts: `4×10 − 176 = −136` (n=7/9/15),
    `4×100 − 176 = +224` (n=3/4/6/12), `4×1000 − 176 = +3,824` (n=5/8/10).
    Thirteen rows, call counts an order of magnitude apart, one pair of
    constants. n=1 is the control and is flat — −180 at both R=100 and
    R=1000 — so B(1) was already right and the step sits between 1 and 2.

    The step is keyed on `n_in + m_out`, not `n_in`, and the row that decides
    that is `jsr_multiret_n02_r01000`: 1 input, 2 outputs, 1,000 calls, which
    sat at **+3,952** and is the largest single residual this question ever
    had. Under the input-only reading n_in = 1 and no step applies. Keying on
    total operands takes it to **−56**, into the flat band with everything
    else. Wired as `jsr_param_cost.b_multiparam_extra: 4` with
    `b_multiparam_threshold: 2`. Zero-operand JSRs are untouched, which
    matters because 1,973 of the real corpus's 2,221 JSR calls pass nothing.

    **(c) A distinct JSR target costs 8 more than the model charged. WIRED.**
    With (b) in place the zero-param multi-target sweep's residual resolved to
    exactly `8t − 280`: −272, −256, −240, −200, −160, −120, +40, +120 at
    t = 1, 3, 5, 10, 15, 20, 40, 50 — **+8 per target at every step**, across
    two generators and name lengths 4 through 40 (the namelen rows are all
    identical, so this is not a name term; that law is already correct).
    `jsr_target_declaration.per_target` 152 → 160 flattens all thirteen rows
    to the same −280.

    **Real-set effect of (b) and (c) together: 1.6894% → 1.6753% mean absolute
    error, and all sixteen moved the right way.** Small, as it must be — these
    are tens of bytes per call site on megabyte files — but it is the right
    sign and it is measured rather than fitted.

    **What is actually left.** After (b) and (c) every slope in the JSR family
    is zero. Thirty-three captured rows reduce to two flat per-file constants:

    * **−184** on every param-bearing single-target file (16 rows: n = 1…15,
      call counts 10 / 100 / 1,000 — the constant does not move with either).
      −188 at n ≤ 2, a further 4-byte thread of its own.
    * **−280** on every zero-param multi-target file (13 rows).

    They differ by 96 and cannot be separated further here: every row in the
    first group has exactly one distinct target, so per-file and per-target are
    collinear, and the second group's targets have no SBR/RET at all (the
    confirmed real rule for zero-param targets). On a real megabyte program a
    200-byte file constant is 0.02%, so this is now the smallest thing in the
    project, and it stays documented rather than absorbed into `a_base` where
    it would be untraceable.

    Two small threads survive alongside it: `jsr_multiret_n04_r01000` sits
    +184 from `_n02` at the same call count and operand shape, which is the
    2 extra RET points in the target and wants a per-RET-point rate from a
    third point; and `jsr_midchain_real_chain`'s 56 bytes, unchanged, still
    one data point.


    **CAPTURE ERRORS: 4 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    4 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `jsr_target_content_scale_010`, `jsr_target_content_scale_050`, `jsr_target_content_scale_100`, `jsr_target_content_scale_150`

8. **OQ-EVENTTRIGGER** — **the instruction half CLOSED 2026-09-17 and WIRED.**
    The EVENT instruction had no weight in the table at all and was charged
    zero. `uwclose_event_n{00010,00100,01000}` -- an EVENT task plus n rungs of
    `EVENT(EvtTask);`, nothing else varying -- reads 20,232 / 25,272 / 75,672
    against a flat predicted 19,664, so the under-charge is 568 / 5,608 /
    56,008: **exactly 56n + 8**, the 8 being the universal per-file residual.
    Three counts spanning 100x with zero residual, so KNOWN. Wired as
    `logic_instructions.weights.EVENT: 56`; all three rows now land at +8.

    The trigger-SOURCE half of this entry (what an EVENT task's own
    configuration costs, as against the instruction that fires it) is untouched
    and stays open below.

    task_extra (+700) was derived only
    from CONTINUOUS+PERIODIC tasks; EVENT-type tasks are completely
    untested, and so is trigger-source (Axis Watch vs. EVENT-instruction)
    within EVENT. Two files built, awaiting capture.[^eventtrigger]

    **`eventtask_instronly` real capture landed 2026-08-31 — the task-TYPE
    question is closed.** Predicted 19,600, real 19,600 — exact, 0.00%
    residual. `task_extra`'s existing formula (derived only from
    CONTINUOUS/PERIODIC before now) extends cleanly to an EVENT-type task
    with no separate term needed. Still open: `eventtask_axiswatch` (the
    trigger-SOURCE sub-question, Axis Watch vs. EVENT-instruction) has no
    real capture yet — that comparison is the only piece of this OQ still
    genuinely awaiting data.


    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `eventtask_axiswatch`


11. **OQ-SERIESOUTPUT** — a rung with more than one output instruction in
    series. Opened 2026-09-13 (capture-batch segment 5), replacing the closed
    OQ-COMPOSITESCALE at this slot. **16 files built, awaiting capture.**

    **CAPTURE 2026-09-18, 25 files, all converted `ok`, all `error_count` 0.
    Kept short deliberately.**

    **Arm A, `sroutc_c{1,2,4}_k{1,2,4,8}` — THE RATIO HYPOTHESIS IS DEAD.** The
    grid is completely FLAT in condition count:

        per rung      k=1    k=2    k=4    k=8
        c=1             0    -12    -36    -84
        c=2             0    -12    -36    -84
        c=4             0    -12    -36    -84

    Identical to the byte at every one of the twelve cells. The discount is
    −12 × (k − 1) and condition count does not enter it. `sroutc_c01_k01` reads
    0, matching `srout_ote_k01` exactly, so the control holds.

    This was specified as "the decisive measurement for the whole project"
    because a condition/output RATIO was the one hypothesis that reconciled the
    synthetic families with the real ones. **It does not.** The law is now
    confirmed by a FOURTH independent family and all sixteen real programs still
    reject it (applying it: 1.70% → 3.22%, every file worse).

    **What is left, and it is now the only candidate.** Every generated file that
    shows the discount repeats ONE rung 1,000 times. Rung COUNT is excluded
    (200 and 1,000 give the same per-rung figure) and tag UNIQUENESS is excluded
    (`srout_oteuniq_k08`). What has never been varied is **rung IDENTITY within
    a file** — real ladder never repeats a rung, and no file in the corpus
    contains a multi-output shape where every rung differs.

    That is the same systematic corpus defect OQ-TAGORDER names at tag scope:
    **the corpus is uniform where real programs vary.** Two independent
    questions now point at it. A file of 1,000 DISTINCT 4-output rungs, against
    `sroutc_c01_k04`'s 1,000 identical ones, settles it and costs one file.

    **Arm B, `cpttri_k3_*` — the k=3 tier truth table is closed.** t211 and t221
    read 0, t212 reads +4/rung. `cpttri_pow_p3_adjacent` reads **+48/rung**:
    `**` adjacency is a real unmodelled effect, separate from operator count.

    **Arm C, `stc2_*` — THE FALSIFICATION TEST PASSED.** These are the six
    2-operator midpoints specified to over-determine the ST constants wired from
    single points earlier the same day. Four of six land at exactly **0**:
    `and`, `or`, `xor` at two operators, and both all-float rows
    (`premreal2_mul`, `premreal2_pow`). So the bitwise premium of 0 and the
    all-float premiums of 0 and 8 hold at a second operator count and are no
    longer single-point. Only `stc2_prem2_pow` is off, at +28/rung — the DINT
    `**` premium of 38 is right at four operators and not at two.

    **Arm D, `cptnar_j*` — narrowing is badly wrong on mixed-width shapes**:
    +88, +204 and +120 per rung. OQ-CPTNARROW's `rate_T × k − 132` was derived on
    uniform-width operands and does not survive mixing. Real exposure is still 27
    calls in one program, so this stays unwired.

    Two captured single-shape sweeps say the engine over-charges by exactly 12
    bytes per output instruction beyond the first in a series cascade:

        UID()UIE();                                      2 outputs  −12.000/rung
        XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);   3 outputs  −24.000/rung

    Both slopes are exact across three orders of magnitude of rung count. The
    one-output controls are exact too — `XIC(B0)OTE(B1);` reads 0 over 1,000
    rungs, and `MOV(0,D0);`, `ADD(D0,D1,D2);` and `OTE(B0);` each read the
    universal +8 at 10 through 5,000 rungs — so the per-instruction weights are
    right in isolation and something about the cascade is not. Parallel branch
    legs are already known exempt: `[XIC(B0),XIC(B1)]OTE(B2);` is 0, and
    `branchdepthc_legs30_n01000` carries 30,000 extra instructions at exactly 0.

    **IT IS NOT WIRED, AND MUST NOT BE FITTED, because the real programs reject
    it.** Applying −12 per extra series output takes the sixteen held-out
    programs from 2.07% to **2.90%** mean absolute error and makes every single
    one of them worse — they already under-predict and this predicts less.
    Counting outputs at bracket depth 0 only (branches exempt) gives the same
    2.90%; counting branch contents as well gives 4.51%. So the law is exact on
    two generated shapes and wrong on the only files that count, which means
    something those two shapes share is absent from real ladder.

    Four candidates, none separable in the existing corpus:

      1. The count may not be linear at 12 — two points cannot tell 12-per-extra
         from "12 for the second output and nothing after", or from a cap.
      2. Every rung in both sweeps is BYTE-IDENTICAL thousands of times over,
         addressing the same operands. Real rungs differ. One-output shapes are
         exact under the same repetition (`instr_mov_n05000` is 5,000 identical
         rungs), so repetition alone is not it — repetition *plus* a cascade is
         untested.
      3. Series versus parallel at matched output counts, which nothing in the
         corpus does.
      4. Repeated instruction type versus distinct types within the rung.

    **Files built 2026-09-13** — `src/sample_gen/gen_seriesoutput_closeout.py`,
    16 files, every shape built from instructions whose isolated weight is
    already confirmed exact:

    - **A, `srout_ote_k{01..08}_n01000`** (8 files). One XIC condition and k OTE
      outputs in series, each to its own bit. Eight consecutive counts read the
      shape of the law instead of two points on it.
    - **B, `srout_oteuniq_k{02,04,08}_n00200`** (3 files). The same cascade with
      every rung writing its own distinct bits, so no two rungs are identical
      and no tag is addressed twice. Tests candidate 2 against group A directly.
    - **C, `srout_branch_k{02,04,08}_n01000`** (3 files). The same k outputs in
      parallel legs, same tags, same rung count — candidate 3 at matched counts.
    - **D, `srout_mixed_k04_n01000`** vs **`srout_same_k04_n01000`** (2 files).
      Four outputs of four different types against four OTEs — candidate 4.

    **TWO MORE POINTS AND ONE CANDIDATE ELIMINATED, 2026-09-13 (capture-batch
    segment 8, `ntag_*`).** The law is now measured on THREE independently
    generated shapes at three different output counts, all exact:

    | shape | outputs | per rung |
    |---|---:|---:|
    | `UID()UIE();` | 2 | **−12** at n = 1, 10, 100 and 1,000 |
    | `XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);` | 3 | **−24** at n = 400 and 4,000 |
    | `UID()XIC(B0)OTE(B1)MOV(D0,D1)UIE();` | 4 | **−36** at n = 100 |

    −12 × (outputs − 1) at 2, 3 and 4 outputs, nothing fitted to get there.

    **Candidate 2 — identical-rung repetition, or deduplication — is DEAD.**
    `ntag_uidpair_n00001` is a ONE-RUNG file and pays the full −12. There is no
    repetition in a one-rung file, so the discount cannot be amortisation of a
    repeated structure. That was the candidate I thought most likely, and group B
    of the built batch (`srout_oteuniq_*`) existed to test it; it is answered
    without capture.

    **Candidate 4 — repeated versus distinct instruction types — is badly
    weakened.** The `withbody` rung's four outputs are four DIFFERENT
    instructions (UID, OTE, MOV, UIE) and it pays exactly 12 per extra, the same
    rate as `UID()UIE();`'s two distinct ones. The law does not care about type
    distinctness.

    So: the discount needs no repetition, ignores instruction type, exempts
    parallel branches, and is exact at three output counts on three shapes — and
    the sixteen real programs still reject it outright (2.07% → 2.90% even
    counting series-only outputs at bracket depth 0).

    **JOINT HYPOTHESIS WITH OQ-REALUNDER, and it makes both coherent.** That
    entry's differencing puts the real-file residual on compiled logic, with
    `residual / routine_logic_bytes` bimodal — eleven programs 9% to 22% SHORT.
    If the −12 discount is in fact real and universal, then real ladder's true
    under-charge is LARGER than 9–22%, and applying only the discount makes real
    files worse precisely because the bigger positive term is still missing. One
    unpriced positive term in real ladder explains both observations; two
    independent errors of opposite sign in the same category does not.

    That makes `strip_ladder.py`'s **L2 rung — minus all rung and ST content —
    the decisive measurement for this entry too**, not just for OQ-REALUNDER.
    Nothing further should be fitted here until it is captured.

11b. **OQ-UDTTAGSLOT** — is a standalone UDT tag's data slot padded to 8 bytes?
    Opened 2026-09-13 (capture-batch segment 5). **WIRED, and thin. 52 files
    built, awaiting capture.**

    Two captured families disagreed about what one UDT-typed tag costs, and only
    because they sit on opposite sides of an 8-byte boundary:

        dscale2_udt_u001_t001..t500   9-byte UDT, 1 to 500 tags   EXACT (14/18 rows 0)
        addit_dm_ln / addit_dh_ln    40-byte UDT, 40 and 400 tags −7.000/tag, exact slope

    One hypothesis fits both with zero residual: pad a standalone (non-array)
    UDT tag's DATA slot up to 8 — 40 stays 40, 9 becomes 16 — and set
    `definition_scale_correction.udt_tag_extra` to −4 rather than the +3 that
    held for as long as only the 9-byte family existed. Both are wired
    (`memory_model.yaml standalone_udt_tag_slot`); corpus mean absolute error
    1.853% -> 1.841% and the `udt` category picked up 7 more rows inside ±8.
    It is the same kind of per-TAG slot rule as the already-KNOWN
    `standalone_atomic_tag_slot` of 4, one level up.

    **Why it stays open**: the padding constant and the −4 are not separable
    from either family alone, and the whole corpus contains exactly TWO UDT
    sizes that bear on it, 9 and 40 — a two-parameter hypothesis fitted to two
    points, one on each side. That is the shape of fit this project has had to
    undo four times in the AOI-definition cost alone.

    **A second reading, recorded rather than fitted**: padding the UDT ELEMENT
    size instead of the tag slot improves the sixteen real programs *more*
    (2.13% -> 1.88%) but costs the `tags` category its accuracy outright (0.27%
    -> 2.03% mean absolute error) and is flatly contradicted by
    `dscale2_udt_arr002/arr010/arr100/arr500`, which read +1 at every length
    against a 12-byte 4-aligned element. So that real-file gain is absorbing
    some other missing term and must not be spent here — see OQ-REALUNDER.

    **Files built 2026-09-13** — `src/sample_gen/gen_udttagslot_closeout.py`,
    52 files, 8-character tag names throughout so the `tag_overhead` bucket
    never moves:

    - **A, `udtslot_s{01..16}_t{050,400}`** (32 files). A UDT of k SINT members
      for k = 1..16, packing to exactly k bytes, at 50 and 400 tags. Every
      residue mod 8 twice, on both sides of the boundary, with the per-tag cost
      read as a slope 350 tags apart rather than a single count.
    - **B, `udtslot_d{01,02,03,04,05,06,08,10}_t{050,400}`** (16 files). DINT
      UDTs of 4 to 40 bytes — says whether the step is really at 8 and not at 4,
      and the 40-byte point reproduces the additivity D axis as a cross-check.
    - **C, `udtslot_arr_s{03,05}_n{050,400}`** (4 files). Arrays of the 3- and
      5-byte UDTs — the first array arm that can see an element-padding rule at
      two different residues.

12. **OQ-AOIINTERNALLOGIC** — new, real, corpus-wide gap, found 2026-08-31:
    AOIs were closed out without ever putting logic inside one. Every AOI
    has at least one internal subroutine and can have more (HomeToTorque
    is the real example).
    `aoi_xml()` (builders.py) has hardcoded a self-closing
    `<Routine Name="Logic" Type="RLL"/>` for EVERY AOI test file this
    project has ever generated — $0 real internal-logic content has ever
    been exercised in ANY AOI calibration file, and the shared builder
    never supported more than one internal routine. The existing
    `aoi_definition` formula (base + per_declared_item*count +
    name-length term) is purely a Parameter/LocalTag declaration-cost
    model — it has never been tested against real Logic-routine content
    or a second internal routine, both of which are common in real AOIs.
    Real confidential-project review (not committed, never named beyond
    this generic description) confirms this is a real, material gap: 39
    real AOI definitions there have 573 total real rungs of internal
    logic (111,507 chars) — 100% currently unsized anywhere in this
    project — and 8 of the 39 have 2 internal RLL routines, not 1 (e.g.
    HomeToTorque: Logic 21 rungs + EnableInFalse 1 rung). Fixed the
    builder (`logic_rungs_xml`/`extra_routines_xml` params, both default
    `""`, confirmed byte-identical output for every existing caller) and
    built `aoi_logic_scale_{000,010,050,100}` (Logic-content-scale sweep)
    plus `aoi_multiroutine_control`/`aoi_multiroutine_real` (mirrors
    HomeToTorque's real 2-routine shape exactly) — all 6 predict the
    identical 19,440 bytes regardless of Logic content size or
    second-routine presence, confirming both are currently zero-weighted.
    Awaiting real capture; if either scales with real Capacity, this is a
    second, independent, currently-unmodeled cost category on top of
    OQ-JSRPARAMCOST's target-content finding — real AccuTally logic
    content (routine + AOI-internal combined) may be substantially larger
    than this project has ever priced.

    **Real capture landed 2026-08-31 — confirmed, AOI internal logic
    content is NOT free, and multi-routine vs single-routine content of
    the same size costs the same.** All 6 files share predicted 19,440
    (the model still doesn't weigh AOI-internal logic at all). Real
    results: `aoi_logic_scale_000` (0 rungs) → 19,440, exact 0.00% —
    confirms the empty-shell baseline itself is right. `_010` → 19,676
    (+236, 1.21%), `_050` → 20,620 (+1,180, 6.07%), `_100` → 21,776
    (+2,336, 12.02%) — a clean, escalating, real cost that scales with
    logic-content size, same shape as the JSR-target-content finding
    above. `aoi_multiroutine_control` (HomeToTorque's real 2-routine
    shape, same total content as `_050`) reads the exact same 20,620 as
    `_050` — **splitting the same content across 2 internal routines
    instead of 1 costs identically to keeping it in one routine**, so the
    per-routine count itself isn't a separate cost driver, only total
    content is. `aoi_multiroutine_real` (the literal HomeToTorque content,
    not a synthetic same-size stand-in) reads 20,912 (+1,472, 7.57%) —
    close to but not identical to `_control`, the gap presumably from real
    instruction-mix differences (HomeToTorque's real rungs vs the
    synthetic control's), not the routine-count structure. **Architectural
    conclusion: AOI internal Logic-routine content should be weighed with
    the same per-instruction model as ordinary routine logic (same fix
    direction as the JSR-target-content finding above), not treated as
    zero-cost; the per-routine-count dimension can be dropped from the
    model entirely — real data shows it doesn't matter.**

    **WIRED 2026-08-31.** New `parser/logic.py` function,
    `parse_aoi_internal_logic()`: walks `Controller/
    AddOnInstructionDefinitions/AddOnInstructionDefinition/Routines/
    Routine` for every AOI definition and aggregates ALL of its internal
    RLL routines' rung text into ONE pseudo-`RoutineLogic` per AOI name
    (deliberately not tracked per-routine, matching the confirmed "routine
    count doesn't matter" finding). `report.py`'s AOI-definition-cost path
    now calls `compute_routine_logic_bytes(..., charge_shell=False)` on
    that aggregate and adds it to the existing param/localtag declaration
    cost (`AoiDefinitionModel` untouched — confirmed via the n=0 file
    landing at an exact 0.00% match, so no double-counting). Re-validated
    against real data: residuals dropped from 0.00%/1.21%/6.07%/12.02%
    (n=0/10/50/100) to **0.00%/0.00%/-0.29%/-0.55%** — essentially exact
    at every point tested, max error cut from 12.02% to 0.55%.
    `aoi_multiroutine_control` (2 internal routines, same total content as
    `_050`) now predicts identically to `_050` as designed (-0.29%);
    `aoi_multiroutine_real` (literal HomeToTorque content) lands at +1.02%,
    a small real instruction-mix difference, not a routine-count effect.
    **Checked against `gen_composite_realistic.py`'s AOI calls: this fix
    does NOT move the composite batch's ~3% residual at all** — that
    generator still uses the old hardcoded self-closing `<Routine
    Name="Logic" Type="RLL"/>` shape (never updated to use `aoi_xml()`'s
    new `logic_rungs_xml` param), so its AOIs have zero internal content to
    weigh either way. **Correcting the composite-residual hypothesis
    written earlier in the same pass** (see OQ-COMPOSITESCALE below): neither
    this fix nor the JSR-target-content fix explains the composite
    batch's residual, since composite files don't currently exercise
    either gap — that residual's real source is still unidentified.

    **REOPENED 2026-09-12. The wiring above is validated against SUSPECT
    rows, and the files were gone.** All six calibration files had been
    deleted from the repo entirely, so nothing could be re-examined, and
    **five of the six captured WITH Studio build errors**:

    | file | recorded `error_count` |
    |---|---:|
    | `aoi_logic_scale_000` (empty shell) | 0 |
    | `aoi_logic_scale_010` | 1 |
    | `aoi_logic_scale_050` | 8 |
    | `aoi_logic_scale_100` | 16 |
    | `aoi_multiroutine_control` | 8 |
    | `aoi_multiroutine_real` | 8 |

    No error text was ever recorded. The count rises with rung count, so a
    repeating rung shape in the generator's 5-shape mix is being rejected
    while Studio imports the rest of the project — which is the worst case,
    because `actual_bytes` still gets filled in from a project missing part of
    the logic it was built to measure. Per CLAUDE.md that makes every one of
    those rows **suspect, not wrong**, and it points one way: the measured
    bytes UNDER-state the real cost, so the per-instruction weighting fitted
    to them is likely **under-charging AOI internal logic**. The headline
    "essentially exact at every point tested, max error cut from 12.02% to
    0.55%" is an exactness against those numbers. Only `aoi_logic_scale_000`,
    the zero-logic baseline, is clean — and that file contains no AOI internal
    logic at all, so it validates nothing about the weighting.

    This matters at real scale: the same real program reviewed above has 39
    AOI definitions carrying 573 rungs of internal logic between them.

    The six files are **rebuilt** and now exist again. The gate reports all
    five errored rows as STALE — the rebuild does not reproduce the captured
    content byte-for-byte, because the shared builder has moved since — so
    their `actual_bytes` describes content the repo no longer holds and cannot
    be used even with a caveat. They need recapture.

    **One diagnosis was tried and is recorded here because it is WRONG.** The
    suspect shape looked like `MOV(In0,In1)`, on the theory that an AOI's
    Input parameters are read-only inside its own logic. They are not. Real
    shipping AOIs write to their Input parameters routinely —
    `MOV(RawInput,RawMax)`, `OTU(HMI_ResetStats)` in the real corpus — because
    an Input is a local copy made at invocation, not a reference; only InOut is
    by-reference and only Output flows back. A lint rule built on that premise
    fires on 133 committed files including all four real production programs,
    which demonstrably compile. It was written, tested, and reverted.

    Counting shape occurrences does not settle it either. The mix cycles 5
    shapes, so at 13/42/78 rungs each shape appears a known number of times,
    and **no single shape appears 1, 8 and 16 times**: `CLR(Loc0)` appears
    8 and 16 at n=50/100 but 3 at n=10; `MOV(In0,In1)` appears 2, 8 and 15.
    Either the error is not one-per-rung, or more than one shape is involved.

    **17 files built to measure it instead of inferring it**
    (`src/sample_gen/gen_aoi_internal_shape_isolation.py`):

    - **`aoishape_{mov,xicote,clr,add,equote}_n{01,05,10}`** (15 files). Each
      of the five mix shapes alone in an AOI's Logic routine, at 1/5/10 rungs,
      same 3 In / 1 Out / 2 Local parameter shape as the captured sweep. The
      recorded error count then names the offender directly: a shape rejected
      once per rung shows its count tracking the rung count in its own three
      files and zero in the other twelve. Shapes are verbatim from the captured
      mix, `MOV(In0,In1)` included — changing them would measure a different
      question.
    - **`aoishape_control_empty`** — zero internal logic, current builder
      output. Separates a rung-shape cause from the surrounding project
      structure: if this errors too, no rung is at fault.
    - **`aoishape_control_mix13`** — the same 13 mixed rungs
      `aoi_logic_scale_010` carries. Its error count is directly comparable to
      that row's recorded 1 (its bytes are not — a different AOI type-name
      length carries its own cost).

    If every one of the 17 comes back at zero errors, the cause was in project
    structure the sweep has since changed, and the next step is **the raw
    Studio 5000 error-log line** for one of the original six files rather than
    another round of inference.

    **CAPTURED 2026-09-14 (segment 15). All 17 at ZERO errors, the 13-rung mix
    included. No rung shape is at fault**, so that condition is met: the original
    five errored rows were broken by the surrounding project structure, and the
    next step is the raw Studio error-log line. Two rounds of shape inference
    have now been tried and both were wrong; there is no third.

    **The calibration question this was protecting is answered. The AOI-internal
    weighting under-charged by exactly 4 bytes per instruction that WRITES A
    NON-BOOL DESTINATION. Wired 2026-09-14, KNOWN.**

        aoishape_{mov,add,clr}_n{1,5,10}    +4 per rung
        aoishape_{xicote,equote}_n{1,5,10}   0 at every count
        aoishape_control_empty               0
        aoishape_control_mix13              +32 on 8 word destinations
        aoistr_scale_rung_n{011..085}       +4 per rung, 7.7x span
        realscale_aoiint_n{0..12000}         0 through 12,000 instructions

    MOV/ADD/CLR write a DINT, OTE writes a BOOL, EQU and XIC write nothing. ADD
    at three operands, MOV at two and CLR at one all cost the same +4, so it is
    not per-operand. `control_mix13` is the additive cross-check on a mixed file:
    3 MOV + 3 CLR + 2 ADD = 8, residual 8x4 exactly. All 27 rows across the five
    families are byte-exact with it wired.

    **This explains `aoi_internal_per_rung`** — the 4 bytes/rung measured
    2026-09-10, which looked perfect and was rejected for making the 122-file
    `aoi` family four times worse. Right number, wrong carrier:
    `aoistr_scale_rung`'s rungs are `XIC(EnableIn)MOV(In0,In1);`, **one MOV
    each**, so per-rung and per-word-destination coincide on that family and
    nowhere else. Both readings that note was stuck between are dead — per-rung
    requires xicote/equote to cost 4 (they cost 0), and per-instruction-at-2
    requires a 2-instruction rung to cost more than a 1-instruction rung (the
    split is the other way round).

    **Negative control: PROGRAM routines are unaffected.**
    `instr_{mov,clr,add,equ,xic,ote}_n{10..5000}` all sit at the universal +8
    per-file residual — the same 8 for every instruction at every count to 5,000.
    The weights are already right outside an AOI. `word_destination_count` is
    populated by `parse_aoi_internal_logic` only and stays 0 for
    `parse_rll_routines`.

    Real set 1.6289% -> **1.6051%** mean, +1.2579% -> **+1.1797%** sum-weighted;
    corpus byte-exact 1,220 -> 1,235. `composite` gets worse, 1.663% -> 1.682%,
    recorded rather than hidden — it is the family whose own generator defects
    are still open.

    **Still open here:** segments 30/31 (`aoi_logic_scale_*`,
    `aoi_multiroutine_*`) need recapture and are now a TEST of this law rather
    than an input to it. `_DESTINATION_ARG` in `parser/logic.py` covers 42
    mnemonics; MOV/ADD/CLR are measured and the rest are classified from
    documented operand order, so a mnemonic whose destination sits elsewhere
    would be mis-charged by 4. Real AOI-internal inventory, corrected 2026-09-18:
    38,821 instructions across ALL sixteen programs, of which 9,291 are charged
    and 6,963 of those are the measured three. (The "11,241 across 6 of the 16"
    written here previously was wrong -- see the in-depth review below.)

    **IN-DEPTH REVIEW 2026-09-18 — the `_DESTINATION_ARG` exposure is now
    MEASURED instead of feared, and it is an order of magnitude smaller than
    this entry claimed. Two real defects in the table were found and fixed.**

    The open worry above was that 39 of the 42 mnemonics are classified from
    documented operand order rather than captured, so a mis-classified one is
    charged or spared 4 bytes on no evidence. That worry was never sized. It is
    now, by inventorying every AOI-internal instruction in all sixteen real
    programs against the table:

    | | instructions | bytes at 4 each |
    |---|---:|---:|
    | total AOI-internal | 38,821 | — |
    | charged the surcharge | 9,291 | 37,164 |
    | of those, MEASURED (MOV/ADD/CLR) | 6,963 | 27,852 |
    | of those, classified but NEVER measured | **2,328** | **9,312** |

    So the entire unmeasured exposure across the whole held-out set is **9,312
    bytes, about 0.09%** — and that is the figure for every one of those
    classifications being wrong at once, in the same direction. The largest
    single one is DIV at 538 instructions (2,152 bytes); CPT 471, SUB 372,
    MUL 350, COP 206 and then a tail of 14 mnemonics under 110 each. **No test
    batch for this is justified ahead of anything that moves a percent**, which
    is the disposition this thread should have had all along, and the number is
    recorded here so the question is not reopened on vibes.

    Correcting this entry's own arithmetic while here: it said "11,241
    instructions across 6 of the 16 programs". The real figure is **38,821
    across all sixteen** — every real program has AOI-internal logic, from
    1,315 (emporiumedger) to 4,124 (accutally). The old number was counting
    something narrower and was being used to argue the exposure was larger than
    it is.

    **Defect 1, fixed: five entries named the wrong operand.** COP, CPS and FLL
    are `(Source, Dest, Length)` and BSL/BSR are `(Array, Control, Source,
    Length)`, so the table's `-1` inspected the LENGTH operand. It charged the
    right total anyway — a literal length does not resolve to BOOL, and the
    unresolved default is a word — so it was right for the wrong reason and
    would have started charging a BOOL-destination COP the moment a length was
    a tag. Now explicit: `COP/CPS/FLL: 1`, `BSL/BSR: 0`. 300 real instructions
    read the correct operand; the predicted total does not move, which is the
    expected result and the reason this was invisible.

    **Defect 2, fixed: five word-destination writers were missing entirely.**
    The same inventory lists every mnemonic charged nothing, and `GSV` is in it
    — 363 real occurrences of an instruction whose whole purpose is to read a
    controller attribute INTO a tag. With MVM, SCP, SIZE and AVE that is 453
    real instructions that write a word and were charged zero. Added on the
    same documented-operand-order basis as the other 39. `SSV` is deliberately
    NOT added: it writes the attribute and only reads the tag.

    Judged against what was already spared correctly, the table holds up: every
    comparison (EQU 2,314, GRT 661, NEQ 644, LIM 442, LES 410, GEQ 330, LEQ
    145, CMP 109, MEQ) writes nothing and is charged nothing, and the bit
    outputs (OTE 2,432, OTU 1,869, OTL 990, ONS 1,514, OSR, OSF) are correctly
    outside a set defined as NON-BOOL destinations. Timers and counters
    (TON 732, RES 621, RTO 156, CTU 130) write a structure rather than a word
    and stay out; that is a judgement, not a measurement, and it is 1,639
    instructions (6,556 bytes) — the one remaining item here worth a file if
    anything ever is.

    Real set: 1.6753% -> **1.6732%**. No generated row moved at all, which is
    itself the finding: not one file in the 2,500-row corpus puts a GSV, MVM,
    COP or FLL inside an AOI, so this whole surface was only ever exercised by
    the real programs.

    **CAPTURE ERRORS: 5 row(s)** — `aoi_logic_scale_010/050/100`,
    `aoi_multiroutine_control/real`. These were routed to OQ-AOIDEFITEMIZE and
    OQ-BUILDFAIL-OPEN by sample-prefix rules, so the rows that invalidate this
    question's headline were being flagged against two unrelated questions.
    `samples/oq_owners.csv` now routes both families here, which is where the
    consequence actually lands.

13. **OQ-IDENTNAMELEN** — new, real, found 2026-08-31 in the same push as
    the "5/10/15/20/50 subroutines... different routine name lengths"
    directive. `gen_jsr_multi_distinct_targets_scale.py`'s
    `group_name_length` (10 fixed JSR targets, name length swept 4/8/16/
    32/40 chars — 40 capped per Rockwell's real Logix identifier limit,
    see that generator's own comment) and `gen_program_multi_distinct_
    scale.py`'s matching `group_name_length` (10 fixed extra Programs,
    same length sweep) both currently predict a FLAT total regardless of
    name length — neither `jsr_target_param_counts`' `A(n)` nor
    `task_program_shell`'s `program_extra` has a name-length term, unlike
    tags/UDTs/AOI definitions (all confirmed real name-length bucket
    costs already).

    **Real capture landed 2026-08-31 for both sweeps at namelen04/08/16/
    32 (namelen40 not yet captured — that variant failed import under the
    old, invalid namelen48; see the fix below) — and the two
    independent sweeps show the SAME real pattern.** Deltas (against the
    flat predicted baseline, so pure name-length signal) at len 4/8/16/32,
    10 items per file:
      - JSR targets: +1,440 / +1,520 / +1,600 / +1,760 (7.13% / 7.53% /
        7.92% / 8.72%)
      - Programs: -160 / -80 / 0 / +160 (-0.62% / -0.31% / 0.00% / 0.62%)
    (JSR shows a large constant offset because its predicted baseline is
    already under-costed by the separate, still-open target-content and
    per-param findings above; Programs' baseline is exact at len=16 so its
    deltas read as pure signal directly.) Per-item, both sweeps show the
    IDENTICAL step shape: +8/item from len4→len8 (a 4-char step), +8/item
    from len8→len16 (an 8-char step — HALF the per-char rate of the first
    step), +16/item from len16→len32 (a 16-char step — same per-char rate
    as the second step). Expressed relative to a 4-char name: `extra_bytes
    (len) = 2*(min(len,8)-4)` for `4<=len<=8`, `= len` for `len>8` — fits
    all 8 real data points (both sweeps) within rounding. The doubled rate
    in the first 4-char step, then a steady ~1 byte/char/item above that,
    is consistent with a real 8-byte-aligned minimum name-field allocation
    (matches the shape, though not the exact constants, of the already-
    wired AOI type-name-length bucket formula). **Real, general, and
    reproducible across two independent identifier classes (JSR target
    routine names, Program names) — genuinely new, not previously known,
    and NOT yet wired.** Needs the len=40 capture (in flight) to confirm
    the fit holds at the real Rockwell maximum before committing to
    exact constants, and a decision on whether this generalizes to
    Routine names too (untested) or is specific to JSR-target/Program
    identifiers.

    **WIRED 2026-09-12. The len=40 capture this was held open waiting for
    had already landed** — `jsr_multi_distinct_targets_namelen40` and
    `program_multi_distinct_namelen40` are both in the manifest with
    `error_count = 0`, and the fit holds at Rockwell's real identifier
    maximum. Per-identifier cost relative to a 4-character name, 10
    identifiers per file:

    | name length | 4 | 8 | 16 | 32 | 40 |
    |---|---:|---:|---:|---:|---:|
    | JSR targets | 0 | +8 | +16 | +32 | +40 |
    | Programs | 0 | +8 | +16 | +32 | +40 |

    Above 8 characters the cost is exactly the character count — 1 byte per
    character, no bucketing, unlike the AOI type-name and alias-tag formulas
    which both bucket. At 4 characters it is zero, not 4. Wired as ONE shared
    `identifier_name_length` in `memory_model.yaml`, used by both the
    JSR-target declaration and the Program shell, because the whole finding
    is that two independent identifier classes agree:

        name_bytes(len) = 0               for len <= 4
                        = 2 * (len - 4)   for 4 < len <= 8
                        = len             for len > 8

    Results: all five `program_multi_distinct_namelen*` rows went from
    `0 / −80 / −160 / −320 / −400` to **exactly 0** — Programs had no
    name-length term at all, so len=40 was under-predicting by 400 bytes on
    10 programs. All five `jsr_multi_distinct_targets_namelen*` rows collapsed
    onto a **uniform +200** (was +240 at len=4, +200 elsewhere): the JSR path
    already had a straight `1 × len` term with the right slope but no floor,
    and with the floor applied there is no name-length signal left in that
    residual at all — the remaining flat +200 is the separate per-target
    under-charge (OQ-JSRPARAMCOST). `jsr_crossed_n20/n40_namelen16/32` are
    unchanged, correctly: they were already flat in name length. Corpus exact
    predictions 1,031 → 1,040.

    **Two things the wired law does not rest on measurements for. 24 files
    built** (`src/sample_gen/gen_identname_closeout.py`):

    - **A, `identnamelen_prog_c01..c12`** (12 files). The law is two pieces
      meeting at 8 characters and the sub-8 piece is a straight line drawn
      between two anchors (0 at 4 chars, 8 at 8 chars) with **no data of its
      own**. Real Logix names that short are common, so this sweeps every
      length 1..12 directly, 10 Programs per file. Programs rather than JSR
      targets deliberately: the Program sweep reconciles at exactly 0 across
      its whole range, so any deviation is pure name-length signal, whereas
      the JSR sweep's flat +200 would have to be subtracted first.
    - **B, `identnamelen_rtn_c{01,04,08,12,16,32,40}`** (7 files). Whether
      the law generalizes to plain ROUTINE names, which this entry flags as
      untested. `routine_extra` has no name-length term, exactly as
      `program_extra` had none. If plain routines follow the same law they
      need the same wiring; if they do not, the law belongs to **scheduling
      and call targets** (Programs, JSR targets) rather than to every named
      object — a materially different rule that changes where else it should
      be applied. The routines are uncalled on purpose so the JSR-target
      declaration path cannot contribute.
    - **C, `identnamelen_task_c{04,08,16,32,40}`** (5 files). Tasks are the
      third identifier in the same shell formula (`task_extra`) and the only
      one whose name no sweep has ever varied. Each extra Periodic task
      schedules one Program held at a fixed 16-character name so only the
      task name moves.

    The engine currently predicts a **flat** total across every file in B and
    C, which is the hypothesis under test: flat captures confirm the law is
    specific to scheduling/call targets, varying ones say it is general and
    two more terms need wiring.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.

    **CLOSED 2026-09-14 (capture-batch segment 9). 19 of 19 rows byte-exact,
    against 7 of 19 before. Two corrections, and the second one was invisible
    until both arms were read together.**

    **1. The law is a STEP, not a ramp: `8 * floor(namelen / 8)`** per
    identifier -- the same form the project already uses for tag, UDT and
    AOI-definition names, so there is now one name law rather than two. The
    previous three-regime fit (0 below 5 characters, 2/char to 8, then 1 x len)
    was anchored at 1, 4, 8, 16, 32 and 40, and the new law agrees with it at
    **every one of those anchors**. It was wrong only across the interval it had
    to interpolate -- which its own entry described as "an interpolation between
    two anchors rather than measured", and which is exactly what this sweep
    measures:

        len   old (ramp)   measured (step)
          5            2                 0
          6            4                 0
          7            6                 0
          9            9                 8
         12           12                 8

    `identnamelen_prog_c{01..12}` carries 10 Programs at each length and reads
    25,688 flat for lengths 1-7 then 25,768 flat for 8-12 -- seven files at seven
    lengths on one total, then five files at five lengths on another. A ramp
    cannot produce that.

    **2. ORDINARY routines pay it too, and only JSR targets were being charged.**
    `identnamelen_rtn_c{01,04,08,12,16,32,40}` carries 10 non-JSR routines and
    reads 0 / 0 / 80 / 80 / 160 / 320 / 400 over its baseline -- 8 bytes per
    routine per bucket, identical to the per-program rate. The engine predicted
    those seven files FLAT, because routine names were charged only through
    `jsr_target_declaration`.

    **3. The n-1 convention is PER PROGRAM for routines, per project for
    programs** -- and this is the part neither arm could settle alone. Charging
    routines with a flat project-wide n-1 makes the `rtn` arm exact and
    over-charges every `prog` file by exactly 80. The two arms distribute the
    same routine count differently: `rtn` puts 11 routines in ONE program (10
    charged), `prog` puts 11 routines across 11 programs, one each (none
    charged). The first routine in each program is inside the baseline
    `fixed_base_per_routine` was fitted against, which is also what keeps
    `identnamelen_rtn_c01` and `_c04` exact at zero.

    **Effect on the real set: slightly worse, and the change is still right.**
    1.6091% -> 1.6112% mean, +1.2261% -> +1.2417% sum-weighted. The step law
    lowers the charge for every 9-15, 17-23 and 25-31 character name, real
    programs are full of them, and the real set under-predicts -- so removing an
    over-charge costs the headline. That is the fifth time today the same
    arithmetic has appeared, and the reasoning is the same: the old value was a
    self-documented interpolation, this one is measured on a sweep built to
    measure it, and 19 of 19 rows land on the byte.

    **Still open: the TASK arm.** `identnamelen_task_c{04,08,16,32,40}` (5 rows)
    was never captured, so whether a Task's own name follows the same law is
    untested. Those are the 5 errored/uncaptured rows this segment carried.


14. **OQ-193ECMETR** — new, real, genuinely undiagnosed (now covering TWO
    catalogs — see the correction below). 2026-09-02, real Studio
    5000 error on `composite_realistic_v2_18`/`_50` ("Error:
    TestMod2_193ECMETRA: Child module incompatible with parent module").
    Self-audit (checking for real currently-unreconciled `error_count`
    data per CLAUDE.md's standing rule, not just the composite files
    originally reported) found this is NOT composite-specific: BOTH standalone
    `modulesweep_193_ecm_etr_a`/`_b` already carry a real `error_count=1`
    in `manifest.csv` — sitting there uninvestigated since capture, never
    previously flagged. No real Studio 5000 error-log line exists for the
    standalone repro (only the composite-context quote above), so the
    exact cause is unconfirmed — plausible candidates (EKey/revision
    mismatch between the extracted 1756-EN4TR adapter and the E300 relay
    child, or the E300 family needing a different real parent device
    entirely) are just guesses, not verified. Excluded from
    `gen_composite_realistic.py`'s module pool
    (`_UNDIAGNOSED_COMPOSITE_CATALOGS`) so future composite files stop
    reproducing it. Needs the real per-file Studio 5000 error-log detail
    (not just the generic error line already quoted) to actually
    root-cause.

    **CORRECTION, same day, within the hour:** `2198-S130-ERS3` was
    initially diagnosed below as "requires a safety-capable controller"
    and wired into `_SIL2_CATALOGS` — DISPROVEN by real evidence almost
    immediately after: a real production file
    (`TitusvilleTrimmer_20260902r2.L5X`) runs a real `2198-D057-ERS3`
    module (`EM113_TrimmerLC_EM109_TrimInfdLC`) on a plain non-safety
    1756-L82E (`<SafetyInfo/>` empty, no SafetyTask anywhere) —
    `SafetyEnabled="false"`, no `SafetyNetwork`, structurally the same
    shape this project's own genericized block already uses. An
    "-ERS3" catalog genuinely CAN run on a non-safety controller for
    real, so the safety-controller theory is wrong. Reverted out of
    `_SIL2_CATALOGS`. The real `error_count=2` signal on
    `modulesweep_2198_s130_ers3` (and the clean 7/7 correlation across
    every "-ERS3" catalog in the corpus) is still real and still
    unexplained — `2198-S130-ERS3` moves into the SAME genuinely-
    undiagnosed bucket as `193-ECM-ETR/A`/`/B` above
    (`_UNDIAGNOSED_COMPOSITE_CATALOGS`) rather than standing on a second
    guessed theory.

    **SOLVED 2026-09-06, and the lead above was close.** The genericized
    `-ERS3` blocks were indeed missing something the real modules carry: the
    `<ExtendedProperties>` element (Vendor, CatNum, FeedbackDevice1-4,
    ConfigID), plus a corrupted ConfigData payload of 119 L5K values against
    the real 118. Both confirmed by diffing against
    `composite_realistic_v4_001`, which carries the same catalogs on a plain
    non-safety 1756-L81E and captured at zero errors — one of 31 such files.
    The `<ExtendedProperties>` fix had already been made on 2026-09-03 in
    `gen_module_motion.py`'s `_drive_module_xml()`;
    `gen_module_sweep_variants.py` keeps a separate hardcoded copy of the
    module XML and never received it. Full entry in RESOLVED_QUESTIONS.md.

    **Worth recording, because it cost real time:** the safety-controller
    theory was disproven here, in writing, with real evidence — and was then
    re-derived from scratch two weeks later and briefly wired into a lint
    rule that flagged the known-good files. The disproof was in this
    document the whole time. Read the correction before re-opening a
    question, and check the repo for files that already work before
    theorising about why one does not.

    **New real evidence, 2026-09-03 — the "missing Motion/Axis
    association" lead above is now DISPROVEN too.** All 50
    `composite_realistic_v3_*` files hit the exact same 2-error signature
    on real Studio 5000 conversion: `Tag 'D012_23:SI': Invalid
    data type for safety tag` + `Project size exceeds controller
    capacity` — 2 errors, matching the "clean X/X correlation" pattern
    already noted above for other "-ERS3" catalogs. Critically, v3's
    `2198-D012-ERS3` module is NOT missing a Motion/Axis association the
    way `modulesweep_2198_s130_ers3` was — it's dual-axis-bound (2 real
    `AXIS_CIP_DRIVE` tags, `MotionModule="D012_NN:Ch1"`/`"...Ch2"`,
    matching `gen_module_motion.py`'s already-real, already-confirmed
    shape) plus a shared MOTION_GROUP tag, and STILL hits the identical
    error. So the "needs a real axis" theory doesn't hold either — every
    "-ERS3" catalog this project has ever generated fails this way
    (with or without an axis bound), while only a real
    Titusville production file has ever shown it working. Direct,
    attribute-by-attribute comparison of a real `2198-D057-ERS3`
    Module block (from Titusville) against this project's generated
    `2198-D012-ERS3` block found them structurally near-identical
    (same Ports/EKey/Communications/Connections shape, same
    `SafetyEnabled="false"`, no `SafetyNetwork`) — the one confirmed
    difference is the real block's `<ExtendedProperties>`
    (`Vendor`/`CatNum`/`FeedbackDevice1-4`/`ConfigID`) is entirely absent
    from every generated instance, but that can't be confirmed as the
    cause either: `gen_module_sweep_variants.py`'s own real-corpus-
    verbatim `2198-D012-ERS3` "2conn" block (source:
    `motion_p208/p208_D012_NodeAndAxisDual3.L5X`, a real reference
    export) ALSO has no `<ExtendedProperties>` and the exact same zeroed
    `ControllerToDriveConnectionSize`/etc. diagnostic fields our
    generator produces — meaning that shape was already confirmed real
    once, not a generator bug in itself, so a missing `ConfigID` isn't a
    safe conclusion without a same-catalog real counter-example that DOES
    import clean. Still needs the raw Designer error-log detail (not
    l5xgit's one-line summary) or a same-catalog Titusville-style real
    file confirmed to import successfully in isolation to make further
    progress — not re-guessing a third theory here. `Project size exceeds
    controller capacity` is unconfirmed whether it's a second real issue
    or a downstream artifact of the first import failure (this project's
    own established pattern elsewhere: a primary import failure has
    previously been found to silently produce a second, misleading
    symptom — see the IP-duplicate/axis-tags-never-made finding,
    2026-08-27, `gen_module_motion.py`).

    **Real generator bug found and fixed, 2026-09-03 — root cause of the
    SI/SO error still NOT confirmed, but a real, independently-confirmed
    channel-numbering mistake found and corrected along the way.** This
    project's own real source file for the dual-axis case
    (`motion_p208/p208_D012_NodeAndAxisDual.L5X`/`Dual3.L5X`, which
    `gen_module_motion.py`'s own docstring claims to genericize
    "structurally verbatim") uses `MotionModule="D012_1:Ch1"` and
    `"...Ch3"` for its two axis tags — **never Ch2.** Both
    `gen_module_motion.py`'s `group_motion_dual_axis_drive()` and
    `gen_composite_realistic_v3.py` had instead hand-typed `Ch2` for the
    second axis — a real transcription bug, confirmed independently
    against 2 real corpus files, not a guess. Fixed (Ch2 -> Ch3 in both
    places), all affected files regenerated, lint-clean.

    **CORRECTION, same day, within the hour:** initially theorized Ch2
    might be internally reserved for the drive's Safe-Torque-Off/safety
    channel, explaining the SI/SO auto-creation — disproven
    immediately by two more real reference exports
    (`SampleAxis.L5X`/`SampleAxis_2and4.L5X`): a real 4-axis Kinetix 5700
    config genuinely uses all 4 channels — Ch1/Ch3 carry the two real
    motor axes (`AxisConfiguration="Position Loop"`), Ch2/Ch4 carry their
    paired **Feedback-Only companion axes** (`AxisConfiguration="Feedback
    Only"`, `FeedbackConfiguration="Master Feedback"`, no motor/tuning
    params at all) — legitimate, ordinary channels, nothing safety-related
    about them. So Ch2 itself isn't the problem; the real, still-open
    question is why our generator's ORIGINAL mistake (a full
    `Position Loop`-configured axis tag placed on Ch2, a slot real
    Kinetix 5700 configs use for a structurally DIFFERENT
    `Feedback Only`-shaped axis) specifically produced a SAFETY-tagged
    error rather than some other kind of mismatch error. The Ch1/Ch3 fix
    still stands (matches 2 independent real corpus captures exactly for
    a 2-declared-axis file), but calling it "the fix for the SI/SO
    error" is not yet confirmed — needs a real ACD retest of the
    regenerated files to know whether it actually clears that error or
    just happens to also be correct for an unrelated reason.

    **Real symptom clarified, real second bug found and fixed, still
    2026-09-03.** A retest of the Ch2->Ch3 fix (`modulemotion_
    d012_dual_axis.L5X`) gave the same 2-error signature, and clarified the
    actual crash: opening the **module's own I/O-tree profile page**
    (not the axis properties page) crashes Studio outright -- confirmed
    by testing the original, unmodified real source file
    (`p208_D012_NodeAndAxisDual.L5X`, the one this project's D012 module
    block is extracted from) side by side: **that file opens fine.**
    Definitive proof the bug is in how this project's own pipeline
    reassembles the real content, not in the real content itself. A
    precise structural diff (whitespace-normalized, identifiers scrubbed)
    against that real file found a second real, concrete bug: `_axis_tag`
    -- the ONE helper this project used to build every axis tag -- was
    also being used to build P208's own on-board "DC BUS" axis, but a
    real DC-bus axis is a structurally DIFFERENT, much shorter
    `AxisConfiguration="Non-Regenerative AC/DC Converter"` shape with no
    servo-tuning parameters at all -- nothing like the full `Position
    Loop` servo template `_axis_tag` always applied. Every P208 axis this
    project has ever generated (5 `modulemotion_*` files, all 50
    `composite_realistic_v3_*` files, all 18 `axis_scale_*` files) has
    been structurally malformed this way -- the leading real suspect for
    the module-page crash, though NOT yet confirmed (the P208 module was
    ruled out independently of this fix, before it was applied -- still
    needs a retest of the regenerated file to know either way).
    Fixed: new `_dcbus_axis_tag()` helper using the real, verbatim-
    extracted DC-bus shape, wired into all 3 generators
    (`gen_module_motion.py`, `gen_composite_realistic_v3.py`,
    `gen_module_axis_scale.py` -- the last one had never been checked
    against this bug before). All affected files regenerated, lint-clean,
    177/177 tests passing.

    **Two separate, real bugs found and fixed the same pass, NOT this
    one:**
    - **Sequential slot numbering.** Many racks did not use slot numbers in
      sequence; a lint check for this was added.
      `gen_composite_realistic.py`'s `_modules_xml_unique_ips` keyed each
      catalog's assigned Local-ICP backplane slot off its raw index in the
      file's full catalog list (`slot=2+i`), regardless of whether that
      catalog even has an ICP-backplane root module — an Ethernet-only
      catalog between two ICP catalogs silently consumed an index without
      consuming a slot, leaving a real gap (confirmed real example:
      `composite_realistic_22_r2.L5X`, slots 3 and 5 present, 4 missing).
      Also always started at slot 2, one too high — `wrapper.py`'s own
      Local module template puts the CPU's downstream ICP port at
      `Address="0"` in every branch, so the first real expansion module is
      physically slot 1. Fixed: only catalogs whose block actually
      contains a Local-ICP root module consume a slot, numbered
      sequentially from 1 with no gaps. New lint check added,
      `non_sequential_module_slots` (`sample_gen/lint.py`
      `_slot_sequence_findings`) — flags any (ParentModule, PortId) group
      of 2+ modules with numeric addresses that isn't a contiguous run, so
      a future generator can't reintroduce this silently. (Also flags 2
      pre-existing `modulerack_1756_local`/`_remote` files not touched by
      this fix — those may be intentionally sparse racks, not bugs; not
      changed, flagged for confirmation before any future regen.)
    - **"Safety-rated module in a non-safety-declared composite"
      (`2198-S130-ERS3`, `composite_realistic_v2_19`/`_30`)** — this WAS
      diagnosed and fixed here initially, then disproven within the hour
      by real evidence. See the CORRECTION under OQ-193ECMETR above for
      the full story: it's genuinely undiagnosed, not a safety-controller
      requirement, and now sits in the same exclusion bucket as
      `193-ECM-ETR/A`/`/B`.


    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.

15. **OQ-V3GENBUGS** — three real generator bugs found via the actual
    Studio 5000 ACD-conversion errors on the v3 composite batch (50 files,
    2026-09-02), all root-caused to the exact reported symptom and fixed:
    `_LOCAL_ICP_SLOT_RE` crossing `<Module>` boundaries in DOTALL mode
    (corrupted an unrelated child module's valid ICP slot when the "root"
    module's own port didn't match), `lint.py`'s `_module_slot_findings`
    treating a real, valid nameless `<Module>` (e.g. `1756-OF8/B`) as
    invisible to slot-collision checks, and an IPv4 4th-octet overflow in
    `_modules_xml_unique_ips` (`base = 60 + (i+1)*10` broke past ~19
    catalogs/file — v3 routinely has 15-34). All three fixed and covered
    by new regression tests (`tests/test_gen_composite_realistic.py`).
    New test batches this same pass, all lint-clean and pushed:
    `composite_realistic_v3_*` (50, deliberately wide-varying program/AOI/
    subroutine counts — see [^compositescale] — built specifically to
    re-derive the JSR/AOI composite-scale surcharge that over-generalized
    at Titusville's real 179-distinct-JSR-target scale, see OQ-JSRSCALE
    below), `axis_scale_*` (18, single/dual-axis 2198 servo drive counts
    1-20 ± regen), `rack_5069_*` (11, real `Remote5069.L5X`-derived AENTR
    multi-child racks), `rack_pointio_*` (11, real `1734-AENT/B` multi-slot
    adapter), `rack_1756_*` (12, local-rack size scaling 2-16 modules),
    `cipmodule_scale_*` (7, CIP-MODULE declared-I/O-size sweep 64-2048
    bytes, anchored against Titusville's real 496-byte `IO_Optm` instance),
    `bridge_placeholder_*` (2, real zero-connection `ETHERNET-BRIDGE`
    IP-only fan-out node). None of these have real capture data back yet
    (ACD conversion still being validated as of 2026-09-02) — no sizing
    formula changes from this item, generator-correctness only.

    **2026-09-12: that status was stale and the answer is bad.** Every one of
    the 133 rows across the seven families named above is captured, and **65 of
    them captured WITH Studio build errors**:

    | family | rows | convert ok | captured | captured WITH errors |
    |---|---:|---:|---:|---:|
    | `composite_realistic_v3` | 50 | 50 | 50 | **49** (exactly 2 each) |
    | `axis_scale` | 18 | 18 | 18 | **18** (n+1 single, n/2+1 dual) |
    | `rack_5069` | 34 | 34 | 34 | 0 |
    | `rack_pointio` | 12 | 12 | 12 | 0 |
    | `rack_1756` | 12 | 12 | 12 | 0 |
    | `cipmodule_scale` | 7 | 5 | 5 | 0 — **2 never attempted, files gone** |
    | `bridge_placeholder` | 2 | 2 | 2 | 0 |

    The three racks and the bridge are clean and can be used. The other two
    cannot be used as they stand.

    `axis_scale`'s signature is **one error per axis plus one** — exactly the
    pattern CLAUDE.md cites as the reason the step-2b gate exists. It routes to
    OQ-AXISMARGINAL, which already carries it.

    **`composite_realistic_v3` is the new one, and it taints another
    question.** 49 of 50 files carry **exactly 2** errors, constant across a
    batch whose size spans 1.3–1.9 MB and whose programs (5–12), AOIs (5–24),
    modules (17–34) and routines all vary widely. A count that scales with no
    content dimension is two discrete template defects, not a per-item problem.
    And v3 was built specifically to re-derive the composite-scale JSR/AOI
    surcharge, so **OQ-COMPOSITESCALE's re-derivation is standing on 49 suspect
    rows.**

    Structural inference was tried and did not find it. Recorded so it is not
    repeated:

    - v3 declares four catalogs v4 does not (`1756-OA16I`, `1756-OF4/A`,
      `1756-OF8/B`, `1794-IB16/A`). **All four, plus `1794-ACN15/C` and
      `1756-CNB/D`, have their own standalone `modulesweep_*` capture at zero
      errors.** No single catalog is the offender.
    - Nameless `<Module>` elements are not it: v3_12 has 3 and errors,
      v4_013 has 8 and is clean. They are legitimate drive-peripheral and
      POINT I/O sub-modules, so the earlier decision to teach lint to tolerate
      them was right.
    - The one clean file, `composite_realistic_v3_13`, is not structurally
      special — 11 programs, 18 AOIs, 48 modules, 4 axes, mid-range for the
      batch. Its immediate neighbours v3_12 and v3_14 both error.
    - **v4 is clean**: 31 captured rows, 0 errors, from a successor generator
      whose files are bigger (97 modules, 14 axes against v3's 48 and 4). So
      the defect is specific to the v3 template, not to composite files.

    **8 files built to name the subsystem by measurement**
    (`src/sample_gen/gen_v3_error_ablation.py`): profile 12 — a known 2-error
    profile — with one subsystem removed per file (`v3abl_control`, `noaoi`,
    `minudt`, `nomodules`, `noprograms`, `norungs`, `nostrings`, `minarrays`).
    The arm that drops to zero errors names it. Every arm lands within 2 bytes
    of the same 1.75 MB total because the generator pads to a target size, so
    project size cannot be the confound — only the removed subsystem varies.
    The control must reproduce the 2 errors or the v3 template has moved since
    those captures and the whole batch needs recapturing before anything else
    is concluded from it. If every arm still shows 2, the defect is in the
    fixed scaffolding no ablation touches — the motion block, MainProgram, or
    controller header — and the next step is **the raw Studio 5000 error-log
    line** for one v3 file rather than more inference.

    **A real sizing bug found while building that batch and FIXED.**
    `parser/modules.py`'s `_ATOMIC_BYTES` was a hardcoded literal listing only
    the SIGNED atomics, so every module member declared `USINT` / `UINT` /
    `UDINT` / `ULINT` fell through to `unknown_member_types` and the module's
    size came back as an explicit floor instead of a real total — two modules
    in the v3 template (`AL1122`, `AL1222`) have 25 such members each. All four
    types are standard Logix atomics already present in `memory_model.yaml`'s
    `atomic_types`, and they are not rare: **109 committed sample files declare
    them, and all four appear in the real production corpus** (25 `UINT`, 20
    `USINT`, 16 `UDINT`, 9 `ULINT` member declarations). The table now derives
    from the model, so this cannot recur for a type the model already knows —
    which is what CLAUDE.md's no-hardcoded-sizes rule exists to prevent.

    **ABLATION CAPTURED 2026-09-14 (segment 24) AND IT CANNOT BE DIFFERENCED.
    That is itself the finding about the v3 template. BLOCKED.**

    Each `v3abl_*` variant is supposed to remove exactly one feature from a common
    control. `v3abl_noprograms` has 2 programs against the control's 10 and 690
    rungs against 2,013 -- and is **larger on disk than the control**, 14.66 MB
    against 13.99 MB. Removing eight programs and two-thirds of the rungs cannot
    increase a project, so the variant changes more than the feature it names.

    The totals say the same. Predicted is near-constant across all eight variants
    (1,745,740 to 1,749,057) while actual ranges 1,686,379 to 1,748,759, so the
    engine is blind to whatever actually differs between them.

    Two further problems on the same eight rows. `v3abl_minarrays` has a **blank
    `error_count`** -- never recorded -- so its -62,678 is suspect on top of being
    undifferenceable. And `v3abl_noprograms` reading -296 against the control's
    -34,961 invites exactly the wrong conclusion ("the whole error is program
    content") from a comparison that is not valid; it is recorded here so that
    reading is not reached a second time.

    **Needed: the ablation rebuilt so each variant removes only its named feature,
    with the control's content otherwise byte-identical.** Until then no `v3abl_`
    row may be differenced and the ~2% error on these files stays attributed to
    nothing.


16. **OQ-JSRSCALE / OQ-COMPOSITESCALE** — the composite AOI/JSR surcharge.
    **REFITTED ON REAL PROGRAMS 2026-09-04. Was the project's #1 error
    source; is now its largest remaining one, but 5x smaller.**

    supplied real Capacity readings for 8 whole real customer
    programs, joining `Cardin_TrimSortStack` for **9 real data points** —
    the first time this question has had more than one. Under the old model
    (`aoi=20`, `jsr=47`, file-wide cap 12,000) **all nine under-predicted**,
    by +8.35% to +30.63%, aggregate **+12.62%**, mean |error| **14.95%**.

    The driver was identified BEFORE anything was refitted, deliberately —
    correlating each real file's residual against every measurable
    candidate:

    | driver | corr | | driver | corr |
    |---|---:|---|---|---:|
    | JSR-target instructions | **+0.813** | | routine count | +0.769 |
    | all RLL instructions | +0.805 | | controller tags | +0.514 |
    | unweighted instructions | +0.524 | | AOI-internal instructions | +0.203 |
    | **ST source lines** | **−0.396** | | **unsized modules** | **−0.255** |

    So the residual is JSR-target logic content, and it is NOT unmodeled ST
    (negative) and NOT the unsized rack-aliased modules (negative). That
    matters: it rules out the two most tempting alternative explanations
    before the surcharge was touched, which is the check that was missing
    when the drive-bus discount got fitted on bad data and had to be
    reverted.

    Refit: least squares of (actual − prediction-with-no-surcharge) on
    [aoi_instr, jsr_instr] over all 9 real files → **52.52 / 20.81**,
    rounded to **52 / 21** with no meaningful loss. **Cap disabled** (0) —
    it was a patch for a jsr rate 2.3x too high, and at real scale it was
    suppressing 252,749–1,260,885 bytes per file, which IS the +12.62%.

    Leave-one-out over the 9 (fit on 8, predict the 9th): **mean |error|
    3.83%, max 9.41%**. Two rates beat one combined rate (same mean, max
    12.78%) and a JSR-only rate (4.86% / 17.69%), which is why both are
    kept.

    Result: real programs **14.95% → 3.29%** mean, aggregate **+12.62% →
    −0.41%**, 2 of 8 now inside ±1%. Cost, stated not buried: the 176
    corpus rows carrying AOI/JSR content go 3.09% → 3.57% and the whole
    1,885-row corpus 1.378% → 1.423%. The synthetic composites and the real
    programs genuinely disagree about this law; this trades a rounding
    error on the instruments for a 5x gain on the thing the project exists
    to predict, per CLAUDE.md's North Star.

    **STILL OPEN, and this is the main remaining gap:** 3.29% is not <1%,
    and leave-one-out says expect ~3.8% on a file nobody has seen. The two
    worst are `MurrayBros` (+7.43%, the smallest file at 923 KB) and
    `K3M16_Edgers` (+5.55%) — both still UNDER — against `Pukall_Gang`
    (−5.44%) OVER, so the remaining error is not a single sign and not a
    simple scale term. What is needed: **more real programs** (each one has
    been worth more than any synthetic batch), and the captures for the
    already-generated `realscale_jsrtgt_xic_n*` ladder, which is the only
    thing that can separate per-instruction cost from per-target and
    per-routine cost at real scale.

    **IN-DEPTH REVIEW 2026-09-18 — the composite residual is IDENTIFIED, and
    it is not a composite effect at all.** The `addit_*` additivity grid
    (33 captured rows) was built to ask whether categories interact. It
    answers cleanly, and the answer relocates this question.

    Every grid cell was re-evaluated live against the current engine and
    sorted by its logic dimension L (rung count 0 / 400 / 4000):

    | L | cells | residual range | per-rung |
    |---:|---:|---|---:|
    | 0 | 3 | −40 … 0 | — |
    | 400 | 4 | −9,332 … −9,848 | −23.3 … −24.6 |
    | 4000 | 10 | −95,732 … −96,248 | −23.93 … −24.06 |

    So the residual is **−24 per rung, at two scales an order of magnitude
    apart, across 10 independent cells**, and it is **entirely carried by the
    L dimension**. Hold L at 0 and every combination of D (UDT definitions),
    A (AOI definitions/instances) and M (modules) reads within 40 bytes of
    zero. Vary D, A or M at fixed L and the residual does not move by more
    than ±300. **The categories ARE additive.** There is no composite
    surcharge to fit; there is one mispriced ladder term that composite files
    happen to contain a lot of.

    And that term is already known. The grid's rung shape is

        XIC(Bit0)MOV(1,Dst0)ADD(Dst0,1,Dst0)OTE(Bit1);

    which is **three writing instructions** (MOV, ADD, OTE). −24/rung is
    exactly **−12 × (3 − 1)** — the OQ-SERIESOUTPUT law, at a rung width
    nothing else in the corpus tests. `addit_*` is therefore the **third
    independent confirmation** of that law, after the `srout_*` sweeps
    (k = 1…8, 16 rows byte-exact) and `ntag_uidpair` (k = 2). Three unrelated
    synthetic families, built by different generators months apart for
    different questions, all land on −12 per extra output.

    This sharpens rather than resolves the central contradiction. The same
    −12 that is byte-exact on three synthetic families takes the sixteen real
    programs from 1.6894% to 3.2167% and makes every one worse. The refitted
    52/21 AOI/JSR surcharge above is now best understood as **a proxy that
    absorbs the real files' side of that contradiction** — it is fitted on
    real files, where the −12 does not appear, so it is soaking up whatever
    real ladder does that synthetic cascades do not. That is why the
    surcharge costs the corpus 1.378% → 1.423% while paying 5x on the real
    set: the two sets disagree about one specific thing, and both terms are
    fitted to opposite sides of it.

    **Consequence for the plan.** Refitting the 52/21 surcharge harder cannot
    reach 1%, because it is compensating for a term it does not name. The
    decisive measurement is the `sroutc_c{1,2,4}_k{1,2,4,8}` grid (arm A of
    `gen_oq_closeout.py`, 12 files, built and awaiting capture), which is the
    only thing in flight that separates output count from condition count
    inside one rung. If the discount is a function of the condition/output
    RATIO rather than the raw output count, the real files — which carry many
    conditions per output — sit where the discount is near zero, the
    synthetic cascades sit where it is −12, and both sets are describing the
    same law. That is the single hypothesis that reconciles them, and one
    capture batch tests it.

    Until then the surcharge stays at 52/21 and OQ-SERIESOUTPUT stays
    `apply: false`. Neither is right; together they are the least wrong
    configuration measured.


17. **OQ-AXISCOMBO** — cited in RESOLVED_QUESTIONS.md (OQ-AXISSTRUCT,
    OQ-AXISDEEP) as "the one remaining piece," but no item by this name —
    or covering this ground — was ever actually created here. A real
    doc-sync gap, not a resolved one. Chasing it down surfaced a second,
    more substantive gap: OQ-AXISSTRUCT's real Capacity numbers don't
    match what's already wired into `memory_model.yaml`'s
    `predefined_structures` from OQ-PREDEFINED. Correction to the record:
    axis content is NOT "100%-blind, priced at exactly $0" as previously
    stated — AXIS_CIP_DRIVE/AXIS_SERVO/AXIS_VIRTUAL/
    COORDINATE_SYSTEM are wired and sizing without error today (FITTED,
    single-sample-each). See footnote for the actual unreconciled numbers
    and what's needed to close this for real.

19. **OQ-EXPORTSCOPE** — new, 2026-09-04. The estimation path has to handle
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

22. **OQ-BUILDFAIL-OPEN** — the 11 sample files that genuinely still fail to
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

43. **OQ-REALUNDER** — new 2026-09-12, and it is still the single biggest
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

23. **OQ-DEFSCALE** — definition- and instance-count scaling. **CAPTURED
    AND RECONCILED 2026-09-11, all 30 files, zero import errors. Four exact
    linear laws, none of them wired, and the reason is a confound, not a
    doubt about the numbers.**


    **IN-DEPTH REVIEW 2026-09-18. One term wired exactly, one measured exactly
    and BLOCKED by a confound that runs through the whole corpus.**

    **(a) An AOI DEFINITION is over-charged 7, not 3. Wired, KNOWN.**
    `defscale_aoidefs_n{001,002,005,010,020,040,060}` varies only the definition
    count and carries no instances at all, so it reads the definition term
    alone:

        definitions   1    2     5     10     20      40      60
        residual     -4   -8   -20    -40    -80    -160    -240

    Exactly 4 per definition beyond the 3 already applied, at all seven counts.
    The original −3 came from ONE file, `dscale2_aoi_d060_t060`, solved jointly
    with the per-instance −8 from that same file — and a single file cannot
    separate two per-unit terms. It did not. With −7 wired, all seven rows are
    byte-exact. Corrected in `definition_scale_correction`, not in
    `aoi_definition.base`, because the base is what one definition costs and
    this is the term that scales with how many there are.

    **(b) An RLL routine containing AOI calls carries a one-time ~260, and it is
    the SAME constant the ST side carries at 264 — but it CANNOT be wired.**

    `dscale2_aoi_d001_t{001..100}_call` reads a flat **+260** at every target
    count from 1 to 100. Flat across a 100x span means once per file or once per
    routine, not per call or per instance. `defscale_aoiinst_n{001..060}` reads
    `+260 − 4n`, the same 260 plus the per-instance term.

    That 260 is `st_aoi_call_routine_bytes` (264) seen in the other language,
    within the per-instance 4. **The RLL path has no such term at all.**

    **Why it is not wired: every generated file in the corpus that contains an
    AOI call — all 80 of them, both languages — has exactly ONE calling
    routine.** So "once per routine" and "once per file" fit every row
    identically, and on the sixteen real programs the two readings differ by
    **764 routines × 264 = 201,696 bytes against 16 × 264 = 4,224**. A 48x
    spread on a term large enough to move the headline. Guessing here would be
    the largest unforced error available in this model.

    **This also forced a correction to something wired earlier the same day.**
    `st_aoi_call_routine_confidence` was marked KNOWN when the ST batch closed;
    it is now **FITTED**, because the 264 is measured but its CARRIER is not.
    The ST side happens to be safe either way — 26 real ST routines against 16
    files is 2,640 bytes — but the tier was claiming more than the data
    supports, and the KNOWN register is what surfaced it.

    **What settles it: one file with AOI calls in TWO routines**, everything
    else held identical to `dscale2_aoi_d001_t002_call`. If the residual goes to
    520 it is per routine; if it stays at 260 it is per file. One file decides a
    200,000-byte term, and it unblocks the ST constant at the same time.

    All four sweeps came back perfectly linear with zero residual:

        defscale_aoidefs_n*    over-prediction = +3 x n          7 points
        defscale_aoiinst_n*    over-prediction = -264 - 157 x n  7 points
        defscale_udts_n*       over-prediction = -16 x n         8 points
        defscale_udttag_n*     over-prediction = -19 x n         8 points

    Subtracting the paired sweeps: an AOI **definition** is over-charged by
    **3** bytes; an **instantiated** AOI is under-charged by **160** per unit
    plus **264** once; a **UDT definition** is under-charged by **16**; a UDT
    that has a tag is under-charged by a further **3**.

    Applied to the sixteen real programs those four numbers give:

        mean |error|   2.17%  ->  1.63%
        within 1%          4  ->  6
        within 2%          9  ->  11

    and they move every file UP — the direction the real files need, and the
    opposite direction to OQ-MODULEMARGINAL's module over-charge. The two
    together are the clearest evidence yet that the real-file residual is
    composed of large offsetting terms rather than one missing cost.

    **Why it is not wired: every sweep varies two things at once.**
    `defscale_aoiinst_n` holds n definitions, each with exactly ONE instance
    tag AND exactly ONE calling rung, so n = definitions = instance tags =
    calls, and "160 per instance tag", "160 per AOI call" and "160 extra for
    a definition that is instantiated at all" fit all seven points
    identically. `defscale_udttag_n` holds n UDTs with ONE tag each, so "3
    per UDT tag" and "3 once for a UDT that has any tag" fit all eight.

    On a real program those readings are nowhere near each other. AccuTally
    carries 902 AOI instances across 39 definitions and 33,574 UDT tags
    across 174 UDT definitions:

        per instance / per tag   160 x 902 + 3 x 33,574  = +245,042
        per definition           160 x  39 + 3 x    174  =   +6,762

    238 KB apart on one file, 4% of it — the same structural ambiguity as
    OQ-MODULEMARGINAL's per-catalog-vs-per-file question, in a different cost
    category, and it gets measured for the same reason: on this project the
    tidier reading has been wrong before.

    **Test files built 2026-09-11, `gen_defscale2.py`, 39 files.** Every
    definition is built from `gen_defscale`'s own `_aoi_members()` /
    `_udt_members()`, so they are byte-identical to the captured sweep and
    difference straight against it. The model's own prediction is a perfectly
    straight line across every new sweep (112/instance tag, 101/UDT tag,
    20/AOI array element, 12/UDT array element, and **0 per call**), so any
    slope error or curvature in the capture is unambiguous.

    | arm | files | what is pinned | what it decides |
    |---|---:|---|---|
    | `dscale2_aoi_d001_t*_call` | 8 | 1 definition | slope is per-INSTANCE, not per-definition (1→100 instances) |
    | `dscale2_aoi_d001_t*_nocall` | 4 | 1 definition, no logic | splits the instance TAG from its CALL |
    | `dscale2_aoi_d001_t001_c*` | 3 | 1 definition, 1 instance | the converse: call count varies alone. The model charges 0 per call, so any movement here is pure call cost |
    | `dscale2_aoi_d*_t*_nocall` | 3 | — | `defscale_aoiinst_n{05,20,60}` minus its calling rungs, for a direct difference at real-file scale |
    | `dscale2_aoi_arr*` | 3 | 1 definition, 1 tag | per-instance or per-tag: an ARRAY of 2/10/50 instances |
    | `dscale2_udt_u001_t*` | 9 | 1 UDT definition | slope is per-TAG, not per-definition (1→500 tags) |
    | `dscale2_udt_u{005,025}_t*` | 5 | — | definition count x tag count crossed: additive or interacting |
    | `dscale2_udt_arr*` | 4 | 1 UDT, 1 tag | per-element or per-tag, 2→500 elements |

    `dscale2_udt_u001_t001` is byte-identical to the already-captured
    `defscale_udttag_n001` and is kept deliberately: it anchors the new
    sweep's intercept in the same capture run and doubles as a
    run-to-run reproducibility check.

    **Not covered, and reported rather than guessed:** program-scoped
    structure tags. A Program-scoped ATOMIC tag has a confirmed real shape
    (`program_tag_xml`, dual L5K+Decorated), but no real corpus file has been
    read for a Program-scoped UDT or AOI-instance tag — and real programs put
    most of their instances there. Building one from a guessed shape would
    put an unverified XML shape inside the experiment meant to settle the
    question. It needs a real export first.

    **The original framing of this item stands and is now confirmed rather
    than suspected.** Across all captured non-real files the maximum was 7
    AOI definitions and 6 UDTs, while the real programs carry 11–39
    definitions and 51–174 UDTs; the first batch to bracket them found an
    exact error at every point. What the first batch could not do was
    attribute it, which is what the 39 new files are for.


24. **OQ-SHELLCONST** — new, 2026-09-04, split out of OQ-SHELLSCALE. Two
    small CONSTANT (non-scaling) residuals the shell isolation exposed
    once the slopes were exact:

    - **−23 bytes** on every `shellscale_programs_*` and
      `shellscale_routines_*` file, dead flat from n=1 to n=200. A fixed
      per-file baseline offset, worth 0.09% at the small end and 0.03% at
      the large end. Too small to chase on its own, but it is real and
      exact, so it is probably one concrete unpriced item rather than
      accumulated rounding.
    - **−815 bytes** on all four `shellscale_crossed_*` files, also dead
      flat. These have the same Program and Routine counts as their pure
      counterparts (verified by element count) but come from a different
      generator, so something that generator emits — most likely the
      cross-program JSR wiring — costs 815 bytes that nothing prices. This
      one is worth identifying: 815 flat is 1.5% on a 54 KB file.

    Both are constants, not slopes, so neither affects the OQ-DEFSCALE
    reading above.

    **The `pool*` arm is CLOSED 2026-09-14 (segment 23). Nine rows, all nine
    inside the +-8 band, six byte-exact**: `control`, `bool03`, `dint04`,
    `real06`, `str82x2` and `strarr02` at 0, and `arr20`, `full` and `full_rungs`
    at +4. The two composed files are the point -- `full` and `full_rungs` carry
    every pool member at once and land in band, so the shell constants are
    additive and none of them needed changing.

    That does NOT close the two constants above: `pool*` is a different generator
    from `shellscale_*`, so the -23 and the -815 are untouched by it. The -815 in
    particular still wants identifying.


    **THE -23, LOCALISED 2026-09-12 -- and it is a TAG constant, not a shell or
    logic one.** A residual census over every clean generated capture: of 2,563
    files, 844 (32.9%) predict EXACTLY right and **263 (10.3%) sit at exactly
    -23**, by far the largest non-zero bucket. 23 is an odd number, which a
    memory allocation essentially never is.

    Narrowed in three steps:

      - 258 of the 263 contain real ladder rungs, so it looked like a logic
        term. It is not: the -23 is identical at 1 rung and at 27,267
        (`instr_*_n00010` and `randommix_00_n00609rungs` alike), so nothing
        about it scales with logic.
      - "Any file with logic" does not fit either -- among real-rung files 25.6%
        are at -23 and 20.2% are at exactly 0.
      - What separates the two groups is the **tag pool**. Every -23 family
        (`instr_*` 234 files, `shellscale_*`, `randommix_*`, `lbljmp_*`) shares
        one pool: 4 DINT, 6 REAL, 3 BOOL, a DINT[20], a CONTROL, a 2-element
        STRING array and two STRING(82). Every real-rung family at exactly 0
        (`cmpcpt_*`, `cptmix_*`) uses only DINTs, REALs and BOOLs.

    So this is a tag-sizing error. Two consequences: the instruction weights
    fitted from those 263 files are UNAFFECTED, because a constant pool cancels
    in every difference between counts -- but every absolute prediction carrying
    that pool is 23 bytes low.

    Already ruled out: the string shapes are exact. All 8 `customstring_*` files
    and every `stringarray_*` file (built-in and custom, n=1 to 100) predict to
    the byte. That leaves the **CONTROL** tag -- the only pool member with no
    isolation probe anywhere in the corpus -- and the DINT[20] array.

    **Test files built 2026-09-12, `gen_pool_residual.py`, 9 files.** Each pool
    member alone with no logic (`pool23_{dint04,real06,bool03,arr20,control,`
    `strarr02,str82x2}`), the whole pool with no logic (`pool23_full`), and the
    whole pool plus 10 XIC/OTE rungs (`pool23_full_rungs`). Differencing the
    seven single-shape files against `pool23_full` says which member carries the
    23; `pool23_full` against `pool23_full_rungs` pins it as pool-borne rather
    than logic-borne, since the two must read the same residual.

    Checked before shipping: the engine is internally additive here -- the seven
    parts sum to `pool23_full` net of the empty-project baseline with a
    difference of exactly 0 -- so the 23 is one of the seven constants being
    wrong, not an additivity failure, and each file measures one constant.

25. **OQ-VERIFINSTR** — **everything measurable from generated files is
    CLOSED and WIRED; see `docs/RESOLVED_QUESTIONS.md`.** The zero-operand half
    (MCR/TND/UID/UIE, 20 of 20 rows exact), the ten weights found unreconciled
    2026-09-12, `DTR = 40`, and the 112-per-target SBR/RET operand cost are all
    in the engine, with the last two in MEMORY_MODEL.md's KNOWN register.

    **What is left cannot be closed by a generated file, and needs one thing
    from James: a single verified rung apiece for `EOT`, `IOT`, `SFR` and
    `SFP`.** All four are real instructions with no entry in
    `logic_instructions.weights`, so every occurrence is charged zero.

    Files were written for them and WITHDRAWN rather than shipped, which is the
    part worth remembering:

    - `lint.py` rejects all four as unrecognized — accurately, since no real
      rung containing one has ever been verified into this project.
    - `SFR`/`SFP` address an SFC routine by name and this project's builders
      produce none, so the rung would name a routine that does not exist.
      Studio would reject that rung, the rest of the file would still import,
      and `actual_bytes` would still be filled in — the exact mechanism behind
      OQ-AOIINTERNALLOGIC's suspect calibration, arrived at deliberately.
    - `IOT`'s operand is a real output module reference and `EOT`'s an SFC
      storage bit, so both invented shapes are guesses.

    Per CLAUDE.md's transplant-never-compose rule these need one real rung each,
    not a composed one. Tracked in `docs/INSTRUCTION_COVERAGE.md`.

26. **OQ-CPTREALDEST** — REAL-destination CPT: two measured constants with
    no known mechanism. 2026-09-04. **Not blocking — the path is exact on
    all 47 captured calls — but both terms are descriptions, not theory,
    and a model you cannot explain is a model that will surprise you on a
    file you have not seen.**

    The ladder itself is clean and tier-blind: `124 + 40n`, and fitting
    `a + b*tier1 + c*tier2` against the opcount files returns b = c = 40
    (which makes sense — it is all float arithmetic, so a MUL should not
    cost more than an ADD the way it does on the integer path). Sitting on
    top:

    - **A 5-operator expression measures 328, not the 324 the ladder
      says.** Three files from three different generators
      (`cptmix_real*`, `cptcx_constants_floatconst_n4`,
      `instr_cpt_literaloperands`) independently agree on 328, and 6 and 8
      operators are back on the ladder exactly (364, 444). So it is not a
      ">= 5" step — the previous model had it as one and over-charged the
      6- and 8-operator files by 4 each.
    - **`**` adds 8, plus another 4 when the expression also contains a
      tier-2 operator**, and a pow expression does NOT get the 5-operator
      bump (`powmulti_n05` is 324+12, not 328+12).

    Two ad-hoc +4s is one too many to be comfortable. `cptrdops_n07/09/10`
    fills the ladder either side of the anomaly, `cptrdpow_k2/k3` tests
    whether pow_extra is per-operator or per-call (every existing real-dest
    pow file has exactly ONE `**`), and `cptrdarrange_*` tests whether the
    5-operator +4 is really the same arrangement effect OQ-CPTARRANGE found on
    the integer path, wearing a different hat (that question is now closed and
    archived in `docs/RESOLVED_QUESTIONS.md`). Blocked on capture.

    **IN-DEPTH REVIEW 2026-09-18 — the captures landed, and the FIRST thing
    they say is that every number in this batch had to be normalised before it
    could be read. Two of the sub-questions are now closed.**

    **(0) A per-file constant of −352 runs through the whole `gen_cpt_closeout`
    batch, and it is why this looked unreadable.** Of the 58 captured `cpt` rows
    from it, 53 sit at −352 plus a whole number of 4-bytes-per-rung; the other
    five — `cptwide_lint_k1..k4` and `cptwide_mixed_sint_lint` — sit on a
    baseline of **0**. The discriminator is exact and mechanical: **a file whose
    logic REFERENCES one of the pool's LINT tags has baseline 0; one that does
    not has baseline −352.**

    With that one substitution, **every one of the 58 residuals is its baseline
    plus an exact multiple of 4 bytes per rung. No exceptions.** That is what
    makes the batch usable, and it is also a warning: any conclusion drawn by
    differencing a file in this batch against a file from an OLDER generator
    carries a spurious 352, and several readings in this entry were contaminated
    that way before this was found.

    The −352 itself is NOT explained. It is numerically 4 × 88, the engine's
    charge for the four unreferenced LINT tags `N0..N3` that `gen_cpt_closeout`
    adds to the shared pool, so the arithmetic is consistent with "unreferenced
    LINT tags cost nothing, and referencing any one of them costs the full 352".
    That reading is uncomfortable — it makes one reference pay for four tags —
    and the measured standalone LINT tag slot is 4 bytes (`type_lint_50tag`,
    KNOWN), which does not obviously produce 88. Not patched. Recorded as the
    normalisation it is, with its own probe named below.

    **(1) The REAL-dest operator ladder is EXACT at 7, 9 and 10 operators.**
    `cptrdops_n07/n09/n10` all sit precisely on baseline, so `124 + 40n` holds
    and there is no ">= 5 step". That half of the question is closed.

    **(2) The 5-operator anomaly is NOT an operator-count effect, and it is not
    resolved either — it is now a CONTRADICTION between shapes.** The two
    all-REAL, unparenthesised 5-operator files built for this
    (`cptrdarrange_alternating_n05`, `cptrdarrange_grouped_n05`) both read −4 per
    rung against `operator_count_base[5] = 328`: they measure the ladder's 324.
    The three older families that pinned 328 still measure 328 and are still
    exact.

    | n=5 REAL-dest shape | measures |
    |---|---:|
    | all-REAL, no parentheses, `R0+R1*R2+R3*R4+R1` | **324** |
    | parenthesised, mixed DINT/REAL, `(R0+L1)*L2-L3/L4+L5` | 328 |
    | nested parentheses, `L5+(L4-(L3/(L2*(R0+R1))))` | 328 |
    | no parentheses, three float literals, `R0*1.5+R1*2.5-R2/3.5` | 328 |

    No single discriminator covers all four. Parenthesisation explains the middle
    two and fails on the last; integer operands explain the middle two and fail
    on the last; the leading-tier-1-run rule that CLOSED the integer path (see
    OQ-CPTARRANGE, now archived) predicts 324 for the run-of-1 rows and breaks
    eight of them.
    **Left at 328, unchanged**, because every candidate change fixes fewer rows
    than it breaks — applying the integer path's rule here with base 324 fixes 4
    and breaks 10. Counted, not guessed at.

    **(3) `**` on the REAL-dest path is per-operator, and the rate is not what is
    wired.** Normalised, `cptrdpow_k2` is **+12 per rung** and `cptrdpow_k3` is
    **+20** — a clean +8 per additional `**`, which answers the question the two
    files were built for: per operator, not per call. The wired `pow_extra: 8`
    plus `pow_with_tier2_extra: 4` charges a flat 12 for any count, so it is
    right at k=1 by construction and 8 short per extra `**`. NOT wired, and the
    reason is (2): `cptrd_powmulti_n05` is a 5-operator pow row, so the pow base
    and the 5-operator base are entangled and moving one moves the other. They
    have to be settled together.

    **(4) The narrow-operand rate is badly wrong, and SINT and INT do not
    match.** Normalised per rung — SINT k=0..4: 0, **−92**, **−44**, 0, **+44**;
    INT k=0..4: 0, **−80**, **−20**, **+36**, **+92**. Both monotone in k with a
    roughly constant step after k=1 (SINT ~+48 per operand, INT ~+56) and a large
    negative jump at k=1, so the one-point fit `3*40 + 136` is wrong in base and
    rate, and the assumption that the two narrow types behave identically is
    refuted. That belongs to OQ-CPTNARROW below and is cross-referenced rather
    than duplicated.

    **(5) A float literal with an INTEGER destination is unpriced, and it is
    large.** `cptidflit_k1/k2/k3` normalise to **+120, +124 and +188 per rung**:
    the integer CPT path charges nothing at all for a float literal where the
    REAL path charges 4. These three files exist precisely because no
    integer-destination CPT capture had ever contained one, and real logic writes
    `CPT(Dest,A*1.5+B)` routinely. **120+ bytes per rung is the largest single
    unpriced CPT term found in this project.**

    **NOT wired, and the reason is a CONFOUND IN THE FILES rather than a hard
    law.** The three shapes vary the operator count alongside the literal count:

        file            expression                 operators  float lits  per rung
        cptidflit_k1    L0*1.5+L1                       2          1         +120
        cptidflit_k2    L0*1.5+L1*2.5                   3          2         +124
        cptidflit_k3    L0*1.5+L1*2.5-L2/3.5            5          3         +188

    So "not linear in the literal count", written here earlier the same day, was
    the wrong diagnosis. Fitting `a x literals + b x operators + c` reproduces
    all three EXACTLY — a = −56, b = +60, c = +56 — and that is worthless:
    three parameters against three points is exactly determined, unfalsifiable,
    and it returns a NEGATIVE per-literal rate, which is not a thing. Same trap
    OQ-STEXPR-OPERATOR was stuck in, except there a regime split dissolved it and
    here there is nothing to dissolve.

    **What is needed, in priority order.** (a) FOUR integer-destination files at
    a FIXED operator count of three, varying only the float literals:
    `L0*1.5+L1*L2` (1), `L0*1.5+L1*2.5` (2), `L0*1.5*2.5+L1` (3) and
    `L0*1.5*2.5*3.5` (3 again, moved) — the last pair separating literal COUNT
    from literal POSITION. The 1..6 sweep at a fixed operator count written here
    before would have repeated the confound, because the existing files' operator
    skeleton is what changes between them. This is still the biggest number
    here. (b) Three files to settle the −352: the identical rung shape with the
    pool's LINT tags removed entirely, with exactly one LINT tag, and with four
    of which one is referenced. (c) An n=5 REAL-dest discriminator set — all-REAL
    parenthesised, all-REAL with one float literal, mixed-operand unparenthesised
    — which separates the three candidates for (2) in three files.


    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `cptrd_operand_bool`

27. **OQ-CPTNARROW** — how the SINT/INT → DINT widening scales. 2026-09-04.

    2026-09-04: INTs use a behind-the-scenes conversion to DINT. That is
    the mechanism, and it resolved two things at once:
    LINT operands cost **nothing** (already 64-bit, no widening), and
    SINT/INT operands cost **+256/rung** on the 3-operator all-REAL control.

    **What is NOT determined: how that 256 splits.** There is exactly one
    file in the corpus with narrow operands in a REAL-destination CPT
    (`cptrd_operand_sint`, 3 SINT operands). 256/3 is not an integer, which
    rules out a pure per-operand rate, but per-call, per-operand-plus-block
    and per-conversion-site all fit that single point identically. The
    model currently charges `3*40 + 136` — the ordinary per-int-operand
    conversion each operand pays, plus one widening block per call. That
    split has a physical story and no evidence.

    It matters for real files, which have arbitrary SINT/INT counts: if the
    truth is per-operand, a 10-narrow-operand expression is wrong by ~600
    bytes per call.

    `cptnarrow_{sint,int}_k0..4` varies ONLY the narrow count at a fixed
    3-operator shape (k=0 must reproduce the 244/rung control, which is the
    built-in check that the batch is comparable). INT is swept alongside
    SINT because the model assumes they behave identically and that has
    never been tested — this project already assumed LINT belonged in the
    same set and it turned out to cost nothing. `cptwide_lint_k1..4`
    confirms LINT is free at every count rather than just at the one count
    (3) the single existing file happens to use, and
    `cptwide_mixed_sint_lint` covers mixed integer WIDTHS, which nothing in
    the corpus does. Blocked on capture.



    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.


    **SOLVED 2026-09-18, and deliberately NOT wired. The law is
    `rate_T x k - 132`**, where k is the number of narrow operands in the
    expression and `rate_T` is per narrow type. Differenced against
    `cptnarrow_*_k0` (the same expression with every operand REAL), 100 rungs
    each, so the file base and the operator structure both cancel:

        k          1      2      3      4      rate   intercept
        INT      -80    -20    +36    +92        56       -132
        SINT     -92    -44     +0    +44        44       -132

    Eight of the ten points are EXACT on that form. Both types share the same
    -132 intercept, which is what makes it a law rather than two curve fits, and
    the two misses are a consistent **-4 at exactly k=1 in both types** -- not
    noise, and unexplained.

    **Why it is not wired: it cannot move the real set.** Across all sixteen real
    programs there are **27 CPT calls with any SINT/INT operand, and they are all
    in ONE file** (by narrow-operand count: 7 at k=1, 12 at k=2, 7 at k=3, 1 at
    k=7). At these rates that is on the order of 1,300 bytes on a single program.
    CLAUDE.md's rule applies as written -- a task that does not move real
    prediction error toward 1% waits -- so the derivation is recorded here and
    the wiring is not spent now.

    Two things to carry forward when it is wired. The k=7 real call is outside
    the measured range (k goes to 4 here), so the rate's linearity past 4 is an
    extrapolation. And the -4 at k=1 should be resolved first: a single
    `cptnarrow_{int,sint}_k1` variant with the narrow operand in a non-leading
    position would say whether it is positional.

28. **OQ-CPTTYPEMISMATCH** (the one thread OQ-CPTARRANGE left open; that
    question itself is CLOSED and wired — see `docs/RESOLVED_QUESTIONS.md`).

    A CPT whose destination and operands disagree in type costs more, and
    nothing in the model has a term for it.
    `cptdest_d{dint,real}o{dint,real}_n{00010,00100,01000}` is a clean 2x2 on
    one shape (`L0+L1*L2+L3`, three operators, four operands):

        destination   operands      residual per CPT
        DINT          4 x DINT                     0
        DINT          4 x REAL                   +48
        REAL          4 x DINT                    +4
        REAL          4 x REAL                     0

    Exactly linear across a 100x span in all four arms, and **both matched arms
    are byte-exact at every count** — an independent validation of the
    integer-tier and REAL-destination models at scale.

    **Not wired: one operand count cannot separate a per-call cost from a
    per-operand one.** +48 on four REAL operands is equally 48 per call or 12
    per operand; +4 on four DINT operands equally 4 per call or 1 per operand.

    Real exposure was measured before deciding: **3 of the 256 CPT calls in the
    sixteen real programs** are integer-destination with a REAL operand or float
    literal, roughly 144 bytes across the whole real set. No pressure to guess.

    **Discriminator: the same four arms at two operand counts (2 and 8),
    operator count held at three.** Four files settle both constants outright.

29. **OQ-STEXPR** — **the four assumptions and the AOI-call separation are
    CLOSED and WIRED 2026-09-18; see `docs/RESOLVED_QUESTIONS.md` for the
    derivation and `docs/MEMORY_MODEL.md`'s KNOWN register for the constants.**
    The ST family went 8.3291% -> 0.0091% mean absolute error, 60 of 69 rows
    byte-exact, 67 of 69 inside the universal ±8.

    **Three single-point threads survive, and they are the only ST rows outside
    that band:**

    - `st_jsr_param_target_n00100` is the only non-exact ST file (+228). Every
      JSR parameter constant was fitted on RLL targets and the corpus holds 63
      SBR / 42 RET inside ST, so an ST JSR target is a real shape that may be
      charged differently. One file with the same target at a second call count
      separates a per-call error from a per-file one.
    - `st_ctl_case` carries a −32 residual; the CASE decomposition into
      per-construct and per-selector is one data point short.
    - `while_block` was corrected 72 -> 76 on the strength of the literal-RHS
      rate. Only one WHILE file exists, so that split rests on a substitution.
      A WHILE-count sweep at fixed assignment content settles it outright.

    None of the three is worth a batch on its own; they are the natural
    passengers on the next ST batch, whatever drives it.

    **CAPTURE ERRORS: 1 row(s)** — `st_instr_concat_n01000` captured WITH Studio
    build errors, so its `actual_bytes` is SUSPECT rather than wrong: part of the
    file may never have reached the controller, which reads as the model
    over-predicting (it sits at −52,000). No error text was recorded — it was
    captured before the error-log reader worked — so it needs RECAPTURE before
    its number is used, and it is excluded from every ST figure quoted above,
    including the 0.0091%.

30. **OQ-REAL5069** — *amended 2026-09-14 by the strip ladder: the
    "identical content, identical residual" result holds and is not in doubt,
    but it was measured on GENERATED files. On real exports the two platforms'
    bare shells differ by 3,736 where the engine has them 8 apart. Read this
    entry as "no per-platform CONTENT model is needed", not "the platform
    difference is fully wired". The residue is unpriced controller-shell
    content — see OQ-CTLSHELL.*
    **SHELVED 2026-09-11 until 2026-09-18. Not closed,
    and not to be raised again before then.**

    Two corrections belong on the record first.

    **The premise below is out of date.** Four of the sixteen real captured
    programs ARE 5069 (elmsdale and salamanca and superior on 5069-L330ERM,
    flarefunction on 5069-L320ERMS3). The platform is no longer unvalidated.

    **The platform breakdown that replaced it was worse than the stale
    premise, and it was mine.** Grouping the sixteen real files by processor
    family gave 5069-L330ERM a -4.00% median and called it the corpus's
    worst platform — with **salamanca at +1.08%, one of the four most
    accurate files in the whole set, counted inside that bucket.** Family
    sizes are n=1, n=2 and n=3. Those medians are not measurements.

    The disproof is already in the same table: **murraybros is -5.16% on a
    1756-L81E**, worse than every 5069 file, on the family with the best
    median. Whatever drives the large residuals is not the processor, and
    reading one into a catalog string is exactly the failure this file
    already documents once — the rejected per-platform baseline that fitted
    190 near-empty files beautifully and broke 612 real ones.

    `gen_platform_equivalence.py` and its 15 files are KEPT, uncaptured, for
    when this is picked back up. They are still the right experiment if the
    question turns out to be real; nothing about them assumes it is.

    Priority: low, by the project owner's call. The residual is real and
    lives somewhere else.

    **CAPTURED AND ANSWERED 2026-09-14 (segment 17). 10 of the 15 landed, and
    they say the platform costs nothing beyond the baseline constant already
    wired. CLOSED.**

    The design was: identical content at five densities on each of three
    processors, so flat-across-densities means a real constant, growing means a
    rate, and zero means the platform is not the cause. Each density unit is one
    `PlatEqUdt` tag (8 DINTs), one DINT tag and one rung, byte-identical across
    platforms.

        density   5069-L306ER    1756-L81E
              0             0            0
             25          -332         -332
            100        -1,232       -1,232
            400        -4,832       -4,832
          1,600       -19,232      -19,232

    **The two processors' residuals are identical to the byte at every density**,
    and both empty-project rows are exact (18,160 and 18,128 predicted and
    actual). So the entire platform difference is the 32-byte baseline constant,
    which is already wired exactly. There is no per-platform rate, and the
    rejected per-platform baseline that broke 612 files stays rejected for a
    second, independent reason: even if it had fitted, there is nothing for it
    to fit.

    That settles the question this entry was shelved on. It does NOT make 5069
    a validated platform end-to-end — see the residual below, which is shared
    and is not 5069's.

    **A real finding that is NOT the platform's, and must not be fitted here.**
    Both arms over-predict by exactly `12n + 32`, exact at all four densities on
    both processors. Each unit contains a UDT tag, a DINT tag and a rung, and
    **all three scale together in this family**, which is the collinearity trap
    this project has now hit seven times. Two of the three are independently
    exact elsewhere -- `dscale2_udt_u001_t{001..500}` is flat in tag count over
    a 500x span, so a UDT tag is not it, and `instr_*` sits in the universal +-8
    band to 5,000 instructions -- but the rung here is
    `XIC(PeBit0)MOV(0,PeDint0000)OTE(PeBit1);`, a three-instruction rung with a
    LITERAL MOV source, which no isolating family covers. So the 12 is not
    attributed. **The discriminator is three files at one fixed unit count, each
    carrying only one of the three components.**

    **`platform_plateql330_*` (5 rows) never captured**, so the equivalence
    result rests on two processors rather than three. A second 5069 model would
    confirm it; it is not needed to reach the conclusion, since the two arms
    already agree to the byte.

    ---

    *Original entry, retained for history:*

    **the 5069 platform has ZERO real-file validation.**
    Found 2026-09-05, while checking which platforms the real corpus
    actually covers.

    Every one of the nine real production exports in `samples/local/` is a
    **1756-L8x**:

    | file | processor | fw |
    |---|---|---|
    | k3m16_edgers | 1756-L82E | 32.04 |
    | murraybros | 1756-L81E | 35.05 |
    | emporium | 1756-L83E | 32.04 |
    | pukall_gang | 1756-L81E | 35.05 |
    | ipc_edgerline | 1756-L81E | 35.05 |
    | cmu | 1756-L82E | 35.05 |
    | emporiumedger | 1756-L81E | 35.05 |
    | mrfp_edger | 1756-L81E | 35.05 |
    | accutally | 1756-L83E | 35.05 |

    Everything the model knows about 5069 -- the safety-capable baseline
    delta (+304), the 5069 catalog entries in `module_overhead_by_catalog`,
    the 5069 processor baselines -- comes from files this project generated
    itself. Not one of them has ever been checked against a real 5069
    program.

    That is the same extrapolation risk as OQ-DEFSCALE, and it went
    unnoticed for the same reason: corpus-level pass rates looked healthy
    because the corpus is full of synthetic 5069 files that the model was
    fitted on. Per CLAUDE.md's accuracy rule (real programs only, generated
    files are an instrument not evidence), the honest statement is that
    **this tool is validated on 1756-L8x and unvalidated on 5069.**

    It matters more than the raw file count suggests: 1756-L7x and 1769 are
    now formally dead architecture (2026-09-05), which leaves
    5069/CompactLogix 5380 as the platform this tool most likely gets used
    on going forward -- and it is the one with no real evidence behind it.

    **What is needed:** one real 5069 export with a controller capture.
    An "Elmsdale" project is known to run on 5069, but that file is not in
    `samples/local/`. Any real 5069 program would do -- the point is a
    first real data point, not that specific one.

    Until then, the UI should arguably say so on a 5069 file the way it
    already warns on a Safety project. Not implemented yet -- flagged here
    rather than built, because a warning banner claiming more precision
    about its own uncertainty than the data supports would be its own kind
    of dishonesty.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.

31. **OQ-AOISTRUCT** — **what an AOI costs to DECLARE, as a function of its
    structure rather than its name.** New, 2026-09-06, under two
    constraints set the same day: the AOIs in the worst-predicting real
    file also appear in other real projects, so they are not that file's
    problem; and the tool is going to people outside the organisation whose
    code will be different and whose AOI libraries will be entirely
    unfamiliar.

    Those two together rule out the tempting move. MurrayBros' residual
    correlates hardest with AOI structure (aoiaxisparam +0.889, aoirungs
    +0.848, aoidefs +0.838, aoilocals +0.835), and the shared definitions
    that recur across the nine projects (`PTimer`, `HomeToTorque`,
    `SpecialInputs`, `T_ADD`, `T_DST`, `AnalogSensor`, `Debounce`,
    `ts_PilotLight`, `VirtualAxis`, `ts_AxisGap`, `TierPinchAOI`,
    `ts_TotalSB` are byte-identical across projects) would make a
    per-AOI-name correction table easy to fit and worth exactly nothing to
    a stranger importing an L5X full of AOIs this project has never seen.

    **What the model prices today**, read straight out of
    `compute_aoi_definition_cost` + `AoiDefinitionModel.bytes_for`: base
    1184, plus a per-type rate (BOOL 16 / SINT 18 / INT 18 / LINT 24,
    single-type definitions only) or a flat 20 per declared item, plus AOI
    TYPE-name length buckets. That is the entire function.

    **Seven structural properties are therefore priced at exactly ZERO**,
    each of them an untested assumption rather than a measurement, and
    each measured against the real corpus (81 AOI definitions / 2,120
    Parameters+LocalTags in `samples/local`):

    | # | unpriced property | real corpus evidence |
    |---|---|---|
    | 1 | member NAME length | mean 12.1 chars, max 32; tag names elsewhere in this model cost 8 bytes per 8-char chunk |
    | 2 | member DESCRIPTIONS | 803 of 2,120 carry one; **zero** generated files ever emitted one |
    | 3 | InOut parameters | skipped outright by `compute_aoi_definition_cost`; 94 real ones, and the only legal way to pass an array/STRING/MESSAGE/UDT into an AOI |
    | 4 | predefined-structure members | TIMER 557 real member uses, DateTime 120, COUNTER 66, STRING 58, MOTION_INSTRUCTION 36, MESSAGE 15 — **none ever generated**; all fall off the per-type table onto the flat atomic rate |
    | 5 | array dimensions | a member counts once whether scalar or `Dimensions="1024"`; 46 real dimensioned AOI members |
    | 6 | member counts past the fitted range | real AOIs run to 102 params / 128 locals / 85 internal rungs (median 12/11/11); the generated corpus topped out near 6/2/1 |
    | 7 | extra internal routines | 7 of 81 real definitions carry an EnableInFalse and/or Prescan routine besides Logic |

    #6 is the identical extrapolation shape as OQ-SHELLSCALE (a constant
    fitted at n=2, applied at n=200, wrong by 8 bytes/unit and invisible
    until the ladder was built) and OQ-DEFSCALE. Both of those were real.

    **`gen_aoi_structure.py`, 56 files**, one property per group, everything
    else held fixed — including the AOI type name, which IS priced and
    would otherwise contaminate every reading:

    | group | files | varies |
    |---|---:|---|
    | `aoistr_namelen_c{04,08,12,16,20,28,40}` | 7 | member name length, 20 DINT params |
    | `aoistr_desc_l{000,016,064,256}`, `_all_l{000,064}`, `_aoidesc_l256`, `_aoirevnote_l256` | 8 | member and AOI-level description text |
    | `aoistr_inout_n{00,04,16,48}` | 4 | InOut param count |
    | `aoistr_predef_{base,timer,counter,motion,string,msg_inout}_n{01,08}` | 11 | predefined-structure member type |
    | `aoistr_dim_{base,local_atomic,local_timer,inout}_d{8,64,512}` | 9 | array dimension |
    | `aoistr_scale_{param,local,rung}_n*` | 12 | member/rung count to the real p90 and past it |
    | `aoistr_routines_n{1,2,3}` | 3 | internal routine count, total rungs held at 24 |
    | `aoistr_real_{median,p90}` | 2 | composite: do the isolated parts add? |

    **The design property that makes this readable**: the model predicts a
    DEAD FLAT line across every group except the three scale sweeps —
    19,712 for all seven name-length files, 19,472 for all nine
    inout/predefined files, 19,392 for all nine dimension files, 20,352 for
    all three routine-count files. Any spread at all in the captured
    numbers is an unpriced item, with no fitting or disentangling required
    to see it.

    Platform is 1756-L81E fw35.05 for all 56 — the same processor and
    firmware as MurrayBros and MRFP_Edger, so nothing here is confounded by
    OQ-BASELINE-PROCFW.

    Only the two composites are instantiated; the other 54 are
    definition-only, so what is captured is the declaration cost itself
    with no tag_overhead or member storage mixed in.

    Three generator gaps had to be closed to build this and are worth
    recording, because each one was a silent hole rather than a deliberate
    omission:
    - `builders.py` could not emit a predefined-structure AOI member at
      all. The atomic path writes a bare `Radix` + scalar `DataValue`
      (wrong for TIMER); the nested-UDT path writes an L5K value list that
      does not match the real positional encoding (a real TIMER LocalTag's
      L5K default is `[0,1500,0]` — three fields for five members, because
      EN/TT/DN alias into the leading status word). `predefined_members.py`
      now supplies the exact block captured from the real corpus rather
      than a guessed encoding that would only have failed in Studio 5000,
      costing a capture run to discover.
    - `builders.py` could not emit a member `<Description>`, an AOI-level
      `<Description>`/`<RevisionNote>`, or an `EnableInFalse`/`Prescan`
      routine. All three now render in the real shape and order
      (Description then RevisionNote before `<Parameters>`; routines
      alphabetical as EnableInFalse/Logic/Prescan, with the matching
      `ExecuteEnableInFalse`/`ExecutePrescan` attribute flipped to "true").
    - `lint.py`'s missing-array-subscript rule fired on an array InOut
      Parameter passed bare to an AOI call — which is the correct real
      form (LOG_HMIDisplay `Dimensions="25"`, BitArray
      `Dimensions="1024"`). Exempted at the AOI call site. This project had
      never before wired an array InOut param to an actual caller, so the
      rule had never been exercised against it.

    **Blocked on capture.**


32. **OQ-MODULEMARGINAL** — the last ASSUMED exposure that reaches a real
    file. 4.15% of real-file bytes on the current engine, of which the 2198
    `-ERS3` drives are 4.07% and eleven other catalogs are the rest. The
    worst-exposed real files are `k3m16` (7.06% ASSUMED), `horizon` (7.00%)
    and `ipc` (6.44%), and every ASSUMED byte in all sixteen real files is a
    `module_io` entry — nothing else in the model is both ASSUMED and
    reachable from a real export.

    **CAPTURED AND RECONCILED 2026-09-11, 54 files (`asmclose_*`, n=1/2/4
    per catalog). The marginal law is exact, and it must not be wired on
    its own.**

    Over-prediction is exactly linear in the module count, with zero
    residual at n=1, n=2 and n=4 for every catalog:

        over-prediction(n) = discount x (n - 1)

        1794-AENT                 432      1756-EN4TR             1520
        1734-AENT/B               520      1756-IB16IF/A          2208
        1734-AENT/C               520      440C-CR30-22BBB/A      3768
        1756-IB16                 792      AL1222                    0
        1756-IB32/B               792      842E-CM-M              1000
        PowerFlex 755-EENET-CM-S  976

    So the model charges every module full price and the controller charges
    the first one full price and `full - discount` for the rest.

    **The AL1222 "control" is void — corrected 2026-09-13.** This entry
    previously read AL1222's discount of exactly 0 as the control proving a
    real per-catalog-shape property rather than a flat per-module fudge.
    `asmclose_al1222_1conn_n{01,02,04,08}` all read **18,128 — the bare
    baseline — at every one of the four counts**, with distinct module names
    and zero import errors. A module cannot cost the same at n=8 as at n=1,
    so the AL1222 modules never reached the controller at all. A catalog that
    contributes nothing has a zero discount trivially and is a control for
    nothing. (The table's `'AL1222': bytes: -793` is an artifact of the same
    non-arrival: it happens to cancel the 850 declared bytes, which is why
    the n=1 row still lands within 57.) The per-catalog reading is now
    settled on real evidence instead — see the mixture arm below.

    The 2198 `-ERS3` family does not fit that form — it carries an extra
    flat error at n=1 as well:

        D012 / D020 / D032 / D057   +6,384 at n=1, then +7,368 per extra
        S086-ERS3                   +3,264 at n=1, then +4,248 per extra
        S130-ERS3                   +3,228 at n=1, then +4,212 per extra

    i.e. a drive after the first costs 984 less than the first, AND the
    first is itself over-charged. This is the single largest ASSUMED block
    in the project.

    **WIRED 2026-09-13 for ten of the seventeen catalogs. The blanket "makes
    every real file worse" reading was true and the conclusion drawn from it
    was wrong.** Applying all seventeen rates removes 189,570 bytes across
    216 repeated modules in the sixteen real programs and does make all of
    them worse. Attributing that catalog by catalog, which had not been done,
    puts **95% of it in two families**: ETHERNET-MODULE (67,450 bytes) and the
    six 2198-*-ERS3 drives (112,176). With those two held out, the other ten
    catalogs move the real programs by 10,464 bytes across 47.4 MB:

        variant                                   mean |%|   sum-weighted
        discount off                                1.6009       +1.2370%
        all 17 catalogs                             1.7492       +1.6298%
        without ETHERNET-MODULE and 2198-*-ERS3     1.6289       +1.2579%

    So the ten ordinary I/O and adapter catalogs are neutral on real files to
    within noise, while taking the `asmclose_*` rows from 16 byte-exact to 47.
    Both exclusions are on shape grounds and were decided from the shapes, not
    from which way they moved the number:

      - **ETHERNET-MODULE is not a catalog.** It is a generic placeholder
        whose cost is driven by connection sizes typed in by hand — 109
        instances across the sixteen real programs carry 40 distinct
        connection shapes, which is why `module_connection_data` exists. The
        `genem_n{01,02,04,08}` sweep cloned ONE shape, so its 710-byte repeat
        rate is the cost of a second identical clone and says nothing about a
        second differently-configured device.
      - **2198-*-ERS3 was measured on bare drives with no axis tag,** which no
        real program contains. Arm C exists to fix exactly that and every one
        of its six rows captured WITH Studio build errors, so the with-axis
        rate is still unmeasured.

    The compensating-error problem stated in OQ-REALGAP survives this and is
    now better quantified: with the ten clean catalogs wired, the real-file
    under-prediction is +1.2579% sum-weighted, and the honest figure once the
    two suspect families are also resolved is nearer +1.63%. That is the size
    of the gap OQ-REALUNDER has to close, and it is larger than the headline
    suggested.

    **PER-CATALOG, NOT PER-FILE — SETTLED 2026-09-13 by Arm B.** Every one of
    the 54 single-catalog captures fits both readings identically:

      - PER-CATALOG — the first module *of each catalog* pays full price:
        error = sum over catalogs of `d_i x (n_i - 1)`
      - PER-FILE — the first module *in the file* pays full price and
        everything after it is discounted whatever its catalog:
        error = `sum(d_i x n_i) - d_first`

    On a single-catalog file these are the same number; on a real program
    carrying 20-60 modules across 10-20 catalogs they differ by most of the
    module total. The mixtures separate them three independent ways and all
    three say PER-CATALOG:

        quadruple   sum(d)   over-prediction at x2   x2rev     at x1
        mixq1        2,744            2,834          2,834        33
        mixq2        7,472            7,424          7,424       -32
        mixq3        7,080            7,048          7,048        24

      1. `x2rev` is **byte-identical** to `x2` in all three quadruples. Under
         PER-FILE the total has to move by `d_first - d_last` (1,224 / 3,704 /
         3,312 here). It does not move at all.
      2. The `x1` residual is ~0 against a PER-FILE prediction of
         `sum(d) - d_first`, i.e. 1,224 to 6,944 bytes.
      3. The `x2` over-prediction equals `sum(d)` to within 90 bytes on a
         five-module file whose own baseline residual is already ~30.

    This is what the engine already implemented, so no code changed — but it
    was an assumption until now and is now measured.

    **Test files built 2026-09-11, `gen_module_marginal.py`, 36 files.**

      - **Arm A, 17 files** (`asmclose_*_n08`) — n=8 for every catalog that
        already has n=1/2/4, from the same builders so it differences
        straight against n=4. This is the first point that can FALSIFY the
        law: three points fit it exactly but two of them define it, so a
        per-rack or per-connection-block step above four modules would be
        invisible in the existing data.
      - **Arm B, 9 files** (`modmarg_mix{q1,q2,q3}_{x1,x2,x2rev}`) — the
        decisive experiment. Three quadruples of catalogs with widely
        separated discounts, each at 1 and 2 copies per catalog. The two
        readings are separated by 2,744 / 6,952 / 6,288 bytes on the `x1`
        and `x2` files, on files that are otherwise exact to the byte, so
        one capture each settles it. The `x2rev` files reverse module order
        within the file: PER-FILE requires the total error to move by
        `d_first - d_last` (1,224 / 3,704 / 3,312 here), PER-CATALOG
        requires it not to move at all — so the mixture is self-checking
        rather than one arithmetic coincidence.
      - **Arm C, 6 files** (`modmarg_drvaxis_*`) — the -ERS3 drives WITH
        their axis (one `AXIS_CIP_DRIVE` per drive plus the one shared
        `MOTION_GROUP`), at n=1/2/4/8 for D012 and n=1/2 for S086. All 54
        `asmclose_*` files hold bare drive modules with no axis tag; a real
        program never does. Differencing against the bare-drive capture at
        the same count separates the drive's own marginal cost from the
        axis's, which is the form the cost actually takes on a real file.
      - **Arm D, 4 files** (`modmarg_ob32chain_n{01,02,04,08}`) — see the
        contamination note below.

    **Contaminated data found and cleared, 2026-09-11.**
    `asmclose_1756_ob32_rackaliased_n02` and `_n04` are not usable and their
    capture columns have been cleared. The 1756-OB32 block is the only
    2-deep chain in the set (a 1756-EN2T adapter plus the output card behind
    it), and the copier that multiplies a module block renames only the
    FIRST `<Module>` in it. Every copy after the first therefore shipped an
    identically-named OB32 still pointing at `ParentModule="<the first
    adapter>"` and still sitting in the same slot 3. Studio merged the
    identical duplicates instead of rejecting them, so both files captured
    at ZERO import errors while measuring N adapters sharing ONE output
    card. The "1756-OB32 discount = 1760" read off them is therefore not a
    discount at all — it is the cost of the cards that never got imported.
    `lint.duplicate_module_name` now catches this class outright; a
    corpus-wide sweep found these two files and no others. Arm D rebuilds
    the full n=1/2/4/8 sweep under a new sample_id, with every module in
    every copy renamed and its `ParentModule` repointed at its own adapter,
    rather than regenerating in place — regenerating in place would leave
    the old captured `actual_bytes` attached to different file content.

    One catalog is still deliberately not covered and is reported rather
    than faked: **150 SMC Flex-E** (0.069% exposure) has no real module XML
    in either sweep table, so there is nothing verbatim to build from. It
    needs a real export before it can be tested at all.

    **Arms A, B and D captured and reconciled 2026-09-13. Arm C is the only
    one still outstanding, and it is outstanding because all six of its rows
    captured with build errors.**

      - **Arm A (n=8) does not falsify `d x (n - 1)`.** 64 of the 71
        `asmclose_*` rows land byte-exact with the discount applied against 16
        without it, and the marginal is flat at every one of n=1/2/4/8 on 13
        catalog families. A per-rack or per-connection-block step above four
        modules would have shown here and does not.
      - **Arm B settled per-catalog vs per-file** — see above.
      - **Arm D (`modmarg_ob32chain_n{01,02,04,08}`) reads 21,760 / 24,080 /
        28,720 / 38,000**, a flat marginal of **2,320 per additional
        EN2T-plus-OB32 chain** against a modelled 3,544 — so a 1,224 discount
        per chain, exact at three counts. It does **not** split between the two
        catalogs: one equation, two unknowns. The n=1 point gives the pair at
        88 bytes over what the table charges, which is the second equation, but
        both equations are the pair rather than either catalog. **The missing
        file is an EN2T-only count sweep** (n=1/2/4/8, every copy under
        `Local`, no downstream child): differenced against Arm D it gives
        1756-EN2T's own rate and leaves rack-aliased 1756-OB32 by subtraction.

    **PER-RACK VS PER-PROJECT: implemented, measured, and irrelevant on real
    files.** This was recorded as the open scope question and as the reason the
    discount could not be wired. `ModuleOverheadModel.repeat_scope`
    (`project | parent`) now implements both, and they produce **byte-identical
    totals on all sixteen real programs**. The reason is structural rather than
    lucky: in every one of the sixteen, no catalog carrying a measured repeat
    rate ever appears under more than one parent module. Exactly one real export
    in `samples/local/` splits one at all (`BAI10048_TrimmerTally`, a 1756-IB32/B
    across two parents), and it is not in the held-out sixteen. So the question
    stays genuinely open — nothing in the corpus discriminates, because every
    copy in every captured sweep sits under `Local` — but it cannot be what made
    the real files worse, and it cannot change a real-file number until a real
    file contains a split catalog. Default is `project`.

    **A 16-byte disagreement on 1756-IB16, unresolved and small.** The
    additivity M axis (a file holding nothing but 1756-IB16 modules) gives
    1,704 first / 904 after; `asmclose_1756_ib16_1conn_n*` gives 1,684 / 892,
    which is what is wired. Both are byte-exact on their own zero points, so
    the two file shapes differ by 8 somewhere outside the module term. Flagged
    rather than chased: it is 16 bytes on a 1,712-byte constant.

    **ROOT CAUSE OF 33 ERRORED ROWS FOUND AND FIXED 2026-09-14.** A 2198 drive
    needs its 2198-P bus supply module AND that supply's converter axis -- an
    AXIS_CIP_DRIVE whose `AxisConfiguration` is `"Non-Regenerative AC/DC
    Converter"`, pointed at the supply's `Ch1`. Without them Studio converts the
    file and then fails Build, once PER DRIVE MODULE:

        Primary Bus Sharing Group 1 contains a module configured as Shared DC or
        Shared DC/DC with no module configured as Shared AC/DC or Shared DC -
        Non-CIP Converter.

    Only one of the 33 rows carried that text. The error COUNTS identified the
    rest: `axmarg_1cat_n{02,04,08,12,20}` record exactly 2/4/8/12/20 errors, and
    `axis_scale_n{02..20}_dual` -- the same axis counts on half as many modules --
    record n/2 + 1. Per drive module, not per axis.

    The representation is the one the `kinetix_drive_without_bus_supply` lint rule
    said it could not check: that rule tests only for a supply MODULE, noting the
    power group "is not an attribute of `<Module>` -- it appears nowhere in the
    real corpus either". It is on the AXIS_CIP_DRIVE TAG.
    `BaillieLeitchField_Edger` carries 25 `"Position Loop"` axes and 2 converters
    (`MotionModule="BUS_601A:Ch1"`, `"BUS_601B:Ch1"`); `SJ_Gormley` 27 and 2.

    **This also explains the -ERS3 family's otherwise unexplained EXTRA flat
    over-charge at n=1** (recorded above as +6,384 for the D-series before the
    per-extra-drive term). Those files had no bus supply either, so part of every
    one of them never reached the controller. That is why segment 14 excluded the
    2198 repeat rate as measured-on-a-broken-shape, and it means the six
    `'2198-*-ERS3': { bytes: 4113, confidence: KNOWN }` first-instance entries
    rest on the same broken captures and are **suspect, not KNOWN**.

    Fixed in `gen_module_motion.bus_supply_with_converter()`, which returns both
    halves together because needing one without the other is always a bug, and
    applied in `gen_assumed_closeout` (the n=1/2/4 2198 sweep), `gen_module_marginal`
    (Arm A n=8 and Arm C drive+axis), and `gen_axis_marginal`. A second real defect
    was corrected alongside it: `gen_module_axis_scale` put a dual drive's second
    axis on **Ch2**, and across the three real Kinetix exports there are 33 `Ch1`
    references, 25 `Ch3` and **no `Ch2` at all**.

    Two new lint rules make both unshippable: `kinetix_axis_without_converter` and
    `drive_axis_unreal_channel`. They caught 36 and 9 committed files respectively
    before the fix; the converter rule is down to 6 and the channel rule to 0.

    **48 rows had their capture columns cleared** -- 26 `asmclose_2198_*`, 9
    `axmarg_*`, 9 `axis_scale_*_dual*`, 6 `modmarg_drvaxis_*` (the last of which
    was Arm C, whose whole purpose was to measure the drives WITH their axes and
    which had failed for this exact reason). All need recapture. Nothing wired
    regresses: the 2198 repeat rate was already excluded in segment 14.

    **CAPTURE ERRORS: 6 row(s)** flagged here by `scripts/capture_errors.py`
    (step 2b), 2026-09-17 -- `modmarg_drvaxis_2198_d012_ers3_n{01,02,04,08}` and
    `modmarg_drvaxis_2198_s086_ers3_n{01,02}`. Was 0.

    **AND THEY FINALLY CARRY ERROR TEXT, WHICH DIAGNOSES A DEFECT IN EVERY
    GENERATED KINETIX FILE.** Studio says, once per drive:

        Drv1: Primary Bus Sharing Group 1 contains a module configured as
        Shared DC or Shared DC/DC with no module configured as Shared AC/DC
        or Shared DC - Non-CIP Converter.

    So the drive declares itself a **Shared DC** bus member and nothing in its
    group declares itself the **Shared AC/DC** converter. Adding the `2198-P208`
    module and its converter axis -- done on 2026-09-13 -- was necessary and is
    not sufficient: the P208 has to be configured as the converter *for that
    group*, and it is not.

    **Why, and it is a structural flaw in how payloads are stored.** Bus sharing
    lives inside the module's `ConfigData` L5K blob, not in any attribute the
    generator sets. `sample_gen/data/kinetix.py` keys payloads by CATALOG, but
    bus sharing is a per-PROJECT, per-BUS property, so a payload lifted from a
    shared-bus drive in one real export carries that export's bus role and group
    number into a generated file whose supply came from somewhere else. A table
    keyed on catalog alone cannot produce a coherent bus.

    **Located but NOT decoded, and it must not be guessed.** Across all real
    2198 drives the only indices that vary in a bus-shaped way are **50, 52, 58,
    62** in the 114-value (Major 9/11) layout and **51, 53, 59, 63** in the
    119-value (Major 13/14) layout -- one pair per channel, since 50 always
    equals 58 and 52 always equals 62. Griffin's drives read `(0,0)`, `(2,0)` or
    `(2,4)` there, which says plainly that **some real drives are standalone and
    some are shared** on the same project. That is consistent with 0 = standalone
    and 2 = Shared DC, but the enum is inferred, not measured, and no constant
    may be set from it.

    **The fix that needs no decoding, and the donor already exists.** Griffin
    carries three genuinely standalone drives -- `EM112_StickReclaimDeck`
    (2198-D012-ERS3), `EM114_StickUnscrambler` (D012) and `EM101_PkgDeck1`
    (D057) -- all reading `0` at every one of those four indices. A standalone
    drive requires no converter, so the error cannot arise, and the generated
    files would stop needing a P208 at all. Whether a standalone drive costs the
    same bytes as a shared one is then a question the corpus can answer, rather
    than a confound the corpus is silently carrying.

    Not done here because it changes the shape of every generated Kinetix file
    and that is a decision, not a cleanup. Suspect, not wrong:
    `actual_bytes` is filled in but part of the file may never have reached the
    controller, which reads as the model over-predicting.

    **MEASURED CLEANLY 2026-09-13 (capture-batch segment 5), and still gated
    off.** The additivity grid's M axis is a file containing nothing but
    1756-IB16 modules on the local chassis — no tags, no UDTs, no AOIs, one NOP
    rung — at 0, 4 and 16 modules, with the all-zero corner exact (18,392
    predicted, 18,392 actual). The over-charge is `808n − 800`, exact at both
    counts, which decomposes without ambiguity:

        first module    1,712 charged, 1,704 real   (8 out, inside the band)
        every one after 1,712 charged,   904 real   (808 out)

    So the repeat discount is real, it is 808 for this catalog, and the FIRST
    instance carries no discount at all. The existing
    `module_overhead_repeat_discount` table holds 1,684 / 892 for 1756-IB16 — a
    792 discount, 16 short of this — derived from the module sweeps rather than
    from a file with nothing else in it.

    `apply_repeat_discount` is **true** since 2026-09-13, for the ten catalogs
    whose rate was measured on a shape real programs contain. The reason it was
    false — that the sixteen real programs under-predict and a discount predicts
    less — held for the table as a whole and not for those ten: they are worth
    10,464 bytes across 47.4 MB. The per-rack-versus-per-project question this
    paragraph raised is implemented and measured above; it changes nothing on
    any of the sixteen.

33. **OQ-ALARMDEF** — *scope note added 2026-09-14: this entry covers the ALMD
    / ALMA INSTRUCTIONS only. Tag-based `<AlarmCondition>` elements are a
    separate feature, are present in real programs at 19–21% of total memory,
    and are NOT parked — see OQ-ALARMCONDREAL.*
    **PARKED 2026-09-14, not closed. Zero ALMD / ALMA /
    ALARM_DIGITAL / ALARM_ANALOG occurrences across all sixteen real programs**,
    verified by direct grep. Nothing in this entry can move real prediction
    error, so it waits behind everything that can, and no further alarm test
    files are to be generated. The `almd_*`, `alarmbits_*`, `alarmdef_*` and
    `alarmsep_*` families are parked with it. Revisit when real-file error is
    under 1% or a real program starts using the instruction.

    Datatype-level alarm definitions. **RESOLVED except one
    term, 2026-09-12, by reading the 68 `alarmdef_*` and 33 `alarmsep_*` rows
    TOGETHER for the first time. They collapse to a single law, and that law
    disproves what this entry previously recorded.**

        deficit = SUM over UDTs of (8 + 8 x floor(BIT_members / 2))

    Zero residual on 64 of the 68 `alarmdef_*` rows and on all 33
    `alarmsep_*`. `alarmdef_l81_d1_*` sits at -72 because its UDT has 16 BIT
    members and 8 + 8x8 = 72 exactly; d02/d04/d08 sit at -16/-32/-64 because
    each of their 2/4/8 UDTs has one BIT member at 8 apiece. Four processor and
    firmware variants (l81, l81 v35, l81 v38, l902ts) give identical numbers, so
    it is platform-invariant across the active set.

    **DISPROVED: "8 bytes per DatatypeAlarmDefinition".** That came off the d0N
    ladder, in which definition count and UDT count are both N -- perfectly
    collinear. `alarmsep_u04_b04_def{1,2,3}` breaks it: four UDTs held fixed
    while definitions run 1, 2, 3, 4, and all four files are BYTE-IDENTICAL. The
    8 belongs to the UDT, not the alarm definition. **Alarm definitions cost
    exactly ZERO**, now confirmed 19 ways -- 15 matched `_alarm`/`_noalarm`
    pairs plus the def1/2/3/4 quadruple. Had the 8/definition been wired it
    would have been a wrong constant on every real file, which all carry
    hundreds of conditions.

    **Also re-confirmed, and both already recorded:** operator message text is
    free (`msg_none/s/m/l` byte-identical), and member-alarm count is free
    (`d1_m00` through `d1_m16` byte-identical).

    **The +72 "does not fit, and is the reason nothing is wired" note in the
    previous version of this entry is closed.** The extra 64 bytes were never an
    alarm term: the `d1_*` UDT carries 16 BIT members against 2 in the d0N
    files, and the law above accounts for the difference to the byte.

    **THE "2 BYTES PER TAG" THREAD IS CLOSED 2026-09-14 (segment 21). It was
    never per-tag, and the per-tag bytes are now modelled anyway.**

    `alarmbits_b{08,16,32,64}_t{01,04,16}` sweeps BIT-member count against tag
    count. The residual is **flat in tag count on every one of the 12 rows** --
    -24 / -56 / -112 / -232 at 8 / 16 / 32 / 64 BIT members, identical at t01,
    t04 and t16. A per-tag term cannot do that.

    Re-run live against the current engine, the `alarmdef_*_t{01,04,16}` ladders
    that produced the -2 / -8 / -32 below now read **-56 flat**, identical to
    `alarmbits_b16_*`. So the per-tag 2 bytes was real and is now supplied by the
    standalone-UDT-tag 8-byte slot alignment wired earlier on 2026-09-14. Both
    families agree, and the hypothesis below is superseded rather than merely
    unconfirmed.

    **What is left is a per-DEFINITION term scaling with BIT-member count**, and
    it is not fitted. Backing 24 / 56 / 112 / 232 out of the engine's
    `8 + 8*floor(BIT/2)` charge leaves a required 16 / 16 / 24 / 32: flat to 16
    bits, then +8 per doubling. Four points, all powers of two, and no mechanism
    predicting a step there rather than at a 32-bit word boundary.
    **Discriminator: BIT counts BETWEEN the powers of two -- 12, 20, 24, 40, 48
    -- which is where a bucket law shows its step shape.**

    *Superseded hypothesis, retained because the numbers are still the record:*
    Exactly four of the 68 rows carry a
    residual beyond the law, and they are the tag ladders:

        inst_t01   -2      noinst_t01   -2
        inst_t04   -8      noinst_t04   -8
        inst_t16  -32      noinst_t16  -32

    2 bytes per tag, identical WITH and WITHOUT an alarm definition -- so a tag
    term, not an alarm term. Those files' UDT has 16 BIT members, and 16 bits is
    exactly 2 bytes, so the hypothesis with a mechanism behind it is that a
    BIT-member UDT tag's own backing storage goes uncharged at
    `ceil(BIT_members / 8)` bytes per tag.

    **Test files built 2026-09-12, `gen_alarm_bitbacking.py`, 12 files.**
    `alarmbits_b{08,16,32,64}_t{01,04,16}` crosses BIT-member count with tag
    count. Under `ceil(bits/8)` per tag the deficit beyond the law runs 1/4/16,
    2/8/32, 4/16/64, 8/32/128 across the grid; under a flat 2 per tag every row
    reads 2/8/32 regardless of member count -- 128 against 32 at b64/t16, on
    files whose other terms cancel exactly. Every existing file in the tag
    ladder has the same 16-member UDT, so the two readings fit it identically:
    the same one-variable trap the 8-per-definition claim fell into. No alarm
    definitions anywhere in the batch, since they are now known to cost zero.

    **Nothing is wired yet, and the reason is OQ-UDTMEMBERNAME.** The law above
    is the same `8 + 8 x floor(bool/2)` per UDT that OQ-UDTMEMBERNAME records,
    and it is contradicted there by `udttype_bool_n4` -- a structural twin with
    2-character member names that predicts EXACTLY while `alarmsep_u01_b04`
    with 7-character names is 24 short. Wiring the law would fix 97 rows and
    break that one, and the 47 pending `udtmn*`/`udtmn2*` files decide which of
    member-name length or BIT count is the real driver.

    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `almd_realtext`



34. **OQ-L9BUDGET** — no memory budget for the 1756-L9xTS family.
    `controller_budgets.yaml` returns None for all four catalogs, so the UI
    has no denominator on an L9 file and cannot show headroom.

    Deliberately not guessed. The catalog digits look like they encode
    memory (L902/L905/L908/L915), but that is a pattern, not a source, and
    this project has been wrong before inferring a constant from a catalog
    name. Needs the real per-catalog user memory from a datasheet or a
    controller.

    The UI degrades correctly today -- it shows the byte total without a
    percentage rather than inventing one.

    **Test files built 2026-09-08**: `fwmatrix_v38_1756_l9{02,05,08,15}ts`.

    **CAPTURED 2026-09-11, and they do NOT close it.** The premise above
    was wrong: the capture harness records memory USED, not the capacity
    denominator, and `message_value` came back 0 on all four. What the
    four files did settle is the **baseline**, which was a different
    question — an empty v38 L9 project measures 20,404 against 18,128 for
    a 1756-L81E on the same firmware, a flat **+2,276 with zero variance
    across all four catalogs**. Wired as a `catalog_baseline_delta`, and
    independently replicated by the 14 `alarmdef_l902ts_*` files, which
    sit exactly 2,276 above their L81 twins once the shared alarm offset
    is removed.

    The budget itself still needs the real per-catalog user memory from a
    datasheet or a controller. The UI continues to degrade correctly,
    showing the byte total with no percentage rather than inventing one. Generated at v38
    only -- the family postdates the v31-v37 firmwares in the matrix, and
    building an L9 at v31 would fabricate a firmware that never shipped.


37. **OQ-UDTMEMBERNAME** (supersedes OQ-UDTBOOLMEMBER) — a UDT member's
    NAME LENGTH is unmodelled, and the whole corpus is blind to it because
    every generator ever written used two-character member names.

    The `alarmsep` batch captured 2026-09-11 and its 15 points fit one law
    with **zero residual**:

        deficit = udt_definitions x (8 + 8 * floor(bool_members / 2))

            u\b      1     2     4     8    16
              1     -8   -16   -24   -40   -72
              2    -16   -32   -48   -80  -144
              4    -32   -64   -96  -160  -288

    That reads as a BOOL-member cost, which is what OQ-UDTBOOLMEMBER
    predicted, and it is **wrong**. `udttype_bool_n4` is a structural twin
    of `alarmsep_u01_b04` — one UDT, one hidden backing SINT, four BIT
    members, no tags, both type names bucketing to the same ceil(len/8) —
    and it predicts EXACTLY while alarmsep_u01_b04 is 24 short. The one
    thing that differs is the member names: `M0`..`M3` against
    `Sts_A00`..`Sts_A03`. Two characters against seven.

    So the driver is member name length, or something travelling with it,
    and alarmsep cannot separate them because it varies BOOL count and
    total name length together. Nothing is wired off that law.

    `udt_definition` charges for the TYPE name (`name_per_8_chars`) and
    nothing at all for member names. Real programs are nothing like the
    fixtures:

        311DGeneratedProgram          689 members, avg  8.2 chars
        BaillieLeitchField_Edger      619 members, avg 10.2 chars
        Elmsdale                      877 members, avg 10.7 chars
        SJ_Gormley                    509 members, avg  9.8 chars
        FlareFunction_311D          2,284 members, avg  9.7 chars
        BAI10048_TrimmerTally       1,861 members, avg 12.3 chars

    **Test files built 2026-09-11**, `gen_udt_membername.py`, 24 files, all
    1756-L81E v35, type name held at exactly 8 characters throughout so the
    already-modelled type-name bucket cannot move. The engine predicts
    IDENTICALLY across every name length in every arm, so all 24 are direct
    measurements of an unmodelled quantity:

      - `udtmn_bool_short_b{01,02,04,08,16}` — BOOL count at 2-char names.
        The control; should predict exactly, matching udttype_bool_n4.
      - `udtmn_bool_l07_b{01,02,04,08,16}` — the same counts at alarmsep's
        7-char names, with no alarm definitions in the file at all.
      - `udtmn_bool_len{02,04,08,12,16,24,32}_b04` — the pure name-length
        sweep. Free, per character, or bucketed by 8 like every other name
        cost in this model?
      - `udtmn_dint_len{02,07,16,32}_n04` — the same on DINT. BOOLs are the
        one member kind with a hidden backing SINT, so this rules a
        BOOL-specific explanation in or out.
      - `udtmn_bool_len{02,07,16}_b16` — name length where a second backing
        SINT appears, and where the alarmsep law needed floor(b/2) rather
        than a flat per-member rate.

    **HOLE FOUND IN THAT BATCH, 2026-09-11, same day.** All 24 `udtmn_*`
    files carry `tags_xml=""`. Zero tags, in every arm. So whatever they
    measure, they measure it PER DEFINITION, and they are structurally
    incapable of saying whether the same term is ALSO charged per tag of the
    type. That distinction is the whole of the real-file exposure: AccuTally
    carries 33,574 UDT tags against 174 UDT definitions -- 193 tags per
    definition -- so a per-definition name term and a per-tag one differ by
    more than two orders of magnitude on that file. It is the identical
    failure mode OQ-DEFSCALE's captured sweeps hit from the other direction.

    `gen_udt_membername2.py`, **23 more files**, built from the same
    `_member_name()` / `_type_name()` so every arm differences straight
    against the 24 pending ones. Type names stay at 8 characters throughout,
    and the engine predicts IDENTICALLY across name length in every arm, so
    every difference is a measurement:

      - `udtmn2_bool_len{02,16,32}_b04_t{01,05,25}` (9) — the same 4-BOOL UDT
        at three name lengths with 1/5/25 tags of it; the t=0 point already
        exists. Per-definition means the length effect is identical at every
        t; per-tag means it grows 25x across the arm.
      - `udtmn2_dint_len{02,32}_n04_t{01,25}` (4) — the same on DINT. A
        BOOL-specific explanation was already assumed once and was wrong
        (OQ-UDTBOOLMEMBER), so no name-length result is believed on BOOL
        evidence alone.
      - `udtmn2_nest_len{02,32}` (2) — an outer UDT whose 4 members are each
        an inner UDT with 4 members at the swept length. Are a nested type's
        member names charged again inside every containing definition? If so
        the cost compounds with nesting depth, and real programs nest heavily.
      - `udtmn2_bool_len32_b04_arr{010,100}` (2) — one tag that is an array of
        10/100 elements. Per-tag applies once; per-element multiplies.
      - `udtmn2_aoi_{plen,llen}{02,16,32}` (6) — the same question for an AOI's
        PARAMETER and LOCAL TAG names, which no generator has ever varied.

    **Do not oversell this as the fix for the real-file error.** Checked
    directly: the real-file deficit per declared member/parameter/local tag
    ranges from **+15 to −46 bytes** across the 16 real programs, and four
    of them over-predict. Whatever drives the 2–5% real-file error is not
    one missing per-name term, and this is not it. It is a real gap worth
    closing on its own terms, not the headline.

    Also confirmed by this batch, and worth keeping: **alarm DEFINITIONS
    cost nothing.** Every `alarmsep_*_alarm` measured byte-identical to its
    `_noalarm` twin, and `def1/def2/def3` identical again.



    **THE NAME-LENGTH LAW IS SOLVED AND WIRED 2026-09-13 (capture-batch
    segments 10 and 11, `udtmn2_*` 23 files and `udtmn_*` 24 files).** A UDT
    definition charged NOTHING for its members' own names. They cost the SAME
    8-aligned pool as an AOI definition's member names — which is the right
    answer for the right reason: it is the same thing, a definition's member
    names, in the same file format.

        member_name_pool = 8 * ceil(sum(len(name) + 1) / 8)

    `udtmn_bool_len{02,04,07,08,12,16,24,32}_b04` holds four BOOL members and
    varies ONLY the name length, so nothing else can move:

    | name length | 02 | 04 | 07 | 08 | 12 | 16 | 24 | 32 |
    |---|---:|---:|---:|---:|---:|---:|---:|---:|
    | residual before | −8 | 0 | +8 | +16 | +32 | +48 | +80 | +112 |
    | increment | | +8 | +8 | +8 | +16 | +16 | +32 | +32 |

    The pool's own increments are those same seven numbers. **A raw
    1-byte-per-character rate fits five of the seven and misses 04→07 (it wants
    +12) and 07→08 (it wants +4)** — that pair is the whole discrimination, and
    nothing in the `udtmn2_*` batch could have made it, because every one of its
    name lengths lands on the same residue mod 8. The two batches together are
    what settled the form; either alone would have fitted the wrong one.

    Cross-checks, all clean: `udtmn2_bool_len{02,16,32}_b04_t{01,05,25}` is FLAT
    in tag count at each length (−8/−8/−8, +48/+48/+48, +112/+112/+112), so the
    cost is per DEFINITION and not per instance. `udtmn2_dint_len{02,32}_n04`
    and `udtmn2_nest_len{02,32}` agree at 4 and 8 members. And the six
    `udtmn2_aoi_*` rows are the control — flat at −4 across all three lengths,
    because segment 4 had already priced the AOI side.

    **Effect.** Every family is now flat in name length, where it used to span
    120 bytes. The `udt` category is **108 of 108 within 1%** (mean absolute
    error 0.148%). On the sixteen real programs, mean absolute error
    **2.025% → 1.605%** and sum-weighted **+2.145% → +1.245%** — the largest
    single real-file gain of the day, because real UDT member names average
    around 12 characters and a real program carries 174 UDT definitions. The
    residual also went two-sided again: five programs now over-predict, worst
    +3.28% (was +4.22%), and `pukall_gang` is −0.06%.

    **WHAT IS LEFT, and it is deliberately NOT fitted.** With the length law in,
    every family collapses to a per-shape CONSTANT over-charge:

    | shape | declared members | hidden BOOL runs | residual |
    |---|---:|---:|---:|
    | `udtmn_bool_l07_b01` | 1 | 1 | −8 |
    | `udtmn_bool_l07_b02` | 2 | 1 | −16 |
    | `udtmn_bool_*_b04` | 4 | 1 | −24 |
    | `udtmn_bool_l07_b08` | 8 | 1 | −40 |
    | `udtmn_bool_*_b16` | 16 | 2 | −64 |
    | `udtmn_dint_len*_n04` | 4 | 0 | −32 |
    | `udtmn2_nest_len*` | 8 | ? | −64 |

    `−(4m − 8r + 16)` fits five of those seven exactly and misses `b01` by 4 and
    `nest` by 16. That is **three constants** — a `per_member` of 12 rather than
    16, a `bool_run_bonus` of 40 rather than 32, and a −16 per definition — fitted
    to five points, in the one family where member count and hidden backing SINTs
    are inseparable. Fitting it is precisely the move that gave the AOI
    definition four overlapping terms and had to be undone. It needs a UDT
    member-count sweep with NO BOOL members, so runs cannot confound the count;
    the existing `dint_n04` is the only such point.

    Also recorded: hidden backing SINTs are excluded from the pool, the same
    convention `declared_member_count` already uses. Their generated names are
    long (`ZZZZZZZZZZBoolMember00`, 22 characters), so including them would be a
    large change, and the member-COUNT arm is exactly where that would show —
    and it does not come out flat either way.

38. **OQ-JSRFOLD** — new, 2026-09-11. A JSR and its target routine are
    over-charged at low counts and under-charged per unit, and the shape
    points at how the target's cost is folded in.

    `forloop_ctl_r{001,005,025,100}` — N JSR rungs against N target
    routines, built as the control arm for FOR:

        N      predicted   actual   delta
        1         18,831   18,552    +279
        5         20,235   19,960    +275
       25         27,255   27,000    +255
      100         53,580   53,400    +180

    Both arms are exactly linear and they disagree in two ways at once:
    actual is `18,552 + 352(N-1)`, predicted is `18,831 + 351(N-1)`. So a
    fixed **+279 excess** plus **1 byte per unit short**.

    Routine shells alone are not the problem: `subrtn_shell_r100` adds 100
    extra routines and predicts exactly, 12 of 12 across that family. What
    differs here is that these targets are JSR TARGETS, and report.py
    deliberately never emits a JSR target as its own SizeEntry — its cost
    is folded into the caller instead (`RoutineLogic.is_jsr_target`). The
    FOR arm has the same 100 target routines and, once FOR was weighted,
    predicts exactly at all four counts; those targets are NOT JSR targets
    and so are emitted normally. That asymmetry is the suspect.

    Not wired. A 1-byte-per-unit term is not a plausible memory quantity on
    its own, so the fold-in is probably misattributing a larger cost rather
    than being off by one, and guessing at that would be fitting noise. The
    isolation needed is a JSR-target sweep that varies the TARGET's own
    content while holding the call count fixed, which nothing covers:
    every existing JSR file uses a one-rung target.

    Stake: real programs are full of JSRs. Small per-file, but it applies
    everywhere.



    **CAPTURE ERRORS: 2 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    2 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `jsr_midchain_leaf_control`, `jsr_midchain_real_chain`

40. **OQ-AOIDEFITEMIZE** — an AOI's priced definition cost and its own
    itemized member breakdown are two different computations, and they
    disagree by a large margin on every real AOI.


    **IN-DEPTH REVIEW 2026-09-18 — the `mbshape_*` family read in full, and the
    answer is that it is NOT a per-member constant, which is worth knowing
    because the shape of the residual makes it look like one.**

    `mbshape_*` is 15 files built to a real program's AOI profile (19
    definitions, 453 parameters, 280 local tags) with one axis varied at a time.
    It sits at 2.36% mean absolute error while every isolated AOI family is
    essentially exact -- `aoipack_*` 281 rows at 0.048%, `aoistructure` 110 rows
    at 0.118%, `aoi` 159 rows at 0.037%. So whatever this is, it does not show up
    when one AOI is measured alone.

    Regressing the residual on definition count, parameter count and local-tag
    count over all 15 rows:

        residual = -1.9 x parameters - 1.9 x locals - 97     RMS 1,496 -> 33

    Parameters and locals carry it at the SAME rate, from two independent axes
    over a 2.3x span, and the fit is tight. Definition count does not: its
    coefficient is +2.4 and its three rows are the three worst fits (+85, -61,
    +57). `mbshape_rungs_{05,10,20}` are byte-identical to each other, so AOI
    internal rung count is priced correctly and contributes nothing here.

    **Why it is NOT wired: the rate is not an integer, and splitting it does not
    make it one.** A per-member cost has to be a whole number of bytes. Fitting
    BOOL and non-BOOL members separately gives -1.11 and -2.62 and barely moves
    the residual (RMS 35 against 37 for the single shared rate), so the
    BOOL-packing explanation is refuted rather than unconfirmed. A non-integral
    per-member rate that is stable across two axes is the signature of something
    being counted at a different granularity than the thing it correlates with.

    **Real exposure is small**: roughly 5,000 declared members across the 331 AOI
    definitions in the sixteen programs, so about 9,500 bytes, 0.01%. This is not
    where the remaining error is, which is the other reason it is recorded rather
    than fitted.

    **What would settle it**: a single-definition file with the same
    BOOL/BOOL/REAL/DINT/BOOL/REAL type cycle, member count swept 6/12/24/48. If
    the rate survives at one definition it is genuinely per member and the
    non-integer is an averaging artifact to be decomposed; if it vanishes, it
    belongs to the 19-definition shape and the per-member reading is a
    coincidence of this family's construction.

    Found 2026-09-11 while making the treemap sum to the report. For each
    AOI, `report.py` charges a definition cost (per-declared-member rate
    table plus the type-name-length bucket, OQ-AOIDEF's wiring), while
    `sizing/tree.py`'s `expand_definition_children` enumerates the same
    definition member by member. The enumeration always comes in LOWER.
    On Elmsdale, all 21 AOIs:

        AOI               priced    itemized    unexplained
        DriveAxis         18,873       3,633         15,240
        T_DST             12,344       3,000          9,344
        TS_VFD            10,581       3,361          7,220
        T_Clock            6,975       2,231          4,744
        VirtualAxis        6,589       2,085          4,504
        HomeToTorque       6,122       1,902          4,220
        TS_TrackSts        5,268       1,568          3,700
        ... (21 total)                              66,908

    66,908 bytes, 6.1% of that file's whole predicted total, is charged by
    the report and accounted for by nothing in the breakdown. It is not
    a rounding effect and it is not uniform: it scales with something the
    member enumeration does not see.

    Two possibilities, and they need separating before either is acted on:

      - The per-member rate table is right and the enumeration is
        incomplete — it is missing whole categories of declared thing
        (nested UDT members expanded at the wrong depth, InOut parameters,
        local tags of structured type). This would be a pure display bug.
      - The rate table over-charges and the real definition cost is closer
        to the enumeration. This would be a SIZING error worth 6% on a
        real file, which is six times the whole error budget.

    The first is more likely — the rate table was fitted against real
    capture data and the real-file error is currently 2.17%, which a 6%
    over-charge would not survive — but "more likely" is not measured.

    The isolation test is cheap and exists in shape already: a
    single-AOI file whose definition declares a known member roster,
    captured, differenced against the same file with one member added.
    `aoidef_*` covers the flat single-type case; what is missing is an AOI
    whose members are themselves structured (a UDT member, a TIMER, an
    InOut of UDT type), which is exactly what every real AOI above has and
    every existing test file lacks.

    Until then the UI carries the difference as an explicit
    "Unitemized definition cost" row rather than dropping it, so the
    treemap sums to the report total and the size of the unexplained part
    is visible instead of silent.


    **CAPTURE ERRORS: 40 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    43 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `aoi_logic_scale_010`, `aoi_logic_scale_050`, `aoi_logic_scale_100`, `composite_realistic_03_r2`, `composite_realistic_04_r2`, `composite_realistic_05_r2` (+37 more)

41. **OQ-POINTIOCONN** — a POINT I/O card's memory cost depends on its
    connection format, which the model does not represent at all, and the
    flat rate it charges instead is wrong in both directions.

    Three real captures, 2026-09-11. Identical content otherwise: one
    1756-L81E v35, one adapter, sixteen 1734-IB8/C cards. The non-module
    part of the prediction is byte-identical (18,336) across all three, so
    the whole difference is the I/O subsystem.

        format          adapter          actual   module subsystem   per module
        Enhanced        1734-AENTR/C     32,616        14,280             840
        Enhanced Data   1734-AENTR/C     37,320        18,984           1,117
        Optimized       1734-AENT/A      28,688        10,352             609

    Against predictions of 47,280 / 47,360 / 20,050 — over by 45% and 27%
    on the first two, under by 30% on the third.

    The three formats are structurally distinct in the L5X and the parser
    already tells them apart:

      - **Enhanced** — the card has a ConfigTag and NO `<Connections>`
        element at all.
      - **Enhanced Data** — the card carries its own `InputData`
        `<Connection>`.
      - **Optimized** — the card carries `<RackConnection><InAliasTag/>`,
        its I/O aliased into the adapter's own Slot array.

    One clean single-variable result is already in hand. Enhanced Data
    minus Enhanced is the same adapter, the same sixteen cards and only
    the connection format changed: **+4,704, exactly 16 × 294.** A card's
    own connection costs 294 bytes more than no connection. That is a real
    per-module, per-format cost and nothing in the model has a term for it.

    What is NOT separable from these three points: the adapter's own cost
    from the per-card cost, because every file has sixteen cards; and the
    Optimized arm changes the adapter catalog (1734-AENT/A) at the same
    time as the format, confounding the two.

    Both fall out of a count sweep — the same differencing method every
    other constant in this project came from. For each format, N =
    1, 2, 4, 8, 16 cards: the slope is the per-card cost of that format
    and the intercept is that adapter's own cost, each fitted
    independently of the other.

    **Built 2026-09-11**, `gen_pointio_conn_sweep.py`, **15 files** --
    `pioconn_{enhanced,enhdata,optimized}_n{01,02,04,08,16}`, 1756-L81E
    v35, every module block verbatim from the real exports. Only what
    genuinely depends on the card count is rewritten, and the three
    formats need different rewrites because they carry the rack
    differently:

      - **Enhanced Data** -- the adapter's InputTag is just the two status
        DINTs and every card carries its own self-contained Connection.
        Only the card count, the adapter's Bus Size, the L5K per-slot
        blobs and the rack-sized `pad` arrays on its input and output
        types change.
      - **Enhanced** -- the adapter's InputTag holds one StructureMember
        per card (`Slot01`..`Slot16`), and the file DEFINES that
        module-scoped type itself under `<ExtendedProperties>`, so the
        slot list is rewritten in both places alongside the status arrays
        and the output pad. The type NAME carries a Studio-computed hash,
        `AB:1734_ERACK_649387C8:I:0`, which is not derivable from the
        L5X, so it is kept verbatim; the file supplies the matching
        definition. Whether Studio 5000 accepts a self-described type
        whose hash it would have computed differently is something a real
        conversion answers and guesswork does not.
      - **Optimized** -- every card is rack-aliased into the adapter's own
        SINT array and the profile is named after the slot count,
        `AB:1734_17SLOT:I:0`. Systematic rather than hashed, so it is
        rewritten to match along with the array dimensions and element
        lists. Unlike the Enhanced case this type is NOT defined in the
        file -- it is a catalog profile -- so if `AB:1734_<n>SLOT` does
        not exist at some n, that file fails to import.

    A conversion failure in either of the latter two arms is a RESULT, not
    a defect: it says the rack-optimized profile exists only at certain
    sizes, or that the ERACK hash must match. Logged, not worked around.

    Verified before shipping: slots 1..N, adapter Bus Size N+1, per-slot
    L5K arrays and pad dimensions all N+1, slot member lists trimmed in
    both the Decorated structure and the type definition, and zero sizing
    errors in the two arms the model can price.

    **Naming arm, 12 more files** (`pioname_*`). Every card in all three
    real exports is NAMELESS -- catalog and slot only. That is the unusual
    shape, not the normal one: a module you name in the I/O tree gets
    module-defined tags of its own, and this model already charges real
    bytes for a tag's NAME LENGTH elsewhere (`alias_tag`, the AOI and UDT
    type-name-length buckets). So naming a card plausibly costs something,
    plausibly scales with the name, and plausibly differs by connection
    format -- a rack-aliased card has no tag of its own to name, so it may
    be free there and not free in the other two.

      - `pioname_{enhanced,enhdata,optimized}_named_n08` — 8 named cards,
        8-character names, one per format. Differences against the
        nameless `pioconn_<fmt>_n08` at the same count.
      - `pioname_enhdata_len{05,08,16,24,32}_n08` — the same 8 cards at
        five name lengths. Flat rate or per character?
      - `pioname_enhdata_named_n{01,02,04,16}` — named-card count, against
        the nameless file at each count. Per card or once per file?

    The engine currently predicts **exactly the same total named or
    nameless, at every length and every count** — it has no term for a
    module name at all. That makes all twelve direct measurements of an
    unmodeled quantity: any nonzero capture delta is a gap, and a zero
    delta confirms the zero rather than leaving it assumed.

    Stake: this is not a corner case. Elmsdale alone has three of these
    racks (JB101_IO, C102_IO, MCP101_IO — 19 cards), all currently priced
    at either a flat 1,672 they do not cost or, for the rack-aliased ones,
    at zero.

    **IN-DEPTH REVIEW 2026-09-18 — all 27 rows captured and read. Every slope
    is now measured; NOTHING is wired, and the reason is a classifier problem
    rather than a measurement one.**

    **The per-card cost, by connection format.** Differencing consecutive card
    counts within each format, which cancels both the adapter and the file base:

    | format | n=1 | 2 | 4 | 8 | 16 | per card |
    |---|---:|---:|---:|---:|---:|---:|
    | Optimized | +574 | +566 | +566 | +582 | +582 | **0 — flat** |
    | Enhanced | +648 | −496 | −2,776 | −7,304 | −16,392 | **−1,136** |
    | Enhanced Data | +643 | −218 | −1,924 | −5,320 | −12,144 | **−852** |

    The Optimized arm is FLAT across a 16x span — a rack-aliased card is priced
    correctly today and the +570 it carries is a per-file constant, not a slope.
    The other two are over-charged by 1,136 and 852 per card, exactly linear
    from n=4 upward (n=2 and n=4 sit 8 and 16 off the line, the usual small
    noise). Their difference, 284, is the same order as the 294 bytes per card
    the three original real captures put on Enhanced Data over Enhanced, so the
    RELATIVE ordering the model has is right and the absolute level is not.

    **The module-NAME measurement, which was the naming arm's whole point, and
    it is unambiguous.** `pioname_enhdata_len{05,08,16,24,32}_n08` — 8 cards,
    name length the only variable:

        length     5      8     16     24     32
        residual -4,808 -4,808 -4,744 -4,680 -4,616

    Length 5 and length 8 are IDENTICAL, and every 8 characters after that is
    exactly +64 across 8 cards, i.e. **8 bytes per card per 8 characters, with
    the first 8 characters free.** The engine charges a module name nothing at
    all, so this is a direct measurement of an unmodeled quantity, as designed.
    The named-versus-nameless arm adds that having a Name AT ALL costs 64 per
    card (+64, +128, +256, +512 at n=1, 2, 4, 8 — per card, no free first one),
    but a nameless module cannot occur in a real export, so that 64 is already
    inside the per-catalog `module_overhead` that was fitted on real modules.

    **NOT wired, and the disagreement is worth stating precisely.** The measured
    module-name law is `8 × ((len − 1) // 8)` — a full eight characters free.
    The shared `identifier_name_length` law, KNOWN from the program, task,
    routine and JSR-target sweeps, is `8 × (len // 8)` — it charges 8 at exactly
    length 8, where these files measure 0. One 8-byte bucket apart, on the
    strength of one length pair. Real exposure across all sixteen programs is
    **449 modules and 4,816 bytes, 0.05% of the real set**, so introducing a
    SECOND name law for that is not justified; recorded here instead, and the
    len05/len08 pair should be repeated before anyone acts on it.

    **The per-card correction is NOT wired because real cards cannot be
    classified.** Real exposure is 45 POINT I/O modules in 4 of the 16
    programs — Elmsdale 20, FlareFunction 14, CMU 7, K3M16 4 — so at 1,136 per
    card this is 38,000 to 51,000 bytes, material. But at the CARD level an
    Enhanced card and an Optimized card are structurally identical in L5X: both
    carry no `<Connection>` element at all, and they differ only in the
    adapter's InputTag. 34 of the 45 real cards are in exactly that
    indistinguishable state. The two formats' corrections differ by 1,136, so
    guessing is worse than not charging.

    And the sweep cannot settle it, by its own admission: the Optimized arm
    changes the adapter CATALOG at the same time as the format, so "Optimized is
    flat" and "that adapter is flat" are not separated either.

    **One observation that should be tested rather than believed.** Applying
    −1,136 per card to Elmsdale's 20 cards takes its residual from **+22,862 to
    +142** — from 1.99% to 0.01%. That is either a coincidence or it says
    Elmsdale's racks are Enhanced and this is most of its remaining error. The
    same correction makes FlareFunction, which over-predicts, substantially
    worse. So the hypothesis is testable and the test is cheap: Elmsdale's
    adapters are named `JB101_IO`, `C102_IO` and `MCP101_IO`, and reading which
    format each one uses off the real export settles which way the correction
    goes on the one real program where it matters most.

    **What is needed: two files, not twelve.** The same adapter catalog
    (`1734-AENT/B`) carrying 8 cards in Enhanced and in Optimized form — the
    one comparison this batch confounded. That separates the format from the
    adapter, and with it the 34 unclassifiable real cards become classifiable
    by their adapter's InputTag shape.


42. **OQ-AXISMARGINAL** — new 2026-09-11, and the largest single-sign
    unreconciled block in the corpus. Found by `scripts/unreconciled.py`, also
    new that day, which recomputes every captured row against the CURRENT
    engine: **1,601 of 2,770 captured rows sit outside +-8 bytes**, and the
    worst family by magnitude is the 31-row axis set, captured 2026-09-03.

    Every `axis_scale_*` file with n>=2 over-predicts, monotonically, to
    **+62,528 bytes (+10.5%)** at 20 axes. Both arms are perfectly linear in
    axis count with zero residual at every step:

        single-axis drives   +3,288 per axis    n = 2,4,6,8,12,16,20
        dual-axis drives     +2,600 per axis    n = 2,4,6,8,12,16,20

    and the two shared base points (n=1 single, n=2 dual) both sit at +56 —
    exact. So the FIRST axis in a file is priced right and every one after it
    is not. This is a marginal error, not a base-constant error, which matters
    because `AXIS_CIP_DRIVE` was promoted FITTED -> KNOWN earlier the same day
    on single-axis evidence. That promotion is correct for one axis and wrong
    for the twentieth, and the entry should be read that way until this
    closes.

    Real exposure: the sixteen real programs carry **359 AXIS_CIP_DRIVE and 65
    AXIS_VIRTUAL** tags. At the single-arm rate that is roughly **650 KB** of
    over-prediction sitting inside the real totals, the same order as
    OQ-MODULEMARGINAL's 824,864 — and in the same direction, so the two
    together are most of what the under-predicting real files are being
    compensated by.

    **Why the two arms do not decompose on their own.** The naive subtraction
    gives a clean-looking answer:

        single: 1 module per axis      A + M    = 3,288
        dual:   1 module per 2 axes    A + M/2  = 2,600
        -> M = 1,376, A = 1,912   (A identical from both arms)

    It is not valid, for two reasons that come from reading the files rather
    than the numbers:

      - The single arm is 8 x 2198-S086-ERS3, **one catalog repeated**. The
        dual arm is one each of D012/D020/D032/D057, **four distinct
        catalogs**, repeating only as n grows. OQ-MODULEMARGINAL's open
        question is exactly whether the module discount is per catalog or per
        file, so `M` is not the same quantity in the two arms.
      - **Every one of these 31 files carries `error_count = n+1` with an
        EMPTY `error_log`.** All 144 errored rows in the manifest were
        captured between 2026-08-23 and 2026-09-08; the error-log reader in
        `logix_build_capture.ahk` only began working 2026-09-10, so not one of
        them has any error text on record. The n=1 file has 2 errors and is
        still byte-exact, which suggests they are benign — but that is an
        inference, and this is the direct reason a 31-row family with a 10%
        systematic error sat unexamined: there was no way to tell whether the
        rows were trustworthy. **The 144 errored rows need recapture under the
        current tooling**, and that is the single highest-value thing the
        capture rig can do.

    **Test files built 2026-09-11, `gen_axis_marginal.py`, 16 files.**

      - `axmarg_virtual_n{01,02,04,08,12,16,20}` (7) — the decoupling arm.
        AXIS_VIRTUAL needs no drive module at all, so a count sweep with ZERO
        modules in the file measures the per-axis term with nothing to share
        it with, which neither captured arm can do. Real programs carry 65 of
        these, so it is their real shape.
      - `axmarg_1cat_n{02,04,08,12,20}` (5) — the same axis and module counts
        as the captured `axis_scale_n*_dual`, but ONE catalog repeated instead
        of four distinct. Same axes, same modules, only catalog repetition
        differs.
      - `axmarg_ncat_n08_{1,2,4}cat` (3) — axis count AND module count both
        pinned at 8 and 5; only the number of distinct catalogs moves. All
        three predict an identical 245,080 (they draw from one catalog family
        the engine prices identically), so any difference in the captured
        actual is purely the catalog-diversity effect. Under a per-catalog
        discount the three differ; under a per-file one they do not move.
      - `axmarg_mixed_n08` (1) — 8 AXIS_VIRTUAL plus 8 AXIS_CIP_DRIVE in one
        file, against the two single-type files at the same count: is the
        marginal term per axis TAG regardless of type, or per type?

    **Do not wire any of this before the virtual arm lands.** The 1,912/1,376
    split is arithmetically exact on 14 points and still rests on an
    assumption the data cannot support, which is the same mistake the axis
    promotion already made once today.

    **CAPTURE ERRORS: 57 row(s)** flagged here by `scripts/capture_errors.py` (step 2b),
    recounted 2026-09-17. Was 51; the 6 added are `axis_scale_n02_dual`,
    `axis_scale_n08_dual`, `axis_scale_n08_dual_regen` and
    `axmarg_ncat_n08_{1cat,2cat,4cat}`, all newly captured in the 212-row batch
    and all failing for the SAME newly-diagnosed reason as OQ-MODULEMARGINAL's
    six -- see the bus-sharing diagnosis recorded there. This is the first time
    any axis-family row has carried real Studio error text.
    Previously 51, before that 74, then 56.
    Was 74, then 56. The last 5 went when `axis_scale` was trimmed from 18 files to
    7 on 2026-09-14: nine count points per shape bought nothing a four-point
    geometric ladder does not, every one of them needed recapture anyway for the
    Ch2/Ch3 fix, and the marginal has been flat wherever this project has measured
    one. Removed: `axis_scale_n{04_dual,06_single,06_dual,12_single,12_dual,
    16_single,16_dual,20_single,20_dual,20_dual_regen,08_single_regen}`.
    **18 were CLEARED 2026-09-14** -- the nine `axmarg_*` drive
    files and the nine `axis_scale_*_dual*` files -- because their content changed:
    a 2198-P bus supply plus its converter axis were added to the first group and
    the second group's dual-axis channel was corrected from Ch2 to Ch3. Their old
    `actual_bytes` measured a project whose drives never got bus power, so it
    describes content the repo no longer holds. See OQ-MODULEMARGINAL for the
    root cause and the evidence.
    65 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `axis_scale_n01_single`, `axis_scale_n02_dual`, `axis_scale_n02_single`, `axis_scale_n04_dual`, `axis_scale_n04_single`, `axis_scale_n06_dual` (+59 more)
    1 committed file(s) attempted and never reached `ok` in
    `convert_log.csv`: `daxis_axis_cip_drive`


44. **OQ-ALARMCONDREAL** — new 2026-09-14, from the strip ladder. Tag-based
    alarm conditions are the **second-largest category in both real programs
    measured**, and the wired model is nearly exact on one of them and 8.8%
    short on the other.

    | | conditions | actual step | predicted step | per condition actual | per condition predicted |
    |---|---:|---:|---:|---:|---:|
    | `griffin_stackerline_1mar25` | 400 | 443,128 | 442,400 | 1,107.8 | 1,106.0 |
    | `elmsdale_20251017r01` | 200 | 243,040 | 221,600 | **1,215.2** | 1,108.0 |

    That is 19% and 21% of the whole program respectively. The step is clean:
    an exhaustive element-tag diff of each full export against its `NoAlarms`
    sibling shows `AlarmCondition`, `AlarmConfig`, `HMIGroup` and the
    `AlarmConditions` container are the **only** elements that differ — no tags,
    rungs, routines, programs, UDTs or AOIs moved.

    These are controller-scope **Alarm Manager** alarms, and they must not be
    confused with a scheduled program that happens to be named for alarms.
    Elmsdale has both: 200 controller Alarm Manager conditions, and a separate
    `AlarmsAndMessages` **program** of ordinary ladder whose
    `TiltHoist_Alarms` routine makes 161 references to `Alarms_TiltHoist`. The
    two are measured by different files and never double-count — `NoAlarms`
    strips the definitions and keeps the program, the per-program `NoAlarmMsg`
    strips the program and keeps the definitions, and because the associated
    array is a CONTROLLER tag neither strip leaves a dangling reference.

    Only the alarm definitions were stripped; the associated tags remain in the `NoAlarms`
    files as ordinary controller tags, so their data cost is NOT inside this
    step. `alarm_conditions` prices the definitions 800 + 500n + an
    associated-tag term keyed on each `AssocTag1/2/3` target's resolved type.

    **ASSOCIATED-TAG AUDIT DONE 2026-09-14, AND IT RULES ITSELF OUT.** All 600
    Elmsdale and 1,200 Griffin associated-tag references were resolved:

        Elmsdale   Alarms_TiltHoist[0..199].{Number, Description, MoreInfo}
        Griffin    StackerAlarms[0..199].{Number, Description, MoreInfo}

    Both arrays are **the same UDT, `Alarms_SE`, at the same `Dimensions=200`**,
    with the same members (`SINT` filler, `BIT Active`, `STRING Description`,
    `STRING MoreInfo`, `DINT Number`) and the same three members referenced.
    An attribute-by-attribute frequency diff of all 600 conditions shows every
    one of the 37 `AlarmCondition` attributes identically distributed between
    the two programs **except the tag names themselves**, which the `alarmcond_*`
    batch already proved free. So associated-tag type mix cannot explain the
    gap, and neither can severity, delays, condition type, or HMI group.

    **The one structural difference found: conditions per array element.**
    Elmsdale has 200 conditions over a 200-element array (1:1). Griffin has
    **400 conditions over a 200-element array (2:1)** — its alarms come in two
    named sets, `StackerAlarm*` and `Stacker3Alarm*`, both pointing into the
    same 200 elements.

    **And the two files cannot both fit the wired shape.** Solving
    `cost = B + n·k` on the two measured steps gives

        200,088 = 200k   ->   k = 1000.44,  B = 42,952

    A non-integer per-condition cost means `base + flat-per-condition` is the
    wrong shape for a real Alarm Manager, not that one of the constants is
    slightly off. Two files cannot say what the right shape is.

    **This is NOT the parked ALMD/ALMA question (OQ-ALARMDEF).** That entry is
    parked because zero ALMD/ALMA *instructions* appear in any of the sixteen
    real programs, which remains true. Tag-based alarm *conditions* are a
    different feature, they are present in real programs, and on the evidence
    above they are one of the largest single levers on real-file error. The
    CLAUDE.md scope note has been corrected accordingly.

    **What the existing `alarmcond_*` batch already covers, and its two gaps.**
    39 of 43 rows captured clean. `alarmcond_count_bare_n000..n128` pins
    800 + 500 per condition exactly; `alarmcond_count_real_n001..n128` runs at
    exactly 1,104 per condition (500 + 604 of associated-tag cost), which is
    within 4 bytes of Griffin's measured 1,107.8 — the synthetic family and the
    real Griffin agree. Elmsdale at 1,215.2 is the outlier. Every row in the
    family reads `predicted = actual − 16` including `n000`, which has zero
    conditions, so that 16 is the generator shell and not an alarm term — it
    must not be wired as one.

    Never captured, and both are real gaps: `alarmcond_type_{trip, trip_high,
    trip_low, deviation}` (condition type is assumed free and has never been
    measured; every real condition is `TRIP`) and `alarmcond_hmigroup_len64`.

    **Next measurement, and it is small.** Hold condition count fixed and sweep
    **conditions per associated array element** (1:1, 2:1, 4:1) and array size
    independently — that is the only structural difference the audit left
    standing. Four to six files, plus the four never-captured
    `alarmcond_type_*` rows re-submitted.

45. **OQ-CTLSHELL** — new 2026-09-14, from the strip ladder. **A real export's
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

46. **OQ-LADDERBASE** — new 2026-09-14, and it blocks every conclusion the
    strip ladder produced on Elmsdale. **The per-program strip batch and the
    category ladder batch cannot both be true, and the discrepancy is
    18,000–25,000 bytes.**

    Nine per-program variants of `elmsdale_20251017r01` were captured — each
    the full export minus exactly one `<Program>`. Scored against the captured
    full-file actual of 1,147,896, every one of the nine is under-charged by a
    near-constant amount that has no relationship to program size:

    | program removed | routines | rungs | actual drop | predicted drop | engine |
    |---|---:|---:|---:|---:|---:|
    | `TiltHoist` | 21 | 267 | 109,004 | 81,264 | +27,740 |
    | `TiltHoist_Infeed` | 10 | 79 | 37,640 | 18,892 | +18,748 |
    | `Inputs` | 4 | 110 | 33,956 | 15,256 | +18,700 |
    | `Outputs` | 4 | 33 | 27,948 | 9,520 | +18,428 |
    | `TiltHoist_Outfeed` | 5 | 31 | 29,036 | 11,008 | +18,028 |
    | `InfeedData` | 4 | 31 | 36,488 | 19,160 | +17,328 |
    | `PlanerInterface` | 3 | 21 | 26,376 | 9,932 | +16,444 |
    | `Housekeeping` | 5 | 27 | 25,508 | 9,280 | +16,228 |
    | `AlarmsAndMessages` (the program) | 3 | 114 | 36,324 | 20,764 | +15,560 |

    **Those sum to +167,204 against a whole-file residual of +30,432 — 5.5x
    too much.** A per-program cost cannot behave that way. A 3-routine program
    and a 21-routine program cannot both cost ~17,000 more than predicted while
    the file containing all nine is only 30,432 short.

    **It is a baseline problem, not a model problem, and two independent checks
    say so.**

    *Base-free check.* `Inputs` and `Outputs` carry the same four routine names
    (`C102`, `JB101`, `Main`, `MCP101`) and differ only in content — 110 rungs
    against 33. Their predicted drops differ by 5,736 and their actual drops by
    6,008: **a gap of 272** with no baseline involved at all. The engine is
    right on the margin; the constant is common to every variant, which is the
    signature of a wrong shared base.

    *Solving for the base.* Setting each program's error to zero implies a
    full-file actual of 1,129,148 … 1,132,336 for seven of the nine, tightly
    clustered. Taking the median, **1,129,868 — 18,028 below the captured
    1,147,896** — re-scores the batch as:

        TiltHoist_Outfeed      +0        InfeedData          -700
        Outputs             +400        Housekeeping      -1,800
        Inputs              +672        PlanerInterface   -1,584
        TiltHoist_Infeed    +720        AlarmsAndMessages -2,468
        TiltHoist         +9,712

    Eight of nine inside ±2,500, from +15,560…+18,748. (This fit is circular on
    its own — the base is derived from the same rows it then scores. The
    independent evidence is below.)

    **THE INDEPENDENT CONFIRMATION, and it closes a second anomaly at the same
    time.** The alarms step does not use any per-program file. Re-scored against
    1,129,868 it goes from **+21,440 to +3,412**, and Elmsdale's cost per alarm
    condition moves from 1,215.2 to **1,125.1** against Griffin's measured
    1,107.8. The 107-byte-per-condition disagreement that OQ-ALARMCONDREAL was
    opened for is 17 bytes once the base is corrected. **One wrong number
    explains both anomalies**, which is a far better account than two unrelated
    structural effects.

    **What does NOT reconcile, and why nothing may be wired yet.** The Trials
    ladder rungs are still inconsistent with that base. `NoProgramLogic`
    (760,800) and `NoLogic` (733,988) imply the engine OVER-charges program
    content by 29,676, while the rebased per-program batch implies it is right
    to within about +4,950 in total. Those differ by roughly 34,600. Also
    unexplained: removing the whole `AlarmsAndMessages` **program** costs
    36,324 actual, while removing its same 3 routines **and** all 63 program
    tags **and** all 9 program shells costs 26,812 — strictly more content for
    strictly less memory, which no monotone cost model permits. (Neither of
    those touches the controller Alarm Manager, which is stripped by a
    different file.)

    So one of the two capture sessions carries an error of 18,000–25,000 and
    the arithmetic cannot say which. **Every Elmsdale conclusion in
    OQ-REALUNDER, OQ-ALARMCONDREAL and the logic-step split is provisional
    until this is settled.** Griffin's ladder is unaffected — it is a separate
    program captured in one pass and its steps close without a floating base.

    **CAPTURE ERRORS: none. RECAPTURED CLEAN, verified 2026-09-18.** The rows
    this entry used to flag as captured-with-errors now carry `error_count = 0`
    in the manifest, so their `actual_bytes` is trustworthy and every number
    above is drawn from clean captures. `scripts/capture_errors.py` routes no
    errored row here any more; the old block was a warning that had outlived
    its cause.

    **The measurement that settles it, and it is three files in one session:**
    the unmodified full export, `Elmsdale_NoAlarms`, and any one per-program
    variant, captured back to back without the software being restarted between
    them. If the full export reads ~1,129,868 the per-program batch is right and
    the Trials full-file number was wrong; if it reads 1,147,896 again then the
    per-program batch shares a common defect and the ladder stands.

48. **OQ-TAGORDER** — new 2026-09-18, raised from outside the model: "BOOL
    LINT INT DINT BOOL takes up different space in the controller than another
    order." **Does the ORDER in which controller tags are declared change what
    they cost?**

    **It has never been tested. Confirmed by search, not assumed.** The only
    order-varying files in the entire corpus are `aoidshape_order_*` — five
    files that permute AOI DEFINITION MEMBERS — and every tag family declares
    tags GROUPED BY TYPE: `type_bool_50tag` is 50 consecutive BOOLs,
    `typesweep_*` uses one fixed pool, `array_*` and `udtslot_*` the same. Not
    one file in 3,076 captured rows holds a mixed tag multiset and varies only
    the order.

    **The one order result that exists says order is free — at a DIFFERENT
    SCOPE.** `aoidshape_order_{boolsfirst,dintsfirst,alternating,pairs,blocks5}`
    permute the same BOOL/DINT multiset five ways inside an AOI definition and
    all five read **19,672 actual, +12 delta, byte-identical**. That is a real
    measurement about MEMBERS OF ONE PACKED STRUCTURE. Controller tags are
    separately allocated objects. The first does not answer the second and must
    not be cited as if it does.

    **Real programs look nothing like the corpus on this axis.** The declared
    type CHANGES between consecutive controller tags **33–60% of the time**
    (median ~52%) across the sixteen; generated files are ~0%. Dominant
    transitions: BOOL→DINT 1,297, DINT→BOOL 1,249, then REAL↔DINT and
    BOOL↔REAL. BOOL and DINT together are **58% of the 31,532 real tags**.

    **One correction to the hypothesis as raised, and it narrows the target.**
    8-byte types are essentially absent from the real set: **2 LINT tags out of
    31,532**, zero LREAL, zero ULINT. An alignment effect at LINT boundaries
    cannot be the real-file residual whatever it does in principle. The version
    that matters is BOOL/DINT/REAL interleaving.

    **WHY THIS SURVIVES THE TEST THAT KILLED EVERY OTHER TAG HYPOTHESIS.**
    2026-09-18 ruled out a per-tag constant at any value, a per-BOOL-tag
    constant, and a proportional scale on tag bytes — all three move the
    aggregate bias and leave the spread untouched. **An order effect is
    invisible to all three by construction**: it changes what a file costs
    without changing any count, so no per-unit or per-category correction can
    express it and no correlation against tag count can detect it. That day's
    conclusion should be read as "tags are not wrong by a scalar", NOT "tags are
    not wrong".

    It also fits the one signal that did survive: a 1% proportional increase on
    tag bytes cut the real spread 1.037 → 0.813, the only thing measured that
    day which moved spread rather than bias. A per-file order effect looks
    exactly like that from outside — roughly proportional to tag count, but
    varying file to file with how the engineer happened to declare them.

    **SPEC — 8 files, one fixed multiset, order the only variable.** Same design
    as `aoidshape_order_*`, one scope up. 25 BOOL + 25 DINT controller tags,
    identical names and name lengths, nothing else in the file:

      1. `tagorder_grouped_bd`   — 25 BOOL then 25 DINT
      2. `tagorder_grouped_db`   — 25 DINT then 25 BOOL
      3. `tagorder_alternating`  — B D B D … (49 transitions)
      4. `tagorder_pairs`        — B B D D B B D D …
      5. `tagorder_blocks5`      — BBBBB DDDDD …
      6. `tagorder_realchurn`    — the literal declaration sequence of the first
         50 controller tags of a real export, types transplanted, so the corpus
         finally contains one file with real churn

    Plus a three-type arm matching real composition (BOOL/DINT/REAL 33/25/11):

      7. `tagorder3_grouped`     — grouped by type
      8. `tagorder3_realchurn`   — real transition sequence

    **Read it by differencing WITHIN the set: all eight carry identical tag
    multisets, so any spread between them IS the order effect and nothing
    else** — no baseline, no engine constant, no other family involved. If they
    land together, order is free at tag scope too and this closes in one capture
    round. If they spread, the per-transition cost falls straight out of file 3
    (49 transitions) against file 1 (1 transition).

    **Priority: HIGH.** It touches 58% of real tags, it is the only untested
    dimension found that a scalar correction cannot express, and it is eight
    files.


---

# SECOND PASS: THE IN-DEPTH REVIEW, 2026-09-18

The table above was a triage — every entry recomputed, each given a status. This
pass went through the ones it left open one at a time, re-derived each question's
numbers from the captures on disk rather than from what the entry claimed, and
either wired the result or said in counted terms why not. **Real set 1.6894% →
1.6566% mean absolute error over the sixteen held-out programs, every one of them
the right way.** Corpus mean 1.4758% → below it, with two families rebuilt:
Structured Text 8.3291% → **0.0091%** and `unweighted_*` 4.6865% → **0.1574%**.

## Closed and wired in this pass

| question | what it turned out to be |
|---|---|
| **OQ-JSRPARAMCOST** | Every SLOPE closed. `b_multiparam_extra = 4` keyed on TOTAL operands (the row that decides it went +3,952 → −56); `per_target` 152 → 160 from an exact `8t − 280` across t = 1..50. What is left is two flat per-file constants, −184 and −280, on files of 18–256 KB. |
| **OQ-STEXPR** | All four assumptions measured. The one-operator row is a LOOKUP per operator class, not a lookup plus a premium; the premium vanishes on all-float operands; `**` is 38 not 80; conversion is per SOURCE keyed on the source's type; the AOI-call one-time is per ROUTINE. |
| **OQ-STEXPR-OPERATOR** | The "two unknowns from two points" blocker was a misreading of the law's own shape — it already has two regimes, so each point pins a constant alone. The six 2-operator files are now the falsification test, not the enabler. |
| **OQ-CPTARRANGE** | Arrangement is real and the rule is exact: +4 iff EXACTLY TWO tier-1 operators precede the first tier-2 one. Six rows out of 28, and it retro-explains four points it was not fitted to. |
| **OQ-VERIFINSTR** | `DTR = 40` (it had no weight at all, not the 16 the entry claimed) and 112 per JSR target whose SBR/RET carry operands — which also collapses OQ-JSRPARAMCOST's two file constants from 96 apart to 16. |
| **OQ-AOIINTERNALLOGIC** | The unmeasured `_DESTINATION_ARG` exposure SIZED at 9,312 bytes (0.09%) for every classification being wrong at once, so no test batch is justified. Two real table defects fixed: five entries named the wrong operand, and five word-destination writers were missing, GSV among them at 363 real occurrences. |

## Read in full and deliberately NOT wired, with the count

| question | measured | why it stays unwired |
|---|---|---|
| **OQ-COMPOSITESCALE** | The categories ARE additive: hold logic at 0 and every D×A×M combination reads within 40 of zero. The single non-additive term is compiled logic at −24 per rung, which is −12 × (3 − 1) — the OQ-SERIESOUTPUT law at a rung width nothing else tests. | It makes `addit_*` the THIRD independent confirmation of a law all sixteen real programs reject. The `sroutc_*` grid is the decisive measurement for the whole project. |
| **OQ-CPTREALDEST** | The ladder is exact at 7, 9 and 10 operators; `**` is +8 per extra operator, not a flat 12; the integer-destination float literal is +120 to +188 per rung and charged NOTHING. | The 5-operator base is a shape CONTRADICTION (324 all-REAL against 328 for three parenthesised/float-literal families) and every candidate fix repairs 4 rows and breaks 10. The float-literal term is not linear over three points. |
| **OQ-CPTNARROW** | `rate_T × k − 132`, eight of ten points exact, and SINT ≠ INT, which this entry assumed. | 27 real CPT calls with a narrow operand, all in ONE program, ~1,300 bytes. |
| **OQ-POINTIOCONN** | Optimized is FLAT across a 16x span; Enhanced −1,136 per card; Enhanced Data −852. Module names cost 8 per 8 characters with the first 8 free. | 34 of the 45 real POINT I/O cards are structurally indistinguishable between the two formats that differ by 1,136, and the sweep confounds format with adapter catalog. Two files fix that. |

## The one normalisation that had to be found before anything could be read

**A per-file constant of −352 runs through all 58 captured `cpt` rows from
`gen_cpt_closeout.py`** — except the five whose logic references a LINT tag,
which sit at 0. With that one substitution every residual in the batch is its
baseline plus an exact multiple of 4 bytes per rung, no exceptions. Without it
the batch looks like noise, and several readings in OQ-CPTREALDEST and
OQ-CPTARRANGE had been contaminated by a spurious 352 from differencing against
an older generator. The −352 itself is unexplained and has its own three-file
probe specified.

## Doc currency fixed in this pass

Seven `**CAPTURE ERRORS**` blocks were stale — `scripts/capture_errors.py` only
checks questions it routes errored rows TO, so a block whose rows have since been
recaptured is invisible to the gate and survives as a false warning. Audited all
19 against the gate's routing; the seven are replaced with a note recording that
those numbers are now known to come from clean captures. Two stale claims inside
entries were corrected: OQ-AOIINTERNALLOGIC's "11,241 instructions across 6 of
the 16 programs" (the real figure is 38,821 across all sixteen) and
OQ-VERIFINSTR's five siblings, which were already weighted by the time their
files were captured, so that batch confirms them rather than measuring them.
