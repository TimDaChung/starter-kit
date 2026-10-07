"""Tests for prep_images.py (GIF limits, per-column thumbnail boxes) and fetch_plan.py table cells.

The test video is generated on the spot with the ffmpeg bundled in imageio-ffmpeg;
no video file is kept in the repo.

Run: python -m pytest skills/art-request-sheet/scripts/test_prep_and_fetch.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

imageio_ffmpeg = pytest.importorskip('imageio_ffmpeg')
Image = pytest.importorskip('PIL.Image')

import prep_images  # noqa: E402


@pytest.fixture(scope='module')
def video(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A 14 s 640x360 30 fps test pattern, longer than the 10 s default cut."""
    out = tmp_path_factory.mktemp('vid') / '07_test.mp4'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'lavfi',
                    '-i', 'testsrc=duration=14:size=640x360:rate=30', '-pix_fmt', 'yuv420p', str(out)],
                   check=True)
    return out


def gif_info(path: Path) -> tuple[tuple[int, int], int, float]:
    """(size, frame count, total seconds) of a GIF."""
    with Image.open(path) as im:
        frames, total_ms = 0, 0
        for i in range(im.n_frames):
            im.seek(i)
            frames += 1
            total_ms += im.info.get('duration', 0)
        return im.size, frames, total_ms / 1000


def test_mp4_to_gif_keeps_first_10s_at_6fps_360px(video: Path, tmp_path: Path,
                                                  capsys: pytest.CaptureFixture[str]) -> None:
    dst = tmp_path / 'out.gif'
    size = prep_images.mp4_to_gif(str(video), str(dst))
    (w, h), frames, secs = gif_info(dst)
    assert (w, h) == (360, 202)
    assert 58 <= frames <= 61            # 10 s * 6 fps
    assert 9.5 <= secs <= 10.5
    assert size == dst.stat().st_size < 9 * 1024 * 1024
    out = capsys.readouterr().out
    assert 'first 10.0s of 14.0s' in out and 'warning' not in out


def test_mp4_to_gif_options_and_size_warning(video: Path, tmp_path: Path,
                                             capsys: pytest.CaptureFixture[str]) -> None:
    dst = tmp_path / 'out.gif'
    prep_images.mp4_to_gif(str(video), str(dst), seconds=3, fps=4, width=200, warn_mb=0.000001)
    (w, _), frames, secs = gif_info(dst)
    assert w == 200 and 11 <= frames <= 13 and 2.5 <= secs <= 3.5
    assert 'warning: out.gif is' in capsys.readouterr().out


def test_mp4_to_gif_seconds_zero_keeps_whole_video(video: Path, tmp_path: Path) -> None:
    dst = tmp_path / 'out.gif'
    prep_images.mp4_to_gif(str(video), str(dst), seconds=0, fps=2, width=120)
    assert 13.5 <= gif_info(dst)[2] <= 14.5


def test_shrink_uses_given_box(tmp_path: Path) -> None:
    src = tmp_path / 'big.png'
    Image.new('RGB', (1920, 1080), 'red').save(src)
    assert prep_images.shrink(str(src), str(tmp_path / 'a.png'), (530, 300)) == (530, 298)
    assert Image.open(tmp_path / 'a.png').size == (530, 298)
    assert prep_images.shrink(str(src), str(tmp_path / 'b.png'), (180, 300)) == (180, 101)


def run_prep(src: Path, out: Path, *extra: str) -> str:
    proc = subprocess.run([sys.executable, str(SCRIPTS / 'prep_images.py'), str(src), str(out), *extra],
                          capture_output=True, text=True, encoding='utf-8', check=True)
    return proc.stdout


def test_prep_cli_dept1_default_is_530x300(tmp_path: Path) -> None:
    src = tmp_path / 'src'
    src.mkdir()
    Image.new('RGB', (2496, 1404)).save(src / '05_主介面.png')
    Image.new('RGB', (100, 100)).save(src / '06_後補.png')
    out = run_prep(src, tmp_path / 'up')
    assert Image.open(tmp_path / 'up' / 'r05.png').size == (530, 298)
    assert not (tmp_path / 'up' / 'r06.png').exists()
    assert 'box 530x300' in out and 'warning' not in out


