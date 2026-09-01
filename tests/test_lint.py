from sample_gen.builders import MemberSpec, aoi_xml, rung_xml, tag_xml
from sample_gen.lint import lint_l5x
from sample_gen.wrapper import build_l5x

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


_MODULE_WRAPPER = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <DataTypes/>
    <Modules>
      <Module Name="Local" CatalogNumber="1756-L81E" ParentModule="Local" ParentModPortId="1">
        <Ports><Port Id="1" Address="0" Type="ICP" Upstream="false"><Bus Size="17"/></Port></Ports>
      </Module>
      {modules}
    </Modules>
    <AddOnInstructionDefinitions/>
    <Tags/>
    <Programs>
      <Program Name="MainProgram">
        <Tags/>
        <Routines>
          <Routine Name="MainRoutine" Type="RLL">
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


def _module_xml(name: str, address: str) -> str:
    return (
        f'<Module Name="{name}" CatalogNumber="1756-CNB/D" ParentModule="Local" ParentModPortId="1">'
        f'<Ports><Port Id="1" Address="{address}" Type="ICP" Upstream="true"/></Ports>'
        f"</Module>"
    )


def test_flags_two_modules_claiming_the_same_slot():
    modules = _module_xml("ModA", "3") + _module_xml("ModB", "3")
    findings = lint_l5x(_MODULE_WRAPPER.format(modules=modules))
    assert any(f.kind == "duplicate_module_slot" for f in findings)


def test_does_not_flag_modules_in_distinct_slots():
    modules = _module_xml("ModA", "3") + _module_xml("ModB", "4")
    findings = lint_l5x(_MODULE_WRAPPER.format(modules=modules))
    assert not any(f.kind == "duplicate_module_slot" for f in findings)


def test_flags_module_address_beyond_parent_bus_size():
    # Local's own Port Id=1 declares Bus Size=17 -- Address=20 overflows it.
    modules = _module_xml("Overflow", "20")
    findings = lint_l5x(_MODULE_WRAPPER.format(modules=modules))
    assert any(f.kind == "chassis_size_exceeded" for f in findings)


def test_does_not_flag_module_address_within_parent_bus_size():
    modules = _module_xml("InBounds", "3")
    findings = lint_l5x(_MODULE_WRAPPER.format(modules=modules))
    assert not any(f.kind == "chassis_size_exceeded" for f in findings)


# James, 2026-08-31: real Studio 5000 verify errors on composite_realistic_
# 02/03.ACD, "Invalid number of arguments for instruction" on every AOI
# call rung -- a hidden (Required=false/Visible=false) Input/Output
# Parameter isn't a real call-argument slot, but the generator supplied
# one anyway. Found while fixing this that _INSTRUCTION_CALL's own regex
# was ALSO silently blind to any mixed-case AOI name (only matched
# ALL-CAPS mnemonics) -- both are covered here.

def test_instruction_call_regex_matches_mixed_case_aoi_names():
    # Real bug: the old pattern (\b[A-Z][A-Z0-9_]*\() never matched
    # "Comp02Aoi0(" or any other mixed-case AOI call at all.
    definition, storage = aoi_xml("MixedCaseAoi", input_params=[MemberSpec("In0", "DINT", required=True)])
    tag = tag_xml("Inst", "MixedCaseAoi", udt_members=storage)
    rung = rung_xml(0, "MixedCaseAoi(Inst,0);")
    l5x = build_l5x(target_name="T", tags_xml=tag, extra_aoi_xml=definition, extra_rungs_xml=rung)
    # A wrong arg count would still be caught below -- this call is
    # correct (1 required param, 1 arg supplied), so expect no findings.
    assert lint_l5x(l5x) == []


def test_flags_aoi_call_with_hidden_param_supplied_an_argument():
    definition, storage = aoi_xml(
        "HiddenParamAoi",
        input_params=[MemberSpec("In0", "DINT")],  # required=False, visible=False -> hidden
        output_params=[MemberSpec("Out0", "BOOL")],
    )
    tag = tag_xml("Inst", "HiddenParamAoi", udt_members=storage)
    rung = rung_xml(0, "HiddenParamAoi(Inst,0,OutBit);")
    l5x = build_l5x(
        target_name="T", tags_xml=tag + "\n" + tag_xml("OutBit", "BOOL"),
        extra_aoi_xml=definition, extra_rungs_xml=rung,
    )
    assert any(f.kind == "aoi_call_arg_count_mismatch" for f in lint_l5x(l5x))


