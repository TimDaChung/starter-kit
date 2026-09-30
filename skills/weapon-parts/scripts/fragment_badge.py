"""Compose a weapon "fragment" icon: paste a fragment badge onto a weapon icon's corner.

The plan (武具系統 §2.7) defines the fragment icon as "the weapon icon with a
fragment mark added at the top-left, same logic as cannon-wing fragments". That
is a composite, not a new drawing, so it is done here: every weapon gets the
same badge at the same size and position.

Usage:
    python fragment_badge.py <icon.png> <badge.png> [out.png]
                             [--scale 0.35] [--corner top-left] [--margin 0.04]

--scale   badge side as a fraction of the icon side (the badge keeps its aspect
          ratio and is fitted inside that square)
--corner  top-left | top-right | bottom-left | bottom-right
--margin  inset from the two nearest edges, as a fraction of the icon side

The badge should be a transparent PNG (remove its background first). The icon
may be opaque. Output defaults to <icon stem>_fragment.png next to the icon.
"""
import argparse
import pathlib

from PIL import Image

CORNERS = ("top-left", "top-right", "bottom-left", "bottom-right")


def fit_badge(badge: Image.Image, box: int) -> Image.Image:
    """Scale the badge to fit inside a box x box square, keeping its aspect ratio."""
    ratio = min(box / badge.width, box / badge.height)
    size = (max(1, round(badge.width * ratio)), max(1, round(badge.height * ratio)))
    return badge.resize(size, Image.LANCZOS)


def corner_offset(icon_size: tuple[int, int], badge_size: tuple[int, int], corner: str, margin: int) -> tuple[int, int]:
    """Top-left paste position for the badge in the requested corner."""
    iw, ih = icon_size
    bw, bh = badge_size
    x = margin if corner.endswith("left") else iw - bw - margin
    y = margin if corner.startswith("top") else ih - bh - margin
    return x, y


def compose(icon: Image.Image, badge: Image.Image, scale: float, corner: str, margin: float) -> Image.Image:
    icon = icon.convert("RGBA")
    badge = badge.convert("RGBA")
    side = min(icon.size)
    if icon.width != icon.height:
        print(f"warning: icon is {icon.width}x{icon.height}, not square; scale uses the shorter side")
    fitted = fit_badge(badge, round(side * scale))
    pos = corner_offset(icon.size, fitted.size, corner, round(side * margin))
    out = icon.copy()
    out.alpha_composite(fitted, dest=pos)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("icon")
    parser.add_argument("badge")
    parser.add_argument("out", nargs="?")
    parser.add_argument("--scale", type=float, default=0.35, help="badge side / icon side")
    parser.add_argument("--corner", choices=CORNERS, default="top-left")
    parser.add_argument("--margin", type=float, default=0.04, help="inset / icon side")
    args = parser.parse_args()

    if not 0 < args.scale <= 1:
        raise SystemExit(f"--scale must be in (0, 1], got {args.scale}")
    if not 0 <= args.margin < 0.5:
        raise SystemExit(f"--margin must be in [0, 0.5), got {args.margin}")

    icon_path = pathlib.Path(args.icon)
    out_path = pathlib.Path(args.out) if args.out else icon_path.with_name(f"{icon_path.stem}_fragment.png")
    result = compose(Image.open(icon_path), Image.open(args.badge), args.scale, args.corner, args.margin)
    result.save(out_path)
    print(f"{out_path}: {result.width}x{result.height}, badge {round(args.scale * 100)}% at {args.corner}")


if __name__ == "__main__":
    main()
