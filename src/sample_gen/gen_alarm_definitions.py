"""Datatype-level alarm definitions: the v38 shape priced at zero (OQ-ALARMDEF).

WHAT THIS IS
------------
`<AlarmDefinitions><DatatypeAlarmDefinition><MemberAlarmDefinition>` is an
alarm TEMPLATE attached to a data type, distinct from the tag-level
`<AlarmCondition>` this project already sizes exactly (OQ-ALARMCOND,
closed). A definition says "every tag of type X gets these alarms"; a
condition is one concrete alarm on one concrete tag.

It was found in the four real 1756-L9xTS v38 exports, carrying a stock
Rockwell P_PID definition with six member alarms, and the sizing engine
priced the whole block at zero while reporting nothing at all. The silence
is fixed (`audit_coverage()` now emits a `coverage/alarm_definitions`
notice). The byte cost is what this batch measures.

FIRMWARE: v35 PRIMARY, v38 AS A CONTROL
---------------------------------------
This project standardises generated tests on v35 so every batch differences
cleanly against the ~2,400 existing v35 captures. This batch briefly did not,
on the reasoning that <AlarmDefinitions> is absent from all 26 real corpus
exports at MajorRev 20-35 and present in all four at 38.

That reasoning was wrong, and worth recording so it is not repeated: those 26
files are projects that did not USE the feature. Absence from them is not
evidence that v35 rejects the element -- no v35 file carrying one was ever
tested. Building the whole batch off-standard on that basis cost the
comparability the standard exists to provide.

So the primary arm is v35, matching every other batch. A matching v38 arm is
kept deliberately, and now earns its place as a real control: it answers
whether firmware changes the cost at all, and if v35 turns out to reject the
element outright, the v38 arm still closes OQ-ALARMDEF while the v35 failures
prove the version boundary.

WHAT EACH GROUP SEPARATES
-------------------------
Group A -- definition and member marginal cost. A definition with 0, 1, 2,
4, 8 and 16 members prices the per-member slope; 1, 2, 4 and 8 definitions
each holding a single member prices the per-definition intercept. The two
sweeps are deliberately non-collinear, which is exactly what the real files
cannot offer: they carry one definition at one member count.

Group B -- does an uninstantiated template cost anything? A definition
naming a UDT is paired against 0, 1, 4 and 16 real tags of that UDT, with
matching tag-only files carrying no definition at all. Differencing the two
ladders separates the template's own storage from per-instance storage. The
real exports make this worth asking: they carry a P_PID definition while
`<DataTypes/>` is empty and no P_PID tag exists anywhere, so a template can
clearly outlive any instance of its type.

Group C -- does the operator message text count? The ADM message in the
real exports is a long CDATA string with embedded format directives. Four
files hold the definition and member count fixed and vary only that text:
absent, ~16, ~128 and ~512 characters.

ONE PROCESSOR, TWO FIRMWARES
----------------------------
Every file is built twice on 1756-L81E: once at v35 and once at v38. Holding
the processor fixed and varying only firmware makes the v35-vs-v38 difference
readable directly. 1756-L81E is the catalog the existing baseline and most of
the real corpus already use, so the v35 arm slots straight into the rest of
the measured data.

Run: python -m sample_gen.gen_alarm_definitions
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from .builders import MemberSpec, tag_xml, udt_xml
from .gen_fw_catalog_matrix import _local_ports_xml, _product_code
from .manifest import append_manifest_row, write_sample

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "alarmdefs"

# (catalog, slug, major_rev, software_revision). v35 is the project standard
# and the primary arm; v38 is the control -- see the module docstring.
_PROCESSORS = [
    ("1756-L81E", "l81_v35", "35", "35.05"),
    ("1756-L81E", "l81_v38", "38", "38.02"),
]
_MINOR_REV = "11"

# The UDT the definitions attach to. BOOL status members are what a real
# MemberAlarmDefinition's Input points at -- ".Sts_Fail" in the real P_PID
# block. 16 of them covers the largest member sweep point.
_UDT_NAME = "AlarmSrcType"
_MAX_MEMBERS = 16


def _udt_member_name(i: int) -> str:
    return f"Sts_A{i:02d}"


def _alarm_member_name(i: int) -> str:
    return f"Alm_A{i:02d}"


def _source_udt_xml() -> str:
    return udt_xml(_UDT_NAME, [MemberSpec(_udt_member_name(i), "BOOL") for i in range(_MAX_MEMBERS)])


def _message_xml(text: str | None) -> str:
    """The real block nests AlarmConfig > Messages > Message Type="ADM" >
    Text > CDATA. `None` omits AlarmConfig entirely."""
    if text is None:
        return ""
    return (
        "<AlarmConfig>\n<Messages>\n<Message Type=\"ADM\">\n<Text Lang=\"en-US\">\n"
        f"<![CDATA[{text}]]>\n</Text>\n</Message>\n</Messages>\n</AlarmConfig>\n"
    )


def _member_alarm_xml(index: int, message: str | None = "Alarm on status bit") -> str:
    """One <MemberAlarmDefinition>, attribute for attribute in the real
    order and with the real defaults, copied from the L9 exports rather
    than composed from the schema."""
    body = _message_xml(message)
    open_tag = (
        f'<MemberAlarmDefinition Name="{_alarm_member_name(index)}" '
        f'Input=".{_udt_member_name(index)}" ConditionType="TRIP" Limit="0.0" '
        f'Severity="500" OnDelay="0" OffDelay="0" ShelveDuration="480" '
        f'MaxShelveDuration="480" Deadband="0.0" Required="false"\n'
        f' AlarmSetOperIncluded="true" AlarmSetRollupIncluded="true" AckRequired="true" '
        f'Latched="false" EvaluationPeriod="500 millisecond" Expression="= 1" '
        f'IsTemplate="true"'
    )
    if not body:
        return open_tag + "/>\n"
    return open_tag + ">\n" + body + "</MemberAlarmDefinition>\n"


def _alarm_definitions_xml(definitions: list[tuple[str, list[str]]]) -> str:
    """`definitions` is [(datatype_name, [member_alarm_xml, ...]), ...].
    An empty list omits the whole element, matching a project that has
    never had one."""
    if not definitions:
        return ""
    body = "".join(
        f'<DatatypeAlarmDefinition Name="{name}">\n{"".join(members)}</DatatypeAlarmDefinition>\n'
        for name, members in definitions
    )
    return f"<AlarmDefinitions>\n{body}</AlarmDefinitions>\n"


def _build_xml(catalog: str, target_name: str, major_rev: str, software_revision: str, *,
               datatypes_xml: str = "", alarm_definitions_xml: str = "",
               tags_xml: str = "") -> str:
    """Controller shell copied from the real 1756-L9xTS v38 exports, with
    the 1756-L81E port shape substituted for the L8 arm. Deliberately does
    not route through wrapper.py's build_l5x: that function has no hook for
    a controller-level AlarmDefinitions element, and ~1300 already-converted
    files depend on its exact output."""
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    guid = "{" + str(uuid.uuid4()).upper() + "}"
    is_l9 = catalog.startswith("1756-L9")
    is_v38 = major_rev == "38"
    # DataExchangeId is a v38 addition -- confirmed present in the real v38
    # exports and absent from every v35 one. Emitting it on a v35 file would
    # make the firmware arms differ by more than the firmware.
    dx = f' DataExchangeId="{guid}"' if is_v38 else ""
    # Both real families carry these v38 attributes; only the L9 exports
    # carry SafetyEnabled, dual-IP mode, OpcUaInfo and the A1/A2 port pair.
    safety_info = '<SafetyInfo SafetyEnabled="false"/>' if is_l9 else "<SafetyInfo/>"
    dual_ip = ' EtherNetIPMode="A1/A2: Dual-IP"' if is_l9 else ""
    opcua = '<OpcUaInfo EnabledPorts=""/>\n' if is_l9 else ""
    datalogs = "" if is_l9 else "<DataLogs/>\n"
    if is_l9:
        ethernet_ports = (
            '<EthernetPorts>\n'
            '<EthernetPort Port="1" Label="A1" PortEnabled="true"/>\n'
            '<EthernetPort Port="2" Label="A2" PortEnabled="true"/>\n'
            '</EthernetPorts>\n'
        )
    else:
        ethernet_ports = '<EthernetPorts>\n<EthernetPort Port="1" Label="1" PortEnabled="true"/>\n</EthernetPorts>\n'
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{software_revision}" TargetName="{target_name}" TargetType="Controller" ContainsContext="false" Owner="Admin" ExportDate="{now}" ExportOptions="NoRawData L5KData DecoratedData ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Target" Name="{target_name}" ProcessorType="{catalog}" MajorRev="{major_rev}" MinorRev="{_MINOR_REV}" TimeSlice="20" ShareUnusedTimeSlice="1" ProjectCreationDate="{now}" LastModifiedDate="{now}" SFCExecutionControl="CurrentActive" SFCRestartPosition="MostRecent" SFCLastScan="DontScan" ProjectSN="16#0000_0000" MatchProjectToController="false" CanUseRPIFromProducer="false" InhibitAutomaticFirmwareUpdate="0" PassThroughConfiguration="EnabledWithAppend" DownloadProjectDocumentationAndExtendedProperties="true" DownloadProjectCustomProperties="true" ReportMinorOverflow="false"{dual_ip} AutoDiagsEnabled="false" WebServerEnabled="false"{dx}>
<RedundancyInfo Enabled="false" KeepTestEditsOnSwitchOver="false" IOMemoryPadPercentage="90" DataTablePadPercentage="50"/>
<Security Code="0" ChangesToDetect="16#ffff_ffff_ffff_ffff"/>
{safety_info}
<DataTypes>
{datatypes_xml}</DataTypes>
<Modules>
<Module Name="Local" CatalogNumber="{catalog}" Vendor="1" ProductType="14" ProductCode="{_product_code(catalog)}" Major="{major_rev}" Minor="{_MINOR_REV}" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="true">
<EKey State="Disabled"/>
<Ports>
{_local_ports_xml(catalog)}
</Ports>
</Module>
</Modules>
<AddOnInstructionDefinitions/>
{alarm_definitions_xml}<Tags>
{tags_xml}</Tags>
<Programs>
<Program Name="MainProgram" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" UseAsFolder="false">
<Tags/>
<Routines>
<Routine Name="MainRoutine" Type="RLL">
<RLLContent>
<Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>
</RLLContent>
</Routine>
</Routines>
</Program>
</Programs>
<Tasks>
<Task Name="MainTask" Type="CONTINUOUS" Priority="10" Watchdog="500" DisableUpdateOutputs="false" InhibitTask="false">
<ScheduledPrograms>
<ScheduledProgram Name="MainProgram"/>
</ScheduledPrograms>
</Task>
</Tasks>
<CST MasterID="0"/>
<WallClockTime LocalTimeAdjustment="0" TimeZone="0"/>
<Trends/>
{datalogs}<TimeSynchronize Priority1="128" Priority2="128" PTPEnable="false"/>
{ethernet_ports}{opcua}</Controller>
</RSLogix5000Content>
"""


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "alarmdefs", out_path, bytes_)


