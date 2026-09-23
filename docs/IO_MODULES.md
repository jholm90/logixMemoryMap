# I/O Modules

The module catalogue found in the real production corpus, the topology rules that
govern how modules are reached, and the four structurally distinct ways a module
declares its data size.

Sizing constants live in `MEMORY_MODEL.md`. This file is the reference for what
real fleets actually contain.

**In scope:** Ethernet and local in-rack modules. ControlNet and DeviceNet are
not supported.

---

## The one rule that matters most

**Module size can never be a flat catalog-number lookup.** Several catalogs are
configurable — the same catalog can hold 2 input cards or 30, and generic Ethernet
profiles have their sizes typed in by hand — so **two instances of the same
catalog number are different devices.**

The catalog number selects the per-module *overhead*. The file states the *size*.
Read it.

---

## Topology

`ParentModule` and `ParentModPortId` encode the real physical hierarchy.
**Sizing must walk this chain rather than assuming one flat local rack.**

- **`ParentModule="Local"`** — directly in the controller's own chassis (1756
  backplane) or on the controller's own local bus (5069 Compact 5000 I/O, which
  snaps on with no separate adapter).
- **An Ethernet bridge or adapter module's own `Name` becomes the `ParentModule`
  value for everything downstream of it.** A `1756-EN2T` named `Sorter2_EN2T`
  makes every module in a second, remote 1756 rack list
  `ParentModule="Sorter2_EN2T"`. The same pattern applies to `1734-AENT` /
  `1734-AENTR` heading a POINT I/O bank and `1794-AENT` heading a FLEX I/O bank.

This is the "1756 modules go in 1756 racks and need an Ethernet card to reach
them" case, stated in the file.

---

## The four data-size conventions

Four real, structurally distinct ways a module's data size appears. Each needs its
own parsing path.

### 1. Catalog-fixed backplane module

Example: `1756-IB16`. Its own `<Connection><InputTag>` with an AOP-defined
`Structure`. Size is fully determined by the catalog number and identical every
time. This is the only pattern where a lookup would work.

### 2. POINT I/O rack member

Example: a `1734-IB8` behind a `1734-AENT` adapter. **No independent connection at
all** — `<RackConnection><InAliasTag/></RackConnection>`. Its data is rolled into
the adapter's own combined rack-image connection.

**Sizing has to walk adapter and members together, never module by module.**

### 3. Generic Ethernet module with no EDS

`CatalogNumber="ETHERNET-MODULE"`. Real examples are IO-Link masters and bus
couplers. **Size is not catalog-derived at all** — it is the explicit
`PrimCxnInputSize` and `PrimCxnOutputSize` attributes on `<Communications>`,
chosen per instance when the module was added.

One real instance is 450 input and 8 output bytes, and nothing about the catalog
number says so. The `Structure` `DataType` name encodes the byte count directly:
`AB:ETHERNET_MODULE_SINT_450Bytes:I:0`.

This is the single most common entry in the corpus, and the reason a per-catalog
constant was never the right shape for it. Real instances carry on the order of 40
distinct connection shapes with input spanning 2 to 450 bytes.

### 4. 5069 Compact I/O

Example: `5069-IB16/A`. Explicit `InputSize` and `OutputSize` attributes directly
on `<Connection>` itself — **not** on `<Communications>` — plus a deeper
per-channel `StructureMember` nesting than 1756's flat member list.

---

## `CommMethod` must agree with the connection's element type

Across 183 real `ETHERNET-MODULE` instances, with no counter-example:

| CommMethod | element type |
|---|---|
| 536870915 | INT |
| 536870916 | SINT |
| 536870914 | REAL |
| 536870913 | DINT |
| 536870932 | no connection at all |

Getting this wrong invalidated two arms of the batch that derived the connection
cost law. A generated module whose `CommMethod` disagrees with its declared
element type is a silently wrong file, not a build failure.

---

## Catalogue found in the real corpus

120 distinct catalog numbers. Counts are files containing at least one.

### Controllers

| Catalog | Family |
|---|---|
| 1756-L55, L61, L71, L72, L75, L81E, L81ES, L82E, L83E, L84ES | ControlLogix 5560 / 5570 / 5580 |
| 1756-L8SP | ControlLogix safety partner |
| 5069-L306ERS2, L310ERS2, L320ERMS2, L320ERMS3, L330ERMS2, L340ERS2 | CompactLogix 5380 |
| 1769-L33ERMS | CompactLogix 5370 |

