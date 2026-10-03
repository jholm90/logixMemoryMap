"""OQ-AOICOMPLEX: a drive-axis AOI as complex as the ones real programs carry.

Real programs nearly all carry one large drive-axis AOI (~18-20 KB of predicted internal
logic in each, the single biggest AOI-logic item in most of them) with a nested homing AOI
called from inside it. Measured composition of that kind of AOI, used here as targets only
(no real rung is copied; every rung below is built from standard instruction signatures):

  parameters   16 Input (11 BOOL, 3 REAL, 2 DINT), 2 Output BOOL, InOut AXIS_CIP_DRIVE,
               InOut servo UDT (~45 BOOL, ~23 REAL, 12 MOTION_INSTRUCTION, 7 DINT, the
               nested homing AOI's instance)
  locals       ~60: 30 REAL, 17 DINT, 6 TIMER, 5 BOOL, DINT[4], MOTION_INSTRUCTION
  logic        ~53 rungs, ~500 instructions, up to ~34 per rung and 9 branches; over half
               the operands are InOut-UDT members or axis attributes; ~130 integer literals
  content      XIC/XIO/ONS/OTL/OTU bit logic, EQU/NEQ state compares against literals, MOV,
               ~20 GSV and ~13 SSV on the Axis class through the InOut axis, MSO/MSF/MAFR/
               MASR/MAH/MAJ/MAM/MAS on InOut-UDT MOTION_INSTRUCTION members, TON, REAL
               math and CPT, JMP/LBL, COP, and one call of the nested homing AOI

GSV/SSV on the Axis class (~1,170 real calls) were never measured: the engine prices every
GSV/SSV at a flat 84 from three near-empty files. An AOI calling an AOI inside its own logic
was never measured either.

Two AOIs, the same definitions in every file except `DxAxis`'s Logic routine:
  DxHome   nested homing AOI (InOut axis, 7 locals REAL, TIMERs, MOTION_INSTRUCTION[7],
           EnableInFalse); its own logic is identical in every file
  DxAxis   the drive-axis AOI above; instances DxX / DxY called on PnAxisX / PnAxisY with
           servo tags SrvX / SrvY. The InOut parameters are NAMED PnAxisX and SrvX, and every
           local and input has a controller tag of the same name and type, so the identical
           body text also runs in a program routine (`aoicx_full_prog`)

Files (each differenced against `aoicx_n00`, where DxAxis has one rung):
  aoicx_<block>    one block of the body: bits, cmp, gsv, ssv, motion, math, jmp, axmem,
                   nested (DxHome called on a DxAxis local), nested_udt (on the servo UDT's
                   DxHome member, the real arrangement)
  aoicx_full       every block together -- additivity: full - n00 vs the sum of the blocks
  aoicx_full_prog  DxAxis back to one rung; the full body in MainRoutine on the same-named
                   controller tags -- AOI-internal vs program cost of the same content
  aoicx_full_two   a second definition DxAxisB with the full body as well, its own two
                   instances -- whether a second large AOI costs what the first does

Motion inventory: the captured-proven 2198-P208 bus supply + converter axis and one
2198-D032-ERS3 with CIP axes PnAxisX / PnAxisY. 1756-L81E at v35, realism floor.

Run: python -m sample_gen.gen_aoi_complex
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml
from sample_gen.gen_module_motion import (
    _MOTION_GROUP_TAG_XML, _axis_tag, _drive_module_xml, bus_supply_with_converter,
)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.predefined_members import predef_array_member, predef_member
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoicx"
CATEGORY = "aoi_complex"
AX, SRV = "PnAxisX", "SrvX"  # InOut parameter names == controller tag names

IN_BOOL = ["InEnable", "InReset", "InHome", "InJogF", "InJogR", "InAuto", "InStop",
           "InBypass", "InTqHome", "InHold", "InClrCnt"]
IN_REAL = ["InSpd", "InAcc", "InDec"]
IN_DINT = ["InMode", "InCmd"]
OUT_BOOL = ["OutReady", "OutFault"]
LO_REAL = [f"LoR{k:02d}" for k in range(30)]
LO_DINT = [f"LoD{k:02d}" for k in range(17)]
LO_TMR = [f"LoT{k}" for k in range(6)]
LO_BOOL = [f"LoB{k}" for k in range(5)]
MI_MEMBERS = ["Mso", "Msf", "Mafr", "Masr", "Mah", "Maj", "Mam1", "Mam2", "Mas1", "Mas2",
              "Mi10", "Mi11"]

# GSV / SSV Axis attributes and their data types (instruction-set facts).
GSV_ATTR = [("ConversionConstant", "R"), ("PositionErrorTolerance", "R"),
            ("SoftTravelLimitPositive", "R"), ("SoftTravelLimitNegative", "R"),
            ("TorqueLimitPositive", "R"), ("TorqueLimitNegative", "R"),
            ("MaximumAcceleration", "R"), ("MaximumDeceleration", "R"),
            ("PositionScalingNumerator", "R"), ("PositionScalingDenominator", "R"),
            ("PositionUnwindNumerator", "R"), ("PositionUnwindDenominator", "R"),
            ("RotaryMotorRatedSpeed", "R"), ("MotorOverspeedUserLimit", "R"),
            ("TravelMode", "D"), ("AxisConfigurationState", "D"), ("HomeSequence", "D"),
            ("MotorType", "D"), ("ConversionConstant", "R"), ("TorqueLimitPositive", "R")]
SSV_ATTR = ["HomePosition", "HomeOffset", "HomeSpeed", "HomeReturnSpeed",
            "SoftTravelLimitPositive", "SoftTravelLimitNegative", "TorqueLimitPositive",
            "TorqueLimitNegative", "SoftTravelLimitPositive", "SoftTravelLimitNegative",
            "TorqueLimitPositive", "TorqueLimitNegative", "HomePosition"]


# --- the servo UDT and the nested homing AOI ----------------------------------

def _home_aoi() -> tuple[str, list[MemberSpec]]:
    """Nested homing AOI: torque-limited move to a hard stop, then redefine position."""
    hl = ["HmR0", "HmR1", "HmR2", "HmR3", "HmR4", "HmR5", "HmR6"]
    rungs = [
        "XIC(HmStart)ONS(HmOns0)[MOV(0,HmStep),CLR(HmR0)];",
        "EQU(HmStep,0)XIC(HmStart)[MOV(HmTq,HmR1),MUL(HmTq,-1.0,HmR2),MOV(10,HmStep)];",
        f"EQU(HmStep,10)[SSV(Axis,HmAx,TorqueLimitPositive,HmR1),SSV(Axis,HmAx,TorqueLimitNegative,HmR2),"
        f"MOV(20,HmStep)];",
        "EQU(HmStep,20)MSO(HmAx,HmMi[0])XIC(HmMi[0].DN)MOV(30,HmStep);",
        "EQU(HmStep,30)ONS(HmOns1)MAJ(HmAx,HmMi[1],HmDir,HmSpd,Units per sec,HmAcc,Units per sec2,"
        "HmAcc,Units per sec2,Trapezoidal,100,100,% of Maximum,Disabled,Programmed,0,None);",
        "EQU(HmStep,30)XIC(HmMi[1].IP)TON(HmTmr0,?,?);",
        "EQU(HmStep,30)XIC(HmTmr0.DN)LIM(HmR3,HmR4,HmR5)ADD(HmR0,1.0,HmR0)MOV(40,HmStep);",
        "EQU(HmStep,40)MAS(HmAx,HmMi[2],Jog,Yes,HmAcc,Units per sec2,No,100,% of Time)"
        "XIC(HmMi[2].DN)MOV(50,HmStep);",
        "EQU(HmStep,50)MAH(HmAx,HmMi[3])XIC(HmMi[3].DN)[MOV(HmOff,HmR6),MOV(60,HmStep)];",
        "EQU(HmStep,60)MAM(HmAx,HmMi[4],0,HmR6,HmSpd,Units per sec,HmAcc,Units per sec2,HmAcc,"
        "Units per sec2,Trapezoidal,100,100,% of Maximum,Disabled,Programmed,0,None,0,0)"
        "XIC(HmMi[4].PC)MOV(70,HmStep);",
        "EQU(HmStep,70)[SSV(Axis,HmAx,TorqueLimitPositive,HmTqMax),"
        "SSV(Axis,HmAx,TorqueLimitNegative,HmTqMin),MOV(80,HmStep)];",
        "EQU(HmStep,80)[OTE(HmDone),OTE(HmHomed)];",
        "NEQ(HmStep,0)NEQ(HmStep,80)TON(HmTmr1,?,?);",
        "XIC(HmTmr1.DN)[OTE(HmErr),MSF(HmAx,HmMi[5])];",
        "NEQ(HmStep,0)NEQ(HmStep,80)OTE(HmBusy);",
        "XIC(HmBusy)XIO(HmErr)OTE(HmActive);",
        "LIM(1,HmStep,79)MUL(HmR0,2.5,HmR3);",
        "GRT(HmR0,HmR4)DIV(HmR0,HmR4,HmR5);",
        "XIC(HmErr)CLR(HmR6);",
        "XIC(HmReset)ONS(HmOns2)CLR(HmStep);",
        "XIC(HmReset)MSO(HmAx,HmMi[6]);",
    ]
    logic = "\n".join(rung_xml(k, r) for k, r in enumerate(rungs))
    eif = rung_xml(0, "[RES(HmTmr0),RES(HmTmr1),CLR(HmStep)];")
    return aoi_xml(
        "DxHome",
        input_params=[MemberSpec("HmStart", "BOOL", required=True, visible=True),
                      MemberSpec("HmTq", "REAL", required=True, visible=True),
                      MemberSpec("HmSpd", "REAL"), MemberSpec("HmAcc", "REAL"),
                      MemberSpec("HmOff", "REAL"), MemberSpec("HmTqMax", "REAL"),
                      MemberSpec("HmTqMin", "REAL"), MemberSpec("HmDir", "DINT"),
                      MemberSpec("HmReset", "BOOL")],
        output_params=[MemberSpec(n, "BOOL") for n in ("HmDone", "HmBusy", "HmErr", "HmHomed",
                                                        "HmActive")],
        inout_params=[MemberSpec("HmAx", "AXIS_CIP_DRIVE")],
        local_tags=[MemberSpec(n, "REAL") for n in hl]
                   + [MemberSpec("HmStep", "DINT"), MemberSpec("HmOns0", "BOOL"),
                      MemberSpec("HmOns1", "BOOL"), MemberSpec("HmOns2", "BOOL"),
                      predef_member("HmTmr0", "TIMER"), predef_member("HmTmr1", "TIMER"),
                      predef_array_member("HmMi", "MOTION_INSTRUCTION", 7)],
        logic_rungs_xml=logic, enable_in_false_rungs_xml=eif,
        description="Nested homing: torque-limited move to a stop, then redefine position.")


def _servo_members(home_storage: list[MemberSpec]) -> list[MemberSpec]:
    return ([MemberSpec(f"B{k:02d}", "BOOL") for k in range(96)]
            + [MemberSpec(f"R{k:02d}", "REAL") for k in range(23)]
            + [MemberSpec(f"D{k:02d}", "DINT") for k in range(7)]
            + [MemberSpec(n, "MOTION_INSTRUCTION") for n in MI_MEMBERS]
            + [MemberSpec("Home", "DxHome", nested_members=tuple(home_storage), is_aoi_member=True)])


# --- the DxAxis body, block by block --------------------------------------------

class _Writes:
    """Hands out write targets so no output is written twice in one body."""

    def __init__(self) -> None:
        self.srv_b = [f"{SRV}.B{k:02d}" for k in range(16, 96)]  # B00-B15 are read-only status

    def b(self) -> str:
        return self.srv_b.pop(0)


def _bits(w: _Writes) -> list[str]:
    r = []
    for k in range(16):
        a, b, c = f"{SRV}.B{k:02d}", f"{SRV}.B{(k + 5) % 16:02d}", IN_BOOL[k % 11]
        if k % 4 == 0:
            r.append(f"XIC({c})[XIC({a}),XIC({b})XIO(LoB{k % 5}),XIC({SRV}.B{(k + 9) % 16:02d})]"
                     f"XIO(InStop)ONS(LoOns[0].{k})OTL({w.b()});")
        elif k % 4 == 1:
            r.append(f"XIO({c})XIC({a})ONS(LoOns[0].{k})OTU({w.b()});")
        elif k % 4 == 2:
            legs = ",".join(f"XIC({SRV}.B{(k + j) % 16:02d})" for j in range(6))
            r.append(f"[{legs}]XIO(InBypass)OTE({w.b()});")
        else:
            r.append(f"XIC({a})XIC({b})XIO({c})[OTE({w.b()}),XIC(LoOns[1].{k})ONS(LoOns[3].{k})"
                     f"OTL({w.b()})];")
    return r


def _cmp(w: _Writes) -> list[str]:
    """State machine on the servo UDT's step word: wide rungs of compares and moves."""
    r = []
    for k in range(18):
        st = k * 10
        ons = f"LoOns[0].{16 + k}" if k < 16 else f"LoOns[1].{k}"
        r.append(f"EQU({SRV}.D00,{st})XIC(InEnable)[MOV({st + 10},{SRV}.D00),MOV({k},LoD{k % 17:02d}),"
                 f"NEQ(InCmd,{k})MOV(0,{SRV}.R{k % 23:02d}),EQU(InMode,{k})MOV(InSpd,LoR{20 + k % 10}),"
                 f"XIO(InHold)OTU({w.b()}),NEQ({SRV}.D01,{k})ONS({ons})OTU({w.b()})];")
    return r


