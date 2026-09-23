"""EVENT task trigger-source cost: does an event task
triggered by MAW cost more than one triggered by the EVENT instruction?

Real corpus shape confirmed (a real export,
a real export, 12 real Task elements grepped): the two real
EventTrigger values are "EVENT Instruction Only" (no EventTag) and
"Axis Watch" (EventTag pointing at a real AXIS_CIP_DRIVE tag -- confirmed
against export 21's own EM108_GradingLC axis). "Axis Watch" is a task-level
config, not the MAW *instruction* itself -- the "MAW" almost certainly
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
# resolves. REAL BUG FOUND in live testing -- "Line 33: Invalid display
# style" and "Line 70: Tag being used for event task does not exist". An
# axis-watch event task needs an actual axis, and
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

# REAL BUG FOUND (real Studio 5000 error on
# eventtask_instronly.L5X): "Failed to set the 'Size' property (Chassis
# size exceeds the allowable size for a chassis.)" on the Local module's
# own backplane Bus, with NO axis tag involved at all -- proving the
# earlier dismissal of this same error class as "very likely a
# downstream artifact of the malformed-tag import abort" (see
# _WATCHED_AXIS_TAG_XML's comment above) was wrong; it's a real,
# independent bug. Root cause: "5069-L306ER" (bare, no S2/M/MS2/MS3
# suffix) is the ONLY place in this entire project that ever used that
# exact catalog string -- every other 5069 file uses a specific suffixed
# variant. wrapper.py's _5069_BUS_SIZE_BY_MODEL buckets ALL L306 variants
# (bare ER, ERS2, ERM, ERMS2, ERMS3) under the same Bus Size=9, an
# assumption confirmed ONLY against L306ERS2_Sample.L5X (a Safety+Motion
# variant) and never independently checked against the bare non-suffixed
# model -- this real error shows that assumption doesn't hold for the
# bare "ER" tier. Rather than guess a corrected bus size with zero real
# corpus evidence for the bare catalog, switch to the wrapper's own
# default processor (1756-L81E) -- which also fixes a separate, real
# mismatch: this file's docstring claims it's a "direct mirror of
# taskoverhead_n02tasks (... same 5069-L306ER/fw35.11 baseline)", but
# gen_task_overhead.py never actually passes a processor_type override,
# so taskoverhead_n02tasks is really 1756-L81E all along -- these files
# were never actually on the same processor they claimed to be compared
# against. Dropping the override fixes both problems with one real,
# evidenced change, not a guess.


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
    # BoardAndLugID in the export 21 corpus exactly.
    extra_program = program_xml("EventProgram0")
    extra_task = task_xml("EventTask0", "EventProgram0", task_type="EVENT",
                           event_trigger="EVENT Instruction Only")
    l5x = build_l5x(
        target_name="EventTaskInstrOnly", tags_xml="",
        extra_programs_xml=extra_program, extra_tasks_xml=extra_task,
    )
    _write(
        l5x, "eventtask_instronly",
        "1 Continuous + 1 EVENT Task (EventTrigger=\"EVENT Instruction Only\", real corpus shape "
        "confirmed against export 21's BoardAndLugID task) -- direct mirror of taskoverhead_n02tasks "
        "(1 Continuous + 1 Periodic), same default 1756-L81E/fw35.11 processor (see the bare-"
        "\"5069-L306ER\" chassis-size bug note above -- that catalog is untested/broken, this file "
        "now matches taskoverhead_n02tasks's REAL processor instead of a claimed-but-wrong one), "
        "isolating PERIODIC-vs-EVENT cost. No existing calibration file has ever used Type=\"EVENT\".",
    )

    _axiswatch()


def _axiswatch(suffix: str = "", note: str = "") -> None:
    # EventTrigger="Axis Watch" -- needs a real controller-scope
    # AXIS_CIP_DRIVE tag as the EventTag target (confirmed real shape:
    # Export 21's EM108_GradingLC). the "MAW" question maps to this --
    # Axis Watch is the real task-level trigger MAW (Motion Axis Watch)
    # corresponds to; there's no other real EVENT-trigger shape in the
    # corpus to test against.
    extra_program2 = program_xml("EventProgram1")
    extra_task2 = task_xml("EventTask1", "EventProgram1", task_type="EVENT",
                            event_trigger="Axis Watch", event_tag="WatchedAxis")
    l5x2 = build_l5x(
        target_name="EventTaskAxisWatch", tags_xml=_WATCHED_AXIS_TAG_XML,
        extra_programs_xml=extra_program2, extra_tasks_xml=extra_task2,
    )
    _write_unmodeled(
        l5x2, f"eventtask_axiswatch{suffix}",
        "1 Continuous + 1 EVENT Task (EventTrigger=\"Axis Watch\", EventTag pointing at a real "
        "AXIS_CIP_DRIVE controller-scope tag, real corpus shape confirmed against export 21's "
        "DataMove_GradingLC task/EM108_GradingLC axis) -- identical to eventtask_instronly except "
        "trigger source, isolating whether Axis-Watch-triggered EVENT tasks (what the \"MAW\" "
        "question maps to) cost differently from EVENT()-instruction-triggered ones. The extra "
        "AXIS_CIP_DRIVE tag itself has its own real, separately-modeled cost -- watch for that "
        "confound when reconciling captures." + note,
    )



def regenerate_open() -> None:
    """Rebuild eventtask_axiswatch under a new name.

    The capture tooling skips any file name it has already seen. The original
    was captured once on a 5069-L306ER before the processor override was
    dropped, with one build error and no error text, so the current file never
    reached a controller. The `_r2` copy exists to be built once and have its
    Studio error log recorded.
    """
    _axiswatch("_r2", " -- OQ-BUILDFAIL-OPEN re-trigger under a new name so the build's "
                      "Studio error log is recorded; content identical to the original file")

if __name__ == "__main__":
    import sys
    regenerate_open() if "--regenerate-open" in sys.argv else main()
