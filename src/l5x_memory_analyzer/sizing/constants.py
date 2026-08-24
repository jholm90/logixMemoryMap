"""Loads sizing constants from memory_model.yaml (mirrors docs/MEMORY_MODEL.md).

Parser/sizing code must pull byte sizes and packing rules from here, never
hardcode them inline -- see CLAUDE.md working agreement.
"""

from __future__ import annotations

import math
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
    custom_definition_cost: int
    custom_definition_confidence: str
    builtin_tag_overhead_correction: int
    builtin_tag_overhead_correction_confidence: str
    custom_data_padding_multiple: int
    custom_mod4eq1_definition_bonus: int
    custom_data_padding_confidence: str


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
    confidence: str

    def bytes_for(self, declared_item_count: int) -> int:
        return self.base + self.per_declared_item * declared_item_count


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
class CptExpressionModel:
    base_read: int
    operator_tier_costs: dict[str, int]
    per_extra_same_tier_operand: int

    def cost_for(self, operators: list[str]) -> int:
        """Real per-call CPT cost from its expression's operator tokens
        (OQ-CMPCPTLAYOUT, wired 2026-08-26) -- see memory_model.yaml
        cpt_expression for the full derivation. A UNIFORM expression (every
        operator the same tier -- covers plain chains like A+B+C+D, the
        dominant real usage pattern) is exact: confirmed 0 residual across
        the n=1 operand-count sweep (1-10 operands) AND the n=1000
        chain-length sweep (3/4/5/6/8/10 operands), independently. A MIXED
        expression (more than one distinct operator tier present, e.g.
        A+B*C) falls back to a simple per-operator-tier sum -- a WEAK
        approximation, not a confirmed one: off by only ~20 bytes/call on
        2 simple 3-operator test points, but off by ~150 bytes/call on a
        real 5-operator/3-tier/mixed-literal corpus expression. See
        memory_model.yaml cpt_expression for the full derivation and why
        this isn't patched further tonight (too few points to isolate
        which factor drives the larger gap).
        """
        if not operators:
            return self.base_read
        tiers = [self.operator_tier_costs[op] for op in operators]
        if len(set(tiers)) == 1:
            return self.base_read + tiers[0] + self.per_extra_same_tier_operand * (len(operators) - 1)
        return self.base_read + sum(tiers)


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
class LogicInstructionModel:
    fixed_base_per_routine: int
    jsr_fixed_base_per_routine: int
    confidence: str
    weights: dict[str, int]
    cpt_expression: CptExpressionModel
    operand_type_surcharge: OperandTypeSurchargeModel
    indirect_index: IndirectIndexModel
    cmp_surcharge: CmpSurchargeModel


@dataclass(frozen=True)
class MemoryModel:
    atomic_types: dict[str, AtomicType]
    predefined_structures: dict[str, AtomicType]
    predefined_array_structures: dict[str, PredefinedArrayStructure]
    bool: BoolModel
    string: StringModel
    udt: UdtModel
    array: ArrayModel
    aoi_array: AoiArrayModel
    aoi_definition: AoiDefinitionModel
    tag_overhead: TagOverheadModel
    alias_overhead: TagOverheadModel
    udt_definition: UdtDefinitionModel
    logic_instructions: LogicInstructionModel
    empty_project_baseline_bytes: int
    empty_project_baseline_confidence: str


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
    return MemoryModel(
        atomic_types=atomic_types,
        predefined_structures=predefined_structures,
        predefined_array_structures=predefined_array_structures,
        empty_project_baseline_bytes=baseline["bytes"],
        empty_project_baseline_confidence=baseline["confidence"],
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
            custom_definition_cost=s["custom_definition_cost"],
            custom_definition_confidence=s["custom_definition_confidence"],
            builtin_tag_overhead_correction=s["builtin_tag_overhead_correction"],
            builtin_tag_overhead_correction_confidence=s["builtin_tag_overhead_correction_confidence"],
            custom_data_padding_multiple=s["custom_data_padding_multiple"],
            custom_mod4eq1_definition_bonus=s["custom_mod4eq1_definition_bonus"],
            custom_data_padding_confidence=s["custom_data_padding_confidence"],
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
            confidence=raw["aoi_definition"]["confidence"],
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
        ),
    )
