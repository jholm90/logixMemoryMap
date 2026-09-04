"""Loads sizing constants from memory_model.yaml (mirrors docs/MEMORY_MODEL.md).

Parser/sizing code must pull byte sizes and packing rules from here, never
hardcode them inline -- see CLAUDE.md working agreement.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

_DEFAULT_PATH = Path(__file__).with_name("memory_model.yaml")


@dataclass(frozen=True)
class AtomicType:
    bytes: int
    confidence: str


@dataclass(frozen=True)
class BoolModel:
    standalone_tag_bytes: int
    standalone_confidence: str
    member_bits_per_backing_byte: int
    member_backing_type: str
    member_confidence: str
    array_bits_per_packed_word: int
    array_packed_word_bytes: int
    array_confidence: str


@dataclass(frozen=True)
class StringModel:
    len_field_bytes: int
    default_data_bytes: int
    confidence: str
    custom_confidence: str
    custom_definition_base: int
    custom_definition_namelen_offset: int
    custom_definition_namelen_bucket: int
    custom_definition_confidence: str
    builtin_tag_overhead_correction: int
    builtin_tag_overhead_correction_confidence: str
    custom_data_padding_multiple: int
    custom_mod4eq1_definition_bonus: int
    custom_data_padding_confidence: str

    def custom_definition_cost_for(self, type_name_length: int) -> int:
        """Custom StringFamily type's own one-time definition cost --
        OQ-CUSTOMSTRINGTYPENAME, SOLVED 2026-08-26. A clean step function
        of the type's own name length, confirmed exact against 22 real
        dense-sweep points (every length 1-16 plus 20/24/28/32/36/40) and
        3 more confirming it's identical whether the type is used
        standalone or as a UDT member (no separate nesting cost) -- see
        memory_model.yaml for the full derivation."""
        bucket = self.custom_definition_namelen_bucket
        return self.custom_definition_base + bucket * (
            (type_name_length - self.custom_definition_namelen_offset) // bucket
        )


@dataclass(frozen=True)
class StringArrayModel:
    builtin_confidence: str
    builtin_array_base: int
    builtin_per_element: int
    custom_confidence: str
    custom_array_base: int
    custom_per_element: int


@dataclass(frozen=True)
class PredefinedArrayStructure:
    base: int
    per_element: int
    confidence: str


@dataclass(frozen=True)
class UdtModel:
    alignment_confidence: str


@dataclass(frozen=True)
class ArrayModel:
    atomic_confidence: str
    udt_confidence: str


@dataclass(frozen=True)
class AoiArrayModel:
    flat_discount: int
    bool_word_size: int
    bool_word_extra: int
    confidence: str


@dataclass(frozen=True)
class AoiDefinitionModel:
    base: int
    per_declared_item: int
    per_type_rate: dict[str, int]
    confidence: str
    name_length_bucket_bytes: int
    name_length_floor_bytes: int
    name_length_bucket_confidence: str

    def bytes_for(self, type_counts: dict[str, int], name: str = "") -> int:
        # per_type_rate only applies when every declared item shares the
        # SAME type -- confirmed real that per-type rates do NOT compose
        # additively once BOOL sits alongside another type (see
        # memory_model.yaml aoi_definition for the mixed-type evidence), so
        # a mixed-type AOI definition falls back to the flat per_declared_item
        # rate for every item rather than risk a worse per-type sum.
        total_items = sum(type_counts.values())
        if len(type_counts) == 1:
            (only_type,) = type_counts
            rate = self.per_type_rate.get(only_type, self.per_declared_item)
            total = self.base + rate * total_items
        else:
            total = self.base + self.per_declared_item * total_items
        return total + self.name_length_bytes(name)

    def name_length_bytes(self, name: str) -> int:
        # OQ-AOIDEF closeout, wired 2026-08-29 -- real data
        # (aoiname_len08/09/13/16/20/25/30) confirmed 7/7 exact against
        # `8*max(0,(len-8)//4) - 8`. Unlike UDT-definition's own
        # 8*ceil(len/8) step, an AOI type name's cost isn't purely
        # length-driven: there's a flat -8 floor (matching the same
        # -8-byte universal per-file residual seen throughout this
        # project) that any name length 8-9 hits, THEN +8 every 4
        # characters beyond that -- see memory_model.yaml aoi_definition
        # for the full derivation. Not confirmed below len=8 (no real
        # data there), but the bucket floors at the same -8 rather than
        # extrapolating further negative for very short names.
        #
        # Bucket boundary fixed 2026-08-30: the original `(len-7)//4`
        # divisor (chosen to fit only the 7 tested lengths, which happen
        # to skip every len==3 (mod 4)) put len=19 one bucket too high.
        # Cross-checked against real captures of two same-shape (10 BOOL
        # In/10 BOOL Out/10 BOOL Local) AOI array-packing files that only
        # differ by AOI type name length -- AoiPureBoolDense (16 chars,
        # confirmed bucket2) and AoiPureBoolBoundary (19 chars) -- every
        # count point (n=16) lands on the exact same total byte count
        # under `(len-8)//4` (bucket2 for both) but disagreed by 8 bytes
        # under the old divisor (which put len=19 in bucket3). The 7
        # originally-tested lengths (8,9,13,16,20,25,30) are all
        # unaffected by this change; only len%4==3 (11,15,19,23,27,...)
        # shifts down one bucket.
        bucket = max(0, (len(name) - 8) // 4)
        return self.name_length_bucket_bytes * bucket + self.name_length_floor_bytes


@dataclass(frozen=True)
class TagOverheadModel:
    flat_base: int
    per_8_chars: int
    confidence: str

    def bytes_for(self, name: str) -> int:
        return self.flat_base + self.per_8_chars * (len(name) // 8)


@dataclass(frozen=True)
class UdtDefinitionModel:
    base: int
    per_member: int
    name_per_8_chars: int
    bool_run_bonus: int
    confidence: str

    def bytes_for(self, name: str, declared_member_count: int, bool_run_count: int) -> int:
        # ONE shared base -- see memory_model.yaml udt_definition for why
        # this isn't two separately-additive base constants (168 for
        # member-count, 224 for name-length): those were two different 1-D
        # slices through the same 2-variable surface, both correct in
        # isolation (holding the other variable at its sweep's baseline),
        # but adding them together double-counts the shared base they
        # both include. Solving the two slices simultaneously gives one
        # true base of 160. bool_run_bonus applies once per separate BOOL
        # run (each with its own hidden backing SINT) -- a non-BOOL member
        # breaking a run means a second hidden SINT and a second bonus.
        total = self.base + self.per_member * declared_member_count + self.name_per_8_chars * math.ceil(len(name) / 8)
        total += self.bool_run_bonus * bool_run_count
        return total


@dataclass(frozen=True)
class CptRealDestModel:
    """REAL-destination CPT cost (OQ-CMPCPTLAYOUT, wired 2026-09-04) -- see
    memory_model.yaml cpt_expression.real_dest for the full derivation and
    the flagged coverage gaps."""

    first_operator: int
    extra_operator: int
    single_pow_extra: int
    five_plus_operator_extra: int
    per_int_operand: int
    per_float_literal: int
    confidence: str

    def cost_for(
        self, operators: list[str], n_int_operands: int, n_float_literals: int, base_read: int
    ) -> int:
        n_ops = len(operators)
        if n_ops == 0:
            # A bare REAL copy, 'CPT(R1,R0)' -- no operators, so no float
            # arithmetic to charge differently. Falls through to the plain
            # base_read the integer path would have charged.
            return base_read + self.per_int_operand * n_int_operands
        total = base_read + self.first_operator + self.extra_operator * (n_ops - 1)
        if n_ops == 1 and operators[0] == "**":
            total += self.single_pow_extra
        if n_ops >= 5:
            total += self.five_plus_operator_extra
        return (
            total
            + self.per_int_operand * n_int_operands
            + self.per_float_literal * n_float_literals
        )


@dataclass(frozen=True)
class CptExpressionModel:
    base_read: int
    operator_tier_costs: dict[str, int]
    per_extra_same_tier_operand: int
    two_tier_mix_base: int
    two_tier_mix_per_operator: int
    pow_tier_mix_base: int
    pow_tier_mix_per_operator: int
    three_tier_mix_base_by_remainder: dict[int, int]
    three_tier_mix_per_pow_operand: int
    real_dest: "CptRealDestModel"

    def cost_for(self, operators: list[str]) -> int:
        """Real per-call CPT cost from its expression's operator tokens
        (OQ-CMPCPTLAYOUT, wired 2026-08-26) -- see memory_model.yaml
        cpt_expression for the full derivation. A UNIFORM expression (every
        operator the same tier -- covers plain chains like A+B+C+D, the
        dominant real usage pattern) is exact: confirmed 0 residual across
        the n=1 operand-count sweep (1-10 operands) AND the n=1000
        chain-length sweep (3/4/5/6/8/10 operands), independently.

        A MIXED expression using EXACTLY the ADD/SUB and MUL/DIV/MOD tiers
        together (no POW) is ALSO exact now, 2026-08-26: `two_tier_mix_base
        + two_tier_mix_per_operator * operator_count`, confirmed at 4 of 5
        real operand-count points (3/5/11/15 operands exact, 8 operands off
        by the same small universal noise seen throughout this project) --
        order/arrangement doesn't matter (alternating vs grouped tiers give
        the same result).

        A MIXED expression using POW alongside EXACTLY ONE other tier (T1T3
        or T2T3) is ALSO exact now, 2026-08-25: `pow_tier_mix_base +
        pow_tier_mix_per_operator * operator_count`, wired from real capture
        data that already existed in manifest.csv (2026-08-24) but had never
        been reconciled into a formula. T1T3 and T2T3 give IDENTICAL real
        bytes at every one of 5 tested operator counts (2/4/7/10/14) --
        once POW is present, the OTHER tier (T1 vs T2) makes no measurable
        difference, so one formula covers both pairs. 4 of 5 points exact
        (k=2,4,10,14), k=7 off by the same +16 this project's other CPT
        formulas also miss by at that specific operator count -- a
        file-specific quirk, not a per-formula one. See memory_model.yaml
        cpt_expression for the full derivation.

        A mix using ALL 3 tiers together (ADD/SUB + MUL/DIV/MOD + POW) is
        ALSO exact now, 2026-08-29 (OQ-CMPCPTLAYOUT closeout): a real
        correction on top of the plain per-operator-tier sum,
        `three_tier_mix_base_by_remainder[operator_count % 3] +
        three_tier_mix_per_pow_operand * pow_operand_count`. Confirmed 0
        residual across all 9 real all-3-tier data points spanning
        operator counts 4-14 (the original n=3/5/8/10/11/15 sweep plus 3
        new remainder-2 probes at n=6/9/12) -- see memory_model.yaml
        cpt_expression for the full derivation. `operator_count % 3`
        determines the class deterministically from the [+,*,**]-cycling
        construction any real alternating 3-tier expression follows: which
        of the 3 tiers ends up with one extra operator. remainder=0
        (T1==T2==T3) rests on a single real point (n=10) -- same slope as
        the other two remainder classes (independently confirmed at 3 and
        4 points each), just one point short of independent confirmation
        for its own base constant.
        """
        if not operators:
            return self.base_read
        tiers = [self.operator_tier_costs[op] for op in operators]
        if len(set(tiers)) == 1:
            return self.base_read + tiers[0] + self.per_extra_same_tier_operand * (len(operators) - 1)
        add_tier = self.operator_tier_costs["+"]
        mul_tier = self.operator_tier_costs["*"]
        pow_tier = self.operator_tier_costs["**"]
        if set(tiers) == {add_tier, mul_tier}:
            return self.two_tier_mix_base + self.two_tier_mix_per_operator * len(operators)
        if set(tiers) in ({add_tier, pow_tier}, {mul_tier, pow_tier}):
            return self.pow_tier_mix_base + self.pow_tier_mix_per_operator * len(operators)
        pow_operand_count = tiers.count(pow_tier)
        remainder = len(operators) % 3
        correction = self.three_tier_mix_base_by_remainder[remainder] + \
            self.three_tier_mix_per_pow_operand * pow_operand_count
        return self.base_read + sum(tiers) + correction


@dataclass(frozen=True)
class OperandTypeSurchargeModel:
    confidence: str
    surcharges: dict[str, dict[str, int]]  # instruction -> {atomic_type: extra bytes/call}

    def surcharge_for(self, mnemonic: str, atomic_type: str) -> int:
        return self.surcharges.get(mnemonic, {}).get(atomic_type, 0)


@dataclass(frozen=True)
class IndirectIndexModel:
    confidence: str
    tag_index_cost: int
    tag_offset_index_cost: int

    def cost_for(self, kind: str) -> int:
        if kind == "tag":
            return self.tag_index_cost
        if kind == "tag_offset":
            return self.tag_offset_index_cost
        return 0


@dataclass(frozen=True)
class CmpSurchargeModel:
    compound_confidence: str
    compound_cost: int
    float_literal_confidence: str
    float_literal_cost: int


@dataclass(frozen=True)
class TaskProgramOverheadModel:
    routine_extra: int
    program_extra: int
    task_extra: int
    confidence: str


@dataclass(frozen=True)
class JsrParamCostModel:
    """Real per-param JSR cost (OQ-JSRPARAMCOST, wired 2026-08-25):
    `delta(n,R) = A(n) + B(n)*R`, `A(n) = a_base + a_per_param*n` (a
    one-time cost of the callee's own Parameters-block declaration, paid
    once per distinct target routine regardless of call-site count) and
    `B(n) = b_base + b_per_param*n` (the true per-call-site marginal
    rate). Confirmed exact at 3 real (n,B) points (n=5,8,10) -- see
    memory_model.yaml jsr_param_cost for the derivation. output_param_cost
    (wired 2026-08-29): the per-call cost of each trailing RETURN-value
    argument a JSR passes back, charged once per output arg per call site
    -- a real, previously completely unmodeled cost (see
    memory_model.yaml jsr_param_cost for the 2-file derivation)."""
    a_base: int
    a_per_param: int
    b_base: int
    b_per_param: int
    confidence: str
    output_param_cost: int

    def a_cost(self, n: int) -> int:
        return self.a_base + self.a_per_param * n

    def b_cost(self, n: int) -> int:
        return self.b_base + self.b_per_param * n


@dataclass(frozen=True)
class LogicInstructionModel:
    fixed_base_per_routine: int
    jsr_fixed_base_per_routine: int
    confidence: str
    weights: dict[str, int]
    cpt_expression: CptExpressionModel
    operand_type_surcharge: OperandTypeSurchargeModel
    indirect_index: IndirectIndexModel
    cmp_surcharge: CmpSurchargeModel
    task_program_overhead: TaskProgramOverheadModel
    jsr_param_cost: JsrParamCostModel
    branch_bracket_cost_per_instruction: int
    branch_bracket_confidence: str
    aoi_logic_composite_surcharge_per_instr: int
    jsr_target_composite_surcharge_per_instr: int
    composite_surcharge_confidence: str
    composite_surcharge_cap: int
    safety_task_program_shell: int
    safety_task_program_shell_confidence: str


@dataclass(frozen=True)
class FirmwareBaselineDeltaModel:
    """Real per-firmware-major-version delta over the confirmed v34/v35
    baseline (OQ-BASELINE-PROCFW, wired 2026-08-29) -- see memory_model.yaml
    firmware_baseline_delta for the full derivation and which manifest.csv
    rows it's fitted from. Keyed by the integer major version parsed out of
    the L5X root's own SoftwareRevision attribute (e.g. "31.02" -> "31");
    any major not in the table (including v34/v35 themselves, and any
    firmware with no real sample) falls back to default_bytes/
    default_confidence -- i.e. no adjustment."""
    by_major_version: dict[str, tuple[int, str]]
    default_bytes: int
    default_confidence: str

    def delta_for(self, software_revision: str | None) -> tuple[int, str]:
        if not software_revision:
            return self.default_bytes, self.default_confidence
        major = software_revision.split(".")[0]
        return self.by_major_version.get(major, (self.default_bytes, self.default_confidence))


@dataclass(frozen=True)
class SafetyCapableBaselineDeltaModel:
    """Real 5069 safety-CAPABLE processor baseline overhead, independent of
    actual SafetyInfo/SafetyTask content (OQ-BASELINE-PROCFW, wired
    2026-08-29) -- see memory_model.yaml safety_capable_baseline_delta for
    the full derivation (n=2 real catalogs, extended to the whole
    safety-suffix family the same way this project already extends L71's
    confirmed shape to L72-L75). catalog_suffix_pattern is matched against
    the L5X Controller element's own ProcessorType attribute."""
    bytes: int
    confidence: str
    catalog_suffix_pattern: str

    def applies_to(self, processor_type: str | None) -> bool:
        if not processor_type:
            return False
        return bool(re.search(self.catalog_suffix_pattern, processor_type))


