"""Whole-controller export, or a partial one? And which parts are real?

James, 2026-09-04: "Can you please rewrite the estimation script for
handling controller, udt, aoi, programs, routines, rungs logic exports...
Anything that's not a controller export can not use the prices sir base
load, but rungs, routines and programs might contain controller tags."

Studio 5000 exports at six granularities, and until this module every one of
them was sized as though it were a whole project. That is not a rounding
error. A single exported RUNG came back at 15,080 bytes, of which 13,296 was
`empty_project_baseline` -- a controller's fixed scaffolding cost, charged
to a rung. The same 13,296 was being added to every AOI, routine, program
and UDT export too.

HOW A PARTIAL EXPORT IS SHAPED
------------------------------
The root element states it directly (real values, read off the files in
samples/local/Template/):

    TargetType="Controller"                  ContainsContext="false"
    TargetType="Program"                     ContainsContext="true"
    TargetType="Routine" TargetSubType="RLL" ContainsContext="true"
    TargetType="Rung"    TargetCount="6"     ContainsContext="true"
    TargetType="AddOnInstructionDefinition"  ContainsContext="true"
    TargetType="DataType"                    ContainsContext="true"

A partial export still carries a full-looking `<Controller>` element, which
is exactly why this went unnoticed -- but it is marked `Use="Context"`, and
so is every declaration hanging off it that the target merely REFERENCES.
The thing actually being exported is marked `Use="Target"`.

The rule that falls out, and the one this module implements: an element is
TARGET-scope if it or any ancestor carries `Use="Target"`; everything else
in a `ContainsContext="true"` file is CONTEXT. Note the nesting is not what
you would guess -- in a Rung export the chain is

    Program Use="Context" > Routines Use="Context" > Routine Use="Context"
      > RLLContent Use="Context" > Rung Use="TARGET"

so "is it inside a Context container" is the WRONG test; only the nearest
Use attribute up the chain decides.

WHAT THAT MEANS FOR SIZING
--------------------------
* No base load on anything but a Controller export. `empty_project_baseline`,
  the firmware/catalog/safety baseline deltas and the whole task/program
  shell decomposition are properties of a PROJECT. A program, routine, rung,
  AOI or UDT export has no project.
* Context declarations are still real, and James's point about them is the
  reason this module reports them rather than dropping them: "rungs,
  routines and programs might contain controller tags". A rung that
  references `CurrentTimeSTR` carries that controller tag along in its
  context, and importing the rung into a controller that does not already
  have it creates it. So the honest answer is two numbers, not one: what the
  target itself costs, and what its context would additionally cost IF those
  declarations are not already in the destination controller. Summing them
  blindly over-states an import into a controller that already has them;
  dropping the context under-states a fresh import. Both get reported.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

# Target types Studio 5000 emits. Anything else is passed through unchanged
# and treated as partial (never as a whole controller) -- an unrecognised
# target type must not silently earn the project base load.
WHOLE_CONTROLLER = "Controller"

_TARGET_TYPE_LABEL = {
    "Controller": "whole controller project",
    "Program": "single program",
    "Routine": "single routine",
    "Rung": "loose rung(s)",
    "AddOnInstructionDefinition": "single Add-On Instruction definition",
    "DataType": "single UDT definition",
}


@dataclass(frozen=True)
class ExportScope:
    target_type: str
    target_name: str | None
    target_sub_type: str | None
    target_count: int
    contains_context: bool

    @property
    def is_whole_controller(self) -> bool:
        """A whole project, and the ONLY case that earns the project base
        load. Deliberately requires both signals to agree: TargetType says
        Controller AND the file does not declare itself as carrying context.
        A Controller-typed export WITH context is not a shape this project
        has ever seen, and if one turns up it is safer to treat it as partial
        (understate) than to hand it a 13,296-byte baseline it may not have.
        """
        return self.target_type == WHOLE_CONTROLLER and not self.contains_context

    def describe(self) -> str:
        label = _TARGET_TYPE_LABEL.get(self.target_type, f"unrecognised target type {self.target_type!r}")
        name = f" '{self.target_name}'" if self.target_name else ""
        sub = f" ({self.target_sub_type})" if self.target_sub_type else ""
        count = f" x{self.target_count}" if self.target_count > 1 else ""
        return f"{label}{name}{sub}{count}"


@dataclass(frozen=True)
class ContextNames:
    """Names of declarations present only as CONTEXT, per entry-path family.

    Kept as plain name sets rather than element references so a SizeEntry
    can be classified by its `path` alone -- report.py builds those paths as
    "controller/<tag>", "program:<P>/<R>", "udt_definitions/<name>",
    "aoi_definitions/<name>" and so on, and nothing downstream keeps a link
    back to the element it came from.
    """

    controller_tags: frozenset[str] = frozenset()
    programs: frozenset[str] = frozenset()
    routines: frozenset[str] = frozenset()         # context "program:<P>/<R>"
    target_routines: frozenset[str] = frozenset()  # target "program:<P>/<R>"
    udts: frozenset[str] = frozenset()
    aois: frozenset[str] = frozenset()
    modules: frozenset[str] = frozenset()


def detect_export_scope(root: ET.Element) -> ExportScope:
    """Read the export's own declared scope off the root element."""
    try:
        count = int(root.get("TargetCount") or "1")
    except ValueError:
        count = 1
    return ExportScope(
        target_type=root.get("TargetType") or WHOLE_CONTROLLER,
        target_name=root.get("TargetName"),
        target_sub_type=root.get("TargetSubType"),
        target_count=max(count, 1),
        contains_context=(root.get("ContainsContext") or "").lower() == "true",
    )


