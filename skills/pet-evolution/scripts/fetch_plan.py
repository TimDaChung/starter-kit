"""Fetch a pet plan page from the Notion item database: dump text and download images.

Usage:
    NOTION_KEY=<readonly token> python fetch_plan.py <page_id> <out_dir>
    NOTION_KEY=<readonly token> python fetch_plan.py --list

Writes <out_dir>/plan.md (block text in reading order, image placeholders inline)
and <out_dir>/img_NN.png for every image block. Image URLs are signed and expire
in ~5 minutes, so images are downloaded immediately during the walk.
"""
import json
import os
import pathlib
import sys
import urllib.request

API = "https://api.notion.com/v1"
ITEM_DB = "217e22985ac9817d8a65c6a6ed6a135c"
PET_CATEGORY = "8. 寵物"


def request(path: str, body: dict | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {os.environ['NOTION_KEY']}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, headers=headers, method="POST" if data else "GET")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def rich_text(items: list) -> str:
    return "".join(t.get("plain_text", "") for t in items)


def block_text(block: dict) -> str:
    kind = block["type"]
    payload = block.get(kind, {})
    if kind == "table_row":
        return " | ".join(rich_text(cell) for cell in payload.get("cells", []))
    return rich_text(payload.get("rich_text", []))


def walk(block_id: str, out: pathlib.Path, lines: list[str], depth: int, counter: list[int]) -> None:
    cursor = None
    while True:
        query = "?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
        data = request(f"/blocks/{block_id}/children{query}")
        for block in data["results"]:
            indent = "  " * depth
            if block["type"] == "image":
                image = block["image"]
                src = image.get("file", {}).get("url") or image.get("external", {}).get("url")
                caption = rich_text(image.get("caption", []))
                name = f"img_{counter[0]:02d}.png"
                urllib.request.urlretrieve(src, out / name)
                counter[0] += 1
                lines.append(f"{indent}[image {name}] {caption}")
            else:
                text = block_text(block)
                if text:
                    prefix = "#" * int(block["type"][-1]) + " " if block["type"].startswith("heading_") else ""
                    lines.append(f"{indent}{prefix}{text}")
            if block.get("has_children"):
                walk(block["id"], out, lines, depth + 1, counter)
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]


def list_pets() -> None:
    body = {"filter": {"property": "道具大類", "select": {"equals": PET_CATEGORY}}, "page_size": 100}
    data = request(f"/databases/{ITEM_DB}/query", body)
    for row in data["results"]:
        props = row["properties"]
        rarity = (props.get("稀有度", {}).get("select") or {}).get("name")
        name = rich_text(props["Name"]["title"])
        print(f"{rarity}\t{name}\t{row['id'].replace('-', '')}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:] == ["--list"]:
        list_pets()
        return
    page_id, out_dir = sys.argv[1], pathlib.Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    walk(page_id, out_dir, lines, 0, [0])
    (out_dir / "plan.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_dir / 'plan.md'} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