def _gsv() -> list[str]:
    reals = iter(LO_REAL[:10] + LO_REAL[20:])
    dints = iter(LO_DINT)
    legs = [f"GSV(Axis,{AX},{a},{next(reals) if t == 'R' else next(dints)})" for a, t in GSV_ATTR]
    return [f"XIC(InEnable)ONS(LoOns[1].0)[{','.join(legs[:10])}];",
            f"XIC(InEnable)ONS(LoOns[1].1)[{','.join(legs[10:])}];"]


def _ssv() -> list[str]:
    def src(k):
        return f"{SRV}.R{k:02d}" if k < 4 else LO_REAL[20 + k % 10]
    legs = [f"SSV(Axis,{AX},{a},{src(k)})" for k, a in enumerate(SSV_ATTR)]
    return [f"XIC(InHome)ONS(LoOns[1].2)[{','.join(legs[:4])}];",
            f"XIC(InTqHome)ONS(LoOns[1].3)[{','.join(legs[4:8])}];",
            f"XIO(InTqHome)ONS(LoOns[1].4)[{','.join(legs[8:])}];"]


def _motion(w: _Writes) -> list[str]:
    m = f"{SRV}."
    return [
        f"XIC(InEnable)XIO({AX}.ServoActionStatus)ONS(LoOns[2].0)MSO({AX},{m}Mso);",
        f"[XIO(InEnable),XIC(InStop)]ONS(LoOns[2].1)MSF({AX},{m}Msf);",
        f"XIC(InReset)ONS(LoOns[2].2)[MAFR({AX},{m}Mafr),MASR({AX},{m}Masr)];",
        f"XIC(InHome)XIO(InTqHome)ONS(LoOns[2].3)MAH({AX},{m}Mah);",
        f"[XIC(InJogF),XIC(InJogR)]ONS(LoOns[2].4)MAJ({AX},{m}Maj,{m}D01,InSpd,Units per sec,InAcc,"
        f"Units per sec2,InDec,Units per sec2,S-Curve,100,100,% of Maximum,Disabled,Programmed,0,None);",
        f"XIC(InAuto)EQU({m}D02,1)ONS(LoOns[2].5)MAM({AX},{m}Mam1,0,{m}R04,InSpd,Units per sec,InAcc,"
        f"Units per sec2,InDec,Units per sec2,Trapezoidal,100,100,% of Maximum,Disabled,Programmed,0,"
        f"None,0,0);",
        f"XIC(InAuto)EQU({m}D02,2)ONS(LoOns[2].6)MAM({AX},{m}Mam2,1,{m}R05,{m}R06,Units per sec,{m}R07,"
        f"Units per sec2,{m}R07,Units per sec2,S-Curve,{m}R08,{m}R08,% of Maximum,Enabled,Programmed,0,"
        f"None,0,0);",
        f"[XIC(InStop),XIO(InJogF)XIO(InJogR)XIC({m}Maj.IP)]ONS(LoOns[2].7)MAS({AX},{m}Mas1,Jog,Yes,"
        f"InDec,Units per sec2,No,100,% of Time);",
        f"XIC(InHold)ONS(LoOns[2].8)MAS({AX},{m}Mas2,All,Yes,InDec,Units per sec2,No,100,% of Time);",
        f"[XIC({m}Mso.ER),XIC({m}Maj.ER),XIC({m}Mam1.ER),XIC({m}Mam2.ER),XIC({m}Mah.ER)]OTE({w.b()});",
    ]


