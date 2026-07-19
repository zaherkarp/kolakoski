# Round 2 — Review by "Dr. Emeka Okafor" (computational mathematics / scientific software)

> **Disclosure.** Dr. Emeka Okafor is a **fictional reviewer persona executed as an AI
> subagent**, part of this teaching exercise's peer-review process (see PLAN.md §9).
> Round 2 audits whether the author's round-1 dispositions actually landed in PLAN v2,
> and sweeps v2 for new defects. Read-only access plus throwaway measurement code.
>
> - **Round:** 2 · **Artifact reviewed:** `PLAN.md` version 2 (commit `d92e03c`,
>   re-authored as `2b8c5c1` with identical content)
> - **Date:** 2026-07-19
> - **Author responses:** PLAN.md Appendix A (v3 entry)
>
> The review below is reproduced verbatim from the subagent's report, starting at its
> Verdict heading.

## Verdict
REQUEST CHANGES — every round-1 major landed and re-verified, but two v2-introduced defects must be fixed before freeze: the PNG-mtime drift guard is unsound under git (it fails on every fresh clone), and §6/§11's oracle constants contradict the plan's own §5D (2/5 where the provable constant is 3/5); both are small, targeted edits.

## Disposition audit
| R1 point | Landed? |
|---|---|
| M1 §5B bound | **YES** — window L+⌊L/3⌋ ≤ S(L) ≤ 2L−⌊L/3⌋ re-verified: 0 violations to 10⁷, attained on both sides (L=1, L=3), so stated tightly; 33/39 rounds quoted and reproduced. |
| M2 §5A invariant | **YES** — `rld(seq[:i],1)==seq` re-checked at every loop entry to 40 terms; seed step `rld([1,2],1)=[1,2,2]` correct; truncation and n ≤ 3 now specced. |
| M3 fig6 streaming | **YES** as specced (STREAM_METHODS + stream_stats in §5/§7), but the contract v2 added is underspecified → Finding 3. |
| M4 oracle vacuity | **PARTIAL** — fix present and non-vacuous, but A.1's justification ("0.72 justified by the now-proven ≤ 3/4 ratio bound") is backwards: 0.72 < 3/4, so the proven bound cannot justify it, and r/L = 8/11 ≈ 0.727 > 0.72 at L=11 — 0.72 is an n-specific empirical pin (§6's own "clears ≈ 2/3 with margin" is the honest framing). Response mischaracterizes the epistemic status; no other response misstates me. |
| m1–m5 | **YES** — separate passes + whiskers + grid; corridor→lines; 1,250 bins linear-x (10⁷/1250 = 8,000/bin checks); requirements.txt pins landed *with* an honest scope comment (diff read); density row now measured, numbers match mine exactly. |
| m6 drift guard | **PARTIAL** — guard added to spec, mechanism unsound → Finding 1. |
| Q1/add-1..4/C4/my-Q2 | **YES** — Nilsson must-have with dependency chain; stream_stats (contract gap aside); grid/pins/verify chain; C4 divergences 2/6/3 re-verified; `tools/crosscheck_oeis.py` in deliverables + ledger. |
| Q4 guide (PARTIALLY REJECTED) | Adjudication **accepted** — see answers below. |

