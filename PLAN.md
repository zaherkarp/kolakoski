# PLAN — A Teaching Exercise on the Kolakoski Sequence

**Version: 3** · **Status: FROZEN — implementation follows this document**

This document is the blueprint for a small, self-contained lesson built around the
Kolakoski sequence (OEIS [A000002](https://oeis.org/A000002)). It is a *living*
document: it is reviewed by two mathematician-programmer reviewers, revised in
response, and frozen before implementation begins. The review history is part of the
lesson — see [§9 Review process](#9-review-process) and Appendix A, where every
round-1 point is answered.

> **What changed in v2.** Both reviewers refuted v1's §5B growth bound with the same
> counterexample (L = 257) — replaced by *provable* bounds from no-`111`/no-`222`,
> with the 3/2 ratio demoted to "conjectural". §5A loop invariant corrected. Nilsson
> 2014 read first-hand: a *two-sided, unconditional* density bound — it, not Chvátal
> 1993, is the headline bound. Nilsson generator promoted to must-have with a
> streaming benchmark interface. Test-oracle vacuity fixed. Details: Appendix A.1–A.2.
>
> **What changed in v3 (freeze edits — confined to the round-2 lists).** The
> PNG-drift guard is re-mechanized (git does not preserve mtimes — Okafor
> demonstrated spurious failure on every fresh clone): `make verify` now re-renders
> figs 1–5 and byte-compares against the *committed* PNGs. The §6 structural oracle
> now asserts the **provable** run-count window ⌈(3L−2)/5⌉ ≤ len(rle(K[:L])) ≤
> ⌈3L/4⌉ (both reviewers derived the same correction independently; the v2-proposed
> 2/5 constant was weaker than trivial, and the 0.72 pin's justification was
> logically backwards — dropped). Registry membership and the `stream_stats`
> contract are pinned. fig2 gains pinned y-limits and eventual-bound scoping (
> Nilsson's N is not effective). T5(b)'s closed form gets the corrected k−2
> exponent — a reviewer self-correction. Two Appendix-A response rows are corrected
> for provenance/endorsement errors the reviewers caught in the author's own
> tables. Details: Appendix A.3–A.4.

---

## 1. Purpose and audience

**What we are building.** A repository a curious person can read top-to-bottom in an
evening and come away (a) understanding a genuinely open problem in mathematics that
can be stated in one sentence, and (b) having seen how careful mathematical software
gets designed: claims separated from conjectures, algorithms with stated invariants,
tests with independent oracles, and figures that show rather than tell.

**Audience.** Advanced undergraduate level, or any programmer comfortable with Python
and unafraid of a proof sketch. No background in combinatorics on words is assumed.

**Why the Kolakoski sequence.** It is self-describing (the definition fits in a
sentence), computable by a beginner (a dozen lines), and yet the most basic question
about it — *do 1s and 2s each occupy half the sequence in the limit?* (asked by
Keane, per Chvátal's report) — has been open for decades. Few objects offer this
ratio of accessibility to depth.

## 2. Learning objectives

A reader who works through the material should be able to:

1. State the definition of the Kolakoski sequence two ways (as a run-length fixed
   point, and constructively) and explain why the two definitions agree.
2. Prove two structural facts: the sequence contains no `1,1,1` or `2,2,2` (one
   line), and it is not eventually periodic (elementary, but with details that
   demand care — see §8.4).
3. Implement a correct generator from memory, and state the loop invariant that
   makes it correct.
4. State *precisely* what is open about the density of 1s (that even the existence of
   the limiting density is unproven), and name the best known rigorous bound —
   Nilsson 2014's two-sided sup-bound — together with the older Chvátal bound and
   the conditional Kupin–Rowland bound, distinguishing their logical strengths.
5. Explain why the naive generator needs O(n) memory and how a chain-of-levels
   scheme gets the same terms in far less memory (provably O(log n) levels).
6. Read each figure and say what it does — and does not — demonstrate.

## 3. Mathematical background (with a claims ledger)

**Definition (informal).** Write down a sequence of 1s and 2s in *maximal* runs
(maximality matters: without it, run-length encoding is ill-defined — `1,2,2` also
splits into blocks `(1)(2)(2)` with lengths `1,1,1`), letting the run lengths be
read off the sequence itself, starting `1, 2, 2, …`. The sequence *is* its own
run-length description:

```
K   = 1 2 2 1 1 2 1 2 2 1 2 2 1 1 2 1 1 ...
runs: (1)(2 2)(1 1)(2)(1)(2 2)(1)(2 2)(1 1)...
lens:  1  2    2   1  1  2    1  2    2   ...  = K again
```

**Definition (precise).** For an infinite word w ∈ {1,2}^ℕ that is not eventually
constant, let `rle(w)` be its sequence of maximal-run lengths. (The domain condition
is needed: an eventually-constant word has a last, infinite run, so `rle` produces
no value in {1,2}^ℕ for it.) **K is the unique such w with w₁ = 1 and rle(w) = w.**
The one other infinite fixed point starts with 2; it is
[A078880](https://oeis.org/A078880), and it equals shift(K) — deleting K's first
letter deletes exactly K's first run (that run has length K₁ = 1), so
`rle(shift K) = shift(rle K) = shift(K)`. Among *finite* words, exactly the empty
word ε and the word `1` are fixed by rle. These degenerate and sibling fixed points
are stated up front so that "unique" is honest and Exercise T2 is provable as posed.

**Claims ledger.** Every mathematical statement in the repo carries one of three
labels: **verified** = computed by code in this repo; **known** = cited to a source
we checked (first-hand unless marked otherwise); **OPEN** = nobody knows. Exact
rationals are carried alongside rounded decimals so rounding direction is checkable.

| Claim | Status | Source / how we check |
|---|---|---|
| First 10,502 terms are as tabulated by OEIS | **verified** | our generators vs. the OEIS b-file (all 10,502 terms matched, 2026-07-19; re-runnable via `tools/crosscheck_oeis.py`) |
| Runs have length 1 or 2; no `111`/`222` occurs | **proven** (easy) | one-line argument in writeup; tests check it to 10⁶ |
| Prefix sums: L + ⌊L/3⌋ ≤ sum(K[:L]) ≤ 2L − ⌊L/3⌋ | **proven** | two-line proof from no-`111`/no-`222` (writeup §6, Exercise T5); verified for all L ≤ 10⁷ |
| K is not eventually periodic | **proven** (with care) | full minimal-eventual-period proof in writeup §4 — v1's gapped sketch is preserved as Exercise T4's raw material |
| K is cube-free; its square subwords have lengths in {2,4,6,18,54} | **known** | Carpi 1994 via OEIS A000002 comment; corroborated in-repo: square half-lengths found in first 20,000 terms are exactly {1,2,3,9,27}, no cubes |
| Density of 1s exists and equals 1/2 | **OPEN** | Keane's question (per Chvátal's abstract); OEIS: "It is an unsolved problem…" |
| Upper densities of 1s AND of 2s are each < 0.501 | **known** | Chvátal, DIMACS TR 93-84 (1993) — abstract fetched and quoted first-hand |
| Finer Chvátal digits 0.500838 / 0.499162 | **known (second-hand)** | reported (e.g. Wikipedia) from the TR body; the TR's full text is behind a dead FTP link (attempted 2026-07-19), so these digits stay second-hand |
| For *some* N ≥ 1: sup over n ≥ N of \|#1s(n)/n − 1/2\| ≤ 455920839/911696379 − 1/2 ≤ 0.000080 | **known** | Nilsson 2014, Acta Phys. Pol. A 126, 549–552 — PDF read first-hand; bound is two-sided and does **not** assume the frequency exists; N is **not effective** in the paper, so no finite plotted range is covered by the theorem. Best known rigorous bound. |
| \|freq₁(K) − 1/2\| ≤ 17/762 *assuming the limit exists*; semi-rigorous unconditional 1/46 | **known** | Kupin–Rowland, arXiv:0809.2776, abstract quoted first-hand — a hedging-discipline exhibit (conditional-rigorous vs unconditional-semi-rigorous) |
| Kolakoski-(3,1) (alphabet {1,3}) relates to a **primitive substitution**; hence its letter frequencies exist | **known** | Baake–Sing, "Kolakoski-(3,1) is a (deformed) model set", arXiv:math/0206098 (abstract, first-hand) + the standard theorem: primitive ⟹ uniquely ergodic ⟹ uniform letter frequencies (textbook cite pinned at writeup time) |
| density(10⁶) = 0.499986; density(10⁷) = 0.5000046 (note the sign flip) | **verified** | computed in-repo; also independently by both reviewers |
| Discrepancy D(n) = #1s − #2s = A088568(n): extremes +63/−66 for n ≤ 10⁶; +189 (n = 7,518,095) / −154 (n = 2,222,194) for n ≤ 10⁷ | **verified** | computed in-repo; identity D = A088568 is exact algebra (3n − 2·S(n) = #1 − #2) |
| \|D(2⁶⁴)\| = 836,086,974 ≈ 0.19·√(2⁶⁴); growth "seems" ~√n | **known** | R. Brent's comment on A088568 / A289323 (fetched first-hand); explicitly *not* a theorem |
| Run counts: ⌈(3L−2)/5⌉ ≤ len(rle(K[:L])) ≤ ⌈3L/4⌉ | **proven** | inverts the prefix-sum window (derivation in §6); verified for all L ≤ 10⁷ by both reviewers and the author, near-tight on both sides |
| Max \|density − 1/2\| over n ∈ (10⁶, 10⁷] is 3.892106×10⁻⁵ at n = 1,798,512 — matching Nilsson 2014's own Table I decade entry 3.892×10⁻⁵ | **verified** | computed in-repo (round-2 review, re-verified by author); a free cross-corroboration of our generator against the paper's independent computation |

## 4. Deliverables

```
PLAN.md                       this file (v1 → v2 → v3-frozen, with Appendix A)
kolakoski.py                  core module, stdlib-only, heavily annotated
viz.py                        renders figures/fig1..fig6 (numpy + matplotlib)
tools/crosscheck_oeis.py      re-runnable OEIS b-file cross-check (network; stdlib)
tests/test_kolakoski.py       pytest suite (stdlib + pytest only)
figures/*.png                 six committed figures (see §7)
docs/WRITEUP.md               the lesson (see §8)
docs/reviews/round*-*.md      verbatim reviewer reports + author responses
README.md                     tour, quickstart, gallery, learning path
Makefile, requirements.txt, conftest.py, .gitignore   (committed; requirements now pin exact versions)
```

Constraint: the pre-existing `kolakoski_stars_blog_viz.py` and `out/` are historical
artifacts of this repo and stay byte-identical.

## 5. Algorithms (specification)

All in `kolakoski.py`, stdlib-only. Every function gets: a docstring with a "Why this
works" paragraph, a doctest, the loop invariant as a comment at the loop head, and an
honest complexity note. Two registries drive tests and benchmarks:

```python
METHODS:        dict[str, Callable[[int], list[int]]]   # {"pointer": A, "expand": B}
STREAM_METHODS: dict[str, Callable[[], Iterator[int]]]  # {"gen": C, "nilsson": D}
```

Membership is pinned as shown (round-2 Okafor finding 3). The streaming consumer has
an exact contract: `stream_stats(it, n)` pulls **exactly n** terms from `it` and
returns the tuple `(count_ones, min_D, max_D)` while retaining nothing — it is the
measurement harness for fig6 (both panels use it as the stream consumer, so timing
and memory measure the same computation) and the solution scaffold for Exercise C1.
Cross-implementation agreement tests materialize streams via `itertools.islice` when
comparing against `METHODS` output.

**A. `kolakoski_pointer(n)` — the classic self-reading tape.** Seed `[1,2,2]`; a read
pointer `i` starts at index 2; the writer appends runs of the alternating symbol, run
lengths dictated by `seq[i]`.
*Invariant (corrected in v2, machine-checked to 40 terms during review):* at every
loop entry, `rld(seq[:i], 1) == seq` — the lengths consumed so far, decoded, rebuild
exactly the tape written so far. The seed establishes it: `rld([1,2], 1) = [1,2,2]`.
*Edge cases are part of the spec:* the function returns `seq[:n]` (truncating a
possibly overshooting final run), and n ∈ {0,1,2,3} return the right prefixes of
`[1,2,2]` without entering the loop. *Time O(n), memory O(n).*

**B. `kolakoski_expand(n)` — iterate run-length decoding.** Define
`rld(lengths, first)` = the word whose maximal runs have the given lengths, symbols
alternating from `first`. Start from the seed word `[1,2]` and repeatedly apply
`w ↦ rld(w, first=1)`.
*Key lemma (structural part — proven in writeup §6):* if w is a prefix of K with
len(w) = L, then `rld(w, 1)` is the concatenation of the first L maximal runs of K,
hence again a prefix of K, of length sum(w).
*Growth (provable):* L + ⌊L/3⌋ ≤ sum(w) ≤ 2L − ⌊L/3⌋, because among any 3
consecutive symbols of K there is at least one 2 and at least one 1 (else `111` or
`222`). So each round multiplies the length by a factor in [4/3 − o(1), 5/3 + o(1)],
and Θ(log n) rounds reach n terms **with no unproven input**. Empirically the factor
approaches 3/2 — but "the factor → 3/2" is *equivalent to the open density
conjecture* (Exercise T5c), so the analysis never assumes it. Measured: 33 rounds to
pass 10⁶, 39 to pass 10⁷.
*Teaching trap to document:* the singleton word `[1]` is a spurious finite fixed
point of `rld(·, 1)` — this is why the seed is `[1,2]`.
*Edges (round-2 Okafor finding 4):* iterate until len(w) ≥ n and return `w[:n]`;
n ≤ 2 is served from the seed without iterating.
*Time O(n) total, memory O(n).*

**C. `kolakoski_gen()` — unbounded lazy generator.** Wraps A so callers can take
terms one at a time. Memory still O(n) — stated honestly; it exists to set up why D
is interesting.

**D. `kolakoski_nilsson()` — low-memory unbounded generator (must-have).** A chain
of levels: level 0 emits symbols of K; each level holds its current symbol and the
remaining budget of the current run, and pulls its next run length from the level
above, levels created lazily. *Depth (provable):* each level consumes one symbol of
its parent per emitted run, i.e. advances at a rate in [3/5, 3/4] symbols-per-symbol
by the prefix-sum bounds (conjecturally ~2/3); either way the depth after n terms is
Θ(log n) and total work is O(n). Review measurement: 39 levels after 10⁷ pulls;
streaming memory ~9 KB vs ~17 MB for the O(n) list. This is the idea behind
Nilsson's space-efficient computation (J. Integer Seq. 15 (2012), #12.6.7 —
abstract, quoted verbatim: "logarithmic space and still runs in linear time").
*Promoted from should-have to must-have in v2:* learning objective 5, fig6's memory
panel, and Exercise C1 all depend on it — v1's "demote by deleting one line"
contingency was refuted in review and is withdrawn.

**E. Helpers.** `rle(word)` (maximal-run lengths), `rld(lengths, first)` (inverse),
used by tests and the writeup's equivalence argument.

**CLI demo.** `python3 kolakoski.py 30` prints the terms, the bracketed run
structure, and a live check that `rle(prefix)` is again a prefix — the module
demonstrates its own defining property when run.

## 6. Testing strategy

Three oracle *families*, chosen so no test checks the code against itself (with the
vacuity fix below):

1. **External data:** first 300 terms hard-coded, copied at dev time from the OEIS
   b-file (provenance comment with date; the full 10,502-term cross-check is
   re-runnable via `tools/crosscheck_oeis.py`, network required, stdlib only).
   Review measurement: typical wrong variants (bad seed, bad pointer start, flipped
   parity) first diverge at indices 2, 6, 3 — a 300-term oracle catches that bug
   class with two orders of magnitude to spare.
2. **Independent implementations:** pointer vs. expand (vs. Nilsson) derive from
   different characterizations; `test_methods_agree` compares them exhaustively for
   n = 0..500 and at n = 10⁵ (all) and 10⁶ (pointer vs. expand).
3. **Structural properties:** the fixed-point check `rle(K[:n])` is a prefix of K
   (dropping the last, possibly truncated, run). **Vacuity fix (v2, re-mechanized
   in v3):** this oracle is satisfied by `rle = identity`, so it is pinned by
   (a) hard-coded vectors such as `rle([1,2,2,1,1]) == [1,2,2]` and
   `rld([1,2,2],1) == [1,2,2,1,1]`, and (b) the **proven two-sided run-count
   window** ⌈(3L−2)/5⌉ ≤ len(rle(K[:L])) ≤ ⌈3L/4⌉ asserted for every L ≤ 10⁶
   (identity fails it at every L ≥ 4; run-merging bugs fail it from below).
   *Derivation:* with R runs in a length-L prefix, sum(K[:R−1]) ≤ L−1 and
   L ≤ sum(K[:R]); apply the prefix-sum window: 4(R−1)−2 ≤ 3(L−1) ⟹ R ≤ ⌈3L/4⌉,
   and 3L − 2 ≤ 5R ⟹ R ≥ ⌈(3L−2)/5⌉. Both round-2 reviewers derived this window
   independently and verified it to 10⁷ (near-tight both sides); the v2-proposed
   constants (a one-sided 0.72·n and a ⌊2L/5⌋ lower bound weaker than the trivial
   ⌈L/2⌉) are withdrawn. Plus the **proven prefix-sum bounds**
   L + ⌊L/3⌋ ≤ sum(K[:L]) ≤ 2L − ⌊L/3⌋ asserted for all L ≤ 10⁶.

Plus: edge cases n ∈ {0,1,2,3} for every `METHODS` entry; alphabet ⊆ {1,2} and no
`x,x,x` window over 10⁶ terms; `rld(rle(w), w[0]) == w` round-trips on hand-picked
words *and* K-prefixes; a *loose* density sanity check |density(10⁶) − 1/2| < 0.002
explicitly commented as "a computation, not a theorem"; and a doctest runner so
every docstring example is executed. Suite budget: under ~10 seconds (review
timings: pointer 10⁶ ≈ 0.14 s, expand 10⁶ ≈ 0.24 s — comfortable).

## 7. Visualization plan

Rendered by `viz.py` into `figures/`, committed. Global rules: Agg backend, one
shared style block, a colorblind-safe two-hue palette for the two symbols, dpi 150,
≤ 400 KB per file. No randomness anywhere. **Determinism claim, scoped (v2):**
figures 1–5 must be byte-identical across runs *in the pinned environment*
(`requirements.txt` now pins exact versions; PNGs embed the matplotlib version
string, so cross-version identity is not claimed). Enforced by `viz.py --verify`, which (re-mechanized in v3 — git does not preserve
mtimes, so the v2 mtime guard would fail spuriously on every fresh clone, as
round-2 Okafor demonstrated): renders figs 1–5 into a temp directory, **byte-
compares them against the committed PNGs** (this simultaneously proves determinism
and that the committed figures match the current `viz.py` — the drift guard), and
checks the ≤ 400 KB budget. fig6 is timing-based and exempt from the byte
comparison (size check only). Environment scope: the pinned requirements plus
Python 3.11.

Data-side rules: never hand matplotlib 10⁶ raw points — fig2 samples ~4,000
log-spaced indices; fig3 aggregates into a fixed number of data-side bins
(independent of figure size); benchmarks time and measure memory in **separate
passes** (review measurement: tracemalloc inflates runtime ~8.5×), and the memory
pass consumes `STREAM_METHODS` streams via `stream_stats` so the instrument measures
the algorithm, not the output list.

| # | file | teaching point (one line) | design sketch |
|---|---|---|---|
| 1 | `fig1_self_description.png` | K reads out its own run lengths: `rle(K) = K`. | First ~30 terms as colored unit blocks; brackets group runs; the run lengths printed beneath visibly reproduce the sequence. No axes — a diagram, not a chart. |
| 2 | `fig2_density.png` | The running density of 1s hugs 1/2; the best rigorous bounds are far tighter than the wiggle — yet the limit is unproven. | Main panel: density of 1s among first n terms, log-x from n = 10 to 10⁷, **y-limits pinned to [0.47, 0.53]** (the early transient — density(3) = 1/3 — is clipped, and the caption says so); dashed line at 1/2; Chvátal's **first-hand** 0.499/0.501 lines, labeled as bounds on **limit points** which the finite curve may legitimately exit. Inset zoom on the decade (10⁶, 10⁷] with Nilsson's two-sided ±0.000080 lines, **scoped as an eventual bound (its N is not effective — the theorem does not certify the plotted decade)**; Chvátal's lines stay out of the inset (off-scale ~12×). Caption carries the exact rational and the free cross-check: our measured max deviation in that decade, 3.892×10⁻⁵ at n = 1,798,512, equals Nilsson's own Table I entry. The story on ink: 0.501 → 0.000080, limit still open. |
| 3 | `fig3_discrepancy_walk.png` | The +1/−1 walk (1↦+1, 2↦−1) = A088568 stays astonishingly near 0 — no theorem explains it. | D(n) to 10⁷, linear x, 1,250 data-side min/max bins (~8,000 points/bin). Dashed ±0.2·√n guides labeled "±0.2√n" **on the lines themselves**, c = 0.2 chosen to match Brent's reported \|D(2⁶⁴)\| ≈ 0.19·√(2⁶⁴); caption: "fair-coin-walk scale, small constant; no theorem either way" (adjudication of a genuine reviewer disagreement — Appendix A; walk occupies ~27% of the y-axis at this design, per round-2 measurement). Extremes annotated: +189 at n = 7,518,095; −154 at n = 2,222,194. |
| 4 | `fig4_turtle.png` | The same bits drawn as geometry: turn left on 1, right on 2. | Unit-step turtle path, ~20,000 steps, colored by time (perceptually uniform colormap), equal aspect, axes off. Purely qualitative. |
| 5 | `fig5_raster.png` | No wrap width makes the columns line up — what aperiodicity looks like (evidence, not proof). | Two panels: first 8,100 terms wrapped at width 90; first 8,010 wrapped at 89. Binary colormap, nearest-neighbor. |
| 6 | `fig6_benchmark.png` | Four correct implementations, two resource profiles — and a three-orders-of-magnitude memory gap. | n-grid 10³..10⁷ (×10). Left: wall time vs n (log-log), min of 3 runs with min–max whiskers, timing pass free of instrumentation; streams timed through `stream_stats` (the same consumer the memory pass uses). Right: tracemalloc peak vs n, **single run** (peaks need no min-of-k), with `METHODS` consumed as lists vs `STREAM_METHODS` via `stream_stats` — the O(n)-list vs O(log n)-stream separation (~17 MB vs ~9–15 KB at 10⁶) is the payoff; the caption states the one deliberate asymmetry (the output list is counted in the list family's footprint). Measured budget ≈ 2 min total (~30 s timing + ~80 s traced). Caption states methodology, environment, and that timings vary by machine. |

## 8. Writeup outline (`docs/WRITEUP.md`)

1. **Hook** — the sequence that describes itself; fig1.
2. **Two definitions and why they agree** — `w ↦ (w₁, rle(w))` and
   `(s, ℓ) ↦ rld(ℓ, s)` as **mutually inverse bijections** (the "adjoint" wording of
   v1 is withdrawn — rle is not even monotone for the prefix order: rle(12) = 11 and
   rle(122) = 12 are prefix-incomparable); the forcing argument pinning down
   `1,2,2,1,1,…`; the fixed-point inventory: ε and `1` (finite), K and
   shift(K) = A078880 (infinite), with the one-line shift proof.
3. **A short history** — Oldenburger 1939 (Trans. AMS 46, 453–466); Kolakoski's 1965
   Monthly problem 5304 (solution: Üçoluk 1966); **Keane's density question** as
   credited by Chvátal's abstract; OEIS's naming note.
4. **Easy theorems, honest proofs** — no `111`/`222` (one line); the prefix-sum
   bounds (two lines from it); non-periodicity in full: minimal *eventual* period p,
   block aligned at a run boundary past the preperiod, a length-2 run exists in the
   block (a (12)^∞ tail would force rle(K) = K to end 1^∞ ∋ 111), so the r runs in
   the block satisfy r < p while rle(K) = K is eventually periodic with period r —
   contradiction with minimality. v1's gapped sketch is quoted in Exercise T4.
5. **The open problem** — what exactly is unknown (existence of the limit, and its
   value); the bound history told with logical precision: Chvátal 1993 (< 0.501 both
   letters, computer-assisted; method sketch), the reported finer digits
   (second-hand), **Nilsson 2014's sup-bound ±0.000080 (two-sided, unconditional,
   first-hand quote)**, and Kupin–Rowland's pair (rigorous-but-conditional 17/762 vs
   semi-rigorous-unconditional 1/46) as a lesson in reading hedges; what our own
   10⁶–10⁷ measurements show and why that is *evidence, not proof* (density sign
   flip; Brent's √n-scale discrepancy data at 2⁶⁴).
6. **Algorithms** — walkthroughs of A/B/D mirroring the code annotations: corrected
   invariant, decode-prefix lemma with proof, provable growth window [4/3, 5/3] and
   what 3/2 would cost (T5c), the `[1]` trap, level-depth argument for D.
7. **Figure gallery** — each figure embedded with 2–3 sentences of commentary plus
   one "look for this" prompt.
8. **Exercises** (graded ●○○ → ●●●) —
   *Computational:* C1 density at 10⁸ with the streaming generator (O(log n)
   memory); C2 tabulate gaps between sign changes of D(n); C3 add a third wrap
   width to fig5 and explain; **C4 (new, from review) "break the generator, then
   catch it"** — three sabotaged variants (bad seed / bad pointer start / flipped
   parity), predict which test catches each and at which index the output first
   diverges (answers 2, 6, 3 — verified), then map each oracle's blind spots.
   *Theoretical:* T1 write out the no-`111` proof; T2 the fixed-point inventory
   (ε, 1, K, shift K); T3 prove the decode-prefix lemma; **T4 (repurposed) find and
   repair the gaps in v1's non-periodicity sketch** — the sketch is quoted verbatim;
   deliverables are named (identify gaps (i)–(iii) of §8.4, repair each,
   cross-reference the full proof), and the answer key accepts additional
   legitimate gaps beyond the canonical three (e.g. why run-boundary alignment
   persists across all copies of the period block); **T5 (new, from review)
   provable prefix-sum bounds and what 3/2 would cost** — (a) the
   [L + ⌊L/3⌋, 2L − ⌊L/3⌋] window from no-`111`/no-`222`; (b) Θ(log n)
   expand-rounds with no unproven input — the answer key uses the corrected closed
   form L_k ≥ 2 + (4/3)^{k−2} for k ≥ 2, tight at k = 2 (the reviewer's original
   k−1 exponent failed at k = 1, 2 and was self-corrected in round 2); (c) "round
   factor → 3/2" ⟺ the open density conjecture.
   *Extension:* X1 implement **Kolakoski-(3,1)** (alphabet {1,3} — named per the
   actual Baake–Sing title), plot its running letter frequency next to Kol(1,2)'s,
   and explain via the primitive-substitution theorem why *there* the frequency
   provably exists; route further reading through Dekking 1997, with Baake–Sing as
   "for the curious".
9. **References** — numbered; each carries "verified against source, date" or an
   explicit "second-hand via …" tag; exact rationals quoted where bounds are stated.

## 9. Review process

Two reviewer personas — **explicitly fictional, run as AI subagents**, disclosed as
such in every review file — critique this plan and later the artifacts:

- **Dr. Salomé Vidal** — combinatorics on words / symbolic dynamics. Lane:
  definitions and side conditions, proof rigor, citation accuracy, hedging
  discipline, exercise solvability.
- **Dr. Emeka Okafor** — computational mathematics / scientific software. Lane:
  invariants and edge cases, complexity claims, test-oracle independence, benchmark
  honesty, figure craft, whether comments teach *why* rather than narrate *what*.

**Protocol.** Round 1 (done): both reviewed v1 → point-by-point responses in
Appendix A → this v2. Round 2: both review v2 → v3 declared **frozen**;
implementation follows v3. Round 3 (post-implementation): Vidal reads the writeup +
code comments + captions and must hand-trace a generator for n ≤ 15, re-verify ≥ 2
quantitative claims by running the repo's code, **and re-derive the corrected §5B/§6
prefix-sum bounds**; Okafor reads code + tests + viz and must run the suite, audit
one oracle for independence, empirically probe one complexity claim, **and run
`viz.py --verify` (the determinism/size/drift gate is his check)**. Findings →
fixes → `docs/reviews/round3-responses.md`.

**Anti-rubber-stamp rules.** Round-1 reviews required ≥ 2 major and ≥ 3 minor
substantive issues (both reviewers exceeded this); round 2 relaxes to ≥ 1 major or
≥ 2 minor *or* a justified sign-off enumerating residual risks. Every review must
contain an *Independent verification performed* section with shown work. Symmetric
safeguard: the author re-verifies every accepted correction before applying it
(done for 100% of round-1 factual claims — see Appendix A) and may reject
suggestions with recorded reasons.

## 10. Milestones (commit sequence)

1. ~~Scaffolding~~ → 2. ~~PLAN v1~~ → 3. ~~round-1 reviews (Okafor, Vidal)~~ →
4. ~~v2 + responses~~ → 5. ~~round-2 reviews~~ → 6. **this v3, frozen** →
7. `kolakoski.py` + `tools/crosscheck_oeis.py` + tests (suite green before commit)
→ 8. `viz.py` + figures (verify = render-and-byte-compare vs committed) →
9. writeup + README → 10. round-3 reviews → 11. fixes + responses → 12. push,
open PR.

## 11. Freeze note

The round-1 seeded questions and the round-2 focused questions are all resolved
(Appendix A.1–A.4). Both round-2 reviewers recommended freezing after the listed
edits with no further pre-implementation round; this v3 confines its diff to those
lists. Round-3 (post-implementation) mandatory checks, restated: **Vidal** —
hand-trace a generator to n ≤ 15; re-verify ≥ 2 quantitative writeup claims by
running repo code; re-derive the §5B prefix-sum window and the §6 run-count window.
**Okafor** — run the test suite; audit one oracle for independence; empirically
probe one complexity claim; run `viz.py --verify` (determinism + committed-PNG
byte-compare + size gate is his check).

---

## Appendix A — Changelog and review responses

| Version | Date | Summary |
|---|---|---|
| v1 | 2026-07-19 | Initial draft for round-1 review. |
| v2 | 2026-07-19 | All round-1 points addressed: §5B bound replaced by provable window; §5A invariant corrected; Nilsson 2014 upgraded to first-hand two-sided headline bound; Nilsson generator promoted to must-have with streaming benchmark; test-oracle vacuity fixed; fig2/fig3/fig6 redesigned; definitions tightened (maximal runs, rle domain, fixed-point inventory); Baake–Sing renamed (3,1); Keane credited; exercises C4/T5 added, T4 repurposed. |
| v3 **(frozen)** | 2026-07-19 | Round-2 freeze edits, diff confined to the reviewers' lists: drift guard re-mechanized (render + byte-compare vs committed PNGs; mtime withdrawn); §6 oracle adopts the provable run-count window ⌈(3L−2)/5⌉ ≤ R ≤ ⌈3L/4⌉ (v2's 2/5 and 0.72 constants withdrawn); registries and `stream_stats` contract pinned; §5B edge sentence; fig2 y-limits + eventual-bound scoping + Table-I cross-check; fig3 on-line guide labels; fig6 budget/single-run-memory notes; T4 deliverables + flexible key; T5(b) exponent corrected (reviewer self-correction); objective-2 rewording; two ledger rows added; A.1-M4/A.2-M1/A.2-T5/A.2-Q5 response rows corrected (see A.3–A.4). |

**Re-verification policy (applied below).** Every reviewer claim marked ACCEPTED was
independently re-verified by the author before being applied: computational claims
were re-run from scratch (fresh scripts, not the reviewers' code), and source quotes
were re-fetched. Where a reviewer's claim was *itself* imperfect, the response says
so — reviews are evidence, not authority.

### A.1 Responses to round-1 — Okafor (`docs/reviews/round1-okafor.md`)

| # | Point | Decision | Response / re-verification |
|---|---|---|---|
| M1 | §5B bound false; first failure L = 257; replace with L + ⌊L/3⌋ | **ACCEPTED** | Re-verified: sum(K[:257]) = 384 < 385; 563,998 violations below 10⁶; replacement bound has **0 violations up to 10⁷** (beyond his 10⁶). §5B rewritten; round counts 33/39 confirmed and quoted. Both reviewers found the same counterexample independently — the strongest possible signal it is real. |
| M2 | §5A invariant false at entry; edges/truncation unspecified | **ACCEPTED** | Re-verified the counterexample (`rld([1,2,2],1) = [1,2,2,1,1]`) and the corrected invariant (holds at every loop entry to 40 terms). Spec now states `rld(seq[:i],1) == seq`, the truncating return, and n ≤ 3 behavior. |
| M3 | list-returning registry destroys fig6's memory story | **ACCEPTED** | `STREAM_METHODS` + `stream_stats` added (§5, §7); memory pass consumes streams. His 9.1 KB vs 8.5–16.8 MB measurements adopted as design targets, to be re-measured in-repo for the caption. |
| M4 | structural oracle vacuous for `rle = identity` | **ACCEPTED** | Vacuity confirmed by inspection (identity fixes everything; K-prefixes are K-prefixes). §6 adds hard-coded vectors + a run-count assertion. **[v3 correction: this row originally claimed the 0.72 threshold was "justified by the now-proven ≤ 3/4 ratio bound" — logically backwards, as both round-2 reviewers pointed out (0.72 < 3/4, so the theorem cannot justify it; and r/L = 8/11 > 0.72 at L = 11). v3 drops 0.72 entirely in favor of the provable window — see A.3 finding 2 / A.4 finding 1.]** |
| m1 | never time under tracemalloc; report spread; state n-grid | **ACCEPTED** | Separate passes specified; min-of-3 with min–max whiskers; grid 10³..10⁷ stated. His 8.5× overhead measurement is quoted in §7 as the reason. |
| m2 | Chvátal corridor misleads | **ACCEPTED** (merged with Vidal m6) | Lines instead of band, labeled as limit-point bounds; and the numbers on ink are now the first-hand 0.499/0.501, with finer digits demoted to caption/second-hand. |
| m3 | fig3 bins must be data-side; pick x-scale | **ACCEPTED** | 1,250 fixed bins, linear x (his Q3 answered). |
| m4 | pin versions; scope determinism per-environment | **ACCEPTED** | `requirements.txt` now pins `numpy==2.4.6`, `matplotlib==3.11.1`, `pytest==9.1.1`; §7 scopes the byte-identity claim; his two-process hash experiment noted. |
| m5 | ledger labeled density "verified" before measuring | **ACCEPTED** | Now measured (0.499986 / 0.5000046) and re-verified by the author; his numbers matched. |
| m6 | figure-drift gap between commits 8–9 | **ACCEPTED** | `make verify` gains a PNG-older-than-viz.py failure; round-3 assignment of `--verify` to Okafor recorded in §9. |
| Q1 | Nilsson must-have; "delete one line" contingency false | **ACCEPTED** | Promoted; contingency withdrawn; C1/objective-5/fig6 dependency chain acknowledged in §5D. |
| Q4 | cut the ±√n guide | **PARTIALLY REJECTED** | His flattening arithmetic is correct for c = 1 at n = 10⁶ (re-verified: max D = 63 vs 1000). But Vidal's counter-evidence (Brent: \|D(2⁶⁴)\| ≈ 0.19·√n; O(log n) "seems incorrect") was re-fetched and is decisive on the premise: √n *is* the empirically right order at scale. Adjudication: keep the guide at **c = 0.2** on a 10⁷-range plot (guide 632 vs walk 189 at the right edge — visible, not flattened), caption states c, its provenance, and "no theorem either way". |
| add-1 | `stream_stats` helper | **ACCEPTED** | In §5E. |
| add-2/3/4 | n-grid; exact pins; CI-style chain | **ACCEPTED** | §7, requirements, Makefile `verify`. |
| C4 | mutation-testing exercise | **ACCEPTED** | Divergence indices 2/6/3 independently re-verified; added as C4. |
| his Q2 | commit a re-runnable b-file checker? | **ACCEPTED** | `tools/crosscheck_oeis.py` (stdlib, network, standalone) added to deliverables; the 10,502 claim is now reproducible, not an anecdote. |

### A.2 Responses to round-1 — Vidal (`docs/reviews/round1-vidal.md`)

| # | Point | Decision | Response / re-verification |
|---|---|---|---|
| M1 | §5B false (same counterexample); provable window [4/3, 5/3]; hedge §5D's 2/3 | **ACCEPTED** | Same re-verification as Okafor M1; her upper bound 2L − ⌊L/3⌋ additionally verified to 10⁷ with 0 violations. §5D now carries the provable [3/5, 3/4] window. Her D-walk extremes to 10⁷ re-verified exactly and added to the ledger. **[v3 correction: this row originally described her `⌊(L−2)/3⌋` (which appeared only in her verification log) as the proposal and credited the ⌊L/3⌋ strengthening to the author. Wrong — her M1 and T5(a) proposed L + ⌊L/3⌋ with the disjoint-triples proof verbatim; the author adopted, not strengthened, it. Caught by her in round 2 (finding 2).]** |
| M2 | Nilsson 2014 is readable, rigorous, unconditional; upgrade and verify the lower side | **ACCEPTED** | The author obtained and read the PDF (the v1 "could not read" note reflected a broken local toolchain, since fixed — her "one download away" verdict was right). First-hand quote now in the ledger. **Her own Q2 is answered affirmatively by the source:** the paper's bound is `sup_{n≥N} |o_n/n − 1/2| ≤ 455920839/911696379 − 1/2 ≤ 0.000080` — two-sided by construction, no separate lower table needed. Objective 4 and §8.5 now name Nilsson as the headline bound. |
| M3 | non-periodicity: ledger inconsistency + real gaps; full proof supplied | **ACCEPTED** | Ledger relabeled "proven (with care)"; her minimal-eventual-period proof adopted as writeup §4 main text (gaps (i)–(iii) each addressed); T4 repurposed as gap-hunting on v1's sketch, per her recommendation. |
| m1 | "maximal" blocks | **ACCEPTED** | Fixed in §3 with her (1)(2)(2) counterexample retained as the explanation. |
| m2 | rle domain condition; surface ε and `1` | **ACCEPTED** | Her proposed wording adopted nearly verbatim in §3. |
| m3 | "adjoint pair" wrong | **ACCEPTED** | Re-verified her example (rle(12) = 11, rle(122) = 12, prefix-incomparable). §8.2 now says mutually inverse bijections with the first symbol carried along. |
| m4 | Kupin–Rowland missing from ledger; arXiv:0809.2776 | **ACCEPTED** | Abstract re-fetched first-hand; exact conditionality language confirmed and quoted; ledger row added. (The author's private notes had the wrong arXiv ID 0809.2777; her ID is the correct one — fixed.) |
| m5 | Baake–Sing title is "(3,1)"; name a frequency theorem | **ACCEPTED** | Title re-verified from the arXiv listing; X1 renamed Kolakoski-(3,1); "primitive ⟹ uniquely ergodic ⟹ frequencies exist" stated, textbook cite to be pinned at writeup time (round 3 checks it). |
| m6 | Chvátal provenance (only 0.50084 is on Wikipedia; abstract says 0.501) + band semantics | **ACCEPTED** | The author fetched the TR abstract first-hand (0.501 both letters; Keane credited) and attempted the TR body — the FTP link is dead (timeout, 2026-07-19, documented). Finer digits stay second-hand in the ledger; fig2 redesigned to put only first-hand numbers on ink. |
| add-1..4 | KR row; shift(K) proposition; Keane credit; D = A088568 exactly + bound test | **ACCEPTED** | shift(K) = A078880 re-verified against all 10,000 b-file terms; the algebra D(n) = 3n − 2S(n) re-derived; structural bound test to 10⁶ added to §6; Keane credited in §1/§8.3. |
| T5 | provable-bounds exercise with the 3/2 ⟺ conjecture punchline | **ACCEPTED** | Added. **[v3 correction: this row originally said "her solution sketch checks out" — the (b) recurrence does follow from the lower bound, but the closed form L_k ≥ 2 + (4/3)^{k−1} fails at k = 1, 2. She caught her own slip in round 2 (and correctly noted the author's re-verification should have caught it first — the policy verified the recurrence's logic but not the closed form; lesson recorded). Corrected form L_k ≥ 2 + (4/3)^{k−2} for k ≥ 2, tight at k = 2, re-verified to 10⁷ by both parties; §8's answer key uses it.]** |
| her Q1 | was the v1 bound intended for iteration lengths only? | **ANSWERED** | No proof was in hand; the v1 bound was simply wrong (it encoded D ≤ 2, refuted at 257). The 4/3 analysis is adopted; nothing is claimed for the iteration subsequence beyond it. |
| her Q3 | exact rationals in the ledger | **ACCEPTED** | Ledger and §8.9 carry them. |
| her Q4 | who reads the TR body before v3? | **ANSWERED** | The author attempted it (dead FTP, documented in the ledger row); the digits remain second-hand and are presented as such; Nilsson's first-hand bound carries the headline, so no claim depends on the TR body. |
| her Q5 | is the JIS quote verbatim? | **ANSWERED/VERIFIED** | Yes — the JIS abstract page was fetched during planning; "uses logarithmic space and still runs in linear time" is a verbatim substring of the abstract. **[v3 correction: this row originally described §5D's quote as ellipsized; §5D in fact carries the longer un-ellipsized fragment "logarithmic space and still runs in linear time". Her round-2 audit re-verified the substring against the source either way.]** |
| fig3 stance (vs Okafor Q4) | keep guide, fix premise, cite Brent | **ACCEPTED (adjudicated)** | Brent's A088568/A289323 comments re-fetched first-hand; her premise correction stands; c = 0.2 design adopted as above. |

### A.3 Responses to round-2 — Okafor (`docs/reviews/round2-okafor.md`)

Verdict: REQUEST CHANGES (two v2-introduced defects). Disposition audit: all
round-1 majors landed; two PARTIALs addressed below.

| # | Point | Decision | Response / re-verification |
|---|---|---|---|
| F1 | mtime drift guard unsound — git assigns checkout-time mtimes; every fresh clone fails | **ACCEPTED** | Re-verified by cloning this repo into scratch: all files carry checkout-time mtimes (write-order, not authorship). Guard re-mechanized per his fix: `viz.py --verify` renders figs 1–5 to a temp dir and byte-compares against the committed PNGs (§7) — which also ties committed figures to current `viz.py`, closing the gap he identified in render-twice. |
| F2 | §11-Q4's 2/5 constant wrong; exact window ⌈(3L−2)/5⌉ ≤ R ≤ ⌈3L/4⌉ | **ACCEPTED** | The author had independently derived the same 3/5 correction between rounds (scratch log), and re-verified his exact form: 0 violations to 10⁶, tightness slacks 0 and 2 — matching his 10⁷ run. Adopted in §6 with the derivation; 0.72 dropped; A.1-M4's backwards justification corrected in place. Convergent with Vidal round-2 finding 1. |
| F3 | stream/registry contract underspecified | **ACCEPTED** | §5 pins membership ({pointer, expand} / {gen, nilsson}), the `stream_stats(it, n)` pull-exactly-n + `(count_ones, min_D, max_D)` contract, islice materialization for agreement tests, and same-consumer timing (§7). |
| F4 | expand lacks edge/truncation sentence | **ACCEPTED** | Added to §5B verbatim. |
| F5 | state fig6 budget; memory pass single-run | **ACCEPTED** | §7 fig6 row updated (~2 min; single-run peaks). |
| regressions | README must echo the pin caveat; record Python 3.11 | **ACCEPTED** | §7 scope note updated; README requirement recorded for milestone 9. |
| fig3 nit | label guides on-line | **ACCEPTED** | §7 fig3 row updated. |

### A.4 Responses to round-2 — Vidal (`docs/reviews/round2-vidal.md`)

Verdict: APPROVE WITH NITS. Disposition audit: all round-1 math landed; her
PARTIALs concern the author's response tables, corrected in place above.

| # | Point | Decision | Response / re-verification |
|---|---|---|---|
| F1 | 0.72 justification backwards; ⌊2L/5⌋ weaker than trivial ⌈L/2⌉ | **ACCEPTED** | Same resolution as A.3-F2 (her derivation and Okafor's agree); her observation that 2L/5 < L/2 makes the v2 proposal weaker-than-trivial is recorded as the reason the author's Q4 framing was itself defective. |
| F2 | A.2-M1 miscredited her bound proposal | **ACCEPTED** | Row corrected in place with the true provenance (her M1/T5(a) proposed L + ⌊L/3⌋ with proof; the author adopted it). |
| F3 | A.2-T5 endorsed an off-by-one closed form | **ACCEPTED** | Row corrected in place; T5(b) answer key uses L_k ≥ 2 + (4/3)^{k−2}, k ≥ 2 (tight at k = 2) — re-verified by the author against the actual iteration lengths (2, 3, 5, 7, 10, 15, 23, 34, 50, 75, …: original form fails exactly at k = 1, 2; corrected form has zero failures). Her meta-point stands: the re-verification policy checked the recurrence but not the closed form — noted as a policy lesson. |
| F4 | fig2 y-range unstated; Nilsson's N not effective | **ACCEPTED** | §7 fig2 row pins y ∈ [0.47, 0.53], x from 10, clipping captioned; eventual-bound scoping added to the figure spec *and* the ledger row; her Table-I coincidence (our 3.892106×10⁻⁵ at n = 1,798,512 vs the paper's 3.892×10⁻⁵ — re-verified exactly by the author) goes in the caption as a cross-check. |
| F5 | bundled nits (objective 2; "a fortiori"; her-Q5 row) | **ACCEPTED** | All three fixed in place. |
| Q2 guards | T4 must name deliverables; key accepts extra gaps | **ACCEPTED** | §8 T4 updated verbatim. |

**Process note.** Round 1: the two reviewers, working in parallel without seeing
each other's reports, refuted the same v1 lemma with the same first counterexample
(L = 257) via different routes (Okafor: direct scan; Vidal: the D ≤ 2 equivalence),
and disagreed productively about fig3, which the author resolved with a third,
re-fetched source. Round 2: they independently derived the same corrected run-count
window; one reviewer caught errors in the author's response tables, the other
caught an unsound verification mechanism the author had accepted; and one reviewer
publicly corrected her own round-1 slip. Errors flowed in every direction —
author→reviewer, reviewer→author, reviewer→self — and every accepted claim carries
a recorded independent re-check. This is the review system working as designed, and
it is left visible on purpose.
