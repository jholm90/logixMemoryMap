"""CPT operator-tier linearity confirmation (James, 2026-08-25): "whats
your CPT confidence? why is it not 100% yet? you need to generate tests
to satisfy this."

Mining the already-captured `cmpcpt_*` real data (gen_cmpcpt_layout.py,
27 real rows, all at n=1000) found real, clean-looking per-operator-tier
deltas -- ADD/SUB cost the same (+36/rung over a bare-copy baseline),
MUL/DIV cost the same (+52/rung), POW is its own tier (+116/rung) -- all
computed by direct subtraction between file variants sharing the exact
same tag pool, so the deltas are real regardless of what CPT's true
per-rung weight actually is. **But every one of those 27 rows is at the
SAME single rung count (1000)** -- there is no second count point
anywhere in the existing data to confirm these deltas are genuinely flat
per-rung rates, as opposed to some other shape that happens to look
linear at exactly one point. This project's own standing rule (don't wire
a formula off one data point) applies here just as much as anywhere else.

This file adds a SECOND count point (n=100) for the 4 shapes needed to
confirm (or refute) linearity for all 3 established tiers:
  - barecopy (CPT(L2,L0)) -- the zero-operator anchor
  - add (CPT(L2,L0+L1)) -- ADD/SUB tier
  - mul (CPT(L2,L0*L1)) -- MUL/DIV tier
  - pow (CPT(L2,L0**L1)) -- POW tier
Same tag pool as gen_cmpcpt_layout.py (identical DINT/REAL/BOOL tags) so
the n=1000 vs n=100 deltas isolate purely the rung-count effect, same
subtraction methodology already used throughout this project.

Separately, this data also revealed operand-TYPE effects that are NOT a
count-linearity question and are NOT addressed by this file: int-literal
operands show a flat +264 delta (same across all 5 operators, not yet
confirmed as truly rung-count-independent either) and float-literal
operands show an even more complex pattern (operator-independent for
ADD/SUB/MUL/DIV but not POW). Those need their own dedicated follow-up
once this file's linearity question is settled -- not attempted here to
keep this batch focused on one question at a time.

Run: python -m sample_gen.gen_cpt_confirm
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
RUNG_COUNT = 100

# Identical to gen_cmpcpt_layout.py's _POOL_TAGS_XML -- must match exactly
# for the n=1000 vs n=100 subtraction to isolate only the rung-count effect.
_POOL_TAGS_XML = (
    "\n".join(tag_xml(f"L{i}", "DINT") for i in range(8)) + "\n"
    + "\n".join(tag_xml(f"R{i}", "REAL") for i in range(3)) + "\n"
    + tag_xml("TB0", "BOOL")
)


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    fn_bare = lambda i: "CPT(L2,L0);"
    l5x = build_l5x(target_name="CptBareCopyN100", tags_xml=_POOL_TAGS_XML, extra_rungs_xml=rungs_xml(RUNG_COUNT, fn_bare))
    _write(l5x, f"cmpcpt_cpt_barecopy_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of CPT(L2,L0) -- bare copy, 2nd count point to confirm linearity vs the n=1000 point")

    for op, opname in [("+", "add"), ("*", "mul"), ("**", "pow")]:
        fn = lambda i, op=op: f"CPT(L2,L0{op}L1);"
        l5x = build_l5x(target_name=f"CptOperator{opname}N100", tags_xml=_POOL_TAGS_XML,
                         extra_rungs_xml=rungs_xml(RUNG_COUNT, fn))
        _write(l5x, f"cmpcpt_cpt_op_{opname}_n{RUNG_COUNT:05d}",
               f"{RUNG_COUNT} rungs of CPT(L2,L0{op}L1) -- 2nd count point to confirm the {opname.upper()} tier "
               f"delta over barecopy is truly linear per-rung, not just flat-looking at n=1000")

    print("\nDone. 4 files.")


if __name__ == "__main__":
    main()
