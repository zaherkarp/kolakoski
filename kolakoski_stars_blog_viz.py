#!/usr/bin/env python3
"""
kolakoski_stars_blog_viz.py

Purpose
-------
Create a "calm on average, turbulent locally" visualization pack for a blog post:
- Kolakoski sequence rolling density of 1s (structured local turbulence)
- Stars-like simulation with stable national mean, shifting measure landscape
- Optional PNG charts (if matplotlib installed)
- Always writes CSVs
- Writes a ready-to-paste Markdown snippet

No external deps required for CSV + ASCII preview.
Optional: matplotlib for pretty PNG output.

Outputs (in ./out/)
-------------------
- kolakoski.csv
- stars_simulated.csv
- stars_summary_by_year.csv
- blog_viz_snippet.md
- (optional PNGs if matplotlib installed)
    - fig_kolakoski_rolling_density.png
    - fig_stars_national_vs_volatility.png
    - fig_measure_share_ge4.png

Run
---
python3 kolakoski_stars_blog_viz.py
"""

from __future__ import annotations

import os
import csv
import math
import random
from typing import List, Optional, Dict, Tuple


# ---------------------------
# Utilities
# ---------------------------

def ensure_outdir(path: str = "out") -> str:
    os.makedirs(path, exist_ok=True)
    return path

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# ---------------------------
# Kolakoski sequence
# ---------------------------

def kolakoski(n: int) -> List[int]:
    """
    Generate first n terms of the Kolakoski sequence over alphabet {1,2}.
    Standard seed: 1,2,2.
    """
    if n <= 0:
        return []
    seq = [1, 2, 2]
    if n <= 3:
        return seq[:n]

    i = 2      # read run-lengths from seq[i]
    value = 1  # next symbol to write (alternates 1,2,1,2,...)

    # This generator is standard and safe for a few 10k terms.
    while len(seq) < n:
        run_len = seq[i]
        seq.extend([value] * run_len)
        value = 2 if value == 1 else 1
        i += 1

    return seq[:n]