def _math(w: _Writes) -> list[str]:
    r = [f"XIC(InEnable)TON({t},?,?);" for t in LO_TMR[:3]]
    r += [f"XIC({SRV}.B0{k})TON({LO_TMR[3 + k]},?,?);" for k in range(3)]
    r += [
        f"XIC(LoT0.DN)[MOV(LoD10,LoT1.PRE),MOV(LoD11,LoT2.PRE)];",
        f"GRT(InSpd,0.0)[DIV(InSpd,LoR00,LoR10),MUL(LoR10,60.0,LoR11),DIV(LoR11,{SRV}.R09,LoR12)];",
        f"XIC(InEnable)[MUL(InAcc,LoR00,LoR13),DIV(LoR13,100.0,LoR14),ADD(LoR14,{SRV}.R10,LoR15),"
        f"SUB(LoR15,{SRV}.R11,LoR16)];",
        f"XIC(InEnable)[CPT(LoR17,(LoR04-LoR05)/LoR06*100.0),"
        f"CPT(LoR18,LoR07*LoR08/1000.0),CPT(LoR19,{SRV}.R12+{SRV}.R13*LoR09)];",
        f"LES(LoR17,{SRV}.R14)GEQ(LoR18,{SRV}.R15)OTE({w.b()});",
        f"XIC(InClrCnt)[COP(LoOns[0],LoD12,1),COP(LoOns[3],LoD13,1),CLR(LoD14)];",
        f"GRT({SRV}.R16,LoR19)[ADD(LoD15,1,LoD15),MOV(LoD15,{SRV}.D03)];",
    ]
    return r


