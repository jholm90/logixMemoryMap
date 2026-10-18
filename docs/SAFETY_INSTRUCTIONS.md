# Safety-routine instructions — call shapes

Every instruction a GuardLogix safety routine offers that the model has not sized, with
its operands in order, as Studio itself exports them. Source: a Studio-made v35 safety
routine with one rung per instruction and every operand filled, plus its printed ladder,
which names each operand (2026-10-17, kept in the gitignored `samples/local/`). RIN, ROUT
and FPMS come from the first seed (`L81ES_Sample.L5X`). Sizing is OQ-SAFETYPARTITION.

## How a safety instruction call is laid out

1. **First operand: the backing tag**, of the instruction's own structure type (table).
2. **Then its settings**, in this order where present:
   - **Drop-down keywords** are written exactly as Studio displays them, spaces and
     hyphens included: `EMERGENCY STOP`, `EQUIVALENT - ACTIVE HIGH`, `SAFETY GATE`,
     `LIGHT CURTAIN`, `ENABLE PENDANT`, `POSITION LIMIT SWITCH`. Single-word ones:
     `MANUAL`, `AUTOMATIC`, `NEGATIVE`, `DISABLED`, `ENABLED`, `IMMEDIATE`, `NONE`,
     `OFF`, `False`, `Seconds`, and a cam profile letter (`A`).
   - **Times and limits as numbers** (ms unless the label says s). Some settings take a
     tag instead (DCAF's discrepancy time, CSM's delay and pulse period, every drive-safety
     delay and speed), conventionally the backing tag's own member.
3. **Then the inputs**, conventionally the backing tag's own member of the same name
   (`DCS.ChannelA`): the member name is the operand label without spaces.
4. **Drive-safety instructions** (SS1, SS2, SBC, SOS, SDI, SLS, SLP) also take the SFX
   instruction's backing tag as *Feedback SFX* (all but SBC), and **end with output
   operands** (Active, Fault, Limit and so on), which are separate BOOL tags. SFX ends with
   its own two outputs, conventionally `SFX.SFH` and `SFX.FP`.
5. Some fields the ladder displays are not operands and do not appear in the text:
   Revision, Diagnostic Code, Fault Code, Fault Type, Actual Position/Cycles/Speed.

The operand count of every call matches the instruction's template in Studio's
instruction toolbar. THRSe is the one built-in mnemonic with a lowercase letter; the
parser named it explicitly on this evidence, having missed every THRSe rung before.

**Building files from these:** every output operand needs its own tag. The source routine
wires one `Bool1` to every drive-safety output and reuses two inputs (THRSe Reset on
`THRSe.InputStatus`, SS2 Active on `SS2.Reset`); a generated file may not, under the
realism floor.

## Operands, in order (after the backing tag)

Keywords and numbers show the value the source used; an input or setting shown by label
alone is the backing tag's own member.