def rolling_density_of_ones(seq: List[int], window: int) -> List[Optional[float]]:
    """
    Rolling density of ones over a fixed window.
    Returns list same length as seq; first window-1 values are None.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    out: List[Optional[float]] = [None] * len(seq)
    if not seq:
        return out
    if window == 1:
        return [1.0 if v == 1 else 0.0 for v in seq]

    ones_count = 0
    for i, v in enumerate(seq):
        if v == 1:
            ones_count += 1
        if i >= window:
            if seq[i - window] == 1:
                ones_count -= 1
        if i >= window - 1:
            out[i] = ones_count / window
    return out


# ---------------------------
# Stars-like simulation
# ---------------------------

def simulate_stars(
    years: List[int],
    measures: List[str],
    n_contracts: int,
    seed: int,
    national_mean_center: float = 3.60,
    national_mean_drift_per_year: float = 0.02,
    national_mean_noise: float = 0.05,
    regime_flip_prob: float = 0.35,
    regime_shock_scale: float = 0.22,
    contract_noise: float = 0.28,
) -> List[Tuple[int, str, str, float]]:
    """
    Produce synthetic contract-level stars values (half-star increments) by year and measure.

    Design goal:
    - national mean stays fairly stable (with gentle drift)
    - each measure experiences regime-like shifts (definition change / coding drift / cutpoint reset vibe)
    - contract-level spread exists each year
    """
    rng = random.Random(seed)
    contract_ids = [f"C{str(i).zfill(4)}" for i in range(1, n_contracts + 1)]

    # Per-measure baseline offsets and evolving "regime" effect
    baseline = {m: rng.uniform(-0.12, 0.12) for m in measures}
    regime_sign = {m: rng.choice([-1.0, 1.0]) for m in measures}
    regime_level = {m: rng.uniform(-0.08, 0.08) for m in measures}

    rows: List[Tuple[int, str, str, float]] = []

    for yi, year in enumerate(years):
        national_mean = (
            national_mean_center
            + yi * national_mean_drift_per_year
            + rng.uniform(-national_mean_noise, national_mean_noise)
        )

        for m in measures:
            # Occasionally flip regimes and nudge magnitude
            if rng.random() < regime_flip_prob:
                regime_sign[m] *= -1.0
                regime_level[m] += rng.uniform(-regime_shock_scale, regime_shock_scale)

            mu = national_mean + baseline[m] + (regime_sign[m] * regime_level[m])

            for cid in contract_ids:
                v = mu + rng.uniform(-contract_noise, contract_noise)
                v = clamp(v, 1.0, 5.0)
                v = round(v * 2.0) / 2.0  # half-star increments
                rows.append((year, cid, m, float(v)))

    return rows


def summarize_stars(rows: List[Tuple[int, str, str, float]], measures: List[str]) -> List[Dict[str, float]]:
    """
    Summarize:
      - national mean by year
      - SD of measure means by year (volatility proxy)
      - mean share >=4 across measures
    """
    # year -> measure -> list of values
    bucket: Dict[int, Dict[str, List[float]]] = {}
    for year, _cid, measure, stars in rows:
        bucket.setdefault(year, {}).setdefault(measure, []).append(stars)

    out: List[Dict[str, float]] = []
    for year in sorted(bucket.keys()):
        all_vals: List[float] = []
        measure_means: List[float] = []
        measure_pct_ge4: List[float] = []

        for m in measures:
            vals = bucket[year].get(m, [])
            if not vals:
                continue
            all_vals.extend(vals)
            mu = sum(vals) / len(vals)
            measure_means.append(mu)
            measure_pct_ge4.append(sum(1 for v in vals if v >= 4.0) / len(vals))

        national_mean = sum(all_vals) / len(all_vals) if all_vals else float("nan")

        # sample SD of measure means
        if len(measure_means) >= 2:
            mm = sum(measure_means) / len(measure_means)
            var = sum((x - mm) ** 2 for x in measure_means) / (len(measure_means) - 1)
            sd_measure_means = math.sqrt(var)
        else:
            sd_measure_means = 0.0

        mean_pct_ge4 = (sum(measure_pct_ge4) / len(measure_pct_ge4)) if measure_pct_ge4 else 0.0

        out.append({
            "year": float(year),
            "national_mean_stars": national_mean,
            "sd_of_measure_means": sd_measure_means,
            "mean_pct_ge4": mean_pct_ge4,
        })

    return out


def measure_year_pct_ge4(rows: List[Tuple[int, str, str, float]], measures: List[str]) -> List[Dict[str, float]]:
    """
    For each year and measure: share of contracts with stars >= 4.0
    """
    bucket: Dict[Tuple[int, str], List[float]] = {}
    for year, _cid, measure, stars in rows:
        bucket.setdefault((year, measure), []).append(stars)

    out: List[Dict[str, float]] = []
    for (year, measure), vals in sorted(bucket.items()):
        pct = sum(1 for v in vals if v >= 4.0) / len(vals) if vals else 0.0
        out.append({"year": float(year), "measure": measure, "pct_ge4": pct})
    return out


# ---------------------------
# ASCII preview (always available)
# ---------------------------

def ascii_line_plot(points: List[Tuple[str, float]], width: int = 50, value_fmt: str = "{:.3f}") -> None:
    ys = [p[1] for p in points]
    max_val = max(ys)
    min_val = min(ys)

    for x, y in points:
        if max_val == min_val:
            pos = width // 2
        else:
            pos = int((y - min_val) / (max_val - min_val) * width)
        print(f"{x}: {value_fmt.format(y)} " + (" " * pos) + "*")


# ---------------------------
# Optional plotting with matplotlib
# ---------------------------

def try_make_pngs(outdir: str, k_csv: str, s_summary_csv: str, s_pct_csv: str) -> bool:
    """
    Attempt to import matplotlib and create PNGs.
    Returns True if successful, False otherwise.
    """
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        return False

    # Read CSVs (pure python)
    k_idx: List[int] = []
    k_roll: List[float] = []
    with open(k_csv, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["rolling_density_ones"] in ("", "None"):
                continue
            k_idx.append(int(row["index"]))
            k_roll.append(float(row["rolling_density_ones"]))

    years: List[int] = []
    nat_mean: List[float] = []
    vol: List[float] = []
    with open(s_summary_csv, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            years.append(int(float(row["year"])))
            nat_mean.append(float(row["national_mean_stars"]))
            vol.append(float(row["sd_of_measure_means"]))

    # Plot 1: Kolakoski rolling density
    plt.figure()
    plt.plot(k_idx, k_roll)
    plt.title("Kolakoski: Rolling density of 1s")
    plt.xlabel("Sequence index")
    plt.ylabel("Rolling density of 1s")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "fig_kolakoski_rolling_density.png"), dpi=160)
    plt.close()

    # Plot 2: National mean vs volatility proxy
    plt.figure()
    plt.plot(years, nat_mean, label="National mean (overall)")
    plt.plot(years, vol, label="Volatility: SD of measure means")
    plt.title("Illusion of Stability: calm national mean, shifting measure landscape")
    plt.xlabel("Year")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "fig_stars_national_vs_volatility.png"), dpi=160)
    plt.close()

    # Plot 3: pct >=4 by measure-year
    # Load and group
    by_measure: Dict[str, List[Tuple[int, float]]] = {}
    with open(s_pct_csv, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            y = int(float(row["year"]))
            m = row["measure"]
            p = float(row["pct_ge4"])
            by_measure.setdefault(m, []).append((y, p))

    plt.figure()
    for m, pts in by_measure.items():
        pts_sorted = sorted(pts, key=lambda t: t[0])
        xs = [t[0] for t in pts_sorted]
        ys = [t[1] for t in pts_sorted]
        plt.plot(xs, ys, label=m)
    plt.title("Measure-level turbulence: share of contracts at ≥4 Stars")
    plt.xlabel("Year")
    plt.ylabel("Percent ≥ 4 Stars")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "fig_measure_share_ge4.png"), dpi=160)
    plt.close()

    return True


# ---------------------------
# Markdown snippet writer
# ---------------------------

def write_markdown_snippet(outdir: str, made_pngs: bool) -> str:
    path = os.path.join(outdir, "blog_viz_snippet.md")
    lines: List[str] = []
    lines.append("## Data viz: Illusion of stability (simulated)")
    lines.append("")
    lines.append("This post uses two synthetic signals:")
    lines.append("- The Kolakoski sequence: locally turbulent, long-run balanced")
    lines.append("- A Stars-like toy system: stable national mean, shifting measure-level landscape")
    lines.append("")
    lines.append("Artifacts written to `./out/`:")
    lines.append("- `kolakoski.csv`")
    lines.append("- `stars_simulated.csv`")
    lines.append("- `stars_summary_by_year.csv`")
    lines.append("- `stars_pct_ge4_by_measure_year.csv`")
    lines.append("")
    if made_pngs:
        lines.append("### Figures")
        lines.append("")
        lines.append("![Kolakoski rolling density](./out/fig_kolakoski_rolling_density.png)")
        lines.append("")
        lines.append("![National mean vs volatility proxy](./out/fig_stars_national_vs_volatility.png)")
        lines.append("")
        lines.append("![Share of contracts at ≥4 Stars by measure](./out/fig_measure_share_ge4.png)")
        lines.append("")
    else:
        lines.append("> If you want PNG figures auto-generated, install matplotlib and re-run:")
        lines.append("")
        lines.append("```bash")
        lines.append("python3 -m pip install --user matplotlib")
        lines.append("python3 kolakoski_stars_blog_viz.py")
        lines.append("```")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


# ---------------------------
# Main
# ---------------------------

def main() -> None:
    outdir = ensure_outdir("out")

    # Parameters you can tweak
    K_N = 6000
    K_WINDOW = 200

    YEARS = list(range(2016, 2026))
    MEASURES = [
        "Breast Cancer Screening",
        "Medication Reconciliation",
        "Plan All-Cause Readmissions",
        "Controlling Blood Pressure",
    ]
    N_CONTRACTS = 250
    SEED = 42

    # 1) Kolakoski + rolling density
    k = kolakoski(K_N)
    k_roll = rolling_density_of_ones(k, K_WINDOW)

    k_csv = os.path.join(outdir, "kolakoski.csv")
    with open(k_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "value", "is_one", "rolling_density_ones"])
        for i, v in enumerate(k):
            w.writerow([i + 1, v, 1 if v == 1 else 0, k_roll[i]])

    # Quick ASCII preview (sampled so it prints nicely)
    print("\nKolakoski rolling density of 1s (sampled preview):")
    sampled = []
    step = 50
    for i in range(0, len(k_roll), step):
        if k_roll[i] is not None:
            sampled.append((str(i + 1), float(k_roll[i])))
        if len(sampled) >= 30:
            break
    if sampled:
        ascii_line_plot(sampled, value_fmt="{:.3f}")
    else:
        print("(not enough terms for the chosen window)")

    # 2) Stars-like simulation
    stars_rows = simulate_stars(
        years=YEARS,
        measures=MEASURES,
        n_contracts=N_CONTRACTS,
        seed=SEED,
    )

    s_csv = os.path.join(outdir, "stars_simulated.csv")
    with open(s_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "contract_id", "measure", "stars"])
        for row in stars_rows:
            w.writerow(row)

    # 3) Summaries
    summary = summarize_stars(stars_rows, MEASURES)
    s_summary_csv = os.path.join(outdir, "stars_summary_by_year.csv")
    with open(s_summary_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "national_mean_stars", "sd_of_measure_means", "mean_pct_ge4"])
        w.writeheader()
        for d in summary:
            w.writerow(d)

    pct = measure_year_pct_ge4(stars_rows, MEASURES)
    s_pct_csv = os.path.join(outdir, "stars_pct_ge4_by_measure_year.csv")
    with open(s_pct_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "measure", "pct_ge4"])
        w.writeheader()
        for d in pct:
            w.writerow(d)

    print("\nNational mean stars (by year):")
    ascii_line_plot([(str(int(d["year"])), float(d["national_mean_stars"])) for d in summary], value_fmt="{:.2f}")

    print("\nVolatility proxy: SD of measure means (by year):")
    ascii_line_plot([(str(int(d["year"])), float(d["sd_of_measure_means"])) for d in summary], value_fmt="{:.3f}")

    # 4) Optional PNGs
    made_pngs = try_make_pngs(outdir, k_csv, s_summary_csv, s_pct_csv)
    if made_pngs:
        print("\nMade PNG figures in ./out/")
    else:
        print("\n(matplotlib not found) Skipped PNG figure generation.")

    # 5) Markdown snippet
    md_path = write_markdown_snippet(outdir, made_pngs)
    print("\nWrote Markdown snippet:", md_path)

    print("\nFiles written to ./out/:")
    print(" - kolakoski.csv")
    print(" - stars_simulated.csv")
    print(" - stars_summary_by_year.csv")
    print(" - stars_pct_ge4_by_measure_year.csv")
    if made_pngs:
        print(" - fig_kolakoski_rolling_density.png")
        print(" - fig_stars_national_vs_volatility.png")
        print(" - fig_measure_share_ge4.png")
    print(" - blog_viz_snippet.md")


if __name__ == "__main__":
    main()
