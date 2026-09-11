---
name: game-prototype
version: 1.0.0
description: |
  快速建立可玩單檔 HTML 遊戲原型，emoji 代替美術，速度優先。
  目的：testing 玩法 / 互動 / state machine。
  完成標準：玩法閉環 + 可邀人試玩。
  美術升級請改用 /game-develop。
  MANUAL TRIGGER ONLY：使用者輸入 /game-prototype 才啟動。
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
  - TaskList
---

# /game-prototype — 單檔 HTML 遊戲玩法原型

快速打通遊戲玩法 / 互動 / state machine。**emoji 代替所有美術**——避免在 prototype 階段花時間調 design system。

---

## 啟動：每次 invoke 第一步（Resume 偵測）

讀取兩檔判斷狀態：

| 狀態 | 動作 |
|------|------|
| 都沒有 `GAME_SPEC.md` / `GAME_TODO.md` | 新專案，從 Phase 0 開始 |
| 有 SPEC、無 TODO | 接 develop 之前產出，跳到 Phase 5 補建 TODO |
| 兩者都有 | 列未完成項，問 user 本次推進什麼；或重新跑 playtest |

給 user 一句話狀態摘要：「上次做到 X，建議下次推進 Y / Z」。

---

## 核心紀律（不可違反）

1. **整套 5 phases 連續跑完才回報**：phase 之間自動推進，不對 user check-in。**唯一例外**：玩法核心 / 規則明顯模糊到無法下筆才停下來一次性問清楚。Phase 5 完才一次性給總結摘要
2. **絕不呼叫任何生圖 skill**——一旦 user 要求換真圖，立刻提醒：「請改用 `/game-develop`，prototype 階段不做美術」
3. **單檔、無外部 asset、無 build step**——複製到別人電腦 double click 能玩
4. **一個 phase 完成後 checkpoint**（更新 TODO + Edit HTML），允許隨時中斷恢復；但**不暫停等 user 看**
5. **修改檔案 100% 用 Edit**（依既有 memory `feedback_no_sed.md`），不重寫整檔
6. **沒對應工具時自己做**：音效 / 動效 / 特殊互動 → 用原生 JS / CSS animation / Web Audio API
7. **section marker 強制**：HTML 內必須有 8 個 `<!-- === SECTION: NAME === -->` 標記（見 Phase 2）

---

## Phase 0：玩法澄清

優先**從 user 訊息推斷**這 5 項：

1. 遊戲類型：回合制 / 即時 / 解謎 / 抽卡 / etc
2. 玩家數：1 / 2 / 4 / 多人 PvP / 多人協作
3. 勝利條件：HP 歸零 / 籌碼最多 / 時間結束 / etc
4. 預期一輪時間：（分鐘）
5. 平台輸入：滑鼠 / 鍵盤 / 觸控

只有**完全無法推斷**的項目才合併成一次列表問完（不一題一題問）。能合理推斷的直接寫進 SPEC，繼續推進——回報時提一句「我假設了 X / Y / Z，要改說一聲」。

---

## Phase 1：UI 流程設計

列出**每個畫面**：
- 進入畫面 / 主遊戲畫面 / 結算畫面 / 設定畫面
- 每個畫面內的元件清單

**emoji 配對表**（重要）：寫進 GAME_SPEC.md 的「Emoji ↔ 概念對照」。範例：

| Emoji | 概念 | （develop 階段填路徑） |
|-------|------|----------------------|
| 🐉    | 火龍怪物 | (待填) |
| ❤️    | HP | (待填) |
| 🪙    | 籌碼 | (待填) |
| ⚔️    | 攻擊招式 | (待填) |
| 🛡️    | 防禦招式 | (待填) |

---

## Phase 2：建立單檔 HTML

**強制 section marker 結構**（共 8 個 SECTION）：

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{遊戲名}</title>
<style>
/* === SECTION: CSS-VARIABLES === */
:root {
  --bg: #1a1a1a;
  --text: #e8e8e8;
  --accent: #c89b4a;
  --danger: #a83246;
}

/* === SECTION: CSS-LAYOUT === */
body { margin: 0; font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); }
#app { max-width: 800px; margin: 0 auto; padding: 1rem; }

/* === SECTION: CSS-COMPONENTS === */
.btn { padding: 0.6em 1.2em; background: var(--accent); border: none; border-radius: 4px; cursor: pointer; }
.card { padding: 1rem; border: 1px solid var(--accent); border-radius: 8px; }
</style>
</head>
<body>
<!-- === SECTION: HTML-BODY === -->
<div id="app"></div>

<script>
// === SECTION: JS-STATE ===
const state = {
  round: 0,
  players: [],
};

// === SECTION: JS-LOGIC ===
function startRound() {
  state.round += 1;
}

// === SECTION: JS-RENDER ===
function render() {
  document.getElementById('app').innerHTML = `<div>Round ${state.round}</div>`;
}

// === SECTION: JS-EVENTS ===
document.addEventListener('DOMContentLoaded', () => {
  render();
});
</script>
</body>
</html>
```

**design system 紀律**（prototype 階段嚴格簡化）：
- 配色 ≤ 4 個（bg / text / accent / danger）
- 字型用系統預設（`font-family: system-ui, -apple-system, sans-serif`）
- 不引入外部資源（無 Google Fonts / 無 CDN）

---

## Phase 3：self-walkthrough

跑一輪確認玩法閉環，**列 5 個 edge case** 確認：

1. 勝利條件觸發
2. 平手 / 失敗條件
3. 第一回合 / 最後回合的 UI 差異
4. 異常輸入（連點 / 跳步驟）
5. 狀態 reset / 重玩

回報：「玩法閉環 OK ／ 有 N 個 issue 待修」。

---

## Phase 4：迭代修正

user 回饋 → Edit HTML → 再 self-walkthrough → loop。

**每次 Edit 都針對 single section**——多 section 改動拆多次 Edit 呼叫。

---

## Phase 5：Freeze + 產 SPEC + TODO

確認玩法穩定後：

1. **複製 SPEC 樣板**：從 `~/.claude/skills/game-develop/templates/GAME_SPEC.template.md` 複製到專案目錄為 `GAME_SPEC.md`，填入 prototype 階段所有資訊（玩法 / state machine / emoji 對照表 / 平衡假設）
2. **複製 TODO 樣板**：從 `~/.claude/skills/game-develop/templates/GAME_TODO.template.md` 複製到專案目錄為 `GAME_TODO.md`，prototype 階段相關項目先標 ✅
3. 告訴 user：「prototype 完成。下一步可以：
   - 邀人試玩收回饋（迭代 Phase 4）
   - 跑 `/game-develop` 升級美術 + balance + ship」

---

## 工作量切分（避免 session 超時）

當 user 一次要動 5+ 處或寫 500+ 行新 code：
1. 先把任務拆成「子任務清單」寫進 GAME_TODO.md
2. 本 session 跑前 1–2 個子任務 + checkpoint
3. 告訴 user：「子任務 A、B 完成；C/D/E 排在 TODO，下次 invoke 接續」

---

## 行數監控（提醒 only）

- HTML 5000 行：提醒 user「未來改動建議用 grep marker 精準定位」
- HTML 8000 行：提醒「考慮哪些 section 可以瘦身（例如 emoji 對照表搬到 SPEC）」

**不強制拆檔**——除非 user 明確說要。

---

**End of skill.**
