"""What this engine did NOT price on the file it was just given.

James, 2026-09-04, handing over a batch of unseen real programs: "beware
there is going to be stuff that you might have never seen before inside. I
need to make sure that in the long run all of the calculations are done
inside the python logic for the total project scripts and not just claude
in depth testing."

That is the gap this module closes. Before it, three real classes of
content were priced at exactly zero with NO signal of any kind:

  * A routine that is not RLL. `parse_rll_routines()` and
    `parse_aoi_internal_logic()` both `continue` past any Routine whose
    Type isn't "RLL", so Structured Text, Function Block and SFC routines
    did not merely size wrong -- they did not exist. The first real virgin
    file measured (Cardin_TrimSortStack) carries 3 ST routines / 505 ST
    lines that contributed 0 to its prediction, and nothing in the output
    said so. Across samples/local/ it is 297 ST routines / 24,017 lines.
  * An instruction mnemonic with no entry in `logic_instructions.weights`.
    `size_routine()` does `weights.get(mnemonic)` and skips a None, so an
    unrecognised instruction costs 0 and is indistinguishable in the
    output from one that genuinely costs 0.
  * An AOI whose internal Logic routine is non-RLL, same reason.

Unsized TAGS and unmodeled MODULES already surfaced as SizeErrors, and
that is exactly the pattern followed here: `audit_coverage()` returns the
same shape, `build_report()` appends it to the errors list, and it
therefore reaches the CLI, the UI and the CSV/XLSX export with no
per-caller work. A gap is REPORTED, never guessed at with a made-up byte
value -- an invented number would be worse than a visible hole.

Deliberately NOT flagged, because each is priced somewhere other than the
weights table and flagging it would be a false alarm:
  * CPT -- costed per call from its own expression (`cpt_expression`).
  * BST/NXB/BND -- costed via branch_bracket_cost_per_instruction.
  * Any declared AddOnInstructionDefinition name -- an AOI call is priced
    as an AOI, not as a built-in mnemonic.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from l5x_memory_analyzer.parser.alarms import parse_alarm_conditions
from l5x_memory_analyzer.parser.logic import count_instructions_in_text, routine_language

# Priced outside logic_instructions.weights -- see the module docstring.
_PRICED_ELSEWHERE = frozenset({"CPT", "BST", "NXB", "BND"})

# Routine Type values this engine can size. Everything else is a real
# coverage hole, not a parse error.
_SIZED_ROUTINE_TYPES = frozenset({"RLL"})

_ROUTINE_TYPE_NOTES = {
    "ST": ("Structured Text", "OQ-STSIZING"),
    "FBD": ("Function Block Diagram", "no open question yet -- no real data"),
    "SFC": ("Sequential Function Chart", "no open question yet -- no real data"),
}


@dataclass(frozen=True)
class CoverageGap:
    """One class of content the engine found and did not price."""

    kind: str      # "routine_type" | "instruction"
    detail: str    # "ST" / "SBR"
    count: int     # routines, or instruction occurrences
    path: str
    message: str


def _routine_content_size(routine_el: ET.Element) -> int:
    """A rough 'how much is in here' number for the report line -- ST/ST-like
    source lines, or child elements for a diagram language. Never used as a
    byte estimate, only to say how large the unpriced hole is."""
    st = routine_el.find("STContent")
    if st is not None:
        return len(st.findall("Line"))
    fbd = routine_el.find("FBDContent")
    if fbd is not None:
        return sum(len(sheet) for sheet in fbd)
    sfc = routine_el.find("SFCContent")
    if sfc is not None:
        return len(list(sfc))
    return 0


def _iter_routines(root: ET.Element):
    """(owner_label, routine_element) for every routine in the file, program
    routines and AOI-internal routines alike -- both parsers drop non-RLL."""
    programs = root.find("Controller/Programs")
    if programs is not None:
        for program_el in programs.findall("Program"):
            owner = f"Program {program_el.get('Name')}"
            routines_el = program_el.find("Routines")
            if routines_el is not None:
                for routine_el in routines_el.findall("Routine"):
                    yield owner, routine_el
    aois = root.find("Controller/AddOnInstructionDefinitions")
    if aois is not None:
        for aoi_el in aois.findall("AddOnInstructionDefinition"):
            owner = f"AOI {aoi_el.get('Name')}"
            routines_el = aoi_el.find("Routines")
            if routines_el is not None:
                for routine_el in routines_el.findall("Routine"):
                    yield owner, routine_el


def _declared_aoi_names(root: ET.Element) -> set[str]:
    aois = root.find("Controller/AddOnInstructionDefinitions")
    if aois is None:
        return set()
    return {
        el.get("Name") for el in aois.findall("AddOnInstructionDefinition") if el.get("Name")
    }


def _rung_texts(routine_el: ET.Element) -> list[str]:
    rll = routine_el.find("RLLContent")
    if rll is None:
        return []
    return [
        rung_el.find("Text").text or ""
        for rung_el in rll.findall("Rung")
        if rung_el.find("Text") is not None
    ]


def _looks_user_defined(mnemonic: str) -> bool:
    """Every built-in Logix mnemonic is 5 uppercase characters or fewer and
    carries no underscore. A longer or underscored name in instruction
    position is far more likely an AOI call whose definition did not come
    across in this export than a built-in nobody has weighed yet."""
    return len(mnemonic) > 5 or "_" in mnemonic


def audit_coverage(root: ET.Element, weighted_mnemonics) -> list[CoverageGap]:
    """Every class of content in this file that the engine priced at zero
    without modelling it. `weighted_mnemonics` is the model's own
    `logic_instructions.weights` keys, so this can never drift out of sync
    with what the sizer actually knows."""
    gaps: list[CoverageGap] = []

    # --- routines in a language this engine cannot size ---------------
    by_type: dict[str, list[tuple[str, str, int]]] = {}
    for owner, routine_el in _iter_routines(root):
        rtype = routine_language(routine_el)
        if rtype in _SIZED_ROUTINE_TYPES:
            continue
        by_type.setdefault(rtype, []).append(
            (owner, routine_el.get("Name") or "?", _routine_content_size(routine_el))
        )
    for rtype, found in sorted(by_type.items()):
        label, ref = _ROUTINE_TYPE_NOTES.get(rtype, (rtype, "unrecognised Routine Type"))
        content = sum(size for _, _, size in found)
        owners = sorted({owner for owner, _, _ in found})
        gaps.append(CoverageGap(
            kind="routine_type", detail=rtype, count=len(found),
            path=f"coverage/routine_type/{rtype}",
            message=(
                f"{len(found)} {label} routine(s) ({content} source line(s)/element(s)) across "
                f"{len(owners)} owner(s) contribute ZERO to this total -- {label} is not sized "
                f"by this engine at all ({ref}). The total below is understated by however much "
                f"that content really costs. Owners: {', '.join(owners[:6])}"
                f"{' ...' if len(owners) > 6 else ''}"
            ),
        ))

    # --- instructions with no weight ----------------------------------
    skip = _PRICED_ELSEWHERE | set(weighted_mnemonics) | _declared_aoi_names(root)
    unweighted: dict[str, int] = {}
    for _owner, routine_el in _iter_routines(root):
        if routine_language(routine_el) not in _SIZED_ROUTINE_TYPES:
            continue  # already reported whole, above
        for mnemonic, n in count_instructions_in_text(_rung_texts(routine_el)).items():
            if mnemonic not in skip:
                unweighted[mnemonic] = unweighted.get(mnemonic, 0) + n
    for mnemonic, n in sorted(unweighted.items(), key=lambda kv: -kv[1]):
        note = (
            " The name shape (longer than any built-in mnemonic, or containing an underscore) "
            "suggests a user-defined AOI whose AddOnInstructionDefinition is NOT present in "
            "this file -- a partial/filtered export -- rather than a built-in instruction. "
            "Confirm which before adding a weight for it; a real case of this is on file "
            "(AOI_BNI004A_40_27_041, called 4x in a real corpus export that carries no "
            "definition for it)."
            if _looks_user_defined(mnemonic) else ""
        )
        gaps.append(CoverageGap(
            kind="instruction", detail=mnemonic, count=n,
            path=f"coverage/instruction/{mnemonic}",
            message=(
                f"{mnemonic} appears {n} time(s) in sized RLL routines but has no weight in "
                f"logic_instructions.weights, so it is charged 0 bytes. That is an absence of "
                f"data, not a measurement -- see docs/INSTRUCTION_COVERAGE.md.{note}"
            ),
        ))

    # Tag-based alarm conditions were reported here as an unpriced gap
    # from 2026-09-04 until 2026-09-05, when the alarmcond_* batch solved
    # them exactly (memory_model.yaml alarm_conditions, sizing/alarms.py).
    # They are now a real sized entry, so flagging them would be a false
    # alarm -- the gap list has to shrink when a hole is actually closed,
    # or it stops meaning anything.

    return gaps
