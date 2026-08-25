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

# Real 5069-family (Compact 5000, no separate chassis) Local-module Ports
# shape, confirmed 2026-08-22 against samples/local/DnR_Personal/
# BT1XX_FFC_20240325.L5X (5069-L330ERMS2): local bus Port Type="5069" (not
# "ICP"), Bus Size="32" (vs 1756's 17-slot-chassis convention), and TWO
# Ethernet ports (dual embedded switch) rather than 1756's one. James,
# 2026-08-22: "You'll have to swap to a 5069 processor to test the 5069
# modules" -- a naive processor_type string swap on the old ICP/single-
# Ethernet template would still be structurally wrong, so this is a real
# separate shape, not just a catalog-string substitution.
_5069_BUS_SIZE = "32"

# Real per-catalog ProductCode, 2026-08-26 (James's own real fw_baseline
# exports, samples/local/fw_versions/) -- found while investigating why
# every stringconst_*_l8 file (Constant-flag x processor batch) failed to
# convert. ProductCode is NOT just "164 for 1756, 223 for 5069" as this
# file assumed before today -- it's a distinct per-catalog identifier, and
# the DEFAULT 5069 processor this whole project has used throughout
# (5069-L306ER) was carrying the WRONG code (223, which is really
# 5069-L330ERMS2's -- see the comment above) instead of its own real 196.
# That mismatch evidently did NOT block import (hundreds of prior
# 5069-L306ER conversions succeeded with the wrong code), so it's very
# unlikely to be the actual cause of the stringconst failures -- but it's
# a real inaccuracy either way, now fixed with ground truth instead of a
# guessed bucket value. Falls back to the old bucket guess (164 non-5069 /
# 223 5069) for any catalog not in this table -- still unconfirmed for
# those, not claiming completeness beyond what's actually been verified.
_PRODUCT_CODES = {
    "1756-L81E": "164",
    "1756-L82E": "165",
    "1756-L83E": "166",
    "1756-L84E": "167",
    "1756-L85E": "168",
    "1769-L16ER-BB1B": "153",
    "1769-L18ER-BB1B": "154",
    "1769-L18ERM-BB1B": "155",
    "1769-L19ER-BB1B": "152",
    "1769-L24ER-QB1B": "149",
    "1769-L24ER-QBFC1B": "150",
    "1769-L27ERM-QBFC1B": "151",
    "1769-L30ERM": "156",
    "1769-L33ERM": "110",
    "5069-L306ER": "196",
    "5069-L306ERM": "189",
    "5069-L306ERMS2": "226",
    "5069-L306ERMS3": "243",
    "5069-L306ERS2": "235",
    "5069-L320ER": "217",
    "5069-L330ER": "218",
    "5069-L330ERMS2": "223",
    "5069-L340ER": "219",
    "5069-L3100ERM": "230",
}


