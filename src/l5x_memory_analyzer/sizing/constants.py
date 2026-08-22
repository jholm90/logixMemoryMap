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


@dataclass(frozen=True)
class UdtModel:
    alignment_confidence: str


@dataclass(frozen=True)
class ArrayModel:
    atomic_confidence: str
    udt_confidence: str


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
class LogicInstructionModel:
    fixed_base_per_routine: int
    jsr_fixed_base_per_routine: int
    confidence: str
    weights: dict[str, int]


@dataclass(frozen=True)
class MemoryModel:
    atomic_types: dict[str, AtomicType]
    predefined_structures: dict[str, AtomicType]
    bool: BoolModel
    string: StringModel
    udt: UdtModel
    array: ArrayModel
    tag_overhead: TagOverheadModel
    udt_definition: UdtDefinitionModel
    logic_instructions: LogicInstructionModel


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
    b = raw["bool"]
    s = raw["string"]
    return MemoryModel(
        atomic_types=atomic_types,
        predefined_structures=predefined_structures,
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
        ),
        udt=UdtModel(alignment_confidence=raw["udt"]["alignment_confidence"]),
        array=ArrayModel(
            atomic_confidence=raw["array"]["atomic_confidence"],
            udt_confidence=raw["array"]["udt_confidence"],
        ),
        tag_overhead=TagOverheadModel(
            flat_base=raw["tag_overhead"]["flat_base"],
            per_8_chars=raw["tag_overhead"]["per_8_chars"],
            confidence=raw["tag_overhead"]["confidence"],
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
        ),
    )
