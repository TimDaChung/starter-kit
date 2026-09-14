---
name: generate2dsprite
description: "Generate + postprocess 2D game sprites/animation sheets via Nano Banana Pro + local chroma-key processor: pixel-art or cel-shaded chibi (Q版 / gacha-style, art_style=cel_shaded_chibi) characters, props, creatures, spells, impacts, transparent GIF exports."
---

# Generate2dsprite

> **執行角色：美術**——關注風格一致、動作可讀性、sprite 規格（尺寸 / 幀數 / 透明背景 / 命名）；完成後切**企劃**視角複核規格對齊。

Use this skill for self-contained 2D sprite or animation assets, in either of two families:

- **Pixel / HD family** (`pixel_art`, `retro_pixel`, `clean_hd`, `pixel_inspired`): classic 2D game actors, 16-bit RPG sprites, HD map props. Default when the user says nothing about style.
- **Cel-shaded chibi** (`cel_shaded_chibi`): Q版 2.5-head, bold black outlines, two-tone shading, Eversoul / Idle Heroes / Disgaea / AFK Arena look. Pick it when the user says chibi / Q版 / cel-shaded / gacha-style, or when the project's existing sprites are chibi.

Both families share the same processor, workflow, and bundle structure. Sections marked **[chibi]** apply only when `art_style = cel_shaded_chibi`.

If the user wants a whole playable content pack, map, story, slideshow, or pack assembly, use `game-develop`.

## Parameters

Infer these from the user request:

- `asset_type`: `player` | `npc` | `creature` | `character` | `spell` | `projectile` | `impact` | `prop` | `summon` | `fx`
- `action`: `single` | `idle` | `cast` | `attack` | `hurt` | `combat` | `walk` | `run` | `hover` | `charge` | `projectile` | `impact` | `explode` | `death`
- `view`: `topdown` | `side` | `3/4`
- `sheet`: `auto` | `1x4` | `2x2` | `2x3` | `3x3` | `4x4`
- `frames`: `auto` or explicit count
- `bundle`: `single_asset` | `unit_bundle` | `spell_bundle` | `combat_bundle` | `line_bundle`
- `effect_policy`: `all` | `largest`
- `anchor`: `center` | `bottom` | `feet`
- `margin`: `tight` | `normal` | `safe`
- `art_style`: pixel_art | clean_hd | pixel_inspired | retro_pixel | cel_shaded_chibi | map_style | project-native
- `reference`: `none` | `attached_image` | `generated_image` | `local_file`
- `prompt`: the user's theme or visual direction
- `role`: only when the asset is clearly an NPC role
- `name`: optional output slug

Read [references/modes.md](references/modes.md) when the request is ambiguous.

## Consistency rules (read before the first generation)

The lock rules shared by all five image skills live in [`../imagen/references/consistency-rules.md`](../imagen/references/consistency-rules.md) — §1 default visual rules, §2 project asset inheritance, §3 batch consistency mode, §4 hand-off to `art-style-guard`. Summary plus the sprite-only deltas:

- **Default visual rules (§1)**: female → fair luminous skin; all characters → refined attractive features (mobile gacha aesthetic), no western cartoon / Disney / Pixar / caricature drift; canvas full-bleed to all four edges via a positive composition instruction. Explicit user requests override. **[HD / chibi]** "refined" also means big expressive eyes and a well-proportioned chibi body.
- **Project asset inheritance (§2, REQUIRED pre-flight)**: scan `assets/sprites/`, `sprites/`, `assets/sprites/monsters/`, `assets/maps/`, `assets/tiles/`. If same-category sprites exist: LOCK art style, head-body proportions, view angle, anchor (bottom / center), pixel / HD scale, line weight, shading style, facing direction, lighting direction; pass at least one existing sprite as `--ref` next to the subject ref; embed the "visually rhyme" Strict Rule; confirm the lock with the user.
  - **[chibi]** The `--ref` must be a frame-1 PNG of an existing project chibi — descriptive words alone are NOT enough. Strict Rules must say: "STRICT 2.5-head means head approximately 40% of total body height, NOT taller adult-leaning proportions even if the character concept is mature." Mature / elegant archetypes (aristocrat, sage, refined merchant) reliably drift to 3–3.5 heads without a visual anchor.
