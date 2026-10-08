"""Place a generated boss onto an exact 16:9 gray canvas at a fixed screen size.

The draw engine neither returns a reliable 16:9 (1536x1024 and 1672x941 both
happen) nor honours "body height = 55% of the screen" (a test run gave 90% and
64% from the same prompt). Both are guaranteed here instead of in the prompt.

Usage:
    python fit_canvas.py <in.png> <out.png> [--height 0.55] [--max-width 0.5]
                         [--width 1920] [--gray auto|R,G,B] [--threshold 28]
    python fit_canvas.py <in.png> <out.png> --transparent
                         [--key-low 10] [--key-high 40] [--feather 1] [--margin 0]

Steps:
1. Background gray = average of the four corner pixels (--gray auto), so the
   new canvas matches the gray the engine painted and no seam shows.
2. Subject bounding box = pixels whose color differs from that gray by more
   than --threshold (max channel delta). Soft glows below the threshold are
   treated as background.
3. The subject is scaled so its box height is --height of the canvas height,
   shrunk further if its width would exceed --max-width of the canvas width,
   then centered.
4. It is composited through a feathered mask (not pasted as a rectangle): the
   engine's gray is never perfectly flat, so a hard rectangle leaves a visible
   frame around the subject.

--whole: skip steps 2-3 and fit the entire source image into the canvas
(for capture-performance frames, where effects fill the frame and a subject
box is meaningless).
--cover: center-crop the source to 16:9 and scale to fill (for full-bleed
scenes such as boss-scene backgrounds; no gray bars).
--transparent: key out the gray instead of placing on a canvas. Output is an
RGBA PNG cropped to the subject box (plus --margin), at source resolution, no
16:9 and no scaling. For demos, decks and cut-ins that need the boss alone.
  1. background gray = corner average (same as above)
  2. alpha = max channel delta from that gray, ramped from --key-low (fully
     transparent) to --key-high (fully opaque)
  3. MinFilter(3) erodes one pixel so the gray fringe is not kept, then a
     GaussianBlur(--feather) softens the edge
  4. edge colors are un-mixed from the gray (color = (pixel - (1-a)*gray) / a),
     so half-transparent edges and soft shadows do not carry a gray halo
  5. crop to the bounding box of alpha > 8, padded by --margin pixels
  Known limit: parts of the subject whose color is close to the background gray
  (gray armour, white-gray smoke) become see-through, and a neutral drop
  shadow is kept as a gray patch (it differs from the gray as much as the
  subject does). Check on a dark and a light background before use.

Prints the source and final screen ratios so the caller can verify, and warns
when the subject had to be upscaled (loses detail; regenerate larger instead).
"""
import argparse

from PIL import Image, ImageChops, ImageFilter


def corner_gray(img: Image.Image) -> tuple[int, int, int]:
    w, h = img.size
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]
    px = [img.getpixel(p) for p in pts]
    return tuple(sum(c[i] for c in px) // len(px) for i in range(3))


def subject_box(img: Image.Image, gray: tuple[int, int, int], threshold: int) -> tuple[int, int, int, int]:
    diff = ImageChops.difference(img, Image.new("RGB", img.size, gray))
    mask = diff.convert("L").point(lambda v: 255 if v > threshold else 0)
    box = mask.getbbox()
    if box is None:
        raise SystemExit("no subject found: image is uniform gray")
    return box


def feather_mask(img: Image.Image, gray: tuple[int, int, int], radius: float) -> Image.Image:
    diff = ImageChops.difference(img, Image.new("RGB", img.size, gray)).convert("L")
    # ramp: delta <= 6 is pure background, delta >= 30 is fully subject
    ramp = diff.point(lambda v: 0 if v <= 6 else 255 if v >= 30 else (v - 6) * 255 // 24)
    return ramp.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))


