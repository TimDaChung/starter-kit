# imagen 家族共用規則（imagen / imagen-portrait / imagen-ui）

三支 imagen skill 的共用流程、格式與指令集中在此，各 SKILL.md 只留 2–4 行摘要 + 該 skill 的差異。章節編號固定，引用寫「見 common.md §N」。§1–§3 的完整條文在同目錄 `consistency-rules.md`（五支生圖 skill 共用，英文正文 + 繁中摘要），此處只放繁中摘要與 imagen 家族的參數表。

| § | 章節 | 何時讀 |
|---|------|--------|
| 1 | 預設視覺規則 | 寫任何含角色 / 背景的 prompt 前 |
| 2 | 專案既存資產優先 | 每個專案第一次生圖前（pre-flight） |
| 3 | 批次一致性模式 | 一次要 ≥ 2 張同類資產 |
| 4 | Prompt 確認框 | Phase 4 Step 1 / Step 2 |
| 5 | 參考圖規則 | 使用者附圖 / 需要 `--ref` |
| 6 | 生成後檢查與調整循環 | 每次生成或交付後 |
| 7 | 存檔位置與檔名 | Phase 5 生成前 |
| 8 | `imagen_history.md` | Phase 1 讀偏好、Phase 6 寫入 |
| 9 | 呼叫 `generate.py` 與模式判定 | Phase 4 Step 2 / Phase 5 / Phase 5.5 |

---

## §1 預設視覺規則

使用者沒明說就套用：**女性角色白皮膚**（fair luminous skin，避免 tanned / olive / bronzed / dark）、**所有角色美型**（手遊 gacha 審美；[EXCLUSION] 段排除 western cartoon / Disney / Pixar / caricature，狂野詞如 "manic"、"wild flying outward"、"battle-tested" 會誘發西風）、**背景滿版到四邊**（[COMPOSITION] 段用正向指令 "background extends full-bleed to all four edges"，純 negation 反而誘發 frame design）。使用者明確要求不同就依使用者。

完整條文：`consistency-rules.md` §1。

---

## §2 專案既存資產優先（生圖前必做）

生圖前**先掃專案目錄**找同類資產；找到就：(1) 把其規格**鎖死當預設**，不重新發想；(2) 代表性 1–2 張當 `--ref`，**在識別 / 題材 ref 之外多塞一張既有資產 ref 強制風格鎖**；(3) Strict Rules 段明寫「the new asset must visually rhyme with the existing project assets — same …」；(4) 跟使用者確認：「專案既有 N 張同類資產（規格為…），這次照樣生？要改請明說」。

完整條文與「為什麼」：`consistency-rules.md` §2。imagen 家族各 skill 的掃描路徑與鎖死項目：

| skill | 掃描路徑 | 鎖死項目 | Strict Rules 例句重點 |
|-------|---------|---------|---------------------|
| imagen | 立繪 `立繪/`、`assets/portraits/`、`portraits/`；sprite `assets/sprites/`、`sprites/`；UI `assets/ui/`、`ui/`；地圖 `assets/maps/`、`assets/backgrounds/`、`maps/` | 畫風、頭身比、視角、構圖、留白比例、面向方向、光源、色溫 | same head-body proportions, same line weight, same shading style, same view angle |
| imagen-portrait | `立繪/`、`assets/portraits/`、`portraits/`、`assets/sprites/`（chibi sprite 也可作 portrait 風格參考） | 畫風代號、頭身比、視角、光源、構圖留白、面向方向 | same head-body proportions, same view angle, same lighting |
| imagen-ui | `assets/ui/`、`ui/`、`assets/icons/`、`assets/frames/`（立繪 / sprite 亦可參考其風格代號） | 風格代號、邊框粗細 / 轉角圓度、光效強度、配色主軸、稀有度視覺系統 | same border weight, same corner radius, same lighting style, same color temperature |

---

## §3 批次一致性模式（同類別資產 ≥ 2 張）

