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
    kind: str  # "missing_array_subscript" | "unrecognized_instruction"
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


def lint_l5x(l5x_text: str) -> list[LintFinding]:
    root = ET.fromstring(l5x_text)
    findings: list[LintFinding] = []

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
