# PLAN — A Teaching Exercise on the Kolakoski Sequence

**Version: 1** (draft for review) · **Status: awaiting round-1 review**

This document is the blueprint for a small, self-contained lesson built around the
Kolakoski sequence (OEIS [A000002](https://oeis.org/A000002)). It is a *living*
document: it will be reviewed by two mathematician-programmer reviewers, revised in
response, and frozen before implementation begins. The review history is part of the
lesson — see [§9 Review process](#9-review-process) and Appendix A.

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
about it — *do 1s and 2s each occupy half the sequence in the limit?* — has been open
since the 1960s. Few objects offer this ratio of accessibility to depth.

## 2. Learning objectives

A reader who works through the material should be able to:

1. State the definition of the Kolakoski sequence two ways (as a run-length fixed
   point, and constructively) and explain why the two definitions agree.
2. Prove the two easiest structural facts: the sequence contains no `1,1,1` or
   `2,2,2`, and it is not eventually periodic.
3. Implement a correct generator from memory, and explain the loop invariant that
   makes it correct.
4. State *precisely* what is open about the density of 1s (that even the existence of
   the limiting density is unproven), and name the best known rigorous bounds.
5. Explain why the naive generator needs O(n) memory and how a cleverer scheme gets
   the same terms in O(log n) memory.
6. Read each figure and say what it does — and does not — demonstrate.

## 3. Mathematical background (with a claims ledger)

**Definition (informal).** Write down a sequence of 1s and 2s, in runs (blocks of
equal symbols) whose lengths are read off the sequence itself, starting `1, 2, 2, …`.
The sequence *is* its own run-length description:

```
K   = 1 2 2 1 1 2 1 2 2 1 2 2 1 1 2 1 1 ...
runs: (1)(2 2)(1 1)(2)(1)(2 2)(1)(2 2)(1 1)...
lens:  1  2    2   1  1  2    1  2    2   ...  = K again
```

**Definition (precise).** Let `rle(w)` map a finite or infinite word over {1,2} to
its sequence of run lengths. K is the unique infinite word over {1,2} that begins
with 1 and satisfies `rle(K) = K`. (Starting with 2 instead gives the one other
fixed point, `2,2,1,1,2,1,2,2,...` = A000002's sibling A078880.)

**Claims ledger.** Every mathematical statement in the repo carries one of three
labels, and the writeup will keep them straight:

| Claim | Status | Source / how we check |
|---|---|---|
| First 10,502 terms are `1,2,2,1,1,2,1,…` as tabulated by OEIS | **verified** | our generators vs. the OEIS b-file (all 10,502 terms matched at dev time, 2026-07-19) |
| Runs have length 1 or 2; no `111`/`222` occurs | **proven** (easy) | writeup gives the one-line argument; tests check it to 10⁶ |
| K is not eventually periodic | **proven** (easy) | writeup gives a proof via the run-length derivative; fig5 gives visual (non-)evidence |
| K is cube-free; its square subwords have lengths in {2,4,6,18,54} | **known** | Carpi 1994, as summarized in OEIS A000002 comments |
| Density of 1s exists and equals 1/2 | **OPEN** | OEIS: "It is an unsolved problem…" — the star of the show |
| 0.49916 < (lim inf and lim sup of density) < 0.50084 | **known** | Chvátal, DIMACS TR 93-84 (1993); Wikipedia-verified digits, rounded outward |
| Sharper bound ≈ ±0.000080 | **known (second-hand)** | Nilsson 2014 (Acta Phys. Pol. A 126) as summarized by Wikipedia; we could not read the PDF directly, so it is quoted as "reported" |
| Kolakoski-(1,3) comes from a primitive substitution; its letter frequencies provably exist | **known** | Baake–Sing 2003 (abstract, arXiv:math/0206098) + standard Perron–Frobenius theory for primitive substitutions (Allouche–Shallit 2003) |
| Density at n = 10⁶, 10⁷ (numbers to be measured) | **verified** | computed by our code; quoted with the n at which they were computed |

The rule enforced throughout: **"verified" = computed by code in this repo; "known" =
cited to a checked source; everything else is hedged or omitted.**

## 4. Deliverables

```
PLAN.md                       this file (v1 → v2 → v3-frozen, with Appendix A)
kolakoski.py                  core module, stdlib-only, heavily annotated
viz.py                        renders figures/fig1..fig6 (numpy + matplotlib)
tests/test_kolakoski.py       pytest suite (stdlib + pytest only)
figures/*.png                 six committed figures (see §7)
docs/WRITEUP.md               the lesson (see §8)
docs/reviews/round*-*.md      verbatim reviewer reports + author responses
README.md                     tour, quickstart, gallery, learning path
Makefile, requirements.txt, conftest.py, .gitignore   (already committed)
```

Constraint: the pre-existing `kolakoski_stars_blog_viz.py` and `out/` are historical
artifacts of this repo and stay byte-identical.

## 5. Algorithms (specification)

All in `kolakoski.py`, stdlib-only. Every function gets: a docstring with a "Why this
works" paragraph, a doctest, the loop invariant as a comment at the loop head, and an
honest complexity note. A registry `METHODS: dict[str, callable]` maps method names to
`f(n) -> list[int]` so tests and the benchmark iterate over all implementations; adding
or demoting an algorithm is a one-line change.

**A. `kolakoski_pointer(n)` — the classic self-reading tape.** Seed `[1,2,2]`; a read
pointer `i` starts at index 2; the writer appends runs of the alternating symbol, run
lengths dictated by `seq[i]`.
*Invariant:* when the pointer is at `i`, every element of `seq[:i+1]` has already been
used (or is being used) as a run length, and `seq` is exactly the concatenation of the
runs those lengths describe. *Time O(n), memory O(n).*

**B. `kolakoski_expand(n)` — iterate run-length decoding.** Define
`rld(lengths, first)` = the word whose runs have the given lengths, symbols
alternating from `first`. Start from the seed word `[1,2]` and repeatedly apply
`w ↦ rld(w, first=1)`.
*Key lemma (writeup proves):* if `w` is a prefix of K then `rld(w, 1)` is again a
prefix of K, of length `sum(w)` ≥ ⌈3·len(w)/2⌉ − 1; hence iterating from `[1,2]`
converges to K, lengths growing geometrically (ratio → 3/2), so Θ(log n) rounds reach
n terms. *Teaching trap to document:* the singleton word `[1]` is a spurious finite
fixed point of `rld(·, 1)` — this is why the seed is `[1,2]` and why "K is the
*unique* fixed point" needs its side conditions stated carefully.
*Time O(n) total, memory O(n).*

**C. `kolakoski_gen()` — unbounded lazy generator.** Wraps A so callers can take
terms one at a time (`itertools.islice`-friendly). Memory still O(n) — stated
honestly; it exists to set up why D is interesting.

**D. `kolakoski_nilsson()` — O(log n)-memory unbounded generator.** A chain of
levels: level 0 emits symbols of K; each level holds its current symbol and the
remaining budget of the current run, and pulls its next run length from the level
above, levels created lazily. Depth after n terms is Θ(log n) (each level advances
~2/3 as fast as the one below); total work is O(n) (geometric series). This is the
idea behind Nilsson's space-efficient digit-distribution computation (J. Integer
Seq. 15 (2012), #12.6.7: "logarithmic space … linear time").
*Status: should-have.* If it turns out disproportionately fiddly, it is demoted to a
guided exercise, and the registry/tests/benchmark adapt by deleting one line.

**E. Helpers.** `rle(word)` (run lengths), `rld(lengths, first)` (inverse), used by
tests and the writeup's equivalence argument.

**CLI demo.** `python3 kolakoski.py 30` prints the terms, the bracketed run
structure, and a live check that `rle(prefix)` is again a prefix — the module
demonstrates its own defining property when run.

## 6. Testing strategy

Three genuinely independent oracles, so no test is checking the code against itself:

1. **External data:** first 300 terms hard-coded, copied at dev time from the OEIS
   b-file (provenance comment with date; full 10,502-term cross-check already done
   during planning and recorded in the test file comment).
2. **Independent algorithms:** pointer vs. expand (vs. Nilsson) are derived from
   different characterizations; `test_methods_agree` compares them exhaustively for
   n = 0..500 and spot-checks n = 10⁵ (all) and 10⁶ (pointer vs. expand).
3. **Structural property:** `rle(K[:n])` must reproduce a prefix of K (dropping the
   last, possibly truncated, run) — the defining fixed-point equation as a test.

Plus: edge cases n ∈ {0,1,2,3} for every method; alphabet ⊆ {1,2} and no `x,x,x`
window over 10⁶ terms; `rld(rle(w), w[0]) == w` round-trips; a *loose* density sanity
check |density(10⁶) − 1/2| < 0.002 explicitly commented as "a computation, not a
theorem"; and a doctest runner so every docstring example is executed. Suite budget:
under ~10 seconds.

## 7. Visualization plan

Rendered by `viz.py` into `figures/`, committed. Global rules: Agg backend, one
shared style block, a colorblind-safe two-hue palette for the two symbols, dpi 150,
≤ 400 KB per file. No randomness anywhere; figures 1–5 must be byte-identical across
runs (enforced by `viz.py --verify`, which renders twice and compares SHA-256; fig6
is timing-based and exempt). Never hand matplotlib 10⁶ raw points: fig2 samples
~4,000 log-spaced indices; fig3 uses per-pixel min/max banding.

| # | file | teaching point (one line) | design sketch |
|---|---|---|---|
| 1 | `fig1_self_description.png` | K reads out its own run lengths: `rle(K) = K`. | First ~30 terms as colored unit blocks; brackets group runs; the run lengths printed beneath visibly reproduce the sequence. No axes — a diagram, not a chart. |
| 2 | `fig2_density.png` | The running density of 1s hugs 1/2, but neither convergence nor the limit is proven. | Density of 1s among first n terms, n up to 10⁷, log-x; dashed line at 1/2; shaded Chvátal band [0.49916, 0.50084]. |
| 3 | `fig3_discrepancy_walk.png` | The +1/−1 walk (1↦+1, 2↦−1) stays astonishingly near 0 — nobody can prove it keeps doing so. | Partial sums D(n) to 10⁶ (this is OEIS A088568 up to sign convention); min/max band per pixel column; a ±√n guide curve labeled "visual reference only — NOT a theorem". |
| 4 | `fig4_turtle.png` | The same bits drawn as geometry: turn left on 1, right on 2. | Unit-step turtle path, ~20,000 steps, colored by time (perceptually uniform colormap), equal aspect, axes off. Purely qualitative. |
| 5 | `fig5_raster.png` | No wrap width makes the columns line up — what aperiodicity looks like (evidence, not proof). | Two panels: first 8,100 terms wrapped at width 90; first 8,010 wrapped at 89. Binary colormap, nearest-neighbor. |
| 6 | `fig6_benchmark.png` | Three correct algorithms, three resource profiles. | Left: wall time vs n (log-log, best of 3) for every `METHODS` entry; right: peak memory (tracemalloc) vs n, where the O(n) vs O(log n) gap is the payoff. Caption states methodology and that timings vary by machine. |

## 8. Writeup outline (`docs/WRITEUP.md`)

1. **Hook** — the sequence that describes itself; fig1.
2. **Two definitions and why they agree** — `rle`/`rld` as an adjoint pair; the
   forcing argument that pins down `1,2,2,1,1,…` symbol by symbol; the exactly-two-
   fixed-points statement (start-with-1 vs start-with-2), each with proof or proof
   sketch a strong undergraduate can complete.
3. **A short history** — Oldenburger 1939 (Trans. AMS 46, 453–466) where the word
   appears in symbolic dynamics; Kolakoski's 1965 Monthly problem 5304 (solution:
   Üçoluk 1966) that gave it its name; OEIS's naming note.
4. **Easy theorems** — no `111`/`222` (one line from the definition); non-periodicity:
   if K were eventually periodic with period p, applying the run-length derivative
   maps period sums → strictly shorter period (average run length > 1), contradicting
   `rle(K) = K`. Spelled out with the boundary details — this proof is on the round-3
   mandatory-check list precisely because "average run length > 1" needs care.
5. **The open problem** — what exactly is unknown (existence of the limit, and its
   value); Chvátal's bounds and how such bounds are proven (finite automata /
   exhaustive verification flavor, one paragraph); Nilsson's reported sharpening;
   Kupin–Rowland's conditional bound (17/762, assuming existence); what our own
   measurements at 10⁶–10⁷ show and why that is *evidence, not proof*.
6. **Algorithms** — walkthroughs of A/B/D mirroring the code annotations: invariant,
   correctness argument, complexity; the `[1]` trap; the decode-prefix lemma.
7. **Figure gallery** — each figure embedded with 2–3 sentences of commentary plus
   one "look for this" prompt.
8. **Exercises** (graded ●○○ → ●●●) —
   *Computational:* C1 reproduce the density at 10⁸ with O(log n) memory; C2 tabulate
   gaps between sign changes of D(n); C3 add a third wrap width to fig5 and explain
   what you see.
   *Theoretical:* T1 write out the no-`111` proof; T2 prove the two-fixed-points
   claim; T3 prove the decode-prefix lemma; T4 patch the stated gap in the
   non-periodicity sketch.
   *Extension:* X1 implement Kolakoski-(1,3), plot its running letter frequency next
   to Kol(1,2)'s, and read Baake–Sing to explain the moral: *there* the frequency
   provably exists — self-similarity buys what brute computation cannot.
9. **References** — numbered; each carries "verified against source, date" or an
   explicit "second-hand via …" tag. OEIS A000002 (+ b-file, + A088568, + A078880),
   Oldenburger 1939, Kolakoski 1965/Üçoluk 1966, Chvátal 1993, Nilsson 2012 & 2014,
   Carpi 1994 (via OEIS), Baake–Sing 2003, Allouche–Shallit 2003, Dekking 1997.

## 9. Review process

Two reviewer personas — **explicitly fictional, run as AI subagents**, disclosed as
such in every review file — critique this plan and later the artifacts:

- **Dr. Salomé Vidal** — combinatorics on words / symbolic dynamics. Lane:
  definitions and their side conditions, proof-sketch rigor, citation accuracy,
  hedging discipline, exercise solvability.
- **Dr. Emeka Okafor** — computational mathematics / scientific software. Lane:
  invariants and edge cases, complexity claims, test-oracle independence, benchmark
  honesty, figure craft, whether comments teach *why* rather than narrate *what*.

**Protocol.** Round 1: both review PLAN v1 → author responds point-by-point
(ACCEPTED with the change / REJECTED with reasons / DEFERRED) in Appendix A → v2.
Round 2: both review v2 → v3 declared **frozen**; implementation follows v3.
Round 3 (post-implementation): Vidal reads the writeup + code comments + captions
and must hand-trace a generator for n ≤ 15 and re-verify ≥ 2 quantitative claims by
running the repo's code; Okafor reads code + tests + viz and must run the suite,
audit one oracle for independence, and empirically probe one complexity claim.
Findings → fixes → `docs/reviews/round3-responses.md`.

**Anti-rubber-stamp rules.** Round-1 reviews must surface ≥ 2 major and ≥ 3 minor
substantive issues; "looks good overall" is banned; every review must contain an
*Independent verification performed* section where the reviewer picks ≥ 1 factual
claim and confirms or refutes it with shown work. Symmetric safeguard: the author
must independently re-verify any accepted correction before applying it (reviewers
can be wrong too), and may reject suggestions with recorded reasons.

## 10. Milestones (commit sequence)

1. ~~Scaffolding~~ (done) → 2. this file (v1) → 3. round-1 reviews → 4. v2 +
responses → 5. round-2 reviews → 6. v3 frozen → 7. `kolakoski.py` + tests (suite
green before commit) → 8. `viz.py` + figures → 9. writeup + README → 10. round-3
reviews → 11. fixes + responses → 12. push, open PR.

## 11. Open questions for the reviewers (seeded, genuine)

1. **Nilsson generator (§5D):** must-have or stretch? It is the only algorithm whose
   correctness argument is nontrivial; is the pedagogical payoff (the O(log n)
   memory curve in fig6) worth the page budget?
2. **Non-periodicity sketch (§8.4):** is the "derivative shortens the period"
   argument airtight as stated for *eventually* periodic words, or does it need the
   preperiod handled explicitly? What is the cleanest version at this audience level?
3. **Chvátal band in fig2:** the band is ±0.00084 while our curve will sit within
   ~±0.0003 of 1/2 at visible scales — does the band mislead more than it informs?
   Should Nilsson's reported ±0.00008 appear too, given it is second-hand?
4. **fig3's ±√n guide:** it is *not* a theorem (and the truth may be much smaller —
   A088568's plot suggests very slow growth). Keep with a loud disclaimer, or cut?
5. **Exercise X1** (Kolakoski-(1,3)): right capstone, or too far afield? Is the
   Perron–Frobenius "frequencies exist for primitive substitutions" chain
   (Baake–Sing + Allouche–Shallit) stated at the right level of rigor?
6. **Scope check:** anything listed above that should be cut to keep the lesson
   readable in one sitting? Anything essential missing?

---

## Appendix A — Changelog and review responses

| Version | Date | Summary |
|---|---|---|
| v1 | 2026-07-19 | Initial draft for round-1 review. |

*(Point-by-point response tables will be added here per round.)*
