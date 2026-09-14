"""An AOI-internal instruction writing a non-BOOL destination costs 4 more.

OQ-AOIINTERNALLOGIC, derived 2026-09-14 (capture-batch segment 15). The same
instruction in an ordinary Program routine costs nothing extra: `instr_*` sits
at the universal +8 per-file residual for MOV, CLR, ADD, EQU, XIC and OTE alike
at every count from 10 to 5,000 instructions. Only the AOI-internal path
under-charges, and only for instructions that write a word.

This replaces `aoi_internal_per_rung`, which carried the right number on the
wrong carrier and was therefore exact on its own sweep and wrong everywhere
else: `aoistr_scale_rung`'s rungs are `XIC(EnableIn)MOV(In0,In1);`, one MOV
each, so per-rung and per-word-destination are the same number on that family
and nowhere else in the corpus.

Five families agree with no counter-example:

    aoishape_{mov,add,clr}_n{1,5,10}   +4 per rung
    aoishape_{xicote,equote}_n{1,5,10}  0 at every count
    aoistr_scale_rung_n{011..085}      +4 per rung across a 7.7x span
    realscale_aoiint_n{0..12000}        0 through 12,000 instructions
    aoishape_control_mix13             +32 on 8 word destinations, mixed file

All 27 of those rows are byte-exact with this wired.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.parser.logic import parse_aoi_internal_logic, word_destination_count
from l5x_memory_analyzer.sizing.constants import load_memory_model


@pytest.fixture
def model():
    return load_memory_model()


def _aoi_root(rung_texts: list[str]) -> ET.Element:
    rungs = "".join(
        f'<Rung Number="{i}" Type="N"><Text><![CDATA[{t}]]></Text></Rung>'
        for i, t in enumerate(rung_texts)
    )
    return ET.fromstring(f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test" ProcessorType="1756-L81E" MajorRev="35">
        <DataTypes/>
        <AddOnInstructionDefinitions>
          <AddOnInstructionDefinition Name="Probe" Revision="1.0">
            <Parameters>
              <Parameter Name="EnableIn" DataType="BOOL" Usage="Input" Required="false" Visible="false"/>
              <Parameter Name="EnableOut" DataType="BOOL" Usage="Output" Required="false" Visible="false"/>
              <Parameter Name="In0" DataType="DINT" Usage="Input" Required="true" Visible="true"/>
              <Parameter Name="In1" DataType="DINT" Usage="Input" Required="true" Visible="true"/>
              <Parameter Name="In2" DataType="BOOL" Usage="Input" Required="true" Visible="true"/>
              <Parameter Name="Out0" DataType="BOOL" Usage="Output" Required="true" Visible="true"/>
            </Parameters>
            <LocalTags>
              <LocalTag Name="Loc0" DataType="DINT"/>
              <LocalTag Name="Loc1" DataType="DINT"/>
            </LocalTags>
            <Routines>
              <Routine Name="Logic" Type="RLL"><RLLContent>{rungs}</RLLContent></Routine>
            </Routines>
          </AddOnInstructionDefinition>
        </AddOnInstructionDefinitions>
        <Tags/><Programs/><Tasks/><Modules/>
      </Controller>
    </RSLogix5000Content>
    """)


def _count(rung_texts: list[str]) -> int:
    routine = parse_aoi_internal_logic(_aoi_root(rung_texts))["Probe"]
    return routine.word_destination_count


def test_the_constant_is_wired_at_four(model):
    assert model.logic_instructions.aoi_internal_per_word_destination == 4
    assert model.logic_instructions.aoi_internal_per_word_destination_confidence == "KNOWN"


def test_the_superseded_per_rung_term_stays_at_zero(model):
    """Both terms applying would double-charge every single-word-destination
    rung, which is most real AOI logic."""
    assert model.logic_instructions.aoi_internal_per_rung == 0


def test_word_writing_instructions_count(model):
    """MOV, ADD and CLR each write a DINT. Operand count does not matter --
    CLR has one, MOV two, ADD three, and all three cost the same +4."""
    assert _count(["MOV(In0,In1);"]) == 1
    assert _count(["ADD(In0,In1,Loc1);"]) == 1
    assert _count(["CLR(Loc0);"]) == 1


