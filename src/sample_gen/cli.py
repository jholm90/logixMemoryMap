"""L5X sample generator CLI (James, 2026-08-20: "the l5x generator
application where you make up the l5x files based on things you want to
test -- UDT size, comment length for bits or rungs etc.").

Every subcommand writes a full L5X to samples/generated/<category>/ and
logs a manifest.csv row with predicted_bytes already filled in (from this
project's own sizing engine) -- actual_bytes stays blank until James runs
it through Studio 5000 and reports back.

Examples:
  python -m sample_gen.cli udt --name MotorStatus --member Running:BOOL \\
      --member Speed:DINT --member Faulted:BOOL --out motorstatus_test

  python -m sample_gen.cli tags --type DINT --dims 10000 --out dint_10k_array

  python -m sample_gen.cli rungs --count 1000 --instr "XIC(In{i})OTE(Out{i});" \\
      --comment-len 100 --out xic_ote_1000_comment100
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sample_gen.builders import MemberSpec, rungs_xml, tag_xml, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated"


def _filler_comment(length: int, prefix: str = "") -> str | None:
    if length <= 0:
        return None
    body = (prefix + "x" * length)[:length] if prefix else "x" * length
    return body


def _parse_member(spec: str) -> MemberSpec:
    # NAME:TYPE or NAME:TYPE:DIM
    parts = spec.split(":")
    if len(parts) == 2:
        name, dt = parts
        return MemberSpec(name, dt)
    if len(parts) == 3:
        name, dt, dim = parts
        return MemberSpec(name, dt, int(dim))
    raise argparse.ArgumentTypeError(f"member spec must be NAME:TYPE or NAME:TYPE:DIM, got {spec!r}")


def _cmd_udt(args: argparse.Namespace) -> int:
    members = [_parse_member(m) for m in args.member]
    if args.member_desc_len:
        desc = _filler_comment(args.member_desc_len)
        members = [MemberSpec(m.name, m.data_type, m.dimension, desc) for m in members]

    udt_frag = udt_xml(args.name, members)
    tag_frag = tag_xml("TestInstance", args.name)
    l5x = build_l5x(
        target_name=args.name,
        tags_xml=tag_frag,
        extra_datatypes_xml=udt_frag,
    )

    out_path = OUT_ROOT / "udt" / f"{args.out}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(args.out, f"UDT {args.name}: {', '.join(m.data_type for m in members)}", "udt", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 0


def _cmd_tags(args: argparse.Namespace) -> int:
    dims = tuple(int(d) for d in args.dims.split(",")) if args.dims else ()
    desc = _filler_comment(args.desc_len) if args.desc_len else None

    tags = []
    for i in range(args.count):
        name = f"{args.out}_{i}" if args.count > 1 else args.out
        tags.append(tag_xml(name, args.type, dims, description=desc))
    tags_frag = "\n".join(tags)

    l5x = build_l5x(target_name=args.out, tags_xml=tags_frag)
    out_path = OUT_ROOT / "tags" / f"{args.out}.L5X"
    bytes_ = write_sample(l5x, out_path)
    dims_desc = f"[{args.dims}]" if dims else ""
    append_manifest_row(args.out, f"{args.count}x {args.type}{dims_desc} tag(s)", "tag", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")
    return 0


def _cmd_rungs(args: argparse.Namespace) -> int:
    comment_fn = (lambda i: _filler_comment(args.comment_len)) if args.comment_len else None
    instr_fn = lambda i: args.instr.format(i=i)
    rungs_frag = rungs_xml(args.count, instr_fn, comment_fn)

    l5x = build_l5x(target_name=args.out, tags_xml="", extra_rungs_xml=rungs_frag)
    out_path = OUT_ROOT / "logic" / f"{args.out}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(
        args.out, f"{args.count} rungs of {args.instr!r}, comment_len={args.comment_len}",
        "logic_bit", out_path, bytes_,
    )
    print(f"Wrote {out_path} (predicted {bytes_} bytes -- note: this is tag/UDT space only, "
          f"logic compiled size is NOT modeled yet, see PROJECT_PLAN.md Phase 4)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sample_gen")
    subparsers = parser.add_subparsers(dest="command", required=True)

    udt_parser = subparsers.add_parser("udt", help="Generate a UDT + one tag of that type")
    udt_parser.add_argument("--name", required=True, help="UDT type name")
    udt_parser.add_argument("--member", action="append", required=True,
                             help="NAME:TYPE or NAME:TYPE:DIM, repeatable, in declared order")
    udt_parser.add_argument("--member-desc-len", type=int, default=0,
                             help="Give every member a filler Description of this length (0 = none)")
    udt_parser.add_argument("--out", required=True, help="Output file basename")
    udt_parser.set_defaults(func=_cmd_udt)

    tags_parser = subparsers.add_parser("tags", help="Generate N tags of a given type/dimensions")
    tags_parser.add_argument("--type", required=True, help="DataType (atomic, BOOL, or a UDT/AOI name)")
    tags_parser.add_argument("--dims", default="", help="Comma-separated dimensions, e.g. '10000' or '4,4'")
    tags_parser.add_argument("--count", type=int, default=1, help="How many tags to generate")
    tags_parser.add_argument("--desc-len", type=int, default=0,
                              help="Give every tag a filler Description of this length (0 = none)")
    tags_parser.add_argument("--out", required=True, help="Output file basename / tag name prefix")
    tags_parser.set_defaults(func=_cmd_tags)

    rungs_parser = subparsers.add_parser("rungs", help="Generate N rungs of a given instruction pattern")
    rungs_parser.add_argument("--count", type=int, required=True)
    rungs_parser.add_argument("--instr", required=True,
                               help="Instruction text template, {i} substituted with rung index, "
                                    "e.g. 'XIC(In{i})OTE(Out{i});'")
    rungs_parser.add_argument("--comment-len", type=int, default=0,
                               help="Give every rung a filler comment of this length (0 = none) -- OQ-COMMENTS")
    rungs_parser.add_argument("--out", required=True, help="Output file basename")
    rungs_parser.set_defaults(func=_cmd_rungs)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
