"""ETHERNET-MODULE: a quarter of all real modules, priced by one constant.

Written 2026-09-12. Counting every non-CPU module across the sixteen real
programs gives 438, and the largest single catalog by a wide margin is the
GENERIC `ETHERNET-MODULE` profile at **109 instances -- 25% of them**. It has no
entry in `module_overhead_by_catalog` at all, so every one of those 109 falls
back to the flat cross-catalog default of 1,672 bytes.

A per-catalog constant is not merely imprecise here, it is the wrong SHAPE.
ETHERNET-MODULE is the profile used for any EtherNet/IP device with no AOP:
the connection sizes are typed in by hand, so two instances of the same
"catalog" are different devices. The 109 real instances carry **40 distinct
connection shapes**, with the primary input size spanning 2 to 450 bytes -- a
225x range -- and output 2 to 64:

    x11  In 10  Out 4        x6   In 6   Out 2
    x10  In 450 Out 8        x5   In 12  Out 2
    x9   In 4   Out 2        x5   In 4   Out 6
    x7   In 64  Out 64       x4   In 14  Out 2
                             x4   no connections at all

One number cannot price that set, and this is the concrete case
OQ-MODULESTRUCTURAL was raised for: a module's overhead has to come from its
own declared structure, which is already in the L5X and already parsed, rather
than from a table that can only ever cover catalogs someone captured.

The three rack sweeps say the same thing from another direction -- all 57 rows
captured clean, none ever reconciled, and the per-module error FLIPS SIGN by
family: 1756 chassis cards +523/module (over-charged), 5069 -992/module and
POINT I/O -932/card (both under-charged), with residuals up to 5,831 bytes that
a flat per-family constant does not absorb either. Those three families are
only 14% of the real module population though, so they are a large CORPUS error
and a small real-file one; ETHERNET-MODULE is the opposite.

WHAT THIS BATCH MEASURES. The block is transplanted from a real instance, with
only identity (name, IP) and the two connection sizes changed. Sizes are in
BYTES and the connection data is INT-typed, so the array dimension is
bytes/2 and the `AB:ETHERNET_MODULE_INT_<n>Bytes` type name carries the size --
all three move together in a real export, which is why they are generated from
one number here rather than set independently.

  ARM A  `genem_in{N}` -- primary INPUT size swept 2/4/10/32/64/128/256/450
         bytes at a fixed output of 4. Brackets the whole real range including
         its two extremes. If cost is linear in input bytes, this is the slope.
  ARM B  `genem_out{M}` -- primary OUTPUT size swept 2/4/8/16/32/64 at a fixed
         input of 4. Separates the two directions, which no real instance can
         do because real devices vary both at once.
  ARM C  `genem_n{K}` -- K identical instances at In 10 / Out 4, K = 1/2/4/8.
         The per-module marginal question from OQ-MODULEMARGINAL, asked for the
         one catalog where it matters most on a real file.
  ARM D  `genem_noconn` -- one instance with NO connections, the shape 4 real
         instances actually have. `zero_connection_module_bytes` (2,344) claims
         to cover this; nothing has ever tested it for this profile.

Run: python -m sample_gen.gen_generic_ethernet_module
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

INPUT_SIZES = (2, 4, 10, 32, 64, 128, 256, 450)

# Element data type x byte size. The connection's element TYPE is part of the
# comm-format choice on a generic module, and the real corpus uses three of
# them: INT 130 connections, SINT 80, DINT 2. The same byte size appears under
# different types -- 450 bytes as SINT (14 real instances) and 64 bytes as INT
# (14) -- so if cost follows ELEMENT COUNT rather than byte count, SINT and INT
# at one byte size differ by 2x and DINT/REAL by 4x. Nothing in the corpus can
# separate those two readings, because no real pair holds bytes fixed while the
# type changes.
#
# REAL is the one type with NO corpus instance. It is a legitimate comm-format
# choice on a generic module and the AB:ETHERNET_MODULE_<TYPE>_<n>Bytes naming
# is mechanical, so it is built -- but it is the one arm where a conversion
# failure would be a finding about the shape rather than about the cost.
ELEMENT_BYTES = {"SINT": 1, "INT": 2, "DINT": 4, "REAL": 4}
TYPE_SIZE_PAIRS = (
    (8, "SINT"), (8, "INT"),                                  # commonest small real pair
    (64, "SINT"), (64, "INT"), (64, "DINT"), (64, "REAL"),     # one size, every type
    (450, "SINT"), (450, "INT"),                               # the largest real shape
)
OUTPUT_SIZES = (2, 4, 8, 16, 32, 64)
COUNTS = (1, 2, 4, 8)

_BASE_INPUT = 4     # held fixed while OUTPUT is swept
_BASE_OUTPUT = 4    # held fixed while INPUT is swept

# Config array length, verbatim from the real instance: ConfigSize="0" with a
# 400-element SINT placeholder. Left exactly as captured -- it is identical in
# every real instance, so it cancels in every difference across this batch.
_CONFIG_ELEMENTS = 400


def _elements(count: int, value: str = "0") -> str:
    return "\n".join(f'<Element Index="[{i}]" Value="{value}"/>' for i in range(count))


def _config_tag() -> str:
    zeros = ",".join("0" for _ in range(_CONFIG_ELEMENTS))
    return (
        '<ConfigTag ConfigSize="0" ExternalAccess="Read/Write">\n'
        '<Data Format="L5K">\n'
        f'<![CDATA[[4,1,[{zeros}]]]]>\n'
        '</Data>\n'
        '<Data Format="Decorated">\n'
        '<Structure DataType="AB:ETHERNET_MODULE:C:0">\n'
        f'<ArrayMember Name="Data" DataType="SINT" Dimensions="{_CONFIG_ELEMENTS}" Radix="Hex">\n'
        f'{_elements(_CONFIG_ELEMENTS, "16#00")}\n'
        '</ArrayMember>\n'
        '</Structure>\n'
        '</Data>\n'
        '</ConfigTag>'
    )


def _module_xml(name: str, address: str, input_bytes: int, output_bytes: int,
                with_connection: bool = True, element_type: str = "INT") -> str:
    """One ETHERNET-MODULE, transplanted from the real instance.

    Only identity and the two connection sizes change. Sizes are in BYTES and
    the connection data is INT-typed, so the array dimension is bytes/2 and the
    `AB:ETHERNET_MODULE_INT_<n>Bytes` type name carries the byte count -- in a
    real export all three move together, so they are derived from one number
    here instead of being settable apart and drifting out of agreement.
    """
    head = (
        f'<Module Name="{name}" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" '
        f'ProductCode="18" Major="1" Minor="1" ParentModule="Local" ParentModPortId="2" '
        f'Inhibited="false" MajorFault="false">\n'
        '<EKey State="Disabled"/>\n'
        '<Ports>\n'
        f'<Port Id="2" Address="{address}" Type="Ethernet" Upstream="true"/>\n'
        '</Ports>\n'
    )
    if not with_connection:
        return (
            head
            + '<Communications CommMethod="536870915">\n'
            + _config_tag() + "\n"
            + '<Connections/>\n</Communications>\n</Module>'
        )

    elem = ELEMENT_BYTES[element_type]
    in_words, out_words = input_bytes // elem, output_bytes // elem
    out_l5k = ",".join("0" for _ in range(out_words))
    return (
        head
        + f'<Communications CommMethod="536870915" PrimCxnInputSize="{input_bytes}" '
          f'PrimCxnOutputSize="{output_bytes}">\n'
        + _config_tag() + "\n"
        + '<Connections>\n'
          f'<Connection Name="Standard" RPI="10000" Type="Output" InputCxnPoint="101" '
          f'OutputCxnPoint="100" OutputSize="{output_bytes}" InputSize="{input_bytes}" '
          f'EventID="0" ProgrammaticallySendEventTrigger="false" Unicast="true">\n'
          '<InputTag ExternalAccess="Read/Write">\n'
          '<Data Format="Decorated">\n'
          f'<Structure DataType="AB:ETHERNET_MODULE_{element_type}_{input_bytes}Bytes:I:0">\n'
          f'<ArrayMember Name="Data" DataType="{element_type}" Dimensions="{in_words}" '
          f'Radix="{"Float" if element_type == "REAL" else "Decimal"}">\n'
          f'{_elements(in_words)}\n'
          '</ArrayMember>\n</Structure>\n</Data>\n</InputTag>\n'
          '<OutputTag ExternalAccess="Read/Write">\n'
          '<Data Format="L5K">\n'
          f'<![CDATA[[[{out_l5k}]]]]>\n'
          '</Data>\n'
          '<Data Format="Decorated">\n'
          f'<Structure DataType="AB:ETHERNET_MODULE_{element_type}_{output_bytes}Bytes:O:0">\n'
          f'<ArrayMember Name="Data" DataType="{element_type}" Dimensions="{out_words}" '
          f'Radix="{"Float" if element_type == "REAL" else "Decimal"}">\n'
          f'{_elements(out_words)}\n'
          '</ArrayMember>\n</Structure>\n</Data>\n</OutputTag>\n'
          '</Connection>\n</Connections>\n</Communications>\n</Module>'
    )


_WHY = (
    "ETHERNET-MODULE is the single largest module catalog in the real programs -- 109 of their 438 "
    "non-CPU modules, 25% -- and it has NO entry in module_overhead_by_catalog, so all 109 fall "
    "back to the flat 1,672-byte cross-catalog default. It is the generic profile for any "
    "EtherNet/IP device with no AOP, so its connection sizes are typed in by hand and two "
    "instances of the same 'catalog' are different devices: the 109 real instances carry 40 "
    "distinct connection shapes with input spanning 2 to 450 bytes. One constant cannot price "
    "that, which makes this the concrete case for OQ-MODULESTRUCTURAL. Block transplanted from a "
    "real instance; only identity and the swept size differ."
)


def _write(name: str, modules: str, description: str) -> None:
    l5x = build_l5x(target_name=name.replace("_", "")[:24], tags_xml="",
                    extra_modules_xml=modules)
    out = OUT / f"{name}.L5X"
    write_sample_unmodeled(l5x, out)
    append_manifest_row(name, description, "modules", out, 0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for size in INPUT_SIZES:
        _write(f"genem_in{size:03d}",
               _module_xml("GenEm1", "192.168.1.20", size, _BASE_OUTPUT),
               f"ONE ETHERNET-MODULE with primary INPUT size {size} bytes and output held at "
               f"{_BASE_OUTPUT}. Arm A of the input sweep (2/4/10/32/64/128/256/450), which "
               f"brackets the entire real range including both extremes. {_WHY}")
        n += 1
    for size in OUTPUT_SIZES:
        _write(f"genem_out{size:03d}",
               _module_xml("GenEm1", "192.168.1.20", _BASE_INPUT, size),
               f"ONE ETHERNET-MODULE with primary OUTPUT size {size} bytes and input held at "
               f"{_BASE_INPUT}. Arm B separates the two directions, which no real instance can do "
               f"because real devices vary both at once. {_WHY}")
        n += 1
    for k in COUNTS:
        mods = "\n".join(_module_xml(f"GenEm{i + 1}", f"192.168.1.{20 + i}", 10, 4)
                         for i in range(k))
        _write(f"genem_n{k:02d}", mods,
               f"{k} identical ETHERNET-MODULEs at input 10 / output 4 (the most common real "
               f"shape, 11 instances). Arm C asks OQ-MODULEMARGINAL's per-module question for the "
               f"one catalog where it matters most on a real file: the measured law elsewhere is "
               f"over-prediction = discount x (n-1), and this catalog has no discount on record "
               f"because it has no entry at all. {_WHY}")
        n += 1
    for size, etype in TYPE_SIZE_PAIRS:
        _write(f"genem_dt{etype.lower()}_{size:03d}",
               _module_xml("GenEm1", "192.168.1.20", size, _BASE_OUTPUT, element_type=etype),
               f"ONE ETHERNET-MODULE whose input connection is {size} bytes of {etype} elements "
               f"({size // ELEMENT_BYTES[etype]} elements), output held at {_BASE_OUTPUT} bytes of "
               f"INT. Arm E crosses element DATA TYPE with byte size, which nothing in the corpus "
               f"can do: real generic modules use INT (130 connections), SINT (80) and DINT (2), "
               f"and the same byte size appears under different types -- 450 bytes as SINT (14 real "
               f"instances) and 64 bytes as INT (14) -- but no real pair holds bytes fixed while "
               f"the type changes. If cost follows ELEMENT COUNT rather than byte count, SINT and "
               f"INT at one size differ by 2x and DINT/REAL by 4x. "
               + ("REAL is the one type with no corpus instance: it is a legitimate comm-format "
                  "choice and the AB:ETHERNET_MODULE_<TYPE>_<n>Bytes naming is mechanical, so a "
                  "conversion failure here would be a finding about the shape rather than the cost."
                  if etype == "REAL" else "") + f" {_WHY}")
        n += 1

    _write("genem_noconn", _module_xml("GenEm1", "192.168.1.20", 0, 0, with_connection=False),
           f"ONE ETHERNET-MODULE with NO connections -- the shape four real instances actually "
           f"have. zero_connection_module_bytes (2,344, FITTED) claims to cover this case and has "
           f"never been tested for this profile. Arm D. {_WHY}")
    n += 1
    print(f"Total: {n}")


if __name__ == "__main__":
    main()
