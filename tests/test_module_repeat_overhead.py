"""The repeat-instance module discount: measured, and deliberately NOT applied.

OQ-BUILDFAIL-OPEN / OQ-MODULEIO, wired 2026-09-12 from the asmclose_* count
sweeps: 16 catalogs, each at 1 / 2 / 4 modules, so two independent marginal
measurements per catalog, all agreeing exactly. The discount is real in every
one of the 16 but is neither a constant nor a fixed ratio (432..3,768 bytes,
extra/first 0.24..0.79), which is why it is a second per-catalog number.

Applying it project-wide made all 16 held-out real programs WORSE, because it
only ever reduces a prediction and the real set is already under-predicting, so
it sits behind module_overhead_repeat_discount.apply_repeat_discount = false.

These tests pin both halves: that the measured data is still present and the
mechanism still works when enabled, and that with the gate off every instance
pays the first-instance rate. A future change that silently switches the gate
should fail here.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report


@pytest.fixture
def model():
    return load_memory_model()


def _modules_root(catalogs: list[str]) -> ET.Element:
    """A real connection block matters: a module with no <Communications> takes
    the zero-connection flat rate instead of the per-catalog table, so a
    fixture without one silently tests a different branch."""
    mods = "".join(
        f"""<Module Name="M{i}" CatalogNumber="{c}">
              <Ports><Port Id="1" Address="{i + 1}" Type="ICP" Upstream="true"/></Ports>
              <Communications>
                <Connections>
                  <Connection Name="Standard" RPI="10000" Type="Input" InputSize="4" OutputSize="0">
                    <InputTag ExternalAccess="Read/Write">
                      <Data Format="Decorated">
                        <Structure DataType="AB:TEST:I:0">
                          <DataValueMember Name="Fault" DataType="DINT" Value="0"/>
                        </Structure>
                      </Data>
                    </InputTag>
                  </Connection>
                </Connections>
              </Communications>
            </Module>"""
        for i, c in enumerate(catalogs)
    )
    return ET.fromstring(f"""
    <RSLogix5000Content SchemaRevision="1.0">
      <Controller Name="Test" ProcessorType="1756-L81E" MajorRev="35">
        <DataTypes/><AddOnInstructionDefinitions/><Tags/>
        <Modules>
          <Module Name="Local" CatalogNumber="1756-L81E">
            <Ports><Port Id="1" Address="0" Type="ICP" Upstream="false"/></Ports>
          </Module>
          {mods}
        </Modules>
        <Programs/><Tasks/>
      </Controller>
    </RSLogix5000Content>
    """)


def _module_bytes(catalogs: list[str], model) -> list[int]:
    entries, _ = build_report(_modules_root(catalogs), model)
    return [e.bytes for e in entries if e.category == "module_io"]


def test_the_discount_is_gated_off(model):
    """With the gate off, three modules of one catalog cost the same each."""
    assert model.module_overhead_by_catalog.repeat_by_catalog == {}
    sizes = _module_bytes(["1756-IB16"] * 3, model)
    assert len(sizes) == 3
    assert sizes[0] == sizes[1] == sizes[2]


def test_the_measured_repeat_data_is_still_on_record(model):
    """The numbers are good -- 16 catalogs, two independent marginal points
    each, zero variance -- so they stay in memory_model.yaml even though the
    scope they were applied at was wrong. Losing them would mean re-measuring."""
    import yaml

    from l5x_memory_analyzer.sizing import constants

    raw = yaml.safe_load(constants._DEFAULT_PATH.read_text(encoding="utf-8"))
    with_repeat = {
        catalog: v for catalog, v in raw["module_overhead_by_catalog"].items()
        if "repeat_bytes" in v
    }
    assert len(with_repeat) == 16
    for catalog, v in with_repeat.items():
        assert v["repeat_bytes"] < v["bytes"], catalog


def test_the_mechanism_still_works_when_enabled(model):
    """Exercised directly on the model so the gate can be turned back on with
    confidence once the per-rack-versus-per-project scope is settled."""
    from dataclasses import replace

    table = replace(model.module_overhead_by_catalog,
                    repeat_by_catalog={"1756-IB16": 892})
    assert table.overhead_for("1756-IB16", 1)[0] == 1684
    assert table.overhead_for("1756-IB16", 2)[0] == 892
    assert table.overhead_for("1756-IB16", 9)[0] == 892


def test_the_discount_is_per_catalog_not_per_module(model):
    """Two different catalogs are each on their FIRST instance, so neither gets
    a repeat rate -- the split keys on the catalog, not on position in the file."""
    mixed = _module_bytes(["1756-IB16", "1756-IB32/B"], model)
    ib16_alone = _module_bytes(["1756-IB16"], model)[0]
    ib32_alone = _module_bytes(["1756-IB32/B"], model)[0]
    assert mixed == [ib16_alone, ib32_alone]


def test_an_unmeasured_catalog_keeps_paying_the_first_instance_rate(model):
    """No repeat_bytes means the old behaviour, which over-predicts rather than
    under-predicts -- the safe direction for a catalog with no real data."""
    assert "9999-NOT-A-REAL-CATALOG" not in model.module_overhead_by_catalog.repeat_by_catalog
    sizes = _module_bytes(["9999-NOT-A-REAL-CATALOG"] * 3, model)
    assert sizes[0] == sizes[1] == sizes[2]


def test_the_six_2198_ers3_drives_all_cost_the_same(model):
    """They were ASSUMED at 10,497 / 7,377 / 7,341 against a real 4,624, and
    all six measure identically, so the per-catalog distinction between them was
    an artifact of guessing. Correcting this is what unmasked OQ-REALUNDER."""
    catalogs = ["2198-D012-ERS3", "2198-D020-ERS3", "2198-D032-ERS3",
                "2198-D057-ERS3", "2198-S086-ERS3", "2198-S130-ERS3"]
    table = model.module_overhead_by_catalog
    values = {table.overhead_for(c, 1) for c in catalogs}
    assert len(values) == 1, values
    overhead, confidence = values.pop()
    assert confidence == "KNOWN"
    assert overhead < 7341, "must be below every one of the old ASSUMED guesses"
