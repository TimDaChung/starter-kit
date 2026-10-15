"""From the ad team's review-folder path, find the plan's "Banner圖檔名稱" in Notion.

  python find_banner_name.py "X:\\...\\魚樂園\\v8.7\\v8.7魚樂園_賓果衝刺禮\\對稿\\1024x576_GAF"

Path -> version (v8.7) + giftbag name (賓果衝刺禮) -> 版本或更新之書 page titled v8.7
-> 活動之書 pages whose 上線版號 links to it -> the page with a heading containing the giftbag
name -> the "Banner圖檔名稱：…" line under that heading. Read-only, dept-4 REST proxy.
Prints one line per step so a wrong hop is visible; exit 1 when nothing (or several) match.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plan-dept14-writer" / "scripts"))
from notion_rest import Notion, find_token, plain  # noqa: E402

ACTIVITY_DB = "217e22985ac981fe8a2fe9d1b5526bd1"   # 魚樂園之書／活動之書
VERSION_DB = "217e22985ac9816b9ac8f1b5a0294f7d"    # 魚樂園之書／版本或更新之書
PATH_RE = re.compile(r"[\\/](?P<ver>v\d+(?:\.\d+)+)[\\/](?P=ver)[^\\/]*?_(?P<gift>[^\\/]+?)(?:[\\/]|$)")
NAME_RE = re.compile(r"Banner\s*圖?檔名稱?\s*[:：]\s*(?P<name>\S+)")


def parse_path(path: str) -> tuple[str, str]:
    """'…\\v8.7\\v8.7魚樂園_賓果衝刺禮\\對稿\\…' -> ('v8.7', '賓果衝刺禮')."""
    m = PATH_RE.search(path)
    if not m:
        raise SystemExit(f"cannot read version and giftbag name from path: {path}")
    return m.group("ver"), m.group("gift")


def title_of(page: dict) -> str:
    return plain(next(v for v in page["properties"].values() if v["type"] == "title")["title"])


def version_page(api: Notion, ver: str) -> dict:
    r = api.call("POST", f"/databases/{VERSION_DB}/query", {"filter": {"property": "title", "title": {"equals": ver}}})
    hits = r["results"]
    if len(hits) != 1:
        raise SystemExit(f"version page {ver!r}: {len(hits)} matches in 版本或更新之書")
    return hits[0]


def activities_for(api: Notion, version_id: str) -> list[dict]:
    r = api.call("POST", f"/databases/{ACTIVITY_DB}/query",
                 {"filter": {"property": "上線版號", "relation": {"contains": version_id}}, "page_size": 50})
    return r["results"]


def banner_name_in(api: Notion, page_id: str, gift: str) -> tuple[str, str] | None:
    """(heading text, file name) of the section whose heading contains `gift`, else None."""
    heading, name = None, None
    for _, b in api.walk(page_id, 0, 4):
        t = b["type"]
        if t.startswith("heading_"):
            txt = plain(b[t]["rich_text"])
            if heading and name:
                break
            heading = txt if gift in txt else None
            continue
        if heading and isinstance(b.get(t), dict):
            m = NAME_RE.search(plain(b[t].get("rich_text")))
            if m:
                name = m.group("name")
    return (heading, name) if heading and name else None


def find(path: str, api: Notion | None = None, log=print) -> str:
    ver, gift = parse_path(path)
    log(f"path    : version {ver}, giftbag 「{gift}」")
    api = api or Notion(find_token(dept="四部"))
    vp = version_page(api, ver)
    log(f"version : {title_of(vp)}  {vp['id']}")
    acts = activities_for(api, vp["id"])
    log(f"plans   : {len(acts)} activity page(s) on {ver}: " + "、".join(title_of(p) for p in acts))
    found = []
    for p in acts:
        hit = banner_name_in(api, p["id"], gift)
        if hit:
            found.append((p, *hit))
    if len(found) != 1:
        raise SystemExit(f"{len(found)} plan(s) have a section containing 「{gift}」 with a Banner 圖檔名稱; "
                         "give the file name explicitly")
    p, heading, name = found[0]
    log(f"section : {title_of(p)} › {heading}")
    log(f"name    : {name}")
    return name


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    find(sys.argv[1])
