"""The repeat-instance module discount: applied, with two families left out.

OQ-MODULEIO. Measured 2026-09-12 from the asmclose_* count sweeps -- 16
catalogs at 1 / 2 / 4 / 8 modules each, so three independent marginal points
per catalog, all agreeing exactly. The discount is real in every one but is
neither a constant nor a fixed ratio (432..3,768 bytes, extra/first
0.24..0.79), which is why it has to be a second per-catalog number.

It was gated off on 2026-09-12 because applying it project-wide moved all
sixteen held-out real programs further under-predicted, with the recorded
hypothesis that the shared thing is shared per rack rather than per project.
2026-09-13 measured both halves of that:

  - repeat_scope (project | parent) produces byte-identical totals on all
    sixteen real programs, because in every one of them no catalog carrying a
    measured repeat rate appears under more than one parent. Scope cannot be
    the cause.
  - The regression was 95% two catalog families, ETHERNET-MODULE (67,450 of
    189,570 bytes) and the six 2198-*-ERS3 drives (112,176), both of whose
    repeat rates were measured on a shape real programs do not contain. With
    those two left out, the other ten catalogs shift the real programs by
    10,464 bytes across 47.4 MB -- neutral to within noise -- while taking the
    asmclose rows from 16 byte-exact to 47.

So the gate is on, those two families carry no repeat_bytes, and these tests
pin all of it: which catalogs are in, which are deliberately out and why, and
that the per-catalog (not per-file) reading the mixtures settled is what the
engine actually implements.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

# Left out of repeat_by_catalog on shape grounds, not because of which way they
# moved the number. See memory_model.yaml module_overhead_repeat_discount.
EXCLUDED_ON_SHAPE_GROUNDS = (
    "ETHERNET-MODULE",
    "2198-D012-ERS3", "2198-D020-ERS3", "2198-D032-ERS3",
    "2198-D057-ERS3", "2198-S086-ERS3", "2198-S130-ERS3",
)


@pytest.fixture
def model():
    return load_memory_model()


def _modules_root(catalogs: list[str], parents: list[str] | None = None) -> ET.Element:
    """A real connection block matters: a module with no <Communications> takes
    the zero-connection flat rate instead of the per-catalog table, so a
    fixture without one silently tests a different branch."""
    parents = parents or ["Local"] * len(catalogs)
    mods = "".join(
        f"""<Module Name="M{i}" CatalogNumber="{c}" ParentModule="{p}">
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
        for i, (c, p) in enumerate(zip(catalogs, parents))
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


def _module_bytes(catalogs: list[str], model, parents: list[str] | None = None) -> list[int]:
    entries, _ = build_report(_modules_root(catalogs, parents), model)
    return [e.bytes for e in entries if e.category == "module_io"]


def test_the_discount_is_applied(model):
    """Three modules of one catalog: the first pays full price, the rest don't."""
    assert model.module_overhead_by_catalog.repeat_by_catalog != {}
    sizes = _module_bytes(["1756-IB16"] * 3, model)
    assert len(sizes) == 3
    assert sizes[1] == sizes[2] < sizes[0]
    # 1,684 first / 892 after, straight off asmclose_1756_ib16_1conn_n{01,02,04,08}.
    assert sizes[0] - sizes[1] == 1684 - 892


def test_exactly_the_ten_measured_applicable_catalogs_are_wired(model):
    """Ten of the seventeen measured rates apply. The other seven are held out
    on shape grounds and each says so at its own table entry -- a future change
    that quietly adds one back should fail here."""
    import yaml

    from l5x_memory_analyzer.sizing import constants

    raw = yaml.safe_load(constants._DEFAULT_PATH.read_text(encoding="utf-8"))
    with_repeat = {
        catalog: v for catalog, v in raw["module_overhead_by_catalog"].items()
        if "repeat_bytes" in v
    }
    assert len(with_repeat) == 10
    for catalog in EXCLUDED_ON_SHAPE_GROUNDS:
        assert catalog not in with_repeat, catalog
        assert catalog in raw["module_overhead_by_catalog"], catalog
    for catalog, v in with_repeat.items():
        assert v["repeat_bytes"] < v["bytes"], catalog
    assert model.module_overhead_by_catalog.repeat_by_catalog.keys() == with_repeat.keys()


def test_an_excluded_family_keeps_paying_the_first_instance_rate(model):
    """A 2198 drive and an ETHERNET-MODULE cost the same every time. Their
    measured repeat rates exist but describe a bare drive with no axis tag and
    a cloned connection shape respectively, neither of which a real program
    contains."""
    for catalog in ("2198-D012-ERS3", "ETHERNET-MODULE"):
        sizes = _module_bytes([catalog] * 3, model)
        assert sizes[0] == sizes[1] == sizes[2], catalog


def test_repeat_scope_defaults_to_project(model):
    """project | parent is a real open question (nothing captured splits a
    catalog across parents), so it is a model field rather than a code comment.
    The default is project; parent restarts the count under each parent."""
    table = model.module_overhead_by_catalog
    assert table.repeat_scope == "project"
    assert table.occurrence_key("1756-IB16", "Rack2") == ("1756-IB16", "")

    from dataclasses import replace

    per_rack = replace(table, repeat_scope="parent")
    assert per_rack.occurrence_key("1756-IB16", "Rack2") == ("1756-IB16", "Rack2")


def test_parent_scope_restarts_the_count_under_each_parent(model):
    """Two IB16s under one parent: second is discounted. One under each of two
    parents: both pay full price."""
    from dataclasses import replace

    per_rack = replace(model, module_overhead_by_catalog=replace(
        model.module_overhead_by_catalog, repeat_scope="parent"))
    same = _module_bytes(["1756-IB16"] * 2, per_rack, ["Local", "Local"])
    assert same[1] < same[0]
    split = _module_bytes(["1756-IB16"] * 2, per_rack, ["Local", "Rack2"])
    assert split[0] == split[1] == same[0]


def test_the_mechanism_is_flat_from_the_second_instance_on(model):
    """d x (n - 1), confirmed at n = 1 / 2 / 4 / 8 -- n=8 was the first point
    that could have shown a per-rack or per-connection-block step and doesn't."""
    table = model.module_overhead_by_catalog
    assert table.overhead_for("1756-IB16", 1)[0] == 1684
    assert table.overhead_for("1756-IB16", 2)[0] == 892
    assert table.overhead_for("1756-IB16", 9)[0] == 892


def test_the_discount_is_per_catalog_not_per_module(model):
    """Two different catalogs are each on their FIRST instance, so neither gets
    a repeat rate -- the split keys on the catalog, not on position in the file.
    Settled on real data by modmarg_mixq{1,2,3}: reversing module order leaves
    the total byte-identical, which per-file ordering could not do."""
    mixed = _module_bytes(["1756-IB16", "1756-IB32/B"], model)
    ib16_alone = _module_bytes(["1756-IB16"], model)[0]
    ib32_alone = _module_bytes(["1756-IB32/B"], model)[0]
    assert mixed == [ib16_alone, ib32_alone]


def test_module_order_does_not_change_the_total(model):
    """The x2rev half of the mixture arm, in miniature."""
    forward = sum(_module_bytes(["1756-IB16"] * 2 + ["1756-IB32/B"] * 2, model))
    reverse = sum(_module_bytes(["1756-IB32/B"] * 2 + ["1756-IB16"] * 2, model))
    assert forward == reverse


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
