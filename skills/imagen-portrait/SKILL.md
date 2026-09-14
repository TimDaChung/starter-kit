---
name: imagen-portrait
version: 1.0.0
description: |
  Nano Banana Pro 生成 RPG 手遊角色立繪。預設米哈遊（原神 / 崩鐵 / 絕區零）/ 明日方舟 / NIKKE / 碧藍航線等高營收手遊風格 — 內建 6 風格庫 + 英文 boilerplate。
  觸發：「立繪」「角色立繪」「角色卡」「半身像」「米哈遊風」「方舟風」「gacha 立繪」。
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

# /imagen-portrait — RPG 手遊角色立繪生成

> **執行角色：美術**——關注風格一致、角色辨識度、立繪規格（構圖 / 尺寸 / 命名）。

使用 Gemini 的 Nano Banana Pro (`gemini-3-pro-image-preview`) 生成 RPG 手遊角色立繪，預設套用高營收手遊（米哈遊、明日方舟等）的視覺語言。

姊妹 skill：
- `/imagen` — 通用生圖（會問你風格）
- `/imagen-ui` — UI 素材（手遊 UI 元件）
- `/imagen-portrait`（這支）— 角色立繪

---

## 核心原則

1. **Prompt 忠於討論結果** — 嚴禁擅自添加使用者沒提到的元素或設計細節。
2. **預設手遊高品質審美** — 厚塗、立體光影、設計密度高、有 silhouette 辨識度。除非使用者要 chibi / 像素 / 寫實扁平等其他風格才切換。
3. **每次都問角色設定** — 立繪是設計工作，必須先確認角色身份、職業、世界觀基調。
4. **記錄偏好** — 每次生圖後寫入 memory `imagen_history.md`。

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

**生圖前先掃專案目錄**找有沒有已有立繪 / 角色資產：`立繪/`、`assets/portraits/`、`portraits/`、`assets/sprites/`（chibi sprite 也可作 portrait 風格參考）。

**若找到既有立繪：**
1. 把既有立繪的「畫風代號、頭身比、視角、光源、構圖留白、面向方向」**鎖死當預設**，不要從風格庫重新挑
2. 把代表性 1-2 張當 `--ref` 傳 Banana Pro，除了角色設計 ref 之外**多塞既有立繪 ref 強制風格鎖**
3. Strict Rules 段明寫「the new portrait must visually rhyme with existing project portraits — same head-body proportions, same view angle, same lighting」
4. 跟使用者確認：「專案既有 N 張立繪（畫風 / 頭身比為...），這次照樣？要改風格請明說」

**為什麼**：使用者明確要求「專案已有的東西，畫風跟畫面、人物比例等是要默認參照的」(2026-05-07)。立繪特別容易在頭身比飄（成熟系角色被 Banana 自動拉長身），ref + Strict Rules 雙鎖才穩。

---

## 批次一致性模式（同類別資產 ≥ 2 張）

**當使用者一次要產 ≥ 2 張同類別資產時**（例：4 個角色立繪、一組職業立繪、SR/SSR 角色組），切換到批次模式：

1. **先訂統一規格** — 任何生圖前，先決定：風格代號、長寬比、頭身比、視角、光源方向、**面向方向（朝左 / 朝右）**、構圖留白、姿態鎖定條件、背景處理強度。
2. **區分「鎖死」vs「可變」** — 鎖死 = 風格 / 比例 / 視角 / 面向 / 光源；可變 = 配色 / 武器 / 場景 / 表情。
3. **把鎖死規格寫進每張 prompt 的 Strict Rules 段** — 同批次所有 prompt 的 Strict Rules 用同一段文字，AI 變化只能在「可變」項。立繪特別注意：頭身比、面向方向、視角不寫 Strict 容易飄。
4. **生完必確認** — 二選一：(a) 每張生完個別確認再套用 (b) 全部生完後一次看統一性 + 符合度。**確認步驟不能省**，避免實裝後才發現要重生。
5. **例外**：明確稀有度差距的角色組（R/SR/SSR）— 視覺差距是設計目的，但**頭身比仍要統一**，差距走配件密度 / 光效 / 服裝細節，不走頭身比。

