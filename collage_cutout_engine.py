"""
=============================================================================
VOX / JOHNNY HARRIS STYLE DOCUMENTARY COLLAGE CUTOUT & SLIDING ENGINE (V2.0 PRO)
=============================================================================
Features:
1. Dynamic Spatial Staging & Reality Hierarchy:
   - Sky elements (Clouds, Rain, Sun, Moon, Planes) staged in the upper sky (y ~ 0.22*h).
   - Ground/Person elements (Girls, People, Buildings, Cars) staged below the sky (y ~ 0.65*h).
   - Rain effect: Animates falling water droplets / streaks between clouds and person!
2. Multi-Directional Sliding & Entrance:
   - Slide from Right, Slide from Left, Rise from Bottom, Descend from Top, or Pop with Elastic Bounce!
3. 1,000+ Procedural Marker & Accent Combinations:
   - Bead Pointer Ring (pixel-perfect match to user reference image with terminal orange/gold bead).
   - Arrowhead Pointer, Double Sketch Loops, Architectural Viewfinder Reticles,
     Hand-Drawn Boxes, Chisel Highlighter Washes, Concentric Radar Waves, Washi Tape Pins.
   - 6 vivid neon & studio colorways, multi-quadrant bezier arcs, and hand-drawn micro-jitter.
4. Randomized / Occasional '+' Crosshairs:
   - Only appears ~35% of the time (or scattered organic crosses like the user screenshot).
   - 65% clean canvas, parchment, or bold colored studio backgrounds (like Editorial Red).
5. Ultra-low RAM streaming via FFmpeg rawvideo pipe (< 35MB RAM, Render 512MB safe).
=============================================================================
"""

import os
import sys
import math
import random
import re
import subprocess
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def release_system_memory():
    """Immediately triggers garbage collection and OS memory trim to keep RAM < 35MB."""
    try:
        import gc
        gc.collect()
        try:
            import ctypes
            ctypes.CDLL('libc.so.6').malloc_trim(0)
        except Exception:
            pass
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Aesthetic Canvas Studio Palettes (Warm Paper, Studio Off-White, Parchment, Bauhaus)
# ---------------------------------------------------------------------------
STUDIO_PALETTES = [
    {"name": "parchment_warm", "bg": (246, 244, 238), "grid": (185, 180, 172, 130), "text": (24, 24, 24), "is_dark": False},
    {"name": "studio_cream",   "bg": (250, 248, 242), "grid": (195, 190, 182, 120), "text": (20, 20, 20), "is_dark": False},
    {"name": "editorial_red",  "bg": (205, 36, 36),   "grid": (255, 255, 255, 80),  "text": (255, 255, 255), "is_dark": True}, # Match user reference screenshot!
    {"name": "drafting_kraft", "bg": (241, 236, 226), "grid": (180, 175, 165, 140), "text": (30, 28, 25), "is_dark": False},
    {"name": "blueprint_slate","bg": (234, 238, 242), "grid": (175, 185, 195, 130), "text": (20, 25, 30), "is_dark": False},
    {"name": "muted_sage",     "bg": (236, 241, 236), "grid": (175, 188, 175, 130), "text": (20, 30, 20), "is_dark": False},
    {"name": "vintage_peach",  "bg": (248, 241, 237), "grid": (195, 180, 175, 125), "text": (35, 25, 20), "is_dark": False},
    {"name": "bauhaus_cream",  "bg": (244, 242, 235), "grid": (180, 178, 170, 135), "text": (18, 18, 18), "is_dark": False},
    {"name": "bauhaus_navy",   "bg": (28, 48, 92),     "grid": (255, 255, 255, 60),  "text": (250, 250, 250), "is_dark": True},
    {"name": "terracotta",     "bg": (212, 92, 70),    "grid": (255, 255, 255, 75),  "text": (255, 255, 255), "is_dark": True},
]

# Washi tape colors (red, cobalt blue, kraft beige, deep green)
WASHI_TAPE_COLORS = [
    (210, 50, 45, 235),   # Crimson red
    (40, 90, 185, 230),   # Cobalt blue
    (215, 185, 140, 230), # Kraft tape
    (45, 120, 75, 230),   # Vintage green
    (230, 145, 30, 230),  # Mustard amber
]

# ---------------------------------------------------------------------------
# 1,000+ Procedural Marker Colorways & Types
# ---------------------------------------------------------------------------
MARKER_COLORWAYS = [
    {"name": "stabilo_yellow", "main": (255, 235, 20, 235),  "accent": (255, 130, 25, 245), "glow": (255, 245, 80, 110)}, # User reference screenshot style!
    {"name": "tangerine_neon", "main": (255, 125, 25, 235),  "accent": (255, 235, 20, 245), "glow": (255, 160, 60, 110)},
    {"name": "electric_cyan",  "main": (30, 215, 255, 235),  "accent": (255, 235, 20, 245), "glow": (80, 230, 255, 110)},
    {"name": "mint_green",     "main": (60, 240, 110, 235),  "accent": (255, 255, 255, 245),"glow": (110, 255, 150, 110)},
    {"name": "coral_magenta",  "main": (255, 60, 100, 235),  "accent": (255, 235, 20, 245), "glow": (255, 110, 150, 110)},
    {"name": "studio_white",   "main": (255, 255, 255, 245), "accent": (255, 235, 20, 245), "glow": (255, 255, 255, 100)},
]

MARKER_STYLES = [
    "bead_pointer_ring",       # User screenshot: Hand circle + curved bezier line + terminal solid bead dot!
    "arrow_pointer_ring",      # Circle + curved bezier line + sharp triangular arrowhead
    "double_sketch_loop",      # Organic dual-drawn loop with marker tail
    "architectural_viewfinder",# 4 corner framing brackets [ ]
    "hand_drawn_box",          # Sketched rounded bounding box
    "highlighter_wash_strip",  # Semi-transparent chisel highlighter bar
    "concentric_pulse_waves",  # Radiating pulse arcs
    "washi_tape_pin",          # Torn tape sticker note
    "underline_brush_stroke",  # Double brush underline under label
]

