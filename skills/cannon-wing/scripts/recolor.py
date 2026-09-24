"""Shift a hue band of a transparent PNG into a target hue.

The draw model has a persistent bias: particle VFX come out fluorescent
yellow-green no matter what the plan specifies. Fighting it in the prompt costs
attention that the model then takes away from sculpt detail (measured: adding
colour-enforcement wording flattened the render and broke background removal).
So recolour afterwards instead.

Safe because the bands rarely overlap — VFX land around hue 60-100 while gold
sits near 45 and the blues are past 180. Always eyeball the result.

Usage:
    python recolor.py <in.png> <out.png> [--from 55,105] [--to 38,52]
                      [--min-sat 0.15]
"""
import argparse

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--from", dest="src_band", default="55,105", help="source hue band, degrees")
    ap.add_argument("--to", dest="dst_band", default="38,52", help="target hue band, degrees")
    ap.add_argument("--min-sat", type=float, default=0.15, help="skip near-grey pixels")
    args = ap.parse_args()

    h0, h1 = (float(v) for v in args.src_band.split(","))
    t0, t1 = (float(v) for v in args.dst_band.split(","))

    im = Image.open(args.src).convert("RGBA")
    arr = np.array(im).astype(np.float32) / 255.0
    rgb, alpha = arr[:, :, :3], arr[:, :, 3]

    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    diff = mx - mn
    sat = np.where(mx > 0, diff / np.maximum(mx, 1e-6), 0.0)

    # hue in degrees
    hue = np.zeros_like(mx)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    nz = diff > 1e-6
    idx = nz & (mx == r)
    hue[idx] = (60 * ((g[idx] - b[idx]) / diff[idx])) % 360
    idx = nz & (mx == g)
    hue[idx] = 60 * ((b[idx] - r[idx]) / diff[idx]) + 120
    idx = nz & (mx == b)
    hue[idx] = 60 * ((r[idx] - g[idx]) / diff[idx]) + 240

    target = (hue >= h0) & (hue <= h1) & (sat >= args.min_sat) & (alpha > 0.02)
    n = int(target.sum())
    total = int((alpha > 0.02).sum())
    print(f"remapping {n} px ({n / max(total, 1) * 100:.1f}% of opaque area)")
    if n == 0:
        im.save(args.dst)
        return

    # linear remap of the band, preserving relative position within it
    pos = (hue[target] - h0) / max(h1 - h0, 1e-6)
    hue[target] = t0 + pos * (t1 - t0)

    # HSV -> RGB for the remapped pixels only
    v = mx[target]
    s = sat[target]
    hp = hue[target] / 60.0
    c = v * s
    x = c * (1 - np.abs(hp % 2 - 1))
    m = v - c
    sector = np.floor(hp).astype(int) % 6
    zeros = np.zeros_like(c)
    table = [
        (c, x, zeros),
        (x, c, zeros),
        (zeros, c, x),
        (zeros, x, c),
        (x, zeros, c),
        (c, zeros, x),
    ]
    rr = np.select([sector == i for i in range(6)], [t[0] for t in table])
    gg = np.select([sector == i for i in range(6)], [t[1] for t in table])
    bb = np.select([sector == i for i in range(6)], [t[2] for t in table])

    rgb[:, :, 0][target] = rr + m
    rgb[:, :, 1][target] = gg + m
    rgb[:, :, 2][target] = bb + m

    out = np.dstack([rgb, alpha])
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA").save(args.dst)
    print(f"saved {args.dst}")


if __name__ == "__main__":
    main()