**單張立繪跳過此模式**，直接走原 Phase 流程。

**為什麼**：同遊戲的角色立繪要視覺押韻。沒鎖規格進 prompt，AI 會飄（頭身比變、視角混、面向鏡像翻、風格漂浮）。詳見 memory `feedback_same_category_unified_style.md`。

---

## 風格庫（默認從這幾種挑）

| 風格代號 | 參考遊戲 | 視覺特徵 |
|---------|---------|---------|
| `mihoyo_genshin` | 原神 | 厚塗動漫，賽璐璐 + 寫實光影混合，金屬高光強，色彩飽和層次豐富，魔幻奇幻 |
| `mihoyo_starrail` | 崩壞：星穹鐵道 | 時尚動漫偏寫實，光影細膩，妝感強，科幻 + 奇幻混搭 |
| `mihoyo_zzz` | 絕區零 | 潮流動漫，賽博朋克，高彩度，街頭時尚 |
| `arknights` | 明日方舟 | 偏寫實二次元，職人感強，硬朗光影，暗色調 / 金屬質感，工業風 |
| `nikke` | 勝利女神：NIKKE | 高細節寫實 + 二次元，軍用 / 機械風，霓虹點綴 |
| `azurlane` | 碧藍航線 | 繪師導向，細節密度極高，帶艦娘元素 |
| `custom` | — | 使用者描述或上傳參考圖 |

如果使用者沒指定，**先問他要哪種風格**（用 AskUserQuestion 列出選項）。

---

## Phase 1｜需求收集

用 AskUserQuestion 依序確認（可合併問）：

### 第一輪：角色設定

| 項目 | 範例 |
|------|------|
| **角色身份** | 「冰系法師女孩」「機械師大叔」「狐耳暗殺者」 |
| **職業 / 種族 / 陣營** | 「劍士 / 精靈 / 王國軍」 |
| **世界觀基調** | 「奇幻」「賽博朋克」「廢土」「武俠」 |
| **性別 / 年齡感** | 「少女」「青年」「成熟女性」 |

### 第二輪：視覺風格

| 項目 | 範例 |
|------|------|
| **風格代號** | 從上方風格庫挑，或 `custom` |
| **配色主軸** | 「冷藍 + 銀」「黑紅 + 金」「白金 + 粉」 |
| **服裝設計密度** | 「簡潔」「中等」「複雜（多層次 + 配件）」 |
| **武器 / 標誌物** | 「長劍」「魔法書」「雙槍」「無」 |

### 第三輪：構圖與規格

| 項目 | 選項 | 預設 |
|------|------|------|
| **構圖** | 全身 / 半身（腰以上）/ 大頭照 | 半身 |
| **姿態** | 站姿 idle / 戰鬥姿 / 互動姿 / 角色卡定格 | 站姿 idle |
| **背景** | 透明背景 / 漸層 / 場景背景（教堂 / 戰場 / 街道）| 透明 / 漸層（看用途） |
| **長寬比** | 3:4（半身 / 角色卡）/ 9:16（全身直立）/ 2:3 | 依構圖建議 |
| **解析度** | 1K / 2K / 4K | 2K |
| **參考圖** | 是否上傳（角色 / 服裝 / 風格）| 無 |

**如果使用者之前用過：**
讀 memory `imagen_history.md`，提示：「上次做 [角色] 用了 [風格 + 構圖]，這次要沿用嗎？」

---

## Phase 2｜參考圖處理

### 角色參考圖
1. 用 Read 工具看圖
2. 向使用者確認：哪些保留（臉型 / 髮色 / 標誌服裝），哪些改
3. 寫進 prompt（只寫確認過的）

