#!/usr/bin/env python3
"""
Nano Banana Pro (gemini-3-pro-image-preview) image generation script.

Usage:
  python generate.py --prompt "..." --output "./output.png"
  python generate.py --prompt "..." --ratio "16:9" --size "2K" --output "./output.png"
  python generate.py --prompt "..." --ref "style.jpg" --ref "char.png" --output "./output.png"
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# === Config ===
MODEL = "gemini-3-pro-image-preview"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# Officially supported values for the Pro image model
# (https://ai.google.dev/gemini-api/docs/image-generation).
VALID_RATIOS = [
    "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
]
VALID_SIZES = ["1K", "2K", "4K"]


def load_api_key() -> str:
    """Load the API key from the environment variable or the skill's .env file."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    # Fall back to the .env file in the skill directory
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                value = line.split("=", 1)[1].strip()
                # Strip matching surrounding single or double quotes
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                    value = value[1:-1]
                return value

    print("ERROR: GEMINI_API_KEY not found. Set the environment variable or add it to the .env file.", file=sys.stderr)
    sys.exit(1)


def encode_image(image_path: str) -> dict:
    """Encode an image file as a base64 inline_data part."""
    path = Path(image_path)
    if not path.exists():
        print(f"ERROR: Reference image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    suffix = path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime_type = mime_map.get(suffix)
    if mime_type is None:
        supported = ", ".join(sorted(mime_map))
        print(
            f"ERROR: Unsupported reference image extension '{suffix}' for {image_path}. "
            f"Supported: {supported}",
            file=sys.stderr,
        )
        sys.exit(1)

    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return {
        "inline_data": {
            "mime_type": mime_type,
            "data": data
        }
    }


def build_request(prompt: str, ratio: str, size: str, ref_images: list[str]) -> dict:
    """Build the API request payload."""
    parts = []

    # Reference images go before the prompt
    for img_path in ref_images:
        parts.append(encode_image(img_path))

    # Text prompt
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": ratio,
                "imageSize": size
            }
        }
    }

    return payload


def call_api(payload: dict, api_key: str) -> dict:
    """Call the Gemini API and return the parsed JSON response."""
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"ERROR: API returned HTTP {e.code}", file=sys.stderr)
        print(error_body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Connection failed - {e.reason}", file=sys.stderr)
        sys.exit(1)


def extract_and_save(response: dict, output_path: str) -> str:
    """Extract images from the response and save them; return the text response (if any)."""
    candidates = response.get("candidates", [])
    if not candidates:
        print("ERROR: No candidates in API response", file=sys.stderr)
        print(json.dumps(response, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    text_response = ""
    image_saved = False
    image_count = 0
    finish_reasons = []

    # The API only ever returns image/jpeg for this model (confirmed against
    # both generateContent and the interactions endpoint); warn when the
    # requested output extension disagrees so downstream chroma-key users
    # know the bytes are JPEG regardless of the file name.
    MIME_EXT = {"image/jpeg": {".jpg", ".jpeg"}, "image/png": {".png"}, "image/webp": {".webp"}}

    for candidate in candidates:
        finish_reasons.append(candidate.get("finishReason", "UNKNOWN"))
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            # Text part
            if "text" in part:
                text_response += part["text"]

            # Image part
            if "inline_data" in part or "inlineData" in part:
                img_data = part.get("inline_data") or part.get("inlineData", {})
                b64_data = img_data.get("data", "")
                if b64_data:
                    image_count += 1
                    if image_count == 1:
                        save_path = output_path
                    else:
                        # Number additional images
                        p = Path(output_path)
                        save_path = str(p.parent / f"{p.stem}_{image_count}{p.suffix}")

                    img_bytes = base64.b64decode(b64_data)
                    Path(save_path).write_bytes(img_bytes)
                    print(f"OK: Image saved to {save_path} ({len(img_bytes)} bytes)")
                    image_saved = True

                    mime = img_data.get("mimeType") or img_data.get("mime_type") or ""
                    ext = Path(save_path).suffix.lower()
                    if mime in MIME_EXT and ext not in MIME_EXT[mime]:
                        print(
                            f"WARNING: API returned {mime} but output file is {ext} — "
                            "bytes are saved as-is (no conversion). This model only "
                            "outputs JPEG; expect chroma-subsampling artifacts on hard "
                            "edges when chroma-keying.",
                            file=sys.stderr,
                        )

    if not image_saved:
        reasons = ", ".join(finish_reasons) or "UNKNOWN"
        print(f"ERROR: No image data in response (finishReason: {reasons})", file=sys.stderr)
        if "IMAGE_RECITATION" in finish_reasons:
            print(
                "HINT: IMAGE_RECITATION means the prompt was too generic/derivative "
                "and the output was withheld. Rephrase with more specific, original "
                "details and retry.",
                file=sys.stderr,
            )
        elif any(r.startswith("SAFETY") or r == "PROHIBITED_CONTENT" for r in finish_reasons):
            print("HINT: blocked by safety filters — adjust the prompt content.", file=sys.stderr)
        print(f"Response: {json.dumps(response, indent=2, ensure_ascii=False)[:2000]}", file=sys.stderr)
        sys.exit(1)

    return text_response


def main() -> None:
    # Windows pipes default to the legacy codepage (e.g. cp950); model text
    # containing emoji or non-Big5 characters would raise UnicodeEncodeError
    # after the image was already saved, turning a success into exit code 1.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Nano Banana Pro image generation")
    parser.add_argument("--prompt", required=True, help="Generation prompt")
    parser.add_argument("--ratio", default="1:1", choices=VALID_RATIOS, help="Aspect ratio (default: 1:1)")
    parser.add_argument("--size", default="1K", choices=VALID_SIZES, help="Image size (default: 1K)")
    parser.add_argument("--output", required=True, help="Output image path")
    parser.add_argument("--ref", action="append", default=[], help="Reference image path (repeatable)")
    args = parser.parse_args()

    # Ensure the output directory exists
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # Load API key
    api_key = load_api_key()

    # Build request
    print(f"Model: {MODEL}")
    print(f"Aspect ratio: {args.ratio} | Size: {args.size}")
    if args.ref:
        print(f"Reference images: {len(args.ref)}")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print("Generating...")

    payload = build_request(args.prompt, args.ratio, args.size, args.ref)
    response = call_api(payload, api_key)

    # Extract and save
    text = extract_and_save(response, args.output)
    if text:
        print(f"\nModel text response: {text}")

    print("\nDone.")


if __name__ == "__main__":
    main()
