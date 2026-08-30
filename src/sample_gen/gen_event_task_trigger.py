"""EVENT task trigger-source cost, James (2026-08-25): "Does an event task
triggered by MAW cost more than an event task triggered by the EVENT
instruction?"

Real corpus shape confirmed (SJ_Gormley_20251112_r02.L5X,
Sorter1_20260722r00.L5X, 12 real Task elements grepped): the two real
EventTrigger values are "EVENT Instruction Only" (no EventTag) and
"Axis Watch" (EventTag pointing at a real AXIS_CIP_DRIVE tag -- confirmed
against Gormley's own EM108_GradingLC axis). "Axis Watch" is a task-level
config, not the MAW *instruction* itself -- James's "MAW" almost certainly
means this, since Axis Watch is exactly the task-scheduling trigger the
MAW (Motion Axis Watch) instruction/concept maps to; there is no separate
real corpus example of an EVENT task triggered any other way.

No existing calibration file has ever used Type="EVENT" at all -- the
existing task_extra=+700 constant (memory_model.yaml) was derived
EXCLUSIVELY from CONTINUOUS+PERIODIC tasks (taskoverhead_n0Xtasks). This
is a genuinely untested axis, not a re-derivation.

Both files below mirror taskoverhead_n02tasks.L5X (1 Continuous + 1 extra
Task, each Program a single NOP rung, same 5069-L306ER/fw35.11 baseline)
exactly, changing ONLY the extra Task's Type/trigger -- so a direct delta
against that existing captured file isolates PERIODIC-vs-EVENT, and a
direct delta between these two isolates trigger-source-within-EVENT.

Run: python -m sample_gen.gen_event_task_trigger
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import program_xml, task_xml
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.manifest import append_manifest_row, write_sample, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"

# Real AXIS_CIP_DRIVE + companion MOTION_GROUP tag pair (see
# gen_axis_composite.py's _AXIS_TAG_XML docstring for provenance), renamed
# from "Axis_Cip_Drive" to "WatchedAxis" so the EventTag reference below
# resolves. REAL BUG FOUND 2026-08-30 (James, live testing: "Line 33:
# Invalid display style" + "Line 70: Tag being used for event task does
# not exist" -- then, pointedly: "if you set it for axis watch then you
# should have generated an axis - does this not sound very obvious?"):
# this file previously built WatchedAxis with the generic tag_xml() scalar
# helper (a bare Format="Decorated"/<DataValue DataType="AXIS_CIP_DRIVE"
# Value="0"/>), which is not how AXIS_CIP_DRIVE is ever really represented
# -- it needs the full Format="Axis"/<AxisParameters> structure plus its
# required MotionGroup companion tag, exactly like every other real
# AXIS_CIP_DRIVE use in this project (gen_axis_composite.py). Fixed by
# reusing that already-real, already-proven shape instead of re-deriving
# it. The chassis "Size" error also reported in that same run (Bus
# Size="32" on 5069-L306ER) is very likely a downstream artifact of this
# same malformed-tag import abort, not an independent bug -- hundreds of
# other 5069-L306ER files use that identical Bus Size and import fine.
_WATCHED_AXIS_TAG_XML = _AXIS_TAG_XML.replace('Name="Axis_Cip_Drive"', 'Name="WatchedAxis"')


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "task_overhead", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    """Like _write, but for the AXIS_CIP_DRIVE-bearing file -- unmodeled
    predefined structure (OQ-AXISSTRUCT), same convention as
    gen_axis_composite.py's _write_unmodeled."""
    out_path = OUT_ROOT / f"{out_name}.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(out_name, f"{description} (unmodeled predefined structure)", "task_overhead", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- unmodeled axis structure)")


def main() -> None:
    # EventTrigger="EVENT Instruction Only" -- no EventTag needed, matches
    # BoardAndLugID in the Gormley corpus exactly.
    extra_program = program_xml("EventProgram0")
    extra_task = task_xml("EventTask0", "EventProgram0", task_type="EVENT",
                           event_trigger="EVENT Instruction Only")
    l5x = build_l5x(
        target_name="EventTaskInstrOnly", tags_xml="", processor_type="5069-L306ER",
        major_rev="35", minor_rev="11", software_revision="35.05",
        extra_programs_xml=extra_program, extra_tasks_xml=extra_task,
    )
    _write(
        l5x, "eventtask_instronly",
        "1 Continuous + 1 EVENT Task (EventTrigger=\"EVENT Instruction Only\", real corpus shape "
        "confirmed against SJ_Gormley's BoardAndLugID task) -- direct mirror of taskoverhead_n02tasks "
        "(1 Continuous + 1 Periodic) with only the 2nd Task's Type/trigger changed, isolating "
        "PERIODIC-vs-EVENT cost. No existing calibration file has ever used Type=\"EVENT\".",
    )

    # EventTrigger="Axis Watch" -- needs a real controller-scope
    # AXIS_CIP_DRIVE tag as the EventTag target (confirmed real shape:
    # Gormley's EM108_GradingLC). James's "MAW" question maps to this --
    # Axis Watch is the real task-level trigger MAW (Motion Axis Watch)
    # corresponds to; there's no other real EVENT-trigger shape in the
    # corpus to test against.
    extra_program2 = program_xml("EventProgram1")
    extra_task2 = task_xml("EventTask1", "EventProgram1", task_type="EVENT",
                            event_trigger="Axis Watch", event_tag="WatchedAxis")
    l5x2 = build_l5x(
        target_name="EventTaskAxisWatch", tags_xml=_WATCHED_AXIS_TAG_XML, processor_type="5069-L306ER",
        major_rev="35", minor_rev="11", software_revision="35.05",
        extra_programs_xml=extra_program2, extra_tasks_xml=extra_task2,
    )
    _write_unmodeled(
        l5x2, "eventtask_axiswatch",
        "1 Continuous + 1 EVENT Task (EventTrigger=\"Axis Watch\", EventTag pointing at a real "
        "AXIS_CIP_DRIVE controller-scope tag, real corpus shape confirmed against SJ_Gormley's "
        "DataMove_GradingLC task/EM108_GradingLC axis) -- identical to eventtask_instronly except "
        "trigger source, isolating whether Axis-Watch-triggered EVENT tasks (what James's \"MAW\" "
        "question maps to) cost differently from EVENT()-instruction-triggered ones. The extra "
        "AXIS_CIP_DRIVE tag itself has its own real, separately-modeled cost -- watch for that "
        "confound when reconciling captures.",
    )


if __name__ == "__main__":
    main()