def _jmp() -> list[str]:
    return [f"XIO(InEnable)JMP(LblSkip);",
            f"XIC(InBypass)JMP(LblSkip);",
            f"XIC(InEnable)XIO(InBypass)[MOV(InMode,LoD16),MOV(InCmd,{SRV}.D04)];",
            f"LBL(LblSkip)NOP();",
            f"XIC(InHold)JMP(LblEnd);",
            f"XIC(InAuto)MOV(InMode,{SRV}.D05);",
            f"LBL(LblEnd)NOP();"]


def _axmem(w: _Writes) -> list[str]:
    return [
        f"XIC({AX}.ServoActionStatus)XIC({AX}.DriveEnableStatus)XIO({AX}.PhysicalAxisFault)"
        f"OTE(OutReady);",
        f"[XIC({AX}.PhysicalAxisFault),XIC({AX}.ModuleFault),XIC({AX}.GuardFault),NEQ({AX}.AxisFault,0),NEQ({AX}.ModuleFaults,0)]"
        f"OTE(OutFault);",
        f"[XIC({AX}.MoveStatus),XIC({AX}.JogStatus),XIC({AX}.GearingStatus),XIC({AX}.AccelStatus)]"
        f"XIO({AX}.HomeInputStatus)OTE({w.b()});",
        f"XIC({AX}.AxisHomedStatus)[MOV({AX}.ActualPosition,{SRV}.R17),MOV({AX}.ActualVelocity,{SRV}.R18),"
        f"MOV({AX}.CommandVelocity,{SRV}.R19)];",
        f"XIO({AX}.VelocityStandstillStatus)TON(LoTv,?,?);",
        f"GRT({AX}.ActualVelocity,{SRV}.R20)LES({AX}.ActualPosition,{SRV}.R21)OTE({w.b()});",
        f"MOV({AX}.CIPAxisState,{SRV}.D06);",
    ]


