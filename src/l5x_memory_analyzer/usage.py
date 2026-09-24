"""Where every tag, member, routine, module and type member is USED.

The treemap says how much memory a thing costs; this says whether anything
reads or writes it. An array nobody indexes, a UDT member no rung touches, a
routine nothing calls -- those are the memory a project can get back.

What counts as a use, all read from the one L5X:

  * every operand in ladder rung text, Structured Text and FBD/SFC operand
    attributes, resolved in the routine's own scope (program tags first, then
    controller tags) -- including the tags inside an array subscript;
  * an alias tag's target, an alarm condition's watched input and associated
    tags, an axis's motion group and its drive module;
  * inside an Add-On Instruction's own logic, its parameters and local tags;
  * a JSR's target routine, and a program's main routine;
  * a module I/O reference (`Rack:1:I.Data.0`).

What cannot be seen from an L5X: HMI and SCADA access, and messages from other
controllers. A tag with no use here may still be read over the network, which
is why the UI says "no references in this project" rather than "unused
memory you can delete".

Counting is by path. A use of `Tag.A.B` is a use of `Tag`, of `Tag.A` and of
`Tag.A.B`. An array subscript that is not a literal (`Arr[Idx]`) is a use of
every element. A reference that stops at a structure -- a COP source, an AOI
InOut argument, a whole UDT moved as one -- uses every member under it; those
are reported as "used via its parent" rather than counted, so a member that is
only ever copied as part of its parent is not called unused. A file
instruction (COP, FLL, FAL, ...) on one array element touches the elements after
it too, so it marks the whole array.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

CONTROLLER_SCOPE = "controller"

# Instructions whose array operand is a starting element of a run of elements.
_FILE_INSTRUCTIONS = frozenset({
    "COP", "CPS", "FLL", "FAL", "FSC", "FFL", "FFU", "LFL", "LFU", "BSL", "BSR",
    "AVE", "SRT", "STD", "SIZE", "DDT", "FBC", "SQI", "SQO", "SQL", "FOR",
})

_MODULE_REF = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*):(?:\d+:)?[IOCS]\b")
_HEX_LITERAL = re.compile(r"\b\d+#[0-9A-Fa-f_]+")
_ST_COMMENT = re.compile(r"\(\*.*?\*\)|//[^\n]*|/\*.*?\*/", re.S)
_ST_STRING = re.compile(r"'[^']*'|\"[^\"]*\"")
_BRACKET = r"\[(?:[^\[\]]|\[[^\[\]]*\])*\]"
_PATH = re.compile(
    r"(?<![A-Za-z0-9_.:#])([A-Za-z_][A-Za-z0-9_]*)((?:" + _BRACKET + r"|\.[A-Za-z0-9_]+)*)(?![A-Za-z0-9_\[.]|\s*\()"
)
_SEGMENT = re.compile(_BRACKET + r"|\.[A-Za-z0-9_]+")
_CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_LITERAL_INDEX = re.compile(r"^\s*\d+(\s*,\s*\d+)*\s*$")

WILD = "[*]"

# Members no program names directly: an AOI's own enable pair, and the hidden
# SINT a UDT's BOOL members are packed into.
SYSTEM_MEMBERS = frozenset({"EnableIn", "EnableOut"})
HIDDEN_MEMBER_PREFIX = "ZZZZZZZZZZ"


def _segments(tail: str) -> tuple[list[str], list[str]]:
    """('.A[3].B[Idx]') -> (['.A', '[3]', '.B', '[*]'], ['Idx']) -- the
    normalised path and the text of every non-literal subscript."""
    segs: list[str] = []
    inner: list[str] = []
    for s in _SEGMENT.findall(tail):
        if s.startswith("["):
            body = s[1:-1]
            if _LITERAL_INDEX.match(body):
                segs.append("[" + ",".join(p.strip() for p in body.split(",")) + "]")
            else:
                segs.append(WILD)
                inner.append(body)
        else:
            segs.append(s)
    return segs, inner


@dataclass
class _Node:
    n: int = 0          # uses that pass through this node (or end here)
    end: int = 0        # uses that stop exactly here: the whole thing, as one
    kids: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Usage:
    """How often something is used.

    count: direct uses. via_parent: used only as part of its parent (a whole
    structure or array referenced as one). implicit: used by the AOI's own
    logic on every call (an AOI instance member).
    """
    count: int
    via_parent: bool = False
    implicit: int = 0

    @property
    def unused(self) -> bool:
        return self.count == 0 and not self.via_parent and self.implicit == 0

    def as_json(self) -> dict:
        return {"count": self.count, "via_parent": self.via_parent, "implicit": self.implicit}


class UsageIndex:
    def __init__(self, root: ET.Element) -> None:
        self._root = root
        controller = root.find("Controller") if root.tag != "Controller" else root
        self._controller = controller
        # Declarations: scope -> {tag name -> (data type, dims)} and aliases.
        self._types: dict[str, dict[str, tuple[str, str]]] = {}
        self._aliases: dict[str, dict[str, str]] = {}
        self._members: dict[str, dict[str, tuple[str, str]]] = {}
        self._aoi_names: set[str] = set()
        self._tries: dict[str, _Node] = {}
        self._type_member: dict[tuple[str, str], int] = {}
        self._type_whole: dict[str, int] = {}
        self._aoi_internal: dict[tuple[str, str], int] = {}
        self._aoi_calls: dict[str, int] = {}
        self._routine_calls: dict[str, int] = {}
        self._main_routines: set[str] = set()
        self._modules: dict[str, int] = {}
        self._routines: dict[str, set[str]] = {}
        self._declare()
        self._scan()

    # ---- declarations ---------------------------------------------------

    def _declare(self) -> None:
        root = self._root
        for dt in root.iter("DataType"):
            self._members[dt.get("Name")] = {
                m.get("Name"): (m.get("DataType"), m.get("Dimension") or "0")
                for m in dt.iter("Member")}
        for aoi in root.iter("AddOnInstructionDefinition"):
            name = aoi.get("Name")
            self._aoi_names.add(name)
            own = {p.get("Name"): (p.get("DataType"), p.get("Dimensions") or "0")
                   for p in aoi.iter("Parameter")}
            own.update({t.get("Name"): (t.get("DataType"), t.get("Dimensions") or "0")
                        for t in aoi.iter("LocalTag")})
            self._members[name] = own
        for k, v in {"TIMER": ("PRE", "ACC", "EN", "TT", "DN"),
                     "COUNTER": ("PRE", "ACC", "CU", "CD", "DN", "OV", "UN"),
                     "CONTROL": ("LEN", "POS", "EN", "EU", "DN", "EM", "ER", "UL", "IN", "FD")}.items():
            self._members.setdefault(k, {m: ("DINT" if m in ("PRE", "ACC", "LEN", "POS") else "BOOL", "0")
                                         for m in v})
        if self._controller is None:
            return
        self._declare_scope(CONTROLLER_SCOPE, self._controller)
        for program in self._controller.iter("Program"):
            scope = f"program:{program.get('Name')}"
            self._declare_scope(scope, program)
            self._routines[scope] = {r.get("Name") for r in program.iter("Routine")}
            main = program.get("MainRoutineName")
            if main:
                self._main_routines.add(f"{scope}/{main}")

    def _declare_scope(self, scope: str, container: ET.Element) -> None:
        tags = container.find("Tags")
        types, aliases = {}, {}
        if tags is not None:
            for t in tags.findall("Tag"):
                if t.get("TagType") == "Alias" and t.get("AliasFor"):
                    aliases[t.get("Name")] = t.get("AliasFor")
                types[t.get("Name")] = (t.get("DataType") or "", t.get("Dimensions") or "0")
        self._types[scope] = types
        self._aliases[scope] = aliases

    # ---- recording ------------------------------------------------------

    def _resolve(self, scope: str, base: str) -> str | None:
        if scope != CONTROLLER_SCOPE and base in self._types.get(scope, {}):
            return scope
        if base in self._types.get(CONTROLLER_SCOPE, {}):
            return CONTROLLER_SCOPE
        return None

    def _record(self, scope: str, base: str, segs: list[str], depth: int = 0) -> None:
        owner = self._resolve(scope, base)
        if owner is None:
            return
        key = f"{owner}/{base}"
        node = self._tries.setdefault(key, _Node())
        node.n += 1
        for s in segs:
            node = node.kids.setdefault(s, _Node())
            node.n += 1
        node.end += 1
        # Type members, for the definition view.
        dtype, dims = self._types[owner][base]
        cur = dtype
        for s in segs:
            if s.startswith("["):
                continue
            member = s[1:]
            if member.isdigit() or cur not in self._members:
                cur = None
                break
            self._type_member[(cur, member)] = self._type_member.get((cur, member), 0) + 1
            cur = self._members[cur].get(member, (None,))[0]
        if cur in self._members:
            self._type_whole[cur] = self._type_whole.get(cur, 0) + 1
        # An alias is a use of what it points at.
        alias = self._aliases.get(owner, {}).get(base)
        if alias and depth < 8:
            self._record_text(owner, alias + "".join(segs), depth + 1)

    def _record_text(self, scope: str, text: str, depth: int = 0) -> None:
        """Every operand path in one piece of logic text, in one scope."""
        for m in _MODULE_REF.finditer(text):
            self._modules[m.group(1)] = self._modules.get(m.group(1), 0) + 1
        text = _MODULE_REF.sub(" ", text)
        text = _HEX_LITERAL.sub(" ", text)
        for m in _PATH.finditer(text):
            segs, inner = _segments(m.group(2))
            self._record(scope, m.group(1), segs, depth)
            for body in inner:
                self._record_text(scope, body, depth)

    def _record_file_instructions(self, scope: str, text: str) -> None:
        """COP(Arr[0],...) touches the elements after [0] too: a whole-array use."""
        for m in _CALL.finditer(text):
            if m.group(1) not in _FILE_INSTRUCTIONS:
                continue
            for arg in _args(text, m.end()):
                pm = _PATH.match(arg.strip())
                if not pm:
                    continue
                segs, _ = _segments(pm.group(2))
                if segs and segs[-1].startswith("["):
                    owner = self._resolve(scope, pm.group(1))
                    if owner is None:
                        continue
                    node = self._tries.setdefault(f"{owner}/{pm.group(1)}", _Node())
                    for s in segs[:-1]:
                        node = node.kids.setdefault(s, _Node())
                    node.end += 1

    def _scan_logic(self, scope: str, container: ET.Element, routine_scope: str | None = None) -> None:
        for routine in container.iter("Routine"):
            texts: list[str] = [t.text or "" for t in routine.iter("Text")]
            texts += [_ST_STRING.sub(" ", _ST_COMMENT.sub(" ", ln.text or "")) for ln in routine.iter("Line")]
            texts += [el.get("Operand") for el in routine.iter() if el.get("Operand")]
            for text in texts:
                self._record_text(scope, text)
                self._record_file_instructions(scope, text)
                for m in _CALL.finditer(text):
                    name = m.group(1)
                    if name in self._aoi_names:
                        self._aoi_calls[name] = self._aoi_calls.get(name, 0) + 1
                    elif name == "JSR" and routine_scope:
                        args = _args(text, m.end())
                        if args:
                            target = f"{routine_scope}/{args[0].strip()}"
                            self._routine_calls[target] = self._routine_calls.get(target, 0) + 1

    def _scan(self) -> None:
        if self._controller is None:
            return
        for program in self._controller.iter("Program"):
            scope = f"program:{program.get('Name')}"
            self._scan_logic(scope, program, routine_scope=scope)
        for aoi in self._root.iter("AddOnInstructionDefinition"):
            name = aoi.get("Name")
            for routine in aoi.iter("Routine"):
                texts = [t.text or "" for t in routine.iter("Text")]
                texts += [_ST_STRING.sub(" ", _ST_COMMENT.sub(" ", ln.text or "")) for ln in routine.iter("Line")]
                for text in texts:
                    for m in _PATH.finditer(_HEX_LITERAL.sub(" ", text)):
                        if m.group(1) in self._members[name]:
                            k = (name, m.group(1))
                            self._aoi_internal[k] = self._aoi_internal.get(k, 0) + 1
                            self._type_member[k] = self._type_member.get(k, 0) + 1
        # Non-logic references: alias targets, alarms, motion.
        for scope, container in [(CONTROLLER_SCOPE, self._controller)] + [
                (f"program:{p.get('Name')}", p) for p in self._controller.iter("Program")]:
            tags = container.find("Tags")
            if tags is None:
                continue
            for t in tags.findall("Tag"):
                name = t.get("Name")
                for cond in t.iter("AlarmCondition"):
                    if cond.get("Input") is not None:
                        segs, _ = _segments(cond.get("Input"))
                        self._record(scope, name, segs)
                    for k, v in cond.attrib.items():
                        if k.startswith("AssocTag") and v:
                            self._record_text(scope, v)
                for ap in t.iter("AxisParameters"):
                    if ap.get("MotionGroup"):
                        self._record(scope, ap.get("MotionGroup"), [])
                    mod = (ap.get("MotionModule") or "").split(":")[0]
                    if mod and mod != "<NA>":
                        self._modules[mod] = self._modules.get(mod, 0) + 1
                if t.get("TagType") == "Alias" and t.get("AliasFor"):
                    alias_for = t.get("AliasFor")
                    mm = _MODULE_REF.match(alias_for)
                    if mm:
                        self._modules[mm.group(1)] = self._modules.get(mm.group(1), 0) + 1
                if t.get("TagType") in ("Produced", "Consumed"):
                    self._record(scope, name, [])

    # ---- queries --------------------------------------------------------

    def tag(self, tag_path: str, segments: list[str] | tuple[str, ...] = ()) -> Usage | None:
        """Uses of a tag (`controller/Name`, `program:P/Name`) or of a member
        or element below it (segments like '.Member', '[3]')."""
        last = segments[-1] if segments else ""
        if last.startswith(".") and (last[1:] in SYSTEM_MEMBERS or last[1:].startswith(HIDDEN_MEMBER_PREFIX)):
            return None
        root = self._tries.get(tag_path)
        implicit = self._aoi_instance_implicit(tag_path, segments, root)
        if root is None:
            return Usage(0, implicit=implicit)
        frontier = [root]
        via_parent = False
        for s in segments:
            if any(node.end for node in frontier):
                via_parent = True
            nxt = []
            for node in frontier:
                if s in node.kids:
                    nxt.append(node.kids[s])
                if s.startswith("[") and WILD in node.kids and s != WILD:
                    nxt.append(node.kids[WILD])
            frontier = nxt
            if not frontier:
                break
        return Usage(sum(node.n for node in frontier), via_parent=via_parent, implicit=implicit)

    def _aoi_instance_implicit(self, tag_path, segments, root) -> int:
        """An AOI instance's parameter is used by the AOI's own logic every
        time that instance is called."""
        if len(segments) != 1 or not segments[0].startswith(".") or root is None or root.n == 0:
            return 0
        scope, _, base = tag_path.partition("/")
        dtype = self._types.get(scope, {}).get(base, ("",))[0]
        if dtype not in self._aoi_names:
            return 0
        return self._aoi_internal.get((dtype, segments[0][1:]), 0)

    def type_member(self, type_name: str, member: str) -> Usage | None:
        """Uses of one member of a UDT or AOI, across every instance, by name.

        A member counts only where logic names it. One that is only ever
        copied along with its whole structure (COP of the UDT) is still
        reported unused here -- nothing reads it -- and `copied_whole` says
        so. None for what no program can use by name: an AOI's EnableIn /
        EnableOut, and the hidden SINT Logix packs BOOL members into."""
        if member in SYSTEM_MEMBERS or member.startswith(HIDDEN_MEMBER_PREFIX):
            return None
        return Usage(self._type_member.get((type_name, member), 0))

    def has_member(self, type_name: str, member: str) -> bool:
        return member in self._members.get(type_name, {})

    def copied_whole(self, type_name: str) -> bool:
        return self._type_whole.get(type_name, 0) > 0

    def type_instances(self, type_name: str) -> int:
        """Tags declared with this type, plus members of other types declared
        with it -- a UDT used only nested inside another UDT is still used."""
        tags = sum(1 for types in self._types.values() for dt, _ in types.values() if dt == type_name)
        nested = sum(1 for owner, members in self._members.items() if owner != type_name
                     for dt, _ in members.values() if dt == type_name)
        return tags + nested

    def aoi_calls(self, name: str) -> int:
        return self._aoi_calls.get(name, 0)

    def is_routine(self, path: str) -> bool:
        scope, _, name = path.partition("/")
        return name in self._routines.get(scope, set())

    def routine(self, routine_path: str) -> Usage:
        calls = self._routine_calls.get(routine_path, 0)
        return Usage(calls, implicit=1 if routine_path in self._main_routines else 0)

    def module(self, name: str) -> Usage:
        return Usage(self._modules.get(name, 0))


def _args(text: str, start: int) -> list[str]:
    depth, args, arg_start = 1, [], start
    for i in range(start, len(text)):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                args.append(text[arg_start:i])
                return args
        elif c == "," and depth == 1:
            args.append(text[arg_start:i])
            arg_start = i + 1
    return args


def segments_of(subpath: str) -> list[str]:
    """'.A[3].B' -> ['.A', '[3]', '.B'] (the form /api/node's subpath uses)."""
    return _segments(subpath)[0]
