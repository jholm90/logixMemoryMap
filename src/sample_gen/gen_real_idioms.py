"""OQ-REALIDIOM: features real ladder carries at real density that no realism file has.

After OQ-LITREAL and the motion-structure types, plant + real program transplants
still read 2.6-7.7% of their added logic short, and five of seven routines removed
from export 27's worst program read 200-650 bytes short each. Against the realism
plant (the base of every batch since the realism floor), real ladder differs in:

  rungs per routine           real 16.7            plant ~97
  ONS / OTL / OTU targets     bits of DINT words   BOOL members only
  motion instructions         literal tails        none
                              (`...,0,None,0,0`), jerk `75,75`, move type `1`

Nothing here copies real ladder: every rung is built from the standard instruction
signatures over synthetic tags. Three arms, 1756-L81E at v35, realism floor.

GRANULARITY (`realidiom_gran_spr{01,02,05,10,20}`): the plant alone, the same 12,800
rungs cut into routines of 1, 2, 5, 10 (the standard plant) and 20 stations -- 10 to
200 rungs per routine, each routine called by its own JSR. spr10 is the standard plant
under another name (control; `realism_base_f25` reads -1,794). The per-routine and
per-JSR constants were measured on near-empty files; this checks them at real
granularity.

BIT TARGETS (`realidiom_bit_<instr>_<target>`): plant + 800 rungs `XIC(IdC[i])<instr>(t)`
(ONS adds `OTE(IdQ[i])`), each target written once, for instr in ONS, OTL, OTU, OTE and
target in: `mbool` a BOOL member (`IdU07.B12`), `dbit` a bit of a scalar DINT tag
(`IdD07.12`), `abit` a bit of a DINT array element (`IdW[7].12`), `mbit` a bit of a DINT
member (`IdU07.W.12`). Same inventory in all; control `realidiom_bit_n00`.

MOTION (`realidiom_mam_*`, `realidiom_mas_*`): the motop inventory (captured, `motop_n00`
+1,330) plus 400 calls, one MOTION_INSTRUCTION each (`MoMiS###`), alternating PnAxisX /
PnAxisY. `mam_tag` is the captured-exact `motioninstr_mam` shape (every numeric operand
a tag); each other file changes one thing toward the real idiom, and `mam_real` changes
all of them.

Run: python -m sample_gen.gen_real_idioms
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml
from sample_gen.gen_motion_operands import _inventory as motop_inventory
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "realidiom"
CATEGORY = "real_idiom"
N_BITS = 800
WORDS = N_BITS // 32
N_MOTION = 400

_IDU_MEMBERS = [MemberSpec(f"B{j}", "BOOL") for j in range(32)] + [MemberSpec("W", "DINT")]


def _write(sample_id: str, description: str, oq: str, stations_per_routine: int = 10, **arm) -> None:
    out = OUT_ROOT / f"{sample_id}.L5X"
    target = "".join(p.capitalize() for p in sample_id.split("_"))
    l5x = build_l5x(target_name=target, **with_baseline(stations_per_routine=stations_per_routine, **arm))
    predicted = write_sample(l5x, out)
    append_manifest_row(sample_id, f"{oq}: {description}", CATEGORY, out, predicted)
    print(f"Wrote {out.name} (predicted {predicted:,})")


# --- granularity ---------------------------------------------------------------

def granularity() -> None:
    for spr in (1, 2, 5, 10, 20):
        _write(f"realidiom_gran_spr{spr:02d}",
               f"the realism plant alone, 1,280 stations cut {spr} per routine ({10 * spr} rungs per "
               f"routine, one JSR each)" + (" -- the standard plant, control" if spr == 10 else
                                            "; vs realidiom_gran_spr10 (real ladder: 16.7 rungs per routine)"),
               "OQ-REALIDIOM", stations_per_routine=spr, tags_xml="")


# --- bit targets ---------------------------------------------------------------

def _bit_inventory() -> dict[str, str]:
    tags = [tag_xml("IdC", "BOOL", (N_BITS,)), tag_xml("IdQ", "BOOL", (N_BITS,)),
            tag_xml("IdW", "DINT", (WORDS,))]
    tags += [tag_xml(f"IdD{k:02d}", "DINT") for k in range(WORDS)]
    tags += [tag_xml(f"IdU{k:02d}", "IdUdt") for k in range(WORDS)]
    return {"tags_xml": "\n".join(tags), "extra_datatypes_xml": udt_xml("IdUdt", _IDU_MEMBERS)}


_TARGETS = {
    "mbool": (lambda k, j: f"IdU{k:02d}.B{j}", "a BOOL member of a UDT tag"),
    "dbit": (lambda k, j: f"IdD{k:02d}.{j}", "a bit of a scalar DINT tag"),
    "abit": (lambda k, j: f"IdW[{k}].{j}", "a bit of a DINT array element"),
    "mbit": (lambda k, j: f"IdU{k:02d}.W.{j}", "a bit of a DINT member of a UDT tag"),
}


def bit_targets() -> None:
    inv = _bit_inventory()
    _write("realidiom_bit_n00", "control: plant + the bit-target inventory, no added rungs",
           "OQ-REALIDIOM", **inv)
    for instr in ("OTE", "ONS", "OTL", "OTU"):
        for key, (target, what) in _TARGETS.items():
            rungs = []
            for i in range(N_BITS):
                t = target(i // 32, i % 32)
                rungs.append(f"XIC(IdC[{i}])ONS({t})OTE(IdQ[{i}]);" if instr == "ONS"
                             else f"XIC(IdC[{i}]){instr}({t});")
            body = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))
            _write(f"realidiom_bit_{instr.lower()}_{key}",
                   f"{N_BITS} rungs `{rungs[37]}` -- {instr} on {what}, each target written once; "
                   f"vs realidiom_bit_{instr.lower()}_mbool and realidiom_bit_n00",
                   "OQ-REALIDIOM", extra_rungs_xml=body, **inv)


# --- motion --------------------------------------------------------------------

def _mam(i: int, *, move="MoA[{i}]", dyn=("MoRef1.R", "MoRef2.R", "MoRef3.R", "MoRef4.R"),
         units=("Units per sec", "Units per sec2", "Units per sec2"), profile="S-Curve",
         jerk=("MoRef5.R", "MoRef6.R"), jerk_units="% of Maximum", merge="Enabled",
         merge_speed="Programmed", tail=("MoK", "MoDst[0]", "MoDst[1]"), axis=None) -> str:
    ax = axis(i) if axis else ("PnAxisX", "PnAxisY")[i % 2]
    pos, spd, acc, dec = dyn
    return (f"MAM({ax},MoMiS{i:03d},{move.format(i=i)},{pos},{spd},{units[0]},{acc},{units[1]},{dec},"
            f"{units[2]},{profile},{jerk[0]},{jerk[1]},{jerk_units},{merge},{merge_speed},{tail[0]},None,"
            f"{tail[1]},{tail[2]});")


_MAM_VARIANTS = {
    "tag": ({}, "every numeric operand a tag, move type a DINT tag -- the captured-exact "
                "motioninstr_mam shape; the control for every mam_* file"),
    "tail0": ({"tail": ("0", "0", "0")}, "lock position, event distance and calculated data as the "
                                         "literal 0 -- the real `...,Programmed,0,None,0,0)` tail"),
    "jerk75": ({"jerk": ("75", "75")}, "accel and decel jerk as the literal 75 -- the real `S-Curve,75,75` form"),
    "move1": ({"move": "1"}, "move type as the literal 1"),
    "dynilit": ({"dyn": ("100", "50", "200", "200")}, "position, speed, accel and decel as integer literals"),
    "dynflit": ({"dyn": ("100.0", "50.0", "200.0", "200.0")}, "position, speed, accel and decel as float literals"),
    "virtual": ({"axis": lambda i: ("MoV1", "MoV2", "MoV3", "MoV4")[i % 4]}, "a virtual axis instead of a CIP axis"),
    "keywords": ({"units": ("% of Maximum",) * 3, "profile": "Trapezoidal", "merge": "Disabled",
                  "merge_speed": "Current"}, "keyword operands changed: % of Maximum, Trapezoidal, Disabled, Current"),
    "real": ({"move": "1", "jerk": ("75", "75"), "merge": "Disabled", "tail": ("0", "0", "0")},
             "all the real idioms together: `MAM(Ax,Mi,1,Pos,Spd,Units per sec,Acc,Units per sec2,Dec,"
             "Units per sec2,S-Curve,75,75,% of Maximum,Disabled,Programmed,0,None,0,0)`"),
}


def motion() -> None:
    inv = motop_inventory()
    for key, (kw, what) in _MAM_VARIANTS.items():
        rungs = [f"XIC(MoC[{i}])" + _mam(i, **kw) for i in range(N_MOTION)]
        body = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))
        _write(f"realidiom_mam_{key}",
               f"motop inventory + {N_MOTION} rungs `{rungs[1]}` -- {what}"
               + ("" if key == "tag" else "; vs realidiom_mam_tag") + "; control motop_n00",
               "OQ-REALIDIOM", extra_rungs_xml=body, **inv)
    mas = {
        "tag": ("MAS({ax},MoMiS{i:03d},All,Yes,MoRef4.R,Units per sec2,Yes,MoRef5.R,% of Time);",
                "decel and jerk as REAL tags"),
        "lit": ("MAS({ax},MoMiS{i:03d},All,Yes,50,Units per sec2,Yes,75,% of Maximum);",
                "decel 50 and jerk 75 as integer literals -- the common real form; vs realidiom_mas_tag"),
    }
    for key, (tpl, what) in mas.items():
        rungs = [f"XIC(MoC[{i}])" + tpl.format(ax=("PnAxisX", "PnAxisY")[i % 2], i=i) for i in range(N_MOTION)]
        body = "\n".join(rung_xml(i, r) for i, r in enumerate(rungs))
        _write(f"realidiom_mas_{key}", f"motop inventory + {N_MOTION} rungs `{rungs[1]}` -- {what}; control motop_n00",
               "OQ-REALIDIOM", extra_rungs_xml=body, **inv)


def main() -> None:
    granularity()
    bit_targets()
    motion()


if __name__ == "__main__":
    main()
