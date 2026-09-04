"""CLI entry point.

`dump`: load an L5X file and print its raw XML back out -- satisfies the
Phase 0 exit criterion (docs/PROJECT_PLAN.md), proves the skeleton runs
end to end before the sizing engine existed.

`size`: run the Phase 1 tag/UDT sizing engine and print a flat byte
breakdown -- see docs/TASKS.md Phase 1 output-contract item.

`ui`: serve the Phase 2 treemap UI over a local web server. l5x_path is
optional -- omit it to start with the File->Open picker instead (James
2026-08-20: desktop-shortcut launch shouldn't require a command prompt).

`export`: write the same flat byte breakdown as `size` to a CSV or XLSX
file instead of stdout (docs/TASKS.md Phase 6 "Export report"). Format is
inferred from the output path's extension.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET

from l5x_memory_analyzer.parser.load import L5XFormatError, load_l5x
from l5x_memory_analyzer.parser.export_scope import (
    context_names,
    detect_export_scope,
    split_totals,
)
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report


def _cmd_dump(args: argparse.Namespace) -> int:
    try:
        doc = load_l5x(args.l5x_path)
    except (L5XFormatError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"# {doc.path.name} "
        f"(SchemaRevision={doc.schema_revision}, SoftwareRevision={doc.software_revision})",
        file=sys.stderr,
    )
    ET.indent(doc.root, space="  ")
    print(ET.tostring(doc.root, encoding="unicode"))
    return 0


def _cmd_size(args: argparse.Namespace) -> int:
    try:
        doc = load_l5x(args.l5x_path)
    except (L5XFormatError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if doc.is_safety_project:
        print(
            f"warning: this is a Safety-rated project ({doc.safety_level}) -- Safety Task/Program "
            f"content is NOT sized by this tool at all. The total below is understated, not a full "
            f"picture. Treat it as informational only until Safety content sizing is built (OQ-SAFETY).",
            file=sys.stderr,
        )

    model = load_memory_model()
    entries, errors = build_report(doc.root, model)
    entries = sorted(entries, key=lambda e: e.bytes, reverse=True)

    # Export scope up front, before any number (2026-09-04). A partial
    # export's total is not comparable to a controller Capacity reading,
    # and the three-way split is the only honest way to state it: what the
    # exported thing costs, versus what it drags along that the destination
    # controller may already have.
    scope = detect_export_scope(doc.root)
    totals = split_totals(entries, context_names(doc.root, scope))
    if not scope.is_whole_controller:
        print(f"scope: PARTIAL EXPORT -- {scope.describe()}", file=sys.stderr)
        print(f"  target  {totals['target']:>12,}  the exported item itself", file=sys.stderr)
        print(f"  context {totals['context']:>12,}  declarations it references -- cost these "
              f"ONLY if the destination controller does not already have them", file=sys.stderr)
        print(f"  total   {totals['total']:>12,}  (no project base load; not comparable to a "
              f"controller Capacity reading)", file=sys.stderr)
    else:
        print(f"scope: whole controller project -- project overhead "
              f"{totals['project']:,} of {totals['total']:,}", file=sys.stderr)


    print(f"{'BYTES':>10}  {'%':>6}  {'BASIS':<9}  {'CATEGORY':<15}  PATH")
    for e in entries:
        print(f"{e.bytes:>10}  {e.pct_of_total:>5.1f}%  {e.basis:<9}  {e.category:<15}  {e.path}")

    if errors:
        print(f"\n{len(errors)} tag(s) could not be sized:", file=sys.stderr)
        for err in errors:
            print(f"  {err.path}: {err.message}", file=sys.stderr)

    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    try:
        doc = load_l5x(args.l5x_path)
    except (L5XFormatError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if doc.is_safety_project:
        print(
            f"warning: this is a Safety-rated project ({doc.safety_level}) -- Safety Task/Program "
            f"content is NOT sized by this tool at all. The exported total is understated, not a "
            f"full picture.",
            file=sys.stderr,
        )

    suffix = args.output_path.lower().rsplit(".", 1)[-1] if "." in args.output_path else ""
    if suffix not in ("csv", "xlsx"):
        print(f"error: output path must end in .csv or .xlsx, got {args.output_path!r}", file=sys.stderr)
        return 1

    model = load_memory_model()
    entries, errors = build_report(doc.root, model)

    from l5x_memory_analyzer.sizing.export import write_csv, write_xlsx

    if suffix == "csv":
        with open(args.output_path, "w", encoding="utf-8", newline="") as f:
            f.write(write_csv(entries, errors))
    else:
        try:
            data = write_xlsx(entries, errors)
        except ImportError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        with open(args.output_path, "wb") as f:
            f.write(data)

    print(f"wrote {args.output_path}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} tag(s) could not be sized -- see the Errors section/sheet", file=sys.stderr)
    return 0


def _cmd_ui(args: argparse.Namespace) -> int:
    from l5x_memory_analyzer.ui.server import run

    print(f"Serving http://{args.host}:{args.port} (Ctrl+C to stop)", file=sys.stderr)
    run(args.l5x_path, host=args.host, port=args.port, open_browser=not args.no_browser)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="l5x-memory-analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dump_parser = subparsers.add_parser("dump", help="Load an L5X file and print its raw XML")
    dump_parser.add_argument("l5x_path", help="Path to an L5X export file")
    dump_parser.set_defaults(func=_cmd_dump)

    size_parser = subparsers.add_parser("size", help="Print a tag/UDT byte-size breakdown")
    size_parser.add_argument("l5x_path", help="Path to an L5X export file")
    size_parser.set_defaults(func=_cmd_size)

    export_parser = subparsers.add_parser("export", help="Write a byte-size breakdown to CSV or XLSX")
    export_parser.add_argument("l5x_path", help="Path to an L5X export file")
    export_parser.add_argument("output_path", help="Output file path, ending in .csv or .xlsx")
    export_parser.set_defaults(func=_cmd_export)

    ui_parser = subparsers.add_parser("ui", help="Serve the treemap UI, optionally for an L5X file")
    ui_parser.add_argument("l5x_path", nargs="?", default=None,
                            help="Path to an L5X export file (omit to start with File->Open)")
    ui_parser.add_argument("--host", default="127.0.0.1")
    ui_parser.add_argument("--port", type=int, default=8765)
    ui_parser.add_argument("--no-browser", action="store_true",
                            help="Don't auto-open the default browser on start")
    ui_parser.set_defaults(func=_cmd_ui)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
