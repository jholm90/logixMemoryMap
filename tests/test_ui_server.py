"""End-to-end checks on the Flask UI's own endpoints.

These exist because every bug they cover was found by opening a real file
in a browser rather than by any unit test: an endpoint that 400s, a tree
that stops summing to the report, a drill that dead-ends one level down.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from l5x_memory_analyzer.ui.server import create_app

FIXTURE = Path("samples/generated")

# One file from each family that exercises a different part of the tree:
# alarms, AOI definitions, composite (modules + axes + UDTs), predefined
# array structures. Picked by directory rather than by exact filename so a
# regenerated corpus does not break the test, and skipped rather than
# failed when a directory is absent.
SAMPLE_DIRS = ("alarms", "aoi", "composite", "predefined", "udt", "modules")


def _samples() -> list[str]:
    out = []
    for name in SAMPLE_DIRS:
        files = sorted((FIXTURE / name).rglob("*.L5X"))
        if files:
            out.append(str(files[0]))
    return out


@pytest.fixture(scope="module", params=_samples() or ["__none__"])
def client(request):
    if request.param == "__none__":
        pytest.skip("no generated samples present")
    app = create_app(request.param)
    return app.test_client()


def _leaf_values(node, out):
    if node.get("children"):
        for child in node["children"]:
            _leaf_values(child, out)
    else:
        out.append(node.get("value", 0))


def test_tree_leaves_sum_to_the_reported_total(client):
    # The treemap's whole premise is that area is proportional and the
    # levels add up. An AOI whose definition decomposition came in lower
    # than its priced entry silently dropped 6% of a real file's bytes out
    # of the picture.
    report = client.get("/api/report").get_json()
    values: list[float] = []
    _leaf_values(report["hierarchy"], values)
    assert round(sum(values)) == round(sum(e["bytes"] for e in report["entries"]))


def test_report_exposes_module_and_type_metadata(client):
    report = client.get("/api/report").get_json()
    assert isinstance(report["type_names"], list)
    assert isinstance(report["aoi_names"], list)


def test_alarms_endpoint_rejects_a_non_alarm_path(client):
    res = client.get("/api/alarms?path=controller/Something")
    assert res.status_code == 400


def test_every_drillable_node_in_the_initial_tree_actually_expands(client):
    """A node that says has_children and then 400s is a dead end in the UI.

    Real cases this catches: a CAM/CAM_PROFILE array (priced per element,
    no scalar size) and a definition drilled in instance mode.
    """
    report = client.get("/api/report").get_json()
    drillable: list[dict] = []

    def walk(node):
        if node.get("children"):
            for child in node["children"]:
                walk(child)
        elif node.get("has_children"):
            drillable.append(node)

    walk(report["hierarchy"])
    failures = []
    for node in drillable[:200]:
        path = node["path"]
        if path.startswith("alarms/"):
            res = client.get(f"/api/alarms?path={path}")
        else:
            res = client.get(f"/api/node?tag={path}&path=")
        if res.status_code != 200:
            failures.append((path, node.get("data_type"), res.get_json()))
    assert not failures, failures


def test_definition_instance_mode_drills_more_than_one_level(client):
    report = client.get("/api/report").get_json()
    names = report["type_names"]
    if not names:
        pytest.skip("sample declares no UDT/AOI")
    for name in names:
        top = client.get(f"/api/node?tag=udt_definitions/{name}&mode=instance")
        if top.status_code != 200:
            continue
        for child in top.get_json()["children"]:
            if not child["has_children"]:
                continue
            deeper = client.get(
                f"/api/node?tag=udt_definitions/{name}"
                f"&path={child['segment']}&mode=instance"
            )
            assert deeper.status_code == 200, deeper.get_json()
            return
    pytest.skip("no nested member in any declared type of this sample")
