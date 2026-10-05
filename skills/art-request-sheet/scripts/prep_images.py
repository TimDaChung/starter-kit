"""Prepare reference images for pasting into the art request sheet.

- mp4 -> GIF (about 10 fps, 128 colors); also keeps a full-size GIF next to
  the source so the user has it in the Downloads folder
- every image is scaled down to fit inside 530x300 (the reference column is
  550px wide)
- output names are ASCII (r01.png, r07.gif, ...) taken from the leading
  number of each source file, because Chrome uploads choke on odd names

Write the output into the session scratchpad: Chrome's file_upload only
accepts files from there.

Files whose name contains "後補" or that you list in --skip are left out.

Usage:
  python prep_images.py <source_dir> <out_dir> [--skip 04 11]
Requires: pillow, imageio-ffmpeg (pip install pillow imageio-ffmpeg)
"""
import argparse
import os
import re
import sys

from PIL import Image, ImageSequence

LONG_PREFIX = '\\\\?\\'


def lp(path):
    """Prefix long Windows paths so open() works past the 260-char limit."""
    path = os.path.abspath(path)
    if os.name == 'nt' and len(path) >= 240 and not path.startswith(LONG_PREFIX):
        return LONG_PREFIX + path.replace('/', '\\')
    return path



MAX_W, MAX_H = 530, 300
IMG_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp')


def mp4_to_gif(src, dst, max_side=640):
    try:
        import imageio_ffmpeg
    except ImportError:
        sys.exit('imageio-ffmpeg is missing: pip install -r %USERPROFILE%\\starter-kit\\requirements.txt')
    reader = imageio_ffmpeg.read_frames(lp(src))
    meta = next(reader)
    w, h = meta['size']
    fps = meta['fps'] or 30
    step = max(1, round(fps / 10))
    frames = []
    for idx, raw in enumerate(reader):
        if idx % step:
            continue
        im = Image.frombytes('RGB', (w, h), raw)
        im.thumbnail((max_side, max_side))
        frames.append(im.convert('P', palette=Image.ADAPTIVE, colors=128))
    frames[0].save(lp(dst), save_all=True, append_images=frames[1:],
                   duration=int(1000 * step / fps), loop=0, optimize=True)


def fit(w, h):
    s = min(MAX_W / w, MAX_H / h, 1)
    return max(1, int(w * s)), max(1, int(h * s))


def shrink(src, dst):
    im = Image.open(lp(src))
    nw, nh = fit(*im.size)
    if src.lower().endswith('.gif') and getattr(im, 'n_frames', 1) > 1:
        frames, durs = [], []
        for fr in ImageSequence.Iterator(im):
            frames.append(fr.convert('RGB').resize((nw, nh), Image.LANCZOS)
                          .convert('P', palette=Image.ADAPTIVE, colors=128))
            durs.append(fr.info.get('duration', 100))
        frames[0].save(lp(dst), save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
    else:
        im.convert('RGB').resize((nw, nh), Image.LANCZOS).save(lp(dst))
    return nw, nh


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source_dir')
    ap.add_argument('out_dir')
    ap.add_argument('--skip', nargs='*', default=[], help='leading numbers to leave out, e.g. 04')
    args = ap.parse_args()
    os.makedirs(lp(args.out_dir), exist_ok=True)

    names = sorted(os.listdir(lp(args.source_dir)))
    # videos first, so their GIFs are picked up below
    for name in names:
        if name.lower().endswith('.mp4'):
            gif = os.path.splitext(name)[0] + '.gif'
            if gif not in names:
                mp4_to_gif(os.path.join(args.source_dir, name), os.path.join(args.source_dir, gif))
                print(f'converted {name} -> {gif}')
    for name in sorted(os.listdir(lp(args.source_dir))):
        if not name.lower().endswith(IMG_EXT):
            continue
        m = re.match(r'(\d+)', name)
        if not m or m.group(1) in args.skip or '後補' in name:
            print(f'skip     {name}')
            continue
        is_gif = name.lower().endswith('.gif')
        out = f'r{m.group(1)}.gif' if is_gif else f'r{m.group(1)}.png'
        size = shrink(os.path.join(args.source_dir, name), os.path.join(args.out_dir, out))
        kb = os.path.getsize(lp(os.path.join(args.out_dir, out))) // 1024
        print(f'{out:<9}<- {name}  {size[0]}x{size[1]}  {kb} KB')


if __name__ == '__main__':
    main()
