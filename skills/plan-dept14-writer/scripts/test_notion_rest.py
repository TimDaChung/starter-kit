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
    with pytest.raises(RuntimeError, match="after 0s"):
        FakeUploads(["pending"] * 5).wait_uploaded("fu1", "pending", timeout=0, interval=0)
