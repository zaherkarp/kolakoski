"""The Kolakoski sequence, four ways — a heavily annotated teaching module.

The Kolakoski sequence (OEIS A000002) is the sequence over the alphabet {1, 2}

    K = 1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 2, 2, 1, 1, 2, 1, 1, ...

that *describes its own run structure*. Chop K into maximal runs (blocks of
equal symbols — "maximal" matters, otherwise the chopping is not unique) and
write down the length of each run:

        K    =  1  2 2  1 1  2  1  2 2  1  2 2  1 1  2  1 1 ...
        runs = (1)(2 2)(1 1)(2)(1)(2 2)(1)(2 2)(1 1)(2)(1 1)...
        lens =  1   2    2   1  1   2   1   2    2   1   2  ...
             =  K, again.

Formally: for an infinite word w over {1,2} that is not eventually constant,
let rle(w) be its sequence of maximal-run lengths. K is the unique such word
that starts with 1 and satisfies rle(K) = K. (Starting with 2 instead gives
the one other infinite fixed point, OEIS A078880 — which is just K with its
first letter deleted. Among finite words, only the empty word and "1" are
fixed. See docs/WRITEUP.md §2 for the two-line proofs.)

Why anyone cares: the most basic statistical question about K — *do 1s and 2s
each occupy half of it in the limit?* — is an open problem (asked by Keane;
see docs/WRITEUP.md §5). The best rigorous bound to date says the density of
1s eventually stays within 0.000080 of 1/2 (Nilsson 2014), yet nobody can
prove the limit even exists. Everything in this repo orbits that gap between
"easy to compute" and "impossible, so far, to prove".

This module is deliberately standard-library-only: the mathematics needs no
dependencies. It provides four independent ways to produce K —

    kolakoski_pointer(n)   the classic self-reading tape        O(n) memory
    kolakoski_expand(n)    iterate run-length *decoding*        O(n) memory
    kolakoski_gen()        unbounded generator (pointer inside) O(n) memory
    kolakoski_nilsson()    unbounded chain-of-levels generator  O(log n) memory

— plus the run-length encode/decode pair `rle`/`rld` they are all defined
through, and `stream_stats` for measuring the generators without storing
their output. Four implementations is three more than anyone needs to *use*;
the redundancy is the point — they cross-check one another in the test suite
(tests/test_kolakoski.py), and each one teaches a different idea.

Run this file to watch the sequence describe itself:

    python3 kolakoski.py 30
"""

from __future__ import annotations

from itertools import islice
from typing import Callable, Iterable, Iterator

__all__ = [
    "rle", "rld",
    "kolakoski_pointer", "kolakoski_expand",
    "kolakoski_gen", "kolakoski_nilsson",
    "stream_stats", "METHODS", "STREAM_METHODS",
]


# ---------------------------------------------------------------------------
# The encode/decode pair. Everything else in the module is defined in terms
# of these two, so they come first and stay tiny.
# ---------------------------------------------------------------------------

def rle(word: Iterable[int]) -> list[int]:
    """Run-length *encode*: the lengths of the maximal runs of `word`.

    >>> rle([1, 2, 2, 1, 1])
    [1, 2, 2]
    >>> rle([])
    []

    Note what is thrown away: the symbols. `rle` alone is lossy — that is
    why its inverse `rld` needs to be told the first symbol. The pair
    (first symbol, run lengths) determines the word exactly; see `rld`.

    Time O(len(word)), memory O(#runs).
    """
    lengths: list[int] = []
    prev = None            # symbol of the run currently being counted
    count = 0              # its length so far
    for x in word:
        if x == prev:
            count += 1
        else:
            # A new maximal run starts here; close out the previous one.
            if prev is not None:
                lengths.append(count)
            prev, count = x, 1
    if prev is not None:   # close the final run (empty input closes nothing)
        lengths.append(count)
    return lengths


