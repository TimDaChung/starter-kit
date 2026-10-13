---
name: weapon-parts
description: |
  魚樂園陣營戰「武具」登場動畫分鏡產出流程，weapon-design 的下游：
  登場動畫分鏡（一張 16:9 灰底 2×2 四格，格序固定：中間出現 → 招牌動作 A → 招牌動作 B → 統一發光）、3 星以上金色閃點版分鏡、追擊提示格（選做）。
  道具 ICON＋碎片版**不生圖、走後製**（`pet-parts/scripts/item_icon.py` 從定稿裁，與炮台翅膀、寵物線一致）。
  讀功能之書〈武具系統〉§2.9（外觀以道具之書武具頁為準） → 以外觀定稿為參考圖分批算圖 → 加標籤 → 交付。必須等武具外觀定稿後才做。
  適用於：「武具配件」「登場動畫分鏡」「武具分鏡」「追擊提示」。
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

# 武具配件 Skill

> **執行角色：美術企劃**——關注分鏡與武具定稿的一致性、登場分鏡是否照企劃 §2.9 的動作與格序；交付前逐條跑驗收清單，四格一定要是同一把。

**前置條件：武具外觀必須已經定稿。** 上游是 `weapon-design`。

**道具 ICON 不生圖、走後製**：武具 ICON 就是整組縮圖，從 `weapon-design` 定稿直接裁（Tim 定案 2026-09-30，炮台翅膀、寵物線同規）；碎片版＝同圖左上疊角標。生圖只做登場動畫分鏡。

依賴：

- `配件規格.md` — 各批規格、驗收清單（硬規範）
- `prompt模板.md` — 各產出的提示詞模板
- 共用：道具 ICON 後製 `~/.claude/skills/pet-parts/scripts/item_icon.py`（三條生圖線共用）；分鏡加標籤 `~/.claude/skills/pet-parts/scripts/label_frames.py`；讀企劃 `~/.claude/skills/art-request-sheet/scripts/fetch_plan.py`；補 16:9（追擊提示格用）`~/.claude/skills/boss-design/scripts/fit_canvas.py`
- **`kit 根目錄/references/生圖線共用流程.md`** — 魚線十支共用的工作流程；本檔只寫武具配件線獨有的差異
- **`kit 根目錄/references/image-studio-共用須知.md`** — 產圖層面的問題先查那份

---

## 全程規則

共用規則照 `生圖線共用流程.md` 第三節。本 skill 另加：

- **等定稿**：三個生圖產出（一個選做）全部以 `weapon-design` 的定稿為 `--reference`，不重新發想造型；道具 ICON 不生圖、直接裁定稿。沒有定稿就先走上游
- 盤點後**分批**派出去產；追擊提示格是選做，**使用者要才做**
- **分鏡格序固定**：中間出現 → 招牌動作 A → 招牌動作 B → 統一發光（企劃 §2.9 PM 註記：統一「從中間出現，再做一些動作，最後統一發光」，避免花式進場）。動作 A／B 照企劃 §2.9 該把的原文拆，不增不減
- **文字不交給模型畫**：分鏡標籤、追擊提示的「追擊效果觸發」字樣都由程式或後製加

---

## 流程

### Step 1 — 確認定稿、讀企劃

確認定稿圖在手（沒有就先走 `weapon-design`）。讀企劃：

```sh
python ~/.claude/skills/art-request-sheet/scripts/fetch_plan.py 25ee22985ac9803aa831d54f90bb1910 _工作暫存/武具系統
```

從 `plan.md` 盤點（位置見 `配件規格.md` 第一節）：§2.9 該把的登場動畫四步、§2.9 第 3 點金閃、§2.7〈追擊動畫〉。把**分鏡四格的拆法**列給使用者確認後**一次派出**。從零發想的武具沒有企劃 → 依 mini 企劃的「登場動畫概念」拆四格，一樣先確認。

### Step 2 — 分批算圖

各批生圖彼此獨立，可以同時送：

