"""Find and remove legacy long-lived Notion integration tokens (ntn_ / secret_).

Since 2026-10-06 the department Notion API proxy (notion_credentials.py) is the only
supported way to read / write plan pages; the old long-lived integration tokens were
revoked. Copies of them left on a machine only cause 401s or tempt the AI to use a
dead path, so this script cleans them up. It never prints a token value.

What it looks at:
    ~/.claude.json            mcpServers (user scope) and projects[*].mcpServers (local scope)
                              -> servers whose env / headers / args carry a legacy token: removed
    ~/.claude/backups/.claude.json.backup*
                              -> the same servers stripped from Claude Code's rotating backups
    ~/.claude/settings*.json  env entries carrying a legacy token: removed
    Windows user env vars     (HKCU\\Environment) carrying a legacy token: removed
    ~/.claude/CLAUDE.md, ~/.claude/projects/*/memory/*.md
                              -> lines with a legacy token: reported only (edit by hand / ask the AI)

Notion MCP servers that do not carry a legacy token (e.g. OAuth to mcp.notion.com) are
reported but left alone.

Usage:
    py -3 notion_legacy_cleanup.py            # dry run: list findings, change nothing
    py -3 notion_legacy_cleanup.py --apply    # remove what is listed as removable
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HOME = Path.home()
CLAUDE_JSON = HOME / ".claude.json"
CLAUDE_DIR = HOME / ".claude"
SETTINGS_FILES = (CLAUDE_DIR / "settings.json", CLAUDE_DIR / "settings.local.json")
TOKEN_RE = re.compile(r"\b(?:ntn_[A-Za-z0-9]{20,}|secret_[A-Za-z0-9]{30,})")
NOTION_HINT_RE = re.compile(r"notion", re.IGNORECASE)


@dataclass
class Finding:
    where: str
    detail: str
    removable: bool
    done: bool = False


def has_token(value: Any) -> bool:
    return bool(TOKEN_RE.search(json.dumps(value, ensure_ascii=False)))


def mask(text: str) -> str:
    return TOKEN_RE.sub(lambda m: m.group(0).split("_", 1)[0] + "_****", text)


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def write_json(path: Path, data: dict[str, Any]) -> None:
    # Atomic replace, no .bak: a backup would keep the very token we are removing.
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def remove_via_cli(name: str, scope: str, cwd: str | None) -> bool:
    exe = shutil.which("claude")
    if not exe:
        return False
    try:
        proc = subprocess.run(
            [exe, "mcp", "remove", name, "-s", scope],
            cwd=cwd, capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def scan_mcp(apply: bool) -> list[Finding]:
    data = load_json(CLAUDE_JSON)
    if data is None:
        return []
    found: list[Finding] = []
    # (scope, project path or None, servers dict)
    groups: list[tuple[str, str | None, dict[str, Any]]] = [("user", None, data.get("mcpServers") or {})]
    for proj, cfg in (data.get("projects") or {}).items():
        if isinstance(cfg, dict) and cfg.get("mcpServers"):
            groups.append(("local", proj, cfg["mcpServers"]))

    fallback: list[tuple[str | None, str]] = []
    for scope, proj, servers in groups:
        for name, cfg in servers.items():
            where = f"~/.claude.json mcpServers.{name}" + (f" (project {proj})" if proj else " (user)")
            if has_token(cfg):
                f = Finding(where, "MCP server carries a legacy Notion token", removable=True)
                if apply:
                    cwd = proj if proj and Path(proj).is_dir() else None
                    if (scope == "user" or cwd) and remove_via_cli(name, scope, cwd):
                        f.done = True
                    else:
                        fallback.append((proj, name))
                found.append(f)
            elif NOTION_HINT_RE.search(name) or NOTION_HINT_RE.search(json.dumps(cfg)):
                found.append(Finding(where, "Notion MCP without a legacy token; left alone", removable=False))

    if fallback:
        # The CLI was unavailable or failed: edit the file directly (re-read to keep any CLI edits).
        data = load_json(CLAUDE_JSON) or {}
        for proj, name in fallback:
            servers = data.get("mcpServers") if proj is None else (data.get("projects") or {}).get(proj, {}).get("mcpServers")
            if servers and name in servers:
                del servers[name]
        write_json(CLAUDE_JSON, data)
        for f in found:
            if f.removable and not f.done:
                f.done = True
    return found


def strip_token_servers(data: dict[str, Any]) -> int:
    removed = 0
    groups = [data.get("mcpServers") or {}]
    groups += [cfg.get("mcpServers") or {} for cfg in (data.get("projects") or {}).values() if isinstance(cfg, dict)]
    for servers in groups:
        for name in [n for n, cfg in servers.items() if has_token(cfg)]:
            del servers[name]
            removed += 1
    return removed


def scan_backups(apply: bool) -> list[Finding]:
    # Claude Code keeps rotating copies of ~/.claude.json; an old token sits in all of them.
    found: list[Finding] = []
    for path in sorted((CLAUDE_DIR / "backups").glob(".claude.json.backup*")):
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        n = strip_token_servers(data)
        if n:
            if apply:
                write_json(path, data)
            found.append(Finding(f"backups/{path.name}", f"{n} MCP server(s) with a legacy Notion token", removable=True, done=apply))
    return found


def scan_settings(apply: bool) -> list[Finding]:
    found: list[Finding] = []
    for path in SETTINGS_FILES:
        data = load_json(path)
        env = (data or {}).get("env") or {}
        bad = [k for k, v in env.items() if has_token(v)]
        if not bad:
            continue
        for k in bad:
            found.append(Finding(f"{path.name} env.{k}", "legacy Notion token in settings env", removable=True, done=apply))
        if apply and data is not None:
            for k in bad:
                del env[k]
            write_json(path, data)
    return found


def scan_user_env(apply: bool) -> list[Finding]:
    if sys.platform != "win32":
        return []
    try:
        out = subprocess.run(["reg", "query", r"HKCU\Environment"], capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    found: list[Finding] = []
    for line in out.splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3 and parts[1].startswith("REG_") and TOKEN_RE.search(parts[2]):
            f = Finding(f"user env var {parts[0]}", "legacy Notion token in Windows user environment", removable=True)
            if apply:
                r = subprocess.run(["reg", "delete", r"HKCU\Environment", "/v", parts[0], "/f"], capture_output=True, text=True)
                f.done = r.returncode == 0
            found.append(f)
    return found


def scan_text_files() -> list[Finding]:
    paths = [CLAUDE_DIR / "CLAUDE.md", *sorted((CLAUDE_DIR / "projects").glob("*/memory/*.md"))]
    found: list[Finding] = []
    for path in paths:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines, 1):
            if TOKEN_RE.search(line):
                found.append(Finding(f"{path}:{i}", "legacy token in text: " + mask(line.strip())[:80], removable=False))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="remove removable findings (default: dry run)")
    args = ap.parse_args()

    findings = scan_mcp(args.apply) + scan_backups(args.apply) + scan_settings(args.apply) + scan_user_env(args.apply) + scan_text_files()
    if not findings:
        print("clean: no legacy Notion token found")
        return 0
    for f in findings:
        if not f.removable:
            status = "REPORT"
        elif not args.apply:
            status = "WOULD REMOVE"
        else:
            status = "REMOVED" if f.done else "FAILED"
        print(f"[{status}] {f.where} - {f.detail}")
    if any(f.removable for f in findings):
        print("\nrestart Claude Code for MCP / env changes to take effect" if args.apply else "\nrun with --apply to remove")
    if any(not f.removable and "text" in f.detail for f in findings):
        print("text-file hits: delete those lines by hand (the tokens are revoked; nothing to migrate)")
    return 1 if any(f.removable and args.apply and not f.done for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
