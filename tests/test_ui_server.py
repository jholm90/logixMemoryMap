"""End-to-end checks on the Flask UI's own endpoints.

These exist because every bug they cover was found by opening a real file
in a browser rather than by any unit test: an endpoint that 400s, a tree
that stops summing to the report, a drill that dead-ends one level down.
"""

from __future__ import annotations


import pytest

from l5x_memory_analyzer.ui.server import create_app

# Inputs that exercise different parts of the tree: the synthetic demo project
# (modules, a Kinetix bus, UDTs, an AOI, programs), the tag-alarm batch and the
# predefined-structure batch (CAM / CAM_PROFILE / MESSAGE arrays). The generated
# batches are rebuilt from their generators (tests/conftest.py).
SAMPLES = {
    "demo": None,
    "alarms": ("alarms", "gen_alarm_conditions"),
    "predefined": ("predefined", "gen_predefined_probe"),
}


@pytest.fixture(scope="module", params=list(SAMPLES))
def client(request, demo_l5x, regenerate):
    spec = SAMPLES[request.param]
    if spec is None:
        path = demo_l5x
    else:
        folder, generator = spec
        path = sorted((regenerate(generator) / folder).glob("*.L5X"))[0]
    return create_app(str(path)).test_client()


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


def test_every_ladder_routine_opens_into_its_rungs(client):
    """An RLL tile is drillable into its rungs, an AOI's own logic included.

    An AOI's Logic tile offered a drill and then 400'd: the rung endpoint
    accepted program routines only and the AOI's rung count was never sent.
    """
    report = client.get("/api/report").get_json()
    routines: list[dict] = []

    def walk(node):
        for child in node.get("children") or []:
            walk(child)
        if node.get("data_type") == "RLL" and node.get("path"):
            routines.append(node)

    walk(report["hierarchy"])
    failures = []
    for node in routines:
        path = node["path"]
        count = report["rung_counts"].get(path)
        if count is None:
            failures.append((path, "no rung count"))
            continue
        res = client.get("/api/rungs", query_string={"path": path})
        if res.status_code != 200 or len(res.get_json()["rungs"]) != count:
            failures.append((path, res.status_code))
    assert not failures, failures


def test_aoi_rungs_name_their_routine_when_the_aoi_has_several():
    import xml.etree.ElementTree as ET

    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.ui.server import _build_all_rungs

    def routine(name, *texts):
        rungs = "".join(
            f'<Rung Number="{i}" Type="N"><Text><![CDATA[{t}]]></Text></Rung>'
            for i, t in enumerate(texts))
        return f'<Routine Name="{name}" Type="RLL"><RLLContent>{rungs}</RLLContent></Routine>'

    def aoi(name, routines):
        return (f'<AddOnInstructionDefinition Name="{name}"><Routines>{routines}'
                f'</Routines></AddOnInstructionDefinition>')

    root = ET.fromstring(
        "<RSLogix5000Content><Controller><AddOnInstructionDefinitions>"
        + aoi("Two", routine("Logic", "XIC(A)OTE(B);", "NOP();") + routine("Prescan", "OTU(B);"))
        + aoi("One", routine("Logic", "XIC(A)OTE(B);"))
        + aoi("Protected", "")
        + "</AddOnInstructionDefinitions></Controller></RSLogix5000Content>")
    rungs = _build_all_rungs(root, load_memory_model())

    two = rungs["aoi_definitions/Two/Logic+Prescan"]
    assert [(r["routine"], r["number"]) for r in two] == [("Logic", 0), ("Logic", 1), ("Prescan", 0)]
    assert "routine" not in rungs["aoi_definitions/One/Logic"][0]
    assert rungs["aoi_definitions/Protected/Logic"] == []


def test_instance_and_heartbeat_endpoints():
    app = create_app(None)
    c = app.test_client()
    assert c.get("/api/instance").get_json()["app"] == "l5x-memory-analyzer"
    before = app.config["last_seen"]
    assert c.post("/api/heartbeat").status_code == 204
    assert app.config["last_seen"] >= before


def test_a_second_launch_on_the_same_port_returns_instead_of_serving():
    """Each click on the desktop shortcut used to start one more server on the port
    (Windows lets waitress's SO_REUSEADDR socket bind it twice). A second run() finds
    the first and returns."""
    import socket
    import threading
    import time
    from l5x_memory_analyzer.ui import server

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    first = threading.Thread(target=server.run, args=(None,), kwargs={"port": port}, daemon=True)
    first.start()
    for _ in range(100):
        if server.running_instance("127.0.0.1", port):
            break
        time.sleep(0.05)
    assert server.running_instance("127.0.0.1", port)

    second = threading.Thread(target=server.run, args=(None,), kwargs={"port": port}, daemon=True)
    second.start()
    second.join(timeout=10)
    assert not second.is_alive()
    # The port is held exclusively: a plain bind by anything else fails.
    assert server._bind_exclusive("127.0.0.1", port) is None
