"""ST boolean operators must not crash the report.

Real traceback, 2026-09-09: loading a file in the UI died with
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
