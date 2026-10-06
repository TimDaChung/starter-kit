"""Local store for the department Notion API proxy credentials (pm1 / pm4).

Each member fetches a personal quarterly credential from the department setup page.
The setup prompt holds the proxy base URL, an `Auth` value (user/YYYY-MM-DD/secret),
the expiry date and the refresh page URL. This script keeps them in
~/.config/notion-pm/credentials.json and never prints the auth value.

    {"pm1": {"baseUrl", "auth", "expiresAt", "refreshUrl", "notified"}, "pm4": {...}}

The proxy base URL and the refresh page come from the setup prompt.

Usage:
    py -3 notion_credentials.py --show                 # dept, user, expiry, days left, source (no auth)
    py -3 notion_credentials.py --from-file <setup.txt> [--keep-source]
    py -3 notion_credentials.py --from-downloads       # per dept: newest ~/Downloads/notion-pmN-setup*.txt, then delete that dept's copies
    py -3 notion_credentials.py --from-clipboard       # fallback: the user pressed the page's copy button
    py -3 notion_credentials.py --refresh-url pm1      # print the pm1 setup page saved from its prompt
    py -3 notion_credentials.py --migrate              # copy setups found in ~/.claude CLAUDE.md / memory into the json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

DEPTS = ("pm1", "pm4")
TZ = dt.timezone(dt.timedelta(hours=8))
REMIND_DAYS = 4
DOWNLOAD_GLOB = "notion-pm*-setup*.txt"
# Fallback setup (install / refresh) pages for --refresh-url when no setup prompt has been
# installed yet. Left empty on purpose: fill in only after the owner confirms the URLs may
# live in this public repo.
DEFAULT_SETUP_PAGES: dict[str, str] = {
    "pm1": "https://sso.vgs.tw/notion-pm1.rw/",
    "pm4": "https://sso.vgs.tw/notion-pm4.rw/",
}

BASE_RE = re.compile(r"https?://notion-pm(\d)-[A-Za-z0-9.\-]+(?::\d+)?")
AUTH_RE = re.compile(r"(?<![A-Za-z0-9._@\-])([A-Za-z0-9._@\-]+/(\d{4}-\d{2}-\d{2})/[A-Za-z0-9_\-]{32,})")
EXPIRY_RE = re.compile(r"憑證到\s*(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}:\d{2}))?")
URL_RE = re.compile(r"https?://[^\s\"'`<>()（）「」，。、；]+")


def credentials_path() -> Path:
    """Resolved at call time so tests can point HOME/USERPROFILE elsewhere."""
    return Path.home() / ".config" / "notion-pm" / "credentials.json"


def claude_dir() -> Path:
    return Path.home() / ".claude"


# ---------------------------------------------------------------- parsing
def _expiry_iso(date: str, clock: str | None = None) -> str:
    return f"{date}T{clock or '23:59:59'}+08:00"


def _parse_near(text: str, base_match: re.Match[str], reach: int = 3000) -> dict[str, Any] | None:
    """Build one entry from the setup text around a base-URL match (nearest Auth wins)."""
    dept = f"pm{base_match.group(1)}"
    pos = base_match.start()
    auths = list(AUTH_RE.finditer(text))
    if not auths:
        return None
    auth_m = min(auths, key=lambda m: abs(m.start() - pos))
    if abs(auth_m.start() - pos) > reach:
        return None
    lo, hi = max(0, pos - reach), min(len(text), pos + reach)
    window = text[lo:hi]
    exp = EXPIRY_RE.search(window)
    expires_at = _expiry_iso(exp.group(1), exp.group(2)) if exp else _expiry_iso(auth_m.group(2))
    base_url = base_match.group(0).rstrip("/")
    refresh = ""
    for m in URL_RE.finditer(window):
        url = m.group(0).rstrip(".,;:")
        if url.startswith(base_url):
            continue
        if f"/notion-{dept}." in url or f"/notion-{dept}/" in url:
            refresh = url if url.endswith("/") else url + "/"
            break
    return {
        "baseUrl": base_url,
        "auth": auth_m.group(1),
        "expiresAt": expires_at,
        "refreshUrl": refresh,
        "notified": None,
    }


def parse_setup(text: str) -> tuple[str, dict[str, Any]]:
    """Extract (dept, entry) from a setup prompt. Raises ValueError if incomplete."""
    base = BASE_RE.search(text)
    if base is None:
        raise ValueError("no proxy base URL (https://notion-pmN-...) found in the setup prompt")
    entry = _parse_near(text, base, reach=len(text))
    if entry is None:
        raise ValueError("no Auth value (user/YYYY-MM-DD/secret) found in the setup prompt")
    return f"pm{base.group(1)}", entry


# ---------------------------------------------------------------- expiry helpers
def expires(entry: dict[str, Any]) -> dt.datetime:
    return dt.datetime.fromisoformat(entry["expiresAt"].replace("Z", "+00:00"))


def days_left(entry: dict[str, Any], now: dt.datetime | None = None) -> int:
    """Whole days until expiry (negative once expired)."""
    now = now or dt.datetime.now(TZ)
    return (expires(entry) - now).days


def is_expired(entry: dict[str, Any], now: dt.datetime | None = None) -> bool:
    return (now or dt.datetime.now(TZ)) > expires(entry)


def expiry_state(entry: dict[str, Any], now: dt.datetime | None = None) -> str | None:
    """None | 'expiring' (from REMIND_DAYS calendar days before the expiry date) | 'expired'."""
    now = now or dt.datetime.now(TZ)
    if now > expires(entry):
        return "expired"
    remind_from = expires(entry).astimezone(TZ).date() - dt.timedelta(days=REMIND_DAYS)
    if now.astimezone(TZ).date() >= remind_from:
        return "expiring"
    return None


def user_of(entry: dict[str, Any]) -> str:
    return entry["auth"].split("/", 1)[0]


def describe(dept: str, entry: dict[str, Any], source: str | None = None) -> str:
    """One-line summary that never includes the auth value."""
    src = f" source={source}" if source else ""
    return (f"{dept}: user={user_of(entry)} expiresAt={entry['expiresAt']} "
            f"({days_left(entry)} days left) auth=<hidden {len(entry['auth'])} chars>{src}")


# ---------------------------------------------------------------- storage
def load() -> dict[str, Any]:
    path = credentials_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save(data: dict[str, Any]) -> None:
    """Back up the existing file, then write the new one (0600 off Windows)."""
    path = credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, path.with_suffix(".json.bak"))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o600)


def scan_files() -> list[Path]:
    """Places a member's first install may have written the setup to."""
    files = [claude_dir() / "CLAUDE.md"]
    files += sorted((claude_dir() / "projects").glob("*/memory/*.md"))
    return [f for f in files if f.is_file()]