@dataclass(frozen=True)
class ModuleOverheadModel:
    """Real per-catalog module overhead (OQ-MODULEIO, wired 2026-08-29) --
    see memory_model.yaml module_overhead_by_catalog for the full
    derivation and which catalogs were deliberately left off (adapter/
    bridge catalogs that may be absorbing a rack of aliased children,
    generic-catalog placeholders whose overhead scales with declared I/O
    size, and a few real connection-variant-dependent cases). Any catalog
    not in the table falls back to the flat default_bytes/
    default_confidence -- the same flat FITTED-from-2-points estimate this
    project used everywhere before this table existed."""
    by_catalog: dict[str, tuple[int, str]]
    default_bytes: int
    default_confidence: str

    def overhead_for(self, catalog_number: str | None) -> tuple[int, str]:
        if not catalog_number:
            return self.default_bytes, self.default_confidence
        return self.by_catalog.get(catalog_number, (self.default_bytes, self.default_confidence))

    def has_real_data_for(self, catalog_number: str | None) -> bool:
        """True if this SPECIFIC catalog has its own real capture point here,
        as opposed to falling back to the flat cross-catalog default. Lets
        report.py's rack-aliased/legacy-network exclusion (real data
        confirms module_overhead does NOT apply the same way to those
        shapes in general) still charge a catalog that DOES have its own
        confirmed real value despite being one of those shapes -- see
        memory_model.yaml's 2026-08-31 comment for the derivation."""
        return bool(catalog_number) and catalog_number in self.by_catalog


