"""Parses Controller/Tasks out of an L5X document (2026-08-27, Phase 5
Task-level UI grouping).

Distinct from the separate, still-open per-Task BYTE-COST question
(docs/OPEN_QUESTIONS.md OQ item on Task/Program/Routine overhead, blocked
on real capture data to disentangle NOP content cost from routine-shell
cost) -- this module only extracts which Programs are scheduled under
which Task, a real, directly-stated L5X relationship (no fitting needed,
same category as parser/modules.py's Connection/ConfigTag sizes), purely
to let the UI nest "Program: X" groups under their owning "Task: Y" group.
No new byte formula involved: a Task's displayed total is just the sum of
its already-correctly-computed Programs' bytes.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TaskInfo:
    name: str
    scheduled_program_names: tuple[str, ...] = field(default_factory=tuple)


def parse_tasks(root: ET.Element) -> list[TaskInfo]:
    tasks_el = root.find("Controller/Tasks")
    if tasks_el is None:
        return []

    result: list[TaskInfo] = []
    for task_el in tasks_el.findall("Task"):
        name = task_el.get("Name", "")
        programs: list[str] = []
        scheduled_el = task_el.find("ScheduledPrograms")
        if scheduled_el is not None:
            for sp_el in scheduled_el.findall("ScheduledProgram"):
                prog_name = sp_el.get("Name")
                if prog_name:
                    programs.append(prog_name)
        result.append(TaskInfo(name=name, scheduled_program_names=tuple(programs)))
    return result


def program_to_task_map(root: ET.Element) -> dict[str, str]:
    """Program name -> owning Task name, for every Program that IS
    scheduled under some Task. A Program can only be scheduled under one
    Task at a time in real Logix (confirmed by inspection: every real
    corpus/generated file's ScheduledProgram entries are unique across
    Tasks) -- last one wins on a real conflict, same defensive convention
    already used elsewhere in this project (see report.py's tag_types
    comment) rather than raising on untested territory."""
    mapping: dict[str, str] = {}
    for task in parse_tasks(root):
        for prog_name in task.scheduled_program_names:
            mapping[prog_name] = task.name
    return mapping
