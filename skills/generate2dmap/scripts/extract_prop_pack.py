#!/usr/bin/env python3
"""Extract transparent map props from a solid-magenta prop-pack sheet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from PIL import Image

_SKILLS_ROOT = Path(__file__).resolve().parents[2]
for _candidate in (_SKILLS_ROOT / "imagen" / "bin", Path.home() / ".claude" / "skills" / "imagen" / "bin"):
    if (_candidate / "chroma_tools.py").exists():
        sys.path.insert(0, str(_candidate))
        break
try:
    from chroma_tools import (
        BBox,
        Component,
        bbox_touches_edge,
        clean_edges,
        connected_components,
        pad_bbox,
        remove_bg_magenta,
        sanitize_slug,
        trim_border,
    )
except ImportError as exc:
    raise ImportError(
        "chroma_tools.py not found. Install the imagen skill from the starter kit "
        "(expected at skills/imagen/bin/ next to this skill, or ~/.claude/skills/imagen/bin/)."
    ) from exc


def parse_labels(args: argparse.Namespace, expected_count: int) -> list[str]:
    labels: list[str] = []
    if args.labels:
        labels = [item.strip() for item in args.labels.split(",")]
    if args.labels_file:
        labels = [
            line.strip()
            for line in args.labels_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    if not labels:
        labels = [f"prop-{index + 1}" for index in range(expected_count)]
    if len(labels) > expected_count:
        raise ValueError(f"Got {len(labels)} labels for {expected_count} cells.")
    labels.extend(f"prop-{index + 1}" for index in range(len(labels), expected_count))
    return [
        sanitize_slug(label, fallback="prop") if label.lower() not in {"empty", "skip", "-"} else ""
        for label in labels
    ]


def alpha_bbox(img: Image.Image) -> BBox | None:
    return img.getchannel("A").getbbox()


def mask_to_component(img: Image.Image, component: Component) -> Image.Image:
    """Return a copy of ``img`` containing only the pixels of ``component``."""
    if component.coords is None:
        raise ValueError("Component has no coords; call connected_components(keep_coords=True).")
    selected = Image.new("RGBA", img.size, (0, 0, 0, 0))
    src = img.load()
    dst = selected.load()
    for x, y in component.coords:
        dst[x, y] = src[x, y]
    return selected


def extract_cell(
    cell: Image.Image,
    args: argparse.Namespace,
) -> tuple[Image.Image | None, dict[str, object]]:
    frame = trim_border(cell, args.trim_border)
    frame = clean_edges(frame, args.edge_clean_depth)
    components = connected_components(frame, args.min_component_area, keep_coords=True)
    selected_component: Component | None = None
    bbox = alpha_bbox(frame)

    if args.component_mode == "largest" and components:
        selected_component = components[0]
        frame = mask_to_component(frame, selected_component)
        bbox = selected_component.bbox
    elif components:
        bbox = alpha_bbox(frame)

    padded_bbox = pad_bbox(bbox, args.component_padding, frame.width, frame.height) if bbox else None
    edge_touch = bbox_touches_edge(bbox, frame.width, frame.height, args.edge_touch_margin)
    prop = frame.crop(padded_bbox) if padded_bbox else None

    return prop, {
        "component_mode": args.component_mode,
        "component_count": len(components),
        "selected_component_area": selected_component.area if selected_component else None,
        "selected_component_bbox": list(selected_component.bbox) if selected_component else None,
        "crop_bbox": list(bbox) if bbox else None,
        "padded_crop_bbox": list(padded_bbox) if padded_bbox else None,
        "edge_touch": edge_touch,
        "output_size": list(prop.size) if prop else [0, 0],
    }


def iter_cells(img: Image.Image, rows: int, cols: int) -> Iterable[tuple[int, int, BBox, Image.Image]]:
    width, height = img.size
    cell_width = width // cols
    cell_height = height // rows
    for row in range(rows):
        for col in range(cols):
            box = (col * cell_width, row * cell_height, (col + 1) * cell_width, (row + 1) * cell_height)
            yield row, col, box, img.crop(box)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--rows", required=True, type=int)
    parser.add_argument("--cols", required=True, type=int)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--labels", help="Comma-separated labels in row-major order.")
    parser.add_argument("--labels-file", type=Path)
    parser.add_argument("--threshold", type=int, default=100)
    parser.add_argument("--edge-threshold", type=int, default=150)
    parser.add_argument("--trim-border", type=int, default=4)
    parser.add_argument("--edge-clean-depth", type=int, default=2)
    parser.add_argument("--component-mode", choices=["all", "largest"], default="largest")
    parser.add_argument("--component-padding", type=int, default=8)
    parser.add_argument("--min-component-area", type=int, default=100)
    parser.add_argument("--edge-touch-margin", type=int, default=0)
    parser.add_argument("--reject-edge-touch", action="store_true")
    parser.add_argument("--keep-empty", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    expected_count = args.rows * args.cols
    labels = parse_labels(args, expected_count)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    raw = Image.open(args.input).convert("RGBA")
    cleaned = remove_bg_magenta(raw, args.threshold, args.edge_threshold)
    manifest_path = args.manifest or (args.output_dir / "prop-pack.json")
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []

    for index, (row, col, source_box, cell) in enumerate(iter_cells(cleaned, args.rows, args.cols)):
        label = labels[index]
        cell_info: dict[str, object] = {
            "index": index,
            "label": label,
            "grid": [row, col],
            "source_box": list(source_box),
        }
        if not label:
            cell_info["status"] = "skipped-label"
            rejected.append(cell_info)
            continue

        prop, info = extract_cell(cell, args)
        cell_info.update(info)

        if prop is None:
            cell_info["status"] = "empty"
            if args.keep_empty:
                prop = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            else:
                rejected.append(cell_info)
                continue

        prop_dir = args.output_dir / label
        prop_dir.mkdir(parents=True, exist_ok=True)
        prop_path = prop_dir / "prop.png"
        prop.save(prop_path)
        cell_info["status"] = "accepted"
        cell_info["image"] = str(prop_path)
        accepted.append(cell_info)

    edge_touch_props = [item["label"] for item in accepted if bool(item.get("edge_touch"))]
    manifest = {
        "input": str(args.input),
        "rows": args.rows,
        "cols": args.cols,
        "threshold": args.threshold,
        "edge_threshold": args.edge_threshold,
        "component_mode": args.component_mode,
        "component_padding": args.component_padding,
        "min_component_area": args.min_component_area,
        "edge_touch_margin": args.edge_touch_margin,
        "accepted": accepted,
        "rejected": rejected,
        "edge_touch_props": edge_touch_props,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if args.reject_edge_touch and edge_touch_props:
        raise ValueError(f"Accepted props touch a cell edge: {edge_touch_props}")

    print(str(manifest_path.resolve()))


if __name__ == "__main__":
    main()
