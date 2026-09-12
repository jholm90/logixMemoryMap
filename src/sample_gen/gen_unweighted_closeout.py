"""EVENT: the last in-scope instruction on a real file with no weight.

Written 2026-09-12, after wiring ten measured weights off sweeps that had been
captured and never differenced (MCD 184, PID 156, MAG 124, MCS 120, UPPER 84,
STOR 80, FBC 76, LFU 72, RTOS 72, BRK 56). That took the real files' unpriced
instruction uses from 133 to 72, and then classifying the remainder took it to
57 -- all of which are EVENT:

  ESTOP / ROUT / LC / RIN   OUT OF SCOPE, not unpriced. All four only appear
        inside a GuardLogix SafetyProgram, which this project does not size at
        all -- the same reclassification CROUT got 2026-08-24. Identified from
        their real call shapes, every one of which takes the `_S`-suffixed
        safety reset tags that exist only in a safety task. Now in
        `coverage._SAFETY_FAMILY` rather than reported as a hole.

  SCP   NOT a built-in at all. Four real exports declare an
        AddOnInstructionDefinition named SCP; a fifth calls it without
        declaring it. Its arity even varies across the corpus (3 operands in
        one program, 7 in another), which is the signature of a user AOI. So
        the gap there is a partial export, not a missing weight, and adding
        one would be inventing a cost for something that has none of its own.
        Now in `coverage._KNOWN_USER_AOI`.

That leaves EVENT, at 57 uses across the sixteen real programs, and its
per-rung cost has never been measured: `eventtask_instronly` is a single point,
which can confirm a total but cannot separate the instruction's cost from the
file's.

THE SHAPE IS TRANSPLANTED, NOT COMPOSED. `EVENT(TrackingInfeed);` is verbatim
from the real corpus, where it is by far the most common form (12 of 44 uses,
and all 16 distinct real shapes are the same single-operand call naming an
EVENT task). This rule is not pedantry: inventing call shapes has cost this
project real time three separate times -- invented alarm ConditionTypes (all
four rejected), bare 2-operand MAM/MAJ/MAS/MRP rungs (failed every rung), and
the Kinetix `:SI` safety tags Studio synthesises itself.

The operand is a TASK name, so the file has to declare a real EVENT task for
the rung to resolve against, which is what `gen_event_task_trigger`'s own
verified task XML provides. Three counts, so the per-rung slope is a
measurement and the file baseline falls out as the intercept.

Run: python -m sample_gen.gen_unweighted_closeout
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "instructions"

COUNTS = (10, 100, 1000)

# The EVENT task the rungs name. Shape kept minimal and real: an EVENT task
# with no trigger source configured is what `eventtask_instronly` already
# captured at zero errors, so the task shell's own cost is a known quantity
# that cancels in every difference across this sweep.
TASK_NAME = "EvtTask"

_EVENT_TASK_XML = f"""    <Task Name="{TASK_NAME}" Type="EVENT" Rate="10" Priority="10" Watchdog="500"
     DisableUpdateOutputs="false" InhibitTask="false" EventInfo="EVENT_INSTRUCTION_ONLY">
      <ScheduledPrograms>
        <ScheduledProgram Name="EvtProgram"/>
      </ScheduledPrograms>
    </Task>"""

_EVENT_PROGRAM_XML = """    <Program Name="EvtProgram" TestEdits="false" MainRoutineName="MainRoutine"
     Disabled="false" UseAsFolder="false">
      <Tags/>
      <Routines>
        <Routine Name="MainRoutine" Type="RLL">
          <RLLContent>
            <Rung Number="0" Type="N">
              <Text><![CDATA[NOP();]]></Text>
            </Rung>
          </RLLContent>
        </Routine>
      </Routines>
    </Program>"""


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for n in COUNTS:
        rungs = rungs_xml(n, lambda _i: f"EVENT({TASK_NAME});")
        l5x = build_l5x(
            target_name=f"UwCloseEvent{n:04d}",
            tags_xml=tag_xml("Dummy", "DINT"),
            extra_rungs_xml=rungs,
            extra_tasks_xml=_EVENT_TASK_XML,
            extra_scheduled_programs_xml=_EVENT_PROGRAM_XML,
        )
        name = f"uwclose_event_n{n:05d}"
        out = OUT_ROOT / f"{name}.L5X"
        bytes_ = write_sample(l5x, out)
        append_manifest_row(
            name,
            f"{n} rungs of EVENT({TASK_NAME}) triggering one declared EVENT task. EVENT is the "
            f"LAST in-scope instruction with no weight that reaches a real file -- 57 uses across "
            f"the sixteen real programs -- and is currently charged ZERO, which is an absence of "
            f"data rather than a measurement. Call shape is verbatim from the real corpus "
            f"(EVENT(TrackingInfeed), the most common of 44 real uses; all 16 distinct real shapes "
            f"are the same single-operand form naming an EVENT task). Three counts so the per-rung "
            f"slope is measured and the shared file/task baseline falls out as the intercept -- "
            f"the existing eventtask_instronly is a single point, which can confirm a total but "
            f"cannot separate the instruction from the file. OQ-VERIFINSTR.",
            "instructions", out, bytes_,
        )
        print(f"Wrote {out} (predicted {bytes_} bytes)")
    print(f"Total: {len(COUNTS)}")


if __name__ == "__main__":
    main()
