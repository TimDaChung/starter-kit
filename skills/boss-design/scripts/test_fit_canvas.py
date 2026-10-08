"""Tests for fit_canvas.py on a synthetic gray-background boss (no network, no quota).

Run: python -m pytest skills/boss-design/scripts/test_fit_canvas.py -q
"""
from __future__ import annotations

import random
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFilter

SCRIPT = Path(__file__).with_name("fit_canvas.py")
GRAY = (128, 128, 128)
BODY = (400, 160, 760, 520)  # red ellipse bbox on a 1200x800 source


def make_boss(path: Path) -> Path:
    """Gray canvas + noisy background + soft drop shadow + red body with a blue horn."""
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), GRAY)
    rnd = random.Random(7)
    px = img.load()
    for _ in range(20000):  # engine gray is never perfectly flat
        x, y = rnd.randrange(w), rnd.randrange(h)
        d = rnd.randint(-4, 4)
        px[x, y] = tuple(c + d for c in GRAY)
    shadow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shadow).ellipse((420, 500, 760, 560), fill=120)
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    img.paste(Image.new("RGB", (w, h), (40, 40, 40)), (0, 0), shadow)
    body = Image.new("L", (w, h), 0)
    ImageDraw.Draw(body).ellipse(BODY, fill=255)
    body = body.filter(ImageFilter.GaussianBlur(1.5))  # anti-aliased edge mixes with gray
    img.paste(Image.new("RGB", (w, h), (210, 40, 30)), (0, 0), body)
    ImageDraw.Draw(img).polygon([(560, 170), (600, 100), (620, 175)], fill=(40, 90, 220))
    img.save(path)
    return path


def run(*args: str) -> str:
    res = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=True)
    return res.stdout


@pytest.fixture()
def boss(tmp_path: Path) -> Path:
    return make_boss(tmp_path / "boss.png")


def test_transparent_corners_clear_and_body_kept(boss: Path, tmp_path: Path) -> None:
    out = tmp_path / "boss_alpha.png"
    run(str(boss), str(out), "--transparent")
    img = Image.open(out)
    assert img.mode == "RGBA"
    w, h = img.size
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        assert img.getpixel((x, y))[3] == 0, f"corner {(x, y)} not transparent"
    # cropped tight: horn top ~100, shadow bottom ~575, body sides 400..760
    assert 330 <= w <= 400 and 440 <= h <= 500, img.size
    # body center fully opaque and still red
    r, g, b, a = img.getpixel((w // 2, h // 2))
    assert a == 255 and r > 180 and g < 70 and b < 70
    # horn survives
    assert any(img.getpixel((x, 15))[2] > 150 and img.getpixel((x, 15))[3] > 200 for x in range(150, 230))


def test_transparent_edges_have_no_gray_halo(boss: Path, tmp_path: Path) -> None:
    out = tmp_path / "boss_alpha.png"
    run(str(boss), str(out), "--transparent")
    img = Image.open(out)
    w, h = img.size
    y = h // 2
    semi = [img.getpixel((x, y)) for x in range(0, w // 2) if 0 < img.getpixel((x, y))[3] < 255]
    assert semi, "expected a feathered edge"
    for r, g, b, a in semi:
        if a > 60:  # visible edge pixels must stay red, not drift to gray
            assert r - max(g, b) > 80, (r, g, b, a)


def test_transparent_margin_and_thresholds(boss: Path, tmp_path: Path) -> None:
    tight, padded = tmp_path / "t.png", tmp_path / "p.png"
    run(str(boss), str(tight), "--transparent")
    run(str(boss), str(padded), "--transparent", "--margin", "20", "--key-low", "12", "--key-high", "50", "--feather", "2")
    t, p = Image.open(tight), Image.open(padded)
    assert p.width >= t.width + 30 and p.height >= t.height + 30
    assert p.getpixel((0, 0))[3] == 0


def test_transparent_requires_png(boss: Path, tmp_path: Path) -> None:
    res = subprocess.run([sys.executable, str(SCRIPT), str(boss), str(tmp_path / "x.jpg"), "--transparent"],
                         capture_output=True, text=True)
    assert res.returncode != 0


def test_default_gray_canvas_unchanged(boss: Path, tmp_path: Path) -> None:
    out = tmp_path / "canvas.png"
    run(str(boss), str(out), "--height", "0.55")
    img = Image.open(out)
    assert img.mode == "RGB" and img.size == (1920, 1080)
    c = img.getpixel((5, 5))
    assert all(abs(c[i] - GRAY[i]) <= 4 for i in range(3))