def rld(lengths: Iterable[int], first: int = 1) -> list[int]:
    """Run-length *decode* over {1,2}: build the word whose maximal runs
    have the given `lengths`, with symbols alternating starting from `first`.

    >>> rld([1, 2, 2], first=1)
    [1, 2, 2, 1, 1]
    >>> rld([2, 2, 1, 1], first=2)
    [2, 2, 1, 1, 2, 1]
    >>> rld([], first=1)
    []

    Why alternation is forced, not a choice: consecutive *maximal* runs must
    have different symbols (equal symbols would merge into one run), and over
    a two-letter alphabet "different" means "the other one". This is exactly
    why w ↦ (w[0], rle(w)) and (first, lengths) ↦ rld(lengths, first) are
    mutually inverse bijections — carry the first symbol along and no
    information is lost in either direction.

    Time and memory O(sum(lengths)).
    """
    word: list[int] = []
    symbol = first
    for run_length in lengths:
        word.extend([symbol] * run_length)
        symbol = 3 - symbol     # the {1,2} trick: 3-1 == 2, 3-2 == 1
    return word


# ---------------------------------------------------------------------------
# Method A: the classic self-reading tape.
# ---------------------------------------------------------------------------

def kolakoski_pointer(n: int) -> list[int]:
    """First n terms of K via the self-reading tape (the textbook method).

    >>> kolakoski_pointer(12)
    [1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 2, 2]
    >>> [kolakoski_pointer(k) for k in range(4)]
    [[], [1], [1, 2], [1, 2, 2]]

    Why this works
    --------------
    K says: "my j-th maximal run has length K[j]" (0-indexed here). So keep
    the sequence built so far on a tape, and keep a read pointer i trailing
    behind the write end. The number seq[i] under the pointer is the length
    of the *next* run to write; runs alternate symbols, and the first run is
    a single 1. Writing that run and advancing the pointer keeps the tape
    exactly one step ahead of its own description — forever.

    The seed [1, 2, 2] with the pointer at i = 2 is the state *after* the
    first two runs, (1) and (2 2), have been written: their lengths 1, 2 are
    seq[0], seq[1], both already consumed, and seq[2] is the first length
    not yet used. The seed cannot be shorter: with fewer than 3 symbols the
    pointer would catch up with the write end and read symbols that do not
    exist yet.

    Time O(n); memory O(n) — the whole tape is retained. That honest cost is
    what kolakoski_nilsson() exists to beat.
    """
    if n <= 3:
        # The loop below assumes the 3-term seed is in place; for n <= 3 the
        # answer is just a prefix of the seed. (n <= 0 gives [].)
        return [1, 2, 2][:max(0, n)]

    seq = [1, 2, 2]
    i = 2               # read pointer: seq[i] is the next unused run length
    symbol = 1          # runs alternate; run #3 (0-indexed run 2) is 1s
    while len(seq) < n:
        # Loop invariant (machine-checked in the test suite):
        #     rld(seq[:i], 1) == seq
        # In words: the run lengths consumed so far, decoded, rebuild the
        # tape exactly. The seed establishes it — rld([1,2], 1) == [1,2,2] —
        # and each iteration extends both sides consistently: we consume one
        # more length (seq[i]) and append precisely the run it describes.
        seq.extend([symbol] * seq[i])
        symbol = 3 - symbol
        i += 1
    # The final run may overshoot n (e.g. n=4 builds 5 terms); truncate.
    return seq[:n]


# ---------------------------------------------------------------------------
# Method B: K as the limit of iterated run-length *decoding*.
# ---------------------------------------------------------------------------

def kolakoski_expand(n: int) -> list[int]:
    """First n terms of K by iterating w ↦ rld(w, 1) from the seed [1, 2].

    >>> kolakoski_expand(12)
    [1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 2, 2]
    >>> kolakoski_expand(2)
    [1, 2]

    Why this works
    --------------
    Decode-prefix lemma (proved in docs/WRITEUP.md §6): if w is a prefix of
    K with L = len(w), then rld(w, 1) is the concatenation of the first L
    maximal runs of K — because rle(K) = K says those runs have lengths
    w[0..L-1], and they alternate starting from K's first symbol, 1. So
    rld(w, 1) is again a prefix of K, of length sum(w) ≥ L + 1 for L ≥ 2:
    the map sends K-prefixes to strictly longer K-prefixes, and iterating it
    from the K-prefix [1, 2] converges to K itself.

    How fast? Provably fast, with no open-problem input: among any 3
    consecutive symbols of K there is at least one 2 and at least one 1
    (three equal symbols would be a run of length 3, contradicting
    rle(K) = K ⊆ {1,2}). Hence sum(w) sits in [L + ⌊L/3⌋, 2L − ⌊L/3⌋], and
    each round multiplies the length by roughly [4/3, 5/3]. Θ(log n) rounds
    reach n terms — measured: 33 rounds pass 10⁶, 39 pass 10⁷. (Empirically
    the factor approaches 3/2, but proving *that* is equivalent to the open
    density conjecture — Exercise T5. The analysis above never assumes it.)

    Two traps this function documents by existing:
    - The seed must be [1, 2], not [1]: the word [1] is a *fixed point* of
      rld(·, 1) — it decodes to itself and the iteration would sit still
      forever. "K is the unique fixed point" needs its fine print.
    - Iterate until len(w) >= n, then truncate to w[:n]; n <= 2 is served
      straight from the seed without iterating.

    Time O(n) total (geometric series); memory O(n).
    """
    if n <= 2:
        return [1, 2][:max(0, n)]
    w = [1, 2]
    while len(w) < n:
        w = rld(w, 1)
    return w[:n]


