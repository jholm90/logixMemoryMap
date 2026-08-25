"""MESSAGE-structure MessageType sweep (OQ-PREDEFINED, 2026-08-25). James
reversed the earlier deprioritization ("Message size is fine for the 90%
accuracy, not a common usage instruction"): "Generate messages to satisfy
this question? Message instructions are just like axis tags, lots of
config but always the same data size."

The only MessageType tested so far is CIP Generic (`instrfirst_msg.L5X`,
`gen_instruction_firstpass.py`), a 12-attribute get-attribute-list message.
Real corpus grep across every `samples/local/` file (2026-08-25) turned up
8 distinct real MessageTypes in use, each with its own attribute SET
(never guessed -- every attribute name/value pair below is copied verbatim
from a real `<MessageParameters>` element, only RemoteElement/LocalElement/
ConnectionPath genericized to this file's own placeholder tags, matching
`message_tag_xml`'s existing convention):

  CIP Data Table Read   (4 real occurrences)  -- ConnectedFlag present
  CIP Data Table Write  (1)                    -- ConnectedFlag present
  PLC5 Typed Read       (1)                    -- no ConnectedFlag (unconnected)
  PLC5 Typed Write      (8)                    -- no ConnectedFlag
  PLC5 Word Range Write (3)                    -- no ConnectedFlag
  SLC Typed Read        (1)                    -- no ConnectedFlag
  SLC Typed Write       (1)                    -- no ConnectedFlag

("Unconfigured" also appears 9x but is a real empty/placeholder MSG state,
not a functioning message -- not tested here.)

Each type gets its own isolated 1-rung MSG() file (mirrors instrfirst_msg's
shape exactly) so a per-type Capacity delta directly tests James's
hypothesis: does MessageType/attribute-set variation change the tag's real
byte size at all, or is MESSAGE's real footprint flat regardless of
config (the AXIS_CIP_DRIVE pattern)? MESSAGE has no predefined_structures
entry in memory_model.yaml (completely unmodeled byte size) -- every file
here uses write_sample_unmodeled, same as instrfirst_msg.

Run: python -m sample_gen.gen_msg_typesweep
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# (MessageType, real RemoteElement value (a remote-device address string,
# not a local tag reference -- kept verbatim, not genericized, since
# substituting a local tag name would break each protocol's real address
# format), real full attribute string minus MessageType/RemoteElement/
# LocalElement/ConnectionPath)
_REAL_TYPES = [
    ("CIP Data Table Read", "RemoteTag",
     'RequestedLength="1" ConnectedFlag="2" ConnectionPath="RemoteTarget" CommTypeCode="0" '
     'LocalIndex="0"'),
    ("CIP Data Table Write", "RemoteTag",
     'RequestedLength="1" ConnectedFlag="2" ConnectionPath="RemoteTarget" CommTypeCode="0" '
     'LocalIndex="0"'),
    ("PLC5 Typed Read", "F58:0",
     'RequestedLength="15" ConnectionPath="RemoteTarget" CommTypeCode="0" LocalIndex="0"'),
    ("PLC5 Typed Write", "na",
     'RequestedLength="4" ConnectionPath="RemoteTarget" CommTypeCode="0" LocalIndex="0"'),
    ("PLC5 Word Range Write", "na",
     'RequestedLength="28" ConnectionPath="RemoteTarget" CommTypeCode="0" LocalIndex="0"'),
    ("SLC Typed Read", "F24:0",
     'RequestedLength="512" ConnectionPath="RemoteTarget" CommTypeCode="0" LocalIndex="0"'),
    ("SLC Typed Write", "F24:0",
     'RequestedLength="512" ConnectionPath="RemoteTarget" CommTypeCode="0" LocalIndex="0"'),
]

_POOL_TAGS_XML = "\n".join([
    tag_xml("Arr0", "DINT", dimensions=(20,)),
])


def _msg_tag_xml(name: str, message_type: str, remote_element: str, attrs: str) -> str:
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="MESSAGE" ExternalAccess="Read/Write">\n'
        f'        <Data Format="Message">\n'
        f'          <MessageParameters MessageType="{message_type}" RemoteElement="{remote_element}" {attrs} '
        f'LocalElement="Arr0"/>\n'
        f'        </Data>\n'
        f"      </Tag>"
    )


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- MESSAGE unmodeled, see OQ-PREDEFINED)")


def main() -> None:
    for message_type, remote_element, attrs in _REAL_TYPES:
        slug = "".join(c if c.isalnum() else "_" for c in message_type).strip("_").lower()
        msg_tag = _msg_tag_xml("Msg1", message_type, remote_element, attrs)
        instr = "MSG(Msg1);"
        rung = rung_xml(0, instr)
        l5x = build_l5x(target_name=f"MsgType{slug.title().replace('_', '')}",
                         tags_xml=_POOL_TAGS_XML + "\n" + msg_tag, extra_rungs_xml=rung)
        _write(
            f"msgtype_{slug}", l5x,
            f'MSG(Msg1), MessageType="{message_type}" -- real attribute set copied verbatim from '
            f"samples/local/ corpus (RemoteElement kept as a real-shaped literal address string per "
            f"this protocol, LocalElement points at this file's own Arr0 tag, ConnectionPath "
            f"genericized), OQ-PREDEFINED MessageType sweep -- tests whether MESSAGE's real byte size "
            f"varies with MessageType/attribute-set config or stays flat like AXIS_CIP_DRIVE",
        )
    print(f"\nDone. {len(_REAL_TYPES)} files.")


if __name__ == "__main__":
    main()
