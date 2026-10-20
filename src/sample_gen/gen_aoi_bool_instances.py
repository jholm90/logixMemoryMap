"""OQ-AOIBOOLINST: what a scalar AOI instance with many BOOL members costs.

`aoiint_n00` (an AOI with 55 BOOL members, 50 scalar instances) reads 12,198 under the
engine before any logic. The engine prices a SCALAR instance's BOOL parameters and locals
at 4 bytes each, while an instance ARRAY packs them into 32-bit words with EnableIn and
EnableOut (aoi_array, measured on 48 families). Packing the scalar instances the same way
accounts for 10,600 of the 12,198; what the rest is -- a per-instance slot, an alignment,
or the BOOL-heavy definition -- is what this batch separates.

One AOI `BoolInst`: Inputs InB (BOOL), InD (DINT), InR (REAL); Output Sts (BOOL); Local
LoD (DINT); and k BOOL locals, so k + 4 BOOL bits with EnableIn / EnableOut. 1756-L81E v35
on the realism floor, no logic, no calls; instance names of one length.

  aoibool_k<k>_def        the definition alone (k = 0, 28, 29, 55, 60, 61: 4, 32, 33, 59,
                          64, 65 bits -- one, one, two, two, two, three words)
  aoibool_k<k>_n01        one scalar instance
  aoibool_k<k>_n50        fifty scalar instances
  aoibool_k55_n25         the middle point (linearity)
  aoibool_k55_arr50       one BoolInst[50] array: ties the scalar law to the measured array law
  aoibool_p55_n01 / _n50  the 55 BOOLs as Input parameters instead of locals

Differenced against each other: def against `realism_base_f25`, n01 against def, n50 and
n25 against n01.

Run: python -m sample_gen.gen_aoi_bool_instances
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "aoibool"
CATEGORY = "aoi"
OQ = "OQ-AOIBOOLINST"
AOI = "BoolInst"
KS = (0, 28, 29, 55, 60, 61)


def definition(k: int, as_params: bool = False) -> tuple[str, list[MemberSpec]]:
    bools = [MemberSpec(f"Bk{i:02d}", "BOOL") for i in range(k)]
    inputs = [MemberSpec("InB", "BOOL", visible=True), MemberSpec("InD", "DINT", visible=True),
              MemberSpec("InR", "REAL", visible=True)] + (bools if as_params else [])
    locals_ = [MemberSpec("LoD", "DINT")] + ([] if as_params else bools)
    return aoi_xml(AOI, input_params=inputs, output_params=[MemberSpec("Sts", "BOOL")], local_tags=locals_)


def plan() -> list[tuple[str, dict, str]]:
    files: list[tuple[str, dict, str]] = []
    for k in KS:
        bits = k + 4
        words = -(-bits // 32)
        what = f"{k} BOOL locals ({bits} BOOL bits with EnableIn/EnableOut, {words} word(s))"
        files.append((f"aoibool_k{k:02d}_def", {"k": k, "n": 0}, f"the AOI definition alone, {what}"))
        files.append((f"aoibool_k{k:02d}_n01", {"k": k, "n": 1}, f"one scalar instance, {what}"))
        files.append((f"aoibool_k{k:02d}_n50", {"k": k, "n": 50}, f"fifty scalar instances, {what}"))
    files.append(("aoibool_k55_n25", {"k": 55, "n": 25}, "twenty-five scalar instances, 55 BOOL locals (linearity)"))
    files.append(("aoibool_k55_arr50", {"k": 55, "arr": 50}, "one 50-element instance array, 55 BOOL locals"))
    files.append(("aoibool_p55_n01", {"k": 55, "n": 1, "params": True}, "one scalar instance, the 55 BOOLs as Input parameters"))
    files.append(("aoibool_p55_n50", {"k": 55, "n": 50, "params": True}, "fifty scalar instances, the 55 BOOLs as Input parameters"))
    return files


def make(sample_id: str, kw: dict) -> str:
    aoi, storage = definition(kw["k"], kw.get("params", False))
    if "arr" in kw:
        tags = [tag_xml("BiArr", AOI, (kw["arr"],), udt_members=storage)]
    else:
        tags = [tag_xml(f"BiI{i:02d}", AOI, udt_members=storage) for i in range(kw["n"])]
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    return build_l5x(target_name=target, **with_baseline(tags_xml="\n".join(tags), extra_aoi_xml=aoi))


def main() -> None:
    for sample_id, kw, what in plan():
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make(sample_id, kw), out)
        append_manifest_row(sample_id, f"{OQ}: AOI {AOI} (InB, InD, InR in; Sts out; LoD local), {what}; no logic, "
                                       f"no calls; realism floor, 1756-L81E v35. def against realism_base_f25, n01 "
                                       f"against def, n25 / n50 / arr50 against n01.", CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    main()
