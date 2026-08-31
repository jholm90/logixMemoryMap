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

import re
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
# "ICP"), vs 1756's 17-slot-chassis convention, and TWO Ethernet ports
# (dual embedded switch) rather than 1756's one. James, 2026-08-22:
# "You'll have to swap to a 5069 processor to test the 5069 modules" -- a
# naive processor_type string swap on the old ICP/single-Ethernet template
# would still be structurally wrong, so this is a real separate shape, not
# just a catalog-string substitution.
#
# BUG FOUND 2026-08-28 (James, real Studio 5000 error on
# modulesweep_5069_ib16_a.L5X): "Failed to set the 'Size' property
# (Chassis size exceeds the allowable size for a chassis.)". The flat
# Bus Size="32" used for EVERY 5069 catalog was only ever confirmed real
# for 5069-L330ERMS2 -- it's NOT a fixed constant, it's a real per-model
# maximum-local-I/O-count that scales with CPU tier. An empty project
# (no local module attached) never trips this validation regardless of
# the declared value (confirmed: v35_l306er.L5X passes 8/8 with the same
# wrong "32"), which is exactly why this stayed hidden until a real local
# 5069 I/O module actually got attached. Real per-catalog values pulled
# directly from 5 separate real corpus files (never guessed):
# samples/local/L306ERS2_Sample.L5X (5069-L306ERS2, 9),
# samples/local/DnR_Personal/PWO_134190.L5X (5069-L310ERS2, 9),
# samples/local/DnR_Personal/Fisher_Synergy_Bead_20240725.L5X
# (5069-L320ERMS2, 17), FlareFunction_311D_240731.L5X (5069-L320ERMS3, 17),
# BT1XX_FFC_20240325.L5X (5069-L330ERMS2, 32),
# Fisher_P800Sub_20240531.L5X (5069-L340ERS2, 32). The M/MS2/MS3/S2/ER
# suffix doesn't change the physical backplane capacity within the same
# base model number (e.g. L306ER and L306ERS2 are the same tier, only the
# safety/motion feature suffix differs), so this keys off the base model
# number extracted from processor_type.
_5069_BUS_SIZE_BY_MODEL = {
    "L306": "9", "L310": "9",
    "L320": "17",
    "L330": "32", "L340": "32",
}
_5069_BUS_SIZE_DEFAULT = "32"  # unconfirmed for any model not in the table above


def _5069_bus_size(processor_type: str) -> str:
    m = re.match(r"5069-(L\d{3})", processor_type)
    return _5069_BUS_SIZE_BY_MODEL.get(m.group(1), _5069_BUS_SIZE_DEFAULT) if m else _5069_BUS_SIZE_DEFAULT


# 1769-family (CompactLogix 5370, DIN-rail expansion I/O bus) real Local
# Ports shape -- STRUCTURAL BUG FOUND 2026-08-28 (James: "the 5069 and
# 1769 have different backplane sizes based on the catalog number
# ordered"): there was no is_1769 branch at all before this, so every
# 1769 processor silently fell through to the generic ICP-chassis else
# branch (Port Type="ICP", single Ethernet port) -- wrong PORT TYPE, not
# just a wrong number. Real corpus evidence (samples/local/DnR_Personal/
# TOYOTA_135453_20221024.L5X, ProcessorType="1769-L33ERMS"): Port
# Type="Compact" (a third distinct value, neither 1756's "ICP" nor
# 5069's "5069"), single Ethernet port -- same single-Ethernet shape as
# 1756, unlike 5069's dual-Ethernet. Only ONE real per-catalog bus-size
# data point exists so far (L33ERMS -> 17); every other 1769 catalog's
# real max is UNCONFIRMED -- same 17 kept only as a fallback, not
# asserted as correct for other models the way the 5069 table is.
_1769_BUS_SIZE_BY_MODEL = {
    "L33": "17",  # confirmed, TOYOTA_135453_20221024.L5X (1769-L33ERMS)
}
_1769_BUS_SIZE_DEFAULT = "17"  # unconfirmed for any model not in the table above


