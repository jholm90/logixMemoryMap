import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.logic import parse_rll_routines
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.logic import compute_routine_logic_bytes
from l5x_memory_analyzer.sizing.report import ESTIMATED, EXACT, build_report

MODEL = load_memory_model()
# Read from the model, never restated here as a literal. These assertions
# used to hardcode 47; when the composite surcharge was refitted on 9 real
# programs (20/47 -> 52/21, 2026-09-04) three tests failed for asserting a
# constant's VALUE rather than that it is APPLIED ONCE PER JSR-target
# instruction, which is the behaviour they exist to pin. See CLAUDE.md:
# never hardcode a byte size where a named constant from the model will do.
_JSR_SURCHARGE = MODEL.logic_instructions.jsr_target_composite_surcharge_per_instr

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

    # StRoutine (Type="ST") is skipped entirely by the RLL parser -- but it
    # is no longer skipped SILENTLY: see
    # test_build_report_reports_non_rll_routine_as_a_coverage_gap below.
    assert len(routines) == 1
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
    # The only error is the ST coverage gap asserted on in its own test
    # below; nothing here should fail to size.
    assert [e.path for e in errors] == ["coverage/routine_type/ST"]

    # 2026-08-27, Task/Program/Routine shell decomposition: a single plain
    # routine's fixed_base_per_routine is now a separate "SHELL" entry
    # (charged once per file, see report.py/memory_model.yaml
    # task_program_overhead) rather than baked into the routine's own
    # entry -- same total, two entries instead of one.
    logic_entries = [e for e in entries if e.tier == ESTIMATED]
    assert len(logic_entries) == 2
    routine_entry = next(e for e in logic_entries if e.data_type == "RLL")
    shell_entry = next(e for e in logic_entries if e.data_type == "SHELL")
    assert routine_entry.path == "program:MainProgram/MainRoutine"
    assert routine_entry.category == "routine_logic"
    assert routine_entry.bytes == 4 * 3 + 16 * 2
    assert routine_entry.basis == "FITTED"
    assert shell_entry.bytes == 4816
    assert shell_entry.basis == "FITTED"
    assert routine_entry.bytes + shell_entry.bytes == 4816 + 4 * 3 + 16 * 2

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
    # FIXED SHELL cost is already folded into the caller's jsr_fixed_base_
    # per_routine constant -- before that fix the engine also charged
    # SubTest its own full fixed_base_per_routine, overcounting every
    # JSR-using program. That part still holds (charge_shell=False for a
    # JSR target). What's NO LONGER true (2026-08-31, real data at real
    # scale disproved it -- see OPEN_QUESTIONS.md OQ-JSRPARAMCOST) is that
    # the target's own CONTENT was also free: it's now weighed with the
    # normal per-instruction model, same as any other routine.
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
    # MainRoutine gets its own entry (its content, never double-counted
    # with SubTest's own content). SubTest, being a JSR target, gets its
    # A(n) Parameters-block one-time cost (OQ-JSRPARAMCOST) PLUS its own
    # instruction content weighed normally (2026-08-31) -- just not its
    # own fixed_base_per_routine shell, which stays folded into the
    # caller's jsr_fixed_base_per_routine as before this feature existed.
    assert len(logic_entries) == 2
    by_path = {e.path: e for e in logic_entries}
    main = by_path["program:MainProgram/MainRoutine"]
    sub = by_path["program:MainProgram/SubTest"]
    # jsr_fixed_base_per_routine(5096) + JSR's own weight(72)*1 + B(0)=4 = 5172
    assert main.bytes == 5096 + 72 + 4
    # A(0) = a_base(104) + a_per_param(20)*0 = 104, plus SubTest's own
    # content (one NOP rung, weight 16, plus the 2026-08-31 composite-scale
    # surcharge of 47/instr = 47) -- no fixed_base_per_routine (that stays
    # folded into MainRoutine's jsr_fixed_base_per_routine above).
    assert sub.bytes == 104 + 16 + _JSR_SURCHARGE


