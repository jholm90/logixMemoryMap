import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.logic import parse_rll_routines
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.logic import compute_routine_logic_bytes
from l5x_memory_analyzer.sizing.report import ESTIMATED, EXACT, build_report

MODEL = load_memory_model()

_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <DataTypes/>
    <AddOnInstructionDefinitions/>
    <Tags>
      <Tag Name="A" TagType="Base" DataType="BOOL"/>
      <Tag Name="B" TagType="Base" DataType="BOOL"/>
    </Tags>
    <Programs>
      <Program Name="MainProgram">
        <Tags/>
        <Routines>
          <Routine Name="MainRoutine" Type="RLL">
            <RLLContent>
              <Rung Number="0" Type="N"><Text><![CDATA[XIC(A)OTE(B);]]></Text></Rung>
              <Rung Number="1" Type="N"><Text><![CDATA[XIC(A)XIC(B)OTE(A);]]></Text></Rung>
            </RLLContent>
          </Routine>
          <Routine Name="StRoutine" Type="ST">
            <STContent/>
          </Routine>
        </Routines>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>
"""


def test_parse_rll_routines_counts_instructions_and_skips_st():
    root = ET.fromstring(_XML)
    routines = parse_rll_routines(root)

    assert len(routines) == 1  # StRoutine (Type="ST") is skipped entirely
    routine = routines[0]
    assert routine.program_name == "MainProgram"
    assert routine.routine_name == "MainRoutine"
    assert routine.rung_count == 2
    # Rung 0: XIC x1, OTE x1. Rung 1: XIC x2, OTE x1. Total: XIC=3, OTE=2.
    assert routine.instruction_counts == {"XIC": 3, "OTE": 2}


def test_compute_routine_logic_bytes_sums_weights_plus_fixed_base():
    root = ET.fromstring(_XML)
    routine = parse_rll_routines(root)[0]
    bytes_, confidence = compute_routine_logic_bytes(routine, MODEL.logic_instructions)

    # fixed_base(4816) + XIC(4)*3 + OTE(16)*2 = 4816 + 12 + 32 = 4860
    # (XIC's isolated weight is 4, not the raw 20 -- that raw number was
    # XIC+its-own-test-file's-companion-OTE combined, decomposed 2026-08-22)
    assert bytes_ == 4816 + 4 * 3 + 16 * 2
    assert confidence == "FITTED"


def test_build_report_includes_estimated_logic_entries():
    root = ET.fromstring(_XML)
    entries, errors = build_report(root, MODEL)
    assert errors == []

    logic_entries = [e for e in entries if e.tier == ESTIMATED]
    assert len(logic_entries) == 1
    logic_entry = logic_entries[0]
    assert logic_entry.path == "program:MainProgram/MainRoutine"
    assert logic_entry.category == "routine_logic"
    assert logic_entry.bytes == 4816 + 4 * 3 + 16 * 2
    assert logic_entry.basis == "FITTED"

    # Exact-tier tag entries are untouched by the logic addition, still
    # their own tier, and total_bytes/pct_of_total now includes logic too.
    exact_entries = [e for e in entries if e.tier == EXACT]
    assert len(exact_entries) == 3  # tags A, B + project_baseline (2026-08-23)
    total = sum(e.bytes for e in entries)
    for e in entries:
        assert e.pct_of_total == (e.bytes / total) * 100


def test_paired_instruction_weights_dont_double_count_companion_instruction():
    # Regression test for the 2026-08-22 fix: gen_logic_sweep.py's XIC test
    # file's rung text is "XIC(tag)OTE(tag);", not "XIC(tag);" alone (a
    # bare XIC can't legally close a rung). Before the fix, this engine
    # summed the raw (uncorrected) XIC weight AND the raw OTE weight for
    # every rung, double-counting OTE's contribution -- caught by cross-
    # checking against real captured Capacity data for instr_xic_n01000
    # (engine said 40,816; real delta was 24,816).
    xml = """
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test">
        <DataTypes/>
        <AddOnInstructionDefinitions/>
        <Tags>
          <Tag Name="B0" TagType="Base" DataType="BOOL"/>
          <Tag Name="B1" TagType="Base" DataType="BOOL"/>
        </Tags>
        <Programs>
          <Program Name="P">
            <Tags/>
            <Routines>
              <Routine Name="R" Type="RLL">
                <RLLContent>
                  <Rung Number="0" Type="N"><Text><![CDATA[XIC(B0)OTE(B1);]]></Text></Rung>
                </RLLContent>
              </Routine>
            </Routines>
          </Program>
        </Programs>
      </Controller>
    </RSLogix5000Content>
    """
    root = ET.fromstring(xml)
    routine = parse_rll_routines(root)[0]
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    # Real Capacity-tab delta for 1000 such rungs is exactly 4816 + 20*1000
    # = 24,816 -- i.e. 20 blocks/rung for the WHOLE "XIC(tag)OTE(tag);"
    # rung, matching XIC_alone(4) + OTE_alone(16) = 20 per rung once
    # decomposed correctly, not 20+16=36.
    per_rung_marginal = bytes_ - MODEL.logic_instructions.fixed_base_per_routine
    assert per_rung_marginal == 20


def test_jsr_target_routine_not_double_counted():
    # Regression test for the 2026-08-22 fix: a JSR target routine's own
    # cost is already folded into the caller's jsr_fixed_base_per_routine
    # constant (confirmed against real data for instr_jsr_n*.L5X -- the
    # target's content stayed fixed across the whole calibration sweep, so
    # its cost got absorbed into that constant rather than needing its own
    # separate charge). Before this fix the engine also charged SubTest its
    # own full fixed_base_per_routine, overcounting every JSR-using program.
    xml = """
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test">
        <DataTypes/>
        <AddOnInstructionDefinitions/>
        <Tags/>
        <Programs>
          <Program Name="MainProgram">
            <Tags/>
            <Routines>
              <Routine Name="MainRoutine" Type="RLL">
                <RLLContent>
                  <Rung Number="0" Type="N"><Text><![CDATA[JSR(SubTest,0);]]></Text></Rung>
                </RLLContent>
              </Routine>
              <Routine Name="SubTest" Type="RLL">
                <RLLContent>
                  <Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>
                </RLLContent>
              </Routine>
            </Routines>
          </Program>
        </Programs>
      </Controller>
    </RSLogix5000Content>
    """
    root = ET.fromstring(xml)
    routines = parse_rll_routines(root)
    by_name = {r.routine_name: r for r in routines}
    assert by_name["SubTest"].is_jsr_target is True
    assert by_name["MainRoutine"].is_jsr_target is False
    # Phase 5 call-tree UI (2026-08-27): jsr_target_names captures WHICH
    # routine(s) THIS routine calls, distinct from is_jsr_target (which
    # only says whether some other routine calls this one).
    assert by_name["MainRoutine"].jsr_target_names == frozenset({"SubTest"})
    assert by_name["SubTest"].jsr_target_names == frozenset()

    entries, errors = build_report(root, MODEL)
    assert errors == []
    logic_entries = [e for e in entries if e.tier == ESTIMATED]
    # Only MainRoutine gets an entry -- SubTest is skipped entirely, not
    # charged its own fixed_base on top of the caller's jsr_fixed_base.
    assert len(logic_entries) == 1
    assert logic_entries[0].path == "program:MainProgram/MainRoutine"
    # jsr_fixed_base_per_routine(5096) + JSR's own weight(72)*1 = 5168
    assert logic_entries[0].bytes == 5096 + 72


# ---------------------------------------------------------------------------
# CPT expression-aware cost -- 2026-08-26, OQ-CMPCPTLAYOUT. CPT is
# deliberately absent from the flat `weights` table now (real data: its
# cost is expression-complexity-dependent, not a flat per-call constant);
# these confirm the dedicated parser+cost_for path replaces it exactly.
# ---------------------------------------------------------------------------

def _one_rung_routine(rung_text: str):
    xml = f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test">
        <DataTypes/>
        <AddOnInstructionDefinitions/>
        <Tags/>
        <Programs>
          <Program Name="MainProgram">
            <Tags/>
            <Routines>
              <Routine Name="MainRoutine" Type="RLL">
                <RLLContent>
                  <Rung Number="0" Type="N"><Text><![CDATA[{rung_text}]]></Text></Rung>
                </RLLContent>
              </Routine>
            </Routines>
          </Program>
        </Programs>
      </Controller>
    </RSLogix5000Content>
    """
    root = ET.fromstring(xml)
    return parse_rll_routines(root)[0]


