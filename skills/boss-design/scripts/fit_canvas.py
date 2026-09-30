"""Place a generated boss onto an exact 16:9 gray canvas at a fixed screen size.

The draw engine neither returns a reliable 16:9 (1536x1024 and 1672x941 both
happen) nor honours "body height = 55% of the screen" (a test run gave 90% and
64% from the same prompt). Both are guaranteed here instead of in the prompt.

Usage:
    python fit_canvas.py <in.png> <out.png> [--height 0.55] [--max-width 0.5]
                         [--width 1920] [--gray auto|R,G,B] [--threshold 28]

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


def place(src: Image.Image, args: argparse.Namespace) -> tuple[Image.Image, list[str]]:
    rgb = src.convert("RGB")
    gray = corner_gray(rgb) if args.gray == "auto" else tuple(int(v) for v in args.gray.split(","))
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
    args = parser.parse_args()
    out, notes = place(Image.open(args.src), args)
    out.save(args.dst)
    print(f"{args.dst}: {out.size[0]}x{out.size[1]}")
    for note in notes:
        print(f"  {note}")


if __name__ == "__main__":
    main()