def test_jsr_param_cost_a_charged_once_even_with_two_call_sites():
    # A(n) is the TARGET routine's own one-time Parameters-block cost --
    # must not be double-charged just because 2 different rungs (or 2
    # different calling routines) both JSR to the same target.
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
                  <Rung Number="0" Type="N"><Text><![CDATA[JSR(SubTest,2,A,B);]]></Text></Rung>
                  <Rung Number="1" Type="N"><Text><![CDATA[JSR(SubTest,2,C,D);]]></Text></Rung>
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
    entries, errors = build_report(root, MODEL)
    assert errors == []
    logic_entries = [e for e in entries if e.tier == ESTIMATED]
    by_path = {e.path: e for e in logic_entries}
    sub = by_path["program:MainProgram/SubTest"]
    # A(2) = 104 + 20*2 = 144 -- charged exactly once, not twice for the 2
    # call sites, plus SubTest's own content (one NOP rung, weight 16 +
    # composite-scale surcharge 47) -- also charged exactly once regardless
    # of call-site count, since it's the target routine's own content, not
    # a per-call cost.
    assert sub.bytes == 144 + 16 + _JSR_SURCHARGE
    main = by_path["program:MainProgram/MainRoutine"]
    # jsr_fixed_base(5096) + JSR weight(72)*2 calls + B(2)=4+20*2=44 *2 calls
    assert main.bytes == 5096 + 72 * 2 + 44 * 2


def test_jsr_output_param_cost_charged_per_call_site():
    # OQ-JSRPARAMCOST, wired 2026-08-29: trailing return-value args
    # (`JSR(name, N_in, in_1..in_N, out_1..out_M)`) were completely
    # unmodeled -- real jsr_mixedio_5in_2out/jsr_multiret_n04 capture data
    # showed ~20/output-arg, same rate as an input arg. N_in=1 (arg "A"),
    # 2 trailing output args (B, C) -> m_out=2.
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
                  <Rung Number="0" Type="N"><Text><![CDATA[JSR(SubTest,1,A,B,C);]]></Text></Rung>
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
    entries, errors = build_report(root, MODEL)
    assert errors == []
    logic_entries = [e for e in entries if e.tier == ESTIMATED]
    by_path = {e.path: e for e in logic_entries}
    main = by_path["program:MainProgram/MainRoutine"]
    # jsr_fixed_base(5096) + JSR weight(72) + B(1)=4+20=24 + output_param_cost(20)*2
    assert main.bytes == 5096 + 72 + 24 + 20 * 2
    sub = by_path["program:MainProgram/SubTest"]
    # A(1) unaffected by output param count (not yet adjusted -- see
    # OPEN_QUESTIONS.md OQ-JSRPARAMCOST), plus SubTest's own content (one
    # NOP rung, weight 16 + composite-scale surcharge 47).
    assert sub.bytes == 104 + 20 + 16 + _JSR_SURCHARGE


