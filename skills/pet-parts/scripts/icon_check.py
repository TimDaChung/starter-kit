"""Split a skill-icon sheet into square icons and preview them at in-game sizes.

The model draws all of a pet's skill icons side by side on gray (one call keeps
their style consistent). This script cuts each icon out as a square PNG and
writes a preview sheet showing every icon at 256 / 128 / 64 px, because an
icon that reads well large can turn to mush at the size players actually see.

Usage:
    python icon_check.py <sheet.png> <out_dir> --names 凌空疾翔,銳視鷹眼 [--size 512] [--threshold 28]

Icons are found by column projection against the corner-sampled gray. The
number found must equal the number of names.
"""
import argparse
import pathlib

from PIL import Image, ImageChops, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msjhbd.ttc",
    "C:/Windows/Fonts/msjh.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]
PREVIEW_SIZES = (256, 128, 64)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    raise SystemExit("no CJK font found; add one to FONT_CANDIDATES")


def corner_gray(img: Image.Image) -> tuple[int, int, int]:
    w, h = img.size
    px = [img.getpixel(p) for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
    return tuple(sum(c[i] for c in px) // 4 for i in range(3))


def find_boxes(img: Image.Image, threshold: int) -> list[tuple[int, int, int, int]]:
    gray = corner_gray(img)
    mask = ImageChops.difference(img, Image.new("RGB", img.size, gray)).convert("L")
    mask = mask.point(lambda v: 255 if v > threshold else 0)
    w, h = mask.size
    cols = [any(mask.getpixel((x, y)) for y in range(0, h, 3)) for x in range(w)]
    boxes, start = [], None
    for x, on in enumerate(cols + [False]):
        if on and start is None:
            start = x
        elif not on and start is not None:
            if x - start > w * 0.05:
                sub = mask.crop((start, 0, x, h)).getbbox()
                boxes.append((start, sub[1], x, sub[3]))
            start = None
    return boxes


def square(img: Image.Image, box: tuple[int, int, int, int], size: int) -> Image.Image:
    l, t, r, b = box
    side = max(r - l, b - t)
    cx, cy = (l + r) // 2, (t + b) // 2
    crop = img.crop((cx - side // 2, cy - side // 2, cx - side // 2 + side, cy - side // 2 + side))
    return crop.resize((size, size), Image.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("out_dir")
    parser.add_argument("--names", required=True)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--threshold", type=int, default=28)
    args = parser.parse_args()

    names = [n.strip() for n in args.names.split(",")]
    src = Image.open(args.src).convert("RGB")
    boxes = find_boxes(src, args.threshold)
    if len(boxes) != len(names):
        raise SystemExit(f"found {len(boxes)} icons, expected {len(names)}: {boxes}")

    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    icons = []
    for name, box in zip(names, boxes):
        icon = square(src, box, args.size)
        icon.save(out / f"ICON_{name}.png")
        icons.append(icon)
        print(f"  {name}: {box[2] - box[0]}x{box[3] - box[1]}px -> ICON_{name}.png")

    pad, label_h = 24, 40
    row_h = max(PREVIEW_SIZES) + label_h + pad
    width = pad + sum(s + pad for s in PREVIEW_SIZES)
    sheet = Image.new("RGB", (width, pad + row_h * len(icons)), (40, 40, 40))
    draw = ImageDraw.Draw(sheet)
    font = load_font(22)
    for i, (name, icon) in enumerate(zip(names, icons)):
        y = pad + i * row_h
        draw.text((pad, y), name, font=font, fill=(255, 255, 255))
        x = pad
        for s in PREVIEW_SIZES:
            sheet.paste(icon.resize((s, s), Image.LANCZOS), (x, y + label_h + max(PREVIEW_SIZES) - s))
            draw.text((x, y + label_h + max(PREVIEW_SIZES) + 2), f"{s}px", font=load_font(14), fill=(180, 180, 180))
            x += s + pad
    sheet.save(out / "ICON_尺寸預覽.png")
    print(f"preview: {out / 'ICON_尺寸預覽.png'} — check the 64px column reads at a glance")


if __name__ == "__main__":
    main()