def test_prep_cli_dept4_sizes_each_file_for_its_column(tmp_path: Path, video: Path) -> None:
    src = tmp_path / 'src'
    src.mkdir()
    for n in ('01', '02', '03'):
        Image.new('RGB', (1920, 1080)).save(src / f'{n}_畫面.png')
    (src / '07_test.mp4').write_bytes(video.read_bytes())
    spec = {'layout': 'dept4-slot', 'tabs': [
        {'tab': 'static', 'rows': [{'item': 'a', 'plan_image': 'r01.png', 'refs': ['r02.png']}]},
        {'tab': 'dynamic', 'rows': [{'item': 'b', 'refs': ['r07.gif']}]},
        {'tab': 'help', 'rows': [{'page': 'P1', 'plan_image': 'r03.png'}]}]}
    spec_path = tmp_path / 'spec.json'
    spec_path.write_text(json.dumps(spec), encoding='utf-8')
    out = run_prep(src, tmp_path / 'up', '--spec', str(spec_path))
    up = tmp_path / 'up'
    assert Image.open(up / 'r01.png').size == (380, 213)   # static plan image column 400px
    assert Image.open(up / 'r02.png').size == (280, 157)   # static ref column 300px
    assert Image.open(up / 'r03.png').size == (430, 241)   # help image column 450px
    assert Image.open(up / 'r07.gif').size == (180, 101)   # dynamic ref column 200px
    assert (src / '07_test.gif').exists()                  # full GIF kept next to the source
    assert 'first 10.0s' in out


def test_prep_cli_dept4_without_spec_warns(tmp_path: Path) -> None:
    src = tmp_path / 'src'
    src.mkdir()
    Image.new('RGB', (400, 200)).save(src / '01_a.png')
    out = run_prep(src, tmp_path / 'up', '--layout', 'dept4-slot')
    assert 'pass --spec' in out
    assert Image.open(tmp_path / 'up' / 'r01.png').size == (100, 50)


# ---------- fetch_plan ----------

def test_table_cell_keeps_row_on_one_line() -> None:
    fetch_plan = pytest.importorskip('fetch_plan')
    cell = [{'plain_text': '第一行\n第二行', 'annotations': {'color': 'red'}},
            {'plain_text': '\r\nA|B', 'annotations': {}}]
    text = fetch_plan.table_cell(cell)
    assert text == '<span color="red">第一行<br>第二行</span><br>A\\|B'
    assert '\n' not in text and '\r' not in text


# ---------- reference docs (rules found by the 2026-10-07 E2E run) ----------

REFS = SCRIPTS.parent / 'references'


def test_skill_md_explains_br_in_table_cells() -> None:
    text = (SCRIPTS.parent / 'SKILL.md').read_text(encoding='utf-8')
    assert '`<br>`' in text and '儲存格內的換行' in text


def test_help_tab_rule_checks_subsections_not_chapter_title() -> None:
    text = (REFS / 'writing-rules-dept4-slot.md').read_text(encoding='utf-8')
    section = text.split('## 說明頁分頁', 1)[1].split('\n## ', 1)[0]
    assert '看子節有沒有實際內容' in section
    assert '第 4 章標「待補」就只建表頭' not in section   # the old title-based rule is gone


def test_dynamic_reverse_check_is_documented() -> None:
    text = (REFS / 'writing-rules-dept4-slot.md').read_text(encoding='utf-8')
    dyn = text.split('## 動態分頁', 1)[1].split('\n## ', 1)[0]
    assert '反向' in dyn and 'Dialog 開關' in dyn and '缺漏清單' in dyn
    gaps = text.split('## 常見缺漏', 1)[1]
    assert '反向' in gaps


def test_chrome_paste_shows_tab_switch_with_existing_helper() -> None:
    text = (REFS / 'chrome-paste.md').read_text(encoding='utf-8')
    assert 'window.claudeGo = ' in text            # the helper the example relies on
    assert """claudeGo("'動態'!C3")""" in text
