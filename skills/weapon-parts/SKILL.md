---
name: weapon-parts
version: 1.0.0
description: |
  魚樂園陣營戰「武具」配件產出流程，weapon-design 的下游：武具 ICON（含 64px 可讀性檢查）、碎片 ICON（程式疊角標，不生圖）、
  登場動畫分鏡（一張 2×2 四格，格序固定：中間出現 → 招牌動作 A → 招牌動作 B → 統一發光）、3 星以上金色閃點版分鏡、追擊提示格（選做）。
  讀功能之書〈武具系統〉 → 以外觀定稿為參考圖分批算圖 → 後製 → 交付。必須等武具外觀定稿後才做。
  適用於：「武具配件」「武具 ICON」「武具碎片」「登場動畫分鏡」「武具分鏡」「追擊提示」。
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

> **執行角色：美術企劃**——關注配件與武具定稿的一致性、登場分鏡是否照企劃 §2.9 的動作與格序；交付前逐條跑驗收清單，ICON 一定看 64px。

**前置條件：武具外觀必須已經定稿。** 上游是 `weapon-design`。

依賴：

- `配件規格.md` — 各批規格、驗收清單（硬規範）
- `prompt模板.md` — 各產出的提示詞模板
- `scripts/fragment_badge.py` — 碎片 ICON：把角標疊到武具 ICON 左上
- `assets/` — 通用碎片角標 PNG 放這裡（見 `配件規格.md` 第三節）
- 共用：ICON 切正方形與尺寸預覽 `~/.claude/skills/pet-parts/scripts/icon_check.py`；分鏡加標籤 `~/.claude/skills/pet-parts/scripts/label_frames.py`；讀企劃 `~/.claude/skills/pet-evolution/scripts/fetch_plan.py`；補 16:9 `~/.claude/skills/boss-design/scripts/fit_canvas.py`
- **`kit 根目錄/references/image-studio-共用須知.md`** — 產圖層面的問題先查那份

---

## 全程規則

- **等定稿**：五個產出全部以 `weapon-design` 的定稿為 `--reference`，不重新發想造型；沒有定稿就先走上游
- **有企劃的一次全部盤點、分批派出去產**，不要一件一件問；企劃沒寫到的才詢問。追擊提示格是選做，**使用者要才做**
- **每輪至少算 2 張**，全部看完挑最好的
- **分鏡格序固定**：中間出現 → 招牌動作 A → 招牌動作 B → 統一發光（企劃 §2.9 PM 註記：統一「從中間出現，再做一些動作，最後統一發光」，避免花式進場）。動作 A／B 照企劃 §2.9 該把的原文拆，不增不減
- **文字不交給模型畫**：分鏡標籤、追擊提示的「追擊效果觸發」字樣都由程式或後製加
- **不修改既有企劃**；文字與圖不一致時列出來問
- 中間產物進 `_工作暫存/`（已 gitignore）；**未上線的設計圖不進 repo**

---

## 流程

### Step 1 — 確認定稿、讀企劃

確認定稿圖在手（沒有就先走 `weapon-design`）。讀企劃：

```sh
NOTION_KEY=$(tr -d '\r\n ' < "<四部readonly_token.txt 路徑>") \
  python ~/.claude/skills/pet-evolution/scripts/fetch_plan.py 25ee22985ac9803aa831d54f90bb1910 _工作暫存/武具系統
```

從 `plan.md` 盤點（位置見 `配件規格.md` 第一節）：§2.7 碎片美術需求、§2.9 該把的登場動畫四步、§2.9 第 3 點金閃、§2.7〈追擊動畫〉。把**分鏡四格的拆法**列給使用者確認後**一次派出**。從零發想的武具沒有企劃 → 依 mini 企劃的「登場動畫概念」拆四格，一樣先確認。

### Step 2 — 分批算圖

四批生圖彼此獨立，可以同時送；碎片不生圖：

| 批 | 產出 | 提示詞 | 參考圖 |
|---|---|---|---|
| 1 武具 ICON | 一張正方形構圖 | `prompt模板.md` 第一節 | 定稿 |
| 2 碎片 ICON | **不生圖**：批 1 定稿 ＋ `assets/` 角標 → `scripts/fragment_badge.py` | — | — |
| 3 登場分鏡 | 一張 16:9 灰底 2×2 四格 | 第三節 | 定稿 |
| 4 金閃版分鏡 | 同四格＋金色閃點 | 第四節 | 定稿（或批 3 定稿，鎖姿勢） |
| 5 追擊提示格（選做） | 一張 16:9，左武具、右留字區 | 第五節 | 定稿 |

```sh
python3 ~/.claude/skills/image-studio/scripts/image-studio-client.py draw \
  --count 2 --prompt-file <prompt.txt> --reference <定稿圖> --output <_工作暫存/武具名/批次>
```

**全部不加 `--remove-background`**：ICON 自帶底板、分鏡與提示格都是灰底交付。

### Step 3 — 後製

- **ICON**：`python ~/.claude/skills/pet-parts/scripts/icon_check.py <圖> <輸出資料夾> --names <武具名>`，產出 `ICON_<武具名>.png` 與 `ICON_尺寸預覽.png`；**64px 欄看不懂就重抽**
- **碎片 ICON**：`python ~/.claude/skills/weapon-parts/scripts/fragment_badge.py <ICON_武具名.png> <角標.png>`，`--scale 0.28`，輸出同資料夾 `ICON_<武具名>_fragment.png`（角標疊左上；可調 `--scale`、`--corner`、`--margin`）。角標固定用 `assets/fragment_badge.png`（線上碎片圖示的裁切，見 `配件規格.md` 第三節）
- **登場分鏡**：`python ~/.claude/skills/pet-parts/scripts/label_frames.py <圖> <輸出> --cols 2 --rows 2 --captions "中間出現|<動作A>|<動作B>|統一發光" --title 登場動畫`（格數不符會擋下，重抽）
- **金閃版**：同上，`--title "登場動畫（3星金閃）"`
- **追擊提示格**：`fit_canvas.py --whole` 補成 1920×1080 後，用 PIL 在右側加「追擊效果觸發」（片段見 `配件規格.md` 第六節）

### Step 4 — 挑圖與交付

1. 複製到使用者看得到的資料夾，`explorer.exe` 開給他看
2. **自己先逐條跑 `配件規格.md` 第八節**，主動回報哪張好、好在哪；ICON 一定要看 64px 欄，分鏡一定要對四格是否同一把、位置一致
3. 定稿輸出到使用者指定位置，附最終提示詞
4. 暴露了新規則或前科 → 回寫 `配件規格.md` 第九節或 `prompt模板.md`

---

## 維護說明

- 改規格或驗收 → `配件規格.md`
- 改提示詞 → `prompt模板.md`
- 改角標比例、位置、輸出命名 → `scripts/fragment_badge.py`
- 換通用角標 → 替換 `assets/` 裡的 PNG，檔名記在 `配件規格.md` 第三節
- ICON 切割與分鏡標籤的邏輯在 `pet-parts/scripts/`，兩線共用，改那邊
