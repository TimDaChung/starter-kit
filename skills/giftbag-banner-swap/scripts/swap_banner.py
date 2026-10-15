"""Copy a giftbag banner.zip from the ad team's review folder into the two upload shares
under the plan's file name, then tell the PM to press sync.

Dry run by default: shows source, size, sha256 and both targets. Add --write to copy.

  python swap_banner.py <review folder or banner.zip> <YYMM_giftbag_theme.zip> [--write] [--force]

The source folder is never modified (the ad team owns it). Both targets get the same bytes;
after copying, all three sha256 values are compared and printed. Existing targets are never
overwritten unless --force (a same-named file usually means this month was already uploaded).
Targets come from paths.json next to this script; --hd / --hdr override them (tests).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

NAME_RE = re.compile(r"^(?P<yy>\d{2})(?P<mm>0[1-9]|1[0-2])_giftbag_(?P<theme>[A-Za-z0-9]+)\.zip$")
PATHS_FILE = Path(__file__).with_name("paths.json")


def load_paths() -> dict[str, str]:
    return json.loads(PATHS_FILE.read_text(encoding="utf-8"))


def check_name(name: str, today: dt.date | None = None) -> list[str]:
    """Problems with the target file name against the dept rule; empty list = OK."""
    m = NAME_RE.match(name)
    if not m:
        return [f"{name!r} is not YYMM_giftbag_<theme>.zip (YY = year, MM = month 01-12, theme = letters/digits only)"]
    today = today or dt.date.today()
    yy = 2000 + int(m.group("yy"))
    warn = []
    if not (today.year - 1 <= yy <= today.year + 1):
        warn.append(f"year {yy} is far from today ({today.year}); check YY")
    return warn


def find_zip(src: Path) -> Path:
    if src.is_file():
        return src
    if not src.is_dir():
        raise SystemExit(f"source not found: {src}")
    zips = sorted(src.glob("*.zip"))
    if (src / "banner.zip").is_file():
        return src / "banner.zip"
    if len(zips) == 1:
        return zips[0]
    raise SystemExit(f"expected banner.zip in {src}, found: {[z.name for z in zips] or 'no zip'}")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def plan(src: Path, name: str, targets: dict[str, Path]) -> dict:
    zip_path = find_zip(src)
    if not zipfile.is_zipfile(zip_path):
        raise SystemExit(f"{zip_path} is not a zip file")
    with zipfile.ZipFile(zip_path) as z:
        entries = z.namelist()
    return {"source": zip_path, "size": zip_path.stat().st_size, "entries": entries, "sha256": sha256(zip_path),
            "targets": {k: d / name for k, d in targets.items()}}


def copy_all(p: dict, force: bool) -> dict[str, str]:
    """Copy to every target; returns {label: sha256 of the copy}."""
    clashes = [t for t in p["targets"].values() if t.exists()]
    if clashes and not force:
        raise SystemExit("already exists (this month may be uploaded already; ask the PM, or --force): "
                         + ", ".join(str(t) for t in clashes))
    out = {}
    for label, t in p["targets"].items():
        if not t.parent.is_dir():
            raise SystemExit(f"upload folder not reachable: {t.parent}")
        shutil.copy2(p["source"], t)
        out[label] = sha256(t)
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Giftbag banner: review folder -> renamed copies in HD and HDR shares.")
    ap.add_argument("source", help="review folder (contains banner.zip) or the zip itself")
    ap.add_argument("name", help="target file name, YYMM_giftbag_<theme>.zip")
    ap.add_argument("--write", action="store_true", help="actually copy (default: preview)")
    ap.add_argument("--force", action="store_true", help="overwrite existing targets")
    ap.add_argument("--hd", help="override HD upload folder")
    ap.add_argument("--hdr", help="override HDR upload folder")
    a = ap.parse_args()

    problems = check_name(a.name)
    if problems and not NAME_RE.match(a.name):
        raise SystemExit(problems[0])
    for w in problems:
        print("warning:", w)
    cfg = load_paths()
    targets = {"HD": Path(a.hd or cfg["hd"]), "HDR": Path(a.hdr or cfg["hdr"])}
    p = plan(Path(a.source), a.name, targets)
    print(f"source : {p['source']}  ({p['size']:,} bytes, {len(p['entries'])} entries)  sha256 {p['sha256'][:16]}…")
    for label, t in p["targets"].items():
        print(f"{label:<6}: {t}{'  (EXISTS)' if t.exists() else ''}")
    if not a.write:
        print("dry run: add --write to copy")
        return
    copies = copy_all(p, a.force)
    ok = all(v == p["sha256"] for v in copies.values())
    print("copied; sha256 match on both targets:", "yes" if ok else "NO — re-copy")
    if not ok:
        raise SystemExit(1)
    print(f"next: open {cfg['sync_url']} and press sync (a person presses it; see SKILL.md step 4)")


if __name__ == "__main__":
    main()
