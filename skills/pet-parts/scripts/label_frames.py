"""Normalize a pet-animation storyboard to its exact grid ratio and tag each frame.

The model draws the frames in one image (so the pet stays identical); text is
added here, never in the prompt (models misspell Chinese and invent UI).

Usage:
    python label_frames.py <sheet.png> <out.png> --cols 3 --rows 1 \
        --captions "站著轉頭向左看|轉頭向右看|跨步張弓瞄準" [--title 一般動態] [--cell-width 960]

Cells keep the shape the model drew. The engine caps output around 3:1, so a
1x3 strip cannot be 48:9 and cells come out near-square; for a pose storyboard
that is fine (the pet is bigger). The sheet is only scaled to --width.
"""
import argparse
import pathlib

from PIL import Image, ImageDraw, ImageFont

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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    parser.add_argument("--cols", type=int, required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--captions", required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--width", type=int, default=2400)
    args = parser.parse_args()

    captions = [c.strip() for c in args.captions.split("|")]
    if len(captions) != args.cols * args.rows:
        raise SystemExit(f"{len(captions)} captions for a {args.cols}x{args.rows} grid")

    src = Image.open(args.src).convert("RGB")
    # each cell should be at least roughly square; a 1x3 request returned as 16:9 means one big frame
    if (src.width / args.cols) / (src.height / args.rows) < 0.75:
        raise SystemExit(f"source {src.width}x{src.height} is too narrow for {args.cols} columns: "
                         "the model drew fewer panels than asked, regenerate")
    size = (args.width, round(args.width * src.height / src.width))
    sheet = src.resize(size, Image.LANCZOS)
    cell_w, cell_h = size[0] // args.cols, size[1] // args.rows

    draw = ImageDraw.Draw(sheet)
    font = load_font(round(min(cell_w, cell_h) * 0.055))
    pad = round(cell_h * 0.025)
    for i, caption in enumerate(captions):
        row, col = divmod(i, args.cols)
        x, y = col * cell_w + pad * 2, row * cell_h + pad * 2
        prefix = f"{args.title} " if args.title and i == 0 else ""
        text = f"{prefix}圖{i + 1}  {caption}"
        box = draw.textbbox((x + pad, y + pad), text, font=font)
        draw.rectangle((x, y, box[2] + pad, box[3] + pad), fill=(255, 196, 0))
        draw.text((x + pad, y + pad), text, font=font, fill=(0, 0, 0))

    sheet.save(args.dst)
    print(f"{args.dst}: {size[0]}x{size[1]} ({args.cols}x{args.rows}, cell {cell_w}x{cell_h})")


if __name__ == "__main__":
    main()
