# Sample Batch Notes — 2026-08-23

Plain-English explanation of every file in this batch (52 new `.L5X`
files across 4 generators), for reference while capturing real Capacity/
Build data. Each generator's own docstring has the full technical
reasoning and real-corpus citations — this doc is the quick "what am I
looking at and why" version. Grouped by generator; within each group,
files are listed in the order that makes the comparison logic clearest,
not alphabetically.

All files convert/lint clean and are ready to run through the normal
L5X→ACD→Build→Capacity pipeline.

## 1. CPT/CMP expression complexity (`gen_cmpcpt_complexity.py`, 31 files, `samples/generated/logic/`)

**Why this batch exists:** the existing CPT weight (452 blocks/rung) was
proven wrong overnight — real data shows CPT's cost depends on how complex
the expression inside it is, not a flat number. Every file below has
exactly ONE rung with ONE instruction, so each file's real Capacity delta
is a clean, direct read of that one expression's true cost — no dividing
by rung count, no assumptions.

### A. `cptcx_operandcount_n01` through `_n10` (8 files)

Same idea repeated with more operands each time, same `+` operator
throughout: `CPT(Dest,L0)`, then `CPT(Dest,L0+L1)`, then
`CPT(Dest,L0+L1+L2)`, ... up to 10 tags added together. **What to look
for:** does the real byte cost grow smoothly with operand count? Roughly
linear? A step function? This is the core data needed to build a real
per-operand cost model.

### B. `cptcx_operatormix_mixedops` / `_nested` / `_powermix` (3 files)

Same operand count (4) as one of the files above, but different operator
shapes: mixed operators (`L0+L1-L2*L3`), parentheses/nesting
(`(L0+L1)*(L2-L3)`), and the `**` power operator mixed in
(`L0**L1+L2**L3`). **What to look for:** compare these against
`cptcx_operandcount_n04` (same operand count, plain `+` chain) — does
operator TYPE matter on its own, once operand count is held fixed?

### C. `cptcx_constants_*` (5 files)

Same idea as group A, but some operands are literal numbers instead of
tags: `L0+5` (int const), `L0+L1+5`, `L0+5+L1+10` (two int consts),
`R0*1.5+R1` (float const, REAL tags), `R0*1.5+R1*2.5-R2/3.5` (multiple
float consts). **What to look for:** does a literal constant cost the
same as a tag operand, less, or more? This directly answers "be sure to
put constants as well as tags."

### D. `cmpcx_*` (10 files)

CMP's own version of the same idea — a comparison complexity ladder:
plain tag comparison (`L0>L1`), an expression on one side
(`L0+L1>L2`), expressions on both sides (`L0+L1>L2+L3`), a more complex
shape (`(L0+L1)*L2>L3-L4`), an int literal (`L0>5`), a float literal
(`L0>5.5`), expression plus literal (`L0+L1>5`), float constant mixed
with tags (`L0*1.5>L1+2.5`), and two compound (AND) conditions — one
simple (`L0>L1&&L2>L3`), one with expressions in each half
(`(L0+L1)>L2&&(L3-L4)<L5`). Every CMP file also has a trailing
`OTE(TB0)` — that's not a mistake, it matches the confirmed real shape
(a bare CMP can't legally close a rung, same reason the original
instruction sweep pairs several instructions with a companion OTE).

### E. `*_spotcheck_*_n100` (3 files)

The "couple of spot checks in files with multiple rungs with the same
expression" — 3 of the expressions above (`CPT(Dest,L0+L1)`,
`CPT(Dest,L0+L1-L2*L3)`, `CMP(L0>L1)`), each repeated across 100
identical rungs instead of just 1. **What to look for:** does the n=100
result equal roughly 100× the n=1 result? If yes, the single-rung reads
above scale linearly and can be trusted directly. If not, something about
repeated identical expressions behaves differently than one in isolation
(background optimization, dedup, etc.).

### F. `cmpcpt_randommix_00` / `_01` (2 files)

A realistic mixed file — several different CPT/CMP expression shapes from
groups A-D above, each repeated a random number of times (20-150 rungs),
combined into one file (553 total rungs in file 00, 655 in file 01). Not
meant to validate anything on its own (there's no correct model to check
against yet) — just gives a realistic multi-expression file to capture,
which will help confirm whatever per-operand model eventually gets built
actually composes correctly across a real mixed routine.

## 2. AOI Required/Visible parameter flags (`gen_aoi_required_visible.py`, 9 files, `samples/generated/aoi/`)

**Why this batch exists:** you explained the real meaning of the
Required/Visible parameter flags (Required = must have a tag wired on the
calling rung; Visible-not-Required = must have SOME value but wiring it
is optional; neither = hidden, tag-browser only) — every earlier AOI test
this project generated hardcoded both flags to `false`/`false`, so none
of that behavior was ever actually tested.

### A. `reqvis_allhidden_n4_def_only` / `_allrequired_n4_def_only` / `_allvisibleoptional_n4_def_only` / `_mixed_n4_def_only` (4 files)

