#!/usr/bin/env python3
"""Shared chroma-key helpers for magenta-backdrop sprite and prop sheets.

Used by generate2dsprite/scripts/generate2dsprite.py and
generate2dmap/scripts/extract_prop_pack.py. Pure Pillow, no numpy.
"""

from __future__ import annotations

import math
import re
from collections import deque
from dataclasses import dataclass
from PIL import Image


MAGENTA: tuple[int, int, int] = (255, 0, 255)
DARK_LINE_MAX: int = 40
EDGE_MAGENTA_DISTANCE: float = 150.0

BBox = tuple[int, int, int, int]


@dataclass(slots=True)
class Component:
    """One 4-connected opaque region of an RGBA image.

    ``bbox`` is (x0, y0, x1, y1) with exclusive x1/y1, matching PIL crop boxes.
    ``coords`` is only populated when ``connected_components`` is called with
    ``keep_coords=True``.
    """

    area: int
    bbox: BBox
    touches_edge: bool
    coords: list[tuple[int, int]] | None = None


def color_distance(rgb: tuple[int, int, int], target: tuple[int, int, int] = MAGENTA) -> float:
    """Euclidean RGB distance between ``rgb`` and ``target`` (magenta by default)."""
    r, g, b = rgb
    tr, tg, tb = target
    return math.sqrt((r - tr) ** 2 + (g - tg) ** 2 + (b - tb) ** 2)


def remove_bg_magenta(img: Image.Image, threshold: int = 100, edge_threshold: int = 150) -> Image.Image:
    """Return an RGBA copy of ``img`` with the magenta backdrop made transparent.

    Two passes: every pixel closer than ``threshold`` to magenta is cleared, then a
    flood fill from the image border also clears border-connected pixels closer than
    the looser ``edge_threshold`` (antialiased fringe). The input is never mutated.
    """
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]
            if a > 0 and color_distance((r, g, b)) < threshold:
                pixels[x, y] = (0, 0, 0, 0)

    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or x < 0 or x >= width or y < 0 or y >= height:
            continue
        visited.add((x, y))
        r, g, b, a = pixels[x, y]
        should_expand = a == 0
        if a > 0 and color_distance((r, g, b)) < edge_threshold:
            pixels[x, y] = (0, 0, 0, 0)
            should_expand = True
        if should_expand:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nxt = (x + dx, y + dy)
                    if nxt not in visited:
                        queue.append(nxt)

    return img


def trim_border(img: Image.Image, px: int = 4) -> Image.Image:
    """Crop ``px`` pixels off every side; no-op when ``px <= 0`` or the image is too small."""
    if px <= 0:
        return img
    width, height = img.size
    if width <= px * 2 or height <= px * 2:
        return img
    return img.crop((px, px, width - px, height - px))


def clean_edges(img: Image.Image, depth: int = 3) -> Image.Image:
    """Clear near-black grid lines and magenta fringe in the outer ``depth`` pixel rings.

    Mutates and returns ``img``. No-op when ``depth <= 0``.
    """
    if depth <= 0:
        return img
    pixels = img.load()
    width, height = img.size

    def is_debris(r: int, g: int, b: int) -> bool:
        dark = r < DARK_LINE_MAX and g < DARK_LINE_MAX and b < DARK_LINE_MAX
        return dark or color_distance((r, g, b)) < EDGE_MAGENTA_DISTANCE

    for d in range(depth):
        for x in range(width):
            for y in (d, height - 1 - d):
                if 0 <= y < height:
                    r, g, b, a = pixels[x, y]
                    if a > 0 and is_debris(r, g, b):
                        pixels[x, y] = (0, 0, 0, 0)
        for y in range(height):
            for x in (d, width - 1 - d):
                if 0 <= x < width:
                    r, g, b, a = pixels[x, y]
                    if a > 0 and is_debris(r, g, b):
                        pixels[x, y] = (0, 0, 0, 0)
    return img


def connected_components(img: Image.Image, min_area: int = 1, keep_coords: bool = False) -> list[Component]:
    """Find 4-connected opaque regions, largest first, dropping those below ``min_area``.

    Set ``keep_coords=True`` to retain every pixel coordinate of each component
    (needed to mask an image down to a single component).
    """
    alpha = img.getchannel("A")
    pixels = alpha.load()
    width, height = img.size
    visited = [[False] * width for _ in range(height)]
    components: list[Component] = []

    for y in range(height):
        for x in range(width):
            if pixels[x, y] == 0 or visited[y][x]:
                continue
            queue: deque[tuple[int, int]] = deque([(x, y)])
            visited[y][x] = True
            coords: list[tuple[int, int]] = []
            area = 0
            min_x = max_x = x
            min_y = max_y = y
            touches_edge = x == 0 or y == 0 or x == width - 1 or y == height - 1

            while queue:
                cx, cy = queue.popleft()
                area += 1
                if keep_coords:
                    coords.append((cx, cy))
                min_x = min(min_x, cx)
                min_y = min(min_y, cy)
                max_x = max(max_x, cx)
                max_y = max(max_y, cy)
                if cx == 0 or cy == 0 or cx == width - 1 or cy == height - 1:
                    touches_edge = True
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < width and 0 <= ny < height and pixels[nx, ny] > 0 and not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue.append((nx, ny))

            if area >= min_area:
                components.append(
                    Component(
                        area=area,
                        bbox=(min_x, min_y, max_x + 1, max_y + 1),
                        touches_edge=touches_edge,
                        coords=coords if keep_coords else None,
                    )
                )

    components.sort(key=lambda item: item.area, reverse=True)
    return components


def pad_bbox(bbox: BBox, padding: int, width: int, height: int) -> BBox:
    """Grow ``bbox`` by ``padding`` on every side, clamped to a ``width`` x ``height`` image."""
    x0, y0, x1, y1 = bbox
    return (
        max(0, x0 - padding),
        max(0, y0 - padding),
        min(width, x1 + padding),
        min(height, y1 + padding),
    )


def bbox_touches_edge(bbox: BBox | None, width: int, height: int, margin: int = 0) -> bool:
    """True when ``bbox`` comes within ``margin`` pixels of any image edge. ``None`` is False."""
    if not bbox:
        return False
    x0, y0, x1, y1 = bbox
    return x0 <= margin or y0 <= margin or x1 >= width - margin or y1 >= height - margin


def sanitize_slug(text: str, fallback: str = "asset") -> str:
    """Lowercase ``text`` to a filesystem-safe dash slug; return ``fallback`` when nothing survives."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or fallback
