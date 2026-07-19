"""Test suite for kolakoski.py — three oracle families, none self-referential.

The design problem with testing a self-describing sequence: the obvious test
"does rle(K) reproduce K?" is exactly the property the code *implements*, so
a bug that breaks both sides symmetrically sails through. The suite therefore
leans on three *independent* kinds of truth (PLAN.md §6):

  1. External data   — 300 terms transcribed from OEIS (a source none of our
                       code derives from), plus a re-runnable full check in
                       tools/crosscheck_oeis.py.
  2. Independent     — four implementations built on different
     implementations   characterizations must agree term-for-term.
  3. Structural      — theorems about K (fixed-point property, run-count and
     theorems          prefix-sum windows) asserted over large prefixes, plus
                       hand-computed vectors that pin rle/rld themselves
                       (without which oracle 3 is vacuously satisfied by
                       rle = identity — found in review, round 1).

Review-measured fact worth recording: typical wrong variants (bad seed, bad
pointer start, flipped parity) first diverge from K at indices 2, 6, and 3 —
so even the 300-term literal catches that whole bug class ~100× over.
Exercise C4 in the writeup turns this into a mutation-testing lab.

Suite budget: a few seconds (dominated by two 10^6-term generations).
"""

import doctest
from itertools import islice

import pytest

import kolakoski
from kolakoski import (
    METHODS,
    STREAM_METHODS,
    _demo,
    kolakoski_expand,
    kolakoski_pointer,
    rld,
    rle,
    stream_stats,
)

# ---------------------------------------------------------------------------
# Oracle 1: external data.
#
# First 300 terms of OEIS A000002, transcribed 2026-07-19 from the b-file
# https://oeis.org/A000002/b000002.txt (10,502 terms). At transcription time
# ALL 10,502 terms were verified against kolakoski_pointer; that full check
# is re-runnable via `python3 tools/crosscheck_oeis.py` (network required).
# OEIS content is licensed CC BY-SA 4.0.
# ---------------------------------------------------------------------------

A000002_PREFIX = [
    1,2,2,1,1,2,1,2,2,1,2,2,1,1,2,1,1,2,2,1,2,1,1,2,1,2,2,1,1,2,1,1,2,1,2,2,1,2,2,1,1,2,1,2,2,1,2,1,1,2,
    1,1,2,2,1,2,2,1,1,2,1,2,2,1,2,2,1,1,2,1,1,2,1,2,2,1,2,1,1,2,2,1,2,2,1,1,2,1,2,2,1,2,2,1,1,2,1,1,2,2,
    1,2,1,1,2,1,2,2,1,2,2,1,1,2,1,1,2,1,2,2,1,1,2,1,1,2,2,1,2,1,1,2,1,1,2,2,1,2,2,1,1,2,1,2,2,1,2,1,1,2,
    2,1,2,2,1,2,1,1,2,1,1,2,2,1,2,2,1,1,2,1,2,2,1,2,1,1,2,1,1,2,2,1,2,1,1,2,1,2,2,1,1,2,1,1,2,1,2,2,1,2,
    1,1,2,2,1,2,2,1,1,2,1,2,2,1,2,2,1,1,2,1,1,2,1,2,2,1,1,2,1,1,2,2,1,2,2,1,2,1,1,2,1,2,2,1,1,2,1,1,2,2,
    1,2,1,1,2,1,1,2,2,1,2,2,1,2,1,1,2,1,2,2,1,1,2,1,1,2,1,2,2,1,2,2,1,1,2,1,2,2,1,2,1,1,2,1,1,2,2,1,2,2,
]
assert len(A000002_PREFIX) == 300  # guard against a mangled paste of the literal


def first_n(name: str, n: int) -> list[int]:
    """First n terms via any implementation, list- or stream-flavored."""
    if name in METHODS:
        return METHODS[name](n)
    return list(islice(STREAM_METHODS[name](), n))


ALL_IMPLS = sorted(METHODS) + sorted(STREAM_METHODS)

# Shared large prefixes, computed once — the two list implementations are
# exercised (and implicitly compared) by building them.
K_1M_POINTER = kolakoski_pointer(1_000_000)
K_1M_EXPAND = kolakoski_expand(1_000_000)


@pytest.mark.parametrize("name", ALL_IMPLS)
def test_first_300_terms_match_oeis(name):
    # The one test whose oracle owes nothing to any idea in this repository.
    assert first_n(name, 300) == A000002_PREFIX


@pytest.mark.parametrize("name", ALL_IMPLS)
@pytest.mark.parametrize("n", [0, 1, 2, 3])
def test_edges(name, n):
    # n <= 3 never enters the main loops (seed-only territory) — the classic
    # nest of off-by-ones, so it is pinned for every implementation.
    assert first_n(name, n) == A000002_PREFIX[:n]


# ---------------------------------------------------------------------------
# Oracle 2: independent implementations agree.
# ---------------------------------------------------------------------------

def test_methods_agree_small():
    # Exhaustive prefix-by-prefix agreement, all four implementations.
    # (Streams are cheap to re-instantiate; lists are cheap to re-build.)
    reference = kolakoski_pointer(500)
    for n in range(501):
        for name in ALL_IMPLS:
            assert first_n(name, n) == reference[:n], (name, n)


def test_methods_agree_large():
    assert K_1M_POINTER == K_1M_EXPAND                       # 10^6, both lists
    ref_100k = K_1M_POINTER[:100_000]
    for name in sorted(STREAM_METHODS):                      # 10^5, both streams
        assert first_n(name, 100_000) == ref_100k, name


# ---------------------------------------------------------------------------
# Oracle 3: structural theorems — with the vacuity fix.
# ---------------------------------------------------------------------------