def _scan_entries() -> list[tuple[str, dict[str, Any], Path]]:
    found: list[tuple[str, dict[str, Any], Path]] = []
    for path in scan_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for base in BASE_RE.finditer(text):
            entry = _parse_near(text, base)
            if entry is not None:
                found.append((f"pm{base.group(1)}", entry, path))
    return found


def discover() -> dict[str, dict[str, Any]]:
    """json first; for depts missing there, the newest setup found in CLAUDE.md / memory.

    Entries found in files carry a `_source` key (file path) that is never saved.
    """
    result: dict[str, dict[str, Any]] = {d: dict(e) for d, e in load().items() if d in DEPTS}
    for dept, entry, path in _scan_entries():
        if dept in result and "_source" not in result[dept]:
            continue
        if dept not in result or expires(entry) > expires(result[dept]):
            result[dept] = {**entry, "_source": str(path)}
    return result


def get(dept: str) -> dict[str, Any] | None:
    """Credential for one dept (json, else discovered in CLAUDE.md / memory), or None."""
    return discover().get(dept)


def mark_notified(dept: str, state: str | None) -> None:
    """Persist the reminder state for a dept stored in the json (no-op otherwise)."""
    data = load()
    if dept in data and data[dept].get("notified") != state:
        data[dept]["notified"] = state
        save(data)


def reminder(dept: str, entry: dict[str, Any]) -> str | None:
    """Return a one-time reminder message when the expiry state changes; records it in the json."""
    state = expiry_state(entry)
    if state is None or entry.get("notified") == state:
        return None
    mark_notified(dept, state)
    entry["notified"] = state
    if state == "expiring":
        return (f"Notion credential for {dept} expires {entry['expiresAt']} ({days_left(entry)} days left); "
                f"refresh it after it expires (see plan-dept14-writer/references/notion-access.md)")
    return (f"Notion credential for {dept} expired at {entry['expiresAt']}; "
            f"refresh it (see plan-dept14-writer/references/notion-access.md)")


