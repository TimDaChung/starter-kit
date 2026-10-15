"""Tests for find_banner_name.py with a fake Notion (no network)."""
from __future__ import annotations

from typing import Any

import pytest

import find_banner_name as fb


def test_parse_path_variants() -> None:
    assert fb.parse_path(r"X:\grp.mkt.ad.p1\Someone\魚樂園\v8.7\v8.7魚樂園_賓果衝刺禮\對稿\1024x576_GAF") == ("v8.7", "賓果衝刺禮")
    assert fb.parse_path("X:/a/魚樂園/v8.10/v8.10魚樂園_兌換衝刺禮/對稿/1024x576_GAF/") == ("v8.10", "兌換衝刺禮")
    assert fb.parse_path(r"X:\a\v8.7\v8.7魚樂園_套圈圈衝刺禮") == ("v8.7", "套圈圈衝刺禮")
    with pytest.raises(SystemExit, match="cannot read"):
        fb.parse_path(r"X:\a\魚樂園\對稿\1024x576_GAF")


def rt(text: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": text}, "plain_text": text}]


def block(bid: str, t: str, text: str, kids: bool = False) -> dict[str, Any]:
    return {"id": bid, "type": t, "has_children": kids, t: {"rich_text": rt(text)}}


class FakeApi:
    """Serves version/activity queries and a page tree; mirrors the notion_rest calls used."""
    def __init__(self, versions: list[dict], activities: list[dict], tree: dict[str, list[dict]]) -> None:
        self.versions, self.activities, self.tree = versions, activities, tree

    def call(self, method: str, path: str, body: Any = None, **kw: Any) -> dict[str, Any]:
        if fb.VERSION_DB in path:
            want = body["filter"]["title"]["equals"]
            return {"results": [v for v in self.versions if fb.title_of(v) == want]}
        if fb.ACTIVITY_DB in path:
            want = body["filter"]["relation"]["contains"]
            return {"results": [a for a in self.activities if want in a["properties"]["上線版號"]["relation"][0]["id"]]}
        raise AssertionError(path)

    def walk(self, block_id: str, depth: int = 0, max_depth: int = 6):
        for b in self.tree.get(block_id, []):
            yield depth, b
            if b.get("has_children") and depth < max_depth:
                yield from self.walk(b["id"], depth + 1, max_depth)


def page(pid: str, title: str, version_id: str | None = None) -> dict[str, Any]:
    props: dict[str, Any] = {"Name": {"type": "title", "title": rt(title)}}
    if version_id:
        props["上線版號"] = {"type": "relation", "relation": [{"id": version_id}]}
    return {"id": pid, "properties": props}


def make_api() -> FakeApi:
    versions = [page("ver87", "v8.7"), page("ver86", "v8.6")]
    activities = [page("actA", "賽特賓果樂", "ver87"), page("actB", "陣營戰S9", "ver87"), page("actC", "舊月活動", "ver86")]
    tree = {
        "actA": [block("h5", "heading_1", "5. 儲值"), block("h51", "heading_2", "5.1. 賓果衝刺禮"),
                 block("p1", "paragraph", "活動衝刺禮模組換包裝"), block("p2", "paragraph", "Banner圖檔名稱：2611_giftbag_Setekh.zip"),
                 block("h52", "heading_2", "5.2. 活動更新禮包"), block("p3", "paragraph", "Banner：2403_permanen_activityupdate.png")],
        "actB": [block("h1", "heading_1", "1. 基本資訊"), block("p9", "paragraph", "沒有禮包")],
    }
    return FakeApi(versions, activities, tree)


def test_find_reads_name_from_matching_section() -> None:
    logs: list[str] = []
    name = fb.find(r"X:\x\v8.7\v8.7魚樂園_賓果衝刺禮\對稿\1024x576_GAF", api=make_api(), log=logs.append)
    assert name == "2611_giftbag_Setekh.zip"
    assert any("賽特賓果樂 › 5.1. 賓果衝刺禮" in l for l in logs)


def test_find_stops_when_no_or_many_matches() -> None:
    with pytest.raises(SystemExit, match="0 plan"):
        fb.find(r"X:\x\v8.7\v8.7魚樂園_套圈圈衝刺禮\對稿", api=make_api(), log=lambda s: None)
    with pytest.raises(SystemExit, match="version page 'v9.9': 0"):
        fb.find(r"X:\x\v9.9\v9.9魚樂園_賓果衝刺禮\對稿", api=make_api(), log=lambda s: None)


def test_name_under_other_section_is_not_taken() -> None:
    # 5.2's "Banner：…png" must not be read as the 5.1 name, and 5.1's name must not leak into 5.2
    api = make_api()
    assert fb.banner_name_in(api, "actA", "活動更新禮包") is None
    assert fb.banner_name_in(api, "actA", "賓果衝刺禮") == ("5.1. 賓果衝刺禮", "2611_giftbag_Setekh.zip")
