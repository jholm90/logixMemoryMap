"""OQ-AOILITARG: what an AOI Input argument costs when its type differs from the parameter's.

AOI call arguments are measured on BOOL and DINT parameters only (`litop_bool_*`): an Input
argument costs 28 as a tag or the literal 12345 and 16 as the literal 0 or 1. Typed calls
convert a literal or a mismatched tag into the call's type (OQ-LITREAL); an AOI call copies
each Input argument into its parameter, so the same conversion may apply. Real Input
arguments, seventeen programs: REAL parameter <- integer literal 1,133, <- float literal 56,
<- DINT tag 12; INT/SINT parameters <- literal handful.

One AOI `LitArgs` with four Required Input parameters (InR REAL, InD DINT, InI INT, InS SINT)
and a BOOL Output; 400 instances `LaI###`, one call each; source tags LaR/LaD/LaI/LaS of the
four types. Exactly one argument differs from the all-tag control between files.

  aoilit_n00         AOI, instances and source tags, no calls -- control
  aoilit_tag         LitArgs(LaI###,LaR,LaD,LaI,LaS)       every argument its own type
  aoilit_r_ilit5     InR <- 5          integer literal into REAL
  aoilit_r_ilit0     InR <- 0          the 'cheap' literal into REAL
  aoilit_r_flit      InR <- 5.0        float literal into REAL
  aoilit_r_dint      InR <- LaD        DINT tag into REAL
  aoilit_i_ilit      InI <- 5          integer literal into INT
  aoilit_s_ilit      InS <- 5          integer literal into SINT
  aoilit_d_ilit      InD <- 12345      integer literal into DINT (litop_bool says +0 vs a tag)

1756-L81E at v35, realism floor.

Run: python -m sample_gen.gen_aoi_literal_args
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoilit"
CATEGORY = "aoi_literal_arg"
N = 400

PARAMS = [MemberSpec("InR", "REAL", required=True, visible=True),
          MemberSpec("InD", "DINT", required=True, visible=True),
          MemberSpec("InI", "INT", required=True, visible=True),
          MemberSpec("InS", "SINT", required=True, visible=True)]
TAGS = ["LaR", "LaD", "LaI", "LaS"]
CASES = {
    "tag": ({}, "every argument a tag of its parameter's type -- the control"),
    "r_ilit5": ({0: "5"}, "InR (REAL) given the integer literal 5"),
    "r_ilit0": ({0: "0"}, "InR (REAL) given the literal 0, the cheap literal on BOOL/DINT"),
    "r_flit": ({0: "5.0"}, "InR (REAL) given the float literal 5.0"),
    "r_dint": ({0: "LaD"}, "InR (REAL) given the DINT tag LaD"),
    "i_ilit": ({2: "5"}, "InI (INT) given the integer literal 5"),
    "s_ilit": ({3: "5"}, "InS (SINT) given the integer literal 5"),
    "d_ilit": ({1: "12345"}, "InD (DINT) given the literal 12345 -- litop_bool measured +0 against a tag"),
}


def _aoi() -> tuple[str, list[MemberSpec]]:
    return aoi_xml(
        "LitArgs", input_params=PARAMS, output_params=[MemberSpec("Sts", "BOOL")],
        logic_rungs_xml=('<Rung Number="0" Type="N"><Text><![CDATA[GRT(InR,InD)OTE(Sts);]]></Text></Rung>'),
        description="Four typed Required inputs: what an argument of another type costs at the call.")


def _write(sample_id: str, rungs: list[str], description: str, tags: str, aoi: str) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    body = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(tags_xml=tags, extra_rungs_xml=body,
                                                        extra_aoi_xml=aoi))
    predicted = write_sample(l5x, out)
    append_manifest_row(
        sample_id, f"OQ-AOILITARG: {description}. Same AOI, 400 instances and source tags in every "
                   f"aoilit_* file; exactly one argument differs from aoilit_tag.",
        CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


def main() -> None:
    aoi, storage = _aoi()
    tags = "\n".join([tag_xml(f"LaI{i:03d}", "LitArgs", udt_members=storage) for i in range(N)]
                     + [tag_xml(n, t) for n, t in zip(TAGS, ("REAL", "DINT", "INT", "SINT"))])
    _write("aoilit_n00", [], "control: AOI definition, instances and source tags, no calls", tags, aoi)
    for key, (subst, what) in CASES.items():
        args = [subst.get(k, TAGS[k]) for k in range(4)]
        rungs = [f"LitArgs(LaI{i:03d},{','.join(args)});" for i in range(N)]
        _write(f"aoilit_{key}", rungs, f"{N} calls `{rungs[1]}` -- {what}", tags, aoi)


if __name__ == "__main__":
    main()