| mnemonic | backing type | operands | settings and inputs |
|---|---|---:|---|
| RIN | REDUNDANT_INPUT | 6 | Reset Type = `AUTOMATIC`; Channel A; Channel B; Circuit Reset; Fault Reset |
| ESTOP | EMERGENCY_STOP | 6 | Reset Type = `MANUAL`; Channel A; Channel B; Circuit Reset; Fault Reset |
| ENPEN | ENABLE_PENDANT | 6 | Reset Type = `MANUAL`; Channel A; Channel B; Circuit Reset; Fault Reset |
| DIN | DIVERSE_INPUT | 6 | Reset Type = `MANUAL`; Channel A; Channel B; Circuit Reset; Fault Reset |
| ROUT | REDUNDANT_OUTPUT | 6 | Feedback Type = `NEGATIVE`; Enable; Feedback 1; Feedback 2; Fault Reset |
| FPMS | FIVE_POS_MODE_SELECTOR | 7 | Input 1; Input 2; Input 3; Input 4; Input 5; Fault Reset |
| LC | LIGHT_CURTAIN | 8 | Reset Type = `MANUAL`; Channel A; Channel B; Input Filter Time = 0; Mute Light Curtain; Circuit Reset; Fault Reset |
| CROUT | CONFIGURABLE_ROUT | 9 | Feedback Type = `NEGATIVE`; Feedback Reaction Time (ms) = 100; Actuate; Feedback 1; Feedback 2; Input Status; Output Status; Reset |
| SMAT | SAFETY_MAT | 7 | Restart Type = `MANUAL`; Short Circuit Detect Delay Time (ms) = 100; Channel A; Channel B; Input Status; Reset |
| THRS | TWO_HAND_RUN_STATION | 8 | Active Pin Type = `DISABLED`; Active Pin; Right Button Normally Open; Right Button Normally Closed; Left Button Normally Open; Left Button Normally Closed; Fault Reset |
| THRSe | THRS_ENHANCED | 10 | Discrepancy Time (ms) = 500; Enable; Disconnected; Right Button Normally Open; Right Button Normally Closed; Left Button Normally Open; Left Button Normally Closed; Input Status; Reset |
| DCS | DCI_STOP | 10 | Safety Function = `EMERGENCY STOP`; Input Type = `EQUIVALENT - ACTIVE HIGH`; Discrepancy Time (ms) = 500; Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Channel A; Channel B; Input Status; Reset |
| DCST | DCI_STOP_TEST | 11 | Safety Function = `EMERGENCY STOP`; Input Type = `EQUIVALENT - ACTIVE HIGH`; Discrepancy Time (ms) = 500; Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Channel A; Channel B; Test Request; Input Status; Reset |
| DCSTL | DCI_STOP_TEST_LOCK | 14 | Safety Function = `SAFETY GATE`; Input Type = `EQUIVALENT - ACTIVE HIGH`; Discrepancy Time (ms) = 500; Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Channel A; Channel B; Test Request; Unlock Request; Lock Feedback; Hazard Stopped; Input Status; Reset |
| DCSTM | DCI_STOP_TEST_MUTE | 15 | Safety Function = `LIGHT CURTAIN`; Input Type = `EQUIVALENT - ACTIVE HIGH`; Discrepancy Time (ms) = 500; Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Test Type = `NONE`; Test Time (ms) = 500; Channel A; Channel B; Test Request; Mute; Muting Lamp Status; Input Status; Reset |
| DCSRT | DCI_START | 9 | Safety Function = `ENABLE PENDANT`; Input Type = `EQUIVALENT - ACTIVE HIGH`; Discrepancy Time (ms) = 500; Enable; Channel A; Channel B; Input Status; Reset |
| DCM | DCI_MONITOR | 8 | Safety Function = `POSITION LIMIT SWITCH`; Input Type = `EQUIVALENT - ACTIVE HIGH`; Discrepancy Time (ms) = 500; Channel A; Channel B; Input Status; Reset |
| DCA | DCA_INPUT | 11 | Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Channel A; Channel B; Tolerance; Discrepancy Time (ms) = 500; High Limit; Low Limit; Input Status; Reset |
| DCAF | DCAF_INPUT | 11 | Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Channel A; Channel B; Tolerance; Discrepancy Time (ms); High Limit; Low Limit; Input Status; Reset |
| TSAM | MUTING_TWO_SENSOR_ASYM | 14 | Restart Type = `MANUAL`; S1-S2 Time (ms) = 500; S2-LC Time (ms) = 500; Maximum Mute Time (s) = 500; Maximum Override Time (s) = 10; Light Curtain; Sensor 1; Sensor 2; Enable Mute; Override; Input Status; Muting Lamp Status; Reset |
| TSSM | MUTING_TWO_SENSOR_SYM | 15 | Restart Type = `MANUAL`; S1-S2 Discrepancy Time (ms) = 500; S1,S2-LC Minimum Time (ms) = 500; S1,S2-LC Maximum Time (ms) = 500; Maximum Mute Time (s) = 500; Maximum Override Time (s) = 10; Light Curtain; Sensor 1; Sensor 2; Enable Mute; Override; Input Status; Muting Lamp Status; Reset |
| FSBM | MUTING_FOUR_SENSOR_BIDIR | 19 | Restart Type = `MANUAL`; S1-S2 Time (ms) = 500; S2-LC Time (ms) = 500; LC-S3 Time (ms) = 500; S3-S4 Time (ms) = 500; Maximum Mute Time (s) = 500; Maximum Override Time (s) = 10; Direction; Light Curtain; Sensor 1; Sensor 2; Sensor 3; Sensor 4; Enable Mute; Override; Input Status; Muting Lamp Status; Reset |
| CPM | CB_CRANKSHAFT_POS_MONITOR | 10 | Cam Profile = `A`; Enable; Brake Cam; Takeover Cam; Dynamic Cam; Input Status; Reverse; Press Motion Status; Reset |
| CBIM | CB_INCH_MODE | 11 | Ack Type = `MANUAL`; Inch Time (ms) = 500; Enable; Safety Enable; Standard Enable; Start; Press In Motion; Motion Monitor Fault; Slide Zone; Safety Enable Ack |
| CBSSM | CB_SINGLE_STROKE_MODE | 11 | Ack Type = `MANUAL`; Takeover Mode = `ENABLED`; Enable; Safety Enable; Standard Enable; Start; Press In Motion; Motion Monitor Fault; Slide Zone; Safety Enable Ack |
| CBCM | CB_CONTINUOUS_MODE | 14 | Ack Type = `MANUAL`; Mode = `IMMEDIATE`; Takeover Mode = `DISABLED`; Enable; Safety Enable; Standard Enable; Arm Continuous; Start; Stop At Top; Press In Motion; Motion Monitor Fault; Slide Zone; Safety Enable Ack |
| CSM | CAMSHAFT_MONITOR | 8 | Mechanical Delay Time (ms); Max Pulse Period (ms); Motion Request; Channel A; Channel B; Input Status; Reset |
| EPMS | EIGHT_POS_MODE_SELECTOR | 12 | Input 1; Input 2; Input 3; Input 4; Input 5; Input 6; Input 7; Input 8; Input Status; Lock; Reset |
| AVC | AUX_VALVE_CONTROL | 12 | Feedback Type = `NEGATIVE`; Feedback Reaction Time (ms) = 500; Delay Type = `OFF`; Delay Time (ms) = 500; Output Follows Actuate = `False`; Actuate; Delay Enable; Feedback 1; Input Status; Output Status; Reset |
| MMVC | MANUAL_VALVE_CONTROL | 10 | Enable; Keyswitch; Bottom; Flywheel Stopped; Safety Enable; Actuate; Input Status; Output Status; Reset |
| MVC | MAIN_VALVE_CONTROL | 9 | Feedback Type = `NEGATIVE`; Feedback Reaction Time (ms) = 500; Actuate; Feedback 1; Feedback 2; Input Status; Output Status; Reset |
| SFX | SAFETY_FEEDBACK_INTERFACE | 14 | Time Unit = `Seconds`; Position Scaling; Feedback Resolution; Unwind; Home Position; Feedback Position; Feedback Velocity; Feedback Valid; Connection Faulted; Home Trigger; Reset; Safe Feedback Homed → *output tag*; SFX Fault → *output tag* |
| SS1 | SAFE_STOP_1 | 13 | Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Stop Monitor Delay; Stop Delay; Standstill Speed; Decel Ref Speed; Decel Speed Tolerance; Feedback SFX → SFX tag; Request; Reset; SS1 Active → *output tag*; SS1 Fault → *output tag* |
| SS2 | SAFE_STOP_2 | 20 | Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Stop Monitor Delay; Stop Delay; SS2 Standstill Speed; Decel Ref Speed; Decel Speed Tolerance; Mode; Check Delay; SOS Standstill Speed; Standstill Deadband; Feedback SFX → SFX tag; Request; Reset; SS2 Active → *output tag*; SS2 Fault → *output tag*; SOS Active → *output tag*; SOS Standstill → *output tag*; SOS Fault → *output tag* |
| SBC | SAFE_BRAKE_CONTROL | 13 | Restart Type = `MANUAL`; STO to SBC Delay; Brake Feedback Check Delay; Brake Feedback 1; Brake Feedback 2; Input Status; Output Status; Brake Engage L; Reset; SBC Active → *output tag*; Brake Engaged → *output tag*; SBC Integrity → *output tag* |
| SOS | SAFE_OPERATING_STOP | 13 | Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Mode; Check Delay; Standstill Speed; Standstill Deadband; Feedback SFX → SFX tag; Request; Reset; SOS Active → *output tag*; SOS Standstill → *output tag*; SOS Fault → *output tag* |
| SDI | SAFE_DIRECTION | 11 | Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Position Window; Feedback SFX → SFX tag; Positive Request; Negative Request; Reset; SDI Active → *output tag*; SDI Limit → *output tag*; SDI Fault → *output tag* |
| SLS | SAFELY_LIMITED_SPEED | 11 | Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Check Delay; Active Limit; Feedback SFX → SFX tag; Request; Reset; SLS Active → *output tag*; SLS Limit → *output tag*; SLS Fault → *output tag* |
| SLP | SAFELY_LIMITED_POSITION | 12 | Restart Type = `MANUAL`; Cold Start Type = `MANUAL`; Check Delay; Positive Travel Limit; Negative Travel Limit; Feedback SFX → SFX tag; Request; Reset; SLP Active → *output tag*; SLP Limit → *output tag*; SLP Fault → *output tag* |

