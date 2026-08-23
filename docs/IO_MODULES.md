# I/O Module Inventory

Source: every real file in `samples/local/` (54 files, including the new
`DnR_Personal/` batch), scanned for distinct `<Module CatalogNumber=...>`
values. 120 distinct catalog numbers found. This is Phase 3's deferred
`Controller/Modules` parsing (James, 2026-08-20: "leave the module stuff
to later"), now picked back up — **2026-08-22: high priority, testing
starts next.**

Scope for this pass, per James: **Ethernet and local (in-rack) modules
only.** ControlNet and DeviceNet are explicitly skipped for now — see
bottom of this doc, added to the features backlog.

## Topology note (matters for connection/RPI sizing, not just tag size)

`ParentModule`/`ParentModPortId` in the L5X encode the real physical
hierarchy, confirmed across the corpus:

- **`ParentModule="Local"`** = directly in the controller's own chassis
  (1756 backplane) or directly on the controller's own Ethernet/local bus
  (5069 Compact 5000 I/O snaps on with no separate adapter needed).
- **An Ethernet bridge/adapter module's own `Name`** becomes the
  `ParentModule` value for everything downstream of it — e.g.
  `1756-EN2T` named `Sorter2_EN2T` in one rack makes every module in a
  *second, remote* 1756 rack list `ParentModule="Sorter2_EN2T"`. Same
  pattern for `1734-AENT`/`1734-AENTR` (Point I/O) and `1794-AENT` (FLEX
  I/O) heading a distributed I/O bank — this is exactly the "1756 modules
  go in 1756 racks and need an Ethernet card... to access them" case James
  flagged. Sizing needs to walk this chain, not assume everything is one
  flat local rack.

## A. Controllers (chassis root, `ParentModule="Local"`)

| Catalog | Family | Real file count |
|---|---|---|
| 1756-L55, L61, L71, L72, L75, L81E, L81ES, L82E, L83E, L84ES | ControlLogix 5580/5570/5560 | 1756-L81E×8, L83E×7, L82E×4, L81ES×3, others×1 |
| 1756-L8SP | ControlLogix safety partner | 1 |
| 5069-L306ERS2, L310ERS2, L320ERMS2, L320ERMS3, L330ERMS2, L340ERS2 | CompactLogix 5380 | 1 each |
| 1769-L33ERMS | CompactLogix 5370 | 1 |

## B. 1756 local backplane I/O (`ParentModule="Local"`, same rack as controller)

| Catalog | Type | Real file count |
|---|---|---|
| 1756-IA16, IA32/A, IB16, IB16IF/A, IB32/B, OA16, OA16I, OB16E, OB32, OW16I | Digital I/O | 1-3 each |
| 1756-IF8/A, OF4/A | Analog I/O | 1-3 each |
| 1756-HSC/A, HSC/B | High-speed counter | 1 each |
| 1756-HYD02 | Hydraulic axis | 1 |

## C. Ethernet bridge/adapter modules (create a REMOTE 1756 rack)

| Catalog | Real file count | Note |
|---|---|---|
| 1756-EN2T | 4 | Most common remote-rack head in the corpus |
| 1756-EN4TR | 2 | |
| 1756-ENBT/A | 2 | Older-generation equivalent |

## D. 1734 Point I/O (Ethernet-adapter-headed distributed I/O)

| Catalog | Role | Real file count |
|---|---|---|
| 1734-AENT/B, /C, AENTR/B, /C | Ethernet adapter head | 3-4 each |
| 1734-IB8/C, IB8S/B, IE2C/C, IE4C/C, IJ/C, IR2/C, OB2EP/C, OB8/C, OB8E/C, OB8S/A, OB8S/B, OE2C/C | I/O modules on the bank | 1-5 each |

## E. 1794 FLEX I/O (Ethernet variant only — `1794-AENT`)

| Catalog | Role | Real file count |
|---|---|---|
| 1794-AENT | Ethernet adapter head | 1 |
| 1794-IA16/A, IB16/A, IB16XOB16P/A, IB32/A, IR8/A, OA8/A, OE4/B, OW8/A, VHSC/A | I/O modules on the bank | 1-2 each |

## F. 5069 Compact 5000 I/O (snaps directly onto controller's local bus)

| Catalog | Real file count |
|---|---|
| 5069-IB16/A, IB8S/A, OB16/A, OB16/B, OBV8S/A | 1-2 each |

## G. Ethernet drives, motion, and other networked devices

| Catalog | Device | Real file count |
|---|---|---|
| 2198-C4004-ERS, D012/D020/D032/D057-ERS3, H008-ERS, P031/P070/P141/P208, RP200, S086/S130-ERS3 | Kinetix 5700 servo drive family (incl. power supplies, safety) | 1-13 each — **D020-ERS3 (13) and D032-ERS3/D057-ERS3/P208 (12 each) are the most common single catalog numbers in the whole corpus** |
| PowerFlex 525-EENET, 527-STO CIP Safety, 755-EENET, 755-EENET-CM, 755-EENET-CM-S | VFDs, embedded Ethernet | 1-5 each |
| 2097-V34PR5-LM | Kinetix 350 single-axis servo | 1 |
| 193-ECM-ETR/A, /B | E300 electronic overload relay | 1-2 |
| 150 SMC Flex-E | Soft starter | 2 |
| 842E-CM-M | Ethernet absolute encoder | 1 |
| 843E-MIPxxBAx/A | Ethernet incremental encoder interface | 1 |
| 440C-CR30-22BBB/A, 442G-MABLB-UR-E0JP4679/A | Safety relay (GuardMaster-class) | 1-4 |
| EX260-SEN1/A, SEN3/A | SMC EX260 Ethernet valve manifold | 1-3 |
| FANUC Robot R30iB Plus/A | Robot controller | 1 |
| CIP-MODULE | Generic explicit-message-only CIP device | 3 |
| ETHERNET-BRIDGE, ETHERNET-MODULE, ETHERNET-PANELVIEW, Generic-Ethernet-Device, Generic-1756-Device | Generic/placeholder Ethernet node (incl. PanelView Ethernet HMI) | 1-19 — **ETHERNET-MODULE (19) is the single most common entry in the corpus, unsurprisingly** |
| *(no CatalogNumber, ProductType-only)* | Named third-party Ethernet devices — RFID readers, encoders, RMC motion controllers, Modbus bridges, etc. | ~9 files each with 1+ |

## Skipped for now — added to the features backlog

James, 2026-08-22: skip ControlNet/DeviceNet for now, add to the features
list.

- **1756-CNB/D** — ControlNet bridge
- **1756-DNB** — DeviceNet bridge
- **1794-ACN15/C** — FLEX I/O ControlNet adapter (vs. the in-scope
  1794-AENT Ethernet adapter)
- **1785-PLC5C** — PLC-5 over ControlNet
- **1756-DHRIO/E** — Data Highway+/Remote I/O bridge (legacy, neither
  Ethernet nor ControlNet/DeviceNet, but same "later" bucket)
- **1771-ASB, 1746-NO8I** — legacy Universal Remote I/O / SLC 500 gear
  reached through the above bridges

## Module data-size patterns (confirmed 2026-08-22 — read before building
## any more module tests)

James: "we can have Io modules from some vendors that have different
sizing based on the internal config setup — I can have the same catalog
Phoenix rack with 2 input card or 30 input cards, you need to be careful
looking at the data sizes in the l5x module properties." Confirmed exactly
right, and there isn't just one pattern — four real, structurally distinct
ways a module's data size shows up in the L5X, found across the corpus so
far:

1. **Catalog-fixed backplane module** (1756-IB16): its own
   `<Connection><InputTag>` with a real AOP-defined `Structure` — size is
   fully determined by `CatalogNumber`, identical every time.
2. **Point I/O rack member** behind a `1734-AENT`/`AENTR` adapter: **no
   independent connection at all** — `<RackConnection><InAliasTag/></
   RackConnection>`. Its data is rolled into the adapter's own combined
   rack-image connection instead. Sizing has to walk adapter+members
   together, never module-by-module.
3. **Generic/no-EDS Ethernet module** (`CatalogNumber="ETHERNET-MODULE"`
   — real corpus examples are Balluff/IFM IO-Link masters and Phoenix bus
   couplers): size is **not catalog-derived at all** — it's the explicit
   `PrimCxnInputSize`/`PrimCxnOutputSize` attributes on `<Communications>`,
   chosen per-instance in Studio 5000 when the module was added. This is
   James's exact caution, confirmed: `IFM_LugLoader1` in
   `Emporium_2025_05_28r01.L5X` is 450 input / 8 output bytes, and nothing
   about the catalog number says so — the `Structure` `DataType` name even
   encodes the byte count directly (`AB:ETHERNET_MODULE_SINT_450Bytes:I:0`).
4. **5069 Compact I/O** (`5069-IB16/A`): a fourth convention — explicit
   `InputSize`/`OutputSize` attributes directly on `<Connection>` itself
   (not on `<Communications>`), plus a deeper per-channel `StructureMember`
   nesting style than 1756's flat member list.

**Takeaway for the eventual sizing engine:** module size can never be a
flat catalog-number lookup table alone. It needs per-instance parsing of
whichever of these four conventions applies, and pattern 2 needs
rack-level (not module-level) grouping.

## First batch — built 2026-08-22, `gen_io_modules.py`

7 files in `samples/generated/modules/`, real-shape (see `builders.py`'s
`module_1756_digital_input_xml`/`module_generic_ethernet_xml`):

- **1756 local** (pattern 1): 1/3/10 `1756-IB16` backplane modules —
  captured clean, real data in `manifest.csv`.
- **Generic Ethernet / config-variance** (pattern 3) — the direct test of
  James's caution: 4 files, all `CatalogNumber="ETHERNET-MODULE"`, at
  input/output byte sizes 2/2, 8/8, 32/16, 450/8 (the real IFM value) —
  captured clean. Real Capacity does move differently across these,
  confirming "config drives size, not catalog."

**2026-08-23, James: "purge the old shit... new stuff only."** Dropped
from this batch entirely, never once converted successfully across
several days of retries (`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` on every
`l5xgit` attempt, no schema-level detail available to diagnose from here):
- **Point I/O** (pattern 2): `1734-AENT` adapter + 2/8 `1734-IB8` blocks —
  `module_point_io_xml` removed from `builders.py`.
- **5069 local** (pattern 4): 1/3 `5069-IB16/A` modules — `module_
  5069_digital_input_xml` removed from `builders.py`.
- The 1000/1000 generic-Ethernet config-variance point.

Best guess, unconfirmed: these reference module-specific predefined
DataTypes (`AB:1734_DI8:C:0`, `AB:5000_DI16:C:0`, etc.) that only resolve
if the exact module's EDS/AOP is registered in the target Designer
install's catalog — which the XML shape being "real" (corpus-derived)
doesn't guarantee on a machine that's never added that specific catalog
entry. James is rebuilding these himself from a live Studio 5000 project
rather than iterating blind on this theory. The real corpus catalog
inventory above (sections A-D) stays accurate regardless — this is about
generating fresh, importable L5X, not about what real fleets use.

Drives (2198-*/PowerFlex) intentionally skipped this round per James.

## Next step

Once this batch comes back: pick the next representative modules — likely
1756-EN2T (most common remote-rack bridge) next, since B/C/D/E/F/G in the
inventory above still need their own real shape confirmed one at a time,
same discipline as this batch.
