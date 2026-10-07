"""Prepare reference images for pasting into the art request sheet.

- mp4 -> GIF with ffmpeg palettegen / paletteuse: only the first 10 s, about
  6 fps, 360 px wide (about 2 MB). The GIF is kept next to the source so the
  user has it in the Downloads folder. A GIF over 9 MB gets a warning:
  Chrome's file_upload refuses more than 10 MB in one go.
- every image is scaled down to fit the thumbnail box of the column it is
  pasted into. Boxes come from scripts/layouts/<layout>.json (column
  "thumb": [w, h], else width - 20 by 300); dept1 is 530x300.
  With --spec, each file gets the box of the column the spec puts it in
  (the tightest one if it is used in several); files not in the spec, or no
  --spec, get the smallest box of the layout.
- output names are ASCII (r01.png, r07.gif, ...) taken from the leading
  number of each source file, because Chrome uploads choke on odd names

Write the output into the session scratchpad: Chrome's file_upload only
accepts files from there. Then pass the same folder to
build_sheet.py --images so row heights match the real image sizes.

Files whose name contains "後補" or that you list in --skip are left out.

Usage:
  python prep_images.py <source_dir> <out_dir> [--layout dept4-slot] [--spec spec.json]
                        [--skip 04 11] [--gif-seconds 10] [--gif-fps 6] [--gif-width 360]
Requires: pillow, imageio-ffmpeg (pip install pillow imageio-ffmpeg)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageSequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_sheet import Box, DEFAULT_LAYOUT, file_boxes, fit_size, layout_min_box, load_layout, lp, thumb_box  # noqa: E402

IMG_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
GIF_SECONDS = 10.0
GIF_FPS = 6
GIF_WIDTH = 360
GIF_WARN_MB = 9.0


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
    except ImportError:
        sys.exit('imageio-ffmpeg is missing: pip install -r %USERPROFILE%\\starter-kit\\requirements.txt')
    return imageio_ffmpeg.get_ffmpeg_exe()


def video_duration(src: str) -> float | None:
    """Duration in seconds from the container header (no full decode)."""
    import imageio_ffmpeg
    reader = imageio_ffmpeg.read_frames(lp(src))
    try:
        meta = next(reader)
    finally:
        reader.close()
    return meta.get('duration') or None


def mp4_to_gif(src: str, dst: str, seconds: float = GIF_SECONDS, fps: int = GIF_FPS,
               width: int = GIF_WIDTH, warn_mb: float = GIF_WARN_MB) -> int:
    """Convert the first `seconds` of a video (0 = all) to a palette GIF; return its size in bytes."""
    exe = ffmpeg_exe()
    total = video_duration(src) or seconds
    target = min(total, seconds) if seconds > 0 else total
    vf = (f'fps={fps},scale={width}:-2:flags=lanczos,split[a][b];'
          f'[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4')
    cmd = [exe, '-y', '-hide_banner', '-loglevel', 'error', '-nostats', '-progress', 'pipe:1']
    if seconds > 0:
        cmd += ['-t', f'{seconds:g}']
    cmd += ['-i', lp(src), '-vf', vf, '-loop', '0', lp(dst)]
    name = os.path.basename(src)
    print(f'gif      {name}: first {target:.1f}s of {total:.1f}s, {fps} fps, {width}px wide', flush=True)
    started = last_print = time.monotonic()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            encoding='utf-8', errors='replace')
    assert proc.stdout is not None and proc.stderr is not None
    for line in proc.stdout:
        key, _, value = line.strip().partition('=')
        if key == 'out_time_us' and value.isdigit() and time.monotonic() - last_print >= 2:
            done = int(value) / 1e6
            print(f'         ... {done:.1f}/{target:.1f}s ({min(100.0, done / target * 100):.0f}%)', flush=True)
            last_print = time.monotonic()
    err = proc.stderr.read()
    if proc.wait() != 0:
        sys.exit(f'ffmpeg failed on {name}: {err.strip()[-500:]}')
    size = os.path.getsize(lp(dst))
    print(f'         done in {time.monotonic() - started:.1f}s, {size / 1048576:.2f} MB', flush=True)
    if size > warn_mb * 1048576:
        print(f'warning: {os.path.basename(dst)} is {size / 1048576:.1f} MB (> {warn_mb:g} MB); '
              f'Chrome file_upload takes 10 MB per call. Lower --gif-seconds / --gif-fps / --gif-width',
              flush=True)
    return size


def shrink(src: str, dst: str, box: Box) -> Box:
    """Scale an image (animated GIFs frame by frame) to fit inside box; return the new size."""
    with Image.open(lp(src)) as im:
        nw, nh = fit_size(*im.size, box)
        animated = src.lower().endswith('.gif') and getattr(im, 'n_frames', 1) > 1
        if animated and (nw, nh) == im.size:
            pass  # already small enough: copy as is, re-quantizing would only cost quality
        elif animated:
            frames, durs = [], []
            for fr in ImageSequence.Iterator(im):
                frames.append(fr.convert('RGB').resize((nw, nh), Image.LANCZOS)
                              .convert('P', palette=Image.ADAPTIVE, colors=128))
                durs.append(fr.info.get('duration', 100))
            frames[0].save(lp(dst), save_all=True, append_images=frames[1:], duration=durs, loop=0,
                           optimize=True)
            return nw, nh
        else:
            im.convert('RGB').resize((nw, nh), Image.LANCZOS).save(lp(dst))
            return nw, nh
    shutil.copyfile(lp(src), lp(dst))
    return nw, nh


def main() -> None:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source_dir')
    ap.add_argument('out_dir')
    ap.add_argument('--layout', default=None,
                    help=f"layout name or .json path (default: the spec's layout, else {DEFAULT_LAYOUT})")
    ap.add_argument('--spec', help='build_sheet spec; sizes each file for the column it is pasted into')
    ap.add_argument('--skip', nargs='*', default=[], help='leading numbers to leave out, e.g. 04')
    ap.add_argument('--gif-seconds', type=float, default=GIF_SECONDS, help='seconds of video kept (0 = all)')
    ap.add_argument('--gif-fps', type=int, default=GIF_FPS)
    ap.add_argument('--gif-width', type=int, default=GIF_WIDTH)
    args = ap.parse_args()
    os.makedirs(lp(args.out_dir), exist_ok=True)

    spec = None
    if args.spec:
        with open(lp(args.spec), encoding='utf-8') as fh:
            spec = json.load(fh)
    layout = load_layout(args.layout or (spec or {}).get('layout', DEFAULT_LAYOUT))
    boxes = file_boxes(spec, layout) if spec else {}
    default_box = layout_min_box(layout)
    print(f"layout {layout['name']}: default box {default_box[0]}x{default_box[1]}, "
          f'{len(boxes)} files sized from the spec', flush=True)
    if spec is None and len({thumb_box(c) for t in layout['tabs'] for c in t['columns']
                             if c['kind'] in ('image', 'ref')}) > 1:
        print('warning: this layout has image columns of different widths; pass --spec so each '
              'image is sized for its own column instead of the smallest one', flush=True)

    names = sorted(os.listdir(lp(args.source_dir)))
    # videos first, so their GIFs are picked up below
    for name in names:
        if name.lower().endswith('.mp4'):
            gif = os.path.splitext(name)[0] + '.gif'
            gif_path = os.path.join(args.source_dir, gif)
            # an oversized GIF left by an older version of this script is redone
            if gif not in names or os.path.getsize(lp(gif_path)) > GIF_WARN_MB * 1048576:
                mp4_to_gif(os.path.join(args.source_dir, name), gif_path, args.gif_seconds, args.gif_fps, args.gif_width)
    for name in sorted(os.listdir(lp(args.source_dir))):
        if not name.lower().endswith(IMG_EXT):
            continue
        m = re.match(r'(\d+)', name)
        if not m or m.group(1) in args.skip or '後補' in name:
            print(f'skip     {name}', flush=True)
            continue
        is_gif = name.lower().endswith('.gif')
        out = f'r{m.group(1)}.gif' if is_gif else f'r{m.group(1)}.png'
        box = boxes.get(out, default_box)
        size = shrink(os.path.join(args.source_dir, name), os.path.join(args.out_dir, out), box)
        kb = os.path.getsize(lp(os.path.join(args.out_dir, out))) // 1024
        print(f'{out:<9}<- {name}  {size[0]}x{size[1]} (box {box[0]}x{box[1]})  {kb} KB', flush=True)


if __name__ == '__main__':
    main()
