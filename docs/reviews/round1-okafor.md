# Round 1 — Review by "Dr. Emeka Okafor" (computational mathematics / scientific software)

> **Disclosure.** Dr. Emeka Okafor is a **fictional reviewer persona executed as an AI
> subagent**, part of this teaching exercise's peer-review process (see PLAN.md §9). The
> persona was instructed to review adversarially, with hard minimum-findings quotas and a
> mandatory independent-verification section, and had read-only access to the repository
> plus permission to run throwaway measurement code.
>
> - **Round:** 1 · **Artifact reviewed:** `PLAN.md` version 1 (commit `366d2d5`)
> - **Date:** 2026-07-19
> - **Author responses:** PLAN.md Appendix A (v2 entry)
>
> The review below is reproduced verbatim from the subagent's report, starting at its
> Verdict heading.

## Verdict
REQUEST CHANGES — the plan's architecture is sound, but §5B's key lemma is numerically false, §5A's stated invariant fails at loop entry, the fig6 memory panel cannot show its own payoff as specced, and the "independent" structural oracle passes vacuously for identity `rle`; all four are fixable in v2.

## Major issues

1. **[§5B] The key lemma's inequality is false.** `sum(w) ≥ ⌈3·len(w)/2⌉ − 1` first fails at the 257-term prefix of K: `sum = 384`, bound `= 385`. It fails for 563,998 of the first 10⁶ prefix lengths (56% — not an edge case; it fails whenever the discrepancy walk exceeds +2, which is most of the time). Worse, the "(ratio → 3/2)" framing quietly assumes the open density conjecture the repo is about. Fix: use `sum(w) ≥ len(w) + ⌊len(w)/3⌋` — it follows from the already-proven no-`111` fact (any 3 consecutive symbols contain a 2), I verified 0 violations to 10⁶ (tight at m=1), and ratio ≥ 4/3 still gives Θ(log n) rounds. Measured round counts: 33 to reach 10⁶, 39 to reach 10⁷ — quote these in the writeup.

2. **[§5A] The stated invariant is false at loop entry, and the spec omits truncation and n ≤ 3.** At entry (`seq=[1,2,2]`, `i=2`), the runs described by `seq[:i+1] = [1,2,2]` concatenate to `[1,2,2,1,1]` ≠ `seq` — the seed encodes only the runs dictated by `seq[0]` and `seq[1]`; `seq[2]` is unconsumed. The "(or is being used)" hedge makes the invariant unfalsifiable at any program point. The true invariant, which I verified at every loop entry to n=30: `rld(seq[:i], 1) == seq`. Separately: appending whole runs overshoots (n=4 produces length 5), and for n ∈ {0,1,2,3} the loop never runs, so without an explicit `return seq[:n]` the function returns 3 terms for n=0. §6 promises to test those edges; §5A must define them.

3. **[§5D + §7 fig6] The registry contract `f(n) -> list[int]` destroys fig6's memory payoff.** If Nilsson is benchmarked through that interface, tracemalloc measures the output list: I measured 8.5 MB materialized vs **9.1 KB** streaming at n=10⁶ (pointer: 16.8 MB). As specced, the right panel shows three O(n) curves and the lesson's climax evaporates. Fix: the memory pass must consume the generator streaming (running count/density, nothing retained); give the registry a `mode="list"|"stream"` field or benchmark generators separately.

4. **[§6] Oracle 3 and the round-trip test cannot fail for identity implementations — `rle` correctness is never pinned.** I checked: with buggy `rle = identity` and `rld = lambda L, f: L`, both `rld(rle(w), w[0]) == w` and "`rle(K[:n])` is a prefix of K" pass (K is a fixed point of `rle`, and identity fixes everything). So the "structural" oracle silently degenerates to oracle 2. Fix: hardcode a few `rle`/`rld` vectors (e.g. `rle([1,2,2,1,1]) == [1,2,2]`) and assert `len(rle(K[:n])) ≈ 2n/3 < n`, which identity cannot satisfy.

## Minor issues

1. **[§7 fig6] Never time under tracemalloc.** Measured overhead on this machine: pointer(10⁶) takes 1.20 s traced vs 0.14 s untraced — **8.5×**, not a perturbation. Spec must say: separate passes for time and memory. Also "best of 3": min-of-k is defensible for CPU-bound loops, but report the spread (e.g. min with min–max whiskers) and state the n-grid in the caption.

2. **[§7 fig2] The Chvátal band drawn as a filled corridor misleads.** Chvátal bounds lim inf/lim sup, not finite-n densities; the curve sits outside the band for small n (density(3) = 1/3) yet the shading visually asserts a corridor for all n. Draw two labeled horizontal lines ("bounds on lim inf/lim sup"), state y-limits and the x-start explicitly.

3. **[§7 fig3] "Per pixel column" is underdetermined** — column count depends on figsize/dpi/margins, none pinned. Fix a data-side bin count (e.g. 1,000 bins → ~1,000 points/bin at 10⁶) decoupled from rendering, and state x-scale (linear vs log changes the banding entirely).

4. **[§7/§4] Scope the byte-identical claim and pin versions.** Verified: two separate-process renders hash identically here (mpl 3.11.1, Agg). But the PNG embeds `Software: Matplotlib version 3.11.1`, and requirements.txt says `matplotlib>=3.8` — any version bump or another machine's freetype changes bytes. `--verify` (same-env, render-twice) is the right gate; pin exact versions in requirements.txt and say the claim is per-environment, or committed PNGs will diff spuriously under review.

