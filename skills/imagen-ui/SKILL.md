---
name: imagen-ui
version: 1.0.0
description: |
  Nano Banana Pro 生成 RPG 手遊 UI 素材（button / icon / frame / banner / popup / rarity_glow 等 15 種元件）。預設米哈遊 / 方舟 / NIKKE 等高營收手遊風格 — 6 風格庫 + 英文 boilerplate。
  觸發：「UI 素材」「icon」「卡框」「頭像框」「banner」「技能 icon」「稀有度光效」「米哈遊 UI」「方舟 UI」。
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Agent
  - AskUserQuestion
---

# /imagen-ui — RPG 手遊 UI 素材生成

> **執行角色：美術**——關注風格一致、可讀性、UI 資產規格；產出後切**工程**視角核對切圖與尺寸可直接使用。

使用 Gemini 的 Nano Banana Pro (`gemini-3-pro-image-preview`) 生成 RPG 手遊 UI 元件，預設套用高營收手遊（米哈遊、明日方舟等）的 UI 視覺語言。

---

## 核心原則

1. **Prompt 忠於討論結果** — 不擅自加裝飾元素。
2. **預設手遊高品質 UI 審美** — 金屬質感 / 漸層 / 半透明 / 細節描邊，但**不喧賓奪主**（UI 元件背後通常會放文字或其他內容）。
3. **每次都問元件類型** — UI 是功能性設計，必須先確定要做哪一類元件。
4. **去背優先** — 大多數 UI 元件都要去背才能融入遊戲畫面；Gemini 輸出沒有 alpha，所以生成時鎖純品紅 `#FF00FF` 滿版背景，Phase 5 再用 magenta chroma-key 後製去背。
5. **記錄偏好** — 寫入 `<project-dir>/docs/imagen_history.md`。

---

## 預設視覺規則（除非使用者明確要求不同）

生圖時，使用者沒明確指定以下項目就套預設：

1. **女性角色預設白皮膚**（fair luminous skin / pale skin）— 避免 sun-kissed / tanned / olive / bronzed / dark。使用者明確要求其他膚色才換。
2. **所有角色預設美型**（refined attractive features，手遊 gacha 美學）— 美容貌、比例好。避免 western cartoon / Disney / Pixar / caricature 漂移。Banana Pro 對某些狂野詞會 bias 到 western 風，需要在 [EXCLUSION] 段明確排除這些風格。
3. **背景 / 元件背景必須滿版到四個邊緣**（full-bleed edge-to-edge）— UI 元件如果有背景場景，不要意外白邊 / letterbox / painting frame。在 [COMPOSITION] 段用**正向指令**鎖；純粹在 [EXCLUSION] 加 negation 反而可能誘發 frame design。
4. 使用者明確要求不同就依使用者指示。

---

## 專案既存資產優先（生圖前必做）

**生圖前先掃專案目錄**找有沒有已有 UI 資產：`assets/ui/`、`ui/`、`assets/icons/`、`assets/frames/`，含立繪 / sprite 也可參考其風格代號。

**若找到既有 UI 元件：**
1. 把既有 UI 的「風格代號、邊框粗細 / 轉角圓度、光效強度、配色主軸、稀有度視覺系統」**鎖死當預設**，不要從風格庫重新挑
2. 把代表性 1-2 張當 `--ref` 傳 Banana Pro，**多塞既有 UI ref 強制風格鎖**
3. Strict Rules 段明寫「the new UI element must visually rhyme with existing project UI — same border weight, same corner radius, same lighting style, same color temperature」
4. 跟使用者確認：「專案既有 N 個同類 UI（風格 / 邊框 / 光效為...），這次照樣？要改請明說」

**為什麼**：專案已有的東西，畫風、畫面預設要參照。UI 元件常組成系列同畫面出現，新做的 1 個風格飄掉直接破壞整個 HUD 視覺。

---

## 批次一致性模式（同類別資產 ≥ 2 張）

**當使用者一次要產 ≥ 2 個同類別 UI 元件時**（例：6 個技能 icon、4 種稀有度卡框、活動 banner 系列、多語系 popup），切換到批次模式：

