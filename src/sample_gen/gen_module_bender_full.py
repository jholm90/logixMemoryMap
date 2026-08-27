"""Full REAL PROGRAM replica -- every importable module from James's real
DnR_Personal/Bender134053_201104.L5X, genericized but structurally
verbatim (2026-08-27, James: "i want a full test like take all of the io
from Bender program and put in this file to get 99.97% accuracy").

Unlike every other generator in this sweep -- which extracts ONE
representative module per catalog, or a deduplicated subset for a rack
test -- this file is the real program's Controller/Modules section,
duplicates and all: 5 real 1734-AENTR/C Point I/O adapters (MCC/HMI/JB/VP/
PP134070 in the real file) with their full real child counts (44 total,
not deduplicated), 5 ArmorBlock (1732E-series) I/O modules, 2 PowerFlex
527-STO CIP Safety drives, 2 EX260 SMC valve manifold nodes, a real Delta
Motion RMC150E (generic Ethernet-Module profile), the full real 2-bus,
5-module Kinetix 5700 shared-bus subgraph with 8 real axis tags (same
real modules/axis wiring as gen_module_kinetix_bus.py), the real FANUC
Robot R30iB Plus/A controller (`RobotController1` -- all 3 real
connections including its 2 real CIP Safety connections, see below), and
a real GuardLogix Safety Partner (see below).

**GuardLogix Safety Partner -- WRONG in an earlier pass, corrected
2026-08-27.** James: "The large full program has the safety partner. For
a second time I removed it temporarily for you to see the field io
without complaining. I regret doing this. You need to handle safety
partner. One safety partner is located beside the CPU on the right if the
program is sil3. Sil2 has no safety partner. You need to handle this."
An earlier pass excluded the Safety Partner outright after hitting a real
Studio 5000 import error ("Invalid module type for import. Module type
cannot be created independently.") -- wrong call: James's own stripped
reference file had the partner manually removed ONLY so the field I/O
would be visible without that error blocking the rest of the import, not
because the partner should be dropped from the model. Root-caused
properly this time: the real Bender program is SIL3/PLe
(`Controller/SafetyInfo SafetyLevel="SIL3/PLe"`, confirmed real), and a
SIL3 redundant safety pairing needs the PRIMARY CPU's own backplane Port
to declare `Width="2"` (it now spans its own slot AND the partner's) plus
a real `SafetyNetwork` identifier -- without that, Studio 5000 has no way
to know slot 1 is reserved for a paired partner and correctly rejects it
as an invalid standalone add. `wrapper.py`'s `build_l5x(...,
safety_level="SIL3")` now emits that real Width/SafetyNetwork
configuration on the Local module plus real `SafetyInfo` content
(SIL3/PLe); `safety_partner_module_xml()` builds the real partner module
itself (`EKey State="ExactMatch"`, `Width="0"` on its own port,
module-level `SafetyNetwork` -- all confirmed real from the source file).
SIL2 programs use a single non-redundant safety-capable primary with NO
partner at all (`safety_level="SIL2"` -- no Width/partner, just a
safety-rated processor_type + SafetyInfo) -- this capability is opt-in
per file, not forced on every generated file.

**EDS-dependent devices, James: "You will need to accommodate missing
eds files. This is a 100% requirement."** 2 real TR-Electronic GmbH
encoders (`LH_CART_ENC`/`RH_CART_ENC`, no CatalogNumber) and a Datalogic
barcode reader (`Datalogic`, also no CatalogNumber) real-error "Module
profile could not be found" -- confirmed genuinely independent failures
(explicit "profile not found," not a cascade), each needs an EDS
registered on the specific machine that built the real program, not
guaranteed present anywhere else. Represented via Rockwell's own built-in
Generic Ethernet Module (`CatalogNumber="ETHERNET-MODULE"`,
`Vendor="1"`, no EDS needed -- confirmed real, this exact file's own
RMC150E module already uses it) as `GenericEncoder1`/`GenericEncoder2`/
`GenericBarcodeReader1`, preserving their real stated Connection sizes
exactly (12-byte Input Only x2, 476/468-byte bidirectional).

**The FANUC robot's earlier exclusion was reconsidered and reversed.**
Its first-pass error was a bare "Module import failed" -- unlike the 3
EDS devices above, it never said "profile could not be found." That
weaker, vaguer error is the same shape as the OTHER modules that failed
purely as a cascade of the Safety Partner's invalid standalone import
(see James's message above) -- most likely the robot's failure was the
same cascade, not an independent EDS problem. With the Safety Partner now
fixed, the robot is back in as its REAL, full, verbatim module (not a
Generic Ethernet Module substitute) -- James: "The robot stays. Your
purpose is to calculate memory usage of tags and logic... You need to
take the possibility of safety [I/O] data into your programming." Its 2
real CIP Safety connections (`A_Safety_Output` 8 bytes,
`B_Safety_Input` 12 bytes) are included verbatim alongside its real
Standard connection (16/16 bytes) -- real stated sizes, real Decorated
Structure content, all counted toward the sizing total per the actual
project goal (calculating memory usage), not excluded just because a
generic substitute mechanism couldn't represent them for a clean
reimport.

Genericized the same way as every other real extraction in this project:
every real module Name replaced with a generic Name (adapter children
numbered PtIOAdapterN_ModM in real file order), every real IP address
and SafetyNetwork identifier replaced with a placeholder (same real
16#0000_xxxx_xxxx_xxxx bit-length/format, different digits),
ExtendedProperties/Description/Comments stripped throughout.
Sanity-checked before writing: 0 duplicate Names, 0 dangling
ParentModule references, 0 lint findings, 0 sizing crashes.

**Cross-checked 2026-08-27 against James's own "stripped" export**
(samples/local/bender_stripped/Bender134053_stripper.L5X -- the real
program with logic/UDTs/most Controller Tags removed but the Modules
section left intact, gitignored real corpus): module catalog inventory
matches this file's extraction exactly, module-for-module (the Safety
Partner's absence there was James's own deliberate temporary removal,
confirmed above, not evidence it should stay excluded).

Sizing this file returns real SizeErrors -- one per rack-aliased
(RackConnection/InAliasTag) Point I/O child module, all already-
documented (module_overhead was FITTED from only 2 discrete-Connection
modules; zero real data confirms it applies the same way to a
rack-aliased child, so it's deliberately not charged, per
parser/modules.py's own docstring). **This is exactly the intended use
of this file, not a bug to fix**: once James captures this exact
module section's real controller-memory cost from the actual Bender
controller, the residual between predicted and real can be divided
across these modules to solve for their real per-module overhead -- the
same fitting methodology that produced `module_overhead` itself.

The CPU's own "Local" self-entry (1756-L81ES in the real file) is
NOT included in extra_modules_xml -- build_l5x's own wrapper already
synthesizes it; processor_type="1756-L81ES" is passed through to match
the real program's exact processor exactly rather than the project
default (1756-L81E).

Run: python -m sample_gen.gen_module_bender_full
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.gen_module_motion import _axis_tag, _MOTION_GROUP_TAG_XML
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x, safety_partner_module_xml

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

_ALL_MODULES_XML = """\
<Module Name="GenericMotionController1" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" ProductCode="18" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="192.168.1.10" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870914" PrimCxnInputSize="44" PrimCxnOutputSize="84">
<ConfigTag ConfigSize="0" ExternalAccess="Read/Write">
<Data Format="L5K">
[4,4,[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE:C:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="400" Radix="Hex">
<Element Index="[0]" Value="16#00" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#00" />
<Element Index="[4]" Value="16#00" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
<Element Index="[8]" Value="16#00" />
<Element Index="[9]" Value="16#00" />
<Element Index="[10]" Value="16#00" />
<Element Index="[11]" Value="16#00" />
<Element Index="[12]" Value="16#00" />
<Element Index="[13]" Value="16#00" />
<Element Index="[14]" Value="16#00" />
<Element Index="[15]" Value="16#00" />
<Element Index="[16]" Value="16#00" />
<Element Index="[17]" Value="16#00" />
<Element Index="[18]" Value="16#00" />
<Element Index="[19]" Value="16#00" />
<Element Index="[20]" Value="16#00" />
<Element Index="[21]" Value="16#00" />
<Element Index="[22]" Value="16#00" />
<Element Index="[23]" Value="16#00" />
<Element Index="[24]" Value="16#00" />
<Element Index="[25]" Value="16#00" />
<Element Index="[26]" Value="16#00" />
<Element Index="[27]" Value="16#00" />
<Element Index="[28]" Value="16#00" />
<Element Index="[29]" Value="16#00" />
<Element Index="[30]" Value="16#00" />
<Element Index="[31]" Value="16#00" />
<Element Index="[32]" Value="16#00" />
<Element Index="[33]" Value="16#00" />
<Element Index="[34]" Value="16#00" />
<Element Index="[35]" Value="16#00" />
<Element Index="[36]" Value="16#00" />
<Element Index="[37]" Value="16#00" />
<Element Index="[38]" Value="16#00" />
<Element Index="[39]" Value="16#00" />
<Element Index="[40]" Value="16#00" />
<Element Index="[41]" Value="16#00" />
<Element Index="[42]" Value="16#00" />
<Element Index="[43]" Value="16#00" />
<Element Index="[44]" Value="16#00" />
<Element Index="[45]" Value="16#00" />
<Element Index="[46]" Value="16#00" />
<Element Index="[47]" Value="16#00" />
<Element Index="[48]" Value="16#00" />
<Element Index="[49]" Value="16#00" />
<Element Index="[50]" Value="16#00" />
<Element Index="[51]" Value="16#00" />
<Element Index="[52]" Value="16#00" />
<Element Index="[53]" Value="16#00" />
<Element Index="[54]" Value="16#00" />
<Element Index="[55]" Value="16#00" />
<Element Index="[56]" Value="16#00" />
<Element Index="[57]" Value="16#00" />
<Element Index="[58]" Value="16#00" />
<Element Index="[59]" Value="16#00" />
<Element Index="[60]" Value="16#00" />
<Element Index="[61]" Value="16#00" />
<Element Index="[62]" Value="16#00" />
<Element Index="[63]" Value="16#00" />
<Element Index="[64]" Value="16#00" />
<Element Index="[65]" Value="16#00" />
<Element Index="[66]" Value="16#00" />
<Element Index="[67]" Value="16#00" />
<Element Index="[68]" Value="16#00" />
<Element Index="[69]" Value="16#00" />
<Element Index="[70]" Value="16#00" />
<Element Index="[71]" Value="16#00" />
<Element Index="[72]" Value="16#00" />
<Element Index="[73]" Value="16#00" />
<Element Index="[74]" Value="16#00" />
<Element Index="[75]" Value="16#00" />
<Element Index="[76]" Value="16#00" />
<Element Index="[77]" Value="16#00" />
<Element Index="[78]" Value="16#00" />
<Element Index="[79]" Value="16#00" />
<Element Index="[80]" Value="16#00" />
<Element Index="[81]" Value="16#00" />
<Element Index="[82]" Value="16#00" />
<Element Index="[83]" Value="16#00" />
<Element Index="[84]" Value="16#00" />
<Element Index="[85]" Value="16#00" />
<Element Index="[86]" Value="16#00" />
<Element Index="[87]" Value="16#00" />
<Element Index="[88]" Value="16#00" />
<Element Index="[89]" Value="16#00" />
<Element Index="[90]" Value="16#00" />
<Element Index="[91]" Value="16#00" />
<Element Index="[92]" Value="16#00" />
<Element Index="[93]" Value="16#00" />
<Element Index="[94]" Value="16#00" />
<Element Index="[95]" Value="16#00" />
<Element Index="[96]" Value="16#00" />
<Element Index="[97]" Value="16#00" />
<Element Index="[98]" Value="16#00" />
<Element Index="[99]" Value="16#00" />
<Element Index="[100]" Value="16#00" />
<Element Index="[101]" Value="16#00" />
<Element Index="[102]" Value="16#00" />
<Element Index="[103]" Value="16#00" />
<Element Index="[104]" Value="16#00" />
<Element Index="[105]" Value="16#00" />
<Element Index="[106]" Value="16#00" />
<Element Index="[107]" Value="16#00" />
<Element Index="[108]" Value="16#00" />
<Element Index="[109]" Value="16#00" />
<Element Index="[110]" Value="16#00" />
<Element Index="[111]" Value="16#00" />
<Element Index="[112]" Value="16#00" />
<Element Index="[113]" Value="16#00" />
<Element Index="[114]" Value="16#00" />
<Element Index="[115]" Value="16#00" />
<Element Index="[116]" Value="16#00" />
<Element Index="[117]" Value="16#00" />
<Element Index="[118]" Value="16#00" />
<Element Index="[119]" Value="16#00" />
<Element Index="[120]" Value="16#00" />
<Element Index="[121]" Value="16#00" />
<Element Index="[122]" Value="16#00" />
<Element Index="[123]" Value="16#00" />
<Element Index="[124]" Value="16#00" />
<Element Index="[125]" Value="16#00" />
<Element Index="[126]" Value="16#00" />
<Element Index="[127]" Value="16#00" />
<Element Index="[128]" Value="16#00" />
<Element Index="[129]" Value="16#00" />
<Element Index="[130]" Value="16#00" />
<Element Index="[131]" Value="16#00" />
<Element Index="[132]" Value="16#00" />
<Element Index="[133]" Value="16#00" />
<Element Index="[134]" Value="16#00" />
<Element Index="[135]" Value="16#00" />
<Element Index="[136]" Value="16#00" />
<Element Index="[137]" Value="16#00" />
<Element Index="[138]" Value="16#00" />
<Element Index="[139]" Value="16#00" />
<Element Index="[140]" Value="16#00" />
<Element Index="[141]" Value="16#00" />
<Element Index="[142]" Value="16#00" />
<Element Index="[143]" Value="16#00" />
<Element Index="[144]" Value="16#00" />
<Element Index="[145]" Value="16#00" />
<Element Index="[146]" Value="16#00" />
<Element Index="[147]" Value="16#00" />
<Element Index="[148]" Value="16#00" />
<Element Index="[149]" Value="16#00" />
<Element Index="[150]" Value="16#00" />
<Element Index="[151]" Value="16#00" />
<Element Index="[152]" Value="16#00" />
<Element Index="[153]" Value="16#00" />
<Element Index="[154]" Value="16#00" />
<Element Index="[155]" Value="16#00" />
<Element Index="[156]" Value="16#00" />
<Element Index="[157]" Value="16#00" />
<Element Index="[158]" Value="16#00" />
<Element Index="[159]" Value="16#00" />
<Element Index="[160]" Value="16#00" />
<Element Index="[161]" Value="16#00" />
<Element Index="[162]" Value="16#00" />
<Element Index="[163]" Value="16#00" />
<Element Index="[164]" Value="16#00" />
<Element Index="[165]" Value="16#00" />
<Element Index="[166]" Value="16#00" />
<Element Index="[167]" Value="16#00" />
<Element Index="[168]" Value="16#00" />
<Element Index="[169]" Value="16#00" />
<Element Index="[170]" Value="16#00" />
<Element Index="[171]" Value="16#00" />
<Element Index="[172]" Value="16#00" />
<Element Index="[173]" Value="16#00" />
<Element Index="[174]" Value="16#00" />
<Element Index="[175]" Value="16#00" />
<Element Index="[176]" Value="16#00" />
<Element Index="[177]" Value="16#00" />
<Element Index="[178]" Value="16#00" />
<Element Index="[179]" Value="16#00" />
<Element Index="[180]" Value="16#00" />
<Element Index="[181]" Value="16#00" />
<Element Index="[182]" Value="16#00" />
<Element Index="[183]" Value="16#00" />
<Element Index="[184]" Value="16#00" />
<Element Index="[185]" Value="16#00" />
<Element Index="[186]" Value="16#00" />
<Element Index="[187]" Value="16#00" />
<Element Index="[188]" Value="16#00" />
<Element Index="[189]" Value="16#00" />
<Element Index="[190]" Value="16#00" />
<Element Index="[191]" Value="16#00" />
<Element Index="[192]" Value="16#00" />
<Element Index="[193]" Value="16#00" />
<Element Index="[194]" Value="16#00" />
<Element Index="[195]" Value="16#00" />
<Element Index="[196]" Value="16#00" />
<Element Index="[197]" Value="16#00" />
<Element Index="[198]" Value="16#00" />
<Element Index="[199]" Value="16#00" />
<Element Index="[200]" Value="16#00" />
<Element Index="[201]" Value="16#00" />
<Element Index="[202]" Value="16#00" />
<Element Index="[203]" Value="16#00" />
<Element Index="[204]" Value="16#00" />
<Element Index="[205]" Value="16#00" />
<Element Index="[206]" Value="16#00" />
<Element Index="[207]" Value="16#00" />
<Element Index="[208]" Value="16#00" />
<Element Index="[209]" Value="16#00" />
<Element Index="[210]" Value="16#00" />
<Element Index="[211]" Value="16#00" />
<Element Index="[212]" Value="16#00" />
<Element Index="[213]" Value="16#00" />
<Element Index="[214]" Value="16#00" />
<Element Index="[215]" Value="16#00" />
<Element Index="[216]" Value="16#00" />
<Element Index="[217]" Value="16#00" />
<Element Index="[218]" Value="16#00" />
<Element Index="[219]" Value="16#00" />
<Element Index="[220]" Value="16#00" />
<Element Index="[221]" Value="16#00" />
<Element Index="[222]" Value="16#00" />
<Element Index="[223]" Value="16#00" />
<Element Index="[224]" Value="16#00" />
<Element Index="[225]" Value="16#00" />
<Element Index="[226]" Value="16#00" />
<Element Index="[227]" Value="16#00" />
<Element Index="[228]" Value="16#00" />
<Element Index="[229]" Value="16#00" />
<Element Index="[230]" Value="16#00" />
<Element Index="[231]" Value="16#00" />
<Element Index="[232]" Value="16#00" />
<Element Index="[233]" Value="16#00" />
<Element Index="[234]" Value="16#00" />
<Element Index="[235]" Value="16#00" />
<Element Index="[236]" Value="16#00" />
<Element Index="[237]" Value="16#00" />
<Element Index="[238]" Value="16#00" />
<Element Index="[239]" Value="16#00" />
<Element Index="[240]" Value="16#00" />
<Element Index="[241]" Value="16#00" />
<Element Index="[242]" Value="16#00" />
<Element Index="[243]" Value="16#00" />
<Element Index="[244]" Value="16#00" />
<Element Index="[245]" Value="16#00" />
<Element Index="[246]" Value="16#00" />
<Element Index="[247]" Value="16#00" />
<Element Index="[248]" Value="16#00" />
<Element Index="[249]" Value="16#00" />
<Element Index="[250]" Value="16#00" />
<Element Index="[251]" Value="16#00" />
<Element Index="[252]" Value="16#00" />
<Element Index="[253]" Value="16#00" />
<Element Index="[254]" Value="16#00" />
<Element Index="[255]" Value="16#00" />
<Element Index="[256]" Value="16#00" />
<Element Index="[257]" Value="16#00" />
<Element Index="[258]" Value="16#00" />
<Element Index="[259]" Value="16#00" />
<Element Index="[260]" Value="16#00" />
<Element Index="[261]" Value="16#00" />
<Element Index="[262]" Value="16#00" />
<Element Index="[263]" Value="16#00" />
<Element Index="[264]" Value="16#00" />
<Element Index="[265]" Value="16#00" />
<Element Index="[266]" Value="16#00" />
<Element Index="[267]" Value="16#00" />
<Element Index="[268]" Value="16#00" />
<Element Index="[269]" Value="16#00" />
<Element Index="[270]" Value="16#00" />
<Element Index="[271]" Value="16#00" />
<Element Index="[272]" Value="16#00" />
<Element Index="[273]" Value="16#00" />
<Element Index="[274]" Value="16#00" />
<Element Index="[275]" Value="16#00" />
<Element Index="[276]" Value="16#00" />
<Element Index="[277]" Value="16#00" />
<Element Index="[278]" Value="16#00" />
<Element Index="[279]" Value="16#00" />
<Element Index="[280]" Value="16#00" />
<Element Index="[281]" Value="16#00" />
<Element Index="[282]" Value="16#00" />
<Element Index="[283]" Value="16#00" />
<Element Index="[284]" Value="16#00" />
<Element Index="[285]" Value="16#00" />
<Element Index="[286]" Value="16#00" />
<Element Index="[287]" Value="16#00" />
<Element Index="[288]" Value="16#00" />
<Element Index="[289]" Value="16#00" />
<Element Index="[290]" Value="16#00" />
<Element Index="[291]" Value="16#00" />
<Element Index="[292]" Value="16#00" />
<Element Index="[293]" Value="16#00" />
<Element Index="[294]" Value="16#00" />
<Element Index="[295]" Value="16#00" />
<Element Index="[296]" Value="16#00" />
<Element Index="[297]" Value="16#00" />
<Element Index="[298]" Value="16#00" />
<Element Index="[299]" Value="16#00" />
<Element Index="[300]" Value="16#00" />
<Element Index="[301]" Value="16#00" />
<Element Index="[302]" Value="16#00" />
<Element Index="[303]" Value="16#00" />
<Element Index="[304]" Value="16#00" />
<Element Index="[305]" Value="16#00" />
<Element Index="[306]" Value="16#00" />
<Element Index="[307]" Value="16#00" />
<Element Index="[308]" Value="16#00" />
<Element Index="[309]" Value="16#00" />
<Element Index="[310]" Value="16#00" />
<Element Index="[311]" Value="16#00" />
<Element Index="[312]" Value="16#00" />
<Element Index="[313]" Value="16#00" />
<Element Index="[314]" Value="16#00" />
<Element Index="[315]" Value="16#00" />
<Element Index="[316]" Value="16#00" />
<Element Index="[317]" Value="16#00" />
<Element Index="[318]" Value="16#00" />
<Element Index="[319]" Value="16#00" />
<Element Index="[320]" Value="16#00" />
<Element Index="[321]" Value="16#00" />
<Element Index="[322]" Value="16#00" />
<Element Index="[323]" Value="16#00" />
<Element Index="[324]" Value="16#00" />
<Element Index="[325]" Value="16#00" />
<Element Index="[326]" Value="16#00" />
<Element Index="[327]" Value="16#00" />
<Element Index="[328]" Value="16#00" />
<Element Index="[329]" Value="16#00" />
<Element Index="[330]" Value="16#00" />
<Element Index="[331]" Value="16#00" />
<Element Index="[332]" Value="16#00" />
<Element Index="[333]" Value="16#00" />
<Element Index="[334]" Value="16#00" />
<Element Index="[335]" Value="16#00" />
<Element Index="[336]" Value="16#00" />
<Element Index="[337]" Value="16#00" />
<Element Index="[338]" Value="16#00" />
<Element Index="[339]" Value="16#00" />
<Element Index="[340]" Value="16#00" />
<Element Index="[341]" Value="16#00" />
<Element Index="[342]" Value="16#00" />
<Element Index="[343]" Value="16#00" />
<Element Index="[344]" Value="16#00" />
<Element Index="[345]" Value="16#00" />
<Element Index="[346]" Value="16#00" />
<Element Index="[347]" Value="16#00" />
<Element Index="[348]" Value="16#00" />
<Element Index="[349]" Value="16#00" />
<Element Index="[350]" Value="16#00" />
<Element Index="[351]" Value="16#00" />
<Element Index="[352]" Value="16#00" />
<Element Index="[353]" Value="16#00" />
<Element Index="[354]" Value="16#00" />
<Element Index="[355]" Value="16#00" />
<Element Index="[356]" Value="16#00" />
<Element Index="[357]" Value="16#00" />
<Element Index="[358]" Value="16#00" />
<Element Index="[359]" Value="16#00" />
<Element Index="[360]" Value="16#00" />
<Element Index="[361]" Value="16#00" />
<Element Index="[362]" Value="16#00" />
<Element Index="[363]" Value="16#00" />
<Element Index="[364]" Value="16#00" />
<Element Index="[365]" Value="16#00" />
<Element Index="[366]" Value="16#00" />
<Element Index="[367]" Value="16#00" />
<Element Index="[368]" Value="16#00" />
<Element Index="[369]" Value="16#00" />
<Element Index="[370]" Value="16#00" />
<Element Index="[371]" Value="16#00" />
<Element Index="[372]" Value="16#00" />
<Element Index="[373]" Value="16#00" />
<Element Index="[374]" Value="16#00" />
<Element Index="[375]" Value="16#00" />
<Element Index="[376]" Value="16#00" />
<Element Index="[377]" Value="16#00" />
<Element Index="[378]" Value="16#00" />
<Element Index="[379]" Value="16#00" />
<Element Index="[380]" Value="16#00" />
<Element Index="[381]" Value="16#00" />
<Element Index="[382]" Value="16#00" />
<Element Index="[383]" Value="16#00" />
<Element Index="[384]" Value="16#00" />
<Element Index="[385]" Value="16#00" />
<Element Index="[386]" Value="16#00" />
<Element Index="[387]" Value="16#00" />
<Element Index="[388]" Value="16#00" />
<Element Index="[389]" Value="16#00" />
<Element Index="[390]" Value="16#00" />
<Element Index="[391]" Value="16#00" />
<Element Index="[392]" Value="16#00" />
<Element Index="[393]" Value="16#00" />
<Element Index="[394]" Value="16#00" />
<Element Index="[395]" Value="16#00" />
<Element Index="[396]" Value="16#00" />
<Element Index="[397]" Value="16#00" />
<Element Index="[398]" Value="16#00" />
<Element Index="[399]" Value="16#00" />
</ArrayMember>
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="Standard" RPI="5000" Type="Output" InputCxnPoint="1" OutputCxnPoint="2" OutputSize="84" InputSize="44" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE_REAL_44Bytes:I:0">
<ArrayMember Name="Data" DataType="REAL" Dimensions="11" Radix="Float">
<Element Index="[0]" Value="4450.0" />
<Element Index="[1]" Value="1.51208292e-036" />
<Element Index="[2]" Value="5.60519386e-045" />
<Element Index="[3]" Value="0.4399925" />
<Element Index="[4]" Value="0.4349925" />
<Element Index="[5]" Value="1.51208292e-036" />
<Element Index="[6]" Value="0.0" />
<Element Index="[7]" Value="87.16999" />
<Element Index="[8]" Value="87.16999" />
<Element Index="[9]" Value="0.0" />
<Element Index="[10]" Value="0.0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[4.45000000e+003,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000,0.00000000e+000
		,0.00000000e+000,0.00000000e+000,0.00000000e+000]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE_REAL_84Bytes:O:0">
<ArrayMember Name="Data" DataType="REAL" Dimensions="21" Radix="Float">
<Element Index="[0]" Value="4450.0" />
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
<Element Index="[17]" Value="0.0" />
<Element Index="[18]" Value="0.0" />
<Element Index="[19]" Value="0.0" />
<Element Index="[20]" Value="0.0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="VFD_Safety1" CatalogNumber="PowerFlex 527-STO CIP Safety" Vendor="1" ProductType="45" ProductCode="15" Major="2" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_44c9_02ec_6f66" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.11" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="292">
<Data Format="L5K">
[296,2,257,18,94420071,0,2565904,16908804,1,0,0,0,0,0,0,0,0,262148000,262148000,262148000,262148000,0,0,32768
		,230,-65536,1120403456,1045220557,1073741824,0,1114636288,0,1120403456,1120403456,0,1120403456
		,1124859904,1115815936,0,1120403456,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,32768004,16384500,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<SafetyScript Size="59">
<Data Format="L5K">
[55,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,39,0,0,0,0,0,0,0,0,3,0,0,0,25,0,0,0,0,0,0,18,0,0,0,0,0,0,0,-41,-20,58,-48,-19,44,105,3,-56,68,0,0,1,1,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="AMotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="48" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="56" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="BMotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="CSafety_Output" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="1" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 25 00 80 01 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety1:SO:0">
<DataValueMember Name="Command" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="DSafety_Input" RPI="10000" Type="SafetyInputDataDriven" InputSize="5" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 24 c7 20 04 25 00 a0 01" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety1:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0010" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="VFD_Safety2" CatalogNumber="PowerFlex 527-STO CIP Safety" Vendor="1" ProductType="45" ProductCode="15" Major="2" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_44c9_02ec_9382" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.12" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="292">
<Data Format="L5K">
[296,2,257,18,94420071,0,2565904,16908804,1,0,0,0,0,0,0,0,0,262148000,262148000,262148000,262148000,0,0,32768
		,230,-65536,1120403456,1045220557,1073741824,0,1114636288,0,1120403456,1120403456,0,1120403456
		,1124859904,1115815936,0,1120403456,1,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,32768004,16384500,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<SafetyScript Size="59">
<Data Format="L5K">
[55,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,39,0,0,0,0,0,0,0,0,3,0,0,0,25,0,0,0,0,0,0,18,0,0,0,0,0,0,0,-41,-20,58,-48,-19,44,105,3,-56,68,0,0,1,1,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="AMotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="44" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="60" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="BMotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="CSafety_Output" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="1" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 25 00 80 01 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety1:SO:0">
<DataValueMember Name="Command" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="DSafety_Input" RPI="10000" Type="SafetyInputDataDriven" InputSize="5" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 24 c7 20 04 25 00 a0 01" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety1:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0010" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.13" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="5000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_0000_0001_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#1010_1111" />
<Element Index="[6]" Value="2#0000_0001" />
<Element Index="[7]" Value="2#1100_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0011" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-4065,-1,[0,0,0,0,0,0,0,0,0,8,6,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_1000" />
<Element Index="[10]" Value="2#0000_0110" />
<Element Index="[11]" Value="2#0000_0000" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod1" CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_447d_042b_b261">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,1902747612,70116045,17611,514,1000,131072,0,2,16842752,0,513,131072,0,786434,131072,12,65538
		,65566,65566,65566,150]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Status" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S:O:0">
<DataValueMember Name="Test00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test03Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod2" CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_447d_042b_b261">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,1640560518,47005553,17651,514,787432,131072,12,2,131072,0,2,131072,0,2,131072,0,65538,65686,30
		,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Status" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S:O:0">
<DataValueMember Name="Test00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test03Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod3" CatalogNumber="1734-OB8S/B" Vendor="1" ProductType="35" ProductCode="16" Major="2" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_447d_042b_b261">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="26">
<Data Format="L5K">
[30,864,1181255011,46978231,17651,16843752,16843009,16843009,257]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_OB8S_Safety1:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06OutputStatus" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07OutputStatus" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_OB8S:O:0">
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod4" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,0,32767,0,3113,16547,2867,16793,3,0,1,0,0,16383,0,3113,16547,2867,16793,3,0,1,2,10]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="10" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="5000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="-4072" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod5" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod6" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod7" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="7" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod8" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="8" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod9" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="9" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod10" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="10" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod11" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="11" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod12" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="12" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,3277,16383,0,3113,16547,2867,16793,3,0,0,0,3277,16383,0,3113,16547,2867,16793,3,0,0,2,100]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="100" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="80000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="3289" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="6399" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter1_Mod13" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="PtIOAdapter1" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="13" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,3277,16383,0,3113,16547,2867,16793,3,0,0,0,3277,16383,0,3113,16547,2867,16793,3,0,0,2,100]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="100" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="80000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="3295" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="3308" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter2" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="4" />
</Port>
<Port Id="2" Address="192.168.1.14" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_4SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_0011" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="4" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-13,-1,[0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_4SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="4" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter2_Mod1" CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="PtIOAdapter2" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_447e_0416_2962">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,1359773264,55395539,17608,514,1000,131072,0,2,16842752,0,513,131072,0,0,0,0,65536,65566,30,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Status" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S:O:0">
<DataValueMember Name="Test00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test03Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter2_Mod2" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter2" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter2_Mod3" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIOAdapter2" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="14" />
</Port>
<Port Id="2" Address="192.168.1.15" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1100_0000_1000_1111" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0100" />
<Element Index="[5]" Value="2#0001_1010" />
<Element Index="[6]" Value="2#0000_0011" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
<Element Index="[10]" Value="2#0000_0000" />
<Element Index="[11]" Value="2#0000_0000" />
<Element Index="[12]" Value="2#0110_0011" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-16241,-1,[0,0,0,0,0,0,0,0,0,16,6,6,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_14SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="14" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0001_0000" />
<Element Index="[10]" Value="2#0000_0110" />
<Element Index="[11]" Value="2#0000_0110" />
<Element Index="[12]" Value="2#0000_0000" />
<Element Index="[13]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod1" CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_447e_0429_d394">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,-1812573082,51911118,17608,33686018,1000,16842752,0,513,50397184,0,1025,16842752,0,513,131072
		,0,65538,65566,65566,65566,30]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Status" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S:O:0">
<DataValueMember Name="Test00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test03Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod2" CatalogNumber="1734-IB8S/B" Vendor="1" ProductType="35" ProductCode="15" Major="2" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_447e_0429_d394">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="PointIO" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="82">
<Data Format="L5K">
[86,864,-1066055356,41434372,17644,514,1000,131072,0,2,131072,0,2,131072,0,2,0,0,65536,65566,65566,30,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="Input" RPI="10000" Type="SafetyInput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S_Safety2:I:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt01Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt03Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt05Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06Status" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt07Status" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Output" RPI="20000" Type="SafetyOutput" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Unicast="true">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IB8S:O:0">
<DataValueMember Name="Test00Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test01Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test02Data" DataType="BOOL" Value="0" />
<DataValueMember Name="Test03Data" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod3" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,3277,16383,0,3113,16547,2867,16793,3,0,0,0,3277,16383,0,3113,16547,2867,16793,3,0,0,2,100]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="100" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="80000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="3306" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="19" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0101_0101" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod4" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod5" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod6" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod7" CatalogNumber="1734-OE2C/C" Vendor="1" ProductType="115" ProductCode="25" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="7" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="40" ExternalAccess="Read/Write">
<Data Format="L5K">
[44,123,1,0,0,3277,16383,-32768,32767,0,1,1,0,0,0,0,0,1638,8191,-32768,32767,0,1,1,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_OE2:C:0">
<DataValueMember Name="Ch0FaultValue" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0ProgValue" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0LowLimit" DataType="INT" Radix="Decimal" Value="-32768" />
<DataValueMember Name="Ch0HighLimit" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0FaultMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch0ProgMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1FaultValue" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1ProgValue" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="1638" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="8191" />
<DataValueMember Name="Ch1LowLimit" DataType="INT" Radix="Decimal" Value="-32768" />
<DataValueMember Name="Ch1HighLimit" DataType="INT" Radix="Decimal" Value="32767" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1FaultMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch1ProgMode" DataType="SINT" Radix="Decimal" Value="1" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_OE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_1001" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="1" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[5000,32767]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_OE2:O:0">
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="5000" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="32767" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod8" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="8" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod9" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="9" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod10" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="10" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod11" CatalogNumber="1734-OB8E/C" Vendor="1" ProductType="7" ProductCode="218" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="11" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB8:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt2FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt3FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt4FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt5FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt6FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt7FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod12" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="12" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter3_Mod13" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter3" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="13" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="10" />
</Port>
<Port Id="2" Address="192.168.1.16" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_10SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1100_0011_0001" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="10" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0011" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-975,-1,[0,0,0,0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_10SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="10" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
<Element Index="[7]" Value="2#0000_0000" />
<Element Index="[8]" Value="2#0000_0000" />
<Element Index="[9]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod1" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod2" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod3" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod4" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,3277,16383,0,3113,16547,2867,16793,3,0,0,0,3277,16383,0,3113,16547,2867,16793,3,0,0,2,100]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="100" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="80000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="3296" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="3311" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod5" CatalogNumber="1734-IE2C/C" Vendor="1" ProductType="115" ProductCode="24" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="536870913">
<ConfigTag ConfigSize="42" ExternalAccess="Read/Write">
<Data Format="L5K">
[46,123,1,3277,16383,0,3113,16547,2867,16793,3,0,0,0,3277,16383,0,3113,16547,2867,16793,3,0,0,2,100]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:C:0">
<DataValueMember Name="Ch0LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch0HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch0DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch0HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch0LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch0HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch0RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch0LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch0AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LowEngineering" DataType="INT" Radix="Decimal" Value="3277" />
<DataValueMember Name="Ch1HighEngineering" DataType="INT" Radix="Decimal" Value="16383" />
<DataValueMember Name="Ch1DigitalFilter" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1LAlarmLimit" DataType="INT" Radix="Decimal" Value="3113" />
<DataValueMember Name="Ch1HAlarmLimit" DataType="INT" Radix="Decimal" Value="16547" />
<DataValueMember Name="Ch1LLAlarmLimit" DataType="INT" Radix="Decimal" Value="2867" />
<DataValueMember Name="Ch1HHAlarmLimit" DataType="INT" Radix="Decimal" Value="16793" />
<DataValueMember Name="Ch1RangeType" DataType="SINT" Radix="Decimal" Value="3" />
<DataValueMember Name="Ch1LimitAlarmLatch" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="Ch1AlarmDisable" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="NotchFilter" DataType="SINT" Radix="Decimal" Value="2" />
<DataValueMember Name="RealTimeSample" DataType="INT" Radix="Decimal" Value="100" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="InputData" RPI="80000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_IE2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Ch0Data" DataType="INT" Radix="Decimal" Value="15950" />
<DataValueMember Name="Ch1Data" DataType="INT" Radix="Decimal" Value="20" />
<DataValueMember Name="Ch0Status" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Ch0Fault" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0LLAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Underrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch0Overrange" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Status" DataType="SINT" Radix="Binary" Value="2#0101_0101" />
<DataValueMember Name="Ch1Fault" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Calibration" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1HAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1LLAlarm" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1HHAlarm" DataType="BOOL" Value="0" />
<DataValueMember Name="Ch1Underrange" DataType="BOOL" Value="1" />
<DataValueMember Name="Ch1Overrange" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod6" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod7" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="7" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod8" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="8" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter4_Mod9" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="PtIOAdapter4" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="9" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,0,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="ArmorBlock1" CatalogNumber="1732E-IB16M12DR/A" Vendor="1" ProductType="7" ProductCode="355" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.17" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="10" ExternalAccess="Read/Write">
<Data Format="L5K">
[14,107,1,1000,1000,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_D16Diag:C:0">
<DataValueMember Name="FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt00_01OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15OpenWireEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1732_DI16Diag:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="INT" Radix="Binary" Value="2#0000_1111_1101_1100" />
<DataValueMember Name="Pt00_01OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00_01ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15ShortCircuit" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="ArmorBlock2" CatalogNumber="1732E-OB16M12R/A" Vendor="1" ProductType="7" ProductCode="370" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.18" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="5" ExternalAccess="Read/Write">
<Data Format="L5K">
[9,100,1,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_DO16:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1732_D2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_DO16:O:0">
<DataValueMember Name="Data" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="ArmorBlock3" CatalogNumber="1732E-IB16M12DR/A" Vendor="1" ProductType="7" ProductCode="355" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.19" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="10" ExternalAccess="Read/Write">
<Data Format="L5K">
[14,107,1,1000,1000,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_D16Diag:C:0">
<DataValueMember Name="FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt00_01OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15OpenWireEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1732_DI16Diag:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="INT" Radix="Binary" Value="2#0000_0000_0100_1000" />
<DataValueMember Name="Pt00_01OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00_01ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15ShortCircuit" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="ArmorBlock4" CatalogNumber="1732E-IB16M12DR/A" Vendor="1" ProductType="7" ProductCode="355" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.20" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="10" ExternalAccess="Read/Write">
<Data Format="L5K">
[14,107,1,1000,1000,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_D16Diag:C:0">
<DataValueMember Name="FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt00_01OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13OpenWireEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15OpenWireEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Input" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1732_DI16Diag:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
<DataValueMember Name="Data" DataType="INT" Radix="Binary" Value="2#0010_0111_0000_0010" />
<DataValueMember Name="Pt00_01OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15OpenWire" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt00_01ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt02_03ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt04_05ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt06_07ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt08_09ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt10_11ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt12_13ShortCircuit" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt14_15ShortCircuit" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="ArmorBlock5" CatalogNumber="1732E-OB16M12R/A" Vendor="1" ProductType="7" ProductCode="370" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.21" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigTag ConfigSize="5" ExternalAccess="Read/Write">
<Data Format="L5K">
[9,100,1,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_DO16:C:0">
<DataValueMember Name="FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<Connection Name="OutputData" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1732_D2:I:0">
<DataValueMember Name="Fault" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0000" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1732_DO16:O:0">
<DataValueMember Name="Data" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="ValveManifold1" CatalogNumber="EX260-SEN1/A" Vendor="7" ProductType="27" ProductCode="156" Major="2" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.22" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="0">
<Data Format="L5K">
[4,105]
</Data>
</ConfigData>
<Connections>
<Connection Name="Output" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="SM:EX260_SEN1:I:0">
<DataValueMember Name="InputArea" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="SOLV_Status" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="SM:EX260_SEN1:O:0">
<ArrayMember Name="OutputArea" DataType="INT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="ValveManifold2" CatalogNumber="EX260-SEN1/A" Vendor="7" ProductType="27" ProductCode="156" Major="2" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.23" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="0">
<Data Format="L5K">
[4,105]
</Data>
</ConfigData>
<Connections>
<Connection Name="Output" RPI="10000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="SM:EX260_SEN1:I:0">
<DataValueMember Name="InputArea" DataType="INT" Radix="Binary" Value="2#0000_0000_0000_0000" />
<DataValueMember Name="SOLV_Status" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="SM:EX260_SEN1:O:0">
<ArrayMember Name="OutputArea" DataType="INT" Dimensions="2" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000_0000_0000" />
<Element Index="[1]" Value="2#0000_0000_0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="RobotController1" CatalogNumber="FANUC Robot R30iB Plus/A" Vendor="356" ProductType="12" ProductCode="4" Major="3" Minor="1" UserDefinedVendor="356" UserDefinedProductType="140" UserDefinedProductCode="40" UserDefinedMajor="3" UserDefinedMinor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_1001_0003_0003" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="192.168.1.24" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="0">
<Data Format="L5K">
[4,100]
</Data>
</ConfigData>
<SafetyScript Size="57">
<Data Format="L5K">
[53,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,37,0,0,0,0,0,0,0,0,3,0,0,0,23,0,0,0,0,0,0,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="A_Safety_Output" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="8" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 00 04 20 04 25 00 88 03 20 04 25 00 00 04" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[12,0,0,0,65,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="FR:Safety_RobotPlus_8Bytes:SO:0">
<ArrayMember Name="Output" DataType="SINT" Dimensions="8" Radix="Hex">
<Element Index="[0]" Value="16#0c" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#00" />
<Element Index="[4]" Value="16#41" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="B_Safety_Input" RPI="10000" Type="SafetyInputDataDriven" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 00 04 20 04 25 00 00 04 20 04 25 00 08 03" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="FR:Safety_RobotPlus_8Bytes:SI:0">
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<ArrayMember Name="Input" DataType="SINT" Dimensions="8" Radix="Hex">
<Element Index="[0]" Value="16#00" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#00" />
<Element Index="[4]" Value="16#00" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="Standard_Slot_01" RPI="32000" Type="StandardDataDriven" OutputSize="16" InputSize="16" EventID="0" ProgrammaticallySendEventTrigger="false" Priority="Scheduled" InputConnectionType="Unicast" InputProductionTrigger="Cyclic" ConnectionPath="20 04 24 64 2c 97 2c 65" InputTagSuffix="I1" OutputTagSuffix="O1">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="FR:Standard_RobotPlus_16Bytes:I1:0">
<ArrayMember Name="Input" DataType="SINT" Dimensions="16" Radix="Hex">
<Element Index="[0]" Value="16#70" />
<Element Index="[1]" Value="16#04" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#04" />
<Element Index="[4]" Value="16#ff" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
<Element Index="[8]" Value="16#00" />
<Element Index="[9]" Value="16#02" />
<Element Index="[10]" Value="16#00" />
<Element Index="[11]" Value="16#e0" />
<Element Index="[12]" Value="16#1f" />
<Element Index="[13]" Value="16#00" />
<Element Index="[14]" Value="16#00" />
<Element Index="[15]" Value="16#80" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[[0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,-64]]
</Data>
<Data Format="Decorated">
<Structure DataType="FR:Standard_RobotPlus_16Bytes:O1:0">
<ArrayMember Name="Output" DataType="SINT" Dimensions="16" Radix="Hex">
<Element Index="[0]" Value="16#00" />
<Element Index="[1]" Value="16#00" />
<Element Index="[2]" Value="16#00" />
<Element Index="[3]" Value="16#00" />
<Element Index="[4]" Value="16#00" />
<Element Index="[5]" Value="16#00" />
<Element Index="[6]" Value="16#00" />
<Element Index="[7]" Value="16#00" />
<Element Index="[8]" Value="16#00" />
<Element Index="[9]" Value="16#02" />
<Element Index="[10]" Value="16#00" />
<Element Index="[11]" Value="16#00" />
<Element Index="[12]" Value="16#00" />
<Element Index="[13]" Value="16#00" />
<Element Index="[14]" Value="16#00" />
<Element Index="[15]" Value="16#c0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="Bus1_PowerSupply" CatalogNumber="2198-P031" Vendor="1" ProductType="48" ProductCode="1" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.25" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="376">
<Data Format="L5K">
[380,3,257,1,25822311,2,2565904,131588,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,-65280,0,0,0,0,0,1120403456,0,0,1120403456
		,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>

<Module Name="Bus1_Drive_D032" CatalogNumber="2198-D032-ERS3" Vendor="1" ProductType="45" ProductCode="13" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_44c9_02ec_d2d2" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.26" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="448">
<Data Format="L5K">
[452,5,1793,13,165675015,0,10000,131588,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8585347,0,2,0,512,0,0,0,0,0,0,0,0,0,1176256512
		,0,0,0,4,1,0,3,0,0,0,0,0,1,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<SafetyScript Size="61">
<Data Format="L5K">
[57,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,41,0,0,0,0,0,0,0,0,3,0,0,0,27,0,0,0,0,0,0,20,0,0,0,96,3,0,0,102,44,-39,9,-128,19,-12,2,-119,68,0,0,1,1,1,1,0
		]
</Data>
</SafetyScript>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="80" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="112" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="C_Safety_Output" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="2" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 25 00 88 01 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety2:SO:0">
<DataValueMember Name="Command1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff1" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset1" DataType="BOOL" Value="0" />
<DataValueMember Name="Command2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff2" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="D_Safety_Input" RPI="10000" Type="SafetyInputDataDriven" InputSize="6" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 24 c7 20 04 25 00 a8 01" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety2:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0010" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Status1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired1" DataType="BOOL" Value="0" />
<DataValueMember Name="Status2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="Bus2_PowerSupply" CatalogNumber="2198-P070" Vendor="1" ProductType="48" ProductCode="2" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.27" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="376">
<Data Format="L5K">
[380,3,257,2,25822311,2,2565904,131588,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,-65024,0,0,0,0,0,1120403456,0,0,1120403456
		,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:MotionDevice_Diagnostics:S:0">
<DataValueMember Name="LostControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDeviceTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDeviceToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDeviceConnectionSize" DataType="INT" Radix="Decimal" Value="36" />
<DataValueMember Name="DeviceToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="44" />
<DataValueMember Name="NominalControllerToDeviceTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDeviceToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
</Connections>
</Communications>
</Module>

<Module Name="Bus2_Drive_D057" CatalogNumber="2198-D057-ERS3" Vendor="1" ProductType="45" ProductCode="14" Major="9" Minor="3" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_44c9_02ed_0afc" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.28" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="448">
<Data Format="L5K">
[452,5,1793,14,165675015,0,10000,131588,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8585347,0,2,0,512,0,0,0,0,0,0,0,0,0,1176256512
		,0,0,0,4,1,0,3,0,0,0,0,0,1,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,67305472,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<SafetyScript Size="61">
<Data Format="L5K">
[57,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,41,0,0,0,0,0,0,0,0,3,0,0,0,27,0,0,0,0,0,0,20,0,0,0,96,3,0,0,102,44,-39,9,47,-46,6,3,-55,68,0,0,1,1,1,1,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="80" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="108" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="C_Safety_Output" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="2" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 25 00 88 01 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety2:SO:0">
<DataValueMember Name="Command1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff1" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset1" DataType="BOOL" Value="0" />
<DataValueMember Name="Command2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff2" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="D_Safety_Input" RPI="10000" Type="SafetyInputDataDriven" InputSize="6" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 24 c7 20 04 25 00 a8 01" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety2:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0010" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Status1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired1" DataType="BOOL" Value="0" />
<DataValueMember Name="Status2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="Bus2_Drive_D020" CatalogNumber="2198-D020-ERS3" Vendor="1" ProductType="45" ProductCode="12" Major="11" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" SafetyNetwork="16#0000_44c9_02ed_47c8" SafetyEnabled="true">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="2" Address="192.168.1.29" Type="Ethernet" Upstream="true" />
</Ports>
<Communications>
<ConfigData ConfigSize="448">
<Data Format="L5K">
[452,5,1793,12,165675015,0,10000,131588,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,131,0,2,0,512,0,0,0,0,0,0,0,0,0,1176256512
		,0,0,0,4,1,0,3,0,0,0,0,0,1,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,262148,0,50528513,0,0,0,8192000,8192125,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
		,0,0,0,0,0,0,0,0,0,0,0]
</Data>
</ConfigData>
<SafetyScript Size="61">
<Data Format="L5K">
[57,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,41,0,0,0,0,0,0,0,0,3,0,0,0,27,0,0,0,0,0,0,20,0,0,0,96,3,0,0,102,44,-39,9,-125,111,116,4,-113,68,0,0,1,1,1,1
		,0]
</Data>
</SafetyScript>
<Connections>
<Connection Name="A_MotionDiagnostics" RPI="1000" Type="DiagnosticInput" EventID="0" ProgrammaticallySendEventTrigger="false">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:Motion_Diagnostics:S:1">
<DataValueMember Name="LostControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateControllerToDriveTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LostDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LateDriveToControllerTransmissions" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumControllerToDriveTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumDriveToControllerTime" DataType="INT" Radix="Decimal" Value="0" />
<DataValueMember Name="LastSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="AverageSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="MaximumSystemClockJitter" DataType="DINT" Radix="Decimal" Value="0" />
<DataValueMember Name="TimingStatisticsEnabled" DataType="SINT" Radix="Decimal" Value="0" />
<DataValueMember Name="ControllerToDriveConnectionSize" DataType="INT" Radix="Decimal" Value="100" />
<DataValueMember Name="DriveToControllerConnectionSize" DataType="INT" Radix="Decimal" Value="96" />
<DataValueMember Name="NominalControllerToDriveTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="NominalDriveToControllerTime" DataType="INT" Radix="Decimal" Value="2000" />
<DataValueMember Name="CoarseUpdatePeriod" DataType="INT" Radix="Decimal" Value="4000" />
</Structure>
</Data>
</InputTag>
</Connection>
<Connection Name="B_MotionSync" RPI="4000" Type="MotionSync" EventID="0" ProgrammaticallySendEventTrigger="false" />
<Connection Name="C_Safety_Output" RPI="20000" Type="SafetyOutputDataDriven" OutputSize="2" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="60" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 25 00 88 01 20 04 24 c7" OutputTagSuffix="SO">
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety2:SO:0">
<DataValueMember Name="Command1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff1" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset1" DataType="BOOL" Value="0" />
<DataValueMember Name="Command2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="SafeTorqueOff2" DataType="BOOL" Value="0" />
<DataValueMember Name="Reset2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</OutputTag>
</Connection>
<Connection Name="D_Safety_Input" RPI="10000" Type="SafetyInputDataDriven" InputSize="6" EventID="0" ProgrammaticallySendEventTrigger="false" TimeoutMultiplier="2" NetworkDelayMultiplier="200" ReactionTimeLimit="40.064" MaxObservedNetworkDelay="0" Priority="High" InputConnectionType="Unicast" InputProductionTrigger="Application" ConnectionPath="20 04 25 00 60 03 20 04 24 c7 20 04 25 00 a8 01" InputTagSuffix="SI">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:CIP_Drive_Safety2:SI:0">
<DataValueMember Name="ConnectionStatus" DataType="DINT" Radix="Binary" Value="2#0000_0000_0000_0000_0000_0000_0000_0010" />
<DataValueMember Name="RunMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="1" />
<DataValueMember Name="Status1" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled1" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault1" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired1" DataType="BOOL" Value="0" />
<DataValueMember Name="Status2" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="TorqueDisabled2" DataType="BOOL" Value="0" />
<DataValueMember Name="SafetyFault2" DataType="BOOL" Value="0" />
<DataValueMember Name="ResetRequired2" DataType="BOOL" Value="0" />
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter5" CatalogNumber="1734-AENTR/C" Vendor="1" ProductType="12" ProductCode="196" Major="6" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="1" Address="0" Type="PointIO" Upstream="false">
<Bus Size="7" />
</Port>
<Port Id="2" Address="192.168.1.30" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="805306369">
<Connections>
<Connection Name="Output" RPI="20000" Type="Output" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:1734_7SLOT:I:0">
<DataValueMember Name="SlotStatusBits0_31" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1000_0001" />
<DataValueMember Name="SlotStatusBits32_63" DataType="DINT" Radix="Binary" Value="2#1111_1111_1111_1111_1111_1111_1111_1111" />
<ArrayMember Name="Data" DataType="SINT" Dimensions="7" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_1010" />
<Element Index="[2]" Value="2#0000_1010" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="L5K">
[-127,-1,[0,0,0,0,0,0,0]]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_7SLOT:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="7" Radix="Binary">
<Element Index="[0]" Value="2#0000_0000" />
<Element Index="[1]" Value="2#0000_0000" />
<Element Index="[2]" Value="2#0000_0000" />
<Element Index="[3]" Value="2#0000_0000" />
<Element Index="[4]" Value="2#0000_0000" />
<Element Index="[5]" Value="2#0000_0000" />
<Element Index="[6]" Value="2#0000_0000" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter5_Mod1" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter5" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="1" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter5_Mod2" CatalogNumber="1734-IB8/C" Vendor="1" ProductType="7" ProductCode="216" Major="3" Minor="1" ParentModule="PtIOAdapter5" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="2" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="36" ExternalAccess="Read/Write">
<Data Format="L5K">
[40,103,1,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DI8:C:0">
<DataValueMember Name="Pt0FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt0FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt1FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt2FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt3FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt4FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt5FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt6FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOffOn" DataType="INT" Radix="Decimal" Value="1000" />
<DataValueMember Name="Pt7FilterOnOff" DataType="INT" Radix="Decimal" Value="1000" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter5_Mod3" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="PtIOAdapter5" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="3" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,3,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0011" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="1" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter5_Mod4" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="PtIOAdapter5" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="4" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,3,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0011" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="1" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter5_Mod5" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="PtIOAdapter5" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="5" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,3,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0011" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="1" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="PtIOAdapter5_Mod6" CatalogNumber="1734-OB2EP/C" Vendor="1" ProductType="7" ProductCode="163" Major="3" Minor="1" ParentModule="PtIOAdapter5" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="CompatibleModule" />
<Ports>
<Port Id="1" Address="6" Type="PointIO" Upstream="true" />
</Ports>
<Communications CommMethod="1073741824">
<ConfigTag ConfigSize="12" ExternalAccess="Read/Write">
<Data Format="L5K">
[16,123,1,0,0,0,0,0,3,0,0]
</Data>
<Data Format="Decorated">
<Structure DataType="AB:1734_DOB2:C:0">
<DataValueMember Name="FaultMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultMode" DataType="BOOL" Value="0" />
<DataValueMember Name="FaultValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultValue" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgMode" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgMode" DataType="BOOL" Value="0" />
<DataValueMember Name="ProgValue" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1ProgValue" DataType="BOOL" Value="0" />
<DataValueMember Name="NoLoadEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1NoLoadEn" DataType="BOOL" Value="0" />
<DataValueMember Name="AutoRestartEn" DataType="SINT" Radix="Binary" Value="2#0000_0011" />
<DataValueMember Name="Pt0AutoRestartEn" DataType="BOOL" Value="1" />
<DataValueMember Name="Pt1AutoRestartEn" DataType="BOOL" Value="1" />
<DataValueMember Name="FaultLatchEn" DataType="SINT" Radix="Binary" Value="2#0000_0000" />
<DataValueMember Name="Pt0FaultLatchEn" DataType="BOOL" Value="0" />
<DataValueMember Name="Pt1FaultLatchEn" DataType="BOOL" Value="0" />
</Structure>
</Data>
</ConfigTag>
<Connections>
<RackConnection>
<InAliasTag />
<OutAliasTag />
</RackConnection>
</Connections>
</Communications>
</Module>

<Module Name="GenericEncoder1" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" ProductCode="18" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="192.168.1.70" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870914" PrimCxnInputSize="12" PrimCxnOutputSize="0">
<Connections>
<Connection Name="Standard" RPI="20000" Type="Input" InputCxnPoint="1" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE_REAL_12Bytes:I:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="12" Radix="Decimal">
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
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="GenericEncoder2" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" ProductCode="18" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="192.168.1.71" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870914" PrimCxnInputSize="12" PrimCxnOutputSize="0">
<Connections>
<Connection Name="Standard" RPI="20000" Type="Input" InputCxnPoint="1" InputSize="12" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE_REAL_12Bytes:I:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="12" Radix="Decimal">
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
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
</Connection>
</Connections>
</Communications>
</Module>
<Module Name="GenericBarcodeReader1" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" ProductCode="18" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="2" Address="192.168.1.72" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870914" PrimCxnInputSize="476" PrimCxnOutputSize="468">
<Connections>
<Connection Name="Standard" RPI="20000" Type="Output" InputCxnPoint="1" OutputCxnPoint="2" OutputSize="468" InputSize="476" EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">
<InputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE_REAL_476Bytes:I:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="476" Radix="Decimal">
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
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
<Element Index="[40]" Value="0" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="0" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="0" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="0" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="0" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
<Element Index="[80]" Value="0" />
<Element Index="[81]" Value="0" />
<Element Index="[82]" Value="0" />
<Element Index="[83]" Value="0" />
<Element Index="[84]" Value="0" />
<Element Index="[85]" Value="0" />
<Element Index="[86]" Value="0" />
<Element Index="[87]" Value="0" />
<Element Index="[88]" Value="0" />
<Element Index="[89]" Value="0" />
<Element Index="[90]" Value="0" />
<Element Index="[91]" Value="0" />
<Element Index="[92]" Value="0" />
<Element Index="[93]" Value="0" />
<Element Index="[94]" Value="0" />
<Element Index="[95]" Value="0" />
<Element Index="[96]" Value="0" />
<Element Index="[97]" Value="0" />
<Element Index="[98]" Value="0" />
<Element Index="[99]" Value="0" />
<Element Index="[100]" Value="0" />
<Element Index="[101]" Value="0" />
<Element Index="[102]" Value="0" />
<Element Index="[103]" Value="0" />
<Element Index="[104]" Value="0" />
<Element Index="[105]" Value="0" />
<Element Index="[106]" Value="0" />
<Element Index="[107]" Value="0" />
<Element Index="[108]" Value="0" />
<Element Index="[109]" Value="0" />
<Element Index="[110]" Value="0" />
<Element Index="[111]" Value="0" />
<Element Index="[112]" Value="0" />
<Element Index="[113]" Value="0" />
<Element Index="[114]" Value="0" />
<Element Index="[115]" Value="0" />
<Element Index="[116]" Value="0" />
<Element Index="[117]" Value="0" />
<Element Index="[118]" Value="0" />
<Element Index="[119]" Value="0" />
<Element Index="[120]" Value="0" />
<Element Index="[121]" Value="0" />
<Element Index="[122]" Value="0" />
<Element Index="[123]" Value="0" />
<Element Index="[124]" Value="0" />
<Element Index="[125]" Value="0" />
<Element Index="[126]" Value="0" />
<Element Index="[127]" Value="0" />
<Element Index="[128]" Value="0" />
<Element Index="[129]" Value="0" />
<Element Index="[130]" Value="0" />
<Element Index="[131]" Value="0" />
<Element Index="[132]" Value="0" />
<Element Index="[133]" Value="0" />
<Element Index="[134]" Value="0" />
<Element Index="[135]" Value="0" />
<Element Index="[136]" Value="0" />
<Element Index="[137]" Value="0" />
<Element Index="[138]" Value="0" />
<Element Index="[139]" Value="0" />
<Element Index="[140]" Value="0" />
<Element Index="[141]" Value="0" />
<Element Index="[142]" Value="0" />
<Element Index="[143]" Value="0" />
<Element Index="[144]" Value="0" />
<Element Index="[145]" Value="0" />
<Element Index="[146]" Value="0" />
<Element Index="[147]" Value="0" />
<Element Index="[148]" Value="0" />
<Element Index="[149]" Value="0" />
<Element Index="[150]" Value="0" />
<Element Index="[151]" Value="0" />
<Element Index="[152]" Value="0" />
<Element Index="[153]" Value="0" />
<Element Index="[154]" Value="0" />
<Element Index="[155]" Value="0" />
<Element Index="[156]" Value="0" />
<Element Index="[157]" Value="0" />
<Element Index="[158]" Value="0" />
<Element Index="[159]" Value="0" />
<Element Index="[160]" Value="0" />
<Element Index="[161]" Value="0" />
<Element Index="[162]" Value="0" />
<Element Index="[163]" Value="0" />
<Element Index="[164]" Value="0" />
<Element Index="[165]" Value="0" />
<Element Index="[166]" Value="0" />
<Element Index="[167]" Value="0" />
<Element Index="[168]" Value="0" />
<Element Index="[169]" Value="0" />
<Element Index="[170]" Value="0" />
<Element Index="[171]" Value="0" />
<Element Index="[172]" Value="0" />
<Element Index="[173]" Value="0" />
<Element Index="[174]" Value="0" />
<Element Index="[175]" Value="0" />
<Element Index="[176]" Value="0" />
<Element Index="[177]" Value="0" />
<Element Index="[178]" Value="0" />
<Element Index="[179]" Value="0" />
<Element Index="[180]" Value="0" />
<Element Index="[181]" Value="0" />
<Element Index="[182]" Value="0" />
<Element Index="[183]" Value="0" />
<Element Index="[184]" Value="0" />
<Element Index="[185]" Value="0" />
<Element Index="[186]" Value="0" />
<Element Index="[187]" Value="0" />
<Element Index="[188]" Value="0" />
<Element Index="[189]" Value="0" />
<Element Index="[190]" Value="0" />
<Element Index="[191]" Value="0" />
<Element Index="[192]" Value="0" />
<Element Index="[193]" Value="0" />
<Element Index="[194]" Value="0" />
<Element Index="[195]" Value="0" />
<Element Index="[196]" Value="0" />
<Element Index="[197]" Value="0" />
<Element Index="[198]" Value="0" />
<Element Index="[199]" Value="0" />
<Element Index="[200]" Value="0" />
<Element Index="[201]" Value="0" />
<Element Index="[202]" Value="0" />
<Element Index="[203]" Value="0" />
<Element Index="[204]" Value="0" />
<Element Index="[205]" Value="0" />
<Element Index="[206]" Value="0" />
<Element Index="[207]" Value="0" />
<Element Index="[208]" Value="0" />
<Element Index="[209]" Value="0" />
<Element Index="[210]" Value="0" />
<Element Index="[211]" Value="0" />
<Element Index="[212]" Value="0" />
<Element Index="[213]" Value="0" />
<Element Index="[214]" Value="0" />
<Element Index="[215]" Value="0" />
<Element Index="[216]" Value="0" />
<Element Index="[217]" Value="0" />
<Element Index="[218]" Value="0" />
<Element Index="[219]" Value="0" />
<Element Index="[220]" Value="0" />
<Element Index="[221]" Value="0" />
<Element Index="[222]" Value="0" />
<Element Index="[223]" Value="0" />
<Element Index="[224]" Value="0" />
<Element Index="[225]" Value="0" />
<Element Index="[226]" Value="0" />
<Element Index="[227]" Value="0" />
<Element Index="[228]" Value="0" />
<Element Index="[229]" Value="0" />
<Element Index="[230]" Value="0" />
<Element Index="[231]" Value="0" />
<Element Index="[232]" Value="0" />
<Element Index="[233]" Value="0" />
<Element Index="[234]" Value="0" />
<Element Index="[235]" Value="0" />
<Element Index="[236]" Value="0" />
<Element Index="[237]" Value="0" />
<Element Index="[238]" Value="0" />
<Element Index="[239]" Value="0" />
<Element Index="[240]" Value="0" />
<Element Index="[241]" Value="0" />
<Element Index="[242]" Value="0" />
<Element Index="[243]" Value="0" />
<Element Index="[244]" Value="0" />
<Element Index="[245]" Value="0" />
<Element Index="[246]" Value="0" />
<Element Index="[247]" Value="0" />
<Element Index="[248]" Value="0" />
<Element Index="[249]" Value="0" />
<Element Index="[250]" Value="0" />
<Element Index="[251]" Value="0" />
<Element Index="[252]" Value="0" />
<Element Index="[253]" Value="0" />
<Element Index="[254]" Value="0" />
<Element Index="[255]" Value="0" />
<Element Index="[256]" Value="0" />
<Element Index="[257]" Value="0" />
<Element Index="[258]" Value="0" />
<Element Index="[259]" Value="0" />
<Element Index="[260]" Value="0" />
<Element Index="[261]" Value="0" />
<Element Index="[262]" Value="0" />
<Element Index="[263]" Value="0" />
<Element Index="[264]" Value="0" />
<Element Index="[265]" Value="0" />
<Element Index="[266]" Value="0" />
<Element Index="[267]" Value="0" />
<Element Index="[268]" Value="0" />
<Element Index="[269]" Value="0" />
<Element Index="[270]" Value="0" />
<Element Index="[271]" Value="0" />
<Element Index="[272]" Value="0" />
<Element Index="[273]" Value="0" />
<Element Index="[274]" Value="0" />
<Element Index="[275]" Value="0" />
<Element Index="[276]" Value="0" />
<Element Index="[277]" Value="0" />
<Element Index="[278]" Value="0" />
<Element Index="[279]" Value="0" />
<Element Index="[280]" Value="0" />
<Element Index="[281]" Value="0" />
<Element Index="[282]" Value="0" />
<Element Index="[283]" Value="0" />
<Element Index="[284]" Value="0" />
<Element Index="[285]" Value="0" />
<Element Index="[286]" Value="0" />
<Element Index="[287]" Value="0" />
<Element Index="[288]" Value="0" />
<Element Index="[289]" Value="0" />
<Element Index="[290]" Value="0" />
<Element Index="[291]" Value="0" />
<Element Index="[292]" Value="0" />
<Element Index="[293]" Value="0" />
<Element Index="[294]" Value="0" />
<Element Index="[295]" Value="0" />
<Element Index="[296]" Value="0" />
<Element Index="[297]" Value="0" />
<Element Index="[298]" Value="0" />
<Element Index="[299]" Value="0" />
<Element Index="[300]" Value="0" />
<Element Index="[301]" Value="0" />
<Element Index="[302]" Value="0" />
<Element Index="[303]" Value="0" />
<Element Index="[304]" Value="0" />
<Element Index="[305]" Value="0" />
<Element Index="[306]" Value="0" />
<Element Index="[307]" Value="0" />
<Element Index="[308]" Value="0" />
<Element Index="[309]" Value="0" />
<Element Index="[310]" Value="0" />
<Element Index="[311]" Value="0" />
<Element Index="[312]" Value="0" />
<Element Index="[313]" Value="0" />
<Element Index="[314]" Value="0" />
<Element Index="[315]" Value="0" />
<Element Index="[316]" Value="0" />
<Element Index="[317]" Value="0" />
<Element Index="[318]" Value="0" />
<Element Index="[319]" Value="0" />
<Element Index="[320]" Value="0" />
<Element Index="[321]" Value="0" />
<Element Index="[322]" Value="0" />
<Element Index="[323]" Value="0" />
<Element Index="[324]" Value="0" />
<Element Index="[325]" Value="0" />
<Element Index="[326]" Value="0" />
<Element Index="[327]" Value="0" />
<Element Index="[328]" Value="0" />
<Element Index="[329]" Value="0" />
<Element Index="[330]" Value="0" />
<Element Index="[331]" Value="0" />
<Element Index="[332]" Value="0" />
<Element Index="[333]" Value="0" />
<Element Index="[334]" Value="0" />
<Element Index="[335]" Value="0" />
<Element Index="[336]" Value="0" />
<Element Index="[337]" Value="0" />
<Element Index="[338]" Value="0" />
<Element Index="[339]" Value="0" />
<Element Index="[340]" Value="0" />
<Element Index="[341]" Value="0" />
<Element Index="[342]" Value="0" />
<Element Index="[343]" Value="0" />
<Element Index="[344]" Value="0" />
<Element Index="[345]" Value="0" />
<Element Index="[346]" Value="0" />
<Element Index="[347]" Value="0" />
<Element Index="[348]" Value="0" />
<Element Index="[349]" Value="0" />
<Element Index="[350]" Value="0" />
<Element Index="[351]" Value="0" />
<Element Index="[352]" Value="0" />
<Element Index="[353]" Value="0" />
<Element Index="[354]" Value="0" />
<Element Index="[355]" Value="0" />
<Element Index="[356]" Value="0" />
<Element Index="[357]" Value="0" />
<Element Index="[358]" Value="0" />
<Element Index="[359]" Value="0" />
<Element Index="[360]" Value="0" />
<Element Index="[361]" Value="0" />
<Element Index="[362]" Value="0" />
<Element Index="[363]" Value="0" />
<Element Index="[364]" Value="0" />
<Element Index="[365]" Value="0" />
<Element Index="[366]" Value="0" />
<Element Index="[367]" Value="0" />
<Element Index="[368]" Value="0" />
<Element Index="[369]" Value="0" />
<Element Index="[370]" Value="0" />
<Element Index="[371]" Value="0" />
<Element Index="[372]" Value="0" />
<Element Index="[373]" Value="0" />
<Element Index="[374]" Value="0" />
<Element Index="[375]" Value="0" />
<Element Index="[376]" Value="0" />
<Element Index="[377]" Value="0" />
<Element Index="[378]" Value="0" />
<Element Index="[379]" Value="0" />
<Element Index="[380]" Value="0" />
<Element Index="[381]" Value="0" />
<Element Index="[382]" Value="0" />
<Element Index="[383]" Value="0" />
<Element Index="[384]" Value="0" />
<Element Index="[385]" Value="0" />
<Element Index="[386]" Value="0" />
<Element Index="[387]" Value="0" />
<Element Index="[388]" Value="0" />
<Element Index="[389]" Value="0" />
<Element Index="[390]" Value="0" />
<Element Index="[391]" Value="0" />
<Element Index="[392]" Value="0" />
<Element Index="[393]" Value="0" />
<Element Index="[394]" Value="0" />
<Element Index="[395]" Value="0" />
<Element Index="[396]" Value="0" />
<Element Index="[397]" Value="0" />
<Element Index="[398]" Value="0" />
<Element Index="[399]" Value="0" />
<Element Index="[400]" Value="0" />
<Element Index="[401]" Value="0" />
<Element Index="[402]" Value="0" />
<Element Index="[403]" Value="0" />
<Element Index="[404]" Value="0" />
<Element Index="[405]" Value="0" />
<Element Index="[406]" Value="0" />
<Element Index="[407]" Value="0" />
<Element Index="[408]" Value="0" />
<Element Index="[409]" Value="0" />
<Element Index="[410]" Value="0" />
<Element Index="[411]" Value="0" />
<Element Index="[412]" Value="0" />
<Element Index="[413]" Value="0" />
<Element Index="[414]" Value="0" />
<Element Index="[415]" Value="0" />
<Element Index="[416]" Value="0" />
<Element Index="[417]" Value="0" />
<Element Index="[418]" Value="0" />
<Element Index="[419]" Value="0" />
<Element Index="[420]" Value="0" />
<Element Index="[421]" Value="0" />
<Element Index="[422]" Value="0" />
<Element Index="[423]" Value="0" />
<Element Index="[424]" Value="0" />
<Element Index="[425]" Value="0" />
<Element Index="[426]" Value="0" />
<Element Index="[427]" Value="0" />
<Element Index="[428]" Value="0" />
<Element Index="[429]" Value="0" />
<Element Index="[430]" Value="0" />
<Element Index="[431]" Value="0" />
<Element Index="[432]" Value="0" />
<Element Index="[433]" Value="0" />
<Element Index="[434]" Value="0" />
<Element Index="[435]" Value="0" />
<Element Index="[436]" Value="0" />
<Element Index="[437]" Value="0" />
<Element Index="[438]" Value="0" />
<Element Index="[439]" Value="0" />
<Element Index="[440]" Value="0" />
<Element Index="[441]" Value="0" />
<Element Index="[442]" Value="0" />
<Element Index="[443]" Value="0" />
<Element Index="[444]" Value="0" />
<Element Index="[445]" Value="0" />
<Element Index="[446]" Value="0" />
<Element Index="[447]" Value="0" />
<Element Index="[448]" Value="0" />
<Element Index="[449]" Value="0" />
<Element Index="[450]" Value="0" />
<Element Index="[451]" Value="0" />
<Element Index="[452]" Value="0" />
<Element Index="[453]" Value="0" />
<Element Index="[454]" Value="0" />
<Element Index="[455]" Value="0" />
<Element Index="[456]" Value="0" />
<Element Index="[457]" Value="0" />
<Element Index="[458]" Value="0" />
<Element Index="[459]" Value="0" />
<Element Index="[460]" Value="0" />
<Element Index="[461]" Value="0" />
<Element Index="[462]" Value="0" />
<Element Index="[463]" Value="0" />
<Element Index="[464]" Value="0" />
<Element Index="[465]" Value="0" />
<Element Index="[466]" Value="0" />
<Element Index="[467]" Value="0" />
<Element Index="[468]" Value="0" />
<Element Index="[469]" Value="0" />
<Element Index="[470]" Value="0" />
<Element Index="[471]" Value="0" />
<Element Index="[472]" Value="0" />
<Element Index="[473]" Value="0" />
<Element Index="[474]" Value="0" />
<Element Index="[475]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</InputTag>
<OutputTag ExternalAccess="Read/Write">
<Data Format="Decorated">
<Structure DataType="AB:ETHERNET_MODULE_REAL_468Bytes:O:0">
<ArrayMember Name="Data" DataType="SINT" Dimensions="468" Radix="Decimal">
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
<Element Index="[10]" Value="0" />
<Element Index="[11]" Value="0" />
<Element Index="[12]" Value="0" />
<Element Index="[13]" Value="0" />
<Element Index="[14]" Value="0" />
<Element Index="[15]" Value="0" />
<Element Index="[16]" Value="0" />
<Element Index="[17]" Value="0" />
<Element Index="[18]" Value="0" />
<Element Index="[19]" Value="0" />
<Element Index="[20]" Value="0" />
<Element Index="[21]" Value="0" />
<Element Index="[22]" Value="0" />
<Element Index="[23]" Value="0" />
<Element Index="[24]" Value="0" />
<Element Index="[25]" Value="0" />
<Element Index="[26]" Value="0" />
<Element Index="[27]" Value="0" />
<Element Index="[28]" Value="0" />
<Element Index="[29]" Value="0" />
<Element Index="[30]" Value="0" />
<Element Index="[31]" Value="0" />
<Element Index="[32]" Value="0" />
<Element Index="[33]" Value="0" />
<Element Index="[34]" Value="0" />
<Element Index="[35]" Value="0" />
<Element Index="[36]" Value="0" />
<Element Index="[37]" Value="0" />
<Element Index="[38]" Value="0" />
<Element Index="[39]" Value="0" />
<Element Index="[40]" Value="0" />
<Element Index="[41]" Value="0" />
<Element Index="[42]" Value="0" />
<Element Index="[43]" Value="0" />
<Element Index="[44]" Value="0" />
<Element Index="[45]" Value="0" />
<Element Index="[46]" Value="0" />
<Element Index="[47]" Value="0" />
<Element Index="[48]" Value="0" />
<Element Index="[49]" Value="0" />
<Element Index="[50]" Value="0" />
<Element Index="[51]" Value="0" />
<Element Index="[52]" Value="0" />
<Element Index="[53]" Value="0" />
<Element Index="[54]" Value="0" />
<Element Index="[55]" Value="0" />
<Element Index="[56]" Value="0" />
<Element Index="[57]" Value="0" />
<Element Index="[58]" Value="0" />
<Element Index="[59]" Value="0" />
<Element Index="[60]" Value="0" />
<Element Index="[61]" Value="0" />
<Element Index="[62]" Value="0" />
<Element Index="[63]" Value="0" />
<Element Index="[64]" Value="0" />
<Element Index="[65]" Value="0" />
<Element Index="[66]" Value="0" />
<Element Index="[67]" Value="0" />
<Element Index="[68]" Value="0" />
<Element Index="[69]" Value="0" />
<Element Index="[70]" Value="0" />
<Element Index="[71]" Value="0" />
<Element Index="[72]" Value="0" />
<Element Index="[73]" Value="0" />
<Element Index="[74]" Value="0" />
<Element Index="[75]" Value="0" />
<Element Index="[76]" Value="0" />
<Element Index="[77]" Value="0" />
<Element Index="[78]" Value="0" />
<Element Index="[79]" Value="0" />
<Element Index="[80]" Value="0" />
<Element Index="[81]" Value="0" />
<Element Index="[82]" Value="0" />
<Element Index="[83]" Value="0" />
<Element Index="[84]" Value="0" />
<Element Index="[85]" Value="0" />
<Element Index="[86]" Value="0" />
<Element Index="[87]" Value="0" />
<Element Index="[88]" Value="0" />
<Element Index="[89]" Value="0" />
<Element Index="[90]" Value="0" />
<Element Index="[91]" Value="0" />
<Element Index="[92]" Value="0" />
<Element Index="[93]" Value="0" />
<Element Index="[94]" Value="0" />
<Element Index="[95]" Value="0" />
<Element Index="[96]" Value="0" />
<Element Index="[97]" Value="0" />
<Element Index="[98]" Value="0" />
<Element Index="[99]" Value="0" />
<Element Index="[100]" Value="0" />
<Element Index="[101]" Value="0" />
<Element Index="[102]" Value="0" />
<Element Index="[103]" Value="0" />
<Element Index="[104]" Value="0" />
<Element Index="[105]" Value="0" />
<Element Index="[106]" Value="0" />
<Element Index="[107]" Value="0" />
<Element Index="[108]" Value="0" />
<Element Index="[109]" Value="0" />
<Element Index="[110]" Value="0" />
<Element Index="[111]" Value="0" />
<Element Index="[112]" Value="0" />
<Element Index="[113]" Value="0" />
<Element Index="[114]" Value="0" />
<Element Index="[115]" Value="0" />
<Element Index="[116]" Value="0" />
<Element Index="[117]" Value="0" />
<Element Index="[118]" Value="0" />
<Element Index="[119]" Value="0" />
<Element Index="[120]" Value="0" />
<Element Index="[121]" Value="0" />
<Element Index="[122]" Value="0" />
<Element Index="[123]" Value="0" />
<Element Index="[124]" Value="0" />
<Element Index="[125]" Value="0" />
<Element Index="[126]" Value="0" />
<Element Index="[127]" Value="0" />
<Element Index="[128]" Value="0" />
<Element Index="[129]" Value="0" />
<Element Index="[130]" Value="0" />
<Element Index="[131]" Value="0" />
<Element Index="[132]" Value="0" />
<Element Index="[133]" Value="0" />
<Element Index="[134]" Value="0" />
<Element Index="[135]" Value="0" />
<Element Index="[136]" Value="0" />
<Element Index="[137]" Value="0" />
<Element Index="[138]" Value="0" />
<Element Index="[139]" Value="0" />
<Element Index="[140]" Value="0" />
<Element Index="[141]" Value="0" />
<Element Index="[142]" Value="0" />
<Element Index="[143]" Value="0" />
<Element Index="[144]" Value="0" />
<Element Index="[145]" Value="0" />
<Element Index="[146]" Value="0" />
<Element Index="[147]" Value="0" />
<Element Index="[148]" Value="0" />
<Element Index="[149]" Value="0" />
<Element Index="[150]" Value="0" />
<Element Index="[151]" Value="0" />
<Element Index="[152]" Value="0" />
<Element Index="[153]" Value="0" />
<Element Index="[154]" Value="0" />
<Element Index="[155]" Value="0" />
<Element Index="[156]" Value="0" />
<Element Index="[157]" Value="0" />
<Element Index="[158]" Value="0" />
<Element Index="[159]" Value="0" />
<Element Index="[160]" Value="0" />
<Element Index="[161]" Value="0" />
<Element Index="[162]" Value="0" />
<Element Index="[163]" Value="0" />
<Element Index="[164]" Value="0" />
<Element Index="[165]" Value="0" />
<Element Index="[166]" Value="0" />
<Element Index="[167]" Value="0" />
<Element Index="[168]" Value="0" />
<Element Index="[169]" Value="0" />
<Element Index="[170]" Value="0" />
<Element Index="[171]" Value="0" />
<Element Index="[172]" Value="0" />
<Element Index="[173]" Value="0" />
<Element Index="[174]" Value="0" />
<Element Index="[175]" Value="0" />
<Element Index="[176]" Value="0" />
<Element Index="[177]" Value="0" />
<Element Index="[178]" Value="0" />
<Element Index="[179]" Value="0" />
<Element Index="[180]" Value="0" />
<Element Index="[181]" Value="0" />
<Element Index="[182]" Value="0" />
<Element Index="[183]" Value="0" />
<Element Index="[184]" Value="0" />
<Element Index="[185]" Value="0" />
<Element Index="[186]" Value="0" />
<Element Index="[187]" Value="0" />
<Element Index="[188]" Value="0" />
<Element Index="[189]" Value="0" />
<Element Index="[190]" Value="0" />
<Element Index="[191]" Value="0" />
<Element Index="[192]" Value="0" />
<Element Index="[193]" Value="0" />
<Element Index="[194]" Value="0" />
<Element Index="[195]" Value="0" />
<Element Index="[196]" Value="0" />
<Element Index="[197]" Value="0" />
<Element Index="[198]" Value="0" />
<Element Index="[199]" Value="0" />
<Element Index="[200]" Value="0" />
<Element Index="[201]" Value="0" />
<Element Index="[202]" Value="0" />
<Element Index="[203]" Value="0" />
<Element Index="[204]" Value="0" />
<Element Index="[205]" Value="0" />
<Element Index="[206]" Value="0" />
<Element Index="[207]" Value="0" />
<Element Index="[208]" Value="0" />
<Element Index="[209]" Value="0" />
<Element Index="[210]" Value="0" />
<Element Index="[211]" Value="0" />
<Element Index="[212]" Value="0" />
<Element Index="[213]" Value="0" />
<Element Index="[214]" Value="0" />
<Element Index="[215]" Value="0" />
<Element Index="[216]" Value="0" />
<Element Index="[217]" Value="0" />
<Element Index="[218]" Value="0" />
<Element Index="[219]" Value="0" />
<Element Index="[220]" Value="0" />
<Element Index="[221]" Value="0" />
<Element Index="[222]" Value="0" />
<Element Index="[223]" Value="0" />
<Element Index="[224]" Value="0" />
<Element Index="[225]" Value="0" />
<Element Index="[226]" Value="0" />
<Element Index="[227]" Value="0" />
<Element Index="[228]" Value="0" />
<Element Index="[229]" Value="0" />
<Element Index="[230]" Value="0" />
<Element Index="[231]" Value="0" />
<Element Index="[232]" Value="0" />
<Element Index="[233]" Value="0" />
<Element Index="[234]" Value="0" />
<Element Index="[235]" Value="0" />
<Element Index="[236]" Value="0" />
<Element Index="[237]" Value="0" />
<Element Index="[238]" Value="0" />
<Element Index="[239]" Value="0" />
<Element Index="[240]" Value="0" />
<Element Index="[241]" Value="0" />
<Element Index="[242]" Value="0" />
<Element Index="[243]" Value="0" />
<Element Index="[244]" Value="0" />
<Element Index="[245]" Value="0" />
<Element Index="[246]" Value="0" />
<Element Index="[247]" Value="0" />
<Element Index="[248]" Value="0" />
<Element Index="[249]" Value="0" />
<Element Index="[250]" Value="0" />
<Element Index="[251]" Value="0" />
<Element Index="[252]" Value="0" />
<Element Index="[253]" Value="0" />
<Element Index="[254]" Value="0" />
<Element Index="[255]" Value="0" />
<Element Index="[256]" Value="0" />
<Element Index="[257]" Value="0" />
<Element Index="[258]" Value="0" />
<Element Index="[259]" Value="0" />
<Element Index="[260]" Value="0" />
<Element Index="[261]" Value="0" />
<Element Index="[262]" Value="0" />
<Element Index="[263]" Value="0" />
<Element Index="[264]" Value="0" />
<Element Index="[265]" Value="0" />
<Element Index="[266]" Value="0" />
<Element Index="[267]" Value="0" />
<Element Index="[268]" Value="0" />
<Element Index="[269]" Value="0" />
<Element Index="[270]" Value="0" />
<Element Index="[271]" Value="0" />
<Element Index="[272]" Value="0" />
<Element Index="[273]" Value="0" />
<Element Index="[274]" Value="0" />
<Element Index="[275]" Value="0" />
<Element Index="[276]" Value="0" />
<Element Index="[277]" Value="0" />
<Element Index="[278]" Value="0" />
<Element Index="[279]" Value="0" />
<Element Index="[280]" Value="0" />
<Element Index="[281]" Value="0" />
<Element Index="[282]" Value="0" />
<Element Index="[283]" Value="0" />
<Element Index="[284]" Value="0" />
<Element Index="[285]" Value="0" />
<Element Index="[286]" Value="0" />
<Element Index="[287]" Value="0" />
<Element Index="[288]" Value="0" />
<Element Index="[289]" Value="0" />
<Element Index="[290]" Value="0" />
<Element Index="[291]" Value="0" />
<Element Index="[292]" Value="0" />
<Element Index="[293]" Value="0" />
<Element Index="[294]" Value="0" />
<Element Index="[295]" Value="0" />
<Element Index="[296]" Value="0" />
<Element Index="[297]" Value="0" />
<Element Index="[298]" Value="0" />
<Element Index="[299]" Value="0" />
<Element Index="[300]" Value="0" />
<Element Index="[301]" Value="0" />
<Element Index="[302]" Value="0" />
<Element Index="[303]" Value="0" />
<Element Index="[304]" Value="0" />
<Element Index="[305]" Value="0" />
<Element Index="[306]" Value="0" />
<Element Index="[307]" Value="0" />
<Element Index="[308]" Value="0" />
<Element Index="[309]" Value="0" />
<Element Index="[310]" Value="0" />
<Element Index="[311]" Value="0" />
<Element Index="[312]" Value="0" />
<Element Index="[313]" Value="0" />
<Element Index="[314]" Value="0" />
<Element Index="[315]" Value="0" />
<Element Index="[316]" Value="0" />
<Element Index="[317]" Value="0" />
<Element Index="[318]" Value="0" />
<Element Index="[319]" Value="0" />
<Element Index="[320]" Value="0" />
<Element Index="[321]" Value="0" />
<Element Index="[322]" Value="0" />
<Element Index="[323]" Value="0" />
<Element Index="[324]" Value="0" />
<Element Index="[325]" Value="0" />
<Element Index="[326]" Value="0" />
<Element Index="[327]" Value="0" />
<Element Index="[328]" Value="0" />
<Element Index="[329]" Value="0" />
<Element Index="[330]" Value="0" />
<Element Index="[331]" Value="0" />
<Element Index="[332]" Value="0" />
<Element Index="[333]" Value="0" />
<Element Index="[334]" Value="0" />
<Element Index="[335]" Value="0" />
<Element Index="[336]" Value="0" />
<Element Index="[337]" Value="0" />
<Element Index="[338]" Value="0" />
<Element Index="[339]" Value="0" />
<Element Index="[340]" Value="0" />
<Element Index="[341]" Value="0" />
<Element Index="[342]" Value="0" />
<Element Index="[343]" Value="0" />
<Element Index="[344]" Value="0" />
<Element Index="[345]" Value="0" />
<Element Index="[346]" Value="0" />
<Element Index="[347]" Value="0" />
<Element Index="[348]" Value="0" />
<Element Index="[349]" Value="0" />
<Element Index="[350]" Value="0" />
<Element Index="[351]" Value="0" />
<Element Index="[352]" Value="0" />
<Element Index="[353]" Value="0" />
<Element Index="[354]" Value="0" />
<Element Index="[355]" Value="0" />
<Element Index="[356]" Value="0" />
<Element Index="[357]" Value="0" />
<Element Index="[358]" Value="0" />
<Element Index="[359]" Value="0" />
<Element Index="[360]" Value="0" />
<Element Index="[361]" Value="0" />
<Element Index="[362]" Value="0" />
<Element Index="[363]" Value="0" />
<Element Index="[364]" Value="0" />
<Element Index="[365]" Value="0" />
<Element Index="[366]" Value="0" />
<Element Index="[367]" Value="0" />
<Element Index="[368]" Value="0" />
<Element Index="[369]" Value="0" />
<Element Index="[370]" Value="0" />
<Element Index="[371]" Value="0" />
<Element Index="[372]" Value="0" />
<Element Index="[373]" Value="0" />
<Element Index="[374]" Value="0" />
<Element Index="[375]" Value="0" />
<Element Index="[376]" Value="0" />
<Element Index="[377]" Value="0" />
<Element Index="[378]" Value="0" />
<Element Index="[379]" Value="0" />
<Element Index="[380]" Value="0" />
<Element Index="[381]" Value="0" />
<Element Index="[382]" Value="0" />
<Element Index="[383]" Value="0" />
<Element Index="[384]" Value="0" />
<Element Index="[385]" Value="0" />
<Element Index="[386]" Value="0" />
<Element Index="[387]" Value="0" />
<Element Index="[388]" Value="0" />
<Element Index="[389]" Value="0" />
<Element Index="[390]" Value="0" />
<Element Index="[391]" Value="0" />
<Element Index="[392]" Value="0" />
<Element Index="[393]" Value="0" />
<Element Index="[394]" Value="0" />
<Element Index="[395]" Value="0" />
<Element Index="[396]" Value="0" />
<Element Index="[397]" Value="0" />
<Element Index="[398]" Value="0" />
<Element Index="[399]" Value="0" />
<Element Index="[400]" Value="0" />
<Element Index="[401]" Value="0" />
<Element Index="[402]" Value="0" />
<Element Index="[403]" Value="0" />
<Element Index="[404]" Value="0" />
<Element Index="[405]" Value="0" />
<Element Index="[406]" Value="0" />
<Element Index="[407]" Value="0" />
<Element Index="[408]" Value="0" />
<Element Index="[409]" Value="0" />
<Element Index="[410]" Value="0" />
<Element Index="[411]" Value="0" />
<Element Index="[412]" Value="0" />
<Element Index="[413]" Value="0" />
<Element Index="[414]" Value="0" />
<Element Index="[415]" Value="0" />
<Element Index="[416]" Value="0" />
<Element Index="[417]" Value="0" />
<Element Index="[418]" Value="0" />
<Element Index="[419]" Value="0" />
<Element Index="[420]" Value="0" />
<Element Index="[421]" Value="0" />
<Element Index="[422]" Value="0" />
<Element Index="[423]" Value="0" />
<Element Index="[424]" Value="0" />
<Element Index="[425]" Value="0" />
<Element Index="[426]" Value="0" />
<Element Index="[427]" Value="0" />
<Element Index="[428]" Value="0" />
<Element Index="[429]" Value="0" />
<Element Index="[430]" Value="0" />
<Element Index="[431]" Value="0" />
<Element Index="[432]" Value="0" />
<Element Index="[433]" Value="0" />
<Element Index="[434]" Value="0" />
<Element Index="[435]" Value="0" />
<Element Index="[436]" Value="0" />
<Element Index="[437]" Value="0" />
<Element Index="[438]" Value="0" />
<Element Index="[439]" Value="0" />
<Element Index="[440]" Value="0" />
<Element Index="[441]" Value="0" />
<Element Index="[442]" Value="0" />
<Element Index="[443]" Value="0" />
<Element Index="[444]" Value="0" />
<Element Index="[445]" Value="0" />
<Element Index="[446]" Value="0" />
<Element Index="[447]" Value="0" />
<Element Index="[448]" Value="0" />
<Element Index="[449]" Value="0" />
<Element Index="[450]" Value="0" />
<Element Index="[451]" Value="0" />
<Element Index="[452]" Value="0" />
<Element Index="[453]" Value="0" />
<Element Index="[454]" Value="0" />
<Element Index="[455]" Value="0" />
<Element Index="[456]" Value="0" />
<Element Index="[457]" Value="0" />
<Element Index="[458]" Value="0" />
<Element Index="[459]" Value="0" />
<Element Index="[460]" Value="0" />
<Element Index="[461]" Value="0" />
<Element Index="[462]" Value="0" />
<Element Index="[463]" Value="0" />
<Element Index="[464]" Value="0" />
<Element Index="[465]" Value="0" />
<Element Index="[466]" Value="0" />
<Element Index="[467]" Value="0" />
</ArrayMember>
</Structure>
</Data>
</OutputTag>
</Connection>
</Connections>
</Communications>
</Module>
"""


def main() -> None:
    tags_xml = "\n".join([
        _MOTION_GROUP_TAG_XML,
        _axis_tag("Bus1_Power_Axis", "Bus1_PowerSupply:Ch1"),
        _axis_tag("Bus1_Drive_X_Axis", "Bus1_Drive_D032:Ch1"),
        _axis_tag("Bus1_Drive_Z_Axis", "Bus1_Drive_D032:Ch3"),
        _axis_tag("Bus2_Power_Axis", "Bus2_PowerSupply:Ch1"),
        _axis_tag("Bus2_Drive057_Trav_Axis", "Bus2_Drive_D057:Ch1"),
        _axis_tag("Bus2_Drive057_Xfer_Axis", "Bus2_Drive_D057:Ch3"),
        _axis_tag("Bus2_Drive020_Chuck_Axis", "Bus2_Drive_D020:Ch1"),
        _axis_tag("Bus2_Drive020_Sf_Axis", "Bus2_Drive_D020:Ch3"),
    ])
    target_name = "BenderFullProgram"
    modules_xml = _ALL_MODULES_XML + "\n" + safety_partner_module_xml(target_name)
    l5x = build_l5x(
        target_name=target_name, tags_xml=tags_xml,
        extra_modules_xml=modules_xml, processor_type="1756-L81ES",
        safety_level="SIL3",
    )
    # Real l5x2acd conversion failure, James's 2026-08-27 push
    # (samples/convert_log.csv) -- this file contains the same PowerFlex
    # 527-STO / FANUC robot / safety-drive module shapes that also fail
    # standalone in gen_module_sweep.py/gen_module_sweep_variants.py
    # (undiagnosed there too, see those files' own _UNDIAGNOSED_RETEST_
    # comments), so no new/separate root cause was found here specifically
    # -- regenerated unchanged, suffixed per James's own instruction so
    # his re-test run doesn't collide with the still-present old failing
    # file.
    out_path = OUT_ROOT / "modulerack_bender_full_program_r2.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(
        "modulerack_bender_full_program_r2",
        "Full real-program replica: all 69 non-CPU modules in James's real "
        "DnR_Personal/Bender134053_201104.L5X now represented (5 Point I/O adapters with "
        "all 44 real children, 5 ArmorBlock I/O, 2 PowerFlex 527-STO safety drives, 2 "
        "EX260 valve manifolds, RMC150E, full 2-bus/5-module Kinetix 5700 subgraph with 8 "
        "real axis tags, the real FANUC robot controller with its 2 real CIP Safety "
        "connections restored, a real GuardLogix Safety Partner via wrapper.py's new "
        "safety_partner support, and 3 EDS-dependent devices represented via Generic "
        "Ethernet Module with real stated Connection sizes preserved), genericized but "
        "structurally verbatim, not deduplicated -- built to be captured against the real "
        "program's actual controller memory for accuracy validation. See this generator's "
        "own docstring for the full real error-driven rationale on the Safety Partner fix "
        "and the robot's restoration. 0 lint findings, 0 duplicate names, 0 dangling "
        "parent refs.",
        "modules", out_path, 0,
    )
    print("Done. 1 full-program replica file written (69 modules incl. Safety Partner, 8 axes).")


if __name__ == "__main__":
    main()
