"""Find the art-share images for a 一部 monthly event plan and paste them into its slots.

Covers three page kinds (titles start with YYMM):
  神娃大活動   costume pair images, 10 headshots, VIP front + VIP headshot
  人物大活動   12 character images (01-k = male, 02-k = female); 吃碰特效 (mp4) is manual
  神裝禮包     pair image per pack, picked by the seq numbers written on the page

  python art_share_slots.py list  <url|id> [--json out.json] [--kind 神娃|人物|神裝] [--yymm 2611]
                                  [--avatar-dir DIR] [--headshot-dir DIR] [--char-dir DIR] [--share-root DIR]
        # read-only: resolve folders, map every slot to a file, compare with what is on the page
  python art_share_slots.py paste <url|id> [--replace] [--only KEY ...] [--confirm] (same folder options)
        # without --confirm: prints the plan and exits (dry run)
        # pastes "todo" slots; "differs" slots only with --replace; manual / missing slots are never touched

Folder rules (art share X:, falls back to Y:):
  ●Avatar魔鬼營\\YYYYMM_<name>(大活動)\\靜態平面        pairs N+M.jpg|png, 前背景\\去背_N_front*.png
  ●大頭貼與配件\\YYYYMM_<name>(大活動)                  N_01.png headshots (256x256)
  【神幣、鬥地主】\\人物系統(人物、場景、禮包)\\YYMM01_<中文月>月大活動\\去背用   01-k.png / 02-k.png
A folder is picked by its numeric prefix; zero or several candidates, or a folder whose name states another
month, stop the run with the candidate list (pass the folder explicitly with --*-dir after the PM picks).

Comparison: MD5 first, then pixels (white background, 64x64 grey mean abs diff <= SAME_DIFF); file names are
hints only. Statuses: todo / same / differs / missing_source / ambiguous / manual.
See ../references/image-slots.md section 七 for the slot rules and known pitfalls.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from notion_rest import Notion, find_token, image_block, open_page, page_id_from, plain  # noqa: E402

SHARE_DIRS = ("X:/grp.product.art.check", "Y:/grp.product.art.check")
AVATAR_ROOT = "●Avatar魔鬼營"
HEADSHOT_ROOT = "●大頭貼與配件"
CHAR_ROOT = "【神幣、鬥地主】/人物系統(人物、場景、禮包)"
IMG_EXT = (".jpg", ".jpeg", ".png")
SAME_DIFF = 1.0
CN_MONTH = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十", 11: "十一", 12: "十二"}
KINDS = {"神娃": "神娃大活動", "人物": "人物大活動", "神裝": "神裝禮包"}

# costume group -> pair index (avatar) / k (character); 儲值裝 was removed from avatar pages in 202607
AVATAR_PAIR = {"新手裝": 0, "一般裝1": 1, "一般裝2": 2, "BOSS裝1": 3, "BOSS裝2": 4}
CHAR_K = {"新手裝": 1, "一般裝1": 2, "一般裝2": 3, "儲值裝": 4, "BOSS裝1": 5, "BOSS裝2": 6}
HEADSHOT_OFFSET = {"新手裝": 0, "一般裝": 2, "BOSS裝": 6}
GROUP_RE = re.compile(r"(新手裝|一般裝\s*[12]|儲值裝|boss裝\s*[12])\s*-\s*(男|女)", re.I)


class StopForPM(SystemExit):
    """Raised when a folder cannot be picked safely; the message lists the candidates."""


@dataclass
class Slot:
    key: str                      # stable id, e.g. "圖示/新手裝", "大頭貼/3", "VIP前景"
    label: str                    # human description of the slot
    mode: str                     # "after" = image is the next sibling of anchor; "child" = first child of anchor
    anchor: str                   # block id of the paragraph / list item that owns the slot
    parent: str                   # parent block id of the anchor (used by mode "after")
    image_block: str | None = None
    image_url: str | None = None
    image_name: str | None = None
    source: str | None = None     # resolved file on the share
    candidates: list[str] = field(default_factory=list)
    status: str = ""
    diff: float | None = None
    note: str = ""


# ------------------------------------------------------------------ titles and folders
def parse_title(title: str) -> tuple[str, str]:
    """Return (kind, yymm) from a page title like 'YYMM神娃大活動-<主題>' (prefixes such as 【測試】 are ignored)."""
    m = re.search(r"(\d{4})\s*(神娃大活動|人物大活動|神裝禮包)", title)
    if not m:
        raise SystemExit(f"title does not look like a 一部 monthly event page: {title!r} (use --kind/--yymm)")
    return m.group(2), m.group(1)


def activity_name(title: str) -> str:
    m = re.search(r"大活動\s*-\s*(.+)$", title)
    return m.group(1).strip() if m else ""


def find_share_root(override: str | None = None) -> Path:
    for d in ([override] if override else SHARE_DIRS):
        p = Path(d)
        if p.is_dir():
            return p
    raise SystemExit(f"art share not reachable (tried {', '.join([override] if override else SHARE_DIRS)})")


def _month_in_name(name: str, char_style: bool) -> int | None:
    """Month a folder name claims, or None when the name does not state one."""
    if char_style:
        m = re.match(r"\d{6}_(.+?)月", name)
        if not m:
            return None
        rev = {v: k for k, v in CN_MONTH.items()}
        return rev.get(m.group(1))
    m = re.search(r"_(\d{1,2})月大活動", name)
    return int(m.group(1)) if m else None


def resolve_month_dir(root: Path, yymm: str, char_style: bool = False) -> tuple[Path, list[str]]:
    """Pick the month folder under root by prefix (YYYYMM_ for avatar/headshot, YYMM01_ for characters).

    Returns (folder, notes). Raises StopForPM with the candidates when the choice is not safe:
    no folder, several folders, or the only folder states another month in its name.
    """
    month = int(yymm[2:])
    prefix = f"{yymm}01_" if char_style else f"20{yymm}_"
    dirs = sorted(p for p in root.iterdir() if p.is_dir())
    if not char_style:
        dirs = [p for p in dirs if p.name.endswith("(大活動)")]
    hits = [p for p in dirs if p.name.startswith(prefix)]
    wrong = [p for p in hits if _month_in_name(p.name, char_style) not in (None, month)]
    good = [p for p in hits if p not in wrong]
    notes = [f"ignored {p.name}: name says another month than prefix {prefix}" for p in wrong]
    if len(good) == 1:
        return good[0], notes
    # folders whose name claims this month under a different prefix (prefix typo)
    named = [p for p in dirs if p not in hits and _month_in_name(p.name, char_style) == month
             and p.name[:4 if not char_style else 2] == (f"20{yymm[:2]}" if not char_style else yymm[:2])]
    cands = good or (wrong + named)
    why = "several folders" if len(good) > 1 else "no folder"
    lines = [f"[{root.name}] {why} for prefix {prefix}; the PM must pick one and pass it with --*-dir:"]
    lines += [f"  - {p}" for p in cands] or ["  (no candidates)"]
    if named and not good:
        lines.append("  note: candidates above state this month in their name but carry another prefix")
    raise StopForPM("\n".join(lines))


def pair_files(static_dir: Path) -> dict[int, Path]:
    """Map the first number of every 'N+M.ext' pair image to its path."""
    out: dict[int, Path] = {}
    for p in static_dir.iterdir():
        m = re.fullmatch(r"(\d{4,})\+(\d{4,})", p.stem)
        if m and p.suffix.lower() in IMG_EXT and int(m.group(2)) == int(m.group(1)) + 1:
            out[int(m.group(1))] = p
    return out


def base_number(static_dir: Path) -> tuple[int, list[str]]:
    """Smallest pair number in 靜態平面 (N); notes flag anything other than 5 consecutive pairs."""
    pairs = pair_files(static_dir)
    if not pairs:
        raise StopForPM(f"no 'N+M' pair images in {static_dir}; art not delivered yet or wrong folder")
    n = min(pairs)
    notes = []
    expect = [n + 2 * i for i in range(5)]
    if sorted(pairs) != expect:
        notes.append(f"pair numbers {sorted(pairs)} are not the expected 5 consecutive pairs {expect}")
    return n, notes


def find_file(folder: Path, stem: str) -> list[Path]:
    """Files named stem with any image extension (extensions are not consistent on the share)."""
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.is_file() and p.stem == stem and p.suffix.lower() in IMG_EXT)


def vip_front_files(static_dir: Path, num: int) -> list[Path]:
    """去背_<num>_front*.png in 前背景 (the art team also writes 'fonrt'); suffix 1/2 is not reliable."""
    folder = static_dir / "前背景"
    if not folder.is_dir():
        return []
    pat = re.compile(rf"去背_{num}_(front|fonrt)\d*", re.I)
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMG_EXT and pat.fullmatch(p.stem))


# ------------------------------------------------------------------ page tree -> slots
def fetch_tree(api: Notion, block_id: str, depth: int = 0, max_depth: int = 5) -> list[dict[str, Any]]:
    kids = api.children(block_id)
    for b in kids:
        if b.get("has_children") and depth < max_depth and b["type"] not in ("child_page", "child_database", "table"):
            b["children"] = fetch_tree(api, b["id"], depth + 1, max_depth)
    return kids


def btext(b: dict[str, Any]) -> str:
    v = b.get(b["type"], {})
    return plain(v.get("rich_text")) if isinstance(v, dict) else ""


def _img_info(b: dict[str, Any] | None) -> tuple[str | None, str | None, str | None]:
    if not b or b.get("type") != "image":
        return None, None, None
    v = b["image"]
    url = v.get("file", {}).get("url") or v.get("external", {}).get("url") or v.get("file_upload", {}).get("url")
    name = urllib.parse.unquote(url.split("?")[0].rsplit("/", 1)[-1]) if url else None
    return b["id"], url, name


def _first_child_image(b: dict[str, Any]) -> dict[str, Any] | None:
    for c in b.get("children", []):
        if c["type"] == "image":
            return c
    return None


def _norm_group(raw: str) -> str:
    return re.sub(r"\s+", "", raw).replace("boss", "BOSS").replace("Boss", "BOSS")


def find_slots(kind: str, tree: list[dict[str, Any]], page_id: str) -> tuple[list[Slot], list[str]]:
    """Walk the page tree in reading order and return the image slots of the given page kind.

    Pure function over the block dicts (as returned by the API, with 'children' filled in), so it can be
    tested with hand-made trees. Returns (slots, notes).
    """
    slots: list[Slot] = []
    notes: list[str] = []
    st: dict[str, Any] = {"section": "", "group": "", "gender": "", "removed": False,
                          "hs_group": "", "hs_idx": 0, "vip": "", "chipeng": False, "seqs": [], "pack": ""}

    def visit(blocks: list[dict[str, Any]], parent: str) -> None:
        for i, b in enumerate(blocks):
            t = b["type"]
            txt = btext(b)
            nxt = blocks[i + 1] if i + 1 < len(blocks) else None
            if t == "heading_1":
                st["section"] = ""
            elif t == "heading_2":
                st["section"] = ("costume" if "神娃" in txt or "人物" in txt else
                                 "headshot" if "大頭貼" in txt else
                                 "other" if "其他" in txt else
                                 "pack" if "神裝禮包" in txt else "")
                st["pack"] = txt.strip()
                st["seqs"] = []
                st["group"] = st["hs_group"] = st["vip"] = ""
                st["chipeng"] = False
            elif t == "heading_3":
                g = GROUP_RE.search(txt)
                if st["section"] == "costume" and g:
                    st["group"], st["gender"] = _norm_group(g.group(1)), g.group(2)
                    st["removed"] = "移除" in txt
                elif st["section"] == "headshot":
                    hg = _norm_group(re.sub(r"[(（].*", "", txt).strip())
                    st["hs_group"] = "" if ("移除" in txt or hg not in HEADSHOT_OFFSET) else hg
                    st["hs_idx"] = 0
                elif st["section"] == "other":
                    st["chipeng"] = "吃碰" in txt
                    st["vip"] = ""
            # ---- slots
            if kind in ("神娃大活動", "神裝禮包") and t == "paragraph" and txt.strip().startswith("圖示(男女共用)"):
                img = nxt if nxt and nxt["type"] == "image" else None
                if kind == "神娃大活動" and st["section"] == "costume":
                    if st["removed"] or st["group"] not in AVATAR_PAIR:
                        notes.append(f"skipped 圖示 slot of {st['group'] or '?'} (removed or unknown group)")
                    else:
                        s = Slot(f"圖示/{st['group']}", f"1.神娃 {st['group']} 圖示(男女共用)", "after", b["id"], parent)
                        s.image_block, s.image_url, s.image_name = _img_info(img)
                        slots.append(s)
                elif kind == "神裝禮包" and st["section"] == "pack":
                    s = Slot(f"圖示/{st['pack']}", f"{st['pack']} 圖示(男女共用)", "after", b["id"], parent)
                    s.image_block, s.image_url, s.image_name = _img_info(img)
                    seqs = sorted(set(st["seqs"]))
                    s.note = "seq " + "+".join(map(str, seqs)) if seqs else "no seq on page"
                    slots.append(s)
            if t == "numbered_list_item" and kind == "神裝禮包":
                m = re.match(r"\s*seq\s*[:：]\s*(\d+)", txt, re.I)
                if m:
                    st["seqs"].append(int(m.group(1)))
            if t == "numbered_list_item" and kind == "神娃大活動":
                if st["section"] == "headshot" and txt.strip().startswith("圖片") and st["hs_group"]:
                    idx = HEADSHOT_OFFSET[st["hs_group"]] + st["hs_idx"]
                    st["hs_idx"] += 1
                    s = Slot(f"大頭貼/{idx}", f"2.大頭貼 {st['hs_group']} 第{st['hs_idx']}格", "child", b["id"], parent)
                    s.image_block, s.image_url, s.image_name = _img_info(_first_child_image(b))
                    slots.append(s)
                elif st["section"] == "other":
                    if txt.strip().startswith("VIP前景"):
                        st["vip"] = "VIP前景"
                    elif txt.strip().startswith("VIP頭貼"):
                        st["vip"] = "VIP頭貼"
                    elif txt.strip().startswith("圖片") and st["vip"]:
                        s = Slot(st["vip"], f"3.其他內容 {st['vip']}", "child", b["id"], parent)
                        s.image_block, s.image_url, s.image_name = _img_info(_first_child_image(b))
                        slots.append(s)
            if t == "numbered_list_item" and kind == "人物大活動":
                if st["section"] == "costume" and txt.strip().startswith("圖示") and st["group"] in CHAR_K:
                    sex = "01" if st["gender"] == "男" else "02"
                    s = Slot(f"圖示/{st['group']}-{st['gender']}", f"1.人物 {st['group']}-{st['gender']} 圖示",
                             "child", b["id"], parent)
                    s.image_block, s.image_url, s.image_name = _img_info(_first_child_image(b))
                    s.note = f"{sex}-{CHAR_K[st['group']]}"
                    slots.append(s)
                elif st["section"] == "other" and st["chipeng"] and txt.strip().startswith("圖示"):
                    s = Slot("吃碰特效", "2.其他 吃碰特效 圖示", "child", b["id"], parent)
                    s.image_block, s.image_url, s.image_name = _img_info(_first_child_image(b))
                    slots.append(s)
            if b.get("children") and t not in ("table",):
                visit(b["children"], b["id"])

    visit(tree, page_id)
    return slots, notes


# ------------------------------------------------------------------ slot -> source file
@dataclass
class Dirs:
    static: Path | None = None    # avatar 靜態平面
    headshot: Path | None = None
    char: Path | None = None      # character 去背用
    char_month: Path | None = None
    base: int | None = None


def assign_sources(kind: str, slots: list[Slot], dirs: Dirs) -> None:
    """Fill slot.source / candidates / status (missing_source, ambiguous, manual) from the folder rules."""
    for s in slots:
        files: list[Path] = []
        if kind == "神娃大活動" and dirs.base is not None and dirs.static:
            n = dirs.base
            if s.key.startswith("圖示/"):
                i = AVATAR_PAIR[s.key.split("/", 1)[1]]
                files = find_file(dirs.static, f"{n + 2 * i}+{n + 2 * i + 1}")
            elif s.key.startswith("大頭貼/"):
                files = find_file(dirs.headshot, f"{n + int(s.key.split('/')[1])}_01") if dirs.headshot else []
            elif s.key == "VIP前景":
                files = vip_front_files(dirs.static, n + 1)
            elif s.key == "VIP頭貼":
                files = find_file(dirs.headshot, f"{n + 1}_01") if dirs.headshot else []
        elif kind == "神裝禮包" and dirs.static:
            seqs = [int(x) for x in re.findall(r"\d+", s.note)]
            if len(seqs) == 2 and seqs[1] == seqs[0] + 1:
                files = find_file(dirs.static, f"{seqs[0]}+{seqs[1]}")
            else:
                s.status, s.note = "ambiguous", f"{s.note}: expected two consecutive seq numbers"
                continue
        elif kind == "人物大活動":
            if s.key == "吃碰特效":
                folder = dirs.char_month / "吃碰特效" if dirs.char_month else None
                s.candidates = [str(p) for p in sorted(folder.iterdir())] if folder and folder.is_dir() else []
                s.status, s.note = "manual", "source is mp4: pick a frame by hand"
                continue
            if dirs.char:
                files = find_file(dirs.char, s.note)
        s.candidates = [str(p) for p in files]
        if len(files) == 1:
            s.source = str(files[0])
        elif not files:
            s.status = "missing_source"
        else:
            s.status = "ambiguous"


# ------------------------------------------------------------------ comparison
def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def pixel_diff(a: bytes, b: bytes) -> float:
    """0 = identical pixels; otherwise mean abs grey difference on a 64x64 thumbnail (white background)."""
    from PIL import Image

    def load(x: bytes) -> Image.Image:
        im = Image.open(io.BytesIO(x)).convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        return bg.convert("RGB")

    ia, ib = load(a), load(b)
    if ia.size == ib.size and ia.tobytes() == ib.tobytes():
        return 0.0
    ga = ia.convert("L").resize((64, 64))
    gb = ib.convert("L").resize((64, 64))
    pa, pb = ga.tobytes(), gb.tobytes()
    return sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)


def compare_bytes(page: bytes, share: bytes) -> tuple[bool, float]:
    if _md5(page) == _md5(share):
        return True, 0.0
    d = pixel_diff(page, share)
    return d <= SAME_DIFF, round(d, 2)


def download(url: str, tries: int = 3) -> bytes:
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except OSError:
            if attempt == tries - 1:
                raise
    raise RuntimeError("unreachable")


def classify(slots: list[Slot]) -> None:
    for s in slots:
        if s.status:  # manual / ambiguous / missing_source already set
            if s.status == "missing_source" and s.image_block:
                s.note = (s.note + "; " if s.note else "") + "page has an image but the share has no file"
            continue
        if not s.image_block:
            s.status = "todo"
            continue
        if not s.image_url:
            s.status, s.note = "differs", "page image has no readable url"
            continue
        same, d = compare_bytes(download(s.image_url), Path(s.source).read_bytes())
        s.status, s.diff = ("same" if same else "differs"), d


# ------------------------------------------------------------------ orchestration
STATUS_TEXT = {"todo": "空格待貼", "same": "已貼且相同", "differs": "已貼但網芳不同", "missing_source": "網芳缺檔",
               "ambiguous": "需確認(多個候選)", "manual": "需人工"}


def resolve_dirs(kind: str, yymm: str, a: argparse.Namespace) -> tuple[Dirs, list[str]]:
    notes: list[str] = []
    dirs = Dirs()

    def root() -> Path:
        return find_share_root(a.share_root)

    if kind in ("神娃大活動", "神裝禮包"):
        if a.avatar_dir:
            month = Path(a.avatar_dir)
        else:
            month, n = resolve_month_dir(root() / AVATAR_ROOT, yymm)
            notes += n
        dirs.static = month / "靜態平面" if (month / "靜態平面").is_dir() else month
        notes.append(f"avatar: {dirs.static}")
    if kind == "神娃大活動":
        if a.headshot_dir:
            dirs.headshot = Path(a.headshot_dir)
        else:
            dirs.headshot, n = resolve_month_dir(root() / HEADSHOT_ROOT, yymm)
            notes += n
        notes.append(f"headshot: {dirs.headshot}")
        dirs.base, n = base_number(dirs.static)
        notes += n + [f"base number N = {dirs.base}"]
    if kind == "人物大活動":
        if a.char_dir:
            dirs.char_month = Path(a.char_dir)
        else:
            dirs.char_month, n = resolve_month_dir(root() / CHAR_ROOT, yymm, char_style=True)
            notes += n
        dirs.char = dirs.char_month / "去背用"
        notes.append(f"character: {dirs.char}")
    return dirs, notes


def build_plan(a: argparse.Namespace) -> tuple[Notion, str, str, list[Slot], list[str]]:
    pid = page_id_from(a.page)
    api, page = open_page(pid)
    title = "".join(x.get("plain_text", "") for v in page["properties"].values() if v["type"] == "title" for x in v["title"])
    kind, yymm = (KINDS[a.kind], a.yymm) if a.kind and a.yymm else parse_title(title)
    dirs, notes = resolve_dirs(kind, yymm, a)
    act = activity_name(title)
    if kind == "神娃大活動" and act and dirs.static and act not in str(dirs.static) and f"{int(yymm[2:])}月大活動" not in str(dirs.static):
        notes.append(f"folder name differs from the plan's activity name {act!r}: check it is the right month")
    tree = fetch_tree(api, pid)
    slots, n2 = find_slots(kind, tree, pid)
    assign_sources(kind, slots, dirs)
    classify(slots)
    return api, title, kind, slots, notes + n2


def print_plan(title: str, kind: str, slots: list[Slot], notes: list[str]) -> None:
    print(f"# {title}  ({kind})")
    for n in notes:
        print(f"  - {n}")
    print("\n| slot | status | page image | share file | note |\n|---|---|---|---|---|")
    for s in slots:
        src = Path(s.source).name if s.source else (", ".join(Path(c).name for c in s.candidates) or "-")
        extra = s.note + (f" diff={s.diff}" if s.diff else "")
        print(f"| {s.key} | {STATUS_TEXT.get(s.status, s.status)} | {s.image_name or '-'} | {src} | {extra} |")
    counts: dict[str, int] = {}
    for s in slots:
        counts[s.status] = counts.get(s.status, 0) + 1
    print("\n# " + "  ".join(f"{STATUS_TEXT.get(k, k)}={v}" for k, v in counts.items()))


def cmd_list(a: argparse.Namespace) -> list[Slot]:
    _, title, kind, slots, notes = build_plan(a)
    print_plan(title, kind, slots, notes)
    if a.json:
        Path(a.json).write_text(json.dumps({"title": title, "kind": kind, "notes": notes,
                                            "slots": [asdict(s) for s in slots]}, ensure_ascii=False, indent=1),
                                encoding="utf-8")
        print(f"json: {a.json}")
    return slots


def cmd_paste(a: argparse.Namespace) -> None:
    api_read, title, kind, slots, notes = build_plan(a)
    print_plan(title, kind, slots, notes)
    want = {"todo"} | ({"differs"} if a.replace else set())
    todo = [s for s in slots if s.status in want and s.source and (not a.only or s.key in a.only)]
    if not todo:
        print("\nnothing to paste")
        return
    print("\nplan:")
    for s in todo:
        print(f"  {'REPLACE' if s.status == 'differs' else 'INSERT '} {s.key} <- {s.source}")
    if not a.confirm:
        print("\ndry run: add --confirm after the PM approves the list above")
        return
    api = Notion(find_token(line="神幣"))
    for s in todo:
        fid = api.upload_file(s.source)
        if s.status == "differs":
            api.replace_image(s.image_block, fid)
        elif s.mode == "after":
            api.append(s.parent, [image_block(fid)], after=s.anchor)
        else:
            api.append(s.anchor, [image_block(fid)])
        print(f"  done {s.key}")
    # read back: every touched slot must now hold the share file
    _, _, _, after, _ = build_plan(a)
    by_key = {s.key: s for s in after}
    bad = [s.key for s in todo if by_key.get(s.key) is None or by_key[s.key].status != "same"]
    print(f"\nverify: {len(todo) - len(bad)}/{len(todo)} slots now match the share" + (f"; FAILED {bad}" if bad else ""))
    if bad:
        raise SystemExit(1)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "paste"):
        s = sub.add_parser(name)
        s.add_argument("page")
        s.add_argument("--kind", choices=list(KINDS))
        s.add_argument("--yymm")
        s.add_argument("--share-root")
        s.add_argument("--avatar-dir", help="avatar month folder (the one holding 靜態平面)")
        s.add_argument("--headshot-dir")
        s.add_argument("--char-dir", help="character month folder (the one holding 去背用)")
        if name == "list":
            s.add_argument("--json")
        else:
            s.add_argument("--replace", action="store_true")
            s.add_argument("--only", action="append")
            s.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    try:
        {"list": cmd_list, "paste": cmd_paste}[a.cmd](a)
    except StopForPM as e:
        print(f"STOP: {e}")
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
