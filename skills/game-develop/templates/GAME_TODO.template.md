# {遊戲名} 開發進度

> 標記：☐ 未開始 ／ ⏳ 進行中 ／ ✅ 完成
> 子項決策原因用 `└` 縮排寫在該項下方（取代 LOG）。

---

## Phase 1: Design System

- ☐ 視覺主題決定
  └ 理由：（填）
- ☐ CSS variables 內嵌（HTML 內 `/* === SECTION: CSS-VARIABLES === */`）
- ☐ DESIGN.md 完成（風格代號 / 色票 / 字級階 / 元件規則）
  └ 跳過理由（如選擇）：（填）

## Phase 2: 素材清單規劃

- ☐ 立繪清單（從 GAME_SPEC.md emoji 表反推）
- ☐ UI 元件清單
- ☐ sprite / 動畫清單
- ☐ 地圖 / 背景清單
- ☐ 通用插圖清單

## Phase 3: 批次生圖

> 每張一行：標 ✅ + 路徑 + 版本。`└` 寫關鍵決策（retake 幾次、style-lock）。

### 立繪 (0/N)
- ☐ {角色 A}
- ☐ {角色 B}

### UI 元件 (0/N)
- ☐ btn_primary
- ☐ btn_secondary
- ☐ icon_hp
- ☐ frame_card
- ☐ banner_title

### Sprite (0/N)
- ☐ {移動角色 A 動畫表}

### 地圖 / 背景 (0/N)
- ☐ {場景 A}

### 通用插圖 (0/N)
- ☐ {插圖 A}

## Phase 4: 素材整合（emoji → 真圖）

- ☐ 立繪整合（HTML CSS-COMPONENTS / HTML-BODY）
- ☐ UI 元件整合
- ☐ sprite 整合
- ☐ 地圖 / 背景整合
- ☐ chrome-devtools MCP 跑一輪確認 layout 沒破

## Phase 5: Polish（順序：balance → dialogue → design review → qa）

- ☐ Balance simulation（呼叫 game-balance-auditor agent）
  └ 結果摘要：（填）
- ☐ 對白文案（呼叫 dialogue-writer agent）
  └ 完成範圍：（填）
- ☐ 視覺 QA（自行 self-walkthrough：chrome-devtools MCP 截圖逐畫面檢查）
  └ 修正項數：（填）
- ☐ 玩法 QA（呼叫 webapp-testing skill，Playwright 腳本存 tests/）
  └ 修正項數：（填）

---

## 進度摘要（每次 session 結尾更新）

- 上次 session 完成：（填）
- 下次 session 接續：（填）
