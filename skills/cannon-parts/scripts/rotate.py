"""Rotate a part sheet 90 degrees.

Why this exists: asking the model to draw a bullet-impact ring "lying on its
side, facing right" warps it — the round frame gets stretched into an ellipse.
So the sheet is generated in the orientation the model draws best (bullet
pointing up, rings face-on and perfectly circular) and rotated afterwards.

Default is clockwise, which maps the generated layout to the delivery layout:

    generated                 delivered
    [ring A] [ring B]         [      ] [ring A]
         [bullet ↑]     -->   [bullet→] [ring B]

Usage:
    python rotate.py <in.png> <out.png> [--ccw]
"""
import argparse

from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--ccw", action="store_true", help="counter-clockwise instead")
    args = ap.parse_args()

    im = Image.open(args.src)
    # PIL's ROTATE_90 is counter-clockwise, so clockwise is ROTATE_270.
    mode = Image.Transpose.ROTATE_90 if args.ccw else Image.Transpose.ROTATE_270
    out = im.transpose(mode)
    out.save(args.dst)
    direction = "counter-clockwise" if args.ccw else "clockwise"
    print(f"rotated {direction}: {im.size} -> {out.size}  saved {args.dst}")


if __name__ == "__main__":
    main()
