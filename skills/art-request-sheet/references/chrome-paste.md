# 用 Claude in Chrome 貼參考圖

實測可行的做法（2026-10-05，一部新系統企劃首跑）。核心是：在頁面放一個隱藏的檔案輸入框 → 用 `file_upload` 把圖塞進去 → 用名稱方塊跳到目標格 → 對 Sheets 的編輯器送一個合成的 paste 事件。圖會以「浮在儲存格上方」的方式貼在該格左上角。

## 已知坑

| 坑 | 原因 | 做法 |
|---|---|---|
| 「插入 → 圖片 → 插入儲存格內／上方」之後截圖一直逾時 | Google 圖片挑選器是跨網域 iframe，開著時 Chrome 擷取畫面會卡住 | 不用選單；按 Escape 關掉挑選器即可恢復 |
| `file_upload` 回「only files this session is allowed to read」 | 只收 scratchpad 裡的檔案；工作目錄、Downloads 都被拒 | `prep_images.py` 輸出到 scratchpad |
| 貼出來的圖超大 | 原圖 2496px 寬，照原尺寸貼 | 先用 `prep_images.py --spec spec.json` 縮到各欄的縮圖上限內（一部 530×300；四部依欄位） |
| paste 沒反應 | activeElement 是自己塞的 input，不是 Sheets 編輯器 | 先用名稱方塊跳格，確認 `document.activeElement.id === 'waffle-rich-text-editor'` 再送 |
| 單次上傳失敗 | `file_upload` 單次總量上限 10 MB（2026-10-07 E2E：91 秒影片舊版轉出 79 MB） | `prep_images.py` 預設只轉前 10 秒、約 2 MB；仍超過就分批上傳 |
| 貼完圖後第一次截圖逾時 | 剛貼上的圖還在選取狀態 | 先按 Escape 取消選取再截圖（2026-10-05 改版企劃測試重現） |

## 步驟

1. `tabs_context_mcp` → `navigate` 到表格網址，等 3 秒。
2. 塞輸入框並定義兩個輔助函式（`javascript_tool`）：

```js
(() => {
  let i = document.getElementById('claude_img_in');
  if (!i) {
    i = document.createElement('input');
    i.type = 'file'; i.id = 'claude_img_in'; i.multiple = true;
    i.style.cssText = 'position:fixed;left:0;top:0;width:200px;height:40px;z-index:99999;opacity:0.01';
    document.body.appendChild(i);
  }
  window.claudeGo = (a1) => {
    const nb = document.querySelector('#t-name-box');
    nb.focus(); nb.value = a1;
    nb.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13, which: 13, bubbles: true}));
    return true;
  };
  window.claudePaste = (name) => {
    const f = [...document.getElementById('claude_img_in').files].find(x => x.name === name);
    const ae = document.activeElement;
    const dt = new DataTransfer(); dt.items.add(f);
    const ev = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true});
    ae.dispatchEvent(ev);
    return [ae.id, ev.defaultPrevented];
  };
  return 'ok';
})()
```

3. `find`「file input」拿到輸入框的 ref，`file_upload` 一次上傳 `paste_plan.json` 列的所有檔案（路徑在 scratchpad 的 `up/`）。
4. 每張圖一組，用 `browser_batch` 串起來：

```
javascript_tool: claudeGo('G6')
wait 1
javascript_tool: claudePaste('r05.png')     → 回傳 ["waffle-rich-text-editor", true] 才算成功
wait 3（GIF 等 5–6 秒）
```

   **切換分頁**（多分頁時 `paste_plan.json` 每筆有 `tab`）：名稱方塊直接輸入「分頁名!儲存格」就會切過去並選到那格，分頁名用單引號包住（2026-10-07 E2E 實測可行）：

```
javascript_tool: claudeGo("'動態'!C3")
wait 2
javascript_tool: claudePaste('r11.png')
```

   同一分頁接下來的圖可以只寫 `claudeGo('E5')`；換分頁時再帶分頁名。

5. 全部貼完 `claudeGo('A1')`，縮放下拉選 50%，逐段 scroll + screenshot 檢查每張圖在對的列。
6. 縮放改回 100%（縮放是使用者自己的檢視設定，不能留著 50%），`tabs_close_mcp` 關分頁。重新整理或關分頁時，塞進去的輸入框就會消失，不會留在檔案裡。

## 貼錯了怎麼辦

點選那張圖按 Delete 刪掉，再重新跳格貼一次。不要用 Ctrl+Z 連續回復，會把前面的寫入也一起撤掉。

## 重做已經貼過圖的表（2026-10-05 改版企劃重做實測）

- **整份重寫最乾淨的做法**：同一個 `update_spreadsheet` 先 `addSheet`（例 `sheetId: 100`、`title: "工作表1"`、`index: 0`），再 `deleteSheet` 舊分頁。舊分頁上的圖會一起消失，不用進 Chrome 一張張刪；連結不變。spec 的 `sheet_id` 改成新的 ID，之後照正常流程寫。

- **要刪掉一整列**：先用 Chrome 點選該列的圖、按 Delete（每刪一張截圖確認一次，圖被選取時四周有控制點），**再**用 API `deleteDimension` 刪列。下面各列的圖會跟著列一起往上移，不用重貼。
- **重寫文字**：`update_values` 寫入新值時，舊的紅字 runs 會一起清掉，不用另外重設。
- **點圖前先確認沒有圖被選取**：剛開頁面或縮放後，有時某張圖會處於選取狀態，這時按 Delete 會誤刪。先點一個空白儲存格再操作。
- 剛載入頁面就點縮放下拉可能沒反應，等 3 秒或重點一次。