def _use_map(root: ET.Element) -> dict[ET.Element, str]:
    """element -> nearest Use value at or above it ("Target"/"Context"/"").

    ElementTree has no parent pointers, so this is one explicit walk rather
    than repeated ancestor lookups.
    """
    resolved: dict[ET.Element, str] = {}

    def walk(el: ET.Element, inherited: str) -> None:
        own = el.get("Use") or inherited
        resolved[el] = own
        for child in el:
            walk(child, own)

    walk(root, root.get("Use") or "")
    return resolved


def context_names(root: ET.Element, scope: ExportScope) -> ContextNames:
    """Which declarations in this file are context-only, by name.

    A whole-controller export has no context at all -- everything in it is
    the project -- so this returns empty sets and every caller's
    classification collapses to "target", which is the pre-existing
    behaviour for those files.
    """
    if scope.is_whole_controller:
        return ContextNames()

    use = _use_map(root)

    def is_context(el: ET.Element) -> bool:
        return use.get(el) != "Target"

    controller = root.find("Controller")
    if controller is None:
        return ContextNames()

    ctrl_tags = {
        t.get("Name") for t in controller.findall("Tags/Tag")
        if t.get("Name") and is_context(t)
    }
    udts = {
        d.get("Name") for d in controller.findall("DataTypes/DataType")
        if d.get("Name") and is_context(d)
    }
    aois = {
        a.get("Name")
        for a in controller.findall("AddOnInstructionDefinitions/AddOnInstructionDefinition")
        if a.get("Name") and is_context(a)
    }
    modules = {
        m.get("Name") for m in controller.findall("Modules/Module")
        if m.get("Name") and is_context(m)
    }

    programs: set[str] = set()
    routines: set[str] = set()
    target_routines: set[str] = set()
    for program_el in controller.findall("Programs/Program"):
        pname = program_el.get("Name")
        if not pname:
            continue
        if is_context(program_el):
            programs.add(pname)
        for routine_el in program_el.findall("Routines/Routine"):
            rname = routine_el.get("Name")
            if not rname:
                continue
            # A routine inside a context program can still BE the target
            # (Routine export), and a rung inside a context routine can be
            # the target (Rung export) -- in which case the routine itself
            # is context but its target rung's cost is real. The rung case
            # is handled by report.py, which sizes rungs through the
            # routine; here the routine counts as target if it, or anything
            # inside it, is marked Target.
            has_target_descendant = any(
                use.get(d) == "Target" for d in routine_el.iter()
            )
            if is_context(routine_el) and not has_target_descendant:
                routines.add(f"program:{pname}/{rname}")
            else:
                target_routines.add(f"program:{pname}/{rname}")

    return ContextNames(
        controller_tags=frozenset(ctrl_tags), programs=frozenset(programs),
        routines=frozenset(routines), target_routines=frozenset(target_routines),
        udts=frozenset(udts), aois=frozenset(aois),
        modules=frozenset(modules),
    )


# Entry paths report.py builds, mapped to the ContextNames field that
# decides them. Kept here next to the producer of those names so the two
# cannot drift apart silently.
def classify_path(path: str, ctx: ContextNames) -> str:
    """"target" | "context" | "project" for one SizeEntry path."""
    if path in ("project_baseline", "task_program_shell", "safety_task_program_shell",
                "firmware_baseline_delta", "safety_capable_baseline_delta",
                "catalog_baseline_delta"):
        return "project"
    if path.startswith("controller/"):
        return "context" if path[len("controller/"):] in ctx.controller_tags else "target"
    if path.startswith("udt_definitions/"):
        # report.py emits AOI definitions under this SAME path prefix (see
        # its definition_entries block) -- checking only ctx.udts here would
        # silently classify every context AOI as target. Confirmed against a
        # real AOI export: SingleSolValve_AOI.L5X has an empty <DataTypes>
        # and one AddOnInstructionDefinition, and its entry path is
        # "udt_definitions/SingleSolValve".
        name = path[len("udt_definitions/"):]
        return "context" if name in ctx.udts or name in ctx.aois else "target"
    if path.startswith("modules/"):
        return "context" if path[len("modules/"):] in ctx.modules else "target"
    if path.startswith("program:"):
        # A routine_logic path and a program_tag path are both
        # "program:<P>/<X>", so the routine sets have to be consulted BEFORE
        # falling back to "is the program itself context". Without that, a
        # Routine export's own target routine was classified as context
        # purely because its containing program is (real case:
        # Flashers_Routine_RLL.L5X, target routine inside context program
        # "Housekeeping" -- it reported target=0).
        if path in ctx.target_routines:
            return "target"
        if path in ctx.routines:
            return "context"
        program = path[len("program:"):].split("/", 1)[0]
        return "context" if program in ctx.programs else "target"
    return "target"


def split_totals(entries, ctx: ContextNames) -> dict[str, int]:
    """{"target","context","project","total"} byte subtotals for a report.

    `entries` is any iterable of objects with `.path` and `.bytes` (a
    SizeEntry). The split is what makes a partial export's number honest:

      target  -- what the exported thing itself costs
      context -- declarations it drags along (controller tags, UDTs, AOIs),
                 which cost this much ONLY IF the destination controller
                 does not already have them
      project -- base load / shells; nonzero only on a whole-controller
                 export, by construction

    On a whole-controller export every entry classifies as target or
    project and `context` is 0, so callers can print the same three numbers
    for every file without special-casing.
    """
    out = {"target": 0, "context": 0, "project": 0}
    for e in entries:
        out[classify_path(e.path, ctx)] += e.bytes
    out["total"] = out["target"] + out["context"] + out["project"]
    return out
