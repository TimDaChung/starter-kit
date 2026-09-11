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
  - WebSearch
  - TaskCreate
  - TaskUpdate
  - TaskList
---

# /imagen — Nano Banana Pro 圖片生成

使用 Gemini 的 Nano Banana Pro (`gemini-3-pro-image-preview`) 生成圖片。

---

## 核心原則

1. **Prompt 忠於討論結果** — 嚴禁擅自添加使用者沒提到的元素、風格或細節。Prompt 內容必須完全基於對話中確認的內容。
2. **每次都問** — 圖片類型、尺寸、用途不要假設，每次都向使用者確認。
3. **先建議再執行** — 收集完需求後，先給出專業建議，等使用者確認再產 prompt。
4. **記錄偏好** — 每次生圖後，將使用情境記錄到 memory 供未來參考。

---

## 預設視覺規則（除非使用者明確要求不同）

生圖時，使用者沒明確指定以下項目就套默認：

1. **女性角色預設白皮膚**（fair luminous skin / pale skin）— 避免 sun-kissed / tanned / olive / bronzed / dark。使用者明確要求其他膚色才換。
2. **所有角色預設美型**（refined attractive features，手遊 gacha 美學）— 美容貌、比例好。避免 western cartoon / Disney / Pixar / caricature 漂移。Banana Pro 對某些狂野詞（如 "manic"、"wild flying outward"、"battle-tested"）會 bias 到 western 風，需要在 [EXCLUSION] 段明確排除這些風格。
3. **背景必須滿版到四個邊緣**（full-bleed edge-to-edge）— 不要白邊、letterbox、painting frame、gallery framing。在 [COMPOSITION] 段用**正向指令**鎖（"background extends full-bleed to all four edges"）；純粹在 [EXCLUSION] 加 negation 反而可能誘發 frame design。
4. 使用者明確要求不同就依使用者指示。

詳見 memory `feedback_default_fair_skin.md`、`feedback_same_category_unified_style.md`。

---

## 專案既存資產優先（生圖前必做）

**生圖前先掃專案目錄**找有沒有同類別已有資產：
- 立繪 / 角色 portraits → `立繪/`、`assets/portraits/`、`portraits/`
- sprite / 動畫 → `assets/sprites/`、`sprites/`
- UI 元件 → `assets/ui/`、`ui/`
- 地圖 / 背景 → `assets/maps/`、`assets/backgrounds/`、`maps/`

**若找到已有同類別資產：**
1. 把既有資產的「畫風、頭身比例、視角、構圖、留白比例、面向方向、光源、色溫」**鎖死當預設**，不要重新發想
2. 把代表性 1-2 張當 `--ref` 傳 Banana Pro（除了識別/題材 ref 之外，**多塞一張既有資產 ref 強制風格鎖**）
3. 在 prompt 的 Strict Rules 段明寫「the new asset must visually rhyme with the existing project assets — same head-body proportions, same line weight, same shading style, same view angle」
4. 跟使用者確認 lock：「專案既有 N 張同類資產（風格 / 比例 / 視角為...），這次照樣生？要改請明說」

**為什麼**：使用者明確要求「專案已有的東西，畫風跟畫面、人物比例等是要默認參照的」(2026-05-07)。違反等於每次重新發想，4 張一組裡有 1 張飄掉就破壞 roster 視覺押韻。

---

## 批次一致性模式（同類別資產 ≥ 2 張）

**當使用者一次要產 ≥ 2 張同類別資產時**（例：4 個角色立繪、6 種怪物 sprite、一組 UI 元件），切換到批次模式：

1. **先訂統一規格** — 任何生圖前，先決定：風格代號、長寬比、頭身比、視角、光源方向、**面向方向（朝左 / 朝右）**、構圖留白、姿態鎖定條件。
2. **區分「鎖死」vs「可變」** — 鎖死 = 風格 / 比例 / 視角 / 面向 / 光源；可變 = 配色 / 武器 / 場景 / 表情。
3. **把鎖死規格寫進每張 prompt 的 Strict Rules 段** — 同批次所有 prompt 的 Strict Rules 用同一段文字，AI 變化只能在「可變」項。
4. **生完必確認** — 二選一：(a) 每張生完個別確認再套用 (b) 全部生完後一次看統一性 + 符合度。**確認步驟不能省**，避免實裝後才發現要重生。

**單張生圖跳過此模式**，直接走原 Phase 流程。

**為什麼**：同類別資產要視覺押韻。沒鎖規格進 prompt，AI 會飄（頭身比變、視角混、面向鏡像翻）。詳見 memory `feedback_same_category_unified_style.md`。

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
| **長寬比** | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 等 | 依用途建議 |
| **解析度** | 512, 1K, 2K, 4K | 1K |
| **參考圖** | 是否有畫風參考或角色示意圖？ | 無 |

**如果使用者之前用過這個 Skill：**
先讀取 memory 中的歷史記錄，提示：「上次你做 [情境] 用了 [尺寸] + [風格]，這次要沿用還是重新設定？」

---

## Phase 2｜參考圖處理

如果使用者提供參考圖：

### 畫風參考
1. 用 Read 工具查看圖片
2. **向使用者描述你看到的風格特徵**，確認理解正確
3. 將風格特徵轉化為 prompt 中的描述詞（但僅限使用者確認的特徵）

### 角色示意圖
1. 用 Read 工具查看圖片
2. **向使用者確認**：哪些特徵要保留？哪些可以改？
3. 將確認的特徵納入 prompt