def test_bool_and_no_destination_instructions_do_not_count(model):
    """OTE writes a BOOL; EQU and XIC write nothing at all. This is the split
    that killed both the per-rung and the per-instruction readings."""
    assert _count(["XIC(In2)OTE(Out0);"]) == 0
    assert _count(["EQU(In0,In1)OTE(Out0);"]) == 0


def test_a_bit_conditional_does_not_add_to_a_word_write(model):
    """aoistr_scale_rung's real shape: the MOV counts, the XIC guarding it
    does not, so the rung is worth 4 and not 8."""
    assert _count(["XIC(EnableIn)MOV(In0,In1);"]) == 1


def test_the_mixed_shape_matches_the_captured_file(model):
    """aoishape_control_mix13 cycles five shapes over 13 rungs -- 3 MOV, 3 CLR,
    2 ADD, 3 XIC/OTE, 2 EQU/OTE -- and its residual was +32, i.e. 8 x 4."""
    shapes = ["MOV(In0,In1);", "XIC(In2)OTE(Out0);", "CLR(Loc0);",
              "ADD(In0,In1,Loc1);", "EQU(In0,In1)OTE(Out0);"]
    rungs = [shapes[i % len(shapes)] for i in range(13)]
    assert _count(rungs) == 8


def test_a_bool_local_destination_does_not_count(model):
    """The rule turns on the DESTINATION'S TYPE, not on the mnemonic, so a MOV
    into a BOOL is free while a MOV into a DINT is not."""
    routine = parse_aoi_internal_logic(ET.fromstring(_mixed_dest_root()))["Probe"]
    assert routine.word_destination_count == 1


def _mixed_dest_root() -> str:
    """One MOV to a DINT local and one to a BOOL local, in the same routine."""
    return """
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test" ProcessorType="1756-L81E" MajorRev="35">
        <DataTypes/>
        <AddOnInstructionDefinitions>
          <AddOnInstructionDefinition Name="Probe" Revision="1.0">
            <Parameters>
              <Parameter Name="In0" DataType="DINT" Usage="Input" Required="true" Visible="true"/>
            </Parameters>
            <LocalTags>
              <LocalTag Name="WordLoc" DataType="DINT"/>
              <LocalTag Name="BitLoc" DataType="BOOL"/>
            </LocalTags>
            <Routines>
              <Routine Name="Logic" Type="RLL"><RLLContent>
                <Rung Number="0" Type="N"><Text><![CDATA[MOV(In0,WordLoc);]]></Text></Rung>
                <Rung Number="1" Type="N"><Text><![CDATA[MOV(In0,BitLoc);]]></Text></Rung>
              </RLLContent></Routine>
            </Routines>
          </AddOnInstructionDefinition>
        </AddOnInstructionDefinitions>
        <Tags/><Programs/><Tasks/><Modules/>
      </Controller>
    </RSLogix5000Content>
    """


def test_an_array_element_or_member_resolves_to_its_base_tag(model):
    """`Loc0[3]` and `Loc0.1` both key off Loc0, which is how the AOI's own
    declaration table is keyed."""
    assert _count(["MOV(In0,Loc0[3]);"]) == 1
    assert _count(["MOV(In0,Loc0.0);"]) == 1


def test_program_routine_logic_is_untouched(model):
    """The negative control. Program-routine weights are already exact at 5,000
    instructions, so word_destination_count must stay 0 outside an AOI or every
    real program gains cost it does not have."""
    from l5x_memory_analyzer.parser.logic import parse_rll_routines

    root = ET.fromstring("""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test" ProcessorType="1756-L81E" MajorRev="35">
        <DataTypes/><AddOnInstructionDefinitions/>
        <Tags><Tag Name="A" DataType="DINT"/><Tag Name="B" DataType="DINT"/></Tags>
        <Programs>
          <Program Name="Main" MainRoutineName="R">
            <Tags/>
            <Routines><Routine Name="R" Type="RLL"><RLLContent>
              <Rung Number="0" Type="N"><Text><![CDATA[MOV(A,B);]]></Text></Rung>
            </RLLContent></Routine></Routines>
          </Program>
        </Programs>
        <Tasks/><Modules/>
      </Controller>
    </RSLogix5000Content>
    """)
    for routine in parse_rll_routines(root):
        assert routine.word_destination_count == 0
