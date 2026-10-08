"""Derived page assets for the 人物設定 page (Leo's layout, 2026-10-08), plus proposal lints.

  * color_chip(main_color)   -> PNG bytes of the small swatch shown under 主色 (one cell per colour word)
  * crop_halves(sheet)       -> (male PNG bytes, female PNG bytes): the design sheet cut down the middle
  * lint(proposal)           -> list of warnings: male/female colour-family overlap, 特效 without 實體/虛體

python sheet_assets.py lint  proposal.json
python sheet_assets.py chips proposal.json --out DIR     # write every chip, for a visual check
"""
import argparse
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# colour word -> (hex, family). Families drive the overlap lint; black/white/grey are neutral.
COLORS = {
    "黑": ("#1a1a1a", "黑"), "灰": ("#8a8a8a", "灰"), "黑灰": ("#3a3a3a", "黑"), "白": ("#ffffff", "白"), "月白": ("#e6edf5", "白"),
    "銀": ("#c4c7cf", "白"), "金": ("#e0a800", "金"), "金黃": ("#f2c200", "金"), "黃": ("#f5d000", "黃"),
    "紅": ("#c00000", "紅"), "赤": ("#b3261e", "紅"), "火紅": ("#e03000", "紅"), "酒紅": ("#7a1022", "紅"), "朱": ("#e0401a", "紅"),
    "粉": ("#f4a6c0", "粉"), "桃": ("#f07aa0", "粉"), "橙": ("#f08a00", "橙"), "橘": ("#f08a00", "橙"),
    "棕": ("#8b5a2b", "棕"), "淺棕": ("#b9895a", "棕"), "咖啡": ("#6b4226", "棕"), "米": ("#efe2c4", "棕"),
    "綠": ("#2e8b57", "綠"), "墨綠": ("#1f4d36", "綠"), "翠": ("#1fa060", "綠"), "藍綠": ("#138a8a", "青"), "青": ("#1e90b0", "青"),
    "青藍": ("#1f6fb5", "藍"), "藍": ("#1f4fbf", "藍"), "淺藍": ("#8cc8f0", "藍"), "天藍": ("#5cb0f0", "藍"), "藏青": ("#1f2a5c", "藍"),
    "深藍": ("#16246e", "藍"), "紫": ("#7b3fa0", "紫"), "藍紫": ("#5a4fcf", "紫"), "淺紫": ("#b49ad8", "紫"), "淡紫": ("#b49ad8", "紫"),
}
NEUTRAL = {"黑", "白", "灰"}
CHIP_W, CHIP_H = 92, 42  # same size as the chips on Leo's page
FONTS = [r"C:\Windows\Fonts\msjhbd.ttc", r"C:\Windows\Fonts\msjh.ttc"]


def color_words(main_color: str) -> list[str]:
    """'紫 / 黑白' -> ['紫', '黑', '白'] (longest dictionary match per token)."""
    out = []
    for token in re.split(r"[/／、,，\s]+", main_color.strip()):
        while token:
            hit = next((token[:n] for n in range(len(token), 0, -1) if token[:n] in COLORS), None)
            out.append(hit or token)
            token = token[len(hit):] if hit else ""
    return [w for w in out if w]


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for f in FONTS:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def color_chip(main_color: str) -> bytes:
    words = color_words(main_color)
    img = Image.new("RGB", (CHIP_W, CHIP_H), "#999999")
    d = ImageDraw.Draw(img)
    inner_w = CHIP_W - 2
    font = _font(15)
    for i, w in enumerate(words):
        x0 = 1 + inner_w * i // len(words)
        x1 = 1 + inner_w * (i + 1) // len(words)
        hexv = COLORS.get(w, ("#9e9e9e", "?"))[0]
        d.rectangle([x0, 1, x1 - 1, CHIP_H - 2], fill=hexv)
        r, g, b = (int(hexv[k:k + 2], 16) for k in (1, 3, 5))
        ink = "#000000" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"
        tw = d.textlength(w, font=font)
        d.text(((x0 + x1 - tw) / 2, (CHIP_H - 17) / 2), w, fill=ink, font=font)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def crop_halves(sheet: str | Path) -> tuple[bytes, bytes]:
    """The sheet is two panels side by side (male left, female right): cut at the middle."""
    img = Image.open(sheet).convert("RGB")
    w, h = img.size
    out = []
    for box in ((0, 0, w // 2, h), (w - w // 2, 0, w, h)):
        buf = io.BytesIO()
        img.crop(box).save(buf, "PNG")
        out.append(buf.getvalue())
    return out[0], out[1]


def _families(main_color: str) -> list[str]:
    seen = []
    for w in color_words(main_color):
        fam = COLORS.get(w, (None, w))[1]
        if fam not in seen:
            seen.append(fam)
    return seen


def lint(p: dict) -> list[str]:
    warns = []
    for key, label in (("male", "男"), ("female", "女")):
        sets = [(g["tier"], _families(g[key]["main_color"])) for g in p["groups"]]
        unknown = {w for g in p["groups"] for w in color_words(g[key]["main_color"]) if w not in COLORS}
        if unknown:
            warns.append(f"[色票] {label}裝有色詞不在對照表（色塊會是灰色）：{'、'.join(sorted(unknown))}，到 sheet_assets.COLORS 補")
        count = Counter(f for _, fams in sets for f in fams if f not in NEUTRAL)
        for fam, n in count.items():
            if n >= 3:
                tiers = [t for t, fams in sets if fam in fams]
                warns.append(f"[配色重疊] {label}裝「{fam}」系出現在 {n} 套（{'、'.join(tiers)}），同色系最多兩套")
        firsts = Counter(fams[0] for _, fams in sets if fams)
        for fam, n in firsts.items():
            if n >= 2:
                tiers = [t for t, fams in sets if fams and fams[0] == fam]
                warns.append(f"[配色重疊] {label}裝第一主色同為「{fam}」系：{'、'.join(tiers)}")
    for g in p["groups"]:
        for key, label in (("male", "男"), ("female", "女")):
            c = g[key]
            fx = [r for r in c.get("requirements", []) if r.startswith("特效")]
            for r in fx:
                if "實體" not in r[:8] and "虛體" not in r[:8]:
                    warns.append(f"[特效] {g['tier']}{label}｜{c['persona']}：「{r[:20]}…」沒標實體／虛體，寫成「特效（實體）：…」或「特效（虛體）：…」")
    return warns


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["lint", "chips"])
    ap.add_argument("proposal")
    ap.add_argument("--out")
    a = ap.parse_args()
    p = json.loads(Path(a.proposal).read_text(encoding="utf-8"))
    if a.mode == "lint":
        warns = lint(p)
        print("\n".join(warns) if warns else "OK: no lint warnings")
        return
    out = Path(a.out or ".")
    out.mkdir(parents=True, exist_ok=True)
    for g in p["groups"]:
        for key in ("male", "female"):
            (out / f"{g['key']}_{key}_color.png").write_bytes(color_chip(g[key]["main_color"]))
    print(f"chips -> {out}")


if __name__ == "__main__":
    main()
