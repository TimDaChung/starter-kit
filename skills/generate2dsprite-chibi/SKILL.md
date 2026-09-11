---
name: generate2dsprite-chibi
description: "generate2dsprite 的 CEL-SHADED CHIBI 版：Q版 2.5-head、粗黑描邊、雙色階（Eversoul/Disgaea 風）。Use when user explicitly wants chibi / Q版 / cel-shaded / gacha-style sprites."
---

# Generate2dsprite-Chibi

Use this skill for self-contained 2D sprite or animation assets in **cel-shaded chibi anime style**.

This is a sister skill to `generate2dsprite` — same processor, same workflow, different default art style.

- Use `generate2dsprite` (original) when the user wants pixel art, retro JRPG, 16-bit sprites, or clean HD map props.
- Use `generate2dsprite-chibi` (this) when the user wants cel-shaded chibi, gacha-style anime sprites, or animation-heavy assets where frame-to-frame consistency matters most.

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

1. **Female characters: fair luminous skin** (avoid sun-kissed / tanned / olive / bronzed / dark). Override only when the user explicitly requests a darker skin tone. Applies even at chibi proportions.
2. **All characters: refined attractive features** (mobile gacha aesthetic — beautiful face, big expressive eyes, well-proportioned chibi). **Avoid** western cartoon / Disney / Pixar / caricature drift. Banana Pro can be biased toward western-cartoon style by certain prompt words (e.g. "manic", "wild flying outward", "battle-tested"); explicitly exclude these styles in the EXCLUSION section when needed.
3. **Sprite sheet must fill canvas edge-to-edge with the magenta background** — NO white margins, NO letterbox bars, NO frame around the sheet. The magenta #FF00FF must extend to all four edges of every cell.
4. Any user explicit request overrides these defaults.

See feedback memory `feedback_default_fair_skin.md` and `feedback_same_category_unified_style.md`.

---

## Project asset inheritance (pre-flight, REQUIRED)

Before generating, scan the project directory for existing same-category chibi assets:
- character chibi sprites → `assets/sprites/<char>/idle/`, `assets/sprites/<char>/talk/`, etc.
- monster chibi sprites → `assets/sprites/monsters/`
- judge / NPC chibi → `assets/sprites/judges/`, `assets/sprites/npcs/`

**If existing same-category chibi assets are found:**
1. LOCK their visual specs as the default: head-body proportion (count head heights in their frame 1), view angle, anchor, line weight, shading style, facing direction, lighting direction
2. Pass at least one frame 1 PNG of an existing chibi as a `--ref` alongside the identity/subject ref — this gives Banana a concrete chibi proportion anchor; descriptive words alone are NOT enough (mature/elegant archetypes consistently drift to 3-3.5 head without a visual anchor)
3. Embed in Strict Rules: "the new chibi must visually rhyme with the existing project chibi roster — same head-body ratio, same body height in cell, same line weight, same shading; STRICT 2.5-head means head approximately 40% of total body height, NOT taller adult-leaning proportions even if the character concept is mature"
4. Confirm with the user: "the project already has N same-category chibi (head-body ratio = ..., body height = ... px in 128 cell). Generate the new one matching this lock? Tell me if you want to deviate."

**Why**: Existing project assets define the visual lock for new ones. Without a concrete chibi `--ref` from the project, mature/elegant character archetypes (aristocrat, sage, refined merchant) reliably drift to 3–3.5 head proportions even when the prompt says "2.5-head" — fix is to pass an existing project chibi frame as `--ref` and write explicit head=40% into Strict Rules.

---

## Batch consistency mode (multiple same-category assets)

**When the user requests 2+ same-category assets in one go** (e.g. 4 hero chibi sprites, 6 chibi monsters, a chibi judge roster), switch into batch mode:

