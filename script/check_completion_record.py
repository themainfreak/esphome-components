#!/usr/bin/env python3
"""Check the completion record block that LIVE_CHECKS.md requires.

Usage: check_completion_record.py FILE   (FILE holds the PR body or final report)

Exit 0 when the record is fine, 1 otherwise. "complete" is refused when a read
is missing, pending, or returned nothing, "?", unknown or unavailable.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

REQUIRED = ("Live items:", "Expected:", "Read 1:", "Post-deploy check:", "Undos:")
FAILED_READS = ("?", "unknown", "unavailable", "none", "")


def check(text: str) -> list[str]:
    """Return the problems found in a report; empty means fine."""
    problems = [f"missing '{key}' line" for key in REQUIRED if key not in text]
    claims_complete = re.search(r"(?<!not )\bcomplete\b", text, re.I) and not re.search(
        r"ready for merge, not complete", text, re.I
    )
    if problems or not claims_complete:
        return problems
    for line in text.splitlines():
        if line.startswith("Post-deploy check:"):
            if "pending" in line.lower():
                problems.append("says complete while the post-deploy check is pending")
        if line.startswith("Read ") and "->" in line:
            value = line.split("->", 1)[1].split("(matches")[0].strip().strip("\"'`")
            if value.lower() in FAILED_READS:
                problems.append(f"failed read: {line.strip()}")
            if "(matches: no" in line:
                problems.append(f"read does not match: {line.strip()}")
    return problems


def main() -> int:
    problems = check(Path(sys.argv[1]).read_text())
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
