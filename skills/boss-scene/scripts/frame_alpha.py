"""Turn a fishing-ground edge frame (decorations on a gray center) into an overlay PNG.

The engine paints the frame's empty center as flat-ish gray. This script makes
that gray transparent (feathered, so crystal glows fade instead of clipping),
and optionally composites the result onto a base fishing-ground image to
preview how the overlay reads in game.

Usage:
    python frame_alpha.py <frame.png> <out_overlay.png> [--preview <base.png> <out_preview.png>]
                          [--width 1920] [--low 8] [--high 36]

Background gray is sampled from the image center (the frame's corners are
decorated, so corner sampling would be wrong). Pixels within --low of that gray
become fully transparent, beyond --high fully opaque, linear in between.
Prints the opaque share of the center 70% region: a high value means the model
put decorations in the fish area and the frame should be regenerated.
"""
import argparse

from PIL import Image, ImageChops, ImageFilter


def center_gray(img: Image.Image) -> tuple[int, int, int]:
    w, h = img.size
    patch = img.crop((w // 2 - 20, h // 2 - 20, w // 2 + 20, h // 2 + 20)).resize((1, 1), Image.BOX)
    return patch.getpixel((0, 0))


def alpha_mask(img: Image.Image, gray: tuple[int, int, int], low: int, high: int) -> Image.Image:
    diff = ImageChops.difference(img, Image.new("RGB", img.size, gray)).convert("L")
    span = max(high - low, 1)
    ramp = diff.point(lambda v: 0 if v <= low else 255 if v >= high else (v - low) * 255 // span)
    return ramp.filter(ImageFilter.GaussianBlur(1.5))


def center_coverage(mask: Image.Image, share: float = 0.7) -> float:
    w, h = mask.size
    mx, my = round(w * (1 - share) / 2), round(h * (1 - share) / 2)
    region = mask.crop((mx, my, w - mx, h - my))
    hist = region.histogram()
    opaque = sum(hist[128:])
    return opaque / (region.width * region.height)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    parser.add_argument("--preview", nargs=2, metavar=("BASE", "OUT"))
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--low", type=int, default=8)
    parser.add_argument("--high", type=int, default=36)
    args = parser.parse_args()

    height = round(args.width * 9 / 16)
    rgb = Image.open(args.src).convert("RGB").resize((args.width, height), Image.LANCZOS)
    gray = center_gray(rgb)
    mask = alpha_mask(rgb, gray, args.low, args.high)
    overlay = rgb.copy()
    overlay.putalpha(mask)
    overlay.save(args.dst)
    coverage = center_coverage(mask)
    print(f"{args.dst}: {args.width}x{height} RGBA, center gray {gray}")
    print(f"  center 70% region opaque: {coverage:.1%}")
    if coverage > 0.05:
        print("  WARNING decorations intrude into the fish area: regenerate")

    if args.preview:
        base_path, out_path = args.preview
        base = Image.open(base_path).convert("RGBA").resize((args.width, height), Image.LANCZOS)
        base.alpha_composite(overlay)
        base.convert("RGB").save(out_path)
        print(f"  preview: {out_path}")


if __name__ == "__main__":
    main()