1. **Define a unified spec FIRST** before any generation: art style code, sheet shape, head/body proportion (e.g. STRICT 2.5-head for chibi — head ≈ 40% of total height, body ≥ 1.5× head height), view angle (typically 3/4 from slightly above), lighting direction, **facing direction (left/right)** locked across the entire batch, anchor (bottom for humanoids, center for creatures), pose family.
2. **Distinguish "locked" vs "variable"**: locked = style / 2.5-head proportion / view / facing / sheet shape / anchor; variable = colors / accessories / weapons / FX color / costume detail.
3. **Write the locked rules into the Strict Rules section of EVERY prompt in the batch** — same wording across all assets. Chibi especially needs explicit head-to-body ratio lock (AI tends to enlarge the head and shrink the body) and explicit facing direction lock (AI tends to mirror frames or flip to symmetric front-facing for symmetric costumes).
4. **After generation, verify**: per-asset (check frame 1 — the one used as ICON — before applying) or batch-end (lay all sprites side by side and check uniformity). The confirmation step is mandatory.
5. **Exception**: rarity-tier chibi (R/SR/SSR) — visual gap is the design goal, but **2.5-head proportion must stay unified**; gap goes into accessory density / FX intensity / silhouette complexity, not head ratio.

**Single-asset generation skips this mode** — go straight to the regular workflow.

**Why**: Chibi roster screens (gacha pull lists, hero rosters, monster grids) require strict visual rhyming. Without locking spec into every prompt, AI drifts hard — chibi proportions are especially fragile because reference images are usually in adult proportions. See feedback memory `feedback_same_category_unified_style.md`.

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

**Default art style for this skill: `cel_shaded_chibi`.**

Always include this style block in the prompt unless the user overrides it:

```
Style: anime cel-shaded chibi sprite, 2.5-head proportions, clean bold black outlines,
flat color fills with two-tone shading only (base color + one shadow tone), no gradients,
no painterly brushwork, no soft edges. Reference style: Eversoul / Idle Heroes / Disgaea sprite art.
```

Why this is the default:

- Flat fills + bold outlines = the most stable frame-to-frame consistency on Banana Pro
- Chibi proportions exaggerate poses, so few frames read clearly
- Effects (spells, projectiles, impacts) tend to render as cleanly separated elements, useful for layered animation compositing later
- Industry-standard look for animation-heavy gacha / mobile games (Eversoul, Idle Heroes, Disgaea, AFK Arena)

Only switch art_style when the user explicitly asks for a different look:

- `pixel_art` / `retro_pixel`: redirect the user to the sister skill `generate2dsprite` instead — that one defaults to pixel art.
- `clean_hd`: for map props or hand-painted HD assets matching a map.
- `map_style` or `project-native`: match an existing map, game, or reference instead of cel-shaded chibi.

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

#### 5b. Cross-character proportion QC (batch mode, REQUIRED)

When generating ≥2 characters in the same batch, head-body ratio drift is the #1 silent failure on Banana Pro — boilerplate "2.5-head proportions" alone is NOT enough; mature/elegant character archetypes (aristocrat, sage, refined merchant) consistently get pulled toward 3–3.5 head while playful/young archetypes stay near 2.5.

**Required step** before declaring done:
1. Open frame 1 (idle stance) of every character side by side at the same display size.
2. Eyeball head height ratio between tallest and shortest head — if head height differs by >15%, the batch fails.
3. Optional automated check: measure head bbox per character via PIL alpha (head = top connected component above shoulder) and compare ratios.
4. **Regenerate only the outlier(s)** with a stricter prompt — add to Strict Rules: `"head must be approximately 40% of total chibi body height — explicitly NOT taller / leaner adult proportions; head from chin to crown must be at least as tall as the torso from shoulders to hips"`.

Do not accept "looks roughly OK" — the user reads sprite rosters side by side, and unequal head sizes break the gacha-game-roster feel that's the whole point of chibi.

See feedback memory `feedback_same_category_unified_style.md` for the project-locked principle.

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
- 非 chibi 的一般 sprite（像素／寫實） → 改用 `generate2dsprite`
- 場景／地圖 → `generate2dmap`
- 通用生圖需求 → `imagen`
