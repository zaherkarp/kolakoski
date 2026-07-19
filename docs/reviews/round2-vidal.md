# Round 2 — Review by "Dr. Salomé Vidal" (combinatorics on words / symbolic dynamics)

> **Disclosure.** Dr. Salomé Vidal is a **fictional reviewer persona executed as an AI
> subagent**, part of this teaching exercise's peer-review process (see PLAN.md §9).
> Round 2 audits whether the author's round-1 dispositions actually landed in PLAN v2,
> and sweeps v2 for new defects. Read-only access plus throwaway verification code and
> source fetches.
>
> - **Round:** 2 · **Artifact reviewed:** `PLAN.md` version 2 (commit `d92e03c`,
>   re-authored as `2b8c5c1` with identical content)
> - **Date:** 2026-07-19
> - **Author responses:** PLAN.md Appendix A (v3 entry)
>
> The review below is reproduced verbatim from the subagent's report.

## Verdict
APPROVE WITH NITS — every load-bearing mathematical claim in the v2 body of /home/user/kolakoski/PLAN.md survived independent re-derivation and recomputation to 10^7, but §6's vacuity-fix constant is justified backwards in A.2/A.1, and two response-table rows misstate what round 1 said or endorsed.

## Disposition audit
| R1 point | Landed? |
|---|---|
| M1 §5B window | YES on math (verified 0 violations to 10^7, both sides sharp: min slack 0). PARTIAL on the response: A.2-M1 calls my "⌊(L−2)/3⌋ variant" cautious and credits the strengthening to the author — but M1 and T5(a) proposed L+⌊L/3⌋ with the disjoint-triples proof verbatim; (L−2)/3 appeared only in my verification log. Mischaracterization, no damage. |
| M2 Nilsson upgrade | YES. I re-read the [PDF](http://przyrbwn.icm.edu.pl/APP/PDF/126/a126z2p31.pdf): the ledger's sup-display is verbatim from p. 552. |
| M3 non-periodicity | YES — ledger "proven (with care)"; §8.4 proof re-checked step-by-step (the (12)^∞ exclusion and the fact that run boundaries propagate p-periodically, so every block copy aligns, both hold). Residual: objective 2 still calls it one of the "two easiest structural facts". |
| m1–m3, m4–m6 | YES all six (counterexamples retained correctly; KR row with right arXiv ID; (3,1) renamed; Chvátal provenance honest). |
| add-1..4 | YES (I re-matched A078880's b-file against shift(K): 10,000/10,000). |
| T5 | PARTIAL — exercise landed, but "her solution sketch checks out" is false at the start: L_k ≥ 2+(4/3)^{k−1} fails at k=1,2 (L₁=2<3, L₂=3<10/3). Correct: L_k ≥ 2+(4/3)^{k−2} for k≥2, tight at k=2 (verified to 10^7). My slip; the re-verification policy should have caught it. |
| her Q1/Q3/Q4/Q5, fig3 | YES answered/adopted. Q5 nit: A.2 describes §5D as carrying an ellipsized quote; §5D carries the longer un-ellipsized fragment (which I re-verified is a verbatim substring of the [JIS abstract](https://cs.uwaterloo.ca/journals/JIS/VOL15/Nilsson/nilsson5.html)). |

**Counter-claims.** (a) Correct mathematics, wrong provenance: partition positions 1..3⌊L/3⌋ into disjoint triples; a one-letter triple is a forbidden 111/222, so #2s ≥ ⌊L/3⌋ and #1s ≥ ⌊L/3⌋; S = L + #2s gives the window. That is my M1/T5(a) argument, not a strengthening of it. (b) Confirmed: the paper displays sup_{n≥N} |o_n/n − 1/2| ≤ 455920839/911696379 − 1/2 ≤ 0.000080 with the absolute value, plus "we do not assume that the letter frequency exists" — the lower side is inside the display; my Q2 is answered by the source.

## Findings
1. **(major) §6's length-shrink constants: the stated justification inverts the implication, and Q4's proposed window is weaker than trivial.** A.1-M4 says 0.72 is "justified by the now-proven ≤ 3/4 ratio bound" — backwards: 0.72 < 0.75, so the theorem cannot justify it; 0.72 is only an empirical margin over the conjectural 2/3 (measured max R/L = 0.66848 for L ≥ 10^3). And the offered lower constant ⌊2L/5⌋ is weaker than the trivial ⌈L/2⌉ (runs have length ≤ 2), never tight (measured slack grows ~0.27L), while §5D itself already states the correct rate 3/5. Fix in Q4 answer below.
2. **(minor)** A.2-M1 provenance mischaracterization (audit table).
3. **(minor)** A.2-T5 "checks out" endorsement of an off-by-one closed form (audit table); the writeup's T5(b) key must use the k−2 exponent.
4. **(minor) fig2 spec gaps.** Main-panel y-range is unstated; on any range containing the early transient, the 0.499/0.5/0.501 lines are ~2 px apart at 150 dpi — pin y-limits (e.g. [0.47, 0.53], early curve clipped, captioned). And Nilsson's bound holds only "for n ≥ some N ≥ 1", N not effective in the paper — the inset lines need the same eventual-bound scoping as Chvátal's, and the ledger row should say "for some N (not effective)".
5. **(minor, bundled nits)** Objective 2 "easiest" vs ledger "(with care)"; "a fortiori" in the Baake–Sing row should be "hence"; her-Q5 row misdescribes §5D's quote form.

## Independent verification performed
Fresh generator (scratch, vidal-r2/), 10^7 terms; [Nilsson 2014 PDF](http://przyrbwn.icm.edu.pl/APP/PDF/126/a126z2p31.pdf) and JIS page fetched; b078880.txt downloaded.
- §5B window: 0 violations either side to 10^7; min slacks 0/0 (sharp at L=1, L=3). No 111/222 window in 10^7 terms.
- v1 bound: first failure L=257 (S=384<385, D=3); 563,998 violations ≤ 10^6, matching A.1-M1 exactly (equals #{D≥3} since D ≡ L mod 2).
- D extremes +63/−66 (10^6), +189 at 7,518,095, −154 at 2,222,194; densities 0.499986 / 0.5000046 — all match the ledger.
- Run counts: derived and checked ⌈(3L−2)/5⌉ ≤ R(L) ≤ ⌈3L/4⌉, 0 violations to 10^7, both sides attained; R(10^5)=66,652 (0.6665n, so the 0.72 test does pass empirically).
- Expand rounds from [1,2]: 33 to ≥10^6, 39 to ≥10^7 (lengths 2,3,5,7,10,15,23,34,...); corrected T5(b) form holds ∀k≥2, original fails at k=1,2. D at iteration lengths reaches −84, so even my Q1's restricted v1-bound is empirically dead (and my round-1 Q1 misprinted the lengths as "...,22,33,...").
- Nilsson: u₃₄ − 1/2 = 4403/55254326 ≈ 7.9686×10^−5 ≤ 0.000080 (outward, correct); display quoted verbatim above. Cross-corroborations: his Table I gives 39 pointers at 10^7 (= §5D's 39 levels; my run-count chain gives 38 transitions + level 0), o(10^7) = 5,000,046, and decade deviation 3.892×10^−5 — my max |density−1/2| on (10^6,10^7] is 3.892106×10^−5 at n = 1,798,512, an exact match.
- A078880 b-file = shift(K) for all 10,000 terms. rle/rld hand vectors and rle(12)=11 vs rle(122)=12 incomparability re-checked.

## Answers to §11 round-2 questions (your lane: Q1, Q2, Q4)
**Q1.** Not overloaded — main panel plus inset is right. Three conditions: pin the main-panel y-range (Finding 4, else the Chvátal lines are sub-pixel); scope both line families as limit-point/eventual bounds (Nilsson's N is not effective, so the inset must not claim the theorem covers the plotted decade); the measured max deviation in the inset decade is 49% of the corridor half-width and equals Nilsson's own Table I entry — cite that coincidence in the caption as a free cross-check.

**Q2.** Honest and sound, not too self-referential: gap-hunting a genuinely flawed proof with the correct proof in main text is exactly how referees are trained, and the AI-persona disclosure adjacent to the quoted sketch keeps provenance clean. Two guards: T4 should name deliverables (identify gaps (i)–(iii), repair each, cross-reference §8.4), and the key should accept extra legitimate gaps (e.g. why boundary-alignment persists across all block copies).

**Q4.** Neither as offered. Assert the provable two-sided window ⌈(3L−2)/5⌉ ≤ len(rle(K[:L])) ≤ ⌈3L/4⌉ for all L ≤ 10^6. Derivation: a length-L prefix with R runs satisfies sum(K[:R−1]) ≤ L−1 and L ≤ sum(K[:R]); apply the §5B window: 4(R−1)−2 ≤ 3(L−1) gives R ≤ ⌈3L/4⌉, and 3L−2 ≤ 5R gives the lower side. It is a theorem (no magic 0.72), tight, catches rle=identity at every L ≥ 4, catches run-merging bugs from below, and matches §5D's [3/5, 3/4] rates. The 0.72 one-sided test may stay only if relabeled "empirical margin over conjectural 2/3" — its current justification is unsound.

## Freeze recommendation
v3 may freeze after the listed edits (§6 window + A.1-M4 justification, A.2-M1/T5 response rows, fig2 y-range and eventual-bound scoping, T5(b) exponent, plus the bundled nits) — all localized, none architectural, no re-review needed if the diff is confined to them.
