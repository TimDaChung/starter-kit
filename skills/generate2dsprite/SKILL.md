---
name: generate2dsprite
description: "Generate + postprocess 2D game sprites/animation sheets via Nano Banana Pro + local chroma-key processor: pixel-art characters, props, creatures, spells, impacts, transparent GIF exports."
---

# Generate2dsprite

> **執行角色：美術**——關注風格一致、動作可讀性、sprite 規格（尺寸 / 幀數 / 透明背景 / 命名）。

Use this skill for self-contained 2D sprite or animation assets.

If the user wants a whole playable content pack, map, story, slideshow, or pack assembly, use `generate2dgamepack`.

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
- `art_style`: pixel_art | clean_hd | pixel_inspired | retro_pixel | map_style | project-native
- `reference`: `none` | `attached_image` | `generated_image` | `local_file`
- `prompt`: the user's theme or visual direction
- `role`: only when the asset is clearly an NPC role
- `name`: optional output slug

Read [references/modes.md](references/modes.md) when the request is ambiguous.

## Default visual rules (unless user explicitly specifies otherwise)

When the user has NOT specified the following, apply these defaults:

1. **Female characters: fair luminous skin** (avoid sun-kissed / tanned / olive / bronzed / dark). Override only when the user explicitly requests a darker skin tone.
2. **All characters: refined attractive features** (mobile gacha aesthetic — beautiful face, well-proportioned). **Avoid** western cartoon / Disney / Pixar / caricature drift. Banana Pro can be biased toward western-cartoon style by certain prompt words (e.g. "manic", "wild flying outward", "battle-tested"); explicitly exclude these styles in the EXCLUSION section when needed.
3. **Background / canvas must extend full-bleed to all four edges** — NO white margins, NO letterbox bars, NO painting-style frame, NO gallery framing. Use **positive instruction** in the composition section ("background extends full-bleed to all four edges"); pure negation in EXCLUSION can paradoxically trigger frame design.
4. Any user explicit request overrides these defaults.

See feedback memory `feedback_default_fair_skin.md` and `feedback_same_category_unified_style.md`.

---

## Project asset inheritance (pre-flight, REQUIRED)

Before generating, scan the project directory for existing same-category sprite assets:
- character / NPC sprites → `assets/sprites/`, `sprites/`
- monster sprites → `assets/sprites/monsters/`
- maps / tilesets → `assets/maps/`, `assets/tiles/`

**If existing same-category assets are found:**
1. LOCK their visual specs as the default for the new asset: art style, head-body proportions, view angle, anchor (bottom/center), pixel/HD scale, line weight, shading style, facing direction, lighting direction
2. Pass at least one of the existing assets as a `--ref` to Banana Pro alongside the identity/subject ref — concrete style anchor, not just descriptive words
3. Embed in Strict Rules: "the new sprite must visually rhyme with the existing project sprites — same head-body proportions, same line weight, same shading style, same view angle"
4. Confirm with the user: "the project already has N same-category sprites (style / proportion / view = ...). Generate the new one with the same lock? Tell me if you want to deviate."

**Why**: Existing project assets define the visual lock for new ones. One drifted sprite in a multi-character roster breaks the visual rhyme — common failure: a single character generated without a project `--ref` ends up with different head-body proportions or line weight than the rest of the roster, only spotted after assembling them side by side.

---

## Batch consistency mode (multiple same-category assets)

**When the user requests 2+ same-category assets in one go** (e.g. 4 character sprites, 6 monster sprites, a full enemy roster), switch into batch mode:

1. **Define a unified spec FIRST** before any generation: art style, sheet shape, head/body proportion (e.g. 2.5-head for chibi, 4-head for semi-chibi, true-scale for HD), view angle (top-down / 3/4 / side), lighting direction, **facing direction (left/right)** for non-symmetric idle, anchor (bottom/center/feet), margin policy.
2. **Distinguish "locked" vs "variable"**: locked = style / proportion / view / facing / sheet shape / anchor; variable = colors / weapons / costume / FX color.
3. **Write the locked rules into the Strict Rules section of EVERY prompt in the batch** — same wording across all assets, AI flexibility confined to variable parts. Sprites especially need explicit facing direction lock — without it, even `3/4 view` lets AI mirror frames left/right.
4. **After generation, verify**: per-asset (check before applying) or batch-end (check uniformity + spec compliance before applying any). The confirmation step is mandatory.
5. **Exception**: rarity-tier assets (R/SR/SSR monsters) — visual gap is the design goal, but **proportion must stay unified**; gap goes into accessory density / FX intensity / silhouette complexity, not head ratio.

