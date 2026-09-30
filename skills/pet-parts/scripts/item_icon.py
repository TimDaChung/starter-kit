"""Post-process an item icon (道具縮圖) from a finished design image.

No image generation involved: the icon is the approved design itself,
cropped to a square and placed on a dark rounded board. Shared by the
pet, cannon-wing and weapon lines.

Usage:
    python item_icon.py <master.png> <out_dir> --name <item>
        [--half left|right]        # take one half first (pet line: stage 1 / stage 2)
        [--region x0,y0,x1,y1]     # or an explicit crop box in source pixels
        [--board dark|none]        # dark rounded board (default) or transparent
        [--badge <png>] [--badge-scale 0.28] [--badge-corner top-left]
        [--size 512] [--margin 0.08]

Outputs in <out_dir>:
    ICON_<name>.png            square icon, <size> px
    ICON_<name>_fragment.png   same with the badge overlaid (only with --badge)
    ICON_<name>_尺寸預覽.png    256 / 128 / 64 px row for a readability check
"""

from __future__ import annotations

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BG_TOLERANCE = 28          # colour distance treated as "background"
FEATHER_PX = 2             # soft edge after keying out the background
PREVIEW_SIZES = (256, 128, 64)
BOARD_TOP = (46, 34, 24)   # dark brown
BOARD_BOTTOM = (22, 34, 52)  # dark blue
BOARD_BORDER = (196, 156, 72)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an item icon from a finished design image.")
    parser.add_argument("master", help="finished design image (grey background or transparent PNG)")
    parser.add_argument("out_dir", help="output directory")
    parser.add_argument("--name", required=True, help="item name used in output file names")
    parser.add_argument("--half", choices=["left", "right"], help="use only this half of the source first")
    parser.add_argument("--region", help="explicit crop box x0,y0,x1,y1 in source pixels")
    parser.add_argument("--grid", help="source is an RxC overview sheet, e.g. 3x3 (cannon-wing line)")
    parser.add_argument("--cell", help="which grid cell to take, row,col counted from 1 (e.g. 3,1 = bottom-left)")
    parser.add_argument("--grid-bottom", type=float, default=0.0,
                        help="fraction of height reserved for captions under the grid (excluded before splitting)")
    parser.add_argument("--board", choices=["dark", "none"], default="dark")
    parser.add_argument("--badge", help="transparent PNG badge to overlay (fragment icon)")
    parser.add_argument("--badge-scale", type=float, default=0.28, help="badge side as a fraction of icon side")
    parser.add_argument("--badge-corner", choices=["top-left", "top-right", "bottom-left", "bottom-right"],
                        default="top-left")
    parser.add_argument("--badge-margin", type=float, default=0.04, help="badge inset as a fraction of icon side")
    parser.add_argument("--size", type=int, default=512, help="icon side in px")
    parser.add_argument("--margin", type=float, default=0.08, help="padding around the subject as a fraction")
    return parser.parse_args()


def key_out_background(img: Image.Image) -> Image.Image:
    """Return an RGBA image whose flat background is transparent.

    A PNG that already carries meaningful alpha is returned as is; otherwise the
    background colour is sampled from the four corners and keyed out.
    """
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getextrema()[0] < 255:
        return rgba
    w, h = rgba.size
    corners = [rgba.getpixel((0, 0)), rgba.getpixel((w - 1, 0)), rgba.getpixel((0, h - 1)), rgba.getpixel((w - 1, h - 1))]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    px = rgba.load()
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            dist = max(abs(r - bg[0]), abs(g - bg[1]), abs(b - bg[2]))
            if dist <= BG_TOLERANCE:
                px[x, y] = (r, g, b, 0)
            elif dist <= BG_TOLERANCE * 2:
                px[x, y] = (r, g, b, int(255 * (dist - BG_TOLERANCE) / BG_TOLERANCE))
    soft = rgba.getchannel("A").filter(ImageFilter.GaussianBlur(FEATHER_PX))
    rgba.putalpha(soft)
    return rgba


