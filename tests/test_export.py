import csv
import io
import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.export import write_csv, write_xlsx
from l5x_memory_analyzer.sizing.report import build_report

MODEL = load_memory_model()

_XML = """
<RSLogix5000Content SchemaRevision="1.0">
  <Controller Name="Test">
    <DataTypes/>
    <AddOnInstructionDefinitions/>
    <Tags>
      <Tag Name="RealDint" TagType="Base" DataType="DINT"/>
    </Tags>
    <Programs/>
  </Controller>
</RSLogix5000Content>
"""


def test_write_csv_round_trips_every_entry():
    root = ET.fromstring(_XML)
    entries, errors = build_report(root, MODEL)
    text = write_csv(entries, errors)

    rows = list(csv.reader(io.StringIO(text)))
    assert rows[0] == ["path", "category", "data_type", "bytes", "pct_of_total", "tier", "basis"]
    data_rows = rows[1 : 1 + len(entries)]
    assert len(data_rows) == len(entries)
    # Sorted by bytes descending, same as the CLI's `size` command.
    sizes = [int(r[3]) for r in data_rows]
    assert sizes == sorted(sizes, reverse=True)
    paths = {r[0] for r in data_rows}
    assert paths == {e.path for e in entries}
    # No errors in this minimal fixture -- no ERRORS section emitted.
    assert not any(row and row[0] == "ERRORS" for row in rows)


def test_write_xlsx_produces_a_real_workbook():
    openpyxl = pytest.importorskip("openpyxl")
    root = ET.fromstring(_XML)
    entries, errors = build_report(root, MODEL)
    data = write_xlsx(entries, errors)

    wb = openpyxl.load_workbook(io.BytesIO(data))
    ws = wb["Report"]
    header = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    assert header == ["path", "category", "data_type", "bytes", "pct_of_total", "tier", "basis"]
    data_rows = list(ws.iter_rows(min_row=2, values_only=True))
    assert len(data_rows) == len(entries)
    assert "Errors" not in wb.sheetnames
