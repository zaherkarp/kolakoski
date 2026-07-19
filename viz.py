#!/usr/bin/env python3
"""Six figures for the Kolakoski teaching exercise — deterministic by design.

Each figure teaches one thing (PLAN.md §7 pins the full specs):

    fig1  the sequence describing itself           (a diagram, not a chart)
    fig2  running density vs the rigorous bounds   (the open problem, on ink)
    fig3  the discrepancy walk D(n) = #1s - #2s    (OEIS A088568)
    fig4  the same bits as turtle geometry         (qualitative)
    fig5  two wrap widths, no alignment            (aperiodicity, visually)
    fig6  four implementations, resource profiles  (the O(log n) payoff)

Design notes (from the data-viz method used across this repo):
- Color is assigned by JOB. The two symbols are categorical identities and
  keep their colors everywhere: 1 = blue, 2 = orange (validated pair:
  CVD ΔE 24.7, normal 33.6, both >= 3:1 on the surface). The four
  implementations in fig6 use the first four slots of the validated
  categorical order; two of them sit below 3:1 contrast on the light
  surface, which is legal only with direct labels — fig6 direct-labels
  every series. Time-in-fig4 is a magnitude, so it gets a one-hue
  sequential ramp (blue, steps 250-700), not a rainbow.
- Reference lines (1/2, Chvátal, Nilsson, ±0.2√n) are chrome, not series:
  muted/secondary ink, dashed or thin, each labeled on the line.
- Determinism: no randomness anywhere; figs 1-5 are pure functions of K, so
  `--verify` re-renders them into a temp dir and BYTE-COMPARES against the
  committed PNGs (this both proves determinism and pins the committed
  figures to the current code — the drift guard; git mtimes cannot do this).
  fig6 times real code, so it is exempt from the byte check (size gate only).
  Byte-identity is promised only in the pinned environment (requirements.txt
  + Python 3.11): the PNG embeds matplotlib's version string.

Usage:
    python3 viz.py                 # render all six into figures/
    python3 viz.py --only 1,3      # a subset
    python3 viz.py --verify        # tests+CI gate: byte-compare 1-5, size-check all
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless, deterministic; never a display backend

import matplotlib.pyplot as plt  # noqa: E402  (backend must be set first)
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, ListedColormap  # noqa: E402

from kolakoski import METHODS, STREAM_METHODS, kolakoski_pointer, rle, stream_stats  # noqa: E402

# ---------------------------------------------------------------------------
# Palette — the validated reference instance (see PLAN.md §7 / dataviz method).
# Roles, not decoration: change a hex here and every figure follows.
# ---------------------------------------------------------------------------

SURFACE = "#fcfcfb"          # light chart surface (the validator's reference)
INK = "#0b0b0b"              # primary text
INK_2 = "#52514e"            # secondary text
MUTED = "#898781"            # axis labels, captions, reference-line labels
GRID = "#e1e0d9"             # hairline gridlines
BASELINE = "#c3c2b7"         # axis lines / zero baselines

C_ONE = "#2a78d6"            # the symbol 1, everywhere it appears
C_TWO = "#eb6834"            # the symbol 2, everywhere it appears
C_ONE_LIGHT = "#86b6ef"      # sequential blue step 250 (band fills)

# fig6 series: first four slots of the validated categorical order, fixed.
C_IMPL = {"pointer": "#2a78d6", "expand": "#008300", "gen": "#e87ba4", "nilsson": "#eda100"}

# fig4 time ramp: one-hue sequential (blue steps 250..700), light -> dark.
CMAP_TIME = LinearSegmentedColormap.from_list(
    "blue-seq", ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
)

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans",       # matplotlib's bundled default: portable
    "font.size": 10,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "axes.titlesize": 12,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,             # grid stays recessive, under the data
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.frameon": False,
    "figure.dpi": 150,
    "savefig.dpi": 150,
})

FIGDIR = Path(__file__).resolve().parent / "figures"
SIZE_BUDGET = 400_000  # bytes per PNG (PLAN §7)


# ---------------------------------------------------------------------------
# Data: K once, as a numpy array; everything below derives from it.
# ---------------------------------------------------------------------------

N_MAX = 10_000_000
_K_CACHE: np.ndarray | None = None


def K() -> np.ndarray:
    """First 10^7 terms as uint8 (~10 MB) — computed once, shared by all figs."""
    global _K_CACHE
    if _K_CACHE is None:
        _K_CACHE = np.array(kolakoski_pointer(N_MAX), dtype=np.uint8)
    return _K_CACHE


def save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path)  # facecolor/dpi come from rcParams — one source of truth
    plt.close(fig)


# ---------------------------------------------------------------------------
# fig1 — the self-description diagram. Deliberately not a chart: no axes,
# no scales; three rows of aligned marks and text ARE the theorem rle(K)=K.
# ---------------------------------------------------------------------------

def fig1(path: Path) -> None:
    n = 30                       # ends exactly at a run boundary: 20 whole runs
    terms = K()[:n]
    lengths = rle(terms.tolist())
    assert sum(lengths) == n     # boundary property the layout depends on

    fig, ax = plt.subplots(figsize=(9.0, 3.0))
    ax.set_axis_off()
    ax.set_xlim(-2.4, n + 0.4)
    ax.set_ylim(-2.3, 2.6)

    # Row 1 — the sequence as colored unit blocks, digit inside each block.
    # White digits clear the 3:1 large-text bar on both fills (4.4:1 / 3.2:1).
    for x, t in enumerate(terms):
        color = C_ONE if t == 1 else C_TWO
        ax.add_patch(plt.Rectangle((x + 0.06, 0), 0.88, 1.0, facecolor=color,
                                   edgecolor=SURFACE, linewidth=0))
        ax.text(x + 0.5, 0.5, str(t), ha="center", va="center",
                color="white", fontsize=13, fontweight="bold")

    # Row 2 — brackets grouping each maximal run.
    # Row 3 — each run's LENGTH under its bracket... which re-spells row 1.
    pos = 0
    for j, run_len in enumerate(lengths):
        left, right = pos + 0.14, pos + run_len - 0.14
        ax.plot([left, left, right, right], [-0.18, -0.42, -0.42, -0.18],
                color=INK_2, linewidth=1.1, solid_capstyle="round")
        ax.text((left + right) / 2, -1.05, str(run_len), ha="center",
                va="center", color=INK, fontsize=13, fontweight="bold")
        pos += run_len

    # The punchline, drawn not asserted: the first len(lengths) blocks vs the
    # lengths row. A subtle underline marks the equal prefix.
    m = len(lengths)
    ax.plot([0.06, m - 0.06], [-1.62, -1.62], color=BASELINE, linewidth=1.0)
    ax.text(m / 2, -2.05,
            f"the {m} run lengths  =  the first {m} terms of the sequence itself",
            ha="center", va="center", color=INK_2, fontsize=10)

    ax.text(-0.3, 0.5, "K", ha="right", va="center", color=INK, fontsize=12,
            fontweight="bold")
    ax.text(-0.3, -1.05, "run\nlengths", ha="right", va="center", color=INK_2,
            fontsize=8.5, linespacing=1.1)
    ax.set_title("The Kolakoski sequence reads out its own run lengths:  rle(K) = K",
                 pad=14)
    fig.tight_layout()
    save(fig, path)


# ---------------------------------------------------------------------------
# fig2 — running density of 1s, with only first-hand-verified numbers on ink.
# Main panel: Chvátal's 0.499/0.501 (bounds on LIMIT POINTS — the finite
# curve may exit them, and at tiny n it does). Inset: the last decade against
# Nilsson 2014's two-sided ±0.000080 (an EVENTUAL bound: it holds for n past
# some N the paper does not make effective — so the lines contextualize, they
# do not certify the plotted decade).
# ---------------------------------------------------------------------------

def fig2(path: Path) -> None:
    ones_cum = np.cumsum(K() == 1)

    # ~4,000 log-spaced sample points: matplotlib never sees 10^7 vertices.
    ns = np.unique(np.logspace(1, 7, 4000).astype(np.int64))
    dens = ones_cum[ns - 1] / ns

    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.set_xscale("log")
    ax.set_xlim(10, N_MAX)
    ax.set_ylim(0.47, 0.53)     # pinned (PLAN §7): early transient is clipped
    ax.plot(ns, dens, color=C_ONE, linewidth=1.6)

    ax.axhline(0.5, color=BASELINE, linewidth=1.0, linestyle=(0, (5, 4)))
    for y in (0.499, 0.501):
        ax.axhline(y, color=INK_2, linewidth=0.9)
    ax.annotate("Chvátal 1993: every limit point\nof the density lies between\n"
                "these two lines",
                xy=(900, 0.4988), xytext=(280, 0.4795), ha="left",
                color=INK_2, fontsize=8.5, linespacing=1.3,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8,
                                shrinkB=4))

    ax.set_xlabel("n  (log scale)")
    ax.set_ylabel("share of 1s among the first n terms")
    ax.set_title("The density of 1s hugs 1/2 — whether it converges is an open problem")

    # Inset: the decade (10^6, 10^7] against Nilsson's corridor. Chvátal's
    # lines stay out (off this scale by ~12x). The measured max deviation in
    # this decade, 3.892e-5 at n = 1,798,512, equals the paper's own Table I
    # entry — a free cross-check of our generator against his computation.
    bound = 455920839 / 911696379 - 0.5          # = 7.9686e-5, the exact bound
    axi = ax.inset_axes([0.585, 0.10, 0.385, 0.42])
    sel = ns >= 10**6
    axi.set_xscale("log")
    axi.plot(ns[sel], dens[sel], color=C_ONE, linewidth=1.2)
    axi.axhline(0.5, color=BASELINE, linewidth=0.8, linestyle=(0, (5, 4)))
    for s in (+1, -1):
        axi.axhline(0.5 + s * bound, color=INK_2, linewidth=0.8)
    axi.set_xlim(10**6, 10**7)
    axi.set_ylim(0.5 - 1.55e-4, 0.5 + 1.55e-4)
    axi.set_yticks([0.4999, 0.5, 0.5001])
    axi.set_title("last decade vs Nilsson 2014 (eventual bound)", fontsize=8,
                  color=INK_2)
    axi.text(9.3e6, 0.5 + bound + 6e-6, "+0.000080", ha="right", va="bottom",
             color=INK_2, fontsize=7.5)
    axi.text(9.3e6, 0.5 - bound - 6e-6, "−0.000080", ha="right", va="top",
             color=INK_2, fontsize=7.5)
    axi.tick_params(labelsize=7)
    axi.grid(True, color=GRID, linewidth=0.5)

    fig.tight_layout()
    save(fig, path)


# ---------------------------------------------------------------------------
# fig3 — the discrepancy walk D(n) = #1s - #2s  (= OEIS A088568).
# 1,250 fixed data-side bins (8,000 points each), drawn as a min/max band —
# honest downsampling that cannot hide a spike. The ±0.2·√n guides carry the
# adjudicated caption stance: an empirical scale reference, not a theorem.
# ---------------------------------------------------------------------------

def fig3(path: Path) -> None:
    steps = np.where(K() == 1, 1, -1).astype(np.int32)
    D = np.cumsum(steps)

    bins = 1250
    per = N_MAX // bins                          # 8,000 terms per bin
    Db = D.reshape(bins, per)
    x = (np.arange(bins) + 0.5) * per            # bin centers on the n-axis
    lo, hi = Db.min(axis=1), Db.max(axis=1)

    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.fill_between(x, lo, hi, color=C_ONE_LIGHT, linewidth=0)
    ax.plot(x, (lo + hi) / 2, color=C_ONE, linewidth=0.7)
    ax.axhline(0, color=BASELINE, linewidth=1.0)

    # Guides at ±0.2√n — c = 0.2 matches Brent's |D(2^64)| ≈ 0.19·√(2^64).
    ng = np.linspace(0, N_MAX, 400)
    for s in (+1, -1):
        ax.plot(ng, s * 0.2 * np.sqrt(ng), color=MUTED, linewidth=1.0,
                linestyle=(0, (6, 4)))
    ax.text(N_MAX * 0.985, 0.2 * np.sqrt(N_MAX * 0.985) + 25, "+0.2√n",
            ha="right", color=MUTED, fontsize=9)
    ax.text(N_MAX * 0.985, -0.2 * np.sqrt(N_MAX * 0.985) - 25, "−0.2√n",
            ha="right", va="top", color=MUTED, fontsize=9)

    # The measured extremes, annotated exactly (ledger numbers).
    ax.annotate("max +189\nn = 7,518,095", xy=(7_518_095, 189),
                xytext=(5_500_000, 310), color=INK_2, fontsize=8.5,
                ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.annotate("min −154\nn = 2,222,194", xy=(2_222_194, -154),
                xytext=(3_300_000, -430), color=INK_2, fontsize=8.5,
                ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

    ax.set_xlim(0, N_MAX)
    ax.set_ylim(-700, 700)
    ax.ticklabel_format(axis="x", style="plain")
    ax.set_xticks(np.arange(0, N_MAX + 1, 2_000_000),
                  ["0", "2M", "4M", "6M", "8M", "10M"])
    ax.set_xlabel("n")
    ax.set_ylabel("D(n) = #1s − #2s")
    ax.set_title("The ±1 walk stays astonishingly near zero — "
                 "no theorem explains it  (A088568)")
    ax.text(0.01, 0.02, "band: min/max per 8,000-term bin · guides: "
            "fair-coin scale with Brent's empirical constant — not a theorem",
            transform=ax.transAxes, color=MUTED, fontsize=7.5)
    fig.tight_layout()
    save(fig, path)


# ---------------------------------------------------------------------------
# fig4 — the turtle. Turn left on 1, right on 2, walk one unit; color by
# time on a one-hue sequential ramp. Purely qualitative: the figure claims
# nothing except "this is what the bits look like as geometry".
# ---------------------------------------------------------------------------

def fig4(path: Path) -> None:
    n = 20_000
    turns = np.where(K()[:n] == 1, 1, -1)        # +90° on 1, −90° on 2
    heading = np.cumsum(turns) * (np.pi / 2)
    xy = np.empty((n + 1, 2))
    xy[0] = 0.0
    xy[1:, 0] = np.cumsum(np.cos(heading))
    xy[1:, 1] = np.cumsum(np.sin(heading))

    segments = np.stack([xy[:-1], xy[1:]], axis=1)
    lc = LineCollection(segments, cmap=CMAP_TIME, linewidth=0.9,
                        capstyle="round")
    lc.set_array(np.arange(n))                   # segment index = time

    fig, ax = plt.subplots(figsize=(6.0, 6.0))
    ax.add_collection(lc)
    ax.plot(*xy[0], marker="o", color=INK, markersize=5)
    ax.annotate("start", xy=tuple(xy[0]), xytext=(6, 6),
                textcoords="offset points", color=INK_2, fontsize=9)
    ax.set_aspect("equal")
    ax.margins(0.05)
    ax.autoscale()
    ax.set_axis_off()
    ax.set_title("The same bits as geometry: turn left on 1, right on 2\n"
                 "(20,000 steps; light → dark = time)", fontsize=11)
    fig.tight_layout()
    save(fig, path)


# ---------------------------------------------------------------------------
# fig5 — the raster. The identical prefix wrapped at two widths: if K were
# eventually periodic some width would organize the columns. None does.
# Evidence, not proof (the writeup proves it properly).
# ---------------------------------------------------------------------------

def fig5(path: Path) -> None:
    cmap = ListedColormap([C_ONE, C_TWO])        # 1 = blue, 2 = orange, as ever

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.5))
    for ax, width, rows in ((axes[0], 90, 90), (axes[1], 89, 90)):
        n = width * rows
        ax.imshow(K()[:n].reshape(rows, width), cmap=cmap, vmin=1, vmax=2,
                  interpolation="nearest", aspect="equal")
        ax.set_title(f"first {n:,} terms, wrapped at width {width}",
                     fontsize=10, color=INK_2)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.suptitle("No wrap width lines the columns up — what aperiodicity "
                 "looks like  (blue = 1, orange = 2)", fontsize=12, color=INK)
    fig.tight_layout()
    save(fig, path)


# ---------------------------------------------------------------------------
# fig6 — the benchmark. Timing and memory are measured in SEPARATE passes
# (tracemalloc inflates runtime ~8.5x — review-measured), and the streaming
# implementations are consumed through stream_stats in BOTH passes, so the
# instrument measures the algorithm, not a stored output list. That the list
# family's footprint includes its output IS the honest comparison: returning
# a list is precisely its memory cost.
# ---------------------------------------------------------------------------

BENCH_NS = [10**3, 10**4, 10**5, 10**6, 10**7]
BENCH_REPEATS = 3


def _run_once(name: str, n: int) -> None:
    """One full production of n terms via implementation `name` (both families)."""
    if name in METHODS:
        METHODS[name](n)
    else:
        stream_stats(STREAM_METHODS[name](), n)


def fig6(path: Path) -> None:
    impls = list(METHODS) + list(STREAM_METHODS)   # pointer, expand, gen, nilsson

    # Pass 1: wall time, min of 3 with min-max whiskers, no instrumentation.
    times: dict[str, list[tuple[float, float]]] = {name: [] for name in impls}
    for name in impls:
        for n in BENCH_NS:
            runs = []
            for _ in range(BENCH_REPEATS):
                t0 = time.perf_counter()
                _run_once(name, n)
                runs.append(time.perf_counter() - t0)
            times[name].append((min(runs), max(runs)))

    # Pass 2: peak memory, single traced run (a peak needs no min-of-k).
    peaks: dict[str, list[int]] = {name: [] for name in impls}
    for name in impls:
        for n in BENCH_NS:
            tracemalloc.start()
            _run_once(name, n)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peaks[name].append(peak)

    fig, (axt, axm) = plt.subplots(1, 2, figsize=(8.0, 4.5))
    # Direct-label vertical offsets (points), hand-set where line ends crowd:
    # expand/nilsson nearly coincide in time; expand/pointer in memory.
    off_t = {"expand": 7, "nilsson": 0, "gen": -8, "pointer": 0}
    off_m = {"expand": 5, "pointer": -6, "gen": 0, "nilsson": 0}
    for name in impls:
        color = C_IMPL[name]
        lo = np.array([t[0] for t in times[name]])
        hi = np.array([t[1] for t in times[name]])
        axt.errorbar(BENCH_NS, lo, yerr=[np.zeros_like(lo), hi - lo],
                     color=color, linewidth=1.8, marker="o", markersize=4,
                     capsize=2, elinewidth=0.9)
        axm.plot(BENCH_NS, peaks[name], color=color, linewidth=1.8,
                 marker="o", markersize=4)
        # Direct labels (mandatory relief for the sub-3:1 slots): ink text
        # beside the colored line end, identity carried by the adjacent mark.
        axt.annotate(name, xy=(BENCH_NS[-1], lo[-1]),
                     xytext=(5, off_t[name]), textcoords="offset points",
                     va="center", fontsize=8.5, color=INK_2)
        axm.annotate(name, xy=(BENCH_NS[-1], peaks[name][-1]),
                     xytext=(5, off_m[name]), textcoords="offset points",
                     va="center", fontsize=8.5, color=INK_2)

    for ax in (axt, axm):
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("n terms")
        ax.margins(x=0.18)                        # room for the direct labels
    axt.set_ylabel("wall time, s  (min of 3; whisker = spread)")
    axm.set_ylabel("peak traced memory, bytes  (single run)")
    axt.set_title("time: all four are Θ(n)", fontsize=10.5)
    axm.set_title("memory: only nilsson is Θ(log n)\n"
                  "(gen streams its interface, not its tape)", fontsize=9.5)
    fig.suptitle("Same output, a ~10,000× memory gap", fontsize=12)
    fig.text(0.01, 0.012, "streams consumed via stream_stats in both passes; "
             "list outputs counted in the list family's footprint · "
             "Python 3.11 · timings vary by machine",
             color=MUTED, fontsize=7.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, path)


# ---------------------------------------------------------------------------
# Driver: render / verify.
# ---------------------------------------------------------------------------

FIGS = {
    1: ("fig1_self_description.png", fig1),
    2: ("fig2_density.png", fig2),
    3: ("fig3_discrepancy_walk.png", fig3),
    4: ("fig4_turtle.png", fig4),
    5: ("fig5_raster.png", fig5),
    6: ("fig6_benchmark.png", fig6),
}
DETERMINISTIC = (1, 2, 3, 4, 5)     # fig6 times real code — byte-check exempt


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(numbers: list[int], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    for num in numbers:
        filename, fn = FIGS[num]
        t0 = time.perf_counter()
        fn(outdir / filename)
        print(f"  fig{num}  {filename}  {time.perf_counter() - t0:5.1f}s  "
              f"{(outdir / filename).stat().st_size / 1024:6.0f} KB")


def verify() -> int:
    """The gate `make verify` runs: determinism + drift + size, in one pass.

    Re-renders figs 1-5 into a temp dir and byte-compares against figures/ —
    identical bytes prove BOTH that rendering is deterministic AND that the
    committed PNGs were produced by the current viz.py (the drift guard; git
    does not preserve mtimes, so timestamps cannot do this job). All six
    committed files are then held to the size budget.
    """
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        print("re-rendering deterministic figures for byte-comparison:")
        render(list(DETERMINISTIC), tmpdir)
        for num in DETERMINISTIC:
            filename, _ = FIGS[num]
            committed, fresh = FIGDIR / filename, tmpdir / filename
            if not committed.exists():
                print(f"FAIL fig{num}: {committed} missing"); failures += 1
            elif sha256(committed) != sha256(fresh):
                print(f"FAIL fig{num}: committed PNG != current render "
                      f"(stale figure or nondeterminism)"); failures += 1
            else:
                print(f"  ok fig{num}: byte-identical")
    for num in FIGS:
        filename, _ = FIGS[num]
        p = FIGDIR / filename
        if not p.exists():
            print(f"FAIL fig{num}: missing"); failures += 1
        elif p.stat().st_size > SIZE_BUDGET:
            print(f"FAIL fig{num}: {p.stat().st_size} bytes > {SIZE_BUDGET}")
            failures += 1
    print("verify:", "PASS" if failures == 0 else f"{failures} FAILURE(S)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", help="comma-separated figure numbers, e.g. 1,3")
    parser.add_argument("--verify", action="store_true",
                        help="byte-compare figs 1-5 vs committed; size-check all")
    args = parser.parse_args(argv)

    if args.verify:
        return verify()
    numbers = sorted(int(s) for s in args.only.split(",")) if args.only else list(FIGS)
    render(numbers, FIGDIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
