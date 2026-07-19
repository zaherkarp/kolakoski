#!/usr/bin/env python3
"""Re-runnable cross-check of our generators against the OEIS b-file.

The test suite hard-codes only the first 300 terms of A000002 (a literal you
can eyeball). This script makes the *full* external-oracle claim reproducible:
it downloads OEIS's complete table for A000002 (10,502 terms as of 2026-07-19),
parses it, and compares every term against `kolakoski_pointer`.

    python3 tools/crosscheck_oeis.py

Needs network access; exits 0 on a perfect match, 1 on any mismatch, 2 on a
download problem. Standard library only — the point of a trust anchor is that
you can read all of it.

Provenance note: OEIS content is licensed CC BY-SA 4.0; this script fetches
it live rather than vendoring it into the repository.
"""

import sys
import urllib.request

# Make `import kolakoski` work when run as `python3 tools/crosscheck_oeis.py`
# from the repository root (the usual way) or from anywhere else.
sys.path.insert(0, __file__.rsplit("/", 2)[0])

from kolakoski import kolakoski_pointer  # noqa: E402  (path shim above)

B_FILE_URL = "https://oeis.org/A000002/b000002.txt"


def fetch_bfile_terms(url: str = B_FILE_URL) -> list[int]:
    """Download and parse the b-file: lines of "n a(n)", '#' starts a comment."""
    # OEIS rejects urllib's default User-Agent with a 403; identify honestly.
    request = urllib.request.Request(
        url, headers={"User-Agent": "kolakoski-teaching-repo crosscheck (Python urllib)"}
    )
    with urllib.request.urlopen(request, timeout=30) as resp:
        text = resp.read().decode("ascii")
    terms: list[int] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        _, value = line.split()
        terms.append(int(value))
    return terms


def main() -> int:
    try:
        oeis = fetch_bfile_terms()
    except Exception as exc:  # noqa: BLE001 — report and exit, nothing to handle
        print(f"download failed: {exc}", file=sys.stderr)
        return 2

    ours = kolakoski_pointer(len(oeis))
    if ours == oeis:
        print(f"OK: all {len(oeis)} OEIS b-file terms match kolakoski_pointer.")
        return 0

    # Locate the first disagreement — the most useful single fact for debugging.
    for idx, (mine, theirs) in enumerate(zip(ours, oeis), start=1):
        if mine != theirs:
            print(f"MISMATCH at n={idx}: ours={mine}, OEIS={theirs}", file=sys.stderr)
            return 1
    print("MISMATCH: length disagreement (should be unreachable)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
