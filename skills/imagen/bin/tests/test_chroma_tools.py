"""Unit tests for the shared chroma-key helpers in imagen/bin/chroma_tools.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chroma_tools import (  # noqa: E402
    Component,
    bbox_touches_edge,
    clean_edges,
    connected_components,
    pad_bbox,
    remove_bg_magenta,
    sanitize_slug,
    trim_border,
)

MAGENTA = (255, 0, 255, 255)
BLUE = (30, 120, 200, 255)
SHAPE_BOX = (20, 20, 44, 44)  # inclusive rectangle for ImageDraw
EDGE_BOX = (0, 50, 6, 63)  # touches left and bottom edges
SPECKS = [(52, 10), (56, 12), (60, 8)]  # single detached pixels


def make_sheet() -> Image.Image:
    """64x64 magenta sheet: one solid blue square, one edge-touching bar, three specks."""
    img = Image.new("RGBA", (64, 64), MAGENTA)
    draw = ImageDraw.Draw(img)
    draw.rectangle(SHAPE_BOX, fill=BLUE)
    draw.rectangle(EDGE_BOX, fill=BLUE)
    for x, y in SPECKS:
        img.putpixel((x, y), BLUE)
    return img


def test_remove_bg_magenta_clears_background_and_keeps_shape() -> None:
    src = make_sheet()
    out = remove_bg_magenta(src)
    assert out.mode == "RGBA"
    assert out.getpixel((1, 1)) == (0, 0, 0, 0)
    assert out.getpixel((32, 1)) == (0, 0, 0, 0)
    assert out.getpixel((30, 30)) == BLUE
    assert out.getpixel((2, 60)) == BLUE
    # Input must not be mutated.
    assert src.getpixel((1, 1)) == MAGENTA


def test_remove_bg_magenta_edge_threshold_clears_border_connected_fringe() -> None:
    img = Image.new("RGBA", (16, 16), MAGENTA)
    fringe = (220, 60, 220, 255)  # distance ~ 77 from magenta: below 100 anyway
    far_fringe = (180, 90, 180, 255)  # distance ~ 140: only caught by edge_threshold 150
    ImageDraw.Draw(img).rectangle((0, 0, 15, 1), fill=far_fringe)
    img.putpixel((8, 8), fringe)
    out = remove_bg_magenta(img, threshold=100, edge_threshold=150)
    assert out.getpixel((5, 0)) == (0, 0, 0, 0)
    assert out.getpixel((8, 8)) == (0, 0, 0, 0)


def test_trim_border_crops_and_handles_small_or_zero() -> None:
    img = Image.new("RGBA", (64, 64), MAGENTA)
    assert trim_border(img, 4).size == (56, 56)
    assert trim_border(img, 0).size == (64, 64)
    assert trim_border(img, -1).size == (64, 64)
    tiny = Image.new("RGBA", (6, 6), MAGENTA)
    assert trim_border(tiny, 4).size == (6, 6)


def test_clean_edges_removes_dark_lines_and_fringe_only_in_outer_rings() -> None:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 31, 31), outline=(10, 10, 10, 255))  # near-black grid line
    draw.rectangle((10, 10, 20, 20), fill=BLUE)
    img.putpixel((1, 15), (240, 30, 240, 255))  # magenta fringe inside ring 1
    img.putpixel((2, 15), BLUE)  # non-debris pixel in ring 2 must survive
    out = clean_edges(img, depth=2)
    assert out.getpixel((0, 15)) == (0, 0, 0, 0)
    assert out.getpixel((1, 15)) == (0, 0, 0, 0)
    assert out.getpixel((2, 15)) == BLUE
    assert out.getpixel((15, 15)) == BLUE
    assert clean_edges(img, depth=0) is img


def test_connected_components_counts_and_orders_by_area() -> None:
    cleaned = remove_bg_magenta(make_sheet())
    comps = connected_components(cleaned, min_area=1)
    assert len(comps) == 2 + len(SPECKS)
    assert all(isinstance(comp, Component) for comp in comps)
    assert [comp.area for comp in comps] == sorted((comp.area for comp in comps), reverse=True)
    assert comps[0].area == 25 * 25
    assert comps[0].bbox == (20, 20, 45, 45)
    assert comps[0].touches_edge is False
    assert comps[1].touches_edge is True
    assert comps[0].coords is None


def test_connected_components_min_area_drops_specks() -> None:
    cleaned = remove_bg_magenta(make_sheet())
    comps = connected_components(cleaned, min_area=2)
    assert len(comps) == 2


def test_connected_components_keep_coords() -> None:
    cleaned = remove_bg_magenta(make_sheet())
    comps = connected_components(cleaned, min_area=1, keep_coords=True)
    largest = comps[0]
    assert largest.coords is not None
    assert len(largest.coords) == largest.area
    assert (30, 30) in largest.coords


def test_largest_component_selection_ignores_specks() -> None:
    cleaned = remove_bg_magenta(make_sheet())
    largest = connected_components(cleaned)[0]
    for x, y in SPECKS:
        assert not (largest.bbox[0] <= x < largest.bbox[2] and largest.bbox[1] <= y < largest.bbox[3])


def test_bbox_touches_edge() -> None:
    assert bbox_touches_edge((0, 10, 20, 30), 64, 64) is True
    assert bbox_touches_edge((10, 10, 64, 30), 64, 64) is True
    assert bbox_touches_edge((10, 10, 20, 30), 64, 64) is False
    assert bbox_touches_edge((2, 10, 20, 30), 64, 64, margin=2) is True
    assert bbox_touches_edge(None, 64, 64) is False


def test_pad_bbox_clamps_to_image_bounds() -> None:
    assert pad_bbox((10, 10, 20, 20), 4, 64, 64) == (6, 6, 24, 24)
    assert pad_bbox((2, 3, 62, 63), 8, 64, 64) == (0, 0, 64, 64)
    assert pad_bbox((10, 10, 20, 20), 0, 64, 64) == (10, 10, 20, 20)


@pytest.mark.parametrize(
    ("raw", "fallback", "expected"),
    [
        ("Fire Golem!", "asset", "fire-golem"),
        ("  Mossy__Stone  ", "prop", "mossy-stone"),
        ("###", "prop", "prop"),
        ("", "sprite", "sprite"),
    ],
)
def test_sanitize_slug(raw: str, fallback: str, expected: str) -> None:
    assert sanitize_slug(raw, fallback=fallback) == expected
