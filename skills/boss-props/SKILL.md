---
name: boss-props
version: 1.0.0
description: |
  捕魚機 Boss「表演道具與等級系列」產出流程，boss-design 的配套：捕獲／彩金表演裡玩法用到的道具
  （幻石、罐子、老虎機、轉盤、爆竹…）。一個系列畫在同一張 16:9 灰底圖，等級差異用「累加法」
  （每升一級多一個看得見的新元素，不只換顏色），大小與等級名稱由腳本統一。企劃有寫照企劃，沒寫就提案討論。
  適用於：「Boss 道具」「表演道具」「等級系列」「幻石」「罐子造型」「道具等級圖」。
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

# Boss 表演道具 Skill

> **執行角色：美術企劃**——關注道具的等級差異是否一眼可辨（不只靠顏色）、系列風格是否衍生自 Boss 定稿、是否忠實還原企劃；交付前逐條跑驗收清單。

**前置條件：Boss 外觀最好已經定稿**（`boss-design`）。道具的畫風與高級飾件都衍生自 Boss，沒有定稿就只能靠文字描述畫風。

依賴同資料夾的檔案：

- `道具規格.md` — 等級差異法則、畫面規格、驗收清單（硬規範）
- `prompt模板.md` — 等級系列與同級異形的提示詞模板
- `scripts/lineup.py` — 找出每件道具、統一大小、加上等級名稱

共用的：

- 讀企劃：`~/.claude/skills/pet-evolution/scripts/fetch_plan.py`（`--list bosses`）
- **`kit 根目錄/references/image-studio-共用須知.md`** — 產圖層面的問題先查那份

---

## 全程規則

- **一個系列畫在同一張圖**，不要一件一件生
- **每輪至少算 2 張**，全部看完挑最好的
- **有企劃的一次全部盤點出來**，不要一件一件問；只有企劃沒寫到的等級差異才跟使用者討論
- **不修改任何既有企劃**
- 中間產物進 `_工作暫存/`（已 gitignore）；**未上線的設計圖不進 repo**

---

## 流程

### Step 1 — 盤點道具

**模式 A（既有企劃）**：讀企劃

```sh
NOTION_KEY=$(tr -d '\r\n ' < "<四部readonly_token.txt 路徑>") \
  python ~/.claude/skills/pet-evolution/scripts/fetch_plan.py <page_id> _工作暫存/<Boss名>
```

在彩金表演、玩法、機制段落找出所有道具，列成清單給使用者確認：

| 道具 | 等級／種類 | 企劃有沒有寫外觀 | 同時上盤面？ |
|---|---|---|---|
| 例：幻石 | 灰／藍／紫／紅／彩 | 只寫顏色＋「外觀要看得出等級差異」 | 是（一輪 8 顆） |

「同時上盤面」決定 Step 4 要不要統一大小。

**模式 B（接在 boss-design 從零發想之後）**：道具名稱與等級數來自 `boss-design` 的 mini 企劃〈表演與玩法〉段落。

### Step 2 — 等級階梯

- **企劃有寫每級的外觀**：照企劃
- **企劃只寫顏色、或沒寫**：依 `道具規格.md` 第二節的累加法，**提出每一級新增什麼元素**，高級飾件取自 Boss 的招牌部位，最高級要有質變。**列成表給使用者拍板**才算圖

### Step 3 — 算圖

Read `prompt模板.md` 填空，存到 `_工作暫存/prompt_<Boss名>_<道具名>.txt`。

```sh
python3 ~/.claude/skills/image-studio/scripts/image-studio-client.py draw \
  --count 2 --prompt-file <prompt.txt> --reference <Boss定稿圖> --output <_工作暫存/Boss名/道具名>
```

沒有 Boss 定稿就不帶 `--reference`，畫風用文字描述。

### Step 4 — 整理成交付圖

```sh
python ~/.claude/skills/boss-props/scripts/lineup.py <原圖.png> <輸出.png> \
  --labels 灰幻石,藍幻石,紫幻石,紅幻石,彩幻石 [--equalize]
```

- **同時上盤面的道具加 `--equalize`**（統一高度、平均間距）；本來就有大小差的不加
- 腳本找到的件數要等於標籤數，不符會停下並列出找到的位置——通常是兩件黏在一起或特效斷開，重抽或加大間距

### Step 5 — 挑圖與交付

1. 兩張都整理後複製到使用者看得到的資料夾，`explorer.exe` 開給他看
2. **自己先逐條跑 `道具規格.md` 第五節驗收清單**，主動回報哪張好、好在哪
3. 定稿交整理後的圖＋原圖＋最終提示詞
4. 暴露了新規則或前科 → 回寫 `道具規格.md` 第六節或 `prompt模板.md`
5. **主動問下一步**：道具定稿後，還沒做背景就提 `boss-scene`；背景也好了就提 `boss-demo`（定稿的 Boss、背景、道具直接當 demo 素材，取代 emoji 佔位）

---

## 維護說明

- 改等級法則或驗收 → `道具規格.md`
- 改提示詞 → `prompt模板.md`
- 改切件、統一大小、標籤 → `scripts/lineup.py`

## 貼回企劃（2026-10-02 起）

定稿後要放進 Notion 企劃時，交給 `plan-dept14-writer` 的**貼圖模式**（第十一節，腳本 `plan-dept14-writer/scripts/paste_images.py`；落點總表 `plan-dept14-writer/references/image-slots.md`）。PM 給目標頁網址 → `list` 找右欄與卡位 → 報清單取得同意 → 貼 → 回讀。本 skill 產出的落點：

- 道具等級系列 → Boss 頁 `3.2` 底下對應玩法那節右欄（例：賽特 3.2.C、劍魔 3.2.E），caption《<道具>等級&特效示意》
- 範本沒有這節；實頁沒有對應節時先問 PM 開哪節