- **Batch consistency mode (§3, 2+ same-category sprites)**: unified spec first — art style, sheet shape, head/body proportion (2.5-head chibi / true-scale HD), view, lighting direction, **facing direction (left / right)** for non-symmetric idle, anchor, margin policy; locked = style / proportion / view / facing / sheet shape / anchor, variable = colors / weapons / costume / FX color; identical Strict Rules wording in every prompt; mandatory per-asset or batch-end verification. Rarity tiers (R / SR / SSR monsters) keep proportion unified — the gap goes into accessory density / FX intensity / silhouette complexity.
  - **Facing lock**: without an explicit left / right rule, even `3/4 view` lets Banana mirror frames between assets.
  - **[chibi]** Also lock the head-to-body ratio explicitly (head ≈ 40% of total height, body ≥ 1.5× head height) — Banana tends to enlarge the head, shrink the body, and flip symmetric costumes to front-facing.
- **Hand-off (§4)**: second batch onward in the same project, or any style doubt → run `art-style-guard` first (Style Bible + contact-sheet QC).

## Agent Rules

- Decide the asset plan yourself. Do not force the user to spell out sheet size, frame count, or bundle structure when the request already implies them.
- Write the art prompt yourself. Do not default to the prompt-builder script; if a legacy prompt-builder command exists, treat it as historical compatibility only, not the normal skill workflow.
- Use `~/.claude/skills/imagen/bin/generate.py` (Nano Banana Pro / gemini-3-pro-image-preview) for every raw image. The wrapper resolves the API key from `GEMINI_API_KEY` env, then `~/.claude/skills/imagen/.env`.
- When the user provides or implies a visual reference, first Read the reference image with the Read tool so you can see it, then pass the same path to `imagen/bin/generate.py` via one or more `--ref <path>` flags. Banana embeds the reference as inline_data and uses it as the visual anchor — do not rely on a filesystem path string inside the text prompt.
- Do not force pixel art when the asset is a map prop for `generate2dmap` or when the user/project requests a different style. Match the map or reference style first.
- Use the script only as a deterministic processor: magenta cleanup, frame splitting, component filtering, scaling, alignment, QC metadata, transparent sheet export, and GIF export.
- Treat script flags as execution primitives chosen by the agent, not user-facing hardcoded workflow.
- If a generated sheet touches cell edges, drifts in scale, or breaks a projectile / impact loop, either reprocess with better primitive settings or regenerate the raw sheet.
- Keep the solid `#FF00FF` background rule unless the user explicitly wants a different processing workflow.

## Workflow

### 1. Infer the asset plan

Pick the smallest useful output.

Examples:

- controllable hero with four directions -> `player` + `player_sheet`
- healer overworld NPC -> `npc` + `single_asset` or `unit_bundle`
- large boss idle loop -> `creature` + `idle` + `3x3`
- wizard throwing a magic orb -> `spell_bundle`
  - caster cast sheet
  - projectile loop
  - impact burst
- monster line request -> `line_bundle`
  - plan 1-3 forms
  - per form, make the sheets the request actually needs

### 2. Write the prompt manually

Use [references/prompt-rules.md](references/prompt-rules.md).

Choose `art_style` before writing the prompt:

- Use `pixel_art` or `retro_pixel` for classic sprites, 16-bit RPG actors, and requests that explicitly ask for pixel art.
- Use `clean_hd` for map props or assets intended to match clean hand-painted HD maps.
- Use `pixel_inspired` only when the user wants a pixel-adjacent look without retro chunkiness.
- Use `cel_shaded_chibi` when the user says chibi / Q版 / cel-shaded / gacha-style, or the project roster is already chibi.
- Use `map_style` or `project-native` when an existing map, game, or reference should define the style.

**[chibi]** When `art_style = cel_shaded_chibi`, use the `cel_shaded_chibi` style block from prompt-rules.md **Style Rules** verbatim unless the user overrides it. Never write `16-bit`, `retro JRPG`, or `chunky pixel-art` in a chibi prompt.

If a reference is involved, follow prompt-rules.md **Reference Rules**: Read the image first and pass the same path with `--ref` (a freshly generated reference is already on disk — pass that path); state the reference role explicitly (preserve identity / style, animation sheet of the same subject, evolution / variant, matching prop / FX); keep silhouette, palette, face / eye features, costume marks, major accessories, and material language fixed; let only the requested action or evolution change — do not redesign the subject unless the user asks.

Always restate the strict parts from prompt-rules.md **Global Rules** and **Containment Rules**: solid `#FF00FF` background, exact sheet shape, same identity / bounding box / pixel scale across frames, nothing may cross a cell edge.

### 3. Generate the raw image

Call `~/.claude/skills/imagen/bin/generate.py`. Pick `--ratio` and `--size` from the sheet shape:

