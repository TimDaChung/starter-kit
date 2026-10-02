"""Build the 神娃＋人物設定 Notion page (two-column layout) from proposal.json.

  python build_notion.py preview proposal.json                       # no API: print what would be built
  python build_notion.py fill    proposal.json --page <page_id>   [--sheets DIR]   # DEFAULT in the SOP
        # user made the page from the Notion template and gave us the URL; content is inserted right before
        # the template's 調整紀錄 heading (table of contents / adjustment-log skeleton untouched), sheets uploaded inline
  python build_notion.py swap    proposal.json --page <page_id>   [--sheets DIR]
        # template already has placeholder images captioned "示意圖｜<tier>": replace the files in place
  python build_notion.py new     proposal.json --parent <page_id> [--sheets DIR] [--title T]
        # only when the user explicitly asks us to create the page ourselves

Sheets: one PNG per group, matched by group "key" prefix (e.g. 01_newbie*.png) inside --sheets.
Token: NOTION_KEY env or the readwrite token on the share (Tim only). See notion_api.find_token.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from notion_api import (Notion, bullet, callout, column_list, divider, find_token, heading, image_block, para, plain, table)  # noqa: E402

OLD_PARTS = ["五官", "臉型", "服飾", "髮型", "髮飾", "眼鏡", "鬍子", "裝飾", "耳環", "武器", "特效"]
NEW_PARTS = ["服飾", "髮型", "髮飾", "武器", "耳環", "翅膀"]
ALL_PARTS = ["五官", "臉型", "服飾", "髮型", "髮飾", "眼鏡", "鬍子", "裝飾", "耳環", "武器", "特效", "翅膀"]
YES, NO, FREE = "✅", "—", "自由決定"


def tier_base(tier):
    """Return (old, new) default marks for a tier. Mirrors SOP 步驟一 部件需求表."""
    t = "BOSS" if tier.upper().startswith("BOSS") else ("一般" if tier.startswith("一般") else tier)
    if t == "新手":
        old = {p: YES for p in ["五官", "臉型", "服飾", "髮型", "髮飾"]}
        old.update({p: NO for p in ["眼鏡", "鬍子", "裝飾", "耳環", "武器", "特效"]})
        new = {"服飾": YES, "髮型": YES, "髮飾": YES, "武器": NO, "耳環": NO, "翅膀": NO}
    elif t == "一般":
        old = {p: YES for p in ["五官", "臉型", "服飾", "髮型", "髮飾"]}
        old.update({p: NO for p in ["眼鏡", "鬍子", "裝飾", "耳環", "武器", "特效"]})
        new = {"服飾": YES, "髮型": YES, "髮飾": YES, "武器": YES, "耳環": NO, "翅膀": NO}
    elif t == "儲值":
        old = {p: NO for p in OLD_PARTS}
        new = {"服飾": YES, "髮型": YES, "髮飾": YES, "武器": YES, "耳環": NO, "翅膀": NO}
    else:  # BOSS
        old = {p: YES for p in ["五官", "臉型", "服飾", "髮型", "髮飾", "武器", "特效"]}
        old.update({p: NO for p in ["眼鏡", "鬍子", "裝飾", "耳環"]})
        new = {"服飾": YES, "髮型": YES, "髮飾": YES, "武器": YES, "耳環": NO, "翅膀": YES}
    return old, new


def parts_for(tier, gender, char):
    old, new = tier_base(tier)
    choice = char.get("choice")  # 一般裝: "weapon" | "effect" | None
    if tier.startswith("一般") and choice:
        old["武器" if choice == "weapon" else "特效"] = YES
    if gender == "女":
        old["鬍子"] = NO
    old.update(char.get("parts_old", {}))
    new.update(char.get("parts_new", {}))
    return old, new


def mark_cell(v):
    if v == YES:
        return (YES, {})
    if v in (NO, ""):
        return (NO, {"color": "gray"})
    return (v, {"color": "orange"})


def parts_table(tier, gender, char):
    old, new = parts_for(tier, gender, char)
    rows = [[("部件", {"bold": True}), ("神娃", {"bold": True}), ("人物", {"bold": True})]]
    for p in ALL_PARTS:
        if p not in old and p not in new:
            continue
        rows.append([p, mark_cell(old[p]) if p in old else ("", {}), mark_cell(new[p]) if p in new else ("", {})])
    return table(rows)


def sheet_caption(group):
    return f"示意圖｜{group['tier']}"


def find_sheet(sheets_dir, group):
    if not sheets_dir:
        return None
    hits = sorted(Path(sheets_dir).glob(group["key"] + "*.png")) + sorted(Path(sheets_dir).glob(group["key"] + "*.jpg"))
    return hits[0] if hits else None


def char_blocks(tier, gender, char, scenes):
    out = [heading(2, f"{gender}｜{char['persona']}"), para(f"主色：{char['main_color']}", bold=True), parts_table(tier, gender, char)]
    reqs = char.get("requirements", [])
    if reqs:
        out.append(para("重點需求", bold=True))
        out += [bullet(r) for r in reqs]
    for sc in scenes:
        label = sc["name"] + (f"（{sc['corner']}）" if sc.get("corner") else "")
        out.append(para(label, bold=True))
        if sc.get("desc"):
            out.append(bullet(sc["desc"]))
    return out


def build(proposal, api=None, sheets_dir=None, log=print):
    p = proposal
    blocks = [heading(1, "活動總覽")]
    blocks += [bullet(f"活動名稱 ｜ {p['event_name']}"),
               bullet(f"地區 ｜ 中文　平台 ｜ Mobile ✔ PC ✔　上線時間 ｜ {p['period']}"),
               bullet(f"主題 ｜ {p['theme']}　說明 ｜ {p.get('theme_desc', '')}"),
               bullet(f"主要類別 ｜ {'、'.join(p.get('category', []))}　要素 ｜ {'、'.join(p.get('elements', []))}"),
               bullet("角色清單 ｜ 各服飾主色分配，副色由美術搭配")]
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
        left = char_blocks(g["tier"], "男", g["male"], male_scenes) + char_blocks(g["tier"], "女", g["female"], female_scenes)
        right = []
        sheet = find_sheet(sheets_dir, g)
        if sheet and api:
            fid = api.upload_file(sheet, name=f"{g['key']}_{p['month']}")
            log(f"  uploaded {sheet.name}")
            right.append(image_block(fid, sheet_caption(g)))
        elif sheet:
            right.append(para(f"[preview] image {sheet.name}", color="gray"))
        else:
            right.append(callout(f"{sheet_caption(g)}：尚未產出（gen_sheets.py 跑完後用 swap 模式換入）", emoji="🖼️"))
        blocks.append(column_list(left, right))

    dr = p.get("dressing_room")
    if dr:
        blocks.append(heading(1, "更衣室背景"))
        left = [para(dr["name"], bold=True), bullet(dr["desc"])]
        right = [callout("示意圖｜更衣室：由美術依描述製作，本企劃不出圖", emoji="🖼️")]
        blocks.append(column_list(left, right))

    blocks.append(divider())
    blocks.append(callout(f"本頁由 avatar-proposal skill 產出（{date.today().isoformat()}）。部件表依 SOP 步驟一規則自動勾選，橘字為人工覆寫；示意圖為 image-studio 概念稿，給美術看方向用。", emoji="🤖"))
    return blocks


def swap(api, page_id, proposal, sheets_dir, log=print):
    want = {sheet_caption(g): g for g in proposal["groups"]}
    done = 0
    for _, b in api.walk(page_id):
        if b["type"] != "image":
            continue
        cap = plain(b["image"].get("caption"))
        for prefix, g in want.items():
            if cap.startswith(prefix):
                sheet = find_sheet(sheets_dir, g)
                if not sheet:
                    log(f"  skip {prefix}: no sheet file")
                    continue
                fid = api.upload_file(sheet, name=f"{g['key']}_{proposal['month']}")
                api.replace_image(b["id"], fid, caption=prefix)
                log(f"  swapped {prefix} <- {sheet.name}")
                done += 1
    # placeholders (callouts) that still need an image -> insert image after the callout
    for _, b in api.walk(page_id):
        if b["type"] == "callout":
            txt = plain(b["callout"]["rich_text"])
            for prefix, g in want.items():
                if txt.startswith(prefix) and "尚未產出" in txt:
                    sheet = find_sheet(sheets_dir, g)
                    if sheet:
                        fid = api.upload_file(sheet, name=f"{g['key']}_{proposal['month']}")
                        api.append(b["parent"][b["parent"]["type"]], [image_block(fid, prefix)], after=b["id"])
                        api.call("DELETE", f"/blocks/{b['id']}")
                        log(f"  filled placeholder {prefix} <- {sheet.name}")
                        done += 1
    return done


ADJUST_WORDS = ("調整紀錄", "調整記錄", "修改紀錄", "修改記錄")


def fill(api, page_id, proposal, sheets_dir, log=print):
    """Insert the proposal content into an existing (template-made) page.

    Anchor = the first top-level heading whose text contains 調整紀錄/修改紀錄; content goes right before it,
    so the template's table of contents / 調整紀錄 skeleton stays intact. No anchor -> append at the end (warned).
    """
    top = api.children(page_id)
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
    title = a.title or f"{proposal['month']}_大活動_人物設定_{proposal['theme']}"

    if a.mode == "preview":
        blocks = build(proposal, api=None, sheets_dir=a.sheets)
        kinds = {}
        for b in blocks:
            kinds[b["type"]] = kinds.get(b["type"], 0) + 1
        print(f"title: {title}\ntop-level blocks: {len(blocks)} {kinds}")
        for g in proposal["groups"]:
            for gender, key in (("男", "male"), ("女", "female")):
                old, new = parts_for(g["tier"], gender, g[key])
                print(f"  {g['tier']} {gender} {g[key]['persona']:8} 神娃={''.join('1' if old[p]==YES else '0' for p in OLD_PARTS)} 人物={''.join('1' if new[p]==YES else '0' for p in NEW_PARTS)} sheet={find_sheet(a.sheets, g)}")
        return

    api = Notion(find_token("readwrite"))
    if a.mode == "new":
        if not a.parent:
            sys.exit("--parent <page_id> required")
        blocks = build(proposal, api=api, sheets_dir=a.sheets)
        page = api.create_page(a.parent, title, blocks, log=print, deep=True)
        print("verify top-level children:", api.count_children(page["id"]), "/", len(blocks))
        print("URL:", page["url"])
    elif a.mode == "fill":
        if not a.page:
            sys.exit("--page <page_id> required")
        n = fill(api, a.page, proposal, a.sheets)
        print("inserted blocks:", n, "| top-level now:", api.count_children(a.page))
    else:
        if not a.page:
            sys.exit("--page <page_id> required")
        n = swap(api, a.page, proposal, a.sheets)
        print("swapped:", n)


if __name__ == "__main__":
    main()
