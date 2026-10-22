# The Ranked Work Queue

**An item not on this list is not being worked.**

Phases and exit criteria are in `PROJECT_PLAN.md`. Project state, the accuracy
figures and the full elimination table are in `ROADMAP.md`. Individual questions are
in `OPEN_QUESTIONS.md`.

**Before adding anything here, state how many percentage points it should move on
the seventeen real programs, and by what mechanism.** An item that cannot state that
is not worked. If the mechanism is "a category cost constant is slightly wrong," the
ceiling result in `ROADMAP.md` already answers it.

---

## Where the error is, and where it is not

Category mass across the seventeen, as predicted bytes. **This is where the mass
is, which is not the same as where the error is.**

| category | bytes | share |
|---|---:|---:|
| `controller_tag` | 32,892,544 | 60.23% |
| `routine_logic` | 9,799,473 | 17.95% |
| `alarm_condition` | 5,151,920 | 9.43% |
| `udt_definition` | 3,423,387 | 6.27% |
| `module_io` | 1,587,575 | 2.91% |
| `program_tag` | 1,233,347 | 2.26% |
| `project_baseline` | 260,072 | 0.48% |
| `task_program_shell` | 259,724 | 0.48% |

**`controller_tag` carries 60% of the mass and is not where the error is.** Every
real tag shape is already covered; the untested ones total a few thousand bytes
against a residual two orders of magnitude larger. The name-length term — the
strongest-looking candidate — is cleared by 88 clean rows at mean 0.12%.

**Only two categories have a self-consistent required per-file correction**:
`controller_tag` (coefficient of variation 0.039) and `routine_logic` (0.087).
Everything else ranges into the absurd — `program_tag` needs a scale of 347 on one
file and −26 on another — which is a restatement of the fact that those categories
are too small to carry the residual.

---

## The queue

Re-ranked after the capture batch that followed the blind set. That batch closed five
questions (JSRCALLERBASE, RUNGSHAPE, ALARMCONDREAL, BUILDFAIL-OPEN, MODULENAMELEN) and,
by correcting the JSR caller base, exposed a larger real residual that a wrong
constant had been hiding: **mean 2.86%, worst 5.42% (now 0.77% / 3.87% on eighteen —
operand spelling, then OQ-INDIRECTUDT and OQ-MIXEDTYPE, below) on the standard-processor
real programs**.
Every item below is aimed at that.

### 0g. The 174-capture batch — DONE

All 174 captured with zero build errors and no flagged reads (L9/v38 96, operand
spelling 50, realism 16, program scope 12). Closed eight questions; wired two:
- **OQ-INDIRECTUDT**: an index followed by a member +40 (KNOWN), a BOOL element +20,
  a STRING element +108 (FITTED).
- **OQ-MIXEDTYPE**: DINT↔REAL and DINT↔INT conversions per operand (FITTED).
Real set 1.79% → **0.77%** mean, 4.83% → **3.87%** worst; full census: no exact or
within-8 generated row moved. Confirmed without wiring: program scope is free;
the plant prices exactly at 25% and 50% fill; POINT I/O address = BOOL = alias;
REAL member/array spelling and AOI surcharges; STRING MOV = DINT MOV; L9 v38 = L81E
v38 + 2,276 and v35 → v38 = 0 on all 32 items. Series-output law exact again, still
unwired (OQ-SERIESREAL).

### 0zc. The twelve open items of 2026-10-20 — CLOSED

Listed by the owner 2026-10-20 ("i want all these closed and resolved"); each checked against
the code and the data, not the earlier notes.

| item | state |
|---|---|
| MAH / MSO at 60 a rung | **Wired**: `logic_instructions.weights` MAH 60, MSO 60 (their real two-operand shape). |
| Rebuild INSTRUCTION_COVERAGE from current real data | **Done** for the real data in this checkout: a section on the ten counted real safety-controller programs (21,539 standard rungs, 136,996 native instructions, one unweighted occurrence, an undeclared AOI). The seventeen standard exports are not in this checkout; their tables stand as last regenerated. |
| The real alias tag cost, 56 + 8 × floor(len / 8) | **Wired, KNOWN** (`alias_overhead`), the same law as a controller-scope safety tag's standard name entry. |
| OQ-AXISDEEP's composite case | **Closed without code** (RESOLVED_QUESTIONS): round 5's 24 captured files with 1 to 5 axes each read the plant's own +1,786..+1,794, so every axis tag prices at zero residual. |
| The per-task overhead finding | **Documented** (MEMORY_MODEL, "Task, program and routine shell — KNOWN"): `task_extra` 700 exact at 2, 3 and 6 tasks; the +24 at four tasks is name rounding (OQ-TASKNAMEROUND); the old −1,472 a task is superseded. |
| Indirect addressing and cross-program references | **Documented** (MEMORY_MODEL, "Indirect addressing — WIRED", "Cross-program references": −16 a rung a further program, no formula change). |
| The MAM / MAJ / MAS / MRP build failures | **Flagged** (OPEN_BUILD_ERRORS, "Motion instructions need their full parameter list": MAM 20 operands, MAJ 17, MAS 9, MRP 5; RESOLVED OQ-MAMFAMILY-BUILDFAIL). |
| A full sweep for unprocessed captures | **Done for everything that can be priced without a full regeneration**: the 497 batch files on disk and the 40 local ones, and the module families regenerated in the scratchpad (251 clean captures, plus 45 composite). It found two: the Kinetix with-axis terms (D012 / S086, wired) and the 34 `rack_5069_*` captures, never re-priced under the module law (wired, OQ-MODREPEAT). The other deleted families need a corpus-wide regeneration, which waits on the owner's approval. |
| An honest assessment, and commit / push | Below; pushed once the full suite passed. |
| CROUT as a safety instruction | **Done**: Safety family, 0 standard, its rung priced in the safety partition (492); 43 real uses in the safety routines of the ten counted programs, none in the seventeen standard ones. |
| MAPC's real use | **126 calls, 0.10% of real instructions**, priced exact. |
| Twenty more STRING tests | **Built**: `strx_*`, 21 files (OQ-STRSHAPE, TASKS 0zb). |

**The assessment, 2026-10-20.** The standard engine on the seventeen standard-processor
programs is where it was: mean 0.97%, worst 2.57%, the stopping rule not met on the max, and
nothing this session could be scored against them (they are not in this checkout). On the ten
real safety-controller programs the standard figure is mean 1.58%, worst −3.64%; what is left
is not safety content — about 72 bytes an ST line on three programs, and the module and AOI
BOOL terms on two — and batch A measures each. The safety figure is still 1.5% to 44% low,
every gap a device type with a file in batch A or round 5, apart from an encoded safety AOI
that stays a minimum. Roughly: the measuring is done and the machinery to wire it is built;
what remains is two captures, their reconciliation, and whatever batch A shows the
mechanisms named here do not explain. The risk sits in three places: the ST shapes may
explain only part of the −72 a line; the module law has never been read on the realism
floor (every round-2 `modrep_*` file is a blind prediction); and packed 5069 cards' type
sharing is untested until `safe_io6_5069_*` reads.

### 0zd. Safety batch B, the last of 2 — BUILT 2026-10-22 (36 files), awaiting conversion and capture; the four Studio variants are the owner's (OQ-SAFETYLOGICIO, OQ-SAFETYPARTITION, OQ-STRSHAPE, OQ-MODREPEAT)

