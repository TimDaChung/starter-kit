# 實測過的 prompt 範例

以下四組都在 image-studio GPT 線實測過，**文字全部正確**：長句、`200%`、繁體中文標題與四字 CTA 都沒有崩。

- 第 1～3 組：2026-09-22，各 2 張共 6 張（當時跑 21:9，prompt 已改為部門預設 8:5）
- 第 4 組：2026-09-23，照真實企劃跑 8:5，**一次到位**

**8:5 已驗證**：prompt 寫 `8:5 aspect ratio (800 x 500 px deliverable)`，引擎實際吐出 1586 × 992（比例正好 1.60），**等比縮到 800 × 500 即可、裁切 0 px**。

企劃有指定尺寸就以企劃為準（例：《218 小惡魔轉盤︰機台廣宣》指定 800 × 500 jpg）。生成後仍照 SKILL.md Phase 4 的腳本處理到交付尺寸——引擎不保證每次都給同一比例。
拿來當骨架改寫時，`[TYPOGRAPHY]` 段的字樣換成自己的文案即可，其餘段落對應的鐵則見 `rules.md`。

注意：引擎沒有 `--ratio` flag，長寬比與解析度必須寫在 prompt 文字裡（見每組第一行）。

---

## 1. 機台宣傳（題材 Hero 當王）

出圖結果：Logo 立體斜角＋金邊＋紅金漸層＋雲紋，45 字元的 Selling Line 兩張全對。
小瑕疵：其中一張「Drum」與「Trio」字距偏緊，可在 prompt 補 `generous letter spacing between words`。

```
Mobile social-casino promotional banner, 8:5 aspect ratio (800 x 500 px deliverable), 2K resolution, glossy high-saturation casino art style.

[HERO] Three ornate Chinese festival drums stacked diagonally on the left half of the canvas: the largest red drum with gold dragon relief and gold studs sits front and centre and is the single biggest object in frame; a green and a blue drum tucked behind it, crossed drumsticks with red and blue tips.

[ENERGY CORE] A massive warm golden radial light burst directly behind the drums, glowing bloom and floating embers, making the drums pop off the background.

[BACKGROUND] Golden oriental palace courtyard at dusk, softly blurred, lower contrast and lower saturation than the foreground, extends full-bleed to all four edges.

[WEALTH] Gold coins in three depth layers: one or two oversized blurred coins drifting in the extreme foreground, crisp mid-size coins spraying around the drums, and a dense pile of gold coins forming a base along the bottom edge.

[COLOR] Dominant red and gold, orange secondary, highest brightness and saturation concentrated on the drums, the logo and the button.

[TYPOGRAPHY] Three levels of text, all rendered cleanly and spelled exactly as written:
Level 1 - game logo reading "DRAGON DRUM TRIO" in chunky three-dimensional beveled letterforms, thick gold outline, red-to-orange gradient fill, glossy highlights, small oriental cloud ornaments flanking it, placed upper right, the largest text on the canvas.
Level 2 - selling line reading "BEAT THE DRUMS FOR TRIPLE BONUS FEATURE WINS!" in clean bold white sans-serif with dark outline, set in two centred lines directly under the logo, clearly smaller than the logo.
Level 3 - a large green rounded call-to-action button at lower right with white uppercase text reading "PLAY NOW".

[EXCLUSION] No watermark, no UI frame, no extra text beyond the specified copy, no western cartoon or Disney styling, no caricature.
```

---

## 2. 節慶促銷（優惠數字當王）

出圖結果：`200%`、`4TH of JULY SALE`、`MORE COINS`、`GET IT` 全對。
小瑕疵：其中一張數字右緣壓到吉祥物，可在 prompt 補 `keep the mascot clear of the number, no overlap`。

```
Mobile social-casino Fourth of July sale banner, 8:5 aspect ratio (800 x 500 px deliverable), 2K resolution, glossy high-saturation casino art style, celebratory and loud.

[HERO] A giant offer number is the single visual king of the composition: "200%" rendered enormous at the centre, gold gradient with thick red outline and glossy highlights, larger than everything else in frame.

[ENERGY CORE] Bursting fireworks behind the centre, warm golden glow radiating outward from the number.

[BACKGROUND] Deep blue night sky over a blurred city skyline and water reflection, dark at the outer edges and bright toward the centre, low detail so it never competes with the centre, extends full-bleed to all four edges.

[WEALTH] An oversized Uncle Sam top hat, red white and blue with a star band, tipped up and overflowing with gold coins; a wide gold coin pile forming a base along the bottom; a few oversized blurred coins in the extreme foreground.

[MASCOT] A cheerful cartoon pig in an Uncle Sam costume with star-spangled top hat and blue jacket, standing at the right side, waving, clearly smaller than the offer number.

[COLOR] Deep blue background, red and white for festive identity, gold reserved for money and value; highest brightness concentrated on the number and the button.

[TYPOGRAPHY] Three levels of text, all rendered cleanly and spelled exactly as written:
Level 1 - headline reading "4TH of JULY SALE" across the top, bold condensed letters, white and red with dark outline, star accents.
Level 2 - under the giant "200%", a line reading "MORE COINS" in bold gold letters with dark outline.
Level 3 - a large green rounded call-to-action button at bottom centre with white uppercase text reading "GET IT".

[EXCLUSION] No watermark, no UI frame, no extra text beyond the specified copy, no western caricature styling beyond the mascot, no real brand logos.
```

---

## 3. 節慶促銷（繁體中文版）

