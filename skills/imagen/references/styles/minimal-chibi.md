# 極簡團子卡通風（minimal-chibi）

> 參考圖：尚未歸檔——有圖就放網芳 `X:\grp.product.pm1\2. 產品改造\一四部企劃範本\kit-assets\imagen\styles\minimal-chibi\`（X 讀不到換 Y:），歸檔後改寫這行

> 用途：插畫家系／療癒系卡通、貼圖、四格漫畫。需要動作演出時往 2 頭身靠。
> 定位：近年流行的療癒系團子角色一路——頭身相連、五官極簡、靠表情與擠壓變形說話。

---

## 一、風格定義

一句話：**一顆圓滾滾的團子，加上最少的五官與小突起般的四肢，靠表情和姿勢說話。**

| 項目 | 規格 | 說明 |
|---|---|---|
| 頭身比 | **1.5–2 頭身**（預設 1.7） | 頭（不含長耳）約佔全高 55–60%。要做動作演出 → 往 2 靠；純療癒貼圖 → 往 1.5 靠 |
| 輪廓 | 頭身相連的圓角團子，**無脖子** | 剪影縮到 32px 仍可辨識；避免尖角與細長突出物 |
| 四肢 | 短小突起，手無手指（圓頭或至多分一根拇指），腳是兩小截 | 不畫關節、肌肉 |
| 五官 | 眼型照第一節〈眼型與表情〉挑，**預設小黑豆眼**；位置偏臉的下半、間距寬；嘴是一條短線或小倒三角；可加淡腮紅 | 預設五官少、不畫鼻子（動物可用小點）；選了其他眼型或梗臉時照該列規則 |
| 線條 | 單一粗細、偏粗、圓頭筆觸、略帶手繪抖動感；線色深灰或深褐，不用純黑 | 不做粗細變化與排線 |
| 上色 | 平塗為主，最多一層柔和陰影；**不做高光反射、不做材質** | 允許淡淡的紙質或蠟筆顆粒；色塊內輕微水彩暈染可接受（2026-10-12 首測效果好） |
| 配色 | 低～中飽和的粉彩系；角色本體 1 主色＋1 點綴色；背景大量留白或單一淡色 | 避免螢光色、強對比、漸層 |
| 情緒 | 表情驅動：哭、慌、開心、放空用眼睛形狀與汗滴、淚、符號（💦 ！ ♪）表現 | 允許漫畫符號；寫實表情只在「梗臉」時用 |
| 動作 | 小幅度：搖晃、彈跳、擠壓變形（squash & stretch）、縮成一團 | 大動作（揮劍、奔跑）會破壞風格，要的話改用速度線＋擠壓變形暗示 |

### 眼型與表情

眼睛是角色個性最強的開關，**不鎖死**。同一角色選定後全系列固定，只有表情變化時暫時換。

| 眼型 | 感覺 | prompt 片段 |
|---|---|---|
| 小黑豆眼（預設） | 純真、療癒、好投射情緒 | `small black bean eyes set wide apart and low on the face` |
| 死魚眼 | 厭世、放空、吐槽役 | `half-lidded deadpan eyes, flat upper eyelid line, small pupils, bored expression` |
| 圓眼帶高光 | 活潑、有神，接近繪本系 | `round eyes with a single white highlight, colored iris` |
| 線條眼 | 開心、睡著、瞇眼笑 | `closed eyes drawn as simple curved lines` |
| 符號眼 | 漫畫式瞬間情緒（><、@@、星星） | `comic symbol eyes (><), exaggerated emotion` |

**梗臉（人類表情貼上去）**：玩梗時，把寫實或半寫實的人類臉部表情（皺眉、鄙視、震驚、油膩笑容）直接放在團子臉上。反差就是笑點，所以**身體與其他部位維持團子風不變，只有臉破格**。
- prompt：`gag illustration, the round chibi body keeps the minimal cartoon style, but the face has an unexpectedly realistic human facial expression (<表情>), intentional style clash for comedic effect`
- 只用在單格梗圖、四格的反轉格、貼圖；不當角色的常態臉
- 要的是表情，不是特定真人的臉：**不畫可辨識的真人、名人或迷因原圖的臉**

### 頭身比快速對照

| 頭身 | 感覺 | 何時用 |
|---|---|---|
| 1 | 純團子，無頭身分界 | 吉祥物、扭蛋、極簡貼圖 |
| **1.5–1.8** | **本風格主軸**，療癒、好投射情緒 | 插畫、貼圖、四格 |
| 2 | 傳統 Q 版，有明確軀幹 | 需要一點動作的角色、遊戲寵物 |
| 2.5 以上 | 黏土人／縮小人形 | **已超出本風格**，改用其他 skill |

---

## 二、用途變體

| 變體 | 構圖 | 額外規則 |
|---|---|---|
| **單張插畫** | 角色置中或三分點，四周大留白，可有簡單小道具與 1–2 個環境元素 | 背景淡色平塗或紙白；不畫透視複雜的場景 |
| **貼圖／表情包** | 單角色、大表情、可加短字（字由後製加，不交給 AI 畫） | 去背或白底；動作要從剪影就看得懂 |
| **四格漫畫** | 直式 4 格、格框手繪感、每格 1 個重點動作；起承轉合，第 4 格是反轉或放空 | 同一角色跨格比例、配色必須完全一致；對白框留空，台詞後製加 |
| **周邊設計稿** | 正面＋側面＋背面（設定稿）、或吊飾／徽章用單一姿勢 | 三視圖頭身比必須一致，標明主色 hex |

---

## 三、英文 prompt 區塊

組 prompt 時照順序拼：`[SUBJECT]` → `[STYLE]` → `[VARIANT]` → `[EXCLUSION]`。風格區塊**一字不改直接貼**，只把 `{EYES}` 換成〈眼型與表情〉表裡選定的片段（預設豆豆眼）；梗臉另把該列 prompt 接在 `[SUBJECT]` 後。

```text
[STYLE]
minimal cute cartoon illustration, 1.7 head-tall chibi proportion, round blob-shaped body with head and body merged, no neck,
tiny stubby arms and legs without fingers, {EYES}, tiny simple mouth, soft blush,
thick rounded hand-drawn outline in dark warm gray with slight wobble, flat colors with at most one soft shadow tone,
muted pastel palette, plenty of white space, gentle and healing mood, subtle paper texture
```

```text
[VARIANT: illustration]  single character, centered, simple pastel background, one or two small props, generous empty space
[VARIANT: sticker]       single character, big readable expression, clear silhouette, plain white background, no text
[VARIANT: 4-koma]        vertical four-panel comic strip, hand-drawn panel borders, same character with identical proportions and colors in every panel, empty speech bubbles, no text
[VARIANT: model sheet]   character turnaround, front side and back views, identical proportions, flat color, white background, no text
```

```text
[EXCLUSION]
no realistic anatomy, no visible neck, no fingers, no detailed shading, no glossy highlights, no gradients, no neon colors,
no complex perspective background, no 3D render, no anime-style large sparkling eyes, no text or letters
（梗臉時拿掉 `no realistic anatomy`，改成 `realistic only on the face`）
```

---

## 四、鐵則

1. **不仿冒既有 IP**：prompt 裡**一律不寫**既有角色名、作者名、作品名——那會讓圖往特定角色長相靠，出現侵權疑慮。只用第一節的中性描述詞。設計新角色時，**物種、配色、標誌性特徵三者至少兩項要跟市面熱門角色明顯不同**
2. **文字不交給 AI 畫**：對白、標題、貼圖字一律後製加；prompt 永遠帶 `no text`
3. **批次先鎖規格**：≥2 張（同角色多張、四格、一組貼圖）先訂頭身比數字、主色 hex、線色，寫進每張 prompt；第一張核准後當 `--reference` 給後面每張
4. **別往精緻化漂**：AI 容易自動加高光、漸層、細節。驗收時寧可退回「太精緻」也不放行

---

## 五、驗收清單

出圖後逐項看，任一項不過就重生或修 prompt：

- [ ] 頭身比落在 1.5–2（量法：頭頂到臉頰下緣 vs 全高，長耳不算）
- [ ] 沒有脖子、沒有手指；眼型與選定的一致（梗臉只有臉破格，身體仍是團子）
- [ ] 線條粗細一致、圓頭、非純黑
- [ ] 平塗＋至多一層陰影，無高光反射與漸層
- [ ] 配色低飽和、本體 ≤2 色
- [ ] 縮到 64px 剪影仍看得出是誰、在做什麼
- [ ] 圖上沒有 AI 自己生出的文字
- [ ] 不像任何既有知名角色（物種＋配色＋特徵沒有同時撞上）
- [ ] 四格／批次：各格各張比例與配色一致
