---
name: imagen
version: 1.0.0
description: |
  通用生圖（image-studio GPT 線）。
  對話確認需求 + prompt 後生圖，支援參考圖。
  立繪用 imagen-portrait / UI 用 imagen-ui，其他通用需求才用這支。
  內建可選風格庫（references/styles/）：極簡團子卡通風（1.5–2 頭身插畫／貼圖／四格）、動物插圖風（2.5–3 頭身角色扮演動物、平塗色底＋圖案裝飾）、手繪奇幻風（全員寫實比例、水彩＋沾水筆、低彩度大地色、模型箱般的手繪場景）、手繪童書風（全員 Q 版、彩色鉛筆＋淡水彩、溫暖明亮的兒童繪本）。
  觸發：「畫一張」「生圖」「imagen」「產圖」「生成圖片」「團子風」「極簡卡通風」「療癒系畫風」「四格漫畫風」「貼圖風」「動物插圖風」「繪本貓」「手繪奇幻風」「戰略 RPG 插畫風」「水彩手繪風」「手繪童書風」「兒童繪本風」「繪本風」「有哪些畫風」。
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Agent
  - AskUserQuestion
---

# /imagen — 通用圖片生成

> **執行角色：美術**——關注風格一致、可讀性、資產規格（尺寸 / 切圖 / 命名）。

通用生圖 skill。四支 imagen skill 的共用流程、格式、指令集中在 `references/common.md`（下文以「common.md §N」引用）；六支生圖 skill 共用的一致性鎖規則在 `references/consistency-rules.md`；生圖引擎（唯一引擎＝image-studio GPT 線、可用性判定、呼叫契約、失敗處理）在 `references/draw-engines.md`。

---

## 核心原則

1. **Prompt 忠於討論結果** — 嚴禁擅自添加使用者沒提到的元素、風格或細節。Prompt 內容必須完全基於對話中確認的內容。
2. **缺什麼問什麼** — 圖片類型、尺寸、用途不假設；使用者已經講明的不再問，缺的一次問完。使用者說「直接生」就跳過 Phase 3 的建議與 Phase 4 的確認框，把建議與最終 prompt 附在結果一起回報。
3. **先建議再執行** — 收集完需求後，先給出專業建議，等使用者確認再產 prompt。
4. **記錄偏好** — 每次生圖後，將使用情境記錄到 `<project-dir>/docs/imagen_history.md` 供未來參考（common.md §8）。

---

## 一致性規則（生圖前必讀）

- **預設視覺規則**：女性白皮膚、所有角色美型（[EXCLUSION] 排除 western cartoon 漂移）、背景滿版四邊用正向指令鎖；使用者明說即覆蓋。詳見 common.md §1。
- **專案既存資產優先（pre-flight 必做）**：先掃 `立繪/`、`assets/sprites/`、`assets/ui/`、`assets/maps/` 等同類資產；有就鎖畫風 / 頭身比 / 視角 / 構圖 / 面向 / 光源 / 色溫當預設、代表作當 `--reference`、Strict Rules 明寫 visually rhyme、跟使用者確認 lock。詳見 common.md §2（imagen 完整掃描路徑表在該節）。
- **批次一致性模式（≥ 2 張同類資產）**：先訂統一規格 → 分鎖死 / 可變 → 鎖死規格用同一段文字寫進每張 Strict Rules → 生完必確認；單張跳過。詳見 common.md §3。
- **第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`**（Style Bible + contact sheet QC；`references/consistency-rules.md` §4）。

---

## 風格庫（選配）

`references/styles/` 一份檔一套可重用畫風，每份固定五節：風格定義（含眼型表）、用途變體、英文 prompt 區塊、鐵則、驗收清單。使用者點名風格、或 Phase 1「風格」的描述對得上時套用；對不上就照一般流程，不硬套。

| 風格 | 檔案 | 頭身 | 一句話 | 適合 |
|---|---|---|---|---|
| 極簡團子卡通風 | `references/styles/minimal-chibi.md` | 1.5–2 | 圓團子＋最少五官，靠表情說話，大量留白 | 插畫、貼圖、四格漫畫、周邊 |
| 動物插圖風 | `references/styles/animal-illustration.md` | 2.5–3 | 畫得很省的真貓骨架角色，角色扮演，平塗色底＋圖案裝飾（不畫場景） | 主視覺、卡牌／卡套插圖、主題海報、群像 |
| 手繪奇幻風 | `references/styles/handdrawn-fantasy.md` | 全員寫實（人型 6–7，至少 5） | 水彩＋沾水筆手繪、低彩度大地色，模型箱般的手繪場景 | 角色立繪、場景插畫、劇情 CG、故事書頁 |
| 手繪童書風 | `references/styles/handdrawn-picturebook.md` | 全員 Q 版 2–2.5 | 彩色鉛筆＋淡水彩、圓潤玩具感、溫暖明亮，連敵人都可愛 | 兒童繪本頁、冒險場面、角色介紹、封面 |

套用時：
1. **整份讀風格檔**，不憑印象：挑眼型（填 `{EYES}`）、物種（`{ANIMAL}`，有此欄位的風格）、用途變體
2. **組 prompt**：`[SUBJECT]` → 風格檔 `[STYLE]`（一字不改）→ `[VARIANT]` → `[EXCLUSION]`；Phase 4 中文確認框照常
3. **common.md §1 預設視覺規則不適用**（美型、排除 western cartoon 會跟這些風格打架），以風格檔的 `[EXCLUSION]` 為準
4. 生完**用風格檔的驗收清單逐項看**，不過就修 prompt 重算；首張核准後當同批後續的 `--reference`
5. **風格檔是唯一來源**：使用者口頭修正風格 → 改風格檔（kit 檔走 `issue-triage` 建議模式回報維護者），不只在這次 prompt 裡改

共通鐵則：prompt 不寫作者名、角色名、作品名，只用風格檔的中性描述；他人作品不當 `--reference` 餵引擎；文字一律後製。

說「繪本風」沒講寫實或 Q 版時，問一句要哪套（兩套比例不混用）。

新增風格：給參考（作品連結、圖）→ 看實際作品（`image-to-prompt` 拆解或並排看）→ 照五節結構寫 `references/styles/<slug>.md` → 補進上表。只差眼型、配色的加進既有檔當選項，不另開檔。

---

## Phase 1｜需求收集

用 AskUserQuestion 依序確認以下資訊（可合併問，不要一次問太多）：

### 第一輪：核心需求

| 項目 | 說明 | 範例 |
|------|------|------|
| **主題** | 要畫什麼？ | 「火焰怪物」「遊戲 UI 背景」「卡牌插圖」 |
| **用途** | 這張圖要用在哪裡？ | 「遊戲內角色立繪」「行銷素材」「UI icon」「概念驗證」 |
| **風格** | 期望的美術風格？（對得上〈風格庫〉就套用） | 「日系動漫」「寫實」「像素風」「扁平設計」「團子風」「動物插圖」「手繪奇幻」「手繪童書」 |

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
- [生圖模型對某些主題的已知限制（如有）]

要調整什麼嗎？還是可以進入 prompt 階段？
```