def test_jsr_target_content_scales_with_instruction_count():
    # 2026-08-31: real data (jsr_target_content_scale_{010,050,100,150})
    # disproved the old "target content is free" assumption -- see
    # OPEN_QUESTIONS.md OQ-JSRPARAMCOST. This is the direct regression test
    # for that fix: a target with more real content must predict MORE
    # bytes than an otherwise-identical target with less, and the target
    # must NOT pay its own fixed_base_per_routine (that stays folded into
    # the caller's jsr_fixed_base_per_routine).
    def build(target_rungs: str) -> int:
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
                      <Rung Number="0" Type="N"><Text><![CDATA[JSR(SubTest,0);]]></Text></Rung>
                    </RLLContent>
                  </Routine>
                  <Routine Name="SubTest" Type="RLL">
                    <RLLContent>{target_rungs}</RLLContent>
                  </Routine>
                </Routines>
              </Program>
            </Programs>
          </Controller>
        </RSLogix5000Content>
        """
        root = ET.fromstring(xml)
        entries, errors = build_report(root, MODEL)
        assert errors == []
        by_path = {e.path: e for e in entries if e.tier == ESTIMATED}
        return by_path["program:MainProgram/SubTest"].bytes

    one_nop = '<Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>'
    two_nop = (
        '<Rung Number="0" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>'
        '<Rung Number="1" Type="N"><Text><![CDATA[NOP();]]></Text></Rung>'
    )
    # A(0)=104 shared by both; content must differ by exactly one more
    # NOP's weight (16) plus its composite-scale surcharge (47), and
    # neither pays fixed_base_per_routine (4816) -- that would swamp this
    # small a difference if it leaked in.
    assert build(one_nop) == 104 + 16 + _JSR_SURCHARGE
    assert build(two_nop) == 104 + (16 + _JSR_SURCHARGE) * 2


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
    assert [c.operators for c in routine.cpt_calls] == [["+", "*"]]


def test_cpt_parser_handles_nested_parens_and_multiple_calls():
    routine = _one_rung_routine("CPT(D1,(L0+L1)*(L2-L3))CPT(D2,L4);")
    assert [c.operators for c in routine.cpt_calls] == [["+", "*", "-"], []]
    assert [c.dest for c in routine.cpt_calls] == ["D1", "D2"]


def test_cpt_parser_recognizes_pow_and_word_mod():
    routine = _one_rung_routine("CPT(Dest,L0**L1 MOD L2);")
    assert [c.operators for c in routine.cpt_calls] == [["**", "MOD"]]
    # MOD is a word OPERATOR -- it must not land in operand_names, where it
    # would be miscounted as an int operand needing a float conversion.
    assert routine.cpt_calls[0].operand_names == ("L0", "L1", "L2")


def test_cpt_parser_captures_operand_composition_for_real_dest_costing():
    # Destination, tag operands and int-vs-float literals are what
    # sizing/logic.py needs to price a REAL-destination CPT (the integer
    # operator-tier costs don't apply there) -- see memory_model.yaml
    # cpt_expression.real_dest.
    routine = _one_rung_routine("CPT(DestR,(L0+L1)*R1-R2/2+1.5);")
    call = routine.cpt_calls[0]
    assert call.dest == "DestR"
    assert call.operand_names == ("L0", "L1", "R1", "R2")
    assert (call.int_literals, call.float_literals) == (1, 1)


def test_cpt_real_dest_costs_more_than_int_dest_for_same_expression():
    # Real, confirmed on 29 capture rows: an identically-shaped CPT costs
    # materially more with a REAL destination (float evaluation + a real
    # per-operand int->float conversion) than with an integer one.
    xml = """
<RSLogix5000Content SchemaRevision="1.0"><Controller Name="T">
  <Tags>
    <Tag Name="TD0" TagType="Base" DataType="DINT"/>
    <Tag Name="TD1" TagType="Base" DataType="DINT"/>
    <Tag Name="TD2" TagType="Base" DataType="DINT"/>
    <Tag Name="TR0" TagType="Base" DataType="REAL"/>
  </Tags>
  <Programs><Program Name="MainProgram"><Routines>
    <Routine Name="R" Type="RLL"><RLLContent>
      <Rung Number="0" Type="N"><Text><![CDATA[CPT(TD0,TD1+TD2);]]></Text></Rung>
    </RLLContent></Routine>
    <Routine Name="R2" Type="RLL"><RLLContent>
      <Rung Number="0" Type="N"><Text><![CDATA[CPT(TR0,TD1+TD2);]]></Text></Rung>
    </RLLContent></Routine>
  </Routines></Program></Programs>
