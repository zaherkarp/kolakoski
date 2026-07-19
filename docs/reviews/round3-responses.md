# Round 3 — Author responses and fixes

Both round-3 audits returned **APPROVE WITH NITS** with every mandatory gate
passing (31/31 tests → now 33/33; `viz.py --verify` byte-identical; all
hand-traces, window re-derivations, and quantitative re-verifications in
agreement with the shipped code). The findings below were fixed in the same
commit that adds this file. Per the standing policy, each reviewer claim was
re-confirmed by the author before the fix was applied — all were accurate.

## The converged major (Okafor F1 ≡ Vidal F1)

**Finding.** `kolakoski.py`, WRITEUP §2 and §6A claimed the pointer loop
invariant `rld(seq[:i], 1) == seq` is "machine-checked in the test suite" —
and no such test existed. Both reviewers, independently, called out the same
false provenance claim; both confirmed the invariant itself is *true* by
instrumented replay.

**Decision: ACCEPTED — the test was added, making the claim true rather than
weakening it.** `tests/test_kolakoski.py::test_pointer_loop_invariant`
replays the pointer algorithm transparently, asserts the invariant at every
loop entry to n = 2,000, and ties the replay to the shipped function by
output equality (the tie is what makes a replay-based invariant check
meaningful — a concern Okafor raised in his mutant analysis). The docstring
wording is unchanged and now accurate.

That the repo's one substantive round-3 defect was a *false claim about
verification itself*, in a project about claim discipline, is an irony we
choose to display rather than bury.

## Other findings

| Finding | Decision | Fix / note |
|---|---|---|
| Okafor F2 / Vidal F4 — fig2's frozen spec required an on-ink clipping disclosure; none existed | **ACCEPTED** | fig2 gains a fine-print line ("y-axis clipped to [0.47, 0.53] and x starts at n = 10 — the earliest densities exit the frame (density(3) = 1/3)"); WRITEUP §5 discloses it in prose too. fig2 re-rendered; `--verify` re-run green. |
| Okafor F3 / Vidal F3 — module docstring paired a 10⁷ memory number with a 10⁶ one | **ACCEPTED** | Docstring now reads "~16 KB … vs ~17 MB (at 10⁶) and ~10⁸ bytes (at 10⁷)". **Disclosed deviation from frozen v3 wording:** PLAN §5D carries the original mixed-scale sentence; the plan is frozen, so it is corrected here and in the module rather than by rewriting v3. |
| Okafor F4 — no-triples assertion routed through `rle`, vacuous under an identity-`rle` mutant | **ACCEPTED** | `test_alphabet_and_no_triples` now scans the raw bytes directly (`b"\x01\x01\x01"` / `b"\x02\x02\x02"` must not occur); the rle phrasing is kept as a second, labeled non-independent check. |
| Okafor F5 — `_demo` claimed testability, untested | **ACCEPTED** | `test_demo_output` added (first terms + live self-check reports "yes"). |
| Okafor F6 — `stream_stats` silently under-consumes a short iterator | **ACCEPTED** | Docstring caveat added (islice semantics; stats cover what came out). |
| Vidal F2 — "agreeing to seven digits" overstated Nilsson's four printed digits | **ACCEPTED** | Now "to every digit the paper prints", with the exact rational 70/1,798,512 added. |
| Vidal F5a — "[3/5, 3/4] rate" needs "eventually" (R(1)/1 = 1) | **ACCEPTED** | "Eventually" + pointer to the exact finite-L window, in both the docstring and WRITEUP §6D. |
| Vidal F5b — WRITEUP §7 called fig5's panels "the same prefix" (8,100 vs 8,010 terms) | **ACCEPTED** | Now "nearly the same prefix — 8,100 / 8,010 terms", with the reason (each panel fills its rectangle exactly). |

## Post-fix state

- Test suite: **33 passed** (~2 s), including the two new tests.
- `python3 viz.py --verify`: **PASS** — figs 1–5 byte-identical to the
  committed renders (fig2's committed PNG is the new, disclosed render),
  all six under the size budget.
- Residual risks stand as both reviewers recorded them (pinned-environment
  byte-identity will age; Chvátal's finer digits remain second-hand; Brent
  and Carpi claims are cited via OEIS comments and tagged accordingly;
  benchmark numbers are machine-dependent).