1. **先訂統一規格** — 任何生圖前，先決定：風格代號、元件比例（icon 1:1 / banner 16:9 等）、配色主軸、邊框風格、光效強度、字體 / 文字配置（如有）、是否去背（magenta 底）、稀有度視覺系統（如有層級）。
2. **區分「鎖死」vs「可變」** — 鎖死 = 風格 / 比例 / 邊框 / 光效系統 / 配色主軸；可變 = 圖標符號 / 主題色 / 文字內容。
3. **把鎖死規格寫進每張 prompt 的 Strict Rules 段** — 同批次所有 prompt 的 Strict Rules 用同一段文字，AI 變化只能在「可變」項。UI 特別注意：邊框粗細、轉角圓度、光效強度若不寫 Strict 容易飄。
4. **生完必確認** — 二選一：(a) 每張生完個別確認再套用 (b) 全部生完後一次看統一性 + 符合度（建議組成 grid 或實際擺到模擬 UI 上看）。**確認步驟不能省**。
5. **稀有度差距系列例外**：R/SR/SSR 卡框、技能 icon 稀有度差 — 視覺差距是設計目的，但**比例 + 風格代號 + 邊框基本結構仍要統一**，差距走光效強度、邊框複雜度、配件密度，不走比例。

**單張 UI 元件跳過此模式**，直接走原 Phase 流程。

**為什麼**：UI 元件常組成系列出現在同一畫面（角色卡 + 稀有度框、技能列、活動 banner 牆）。沒鎖規格進 prompt，AI 會飄（光效強度不一、邊框風格亂、配色基準偏移）。

---

## 風格庫（預設從這幾種挑）

| 風格代號 | 參考遊戲 | UI 視覺特徵 |
|---------|---------|-----------|
| `mihoyo_genshin` | 原神 | 金黃色金屬框 + 淺色半透明底 + 細刻紋飾邊 + 柔和漸層，奇幻感 |
| `mihoyo_starrail` | 崩壞：星穹鐵道 | 深色玻璃形態 + 霓虹點綴 + 幾何切割 + 賽博紋理，未來感 |
| `arknights` | 明日方舟 | 扁平幾何 + 工業風 + 黑橘配色 + 強對比 + 警示條紋，硬派 |
| `nikke` | 勝利女神：NIKKE | 深色軍用 + 霓虹點綴 + 機械斜切 + 戰術風 |
| `azurlane` | 碧藍航線 | 深藍 + 金邊 + 軍艦元素 + 柔光 |
| `mihoyo_zzz` | 絕區零 | 街頭塗鴉 + 賽博龐克 + 霓虹 + 不規則切割 |
| `custom` | — | 使用者描述或上傳參考圖 |

如果沒指定，**先問風格**。

---

## UI 元件類型庫

| 元件代號 | 用途 | 預設規格 |
|---------|------|---------|
| `button` | 按鈕（confirm / cancel / 主行動）| 以 21:9 生成 → 後製裁到 4:1 / 3:1，magenta 底去背 |
| `icon_skill` | 技能 / 法術 icon | 1:1，magenta 底去背，預留發光區 |
| `icon_item` | 道具 / 物品 icon | 1:1，magenta 底去背 |
| `icon_currency` | 貨幣 / 資源 icon | 1:1，金屬光澤強 |
| `frame_card` | 卡牌 / 角色卡框 | 3:4，中央透空 |
| `frame_avatar` | 頭像框（圓 / 方）| 1:1，中央透空 |
| `banner` | 標題橫幅 / 活動 banner | 16:9 或 21:9 |
| `popup_bg` | 彈窗背景 | 4:3 或 3:4 |
| `slot_item` | 道具格 / 裝備格 | 1:1，可含發光 |
| `rarity_glow` | 稀有度光效 / 邊框 | 1:1 或 3:4，多色版本 |
| `progress_bar` | 進度條 / 血條 | 以 21:9 生成 → 後製裁到 8:1 細長 |
| `divider` | 分隔線 / 裝飾元件 | 以 21:9 生成 → 後製裁到 16:1 細長 |
| `tab` | 分頁標籤 | 以 21:9 生成 → 後製裁到 3:1 或 4:1 |
| `badge` | 徽章 / 成就 / 等級標 | 1:1 |
| `mission_card` | 任務 / 活動卡 | 4:3 |

---

## Phase 1｜需求收集

用 AskUserQuestion 依序確認：

### 第一輪：核心需求

| 項目 | 範例 |
|------|------|
| **元件類型** | 從上方元件代號表挑（必選），可同主題一次做多個 |
| **元件用途** | 「主畫面 confirm 按鈕」「戰鬥 UI 技能 icon」「商城稀有道具 frame」 |
| **風格代號** | 從風格庫挑 |
| **主色調** | 「金 + 米白」「深藍 + 霓虹紫」「黑 + 橘」 |

### 第二輪：技術規格

| 項目 | 選項 | 預設 |
|------|------|------|
| **長寬比** | 1:1 / 3:4 / 4:3 / 16:9 / 21:9（寬元件以 21:9 生成後裁切）| 依元件類型自動建議 |
| **解析度** | 1K / 2K | **1K**（UI 通常不需 2K）|
| **背景處理** | magenta 底去背 / 純色 / 漸層 | **magenta 底去背** |
| **變體數量** | 1 / normal+pressed / 多稀有度版本（白藍紫金紅）| 1 |
| **參考圖** | 是否上傳（既有 UI / 風格 / motif）| 無 |

