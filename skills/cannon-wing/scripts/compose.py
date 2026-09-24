"""Compose sliced part tiles into the standard overview sheet.

Rows are built as: cannon / wing / combo, where the combo row is composited
here rather than drawn by the model — that is what guarantees the cannon sits
fully in front of the wings and that the bottom row uses the exact same assets
as the two rows above it.

When the set has no wing part (a cannon-only revision plan), pass --no-wing and
only the cannon row is emitted.

Usage:
    python compose.py <tiles_dir> <out_dir> <title> [--levels lv0,lv1,lv2]
                      [--no-wing] [--wing-offset 0]
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

BG = (0x7A, 0x6E, 0x68, 255)
PAD = 48
LABEL_BAND = 110
FONT_PATHS = ["C:/Windows/Fonts/msjhbd.ttc", "C:/Windows/Fonts/msjh.ttc"]
LABEL_TEXT = {
    "lv0": "lv0",
    "lv1": "lv1(lv0+2星特效)",
    "lv2": "lv2(4星造型+2星特效)",
}


def load_font(size: int):
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tiles")
    ap.add_argument("out")
    ap.add_argument("title")
    ap.add_argument("--levels", default="lv0,lv1,lv2")
    ap.add_argument("--no-wing", action="store_true")
    ap.add_argument(
        "--wing-offset",
        type=int,
        default=0,
        help="shift wings down by N px when compositing the combo row",
    )
    args = ap.parse_args()

    levels = args.levels.split(",")
    os.makedirs(args.out, exist_ok=True)

    cannons = [Image.open(f"{args.tiles}/cannon_{lv}.png").convert("RGBA") for lv in levels]
    rows = [cannons]

    if not args.no_wing:
        wings = [Image.open(f"{args.tiles}/wing_{lv}.png").convert("RGBA") for lv in levels]
        combos = []
        for cannon, wing in zip(cannons, wings):
            cw, ch = cannon.size
            ww, wh = wing.size
            w = max(cw, ww)
            h = max(ch, wh + args.wing_offset)
            canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            canvas.alpha_composite(wing, ((w - ww) // 2, (h - wh) // 2 + args.wing_offset))
            canvas.alpha_composite(cannon, ((w - cw) // 2, (h - ch) // 2))
            combos.append(canvas)
        rows += [wings, combos]

    n_col = len(levels)
    n_row = len(rows)
    cell_w = max(im.width for row in rows for im in row)
    cell_h = max(im.height for row in rows for im in row)
    sheet_w = cell_w * n_col + PAD * (n_col + 1)
    sheet_h = cell_h * n_row + PAD * (n_row + 1) + LABEL_BAND
    sheet = Image.new("RGBA", (sheet_w, sheet_h), BG)

    for ri, row in enumerate(rows):
        for ci, im in enumerate(row):
            x = PAD + ci * (cell_w + PAD) + (cell_w - im.width) // 2
            y = PAD + ri * (cell_h + PAD) + (cell_h - im.height) // 2
            sheet.alpha_composite(im, (x, y))

    font = load_font(52)
    draw = ImageDraw.Draw(sheet)
    label_y = PAD + n_row * (cell_h + PAD) + 8
    for ci, lv in enumerate(levels):
        text = LABEL_TEXT.get(lv, lv)
        centre = PAD + ci * (cell_w + PAD) + cell_w // 2
        box = draw.textbbox((0, 0), text, font=font)
        draw.text(
            (centre - (box[2] - box[0]) // 2, label_y),
            text,
            font=font,
            fill=(255, 255, 255, 255),
        )

    path = os.path.join(args.out, f"{args.title}.jpg")
    sheet.convert("RGB").save(path, quality=95)
    print(f"saved {path}  {sheet_w}x{sheet_h}  grid {n_row}x{n_col}  cell {cell_w}x{cell_h}")


if __name__ == "__main__":
    main()
