# Round 3 — Review by "Dr. Emeka Okafor" (computational mathematics / scientific software)

> **Disclosure.** Dr. Emeka Okafor is a **fictional reviewer persona executed as an AI
> subagent**, part of this teaching exercise's peer-review process (see PLAN.md §9).
> Round 3 is the post-implementation engineering audit frozen in PLAN v3 §9/§11:
> run the suite, audit an oracle with mutants, probe a complexity claim empirically,
> and own the `viz.py --verify` gate. Read-only on the repo; mutants and instrumented
> copies confined to scratch space.
>
> - **Round:** 3 · **Artifacts reviewed:** implementation at the current branch head
> - **Date:** 2026-07-19
> - **Author responses:** `docs/reviews/round3-responses.md`
>
> The review below is reproduced verbatim from the subagent's report, starting at its
> Verdict heading.

## Verdict
APPROVE WITH NITS — every mandatory gate passes (31/31 tests, verify byte-identical, oracle audit and complexity probes confirm the frozen claims); the findings are comment-accuracy and caption-completeness issues, none affecting correctness.

## Mandatory checks

### 1. Test suite
`python3 -m pytest -q -p no:cacheprovider` from the repo root: **31 passed in 1.08s** (wall 1.30s including interpreter start). Well inside §6's ~10s budget; the header's "a few seconds" is if anything modest. Environment matches the pins exactly: Python 3.11.15, numpy 2.4.6, matplotlib 3.11.1, pytest 9.1.1. **PASS.**

### 2. Oracle audit
I audited the structural-oracle vacuity story by running the *real* test file against three mutants (scratch copies only; repo untouched):

- **m1, `rle = identity`** (the documented threat): `test_rle_fixed_point_on_prefix` alone **passes** — the vacuity is real, exactly as the suite's docstring warns. The closers then kill it: hand vectors fail immediately; `test_run_count_window` fails at its endpoint cross-check (`666673 == 1000000`). Note the mechanism: the per-L window is checked on an *incremental* counter (independent of `rle` — good), so identity-`rle` is caught by the endpoint equality, not the window itself. Full tally: 4 failed, 27 passed.
- **m2, pointer `i = 1`**: 5 failed; first divergence from K at index 6 — matching the suite's recorded review measurement, ~50× inside the 300-term literal's horizon.
- **m3, nilsson discards one parent symbol instead of two**: 4 failed; diverges at index 6.

Independence of the external oracle: the 300-term literal owes nothing to repo code, and `tools/crosscheck_oeis.py` ran clean — **"OK: all 10502 OEIS b-file terms match kolakoski_pointer"**, exit 0, ~1s — which transitively pins the literal (suite asserts impls == literal; crosscheck asserts pointer == b-file). **PASS**, with one non-self-contained assertion noted below (finding 4).

### 3. Complexity probe
Probed `kolakoski_nilsson`'s Θ(log n) depth by counting live generator frames via `gc` (no repo modification):

| n | 10³ | 10⁴ | 10⁵ | 10⁶ | 10⁷ |
|---|---|---|---|---|---|
| levels | 16 | 22 | 27 | 33 | **39** |
| log₁.₅ n | 17.0 | 22.7 | 28.4 | 34.1 | 39.8 |

+5–6 levels per decade, and 39 at 10⁷ — the docstring's exact claim. Memory (tracemalloc peak through `stream_stats`): nilsson 13.2 / 14.8 / 16.4 KB at 10⁵/10⁶/10⁷ (logarithmic) vs `gen` 0.83 / 8.8 / 82.2 MB (linear). Total work O(n): nilsson 0.284s at 10⁶ → 2.832s at 10⁷ (×9.97 for ×10). Bonus: expand takes exactly 33 rounds past 10⁶ and 39 past 10⁷, as documented; fig6's "~10,000×" headline checks out at 10⁷ (pointer peak 162.2 MB / 16.4 KB ≈ 9,900×). **PASS.**

### 4. viz.py --verify
Full output (exit 0):