def fit_whole(rgb: Image.Image, gray: tuple[int, int, int], canvas_w: int) -> tuple[Image.Image, list[str]]:
    canvas_h = round(canvas_w * 9 / 16)
    scale = min(canvas_w / rgb.width, canvas_h / rgb.height)
    resized = rgb.resize((round(rgb.width * scale), round(rgb.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (canvas_w, canvas_h), gray)
    canvas.paste(resized, ((canvas_w - resized.width) // 2, (canvas_h - resized.height) // 2))
    return canvas, [f"whole image fitted, padded {canvas_w - resized.width}px x {canvas_h - resized.height}px"]


def fit_cover(rgb: Image.Image, canvas_w: int) -> tuple[Image.Image, list[str]]:
    canvas_h = round(canvas_w * 9 / 16)
    ratio = canvas_w / canvas_h
    if rgb.width / rgb.height > ratio:
        crop_w = round(rgb.height * ratio)
        left = (rgb.width - crop_w) // 2
        box = (left, 0, left + crop_w, rgb.height)
    else:
        crop_h = round(rgb.width / ratio)
        top = (rgb.height - crop_h) // 2
        box = (0, top, rgb.width, top + crop_h)
    cropped = rgb.crop(box)
    note = f"cover: cropped {rgb.width - cropped.width}px x {rgb.height - cropped.height}px from the source"
    return cropped.resize((canvas_w, canvas_h), Image.LANCZOS), [note]


def key_alpha(rgb: Image.Image, gray: tuple[int, int, int], low: int, high: int, feather: float) -> Image.Image:
    """Alpha from the max per-channel distance to the background gray."""
    r, g, b = ImageChops.difference(rgb, Image.new("RGB", rgb.size, gray)).split()
    delta = ImageChops.lighter(ImageChops.lighter(r, g), b)
    span = max(high - low, 1)
    alpha = delta.point(lambda v: 0 if v <= low else 255 if v >= high else (v - low) * 255 // span)
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    if feather > 0:
        alpha = alpha.filter(ImageFilter.GaussianBlur(feather))
    return alpha


def unmix_gray(rgb: Image.Image, alpha: Image.Image, gray: tuple[int, int, int]) -> Image.Image:
    """Remove the gray contribution from partially transparent pixels."""
    import numpy as np  # only the --transparent path needs numpy

    p = np.asarray(rgb, dtype=np.float32)
    a = np.asarray(alpha, dtype=np.float32)[..., None] / 255.0
    g = np.array(gray, dtype=np.float32)
    out = (p - (1.0 - a) * g) / np.maximum(a, 1e-3)
    out = np.where(a > 0, out, p)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def fit_transparent(rgb: Image.Image, gray: tuple[int, int, int], args: argparse.Namespace) -> tuple[Image.Image, list[str]]:
    alpha = key_alpha(rgb, gray, args.key_low, args.key_high, args.feather)
    box = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    if box is None:
        raise SystemExit("no subject found: image is uniform gray")
    left, top, right, bottom = box
    m = args.margin
    crop = (max(left - m, 0), max(top - m, 0), min(right + m, rgb.width), min(bottom + m, rgb.height))
    rgba = unmix_gray(rgb, alpha, gray)
    rgba.putalpha(alpha)
    out = rgba.crop(crop)
    notes = [
        f"background gray {gray}, key {args.key_low}-{args.key_high}, feather {args.feather}",
        f"cropped to {out.width}x{out.height} (subject box {right - left}x{bottom - top}, margin {m}px)",
    ]
    if left <= 1 or top <= 1 or right >= rgb.width - 1 or bottom >= rgb.height - 1:
        notes.append("WARNING subject touches the source frame edge: it may be cut off, check or regenerate")
    return out, notes


def place(src: Image.Image, args: argparse.Namespace) -> tuple[Image.Image, list[str]]:
    rgb = src.convert("RGB")
    gray = corner_gray(rgb) if args.gray == "auto" else tuple(int(v) for v in args.gray.split(","))
    if args.transparent:
        return fit_transparent(rgb, gray, args)
    if args.cover:
        return fit_cover(rgb, args.width)
    if args.whole:
        return fit_whole(rgb, gray, args.width)
    left, top, right, bottom = subject_box(rgb, gray, args.threshold)
    pad = 12  # keep soft glow just outside the threshold box
    subject = rgb.crop((max(left - pad, 0), max(top - pad, 0), min(right + pad, rgb.width), min(bottom + pad, rgb.height)))
    sw, sh = subject.size
    canvas_w = args.width
    canvas_h = round(canvas_w * 9 / 16)
    scale = min(canvas_h * args.height / sh, canvas_w * args.max_width / sw)
    resized = subject.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (canvas_w, canvas_h), gray)
    offset = ((canvas_w - resized.width) // 2, (canvas_h - resized.height) // 2)
    canvas.paste(resized, offset, feather_mask(resized, gray, radius=2))
    notes = [
        f"source subject: {sh / rgb.height:.0%} of height, {sw / rgb.width:.0%} of width",
        f"placed subject: {resized.height / canvas_h:.0%} of height, {resized.width / canvas_w:.0%} of width",
    ]
    if left <= 1 or top <= 1 or right >= rgb.width - 1 or bottom >= rgb.height - 1:
        notes.append("WARNING subject touches the source frame edge: it may be cut off, check or regenerate")
    if scale > 1:
        notes.append(f"WARNING upscaled x{scale:.2f}: detail is lost, prefer a larger generation")
    return canvas, notes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    parser.add_argument("--height", type=float, default=0.55, help="subject height / canvas height")
    parser.add_argument("--max-width", type=float, default=0.5, help="cap: subject width / canvas width")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--gray", default="auto")
    parser.add_argument("--threshold", type=int, default=28)
    parser.add_argument("--whole", action="store_true", help="fit the whole image, no subject scaling")
    parser.add_argument("--cover", action="store_true", help="crop to fill 16:9, for full-bleed scenes")
    parser.add_argument("--transparent", action="store_true",
                        help="key out the gray, crop to the subject, save RGBA PNG (no canvas, no scaling)")
    parser.add_argument("--key-low", type=int, default=10,
                        help="--transparent: max channel delta at or below which a pixel is fully transparent")
    parser.add_argument("--key-high", type=int, default=40,
                        help="--transparent: max channel delta at or above which a pixel is fully opaque")
    parser.add_argument("--feather", type=float, default=1.0, help="--transparent: edge blur radius in px")
    parser.add_argument("--margin", type=int, default=0, help="--transparent: px kept around the subject box")
    args = parser.parse_args()
    if args.transparent and not args.dst.lower().endswith(".png"):
        parser.error("--transparent needs a .png output (alpha channel)")
    out, notes = place(Image.open(args.src), args)
    out.save(args.dst)
    print(f"{args.dst}: {out.size[0]}x{out.size[1]}")
    for note in notes:
        print(f"  {note}")


if __name__ == "__main__":
    main()
