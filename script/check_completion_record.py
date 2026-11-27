#!/usr/bin/env python3
"""Check the completion record block that LIVE_CHECKS.md requires.

Usage: check_completion_record.py FILE   (FILE holds the PR body or final report)

Exit 0 when the record is fine, 1 when it is not, 2 on bad usage.

The record needs a "Status:" line. Only a last status line that says
"not complete" relaxes the read checks; anything else (a missing status, "complete",
"completed", "done") is a claim of completion and fails closed: every read must
hold a real quoted value, match, and the post-deploy check must be read.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

REQUIRED = (
    "Live items:",
    "Expected:",
    "Read 1:",
    "Post-deploy check:",
    "Synced and healthy",
    "Undos:",
    "Status:",
)
TIME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}[T ])?\d{1,2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?\s*")
FAILED_READS = ("?", "unknown", "unavailable", "none", "null", "")


def _lines(text: str) -> list[str]:
    """Lines without leading spaces, bullets or quote marks."""
    return [re.sub(r"^[\s>*\-+]+", "", line).strip() for line in text.splitlines()]


def _value(line: str) -> str:
    """The quoted output after '->' of a read line, without the matches note."""
    if "->" not in line:
        return ""
    value = line.split("->", 1)[1]
    value = re.split(r"\(matches", value, flags=re.I)[0]
    return value.strip().strip("\"'`").strip()


def _is_failed(value: str) -> bool:
    return value.lower() in FAILED_READS


def check(text: str) -> list[str]:
    """Return the problems found in a report; empty means fine."""
    lines = _lines(text)
    problems = [
        f"missing '{key}' line"
        for key in REQUIRED
        if not any(line.lower().startswith(key.lower()) for line in lines)
    ]
    statuses = [line for line in lines if line.lower().startswith("status:")]
    if statuses and re.fullmatch(
        r"status:\s*ready for merge, not complete\.?", statuses[-1], re.I
    ):
        return problems
    for line in lines:
        low = line.lower()
        if re.match(r"read \d+:", low):
            value = _value(line)
            if _is_failed(value):
                problems.append(f"failed read: {line}")
            if re.search(r"\(matches:\s*no", low):
                problems.append(f"read does not match: {line}")
            elif not re.search(r"\(matches:\s*yes", low):
                problems.append(f"read has no 'matches: yes': {line}")
        elif low.startswith("post-deploy check:"):
            if "pending" in low:
                problems.append("complete claimed while the post-deploy check is pending")
            elif "->" not in line:
                problems.append(f"post-deploy check has no read: {line}")
            else:
                time_match = TIME_RE.match(_value(line))
                if not time_match:
                    problems.append(f"post-deploy read has no read time: {line}")
                    continue
                output = _value(line)[time_match.end() :].strip().strip("\"'`").strip()
                if not output:
                    problems.append(f"post-deploy read has no output: {line}")
                elif _is_failed(output):
                    problems.append(f"failed post-deploy read: {line}")
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_completion_record.py FILE", file=sys.stderr)
        return 2
    problems = check(Path(sys.argv[1]).read_text())
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
