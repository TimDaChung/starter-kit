"""Read the 大活動歷屆主題 Notion database and summarize recent usage.

  python fetch_themes.py [--months 12] [--json out.json]

Prints: option sets of 主要類別 / 要素, the last N months, and per-option counts in that window.
Uses the 一部 (pm1) Notion proxy credential (see plan-dept14-writer/references/notion-access.md).
"""
import argparse
import collections
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from notion_api import Notion, find_token  # noqa: E402

THEME_DB = "dee87244fa40823b9d8301e80dadc59b"  # 大活動歷屆主題（一部 workspace, 2026-10-02）


def val(prop):
    t = prop["type"]
    v = prop[t]
    if t in ("title", "rich_text"):
        return "".join(x["plain_text"] for x in v)
    if t == "select":
        return v["name"] if v else ""
    if t == "multi_select":
        return [x["name"] for x in v]
    if t == "date":
        return v["start"] if v else ""
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--months", type=int, default=12)
    ap.add_argument("--json")
    a = ap.parse_args()
    api = Notion(find_token(dept="一部"))
    db = api.call("GET", f"/databases/{THEME_DB}")
    props = db["properties"]
    opts = {k: [o["name"] for o in v["multi_select"]["options"]] for k, v in props.items() if v["type"] == "multi_select"}
    print("選項全集:", json.dumps(opts, ensure_ascii=False))
    rows, cur = [], None
    while True:
        q = {"page_size": 100}
        if cur:
            q["start_cursor"] = cur
        r = api.call("POST", f"/databases/{THEME_DB}/query", q)
        rows += r["results"]
        if not r.get("has_more"):
            break
        cur = r["next_cursor"]
    items = []
    for pg in rows:
        d = {k: val(pg["properties"][k]) for k in props if props[k]["type"] in ("title", "rich_text", "select", "multi_select", "date")}
        if d.get("月份"):
            items.append(d)
    items.sort(key=lambda x: x["月份"])
    today = date.today()
    y, m = today.year, today.month - a.months
    while m <= 0:
        y, m = y - 1, m + 12
    start = f"{y:04d}-{m:02d}"
    recent = [i for i in items if i["月份"][:7] >= start]
    print(f"\n近 {a.months} 個月（{start} 起）:")
    print("月份 | 活動名稱 | 主題描述 | 主要類別 | 要素")
    for i in recent:
        print(f"{i['月份'][:7]} | {i.get('活動名稱','')} | {i.get('主題描述','')} | {'、'.join(i.get('主要類別',[]))} | {'、'.join(i.get('要素',[]))}")
    c1 = collections.Counter(x for i in recent for x in i.get("主要類別", []))
    c2 = collections.Counter(x for i in recent for x in i.get("要素", []))
    print("\n主要類別 次數:", dict(c1))
    print("要素 次數:", dict(c2))
    unused = {k: [o for o in v if (c1 if k == "主要類別" else c2)[o] == 0] for k, v in opts.items()}
    print("近期沒用過:", json.dumps(unused, ensure_ascii=False))
    empty = [i["月份"][:7] for i in items if not i.get("活動名稱")]
    if empty:
        print("活動名稱空白的月份:", empty)
    if a.json:
        Path(a.json).write_text(json.dumps({"options": opts, "recent": recent, "all": items}, ensure_ascii=False, indent=1), encoding="utf-8")
        print("written", a.json)


if __name__ == "__main__":
    main()
