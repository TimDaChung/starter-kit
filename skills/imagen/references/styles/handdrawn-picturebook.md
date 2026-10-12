# 手繪童書風（handdrawn-picturebook）

> 定位：兒童繪本一路的奇幻冒險——**全員 Q 版**（人、敵人、生物都一樣），彩色鉛筆＋淡水彩、圓潤造型、溫暖柔和，像翻開一本給孩子看的魔法繪本。
> 與 `handdrawn-fantasy.md` 是同源拆出的兩套：那套全員寫實比例，本套全員 Q 版；**兩套不混用比例**。

---

## 一、風格定義

一句話：**所有角色都是圓滾滾的 Q 版，用彩色鉛筆和淡水彩畫在紙上，連魔王和巨人都是可愛的，像給孩子讀的冒險繪本。**

| 項目 | 規格 | 說明 |
|---|---|---|
| 頭身比 | **全員 Q 版 2–2.5 頭身**：人、敵人、魔物、坐騎、小動物一視同仁 | 大型敵人（巨人、魔像）一樣 Q 版，用「整體體型大」表現大小，不用拉長比例 |
| 造型 | 圓潤、簡化：手腳短而圓、手指最多三根或圓頭；建築與道具也圓角、略歪 | 沒有尖銳寫實細節；武器、鎧甲都畫成玩具感 |
| 線條 | **彩色鉛筆線**：線色跟著色塊走（棕、深綠、深藍），軟、略粗、帶顆粒；可局部斷線 | 不用黑線、不用沾水筆細線 |
| 上色 | 淡水彩打底＋**彩色鉛筆疊色**，看得到鉛筆排線與紙紋顆粒；留白多 | 不做厚塗、不做數位漸層、不做硬陰影 |
| 配色 | **溫暖柔和的中彩度**：奶油黃、蘋果紅、草綠、天空藍、橘；比大地色亮，但不刺眼 | 整體明亮、暖；可以多色，但每色都帶一點粉 |
| 光線 | 平光、明亮，幾乎沒有投影，只在腳下一小塊淡影 | 不做戲劇性光線 |
| 背景 | 有場景，但**簡化成繪本插圖**：小山丘、圓圓的樹、蘑菇屋、彎曲小路；遠景只用色塊帶過 | 細節少、留白多；可畫成頁框或圓角框 |
| 臉 | 豆豆眼或小圓眼、腮紅、嘴巴簡單；表情直白（開心、驚訝、害怕都很明顯） | 敵人的「兇」也要可愛：皺眉、鼓腮，不畫獠牙血盆大口 |
| 紙質 | 明顯的紙紋與鉛筆顆粒；邊緣可留白或畫成書頁 | 質感是本風格的一半 |

### 眼型與表情

同一角色選定後全系列固定，只有表情變化時暫時換。

| 眼型 | 感覺 | prompt 片段 |
|---|---|---|
| 豆豆眼（預設） | 童書、天真 | `small black dot eyes with rosy cheeks` |
| 小圓眼帶高光 | 活潑、有神 | `small round eyes with a tiny white highlight, rosy cheeks` |
| 死魚眼 | 厭世、吐槽役 | `half-lidded sleepy eyes, flat upper eyelid line` |
| 瞇眼 | 開心、滿足 | `happy closed eyes drawn as upward curves` |
| 梗臉 | 人類表情貼上去，反差搞笑 | 規則同 `minimal-chibi.md`〈梗臉〉：其他部位維持本風格、只有臉破格、不畫可辨識真人 |

---

## 二、用途變體

| 變體 | 構圖 | 額外規則 |
|---|---|---|
| **繪本頁** | 橫式，角色＋簡化場景，一側或上下留白給文字 | 預設 |
| **冒險場面** | 主角隊伍面對敵人，大小對比清楚，緊張但可愛 | 敵人兇的程度停在「鼓腮皺眉」 |
| **角色介紹** | 單一角色全身，背景只有淡色塊與紙紋 | 適合角色設定、圖鑑 |
| **封面** | 主角置中、主要角色圍繞，畫面最飽滿的一種 | 書名後製，留出上方空間 |

