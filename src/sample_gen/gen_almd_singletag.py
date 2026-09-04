"""ALARM_DIGITAL (ALMD) structure sizing (OQ-PREDEFINED sibling gap, RM018A
read 2026-08-27, James: "size all of these instruction data types" scoped to
1756-RM018A). ALARM_DIGITAL was flagged 2026-08-27 as one of the predefined
structures with ZERO real decorated-data evidence in James's 64-file corpus
-- confirmed again here directly: every real `DataType="ALARM_DIGITAL"` Tag
found across `samples/local/` (16 real instances, 2 files) uses the
specialized `Data Format="Alarm"` semantic view (an `<AlarmDigitalParameters>`
attribute list + `<AlarmConfig>` message/class block), never raw
`Format="Decorated"`/`Format="L5K"` -- same dead end already hit for MESSAGE.
The L5K-array-length technique that solved SFC_STEP/SFC_ACTION/etc. does not
apply here either; a real controller memory-capture diff is the only path to
an exact byte total, same as TIMER/COUNTER/CONTROL's own confirmation
methodology.

Real member list (Input Parameters EnableIn/In/InFault/Condition/AckRequired/
Latched/ProgAck/OperAck/ProgReset/OperReset/ProgSuppress/OperSuppress/
ProgUnsuppress/OperUnsuppress/OperShelve/ProgUnshelve/OperUnshelve/
ProgDisable/OperDisable/ProgEnable/OperEnable/AlarmCountReset/UseProgTime =
23 BOOL, ProgTime = 1 LINT, Severity/MinDurationPRE/ShelveDuration/
MaxShelveDuration = 4 DINT; Output Parameters EnableOut/InAlarm/Acked/
InAlarmUnack/Suppressed/Shelved/Disabled/Commissioned = 8 BOOL,
MinDurationACC/AlarmCount/Status = 3 DINT (Status.0/.1/.2 are bit-aliases of
the Status word, same aliasing pattern as TIMER's .EN/.TT/.DN and MESSAGE's
.FLAGS bits -- NOT separate storage), InAlarmTime/AckTime/RetToNormalTime/
AlarmCountResetTime/ShelveTime/UnshelveTime = 6 LINT) is sourced directly
from RM018A pages 53-64 and cross-validated exactly against the real
`Comms_Bus1_ALMD` tag in `samples/local/L5X_Samples/MRFP_Edger_2026_06_01_
r00.L5X` (every Input-Parameter attribute name matches verbatim). Whether the
31 scalar BOOL members bit-pack (8-per-hidden-SINT, the confirmed convention
for consecutive BOOL members in ordinary UDTs) or take a full byte/word each
in this controller-native structure is UNCONFIRMED -- native predefined
structures go through different firmware code than user UDTs, so the UDT
convention is not assumed to carry over blind.

Two files here isolate what's actually being tested: (1) a minimal ALMD tag
with empty/short AlarmConfig message text, (2) the same tag with real-length
message/class text copied from the real Comms_Bus1_ALMD instance -- tests
whether AlarmConfig's message/class strings (which real tags always carry,
per corpus evidence) add to the tag's own byte cost or are compiled/stored
elsewhere (e.g. project documentation, not controller memory). Both use
write_sample_unmodeled (ALARM_DIGITAL has no predicted_bytes entry in
memory_model.yaml yet).

Run: python -m sample_gen.gen_almd_singletag
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rung_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# Real AlarmDigitalParameters attribute list, copied verbatim (attribute
# names/order) from samples/local/L5X_Samples/MRFP_Edger_2026_06_01_r00.L5X
# Comms_Bus1_ALMD -- only the boolean/DINT VALUES are irrelevant to byte
# size and left at the same real defaults.
_ALMD_PARAMS_ATTRS = (
    'Severity="500" MinDurationPRE="0" ShelveDuration="0" MaxShelveDuration="0" '
    'ProgTime="DT#1970-01-01-00:00:00.000_000Z" EnableIn="false" In="false" InFault="false" '
    'Condition="true" AckRequired="true" Latched="false" ProgAck="false" OperAck="false" '
    'ProgReset="false" OperReset="false" ProgSuppress="false" OperSuppress="false" '
    'ProgUnsuppress="false" OperUnsuppress="false" OperShelve="false" ProgUnshelve="false" '
    'OperUnshelve="false" ProgDisable="false" OperDisable="false" ProgEnable="false" '
    'OperEnable="false" AlarmCountReset="false" UseProgTime="false"'
)

_POOL_TAGS_XML = "\n".join([
    tag_xml("AlmIn", "BOOL"),
    tag_xml("AlmProgAck", "BOOL"),
    tag_xml("AlmProgReset", "BOOL"),
    tag_xml("AlmProgDisable", "BOOL"),
    tag_xml("AlmProgEnable", "BOOL"),
])


def _almd_tag_xml(name: str, message_text: str, alarm_class: str) -> str:
    return (
        f'      <Tag Name="{name}" TagType="Base" DataType="ALARM_DIGITAL" ExternalAccess="Read/Write">\n'
        f'        <Data Format="Alarm">\n'
        f'          <AlarmDigitalParameters {_ALMD_PARAMS_ATTRS}/>\n'
        f"          <AlarmConfig>\n"
        f"            <Messages>\n"
        f'              <Message Type="AM">\n'
        f'                <Text Lang="en-US"><![CDATA[{message_text}]]></Text>\n'
        f"              </Message>\n"
        f"            </Messages>\n"
        f"            <AlarmClass><![CDATA[{alarm_class}]]></AlarmClass>\n"
        f"          </AlarmConfig>\n"
        f"        </Data>\n"
        f"      </Tag>"
    )


def _write(out_name: str, l5x: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- ALARM_DIGITAL unmodeled, see OQ-PREDEFINED)")


def main() -> None:
    # ALMD's REAL operand list, read straight off James's Studio 5000
    # faceplate 2026-09-05 after both files failed with "Rung 0, ALMD:
    # Invalid number of arguments for instruction."
    #
    #     slot 1  ALMD             <- the ALARM_DIGITAL tag
    #     slot 2  ProgAck
    #     slot 3  ProgReset
    #     slot 4  ProgDisable
    #     slot 5  ProgEnable
    #     slot 6  MinDurationPRE
    #     slot 7  MinDurationACC
    #
    # SEVEN operands, and critically there is NO "In" operand -- the alarm
    # input is the RUNG CONDITION, not an argument. The old 6-argument call
    # passed AlmIn second, so Studio bound it to ProgAck and every operand
    # after it landed one slot early, with the last spilling into a slot
    # that does not exist ("Unknown" on the faceplate). That is what the
    # error was really saying: not "too few", but "these don't line up".
    # MinDurationPRE/ACC are v33+ additions and are what the old call was
    # missing entirely.
    instr = "ALMD(Alm1,AlmProgAck,AlmProgReset,AlmProgDisable,AlmProgEnable,0,0);"
    rung = rung_xml(0, instr)

    minimal_tag = _almd_tag_xml("Alm1", "Alarm", "A")
    l5x_minimal = build_l5x(target_name="AlmdMinimal",
                             tags_xml=_POOL_TAGS_XML + "\n" + minimal_tag, extra_rungs_xml=rung)
    _write(
        "almd_minimal", l5x_minimal,
        "ALMD(Alm1), minimal 1-char AlarmClass/message text -- isolates ALARM_DIGITAL structure's "
        "own byte cost (OQ-PREDEFINED sibling gap, RM018A pages 53-64 member list wired 2026-08-27)",
    )

    real_message = "Kinetix Bus 1 Communications Fault"
    real_class = "Edger"
    real_tag = _almd_tag_xml("Alm1", real_message, real_class)
    l5x_real = build_l5x(target_name="AlmdRealtext",
                          tags_xml=_POOL_TAGS_XML + "\n" + real_tag, extra_rungs_xml=rung)
    _write(
        "almd_realtext", l5x_real,
        "ALMD(Alm1), real-length AlarmClass/message text copied verbatim from samples/local/ "
        "Comms_Bus1_ALMD -- tests whether AlarmConfig message/class text adds to the tag's real "
        "byte cost vs. almd_minimal",
    )

    print("\nDone. 2 files.")


if __name__ == "__main__":
    main()
