"""Tidy a prop level-series sheet: find each item, optionally equalize sizes, add level labels.

The model draws the series in one row on gray (so style stays consistent), but
it tends to make higher levels bigger and spaces them unevenly. Items that
share the board in game (e.g. 8 gems at once) must be the same size, so size
is fixed here instead of in the prompt.

Usage:
    python lineup.py <sheet.png> <out.png> --labels 灰幻石,藍幻石,紫幻石,紅幻石,彩幻石
                     [--equalize] [--height 0.45] [--width 1920] [--threshold 28]

Items are found by column projection: columns whose pixels differ from the
background gray (sampled at the corners) by more than --threshold. The number
of items found must equal the number of labels, otherwise the script stops and
reports what it saw (merge the gap, or regenerate with more spacing).

--equalize  scale every item to the same height (--height of the canvas)
            and space them evenly; without it the original sizes are kept.
"""
import argparse
import pathlib

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msjhbd.ttc",
    "C:/Windows/Fonts/msjh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit("no CJK font found; add one to FONT_CANDIDATES")


def corner_gray(img: Image.Image) -> tuple[int, int, int]:
    w, h = img.size
    px = [img.getpixel(p) for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
    return tuple(sum(c[i] for c in px) // 4 for i in range(3))


def subject_mask(img: Image.Image, gray: tuple[int, int, int], threshold: int) -> Image.Image:
    diff = ImageChops.difference(img, Image.new("RGB", img.size, gray)).convert("L")
    return diff.point(lambda v: 255 if v > threshold else 0)


def find_items(mask: Image.Image, min_gap: int) -> list[tuple[int, int, int, int]]:
    w, h = mask.size
    cols = [any(mask.getpixel((x, y)) for y in range(0, h, 3)) for x in range(w)]
    spans, start, gap = [], None, 0
    for x, on in enumerate(cols + [False] * (min_gap + 1)):
        if on:
            start = x if start is None else start
            gap = 0
        elif start is not None:
            gap += 1
            if gap > min_gap:
                spans.append((start, x - gap + 1))
                start, gap = None, 0
    boxes = []
    for left, right in spans:
        if right - left < w * 0.02:  # stray sparks, not an item
            continue
        box = mask.crop((left, 0, right, h)).getbbox()
        boxes.append((left, box[1], right, box[3]))
    return boxes


def feather(img: Image.Image, gray: tuple[int, int, int]) -> Image.Image:
    diff = ImageChops.difference(img, Image.new("RGB", img.size, gray)).convert("L")
    ramp = diff.point(lambda v: 0 if v <= 6 else 255 if v >= 30 else (v - 6) * 255 // 24)
    return ramp.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--equalize", action="store_true")
    parser.add_argument("--height", type=float, default=0.45)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--threshold", type=int, default=28)
    args = parser.parse_args()

    labels = [s.strip() for s in args.labels.split(",")]
    src = Image.open(args.src).convert("RGB")
    gray = corner_gray(src)
    boxes = find_items(subject_mask(src, gray, args.threshold), min_gap=max(4, src.width // 200))
    if len(boxes) != len(labels):
        spans = ", ".join(f"x{b[0]}-{b[2]}" for b in boxes)
        raise SystemExit(f"found {len(boxes)} items ({spans}) but {len(labels)} labels")

    canvas_w, canvas_h = args.width, round(args.width * 9 / 16)
    canvas = Image.new("RGB", (canvas_w, canvas_h), gray)
    slot = canvas_w / len(boxes)
    target_h = canvas_h * args.height
    base_scale = canvas_w / src.width
    label_y = []
    pad = 10
    for i, (l, t, r, b) in enumerate(boxes):
        item = src.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, src.width), min(b + pad, src.height)))
        scale = min(target_h / (b - t), slot * 0.85 / (r - l)) if args.equalize else base_scale
        item = item.resize((round(item.width * scale), round(item.height * scale)), Image.LANCZOS)
        x = round(slot * i + (slot - item.width) / 2)
        y = round(canvas_h * 0.47 - item.height / 2) if args.equalize else round(t * base_scale)
        canvas.paste(item, (x, y), feather(item, gray))
        label_y.append(y + item.height)
        print(f"  {labels[i]}: source {r - l}x{b - t}px -> {item.width}x{item.height}px")

    draw = ImageDraw.Draw(canvas)
    font = load_font(round(canvas_h * 0.04))
    text_y = min(max(label_y) + round(canvas_h * 0.04), canvas_h - round(canvas_h * 0.08))
    for i, label in enumerate(labels):
        cx = slot * i + slot / 2
        box = draw.textbbox((0, 0), label, font=font)
        draw.text((cx - (box[2] - box[0]) / 2, text_y), label, font=font, fill=(255, 255, 255),
                  stroke_width=3, stroke_fill=(30, 30, 30))
    canvas.save(args.dst)
    print(f"{args.dst}: {canvas_w}x{canvas_h}, {len(boxes)} items{' equalized' if args.equalize else ''}")


if __name__ == "__main__":
    main()
