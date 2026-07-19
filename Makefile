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

# Full gate: run tests, then render figures TWICE and require byte-identical
# output for figs 1-5 (fig6 is timing-based, exempt), plus a <=400 KB size
# budget per PNG. This is what CI would run if this repo had CI.
verify: test
	python3 viz.py --verify
