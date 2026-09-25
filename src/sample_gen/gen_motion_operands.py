"""OQ-MOTIONOP and OQ-DENSERUNG: motion-system operands, and dense real-shaped rungs.

Plant + export 27's worst program, one routine removed per file, read short of
the engine on every routine (6.8%-38.6%); the two rungs isolated from it (Studio-made,
one rung kept per routine) read short by 144 of 712 and 252 of 2,484. A two-feature fit
over the seven routines points at operands that live in the motion system -- axis
attributes (`Axis.ActualPosition`, `Axis.VelocityStandstillStatus`) and
MOTION_INSTRUCTION members (`Mam.DN`, `OTU(Mah.PC)`) -- but seven points cannot tell a
motion premium from the rung density those routines also carry (530-680 instructions
per 100 rungs against the plant's 249). This batch separates the two.

Every file is the captured-exact `l9v38_m_kinetix_l8v35` content (realism plant, a
2198-P208 bus supply with its converter axis, one 2198-D032-ERS3, axes PnAxisX/PnAxisY)
plus ONE shared inventory -- four AXIS_VIRTUAL, MOTION_INSTRUCTION and TIMER tags as
scalars, arrays and UDT members, and the plain tags the controls read -- so every file
differences against `motop_n00` and against its paired control with the tags held fixed.
Only the rungs vary.

  axr_*   axis REAL attribute as a source (MOV, GRT, LIM, SUB) against the same rung
          reading a REAL member of a plain UDT tag (`MoRef1.R`); CIP vs virtual axis,
          one axis vs two, ActualPosition vs CommandVelocity, 100 vs 400 rungs.
  axb_*   axis BOOL attribute in XIC/XIO against a BOOL member and a bit of a DINT
          member (`MoRef1.W.5`) -- whether a status bit costs like a word read.
  mi_*    MOTION_INSTRUCTION .DN/.IP/.PC/... read (XIC) and written (OTU), as a scalar
          tag, an array element and a UDT member, each against the same rung on a
          TIMER in the same position (TIMER's EN/TT/DN are bits of its control word,
          exactly as MI's are bits of FLAGS, and TIMER is priced exact), plus a bit of a
          DINT array element.
  dens_*  one heterogeneous unit (a condition, a compare, a writer) at 1, 4, 16 and 64
          per rung in series, 4 and 16 as branch legs, 16 nested -- the same 1,600 units
          in every file, so the residual against dens_ser_k01 is what packing real-
          density rungs costs beyond the series law.

Every output bit is written once. 1756-L81E at v35.

NO REAL-RUNG TEMPLATES. Rebuilding an isolated real rung's structure over synthetic
tags is content derived from a customer export and may not be written under
samples/generated/ (CLAUDE.md, repository rules); a real rung shape is measured only
from a variant Studio itself produced.

Run: python -m sample_gen.gen_motion_operands
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml
from sample_gen.gen_axis_marginal import _virtual_axis_tag
from sample_gen.gen_module_motion import (
    _MOTION_GROUP_TAG_XML, _axis_tag, _drive_module_xml, bus_supply_with_converter,
)
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "motop"
CATEGORY = "motion_operand"

N = 400          # rungs in an isolation file
CELLS = 100      # per-copy UDT tags for the templates
UNITS = 1600     # density units per dens_* file
CIP = ("PnAxisX", "PnAxisY")
VIRT = ("MoV1", "MoV2", "MoV3", "MoV4")
MI_SLOTS = ("Srv", "Mah", "Mam", "Mas")          # MOTION_INSTRUCTION members of MoCell
TMR_SLOTS = ("SrvT", "MahT", "MamT", "MasT")     # the TIMER member in the same position

_CELL_MEMBERS = (
    [MemberSpec(n, "DINT") for n in ("Seq", "Att", "Lim", "Err", "Req", "Inc", "Ons",
                                     "N2", "N4", "N6")]
    + [MemberSpec(n, "REAL") for n in ("D2", "D4", "D6", "A2", "A4", "A6",
                                       "MinP", "MaxP", "MaxCL")]
    + [MemberSpec("NC", "BOOL"), MemberSpec("Eye", "BOOL")]
    + [MemberSpec(n, "MOTION_INSTRUCTION") for n in MI_SLOTS]
    + [MemberSpec(n, "TIMER") for n in TMR_SLOTS + ("Tmr",)]
)
_REF_MEMBERS = [MemberSpec("B1", "BOOL"), MemberSpec("B2", "BOOL"), MemberSpec("B3", "BOOL"),
                MemberSpec("R", "REAL"), MemberSpec("W", "DINT")]


def _cell(c: int) -> str:
    return f"MoCell{c:03d}"


def _inventory() -> dict[str, str]:
    supply, converter = bus_supply_with_converter(
        name="PnBusSupply", address="192.168.1.10", axis_name="PnBusAxis")
    drive = _drive_module_xml("PnDrive1", "2198-D032-ERS3", "false", address="192.168.1.20")
    tags = [_MOTION_GROUP_TAG_XML, converter,
            _axis_tag("PnAxisX", "PnDrive1:Ch1"), _axis_tag("PnAxisY", "PnDrive1:Ch3")]
    tags += [_virtual_axis_tag(v) for v in VIRT]
    tags += [tag_xml(f"MoRef{k}", "MoRef") for k in range(1, 7)]
    tags += [tag_xml(_cell(c), "MoCell") for c in range(CELLS)]
    tags += [tag_xml("MoMi", "MOTION_INSTRUCTION", (N,)), tag_xml("MoTm", "TIMER", (N,))]
    tags += [tag_xml(f"MoMiS{i:03d}", "MOTION_INSTRUCTION") for i in range(N)]
    tags += [tag_xml(f"MoTmS{i:03d}", "TIMER") for i in range(N)]
    tags += [tag_xml("MoDw", "DINT", (N,)), tag_xml("MoDst", "REAL", (N,)),
             tag_xml("MoK", "REAL"), tag_xml("MoLo", "REAL"), tag_xml("MoHi", "REAL")]
    tags += [tag_xml("MoC", "BOOL", (UNITS,)), tag_xml("MoQ", "BOOL", (UNITS,))]
    tags += [tag_xml(n, "DINT", (UNITS,)) for n in ("MoA", "MoB", "MoE")]
    return {
        "tags_xml": "\n".join(tags),
        "extra_modules_xml": "\n".join([supply, drive]),
        "extra_datatypes_xml": "\n".join([udt_xml("MoRef", _REF_MEMBERS),
                                          udt_xml("MoCell", _CELL_MEMBERS)]),
    }


# --- isolation rungs ---------------------------------------------------------

def _axr(src, shape: str) -> list[str]:
    """Axis REAL attribute (or its control) as a source, one reference per rung
    except sub2 (two)."""
    out = []
    for i in range(N):
        x = src(i)
        out.append({
            "mov": f"MOV({x},MoDst[{i}]);",
            "grt": f"GRT({x},MoK)OTE(MoQ[{i}]);",
            "lim": f"LIM(MoLo,{x},MoHi)OTE(MoQ[{i}]);",
            "sub1": f"SUB({x},MoRef2.R,MoDst[{i}]);",
        }[shape] if shape != "sub2" else f"SUB({x[0]},{x[1]},MoDst[{i}]);")
    return out


def _xic(src, n: int = N) -> list[str]:
    return [f"XIC({src(i)})OTE(MoQ[{i}]);" for i in range(n)]


def _xio(src) -> list[str]:
    return [f"XIO({src(i)})OTE(MoQ[{i}]);" for i in range(N)]


def _otu(dst) -> list[str]:
    return [f"XIC(MoC[{i}])OTU({dst(i)});" for i in range(N)]


_MI_BITS = ("EN", "DN", "ER", "PC", "IP")


def _isolation() -> dict[str, tuple[list[str], str]]:
    s: dict[str, tuple[list[str], str]] = {}
    ref2 = lambda i: f"MoRef{1 + i % 2}.R"  # noqa: E731
    cip_pos = lambda i: f"{CIP[i % 2]}.ActualPosition"  # noqa: E731
    virt_pos = lambda i: f"{VIRT[i % 4]}.ActualPosition"  # noqa: E731

    s["axr_mov_ref_n400"] = (_axr(ref2, "mov"), "control: MOV(MoRef{1,2}.R, MoDst[i]) -- a REAL member of a plain UDT tag")
    s["axr_mov_cip_n400"] = (_axr(cip_pos, "mov"), "MOV(PnAxis{X,Y}.ActualPosition, MoDst[i]) -- CIP axis REAL attribute; vs axr_mov_ref_n400")
    s["axr_mov_cip_n100"] = (_axr(cip_pos, "mov")[:100], "as axr_mov_cip_n400 at 100 rungs: a per-reference cost scales by 4")
    s["axr_mov_cip1_n400"] = (_axr(lambda i: "PnAxisX.ActualPosition", "mov"), "as axr_mov_cip_n400 but every rung reads ONE axis: per-reference vs per-distinct-axis")
    s["axr_mov_virt_n400"] = (_axr(virt_pos, "mov"), "MOV(MoV{1..4}.ActualPosition, MoDst[i]) -- AXIS_VIRTUAL attribute; vs axr_mov_ref_n400 and axr_mov_cip_n400")
    s["axr_mov_cipvel_n400"] = (_axr(lambda i: f"{CIP[i % 2]}.CommandVelocity", "mov"), "MOV(PnAxis{X,Y}.CommandVelocity, ...) -- whether the attribute matters; vs axr_mov_cip_n400")
    s["axr_grt_ref_n400"] = (_axr(ref2, "grt"), "control: GRT(MoRef{1,2}.R, MoK) OTE(MoQ[i])")
    s["axr_grt_cip_n400"] = (_axr(cip_pos, "grt"), "GRT(PnAxis{X,Y}.ActualPosition, MoK) OTE(MoQ[i]); vs axr_grt_ref_n400")
    s["axr_grt_virt_n400"] = (_axr(virt_pos, "grt"), "GRT(MoV{1..4}.ActualPosition, MoK) OTE(MoQ[i]); vs axr_grt_ref_n400")
    s["axr_lim_ref_n400"] = (_axr(ref2, "lim"), "control: LIM(MoLo, MoRef{1,2}.R, MoHi) OTE(MoQ[i])")
    s["axr_lim_cip_n400"] = (_axr(cip_pos, "lim"), "LIM(MoLo, PnAxis{X,Y}.ActualPosition, MoHi) OTE(MoQ[i]); vs axr_lim_ref_n400")
    s["axr_sub2_ref_n400"] = (_axr(lambda i: ("MoRef1.R", "MoRef2.R"), "sub2"), "control: SUB(MoRef1.R, MoRef2.R, MoDst[i])")
    s["axr_sub2_cip_n400"] = (_axr(lambda i: ("PnAxisX.ActualPosition", "PnAxisY.ActualPosition"), "sub2"), "SUB(PnAxisX.ActualPosition, PnAxisY.ActualPosition, MoDst[i]) -- two axis references per call; vs axr_sub2_ref_n400")
    s["axr_sub1_cip_n400"] = (_axr(lambda i: "PnAxisX.ActualPosition", "sub1"), "SUB(PnAxisX.ActualPosition, MoRef2.R, MoDst[i]) -- one of two; with sub2_* gives per-reference vs per-call")

    s["axb_xic_ref_n400"] = (_xic(lambda i: f"MoRef{1 + i % 2}.B1"), "control: XIC(MoRef{1,2}.B1) OTE(MoQ[i]) -- a BOOL member")
    s["axb_xic_wbit_n400"] = (_xic(lambda i: f"MoRef{1 + i % 2}.W.5"), "control: XIC(MoRef{1,2}.W.5) -- a bit of a DINT member, the 'whole DINT' hypothesis")
    s["axb_xic_cip_n400"] = (_xic(lambda i: f"{CIP[i % 2]}.AxisHomedStatus"), "XIC(PnAxis{X,Y}.AxisHomedStatus) OTE(MoQ[i]); vs axb_xic_ref_n400 and axb_xic_wbit_n400")
    s["axb_xic_cip_n100"] = (_xic(lambda i: f"{CIP[i % 2]}.AxisHomedStatus", 100), "as axb_xic_cip_n400 at 100 rungs")
    s["axb_xic_cipvss_n400"] = (_xic(lambda i: f"{CIP[i % 2]}.VelocityStandstillStatus"), "XIC(PnAxis{X,Y}.VelocityStandstillStatus) -- a second status attribute; vs axb_xic_cip_n400")
    s["axb_xio_cip_n400"] = (_xio(lambda i: f"{CIP[i % 2]}.AxisHomedStatus"), "XIO(PnAxis{X,Y}.AxisHomedStatus) -- XIO against axb_xic_cip_n400")
    s["axb_xic_virt_n400"] = (_xic(lambda i: f"{VIRT[i % 4]}.AxisHomedStatus"), "XIC(MoV{1..4}.AxisHomedStatus) -- virtual axis; vs axb_xic_cip_n400")

    s["mi_xic_tmr_arr_n400"] = (_xic(lambda i: f"MoTm[{i}].DN"), "control: XIC(MoTm[i].DN) -- TIMER array element status bit")
    s["mi_xic_mi_arr_n400"] = (_xic(lambda i: f"MoMi[{i}].DN"), "XIC(MoMi[i].DN) -- MOTION_INSTRUCTION array element; vs mi_xic_tmr_arr_n400")
    s["mi_xic_mi_arr_n100"] = (_xic(lambda i: f"MoMi[{i}].DN", 100), "as mi_xic_mi_arr_n400 at 100 rungs")
    s["mi_xic_mibits_arr_n400"] = (_xic(lambda i: f"MoMi[{i}].{_MI_BITS[i % 5]}"), "XIC(MoMi[i].{EN,DN,ER,PC,IP}) cycling -- whether the bit matters; vs mi_xic_mi_arr_n400")
    s["mi_xic_dw_arr_n400"] = (_xic(lambda i: f"MoDw[{i}].1"), "control: XIC(MoDw[i].1) -- a bit of a DINT array element, the 'whole DINT' hypothesis")
    s["mi_xic_tmr_sc_n400"] = (_xic(lambda i: f"MoTmS{i:03d}.DN"), "control: XIC(MoTmS###.DN) -- scalar TIMER")
    s["mi_xic_mi_sc_n400"] = (_xic(lambda i: f"MoMiS{i:03d}.DN"), "XIC(MoMiS###.DN) -- scalar MOTION_INSTRUCTION, the dominant real form; vs mi_xic_tmr_sc_n400")
    s["mi_xic_tmr_udt_n400"] = (_xic(lambda i: f"{_cell(i % CELLS)}.{TMR_SLOTS[i // CELLS]}.DN"), "control: XIC(MoCell###.{SrvT,...}.DN) -- TIMER member of a UDT tag")
    s["mi_xic_mi_udt_n400"] = (_xic(lambda i: f"{_cell(i % CELLS)}.{MI_SLOTS[i // CELLS]}.DN"), "XIC(MoCell###.{Srv,Mah,Mam,Mas}.DN) -- MOTION_INSTRUCTION member of a UDT tag (the real `Cell.Servo.MAH.PC` shape); vs mi_xic_tmr_udt_n400")
    s["mi_otu_tmr_arr_n400"] = (_otu(lambda i: f"MoTm[{i}].DN"), "control: XIC(MoC[i]) OTU(MoTm[i].DN)")
    s["mi_otu_mi_arr_n400"] = (_otu(lambda i: f"MoMi[{i}].DN"), "XIC(MoC[i]) OTU(MoMi[i].DN); vs mi_otu_tmr_arr_n400")
    s["mi_otu_tmr_sc_n400"] = (_otu(lambda i: f"MoTmS{i:03d}.DN"), "control: XIC(MoC[i]) OTU(MoTmS###.DN)")
    s["mi_otu_mi_sc_n400"] = (_otu(lambda i: f"MoMiS{i:03d}.DN"), "XIC(MoC[i]) OTU(MoMiS###.DN) -- the real OTU-on-MI shape; vs mi_otu_tmr_sc_n400")
    s["mi_otu_tmr_udt_n400"] = (_otu(lambda i: f"{_cell(i % CELLS)}.{TMR_SLOTS[i // CELLS]}.DN"), "control: XIC(MoC[i]) OTU(MoCell###.{SrvT,...}.DN)")
    s["mi_otu_mi_udt_n400"] = (_otu(lambda i: f"{_cell(i % CELLS)}.{MI_SLOTS[i // CELLS]}.DN"), "XIC(MoC[i]) OTU(MoCell###.{Srv,...}.DN); vs mi_otu_tmr_udt_n400")
    return s


# --- density -----------------------------------------------------------------

def _unit(j: int) -> str:
    if j % 2 == 0:
        return f"XIC(MoC[{j}])GRT(MoA[{j}],MoB[{j}])MOV(MoA[{j}],MoE[{j}])"
    return f"XIO(MoC[{j}])LES(MoA[{j}],MoB[{j}])OTE(MoQ[{j}])"


def _density() -> dict[str, tuple[list[str], str]]:
    s: dict[str, tuple[list[str], str]] = {}
    unit_doc = ("unit j = XIC/XIO(MoC[j]) GRT/LES(MoA[j],MoB[j]) MOV(MoA[j],MoE[j]) or OTE(MoQ[j]), "
                f"{UNITS} units in every dens_* file")
    for k in (1, 4, 16, 64):
        s[f"dens_ser_k{k:02d}"] = (
            ["".join(_unit(r * k + j) for j in range(k)) + ";" for r in range(UNITS // k)],
            f"{UNITS // k} rungs of {k} unit(s) in series ({unit_doc})"
            + ("; the control" if k == 1 else "; vs dens_ser_k01"))
    for k in (4, 16):
        s[f"dens_br_k{k:02d}"] = (
            ["[" + ",".join(_unit(r * k + j) for j in range(k)) + "];" for r in range(UNITS // k)],
            f"{UNITS // k} rungs of {k} branch legs, one unit per leg ({unit_doc}); vs dens_ser_k01")

    def nest(b: int) -> str:
        legs = []
        for g in range(4):
            u = b + 4 * g
            legs.append(_unit(u) + "[" + ",".join(_unit(u + j) for j in (1, 2, 3)) + "]")
        return "[" + ",".join(legs) + "];"
    s["dens_nest_k16"] = ([nest(r * 16) for r in range(UNITS // 16)],
                          f"{UNITS // 16} rungs: 4 legs, each a unit then a 3-leg branch of units -- "
                          f"16 units, branches nested two deep ({unit_doc}); vs dens_ser_k01")
    return s


# --- write ---------------------------------------------------------------------

def _write(sample_id: str, rungs: list[str], description: str, inventory: dict[str, str],
           oq: str) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    body = "\n".join(rung_xml(i, t) for i, t in enumerate(rungs))
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(extra_rungs_xml=body, **inventory))
    predicted = write_sample(l5x, out)
    append_manifest_row(
        sample_id,
        f"{oq}: {description}. Plant + the l9v38_m_kinetix Kinetix block + the shared motop "
        f"inventory, identical in every motop_* file; only the rungs differ, so the residual "
        f"against motop_n00 and against the paired control is the rungs' own under- or "
        f"over-charge.",
        CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


def main() -> None:
    inv = _inventory()
    _write("motop_n00", [], "control, no added rungs", inv, "OQ-MOTIONOP/OQ-DENSERUNG")
    for stem, (rungs, what) in _isolation().items():
        _write(f"motop_{stem}", rungs, what, inv, "OQ-MOTIONOP")
    for stem, (rungs, what) in _density().items():
        _write(f"motop_{stem}", rungs, what, inv, "OQ-DENSERUNG")


if __name__ == "__main__":
    main()