---

## 三、英文 prompt 區塊

組 prompt 時照順序拼：`[SUBJECT]` → `[STYLE]` → `[VARIANT]` → `[EXCLUSION]`。風格區塊**一字不改直接貼**，只把 `{EYES}` 換成〈眼型與表情〉表裡選定的片段。`[SUBJECT]` 寫大型敵人時用「比主角大幾倍的 Q 版」描述，不要寫成寫實巨人。

```text
[STYLE]
children's picture book illustration, every character in a cute super-deformed chibi proportion about 2 to 2.5 heads tall including humans, enemies and creatures,
rounded simplified shapes, short round limbs, toy-like weapons and armor, soft colored-pencil linework in brown, dark green and dark blue with visible grain,
light watercolor base washes layered with visible colored-pencil hatching, lots of white paper showing, {EYES},
warm soft palette of cream yellow, apple red, grass green, sky blue and orange, bright even lighting with only a small soft shadow under each character,
simplified storybook scenery with round trees, little hills, mushroom houses and winding paths, distant scenery as simple color shapes,
visible paper texture and pencil grain
```

```text
[VARIANT: picture book page]  characters with simplified scenery, one side or the top left empty for text, landscape format
[VARIANT: adventure scene]    the hero party facing an enemy, clear size contrast, tense but cute, enemy only pouting and frowning
[VARIANT: character intro]    single character full body, background only a soft color patch and paper texture
[VARIANT: cover]              hero in the center surrounded by main characters, the fullest composition, space at the top for a title
```

```text
[EXCLUSION]
no realistic proportions, no tall characters, no detailed anatomy, no black ink lineart, no thin dip-pen lines, no cel shading, no hard shadows,
no painterly oil brushwork, no 3D render, no glossy highlights, no dark gloomy palette, no muted earthy-only palette, no scary fangs or gore,
no depth of field blur, no cinematic lighting, no text or letters
```

---

## 四、鐵則

1. **不仿冒既有 IP 與作者**：prompt 裡**一律不寫**作者名、遊戲名、作品名、角色名；只用第三節的中性描述詞。他人作品的參考圖只拿來理解風格，**不能當 `--reference` 餵給生圖引擎**（自己算出、已核准的圖可以）。原創吉祥物也要避開既有知名角色的「物種＋配色＋招牌特徵」組合
2. **全員 Q 版、不混寫實比例**：AI 遇到「巨人」「魔王」「戰鬥」會把角色拉成寫實比例，出現就退回；要寫實比例改用 `handdrawn-fantasy.md`
3. **鉛筆顆粒是本風格的一半**：GPT 引擎傾向乾淨數位線，沒有鉛筆顆粒與紙紋就退回；第一張核准後一定當同批 `--reference`
4. **兇也要可愛**：敵人不畫獠牙、血、恐怖表情
5. **文字不交給 AI 畫**：書名、對白一律後製；prompt 永遠帶 `no text`

---

## 五、驗收清單

- [ ] 所有角色都是 Q 版 2–2.5 頭身，包含人與敵人；大型敵人靠整體體型表現大小
- [ ] 造型圓潤簡化，武器鎧甲是玩具感
- [ ] 彩色鉛筆線（非黑線），看得到鉛筆顆粒與排線
- [ ] 淡水彩打底、留白多、紙紋明顯
- [ ] 溫暖柔和的中彩度，整體明亮
- [ ] 背景是簡化的繪本場景，遠景只是色塊
- [ ] 敵人兇得可愛，沒有恐怖元素
- [ ] 圖上沒有 AI 自己生出的文字
- [ ] 不像任何既有作品的特定畫面或角色