### 風格參考圖
1. Read 看圖
2. 描述你看到的風格特徵（厚塗程度、光影、線條、色彩取向），確認理解正確
3. 轉成 prompt 描述詞

### 服裝 / 配件參考圖
1. Read 看圖
2. 確認哪些配件 / 元素要保留
3. 寫進 prompt 的服裝描述

**參考圖限制：** 角色 5 張 / 物件 6 張 / 總計 14 張。

---

## Phase 3｜建議與討論

收集完需求後**先給專業建議**：

```
## 建議

### 風格選定
[風格代號]，原因：[符合 XX 世界觀 / XX 配色 / XX 商業定位]

### 構圖建議
[構圖]，[長寬比]，因為 [用途符合 / 角色設計能完整呈現]

### 重點視覺元素
- [哪些設計細節是 must-keep] 
- [哪些可以 AI 自由發揮]

### 商業參考
跟 [遊戲名] 的 [角色名] 視覺語言相近——金屬質感 / 配件密度 / 光影方向。

### 注意事項
- [Banana Pro 對某些主題的限制，例如過度暴露 / 武器尺寸]
- [風格融合的潛在風險]

可以進入 prompt 階段嗎？
```

確認後進 Phase 4。

---

## Phase 4｜Prompt 撰寫與確認

### Step 1：中文 Prompt

依「**風格 → 角色身份 → 服裝細節 → 姿態 / 表情 → 構圖 / 鏡頭 → 背景 → 光影 → 排除項**」順序組。

**展示格式：**

```
## Prompt 確認

📝 中文 Prompt：
> [完整中文 prompt]

📐 長寬比：[ratio]
📏 解析度：[size]
🎨 風格：[風格代號]
🖼️ 參考圖：[有/無，幾張]

沒問題的話我就轉英文並開始生成。要修改什麼嗎？
```

### Step 2：轉英文 + 套風格 boilerplate

依風格代號加上對應 boilerplate（自動加，不在中文 prompt 顯示）：

#### `mihoyo_genshin` boilerplate
```
gacha mobile RPG character illustration, Genshin Impact-style, anime semi-realistic painterly,
cel-shading with detailed soft shadow, metallic highlight on weapons and accessories,
saturated rich colors, cinematic rim light, intricate costume design, sharp clean linework,
high-density detail, 2D production-quality character art
```

#### `mihoyo_starrail` boilerplate
```
gacha mobile RPG character illustration, Honkai: Star Rail-style, semi-realistic anime,
fashion-forward design, refined makeup rendering, smooth gradient shading, sci-fi accents,
cinematic rim and key light, polished costume detail, slick clean linework, high production value
```

#### `mihoyo_zzz` boilerplate
```
gacha mobile character illustration, Zenless Zone Zero-style, urban streetwear anime,
cyberpunk neon accents, high-saturation color blocking, edgy modern fashion,
cel-shading with sharp shadow lines, comic-style energy, dynamic pose, high production value
```

#### `arknights` boilerplate
```
gacha mobile RPG character illustration, Arknights-style, semi-realistic anime,
muted dark palette with metallic accents, industrial military design language, sharp hard light,
gritty professional rendering, restrained color saturation, refined craftsmanship,
2D production-quality character art
```

#### `nikke` boilerplate
```
gacha mobile RPG character illustration, NIKKE-style, high-detail semi-realistic anime,
military / mecha design language, neon accent highlights, dramatic chiaroscuro lighting,
hyper-detailed costume and accessories, sleek refined rendering, cinematic key light
```

#### `azurlane` boilerplate
```
gacha mobile RPG character illustration, Azur Lane-style, illustrator-driven anime art,
extremely high detail density, decorative naval / military elements, soft painterly shading,
ornate costume design, vibrant accent colors, refined linework, 2D production-quality
```

### Step 3：執行生成或交付 Prompt

