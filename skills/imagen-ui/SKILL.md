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

使用 Gemini 的 Nano Banana Pro (`gemini-3-pro-image-preview`) 生成 RPG 手遊 UI 元件，預設套用高營收手遊（米哈遊、明日方舟等）的 UI 視覺語言。三支 imagen skill 的共用流程、格式、指令集中在 `../imagen/references/common.md`（下文以「common.md §N」引用）。

---

## 核心原則

1. **Prompt 忠於討論結果** — 不擅自加裝飾元素。
2. **預設手遊高品質 UI 審美** — 金屬質感 / 漸層 / 半透明 / 細節描邊，但**不喧賓奪主**（UI 元件背後通常會放文字或其他內容）。
3. **每次都問元件類型** — UI 是功能性設計，必須先確定要做哪一類元件。
4. **去背優先** — 大多數 UI 元件都要去背才能融入遊戲畫面；Gemini 輸出沒有 alpha，所以生成時鎖純品紅 `#FF00FF` 滿版背景，Phase 5 再用 magenta chroma-key 後製去背。
5. **記錄偏好** — 寫入 `<project-dir>/docs/imagen_history.md`（common.md §8）。

---

## 一致性規則（生圖前必讀）

- **預設視覺規則**：女性白皮膚、角色美型（[EXCLUSION] 排除 western cartoon 漂移）、元件若含背景場景須滿版四邊用正向指令鎖；使用者明說即覆蓋。詳見 common.md §1。
- **專案既存資產優先（pre-flight 必做）**：先掃 `assets/ui/`、`ui/`、`assets/icons/`、`assets/frames/`；有既有 UI 就鎖風格代號 / 邊框粗細 / 轉角圓度 / 光效強度 / 配色主軸 / 稀有度視覺系統當預設，**不從風格庫重新挑**，代表作當 `--ref`，Strict Rules 明寫 visually rhyme，跟使用者確認 lock。詳見 common.md §2。
  - UI 元件常組成系列同畫面出現（角色卡 + 稀有度框、技能列、banner 牆），新做的 1 個風格飄掉直接破壞整個 HUD。
- **批次一致性模式（≥ 2 個同類元件，例：6 個技能 icon、4 種稀有度卡框、banner 系列、多語系 popup）**：先訂統一規格（UI 多訂：元件比例、邊框風格、光效強度、字體 / 文字配置、是否去背 magenta 底、稀有度視覺系統）→ 鎖死 = 風格 / 比例 / 邊框 / 光效系統 / 配色主軸，可變 = 圖標符號 / 主題色 / 文字內容 → 同一段 Strict Rules 寫進每張 prompt → 生完必確認（建議組成 grid 或實際擺到模擬 UI 上看）；單張跳過。詳見 common.md §3。
  - 邊框粗細、轉角圓度、光效強度不寫進 Strict 必飄。
  - R / SR / SSR 卡框 / icon 稀有度差：**比例 + 風格代號 + 邊框基本結構仍統一**，差距走光效強度 / 邊框複雜度 / 配件密度，不走比例。
- **第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`**（Style Bible + contact sheet QC）。

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

**如果做多稀有度版本**：產一張通用構造，再用「relight + recolor」走色階變體（白 / 綠 / 藍 / 紫 / 金 / 紅），見 Phase 5。

**如果使用者之前用過**：先讀 `<project-dir>/docs/imagen_history.md` 提示沿用（common.md §8）。

---

## Phase 2｜參考圖處理

依 common.md §5（先 Read 看圖 → 向使用者確認 → 只寫確認過的；上限 6 張）。UI 常見兩類參考：

- **既有 UI 參考**：確認哪些 motif 要保留（角型 / 紋飾 / 質感）、哪些可改
- **風格參考**：描述視覺語言（金屬亮度、紋飾密度、色相），確認理解後轉 prompt 描述詞

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

依「**風格 → 元件類型 → 形狀 → 材質 → 配色 → 紋飾 / 細節 → 背景 → 排除項**」順序組。撰寫原則與確認框格式見 common.md §4；ui **含** 🎨 風格、🧩 套用風格 boilerplate：<style_key>、📦 元件三行。

### Step 2：轉英文 + 套風格 boilerplate

翻譯原則見 common.md §4。依風格代號在英文 prompt 加上對應 UI boilerplate：

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

### Step 3：判定模式

先依 draw-engines.md §2 判引擎（整個任務只判一次）：**GPT 線可用** → Phase 5 改用 image-studio client（draw-engines.md §3；`--size` / `--ratio` 需求改寫進 prompt 文字；去背直接加 `--remove-background`，免走 magenta chroma-key），整批失敗照 §4 先回報原因、由使用者決定是否換線。**GPT 線不可用** → 依 common.md §9 判定：**API 模式** → Phase 5；**Prompt 模式** → 以 §9「生成資訊」格式交付英文 prompt + 建議參數 + 參考圖上傳提醒。

---

## Phase 5｜圖片生成（API 模式）

1. **存放位置與檔名**：依 common.md §7（fallback `<cwd>/imagen-ui/`；檔名 `{元件代號}_{風格代號}_{日期}_{序號}.png`，例 `icon_skill_mihoyo_genshin_20260430_01.png`）。
2. **執行**：英文 prompt Write 到 `prompt-final.txt`，呼叫 `~/.claude/skills/imagen/bin/generate.py`（標準指令 common.md §9）；UI 預設 `--size 1K`。寬元件（button / tab / progress_bar / divider）用 `--ratio 21:9` 生成，去背後再裁到目標比例。

### 去背（magenta chroma-key）

imagen-ui 本身沒有去背功能，借用 generate2dsprite 的後製：

```bash
python ~/.claude/skills/generate2dsprite/scripts/generate2dsprite.py process --target asset --mode single --rows 1 --cols 1 --input <png> --output-dir <dir>
```

### 多稀有度變體（常見需求）

如果要白藍紫金紅五階稀有度，**用同一個 base prompt + 改色相詞 + 改光效強度**生 5 張，每張獨立呼叫 API，保持構造一致只變色：

```
common (white): muted gray-white palette, soft minimal glow
rare (blue): cool blue palette, gentle blue rim glow
epic (purple): deep purple palette, intense purple aura
legendary (gold): rich gold palette, radiant golden burst
mythic (red): crimson palette, fiery red aura with flame motif
```

### 生成後

依 common.md §6（Read 看圖 → 回報絕對資料夾路徑 → 問滿意 / 調整只改指出的部分），UI 另加：

- **工程視角**：尺寸是否為 2 的倍數、是否含安全邊距、檔名是否照 `{元件代號}_{風格代號}_{日期}_{序號}.png`
- 詢問是否做變體（不同色 / 不同稀有度 / pressed 狀態）

---

## Phase 6｜記憶更新

追加一列到 `<project-dir>/docs/imagen_history.md`（6 欄位與 ui 範例見 common.md §8）。

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

通用錯誤（API Key / 安全過濾 / 參考圖格式 / 網路）見 common.md §9；UI 特有：

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
- 第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`