def _nested(where: str) -> list[str]:
    inst = "LoHome" if where == "local" else f"{SRV}.Home"
    return [f"XIC(InTqHome)[MOV({SRV}.R22,{inst}.HmSpd),MOV(InAcc,{inst}.HmAcc)];",
            f"DxHome({inst},InTqHome,{SRV}.R03,{AX});",
            f"XIC({inst}.HmDone)OTL(LoB4);"]


def _blocks() -> dict[str, list[str]]:
    w = _Writes()
    return {"bits": _bits(w), "cmp": _cmp(w), "gsv": _gsv(), "ssv": _ssv(), "motion": _motion(w),
            "math": _math(w), "jmp": _jmp(), "axmem": _axmem(w), "nested": _nested("local")}


# --- assembly --------------------------------------------------------------------

def _dxaxis(name: str, body: list[str], home_storage: list[MemberSpec],
            servo_udt: str = "DxServo") -> tuple[str, list[MemberSpec]]:
    logic = "\n".join(rung_xml(k, r) for k, r in enumerate(body))
    return aoi_xml(
        name,
        input_params=[MemberSpec(n, "BOOL") for n in IN_BOOL] + [MemberSpec(n, "REAL") for n in IN_REAL]
                     + [MemberSpec(n, "DINT") for n in IN_DINT],
        output_params=[MemberSpec(n, "BOOL") for n in OUT_BOOL],
        inout_params=[MemberSpec(AX, "AXIS_CIP_DRIVE"), MemberSpec(SRV, servo_udt)],
        local_tags=[MemberSpec(n, "REAL") for n in LO_REAL] + [MemberSpec(n, "DINT") for n in LO_DINT]
                   + [predef_member(n, "TIMER") for n in LO_TMR] + [predef_member("LoTv", "TIMER")]
                   + [MemberSpec(n, "BOOL") for n in LO_BOOL] + [MemberSpec("LoOns", "DINT", dimension=4)]
                   + [predef_member("LoMi", "MOTION_INSTRUCTION"),
                      MemberSpec("LoHome", "DxHome", nested_members=tuple(home_storage))],
        logic_rungs_xml=logic,
        description="Drive-axis AOI: enable, jog, move, home-to-torque, axis attributes, faults.")


