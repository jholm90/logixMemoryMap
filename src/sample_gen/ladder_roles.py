"""What each ladder instruction is, and where in a rung it may stand.

Three roles:

  condition   tests something and conditions the rung: the bit tests (XIC, XIO), the
              comparisons (EQU / EQ, NEQ / NE, GRT / GT, GEQ / GE, LES / LT, LEQ / LE, LIM /
              LIMIT, MEQ, CMP, DTR, IsINF, IsNAN), the one-shot ONS, the sequencer input SQI,
              license validation LV and AFI (always false). A condition can never be the last thing on a rung or on
              an output branch leg: Studio rejects a rung that ends in one.
  control     program flow and the logic operands: LBL, JMP, JSR, SBR, RET, MCR, TND, NOP,
              IOT, UID, UIE, EOT, EVENT, BRK, FOR. LBL and SBR must be the first instruction on
              their rung and need something after them, and SBR the first of its routine; MCR
              must be the last on its rung, and MCRs come in pairs in a routine (one opening a
              zone, one closing it); the rest may stand anywhere.
  output      everything that does something: OTE / OTL / OTU, MOV, timers and counters, math,
              file, string, motion (MAM, MAJ, ...), messages, PID. An output may end a rung, and
              Logix accepts one mid-rung with conditions after it.

An instruction not listed (an AOI call, or a mnemonic no generator has used) is treated as an
output: placed anywhere, never flagged. `sample_gen.lint` enforces the placement rules on every
generated file, and `rung_findings` is the check it runs.
"""

from __future__ import annotations

import re

from l5x_memory_analyzer.parser.logic import V36_MNEMONIC_ALIASES

_COMPARISONS = {"EQU", "NEQ", "GRT", "GEQ", "LES", "LEQ", "LIM", "MEQ", "CMP", "DTR", "IsINF", "IsNAN"}
# LV (license validation) conditions its rung: Studio refuses one with no output after it
# ("Missing output instruction", ldgap_lv_50 / _100, 2026-10-31).
_BIT_TESTS = {"XIC", "XIO", "ONS", "SQI", "AFI", "LV"}
CONDITIONS = _COMPARISONS | _BIT_TESTS
CONTROL = {"LBL", "JMP", "JSR", "SBR", "RET", "MCR", "TND", "NOP", "IOT", "UID", "UIE", "EOT", "EVENT",
           "BRK", "FOR"}
# Must be the first instruction on the rung (SBR, the first of its routine as well).
FIRST_ON_RUNG = {"LBL", "SBR"}
# Must be the last instruction on the rung.
LAST_ON_RUNG = {"MCR"}

# Both spellings across the v36 rename.
for _new, _old in V36_MNEMONIC_ALIASES.items():
    if _old in CONDITIONS:
        CONDITIONS.add(_new)
    if _old in CONTROL:
        CONTROL.add(_new)


def role(mnemonic: str) -> str:
    if mnemonic in CONDITIONS:
        return "condition"
    if mnemonic in CONTROL:
        return "control"
    return "output"


_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def parse_rung(text: str) -> list:
    """The rung as a nested list: a call is (name, args); a branch is a list of legs, each a
    list of elements. Commas inside a call's parentheses are operand separators, outside them
    (inside `[...]`) leg separators."""
    pos = 0
    n = len(text)

    def seq(stop: str) -> list:
        nonlocal pos
        out = []
        while pos < n:
            c = text[pos]
            if c in " \t\r\n;":
                pos += 1
            elif c == "[":
                pos += 1
                legs = [seq(",]")]
                while pos < n and text[pos] == ",":
                    pos += 1
                    legs.append(seq(",]"))
                pos += 1  # the closing "]"
                out.append(legs)
            elif c in stop:
                return out
            else:
                m = _NAME.match(text, pos)
                if not m:
                    pos += 1
                    continue
                pos = m.end()
                if pos < n and text[pos] == "(":
                    depth, start = 0, pos + 1
                    while pos < n:
                        if text[pos] in "([":
                            depth += 1
                        elif text[pos] in ")]":
                            depth -= 1
                            if depth == 0:
                                break
                        pos += 1
                    out.append((m.group(0), text[start:pos]))
                    pos += 1
        return out

    return seq("")


def _terminal_calls(elements: list) -> list[str]:
    """The instruction(s) a sequence ends on: its last call, or the last call of every leg
    when it ends on a branch."""
    if not elements:
        return []
    last = elements[-1]
    if isinstance(last, tuple):
        return [last[0]]
    return [m for leg in last for m in _terminal_calls(leg)]


def rung_findings(text: str, aoi_names: frozenset[str] | set[str] = frozenset()) -> list[tuple[str, str]]:
    """(kind, detail) for every placement rule the rung breaks."""
    tree = parse_rung(text)
    if not tree:
        return []
    out = []
    flat = []

    def walk(elems, top):
        for i, e in enumerate(elems):
            if isinstance(e, tuple):
                flat.append(e[0])
                if e[0] in FIRST_ON_RUNG and e[0] not in aoi_names and not (top and i == 0):
                    out.append(("must_be_first_on_rung",
                                f"{e[0]} must be the first instruction on its rung: {text.strip()!r}"))
            else:
                for leg in e:
                    walk(leg, False)

    walk(tree, True)
    ends = [m for m in _terminal_calls(tree) if m not in aoi_names]
    for m in sorted(set(flat) & LAST_ON_RUNG - set(aoi_names)):
        if flat[-1] != m or m not in ends or len(ends) != 1:
            out.append(("must_be_last_on_rung", f"{m} must be the last instruction on its rung: {text.strip()!r}"))
    bad = sorted({m for m in ends if role(m) == "condition"})
    if bad:
        out.append(("condition_at_rung_end",
                    f"the rung ends on {', '.join(bad)}, a condition; a rung (and every leg of a "
                    f"branch it ends on) must end on an output or control instruction: {text.strip()!r}"))
    if len(flat) == 1 and flat[0] in FIRST_ON_RUNG and flat[0] not in aoi_names:
        out.append(("first_on_rung_needs_trailing",
                    f"{flat[0]} needs an instruction after it on its rung (e.g. NOP()): {text.strip()!r}"))
    return out


def terminated(text: str) -> str:
    """The rung text with a NOP() appended when it would end on a condition."""
    body = text.rstrip().rstrip(";")
    if any(role(m) == "condition" for m in _terminal_calls(parse_rung(body))):
        body += "NOP()"
    return body + ";"


def routine_findings(rung_texts: list[str], aoi_names: frozenset[str] | set[str] = frozenset()) -> list[tuple[str, str]]:
    """(kind, detail) for the rules that span a routine's rungs.

    MCR in pairs is a project rule, not a build rule: an MCR toggles its zone, so a zone is
    opened by one and closed by the next, and a routine with an odd count leaves a zone open to
    its end. Studio accepts that (one real program, realprog_27, has a single MCR in an AOI's
    logic and verified), but every generated routine closes what it opens."""
    if "MCR" in aoi_names:
        return []
    count = sum(1 for t in rung_texts for name, _ in _calls(parse_rung(t)) if name == "MCR")
    if count % 2:
        return [("mcr_unpaired", f"{count} MCR in the routine; MCRs come in pairs, one opening a zone and "
                                 f"one closing it")]
    return []


def _calls(elements: list):
    for e in elements:
        if isinstance(e, tuple):
            yield e
        else:
            for leg in e:
                yield from _calls(leg)

