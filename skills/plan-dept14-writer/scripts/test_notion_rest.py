"""Tests for notion_rest.py helpers that need no network."""
from __future__ import annotations

from typing import Any

import pytest

import notion_rest as nr


class FakeUploads(nr.Notion):
    def __init__(self, statuses: list[str]) -> None:  # no credentials needed
        self.statuses = statuses
        self.polls = 0

    def call(self, method: str, path: str, body: Any = None, raw: bytes | None = None,
             headers: dict[str, str] | None = None) -> dict[str, Any]:
        assert (method, path) == ("GET", "/file_uploads/fu1")
        self.polls += 1
        return {"status": self.statuses.pop(0)}


def test_wait_uploaded_polls_until_uploaded() -> None:
    api = FakeUploads(["pending", "pending", "uploaded"])
    api.wait_uploaded("fu1", "pending", interval=0)
    assert api.polls == 3


def test_wait_uploaded_returns_at_once_when_send_says_uploaded() -> None:
    api = FakeUploads([])
    api.wait_uploaded("fu1", "uploaded", interval=0)
    assert api.polls == 0


def test_wait_uploaded_raises_on_failed_and_timeout() -> None:
    with pytest.raises(RuntimeError, match="failed"):
        FakeUploads(["failed"]).wait_uploaded("fu1", "pending", interval=0)
    with pytest.raises(RuntimeError, match="expired"):
        FakeUploads(["expired"]).wait_uploaded("fu1", "pending", interval=0)
    with pytest.raises(RuntimeError, match="after 0s"):
        FakeUploads(["pending"] * 5).wait_uploaded("fu1", "pending", timeout=0, interval=0)


def test_table_header_flags() -> None:
    rows = [["名稱", "x"], ["檔名", "y"]]
    assert nr.table(rows)["table"]["has_column_header"] is True
    t = nr.table(rows, header=False, row_header=True)["table"]
    assert (t["has_column_header"], t["has_row_header"]) == (False, True)


class FakeTree(nr.Notion):
    """children() served from a dict; list_format only matters on a list's first item."""
    def __init__(self, tree: dict[str, list[dict[str, Any]]]) -> None:
        self.tree = tree

    def children(self, block_id: str, version: str | None = None) -> list[dict[str, Any]]:
        return self.tree.get(block_id, [])


def li(bid: str, fmt: str | None = None, kids: bool = False) -> dict[str, Any]:
    d: dict[str, Any] = {"id": bid, "type": "numbered_list_item", "has_children": kids,
                         "numbered_list_item": {"rich_text": nr.rt(bid)}}
    if fmt:
        d["numbered_list_item"]["list_format"] = fmt
    return d


def test_check_list_format_default_lists_are_clean() -> None:
    api = FakeTree({"page": [li("a", kids=True), li("b")], "a": [li("a1", kids=True)], "a1": [li("a11")]})
    assert api.check_list_format("page") == []


def test_check_list_format_explicit_top_format_breaks_children() -> None:
    api = FakeTree({"page": [li("a", "numbers", kids=True)], "a": [li("a1", kids=True)], "a1": [li("a11")]})
    [issue] = api.check_list_format("page")
    assert (issue["id"], issue["have"], issue["wrong"]) == ("a", "numbers", [1, 2])


def test_check_list_format_inherits_through_column_and_resets_after_paragraph() -> None:
    para = {"id": "p", "type": "paragraph", "has_children": False, "paragraph": {"rich_text": nr.rt("x")}}
    col = {"id": "cl", "type": "column_list", "has_children": True, "column_list": {}}
    api = FakeTree({"page": [li("a", "letters", kids=True)],
                    "a": [li("a1"), para, li("a2", kids=True)],   # a2 starts a new list after the paragraph
                    "a2": [col], "cl": [{"id": "c", "type": "column", "has_children": True, "column": {}}],
                    "c": [li("c1")]})
    issues = api.check_list_format("page")
    assert [(x["id"], sorted(x["wrong"])) for x in issues] == [("a", [0, 2])]  # level 1 inherits letters = correct; level 0 and the column list at level 2 are wrong
