"""Tests added after the 2026-10-15 review of md2notion.py / plan_lint.py (no network)."""
from __future__ import annotations

import md2notion as m
import plan_lint as pl


def test_images_only_section_is_stacked_not_columns() -> None:
    # column_list needs >= 2 columns (API 400 verified); a section with only images gets no columns
    ns = m.group_columns(m.parse(["## 3.2. 主介面", "![《主介面》](a.png)"]))
    assert not any("_columns" in n for n in ns)
    assert ns[1]["_image"] == "a.png"


def test_image_line_keeps_list_nesting() -> None:
    top = [n for n in m.parse(["1. a", "    ![](x.png)", "    1. b"]) if n.get("type") == "numbered_list_item"]
    assert len(top) == 1
    assert m.plain(top[0]["_kids"][0]["numbered_list_item"]["rich_text"]) == "b"


def test_code_caption_vs_dept1_figure_title() -> None:
    ns = m.parse(["```mermaid", "A-->B", "```", "《1.流程圖》", "![](flow.png)", "",
                  "```mermaid", "C-->D", "```", "《主流程》"])
    codes = [n for n in ns if n.get("type") == "code"]
    assert m.plain(codes[0]["code"]["caption"]) == ""
    assert m.plain(ns[1]["paragraph"]["rich_text"]) == "《1.流程圖》"  # stays as the figure title
    assert m.plain(codes[1]["code"]["caption"]) == "《主流程》"


def test_header_hint_only_applies_to_next_table_and_none() -> None:
    ns = m.parse(["<!-- 表頭:無 -->", "| a | b |", "|---|---|", "| 1 | 2 |",
                  "<!-- 表頭:首欄 -->", "段落", "| c | d |", "|---|---|", "| 3 | 4 |"])
    t1, t2 = [n["table"] for n in ns if n.get("type") == "table"]
    assert (t1["has_column_header"], t1["has_row_header"]) == (False, False)
    assert (t2["has_column_header"], t2["has_row_header"]) == (True, False)  # hint cleared by the paragraph


def test_image_paths_skips_todo() -> None:
    ns = m.group_columns(m.parse(["## x", "1. t", "![《a》](a.png)", "![《b》](TODO)", "## y", "![](c.png)"]))
    assert m.image_paths(ns) == ["a.png", "c.png"]


def test_dotted_pipe_label_still_parses() -> None:
    chart = pl.parse_mermaid("flowchart TD\n    H(結束) -.->|回頭| M{x}")
    assert ("H", "回頭", "M", True) in chart["edges"]
