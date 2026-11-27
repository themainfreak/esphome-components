"""Tests for script/check_completion_record.py."""

from script.check_completion_record import check

BASE = """Live items: sensor.x
Expected: sensor.x = on
Read 1: GET /api/states/sensor.x at 10:00 -> {read} (matches: {m})
Post-deploy check: sensor.x on -> {post}
Undos: git revert
"""


def test_not_complete_with_pending_is_fine() -> None:
    text = BASE.format(read="on", m="yes", post="pending") + "ready for merge, not complete"
    assert check(text) == []


def test_complete_with_pending_refused() -> None:
    assert check(BASE.format(read="on", m="yes", post="pending") + "complete")


def test_complete_with_unknown_read_refused() -> None:
    assert check(BASE.format(read="unknown", m="no", post="on") + "complete")


def test_complete_with_matching_reads_ok() -> None:
    assert check(BASE.format(read="on", m="yes", post="on 11:00") + "complete") == []


def test_missing_block_refused() -> None:
    assert check("complete")
