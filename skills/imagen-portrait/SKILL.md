---
name: imagen-portrait
version: 1.0.0
description: |
  生成 RPG 手遊角色立繪。預設米哈遊（原神 / 崩鐵 / 絕區零）/ 明日方舟 / NIKKE / 碧藍航線等高營收手遊風格 — 內建 6 風格庫 + 英文 boilerplate。
  觸發：「立繪」「角色立繪」「角色卡」「半身像」「米哈遊風」「方舟風」「gacha 立繪」。
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Agent
  - AskUserQuestion
---

# /imagen-portrait — RPG 手遊角色立繪生成

> **執行角色：美術**——關注風格一致、角色辨識度、立繪規格（構圖 / 尺寸 / 命名）。

生成 RPG 手遊角色立繪，預設套用高營收手遊（米哈遊、明日方舟等）的視覺語言。四支 imagen skill 的共用流程、格式、指令集中在 `../imagen/references/common.md`（下文以「common.md §N」引用）；生圖引擎（唯一引擎＝image-studio GPT 線、呼叫契約、失敗處理）見 `../imagen/references/draw-engines.md`。

---

## 核心原則

1. **Prompt 忠於討論結果** — 嚴禁擅自添加使用者沒提到的元素或設計細節。
2. **預設手遊高品質審美** — 厚塗、立體光影、設計密度高、有 silhouette 辨識度。除非使用者要 chibi / 像素 / 寫實扁平等其他風格才切換。
3. **每次都問角色設定** — 立繪是設計工作，必須先確認角色身份、職業、世界觀基調。
4. **記錄偏好** — 每次生圖後寫入 `<project-dir>/docs/imagen_history.md`（common.md §8）。

---

## 一致性規則（生圖前必讀）

- **預設視覺規則**：女性白皮膚、所有角色美型（[EXCLUSION] 排除 western cartoon 漂移）、背景滿版四邊用正向指令鎖；使用者明說即覆蓋。詳見 common.md §1。
- **專案既存資產優先（pre-flight 必做）**：先掃 `立繪/`、`assets/portraits/`、`portraits/`、`assets/sprites/`；有既有立繪就鎖畫風代號 / 頭身比 / 視角 / 光源 / 構圖留白 / 面向當預設，**不從風格庫重新挑**，代表作當 `--reference`，Strict Rules 明寫 visually rhyme，跟使用者確認 lock。詳見 common.md §2。
  - 立繪特別容易在**頭身比**飄（成熟系角色常被自動拉長身），reference + Strict Rules 雙鎖才穩。
- **批次一致性模式（≥ 2 張立繪，例：4 個角色、一組職業、SR/SSR 角色組）**：先訂統一規格（立繪多訂一項**背景處理強度**）→ 分鎖死 / 可變 → 同一段 Strict Rules 寫進每張 prompt → 生完必確認；單張跳過。詳見 common.md §3。
  - 頭身比、面向方向、視角不寫進 Strict 必飄。
  - R / SR / SSR 角色組：**頭身比仍要統一**，差距走配件密度 / 光效 / 服裝細節，不走頭身比。
- **第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`**（Style Bible + contact sheet QC）。

---

## 風格庫（預設從這幾種挑）

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

**如果使用者之前用過**：先讀 `<project-dir>/docs/imagen_history.md`，提示「上次做 [角色] 用了 [風格 + 構圖]，這次要沿用嗎？」（common.md §8）。

---

## Phase 2｜參考圖處理

依 common.md §5（先 Read 看圖 → 向使用者確認 → 只寫確認過的；上限 6 張）。立繪常見三類參考：

- **角色參考**：確認哪些保留（臉型 / 髮色 / 標誌服裝）、哪些改
- **風格參考**：描述厚塗程度、光影、線條、色彩取向，確認理解後轉 prompt 描述詞
- **服裝 / 配件參考**：確認哪些配件 / 元素要保留，寫進服裝描述

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
- [生圖模型對某些主題的限制，例如過度暴露 / 武器尺寸]
- [風格融合的潛在風險]

可以進入 prompt 階段嗎？
```

確認後進 Phase 4。

---

## Phase 4｜Prompt 撰寫與確認

### Step 1：中文 Prompt

依「**風格 → 角色身份 → 服裝細節 → 姿態 / 表情 → 構圖 / 鏡頭 → 背景 → 光影 → 排除項**」順序組。撰寫原則與確認框格式見 common.md §4；portrait **含** 🎨 風格、🧩 套用風格 boilerplate：<style_key> 兩行。

### Step 2：轉英文 + 套風格 boilerplate

翻譯原則見 common.md §4。依風格代號在英文 prompt 加上對應 boilerplate（英文原文不另翻進中文 prompt）：

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

### Step 3：確認引擎可用

依 draw-engines.md §1 確認引擎可用（整個任務只判一次）：**可用** → Phase 5；**不可用** → 生圖停止，請使用者向主任索取安裝包，不改走其他生圖途徑。立繪常用的長寬比與解析度**沒有對應 flag**，一律寫進 prompt 文字（例：`3:4 portrait aspect ratio, 2K resolution`）。

使用者只要 prompt 文字、不要實際生圖 → 以 common.md §9「生成資訊」格式交付英文 prompt + 建議參數 + 參考圖提醒。

---

## Phase 5｜圖片生成

1. **存放位置與檔名**：依 common.md §7（fallback `<cwd>/imagen-portrait/`；檔名 `{角色名或主題}_{風格代號}_{日期}_{序號}.png`，例 `ice_mage_mihoyo_genshin_20260430_01.png`）。
2. **執行**：英文 prompt Write 到 `prompt-final.txt`，呼叫 image-studio client（標準指令 common.md §9 / draw-engines.md §3）；立繪預設在 prompt 文字寫 `2K resolution`，`--reference` 可同時傳角色 + 風格 + 服裝參考。
3. **生成後**：依 common.md §6——Read 看圖 → 回報絕對資料夾路徑 → 問「滿意嗎？要調整 prompt？要做不同表情 / 姿態變體？」；調整只改使用者明確指出的部分。整批失敗見 draw-engines.md §4。

---

## Phase 6｜記憶更新

追加一列到 `<project-dir>/docs/imagen_history.md`（6 欄位與 portrait 範例見 common.md §8）。

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

通用錯誤（安全過濾 / 參考圖格式 / 網路）見 common.md §9，整批失敗分流見 draw-engines.md §4；立繪特有：

| 錯誤 | 處理 |
|------|------|
| 安全過濾觸發（暴露 / 暴力）| 調整 prompt 措辭，避開觸發詞，必要時加 `safe-for-work` 修飾 |
| 風格融合失敗（看起來像 SDXL 通用 anime）| 加強 boilerplate，強調具體遊戲名 + 視覺特徵 |
| 角色臉部變形 | 加 `well-drawn anatomically correct face` + 排除 `malformed face` |
| 武器 / 配件設計混亂 | 拆條目單獨描述，每個配件給獨立形容詞 |
| 跟參考圖差異大 | 確認 `--reference` 有正確傳，描述 must-keep 特徵 |

## 銜接

- 想還原某張參考立繪的風格 → 先用 `image-to-prompt` 逆向出中性 prompt，換上角色名再回來生
- UI 素材／頭像框等 → `imagen-ui`
- 通用生圖需求 → `imagen`
- 第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`
