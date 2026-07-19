# Round 1 — Review by "Dr. Salomé Vidal" (combinatorics on words / symbolic dynamics)

> **Disclosure.** Dr. Salomé Vidal is a **fictional reviewer persona executed as an AI
> subagent**, part of this teaching exercise's peer-review process (see PLAN.md §9). The
> persona was instructed to review adversarially, with hard minimum-findings quotas and a
> mandatory independent-verification section, and had read-only access to the repository
> plus permission to run throwaway verification code and fetch sources.
>
> - **Round:** 1 · **Artifact reviewed:** `PLAN.md` version 1 (commit `366d2d5`)
> - **Date:** 2026-07-19
> - **Author responses:** PLAN.md Appendix A (v2 entry)
>
> The review below is reproduced verbatim from the subagent's report.

## Verdict
REQUEST CHANGES — the ledger discipline is the right design, but §5B's "key lemma" is false as stated (counterexample at prefix length 257), and two ledger rows fail the ledger's own sourcing rule.

## Major issues

1. **[§5B] The quantitative clause of the key lemma is false.** For a K-prefix w, sum(w) ≥ ⌈3·len(w)/2⌉ − 1 is equivalent to D(n) := #1s − #2s ≤ 2 for all n ≤ len(w). It first fails at L = 257: sum(K[:257]) = 384 < ⌈3·257/2⌉ − 1 = 385 (D(257) = 3); by n = 7,518,095 the walk reaches D = 189. Nothing of this strength is provable today — it would be a spectacular discrepancy theorem. Worse, "(ratio → 3/2)" is the open density conjecture smuggled into an algorithm analysis. Fix: keep the structural half (rld(w,1) of a K-prefix is the concatenation of the first len(w) runs of K, hence a K-prefix of length sum(w) — this is correct; I traced it to L = 50). Replace the bound with the provable sum(w) ≥ len(w) + ⌊len(w)/3⌋ (every 3 consecutive symbols contain a 2, by no-111), plus sum(w) ≤ 2len(w) − ⌊len(w)/3⌋; a per-round factor in [4/3, 5/3] still yields Θ(log n) rounds. Say "conjecturally → 3/2". Propagate the same hedge to §5D's "~2/3 as fast" (provable: [3/5, 3/4]).

2. **[§3 Nilsson row] The sharpest-known-bound row is mislabeled "known (second-hand)" when the source is one download away — and the paper says something stronger than the plan does.** I read the Acta Phys. Pol. A PDF (it is openly accessible; "we could not read the PDF" is false as of today). It is a rigorous, unconditional bound, not a measurement: Table II lists upper bounds "induced by the graph G_d", ending u₃₄ = 455920839/911696379 ≈ 0.500080, with the sentence "Let us note here that we do not assume that the letter frequency exists," bounds holding "for all n larger than some N." Fix: upgrade to first-hand, record the exact rational, and verify the paper's *lower*-side table before printing "±0.000080" (I verified the upper side only). This blocks learning objective 4: as drafted, the writeup would name Chvátal as "best known rigorous bounds" when Nilsson's is better and rigorous.

3. **[§3 ledger vs §8.4/T4] Internal inconsistency on non-periodicity, and the sketch has real gaps.** The ledger stamps it "proven (easy)" while §8.4 and Q2 concede the argument needs care — pick one. The gaps for *eventually* periodic words: (i) "the period" must be the *minimal eventual* period or the descent proves nothing; (ii) the period block must be aligned at a run boundary beyond the preperiod (first excluding a constant tail — an infinite run contradicts run lengths ∈ {1,2}); (iii) "average run length > 1" needs an argument: rule out an all-runs-length-1 tail (12)^∞ because it would force rle(K) = K to have tail 1^∞, which contains 111. Clean half-page version: let p = minimal eventual period; align a block at a run boundary; with r = #runs in the block, p = sum of their lengths > r since some run has length 2 (by (iii)); rle(K) = K is then eventually periodic with period r < p, contradicting minimality. And do not print a knowingly gapped proof as main text: either give the full proof and make T4 "find and repair the two gaps in the v1 sketch (see Appendix A)" — the review history becomes teaching material — or mark the gap in place with "this step is unjustified; Exercise T4 fills it."

## Minor issues

1. [§3 informal def] "runs (blocks of equal symbols)" must say **maximal** blocks; otherwise rle is ill-defined — (1)(2)(2) also decomposes 1,2,2 into equal-symbol blocks, with lengths 1,1,1.