def _1769_bus_size(processor_type: str) -> str:
    m = re.match(r"1769-(L\d{2})", processor_type)
    return _1769_BUS_SIZE_BY_MODEL.get(m.group(1), _1769_BUS_SIZE_DEFAULT) if m else _1769_BUS_SIZE_DEFAULT

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
    "1756-L71": "92",
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
    safety_level: str | None = None,
) -> str:
    """`safety_level`: None (default, standard non-safety controller),
    "SIL2" (single non-redundant safety-capable primary -- any module with
    `SafetyEnabled="true"` real-errors "The Controller is not a Safety
    Controller" against a standard controller, confirmed 2026-08-27 on
    James's own real conversion attempts of the 4conn Kinetix safety-drive
    variants and PowerFlex 527-STO), or "SIL3" (redundant primary +
    partner -- see `safety_partner_module_xml`). Real, well-established
    IEC 61508/62061 SIL-to-PL correspondence used for `SafetyLevel`
    (SIL2/PLd, SIL3/PLe) -- James, 2026-08-27: "One safety partner is
    located beside the CPU on the right if the program is sil3. Sil2 has
    no safety partner." Callers must ALSO pass a real safety-rated
    `processor_type` (e.g. "1756-L81ES") -- this function does not
    silently upgrade a plain processor_type on the caller's behalf, real
    processor catalog choice stays explicit."""
    rungs = extra_rungs_xml if extra_rungs_xml.strip() else (
        '<Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>'
    )
    is_1769 = processor_type.startswith("1769")
    is_5069 = processor_type.startswith("5069")
    # REAL BUG FOUND 2026-08-31 (James, real Studio 5000 error on
    # blockbytetest_l71_dint120000.L5X): "Name collision: imported Module
    # 'Local' renamed to 'Local1'" + "Required property 'Port' was missing"
    # + "Requested item could not be found" on Controller/EthernetPorts.
    # Root cause: this project's default ("else") branch below assumes
    # every non-1769/non-5069 processor is Ethernet-embedded like the L8xE
    # (ControlLogix5580) family this project is built around -- wrong for
    # the OLDER pre-5580 ControlLogix line (1756-L6x/ControlLogix5560,
    # 1756-L7x/ControlLogix5570), which has NO embedded network port at
    # all (needs a separate 1756-ENxT/EN2T module in another slot for any
    # network path). Confirmed against a real reference export already in
    # this repo, samples/local/L7_v21_Sample.L5X (ProcessorType=
    # "1756-L71"): its own Local module has exactly ONE Port (ICP, Bus
    # Size="4" -- that specific number is this one customer's chassis
    # choice, not asserted as a per-model constant), no second Ethernet
    # Port, and the file has NO Controller-level <EthernetPorts> element
    # at all. Only 1756-L71 itself is confirmed this way; L72-L75 (same
    # ControlLogix5570 product line) and the L6x/ControlLogix5560 line are
    # assumed to share the same no-embedded-Ethernet shape by product
    # family, not independently confirmed.
    is_pre5580_1756 = bool(re.match(r"1756-L[67]\d", processor_type))
    if is_1769:
        # See _1769_bus_size's docstring above for the real corpus source.
        # SafetyNetwork handling mirrors the SIL2/is_5069 fix (same real
        # orphaned-reference risk applies to any family) even though no
        # real 1769 Safety corpus example has been checked yet -- TOYOTA_
        # 135453_20221024.L5X's own Local module DOES carry a real
        # SafetyNetwork on its Ethernet port, so the family supports it,
        # just not independently confirmed as required in every safety
        # config the way the 5069/1756 cases were.
        safety_net_attrs = (
            (' SafetyNetwork="16#0000_1004_0001_0001"',
             ' SafetyNetwork="16#0000_1004_0002_0002"')
            if safety_level else ("", "")
        )
        local_ports_xml = (
            f'<Port Id="1" Address="0" Type="Compact" Upstream="false"{safety_net_attrs[0]}>\n'
            f'<Bus Size="{_1769_bus_size(processor_type)}"/>\n'
            f'</Port>\n'
            f'<Port Id="2" Type="Ethernet" Upstream="false"{safety_net_attrs[1]}>\n<Bus/>\n</Port>'
        )
        local_product_code = _PRODUCT_CODES.get(processor_type, _PRODUCT_CODE)
    elif is_5069:
        # BUG FOUND 2026-08-28 alongside the SIL2 fix below: this branch
        # is checked BEFORE safety_level, so a 5069-family safety project
        # (e.g. 5069-L306ERMS2 hosting a SafetyEnabled="true" 5069-IB8S/A)
        # never reached the SIL2 SafetyNetwork logic at all -- same
        # orphaned-reference failure, different code path. Real corpus
        # confirmation this time from a genuine 5069 sample already in
        # the local corpus (samples/local/L306ERS2_Sample.L5X,
        # ProcessorType="5069-L306ERS2"): ALL THREE Local ports (the
        # local "5069" bus AND both Ethernet ports) carry a real
        # SafetyNetwork attribute, not just one -- confirmed real, not
        # guessed.
        safety_net_attrs = (
            (' SafetyNetwork="16#0000_1003_0001_0001"',
             ' SafetyNetwork="16#0000_1003_0003_0003"',
             ' SafetyNetwork="16#0000_1003_0004_0004"')
            if safety_level else ("", "", "")
        )
        local_ports_xml = (
            f'<Port Id="1" Address="0" Type="5069" Upstream="false"{safety_net_attrs[0]}>\n'
            f'<Bus Size="{_5069_bus_size(processor_type)}"/>\n'
            f'</Port>\n'
            f'<Port Id="3" Type="Ethernet" Upstream="false"{safety_net_attrs[1]}>\n<Bus/>\n</Port>\n'
            f'<Port Id="4" Type="Ethernet" Upstream="false"{safety_net_attrs[2]}>\n<Bus/>\n</Port>'
        )
        local_product_code = _PRODUCT_CODES.get(processor_type, "223")
    elif safety_level == "SIL3":
        # Redundant pairing: the primary's own local backplane Port needs
        # Width="2" (spans its own slot AND the partner's, confirmed real)
        # plus a real SafetyNetwork identifier on BOTH its ICP and
        # Ethernet ports -- without this a Safety Partner module in
        # extra_modules_xml is rejected as an invalid standalone import.
        # SafetyNetwork values are per-installation-unique in a real
        # project; these are placeholder-format (not James's real
        # numbers) but keep the same real 16#0000_xxxx_xxxx_xxxx
        # bit-length/format.
        local_ports_xml = (
            f'<Port Id="1" Address="0" Type="ICP" Upstream="false" Width="2" '
            f'SafetyNetwork="16#0000_1001_0001_0001">\n'
            f'<Bus Size="{_ICP_BUS_SIZE}"/>\n'
            f'</Port>\n'
            f'<Port Id="2" Type="Ethernet" Upstream="false" SafetyNetwork="16#0000_1001_0002_0002">\n<Bus/>\n</Port>'
        )
        local_product_code = _PRODUCT_CODES.get(processor_type, _PRODUCT_CODE)
    elif safety_level == "SIL2":
        # BUG FOUND 2026-08-28 (James: "did a super in-depth memory
        # analysis... review the last batch of l5x conversions"):
        # this branch previously assumed SIL2 (single non-redundant
        # safety-capable primary, no partner) needed no SafetyNetwork on
        # the Local module's own ports -- "no adjacent slot to reserve,
        # since there's no partner. Only SafetyInfo differs for SIL2."
        # That conflated two separate real Rockwell concepts: Width="2"
        # is about reserving the ADJACENT SLOT for a redundant partner
        # (correctly SIL3-only), but SafetyNetwork is about establishing
        # the safety NETWORK SEGMENT identity that any downstream
        # safety-enabled I/O module's own SafetyNetwork attribute
        # references -- needed any time a descendant module has
        # SafetyEnabled="true", with or without a redundant partner.
        # Root-caused against real convert_log.csv data: every one of 11
        # real SIL2 module-sweep failures (2198-*-ERS3 4conn variants,
        # 1734-OB8S/A+B, PowerFlex 527-STO, 442G-MABLB, FANUC robot,
        # 5069-IB8S/A, 5069-OBV8S/A) had a downstream module correctly
        # declaring SafetyNetwork, but the Local module's own ICP/
        # Ethernet ports never established that network -- an orphaned
        # reference. Confirmed against real corpus (SJ_Gormley_
        # 20251112_r02.L5X): its Local module's ICP port carries
        # SafetyNetwork="...cbbc" and its Ethernet port carries "...cbbd",
        # the exact value every downstream Kinetix ERS3 safety module in
        # that file references. Fixed: SIL2 now emits SafetyNetwork on
        # both ports too, just without SIL3's Width="2" partner
        # reservation.
        local_ports_xml = (
            f'<Port Id="1" Address="0" Type="ICP" Upstream="false" '
            f'SafetyNetwork="16#0000_1002_0001_0001">\n'
            f'<Bus Size="{_ICP_BUS_SIZE}"/>\n'
            f'</Port>\n'
            f'<Port Id="2" Type="Ethernet" Upstream="false" SafetyNetwork="16#0000_1002_0002_0002">\n<Bus/>\n</Port>'
        )
        local_product_code = _PRODUCT_CODES.get(processor_type, _PRODUCT_CODE)
    elif is_pre5580_1756:
        # See is_pre5580_1756's definition above for the real corpus
        # evidence -- ICP-only, no embedded Ethernet Port, matching
        # samples/local/L7_v21_Sample.L5X exactly, including the real Bus
        # Size=4 (NOT the generic _ICP_BUS_SIZE=17 default -- that's an
        # L8xE-family value, this project's OTHER independent 1756-L7x
        # implementation, gen_fw_catalog_matrix.py, already uses the real
        # 4 from the same reference file; using 17 here would have been a
        # guess where a real value was already sitting in this repo).
        _L7X_ICP_BUS_SIZE = "4"
        local_ports_xml = (
            f'<Port Id="1" Address="0" Type="ICP" Upstream="false">\n'
            f'<Bus Size="{_L7X_ICP_BUS_SIZE}"/>\n'
            f'</Port>'
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
    # REAL BUG FOUND 2026-08-30 (James: "your L8 safety failed to generate
    # acd files. You should have known that"). SafetyLocked="true" with no
    # SafetySignature attribute is an invalid combination -- see the same
    # fix in gen_fw_catalog_matrix.py's _build_xml for the full real-corpus
    # cross-check (9/9 files: every SafetyLocked="true" carries a real
    # signature, every "false" has none). These generated files never sign
    # a real safety application, so SafetyLocked="false" is correct.
    if safety_level == "SIL3":
        safety_info_xml = (
            '<SafetyInfo SafetyLocked="false" SignatureRunModeProtect="false" '
            'ConfigureSafetyIOAlways="true" SafetyLevel="SIL3/PLe"/>'
        )
    elif safety_level == "SIL2":
        safety_info_xml = (
            '<SafetyInfo SafetyLocked="false" SignatureRunModeProtect="false" '
            'ConfigureSafetyIOAlways="true" SafetyLevel="SIL2/PLd"/>'
        )
    else:
        safety_info_xml = '<SafetyInfo/>'
    # Format matches the real reference export exactly (Python's ctime-style
    # strftime): "Thu Aug 20 11:19:00 2026".
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    # REAL BUG FOUND 2026-08-28 (James: "looks like your 5069-LxxERMSx has
    # issues as well"). EtherNetIPMode="A1/A2: Dual-IP" is a real
    # Controller-level attribute confirmed present, identical value, in
    # EVERY 5069 corpus file checked (6/6, zero variance -- both plain
    # non-motion S2 catalogs and motion+safety ERMSx catalogs alike, so
    # this is a 5069-family-wide gap, not specific to the ERMSx subset
    # James happened to be testing). Describes how the CPU's two embedded
    # Ethernet ports are configured (Dual-IP addressing) -- something
    # only a 5069 processor has (1756/1769 have at most one embedded
    # port), so it's correctly omitted for every other family.
    ethernet_ip_mode_attr = ' EtherNetIPMode="A1/A2: Dual-IP"' if is_5069 else ""
    # See is_pre5580_1756's definition above: samples/local/L7_v21_Sample.L5X
    # (real 1756-L71 export) has no Controller-level <EthernetPorts> element
    # at all -- this CPU has no embedded network port to describe.
    ethernet_ports_xml = "" if is_pre5580_1756 else (
        '<EthernetPorts>\n<EthernetPort Port="1" Label="1" PortEnabled="true"/>\n</EthernetPorts>\n'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{software_revision}" TargetName="{target_name}" TargetType="Controller" ContainsContext="false" Owner="Admin" ExportDate="{now}" ExportOptions="NoRawData L5KData DecoratedData ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Target" Name="{target_name}" ProcessorType="{processor_type}" MajorRev="{major_rev}" MinorRev="{minor_rev}" ProjectCreationDate="{now}" LastModifiedDate="{now}" SFCExecutionControl="CurrentActive" SFCRestartPosition="MostRecent" SFCLastScan="DontScan" ProjectSN="16#0000_0000" MatchProjectToController="false" CanUseRPIFromProducer="false" InhibitAutomaticFirmwareUpdate="0" PassThroughConfiguration="EnabledWithAppend" DownloadProjectDocumentationAndExtendedProperties="true" DownloadProjectCustomProperties="true" ReportMinorOverflow="false"{ethernet_ip_mode_attr} AutoDiagsEnabled="true" WebServerEnabled="false">
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
{ethernet_ports_xml}</Controller>
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
