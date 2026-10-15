"""Tests for plan_lint.py pure helpers: heading numbers, gaps, references, mermaid decisions.

No Notion access. Run: python -m pytest skills/plan-dept14-writer/scripts/test_plan_lint.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import plan_lint as pl  # noqa: E402


@pytest.mark.parametrize(
    ("text", "want"),
    [
        ("1. 簡介", ("1",)),
        ("2.1. 美術需求表", ("2", "1")),
        ("2.3.B. 配置（左欄頁籤）", ("2", "3", "B")),
        ("4.1 玩法介紹", ("4", "1")),
        ("1.1  101  範例機台", ("1", "1")),
        ("3.10. 顯示規則", ("3", "10")),
        ("目錄", None),
        ("畫面呈現", None),
    ],
)
def test_parse_heading_number(text: str, want: tuple[str, ...] | None) -> None:
    assert pl.parse_heading_number(text) == want


def test_numbering_gap_found() -> None:
    nums = [("4",), ("4", "1"), ("4", "2"), ("4", "4"), ("4", "5")]
    assert pl.numbering_issues(nums) == ["跳號：4.3 不存在（4.4 之前）"]


def test_numbering_letters_and_clean() -> None:
    nums = [("2",), ("2", "1"), ("2", "1", "A"), ("2", "1", "B"), ("2", "2"), ("3",)]
    assert pl.numbering_issues(nums) == []
    assert pl.numbering_issues([("2", "1"), ("2", "1", "A"), ("2", "1", "C")]) == ["跳號：2.1.B 不存在（2.1.C 之前）"]


def test_numbering_duplicate_and_backwards() -> None:
    issues = pl.numbering_issues([("1",), ("2",), ("2",), ("3",), ("3", "2"), ("3", "1")])
    assert "重複編號 2" in issues
    assert any("順序倒退" in x for x in issues)


def test_find_refs() -> None:
    text = "詳見 **3.9.** 與（見 2.3.B.6），可查詢欄位見 4.3；見本節 4. 不算；沿用某企劃 2.6 不算"
    assert pl.find_refs(text) == [("3", "9"), ("2", "3", "B", "6"), ("4", "3")]


SAMPLE_FLOW = """
flowchart TD
    S([活動上線]) --> D1{"是否為新玩家<br/>且未達門檻？"}
    D1 -->|是| A1(遊玩)
    D3 -->|購買| A3(平台付款)
    A3 --> R1[發放首日獎勵]
    R1 --> D4{"全部方案是否都已購買？"}
    D4 -->|是| A4(開放後續獎勵)
    D1 -->|否| E2([不觸發])
    D4 -->|否| A5(解鎖下一方案)
    A5 -.-> D3{"是否購買開放中的方案？"}
    P1 -- 購買高方案 --> D9{單邊}
    class S,E2 startEnd
    linkStyle 3 stroke:#9aa0a6
"""


def test_parse_mermaid_nodes_and_edges() -> None:
    chart = pl.parse_mermaid(SAMPLE_FLOW)
    nodes = chart["nodes"]
    assert nodes["D1"] == {"text": "是否為新玩家 且未達門檻？", "kind": "decision"}
    assert nodes["S"]["text"] == "活動上線"
    assert ("A5", "", "D3", True) in chart["edges"]
    assert ("P1", "購買高方案", "D9", False) in chart["edges"]
    assert ("D4", "是", "A4", False) in chart["edges"]


def test_parse_mermaid_labelled_dotted_and_thick() -> None:
    # Reported 2026-10-15: "M -. 是 .-> F" was not parsed, so M showed only one exit.
    chart = pl.parse_mermaid("""
flowchart TD
    M{"是否重來？"} -->|否| E([結束])
    M -. 是 .-> F(重新開始)
    F == 強制 ==> G[結算]
""")
    assert ("M", "是", "F", True) in chart["edges"]
    assert ("F", "強制", "G", False) in chart["edges"]
    rows, warns = pl.decision_report(chart)
    assert [e["label"] for e in rows[0]["exits"]] == ["否", "是"]
    assert not warns


def test_decision_report_lists_exits_and_warns() -> None:
    rows, warns = pl.decision_report(pl.parse_mermaid(SAMPLE_FLOW))
    d4 = next(r for r in rows if r["id"] == "D4")
    assert [(e["label"], e["to"]) for e in d4["exits"]] == [("是", "開放後續獎勵"), ("否", "解鎖下一方案")]
    assert "判斷節點「單邊」只有 0 個出口" in warns
    assert "判斷節點「是否購買開放中的方案？」只有 1 個出口" in warns


class FakeApi:
    def __init__(self, kids: dict[str, list[dict]]) -> None:
        self.kids = kids

    def children(self, bid: str) -> list[dict]:
        return self.kids.get(bid, [])


def _item(bid: str, has_children: bool = False) -> dict:
    return {"id": bid, "type": "numbered_list_item", "has_children": has_children}


def test_resolve_heading_and_items() -> None:
    sec = pl.Section(("3", "3"), "3.3. 補單", "h33", items=[[_item("i1"), _item("i2"), _item("i3", True)]])
    scope = pl.Scope("頁面", sections=[pl.Section(("3",), "3.", "h3"), sec])
    api = FakeApi({"i3": [_item("i3a"), _item("i3b")]})
    assert pl.resolve(("3", "3"), scope, api)
    assert pl.resolve(("3", "3", "3"), scope, api)
    assert pl.resolve(("3", "3", "3", "2"), scope, api)
    assert not pl.resolve(("3", "3", "4"), scope, api)
    assert not pl.resolve(("3", "3", "3", "3"), scope, api)
    assert not pl.resolve(("5", "1"), scope, api)
