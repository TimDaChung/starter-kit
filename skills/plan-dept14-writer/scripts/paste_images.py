"""Locate image slots in a Notion plan page and paste images there (REST, no MCP, no browser).

  python paste_images.py list    <url|id> [--depth 6]
        # heading tree + every image / column / synced_block / text placeholder, with block ids
  python paste_images.py insert  <url|id> --parent <block_id> [--after <block_id>] --image a.png [--image b.png ...]
                                 [--caption 《…》] [--label 《1.xxx》] [--remove <placeholder_block_id>] --line 魚樂園
        # parent = a column id (right column), a synced_block original, a toggle, or the page itself
        # --caption : 四部 style, written into the image caption (one per --image, or one shared)
        # --label   : 一部 style, a paragraph 《n.圖名》 inserted right above each image, caption left empty
  python paste_images.py replace <image_block_id> --image a.png [--caption 《…》] --line 魚樂園
        # swap a placeholder image (e.g. the 「窩是示意圖」 card) in place
  python paste_images.py split   <grid.png> --grid 2x2 [--out DIR] [--trim 0.0]
        # cut a storyboard grid into cells (pages usually take one image per 分鏡)

--line 神幣/娛樂城/鬥地主/魚樂園 picks the dept credential for writes (神幣 = 一部, others = 四部).
Reading picks 一部/四部 from the id fingerprint, falling back to trying both.
One rw credential per dept; write guard rails (consent first, read back) still apply.
See ../references/image-slots.md for WHERE each kind of image goes.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from notion_rest import (LINE_DEPT, CredentialExpired, Notion, dept_from_id, find_token, image_block, page_id_from, para, plain)  # noqa: E402

PLACEHOLDER_WORDS = ("【待補】", "待補", "圖後補", "圖片放置區", "圖片待補", "美術完成後補上", "後補")
TEXT_TYPES = ("paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "toggle", "callout", "quote")


def reader(page_id):
    dept = dept_from_id(page_id)
    order = [dept] if dept else ["一部", "四部"]
    order += [d for d in ("一部", "四部") if d not in order]
    last = None
    for d in order:
        try:
            api = Notion(find_token("readonly", dept=d))
            api.call("GET", f"/blocks/{page_id}")
            return api, d
        except CredentialExpired:
            raise
        except RuntimeError as e:
            last = e
    raise SystemExit(f"[list] both dept credentials failed (page not connected to the integration?): {last}")


def writer(line):
    if not line:
        raise SystemExit("--line 神幣/娛樂城/鬥地主/魚樂園 is required for writing")
    return Notion(find_token("readwrite", line=line))


def text_of(b):
    t = b["type"]
    v = b.get(t, {})
    if t in TEXT_TYPES:
        return plain(v.get("rich_text"))
    if t == "image":
        return plain(v.get("caption"))
    if t == "child_page":
        return v.get("title", "")
    return ""


def cmd_list(a):
    pid = page_id_from(a.page)
    api, dept = reader(pid)
    print(f"# page {pid}  ({dept})")
    stats = {"image": 0, "placeholder": 0, "synced_original": 0, "synced_ref": 0}
    for depth, b in api.walk(pid, max_depth=a.depth):
        t = b["type"]
        txt = text_of(b)
        ind = "  " * depth
        bid = b["id"]
        if t.startswith("heading_"):
            print(f"{ind}{'#' * int(t[-1])} {txt}   [{bid}]")
        elif t == "image":
            stats["image"] += 1
            kind = b["image"]["type"]
            print(f"{ind}[IMG {kind}] caption={txt or '∅'}   [{bid}]")
        elif t == "column_list":
            print(f"{ind}[COLUMNS]   [{bid}]")
        elif t == "column":
            print(f"{ind}[col]   [{bid}]")
        elif t == "synced_block":
            src = b["synced_block"].get("synced_from")
            if src:
                stats["synced_ref"] += 1
                print(f"{ind}[SYNCED REF -> {src.get('block_id')}]  (do not paste here; paste into the original)   [{bid}]")
            else:
                stats["synced_original"] += 1
                print(f"{ind}[SYNCED ORIGINAL]   [{bid}]")
        elif t == "toggle":
            print(f"{ind}[toggle] {txt[:60]}   [{bid}]")
        elif t == "child_page":
            print(f"{ind}[child page] {txt}   [{bid}]")
        elif txt and any(w in txt for w in PLACEHOLDER_WORDS):
            stats["placeholder"] += 1
            print(f"{ind}[PLACEHOLDER {t}] {txt[:60]}   [{bid}]")
        elif txt.startswith("《") and t == "paragraph":
            print(f"{ind}[label] {txt[:60]}   [{bid}]")
    print(f"\n# images={stats['image']} text-placeholders={stats['placeholder']} synced originals={stats['synced_original']} refs={stats['synced_ref']}")


def cmd_insert(a):
    pid = page_id_from(a.page)
    api = writer(a.line)
    caps = a.caption or []
    labels = a.label or []
    blocks = []
    for i, img in enumerate(a.image):
        cap = caps[i] if i < len(caps) else (caps[0] if len(caps) == 1 else "")
        lab = labels[i] if i < len(labels) else ""
        fid = api.upload_file(img)
        if lab:
            blocks.append(para(lab))
        blocks.append(image_block(fid, cap))
        print(f"  uploaded {Path(img).name}")
    parent = a.parent.replace("-", "") if a.parent else pid
    res = api.append(parent, blocks, after=a.after)
    print(f"  inserted {len(res)} blocks under {parent}" + (f" after {a.after}" if a.after else ""))
    if a.remove:
        for rid in a.remove:
            api.call("DELETE", f"/blocks/{rid}")
            print(f"  removed placeholder {rid}")
    # verify
    kids = api.children(parent)
    new_ids = {r["id"] for r in res}
    ok = sum(1 for k in kids if k["id"] in new_ids)
    print(f"verify: {ok}/{len(res)} new blocks present under parent")


def cmd_replace(a):
    api = writer(a.line)
    fid = api.upload_file(a.image[0])
    r = api.replace_image(a.block, fid, caption=(a.caption[0] if a.caption else None))
    print(f"replaced {a.block} -> type {r['image']['type']}")


def cmd_split(a):
    from PIL import Image
    cols, rows = (int(x) for x in a.grid.lower().split("x"))
    im = Image.open(a.grid_png)
    W, H = im.size
    out = Path(a.out or Path(a.grid_png).with_suffix(""))
    out.mkdir(parents=True, exist_ok=True)
    cw, ch = W / cols, H / rows
    n = 0
    for r in range(rows):
        for c in range(cols):
            n += 1
            tx, ty = cw * a.trim, ch * a.trim
            box = (int(c * cw + tx), int(r * ch + ty), int((c + 1) * cw - tx), int((r + 1) * ch - ty))
            p = out / f"{Path(a.grid_png).stem}_分鏡{n}.png"
            im.crop(box).save(p)
            print(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list")
    s.add_argument("page")
    s.add_argument("--depth", type=int, default=6)
    s = sub.add_parser("insert")
    s.add_argument("page")
    s.add_argument("--parent")
    s.add_argument("--after")
    s.add_argument("--image", action="append", required=True)
    s.add_argument("--caption", action="append")
    s.add_argument("--label", action="append")
    s.add_argument("--remove", action="append")
    s.add_argument("--line")
    s = sub.add_parser("replace")
    s.add_argument("block")
    s.add_argument("--image", action="append", required=True)
    s.add_argument("--caption", action="append")
    s.add_argument("--line")
    s = sub.add_parser("split")
    s.add_argument("grid_png")
    s.add_argument("--grid", required=True)
    s.add_argument("--out")
    s.add_argument("--trim", type=float, default=0.0)
    a = ap.parse_args()
    {"list": cmd_list, "insert": cmd_insert, "replace": cmd_replace, "split": cmd_split}[a.cmd](a)


if __name__ == "__main__":
    main()
