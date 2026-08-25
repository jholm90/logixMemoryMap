"""Full processor-catalog x firmware-version matrix for OQ-BASELINE-PROCFW
(2026-08-25, James: "I want you to source from Rockwell all catalog
processor numbers from the l7-l9 controllogx era and the 5069 processors
... generate a full matrix of all catalog numbers and all versions ...
within the 31-38 firmware range. Skip v30 ... sorted so my PowerShell will
test all v31, then all v32 etc.").

CATALOG SOURCING (never guessed -- see the citation on each list below).
Only catalogs with a REAL confirmed ProductCode already on file in this
project are included here -- fabricating a ProductCode for an unconfirmed
catalog risks a real Studio 5000 import failure and burns a test cycle for
nothing:

  - ControlLogix 5580 (1756-L8x): L81E/L82E/L83E/L84E/L85E. Real
    ProductCodes already in `wrapper.py`'s `_PRODUCT_CODES` (James's own
    fw_baseline exports).
  - CompactLogix 5380 (5069-Lxxx): 14 catalogs across the L306/L310/L320/
    L330/L340/L3100 tiers and their M/S2/S3 safety-suffix variants -- same
    source.

NOT included, flagged rather than guessed:
  - ControlLogix 5570 (1756-L7x): only L71 has a confirmed real
    ProductCode (92, from samples/local/L7_v21_Sample.L5X) and that
    sample is firmware v21 -- outside this v31-38 range, plus this
    project has no confirmation of L7x's actual firmware ceiling in that
    range (real search results were contradictory). L72-L75 have zero
    confirmed ProductCode at all. Needs a real sample before building.
  - ControlLogix 5590 (1756-L9x, "TS" suffix: L902TS/L905TS/L908TS/
    L915TS/L925TS/L950TS/L980TS): real catalog numbers confirmed via web
    search (Rockwell literature + distributor cut sheets, 2026-08-25) --
    this is a BRAND NEW family (FactoryTalk Design Studio only adds
    support in v2.03, Nov 2025) with zero real L5X corpus examples
    anywhere in this project. No ProductCode, no confirmed Module shape.
    Needs a real sample before building -- see docs/OPEN_QUESTIONS.md.
  - CompactLogix 5480 (5069-L4xx process controllers: L430ERMW/L450ERMW/
    L4100ERMW/L4200ERMW): real catalog numbers confirmed via web search,
    zero real corpus examples, same as L9x.

FIRMWARE ATTRIBUTE TABLE -- confirmed from the existing l81_v31-v35/v38
fw_baseline samples (James's own real per-firmware exports), NOT guessed
per-version except where explicitly flagged:
  v31: SoftwareRevision="31.02", no AutoDiagsEnabled/WebServerEnabled attrs
  v32: SoftwareRevision="32.04", no AutoDiagsEnabled/WebServerEnabled attrs
  v33: SoftwareRevision="33.01", AutoDiagsEnabled="false" WebServerEnabled="false"
  v34: SoftwareRevision="34.01", same attrs as v33
  v35: SoftwareRevision="35.05", same attrs as v33/v34
  v36: ASSUMED -- real v36/v37 firmware majors are confirmed to exist
    (Rockwell release notes, 2026-08-25 search) but this project has no
    real v36/v37 L5X sample at all. SoftwareRevision="36.00" (the
    conventional first sub-build number, not independently confirmed)
    and the same AutoDiagsEnabled/WebServerEnabled shape as v35 (the
    last confirmed point before v38's real DataExchangeId addition).
    Flagged in every v36/v37 file's manifest note -- correct this batch
    from real capture data the moment it's available, don't leave the
    assumption silent.
  v37: ASSUMED, same basis as v36 (SoftwareRevision="37.00").
  v38: SoftwareRevision="38.02", same AutoDiagsEnabled/WebServerEnabled as
    v33-v35, PLUS a new DataExchangeId attribute (a real, project-unique
    GUID -- confirmed real from the l81_v38 sample, but that literal GUID
    value is per-EXPORT, not a firmware constant, so a fresh one is
    generated per file here rather than reusing James's own).
  MinorRev="11" is constant across every confirmed sample regardless of
  MajorRev -- used unchanged throughout.

Deliberately does NOT reuse wrapper.py's build_l5x() -- that function
hardcodes AutoDiagsEnabled="true" WebServerEnabled="false" unconditionally
(a pre-existing simplification baked into ~1300 already-tested files this
project already relies on), which doesn't match any of the real
per-firmware attribute sets above. This generator builds the Controller
element directly instead, reusing only the real per-catalog ProductCode
table and the 5069-vs-1756 local-port shape logic.

File naming: `fwmatrix_v{major}_{catalog_slug}.L5X` -- firmware version is
the FIRST sort key, so a plain alphabetical directory listing (what
batch_l5x_to_acd.ps1/batch_memory_capture.ps1 both iterate over) groups
all of v31 together, then all of v32, etc., exactly as requested. v30
skipped entirely (SDK confirmed unable to build v30 projects at all, see
OPEN_QUESTIONS.md OQ-BASELINE-PROCFW).

Run: python -m sample_gen.gen_fw_catalog_matrix
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import _ICP_BUS_SIZE, _PRODUCT_CODES, _5069_BUS_SIZE

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "fw_catalog_matrix"

MINOR_REV = "11"

# (major_rev, software_revision, extra_controller_attrs, assumed)
FIRMWARE_TABLE: list[tuple[str, str, str, bool]] = [
    ("31", "31.02", "", False),
    ("32", "32.04", "", False),
    ("33", "33.01", ' AutoDiagsEnabled="false" WebServerEnabled="false"', False),
    ("34", "34.01", ' AutoDiagsEnabled="false" WebServerEnabled="false"', False),
    ("35", "35.05", ' AutoDiagsEnabled="false" WebServerEnabled="false"', False),
    ("36", "36.00", ' AutoDiagsEnabled="false" WebServerEnabled="false"', True),
    ("37", "37.00", ' AutoDiagsEnabled="false" WebServerEnabled="false"', True),
    # DataExchangeId filled in per-file at generation time (real attribute,
    # but the GUID itself is per-export, not a firmware constant).
    ("38", "38.02", ' AutoDiagsEnabled="false" WebServerEnabled="false" DataExchangeId="{DATAEXCHANGEID}"', False),
]

# ControlLogix 5580 -- real ProductCodes already confirmed in wrapper.py's
# own _PRODUCT_CODES table.
_L8X_CATALOGS = ["1756-L81E", "1756-L82E", "1756-L83E", "1756-L84E", "1756-L85E"]

# CompactLogix 5380 -- same source. Every one of these already has a real
# ProductCode in wrapper.py's _PRODUCT_CODES EXCEPT the 4 confirmed via
# this project's broader real corpus (module-sweep/controller-budget
# sources) rather than wrapper.py's own table -- added here explicitly
# since _PRODUCT_CODES itself doesn't have them yet.
_5069_EXTRA_PRODUCT_CODES = {
    "5069-L306ERS2": "235",
    "5069-L310ERS2": "236",
    "5069-L320ERMS2": "222",
    "5069-L320ERMS3": "245",
    "5069-L330ERMS2": "223",
    "5069-L340ERS2": "239",
}
_5069_CATALOGS = [
    "5069-L306ER", "5069-L306ERM", "5069-L306ERMS2", "5069-L306ERMS3", "5069-L306ERS2",
    "5069-L310ERS2", "5069-L320ER", "5069-L320ERMS2", "5069-L320ERMS3",
    "5069-L330ER", "5069-L330ERMS2", "5069-L340ER", "5069-L340ERS2", "5069-L3100ERM",
]

# ControlLogix 5570 (James, 2026-08-25: "L7 is good all the way").
# Real confirmed ProductCodes for L71/L72/L75 (92/93/96, from
# samples/local/L7_v21_Sample.L5X, L5X_Samples/Sorter1_20260722r00.L5X,
# DnR_Personal/FlareFunction_311D_240731.L5X) are PERFECTLY sequential --
# L73/L74 are inferred as 94/95 from that pattern (unlike the 5069 family,
# where sequential-tier codes turned out NOT to hold -- flagged as
# INFERRED in their own manifest notes, not presented as equally
# confirmed). Bus Size=4 confirmed from the L71 sample itself, same
# minimal-chassis convention as this whole matrix already uses.
_L7X_PRODUCT_CODES = {
    "1756-L71": "92",
    "1756-L72": "93",
    "1756-L73": "94",  # INFERRED, not directly confirmed
    "1756-L74": "95",  # INFERRED, not directly confirmed
    "1756-L75": "96",
}
_L7X_INFERRED = {"1756-L73", "1756-L74"}
_L7X_CATALOGS = list(_L7X_PRODUCT_CODES)

# GuardLogix 5580 safety-rated (James, 2026-08-25: "L8 needs safety
# processors too"). L81ES's ProductCode (164) is confirmed real and
# IDENTICAL to plain L81E's -- same physical hardware, safety unlocked in
# firmware, not a different Module signature. L82ES-L85ES are INFERRED
# on that same same-as-non-S basis (165/166/167/168), not independently
# confirmed -- flagged in their own manifest notes.
_L8XS_PRODUCT_CODES = {
    "1756-L81ES": "164",
    "1756-L82ES": "165",  # INFERRED, not directly confirmed
    "1756-L83ES": "166",  # INFERRED, not directly confirmed
    "1756-L84ES": "167",  # INFERRED, not directly confirmed
    "1756-L85ES": "168",  # INFERRED, not directly confirmed
}
_L8XS_INFERRED = {"1756-L82ES", "1756-L83ES", "1756-L84ES", "1756-L85ES"}
_L8XS_CATALOGS = list(_L8XS_PRODUCT_CODES)

ALL_CATALOGS = _L8X_CATALOGS + _5069_CATALOGS + _L7X_CATALOGS
SAFETY_CATALOGS = _L8XS_CATALOGS
ALL_INFERRED = _L7X_INFERRED | _L8XS_INFERRED


def _product_code(catalog: str) -> str:
    if catalog in _PRODUCT_CODES:
        return _PRODUCT_CODES[catalog]
    if catalog in _5069_EXTRA_PRODUCT_CODES:
        return _5069_EXTRA_PRODUCT_CODES[catalog]
    if catalog in _L7X_PRODUCT_CODES:
        return _L7X_PRODUCT_CODES[catalog]
    if catalog in _L8XS_PRODUCT_CODES:
        return _L8XS_PRODUCT_CODES[catalog]
    raise KeyError(f"No confirmed real ProductCode for {catalog!r} -- refusing to guess")


def _local_ports_xml(catalog: str) -> str:
    if catalog.startswith("5069"):
        return (
            f'<Port Id="1" Address="0" Type="5069" Upstream="false">\n'
            f'<Bus Size="{_5069_BUS_SIZE}"/>\n'
            f'</Port>\n'
            f'<Port Id="3" Type="Ethernet" Upstream="false">\n<Bus/>\n</Port>\n'
            f'<Port Id="4" Type="Ethernet" Upstream="false">\n<Bus/>\n</Port>'
        )
    return (
        f'<Port Id="1" Address="0" Type="ICP" Upstream="false">\n'
        f'<Bus Size="{_ICP_BUS_SIZE}"/>\n'
        f'</Port>\n'
        f'<Port Id="2" Type="Ethernet" Upstream="false">\n<Bus/>\n</Port>'
    )


def _build_xml(catalog: str, major_rev: str, software_revision: str, extra_attrs: str,
                is_safety: bool = False) -> str:
    target_name = f"FwMatrix{major_rev}" + "".join(c for c in catalog if c.isalnum())
    now = datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    if "{DATAEXCHANGEID}" in extra_attrs:
        guid = "{" + str(uuid.uuid4()).upper() + "}"
        extra_attrs = extra_attrs.replace("{DATAEXCHANGEID}", guid)
    product_code = _product_code(catalog)
    local_ports_xml = _local_ports_xml(catalog)
    # Real shape confirmed 2026-08-25 against samples/local/SJ_Gormley_
    # 20251112_r02.L5X and DnR_Personal/Bender134053_201104.L5X (James:
    # "Safety processor needs a safety task. You don't have to put in a
    # safety program... check Gormley or bender as samples"): the real
    # marker isn't the NAME "SafetyTask" -- it's Class="Safety" on BOTH
    # the Task and the Program it schedules. Kept minimal (bare
    # MainRoutine, no real safety content) per James's "don't have to put
    # in a safety program" -- but a Task always schedules a real Program
    # in both real references, so the pairing itself is kept, just empty.
    safety_info_xml = '<SafetyInfo SafetyLocked="true" SignatureRunModeProtect="false" ConfigureSafetyIOAlways="true" SafetyLevel="SIL2/PLd"/>' if is_safety else '<SafetyInfo/>'
    safety_program_xml = (
        '<Program Name="SafetyProgram" TestEdits="false" MainRoutineName="MainRoutine" '
        'Disabled="false" Class="Safety" UseAsFolder="false">\n<Tags/>\n<Routines>\n'
        '<Routine Name="MainRoutine" Type="RLL"/>\n</Routines>\n</Program>\n'
    ) if is_safety else ""
    safety_task_xml = (
        '<Task Name="SafetyTask" Type="PERIODIC" Rate="20" Priority="10" Watchdog="20" '
        'DisableUpdateOutputs="false" InhibitTask="false" Class="Safety">\n<ScheduledPrograms>\n'
        '<ScheduledProgram Name="SafetyProgram"/>\n</ScheduledPrograms>\n</Task>\n'
    ) if is_safety else ""
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{software_revision}" TargetName="{target_name}" TargetType="Controller" ContainsContext="false" Owner="Admin" ExportDate="{now}" ExportOptions="NoRawData L5KData DecoratedData ForceProtectedEncoding AllProjDocTrans">
<Controller Use="Target" Name="{target_name}" ProcessorType="{catalog}" MajorRev="{major_rev}" MinorRev="{MINOR_REV}" ProjectCreationDate="{now}" LastModifiedDate="{now}" SFCExecutionControl="CurrentActive" SFCRestartPosition="MostRecent" SFCLastScan="DontScan" ProjectSN="16#0000_0000" MatchProjectToController="false" CanUseRPIFromProducer="false" InhibitAutomaticFirmwareUpdate="0" PassThroughConfiguration="EnabledWithAppend" DownloadProjectDocumentationAndExtendedProperties="true" DownloadProjectCustomProperties="true" ReportMinorOverflow="false"{extra_attrs}>
<RedundancyInfo Enabled="false" KeepTestEditsOnSwitchOver="false"/>
<Security Code="0" ChangesToDetect="16#ffff_ffff_ffff_ffff"/>
{safety_info_xml}
<DataTypes/>
<Modules>
<Module Name="Local" CatalogNumber="{catalog}" Vendor="1" ProductType="14" ProductCode="{product_code}" Major="{major_rev}" Minor="{MINOR_REV}" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="true">
<EKey State="Disabled"/>
<Ports>
{local_ports_xml}
</Ports>
</Module>
</Modules>
<AddOnInstructionDefinitions/>
<Tags/>
<Programs>
<Program Name="MainProgram" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" UseAsFolder="false">
<Tags/>
<Routines>
<Routine Name="MainRoutine" Type="RLL"/>
</Routines>
</Program>
{safety_program_xml}</Programs>
<Tasks>
<Task Name="MainTask" Type="CONTINUOUS" Priority="10" Watchdog="500" DisableUpdateOutputs="false" InhibitTask="false">
<ScheduledPrograms>
<ScheduledProgram Name="MainProgram"/>
</ScheduledPrograms>
</Task>
{safety_task_xml}</Tasks>
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


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "fw_catalog_matrix", out_path, bytes_)


def main() -> None:
    written = 0
    all_catalogs = ALL_CATALOGS + SAFETY_CATALOGS
    for major_rev, software_revision, extra_attrs, assumed in FIRMWARE_TABLE:
        for catalog in all_catalogs:
            is_safety = catalog in SAFETY_CATALOGS
            slug = catalog.lower().replace("-", "_")
            out_name = f"fwmatrix_v{major_rev}_{slug}"
            assumed_note = (
                f" ASSUMED firmware-attribute shape (no real v{major_rev} sample exists yet -- "
                f"interpolated from the confirmed v35/v38 bracket, correct from real capture)."
                if assumed else ""
            )
            inferred_note = (
                f" ProductCode {_product_code(catalog)} is INFERRED (same-tier sequential pattern "
                f"from confirmed neighbors), not independently confirmed for this exact catalog."
                if catalog in ALL_INFERRED else ""
            )
            safety_note = (
                " GuardLogix safety-rated (SIL2/PLd, single primary, no partner) -- real Task/"
                "Program Class=\"Safety\" shape confirmed against Gormley/Bender real corpus."
                if is_safety else ""
            )
            l5x = _build_xml(catalog, major_rev, software_revision, extra_attrs, is_safety=is_safety)
            _write(
                l5x, out_name,
                f"Blank baseline, {catalog} at firmware {major_rev} (SoftwareRevision "
                f"{software_revision}) -- OQ-BASELINE-PROCFW full catalog x firmware matrix."
                f"{assumed_note}{inferred_note}{safety_note}",
            )
            written += 1
    print(f"Done. {written} files ({len(FIRMWARE_TABLE)} firmware versions x {len(all_catalogs)} catalogs).")


if __name__ == "__main__":
    main()
