"""OQ-MOTIONLIT: the literal law on MAJ, MAPC, MCCP and MAG.

MAM and MAS follow the typed-call literal law exactly (`realidiom_mam_*`, `_mas_*`): an
integer literal in a REAL parameter costs 52 for the first and 44 for each further one, a
float literal 4 more than a REAL tag; keywords, DINT parameters, axis type and the
event-distance / calculated-data arrays cost nothing. Real integer literals in the other
motion instructions: MAPC 1,009, MAJ 188, MCCP 155, MAG 136.

Every file carries the motop inventory (captured, `motop_n00`): the realism plant, a
2198-P208 bus supply with its converter axis, one 2198-D032-ERS3, CIP axes PnAxisX /
PnAxisY on its channels, four AXIS_VIRTUAL, 400 scalar MOTION_INSTRUCTION tags -- plus a
CAM[5] and a CAM_PROFILE[5] for MAPC and MCCP, so the control is `motlit_n00`. 400 calls
per file, one MOTION_INSTRUCTION each, slave/axis alternating PnAxisX / PnAxisY, master a
virtual axis. Signatures are the captured-clean ones (`motioninstr_maj`,
`instrfirst_mapc_v2`, `instrfirst_mccp`, `verifinstr_mag`), operands retargeted.

For each instruction, `_tag` holds every REAL parameter as a REAL tag (the control),
`_ilit` the same positions as integer literals, `_flit` as float literals. The expected
cost per call over `_tag` is written in each description BEFORE capture; the engine does
not yet apply the law to these instructions.

1756-L81E at v35.

Run: python -m sample_gen.gen_motion_literals
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import cam_profile_tag_xml, cam_tag_xml, rung_xml
from sample_gen.gen_motion_operands import _inventory as motop_inventory
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "motlit"
CATEGORY = "motion_literal"
N = 400
FIRST, NEXT, FLOAT = 52, 44, 4  # the measured law (memory_model.yaml operand_type_surcharge.mixed)


def _law(n_int: int, n_float: int = 0) -> int:
    return (FIRST + NEXT * (n_int - 1) if n_int else 0) + FLOAT * n_float


def _inventory() -> dict[str, str]:
    inv = dict(motop_inventory())
    inv["tags_xml"] += "\n" + cam_tag_xml("MlCam", 5) + "\n" + cam_profile_tag_xml("MlProf", 5)
    return inv


def _ax(i: int) -> str:
    return ("PnAxisX", "PnAxisY")[i % 2]


def _master(i: int) -> str:
    return ("MoV1", "MoV2", "MoV3", "MoV4")[i % 4]


def _mi(i: int) -> str:
    return f"MoMiS{i:03d}"


# Each builder takes (i, values) where values fills the instruction's REAL parameters in order.
def _maj(i, v):  # REAL: speed, accel, decel, accel jerk, decel jerk, lock position
    return (f"MAJ({_ax(i)},{_mi(i)},MoA[{i}],{v[0]},Units per sec,{v[1]},Units per sec2,{v[2]},"
            f"Units per sec2,S-Curve,{v[3]},{v[4]},% of Maximum,Disabled,Programmed,{v[5]},None);")


def _mapc(i, v):  # REAL: slave scaling, master scaling, master lock position, cam lock position
    return (f"MAPC({_ax(i)},{_master(i)},{_mi(i)},0,MlProf[0],{v[0]},{v[1]},Once,Forward Only,"
            f"{v[2]},{v[3]},New Cam,Command,Bi-Directional);")


def _mccp(i, v):  # REAL: start slope, end slope (length 2 is a DINT literal in every file)
    return f"MCCP({_mi(i)},MlCam[0],2,{v[0]},{v[1]},MlProf[0]);"


def _mag(i, v):  # REAL: ratio, accel (direction and the two counts are DINT tags)
    return (f"MAG({_ax(i)},{_master(i)},{_mi(i)},MoA[{i}],{v[0]},MoB[{i}],MoE[{i}],Actual,Real,"
            f"Disabled,{v[1]},Units per sec2);")


TAGS = [f"MoRef{k}.R" for k in range(1, 7)]
INSTR = {
    # name: (builder, REAL tags, integer literals, float literals)
    "maj": (_maj, TAGS[:5] + ["MoK"], ["100", "200", "200", "75", "75", "0"],
            ["100.0", "200.0", "200.0", "75.0", "75.0", "0.0"]),
    "mapc": (_mapc, TAGS[:4], ["1", "1", "0", "0"], ["1.0", "1.0", "0.0", "0.0"]),
    "mccp": (_mccp, TAGS[:2], ["1", "1"], ["1.0", "1.0"]),
    "mag": (_mag, TAGS[:2], ["1", "100"], ["1.0", "100.0"]),
}


def _write(sample_id: str, rungs: list[str], description: str, inv: dict[str, str]) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    body = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(extra_rungs_xml=body, **inv))
    predicted = write_sample(l5x, out)
    append_manifest_row(sample_id, f"OQ-MOTIONLIT: {description}", CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


def main() -> None:
    inv = _inventory()
    _write("motlit_n00", [], "control: motop inventory + MlCam CAM[5] + MlProf CAM_PROFILE[5], no "
           "added rungs; every motlit_* file differences against it", inv)
    for name, (build, tags, ilits, flits) in INSTR.items():
        n = len(tags)
        for form, vals, expect in (("tag", tags, 0), ("ilit", ilits, _law(n)), ("flit", flits, _law(0, n))):
            rungs = [f"XIC(MoC[{i}])" + build(i, vals) for i in range(N)]
            what = {"tag": f"every REAL parameter a REAL tag -- the control for motlit_{name}_*",
                    "ilit": f"the {n} REAL parameters as integer literals; expected +{expect} per call "
                            f"over motlit_{name}_tag (52 + 44 x {n - 1})",
                    "flit": f"the {n} REAL parameters as float literals; expected +{expect} per call "
                            f"over motlit_{name}_tag (4 x {n})"}[form]
            _write(f"motlit_{name}_{form}", rungs, f"{N} rungs `{rungs[1]}` -- {what}", inv)
    # The old litop_mam shape, on the realism floor: virtual axis, % of Maximum, Trapezoidal,
    # Disabled/Current, literal move type and tail -- reads 12/call over on a near-empty file.
    shapes = {
        "mam_tag": ("MAM({ax},{mi},MoA[{i}],MoRef1.R,MoRef2.R,Units per sec,MoRef3.R,Units per sec2,"
                    "MoRef4.R,Units per sec2,S-Curve,MoRef5.R,MoRef6.R,% of Maximum,Enabled,Programmed,"
                    "MoK,None,MoDst[0],MoDst[1]);",
                    "the captured-exact realidiom_mam_tag shape on this inventory -- the MAM control"),
        "mam_litop": ("MAM({vx},{mi},1,MoRef1.R,MoRef2.R,% of Maximum,MoRef3.R,% of Maximum,MoRef3.R,"
                      "% of Maximum,Trapezoidal,MoRef4.R,MoRef4.R,% of Maximum,Disabled,Current,0,None,0,0);",
                      "the old litop_mam_tag shape (virtual axis, % of Maximum, Trapezoidal, Disabled, "
                      "Current, literal tail); expected +52 per call over motlit_mam_tag (one REAL literal: "
                      "the lock position) -- litop_mam_tag on a near-empty file read 40"),
    }
    for key, (tpl, what) in shapes.items():
        rungs = [f"XIC(MoC[{i}])" + tpl.format(ax=_ax(i), vx=_master(i), mi=_mi(i), i=i) for i in range(N)]
        _write(f"motlit_{key}", rungs, f"{N} rungs `{rungs[1]}` -- {what}", inv)


if __name__ == "__main__":
    main()
