"""Shared Notion REST helpers for plan-dept14-writer and the image skills (avatar-proposal etc.).

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
READONLY = {"一部": "一部readonly_token.txt", "四部": "四部readonly_token.txt"}
READWRITE = {"神幣": r"神幣(一部)\一部readwrite_token.txt", "娛樂城": r"娛樂城(四部)\娛樂城readwrite_token.txt",
             "鬥地主": r"鬥地主(四部)\鬥地主readwrite_token.txt", "魚樂園": r"魚樂園(四部)\魚樂園readwrite_token.txt"}
LINE_DEPT = {"神幣": "一部", "娛樂城": "四部", "鬥地主": "四部", "魚樂園": "四部"}


def dept_from_id(page_id):
    """Workspace fingerprint observed 2026-10-01: '87244fa40' = 一部, 'e22985ac9' = 四部. None if unknown."""
    pid = page_id.replace("-", "").lower()
    if "87244fa40" in pid:
        return "一部"
    if "e22985ac9" in pid:
        return "四部"
    return None


def page_id_from(url_or_id):
    """Accept a Notion URL or a raw id; return the 32-hex id (last match in the path)."""
    import re
    s = url_or_id.split("?")[0].split("#")[0]
    hits = re.findall(r"[0-9a-fA-F]{32}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", s)
    if not hits:
        raise SystemExit(f"[notion_rest] no page id in: {url_or_id}")
    return hits[-1].replace("-", "")


def _read_share(rel):
    for drive in ("X:", "Y:"):
        p = Path(f"{drive}\\{SHARE_ROOT}\\{rel}")
        try:
            if p.exists():
                return p.read_text(encoding="utf-8").strip()
        except OSError:
            continue
    return None


def find_token(kind="readonly", dept="一部", line=None):
    """kind=readonly -> dept 一部/四部; kind=readwrite -> line 神幣/娛樂城/鬥地主/魚樂園 (default 神幣).
    Env NOTION_KEY overrides everything. Never print the token."""
    if os.environ.get("NOTION_KEY"):
        return os.environ["NOTION_KEY"]
    if kind == "readonly":
        tok = _read_share(READONLY[dept])
    else:
        tok = _read_share(READWRITE[line or "神幣"])
    if tok:
        return tok
    raise SystemExit(f"[notion_rest] no {kind} token ({dept if kind == 'readonly' else (line or '神幣')}): set NOTION_KEY or connect the X:/Y: share "
                     f"(see plan-dept14-writer/references/notion-access.md)."
                     + (" Readwrite tokens are held by Tim only; ask him to run this step." if kind == "readwrite" else ""))


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
