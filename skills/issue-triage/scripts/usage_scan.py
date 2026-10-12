"""Scan local Claude Code transcripts for friction while kit skills were in use (issue-triage mode D).

Read-only and local: nothing leaves the machine; the report is shown to the user, who decides
what to forward. Cheap by design - the model reads this summary, not the raw transcripts.

Signals per kit skill (a skill is "active" from its Skill call or /command for WINDOW user messages):
  - invocations
  - corrections: user messages that push back ("不對", "改回", "又漏"...)
  - tool errors: tool results flagged is_error

Usage: python usage_scan.py [--days 30] [--root ~/.claude/projects] [--kit ~/starter-kit] [--max 8]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

CORRECTION = re.compile(
    r"不對|不是這樣|錯了|改回|重來|重做|又(錯|漏|忘|沒)|漏了|你漏|沒有照|沒照|不要這樣|不用標|怎麼又|"
    r"為(什|甚)麼(沒|不|要|會)|說過|不是叫你|搞錯|弄錯|看錯|不行|失敗了|壞了|跑不動|卡住"
)
NOISE = ("<local-command", "<command-message", "<system-reminder", "<task-notification", "[Request interrupted",
         "This session is being continued")
ENV_ERRORS = ("denied by the Claude Code auto mode classifier", "The user doesn't want to proceed")
WINDOW = 5  # a skill stays "active" for this many user messages after its call
COMMAND = re.compile(r"<command-name>/([\w:-]+)</command-name>")
SECRET = re.compile(r"(ntn_|ghp_|sk-|xox[abp]-|AIza|Bearer\s)\S+")


@dataclass
class SkillStats:
    uses: int = 0
    corrections: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def kit_skills(kit: Path) -> set[str]:
    return {p.name for p in (kit / "skills").iterdir() if (p / "SKILL.md").is_file()}


def user_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


def clip(text: str, n: int = 120) -> str:
    text = SECRET.sub(r"\1***", " ".join(text.split()))
    return text[:n] + ("…" if len(text) > n else "")


def is_correction(text: str) -> bool:
    return bool(text) and not text.startswith(NOISE) and bool(CORRECTION.search(text))


def scan_file(path: Path, skills: set[str], stats: dict[str, SkillStats]) -> None:
    active: str | None = None
    turns = 0
    stamp = time.strftime("%m/%d", time.localtime(path.stat().st_mtime))
    tag = f"{stamp} {path.stem[:8]}"
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        msg = d.get("message") or {}
        if d.get("type") == "assistant":
            for c in msg.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "Skill":
                    name = str((c.get("input") or {}).get("skill", "")).split(":")[-1]
                    if name in skills:
                        active, turns = name, 0
                        stats[name].uses += 1
        elif d.get("type") == "user" and not d.get("isMeta"):
            content = msg.get("content")
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error") and active:
                        body = c.get("content")
                        body = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
                        if not any(e in body for e in ENV_ERRORS):
                            stats[active].errors.append(f"[{tag}] {clip(body, 150)}")
            text = user_text(msg)
            cmd = COMMAND.search(text)
            if cmd and cmd.group(1).split(":")[-1] in skills:
                active, turns = cmd.group(1).split(":")[-1], 0
                stats[active].uses += 1
                continue
            if not active or not text or text.startswith(NOISE):
                continue
            if is_correction(text):
                stats[active].corrections.append(f"[{tag}] {clip(text)}")
            turns += 1
            if turns >= WINDOW:
                active = None


def transcripts(root: Path, days: int) -> Iterator[Path]:
    cutoff = time.time() - days * 86400
    for p in root.glob("*/*.jsonl"):
        if p.stat().st_mtime >= cutoff:
            yield p


def render(stats: dict[str, SkillStats], days: int, files: int, cap: int) -> str:
    lines = [f"# kit 使用掃描（近 {days} 天，{files} 個 session）", "",
             "| skill | 使用次數 | 被糾正 | 工具錯誤 |", "|---|---|---|---|"]
    ranked = sorted(stats.items(), key=lambda kv: (-len(kv[1].corrections) - len(kv[1].errors), -kv[1].uses))
    for name, s in ranked:
        lines.append(f"| {name} | {s.uses} | {len(s.corrections)} | {len(s.errors)} |")
    for name, s in ranked:
        if not (s.corrections or s.errors):
            continue
        lines += ["", f"## {name}"]
        lines += [f"- 糾正 {x}" for x in s.corrections[:cap]]
        lines += [f"- 錯誤 {x}" for x in s.errors[:cap]]
        hidden = max(0, len(s.corrections) - cap) + max(0, len(s.errors) - cap)
        if hidden:
            lines.append(f"- （另有 {hidden} 筆未列）")
    if not stats:
        lines.append("| （期間內沒有使用 kit skill） | 0 | 0 | 0 |")
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    home = Path.home()
    ap = argparse.ArgumentParser(description="Scan transcripts for friction while kit skills were in use.")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--root", type=Path, default=home / ".claude" / "projects")
    ap.add_argument("--kit", type=Path, default=home / "starter-kit")
    ap.add_argument("--max", type=int, default=8, help="max snippets per skill and signal")
    args = ap.parse_args()
    skills = kit_skills(args.kit)
    stats: dict[str, SkillStats] = defaultdict(SkillStats)
    files = list(transcripts(args.root, args.days))
    for p in files:
        scan_file(p, skills, stats)
    print(render(dict(stats), args.days, len(files), args.max))


if __name__ == "__main__":
    main()
