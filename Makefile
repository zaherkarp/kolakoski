# Convenience targets for the Kolakoski teaching exercise.
# Each target is one honest command — read them, then run them by hand if you prefer.

.PHONY: setup demo test figures verify

setup:      ## install the (viz + test only) dependencies
	pip install -r requirements.txt

demo:       ## print the first 30 terms with their run structure and self-check
	python3 kolakoski.py 30

test:       ## run the test suite (stdlib + pytest; ~seconds)
	python3 -m pytest -q

figures:    ## render all six figures into figures/
	python3 viz.py

# Full gate: run tests, then re-render figs 1-5 and require them to be
# BYTE-IDENTICAL to the committed PNGs — proving both determinism and that
# the committed figures match the current viz.py (git does not preserve
# mtimes, so timestamps can't do this; review round 2 caught that). fig6 is
# timing-based and only size-checked. Budget: <=400 KB per PNG.
# This is what CI would run if this repo had CI.
verify: test
	python3 viz.py --verify