出圖結果：中秋加碼／更多金幣／立即領取，1:1 檢視筆畫正確、無簡體、無假字。
關鍵是 `[TYPOGRAPHY]` 段明寫 **TRADITIONAL CHINESE characters**、`correct stroke shapes`，並在 `[EXCLUSION]` 排除 `no Japanese kana, no simplified Chinese, no gibberish characters`。

```
Mobile social-casino Mid-Autumn Festival sale banner for a Taiwanese mahjong casino app, 8:5 aspect ratio (800 x 500 px deliverable), 2K resolution, glossy high-saturation casino art style, festive and loud.

[HERO] A giant offer number is the single visual king of the composition: "200%" rendered enormous at the centre, gold gradient with thick red outline and glossy highlights, larger than everything else in frame.

[ENERGY CORE] A huge full moon with warm golden glow directly behind the number, soft radiating light and drifting osmanthus petals.

[BACKGROUND] Deep indigo night sky with stylised clouds and a blurred classical Chinese pavilion, dark at the outer edges and bright toward the centre, low detail so it never competes with the centre, extends full-bleed to all four edges.

[WEALTH] A red and gold gift box overflowing with gold coins on the left; a wide gold coin pile forming a base along the bottom; two oversized blurred coins in the extreme foreground.

[MASCOT] A cheerful cartoon jade rabbit in a red silk outfit standing at the right side holding a mooncake, clearly smaller than the offer number.

[COLOR] Deep indigo background, red and gold for festive identity, gold reserved for money and value; highest brightness concentrated on the number and the button.

[TYPOGRAPHY] Three levels of text in TRADITIONAL CHINESE characters, rendered cleanly and written exactly as specified, correct stroke shapes:
Level 1 - headline across the top reading 中秋加碼 in bold gold Chinese characters with red outline and dark drop shadow.
Level 2 - directly under the giant "200%", a line reading 更多金幣 in bold white Chinese characters with dark outline.
Level 3 - a large green rounded call-to-action button at bottom centre with white Chinese characters reading 立即領取.

[EXCLUSION] No watermark, no UI frame, no Japanese kana, no simplified Chinese, no extra text beyond the specified copy, no gibberish characters.
```

---

## 4. 機台廣宣・繁中在地化（照真實企劃、帶參考圖）

2026-09-23 實測，來源《218 小惡魔轉盤︰機台廣宣》。企劃要求「使用機台 wow 現有廣宣翻譯、排版與字色與 wow 一致、按鈕色須維持原版設計」，所以**帶兩張參考圖**：wow 英文原版（鎖版面與配色）＋企劃的內文排版示意（鎖中文版面）。

```bash
python ~/.claude/skills/image-studio/scripts/image-studio-client.py draw \
  --count 1 --prompt "$(cat prompt.txt)" \
  --reference wow現有廣宣.jpg --reference 內文排版示意.png --output out
```

出圖結果：五段中文（角標／Logo／slogan／CTA／法遵小字）**逐字核對全對**，版面與 wow 原版一致，綠色 CTA 保留。
驗收：縮圖 1 秒四問過、灰階下 CTA 靠白字＋亮邊框撐住、模糊只剩「主角＋Logo」兩塊。
**唯一沒過的是 A6**：高飽和像素 61.7%（常見 10–35%）＝全畫面一起豔，背景暗部要壓深、把高飽和留給 Logo / CTA / 金幣。

與企劃的落差（交付前要回報 PM）：角標做成金色圓徽（企劃示意是白底方標）、CTA 少了白色內板。

```
Mobile social-casino slot promotional banner, 8:5 aspect ratio (800 x 500 px deliverable), 2K resolution, glossy high-saturation casino art style. Localized Traditional Chinese version of the provided reference banner: keep the reference's layout, colour scheme and lettering style, only the copy becomes Chinese.

[HERO] A cheeky red baby devil mascot on the left half — small white horns, brown tuft of hair, small bat wings, white diaper, holding a tall golden trident, other hand raised waving, grinning. Largest character in frame, fully inside the canvas, not cropped by the edges.

[ENERGY CORE] Hot orange-red glow radiating from behind the devil, burning embers and flame licks.

[BACKGROUND] Hellish volcanic cavern with molten lava river flowing toward the viewer, dark red rock walls, softly blurred and lower contrast than the foreground, darker at the outer edges and brighter toward the centre, extends full-bleed to all four edges.

[WEALTH] A dense pile of gold coins running along the bottom edge as a base, a few crisp coins around the devil, one or two oversized blurred coins in the extreme foreground.

[COLOR] Dominant red and orange, gold for the logo and coins, deep red shadows. Highest brightness concentrated on the logo and the button.

[TYPOGRAPHY] All text in TRADITIONAL CHINESE characters, correct stroke shapes, spelled exactly as specified, placed in the right half so the devil stays clear:
Level 1 - game logo reading 小惡魔轉盤 in chunky three-dimensional beveled Chinese letterforms, gold-to-yellow gradient fill with thick dark red outline and glossy highlights, sitting on a dark red plaque, the largest text on the canvas.
Level 2 - a slogan band under the logo: solid yellow horizontal bar with bold black Chinese text reading 惡魔出動，烈焰狂賞！
Level 3 - a large green rounded call-to-action button at lower right with bold black Chinese text reading 立即前往, white inner panel, gold rim.
Corner badge - a small white rounded label at the upper left reading 全新VIP機台！in bold black Chinese text.
Fine print - a small line along the bottom left in white Chinese text reading ※下注仍需消耗神幣/地主幣

[EXCLUSION] No watermark, no UI frame, no English words, no Japanese kana, no simplified Chinese, no gibberish characters, no extra text beyond the specified copy.
```
