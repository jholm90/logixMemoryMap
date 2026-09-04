"""Instructions whose call shape James verified by hand, 2026-09-04.

James built a project containing every one of these instructions, got it to
BUILD CLEAN in Studio 5000, exported it, and handed the export over
(samples/local/instr_probes/instruction_shapes_20260904.L5X). Every rung
template below is copied operand-for-operand from that export. Nothing here
is composed from a manual.

That distinction has cost this project real time three separate times --
invented alarm ConditionTypes (all four rejected), the bare 2-operand
MAM/MAJ/MAS/MRP rungs (built as MAH/MSO's shape, failed every rung), the
Kinetix `:SI` safety tags (Studio synthesises those itself). So the rule
here is transplant, never compose: the rung strings and the backing tag XML
(sample_gen/verified_tags.py) both come out of James's file verbatim.

Two instructions from that export are deliberately NOT generated, per James
2026-09-04:
  NXT   -- "NXT not valid instruction". It is not a Logix RLL mnemonic at
           all; it appears in his scratch file but never built as one.
  MCLM  -- "skip the MCLM". Coordinated linear move; James excluded it.

Axis choice, James 2026-09-04: "note i used virtual axis and not the
hardware, but any AXIS_** type tag should work. i dont know if you are
aware of the difference between them." AXIS_VIRTUAL has no drive or module
binding, so a file built on it measures the instruction and nothing else --
there is no module connection overhead to subtract back out. That is
strictly better for cost isolation than AXIS_CIP_DRIVE, which is what
gen_motion_instructions.py uses and why those files always needed the
module baseline netted off first.

Run: python -m sample_gen.gen_verified_instructions
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row
from sample_gen.builders import rungs_xml
from sample_gen.verified_tags import tags
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "verified_instr"

# Three counts so a per-instruction cost can be fitted as a slope and the
# file/shell baseline falls out as the intercept, instead of being assumed.
COUNTS = [10, 100, 1000]

# (mnemonic, rung text, tags the rung references) -- rung text verbatim from
# James's verified export, tag names unchanged so the transplant stays exact.
_VERIFIED = [
    # --- no operands -------------------------------------------------------
    ("BRK", "BRK();", ()),

    # --- 2-operand transcendental / math (Src REAL -> Dst REAL) ------------
    ("COS", "COS(Src,Dst);", ("Src", "Dst")),
    ("LOG", "LOG(Src,Dst);", ("Src", "Dst")),
    ("SIN", "SIN(Src,Dst);", ("Src", "Dst")),

    # --- process control ---------------------------------------------------
    # PID's own backing tag is the first operand; PV/TIE/OUT are members of
    # it, so the tag pool is just the one PID structure.
    ("PID", "PID(PID,PID.PV,PID.TIE,PID.OUT,0,0,0);", ("PID",)),

    # --- file/array ---------------------------------------------------------
    # FBC: three DINT[10] arrays plus two CONTROL tags. The three `?` operands
    # are literally what Studio wrote for the unused/optional positions --
    # kept as-is rather than "helpfully" filling them in.
    ("FBC", "FBC(DINT_Arr1[0],DINT_Arr2[0],DINT_Arr3[0],CmpCtrl,?,?,ResultCtrl,?,?);",
     ("DINT_Arr1", "DINT_Arr2", "DINT_Arr3", "CmpCtrl", "ResultCtrl")),

    # --- string -------------------------------------------------------------
    ("STOR", "STOR(String,Dst);", ("String", "Dst")),

    # --- motion, single virtual axis ---------------------------------------
    ("MCD", "MCD(Axis1,MCD,Jog,No,Src,No,Src,No,Src,No,Src,No,Src,"
            "Units per sec,Units per sec2,Units per sec2,Units per sec3);",
     ("Axis1", "MCD", "Src")),

    # --- motion, coordinate system ------------------------------------------
    ("MCS", "MCS(CoordinateSystem1,MCS,All,No,Src,Units per sec2,No,Src,Units per sec3);",
     ("CoordinateSystem1", "MCS", "Src")),

    # --- motion, cam profile -------------------------------------------------
    ("MCSV", "MCSV(MCSV,Cam_Profile,Src,Dst,Dst,Dst);",
     ("MCSV", "Cam_Profile", "Src", "Dst")),

    # --- motion, TWO axes (slave, master) -----------------------------------
    # The only two-axis shape in the set -- this is exactly the structure
    # gen_motion_instructions.py refused to guess at ("MAG needs a MASTER and
    # a SLAVE axis"). Now it doesn't have to guess.
    ("MAG", "MAG(Axis2,Axis1,MAG,dint,Src,dint,dint,Actual,Real,Disabled,Src,Units per sec2);",
     ("Axis2", "Axis1", "MAG", "dint", "Src")),
]


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    written = 0
    for mnemonic, rung_text, tag_names in _VERIFIED:
        tags_xml = tags(*tag_names) if tag_names else ""
        for n in COUNTS:
            rungs = rungs_xml(n, lambda i, t=rung_text: t)
            l5x = build_l5x(
                target_name=f"{mnemonic}N{n}",
                tags_xml=tags_xml,
                extra_rungs_xml=rungs,
            )
            out_name = f"verifinstr_{mnemonic.lower()}_n{n:05d}"
            out_path = OUT_ROOT / f"{out_name}.L5X"
            lint_or_raise(l5x, context=str(out_path))
            out_path.write_text(l5x, encoding="utf-8")
            append_manifest_row(
                out_name,
                f"{n} rungs of {rung_text[:-1]} -- call shape VERBATIM from James's "
                f"2026-09-04 verified build-clean export (virtual axis, no module binding)",
                "verified_instr",
                out_path,
                0,
            )
            written += 1
            print(f"Wrote {out_path}")
    print(f"\nDone. {written} files ({len(_VERIFIED)} instructions x {len(COUNTS)} counts).")


if __name__ == "__main__":
    main()
