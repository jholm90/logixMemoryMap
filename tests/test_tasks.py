import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.tasks import parse_tasks, program_to_task_map

_TASKS_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <Tasks>
      <Task Name="MainTask" Type="CONTINUOUS" Priority="10" Watchdog="500">
        <ScheduledPrograms>
          <ScheduledProgram Name="MainProgram"/>
        </ScheduledPrograms>
      </Task>
      <Task Name="PeriodicTask" Type="PERIODIC" Rate="100" Priority="5" Watchdog="50">
        <ScheduledPrograms>
          <ScheduledProgram Name="ProgB"/>
          <ScheduledProgram Name="ProgC"/>
        </ScheduledPrograms>
      </Task>
    </Tasks>
  </Controller>
</RSLogix5000Content>
"""


def _root(xml: str) -> ET.Element:
    return ET.fromstring(xml)


def test_parse_tasks_returns_name_and_scheduled_programs():
    tasks = parse_tasks(_root(_TASKS_XML))
    assert len(tasks) == 2
    main = next(t for t in tasks if t.name == "MainTask")
    assert main.scheduled_program_names == ("MainProgram",)
    periodic = next(t for t in tasks if t.name == "PeriodicTask")
    assert periodic.scheduled_program_names == ("ProgB", "ProgC")


def test_no_tasks_element_returns_empty_list():
    root = ET.fromstring('<RSLogix5000Content><Controller Name="Test"/></RSLogix5000Content>')
    assert parse_tasks(root) == []


def test_program_to_task_map():
    mapping = program_to_task_map(_root(_TASKS_XML))
    assert mapping == {"MainProgram": "MainTask", "ProgB": "PeriodicTask", "ProgC": "PeriodicTask"}