def test_cpt_parser_extracts_flat_operator_tokens():
    routine = _one_rung_routine("CPT(Dest,L0+L1*L2);")
    assert routine.cpt_calls == [["+", "*"]]


def test_cpt_parser_handles_nested_parens_and_multiple_calls():
    routine = _one_rung_routine("CPT(D1,(L0+L1)*(L2-L3))CPT(D2,L4);")
    assert routine.cpt_calls == [["+", "*", "-"], []]


def test_cpt_parser_recognizes_pow_and_word_mod():
    routine = _one_rung_routine("CPT(Dest,L0**L1 MOD L2);")
    assert routine.cpt_calls == [["**", "MOD"]]


def test_cpt_bare_copy_costs_base_read_only():
    routine = _one_rung_routine("CPT(Dest,L0);")
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.cpt_expression.base_read


def test_cpt_uniform_chain_matches_confirmed_real_formula():
    # cptcx_operandcount real data (n=1 rung, single ADD chain): confirmed
    # exact base(88) + 36 (1st operator) + 24/extra operator thereafter.
    model = MODEL.logic_instructions
    cases = {
        1: 0,        # bare copy, no operator -- handled by the base_read branch
        2: 36,
        3: 36 + 24,
        4: 36 + 24 * 2,
        6: 36 + 24 * 4,
        10: 36 + 24 * 8,
    }
    for operand_count, expected_operator_cost in cases.items():
        operators = ["+"] * (operand_count - 1)
        assert model.cpt_expression.cost_for(operators) == 88 + expected_operator_cost


