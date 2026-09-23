# CMP and CPT real-syntax reference

Real call shapes, extracted from the production corpus with a paren-balanced scan
of every `<Text>` element: 421 real `CMP(...)` calls and 1,533 real `CPT(...)`
calls.

**Read this before writing a CMP or CPT test generator.** Do not re-derive the
syntax — invented CMP compound syntax has already failed to build once.

## CMP — single numeric comparison

The overwhelming majority: about 409 of 421 calls.

CMP takes **one** numeric comparison expression. Operators seen: `>`, `>=`, `<`,
`<=`, `=`, `<>`. **No boolean keywords** (`AND`, `OR`, `NOT`) appear inside CMP
anywhere in the corpus.

```
CMP(Encoder.PositionChange>(Encoder.PulseRisetoFallDistance*2))
CMP(PkgSts.ConsecTest>=(PkgSts.WindowEndBit-PkgSts.WindowStartBit))
CMP(EN207.ScaledOutput >= Vert.HomeOffset - 0.1)
CMP(HMI.IoId=(HMI.IoRange[1].Max+1))
CMP((Wrk_Now.Yr MOD 100)<>0)
CMP(gHMI1.Fault.Display[gHMI1.Fault.Indexer]=cString_Text.Comparison_String)
CMP(ABS(InputValue - LastSampleValue) <> 0)
```

Notes:

- **Parentheses around a sub-expression are used when order of operations needs
  them, not as a stylistic default.** `EN207.ScaledOutput >= Vert.HomeOffset - 0.1`
  has none.
- Whitespace around operators is inconsistent — both `A>=B` and `A >= B` appear.
  Cosmetic, not required either way.
- `=` is used for both numeric and STRING-array-member comparisons.

## CMP — compound

Real but rare: 12 of 421, all in one file, all the same shape with different array
indices and setpoints.

**The rule: AND/OR branching is done in the ladder logic editor, not inside the
CMP expression, and explicit parentheses are required for order of operations.**

```
CMP(_JH_DataLossClearedTmr[9].ACC>=(_JH_DataLossFltResetSP-10)&&(_JH_DataLossClearedTmr[9].ACC<=(_JH_DataLossFltResetSP+10)))
```

Two things this establishes:

1. It is `&&`, a **double** ampersand — not the single `&`, which is bitwise AND.
   A generator using `&` failed to build.
2. **The first comparison is bare and the second is wrapped in its own
   parentheses.** Every real instance follows exactly that shape.

> **`||` is not corpus-confirmed.** Zero instances anywhere. Assumed valid by
> symmetry with `&&`, since Rockwell's expression grammar treats them as a matched
> pair — but this is an assumption. Flag it if a compound-OR test ever comes back
> with an error.

## CPT — arithmetic expression, any complexity

Always `CPT(dest, expr)`, where `expr` is an ordinary math expression.

```
CPT(TotalBitsHigh,(EndBit-StartBit)+1);
CPT(HMI.StnID,HMI.Global.DisplayNumber/10);
CPT(Wrk_F,(Wrk_Now.Mo+9)MOD 12);
CPT(VelocityLimitPositive,ABS(Cfg_MaxFreq)*(MotorRatedSpeed/(MotorRatedFreq*60)));
CPT(THMain_TargetSlopeIN,TAN(THMain_TargetSlopeRAD));
CPT(PosnLug_TimeToRelieve,SQR(((2*PosnLug_ReliefAmt)/PosnBeltSpeeds.Accel[3])));
CPT(Press.Echo83.H2D.Result,Press.Echo83.H2D.Result + ((Press.Echo83.H2D.Temp * 10**1) / 2**12));
```

Real operator and function coverage:

| token | instances |
|---|---:|
| `+` | 726 |
| `-` | 751 |
| `*` | 730 |
| `/` | 775 |
| `MOD` | 146 |
| `**` (power) | 13 |
| `ATN()` | 10 |
| `TAN()` | 9 |
| `ABS()` | 3 |
| `SQR()` | 2 |

**Square root is `SQR`, not `SQRT`.** Note the name.

CPT can also carry a comparison as its expression — `CPT(X,A=B);`,
`CPT(X,(A MOD 100)<>0);`. Logix accepts a boolean result written into a numeric
destination like any other expression. **Not tested by this project today.**

## Cost model

CMP and CPT share one expression cost law — see `MEMORY_MODEL.md`. The tier table
fitted on CPT lands on CMP's measured residuals unchanged, which is the evidence
they share it.