# ---------------------------------------------------------------- install
def _replace_in_sources(dept: str, old_entries: list[dict[str, Any]], new: dict[str, Any]) -> list[str]:
    """Swap old auth values (and their expiry/reminder dates next to them) for the new ones in place."""
    old_auths = {e["auth"] for e in old_entries if e.get("auth") and e["auth"] != new["auth"]}
    if not old_auths:
        return []
    new_date = new["expiresAt"][:10]
    new_remind = (expires(new).astimezone(TZ).date() - dt.timedelta(days=REMIND_DAYS)).isoformat()
    changed: list[str] = []
    for path in scan_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        hits = [a for a in old_auths if a in text]
        if not hits:
            continue
        for old_auth in hits:
            old_date = old_auth.split("/")[1]
            old_remind = (dt.date.fromisoformat(old_date) - dt.timedelta(days=REMIND_DAYS)).isoformat()
            positions = [m.start() for m in re.finditer(re.escape(old_auth), text)]
            lo = max(0, min(positions) - 1500)
            hi = min(len(text), max(positions) + len(old_auth) + 1500)
            region = text[lo:hi].replace(old_auth, new["auth"])
            if old_date != new_date:
                region = region.replace(old_date, new_date).replace(old_remind, new_remind)
            text = text[:lo] + region + text[hi:]
        path.write_text(text, encoding="utf-8")
        changed.append(str(path))
    return changed


def install(text: str) -> tuple[str, dict[str, Any], list[str]]:
    """Parse, validate and store a setup prompt. Returns (dept, entry, files rewritten in place)."""
    dept, entry = parse_setup(text)
    if is_expired(entry):
        raise ValueError(f"refusing to install an expired credential: {describe(dept, entry)}")
    data = load()
    old = [e for d, e, _ in _scan_entries() if d == dept]
    if dept in data:
        old.append(data[dept])
    data[dept] = entry
    save(data)
    return dept, entry, _replace_in_sources(dept, old, entry)


def migrate() -> int:
    data = load()
    moved = 0
    for dept, entry in discover().items():
        source = entry.pop("_source", None)
        if source is None:
            continue
        if is_expired(entry):
            print(f"skip expired {describe(dept, entry, source)}")
            continue
        data[dept] = entry
        moved += 1
        print(f"migrated {describe(dept, entry, source)}")
    if moved:
        save(data)
    else:
        print("nothing to migrate")
    return 0


def show() -> int:
    found = discover()
    if not found:
        print(f"no Notion credential (looked in {credentials_path()} and ~/.claude CLAUDE.md / memory)")
        return 1
    for dept in DEPTS:
        if dept in found:
            entry = found[dept]
            print(describe(dept, entry, entry.get("_source") or str(credentials_path())))
        else:
            print(f"{dept}: missing")
    return 0


def refresh_url(dept: str) -> int:
    """Setup page for a dept: the URL saved from its setup prompt, else the default page (if configured)."""
    url = (get(dept) or {}).get("refreshUrl") or DEFAULT_SETUP_PAGES.get(dept)
    if not url:
        print(f"no setup page known for {dept}; ask the user for the {dept} install page", file=sys.stderr)
        return 1
    print(url)
    return 0


def downloads_by_dept() -> dict[str, list[Path]]:
    """~/Downloads/notion-pmN-setup*.txt grouped by dept, newest first (handles 'name (1).txt')."""
    grouped: dict[str, list[Path]] = {}
    for path in (Path.home() / "Downloads").glob(DOWNLOAD_GLOB):
        m = re.match(r"notion-(pm\d)-setup", path.name)
        if m is None or m.group(1) not in DEPTS:
            print(f"skip {path.name}: the file name must carry the dept (notion-pm1-setup.txt / notion-pm4-setup.txt)",
                  file=sys.stderr)
            continue
        grouped.setdefault(m.group(1), []).append(path)
    for files in grouped.values():
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return grouped


def install_file(source: Path, keep_source: bool, expect_dept: str | None = None) -> int:
    """Install one setup file; prints a summary without the auth value."""
    try:
        text = source.read_text(encoding="utf-8")
        found_dept = parse_setup(text)[0]
        if expect_dept is not None and found_dept != expect_dept:
            raise ValueError(f"{source.name} holds a {found_dept} setup, not {expect_dept}; not installed")
        dept, entry, rewritten = install(text)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    if not keep_source:
        source.unlink()
    print(f"installed {dept} -> {credentials_path()}")
    print(describe(dept, entry))
    for path in rewritten:
        print(f"replaced the old {dept} auth/expiry in place: {path}")
    return 0


