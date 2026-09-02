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

Checks:
  1. Array-typed tag referenced without a [index] subscript anywhere it's
     used as an instruction operand in rung text (the CPS/COP/FLL/BTD bug).
     SIZE is a confirmed exception (James's real COP_Samples.L5X, 2026-08-22:
     SIZE(COP_Source,0,COP_Size); -- bare array tag, no bracket) since its
     first operand is the whole array, not one element -- see lint_l5x.
  2. An instruction/AOI-style call (ALLCAPS mnemonic followed by "(") whose
     name isn't a known native instruction AND doesn't match any
     AddOnInstructionDefinition actually declared in the same file (the
     T_ADD bug).
  3. duplicate_module_slot / chassis_size_exceeded (see _module_slot_findings)
     -- James, 2026-08-31: "Are you sure you are validating chassis size
     and duplicated slots?"
  4. aoi_call_arg_count_mismatch -- James, 2026-08-31, real Studio 5000
     verify error on composite_realistic_02/03.ACD ("Invalid number of
     arguments for instruction" on every AOI call rung): a declared AOI's
     Input/Output Parameters with Required="false" Visible="false" are
     HIDDEN from its own instruction call signature entirely (real Logix
     semantics, confirmed against samples/local/SJ_Gormley_20251112_r02.L5X's
     real PTimer calls -- see gen_aoi_required_visible.py's docstring) --
     only Required and/or Visible params are real call-argument slots.
     Checks the actual argument count at each call site against
     [count(Required), count(Required or Visible)] -- outside that range is
     a real, checkable mismatch. Does not model the exact-position nuance of
     which specific trailing optional params can be omitted (heuristic, not
     authoritative -- matches this file's existing scope).
  5. bit_level_instruction_on_non_bool_operand -- James, 2026-08-31, real,
     caught TWICE on his own re-conversion: "SINT/INT/DINT cannot be used
     for bit level instructions like XIO,XIC,OTE,OTU,OTL,ONS only bools
     and .Bits of SINT/INT/DINT." A bit-level instruction's operand must
     be BOOL or a bit-subscripted (".N") SINT/INT/DINT reference -- flags
     a bare non-BOOL operand with no subscript. Only checks operands this
     project's own generators can actually resolve a type for (see
     _resolve_operand_type); an unresolvable operand is silently skipped,
     not flagged.
  6. rung_missing_output_instruction -- James, 2026-08-31, real: "you also
     have conditional instructions like EQU with no operand at the end of
     the rung or a NOP() instruction. this is basic ladder logic." A rung
     whose every instruction is a pure condition/test
     (_PURE_CONDITION_INSTRUCTIONS) with no real output instruction has no
     effect and real Studio 5000 rejects it.
  7. non_sequential_module_slots -- James, 2026-09-02: "lots of racks did
     not have the slot numbers used in sequence and that was supposed to
     be a check you were adding for validation." See
     _slot_sequence_findings for the real generator bug this caught.

These last two were added the same day their bug class was found TWICE --
once fixed by hand in the one generator that hit it, then reintroduced
fresh in 3 more files written the same session. Hand-fixing a generator
when a real bug is found is not enough; the check has to be enforced here
so a FUTURE generator can't make the identical mistake silently.

Explicitly NOT a substitute for real Studio 5000 verification -- it can't
catch every type mismatch or bad instance-tag wiring. It only catches the
specific real mistakes this project has already made, plus close
relatives of them.
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

# REAL BUG FOUND 2026-08-31, self-audit while adding the aoi_call_arg_
# count_mismatch check below: this pattern required EVERY character after
# the first to be uppercase/digit/underscore -- fine for native
# instructions (XIC, OTE, CPT, all genuinely all-caps in real Logix), but
# it silently never matched ANY mixed-case AOI instance call, which is
# the norm for AOI naming across this entire project's own generators
# (e.g. "Comp02Aoi0(...)", "ReqVisAllhidden(...)", real corpus "PTimer(
# ...)"). The unrecognized_instruction check (T_ADD bug) and this new
# arg-count check were BOTH silently blind to every AOI call in every
# file this project has ever generated -- confirmed by testing the old
# pattern directly: `re.findall(r"\b([A-Z][A-Z0-9_]*)\(", "Comp02Aoi0(
# Inst,0,OutBit);")` returns [] (should return the call). Fixed to match
# any valid Logix identifier (starts with a letter/underscore, not
# case-restricted) immediately followed by "(" -- still correctly
# excludes non-identifier parens (a CPT expression's grouping "(" is
# never immediately preceded by a bare identifier without an operator).
_INSTRUCTION_CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\(")


@dataclass(frozen=True)
class LintFinding:
    kind: str  # "missing_array_subscript" | "unrecognized_instruction" |
    # "duplicate_module_slot" | "chassis_size_exceeded" |
    # "aoi_call_arg_count_mismatch" | "bit_level_instruction_on_non_bool_operand" |
    # "rung_missing_output_instruction" | "lbl_missing_trailing_instruction" |
    # "non_sequential_module_slots"
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


def _aoi_call_arg_bounds(root: ET.Element) -> dict[str, tuple[int, int]]:
    """aoi_name -> (min_args, max_args): min = count of Required="true"
    Input/Output Parameters, max = count of (Required="true" OR
    Visible="true") Input/Output Parameters, both in declaration order,
    excluding EnableIn/EnableOut/InOut (InOut params are always required
    and always present -- real semantics, see builders.py's aoi_xml
    docstring -- so they always count toward BOTH bounds)."""
    bounds = {}
    for aoi_el in root.iter("AddOnInstructionDefinition"):
        name = aoi_el.get("Name")
        if not name:
            continue
        min_args = 0
        max_args = 0
        params_el = aoi_el.find("Parameters")
        if params_el is None:
            bounds[name] = (0, 0)
            continue
        for p_el in params_el.findall("Parameter"):
            usage = p_el.get("Usage")
            if usage not in ("Input", "Output", "InOut"):
                continue
            if p_el.get("Name") in ("EnableIn", "EnableOut"):
                continue
            required = p_el.get("Required") == "true"
            visible = p_el.get("Visible") == "true"
            if usage == "InOut" or required:
                min_args += 1
                max_args += 1
            elif visible:
                max_args += 1
        bounds[name] = (min_args, max_args)
    return bounds


def _split_top_level_args(s: str) -> list[str]:
    """Splits a comma-separated argument list, respecting nested ()/[]
    (e.g. an array-index or bit-subscript operand shouldn't fracture the
    split). Returns [] for an empty/whitespace-only string."""
    s = s.strip()
    if not s:
        return []
    parts = []
    depth = 0
    current = []
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    parts.append("".join(current))
    return parts


def _call_sites(text: str) -> list[tuple[str, str]]:
    """Finds every "NAME(...)" call in rung text and returns (name,
    args_string) pairs, args_string being everything between the matching
    parens (balanced against nested brackets/parens inside, e.g. an
    array-index operand)."""
    sites = []
    for m in _INSTRUCTION_CALL.finditer(text):
        name = m.group(1)
        start = m.end()  # just past the opening "("
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] in "([":
                depth += 1
            elif text[i] in ")]":
                depth -= 1
            i += 1
        if depth == 0:
            sites.append((name, text[start:i - 1]))
    return sites


def _all_rung_texts(root: ET.Element) -> list[str]:
    texts = []
    for text_el in root.iter("Text"):
        if text_el.text:
            texts.append(text_el.text)
    return texts


# James, 2026-08-31, real, caught TWICE this same session on his own
# re-conversion after I'd already fixed the first occurrence: "SINT/INT/
# DINT cannot be used for bit level instructions like XIO,XIC,OTE,OTU,OTL,
# ONS only bools and .Bits of SINT/INT/DINT" and "conditional instructions
# like EQU with no operand at the end of the rung or a NOP() instruction."
# Both fixed by hand in the specific generators that hit them (3 files),
# but hand-fixing individual generators is exactly what already failed
# once -- a FUTURE generator can make the identical mistake and nothing
# catches it before it reaches James. These two checks are the real,
# structural fix: enforced automatically on every generated file, same as
# every other lint check here.
_BIT_LEVEL_INSTRUCTIONS = {"XIC", "XIO", "OTE", "OTU", "OTL", "ONS"}
# Instructions that only TEST a condition, with no side effect of their
# own -- if every instruction call in a rung belongs to this set, the rung
# has no real output/effect and real Studio 5000 rejects it outright.
_PURE_CONDITION_INSTRUCTIONS = {
    "XIC", "XIO", "EQU", "NEQ", "GRT", "GEQ", "LES", "LEQ", "LIM", "MEQ", "CMP",
}
_BIT_SUBSCRIPT_RE = re.compile(r"\.\d+$")
_BASE_TAG_NAME_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)")


def _tag_types_from(container_el: ET.Element, tag_element_name: str = "Tag") -> dict[str, str]:
    """bare tag/param/localtag name -> DataType, from every <Tag>/
    <Parameter>/<LocalTag> element found anywhere under container_el.
    Deliberately the same "last one wins on a bare-name collision"
    simplification already used by sizing/logic.py's own tag_types dict
    (report.py) -- not scope-correct in the face of a genuine same-name
    collision across programs, but no real calibration data in this
    project exercises that collision, and being conservative (a false
    negative) is safer here than a false positive on a file that's
    actually fine."""
    types: dict[str, str] = {}
    for el in container_el.iter(tag_element_name):
        name = el.get("Name")
        data_type = el.get("DataType")
        if name and data_type:
            types[name] = data_type
    return types


def _resolve_operand_type(operand: str, tag_types: dict[str, str]) -> str | None:
    """Best-effort DataType for a rung operand -- only handles the simple,
    common shapes this project's generators actually produce (a bare tag,
    or one level of [index]/.Member off it); anything more complex (a
    UDT-member chain, an indirect/tag-driven index) is deliberately left
    unresolved (None) rather than guessed at, matching sizing/logic.py's
    own _resolve_call_type conservative bias."""
    operand = operand.strip()
    m = _BASE_TAG_NAME_RE.match(operand)
    if not m:
        return None
    base = m.group(1)
    return tag_types.get(base)


def _bit_level_findings(rung_texts: list[str], tag_types: dict[str, str]) -> list[LintFinding]:
    """James, 2026-08-31: "SINT/INT/DINT cannot be used for bit level
    instructions like XIO,XIC,OTE,OTU,OTL,ONS only bools and .Bits of
    SINT/INT/DINT." Flags a bit-level instruction call whose single
    operand (a) does NOT already end in a ".N" bit subscript, AND (b)
    resolves (via _resolve_operand_type) to a non-BOOL atomic type. An
    operand that can't be resolved (AOI-internal member access, an
    indirect index, etc.) is silently skipped -- not flagged -- same
    conservative bias as every other type-sensitive check in this
    project."""
    findings = []
    for text in rung_texts:
        for mnemonic, args_str in _call_sites(text):
            if mnemonic not in _BIT_LEVEL_INSTRUCTIONS:
                continue
            args = _split_top_level_args(args_str)
            if len(args) != 1:
                continue
            operand = args[0].strip()
            if _BIT_SUBSCRIPT_RE.search(operand):
                continue  # already bit-subscripted, valid regardless of type
            resolved_type = _resolve_operand_type(operand, tag_types)
            if resolved_type and resolved_type != "BOOL":
                findings.append(LintFinding(
                    "bit_level_instruction_on_non_bool_operand",
                    f"'{mnemonic}({operand})' -- operand resolves to {resolved_type}, not BOOL, and "
                    f"has no '.N' bit subscript. XIC/XIO/OTE/OTU/OTL/ONS require a BOOL operand or a "
                    f"bit-subscripted SINT/INT/DINT reference: {text.strip()!r}",
                ))
    return findings


def _rung_missing_output_findings(rung_texts: list[str]) -> list[LintFinding]:
    """James, 2026-08-31: "conditional instructions like EQU with no
    operand at the end of the rung or a NOP() instruction. this is basic
    ladder logic." Flags a rung where every instruction call found is a
    pure condition/test instruction (_PURE_CONDITION_INSTRUCTIONS) with no
    real output/effect instruction anywhere in the rung -- real Studio
    5000 rejects a rung with no terminating output. A rung with ZERO
    instruction calls (blank/comment-only) is not flagged -- that's a
    different, already-confirmed-real shape (comments cost 0 blocks at
    any length), not this bug."""
    findings = []
    for text in rung_texts:
        mnemonics = [name for name, _args in _call_sites(text)]
        if mnemonics and all(m in _PURE_CONDITION_INSTRUCTIONS for m in mnemonics):
            findings.append(LintFinding(
                "rung_missing_output_instruction",
                f"every instruction in this rung is a pure condition/test ({', '.join(sorted(set(mnemonics)))}) "
                f"with no real output instruction (or NOP()) terminating the rung: {text.strip()!r}",
            ))
    return findings


def _lbl_missing_trailing_instruction_findings(rung_texts: list[str]) -> list[LintFinding]:
    """James, 2026-08-22 (gen_logic_sweep.py's group_lbl_jmp, found
    confirming the OQ-LBLJMP-STALE batch failure was real, not a stale-ACD-
    cache artifact): "lbl needs something after it, LBL(thisLabel); will
    fail - LBL(thisLabel)NOP(); will pass." A bare LBL with nothing else on
    its rung is invalid, the same general "rung needs a real terminating
    instruction" class as rung_missing_output_instruction above -- but LBL
    isn't a condition/test instruction (it's a label marker), so it was
    never caught by that check's _PURE_CONDITION_INSTRUCTIONS logic. Found
    2026-08-31 doing a full sweep of every "real bug" comment in this
    project for rules that were documented but never actually enforced
    (James: "read all of your comments and see if there are any rules
    that could be made") -- already fixed by hand in gen_logic_sweep.py
    itself, but nothing stopped a NEW generator from reintroducing it
    until now."""
    findings = []
    for text in rung_texts:
        mnemonics = [name for name, _args in _call_sites(text)]
        if mnemonics == ["LBL"]:
            findings.append(LintFinding(
                "lbl_missing_trailing_instruction",
                f"LBL with nothing else on its rung -- real Studio 5000 requires a trailing "
                f"instruction (e.g. NOP()) after LBL: {text.strip()!r}",
            ))
    return findings


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
        # 2026-09-02, real, found generating the v3 composite batch: a
        # Module element with NO Name attribute is real and imports fine
        # (confirmed: 1756-OF8/B's own genericized block has never carried
        # one, and its standalone modulesweep file converts "ok" every
        # time in convert_log.csv) -- but bailing out here on `not name`
        # made such a module invisible to EVERY check in this function,
        # including non_sequential_module_slots below: its real, already-
        # remapped slot doesn't get recorded, so the slot it legitimately
        # occupies reads as a false "gap" in the sequence. A synthetic,
        # per-element identifier (never collides with a real Name, since
        # real names can't contain "#") keeps it visible to slot tracking
        # without needing a fabricated Name in the XML itself.
        name = mod_el.get("Name") or f"{mod_el.get('CatalogNumber', '?')}#{id(mod_el)}"
        parent_module = mod_el.get("ParentModule")
        parent_port_id = mod_el.get("ParentModPortId")
        if not parent_module or parent_port_id is None:
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

    findings.extend(_slot_sequence_findings(slot_claims))
    return findings


def _slot_sequence_findings(
    slot_claims: dict[tuple[str, str, str], list[str]],
) -> list[LintFinding]:
    """James, 2026-09-02: "lots of racks did not have the slot numbers
    used in sequence and that was supposed to be a check you were adding
    for validation." Real bug this caught in gen_composite_realistic.py's
    _modules_xml_unique_ips: it keyed the assigned backplane slot off a
    catalog's raw index in the file's module list, so an Ethernet-only
    catalog (no real ICP-backplane root module) between two ICP-backplane
    catalogs silently consumed an index without consuming a slot, leaving
    a real gap (e.g. composite_realistic_v2_16: slots 2 and 4 present, 3
    never used). Real Rockwell backplanes don't leave a slot number
    unassigned in the middle of a populated run the way this project's own
    generation was doing it -- not because a physical gap is illegal (an
    empty physical slot is fine), but because THIS project always
    generates a fully-populated virtual chassis with no genuinely empty
    slots in between, so a numeric gap here is always a generation
    artifact, not an intentional empty slot.

    Heuristic, not authoritative: only flags a purely-NUMERIC-address
    sibling group (2+ Modules sharing the same (ParentModule,
    ParentModPortId)) whose sorted addresses skip a value -- an
    Ethernet-addressed group (dotted-IP Address strings) is never numeric
    and never flagged. A single module in a group can't have a gap by
    definition and is never flagged either; whether ITS OWN address is a
    sensible starting point is a generator-level concern (see
    gen_composite_realistic.py), not something a single data point can
    validate.
    """
    findings: list[LintFinding] = []
    by_port: dict[tuple[str, str], list[int]] = {}
    for (parent_module, parent_port_id, address), claimants in slot_claims.items():
        if not address.isdigit():
            continue
        by_port.setdefault((parent_module, parent_port_id), []).append(int(address))

    for (parent_module, parent_port_id), addresses in by_port.items():
        if len(addresses) < 2:
            continue
        addresses.sort()
        missing = [n for n in range(addresses[0], addresses[-1] + 1) if n not in addresses]
        if missing:
            findings.append(LintFinding(
                "non_sequential_module_slots",
                f"ParentModule='{parent_module}' Port Id={parent_port_id} has modules at "
                f"slots {addresses} -- missing {missing} in between",
            ))

    return findings


def lint_l5x(l5x_text: str) -> list[LintFinding]:
    root = ET.fromstring(l5x_text)
    findings: list[LintFinding] = []

    findings.extend(_module_slot_findings(root))

    array_tags = _array_tag_names(root)
    aoi_names = _declared_aoi_names(root)
    aoi_call_arg_bounds = _aoi_call_arg_bounds(root)
    rung_texts = _all_rung_texts(root)

    # bit_level_instruction_on_non_bool_operand / rung_missing_output_
    # instruction need to know each rung's OWN scope's tag types -- an
    # AOI-internal routine's operands are its own Parameters/LocalTags,
    # not the file-wide Tags table, and vice versa. Checked per-scope
    # rather than globally so a Program rung is never resolved against an
    # AOI's internal-only names or vice versa.
    global_tag_types = _tag_types_from(root, "Tag")
    findings.extend(_rung_missing_output_findings(rung_texts))
    findings.extend(_lbl_missing_trailing_instruction_findings(rung_texts))
    for program_el in root.iter("Program"):
        findings.extend(_bit_level_findings(_all_rung_texts(program_el), global_tag_types))
    for aoi_el in root.iter("AddOnInstructionDefinition"):
        aoi_tag_types = _tag_types_from(aoi_el, "Parameter")
        aoi_tag_types.update(_tag_types_from(aoi_el, "LocalTag"))
        findings.extend(_bit_level_findings(_all_rung_texts(aoi_el), aoi_tag_types))

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

        for mnemonic, args_str in _call_sites(text):
            if mnemonic in aoi_names:
                # First arg is always the instance tag, not a Parameter --
                # everything after it maps 1:1 to non-hidden Parameters in
                # declaration order. See _aoi_call_arg_bounds's docstring.
                args = _split_top_level_args(args_str)
                param_arg_count = max(len(args) - 1, 0)
                min_args, max_args = aoi_call_arg_bounds.get(mnemonic, (0, 0))
                if not (min_args <= param_arg_count <= max_args):
                    findings.append(LintFinding(
                        "aoi_call_arg_count_mismatch",
                        f"'{mnemonic}(' called with {param_arg_count} parameter argument(s) (plus the "
                        f"instance tag), but its declaration allows {min_args}..{max_args} "
                        f"(Required-count..Required-or-Visible-count non-hidden Input/Output params): "
                        f"{text.strip()!r}",
                    ))
                continue
            if mnemonic in _KNOWN_NATIVE_INSTRUCTIONS:
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
