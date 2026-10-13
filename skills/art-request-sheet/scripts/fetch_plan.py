"""Read a Notion plan page via the department Notion proxy: dump text and download media.

Credential and department come from plan-dept14-writer/scripts/notion_rest.py
(personal pm1/pm4 credential, see plan-dept14-writer/references/notion-access.md).
The department is guessed from the page id fingerprint; if unknown, 一部 then 四部
are tried, and two 404s mean the page is not connected to the integration.

Writes into <out_dir>:
  plan.md   page title + blocks in reading order. Inline marks keep what the
            art sheet needs:
              <span color="red">..</span>      red text (-> red runs in the sheet)
              <span color="gray_background">..</span> / green_background
              ~~..~~                            strikethrough (revision marks)
            media lines look like: [image 05_主介面_已達門檻.jpg]
            table rows are one line each, cells joined by " | "; a line
            break inside a cell is written as <br> and "|" as \\|
  NN_<caption>.<ext>  every image / video / file block, downloaded right away
            (signed URLs expire). Caption = block caption, else the nearest
            preceding 《..》 line, else the original file name.

Usage:
  python fetch_plan.py <notion url or page id> <out_dir>
  python fetch_plan.py --list <kind>        kind: pets / bosses / cannons / wings / weapons

--list prints one row per page of the 魚樂園 書 databases (category, rarity, title,
page id, tab-separated) so the design skills can pick a page without the MCP.
This is the single fetch script for the kit; pet-evolution/scripts/fetch_plan.py is
only a shim that forwards here.
"""
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plan-dept14-writer" / "scripts"))
from notion_rest import Notion, find_token, open_page, page_id_from  # noqa: E402

MEDIA = ("image", "video", "file", "pdf")
ITEM_BOOK = "217e22985ac9817d8a65c6a6ed6a135c"  # 魚樂園 道具之書 (parent of cannon/wing/pet/weapon pages)
FISH_BOOK = "21de22985ac98032a2eef46efabab95b"  # 魚樂園 魚類之書
# --list kind -> (database id, select property, option values to keep; empty = keep all)
LISTS = {
    "pets": (ITEM_BOOK, "道具大類", ["8. 寵物"]),
    "cannons": (ITEM_BOOK, "道具大類", ["1. 炮台"]),
    "wings": (ITEM_BOOK, "道具大類", ["2. 翅膀"]),
    "weapons": (ITEM_BOOK, "道具大類", ["33. 武具"]),
    "bosses": (FISH_BOOK, "類別", ["活動Boss", "場景Boss", "特殊魚"]),
}
KEEP_COLORS = ("red", "gray_background", "green_background", "red_background", "yellow_background")
BAD_NAME = re.compile(r'[\\/:*?"<>|\r\n]+')


def styled(items: list) -> str:
    out = []
    for t in items:
        text = t.get("plain_text", "")
        if not text:
            continue
        ann = t.get("annotations", {})
        if ann.get("strikethrough"):
            text = f"~~{text}~~"
        color = ann.get("color", "default")
        if color in KEEP_COLORS:
            text = f'<span color="{color}">{text}</span>'
        out.append(text)
    return "".join(out)


def table_cell(items: list) -> str:
    """One table cell for plan.md: line breaks -> <br>, "|" escaped, so a row stays on one line."""
    text = styled(items).replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("|", "\\|").replace("\n", "<br>")


def plain(items: list) -> str:
    return "".join(t.get("plain_text", "") for t in items)


