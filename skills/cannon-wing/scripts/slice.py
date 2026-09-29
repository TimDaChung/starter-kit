"""Slice a transparent-PNG part sheet into individual tiles.

The sheet is what image-studio returns for the cannon-wing prompt: one row per
part type (cannon / wing), one column per level (lv0 / lv1 / lv2), drawn on a
background that --remove-background has already stripped to alpha 0.

Usage:
    python slice.py <sheet.png> <out_dir> [--cols 3] [--rows 2]
                    [--row-names cannon,wing] [--col-names lv0,lv1,lv2]
"""
import argparse
import os

import numpy as np
from PIL import Image

ALPHA_MIN = 10


def gaps(vec: np.ndarray, min_width: int) -> list[tuple[int, int, int]]:
    """Return (start, end, width) for every zero-run at least min_width long."""
    out: list[tuple[int, int, int]] = []
    start = None
    for i, x in enumerate(vec):
        if x == 0 and start is None:
            start = i
        elif x > 0 and start is not None:
            if i - start >= min_width:
                out.append((start, i - 1, i - start))
            start = None
    if start is not None and len(vec) - start >= min_width:
        out.append((start, len(vec) - 1, len(vec) - start))
    return out


def content_box(sub: np.ndarray):
    ys, xs = np.where(sub)
    if len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--rows", type=int, default=2)
    ap.add_argument("--row-names", default="cannon,wing")
    ap.add_argument("--col-names", default="lv0,lv1,lv2")
    ap.add_argument(
        "--equal",
        action="store_true",
        help="split into equal cells instead of hunting blank bands. Required for "
        "sheets with a painted background (storyboards) — those have no transparent "
        "gutters, so the alpha projection finds nothing to cut on.",
    )
    args = ap.parse_args()

    row_names = args.row_names.split(",")
    col_names = args.col_names.split(",")
    if len(row_names) < args.rows or len(col_names) < args.cols:
        raise SystemExit("row-names / col-names shorter than rows / cols")

    os.makedirs(args.out, exist_ok=True)
    im = Image.open(args.src).convert("RGBA")
    alpha = np.array(im)[:, :, 3]
    h, w = alpha.shape
    mask = alpha > ALPHA_MIN
    print(f"sheet {w}x{h}  grid {args.rows}x{args.cols}")

    if args.equal:
        # Keep the full cell — a storyboard panel is the background too, so
        # trimming to the content box would be wrong here.
        for ri in range(args.rows):
            for ci in range(args.cols):
                box = (
                    round(w * ci / args.cols),
                    round(h * ri / args.rows),
                    round(w * (ci + 1) / args.cols),
                    round(h * (ri + 1) / args.rows),
                )
                tile = im.crop(box)
                name = f"{row_names[ri]}_{col_names[ci]}.png"
                tile.save(os.path.join(args.out, name))
                print(f"  {name}  {tile.size[0]}x{tile.size[1]}")
        return

    # Column cuts: the widest blank bands in the whole-sheet vertical projection.
    # A wing row has a gap between its left and right piece, so take only the
    # (cols - 1) widest bands rather than every band found.
    xb = [0, w]
    if args.cols > 1:
        col_gaps = [g for g in gaps(mask.sum(axis=0), 6) if w * 0.08 < g[0] and g[1] < w * 0.92]
        col_gaps.sort(key=lambda g: -g[2])
        cuts = sorted((g[0] + g[1]) // 2 for g in col_gaps[: args.cols - 1])
        if len(cuts) < args.cols - 1:
            raise SystemExit(f"found only {len(cuts)} column cuts, need {args.cols - 1}")
        xb = [0] + cuts + [w]
        print(f"  column cuts: {cuts}")

    for ci in range(args.cols):
        x0, x1 = xb[ci], xb[ci + 1]
        sub = mask[:, x0:x1]

        # Row cuts are found per column: lv2 ornaments (pendant chains) often
        # bridge the two rows, so a whole-sheet projection finds no blank band.
        yb = [0, h]
        if args.rows > 1:
            proj = sub.sum(axis=1)
            row_gaps = [g for g in gaps(proj, 4) if h * 0.12 < g[0] and g[1] < h * 0.92]
            row_gaps.sort(key=lambda g: -g[2])
            cuts = sorted((g[0] + g[1]) // 2 for g in row_gaps[: args.rows - 1])
            if len(cuts) < args.rows - 1:
                lo, hi = int(h * 0.40), int(h * 0.80)
                cuts = [lo + int(np.argmin(proj[lo:hi]))]
                print(f"  col {ci}: no blank band, cut at thinnest scanline y={cuts[0]}")
            yb = [0] + cuts + [h]

        for ri in range(args.rows):
            y0, y1 = yb[ri], yb[ri + 1]
            box = content_box(mask[y0:y1, x0:x1])
            if box is None:
                print(f"  {row_names[ri]}_{col_names[ci]}: EMPTY")
                continue
            bx0, by0, bx1, by1 = box
            tile = im.crop((x0 + bx0, y0 + by0, x0 + bx1, y0 + by1))
            name = f"{row_names[ri]}_{col_names[ci]}.png"
            tile.save(os.path.join(args.out, name))
            print(f"  {name}  {tile.size[0]}x{tile.size[1]}")


if __name__ == "__main__":
    main()
