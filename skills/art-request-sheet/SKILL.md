---
name: art-request-sheet
version: 1.0.0
description: |
  把 Notion 企劃轉成 Google Sheets「美術需求表」（發給美術的需求單）：讀企劃〈呈現〉章逐畫面拆列、
  依規則章補數值與交付檔名、照固定格式寫入（淺綠表頭、深綠分隔列、O/X 下拉、紅字標記），
  再把企劃裡的示意圖與影片（轉 GIF）用 Claude in Chrome 貼進參考圖欄，最後依命名格式
  `v<版號>_<活動名>_<企劃名>` 改檔名並回報缺漏。
  適用於：「美術需求表」「美術需求單」「開美術單」「發美術需求」「企劃轉美術需求」「做一份美術需求表」
  「把企劃整理成給美術的表」，或使用者丟出 Notion 企劃連結＋一份空白 Google Sheets 要整理給美術時，
  即使沒講「美術需求表」這幾個字也要用這支。
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - PowerShell
  - AskUserQuestion
---

# 美術需求表 Skill

> **執行角色：企劃（美術需求窗口）**——關注每個畫面與狀態都有一列、描述能讓美術不回頭翻企劃就開工、數值與檔名和企劃規則章一致、參考圖放對列；完成後切美術視角複核（缺圖、動態標記），再切工程視角複核（數值、狀態、命名）。

同資料夾檔案：

- `references/format.md` — 表格格式規格（欄位、顏色、欄寬、字型、紅字規則、命名格式）。**寫表前先讀**
- `references/writing-rules.md` — 拆列與設計描述的寫法、參考圖分配規則、去識別化範例列（實際案例屬機密，在網芳 `X:\grp.product.pm1\2. 產品改造\一四部企劃範本\kit-assets\art-request-sheet\實際範例.md`（X 讀不到換 Y:），讀得到就先讀）
- `references/chrome-paste.md` — 用 Chrome 貼圖的做法與已知坑。**貼圖前先讀**
- `scripts/fetch_plan.py` — 用部門憑證走 Notion proxy＋REST 讀企劃：輸出 `plan.md`（保留紅字／灰綠底／刪除線標記）並當場下載圖片與影片
- `scripts/prep_images.py` — mp4 轉 GIF、縮圖到欄寬、改 ASCII 檔名，輸出到可上傳的資料夾
- `scripts/build_sheet.py` — 從內容 spec 產出寫入值、格式化請求、紅字 runs、貼圖清單

## 0. 開工前確認

需要兩個輸入：**Notion 企劃連結**、**目標 Google Sheets 連結**（通常是空白表）。缺哪個就問哪個。

需要的工具（缺了先講，不要繞路做替代品）：

| 工具 | 用途 | 缺了怎麼辦 |
|---|---|---|
| Notion 部門憑證（本機個人憑證，見 `plan-dept14-writer/references/notion-access.md`） | 讀企劃 | 沒憑證或過期 → 照該檔 §3 協助安裝／換新；兩部都 404 → 照實回報，請頁面擁有者連接 integration；不改用任何 Notion MCP、不用瀏覽器抓文字 |
| Google Sheets connector | 寫文字與格式 | 請使用者在這個對話開啟；不能用 Drive 另建新檔代替 |
| Claude in Chrome | 貼圖（**實驗性**：靠 Sheets 頁面結構，Google 改版可能失效） | 跳過貼圖，交付時列出「哪張圖貼哪格」讓使用者手貼 |
| Python：pillow、imageio-ffmpeg | 縮圖、影片轉 GIF | `pip install -r %USERPROFILE%\starter-kit\requirements.txt` |

改 Google Sheets 前先讀 `anthropic-skills:google-workspace` skill 的 `references/sheets.md`（寫入解析、field mask、sheetId 規則）。

## 1. 讀企劃並下載媒體

1. `python scripts/fetch_plan.py <Notion 連結> "%USERPROFILE%\Downloads\<活動名>_美術需求參考圖"`。憑證與部別由腳本自己判（頁面 id 指紋 → 判不出就一部、四部輪流試），**兩部都 404 就停**，回報頁面沒連接 integration。
2. 腳本輸出 `plan.md`（第一行是頁面標題）與 `NN_<圖名>.<副檔名>` 媒體檔：圖名取 block 說明文字，沒有就取上方最近的《圖名》行。Notion 的檔案網址是簽名網址、幾分鐘到一小時就過期，所以讀頁面時當場下載，不另外抄網址。
3. 讀 `plan.md`。企劃結構通常是：1.目的 → 2.流程圖 → **3.呈現**（逐畫面，左欄說明、右欄示意圖）→ **4.規則**（數值、盤面、檔名對照）→ 5.說明頁 → 6.設定 → 7.後台 → 8.調整紀錄。行內標記：`<span color="red">` 紅字、`gray_background`／`green_background` 調整標記、`~~..~~` 刪除線。
4. 下載失敗的檔會在 `plan.md` 標 `DOWNLOAD FAILED`，重跑一次腳本即可（會拿到新網址）。媒體檔名若和畫面對不上，照 `plan.md` 裡 `[image ..]` 出現的位置改成「序號_畫面名_狀態」（例：`05_主介面_已達門檻.jpg`），序號照企劃順序。

