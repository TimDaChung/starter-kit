"""Shared Notion REST helpers for plan-dept14-writer and the image skills (avatar-proposal etc.).

Calls go through the department Notion API proxy (pm1 = 一部, pm4 = 四部) with a personal
quarterly credential kept by references/scripts/notion_credentials.py in the starter kit
(~/.config/notion-pm/credentials.json). Optional env override: NOTION_PM_AUTH + NOTION_PM_BASE.
See plan-dept14-writer/references/notion-access.md. Never print the auth value.
"""

from __future__ import annotations

import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator


def _import_credentials() -> Any:
    """Load the kit's notion_credentials module.

    The skill folder is a junction into the kit, so resolve __file__ to the real kit path
    (skills/plan-dept14-writer/scripts -> kit root); ~/starter-kit is the documented
    clone location and serves as a fallback.
    """
    candidates = [
        Path(__file__).resolve().parents[3] / "references" / "scripts",
        Path.home() / "starter-kit" / "references" / "scripts",
    ]
    for folder in candidates:
        if (folder / "notion_credentials.py").is_file():
            if str(folder) not in sys.path:
                sys.path.insert(0, str(folder))
            import notion_credentials  # noqa: PLC0415

            return notion_credentials
    raise SystemExit("[notion_rest] notion_credentials.py not found (looked in "
                     + ", ".join(str(c) for c in candidates) + "); run 'starter 升級'.")


creds = _import_credentials()

VER = "2022-06-28"
# list_format (numbers/letters/roman) is only returned from this version on, and it is
# read-only: create and update both reject it (400, tested 2026-10-05). Used for checks only.
LIST_FORMAT_VER = "2025-09-03"
LIST_FORMATS = ("numbers", "letters", "roman")
TIMEOUT = 75
WRITE_METHODS = ("POST", "PATCH", "PUT", "DELETE")
LINE_DEPT = {"神幣": "一部", "娛樂城": "四部", "鬥地主": "四部", "魚樂園": "四部"}
DEPT_CODE = {"一部": "pm1", "四部": "pm4"}


class CredentialExpired(RuntimeError):
    """The proxy answered error=expired: the personal credential must be refreshed."""


class WriteTimeout(RuntimeError):
    """A write timed out; it may or may not have been applied. Read back before retrying."""


@dataclass(frozen=True)
class Credential:
    base_url: str
    auth: str
    dept: str  # pm1 / pm4

    def __repr__(self) -> str:  # never leak the auth value into logs or tracebacks
        return f"Credential(dept={self.dept!r}, base_url={self.base_url!r}, auth=<hidden {len(self.auth)} chars>)"


def dept_from_id(page_id: str) -> str | None:
    """Workspace fingerprint observed 2026-10-01: '87244fa40' = 一部, 'e22985ac9' = 四部. None if unknown."""
    pid = page_id.replace("-", "").lower()
    if "87244fa40" in pid:
        return "一部"
    if "e22985ac9" in pid:
        return "四部"
    return None


def page_id_from(url_or_id: str) -> str:
    """Accept a Notion URL or a raw id; return the 32-hex id (last match in the path)."""
    s = url_or_id.split("?")[0].split("#")[0]
    hits = re.findall(r"[0-9a-fA-F]{32}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", s)
    if not hits:
        raise SystemExit(f"[notion_rest] no page id in: {url_or_id}")
    return hits[-1].replace("-", "")