2. [§3 precise def] rle needs a domain condition: an eventually-constant infinite word has no run-length sequence in {1,2}^ℕ (last run infinite), so "the unique infinite word with rle(K) = K" quantifies over an unstated domain. Proposed wording: "For w ∈ {1,2}^ℕ not eventually constant, let rle(w) be its sequence of maximal-run lengths. K is the unique such w with w₁ = 1 and rle(w) = w; the one other infinite fixed point starts with 2 (A078880). Among finite words exactly ε and 1 are fixed." Surfacing ε and 1 here (not only in §5B) makes T2 exactly provable as posed.

3. [§8.2] "adjoint pair" is the wrong word and will mislead anyone who knows adjunctions. Under the prefix order rle is not even monotone: rle(12) = 11 and rle(122) = 12 are prefix-incomparable. What is true: w ↦ (w₁, rle(w)) and (s, ℓ) ↦ rld(ℓ, s) are mutually inverse bijections. Say "inverse pair, once the first symbol is carried along," and state the two identities with side conditions.

4. [§3 vs §8.5] Kupin–Rowland is used in the outline but absent from the ledger. Add the row with the verified statement (arXiv:0809.2776 abstract): "|freq₁(K) − 1/2| ≤ 17/762, assuming the limit exists", plus a "semi-rigorous" unconditional 1/46. The conditional-rigorous vs unconditional-semi-rigorous pair is a hedging-discipline exhibit — use it in §8.5.

5. [§3 + X1] The Baake–Sing paper's actual title is "Kolakoski-**(3,1)** is a (deformed) model set" (abstract: "its analogue on {1,3} can be related to a primitive substitution rule…"). The plan writes "(1,3)" throughout. Cite the real title, fix which start letter X1 implements, and replace "standard Perron–Frobenius theory" with a named theorem: primitivity ⟹ unique ergodicity ⟹ uniform letter frequencies exist (PF eigenvector computes them); pin the exact Allouche–Shallit/Queffélec theorem number at writeup time.

6. [§3 Chvátal row + fig2] (a) Provenance: Wikipedia states only "upper density of 1s < 0.50084"; the lower digit 0.49916 needs the 2s-side bound, which Wikipedia does not give. The TR abstract (archive.dimacs.rutgers.edu) states both upper densities < 0.501; the five-decimal digits are in the TR body — read it before printing them. (b) Semantics: these bound lim sup/lim inf only, so fig2's curve legitimately *exits* the band at small n (density(3) = 1/3). Draw/label the band as a constraint on limit points, not an envelope.

## Independent verification performed
Throwaway python3 (pointer generator to 10⁷) plus curl/fetch of sources; scratch files under vidal-r1/.

- **§5B refuted**: first violation L = 257 (sum = 384 < 385, i.e. first n with D ≥ 3); walk extremes to 10⁷: max D = 189 (n = 7,518,095), min D = −154 (n = 2,222,194); within 10⁶: +63/−66. Replacement bound sum ≥ L + ⌊(L−2)/3⌋ verified for all L ≤ 10⁷.
- **Ledger row 1 verified**: b000002.txt has exactly 10,502 data terms, all matching my independently written generator. Densities: 0.49960 (10⁴), 0.49972 (10⁵), 0.499986 (10⁶), 0.5000046 (10⁷).
- **A078880**: OEIS name "The sequence starting with 2 that equals its own run length sequence"; its 68 displayed terms equal my K with the first letter deleted — the sibling is exactly shift(K).
- **Carpi row verified**: OEIS comment verbatim: "The sequence is cubefree and all square subwords have lengths which are one of 2, 4, 6, 18 and 54 (see A294447) [Carpi, 1994]" (IPL 52 (1994) 289–294). My scan of the first 30,000 terms found square lengths exactly {2,4,6,18,54}, no cubes.
- **Nilsson 2014 read directly**: quotes in Major 2.
- **Chvátal TR abstract fetched**: "computations proving that the upper density of 1's as well as the upper density of 2[']s … is less than 0.501"; it attributes the question to Keane.
- **A088568** is defined as 3n − 2·(partial sums of A000002) = n − 2·#2s = D(n) exactly; its first terms match my walk. Its comments include Brent's |a(2⁶⁴)| = 836,086,974 ≈ 0.19·√(2⁶⁴) (used in Q4).

