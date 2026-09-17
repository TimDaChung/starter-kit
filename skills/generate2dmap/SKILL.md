---
name: generate2dmap
description: "Generate/revise 2D game maps via Nano Banana Pro (imagen/bin/generate.py): RPG maps, tactical arenas, battle backgrounds, side-scrollers, tilemaps, prop packs, collision zones, map previews."
---

# Generate2dmap

> **執行角色：美術**——關注風格一致、可讀性、地圖資產規格（圖層 / 碰撞區 / 尺寸 / 命名）；碰撞與圖層合約切**工程**視角核對。

## Overview

Build the smallest map bundle that satisfies the game. Decide the map as a pipeline, not as a single strategy label:

1. `visual_model`: `baked_raster` | `layered_raster` | `tilemap` | `layered_tilemap` | `parallax_layers`
2. `runtime_object_model`: `none` | `separate_props` | `y_sorted_props` | `interactive_entities` | `foreground_occluders`
3. `collision_model`: `none` | `coarse_shapes` | `precise_shapes` | `tile_collision` | `polygon_walkmesh` | `trigger_zones`
4. `engine_target`: `raw_canvas` | `Phaser` | `Tiled_JSON` | `LDtk` | `Godot_TileMap` | `Unity_Tilemap` | project-native

Use user-specified parameters when present. When the user does not specify them, infer the lightest pipeline from the existing game, camera, collision needs, map scale, and editing needs.

Read [references/map-strategies.md](references/map-strategies.md) when the pipeline choice is not obvious. Read [references/layered-map-contract.md](references/layered-map-contract.md) before implementing a layered raster map. Read [references/prop-pack-contract.md](references/prop-pack-contract.md) before batching generated props into a sheet.

## Consistency rules (read before the first generation)

The lock rules shared by all five image skills live in [`../imagen/references/consistency-rules.md`](../imagen/references/consistency-rules.md) — §1 default visual rules, §2 project asset inheritance, §3 batch consistency mode, §4 hand-off to `art-style-guard`. Summary plus the map-only deltas:

- **Default visual rules (§1)**: map / background full-bleed to all four edges via a positive composition instruction ("scene extends full-bleed to all four edges of canvas" — pure negation can trigger frame design); any character or NPC on the map → refined attractive features (mobile gacha aesthetic), female → fair luminous skin, no western cartoon / Disney / Pixar drift. Explicit user requests override.
- **Project asset inheritance (§2, REQUIRED pre-flight)**: scan `assets/maps/`, `assets/backgrounds/`, `maps/`, `backgrounds/` (maps), `assets/tiles/`, `assets/props/`, `tiles/` (tilesets / props), and `assets/sprites/` (the character sprites that will sit on the map — their scale + style is the lock for prop scale). If same-category map assets exist: LOCK art style, perspective angle, palette family, lighting direction, scale / pixel-density target, atmosphere; pass at least one existing map / prop as `--ref`; embed in Strict Rules "same perspective, same palette family, same lighting direction, same scale; props from this asset must sit on the existing maps without scale or palette clash"; confirm the lock with the user.
- **Batch consistency mode (§3, 2+ same-category map assets — a prop pack of 8 trees, 6 floor-tile variants, a parallax layer set, several battle backgrounds for one biome)**: unified spec first — art style code (`clean_hd` / `pixel_inspired` / project-native), aspect ratio, perspective (top-down / 3/4 isometric / side / parallax depth), lighting direction (sun angle, time of day), **palette family**, scale / pixel-density target, composition rules (e.g. all props centered, all tiles seamless 256×256); locked = style / perspective / palette / scale / lighting, variable = subject (which tree, which prop) / detail composition; identical Strict Rules wording in every prompt; mandatory verification, preferably by assembling the assets onto a test scene and checking the assembled image.
  - Maps especially need explicit **palette + lighting-direction** locks — without them Banana mixes warm / cool atmospheres or lights adjacent props from different angles, which is visible at first glance on a shared scene.
- **Hand-off (§4)**: second batch onward in the same project, or any style doubt → run `art-style-guard` first (Style Bible + contact-sheet QC).

## Image Generation First

This skill is image-generation-first for visual assets. Call `~/.claude/skills/imagen/bin/generate.py` (Nano Banana Pro / gemini-3-pro-image-preview) as the default creative art source for base maps, dressed references, prop sheets, prop sprites, tileset art, parallax layers, battle backgrounds, and other visible map assets. The agent writes the creative prompts itself — scripts never generate creative prompts or procedurally draw final visual art. Scripts may assemble, slice, chroma-key, crop, validate, compose previews, emit JSON metadata, and wire image-generated assets into engine-native files such as Godot `.tscn` scenes.

