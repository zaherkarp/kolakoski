# Round 3 — Review by "Dr. Salomé Vidal" (combinatorics on words / symbolic dynamics)

> **Disclosure.** Dr. Salomé Vidal is a **fictional reviewer persona executed as an AI
> subagent**, part of this teaching exercise's peer-review process (see PLAN.md §9).
> Round 3 is the post-implementation mathematical-accuracy audit frozen in PLAN v3
> §9/§11: hand-trace a generator, re-verify quantitative writeup claims by running
> the repo's own code, and re-derive both proven windows from scratch. Read-only on
> the repo; scratch work confined to scratch space.
>
> - **Round:** 3 · **Artifacts reviewed:** implementation at the current branch head
> - **Date:** 2026-07-19
> - **Author responses:** `docs/reviews/round3-responses.md`
>
> The review below is reproduced verbatim from the subagent's report, starting at its
> Verdict heading.

## Verdict
APPROVE WITH NITS — every number, proof, window, exercise key, and citation I could reach checks out against the shipped code and sources; the one defect of substance is a verification-provenance claim ("machine-checked in the test suite") that the test suite does not actually contain.

## Mandatory checks

### 1. Hand trace
Traced `kolakoski_expand` by hand to 15 terms, writing each state. w₀=[1,2]. rld(w₀,1): runs (1)(22) → w₁=[1,2,2], len 3. rld(w₁,1): lengths 1,2,2 alternating from 1 → (1)(22)(11) → w₂=[1,2,2,1,1], len 5. w₃: (1)(22)(11)(2)(1) → [1,2,2,1,1,2,1], len 7. w₄: (1)(22)(11)(2)(1)(22)(1) → len 10. w₅: (1)(22)(11)(2)(1)(22)(1)(22)(11)(2) → [1,2,2,1,1,2,1,2,2,1,2,2,1,1,2], len 15; lengths 2,3,5,7,10,15 = S(Lₖ) each step. I also traced `kolakoski_nilsson`'s chain: terms 1–3 hardcoded (runs (1)(22)); terms 4–15 are runs 3–10, lengths read from a parent instance after discarding its first two symbols — K[2..9]=2,1,1,2,1,2,2,1 → 11|2|1|22|1|22|11|2; bookkeeping says five generator instances are live at n=15 (level 4 suspended before spawning). Then ran the repo: `kolakoski_expand(15)`, `islice(kolakoski_nilsson(),15)`, and the replayed intermediate states all match my trace exactly. **Pass.**

### 2. Quantitative claims re-verified
All by importing `/home/user/kolakoski/kolakoski.py` (scripts in scratch `vidal-r3/`). One 10⁷-term pass over `kolakoski_gen`: ones(10⁶)=499,986 → d=0.499986; ones(10⁷)=5,000,046 → d=0.5000046 — sign flip confirmed. D extremes: **+189 at n=7,518,095; −154 at n=2,222,194**. Decade max |d−1/2| on (10⁶,10⁷]: **3.892106×10⁻⁵ at n=1,798,512** (exactly 70/1,798,512). `stream_stats(kolakoski_nilsson(),10⁷)` returned identical (5000046,−154,189) — cross-implementation agreement. Expand rounds via repo `rld`: **33 to clear 10⁶, 39 to clear 10⁷** (lengths 2,3,5,7,10,15,23,34,50,75,…). Live-level probe (fresh process, `gc.get_objects()` counting generators with `gi_code is kolakoski_nilsson.__code__` and live `gi_frame` after 10⁷ `next()` pulls): **39** — method disclosed since levels aren't introspectable otherwise. C4 mutants replayed: divergence at indices **2, 6, 3** as keyed. T5(b): k−2 form holds for all k≥2, tight at k=2; k−1 form fails exactly at k∈{1,2}. Bonus: A078880 b-file re-fetched, 10,000/10,000 = shift(K). **Pass.**

