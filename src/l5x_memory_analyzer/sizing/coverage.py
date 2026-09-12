"""What this engine did NOT price on the file it was just given.

2026-09-04: handing over a batch of unseen real programs: "beware
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

# Safety-task instructions: OUT OF SCOPE, not unpriced.
#
# Reported as coverage gaps until 2026-09-12, which was wrong in the same way
# reporting ST as unpriced was wrong after it got wired -- it overstates the
# hole and it buries the gaps that are real. These five only appear inside a
# GuardLogix SafetyProgram, which this project does not size at all
# (SafetyLevel/safety-task content is explicitly out of scope; CROUT was
# reclassified the same way 2026-08-24, see OQ-CROUT-MAPC-BUILDFAIL).
#
# Identified from their real call shapes in the corpus, which all take the
# `_S`-suffixed safety reset tags that only exist in a safety task:
#   ESTOP(Chain,MANUAL,Ch01,Ch02,E_Stop_Reset_S,Fault_Reset_S)
#   ROUT(Exp,NEGATIVE,Exp.Enable,FBK,FBK,Fault_Reset_S)
#   LC(LC01,MANUAL,Ch_01,Ch_02,0,0,LC01_Reset,Fault_Reset_S)
#   RIN(Chain,AUTOMATIC,Ch01_Ch02,Ch01_Ch02,Gate_Reset_S,Fault_Reset_S)
#
# A safety instruction inside a NON-safety routine would be a different
# matter, but none exists in the corpus and Studio would reject it.
_SAFETY_FAMILY = frozenset({"ESTOP", "ROUT", "CROUT", "LC", "RIN"})

# Mnemonics confirmed in this corpus to be USER AOIs, not built-in
# instructions. A call to one of these in a file that does NOT declare it is a
# partial/filtered export, which is a different finding from a missing weight
# and must not be reported as one.
#
# SCP, 2026-09-12: declared as an AddOnInstructionDefinition in four real
# exports (Fisher_Synergy_Bead, BT1XX_FFC, Fisher_P800Sub, PWO_134190) and
# CALLED BUT NOT DECLARED in MRFP_Edger_2026_06_01_r00. Its call shapes vary in
# arity across the corpus (3 operands in one program, 7 in another), which is
# itself the signature of a user AOI rather than a built-in. The generic
# name-shape heuristic below cannot catch it: "SCP" is short and has no
# underscore, so it reads as a built-in mnemonic.
_KNOWN_USER_AOI = frozenset({"SCP"})

# Routine Type values this engine can size. Everything else is a real
# coverage hole, not a parse error.
# ST joined this set 2026-09-04 when sizing/structured_text.py was wired --
# before that an ST routine contributed exactly ZERO and this coverage gap
# was the only thing saying so. ST is now sized (22 of 23 captured ST files
# land within 11 bytes), so reporting it as an unpriced hole would be
# stale. Individual ST ASSIGNMENT SHAPES outside the measured table are
# still reported, as coverage/st_expression/... from report.py -- that is
# the honest remaining gap, and it is per-shape rather than per-language.
_SIZED_ROUTINE_TYPES = frozenset({"RLL", "ST"})

_ROUTINE_TYPE_NOTES = {
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
    skip = (_PRICED_ELSEWHERE | _SAFETY_FAMILY | set(weighted_mnemonics)
            | _declared_aoi_names(root))
    unweighted: dict[str, int] = {}
    for _owner, routine_el in _iter_routines(root):
        if routine_language(routine_el) not in _SIZED_ROUTINE_TYPES:
            continue  # already reported whole, above
        for mnemonic, n in count_instructions_in_text(_rung_texts(routine_el)).items():
            if mnemonic not in skip:
                unweighted[mnemonic] = unweighted.get(mnemonic, 0) + n
    for mnemonic, n in sorted(unweighted.items(), key=lambda kv: -kv[1]):
        if mnemonic in _KNOWN_USER_AOI:
            note = (
                " CONFIRMED a user AOI, not a built-in: other exports in this corpus declare an "
                "AddOnInstructionDefinition by this name. Its absence here means a "
                "partial/filtered export, so do NOT add a weight for it -- the definition and "
                "its own cost are simply missing from this file."
            )
        elif _looks_user_defined(mnemonic):
            note = (
                " The name shape (longer than any built-in mnemonic, or containing an underscore) "
                "suggests a user-defined AOI whose AddOnInstructionDefinition is NOT present in "
                "this file -- a partial/filtered export -- rather than a built-in instruction. "
                "Confirm which before adding a weight for it; a real case of this is on file "
                "(AOI_BNI004A_40_27_041, called 4x in a real corpus export that carries no "
                "definition for it)."
            )
        else:
            note = ""
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

    # --- datatype-level alarm definitions (v38) -----------------------
    # <AlarmDefinitions><DatatypeAlarmDefinition><MemberAlarmDefinition>
    # is a v38 shape: an alarm TEMPLATE attached to a data type, distinct
    # from the tag-level <AlarmConditions> this engine already prices
    # exactly. Found 2026-09-08 in real blank 1756-L9xTS v38 exports, where
    # a stock P_PID definition carrying six member alarms was priced at
    # zero and reported nothing at all -- the exact silent-zero this audit
    # exists to prevent. Reported as a gap until real capture data says
    # what a definition costs; see OQ-ALARMDEF.
    # Keyed on the DEFINITION, not on its member alarms: a definition
    # holding zero members is still unpriced content, and gating the notice
    # on member count alone reproduced the same silence one level up.
    datatype_defs = root.findall(".//DatatypeAlarmDefinition")
    member_defs = root.findall(".//DatatypeAlarmDefinition/MemberAlarmDefinition")
    if datatype_defs:
        owners = sorted({el.get("Name") or "?" for el in datatype_defs})
        gaps.append(CoverageGap(
            kind="alarm_definition", detail="DatatypeAlarmDefinition",
            count=len(member_defs) or len(datatype_defs),
            path="coverage/alarm_definitions",
            message=(
                f"{len(member_defs)} MemberAlarmDefinition across "
                f"{len(datatype_defs)} DatatypeAlarmDefinition ({', '.join(owners[:4])}"
                f"{', ...' if len(owners) > 4 else ''}) priced at zero. This is a "
                f"datatype-level alarm TEMPLATE (v38), not the tag-level "
                f"AlarmCondition the engine sizes exactly. Unmodelled -- OQ-ALARMDEF."
            ),
        ))

    return gaps
