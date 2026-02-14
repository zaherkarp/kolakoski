## Data viz: Illusion of stability (simulated)

This post uses two synthetic signals:
- The Kolakoski sequence: locally turbulent, long-run balanced
- A Stars-like toy system: stable national mean, shifting measure-level landscape

Artifacts written to `./out/`:
- `kolakoski.csv`
- `stars_simulated.csv`
- `stars_summary_by_year.csv`
- `stars_pct_ge4_by_measure_year.csv`

> If you want PNG figures auto-generated, install matplotlib and re-run:

```bash
python3 -m pip install --user matplotlib
python3 kolakoski_stars_blog_viz.py
```

