---
name: boss-scene
description: |
  捕魚機 Boss 的「專屬背景」產出流程，boss-design 的配套：兩種背景——
  A 漁場邊框（Boss 事件期間疊在漁場底圖上的四邊主題裝飾，中央留給魚群，輸出透明 PNG 疊層）、
  B 表演背景（捕獲／彩金表演、小遊戲的 16:9 滿版場景）。讀魚類之書企劃的背景段落、或跟著從零設計的 Boss 一起發想。
  適用於：「Boss 背景」「Boss 場景」「漁場背景」「漁場邊框」「表演背景」「小遊戲背景」「捕獲表演背景」。
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - PowerShell
  - AskUserQuestion
---

# Boss 背景 Skill

> **執行角色：美術企劃**——關注背景是否忠實還原企劃、漁場邊框是否把中央留給魚群、表演背景是否留出舞台並襯得起 Boss；交付前逐條跑驗收清單，不合格就重抽或改提示詞。

依賴同資料夾的檔案：

- `背景設計法則.md` — 兩種背景的規格、驗收清單（硬規範）
- `prompt模板.md` — 兩種背景的提示詞模板（改提示詞只改這份）
- `scripts/frame_alpha.py` — 漁場邊框的灰色中央轉透明、量中央是否乾淨、疊到底圖預覽

共用的：

- **`kit 根目錄/references/生圖線共用流程.md`** — 魚線十支共用的工作流程：前置需求、讀企劃（`fetch_plan.py`，`--list bosses`）、全程規則、從零發想的提案與拍板、挑圖、檢視與交付
- 補 16:9：`~/.claude/skills/boss-design/scripts/fit_canvas.py --cover`
- Boss 清單與已知企劃問題：`~/.claude/skills/boss-design/參考素材索引.md`
- **`kit 根目錄/references/image-studio-共用須知.md`** — 算圖中斷、憑證到期、平台偶發異常。**遇到產圖層面的問題先查那份**

---

## 這支 skill 的定位

`boss-design` 的配套，**做 Boss 的背景，不做 Boss 本身**。

| 種類 | 企劃裡的名稱 | 交付 |
|---|---|---|
| **A 漁場邊框** | 「X 階段漁場背景」 | 透明 PNG 疊層（中央透明）＋灰底原圖；有底圖時加預覽合成 |
| **B 表演背景** | 「捕獲表演背景」「小遊戲背景」「抽幻石表演背景」 | 16:9 滿版圖 |

**不做**：Boss 本體（→ `boss-design`）、UI 元件、既有底台的追加修改（例：古代遺跡中央 Logo 發光）。

**建議順序**：先用 `boss-design` 定好 Boss 外觀，再做背景——表演背景要拿 Boss 定稿當配色參考。

---

## 前置需求

照 `kit 根目錄/references/生圖線共用流程.md` 第一節（image-studio 憑證與 401 處置、四部 pm4 憑證由 `fetch_plan.py` 自動取、Pillow）。本 skill 的 Notion 讀取範圍：**魚類之書（四部）**。

---

## 全程規則

- **法則優先**：產圖前後都對照 `背景設計法則.md`，交付前逐條跑第六節驗收清單
- 共用規則照 `生圖線共用流程.md` 第三節；本線不修改既有企劃的範圍含背景段落的錯字、矛盾，列給使用者看即可

---

## 流程

### Step 1 — 盤點要做哪些背景

**模式 A（既有企劃）**：讀企劃

```sh
python ~/.claude/skills/art-request-sheet/scripts/fetch_plan.py <page_id> _工作暫存/<Boss名>
```

在 `plan.md` 裡找所有背景段落（搜「背景」「場景」），**列成清單給使用者確認要做哪幾張**：

| 背景 | 種類 | 企劃段落 | 階段 |
|---|---|---|---|
| 例：第一階段漁場背景 | A 漁場邊框 | 3.2.B 場景圖 | 一階 |
| 例：第二階段彩金表演背景 | B 表演背景 | 3.3.F 彩金表演 | 二階 |

（節號照範本實例劍魔頁 2026-10 現況：`3.2 Boss靜態` 下 A 靜態造型／B 場景圖／C 前哨階段與通緝令／D 血條與段數介面／E 老虎機／F 獎圈，`3.3 Boss動態` 下 F 彩金表演。其他 Boss 頁以 `plan.md` 實際讀到的節名為準。）

企劃背景段落常附**參考圖**（例：墨海的沉船甲板、晶龍的輻射晶礦），要實際 Read；參考圖若混著 UI mockup，只當構圖參考，不直接當 `--reference`。