class Walker:
    def __init__(self, api: Notion, out: Path) -> None:
        self.api = api
        self.out = out
        self.lines: list[str] = []
        self.n_media = 0
        self.caption = ""

    def children(self, block_id: str) -> list[dict]:
        results, cursor = [], None
        while True:
            q = "?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
            data = self.api.call("GET", f"/blocks/{block_id}/children{q}")
            results += data["results"]
            if not data.get("has_more"):
                return results
            cursor = data["next_cursor"]

    def save_media(self, kind: str, payload: dict, indent: str) -> None:
        src = payload.get("file", {}).get("url") or payload.get("external", {}).get("url")
        if not src:
            return
        self.n_media += 1
        orig = urllib.parse.unquote(src.split("?")[0].rsplit("/", 1)[-1])
        ext = Path(orig).suffix.lower() or (".mp4" if kind == "video" else ".png")
        label = plain(payload.get("caption", [])) or self.caption or Path(orig).stem
        name = f"{self.n_media:02d}_{BAD_NAME.sub('_', label).strip()[:40]}{ext}"
        try:
            urllib.request.urlretrieve(src, self.out / name)
            self.lines.append(f"{indent}[{kind} {name}]")
        except (urllib.error.URLError, OSError) as exc:
            self.lines.append(f"{indent}[{kind} {name} DOWNLOAD FAILED: {exc}]")
            print(f"FAIL {name}: {exc}")

    def walk(self, block_id: str, depth: int = 0) -> None:
        number = 0
        for b in self.children(block_id):
            kind, indent = b["type"], "    " * depth
            payload = b.get(kind, {})
            number = number + 1 if kind == "numbered_list_item" else 0
            if kind in MEDIA:
                self.save_media(kind, payload, indent)
            elif kind == "table_row":
                self.lines.append(indent + " | ".join(table_cell(c) for c in payload.get("cells", [])))
            elif kind == "child_page":
                self.lines.append(f"{indent}[child page: {payload.get('title', '')}]")
                continue
            elif kind == "divider":
                self.lines.append(f"{indent}---")
            else:
                text = styled(payload.get("rich_text", []))
                if text:
                    m = re.search(r"《([^》]+)》", plain(payload.get("rich_text", [])))
                    if m:
                        self.caption = m.group(1)
                    if kind.startswith("heading_"):
                        text = "#" * int(kind[-1]) + " " + text
                    elif kind == "bulleted_list_item":
                        text = "- " + text
                    elif kind == "numbered_list_item":
                        text = f"{number}. " + text
                    elif kind == "to_do":
                        text = ("[x] " if payload.get("checked") else "[ ] ") + text
                    self.lines.append(indent + text)
            if kind == "synced_block" and payload.get("synced_from"):
                self.walk(payload["synced_from"]["block_id"], depth)
            elif b.get("has_children"):
                inner = depth if kind in ("column_list", "column", "synced_block", "table") else depth + 1
                self.walk(b["id"], inner)


def query_all(api: Notion, db_id: str, body: dict | None = None) -> list[dict]:
    """Every row of a database query (read-only POST), following the cursor."""
    rows: list[dict] = []
    cursor = None
    while True:
        payload: dict = {"page_size": 100, **(body or {})}
        if cursor:
            payload["start_cursor"] = cursor
        data = api.call("POST", f"/databases/{db_id}/query", payload)
        rows += data["results"]
        if not data.get("has_more"):
            return rows
        cursor = data["next_cursor"]


def list_lines(rows: list[dict], prop: str, keep: list[str]) -> list[str]:
    """One tab-separated line per kept row: category, rarity, title, page id (no dashes)."""
    out = []
    for row in rows:
        props = row["properties"]
        category = (props.get(prop, {}).get("select") or {}).get("name")
        if keep and category not in keep:
            continue
        rarity = (props.get("稀有度", {}).get("select") or {}).get("name") or ""
        title = next((plain(v["title"]) for v in props.values() if v["type"] == "title"), "")
        out.append(f"{category}\t{rarity}\t{title}\t{row['id'].replace('-', '')}")
    return out


def list_rows(kind: str, api: Notion | None = None) -> None:
    if kind not in LISTS:
        sys.exit(f"unknown list kind {kind!r}; choose from {', '.join(LISTS)}")
    db_id, prop, keep = LISTS[kind]
    api = api or Notion(find_token(dept="四部"))
    for line in list_lines(query_all(api, db_id), prop, keep):
        print(line)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 3 and sys.argv[1] == "--list":
        list_rows(sys.argv[2])
        return
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    page_id, out = page_id_from(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    api, page = open_page(page_id)
    title = next((plain(p["title"]) for p in page["properties"].values() if p["type"] == "title"), "")
    w = Walker(api, out)
    w.lines.append(f"# {title}")
    w.walk(page_id)
    (out / "plan.md").write_text("\n".join(w.lines), encoding="utf-8")
    print(f"wrote {out / 'plan.md'} ({len(w.lines)} lines, {w.n_media} media files)")


if __name__ == "__main__":
    main()
