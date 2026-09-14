---
name: imagen
version: 1.0.0
description: |
  Nano Banana Pro (gemini-3-pro-image-preview) 通用生圖。
  對話確認需求 + prompt 後生圖，支援參考圖。
  立繪用 imagen-portrait / UI 用 imagen-ui，其他通用需求才用這支。
  觸發：「畫一張」「生圖」「imagen」「產圖」「生成圖片」。
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Agent
  - AskUserQuestion
---

# /imagen — Nano Banana Pro 圖片生成

> **執行角色：美術**——關注風格一致、可讀性、資產規格（尺寸 / 切圖 / 命名）。

使用 Gemini 的 Nano Banana Pro (`gemini-3-pro-image-preview`) 生成圖片。三支 imagen skill 的共用流程、格式、指令集中在 `references/common.md`（下文以「common.md §N」引用）；五支生圖 skill 共用的一致性鎖規則在 `references/consistency-rules.md`。

---

## 核心原則

1. **Prompt 忠於討論結果** — 嚴禁擅自添加使用者沒提到的元素、風格或細節。Prompt 內容必須完全基於對話中確認的內容。
2. **每次都問** — 圖片類型、尺寸、用途不要假設，每次都向使用者確認。
3. **先建議再執行** — 收集完需求後，先給出專業建議，等使用者確認再產 prompt。
4. **記錄偏好** — 每次生圖後，將使用情境記錄到 `<project-dir>/docs/imagen_history.md` 供未來參考（common.md §8）。

---

## 一致性規則（生圖前必讀）

- **預設視覺規則**：女性白皮膚、所有角色美型（[EXCLUSION] 排除 western cartoon 漂移）、背景滿版四邊用正向指令鎖；使用者明說即覆蓋。詳見 common.md §1。
- **專案既存資產優先（pre-flight 必做）**：先掃 `立繪/`、`assets/sprites/`、`assets/ui/`、`assets/maps/` 等同類資產；有就鎖畫風 / 頭身比 / 視角 / 構圖 / 面向 / 光源 / 色溫當預設、代表作當 `--ref`、Strict Rules 明寫 visually rhyme、跟使用者確認 lock。詳見 common.md §2（imagen 完整掃描路徑表在該節）。
- **批次一致性模式（≥ 2 張同類資產）**：先訂統一規格 → 分鎖死 / 可變 → 鎖死規格用同一段文字寫進每張 Strict Rules → 生完必確認；單張跳過。詳見 common.md §3。
- **第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`**（Style Bible + contact sheet QC；`references/consistency-rules.md` §4）。

---

## Phase 1｜需求收集

用 AskUserQuestion 依序確認以下資訊（可合併問，不要一次問太多）：

### 第一輪：核心需求

| 項目 | 說明 | 範例 |
|------|------|------|
| **主題** | 要畫什麼？ | 「火焰怪物」「遊戲 UI 背景」「卡牌插圖」 |
| **用途** | 這張圖要用在哪裡？ | 「遊戲內角色立繪」「行銷素材」「UI icon」「概念驗證」 |
| **風格** | 期望的美術風格？ | 「日系動漫」「寫實」「像素風」「扁平設計」 |

### 第二輪：技術規格

| 項目 | 選項 | 預設 |
|------|------|------|
| **長寬比** | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 | 依用途建議 |
| **解析度** | 1K, 2K, 4K | 1K |
| **參考圖** | 是否有畫風參考或角色示意圖？ | 無 |

**如果使用者之前用過這個 Skill**：先讀 `<project-dir>/docs/imagen_history.md`，提示上次的情境 / 尺寸 / 風格問要不要沿用（common.md §8）。

---

## Phase 2｜參考圖處理

有參考圖就依 common.md §5：先 Read 看圖 → **畫風參考**向使用者描述你看到的風格特徵確認理解；**角色示意圖**向使用者確認哪些特徵保留、哪些可改 → 只把確認過的特徵寫進 prompt。上限 6 張。

---

## Phase 3｜建議與討論

收集完需求和參考圖後，**先提出專業建議**再進入 prompt 階段：

```
## 建議

