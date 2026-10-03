"""OQ-AOIINTERNAL: AOI-internal logic written the way real AOIs write it.

AOI-internal logic is ~2 MB of the seventeen real programs' predicted memory, and in the
category scale test it is the noisy half of the logic gap (+51% ±37 alone, +12% jointly
with program logic). Real AOIs operate on their parameters -- often InOut UDTs and axes,
which are references to the caller's tag, not copies -- while every AOI calibration file
ran simple logic on Input and Local members.

One AOI `AiOps` per file with the same 50 rungs of
`XIC(b)GRT(d,r)MOV(d,LoDst)ADD(d,1,LoAcc)OTE(Qk)`, where (b, d, r) are:

  aoiint_in      Input parameters  InB, InD, InR
  aoiint_local   Local tags        LoB, LoD, LoR
  aoiint_inout   InOut UDT members IoU.B, IoU.D, IoU.R
  aoiint_axis    InOut AXIS_VIRTUAL IoAx.AxisHomedStatus (b), Local LoD (d), IoAx.ActualPosition (r)
  aoiint_eif     aoiint_local plus 10-rung EnableInFalse and Prescan routines
  aoiint_i50     aoiint_local with 50 instances and 50 calls instead of 1

and `aoiint_n00` the same AOI with one rung. Every file declares the same tags (instances,
the UDT tag, a virtual axis in a motion group); one call per instance from MainRoutine.
1756-L81E at v35, realism floor. Logic is charged once per definition, so aoiint_i50 minus
aoiint_local is 49 x (instance + call).

Run: python -m sample_gen.gen_aoi_internal_shape
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml, udt_xml
from sample_gen.gen_axis_marginal import _virtual_axis_tag
from sample_gen.gen_module_motion import _MOTION_GROUP_TAG_XML
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoiint"
CATEGORY = "aoi_internal_shape"
RUNGS = 50
_UDT = [MemberSpec("D", "DINT"), MemberSpec("R", "REAL"), MemberSpec("B", "BOOL")]
OPS = {
    "in": ("InB", "InD", "InR"),
    "local": ("LoB", "LoD", "LoR"),
    "inout": ("IoU.B", "IoU.D", "IoU.R"),
    "axis": ("IoAx.AxisHomedStatus", "LoD", "IoAx.ActualPosition"),
}


def _rungs(n: int, ops: tuple[str, str, str]) -> str:
    b, d, r = ops
    return "\n".join(rung_xml(k, f"XIC({b})GRT({d},{r})MOV({d},LoDst)ADD({d},1,LoAcc)OTE(Q{k:02d});")
                     for k in range(n))


def _aoi(logic: str, eif: str = "", prescan: str = "") -> tuple[str, list[MemberSpec]]:
    return aoi_xml(
        "AiOps",
        input_params=[MemberSpec("InB", "BOOL", visible=True), MemberSpec("InD", "DINT", visible=True),
                      MemberSpec("InR", "REAL", visible=True)],
        output_params=[MemberSpec("Sts", "BOOL")],
        inout_params=[MemberSpec("IoU", "AiUdt"), MemberSpec("IoAx", "AXIS_VIRTUAL")],
        local_tags=[MemberSpec("LoB", "BOOL"), MemberSpec("LoD", "DINT"), MemberSpec("LoR", "REAL"),
                    MemberSpec("LoDst", "DINT"), MemberSpec("LoAcc", "DINT")]
                   + [MemberSpec(f"Q{k:02d}", "BOOL") for k in range(RUNGS)],
        logic_rungs_xml=logic, enable_in_false_rungs_xml=eif, prescan_rungs_xml=prescan,
        description="Real-shape AOI logic over Input, Local, InOut-UDT and InOut-axis operands.")


def _write(sample_id: str, aoi: str, storage: list[MemberSpec], instances: int, what: str) -> None:
    tags = [_MOTION_GROUP_TAG_XML, _virtual_axis_tag("AiAx"), tag_xml("AiU", "AiUdt", udt_members=_UDT)]
    tags += [tag_xml(f"AiI{i:02d}", "AiOps", udt_members=storage) for i in range(50)]
    calls = "\n".join(rung_xml(i, f"AiOps(AiI{i:02d},AiU,AiAx);") for i in range(instances))
    out = OUT_ROOT / f"{sample_id}.L5X"
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(
        tags_xml="\n".join(tags), extra_datatypes_xml=udt_xml("AiUdt", _UDT), extra_aoi_xml=aoi,
        extra_rungs_xml=calls))
    predicted = write_sample(l5x, out)
    append_manifest_row(sample_id, f"OQ-AOIINTERNAL: {what}. Same tags (50 AiOps instances, AiU, virtual "
                                   f"axis AiAx) in every aoiint_* file; differenced against aoiint_n00.",
                        CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


def main() -> None:
    one = rung_xml(0, "XIC(LoB)OTE(Q00);")
    aoi, st = _aoi(one)
    _write("aoiint_n00", aoi, st, 1, "control: AiOps with one rung, one call")
    for key, ops in OPS.items():
        aoi, st = _aoi(_rungs(RUNGS, ops))
        _write(f"aoiint_{key}", aoi, st, 1, f"AiOps with {RUNGS} rungs over {key} operands {ops}, one call")
    eif = "\n".join(rung_xml(k, f"XIC(LoB)MOV(LoD,LoDst)OTE(Sts);") if k == 0 else
                    rung_xml(k, f"XIC(LoB)ADD(LoD,{k},LoAcc);") for k in range(10))
    aoi, st = _aoi(_rungs(RUNGS, OPS["local"]), eif=eif, prescan=eif)
    _write("aoiint_eif", aoi, st, 1, "aoiint_local plus 10-rung EnableInFalse and Prescan routines")
    aoi, st = _aoi(_rungs(RUNGS, OPS["local"]))
    _write("aoiint_i50", aoi, st, 50, "aoiint_local called from 50 instances (50 calls); logic is charged once")


if __name__ == "__main__":
    main()
