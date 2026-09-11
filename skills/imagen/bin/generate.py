#!/usr/bin/env python3
"""
Nano Banana Pro (gemini-3-pro-image-preview) 圖片生成腳本
用法：
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

# === 設定 ===
MODEL = "gemini-3-pro-image-preview"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

VALID_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1",
    "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9"
]
VALID_SIZES = ["512", "1K", "2K", "4K"]


def load_api_key():
    """從環境變數或 .env 檔案讀取 API Key"""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    # 嘗試從 skill 目錄的 .env 讀取
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()

    print("ERROR: 找不到 GEMINI_API_KEY。請設定環境變數或在 .env 檔案中提供。", file=sys.stderr)
    sys.exit(1)


def encode_image(image_path: str) -> dict:
    """將圖片檔案轉為 base64 inline_data"""
    path = Path(image_path)
    if not path.exists():
        print(f"ERROR: 找不到參考圖: {image_path}", file=sys.stderr)
        sys.exit(1)

    suffix = path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime_type = mime_map.get(suffix, "image/png")

    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return {
        "inline_data": {
            "mime_type": mime_type,
            "data": data
        }
    }


def build_request(prompt: str, ratio: str, size: str, ref_images: list) -> dict:
    """組裝 API 請求 payload"""
    parts = []

    # 加入參考圖（放在 prompt 之前）
    for img_path in ref_images:
        parts.append(encode_image(img_path))

    # 加入文字 prompt
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
    """呼叫 Gemini API"""
    url = f"{ENDPOINT}?key={api_key}"
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"ERROR: API 回傳 {e.code}", file=sys.stderr)
        print(error_body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: 連線失敗 - {e.reason}", file=sys.stderr)
        sys.exit(1)


def extract_and_save(response: dict, output_path: str) -> str:
    """從回應中提取圖片並儲存，回傳文字回應（如有）"""
    candidates = response.get("candidates", [])
    if not candidates:
        print("ERROR: API 回應中沒有 candidates", file=sys.stderr)
        print(json.dumps(response, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    text_response = ""
    image_saved = False
    image_count = 0

    for candidate in candidates:
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            # 文字部分
            if "text" in part:
                text_response += part["text"]

            # 圖片部分
            if "inline_data" in part or "inlineData" in part:
                img_data = part.get("inline_data") or part.get("inlineData", {})
                b64_data = img_data.get("data", "")
                if b64_data:
                    image_count += 1
                    if image_count == 1:
                        save_path = output_path
                    else:
                        # 多張圖時加編號
                        p = Path(output_path)
                        save_path = str(p.parent / f"{p.stem}_{image_count}{p.suffix}")

                    img_bytes = base64.b64decode(b64_data)
                    Path(save_path).write_bytes(img_bytes)
                    print(f"OK: 圖片已儲存至 {save_path} ({len(img_bytes)} bytes)")
                    image_saved = True

    if not image_saved:
        print("WARNING: 回應中沒有找到圖片資料", file=sys.stderr)
        print(f"回應內容: {json.dumps(response, indent=2, ensure_ascii=False)[:2000]}", file=sys.stderr)

    return text_response


def main():
    parser = argparse.ArgumentParser(description="Nano Banana Pro 圖片生成")
    parser.add_argument("--prompt", required=True, help="生成 prompt")
    parser.add_argument("--ratio", default="1:1", choices=VALID_RATIOS, help="長寬比 (預設: 1:1)")
    parser.add_argument("--size", default="1K", choices=VALID_SIZES, help="解析度 (預設: 1K)")
    parser.add_argument("--output", required=True, help="輸出圖片路徑")
    parser.add_argument("--ref", action="append", default=[], help="參考圖路徑（可多次指定）")
    args = parser.parse_args()

    # 驗證
    if args.ratio not in VALID_RATIOS:
        print(f"ERROR: 不支援的長寬比 {args.ratio}，可用: {', '.join(VALID_RATIOS)}", file=sys.stderr)
        sys.exit(1)

    # 確保輸出目錄存在
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # 載入 API Key
    api_key = load_api_key()

    # 組裝請求
    print(f"模型: {MODEL}")
    print(f"長寬比: {args.ratio} | 解析度: {args.size}")
    if args.ref:
        print(f"參考圖: {len(args.ref)} 張")
    print(f"Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print("生成中...")

    payload = build_request(args.prompt, args.ratio, args.size, args.ref)
    response = call_api(payload, api_key)

    # 提取並儲存
    text = extract_and_save(response, args.output)
    if text:
        print(f"\n模型回應文字: {text}")

    print("\n完成！")


if __name__ == "__main__":
    main()
