"""Deprecated shim: the kit's single plan fetcher is art-request-sheet/scripts/fetch_plan.py.

Kept so older notes that call this path keep working. Same CLI:
    python fetch_plan.py <page_id or url> <out_dir>
    python fetch_plan.py --list pets|bosses|cannons|wings|weapons

Differences from the old copy here: plan.md keeps red / gray-green background /
strikethrough marks and a title line, videos and files are downloaded too, and
media are named NN_<caption>.<ext> instead of img_NN.png.
"""
import importlib.util
import sys
from pathlib import Path

CANONICAL = Path(__file__).resolve().parents[2] / "art-request-sheet" / "scripts" / "fetch_plan.py"


def _load_canonical():
    """Import the canonical script under its own module name (this file shares the basename)."""
    spec = importlib.util.spec_from_file_location("art_request_sheet_fetch_plan", CANONICAL)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_canonical = _load_canonical()
LISTS = _canonical.LISTS
list_rows = _canonical.list_rows
_main = _canonical.main

DEPRECATION = f"[fetch_plan] pet-evolution/scripts/fetch_plan.py is a shim; call {CANONICAL} directly."


def main() -> None:
    print(DEPRECATION, file=sys.stderr)
    _main()


if __name__ == "__main__":
    main()
