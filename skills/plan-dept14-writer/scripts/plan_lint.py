"""Deterministic lint for dept plan pages (plan-doc-qa step 1.5, plan-dept14-writer pre-delivery).

Read-only. Checks that do not depend on model attention, so every run gives the same answer:
  1. heading numbering: gaps and duplicates per parent (4.1, 4.2, 4.4 -> 4.3 missing)
  2. cross references: "見 3.9.1" / "見 **2.3.B.6**" must resolve to a heading or a numbered item
  3. (opt-in, --lists) lists not shown as Notion's default 1.->a.->i. (same as notion_rest.py
     check-lists); API-written lists already are, so only manually formatted pages hit this
  4. 「後補」 placeholders with their section
  5. mermaid flowcharts: every decision node with its exits, for the semantic check against the
     rule chapter (done by the reviewer, not here); flags decisions with < 2 exits or unlabeled exits

A synced block starts a new numbering scope (a sub-plan embedded in a version page restarts at 1.).

Usage: python plan_lint.py <url or id> [--json out.json] [--lists]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

HEADING_NUM = re.compile(r"^\s*(\d+(?:\.\d+)*)(?:\.([A-Z]))?\.?(?=\s|$|[^\d.A-Za-z])")
REF = re.compile(r"見\s*\**\s*(\d+(?:\.(?:\d+|[A-Z]))*)\.?")
PLACEHOLDER = "後補"
# Labelled forms: A -- x --> B (solid), A -. x .-> B (dotted), A == x ==> B (thick); or A -->|x| B.
ARROW = re.compile(r"\s*(?:--\s+([^|>]+?)\s+-->|-\.\s+([^|>]+?)\s+\.->|==\s+([^|>]+?)\s+==>"
                   r"|(-\.->|-->|==>|-\.-|---)\s*(?:\|([^|]*)\|)?)\s*")
ARROW_GROUPS = 5
NODE = re.compile(r"^([A-Za-z0-9_]+)\s*(.*)$", re.S)
SHAPES = [("([", "])"), ("[[", "]]"), ("{{", "}}"), ("((", "))"), ("{", "}"), ("(", ")"), ("[", "]")]
SKIP_LINE = re.compile(r"^\s*(%%|flowchart|graph|class |classDef|linkStyle|style |subgraph|end\s*$|click )")


# ------------------------------------------------------------------ pure helpers (unit tested)
def parse_heading_number(text: str) -> tuple[str, ...] | None:
    """'2.3.B. 配置' -> ('2', '3', 'B'); '4.1 玩法介紹' -> ('4', '1'); '目錄' -> None."""
    m = HEADING_NUM.match(text)
    if not m:
        return None
    parts = tuple(m.group(1).split("."))
    if m.group(2):
        parts += (m.group(2),)
    return parts


def _ordinal(token: str) -> int:
    return int(token) if token.isdigit() else ord(token) - ord("A") + 1


def _label(token: str, n: int) -> str:
    return str(n) if token.isdigit() else chr(ord("A") + n - 1)


def numbering_issues(numbers: list[tuple[str, ...]]) -> list[str]:
    """Gaps and duplicates per parent, in document order. Returns human-readable messages."""
    issues: list[str] = []
    seen: set[tuple[str, ...]] = set()
    last_child: dict[tuple[str, ...], int] = {}
    for num in numbers:
        key = ".".join(num)
        if num in seen:
            issues.append(f"重複編號 {key}")
            continue
        seen.add(num)
        parent, cur = num[:-1], _ordinal(num[-1])
        prev = last_child.get(parent, 0)
        if not parent and not prev:
            prev = cur - 1  # top level may start anywhere (a chapter excerpt); children start at 1
        if cur > prev + 1:
            missing = [".".join(parent + (_label(num[-1], n),)) for n in range(prev + 1, cur)]
            issues.append(f"跳號：{'、'.join(missing)} 不存在（{key} 之前）")
        elif cur <= prev:
            issues.append(f"順序倒退：{key} 出現在 {'.'.join(parent + (_label(num[-1], prev),))} 之後")
        last_child[parent] = max(prev, cur)
    return issues


def find_refs(text: str) -> list[tuple[str, ...]]:
    """'詳見 **3.9.** 與見 2.3.B.6' -> [('3','9'), ('2','3','B','6')]; skips '見本節 4.'."""
    return [tuple(m.group(1).split(".")) for m in REF.finditer(text)]


def _strip_shape(rest: str) -> tuple[str, str]:
    rest = rest.strip()
    for o, c in SHAPES:
        if rest.startswith(o) and rest.endswith(c):
            inner = rest[len(o):-len(c)].strip().strip('"')
            return ("decision" if o in ("{", "{{") else "node"), re.sub(r"<br\s*/?>", " ", inner)
    return "", ""


def parse_mermaid(src: str) -> dict[str, Any]:
    """Nodes {id: {"text", "kind"}} and edges [(src, label, dst, dotted)] from a flowchart."""
    nodes: dict[str, dict[str, str]] = {}
    edges: list[tuple[str, str, str, bool]] = []

    def node(seg: str) -> str | None:
        m = NODE.match(seg.strip())
        if not m:
            return None
        nid, rest = m.group(1), m.group(2)
        kind, text = _strip_shape(rest) if rest.strip() else ("", "")
        cur = nodes.setdefault(nid, {"text": nid, "kind": "node"})
        if kind:
            cur.update(text=text, kind=kind)
        return nid

    for line in src.splitlines():
        if not line.strip() or SKIP_LINE.match(line):
            continue
        parts = ARROW.split(line)
        # split yields: seg, (solid_label, dotted_label, thick_label, arrow, pipe_label), seg, ...
        step = ARROW_GROUPS + 1
        segs = parts[0::step]
        ids = [node(s) for s in segs]
        for i in range(len(segs) - 1):
            solid, dotted, thick, arrow, pipe = parts[step * i + 1: step * i + step]
            a, b = ids[i], ids[i + 1]
            if a and b:
                label = (pipe or solid or dotted or thick or "").strip()
                edges.append((a, label, b, bool(dotted) or bool(arrow and "." in arrow)))
    return {"nodes": nodes, "edges": edges}


def decision_report(chart: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    nodes, edges = chart["nodes"], chart["edges"]
    rows, warns = [], []
    for nid, n in nodes.items():
        if n["kind"] != "decision":
            continue
        exits = [(lbl, nodes[d]["text"], dotted) for s, lbl, d, dotted in edges if s == nid]
        rows.append({"id": nid, "text": n["text"], "exits": [{"label": l, "to": t, "dotted": d} for l, t, d in exits]})
        if len(exits) < 2:
            warns.append(f"判斷節點「{n['text']}」只有 {len(exits)} 個出口")
        for lbl, t, _ in exits:
            if not lbl:
                warns.append(f"判斷節點「{n['text']}」→「{t}」的出口沒有標籤")
    return rows, warns


# ------------------------------------------------------------------ Notion walk
@dataclass
class Section:
    number: tuple[str, ...]
    text: str
    block_id: str
    items: list[list[dict[str, Any]]] = field(default_factory=list)  # runs of numbered items (with children)


@dataclass
class Scope:
    name: str
    sections: list[Section] = field(default_factory=list)
    refs: list[tuple[tuple[str, ...], str]] = field(default_factory=list)  # (ref, context text)
    placeholders: list[tuple[str, str]] = field(default_factory=list)  # (section, text)
    charts: list[tuple[str, str]] = field(default_factory=list)  # (section, mermaid src)


def _text(block: dict[str, Any]) -> str:
    from notion_rest import plain

    t = block["type"]
    payload = block.get(t, {})
    if t == "table_row":
        return " | ".join(plain(c) for c in payload.get("cells", []))
    return plain(payload.get("rich_text"))


class Walker:
    def __init__(self, api: Any) -> None:
        self.api = api
        self.scopes: list[Scope] = []
        self.errors: list[str] = []

    def kids(self, block: dict[str, Any]) -> list[dict[str, Any]]:
        bid = block["id"]
        if block["type"] == "synced_block":
            src = (block["synced_block"] or {}).get("synced_from")
            if src:
                bid = src["block_id"]
        try:
            return self.api.children(bid)
        except RuntimeError as e:
            self.errors.append(f"讀不到 {bid}：{str(e)[:120]}")
            return []

    def run(self, page_id: str) -> list[Scope]:
        root = Scope("頁面")
        self.scopes.append(root)
        self.visit({"id": page_id, "type": "page"}, root, [None])
        return self.scopes

    def visit(self, block: dict[str, Any], scope: Scope, cur: list[Section | None], in_item: bool = False) -> None:
        """cur[0] = section currently open in this scope (shared across columns/toggles)."""
        children = self.api.children(block["id"]) if block["type"] == "page" else self.kids(block)
        run: list[dict[str, Any]] | None = None
        for b in children:
            t = b["type"]
            text = _text(b)
            label = ".".join(cur[0].number) if cur[0] else "頁首"
            for r in find_refs(text):
                scope.refs.append((r, f"{label}：{text[:40]}"))
            if PLACEHOLDER in text:
                scope.placeholders.append((label, text[:60]))
            if t.startswith("heading_"):
                num = parse_heading_number(text)
                if num:
                    cur[0] = Section(num, text.strip()[:40], b["id"])
                    scope.sections.append(cur[0])
                run = None
            elif t == "numbered_list_item" and not in_item:
                if run is None:
                    run = []
                    if cur[0]:
                        cur[0].items.append(run)
                run.append(b)
            elif not in_item:
                run = None
            if t == "code" and b["code"].get("language") == "mermaid":
                scope.charts.append((label, _text(b)))
            if t == "synced_block":
                inner = Scope(f"同步區塊＠{label}")
                self.scopes.append(inner)
                self.visit(b, inner, [None])
                continue
            if t == "table":
                for row in self.kids(b):
                    rt_ = _text(row)
                    for r in find_refs(rt_):
                        scope.refs.append((r, f"{label}（表格）：{rt_[:40]}"))
                    if PLACEHOLDER in rt_:
                        scope.placeholders.append((label + "（表格）", rt_[:60]))
                continue
            if b.get("has_children") and t != "child_page":
                self.visit(b, scope, cur, in_item=in_item or t in ("numbered_list_item", "bulleted_list_item"))


def resolve(ref: tuple[str, ...], scope: Scope, api: Any) -> bool:
    by_num = {s.number: s for s in scope.sections}
    for cut in range(len(ref), 0, -1):
        sec = by_num.get(ref[:cut])
        if sec is None:
            continue
        rest = ref[cut:]
        runs = sec.items
        for i, tok in enumerate(rest):
            if not tok.isdigit():
                return False
            k = int(tok)
            run = next((r for r in runs if len(r) >= k), None)
            if run is None:
                return False
            if i == len(rest) - 1:
                return True
            item = run[k - 1]
            kids = api.children(item["id"]) if item.get("has_children") else []
            runs, cur = [], None
            for c in kids:
                if c["type"] == "numbered_list_item":
                    if cur is None:
                        cur = []
                        runs.append(cur)
                    cur.append(c)
                else:
                    cur = None
        return True
    return False


# ------------------------------------------------------------------ CLI
def lint(url: str, lists: bool = False) -> dict[str, Any]:
    from notion_rest import Notion, dept_from_id, find_token, page_id_from

    pid = page_id_from(url)
    guess = dept_from_id(pid)
    api = None
    for dept in ([guess] if guess else ["一部", "四部"]):
        try:
            cand = Notion(find_token(dept=dept))
            cand.call("GET", f"/pages/{pid}")
            api = cand
            break
        except RuntimeError as e:
            if "-> 404" not in str(e):
                raise
    if api is None:
        raise SystemExit("404 with every dept credential: the page is not connected to the integration.")
    w = Walker(api)
    scopes = w.run(pid)
    out: dict[str, Any] = {"numbering": [], "refs": [], "placeholders": [], "charts": [], "lists": [], "errors": w.errors}
    for sc in scopes:
        for msg in numbering_issues([s.number for s in sc.sections]):
            out["numbering"].append(f"[{sc.name}] {msg}")
        for ref, ctx in sc.refs:
            if not resolve(ref, sc, api):
                out["refs"].append(f"[{sc.name}] 見 {'.'.join(ref)} 找不到 ← {ctx}")
        out["placeholders"] += [f"[{sc.name}] {sec}：{t}" for sec, t in sc.placeholders]
        for sec, src in sc.charts:
            rows, warns = decision_report(parse_mermaid(src))
            out["charts"].append({"scope": sc.name, "section": sec, "decisions": rows, "warnings": warns})
    if lists:
        out["lists"] = [f"第 {x['level'] + 1} 層設成 {x['have']}，第 {'、'.join(str(n + 1) for n in x['wrong'])} 層顯示不對"
                        f" → 清單格式改 Default「{x['text']}」"
                        for x in api.check_list_format(pid)]
    return out


def render(out: dict[str, Any]) -> str:
    lines = ["# plan_lint 報告", ""]

    def block(title: str, items: list[str], empty: str) -> None:
        lines.append(f"## {title}（{len(items)}）")
        lines.extend(f"- {x}" for x in items) if items else lines.append(f"- {empty}")
        lines.append("")

    block("標題編號", out["numbering"], "連續、無重複")
    block("章節引用", out["refs"], "全部找得到")
    block("後補", out["placeholders"], "無")
    lines.append(f"## 流程圖判斷節點（{len(out['charts'])} 張圖）")
    for c in out["charts"]:
        lines.append(f"### {c['scope']} {c['section']}")
        for d in c["decisions"]:
            exits = "；".join(f"{e['label'] or '（無標籤）'} → {e['to']}{'（虛線）' if e['dotted'] else ''}" for e in d["exits"])
            lines.append(f"- 「{d['text']}」：{exits}")
        lines.extend(f"- ⚠️ {w_}" for w_ in c["warnings"])
    lines.append("")
    if out["lists"]:
        block("清單顯示不是 1.→a.→i.（API 改不了，要在 Notion 把清單格式改 Default）", out["lists"], "")
    if out["errors"]:
        block("讀取錯誤", out["errors"], "")
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Read-only deterministic lint for a dept plan page.")
    ap.add_argument("url")
    ap.add_argument("--json", help="also write the raw result to this file")
    ap.add_argument("--lists", action="store_true", help="also check numbered lists are shown as Notion's default 1.->a.->i.")
    ap.add_argument("--no-lists", action="store_true", help=argparse.SUPPRESS)  # kept for old notes; default is off
    args = ap.parse_args()
    out = lint(args.url, lists=args.lists and not args.no_lists)
    if args.json:
        Path(args.json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(render(out))


if __name__ == "__main__":
    main()