def install_downloads(keep_source: bool) -> int:
    """Install the newest download of each dept; only that dept's older copies are deleted."""
    grouped = downloads_by_dept()
    if not grouped:
        print(f"no notion-pm1-setup*.txt / notion-pm4-setup*.txt in {Path.home() / 'Downloads'}", file=sys.stderr)
        return 1
    status = 0
    for dept in sorted(grouped):
        newest, *older = grouped[dept]
        result = install_file(newest, keep_source, expect_dept=dept)
        status |= result
        if result == 0 and not keep_source:
            # older browser copies of this dept hold auth values too; other depts' files are left alone
            for leftover in older:
                leftover.unlink(missing_ok=True)
    return status


def _clipboard_commands() -> tuple[list[list[str]], list[list[str]]]:
    """(read commands, clear commands) to try in order for this platform."""
    if os.name == "nt":
        ps = ["powershell", "-NoProfile", "-NonInteractive", "-Command"]
        return ([ps + ["[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"]],
                [["clip"], ps + ["Set-Clipboard -Value ' '"]])
    if sys.platform == "darwin":
        return [["pbpaste"]], [["pbcopy"]]
    return ([["xclip", "-selection", "clipboard", "-o"], ["xsel", "--clipboard", "--output"]],
            [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]])


def read_clipboard() -> str:
    """Clipboard text (pyperclip if installed, else the platform command). Never printed."""
    try:
        import pyperclip  # noqa: PLC0415

        return str(pyperclip.paste() or "")
    except ImportError:
        pass
    for cmd in _clipboard_commands()[0]:
        try:
            done = subprocess.run(cmd, capture_output=True, timeout=15, check=True)
        except (OSError, subprocess.SubprocessError):
            continue
        return done.stdout.decode("utf-8", errors="replace")
    raise RuntimeError("cannot read the clipboard on this machine")


def clear_clipboard() -> None:
    """Overwrite the clipboard so the setup prompt does not linger there."""
    try:
        import pyperclip  # noqa: PLC0415

        pyperclip.copy("")
        return
    except ImportError:
        pass
    for cmd in _clipboard_commands()[1]:
        try:
            subprocess.run(cmd, input=b"", capture_output=True, timeout=15, check=True)
            return
        except (OSError, subprocess.SubprocessError):
            continue


def install_clipboard() -> int:
    """Install a setup prompt the user copied with the page's copy button; then wipe the clipboard."""
    try:
        text = read_clipboard()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1
    try:
        dept, entry, rewritten = install(text)
    except ValueError as error:
        # do not echo the clipboard: it may hold anything
        print(f"clipboard does not hold a valid setup prompt ({len(text)} chars): {error}", file=sys.stderr)
        return 1
    clear_clipboard()
    print(f"installed {dept} -> {credentials_path()} (clipboard cleared)")
    print(describe(dept, entry))
    for path in rewritten:
        print(f"replaced the old {dept} auth/expiry in place: {path}")
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--from-file", type=Path)
    parser.add_argument("--keep-source", action="store_true",
                        help="keep the source file (it contains the auth value; deleted by default)")
    parser.add_argument("--from-downloads", action="store_true",
                        help="install the newest ~/Downloads/notion-pmN-setup*.txt of each dept")
    parser.add_argument("--from-clipboard", action="store_true",
                        help="install the setup prompt the user copied from the page, then clear the clipboard")
    parser.add_argument("--refresh-url", choices=DEPTS)
    parser.add_argument("--migrate", action="store_true")
    args = parser.parse_args()

    if args.from_clipboard:
        return install_clipboard()
    if args.refresh_url:
        return refresh_url(args.refresh_url)
    if args.migrate:
        return migrate()
    if args.from_downloads:
        return install_downloads(args.keep_source)
    if args.from_file is not None:
        if not args.from_file.exists():
            print(f"source not found: {args.from_file}", file=sys.stderr)
            return 1
        return install_file(args.from_file, args.keep_source)
    return show()


if __name__ == "__main__":
    raise SystemExit(main())
