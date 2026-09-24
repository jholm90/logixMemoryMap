# L5X Memory Analyzer

### WinDirStat for Logix controller memory.

**Point it at an L5X export. See exactly where every byte of your controller's memory
budget is going, and which of it nothing even uses — before a download fails with
"memory full".**

> Developed and validated on **Studio 5000 Logix Designer v35** with a **1756-L81E**
> ControlLogix 5580 as the reference controller. See [Platform support](#platform-support)
> for the others.

![The whole controller at a glance: axes, tags, programs, I/O, AOIs and UDTs, each drawn to scale, with unused items striped](docs/images/overview.png)

Tags, UDTs, Add-On Instructions, Kinetix axes, I/O modules, alarm conditions and compiled
ladder logic, all laid out as one drillable treemap where **area is memory** — and every
tile that nothing in the project uses is striped in amber. In the picture above, a 100-record
recipe backup array nobody reads is 6.6% of the controller, sitting right beside the recipe
library that is actually in use.

---

## Why you want this

Logix Designer tells you how much memory is used. It does not tell you **what** is using
it, or whether anything **needs** it. When a project creeps toward its limit, the usual hunt
is a scroll through thousands of tags, a guess about which UDT got bloated, and a hope that
the next download fits.

The L5X Memory Analyzer replaces the hunt with a picture:

- 🔍 **Find the hog in seconds.** The biggest thing on screen is the biggest thing in
  memory. A forgotten 1,000-element array, a UDT someone padded with STRINGs, a routine
  that grew for ten years — they stand out immediately.
- 🧹 **See what nothing uses.** Every tag, array element, UDT member, routine and module
  carries a usage count. Anything never referenced is flagged in the list and striped in
  the treemap: the memory you can get back.
- 🧭 **Drill from the whole controller down to a single REAL.** Controller → task →
  program → routine → rung, or tag → array element → member → the byte.
- ⚙️ **See motion and I/O for what they cost.** Every Kinetix axis, drive, bus supply,
  VFD and Ethernet device is its own tile, sized.
- 📏 **Plan before you buy.** See how full a 1756-L81E would be before you order one, or
  how much headroom a migration leaves.
- 🧾 **Export the evidence.** Every number goes to CSV or XLSX for the design review.
- 🔌 **Works offline.** A single Python process and a browser tab. No cloud, no licence
  server, no Studio 5000 install required. Built for air-gapped OT workstations.

---

## The tour

### 1. The budget bar — your controller's fuel gauge

![Header zoomed: file name, firmware, catalog and the memory budget bar](docs/images/zoom_header.png)

The moment a file opens, the header shows the controller catalog, the firmware, and a
budget bar for **that catalog's real capacity**. Here: 339.9 KB of a 1756-L81E's 3.00 MB,
11.06%, counted in the same blocks Studio 5000's Capacity tab uses.

### 2. Find what nothing uses

Every row in the **List** carries a **Uses** count: how many times that tag, member,
routine or module is referenced by the project's logic, aliases, alarms, axes and modules.
Anything referenced nowhere gets an amber **UNUSED** pill and a highlighted row. Sort by
**Uses** and the dead weight comes straight to the top:

![Controller tags sorted by Uses: an old recipe backup array, an edit buffer, a spare trend buffer, spare sensors and test bits flagged UNUSED](docs/images/list_unused.png)

In the treemap the same things are **striped in amber**, and the stripes take priority over
every other marking, so dead memory is the first thing your eye finds:

![Controller Tags opened: the unused recipe backup and trend buffer striped beside the recipe library in use](docs/images/drill_tags.png)

Hover any striped tile and it says so, and why:

| | |
|:---:|:---:|
| ![Old_Recipe_Backup: 22.4 KB, not used anywhere in this project, 6.58% of the controller](docs/images/tip_unused_tag.png) | ![Bus converter axis: not used anywhere in this project](docs/images/tip_unused_axis.png) |
| **A 22 KB array nothing reads** — 6.6% of the controller. | **An axis no motion instruction commands.** |

It works on routines too. A routine that is not the main routine and that no JSR calls is
flagged, so logic nobody runs any more is easy to find:

![Routines of ST080_Unload: Retired_Homing flagged UNUSED, the others show their JSR calls](docs/images/list_routines.png)

![Retired_Homing tooltip: not the main routine, and no JSR calls it](docs/images/tip_unused_routine.png)

The count is honest about its edges: a tag read over the network by an HMI or SCADA system
is invisible in an L5X, and the tooltip says so rather than calling the memory deletable. A
member used only because its whole structure is copied is reported as "via parent", an
indexed array (`Recipe[Idx]`) counts as a use of every element, and an AOI's parameters
count as used when the AOI's own logic reads them.

### 3. User-defined types, member by member

Open **User-Defined Data Types** to see every UDT as a tile, split into what the definition
costs to exist — its base, its member-name pool, its BOOL packing — and each member. The
members nothing ever names are striped:

![All three UDTs opened: spare and legacy members striped in each](docs/images/drill_udts.png)

Open one and the List ranks its members by how often the project uses them. Here the
station status structure: two spare members never touched, `StepNo` read or written 94 times:

![Station_t members sorted by Uses: SpareFlag and SpareWord UNUSED, StepNo used 94 times](docs/images/list_udt_station.png)

The recipe structure has two legacy fields that survive in every one of its 302 records
across four tags, and nothing reads them:

![Recipe_t opened: definition overhead and members, the two legacy fields striped](docs/images/udt_recipe.png)

| | |
|:---:|:---:|
| ![Recipe_t members: LegacyOffsets and LegacyEnable UNUSED](docs/images/list_udt_recipe.png) | ![LegacyOffsets tooltip: not used anywhere, only ever copied along with its whole structure](docs/images/tip_udt_member_unused.png) |

The **UDT Size** switch shows either what the type costs to exist (definition) or what one
instance of it occupies (instance).

### 4. Hover anything, at any depth

Every tile answers three questions: **what is it, how big is it, and what share is it** —
of the level you are looking at *and* of the whole controller. The two bars tell different
stories the deeper you go:

| | |
|:---:|:---:|
| ![RecipeLibrary: 44.6 KB, 49.3% of Controller Tags, 13.1% of the controller](docs/images/tip_recipe.png) | ![A servo axis: AXIS_CIP_DRIVE, its share of Axis Definitions and of the controller](docs/images/tip_axis.png) |
| **The recipe library.** Half of all controller tags, an eighth of the controller. | **A servo axis.** Axes are not free. |
| ![A Kinetix drive module: 2198-D032-ERS3 and its share of I/O Modules](docs/images/tip_drive.png) | ![A rung: its full ladder text, 68 B, its share of its routine](docs/images/tip_rung.png) |
| **A Kinetix 5700 drive.** Catalog number, size, share of the I/O tree. | **A single rung,** with its ladder text and its estimated compiled size. |
| ![A UDT member: PathSetpoints, REAL[32], 128 B, its share of its record](docs/images/tip_member.png) | ![Free space: its share of controller capacity](docs/images/tip_free.png) |
| **One member of one record** — and its share of the record. | **The room you have left,** as a share of the controller's capacity. |

### 5. Drill in. Then keep drilling.

Click any tile to open it. The breadcrumb always shows where you are, and **Back** takes you
where you came from.

![Breadcrumb zoomed: All › Controller Tags › RecipeLibrary › [0]](docs/images/zoom_breadcrumb.png)

**Into one record of an array.** Here is `RecipeLibrary[0]`, member by member: a `REAL[32]`
of path setpoints, a `REAL[16]` of legacy offsets, the scalar fields, and even the
**hidden SINT that Logix packs the UDT's BOOLs into**, laid out the way the controller
lays them out.

![One UDT array element, member by member, including the hidden BOOL-packing SINT](docs/images/drill_record.png)

### 6. Motion and I/O, priced module by module

Open **I/O Modules** and every device on the network has its own tile: a Kinetix 5700 bus
supply, three dual-axis drives, a PowerFlex 525 infeed conveyor and a vision gateway — each
with the number of places the project uses it.

![I/O Modules opened: PowerFlex 525, Kinetix drives and supply, vision gateway](docs/images/drill_modules.png)

![I/O module list: every device with its catalog number, bytes, uses and share](docs/images/list_modules.png)

The servo axes and the bus converter axis live under **Axis Definitions**, where each
`AXIS_CIP_DRIVE` shows what it really costs:

![Axis Definitions opened: six servo axes and the converter axis](docs/images/drill_axes.png)

### 7. An AOI's definition vs. its instances

An Add-On Instruction costs memory in **two places**, and the tool shows both.

The **definition** is paid once, however many instances you create: its base overhead,
its parameter and local-tag table, and its compiled internal logic.

| | |
|:---:|:---:|
| ![Cylinder2Pos definition opened: overhead, the Logic routine and the parameter table](docs/images/aoi_definition.png) | ![Instance ST030_ClampA opened: its parameter and local-tag data](docs/images/aoi_instance.png) |
| **Definition** `Cylinder2Pos`, paid once. | **Instance** `ST030_ClampA`, paid for every cylinder. |
| ![Tooltip on the Cylinder2Pos definition](docs/images/tip_aoi_definition.png) | ![Tooltip on instance ST030_ClampA](docs/images/tip_aoi_instance.png) |

**Cross-Reference** lists every instance of the AOI, and every path is a link straight to
it in the treemap:

![Cross-reference for Cylinder2Pos: every instance, each a link](docs/images/xref_aoi.png)

### 8. Ladder logic, priced rung by rung

Open a program, then a routine, and every rung becomes a tile labelled with its
instructions and its estimated compiled size.

![A routine opened: every rung as a tile with its instructions and bytes](docs/images/drill_routine.png)

Zoom in and you can read it. The fat rungs are the ones worth rewriting:

![Rung tiles zoomed: each rung's instructions and bytes](docs/images/zoom_rungs.png)

![List of rungs in a routine, sorted by bytes](docs/images/list_rungs.png)

> **Honest by design.** Compiled logic size is an *estimate*: Rockwell does not publish how
> rungs compile. Every logic tile carries a **dashed outline** that means "estimated".
> Tag, UDT and AOI data space is *calculated*, and carries no such mark. (An unused tile's
> amber stripes replace the outline: that it is unused is the more important thing to know.)

### 9. Side by side, and by kind

**⊞ Details** docks the List beside the treemap and follows every drill-down, and
**Type Summary** rolls the level up by kind:

![Treemap with the details list docked alongside](docs/images/details_dock.png)

![Type summary: share of the controller by kind](docs/images/type_summary.png)

### 10. See the whole tree at once

Turn **Depth** up and the treemap nests as many levels as you ask for. Programs open into
routines, arrays into their elements and AOI instances into their members, all in one view.

![Depth 4: programs into routines, arrays into elements, all at once](docs/images/depth4.png)

### 11. How much room is left?

Tick **Show Empty Space** and the controller's free memory becomes a neutral grey tile beside
everything the project uses. It is the fastest way to explain headroom to someone who does
not read hex.

![Free space as a grey tile beside everything that is used](docs/images/empty_space.png)

### 12. A tool that tells you what it doesn't know

Most estimators give you one confident number. This one tells you **how much of that number
to trust**.

![File confidence card zoomed, split into Exact, Measured, Approximate and Unverified](docs/images/zoom_confidence.png)

The **File confidence** card splits the prediction by evidence: **Exact** (calculated from
known sizes), **Measured** (fitted and checked against real controller readings),
**Approximate** and **Unverified**. Anything the model cannot price is listed by name and
never silently counted as zero. This demo prices everything:

![Errors tab: 0 errors, nothing went unpriced in this file](docs/images/errors.png)

Source-protected routines and AOIs get the same honesty. The tool prices what it can see
(the interface, the instances, the calls) and raises a red **MINIMUM** banner, because
nobody can see inside the encryption.

Add `?ConfidenceMode=true` to the address and the whole treemap is recoloured by confidence
band, so the estimated parts of a project are visible at a glance.

![Confidence mode: every tile coloured by how well its size is known](docs/images/confidence_mode.png)

---

## How accurate is it?

Measured against **eighteen real production programs** (1756-L8x and CompactLogix 5380,
standard processors), each compared with the memory figure Studio 5000 reports for the
real compiled project:

| | |
|---|---|
| **Mean absolute error** | **0.77%** |
| **Worst case** | **3.87%** (a program carrying 39 source-protected routines the tool cannot see inside) |
| **Blind test** | a 7.89 MB program predicted at **+2.15%** before its real figure was used for anything |

**Read the worst case as "up to about 5%" on a file the tool has never seen.** The blind
test is the number that matters most: it is the only one no tuning could have touched.

Why the tool can be this close:

- **Tag, UDT and AOI data space is calculated exactly.** Atomic sizes, alignment, BOOL
  packing into hidden SINTs, string lengths and nested arrays are known rules, verified
  against real controller readings.
- **Compiled logic is fitted, instruction by instruction.** Each instruction's weight,
  including its operand types, its indirect addressing, JSR parameters and CPT expression
  structure, is measured on purpose-built test projects compiled in Studio 5000 and read
  back from the Capacity tab. **Over 3,000 captured test projects** sit behind the model.
- **It is checked against real programs, not just its own test files.** The generated
  corpus is the measuring instrument. The real programs are the scoreboard.

The full method, every constant, and every open question are published in
[`docs/`](docs/).

---

## Get started in one minute

```bash
git clone https://github.com/jholm90/logixMemoryMap.git
cd logixMemoryMap
pip install -e .
l5x-memory-analyzer ui
```

Your browser opens at `http://127.0.0.1:8765` with a **File Open** button — pick an L5X
exported from Logix Designer with **File › Save As › L5X**. That makes a good desktop
shortcut: no command prompt, no path to type.

Optionally, name the file to open it straight away:

```bash
l5x-memory-analyzer ui path/to/YourProject.L5X
```

Options: `--host` (default `127.0.0.1`), `--port` (default `8765`), `--no-browser`.

### Prefer the command line?

```bash
l5x-memory-analyzer size   YourProject.L5X            # flat byte breakdown
l5x-memory-analyzer export YourProject.L5X out.xlsx   # CSV or XLSX report
l5x-memory-analyzer dump   YourProject.L5X            # raw parsed XML
```

Without installing, run the same subcommands from `src/` as
`python -m l5x_memory_analyzer.cli <subcommand> ...`.

---

## What it understands

| content | how it is sized |
|---|---|
| Controller and program tags, all atomic types | exact |
| UDTs, nested UDTs, arrays of UDTs, BOOL packing | exact |
| STRING and custom string types | exact |
| Add-On Instruction definitions, instances, parameters, internal logic | calculated + fitted |
| Ladder logic: 100+ instructions, operand types, indirect addressing, branches | fitted, flagged estimated |
| JSR / SBR / RET with and without parameters | fitted, flagged estimated |
| CPT / CMP expressions, by operator structure | fitted, flagged estimated |
| Structured Text | fitted, flagged estimated |
| Tasks, programs, routines | measured |
| I/O modules: 1756, 5069, POINT I/O, Kinetix 5700 drives and supplies, generic Ethernet | measured per family, with a fallback for unseen catalogs |
| Axes and motion groups | measured |
| Tag-based alarm conditions | measured |
| Usage of every tag, member, element, routine, module and type member | counted from logic, aliases, alarms, axes and modules |
| Source-protected routines and AOIs | priced at a flagged **minimum** |

## Platform support

| platform | status |
|---|---|
| **1756-L8x ControlLogix** | ✅ supported, well represented in the real validation set |
| **5069 / CompactLogix 5380** | ✅ supported, represented in the real validation set |
| GuardLogix safety controllers | sized, but safety memory is a separate partition, so accuracy is quoted for standard processors only |
| 1756-L7x, 1769 | older architecture: existing support kept, no new development |
| 1756-L9x ControlLogix 5590 | 96-file side-by-side batch (L81E v35 / L81E v38 / L908TS v38) built, awaiting capture; not yet validated — see [FUTURE_TESTS.md](docs/FUTURE_TESTS.md#l9-controllogix-5590-what-it-takes) |

---

## The screenshots

Every picture above comes from a **synthetic demo project**, not a customer file: an
eight-station bead-dispense line (ST010 Load through ST080 Unload), each station a program
with sequence, cylinder, fault and statistics routines; part-present and cylinder position
sensors; a two-position cylinder AOI; a recipe library and shift production data; a Kinetix
5700 bus with six servo axes; a PowerFlex 525 infeed conveyor and a vision gateway. About
nine tenths of what it declares is used by its logic, and the rest is the kind of thing real
projects accumulate — an old recipe backup, a spare trend buffer, spare sensor inputs, legacy
recipe fields, a retired routine. Every module and axis in it is built from blocks that
compiled with zero errors in Studio 5000, and it opens with **zero unpriced items** — the
build script refuses to write it otherwise. Rebuild it and explore it yourself:

```bash
python scripts/build_demo_project.py
l5x-memory-analyzer ui docs/demo/DemoLine.L5X
```

---

## Documentation

| file | contents |
|---|---|
| [FINAL_REPORT.md](docs/FINAL_REPORT.md) | **start here**: results, wins, losses, what is open, how to get more accuracy |
| [MEMORY_MODEL.md](docs/MEMORY_MODEL.md) | every sizing constant, formula and packing rule |
| [OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) | unresolved sizing and behaviour questions |
| [RESOLVED_QUESTIONS.md](docs/RESOLVED_QUESTIONS.md) | closed questions and why |
| [TASKS.md](docs/TASKS.md) | the ranked work queue |
| [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) | phases and their exit criteria |
| [ROADMAP.md](docs/ROADMAP.md) | where the tool stands and what is next |
| [INSTRUCTION_COVERAGE.md](docs/INSTRUCTION_COVERAGE.md) | per-instruction weight status against real usage |
| [AOI_KNOWLEDGE_MAP.md](docs/AOI_KNOWLEDGE_MAP.md) | what is known and unknown about AOI sizing |
| [TESTING_PLAN.md](docs/TESTING_PLAN.md) | how predictions are validated against real controllers |
| [SAMPLE_GENERATION.md](docs/SAMPLE_GENERATION.md) | how test files are built, and every batch |
| [COMMANDS.md](docs/COMMANDS.md) | every script and CLI command |
| [IO_MODULES.md](docs/IO_MODULES.md) | module and I/O sizing reference |
| [CMP_CPT_REFERENCE.md](docs/CMP_CPT_REFERENCE.md) | expression instruction reference |
| [OPEN_BUILD_ERRORS.md](docs/OPEN_BUILD_ERRORS.md) | sample files that will not build |
| `CLAUDE.md` | working context and the rules that govern changes |

## Licence

Apache-2.0. Python end to end.

`tools/ra-logix-designer-vcs-custom-tools/` is Rockwell Automation's `l5xgit` source,
vendored under its own MIT licence for the capture pipeline's L5X→ACD conversion; see
[tools/README.md](tools/README.md).

*Logix, Studio 5000, ControlLogix, CompactLogix, GuardLogix, POINT I/O and Kinetix are
trademarks of Rockwell Automation, Inc. This project is independent and is not affiliated
with or endorsed by Rockwell Automation.*
