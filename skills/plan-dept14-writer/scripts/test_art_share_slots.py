"""Tests for art_share_slots.py: folder resolution, slot parsing and slot -> file rules.

Uses a fake folder tree under tmp_path and hand-made Notion block dicts; no art share, no Notion.

Run: python -m pytest skills/plan-dept14-writer/scripts/test_art_share_slots.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

Image = pytest.importorskip("PIL.Image")

import art_share_slots as ass  # noqa: E402


# ------------------------------------------------------------------ helpers
def touch(p: Path, data: bytes = b"x") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


def png_bytes(color: tuple[int, int, int], size: tuple[int, int] = (32, 32), level: int = 6) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG", compress_level=level)
    return buf.getvalue()


_n = 0


def blk(kind: str, text: str = "", children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    global _n
    _n += 1
    b: dict[str, Any] = {"id": f"b{_n:04d}", "type": kind, kind: {"rich_text": [{"plain_text": text}]}}
    if children:
        b["children"] = children
        b["has_children"] = True
    return b


def img(name: str) -> dict[str, Any]:
    global _n
    _n += 1
    return {"id": f"i{_n:04d}", "type": "image",
            "image": {"type": "file", "file": {"url": f"https://s3.example/x/{name}?sig=1"}, "caption": []}}


def cols(*columns: list[dict[str, Any]]) -> dict[str, Any]:
    return blk("column_list", children=[blk("column", children=c) for c in columns])


# ------------------------------------------------------------------ titles
@pytest.mark.parametrize("title,kind,yymm", [
    ("2611神娃大活動-主題甲", "神娃大活動", "2611"),
    ("2609人物大活動-主題乙", "人物大活動", "2609"),
    ("2610神裝禮包", "神裝禮包", "2610"),
    ("【測試】2611神娃大活動-主題甲（測完即刪）", "神娃大活動", "2611"),
])
def test_parse_title(title: str, kind: str, yymm: str) -> None:
    assert ass.parse_title(title) == (kind, yymm)


def test_parse_title_rejects_other_pages() -> None:
    with pytest.raises(SystemExit):
        ass.parse_title("2610登入活動")


def test_activity_name() -> None:
    assert ass.activity_name("2609神娃大活動-主題丙") == "主題丙"
    assert ass.activity_name("2610神裝禮包") == ""


# ------------------------------------------------------------------ folder resolution
@pytest.fixture()
def avatar_root(tmp_path: Path) -> Path:
    root = tmp_path / "●Avatar魔鬼營"
    for name in ("2025_活動", "202609_主題丙(大活動)", "202610_主題丁(大活動)",
                 "202611_11月大活動(大活動)", "202611_12月大活動(大活動)", "儲備活動_前背景"):
        (root / name).mkdir(parents=True)
    return root


def test_avatar_folder_by_prefix(avatar_root: Path) -> None:
    got, notes = ass.resolve_month_dir(avatar_root, "2609")
    assert got.name == "202609_主題丙(大活動)" and notes == []


def test_avatar_prefix_typo_is_ignored_when_real_month_exists(avatar_root: Path) -> None:
    got, notes = ass.resolve_month_dir(avatar_root, "2611")
    assert got.name == "202611_11月大活動(大活動)"
    assert any("12月" in n for n in notes)


def test_avatar_prefix_typo_stops_for_pm(avatar_root: Path) -> None:
    # December has no 202612_ folder; the only one naming 12月 carries prefix 202611_
    with pytest.raises(ass.StopForPM) as e:
        ass.resolve_month_dir(avatar_root, "2612")
    assert "202611_12月大活動(大活動)" in str(e.value)


def test_avatar_missing_month_stops(avatar_root: Path) -> None:
    with pytest.raises(ass.StopForPM) as e:
        ass.resolve_month_dir(avatar_root, "2701")
    assert "no folder" in str(e.value)


def test_avatar_several_folders_stop(avatar_root: Path) -> None:
    (avatar_root / "202610_另一個名字(大活動)").mkdir()
    with pytest.raises(ass.StopForPM) as e:
        ass.resolve_month_dir(avatar_root, "2610")
    assert "several folders" in str(e.value)


def test_headshot_folder_named_by_month(tmp_path: Path) -> None:
    root = tmp_path / "●大頭貼與配件"
    for name in ("202605_主題戊(大活動)", "202609_9月大活動(大活動)", "202610_10月大活動(大活動)"):
        (root / name).mkdir(parents=True)
    assert ass.resolve_month_dir(root, "2609")[0].name == "202609_9月大活動(大活動)"
    assert ass.resolve_month_dir(root, "2605")[0].name == "202605_主題戊(大活動)"


def test_character_folder(tmp_path: Path) -> None:
    root = tmp_path / "人物系統"
    for name in ("260101_一月大活動", "261001_十月大活動", "261101_十一月大活動", "270101_一月大活動", "BG"):
        (root / name).mkdir(parents=True)
    assert ass.resolve_month_dir(root, "2611", char_style=True)[0].name == "261101_十一月大活動"
    assert ass.resolve_month_dir(root, "2701", char_style=True)[0].name == "270101_一月大活動"
    with pytest.raises(ass.StopForPM):
        ass.resolve_month_dir(root, "2612", char_style=True)


def test_character_folder_month_mismatch_stops(tmp_path: Path) -> None:
    root = tmp_path / "人物系統"
    (root / "261201_十一月大活動").mkdir(parents=True)
    with pytest.raises(ass.StopForPM) as e:
        ass.resolve_month_dir(root, "2612", char_style=True)
    assert "261201_十一月大活動" in str(e.value)


# ------------------------------------------------------------------ files on the share
@pytest.fixture()
def static_dir(tmp_path: Path) -> Path:
    d = tmp_path / "202609_主題丙(大活動)" / "靜態平面"
    for i in range(5):
        a = 4266 + 2 * i
        touch(d / f"{a}+{a + 1}.{'png' if i == 1 else 'jpg'}")  # extensions are not consistent
        touch(d / f"去背_{a}.png")
    touch(d / "前背景" / "去背_4266_fonrt1.png")
    touch(d / "前背景" / "去背_4267_fonrt2.png")  # typo 'fonrt' and the 1/2 suffix is not reliable
    touch(d / "前背景" / "去背_4269_back2.png")
    return d


def test_base_number_and_pairs(static_dir: Path) -> None:
    n, notes = ass.base_number(static_dir)
    assert n == 4266 and notes == []
    assert ass.find_file(static_dir, "4268+4269")[0].suffix == ".png"


def test_base_number_flags_gaps(static_dir: Path) -> None:
    (static_dir / "4274+4275.jpg").unlink()
    _, notes = ass.base_number(static_dir)
    assert notes and "not the expected" in notes[0]


def test_vip_front_matches_typo(static_dir: Path) -> None:
    assert [p.name for p in ass.vip_front_files(static_dir, 4267)] == ["去背_4267_fonrt2.png"]


# ------------------------------------------------------------------ page trees
def avatar_tree(filled: bool) -> list[dict[str, Any]]:
    def pair(group: str, removed: bool = False) -> list[dict[str, Any]]:
        tail = "(202607移除)" if removed else ""
        out = [cols([blk("heading_3", f"{group}-男{tail}")], [blk("heading_3", f"{group}-女{tail}")]),
               blk("paragraph", "圖示(男女共用)")]
        if filled and not removed:
            out.append(img("pair.jpg"))
        return out + [blk("divider")]

    def hs(n: int, pad: int = 0) -> dict[str, Any]:
        cs = [[blk("numbered_list_item", "名稱："),
               blk("numbered_list_item", "圖片：", [img("h.png")] if filled else None)] for _ in range(n)]
        return cols(*cs, *[[blk("paragraph")] for _ in range(pad)])

    tree = [blk("heading_1", "📌本次內容"), blk("heading_2", "1.神娃（完稿待美術完成後補上）")]
    for g in ("新手裝", "一般裝1", "一般裝2"):
        tree += pair(g)
    tree += pair("儲值裝", removed=True)
    for g in ("BOSS裝1", "BOSS裝2"):
        tree += pair(g)
    tree += [blk("heading_2", "2.大頭貼（美術完成後補上）"),
             blk("heading_3", "新手裝"), hs(2, pad=2), blk("heading_3", "一般裝"), hs(4),
             blk("heading_3", "儲值裝(202607移除)"), hs(4), blk("heading_3", "Boss裝"), hs(4),
             blk("heading_2", "3.其他內容（美術完成後補上）"), blk("heading_3", "VIP相關內容"),
             blk("numbered_list_item", "VIP前景：左前景", [blk("numbered_list_item", "WID："),
                                                      blk("numbered_list_item", "圖片：", [img("v.png")] if filled else None)]),
             blk("numbered_list_item", "VIP頭貼(限MB)：大頭貼", [blk("numbered_list_item", "SEQ："),
                                                           blk("numbered_list_item", "圖片：")]),
             blk("heading_1", "📌相關ID資料")]
    return tree


def test_avatar_slots_empty_page() -> None:
    slots, notes = ass.find_slots("神娃大活動", avatar_tree(filled=False), "page")
    keys = [s.key for s in slots]
    assert keys == ([f"圖示/{g}" for g in ("新手裝", "一般裝1", "一般裝2", "BOSS裝1", "BOSS裝2")]
                    + [f"大頭貼/{i}" for i in range(10)] + ["VIP前景", "VIP頭貼"])
    assert all(s.image_block is None for s in slots)
    assert any("儲值裝" in n for n in notes)
    pair_slot = slots[0]
    assert pair_slot.mode == "after" and pair_slot.parent == "page"
    assert all(s.mode == "child" for s in slots[5:])


def test_avatar_slots_filled_page_reads_images() -> None:
    slots, _ = ass.find_slots("神娃大活動", avatar_tree(filled=True), "page")
    filled = {s.key: s.image_name for s in slots}
    assert filled["圖示/新手裝"] == "pair.jpg" and filled["大頭貼/9"] == "h.png"
    assert filled["VIP前景"] == "v.png" and filled["VIP頭貼"] is None


def test_avatar_sources(static_dir: Path, tmp_path: Path) -> None:
    hs = tmp_path / "hs"
    for i in range(10):
        touch(hs / f"{4266 + i}_01.png")
    slots, _ = ass.find_slots("神娃大活動", avatar_tree(filled=False), "page")
    ass.assign_sources("神娃大活動", slots, ass.Dirs(static=static_dir, headshot=hs, base=4266))
    src = {s.key: Path(s.source).name for s in slots}
    assert src["圖示/新手裝"] == "4266+4267.jpg"
    assert src["圖示/一般裝1"] == "4268+4269.png"
    assert src["圖示/BOSS裝2"] == "4274+4275.jpg"
    assert src["大頭貼/0"] == "4266_01.png" and src["大頭貼/6"] == "4272_01.png" and src["大頭貼/9"] == "4275_01.png"
    assert src["VIP前景"] == "去背_4267_fonrt2.png"   # VIP uses the 新手裝 female number (N+1)
    assert src["VIP頭貼"] == "4267_01.png"


def test_avatar_missing_headshot_is_reported(static_dir: Path, tmp_path: Path) -> None:
    slots, _ = ass.find_slots("神娃大活動", avatar_tree(filled=False), "page")
    ass.assign_sources("神娃大活動", slots, ass.Dirs(static=static_dir, headshot=tmp_path / "none", base=4266))
    assert {s.status for s in slots if s.key.startswith("大頭貼/")} == {"missing_source"}


def char_tree() -> list[dict[str, Any]]:
    tree = [blk("heading_1", "📌本次內容"), blk("heading_2", "1.人物")]
    for g in ("新手裝", "一般裝1", "一般裝2", "儲值裝", "BOSS裝1", "BOSS裝2"):
        tree.append(cols([blk("heading_3", f"{g}-男"), blk("numbered_list_item", "名稱：x"), blk("numbered_list_item", "圖示")],
                         [blk("heading_3", f"{g}-女"), blk("numbered_list_item", "名稱：y"),
                          blk("numbered_list_item", "圖示", [img("02.png")])]))
    tree += [blk("heading_2", "2.其他"), blk("heading_3", "吃碰特效(美術完成後補上)"),
             blk("numbered_list_item", "名稱：z"), blk("numbered_list_item", "圖示：", [img("image.png")]),
             blk("heading_3", "人物禮包"), blk("table")]
    return tree


def test_character_slots_and_sources(tmp_path: Path) -> None:
    month = tmp_path / "261101_十一月大活動"
    for s in ("01", "02"):
        for k in range(1, 7):
            touch(month / "去背用" / f"{s}-{k}.png")
    touch(month / "吃碰特效" / "110.mp4")
    slots, _ = ass.find_slots("人物大活動", char_tree(), "page")
    assert len(slots) == 13
    ass.assign_sources("人物大活動", slots, ass.Dirs(char=month / "去背用", char_month=month))
    src = {s.key: (Path(s.source).name if s.source else s.status) for s in slots}
    assert src["圖示/新手裝-男"] == "01-1.png" and src["圖示/新手裝-女"] == "02-1.png"
    assert src["圖示/儲值裝-女"] == "02-4.png" and src["圖示/BOSS裝2-男"] == "01-6.png"
    assert src["吃碰特效"] == "manual"
    assert next(s for s in slots if s.key == "圖示/新手裝-女").image_name == "02.png"


def test_gift_pack_uses_seq(static_dir: Path) -> None:
    def pack(title: str, m: int, f: int) -> list[dict[str, Any]]:
        return [blk("heading_2", title),
                cols([blk("heading_3", "男"), blk("numbered_list_item", f"seq：{m}"),
                      blk("heading_3", "女"), blk("numbered_list_item", f"seq：{f}")],
                     [blk("heading_3", "前景(共用)"), blk("numbered_list_item", f"seq：{m}"),
                      blk("heading_3", "背景(共用)"), blk("numbered_list_item", f"seq：{f}")]),
                blk("paragraph", "圖示(男女共用)"), img("x.jpg"), blk("divider")]

    tree = [blk("heading_1", "📌本次內容")] + pack("神裝禮包．壹", 4272, 4273) + pack("神裝禮包．貳", 4274, 4275)
    slots, _ = ass.find_slots("神裝禮包", tree, "page")
    ass.assign_sources("神裝禮包", slots, ass.Dirs(static=static_dir))
    assert [Path(s.source).name for s in slots] == ["4272+4273.jpg", "4274+4275.jpg"]


# ------------------------------------------------------------------ comparison
def test_compare_identical_and_reencoded() -> None:
    a = png_bytes((10, 120, 200), level=1)
    b = png_bytes((10, 120, 200), level=9)  # same pixels, different bytes
    assert a != b
    assert ass.compare_bytes(a, a) == (True, 0.0)
    assert ass.compare_bytes(a, b) == (True, 0.0)


def test_compare_changed_image() -> None:
    same, diff = ass.compare_bytes(png_bytes((10, 120, 200)), png_bytes((10, 200, 60)))
    assert not same and diff > ass.SAME_DIFF
