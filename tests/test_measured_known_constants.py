"""The KNOWN register: constants that are exact measurements, not fits.

WHY THIS FILE EXISTS. `confidence: FITTED` on a block is a statement about how
most of that block was derived, and it under-states the constants inside it that
were measured alone, at several counts, with zero residual. Left at FITTED they
read as open questions and get re-derived -- which has already cost this project
whole sessions.

Every entry below is pinned to BOTH its value and its declared tier, against
`memory_model.yaml`, which CLAUDE.md makes the single source of truth for sizing
constants. Changing one without updating the evidence line fails here.

`rows` is the number of captured manifest rows behind the constant and `spans`
is what those rows vary, because "exact" means nothing without saying over what.
"""

from __future__ import annotations

import pytest
import yaml

from l5x_memory_analyzer.sizing.constants import _DEFAULT_PATH as MODEL_PATH


def _raw() -> dict:
    with open(MODEL_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


# (dotted path to the value, expected value, dotted path to its tier, rows, spans)
KNOWN_REGISTER = [
    (
        "jsr_param_cost.b_multiparam_extra", 4,
        "jsr_param_cost.b_multiparam_confidence", 13,
        "call counts 10/100/1000 x param counts 1..15; OQ-JSRPARAMCOST",
    ),
    (
        "jsr_target_declaration.per_target", 160,
        "jsr_target_declaration.per_target_confidence", 13,
        "distinct-target counts 1..50, two generators, name lengths 4..40",
    ),
    (
        "jsr_target_declaration.sbr_ret_operand_bytes", 112,
        "jsr_target_declaration.sbr_ret_operand_confidence", 16,
        "4 target counts (1/10/50/200) plus 12 parameterless subrtn_* controls at 0",
    ),
    (
        "logic_instructions.weights.DTR", 40,
        "logic_instructions.weight_confidence.DTR", 3,
        "10/100/1000 rungs, +404/+4004/+40004 against a weight of zero",
    ),
    (
        "cpt_expression.leading_tier1_run_bytes", 4,
        "cpt_expression.leading_tier1_run_confidence", 28,
        "4 arrangements x operator counts 3..9, tier counts held fixed",
    ),
    (
        "cpt_expression.leading_tier1_run_length", 2,
        "cpt_expression.leading_tier1_run_confidence", 28,
        "the same 28 rows; runs of 0, 1, 3, 4 and 5 all cost nothing",
    ),
    (
        "structured_text.assignment_one_operator_class_bytes.dint.bitwise", 124,
        "structured_text.assignment_operator_class_confidence", 3,
        "stc_prem1_{and,or,xor}, all three at the same +84 over additive",
    ),
    (
        "structured_text.assignment_one_operator_class_bytes.dint.exponent", 204,
        "structured_text.assignment_operator_class_confidence", 1,
        "stc_prem1_pow, 1000 statements",
    ),
    (
        "structured_text.assignment_operator_premium.dint.exponent", 38,
        "structured_text.assignment_operator_class_confidence", 1,
        "stc_opkind_pow at four operators: 348, not the tier table's 516",
    ),
    (
        "structured_text.assignment_operator_premium.real.multiplicative", 0,
        "structured_text.assignment_operator_class_confidence", 1,
        "stc_premreal_mul: all-float operands pay no multiplicative premium",
    ),
    (
        "structured_text.assignment_operator_premium.real.exponent", 8,
        "structured_text.assignment_operator_class_confidence", 1,
        "stc_premreal_pow at four operators: 316",
    ),
    (
        "structured_text.real_dest_source_conversion_bytes.SINT", 92,
        "structured_text.real_dest_source_conversion_confidence", 2,
        "stc_conv_sint, cross-checked by stc_conv_mixed's exact 56+48+92",
    ),
    (
        "structured_text.real_dest_source_conversion_bytes.INT", 104,
        "structured_text.real_dest_source_conversion_confidence", 1,
        "stc_conv_int, 1000 statements",
    ),
    (
        "structured_text.real_dest_source_conversion_bytes.LINT", 0,
        "structured_text.real_dest_source_conversion_confidence", 1,
        "stc_conv_lint reproduces the pure-REAL 56 exactly",
    ),
    (
        "structured_text.st_aoi_call_routine_bytes", 264,
        "structured_text.st_aoi_call_routine_confidence", 7,
        "3 files at ONE call vs 4 at a thousand; a 1000x change moves it 12 bytes",
    ),
]


def _dig(raw: dict, dotted: str):
    node = raw
    for part in dotted.split("."):
        assert part in node, f"{dotted}: '{part}' is gone from memory_model.yaml"
        node = node[part]
    return node


@pytest.mark.parametrize(
    "path,expected,tier_path,rows,spans",
    KNOWN_REGISTER,
    ids=[entry[0] for entry in KNOWN_REGISTER],
)
def test_measured_constant_holds_its_value_and_its_known_tier(
    path, expected, tier_path, rows, spans
):
    raw = _raw()
    assert _dig(raw, path) == expected, (
        f"{path} changed. It is a MEASUREMENT over {rows} captured row(s) "
        f"({spans}), not a fit -- if new data moves it, update this register "
        f"with the new evidence rather than deleting the entry."
    )
    assert _dig(raw, tier_path) == "KNOWN", (
        f"{path} is backed by {rows} captured row(s) ({spans}) and must stay "
        f"KNOWN. Dropping it to FITTED invites a re-derivation that has already "
        f"been done."
    )


def test_the_five_confirmed_instruction_weights_keep_their_tier():
    """DTR's sweep also re-measured five weights that were already in the table.

    They read the family's universal +4 at 10, 100 and 1,000 rungs, so they are
    confirmed by real data rather than assumed, and the register says so.
    """
    raw = _raw()
    weights = raw["logic_instructions"]["weights"]
    tiers = raw["logic_instructions"]["weight_confidence"]
    for mnemonic, value in (("AND", 40), ("OR", 40), ("RTOS", 72),
                            ("LFU", 72), ("UPPER", 84)):
        assert weights[mnemonic] == value
        assert tiers[mnemonic] == "KNOWN"


# Per-constant KNOWN tiers that predate this register (2026-09-18). Every one is
# derived and justified in a comment at its own definition site in
# memory_model.yaml, and most are the exactly-calculable data-space side CLAUDE.md
# distinguishes from fitted logic sizing -- BOOL packing, STRING layout, UDT
# alignment, array element sizing. They are listed rather than re-documented here
# because inventing row counts for measurements someone else took would be worse
# than naming them: the point of the guard below is to stop NEW tiers arriving
# without evidence, not to re-audit the old ones.
PRE_EXISTING_KNOWN = {
    "firmware_baseline_delta.default_confidence",
    "bool.standalone_confidence",
    "bool.member_confidence",
    "bool.array_confidence",
    "string.custom_confidence",
    "string.custom_definition_confidence",
    "string.builtin_tag_overhead_correction_confidence",
    "string.custom_data_padding_confidence",
    "string_array.builtin_confidence",
    "string_array.custom_confidence",
    "udt.alignment_confidence",
    "array.atomic_confidence",
    "array.udt_confidence",
    "cmp_surcharge.compound_confidence",
    "logic_instructions.aoi_internal_per_word_destination_confidence",
}


def test_every_known_tier_key_in_the_yaml_is_registered_here():
    """A new `*_confidence: KNOWN` must arrive with its evidence.

    Without this, marking something KNOWN is free and the register rots. Only the
    per-constant tiers are checked -- block-level `confidence:` keys are a
    statement about how a whole block was derived and have their own entries.
    """
    raw = _raw()
    registered = {entry[2] for entry in KNOWN_REGISTER} | PRE_EXISTING_KNOWN
    registered |= {f"logic_instructions.weight_confidence.{m}"
                   for m in raw["logic_instructions"]["weight_confidence"]}

    def walk(node, prefix=""):
        if not isinstance(node, dict):
            return
        for key, value in node.items():
            if not isinstance(key, str):
                continue
            path = f"{prefix}{key}"
            if (key.endswith("_confidence") and value == "KNOWN"
                    and key != "confidence"):
                assert path in registered, (
                    f"{path} is marked KNOWN but has no entry in KNOWN_REGISTER. "
                    f"Add it with the row count and what those rows span."
                )
            walk(value, f"{path}.")

    walk(raw)