def test_cpt_t1_t2_mix_matches_confirmed_real_formula():
    # gen_cpt_mixed_operators.py's real operand-count sweep, 2026-08-26:
    # a T1(ADD/SUB)+T2(MUL/DIV/MOD)-only mix is exact at 100+32*operators
    # for 3/5/11/15 operators (4/5 real points, k=7 off by small noise).
    # "+","-","*" is exactly this tier set (2 operators).
    model = MODEL.logic_instructions
    assert model.cpt_expression.cost_for(["+", "-", "*"]) == 100 + 32 * 3


def test_cpt_other_mixed_tiers_fall_back_to_additive_sum():
    # Any mix involving POW (T3) alongside another tier isn't the solved
    # T1T2 special case -- still the real-but-approximate additive sum
    # (see memory_model.yaml cpt_expression's "Mixed-tier" note: real
    # data shows T1T3/T2T3 pairs have their own different, not-yet-fully-
    # characterized behavior, not force-fit into this fallback as if
    # confirmed).
    model = MODEL.logic_instructions
    assert model.cpt_expression.cost_for(["+", "**"]) == 88 + 36 + 116


def test_cpt_costed_per_call_not_via_flat_weights_table():
    assert "CPT" not in MODEL.logic_instructions.weights
    routine = _one_rung_routine("CPT(Dest,L0+L1+L2);")
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    # fixed_base_per_routine + base_read(88) + ADD tier(36) + 1 extra operand(24)
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + 88 + 36 + 24


# ---------------------------------------------------------------------------
# Operand-type surcharge -- 2026-08-26, OQ-OPERANDTYPE. Confirmed via the
# real typesweep_* corpus (69 captures, error_count=0): SINT/INT/REAL/
# STRING operands cost more than DINT/LINT for a wide instruction set.
# ---------------------------------------------------------------------------

def test_parser_extracts_typed_call_operands():
    routine = _one_rung_routine("ADD(TD0,TD1,TD2);")
    assert routine.typed_calls == [("ADD", ["TD0", "TD1", "TD2"])]


def test_typed_call_still_counted_in_instruction_counts_too():
    routine = _one_rung_routine("ADD(TD0,TD1,TD2);")
    assert routine.instruction_counts == {"ADD": 1}


def test_operand_type_surcharge_applies_on_top_of_base_weight():
    routine = _one_rung_routine("ADD(TS0,TS1,TS2);")
    tag_types = {"TS0": "SINT", "TS1": "SINT", "TS2": "SINT"}
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions, tag_types)
    # fixed_base + ADD's base DINT-rate weight(40) + SINT surcharge(132)
    add_weight = MODEL.logic_instructions.weights["ADD"]
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + add_weight + 132


def test_operand_type_surcharge_zero_for_dint_and_lint():
    routine_dint = _one_rung_routine("ADD(TD0,TD1,TD2);")
    routine_lint = _one_rung_routine("ADD(TL0,TL1,TL2);")
    tag_types = {"TD0": "DINT", "TD1": "DINT", "TD2": "DINT", "TL0": "LINT", "TL1": "LINT", "TL2": "LINT"}
    dint_bytes, _ = compute_routine_logic_bytes(routine_dint, MODEL.logic_instructions, tag_types)
    lint_bytes, _ = compute_routine_logic_bytes(routine_lint, MODEL.logic_instructions, tag_types)
    assert dint_bytes == lint_bytes == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.weights["ADD"]


def test_operand_type_surcharge_no_tag_types_is_a_noop():
    # No tag_types supplied (default None) -- same behavior as before this
    # feature existed, not a crash.
    routine = _one_rung_routine("ADD(TS0,TS1,TS2);")
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.weights["ADD"]


