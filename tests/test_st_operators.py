"""ST boolean operators must not crash the report.

Real traceback: loading a file in the UI died with
KeyError: 'AND' out of CptExpression.cost_for. The ST tokenizer recognises
AND/OR/XOR as operators, but operator_tier_costs only prices + - * / MOD **,
so any ST assignment containing a boolean operator aborted the entire
report and the file simply failed to load.

A missing measurement is a coverage gap, not a crash. Nothing here asserts a
byte cost for AND/OR/XOR -- there is no capture data for them and inventing
one would be worse than a visible hole.
"""

from __future__ import annotations

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model

EXPR = load_memory_model().logic_instructions.cpt_expression


@pytest.mark.parametrize("operators", [["AND"], ["OR"], ["XOR"], ["+", "AND"], ["AND", "OR", "XOR"]])
def test_boolean_operators_do_not_raise(operators):
    assert EXPR.cost_for(operators) > 0


@pytest.mark.parametrize("operators", [["AND"], ["and"], ["And"]])
def test_boolean_operators_are_reported_as_unpriced(operators):
    assert EXPR.unpriced_operators(operators) == ["AND"]


def test_word_operators_are_case_normalised():
    """The tokenizer matches case-insensitively; the model keys uppercase."""
    assert EXPR.cost_for(["mod", "+"]) == EXPR.cost_for(["MOD", "+"])
    assert EXPR.unpriced_operators(["mod"]) == []


def test_priced_operators_still_charged_alongside_an_unpriced_one():
    """A mixed expression charges what is measured rather than all-or-nothing."""
    assert EXPR.cost_for(["+", "AND"]) == EXPR.cost_for(["+"])


def test_an_all_unpriced_expression_falls_back_to_the_read_cost():
    assert EXPR.cost_for(["AND", "OR"]) == EXPR.base_read


# --- ST's own operator classification, measured by gen_st_closeout --
# These assert the MEASURED per-statement totals, so each one names the file it
# came from. 1,000 statements per file, every residual an exact multiple of 1,000.

ST = load_memory_model().structured_text


def test_one_operator_row_is_a_lookup_per_operator_class():
    """stc_prem1_*, one operator, DINT destination, 1,000 statements each."""
    for op in ("+", "-"):
        assert ST.assignment_cost([op], dest_is_real=False) == 40
    for op in ("*", "/", "MOD"):
        assert ST.assignment_cost([op], dest_is_real=False) == 56
    # +84 over the additive 40 on all three, which is what says it is a class
    # effect rather than three coincidences.
    for op in ("AND", "OR", "XOR"):
        assert ST.assignment_cost([op], dest_is_real=False) == 124
    assert ST.assignment_cost(["**"], dest_is_real=False) == 204


def test_bitwise_costs_nothing_extra_once_the_statement_is_compound():
    """stc_opkind_or: four OR operators, DINT, reads the tier-1 196 exactly --
    so the 84 belongs to the one-operator compile, not to the operator."""
    assert ST.assignment_cost(["OR"] * 4, dest_is_real=False) == 196
    assert ST.assignment_cost(["+"] * 4, dest_is_real=False) == 196
    # stx_opkind_mul: 16 per multiplicative operator above that.
    assert ST.assignment_cost(["*"] * 4, dest_is_real=False) == 260
    # stc_opkind_pow: 348, i.e. 38 per operator -- less than half the 80 the
    # ladder CPT tier table charges for **.
    assert ST.assignment_cost(["**"] * 4, dest_is_real=False) == 348


def test_the_premium_follows_the_operands_not_the_destination():
    """stc_premreal_* against st_expr_cpt_mirror_n01000.

    All-REAL operands pay no multiplicative premium (284, residual 0) and 8 per
    ** (316). A REAL destination with an integer operand anywhere in the
    statement pays the integer rates -- the cpt_mirror is byte-exact only that
    way, and it is the file that decides between the two readings.
    """
    assert ST.assignment_cost(["+"] * 4, True, all_float_operands=True) == 284
    assert ST.assignment_cost(["*"] * 4, True, all_float_operands=True) == 284
    assert ST.assignment_cost(["**"] * 4, True, all_float_operands=True) == 316
    # Same shape, integer operand present: back to 16 per multiplicative.
    assert ST.assignment_cost(["*"] * 4, True, all_float_operands=False) == 348


def test_real_destination_conversion_is_per_source_keyed_on_source_type():
    """stc_conv_*, one operator, REAL destination, two sources of one type."""
    assert ST.conversion_bytes_for("DINT") == 48
    assert ST.conversion_bytes_for("SINT") == 92
    assert ST.conversion_bytes_for("INT") == 104
    assert ST.conversion_bytes_for("LINT") == 0
    # An unmeasured integer type falls back to DINT's rate rather than to zero.
    assert ST.conversion_bytes_for("UDINT") == 48
    # stc_conv_mixed is the additivity check and it is exact: one DINT and one
    # SINT source in the same statement is 56 + 48 + 92.
    mixed = ST.conversion_bytes_for("DINT") + ST.conversion_bytes_for("SINT")
    assert ST.assignment_cost(["+"], dest_is_real=True, conversion_bytes=mixed) == 196


def test_a_one_operator_real_destination_non_additive_shape_is_flagged():
    """Only the additive class is measured on the REAL row at one operator."""
    assert ST.unmeasured_one_operator_class(["+"], dest_is_real=True) == ""
    assert ST.unmeasured_one_operator_class(["*"], dest_is_real=False) == ""
    assert ST.unmeasured_one_operator_class(["*"], dest_is_real=True)


def test_st_aoi_call_one_time_is_per_routine_not_per_call():
    """stc_callone_n{10,100,1000} read a flat +268 at one call; the four
    stx_call_aoi_p* files read +256..+268 at ONE THOUSAND calls. A 1,000x change
    in call count moving the residual by 12 bytes is what separates them."""
    one = ST.st_aoi_call_cost(1, 2)
    thousand = ST.st_aoi_call_cost(1000, 2000)
    assert one - (ST.st_aoi_call_bytes + ST.st_aoi_call_per_param_bytes * 2) == 264
    assert thousand - 1000 * (ST.st_aoi_call_bytes
                              + ST.st_aoi_call_per_param_bytes * 2) == 264
    # A routine with no AOI call pays neither the per-call cost nor the one-time.
    assert ST.st_aoi_call_cost(0, 0) == 0
