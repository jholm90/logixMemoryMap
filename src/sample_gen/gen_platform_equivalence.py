"""Is the 5069 platform's cost the SAME as 1756-L8x, at real content density?

OQ-REAL5069 said the 5069 platform had zero real-file validation. That is
now out of date -- four of the sixteen real captured programs are 5069:

    elmsdale       5069-L330ERM     fw35.05   -5.03%
    superior       5069-L330ERM     fw32.04   -4.00%
    salamanca      5069-L330ERM     fw35.05   +1.08%
    flarefunction  5069-L320ERMS3   fw35.05   -2.07%

and the platform breakdown is not flattering:

    1756-L81   n=7   median -0.88%   mean |err| 1.85%
    1756-L82   n=2   median -1.34%   mean |err| 1.34%
    1756-L83   n=3   median -2.41%   mean |err| 2.30%
    5069-L32   n=1   median -2.07%   mean |err| 2.07%
    5069-L33   n=3   median -4.00%   mean |err| 3.37%

5069-L330ERM is the worst-performing platform in the corpus and it
under-predicts on three files of four. So the question is no longer
"is 5069 validated" -- it is "what does 5069 cost that 1756 does not".

A per-platform baseline constant has been tried once and REJECTED, and
the rejection is the reason this batch is shaped the way it is.
memory_model.yaml records it: grouping the 190 captured fwmatrix baseline
files by processor and firmware produced a beautifully consistent matrix
across nine independent catalogs, wiring it took fwmatrix to 136 of 136
exact -- and simultaneously broke 612 previously-exact files, every one
landing on exactly the size of the correction. Those 612 are the SAME
catalog and firmware as the baseline files. The effect belonged to the
fwmatrix files' near-empty CONTENT, not to the processor, and fitting it
as a platform constant generalised a property of 190 nearly-identical
files onto everything sharing their catalog string.

That is exactly the trap this batch is built to avoid. Instead of one
near-empty file per platform, it emits IDENTICAL content on each platform
at five densities from empty to substantial. Differencing two platforms at
matched content answers the question the earlier attempt could not:

  - difference FLAT across all five densities  -> a real platform baseline
    constant, and the earlier fit failed only because it was measured at a
    single density.
  - difference GROWS with density              -> not a baseline at all but
    a per-something rate that differs by platform, and a constant would be
    the wrong shape however well it fitted one density.
  - difference ZERO                            -> the platform is not the
    cause and the 5069 real-file gap is content the model mis-prices that
    5069 programs happen to contain more of.

PLATFORM LINT EXEMPTION. sample_gen.lint normally requires every generated
file to be 1756-L81E at v35 so it differences cleanly against the ~2,500
existing captures. This batch is exempt for the same stated reason the
firmware/catalog matrix generators are: sweeping the processor IS the
variable under test here. The 1756-L81E arm is the control and stays on
the standard, so the batch still anchors to the rest of the corpus.
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, rung_xml, tag_xml, udt_xml
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row, predicted_bytes
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "platform"
CATEGORY = "platform"

# The control first. 5069-L330ERM is the real-corpus worst performer and
# 5069-L306ER is the smallest 5069 this project has real baseline data for,
# so a difference that is a platform property should appear on both.
PLATFORMS = (
    ("1756-L81E", "PlatEqL81", "the standard this whole corpus is built on -- the control"),
    ("5069-L330ERM", "PlatEqL330", "the real-corpus worst performer: 3 real files, median -4.00%"),
    ("5069-L306ER", "PlatEqL306", "a second 5069 catalog, so a difference can be shown to be a "
                                  "PLATFORM property rather than one catalog's own"),
)

# Empty through substantial. The earlier rejected fit had only the first
# of these, which is precisely why it generalised wrongly.
DENSITIES = (0, 25, 100, 400, 1600)

UDT_NAME = "PlatEqUdt"
_UDT_MEMBERS = [MemberSpec(f"Mbr{i:02d}", "DINT") for i in range(8)]


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    lint_or_raise(l5x, context=str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(l5x, encoding="utf-8")
    append_manifest_row(name, description, CATEGORY, out, predicted_bytes(l5x))
    print(f"Wrote {out}")


def _content(n: int) -> tuple[str, str, str]:
    """n units of mixed content: one UDT tag, one atomic tag and one rung
    each. Mixed on purpose -- a platform term could attach to data, to
    logic, or to neither, and a single-category payload could not tell
    those apart."""
    if not n:
        return "", "", rung_xml(0, "NOP();")
    tags = [tag_xml(f"PeUdt{i:04d}", UDT_NAME, udt_members=_UDT_MEMBERS) for i in range(n)]
    tags += [tag_xml(f"PeDint{i:04d}", "DINT") for i in range(n)]
    tags += [tag_xml("PeBit0", "BOOL"), tag_xml("PeBit1", "BOOL")]
    rungs = [rung_xml(i, f"XIC(PeBit0)MOV({i},PeDint{i:04d})OTE(PeBit1);") for i in range(n)]
    return "\n".join(tags), udt_xml(UDT_NAME, _UDT_MEMBERS), "\n".join(rungs)


def main() -> None:
    for processor, stem, why in PLATFORMS:
        for n in DENSITIES:
            tags, datatypes, rungs = _content(n)
            _write(
                build_l5x(
                    target_name=f"{stem}D{n:04d}",
                    tags_xml=tags,
                    processor_type=processor,
                    extra_datatypes_xml=datatypes,
                    extra_rungs_xml=rungs,
                ),
                f"platform_{stem.lower()}_d{n:04d}",
                f"{processor} carrying {n} content unit(s) -- each unit is one "
                f"{UDT_NAME} tag, one DINT tag and one rung, byte-identical "
                f"across all three platforms. Differencing this against the "
                f"1756-L81E file at the SAME density isolates what the platform "
                f"itself costs, at that density. Five densities because a "
                f"per-platform baseline was fitted once from near-empty files "
                f"alone and broke 612 previously-exact files: flat across "
                f"densities means a real constant, growing means a rate, zero "
                f"means the platform is not the cause. {why}. OQ-REAL5069.",
            )


if __name__ == "__main__":
    main()
