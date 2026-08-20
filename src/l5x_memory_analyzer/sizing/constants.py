"""Loads sizing constants from memory_model.yaml (mirrors docs/MEMORY_MODEL.md).

Parser/sizing code must pull byte sizes and packing rules from here, never
hardcode them inline -- see CLAUDE.md working agreement.
"""

from __future__ import annotations

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
class MemoryModel:
    atomic_types: dict[str, AtomicType]
    predefined_structures: dict[str, AtomicType]
    bool: BoolModel
    string: StringModel
    udt: UdtModel
    array: ArrayModel


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
    )