## Exported text

```
RIN(RIN,AUTOMATIC,RIN.ChannelA,RIN.ChannelB,RIN.CircuitReset,RIN.FaultReset);
ESTOP(ESTOP,MANUAL,ESTOP.ChannelA,ESTOP.ChannelB,ESTOP.CircuitReset,ESTOP.FaultReset);
ENPEN(ENPEN,MANUAL,ENPEN.ChannelA,ENPEN.ChannelB,ENPEN.CircuitReset,ENPEN.FaultReset);
DIN(DIN,MANUAL,DIN.ChannelA,DIN.ChannelB,DIN.CircuitReset,DIN.FaultReset);
ROUT(ROUT,NEGATIVE,ROUT.Enable,ROUT.Feedback1,ROUT.Feedback2,ROUT.FaultReset);
FPMS(FPMS,FPMS.Input1,FPMS.Input2,FPMS.Input3,FPMS.Input4,FPMS.Input5,FPMS.FaultReset);
LC(LC,MANUAL,LC.ChannelA,LC.ChannelB,0,LC.MuteLightCurtain,LC.CircuitReset,LC.FaultReset);
CROUT(CROUT,NEGATIVE,100,CROUT.Actuate,CROUT.Feedback1,CROUT.Feedback2,CROUT.InputStatus,CROUT.OutputStatus,CROUT.Reset);
SMAT(SMAT,MANUAL,100,SMAT.ChannelA,SMAT.ChannelB,SMAT.InputStatus,SMAT.Reset);
THRS(THRS,DISABLED,THRS.ActivePin,THRS.RightButtonNormallyOpen,THRS.RightButtonNormallyClosed,THRS.LeftButtonNormallyOpen,THRS.LeftButtonNormallyClosed,THRS.FaultReset);
THRSe(THRSe,500,THRSe.Enable,THRSe.Disconnected,THRSe.RightButtonNormallyOpen,THRSe.RightButtonNormallyClosed,THRSe.LeftButtonNormallyOpen,THRSe.LeftButtonNormallyClosed,THRSe.InputStatus,THRSe.InputStatus);
DCS(DCS,EMERGENCY STOP,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,DCS.ChannelA,DCS.ChannelB,DCS.InputStatus,DCS.Reset);
DCST(DCST,EMERGENCY STOP,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,DCST.ChannelA,DCST.ChannelB,DCST.TestRequest,DCST.InputStatus,DCST.Reset);
DCSTL(DCSTL,SAFETY GATE,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,DCSTL.ChannelA,DCSTL.ChannelB,DCSTL.TestRequest,DCSTL.UnlockRequest,DCSTL.LockFeedback,DCSTL.HazardStopped,DCSTL.InputStatus,DCSTL.Reset);
DCSTM(DCSTM,LIGHT CURTAIN,EQUIVALENT - ACTIVE HIGH,500,MANUAL,MANUAL,NONE,500,DCSTM.ChannelA,DCSTM.ChannelB,DCSTM.TestRequest,DCSTM.Mute,DCSTM.MutingLampStatus,DCSTM.InputStatus,DCSTM.Reset);
DCSRT(DCSRT,ENABLE PENDANT,EQUIVALENT - ACTIVE HIGH,500,DCSRT.Enable,DCSRT.ChannelA,DCSRT.ChannelB,DCSRT.InputStatus,DCSRT.Reset);
DCM(DCM,POSITION LIMIT SWITCH,EQUIVALENT - ACTIVE HIGH,500,DCM.ChannelA,DCM.ChannelB,DCM.InputStatus,DCM.Reset);
DCA(DCA,MANUAL,MANUAL,DCA.ChannelA,DCA.ChannelB,DCA.Tolerance,500,DCA.HighLimit,DCA.LowLimit,DCA.InputStatus,DCA.Reset);
DCAF(DCAF,MANUAL,MANUAL,DCAF.ChannelA,DCAF.ChannelB,DCAF.Tolerance,DCAF.DiscrepancyTime,DCAF.HighLimit,DCAF.LowLimit,DCAF.InputStatus,DCAF.Reset);
TSAM(TSAM,MANUAL,500,500,500,10,TSAM.LightCurtain,TSAM.Sensor1,TSAM.Sensor2,TSAM.EnableMute,TSAM.Override,TSAM.InputStatus,TSAM.MutingLampStatus,TSAM.Reset);
TSSM(TSSM,MANUAL,500,500,500,500,10,TSSM.LightCurtain,TSSM.Sensor1,TSSM.Sensor2,TSSM.EnableMute,TSSM.Override,TSSM.InputStatus,TSSM.MutingLampStatus,TSSM.Reset);
FSBM(FSBM,MANUAL,500,500,500,500,500,10,FSBM.Direction,FSBM.LightCurtain,FSBM.Sensor1,FSBM.Sensor2,FSBM.Sensor3,FSBM.Sensor4,FSBM.EnableMute,FSBM.Override,FSBM.InputStatus,FSBM.MutingLampStatus,FSBM.Reset);
CPM(CPM,A,CPM.Enable,CPM.BrakeCam,CPM.TakeoverCam,CPM.DynamicCam,CPM.InputStatus,CPM.Reverse,CPM.PressMotionStatus,CPM.Reset);
CBIM(CBIM,MANUAL,500,CBIM.Enable,CBIM.SafetyEnable,CBIM.StandardEnable,CBIM.Start,CBIM.PressInMotion,CBIM.MotionMonitorFault,CBIM.SlideZone,CBIM.SafetyEnableAck);
CBSSM(CBSSM,MANUAL,ENABLED,CBSSM.Enable,CBSSM.SafetyEnable,CBSSM.StandardEnable,CBSSM.Start,CBSSM.PressInMotion,CBSSM.MotionMonitorFault,CBSSM.SlideZone,CBSSM.SafetyEnableAck);
CBCM(CBCM,MANUAL,IMMEDIATE,DISABLED,CBCM.Enable,CBCM.SafetyEnable,CBCM.StandardEnable,CBCM.ArmContinuous,CBCM.Start,CBCM.StopAtTop,CBCM.PressInMotion,CBCM.MotionMonitorFault,CBCM.SlideZone,CBCM.SafetyEnableAck);
CSM(CSM,CSM.MechanicalDelayTime,CSM.MaxPulsePeriod,CSM.MotionRequest,CSM.ChannelA,CSM.ChannelB,CSM.InputStatus,CSM.Reset);
EPMS(EPMS,EPMS.Input1,EPMS.Input2,EPMS.Input3,EPMS.Input4,EPMS.Input5,EPMS.Input6,EPMS.Input7,EPMS.Input8,EPMS.InputStatus,EPMS.Lock,EPMS.Reset);
AVC(AVC,NEGATIVE,500,OFF,500,False,AVC.Actuate,AVC.DelayEnable,AVC.Feedback1,AVC.InputStatus,AVC.OutputStatus,AVC.Reset);
MMVC(MMVC,MMVC.Enable,MMVC.Keyswitch,MMVC.Bottom,MMVC.FlywheelStopped,MMVC.SafetyEnable,MMVC.Actuate,MMVC.InputStatus,MMVC.OutputStatus,MMVC.Reset);
MVC(MVC,NEGATIVE,500,MVC.Actuate,MVC.Feedback1,MVC.Feedback2,MVC.InputStatus,MVC.OutputStatus,MVC.Reset);
SFX(SFX,Seconds,SFX.PositionScaling,SFX.FeedbackResolution,SFX.Unwind,SFX.HomePosition,SFX.FeedbackPosition,SFX.FeedbackVelocity,SFX.FeedbackValid,SFX.ConnectionFaulted,SFX.HomeTrigger,SFX.Reset,SFX.SFH,SFX.FP);
SS1(SS1,MANUAL,MANUAL,SS1.StopMonitorDelay,SS1.StopDelay,SS1.StandstillSpeed,SS1.DecelRefSpeed,SS1.DecelSpeedTolerance,SFX,SS1.Request,SS1.Reset,Bool1,Bool1);
SS2(SS2,MANUAL,MANUAL,SS2.StopMonitorDelay,SS2.StopDelay,SS2.SS2StandstillSpeed,SS2.DecelRefSpeed,SS2.DecelSpeedTolerance,SS2.Mode,SS2.CheckDelay,SS2.SOSStandstillSpeed,SS2.StandstillDeadband,SFX,SS2.Request,SS2.Reset,SS2.Reset,Bool1,Bool1,Bool1,Bool1);
SBC(SBC,MANUAL,SBC.STOtoSBCDelay,SBC.BrakeFeedbackCheckDelay,SBC.BrakeFeedback1,SBC.BrakeFeedback2,SBC.InputStatus,SBC.OutputStatus,SBC.BrakeEngageL,SBC.Reset,Bool1,Bool1,Bool1);
SOS(SOS,MANUAL,MANUAL,SOS.Mode,SOS.CheckDelay,SOS.StandstillSpeed,SOS.StandstillDeadband,SFX,SOS.Request,SOS.Reset,Bool1,Bool1,Bool1);
SDI(SDI,MANUAL,MANUAL,SDI.PositionWindow,SFX,SDI.PositiveRequest,SDI.NegativeRequest,SDI.Reset,Bool1,Bool1,Bool1);
SLS(SLS,MANUAL,MANUAL,SLS.CheckDelay,SLS.ActiveLimit,SFX,SLS.Request,SLS.Reset,Bool1,Bool1,Bool1);
SLP(SLP,MANUAL,MANUAL,SLP.CheckDelay,SLP.PositiveTravelLimit,SLP.NegativeTravelLimit,SFX,SLP.Request,SLP.Reset,Bool1,Bool1,Bool1);
```

ATAN2 is also offered in a safety routine and is a standard instruction:
`ATAN2(SourceA,SourceB,Dest)` on REAL tags.

## The safety-routine palette

A v35 safety routine offers 97 instructions: the 39 safety instructions above and 58
ordinary ones. That is the whole set — a Studio scrap holding every instruction the
safety-routine palette offers — and nothing outside it builds in a safety routine (PID,
for one, is not offered; NEQ is). The 58 ordinary ones:

ABS, ADD, AFI, AND, ATAN2, CLR, CMP, COP, CPT, CTD, CTU, DIV, EQU, EVENT, FAL, FLL, FSC,
GEQ, GRT, GSV, JMP, JSR, LBL, LEQ, LES, LIM, MCR, MEQ, MOD, MOV, MUL, MVM, NEG, NEQ, NOP,
NOT, ONS, OR, OSF, OSR, OTE, OTL, OTU, RES, RET, RTO, SBR, SIZE, SQR, SSV, SUB, SWPB, TND,
TOF, TON, XIC, XIO, XOR.

Lint (`instruction_not_in_safety_palette`) refuses any other instruction in a
Class="Safety" program; the v36+ spellings of the renamed ones are accepted.
