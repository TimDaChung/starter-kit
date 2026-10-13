"""The pet-evolution fetch_plan.py is a shim over art-request-sheet/scripts/fetch_plan.py.

No network: main() is patched, list kinds are checked against the canonical table.
Run: python -m pytest skills/pet-evolution/scripts -q
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
CANONICAL = HERE.parents[1] / "art-request-sheet" / "scripts" / "fetch_plan.py"


@pytest.fixture(scope="module")
def shim():
    spec = importlib.util.spec_from_file_location("pet_fetch_plan_shim", HERE / "fetch_plan.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_shim_points_at_canonical_script(shim) -> None:
    assert CANONICAL.is_file()
    assert Path(shim.CANONICAL) == CANONICAL
    assert shim._main.__module__ == "art_request_sheet_fetch_plan"


def test_list_kinds_cover_every_design_line(shim) -> None:
    assert set(shim.LISTS) >= {"pets", "bosses", "cannons", "wings", "weapons"}


def test_main_prints_deprecation_then_forwards(shim, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    calls: list[str] = []
    monkeypatch.setattr(shim, "_main", lambda: calls.append("forwarded"))
    monkeypatch.setattr(sys, "argv", ["fetch_plan.py", "--list", "pets"])
    shim.main()
    assert calls == ["forwarded"]
    assert "shim" in capsys.readouterr().err
