"""Produced and Consumed tags -- the last real tag shapes with zero coverage.

The tag survey behind OQ-TAGSHAPE compared 31,532 real tags against 91,641
corpus tags over 3,479 captured files and found the corpus covers every real
tag shape except three: Produced (0.11% of real tags), Consumed (0.06%) and
2-D arrays (0.16%). The 2-D case is covered by the rshape_sub2d ladder; these
two files close the other two.

THIS IS COMPLETENESS, NOT A RESIDUAL HUNT, and the entry says so plainly:
0.33% of real tags at 84 bytes of flat base each is roughly 8,700 bytes
against a residual of 653,678. It cannot be the missing cost. It is here
because a Studio session is already running for the rshape and tgord batches,
these are two files rather than a session of their own, and "the corpus
covers every real tag shape" is a claim worth being able to make without an
asterisk.

SHAPE TAKEN FROM A REAL EXPORT, not invented -- export 08's `TiltHoistToPlaner`
(Produced) and `PlanerToTiltHoist` (Consumed). Both are UDT-typed and neither
carries a `<Data>` element at all, which is the part most likely to be got
wrong by extrapolating from an ordinary Base tag. A Produced tag carries
`<ProduceInfo>` with ProduceCount and the RPI bounds; a Consumed tag carries
`<ConsumeInfo>` naming the producer controller, the remote tag and the RPI.

Both files declare the SAME UDT and the SAME number of tags as the Base
control, so the pair differences against `prodcons_base` on tag type alone.

Run: python -m sample_gen.gen_prodcons
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, collect_nested_datatypes, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"
CATEGORY = "tag_prodcons"

UDT = "MsgPacket"
MEMBERS = [MemberSpec("DATA", "DINT", dimension=32)]
COUNT = 20


def _produced(name: str) -> str:
    """ProduceInfo attributes copied from a real export's Produced tag."""
    return (
        f'      <Tag Name="{name}" TagType="Produced" DataType="{UDT}" '
        f'Constant="false" ExternalAccess="Read/Write">\n'
        f'        <ProduceInfo ProduceCount="1" ProgrammaticallySendEventTrigger="false" '
        f'UnicastPermitted="true" MinimumRPI="0.200" MaximumRPI="536870.900" '
        f'DefaultRPI="0" />\n'
        f"      </Tag>"
    )


def _consumed(name: str, idx: int) -> str:
    """ConsumeInfo attributes copied from a real export's Consumed tag."""
    return (
        f'      <Tag Name="{name}" TagType="Consumed" DataType="{UDT}" '
        f'ExternalAccess="Read/Write">\n'
        f'        <ConsumeInfo Producer="PeerPLC" RemoteTag="RemotePacket{idx:02d}" '
        f'RemoteInstance="0" RPI="20" Unicast="true" />\n'
        f"      </Tag>"
    )


VARIANTS = {
    "base": (lambda i: tag_xml(f"Packet{i:02d}", UDT, udt_members=MEMBERS),
             "ordinary Base tags -- the control the other two difference against"),
    "produced": (lambda i: _produced(f"Packet{i:02d}"),
                 "Produced tags, each with the ProduceInfo block a real export carries "
                 "(ProduceCount, the unicast flag and the RPI bounds) and no <Data> "
                 "element at all"),
    "consumed": (lambda i: _consumed(f"Packet{i:02d}", i),
                 "Consumed tags, each with the ConsumeInfo block a real export carries "
                 "(producer controller, remote tag name, RPI, unicast) and no <Data> "
                 "element at all"),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for key, (make, why) in VARIANTS.items():
        l5x = build_l5x(
            target_name="ProdConsProbe",
            tags_xml="\n".join(make(i) for i in range(COUNT)),
            extra_datatypes_xml=collect_nested_datatypes(UDT, MEMBERS),
        )
        name = f"prodcons_{key}"
        out = OUT / f"{name}.L5X"
        append_manifest_row(
            name,
            f"{COUNT} tags of the same {UDT} UDT (one DINT[32] member), declared as "
            f"{why}. OQ-TAGSHAPE: the tag survey compared 31,532 real tags against "
            f"91,641 corpus tags over 3,479 captured files and found the corpus already "
            f"covers every real tag shape except Produced (0.11% of real tags), Consumed "
            f"(0.06%) and 2-D arrays (0.16%) -- the 2-D case is the rshape_sub2d ladder, "
            f"and these three files close the other two. Completeness rather than a "
            f"residual hunt, and the entry says so: 0.33% of real tags at 84 bytes of "
            f"flat base is about 8,700 bytes against a residual of 653,678, so this "
            f"cannot be the missing cost. The Produced and Consumed shapes are copied "
            f"from a real export rather than extrapolated, including the part most "
            f"likely to be got wrong -- neither carries a <Data> element.",
            CATEGORY, out, write_sample(l5x, out))
    print("Total: 3")


if __name__ == "__main__":
    main()