### 3. Windows re-derived
From scratch, then compared. *Prefix sums:* rle(K)=K forces run lengths ∈{1,2}, so no xxx; any 3 consecutive symbols contain a 1 and a 2; the ⌊L/3⌋ disjoint triples in positions 1..3⌊L/3⌋ give #2s(L) ≥ ⌊L/3⌋ and #2s(L) ≤ L−⌊L/3⌋; S(L)=L+#2s(L) ⟹ **L+⌊L/3⌋ ≤ S(L) ≤ 2L−⌊L/3⌋** — identical to §5B/writeup §4 (constants, floors, no side condition needed). *Run counts:* first m runs occupy S(m) positions; a length-L prefix (L≥1) with R runs satisfies S(R−1) ≤ L−1 and L ≤ S(R). Then L ≤ S(R) ≤ (5R+2)/3 ⟹ R ≥ ⌈(3L−2)/5⌉; and (4(R−1)−2)/3 ≤ S(R−1) ≤ L−1 ⟹ 4R ≤ 3L+3 ⟹ R ≤ ⌊(3L+3)/4⌋, which equals ⌈3L/4⌉ (checked case-by-case mod 4) — **⌈(3L−2)/5⌉ ≤ R(L) ≤ ⌈3L/4⌉**, matching writeup §4/PLAN §6 exactly, same route. My 10⁷ pass: 0 violations on both windows, min slack 0 on all four sides ("near-tight" is if anything understated), runs(10⁷)=6,666,660, zero triples. **Pass.**

Also all clear: §2 inventory and one-line shift proof (b-file re-check above); §4 non-periodicity proof re-read step-by-step — airtight as printed, the three named gaps are the right three; §5 table tags match the documented history (Chvátal limit-point logic (0.499,0.501) is valid given both letters <0.501; KR abstract re-fetched today, "assuming the limit exists" / "semi-rigorous" verbatim; Nilsson rational = 4403/55254326 ≈ 7.9686×10⁻⁵ ≤ 0.000080, outward); fig2's ink says "eventual bound" and puts only first-hand 0.499/0.501 on ink; fig1's 30 terms = exactly 20 complete runs (S(20)=30); fig3's ink matches the ledger; T2 is provable in three lines as posed (R=L forces all runs length 1, so w=1^L, which has one run unless L=1); OEIS A000002 re-fetched: Carpi comment, "unsolved problem" line, Oldenburger note all verbatim.

## Findings
1. **(major) False verification-provenance claim.** WRITEUP §2 ("machine-checked in the test suite", line 47) and §6A (line 206), plus `kolakoski.py:165`, claim the pointer invariant `rld(seq[:i],1)==seq` is machine-checked by the tests. It is not: `tests/test_kolakoski.py` (and conftest) contain no such check — the suite verifies outputs, never this loop-entry state. The invariant itself is true (my instrumented replay: 0 violations at every loop entry to n=2000). In a repo whose subject is claim discipline, a "verified" pointing at a nonexistent check must be fixed: add the six-line replay test, or reword to "checked during review".
2. **(minor)** §5 "agreeing to seven digits" (line 175) overstates: Nilsson's Table I prints four significant digits (3.892×10⁻⁵); the correct sentence is the one before it ("to the printed digit"). Say "to every digit the paper prints".
3. **(minor)** `kolakoski.py:286–288` pairs mismatched scales: "39 levels after 10⁷ terms, ~15 KB … vs ~17 MB for the stored tape" — 17 MB is the 10⁶-term tape (fig6 ink: ~1.7×10⁷ B at 10⁶, ~10⁸ B at 10⁷; writeup §6 states 10⁸ correctly).
4. **(minor)** The frozen fig2 spec requires the caption to disclose the clipped early transient (density(3)=1/3); the disclosure survives only as a `viz.py:204` comment — neither ink nor §5 prose says it.
5. **(minor, bundled)** (a) "rate provably in [3/5, 3/4]" (§6D and docstring) is the asymptotic rate — at L=1,2 the ratio R/L=1 exceeds 3/4; add "eventually" (the adjacent ceiling window is the finite-L truth). (b) §7 calls fig5's panels "the same prefix" — ink correctly says 8,100 vs 8,010 terms.

## Residual risks
Chvátal's finer digits: still second-hand (TR body unreachable) — correctly quarantined off-ink. Nilsson's N: not effective, so no plotted range is theorem-covered — scoped everywhere I looked, including fig2 ink. Brent 2⁶⁴ and Carpi: known only via OEIS comments (tagged [O]; comment re-fetched verbatim today). Memory figures (~16 KB / ~10⁸ B): machine- and measurement-dependent — Okafor's `--verify`/benchmark lane, not re-measured here. Monthly 1965/1966 page numbers: bibliographic data via OEIS, per their [O] tag, not independently fetched. My level probe counts generator frames, which presumes level=frame — same identification the docstring makes.
