# 繪本貓風（storybook-cat）

> 用途：可愛動物插畫、卡牌／卡套／海報主視覺、角色扮演主題圖。主角預設是貓，其他小動物照同一套規則也能用。
> 定位：日系繪本／卡套插畫一路——保留真貓骨架的可愛動物、角色扮演道具、平塗色底加圖案化裝飾背景。

---

## 一、風格定義

一句話：**畫得很省的真貓骨架角色，大大地擺在一片平塗色底上，背景只用圖案化的裝飾（星芒、火焰、浪、花草邊框），不畫場景。**

兩個最容易畫錯的地方：

1. **角色要省**：毛色是幾塊乾淨的平塗色塊，白色就是紙白；花色交界切得俐落，**不做漸層、不畫整身毛**。複雜度放在道具與服裝，不放在毛
2. **背景不是場景**：一片單色或兩色的平塗底，加上風格化圖案元素；**沒有透視、沒有房間、沒有家具與雜物**

| 項目 | 規格 | 說明 |
|---|---|---|
| 頭身比 | **2.5 頭身**（上限 2.8） | 頭高約佔全高 40%，頭大而寬；身體短胖、腿短，但仍看得出肩、腰、後腿、尾巴；能坐、能人立、能跳撲。AI 一律會拉高，prompt 要用比例數字壓 |
| 毛色 | 2–3 塊平塗色塊＋紙白；真貓花色（白、灰白賓士、虎斑、三花、黑貓） | 交界乾淨不暈染；虎斑只畫幾條簡化條紋 |
| 毛流 | 只在耳內、臉頰、胸口邊緣點**幾筆短線**；外輪廓**圓順**，全身最多一兩個小毛尖缺口 | 不全身排線、不做鋸齒狀刺毛輪廓 |
| 眼睛 | 照〈眼型與表情〉挑，**預設大圓眼＋彩色虹膜＋黑瞳＋小白高光** | 眼睛是全圖最精細的地方 |
| 臉 | 小鼻＋「ω」嘴（可張嘴叫）；鬍鬚 3–4 條細線 | 臉部元素集中、小 |
| 爪 | 舉爪時**粉紅肉球朝向觀者** | 招牌動作 |
| 線條 | 深棕到黑色的**細**沾水筆描線，轉角與收筆有粗細變化；所有形狀都有外框 | 不能是粗細完全一致的向量／貼紙線 |
| 上色 | 平塗；陰影只用一層很淡的灰或同色系 | 服裝布料可有少量水彩感明暗 |
| 配色 | **角色素淨**（灰、白、米、黑），**鮮豔留給道具與背景**（芥末黃、珊瑚紅、青藍、草綠） | 角色與背景明度要拉開 |
| 背景 | 單色或兩色平塗底＋圖案化元素：四角星芒 ✦、小星星、風格化火焰／浪／雲、花朵與葉子角落裝飾、緞帶 | 元素是平面裝飾，散佈或排在邊緣；中央讓給角色 |
| 構圖 | 角色**很大**，佔畫面 60–80%，常面向觀者；動態姿勢（跳起、揮杖、撲） | 群像時各自擺出不同動作 |
| 道具與服裝 | 魔法／角色扮演系：披風、法杖、寶石、緞帶、項鍊、書、愛心杖 | 道具顏色鮮豔、細節比角色多；**衣服要畫完整**：上衣有下襬（紮進或放出）、袖口、領口，不能畫到一半就消失在毛裡 |
| 質感 | 乾淨的數位插畫，帶一點印刷感 | 不要厚塗、不要光澤 |

### 角色設計的複雜度上限

自創角色（例：蔬菜配色的狼）也照「真貓花色」的邏輯處理：**把主題顏色變成 2–3 塊乾淨的毛色區**，不做漸層過渡。主題元素最多 1–2 個落在身體輪廓上（例：耳朵形狀、尾巴形狀），其餘交給道具。

### 眼型與表情

同一角色選定後全系列固定，只有表情變化時暫時換。

| 眼型 | 感覺 | prompt 片段 |
|---|---|---|
| 大圓眼帶高光（預設） | 無辜、好奇、有神 | `large round eyes with colored iris, black pupil and a small white highlight` |
| 死魚眼 | 厭世、不屑、貓的冷淡 | `half-lidded unimpressed eyes, flat upper eyelid line` |
| 瞇眼 | 滿足、撒嬌、睡著 | `contented squinting eyes drawn as curved lines` |
| 瞳孔放大 | 興奮、狩獵模式 | `wide eyes with fully dilated round pupils, excited` |
| 梗臉 | 人類表情貼在臉上，反差搞笑 | 規則同 `minimal-chibi.md`〈梗臉〉：身體維持本風格、只有臉破格、不畫可辨識真人 |

---

## 二、用途變體

| 變體 | 構圖 | 額外規則 |
|---|---|---|
| **主視覺** | 單一角色置中、很大、動態姿勢；平塗色底＋散佈星芒 | 直式或橫式皆可 |
| **群像（卡套／遊戲墊）** | 2–3 隻並排，各自動作不同，橫式；四角花草裝飾邊框 | 每隻毛色不同；彼此不重疊到看不出輪廓 |
| **雙色對比** | 畫面左右或對角分成兩種主題色（例：火焰紅 vs 浪花青），各配一隻角色 | 兩邊背景圖案各自呼應角色主題 |
| **卡牌插圖** | 主角在上 2/3，下 1/3 只有色底與圖案 | 重要元素不放下 1/3 |
| **角色扮演主題** | 主題靠**服裝道具**與**背景圖案**說（例：上班族＝領帶、公事包、咖啡杯；背景散佈簡化的文件、迴紋針圖案） | 不畫真實場景；圖案元素平面化、散佈 |