**參考圖限制：**
- 角色圖：最多 5 張
- 物件圖：最多 6 張
- 總計：最多 14 張

---

## Phase 3｜建議與討論

收集完需求和參考圖後，**先提出專業建議**再進入 prompt 階段：

### 建議內容

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

### 流程（兩步驟）

#### Step 1：中文 Prompt 確認

建議確認後，**自動整理一份中文版 prompt** 給使用者確認。

**撰寫原則（嚴格遵守）：**
- 只包含討論中**明確提到或確認**的內容
- **不要**自行添加：額外的背景元素、光影描述、情緒氛圍、構圖指示等使用者沒提的東西
- **不要**使用模板化的 prompt 結構（如 "masterpiece, best quality, 4k, detailed" 等套路詞）
- 簡潔直白，描述清楚即可

**展示格式：**

```
## Prompt 確認

📝 中文 Prompt：
> [完整中文 prompt，基於討論內容整理]

📐 長寬比：[ratio]
📏 解析度：[size]
🖼️ 參考圖：[有/無，幾張]

沒問題的話我就轉英文並開始生成。要修改什麼嗎？
```

#### Step 2：轉換英文並交付或生成

使用者確認中文 prompt 沒問題後（如「好」「OK」「沒問題」「可以」），**直接將中文 prompt 翻譯為英文。**

翻譯原則：
- 忠於中文 prompt 的內容，不增不減
- 使用自然英文描述
- 不加入翻譯過程中想到的「補充」

翻譯完成後，依據模式執行：
- **Prompt 模式**：將英文 prompt 連同建議的參數設定（長寬比、解析度）一併提供給使用者，方便直接貼到 Google AI Studio 使用。同時提醒參考圖的使用方式。
- **API 模式**：直接呼叫 API 生成（見 Phase 5）。

**模式判斷：** 預設使用 Prompt 模式（只產出 prompt）。如果使用者的 API Key 確認可用（曾成功呼叫過），自動切換為 API 模式。

---

## Phase 5｜圖片生成（API 模式）

> 此階段僅在 API 模式下執行。如果是 Prompt 模式，跳過此階段直接進入 Phase 6。

### 檔案命名與存放

- 預設存放位置：`~/.claude/gemini/`
- 檔名格式：`{簡短描述}_{日期}_{序號}.png`
- 範例：`fire_monster_20260331_01.png`

如果使用者指定了其他路徑，使用指定路徑。

### 執行生成

使用 curl 呼叫 Gemini API：

1. 將參考圖轉為 base64
2. 組裝 JSON payload（含 prompt、參考圖 inline_data、generationConfig）
3. POST 到 `https://generativelanguage.googleapis.com/v1beta/models/{模型}:generateContent`
4. 從回應中提取 base64 圖片資料並儲存為 PNG

### 生成後

1. 用 Read 工具查看生成的圖片，確認有正常產出
2. 告知使用者圖片路徑
3. 詢問：「滿意嗎？要調整 prompt 重新生成，還是這張可以用？」

如果使用者要調整：
- 根據回饋修改 prompt（同樣只改使用者提到的部分）
- 重新確認並生成

---

## Phase 5.5｜Prompt 交付（Prompt 模式）

> 此階段僅在 Prompt 模式下執行。

將英文 prompt 以方便複製的格式呈現：

```
## 生成資訊

📝 英文 Prompt：
> [完整英文 prompt]

📐 建議長寬比：[ratio]
📏 建議解析度：[size]
🖼️ 參考圖：[幾張，提醒一起上傳到 AI Studio]

💡 使用方式：到 Google AI Studio 貼上 prompt，上傳參考圖，選擇對應的長寬比即可生成。
```

如果使用者要調整：
- 根據回饋修改 prompt（同樣只改使用者提到的部分）
- 重新產出英文版

---

## Phase 6｜記憶更新

每次完成 prompt 產出或成功生成圖片後，更新 memory 記錄。

### 記錄格式

在 memory 目錄中更新或建立 `imagen_history.md`：

```markdown
---
name: imagen 使用記錄
description: /imagen skill 的歷史使用情境、尺寸、風格偏好，用於下次生圖時參考
type: user
---

## 使用記錄

| 日期 | 主題 | 用途 | 風格 | 長寬比 | 解析度 | 備註 |
|------|------|------|------|--------|--------|------|
| 2026-03-31 | 火焰怪物 | 卡牌插圖 | 日系動漫 | 3:4 | 2K | 有參考圖 |
```

同時確認 `MEMORY.md` 中有對應的索引條目。

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

| 錯誤 | 處理方式 |
|------|---------|
| API Key 無效 | 提示使用者檢查 `.env` 中的 `GEMINI_API_KEY` |
| 生成失敗（安全過濾） | 告知使用者，建議調整 prompt 中可能觸發過濾的詞彙 |
| 參考圖格式不支援 | 支援 JPG/PNG/WebP/GIF，提示使用者轉換格式 |
| 網路錯誤 | 提示檢查網路連線，可重試一次 |

## 銜接：更專精的生圖 skill

- 有參考圖、想先還原其風格 → 先用 `image-to-prompt` 逆向出中性可換角色的 prompt，再回來生圖
- 角色立繪／半身像 → `imagen-portrait`
- UI 素材（icon／卡框／banner） → `imagen-ui`
- 2D 地圖／場景 → `generate2dmap`
- 角色 sprite／動畫 → `generate2dsprite`（chibi／Q 版風用 `generate2dsprite-chibi`）
