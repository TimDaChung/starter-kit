"""Build the art request sheet payloads from a content spec.

Spec (JSON, UTF-8):
{
  "sheet_id": 0,
  "rows": [
    {
      "item": "主介面—活動進行中",
      "dynamic": "X",                       // "O" or "X"
      "art_text": ["活動標題"],      // omit by default (column F stays empty); only when the user asks
      "desc": [
        "1. 返回鍵",
        "    a. 子項",
        "12. {按鈕}：",                        // {...} = red text
        "    c. 單次花費：小轉盤 {500}"
      ],
      "refs": ["r05.png", "r06.png"]          // optional, pasted into G, H, I in order
    }
  ]
}

Outputs in --out:
  values.json      2D array for update_values, range A1:I<n>
  requests.json    requests for one update_spreadsheet call (tab rename to
                   「美術需求表」, format, merge, dropdown, borders, widths,
                   heights, red text runs)
  paste_plan.json  [{"cell": "G6", "file": "r05.png"}, ...]
and prints a short summary with the A1 range to write.

Order matters: write values.json first (to the tab's current name, e.g.
'工作表1'!A1:I<n>), then send requests.json. The red text runs apply to the
written text, and the rename comes with the formatting. Optional spec key
"tab_title" overrides the tab name.

Usage: python build_sheet.py spec.json --out <dir>
"""
import argparse
import json
import math
import os
import re
import sys

LONG_PREFIX = '\\\\?\\'


def lp(path):
    """Prefix long Windows paths so open() works past the 260-char limit."""
    path = os.path.abspath(path)
    if os.name == 'nt' and len(path) >= 240 and not path.startswith(LONG_PREFIX):
        return LONG_PREFIX + path.replace('/', '\\')
    return path


TAB_TITLE = '美術需求表'
HEADER = ['項目', '子項目', '是否有動態', '美術設計圖', '設計描述', '美術字', '參考圖1', '參考圖2', '參考圖3']
COL_WIDTHS = [220, 50, 75, 75, 600, 140, 550, 550, 550]
HEADER_BG = {'red': 0xE2 / 255, 'green': 0xEF / 255, 'blue': 0xD9 / 255}
DIVIDER_BG = {'red': 0x93 / 255, 'green': 0xC4 / 255, 'blue': 0x7D / 255}
BLACK = {'red': 0, 'green': 0, 'blue': 0}
RED = {'red': 1, 'green': 0, 'blue': 0}
FONT = 'Microsoft JhengHei'
MIN_ROW_PX = 330
CHARS_PER_LINE = 44   # about 600px of 10pt CJK text
LINE_PX = 17
REF_COLS = 'GHI'


def parse_red(lines):
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


def runs_for(text, spans):
    runs = []
    for start, end in spans:
        if not runs and start > 0:
            runs.append({'startIndex': 0, 'format': {'foregroundColorStyle': {'rgbColor': BLACK}}})
        if runs and runs[-1]['startIndex'] == start:
            runs.pop()  # adjacent red spans: drop the zero-length black run
        runs.append({'startIndex': start, 'format': {'foregroundColorStyle': {'rgbColor': RED}}})
        if end < len(text):
            runs.append({'startIndex': end, 'format': {'foregroundColorStyle': {'rgbColor': BLACK}}})
    return runs


def row_height(text):
    lines = sum(max(1, math.ceil(len(line.rstrip()) / CHARS_PER_LINE)) for line in text.split('\n'))
    return max(MIN_ROW_PX, lines * LINE_PX + 30)


def grid(sid, r0, r1, c0, c1):
    return {'sheetId': sid, 'startRowIndex': r0, 'endRowIndex': r1, 'startColumnIndex': c0, 'endColumnIndex': c1}


