# CMP/CPT real-syntax reference

Pulled directly from `samples/local/**/*.L5X` (54 real production files,
gitignored, local-only) — 421 real `CMP(...)` calls and 1533 real
`CPT(...)` calls, extracted with a paren-balanced scan of every `<Text>`
element. Built 2026-08-22 after James's correction: don't guess/reinvent
CMP-compound syntax, pull real examples from the corpus instead. Use this
file as the reference before writing a new CMP/CPT test generator instead
of re-deriving syntax from scratch.

## CMP — single numeric comparison (the overwhelming majority, ~409/421)

CMP takes ONE numeric comparison expression. Operators seen: `>`, `>=`,
`<`, `<=`, `=`, `<>`. No boolean keywords (`AND`/`OR`/`NOT`) appear inside
CMP anywhere in the corpus.

```
CMP(Encoder.PositionChange>(Encoder.PulseRisetoFallDistance*2))
CMP(PkgSts.ConsecTest>=(PkgSts.WindowEndBit-PkgSts.WindowStartBit))
CMP(EN207.ScaledOutput >= Vert.HomeOffset - 0.1)
CMP(HMI.IoId=(HMI.IoRange[1].Max+1))
CMP((Wrk_Now.Yr MOD 100)<>0)
CMP(gHMI1.Fault.Display[gHMI1.Fault.Indexer]=cString_Text.Comparison_String)
CMP(ABS(InputValue - LastSampleValue) <> 0)
```

Notes: parens around a sub-expression are used when needed for order of
operations (arithmetic on one/both sides), not as a stylistic default —
`EN207.ScaledOutput >= Vert.HomeOffset - 0.1` has none. Whitespace around
operators is inconsistent (both `A>=B` and `A >= B` appear) — cosmetic,
not required either way. Equality (`=`) is used for both numeric and
STRING-array-member comparisons.

## CMP — compound (AND), real but rare (12/421, all one file/pattern)

James, 2026-08-22, after seeing the generator's failing `&`/`|` version:
**"CMP branches of AND/OR would be using the ladder logic editor and not
internal to the CMP... apparent parenthesis is needed with all written
statements for order of operations."** The corpus has exactly one real
compound-AND pattern (`EmporiumEdger_20250905r1.L5X`, 12 instances, all
the same shape with different array indices/setpoints):

```
CMP(_JH_DataLossClearedTmr[9].ACC>=(_JH_DataLossFltResetSP-10)&&(_JH_DataLossClearedTmr[9].ACC<=(_JH_DataLossFltResetSP+10)))
```

Confirmed from this: it's `&&` (double ampersand), not the single `&`
(bitwise AND) the generator was using. The first comparison is bare
(`A>=(B-10)`), the second is wrapped in its own parens
(`&&(A<=(B+10))`) — every real instance follows this exact shape, first
clause unwrapped, second wrapped.

**Not corpus-confirmed:** `||` (OR) — zero instances found anywhere in
this corpus. Assumed valid by symmetry with `&&` (Rockwell's own
Structured Text-influenced expression grammar treats `&&`/`||` as a
matched pair), but this is an assumption, not a confirmed fact — flag it
if a compound-OR test ever comes back with an error.

## CPT — arithmetic expression, any complexity

Same `dest,expr` shape throughout, `expr` is a normal math expression:

```
CPT(TotalBitsHigh,(EndBit-StartBit)+1);
CPT(HMI.StnID,HMI.Global.DisplayNumber/10);
CPT(Wrk_F,(Wrk_Now.Mo+9)MOD 12);
CPT(VelocityLimitPositive,ABS(Cfg_MaxFreq)*(MotorRatedSpeed/(MotorRatedFreq*60)));
CPT(THMain_StsLevelingSlope,ATN((THMainFar_HoistActPos.ActualPosition-ThMainNear_HoistActPos.ActualPosition)/(THMainFAR_WIndupChainAttachLocIN-THMainNear_WIndupChainAttachLocIN)));
CPT(THMain_TargetSlopeIN,TAN(THMain_TargetSlopeRAD));
CPT(PosnLug_TimeToRelieve,SQR(((2*PosnLug_ReliefAmt)/PosnBeltSpeeds.Accel[3])));
CPT(Press.Echo83.H2D.Result,Press.Echo83.H2D.Result + ((Press.Echo83.H2D.Temp * 10**1) / 2**12));
```

Real function/operator coverage found: `+ - * /` (726/751/730/775
instances), `MOD` (146), `**` power (13), `ABS()` (3), `ATN()` (10),
`TAN()` (9), `SQR()` (2, square root — NOT `SQRT`, note the name). CPT
can also carry a comparison as its "expression" (`CPT(X,A=B);`,
`CPT(X,(A MOD 100)<>0);`) — Logix apparently accepts a boolean result
written into a numeric dest same as any other expression; not something
this project tests today.

## Applies to

`src/sample_gen/gen_cmpcpt_layout.py`'s `group_cmp_layout` — the
`and_compound`/`or_compound`/`duplicate_cond` variants used
`L0>L1&L2<L3` (single `&`, no parens on either clause). Fixed to
`L0>L1&&(L2<L3)` matching the confirmed real shape above.
