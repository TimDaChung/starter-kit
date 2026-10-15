"""Tests for swap_banner.py on scratch folders (no share access)."""
from __future__ import annotations

import datetime as dt
import zipfile
from pathlib import Path

import pytest

import swap_banner as sb


def make_zip(p: Path) -> Path:
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("banner.png", b"\x89PNG fake")
    return p


def test_check_name_rule() -> None:
    today = dt.date(2026, 10, 15)
    assert sb.check_name("2611_giftbag_bingo.zip", today) == []
    assert sb.check_name("2611_giftbag_bingo02.zip", today) == []
    for bad in ("banner.zip", "2613_giftbag_x.zip", "2611_giftbag_賓果.zip", "2611_giftbag_bingo.ZIP", "2611-giftbag-bingo.zip"):
        assert sb.check_name(bad, today), bad
    assert sb.check_name("1911_giftbag_old.zip", today) == ["year 2019 is far from today (2026); check YY"]


def test_find_zip_prefers_banner_zip(tmp_path: Path) -> None:
    review = tmp_path / "1024x576_GAF"
    review.mkdir()
    make_zip(review / "other.zip")
    assert sb.find_zip(review) == review / "other.zip"  # the only zip
    make_zip(review / "banner.zip")
    assert sb.find_zip(review) == review / "banner.zip"
    make_zip(review / "third.zip")
    assert sb.find_zip(review) == review / "banner.zip"
    (review / "banner.zip").unlink()
    with pytest.raises(SystemExit, match="expected banner.zip"):
        sb.find_zip(review)


def test_plan_and_copy_to_both_targets(tmp_path: Path) -> None:
    src = make_zip(tmp_path / "banner.zip")
    hd, hdr = tmp_path / "HD", tmp_path / "HDR"
    hd.mkdir(), hdr.mkdir()
    p = sb.plan(src, "2611_giftbag_bingo.zip", {"HD": hd, "HDR": hdr})
    assert p["entries"] == ["banner.png"]
    copies = sb.copy_all(p, force=False)
    assert set(copies) == {"HD", "HDR"} and all(v == p["sha256"] for v in copies.values())
    assert (hd / "2611_giftbag_bingo.zip").read_bytes() == src.read_bytes()
    assert src.exists()  # source untouched
    with pytest.raises(SystemExit, match="already exists"):
        sb.copy_all(p, force=False)
    sb.copy_all(p, force=True)


def test_rejects_non_zip_and_missing_folder(tmp_path: Path) -> None:
    bad = tmp_path / "banner.zip"
    bad.write_bytes(b"not a zip")
    with pytest.raises(SystemExit, match="not a zip"):
        sb.plan(bad, "2611_giftbag_x.zip", {"HD": tmp_path})
    src = make_zip(tmp_path / "ok.zip")
    p = sb.plan(src, "2611_giftbag_x.zip", {"HD": tmp_path / "missing"})
    with pytest.raises(SystemExit, match="not reachable"):
        sb.copy_all(p, force=False)


def test_paths_json_has_all_keys() -> None:
    assert set(sb.load_paths()) == {"hd", "hdr", "sync_url"}