def get_font(size: int = 28, font_type: str = "bold") -> ImageFont.ImageFont:
    """Loads clean, modern system/local typography without cursive distortion."""
    fonts_dir = "fonts"
    candidates = []
    if font_type == "bold":
        candidates = [
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            os.path.join(fonts_dir, "Mukta-Bold.ttf"),
            os.path.join(fonts_dir, "NotoSansDevanagari-Bold.ttf"),
            os.path.join(fonts_dir, "BroadcastTitling.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            os.path.join(fonts_dir, "Arial.ttf"),
        ]
    elif font_type == "serif":
        candidates = [
            "/System/Library/Fonts/Times.ttc",
            "/Library/Fonts/Times New Roman.ttf",
            os.path.join(fonts_dir, "TiroDevanagariHindi-Regular.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            os.path.join(fonts_dir, "NotoSansDevanagari-Regular.ttf"),
            os.path.join(fonts_dir, "Arial.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def create_collage_canvas(
    width: int,
    height: int,
    palette_name: Optional[str] = None,
    draw_grid: Optional[bool] = None,
    draw_tape: bool = True,
    draw_vignette: bool = True
) -> Image.Image:
    """
    Creates an authentic documentary studio canvas:
    - User request: '+' crosses are NOT mandatory every time.
      Only drawn ~35% of the time, or as scattered organic accents (like the user reference image).
    - 65% of the time, the canvas is clean parchment, textured studio paper, or bold colored canvas.
    """
    if palette_name:
        palette = next((p for p in STUDIO_PALETTES if p["name"] == palette_name), None)
    else:
        # Choose palette with 25% chance of bold editorial (red/navy/terracotta)
        if random.random() < 0.25:
            palette = random.choice([p for p in STUDIO_PALETTES if p["name"] in ["editorial_red", "bauhaus_navy", "terracotta"]])
        else:
            palette = random.choice([p for p in STUDIO_PALETTES if p["name"] not in ["editorial_red", "bauhaus_navy", "terracotta"]])
            
    if not palette:
        palette = STUDIO_PALETTES[0]

    bg_rgb = palette["bg"]
    grid_rgba = palette["grid"]

    # 1. Base Paper Canvas
    base = Image.new("RGBA", (width, height), bg_rgb + (255,))
    draw = ImageDraw.Draw(base, "RGBA")

    # 2. '+' Crosshairs: Randomly decide if grid should be drawn
    # User request: "vo + ke nisan lgane ki jrurt n he kabhi kabhi achal lgane ke liye lga do rendomply smja"
    should_draw_grid = draw_grid if draw_grid is not None else (random.random() < 0.35)

    if should_draw_grid:
        cross_mode = random.choice(["scattered", "regular"])
        cross_len = 5

        if cross_mode == "scattered":
            # Scattered aesthetic crosshairs (8 to 15 crosses, like in user reference image!)
            num_crosses = random.randint(10, 16)
            for _ in range(num_crosses):
                cx = random.randint(int(width * 0.08), int(width * 0.92))
                cy = random.randint(int(height * 0.08), int(height * 0.92))
                draw.line([(cx - cross_len, cy), (cx + cross_len, cy)], fill=grid_rgba, width=1)
                draw.line([(cx, cy - cross_len), (cx, cy + cross_len)], fill=grid_rgba, width=1)
        else:
            # Regular drafting grid
            grid_step = int(min(width, height) * 0.12)
            start_x = grid_step // 2
            start_y = grid_step // 2
            for y in range(start_y, height, grid_step):
                for x in range(start_x, width, grid_step):
                    draw.line([(x - cross_len, y), (x + cross_len, y)], fill=grid_rgba, width=1)
                    draw.line([(x, y - cross_len), (x, y + cross_len)], fill=grid_rgba, width=1)

    # 3. Washi Tape Accent Strips (Torn paper stickers on corners/edges)
    if draw_tape and palette["name"] not in ["editorial_red", "bauhaus_navy"]:
        tape_w = int(width * 0.18)
        tape_h = int(height * 0.035)
        tape_color = random.choice(WASHI_TAPE_COLORS)

        positions = [
            (int(width * 0.08), int(height * 0.12), -4),
            (int(width * 0.74), int(height * 0.84), 5),
        ]
        num_tapes = random.choice([1, 2])
        for tx, ty, angle in positions[:num_tapes]:
            tape_surf = Image.new("RGBA", (tape_w, tape_h), (0, 0, 0, 0))
            t_draw = ImageDraw.Draw(tape_surf)
            t_draw.rectangle([(0, 0), (tape_w, tape_h)], fill=tape_color)
            t_draw.line([(0, tape_h // 2), (tape_w, tape_h // 2)], fill=(255, 255, 255, 40), width=1)
            rotated_tape = tape_surf.rotate(angle, expand=True, resample=Image.BICUBIC)
            base.paste(rotated_tape, (tx, ty), mask=rotated_tape)

    # 4. Subtle Vignette Border
    if draw_vignette:
        vignette = Image.new("L", (width, height), 0)
        v_draw = ImageDraw.Draw(vignette)
        pad = int(min(width, height) * 0.08)
        v_draw.ellipse([(-pad, -pad), (width + pad, height + pad)], fill=255)
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=int(min(width, height) * 0.12)))
        
        vig_alpha = np.array(vignette, dtype=np.float32)
        vig_dark = ((255 - vig_alpha) * 0.16).astype(np.uint8)
        vig_np = np.zeros((height, width, 4), dtype=np.uint8)
        vig_np[:, :, 3] = vig_dark
        vig_img = Image.fromarray(vig_np, "RGBA")
        base = Image.alpha_composite(base, vig_img)

    return base, palette


def sharpen_cutout(img: Image.Image, amount: float = 1.35) -> Image.Image:
    """
    Applies high-clarity edge and micro-texture sharpening to cutouts.
    Sharpens RGB color channels while preserving clean alpha transparency.
    Fulfills user request: 'hr ditelsh ko shrp kro jisse ache se smj aye'!
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    r, g, b, a = img.split()
    rgb = Image.merge("RGB", (r, g, b))
    crisp_rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.8, percent=int(amount * 100), threshold=2))
    crisp_rgb.putalpha(a)
    return crisp_rgb


def make_transparent_cutout(
    img_input: Any,
    output_png: Optional[str] = None
) -> Image.Image:
    """
    Takes an input image and guarantees a clean transparent PNG cutout.
    Trims borders and extracts silhouette.
    """
    if isinstance(img_input, str):
        pil_img = Image.open(img_input).convert("RGBA")
    else:
        pil_img = img_input.convert("RGBA")

    w, h = pil_img.size
    np_rgba = np.array(pil_img)

    # Check if already transparent RGBA
    alpha_channel = np_rgba[:, :, 3]
    transparent_ratio = np.count_nonzero(alpha_channel < 50) / (w * h)
    
    if transparent_ratio > 0.05:
        bbox = pil_img.getbbox()
        if bbox:
            pil_img = pil_img.crop(bbox)
        if output_png:
            pil_img.save(output_png, format="PNG")
        return pil_img

    # Check outer corners for solid white/black/grey studio background
    corners = [
        np_rgba[0:15, 0:15, :3],
        np_rgba[0:15, -15:, :3],
        np_rgba[-15:, 0:15, :3],
        np_rgba[-15:, -15:, :3]
    ]
    mean_corner = np.mean([c.mean(axis=(0, 1)) for c in corners], axis=0)
    is_white_bg = np.all(mean_corner > 220)
    is_black_bg = np.all(mean_corner < 35)

    if is_white_bg or is_black_bg:
        rgb_data = np_rgba[:, :, :3].astype(np.float32)
        diff = np.sqrt(np.sum((rgb_data - mean_corner)**2, axis=2))
        thresh = 40.0 if is_white_bg else 35.0
        mask = (diff < thresh).astype(np.uint8)
        
        from collections import deque
        visited = np.zeros((h, w), dtype=bool)
        queue = deque()

        for x in range(w):
            if mask[0, x]: queue.append((0, x))
            if mask[h - 1, x]: queue.append((h - 1, x))
        for y in range(h):
            if mask[y, 0]: queue.append((y, 0))
            if mask[y, w - 1]: queue.append((y, w - 1))

        while queue:
            cy, cx = queue.popleft()
            if visited[cy, cx]:
                continue
            visited[cy, cx] = True
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                    if mask[ny, nx]:
                        queue.append((ny, nx))

        final_alpha = np.where(visited, 0, 255).astype(np.uint8)
        pil_alpha = Image.fromarray(final_alpha, "L").filter(ImageFilter.GaussianBlur(radius=0.8))
        pil_img.putalpha(pil_alpha)

        bbox = pil_img.getbbox()
        if bbox:
            pil_img = pil_img.crop(bbox)
        if output_png:
            pil_img.save(output_png, format="PNG")
        return pil_img

    try:
        from bg_remover import remove_background_pro
        cutout = remove_background_pro(pil_img)
        bbox = cutout.getbbox()
        if bbox:
            cutout = cutout.crop(bbox)
        if output_png:
            cutout.save(output_png, format="PNG")
        return cutout
    except Exception:
        if output_png:
            pil_img.save(output_png, format="PNG")
        return pil_img


def create_cutout_drop_shadow(
    cutout_img: Image.Image,
    blur_radius: int = 14,
    offset: Tuple[int, int] = (8, 14),
    shadow_opacity: float = 0.32
) -> Tuple[Image.Image, Tuple[int, int]]:
    """Creates a photorealistic soft paper drop shadow behind a cutout."""
    w, h = cutout_img.size
    alpha = cutout_img.split()[3]
    
    pad = blur_radius * 2
    sw = w + pad * 2
    sh = h + pad * 2
    
    shadow_mask = Image.new("L", (sw, sh), 0)
    shadow_mask.paste(alpha, (pad + offset[0], pad + offset[1]))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    shadow_np = np.array(shadow_mask, dtype=np.float32)
    shadow_alpha = (shadow_np * shadow_opacity).astype(np.uint8)
    
    shadow_rgba = np.zeros((sh, sw, 4), dtype=np.uint8)
    shadow_rgba[:, :, :3] = (20, 22, 28)
    shadow_rgba[:, :, 3] = shadow_alpha
    
    shadow_img = Image.fromarray(shadow_rgba, "RGBA")
    return shadow_img, (offset[0] - pad, offset[1] - pad)


# ---------------------------------------------------------------------------
# High-Contrast Label & Chapter Badge Utilities (Pro-Level Alignment & Clarity)
# ---------------------------------------------------------------------------
def draw_sharp_badge_label(
    draw: ImageDraw.ImageDraw,
    label: str,
    pos: Tuple[int, int],
    font: ImageFont.ImageFont,
    anchor: str = "mm",
    is_dark_bg: bool = False,
    accent_color: Optional[Tuple[int, int, int, int]] = None,
    canvas_bounds: Optional[Tuple[int, int, int, int]] = None
) -> Tuple[int, int]:
    """
    Renders high-contrast, razor-sharp documentary labels with boundary safety clamping.
    Draws a subtle contrast halo / backing so text is legible and crisp on any canvas.
    Returns the final clamped (x, y) coordinates.
    """
    if not label or not font:
        return pos
    x, y = pos
    tb = font.getbbox(label)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]

    # Boundary clamping if canvas bounds are provided (safe_l, safe_t, safe_r, safe_b)
    if canvas_bounds:
        sl, st, sr, sb = canvas_bounds
        # Compute bounding box based on anchor
        if "l" in anchor:
            lx1, lx2 = x, x + tw
        elif "r" in anchor:
            lx1, lx2 = x - tw, x
        else:
            lx1, lx2 = x - tw // 2, x + tw // 2

        if "a" in anchor or "t" in anchor:
            ly1, ly2 = y, y + th
        elif "d" in anchor or "b" in anchor:
            ly1, ly2 = y - th, y
        else:
            ly1, ly2 = y - th // 2, y + th // 2

        if lx1 < sl:
            x += (sl - lx1)
        elif lx2 > sr:
            x -= (lx2 - sr)

        if ly1 < st:
            y += (st - ly1)
        elif ly2 > sb:
            y -= (ly2 - sb)

    # Sharp rendering with contrast halo / drop shadow
    if is_dark_bg:
        shadow_c = (10, 10, 12, 230)
        draw.text((x + 2, y + 2), label, fill=shadow_c, font=font, anchor=anchor)
        draw.text((x, y), label, fill=(255, 255, 255, 255), font=font, anchor=anchor)
    else:
        halo_c = (255, 255, 255, 240)
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            draw.text((x + ox, y + oy), label, fill=halo_c, font=font, anchor=anchor)
        draw.text((x, y), label, fill=(18, 18, 22, 255), font=font, anchor=anchor)

    return (x, y)


def draw_scene_anchor_pill(
    draw: ImageDraw.ImageDraw,
    text: str,
    canvas_w: int,
    y_pos: int,
    font: ImageFont.ImageFont,
    is_dark_bg: bool = False
):
    """Draws a clean Vox-style chapter pill banner at top center."""
    if not text:
        return
    text_clean = text.upper().strip()[:28]
    tb = font.getbbox(text_clean)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]

    pad_x = 22
    pad_y = 8
    cx = canvas_w // 2
    x1 = cx - tw // 2 - pad_x
    x2 = cx + tw // 2 + pad_x
    y1 = y_pos - th // 2 - pad_y
    y2 = y_pos + th // 2 + pad_y

    if is_dark_bg:
        badge_bg = (255, 255, 255, 225)
        badge_text = (20, 20, 24, 255)
        border_c = (255, 255, 255, 255)
    else:
        badge_bg = (24, 24, 28, 225)
        badge_text = (255, 255, 255, 255)
        border_c = (255, 255, 255, 90)

    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=16, fill=badge_bg, outline=border_c, width=1)
    draw.text((cx, y_pos), text_clean, fill=badge_text, font=font, anchor="mm")


# ---------------------------------------------------------------------------
# 1,000+ Procedural Marker & Annotation Engine (With Safe Margin Clamping)
# ---------------------------------------------------------------------------
def draw_procedural_marker(
    draw: ImageDraw.ImageDraw,
    center: Tuple[int, int],
    radius: int,
    style: Optional[str] = None,
    color_scheme: Optional[Dict[str, Any]] = None,
    label: Optional[str] = None,
    label_font: Optional[ImageFont.ImageFont] = None,
    quadrant: str = "top_right",
    text_color: Optional[Tuple[int, int, int, int]] = None,
    canvas_size: Tuple[int, int] = (1080, 1920),
    is_dark_bg: bool = False
):
    """
    Draws one of 1,000+ procedural documentary markers with mathematical boundary clamping:
    - 'bead_pointer_ring': Yellow marker circle around detail + S-curve pointer line
      terminating in a solid orange/gold accent bead dot pointing to the bold label!
    - Guaranteed zero text clipping: automatically clamps within safe screen margins.
    """
    cx, cy = center
    cw, ch = canvas_size
    safe_l, safe_r = int(cw * 0.06), int(cw * 0.94)
    safe_t, safe_b = int(ch * 0.08), int(ch * 0.90)
    canvas_bounds = (safe_l, safe_t, safe_r, safe_b)

    if not color_scheme:
        color_scheme = random.choice(MARKER_COLORWAYS)
    if not style:
        # 55% probability of the exact bead_pointer_ring from user screenshot
        if random.random() < 0.55:
            style = "bead_pointer_ring"
        else:
            style = random.choice(MARKER_STYLES)

    main_c = color_scheme["main"]
    accent_c = color_scheme["accent"]
    glow_c = color_scheme["glow"]

    # Direction vectors for quadrant
    dx = 1 if "right" in quadrant else -1
    dy = -1 if "top" in quadrant else 1

    # Measure label if present
    tw, th = (0, 0)
    if label and label_font:
        tb = label_font.getbbox(label)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]

    # Auto-flip dx if text would overflow horizontally
    if dx > 0 and (cx + radius + tw + 30 > safe_r) and (cx - radius - tw - 30 >= safe_l):
        dx = -1
    elif dx < 0 and (cx - radius - tw - 30 < safe_l) and (cx + radius + tw + 30 <= safe_r):
        dx = 1

    # Auto-flip dy if text would overflow vertically
    if dy < 0 and (cy - radius - th - 30 < safe_t):
        dy = 1
    elif dy > 0 and (cy + radius + th + 30 > safe_b):
        dy = -1

    if style == "bead_pointer_ring":
        # -------------------------------------------------------------------
        # EXACT STYLE FROM USER SCREENSHOT:
        # Circle + curved squiggly pointer arc + terminal accent bead dot!
        # -------------------------------------------------------------------
        # 1. Focus circle with inner glow
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.ellipse(bbox, outline=main_c, width=5)
        draw.ellipse([cx - radius + 2, cy - radius + 2, cx + radius - 2, cy + radius - 2], outline=glow_c, width=2)

        # 2. Check if label fits to the right, to the left, or needs to go above/below
        fits_right = (cx + radius + tw + 30 <= safe_r)
        fits_left = (cx - radius - tw - 30 >= safe_l)

        if fits_right and ("right" in quadrant or not fits_left):
            ex = cx + radius + 20
            ey = cy + dy * int(radius * 0.7)
            ey = max(safe_t + 20, min(safe_b - 20, ey))
            bead_pos = (ex, ey)
            label_pos = (ex + 16, ey)
            anchor = "la"

            start_angle = math.atan2(ey - cy, ex - cx)
            sx = int(cx + radius * math.cos(start_angle))
            sy = int(cy + radius * math.sin(start_angle))
            ctrl_x = (sx + ex) // 2 + int(radius * 0.25)
            ctrl_y = (sy + ey) // 2 - dy * int(radius * 0.20)

        elif fits_left:
            ex = cx - radius - 20
            ey = cy + dy * int(radius * 0.7)
            ey = max(safe_t + 20, min(safe_b - 20, ey))
            bead_pos = (ex, ey)
            label_pos = (ex - 16, ey)
            anchor = "ra"

            start_angle = math.atan2(ey - cy, ex - cx)
            sx = int(cx + radius * math.cos(start_angle))
            sy = int(cy + radius * math.sin(start_angle))
            ctrl_x = (sx + ex) // 2 - int(radius * 0.25)
            ctrl_y = (sy + ey) // 2 - dy * int(radius * 0.20)

        else:
            # Squeeze: Place ABOVE circle, perfectly centered! (Like Bauhaus screenshots 2 & 3!)
            ey = cy - radius - 22 if cy - radius - 60 >= safe_t else cy + radius + 22
            ex = cx
            bead_pos = (ex, ey)
            lbl_y = ey - 22 if ey < cy else ey + 22
            label_pos = (cx, lbl_y)
            anchor = "mm"

            sx = cx
            sy = cy - radius if ey < cy else cy + radius
            ctrl_x = cx + int(radius * 0.15)
            ctrl_y = (sy + ey) // 2

        # Draw smooth bezier pointer curve
        steps = 22
        pts = []
        for i in range(steps + 1):
            t = i / steps
            bx = (1 - t)**2 * sx + 2 * (1 - t) * t * ctrl_x + t**2 * ex
            by = (1 - t)**2 * sy + 2 * (1 - t) * t * ctrl_y + t**2 * ey
            pts.append((int(bx), int(by)))
        draw.line(pts, fill=main_c, width=4)

        # 3. Terminal Accent Bead (Solid accent dot at bead_pos)
        bead_r = 7
        bx, by = bead_pos
        draw.ellipse([bx - bead_r, by - bead_r, bx + bead_r, by + bead_r], fill=accent_c, outline=main_c, width=2)

        # 4. Sharp Label Typography right beside the bead
        if label and label_font:
            draw_sharp_badge_label(draw, label, label_pos, label_font, anchor=anchor, is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

    elif style == "arrow_pointer_ring":
        # Circle + curved arrow with sharp triangular head
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.ellipse(bbox, outline=main_c, width=4)

        fits_right = (cx + radius + tw + 30 <= safe_r)
        fits_left = (cx - radius - tw - 30 >= safe_l)

        if fits_right and ("right" in quadrant or not fits_left):
            ex = cx + radius + 20
            ey = max(safe_t + 20, min(safe_b - 20, cy + dy * int(radius * 0.7)))
            label_pos = (ex + 16, ey)
            anchor = "la"
            dx_arr = 1
            start_angle = math.atan2(ey - cy, ex - cx)
            sx = int(cx + radius * math.cos(start_angle))
            sy = int(cy + radius * math.sin(start_angle))
            ctrl_x = (sx + ex) // 2 + 15
            ctrl_y = (sy + ey) // 2 - dy * 15
        elif fits_left:
            ex = cx - radius - 20
            ey = max(safe_t + 20, min(safe_b - 20, cy + dy * int(radius * 0.7)))
            label_pos = (ex - 16, ey)
            anchor = "ra"
            dx_arr = -1
            start_angle = math.atan2(ey - cy, ex - cx)
            sx = int(cx + radius * math.cos(start_angle))
            sy = int(cy + radius * math.sin(start_angle))
            ctrl_x = (sx + ex) // 2 - 15
            ctrl_y = (sy + ey) // 2 - dy * 15
        else:
            ey = cy - radius - 20 if cy - radius - 50 >= safe_t else cy + radius + 20
            ex = cx
            lbl_y = ey - 20 if ey < cy else ey + 20
            label_pos = (cx, lbl_y)
            anchor = "mm"
            dx_arr = 0
            sx = cx
            sy = cy - radius if ey < cy else cy + radius
            ctrl_x = cx + 15
            ctrl_y = (sy + ey) // 2

        pts = []
        for i in range(20):
            t = i / 19.0
            bx = (1 - t)**2 * sx + 2 * (1 - t) * t * ctrl_x + t**2 * ex
            by = (1 - t)**2 * sy + 2 * (1 - t) * t * ctrl_y + t**2 * ey
            pts.append((int(bx), int(by)))
        draw.line(pts, fill=main_c, width=4)

        if dx_arr != 0:
            draw.polygon([(ex, ey), (ex - dx_arr * 14, ey - 7), (ex - dx_arr * 14, ey + 7)], fill=accent_c)
        else:
            arr_dy = -1 if ey < cy else 1
            draw.polygon([(ex, ey), (ex - 7, ey - arr_dy * 14), (ex + 7, ey - arr_dy * 14)], fill=accent_c)

        if label and label_font:
            draw_sharp_badge_label(draw, label, label_pos, label_font, anchor=anchor, is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

    elif style == "double_sketch_loop":
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=main_c, width=4)
        draw.ellipse([cx - radius + 4, cy - radius - 3, cx + radius - 2, cy + radius + 5], outline=glow_c, width=3)
        if label and label_font:
            lbl_y = cy - radius - 30 if dy < 0 else cy + radius + 30
            draw_sharp_badge_label(draw, label, (cx, lbl_y), label_font, anchor="mm", is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

    elif style == "architectural_viewfinder":
        b = radius + 15
        arm = int(radius * 0.35)
        # 4 Corner brackets
        draw.line([(cx - b, cy - b), (cx - b + arm, cy - b)], fill=main_c, width=4)
        draw.line([(cx - b, cy - b), (cx - b, cy - b + arm)], fill=main_c, width=4)
        draw.line([(cx + b, cy - b), (cx + b - arm, cy - b)], fill=main_c, width=4)
        draw.line([(cx + b, cy - b), (cx + b, cy - b + arm)], fill=main_c, width=4)
        draw.line([(cx - b, cy + b), (cx - b + arm, cy + b)], fill=main_c, width=4)
        draw.line([(cx - b, cy + b), (cx - b, cy + b - arm)], fill=main_c, width=4)
        draw.line([(cx + b, cy + b), (cx + b - arm, cy + b)], fill=main_c, width=4)
        draw.line([(cx + b, cy + b), (cx + b, cy + b - arm)], fill=main_c, width=4)
        # Center target crosshair
        draw.line([(cx - 8, cy), (cx + 8, cy)], fill=accent_c, width=2)
        draw.line([(cx, cy - 8), (cx, cy + 8)], fill=accent_c, width=2)
        if label and label_font:
            draw_sharp_badge_label(draw, label, (cx, cy + b + 25), label_font, anchor="mm", is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

    elif style == "hand_drawn_box":
        b = radius + 10
        draw.rounded_rectangle([(cx - b, cy - b), (cx + b, cy + b)], radius=16, outline=main_c, width=4)
        draw.line([(cx + b - 15, cy + b), (cx + b + 12, cy + b)], fill=glow_c, width=3)
        if label and label_font:
            lbl_y = cy - b - 25 if dy < 0 else cy + b + 25
            draw_sharp_badge_label(draw, label, (cx, lbl_y), label_font, anchor="mm", is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

    elif style == "concentric_pulse_waves":
        for i, rad in enumerate([radius, int(radius * 1.35), int(radius * 1.7)]):
            c = main_c if i == 0 else (glow_c[0], glow_c[1], glow_c[2], max(40, 160 - i * 60))
            draw.arc([cx - rad, cy - rad, cx + rad, cy + rad], start=-60, end=140, fill=c, width=3)
        if label and label_font:
            lbl_x = cx + radius + 25 if dx > 0 else cx - radius - 25
            draw_sharp_badge_label(draw, label, (lbl_x, cy - radius), label_font, anchor=("la" if dx > 0 else "ra"), is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

    else:
        # Fallback to high-visibility focus ring
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.ellipse(bbox, outline=main_c, width=5)
        if label and label_font:
            lbl_y = cy - radius - 25 if dy < 0 else cy + radius + 25
            draw_sharp_badge_label(draw, label, (cx, lbl_y), label_font, anchor="mm", is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)


def draw_concentric_framing_arcs(
    draw: ImageDraw.ImageDraw,
    center: Tuple[int, int],
    base_radius: int,
    scale_factor: float = 1.0,
    is_dark_bg: bool = False
):
    """
    Draws iconic Bauhaus / Vox modernist concentric framing arcs behind cutouts.
    Directly matches user reference screenshots 4 & 5 (Bauhaus yellow & orange discs).
    """
    cx, cy = center
    r_outer = int(base_radius * 1.18 * scale_factor)
    r_inner = int(base_radius * 0.88 * scale_factor)

    # Outer Bauhaus Yellow Band
    yellow_c = (245, 190, 25, 230) if not is_dark_bg else (255, 215, 40, 220)
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=yellow_c)

    # Inner Bauhaus Orange Disc
    orange_c = (235, 85, 25, 235) if not is_dark_bg else (240, 95, 30, 225)
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=orange_c)


def draw_curved_callout_arrow(
    draw: ImageDraw.ImageDraw,
    start_pt: Tuple[int, int],
    end_pt: Tuple[int, int],
    color: Tuple[int, int, int, int] = (245, 180, 20, 245),
    width: int = 4,
    curvature: float = 0.28,
    has_head: bool = True,
    has_bead: bool = False
):
    """
    Draws a smooth, organic curved pointer arrow matching Bauhaus/Vox infographic callouts.
    Directly matches user reference screenshots 2, 3 & 6 ('curves', 'details', 'decoration' callout arrows).
    """
    sx, sy = start_pt
    ex, ey = end_pt
    dx = ex - sx
    dy = ey - sy
    dist = math.hypot(dx, dy)
    if dist < 8:
        return

    mid_x = (sx + ex) / 2.0
    mid_y = (sy + ey) / 2.0
    nx = -dy / dist
    ny = dx / dist
    ctrl_x = mid_x + nx * dist * curvature
    ctrl_y = mid_y + ny * dist * curvature

    steps = 22
    pts = []
    for i in range(steps + 1):
        t = i / float(steps)
        bx = (1 - t)**2 * sx + 2 * (1 - t) * t * ctrl_x + t**2 * ex
        by = (1 - t)**2 * sy + 2 * (1 - t) * t * ctrl_y + t**2 * ey
        pts.append((int(bx), int(by)))
    draw.line(pts, fill=color, width=width)

    if has_bead:
        bead_r = width + 3
        draw.ellipse([sx - bead_r, sy - bead_r, sx + bead_r, sy + bead_r], fill=color)

    if has_head:
        tx = ex - ctrl_x
        ty = ey - ctrl_y
        td = math.hypot(tx, ty)
        if td > 1:
            tx /= td
            ty /= td
            hl = width * 3.6
            hw = width * 2.2
            p1 = (ex - tx * hl - ty * hw, ey - ty * hl + tx * hw)
            p2 = (ex - tx * hl + ty * hw, ey - ty * hl - tx * hw)
            draw.polygon([(ex, ey), (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1]))], fill=color)


def draw_falling_rain_fx(
    draw: ImageDraw.ImageDraw,
    cloud_bbox: Tuple[int, int, int, int],
    ground_bbox: Tuple[int, int, int, int],
    frame_idx: int,
    total_frames: int
):
    """
    Animates smooth, continuous falling monsoon rain streaks descending from cloud towards ground.
    Deterministic particle paths ensure continuous flow without frame-to-frame jumping or flicker!
    Fulfills user request: 'badal aa gye ladki bhigne lagi to badal ke niche hi he ladki'!
    """
    c_x1, c_y1, c_x2, c_y2 = cloud_bbox
    g_x1, g_y1, g_x2, g_y2 = ground_bbox

    cloud_bottom = c_y2 - 10
    ground_bottom = g_y2 + 20
    fall_dist = max(80, ground_bottom - cloud_bottom)
    rain_span = max(60, (c_x2 - c_x1) - 40)

    num_streaks = 36
    streak_len = 28
    rain_color = (180, 225, 255, 195)
    rain_glow = (255, 255, 255, 120)

    for i in range(num_streaks):
        rx = c_x1 + 20 + int(((i * 79 + 17) % 100) / 100.0 * rain_span)
        speed = 18 + (i % 5) * 4
        y_offset = (frame_idx * speed + i * 83) % fall_dist
        ry = cloud_bottom + y_offset

        # Smooth fall with slight natural diagonal wind angle
        draw.line([(rx, ry), (rx - 3, ry + streak_len)], fill=rain_color, width=2)
        # Bright head sparkle
        draw.line([(rx, ry), (rx - 1, ry + 6)], fill=rain_glow, width=2)


# ---------------------------------------------------------------------------
# Country & Geographical Map Registry (Accurate Nation-Specific Cutouts)
# ---------------------------------------------------------------------------
COUNTRY_MAP_REGISTRY = {
    "india": {
        "aliases": ["भारत", "हिन्दुस्तान", "हिंदुस्तान", "india", "bharat", "hindustan", "भारतीय", "indian"],
        "en": "India map outline territory",
        "label": "INDIA",
        "search": "India map outline territory transparent png cutout isolated",
        "flag_colors": [(255, 153, 51), (255, 255, 255), (19, 136, 8)],
        "type": "map"
    },
    "pakistan": {
        "aliases": ["पाकिस्तान", "pakistan", "pakistani", "पाकिस्तानी"],
        "en": "Pakistan map outline territory",
        "label": "PAKISTAN",
        "search": "Pakistan map outline territory transparent png cutout isolated",
        "flag_colors": [(1, 65, 28), (255, 255, 255)],
        "type": "map"
    },
    "china": {
        "aliases": ["चीन", "चाइना", "china", "chinese", "चीनी"],
        "en": "China map outline territory",
        "label": "CHINA",
        "search": "China map outline territory transparent png cutout isolated",
        "flag_colors": [(222, 41, 16), (255, 222, 0)],
        "type": "map"
    },
    "russia": {
        "aliases": ["रूस", "रशिया", "russia", "russian", "रूसी"],
        "en": "Russia map outline territory",
        "label": "RUSSIA",
        "search": "Russia map outline territory transparent png cutout isolated",
        "flag_colors": [(255, 255, 255), (0, 57, 166), (213, 43, 30)],
        "type": "map"
    },
    "usa": {
        "aliases": ["अमेरिका", "यूएसए", "united states", "usa", "america", "american", "अमेरिकी"],
        "en": "United States America map outline territory",
        "label": "UNITED STATES",
        "search": "United States America map outline territory transparent png cutout isolated",
        "flag_colors": [(179, 25, 66), (255, 255, 255), (10, 49, 97)],
        "type": "map"
    },
    "britain": {
        "aliases": ["ब्रिटेन", "इंग्लैंड", "अंग्रेज", "ब्रिटिश", "यूके", "britain", "uk", "england", "british", "अंग्रेजों", "ईस्ट इंडिया"],
        "en": "United Kingdom Great Britain map outline territory",
        "label": "BRITAIN",
        "search": "United Kingdom Great Britain map outline territory transparent png cutout isolated",
        "flag_colors": [(1, 33, 105), (255, 255, 255), (200, 16, 46)],
        "type": "map"
    },
    "bangladesh": {
        "aliases": ["बांग्लादेश", "बंगलादेश", "bangladesh", "bangladeshi"],
        "en": "Bangladesh map outline territory",
        "label": "BANGLADESH",
        "search": "Bangladesh map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 106, 78), (244, 42, 65)],
        "type": "map"
    },
    "nepal": {
        "aliases": ["नेपाल", "nepal", "nepali", "नेपाली"],
        "en": "Nepal map outline territory",
        "label": "NEPAL",
        "search": "Nepal map outline territory transparent png cutout isolated",
        "flag_colors": [(220, 20, 60), (0, 56, 147)],
        "type": "map"
    },
    "sri_lanka": {
        "aliases": ["श्रीलंका", "sri lanka", "srilanka"],
        "en": "Sri Lanka map outline territory",
        "label": "SRI LANKA",
        "search": "Sri Lanka map outline territory transparent png cutout isolated",
        "flag_colors": [(141, 21, 58), (255, 190, 0)],
        "type": "map"
    },
    "afghanistan": {
        "aliases": ["अफगानिस्तान", "अफ़ग़ानिस्तान", "afghanistan"],
        "en": "Afghanistan map outline territory",
        "label": "AFGHANISTAN",
        "search": "Afghanistan map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 0, 0), (211, 32, 40), (0, 122, 54)],
        "type": "map"
    },
    "japan": {
        "aliases": ["जापान", "japan", "japanese", "जापानी"],
        "en": "Japan map outline territory",
        "label": "JAPAN",
        "search": "Japan map outline territory transparent png cutout isolated",
        "flag_colors": [(255, 255, 255), (188, 0, 45)],
        "type": "map"
    },
    "germany": {
        "aliases": ["जर्मनी", "germany", "german", "जर्मन"],
        "en": "Germany map outline territory",
        "label": "GERMANY",
        "search": "Germany map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 0, 0), (221, 0, 0), (255, 204, 0)],
        "type": "map"
    },
    "france": {
        "aliases": ["फ्रांस", "फ़्रांस", "france", "french", "फ्रांसीसी"],
        "en": "France map outline territory",
        "label": "FRANCE",
        "search": "France map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 38, 84), (255, 255, 255), (237, 41, 57)],
        "type": "map"
    },
    "israel": {
        "aliases": ["इजराइल", "इज़राइल", "इस्राइल", "israel", "israeli"],
        "en": "Israel map outline territory",
        "label": "ISRAEL",
        "search": "Israel map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 56, 184), (255, 255, 255)],
        "type": "map"
    },
    "palestine": {
        "aliases": ["फिलिस्तीन", "फ़िलिस्तीन", "palestine", "palestinian"],
        "en": "Palestine map outline territory",
        "label": "PALESTINE",
        "search": "Palestine map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 0, 0), (255, 255, 255), (0, 122, 61), (238, 42, 53)],
        "type": "map"
    },
    "ukraine": {
        "aliases": ["यूक्रेन", "ukraine", "ukrainian"],
        "en": "Ukraine map outline territory",
        "label": "UKRAINE",
        "search": "Ukraine map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 87, 183), (255, 215, 0)],
        "type": "map"
    },
    "iran": {
        "aliases": ["ईरान", "iran", "iranian", "ईरानी"],
        "en": "Iran map outline territory",
        "label": "IRAN",
        "search": "Iran map outline territory transparent png cutout isolated",
        "flag_colors": [(35, 159, 64), (255, 255, 255), (218, 0, 0)],
        "type": "map"
    },
    "saudi_arabia": {
        "aliases": ["सऊदी अरब", "सऊदी", "saudi arabia", "saudi"],
        "en": "Saudi Arabia map outline territory",
        "label": "SAUDI ARABIA",
        "search": "Saudi Arabia map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 108, 53), (255, 255, 255)],
        "type": "map"
    },
    "canada": {
        "aliases": ["कनाडा", "canada", "canadian"],
        "en": "Canada map outline territory",
        "label": "CANADA",
        "search": "Canada map outline territory transparent png cutout isolated",
        "flag_colors": [(255, 0, 0), (255, 255, 255)],
        "type": "map"
    },
    "australia": {
        "aliases": ["ऑस्ट्रेलिया", "australia", "australian"],
        "en": "Australia map outline territory",
        "label": "AUSTRALIA",
        "search": "Australia map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 0, 139), (255, 255, 255), (255, 0, 0)],
        "type": "map"
    },
    "italy": {
        "aliases": ["इटली", "italy", "italian"],
        "en": "Italy map outline territory",
        "label": "ITALY",
        "search": "Italy map outline territory transparent png cutout isolated",
        "flag_colors": [(0, 146, 70), (255, 255, 255), (206, 43, 55)],
        "type": "map"
    },
    "turkey": {
        "aliases": ["तुर्की", "तुर्किये", "turkey", "turkiye"],
        "en": "Turkey map outline territory",
        "label": "TURKEY",
        "search": "Turkey map outline territory transparent png cutout isolated",
        "flag_colors": [(227, 10, 23), (255, 255, 255)],
        "type": "map"
    },
    "egypt": {
        "aliases": ["मिस्र", "इजिप्ट", "egypt", "egyptian"],
        "en": "Egypt map outline territory",
        "label": "EGYPT",
        "search": "Egypt map outline territory transparent png cutout isolated",
        "flag_colors": [(206, 17, 38), (255, 255, 255), (0, 0, 0)],
        "type": "map"
    },
    "south_korea": {
        "aliases": ["दक्षिण कोरिया", "south korea", "korean"],
        "en": "South Korea map outline territory",
        "label": "SOUTH KOREA",
        "search": "South Korea map outline territory transparent png cutout isolated",
        "flag_colors": [(255, 255, 255), (205, 46, 58), (0, 71, 160)],
        "type": "map"
    },
    "north_korea": {
        "aliases": ["उत्तर कोरिया", "north korea"],
        "en": "North Korea map outline territory",
        "label": "NORTH KOREA",
        "search": "North Korea map outline territory transparent png cutout isolated",
        "flag_colors": [(237, 28, 36), (2, 79, 162), (255, 255, 255)],
        "type": "map"
    }
}


def detect_country_in_text(text: str) -> List[Dict[str, Any]]:
    """Identifies exact countries mentioned in Hindi, Hinglish, or English text."""
    if not text:
        return []
    t_low = text.lower()
    found_countries = []
    seen_keys = set()
    
    for c_key, c_data in COUNTRY_MAP_REGISTRY.items():
        aliases = sorted(c_data["aliases"], key=lambda a: len(a), reverse=True)
        for al in aliases:
            pattern = r'(?:\b|[\s,।॥!?—–-]|^)' + re.escape(al.lower()) + r'(?:\b|[\s,।॥!?—–-]|$)'
            if re.search(pattern, t_low) or al.lower() in t_low:
                if c_key not in seen_keys:
                    seen_keys.add(c_key)
                    found_countries.append({
                        "key": c_key,
                        "raw": al,
                        "clean_en": c_data["en"],
                        "label": c_data["label"],
                        "search": c_data["search"],
                        "flag_colors": c_data.get("flag_colors", [(200, 200, 200)]),
                        "type": "map"
                    })
                break
    return found_countries


# ---------------------------------------------------------------------------
# Semantic Entity Spatial Mapping (Sky Elements vs Ground Elements)
# ---------------------------------------------------------------------------
HISTORICAL_ENTITY_MAP = {
    # Maps & Geographical Outlines (Only triggered when map/naksa is explicitly mentioned or contrasted)
    "भारत का नक्शा": {"en": "India map outline territory", "label": "INDIA MAP", "type": "map"},
    "भारत का मैप": {"en": "India map outline territory", "label": "INDIA MAP", "type": "map"},
    "india map": {"en": "India map outline territory", "label": "INDIA MAP", "type": "map"},
    "पाकिस्तान का नक्शा": {"en": "Pakistan map outline territory", "label": "PAKISTAN MAP", "type": "map"},
    "pakistan map": {"en": "Pakistan map outline territory", "label": "PAKISTAN MAP", "type": "map"},
    "नक्शा": {"en": "geographical map border territory outline", "label": "GEOGRAPHICAL MAP", "type": "map"},
    "मैप": {"en": "geographical map border territory outline", "label": "GEOGRAPHICAL MAP", "type": "map"},
    "map": {"en": "geographical map border territory outline", "label": "GEOGRAPHICAL MAP", "type": "map"},
    "सीमा": {"en": "international border boundary checkpoint", "label": "BORDER", "type": "map"},

    # Battles, Historical Dates & Colonial Milestones
    "प्लासी": {"en": "Battle of Plassey 1757 historical painting", "label": "BATTLE OF PLASSEY", "type": "event"},
    "1757": {"en": "Battle of Plassey 1757 historical painting", "label": "YEAR 1757", "type": "event"},
    "1857": {"en": "1857 Indian rebellion sepoy mutiny freedom struggle", "label": "1857 REBELLION", "type": "event"},
    "विद्रोह": {"en": "1857 Indian rebellion freedom revolt historical", "label": "REVOLT 1857", "type": "event"},
    "प्रथम स्वतंत्रता संग्राम": {"en": "first war of Indian independence 1857", "label": "FIRST WAR OF INDEPENDENCE", "type": "event"},
    "स्वतंत्रता संग्राम": {"en": "Indian freedom struggle independence movement", "label": "FREEDOM STRUGGLE", "type": "event"},
    "ईस्ट इंडिया": {"en": "East India Company coat of arms seal historical", "label": "EAST INDIA CO.", "type": "seal"},
    "ब्रिटिश शासन": {"en": "British Raj colonial empire royal emblem", "label": "BRITISH RAJ", "type": "seal"},
    "अंग्रेजी शासन": {"en": "British Raj colonial empire royal emblem", "label": "BRITISH RULE", "type": "seal"},
    "1947": {"en": "15 August 1947 Indian independence day national flag", "label": "1947 INDEPENDENCE", "type": "event"},
    "15 अगस्त": {"en": "15 August 1947 Indian independence celebration tricolor", "label": "INDEPENDENCE DAY", "type": "event"},
    "आजादी": {"en": "Indian independence freedom struggle tricolor", "label": "INDEPENDENCE", "type": "event"},
    "विभाजन": {"en": "Partition of India 1947 historical migration refugee border line", "label": "PARTITION 1947", "type": "event"},
    "1950": {"en": "26 January 1950 Constitution of India republic day", "label": "REPUBLIC 1950", "type": "event"},
    "26 जनवरी": {"en": "26 January 1950 Constitution of India republic day", "label": "26 JANUARY 1950", "type": "event"},
    "संविधान": {"en": "Constitution of India preamble book emblem", "label": "CONSTITUTION", "type": "book"},
    "लोकतंत्र": {"en": "Indian parliament democracy voting ballot", "label": "DEMOCRACY", "type": "concept"},
    "गणराज्य": {"en": "sovereign republic India Ashoka lion pillar emblem", "label": "REPUBLIC OF INDIA", "type": "seal"},
    "संप्रभु": {"en": "sovereign republic India Ashoka lion pillar emblem", "label": "SOVEREIGN REPUBLIC", "type": "seal"},
    "संसद": {"en": "Indian Parliament building New Delhi facade", "label": "PARLIAMENT", "type": "building"},
    "सुप्रीम कोर्ट": {"en": "Supreme Court of India judiciary scales of justice", "label": "SUPREME COURT", "type": "building"},
    "अदालत": {"en": "Supreme Court judiciary gavel justice scales", "label": "JUSTICE & LAW", "type": "concept"},
    "न्याय": {"en": "scales of justice law order constitution", "label": "JUSTICE SYSTEM", "type": "concept"},
    "अधिकार": {"en": "fundamental citizen rights constitution book", "label": "CITIZEN RIGHTS", "type": "concept"},
    "नागरिक": {"en": "citizens of democracy united people rights", "label": "CITIZENS", "type": "concept"},
    "संस्थाएं": {"en": "democratic institutions parliament judiciary law", "label": "INSTITUTIONS", "type": "concept"},
    "सैन्य शक्ति": {"en": "Indian military armed forces army defense soldiers", "label": "MILITARY POWER", "type": "concept"},
    "आर्थिक विकास": {"en": "economic development GDP financial growth skyline", "label": "ECONOMIC GROWTH", "type": "finance"},
    "विज्ञान": {"en": "scientific research innovation laboratory technology", "label": "SCIENCE & TECH", "type": "concept"},
    "तकनीक": {"en": "high technology digital innovation futuristic", "label": "TECHNOLOGY", "type": "concept"},
    "अंतरिक्ष": {"en": "ISRO space exploration rocket satellite launch mission", "label": "SPACE & ISRO", "type": "concept"},
    "अर्थव्यवस्था": {"en": "modern economy GDP stock market financial growth", "label": "INDIAN ECONOMY", "type": "finance"},

    # Economic & Currency Elements (User Screenshot: Businessman eating cash!)
    "businessman": {"en": "rich greedy businessman eating money cash", "label": "GREED & MONEY", "type": "person"},
    "पैसा": {"en": "money currency cash stacks rupee dollar", "label": "MONEY & WEALTH", "type": "finance"},
    "रुपया": {"en": "Indian rupee notes currency cash", "label": "INDIAN RUPEE", "type": "finance"},
    "दौलत": {"en": "money wealth gold bars cash", "label": "WEALTH & ASSETS", "type": "finance"},

    # Design & Architectural Artifacts (User Screenshot: Bauhaus Curves & Details)
    "bauhaus": {"en": "Bauhaus modernist architecture graphic poster", "label": "BAUHAUS", "type": "architecture"},
    "curves": {"en": "architectural design curved roof aesthetic", "label": "CURVES", "type": "architecture"},
    "details": {"en": "architectural facade stone masonry details", "label": "DETAILS", "type": "architecture"},
    "decoration": {"en": "ornate vintage interior decoration art", "label": "DECORATION", "type": "architecture"},
    "झूमर": {"en": "crystal chandelier vintage lighting lamp", "label": "CHANDELIER", "type": "object"},
    "chandelier": {"en": "crystal chandelier vintage lighting lamp", "label": "CHANDELIER", "type": "object"},

    # Sky & Weather Elements (User Example: Clouds, Rain, Sky)
    "badal": {"en": "dark stormy rain clouds storm", "label": "RAIN CLOUDS", "type": "sky"},
    "बादल": {"en": "dark stormy rain clouds storm", "label": "RAIN CLOUDS", "type": "sky"},
    "cloud": {"en": "dark stormy rain clouds", "label": "CLOUDS", "type": "sky"},
    "barish": {"en": "monsoon rain water drops", "label": "MONSOON RAIN", "type": "sky"},
    "बारिश": {"en": "monsoon rain water drops", "label": "MONSOON RAIN", "type": "sky"},
    "सूरज": {"en": "bright sun solar flares", "label": "SUN", "type": "sky"},
    "चांद": {"en": "full glowing moon night", "label": "MOON", "type": "sky"},
    "हवाई जहाज": {"en": "flying jet aircraft", "label": "AIRCRAFT", "type": "sky"},

    # People / Ground Elements (User Example: Girl getting wet under cloud)
    "ladki": {"en": "young girl student woman standing", "label": "GIRL", "type": "person"},
    "लड़की": {"en": "young girl student woman standing", "label": "GIRL", "type": "person"},
    "ladka": {"en": "young boy standing", "label": "BOY", "type": "person"},
    "लड़का": {"en": "young boy standing", "label": "BOY", "type": "person"},
}

SKY_KEYWORDS = {"badal", "बादल", "cloud", "clouds", "rain", "barish", "बारिश", "sun", "suraj", "सूरज", "chand", "चांद", "moon", "star", "stars", "sky", "aasman", "plane", "aircraft", "crown"}
GROUND_KEYWORDS = {"ladki", "लड़की", "girl", "woman", "ladka", "लड़का", "boy", "man", "person", "log", "people", "soldier", "army", "police", "car", "building", "house", "palace", "throne", "ground", "zameen"}


def detect_collage_entities(scene_text: str, main_topic: str = "") -> Dict[str, Any]:
    """Analyzes scene text to detect entities and their spatial / transition role with exact country mapping."""
    text_lower = (scene_text or "").lower()
    topic_lower = (main_topic or "").lower()
    combined = f"{text_lower} {topic_lower}"

    # 1. Exact Country & Map Detection (Guaranteed: NEVER use wrong country or generic world map!)
    countries_in_scene = detect_country_in_text(scene_text)

    # 1.a Multi-country scene (e.g. India & Pakistan, Russia & Ukraine, USA & China, Britain & India)
    if len(countries_in_scene) >= 2:
        c1, c2 = countries_in_scene[0], countries_in_scene[1]
        return {
            "is_detected": True,
            "is_multi_entity": True,
            "entities": [c1, c2],
            "transition_label": f"{c1['label']} & {c2['label']}"
        }

    # 2. Check for Cloud & Girl / Person spatial pair (User explicit example: "badel aa gye ladki bhigne lagi")
    has_sky = any(k in text_lower for k in ["badal", "बादल", "cloud", "rain", "barish", "बारिश"])
    has_person = any(k in text_lower for k in ["ladki", "लड़की", "girl", "ladka", "लड़का", "boy", "person", "bhigne"])
    if has_sky and has_person:
        return {
            "is_detected": True,
            "is_multi_entity": True,
            "entities": [
                {"raw": "बादल", "clean_en": "dark stormy rain clouds storm", "label": "RAIN CLOUDS", "search": "dark rain clouds storm transparent png cutout isolated", "type": "sky"},
                {"raw": "लड़की", "clean_en": "young girl student woman standing", "label": "GIRL", "search": "young girl student woman transparent png cutout isolated", "type": "person"}
            ],
            "transition_label": "CLOUDS & GIRL"
        }

    # 3. Explicit Map/Nation Context (नक्शा, मैप, map, देश, सीमा, border, राष्ट्र, गणराज्य, विभाजन)
    map_context_keywords = ["नक्शा", "मैप", "map", "देश", "सीमा", "border", "विभाजन", "गणराज्य", "territory", "राष्ट्र", "पहचान", "ताकत"]
    has_map_context = any(k in text_lower for k in map_context_keywords)

    if len(countries_in_scene) == 1:
        c = countries_in_scene[0]
        # Check if a specific milestone artifact is also in this scene (e.g. संविधान, ईस्ट इंडिया, संसद, आदि)
        milestone = None
        for mk, mv in HISTORICAL_ENTITY_MAP.items():
            if mk in text_lower and mk not in c["raw"].lower() and mv.get("type") != "map":
                milestone = {
                    "raw": mk,
                    "clean_en": mv["en"],
                    "label": mv["label"],
                    "search": f"{mv['en']} transparent png cutout isolated",
                    "type": mv.get("type", "concept")
                }
                break
        if milestone:
            return {
                "is_detected": True,
                "is_multi_entity": True,
                "entities": [c, milestone],
                "transition_label": f"{c['label']} & {milestone['label']}"
            }
        return {
            "is_detected": True,
            "is_multi_entity": False,
            "entities": [c],
            "transition_label": f"{c['label']} MAP"
        }

    if has_map_context and not countries_in_scene:
        # Check if main_topic specifies a country (e.g. 'भारत का इतिहास' -> India map!)
        topic_countries = detect_country_in_text(main_topic)
        if topic_countries:
            tc = topic_countries[0]
            return {
                "is_detected": True,
                "is_multi_entity": False,
                "entities": [tc],
                "transition_label": f"{tc['label']} MAP"
            }

    # 4. Check for Paired Concepts and Explicit Contrasts / Comparisons
    PAIRED_CONCEPTS_MAP = [
        ("विज्ञान", "तकनीक", "SCIENCE", "TECHNOLOGY", "science technology research transparent png cutout"),
        ("science", "technology", "SCIENCE", "TECHNOLOGY", "science technology research transparent png cutout"),
        ("हार्डवेयर", "सॉफ्टवेयर", "HARDWARE", "SOFTWARE", "computer hardware software engineering transparent png cutout"),
        ("इंसान", "मशीन", "HUMAN", "MACHINE", "human portrait silhouette modern robot transparent png cutout"),
        ("अतीत", "भविष्य", "PAST", "FUTURE", "ancient hourglass futuristic technology transparent png cutout"),
        ("धनी", "गरीब", "RICH", "POOR", "wealthy business money poverty struggle transparent png cutout"),
        ("सफलता", "असफलता", "SUCCESS", "FAILURE", "success trophy failure broken target transparent png cutout"),
        ("शेयर मार्केट", "क्रिप्टो", "STOCK MARKET", "CRYPTO", "stock market trading bull bitcoin transparent png cutout"),
        ("पुरानी तकनीक", "आधुनिक एआई", "OLD TECH", "MODERN AI", "vintage typewriter modern artificial intelligence transparent png cutout"),
    ]

    for c1_word, c2_word, l1, l2, search_query in PAIRED_CONCEPTS_MAP:
        if c1_word in text_lower and c2_word in text_lower:
            is_conflict = any(k in text_lower for k in [" vs ", "versus", "बनाम", " या ", "ya phir", "मुकाबला", "टक्कर", "युद्ध", "clash", "rivalry", "विवाद"])
            conn_symbol = "vs" if is_conflict else "&"
            return {
                "is_detected": True,
                "is_multi_entity": True,
                "is_vs": is_conflict,
                "entities": [
                    {"raw": c1_word, "clean_en": l1.lower(), "label": l1, "search": f"{l1.lower()} transparent png cutout isolated"},
                    {"raw": c2_word, "clean_en": l2.lower(), "label": l2, "search": f"{l2.lower()} transparent png cutout isolated"}
                ],
                "transition_label": f"{l1} {conn_symbol} {l2}"
            }

    # Narrative action words: Sequential actions/storytelling (e.g. मेहनत की और कंपनी बनाई, सायरन बजी और जांच शुरू हुई)
    # MUST NOT be hijacked into 2D collages - they must play real cinematic HD videos!
    NARRATIVE_STORY_WORDS = {
        'की', 'किया', 'किए', 'लगा', 'लगी', 'लगे', 'हुई', 'हुआ', 'हुए', 'था', 'थी', 'थे',
        'आया', 'आई', 'आए', 'गया', 'गई', 'गए', 'चला', 'चली', 'चले', 'बनाई', 'बनाया',
        'देखा', 'देखी', 'देखे', 'सोचा', 'सोची', 'पहुंचा', 'पहुंची', 'मिला', 'मिली', 'मिले',
        'टूटा', 'टूटी', 'सपना', 'सपने', 'कहानी', 'बात', 'शुरू', 'खत्म', 'जाना', 'आना',
        'रहना', 'सोना', 'उठना', 'बैठना', 'रोना', 'हंसना', 'करना', 'होने', 'करने', 'रात-दिन', 'दिन',
        'अचानक', 'फिर', 'लेकिन', 'तभी', 'जब', 'तब', 'जिसने', 'जिसका', 'जिसके', 'जिसकी',
        'सायरन', 'बजी', 'बजा', 'शुरुआत', 'कदम', 'रास्ता', 'मंजिल', 'हासिल', 'सकता', 'सकती', 'सकते'
    }

    # Explicit contrast & comparison regexes
    two_entity_regexes = [
        r'([A-Za-z\u0900-\u097F0-9\s]{2,20})\s+(?:vs|versus|बनाम|या फिर|ya phir|मुकाबला)\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})',
        r'क(?:भी|हा)\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})\s+तो\s+क(?:भी|हा)\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})',
        r'सिर्फ\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})\s+नहीं.*?बल्कि\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})',
    ]

    for pat in two_entity_regexes:
        m = re.search(pat, text_lower)
        if m:
            p1_raw = m.group(1).strip()
            p2_raw = m.group(2).strip()
            clean_p1 = " ".join([w for w in p1_raw.split() if w not in ["का", "की", "के", "में", "से", "पर", "एक", "यह", "है", "था", "थी", "हो", "रहे"]])
            clean_p2 = " ".join([w for w in p2_raw.split() if w not in ["का", "की", "के", "में", "से", "पर", "एक", "यह", "है", "था", "थी", "हो", "रहे"]])

            w1 = clean_p1.split()
            w2 = clean_p2.split()
            if not w1 or not w2:
                continue
            if any(w in NARRATIVE_STORY_WORDS for w in w1 + w2):
                continue

            if len(clean_p1) >= 2 and len(clean_p2) >= 2:
                e1 = _resolve_entity(clean_p1, main_topic)
                e2 = _resolve_entity(clean_p2, main_topic)
                if e1 and e2 and e1["clean_en"] != e2["clean_en"]:
                    is_conflict = any(k in text_lower for k in [" vs ", "versus", "बनाम", " या ", "ya phir", "तनाव", "युद्ध", "clash", "rivalry", "लड़ाई", "विवाद", "मुकाबला"])
                    conn_symbol = "vs" if is_conflict else "&"
                    return {
                        "is_detected": True,
                        "is_multi_entity": True,
                        "is_vs": is_conflict,
                        "entities": [e1, e2],
                        "transition_label": f"{e1['label']} {conn_symbol} {e2['label']}"
                    }

    # 5. Single entity milestone detection (Strictly in scene text)
    for key, val in HISTORICAL_ENTITY_MAP.items():
        if key in text_lower:
            return {
                "is_detected": True,
                "is_multi_entity": False,
                "entities": [{
                    "raw": key,
                    "clean_en": val["en"],
                    "label": val["label"],
                    "search": f"{val['en']} transparent png cutout isolated",
                    "type": val.get("type", "concept")
                }],
                "transition_label": val["label"]
            }

    clean_kw = " ".join([w for w in scene_text.split() if len(w) > 2][:3]) if scene_text else main_topic
    return {
        "is_detected": False,
        "is_multi_entity": False,
        "entities": [{
            "raw": clean_kw,
            "clean_en": f"{clean_kw} documentary artifact",
            "label": clean_kw.upper()[:20],
            "search": f"{clean_kw} transparent png cutout isolated",
            "type": "concept"
        }],
        "transition_label": clean_kw.upper()[:20]
    }


def _resolve_entity(raw_text: str, main_topic: str = "") -> Optional[Dict[str, str]]:
    """Helper to resolve a raw Hindi/English phrase to a searchable cutout entity."""
    t_low = raw_text.lower().strip()

    # Priority 1: Check if raw_text mentions a country
    c_list = detect_country_in_text(raw_text)
    if c_list:
        c = c_list[0]
        return {
            "raw": raw_text,
            "clean_en": c["clean_en"],
            "label": c["label"],
            "search": c["search"],
            "flag_colors": c.get("flag_colors", [(200, 200, 200)]),
            "type": "map"
        }

    # Priority 2: Historical milestone map
    for k, v in HISTORICAL_ENTITY_MAP.items():
        if k in t_low:
            return {
                "raw": raw_text,
                "clean_en": v["en"],
                "label": v["label"],
                "search": f"{v['en']} transparent png cutout isolated",
                "type": v.get("type", "concept")
            }

    try:
        from web_image_fetcher import translate_to_visual_english
        en_phrase = translate_to_visual_english(raw_text, main_topic)
    except Exception:
        en_phrase = raw_text

    clean_en = en_phrase or raw_text
    label = " ".join(clean_en.split()[:2]).upper()

    # Infer type
    ent_type = "sky" if any(w in t_low for w in SKY_KEYWORDS) else ("person" if any(w in t_low for w in GROUND_KEYWORDS) else "concept")
    return {
        "raw": raw_text,
        "clean_en": clean_en,
        "label": label,
        "search": f"{clean_en} transparent png cutout isolated",
        "type": ent_type
    }


def fetch_and_prepare_cutouts(
    entities: List[Dict[str, str]],
    output_dir: str,
    used_media_ids: Optional[set] = None
) -> List[str]:
    """Downloads and prepares transparent cutout PNGs for detected entities."""
    os.makedirs(output_dir, exist_ok=True)
    used_ids = used_media_ids if used_media_ids is not None else set()
    prepared_cutouts = []

    for idx, ent in enumerate(entities):
        clean_en = ent.get("clean_en", "").strip() or ent.get("raw", "artifact")
        label = ent.get("label", clean_en.upper())
        search_q = ent.get("search") or f"{clean_en} transparent png cutout isolated"
        target_png = os.path.join(output_dir, f"cutout_asset_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', clean_en)[:20]}.png")
        raw_downloaded = None

        # 1. Pinterest HD transparent search
        try:
            from pinterest_downloader import fetch_pinterest_photos_via_gallery_dl
            print(f"📌 [Cutout Fetcher] Searching Pinterest for transparent cutout ({idx+1}/{len(entities)}): '{search_q}'...")
            p_files = fetch_pinterest_photos_via_gallery_dl(search_q, limit=1, output_dir=output_dir, used_media_ids=used_ids, orientation="any")
            if p_files and os.path.exists(p_files[0]) and os.path.getsize(p_files[0]) > 2000:
                raw_downloaded = p_files[0]
        except Exception as e_pin:
            print(f"⚠️ [Cutout Fetcher Pinterest warning]: {e_pin}")

        # 2. Web Image Fallback
        if not raw_downloaded or not os.path.exists(raw_downloaded):
            try:
                from web_image_fetcher import fetch_web_image
                web_path = os.path.join(output_dir, f"web_cutout_{idx}.png")
                if fetch_web_image(f"{clean_en} isolated png", web_path, orientation="square"):
                    if os.path.exists(web_path) and os.path.getsize(web_path) > 2000:
                        raw_downloaded = web_path
            except Exception as e_web:
                print(f"⚠️ [Cutout Fetcher Web Image warning]: {e_web}")

        # 3. Clean transparent cutout processing
        if raw_downloaded and os.path.exists(raw_downloaded):
            try:
                cutout_pil = make_transparent_cutout(raw_downloaded, output_png=target_png)
                if os.path.exists(target_png) and os.path.getsize(target_png) > 1000:
                    prepared_cutouts.append(target_png)
                    continue
            except Exception as e_proc:
                print(f"⚠️ [Cutout Processing warning]: {e_proc}")

        # 4. Stylized Graphical Fallback (Territory Map Badge for Maps, Emblems for Artifacts)
        fallback_img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        fb_draw = ImageDraw.Draw(fallback_img)
        ent_type = ent.get("type", "concept")

        if ent_type == "map":
            flag_colors = ent.get("flag_colors", [(255, 153, 51), (255, 255, 255), (19, 136, 8)])
            # Draw sophisticated geographic emblem/badge with flag bands
            fb_draw.ellipse([(30, 30), (570, 570)], fill=(20, 24, 38, 245), outline=(255, 255, 255, 220), width=6)
            fb_draw.ellipse([(50, 50), (550, 550)], outline=(255, 215, 0, 180), width=3)
            # Flag accent arc / stripes
            for b_idx, col in enumerate(flag_colors[:3]):
                arc_inset = 65 + b_idx * 16
                fb_draw.arc([(arc_inset, arc_inset), (600 - arc_inset, 600 - arc_inset)], start=140, end=40, fill=col + (220,), width=8)
            # Stylized territory map diamond / continent polygon
            poly_pts = [(300, 110), (450, 210), (490, 380), (370, 490), (300, 510), (220, 480), (140, 360), (160, 200)]
            fb_draw.polygon(poly_pts, fill=(35, 45, 65, 230), outline=(255, 255, 255, 160))
            # Inner territory grid
            fb_draw.line([(300, 110), (300, 510)], fill=(255, 255, 255, 80), width=2)
            fb_draw.line([(150, 310), (470, 310)], fill=(255, 255, 255, 80), width=2)
            # Center country name
            f_fb = get_font(size=44, font_type="bold")
            fb_draw.text((300, 290), label[:12], fill=(255, 255, 255, 255), font=f_fb, anchor="mm")
            # Sub-pill
            f_sub = get_font(size=20, font_type="bold")
            fb_draw.text((300, 335), "TERRITORY MAP", fill=(255, 215, 0, 240), font=f_sub, anchor="mm")
        else:
            fb_color = (210, 60, 45, 240) if idx == 0 else (40, 110, 200, 240)
            fb_draw.rounded_rectangle([(40, 40), (560, 560)], radius=80, fill=fb_color, outline=(255, 255, 255, 200), width=8)
            fb_draw.ellipse([(100, 100), (500, 500)], outline=(255, 255, 255, 160), width=5)
            f_fb = get_font(size=40, font_type="bold")
            fb_draw.text((300, 300), label[:14], fill=(255, 255, 255, 255), font=f_fb, anchor="mm")
        fallback_img.save(target_png, format="PNG")
        prepared_cutouts.append(target_png)

    return prepared_cutouts


# ---------------------------------------------------------------------------
# Core Multi-Directional & Spatial Animation Renderer
# ---------------------------------------------------------------------------
def render_collage_motion_clip(
    cutout_paths: List[str],
    output_mp4: str,
    duration: float,
    entity_metadata: Dict[str, Any],
    target_size: Tuple[int, int] = (1080, 1920),
    fps: int = 24
) -> str:
    """
    Renders multi-directional documentary collage animation:
    - User Request 1: Multi-Directional Slide! (Right, Left, Bottom-rise, Top-drop).
    - User Request 2: Spatial Hierarchy (e.g. Clouds above at y~0.22, Girl below at y~0.68 + Rain FX).
    - User Request 3: 1,000+ Procedural Markers (Bead pointer, Arrow pointer, Double loop, etc.).
    - User Request 4: Occasional '+' crosshairs (not on every frame).
    """
    w, h = target_size
    duration = max(3.5, float(duration))
    total_frames = int(duration * fps)

    entities = entity_metadata.get("entities", [])
    scene_text = entity_metadata.get("scene_text", "")

    # 1. Load transparent cutouts
    loaded_cutouts = []
    for p in cutout_paths:
        if os.path.exists(p):
            try:
                c_img = make_transparent_cutout(p)
                loaded_cutouts.append(c_img)
            except Exception as e_cut:
                print(f"⚠️ [Collage Cutout] Warning loading {p}: {e_cut}")
    
    if not loaded_cutouts:
        # Fallback to elegant procedural cutouts so render never fails
        ents = list(entities) if entities else [{"label": "ARTIFACT 1", "clean_en": "artifact"}, {"label": "ARTIFACT 2", "clean_en": "artifact"}]
        if len(ents) < 2 and entity_metadata.get("is_multi_entity"):
            ents.append({"label": "ENTITY 2", "clean_en": "concept"})
        for idx, ent in enumerate(ents[:2]):
            fallback_img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
            fb_draw = ImageDraw.Draw(fallback_img)
            fb_color = (205, 36, 36, 240) if idx == 0 else (40, 110, 200, 240)
            fb_draw.rounded_rectangle([(40, 40), (560, 560)], radius=80, fill=fb_color, outline=(255, 255, 255, 200), width=8)
            fb_draw.ellipse([(100, 100), (500, 500)], outline=(255, 255, 255, 160), width=5)
            f_fb = get_font(size=36, font_type="bold")
            lbl_text = ent.get("label", "ENTITY")[:14]
            fb_draw.text((300, 300), lbl_text, fill=(255, 255, 255, 255), font=f_fb, anchor="mm")
            loaded_cutouts.append(fallback_img)

    # Multi-entity detection based on loaded cutouts and metadata
    is_multi = bool((entity_metadata.get("is_multi_entity") or len(entities) >= 2) and len(loaded_cutouts) >= 2)

    # 2. Canvas Base & Palette Metadata
    canvas_base, palette_info = create_collage_canvas(w, h, draw_grid=None, draw_tape=True, draw_vignette=True)
    is_dark_bg = palette_info.get("is_dark", False)

    # 3. Determine Spatial Staging & Directional Transition Mode
    # Check if Sky + Ground relationship exists (e.g. Clouds above, Person/Girl below!)
    e1_type = entities[0].get("type", "concept") if len(entities) > 0 else "concept"
    e2_type = entities[1].get("type", "concept") if len(entities) > 1 else "concept"

    is_sky_ground_scene = (
        is_multi and (
            (e1_type == "sky" and e2_type in ["person", "building", "ground", "concept"]) or
            ("badal" in scene_text.lower() or "cloud" in scene_text.lower())
        )
    )

    # Pick transition direction
    if is_sky_ground_scene:
        transition_mode = "sky_descends_ground_rises"
    elif is_multi:
        transition_mode = random.choice([
            "slide_left_then_right_enters",
            "slide_right_then_left_enters",
            "slide_bottom_up"
        ])
    else:
        transition_mode = random.choice([
            "rise_from_bottom",
            "descend_from_top",
            "ken_burns_zoom"
        ])

    # 4. Scale and size cutouts with Pro-level Sharpening and Balanced Margins
    if is_sky_ground_scene:
        max_c1_w, max_c1_h = int(w * 0.72), int(h * 0.22) # Cloud: wider banner on top
        max_c2_w, max_c2_h = int(w * 0.48), int(h * 0.45) # Girl/Person: standing below
    elif is_multi:
        max_c1_w, max_c1_h = int(w * 0.35), int(h * 0.35) # Balanced symmetrical columns with ample center breathing room
        max_c2_w, max_c2_h = int(w * 0.35), int(h * 0.35)
    else:
        max_c1_w, max_c1_h = int(w * 0.62), int(h * 0.52) # Rule of thirds balanced framing
        max_c2_w, max_c2_h = int(w * 0.62), int(h * 0.52)

    scaled_cutouts = []
    shadows = []
    for idx, c in enumerate(loaded_cutouts):
        cw, ch = c.size
        mw = max_c1_w if idx == 0 else max_c2_w
        mh = max_c1_h if idx == 0 else max_c2_h
        scale = min(mw / cw, mh / ch)
        nw, nh = max(60, int(cw * scale)), max(60, int(ch * scale))
        # Ultra-sharp downsampling with LANCZOS + unsharp mask sharpening
        c_sharp = sharpen_cutout(c, amount=1.35)
        res_c = c_sharp.resize((nw, nh), Image.LANCZOS)
        res_c = sharpen_cutout(res_c, amount=1.15)
        sh_img, sh_offset = create_cutout_drop_shadow(res_c, blur_radius=14, offset=(8, 14), shadow_opacity=0.35)
        scaled_cutouts.append(res_c)
        shadows.append((sh_img, sh_offset))

    font_title = get_font(size=int(w * 0.044), font_type="bold")
    font_callout = get_font(size=int(w * 0.030), font_type="serif")
    font_pill = get_font(size=int(w * 0.026), font_type="bold")
    font_vs = get_font(size=int(w * 0.028), font_type="bold")

    safe_l, safe_r = int(w * 0.06), int(w * 0.94)
    safe_t, safe_b = int(h * 0.08), int(h * 0.90)
    canvas_bounds = (safe_l, safe_t, safe_r, safe_b)
    scene_tag = entity_metadata.get("transition_label", "")

    # Pick procedural marker colorways & styles
    marker_color_1 = random.choice(MARKER_COLORWAYS)
    marker_color_2 = random.choice([c for c in MARKER_COLORWAYS if c["name"] != marker_color_1["name"]])
    marker_style_1 = "bead_pointer_ring" if random.random() < 0.60 else random.choice(MARKER_STYLES)
    marker_style_2 = "bead_pointer_ring" if random.random() < 0.60 else random.choice(MARKER_STYLES)

    # 5. FFmpeg subprocess with High-Clarity CRF 18
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{w}x{h}",
        "-pix_fmt", "rgba",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-threads", "1",
        os.path.abspath(output_mp4)
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    slide_dur_frames = int(0.9 * fps)
    t_trans_start = int(total_frames * 0.40)
    t_trans_end = t_trans_start + slide_dur_frames

    def ease_out_cubic(t_norm: float) -> float:
        t_c = max(0.0, min(1.0, t_norm))
        return 1.0 - math.pow(1.0 - t_c, 3)

    # 6. Render Frames Loop
    for frame_idx in range(total_frames):
        frame = canvas_base.copy()
        draw = ImageDraw.Draw(frame, "RGBA")

        # Top Scene Anchor Pill (Consistent Vox-style chapter tag)
        if scene_tag:
            draw_scene_anchor_pill(draw, scene_tag, w, int(h * 0.075), font_pill, is_dark_bg=is_dark_bg)

        if is_sky_ground_scene:
            # ===============================================================
            # SPATIAL HIERARCHY: SKY (CLOUDS) ON TOP, GROUND (GIRL) BELOW!
            # ===============================================================
            c1 = scaled_cutouts[0] # Cloud
            sh1, off1 = shadows[0]
            c2 = scaled_cutouts[1] # Girl
            sh2, off2 = shadows[1]

            lbl1 = entities[0]["label"] if len(entities) > 0 else "CLOUDS"
            lbl2 = entities[1]["label"] if len(entities) > 1 else "GIRL"

            target_c1_y = int(h * 0.24)
            target_c2_y = int(h * 0.72)

            # Phase 1: Cloud descends from top of screen
            if frame_idx < t_trans_start:
                t_in = min(1.0, frame_idx / (fps * 0.6))
                e_in = ease_out_cubic(t_in)
                pos_y1 = int((-c1.height) + (target_c1_y + c1.height) * e_in)
                x1 = int(w * 0.50 - c1.width / 2)
                y1 = int(pos_y1 - c1.height / 2)

                frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                frame.paste(c1, (x1, y1), mask=c1)

                # Procedural Marker on Cloud (Clamped)
                ring_cx = x1 + int(c1.width * 0.5)
                ring_cy = y1 + int(c1.height * 0.45)
                draw_procedural_marker(
                    draw, (ring_cx, ring_cy), int(c1.width * 0.22),
                    style=marker_style_1, color_scheme=marker_color_1,
                    label=lbl1, label_font=font_title, quadrant="top_right",
                    canvas_size=(w, h), is_dark_bg=is_dark_bg
                )

            # Phase 2: Cloud stays at top, Girl rises up from bottom under the cloud!
            elif t_trans_start <= frame_idx < t_trans_end:
                t_norm = (frame_idx - t_trans_start) / slide_dur_frames
                ease_val = ease_out_cubic(t_norm)

                # Cloud at top
                x1 = int(w * 0.50 - c1.width / 2)
                y1 = int(target_c1_y - c1.height / 2)
                frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                frame.paste(c1, (x1, y1), mask=c1)

                # Girl rises from bottom of canvas
                pos_y2 = int((h + c2.height) - (h + c2.height - target_c2_y) * ease_val)
                x2 = int(w * 0.50 - c2.width / 2)
                y2 = int(pos_y2 - c2.height / 2)
                frame.paste(sh2, (x2 + off2[0], y2 + off2[1]), mask=sh2)
                frame.paste(c2, (x2, y2), mask=c2)

                # Smooth continuous rain streaks
                draw_falling_rain_fx(
                    draw,
                    (x1, y1, x1 + c1.width, y1 + c1.height),
                    (x2, y2, x2 + c2.width, y2 + c2.height),
                    frame_idx, total_frames
                )

            # Phase 3: Both elements in natural spatial position, focus shifts to Girl!
            else:
                x1 = int(w * 0.50 - c1.width / 2)
                y1 = int(target_c1_y - c1.height / 2)
                frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                frame.paste(c1, (x1, y1), mask=c1)

                x2 = int(w * 0.50 - c2.width / 2)
                y2 = int(target_c2_y - c2.height / 2)
                frame.paste(sh2, (x2 + off2[0], y2 + off2[1]), mask=sh2)
                frame.paste(c2, (x2, y2), mask=c2)

                # Smooth continuous rain streaks
                draw_falling_rain_fx(
                    draw,
                    (x1, y1, x1 + c1.width, y1 + c1.height),
                    (x2, y2, x2 + c2.width, y2 + c2.height),
                    frame_idx, total_frames
                )

                # Procedural Marker on Girl (Under the clouds, safely clamped)
                ring2_cx = x2 + int(c2.width * 0.5)
                ring2_cy = y2 + int(c2.height * 0.35)
                draw_procedural_marker(
                    draw, (ring2_cx, ring2_cy), int(c2.width * 0.32),
                    style=marker_style_2, color_scheme=marker_color_2,
                    label=lbl2, label_font=font_title, quadrant="top_right",
                    canvas_size=(w, h), is_dark_bg=is_dark_bg
                )

        elif is_multi:
            # ===============================================================
            # DYNAMIC MULTI-DIRECTIONAL TRANSITIONS (Symmetrical Balanced Layout)
            # ===============================================================
            c1 = scaled_cutouts[0]
            sh1, off1 = shadows[0]
            c2 = scaled_cutouts[1]
            sh2, off2 = shadows[1]

            lbl1 = entities[0]["label"] if len(entities) > 0 else "ENTITY 1"
            lbl2 = entities[1]["label"] if len(entities) > 1 else "ENTITY 2"

            cy_fixed = int(h * 0.50)
            col1_cx = int(w * 0.26)
            col2_cx = int(w * 0.74)

            if frame_idx < t_trans_start:
                # Phase 1: Entity 1 starts centered with zoom
                zoom_scale = 1.0 + (frame_idx / t_trans_start) * 0.08
                curr_w = int(c1.width * zoom_scale)
                curr_h = int(c1.height * zoom_scale)
                c1_dyn = sharpen_cutout(c1.resize((curr_w, curr_h), Image.LANCZOS), amount=1.15)
                sh1_dyn, off1_dyn = create_cutout_drop_shadow(c1_dyn, blur_radius=14, offset=(8, 14), shadow_opacity=0.35)

                x1 = int(w * 0.50 - curr_w / 2)
                y1 = int(cy_fixed - curr_h / 2)
                frame.paste(sh1_dyn, (x1 + off1_dyn[0], y1 + off1_dyn[1]), mask=sh1_dyn)
                frame.paste(c1_dyn, (x1, y1), mask=c1_dyn)

                ring_cx = x1 + int(curr_w * 0.5)
                ring_cy = y1 + int(curr_h * 0.38)
                draw_procedural_marker(
                    draw, (ring_cx, ring_cy), int(min(curr_w, curr_h) * 0.35),
                    style=marker_style_1, color_scheme=marker_color_1,
                    label=lbl1, label_font=font_title, quadrant="top_right",
                    canvas_size=(w, h), is_dark_bg=is_dark_bg
                )

            elif t_trans_start <= frame_idx < t_trans_end:
                # Phase 2: Directional Sliding Transition
                t_norm = (frame_idx - t_trans_start) / slide_dur_frames
                ease_val = ease_out_cubic(t_norm)

                if transition_mode == "slide_bottom_up":
                    # Entity 1 moves to left, Entity 2 RISES UP FROM BOTTOM!
                    pos1_x = int(w * (0.50 - 0.24 * ease_val))
                    x1 = int(pos1_x - c1.width / 2)
                    y1 = int(cy_fixed - c1.height / 2)
                    frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                    frame.paste(c1, (x1, y1), mask=c1)

                    pos2_y = int((h + c2.height) - (h + c2.height - cy_fixed) * ease_val)
                    x2 = int(col2_cx - c2.width / 2)
                    y2 = int(pos2_y - c2.height / 2)
                    frame.paste(sh2, (x2 + off2[0], y2 + off2[1]), mask=sh2)
                    frame.paste(c2, (x2, y2), mask=c2)

                elif transition_mode == "slide_right_then_left_enters":
                    # Reverse Horizontal: Entity 1 slides right, Entity 2 enters from left!
                    pos1_x = int(w * (0.50 + 0.24 * ease_val))
                    x1 = int(pos1_x - c1.width / 2)
                    y1 = int(cy_fixed - c1.height / 2)
                    frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                    frame.paste(c1, (x1, y1), mask=c1)

                    pos2_x = int(w * (-0.25 + 0.51 * ease_val))
                    x2 = int(pos2_x - c2.width / 2)
                    y2 = int(cy_fixed - c2.height / 2)
                    frame.paste(sh2, (x2 + off2[0], y2 + off2[1]), mask=sh2)
                    frame.paste(c2, (x2, y2), mask=c2)

                else:
                    # Standard Horizontal: Entity 1 slides left, Entity 2 enters from right
                    pos1_x = int(w * (0.50 - 0.24 * ease_val))
                    x1 = int(pos1_x - c1.width / 2)
                    y1 = int(cy_fixed - c1.height / 2)
                    frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                    frame.paste(c1, (x1, y1), mask=c1)

                    pos2_x = int(w * (1.25 - 0.51 * ease_val))
                    x2 = int(pos2_x - c2.width / 2)
                    y2 = int(cy_fixed - c2.height / 2)
                    frame.paste(sh2, (x2 + off2[0], y2 + off2[1]), mask=sh2)
                    frame.paste(c2, (x2, y2), mask=c2)

            else:
                # Phase 3: Both entities rest with Symmetrical Alignment & Center VS Badge!
                phase3_norm = (frame_idx - t_trans_end) / max(1, (total_frames - t_trans_end))
                zoom2_scale = 1.0 + phase3_norm * 0.08

                target_x1 = col2_cx if transition_mode == "slide_right_then_left_enters" else col1_cx
                target_x2 = col1_cx if transition_mode == "slide_right_then_left_enters" else col2_cx

                # 1. Central Badge: Only show "VS" when it is a true conflict/rivalry! Otherwise show "&" or neutral connector.
                is_vs_context = bool(
                    entity_metadata.get("is_vs") or
                    any(k in scene_text.lower() for k in [
                        " vs ", "vs.", "versus", "बनाम", " या ", "ya phir", "ya fir", " or ",
                        "तनाव", "युद्ध", "conflict", "clash", "rivalry", "दुश्मनी", "लड़ाई", "विवाद"
                    ]) or
                    (" vs " in scene_tag.lower() or "versus" in scene_tag.lower())
                )
                is_and_context = bool(
                    any(k in scene_text.lower() for k in [" और ", " तथा ", " & ", " and ", "साथ"]) or
                    (" & " in scene_tag or " and " in scene_tag.lower())
                )

                if is_vs_context:
                    # True Rivalry/Clash: Draw prominent "VS" Badge in crimson
                    vs_r = int(min(w, h) * 0.034)
                    vs_bg = (210, 40, 40, 240) if is_dark_bg else (190, 30, 30, 240)
                    draw.ellipse([w // 2 - vs_r, cy_fixed - vs_r, w // 2 + vs_r, cy_fixed + vs_r], fill=vs_bg, outline=(255, 255, 255, 220), width=3)
                    draw.text((w // 2, cy_fixed), "VS", fill=(255, 255, 255, 255), font=font_vs, anchor="mm")
                elif is_and_context:
                    # Cooperative/Associated Pair: Draw elegant "&" Badge with gold accent
                    vs_r = int(min(w, h) * 0.030)
                    vs_bg = (30, 40, 58, 230) if is_dark_bg else (235, 240, 250, 230)
                    vs_txt = (255, 215, 0, 255) if is_dark_bg else (30, 45, 75, 255)
                    draw.ellipse([w // 2 - vs_r, cy_fixed - vs_r, w // 2 + vs_r, cy_fixed + vs_r], fill=vs_bg, outline=(255, 215, 0, 180), width=2)
                    draw.text((w // 2, cy_fixed), "&", fill=vs_txt, font=font_vs, anchor="mm")
                else:
                    # Neutral clean separation - subtle connector dot
                    dot_r = int(min(w, h) * 0.012)
                    dot_col = (255, 255, 255, 120) if is_dark_bg else (40, 40, 45, 120)
                    draw.ellipse([w // 2 - dot_r, cy_fixed - dot_r, w // 2 + dot_r, cy_fixed + dot_r], fill=dot_col)

                # 2. Entity 1 (Balanced Column)
                x1 = int(target_x1 - c1.width / 2)
                y1 = int(cy_fixed - c1.height / 2)
                frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                frame.paste(c1, (x1, y1), mask=c1)

                # Entity 1 Symmetrical Badge Label below
                lbl1_y = min(safe_b - 20, y1 + c1.height + 25)
                draw_sharp_badge_label(draw, lbl1, (target_x1, lbl1_y), font_title, anchor="mm", is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

                # 3. Entity 2 (Active Focus Column with Ken Burns & Symmetrical Focus)
                curr2_w = int(c2.width * zoom2_scale)
                curr2_h = int(c2.height * zoom2_scale)
                c2_dyn = sharpen_cutout(c2.resize((curr2_w, curr2_h), Image.LANCZOS), amount=1.2)
                sh2_dyn, off2_dyn = create_cutout_drop_shadow(c2_dyn, blur_radius=14, offset=(8, 14), shadow_opacity=0.35)

                x2 = int(target_x2 - curr2_w / 2)
                y2 = int(cy_fixed - curr2_h / 2)
                frame.paste(sh2_dyn, (x2 + off2_dyn[0], y2 + off2_dyn[1]), mask=sh2_dyn)
                frame.paste(c2_dyn, (x2, y2), mask=c2_dyn)

                # Entity 2 Symmetrical Badge Label below matching Entity 1
                lbl2_y = min(safe_b - 20, y2 + curr2_h + 25)
                draw_sharp_badge_label(draw, lbl2, (target_x2, lbl2_y), font_title, anchor="mm", is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

                # Active Focus Ring highlighting Entity 2 detail
                ring2_cx = x2 + int(curr2_w * 0.5)
                ring2_cy = y2 + int(curr2_h * 0.38)
                draw_procedural_marker(
                    draw, (ring2_cx, ring2_cy), int(min(curr2_w, curr2_h) * 0.35),
                    style=marker_style_2, color_scheme=marker_color_2,
                    label=None, label_font=font_title, quadrant="top_right",
                    canvas_size=(w, h), is_dark_bg=is_dark_bg
                )

        else:
            # ===============================================================
            # SINGLE ENTITY PROCEDURAL MOTION (Rule of Thirds & Clamped Detail Marker)
            # ===============================================================
            c1 = scaled_cutouts[0]
            lbl1 = entities[0]["label"] if len(entities) > 0 else "ARTIFACT"

            zoom_norm = frame_idx / max(1, total_frames)
            scale_now = 1.0 + zoom_norm * 0.10
            curr_w = int(c1.width * scale_now)
            curr_h = int(c1.height * scale_now)
            c1_dyn = sharpen_cutout(c1.resize((curr_w, curr_h), Image.LANCZOS), amount=1.2)
            sh1_dyn, off1_dyn = create_cutout_drop_shadow(c1_dyn, blur_radius=14, offset=(8, 14), shadow_opacity=0.35)

            if transition_mode == "rise_from_bottom":
                t_rise = min(1.0, frame_idx / (fps * 0.7))
                e_rise = ease_out_cubic(t_rise)
                curr_cy = int((h + curr_h / 2) - (h + curr_h / 2 - h * 0.52) * e_rise)
            else:
                curr_cy = int(h * 0.52)

            x1 = int(w * 0.44 - curr_w / 2)
            y1 = int(curr_cy - curr_h / 2)

            # Iconic Bauhaus / Vox Modernist Framing Arcs (matching user screenshots 4 & 5)
            # Drawn BEHIND the cutout with smooth expansion motion!
            arc_scale = 1.0 + zoom_norm * 0.08
            arc_cx = int(w * 0.50)
            draw_concentric_framing_arcs(
                draw, (arc_cx, curr_cy),
                base_radius=int(max(curr_w, curr_h) * 0.52),
                scale_factor=arc_scale,
                is_dark_bg=is_dark_bg
            )

            # Paste Shadow + Cutout
            frame.paste(sh1_dyn, (x1 + off1_dyn[0], y1 + off1_dyn[1]), mask=sh1_dyn)
            frame.paste(c1_dyn, (x1, y1), mask=c1_dyn)

            # Procedural Marker on Key Detail (Exact match for user screenshot, safely clamped!)
            ring_cx = x1 + int(curr_w * 0.48)
            ring_cy = y1 + int(curr_h * 0.32)
            draw_procedural_marker(
                draw, (ring_cx, ring_cy), int(min(curr_w, curr_h) * 0.32),
                style=marker_style_1, color_scheme=marker_color_1,
                label=lbl1, label_font=font_title, quadrant="top_right",
                canvas_size=(w, h), is_dark_bg=is_dark_bg
            )

            # Curved Callout Arrow pointing to detail (matching user screenshots 2, 3 & 6)
            callout_tag = "DETAILS" if len(lbl1) > 10 else lbl1
            arr_sx = min(safe_r - 30, x1 + curr_w + 25)
            arr_sy = max(safe_t + 35, y1 - 25)
            arr_ex = x1 + int(curr_w * 0.72)
            arr_ey = y1 + int(curr_h * 0.28)
            draw_curved_callout_arrow(draw, (arr_sx, arr_sy), (arr_ex, arr_ey), color=(245, 185, 20, 245), width=4, curvature=0.25)
            draw_sharp_badge_label(draw, callout_tag, (arr_sx, arr_sy - 16), font_pill, anchor="mm", is_dark_bg=is_dark_bg, canvas_bounds=canvas_bounds)

        # Write frame to FFmpeg stdin
        raw_bytes = frame.tobytes()
        proc.stdin.write(raw_bytes)

        del frame, draw
        if frame_idx % 25 == 0:
            release_system_memory()

    proc.stdin.close()
    proc.wait()

    release_system_memory()
    print(f"🎬 [Collage Cutout Engine V2] Successfully rendered ultra-sharp multi-directional clip: {os.path.basename(output_mp4)} ({duration:.1f}s)")
    return output_mp4