# ---------------------------------------------------------------------------
# Method C: the unbounded generator (streaming interface, honest O(n) memory).
# ---------------------------------------------------------------------------

def kolakoski_gen() -> Iterator[int]:
    """Yield K's terms forever, using the pointer method internally.

    >>> list(islice(kolakoski_gen(), 9))
    [1, 2, 2, 1, 1, 2, 1, 2, 2]

    The streaming *interface* hides the tape but does not shrink it: the
    generator still retains everything it has produced, because the read
    pointer will eventually need it. Memory after n terms: O(n), stated
    honestly. The whole point of kolakoski_nilsson() below is that this
    cost is not inherent.
    """
    seq = [1, 2, 2]
    i = 2               # read pointer, exactly as in kolakoski_pointer
    symbol = 1
    emitted = 0         # how many of seq's entries have been yielded so far
    while True:
        # Yield whatever the tape holds that hasn't been yielded yet...
        while emitted < len(seq):
            yield seq[emitted]
            emitted += 1
        # ...then extend the tape by one run, exactly as in the list version.
        seq.extend([symbol] * seq[i])
        symbol = 3 - symbol
        i += 1


# ---------------------------------------------------------------------------
# Method D: Nilsson's idea — a lazy chain of levels, O(log n) memory.
# ---------------------------------------------------------------------------

def kolakoski_nilsson() -> Iterator[int]:
    """Yield K's terms forever in O(log n) memory (chain-of-levels method).

    >>> list(islice(kolakoski_nilsson(), 9))
    [1, 2, 2, 1, 1, 2, 1, 2, 2]

    Why this works
    --------------
    The pointer method keeps the whole tape only to reread it as run
    lengths. But "the run lengths of K" are K again — so instead of
    rereading a stored copy, ask a *second, slower instance of this very
    generator* for them. That instance asks a third, and so on: a chain of
    levels, each producing K, each consuming its parent lazily.

    Level arithmetic: a level yields its first three symbols 1, 2, 2 from
    the hardcoded first two runs (1)(2 2) — lengths K[0]=1, K[1]=2, already
    spent on those very runs — and only *then* instantiates its parent,
    discards the parent's first two symbols (the spent lengths), and reads
    K[2], K[3], ... as the lengths of run 3, 4, ... with symbols alternating
    1, 2, 1, ... (run j is 1s for odd j, and run 3 is where we resume).

    Memory: each level is one small generator frame. A level consumes one
    parent symbol per run it emits, i.e. advances — eventually — at a rate
    in [3/5, 3/4] symbols-per-symbol (at L = 1 the ratio is 1; the exact
    finite-L statement is the run-count window ⌈(3L−2)/5⌉ ≤ #runs(L) ≤
    ⌈3L/4⌉, asserted in the test suite; conjecturally the rate is ~2/3).
    So after n terms only Θ(log n) levels exist — measured: 39 levels
    after 10⁷ terms, ~16 KB of generator frames, vs ~17 MB (at 10⁶) and
    ~10⁸ bytes (at 10⁷) for the tape-retaining methods. Total work
    remains O(n): the per-level costs form a geometric series. This is the construction behind Nilsson's
    space-efficient computation of the digit distribution (J. Integer
    Sequences 15 (2012), article 12.6.7 — "logarithmic space and still
    runs in linear time").
    """
    # First two runs, hardcoded: run 1 = (1), run 2 = (2 2).
    yield 1
    yield 2
    yield 2
    # Now recurse — lazily: the parent level does not exist until the code
    # reaches this line, which is what keeps the chain logarithmic (a level
    # only spawns its parent after emitting 3 symbols, so level k+1 exists
    # only once level k has done Θ(1) of work... and so on up the chain).
    parent = kolakoski_nilsson()
    next(parent)        # discard K[0] = 1 (spent on run 1 above)
    next(parent)        # discard K[1] = 2 (spent on run 2 above)
    symbol = 1          # run 3 is a run of 1s (runs alternate, run 1 was 1s)
    for run_length in parent:      # parent yields K[2], K[3], ... on demand
        for _ in range(run_length):
            yield symbol
        symbol = 3 - symbol


