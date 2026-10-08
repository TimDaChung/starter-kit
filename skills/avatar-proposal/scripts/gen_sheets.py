"""Generate one design sheet (male left, female right) per group with image-studio.

  python gen_sheets.py proposal.json --out DIR [--ref-dir DIR] [--only 01_newbie,05_boss1] [--dry-run]

Rules baked in (see SKILL.md 前科表):
  * ONE job at a time, never in parallel (5 parallel jobs -> 1/10 images survived).
  * count=1 per group (Tim 2026-10-02).
  * reference = the Sept-2026 production sheet of the same tier, read from the art share.
  * the 人物更衣室 background is drawn too (key 07_dressing_room, Leo 2026-10-08: art needs a picture to confirm);
    its reference is the last slide image of the Sept-2026 人物設定 pptx on the art share.
Prompt template lives here (TEMPLATE / TIER_TEXT); prompt模板.md documents it, change both together.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CLIENT = Path.home() / ".claude/skills/image-studio/scripts/image-studio-client.py"
REF_SUBDIR = r"grp.product.art.check\●Avatar魔鬼營\202609_天魔混世記(大活動)\靜態平面"
REF_BY_KEY = {"01_newbie": "4266+4267.jpg", "02_normal1": "4268+4269.jpg", "03_normal2": "4270+4271.jpg",
              "04_topup": "4268+4269.jpg", "05_boss1": "4272+4273.jpg", "06_boss2": "4274+4275.jpg"}

TEMPLATE = (
    "Game avatar design sheet for a mobile mahjong game. Follow the reference image EXACTLY for layout, proportions and rendering: "
    "one wide landscape image, flat warm grey-brown background (#6b5e58), two tall rounded-rectangle panels side by side with a thin dark outline, "
    "LEFT panel = male character, RIGHT panel = female character. Each character is a chibi about 3 heads tall, full body, standing, facing the viewer, "
    "big expressive eyes, clean cel-shaded Taiwanese mobile-game style with crisp bold outlines, flat bright saturated colors, simple shapes, "
    "few small details (do NOT over-decorate; keep patterns large and simple like the reference). "
    "Do NOT copy the costumes, theme or colors of the reference; only its format and style. No text, no numbers, no logos, no watermark.\n"
    "Theme of this month: {theme_en}.\n"
    "Avoid (hard rules): {avoid}\n"
)
DEFAULT_AVOID = ("religious items (shrines, torii gates, stone lanterns, prayer beads, crosses, talismans, taiji, Buddhist beads), "
                 "torn or ragged clothing, books, clocks, snakes, green hats on men, heavy armor or huge weapons on women, "
                 "grim or gloomy mood, exposed cleavage or thighs.")

TIER_TEXT = {
    "新手": "STRENGTH TIER: NEWBIE (lowest). Both characters are simple and plain: few accessories, no patterns, NO weapon, NO glowing effects, NO wings, "
          "no background scene (both panels keep the plain grey-brown background).",
    "一般": "STRENGTH TIER: NORMAL (middle). Moderate detail only. Each character has EITHER one weapon OR one glowing effect, never both. No wings.",
    "儲值": "STRENGTH TIER: PREMIUM (static, between normal and boss). Ornate costume with gold trim, a weapon, NO glowing effects, wings optional. "
          "No background scene (both panels keep the plain grey-brown background).",
    "BOSS": "STRENGTH TIER: BOSS (highest). Both characters are the most elaborate: ornate costume with gold trim and gems, a weapon AND glowing effects, large and showy.",
}
DRESSING_KEY = "07_dressing_room"
DRESSING_PPTX = r"grp.product.art.check\●Avatar魔鬼營\202609_天魔混世記(大活動)\2609_大活動_人物設定.pptx"
DRESSING_TEMPLATE = (
    "Background art for the avatar dressing room screen of a mobile mahjong game. Follow the reference image for format and rendering: "
    "one wide landscape scene (3:2), symmetrical one-point perspective, a raised round stage in the centre with a few steps in front "
    "where the player's avatar will stand, an empty floor in the lower half, decorative scenery on both sides framing the stage, "
    "clean cel-shaded vector-like game art with bold outlines and bright saturated colours. NO characters, NO people, NO creatures in the "
    "foreground, no text, no logos, no watermark. Do NOT copy the reference's theme or colours; only its layout and style.\n"
    "Theme of this month: {theme_en}.\n"
    "Scene: {scene}\n"
    "Avoid (hard rules): {avoid}\n"
)
PANEL_BG = " The {side} panel keeps the plain grey-brown background."
CORNER_EN = {"左上": "TOP-LEFT", "右上": "TOP-RIGHT", "左下": "BOTTOM-LEFT", "右下": "BOTTOM-RIGHT"}


def tier_key(tier):
    return "BOSS" if tier.upper().startswith("BOSS") else ("一般" if tier.startswith("一般") else tier)


def group_prompt(p, g):
    parts = [TEMPLATE.format(theme_en=p["theme_en"], avoid=p.get("avoid_en", DEFAULT_AVOID)), TIER_TEXT[tier_key(g["tier"])]]
    fg = g.get("foregrounds", [])
    bg = g.get("background")
    for side, gender, key in (("LEFT", "male", "male"), ("RIGHT", "female", "female")):
        c = g[key]
        parts.append(f"\n{side} {gender}: {c['prompt_en']} Main colors: {c.get('main_color_en', c['main_color'])}.")
        scenes = [s for s in fg if s.get("owner", "male") == key]
        for s in scenes:
            parts.append(f"Foreground item for the {side} panel, placed floating in the {CORNER_EN.get(s.get('corner'), 'TOP-RIGHT')} corner of the panel, "
                         f"small and not covering the character: {s['prompt_en']}")
        if bg and bg.get("owner", "female") == key:
            parts.append(f"The {side} panel has a FULL-BLEED background scene filling the whole panel behind the character: {bg['prompt_en']}")
        elif not scenes or not bg:
            parts.append(PANEL_BG.format(side=side).strip())
    return "\n".join(parts)


def dressing_prompt(p):
    dr = p["dressing_room"]
    return DRESSING_TEMPLATE.format(theme_en=p["theme_en"], scene=dr["prompt_en"], avoid=p.get("avoid_en", DEFAULT_AVOID))


def dressing_ref(ref_dir, out_dir):
    """Extract the Sept dressing-room image from the pptx (last slide, first picture) into out_dir."""
    if ref_dir:
        cand = Path(ref_dir) / "dressing_room.jpg"
        return cand if cand.exists() else None
    for drive in ("X:", "Y:"):
        src = Path(f"{drive}\\{DRESSING_PPTX}")
        try:
            if not src.exists():
                continue
            from pptx import Presentation
            slide = Presentation(str(src)).slides[-1]
            pic = next(sh for sh in slide.shapes if sh.shape_type == 13)
            dst = Path(out_dir) / f"_ref_dressing_room.{pic.image.ext}"
            dst.write_bytes(pic.image.blob)
            return dst
        except (OSError, StopIteration, ImportError):
            pass
    return None


def find_ref(ref_dir, key):
    name = REF_BY_KEY.get(key)
    if not name:
        return None
    if ref_dir:
        cand = Path(ref_dir) / name
        return cand if cand.exists() else None
    for drive in ("X:", "Y:"):
        cand = Path(f"{drive}\\{REF_SUBDIR}\\{name}")
        try:
            if cand.exists():
                return cand
        except OSError:
            pass
    return None


def run_one(prompt_file, ref, out_dir, timeout=1200):
    cmd = [sys.executable, str(CLIENT), "draw", "--count", "1", "--prompt-file", str(prompt_file), "--output", str(out_dir), "--timeout", str(timeout)]
    if ref:
        cmd += ["--reference", str(ref)]
    env = dict(os.environ, PYTHONUTF8="1")
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr)[-600:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("proposal")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref-dir")
    ap.add_argument("--only")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retry", type=int, default=1)
    a = ap.parse_args()
    p = json.loads(Path(a.proposal).read_text(encoding="utf-8"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
    jobs = []  # (key, prompt, ref, final file); run strictly one after another
    for g in p["groups"]:
        if not only or g["key"] in only:
            jobs.append((g["key"], group_prompt(p, g), find_ref(a.ref_dir, g["key"]),
                         out / f"{g['key']}_{g['tier']}_{g['male']['persona']}+{g['female']['persona']}.png"))
    if p.get("dressing_room") and (not only or DRESSING_KEY in only):
        if p["dressing_room"].get("prompt_en"):
            jobs.append((DRESSING_KEY, dressing_prompt(p), dressing_ref(a.ref_dir, out), out / f"{DRESSING_KEY}_人物更衣室.png"))
        else:
            print(f"WARNING: dressing_room has no prompt_en; {DRESSING_KEY} skipped")
    results = []
    for key, prompt, ref, final in jobs:
        gdir = out / key
        gdir.mkdir(exist_ok=True)
        prompt_file = gdir / "prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        print(f"== {key} ref={ref.name if ref else 'NONE'} -> {final.name}")
        if a.dry_run:
            continue
        if not ref:
            print("   WARNING: no reference sheet found (art share not reachable?) — continuing without")
        ok = False
        for attempt in range(1 + a.retry):
            before = set(gdir.glob("*.png"))
            code, tail = run_one(prompt_file, ref, gdir)
            new = sorted(set(gdir.glob("*.png")) - before, key=lambda x: x.stat().st_mtime)
            if code == 0 and new:
                shutil.copy(new[-1], final)
                print(f"   ok -> {final.name}")
                ok = True
                break
            print(f"   attempt {attempt + 1} failed (exit {code}): {tail.strip()[-200:]}")
            time.sleep(5)
        results.append((key, ok))
    print("\nsummary:", ", ".join(f"{k}:{'ok' if v else 'FAIL'}" for k, v in results))


if __name__ == "__main__":
    main()