一次要 ≥ 2 張同類資產時：(1) **先訂統一規格**——風格代號、長寬比、頭身比、視角、光源方向、**面向方向（朝左 / 朝右）**、構圖留白、姿態鎖定條件；(2) 分「鎖死」（風格 / 比例 / 視角 / 面向 / 光源）vs「可變」（配色 / 武器 / 場景 / 表情）；(3) 鎖死規格用**同一段文字**寫進每張 prompt 的 Strict Rules，AI 只能動可變項；(4) **生完必確認**——逐張確認再套用，或全部生完一次看統一性 + 符合度，不能省；(5) 稀有度差距系列（R / SR / SSR）視覺差距是設計目的，但**比例仍統一**，差距走配件密度 / 光效 / 細節複雜度。單張生圖跳過此模式。

完整條文與「為什麼」：`consistency-rules.md` §3。同專案第二批以後 / 風格疑慮 → 先過 `art-style-guard`（`consistency-rules.md` §4）。

---

## §4 Prompt 確認框（Phase 4）

**Step 1 撰寫原則（嚴格遵守）**：只包含討論中**明確提到或確認**的內容；不自行添加背景元素、光影描述、情緒氛圍、構圖指示；不用模板套路詞（"masterpiece, best quality, 4k, detailed"）；簡潔直白，描述清楚即可。

**展示格式（唯一版本）**：

```
## Prompt 確認

📝 中文 Prompt：
> [完整中文 prompt，基於討論內容整理]

📐 長寬比：[ratio]
📏 解析度：[size]
🎨 風格：[風格代號]                    ← portrait / ui 用；imagen 省略
🧩 套用風格 boilerplate：<style_key>    ← portrait / ui 用；imagen 省略
📦 元件：[元件代號]                    ← 僅 ui
🖼️ 參考圖：[有/無，幾張]

沒問題的話我就轉英文並開始生成。要修改什麼嗎？
```

使用者回「好」「OK」「沒問題」「可以」即視為確認，直接進 Step 2，不再追問。

**Step 2 轉英文原則**：忠於中文 prompt，不增不減；自然英文；不加翻譯過程中想到的「補充」。portrait / ui 在英文版加上對應風格 boilerplate（英文原文不另翻進中文 prompt，確認框以 🧩 行標示）。轉完依 §9 判定模式執行。

---

## §5 參考圖規則

1. **先 Read 看圖**（Claude Code 可直接看圖），看過才決定寫什麼。
2. **向使用者確認**：風格參考 → 描述你看到的特徵（厚塗程度、光影、線條、色彩取向）確認理解正確；角色 / 元件 / 服裝參考 → 確認哪些特徵保留、哪些可改。
3. **只把確認過的特徵寫進 prompt**。
4. API 模式用 `--ref <path>` 傳給 Banana Pro，可重複多次（角色 + 風格 + 服裝可一起傳）；wrapper 會把圖嵌成 inline_data，**不要**只在 prompt 文字裡寫路徑。Prompt 模式則提醒使用者一起上傳到 Google AI Studio。
5. **上限 6 張**，超過品質下降。支援 JPG / PNG / WebP / GIF。

---

## §6 生成後檢查與調整循環

1. 用 Read 工具看生成的圖，確認正常產出（imagen-ui 另加工程視角核對，見其 SKILL.md）。
2. **回報完整絕對資料夾路徑**（不逐檔列）。
3. 詢問：「滿意嗎？要調整 prompt 重新生成，還是這張可以用？」（portrait / ui 另問是否做變體）。
4. 要調整 → **只改使用者明確指出的部分**，重新走 §4 確認再生成；Prompt 模式則重新產出英文版交付。

---

## §7 存檔位置與檔名

**位置決定順序**：(1) 使用者明確指定 → 用指定的；(2) 沒指定 → **先問**「要存在哪？」；(3) fallback → 當前工作目錄下 `<skill 名>/`（`imagen/`、`imagen-portrait/`、`imagen-ui/`）。

