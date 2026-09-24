"""Loads every sizing constant from `memory_model.yaml`, which mirrors
`docs/MEMORY_MODEL.md`.

Parser and sizing code pulls byte sizes and packing rules from here and never
hardcodes them inline. That file is the single source of truth and is expected to
move as capture data lands, so a literal in the code is a value that will silently
go stale.

THE CONFIDENCE TIERS, and what each one permits:

  KNOWN    Measured directly, or read straight out of the L5X. Either two
           independent derivations agree, or a capture sits at 0.0000% residual
           across a range of counts. A KNOWN constant is not re-derived.
  FITTED   Regressed from real capture data. Right on average, carries residual
           error, and can be wrong off the range it was fitted on.
  ASSUMED  No capture behind it. Derived from documentation or inference.
  UNKNOWN  Not modelled. Reported as a coverage gap rather than guessed.

`weakest` propagates the tier upward, so one stale ASSUMED on a leaf type marks
everything above it as assumed. `scripts/audit_confidence.py` is the check that
the tiers match the capture data on disk; run it after every reconciliation.

A CONSTANT MEASURED ALONE, AT SEVERAL COUNTS, WITH ZERO RESIDUAL IS KNOWN EVEN IF
THE BLOCK AROUND IT READS FITTED. Those carry their own `*_confidence: KNOWN` key
and are pinned by a test. A constant left reading FITTED gets re-derived, which
has already cost whole sessions.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_DEFAULT_PATH = Path(__file__).with_name("memory_model.yaml")


@dataclass(frozen=True)
class AtomicType:
    bytes: int
    confidence: str


@dataclass(frozen=True)
class BoolModel:
    standalone_tag_bytes: int
    standalone_confidence: str
    member_bits_per_backing_byte: int
    member_backing_type: str
    member_confidence: str
    array_bits_per_packed_word: int
    array_packed_word_bytes: int
    array_confidence: str


@dataclass(frozen=True)
class StringModel:
    len_field_bytes: int
    default_data_bytes: int
    confidence: str
    custom_confidence: str
    custom_definition_base: int
    custom_definition_namelen_offset: int
    custom_definition_namelen_bucket: int
    custom_definition_confidence: str
    builtin_tag_overhead_correction: int
    builtin_tag_overhead_correction_confidence: str
    custom_data_padding_multiple: int
    custom_mod4eq1_definition_bonus: int
    custom_data_padding_confidence: str

    def custom_definition_cost_for(self, type_name_length: int) -> int:
        """Custom StringFamily type's own one-time definition cost --
        OQ-CUSTOMSTRINGTYPENAME, SOLVED . A clean step function
        of the type's own name length, confirmed exact against 22 real
        dense-sweep points (every length 1-16 plus 20/24/28/32/36/40) and
        3 more confirming it's identical whether the type is used
        standalone or as a UDT member (no separate nesting cost) -- see
        memory_model.yaml for the full derivation."""
        bucket = self.custom_definition_namelen_bucket
        return self.custom_definition_base + bucket * (
            (type_name_length - self.custom_definition_namelen_offset) // bucket
        )


@dataclass(frozen=True)
class StringArrayModel:
    builtin_confidence: str
    builtin_array_base: int
    builtin_per_element: int
    custom_confidence: str
    custom_array_base: int
    custom_per_element: int

    def custom_base_for(self, type_name_length: int) -> tuple[int, str]:
        """One-time array-level cost for an array of a custom string type.

        Takes the name length only so callers need not change; the answer
        does not depend on it. That was measured, not assumed: the closing
        batch differenced every array against a scalar control of the same
        type at the same name length, and the remainder was a flat 936 at
        all 8 measured lengths from 4 to 40 characters.

        An earlier two-point reading had this varying with name length
        (11 -> 4, 13 -> 12). It was wrong, and wrong in an instructive
        way: with no scalar control, the type DEFINITION's name-length
        step was being attributed to the array base.
        """
        return self.custom_array_base, self.custom_confidence


@dataclass(frozen=True)
class PredefinedArrayStructure:
    base: int
    per_element: int
    confidence: str


@dataclass(frozen=True)
class UdtModel:
    alignment_confidence: str


@dataclass(frozen=True)
class ArrayModel:
    atomic_confidence: str
    udt_confidence: str


@dataclass(frozen=True)
class AoiArrayModel:
    flat_discount: int
    bool_word_size: int
    bool_word_extra: int
    enable_bits_packed_with_bools: int
    block_alignment_bytes: int
    array_tag_flat_bytes: int
    confidence: str


@dataclass(frozen=True)
class AoiDefinitionModel:
    """One itemised AOI-definition cost -- see memory_model.yaml aoi_definition
    for the 124-file derivation and for what each of the four superseded terms
    (per_declared_item, per_type_rate, the linear member-name rate and
    aoi_member_type_extra) was really measuring."""

    base: int
    confidence: str
    name_length_bucket_bytes: int
    name_length_floor_bytes: int
    name_length_bucket_confidence: str
    per_member_descriptor_bytes: int = 0
    bool_word_bytes: int = 0
    bool_word_bits: int = 32
    enable_bits: int = 2
    name_pool_alignment_bytes: int = 8
    name_pool_per_name_bytes: int = 1
    # The definition as a whole occupies a whole number of
    # total_alignment_bytes, measured around the project-wide 1-byte offset
    # (total_alignment_offset) the other terms carry. 0 disables alignment.
    total_alignment_bytes: int = 0
    total_alignment_offset: int = 0

    def aligned_total(self, raw_total: int) -> int:
        """Round a summed definition cost up to its storage alignment.

        Measured on 125 clean def-only captures: every file the unaligned sum
        put at 4 mod 8 read exactly 4 bytes high, and every file it put at 0
        mod 8 read exactly as predicted. Aligning (raw + 1) to 8 and removing
        the 1 again moves 74 of them onto the lattice the other 51 were
        already on. See memory_model.yaml aoi_definition.
        """
        align = self.total_alignment_bytes
        if align <= 1:
            return raw_total
        off = self.total_alignment_offset
        return align * -(-(raw_total + off) // align) - off

    def member_name_pool_bytes(self, member_names) -> int:
        """The declared members' names, pooled and rounded up.

        One byte per name on top of its characters, then the whole total
        rounded up to name_pool_alignment_bytes -- not a per-name rounding and
        not the old 1-byte-per-character-with-3-free rate, both of which fit
        the single name-length sweep they were derived from and then leaked
        into every other family.
        """
        align = self.name_pool_alignment_bytes
        chars = sum(len(n) + self.name_pool_per_name_bytes for n in member_names)
        if align <= 1:
            return chars
        return align * -(-chars // align)

    def bool_word_cost(self, bool_count: int) -> int:
        """The words the declared scalar BOOLs occupy, with EnableIn/EnableOut
        counted as two further bits in the same words -- the same enable-bit
        correction the instance-array side carries."""
        bits = bool_count + self.enable_bits
        return self.bool_word_bytes * -(-bits // self.bool_word_bits)

    def name_length_bytes(self, name: str) -> int:
        # OQ-AOIDEF closeout, wired -- real data
        # (aoiname_len08/09/13/16/20/25/30) confirmed 7/7 exact against
        # `8*max(0,(len-8)//4) - 8`. Unlike UDT-definition's own
        # 8*ceil(len/8) step, an AOI type name's cost isn't purely
        # length-driven: there's a flat -8 floor (matching the same
        # -8-byte universal per-file residual seen throughout this
        # project) that any name length 8-9 hits, THEN +8 every 4
        # characters beyond that -- see memory_model.yaml aoi_definition
        # for the full derivation. Not confirmed below len=8 (no real
        # data there), but the bucket floors at the same -8 rather than
        # extrapolating further negative for very short names.
        #
        # Bucket boundary fixed: the original `(len-7)//4`
        # divisor (chosen to fit only the 7 tested lengths, which happen
        # to skip every len==3 (mod 4)) put len=19 one bucket too high.
        # Cross-checked against real captures of two same-shape (10 BOOL
        # In/10 BOOL Out/10 BOOL Local) AOI array-packing files that only
        # differ by AOI type name length -- AoiPureBoolDense (16 chars,
        # confirmed bucket2) and AoiPureBoolBoundary (19 chars) -- every
        # count point (n=16) lands on the exact same total byte count
        # under `(len-8)//4` (bucket2 for both) but disagreed by 8 bytes
        # under the old divisor (which put len=19 in bucket3). The 7
        # originally-tested lengths (8,9,13,16,20,25,30) are all
        # unaffected by this change; only len%4==3 (11,15,19,23,27,...)
        # shifts down one bucket.
        bucket = max(0, (len(name) - 8) // 4)
        return self.name_length_bucket_bytes * bucket + self.name_length_floor_bytes


@dataclass(frozen=True)
class TagOverheadModel:
    flat_base: int
    per_8_chars: int
    confidence: str

    def bytes_for(self, name: str) -> int:
        return self.flat_base + self.per_8_chars * (len(name) // 8)


@dataclass(frozen=True)
class UdtDefinitionModel:
    base: int
    per_member: int
    name_per_8_chars: int
    bool_run_bonus: int
    confidence: str
    # The declared MEMBERS' own names, pooled the same way an AOI definition's
    # are -- see memory_model.yaml udt_definition. Charged zero until
    # when the udtmn_* length sweep measured it at eight lengths.
    member_name_pool_alignment_bytes: int = 0
    member_name_pool_per_name_bytes: int = 1

    def member_name_pool_bytes(self, member_names) -> int:
        """One byte per name on top of its characters, total rounded up.

        The SAME pool law as AoiDefinitionModel.member_name_pool_bytes, and
        deliberately so -- it is the same thing, a definition's member names,
        in the same file format. Measured independently here on
        udtmn_bool_len{02,04,07,08,12,16,24,32}_b04, four BOOL members with the
        name length as the only variable: the observed increments are
        +8 +8 +8 +16 +16 +32 +32 and the pool's own are the same seven numbers.
        A raw 1-byte-per-character rate fits five of the seven and misses the
        04->07 and 07->08 steps, which is what discriminates the two forms.
        """
        align = self.member_name_pool_alignment_bytes
        if align <= 0:
            return 0
        chars = sum(len(n) + self.member_name_pool_per_name_bytes for n in member_names)
        if align <= 1:
            return chars
        return align * -(-chars // align)

    def bytes_for(self, name: str, declared_member_count: int, bool_run_count: int,
                  member_names=()) -> int:
        # ONE shared base -- see memory_model.yaml udt_definition for why
        # this isn't two separately-additive base constants (168 for
        # member-count, 224 for name-length): those were two different 1-D
        # slices through the same 2-variable surface, both correct in
        # isolation (holding the other variable at its sweep's baseline),
        # but adding them together double-counts the shared base they
        # both include. Solving the two slices simultaneously gives one
        # true base of 160. bool_run_bonus applies once per separate BOOL
        # run (each with its own hidden backing SINT) -- a non-BOOL member
        # breaking a run means a second hidden SINT and a second bonus.
        total = self.base + self.per_member * declared_member_count + self.name_per_8_chars * math.ceil(len(name) / 8)
        total += self.bool_run_bonus * bool_run_count
        total += self.member_name_pool_bytes(member_names)
        return total


@dataclass(frozen=True)
class CptRealDestModel:
    """REAL-destination CPT cost (OQ-CMPCPTLAYOUT, wired) -- see
    memory_model.yaml cpt_expression.real_dest for the full derivation and
    the flagged coverage gaps."""

    expression_base: int
    extra_operator: int
    # Measured base by operator count, before operand/literal terms. Falls
    # back to expression_base + extra_operator*n outside the table.
    operator_count_base: dict[int, int]
    pow_extra: int
    pow_with_tier2_extra: int
    per_int_operand: int
    narrow_widening_block: int
    per_float_literal: int
    confidence: str

    def base_for(self, operators: list[str]) -> int:
        n = len(operators)
        linear = self.expression_base + self.extra_operator * n
        if any(op == "**" for op in operators):
            # A pow expression uses the PLAIN linear base -- it does not get
            # the measured 5-operator bump below. See the class docstring.
            has_t2 = any(op in ("*", "/", "MOD") for op in operators)
            return linear + self.pow_extra + (self.pow_with_tier2_extra if has_t2 else 0)
        return self.operator_count_base.get(n, linear)

    def cost_for(
        self,
        operators: list[str],
        n_int_operands: int,
        n_float_literals: int,
        base_read: int,
        has_narrow_operand: bool = False,
    ) -> int:
        """REFIT -- exact on all 47 captured REAL-dest CPT calls.

        The operator ladder is `124 + 40*n` and the operator's TIER does not
        matter here (unlike the integer path, where * and / cost more than
        + and -): fitting a + b*tier1 + c*tier2 against the opcount files
        returns b = c = 40. That makes sense for a float evaluation.

        Two empirical corrections sit on top, and neither has a known
        mechanism. They are stored as measurements, not as a theory:

        1. A 5-operator expression costs 328, not the 324 the ladder
           predicts. Three files from three different generators
           (cptmix_real*, cptcx_constants_floatconst_n4,
           instr_cpt_literaloperands) independently agree on 328, and 6 and
           8 operators are back on the ladder exactly (364, 444). So it is
           not a ">=5" step -- the old model had it as one and over-charged
           the 6- and 8-operator files by 4 each.
        2. `**` adds 8, plus another 4 if the expression also contains a
           tier-2 operator (* / MOD). And a pow expression does NOT get
           correction 1: powmulti_n05 lands on 324+12, not 328+12.

        Both are the kind of thing that wants an operator-count x
        tier-composition sweep to explain rather than a story invented to
        fit 47 points. See OQ-CPTREALDEST.

        The operand terms:
          per_int_operand   40 for every DINT/SINT/INT operand and integer
                            literal -- the conversion into the float
                            evaluation. NOT charged for LINT: the
                            SINT/LINT isolation pair is the same expression
                            with only the operand type swapped, and the
                            LINT file lands byte-identical to the all-REAL
                            control at 244/rung.
          narrow_widening_block: "ints will use a behind
                            the scenes conversion to dint". SINT/INT are
                            widened first; LINT, already 64-bit, is not.
                            ONE-POINT FIT and the per-operand/per-call
                            split is undetermined -- see the yaml comment
                            and OQ-CPTNARROW.
          per_float_literal 4, confirmed across 12 files at 1, 2 and 3
                            float literals.
        """
        if not operators:
            # A bare REAL copy, 'CPT(R1,R0)' -- no operators, so no float
            # arithmetic to charge differently. Falls through to the plain
            # base_read the integer path would have charged.
            return base_read + self.per_int_operand * n_int_operands
        return (
            self.base_for(operators)
            + self.per_int_operand * n_int_operands
            + (self.narrow_widening_block if has_narrow_operand else 0)
            + self.per_float_literal * n_float_literals
        )


@dataclass(frozen=True)
class CptExpressionModel:
    base_read: int
    operator_tier_costs: dict[str, int]
    per_extra_same_tier_operand: int
    two_tier_mix_base: int
    two_tier_mix_per_tier1: int
    two_tier_mix_per_tier2: int
    pow_tier_mix_base: int
    pow_tier_mix_per_operator: int
    three_tier_mix_base_by_remainder: dict[int, int]
    three_tier_mix_per_pow_operand: int
    real_dest: "CptRealDestModel"
    # Per-tier override for the rate above, keyed by the operator's own tier
    # cost. The scalar was measured on ADD alone; tier 2 is 40, not 24.
    per_extra_same_tier_by_tier_cost: dict = field(default_factory=dict)
    # ARRANGEMENT: a two-tier mix whose leading run of tier-1 operators is
    # exactly this long, before the first tier-2 operator, costs extra.
    # OQ-CPTARRANGE, measured -- see memory_model.yaml.
    leading_tier1_run_length: int = 0
    leading_tier1_run_bytes: int = 0

    def leading_tier1_run_extra(self, tiers: list[int], add_tier: int) -> int:
        """The arrangement term: tier COUNTS are not enough.

        `L0+L1+L2*L3` and `L0+L1*L2+L3` have identical tier counts and differ by
        4 real bytes. Across the 28-file cptarrange_* sweep -- four arrangements
        at every operator count 3 through 9, tier counts held fixed -- the
        discriminator is exactly how many tier-1 operators precede the first
        tier-2 one, and only a run of exactly two costs anything.
        """
        if not self.leading_tier1_run_bytes:
            return 0
        run = 0
        for tier in tiers:
            if tier != add_tier:
                break
            run += 1
        return self.leading_tier1_run_bytes if run == self.leading_tier1_run_length else 0

    @staticmethod
    def _normalize(op: str) -> str:
        """Word operators are matched case-insensitively by the ST tokenizer
        but keyed uppercase in the model, so "mod" and "MOD" must land on the
        same entry. Symbol operators are returned unchanged."""
        return op.upper() if op.isalpha() else op

    def priced_operators(self, operators) -> list[str]:
        """Only the operators this model has a measured tier cost for."""
        return [
            self._normalize(op) for op in operators
            if self._normalize(op) in self.operator_tier_costs
        ]

    def operator_premium_above_tier1(self, operator: str) -> int:
        """This operator's tier cost above the cheapest (tier-1) one.

        The single number ST needs from this table: a multiplicative operator
        costs 16 bytes more than an additive one in an ST assignment, and 16 is
        exactly this table's tier-1-to-tier-2 step (36 -> 52), measured
        independently on ladder CPT and on the 6-file stx_opkind_* sweep. An
        operator the table does not price (AND, OR, XOR) pays no premium, which
        stx_opkind_and and stx_opkind_xor measured directly at the tier-1 rate.
        """
        costs = self.operator_tier_costs
        if not costs:
            return 0
        tier1 = min(costs.values())
        return max(0, costs.get(operator.upper(), tier1) - tier1)

    def unpriced_operators(self, operators) -> list[str]:
        """Operators the ST/RLL tokenizer recognises but this model has never
        measured a cost for: AND, OR and XOR.

        These used to raise KeyError straight out of cost_for, which aborted
        the whole report and made the UI fail to load the file at all (real
        traceback on an ST assignment containing AND). A missing
        measurement is a coverage gap, not a crash: the expression is charged
        for the operators that ARE measured and the rest are reported, the
        same discipline every other unpriced construct in this engine follows.
        """
        seen, out = set(), []
        for op in operators:
            n = self._normalize(op)
            if n not in self.operator_tier_costs and n not in seen:
                seen.add(n)
                out.append(n)
        return out

    def cost_for(self, operators: list[str]) -> int:
        """Real per-call CPT cost from its expression's operator tokens
        (OQ-CMPCPTLAYOUT, wired) -- see memory_model.yaml
        cpt_expression for the full derivation. A UNIFORM expression (every
        operator the same tier -- covers plain chains like A+B+C+D, the
        dominant real usage pattern) is exact: confirmed 0 residual across
        the n=1 operand-count sweep (1-10 operands) AND the n=1000
        chain-length sweep (3/4/5/6/8/10 operands), independently.

        A MIXED expression using EXACTLY the ADD/SUB and MUL/DIV/MOD tiers
        together (no POW) is ALSO exact now: `two_tier_mix_base
        + two_tier_mix_per_operator * operator_count`, confirmed at 4 of 5
        real operand-count points (3/5/11/15 operands exact, 8 operands off
        by the same small universal noise seen throughout this project) --
        order/arrangement doesn't matter (alternating vs grouped tiers give
        the same result).

        A MIXED expression using POW alongside EXACTLY ONE other tier (T1T3
        or T2T3) is ALSO exact now: `pow_tier_mix_base +
        pow_tier_mix_per_operator * operator_count`, wired from real capture
        data that already existed in manifest.csv but had never
        been reconciled into a formula. T1T3 and T2T3 give IDENTICAL real
        bytes at every one of 5 tested operator counts (2/4/7/10/14) --
        once POW is present, the OTHER tier (T1 vs T2) makes no measurable
        difference, so one formula covers both pairs. 4 of 5 points exact
        (k=2,4,10,14), k=7 off by the same +16 this project's other CPT
        formulas also miss by at that specific operator count -- a
        file-specific quirk, not a per-formula one. See memory_model.yaml
        cpt_expression for the full derivation.

        A mix using ALL 3 tiers together (ADD/SUB + MUL/DIV/MOD + POW) is
        ALSO exact now (OQ-CMPCPTLAYOUT closeout): a real
        correction on top of the plain per-operator-tier sum,
        `three_tier_mix_base_by_remainder[operator_count % 3] +
        three_tier_mix_per_pow_operand * pow_operand_count`. Confirmed 0
        residual across all 9 real all-3-tier data points spanning
        operator counts 4-14 (the original n=3/5/8/10/11/15 sweep plus 3
        new remainder-2 probes at n=6/9/12) -- see memory_model.yaml
        cpt_expression for the full derivation. `operator_count % 3`
        determines the class deterministically from the [+,*,**]-cycling
        construction any real alternating 3-tier expression follows: which
        of the 3 tiers ends up with one extra operator. remainder=0
        (T1==T2==T3) rests on a single real point (n=10) -- same slope as
        the other two remainder classes (independently confirmed at 3 and
        4 points each), just one point short of independent confirmation
        for its own base constant.
        """
        if not operators:
            return self.base_read
        operators = self.priced_operators(operators)
        if not operators:
            # Every operator in the expression is one this project has never
            # measured (see unpriced_operators). Charging a tier for them
            # would be inventing a constant, so only the read cost stands and
            # the caller reports the expression as unpriced.
            return self.base_read
        tiers = [self.operator_tier_costs[op] for op in operators]
        if len(set(tiers)) == 1:
            extra = self.per_extra_same_tier_by_tier_cost.get(
                tiers[0], self.per_extra_same_tier_operand)
            return self.base_read + tiers[0] + extra * (len(operators) - 1)
        add_tier = self.operator_tier_costs["+"]
        mul_tier = self.operator_tier_costs["*"]
        pow_tier = self.operator_tier_costs["**"]
        if set(tiers) == {add_tier, mul_tier}:
            # REFIT . The old form charged the same
            # two_tier_mix_per_operator regardless of WHICH tier each
            # operator was, so it could only be right where the two tiers
            # happened to balance -- 15 of 23 real points, and it missed
            # every unbalanced one by 4 or 8.
            #
            # Splitting the rate by tier fixes that and, more importantly,
            # cross-validates against data it was not fitted on. The
            # single-operator captures say a MUL/DIV costs exactly 16 more
            # than an ADD/SUB (140 vs 124); fitting these multi-operator
            # mixes independently returns per_tier2 - per_tier1 = 40 - 24 =
            # 16, the same number. And the resulting form collapses onto
            # the uniform-tier path exactly: 100 + 24n reproduces the whole
            # pure-ADD chain (124/148/172/196/220/268/316 at n=1..9), which
            # is the branch above computing it a different way.
            #
            # 19 of 23 exact. The four that remain are all -4 and all
            # unexplained: three (2,1) files (two of which,
            # cptcx_operatormix_mixedops and _nested, are the SAME operator
            # multiset arranged differently and agree with each other), and
            # cptmix_scaling_grouped_n05, whose (2,2) counts match
            # cptmix_scaling_alternating_n05 exactly yet costs 4 more.
            # Arrangement therefore matters somewhere, but not consistently
            # -- at n=11 the same alternating/grouped pair is identical. Not
            # patched with an invented rule; see OQ-CPTARRANGE.
            n_tier1 = sum(1 for t in tiers if t == add_tier)
            n_tier2 = sum(1 for t in tiers if t == mul_tier)
            return (
                self.two_tier_mix_base
                + self.two_tier_mix_per_tier1 * n_tier1
                + self.two_tier_mix_per_tier2 * n_tier2
                + self.leading_tier1_run_extra(tiers, add_tier)
            )
        if set(tiers) in ({add_tier, pow_tier}, {mul_tier, pow_tier}):
            return self.pow_tier_mix_base + self.pow_tier_mix_per_operator * len(operators)
        pow_operand_count = tiers.count(pow_tier)
        remainder = len(operators) % 3
        correction = self.three_tier_mix_base_by_remainder[remainder] + \
            self.three_tier_mix_per_pow_operand * pow_operand_count
        return self.base_read + sum(tiers) + correction


@dataclass(frozen=True)
class OperandTypeSurchargeModel:
    confidence: str
    surcharges: dict[str, dict[str, int]]  # instruction -> {atomic_type: extra bytes/call}
    # OQ-MIXEDTYPE: a call whose operands mix DINT with REAL, or DINT with INT.
    # See memory_model.yaml operand_type_surcharge.mixed.
    mixed: dict = field(default_factory=dict)

    def surcharge_for(self, mnemonic: str, atomic_type: str) -> int:
        return self.surcharges.get(mnemonic, {}).get(atomic_type, 0)

    def mixed_surcharge_for(self, mnemonic: str, types: list[str | None],
                            dest_index: int | None) -> int | None:
        """Surcharge for a call mixing DINT with REAL or with INT; None when
        the mix is not one that has been measured (the caller then falls back
        to the first resolvable operand, as before)."""
        known = {t for t in types if t}
        if not self.mixed or len(known) != 2 or "DINT" not in known:
            return None
        other = (known - {"DINT"}).pop()
        is_dest = [i == dest_index for i in range(len(types))]
        if other == "REAL":
            total = self.surcharge_for(mnemonic, "REAL")
            for t, dest in zip(types, is_dest):
                if t == "DINT" and not dest:
                    total += self.mixed["real_dint_source"]
                elif t == "DINT" and dest:
                    total += (self.mixed["real_dint_dest_mov"] if mnemonic == "MOV"
                              else self.mixed["real_dint_dest"])
            return total
        if other == "INT":
            total = sum(self.mixed["int_operand"] for t in types if t == "INT")
            if any(t == "INT" and not dest for t, dest in zip(types, is_dest)):
                total += self.mixed["int_source"]
            return total
        return None


@dataclass(frozen=True)
class IndirectIndexModel:
    confidence: str
    tag_index_cost: int
    tag_offset_index_cost: int
    # OQ-INDIRECTUDT: extra cost by what the indexed element is. See
    # memory_model.yaml indirect_index.
    member_access_cost: int = 0
    bool_element_cost: int = 0
    string_element_cost: int = 0

    def element_cost_for(self, follows: str, element_type: str | None) -> int:
        """On top of cost_for(kind): a member after the index, or an indexed
        BOOL / STRING element. A bit after the index is unmeasured (0)."""
        if follows == "member":
            return self.member_access_cost
        if follows:
            return 0
        if element_type == "BOOL":
            return self.bool_element_cost
        if element_type == "STRING":
            return self.string_element_cost
        return 0

    def cost_for(self, kind: str) -> int:
        if kind == "tag":
            return self.tag_index_cost
        if kind == "tag_offset":
            return self.tag_offset_index_cost
        return 0


@dataclass(frozen=True)
class CmpSurchargeModel:
    compound_confidence: str
    compound_cost: int
    float_literal_confidence: str
    float_literal_cost: int


@dataclass(frozen=True)
class TaskProgramOverheadModel:
    routine_extra: int
    program_extra: int
    task_extra: int
    confidence: str


@dataclass(frozen=True)
class JsrParamCostModel:
    """Real per-param JSR cost (OQ-JSRPARAMCOST, wired):
    `delta(n,R) = A(n) + B(n)*R`, `A(n) = a_base + a_per_param*n` (a
    one-time cost of the callee's own Parameters-block declaration, paid
    once per distinct target routine regardless of call-site count) and
    `B(n) = b_base + b_per_param*n` (the true per-call-site marginal
    rate). Confirmed exact at 3 real (n,B) points (n=5,8,10) -- see
    memory_model.yaml jsr_param_cost for the derivation. output_param_cost
    (wired): the per-call cost of each trailing RETURN-value
    argument a JSR passes back, charged once per output arg per call site
    -- a real, previously completely unmodeled cost (see
    memory_model.yaml jsr_param_cost for the 2-file derivation)."""
    a_base: int
    a_per_param: int
    b_base: int
    b_per_param: int
    confidence: str
    output_param_cost: int
    b_multiparam_extra: int = 0
    b_multiparam_threshold: int = 2
    # A structure or STRING argument is copied like COP, not like MOV: it costs
    # structured_arg_call_extra more per call and structured_arg_target_extra
    # more once on the target. See memory_model.yaml jsr_param_cost.
    structured_arg_call_extra: int = 0
    structured_arg_target_extra: int = 0
    structured_ret_call_extra: int = 0
    # RET instructions that return values, on the target: each costs
    # ret_instr_bytes + ret_operand_bytes per value, less ret_target_offset
    # once per target (floored at zero). See memory_model.yaml jsr_param_cost.
    ret_instr_bytes: int = 0
    ret_operand_bytes: int = 0
    ret_target_offset: int = 0

    def ret_cost(self, operand_counts) -> int:
        if not operand_counts:
            return 0
        raw = (self.ret_instr_bytes * len(operand_counts)
               + self.ret_operand_bytes * sum(operand_counts) - self.ret_target_offset)
        return max(raw, 0)

    def a_cost(self, n: int) -> int:
        return self.a_base + self.a_per_param * n

    def b_cost(self, n: int, m_out: int = 0) -> int:
        """Per-call-site cost of a JSR passing n input and m_out output params.

        The `b_multiparam_extra` step is measured, not fitted -- see
        memory_model.yaml jsr_param_cost. It is keyed on the TOTAL operand
        count, inputs plus outputs, not on the input count alone: a call
        passing 1 input and 2 outputs pays it and a call passing 1 input and
        nothing back does not."""
        total_operands = n + m_out
        extra = (self.b_multiparam_extra
                 if total_operands >= self.b_multiparam_threshold else 0)
        return self.b_base + self.b_per_param * n + extra


@dataclass(frozen=True)
class LogicInstructionModel:
    fixed_base_per_routine: int
    jsr_fixed_base_per_routine: int
    confidence: str
    weights: dict[str, int]
    cpt_expression: CptExpressionModel
    operand_type_surcharge: OperandTypeSurchargeModel
    indirect_index: IndirectIndexModel
    cmp_surcharge: CmpSurchargeModel
    task_program_overhead: TaskProgramOverheadModel
    jsr_param_cost: JsrParamCostModel
    branch_bracket_cost_per_instruction: int
    branch_bracket_confidence: str
    aoi_logic_composite_surcharge_per_instr: int
    jsr_target_composite_surcharge_per_instr: int
    composite_surcharge_confidence: str
    composite_surcharge_cap: int
    safety_task_program_shell: int
    safety_task_program_shell_confidence: str
    # The per-routine shell base on its own, separate from `confidence`, which
    # describes the instruction weights. Measured exact: the empty-project
    # baseline and the subrtn_shell / taskoverhead controls.
    fixed_base_per_routine_confidence: str = "FITTED"
    aoi_internal_per_rung: int = 0
    aoi_internal_per_rung_confidence: str = "FITTED"
    # Extra cost of an AOI-internal instruction that writes a non-BOOL
    # destination, over and above the per-instruction weight it would carry in
    # an ordinary Program routine. Supersedes aoi_internal_per_rung above, which
    # was the same number on the wrong carrier. See memory_model.yaml
    # aoi_internal_per_word_destination for the five families behind it.
    aoi_internal_per_word_destination: int = 0
    # OQ-SERIESOUTPUT: bytes REMOVED per writing instruction beyond the first in
    # a rung. Positive value, subtracted. See memory_model.yaml series_output.
    series_output_extra_discount: int = 0
    aoi_internal_per_word_destination_confidence: str = "KNOWN"
    # Cost of one AOI call site: a base plus a rate per parameter passed (the
    # instance tag is not a parameter) -- see memory_model.yaml aoi_call_site.
    aoi_call_site_bytes: int = 0
    aoi_call_site_per_param_bytes: int = 0
    aoi_call_site_input_ref_extra_bytes: int = 0


@dataclass(frozen=True)
class ProcessorFirmwareCorrectionModel:
    """Per-processor-family firmware correction on top of the single global
    firmware ladder (OQ-BASELINE-PROCFW).

    The 72 active-platform `fwmatrix_*` captures each hold one processor at one
    firmware with NO content, so their residual is the baseline error by
    definition. Read that way, each processor's residual is constant within a
    firmware band and the bands differ by family -- which one global ladder
    cannot express, and which is why 72 files sat at -48/-32/-8/+8/+16.

    Patterns are tried IN ORDER and the first match wins. That ordering is
    load-bearing rather than cosmetic: "5069-L3100ERM" also starts with
    "5069-L310", so the L3100 pattern has to precede the L306/L310/L320 one or
    it is silently swallowed."""
    by_processor_pattern: tuple[tuple[str, dict[str, int]], ...]
    confidence: str

    def correction_for(self, processor_type: str | None,
                       software_revision: str | None) -> tuple[int, str]:
        if not processor_type or not software_revision:
            return 0, self.confidence
        major = software_revision.split(".")[0]
        for pattern, by_major in self.by_processor_pattern:
            if re.search(pattern, processor_type):
                return by_major.get(major, 0), self.confidence
        return 0, self.confidence


@dataclass(frozen=True)
class FirmwareBaselineDeltaModel:
    """Real per-firmware-major-version delta over the confirmed v34/v35
    baseline (OQ-BASELINE-PROCFW, wired) -- see memory_model.yaml
    firmware_baseline_delta for the full derivation and which manifest.csv
    rows it's fitted from. Keyed by the integer major version parsed out of
    the L5X root's own SoftwareRevision attribute (e.g. "31.02" -> "31");
    any major not in the table (including v34/v35 themselves, and any
    firmware with no real sample) falls back to default_bytes/
    default_confidence -- i.e. no adjustment."""
    by_major_version: dict[str, tuple[int, str]]
    default_bytes: int
    default_confidence: str

    def delta_for(self, software_revision: str | None) -> tuple[int, str]:
        if not software_revision:
            return self.default_bytes, self.default_confidence
        major = software_revision.split(".")[0]
        return self.by_major_version.get(major, (self.default_bytes, self.default_confidence))


@dataclass(frozen=True)
class SafetyCapableBaselineDeltaModel:
    """Real 5069 safety-CAPABLE processor baseline overhead, independent of
    actual SafetyInfo/SafetyTask content (OQ-BASELINE-PROCFW, wired) --
    see memory_model.yaml safety_capable_baseline_delta for
    the full derivation (n=2 real catalogs, extended to the whole
    safety-suffix family the same way this project already extends L71's
    confirmed shape to L72-L75). catalog_suffix_pattern is matched against
    the L5X Controller element's own ProcessorType attribute."""
    bytes: int
    confidence: str
    catalog_suffix_pattern: str

    def applies_to(self, processor_type: str | None) -> bool:
        if not processor_type:
            return False
        return bool(re.search(self.catalog_suffix_pattern, processor_type))


