"""Cut a transparent sprite/asset sheet from image-studio into one PNG per cell.

Used when several small assets of the same style were drawn on ONE sheet
(N columns x M rows, generated with --remove-background) to save hourly quota.

Objects often spill over their own cell (a pot's feet crossing into the next
row), so the sheet is NOT cut along fixed grid lines. Instead every connected
opaque blob on the whole sheet is assigned to the cell that contains its
centre of mass, and each cell is cropped to the union of its blobs. Spill-over
stays with its owner and does not leak into the neighbour as a fragment.

Usage:
    python sheet_cut.py <sheet.png> <out_dir> --cols 4 --rows 2
                        [--last-row 2] [--names a,b,c,...] [--pad 8]
                        [--min-blob 0.002]

  --last-row   number of cells in the bottom row when it is not full
               (e.g. 4 on top + 2 below: --cols 4 --rows 2 --last-row 2;
               the short row is treated as evenly spread across the width)
  --names      file names in reading order (left->right, top->bottom)
  --min-blob   blobs smaller than this fraction of one cell are dropped as noise

Outputs <out_dir>/<name>.png for every cell, plus <out_dir>/_check_dark.png:
every cut on a dark background with its name, for a visual check of stray
fragments and clipped edges. Look at the check image before using the cuts.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ALPHA_MIN = 10
SCALE = 4  # labelling runs on a 1/SCALE mask for speed; crops use full resolution


def label_blobs(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """4-connected component labelling with union-find (numpy only, no scipy)."""
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    parent = [0]

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    nxt = 1
    for y in range(h):
        row = mask[y]
        for x in range(w):
            if not row[x]:
                continue
            up = labels[y - 1, x] if y else 0
            left = labels[y, x - 1] if x else 0
            if up and left:
                a, b = find(up), find(left)
                labels[y, x] = min(a, b)
                if a != b:
                    parent[max(a, b)] = min(a, b)
            elif up or left:
                labels[y, x] = find(up or left)
            else:
                parent.append(nxt)
                labels[y, x] = nxt
                nxt += 1
    roots = np.array([find(i) for i in range(nxt)], dtype=np.int32)
    labels = roots[labels]
    uniq = np.unique(labels[labels > 0])
    remap = np.zeros(nxt, dtype=np.int32)
    remap[uniq] = np.arange(1, len(uniq) + 1)
    return remap[labels], len(uniq)


def cell_boxes(w: int, h: int, cols: int, rows: int, last_row: int) -> list[tuple[float, float, float, float]]:
    boxes = []
    ch = h / rows
    for r in range(rows):
        n = last_row if (r == rows - 1 and last_row) else cols
        cw = w / n
        for c in range(n):
            boxes.append((c * cw, r * ch, (c + 1) * cw, (r + 1) * ch))
    return boxes


def cut(sheet_path: Path, out_dir: Path, cols: int, rows: int, last_row: int,
        names: list[str], pad: int, min_blob: float) -> list[Path]:
    sheet = Image.open(sheet_path).convert("RGBA")
    w, h = sheet.size
    alpha = np.asarray(sheet)[..., 3]
    if alpha.min() > ALPHA_MIN:
        raise SystemExit("sheet has no transparency - generate it with --remove-background")

    small = Image.fromarray(alpha).resize((max(1, w // SCALE), max(1, h // SCALE)), Image.Resampling.BOX)
    mask = np.asarray(small) > ALPHA_MIN
    labels, count = label_blobs(mask)
    # full-resolution label map (edge pixels beyond the last whole SCALE block reuse the last block)
    labels_full = np.repeat(np.repeat(labels, SCALE, axis=0), SCALE, axis=1)
    labels_full = np.pad(labels_full, ((0, max(0, h - labels_full.shape[0])), (0, max(0, w - labels_full.shape[1]))),
                         mode="edge")[:h, :w]

    boxes = cell_boxes(w, h, cols, rows, last_row)
    if names and len(names) != len(boxes):
        raise SystemExit(f"--names has {len(names)} entries but the sheet has {len(boxes)} cells")
    names = names or [f"cell_{i + 1:02d}" for i in range(len(boxes))]
    min_px = min_blob * (w / cols) * (h / rows) / (SCALE * SCALE)

    owned: list[list[tuple[int, int, int, int]]] = [[] for _ in boxes]
    for lab in range(1, count + 1):
        ys, xs = np.nonzero(labels == lab)
        if len(xs) < min_px:
            continue
        cx, cy = xs.mean() * SCALE, ys.mean() * SCALE
        for i, (x0, y0, x1, y1) in enumerate(boxes):
            if x0 <= cx < x1 and y0 <= cy < y1:
                owned[i].append((xs.min() * SCALE, ys.min() * SCALE, (xs.max() + 1) * SCALE, (ys.max() + 1) * SCALE))
                break

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    tiles: list[tuple[str, Image.Image | None]] = []
    for name, blobs in zip(names, owned):
        if not blobs:
            print(f"warning: cell '{name}' is empty")
            tiles.append((name, None))
            continue
        x0 = max(0, min(b[0] for b in blobs) - pad)
        y0 = max(0, min(b[1] for b in blobs) - pad)
        x1 = min(w, max(b[2] for b in blobs) + pad)
        y1 = min(h, max(b[3] for b in blobs) + pad)
        crop = sheet.crop((x0, y0, x1, y1))
        # keep only this cell's blobs: clear pixels that belong to other owners' blobs
        mine = set()
        for b in blobs:
            sub = labels[b[1] // SCALE:b[3] // SCALE, b[0] // SCALE:b[2] // SCALE]
            vals, cnts = np.unique(sub[sub > 0], return_counts=True)
            if len(vals):
                mine.add(int(vals[np.argmax(cnts)]))
        keep = np.isin(labels_full[y0:y1, x0:x1], list(mine))
        # dilate the keep mask a little so anti-aliased edges survive
        keep_img = Image.fromarray(keep.astype(np.uint8) * 255).filter(
            ImageFilter.MaxFilter(2 * SCALE + 1))
        arr = np.asarray(crop).copy()
        arr[..., 3] = np.where(np.asarray(keep_img) > 0, arr[..., 3], 0)
        tile = Image.fromarray(arr, "RGBA")
        bbox = tile.getchannel("A").point(lambda v: 255 if v > ALPHA_MIN else 0).getbbox()
        if bbox:
            bx0, by0, bx1, by1 = bbox
            tile = tile.crop((max(0, bx0 - pad), max(0, by0 - pad),
                              min(tile.width, bx1 + pad), min(tile.height, by1 + pad)))
        path = out_dir / f"{name}.png"
        tile.save(path)
        written.append(path)
        tiles.append((name, tile))

    write_check(tiles, out_dir / "_check_dark.png")
    return written


def write_check(tiles: list[tuple[str, Image.Image | None]], path: Path) -> None:
    cell = 260
    per_row = min(4, max(1, len(tiles)))
    rows = (len(tiles) + per_row - 1) // per_row
    canvas = Image.new("RGB", (per_row * cell, rows * (cell + 28)), (40, 40, 48))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 18)
    except OSError:
        font = ImageFont.load_default()
    for i, (name, tile) in enumerate(tiles):
        gx, gy = (i % per_row) * cell, (i // per_row) * (cell + 28)
        draw.text((gx + 8, gy + cell + 4), name, fill=(230, 230, 230), font=font)
        if tile is None:
            draw.text((gx + cell // 2 - 30, gy + cell // 2 - 10), "(empty)", fill=(255, 120, 120), font=font)
            continue
        t = tile.copy()
        t.thumbnail((cell - 16, cell - 16))
        canvas.paste(t, (gx + (cell - t.width) // 2, gy + (cell - t.height) // 2), t)
    canvas.save(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--cols", type=int, required=True)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--last-row", type=int, default=0)
    parser.add_argument("--names", default="")
    parser.add_argument("--pad", type=int, default=8)
    parser.add_argument("--min-blob", type=float, default=0.002)
    args = parser.parse_args()
    names = [n.strip() for n in args.names.split(",") if n.strip()]
    written = cut(args.sheet, args.out_dir, args.cols, args.rows, args.last_row, names, args.pad, args.min_blob)
    print(f"{len(written)} cuts -> {args.out_dir} (check {args.out_dir / '_check_dark.png'} before use)")


if __name__ == "__main__":
    main()
