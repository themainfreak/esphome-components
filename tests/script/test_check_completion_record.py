"""Tests for script/check_completion_record.py, one rule per test."""

import pytest

from script.check_completion_record import check

TEMPLATE = """Live items: sensor.x
Expected: sensor.x = on
Read 1: GET /api/states/sensor.x at 10:00 -> {read} (matches: {m})
Post-deploy check: sensor.x on -> {post}
Synced and healthy / previous build ready to reflash: build 1
Undos: git revert
Status: {status}
"""
GOOD_POST = "11:00 on"


def rec(read="on", m="yes", post=GOOD_POST, status="complete") -> str:
    return TEMPLATE.format(read=read, m=m, post=post, status=status)


def test_good_complete_ok() -> None:
    assert check(rec()) == []


def test_not_complete_with_pending_ok() -> None:
    assert check(rec(post="pending", status="ready for merge, not complete")) == []


def test_pending_refused() -> None:
    assert check(rec(post="pending"))


@pytest.mark.parametrize("read", ["?", "unknown", "unavailable", ""])
def test_failed_read_refused_even_when_matches_yes(read: str) -> None:
    assert any("failed read" in p for p in check(rec(read=read)))


def test_non_matching_read_with_good_value_refused() -> None:
    assert any("does not match" in p for p in check(rec(m="no")))


@pytest.mark.parametrize("post", ["?", "unknown", "unavailable", ""])
def test_untimed_post_deploy_refused(post: str) -> None:
    assert check(rec(post=post))


@pytest.mark.parametrize(
    "post", ["11:00 ?", "11:00 unknown", "11:00 unavailable", '2026-11-20 10:00 "unknown"', "11:00 'None'"]
)
def test_timed_failed_post_deploy_refused(post: str) -> None:
    assert any("failed post-deploy read" in p for p in check(rec(post=post)))


@pytest.mark.parametrize("post", ["11:00", "2026-11-20 10:00 ", '11:00 ""'])
def test_post_deploy_time_without_output_refused(post: str) -> None:
    assert any("no output" in p for p in check(rec(post=post)))


def test_dated_post_deploy_ok() -> None:
    assert check(rec(post='2026-11-20 10:00 "on"')) == []


def test_status_with_not_complete_inside_claim_checked() -> None:
    assert check(rec(read="?", status="complete (earlier: not complete)"))


def test_post_deploy_without_read_time_refused() -> None:
    assert any("read time" in p for p in check(rec(post="on")))


@pytest.mark.parametrize("line", ["Live items:", "Expected:", "Read 1:", "Post-deploy check:",
                                  "Synced and healthy", "Undos:", "Status:"])
def test_missing_line_refused(line: str) -> None:
    text = "\n".join(x for x in rec().splitlines() if not x.startswith(line))
    assert any("missing" in p for p in check(text))


def test_later_not_complete_phrase_does_not_hide_claim() -> None:
    text = rec(read="?") + "\nnote: earlier said ready for merge, not complete\n"
    assert check(text)


@pytest.mark.parametrize("status", ["completed", "done", "Complete."])
def test_other_claims_checked(status: str) -> None:
    assert check(rec(read="?", status=status))


def test_bulleted_lines_checked() -> None:
    text = "\n".join("- " + x for x in rec(read="?").splitlines())
    assert any("failed read" in p for p in check(text))
