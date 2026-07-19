# kolakoski

A small, self-contained **teaching repository** about the Kolakoski sequence
(OEIS [A000002](https://oeis.org/A000002)) — the sequence over {1,2} that is
its own run-length description:

![The sequence describing itself](figures/fig1_self_description.png)

The mathematics fits in an evening; the central question — *do 1s and 2s each
occupy half the sequence in the limit?* — has been open since the 1960s. This
repo uses that gap as a lesson in how careful mathematical software gets built:
**proven, cited, and measured claims are kept strictly apart**, algorithms
carry machine-checked invariants, tests use three independent oracle families,
and every figure says exactly what it does and does not demonstrate.

It was also **built in the open under adversarial review**: the plan was
critiqued across three rounds by two AI reviewer personas (disclosed as such),
who refuted one of its lemmas, corrected the author's response tables, and
once corrected themselves. The full trail ships with the repo — the errors are
part of the curriculum.

## Quickstart

```bash
pip install -r requirements.txt   # numpy/matplotlib (figures) + pytest only;
                                  # kolakoski.py itself is stdlib-only
make demo      # watch the sequence describe itself in your terminal
make test      # 31 tests, ~2 s
make figures   # re-render all six figures into figures/
make verify    # full gate: tests + figs 1-5 byte-identical to committed
```

Versions are pinned exactly so the committed PNGs reproduce byte-for-byte;
any reasonably recent versions work for everything except that byte-identity
check (Python 3.11 is what the figures were rendered under).

No network is needed except for `python3 tools/crosscheck_oeis.py`, which
re-verifies all 10,502 OEIS b-file terms against the generators.

## The learning path

1. **[docs/WRITEUP.md](docs/WRITEUP.md)** — the lesson: definitions with the
   fine print, four short proofs, the open problem with the real bounds
   (Chvátal → Nilsson → Kupin–Rowland, each tagged first-hand/second-hand),
   a guided tour of the algorithms, the figure gallery, and graded exercises.
2. **[kolakoski.py](kolakoski.py)** — four independent implementations,
   annotated to teach: the self-reading tape, iterated run-length decoding,
   an honest O(n) generator, and the O(log n)-memory chain of levels.
   `python3 kolakoski.py 30` demonstrates the defining property live.
3. **[tests/test_kolakoski.py](tests/test_kolakoski.py)** — the three-oracle
   design (external data / independent implementations / structural
   theorems), including why a naive fixed-point test is vacuous.
4. **[viz.py](viz.py)** + **[figures/](figures)** — six deterministic,
   palette-validated figures; `--verify` re-renders and byte-compares.
5. **[PLAN.md](PLAN.md)** — the frozen blueprint (v3) with its full changelog.

## The review trail

| Round | Reviewer (fictional persona, AI-run) | Verdict | File |
|---|---|---|---|
| 1 | Dr. Emeka Okafor — computational math / sci. software | REQUEST CHANGES | [docs/reviews/round1-okafor.md](docs/reviews/round1-okafor.md) |
| 1 | Dr. Salomé Vidal — combinatorics on words | REQUEST CHANGES | [docs/reviews/round1-vidal.md](docs/reviews/round1-vidal.md) |
| 2 | Okafor — disposition audit + new findings | REQUEST CHANGES | [docs/reviews/round2-okafor.md](docs/reviews/round2-okafor.md) |
| 2 | Vidal — disposition audit + self-correction | APPROVE WITH NITS | [docs/reviews/round2-vidal.md](docs/reviews/round2-vidal.md) |
| 3 | both — post-implementation accuracy audit | see files | docs/reviews/round3-*.md |

Author responses, point by point with independent re-verification of every
accepted claim, live in [PLAN.md Appendix A](PLAN.md#appendix-a--changelog-and-review-responses).
Highlight reel: both reviewers independently refuted the same v1 lemma with
the same counterexample (L = 257); round 2 caught an unsound verification
mechanism (git mtimes) and two errors in the author's own response tables;
one reviewer publicly fixed an off-by-one in her own round-1 exercise key.

## Repository map

```
kolakoski.py                 the annotated core module (stdlib-only)
viz.py                       figure generator + the --verify gate
tests/test_kolakoski.py      pytest suite
tools/crosscheck_oeis.py     re-runnable OEIS cross-check (network)
figures/                     six committed PNGs (see the writeup's gallery)
docs/WRITEUP.md              the lesson
docs/reviews/                verbatim review reports, all rounds
PLAN.md                      the frozen plan + changelog + review responses
kolakoski_stars_blog_viz.py  pre-existing doodle (untouched), with out/
```

The pre-existing `kolakoski_stars_blog_viz.py` and `out/` predate this
exercise and are deliberately left as they were.