5. **[§3] Ledger discipline slip:** the density row is labeled **verified** before the numbers exist. Label it "to-measure". (For v2: I measured density(10⁶) = 0.499986, density(10⁷) = 0.5000046 — note the sign of the deviation flips, a nice caption fact.)

6. **[§10] Figure-drift gap:** step 9 (writeup/README) can touch `viz.py` after step 8 committed the PNGs, with no re-render gate before push. Add: any commit touching `viz.py` must include regenerated `figures/` and a passing `make verify` (a make rule can fail if any PNG is older than `viz.py`). Assign `--verify` explicitly to me in round 3.

## Independent verification performed
All on this machine, CPython 3.x, matplotlib 3.11.1.

- **§5B refuted:** generated K by pointer method; `sum(K[:257]) = 384` (#1=130, #2=127) vs claimed bound `⌈3·257/2⌉−1 = 385`; 563,998 violations for m ≤ 10⁶. Replacement bound `m + ⌊m/3⌋`: 0 violations.
- **§5A entry state:** `rld([1,2,2],1) = [1,2,2,1,1] ≠ [1,2,2]`; corrected invariant `rld(seq[:i],1)==seq` held at every iteration to n=30.
- **Nilsson prototype (~10 lines, recursive lazy chain):** first 20 terms match; **39 levels** instantiated after 10⁷ pulls (log₁.₅ 10⁷ = 39.8 — §5D's 2/3-per-level claim confirmed); streaming tracemalloc peak 9.1 KB vs 8.5 MB materialized.
- **Timings:** pointer(10⁶) 0.14 s, pointer(10⁷) 1.50 s, expand(10⁶) 0.24 s, expand(10⁷) 3.00 s, generator 10⁶ pulls 0.33 s → §6's 10 s suite budget and fig2's 10⁷ are comfortably feasible.
- **Determinism probe:** identical figure rendered in two separate processes → same SHA-256 (`2655…93f2`); only metadata chunk is the mpl version string.
- **Broken-variant divergence:** seed `[1,2]`/i=1 diverges at index 2; i=1 off-by-one at index 6; alternation-parity at index 3 — the 300-term OEIS oracle catches this whole bug class with two orders of magnitude to spare.

## Answers to the seeded questions (§11)
- **Q1 (Nilsson): must-have.** Evidence: my prototype is ~10 lines, the depth claim checks out exactly (39 levels at 10⁷), and the payoff is 9.1 KB vs 16.8 MB — 3+ orders of magnitude, the most striking empirical plot in the repo. Moreover the plan already hard-depends on it three times: learning objective 5, fig6's right panel, and exercise C1 (density at 10⁸ in O(log n) memory) is **unsolvable** without it — "demote by deleting one line" is false as stated. Keep it; budget one page; require the streaming benchmark harness (Major 3).
- **Q3 (Chvátal band):** keep, but as two labeled boundary lines, not a filled corridor (Minor 2). Omit Nilsson's ±0.00008 from the figure — a plot gives second-hand and verified data equal visual authority, which your own ledger forbids; put it in the caption as "reported".
- **Q4 (±√n guide): cut it.** Measured: max D(n) = 63 (n=334,915), min = −66 over n ≤ 10⁶, while √10⁶ = 1000 — the guide inflates the y-axis ~15× and flattens the walk into the very line the figure wants the reader to marvel at. State "extremes ±66 at 10⁶; compare √n = 1000" in the caption instead.
- **Q6 (scope, my lane):** cut nothing algorithmic — all of §5 costs < 0.35 s at 10⁶ (measured). But declare the D-dependency chain explicitly (objective 5, C1, fig6) so the should-have contingency is honest.

(Q2, Q5 are Dr. Vidal's lane; I defer.)

## Suggested additions
- A `stream_stats(gen, n)` helper (count of 1s, running extremes, no storage) — it is the honest consumer for fig2/fig6 at 10⁷–10⁸ and the solution scaffold for C1.
- State the fig6 n-grid in the plan (e.g. n = 10³…10⁷, ×10) so reviewers can pre-compute the budget (~35 s at best-of-3, measured rates).
- Pin exact `numpy`/`matplotlib`/`pytest` versions (Minor 4) and record them in fig6's caption.
- A one-line CI-style make target chaining `test` → `figures` → `--verify` → PNG-mtime check (Minor 6).

## Proposed exercise
**C4 — "Break the generator, then catch it" (mutation testing)** · difficulty ●●○. Give students three sabotaged pointer variants: (a) seed `[1,2]` with i=1, (b) seed `[1,2,2]` with i=1, (c) alternation parity flipped at the seed boundary. Task: predict which test in the suite catches each mutant and at which index the output first diverges from K; then run the suite to check. *Solution (verified):* first divergences at indices **2, 6, 3** respectively; the hardcoded-OEIS oracle catches all three; `test_methods_agree` catches them only while some method stays unmutated; the structural `rle` oracle misses (c)'s cousin `rle=identity` entirely — which is the punchline connecting to Major 4: oracles have blind spots you can map.

## Questions for the author
1. fig6 memory panel: will you adopt a streaming consumer for D (Major 3), and if so what interface does `METHODS` expose for it?
2. Is the b-file cross-check reproducible — will the checker script (network-marked, skipped offline) be committed, or does the 10,502-term claim stay a dev-time anecdote in a comment?
3. For fig3, linear or log x? The min/max banding spec differs materially between the two.
4. §5B's writeup: do you want the 4/3 bound proof inline (it is two sentences from no-`111`) or as exercise T3's warm-up?
