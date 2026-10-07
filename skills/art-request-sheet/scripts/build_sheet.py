"""Build the art request sheet payloads from a content spec and a layout.

The sheet format (tabs, headers, colours, widths, dropdowns, merges) lives in
scripts/layouts/<name>.json, not in this file. Pick it with the spec key
"layout" ("dept1" when omitted, so old specs still work).

Spec, single tab (the original dept1 form, still accepted):
{
  "layout": "dept1",                        // optional, default "dept1"
  "sheet_id": 0,
  "tab_title": "美術需求表",                 // optional, overrides the layout title
  "rows": [
    {
      "item": "主介面—活動進行中",
      "dynamic": "X",                       // must be one of the layout's dropdown values
      "art_text": ["活動標題"],              // dept1: omit by default (column stays empty)
      "desc": [
        "1. 返回鍵",
        "12. {按鈕}：",                     // {...} = red text
        "    c. 單次花費：小轉盤 {500}"
      ],
      "refs": ["r05.png", "r06.png"]        // optional, pasted into the ref columns in order
    }
  ]
}

Spec, several tabs (e.g. layout "dept4-slot"):
{
  "layout": "dept4-slot",
  "tabs": [
    {"tab": "static",  "sheet_id": 0,      "rows": [...]},   // 1st tab: the existing blank tab
    {"tab": "dynamic", "sheet_id": 910001, "rows": [...]},   // later tabs: created by addSheet
    {"tab": "naming",  "rows": []}                           // no rows = header only
  ]
}
"tab" is a tab key of the layout (see the layout file). Row keys are the
column "key"s of that tab. Layout-specific row rules:
  - item left empty  -> the row continues the previous item group; columns
    listed in the tab's "vmerge" are merged vertically inside the group
    (item always; image/desc columns merge while their value is empty)
  - "plan_image": "r03.png" -> pasted into that tab's image column
  - {"section": "獎圖"} -> a full-width section row (only tabs with a "section" style)

Later tabs and their sheet ids: the first tab reuses the existing tab
(sheet_id from get_spreadsheet). Every later tab is created by addSheet with
the sheet_id written in the spec; when omitted, the script assigns
910000 + tab index. Check get_spreadsheet first that the ids are free. The
reply of the addSheet call (replies[i].addSheet.properties.sheetId) must equal
those ids; if Sheets refuses an id or returns a different one, put the real id
into tabs[i].sheet_id and rerun this script before sending requests.json.

Outputs in --out:
  add_sheets.json  (only with 2+ tabs) addSheet requests, send FIRST in one
                   update_spreadsheet call
  values.json      2D array for update_values on the 1st tab, written to the
                   tab's CURRENT name (e.g. '工作表1'!A1:I<n>)
  values_<k>.json  2D array for tab k (k = 2, 3, ...), written to the title
                   printed in the summary (addSheet already set it)
  requests.json    one update_spreadsheet call for all tabs: rename, freeze,
                   fonts, colours, merges, dropdowns, borders, widths,
                   heights, red text runs
  paste_plan.json  [{"cell": "G6", "file": "r05.png"}, ...]; with 2+ tabs each
                   entry also has "tab": <tab title>

Order: add_sheets.json -> every values file -> requests.json -> paste images.
The red text runs apply to written text, so requests.json goes after values.

Usage: python build_sheet.py spec.json --out <dir>
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any

LONG_PREFIX = '\\\\?\\'
LAYOUT_DIR = Path(__file__).resolve().parent / 'layouts'
DEFAULT_LAYOUT = 'dept1'
NEW_SHEET_ID_BASE = 910000
BLACK = {'red': 0, 'green': 0, 'blue': 0}
RED = {'red': 1, 'green': 0, 'blue': 0}

Json = dict[str, Any]


def lp(path: str) -> str:
    """Prefix long Windows paths so open() works past the 260-char limit."""
    path = os.path.abspath(path)
    if os.name == 'nt' and len(path) >= 240 and not path.startswith(LONG_PREFIX):
        return LONG_PREFIX + path.replace('/', '\\')
    return path


def rgb(hex_color: str) -> Json:
    """'#E2EFD9' -> Sheets colour dict (same float maths as the old constants)."""
    h = hex_color.lstrip('#')
    return {'red': int(h[0:2], 16) / 255, 'green': int(h[2:4], 16) / 255, 'blue': int(h[4:6], 16) / 255}


def col_letter(index: int) -> str:
    """0-based column index -> A1 letters."""
    letters = ''
    index += 1
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def load_layout(name: str) -> Json:
    """Load scripts/layouts/<name>.json, or a .json path."""
    path = Path(name) if name.endswith('.json') else LAYOUT_DIR / f'{name}.json'
    if not path.is_file():
        known = ', '.join(sorted(p.stem for p in LAYOUT_DIR.glob('*.json')))
        sys.exit(f'unknown layout "{name}" (known: {known})')
    with open(lp(str(path)), encoding='utf-8') as fh:
        return json.load(fh)


def parse_red(lines: list[str]) -> tuple[str, list[tuple[int, int]]]:
    """Join lines and strip {..} markers; return text and red (start, end) spans."""
    raw = '\n'.join(lines)
    text, spans = '', []
    for part in re.split(r'(\{[^{}]*\})', raw):
        if part.startswith('{') and part.endswith('}'):
            body = part[1:-1]
            spans.append((len(text), len(text) + len(body)))
            text += body
        else:
            text += part
    if any(ord(ch) > 0xFFFF for ch in text):
        sys.exit('desc contains characters outside the BMP; run indexes would be off')
    return text, spans


def runs_for(text: str, spans: list[tuple[int, int]]) -> list[Json]:
    """Turn red spans into textFormatRuns (black elsewhere)."""
    runs: list[Json] = []
    for start, end in spans:
        if not runs and start > 0:
            runs.append({'startIndex': 0, 'format': {'foregroundColorStyle': {'rgbColor': BLACK}}})
        if runs and runs[-1]['startIndex'] == start:
            runs.pop()  # adjacent red spans: drop the zero-length black run
        runs.append({'startIndex': start, 'format': {'foregroundColorStyle': {'rgbColor': RED}}})
        if end < len(text):
            runs.append({'startIndex': end, 'format': {'foregroundColorStyle': {'rgbColor': BLACK}}})
    return runs


def row_height(text: str, cfg: Json) -> int:
    """Estimate a row height in px from the wrapped line count."""
    per_line = cfg['chars_per_line']
    lines = sum(max(1, math.ceil(len(line.rstrip()) / per_line)) for line in text.split('\n'))
    return max(cfg['min_px'], lines * cfg['line_px'] + 30)


def grid(sid: int, r0: int, r1: int, c0: int, c1: int) -> Json:
    return {'sheetId': sid, 'startRowIndex': r0, 'endRowIndex': r1, 'startColumnIndex': c0, 'endColumnIndex': c1}


def as_lines(value: Any) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def is_empty(value: Any) -> bool:
    return value is None or value == '' or value == []


def normalize_spec(spec: Json, layout: Json) -> list[Json]:
    """Return the list of tab specs; the old single-tab form becomes one tab."""
    if 'tabs' in spec:
        tabs = spec['tabs']
    else:
        tab = {'tab': layout['tabs'][0]['key'], 'sheet_id': spec.get('sheet_id', 0), 'rows': spec['rows']}
        if 'tab_title' in spec:
            tab['tab_title'] = spec['tab_title']
        tabs = [tab]
    if not tabs:
        sys.exit('spec has no tabs')
    return tabs


def cell_value(col: Json, row: Json, tab_cfg: Json, row_no: int) -> str:
    """Plain cell text for one column of one content row."""
    kind = col['kind']
    key = col.get('key')
    if kind in ('blank', 'ref', 'image'):
        return ''
    if kind == 'text':
        value = row.get(key, '')
        return '\n'.join(value) if isinstance(value, list) else str(value)
    if kind == 'dynamic':
        dyn_cfg = tab_cfg['dynamic']
        value = row.get(key, dyn_cfg['default'])
        allowed = list(dyn_cfg['values']) + ([''] if dyn_cfg['default'] == '' else [])
        if value not in allowed:
            sys.exit(f"row {row_no}: {key} must be one of {'/'.join(dyn_cfg['values'])}")
        return value
    if kind == 'art_text':
        art = row.get(key) or []
        return '\n'.join(f'{k + 1}. {t}' for k, t in enumerate(art)) if len(art) > 1 else ''.join(art)
    if kind == 'desc':
        return parse_red(as_lines(row.get(key)))[0]
    sys.exit(f'unknown column kind "{kind}"')


def find_groups(rows: list[Json], group_key: str) -> list[list[int]]:
    """Split content rows into item groups (indexes into rows); sections stand alone."""
    groups: list[list[int]] = []
    for i, row in enumerate(rows):
        if 'section' in row:
            groups.append([i])
            continue
        prev_section = bool(groups) and 'section' in rows[groups[-1][0]]
        if not groups or prev_section or not is_empty(row.get(group_key)):
            groups.append([i])
        else:
            groups[-1].append(i)
    return groups


def build_tab(tab_spec: Json, tab_cfg: Json, layout: Json, sid: int
              ) -> tuple[list[list[str]], list[Json], list[Json], int, str]:
    """Build values, requests and paste plan for one tab."""
    cols = tab_cfg['columns']
    ncols = len(cols)
    rows = tab_spec.get('rows', [])
    title = tab_spec.get('tab_title', tab_cfg['title'])
    row2 = tab_cfg.get('row2')
    start = 2 if row2 else 1
    n = len(rows) + start
    group_key = tab_cfg.get('group_key', 'item')
    values: list[list[str]] = [[c['header'] for c in cols]]
    if row2:
        values.append([row2.get('text', '')] + [''] * (ncols - 1))
    requests: list[Json] = []
    run_reqs: list[Json] = []
    heights: list[tuple[int, int]] = []
    plan: list[Json] = []
    ref_cols = sorted((c['ref'], i) for i, c in enumerate(cols) if c['kind'] == 'ref')
    image_cols = [(i, c['key']) for i, c in enumerate(cols) if c['kind'] == 'image']
    height_cfg = tab_cfg['row_height']
    section_rows: list[int] = []

    for i, row in enumerate(rows):
        r = i + start  # 0-based row index
        if 'section' in row:
            values.append([str(row['section'])] + [''] * (ncols - 1))
            section_rows.append(r)
            continue
        values.append([cell_value(c, row, tab_cfg, r + 1) for c in cols])
        height_text = ''
        for c_idx, col in enumerate(cols):
            if col['kind'] != 'desc':
                continue
            text, spans = parse_red(as_lines(row.get(col['key'])))
            if col['key'] == height_cfg['key']:
                height_text = text
            if spans:
                run_reqs.append({'updateCells': {
                    'rows': [{'values': [{'textFormatRuns': runs_for(text, spans)}]}],
                    'fields': 'textFormatRuns',
                    'start': {'sheetId': sid, 'rowIndex': r, 'columnIndex': c_idx}}})
        heights.append((r, row_height(height_text, height_cfg)))
        for c_idx, key in image_cols:
            if row.get(key):
                plan.append({'cell': f'{col_letter(c_idx)}{r + 1}', 'file': row[key]})
        refs = row.get('refs', [])
        if len(refs) > len(ref_cols):
            print(f'warning: row {r + 1} has {len(refs)} refs, only {len(ref_cols)} ref columns', file=sys.stderr)
        for (_, c_idx), f in zip(ref_cols, refs):
            plan.append({'cell': f'{col_letter(c_idx)}{r + 1}', 'file': f})

    full = grid(sid, 0, n, 0, ncols)
    props: Json = {'sheetId': sid, 'title': title}
    fields = 'title'
    if tab_cfg.get('freeze_rows'):
        props['gridProperties'] = {'frozenRowCount': tab_cfg['freeze_rows']}
        fields += ',gridProperties.frozenRowCount'
    requests.append({'updateSheetProperties': {'properties': props, 'fields': fields}})

    body_font = tab_cfg.get('body_font', layout.get('body_font'))
    body_fmt: Json = {}
    body_fields: list[str] = []
    if body_font:
        body_fmt['textFormat'] = {'fontFamily': body_font['family'], 'fontSize': body_font['size']}
        body_fields += ['userEnteredFormat.textFormat.fontFamily', 'userEnteredFormat.textFormat.fontSize']
    body_fmt.update({'wrapStrategy': 'WRAP', 'verticalAlignment': 'MIDDLE'})
    body_fields += ['userEnteredFormat.wrapStrategy', 'userEnteredFormat.verticalAlignment']
    requests.append({'repeatCell': {'range': full, 'cell': {'userEnteredFormat': body_fmt},
                                    'fields': ','.join(body_fields)}})

    head = tab_cfg['header']
    head_text: Json = {'bold': head.get('bold', False),
                       'fontFamily': head.get('font_family', body_font['family'] if body_font else 'Arial'),
                       'fontSize': head.get('font_size', body_font['size'] if body_font else 10)}
    head_fields = ['userEnteredFormat.backgroundColor', 'userEnteredFormat.textFormat.bold']
    if 'font_family' in head:
        head_fields.append('userEnteredFormat.textFormat.fontFamily')
    if 'font_size' in head:
        head_fields.append('userEnteredFormat.textFormat.fontSize')
    if 'fg' in head:
        head_text['foregroundColorStyle'] = {'rgbColor': rgb(head['fg'])}
        head_fields.append('userEnteredFormat.textFormat.foregroundColorStyle')
    head_fields.append('userEnteredFormat.horizontalAlignment')
    requests.append({'repeatCell': {'range': grid(sid, 0, 1, 0, ncols), 'cell': {'userEnteredFormat': {
        'backgroundColor': rgb(head['bg']), 'textFormat': head_text, 'horizontalAlignment': 'CENTER'}},
        'fields': ','.join(head_fields)}})
    for c_idx, col in enumerate(cols):
        if 'header_bg' in col:
            requests.append({'repeatCell': {'range': grid(sid, 0, 1, c_idx, c_idx + 1),
                                            'cell': {'userEnteredFormat': {'backgroundColor': rgb(col['header_bg'])}},
                                            'fields': 'userEnteredFormat.backgroundColor'}})

    if row2:
        requests.append({'repeatCell': {'range': grid(sid, 1, 2, 0, ncols),
                                        'cell': {'userEnteredFormat': {'backgroundColor': rgb(row2['bg'])}},
                                        'fields': 'userEnteredFormat.backgroundColor'}})
        if row2.get('merge_cols'):
            c0, c1 = row2['merge_cols']
            requests.append({'mergeCells': {'range': grid(sid, 1, 2, c0, c1), 'mergeType': 'MERGE_ALL'}})

    if rows:
        for c_idx, col in enumerate(cols):
            if col.get('center'):
                requests.append({'repeatCell': {'range': grid(sid, start, n, c_idx, c_idx + 1),
                                                'cell': {'userEnteredFormat': {'horizontalAlignment': 'CENTER'}},
                                                'fields': 'userEnteredFormat.horizontalAlignment'}})
        for c_idx, col in enumerate(cols):
            if col['kind'] == 'dynamic':
                requests.append({'setDataValidation': {'range': grid(sid, start, n, c_idx, c_idx + 1), 'rule': {
                    'condition': {'type': 'ONE_OF_LIST',
                                  'values': [{'userEnteredValue': v} for v in tab_cfg['dynamic']['values']]},
                    'strict': True, 'showCustomUi': True}}})

    groups = find_groups(rows, group_key)
    borders = tab_cfg.get('borders', 'all')
    line = {'style': 'SOLID', 'color': BLACK}
    if borders == 'all':
        requests.append({'updateBorders': {'range': full, 'top': line, 'bottom': line, 'left': line, 'right': line,
                                           'innerHorizontal': line, 'innerVertical': line}})
    elif borders == 'group_bottom':
        sep = {'style': tab_cfg.get('group_border_style', 'DOUBLE'), 'color': BLACK}
        for g in groups:
            last = g[-1] + start
            requests.append({'updateBorders': {'range': grid(sid, last, last + 1, 0, ncols), 'bottom': sep}})

    for c_idx, col in enumerate(cols):
        requests.append({'updateDimensionProperties': {
            'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': c_idx, 'endIndex': c_idx + 1},
            'properties': {'pixelSize': col['width']}, 'fields': 'pixelSize'}})
    for r, h in heights:
        requests.append({'updateDimensionProperties': {
            'range': {'sheetId': sid, 'dimension': 'ROWS', 'startIndex': r, 'endIndex': r + 1},
            'properties': {'pixelSize': h}, 'fields': 'pixelSize'}})

    section = tab_cfg.get('section')
    for r in section_rows:
        if not section:
            sys.exit(f'tab "{tab_cfg["key"]}" has no section style; row {r + 1} cannot be a section')
        requests.append({'repeatCell': {'range': grid(sid, r, r + 1, 0, ncols), 'cell': {'userEnteredFormat': {
            'backgroundColor': rgb(section['bg']),
            'textFormat': {'bold': True, 'foregroundColorStyle': {'rgbColor': rgb(section['fg'])}}}},
            'fields': 'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.bold,'
                      'userEnteredFormat.textFormat.foregroundColorStyle'}})

    key_cols = {c['key']: i for i, c in enumerate(cols) if c.get('key')}
    for key in tab_cfg.get('vmerge', []):
        c_idx = key_cols[key]
        for g in groups:
            if 'section' in rows[g[0]]:
                continue
            runs: list[list[int]] = []
            for i in g:
                if not runs or (key != group_key and not is_empty(rows[i].get(key))):
                    runs.append([i])
                else:
                    runs[-1].append(i)
            for run in runs:
                if len(run) > 1:
                    requests.append({'mergeCells': {'range': grid(sid, run[0] + start, run[-1] + start + 1,
                                                                  c_idx, c_idx + 1), 'mergeType': 'MERGE_ALL'}})

    return values, requests + run_reqs, plan, n, title


def build(spec: Json, layout: Json | None = None) -> Json:
    """Return {'tabs': [...], 'add_sheets': [...], 'requests': [...], 'plan': [...]}."""
    if layout is None:
        layout = load_layout(spec.get('layout', DEFAULT_LAYOUT))
    cfg_by_key = {t['key']: t for t in layout['tabs']}
    tabs = normalize_spec(spec, layout)
    multi = len(tabs) > 1
    out: Json = {'tabs': [], 'add_sheets': [], 'requests': [], 'plan': []}
    seen_ids: set[int] = set()
    for k, tab_spec in enumerate(tabs):
        if tab_spec['tab'] not in cfg_by_key:
            sys.exit(f'layout "{layout["name"]}" has no tab "{tab_spec["tab"]}" (has: {", ".join(cfg_by_key)})')
        tab_cfg = cfg_by_key[tab_spec['tab']]
        sid = tab_spec.get('sheet_id', 0 if k == 0 else NEW_SHEET_ID_BASE + k)
        if sid in seen_ids:
            sys.exit(f'duplicate sheet_id {sid}')
        seen_ids.add(sid)
        values, requests, plan, n, title = build_tab(tab_spec, tab_cfg, layout, sid)
        if k > 0:
            out['add_sheets'].append({'addSheet': {'properties': {'sheetId': sid, 'title': title}}})
        if multi:
            plan = [{'tab': title, **p} for p in plan]
        out['tabs'].append({'title': title, 'sheet_id': sid, 'values': values, 'rows': n,
                            'range': f'A1:{col_letter(len(tab_cfg["columns"]) - 1)}{n}'})
        out['requests'] += requests
        out['plan'] += plan
    return out


def write_json(path: str, obj: Any) -> None:
    with open(lp(path), 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, separators=(',', ':'))


def main() -> None:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    with open(lp(args.spec), encoding='utf-8') as fh:
        spec = json.load(fh)
    result = build(spec)
    os.makedirs(lp(args.out), exist_ok=True)
    tabs = result['tabs']
    if result['add_sheets']:
        write_json(os.path.join(args.out, 'add_sheets.json'), result['add_sheets'])
    for k, tab in enumerate(tabs):
        name = 'values.json' if k == 0 else f'values_{k + 1}.json'
        write_json(os.path.join(args.out, name), tab['values'])
    write_json(os.path.join(args.out, 'requests.json'), result['requests'])
    write_json(os.path.join(args.out, 'paste_plan.json'), result['plan'])
    if result['add_sheets']:
        ids = ', '.join(f"{t['title']}={t['sheet_id']}" for t in tabs[1:])
        print(f'step 1: send add_sheets.json first (reply sheetIds must be {ids})')
    for k, tab in enumerate(tabs):
        name = 'values.json' if k == 0 else f'values_{k + 1}.json'
        where = '<current tab name>' if k == 0 else f"'{tab['title']}'"
        print(f"values: {name} -> {where}!{tab['range']}  (tab {tab['title']}, sheetId {tab['sheet_id']})")
    print(f"requests: {len(result['requests'])}  paste: {len(result['plan'])} images")
    for p in result['plan']:
        prefix = f"{p['tab']}!" if 'tab' in p else ''
        print(f"  {prefix}{p['cell']:<4} <- {p['file']}")


if __name__ == '__main__':
    main()
