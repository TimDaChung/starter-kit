---
name: pet-parts
version: 1.0.0
description: |
  魚樂園寵物「配件」產出流程，pet-evolution 的下游：動畫分鏡（一般／上陣／虛弱各一張 3–4 格，一階二階各一套，動作照企劃原文）、
  技能 ICON（含 64px 可讀性檢查）、專屬背景（16:9 滿版）、滿星貼圖（有才做）、道具 ICON（後製不生圖，一階／二階各一）。
  讀道具之書的寵物企劃 → 以兩階定稿為參考圖分批算圖 → 交付。必須等寵物兩階定稿後才做。
  適用於：「寵物配件」「寵物動畫分鏡」「寵物動態示意」「寵物姿勢圖」「寵物技能 ICON」「寵物背景」「滿星貼圖」。
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

# 寵物配件 Skill

> **執行角色：美術企劃**——關注配件與寵物定稿的一致性、企劃條目是否全數還原；交付前逐條跑驗收清單。

**前置條件：寵物兩階必須已經定稿。** 上游是 `pet-evolution`。

依賴：

- `配件規格.md` — 各批規格、驗收清單（硬規範）
- `prompt模板.md` — 三批的提示詞模板
- `scripts/label_frames.py` — 動畫分鏡加標籤、檢查格數
- `scripts/icon_check.py` — 切技能 ICON、產 256／128／64px 尺寸預覽
- `scripts/item_icon.py` — **道具 ICON 後製**（從定稿裁主體、去灰底、疊深色圓角底板，出 512 主圖＋256／128／64 預覽；`--badge` 出碎片版）。三條生圖線共用，只吃 Pillow
- 共用：讀企劃 `~/.claude/skills/pet-evolution/scripts/fetch_plan.py`；背景裁切 `~/.claude/skills/boss-design/scripts/fit_canvas.py --cover`
- **`kit 根目錄/references/image-studio-共用須知.md`** — 產圖層面的問題先查那份

---

## 全程規則

- **有企劃的一次全部盤點、分批派出去產**，不要一件一件問；企劃沒寫到的才詢問
- **每輪至少算 2 張**，全部看完挑最好的
- **不修改既有企劃**；文字與圖不一致時列出來問
- 中間產物進 `_工作暫存/`（已 gitignore）；**未上線的設計圖不進 repo**

---

## 流程

### Step 1 — 確認定稿、讀企劃

確認兩階定稿圖在手（沒有就先走 `pet-evolution`）。讀企劃：

```sh
NOTION_KEY=$(tr -d '\r\n ' < "<四部readonly_token.txt 路徑>") \
  python ~/.claude/skills/pet-evolution/scripts/fetch_plan.py <page_id> _工作暫存/<寵物名>
```

從 `plan.md` 盤點（位置見 `配件規格.md` 第一節）：零星／三星動態、技能 ICON 描述、專屬背景、有沒有滿星貼圖；道具 ICON（本體縮圖＋碎片版）不用盤企劃，定稿一到就後製。列成清單給使用者確認後**一次派出**。

### Step 2 — 分批算圖

三批彼此獨立，可以同時送：

| 批 | 提示詞 | 參考圖 |
|---|---|---|
| 1 動畫分鏡（**每個動畫一張、一階二階各一套**，動作照企劃原文、循環拆格；拆法先給使用者看） | `prompt模板.md` 第一節 | 該階定稿 |
| 2 技能 ICON | 第二節 | 二階定稿（配色用） |
| 3 專屬背景 | 第三節 | 不給 |

> **技能 ICON 是技能圖示，照上表生圖流程；道具 ICON 是縮圖，走後製**（Step 3），不進生圖批次。兩者不要混。

```sh
python3 ~/.claude/skills/image-studio/scripts/image-studio-client.py draw \
  --count 2 --prompt-file <prompt.txt> [--reference <定稿圖>] --output <_工作暫存/寵物名/批次>
```

### Step 3 — 後製

- **動畫分鏡**：`python ~/.claude/skills/pet-parts/scripts/label_frames.py <圖> <輸出> --cols 3 --rows 1 --captions "…|…|…" --title 一般動態`（格數不符會擋下，重抽）
- **技能 ICON**：`python ~/.claude/skills/pet-parts/scripts/icon_check.py <圖> <輸出資料夾> --names 技能1,技能2`，產出正方形 ICON 與 `ICON_尺寸預覽.png`
- **道具 ICON（後製，不生圖）**：一階／二階各一張，從並排定稿各取一半：
  ```sh
  python ~/.claude/skills/pet-parts/scripts/item_icon.py <兩階定稿.png> <輸出資料夾> --name <寵物名>_一階 --half left [--badge <角標.png>]
  python ~/.claude/skills/pet-parts/scripts/item_icon.py <兩階定稿.png> <輸出資料夾> --name <寵物名>_二階 --half right [--badge <角標.png>]
  ```
  產出 `ICON_<名>.png`（512）＋`ICON_<名>_尺寸預覽.png`（256／128／64）；給了 `--badge` 才多出碎片版 `ICON_<名>_fragment.png`（同圖左上疊碎片角標）。**碎片角標素材不進 repo**（線上 UI 素材裁切、kit 是公開 repo）：向主任拿，放本機 `skills/pet-parts/_工作暫存/fragment_badge.png`（已 gitignore），腳本用 `--badge <路徑>` 指路；沒有角標就只出主圖不出碎片版
- **背景**：`python ~/.claude/skills/boss-design/scripts/fit_canvas.py <圖> <輸出> --cover`
- **滿星貼圖**：二階定稿＋程式加字（字不交給模型寫）

### Step 4 — 挑圖與交付

1. 複製到使用者看得到的資料夾，`explorer.exe` 開給他看
2. **自己先逐條跑 `配件規格.md` 第七節**，主動回報哪張好、好在哪；技能 ICON 與道具 ICON 都要看 64px 欄（道具 ICON 64px 要看得出是這隻寵物）
3. 定稿輸出到使用者指定位置，附最終提示詞
4. 暴露了新規則或前科 → 回寫 `配件規格.md` 第八節或 `prompt模板.md`

---

## 維護說明

- 改規格或驗收 → `配件規格.md`
- 改提示詞 → `prompt模板.md`
- 改技能 ICON 切割與預覽 → `scripts/icon_check.py`
- 改道具 ICON 後製（裁切、底板、角標）→ `scripts/item_icon.py`（三條線共用，改動要顧炮台翅膀與武具線）