## Answers to the seeded questions (§11)
1. (partly my lane) Keep D as should-have: its level hierarchy is iterated rle made mechanical — the same structure the non-periodicity proof uses. Hedge its "~2/3" as in Major 1.
2. Not airtight; see Major 3 for the two genuine gaps and the minimal-eventual-period descent, which is the cleanest audience-level version. Full proof in the writeup; repurpose T4 as gap-hunting-in-v1.
3. Keep the Chvátal band, drawn as a limit constraint (right-edge bracket or explicit label), since the curve exits it at small n — the band-vs-wiggle mismatch *is* the lesson; say so in the caption. Nilsson: now verified rigorous and unconditional, so it may appear — but ±0.00008 is a hairline at fig2's scale; show it as an inset zoom or right-edge bracket with the exact rational. "0.501 → 0.500838 → 0.500080, limit still unproven" is exactly the story.
4. Keep, but fix the premise: "A088568's plot suggests very slow growth" is contradicted at scale — Brent's OEIS comment reports growth ~0.19·√n at n = 2⁶⁴ and calls the O(log n) conjecture "seems incorrect". So √n is the empirically right order with a small constant at small n (my max|D| = 63 at 10⁶ vs √10⁶ = 1000 — a raw ±√n envelope flattens the walk). Plot ±c·√n with c stated, caption "fair-coin-walk scale, no theorem either way", cite Brent/A289323.
5. Keep X1 as capstone with Minor 5's repairs; route the reading through Dekking 1997 (already in your refs) and Sing's survey, demoting Baake–Sing to "for the curious" (model sets/diffraction exceed this audience). With a named frequency theorem, the rigor level is right.
6. Math content is correctly sized; the one-evening risk is §5D+fig6, not the mathematics. Add to the round-3 mandatory checks: re-derive the corrected §5B bound.

## Suggested additions
- Ledger row for Kupin–Rowland (Minor 4) — conditional vs semi-rigorous is a hedging exhibit.
- One-line proposition in §8.2: the start-with-2 fixed point is shift(K) — deleting K's first letter deletes exactly its first run (length K₁ = 1), so rle(shift K) = shift(rle K) = shift(K). Verified against A078880. Demystifies "exactly two fixed points" and upgrades T2.
- Credit Keane with the density question in §8.3 (per Chvátal's abstract) — correct attribution.
- State D(n) = A088568(n) exactly (drop "up to sign convention"); add a structural test asserting the corrected prefix-sum bound to 10⁶.

## Proposed exercise
**T5 (●●○). Provable prefix-sum bounds, and what 3/2 would cost.** Let w = K[:L]. (a) Show every 3 consecutive symbols of K contain a 2 and a 1; deduce ⌊L/3⌋ ≤ #2s(w) ≤ L − ⌊L/3⌋, hence L + ⌊L/3⌋ ≤ sum(w) ≤ 2L − ⌊L/3⌋. (b) Conclude each §5B round multiplies prefix length by a factor in [4/3 − o(1), 5/3 + o(1)], so Θ(log n) rounds suffice — with no unproven input. (c) Show sum(w)/L → 3/2 is *equivalent* to the open density conjecture.
*Solution:* (a) partition positions 1..3⌊L/3⌋ into consecutive triples; an all-equal triple is a forbidden 111/222; count. (b) L_{k+1} = sum(w_k) ≥ (4L_k − 2)/3 gives L_k ≥ 2 + (4/3)^{k−1}; similarly above; take logs. (c) sum/L = 1 + #2s/L, and #2s/L → 1/2 iff #1s/L → 1/2.

## Questions for the author
1. Was §5B's bound meant only for the iteration lengths 2, 3, 5, 7, 10, 15, …? Even so restricted it is unproven (it encodes D(L_k) ≤ 2); if you believe you have a proof, show it in v2 — otherwise adopt the 4/3 bound.
2. Does Nilsson 2014 give the matching lower bound (> 0.499920) that your "±0.000080" implies? I verified only the upper table.
3. Will the ledger carry exact rationals (455920839/911696379, 17/762) beside outward-rounded decimals, so rounding direction is checkable?
4. Who reads Chvátal's TR body (the .ps on the DIMACS archive) to confirm 0.500838/0.499162 for both letters before v3 freezes?
5. Is "logarithmic space … linear time" verbatim from JIS 12.6.7? The arXiv version (1110.4228) is free — verify before quoting.
