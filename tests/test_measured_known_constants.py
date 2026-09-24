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
        "indirect_index.member_access_cost", 40,
        "indirect_index.member_access_confidence", 6,
        "opsp_ind_mov_e04/e08/e12/e76_idx, opsp_ind_equ_e76_idx and opsp_ind_xicmem_idx "
        "against their literal-index twins, 500 rungs each on the realism floor: "
        "every one +40 per index over the 84 index cost, element size irrelevant; "
        "OQ-INDIRECTUDT",
    ),
    (
        "logic_instructions.fixed_base_per_routine", 4816,
        "logic_instructions.fixed_base_per_routine_confidence", 12,
        "empty-project baseline plus subrtn_shell/sbronly/sbrret at 1/5/25/100 "
        "routines, all at 0.000%",
    ),
    (
        "task_program_overhead.task_extra", 700,
        "task_program_overhead.confidence", 7,
        "taskoverhead_n02tasks/_n03tasks exact and identnamelen_task_c04..c40 "
        "(six tasks, names 4..40 chars) exact; _n04tasks' +24 is task-name "
        "rounding, OQ-TASKNAMEROUND",
    ),
    (
        "aoi_definition.total_alignment_bytes", 8,
        "aoi_definition.confidence", 125,
        "125 def-only AOI captures: 68 exact, 117 inside +/-8 once aligned; "
        "every file the unaligned sum put at 4 mod 8 read 4 high; OQ-AOIDEFSHAPE",
    ),
    (
        "aoi_definition.base", 1163,
        "aoi_definition.confidence", 125,
        "the same 125 def-only captures; real-shape ladder confirms "
        "1,231 per definition against 1,233 predicted over 5..40 definitions",
    ),
    (
        "aoi_definition.name_length_bucket_bytes", 8,
        "aoi_definition.name_length_bucket_confidence", 7,
        "aoiname_len08/09/13/16/20/25/30_def_only, 7/7 exact, only the type "
        "name length varying",
    ),
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
        "definition_scale_correction.aoi_definition_extra", -7,
        "definition_scale_correction.aoi_definition_extra_confidence", 7,
        "defscale_aoidefs_n001..n060, definition count the only variable",
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


# Per-constant KNOWN tiers that predate this register. Every one is
# derived and justified in a comment at its own definition site in
# memory_model.yaml, and most are the exactly-calculable data-space side CLAUDE.md
# distinguishes from fitted logic sizing -- BOOL packing, STRING layout, UDT
# alignment, array element sizing. They are listed rather than re-documented here
# because inventing row counts for measurements someone else took would be worse
# than naming them: the point of the guard below is to stop NEW tiers arriving
# without evidence, not to re-audit the old ones.
# `structured_text.st_aoi_call_routine_bytes` was in this register on the day it
# was wired and came straight back out. The 264 is measured; what is NOT measured
# is whether it is charged per ROUTINE or per FILE, because all 80 files in the
# corpus that contain an AOI call have exactly one calling routine. A constant
# whose carrier is assumed is not KNOWN, whatever its value, so it is FITTED --
# and the register is what forced that to be said out loud.
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