def test_does_not_flag_aoi_call_with_required_params_correctly_wired():
    definition, storage = aoi_xml(
        "RequiredParamAoi",
        input_params=[MemberSpec("In0", "DINT", required=True)],
        output_params=[MemberSpec("Out0", "BOOL", required=True)],
    )
    tag = tag_xml("Inst", "RequiredParamAoi", udt_members=storage)
    rung = rung_xml(0, "RequiredParamAoi(Inst,0,OutBit);")
    l5x = build_l5x(
        target_name="T", tags_xml=tag + "\n" + tag_xml("OutBit", "BOOL"),
        extra_aoi_xml=definition, extra_rungs_xml=rung,
    )
    assert not any(f.kind == "aoi_call_arg_count_mismatch" for f in lint_l5x(l5x))


def test_does_not_flag_aoi_call_omitting_trailing_visible_optional_param():
    # Real corpus precedent (PTimer, samples/local/SJ_Gormley_20251112_
    # r02.L5X): a Required=false/Visible=true param CAN be omitted from
    # the end of the call entirely.
    definition, storage = aoi_xml(
        "OptionalParamAoi",
        input_params=[
            MemberSpec("In0", "DINT", required=True),
            MemberSpec("In1", "DINT", required=False, visible=True),
        ],
    )
    tag = tag_xml("Inst", "OptionalParamAoi", udt_members=storage)
    rung = rung_xml(0, "OptionalParamAoi(Inst,0);")  # omits In1
    l5x = build_l5x(target_name="T", tags_xml=tag, extra_aoi_xml=definition, extra_rungs_xml=rung)
    assert not any(f.kind == "aoi_call_arg_count_mismatch" for f in lint_l5x(l5x))


def test_flags_bit_level_instruction_on_bare_dint_tag():
    tag = tag_xml("MyDint", "DINT")
    rung = rung_xml(0, "XIC(MyDint)OTE(MyDint);")
    l5x = build_l5x(target_name="T", tags_xml=tag, extra_rungs_xml=rung)
    findings = [f for f in lint_l5x(l5x) if f.kind == "bit_level_instruction_on_non_bool_operand"]
    assert len(findings) == 2


def test_does_not_flag_bit_level_instruction_on_bool_tag():
    tag = tag_xml("MyBool", "BOOL")
    rung = rung_xml(0, "XIC(MyBool)OTE(MyBool);")
    l5x = build_l5x(target_name="T", tags_xml=tag, extra_rungs_xml=rung)
    assert not any(f.kind == "bit_level_instruction_on_non_bool_operand" for f in lint_l5x(l5x))


def test_does_not_flag_bit_level_instruction_with_bit_subscript():
    tag = tag_xml("MyDint", "DINT")
    rung = rung_xml(0, "XIC(MyDint.0)OTE(MyDint.1);")
    l5x = build_l5x(target_name="T", tags_xml=tag, extra_rungs_xml=rung)
    assert not any(f.kind == "bit_level_instruction_on_non_bool_operand" for f in lint_l5x(l5x))


def test_flags_rung_with_only_conditional_instructions():
    tag = tag_xml("MyDint", "DINT")
    rung = rung_xml(0, "EQU(MyDint,1);")
    l5x = build_l5x(target_name="T", tags_xml=tag, extra_rungs_xml=rung)
    assert any(f.kind == "rung_missing_output_instruction" for f in lint_l5x(l5x))


def test_does_not_flag_rung_ending_in_output_instruction():
    tags = tag_xml("MyDint", "DINT") + "\n" + tag_xml("MyBool", "BOOL")
    rung = rung_xml(0, "EQU(MyDint,1)OTE(MyBool);")
    l5x = build_l5x(target_name="T", tags_xml=tags, extra_rungs_xml=rung)
    assert not any(f.kind == "rung_missing_output_instruction" for f in lint_l5x(l5x))


def test_does_not_flag_empty_rung_as_missing_output():
    l5x = build_l5x(target_name="T", tags_xml="", extra_rungs_xml=rung_xml(0, ""))
    assert not any(f.kind == "rung_missing_output_instruction" for f in lint_l5x(l5x))


def test_flags_bare_lbl_with_nothing_after_it():
    l5x = build_l5x(target_name="T", tags_xml="", extra_rungs_xml=rung_xml(0, "LBL(L1);"))
    assert any(f.kind == "lbl_missing_trailing_instruction" for f in lint_l5x(l5x))


def test_does_not_flag_lbl_followed_by_nop():
    l5x = build_l5x(target_name="T", tags_xml="", extra_rungs_xml=rung_xml(0, "LBL(L1)NOP();"))
    assert not any(f.kind == "lbl_missing_trailing_instruction" for f in lint_l5x(l5x))