---

## 三、英文 prompt 區塊

組 prompt 時照順序拼：`[SUBJECT]` → `[STYLE]` → `[VARIANT]` → `[EXCLUSION]`。風格區塊**一字不改直接貼**，只把 `{EYES}` 換成〈眼型與表情〉表裡選定的片段、`{ANIMAL}` 換成主角物種（預設 `cats`）。非貓物種保留 ω 嘴與肉球的可愛化，鼻口部可稍長但不寫實。`[SUBJECT]` 描述毛色時寫成「幾塊色區」，不要寫漸層。

```text
[STYLE]
cute flat illustration of {ANIMAL} in a clean inked picture-book style, chubby proportions exactly 2.5 heads tall with the head about 40 percent of total height,
big wide head, short plump body, short stubby legs, still anatomically recognizable, coat drawn as two or three clean flat color patches plus plain white areas with crisp boundaries and no gradients,
smooth rounded outer silhouette with at most one or two tiny fur notches, only a few short fur strokes inside the ears and on the cheeks, {EYES}, small nose, tiny "ω" shaped mouth, three or four thin whiskers,
pink paw pads shown when a paw is raised, thin dark brown hand-inked dip-pen outlines with natural line weight variation, slight hand-drawn irregularity and tapered stroke ends around every shape,
clothing drawn as complete garments with visible hems, cuffs and collars,
flat fills with at most one very light shadow tone, character colors kept soft and neutral while props and background are vivid,
background is a simple flat solid color field decorated with stylized graphic motifs such as four-pointed sparkles, small stars, ribbons and corner flower ornaments,
no scenery and no perspective in the background, character drawn large and filling most of the frame in a dynamic pose
```

```text
[VARIANT: key art]      single character large in the center, dynamic pose, flat colored background with scattered sparkles
[VARIANT: group]        two or three characters side by side each in a different playful pose, distinct coat colors, flower and leaf ornaments in the corners, landscape format
[VARIANT: duo contrast] background split diagonally into two themed color fields with stylized graphic motifs (<主題A> vs <主題B>), one character on each side
[VARIANT: card art]     main subject in the upper two thirds, lower third is only flat color and small motifs
[VARIANT: role-play]    themed costume and props (<主題>), background motifs are simplified flat icons related to the theme scattered on a solid color field
```

```text
[EXCLUSION]
no room, no interior, no furniture, no scenery, no perspective background, no clutter, no realistic fur rendering, no fluffy spiky fur,
no fur gradients, no painterly brushwork, no 3D render, no glossy highlights, no depth of field, no cinematic lighting,
no jagged spiky fur silhouette, no tall or slender body, no long legs, no uniform vector stroke, no sticker-style thick outline, no clothing that fades out or ends abruptly,
no human body with animal head, no visible teeth detail, no text or letters, no thick wobbly outlines
```

---

## 四、鐵則

1. **不仿冒既有 IP 與作者**：prompt 裡**一律不寫**作者名、作品名、卡名；只用第三節的中性描述詞。他人作品的參考圖只拿來理解風格，**不能當 `--reference` 餵給生圖引擎**（自己算出、已核准的圖可以）
2. **貓是貓**：服裝道具套在動物身上，身體結構維持動物（四腳、尾巴、動物臉）；不畫成「動物頭人身」
3. **文字不交給 AI 畫**：卡名、標題、對白一律後製；prompt 永遠帶 `no text`
4. **批次先鎖規格**：同一角色出多張時，先訂毛色色塊（含 hex）、眼睛顏色、標誌配件，寫進每張 prompt；第一張核准後當 `--reference`
5. **背景一律平面裝飾**：AI 會本能地補場景與雜物（前科 2026-10-12：上班族蔥狼兩次都畫成整間辦公室，第一次還帶景深與寫實毛）；出現房間、家具、透視就退回
6. **衣服要完整、頭身要壓**：AI 會把上衣畫到胸口就消失、把身體拉成 3.5 頭身（前科 2026-10-12 第三版：襯衫沒有下半部、腿長身瘦）；驗收時兩項都要看
7. **角色不要畫滿**：主題感靠道具與背景圖案，不靠在毛上加漸層與紋理（同一前科：蔥色從白漸層到綠，角色顯得太複雜）

---

## 五、驗收清單

- [ ] 頭身比約 2.5（頭佔全高約 40%），身體短胖、腿短
- [ ] 衣服完整：上衣有下襬、袖口、領口，沒有畫到一半消失
- [ ] 毛色是 2–3 塊乾淨平塗色塊＋白，沒有漸層、沒有整身毛流
- [ ] 外輪廓圓順，毛尖缺口全身不超過一兩處（前科 2026-10-12 第四版：頭部輪廓鋸齒毛尖太多）
- [ ] 眼型與選定的一致；預設時有彩色虹膜＋黑瞳＋小白高光
- [ ] ω 嘴、細鬍鬚在；舉爪時看得到粉紅肉球
- [ ] 細沾水筆線、有粗細變化，不是一致粗細的向量線；每個形狀都有外框
- [ ] 角色素淨、道具與背景鮮豔，明度拉得開
- [ ] **背景是平塗色底＋圖案化裝飾，沒有房間、家具、透視、雜物**
- [ ] 角色佔畫面 60% 以上、姿勢有動態
- [ ] 圖上沒有 AI 自己生出的文字
- [ ] 不像任何既有作者的特定作品（構圖、角色、道具沒有整組撞上）
- [ ] 群像／批次：每隻的毛色、眼色、配件前後一致
