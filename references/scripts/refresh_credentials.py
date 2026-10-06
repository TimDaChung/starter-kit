"""Install a new Image Studio credential from a saved quarterly setup prompt.

The quarterly setup prompt contains a ```json fenced block holding
baseUrl / token / expiresAt. This script extracts
that block and writes it to ~/.config/image-studio/credentials.json without ever
printing the token.

Usage:
    py -3 refresh_credentials.py --from-file <setup-prompt.txt> [--keep-source]
    py -3 refresh_credentials.py --show          # report current expiry only
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

CREDENTIALS_PATH = Path.home() / ".config" / "image-studio" / "credentials.json"
REQUIRED_KEYS = ("baseUrl", "token", "expiresAt")
JSON_BLOCK = re.compile(r"\{[^{}]*\"token\"[^{}]*\}", re.DOTALL)


def extract_credentials(text: str) -> dict[str, Any]:
    """Pull the credentials object out of a setup prompt."""
    for match in JSON_BLOCK.finditer(text):
        try:
            candidate = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        if all(key in candidate for key in REQUIRED_KEYS):
            return candidate
    raise ValueError(
        "no credentials JSON found - the file must contain the full setup prompt "
        f"with a JSON object holding {', '.join(REQUIRED_KEYS)}"
    )


def days_left(expires_at: str) -> int:
    """Whole days from now until the credential expires (negative if expired)."""
    expiry = dt.datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    return (expiry - dt.datetime.now(dt.timezone.utc)).days


def describe(credentials: dict[str, Any]) -> str:
    """One-line summary that never includes the token."""
    expires_at = credentials["expiresAt"]
    return (
        f"baseUrl={credentials['baseUrl']} expiresAt={expires_at} "
        f"({days_left(expires_at)} days left) token=<hidden {len(credentials['token'])} chars>"
    )


def write_credentials(credentials: dict[str, Any]) -> None:
    """Back up the existing credential file, then write the new one at 0600."""
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CREDENTIALS_PATH.exists():
        shutil.copy2(CREDENTIALS_PATH, CREDENTIALS_PATH.with_suffix(".json.bak"))
    CREDENTIALS_PATH.write_text(
        json.dumps(credentials, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if os.name != "nt":
        CREDENTIALS_PATH.chmod(0o600)


def show_current() -> int:
    if not CREDENTIALS_PATH.exists():
        print(f"no credential at {CREDENTIALS_PATH}")
        return 1
    current = json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))
    print(describe(current))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-file", type=Path, help="file holding the setup prompt")
    parser.add_argument(
        "--keep-source",
        action="store_true",
        help="keep the source file (it contains the token; deleted by default)",
    )
    parser.add_argument(
        "--show", action="store_true", help="report the installed credential's expiry"
    )
    args = parser.parse_args()

    if args.show or args.from_file is None:
        return show_current()

    source: Path = args.from_file
    if not source.exists():
        print(f"source not found: {source}", file=sys.stderr)
        return 1

    try:
        credentials = extract_credentials(source.read_text(encoding="utf-8"))
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1

    if days_left(credentials["expiresAt"]) < 0:
        print(f"refusing to install an expired credential: {describe(credentials)}", file=sys.stderr)
        return 1

    write_credentials(credentials)
    if not args.keep_source:
        source.unlink()
    print(f"installed {CREDENTIALS_PATH}")
    print(describe(credentials))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
