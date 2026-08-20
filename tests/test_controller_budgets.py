from l5x_memory_analyzer.sizing.controller_budgets import (
    DIVIDED,
    UNIFIED,
    load_controller_budgets,
)

TABLE = load_controller_budgets()


def test_unified_processor_exact_match():
    b = TABLE.lookup("1756-L83E")
    assert b.architecture == UNIFIED
    assert b.display_total_bytes == 10485760


def test_prefix_match_ignores_safety_suffix():
    # Real L5X data (2026-08-20): "1756-L81ES" -- the S is a safety-capable
    # base, not a different memory tier.
    b = TABLE.lookup("1756-L81ES")
    assert b is not None
    assert b.catalog_prefix == "1756-L81E"
    assert b.display_total_bytes == 3145728


def test_unknown_processor_returns_none_not_a_guess():
    assert TABLE.lookup("1769-L33ERMS") is None  # older CompactLogix 5370, not in table
    assert TABLE.lookup(None) is None
    assert TABLE.lookup("totally-fake-part") is None


def test_divided_architecture_sums_both_pools_for_display():
    b = TABLE.lookup("1756-L73")
    assert b.architecture == DIVIDED
    assert b.display_total_bytes == b.data_logic_bytes + b.io_bytes
    assert b.display_total_bytes == 8388608 + 1028096


def test_longest_prefix_wins():
    b = TABLE.lookup("5069-L3100ERMS3")
    assert b.catalog_prefix == "5069-L3100ER"
