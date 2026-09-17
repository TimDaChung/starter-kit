# Consistency Rules

Shared lock rules for the five image-generation skills in this kit: `imagen`, `imagen-portrait`, `imagen-ui`, `generate2dsprite`, `generate2dmap`. Each SKILL.md keeps a short summary plus its own domain deltas; the canonical wording lives here. Section numbers are stable — cite as「consistency-rules.md §N」.

| § | Section | Read when |
|---|---------|-----------|
| 1 | Default visual rules | writing any prompt that contains a character or a background |
| 2 | Project asset inheritance | before the first generation in any project directory (pre-flight) |
| 3 | Batch consistency mode | the request is for 2+ same-category assets |
| 4 | Hand-off to art-style-guard | second batch onward in the same project, or any style doubt |
| 5 | Reference hygiene (anti feedback-loop) | any generation that passes a previously AI-generated image as reference |

---

## 1. Default visual rules (unless the user explicitly specifies otherwise)

> 繁中摘要：女性預設白皮膚、所有角色預設美型（gacha 審美，[EXCLUSION] 排除 western cartoon 漂移）、背景滿版到四邊用正向指令鎖；使用者明說即覆蓋。

When the user has NOT specified the following, apply these defaults:

1. **Female characters: fair luminous skin** (fair luminous skin / pale skin). Avoid sun-kissed / tanned / olive / bronzed / dark. Override only when the user explicitly requests another skin tone.
2. **All characters: refined attractive features** (mobile gacha aesthetic — beautiful face, well-proportioned body). **Avoid** western cartoon / Disney / Pixar / caricature drift. Banana Pro is biased toward western-cartoon style by certain prompt words (e.g. "manic", "wild flying outward", "battle-tested"); when such words are needed, explicitly exclude those styles in the EXCLUSION section.
3. **Background / canvas must extend full-bleed to all four edges** — NO white margins, NO letterbox bars, NO painting-style frame, NO gallery framing. Use a **positive instruction** in the COMPOSITION section ("background extends full-bleed to all four edges" / "scene extends full-bleed to all four edges of canvas"); pure negation in EXCLUSION can paradoxically trigger frame design. Applies equally to UI elements that carry a scene background and to maps.
4. Any explicit user request overrides these defaults.

---

## 2. Project asset inheritance (pre-flight, REQUIRED)

> 繁中摘要：生圖前先掃專案同類資產；找到就鎖死其規格當預設、代表作當 `--ref`、Strict Rules 明寫「visually rhyme」、再跟使用者確認 lock。

Before generating, scan the project directory for existing same-category assets. Which folders to scan is skill-specific — imagen family: `common.md` §2 table; `generate2dsprite` / `generate2dmap`: the bullets in their own SKILL.md.

**If existing same-category assets are found:**

