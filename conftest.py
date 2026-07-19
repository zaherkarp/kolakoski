# This file is intentionally (almost) empty.
#
# Its mere existence at the repository root makes `pytest` insert this
# directory into sys.path (pytest's "rootdir insertion" behavior), so that
# `tests/test_kolakoski.py` can do `import kolakoski` without any packaging
# ceremony (no pyproject.toml, no pip install -e, no src/ layout).
#
# Teaching note: this is the smallest honest solution to Python's
# "how do tests import the code under test?" problem. Real libraries
# graduate to a pyproject.toml + src/ layout; a one-module lesson does not.