模式同 `/imagen`：
- **Prompt 模式**：交付英文 prompt + 建議參數 + 提醒參考圖上傳到 Google AI Studio
- **API 模式**：直接呼叫 `~/.claude/skills/imagen/bin/generate.py`（共用 wrapper），參考圖用 `--ref` 傳

---

## Phase 5｜圖片生成（API 模式）

### 檔案命名與存放

**位置決定**：
1. 使用者明確指定 → 用指定的
2. 沒指定 → 先問「要存在哪？」
3. fallback → 當前工作目錄下 `imagen-portrait/`

檔名：`{角色名或主題}_{風格代號}_{日期}_{序號}.png`
範例：`ice_mage_mihoyo_genshin_20260430_01.png`

### 執行生成

```bash
python ~/.claude/skills/imagen/bin/generate.py \
  --prompt "$(cat prompt-final.txt)" \
  --ratio 3:4 --size 2K \
  --ref reference/character.jpg \
  --output {output_path}
```

`--ref` 可重複多次（角色 + 風格 + 服裝參考都可以一起傳）。

### 生成後

1. Read 看圖確認產出
2. **回報：給完整絕對資料夾路徑**（不用列每個檔案）
3. 詢問：「滿意嗎？要調整 prompt 重新生成？要做不同表情 / 姿態變體？」

調整循環：只改使用者明確指出的部分。

---

## Phase 6｜記憶更新

更新 memory `imagen_history.md`：

```markdown
| 日期 | 角色 / 主題 | 風格 | 構圖 | 長寬比 | 解析度 | 路徑 | 備註 |
|------|-----------|------|------|--------|--------|------|------|
| 2026-04-30 | 冰系法師 | mihoyo_genshin | 半身 | 3:4 | 2K | gemini/portraits/ | 有上傳服裝參考 |
```

---

## 立繪專用 prompt 撰寫原則

1. **角色身份必須具體**：寫清楚職業 / 性格 / 世界觀，不要只寫「漂亮女孩」
2. **服裝設計分層描述**：上裝 / 下裝 / 配件 / 鞋 / 頭飾，每層獨立描述
3. **姿態描述要動態詞**：站立 + 動作（手扠腰 / 持劍 / 半轉身），不要只寫 standing
4. **光源方向明確**：rim light from upper left / cinematic backlight / soft front fill
5. **排除項放最後**：no extra fingers / no malformed face / no nudity / no copyrighted character
6. **避免名字硬塞**：不要寫「神里綾華」「W」這種具體角色名（會觸發版權過濾），用視覺特徵描述

---

## 長寬比速查

| 比例 | 用途 |
|------|------|
| 1:1 | 角色頭像 / icon |
| 2:3 | 卡牌人物（橫向偏直）|
| 3:4 | **半身 / 角色卡（最常用）** |
| 4:5 | Instagram-friendly 半身 |
| 9:16 | **直立全身（手機背景 / wallpaper）** |
| 16:9 | 橫構圖場景立繪（少用）|

---

## 錯誤處理

| 錯誤 | 處理 |
|------|------|
| 安全過濾觸發（暴露 / 暴力）| 調整 prompt 措辭，避開觸發詞，必要時加 `safe-for-work` 修飾 |
| 風格融合失敗（看起來像 SDXL 通用 anime）| 加強 boilerplate，強調具體遊戲名 + 視覺特徵 |
| 角色臉部變形 | 加 `well-drawn anatomically correct face` + 排除 `malformed face` |
| 武器 / 配件設計混亂 | 拆條目單獨描述，每個配件給獨立形容詞 |
| 跟參考圖差異大 | 確認 `--ref` 有正確傳，描述 must-keep 特徵 |

## 銜接

- 想還原某張參考立繪的風格 → 先用 `image-to-prompt` 逆向出中性 prompt，換上角色名再回來生
- UI 素材／頭像框等 → `imagen-ui`
- 通用生圖需求 → `imagen`