1. **LOCK** their visual specs as the default for the new asset — do not re-invent: art style, head-body proportions, view angle, composition / margin, facing direction, lighting direction, color temperature, line weight, shading style (plus each skill's own lock items).
2. Pass 1–2 representative existing assets as `--ref` to Banana Pro **in addition to** the identity / subject ref — a concrete style anchor, not just descriptive words.
3. Embed in the Strict Rules section: "the new asset must visually rhyme with the existing project assets — same head-body proportions, same line weight, same shading style, same view angle" (swap the nouns for the asset category: portrait / UI element / sprite / map asset).
4. Confirm with the user: "the project already has N same-category assets (style / proportion / view = ...). Generate the new one with the same lock? Tell me if you want to deviate."

**Why**: existing project assets define the visual lock for new ones; re-inventing per request is the failure mode. One drifted asset in a roster / HUD / scene breaks the visual rhyme — the common case is a single asset generated without a project `--ref` that ends up with different proportions or line weight, only spotted after assembling everything side by side.

---

## 3. Batch consistency mode (2+ same-category assets in one request)

> 繁中摘要：≥ 2 張同類資產先訂統一規格、分「鎖死 / 可變」、鎖死規格用同一段文字寫進每張 prompt 的 Strict Rules、生完必確認；稀有度差距系列比例仍統一。單張跳過。

**When the user requests 2+ same-category assets in one go** (4 character portraits, 6 monster sprites, a prop pack, a set of skill icons), switch into batch mode:

1. **Define a unified spec FIRST**, before any generation: style code, aspect ratio, head/body proportion, view angle, lighting direction, **facing direction (left / right)**, composition margin, pose lock conditions, plus each skill's own spec items.
2. **Distinguish "locked" vs "variable"**: locked = style / proportion / view / facing / lighting; variable = colors / weapons / costume / scene / expression / FX color.
3. **Write the locked rules into the Strict Rules section of EVERY prompt in the batch** — identical wording across all assets; AI freedom is confined to the variable parts. Anything not written into Strict Rules drifts (head ratio, mixed views, mirrored facing, outline weight, palette temperature).
4. **After generation, verify** — one of: (a) per-asset, check each before applying; (b) batch-end, check uniformity + spec compliance across the whole set before applying any. **The confirmation step is mandatory** — it is what prevents discovering the regeneration need after integration.
5. **Exception — rarity-tier sets** (R / SR / SSR characters, frames, monsters): the visual gap is the design goal, but **proportion / base structure must stay unified**; put the gap into accessory density / FX intensity / costume or border complexity / silhouette complexity, never into head ratio or aspect ratio.

**Single-asset generation skips this mode** — go straight to the regular workflow.

**Why**: same-category assets sit together on one roster screen / HUD / rendered scene, so any spec drift is visible at first glance. Without locking the spec into every prompt, AI drifts.

---

## 4. Hand-off to art-style-guard

> 繁中摘要：同專案第二批以後的生圖、或任何風格疑慮 → 先過 `art-style-guard`（Style Bible + contact sheet QC）；本檔只管單次生圖時的 prompt 鎖。

`art-style-guard` is the authoritative Style Bible / contact-sheet QC skill. Division of labour:

- **This file** = lock rules applied *inside each prompt* at generation time (defaults, inheritance, batch Strict Rules).
- **art-style-guard** = cross-batch memory and the post-generation gate: `docs/STYLE_BIBLE.md` (style keywords, palette hex, line weight, golden samples, banned directions), contact-sheet comparison of new assets against golden samples, max 2 regeneration rounds before escalating to the user.

Hand off **before** generating when any of these hold:

- second batch onward in the same project — the first approved batch defines the bible; from then on prompts are assembled from it, not rewritten from memory
- the user says the style is inconsistent / does not match earlier assets / asks for a redo
- any doubt about whether a new asset will sit with the already-approved ones

When golden samples exist, do the §3 step-4 verification as an art-style-guard contact sheet rather than by eyeballing single images. `docs/imagen_history.md` is a usage log, not a style bible — do not treat it as one.

---

## 5. Reference hygiene (anti feedback-loop)

> 繁中摘要：AI 產出當參考圖會複利放大高頻雜訊（白點／一條條髮絲／碎花越畫越多）——身分走圖、風格走字、圖只給 gen-0 且適度縮圖。兩線（GPT／Gemini）皆適用。

Feeding a model its own output as a reference compounds high-frequency noise: the model reads speckles, strand-by-strand hair, and micro-florals in the reference as *intentional style*, reproduces them, and adds its own — each generation amplifies the last (same mechanism as re-photocopying a copy). Symptoms: detail density visibly climbing across generations, style drifting "busier" without being asked.

When a reference image is itself AI-generated, apply all three together:

1. **Gen-0 only** — the identity anchor is always the *original user-approved* image (a Style Bible golden sample). Never chain: generation N must not become the reference for generation N+1. A polluted series is rescued by going back to the earliest clean image and discarding the intermediates.
2. **Moderate downscale** — resize the reference before passing it (start at **768–1024 px long edge**, not lower): noise lives at far higher frequency than identity, so a moderate downscale kills speckles while faces, silhouettes and palettes survive. Identity drifting → raise the resolution; noise creeping back in → lower it. Record the sweet spot per character in the Style Bible.
3. **Role-split prompt** — state explicitly that the image carries identity ONLY and style follows the text: *"From the reference image, preserve ONLY the character's identity: face, eye shape and color, hair silhouette and color, costume signature marks. Do NOT treat the reference's rendering texture as style — no speckles, hair as simple masses not individual strands, clean flat color areas. The art style follows this text description instead: [style words assembled from the Style Bible]."* Text carries zero compounding noise, so style restarts clean every generation.

One-line summary: **identity from the image, style from the text; the image is always gen-0 and moderately downscaled.** Applies on both engines (draw-engines.md) — observed on the GPT line first, but the mechanism is engine-agnostic. References that are *not* AI-generated (photos, hand-drawn art) need no downscale, but the role-split wording in (3) is still good practice.