**Built 2026-10-22** (owner's go-ahead the same day): `gen_safety_round7.py` (26 files: Part 2
as revised below plus no-call controls for each AOI family, a fourth mixed-rung file and Part
4's one missing file), the two `safe_io6_5069_*` rebuilt by `gen_safety_round6`, and the four
STRING files rebuilt as `strx_*_r2` (`gen_string_shapes --only`; the first build's rows keep
their suspect readings, and the capture tool skips a sample id already read), and four `strm_*`
(`gen_string_members.py`) to say which string member a UDT array pays 4 more for (OQ-STRSHAPE). Every file
passed lint and the realism floor; the two drive files passed `check_proven_blocks.py` (0
unproven) and go through `samples/generated/safety/` by the 2026-10-19 exception.

**Predicted before any reading** (engine of 2026-10-22; each is the reading if the candidate
costs nothing):

| file | safety | what a different reading means |
|---|---:|---|
| `safe_aoiarg_a8_inst20` | 4,866 | instance block of a 10-BOOL AOI (unpacked; packed reads less) |
| `safe_aoiarg_a8tag_5` / `_20` | 6,934 / 12,394 | slope 364 a call if the +44 is per call; 496 if 22 an operand |
| `safe_aoiarg_p16_inst20` / `_call20` | 5,302 / 9,710 | per-call 207 (as SafeAoiA's 208) unless a parameter not passed costs |
| `safe_aoiarg_a8mod_ctl` / `_20` | 9,583 / 17,111 | the calls 7,528, as on tags, unless a module-member operand costs more |
| `safe_aoitmr_def` / `_inst20` | 2,498 / 6,498 | timers in a safety AOI; the instances 200 each unpacked, ~152 packed |
| `safe_par_local50` | 6,210 | the control |
| `safe_par_public50` / `_output50` / `_input50` | 6,210 each | each usage's own cost |
| `safe_par_aoiout20` | 6,498 | an Output AOI parameter (~300 each would explain RS-17) |
| `safe_desc_ctl50_l50` / `_l200` | 3,010 each | +10.8 KB / +43 KB at 4.3 a character |
| `safe_desc_prg50_l200` | 6,210 | the same at program scope |
| `safe_dcs_chain5x4` | 13,794 | a chained DCS costs what one alone does |
| `safe_rtn_idle_dcs20` | 14,074 | content of an uncalled routine compiled (less if not) |
| `safe_op_ctl_100` / `safe_op_slot_100` | 8,715 / 7,915 | a slot-path operand charged nothing; 8,715 if it costs a program BOOL's 8 |
| `safe_mix_ctl` / `_50` / `_100` / `_100_cmt` | 5,922 / 12,342 / 18,346 / 18,346 | ~4 a rung over the engine reproduces the real programs' generic residual |
| `safe_base_5069l320_v32` | 1,410 (standard 853,762) | standard: the v32 delta on a 5069 plant (the 1756-L81ES plant read +11,256) |
| `safe_io6_5069_ob16_1` / `_mix_2_2` | standard 846,574 / 850,844 | OQ-MODREPEAT's packed 5069 cards |
| `strx_equ_elem_r2` … `strx_neq_member_r2` | standard 1,256,194 (`_vidx` 1,332,994) | OQ-STRSHAPE's STRING EQU / NEQ operands |
| `strm_s2_400` / `_c2_400` / `_sc_400` / `_sd_400` | standard 911,482 / 877,882 / 895,482 / 879,482 (plant −1,794 under each) | +1,600 on `s2` alone: a STRING member is 88; +3,200 on `c2` and +1,600 on `sc`: the custom string is 48 (OQ-STRSHAPE, the three programs' 2,744 to 12,677 nested STRINGs) |


**Owner's direction 2026-10-22:** close the safety work first; the ST / FBD / SFC instruction
work (0ze) waits for it. Batch A's readings left the safety figure on RS-02 / RS-03 / RS-17
at −5.6% / −8.3% / −7.3%, outside the owner's tolerance, and −1.0% to −1.8% on the eight
other programs (OPEN_QUESTIONS Section 8).

**Revised 2026-10-22 after a census of every real safety program.** The first version of
this spec aimed most of its files at module-tag operands in safety logic. The other programs
refute that: 1.4 bytes an operand, 5 to 8 at most (Section 8). What is left is content only
these three programs carry and nothing has measured. Each candidate gets its own files, and
each file states what it reads under each candidate, so one capture decides.

**Part 1 — Studio-made variants of RS-17** (the owner's work in Logix Designer; RS-17 is
unlocked; each exported to `samples/local/`, never committed, with both Capacity readings).
Cumulative:

| variant | change | what its reading prices |
|---|---|---|
| V1 | delete the 15 rungs of the AxisSTO call routine (29 calls; the routine stays) | the calls with eight operands (candidate 1): 10,572 priced; ~3.8 KB more if the safety call extra is per operand |
| V2 | V1 + the 29 AxisSTO instances (`Usage="Output"`) and the definition | the instances as Output parameters and the definition (candidates 2, 6) |
| V3 | V2 + clear the description of every safety tag (94) | descriptions (candidate 3): 0, or ~14 KB at 4.3 a character |
| V4 | V3 + set the remaining 59 safety program parameters to `Usage="Local"` | Public parameters in a safety program (candidate 2) |

V3 and V4 only if practical in Studio; Part 2's C and D answer the same questions.

Predicted for each edit before any reading (safety figure, from the engine's 182,826 for RS-17
against its reading of 197,262): **V1** the engine drops 10,836 (the 29 calls 10,572 and the
264 a file that calls an AOI pays); if the safety call extra is 22 an operand the reading drops
~14,700. **V2** the engine drops a further 7,316 (29 instances 6,168, the definition's 800 and
its logic 348); packed instances drop ~1,400 less; an Output AOI parameter at ~300 drops
~8,700 more. **V3** the engine drops 0; at 4.3 a description character ~14,000. **V4** the
engine drops 0; each Public parameter's own cost × 59.

**Part 2 — isolation files**, 1756-L81ES v35 on the realism plant with the safety task, AOIs
of the project's own design (not AxisSTO's text):

| file(s) | content | control | reads, by candidate |
|---|---|---|---|
| A1 `safe_aoiarg_a8tag_5`, A2 `_a8tag_20` | an AOI with 8 Required BOOL parameters (6 in, 2 out), 20 program instances, 5 / 20 calls, operands on safety program BOOLs; a 2198-D012-ERS3 with integrated safety present (proven block) | each other (the slope) | per-call slope 364 if the +44 is per call; 496 if 22 an operand |
| A3 `safe_aoiarg_a8mod_20` | A2 with five operands the drive's `SI` members and two its `SO` members | A2 | a module-member operand's own cost in a call |
| A4 `safe_aoiarg_p16a2_20` | an AOI with 16 parameters, 2 Required, 20 instances, 20 calls | `safe_aoi_call_20` | per parameter or per operand |
| B1 `safe_aoitmr_def` | a safety AOI with 14 BOOL and 2 DINT parameters, an ONS and four TIMER locals, six rungs of TON / TOF / ONS / MOV / XIC / OTE | `safe_n00` | timers inside a safety AOI's definition |
| B2 `safe_aoitmr_inst20` | B1 + 20 program-scope instances, no calls | B1 | the instance block: 136 unpacked, 88 packed (candidate 6) |
| C1 `safe_par_local50` | 50 safety program BOOLs, `Usage` absent | `safe_n00` | the control |
| C2, C3, C4 `safe_par_public50`, `_output50`, `_input50` | C1's 50 as Public / Output / Input | C1 | each usage's own cost (candidate 2); Public 0 in standard memory |
| C5 `safe_par_aoiout20` | B2's 20 instances as `Usage="Output"` | B2 | an AOI-typed Output parameter (~300 if it carries RS-17 alone) |
| D1, D2 `safe_desc_ctl50_l50`, `_l200` | 50 controller-scope safety BOOLs, each with a 50 / 200-character description | `safe_tag_bool_50` | 0 if free; +10.8 KB / +43 KB at 4.3 a character (candidate 3) |
| D3 `safe_desc_prg50_l200` | C1's 50 with 200-character descriptions | C1 | the same at program scope |
| E1 `safe_dcs_chain5x4` | the 20 DCS of `safe_dcs_20` as 4 rungs of 5 chained, nothing else | `safe_dcs_20` | a chained DCS (candidate 4) |
| F1 `safe_rtn_idle_dcs20` | `safe_dcs_20`'s 20 rungs in a safety routine nothing calls | `safe_dcs_20` + the routine shell | content of an uncalled routine (candidate 5) |
| G1, G2 `safe_op_ctl_100`, `safe_op_slot_100` | 100 rungs `XIC(SfBit[i]) OTE(SfOut[i])` / `XIC(Adapter:1:I.Pt0nData) OTE(SfOut[i])`, a 1734-IB8S/B present in both | each other | confirms ~1.4 an operand (the refuted lead) |

**Part 3 — rebuilds of files that never reached a clean reading** (generators fixed, lint
refuses the defects): `safe_io6_5069_ob16_1` and `safe_io6_5069_mix_2_2` (the 5069-OB16/B
ConfigID; OQ-MODREPEAT's packed-card question); `strx_equ_elem`, `strx_equ_member`,
`strx_equ_vidx`, `strx_neq_member` (a BOOL destination; 2,424 real STRING EQU operands are
members behind an index). **Dropped, not rebuilt:** the four `stshape_aoi_*` (AOI-internal
ST is about 80 statements a real program, +4 each at most — under the floor) and
`safe_sil2_5069l320s3_n00` (it was only the SIL3 files' control, and those read exact
without it; the conversion cause stays unknown unless the owner sends its Studio
error-log line).

**Part 4 — the v32 baseline on content** (firmware-matrix exemption: firmware is the
variable): the realism plant on a 5069-L320ERMS2 at v32 and at v35, no safety content,
2 files. RS-06 / RS-09 (v32) read +1.65% / +1.66% standard, about the 11,240 v32 delta that
was read off bare files; if the plant at v32 reads 11,240 more than at v35 the delta is right
and the lead dies, otherwise the delta scales with content.

**Size:** 4 Studio variants (V3 / V4 if practical) and 26 generated files (18 isolation + 6
rebuilt + 2). A1 to A3 carry the drive from the local template (`gen_safety_io.py --local`, the
2026-10-19 exception route); files with a drive or a 1734 safety card are checked against
zero-error captures (`scripts/check_proven_blocks.py`) before hand-over.

**Not in batch B:** the generic −1.0% to −1.8% on the eight other programs (152 + 4.08 a
safety rung, or 54 + 42 a device + 0.58 a bit instruction; no single mechanism, inside a few
percent). **Deferred, under the floor on the programs in this checkout** (re-check on the
seventeen before testing): a STRING member in a UDT array (4 an element, OQ-STRSHAPE; 0 to
500 such elements a real safety program); a further 1734-AENTR/C adapter (470 to 830 over, 3
to 5 a program, OQ-MODREPEAT).

### 0ze. ST, FBD and SFC instructions and data types — QUEUED after 0zd (owner, 2026-10-22)

The owner supplied the Logix 5000 language manuals for Sequential Function Charts,
Structured Text and Function Block Diagram (chat-only, never in the repository) for the
concepts. Not started: the safety work closes first.

**Where the engine stands, per language (2026-10-22):**

| | data (backing tags) | logic |
|---|---|---|
| ST | every predefined type the real set uses | statement shapes exact (OQ-STSHAPE, 39 files); instruction calls through the ladder weight table (four ST/RLL pairs, identical but for the routine); not measured: CASE, WHILE / REPEAT, non-retentive assignment, functions inside expressions, the ST-only blocks (TONR / TOFR / RTOR, CTUD, OSRI / OSFI) |
| FBD | 22 FBD / SFC structures probed exact (OQ-FBDSFC, `predefprobe_*`) | **priced at zero**; `coverage.py` flags it |
| SFC | SFC_STEP / SFC_ACTION / SFC_STOP probed exact | **priced at zero**; `coverage.py` flags it |

RS-01 (7 SFC routines, 272 steps, FBD sheets) reads −8.2% standard, the largest standard
error in the safety set; FBD and SFC logic is the likely cause and is why it is not counted.

**Method, in order:**

1. Inventory the real programs (read-only parse): routines by language, ST statements by
   construct, ST / FBD calls by mnemonic, FBD blocks, wires and sheets, SFC steps,
   transitions, actions, branches and stops. The floor rule (0.5% of real instructions)
   decides what gets files; a construct absent from the real set waits.
2. One Studio-made seed export per family, from the owner: each construct in valid form, so
   lint carries every element's required attributes. An FBD sheet or SFC chart written from
   memory is a build failure waiting to happen (as the 2198 blocks were).
3. Count sweeps per construct as for ladder and ST (control, 1, n, 2n), solved together.
4. For the long tail, a structural law, as the safety device law did for devices: an
   unmeasured instruction priced from its operand count and types and its backing tag,
   fitted on the measured ones and checked leave-one-out. An unseen predefined type sized
   from the export's own L5K data, one DINT per value, as the FBD / SFC structures were.

### 0zb. Safety batch A of 2 — CAPTURED 2026-10-21 and WIRED (OQ-STSHAPE, OQ-MODREPEAT, OQ-STRSHAPE, OQ-AOIBOOLINST, OQ-SAFETYPARTITION)

**Captured 2026-10-21, wired the same day.** 217 readings; 8 with build errors (four `stshape_aoi_*`, four `strx_equ` / `_neq`), 3 never converted, 2 recaptured on the retry of 2026-10-21. Closed OQ-AOIBOOLINST (the scalar AOI law, KNOWN; RESOLVED_QUESTIONS). Wired: 12 safety device types and the device law for any other; produced / consumed safety tags; the SIL3 partner and a peer controller; the ST shapes (39 files exact); nine module repeat rates, the 5069-only prefix-less rule and the per-channel configuration term. Standard figure on the ten counted real safety programs **mean 1.58% → 1.34%, worst −3.64% → −2.45%**; safety figure on nine −1.0% to −1.8%, on RS-02 / RS-03 / RS-17 −5.6% / −8.3% / −7.3% (0zd). The seventeen standard programs are not re-scored (CLAUDE.md).



**Owner's direction 2026-10-20:** two further safety test generations and nothing after
them; the goal is the **standard** figure on programs that carry safety, and the safety
figure within a few percent ("over 10% I'd complain about"). Batch A is everything either
figure still needs a measurement for; batch B is only the follow-up its readings leave.
Generated on the owner's instruction ("I want all tests generated now"), and the module
law made general on the owner's instruction ("the logic needs to be able to handle any
I/O module used by anyone any number of times").

**The standard figure on the ten 1756 / 5069 safety programs** (engine of 2026-10-20,
prediction minus reading; RS-01 not counted, RS-11..16 dead architecture):

| label | error | bytes | what carries it |
|---|---:|---:|---|
| RS-08 | −3.64% | −57,199 | 756 executable ST lines: about −72 a line (OQ-STSHAPE) |
| RS-05 | −3.43% | −43,826 | 576 executable ST lines |
| RS-10 | −3.08% | −90,407 | 1,126 executable ST lines |
| RS-04u | −0.40% | −2,027 | the owner's unlocked re-export of RS-04, read 510,176 standard / 26,858 safety: 1,797 below the locked file, so source protection costs about that on the standard side. The locked RS-04 reads −2.59% (its protected AOI priced at a minimum) |
| RS-09 | +1.80% | +11,830 | repeated 1732E / EX260 modules; +2.52% before the module law |
| RS-06 | +1.78% | +11,650 | the same program on another controller; +2.32% before |
| RS-02 | −1.19% | −17,975 | four PowerFlex 525 sharing two types under the law (−6,496) and the D012 first-copy correction (+4,008); the encoded AxisSTO safety AOI |
| RS-03 / RS-17 | +0.23% / +0.24% | +6,577 / +6,721 | — |
| RS-07 | +0.04% | +461 | — |

**Mean 1.58%, worst −3.64%** with RS-04u in RS-04's place (1.80% with the locked file).
None of the large residuals is safety content. The three worst share one mechanism at one
rate, about 72 bytes per executable ST line; the ST law was measured on bare tags.

**Wired with the dive, no new constant beyond those named:** `/* */` comments stripped and
ST operands read whole through the routine's scope (RS-05 / RS-08 / RS-10 +1,764 / +4,241 /
+7,565; all 79 measured ST files unmoved); the 2198-D012 and -S086 with their axes from round
5 (D012 105 → 4,113 first copy, S086 3,849 / 2,865 as the S130; RS-02 / RS-03 / RS-17
+4,008 each); the module-type law (OQ-MODREPEAT, MEMORY_MODEL "A module-defined type is
defined once per project": 251 clean module captures |error| 214,854 → 131,710, the 34
`rack_5069_*` captures within ±0.35%, the 5069-AENTR 625, nine 5069 catalogs wired from
their own isolation captures); the SIL3 partner's ConfigID 100 (lint refuses a 1756-L8SP
without it); lint accepts every 2198 drive Major a real export carries and a 5069 bus at
its fixed size.

**The roster** (each generator's docstring has the exact statements and devices):

| files | varies | discriminates | against |
|---|---|---|---|
| `stshape_*`, 39 (`gen_st_shapes.py`), L81E v35 plant, one JSR-called ST routine | assignments (400): literal index, UDT member, scalar-UDT member, tag index on source / destination / both, tag index then member, index as a member path, index expression, REAL, REAL member, REAL multiply; BOOL destinations (400): literal, BOOL, NOT, AND, comparison; IF (200): BOOL, `> 5`, `= 5`, `>= tag`, AND, AND of three, OR, NOT, range, REAL, members, tag-indexed BOOL, two statements, ELSE, nested; COP (200) literal / tag index; FOR (50) literal bound, tag bound, loop-indexed body; `/* */` comments | each real ST shape's cost per statement | `stshape_n00`; `stshape_assign400` ties to captured `streal_assign400` |
| `stshape_aoi_*`, 4 | the same in an AOI's own ST Logic | whether AOI-internal ST costs what program ST does | `stshape_aoi_n00`, then the program twin |
| `modrep_*`, 36 (`gen_module_repeat.py`), L81E v35 plant | round 1: 1732E-IB16M12R/A, 1732E-OB16M12R/A, EX260-SEN1/A, EX260-SEN3/A, PowerFlex 525-EENET at 1 / 2 / 4. Round 2, one class each: 1756-IF8/A and 1756-OF8/B (chassis analog), 843E encoders (prefix-less types on an Ethernet device), PowerFlex 755-EENET at 1 / 2 / 4; 1 / 2 / 4 1734-IE2C/C in a sixth POINT rack; 5069-OB16/B one rack × 1, × 4, four racks × 1; ETHERNET-MODULE one, a second sharing its input type, a second sharing only its configuration type | the module-type law on the floor, every round-2 file a blind prediction | `realism_base_f25` |
| `strx_*`, 21 (`gen_string_shapes.py`), L81E v35 plant | 400 STRING calls each: EQU on elements / members / behind an index, NEQ, MOV member / behind an index, COP member, CONCAT member / custom-typed, INSERT, MID (and behind an index), DELETE, FIND, DTOS, STOD, RTOS, STOR, UPPER | STRING operands as real programs write them (OQ-STRSHAPE) | `strx_n00` |
| `aoibool_*`, 22 (`gen_aoi_bool_instances.py`), L81E v35 plant | one AOI with k BOOL locals, k + 4 bits = 4 / 32 / 33 / 59 / 64 / 65, each as the definition alone, 1 and 50 scalar instances; 25 at k = 55; a 50-element array at k = 55; the 55 BOOLs as Input parameters at 1 and 50 | the scalar AOI instance law with many BOOLs (OQ-AOIBOOLINST): packing, slot alignment, the definition | each other; def against `realism_base_f25` |
| `safe_io6_*`, `safe_sil3_*`, `safe_sil2_*`, `safe_pc6_*`, `safe_base_5069l310_v31*`, 27 (`gen_safety_round6.py`) | 1734-OB8S/A, one-connection IB8S/B, 442G at 1 / 2; SIL3 on the L81ES (with its partner) and the 5069-L320ERMS3, empty / content step / with safety cards; safety produced and consumed tags to a peer; the v31 5069-L310ERS2 base; 1 / 2 standard packed 5069-IB16/A, one OB16/B, two of each on the 5069-L330ERMS2 base | every safety shape of the ten counted programs not yet built, both partitions; the packed 5069 cards' type sharing | `safe_n00`, `safe_base_5069l330_v35`, round 5 |
| `safe_iol_*`, 13 local (`gen_safety_io.py --local`) | the generic robot safety interface and the FANUC R30iB Plus at 1 / 2; the revision-11 2198-D032 with network STO at 1 / 2 (no axes, `safe_iol_kinsafe_n` with the drive swapped); RS-04's packed 5069 cards at 1 / 2 on the v31 L310ERS2; the Kinetix drive at SIL3 at 1 / 2 and the 1756 safety pair at SIL3 | each remaining real safety device type, both partitions | `safe_n00`, `safe_iol_kinsafe_n`, `safe_base_5069l310_v31`, `safe_sil3_n00` |

Every file lint-clean on its floor; every safety block matches a compiled real shape
(module-sweep blocks completed with their catalog's ExtendedProperties, or templates from
compiled real exports with every name, address, safety network number, description and
comment replaced). The 13 local files stay in the git-ignored `samples/local/safety_io/`
and are handed over to go into `samples/generated/safety/` (CLAUDE.md exception); the four
robot files and the last nine were sent 2026-10-20. The revision-11 drive block has no
zero-error capture behind it (it is the variable); every other Kinetix block in the batch
matches a captured one, the SIL3 drives differing only in the safety network number.

**Predictions written down before capture** (standard, the engine of 2026-10-20; the
manifest holds every file's): `realism_base_f25` reads 840,384; `modrep_1756_of8_b`
847,594 / 848,498 / 850,306 (+904 a further OF8/B, 554 of overhead); `modrep_843e_mipxxbax_a`
845,241 / 847,888 / 853,182; `modrep_5069_ob16_b_r1x1` 846,715, `_r1x4` 852,355, `_r4x1`
854,230 (a further rack 625 more than a further card); `modrep_genem_n01` 844,234,
`_same_in` 845,866, `_diff` 846,178; `safe_io6_5069_mix_2_2` 850,708 against the base's
842,466.

OQ-AOIBOOLINST (TASKS 0p item 1, spec since 2026-10-04) is in the batch on the owner's
instruction: a scalar AOI instance prices each BOOL at 4 bytes where the instance-array
path packs them (OPEN_QUESTIONS section 3); packing accounts for 10,600 of `aoiint_n00`'s
12,198 and, unwired, moves RS-06 / RS-09 by −23,248 each and RS-02 / RS-03 / RS-17 by
−19,276 to −27,628. RS-06 / RS-09 now read +1.78% / +1.80% with the module law, so the
`aoibool_*` and `modrep_*` readings together settle which term carries them; neither is
wired further until both are read.

**Batch B** is specified only from batch A's readings: what is still outside 1% on the
ten programs, and on the safety figure outside a few percent, with a mechanism.

### 0za. Safety I/O, round 5 — 40 CAPTURED and WIRED 2026-10-19; 17 (1734 / 5069) to capture (OQ-SAFETYPARTITION)

**Captured and wired:** the 40 `safe_iol_*` files (1756 safety I/O, BNI00HN, Kinetix 5700 / 5300, PowerFlex 527) — safety exact per device by connection type, standard by catalog (MEMORY_MODEL, "Safety I/O"). Real safety programs moved from −18…−66% to −1.5…−44% on the safety figure; every remaining gap names unpriced 1734 cards, which the 17 `safe_io_*` files measure. **Next:** capture those 17 with batch A (TASKS 0zb), which builds what this list named: the one-connection IB8S (`Safety6`), the OB8S/A (`Safety3`), the 5069 packed cards, the revision-11 STO drive; the D012-with-axes term is wired (2026-10-20). `AB:1734_IB8S_Safety4` appears in no counted real program.
The BNI00HN runs on any EtherNet/IP network, not only a 5069's (owner, 2026-10-19); it was built on a 5069 only because the real ones sit there, and a 1756-L81ES copy would confirm the cost is the same.


**Owner's direction 2026-10-19: the safety I/O tests are generated here**, superseding the
"Studio seeds only" wait in 0x. `gen_safety_io.py` builds from the repository's own
module-sweep blocks, each completed with the `<ExtendedProperties>` every compiled export
of its catalog carries (profile ConfigID and CatNum); with it each block is structurally
identical to the compiled shape (the 1734-IB8S/B two-connection block to 19 real
instances). Nothing else is taken from a real export.

| files | discriminates | against |
|---|---|---|
| `safe_io_ib8s_1/2/4/8`, `safe_io_ob8s_1/2/4/8` (a further 1734-AENTR/C rack, sized to its cards) | a 1734 safety card's cost in each partition, and the first card's against the next | `safe_n00` and each other |
| `safe_io_ib8s1c_4` | the IB8S test-output connection (SafetyOutput) alone | `safe_io_ib8s_4` |
| `safe_io_mix_4_4` | additivity of IB8S and OB8S in one rack | the two sweeps |
| `safe_io_racks_2x2` | a second rack with its own safety network | `safe_io_ib8s_4` |
| `safe_io_5069_ib8s_1/2/4`, `safe_io_5069_obv8s_1/2/4` (5069-L330ERMS2 v35's own bus) | a 5069 safety card's cost | round 4's `safe_base_5069l330_v35` |

**Not built, and why:** the Kinetix 2198 safety drive (10 real programs, the largest
share), 1756-IB16S / OBV8S, the Balluff BNI00HN (an EDS-profile device whose data types are
named by its EDS revision) and the PowerFlex 527 have no block in this repository that is
proven or matches a compiled shape (the PowerFlex 527's every real instance also carries an
axis and a motion group). Building their templates from the real exports was refused by
the session's confidentiality guard; they need either one Studio-made export each (a
1756-L81ES v35 project with the device added, exported) or the owner's explicit permission
for templates derived from the real exports with every customer value replaced.

**Local-only families, 15 built 2026-10-19** (`gen_safety_io.py --local`): 1756-IB16S/A and 1756-OBV8S/A at 1 / 2 / 4 in the L81ES local chassis; a 2198-P208 and 1 / 2 / 4 2198-D032-ERS3 with integrated safety, each against the same drives without safety (`safe_iol_kinstd_*`, the proven drive block); the BNI00HN at 1 / 2 / 4 on a 5069-L330ERMS2's port 4. Their templates come from compiled real exports with every name, address, safety network number, description and comment replaced, so the templates and the files stay in the git-ignored `samples/local/` and move over chat (handed over 2026-10-19). Every derived block matches its compiled shape; the integrated-safety drive is the one block with no capture behind it yet (`check_proven_blocks.py`: 7 unproven, all of it). **25 more, same day:** the Kinetix 5700 safety drives D012 / D020 / D032 / D057 (rev 14) and S086 (rev 13) at 1 and 2 on the proven bus (2198-P208, its converter axis, the motion group, each drive's servo axes as real programs carry them), each against the same drives without safety (all proven blocks); the 2198-H008-ERS2 (Kinetix 5300) at 1 and 2 with its axis on a 5069-L330ERMS2 port 4; the PowerFlex 527 at 1 and 2 with its axis and a motion group; a 1756 IB16S + OBV8S pair. 40 local files in all, handed over 2026-10-19; the only blocks with no capture behind them are the 18 safety drives. Lint now holds only Kinetix 5700 bus drives to a bus supply and converter axis (`_KINETIX_BUS_DRIVE`): every real 2198-H008-ERS2 project has neither.

Found on the way and fixed: the module-sweep blocks had their `<ExtendedProperties>`
stripped when genericized, the same defect class as the 2198 ConfigID failures, and lint now
refuses a safety I/O card without its ConfigID (`safety_io_without_configid`; 0 hits on 18
real exports). Lint's `chassis_size_mismatch` wrongly held a 5069 controller's own bus to
its card count; real 5069 controllers run a fixed size per catalog.

### 0z. Real safety programs read 2026-10-19 — safety I/O is now the whole safety gap (OQ-SAFETYPARTITION)

16 of 17 read blind (OPEN_QUESTIONS, "Readings, 2026-10-19"). Standard on 1756 / 5069: mean
2.20%, worst −3.71% on ten; RS-01 −8.89% from 7 unsized SFC and 2 FBD routines. Safety: 18 to
66% low on every program, scaling with safety modules; a fitted per-module charge fails
leave-one-out (to −56%), so the Studio seeds of 0x item 1 are the next safety work, ranked:
Kinetix 2198 ERS3 drive (in 10 programs, about 5 KB each), 1734 IB8S/OB8S (12 programs), 5069
IB8S/OBV8S, 1756 IB16S/OBV8S, PowerFlex 527, BNI00HN. The signature and the lock cost 0 safety
(RS-03 = RS-17), so 0x's Studio-made lock variant drops to a check of the standard side
(at most about 144). RS-16 is dropped; RS-01's standard figure is not counted (SFC/FBD).

### 0y. Round 5 — SPEC ONLY, not generated; approval needed (OQ-SAFETYPARTITION, OQ-UDTMEMBERNAME, OQ-REALUNDER)

What round 4 left open that a generated file can answer, plus the two standard-engine
terms its twins exposed. Same platform and plant as rounds 2 to 4 unless stated: the
safety files 1756-L81ES v35 on the plant, the standard files 1756-L81E v35 on the plant.
Every file differences against an existing capture or a control in its own family.

| # | files | varies | held fixed | discriminates | against |
|---|---|---|---|---|---|
| 0 | `safe_aoi_call_60` (built, converted 2026-10-19, **no capture row**) | — | — | the safety AOI call law at a third count | `safe_aoi_inst_prog60` |
| 1 | `safe_lg_ctl2` (the program pool plus 20 scalar safety DINTs `LgSc00..19`), `safe_lg_movsc_20` (`MOV(LgSc{i},LgDb[{i}])`), `safe_lgc_movsc_20` (the same on 20 controller-scope scalar safety DINTs, with `safe_lgc_ctl2`) — 4 files | a scalar word operand in a safety routine | the round-3 pools and rung shape | 4 (as priced) or 8 (as in standard logic) for a scalar word operand in the safety partition | each its own `_ctl2` |
| 2 | `safe_sref3_ctl` (50 controller safety TIMERs `SRefT000..049`, a standard DINT[64]), `safe_sref3_acc_50` (`MOV(SRefT{i}.ACC,StdD[{i}])`) — 2 files | a member of a scalar safety structure read by standard logic | `safe_sref2_*`'s shape | 4 or 8 for a member operand, beside a bare scalar's 8 | `safe_sref3_ctl` |
| 3 | `udtpool_dint_n4_len{01,02,03,04,08,12}`, `udtpool_dint_n8_len{01,02,04,12}`, `udtpool_bool_n4_len{01,02,03,04,08,12}` — 16 files, one UDT definition each, no tags | member type, count and name length | the plant; an 8-character UDT name | the pool's form: `+1` a name (BOOL arm) or `len − 2` (DINT arm, safety UDTs), and whether a BOOL run carries its own term | `realism_base_f25` |
| 4 | `arrtag_dint64_len{04,08,12}`, `arrtag_dint{1,1000}_len08`, `arrtag_dint64x10_len08`, `arrtag_bool64_len08`, `arrtag_real64_len08` — 8 files, standard array tags | name length, dimension, type, count | the plant | whether +4 a standard array tag is per array, per name bucket, per size or per type | `realism_base_f25` |

30 new files and one recapture. Not here: safety I/O (Studio seeds, TASKS 0x item 1);
the signature and the lock (the Studio-made variant of `safe_n00` in 0x).

### 0x. Safety round 4 — DONE: 31 of 32 captured, wired 2026-10-19 (OQ-SAFETYPARTITION)

**Result:** zero errors, safety exact on all 28 safety files before any change. Tag
mapping costs nothing (0 to 200 pairs, both partitions); AOI instances at 5 / 60 and
calls at 5, the AOI parameter / local / rung variants, routine names to 40 characters and
ATAN2 / COP / FLL at 100 all exact; the safety base and content step identical on
5069-L330ERMS2 / L320ERMS2 v35 and 1756-L81ES v32 / v34. Wired: the 5069 safety shell
charged once (it was charged twice, 296 high, on every 5069 safety file with a safety
task, the real ones included), and a scalar safety DINT read by standard logic at 8. The
twins show the −16 / −32 UDT and +4 array residuals are the standard engine's, not
safety's (OQ-UDTMEMBERNAME reopened; OQ-REALUNDER). `safe_aoi_call_60` converted but has
no capture row (0y item 0).


**Built, asked for directly:** `gen_safety_round4.py`, 32 files in `samples/generated/safety/`,
lint clean, on the plant, each differenced in `safety_eval.py` (round 4): tag mapping at
0 / 1 / 10 / 50 / 200 pairs (`safe_map_*`, the `SafetyTagMap` form ` Std=Safety, ...`,
standard first, the standard tags `Class="Standard"` as in every real safety export); AOI instances and
calls at 5 and 60, AOIs with 6 and 12 parameters, 10 rungs without locals and 9 locals
with one rung; subroutines named with 16, 24 and 40 characters; ATAN2, COP and FLL at 100
rungs; a standard MOV of a scalar safety DINT; 1756-L81E twins of `safe_udt_s_def`,
`safe_udt_l_def` and `safe_sref_ctl` (against the captured L81E plant `realism_base_f25`);
and the safety base with one content step on 5069-L330ERMS2 and 5069-L320ERMS2 at v35 and
1756-L81ES at v34 and v32 (controller prefix `SafeBase`, exempt from the platform pin
because the platform is the variable). **Item 1 (safety I/O) waits on Studio seeds.**

**Checked against the real exports before handover** (OPEN_BUILD_ERRORS rule 7): four
defects fixed and the files rebuilt (5069-L320ERMS2 ProductCode 222; 1734-AENTR/C revision
6 below v35; the 5069 A1/A2 port pair; `Class="Standard"` on mapped tags), and lint now
refuses a module on a port its parent lacks. The v32 / v34 bases carry revision 6 adapters
where v35 carries 7; both have the same connection data types, so any difference in what
the adapter costs would sit inside that base's firmware delta.

**Item 3, signature and lock: a Studio-made variant, not a generated file.** The import
trial `safe_lock_trial` was withdrawn unbuilt: every real locked export (8 of 8) also
carries a safety signature, so SafetyLocked="true" without one has no compiled
precedent. Open the captured `safe_n00` in Logix Designer, read Capacity; generate the
safety signature, read Capacity; safety-lock, read Capacity; export after each step.
Three readings difference the signature and the lock directly.

Rounds 1 to 4 are wired; safety exact on all 299 captured safety files.

**Safety I/O reference (asked for 2026-10-18):** the real safety programs in
`samples/local/` hold most of item 1's families (1734 IB8S/OB8S in 10 programs, Kinetix
2198 H008-ERS/ERS2 and D0xx/S086/C4004-ERS3, 5069 IB8S/OBV8S, 1756 IB16S/OBV8S,
PowerFlex 527 STO, a FANUC robot, generic Ethernet and catalog-less devices). The
generators are to use them as the reference for each family's module shape instead of
waiting on a Studio seed per family. Doing so meets the rule that nothing derived from
customer content is committed: a generated module built from a real one carries that
module's structure into `samples/generated/`. The proposal: a reader that takes from
each real module only its catalog-defined structure (element and attribute layout,
connection and data-type shape, the catalog's own default configuration) and writes it
with every customer value replaced (module and tag names, addresses, safety network
numbers, signatures, descriptions, vendor text), checked by lint for any string from the
source file. **Decided 2026-10-18: Studio seeds only.** The rule stands as written: the
real files are read for which safety I/O families exist and how often (the ranking
above), never as a source of module XML; each family's shape comes from one Studio-made
export with both Capacity values, and the generators build from that. What is left is what every real
safety program carries and no file has measured, ranked by its weight in the 16 real
safety programs predicted blind (OPEN_QUESTIONS, OQ-SAFETYPARTITION). **Nothing here is
generated until it is approved; the first three need Studio-made seeds first.**

| # | item | real weight | seed first | then generate | discriminates |
|---|---|---|---|---|---|
| 1 | **Safety I/O** | all 17 programs, 2 to 25 safety modules | one Studio export per family (order by real use: 1734 IB8S/OB8S, Kinetix 2198-H008, 2198-D0xx-ERS3, 5069 IB8S/OBV8S, 1756 IB16S/OBV8S, PowerFlex 527, BNI00HN) with both Capacity values: 1734-AENTR + IB8S + OB8S; 5069-IB8S + OBV8S; 1756-IB16S + OBV8S; one Kinetix 2198 ERS3 axis; PowerFlex 527 STO; BNI00HN | per family 1, 2 and 4 modules on the L81ES plant, each against the plant alone (~18 files) | what a safety module and its connection cost in each partition |
| 2 | **Safety tag mapping** | 8 of 16 | one Studio-made mapping pair, exported, to fix the `SafetyTagMap` form | 0 / 10 / 50 / 200 pairs over the same tags (4 files) | cost per mapping pair, each partition |
| 3 | **Signature and locking** | 9 of 16 | one project read unsigned, signed, then locked, both values each time | none | whether either moves a reading |
| 4 | AOI calls and definitions | 2 of 16 (encoded, safety-locked) | none | calls at 5 / 20 / 60; AOIs with 2 / 6 / 12 parameters; 10 rungs with no locals and 9 locals with one rung (8 files) | the call's per-call and one-time split; whether the 800 moves with parameters; locals against rungs |
| 5 | Routine names | all | none | subroutines named with 16, 24 and 40 characters (3 files) | the routine-name law past two buckets |
| 6 | ATAN2, COP, FLL | COP/FLL in 2 | none | each at 100 rungs (3 files) | their corrections at a second count |
| 7 | Standard-side residuals | all | none | 1756-L81E twins of `safe_udt_s_def`, `safe_udt_l_def` and `safe_sref_ctl`; MOV from a scalar safety DINT in standard logic (4 files) | whether −16 / −32 and +4 are the safety controller's or the engine's; 8 or 4 for a scalar word |
| 8 | Other bases | 12 of 16 not L81ES v34/v35 | Studio File > New, both values: 5069-L330ERS2 v35, 1756-L81ES v32 | none | the safety base off the measured platform |

### 0w. Safety items logged for testing — 2026-10-18, after rounds 2 and 3 read (OQ-SAFETYPARTITION)

Asked for: each of these goes into a later round, once the logic and tag handling of
rounds 2 and 3 have read clean. None is specced yet. Each needs a Studio-made seed first,
because none of these shapes exists anywhere in the repository to build from.

| item | what to measure | seed needed |
|---|---|---|
| **Safety signature** | whether generating the safety task signature moves the standard or the safety reading, and by how much | one project exported and read before and after Generate Safety Signature, both Capacity values each time |
| **Safety locking** | whether a safety-locked project (`SafetyLocked="true"`) reads differently from the same project unlocked | the same project read unlocked and locked, both values each time, and its export while locked |
| **Safety tag mapping** | what each standard → safety mapping pair costs, in each partition, at several counts | one Studio-made mapping exported (the exact `SafetyTagMap` form), then generated count sweeps over the same tags unmapped and mapped |
| **Safety I/O** | what a CIP Safety module and its connection cost in each partition, per family | one Studio-made export per family with its Capacity values: 1734 POINT Guard I/O, 1756 safety I/O, 5069 Compact safety I/O, PointMax, FLEX 5000, and Balluff BNI00HN and other third-party CIP Safety devices. No safety device or safety AOI sample is on hand: the one Balluff file in `samples/local/` is a standard (Class="User") IO-Link master AOI, not safety |

**Order:** after rounds 2 and 3 (and the seven `safe_std_*_r2`) are read and wired; I/O
last, as asked. Signature and locking are two readings of one project each; tag mapping
and each I/O family become count sweeps once their seed fixes the XML.

### 0v. Safety round 3, logic — DONE: 78 captured, wired 2026-10-18 (OQ-SAFETYPARTITION, `safe_lg*` and `safe_aoi_*`)

Asked for directly: confidence in safety LOGIC and its handling before any I/O. Real
safety programs are mostly ordinary instructions in safety routines, and the engine
charges those their standard weight in the safety partition, ASSUMED. This round
measures every ordinary instruction Studio offers in a safety routine (the 58 in the
safety-routine instruction palette — the Studio scrap that holds every one, and nothing
outside it is ever used; lint refuses anything else — less the ones below), each alone, 20 rungs, on one
fixed pool of SafetyProgram tags held in full by every file, so each file differences
against `safe_lg_ctl` alone. Built by `gen_safety_round3.py` on the round-2 builder.

| group | files | varies | control | discriminates |
|---|---:|---|---|---|
| `safe_lg_ctl`, `safe_lgc_ctl` | 2 | nothing | `safe_n00` | the pools themselves (program and controller scope) |
| `safe_lg_<input>_20` | 15 | XIC, XIO, ONS, OSR, OSF, EQU, NEQ, GRT, GEQ, LES, LEQ, LIM, MEQ, CMP, AFI, each with its OTE (OSR, OSF alone) | `safe_lg_ctl` | each input instruction's safety cost, net of OTE |
| `safe_lg_<output>_20` | 30 | OTE, OTL, OTU, TON, TOF, RTO, RES, CTU, CTD, MOV, ADD, SUB, MUL, DIV, MOD, AND, OR, XOR, NEG, ABS, NOT, SQR, ATAN2, CPT, CLR, MVM, SWPB, COP, FLL, SIZE, alone | `safe_lg_ctl` | each output instruction's safety cost, against its standard weight |
| `safe_lg_mcr_20`, `safe_lg_jmplbl_20` | 2 | 10 MCR zones; 10 JMP/LBL pairs | `safe_lg_ctl` | program-control instructions |
| `safe_lg_<op>_20` | 11 | literal DINT and REAL sources, literal compare and add; DINT+REAL, DINT→REAL, INT→DINT; a tag-driven index on XIC and MOV; a timer's .DN; scalar BOOLs | `safe_lg_ctl` | whether the standard operand laws (OQ-LITREAL, OQ-MIXEDTYPE, OQ-INDIRECT) hold in safety |
| `safe_lgc_<x>_20` | 3 | XIC+OTE, MOV, ADD on controller-scope safety tags | `safe_lgc_ctl` | logic on controller-scope operands against program-scope |
| `safe_lg_<shape>_20` | 5 | four inputs in series; two- and three-leg branches; two outputs; a seal-in | `safe_lg_ctl` | rung composition: branch brackets and the series-output law in safety |
| `safe_lg_<x>_100` | 5 | OTE, XIO+OTE, MOV, EQU+OTE, TON at 100 rungs | `safe_lg_ctl` | linearity, beside the 20-rung files |
| `safe_aoi_*` | 5 | a Class="Safety" AOI (required BOOL in and out): definition alone; with 10 internal rungs; 20 instances in the safety program; the same and 20 calls; 20 instances at controller scope | `safe_n00`, then `safe_aoi_def` and `safe_aoi_inst_prog20` | which partition pays a safety AOI's definition, its internal logic, its instances at each scope and its call sites. **Real use confirmed 2026-10-18: one of the real safety programs carries a safety AOI.** Once that export is back in `samples/local/`, its AOI's XML form is checked against `safe_aoi_*` before they convert, and the program is predicted blind on both partitions before its Capacity is read |

Not in this round: FAL and FSC (their captured standard shape leaves operands as `?`,
which is not a shape to transplant), GSV, SSV, EVENT and TND. Every file's standard
reading is also a test: safety-routine logic is expected to cost 0 standard.

### 0u. Safety round 2 — DONE: 74 captured, wired 2026-10-18 (OQ-SAFETYPARTITION, `safe_*`)

Asked for directly: enough rounds to be confident in whole safety programs, safety tags
at controller and program scope alike. Every file is 1756-L81ES v35 on the realism plant,
built by `gen_safety_round2.py` with the round-1 builder, so each one differences against
`safe_n00` (captured) or a control in its own family. Round 1's 112 files are not touched.

| group | files | varies | control | discriminates |
|---|---:|---|---|---|
| `safe_ptag_dint_50_len<k>` | 5 | program-scope name length 4/8/16/24/40 (12 is `safe_tag_dint_50_prog`) | `safe_n00` | whether a safety-program tag's name entry follows 56 + 8 × floor(len / 8) in the safety partition |
| `safe_arr_<shape>_<ctl\|prog>` | 20 | DINT[2], DINT[3], DINT[64], INT[3], SINT[10], REAL[10], BOOL[64], BOOL[96], DINT[4,4], TIMER[4]; 20 tags each, both scopes | `safe_n00` | the data block 8 × ceil((28 + data) / 8) on arrays; that a controller array still pays only its name entry standard |
| `safe_struct_<type>_<ctl\|prog>` | 8 | TIMER, COUNTER, CONTROL, LINT; 20 tags, both scopes | `safe_n00` | the data block on the ordinary structures and LINT, and whether Studio accepts CONTROL and LINT as safety types |
| `safe_udt_<s\|l>_<def\|ctl20\|prog20>` | 6 | a 12-byte and a 40-byte safety UDT: definition alone, then 20 tags at each scope | `safe_n00`, then its `_def` | which partition pays a UDT definition used by safety tags; the data block on a UDT |
| `safe_alias_*` | 5 | 20 aliases: controller → controller, program → controller, program → program | the 20 targets alone, each scope | what a safety alias costs, and where |
| `safe_rtn_<jsr\|idle>_<n>` | 6 | 1/2/5/10 JSR-called safety subroutines; 1/5 uncalled ones | `safe_n00` | a safety routine's shell in each partition, apart from its JSR rung |
| `safe_prg_*` | 5 | 2/3/5 safety programs; a 40-character second name; 50 tags in the second program | `safe_n00`, `safe_prg_2` | a safety program's shell and name in each partition; program-scope tags in any safety program |
| `safe_<estop\|rin>_<op\|b>*_20` | 10 | ESTOP inputs as program BOOLs, controller safety BOOLs, BOOL-array elements; ESTOP and RIN backing tags at controller scope; each with its tags-only file | its tags-only file | whether a safety rung's cost depends on where its operands and backing tag live |
| `safe_sref_*` | 5 | 50 standard rungs: two safety operands, a scalar safety BOOL, MOV from a safety DINT, and the all-standard twin | `safe_sref_ctl` | the +8 per safety operand: per operand or per rung, scalar or array, BOOL or DINT, against the engine's own standard rung |
| `safe_comp_<1..4>` | 4 | whole safety programs: two to five programs, subroutines, ESTOP/RIN/ROUT/LC and drive safety, tags at both scopes, arrays, UDTs, standard logic reading safety status | none (blind) | **blind test**: both partitions predicted and written down before capture |

**Built 2026-10-18:** 74 files, lint clean, `samples/generated/safety/`. **Blind
predictions, written before any reading** (engine of 2026-10-18; the standard figures
include the realism plant's −1,794, so read the standard residual net of it):

| file | standard predicted | safety predicted |
|---|---:|---:|
| `safe_comp_1` | 844,930 | 12,322 |
| `safe_comp_2` | 847,022 | 16,778 |
| `safe_comp_3` | 845,302 | 53,814 |
| `safe_comp_4` | 842,474 | 15,994 |

Known gaps already inside those predictions: an extra safety routine or program's shell
is charged nothing (comp 1, 2, 3 and 4 have them) and an alias nothing in the safety
partition (comp 2).

Not in this round: ordinary instructions inside a safety routine (the seven
`safe_std_*_r2`, already built, convert with this round); safety I/O modules (no Studio
block exists for one — a Studio-made seed with a 1734-AENTR, one IB8S and one OB8S is
needed first).

### 0t. While the safety capture runs — ranked 2026-10-17

1. **README** — DONE: the quick start now leads with `Setup.cmd` for Windows.
2. **Processor/firmware of the `UNKNOWN` capture rows** — NO ACTION: their window titles
   show 1,913 of 2,043 are 1756-L81E at v35, and the other 130 are exactly the platform
   batches (L9/v38 side by side: 74 L81E v38 and 50 L9; five 5069 platform-equivalence
   files; the one L83E Kinetix rack), each identifiable from its window title.
3. **OQ-AOIBOOLINST**: built in 0zb (`aoibool_*`, 22 files), 2026-10-20.

Blocked: **OQ-REALUNDER** needs the seventeen real exports back in `samples/local/` (the
cloud container was reset). The safety-partition estimate and TASKS 2 are DONE (0s).

### 0s. Safety partition — 112 CAPTURED AND WIRED 2026-10-18; seven `_r2` to convert (OQ-SAFETYPARTITION)

**Captured 2026-10-18:** all 112 converted files, zero build errors, standard and safety
reading on every row. Every sweep exact; the laws are in MEMORY_MODEL ("Safety memory is
a separate partition") and wired: `sizing/report.py` takes safety content out of the
standard total (TASKS 2), `sizing/safety.py` prices the safety partition, and the CLI and
UI show it. Against the captures: standard −1,794 on 108 files (the realism plant's own
constant) and −1,790 on the four `safe_ref_*`; safety exact on all 112. Both Studio seeds
exact on both partitions. `python scripts/safety_eval.py --engine` reproduces it.

**Next:** convert and capture the seven `safe_std_*_r2` (ordinary instructions in a
safety routine, the one wired term still ASSUMED), then difference them against
`safe_std_ctl_r2`. **No further batch is specced:** the shapes still open (OQ, "Still
open") have to be ranked on the real safety exports, which are not in `samples/local/`.

**The owner lifted every restriction for this phase**: no noise-floor gate (every
safety-routine instruction is measured, not only the four real programs use) and no
file-size limit. The batch was asked for directly; no separate approval is pending.

**Built:** `python -m sample_gen.gen_safety_partition`, 119 files in
`samples/generated/safety/`, manifest rows `safe_*`. 1756-L81ES at v35, SIL2/PLd, File >
New's SafetyTask/SafetyProgram/MainRoutine, realism floor. Every call shape is Studio's
(`docs/SAFETY_INSTRUCTIONS.md`), every safety tag carries Studio's data block for its
type (`samples/proven_blocks.json`, `safety_tags`), and lint pins the SafePart
controller prefix to exactly that platform, refuses a safety instruction outside a
safety program, and checks every safety call's operand count.

| group | files | varies | held | discriminates |
|---|---:|---|---|---|
| control `safe_n00` | 1 | nothing | plant + empty safety shell | safety base on the plant (v34 seed: 1,394); standard control |
| `safe_tag_<type>_<n>` | 9 | BOOL, DINT ×10/50/200; REAL, INT, SINT ×50 | controller scope, Class=Safety, no logic | per-tag cost in each partition; the standard-side 56-per-tag hypothesis |
| `safe_tag_dint_50_len<k>` | 3 | name length 4/20/40 (12 is the ×50 file) | count | whether the standard side follows 56 + 8 × floor(len / 8) |
| `safe_tag_dint_50_prog` | 1 | scope | count, type | program scope against controller scope |
| `safe_<mn>_tags_<n>` / `safe_<mn>_<n>` | 94 | count; tags alone vs tags + one rung each | program scope, Studio's call shape | instruction cost per partition. ESTOP, RIN, ROUT, LC ×10/50/200; the other 35 ×20 |
| `safe_std_ctl_r2`, `safe_std_<x>_r2` | 7 | XIC+OTE ×10/50/200, TON ×50, MOV ×50, ATAN2 ×20 | safety arrays in full in all | whether an ordinary rung in the safety routine costs its standard weight, and where |
| `safe_ref_ctl`, `safe_ref_<n>` | 4 | XIC(safety)OTE(standard) ×10/50/200 in the standard MainRoutine | both arrays | standard cost of reading a safety tag |

**Rebuilt 2026-10-17** after every file failed conversion with "required property 'port' was missing": `build_l5x` had no ProductCode for 1756-L81ES and gave the Local module the L81E's 164 (GuardLogix 5580's is 211). The wrapper now refuses a 1756 catalog it has no code for, and lint (`local_module_product_code`) refuses a mismatched Local module. Reconvert the whole folder.

**`safe_std_*` rebuilt 2026-10-18**: all seven failed conversion on the safety BOOL array `SIn`, rejected as an invalid tag name because it is the SIN function. The arrays are now `SfIn`, `SfOut`, `SfTmr`, `SfDa`, `SfDb`, `SfRa`, `SfRb`, `SfRc`, and `validate_logix_name` and lint refuse any name equal to an expression function or operator. The seven failed files are abandoned (deleted with their manifest rows; none was captured) and rebuilt as `safe_std_*_r2`, built alone with `--only '^safe_std_'` so the 112 captured files keep their hashes.

**Capture:** convert as usual, then capture a few first with `-Limit 3` and check that
`safety_bytes` fills and the error counts are 0 before running the rest. The updated
`logix_build_capture.ahk` and `batch_memory_capture.ps1` must both be in use: an older
AHK writes no `safety_value`, and every safety file would come back `SAFETY NOT READ`.

**After capture:** each sweep differenced against its control in both columns, each
instruction row against its tags row, solved per partition; then a safety-partition
estimate in the engine and the standard side corrected (TASKS 2).

### 0r. Repository cleanup, 2026-10-12 — DONE

Tracked tree 5.34 GB → 17.6 MB. Removed: every generated `.L5X` (4,177 files, 5.3 GB; all
captured, every number in manifest/captures, every finding in the docs, every generator kept),
the 64 Rockwell sample programs in `samples/samplePrograms/` (used by nothing) and the Rockwell
manual PDF. Kept and repointed: proven Kinetix and module blocks → `samples/proven_blocks.json`
(`check_proven_blocks.py`, `gen_l9_v38.py`, `build_demo_project.py`); tests rebuild the batches
they need from the generators (`tests/conftest.py`), and the engine-vs-controller law tests check
each rebuilt file against the captured file's hash first (all 27 identical, date stamps aside).
Real set unchanged at 0.97% / 2.57%. A fresh `git clone` still downloads the old history until
the history reset (0q) is done; Download ZIP gets the 18 MB tree.

### 0q. History reset — PROPOSED, awaiting the owner's decision

Customer program names reached pushed history (one TASKS.md commit and one generator comment;
both removed from the tree). A force-push alone does not purge them: GitHub keeps orphaned commits
reachable by SHA, closed PRs #1–#3 pin refs, and four `james-*` branches carry the old history.
Plan: one fresh root commit of the current tree (scanned 2026-10-10: zero customer names in 4,633
text files); the Rockwell manual PDF it mentioned was removed in the 2026-10-12 cleanup, with the checkpoint references dropped from CLAUDE.md (commit `172f581` will not exist);
the owner deletes and recreates the GitHub repository, then the one commit is pushed. Before
re-cloning, the owner moves `samples/local/` (real exports, `aliases.csv` — gitignored, on the
capture machine only) out of the old clone. Nothing in the reasoning trail is lost: the docs are
the record by design; captures, manifest and convert log live in the tree.

### 0p. The 92-file capture, 2026-10-04 — DONE; next batch SPEC below (ask before generating)

**Real set 1.27% → 0.97% mean, 3.08% → 2.57% worst, 10/17 inside 1%, 15/17 inside 2%.** Mean
under 1% for the first time; the stopping rule still fails on the max (export 27 2.57%, export 16
2.23%). Nine questions closed (RESOLVED_QUESTIONS, top): AOICOMPLEX, AOIROUTINES (opened and closed
on the same evidence), AOIINTERNAL, AOILITARG, MOTIONLIT, BLOCKSTR, SMALLINSTR, PUBLICTAG, STREAL. Wired, by mean gain:
InOut operands in AOI logic (+8 per instruction, −0.146 pp), AOI REAL arguments (+52 / +4,
−0.062), AOI scan-mode routines (+268 each, −0.027), nested AOI call (+264 per calling definition),
motion literal law on MAJ/MAPC/MCCP/MAG with their weights corrected (−0.008), FLL integer
literal into REAL (+52, +0.003). Pinned by `tests/test_aoi_and_motion_laws.py`.

Suspect row: `aoicx_full_prog` (1 build error: a GSV attribute the configured axis lacks), used only
as reported in OQ-AOICOMPLEX.

**Next batch — SPEC, not built:**

1. **OQ-AOIBOOLINST (8 files) — superseded by TASKS 0zb's 22 `aoibool_*`, built 2026-10-20.** Split `aoiint_n00`'s −12,198 between instance data and definition.
   One AOI with 3 inputs + 1 output and k BOOL locals, k = 0, 16, 32, 55, each at 1 and 50 instances,
   no logic, no axis, realism floor. Instance step (50 − 1) / 49 per k gives the per-instance figure
   against the engine's (320 at k = 55); the 1-instance files give the definition. Differences
   against each other only. Real exposure: 672 instances of 40–47-BOOL AOIs, 11 of 64+.
2. **Studio transplants (the user's).** Unchanged from 0o item 2: export 27's untransplanted
   programs; exports 16 and 06's three largest programs one at a time. With AOI logic now priced
   much closer, a transplant's residual points at program logic alone.
3. **AOI math block (+128) and second definition (−368), optional (4 files).** `aoicx_math` split
   into its TON, CPT and REAL-math-with-float-literal rungs; `aoicx_full_two` with the second
   definition's instances and servo tags but its Logic at one rung. Small; build only if 1 and 2
   leave room.

### 0o. Further tests — BUILT 2026-10-02, CAPTURED 2026-10-03 (see 0p); 2 is the user's Studio work

Ranked by plausible share of the remaining gap (1.27% mean, logic +6.5%):

1. **AOI-internal logic in real shape (~8 files).** AOI logic ~2 MB predicted across the
   seventeen; alone it needs +51% ±37, jointly +12% (~0.25 pp). Real AOIs operate on their
   parameters, often InOut UDTs/axes (references, not copies); every AOI calibration file used
   simple logic on Input/Local members. One AOI, 50 rungs of MOV/ADD/GRT/XIC/OTE on (a) Input
   members, (b) Local members, (c) InOut UDT members, (d) InOut axis members; (e) with
   EnableInFalse + Prescan routines; 1 vs 50 instances to re-confirm logic-once. Realism floor.
2. **Studio transplants (from the user).** Export 27: its untransplanted
   programs hold ~50 KB of its 69 KB residual — alarms, cam-control, junction-box programs next.
   Exports 16 and 06, 2nd/4th worst, never decomposed: their three largest
   programs one at a time.
3. **Public program tags (6 files, spec since 0k).** The captured `progscope_prog_{udt,arr}_n{010,050,200}`
   with every tag `Usage="Public"`, differenced against them. Real: 83 / 41 / 23 public tags in
   three programs, two among the worst five.
4. **Near-empty-weighted small instructions on the realism floor (6 files, 400 calls):** NOP
   (4,785 real), CTU, RES (876 / 957), AFI (627), GSV into a UDT member vs a DINT (521), TON/RTO
   with literal presets.
5. **ST routines (4 files), last:** ~40 real routines, 1,510 lines — likely below the floor.

Item 1 extended: `aoicx_*` 14 files (OQ-AOICOMPLEX) — a drive-axis AOI as complex as the real
ones, with a nested AOI call, GSV/SSV on the Axis class and motion on InOut-UDT members.

Built: 1 → `aoiint_*` 7 files (OQ-AOIINTERNAL); 3 → `progpub_*` 6 (OQ-PUBLICTAG); 4 →
`smallin_*` 10 (OQ-SMALLINSTR); 5 → `streal_*` 4 (OQ-STREAL). Predictions written in each
question before capture. Building `streal_mixed400` exposed a crash in the ST coverage message
(the one-operator gap key has three fields); fixed in `sizing/report.py`.

### 0n. Deep pass, 2026-10-02 (before the motlit capture) — NEXT

**1.27% mean, 3.08% worst** after module I/O operands were typed (code-only, no generated row
moved). Findings, all measured on the real set:

- **Category scale test:** routine logic still the one consistent category, +6.5% ±3.1
  (program logic +7.7% ±4.0; AOI-internal logic +51% ±37 — noisy). Everything else is
  inconsistent across files.
- **What the exact transplants lack:** COP, CONCAT, JMP/LBL, CPS, DTOS, GSV, AFI, SIZE — real
  logic is full of them, the three exactly-priced transplants have almost none, and their
  weights come from near-empty files. → OQ-BLOCKSTR, 19 files built.
- **AOI arguments:** 1,133 integer literals into REAL Input parameters, never measured.
  → OQ-AOILITARG, 9 files built.
- **Module I/O operands:** typed from the modules' own connection tags — wired.
- **Source-protected AOIs: dead end.** The export carries no encrypted payload for a protected
  AOI (description and revision note only), so its logic cannot be sized from the file; its
  instance data (from the L5K values) is within a few KB of what is charged.
- **Alarm conditions:** generated and real conditions share every attribute and shape; no
  lead.
- **Export 27:** its four transplants price within ~3 KB except the protected-AOI program
  (17.7 KB); ~50 KB of its 69 KB residual sits in programs never transplanted. A Studio
  transplant of its next-largest programs (the ones with the alarm, camming-control and
  junction-box logic) is the sharpest remaining instrument.

**Ready to capture together:** `motlit_*` (15), `aoilit_*` (9), `blkstr_*` (27, with the COP/CPS cross-type pairs).

### 0m. After the literal and idiom captures, 2026-10-02 — NEXT

**Real set 1.29% mean, 3.08% worst, 8/17 inside 1%, 15/17 inside 2%.** OQ-LITREAL closed
KNOWN on 198 exact files; OQ-REALIDIOM closed (routine size and DINT-bit targets exact).

**Studio-made checks under the current engine:** transplants 2.9% / −1.0% / 0.2% of added
logic (20.7% on the one with a source-protected AOI); six of seven removed routines within
±4%; the DINT→REAL rung edit predicted to the byte (−600 vs −600). Still short: the
cam-correction routine (520, 12.6%) and the bit-and-status rung (144).

**Next batch — SPEC, not built (ask before generating):**
1. **OQ-MOTIONLIT — BUILT, 15 `motlit_*` files, awaiting capture** (as specified) on the captured motop inventory (control `motop_n00`, +1,330),
   400 calls each, one MOTION_INSTRUCTION per call, alternating PnAxisX/PnAxisY:
   - MAJ: speed/accel/decel/jerk as REAL tags (control) / integer literals / float literals (3).
   - MAPC: slave and master scaling and the two lock positions as REAL tags / integer
     literals (`1,1,…,0,0`) / float literals, on the captured-exact `instrfirst_mapc_v2`
     signature and a CAM_PROFILE from the proven blocks (3).
   - MCCP and MAG: the same tag / integer / float triple on each (needs the real signature
     from `gen_motion_instructions`; 4–6).
   - MAM in the old `litop_mam` shape (AXIS_VIRTUAL, `% of Maximum`, `Trapezoidal`,
     `Disabled,Current,0,None,0,0`) on the realism floor, against `realidiom_mam_tag`: settles
     the 12-per-call disagreement (1).
   Each `_ilit`/`_flit` file differences against its `_tag` twin; the prediction for each is
   the wired law (52 + 44(n−1), +4 per float) applied at the documented REAL positions.
2. **Studio edits (asked for, not built here):** in the cam-correction routine file, delete the
   rung with the three MAM calls and read Capacity — that routine is the one still 12.6%
   short with every literal now priced.
3. Small, only if 1 and 2 leave room: DINT+SINT tag mixes (258 real calls), unresolved
   module I/O and string-member operands (~1.5% of typed calls).

### 0l. Deep review, 2026-09-25 — where it stands and what is left

**Real set now 1.41% mean, 3.18% worst, 6/17 inside 1%, 14/17 inside 2%** (from 2.18% /
4.31% this morning): integer/float literals typed by spelling (OQ-LITREAL) and motion-
structure members typed for the resolver (8,800 real operands had resolved to nothing).

**Studio-made variants re-measured under the current engine** (each isolates real ladder
against the exactly-priced plant, so these are the sharpest instrument available):

| variant | shortfall, % of added logic, before → now |
|---|---|
| plant + worst program's program A | 15.2% → **7.7%** |
| plant + program B | 9.1% → **2.6%** |
| plant + program C | 10.6% → **4.5%** |
| plant + program D (carries a source-protected AOI) | 30.9% → 24.6% (a minimum by design) |
| seven routines removed one at a time | 5 still short 200–650 bytes (10–16%); the other two now within −56 / −20 |
| literal-heavy rung | short 252 → over 60 (≈4 per literal: 52 wired vs 48 measured; litreal decides) |
| bit-and-motion-status rung | still short 144 |

**Real ladder against the plant, per 100 rungs** (the plant is the base of every batch):

| | real | plant |
|---|---:|---:|
| instructions | 556 | 249 |
| bit instructions | 322 | 178 |
| integer literals | 98 | 31 |
| AOI calls | 12.9 | 0 |
| CLR (REAL / DINT) | 7.8 / 11.6 | 0 |
| COP / CPS / FLL | 9.9 | 0 |
| JSR (args) | 6.0 (2.8) | 1.0 (0) |
| motion instructions (literal operands) | 2.3 (4.7) | 0 |
| **rungs per routine** | **16.7** | **~97** |

**Typed-call coverage** (84,844 real calls, current resolver): measured or wired mixes
cover ~97% — DINT|literal 37.5%, DINT 20.9%, REAL 15.9%, STRING 9.5% (OQ-STRINGMOV),
REAL|literal 6.1% (litreal pending), DINT+REAL 1.5%, SINT 1.3%, DINT+INT 1.1%. Unmeasured:
DINT+SINT 0.3% and SINT|literal 0.3% (litint pending), INT+REAL 0.1%. Unresolved ~1.5%:
string members, module I/O image words, members of source-protected AOIs.

**What the 17-program attribution can and cannot say.** After both fixes, rungs,
routines, JSRs and CLR-on-REAL each fit the remaining residual equally (0.52–0.56% mean):
everything scales with size, so 17 files cannot separate them. Isolation batches and
Studio-made variants are the only instruments that separate features.

**Ranked, built and awaiting capture:**
1. `litreal_*` (47), `litint_*` (118), `typun_*` (22) — literal conversion rate per
   instruction and type; CLR/ABS/NEG/BTD/TRN by type (CLR on REAL: 4,120 real calls at the
   DINT rate); CLR vs `MOV(0,…)`.
2. `realidiom_*` (33, OQ-REALIDIOM) — routine granularity at real size (the best single
   fit to what remains is ~324 bytes per routine, and no realism file has small
   routines); ONS/OTL/OTU on bits of DINT words (real error-bit and one-shot idiom,
   never measured on those instructions); MAM/MAS written the real way (literal tails,
   jerk 75, move type 1) — `litop_mam_*` already read 40–64 per call under.

**Not built, for after capture:**
- DINT+SINT and INT+REAL mixes if litint/litreal leave them open (0.4% of calls).
- Module I/O image types (`Local:1:I.Data[0]` INT) — code-only, ~0.7% of typed calls.
- A Studio-made edit of the bit-heavy routine (ONS on DINT bits → BOOL) if `realidiom_bit_*`
  comes back exact but that routine stays short.

**Checked and ruled out today:** motion operands and dense rungs (`motop_*`, exact);
AOI output reads and deep member paths (Studio edits, exact); every documented
data-type rule for the instructions generated (now enforced by lint).

### 0k. Find the ~2% the series law was cancelling — NEXT

Checkpoint: tag `checkpoint-2026-09-25-pre-series-law`, commit `172f581` (0.58% state).
Real set with the law: 2.18% mean, 4.31% worst, all seventeen under, 1.19%–4.31%.

Already ruled out, measured:
- **Operand data types.** 91.7% of 84,846 real typed calls are one measured type,
  3.3% measured mixes; SINT/DINT, INT/REAL and other unmeasured mixes are 0.6%.
- **Instruction coverage.** Every native mnemonic with 5+ real uses is weighted.
- **Axes and alarm conditions.** They correlate with the gap only through size; both
  priced exact on the realism floor (`l9v38_m_kinetix`, `l9v38_m_alarms`), and real
  axis tags have exactly the generated tags' shape.
- **Documentation.** Descriptions and comments measured free.
- **Motion operands and rung density.** Axis attributes, MOTION_INSTRUCTION members and
  rungs of up to 64 units / 16 legs / two-deep nesting all price exact (`motop_*`, 44 files).

**Where it lives (category scale test, seventeen programs).** Scaling one category alone
to absorb each file's shortfall: **routine logic needs +11.6%, spread ±3.1% across the
seventeen**, and would take the set to 0.45% mean. Every other category needs a scale that
varies wildly by file (tags +4.2% ±2.6%, UDT definitions +57% ±26%, modules +89% ±85%).
So the ~2% is almost certainly in **how real ladder is priced**, about 11% of logic,
consistently.

**What it is not, within logic.** The realism plant (1,280 stations of ordinary ladder
over 128 routines) prices exactly, so plain rungs, routines, member operands and the
XIC/OTE/TON/compare/ADD/MOV mix are right. Per-file counts of rungs, instructions,
operands, literals, branches, routines and AOI calls all fit the gap about equally
(0.45–0.6% mean), because all scale with size; 17 files cannot separate them.
Program-scope operand references are a few percent of real references and do not fit
(1.81%), though the two worst programs have the highest share (export 27 12%, export 18 25%).
Distinct operand paths per routine do not separate either: the plant has more (0.75 per
reference) than real ladder (0.53) and still prices exactly.

Leads, ranked:
0. **Feature transplant onto the plant** (spec, not built): the plant prices exactly, so
   add ONE real-ladder feature at a time at its real density and see which reads ~11%
   of its own logic under. About 12 files, each baseline + ~2,000 rungs: branch-heavy
   rungs (real density ~0.8 branch opens per rung), AOI calls at real density, 3-level
   member operands, JSR with parameters, literal-heavy MOV/compare, program-scoped
   operands, public program-scoped operands, COP/FLL block moves, bit-of-word operands
   (`Word.5`), timers/counters with real presets, CPT, and a mixed control.
**Transplant results (export 27, Studio-made).** Four of its programs were imported one
at a time INTO the plant (`realism_base_f25`, 840,384, priced exact), so each file's
error belongs to the imported content alone. Split by category, the shortfall is the
imported logic: **15.2%, 9.1% and 10.6% of added logic** on the three clean programs
(the fourth, 30.9%, carries a source-protected AOI and is a minimum by design) — the same
+11.6% ±3.1% the category test found across the seventeen. A second file with the spares
removed confirmed unused AOIs/spares are priced right (46,560 measured, 46,080
predicted). Real ladder against the plant, per 100 rungs: 530–680 instructions (plant
249), 116–214 extra writers (0), 70–94 branch openings (~10), 51–106 bit-of-word operands
(0), 187–259 multi-level member paths (0). Each of those was measured exact ALONE
(OQ-OPERANDSHAPE, OQ-SERIESREAL, branch tests), so the suspect is their combination in
dense rungs. Next: routine-level variants of the worst program (below).

**Source-protected AOIs: REJECTED — no sidecar, no user-supplied sizes, ever.** A
protected AOI stays priced at its visible interface with the source-protected warning;
the tool never takes sizes from the user. (Measured for reference: export 27's protected
AOI exposes ~20 of its 124 data-type bytes; its encrypted logic is likely ~15 KB of the
plant+Line2 transplant's 24,420 shortfall.) Do not re-propose it.

**Routine-level results (plant + export 27's worst program, one routine removed per
file, JSR and SBR removed with it).** All seven routines read short of the engine, by
6.8% to 38.6% of their predicted cost (136 to 1,184 bytes). Fitting the seven shortfalls
on two features at a time, the best pair is **operands that live in the motion system**:
~+50 per reference to an axis attribute (`Axis.ActualPosition`, `.ActualVelocity`,
`.AxisHomedStatus`, `.CommandVelocity`, `.RegEvent1Status`, …) and ~+29 per reference to
a MOTION_INSTRUCTION member (`Mam.DN`, `OTU(Mah.EN)`, …) — rms ±216 on seven points, so a
lead, not a constant. The engine prices both as plain operands and cannot resolve axis
attribute types at all. Real exposure (17 programs): 6,440 axis-attribute and 1,366
MI-member references; at those rates ~20% of the real shortfall on average (2% to 68% by
program). **Rung-level (Studio-made, one rung kept per routine, against the routine-removed file):** homing-routine rung 7 measured 712 vs 568 predicted (short 144, 25%); cam-correction rung 3 measured 2,484 vs 2,232 (short 252, 11%). The two-feature rates over-predict both rungs (~380 and ~600), so the motion lead is real in direction but not in size, and density is still in play. **Captured — both leads dead.** All 44 `motop_*` files, zero errors, read the control's +1,330 to the byte (OQ-MOTIONOP, OQ-DENSERUNG closed negative, RESOLVED_QUESTIONS): axis attributes and MOTION_INSTRUCTION members cost exactly what plain members and TIMER bits cost, and rungs of up to 64 units, 16 legs or two-deep nesting are priced right. The seven-routine fit was size, not mechanism.

What the two isolated rungs carry that no generated file has:
- **AOI output parameters read from outside the AOI** (`Sensor.Out`, 4 in rung 7) — 1–8% of real operands per program.
- **Four-level member paths** through a UDT whose member is a UDT holding a MOTION_INSTRUCTION (`Cell.Servo.MAH.PC`, 3 in rung 7) — OQ-OPERANDSHAPE went to three levels; deeper is 3.2% of real operands.
- **REAL compared with a DINT tag or an integer literal** (`LES(RealArr[2],DintTag)`, `GRT(RealArr[2],1)`, rung 3), on **program-scope arrays**.

**Studio-made results:** AOI output reads price right (+104 vs +120, the new tag's name bucket); deep member paths price exactly (+448 vs +448); **integer literals against REAL operands do not** (−600 vs −312). Wired as OQ-LITREAL: real set **2.18% → 1.74% mean, 4.31% → 3.44% worst**; 47 `litreal_*`, 118 `litint_*` (SINT/INT/DINT) and 22 `typun_*` (CLR, MOV(0,…)/ABS/NEG/BTD/TRN by type — CLR on REAL alone is 4,120 real calls the engine prices at the DINT rate) built to measure it per instruction and type. Next: capture, then replace the single 52 rate with per-instruction, per-type conversions where they differ.

Next, in order:
1. **(Done) Studio-made variants of the two kept-rung files.** In the rung-7 file: (a) replace the four AOI-output reads with a plain controller BOOL; (b) replace the deep `Cell.Servo.*` references with plain tags of the same type. In the rung-3 file: (c) make the DINT compare limit a REAL tag and the literals `1`/`-1` REAL (`1.0`/`-1.0`). Read Capacity after each single change; each delta against the engine's delta for the same edit says which feature carries the rung's shortfall.
2. **Spec, not built: split the motop inventory's +3,108** (RESOLVED, OQ-DENSERUNG note). Three files on the captured `l9v38_m_kinetix_l8v35` content, differenced against it: MOTION_INSTRUCTION[400] alone; 100 tags of a UDT holding four MOTION_INSTRUCTION members alone; 100 tags of a UDT holding five TIMER members alone. Expected payoff ~0.05 pp — below the floor unless the rate is far above 4 bytes; run only if item 1 comes back empty.

1. **Studio-made variants of export 27 (4.31%) — METHOD AGREED.** Subtractive,
   one program at a time, starting from the full project:
   - Delete ONE program in Logix Designer (its routines and program tags). Leave
     controller tags, UDTs, AOIs and modules alone, so only that program's logic and
     program data leave.
   - Verify, read Capacity (Used), and **export the WHOLE project** (File > Save As
     .L5X), not a program-level export: only a whole-project file can be set against a
     whole-controller reading.
   - Save as `<export>_minus_<program>.L5X` with the Used figure; files go to
     `samples/local/` over chat, never the repository.
   - Order by the engine's predicted logic per program, largest first; the six largest
     carry ~70% of its logic.
   Per program: measured delta (full - variant) against the engine's delta for the same
   two files. A program whose measured delta beats its predicted delta by ~11% or more
   is where the shortfall lives; its rung shapes are then the next test. The variants
   are fitting inputs, not blind tests.
   **Next, one level down:** in the plant-plus-program file of the worst program, empty
   ONE routine at a time (delete its rungs, leave one `NOP();` so JSRs still verify),
   re-read Capacity, largest routines first. Each delta is one routine's rungs. — the technique that found literal
   operands. In Logix Designer, one change at a time, re-read Capacity: (a) delete the
   7 unused AOI definitions; (b) change the 83 `Usage="Public"` program tags to Local;
   (c) delete one heavy data-mapping program. Each gives an exact delta to set against
   the engine's own delta for the same content.
2. **Public program tags** (spec, not built): 6 files, the captured-exact
   `progscope_prog_{udt,arr}_n{010,050,200}` with every tag `Usage="Public"`,
   differenced directly against them. Only three real programs use public tags (83,
   41, 23 of them) and two are among the four worst.
3. **Module-typed operands**: 4.4% of real typed calls do not resolve, mostly
   `Module:slot:I.Data[n]` operands whose element type (often INT) the parser skips, so
   they pay the DINT rate. Code-only: resolve them from the module-defined types.
4. **Structure** (weak, 17 points): per-routine +339 and per-JSR +314 beyond size.
   Wait for leads 1–3.

### 0j. Series-output law — WIRED (option A)

−12 per extra writing instruction, TON counted. Headline 0.58% → 2.18% by design.

The 14 `srsty_*` captures make it universal: −12 per extra writing instruction in
every shape, timers included. Applied, all 38 series files are exact and the real set
reads 2.18% (all under) instead of 0.58%. Either ship it and hunt the ~2% under-charge
it exposes, or keep it off. See OQ-SERIESREAL.

### 0i. The other eight v36 renames — DONE (captured, ACS/ASN/TOD/FRD weights wired)

`gen_v36_renames.py`, 8 files: SQRT, TRUNC, EXPT, ACOS, ASIN, ATAN, TO_BCD, BCD_TO, one
each, 1756-L81E v38, realism floor, 1,000 rungs in the v35 calibration shape. A clean
import confirms v38 takes the name; SQRT/TRUNC/EXPT/ATAN are compared with their v35
weights, ACOS/ASIN/TO_BCD/BCD_TO have none on file and are measured. OQ-V36MNEMONIC.

### 0h. Series-output styles — CAPTURED (see 0j)

14 `srsty_*` files (`gen_series_styles.py`) for OQ-SERIESREAL, built on request: the
dominant real multi-output shape (branch legs with their own conditions, 61% of real
extra outputs) at k = 2/4/8, plus shared-condition legs, two-condition legs, nested
branches, output mid-rung, series latches, mixed writers in legs, and timers. Supersedes
spec item 1 below.

### Accuracy headline excludes protected-heavy programs — DONE

`quick_eval.py` drops real programs with 10+ `<EncodedData>` blocks (export 33 only).
Seventeen counted: 0.58% mean, 2.37% worst.

### Next batch — SPECIFIED, NOT BUILT (ask before generating)

Each answers a still-open item; v35 / 1756-L81E, realism floor.
1. **OQ-SERIESREAL, branch legs with their own conditions** — 6 files, 1,600 unique
   output BOOLs each: `[XIC(a)OTE(x),XIC(b)OTE(y)]` with k = 2, 4, 8 legs, against the
   same outputs as k single-output rungs (k01) and as `XIC(c)[OTE…]` (the measured
   output-only form). Discriminates: whether −12 applies when every leg has its own
   condition, the one real shape never built.
2. **Sixth POINT I/O rack over-predicted by 826** (`l9v38_m_pointio`) — 4 files: the
   baseline plus 1, 2, 4 extra RACK_n racks. Discriminates a per-rack repeat discount
   (AENTR/C or card) from a one-off. Differenced against `realism_base_f25`.
3. **Generic ETHERNET-MODULE under by 440** (`l9v38_m_geneth`, also +392 on the
   near-empty capture) — 3 files: 1, 2, 4 modules of 8/8 SINT. Separates a per-module
   overhead from the connection-data law. ETHERNET-MODULE is 25% of real modules.
4. ~~INT member alignment~~ — **dropped, below the floor in bytes.** 2,716 real typed
   calls carry an INT member operand (0.63% of 431,798 real instructions), but at +4
   each that is about 11 KB across every real export, ~0.02% of bytes.
Plus the 7 `bridgeph_*` files already built (OQ-BRIDGEPH), not yet converted.

### 0f. Export 43 — bridge placeholders, POINT I/O notices, indirect-bit usage — DONE, capture pending

Export 43 (1756-L81E v35, reading supplied with the file, so a fitting input) predicted
2,616,308 on receipt (−2.51%), 2,612,260 now (−2.66%). Its coverage notices were:
- **ETHERNET-BRIDGE placeholders** (inhibited, nothing beneath): charged the flat 2,344
  with a notice. Now 320 each, no notice, for a childless ETHERNET-BRIDGE only
  (OQ-BRIDGEPH). A gateway 1756-EN2T keeps the flat rate and its notice. 7 files
  built to confirm, awaiting capture.
- **Rack-aliased 1734 cards**: already priced (488 all-in, OQ-POINTIOCONN); the notice
  text claiming otherwise was stale and is gone.
- **Usage**: `Tag[Ptr].[BitNum]` (an indirect bit of an indexed element) failed to
  parse, so the array, pointer and bit-number tags read unused. 158 such operands
  across 18 real exports. Fixed and pinned in `tests/test_usage.py`.

### 0d. Usage counts in the UI — DONE

`l5x_memory_analyzer/usage.py`, built once per file at load. Every tag, member, array
element, UDT/AOI member, routine and module carries a use count in the List (**Uses**
column; unused rows tinted amber with an UNUSED pill) and in the treemap (amber stripes,
which take priority over the estimated-logic outline, and a tooltip note). A use is a
reference from ladder, ST or FBD operands, an alias target, an alarm input or associated
tag, an axis's motion group or drive module, a JSR target, or a main routine. Indexed
access uses every element; a file instruction on an element uses the whole array; a
reference to a whole structure uses its members "via parent" (the UDT definition view
still reports a member nothing names as unused, noting it is copied whole). AOI
EnableIn/EnableOut and hidden BOOL-packing members carry no count. HMI/SCADA access is
not visible in an L5X, and the tooltip says so. Pinned by `tests/test_usage.py`. The
light/dark toggle was removed; the page follows the OS setting.

### 0c. L9 (ControlLogix 5590) — DONE

96 files captured clean: L81E v38 = L81E v35 and L9 v38 = L81E v38 + 2,276 on all 32
content items (OQ-L9PLATFORM). Budgets from published user memory, 2 / 5 / 8 / 15 MB
(OQ-L9BUDGET). Nothing further planned for the L9.

### 0e. v36+ instruction names — done

Sixteen renames (EQU→EQ … MOV→MOVE, LIM→LIMIT, FRD→BCD_TO) priced identically to the v35
names; lint refuses the old name at v36+ and the new one below v36. Resolved,
`RESOLVED_QUESTIONS.md` OQ-V36MNEMONIC.

### 0b. UI: an AOI definition's "instance" size view disagrees with the instance tag

On the demo project (`scripts/build_demo_project.py`), opening Add-On Instructions ›
`Valve_Ctrl` with **AOI Size: instance** reads 28 B, the sum of its seven 4-byte members,
while the instance tag `V001` of that same AOI is priced at 104 B in Controller Tags. One
of the two views is leaving out the per-instance overhead the tag sizer charges. Fix so
both views give the instance tag's figure. The README deliberately shows the definition page
and the instance tag, not the instance view, until then.

### 0a. Operand spelling — DONE, 2.86% → 1.66%

The operand-type surcharge and the tag-driven index cost were charged only on bare tag
names. `sizing/operand_types.py` resolves member paths, aliases, program scope and AOI
parameters; the index regex accepts a member-path index. Real set 2.86% / 5.42% →
1.66% / 4.83%; zero generated rows moved. Four questions follow from it
(OQ-TYPEDMEMBER, OQ-INDIRECTUDT, OQ-STRINGMOV, OQ-MIXEDTYPE) — **50 files built**
(`gen_operand_spelling.py`, `samples/generated/opspell/`), awaiting capture alongside
the realism and progscope batches (78 files waiting in all). Ranked by expected
movement: INDIRECTUDT (≤0.6), STRINGMOV (0.2–0.6), MIXEDTYPE (0.1–0.4), TYPEDMEMBER
(confirmation of what is wired).

The confound gate counted any `[` as a branch, so an array subscript read as a branched
rung. Fixed (`_BRANCH_OPEN`, pinned in `test_confound_check.py`).

**Next audit of the same kind:** every other rule keyed on operand TEXT — CPT's REAL
destination (bare `tag_types` lookup), JSR structured-argument detection, CMP operands,
alarm AssocTag resolution — for a spelling it silently skips.

### 0. The realism floor — every generated file from here on

At least 5 Ethernet I/O nodes, at least 25% of the controller predicted, no output bit
written by more than one OTE/ONS and no OTL/OTU target also OTE'd. `sample_gen/realism.py`
builds a baseline that meets it (RACK_1..RACK_5: 1734-AENTR/C + 4 IB8 + 4 OB8 each; a
1,280-station plant, 842,178 predicted alone). `write_sample()` refuses a file below it
(`lint.realism_findings`) and `test_build_guards` refuses a waiting batch below it. An
older generator re-run without the baseline now fails, deliberately.

### 1. Capture the realism batch and the program-scope batch — 28 files

| family | files | question |
|---|---:|---|
| `realism_base_f{25,50}` | 2 | OQ-REALISMFLOOR — is the model exact on a full controller? |
| `realism_srout_{series,branch,inter}_k*` | 8 | OQ-SERIESREAL — does −12/extra output survive unique bits at real fill? |
| `realism_pio_{bool,addr,alias}_n{080,160}` | 6 | OQ-PIOADDR — POINT I/O address vs BOOL vs alias |

`samples/generated/realism/`, `gen_realism_batch.py`.

### 1b. The program-scope batch — OQ-PROGSCOPESTRUCT, 12 files (rebuilt on the baseline)

| family | files | what it measures |
|---|---:|---|
| `progscope_{ctl,prog}_udt_n{010,050,200}` | 6 | a 7-member UDT tag at controller vs program scope |
| `progscope_{ctl,prog}_arr_n{010,050,200}` | 6 | a DINT[20] array tag at controller vs program scope |

| | |
|---|---|
| **Mechanism** | program-scoped structured tags are in 14 of 17 real programs, densest in the three worst, and have never been built |
| **Needs** | one capture run |

The operand-shape batch that held this slot closed negative: member paths cost what
plain tags cost.

### 1a. Real rung skeletons — held until the realism batch reads

The proposed real-rung-skeleton batch (the commonest real instruction sequences with
generated tag names) waits on OQ-SERIESREAL and OQ-REALISMFLOOR: if the plant reproduces
the real under-prediction, the skeleton batch is built on the same baseline; if it lands
exact, fill is eliminated and the skeletons are the next discriminator.

### 2. Take safety content out of the standard total — DONE 2026-10-18 (0s)

Wired from the `safe_*` captures rather than assumed: a safety program's tags and logic
cost 0 standard; a controller-scope safety tag costs its name entry (the alias-tag
formula); the 296 safety shell stays; standard logic reading a safety tag pays its
ordinary weight plus 8 per safety operand. Its effect on the seven real safety files
is not re-read here: they are not in `samples/local/`.

### 2a. Calibrate file confidence to real error

The file-level confidence reads 97–99% on real programs whose error is 2–6%. It must
carry the unexplained real residual, not only the component bands, until that residual
is explained.

### 3. The real residual — OQ-REALUNDER

Once the operand batch reads, rerun the real set. If member operands carry the cost,
wire it and re-measure. If they do not, the next candidates in order are the other
things real rungs have and calibration rungs do not: many instructions per rung with
mixed operand shapes, and program-scoped tags at real density. No term is fitted on
the real set itself.

### 4. Structural module model — generalisation

Unseen 2198 drives and supplies are now priced from their family (4,113 / 3,589 first
copy, 984 repeat discount). An unseen non-2198 catalog still gets the flat 1,672, plus
its declared connection data; a generic Ethernet node gets the measured 4x connection
law. `module_io` is 2.9% of mass. See `FUTURE_TESTS.md`.

### Capture backlog

12 files, the `progscope_*` of item 1. The `opshape_*` and `jsredge_*` batches are
captured and closed.

**A row captured but never differenced is work already paid for and thrown away.**
Run `scripts/unreconciled.py` after every batch.

---

## Standing gates

These are process items, and every one of them exists because its absence cost
something. **They are the part that gets skipped, so they are listed as work.**

| gate | state |
|---|---|
| `quick_eval` prints the stopping-rule verdict every run | done |
| `quick_eval` scoped by default; `--full` only for reconciliation and final checks | done |
| Dead-architecture rows excluded from default reports, never from real rows | done |
| `capture_errors.py` routes every errored row to an owning question and exits non-zero otherwise | done |
| `confound_check.py` gates a generator before files are built | done |
| `unreconciled.py` run after every batch | **run it** |
| One capture roster, not five | done: item 1 is the only roster |
| Comments carry facts, not conversation or dates | done: every comment and docstring |
| No date in source | done: Python, YAML, JavaScript, PowerShell, AutoHotkey, docs |
| No customer program name in source | done: replaced by export numbers |
| No customer program name in git HISTORY | **not done -- see below** |

### Real exports are referred to by number

Every real export is `export NN` throughout the source, the docs and
`memory_model.yaml`. The numbering is stable and the names are gone.

A comparative claim needs the files told apart -- "one declares STRING[200],
another STRING[255]" is only checkable if both can be identified -- so the names
became numbers rather than vanishing into "a real export". Where a citation
pointed at a file only to say where a shape came from, it now reads "a real
export" and keeps the tag or member name, which is the part that makes it
checkable.

**`samples/manifest.csv` carries no real file names either.** Every real row's
`l5x_path` is the neutral `samples/local/realprog_NN.L5X`. The real file name lives
in `samples/local/aliases.csv`, which is gitignored like everything else in that
folder, and `load_manifest()` resolves each row by name under `samples/local/`
through it — whatever folder the archive happened to unpack into. The old reason
for keeping real names in the manifest ("rewriting it breaks prediction") no longer
applies.

### Removing a name from the working tree does not remove it from history

The names are still in every earlier commit. `git log -p` recovers all of them,
and so does any existing clone, fork or cache. **A working-tree cleanup is not a
disclosure remedy.** If the requirement is that a public reader cannot find
them, the history has to be rewritten or the repository re-initialised from the
current tree, and even then anything already cloned stays out.

The mapping from export number back to the real filename is recoverable from
that same history. In the working copy it lives only in the gitignored
`samples/local/aliases.csv`.

---

## The unexplained residual pattern

Kept because it is the only structure left in the residual that has not been
explained away.

The ratio of residual to `routine_logic` bytes is **bimodal** across the real set.
It is not a per-unit error — coefficient of variation is 1.74 per occurrence, 1.72
over the top four instructions and 1.73 per rung, so whatever it is does not scale
with any count the engine has.

With the JSR caller base corrected, all eighteen real programs present under-predict. **A candidate that can only add
bytes is wrong before it is tested**, which eliminates most of what looks plausible.

---

## Done, and not to be re-opened

| item | outcome |
|---|---|
| JSR caller base — OQ-JSRCALLERBASE | **Closed.** A caller routine costs what any routine costs; the per-caller 5,096 was an over-charge on every real program and is gone. |
| Per-rung term — OQ-RUNGSHAPE | **Closed negative.** 12 packing files, all exact. |
| Alarm conditions at real scale — OQ-ALARMCONDREAL | **Solved.** 0–600 real-shape conditions, flat +12 only. |
| Build-failure log — OQ-BUILDFAIL-OPEN | **Closed.** Every file builds; causes enforced in lint. |
| Module name length — OQ-MODULENAMELEN | **Bounded.** Law measured (name stored twice, each rounded to 8), 0.02% real exposure, not wired. |
| AOI call arguments | **Wired.** An Input argument that is not the literal 0/1 costs 28, not 16; an RLL file with AOI calls carries a one-time 264. |
| JSR with UDT/STRING parameters | **Wired.** A structured argument is copied like COP: +8 per call, +12 on the target. 8.0% → 0.03% on those files. |
| Operand shape — OQ-OPERANDSHAPE | **Closed negative.** 26 files exact; member paths cost what plain tags cost. |
| JSR parameter edges | **Wired.** UDT member args at the structured rate; UDT returns +16/call; RET values 48 + 22 each, less 72 per target. |
| Source-protected content | **Reported.** Encrypted routines and AOIs are listed as an unpriced gap; not estimable. |
| Source-protected AOIs and routines | **Priced at a minimum**: stand-in definition from visible Parameters (instances, calls, interface); routine shells. UI banner says MINIMUM. 3.06% → 2.86%. |
| Safety processors in accuracy | **Excluded.** Accuracy is measured on standard processors only. |
| 2198 repeat and unseen catalogs | **Wired.** Family-wide repeat discount of 984; unseen drives and supplies priced from their family. |
| Verify the top instruction weights against real rung shapes | Worked. The weights hold exactly outside the shape they were fitted on. |
| Controller tag shapes | Closed negative. The residual is not in tag data space. |
| Rank open questions by real bytes × uncertainty | Done. This file is its output. |
| Write the stopping rule down and enforce it in code | Done. |
| Refresh the strip ladders | **Dead.** A derived variant of a real export does not build. See the read-only rule in `CLAUDE.md`. |
| The controller-shell probe | **Cancelled.** There was nothing to probe — the engine predicts a File\|New project exactly. |
| Produced and consumed tags | **Force-closed** below the noise floor. Do not reopen. |
| Literal operands, including the INT/SINT over-charge | **Closed on real exposure**: 37 slots, 1,756 bytes across eighteen real exports. |
| AOI definition cost | **KNOWN.** 8-byte total alignment wired; 117 of 125 def-only captures inside ±8. |
| Hiding per-element confidence by default | Done: `?ConfidenceMode=true` shows it; the Errors tab always shows the file-level figure. |
| Partial exports on import — OQ-EXPORTSCOPE | **Closed, accepted in use.** AOI, UDT and program imports behave as needed; the unmeasured import shell stays uncharged. |
| Attribute the real residual with Studio-made deletions | **Declined.** Costs a bench session per reading. Struck from the plan; item 3 is what remains. |
| MAPC | **EXACT.** 164 a call plus the motion literal law on its four REAL parameters (`motlit_mapc_*`, exact; the 260 first measured carried the scaling literals 1,1); the steps 1→10→100 were exact, the 100-call reading landing on the number written down before capture. **Real use (researched 2026-10-20):** 126 calls across the seventeen, 0.10% of real instructions — INSTRUCTION_COVERAGE. Closed. |
| CROUT and the rest of the Safety family | **Classified Safety (2026-10-20).** 0 standard each; the rung cost is the safety partition's (CROUT 492, `sizing/safety.py`, OQ-SAFETYPARTITION). Zero real uses of CROUT; `instrfirst_crout_x10`'s errored row is a standard controller refusing a safety instruction (OQ-CROUT-MAPC-BUILDFAIL), not a missing weight. |