@dataclass(frozen=True)
class ModuleConnectionDataModel:
    """A module connection's data costs a multiple of its declared bytes.

    Derived for the generic ETHERNET-MODULE profile, which is 25% of every
    non-CPU module in the sixteen real programs -- see memory_model.yaml
    module_connection_data for the 14-point derivation and for why it is scoped
    to that profile rather than applied to every module.
    """

    word_bytes: int
    bytes_per_word: int
    odd_word_discount: int
    catalogs: frozenset[str]
    confidence: str

    def applies_to(self, catalog: str) -> bool:
        return catalog in self.catalogs

    def bytes_for(self, input_bytes: int, output_bytes: int) -> int:
        """16 per 4-byte word summed over both directions, less 8 if odd.

        Each direction is rounded up to its own word before summing -- an
        8-byte input and an 8-byte output are 4 words, not one 16-byte block --
        and only the SUM matters: genem_in032 and genem_out032 are byte-identical
        captures, as are genem_in064 and genem_out064.
        """
        if self.word_bytes <= 0:
            return input_bytes + output_bytes
        words = (-(-input_bytes // self.word_bytes)
                 + -(-output_bytes // self.word_bytes))
        return self.bytes_per_word * words - self.odd_word_discount * (words % 2)


@dataclass(frozen=True)
class ModuleOverheadModel:
    """Real per-catalog module overhead (OQ-MODULEIO, wired) --
    see memory_model.yaml module_overhead_by_catalog for the full
    derivation and which catalogs were deliberately left off (adapter/
    bridge catalogs that may be absorbing a rack of aliased children,
    generic-catalog placeholders whose overhead scales with declared I/O
    size, and a few real connection-variant-dependent cases). Any catalog
    not in the table falls back to the flat default_bytes/
    default_confidence -- the same flat FITTED-from-2-points estimate this
    project used everywhere before this table existed."""
    by_catalog: dict[str, tuple[int, str]]
    default_bytes: int
    default_confidence: str
    # Overhead for the SECOND and later modules of the same catalog in one
    # project, where it has been measured. See memory_model.yaml
    # module_overhead_by_catalog for the 16-catalog table and why this has to be
    # a second per-catalog number rather than a constant or a ratio.
    repeat_by_catalog: dict[str, int] = field(default_factory=dict)
    # What the "same project" in the line above actually means. "project"
    # counts every module of a catalog in the file against one running total;
    # "parent" restarts the count under each parent module, i.e. the shared
    # thing is shared per rack rather than per controller. The captured
    # single-catalog and mixture sweeps cannot tell these apart -- every copy
    # in them sits under Local -- so the choice is a real open question, not a
    # formatting detail. See memory_model.yaml
    # module_overhead_repeat_discount.
    repeat_scope: str = "project"
    # Catalog FAMILIES that share one repeat count: (regex, discount). A module
    # whose catalog matches counts its occurrence against the family, not its
    # own catalog, and a later occurrence with no measured repeat_bytes pays
    # its first-copy rate less the family discount. See memory_model.yaml
    # module_family_repeat.
    family_repeat: tuple[tuple[str, int], ...] = ()
    # First-copy overhead for an UNSEEN catalog of a family, instead of the
    # flat cross-catalog default: pattern -> bytes. See module_family_repeat.
    family_first_bytes: dict[str, int] = field(default_factory=dict)

    def _family(self, catalog: str) -> tuple[str, int] | None:
        for pattern, discount in self.family_repeat:
            if re.match(pattern, catalog):
                return pattern, discount
        return None

    def occurrence_key(self, catalog_number: str | None,
                       parent_module: str = "") -> tuple[str, str]:
        """What report.py counts occurrences against, per `repeat_scope`."""
        catalog = catalog_number or ""
        family = self._family(catalog)
        key = family[0] if family else catalog
        return (key, parent_module if self.repeat_scope == "parent" else "")

    def overhead_for(self, catalog_number: str | None,
                     occurrence: int = 1) -> tuple[int, str]:
        """`occurrence` is 1 for the first module of this catalog in the file,
        2 for the second, and so on. A catalog with no measured repeat rate
        keeps paying the first-instance rate every time -- the old behaviour,
        and the safe direction, since it over-predicts rather than under."""
        if not catalog_number:
            return self.default_bytes, self.default_confidence
        family = self._family(catalog_number)
        fallback = (self.default_bytes, self.default_confidence)
        if family and family[0] in self.family_first_bytes:
            fallback = (self.family_first_bytes[family[0]], "ASSUMED")
        first, confidence = self.by_catalog.get(catalog_number, fallback)
        if occurrence > 1 and catalog_number in self.repeat_by_catalog:
            return self.repeat_by_catalog[catalog_number], confidence
        if occurrence > 1 and family:
            return first - family[1], confidence
        return first, confidence

    def has_real_data_for(self, catalog_number: str | None) -> bool:
        """True if this SPECIFIC catalog has its own real capture point here,
        as opposed to falling back to the flat cross-catalog default. Lets
        report.py's rack-aliased/legacy-network exclusion (real data
        confirms module_overhead does NOT apply the same way to those
        shapes in general) still charge a catalog that DOES have its own
        confirmed real value despite being one of those shapes -- see
        memory_model.yaml's comment for the derivation."""
        return bool(catalog_number) and catalog_number in self.by_catalog


@dataclass(frozen=True)
class CatalogBaselineDeltaModel:
    """Real per-catalog baseline delta for processor families whose real
    empty-project baseline diverges enormously from the flat
    empty_project_baseline (OQ-BASELINE-PROCFW, 1769-series thread,
    wired) -- see memory_model.yaml catalog_baseline_delta for the
    full derivation. Exact ProcessorType string match only, deliberately
    NOT prefix/suffix-pattern-matched like safety_capable_baseline_delta
    -- real data shows a single expansion-module suffix character (e.g.
    `-QB1B` vs `-QBFC1B`) changes the real value by over 13,000 bytes, so
    extrapolating beyond an exact confirmed catalog string would be a
    guess, not a real value."""
    by_processor_type: dict[str, tuple[int, str]]
    # Catalogs whose real baseline is an ABSOLUTE floor rather than a delta
    # on top of the firmware ladder (the 1756-L7x thread). An
    # additive delta cannot express "this family ignores the firmware
    # ladder": the L7x actual is a flat 30,152 across v31/v32/v34/v35/v38
    # while the L8x baseline underneath it moves 29,368 -> 32,376 -> 18,128,
    # so any single delta is right for one firmware and wrong for the rest.
    # Wiring it as a delta first got 15 of 30 files exact and left the other
    # 15 off by the firmware ladder's own movement -- which is the
    # experiment that showed the shape was wrong.
    absolute_by_processor_type: dict[str, tuple[int, str]]

    def delta_for(self, processor_type: str | None) -> tuple[int, str] | None:
        if not processor_type:
            return None
        return self.by_processor_type.get(processor_type)

    def absolute_for(self, processor_type: str | None) -> tuple[int, str] | None:
        """The catalog's absolute empty-project baseline, if it has one.

        The caller is responsible for turning this into a correcting delta
        against whatever the flat baseline + firmware/safety deltas already
        produced, so the report still shows one auditable adjustment line
        rather than silently rewriting an earlier entry."""
        if not processor_type:
            return None
        return self.absolute_by_processor_type.get(processor_type)


@dataclass(frozen=True)
class AlarmConditionModel:
    """Exact cost of tag-based alarm conditions -- see memory_model.yaml
    alarm_conditions and sizing/alarms.py. Reproduces all 37 captured
    alarmcond_* points with zero residual."""

    file_base: int
    per_condition: int
    per_associated_tag_by_type: dict[str, int]
    associated_tag_default: int
    confidence: str

    def assoc_tag_cost(self, resolved_type: str | None) -> int:
        """An unresolved reference is charged the STRING rate -- the most
        expensive -- so a partial export over-states rather than silently
        under-states."""
        if resolved_type is None:
            return self.associated_tag_default
        return self.per_associated_tag_by_type.get(resolved_type, self.associated_tag_default)


@dataclass(frozen=True)
class StructuredTextModel:
    """Cost of Structured Text routines -- see memory_model.yaml
    structured_text and sizing/structured_text.py.

    The headline result, and the reason this is a thin model rather than a
    parallel weight table: ST costs EXACTLY what RLL costs for the same
    instruction, plus one flat per-routine shell. Four ST/RLL pairs built
    to be operand-for-operand identical came back separated by exactly
    +432 every time, with no other term:

        st_instr_cop_n01000    135,376  vs  instr_cop_n01000   134,944
        st_instr_dtos_n01000    95,376  vs  instr_dtos_n01000   94,944
        st_instr_size_n01000   151,376  vs  instr_size_n01000  150,944
        st_expr_cpt_mirror_n01000 475,376 vs instr_cpt_n01000  474,944

    So the whole per-instruction weight table, and the tier-aware CPT
    expression model, transfer to ST unchanged. What ST adds on top is a
    per-statement cost and per-construct control-flow costs, all measured
    against a common 100-statement control.
    """

    per_statement: int
    per_statement_literal_rhs: int
    routine_shell: int
    if_block: int
    elsif_branch: int
    case_block: int
    for_block: int
    while_block: int
    comments_and_blanks: int
    confidence: str
    # ST assignment cost, one law -- see memory_model.yaml structured_text for
    # the 30-file derivation and for why the five-entry count-keyed table it
    # replaces was wrong rather than merely sparse.
    assignment_low_operator_bytes: dict[str, dict[int, int]]
    assignment_two_operator_bytes: dict[str, int]
    assignment_per_operator_bytes: dict[str, int]
    real_dest_integer_source_bytes: int
    assignment_expression_confidence: str
    # An AOI called as a bare statement from ST -- charged nothing until
    # and 2,094 of the real corpus's 6,586 ST lines are these.
    st_aoi_call_bytes: int = 0
    st_aoi_call_per_param_bytes: int = 0
    st_aoi_call_confidence: str = "FITTED"
    # ST's OWN operator classification, measured -- it is not the CPT
    # tier table. See memory_model.yaml structured_text for the 21-file
    # derivation and for the three places the two tables disagree.
    assignment_one_operator_class_bytes: dict[str, dict[str, int]] = field(
        default_factory=dict)
    assignment_operator_premium: dict[str, dict[str, int]] = field(
        default_factory=dict)
    # Per named source read into a REAL destination, keyed on the SOURCE's own
    # declared type. stc_conv_mixed confirms the additivity to the byte.
    real_dest_source_conversion_bytes: dict[str, int] = field(default_factory=dict)
    st_aoi_call_routine_bytes: int = 0

    _OPERATOR_CLASSES = {
        "+": "additive", "-": "additive",
        "*": "multiplicative", "/": "multiplicative", "MOD": "multiplicative",
        "AND": "bitwise", "OR": "bitwise", "XOR": "bitwise", "NOT": "bitwise",
        "**": "exponent",
    }

    @classmethod
    def operator_class(cls, operator: str) -> str:
        """Which of the four measured ST operator classes this operator is in.

        An operator nobody has classified reads as additive, the cheapest class,
        so an unknown token cannot silently inflate a prediction.
        """
        return cls._OPERATOR_CLASSES.get(operator.strip().upper(), "additive")

    def conversion_bytes_for(self, source_type: str) -> int:
        """Implicit-conversion cost of reading one source of this type into a
        REAL destination. Unmeasured types fall back to DINT's rate."""
        table = self.real_dest_source_conversion_bytes
        if not table:
            return self.real_dest_integer_source_bytes
        return table.get((source_type or "").upper(),
                         self.real_dest_integer_source_bytes)

    def assignment_cost(self, operators, dest_is_real: bool,
                        conversion_bytes: int = 0,
                        all_float_operands: bool = False) -> int:
        """Bytes for one ST assignment.

        `operators` is the statement's operator tokens in order. At exactly one
        operator the cost is a LOOKUP keyed on that operator's class -- a
        bitwise operator costs 124 where an additive one costs 40, and no
        premium applies. At two or more it is base-plus-rate with a per-operator
        premium, and a bitwise operator's premium is zero. Both halves are
        measured; see memory_model.yaml.

        `conversion_bytes` is the summed implicit-conversion cost of the named
        sources, already keyed per source type by conversion_bytes_for; integer
        LITERALS do not pay it.

        `all_float_operands` selects the premium table, and it is the OPERANDS
        that decide it rather than the destination. stc_premreal_mul (REAL
        destination, REAL sources only) pays no multiplicative premium, while
        st_expr_cpt_mirror_n01000 -- also a REAL destination, but multiplying a
        DINT subexpression by a REAL and dividing a REAL by the literal 2 -- pays
        16 per multiplicative operator. Both are byte-exact only if the premium
        follows the operands. The base still follows the destination.
        """
        kind = "real" if dest_is_real else "dint"
        premium_kind = "real" if all_float_operands else "dint"
        n_operators = len(operators)
        premium = 0
        if n_operators == 1 and self.assignment_one_operator_class_bytes:
            table = self.assignment_one_operator_class_bytes.get(kind, {})
            base = table.get(self.operator_class(operators[0]),
                             table.get("additive",
                                       self.assignment_low_operator_bytes[kind][1]))
        elif n_operators in self.assignment_low_operator_bytes[kind]:
            base = self.assignment_low_operator_bytes[kind][n_operators]
        else:
            base = (self.assignment_two_operator_bytes[kind]
                    + self.assignment_per_operator_bytes[kind] * (n_operators - 2))
            rates = self.assignment_operator_premium.get(premium_kind, {})
            premium = sum(rates.get(self.operator_class(op), 0) for op in operators)
        return base + premium + (conversion_bytes if dest_is_real else 0)

    def unmeasured_one_operator_class(self, operators, dest_is_real: bool) -> str:
        """The class key this statement used that has no measurement, or "".

        Only the additive class is measured on the REAL row at one operator, so a
        `R0 := R1 * R2;` is a real coverage gap rather than a priced shape.
        """
        if len(operators) != 1 or not self.assignment_one_operator_class_bytes:
            return ""
        kind = "real" if dest_is_real else "dint"
        cls = self.operator_class(operators[0])
        if cls in self.assignment_one_operator_class_bytes.get(kind, {}):
            return ""
        return f"1 operator|{kind}|{cls}"

    def st_aoi_call_cost(self, calls: int, params: int) -> int:
        """Per-call cost, plus the one-time a routine with any AOI call pays."""
        if not calls:
            return 0
        return (self.st_aoi_call_bytes * calls
                + self.st_aoi_call_per_param_bytes * params
                + self.st_aoi_call_routine_bytes)


@dataclass(frozen=True)
class IdentifierNameLengthModel:
    """Cost of an identifier's own NAME (OQ-IDENTNAMELEN).

    Shared by every identifier class measured for it -- Program names, JSR
    target routine names, and ordinary routine names.

    It is a STEP, not a ramp: 8 bytes per whole 8 characters, i.e.
    `bucket_bytes * (len // bucket_chars)`. Same form the project already uses
    for tag, UDT and AOI-definition names, so there is now ONE name law rather
    than two.

    Corrected by the `identnamelen_*` sweep, which is the file set
    that measures the interval the earlier three-regime fit had to interpolate
    across. That fit was anchored at 1, 4, 8, 16, 32 and 40 characters and this
    law agrees with it at every one of those anchors -- the disagreement is only
    where it was guessing:

        len   old (ramp)   measured (step)
          1            0                 0
          4            0                 0
          5            2                 0
          6            4                 0
          7            6                 0
          8            8                 8
          9            9                 8
         12           12                 8
         16           16                16
         32           32                32
         40           40                40

    `identnamelen_prog_c{01..12}` holds 10 Programs at each length and reads
    25,688 bytes flat for lengths 1 through 7, then 25,768 flat for 8 through
    12 -- one 80-byte step across 10 programs, landing exactly on 8 per program.
    `identnamelen_rtn_c{01,04,08,12,16,32,40}` holds 10 routines and reads
    0/0/80/80/160/320/400 over the same baseline. Two independent arms, one
    per-identifier rate, 12 of 12 points exact.
    """

    bucket_bytes: int
    bucket_chars: int
    confidence: str
    task_min_bytes: int = 0

    def bytes_for(self, name: str) -> int:
        if self.bucket_chars <= 0:
            return 0
        return self.bucket_bytes * (len(name or "") // self.bucket_chars)

    def bytes_for_task(self, name: str) -> int:
        """A TASK name never costs zero, unlike a program's or a routine's.

        identnamelen_task_c{04,08,16,32,40} (5 extra Periodic tasks per file)
        reads 40 / 40 / 80 / 160 / 200, so 8 / 8 / 16 / 32 / 40 per task. The
        plain floor law gives 0 at length 4, which is the one length that
        disagrees -- and 40 is five times 8, not the corpus's +/-8 per-file
        noise. Program and routine names are floor beyond doubt
        (identnamelen_prog_c01..c07 all cost exactly 0), so this minimum is
        specific to tasks.

        8 * ceil(len/8) fits the same five points identically and differs only
        for a name of 9..15 or 17..23 characters, which no captured task name
        has. Not distinguishable yet -- see OQ-IDENTNAMELEN.
        """
        if self.bucket_chars <= 0:
            return 0
        return max(self.task_min_bytes, self.bytes_for(name))


@dataclass(frozen=True)
class JsrTargetDeclarationModel:
    """Cost of DECLARING a distinct JSR target, over and above its params.

    See memory_model.yaml jsr_target_declaration. Charged once per distinct
    target, never per call -- the residual across the captured JSR corpus
    correlates +0.883 with distinct-target count and -0.445 with call
    count."""

    per_target: int
    per_name_char: int
    confidence: str
    # A target whose SBR/RET carry OPERANDS costs this much more, once, on top
    # of everything else. A parameterless SBR()/RET() pair costs nothing -- see
    # memory_model.yaml jsr_target_declaration.
    sbr_ret_operand_bytes: int = 0

    def cost_for(self, routine_name: str, name_length: "IdentifierNameLengthModel",
                 sbr_ret_operands: int = 0) -> int:
        """per_name_char is not applied directly any more -- the shared
        identifier-name law replaces it, which adds the sub-8-character floor
        the original straight-line fit had no data to see."""
        return (self.per_target + name_length.bytes_for(routine_name)
                + (self.sbr_ret_operand_bytes if sbr_ret_operands else 0))


@dataclass(frozen=True)
class PlatformFirmwareCorrectionModel:
    """Per-(catalog, firmware-major) baseline correction.

    The existing firmware_baseline_delta applies one ladder to every
    catalog; grouping the 190 captured baseline files by declared processor
    AND firmware shows the ladder is platform-specific. See
    memory_model.yaml platform_firmware_correction for the full matrix and
    for why catalogs are listed explicitly rather than prefix-matched
    (5069-L3100ERM would otherwise be captured by a "5069-L310" prefix and
    put in the wrong class)."""

    by_catalog: dict[str, dict[int, int]]
    confidence: str

    @staticmethod
    def _major(software_revision: str | None) -> int | None:
        if not software_revision:
            return None
        head = software_revision.split(".", 1)[0].strip()
        return int(head) if head.isdigit() else None

    def correction_for(
        self, processor_type: str | None, software_revision: str | None
    ) -> tuple[int, str] | None:
        """Correction bytes for this catalog at this firmware, or None.

        Returns None for an unlisted catalog or an unmeasured firmware
        rather than interpolating -- a firmware between two measured points
        is not evidence about the point in between, and this project has
        been bitten by exactly that assumption before (the 1756-L7x ladder,
        which does not track firmware at all)."""
        if not processor_type:
            return None
        table = self.by_catalog.get(processor_type)
        if table is None:
            return None
        major = self._major(software_revision)
        if major is None or major not in table:
            return None
        return table[major], self.confidence


@dataclass(frozen=True)
class MemoryModel:
    atomic_types: dict[str, AtomicType]
    predefined_structures: dict[str, AtomicType]
    predefined_array_structures: dict[str, PredefinedArrayStructure]
    bool: BoolModel
    string: StringModel
    string_array: StringArrayModel
    udt: UdtModel
    array: ArrayModel
    aoi_array: AoiArrayModel
    aoi_definition: AoiDefinitionModel
    tag_overhead: TagOverheadModel
    alias_overhead: TagOverheadModel
    udt_definition: UdtDefinitionModel
    logic_instructions: LogicInstructionModel
    jsr_target_declaration: JsrTargetDeclarationModel
    identifier_name_length: IdentifierNameLengthModel
    alarm_conditions: AlarmConditionModel
    structured_text: StructuredTextModel
    empty_project_baseline_bytes: int
    empty_project_baseline_confidence: str
    module_overhead_bytes: int
    module_overhead_confidence: str
    # Flat cost of a module with no connections and no stated size (a
    # bridge/adapter/gateway node). See memory_model.yaml
    # zero_connection_module -- a per-catalog table was tried and rejected
    # by cross-validation.
    zero_connection_module_bytes: int
    module_connection_data: ModuleConnectionDataModel
    zero_connection_module_confidence: str
    # Catalogs whose zero-connection cost was measured in isolation
    # (OQ-BRIDGEPH): catalog -> (bytes, confidence). Everything else keeps the
    # flat rate above.
    zero_connection_by_catalog: dict
    module_overhead_by_catalog: ModuleOverheadModel
    # OQ-DEFSCALE see memory_model.yaml definition_scale_correction.
    udt_definition_extra: int
    udt_tag_extra: int
    aoi_instance_extra: int
    aoi_definition_extra: int
    standalone_atomic_tag_slot_bytes: int
    standalone_atomic_tag_slot_confidence: str
    standalone_udt_tag_slot_alignment: int
    standalone_udt_tag_slot_confidence: str
    firmware_baseline_delta: FirmwareBaselineDeltaModel
    processor_firmware_correction: ProcessorFirmwareCorrectionModel
    safety_capable_baseline_delta: SafetyCapableBaselineDeltaModel
    catalog_baseline_delta: CatalogBaselineDeltaModel
    platform_firmware_correction: PlatformFirmwareCorrectionModel
    # OQ-POINTIOCONN: overhead for a module whose I/O is aliased into its
    # parent's Slot array, on top of its own declared data. See
    # memory_model.yaml rack_aliased_module.
    rack_aliased_module_bytes: int = 0
    rack_aliased_module_confidence: str = "FITTED"
    # Measured prediction accuracy per instruction, regenerated from captures
    # by scripts/derive_instruction_accuracy.py. Not a sizing constant -- it
    # is how well the sizing constants have been shown to WORK, and it is what
    # the UI reports as confidence instead of a provenance tier.
    instruction_accuracy: dict = field(default_factory=dict)


def load_memory_model(path: str | Path | None = None) -> MemoryModel:
    path = Path(path) if path else _DEFAULT_PATH
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    atomic_types = {
        name: AtomicType(bytes=v["bytes"], confidence=v["confidence"])
        for name, v in raw["atomic_types"].items()
    }
    predefined_structures = {
        name: AtomicType(bytes=v["bytes"], confidence=v["confidence"])
        for name, v in raw.get("predefined_structures", {}).items()
    }
    predefined_array_structures = {
        name: PredefinedArrayStructure(base=v["base"], per_element=v["per_element"], confidence=v["confidence"])
        for name, v in raw.get("predefined_array_structures", {}).items()
    }
    b = raw["bool"]
    s = raw["string"]
    baseline = raw["empty_project_baseline"]
    module_overhead = raw["module_overhead"]
    module_overhead_by_catalog = raw.get("module_overhead_by_catalog", {})
    fw_delta = raw["firmware_baseline_delta"]
    safety_delta = raw["safety_capable_baseline_delta"]
    catalog_delta = raw.get("catalog_baseline_delta", {})
    return MemoryModel(
        instruction_accuracy=raw.get("instruction_accuracy") or {},
        atomic_types=atomic_types,
        predefined_structures=predefined_structures,
        predefined_array_structures=predefined_array_structures,
        structured_text=StructuredTextModel(
            per_statement=raw["structured_text"]["per_statement"],
            per_statement_literal_rhs=raw["structured_text"]["per_statement_literal_rhs"],
            routine_shell=raw["structured_text"]["routine_shell"],
            if_block=raw["structured_text"]["if_block"],
            elsif_branch=raw["structured_text"]["elsif_branch"],
            case_block=raw["structured_text"]["case_block"],
            for_block=raw["structured_text"]["for_block"],
            while_block=raw["structured_text"]["while_block"],
            comments_and_blanks=raw["structured_text"]["comments_and_blanks"],
            assignment_low_operator_bytes={
                kind: {int(k): v for k, v in table.items()}
                for kind, table in
                raw["structured_text"]["assignment_low_operator_bytes"].items()
            },
            assignment_two_operator_bytes=dict(
                raw["structured_text"]["assignment_two_operator_bytes"]),
            assignment_per_operator_bytes=dict(
                raw["structured_text"]["assignment_per_operator_bytes"]),
            real_dest_integer_source_bytes=raw["structured_text"][
                "real_dest_integer_source_bytes"],
            assignment_expression_confidence=raw["structured_text"][
                "assignment_expression_confidence"],
            st_aoi_call_bytes=raw["structured_text"]["st_aoi_call_bytes"],
            st_aoi_call_per_param_bytes=raw["structured_text"][
                "st_aoi_call_per_param_bytes"],
            st_aoi_call_confidence=raw["structured_text"]["st_aoi_call_confidence"],
            st_aoi_call_routine_bytes=raw["structured_text"].get(
                "st_aoi_call_routine_bytes", 0),
            assignment_one_operator_class_bytes={
                kind: dict(table) for kind, table in
                raw["structured_text"].get(
                    "assignment_one_operator_class_bytes", {}).items()
            },
            assignment_operator_premium={
                kind: dict(table) for kind, table in
                raw["structured_text"].get("assignment_operator_premium", {}).items()
            },
            real_dest_source_conversion_bytes=dict(
                raw["structured_text"].get("real_dest_source_conversion_bytes", {})),
            confidence=raw["structured_text"]["confidence"],
        ),
        alarm_conditions=AlarmConditionModel(
            file_base=raw["alarm_conditions"]["file_base"],
            per_condition=raw["alarm_conditions"]["per_condition"],
            per_associated_tag_by_type=dict(raw["alarm_conditions"]["per_associated_tag_by_type"]),
            associated_tag_default=raw["alarm_conditions"]["associated_tag_default"],
            confidence=raw["alarm_conditions"]["confidence"],
        ),
        empty_project_baseline_bytes=baseline["bytes"],
        empty_project_baseline_confidence=baseline["confidence"],
        module_overhead_bytes=module_overhead["bytes"],
        platform_firmware_correction=PlatformFirmwareCorrectionModel(
            by_catalog={
                cat: {int(k): v for k, v in cls["by_firmware_major"].items()}
                for cls in raw.get("platform_firmware_correction", {}).get("classes", {}).values()
                for cat in cls["catalogs"]
            },
            confidence=raw.get("platform_firmware_correction", {}).get("confidence", "UNKNOWN"),
        ),
        identifier_name_length=IdentifierNameLengthModel(
            bucket_bytes=raw["identifier_name_length"]["bucket_bytes"],
            bucket_chars=raw["identifier_name_length"]["bucket_chars"],
            confidence=raw["identifier_name_length"]["confidence"],
            task_min_bytes=raw["identifier_name_length"].get("task_min_bytes", 0),
        ),
        jsr_target_declaration=JsrTargetDeclarationModel(
            per_target=raw.get("jsr_target_declaration", {}).get("per_target", 0),
            per_name_char=raw.get("jsr_target_declaration", {}).get("per_name_char", 0),
            confidence=raw.get("jsr_target_declaration", {}).get("confidence", "UNKNOWN"),
            sbr_ret_operand_bytes=raw.get("jsr_target_declaration", {}).get(
                "sbr_ret_operand_bytes", 0),
        ),
        zero_connection_module_bytes=raw.get("zero_connection_module", {}).get("bytes", 0),
        rack_aliased_module_bytes=raw.get("rack_aliased_module", {}).get("overhead_bytes", 0),
        rack_aliased_module_confidence=raw.get("rack_aliased_module", {}).get("confidence", "FITTED"),
        zero_connection_module_confidence=raw.get("zero_connection_module", {}).get("confidence", "UNKNOWN"),
        zero_connection_by_catalog={
            catalog: (entry["bytes"], entry["confidence"])
            for catalog, entry in (raw.get("zero_connection_module", {}).get("by_catalog") or {}).items()
        },
        module_overhead_confidence=module_overhead["confidence"],
        module_connection_data=ModuleConnectionDataModel(
            word_bytes=raw["module_connection_data"]["word_bytes"],
            bytes_per_word=raw["module_connection_data"]["bytes_per_word"],
            odd_word_discount=raw["module_connection_data"]["odd_word_discount"],
            catalogs=frozenset(raw["module_connection_data"]["catalogs"]),
            confidence=raw["module_connection_data"]["confidence"],
        ),
        module_overhead_by_catalog=ModuleOverheadModel(
            by_catalog={
                catalog: (v["bytes"], v["confidence"])
                for catalog, v in module_overhead_by_catalog.items()
            },
            default_bytes=module_overhead["bytes"],
            default_confidence=module_overhead["confidence"],
            # Gated off: measured exactly per catalog, but applying it
            # project-wide regressed every held-out real program. See
            # memory_model.yaml module_overhead_repeat_discount.
            repeat_by_catalog=(
                {
                    catalog: v["repeat_bytes"]
                    for catalog, v in module_overhead_by_catalog.items()
                    if "repeat_bytes" in v
                }
                if raw.get("module_overhead_repeat_discount", {}).get("apply_repeat_discount")
                else {}
            ),
            repeat_scope=raw.get("module_overhead_repeat_discount", {}).get(
                "repeat_scope", "project"),
            family_repeat=tuple(
                (f["pattern"], f["discount_bytes"])
                for f in raw.get("module_family_repeat", {}).get("families", [])
            ),
            family_first_bytes={
                f["pattern"]: f["unseen_first_bytes"]
                for f in raw.get("module_family_repeat", {}).get("families", [])
                if "unseen_first_bytes" in f
            },
        ),
        udt_definition_extra=raw.get("definition_scale_correction", {}).get("udt_definition_extra", 0),
        udt_tag_extra=raw.get("definition_scale_correction", {}).get("udt_tag_extra", 0),
        aoi_instance_extra=raw.get("definition_scale_correction", {}).get("aoi_instance_extra", 0),
        aoi_definition_extra=raw.get("definition_scale_correction", {}).get("aoi_definition_extra", 0),
        standalone_atomic_tag_slot_bytes=raw["standalone_atomic_tag_slot"]["bytes"],
        standalone_atomic_tag_slot_confidence=raw["standalone_atomic_tag_slot"]["confidence"],
        standalone_udt_tag_slot_alignment=raw["standalone_udt_tag_slot"]["alignment_bytes"],
        standalone_udt_tag_slot_confidence=raw["standalone_udt_tag_slot"]["confidence"],
        processor_firmware_correction=ProcessorFirmwareCorrectionModel(
            by_processor_pattern=tuple(
                (entry["pattern"], {str(k): int(v) for k, v in entry["by_major_version"].items()})
                for entry in raw["processor_firmware_correction"]["by_processor_pattern"]
            ),
            confidence=raw["processor_firmware_correction"]["confidence"],
        ),
        firmware_baseline_delta=FirmwareBaselineDeltaModel(
            by_major_version={
                major: (v["bytes"], v["confidence"])
                for major, v in fw_delta["by_major_version"].items()
            },
            default_bytes=fw_delta["default_bytes"],
            default_confidence=fw_delta["default_confidence"],
        ),
        safety_capable_baseline_delta=SafetyCapableBaselineDeltaModel(
            bytes=safety_delta["bytes"],
            confidence=safety_delta["confidence"],
            catalog_suffix_pattern=safety_delta["catalog_suffix_pattern"],
        ),
        catalog_baseline_delta=CatalogBaselineDeltaModel(
            by_processor_type={
                proc_type: (v["bytes"], v["confidence"])
                for proc_type, v in catalog_delta.items()
                if "bytes" in v
            },
            absolute_by_processor_type={
                proc_type: (v["absolute_bytes"], v["confidence"])
                for proc_type, v in catalog_delta.items()
                if "absolute_bytes" in v
            },
        ),
        bool=BoolModel(
            standalone_tag_bytes=b["standalone_tag_bytes"],
            standalone_confidence=b["standalone_confidence"],
            member_bits_per_backing_byte=b["member_bits_per_backing_byte"],
            member_backing_type=b["member_backing_type"],
            member_confidence=b["member_confidence"],
            array_bits_per_packed_word=b["array_bits_per_packed_word"],
            array_packed_word_bytes=b["array_packed_word_bytes"],
            array_confidence=b["array_confidence"],
        ),
        string=StringModel(
            len_field_bytes=s["len_field_bytes"],
            default_data_bytes=s["default_data_bytes"],
            confidence=s["confidence"],
            custom_confidence=s["custom_confidence"],
            custom_definition_base=s["custom_definition_base"],
            custom_definition_namelen_offset=s["custom_definition_namelen_offset"],
            custom_definition_namelen_bucket=s["custom_definition_namelen_bucket"],
            custom_definition_confidence=s["custom_definition_confidence"],
            builtin_tag_overhead_correction=s["builtin_tag_overhead_correction"],
            builtin_tag_overhead_correction_confidence=s["builtin_tag_overhead_correction_confidence"],
            custom_data_padding_multiple=s["custom_data_padding_multiple"],
            custom_mod4eq1_definition_bonus=s["custom_mod4eq1_definition_bonus"],
            custom_data_padding_confidence=s["custom_data_padding_confidence"],
        ),
        string_array=StringArrayModel(
            builtin_confidence=raw["string_array"]["builtin_confidence"],
            builtin_array_base=raw["string_array"]["builtin_array_base"],
            builtin_per_element=raw["string_array"]["builtin_per_element"],
            custom_confidence=raw["string_array"]["custom_confidence"],
            custom_array_base=raw["string_array"]["custom_array_base"],
            custom_per_element=raw["string_array"]["custom_per_element"],
        ),
        udt=UdtModel(alignment_confidence=raw["udt"]["alignment_confidence"]),
        array=ArrayModel(
            atomic_confidence=raw["array"]["atomic_confidence"],
            udt_confidence=raw["array"]["udt_confidence"],
        ),
        aoi_array=AoiArrayModel(
            flat_discount=raw["aoi_array"]["flat_discount"],
            bool_word_size=raw["aoi_array"]["bool_word_size"],
            bool_word_extra=raw["aoi_array"]["bool_word_extra"],
            enable_bits_packed_with_bools=raw["aoi_array"]["enable_bits_packed_with_bools"],
            block_alignment_bytes=raw["aoi_array"]["block_alignment_bytes"],
            array_tag_flat_bytes=raw["aoi_array"]["array_tag_flat_bytes"],
            confidence=raw["aoi_array"]["confidence"],
        ),
        aoi_definition=AoiDefinitionModel(
            base=raw["aoi_definition"]["base"],
            per_member_descriptor_bytes=raw["aoi_definition"]["per_member_descriptor_bytes"],
            bool_word_bytes=raw["aoi_definition"]["bool_word_bytes"],
            bool_word_bits=raw["aoi_definition"]["bool_word_bits"],
            enable_bits=raw["aoi_definition"]["enable_bits"],
            name_pool_alignment_bytes=raw["aoi_definition"]["name_pool_alignment_bytes"],
            name_pool_per_name_bytes=raw["aoi_definition"]["name_pool_per_name_bytes"],
            total_alignment_bytes=raw["aoi_definition"].get("total_alignment_bytes", 0),
            total_alignment_offset=raw["aoi_definition"].get("total_alignment_offset", 0),
            confidence=raw["aoi_definition"]["confidence"],
            name_length_bucket_bytes=raw["aoi_definition"]["name_length_bucket_bytes"],
            name_length_floor_bytes=raw["aoi_definition"]["name_length_floor_bytes"],
            name_length_bucket_confidence=raw["aoi_definition"]["name_length_bucket_confidence"],
        ),
        tag_overhead=TagOverheadModel(
            flat_base=raw["tag_overhead"]["flat_base"],
            per_8_chars=raw["tag_overhead"]["per_8_chars"],
            confidence=raw["tag_overhead"]["confidence"],
        ),
        alias_overhead=TagOverheadModel(
            flat_base=raw["alias_overhead"]["flat_base"],
            per_8_chars=raw["alias_overhead"]["per_8_chars"],
            confidence=raw["alias_overhead"]["confidence"],
        ),
        udt_definition=UdtDefinitionModel(
            base=raw["udt_definition"]["base"],
            per_member=raw["udt_definition"]["per_member"],
            name_per_8_chars=raw["udt_definition"]["name_per_8_chars"],
            bool_run_bonus=raw["udt_definition"]["bool_run_bonus"],
            confidence=raw["udt_definition"]["confidence"],
            member_name_pool_alignment_bytes=raw["udt_definition"][
                "member_name_pool_alignment_bytes"],
            member_name_pool_per_name_bytes=raw["udt_definition"][
                "member_name_pool_per_name_bytes"],
        ),
        logic_instructions=LogicInstructionModel(
            fixed_base_per_routine=raw["logic_instructions"]["fixed_base_per_routine"],
            jsr_fixed_base_per_routine=raw["logic_instructions"]["jsr_fixed_base_per_routine"],
            confidence=raw["logic_instructions"]["confidence"],
            weights=dict(raw["logic_instructions"]["weights"]),
            cpt_expression=CptExpressionModel(
                base_read=raw["cpt_expression"]["base_read"],
                operator_tier_costs=dict(raw["cpt_expression"]["operator_tier_costs"]),
                per_extra_same_tier_operand=raw["cpt_expression"]["per_extra_same_tier_operand"],
                per_extra_same_tier_by_tier_cost={
                    int(k): v for k, v in raw["cpt_expression"].get(
                        "per_extra_same_tier_by_tier_cost", {}).items()
                },
                two_tier_mix_base=raw["cpt_expression"]["two_tier_mix_base"],
                two_tier_mix_per_tier1=raw["cpt_expression"]["two_tier_mix_per_tier1"],
                two_tier_mix_per_tier2=raw["cpt_expression"]["two_tier_mix_per_tier2"],
                leading_tier1_run_length=raw["cpt_expression"].get(
                    "leading_tier1_run_length", 0),
                leading_tier1_run_bytes=raw["cpt_expression"].get(
                    "leading_tier1_run_bytes", 0),
                pow_tier_mix_base=raw["cpt_expression"]["pow_tier_mix_base"],
                pow_tier_mix_per_operator=raw["cpt_expression"]["pow_tier_mix_per_operator"],
                three_tier_mix_base_by_remainder={
                    int(k): v for k, v in raw["cpt_expression"]["three_tier_mix_base_by_remainder"].items()
                },
                three_tier_mix_per_pow_operand=raw["cpt_expression"]["three_tier_mix_per_pow_operand"],
                real_dest=CptRealDestModel(
                    expression_base=raw["cpt_expression"]["real_dest"]["expression_base"],
                    extra_operator=raw["cpt_expression"]["real_dest"]["extra_operator"],
                    operator_count_base={
                        int(k): v for k, v in
                        raw["cpt_expression"]["real_dest"]["operator_count_base"].items()
                    },
                    pow_extra=raw["cpt_expression"]["real_dest"]["pow_extra"],
                    pow_with_tier2_extra=raw["cpt_expression"]["real_dest"]["pow_with_tier2_extra"],
                    per_int_operand=raw["cpt_expression"]["real_dest"]["per_int_operand"],
                    narrow_widening_block=raw["cpt_expression"]["real_dest"]["narrow_widening_block"],
                    per_float_literal=raw["cpt_expression"]["real_dest"]["per_float_literal"],
                    confidence=raw["cpt_expression"]["real_dest"]["confidence"],
                ),
            ),
            operand_type_surcharge=OperandTypeSurchargeModel(
                confidence=raw["operand_type_surcharge"]["confidence"],
                surcharges={
                    instr: dict(types)
                    for instr, types in raw["operand_type_surcharge"]["surcharges"].items()
                },
                mixed=dict(raw["operand_type_surcharge"].get("mixed") or {}),
            ),
            indirect_index=IndirectIndexModel(
                confidence=raw["indirect_index"]["confidence"],
                tag_index_cost=raw["indirect_index"]["tag_index_cost"],
                tag_offset_index_cost=raw["indirect_index"]["tag_offset_index_cost"],
                member_access_cost=raw["indirect_index"].get("member_access_cost", 0),
                bool_element_cost=raw["indirect_index"].get("bool_element_cost", 0),
                string_element_cost=raw["indirect_index"].get("string_element_cost", 0),
            ),
            cmp_surcharge=CmpSurchargeModel(
                compound_confidence=raw["cmp_surcharge"]["compound_confidence"],
                compound_cost=raw["cmp_surcharge"]["compound_cost"],
                float_literal_confidence=raw["cmp_surcharge"]["float_literal_confidence"],
                float_literal_cost=raw["cmp_surcharge"]["float_literal_cost"],
            ),
            task_program_overhead=TaskProgramOverheadModel(
                routine_extra=raw["task_program_overhead"]["routine_extra"],
                program_extra=raw["task_program_overhead"]["program_extra"],
                task_extra=raw["task_program_overhead"]["task_extra"],
                confidence=raw["task_program_overhead"]["confidence"],
            ),
            jsr_param_cost=JsrParamCostModel(
                a_base=raw["jsr_param_cost"]["a_base"],
                a_per_param=raw["jsr_param_cost"]["a_per_param"],
                b_base=raw["jsr_param_cost"]["b_base"],
                b_per_param=raw["jsr_param_cost"]["b_per_param"],
                confidence=raw["jsr_param_cost"]["confidence"],
                output_param_cost=raw["jsr_param_cost"]["output_param_cost"],
                b_multiparam_extra=raw["jsr_param_cost"].get("b_multiparam_extra", 0),
                b_multiparam_threshold=raw["jsr_param_cost"].get("b_multiparam_threshold", 2),
                structured_arg_call_extra=raw["jsr_param_cost"].get("structured_arg_call_extra", 0),
                structured_arg_target_extra=raw["jsr_param_cost"].get("structured_arg_target_extra", 0),
                structured_ret_call_extra=raw["jsr_param_cost"].get("structured_ret_call_extra", 0),
                ret_instr_bytes=raw["jsr_param_cost"].get("ret_instr_bytes", 0),
                ret_operand_bytes=raw["jsr_param_cost"].get("ret_operand_bytes", 0),
                ret_target_offset=raw["jsr_param_cost"].get("ret_target_offset", 0),
            ),
            branch_bracket_cost_per_instruction=raw["logic_instructions"]["branch_bracket_cost_per_instruction"],
            aoi_call_site_bytes=raw.get("aoi_call_site", {}).get("bytes", 0),
            aoi_call_site_per_param_bytes=raw.get(
                "aoi_call_site", {}).get("per_param_bytes", 0),
            aoi_call_site_input_ref_extra_bytes=raw.get(
                "aoi_call_site", {}).get("input_ref_extra_bytes", 0),
            branch_bracket_confidence=raw["logic_instructions"]["branch_bracket_confidence"],
            aoi_logic_composite_surcharge_per_instr=raw["logic_instructions"]["aoi_logic_composite_surcharge_per_instr"],
            aoi_internal_per_rung=raw["logic_instructions"].get("aoi_internal_per_rung", 0),
            aoi_internal_per_rung_confidence=raw["logic_instructions"].get("aoi_internal_per_rung_confidence", "FITTED"),
            aoi_internal_per_word_destination=raw["logic_instructions"].get(
                "aoi_internal_per_word_destination", 0),
            series_output_extra_discount=(
                raw.get("series_output", {}).get("extra_output_discount", 0)
                if raw.get("series_output", {}).get("apply", False) else 0),
            aoi_internal_per_word_destination_confidence=raw["logic_instructions"].get(
                "aoi_internal_per_word_destination_confidence", "KNOWN"),
            jsr_target_composite_surcharge_per_instr=raw["logic_instructions"]["jsr_target_composite_surcharge_per_instr"],
            composite_surcharge_confidence=raw["logic_instructions"]["composite_surcharge_confidence"],
            composite_surcharge_cap=raw["logic_instructions"]["composite_surcharge_cap"],
            safety_task_program_shell=raw["logic_instructions"]["safety_task_program_shell"],
            safety_task_program_shell_confidence=raw["logic_instructions"]["safety_task_program_shell_confidence"],
            fixed_base_per_routine_confidence=raw["logic_instructions"].get(
                "fixed_base_per_routine_confidence", "FITTED"),
        ),
    )
