"""OQ-SMALLINSTR: small instructions weighted only on near-empty files, on the realism floor.

Real use, seventeen programs: NOP 4,785, RES 957, CTU 876, AFI 627, GSV 521 (108 into a UDT
member), timers with literal presets. Their weights come from near-empty calibration files
(NOP 16, CTU 20, RES 20, AFI 4, GSV 84) and have never been checked on a full controller.

One inventory (BOOL/DINT/COUNTER/TIMER arrays of 400, a UDT array), 400 rungs per file, every
output written once; control `smallin_n00`. 1756-L81E at v35.

Run: python -m sample_gen.gen_small_instr
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "smallin"
CATEGORY = "small_instr"
N = 400
_UDT = [MemberSpec("D", "DINT"), MemberSpec("R", "REAL")]


def _inventory() -> dict[str, str]:
    tags = [tag_xml("SmC", "BOOL", (N,)), tag_xml("SmQ", "BOOL", (N,)), tag_xml("SmD", "DINT", (N,)),
            tag_xml("SmCt", "COUNTER", (N,)), tag_xml("SmT", "TIMER", (N,)),
            tag_xml("SmU", "SmUdt", (N,), udt_members=_UDT)]
    return {"tags_xml": "\n".join(tags), "extra_datatypes_xml": udt_xml("SmUdt", _UDT)}


FILES = {
    "nop": (lambda i: f"XIC(SmC[{i}])NOP();", "XIC then NOP"),
    "ctu": (lambda i: f"XIC(SmC[{i}])CTU(SmCt[{i}],?,?);", "XIC then CTU on a COUNTER array element"),
    "res": (lambda i: f"XIC(SmC[{i}])RES(SmCt[{i}]);", "XIC then RES of a COUNTER array element"),
    "afi": (lambda i: f"AFI()OTE(SmQ[{i}]);", "AFI then OTE"),
    "ote": (lambda i: f"XIC(SmC[{i}])OTE(SmQ[{i}]);", "XIC then OTE -- reference for nop/afi"),
    "gsv_dint": (lambda i: f"GSV(Task,MainTask,LastScanTime,SmD[{i}]);", "GSV a task attribute into a DINT array element"),
    "gsv_udtmem": (lambda i: f"GSV(Task,MainTask,LastScanTime,SmU[{i}].D);", "GSV a task attribute into a DINT member of a UDT element"),
    "ton_q": (lambda i: f"XIC(SmC[{i}])TON(SmT[{i}],?,?);", "TON with ? presets -- the timer control"),
    "ton_lit": (lambda i: f"XIC(SmC[{i}])TON(SmT[{i}],5000,0);", "TON with literal preset 5000 and accum 0; vs smallin_ton_q"),
}


def main() -> None:
    inv = _inventory()

    def write(sample_id: str, rungs: list[str], what: str) -> None:
        out = OUT_ROOT / f"{sample_id}.L5X"
        body = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))
        target = "".join(p.capitalize() for p in sample_id.split("_"))
        l5x = build_l5x(target_name=target, **with_baseline(extra_rungs_xml=body, **inv))
        predicted = write_sample(l5x, out)
        append_manifest_row(sample_id, f"OQ-SMALLINSTR: {what}. Same inventory in every smallin_* file, realism "
                                       f"floor; differenced against smallin_n00.", CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")

    write("smallin_n00", [], "control, no added rungs")
    for key, (fn, what) in FILES.items():
        rungs = [fn(i) for i in range(N)]
        write(f"smallin_{key}", rungs, f"{N} rungs `{rungs[1]}` -- {what}")


if __name__ == "__main__":
    main()
