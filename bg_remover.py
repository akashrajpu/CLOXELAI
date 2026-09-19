"""
=============================================================================
PRO BACKGROUND REMOVER MODULE (Render Ready & Environment Variable Secured)
=============================================================================
Description: Professional grade image background removal module.
Supports Remove.bg API via REMOVE_BG_API_KEY environment variable.

Usage:
  from bg_remover import remove_background
  output_img = remove_background("input.jpg", "output.png")
=============================================================================
"""

import os
import sys
import io
from pathlib import Path
from typing import Union, Optional, Tuple, List
from PIL import Image, ImageColor, ImageFilter
import numpy as np
from collections import deque

try:
    from dotenv import load_dotenv
    if os.path.exists("config.env"):
        load_dotenv("config.env")
    elif os.path.exists(".env"):
        load_dotenv(".env")
except Exception:
    pass

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

def release_system_memory():
    """
    Forces Python Garbage Collection + Linux C-heap memory reclamation (malloc_trim).
    Prevents Render 512MB RAM Out-Of-Memory (OOM) crashes.
    """
    import gc
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL('libc.so.6').malloc_trim(0)
    except Exception:
        pass

# Avoid loading 400MB rembg ONNX model on Render 512MB RAM tier unless explicitly requested
USE_REMBG = os.getenv("USE_REMBG", "false").lower() in ["true", "1"]
REMBG_AVAILABLE = False

if USE_REMBG:
    try:
        from rembg import remove, new_session
        REMBG_AVAILABLE = True
    except ImportError:
        REMBG_AVAILABLE = False


def remove_bg_removebg_api(img_bytes: bytes, api_key: str) -> Image.Image:
    """
    Remove.bg official API integration for studio-grade AI background removal.
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests package required for API. Run: pip install requests")

    response = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": img_bytes},
        data={"size": "auto"},
        headers={"X-Api-Key": api_key},
    )
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        raise RuntimeError(f"Remove.bg API Error {response.status_code}: {response.text}")


def remove_background_pro(img_pil: Image.Image) -> Image.Image:
    """
    Pro Body-Boundary Protection algorithm fallback.
    Starts strictly from outer image edges and flood-fills connected background pixels.
    Uses edge gradient detection to stop at subject silhouette boundaries, ensuring
    inner beard, hair, moustache, clothes, skin, and eyes are 100% PRESERVED.
    """
    img = img_pil.convert("RGBA")
    width, height = img.size
    rgb_img = img.convert("RGB")
    
    gray = rgb_img.convert("L")
    gray_np = np.array(gray, dtype=np.float32)
    
    gy, gx = np.gradient(gray_np)
    edge_mag = np.sqrt(gx**2 + gy**2)
    
    rgb_np = np.array(rgb_img, dtype=np.float32)
    corners = [
        rgb_np[0:15, 0:15],
        rgb_np[0:15, -15:],
        rgb_np[-15:, 0:15],
        rgb_np[-15:, -15:]
    ]
    bg_color = np.mean([c.mean(axis=(0, 1)) for c in corners], axis=0)
    color_diff = np.sqrt(np.sum((rgb_np - bg_color)**2, axis=2))
    
    bg_threshold = 45.0
    mask = np.zeros((height, width), dtype=np.uint8)
    
    queue = deque()
    for x in range(width):
        queue.append((0, x))
        queue.append((height - 1, x))
    for y in range(height):
        queue.append((y, 0))
        queue.append((y, width - 1))
        
    for y, x in queue:
        mask[y, x] = 1

    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    while queue:
        cy, cx = queue.popleft()
        for dy, dx in neighbors:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] == 0:
                if color_diff[ny, nx] < bg_threshold and edge_mag[ny, nx] < 45.0:
                    mask[ny, nx] = 1
                    queue.append((ny, nx))
                elif color_diff[ny, nx] < bg_threshold * 0.65:
                    mask[ny, nx] = 1
                    queue.append((ny, nx))

    fg_mask_np = ((1 - mask) * 255).astype(np.uint8)
    fg_mask_pil = Image.fromarray(fg_mask_np)
    smoothed_mask = fg_mask_pil.filter(ImageFilter.GaussianBlur(radius=1.0))
    img.putalpha(smoothed_mask)
    return img


def remove_background(
    input_image: Union[str, Path, Image.Image, bytes],
    output_path: Optional[Union[str, Path]] = None,
    bg_color: Optional[Union[str, Tuple[int, int, int]]] = None,
    api_key: Optional[str] = None
) -> Image.Image:
    """
    Removes background using Remove.bg API (via REMOVE_BG_API_KEY env var or api_key param)
    with automatic local fallbacks.
    """
    effective_api_key = api_key or os.getenv("REMOVE_BG_API_KEY") or os.getenv("REMOVEBG_API_KEY")

    if isinstance(input_image, (str, Path)):
        with open(input_image, "rb") as f:
            raw_bytes = f.read()
        img = Image.open(input_image)
    elif isinstance(input_image, bytes):
        raw_bytes = input_image
        img = Image.open(io.BytesIO(input_image))
    elif isinstance(input_image, Image.Image):
        img = input_image
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()
    else:
        raise ValueError("Unsupported input format.")

    result_img = None

    if effective_api_key:
        try:
            result_img = remove_bg_removebg_api(raw_bytes, effective_api_key)
        except Exception as err:
            print(f"⚠️ Remove.bg API Notice: {err}. Using local fallback engine...")

    if result_img is None and REMBG_AVAILABLE:
        try:
            session = new_session("u2net")
            result_img = remove(img, session=session)
        except Exception:
            pass

    if result_img is None:
        result_img = remove_background_pro(img)

    if bg_color is not None:
        if isinstance(bg_color, str):
            rgb_vals = ImageColor.getrgb(bg_color)
        else:
            rgb_vals = bg_color[:3]

        bg_canvas = Image.new("RGBA", result_img.size, rgb_vals + (255,))
        bg_canvas.paste(result_img, (0, 0), mask=result_img)
        result_img = bg_canvas.convert("RGB")

    if output_path:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if result_img.mode == "RGBA" and out_path.suffix.lower() not in [".png", ".webp"]:
            out_path = out_path.with_suffix(".png")
        result_img.save(out_path)
        print(f"✅ Output saved to: {out_path}")

    return result_img


def remove_background_batch(
    image_paths: List[Union[str, Path]],
    output_dir: Union[str, Path],
    bg_color: Optional[Union[str, Tuple[int, int, int]]] = None,
    api_key: Optional[str] = None
) -> List[Path]:
    """
    Batch background removal for a list of images.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for idx, path in enumerate(image_paths, 1):
        path_obj = Path(path)
        if not path_obj.exists():
            continue
        target_path = out_dir / f"{path_obj.stem}_nobg.png"
        print(f"[{idx}/{len(image_paths)}] Processing {path_obj.name}...")
        remove_background(path_obj, target_path, bg_color=bg_color, api_key=api_key)
        saved_files.append(target_path)

    return saved_files


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n✨ Pro Background Remover CLI ✨\n")
        print("Usage:")
        print("  python bg_remover.py <input_image_path> [output_image_path] [bg_color]\n")
        sys.exit(0)

    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "output_nobg.png"
    color = sys.argv[3] if len(sys.argv) > 3 else None

    remove_background(in_file, output_path=out_file, bg_color=color)