@dataclass(frozen=True)
class CatalogBaselineDeltaModel:
    """Real per-catalog baseline delta for processor families whose real
    empty-project baseline diverges enormously from the flat
    empty_project_baseline (OQ-BASELINE-PROCFW, 1769-series thread, wired
    2026-08-29) -- see memory_model.yaml catalog_baseline_delta for the
    full derivation. Exact ProcessorType string match only, deliberately
    NOT prefix/suffix-pattern-matched like safety_capable_baseline_delta
    -- real data shows a single expansion-module suffix character (e.g.
    `-QB1B` vs `-QBFC1B`) changes the real value by over 13,000 bytes, so
    extrapolating beyond an exact confirmed catalog string would be a
    guess, not a real value."""
    by_processor_type: dict[str, tuple[int, str]]

    def delta_for(self, processor_type: str | None) -> tuple[int, str] | None:
        if not processor_type:
            return None
        return self.by_processor_type.get(processor_type)


@dataclass(frozen=True)
class AlarmConditionModel:
    """Exact cost of tag-based alarm conditions -- see memory_model.yaml
    alarm_conditions and sizing/alarms.py. Reproduces all 37 captured
    alarmcond_* points with zero residual."""

    file_base: int
    per_condition: int
    per_associated_tag_by_type: dict[str, int]
    associated_tag_default: int
    confidence: str

    def assoc_tag_cost(self, resolved_type: str | None) -> int:
        """An unresolved reference is charged the STRING rate -- the most
        expensive -- so a partial export over-states rather than silently
        under-states."""
        if resolved_type is None:
            return self.associated_tag_default
        return self.per_associated_tag_by_type.get(resolved_type, self.associated_tag_default)


