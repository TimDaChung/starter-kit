"""Write a Markdown plan into a Notion page (the PM's template copy) through the dept proxy.

Dry run by default: prints what would be written / replaced. Add --write to do it.

  python md2notion.py <plan.md> <page url or id>                      # preview whole file
  python md2notion.py <plan.md> <page> --section "3.2. Boss靜態" --write
      replace only that section's content: the heading block stays (links, comments and
      its id survive), everything under it up to the next heading of the same or higher
      level is swapped for the Markdown version. Repeat --section for several sections.
  python md2notion.py <plan.md> <page> --write [--clear-old] [--start "1. 基本資訊"]
      append the whole file (from the first H1, or from --start); --clear-old then deletes
      the blocks that were on the page before. Only for a fresh copy: it wipes PM edits.

Markdown understood:
  # / ## / ###                 heading_1..3
  1. text   - text             numbered / bulleted items, nested by indentation
  | a | b |                    table; header row by default. Put <!-- 表頭:首欄 --> (or
                               首列 / 無) on the line before to match the template's table
  ```mermaid ... ```           code block; a following 《caption》 line becomes its caption
  ![《圖名》](path.png)         image; alt becomes the caption (dept 4). Dept 1 puts 《n.圖名》 on its own
                               line right above the image and leaves alt empty: that line goes to
                               the image column too. Path TODO -> the alt text as a red placeholder,
                               worded as the template does (【待補】 / 圖片放置區 / 圖後補)
  > text                       quote
  ---                          divider
  <span color="red">x</span>  **bold**  [text](url)   inline colour / bold / link (blue)
A section (between headings or dividers) that contains images is laid out as two columns:
text left, images right (house style). API nesting limits are handled by writing parents
first and children afterwards.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from notion_rest import Notion, image_block, open_page, page_id_from, rt  # noqa: E402

INLINE = re.compile(r'<span color="(\w+)">(.*?)</span>|\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)')
HEADER_HINT = re.compile(r"<!--\s*表頭\s*[:：]\s*(首列|首欄|無)\s*-->")
Node = dict[str, Any]


# ------------------------------------------------------------------ parsing (pure)
def rich(s: str, color: str | None = None, bold: bool = False) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    pos = 0
    for m in INLINE.finditer(s):
        if m.start() > pos:
            out += rt(s[pos:m.start()], bold=bold, color=color)
        if m.group(1):
            out += rich(m.group(2), color=m.group(1), bold=bold)
        elif m.group(3):
            out += rich(m.group(3), color=color, bold=True)
        else:
            out += rt(m.group(4), bold=bold, color=color, link=m.group(5))
        pos = m.end()
    if pos < len(s):
        out += rt(s[pos:], bold=bold, color=color)
    return [x for x in out if x["text"]["content"]]


def blk(t: str, text: str) -> Node:
    return {"object": "block", "type": t, t: {"rich_text": rich(text)}}


def parse(lines: list[str]) -> list[Node]:
    """Top-level nodes; list items carry nested children in "_kids"; images are {"_image", "_cap"}."""
    out: list[Node] = []
    stack: list[tuple[int, Node]] = []  # (indent, list item) for nesting
    hint = ""
    i = 0

    def place(node: Node, ind: int) -> None:
        nonlocal stack
        while stack and stack[-1][0] >= ind:
            stack.pop()
        if ind > 0 and stack:
            stack[-1][1].setdefault("_kids", []).append(node)
        else:
            out.append(node)
            stack = []

    while i < len(lines):
        ln = lines[i].rstrip("\n").replace("\t", "    ")
        s = ln.strip()
        ind = len(ln) - len(ln.lstrip(" "))
        if not s:
            i += 1
            continue
        h = HEADER_HINT.fullmatch(s)
        if h:
            hint, i = h.group(1), i + 1
            continue
        if s.startswith("<!--"):
            i += 1
            continue
        if not s.startswith("|"):
            hint = ""
        if s.startswith("```"):
            lang = s[3:].strip() or "plain text"
            src, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                src.append(lines[i].rstrip("\n"))
                i += 1
            i += 1
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            cap = ""
            if j < len(lines) and re.fullmatch(r"《.*》", lines[j].strip()):
                k = j + 1
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if not (k < len(lines) and re.match(r"!\[.*?\]\(.*?\)", lines[k].strip())):  # dept-1 figure title → image
                    cap, i = lines[j].strip(), j + 1
            place({"object": "block", "type": "code",
                   "code": {"rich_text": rt("\n".join(src)), "language": lang, "caption": rt(cap)}}, ind)
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells if c):
                    rows.append(cells)
                i += 1
            width = max(len(r) for r in rows)
            trs = [{"type": "table_row", "table_row": {"cells": [rich(c.replace("<br/>", "\n").replace("<br>", "\n"))
                                                                 for c in r + [""] * (width - len(r))]}} for r in rows]
            place({"object": "block", "type": "table",
                   "table": {"table_width": width, "has_column_header": hint in ("", "首列"),
                             "has_row_header": hint == "首欄", "children": trs}}, ind)
            hint = ""
            continue
        m = re.match(r"(#{1,3}) (.*)", s)
        if m and ind == 0:
            out.append(blk(f"heading_{len(m.group(1))}", m.group(2)))
            stack, i = [], i + 1
            continue
        if s == "---":
            out.append({"object": "block", "type": "divider", "divider": {}})
            stack, i = [], i + 1
            continue
        mi = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", s)
        if mi:
            out.append({"_image": mi.group(2), "_cap": mi.group(1)})  # group_columns moves it; keep list nesting
            i += 1
            j = i  # skip a caption line that only repeats the alt text
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip() == mi.group(1):
                i = j + 1
            continue
        if s.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            place({"object": "block", "type": "quote", "quote": {"rich_text": rich("\n".join(quote))}}, ind)
            continue
        mn = re.match(r"\d+\. (.*)", s)
        mb = re.match(r"[-*] (.*)", s)
        if mn or mb:
            node = blk("numbered_list_item" if mn else "bulleted_list_item", (mn or mb).group(1))
            place(node, ind)
            stack.append((ind, node))
        else:
            place(blk("paragraph", s), ind)
        i += 1
    return out


def group_columns(nodes: list[Node]) -> list[Node]:
    """Sections (between headings / dividers) with images -> {"_columns": [text, images]}."""
    res: list[Node] = []
    sec: list[Node] = []

    def is_fig_title(n: Node) -> bool:
        return n.get("type") == "paragraph" and bool(re.fullmatch(r"《.*》", plain(n["paragraph"]["rich_text"])))

    def flush() -> None:
        groups: list[list[Node]] = []  # each: [image] or [《title》 paragraph, image]
        text: list[Node] = []
        k = 0
        while k < len(sec):
            n = sec[k]
            if is_fig_title(n) and k + 1 < len(sec) and "_image" in sec[k + 1]:
                groups.append([n, sec[k + 1]])
                k += 2
                continue
            (groups.append([n]) if "_image" in n else text.append(n))
            k += 1
        if not groups:
            res.extend(sec)
        elif not text:  # nothing for a left column: stack the images (column_list needs >= 2 columns)
            res.extend(x for g in groups for x in g)
        else:
            res.append({"_columns": [text, [x for g in groups for x in g]]})

    for n in nodes:
        if n.get("type", "").startswith("heading_") or n.get("type") == "divider":
            flush()
            sec = []
            res.append(n)
        else:
            sec.append(n)
    flush()
    return res


def plain(rich_text: list[dict[str, Any]] | None) -> str:
    """Text of rich text from the API (plain_text) or built locally (text.content)."""
    return "".join(x.get("plain_text") or x.get("text", {}).get("content", "") for x in rich_text or [])


def heading_level(b: Node) -> int:
    t = b.get("type", "")
    return int(t[-1]) if t.startswith("heading_") else 0


def heading_text(b: Node) -> str:
    t = b.get("type", "")
    return re.sub(r"\s+", "", plain(b[t]["rich_text"])) if heading_level(b) else ""


def section_span(blocks: list[Node], title: str) -> tuple[int, int]:
    """Index of the heading titled `title` and the end (exclusive) of its content: up to the next
    heading of the same or higher level, leaving trailing dividers in place."""
    key = re.sub(r"\s+", "", title)
    hits = [k for k, b in enumerate(blocks) if heading_text(b) == key]
    if len(hits) != 1:
        raise SystemExit(f"section {title!r}: {len(hits)} matching headings (need exactly 1)")
    start = hits[0]
    level = heading_level(blocks[start])
    end = start + 1
    while end < len(blocks) and not (0 < heading_level(blocks[end]) <= level):
        end += 1
    while end > start + 1 and blocks[end - 1].get("type") == "divider":
        end -= 1
    return start, end


def start_index(nodes: list[Node], start: str | None) -> int:
    """Drop what comes before the plan body (title / property lines)."""
    if start:
        return section_span(nodes, start)[0]
    return next((k for k, n in enumerate(nodes) if n.get("type") == "heading_1"), 0)


def image_paths(nodes: list[Node]) -> list[str]:
    out: list[str] = []
    for n in nodes:
        for x in ([n] if "_image" in n else [y for col in n.get("_columns", []) for y in col]):
            if "_image" in x and x["_image"].strip().upper() != "TODO":
                out.append(x["_image"])
    return out


def human_edited(blocks: list[Node], bot_id: str) -> list[Node]:
    """Blocks whose last editor is not the writer integration: a person touched them in Notion."""
    return [b for b in blocks if (b.get("last_edited_by") or {}).get("id") not in (None, bot_id)]


def describe_block(b: Node) -> str:
    t = b["type"]
    x = b.get(t, {})
    text = plain(x.get("rich_text")) if isinstance(x, dict) else ""
    return f"{t} {text[:30]}".rstrip()


def describe(n: Node) -> str:
    if "_columns" in n:
        return f"columns ×{len(n['_columns'])}"
    if "_image" in n:
        return f"image {n['_cap']}"
    t = n["type"]
    text = plain(n[t].get("rich_text")) if isinstance(n.get(t), dict) else ""
    return f"{t} {text[:30]}"


# ------------------------------------------------------------------ writing
class Writer:
    def __init__(self, api: Notion, base: Path) -> None:
        self.api, self.base, self.uploads = api, base, {}

    def to_block(self, n: Node) -> Node:
        if "_image" not in n:
            return n
        if n["_image"].strip().upper() == "TODO":
            return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(n["_cap"] or "圖後補", color="red")}}
        p = (self.base / n["_image"]).resolve()
        if p not in self.uploads:
            self.uploads[p] = self.api.upload_file(p)  # waits until status == uploaded
            print("  uploaded", p.name)
        return image_block(self.uploads[p], n["_cap"])

    def write(self, parent: str, items: list[Node], after: str | None = None) -> list[Node]:
        """Append items under parent; children go in a second pass (API nesting limits)."""
        strip = lambda b: {k: v for k, v in b.items() if not k.startswith("_")}  # noqa: E731
        payload, pending = [], []
        for n in items:
            if "_columns" in n:
                cols = [{"object": "block", "type": "column",
                         "column": {"children": [strip(self.to_block(x)) for x in col]}} for col in n["_columns"]]
                payload.append({"object": "block", "type": "column_list", "column_list": {"children": cols}})
                pending.append(("cols", n["_columns"]))
            else:
                payload.append(strip(self.to_block(n)))
                pending.append(("kids", n.get("_kids")))
        created = self.api.append(parent, payload, after=after) if payload else []
        if len(created) != len(payload):
            raise RuntimeError(f"appended {len(payload)} blocks but the API returned {len(created)}")
        for (kind, data), c in zip(pending, created):
            if kind == "kids" and data:
                self.write(c["id"], data)
            elif kind == "cols":
                for col_id, col in zip([x["id"] for x in self.api.children(c["id"])], data):
                    for src, made in zip(col, self.api.children(col_id)):
                        if src.get("_kids"):
                            self.write(made["id"], src["_kids"])
        return created


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Markdown plan -> Notion page (dry run unless --write).")
    ap.add_argument("md")
    ap.add_argument("page")
    ap.add_argument("--section", action="append", default=[], help="work on this section only (heading text); default replaces its content")
    ap.add_argument("--append", action="store_true", help="with --section: add the file's section content at the end of the page section, delete nothing")
    ap.add_argument("--only", choices=["table"], help="with --section: swap only these blocks (top level in the section, same count), keep everything else")
    ap.add_argument("--force", action="store_true", help="also replace blocks a person edited by hand (default: list them and stop)")
    ap.add_argument("--start", help="whole-file mode: first heading to write (default: first H1)")
    ap.add_argument("--clear-old", action="store_true", help="whole-file mode: delete the page's previous blocks")
    ap.add_argument("--write", action="store_true", help="actually write (default: preview only)")
    args = ap.parse_args()

    if args.section and (args.clear_old or args.start):
        ap.error("--section cannot be combined with --clear-old / --start")
    if (args.append or args.only) and not args.section:
        ap.error("--append / --only need --section")
    if args.append and args.only:
        ap.error("--append and --only are exclusive")
    md = Path(args.md)
    nodes = group_columns(parse(md.read_text(encoding="utf-8-sig").splitlines()))
    missing = [p for p in image_paths(nodes) if not (md.parent / p).is_file()]
    if missing:
        raise SystemExit("image file(s) not found next to the .md: " + ", ".join(missing))
    pid = page_id_from(args.page)
    api, _ = open_page(pid)
    page = api.children(pid)
    w = Writer(api, md.parent)

    if args.section:
        plans: list[tuple[str, str, list[Node], list[Node]]] = []  # (title, insert-after id, new nodes, old blocks to delete)
        spans: list[tuple[int, int]] = []
        for title in args.section:
            ms, me = section_span(nodes, title)
            ps, pe = section_span(page, title)
            if any(ps < e and s < pe for s, e in spans):
                raise SystemExit(f"section {title!r} overlaps another --section target; pass the outer one only")
            spans.append((ps, pe))
            new, old = nodes[ms + 1:me], page[ps + 1:pe]
            if args.only == "table":
                new = [n for n in new if n.get("type") == "table"]
                old = [b for b in old if b["type"] == "table"]
                if len(new) != len(old):
                    raise SystemExit(f"[{title}] {len(old)} table(s) on the page vs {len(new)} in the file; --only table needs the same count")
                plans += [(title, b["id"], [n], [b]) for n, b in zip(new, old)]  # each new table goes right after the old one
                print(f"[{title}] swap {len(old)} table(s), keep the rest")
            elif args.append:
                plans.append((title, (old[-1] if old else page[ps])["id"], new, []))
                print(f"[{title}] append {len(new)} block(s) after the section's last block:")
            else:
                plans.append((title, page[ps]["id"], new, old))
                print(f"[{title}] replace {len(old)} blocks on the page with {len(new)} from the file:")
            for n in new:
                print("   +", describe(n))
        touched = human_edited([b for *_, old in plans for b in old], api.call("GET", "/users/me")["id"])
        if touched:
            print("blocks last edited by a person, not the writer bot (PM hand edits?):")
            for b in touched:
                print("   !", describe_block(b))
            if not args.force:
                raise SystemExit("stopped: confirm with the PM what to keep, then rerun with --force to replace them")
        if not args.write:
            print("dry run: add --write to apply")
            return
        for title, after_id, new, old in plans:
            w.write(pid, new, after=after_id)  # insert first, so a failure never leaves a hole
            for b in old:
                api.call("DELETE", f"/blocks/{b['id']}")
            print(f"[{title}] done")
    else:
        body = nodes[start_index(nodes, args.start):]
        print(f"append {len(body)} top-level nodes" + (f", then delete {len(page)} existing blocks" if args.clear_old else ""))
        for n in body:
            print("   +", describe(n))
        if not args.write:
            print("dry run: add --write to apply")
            return
        w.write(pid, body)
        if args.clear_old:
            for b in page:
                api.call("DELETE", f"/blocks/{b['id']}")
    print(f"written; uploads: {len(w.uploads)}. Read the page back before telling the PM it is done.")


if __name__ == "__main__":
    main()