**Single-asset generation skips this mode** — go straight to the regular workflow.

**Why**: Same-category sprites must visually rhyme on a shared roster screen / battle field. Without locking spec into every prompt, AI drifts (different head ratios, mixed views, mirrored facings, varying outline weight). See feedback memory `feedback_same_category_unified_style.md`.

---

## Agent Rules

- Decide the asset plan yourself. Do not force the user to spell out sheet size, frame count, or bundle structure when the request already implies them.
- Write the art prompt yourself. Do not default to the prompt-builder script.
- Use `~/.claude/skills/imagen/bin/generate.py` (Nano Banana Pro / gemini-3-pro-image-preview) for every raw image. The wrapper resolves the API key from `GEMINI_API_KEY` env, then `~/.claude/skills/imagen/.env`. There is no `lib/gen_image.py` and no `sprite-forge-claude/` folder — those are legacy doc references.
- When the user provides or implies a visual reference, first Read the reference image with the Read tool so you can see it, then pass the same path to `imagen/bin/generate.py` via one or more `--ref <path>` flags. Banana embeds the reference as inline_data and uses it as the visual anchor — do not rely on a filesystem path string inside the text prompt.
- Do not force pixel art when the asset is a map prop for `$generate2dmap` or when the user/project requests a different style. Match the map or reference style first.
- Use the script only as a deterministic processor: magenta cleanup, frame splitting, component filtering, scaling, alignment, QC metadata, transparent sheet export, and GIF export.
- Do not use scripts to generate the creative image prompt. If a legacy prompt-builder command exists, treat it as historical compatibility only, not the normal skill workflow.
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
- Use `map_style` or `project-native` when an existing map, game, or reference should define the style.

If a reference is involved:

- Make the reference visible first. Use the Read tool on the local image path so you can see it, then pass the same path to `imagen/bin/generate.py` with `--ref`. For freshly generated references, the previous step already wrote the file — pass that path with `--ref`.
- State the reference role explicitly: preserve identity/style, create an animation sheet for the same subject, create an evolution/variant, or derive a matching prop/FX.
- Preserve the stable identity markers from the reference: silhouette, palette, face/eye features, costume marks, major accessories, and material language.
- Let only the requested action or evolution change. Do not redesign the subject unless the user asks.
- Still require exact sheet shape, solid magenta background, frame containment, and same scale across frames.

Keep the strict parts:

- solid `#FF00FF` background
- exact sheet shape
- same character or asset identity across frames
- same bounding box and pixel scale across frames
- explicit containment: nothing may cross cell edges

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

Run `scripts/generate2dsprite.py process` on the raw image.

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

### 6. Return the right bundle

For a single sheet, expect:

- `raw-sheet.png`
- `raw-sheet-clean.png`
- `sheet-transparent.png`
- frame PNGs
- `animation.gif`
- `prompt-used.txt`
- `pipeline-meta.json`

For `player_sheet`, expect:

- transparent 4x4 sheet
- 16 frame PNGs
- direction strips
- 4 direction GIFs

For `spell_bundle` or `unit_bundle`, create one folder per asset in the bundle.

## Defaults

- `idle`
  - small or medium actor -> `2x2`
  - large creature or boss -> `3x3`
- `cast` -> prefer `2x3`
- `projectile` -> prefer `1x4`
- `impact` / `explode` -> prefer `2x2`
- `walk`
  - topdown actor -> `4x4` for four-direction walk
  - side-view asset -> `2x2`
- use `shared_scale` by default for any multi-frame asset where frame-to-frame consistency matters
- use `largest` component mode when detached sparkles or edge debris make the main body unstable

## Resources

- `references/modes.md`: asset, action, bundle, and sheet selection
- `references/prompt-rules.md`: manual prompt patterns and containment rules
- `scripts/generate2dsprite.py`: postprocess primitive for cleanup, extraction, alignment, QC, and GIF export

## 銜接

- 想還原某張參考圖的風格 → 先用 `image-to-prompt` 逆向出中性 prompt 再回來生
- cel-shaded chibi／Q 版風 → 改用 `generate2dsprite-chibi`
- 場景／地圖 → `generate2dmap`
- 通用生圖需求 → `imagen`