1756-L81E and L83E are the most common.

### 1756 local backplane I/O

| Catalog | Type |
|---|---|
| 1756-IA16, IA32/A, IB16, IB16IF/A, IB32/B, OA16, OA16I, OB16E, OB32, OW16I | Digital |
| 1756-IF8/A, OF4/A | Analog |
| 1756-HSC/A, HSC/B | High-speed counter |
| 1756-HYD02 | Hydraulic axis |

### Ethernet bridges — these create a remote 1756 rack

| Catalog | Note |
|---|---|
| 1756-EN2T | Most common remote-rack head |
| 1756-EN4TR | |
| 1756-ENBT/A | Older-generation equivalent |

### 1734 POINT I/O — behind an Ethernet adapter head

| Catalog | Role |
|---|---|
| 1734-AENT/B, /C, AENTR/B, /C | Adapter head |
| 1734-IB8/C, IB8S/B, IE2C/C, IE4C/C, IJ/C, IR2/C, OB2EP/C, OB8/C, OB8E/C, OB8S/A, OB8S/B, OE2C/C | I/O on the bank |

### 1794 FLEX I/O — Ethernet variant only

| Catalog | Role |
|---|---|
| 1794-AENT | Adapter head |
| 1794-IA16/A, IB16/A, IB16XOB16P/A, IB32/A, IR8/A, OA8/A, OE4/B, OW8/A, VHSC/A | I/O on the bank |

### 5069 Compact 5000 I/O

`5069-IB16/A`, `IB8S/A`, `OB16/A`, `OB16/B`, `OBV8S/A`.

### Networked drives, motion and devices

| Catalog | Device |
|---|---|
| 2198-C4004-ERS, D012/D020/D032/D057-ERS3, H008-ERS, P031/P070/P141/P208, RP200, S086/S130-ERS3 | Kinetix 5700 servo family, including supplies and safety variants |
| PowerFlex 525-EENET, 527-STO, 755-EENET, 755-EENET-CM, 755-EENET-CM-S | VFDs with embedded Ethernet |
| 2097-V34PR5-LM | Kinetix 350 single-axis servo |
| 193-ECM-ETR/A, /B | E300 electronic overload relay |
| 150 SMC Flex-E | Soft starter |
| 842E-CM-M | Ethernet absolute encoder |
| 843E-MIPxxBAx/A | Ethernet incremental encoder interface |
| 440C-CR30-22BBB/A, 442G-MABLB-UR-E0JP4679/A | Safety relays |
| EX260-SEN1/A, SEN3/A | Ethernet valve manifold |
| FANUC Robot R30iB Plus/A | Robot controller |
| CIP-MODULE | Generic explicit-message-only CIP device |
| ETHERNET-BRIDGE, ETHERNET-MODULE, ETHERNET-PANELVIEW, Generic-Ethernet-Device, Generic-1756-Device | Generic and placeholder Ethernet nodes |
| *(no CatalogNumber, ProductType only)* | Named third-party devices — RFID readers, encoders, motion controllers, Modbus bridges |

**`ETHERNET-MODULE` is the most common single entry in the corpus.** The
`2198-D020-ERS3`, `D032-ERS3`, `D057-ERS3` and `P208` drives are the most common
named catalogs.

### Not supported

| Catalog | Network |
|---|---|
| 1756-CNB/D | ControlNet bridge |
| 1794-ACN15/C | FLEX I/O ControlNet adapter |
| 1785-PLC5C | PLC-5 over ControlNet |
| 1756-DNB | DeviceNet bridge |
| 1756-DHRIO/E | Data Highway+ / Remote I/O bridge |
| 1771-ASB, 1746-NO8I | Legacy Universal Remote I/O and SLC 500 gear behind the above |

---

## Generating module test files

**Module-specific predefined DataTypes only resolve if that module's EDS or AOP is
registered in the target Designer install's catalogue.** Types like
`AB:1734_DI8:C:0` and `AB:5000_DI16:C:0` caused repeated import aborts with no
schema-level detail available to diagnose from.

**A corpus-derived XML shape being real does not guarantee it imports on a machine
that has never added that catalog entry.** POINT I/O and 5069 local module
generators were dropped for this reason and must be rebuilt from a live Studio
project rather than iterated on blind.

The catalogue above stays accurate regardless — it describes what real fleets use,
not what can be generated.
