"""End-to-end CLI tests for generate2dsprite.py process and extract_prop_pack.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
SKILLS_ROOT = SCRIPTS_DIR.parents[1]
SPRITE_SCRIPT = SCRIPTS_DIR / "generate2dsprite.py"
PROP_SCRIPT = SKILLS_ROOT / "generate2dmap" / "scripts" / "extract_prop_pack.py"

MAGENTA = (255, 0, 255, 255)
CELL = 128
BLOB_COLORS = [
    (30, 120, 200, 255),
    (200, 60, 40, 255),
    (40, 180, 90, 255),
    (230, 200, 40, 255),
]


def make_grid_sheet(rows: int, cols: int) -> Image.Image:
    """Magenta sheet with one distinct centered blob per cell (well inside the cell)."""
    img = Image.new("RGBA", (cols * CELL, rows * CELL), MAGENTA)
    draw = ImageDraw.Draw(img)
    for index in range(rows * cols):
        row, col = divmod(index, cols)
        x0, y0 = col * CELL + 32, row * CELL + 32
        # Vary blob shape per cell so frames are visibly distinct.
        x1, y1 = x0 + 48 + 4 * index, y0 + 60 - 4 * index
        draw.ellipse((x0, y0, x1, y1), fill=BLOB_COLORS[index % len(BLOB_COLORS)])
    return img


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def assert_transparent_corners(path: Path) -> None:
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        assert img.getpixel(corner)[3] == 0, f"{path.name} corner {corner} is not transparent"


def test_process_builtin_2x2_mode(tmp_path: Path) -> None:
    sheet = tmp_path / "sheet.png"
    make_grid_sheet(2, 2).save(sheet)
    out_dir = tmp_path / "out"

    result = run(
        [
            sys.executable,
            str(SPRITE_SCRIPT),
            "process",
            "--input",
            str(sheet),
            "--target",
            "creature",
            "--mode",
            "idle",
            "--output-dir",
            str(out_dir),
            "--shared-scale",
        ]
    )
    assert result.returncode == 0, result.stderr

    assert (out_dir / "sheet-transparent.png").exists()
    assert (out_dir / "raw-sheet.png").exists()
    assert (out_dir / "raw-sheet-clean.png").exists()
    assert (out_dir / "animation.gif").exists()
    frame_paths = [out_dir / f"idle-{index}.png" for index in range(1, 5)]
    for frame_path in frame_paths:
        assert frame_path.exists()
        assert Image.open(frame_path).size == (CELL, CELL)
        assert_transparent_corners(frame_path)
        assert Image.open(frame_path).getbbox() is not None

    meta = json.loads((out_dir / "pipeline-meta.json").read_text(encoding="utf-8"))
    assert meta["rows"] == 2 and meta["cols"] == 2
    assert meta["frame_labels"] == ["idle-1", "idle-2", "idle-3", "idle-4"]
    assert len(meta["frames"]) == 4
    assert meta["edge_touch_frames"] == []
    assert all(frame["component_count"] == 1 for frame in meta["frames"])

    gif = Image.open(out_dir / "animation.gif")
    assert gif.n_frames == 4


def test_process_custom_grid_uses_label_prefix(tmp_path: Path) -> None:
    sheet = tmp_path / "sheet.png"
    make_grid_sheet(1, 3).save(sheet)
    out_dir = tmp_path / "out"
    result = run(
        [
            sys.executable,
            str(SPRITE_SCRIPT),
            "process",
            "--input",
            str(sheet),
            "--target",
            "asset",
            "--mode",
            "talk",
            "--rows",
            "1",
            "--cols",
            "3",
            "--label-prefix",
            "talk",
            "--output-dir",
            str(out_dir),
            "--component-mode",
            "largest",
        ]
    )
    assert result.returncode == 0, result.stderr
    for index in range(1, 4):
        assert (out_dir / f"talk-{index}.png").exists()
    assert (out_dir / "animation.gif").exists()


def test_process_rejects_unknown_mode_without_custom_grid(tmp_path: Path) -> None:
    sheet = tmp_path / "sheet.png"
    make_grid_sheet(2, 2).save(sheet)
    result = run(
        [
            sys.executable,
            str(SPRITE_SCRIPT),
            "process",
            "--input",
            str(sheet),
            "--target",
            "asset",
            "--mode",
            "not-a-mode",
            "--output-dir",
            str(tmp_path / "out"),
        ]
    )
    assert result.returncode != 0
    assert "invalid for target" in result.stderr
    assert not (tmp_path / "out").exists()


def test_process_single_mode(tmp_path: Path) -> None:
    sheet = tmp_path / "single.png"
    make_grid_sheet(1, 1).save(sheet)
    out_dir = tmp_path / "out"
    result = run(
        [
            sys.executable,
            str(SPRITE_SCRIPT),
            "process",
            "--input",
            str(sheet),
            "--target",
            "asset",
            "--mode",
            "single",
            "--output-dir",
            str(out_dir),
        ]
    )
    assert result.returncode == 0, result.stderr
    clean = out_dir / "clean.png"
    assert clean.exists()
    assert Image.open(clean).size == (256, 256)
    assert_transparent_corners(clean)


def test_help_has_no_build_prompt() -> None:
    result = run([sys.executable, str(SPRITE_SCRIPT), "--help"])
    assert result.returncode == 0
    assert "build-prompt" not in result.stdout
    assert "process" in result.stdout


@pytest.mark.skipif(not PROP_SCRIPT.exists(), reason="generate2dmap skill not present")
def test_extract_prop_pack_1x1(tmp_path: Path) -> None:
    sheet = tmp_path / "props.png"
    make_grid_sheet(1, 1).save(sheet)
    out_dir = tmp_path / "props"
    result = run(
        [
            sys.executable,
            str(PROP_SCRIPT),
            "--input",
            str(sheet),
            "--rows",
            "1",
            "--cols",
            "1",
            "--labels",
            "test",
            "--output-dir",
            str(out_dir),
        ]
    )
    assert result.returncode == 0, result.stderr
    prop = out_dir / "test" / "prop.png"
    assert prop.exists()
    assert_transparent_corners(prop)
    manifest = json.loads((out_dir / "prop-pack.json").read_text(encoding="utf-8"))
    assert [item["label"] for item in manifest["accepted"]] == ["test"]
    assert manifest["rejected"] == []