def _controller_twins(home_storage: list[MemberSpec]) -> list[str]:
    """Controller tags with the AOI's input/local names, so the body runs in a program routine."""
    t = [tag_xml(n, "BOOL") for n in IN_BOOL + OUT_BOOL + LO_BOOL]
    t += [tag_xml(n, "REAL") for n in IN_REAL + LO_REAL]
    t += [tag_xml(n, "DINT") for n in IN_DINT + LO_DINT]
    t += [tag_xml(n, "TIMER") for n in LO_TMR + ["LoTv"]]
    t += [tag_xml("LoOns", "DINT", (4,)), tag_xml("LoMi", "MOTION_INSTRUCTION"),
          tag_xml("LoHome", "DxHome", udt_members=home_storage)]
    return t


def _write(sample_id: str, what: str, *, body: list[str], prog_body: list[str] | None = None,
           second: bool = False) -> None:
    home_def, home_storage = _home_aoi()
    servo = _servo_members(home_storage)
    ax_def, ax_storage = _dxaxis("DxAxis", body, home_storage)
    aois = [home_def, ax_def]
    supply, converter = bus_supply_with_converter(name="PnBusSupply", address="192.168.1.10",
                                                  axis_name="PnBusAxis")
    drive = _drive_module_xml("PnDrive1", "2198-D032-ERS3", "false", address="192.168.1.20")
    tags = [_MOTION_GROUP_TAG_XML, converter, _axis_tag("PnAxisX", "PnDrive1:Ch1"),
            _axis_tag("PnAxisY", "PnDrive1:Ch3"),
            tag_xml("SrvX", "DxServo", udt_members=servo), tag_xml("SrvY", "DxServo", udt_members=servo),
            tag_xml("DxX", "DxAxis", udt_members=ax_storage), tag_xml("DxY", "DxAxis", udt_members=ax_storage)]
    tags += _controller_twins(home_storage)
    calls = ["DxAxis(DxX,PnAxisX,SrvX);", "DxAxis(DxY,PnAxisY,SrvY);"]
    if second:
        b_def, b_storage = _dxaxis("DxAxisB", body, home_storage)
        aois.append(b_def)
        tags += [tag_xml("SrvBX", "DxServo", udt_members=servo), tag_xml("SrvBY", "DxServo", udt_members=servo),
                 tag_xml("DxBX", "DxAxisB", udt_members=b_storage),
                 tag_xml("DxBY", "DxAxisB", udt_members=b_storage)]
        calls += ["DxAxisB(DxBX,PnAxisX,SrvBX);", "DxAxisB(DxBY,PnAxisY,SrvBY);"]
    rungs = calls + (prog_body or [])
    out = OUT_ROOT / f"{sample_id}.L5X"
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(
        tags_xml="\n".join(tags), extra_modules_xml="\n".join([supply, drive]),
        extra_datatypes_xml=udt_xml("DxServo", servo), extra_aoi_xml="\n".join(aois),
        extra_rungs_xml="\n".join(rung_xml(i, r) for i, r in enumerate(rungs))))
    predicted = write_sample(l5x, out)
    append_manifest_row(
        sample_id, f"OQ-AOICOMPLEX: {what}. Same definitions (DxHome, DxServo, DxAxis params/locals), "
                   f"instances, Kinetix axes and controller tags in every aoicx_* file; differenced "
                   f"against aoicx_n00.", CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,}; DxAxis {len(body)} rungs)")


def main() -> None:
    one = ["XIC(InEnable)OTE(OutReady);"]
    blocks = _blocks()
    _write("aoicx_n00", "control: DxAxis Logic is one rung", body=one)
    for key, rungs in blocks.items():
        _write(f"aoicx_{key}", f"DxAxis Logic = the `{key}` block only ({len(rungs)} rungs)", body=rungs)
    _write("aoicx_nested_udt", "DxAxis Logic = DxHome called on the servo UDT's DxHome member "
           "(the real arrangement) instead of a DxAxis local", body=_nested("udt"))
    full = [r for rungs in blocks.values() for r in rungs]
    _write("aoicx_full", f"DxAxis Logic = every block together ({len(full)} rungs); full - n00 vs the "
           f"sum of the block files", body=full)
    _write("aoicx_full_prog", "DxAxis Logic one rung; the full body in MainRoutine on same-named "
           "controller tags -- AOI-internal vs program cost of the same content", body=one, prog_body=full)
    _write("aoicx_full_two", "aoicx_full plus a second definition DxAxisB with the same full body and "
           "its own two instances and servo tags", body=full, second=True)


if __name__ == "__main__":
    main()
