# 手繪繪本風（handdrawn-storybook）

> 定位：日系奇幻 RPG 的手繪插畫一路——水彩暈染＋鉛筆／沾水筆線、低彩度大地色、像翻開一本故事書；場景像手工模型箱（diorama）般的手繪舞台。
> 與 `animal-illustration.md` 的分工：那套是乾淨平塗＋平面裝飾背景、不畫場景；本套是**手繪質感＋有場景**。

---

## 一、風格定義

一句話：**用水彩和鉛筆畫出來的奇幻故事書插圖——顏色淡而溫暖、線條看得到筆觸、畫面邊緣像紙一樣褪開。**

| 項目 | 規格 | 說明 |
|---|---|---|
| 頭身比 | 兩檔擇一：**Q 版 2.5–3 頭身**（預設）／**立繪 6–7 頭身** | Q 版用於故事書頁、小動物、場景中的角色；立繪用於角色設定與劇情 CG。同一系列只用一檔 |
| 線條 | 鉛筆或褐色（sepia）沾水筆線，**看得到筆觸**：粗細變化、偶爾斷線、收筆帶飛白 | 線色深褐或暖灰，不用純黑；不能是乾淨均勻的數位線 |
| 上色 | **透明水彩**：色塊內有水痕暈染、邊緣積色、留白透出紙色；可疊一層彩色鉛筆排線補陰影 | 不做厚塗、不做賽璐璐硬陰影、不做數位漸層 |
| 配色 | **低彩度大地色**：赭、土黃、橄欖綠、灰藍、磚紅、羊皮紙米白；全圖 4–6 色 | 高彩度只留給一個焦點（魔法光、寶石、主角的一件衣服） |
| 光線 | 柔和漫射光，像午後或陰天；陰影偏暖灰或灰紫 | 不做強逆光、光暈、電影感打光 |
| 背景 | **有場景**，像手繪的模型箱舞台：小鎮、森林、城堡、室內一角；建築與道具帶手作感（歪斜、木紋、石塊） | 景深用「越遠越淡、越少細節」表現，不用模糊；畫面四邊可淡出成紙白（vignette） |
| 紙質 | 冷壓水彩紙紋理、羊皮紙底色，邊緣可有不規則褪色 | 質感要看得出來，但不蓋過內容 |
| 角色 | 五官簡潔、眼睛中等大小（不是動漫大眼）、表情含蓄；服裝有布料皺褶與手工細節（刺繡、補丁、皮革） | 動物角色同樣用手繪水彩，毛用幾筆鉛筆短線帶過 |
| 構圖 | 故事書頁感：主角與場景同等重要，常見中景全身；可加手繪框線或圓角頁框 | 留一塊相對空的區域給文字（後製） |

### 眼型與表情

同一角色選定後全系列固定，只有表情變化時暫時換。

| 眼型 | 感覺 | prompt 片段 |
|---|---|---|
| 簡潔杏眼（預設） | 含蓄、溫柔、故事書主角 | `simple almond-shaped eyes of moderate size with a small highlight, understated expression` |
| 豆豆眼 | 童書、可愛小動物 | `small dot eyes, gentle picture-book expression` |
| 死魚眼 | 冷淡、疲憊、吐槽役 | `half-lidded tired eyes, flat upper eyelid line` |
| 瞇眼 | 微笑、滿足、睡著 | `closed smiling eyes drawn as soft pencil curves` |
| 梗臉 | 人類表情貼上去，反差搞笑 | 規則同 `minimal-chibi.md`〈梗臉〉：其他部位維持本風格、只有臉破格、不畫可辨識真人 |

---

## 二、用途變體

| 變體 | 構圖 | 額外規則 |
|---|---|---|
| **故事書頁** | 橫式或直式，角色＋場景，四邊淡出成紙白，一側留空給文字 | 預設 Q 版 |
| **角色立繪** | 單一角色全身、站姿，背景只有淡淡的水彩暈染與紙紋 | 預設立繪 6–7 頭身；適合角色設定 |
| **場景插畫** | 模型箱般的小鎮／森林／室內，角色小、場景為主 | 遠景用淡色、少細節表現距離 |
| **劇情 CG** | 2–3 個角色互動，中景，場景交代地點 | 表情含蓄，用姿勢與距離說故事 |
| **小動物繪本** | Q 版動物在自然場景中（森林、田野、廚房），童書感 | 可配合豆豆眼；顏色比預設再柔一點 |