# ---------------------------------------------------------------------------
# The streaming consumer: measure a generator without storing its output.
# ---------------------------------------------------------------------------

def stream_stats(it: Iterator[int], n: int) -> tuple[int, int, int]:
    """Pull exactly n terms from `it`; return (count_ones, min_D, max_D).

    D is the running discrepancy #1s − #2s (OEIS A088568): the +1/−1 walk
    that fig3 plots and that nobody can prove stays small.

    >>> stream_stats(kolakoski_nilsson(), 10)   # walk: 1,0,-1,0,1,0,1,0,-1,0
    (5, -1, 1)

    This is the honest way to benchmark the generators' memory (fig6): it
    retains three integers, so a measurement of generator-plus-consumer
    measures the generator. It is also the solution scaffold for Exercise
    C1 (density at 10⁸ without 10⁸ memory). Contract: exactly n items are
    consumed from `it` — no lookahead — so the caller may keep using the
    iterator afterwards. For n = 0 the walk never moves: (0, 0, 0).
    Caveat: the contract presumes `it` can supply n items; a shorter
    iterator is consumed to exhaustion and the stats cover only what came
    out (islice semantics — no error is raised).

    Time O(n), memory O(1).
    """
    count_ones = 0
    d = 0                       # running #1s - #2s
    min_d = 0
    max_d = 0                   # extremes include the empty-prefix value 0
    for x in islice(it, n):
        if x == 1:
            count_ones += 1
            d += 1
        else:
            d -= 1
        if d < min_d:
            min_d = d
        elif d > max_d:
            max_d = d
    return count_ones, min_d, max_d


# ---------------------------------------------------------------------------
# Registries: tests and the benchmark iterate over these, so the module has
# one authoritative list of its own implementations (PLAN.md §5 pins the
# membership; adding a fifth implementation means adding one line here and
# it is automatically tested against the other four).
# ---------------------------------------------------------------------------

METHODS: dict[str, Callable[[int], list[int]]] = {
    "pointer": kolakoski_pointer,
    "expand": kolakoski_expand,
}

STREAM_METHODS: dict[str, Callable[[], Iterator[int]]] = {
    "gen": kolakoski_gen,
    "nilsson": kolakoski_nilsson,
}


# ---------------------------------------------------------------------------
# Demo: `python3 kolakoski.py [n]` — the module exhibits its own definition.
# ---------------------------------------------------------------------------

def _demo(n: int) -> str:
    """Render n terms, their run structure, and the live self-check.

    (Kept as a function returning a string so the demo itself is testable.)
    """
    terms = kolakoski_pointer(n)
    lengths = rle(terms)

    # Row 1: the terms. Row 2: brackets grouping each maximal run.
    # Row 3: each run's length, centered under its bracket — visibly
    # reproducing row 1.
    row_terms = " ".join(str(t) for t in terms)
    groups: list[str] = []
    lens_row: list[str] = []
    for length in lengths:
        width = 2 * length - 1          # a run of L symbols spans 2L-1 chars
        groups.append("└" + "─" * (width - 2) + "┘" if length > 1 else "╵")
        lens_row.append(str(length).center(width))
    row_groups = " ".join(groups)
    row_lens = " ".join(lens_row)

    # The defining property, checked live on this very prefix: the run
    # lengths of K[:n] (last run dropped — it may be cut mid-run by the
    # prefix boundary) must again be a prefix of K.
    head = lengths[:-1]
    ok = head == terms[: len(head)]
    check = (
        f"self-check: rle(first {n} terms) minus its last entry\n"
        f"            == first {len(head)} terms of K?  {'yes' if ok else 'NO — BUG'}"
    )
    return "\n".join([row_terms, row_groups, row_lens, "", check])


if __name__ == "__main__":
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(f"Kolakoski sequence, first {count} terms — it describes itself:\n")
    print(_demo(count))
