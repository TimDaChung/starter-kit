# -*- coding: utf-8 -*-
"""Objective aids for promo-banner review.

Builds a 4-panel contact sheet (original / thumbnail / grayscale / blur) and
prints luminance + saturation metrics. The metrics are aids, not verdicts:
the ironclad rules are still judged by eye on the panels.

Usage:
    python banner_check.py <image> [<image> ...] [--out DIR] [--thumb 180]
"""
import argparse
import os
import sys
from typing import List, Tuple

from PIL import Image, ImageFilter

PANEL_W = 760


def _panels(im: Image.Image, thumb_w: int) -> List[Tuple[str, Image.Image]]:
    """Original, lobby-thumbnail, grayscale and blur views of one banner."""
    w, h = im.size
    scale = PANEL_W / float(w)
    base = im.resize((PANEL_W, max(1, int(h * scale))), Image.LANCZOS)

    thumb_h = max(1, int(h * (thumb_w / float(w))))
    thumb = im.resize((thumb_w, thumb_h), Image.LANCZOS).resize(base.size, Image.NEAREST)

    gray = base.convert("L").convert("RGB")
    blur = base.filter(ImageFilter.GaussianBlur(radius=max(4, PANEL_W // 45)))
    return [("original", base), ("thumb %dpx" % thumb_w, thumb),
            ("grayscale", gray), ("blur", blur)]


def _metrics(im: Image.Image) -> str:
    """Luminance centre of mass, brightest grid cells, saturation spread."""
    small = im.resize((100, 100), Image.LANCZOS)
    lum = small.convert("L").load()
    hsv = small.convert("HSV").load()

    total = cx = cy = 0.0
    for y in range(100):
        for x in range(100):
            v = lum[x, y] ** 2  # square so highlights dominate, as the eye does
            total += v
            cx += x * v
            cy += y * v
    cx, cy = (cx / total, cy / total) if total else (50.0, 50.0)

    cells = []
    for gy in range(5):
        for gx in range(5):
            vals = [lum[x, y] for y in range(gy * 20, gy * 20 + 20)
                    for x in range(gx * 20, gx * 20 + 20)]
            cells.append((sum(vals) / len(vals), gx, gy))
    cells.sort(reverse=True)
    names = ["左", "中左", "中", "中右", "右"]
    rows = ["上", "中上", "中", "中下", "下"]
    hot = "、".join("%s%s(%.0f)" % (rows[c[2]], names[c[1]], c[0]) for c in cells[:3])

    vivid = 0
    hues = [0] * 12
    for y in range(100):
        for x in range(100):
            hh, ss, vv = hsv[x, y]
            if ss > 153 and vv > 153:  # S>0.6, V>0.6
                vivid += 1
                hues[int(hh / 256.0 * 12) % 12] += 1
    top_hue = sorted(range(12), key=lambda i: -hues[i])[:3]
    hue_names = ["紅", "橙", "黃", "黃綠", "綠", "青綠", "青", "天藍",
                 "藍", "紫", "洋紅", "粉紅"]
    hue_share = sum(hues[i] for i in top_hue) / float(vivid) if vivid else 0.0
    hue_txt = "、".join("%s %.0f%%" % (hue_names[i], 100.0 * hues[i] / vivid)
                        for i in top_hue) if vivid else "—"

    return ("  亮度重心：x %.0f%% / y %.0f%%（越接近 50/50 越像有中央能量區）\n"
            "  最亮三格：%s\n"
            "  高飽和像素：%.1f%%（全圖一起豔 → 偏高；色彩集中 → 10~35%% 常見）\n"
            "  高飽和主色：%s（前三色合計 %.0f%%，越高代表主色越收斂）"
            % (cx, cy, hot, vivid / 100.0, hue_txt, 100 * hue_share))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--out", default=".")
    ap.add_argument("--thumb", type=int, default=180,
                    help="lobby thumbnail width in px (default 180)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    # Windows consoles default to cp950 here; force UTF-8 so the report is readable.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    for path in args.images:
        im = Image.open(path).convert("RGB")
        panels = _panels(im, args.thumb)
        ph = panels[0][1].size[1]
        sheet = Image.new("RGB", (PANEL_W, ph * len(panels) + 6 * (len(panels) - 1)), "white")
        for i, (_, panel) in enumerate(panels):
            sheet.paste(panel, (0, i * (ph + 6)))
        name = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(args.out, "%s_check.jpg" % name)
        sheet.save(out, quality=85)
        print("%s  %dx%d" % (os.path.basename(path), im.size[0], im.size[1]))
        print(_metrics(im))
        print("  面板（上到下：原圖 / 縮圖 / 灰階 / 模糊）：%s\n" % out)


if __name__ == "__main__":
    main()