**模式 B（從零發想）**：通常是接在 `boss-design` 的從零發想之後。提案通則（2–3 案、設計理由、使用者拍板才算圖）照 `生圖線共用流程.md` 第四節；依 Boss 的 mini 企劃提**背景方向**，每案：場景名、核心意象、配色、設計理由。

### Step 2 — 組提示詞

Read `prompt模板.md`，依種類選第一節（A）或第二節（B）填空。存到 `_工作暫存/prompt_<Boss名>_<背景名>.txt`（UTF-8）。

參考圖：

| 情況 | 參考圖 |
|---|---|
| B 表演背景，有 Boss 定稿 | Boss 定稿圖（配色參考），提示詞加「畫面中不要出現這隻 Boss」 |
| A 漁場邊框的二階 | 一階邊框定稿 |
| 其他 | 不給 |

### Step 3 — 算圖

```sh
python3 ~/.claude/skills/image-studio/scripts/image-studio-client.py draw \
  --count 2 --prompt-file <prompt.txt> --output <_工作暫存/Boss名/背景名> [--reference <參考圖>]
```

### Step 4 — 後製

**A 漁場邊框**：

```sh
python ~/.claude/skills/boss-scene/scripts/frame_alpha.py <邊框.png> <疊層.png> \
  [--preview <漁場底圖.png> <預覽.png>]
```

- 輸出 1920×1080 RGBA，灰色中央轉透明（羽化，光暈不會被切斷）
- 會印出**中央 70% 區域的不透明比例**：超過 5% 會警告，代表裝飾侵入魚群區 → 重抽
- 有漁場底圖就加 `--preview` 看實際疊上去的效果；沒有就向使用者要一張底台截圖，或只交疊層

**B 表演背景**：

```sh
python ~/.claude/skills/boss-design/scripts/fit_canvas.py <背景.png> <輸出.png> --cover
```

裁切填滿成 1920×1080，不加灰邊。

### Step 5 — 挑圖

挑圖通則（看完所有候選、三種情況的處置）照 `生圖線共用流程.md` 第五節；提示詞問題回 Step 2 修。常見的失敗：

- 邊框畫成側面仰看（晶柱朝中央刺出）→ 重抽
- 邊框裝飾侵入中央（腳本警告）→ 重抽
- 表演背景把 Boss 畫進去 → 重抽；反覆發生就拿掉 Boss 參考圖，改用文字寫配色
- 表演背景中央被物件塞滿 → 重抽

### Step 6 — 檢視與交付

1. 開資料夾給使用者看、自己先跑驗收清單並回報、定稿輸出到指定位置附最終提示詞，照 `生圖線共用流程.md` 第六節 1–4。本 skill 的差異：**漁場邊框交預覽圖**（有底圖時）比交透明疊層好判斷；定稿 A 交透明疊層＋灰底原圖（＋預覽）、B 交滿版圖
2. 前科回寫落點：`背景設計法則.md` 第七節或 `prompt模板.md`
3. **主動問下一步**：背景定稿後，還沒做道具就提 `boss-props`；道具也好了就提 `boss-demo`（定稿的 Boss、背景、道具直接當 demo 素材）

---

## 維護說明

- 改規格或驗收標準 → `背景設計法則.md`
- 改提示詞 → `prompt模板.md`（流程不用動）
- 改透明化或覆蓋率判定 → `scripts/frame_alpha.py`
- 16:9 裁切邏輯在 `boss-design/scripts/fit_canvas.py`（兩支共用）

## 貼回企劃（2026-10-02 起）

怎麼貼（交給 `plan-dept14-writer` 貼圖模式、憑證、list→報清單→貼→回讀、圖名、卡位、不准動的圖、落點不確定先問）一律照 `plan-dept14-writer/references/image-slots.md`〈通用貼法〉，落點總表同檔第五節。本 skill 產出的落點：

- A 漁場邊框 → Boss 頁 `3.2 Boss靜態 > 3.2.B 場景圖` 右欄（多階段各階一張，或依頁 `3.2.x X階段漁場背景`），**貼預覽合成圖**，caption《漁場背景示意》
- B 表演背景 → `3.3 Boss動態 > 3.3.F 彩金表演` 右欄（捕獲表演背景放該表演那節），caption《彩金表演背景示意》
- 節號照劍魔頁 2026-10 現況，各 Boss 頁不一定相同，以 `list` 實際看到的節名為準
