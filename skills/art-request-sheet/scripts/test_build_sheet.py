"""Tests for build_sheet.py: dept1 regression and the dept4-slot layout.

Run: python -m pytest skills/art-request-sheet/scripts/test_build_sheet.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPTS = Path(__file__).resolve().parent
FIXTURES = SCRIPTS / 'test_fixtures'
sys.path.insert(0, str(SCRIPTS))

import build_sheet  # noqa: E402

Json = dict[str, Any]


def load(path: Path) -> Any:
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def run_cli(spec: Path, out: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / 'build_sheet.py'), str(spec), '--out', str(out)],
                          capture_output=True, text=True, encoding='utf-8', check=True)


def requests_of(reqs: list[Json], kind: str, sid: int | None = None) -> list[Json]:
    found = [r[kind] for r in reqs if kind in r]
    if sid is None:
        return found
    return [r for r in found if json.dumps(r).find(f'"sheetId": {sid}') >= 0]


def merges(reqs: list[Json], sid: int) -> set[tuple[int, int, int, int]]:
    out = set()
    for m in requests_of(reqs, 'mergeCells'):
        g = m['range']
        if g['sheetId'] == sid:
            out.add((g['startRowIndex'], g['endRowIndex'], g['startColumnIndex'], g['endColumnIndex']))
    return out


# ---------- dept1 regression ----------

def test_dept1_output_is_byte_identical_to_v1(tmp_path: Path) -> None:
    """values / paste_plan are byte-identical to build_sheet.py v1.0.0; requests.json is the
    merged-dimension version, whose meaning test_dept1_requests_mean_the_same_as_v1 pins to v1."""
    run_cli(FIXTURES / 'dept1_spec.json', tmp_path)
    for name in ('values.json', 'requests.json', 'paste_plan.json'):
        assert (tmp_path / name).read_bytes() == (FIXTURES / 'dept1_expected' / name).read_bytes(), name
    assert not (tmp_path / 'add_sheets.json').exists()
    assert not (tmp_path / 'values_2.json').exists()


def expand_dimensions(reqs: list[Json]) -> list[Json]:
    """Split every multi-index updateDimensionProperties back into one request per row / column."""
    out: list[Json] = []
    for r in reqs:
        dim = r.get('updateDimensionProperties')
        if dim is None:
            out.append(r)
            continue
        rng = dim['range']
        for i in range(rng['startIndex'], rng['endIndex']):
            out.append({'updateDimensionProperties': {**dim, 'range': {**rng, 'startIndex': i, 'endIndex': i + 1}}})
    return out


def test_dept1_requests_mean_the_same_as_v1(tmp_path: Path) -> None:
    """requests_v1_per_index.json is the v1.0.0 requests.json (one dimension request per row / column).
    Expanding the merged ranges must give it back exactly, request by request."""
    run_cli(FIXTURES / 'dept1_spec.json', tmp_path)
    new = load(tmp_path / 'requests.json')
    old = load(FIXTURES / 'dept1_expected' / 'requests_v1_per_index.json')
    assert len(new) < len(old)
    assert expand_dimensions(new) == old


def test_dimension_requests_merge_adjacent_equal_sizes_only() -> None:
    reqs = build_sheet.dimension_requests(7, 'ROWS', [(2, 330), (3, 330), (4, 400), (6, 400), (7, 400)])
    spans = [(r['updateDimensionProperties']['range']['startIndex'],
              r['updateDimensionProperties']['range']['endIndex'],
              r['updateDimensionProperties']['properties']['pixelSize']) for r in reqs]
    assert spans == [(2, 4, 330), (4, 5, 400), (6, 8, 400)]  # gap at 5 breaks the run
    assert all(r['updateDimensionProperties']['range']['dimension'] == 'ROWS' for r in reqs)


def test_spec_without_layout_defaults_to_dept1() -> None:
    spec = load(FIXTURES / 'dept1_spec.json')
    assert 'layout' not in spec
    explicit = build_sheet.build({**spec, 'layout': 'dept1'})
    implicit = build_sheet.build(spec)
    assert explicit == implicit


def test_dept1_rejects_bad_dynamic() -> None:
    with pytest.raises(SystemExit):
        build_sheet.build({'rows': [{'item': 'x', 'dynamic': 'Y', 'desc': ['a']}]})


# ---------- dept4-slot ----------

@pytest.fixture(scope='module')
def slot() -> Json:
    return build_sheet.build(load(FIXTURES / 'dept4_slot_spec.json'))


def test_slot_tabs_and_headers(slot: Json) -> None:
    titles = [t['title'] for t in slot['tabs']]
    assert titles == ['靜態', '動態', '動態命名表', '說明頁']
    static, dynamic, naming, help_tab = (t['values'] for t in slot['tabs'])
    assert static[0] == ['項目', '子項目', '重要度', '動態', '企劃示意圖', '描述', '美術字需求', '參考圖1', '參考圖2']
    assert static[1][0] == 'ETA︰'
    assert dynamic[0] == ['項目', '時機', '企劃示意圖', '描述', '動態參考', '動態參考2']
    assert naming == [['No', '名稱', '動態檔案名稱', '動態檔案裡的ANIMATION NAME', '說明', '秒數',
                       '備註及重要流程描述', '示意圖', '競品參考', '補充']]
    assert help_tab[0] == ['', '標題語言ID', '英文標題', '繁中標題', '翻譯', '中文', '圖片說明']
    assert help_tab[1][3] == '基本玩法'
    assert [t['range'] for t in slot['tabs']] == ['A1:I11', 'A1:F5', 'A1:J1', 'A1:G2']


def test_slot_add_sheets_for_later_tabs_only(slot: Json) -> None:
    assert slot['add_sheets'] == [
        {'addSheet': {'properties': {'sheetId': 910001, 'title': '動態'}}},
        {'addSheet': {'properties': {'sheetId': 910002, 'title': '動態命名表'}}},
        {'addSheet': {'properties': {'sheetId': 910003, 'title': '說明頁'}}},
    ]
    renames = [r['properties'] for r in requests_of(slot['requests'], 'updateSheetProperties')]
    assert [(p['sheetId'], p['title']) for p in renames] == [(0, '靜態'), (910001, '動態'),
                                                             (910002, '動態命名表'), (910003, '說明頁')]
    assert renames[0]['gridProperties'] == {'frozenRowCount': 2}


def test_slot_static_vertical_merges(slot: Json) -> None:
    m = merges(slot['requests'], 0)
    # rows: 2-3 icon group, 4-6 main UI, 7-9 symbols, 10 dialog (0-based)
    assert (2, 4, 0, 1) in m          # A: 機台icon
    assert (4, 7, 0, 1) in m          # A: 主介面
    assert (7, 10, 0, 1) in m         # A: 獎圖
    assert (4, 7, 4, 5) in m          # E: one plan image for the whole 主介面 group
    assert (7, 10, 4, 5) in m         # E: symbols share one plan image
    assert (2, 4, 4, 5) not in m      # icon rows each have their own plan image
    assert (7, 10, 5, 6) in m         # F: empty desc merges up inside the group
    assert (4, 7, 5, 6) not in m      # rows with their own desc are not merged
    assert not any(c0 == 0 and r0 == 10 for r0, _, c0, _ in m)  # single-row group: no merge


def test_slot_dynamic_dropdown_yn(slot: Json) -> None:
    dvs = [d for d in requests_of(slot['requests'], 'setDataValidation') if d['range']['sheetId'] == 0]
    assert len(dvs) == 1
    rng, rule = dvs[0]['range'], dvs[0]['rule']
    assert (rng['startColumnIndex'], rng['endColumnIndex'], rng['startRowIndex'], rng['endRowIndex']) == (3, 4, 2, 11)
    assert [v['userEnteredValue'] for v in rule['condition']['values']] == ['Y', 'N']
    assert rule['strict'] is True
    others = [d for d in requests_of(slot['requests'], 'setDataValidation') if d['range']['sheetId'] != 0]
    assert others == []


def test_slot_header_style(slot: Json) -> None:
    heads = [r['repeatCell'] for r in slot['requests']
             if 'repeatCell' in r and r['repeatCell']['range']['startRowIndex'] == 0
             and r['repeatCell']['range']['endRowIndex'] == 1 and r['repeatCell']['range']['sheetId'] == 0]
    fmt = heads[0]['cell']['userEnteredFormat']
    assert fmt['backgroundColor'] == build_sheet.rgb('#4A86E8')
    assert fmt['textFormat']['foregroundColorStyle']['rgbColor'] == build_sheet.rgb('#FFFFFF')
    assert 'userEnteredFormat.textFormat.foregroundColorStyle' in heads[0]['fields']


def test_slot_group_separator_borders(slot: Json) -> None:
    bottoms = [b['range']['startRowIndex'] for b in requests_of(slot['requests'], 'updateBorders')
               if b['range']['sheetId'] == 0]
    assert bottoms == [3, 6, 9, 10]
    b = requests_of(slot['requests'], 'updateBorders')[0]
    assert b['bottom']['style'] == 'DOUBLE' and 'innerHorizontal' not in b


def test_slot_red_text_and_paste_plan(slot: Json) -> None:
    runs = [r['updateCells'] for r in slot['requests'] if 'updateCells' in r]
    assert len(runs) == 1 and runs[0]['start'] == {'sheetId': 0, 'rowIndex': 5, 'columnIndex': 5}
    plan = slot['plan']
    assert {'tab': '靜態', 'cell': 'E3', 'file': 'r01.png'} in plan
    assert {'tab': '靜態', 'cell': 'H6', 'file': 'r04.png'} in plan
    assert {'tab': '靜態', 'cell': 'I6', 'file': 'r05.png'} in plan
    assert {'tab': '動態', 'cell': 'E5', 'file': 'r10.gif'} in plan
    assert {'tab': '說明頁', 'cell': 'G2', 'file': 'r11.png'} in plan
    assert all('tab' in p for p in plan)


def test_slot_art_text_is_plain_lines(slot: Json) -> None:
    static = slot['tabs'][0]['values']
    assert static[10][6] == '1.文字：恭喜\n2.按鈕文字：開始'


def test_slot_cli_writes_one_values_file_per_tab(tmp_path: Path) -> None:
    proc = run_cli(FIXTURES / 'dept4_slot_spec.json', tmp_path)
    names = sorted(p.name for p in tmp_path.iterdir())
    assert names == ['add_sheets.json', 'paste_plan.json', 'requests.json', 'values.json',
                     'values_2.json', 'values_3.json', 'values_4.json']
    assert load(tmp_path / 'values_3.json')[0][0] == 'No'
    assert "'動態'!A1:F5" in proc.stdout


def test_slot_default_sheet_ids_and_duplicates() -> None:
    spec = {'layout': 'dept4-slot', 'tabs': [{'tab': 'static', 'rows': []}, {'tab': 'dynamic', 'rows': []}]}
    out = build_sheet.build(spec)
    assert [t['sheet_id'] for t in out['tabs']] == [0, 910001]
    with pytest.raises(SystemExit):
        build_sheet.build({'layout': 'dept4-slot', 'tabs': [{'tab': 'static', 'sheet_id': 5, 'rows': []},
                                                            {'tab': 'dynamic', 'sheet_id': 5, 'rows': []}]})


def test_slot_rejects_o_x_and_unknown_tab() -> None:
    with pytest.raises(SystemExit):
        build_sheet.build({'layout': 'dept4-slot', 'tabs': [{'tab': 'static', 'rows': [
            {'item': 'a', 'dynamic': 'O', 'desc': ['x']}]}]})
    with pytest.raises(SystemExit):
        build_sheet.build({'layout': 'dept4-slot', 'tabs': [{'tab': 'nope', 'rows': []}]})


def test_layouts_have_no_hardcoded_names() -> None:
    """The kit is public: layouts must not carry real machine names or sheet ids."""
    text = ''.join(p.read_text(encoding='utf-8') for p in (SCRIPTS / 'layouts').glob('*.json'))
    text += (SCRIPTS / 'test_fixtures' / 'dept4_slot_spec.json').read_text(encoding='utf-8')
    for banned in ('docs.google.com', 'notion.so', 'notion.com'):
        assert banned not in text


# ---------- thumbnail boxes and image row heights ----------

def row_heights(reqs: list[Json], sid: int) -> dict[int, int]:
    out: dict[int, int] = {}
    for r in expand_dimensions(reqs):
        d = r.get('updateDimensionProperties')
        if d and d['range']['dimension'] == 'ROWS' and d['range']['sheetId'] == sid:
            out[d['range']['startIndex']] = d['properties']['pixelSize']
    return out


def test_dept1_thumb_box_stays_530x300() -> None:
    layout = build_sheet.load_layout('dept1')
    boxes = {build_sheet.thumb_box(c) for c in layout['tabs'][0]['columns'] if c['kind'] == 'ref'}
    assert boxes == {(530, 300)}
    assert build_sheet.layout_min_box(layout) == (530, 300)
    per_file = build_sheet.file_boxes(load(FIXTURES / 'dept1_spec.json'), layout)
    assert per_file and set(per_file.values()) == {(530, 300)}


def test_dept4_thumb_box_follows_column() -> None:
    layout = build_sheet.load_layout('dept4-slot')
    spec = {'layout': 'dept4-slot', 'tabs': [
        {'tab': 'static', 'rows': [{'item': 'a', 'plan_image': 'r01.png', 'refs': ['r02.png']}]},
        {'tab': 'dynamic', 'rows': [{'item': 'b', 'plan_image': 'r01.png', 'refs': ['r03.gif']}]},
        {'tab': 'help', 'rows': [{'page': 'P1', 'plan_image': 'r04.png'}]}]}
    boxes = build_sheet.file_boxes(spec, layout)
    assert boxes['r01.png'] == (360, 300)   # static 400px and dynamic 380px: the tighter one
    assert boxes['r02.png'] == (280, 300)   # static ref column 300px
    assert boxes['r03.gif'] == (180, 300)   # dynamic ref column 200px
    assert boxes['r04.png'] == (430, 300)   # help image column 450px
    assert build_sheet.fit_size(1920, 1080, boxes['r04.png']) == (430, 241)
    assert build_sheet.fit_size(100, 50, boxes['r04.png']) == (100, 50)  # never scaled up


def test_thumb_box_default_without_layout_thumb() -> None:
    assert build_sheet.thumb_box({'width': 250, 'kind': 'ref'}) == (230, 300)


def test_image_row_uses_box_height_when_file_unknown() -> None:
    spec = {'layout': 'dept4-slot', 'tabs': [{'tab': 'static', 'rows': [
        {'item': 'a', 'desc': ['x'], 'plan_image': 'r01.png'},
        {'item': 'b', 'desc': ['x']}]}]}
    h = row_heights(build_sheet.build(spec)['requests'], 0)
    assert h[2] == 300 + build_sheet.IMG_ROW_PAD   # box height, file not readable
    assert h[3] == 60                              # text-only row keeps min_px


def test_image_row_uses_real_size(tmp_path: Path) -> None:
    from PIL import Image
    Image.new('RGB', (760, 300)).save(tmp_path / 'r01.png')   # fits 380x300 as 380x150
    Image.new('RGB', (100, 40)).save(tmp_path / 'r02.png')    # ref smaller than min_px
    spec = {'layout': 'dept4-slot', 'tabs': [{'tab': 'static', 'rows': [
        {'item': 'a', 'desc': ['x'], 'plan_image': 'r01.png', 'refs': ['r02.png']},
        {'item': 'b', 'desc': ['x'], 'refs': ['r02.png']}]}]}
    h = row_heights(build_sheet.build(spec, images_dir=tmp_path)['requests'], 0)
    assert h[2] == 150 + build_sheet.IMG_ROW_PAD
    assert h[3] == 60


def test_shared_image_height_spreads_over_merged_rows() -> None:
    rows = [{'item': 'g', 'sub': 'A', 'desc': ['x'], 'plan_image': 'r01.png'},
            {'sub': 'B', 'desc': ['y']}, {'sub': 'C', 'desc': ['z']}]
    out = build_sheet.build({'layout': 'dept4-slot', 'tabs': [{'tab': 'static', 'rows': rows}]})
    assert (2, 5, 4, 5) in merges(out['requests'], 0)   # E column merged over the three rows
    h = row_heights(out['requests'], 0)
    assert sum(h[r] for r in (2, 3, 4)) >= 300 + build_sheet.IMG_ROW_PAD
    assert h[2] == h[3] == h[4] == 104                    # 60 each + ceil((310 - 180) / 3)


def test_tall_text_row_is_not_lowered_by_image() -> None:
    long_desc = ['字' * 32] * 30   # 30 lines * 17 + 30 = 540 px
    spec = {'layout': 'dept4-slot', 'tabs': [{'tab': 'static', 'rows': [
        {'item': 'a', 'desc': long_desc, 'plan_image': 'r01.png'}]}]}
    assert row_heights(build_sheet.build(spec)['requests'], 0)[2] == 540


def test_slot_requests_merge_dimensions(slot: Json) -> None:
    cols = [r['updateDimensionProperties'] for r in slot['requests'] if 'updateDimensionProperties' in r
            and r['updateDimensionProperties']['range']['dimension'] == 'COLUMNS'
            and r['updateDimensionProperties']['range']['sheetId'] == 0]
    # static widths 100 120 50 40 400 450 150 300 300: only H:I share a size
    assert len(cols) == 8
    assert (cols[-1]['range']['startIndex'], cols[-1]['range']['endIndex']) == (7, 9)
