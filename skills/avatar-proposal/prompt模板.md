# 示意圖提示詞模板

**模板本體在 `scripts/gen_sheets.py` 的 `TEMPLATE`／`TIER_TEXT`／`DEFAULT_AVOID`**，這份只說明結構與前科。改提示詞兩處一起改。

## 結構（每組一段，英文）

1. **版面與畫風錨**：給美術看的人物設定圖；横幅、灰褐底 `#6b5e58`、左右兩直立圓角框；男左女右；Q 版三頭身、正面站姿、大眼；台灣手遊 cel-shaded、粗線、平塗、花紋大而少；只學 reference 的格式與畫風、不抄服裝與主題；無文字無編號
2. **本期主題一句**（`theme_en`）＋**排除項**（`avoid_en`，預設含宗教建築、殘破、書、鐘、蛇、綠帽、女性重甲與大型武器、陰暗、露太多）
3. **強度段**（依 tier）：
   - 新手：簡樸、無花紋、無武器、無特效、無翅膀、兩框皆素底
   - 一般：中等細節；**武器或特效擇一**；無翅膀
   - 儲值：華麗帶金邊、有武器、無特效、翅膀可有可無、兩框素底
   - BOSS：最華麗、武器＋特效全開
4. **左男右女各一段**：`prompt_en`（外觀）＋主色；該側的前景（指定角落、小、不遮人物）；該側是否滿版背景，否則註明保持素底
   - **特效要在 `prompt_en` 寫明實體或虛體**（Leo 2026-10-08）：虛體寫成「某元素化成某形狀」（*a phoenix-shaped burst of flame*、*a small dragon formed from flowing water*），實體寫成真的生物或物件（*a real phoenix creature perched on the shoulder*）。只寫 *phoenix* 模型會自己選，常常和需求不符

## 人物更衣室（`DRESSING_TEMPLATE`，key `07_dressing_room`）

Leo 2026-10-08：更衣室也要出圖給美術確認。一張 3:2 橫幅場景：對稱單點透視、中央圓形站台加台階（玩家人物站的位置）、下半部地板留空、兩側主題布景、**不畫任何人物或生物前景**。場景內容寫在 `dressing_room.prompt_en`。參考圖是九月人物設定 pptx（`●Avatar魔鬼營\202609_天魔混世記(大活動)\2609_大活動_人物設定.pptx`）最後一頁的圖，腳本自動抽到輸出資料夾的 `_ref_dressing_room.jpg`

## 參考圖

每組帶**同強度的九月成品**一張（`REF_BY_KEY`）：新手 4266+4267、一般1 4268+4269、一般2 4270+4271、儲值借用 4268+4269、BOSS1 4272+4273、BOSS2 4274+4275。腳本自動到美術網芳抓，路徑見 `參考素材索引.md`；線上素材不進 kit。固定用這五張，不要每月換成最新成品（會把上月主題帶進來）；只有線上畫風改版才換。

## 前科

| 現象 | 對策（已進模板） |
|---|---|
| 背景自己長出鳥居、石燈籠 | `DEFAULT_AVOID` 列入；背景 `prompt_en` 結尾加 "no torii gate, no stone lanterns" |
| 一般裝比九月成品精緻、花紋多 | 版面段加 "few small details, keep patterns large and simple"；一般段加 "Moderate detail only" |
| 五組並行全部失敗 | 腳本序列執行，不開並行 |
| 兩張候選浪費配額 | `--count 1` |
| Boss 沒有天然翅膀（日系妖怪） | prompt 寫 "instead of wings, …" 給替代物；部件表翅膀標「美術設計」 |
