"""Regression coverage for gen_composite_realistic.py's real generator bugs
-- James, 2026-09-02: "make sure this rule is hard coded correctly for
your generator" (the IP-address-out-of-range fix). Locks in the fix so a
future change to _modules_xml_unique_ips can't silently reintroduce an
invalid IPv4 octet the way the original `base = 60 + (i+1)*10` formula did
once a file combined more than ~19 module catalogs (v1/v2 never did; v3
routinely combines 15-34)."""

from __future__ import annotations

import re

from sample_gen.gen_composite_realistic import _MODULE_CATALOGS, _modules_xml_unique_ips

_IP_RE = re.compile(r"192\.168\.(\d+)\.(\d+)")


def _octets_in_range(xml: str) -> bool:
    return all(
        0 <= int(third) <= 255 and 0 <= int(fourth) <= 255
        for third, fourth in _IP_RE.findall(xml)
    )


def test_large_catalog_list_never_produces_an_out_of_range_ip_octet():
    # Real Studio 5000 error, James 2026-09-02: "Failed to set the
    # 'Address' property (Address out of range.)" on 5 different modules
    # across 2 different v3 files -- every one traced to a 4th-octet value
    # over 255 once a file's catalog list passed ~19 entries. Exercise a
    # list well past that (matches v3's max: up to 34 catalogs/file) and
    # confirm every emitted address stays in bounds.
    catalogs = (_MODULE_CATALOGS * 3)[:40]
    xml = _modules_xml_unique_ips(catalogs)
    assert _octets_in_range(xml)


def test_repeated_full_catalog_list_stays_in_range():
    # A file could in principle reuse the full real catalog pool more than
    # once (e.g. two composite files sharing the same module mix) -- not
    # just a slice past the old ~19-catalog ceiling.
    catalogs = _MODULE_CATALOGS * 2
    xml = _modules_xml_unique_ips(catalogs)
    assert _octets_in_range(xml)


def test_small_catalog_list_still_uses_the_original_192_168_1_block():
    # v1/v2 never exceeded 4 catalogs/file -- confirms the fix is additive
    # (a new 3rd-octet block only kicks in once needed), not a behavior
    # change for the already-validated small-file case.
    catalogs = _MODULE_CATALOGS[:3]
    xml = _modules_xml_unique_ips(catalogs)
    assert "192.168.1." in xml
    assert _octets_in_range(xml)