## 2. 拆列與寫內容

照 `references/writing-rules.md`。**先判斷是新系統還是改版**：企劃有灰底刪除線／綠底調整標記、或寫「既有系統改版」→ 改版企劃，走 writing-rules〈改版企劃〉：只列有變動的畫面，描述上段只寫變動、`=====` 下段列完整資料清單。以下要點是新系統的寫法：

- **一個畫面或一個狀態一列**，順序照〈呈現〉章；動畫（切換、演出）獨立成列。
- 設計描述沿用企劃原文的編號條列，再從規則章補上美術開工需要的東西：盤面配置、各格內容、花費數值、**交付檔名與 spine 動畫命名**。
- 企劃裡紅字的片段（數值、「後補」、特別強調）在表裡也標紅字。
- 「是否有動態」：有動畫、刷光、轉場就是 O，靜態畫面 X。
- 企劃沒寫清楚、或企劃圖和規則對不上的地方，**先照規則章寫，記進缺漏清單**，最後一起回報，不要邊做邊停下來問。

把內容寫成 spec JSON（格式見 `scripts/build_sheet.py --help`），放在 scratchpad。

## 3. 寫入表格

1. `get_spreadsheet`（`fields: ["properties.title","sheets.properties"]`）拿 `sheetId` 和分頁名。
2. `python scripts/build_sheet.py spec.json --out <scratchpad>/build`，產出：
   - `values.json` → **先**一次 `update_values`（範圍用分頁**目前**的名稱，例 `'工作表1'!A1:I<n>`）
   - `requests.json` → **再**一次 `update_spreadsheet`（分頁改名「美術需求表」、字型、顏色、合併、下拉、框線、欄寬列高、紅字 runs）。順序不能反：紅字 runs 要套在已寫入的文字上
   - `paste_plan.json` → 第 4 步貼圖用
3. 用 Read 讀出 `values.json`、`requests.json`，原樣送進工具，不要手改；要改內容就改 spec 重跑。
   - 腳本已處理 Windows 260 字元路徑限制（scratchpad 路徑很長），子資料夾名稱仍盡量短（`b/`、`up/`）
   - 寫入值時字串照常送；`O`／`X`、`1. ...` 開頭的多行文字不會被 Sheets 誤判成數字
4. `get_values` 讀回 `'美術需求表'!A1:F<n>` 核對文字（分頁已改名）。

## 4. 準備圖片並貼進參考圖欄

1. `python scripts/prep_images.py <Downloads 參考圖資料夾> <scratchpad>/up`：mp4 轉 GIF、縮到 530×300 內、改成 `r01.png` 這類 ASCII 名。**一定要輸出到 scratchpad**：Chrome 的 `file_upload` 只收 scratchpad 裡的檔案，工作目錄和 Downloads 都會被拒。
2. 照 `references/chrome-paste.md` 貼圖。**不要用「插入 → 圖片」選單**：Google 圖片挑選器開著時 Chrome 截圖會卡死。
3. 縮放切到 50% 逐段截圖，確認每張圖在對的列；確認完**把縮放改回 100%**、關掉分頁。

「圖後補」這類佔位圖不貼，參考圖欄留空，描述裡寫「示意圖後補」。

## 5. 命名

檔名格式：`v<版號>_<活動名>_<企劃名>`，例：`v20.3_春節集點_Ming.Chen`。

- 版號：企劃〈目的〉表的「限制版本號」或「正式區生效日」裡的版本（`v20.3 以上` → `v20.3`）
- 活動名：企劃標題「項目：」後面的名稱照抄，含「調整」等字（`項目：排行榜調整` → `排行榜調整`）
- 企劃名：PM 的英文名，`名.姓` 首字大寫（帳號 `ming.chen@…` → `Ming.Chen`）；企劃寫的 PM 欄是暱稱時以帳號為準

用 Drive `update_file` 改標題（連結不變）。**使用者說是測試、或同名檔已存在時先問**，不要直接改。

## 6. 交付回報

照這個順序，簡短：

1. 表的連結（標題做成連結），一句說明做了幾列、參考圖貼了幾張。
2. 跟使用者原本預期不同的地方（例如沒先確認清單、改用企劃原圖）。
3. **交給美術前要確認的**：缺漏清單，每條講清楚是什麼、我先怎麼寫。常見類型：企劃圖和規則數值不一致、命名對應是推測的（小／中／大 vs 1／2／3）、動態標記不確定（公版刷光算不算）、圖後補、秒數後補、說明頁要不要列。
4. 參考圖原檔放在哪個資料夾。

不要主動改 Notion 企劃（例如更新企劃裡的美術需求表連結）；需要的話提一句讓使用者決定。