- `1:1` for square sheets (`2x2`, `3x3`, `4x4`)
- `4:3` for `2x3` (e.g. `cast`, `talk` / dialogue)
- `4:1` for `1x4` projectiles
- default `--size 2K` for production sheets, `1K` for quick iterations

Example:

```bash
python ~/.claude/skills/imagen/bin/generate.py \
  --prompt "$(cat assets/sprites/<name>/prompt-used.txt)" \
  --ratio 1:1 --size 2K \
  --ref reference/path.jpg \
  --output assets/sprites/<name>/raw-sheet.png
```

For reference-conditioned generation, repeat `--ref <path>` per reference image. The wrapper writes the file directly to `--output`; there is no separate cache directory to look up.

#### Style reality note (Nano Banana Pro)

Banana's interpretation of "pixel art" / "16-bit" / "retro JRPG" tends to render as **painterly hi-res 2D RPG (Octopath Traveler / Triangle Strategy / Live A Live HD-2D vibe)**, not chunky chunked-pixel sprites. Set user expectations accordingly:

- if the user is fine with hi-res painterly RPG — proceed as normal, the result is high quality
- if the user explicitly wants true chunky 16-bit, plan a downscale step in postprocess (e.g. resize cells to 64–96 px width via Pillow) and warn that fine details will collapse
- prompts asking for "chunky pixels", "16-bit", "retro JRPG" still help nudge the look but will not break Banana out of its painterly bias on their own

#### Banana quirks to expect

- it often draws **black grid borders between cells** even when explicitly told not to. The chroma-key step removes them as long as the magenta backdrop is otherwise clean and `--component-mode largest` is used. Do not regenerate just for this.
- it sometimes repeats two adjacent frames (especially mid-sequence in `2x3` talking / casting sheets) — if the animation must look distinct, write more dramatic frame-to-frame deltas in the prompt

### 4. Postprocess locally

Run `python ~/.claude/skills/generate2dsprite/scripts/generate2dsprite.py process` on the raw image (absolute path: the working directory is the user's project, not this skill folder).

The processor is intentionally low-level. The agent chooses:

- `rows` / `cols`
- `fit_scale`
- `align`
- `shared_scale`
- `component_mode`
- `component_padding`
- `edge_touch` rejection strategy

Use the processor to gather QC metadata, not to make aesthetic decisions for you.

### 5. QC the result

Check:

- did any frame touch the cell edge
- did any frame resize differently than intended
- did detached effects become noise
- does the sheet still read as one coherent animation

If not, rerun with different processor settings or regenerate the raw sheet.

**[chibi] Cross-character proportion QC (batch mode, REQUIRED)** — head-body drift is the #1 silent failure; the boilerplate "2.5-head proportions" alone does not hold mature / elegant archetypes:

- Open frame 1 (idle stance) of every character side by side at the same display size. If head height differs by **>15%** between the tallest and shortest head, the batch fails (optional automated check: measure the head bbox per character via PIL alpha and compare ratios).
- **Regenerate only the outlier(s)** with a stricter Strict Rule: `"head must be approximately 40% of total chibi body height — explicitly NOT taller / leaner adult proportions; head from chin to crown must be at least as tall as the torso from shoulders to hips"`.

### 6. Return the right bundle

- Single sheet: `raw-sheet.png`, `raw-sheet-clean.png`, `sheet-transparent.png`, frame PNGs, `animation.gif`, `prompt-used.txt`, `pipeline-meta.json`
- `player_sheet`: transparent 4x4 sheet, 16 frame PNGs, direction strips, 4 direction GIFs
- `spell_bundle` / `unit_bundle`: one folder per asset in the bundle

## Defaults

Sheet-shape defaults per action (`idle` → `2x2`, large creature / boss → `3x3`; `cast` → `2x3`; `projectile` → `1x4`; `impact` / `explode` → `2x2`; topdown `walk` → `4x4`; side-view `walk` → `2x2`) and processor defaults (`shared_scale` for any multi-frame asset, `largest` component mode when detached sparkles or edge debris destabilize the main body) are listed once in [references/modes.md](references/modes.md) — Sheet Presets and Processor Defaults.

## Resources

- `references/modes.md`: asset, action, bundle, and sheet selection
- `references/prompt-rules.md`: manual prompt patterns and containment rules
- `scripts/generate2dsprite.py`: postprocess primitive for cleanup, extraction, alignment, QC, and GIF export

## 銜接

- 想還原某張參考圖的風格 → 先用 `image-to-prompt` 逆向出中性 prompt 再回來生
- 場景／地圖 → `generate2dmap`
- 通用生圖需求 → `imagen`
- 第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`