@dataclass(frozen=True)
class StructuredTextModel:
    """Cost of Structured Text routines -- see memory_model.yaml
    structured_text and sizing/structured_text.py.

    The headline result, and the reason this is a thin model rather than a
    parallel weight table: ST costs EXACTLY what RLL costs for the same
    instruction, plus one flat per-routine shell. Four ST/RLL pairs built
    to be operand-for-operand identical came back separated by exactly
    +432 every time, with no other term:

        st_instr_cop_n01000    135,376  vs  instr_cop_n01000   134,944
        st_instr_dtos_n01000    95,376  vs  instr_dtos_n01000   94,944
        st_instr_size_n01000   151,376  vs  instr_size_n01000  150,944
        st_expr_cpt_mirror_n01000 475,376 vs instr_cpt_n01000  474,944

    So the whole per-instruction weight table, and the tier-aware CPT
    expression model, transfer to ST unchanged. What ST adds on top is a
    per-statement cost and per-construct control-flow costs, all measured
    against a common 100-statement control.
    """

    per_statement: int
    per_statement_literal_rhs: int
    routine_shell: int
    if_block: int
    elsif_branch: int
    case_block: int
    for_block: int
    while_block: int
    comments_and_blanks: int
    confidence: str
    # "<n_operators>|<dest_is_real>" -> measured bytes. Sparse on purpose --
    # see the memory_model.yaml comment. A shape not in here is NOT
    # interpolated; sizing/structured_text.py reports it as a coverage gap.
    assignment_expression_cost: dict[str, int]
    assignment_expression_confidence: str

    def assignment_cost(self, n_operators: int, dest_is_real: bool) -> int | None:
        """Measured cost for this assignment shape, or None if unmeasured."""
        return self.assignment_expression_cost.get(f"{n_operators}|{str(dest_is_real).lower()}")


