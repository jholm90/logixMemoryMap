"""Closes the one remaining real catalog gap found auditing full coverage
(2026-08-27, James: "confirm you are going to 100% test every io module
you found in a separate file"). Cross-checked every distinct real
CatalogNumber across the full 63-file corpus against gen_module_sweep.py +
gen_module_sweep_variants.py -- 118 of 119 real, non-legacy, non-
processor, non-placeholder catalogs already covered. The one gap: "150 SMC
Flex-E" (a 150-series SMC-Flex soft starter, DPI port type, not a
processor/IO-card catalog at all) from L5X_Samples/K3M16_Edgers_
20220808r00.L5X -- missed by the original sweep because that pass never
walked drive/starter peripherals, only backplane/PointIO/Ethernet I/O and
2198-series motion. No parser change needed: its real shape (ConfigScript
blob + one real Connection with a Decorated InputTag/OutputTag Structure)
is the exact same shape already handled for PowerFlex VFDs.

With this file, individual per-catalog coverage is 119/119.

Run: python -m sample_gen.gen_module_sweep_gap
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

_SMC_FLEX_E_XML = """\
<Module Name="TestMod1_150SMCFlexE" CatalogNumber="150 SMC Flex-E" Vendor="1" ProductType="123" ProductCode="90" Major="6" Minor="8" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" DrivesADCMode="false" DrivesADCEnabled="false" SafetyEnabled="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="DPI" Upstream="false">
<Bus />
</Port>
<Port Id="2" Address="192.168.1.60" Type="Ethernet" Upstream="true" />
</Ports>
<Communications PrimCxnInputSize="16" PrimCxnOutputSize="12">
<ConfigScript Size="460">
<Data Format="L5K">
[-56,1,0,0,4,0,0,0,0,0,0,0,0,0,0,0,25,0,0,0,8,-106,0,0,0,1,0,0,0,1,0,0,0,8,0,0,0,75,2,32,-110,36,0,-1,-1,0,0,0,-6,0,0,0,8,30,0,0,0,1,0,0,0,1,0,0,0
		,9,0,0,0,16,3,32,-109,36,0,48,2,3,1,0,0,0,9,0,0,0,16,3,32,-110,36,0,48,2,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,18,48,9,15,0,1,0,0,0,10,0,0,0
		,16,3,32,-109,36,46,48,9,-114,8,1,0,0,0,9,0,0,0,16,3,32,-109,36,87,48,9,36,1,0,0,0,10,0,0,0,16,3,32,-109,36,96,48,9,12,0,1,0,0,0,10
		,0,0,0,16,3,32,-109,36,97,48,9,13,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,98,48,9,7,0,1,0,0,0,10,0,0,0,16,3,32,-109,36,99,48,9,8,0,1,0,0,0,18
		,0,0,0,16,3,32,-99,36,1,48,1,-127,0,99,2,0,5,0,1,0,0,1,0,0,0,20,0,0,0,16,3,32,-106,36,1,48,0,1,0,100,0,86,111,108,116,32,32,32,32,1
		,0,0,0,20,0,0,0,16,3,32,-106,36,2,48,0,12,0,100,0,37,77,84,85,32,32,32,32,0,0,45,0,0,0,8,100,0,0,0,1,0,0,0,6,0,0,0,24,0,0,0,16,3,32,-110
		,36,0,48,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,34,0,0,0,8,61,0,0,0,1,0,0,0,1,0,0,0,9,0,0,0,16,3,32,-105,36,0,48,3,3,3,0,0,0,-120,19,0
		,0,0,0,23,0,0,0,8,62,0,0,0,1,0,0,0,1,0,0,0,6,0,0,0,75,2,32,-105,36,0,0,29,0,0,0,0,100,0,0,0,2,0,0,0,-128,0,0,0,98,95,1,72,-116,2,-20,17,-102
		,74,100,93,-122,-94,33,24,0,0,0]
</Data>
</ConfigScript>
<Connections>
<Connection Name="Standard" RPI="20000" Type="Output" InputCxnPoint="1" OutputCxnPoint="2" OutputSize="12" InputSize="16" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:150SMCFlex_B0DF532F:I:0">
<DataValueMember Name="LogicStatus" DataType="INT" Radix="Binary" Value="2#0001_0000_0000_1001" />
<DataValueMember Name="LogicStatus_Enabled" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicStatus_Running" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_Phasing" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_PhasingActive" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicStatus_Starting" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_Stopping" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_Alarm" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_AtSpeed" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_Start" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_Bypass" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_Ready" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicStatus_Option1Input" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicStatus_Option2Input" DataType="BOOL" Value="0" />
<DataValueMember Name="PhaseACurrent" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MtrThermUsage" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MotorSpeed" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="WattMeter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MegawattHours" DataType="INT" Radix="Decimal" Value="49" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[1,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:150SMCFlex_A9D06D0C:O:0">
<DataValueMember Name="LogicCommand" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0001" />
<DataValueMember Name="LogicCommand_Stop" DataType="BOOL" Value="1" />
<DataValueMember Name="LogicCommand_Start" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Option1Command" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_ClearFault" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Option2Command" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_AuxEnable" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Aux1" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Aux2" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Aux3" DataType="BOOL" Value="0" />
<DataValueMember Name="LogicCommand_Aux4" DataType="BOOL" Value="0" />
<DataValueMember Name="Undefined_A1" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Undefined_A2" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Undefined_B1" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Undefined_B2" DataType="INT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
"""


def main() -> None:
    l5x = build_l5x(target_name="ModSweepGap150SMC", tags_xml="", extra_modules_xml=_SMC_FLEX_E_XML)
    out_path = OUT_ROOT / "modulesweep_150_smc_flex_e.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(
        "modulesweep_150_smc_flex_e",
        "150 SMC Flex-E -- real corpus module (standalone), genericized from "
        "L5X_Samples/K3M16_Edgers_20220808r00.L5X, structurally verbatim. Closes the "
        "last real catalog-coverage gap found in the 2026-08-27 full audit -- "
        "individual per-catalog coverage is 119/119 real catalogs with this file. "
        "See OQ-MODULEIO.",
        "modules", out_path, 0,
    )
    print("Done. 1 gap-closing module file written.")


if __name__ == "__main__":
    main()