def build(spec):
    sid = spec.get('sheet_id', 0)
    rows = spec['rows']
    n = len(rows) + 2
    values = [HEADER, [''] * 9]
    requests, run_reqs, heights, plan = [], [], [], []

    for i, row in enumerate(rows):
        r = i + 2  # 0-based row index
        text, spans = parse_red(row['desc'])
        art = row.get('art_text') or []
        art_text = '\n'.join(f'{k + 1}. {t}' for k, t in enumerate(art)) if len(art) > 1 else ''.join(art)
        dyn = row.get('dynamic', 'X')
        if dyn not in ('O', 'X'):
            sys.exit(f'row {r + 1}: dynamic must be O or X')
        values.append([row['item'], row.get('sub', ''), dyn, '', text, art_text, '', '', ''])
        heights.append(row_height(text))
        if spans:
            run_reqs.append({'updateCells': {
                'rows': [{'values': [{'textFormatRuns': runs_for(text, spans)}]}],
                'fields': 'textFormatRuns',
                'start': {'sheetId': sid, 'rowIndex': r, 'columnIndex': 4}}})
        for k, f in enumerate(row.get('refs', [])[:3]):
            plan.append({'cell': f'{REF_COLS[k]}{r + 1}', 'file': f})

    full = grid(sid, 0, n, 0, 9)
    line = {'style': 'SOLID', 'color': BLACK}
    requests += [
        {'updateSheetProperties': {'properties': {'sheetId': sid, 'title': spec.get('tab_title', TAB_TITLE)},
                                   'fields': 'title'}},
        {'repeatCell': {'range': full, 'cell': {'userEnteredFormat': {
            'textFormat': {'fontFamily': FONT, 'fontSize': 10}, 'wrapStrategy': 'WRAP', 'verticalAlignment': 'MIDDLE'}},
            'fields': 'userEnteredFormat.textFormat.fontFamily,userEnteredFormat.textFormat.fontSize,'
                      'userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment'}},
        {'repeatCell': {'range': grid(sid, 0, 1, 0, 9), 'cell': {'userEnteredFormat': {
            'backgroundColor': HEADER_BG, 'textFormat': {'bold': True, 'fontFamily': FONT, 'fontSize': 10},
            'horizontalAlignment': 'CENTER'}},
            'fields': 'userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.bold,userEnteredFormat.horizontalAlignment'}},
        {'repeatCell': {'range': grid(sid, 1, 2, 0, 9), 'cell': {'userEnteredFormat': {'backgroundColor': DIVIDER_BG}},
                        'fields': 'userEnteredFormat.backgroundColor'}},
        {'mergeCells': {'range': grid(sid, 1, 2, 0, 8), 'mergeType': 'MERGE_ALL'}},
        {'repeatCell': {'range': grid(sid, 2, n, 0, 1), 'cell': {'userEnteredFormat': {'horizontalAlignment': 'CENTER'}},
                        'fields': 'userEnteredFormat.horizontalAlignment'}},
        {'repeatCell': {'range': grid(sid, 2, n, 2, 3), 'cell': {'userEnteredFormat': {'horizontalAlignment': 'CENTER'}},
                        'fields': 'userEnteredFormat.horizontalAlignment'}},
        {'setDataValidation': {'range': grid(sid, 2, n, 2, 3), 'rule': {
            'condition': {'type': 'ONE_OF_LIST', 'values': [{'userEnteredValue': 'O'}, {'userEnteredValue': 'X'}]},
            'strict': True, 'showCustomUi': True}}},
        {'updateBorders': {'range': full, 'top': line, 'bottom': line, 'left': line, 'right': line,
                           'innerHorizontal': line, 'innerVertical': line}},
    ]
    for c, w in enumerate(COL_WIDTHS):
        requests.append({'updateDimensionProperties': {
            'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': c, 'endIndex': c + 1},
            'properties': {'pixelSize': w}, 'fields': 'pixelSize'}})
    for i, h in enumerate(heights):
        requests.append({'updateDimensionProperties': {
            'range': {'sheetId': sid, 'dimension': 'ROWS', 'startIndex': i + 2, 'endIndex': i + 3},
            'properties': {'pixelSize': h}, 'fields': 'pixelSize'}})
    return values, requests + run_reqs, plan, n


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('spec')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    spec = json.load(open(lp(args.spec), encoding='utf-8'))
    values, requests, plan, n = build(spec)
    os.makedirs(lp(args.out), exist_ok=True)
    for name, obj in (('values.json', values), ('requests.json', requests), ('paste_plan.json', plan)):
        with open(lp(os.path.join(args.out, name)), 'w', encoding='utf-8') as fh:
            json.dump(obj, fh, ensure_ascii=False, separators=(',', ':'))
    print(f'rows: {n - 2} content rows, write range A1:I{n}')
    print(f'requests: {len(requests)}  paste: {len(plan)} images')
    for p in plan:
        print(f"  {p['cell']:<4} <- {p['file']}")


if __name__ == '__main__':
    main()
