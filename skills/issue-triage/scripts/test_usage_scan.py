"""Tests for usage_scan.py with a hand-made transcript; no real sessions read.

Run: python -m pytest skills/issue-triage/scripts/test_usage_scan.py
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import usage_scan as us  # noqa: E402


def _write(path: Path, rows: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    return path


def _skill(name: str) -> dict:
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": name}}]}}


def _user(text: str, **extra: object) -> dict:
    return {"type": "user", "message": {"content": text}, **extra}


def test_scan_attributes_corrections_and_errors(tmp_path: Path) -> None:
    rows = [
        _user("幫我改企劃，不對的地方先列"),  # no active skill yet -> ignored
        _skill("plan-dept14-writer"),
        _user("標題又漏了 4.3"),
        _user("<system-reminder>不對</system-reminder>"),  # noise
        _user("好，謝謝"),
        {"type": "user", "message": {"content": [{"type": "tool_result", "is_error": True, "content": "404 Bearer abc123"}]}},
        _user("<command-name>/plan-doc-qa</command-name>"),
        _user("為什麼沒抓到流程圖", isMeta=True),  # meta -> ignored
        _user("為什麼沒抓到流程圖"),
        _skill("not-a-kit-skill"),  # stays on plan-doc-qa
        _user("改回原本的"),
    ]
    p = _write(tmp_path / "abcdef1234.jsonl", rows)
    stats: dict[str, us.SkillStats] = defaultdict(us.SkillStats)
    us.scan_file(p, {"plan-dept14-writer", "plan-doc-qa"}, stats)
    w, q = stats["plan-dept14-writer"], stats["plan-doc-qa"]
    assert (w.uses, len(w.corrections), len(w.errors)) == (1, 1, 1)
    assert "標題又漏了" in w.corrections[0]
    assert "Bearer ***" in w.errors[0] and "abc123" not in w.errors[0]
    assert (q.uses, len(q.corrections)) == (1, 2)


def test_active_window_expires(tmp_path: Path) -> None:
    rows = [_skill("plan-doc-qa")] + [_user(f"第 {i} 句") for i in range(us.WINDOW)] + [_user("畫風不對")]
    stats: dict[str, us.SkillStats] = defaultdict(us.SkillStats)
    us.scan_file(_write(tmp_path / "s.jsonl", rows), {"plan-doc-qa"}, stats)
    assert stats["plan-doc-qa"].corrections == []


def test_render_ranks_by_friction() -> None:
    stats = {"a": us.SkillStats(uses=9), "b": us.SkillStats(uses=1, corrections=["[x] 不對"])}
    out = us.render(stats, 30, 2, 8)
    assert out.index("| b |") < out.index("| a |")
    assert "## b" in out and "## a" not in out
