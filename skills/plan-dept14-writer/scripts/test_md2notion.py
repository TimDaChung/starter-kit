"""Tests for md2notion.py pure parts (no network)."""
from __future__ import annotations

import pytest

import md2notion as m

SAMPLE = """# 範例企劃
類別：功能

# 1. 基本資訊
## 1.1. 基本設定
<!-- 表頭:首欄 -->
| 名稱 | 範例 |
| --- | --- |
| 檔名 | demo |

## 1.2. 玩法大綱
1. 第一層
    1. 第二層 <span color="red">後補</span>
        1. 第三層
    | 項目 | 值 |
    |---|---|
    | a | 1 |
2. 第一層 B，見 [規範](https://example.com)

---
# 2. 流程圖
```mermaid
flowchart TD
  A --> B
```
《主流程》

# 3. 畫面呈現
## 3.1. 入口
1. 入口按鈕
![《入口》](img/entry.png)
![《彈窗》](TODO)

---
## 3.2. 主介面
1. 主畫面
"""


def nodes() -> list[dict]:
    return m.group_columns(m.parse(SAMPLE.splitlines()))


def test_table_header_hint_and_default() -> None:
    tables = [n for n in m.parse(SAMPLE.splitlines()) if n.get("type") == "table"]
    t = tables[0]["table"]
    assert (t["has_column_header"], t["has_row_header"]) == (False, True)
    assert t["table_width"] == 2 and len(t["children"]) == 2  # separator row dropped


def test_nested_list_and_table_under_item() -> None:
    top = [n for n in m.parse(SAMPLE.splitlines()) if n.get("type") == "numbered_list_item"]
    first = top[0]
    kids = first["_kids"]
    assert [k["type"] for k in kids] == ["numbered_list_item", "table"]
    assert kids[1]["table"]["has_column_header"] is True  # no hint -> header row
    assert kids[0]["_kids"][0]["type"] == "numbered_list_item"
    red = [r for r in kids[0]["numbered_list_item"]["rich_text"] if r.get("annotations", {}).get("color") == "red"]
    assert red and red[0]["text"]["content"] == "後補"
    link = [r for r in top[1]["numbered_list_item"]["rich_text"] if r["text"].get("link")]
    assert link[0]["annotations"]["color"] == "blue"


def test_mermaid_caption_and_columns() -> None:
    ns = nodes()
    code = next(n for n in ns if n.get("type") == "code")
    assert code["code"]["language"] == "mermaid" and m.plain(code["code"]["caption"]) == "《主流程》"
    cols = next(n for n in ns if "_columns" in n)
    text, imgs = cols["_columns"]
    assert [x["type"] for x in text] == ["numbered_list_item"]
    assert [x["_cap"] for x in imgs] == ["《入口》", "《彈窗》"]


def test_start_index_skips_title_lines() -> None:
    ns = nodes()
    assert m.heading_text(ns[m.start_index(ns, None)]) == "範例企劃"
    assert m.heading_text(ns[m.start_index(ns, "1. 基本資訊")]) == "1.基本資訊"


def test_section_span_stops_at_same_level_and_keeps_divider() -> None:
    ns = nodes()
    s, e = m.section_span(ns, "3.1. 入口")
    assert m.heading_text(ns[s]) == "3.1.入口"
    assert all(n.get("type") != "divider" for n in ns[s + 1:e])
    assert ns[e]["type"] == "divider"  # left in place
    s, e = m.section_span(ns, "1.2.玩法大綱")  # whitespace-insensitive
    assert ns[e]["type"] == "divider"
    s, e = m.section_span(ns, "1. 基本資訊")
    assert m.heading_text(ns[e - 1]) != "2.流程圖" and ns[e]["type"] == "divider"


def test_section_span_requires_unique_heading() -> None:
    with pytest.raises(SystemExit, match="0 matching"):
        m.section_span(nodes(), "9. 不存在")


def test_dept1_figure_title_goes_with_image_and_todo_keeps_template_wording() -> None:
    ns = m.group_columns(m.parse("""## 2.1. 入口
1. 入口按鈕
《1.活動入口》
![](a.png)
![【待補】](TODO)
""".splitlines()))
    text, right = ns[1]["_columns"]
    assert [m.plain(x["numbered_list_item"]["rich_text"]) for x in text] == ["入口按鈕"]
    assert m.plain(right[0]["paragraph"]["rich_text"]) == "《1.活動入口》" and right[1]["_image"] == "a.png"
    w = m.Writer(api=None, base=m.Path("."))  # type: ignore[arg-type]
    todo = w.to_block(right[2])
    assert m.plain(todo["paragraph"]["rich_text"]) == "【待補】"
    assert todo["paragraph"]["rich_text"][0]["annotations"]["color"] == "red"

