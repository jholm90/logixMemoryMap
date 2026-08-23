"""Axis + composite-UDT sweep (James, 2026-08-22): "the axis compost udt
test" -- direct response to his feedback that real axis usage is never the
bare AXIS_CIP_DRIVE predefined type alone, it's wrapped in a "mixed and
garbled" custom UDT, used everywhere in his real programs at 0.01%-tolerance
stakes (OQ-AXISDEEP, OQ-MIXEDUDT).

Modeled directly on a real UDT found in his own corpus: `ts_CIPAxis`
(samples/local/BaillieLeitchField_Edger_20260812_r00.L5X and
SJ_Gormley_20251112_r02.L5X). Real ts_CIPAxis members: AxisName(STRING),
AutoSpeeds(nested UDT), Servo(nested UDT "udtServo"), AOI(nested AOI
"DriveAxis" -- a real CIP Motion AOI with a REQUIRED InOut AXIS_CIP_DRIVE
parameter), a hidden-bit BOOL (Enabled), and 4 DINT members (ONS/Test/
RunCond/SafetyCond).

One piece of that shape is deliberately NOT reproduced as a nested member:
nesting an AOI with a *required InOut* parameter inside a UDT is an
unconfirmed Studio 5000 construct -- InOut params bind to another tag by
reference, and it's not established whether/how that binding is expressed
when the AOI itself is a UDT member rather than a standalone instance tag.
Every other nested-AOI test built so far in this project used AOIs with
only Input/Output params. Rather than guess at unvalidated XML and risk an
import failure, this batch keeps the same real building blocks but proves
out the *composition* a different, confirmable way:

  1. group_composite_udt -- the ts_CIPAxis shape minus its AOI member
     (nested UDT x2 + hidden-bit BOOL + STRING + 4 DINT), at 0/1/10
     instances. Directly targets OQ-MIXEDUDT with a real corpus-derived
     shape, not an artificial one.
  2. group_axis_aoi_inout -- a DriveAxis-shaped AOI (EnableIn/EnableOut +
     one BOOL Input (FaultReset) + one InOut AXIS_CIP_DRIVE param
     (Drive_Axis)), instantiated as its own top-level tag, alongside a real
     AXIS_CIP_DRIVE tag (copied shape from samples/generated/axis/
     axis_cip_drive_only.L5X, which needs its own MotionGroup tag) and one
     rung calling the AOI with the axis tag wired into the InOut slot --
     the real, standard CIP Motion AOI call pattern. Tests whether an
     axis-via-InOut usage inside an AOI call costs anything beyond the
     already-known axis-alone number (16,888 blocks over the MotionGroup
     baseline) and the AOI's own definition/instance cost.
  3. group_full_combo -- axis tag + MotionGroup + the composite UDT (1
     instance) + the DriveAxis-shaped AOI instance + call rung, all in one
     file. This is the actual "axis composite udt" ensemble test: if the
     individually-confirmed formulas (axis constant, UDT composite cost,
     AOI def+instance cost) are truly additive, this file's real Capacity
     number should equal their sum, same validation method that already
     worked for OQ-LARGEMIXED.

Run: python -m sample_gen.gen_axis_composite
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import MemberSpec, aoi_xml, collect_nested_datatypes, rung_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "axis"


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    """Like _write, but for files containing an AXIS_*/MOTION_GROUP tag --
    those are unmodeled predefined structures (OQ-AXISSTRUCT), so the raw
    sizing engine can't compute predicted_bytes for them at all (confirmed:
    explicit SizeError, not a crash). Bypasses write_sample()'s strict
    predicted_bytes requirement and logs predicted_bytes=0 with a note, same
    convention already used for axis_cip_drive_only.L5X etc. in
    manifest.csv."""
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, f"{description} (unmodeled predefined structure)", "axis", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- unmodeled axis structure)")

# Real shape, copied verbatim from samples/generated/axis/axis_cip_drive_only.L5X
# (itself confirmed against James's real corpus) -- an AXIS_CIP_DRIVE tag
# requires a MotionGroup tag to reference, both are needed together.
_AXIS_TAG_XML = (
    '      <Tag Name="Axis_Cip_Drive" TagType="Base" DataType="AXIS_CIP_DRIVE" ExternalAccess="Read/Write">\n'
    '        <Data Format="Axis">\n'
    '<AxisParameters MotionGroup="MotionGroup" MotionModule="&lt;NA>" ApplicationCatalogNumberInstance="0" ApplicationCatalogNumberVersion="0" AxisConfiguration="Position Loop" FeedbackConfiguration="Motor Feedback" MotorDataSource="Nameplate Datasheet" MotorCatalogNumber="&lt;none>" Feedback1Type="Not Specified" MotorType="Not Specified" MotionScalingConfiguration="Control Scaling"\n'
    ' ConversionConstant="1000000.0" OutputCamExecutionTargets="0" PositionUnits="Position Units" AverageVelocityTimebase="0.25" PositionUnwind="1000000" HomeMode="Active" HomeDirection="Bi-directional Forward" HomeSequence="Immediate" HomeConfigurationBits="16#0000_0000" HomePosition="0.0" HomeOffset="0.0"\n'
    ' HomeSpeed="0.0" HomeReturnSpeed="0.0" MaximumSpeed="0.0" MaximumAcceleration="0.0" MaximumDeceleration="0.0" ProgrammedStopMode="Fast Stop" MasterInputConfigurationBits="1" MasterPositionFilterBandwidth="0.1" VelocityFeedforwardGain="0.0" AccelerationFeedforwardGain="0.0" PositionErrorTolerance="0.0"\n'
    ' PositionLockTolerance="0.01" VelocityOffset="0.0" TorqueOffset="0.0" BacklashReversalOffset="0.0" TuningTravelLimit="0.0" TuningSpeed="0.0" TuningTorque="100.0" DampingFactor="1.0" DriveModelTimeConstant="0.0015" PositionServoBandwidth="16.0" VelocityServoBandwidth="40.0"\n'
    ' VelocityStandstillWindow="1.0" TorqueLimitPositive="0.0" TorqueLimitNegative="0.0" StoppingTorque="0.0" LoadInertiaRatio="0.0" RegistrationInputs="1" MaximumAccelerationJerk="0.0" MaximumDecelerationJerk="0.0" DynamicsConfigurationBits="7" PositionIntegratorBandwidth="0.0" PositionIntegratorControl="0"\n'
    ' VelocityIntegratorControl="0" SystemInertia="0.0" StoppingAction="Current Decel Disable" InverterCapacity="0.0" CIPAxisExceptionAction="Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported" CIPAxisExceptionActionRA="Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported" MotorUnit="Rev" Feedback1Unit="Rev" ScalingSource="From Calculator" LoadType="Direct Coupled Rotary" ActuatorType="&lt;none>"\n'
    ' TravelMode="Unlimited" PositionScalingNumerator="1.0" PositionScalingDenominator="1.0" PositionUnwindNumerator="1.0" PositionUnwindDenominator="1.0" TravelRange="1000.0" MotionResolution="1000000" MotionPolarity="Normal" MotorTestResistance="0.0" MotorTestInductance="0.0" TuneFriction="0.0"\n'
    ' TuneLoadOffset="0.0" TuningSelect="Total Inertia" TuningDirection="Uni-directional Forward" ApplicationType="Basic" LoopResponse="Medium" PositionLoopBandwidth="0.0" VelocityLoopBandwidth="0.0" VelocityIntegratorBandwidth="0.0" MotionExceptionAction="Unsupported Disable Disable Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported Unsupported" SoftTravelLimitChecking="false" LoadRatio="0.0"\n'
    ' TuneInertiaMass="0.0" SoftTravelLimitPositive="0.0" SoftTravelLimitNegative="0.0" GainTuningConfigurationBits="16#0141" SystemBandwidth="0.0" TransmissionRatioInput="1" TransmissionRatioOutput="1" ActuatorLead="1.0" ActuatorLeadUnit="Millimeter/Rev" ActuatorDiameter="1.0" ActuatorDiameterUnit="Millimeter"\n'
    ' SystemAccelerationBase="0.0" DriveModelTimeConstantBase="0.0015" DriveRatedPeakCurrent="0.0" HookupTestDistance="1.0" HookupTestFeedbackChannel="Feedback 1" LoadCoupling="Rigid" SystemDamping="1.0" AxisID="510977205" InterpolatedPositionConfiguration="16#0000_0002" AxisUpdateSchedule="Base" BusOvervoltageOperationalLimit="0.0"\n'
    ' CurrentLoopBandwidthScalingFactor="0.0" CurrentLoopBandwidth="0.0" DriveRatedVoltage="0.0" MaxOutputFrequency="0.0" MotorTestDataValid="False" HookupTestSpeed="0.0" TestModeConfiguration="Controller Loop Back" TestModeEnable="Disabled"/>\n'
    '        </Data>\n'
    '      </Tag>\n'
    '      <Tag Name="MotionGroup" TagType="Base" DataType="MOTION_GROUP" ExternalAccess="Read/Write">\n'
    '        <Data Format="MotionGroup">\n'
    '<MotionGroupParameters CoarseUpdatePeriod="2000" PhaseShift="0" GeneralFaultType="Non Major Fault" AutoTagUpdate="Enabled" Alternate1UpdateMultiplier="1" Alternate2UpdateMultiplier="1"/>\n'
    '        </Data>\n'
    '      </Tag>'
)

# Real AXIS_VIRTUAL tag shape (near-verbatim from samples/local/L5X_Samples/
# Griffin_StackerLine_1Mar25_r00.L5X's VM305_StackerVirtual/VM308_PeelersVirtual,
# only the tag name changed) -- confirmed 2026-08-25 while investigating
# OQ-CROUT-MAPC-BUILDFAIL: real MAPC calls in that corpus ALWAYS use two
# DISTINCT axis tags for the slave/master operand positions, and in every
# example found, of two DIFFERENT DataTypes (AXIS_CIP_DRIVE for the real
# physical slave axis, AXIS_VIRTUAL for the master/reference axis) -- the
# original gen_instruction_firstpass.py MAPC reproduction reused the SAME
# Axis_Cip_Drive tag for both positions, which real Logix never does and is
# the leading suspect for that file's build failure. Shares the MotionGroup
# tag already declared in _AXIS_TAG_XML above -- only include one of the two
# constants per file's tags_xml, not both MotionGroup declarations.
_AXIS_VIRTUAL_TAG_XML = (
    '      <Tag Name="Axis_Virtual" TagType="Base" DataType="AXIS_VIRTUAL" ExternalAccess="Read/Write">\n'
    '        <Data Format="Axis">\n'
    '<AxisParameters MotionGroup="MotionGroup" ConversionConstant="8000.0" OutputCamExecutionTargets="0" PositionUnits="Percentage" AverageVelocityTimebase="0.25" RotaryAxis="Rotary" PositionUnwind="800000" HomeMode="Active" HomeDirection="Bi-directional Forward" HomeSequence="Immediate" HomeConfigurationBits="16#0000_0000"\n'
    ' HomePosition="0.0" HomeOffset="0.0" MaximumSpeed="100.0" MaximumAcceleration="300.0" MaximumDeceleration="300.0" ProgrammedStopMode="Fast Stop" MasterInputConfigurationBits="1" MasterPositionFilterBandwidth="0.1" MaximumAccelerationJerk="1500.0" MaximumDecelerationJerk="1500.0" DynamicsConfigurationBits="7"\n'
    ' InterpolatedPositionConfiguration="16#0000_0002" AxisUpdateSchedule="Alternate 1"/>\n'
    '        </Data>\n'
    '      </Tag>'
)


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "axis", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


# ---------------------------------------------------------------------------
# 1. Composite UDT matching real ts_CIPAxis shape (minus the nested-AOI
#    member -- see module docstring), at 0/1/10 instances.
# ---------------------------------------------------------------------------

def _composite_members() -> list[MemberSpec]:
    auto_speeds = [
        MemberSpec("JogSpeed", "REAL"),
        MemberSpec("MaxSpeed", "REAL"),
        MemberSpec("HomeSpeed", "REAL"),
    ]
    servo = [
        MemberSpec("Kp", "DINT"),
        MemberSpec("Ki", "DINT"),
        MemberSpec("Enable", "BOOL"),
    ]
    return [
        MemberSpec("AxisName", "STRING"),
        MemberSpec("AutoSpeeds", "AutoSpeeds_Test", nested_members=tuple(auto_speeds)),
        MemberSpec("Servo", "udtServo_Test", nested_members=tuple(servo)),
        MemberSpec("Enabled", "BOOL"),
        MemberSpec("ONS", "DINT"),
        MemberSpec("Test", "DINT"),
        MemberSpec("RunCond", "DINT"),
        MemberSpec("SafetyCond", "DINT"),
    ]


def group_composite_udt() -> None:
    members = _composite_members()
    datatypes = collect_nested_datatypes("ts_CIPAxis_Test", members)

    l5x = build_l5x(target_name="CompositeUdt", tags_xml="", extra_datatypes_xml=datatypes)
    _write(l5x, "axis_composite_udt_def_only", "ts_CIPAxis-shaped composite UDT (nested UDT x2, hidden-bit BOOL, STRING, 4 DINT), 0 instances")

    tag = tag_xml("Inst1", "ts_CIPAxis_Test", udt_members=members)
    l5x = build_l5x(target_name="CompositeUdt", tags_xml=tag, extra_datatypes_xml=datatypes)
    _write(l5x, "axis_composite_udt_1_instance", "ts_CIPAxis-shaped composite UDT, 1 instance")

    tag = tag_xml("Inst10", "ts_CIPAxis_Test", dimensions=(10,), udt_members=members)
    l5x = build_l5x(target_name="CompositeUdt", tags_xml=tag, extra_datatypes_xml=datatypes)
    _write(l5x, "axis_composite_udt_10_instance", "ts_CIPAxis-shaped composite UDT, array of 10 instances")


# ---------------------------------------------------------------------------
# 2. DriveAxis-shaped AOI (BOOL Input + InOut AXIS_CIP_DRIVE), called from a
#    rung wired to a real axis tag.
# ---------------------------------------------------------------------------

def group_axis_aoi_inout() -> None:
    fault_reset = MemberSpec("FaultReset", "BOOL")
    drive_axis = MemberSpec("Drive_Axis", "AXIS_CIP_DRIVE")

    definition, storage = aoi_xml("DriveAxisTest", input_params=[fault_reset], inout_params=[drive_axis])
    inst_tag = tag_xml("DriveAxisInst", "DriveAxisTest", udt_members=storage)
    fault_tag = tag_xml("FaultResetVal", "BOOL")

    tags = "\n".join([_AXIS_TAG_XML, inst_tag, fault_tag])
    # Real AOI call syntax: instance tag first, then Parameters in
    # declaration order (Input, Output, InOut) -- here just FaultReset then
    # the axis tag reference for the InOut slot.
    rung = rung_xml(0, "DriveAxisTest(DriveAxisInst,FaultResetVal,Axis_Cip_Drive);")
    l5x = build_l5x(target_name="AxisAoiInout", tags_xml=tags, extra_aoi_xml=definition, extra_rungs_xml=rung)
    _write_unmodeled(l5x, "axis_aoi_inout_1_instance",
           "Real AXIS_CIP_DRIVE tag + AOI with BOOL Input + InOut AXIS_CIP_DRIVE param, called from a rung, 1 instance")


# ---------------------------------------------------------------------------
# 3. Full combo: axis + composite UDT (1 instance) + AOI-with-InOut-axis
#    call, all in one file -- the additivity test.
# ---------------------------------------------------------------------------

def group_full_combo() -> None:
    members = _composite_members()
    datatypes = collect_nested_datatypes("ts_CIPAxis_Test", members)
    udt_tag = tag_xml("CompositeInst", "ts_CIPAxis_Test", udt_members=members)

    fault_reset = MemberSpec("FaultReset", "BOOL")
    drive_axis = MemberSpec("Drive_Axis", "AXIS_CIP_DRIVE")
    definition, storage = aoi_xml("DriveAxisTest", input_params=[fault_reset], inout_params=[drive_axis])
    inst_tag = tag_xml("DriveAxisInst", "DriveAxisTest", udt_members=storage)
    fault_tag = tag_xml("FaultResetVal", "BOOL")

    tags = "\n".join([_AXIS_TAG_XML, udt_tag, inst_tag, fault_tag])
    rung = rung_xml(0, "DriveAxisTest(DriveAxisInst,FaultResetVal,Axis_Cip_Drive);")
    l5x = build_l5x(target_name="AxisFullCombo", tags_xml=tags, extra_datatypes_xml=datatypes,
                     extra_aoi_xml=definition, extra_rungs_xml=rung)
    _write_unmodeled(l5x, "axis_full_combo",
           "Real AXIS_CIP_DRIVE tag + ts_CIPAxis-shaped composite UDT (1 instance) + AOI-with-InOut-axis call, "
           "all together -- additivity check against the individually-confirmed constants")


def main() -> None:
    group_composite_udt()
    group_axis_aoi_inout()
    group_full_combo()
    print("\nDone. 5 files.")


if __name__ == "__main__":
    main()
