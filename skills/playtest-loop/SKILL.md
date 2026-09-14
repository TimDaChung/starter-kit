---
name: playtest-loop
description: 遊戲 demo 試玩迭代迴圈。Use when 使用者說「重開 server」「我要試玩」「開遊戲」「幫我開一下」「收筆記」「harvest」「我有回報幾個開發者表示」「學習回收」，或任何單檔 HTML 遊戲 demo 進入「玩 → 回饋 → 修 → 再玩」循環時。
---

# playtest-loop

> **執行角色：數值 / QA**——關注回饋收斂、重現步驟、平衡與成長曲線；修改方向切**企劃**視角確認不偏離核心循環。

## 核心原則

使用者只做兩件事：**玩**、**在遊戲內打「開發者表示：」**。其餘全部（起 server、開頁、收筆記、歸類、批次修正、清空、重開）由本 skill 一條龍完成，使用者不需要手動貼 JSON、不需要重複下「重開 server」指令。

## 前置

需要 chrome-devtools MCP 已接、且玩家的 Chrome 以 `--remote-debugging-port=9222` 啟動（MCP 才能連進玩家原本的分頁讀 localStorage）。缺任一項 → 開場說一句，退到「請使用者在主控台跑 `exportDevNotes()` 貼回來」模式，不要硬開新 browser。安裝方式見 kit 的 `安裝說明.md` 前置表。

## 專案偵測

1. 目標 = 使用者指名的專案，否則取對話中最近的遊戲專案（下稱 `<project-dir>/`）。
2. Grep 入口 HTML 是否有 `exportDevNotes` / `exportLearned` → 確認回饋頻道存在。沒有的話，先提議注入標準頻道（localStorage `dev_notes` array + `開發者表示：` 前綴攔截），使用者同意才加。標準頻道程式碼在 `references/dev-notes-channel.js`，用 Edit 貼進入口 HTML 的 `<script>`（有 section marker 時放 `JS-EVENTS`），再依專案的輸入欄 id 呼叫 `attachDevNotesInterceptor(inputEl, sendBtn)`。

## 三個動作

### 1. 開／重開（觸發：重開、我要試玩、幫我開一下）

```bash
# 中文路徑鐵則：cd 進目錄再起，絕不用 --directory 傳中文參數（會 404）
cd "<project-dir>" && python -m http.server 8000   # run_in_background
```

- 先殺同 port 舊行程再起新的。Windows 查 PID 與殺法：
  ```powershell
  netstat -ano | findstr :8000      # last column is the PID
  taskkill /PID <pid> /F
  ```
- 用 chrome-devtools MCP（`list_pages` / `select_page` / `navigate_page`）在**使用者原本玩的分頁** navigate/reload `http://localhost:8000/index.html`（強制 reload，避免看到舊版）。找不到分頁才開新分頁。
- 回報一句「可以玩了」即結束，不要多話。

### 2. 收割 harvest（觸發：收筆記、我有回報幾個、學習回收）

- 用 chrome-devtools MCP（`evaluate_script`）在**玩家玩的那個分頁**執行：
  ```js
  JSON.stringify({dev: JSON.parse(localStorage.getItem("dev_notes")||"[]"),
                  learned: JSON.parse(localStorage.getItem("learned_script")||"{}")})
  ```
  **絕不能開新的 Playwright/puppeteer browser 去讀** — 不同 profile 讀不到玩家的 localStorage。chrome-devtools MCP 不可用時，退而求其次請使用者在主控台跑 `exportDevNotes()` 貼回來。
- 原始 JSON 存 `<project-dir>/playtest-notes/<YYYYMMDD-HHMM>.json` 留底。
- 逐條歸類成表：**bug / 手感時序 / 文筆台詞 / 美術 / 數值難度 / 劇情設計**，附 node 與 context。
- 批次修正（見委派判斷）→ 修完在同分頁執行 `clearDevNotes()`（沒 clear 下次會重複處理）→ 自動回到動作 1 重開。
- learned_script 走 curate 流程：擋爛留好、烘焙進正式腳本節點（依專案 memory 的規則；無 memory 規則時：保留原句、去重、依日期排序）。

### 3. 守護

server 行程死掉 → 回報 + 自動重啟一次；**連續被外部殺 2 次 → 停止自動重啟**，回報使用者判斷。

## 委派判斷（subagent）

單檔 HTML = **單一寫入者鐵則**：所有 agent 只回傳文字/diff，主檔寫入一律由本終端序列執行。

| 筆記情況 | 處理 |
|---|---|
| ≤3 條且都是小修 | 本終端直接改，不派 agent |
| 文筆／台詞類 | 派 dialogue-writer 產草稿（read-only），本終端寫入 |
| 數值／難度類 | 派 game-balance-auditor 模擬分析，本終端套用 |
| 多類混合且量大 | 按類 fan-out read-only agents 平行分析，本終端彙整後一次寫入 |

## 常見錯誤

| 錯誤 | 後果／修法 |
|---|---|
| 開新 browser instance 讀 localStorage | 讀不到（不同 profile）。用 chrome-devtools MCP `evaluate_script` 讀原分頁 |
| `http.server --directory <中文路徑>` | 404／亂碼。`cd` 進目錄再起 |
| 修完沒 reload 分頁 | 玩家玩到舊版還以為沒修。重開後強制 reload |
| harvest 完沒 `clearDevNotes()` | 下次重複處理同批筆記 |
| 筆記處理到一半就重開 server | 先修完、留底、clear，最後才重開 |
