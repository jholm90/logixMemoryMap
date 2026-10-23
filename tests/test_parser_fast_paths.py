"""The rung parser's fast paths return exactly what the character-by-character scans return.

The parser and lint read every rung through a few scanners, and each has a fast path for the
common shape (no argument nests a paren or bracket) in front of the original one-character-
at-a-time scan, which is kept as the reference and as the path for nested arguments. These
tests run both on hand-picked edge cases and on fuzzed rung text, at every position, and
compare. The per-rung helpers behind parse_rll_routines are compared the same way against the
original implementations, copied here verbatim.
"""

from __future__ import annotations

import random
import re

import l5x_memory_analyzer.parser.logic as L
import sample_gen.lint as lint

EDGE_CASES = [
    "", "(", ")", "()", "(,)", "( , )", "A(", "A()", "A(,)", "A(B", "A(B,", "A(B,C", "A(B)C(D)",
    "XIC(A)OTE(B);", "MOV(A[1,2],B);", "CPT(D,(A+B)*C);", "CMP(A>(B+1))OTE(C);", "JSR(R,2,A,B,C,D);",
    "Aoi(Inst,Src[i],Dst)", "Aoi(Inst,(A),B)", "Aoi(Inst,A]B,C)", "Aoi( )", "Aoi(A,)", "Aoi(A, ,B)",
    "[XIC(A),XIO(B)]OTE(C);", "[[XIC(A),XIC(B)],XIO(C)]OTE(D);", "XIC(Arr[Idx].3)OTE(B[I+1]);",
    "MOV(Arr[Stn.Idx],D)MOV(S.T[S.I+1],X);", "SBR();RET();", "SBR(A,B)RET(C);", "RET(,A,)",
    "OTE(A.[B])", "{A(B,C)}", "A({B,C},D)", "THRSe(A,B)", "Fn(A(B),C)", "Fn(A[B(C)],D)",
]
ALPHABET = "AB_1(),[]{}. +x"


def _fuzzed(n: int, seed: int = 20261023) -> list[str]:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        length = rnd.randint(0, 40)
        out.append("".join(rnd.choice(ALPHABET) for _ in range(length)))
    return out


TEXTS = EDGE_CASES + _fuzzed(4000)


def test_extract_call_args_fast_path_matches_the_scan():
    for text in TEXTS:
        for start in range(len(text) + 1):
            assert L._extract_call_args(text, start) == L._extract_call_args_scan(text, start), (text, start)


def test_split_call_args_fast_path_matches_the_scan():
    for text in TEXTS:
        for i in range(len(text) + 1):
            assert L._split_call_args(text, i) == L._split_call_args_scan(text, i), (text, i)


def test_lint_call_sites_fast_path_matches_the_scan():
    for text in TEXTS:
        expected = []
        for m in lint._INSTRUCTION_CALL.finditer(text):
            args = lint._call_args_scan(text, m.end())
            if args is not None:
                expected.append((m.group(1), args))
        assert lint._scan_call_sites(text) == expected, text
        assert lint._call_sites(text) == expected, text


def _split_top_level_args_reference(s: str) -> list[str]:
    s = s.strip()
    if not s:
        return []
    parts, depth, current = [], 0, []
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


def test_lint_split_top_level_args_matches_the_reference():
    for text in TEXTS:
        assert lint._split_top_level_args(text) == _split_top_level_args_reference(text), text


def _operand_refs_reference(rung_texts):
    refs = []
    for text in rung_texts:
        for m in L._INSTRUCTION_CALL.finditer(text):
            args = L._extract_call_args_scan(text, m.end())
            if args is None:
                continue
            mnemonic = m.group(1)
            outer = "bit" if mnemonic in L.BIT_INSTRUCTIONS else "word"
            for arg in args:
                depth = [0] * (len(arg) + 1)
                d = 0
                for i, ch in enumerate(arg):
                    if ch == "[":
                        d += 1
                    elif ch == "]":
                        d -= 1
                    depth[i] = d
                bare = outer == "word" and L._BARE_NAME.fullmatch(arg.strip()) is not None
                for root in L._OPERAND_ROOT.finditer(arg):
                    kind = "index" if depth[root.start()] > 0 else ("bare" if bare else outer)
                    refs.append((mnemonic, root.group(1), kind))
    return tuple(refs)


def _branch_bracket_reference(rung_texts):
    total = 0
    for text in rung_texts:
        i, n = 0, len(text)
        while i < n:
            if text[i] == "[" and not (i > 0 and (text[i - 1].isalnum() or text[i - 1] == "_")):
                group_total, next_i = L._parse_branch_group(text, i)
                total += group_total
                i = next_i
            else:
                i += 1
    return total


RUNGS = EDGE_CASES + [
    "".join(random.Random(seed).choice(["XIC(A)", "XIO(B[I])", "OTE(C.1)", "MOV(D,E[J+1])", "[", "]", ",",
                                        "CPT(F,G*H)", "CMP(K>L)", "JSR(Sub,1,M)", "RET(N)", "Aoi(I,P,Q)",
                                        "MOVE(R,S)", "TON(T,?,?)"]) for _ in range(12))
    for seed in range(1500)
] + _fuzzed(1500, seed=7)