等使用者確認後進入 Phase 4。如果使用者表示沒問題（如「好」「OK」「可以」），直接進入 Phase 4，不需再問。

---

## Phase 4｜Prompt 撰寫與確認

### Step 1：中文 Prompt 確認

建議確認後，**自動整理一份中文版 prompt** 給使用者確認。撰寫原則與展示格式見 common.md §4；imagen **省略** 🎨 風格 / 🧩 boilerplate / 📦 元件三行。

### Step 2：轉英文

使用者確認後直接把中文 prompt 翻成英文（忠於原文、不增不減，common.md §4）。**長寬比與解析度沒有對應 flag，要寫進 prompt 文字**（例：`3:4 portrait aspect ratio, 2K resolution`）。

接著依 draw-engines.md §1 確認引擎可用（image-studio 已裝＋憑證未過期，**整個任務只判這一次**）：可用 → Phase 5；不可用 → 生圖停止，照 kit `references/image-studio-共用須知.md` 第二節處理（沒裝過走〈首裝流程〉、過期走換季流程），不改走其他生圖途徑。

使用者只要 prompt 文字、不要實際生圖 → 走 Phase 5.5。

---

## Phase 5｜圖片生成

1. **存放位置與檔名**：依 common.md §7 決定（fallback `<cwd>/imagen/`；檔名 `{簡短描述}_{日期}_{序號}.png`，例 `fire_monster_20260331_01.png`）。
2. **執行**：英文 prompt Write 到 `prompt-final.txt`，再呼叫 image-studio client（標準指令見 common.md §9 / draw-engines.md §3）；預設一次 2 張（驗收挑一張；使用者指定張數照指定，不自行加抽），每批只發一次請求、不自動重試。
3. **生成後**：Read 看圖 → 回報路徑 → 問是否滿意；要調整只改使用者提到的部分（common.md §6）。整批失敗的診斷與回報見 draw-engines.md §4。

---

## Phase 5.5｜Prompt 交付（使用者只要文字時）

使用者說「只要 prompt 就好」「我自己拿去生」時跳過 Phase 5，以 common.md §9 的「生成資訊」格式交付英文 prompt + 建議長寬比 / 解析度 + 參考圖提醒。要調整 → 只改使用者提到的部分，重新產出英文版。

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

安全過濾 / 參考圖格式 / 網路錯誤的處理見 common.md §9 通用錯誤處理表；整批失敗的診斷分流見 draw-engines.md §4。

## 銜接：更專精的生圖 skill

- 有參考圖、想先還原其風格 → 先用 `image-to-prompt` 逆向出中性可換角色的 prompt，再回來生圖
- 角色立繪／半身像 → `imagen-portrait`
- UI 素材（icon／卡框／banner） → `imagen-ui`
- 2D 地圖／場景 → `generate2dmap`
- 角色 sprite／動畫 → `generate2dsprite`；chibi／Q 版風用 `generate2dsprite`（`art_style=cel_shaded_chibi`）
- 第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`

## 貼回企劃（2026-10-02 起）

定稿後要放進 Notion 企劃時，交給 `plan-dept14-writer` 的**貼圖模式**（第十一節，腳本 `plan-dept14-writer/scripts/paste_images.py`；落點總表 `plan-dept14-writer/references/image-slots.md`）。PM 給目標頁網址 → `list` 找右欄與卡位 → 報清單取得同意 → 貼 → 回讀。本 skill 產出的落點：

- 介面示意／wireframe → 功能頁「呈現 > 介面 > <畫面>」右欄，換掉卡位（一部「圖片放置區」→ 圖上方《n.xxx示意》；四部「窩是示意圖」佔位圖 → caption《<畫面名>》）；版本頁不直接貼
