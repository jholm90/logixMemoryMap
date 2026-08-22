from sample_gen.lint import lint_l5x

_WRAPPER = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <DataTypes/>
    <AddOnInstructionDefinitions>{aoi}</AddOnInstructionDefinitions>
    <Tags>{tags}</Tags>
    <Programs>
      <Program Name="MainProgram">
        <Tags/>
        <Routines>
          <Routine Name="MainRoutine" Type="RLL">
            <RLLContent>
              <Rung Number="0" Type="N"><Text><![CDATA[{rung}]]></Text></Rung>
            </RLLContent>
          </Routine>
        </Routines>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>
"""


def _xml(rung: str, tags: str = "", aoi: str = "") -> str:
    return _WRAPPER.format(rung=rung, tags=tags, aoi=aoi)


def test_flags_array_tag_referenced_without_subscript():
    tags = '<Tag Name="ARR0" TagType="Base" DataType="DINT" Dimensions="20"><Data Format="Decorated"><Array DataType="DINT" Dimensions="20"/></Data></Tag>'
    findings = lint_l5x(_xml("CPS(ARR0,ARR0,5);", tags=tags))
    assert any(f.kind == "missing_array_subscript" for f in findings)


def test_does_not_flag_array_tag_with_subscript():
    tags = '<Tag Name="ARR0" TagType="Base" DataType="DINT" Dimensions="20"><Data Format="Decorated"><Array DataType="DINT" Dimensions="20"/></Data></Tag>'
    findings = lint_l5x(_xml("CPS(ARR0[0],ARR0[0],5);", tags=tags))
    assert not any(f.kind == "missing_array_subscript" for f in findings)


def test_flags_instruction_call_with_no_matching_definition():
    findings = lint_l5x(_xml("T_ADD(D0,D1,D2,D3);"))
    assert any(f.kind == "unrecognized_instruction" and "T_ADD" in f.detail for f in findings)


def test_does_not_flag_call_matching_a_declared_aoi():
    aoi = '<AddOnInstructionDefinition Name="T_ADD"><Parameters/><LocalTags/><Routines><Routine Name="Logic" Type="RLL"/></Routines></AddOnInstructionDefinition>'
    findings = lint_l5x(_xml("T_ADD(Inst,D1,D2,D3);", aoi=aoi))
    assert not any(f.kind == "unrecognized_instruction" for f in findings)


def test_does_not_flag_known_native_instructions():
    findings = lint_l5x(_xml("XIC(A)OTE(B);"))
    assert findings == []
