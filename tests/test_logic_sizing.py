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

    entries, errors = build_report(root, MODEL)
    assert errors == []
    logic_entries = [e for e in entries if e.tier == ESTIMATED]
    # Only MainRoutine gets an entry -- SubTest is skipped entirely, not
    # charged its own fixed_base on top of the caller's jsr_fixed_base.
    assert len(logic_entries) == 1
    assert logic_entries[0].path == "program:MainProgram/MainRoutine"
    # jsr_fixed_base_per_routine(5096) + JSR's own weight(72)*1 = 5168
    assert logic_entries[0].bytes == 5096 + 72
