"""Minimal-but-valid L5X wrapper: single controller, one empty task/program/
routine, no DataTypes/Modules/AOIs beyond the bare minimum. Callers supply
just the Tags XML body -- this is Approach A from docs/SAMPLE_GENERATION.md.

CORRECTED 2026-08-20 (Approach C, per SAMPLE_GENERATION.md): the
hand-authored template failed real Studio 5000 import -- first with an
unrecognized ProcessorType, then with "Child module incompatible with
parent module" once that was fixed. James imported the failing sample via
Studio 5000's own File->Import GUI, got the real error, then hand-built and
exported a genuinely valid blank 1756-L81E project and sent it back. This
template is now a direct copy of that real export's structure (down to the
Controller element's full real attribute set, RedundancyInfo/Security/
SafetyInfo/CST/WallClockTime/TimeSynchronize/EthernetPorts elements, and
the module's two real ports with Bus children) with only the genuinely
parameterized pieces substituted in -- not a re-guess. Confirms OQ-GENMETHOD's
original worry was right: raw hand-authored XML did NOT import cleanly on
the first (or second) try, and needed a real Studio-5000-validated
reference to get right.
"""

from __future__ import annotations

from datetime import datetime

# v35 / ControlLogix 5580-class -- switched 2026-08-20 (James: "why didnt
# you use 1756-L81? lets use that as default") from 5069-L306ER, which was
# only ever chosen because it's the one physical unit James has for real
# hardware spot-checks (OQ-EMULATE). 1756-L81E matches his actual primary
# target per OQ-L5XVERSION (v35/L8-class) and is what his real production
# files (BaillieLeitchField_Edger etc.) actually run on -- makes more sense
# as the generator default. Using the exact string already confirmed twice
# over: it's in controller_budgets.yaml (sourced, 3MB) and it's the literal
# ProcessorType value seen in James's own real L5X files -- not a repeat of
# the earlier 5069-L306ERS suffix-guessing mistake.
DEFAULT_PROCESSOR_TYPE = "1756-L81E"
DEFAULT_MAJOR_REV = "35"
DEFAULT_MINOR_REV = "11"
# Matches James's actual Studio 5000 install exactly (confirmed via his
# real 2026-08-20 reference export) -- was guessed as 35.11 before, wrong.
DEFAULT_SOFTWARE_REVISION = "35.05"


# Real, Studio-5000-confirmed values for 1756-L81E (James, 2026-08-20 export).
_PRODUCT_CODE = "164"
_ICP_BUS_SIZE = "17"


def build_l5x(
    target_name: str,
    tags_xml: str,
    processor_type: str = DEFAULT_PROCESSOR_TYPE,
    major_rev: str = DEFAULT_MAJOR_REV,
    minor_rev: str = DEFAULT_MINOR_REV,
    software_revision: str = DEFAULT_SOFTWARE_REVISION,
    extra_datatypes_xml: str = "",
    extra_rungs_xml: str = "",
    extra_aoi_xml: str = "",
    extra_routines_xml: str = "",
    extra_program_tags_xml: str = "",
) -> str:
    rungs = extra_rungs_xml if extra_rungs_xml.strip() else (
        '<Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>'
    )
    # Format matches the real reference export exactly (Python's ctime-style
    # strftime): "Thu Aug 20 11:19:00 2026".
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{software_revision}" TargetName="{target_name}" TargetType="Controller" ContainsContext="false" Owner="Admin" ExportDate="{now}" ExportOptions="NoRawData L5KData DecoratedData ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Target" Name="{target_name}" ProcessorType="{processor_type}" MajorRev="{major_rev}" MinorRev="{minor_rev}" ProjectCreationDate="{now}" LastModifiedDate="{now}" SFCExecutionControl="CurrentActive" SFCRestartPosition="MostRecent" SFCLastScan="DontScan" ProjectSN="16#0000_0000" MatchProjectToController="false" CanUseRPIFromProducer="false" InhibitAutomaticFirmwareUpdate="0" PassThroughConfiguration="EnabledWithAppend" DownloadProjectDocumentationAndExtendedProperties="true" DownloadProjectCustomProperties="true" ReportMinorOverflow="false" AutoDiagsEnabled="true" WebServerEnabled="false">
<RedundancyInfo Enabled="false" KeepTestEditsOnSwitchOver="false"/>
<Security Code="0" ChangesToDetect="16#ffff_ffff_ffff_ffff"/>
<SafetyInfo/>
<DataTypes>
{extra_datatypes_xml}
</DataTypes>
<Modules>
<Module Name="Local" CatalogNumber="{processor_type}" Vendor="1" ProductType="14" ProductCode="{_PRODUCT_CODE}" Major="{major_rev}" Minor="{minor_rev}" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="true">
<EKey State="Disabled"/>
<Ports>
<Port Id="1" Address="0" Type="ICP" Upstream="false">
<Bus Size="{_ICP_BUS_SIZE}"/>
</Port>
<Port Id="2" Type="Ethernet" Upstream="false">
<Bus/>
</Port>
</Ports>
</Module>
</Modules>
<AddOnInstructionDefinitions>
{extra_aoi_xml}
</AddOnInstructionDefinitions>
<Tags>
{tags_xml}
</Tags>
<Programs>
<Program Name="MainProgram" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" UseAsFolder="false">
<Tags>
{extra_program_tags_xml}
</Tags>
<Routines>
<Routine Name="MainRoutine" Type="RLL">
<RLLContent>
{rungs}
</RLLContent>
</Routine>
{extra_routines_xml}
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
<DataLogs/>
<TimeSynchronize Priority1="128" Priority2="128" PTPEnable="false"/>
<EthernetPorts>
<EthernetPort Port="1" Label="1" PortEnabled="true"/>
</EthernetPorts>
</Controller>
</RSLogix5000Content>
"""


def bool_tags_xml(count: int, name_prefix: str = "TestBool") -> str:
    tags = []
    for i in range(count):
        tags.append(
            f'      <Tag Name="{name_prefix}{i:04d}" TagType="Base" DataType="BOOL" '
            f'Radix="Decimal" Constant="false" ExternalAccess="Read/Write">\n'
            f'        <Data Format="Decorated">\n'
            f'          <DataValue DataType="BOOL" Radix="Decimal" Value="0"/>\n'
            f"        </Data>\n"
            f"      </Tag>"
        )
    return "\n".join(tags)