</Controller></RSLogix5000Content>
"""
    root = ET.fromstring(xml)
    entries, _errors = build_report(root, MODEL)
    by_path = {e.path: e.bytes for e in entries}
    int_dest = by_path["program:MainProgram/R"]
    real_dest = by_path["program:MainProgram/R2"]
    # 1 operator, 2 DINT operands needing conversion:
    #   float first_operator(76) - int '+' tier cost(36) + 2*per_int_operand(40)
    assert real_dest - int_dest == 76 - 36 + 80


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


def test_cpt_pow_tier_mix_solved_for_t1t3_and_t2t3():
    # POW (T3) alongside EXACTLY ONE other tier (T1 or T2) is now solved
    # (OQ-CMPCPTLAYOUT, 2026-08-25): pow_tier_mix_base + pow_tier_mix_per_operator
    # * operator_count. Real data confirmed T1T3 and T2T3 cost IDENTICALLY at
    # every tested operator count -- one formula for both pairs.
    model = MODEL.logic_instructions
    assert model.cpt_expression.cost_for(["+", "**"]) == 160 + 64 * 2
    assert model.cpt_expression.cost_for(["*", "**"]) == 160 + 64 * 2
    assert model.cpt_expression.cost_for(["+", "**"]) == model.cpt_expression.cost_for(["*", "**"])


def test_cpt_all_three_tiers_applies_remainder_correction():
    # All 3 tiers present in one expression, CLOSED 2026-08-29
    # (OQ-CMPCPTLAYOUT): the plain additive sum plus a real correction
    # keyed on operator_count % 3 -- confirmed 0 residual across all 9
    # real all-3-tier data points on file (see memory_model.yaml
    # cpt_expression). 3 operators -> remainder 0, 1 POW operand:
    # base_by_remainder[0](72) + per_pow_operand(4)*1 = 76.
    model = MODEL.logic_instructions
    assert model.cpt_expression.cost_for(["+", "*", "**"]) == 88 + 36 + 52 + 116 + 76


def test_cpt_three_tier_remainder_correction_matches_real_capture_points():
    # Real cptmix_threetier_* / cptmix_threetier_rem2_* capture data
    # (OQ-CMPCPTLAYOUT closeout, 2026-08-29): 3-tier alternating
    # [+,*,**] expressions at operand counts 5/6/9/10 (operator counts
    # 4/5/8/9), covering all 3 remainder classes with a real, exact
    # match at each.
    model = MODEL.logic_instructions
    tiers = ["+", "*", "**"]

    def ops(operator_count):
        return [tiers[i % 3] for i in range(operator_count)]

    # 4 operators (remainder 1, T1=2/T2=1/T3=1): real delta +120 over
    # the plain additive sum.
    plain = 88 + sum(model.cpt_expression.operator_tier_costs[op] for op in ops(4))
    assert model.cpt_expression.cost_for(ops(4)) == plain + 120

    # 5 operators (remainder 2, T1=2/T2=2/T3=1): real delta +148.
    plain = 88 + sum(model.cpt_expression.operator_tier_costs[op] for op in ops(5))
    assert model.cpt_expression.cost_for(ops(5)) == plain + 148

    # 8 operators (remainder 2, T3=2): real delta +152.
    plain = 88 + sum(model.cpt_expression.operator_tier_costs[op] for op in ops(8))
    assert model.cpt_expression.cost_for(ops(8)) == plain + 152

    # 9 operators (remainder 0, T1=T2=T3=3): real delta +84, the one
    # remainder-0 point on file.
    plain = 88 + sum(model.cpt_expression.operator_tier_costs[op] for op in ops(9))
    assert model.cpt_expression.cost_for(ops(9)) == plain + 84


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


# ---------------------------------------------------------------------------
# OQ-BRANCHDEPTH: real branch-bracket cost, wired 2026-08-30. A branch with
# L legs compiles to L+1 real BST/NXB/BND-family instructions (1 BST +
# (L-1) NXB + 1 BND); nested/staggered branches recurse. Confirmed exact
# against 16/16 real capture points (branchdepthc_legs*/branchdepthstag_d*).
# ---------------------------------------------------------------------------

def test_no_branch_costs_nothing_extra():
    routine = _one_rung_routine("XIC(L0)OTE(L1);")
    assert routine.branch_bracket_instruction_count == 0
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    base = (
        MODEL.logic_instructions.fixed_base_per_routine
        + MODEL.logic_instructions.weights["XIC"]
        + MODEL.logic_instructions.weights["OTE"]
    )
    assert bytes_ == base


def test_flat_branch_costs_legs_plus_one_instructions():
    # 3-leg branch -> 1 BST + 2 NXB + 1 BND = 4 real instructions.
    routine = _one_rung_routine("[XIC(L0),XIC(L1),XIC(L2)]OTE(L3);")
    assert routine.branch_bracket_instruction_count == 4
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    base = (
        MODEL.logic_instructions.fixed_base_per_routine
        + 3 * MODEL.logic_instructions.weights["XIC"]
        + MODEL.logic_instructions.weights["OTE"]
    )
    assert bytes_ == base + 4 * MODEL.logic_instructions.branch_bracket_cost_per_instruction


def test_nested_branch_sums_recursively():
    # Outer: [leg1[nested], leg2] = 2 legs -> 3 instructions.
    # Nested: [leg1, leg2] = 2 legs -> 3 instructions. Total = 6.
    routine = _one_rung_routine("[XIC(L0)[XIC(L1),XIC(L2)],XIC(L3)]OTE(L4);")
    assert routine.branch_bracket_instruction_count == 6
    bytes_, _ = compute_routine_logic_bytes(routine, MODEL.logic_instructions)
    base = (
        MODEL.logic_instructions.fixed_base_per_routine
        + 4 * MODEL.logic_instructions.weights["XIC"]
        + MODEL.logic_instructions.weights["OTE"]
    )
    assert bytes_ == base + 6 * MODEL.logic_instructions.branch_bracket_cost_per_instruction


def test_array_index_bracket_not_counted_as_branch():
    # "Arr[5]" is an array index, not a branch -- must not be misclassified.
    routine = _one_rung_routine("MOV(Arr[5],Dest);")
    assert routine.branch_bracket_instruction_count == 0


def test_build_report_reports_non_rll_routine_as_a_coverage_gap():
    """A routine this engine cannot size must SAY SO, not vanish.

    _XML carries a Type="ST" routine that parse_rll_routines drops on the
    floor. Before sizing/coverage.py that produced a silently understated
    total with nothing in the output to hint at it -- the only thing that
    ever caught it was someone reading the L5X by hand (2026-09-04, James:
    "I need to make sure that in the long run all of the calculations are
    done inside the python logic for the total project scripts and not just
    claude in depth testing"). It now comes back as an ordinary SizeError,
    which is what the CLI, the UI and the CSV/XLSX export all render.
    """
    root = ET.fromstring(_XML)
    _entries, errors = build_report(root, MODEL)

    gaps = [e for e in errors if e.path.startswith("coverage/")]
    assert len(gaps) == 1
    assert gaps[0].path == "coverage/routine_type/ST"
    assert "Structured Text" in gaps[0].message
    assert "StRoutine" in gaps[0].message or "MainProgram" in gaps[0].message


def test_coverage_audit_does_not_flag_instructions_priced_outside_the_weights_table():
    """CPT, the branch brackets and any declared AOI are all priced somewhere
    other than logic_instructions.weights. Flagging them as unweighted would
    be a false alarm that trains the reader to ignore the whole section."""
    xml = _XML.replace(
        '<Rung Number="1" Type="N"><Text><![CDATA[XIC(A)XIC(B)OTE(A);]]></Text></Rung>',
        '<Rung Number="1" Type="N"><Text><![CDATA[BST XIC(A) NXB XIC(B) BND OTE(A);]]></Text></Rung>'
        '<Rung Number="2" Type="N"><Text><![CDATA[CPT(C,A+B);]]></Text></Rung>',
    )
    _entries, errors = build_report(ET.fromstring(xml), MODEL)

    flagged = {e.path for e in errors if e.path.startswith("coverage/instruction/")}
    assert flagged == set(), flagged