**如果做多稀有度版本**：產一張通用構造，再用「relight + recolor」走色階變體（白 / 綠 / 藍 / 紫 / 金 / 紅）。

---

## Phase 2｜參考圖處理

### 既有 UI 參考圖
1. Read 看圖
2. 確認：哪些 motif 要保留（角型 / 紋飾 / 質感），哪些可改
3. 寫進 prompt 描述

### 風格參考圖
1. Read 看圖
2. 描述視覺語言（金屬亮度、紋飾密度、色相），確認理解
3. 轉成 prompt 描述詞

**參考圖限制：** 最多 6 張，超過品質下降。

---

## Phase 3｜建議與討論

```
## 建議

### 風格與元件
[風格代號] + [元件代號]，原因：[符合 XX 主題 / XX 配色]

### 技術規格
- 長寬比：[ratio]，因為 [元件用途]
- 解析度：[size]，UI 用途通常 1K 夠
- 背景：[magenta 底去背/漸層]

### 視覺重點
- [must-have 設計元素]
- [must-avoid（例：不要做圓形如果是方框 icon）]

### 商業參考
跟 [遊戲名] 的 [UI 元件] 視覺語言相近——[具體特徵]。

### 注意事項
- [可能影響可讀性 / 適配性的提醒]

要進入 prompt 階段嗎？
```

確認後進 Phase 4。

---

## Phase 4｜Prompt 撰寫與確認

### Step 1：中文 Prompt

依「**風格 → 元件類型 → 形狀 → 材質 → 配色 → 紋飾 / 細節 → 背景 → 排除項**」順序組。

```
## Prompt 確認

📝 中文 Prompt：
> [完整中文 prompt]

📐 長寬比：[ratio]
📏 解析度：[size]
🎨 風格：[風格代號]
📦 元件：[元件代號]
🖼️ 參考圖：[有/無]

要修改什麼嗎？
```

### Step 2：轉英文 + 套風格 boilerplate

#### `mihoyo_genshin` UI boilerplate
```
mobile RPG game UI asset, Genshin Impact-style, ornate gold metal frame, soft cream
parchment fill, decorative engraved filigree border, gentle warm gradient, fantasy aesthetic,
clean readable shape, solid #FF00FF magenta background, edge-to-edge, production-quality 2D game UI
```

#### `mihoyo_starrail` UI boilerplate
```
mobile RPG game UI asset, Honkai Star Rail-style, dark glassmorphism panel, neon accent line,
sharp geometric cut, sci-fi cyber pattern, holographic gradient, clean tech aesthetic,
solid #FF00FF magenta background, edge-to-edge, production-quality 2D game UI
```

#### `mihoyo_zzz` UI boilerplate
```
mobile RPG game UI asset, Zenless Zone Zero-style, urban graffiti accent, cyberpunk neon glow,
asymmetric edgy cut, high-saturation color block, street fashion aesthetic, dynamic energy,
solid #FF00FF magenta background, edge-to-edge, production-quality 2D game UI
```

#### `arknights` UI boilerplate
```
mobile strategy game UI asset, Arknights-style, flat geometric shape, industrial military
aesthetic, black and orange palette with hazard stripe accent, high contrast, sharp clean
edge, restrained ornamentation, solid #FF00FF magenta background, edge-to-edge, production-quality 2D game UI
```

#### `nikke` UI boilerplate
```
mobile RPG game UI asset, NIKKE-style, dark military panel, neon accent glow, mechanical
diagonal cut, tactical HUD aesthetic, sleek metallic surface, solid #FF00FF magenta background, edge-to-edge,
production-quality 2D game UI
```

#### `azurlane` UI boilerplate
```
mobile RPG game UI asset, Azur Lane-style, deep navy with gold trim, naval / military motif,
soft painted gradient, ornate but readable, solid #FF00FF magenta background, edge-to-edge, production-quality 2D game UI
```

### Step 3：執行生成或交付 Prompt

- **Prompt 模式**：交付英文 prompt + 建議參數 + 提醒參考圖
- **API 模式**：呼叫 `~/.claude/skills/imagen/bin/generate.py`

---

## Phase 5｜圖片生成（API 模式）

### 檔案命名與存放

**位置決定**：
1. 使用者明確指定 → 用指定的
2. 沒指定 → 先問「要存在哪？」
3. fallback → 當前工作目錄下 `imagen-ui/`

