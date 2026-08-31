"""Local heuristic pre-flight check for generated L5X files (James,
2026-08-22): "Curious if the SDK had L5X->ACD with controller validation/
program checking to make sure you did a good job generating the program
instead of me doing all these memory tests on bad programs."

Checked: `samples/convert_log.csv` shows every file from today's two real
bugs (the missing `[0]` array subscript on CPS/COP/FLL/BTD/SIZE, and T_ADD
called with no AOI definition at all) converted via `l5xgit l5x2acd` with
status "ok". The SDK's L5X->ACD conversion only opens/parses the project
(catches structural/schema failures like an unsupported ProcessorType,
confirmed from the 27 real FAILED rows in that log) -- it does NOT perform
ladder-logic verification. A file can convert cleanly and still contain
rung-level errors that only a real Studio 5000 Verify would catch. There's
no way to run that verify from this environment (needs the licensed SDK on
Windows), so this is the next best thing: a local, heuristic, non-
authoritative check for the specific classes of error already found the
hard way, run against every file before it ships instead of after James
spends real capture time on it.

Two checks:
  1. Array-typed tag referenced without a [index] subscript anywhere it's
     used as an instruction operand in rung text (the CPS/COP/FLL/BTD bug).
     SIZE is a confirmed exception (James's real COP_Samples.L5X, 2026-08-22:
     SIZE(COP_Source,0,COP_Size); -- bare array tag, no bracket) since its
     first operand is the whole array, not one element -- see lint_l5x.
  2. An instruction/AOI-style call (ALLCAPS mnemonic followed by "(") whose
     name isn't a known native instruction AND doesn't match any
     AddOnInstructionDefinition actually declared in the same file (the
     T_ADD bug).

Explicitly NOT a substitute for real Studio 5000 verification -- it can't
catch type mismatches, wrong argument counts, bad instance-tag wiring, or
anything semantic. It only catches the two specific real mistakes this
project has already made, plus close relatives of them.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

# Every native instruction mnemonic this project has confirmed real via
# the corpus scan (gen_logic_sweep.py's INSTRUCTIONS dict) plus JSR/LBL/JMP
# (handled specially there, not simple single-rung patterns) and a handful
# of other extremely common native instructions not yet in that sweep.
# Deliberately a whitelist, not the AB instruction set exhaustively -- an
# unrecognized-but-real instruction just means "not flagged as suspicious
# vs known-good," not "confirmed good," so keeping this list honest and
# growing it as new real instructions get used matters more than
# completeness on day one.
_KNOWN_NATIVE_INSTRUCTIONS = {
    "ABS", "ADD", "AFI", "ALMD", "BTD", "CLR", "CMP", "CONCAT", "COP", "CPS", "CPT",
    "CTU", "CTD", "DELETE", "DIV", "DTOS", "EQU", "FLL", "GEQ", "GRT", "GSV",
    "JMP", "JSR", "LBL", "LEQ", "LES", "LIM", "MEQ", "MID", "MOD", "MOV",
    "MSG", "MUL", "MVM", "NEQ", "NOP", "ONS", "OTE", "OTL", "OTU", "RES",
    "RTO", "SIZE", "SSV", "STOD", "SUB", "TOF", "TON", "XIC", "XIO", "XPY",
    "OSR", "OSF", "TRN", "SQR", "SBR", "RET",
    # Motion instructions (gen_motion_instructions.py, 2026-08-22) --
    # MAH/MSO corpus-confirmed call syntax, the rest real per Rockwell
    # documentation though not independently corpus-confirmed for that
    # exact mnemonic (see that generator's own docstring caveat).
    "MAM", "MAJ", "MAH", "MAS", "MSO", "MRP", "MAPC", "MCCP", "MAFR", "MASR",
    # First-pass instruction coverage sweep (gen_instruction_firstpass.py,
    # 2026-08-24) -- every real corpus-confirmed or documented-family-
    # inferred mnemonic added that batch. See that generator's own
    # docstring for the CORPUS_CONFIRMED/INFERRED/NEAR_VERBATIM citation
    # per instruction.
    "NOT", "NEG", "UID", "UIE", "MCR", "TND", "ATN", "DEG", "RAD", "TAN",
    "SWPB", "XOR", "FIND", "INSERT", "BSL", "BSR", "FFL", "FFU", "SRT",
    "AVE", "FAL", "FSC", "MDW", "MASD", "MGSD", "MGSR", "CROUT",
}

_INSTRUCTION_CALL = re.compile(r"\b([A-Z][A-Z0-9_]*)\(")


@dataclass(frozen=True)
class LintFinding:
    kind: str  # "missing_array_subscript" | "unrecognized_instruction" |
    # "duplicate_module_slot" | "chassis_size_exceeded"
    detail: str


def _array_tag_names(root: ET.Element) -> set[str]:
    names = set()
    for tags_el in root.iter("Tags"):
        for tag_el in tags_el.findall("Tag"):
            if tag_el.get("Dimensions"):
                name = tag_el.get("Name")
                if name:
                    names.add(name)
    return names


def _declared_aoi_names(root: ET.Element) -> set[str]:
    names = set()
    for aoi_el in root.iter("AddOnInstructionDefinition"):
        name = aoi_el.get("Name")
        if name:
            names.add(name)
    return names


def _all_rung_texts(root: ET.Element) -> list[str]:
    texts = []
    for text_el in root.iter("Text"):
        if text_el.text:
            texts.append(text_el.text)
    return texts


def _module_slot_findings(root: ET.Element) -> list[LintFinding]:
    """James, 2026-08-31: "Are you sure you are validating chassis size
    and duplicated slots? I explicitly remember asking you to check this
    when you were generating these 50 tests" -- a real gap, not a false
    alarm: this project's own lint pre-flight NEVER actually checked
    either one before this. A prior commit (e57fe42) claimed a "self-audit
    against every real failure class... (chassis size...)" came back clean
    on all 50 composite files; that claim was wrong -- it missed the exact
    slot-collision bug real Studio 5000 later caught in composite_
    realistic_07 (see gen_composite_realistic.py's _remap_local_icp_slot).
    This is the real, automated check that should have existed from the
    start, run against every generated file from now on (write_sample's
    lint_or_raise), not a one-off manual read-through.

    Two things, both fully derivable from the XML alone with no external
    Rockwell catalog knowledge needed:

    1. duplicate_module_slot -- two different Modules both claiming the
       identical (ParentModule, ParentModPortId, Address) connection
       point. Real Studio 5000 rejects this outright ("Slot number in use
       by another module") -- confirmed via James's real error on
       composite_realistic_07. Covers both a physical backplane slot
       collision (numeric Address) and a duplicate network address
       collision (Address as an IP string) -- either way, two devices
       can't occupy the same connection point on the same parent port.

    2. chassis_size_exceeded -- a Module's own upstream Port declares a
       numeric Address that is >= the Bus Size its parent module declared
       on the matching port. Real Studio 5000 rejects this too ("Chassis
       size exceeds the allowable size for a chassis") -- confirmed via
       James's real error on both fwmatrix_v31_1769_l30erm (RESOLVED_
       QUESTIONS.md) and eventtask_instronly (bare 5069-L306ER, OPEN_
       QUESTIONS.md OQ item 10). This only catches an INTERNALLY
       inconsistent file (we declared Bus Size=9 but also plugged
       something into slot 12) -- it can't independently verify that our
       own declared Bus Size is Rockwell's real per-catalog limit, which
       still needs real corpus/capture confirmation same as always.
    """
    findings: list[LintFinding] = []
    modules_by_name: dict[str, ET.Element] = {}
    for mod_el in root.iter("Module"):
        name = mod_el.get("Name")
        if name:
            modules_by_name[name] = mod_el

    # slot_key -> list of (module_name) claiming it
    slot_claims: dict[tuple[str, str, str], list[str]] = {}

    for mod_el in root.iter("Module"):
        name = mod_el.get("Name")
        parent_module = mod_el.get("ParentModule")
        parent_port_id = mod_el.get("ParentModPortId")
        if not name or not parent_module or parent_port_id is None:
            continue
        # The upstream Port is this module's own connection point INTO its
        # parent -- its Address is what must be unique among siblings on
        # the same parent port, and (if numeric) within the parent's own
        # declared Bus Size for that port.
        ports_el = mod_el.find("Ports")
        if ports_el is None:
            continue
        upstream_port = None
        for port_el in ports_el.findall("Port"):
            if port_el.get("Upstream") == "true":
                upstream_port = port_el
                break
        if upstream_port is None:
            continue
        address = upstream_port.get("Address")
        if address is None:
            continue

        key = (parent_module, parent_port_id, address)
        slot_claims.setdefault(key, []).append(name)

        if address.isdigit() and parent_module in modules_by_name:
            parent_el = modules_by_name[parent_module]
            parent_ports_el = parent_el.find("Ports")
            if parent_ports_el is not None:
                for parent_port_el in parent_ports_el.findall("Port"):
                    if parent_port_el.get("Id") != parent_port_id:
                        continue
                    bus_el = parent_port_el.find("Bus")
                    bus_size = bus_el.get("Size") if bus_el is not None else None
                    if bus_size and bus_size.isdigit() and int(address) >= int(bus_size):
                        findings.append(LintFinding(
                            "chassis_size_exceeded",
                            f"Module '{name}' Address={address} on parent '{parent_module}' Port "
                            f"Id={parent_port_id}, but that parent Port's own Bus Size={bus_size} "
                            f"(valid Address range is 0..{int(bus_size) - 1})",
                        ))
                    break

    for (parent_module, parent_port_id, address), claimants in slot_claims.items():
        if len(set(claimants)) > 1:
            findings.append(LintFinding(
                "duplicate_module_slot",
                f"{len(claimants)} Modules ({', '.join(claimants)}) all claim ParentModule="
                f"'{parent_module}' Port Id={parent_port_id} Address='{address}'",
            ))

    return findings


def lint_l5x(l5x_text: str) -> list[LintFinding]:
    root = ET.fromstring(l5x_text)
    findings: list[LintFinding] = []

    findings.extend(_module_slot_findings(root))

    array_tags = _array_tag_names(root)
    aoi_names = _declared_aoi_names(root)
    rung_texts = _all_rung_texts(root)

    for text in rung_texts:
        for tag in array_tags:
            # SIZE is a confirmed exception to the bracket rule (James's
            # own Studio-5000-verified COP_Samples.L5X, 2026-08-22:
            # SIZE(COP_Source,0,COP_Size); compiles clean against a plain
            # DINT[10] array with NO [index] subscript) -- unlike CPS/COP/
            # FLL/BTD, SIZE's first operand is the whole array, not one
            # element of it, so a bare tag immediately after "SIZE(" is
            # not a missing-subscript bug.
            pattern = re.compile(r"(?<!SIZE\()\b" + re.escape(tag) + r"\b(?!\s*\[)")
            if pattern.search(text):
                findings.append(LintFinding(
                    "missing_array_subscript",
                    f"array-typed tag '{tag}' referenced without a [index] subscript in rung text: {text.strip()!r}",
                ))

        for mnemonic in _INSTRUCTION_CALL.findall(text):
            if mnemonic in _KNOWN_NATIVE_INSTRUCTIONS or mnemonic in aoi_names:
                continue
            findings.append(LintFinding(
                "unrecognized_instruction",
                f"'{mnemonic}(' called in rung text but it's neither a known native instruction nor a "
                f"declared AddOnInstructionDefinition in this file: {text.strip()!r}",
            ))

    return findings


def lint_or_raise(l5x_text: str, context: str = "") -> None:
    """Convenience wrapper for generator scripts: raise loudly instead of
    silently shipping a file with one of these two known error classes."""
    findings = lint_l5x(l5x_text)
    if findings:
        lines = "\n".join(f"  - [{f.kind}] {f.detail}" for f in findings)
        prefix = f"{context}: " if context else ""
        raise ValueError(f"{prefix}lint found {len(findings)} issue(s):\n{lines}")