def find_token(kind: str = "readonly", dept: str = "一部", line: str | None = None) -> Credential:
    """Return the department credential (one rw credential per dept; there is no read-only one).

    kind is ignored (kept for older callers). A product line (神幣/娛樂城/鬥地主/魚樂園) maps to
    its dept and wins over dept; otherwise dept (一部/四部) is used as given. Write guard rails
    (only the PM's own copy, list the changes and get consent, read back) still apply.
    Env NOTION_PM_AUTH + NOTION_PM_BASE override the stored credential.
    """
    if line:
        dept = LINE_DEPT[line]
    code = DEPT_CODE.get(dept, dept)
    if os.environ.get("NOTION_PM_AUTH") and os.environ.get("NOTION_PM_BASE"):
        return Credential(os.environ["NOTION_PM_BASE"].rstrip("/"), os.environ["NOTION_PM_AUTH"].strip(), code)
    entry = creds.get(code)
    if entry is None:
        raise SystemExit(f"[notion_rest] no Notion credential for {code} ({dept}): install it with the first-install "
                         f"flow in plan-dept14-writer/references/notion-access.md "
                         f"(setup page: notion_credentials.py --refresh-url {code}).")
    note = creds.reminder(code, entry)
    if note:
        print(f"[notion_rest] {note}", file=sys.stderr)
    return Credential(entry["baseUrl"].rstrip("/"), entry["auth"], code)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """allow_redirects=False: a 3xx surfaces as HTTPError instead of being followed."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def build_opener() -> urllib.request.OpenerDirector:
    """No redirects; skip the environment proxy on dev-* hosts (requests' trust_env=False)."""
    handlers: list[urllib.request.BaseHandler] = [_NoRedirect()]
    if socket.gethostname().startswith("dev-"):
        handlers.append(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener(*handlers)


def _is_timeout(exc: BaseException) -> bool:
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return True
    return isinstance(exc, urllib.error.URLError) and isinstance(exc.reason, (TimeoutError, socket.timeout))


class Notion:
    def __init__(self, cred: Credential) -> None:
        if not isinstance(cred, Credential):
            raise TypeError("Notion() takes the Credential returned by find_token(), not a raw token")
        self.cred = cred
        self.opener = build_opener()

    def _expired(self) -> CredentialExpired:
        creds.mark_notified(self.cred.dept, "expired")
        return CredentialExpired(f"Notion credential for {self.cred.dept} expired; refresh it "
                                 f"(see image-studio-style flow in notion-access.md)")

    def call(self, method: str, path: str, body: Any = None, raw: bytes | None = None,
             headers: dict[str, str] | None = None) -> dict[str, Any]:
        h = {"Auth": self.cred.auth, "Notion-Version": VER}
        if body is not None:
            h["Content-Type"] = "application/json"
        if headers:
            h.update(headers)
        data = json.dumps(body).encode() if body is not None else raw
        url = self.cred.base_url + "/v1" + path
        bare = path.split("?")[0]
        read_post = method.upper() == "POST" and (bare.endswith("/query") or bare == "/search")
        is_write = method.upper() in WRITE_METHODS and not read_post
        for attempt in range(4):
            req = urllib.request.Request(url, data=data, headers=h, method=method)
            try:
                with self.opener.open(req, timeout=TIMEOUT) as r:
                    out = json.load(r)
            except urllib.error.HTTPError as e:
                text = e.read().decode(errors="replace")
                try:
                    err = json.loads(text)
                except ValueError:
                    err = {}
                if isinstance(err, dict) and err.get("error") == "expired":
                    raise self._expired() from None
                # 429 is never applied, so it is safe to resend; a 5xx on a write may have landed
                if e.code == 429 or (e.code >= 500 and not is_write):
                    time.sleep(2 + attempt * 2)
                    continue
                raise RuntimeError(f"{method} {path} -> {e.code} {text[:400]}") from None
            except (urllib.error.URLError, TimeoutError, socket.timeout) as e:
                if is_write and _is_timeout(e):
                    raise WriteTimeout(f"{method} {path} timed out after {TIMEOUT}s; it may have been applied. "
                                       f"Read the target back before retrying.") from None
                # reads are safe to resend after a timeout or a dropped connection (WinError 10053/10054)
                if (_is_timeout(e) or not is_write) and attempt < 3:
                    time.sleep(1 + attempt)
                    continue
                raise RuntimeError(f"{method} {path} -> network error {e}") from None
            if isinstance(out, dict) and out.get("error") == "expired":
                raise self._expired()
            return out
        raise RuntimeError(f"{method} {path} -> gave up after retries")

    # ---- files
    def upload_image(self, blob: bytes, ext: str, name: str) -> str:
        ctype = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif", "webp": "image/webp"}.get(ext.lower(), "image/jpeg")
        fu = self.call("POST", "/file_uploads", {"mode": "single_part", "filename": f"{name}.{ext}", "content_type": ctype})
        boundary = "----np" + uuid.uuid4().hex
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}.{ext}\"\r\n"
                f"Content-Type: {ctype}\r\n\r\n").encode() + blob + f"\r\n--{boundary}--\r\n".encode()
        self.call("POST", f"/file_uploads/{fu['id']}/send", raw=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return fu["id"]

    def upload_file(self, path: str | Path, name: str | None = None) -> str:
        p = Path(path)
        return self.upload_image(p.read_bytes(), p.suffix.lstrip("."), name or p.stem)

    def replace_image(self, block_id: str, file_id: str, caption: str | None = None) -> dict[str, Any]:
        """In-place image swap. NOTE: do not send image.type here (API rejects it)."""
        body: dict[str, Any] = {"image": {"file_upload": {"id": file_id}}}
        if caption is not None:
            body["image"]["caption"] = rt(caption)
        return self.call("PATCH", f"/blocks/{block_id}", body)

    # ---- blocks / pages
    def children(self, block_id: str, version: str | None = None) -> list[dict[str, Any]]:
        hdr = {"Notion-Version": version} if version else None
        out: list[dict[str, Any]] = []
        cur = None
        while True:
            d = self.call("GET", f"/blocks/{block_id}/children?page_size=100" + (f"&start_cursor={cur}" if cur else ""), headers=hdr)
            out += d["results"]
            if not d.get("has_more"):
                return out
            cur = d["next_cursor"]

    def walk(self, block_id: str, depth: int = 0, max_depth: int = 6) -> Iterator[tuple[int, dict[str, Any]]]:
        """Yield (depth, block) for the whole subtree."""
        for b in self.children(block_id):
            yield depth, b
            if b.get("has_children") and depth < max_depth:
                yield from self.walk(b["id"], depth + 1, max_depth)

    def check_list_format(self, block_id: str) -> list[dict[str, Any]]:
        """Read-only check of numbered-list display formats against the house style 1.->a.->i.

        API-created lists carry no list_format and render as plain numbers at every level, and
        the API cannot set it. Returns the first item of every list that will look wrong:
        [{"id", "text" (first 20 chars), "level", "have", "want"}]. A list directly under a
        numbered heading ("2.1 ...") is treated as level 1 (a.), which is how the dept templates
        number sections; follow the page's own siblings if they disagree.
        """
        numbered = re.compile(r"\s*\d+(\.\d+)*[.\s]")
        passthrough = ("column_list", "column", "synced_block", "toggle")
        issues: list[dict[str, Any]] = []

        def visit(bid: str, list_level: int | None, under_numbered: bool) -> None:
            # list_level: level of lists found here when inside a list item; None = plain container
            prev_type, cur = None, 0
            for b in self.children(bid, version=LIST_FORMAT_VER):
                t = b["type"]
                payload = b.get(t, {})
                if t.startswith("heading_"):
                    under_numbered = bool(numbered.match(plain(payload.get("rich_text"))))
                if t == "numbered_list_item" and prev_type != "numbered_list_item":
                    cur = list_level if list_level is not None else (1 if under_numbered else 0)
                    want = LIST_FORMATS[cur % 3]
                    have = payload.get("list_format")
                    if (have or "numbers") != want:
                        issues.append({"id": b["id"], "text": plain(payload.get("rich_text"))[:20],
                                       "level": cur, "have": have or "(none = numbers)", "want": want})
                if b.get("has_children"):
                    if t == "numbered_list_item":
                        visit(b["id"], cur + 1, under_numbered)
                    elif t.startswith("heading_"):
                        visit(b["id"], None, under_numbered)
                    elif t in passthrough:
                        visit(b["id"], list_level, under_numbered)
                    else:
                        visit(b["id"], None, False)
                prev_type = t

        visit(block_id, None, False)
        return issues

    def append(self, block_id: str, blocks: list[dict[str, Any]], after: str | None = None,
               log: Callable[[str], Any] | None = None) -> list[dict[str, Any]]:
        res: list[dict[str, Any]] = []
        rest = list(blocks)
        while rest:
            chunk, rest = rest[:100], rest[100:]
            body: dict[str, Any] = {"children": chunk}
            if after:
                body["after"] = after
            r = self.call("PATCH", f"/blocks/{block_id}/children", body)
            res += r["results"]
            if after and r["results"]:
                after = r["results"][-1]["id"]
            if log:
                log(f"  appended {len(chunk)} blocks")
        return res

    def create_page(self, parent_id: str, title: str, blocks: list[dict[str, Any]],
                    log: Callable[[str], Any] | None = None, deep: bool = True) -> dict[str, Any]:
        """deep=True: create with first block only, append the rest (append accepts 3 nesting levels, create only 2)."""
        split = 1 if deep else 100
        page = self.call("POST", "/pages", {"parent": {"page_id": parent_id}, "properties": {"title": {"title": rt(title)}}, "children": blocks[:split]})
        if log:
            log(f"page created {page['url']}")
        self.append(page["id"], blocks[split:], log=log)
        return page

    def count_children(self, block_id: str) -> int:
        return len(self.children(block_id))


def open_page(page_id: str) -> tuple[Notion, dict[str, Any]]:
    """GET a page with the dept guessed from its id; unknown -> try 一部 then 四部 (404 has no side effects)."""
    guess = dept_from_id(page_id)
    tried = []
    for dept in ([guess] if guess else ["一部", "四部"]):
        api = Notion(find_token(dept=dept))
        try:
            return api, api.call("GET", f"/pages/{page_id}")
        except RuntimeError as exc:
            if "-> 404" not in str(exc):
                raise
            tried.append(dept)
    raise SystemExit(f"404 with the {'/'.join(tried)} credential(s): the page is not connected to the integration. "
                     "Ask the page owner to add the connection (… -> Connections).")


# ---------------------------------------------------------------- block builders
def rt(text: Any, bold: bool = False, color: str | None = None, code: bool = False,
       link: str | None = None) -> list[dict[str, Any]]:
    """Rich text. link: URL; linked text is blue unless another color is given (house style)."""
    if link and not color:
        color = "blue"
    out = []
    text = "" if text is None else str(text)
    chunks = [text[i:i + 1900] for i in range(0, len(text), 1900)] or [""]
    for chunk in chunks:
        ann: dict[str, Any] = {}
        if bold:
            ann["bold"] = True
        if code:
            ann["code"] = True
        if color:
            ann["color"] = color
        item: dict[str, Any] = {"type": "text", "text": {"content": chunk, **({"link": {"url": link}} if link else {})}}
        if ann:
            item["annotations"] = ann
        out.append(item)
    return out


def heading(level: int, text: str) -> dict[str, Any]:
    return {"object": "block", "type": f"heading_{level}", f"heading_{level}": {"rich_text": rt(text)}}


def para(text: str, **kw: Any) -> dict[str, Any]:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text, **kw)}}


