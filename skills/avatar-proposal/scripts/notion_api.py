"""Shared Notion REST helpers for the avatar-proposal skill.

Token: env NOTION_KEY wins. Otherwise read from the department template share
(see plan-dept14-writer/references/notion-access.md). Never print the token.
"""
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

NOTION = "https://api.notion.com/v1"
VER = "2022-06-28"
SHARE_ROOT = r"grp.product.pm1\2. 產品改造\一四部企劃範本"
TOKEN_FILES = {
    "readonly": [r"一部readonly_token.txt"],
    "readwrite": [r"神幣(一部)\一部readwrite_token.txt"],
}


def find_token(kind="readonly"):
    """Return token string. kind = readonly | readwrite. Env NOTION_KEY overrides."""
    if os.environ.get("NOTION_KEY"):
        return os.environ["NOTION_KEY"]
    for drive in ("X:", "Y:"):
        for rel in TOKEN_FILES[kind]:
            p = Path(f"{drive}\\{SHARE_ROOT}\\{rel}")
            try:
                if p.exists():
                    return p.read_text(encoding="utf-8").strip()
            except OSError:
                continue
    raise SystemExit(f"[notion_api] no {kind} token: set NOTION_KEY or connect the X:/Y: share "
                     f"(see plan-dept14-writer/references/notion-access.md). "
                     + ("Readwrite tokens are held by Tim only; ask him to run this step." if kind == "readwrite" else ""))


class Notion:
    def __init__(self, token):
        self.token = token

    def call(self, method, path, body=None, raw=None, headers=None):
        h = {"Authorization": f"Bearer {self.token}", "Notion-Version": VER}
        if body is not None:
            h["Content-Type"] = "application/json"
        if headers:
            h.update(headers)
        data = json.dumps(body).encode() if body is not None else raw
        req = urllib.request.Request(NOTION + path, data=data, headers=h, method=method)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                msg = e.read().decode()[:400]
                if e.code == 429 or e.code >= 500:
                    time.sleep(2 + attempt * 2)
                    continue
                raise RuntimeError(f"{method} {path} -> {e.code} {msg}")
        raise RuntimeError(f"{method} {path} -> gave up after retries")

    # ---- files
    def upload_image(self, blob, ext, name):
        ctype = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif", "webp": "image/webp"}.get(ext.lower(), "image/jpeg")
        fu = self.call("POST", "/file_uploads", {"mode": "single_part", "filename": f"{name}.{ext}", "content_type": ctype})
        boundary = "----np" + uuid.uuid4().hex
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}.{ext}\"\r\n"
                f"Content-Type: {ctype}\r\n\r\n").encode() + blob + f"\r\n--{boundary}--\r\n".encode()
        self.call("POST", f"/file_uploads/{fu['id']}/send", raw=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return fu["id"]

    def upload_file(self, path, name=None):
        p = Path(path)
        return self.upload_image(p.read_bytes(), p.suffix.lstrip("."), name or p.stem)

    def replace_image(self, block_id, file_id, caption=None):
        """In-place image swap. NOTE: do not send image.type here (API rejects it)."""
        body = {"image": {"file_upload": {"id": file_id}}}
        if caption is not None:
            body["image"]["caption"] = rt(caption)
        return self.call("PATCH", f"/blocks/{block_id}", body)

    # ---- blocks / pages
    def children(self, block_id):
        out, cur = [], None
        while True:
            d = self.call("GET", f"/blocks/{block_id}/children?page_size=100" + (f"&start_cursor={cur}" if cur else ""))
            out += d["results"]
            if not d.get("has_more"):
                return out
            cur = d["next_cursor"]

    def walk(self, block_id, depth=0, max_depth=6):
        """Yield (depth, block) for the whole subtree."""
        for b in self.children(block_id):
            yield depth, b
            if b.get("has_children") and depth < max_depth:
                yield from self.walk(b["id"], depth + 1, max_depth)

    def append(self, block_id, blocks, after=None, log=None):
        res = []
        rest = list(blocks)
        while rest:
            chunk, rest = rest[:100], rest[100:]
            body = {"children": chunk}
            if after:
                body["after"] = after
            r = self.call("PATCH", f"/blocks/{block_id}/children", body)
            res += r["results"]
            if after and r["results"]:
                after = r["results"][-1]["id"]
            if log:
                log(f"  appended {len(chunk)} blocks")
        return res

    def create_page(self, parent_id, title, blocks, log=None, deep=True):
        """deep=True: create with first block only, append the rest (append accepts 3 nesting levels, create only 2)."""
        split = 1 if deep else 100
        page = self.call("POST", "/pages", {"parent": {"page_id": parent_id}, "properties": {"title": {"title": rt(title)}}, "children": blocks[:split]})
        if log:
            log(f"page created {page['url']}")
        self.append(page["id"], blocks[split:], log=log)
        return page

    def count_children(self, block_id):
        return len(self.children(block_id))


# ---------------------------------------------------------------- block builders
def rt(text, bold=False, color=None, code=False):
    out = []
    text = "" if text is None else str(text)
    chunks = [text[i:i + 1900] for i in range(0, len(text), 1900)] or [""]
    for chunk in chunks:
        ann = {}
        if bold:
            ann["bold"] = True
        if code:
            ann["code"] = True
        if color:
            ann["color"] = color
        item = {"type": "text", "text": {"content": chunk}}
        if ann:
            item["annotations"] = ann
        out.append(item)
    return out


def heading(level, text):
    return {"object": "block", "type": f"heading_{level}", f"heading_{level}": {"rich_text": rt(text)}}


def para(text, **kw):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text, **kw)}}


def bullet(text, **kw):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(text, **kw)}}


def callout(text, emoji="📌", color="gray_background"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": rt(text), "icon": {"type": "emoji", "emoji": emoji}, "color": color}}


def divider():
    return {"object": "block", "type": "divider", "divider": {}}


def table(rows, header=True):
    """rows: list of lists; a cell is a str or (str, {bold/color}) tuple."""
    width = max(len(r) for r in rows)
    children = []
    for r in rows:
        cells = []
        for c in list(r) + [""] * (width - len(r)):
            if isinstance(c, tuple):
                cells.append(rt(c[0], **c[1]))
            else:
                cells.append(rt(str(c)) if c != "" else [])
        children.append({"type": "table_row", "table_row": {"cells": cells}})
    return {"object": "block", "type": "table", "table": {"table_width": width, "has_column_header": header, "has_row_header": False, "children": children}}


def image_block(file_id, caption=""):
    return {"object": "block", "type": "image", "image": {"type": "file_upload", "file_upload": {"id": file_id}, "caption": rt(caption)}}


def column_list(*columns):
    col = lambda kids: {"object": "block", "type": "column", "column": {"children": kids}}
    return {"object": "block", "type": "column_list", "column_list": {"children": [col(c) for c in columns]}}


def plain(rich):
    return "".join(x.get("plain_text", "") for x in rich or [])
