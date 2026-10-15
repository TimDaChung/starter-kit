"""Tests for compose's label wrapping and layout (no browser needed)."""
import json
import pathlib
import sys
from argparse import Namespace

import pytest
from PIL import Image, ImageChops, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import capture_storyboard as cs  # noqa: E402

LONG = "圖6  全通關！獎圖消失、切換慶祝背景畫面，剩餘次數欄炸開噴金幣"


@pytest.fixture(scope="module")
def font() -> ImageFont.FreeTypeFont:
    try:
        return cs.load_font(22)
    except SystemExit:
        pytest.skip("no CJK font on this machine")


def test_long_caption_wraps_within_width(font: ImageFont.FreeTypeFont) -> None:
    width = 300
    lines = cs.wrap_text(LONG, font, width)
    assert len(lines) > 1
    assert "".join(lines).replace(" ", "") == LONG.replace(" ", "")
    for line in lines:
        # a hanging closing mark may poke out by one glyph, nothing more
        limit = width + (font.getlength(line[-1]) if line[-1] in cs.NO_LINE_START else 0)
        assert font.getlength(line) <= limit


@pytest.mark.parametrize("width", range(120, 420, 7))
def test_no_line_starts_with_closing_punctuation(font: ImageFont.FreeTypeFont, width: int) -> None:
    for text in (LONG, "罐子爆開，噴出金幣。」標題壓下（彈跳）！", "閃電擊中右側 2 罐，罐子爆開噴金幣"):
        lines = cs.wrap_text(text, font, width)
        for line in lines[1:]:
            assert line[0] not in cs.NO_LINE_START, (width, lines)
        for line in lines[:-1]:
            assert line[-1] not in cs.NO_LINE_END, (width, lines)


def test_short_caption_stays_one_line(font: ImageFont.FreeTypeFont) -> None:
    assert cs.wrap_text("圖1  舉杖", font, 600) == ["圖1  舉杖"]


def test_ascii_word_not_split(font: ImageFont.FreeTypeFont) -> None:
    lines = cs.wrap_text("倍數跳到 x1000 後定格", font, font.getlength("倍數跳到 x10"))
    assert any("x1000" in line for line in lines)


def _frames(n: int) -> list[Image.Image]:
    colors = [(200, 40, 40), (40, 200, 40), (40, 40, 200), (200, 200, 40), (40, 200, 200)]
    return [Image.new("RGB", (320, 180), colors[k % len(colors)]) for k in range(n)]


def test_label_band_above_frame_leaves_frame_untouched(font: ImageFont.FreeTypeFont) -> None:
    frames = _frames(5)
    labels = [LONG, "圖2  舉杖", "圖3  短", "圖4  " + LONG[4:], "圖5  結算"]
    sheet, boxes = cs.layout_sheet(frames, labels, cols=3, cell_w=320, font=font)
    assert sheet.height == boxes[-1][3] + round(320 * 0.02)
    for frame, box in zip(frames, boxes):
        region = sheet.crop(box)
        assert ImageChops.difference(region, frame).getbbox() is None  # frame pixels untouched
        x0, y0 = box[0], box[1]
        assert sheet.getpixel((x0, y0 - 1)) == cs.LABEL_BG  # label band sits directly above
    # frames in the same row align; the long label makes row 1's band taller than one line
    assert boxes[0][1] == boxes[1][1] == boxes[2][1]
    assert boxes[3][1] == boxes[4][1]
    first_band = boxes[0][1] - round(320 * 0.02)
    assert first_band > font.size * 2


def test_compose_writes_sheet(tmp_path: pathlib.Path, font: ImageFont.FreeTypeFont) -> None:
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    shots = []
    for k, img in enumerate(_frames(3), 1):
        img.save(frames_dir / f"a_{k:02d}.png")
        shots.append({"n": k, "phase": 0, "offset_ms": 0, "caption": LONG[4:] if k == 1 else "噴金幣", "file": f"a_{k:02d}.png"})
    data = {"a": {"name": "測試", "mode": "beats", "phases": [{"name": "分鏡1 測試", "ms": 1500}], "shots": shots}}
    (tmp_path / "candidates.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    cs.cmd_compose(Namespace(out_dir=str(tmp_path), scenario="a", pick="", captions="", min_diff=3.0, cell_width=320))
    sheet = Image.open(tmp_path / "分鏡_測試.png")
    assert sheet.getpixel((round(320 * 0.02), round(320 * 0.02))) == cs.LABEL_BG  # label band is the top-left
    assert (tmp_path / "分鏡_測試_企劃草稿.md").exists()