```
re-rendering deterministic figures for byte-comparison:
  fig1  fig1_self_description.png    1.7s      41 KB
  fig2  fig2_density.png    0.5s     107 KB
  fig3  fig3_discrepancy_walk.png    0.5s     115 KB
  fig4  fig4_turtle.png    0.3s     113 KB
  fig5  fig5_raster.png    0.1s      42 KB
  ok fig1..fig5: byte-identical (all five)
verify: PASS
```

Committed PNGs run 42–141 KB, all under the 400,000 B budget (fig6 size-checked only, per spec). **PASS.**

## Findings

1. **(Minor, kolakoski.py:165)** The pointer loop comment says the invariant `rld(seq[:i], 1) == seq` is "machine-checked in the test suite". It is not — no test asserts it; the suite checks input/output equivalence only. The invariant itself is true (I instrumented a replica: held at all 1,999 loop entries to 3,000 terms), so either add the cheap per-iteration check as a test or reword to "machine-checked during review". A student sent hunting for that test will not find it.
2. **(Minor, fig2 vs frozen §7)** The plan froze: y-limits [0.47, 0.53] "(the early transient — density(3) = 1/3 — is clipped, **and the caption says so**)". The limits are implemented, but no caption — on the PNG or in WRITEUP §5 — discloses the clipping. Not vacuous: the curve genuinely exits the window near n ≈ 11 *inside* the plotted x-range. One sentence fixes it (fig2, unlike fig3, has no on-figure fine-print line at all).
3. **(Minor, kolakoski.py:287–288)** Mixed-n comparison: "39 levels after 10⁷ terms, ~15 KB of generator frames vs ~17 MB for the stored tape" pairs a 10⁷ measurement with a 10⁶ one. Measured: 16.4 KB at 10⁷; but the tape at 10⁷ costs 82 MB (`gen`) / 162 MB (`pointer` incl. its truncation copy) — 17 MB is the 10⁶ list-family peak (measured 16.77 MB, matching the plan's fig6 row). Spec-inherited from §5D, but the module presents it as a single comparison; say "vs ~17 MB at 10⁶ / ~80+ MB at 10⁷".
4. **(Minor, tests)** `test_alphabet_and_no_triples`' no-triples half routes through `rle` (`max(rle(K)) <= 2`), so under the m1 identity mutant it silently passes (observed). The suite as a whole closes the hole, but a direct three-equal-symbols window scan would make this assertion self-contained.
5. **(Nit)** `_demo` says it is "kept as a function returning a string so the demo itself is testable" — no test or doctest exercises it.
6. **(Nit)** `stream_stats` on an iterator shorter than n silently under-consumes (measured: `(1, 0, 1)` from a 2-item iterator with n=10). The "exactly n" contract implicitly assumes a sufficient source; one caveat line would spare a student confusion.

All clear on: registry membership ({pointer, expand} / {gen, nilsson} exactly); edges n ∈ {0,1,2,3} plus graceful negatives for both list impls; truncation at n=4; `stream_stats` n=0 → (0,0,0) and exactly-n consumption; §6 inventory complete (300-term literal with dated provenance, both windows over 10⁶ with the frozen ceil constants, hand vectors, islice materialization, computation-not-theorem density corridor, doctest runner); fig3's annotated extremes independently reproduced (+189 at n=7,518,095; −154 at n=2,222,194); fig6 separate passes / min-of-3 whiskers / single-run memory / `stream_stats` in both passes / direct labels; no randomness anywhere; crosscheck path shim correct from any CWD (Python 3.11 makes `__file__` absolute; verified from inside `tools/`); README quickstart claims accurate; the pre-existing doodle files are disclosed and byte-identical as constrained.

## Residual risks
Byte-identity is promised only in the pinned environment, and the pins will age; when a rebuild under new pins re-renders figures, fig2's committed extreme annotations (fig3's numbers, fig2's inset text) must be re-checked against the data, not assumed. The 17 MB/10⁶ vs 82–162 MB/10⁷ scale-mixing (finding 3) traces back to the frozen plan itself, so fixing the module means a disclosed deviation from v3 wording. Nothing here blocks release.
