"""Minimal-but-valid L5X wrapper: single controller, one empty task/program/
routine, no DataTypes/Modules/AOIs beyond the bare minimum. Callers supply
just the Tags XML body -- this is Approach A from docs/SAMPLE_GENERATION.md,
kept deliberately small since OQ-GENMETHOD (does raw-XML import work
cleanly?) hasn't been confirmed yet. First sample should go through the full
TESTING_PLAN.md loop before this gets used to generate the other 30+.
"""

from __future__ import annotations

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
DEFAULT_SOFTWARE_REVISION = "35.11"


def build_l5x(
    target_name: str,
    tags_xml: str,
    processor_type: str = DEFAULT_PROCESSOR_TYPE,
    major_rev: str = DEFAULT_MAJOR_REV,
    minor_rev: str = DEFAULT_MINOR_REV,
    software_revision: str = DEFAULT_SOFTWARE_REVISION,
    extra_datatypes_xml: str = "",
    extra_rungs_xml: str = "",
) -> str:
    rungs = extra_rungs_xml if extra_rungs_xml.strip() else '              <Rung Number="0" Type="N">\n                <Text>NOP();</Text>\n              </Rung>'
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{software_revision}" TargetName="{target_name}" TargetType="Controller" ContainsContext="false" ExportOptions="References NoRawData L5KData DecoratedData Context Dependencies ForceProtectedEncoding AllProjDocTrans">
  <Controller Use="Target" Name="{target_name}" ProcessorType="{processor_type}" MajorRev="{major_rev}" MinorRev="{minor_rev}" TimeSlice="20" ShareUnusedTimeSlice="1" InstructionSet="v{major_rev}" RedundancyEnabled="false" Class="Standard">
    <DataTypes>
{extra_datatypes_xml}
    </DataTypes>
    <Modules>
      <Module Name="Local" CatalogNumber="{processor_type}" Vendor="1" ProductType="14" ProductCode="149" Major="{major_rev}" Minor="{minor_rev}" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="true">
        <EKey State="ExactMatch"/>
        <Ports>
          <Port Id="1" Address="0" Type="ICP" Upstream="false"/>
        </Ports>
      </Module>
    </Modules>
    <AddOnInstructionDefinitions/>
    <Tags>
{tags_xml}
    </Tags>
    <Programs>
      <Program Name="MainProgram" TestEdits="false" MainRoutineName="MainRoutine" Disabled="false" UseAsFolder="false">
        <Tags/>
        <Routines>
          <Routine Name="MainRoutine" Type="RLL">
            <RLLContent>
{rungs}
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