---

## 三、英文 prompt 區塊

組 prompt 時照順序拼：`[SUBJECT]` → `[STYLE]` → `[VARIANT]` → `[EXCLUSION]`。風格區塊**一字不改直接貼**，只把 `{EYES}` 換成〈眼型與表情〉表裡選定的片段、`{PROPORTION}` 換成頭身檔（Q 版：`chibi proportion about 2.5 to 3 heads tall`；立繪：`elegant proportion about 6 to 7 heads tall`）。

```text
[STYLE]
hand-drawn fantasy storybook illustration, transparent watercolor washes with visible water blooms, pigment pooling at edges and white paper showing through,
loose pencil and sepia dip-pen linework with visible strokes, varying line weight, occasional broken lines and dry-brush stroke ends,
light colored-pencil hatching for shadows, {PROPORTION}, {EYES}, muted earthy palette of ochre, olive green, slate blue, brick red and parchment cream,
soft diffused daylight with warm gray shadows, handmade diorama-like setting with slightly crooked hand-crafted buildings and props,
distance shown by paler colors and fewer details, edges of the image fading softly into the paper, cold-pressed watercolor paper texture
```

```text
[VARIANT: storybook page]   character and setting together, edges vignetting into blank paper, one side left relatively empty for text
[VARIANT: character art]    single character full body standing, background only faint watercolor wash and paper texture
[VARIANT: scene]            diorama-like town, forest or interior as the main subject, characters small in the scene
[VARIANT: story cg]         two or three characters interacting at medium distance, setting clearly shows the location
[VARIANT: picture book]     cute small animals in a natural setting such as a forest, meadow or cozy kitchen, gentle children's book mood
```

```text
[EXCLUSION]
no clean digital lineart, no uniform vector stroke, no cel shading, no hard shadows, no thick painterly oil brushwork, no 3D render,
no glossy highlights, no saturated neon colors, no gradients that look digital, no depth of field blur, no cinematic lighting, no lens flare,
no anime-style huge sparkling eyes, no text or letters
```

---

## 四、鐵則

1. **不仿冒既有 IP 與作者**：prompt 裡**一律不寫**作者名、遊戲名、作品名；只用第三節的中性描述詞。他人作品的參考圖只拿來理解風格，**不能當 `--reference` 餵給生圖引擎**（自己算出、已核准的圖可以）
2. **手繪感是本風格的命**：GPT 引擎傾向乾淨數位線與平滑漸層，出現就退回；第一張核准後一定當同批 `--reference`，靠圖鎖質感比靠文字穩
3. **低彩度、單一焦點色**：全圖彩度壓低，只留一個高彩度焦點；整張都鮮豔就退回
4. **頭身一系列一檔**：Q 版與立繪不混用
5. **文字不交給 AI 畫**：書名、對白一律後製；prompt 永遠帶 `no text`

---

## 五、驗收清單

- [ ] 線條看得到鉛筆／沾水筆筆觸，有粗細變化，不是均勻數位線
- [ ] 水彩質感：色塊內有暈染與水痕，邊緣積色，局部透出紙白
- [ ] 低彩度大地色為主，高彩度只在一個焦點
- [ ] 柔和漫射光，沒有強逆光、光暈、景深模糊
- [ ] 場景有手作感，遠處靠變淡表現距離
- [ ] 頭身符合選定的檔位（Q 版 2.5–3／立繪 6–7）
- [ ] 眼型與選定的一致，不是動漫大眼
- [ ] 看得出紙紋，畫面邊緣有自然褪開（故事書頁變體）
- [ ] 圖上沒有 AI 自己生出的文字
- [ ] 不像任何既有作品的特定畫面（構圖、角色、場景沒有整組撞上）
