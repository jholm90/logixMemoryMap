"""Instructions this engine charges ZERO bytes for, but that appear in real files.

James, 2026-09-05: *"you can do the generation for unweighted instructions.
MCSV is a motion instruction so be cautious it will need an axis... just
like the MAJ MSF etc."*

The coverage audit (sizing/coverage.py) found 38 distinct mnemonics used in
real files with no weight in `logic_instructions.weights`, so every one of
them is priced at 0. On the 8 real programs that is a real, one-directional
under-prediction: RET alone appears 267 times across 17 files, SBR 150
across 14.

EVERY OPERAND SHAPE BELOW IS COPIED FROM A REAL CALL SITE in samples/local/,
with the corpus example quoted per instruction. None is composed from the
manual. That rule is not decoration -- the last two batches that invented a
shape (ST condition types, a 55-char HMIGroup) both came back rejected by
real Studio 5000, and this project has burned real bench time on it twice.

Motion instructions (MSF/MAW/MAR/MDR) are NOT here -- they need a real axis
and belong with the other axis files, so they were added to
gen_motion_instructions.py instead, which already has the proven
AXIS_CIP_DRIVE + MOTION_INSTRUCTION machinery. Its docstring records which
motion instructions were deliberately left out and what structure each would
need (MAG a master+slave pair, MCS/MCLM a COORDINATE_SYSTEM, MCSV a cam
profile pair).

NOT GENERATED, and honestly so -- no real call site exists in the corpus, so
the shape would have to be invented: BRK, NXT, COS, LOG, SIN, PID, FBC,
STOR. SIN/COS/LOG do appear in the corpus but only inside Structured Text,
never in a rung, so a rung sweep cannot reach them.

Run: python -m sample_gen.gen_unweighted_instructions
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import control_tag_xml, rung_xml, string_array_tag_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
COUNTS = (10, 100, 1000)   # same ladder shape as the instr_*_n* sweep

# mnemonic -> (rung text, the REAL corpus call it was copied from)
_INSTRUCTIONS = {
    "AND": ("AND(D0,D1,D2);",
            "AND(FillErrorBins[0],ChangedErrorBins[0],NewErrorBins[0])"),
    "OR": ("OR(D0,D1,D2);",
           "OR(WasteWoodNE,WasteWoodFE,WasteWood)"),
    "DTR": ("DTR(D0,-1,D1);",
            "DTR(THG._2_RxAsyncBuf.HeartbeatCounter,-1,THGComms_RxAsync_Buf_HeartbeatCounter)"),
    "UPPER": ("UPPER(STR0,STR1);",
              "UPPER(gAccess.UserNew.Name,gAccess.UserNew.Name)"),
    "RTOS": ("RTOS(R0,STR0);",
             "RTOS(jsonRealValue1,jsonValue1)"),
    "SCP": ("SCP(R0,R1,R2,R3,R4,R5);",
            "SCP(SCL_FunctionTorque,Local:5:I.Ch00.Data,SCL_FunctionTorque.Scaled)"),
    "LFU": ("LFU(ARR0[0],ARR0[11],CTRL0,?,?);",
            "LFU(ProcessPart_ID[0],ProcessPart_ID[11],ProcessPartControl,?,?)"),
}

_POOL = "\n".join([
    *(tag_xml(f"D{i}", "DINT") for i in range(4)),
    *(tag_xml(f"R{i}", "REAL") for i in range(6)),
    *(tag_xml(f"B{i}", "BOOL") for i in range(3)),
    tag_xml("ARR0", "DINT", dimensions=(20,)),
    control_tag_xml("CTRL0", length=12, position=0),
    string_array_tag_xml("STRPOOL", 2),
    tag_xml("STR0", "STRING", string_max_len=82),
    tag_xml("STR1", "STRING", string_max_len=82),
])


def _write(out_name: str, l5x: str, description: str, category: str = "logic_instr") -> None:
    out_path = OUT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, category, out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_plain_instructions() -> None:
    for mnemonic, (text, corpus) in _INSTRUCTIONS.items():
        for n in COUNTS:
            rungs = "\n".join(rung_xml(i, text) for i in range(n))
            l5x = build_l5x(target_name=f"Unw{mnemonic}", tags_xml=_POOL, extra_rungs_xml=rungs)
            _write(f"unweighted_{mnemonic.lower()}_n{n:05d}", l5x,
                   f"{n} rungs of {mnemonic} alone against a fixed tag pool -- same ladder shape "
                   f"as the instr_*_n* sweep so the per-rung weight falls straight out of the "
                   f"n=10 vs n=100 vs n=1000 differences. {mnemonic} currently has NO weight in "
                   f"logic_instructions.weights, so this engine charges it 0 bytes everywhere it "
                   f"appears in a real file. Operand shape copied from a REAL call site in "
                   f"samples/local/, not composed from the manual: {corpus}")


def group_sbr_ret_ladder() -> None:
    """RET (267 uses across 17 real files) and SBR (150 across 14) are the
    two most-used unweighted instructions by a wide margin. Neither can be
    swept in a plain rung -- they only exist inside a JSR target -- so this
    varies the TARGET count and keeps one SBR/RET pair per target, making
    the per-pair cost the slope against the already-exact +344/target."""
    for n in (1, 10, 50, 200):
        routines, calls = [], []
        for t in range(n):
            name = f"SubTgt{t:03d}"
            body = rung_xml(0, "SBR(D0)NOP();") + rung_xml(1, "RET(D1);")
            routines.append(f'<Routine Name="{name}" Type="RLL"><RLLContent>{body}</RLLContent></Routine>')
            calls.append(rung_xml(t, f"JSR({name},1,D0,D1);"))
        l5x = build_l5x(target_name=f"UnwSbrRet{n:03d}", tags_xml=_POOL,
                        extra_rungs_xml="\n".join(calls), extra_routines_xml="".join(routines))
        _write(f"unweighted_sbrret_t{n:03d}", l5x,
               f"{n} JSR target(s), each containing exactly one SBR/RET pair "
               f"(SBR(D0)NOP(); RET(D1);). RET and SBR are the two most-used unweighted "
               f"instructions in the real corpus by a wide margin -- RET 267 uses across 17 "
               f"files, SBR 150 across 14 -- and both are charged 0 today. They cannot be swept "
               f"in a plain rung because they only exist inside a JSR target, so target count is "
               f"the variable and the per-pair cost is the slope above the already-exact 344 "
               f"bytes per distinct target (realscale_jsrsplit_k*). SBR carries the NOP "
               f"terminator it needs -- see docs/SAMPLE_GENERATION.md.",
               category="jsr_sbr_ret")


def main() -> None:
    group_plain_instructions()
    group_sbr_ret_ladder()
    print(f"\nDone. {len(_INSTRUCTIONS) * len(COUNTS) + 4} files.")


if __name__ == "__main__":
    main()