def safety_partner_module_xml(
    controller_name: str,
    catalog: str = "1756-L8SP",
    product_code: str = "171",
    major_rev: str = DEFAULT_MAJOR_REV,
    minor_rev: str = DEFAULT_MINOR_REV,
) -> str:
    """A GuardLogix Safety Partner module -- physically the slot immediately
    to the right of the primary CPU, real and required whenever a program
    is SIL3/PLe (redundant safety processing across 2 physical modules);
    SIL2 uses a single non-redundant safety-capable primary with no
    partner at all (2026-08-27, James: "One safety partner is located
    beside the CPU on the right if the program is sil3. Sil2 has no
    safety partner. You need to handle this.").

    Confirmed real shape from samples/local/DnR_Personal/
    Bender134053_201104.L5X (a real SIL3/PLe program, Controller/
    SafetyInfo SafetyLevel="SIL3/PLe"): `EKey State="ExactMatch"` (not
    the usual "CompatibleModule" -- a tight redundant pairing needs an
    exact rev match, not just compatibility), `Width="0"` on its own
    upstream Port, and a module-level `SafetyNetwork` attribute (real
    value was all-zero -- the partner shares the primary's own safety
    network identity, it isn't independently CIP-Safety-networked).
    MUST be paired with `build_l5x(..., safety_partner=True)` -- the
    primary's own Local module needs `Width="2"` + real `SafetyNetwork`
    values on ITS ports too, which is what actually makes Studio 5000
    accept this as a valid redundant pairing rather than rejecting it
    ("Invalid module type for import. Module type cannot be created
    independently.", the real error hit before this was wired)."""
    return (
        f'<Module Name="{controller_name}:Partner" CatalogNumber="{catalog}" Vendor="1" ProductType="14" '
        f'ProductCode="{product_code}" Major="{major_rev}" Minor="{minor_rev}" ParentModule="Local" '
        f'ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_0000_0000_0000">\n'
        f'<EKey State="ExactMatch" />\n'
        f'<Ports>\n'
        f'<Port Id="1" Address="1" Type="ICP" Upstream="true" Width="0" />\n'
        f'</Ports>\n'
        f'</Module>'
    )


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
    extra_programs_xml: str = "",
    extra_scheduled_programs_xml: str = "",
    extra_modules_xml: str = "",
    extra_tasks_xml: str = "",
    safety_partner: bool = False,
) -> str:
    rungs = extra_rungs_xml if extra_rungs_xml.strip() else (
        '<Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>'
    )
    is_5069 = processor_type.startswith("5069")
    # safety_partner=True (2026-08-27, real SIL3/PLe requirement -- see
    # safety_partner_module_xml's own docstring): the primary CPU's own
    # local backplane Port needs Width="2" (it now spans its own slot AND
    # the partner's, confirmed real) plus a real SafetyNetwork identifier
    # on BOTH its ICP and Ethernet ports -- without this the Safety
    # Partner module in extra_modules_xml is rejected as an invalid
    # standalone import, it isn't a self-sufficient module on its own.
    # SafetyNetwork values are per-installation-unique in a real project;
    # these are placeholder-format (not James's real numbers) but keep
    # the same real 16#0000_xxxx_xxxx_xxxx bit-length/format.
    if is_5069:
        local_ports_xml = (
            f'<Port Id="1" Address="0" Type="5069" Upstream="false">\n'
            f'<Bus Size="{_5069_BUS_SIZE}"/>\n'
            f'</Port>\n'
            f'<Port Id="3" Type="Ethernet" Upstream="false">\n<Bus/>\n</Port>\n'
            f'<Port Id="4" Type="Ethernet" Upstream="false">\n<Bus/>\n</Port>'
        )
        local_product_code = _PRODUCT_CODES.get(processor_type, "223")
    elif safety_partner:
        local_ports_xml = (
            f'<Port Id="1" Address="0" Type="ICP" Upstream="false" Width="2" '
            f'SafetyNetwork="16#0000_1001_0001_0001">\n'
            f'<Bus Size="{_ICP_BUS_SIZE}"/>\n'
            f'</Port>\n'
            f'<Port Id="2" Type="Ethernet" Upstream="false" SafetyNetwork="16#0000_1001_0002_0002">\n<Bus/>\n</Port>'
        )
        local_product_code = _PRODUCT_CODES.get(processor_type, _PRODUCT_CODE)
    else:
        local_ports_xml = (
            f'<Port Id="1" Address="0" Type="ICP" Upstream="false">\n'
            f'<Bus Size="{_ICP_BUS_SIZE}"/>\n'
            f'</Port>\n'
            f'<Port Id="2" Type="Ethernet" Upstream="false">\n<Bus/>\n</Port>'
        )
        local_product_code = _PRODUCT_CODES.get(processor_type, _PRODUCT_CODE)
    safety_info_xml = (
        '<SafetyInfo SafetyLocked="true" SignatureRunModeProtect="false" '
        'ConfigureSafetyIOAlways="true" SafetyLevel="SIL3/PLe"/>'
        if safety_partner else '<SafetyInfo/>'
    )
    # Format matches the real reference export exactly (Python's ctime-style
    # strftime): "Thu Aug 20 11:19:00 2026".
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{software_revision}" TargetName="{target_name}" TargetType="Controller" ContainsContext="false" Owner="Admin" ExportDate="{now}" ExportOptions="NoRawData L5KData DecoratedData ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Target" Name="{target_name}" ProcessorType="{processor_type}" MajorRev="{major_rev}" MinorRev="{minor_rev}" ProjectCreationDate="{now}" LastModifiedDate="{now}" SFCExecutionControl="CurrentActive" SFCRestartPosition="MostRecent" SFCLastScan="DontScan" ProjectSN="16#0000_0000" MatchProjectToController="false" CanUseRPIFromProducer="false" InhibitAutomaticFirmwareUpdate="0" PassThroughConfiguration="EnabledWithAppend" DownloadProjectDocumentationAndExtendedProperties="true" DownloadProjectCustomProperties="true" ReportMinorOverflow="false" AutoDiagsEnabled="true" WebServerEnabled="false">
<RedundancyInfo Enabled="false" KeepTestEditsOnSwitchOver="false"/>
<Security Code="0" ChangesToDetect="16#ffff_ffff_ffff_ffff"/>
{safety_info_xml}
<DataTypes>
{extra_datatypes_xml}
</DataTypes>
<Modules>
<Module Name="Local" CatalogNumber="{processor_type}" Vendor="1" ProductType="14" ProductCode="{local_product_code}" Major="{major_rev}" Minor="{minor_rev}" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="true">
<EKey State="Disabled"/>
<Ports>
{local_ports_xml}
</Ports>
</Module>
{extra_modules_xml}
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
{extra_programs_xml}
</Programs>
<Tasks>
<Task Name="MainTask" Type="CONTINUOUS" Priority="10" Watchdog="500" DisableUpdateOutputs="false" InhibitTask="false">
<ScheduledPrograms>
<ScheduledProgram Name="MainProgram"/>
{extra_scheduled_programs_xml}
</ScheduledPrograms>
</Task>
{extra_tasks_xml}
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
