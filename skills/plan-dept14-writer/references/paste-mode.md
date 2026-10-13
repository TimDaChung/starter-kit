# 貼圖模式操作步驟（plan-dept14-writer 第十一節）

本檔只放**本 skill 執行貼圖時的操作步驟與指令**。圖放哪、圖名、卡位、synced_block、不准動的圖、AI 示意圖與美術稿的分界、各生圖 skill 產出對哪一節，權威是 `image-slots.md`（〈通用貼法〉＝各生圖 skill「貼回企劃」段共同指向的流程）；重複的規則這裡只指向、不複述。
腳本：`scripts/paste_images.py`（list／insert／replace／split）；一部神娃／人物大活動、神裝禮包另有 `scripts/art_share_slots.py`（從美術網芳找圖，見第 9 條）。

1. **拿到頁面網址**：網址來源（PM 給，不自己找頁、不自己建頁）、部別判定（連結指紋，`notion-access.md`）、寫入憑證（`--line 神幣/娛樂城/鬥地主/魚樂園`）與回寫護欄（先列改動取得同意、寫完回讀）照 `image-slots.md`〈通用貼法〉第 2–3 條
2. **先列再貼**：`python <skill-dir>/scripts/paste_images.py list <網址>`，找出目標節的右欄 column id、卡位（`[PLACEHOLDER]`／佔位圖）、synced_block 原件。**對照 image-slots 第五節**決定每張圖的落點與圖名
3. **貼之前先報清單取得同意**：清單欄位（哪張圖 → 哪一節 block id → 新增／換卡位 → 圖名，一張表列完）照〈通用貼法〉第 3 條，使用者點頭才寫
4. **寫入**：
   - 卡位是佔位圖 → `replace <image_block_id> --image … --caption …`
   - 卡位是文字（圖片放置區／《圖片待補》／【待補】）→ `insert … --parent <右欄 column id> --after <卡位 block> --remove <卡位 block>`
   - 空的右欄或沒有卡位 → `insert --parent <右欄 column id>`（一部加 `--label "《n.圖名》"`，四部加 `--caption "《圖名》"`）
   - 魚樂園物件頁的 parent（synced_block 原件那一欄）、分鏡整張一張貼右欄、透明 PNG 貼預覽合成圖：照〈通用貼法〉第 4、8 條與 `image-slots.md` 第四節
5. **不准動的圖**與**企劃沒有圖位的產出就不出圖、不自己開節**：照〈通用貼法〉第 5–6 條
6. **AI 示意圖與美術稿分開**：照〈通用貼法〉第 7 條（美術稿由第 9 條工具從網芳找、PM 核准）
7. **寫完回讀**：腳本會驗新 block 在不在；再 `list` 一次確認位置，開頁面給使用者看；調整紀錄照 SKILL.md 第八節第 7 條註明實際操作人
8. 貼圖不加調整標記、換掉已上線舊圖時問 PM 要不要記調整紀錄：照〈通用貼法〉第 9 條
9. **一部大活動美術稿（神娃大活動、人物大活動、神裝禮包）：工具找檔、PM 核准清單再貼**——其他頁照舊 PM 給檔才貼。指令（`art_share_slots.py list <網址> [--json]` → PM 核准 → `paste <網址> --confirm`；「網芳不同」要 PM 同意才加 `--replace`，`--only <slot>` 限定格子，不加 `--confirm` 是 dry run）、狀態清單、腳本停下列候選時用 `--avatar-dir`／`--headshot-dir`／`--char-dir` 指定重跑不自己猜、吃碰特效（mp4）一律人工、貼完自己回讀被動到的格子都要回「已貼且相同」——規則與坑全在 `image-slots.md` 第七節