@dataclass(frozen=True)
class MemoryModel:
    atomic_types: dict[str, AtomicType]
    predefined_structures: dict[str, AtomicType]
    predefined_array_structures: dict[str, PredefinedArrayStructure]
    bool: BoolModel
    string: StringModel
    string_array: StringArrayModel
    udt: UdtModel
    array: ArrayModel
    aoi_array: AoiArrayModel
    aoi_definition: AoiDefinitionModel
    tag_overhead: TagOverheadModel
    alias_overhead: TagOverheadModel
    udt_definition: UdtDefinitionModel
    logic_instructions: LogicInstructionModel
    alarm_conditions: AlarmConditionModel
    structured_text: StructuredTextModel
    empty_project_baseline_bytes: int
    empty_project_baseline_confidence: str
    module_overhead_bytes: int
    module_overhead_confidence: str
    module_overhead_by_catalog: ModuleOverheadModel
    firmware_baseline_delta: FirmwareBaselineDeltaModel
    safety_capable_baseline_delta: SafetyCapableBaselineDeltaModel
    catalog_baseline_delta: CatalogBaselineDeltaModel


def load_memory_model(path: str | Path | None = None) -> MemoryModel:
    path = Path(path) if path else _DEFAULT_PATH
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    atomic_types = {
        name: AtomicType(bytes=v["bytes"], confidence=v["confidence"])
        for name, v in raw["atomic_types"].items()
    }
    predefined_structures = {
        name: AtomicType(bytes=v["bytes"], confidence=v["confidence"])
        for name, v in raw.get("predefined_structures", {}).items()
    }
    predefined_array_structures = {
        name: PredefinedArrayStructure(base=v["base"], per_element=v["per_element"], confidence=v["confidence"])
        for name, v in raw.get("predefined_array_structures", {}).items()
    }
    b = raw["bool"]
    s = raw["string"]
    baseline = raw["empty_project_baseline"]
    module_overhead = raw["module_overhead"]
    module_overhead_by_catalog = raw.get("module_overhead_by_catalog", {})
    fw_delta = raw["firmware_baseline_delta"]
    safety_delta = raw["safety_capable_baseline_delta"]
    catalog_delta = raw.get("catalog_baseline_delta", {})
    return MemoryModel(
        atomic_types=atomic_types,
        predefined_structures=predefined_structures,
        predefined_array_structures=predefined_array_structures,
        structured_text=StructuredTextModel(
            per_statement=raw["structured_text"]["per_statement"],
            per_statement_literal_rhs=raw["structured_text"]["per_statement_literal_rhs"],
            routine_shell=raw["structured_text"]["routine_shell"],
            if_block=raw["structured_text"]["if_block"],
            elsif_branch=raw["structured_text"]["elsif_branch"],
            case_block=raw["structured_text"]["case_block"],
            for_block=raw["structured_text"]["for_block"],
            while_block=raw["structured_text"]["while_block"],
            comments_and_blanks=raw["structured_text"]["comments_and_blanks"],
            assignment_expression_cost={
                str(k): v for k, v in
                raw["structured_text"].get("assignment_expression_cost", {}).items()
            },
            assignment_expression_confidence=raw["structured_text"].get(
                "assignment_expression_confidence", "UNKNOWN"),
            confidence=raw["structured_text"]["confidence"],
        ),
        alarm_conditions=AlarmConditionModel(
            file_base=raw["alarm_conditions"]["file_base"],
            per_condition=raw["alarm_conditions"]["per_condition"],
            per_associated_tag_by_type=dict(raw["alarm_conditions"]["per_associated_tag_by_type"]),
            associated_tag_default=raw["alarm_conditions"]["associated_tag_default"],
            confidence=raw["alarm_conditions"]["confidence"],
        ),
        empty_project_baseline_bytes=baseline["bytes"],
        empty_project_baseline_confidence=baseline["confidence"],
        module_overhead_bytes=module_overhead["bytes"],
        module_overhead_confidence=module_overhead["confidence"],
        module_overhead_by_catalog=ModuleOverheadModel(
            by_catalog={
                catalog: (v["bytes"], v["confidence"])
                for catalog, v in module_overhead_by_catalog.items()
            },
            default_bytes=module_overhead["bytes"],
            default_confidence=module_overhead["confidence"],
        ),
        firmware_baseline_delta=FirmwareBaselineDeltaModel(
            by_major_version={
                major: (v["bytes"], v["confidence"])
                for major, v in fw_delta["by_major_version"].items()
            },
            default_bytes=fw_delta["default_bytes"],
            default_confidence=fw_delta["default_confidence"],
        ),
        safety_capable_baseline_delta=SafetyCapableBaselineDeltaModel(
            bytes=safety_delta["bytes"],
            confidence=safety_delta["confidence"],
            catalog_suffix_pattern=safety_delta["catalog_suffix_pattern"],
        ),
        catalog_baseline_delta=CatalogBaselineDeltaModel(
            by_processor_type={
                proc_type: (v["bytes"], v["confidence"])
                for proc_type, v in catalog_delta.items()
            },
        ),
        bool=BoolModel(
            standalone_tag_bytes=b["standalone_tag_bytes"],
            standalone_confidence=b["standalone_confidence"],
            member_bits_per_backing_byte=b["member_bits_per_backing_byte"],
            member_backing_type=b["member_backing_type"],
            member_confidence=b["member_confidence"],
            array_bits_per_packed_word=b["array_bits_per_packed_word"],
            array_packed_word_bytes=b["array_packed_word_bytes"],
            array_confidence=b["array_confidence"],
        ),
        string=StringModel(
            len_field_bytes=s["len_field_bytes"],
            default_data_bytes=s["default_data_bytes"],
            confidence=s["confidence"],
            custom_confidence=s["custom_confidence"],
            custom_definition_base=s["custom_definition_base"],
            custom_definition_namelen_offset=s["custom_definition_namelen_offset"],
            custom_definition_namelen_bucket=s["custom_definition_namelen_bucket"],
            custom_definition_confidence=s["custom_definition_confidence"],
            builtin_tag_overhead_correction=s["builtin_tag_overhead_correction"],
            builtin_tag_overhead_correction_confidence=s["builtin_tag_overhead_correction_confidence"],
            custom_data_padding_multiple=s["custom_data_padding_multiple"],
            custom_mod4eq1_definition_bonus=s["custom_mod4eq1_definition_bonus"],
            custom_data_padding_confidence=s["custom_data_padding_confidence"],
        ),
        string_array=StringArrayModel(
            builtin_confidence=raw["string_array"]["builtin_confidence"],
            builtin_array_base=raw["string_array"]["builtin_array_base"],
            builtin_per_element=raw["string_array"]["builtin_per_element"],
            custom_confidence=raw["string_array"]["custom_confidence"],
            custom_array_base=raw["string_array"]["custom_array_base"],
            custom_per_element=raw["string_array"]["custom_per_element"],
        ),
        udt=UdtModel(alignment_confidence=raw["udt"]["alignment_confidence"]),
        array=ArrayModel(
            atomic_confidence=raw["array"]["atomic_confidence"],
            udt_confidence=raw["array"]["udt_confidence"],
        ),
        aoi_array=AoiArrayModel(
            flat_discount=raw["aoi_array"]["flat_discount"],
            bool_word_size=raw["aoi_array"]["bool_word_size"],
            bool_word_extra=raw["aoi_array"]["bool_word_extra"],
            confidence=raw["aoi_array"]["confidence"],
        ),
        aoi_definition=AoiDefinitionModel(
            base=raw["aoi_definition"]["base"],
            per_declared_item=raw["aoi_definition"]["per_declared_item"],
            per_type_rate=raw["aoi_definition"].get("per_type_rate", {}),
            confidence=raw["aoi_definition"]["confidence"],
            name_length_bucket_bytes=raw["aoi_definition"]["name_length_bucket_bytes"],
            name_length_floor_bytes=raw["aoi_definition"]["name_length_floor_bytes"],
            name_length_bucket_confidence=raw["aoi_definition"]["name_length_bucket_confidence"],
        ),
        tag_overhead=TagOverheadModel(
            flat_base=raw["tag_overhead"]["flat_base"],
            per_8_chars=raw["tag_overhead"]["per_8_chars"],
            confidence=raw["tag_overhead"]["confidence"],
        ),
        alias_overhead=TagOverheadModel(
            flat_base=raw["alias_overhead"]["flat_base"],
            per_8_chars=raw["alias_overhead"]["per_8_chars"],
            confidence=raw["alias_overhead"]["confidence"],
        ),
        udt_definition=UdtDefinitionModel(
            base=raw["udt_definition"]["base"],
            per_member=raw["udt_definition"]["per_member"],
            name_per_8_chars=raw["udt_definition"]["name_per_8_chars"],
            bool_run_bonus=raw["udt_definition"]["bool_run_bonus"],
            confidence=raw["udt_definition"]["confidence"],
        ),
        logic_instructions=LogicInstructionModel(
            fixed_base_per_routine=raw["logic_instructions"]["fixed_base_per_routine"],
            jsr_fixed_base_per_routine=raw["logic_instructions"]["jsr_fixed_base_per_routine"],
            confidence=raw["logic_instructions"]["confidence"],
            weights=dict(raw["logic_instructions"]["weights"]),
            cpt_expression=CptExpressionModel(
                base_read=raw["cpt_expression"]["base_read"],
                operator_tier_costs=dict(raw["cpt_expression"]["operator_tier_costs"]),
                per_extra_same_tier_operand=raw["cpt_expression"]["per_extra_same_tier_operand"],
                two_tier_mix_base=raw["cpt_expression"]["two_tier_mix_base"],
                two_tier_mix_per_operator=raw["cpt_expression"]["two_tier_mix_per_operator"],
                pow_tier_mix_base=raw["cpt_expression"]["pow_tier_mix_base"],
                pow_tier_mix_per_operator=raw["cpt_expression"]["pow_tier_mix_per_operator"],
                three_tier_mix_base_by_remainder={
                    int(k): v for k, v in raw["cpt_expression"]["three_tier_mix_base_by_remainder"].items()
                },
                three_tier_mix_per_pow_operand=raw["cpt_expression"]["three_tier_mix_per_pow_operand"],
                real_dest=CptRealDestModel(
                    first_operator=raw["cpt_expression"]["real_dest"]["first_operator"],
                    extra_operator=raw["cpt_expression"]["real_dest"]["extra_operator"],
                    single_pow_extra=raw["cpt_expression"]["real_dest"]["single_pow_extra"],
                    five_plus_operator_extra=raw["cpt_expression"]["real_dest"]["five_plus_operator_extra"],
                    per_int_operand=raw["cpt_expression"]["real_dest"]["per_int_operand"],
                    per_float_literal=raw["cpt_expression"]["real_dest"]["per_float_literal"],
                    confidence=raw["cpt_expression"]["real_dest"]["confidence"],
                ),
            ),
            operand_type_surcharge=OperandTypeSurchargeModel(
                confidence=raw["operand_type_surcharge"]["confidence"],
                surcharges={
                    instr: dict(types)
                    for instr, types in raw["operand_type_surcharge"]["surcharges"].items()
                },
            ),
            indirect_index=IndirectIndexModel(
                confidence=raw["indirect_index"]["confidence"],
                tag_index_cost=raw["indirect_index"]["tag_index_cost"],
                tag_offset_index_cost=raw["indirect_index"]["tag_offset_index_cost"],
            ),
            cmp_surcharge=CmpSurchargeModel(
                compound_confidence=raw["cmp_surcharge"]["compound_confidence"],
                compound_cost=raw["cmp_surcharge"]["compound_cost"],
                float_literal_confidence=raw["cmp_surcharge"]["float_literal_confidence"],
                float_literal_cost=raw["cmp_surcharge"]["float_literal_cost"],
            ),
            task_program_overhead=TaskProgramOverheadModel(
                routine_extra=raw["task_program_overhead"]["routine_extra"],
                program_extra=raw["task_program_overhead"]["program_extra"],
                task_extra=raw["task_program_overhead"]["task_extra"],
                confidence=raw["task_program_overhead"]["confidence"],
            ),
            jsr_param_cost=JsrParamCostModel(
                a_base=raw["jsr_param_cost"]["a_base"],
                a_per_param=raw["jsr_param_cost"]["a_per_param"],
                b_base=raw["jsr_param_cost"]["b_base"],
                b_per_param=raw["jsr_param_cost"]["b_per_param"],
                confidence=raw["jsr_param_cost"]["confidence"],
                output_param_cost=raw["jsr_param_cost"]["output_param_cost"],
            ),
            branch_bracket_cost_per_instruction=raw["logic_instructions"]["branch_bracket_cost_per_instruction"],
            branch_bracket_confidence=raw["logic_instructions"]["branch_bracket_confidence"],
            aoi_logic_composite_surcharge_per_instr=raw["logic_instructions"]["aoi_logic_composite_surcharge_per_instr"],
            jsr_target_composite_surcharge_per_instr=raw["logic_instructions"]["jsr_target_composite_surcharge_per_instr"],
            composite_surcharge_confidence=raw["logic_instructions"]["composite_surcharge_confidence"],
            composite_surcharge_cap=raw["logic_instructions"]["composite_surcharge_cap"],
            safety_task_program_shell=raw["logic_instructions"]["safety_task_program_shell"],
            safety_task_program_shell_confidence=raw["logic_instructions"]["safety_task_program_shell_confidence"],
        ),
    )