def test_operand_refs_match_the_original_scan():
    for text in RUNGS:
        assert L._operand_refs([text]) == _operand_refs_reference([text]), text
    assert L._operand_refs(RUNGS) == _operand_refs_reference(RUNGS)


def test_branch_bracket_count_matches_the_original_scan():
    for text in RUNGS:
        assert L._branch_bracket_instruction_count([text]) == _branch_bracket_reference([text]), text


def _aoi_call_sites_reference(rung_texts, aoi_names, input_positions=None):
    if not aoi_names:
        return 0, 0, 0
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(n) for n in sorted(aoi_names, key=len, reverse=True)) + r")\(")
    calls = params = input_refs = 0
    for text in rung_texts:
        for match in pattern.finditer(text):
            calls += 1
            args = L._split_call_args_scan(text, match.end() - 1)[1:]
            params += len(args)
            if input_positions is None:
                continue
            for is_input, arg in zip(input_positions.get(match.group(1), ()), args):
                if is_input and not L._CHEAP_LITERAL.match(arg):
                    input_refs += 1
    return calls, params, input_refs


def test_aoi_call_sites_match_the_literal_name_alternation():
    """A call to a declared AOI is found from the rung's named calls, not from an
    alternation of every declared name; both find the same calls."""
    names_sets = [frozenset({"Aoi"}), frozenset({"Aoi", "AoiX", "A"}), frozenset({"MOVE", "XIC", "Sub"}),
                  frozenset({"B", "AB", "_1"})]
    positions = {"Aoi": (True, False, True), "A": (True,), "AoiX": (False, True), "B": (True, True)}
    for names in names_sets:
        for text in RUNGS:
            assert L.aoi_call_sites([text], names, positions) == _aoi_call_sites_reference([text], names, positions), (
                text, names)
        assert L.aoi_call_sites(RUNGS, names) == _aoi_call_sites_reference(RUNGS, names)


def test_parsed_routines_equal_the_per_helper_results():
    """parse_rll_routines builds each field from the cached per-rung facts; every field
    equals the helper it replaced, run over the routine's rungs."""
    import xml.etree.ElementTree as ET
    rungs = "".join(f"<Rung Number=\"{i}\" Type=\"N\"><Text><![CDATA[{t}]]></Text></Rung>"
                    for i, t in enumerate(r for r in RUNGS if r and "]]>" not in r))
    root = ET.fromstring(
        "<RSLogix5000Content><Controller><Programs><Program Name=\"P\"><Routines>"
        f"<Routine Name=\"R\" Type=\"RLL\"><RLLContent>{rungs}</RLLContent></Routine>"
        "</Routines></Program></Programs></Controller></RSLogix5000Content>")
    (routine,) = L.parse_rll_routines(root)
    texts = [L.canonical_rung_text(r) for r in RUNGS if r and "]]>" not in r]
    assert routine.instruction_counts == L._count_instructions(texts)
    assert list(routine.instruction_counts) == list(L._count_instructions(texts))
    assert routine.operand_refs == _operand_refs_reference(texts)
    assert routine.branch_bracket_instruction_count == _branch_bracket_reference(texts)
    assert routine.typed_calls == L._typed_instruction_calls(texts)
    assert routine.cpt_calls == L._cpt_calls(texts)
    assert routine.cmp_calls == L._cmp_calls(texts)
    assert routine.jsr_calls == L._jsr_calls(texts)
    assert routine.jsr_call_args == L.jsr_call_args(texts)
    assert routine.ret_operand_counts == L.ret_operand_counts(texts)
    assert routine.indirect_index_kinds == L._indirect_index_kinds(texts)
    assert routine.indirect_index_sites == L._indirect_index_sites(texts)
    assert routine.jsr_target_names == frozenset(L._jsr_targets(texts))
    assert routine.series_output_extras == L.series_output_extra_count(texts)
    assert routine.sbr_ret_operands == L.sbr_ret_operand_count(texts)


def test_case_selector_count_matches_the_regex():
    """structured_text counts CASE selectors in one pass; the regex it replaces backtracks
    without bound on long runs of words and whitespace. Same count on every input."""
    import l5x_memory_analyzer.sizing.structured_text as st
    rnd = random.Random(11)
    alphabet = ["A", "b", "1", "_", ".", ",", " ", "\t", "\n", "\r", ":", "=", ";", "(", "é", " ", "..",
                "CASE x OF", "1:", "2,3:", "4..6 :", "X := 1;", "ELSE", "END_CASE;"]
    texts = ["", ":", " :", "\n:", "a:=1", "a :", "\n\n  1:\n2:=3\n4 :"]
    texts += ["".join(rnd.choice(alphabet) for _ in range(rnd.randint(0, 30))) for _ in range(6000)]
    for text in texts:
        assert st.case_selector_count(text) == len(st._CASE_SELECTOR.findall(text)), repr(text)