檔名：`{元件代號}_{風格代號}_{日期}_{序號}.png`
範例：`icon_skill_mihoyo_genshin_20260430_01.png`

### 執行生成

先把最終英文 prompt Write 到 `prompt-final.txt`，再執行：

```bash
python ~/.claude/skills/imagen/bin/generate.py \
  --prompt "$(cat prompt-final.txt)" \
  --ratio 1:1 --size 1K \
  --ref reference/style.jpg \
  --output {output_path}
```

寬元件（button / tab / progress_bar / divider）用 `--ratio 21:9` 生成，去背後再裁到目標比例。

### 去背（magenta chroma-key）

imagen-ui 本身沒有去背功能，借用 generate2dsprite 的後製：

```bash
python ~/.claude/skills/generate2dsprite/scripts/generate2dsprite.py process --target asset --mode single --rows 1 --cols 1 --input <png> --output-dir <dir>
```

### 多稀有度變體（常見需求）

如果要白藍紫金紅五階稀有度，**用同一個 base prompt + 改色相詞 + 改光效強度**生 5 張：

```
common (white): muted gray-white palette, soft minimal glow
rare (blue): cool blue palette, gentle blue rim glow
epic (purple): deep purple palette, intense purple aura
legendary (gold): rich gold palette, radiant golden burst
mythic (red): crimson palette, fiery red aura with flame motif
```

每張獨立呼叫 API，保持構造一致只變色。

### 生成後

1. Read 看圖
2. 工程視角：尺寸是否為 2 的倍數、是否含安全邊距、檔名是否照 `{元件代號}_{風格代號}_{日期}_{序號}.png`
3. **回報：給完整絕對資料夾路徑**
4. 詢問：「滿意嗎？要做變體（不同色 / 不同稀有度 / pressed 狀態）嗎？」

---

## Phase 6｜記憶更新

更新 `<project-dir>/docs/imagen_history.md`（三支 imagen skill 共用同一檔、同一欄位）：

```markdown
| 日期 | skill | 用途 | 最終英文 prompt 摘要 | 輸出檔 | 備註 |
|------|-------|------|---------------------|--------|------|
| 2026-04-30 | imagen-ui | 火球術技能 icon | fireball skill icon, mihoyo_genshin, 1:1, 1K | imagen-ui/icon_skill_mihoyo_genshin_20260430_01.png | 五階稀有度變體 |
```

---

## UI 專用 prompt 撰寫原則

1. **形狀必須具體**：rounded square / hexagonal / circular / shield-shaped — 不要含糊
2. **材質明確**：metallic gold / frosted glass / brushed steel / parchment / hologram
3. **預留 content space**：如果元件背後要放文字 / 數字，加 `clear central area for text/number`
4. **強調 magenta 底**：除非有特殊需求，背景一律 `solid #FF00FF magenta background, edge-to-edge`，後製 chroma-key 去背
5. **避免實際內容**：icon 描繪「火球能量球」不要寫具體文字 / logo / 角色名
6. **強調 readable / clean**：UI 必須清楚，加 `clean readable silhouette`、`high contrast against any background`
7. **避免 photo / 3D render 詞彙**：手遊 UI 通常是 2D 風格化，避免觸發寫實 photo 風

---

## 長寬比速查

| 比例 | 適用元件 |
|------|---------|
| 1:1 | icon / avatar / badge / slot / rarity_glow |
| 21:9（生成）→ 後製裁 4:1 / 3:1 | button / tab |
| 21:9（生成）→ 後製裁 8:1 / 16:1 | progress_bar / divider |
| 3:4 | frame_card / popup_bg（直）/ rarity_glow（卡型）|
| 4:3 | popup_bg（橫）/ mission_card |
| 16:9 | banner（一般）|
| 21:9 | banner（超寬橫幅）|

---

## 錯誤處理

| 錯誤 | 處理 |
|------|------|
| 出來太擁擠 | 強調 `clean readable shape` + `clear negative space` |
| 元件變插畫不像 UI | 加 `flat 2D game UI element, not an illustration` |
| 去背不乾淨（magenta 殘邊）| 確認 prompt 有 `solid #FF00FF magenta background, edge-to-edge`，重跑 generate2dsprite `process` 去背 |
| 風格融合失敗（看起來像通用 web UI）| 強化 boilerplate，列具體遊戲名 + UI motif 特徵 |
| 多稀有度色階沒區隔開 | 提高色相對比 + 改光效強度差距 |

## 銜接

- 想還原某張參考 UI 的風格 → 先用 `image-to-prompt` 逆向出中性 prompt 再回來生
- 角色立繪 → `imagen-portrait`
- 通用生圖需求 → `imagen`
