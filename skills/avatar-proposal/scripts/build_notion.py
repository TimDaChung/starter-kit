"""Build the 神娃＋人物設定 Notion page (Leo's per-character layout, 2026-10-08) from proposal.json.

  python build_notion.py preview proposal.json                       # no API: print what would be built
  python build_notion.py fill    proposal.json --page <page_id>   [--sheets DIR]   # DEFAULT in the SOP
        # user made the page from the Notion template and gave us the URL; content is inserted right before
        # the template's 調整紀錄 heading (table of contents / adjustment-log skeleton untouched), sheets uploaded inline
  python build_notion.py swap    proposal.json --page <page_id>   [--sheets DIR]
        # sheets were redrawn: replace crops / dressing room in place, matched by uploaded file name
        # (<month>_<key>_<male|female>.png) or by a template caption 示意圖｜<tier>｜<男|女> / 示意圖｜更衣室
  python build_notion.py new     proposal.json [--parent <page_id>] [--sheets DIR] [--title T]
        # default parent: 活動資料庫 row with 活動類型=人物設定; title <month>人物設定-<theme>
        # only when the user explicitly asks us to create the page ourselves

Sheets: one PNG per group, matched by group "key" prefix (e.g. 01_newbie*.png) inside --sheets; cut into male/female
halves on upload. Dressing room: 07_dressing_room*.png.
Credential: the 一部 (pm1) Notion proxy credential, see notion_api.find_token and
plan-dept14-writer/references/notion-access.md. Writes still need the user's go-ahead first.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from notion_api import (Notion, bullet, callout, column_list, divider, find_token, heading, image_block, para, plain, table)  # noqa: E402
from sheet_assets import color_chip, crop_halves, lint  # noqa: E402

DRESSING_KEY = "07_dressing_room"

ALL_PARTS = ["五官", "臉型", "服飾", "髮型", "髮飾", "眼鏡", "鬍子", "裝飾", "耳環", "武器", "特效", "翅膀"]
# ✅ = make it; — = allowed, not this time; ❌ = never (the tier's spec forbids it, or the system has no such part)
YES, NO, NEVER = "✅", "—", "❌"
GENDER_KEY = {"男": "male", "女": "female"}


def tier_base(tier):
    """Return (old, new) default marks for a tier, as Leo laid them out on the 2612 page (2026-10-08)."""
    t = "BOSS" if tier.upper().startswith("BOSS") else ("一般" if tier.startswith("一般") else tier)
    core = {p: YES for p in ["五官", "臉型", "服飾", "髮型", "髮飾"]}
    if t == "新手":
        old = {**core, "眼鏡": NO, "鬍子": NO, "裝飾": NO, "耳環": NEVER, "武器": NEVER, "特效": NEVER, "翅膀": NEVER}
        new_var = {"耳環": NEVER, "武器": NEVER, "翅膀": NEVER}
    elif t == "一般":
        old = {**core, "眼鏡": NO, "鬍子": NO, "裝飾": NO, "耳環": NO, "武器": NO, "特效": NO, "翅膀": NO}
        new_var = {"耳環": NO, "武器": YES, "翅膀": NO}
    elif t == "儲值":  # 神娃 儲值裝 removed 2026-05; 人物 still made
        old = {p: NEVER for p in ALL_PARTS}
        new_var = {"耳環": NO, "武器": YES, "翅膀": NO}
    else:  # BOSS
        old = {**core, "眼鏡": NO, "鬍子": NO, "裝飾": NO, "耳環": YES, "武器": YES, "特效": YES, "翅膀": NO}
        new_var = {"耳環": YES, "武器": YES, "翅膀": YES}
    # 人物 system has no 五官／臉型／眼鏡／裝飾／特效
    new = {"五官": NEVER, "臉型": NEVER, "服飾": YES, "髮型": YES, "髮飾": YES, "眼鏡": NEVER, "鬍子": NO,
           "裝飾": NEVER, "特效": NEVER, **new_var}
    return old, new


def parts_for(tier, gender, char):
    old, new = tier_base(tier)
    choice = char.get("choice")  # 一般裝: "weapon" | "effect" | None
    if tier.startswith("一般") and choice:
        old["武器" if choice == "weapon" else "特效"] = YES
    if gender == "女":
        old["鬍子"] = new["鬍子"] = NEVER
    old.update(char.get("parts_old", {}))
    new.update(char.get("parts_new", {}))
    return old, new


def mark_cell(v):
    if v in (YES, NEVER):
        return (v, {})
    if v in (NO, ""):
        return (NO, {"color": "gray"})
    return (v, {"color": "orange"})


def parts_table(tier, gender, char):
    """Horizontal: header row = parts, one row each for 神娃 and 人物."""
    old, new = parts_for(tier, gender, char)
    rows = [[("部件", {"bold": True})] + [(p, {"bold": True}) for p in ALL_PARTS],
            [("神娃", {"bold": True})] + [mark_cell(old[p]) for p in ALL_PARTS],
            [("人物", {"bold": True})] + [mark_cell(new[p]) for p in ALL_PARTS]]
    t = table(rows)
    t["table"]["has_row_header"] = True
    return t


def sheet_caption(group, gender=None):
    return f"示意圖｜{group['tier']}" + (f"｜{gender}" if gender else "")


def upload_name(proposal, stem):
    return f"{proposal['month']}_{stem}"


def find_sheet(sheets_dir, group):
    if not sheets_dir:
        return None
    hits = sorted(Path(sheets_dir).glob(group["key"] + "*.png")) + sorted(Path(sheets_dir).glob(group["key"] + "*.jpg"))
    return hits[0] if hits else None


def image_or_placeholder(api, blob, name, caption, log, label):
    """Upload PNG bytes and return an image block; without api (preview) return a gray marker paragraph."""
    if blob is None:
        return callout(f"{caption}：尚未產出（gen_sheets.py 跑完後用 swap 模式換入）", emoji="🖼️")
    if not api:
        return para(f"[preview] {label} {name}.png", color="gray")
    fid = api.upload_image(blob, "png", name)
    log(f"  uploaded {name}.png")
    return image_block(fid)


def char_blocks(p, g, gender, char, scenes, crop, api, log):
    """One character = heading, 主色 + swatch, horizontal parts table, then [crop | 重點需求] columns (Leo's layout)."""
    key = GENDER_KEY[gender]
    stem = f"{g['key']}_{key}"
    out = [heading(2, f"{gender}｜{char['persona']}"),
           para(f"主色：{char['main_color']}", bold=True),
           image_or_placeholder(api, color_chip(char["main_color"]), upload_name(p, stem + "_color"), "", log, "chip"),
           parts_table(g["tier"], gender, char)]
    right = []
    reqs = char.get("requirements", [])
    if reqs:
        right.append(para("重點需求", bold=True))
        right += [bullet(r) for r in reqs]
    for sc in scenes:
        label = sc["name"] + (f"（{sc['corner']}）" if sc.get("corner") else "")
        right.append(para(label, bold=True))
        if sc.get("desc"):
            right.append(bullet(sc["desc"]))
    left = [image_or_placeholder(api, crop, upload_name(p, stem), sheet_caption(g, gender), log, "crop")]
    out.append(column_list(left, right or [para("")]))
    return out


def build(proposal, api=None, sheets_dir=None, log=print):
    p = proposal
    blocks = [heading(1, "活動總覽")]
    blocks += [bullet(f"活動名稱：{p['event_name']}"),
               bullet(f"上線時間：{p['period']}"),
               bullet(f"主題：{p['theme']}"),
               bullet(f"說明：{p.get('theme_desc', '')}"),
               bullet("配色：")]
    cols = [g["tier"] for g in p["groups"]]
    rows = [[("主色", {"bold": True})] + [(c, {"bold": True}) for c in cols]]
    for gender, key in (("男", "male"), ("女", "female")):
        rows.append([(gender, {"bold": True})] + [g[key]["main_color"] for g in p["groups"]])
    blocks.append(table(rows))
    blocks.append(divider())

    for g in p["groups"]:
        head = g["tier"] + (f"　{g['head_note']}" if g.get("head_note") else "")
        blocks.append(heading(1, head))
        fg = g.get("foregrounds", [])
        bg = g.get("background")
        male_scenes = [s for s in fg if s.get("owner", "male") == "male"]
        female_scenes = [s for s in fg if s.get("owner") == "female"]
        if bg:
            (female_scenes if bg.get("owner", "female") == "female" else male_scenes).append(bg)
        sheet = find_sheet(sheets_dir, g)
        crops = crop_halves(sheet) if sheet else (None, None)
        blocks += char_blocks(p, g, "男", g["male"], male_scenes, crops[0], api, log)
        blocks += char_blocks(p, g, "女", g["female"], female_scenes, crops[1], api, log)

    dr = p.get("dressing_room")
    if dr:
        blocks.append(heading(1, "人物更衣室"))
        blocks.append(bullet(f"{dr['name']}：{dr['desc']}" if dr.get("name") else dr["desc"]))
        shot = find_sheet(sheets_dir, {"key": DRESSING_KEY})
        blob = shot.read_bytes() if shot and shot.suffix.lower() == ".png" else None
        blocks.append(image_or_placeholder(api, blob, upload_name(p, DRESSING_KEY), "示意圖｜更衣室", log, "dressing room"))

    blocks.append(divider())
    blocks.append(callout(f"本頁由 avatar-proposal skill 產出（{date.today().isoformat()}）。部件表：✅ 要做｜— 這次沒有（可以有，本期不放）｜❌ 一定不會有（該等級規格不放，或該系統沒有這個部件）｜橘字為人工覆寫。特效一律標明實體或虛體。示意圖為 image-studio 概念稿，給美術看方向用。", emoji="🤖"))
    return blocks


def swap_targets(proposal, sheets_dir):
    """{upload name stem: (caption, png bytes)} for every crop and the dressing room that has a file on disk."""
    out = {}
    for g in proposal["groups"]:
        sheet = find_sheet(sheets_dir, g)
        if sheet:
            for gender, blob in zip(("男", "女"), crop_halves(sheet)):
                out[upload_name(proposal, f"{g['key']}_{GENDER_KEY[gender]}")] = (sheet_caption(g, gender), blob)
    shot = find_sheet(sheets_dir, {"key": DRESSING_KEY})
    if shot and shot.suffix.lower() == ".png":
        out[upload_name(proposal, DRESSING_KEY)] = ("示意圖｜更衣室", shot.read_bytes())
    return out


def swap(api, page_id, proposal, sheets_dir, log=print):
    """Replace images in place. An image is matched by its uploaded file name (<month>_<key>_<male|female>.png,
    as fill/new upload it) or by a caption 示意圖｜<tier>｜<男|女> / 示意圖｜更衣室 on a template placeholder."""
    targets = swap_targets(proposal, sheets_dir)
    by_caption = {cap: stem for stem, (cap, _) in targets.items()}
    done = 0
    for _, b in api.walk(page_id):
        if b["type"] == "image":
            im = b["image"]
            fname = im.get(im["type"], {}).get("url", "").split("?")[0].rsplit("/", 1)[-1]
            stem = fname[:-4] if fname.endswith(".png") else None
            stem = stem if stem in targets else by_caption.get(plain(im.get("caption")))
            if stem:
                api.replace_image(b["id"], api.upload_image(targets[stem][1], "png", stem))
                log(f"  swapped {stem}")
                done += 1
        elif b["type"] == "callout":
            txt = plain(b["callout"]["rich_text"])
            stem = next((s for cap, s in by_caption.items() if txt.startswith(cap + "：") and "尚未產出" in txt), None)
            if stem:
                fid = api.upload_image(targets[stem][1], "png", stem)
                api.append(b["parent"][b["parent"]["type"]], [image_block(fid)], after=b["id"])
                api.call("DELETE", f"/blocks/{b['id']}")
                log(f"  filled placeholder {stem}")
                done += 1
    return done


ADJUST_WORDS = ("調整紀錄", "調整記錄", "修改紀錄", "修改記錄")
# The 人物設定 template page (Leo's layout + 百鬼夜宴 example); PMs duplicate it, fill must never run on it directly.
TEMPLATE_PAGE_ID = "3ed87244fa40819bbbfdd0c04bd28277"
EXAMPLE_MARKER = "範本示例內容"
# 一部 活動資料庫: the template lives here; same-type plans are found by 活動類型
EVENT_DB_ID = "1fa87244fa4081f48ae6cdb09a4059cb"
EVENT_TYPE_PROP, EVENT_TYPE = "活動類型", "人物設定"


def page_title(proposal):
    """Same convention as the DB's other rows (2611人物大活動-月城十二星): <month>人物設定-<theme>."""
    return f"{proposal['month']}人物設定-{proposal['theme']}"


def check_page_type(api, page_id):
    """Stop when the PM copied the wrong kind of page (a 活動資料庫 row whose 活動類型 is not 人物設定)."""
    pg = api.call("GET", f"/pages/{page_id}")
    prop = pg.get("properties", {}).get(EVENT_TYPE_PROP)
    typ = ((prop or {}).get("select") or {}).get("name")
    if typ and typ != EVENT_TYPE:
        raise SystemExit(f"[fill] page 活動類型 is {typ}, not {EVENT_TYPE}: the PM probably copied the wrong page; "
                         f"ask them to copy the template or an old 人物設定 page")


def clear_example(api, page_id, top, log=print):
    """Clear old content before filling. Two cases, both deleting up to (not including) the 調整紀錄 heading:
    - a copy of the template: from the 📌 example marker
    - a copy of an older 人物設定 plan (Tim 2026-10-08: PMs often copy last month's page): from its 活動總覽 heading.
    Returns the refreshed top-level list."""
    start = next((i for i, b in enumerate(top) if b["type"] == "callout" and plain(b["callout"]["rich_text"]).startswith(EXAMPLE_MARKER)), None)
    if start is None:
        start = next((i for i, b in enumerate(top) if b["type"] == "heading_1" and "活動總覽" in plain(b["heading_1"]["rich_text"])), None)
        if start is not None:
            log("  page is a copy of an older plan: replacing its content; its old 調整紀錄 entries are kept, tell the PM to clear them")
    if start is None:
        return top
    end = next((i for i, b in enumerate(top) if i > start and b["type"].startswith("heading_")
                and any(w in plain(b[b["type"]]["rich_text"]) for w in ADJUST_WORDS)), None)
    if end is None:
        raise SystemExit("[fill] old content found but no 調整紀錄 heading after it; not deleting anything, fix the page first")
    for b in top[start:end]:
        api.call("DELETE", f"/blocks/{b['id']}")
    log(f"  cleared old content: {end - start} blocks")
    return api.children(page_id)


def set_title(api, page_id, title):
    pg = api.call("GET", f"/pages/{page_id}")
    key = next(k for k, v in pg["properties"].items() if v["type"] == "title")
    api.call("PATCH", f"/pages/{page_id}", {"properties": {key: {"title": [{"type": "text", "text": {"content": title}}]}}})


def fill(api, page_id, proposal, sheets_dir, log=print, title=None):
    """Insert the proposal content into an existing (template-made) page.

    Anchor = the first top-level heading whose text contains 調整紀錄/修改紀錄; content goes right before it,
    so the template's table of contents / 調整紀錄 skeleton stays intact. No anchor -> append at the end (warned).
    A page duplicated from the template has its example content cleared first (see clear_example).
    title: rename the page too (the copy still carries the template's name).
    """
    if page_id.replace("-", "") == TEMPLATE_PAGE_ID:
        raise SystemExit("[fill] this is the template page itself; duplicate it in Notion and fill the copy")
    check_page_type(api, page_id)
    top = clear_example(api, page_id, api.children(page_id), log=log)
    after = None
    anchor_found = False
    for i, b in enumerate(top):
        if b["type"].startswith("heading_") and any(w in plain(b[b["type"]]["rich_text"]) for w in ADJUST_WORDS):
            anchor_found = True
            after = top[i - 1]["id"] if i > 0 else None
            break
    if not anchor_found:
        log("  WARNING: no 調整紀錄 heading found; appending at the end of the page")
        after = top[-1]["id"] if top else None
    if anchor_found and after is None:
        # Notion has no "insert before"; content can't go above the very first block.
        raise SystemExit("[fill] 調整紀錄 is the first block of the page; add any block above it in the template, then rerun")
    blocks = build(proposal, api=api, sheets_dir=sheets_dir, log=log)
    api.append(page_id, blocks, after=after, log=log)
    if title:
        set_title(api, page_id, title)
        log(f"  title -> {title}")
    return len(blocks)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["preview", "new", "fill", "swap"])
    ap.add_argument("proposal")
    ap.add_argument("--parent")
    ap.add_argument("--page")
    ap.add_argument("--sheets")
    ap.add_argument("--title")
    a = ap.parse_args()
    proposal = json.loads(Path(a.proposal).read_text(encoding="utf-8"))
    title = a.title or page_title(proposal)
    sys.stdout.reconfigure(encoding="utf-8")
    warns = lint(proposal)
    for w in warns:
        print("LINT", w)

    if a.mode == "preview":
        blocks = build(proposal, api=None, sheets_dir=a.sheets)
        kinds = {}
        for b in blocks:
            kinds[b["type"]] = kinds.get(b["type"], 0) + 1
        print(f"title: {title}\ntop-level blocks: {len(blocks)} {kinds}")
        print(f"  {'':16} {' '.join(ALL_PARTS)}")
        for g in proposal["groups"]:
            for gender, key in (("男", "male"), ("女", "female")):
                old, new = parts_for(g["tier"], gender, g[key])
                print(f"  {g['tier']} {gender} 神娃  {'   '.join(old[p][:1] for p in ALL_PARTS)}")
                print(f"  {g['tier']} {gender} 人物  {'   '.join(new[p][:1] for p in ALL_PARTS)}")
            print(f"    sheet={find_sheet(a.sheets, g)}")
        print(f"  dressing room={find_sheet(a.sheets, {'key': DRESSING_KEY})}")
        return
    if warns:
        print("LINT warnings above: fix proposal.json first, or tell the user why they are accepted.")

    api = Notion(find_token(dept="一部"))
    if a.mode == "new":
        blocks = build(proposal, api=api, sheets_dir=a.sheets)
        if a.parent:
            page = api.create_page(a.parent, title, blocks, log=print, deep=True)
        else:
            # default: a row of 活動資料庫 typed 人物設定, like the template page
            page = api.call("POST", "/pages", {"parent": {"database_id": EVENT_DB_ID}, "properties": {
                "Name": {"title": [{"type": "text", "text": {"content": title}}]},
                EVENT_TYPE_PROP: {"select": {"name": EVENT_TYPE}}}, "children": blocks[:1]})
            print(f"page created {page['url']}")
            api.append(page["id"], blocks[1:], log=print)
        print("verify top-level children:", api.count_children(page["id"]), "/", len(blocks))
        print("URL:", page["url"])
    elif a.mode == "fill":
        if not a.page:
            sys.exit("--page <page_id> required")
        n = fill(api, a.page, proposal, a.sheets, title=title)
        print("inserted blocks:", n, "| top-level now:", api.count_children(a.page))
    else:
        if not a.page:
            sys.exit("--page <page_id> required")
        n = swap(api, a.page, proposal, a.sheets)
        print("swapped:", n)


if __name__ == "__main__":
    main()
