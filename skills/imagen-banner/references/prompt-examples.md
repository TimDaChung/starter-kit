# 實測過的 prompt 範例

以下三組在 image-studio GPT 線實測過（2026-09-22，各 2 張，共 6 張），**文字全部正確**：長句、`200%`、繁體中文標題都沒有崩。

⚠️ **比例注意**：實測當時跑的是 21:9，下面的 prompt 已改成**部門預設 8:5（800 × 500 交付）**（2026-09-23）。改比例後**尚未重測**——引擎當時配額用罄（HTTP 429）。8:5 比 21:9 高得多，主角與文字的相對關係會明顯改變，第一次用要特別看：主角會不會被裁到、文字三級還塞不塞得下、CTA 有沒有被擠出安全區。重測後再把這段拿掉。

企劃有指定尺寸就以企劃為準（例：《218 小惡魔轉盤︰機台廣宣》指定 800 × 500 jpg）。生成後一律照 SKILL.md Phase 4 的腳本裁到交付尺寸。
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