def crop_subject(rgba: Image.Image, margin: float) -> Image.Image:
    bbox = rgba.getchannel("A").getbbox()
    if bbox is None:
        raise SystemExit("no subject found after keying out the background")
    subject = rgba.crop(bbox)
    side = int(max(subject.size) * (1 + margin * 2))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(subject, ((side - subject.width) // 2, (side - subject.height) // 2), subject)
    return canvas


def make_board(size: int) -> Image.Image:
    board = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gradient = Image.new("RGBA", (size, size))
    gpx = gradient.load()
    for y in range(size):
        t = y / max(size - 1, 1)
        colour = tuple(int(BOARD_TOP[i] * (1 - t) + BOARD_BOTTOM[i] * t) for i in range(3)) + (255,)
        for x in range(size):
            gpx[x, y] = colour
    radius = size // 9
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    board.paste(gradient, (0, 0), mask)
    border = max(2, size // 128)
    ImageDraw.Draw(board).rounded_rectangle((border // 2, border // 2, size - 1 - border // 2, size - 1 - border // 2),
                                            radius=radius, outline=BOARD_BORDER, width=border)
    return board


def overlay_badge(icon: Image.Image, badge_path: str, scale: float, corner: str, margin: float) -> Image.Image:
    badge = Image.open(badge_path).convert("RGBA")
    side = int(icon.width * scale)
    ratio = side / max(badge.size)
    badge = badge.resize((max(1, int(badge.width * ratio)), max(1, int(badge.height * ratio))), Image.LANCZOS)
    inset = int(icon.width * margin)
    x = inset if "left" in corner else icon.width - badge.width - inset
    y = inset if "top" in corner else icon.height - badge.height - inset
    out = icon.copy()
    out.paste(badge, (x, y), badge)
    return out


def make_preview(icon: Image.Image, name: str) -> Image.Image:
    gap = 24
    width = sum(PREVIEW_SIZES) + gap * (len(PREVIEW_SIZES) + 1)
    height = PREVIEW_SIZES[0] + 80
    preview = Image.new("RGB", (width, height), (40, 40, 40))
    draw = ImageDraw.Draw(preview)
    try:
        font = ImageFont.truetype("msjh.ttc", 20)
    except OSError:
        font = ImageFont.load_default()
    draw.text((gap, 14), name, fill=(235, 235, 235), font=font)
    x = gap
    for size in PREVIEW_SIZES:
        thumb = icon.resize((size, size), Image.LANCZOS)
        y = 50 + (PREVIEW_SIZES[0] - size)
        preview.paste(thumb, (x, y), thumb)
        draw.text((x, y + size + 4), f"{size}px", fill=(200, 200, 200), font=font)
        x += size + gap
    return preview


def main() -> None:
    args = parse_args()
    src = Image.open(args.master)
    if args.region:
        x0, y0, x1, y1 = (int(v) for v in args.region.split(","))
        src = src.crop((x0, y0, x1, y1))
    elif args.grid:
        if not args.cell:
            raise SystemExit("--grid needs --cell row,col")
        rows, cols = (int(v) for v in args.grid.lower().split("x"))
        row, col = (int(v) for v in args.cell.split(","))
        w, h = src.size
        usable_h = int(h * (1 - args.grid_bottom))
        cw, ch = w / cols, usable_h / rows
        src = src.crop((int((col - 1) * cw), int((row - 1) * ch), int(col * cw), int(row * ch)))
    elif args.half:
        w, h = src.size
        src = src.crop((0, 0, w // 2, h) if args.half == "left" else (w // 2, 0, w, h))

    subject = crop_subject(key_out_background(src), args.margin).resize((args.size, args.size), Image.LANCZOS)
    icon = make_board(args.size) if args.board == "dark" else Image.new("RGBA", (args.size, args.size), (0, 0, 0, 0))
    icon.paste(subject, (0, 0), subject)

    os.makedirs(args.out_dir, exist_ok=True)
    icon_path = os.path.join(args.out_dir, f"ICON_{args.name}.png")
    icon.save(icon_path)
    print(f"{icon_path}: {args.size}x{args.size}, board={args.board}")

    if args.badge:
        fragment = overlay_badge(icon, args.badge, args.badge_scale, args.badge_corner, args.badge_margin)
        fragment_path = os.path.join(args.out_dir, f"ICON_{args.name}_fragment.png")
        fragment.save(fragment_path)
        print(f"{fragment_path}: badge {int(args.badge_scale * 100)}% at {args.badge_corner}")

    preview_path = os.path.join(args.out_dir, f"ICON_{args.name}_尺寸預覽.png")
    make_preview(icon, args.name).save(preview_path)
    print(f"{preview_path}: check the 64px column reads at a glance")


if __name__ == "__main__":
    sys.exit(main())