def bullet(text: str, **kw: Any) -> dict[str, Any]:
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(text, **kw)}}


def callout(text: str, emoji: str = "📌", color: str = "gray_background") -> dict[str, Any]:
    return {"object": "block", "type": "callout", "callout": {"rich_text": rt(text), "icon": {"type": "emoji", "emoji": emoji}, "color": color}}


def divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def table(rows: list[list[Any]], header: bool = True) -> dict[str, Any]:
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


def image_block(file_id: str, caption: str = "") -> dict[str, Any]:
    return {"object": "block", "type": "image", "image": {"type": "file_upload", "file_upload": {"id": file_id}, "caption": rt(caption)}}


def column_list(*columns: list[dict[str, Any]]) -> dict[str, Any]:
    def col(kids: list[dict[str, Any]]) -> dict[str, Any]:
        return {"object": "block", "type": "column", "column": {"children": kids}}

    return {"object": "block", "type": "column_list", "column_list": {"children": [col(c) for c in columns]}}


def plain(rich: list[dict[str, Any]] | None) -> str:
    return "".join(x.get("plain_text", "") for x in rich or [])


def _cli() -> None:
    """python notion_rest.py check-lists <url or id>  (read-only)"""
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 3 or sys.argv[1] != "check-lists":
        raise SystemExit(_cli.__doc__)
    pid = page_id_from(sys.argv[2])
    guess = dept_from_id(pid)
    for dept in ([guess] if guess else ["一部", "四部"]):
        try:
            issues = Notion(find_token(dept=dept)).check_list_format(pid)
            break
        except RuntimeError as e:
            if "-> 404" not in str(e):
                raise
    else:
        raise SystemExit("404 with every dept credential: the page is not connected to the integration.")
    fmt = {"numbers": "1.", "letters": "a.", "roman": "i."}
    if not issues:
        print("OK: every numbered list follows 1.->a.->i.")
    for x in issues:
        print(f"{x['id']}  level {x['level']}  now {x['have']}  -> set to {fmt[x['want']]}  「{x['text']}」")


if __name__ == "__main__":
    _cli()