**Engine routing**: when the personal `image-studio` skill is installed, the GPT line is preferred for all raw art — see `../imagen/references/draw-engines.md` (§3 call contract: aspect ratio goes into the prompt text; §4 failure handling: a batch fails only when 0 images saved, and fallback to `generate.py` happens only after reporting the cause and getting the user's go-ahead). Without it, `generate.py` below applies unchanged.

Only use procedural drawing or scripted placeholder art when the user explicitly asks for placeholders, test fixtures, debug maps, or engine scaffolding without final art. For an engine target such as `Godot_TileMap`, generate or reuse the visual tileset art first, then use scripts/code only to build tile layers, collision, zones, and scene wiring.

### Calling generate.py

```bash
python ~/.claude/skills/imagen/bin/generate.py \
  --prompt "<creative prompt>" \
  --ratio <1:1|16:9|4:3|...> --size <1K|2K|4K> \
  --output <path/to/out.png> \
  [--ref <path>]...
```

Pick `--ratio` from the map shape (battle bg → `16:9`, square arena → `1:1`, top-down RPG → `1:1` or `4:3`). Use `--size 2K` for production maps, `1K` for fast iterations and prop packs. Banana embeds each `--ref` as inline_data; pass the file path, not just the description.

## Parameter Contract

User-facing parameters may be stated in natural language:

- `map_kind`: overworld | town | dungeon | shrine | arena | battle_bg | side_scroller | tactical
- `visual_model`: baked raster | layered raster | tilemap | layered tilemap | parallax
- `size`: pixel dimensions, tile dimensions, or camera-relative size
- `perspective`: top-down | 3/4 top-down | side-view | isometric-like
- `art_style`: clean_hd | pixel_inspired | retro_pixel | project-native
- `visual_asset_source`: banana_pro | existing_assets | procedural_placeholder
- `collision_precision`: none | coarse | precise | tile | walkmesh
- `prop_generation`: none | one_by_one | prop_pack_2x2 | prop_pack_3x3 | prop_pack_4x4
- `output_format`: PNG only | layered preview | manifest JSON | engine-native map data

When unspecified:

- Use `banana_pro` as the visual asset source.
- Use `baked_raster + coarse_shapes` for battle backgrounds, title/menu scenes, cutscenes, and fixed arenas.
- Use `layered_raster + y_sorted_props + precise_shapes` for top-down RPG exploration with tall props, occlusion, interactables, or reusable props.
- Use `tilemap` or `layered_tilemap` only when the engine/editor already uses tiles or the user asks for editable tiles.
- Use `parallax_layers` for side-scrollers and scrolling backgrounds.
- Use prop packs when 4 or more small/medium static props share one style and can fit into equal cells.
- Use one-by-one prop generation for hero props, buildings, gates, irregular large props, animated props, or props needing strong identity.
- Use `clean_hd` for generated exploration maps unless the project or user asks for pixel art. This means clean hand-painted top-down 2D RPG game map, HD game asset style, sharp readable terrain shapes, low texture noise, and no chunky pixels.
- Use `pixel_inspired` only when the user wants a pixel-adjacent look without retro chunkiness.
- Use `retro_pixel` only when the user explicitly asks for 16-bit, retro JRPG, or classic pixel-art maps.

## Workflow

1. Inspect the target game.
   - Find camera size, map dimensions, coordinate system, render order, asset loading, collision support, zone data, and existing map formats.
   - Preserve the engine's existing style and data contracts.

2. Choose the pipeline axes.
   - Select `visual_model`, `runtime_object_model`, `collision_model`, and `engine_target`.
   - Select `art_style`. Prefer readable gameplay shapes over decorative texture density.
   - Select `visual_asset_source`. Default to `banana_pro`; use `existing_assets` only when the project already has suitable art; use `procedural_placeholder` only when explicitly requested.
   - Treat `hybrid` as a result of combining axes, not as a primary category.

3. Produce assets (creative prompts written by hand, art from `generate.py` — see Image Generation First).
   - For baked raster maps, generate one background, or edit/use an existing image when supplied, then add optional collision/zones metadata.
   - For layered raster maps, follow the reference pipeline in Prop Generation Rules (ground-only base → dressed reference from the visible base → props → placement).
   - For tilemaps, generate or reuse tileset art first, then follow the engine/editor format for layers, objects, collision, and scene files. Do not script-draw the tileset as the final art source.
   - For parallax scenes, generate background/midground/foreground visual layers first, then produce scroll metadata.

4. Build metadata.
   - Store prop placement, actor spawn points, interactables, blockers, walk bounds, encounter zones, exits, and triggers as structured data.
   - Keep collision independent from pixels unless the target engine explicitly uses tile collision.

5. Validate and preview.
   - Compose a flattened preview for layered maps, then run the Validation checklist below.

## Prop Generation Rules

Use `generate2dsprite` for reusable transparent props, but the agent must write the prop prompt itself using the selected map `art_style` (wording per style: see Parameter Contract defaults; for `clean_hd` explicitly forbid pixel art).

Choose the generation shape deliberately:

- `one_by_one`: safest for large, important, animated, or irregular props.
- `prop_pack_2x2`: 4 related props, safest batch size.
- `prop_pack_3x3`: 9 small/medium props, good quality/time tradeoff.
- `prop_pack_4x4`: 16 very simple small props; fastest but most likely to drift or touch edges.

Prop packs save image-generation calls and prompt overhead, but reduce per-prop control. Use them for rocks, shrubs, barrels, small signs, lamps, crates, floor ornaments, plants, and repeated environmental props. Do not use prop packs for buildings, gates, trees with wide canopies, character-like statues, hero objects, or anything that must be pixel-perfect.

For layered maps with generated props, prefer this reference pipeline:

1. Generate `assets/map/<name>-base.png` as ground-only terrain.
2. Make the base image visible in conversation context. Use the Read tool on the local PNG so you can see it, then pass the same path to `~/.claude/skills/imagen/bin/generate.py` via `--ref`. Do not rely on a path string inside the text prompt as the reference.
3. Generate `assets/map/<name>-dressed-reference.png` from the visible base, preserving camera, terrain, size, road/water shapes, anchor pads, and boundaries. Treat this as a planning/reference image, not the final runtime map.
4. Generate one-by-one props or a prop pack based on the dressed reference.
5. Place extracted props over the original base and compose a flattened preview.
6. Validate that base, dressed reference, and preview dimensions match.

Use `~/.claude/skills/generate2dmap/scripts/extract_prop_pack.py` after generating a solid-magenta prop sheet. If the sheet has antialiased magenta fringe, see [prop-pack-contract.md](references/prop-pack-contract.md) Extraction for the three Claude Code alternatives. Use `~/.claude/skills/generate2dmap/scripts/compose_layered_preview.py` to verify placement over the base map.

## Expected Deliverables

For a baked raster map:

- `assets/map/<name>.png`
- optional `<name>.prompt.txt`
- optional `data/<name>-collision.json` or `data/<name>-zones.json`
- code changes that load/use the image

For a layered raster map:

- `assets/map/<name>-base.png`
- `assets/map/<name>-base.prompt.txt`
- optional `assets/map/<name>-dressed-reference.png` for prop planning
- `assets/props/<prop>/prop.png` folders, from one-by-one props or extracted prop packs
- `data/<name>-props.json` placement metadata
- `data/<name>-collision.json` and/or `data/<name>-zones.json` when gameplay needs them
- `assets/map/<name>-layered-preview.png`
- code changes that load the base, props, y-sorted renderables, collision, and zones

For a tilemap or layered tilemap:

- image-generated or user-supplied `assets/tilesets/<name>.png`
- optional tile slicing/atlas metadata
- engine-native tile layer data such as Tiled JSON, LDtk data, Godot TileMap scene data, Unity tile placement data, or project-native JSON
- object layers for spawns, exits, interactables, blockers, and zones
- a flattened preview assembled from the visual tileset and layer data
- no script-drawn final tileset art unless the user explicitly asked for procedural placeholders

For a prop pack:

- raw generated sheet with solid `#FF00FF` background
- extracted `assets/props/<prop>/prop.png` files
- `prop-pack.json` extraction manifest
- no `edge_touch` entries for accepted props

## Validation

Always validate what the chosen pipeline requires:

- map files exist and have expected dimensions
- transparent props contain alpha
- prop pack manifests parse and accepted props do not touch cell edges
- placement JSON parses and referenced prop files exist
- collision/zones JSON parses when present
- critical spawn, path, entrance, blocker, and zone points behave as expected
- flattened preview looks coherent at the game's camera size

## 銜接

- 想還原某張參考地圖／場景的風格 → 先用 `image-to-prompt` 逆向出中性 prompt 再回來生
- 地圖上的角色／道具 sprite → `generate2dsprite`
- 通用生圖需求 → `imagen`
- 第二批以後的同專案生圖 / 風格疑慮 → 先過 `art-style-guard`
