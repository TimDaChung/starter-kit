"""Shim: the shared Notion REST helpers live in plan-dept14-writer/scripts/notion_rest.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plan-dept14-writer" / "scripts"))
from notion_rest import *  # noqa: E402,F401,F403
from notion_rest import find_token, plain, rt  # noqa: E402,F401