| 批 | 產出 | 提示詞 | 參考圖 |
|---|---|---|---|
| 1 登場分鏡 | 一張 16:9 灰底 2×2 四格 | `prompt模板.md` 第一節 | 定稿 |
| 2 金閃版分鏡 | 同四格＋金色閃點 | 第二節 | 定稿（首跑實證：直接用外觀定稿，四格姿勢仍與批 1 一致，兩批可並行送） |
| 3 追擊提示格（選做） | 一張 16:9，左武具、右留字區 | 第三節 | 定稿 |

```sh
python3 ~/.claude/skills/image-studio/scripts/image-studio-client.py draw \
  --count 2 --prompt-file <prompt.txt> --reference <定稿圖> --output <_工作暫存/武具名/批次>
```

**全部不加 `--remove-background`**：分鏡與提示格都是灰底交付。

### Step 3 — 後製

- **登場分鏡**：`python ~/.claude/skills/pet-parts/scripts/label_frames.py <圖> <輸出> --cols 2 --rows 2 --captions "中間出現|<動作A>|<動作B>|統一發光" --title 登場動畫`（格數不符會擋下，重抽）
- **金閃版**：同上，`--title "登場動畫（3星金閃）"`
- **追擊提示格**：`fit_canvas.py --whole` 補成 1920×1080 後，用 PIL 在右側加「追擊效果觸發」（片段見 `配件規格.md` 第四節）
- **道具 ICON＋碎片版（後製，不生圖）**：**企劃有 ICON 圖位才做，沒有就跳過不出圖**（Tim 2026-10-02；目前武具道具頁沒有 ICON 圖位）。要做時，定稿是單張 16:9 灰底，直接吃、不用 `--half`／`--grid`：
  ```sh
  python ~/.claude/skills/pet-parts/scripts/item_icon.py <外觀定稿.png> <輸出資料夾> --name <武具名> [--badge <角標.png>]
  ```
  產出 `ICON_<武具名>.png`（512）＋`ICON_<武具名>_尺寸預覽.png`（256／128／64）；碎片版 `ICON_<武具名>_fragment.png`（同圖左上疊碎片角標）自動一起出：角標在網芳 `X:\grp.product.pm1\2. 產品改造\一四部企劃範本\kit-assets\fragment_badge.png`（X 讀不到換 Y:），腳本沒給 `--badge` 就自己去讀；讀不到就只出主圖並提示一行。**角標是線上 UI 素材，不進 repo**（kit 是公開 repo）

### Step 4 — 挑圖與交付

1. 挑圖、開資料夾、自己先跑驗收清單並回報、定稿輸出到指定位置附最終提示詞，照 `生圖線共用流程.md` 第五、六節；驗收清單＝`配件規格.md` 第六節
2. 分鏡一定要對四格是否同一把、位置一致，金閃版要對姿勢與批 1 一致；道具 ICON 看 64px 欄，要認得出類型與主色
3. 前科回寫落點：`配件規格.md` 第七節或 `prompt模板.md`

---

## 維護說明

- 改規格或驗收 → `配件規格.md`
- 改提示詞 → `prompt模板.md`
- 分鏡標籤的邏輯在 `pet-parts/scripts/label_frames.py`，兩線共用，改那邊
- 改道具 ICON 後製 → `pet-parts/scripts/item_icon.py`（三線共用，改那邊）。首版自製的 ICON 生圖模板與 `fragment_badge.py` 已於 v3.16.0 同日移除，不要撿回來——道具 ICON 不生圖

## 貼回企劃（2026-10-02 起）

怎麼貼（交給 `plan-dept14-writer` 貼圖模式、憑證、list→報清單→貼→回讀、圖名、卡位、不准動的圖、落點不確定先問）一律照 `plan-dept14-writer/references/image-slots.md`〈通用貼法〉，落點總表同檔第五節。本 skill 產出的落點：

- 登場動畫（含 3 星金閃版）→ 現況暫放在功能之書〈武具系統〉`2.9` 底下該武具的 H4 toggle，toggle 內清單後直接接 image、不分欄《登場動畫分鏡》《登場動畫分鏡（3星金閃）》；武具道具頁目前沒有這節
- 追擊提示格 → 武具系統 `2.7 動畫︰武具追擊動畫` 右欄《追擊動畫分鏡圖》
- 道具 ICON＋碎片 → 企劃沒有圖位就不做（不出圖、不問開節）