| skill | 檔名格式 | 範例 |
|-------|---------|------|
| imagen | `{簡短描述}_{日期}_{序號}.png` | `fire_monster_20260331_01.png` |
| imagen-portrait | `{角色名或主題}_{風格代號}_{日期}_{序號}.png` | `ice_mage_mihoyo_genshin_20260430_01.png` |
| imagen-ui | `{元件代號}_{風格代號}_{日期}_{序號}.png` | `icon_skill_mihoyo_genshin_20260430_01.png` |

最終英文 prompt 先 Write 到 `prompt-final.txt`（與輸出同目錄），再呼叫 generate.py。

---

## §8 `imagen_history.md`

路徑 `<project-dir>/docs/imagen_history.md`，三支 skill **共用同一檔、同一欄位**（6 欄）。

- **Phase 1 讀**：使用者之前用過 → 先讀，提示「上次你做 [情境] 用了 [尺寸 / 風格 / 構圖]，這次要沿用還是重新設定？」
- **Phase 6 寫**：每次完成 prompt 產出或成功生成後追加一列。

```markdown
| 日期 | skill | 用途 | 最終英文 prompt 摘要 | 輸出檔 | 備註 |
|------|-------|------|---------------------|--------|------|
| 2026-03-31 | imagen | 卡牌插圖 | fire monster, anime style, 3:4, 2K | imagen/fire_monster_20260331_01.png | 有參考圖 |
| 2026-04-30 | imagen-portrait | 冰系法師半身立繪 | ice mage girl, mihoyo_genshin, bust shot, 3:4, 2K | imagen-portrait/ice_mage_mihoyo_genshin_20260430_01.png | 有上傳服裝參考 |
| 2026-04-30 | imagen-ui | 火球術技能 icon | fireball skill icon, mihoyo_genshin, 1:1, 1K | imagen-ui/icon_skill_mihoyo_genshin_20260430_01.png | 五階稀有度變體 |
```

這是使用紀錄，不是 Style Bible；跨批風格守門用 `art-style-guard` 的 `docs/STYLE_BIBLE.md`。

---

## §9 呼叫 `generate.py` 與模式判定

**Key 解析順序**：先讀環境變數 `GEMINI_API_KEY`，沒有再讀 `~/.claude/skills/imagen/.env`。

**模式判定（每次任務只判一次，在 Phase 4 Step 2 之後）**：Key 存在 → **API 模式**（Phase 5 直接生成）；否則 **Prompt 模式**（跳過 Phase 5，走 Phase 5.5 交付 prompt）。

**標準指令**（wrapper 自動讀 key、組 payload、存 PNG，不需手動處理 base64 / curl；參數詳見 `--help`）：

```bash
python ~/.claude/skills/imagen/bin/generate.py \
  --prompt "$(cat prompt-final.txt)" \
  --ratio 3:4 --size 1K \
  --ref reference/style.jpg \
  --output {output_path}
```

- `--ratio` 只接受：`1:1` `2:3` `3:2` `3:4` `4:3` `4:5` `5:4` `9:16` `16:9` `21:9`；`--size` 只接受：`1K` `2K` `4K`
- `--ref` 可重複，最多 6 張（§5）

**Prompt 模式交付格式（Phase 5.5）**：

```
## 生成資訊

📝 英文 Prompt：
> [完整英文 prompt]

📐 建議長寬比：[ratio]
📏 建議解析度：[size]
🖼️ 參考圖：[幾張，提醒一起上傳到 AI Studio]

💡 使用方式：到 Google AI Studio 貼上 prompt，上傳參考圖，選擇對應的長寬比即可生成。
```

**通用錯誤處理**（各 skill 的領域錯誤另列在自己的 SKILL.md）：

| 錯誤 | 處理方式 |
|------|---------|
| API Key 無效 | 提示使用者檢查 `.env` 中的 `GEMINI_API_KEY` |
| 生成失敗（安全過濾） | 告知使用者，建議調整 prompt 中可能觸發過濾的詞彙 |
| 參考圖格式不支援 | 支援 JPG/PNG/WebP/GIF，提示使用者轉換格式 |
| 網路錯誤 | 提示檢查網路連線，可重試一次 |