## Findings
1. **(major, §7/Makefile spec)** The "fail if any committed PNG is older than `viz.py`" guard cannot work: git does not preserve mtimes. Demonstrated on a fresh clone of this repo — all files get checkout-time mtimes assigned in path-sorted order (measured: `Makefile` 04.560032s < `docs/…` 04.562505s < `requirements.txt` 04.564427s, pure alphabetical). Since `figures/*` sorts before `viz.py`, **every fresh clone fails `make verify` spuriously**; conversely a branch switch that rewrites `viz.py` refreshes its mtime and fails a consistent tree. Fix: drop mtime; have `make verify` render figs 1–5 to a temp dir and byte-compare against the *committed* PNGs — this also closes a real gap in `--verify` as specced (render-twice checks self-determinism but never ties committed PNGs to current `viz.py`).
2. **(major, §6/§11 Q4)** The proposed two-sided window's lower constant is wrong. Deriving from the proven prefix-sum bounds with r = len(rle(K[:L])) = min{m : S(m) ≥ L}: L ≤ S(r) ≤ (5r+2)/3 gives **r ≥ (3L−2)/5**, and L−1 ≥ S(r−1) ≥ (4(r−1)−2)/3 gives r ≤ (3L+3)/4, i.e. exactly ⌈3L/4⌉. So the window is **⌈(3L−2)/5⌉ ≤ r ≤ ⌈3L/4⌉** — upper as proposed is exactly right; lower is 3/5, not 2/5 (⌊2L/5⌋ is slack by ~L/5 ≈ 20,000 runs at L=10⁵). §5D already states the inverse rate [3/5, 3/4]; §11 Q4 contradicts it. Verified: corrected window has 0 violations for all L ≤ 10⁷ and is near-tight (min 5r−3L = 0, max 4r−3L = 2). Adopt it in §6, drop 0.72 or relabel it "empirical pin, like the density check", and fix A.1 M4's justification sentence.
3. **(minor, §5/§7)** `stream_stats(it, n)` has no return contract (tuple? fields? is n an exact pull count?), registry membership is unstated (§6's "at 10⁵ (all)" implies Nilsson is comparable through METHODS, but §5D defines it as a generator), and the timing pass's consumer for streams is unspecified. Pin: METHODS = {pointer, expand}, STREAM_METHODS = {gen, nilsson}; `stream_stats` pulls exactly n terms and returns (count_1s, min_D, max_D); left panel times streams through the same consumer. Then fig6's two families are comparable at each n and the caption can state the one deliberate asymmetry (list output counted vs not).
4. **(minor, §5B)** Expand lacks the stop/truncate/edge sentence A gained: state "iterate until len(w) ≥ n, return w[:n]; n ≤ 2 served from the seed."
5. **(minor, §7)** State fig6's measured budget: ~30 s timing pass + ~80 s traced memory pass ≈ 2 min total (see below), and that the memory pass is a single run (peaks don't need min-of-3).

Regression sweep: pins are fine — requirements.txt itself carries the "any recent versions work except byte-identity" caveat; echo it in README's quickstart and record Python 3.11 in §7's environment scope. Nothing else regressed.

## Independent verification performed
All on this machine (Python 3.11.15, numpy 2.4.6, mpl 3.11.1 — matching the new pins).
- Regenerated K to 10⁷ (pointer); expand reproduces it exactly to 10⁷; no `xxx` triple in 10⁷ terms; sum(K[:257]) = 384 still refutes v1.
- Prefix-sum window: 0 violations to 10⁷; equality hit once per side. Inverse window: r(L) computed for all L ≤ 10⁷ via searchsorted on cumsum, spot-checked against direct rle; ⌈(3L−2)/5⌉ ≤ r ≤ ⌈3L/4⌉ has 0 violations; r(10⁵) = 66,652 (0.6665); max r/L = 0.7273 at L=11.
- Ledger numbers: density 0.499986 / 0.5000046; D extremes +63 @ 334,915 / −66 @ 97,502 (10⁶) and +189 @ 7,518,095 / −154 @ 2,222,194 (10⁷) — all exact matches. Nilsson: 455920839/911696379 − 1/2 = 4403/55254326 = 7.9686×10⁻⁵ ≤ 0.000080.
- fig3 geometry: guide 0.2√10⁷ = 632.5; walk spans 343 of 1,265 y-units = **27.1%** of the axis (v1 c=1@10⁶: 6.5%); guide/walk-max 3.35× (was 15.9×).
- Mutants diverge at 2, 6, 3; §5A invariant holds to 40 terms; mtime clone experiment as in Finding 1.
- fig6 inputs @10⁷: pointer 2.10 s, expand 2.96 s, gen 1.24 s, nilsson 2.61 s; traced pointer(10⁶) 1.04 s; streamed nilsson peak 14.7 KB vs 16.8 MB list.

## Answers to §11 round-2 questions (your lane: Q3; briefly Q1)
**Q3:** After Findings 2–4 are applied, no — §5 is implementable: the invariant is machine-checkable, edges are pinned, and the [4/3, 5/3] / [3/5, 3/4] windows are mutually consistent and verified. The remaining traps were exactly the stream contract, the §5B edge sentence, and the drift guard. **Q4 (mine by content):** adopt the corrected window of Finding 2. **fig3 adjudication:** I accept c = 0.2 — at 27% axis occupancy the walk is visible, not buried; the constant is principled (Brent's 0.19), and the caption discipline is specced. Nit: label the guide "±0.2√n" on the line itself. **Q1 (brief):** keep the inset — my round-1 objection was to *second-hand* numbers on ink, and Nilsson is now first-hand; worst in-decade deviation ≈ 3.5×10⁻⁵ (n ≈ 2.22M) fills ~44% of the ±8×10⁻⁵ band, so it reads well; keep Chvátal's lines out of the inset (off-scale by 12×).

## Freeze recommendation
Do not freeze as-is; apply the edits for Findings 1–4 (all localized, no new machinery) and v3 may then freeze without a further review round.