Same AOI shape (4 DINT Input parameters), 0 instances — only the
Required/Visible flags on those 4 params differ: all hidden (the old
default), all required, all visible-but-optional, and a realistic mixed
case (2 required + 1 visible-optional + 1 hidden). **What to look for:**
does the AOI's own *definition* cost change at all based on these flags,
or is it purely a UI/editing-behavior thing with no storage cost? (My
guess is no size difference here — but this hasn't been tested before,
so it's worth confirming rather than assuming.)

### B. `reqvis_allhidden_call_full` / `_allrequired_call_full` / `_allvisibleoptional_call_full` (3 files)

Same 3 flag combinations as above, but now with a real instance tag AND
an actual rung that CALLS the AOI instruction (e.g.
`ReqVisCallAllrequired(TestInstance,CallArg0,CallArg1,CallArg2,
CallArg3);`) — every parameter that isn't hidden gets a real tag wired to
it in the call. This is a new kind of test file for this project — every
earlier AOI test only ever built the backing tag, never an actual
instruction call in a rung. **What to look for:** does actually calling
the instruction (vs. just having the backing tag exist) cost anything
extra? Compare against group A's def_only numbers.

### C. `reqvis_2req2optional_call_allwired` / `_2req2optional_call_optomitted` (2 files)

Same AOI (2 required + 2 visible-optional DINT params), same 1 instance +
real call — but one file wires all 4 params in the call, the other only
wires the 2 required ones and leaves the 2 optional ones out entirely.
This matches a real pattern found in your own corpus (the `PTimer`
instruction call in `SJ_Gormley_20251112_r02.L5X` only wires 2 of its 4
non-hidden Input params, leaving the optional ones blank). **What to look
for:** does leaving an optional parameter unwired in the call cost less
than wiring it, or is the cost identical either way?

## 3. LBL/JMP validation rules (`gen_lbljmp_rules.py`, 7 files, `samples/generated/logic/`)

**Why this batch exists:** the existing LBL/JMP data only ever tested a
strict 1-LBL-to-1-JMP pairing, so the confirmed 104-blocks/pair number
can't be split into LBL's own cost vs JMP's own cost. You also flagged
real rules (multiple JMPs can target one LBL; a LBL can exist with no JMP
at all; JMP always needs a LBL somewhere) that hadn't been tested.

### A. `lbljmp_manytoone_n02` / `_n05` / `_n10` (3 files)

One LBL, then 2 / 5 / 10 separate JMP instructions all jumping to that
same one label. **What to look for:** if you plot total cost against
JMP count, the slope of that line is JMP's true per-instance cost (since
LBL only appears once, its cost is now isolated as the fixed/intercept
part) — this is the first real way to separate LBL's cost from JMP's.

### B. `lbljmp_lblonly_n01` / `_n05` / `_n10` (3 files)

1 / 5 / 10 LBL rungs with ZERO JMPs anywhere pointing at them — a legal
shape per your own description. **What to look for:** LBL's cost in
complete isolation, no JMP mixed in at all — the cleanest possible read
of LBL's own per-instance marginal cost.

### C. `lbljmp_samename_diffroutines` (1 file)

Two separate subroutines (MainProgram's MainRoutine, and a second program
called SecondProgram), each with its own `LBL(Common)`/`JMP(Common)` pair
— both routines reuse the exact same label name "Common." This isn't
really a byte-size test, it's a sanity/scoping check: confirms two
routines can both use a common label name like "Start" or "Common"
without colliding, matching your rule that labels are scoped per-
subroutine. Should build and convert clean; if it doesn't, that itself
is useful information (would mean label names need to be globally
unique, not per-routine, which would be a real correction to note).

## 4. JSR/SBR/RET parameter passing (`gen_jsr_sbr_ret.py`, 5 files, `samples/generated/logic/`)

**Why this batch exists:** the existing JSR data only ever tested
`JSR(SubTest,0)` — zero parameters. You described the real mechanism
(JSR passes input params in, SBR receives them into the subroutine's own
local tags as its first instruction, RET sends values back out from
anywhere in the subroutine including conditionally and more than once) —
confirmed against 2 real matching examples in
`SJ_Gormley_20251112_r02.L5X` (`_525_InputMapping_TS`/
`_525_OutputMapping_TS`) before building these.

### A. `jsr_paramcount_n01_r01000` / `_n05_r01000` / `_n10_r01000` (3 files)

1000 identical rungs of `JSR(JsrParamTarget,N,arg1,...,argN);` calling a
subroutine whose only content is `SBR(param1,...,paramN)NOP();` then
`RET();` — 1, 5, or 10 pure input parameters, no return values. **What to
look for:** the "1/5/10 parameters on the JSR" comparison you asked for
— does JSR/SBR's combined cost grow with parameter count, or does the
existing flat 72-blocks/rung JSR weight (which was only ever tested at 0
params) already cover this?

### B. `jsr_mixedio_5in_2out_r01000` (1 file)

1000 rungs of a JSR with 5 input parameters AND 2 return parameters —
`JSR(JsrMixedTarget,5,JIn0,...,JIn4,JOut0,JOut1);`, matching the real
`5-input-then-N-return` shape confirmed in your corpus. **What to look
for:** compare against the pure-5-input file in group A — does adding 2
return parameters cost anything beyond what 5 pure inputs already cost?

### C. `jsr_multiret_n04_r01000` (1 file)

1000 rungs of a JSR to a subroutine with 1 input parameter but 4 separate
RET points — 3 conditional (`XIC(Cond0)RET(LOutA,LOutB);`,
`XIC(Cond1)RET(...)`, `XIC(Cond2)RET(...)`) plus one final unconditional
RET, matching your description ("conditionally elsewhere as well with no
limit on Qty used"). **What to look for:** does having 4 RET instructions
in the subroutine (vs. the usual 1) cost like 4× a normal repeated
instruction, or is there something special about RET specifically?