def test_rle_rld_hand_vectors():
    # These pin rle/rld to hand-computed values. Without them, the fixed-point
    # test below is satisfied by rle = identity (K's prefixes ARE prefixes of
    # K), a vacuity found in review. An identity rle fails here immediately.
    assert rle([1, 2, 2, 1, 1]) == [1, 2, 2]
    assert rle([1]) == [1]
    assert rle([]) == []
    assert rle([2, 2, 2, 2]) == [4]          # rle itself is generic
    assert rld([1, 2, 2], 1) == [1, 2, 2, 1, 1]
    assert rld([2, 2, 1, 1], 2) == [2, 2, 1, 1, 2, 1]
    assert rld([], 1) == []


def test_rld_inverse_of_rle():
    # (first symbol, run lengths) <-> word, both directions, on words chosen
    # to cover run lengths > 2 (K never exhibits those; a correct rle must).
    for word in (
        [1], [2], [1, 2], [2, 1, 1], [1, 1, 1, 2], [2, 2, 2, 2, 1],
        K_1M_POINTER[:257],       # the round-1 counterexample length, for fun
        K_1M_POINTER[:10_000],
    ):
        assert rld(rle(word), word[0]) == word


def test_rle_fixed_point_on_prefix():
    # The defining equation, in its honest finite form: run lengths of a
    # prefix, with the final (possibly boundary-cut) run dropped, are again
    # a prefix of K.
    lengths = rle(K_1M_POINTER)
    head = lengths[:-1]
    assert head == K_1M_POINTER[: len(head)]


def test_run_count_window():
    # Proven two-sided window (PLAN §6, derived in review round 2 by both
    # reviewers independently): ceil((3L-2)/5) <= #runs(L) <= ceil(3L/4).
    # Catches rle = identity at every L >= 4 and run-merging bugs from below.
    runs = 0
    prev = None
    for L, x in enumerate(K_1M_POINTER, start=1):
        if x != prev:
            runs += 1
            prev = x
        assert -(-(3 * L - 2) // 5) <= runs <= -(-(3 * L) // 4), L
    # Cross-check the incremental count against rle itself at the endpoint.
    assert runs == len(rle(K_1M_POINTER))


def test_prefix_sum_window():
    # Proven window L + floor(L/3) <= sum(K[:L]) <= 2L - floor(L/3) — from
    # "any 3 consecutive symbols contain both a 1 and a 2" (no 111/222).
    # This replaced a FALSE v1 bound refuted in review (first failure L=257);
    # the tight version of this story is Exercise T5.
    total = 0
    for L, x in enumerate(K_1M_POINTER, start=1):
        total += x
        assert L + L // 3 <= total <= 2 * L - L // 3, L


def test_alphabet_and_no_triples():
    assert set(K_1M_POINTER) == {1, 2}
    # No x,x,x window anywhere — checked DIRECTLY on the raw symbols, not
    # through rle (round-3 review: routing this through rle lets an
    # identity-rle mutant pass it vacuously; a byte scan has no such hole).
    raw = bytes(K_1M_POINTER)
    assert raw.find(b"\x01\x01\x01") == -1
    assert raw.find(b"\x02\x02\x02") == -1
    # The rle formulation is kept as a second, non-independent phrasing.
    assert max(rle(K_1M_POINTER)) <= 2


def test_pointer_loop_invariant():
    # The invariant kolakoski.py states at its loop head, checked at every
    # loop entry by replaying the same algorithm transparently. The replay
    # is tied to the shipped function by output equality at the end, so
    # this genuinely certifies the shipped algorithm's invariant (added in
    # round 3: both reviewers found the docstring promised this test
    # before it existed).
    n = 2_000
    seq = [1, 2, 2]
    i, symbol = 2, 1
    while len(seq) < n:
        assert rld(seq[:i], 1) == seq, f"invariant broken at i={i}"
        seq.extend([symbol] * seq[i])
        symbol = 3 - symbol
        i += 1
    assert seq[:n] == kolakoski_pointer(n)  # the replay IS the algorithm


def test_density_sanity():
    # A COMPUTATION, NOT A THEOREM: the measured density at 10^6 is
    # 0.499986; asserting a loose corridor guards against gross generator
    # bugs. Nothing here bears on the open conjecture (PLAN §3).
    density = K_1M_POINTER.count(1) / len(K_1M_POINTER)
    assert abs(density - 0.5) < 0.002


# ---------------------------------------------------------------------------
# The streaming consumer's contract, and the docstring examples.
# ---------------------------------------------------------------------------

def test_stream_stats_contract():
    # Exactly n items consumed — no lookahead — so the iterator remains
    # usable; and the stats must match an independent direct computation.
    it = iter(K_1M_POINTER[:20])
    count_ones, min_d, max_d = stream_stats(it, 10)
    assert list(it) == K_1M_POINTER[10:20]       # items 11..20 untouched

    prefix = K_1M_POINTER[:10]
    assert count_ones == prefix.count(1)
    walk, d = [0], 0
    for x in prefix:
        d += 1 if x == 1 else -1
        walk.append(d)
    assert (min_d, max_d) == (min(walk), max(walk))

    assert stream_stats(iter([]), 0) == (0, 0, 0)


def test_demo_output():
    # The CLI demo returns a string precisely so it can be tested; test it
    # (round-3 review caught the claim without the test). The demo must
    # show the terms, and its live self-check must report success.
    text = _demo(30)
    assert text.startswith("1 2 2 1 1 2 1 2 2 1")
    assert "yes" in text and "NO — BUG" not in text


def test_docstring_examples():
    # Every example in the module's docstrings is executed — annotated code
    # whose examples rot is worse than unannotated code.
    results = doctest.testmod(kolakoski)
    assert results.failed == 0, f"{results.failed} doctest failure(s)"
