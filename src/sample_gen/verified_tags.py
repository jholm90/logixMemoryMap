"""Verbatim tag XML transplanted from James's own verified sample export.

Source: samples/local/instr_probes/instruction_shapes_20260904.L5X, exported
2026-09-04 from a project James built and BUILT CLEAN in Studio 5000 himself.
Every <Tag> block below is byte-for-byte what Studio wrote -- nothing here is
composed from a manual, and nothing is edited. That is the entire point: the
last three times this project invented predefined-structure XML from the
documentation (the alarm ConditionTypes, the MAM/MAJ bare-2-operand rungs, the
Kinetix `:SI` safety tags) every single invented variant was rejected by the
real toolchain.

James, 2026-09-04: "note i used virtual axis and not the hardware, but any
AXIS_** type tag should work. i dont know if you are aware of the difference
between them" -- AXIS_VIRTUAL carries no drive/module binding at all
(MotionGroupInstance="<NA>", no associated module), where AXIS_CIP_DRIVE
pulls in a real drive module and its connection overhead. For isolating the
cost of a motion INSTRUCTION that is exactly what we want: no module
overhead to subtract back out afterwards.

Regenerate with: python -m sample_gen.extract_verified_tags
"""

from __future__ import annotations

_TAG_AXIS1 = r"""<Tag Name="Axis1" TagType="Base" DataType="AXIS_VIRTUAL" ExternalAccess="Read/Write">
<Data Format="Axis">
<AxisParameters ConversionConstant="8000.0" OutputCamExecutionTargets="0" PositionUnits="Position Units" AverageVelocityTimebase="0.25" RotaryAxis="Linear" PositionUnwind="8000" HomeMode="Active" HomeDirection="Bi-directional Forward" HomeSequence="Immediate" HomeConfigurationBits="16#0000_0000" HomePosition="0.0" HomeOffset="0.0" MaximumSpeed="0.0" MaximumAcceleration="0.0" MaximumDeceleration="0.0" ProgrammedStopMode="Fast Stop" MasterInputConfigurationBits="1" MasterPositionFilterBandwidth="0.1" MaximumAccelerationJerk="0.0" MaximumDecelerationJerk="0.0" DynamicsConfigurationBits="7" InterpolatedPositionConfiguration="16#0000_0002" AxisUpdateSchedule="Base" />
</Data>
</Tag>"""
_TAG_AXIS2 = r"""<Tag Name="Axis2" TagType="Base" DataType="AXIS_VIRTUAL" ExternalAccess="Read/Write">
<Data Format="Axis">
<AxisParameters ConversionConstant="8000.0" OutputCamExecutionTargets="0" PositionUnits="Position Units" AverageVelocityTimebase="0.25" RotaryAxis="Linear" PositionUnwind="8000" HomeMode="Active" HomeDirection="Bi-directional Forward" HomeSequence="Immediate" HomeConfigurationBits="16#0000_0000" HomePosition="0.0" HomeOffset="0.0" MaximumSpeed="0.0" MaximumAcceleration="0.0" MaximumDeceleration="0.0" ProgrammedStopMode="Fast Stop" MasterInputConfigurationBits="1" MasterPositionFilterBandwidth="0.1" MaximumAccelerationJerk="0.0" MaximumDecelerationJerk="0.0" DynamicsConfigurationBits="7" InterpolatedPositionConfiguration="16#0000_0002" AxisUpdateSchedule="Base" />
</Data>
</Tag>"""
_TAG_COORDINATESYSTEM1 = r"""<Tag Name="CoordinateSystem1" TagType="Base" DataType="COORDINATE_SYSTEM" ExternalAccess="Read/Write">
<Data Format="CoordinateSystem">
<CoordinateSystemParameters MotionGroupInstance="&lt;NA&gt;" ApplicationCatalogNumberInstance="0" ApplicationCatalogNumberVersion="0" SystemType="Cartesian" CoordinateDefinition="&lt;none&gt;" Dimension="2" Axes="{none} {none}" MaximumPendingMoves="1" CoordinationMode="Primary Primary" CoordinationUnits="Coordination Units" ConversionRatioNumerator="1.0 1.0" ConversionRatioDenominator="1 1" CoordinateSystemAutoTagUpdate="Enabled" MaximumSpeed="0.0" MaximumAcceleration="0.0" MaximumDeceleration="0.0" ActualPositionTolerance="0.0" CommandPositionTolerance="0.0" TransformDimension="0" LinkLength1="0.0" LinkLength2="0.0" ZeroAngleOffset1="0.0" ZeroAngleOffset2="0.0" ZeroAngleOffset3="0.0" BaseOffset1="0.0" BaseOffset2="0.0" BaseOffset3="0.0" EndEffectorOffset1="0.0" EndEffectorOffset2="0.0" EndEffectorOffset3="0.0" DynamicsConfigurationBits="7" MaximumAccelerationJerk="0.0" MaximumDecelerationJerk="0.0" MasterInputConfigurationBits="1" MasterPositionFilterBandwidth="0.1" LinkLength3="0.0" BallScrewLead="0.0" ZeroAngleOffset4="0.0" ZeroAngleOffset5="0.0" ZeroAngleOffset6="0.0" MaximumOrientationSpeed="0.0" MaximumOrientationAcceleration="0.0" MaximumOrientationDeceleration="0.0" SwingArmA3="0.0" SwingArmD3="0.0" SwingArmA4="0.0" SwingArmD4="0.0" SwingArmD5="0.0" SwingArmCouplingRatioNumerator="1" SwingArmCouplingRatioDenominator="1" SwingArmCouplingDirection="&lt;none&gt;" RobotJointsDirectionSenseBits="0" />
</Data>
</Tag>"""
_TAG_CAM_PROFILE = r"""<Tag Name="Cam_Profile" TagType="Base" DataType="CAM_PROFILE" Dimensions="10" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0
		,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Array DataType="CAM_PROFILE" Dimensions="10">
<Element Index="[0]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[1]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[2]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[3]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[4]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[5]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[6]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[7]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[8]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
<Element Index="[9]">
<Structure DataType="CAM_PROFILE">
<DataValueMember Name="Status" DataType="DINT" Radix="Decimal" Value="0" />
</Structure>
</Element>
</Array>
</Data>
</Tag>"""
_TAG_PID = r"""<Tag Name="PID" TagType="Base" DataType="PID" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,[0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000]]
</Data>
<Data Format="Decorated">
<Structure DataType="PID">
<DataValueMember Name="CTL" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EN" DataType="BOOL" Value="0" />
<DataValueMember Name="CT" DataType="BOOL" Value="0" />
<DataValueMember Name="CL" DataType="BOOL" Value="0" />
<DataValueMember Name="PVT" DataType="BOOL" Value="0" />
<DataValueMember Name="DOE" DataType="BOOL" Value="0" />
<DataValueMember Name="SWM" DataType="BOOL" Value="0" />
<DataValueMember Name="CA" DataType="BOOL" Value="0" />
<DataValueMember Name="MO" DataType="BOOL" Value="0" />
<DataValueMember Name="PE" DataType="BOOL" Value="0" />
<DataValueMember Name="NDF" DataType="BOOL" Value="0" />
<DataValueMember Name="NOBC" DataType="BOOL" Value="0" />
<DataValueMember Name="NOZC" DataType="BOOL" Value="0" />
<DataValueMember Name="INI" DataType="BOOL" Value="0" />
<DataValueMember Name="SPOR" DataType="BOOL" Value="0" />
<DataValueMember Name="OLL" DataType="BOOL" Value="0" />
<DataValueMember Name="OLH" DataType="BOOL" Value="0" />
<DataValueMember Name="EWD" DataType="BOOL" Value="0" />
<DataValueMember Name="DVNA" DataType="BOOL" Value="0" />
<DataValueMember Name="DVPA" DataType="BOOL" Value="0" />
<DataValueMember Name="PVLA" DataType="BOOL" Value="0" />
<DataValueMember Name="PVHA" DataType="BOOL" Value="0" />
<DataValueMember Name="SP" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="KP" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="KI" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="KD" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="BIAS" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MAXS" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MINS" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="DB" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="SO" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MAXO" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MINO" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="UPD" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="PV" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="ERR" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="OUT" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="PVH" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="PVL" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="DVP" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="DVN" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="PVDB" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="DVDB" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MAXI" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MINI" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="TIE" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MAXCV" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MINCV" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MINTIE" DataType="REAL" Radix="Float" Value="0.0" />
<DataValueMember Name="MAXTIE" DataType="REAL" Radix="Float" Value="0.0" />
<ArrayMember Name="DATA" DataType="REAL" Dimensions="17" Radix="Float">
<Element Index="[0]" Value="0.0" />
<Element Index="[1]" Value="0.0" />
<Element Index="[2]" Value="0.0" />
<Element Index="[3]" Value="0.0" />
<Element Index="[4]" Value="0.0" />
<Element Index="[5]" Value="0.0" />
<Element Index="[6]" Value="0.0" />
<Element Index="[7]" Value="0.0" />
<Element Index="[8]" Value="0.0" />
<Element Index="[9]" Value="0.0" />
<Element Index="[10]" Value="0.0" />
<Element Index="[11]" Value="0.0" />
<Element Index="[12]" Value="0.0" />
<Element Index="[13]" Value="0.0" />
<Element Index="[14]" Value="0.0" />
<Element Index="[15]" Value="0.0" />
<Element Index="[16]" Value="0.0" />
</ArrayMember>
</Structure>
</Data>
</Tag>"""
_TAG_CMPCTRL = r"""<Tag Name="CmpCtrl" TagType="Base" DataType="CONTROL" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,10,0]
</Data>
<Data Format="Decorated">
<Structure DataType="CONTROL">
<DataValueMember Name="LEN" DataType="DINT" Radix="Decimal" Value="10" />
<DataValueMember Name="POS" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EN" DataType="BOOL" Value="0" />
<DataValueMember Name="EU" DataType="BOOL" Value="0" />
<DataValueMember Name="DN" DataType="BOOL" Value="0" />
<DataValueMember Name="EM" DataType="BOOL" Value="0" />
<DataValueMember Name="ER" DataType="BOOL" Value="0" />
<DataValueMember Name="UL" DataType="BOOL" Value="0" />
<DataValueMember Name="IN" DataType="BOOL" Value="0" />
<DataValueMember Name="FD" DataType="BOOL" Value="0" />
</Structure>
</Data>
</Tag>"""
_TAG_RESULTCTRL = r"""<Tag Name="ResultCtrl" TagType="Base" DataType="CONTROL" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,10,0]
</Data>
<Data Format="Decorated">
<Structure DataType="CONTROL">
<DataValueMember Name="LEN" DataType="DINT" Radix="Decimal" Value="10" />
<DataValueMember Name="POS" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EN" DataType="BOOL" Value="0" />
<DataValueMember Name="EU" DataType="BOOL" Value="0" />
<DataValueMember Name="DN" DataType="BOOL" Value="0" />
<DataValueMember Name="EM" DataType="BOOL" Value="0" />
<DataValueMember Name="ER" DataType="BOOL" Value="0" />
<DataValueMember Name="UL" DataType="BOOL" Value="0" />
<DataValueMember Name="IN" DataType="BOOL" Value="0" />
<DataValueMember Name="FD" DataType="BOOL" Value="0" />
</Structure>
</Data>
</Tag>"""
_TAG_DINT_ARR1 = r"""<Tag Name="DINT_Arr1" TagType="Base" DataType="DINT" Dimensions="10" Radix="Decimal" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Array DataType="DINT" Dimensions="10" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
</Array>
</Data>
</Tag>"""
_TAG_DINT_ARR2 = r"""<Tag Name="DINT_Arr2" TagType="Base" DataType="DINT" Dimensions="10" Radix="Decimal" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Array DataType="DINT" Dimensions="10" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
</Array>
</Data>
</Tag>"""
_TAG_DINT_ARR3 = r"""<Tag Name="DINT_Arr3" TagType="Base" DataType="DINT" Dimensions="10" Radix="Decimal" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Array DataType="DINT" Dimensions="10" Radix="Decimal">
<Element Index="[0]" Value="0" />
<Element Index="[1]" Value="0" />
<Element Index="[2]" Value="0" />
<Element Index="[3]" Value="0" />
<Element Index="[4]" Value="0" />
<Element Index="[5]" Value="0" />
<Element Index="[6]" Value="0" />
<Element Index="[7]" Value="0" />
<Element Index="[8]" Value="0" />
<Element Index="[9]" Value="0" />
</Array>
</Data>
</Tag>"""
_TAG_SRC = r"""<Tag Name="Src" TagType="Base" DataType="REAL" Radix="Float" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
0.00000000e+000
</Data>
<Data Format="Decorated">
<DataValue DataType="REAL" Radix="Float" Value="0.0" />
</Data>
</Tag>"""
_TAG_DST = r"""<Tag Name="Dst" TagType="Base" DataType="REAL" Radix="Float" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
0.00000000e+000
</Data>
<Data Format="Decorated">
<DataValue DataType="REAL" Radix="Float" Value="0.0" />
</Data>
</Tag>"""
_TAG_POSN = r"""<Tag Name="Posn" TagType="Base" DataType="REAL" Dimensions="10" Radix="Float" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000]
</Data>
<Data Format="Decorated">
<Array DataType="REAL" Dimensions="10" Radix="Float">
<Element Index="[0]" Value="0.0" />
<Element Index="[1]" Value="0.0" />
<Element Index="[2]" Value="0.0" />
<Element Index="[3]" Value="0.0" />
<Element Index="[4]" Value="0.0" />
<Element Index="[5]" Value="0.0" />
<Element Index="[6]" Value="0.0" />
<Element Index="[7]" Value="0.0" />
<Element Index="[8]" Value="0.0" />
<Element Index="[9]" Value="0.0" />
</Array>
</Data>
</Tag>"""
_TAG_STRING = r"""<Tag Name="String" TagType="Base" DataType="STRING" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,'$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00$00'
		]
</Data>
<Data Format="String" Length="0">
''
</Data>
</Tag>"""
_TAG_DINT = r"""<Tag Name="dint" TagType="Base" DataType="DINT" Radix="Decimal" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
0
</Data>
<Data Format="Decorated">
<DataValue DataType="DINT" Radix="Decimal" Value="0" />
</Data>
</Tag>"""
_TAG_MAG = r"""<Tag Name="MAG" TagType="Base" DataType="MOTION_INSTRUCTION" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="MOTION_INSTRUCTION">
<DataValueMember Name="FLAGS" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EN" DataType="BOOL" Value="0" />
<DataValueMember Name="DN" DataType="BOOL" Value="0" />
<DataValueMember Name="ER" DataType="BOOL" Value="0" />
<DataValueMember Name="PC" DataType="BOOL" Value="0" />
<DataValueMember Name="IP" DataType="BOOL" Value="0" />
<DataValueMember Name="AC" DataType="BOOL" Value="0" />
<DataValueMember Name="ACCEL" DataType="BOOL" Value="0" />
<DataValueMember Name="DECEL" DataType="BOOL" Value="0" />
<DataValueMember Name="TrackingMaster" DataType="BOOL" Value="0" />
<DataValueMember Name="CalculatedDataAvailable" DataType="BOOL" Value="0" />
<DataValueMember Name="ERR" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="STATUS" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="STATE" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SEGMENT" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EXERR" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</Tag>"""
_TAG_MCD = r"""<Tag Name="MCD" TagType="Base" DataType="MOTION_INSTRUCTION" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="MOTION_INSTRUCTION">
<DataValueMember Name="FLAGS" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EN" DataType="BOOL" Value="0" />
<DataValueMember Name="DN" DataType="BOOL" Value="0" />
<DataValueMember Name="ER" DataType="BOOL" Value="0" />
<DataValueMember Name="PC" DataType="BOOL" Value="0" />
<DataValueMember Name="IP" DataType="BOOL" Value="0" />
<DataValueMember Name="AC" DataType="BOOL" Value="0" />
<DataValueMember Name="ACCEL" DataType="BOOL" Value="0" />
<DataValueMember Name="DECEL" DataType="BOOL" Value="0" />
<DataValueMember Name="TrackingMaster" DataType="BOOL" Value="0" />
<DataValueMember Name="CalculatedDataAvailable" DataType="BOOL" Value="0" />
<DataValueMember Name="ERR" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="STATUS" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="STATE" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SEGMENT" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EXERR" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</Tag>"""
_TAG_MCS = r"""<Tag Name="MCS" TagType="Base" DataType="MOTION_INSTRUCTION" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="MOTION_INSTRUCTION">
<DataValueMember Name="FLAGS" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EN" DataType="BOOL" Value="0" />
<DataValueMember Name="DN" DataType="BOOL" Value="0" />
<DataValueMember Name="ER" DataType="BOOL" Value="0" />
<DataValueMember Name="PC" DataType="BOOL" Value="0" />
<DataValueMember Name="IP" DataType="BOOL" Value="0" />
<DataValueMember Name="AC" DataType="BOOL" Value="0" />
<DataValueMember Name="ACCEL" DataType="BOOL" Value="0" />
<DataValueMember Name="DECEL" DataType="BOOL" Value="0" />
<DataValueMember Name="TrackingMaster" DataType="BOOL" Value="0" />
<DataValueMember Name="CalculatedDataAvailable" DataType="BOOL" Value="0" />
<DataValueMember Name="ERR" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="STATUS" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="STATE" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SEGMENT" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EXERR" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</Tag>"""
_TAG_MCSV = r"""<Tag Name="MCSV" TagType="Base" DataType="MOTION_INSTRUCTION" Constant="false" ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="MOTION_INSTRUCTION">
<DataValueMember Name="FLAGS" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EN" DataType="BOOL" Value="0" />
<DataValueMember Name="DN" DataType="BOOL" Value="0" />
<DataValueMember Name="ER" DataType="BOOL" Value="0" />
<DataValueMember Name="PC" DataType="BOOL" Value="0" />
<DataValueMember Name="IP" DataType="BOOL" Value="0" />
<DataValueMember Name="AC" DataType="BOOL" Value="0" />
<DataValueMember Name="ACCEL" DataType="BOOL" Value="0" />
<DataValueMember Name="DECEL" DataType="BOOL" Value="0" />
<DataValueMember Name="TrackingMaster" DataType="BOOL" Value="0" />
<DataValueMember Name="CalculatedDataAvailable" DataType="BOOL" Value="0" />
<DataValueMember Name="ERR" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="STATUS" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="STATE" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="SEGMENT" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="EXERR" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</Tag>"""
VERIFIED_TAGS = {
    'Axis1': _TAG_AXIS1,
    'Axis2': _TAG_AXIS2,
    'CoordinateSystem1': _TAG_COORDINATESYSTEM1,
    'Cam_Profile': _TAG_CAM_PROFILE,
    'PID': _TAG_PID,
    'CmpCtrl': _TAG_CMPCTRL,
    'ResultCtrl': _TAG_RESULTCTRL,
    'DINT_Arr1': _TAG_DINT_ARR1,
    'DINT_Arr2': _TAG_DINT_ARR2,
    'DINT_Arr3': _TAG_DINT_ARR3,
    'Src': _TAG_SRC,
    'Dst': _TAG_DST,
    'Posn': _TAG_POSN,
    'String': _TAG_STRING,
    'dint': _TAG_DINT,
    'MAG': _TAG_MAG,
    'MCD': _TAG_MCD,
    'MCS': _TAG_MCS,
    'MCSV': _TAG_MCSV,
}


def tags(*names: str) -> str:
    """Returns the verbatim XML for the named verified tags, in the order given."""
    return "\n".join(VERIFIED_TAGS[n] for n in names)