def _target_name(out_name: str) -> str:
    return "".join(part.capitalize() for part in out_name.split("_"))


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    written = 0
    udt = _source_udt_xml()

    for catalog, slug, major_rev, software_revision in _PROCESSORS:
        # --- Group A: definition and member marginal cost -----------------
        # Member sweep: one definition, N members. m00 is also the control
        # for the definition sweep -- an AlarmDefinitions element that
        # exists but holds nothing.
        for n_members in (0, 1, 2, 4, 8, 16):
            out_name = f"alarmdef_{slug}_d1_m{n_members:02d}"
            defs = [(_UDT_NAME, [_member_alarm_xml(i) for i in range(n_members)])]
            l5x = _build_xml(catalog, _target_name(out_name), major_rev, software_revision, datatypes_xml=udt,
                             alarm_definitions_xml=_alarm_definitions_xml(defs))
            _write(l5x, out_name,
                   f"OQ-ALARMDEF group A: 1 datatype alarm definition holding {n_members} "
                   f"member alarm(s), {catalog} at v{major_rev}. Member-count slope.")
            written += 1

        # Definition sweep: N definitions, one member each. Needs N distinct
        # data types, since a definition is keyed by the type it attaches to.
        for n_defs in (2, 4, 8):
            out_name = f"alarmdef_{slug}_d{n_defs:02d}_m1"
            type_names = [f"{_UDT_NAME}{i:02d}" for i in range(n_defs)]
            types_xml = "".join(
                udt_xml(t, [MemberSpec(_udt_member_name(0), "BOOL")]) for t in type_names
            )
            defs = [(t, [_member_alarm_xml(0)]) for t in type_names]
            l5x = _build_xml(catalog, _target_name(out_name), major_rev, software_revision, datatypes_xml=types_xml,
                             alarm_definitions_xml=_alarm_definitions_xml(defs))
            _write(l5x, out_name,
                   f"OQ-ALARMDEF group A: {n_defs} datatype alarm definitions, 1 member alarm "
                   f"each, {catalog} at v{major_rev}. Per-definition intercept. Differences "
                   f"against alarmdef_{slug}_d1_m01.")
            written += 1

        # --- Group B: does an uninstantiated template cost anything? ------
        for n_tags in (0, 1, 4, 16):
            tags = "".join(tag_xml(f"AlarmSrc{i:02d}", _UDT_NAME) for i in range(n_tags))
            with_def = f"alarmdef_{slug}_inst_t{n_tags:02d}"
            l5x = _build_xml(catalog, _target_name(with_def), major_rev, software_revision, datatypes_xml=udt,
                             alarm_definitions_xml=_alarm_definitions_xml(
                                 [(_UDT_NAME, [_member_alarm_xml(0)])]),
                             tags_xml=tags)
            _write(l5x, with_def,
                   f"OQ-ALARMDEF group B: 1 definition with 1 member alarm, plus {n_tags} tag(s) "
                   f"of the defined type, {catalog} at v{major_rev}. Instantiation ladder.")
            written += 1

            if n_tags == 0:
                continue  # the no-definition control at 0 tags is d1_m00's sibling
            without_def = f"alarmdef_{slug}_noinst_t{n_tags:02d}"
            l5x = _build_xml(catalog, _target_name(without_def), major_rev, software_revision, datatypes_xml=udt,
                             tags_xml=tags)
            _write(l5x, without_def,
                   f"OQ-ALARMDEF group B control: {n_tags} tag(s) of the same type with NO alarm "
                   f"definition at all, {catalog} at v{major_rev}. Differences against "
                   f"alarmdef_{slug}_inst_t{n_tags:02d} to isolate the template.")
            written += 1

        # --- Group C: does the operator message text count? ---------------
        # Definition and member count held fixed; only the CDATA varies.
        for label, text in (("none", None), ("s", "Status bit tripped"),
                            ("m", "Status bit tripped: " + "detail text " * 9),
                            ("l", "Status bit tripped: " + "detail text " * 41)):
            out_name = f"alarmdef_{slug}_msg_{label}"
            defs = [(_UDT_NAME, [_member_alarm_xml(0, message=text)])]
            l5x = _build_xml(catalog, _target_name(out_name), major_rev, software_revision, datatypes_xml=udt,
                             alarm_definitions_xml=_alarm_definitions_xml(defs))
            length = 0 if text is None else len(text)
            _write(l5x, out_name,
                   f"OQ-ALARMDEF group C: 1 definition, 1 member alarm, operator message text "
                   f"{length} chars ({'no AlarmConfig element' if text is None else label}), "
                   f"{catalog} at v{major_rev}. Message-text slope.")
            written += 1

    print(f"Done. {written} files in {OUT_ROOT}.")


if __name__ == "__main__":
    main()