### 長寬比
建議使用 [比例]，因為 [原因]。

### 風格方向
根據你的需求，建議 [風格描述]。
[如果有參考圖] 從參考圖中我看到 [特徵]，會保留這些元素。

### 注意事項
- [任何可能影響生成品質的提醒]
- [Nano Banana Pro 對某些主題的已知限制（如有）]

要調整什麼嗎？還是可以進入 prompt 階段？
```

等使用者確認後進入 Phase 4。如果使用者表示沒問題（如「好」「OK」「可以」），直接進入 Phase 4，不需再問。

---

## Phase 4｜Prompt 撰寫與確認

### Step 1：中文 Prompt 確認

建議確認後，**自動整理一份中文版 prompt** 給使用者確認。撰寫原則與展示格式見 common.md §4；imagen **省略** 🎨 風格 / 🧩 boilerplate / 📦 元件三行。

### Step 2：轉英文並判定模式

使用者確認後直接把中文 prompt 翻成英文（忠於原文、不增不減，common.md §4）。接著依 common.md §9 判定模式——**整個任務只判這一次**：

- **API 模式**（有 `GEMINI_API_KEY`）→ Phase 5
- **Prompt 模式**（沒有 key）→ Phase 5.5

---

## Phase 5｜圖片生成（API 模式）

1. **存放位置與檔名**：依 common.md §7 決定（fallback `<cwd>/imagen/`；檔名 `{簡短描述}_{日期}_{序號}.png`，例 `fire_monster_20260331_01.png`）。
2. **執行**：英文 prompt Write 到 `prompt-final.txt`，呼叫 `~/.claude/skills/imagen/bin/generate.py`（標準指令、`--ratio` / `--size` 合法值見 common.md §9）。
3. **生成後**：Read 看圖 → 回報路徑 → 問是否滿意；要調整只改使用者提到的部分（common.md §6）。

---

## Phase 5.5｜Prompt 交付（Prompt 模式）

以 common.md §9 的「生成資訊」格式交付英文 prompt + 建議長寬比 / 解析度 + 參考圖上傳提醒。要調整 → 只改使用者提到的部分，重新產出英文版。

---

## Phase 6｜記憶更新

每次完成 prompt 產出或成功生成圖片後，追加一列到 `<project-dir>/docs/imagen_history.md`（6 欄位與範例見 common.md §8）。

---

## 可用長寬比速查

| 長寬比 | 適用場景 |
|--------|---------|
| 1:1 | Icon、頭像、社群貼文 |
| 2:3 | 手機直向插圖 |
| 3:2 | 橫向場景、桌面桌布 |
| 3:4 | 卡牌插圖、人物立繪 |
| 4:3 | 傳統橫向、簡報素材 |
| 4:5 | Instagram 貼文 |
| 5:4 | 接近方形的橫向圖 |
| 9:16 | 手機全螢幕、Story |
| 16:9 | 橫幅 Banner、遊戲場景 |
| 21:9 | 超寬橫幅 |

---

## 錯誤處理

API Key 無效 / 安全過濾 / 參考圖格式 / 網路錯誤的處理見 common.md §9 通用錯誤處理表。

## 銜接：更專精的生圖 skill

- 有參考圖、想先還原其風格 → 先用 `image-to-prompt` 逆向出中性可換角色的 prompt，再回來生圖
- 角色立繪／半身像 → `imagen-portrait`
- UI 素材（icon／卡框／banner） → `imagen-ui`
- 2D 地圖／場景 → `generate2dmap`
- 角色 sprite／動畫 → `generate2dsprite`；chibi／Q 版風用 `generate2dsprite`（`art_style=cel_shaded_chibi`）
- 第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`