def test_operand_type_surcharge_ignores_member_and_array_operands():
    # Neither "Udt.Member" nor "Arr[0]" is a bare tag -- deliberately NOT
    # resolved (see memory_model.yaml operand_type_surcharge), falls back
    # to the base DINT-rate weight rather than guessing.
    routine = _one_rung_routine("ADD(Udt.Member,Arr[0],Dest);")
    tag_types = {"Udt": "SomeUdt", "Arr": "SINT", "Dest": "DINT"}
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions, tag_types)
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.weights["ADD"]


def test_operand_type_surcharge_string_and_lim_negative_real():
    # EQU+STRING and LIM+REAL are the two "unusual" real data points: a
    # STRING-specific surcharge, and the only case where a non-DINT type
    # costs LESS than DINT, not more.
    equ_routine = _one_rung_routine("EQU(TS0,TS1);")
    lim_routine = _one_rung_routine("LIM(TR0,TR1,TR2);")
    equ_bytes, _ = compute_routine_logic_bytes(
        equ_routine, MODEL.logic_instructions, {"TS0": "STRING", "TS1": "STRING"}
    )
    lim_bytes, _ = compute_routine_logic_bytes(
        lim_routine, MODEL.logic_instructions, {"TR0": "REAL", "TR1": "REAL", "TR2": "REAL"}
    )
    assert equ_bytes == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.weights["EQU"] + 52
    assert lim_bytes == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.weights["LIM"] - 8


# ---------------------------------------------------------------------------
# Indirect (tag-driven) array-index cost -- 2026-08-26, OQ-INDIRECT.
# Confirmed KNOWN: exact across 4 real count points (10/50/100/1000) each
# for a plain tag index and a tag+literal-offset index.
# ---------------------------------------------------------------------------

def test_direct_literal_index_costs_nothing_extra():
    routine = _one_rung_routine("MOV(Arr[5],Dest);")
    assert routine.indirect_index_kinds == []
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.weights["MOV"]


def test_tag_driven_index_parsed_and_costed():
    routine = _one_rung_routine("MOV(Arr[Idx],Dest);")
    assert routine.indirect_index_kinds == ["tag"]
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.weights["MOV"] + 84


def test_tag_driven_offset_index_parsed_and_costed():
    routine = _one_rung_routine("MOV(Arr[Idx+1],Dest);")
    assert routine.indirect_index_kinds == ["tag_offset"]
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + MODEL.logic_instructions.weights["MOV"] + 108


def test_unresolvable_index_shape_costs_nothing_not_guessed():
    # Two tags inside the bracket -- not a shape any real capture confirms,
    # deliberately left uncosted rather than guessed at.
    routine = _one_rung_routine("MOV(Arr[Idx+Offset],Dest);")
    assert routine.indirect_index_kinds == []


# ---------------------------------------------------------------------------
# CMP compound-condition/float-literal surcharge -- 2026-08-26. CMP:76
# confirmed exact for a single condition; compound (&&/||) and float-
# literal conditions cost real, additional, previously-unwired amounts.
# ---------------------------------------------------------------------------

def test_cmp_single_condition_costs_base_weight_only():
    routine = _one_rung_routine("CMP(L0>L1)OTE(TB0);")
    assert routine.cmp_calls == [(False, False)]
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    ote_weight = MODEL.logic_instructions.weights["OTE"]
    cmp_weight = MODEL.logic_instructions.weights["CMP"]
    assert cmp_weight == 76
    assert bytes_ == MODEL.logic_instructions.fixed_base_per_routine + cmp_weight + ote_weight


def test_cmp_compound_condition_adds_surcharge():
    for expr in ["L0>L1&&(L2<L3)", "L0>L1||(L2<L3)", "L0>L1&&(L0>L1)"]:
        routine = _one_rung_routine(f"CMP({expr})OTE(TB0);")
        assert routine.cmp_calls == [(True, False)]
        bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
        base = (
            MODEL.logic_instructions.fixed_base_per_routine
            + MODEL.logic_instructions.weights["CMP"]
            + MODEL.logic_instructions.weights["OTE"]
        )
        assert bytes_ == base + 64


def test_cmp_float_literal_adds_surcharge_int_literal_does_not():
    float_routine = _one_rung_routine("CMP(L0>5.5)OTE(TB0);")
    int_routine = _one_rung_routine("CMP(L0>5)OTE(TB0);")
    assert float_routine.cmp_calls == [(False, True)]
    assert int_routine.cmp_calls == [(False, False)]
    base = (
        MODEL.logic_instructions.fixed_base_per_routine
        + MODEL.logic_instructions.weights["CMP"]
        + MODEL.logic_instructions.weights["OTE"]
    )
    float_bytes, _ = compute_routine_logic_bytes(float_routine, MODEL.logic_instructions)
    int_bytes, _ = compute_routine_logic_bytes(int_routine, MODEL.logic_instructions)
    assert float_bytes == base + 72
    assert int_bytes == base
