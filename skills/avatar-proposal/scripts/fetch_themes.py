"""Read the 大活動歷屆主題 Notion database and summarize recent usage.

  python fetch_themes.py [--months 12] [--json out.json] [--recent-plans 3]

Prints: option sets of 主要類別 / 要素, the last N months, and per-option counts in that window.
--recent-plans N: also list the newest N pages per 活動類型 (人物設定 / 人物活動 / 神娃活動) in the 一部
活動資料庫, with page ids, so past plans of the same type can be read (the template page is skipped).
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
EVENT_DB = "1fa87244fa4081f48ae6cdb09a4059cb"  # 活動資料庫, select 活動類型 (Tim 2026-10-08)
PLAN_TYPES = ("人物設定", "人物活動", "神娃活動")
TEMPLATE_PAGE_ID = "3ed87244fa40819bbbfdd0c04bd28277"


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
    ap.add_argument("--recent-plans", type=int, default=0)
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
    if a.recent_plans:
        print(f"\n活動資料庫 最近 {a.recent_plans} 期同類型企劃（可用 notion_api 讀內容）:")
        for typ in PLAN_TYPES:
            r = api.call("POST", f"/databases/{EVENT_DB}/query", {
                "page_size": a.recent_plans + 1, "filter": {"property": "活動類型", "select": {"equals": typ}},
                "sorts": [{"timestamp": "created_time", "direction": "descending"}]})
            pages = [pg for pg in r["results"] if pg["id"].replace("-", "") != TEMPLATE_PAGE_ID][:a.recent_plans]
            names = [f"{val(pg['properties']['Name'])} ({pg['id'].replace('-', '')})" for pg in pages]
            print(f"  {typ}: " + ("；".join(names) if names else "（尚無，只有範本頁）"))
    if a.json:
        Path(a.json).write_text(json.dumps({"options": opts, "recent": recent, "all": items}, ensure_ascii=False, indent=1), encoding="utf-8")
        print("written", a.json)


if __name__ == "__main__":
    main()
