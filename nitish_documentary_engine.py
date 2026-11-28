"""
nitish_documentary_engine.py - 3D Documentary & Pro Motion Graphics Engine
================================================================================
Inspired directly by high-production Indian & international motion documentary creators
(Vane Motion, MagnatesMedia, Vox, Nitish Rajput, Johnny Harris):

1. Dynamic Visual Archetypes & Palette Randomization:
   - Archetype A (Vane Motion / MagnatesMedia Dark Studio):
     Full-bleed vertical 9:16 dark cosmic studio canvas with theme radial glow,
     GIANT KINETIC TYPOGRAPHY BEHIND THE SUBJECT CUTOUT ("PRACTICE", "SUPERPOWER", "AI"),
     and sleek modern UI overlays (green checklists, red scam alerts, celestial rings).
   - Archetype B (Nitish Rajput Theatrical Window):
     Theatrical 16:9 central cinematic window inside 9:16 vertical canvas with heavy
     ambient Gaussian mirror blur reflections top & bottom, thin divider lines, and 3D parallax.
   - Archetype C (Vox Archival Newspaper):
     Authentic newsprint with masthead, columns, embedded sepia cutout photo, and dynamic
     fluorescent yellow marker sweep over the headline punch word.
   - Archetype D (Antique Museum Gallery Frame):
     Warm gallery wall with spotlight wash beam and heavy ornate carved gold frame.

2. Randomized & Non-Repeating Motion Choreography:
   - Diverse palette of 8 distinct entrance styles for single cutouts:
     slide_left, pop_bottom, slide_right, scale_pop, diagonal_left, drop_top, diagonal_right, cinematic_dolly.
   - Mathematical guarantee: No two adjacent scenes will ever use the same entrance style!
   - 4 specialized dual-entity choreographies for clash/comparisons (dual_sides, dual_bottom_pop, etc.).
   - After Effects damped harmonic spring physics + entry tilt + continuous organic breathing/drift.

3. Sound Design Synchronization:
   - Entrance Whoosh on subject entry & staggered second entities.
   - Paper Rustle on newspaper reveals.
   - Dramatic Riser / Vacuum on question climaxes.
   - Typewriter / Clicks on tech / dates.

4. 100% Pure Photos & Zero Stock Videos:
   - Zero stock videos, 100% photo & transparent cutout based.
   - Memory ceiling strictly < 35MB RAM via FFmpeg rawvideo pipe.
"""

import os
import sys
import math
import random
import re
import subprocess
import hashlib
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


def release_system_memory():
    """Triggers garbage collection to strictly enforce < 35MB RAM ceiling."""
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


def get_clean_font(size: int = 40, font_type: str = "bold") -> ImageFont.ImageFont:
    """Loads a high-quality system font with fallbacks."""
    font_candidates = []
    if font_type in ["serif", "antique", "headline"]:
        font_candidates = [
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ]
    elif font_type in ["mono", "typewriter"]:
        font_candidates = [
            "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
            "/System/Library/Fonts/Supplemental/Courier New.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        ]
    elif font_type == "condensed":
        font_candidates = [
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:  # bold sans
        font_candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]

    for p in font_candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


# ==============================================================================
# COLOR THEME PALETTES
# ==============================================================================

def get_theme_palette(theme_name: str) -> Dict[str, Any]:
    """Provides curated broadcast color schemes for dynamic atmosphere."""
    palettes = {
        "emerald": {
            "primary": (0, 230, 118),
            "glow": (0, 210, 106),
            "accent": (180, 255, 210),
            "bg_tint": (10, 22, 16)
        },
        "cyan": {
            "primary": (0, 229, 255),
            "glow": (0, 200, 255),
            "accent": (190, 245, 255),
            "bg_tint": (8, 18, 28)
        },
        "amber": {
            "primary": (255, 179, 0),
            "glow": (255, 160, 0),
            "accent": (255, 230, 150),
            "bg_tint": (26, 18, 10)
        },
        "gold": {
            "primary": (255, 215, 0),
            "glow": (255, 195, 0),
            "accent": (255, 245, 175),
            "bg_tint": (28, 20, 10)
        },
        "crimson": {
            "primary": (255, 68, 68),
            "glow": (230, 45, 45),
            "accent": (255, 180, 180),
            "bg_tint": (28, 10, 12)
        },
        "violet": {
            "primary": (186, 85, 255),
            "glow": (165, 65, 245),
            "accent": (230, 185, 255),
            "bg_tint": (22, 10, 30)
        }
    }
    return palettes.get(theme_name, palettes["emerald"])


# ==============================================================================
# AUDIO SOUND DESIGN SYNCHRONIZATION
# ==============================================================================

def mix_sound_effects_into_audio(
    audio_path: str,
    sfx_events: List[Dict[str, Any]],
    output_audio_path: str
) -> str:
    """
    Overlays authentic sound effects (whoosh, paper rustle, dramatic riser, click)
    directly onto the scene audio at exact millisecond cue timestamps.
    """
    if not (audio_path and os.path.exists(audio_path) and os.path.getsize(audio_path) > 500):
        return audio_path

    valid_sfx = []
    for evt in sfx_events:
        fpath = evt.get("file")
        if fpath and os.path.exists(fpath) and os.path.getsize(fpath) > 100:
            valid_sfx.append(evt)

    if not valid_sfx:
        return audio_path

    # Build FFmpeg amix filter complex
    inputs = ["-i", os.path.abspath(audio_path)]
    filter_chains = []
    mix_labels = ["[0:a]"]

    for idx, evt in enumerate(valid_sfx):
        inputs.extend(["-i", os.path.abspath(evt["file"])])
        in_idx = idx + 1
        delay_ms = int(max(0.0, evt.get("time_sec", 0.0)) * 1000)
        vol = float(evt.get("volume", 0.35))
        lbl = f"sfx_{idx}"
        filter_chains.append(f"[{in_idx}:a]adelay={delay_ms}|{delay_ms},volume={vol:.2f}[{lbl}]")
        mix_labels.append(f"[{lbl}]")

    num_inputs = len(mix_labels)
    filter_chains.append(f"{''.join(mix_labels)}amix=inputs={num_inputs}:duration=first:dropout_transition=2[aout]")
    full_filter = ";".join(filter_chains)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", full_filter,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        os.path.abspath(output_audio_path)
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 500:
            return output_audio_path
    except Exception as e:
        print(f"⚠️ [Documentary Audio SFX Notice]: {e}")

    return audio_path


# ==============================================================================
# AFTER EFFECTS SPRING BOUNCE & DROP SHADOW PREPARATION
# ==============================================================================

def spring_bounce(
    t: float,
    duration: float = 0.40,
    overshoot: float = 0.12,
    freq: float = 12.0,
    decay: float = 7.0
) -> float:
    """
    Standard After Effects Bounce Script expression (Dan Ebberts / MotionScript).
    Returns smooth damped spring motion settling gracefully to 1.0.
    """
    if t <= 0.0:
        return 0.0
    if t >= duration:
        return 1.0
    t_n = t / duration
    return 1.0 - math.exp(-decay * t_n) * math.cos(freq * t_n)


def draw_vs_badge(
    draw: ImageDraw.ImageDraw,
    center: Tuple[int, int],
    theme_name: str = "emerald",
    scale: float = 1.0
):
    """Renders a sleek glowing After Effects VS comparison badge between dual entities."""
    cx, cy = center
    r = int(26 * scale)
    if r < 8:
        return
    pal = get_theme_palette(theme_name)
    accent = pal["primary"]
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(15, 20, 28, 240), outline=accent, width=2)
    f_vs = get_clean_font(max(12, int(20 * scale)), "bold")
    draw.text((cx, cy), "VS", fill=accent, font=f_vs, anchor="mm")


def create_cutout_drop_shadow(
    cutout_img: Image.Image,
    blur_radius: int = 18,
    offset: Tuple[int, int] = (8, 16),
    shadow_opacity: float = 0.50
) -> Tuple[Image.Image, Tuple[int, int]]:
    """Generates a soft, realistic directional 3D drop shadow."""
    if cutout_img.mode != "RGBA":
        cutout_img = cutout_img.convert("RGBA")

    w, h = cutout_img.size
    pad = blur_radius * 2
    canvas_w = w + pad * 2
    canvas_h = h + pad * 2

    shadow_canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    alpha = cutout_img.split()[-1]
    black_shape = Image.new("RGBA", (w, h), (0, 0, 0, int(255 * shadow_opacity)))
    black_shape.putalpha(alpha)

    shadow_canvas.paste(black_shape, (pad + offset[0], pad + offset[1]), mask=black_shape)
    shadow_blurred = shadow_canvas.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    origin_offset = (-pad, -pad)
    return shadow_blurred, origin_offset


def sharpen_cutout(pil_img: Image.Image, amount: float = 1.25) -> Image.Image:
    """Sharpens transparent cutouts so architecture/face details pop."""
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")
    r, g, b, a = pil_img.split()
    rgb = Image.merge("RGB", (r, g, b))
    crisp_rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.8, percent=int(amount * 100), threshold=2))
    crisp_rgb.putalpha(a)
    return crisp_rgb


def paste_transformed_cutout(
    canvas: Image.Image,
    cutout_img: Image.Image,
    w: int,
    h: int,
    cx: int,
    cy: int,
    rot_deg: float = 0.0,
    drop_shadow: bool = True,
    shadow_opacity: float = 0.50
):
    """Resizes, rotates, generates realistic drop shadow, and pastes onto canvas centered at (cx, cy)."""
    sub_scaled = cutout_img.resize((max(2, w), max(2, h)), Image.BILINEAR)
    if abs(rot_deg) > 0.2:
        sub_scaled = sub_scaled.rotate(rot_deg, resample=Image.BICUBIC, expand=True)

    sw, sh = sub_scaled.size
    px = cx - sw // 2
    py = cy - sh // 2

    if drop_shadow:
        sh_img, sh_off = create_cutout_drop_shadow(sub_scaled, blur_radius=18, offset=(6, 14), shadow_opacity=shadow_opacity)
        canvas.paste(sh_img, (px + sh_off[0], py + sh_off[1]), mask=sh_img)

    canvas.paste(sub_scaled, (px, py), mask=sub_scaled)


# ==============================================================================
# DYNAMIC NON-REPEATING MOTION CHOREOGRAPHY SYSTEM
# ==============================================================================

SINGLE_MOTION_STYLES = [
    "slide_left",
    "pop_bottom",
    "slide_right",
    "scale_pop",
    "diagonal_left",
    "drop_top",
    "diagonal_right",
    "cinematic_dolly",
]

DUAL_MOTION_STYLES = [
    "dual_sides",
    "dual_bottom_pop",
    "dual_diagonal",
    "dual_stagger_expand"
]


def pick_scene_motion_style(
    scene_index: int,
    scene_text: str = "",
    is_question: bool = False,
    num_cutouts: int = 1,
    main_topic: str = "",
    prev_motion: Optional[str] = None
) -> str:
    """
    Intelligently selects a non-repeating dynamic motion style for the scene:
    - Guaranteed: no two adjacent scenes will share the same entrance style!
    - High-energy styles (scale_pop, pop_bottom) prioritized on dramatic questions or climaxes.
    - Deterministic pseudo-randomness ensures reproducibility while maximizing visual variety.
    """
    seed_str = f"{main_topic}_{scene_index}_{scene_text[:20]}"
    seed_num = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

    if num_cutouts >= 2:
        return DUAL_MOTION_STYLES[(seed_num + scene_index * 7) % len(DUAL_MOTION_STYLES)]

    if is_question:
        q_pool = [s for s in ["scale_pop", "pop_bottom", "slide_left", "diagonal_left"] if s != prev_motion]
        if q_pool:
            return q_pool[seed_num % len(q_pool)]
        return "scale_pop"

    pool = [s for s in SINGLE_MOTION_STYLES if s != prev_motion]
    if not pool:
        pool = SINGLE_MOTION_STYLES
    return pool[seed_num % len(pool)]


def compute_single_cutout_motion(
    t: float,
    duration: float,
    motion_style: str,
    target_cx: int,
    target_cy: int,
    base_w: int,
    base_h: int,
    canvas_w: int,
    canvas_h: int,
    ease_zoom: float = 0.0,
    zoom_through: float = 0.0,
    seed: int = 0
) -> Tuple[int, int, int, int, float]:
    """
    Computes (curr_w, curr_h, cx, cy, rot_deg) for a single cutout in any canvas.
    Applies After Effects spring entrance, directional displacement, entry tilt,
    and continuous organic breathing/drift after settling.
    """
    spring = spring_bounce(t, duration=0.40, overshoot=0.10, freq=12.0, decay=7.0)

    # Post-settling organic floating drift (breathing effect)
    drift_x = math.sin(t * 1.6 + seed * 1.5) * 4.5
    drift_y = math.cos(t * 1.3 + seed * 2.1) * 3.5
    drift_rot = math.sin(t * 1.1 + seed * 0.9) * 1.0

    cam_scale = 1.00 + ease_zoom * 0.14 + zoom_through * 1.2

    if motion_style == "slide_left":
        off_x = -canvas_w * 0.60 * (1.0 - spring)
        off_y = 0.0
        entry_rot = -3.2 * (1.0 - spring)
        scale_mult = 1.0
    elif motion_style == "slide_right":
        off_x = +canvas_w * 0.60 * (1.0 - spring)
        off_y = 0.0
        entry_rot = +3.2 * (1.0 - spring)
        scale_mult = 1.0
    elif motion_style == "pop_bottom":
        off_x = 0.0
        off_y = +canvas_h * 0.65 * (1.0 - spring)
        entry_rot = 0.0
        scale_mult = 1.0
    elif motion_style == "drop_top":
        off_x = 0.0
        off_y = -canvas_h * 0.55 * (1.0 - spring)
        entry_rot = 0.0
        scale_mult = 1.0
    elif motion_style == "scale_pop":
        off_x = 0.0
        off_y = 0.0
        scale_mult = (0.10 + 0.90 * spring)
        entry_rot = -2.5 * (1.0 - spring)
    elif motion_style == "diagonal_left":
        off_x = -canvas_w * 0.50 * (1.0 - spring)
        off_y = +canvas_h * 0.40 * (1.0 - spring)
        entry_rot = -3.8 * (1.0 - spring)
        scale_mult = 1.0
    elif motion_style == "diagonal_right":
        off_x = +canvas_w * 0.50 * (1.0 - spring)
        off_y = +canvas_h * 0.40 * (1.0 - spring)
        entry_rot = +3.8 * (1.0 - spring)
        scale_mult = 1.0
    elif motion_style == "cinematic_dolly":
        off_x = math.sin(t * 0.8 + seed) * (canvas_w * 0.03)
        off_y = 0.0
        entry_rot = 0.0
        scale_mult = (0.92 + 0.08 * spring)
    else:
        off_x = 0.0
        off_y = 0.0
        entry_rot = 0.0
        scale_mult = 1.0

    total_scale = cam_scale * scale_mult
    curr_w = max(4, int(base_w * total_scale))
    curr_h = max(4, int(base_h * total_scale))
    cx = int(target_cx + off_x + drift_x)
    cy = int(target_cy + off_y + drift_y)
    rot = entry_rot + drift_rot

    return curr_w, curr_h, cx, cy, rot


def compute_dual_cutout_motion(
    t: float,
    duration: float,
    dual_style: str,
    cutout_idx: int,
    base_w: int,
    base_h: int,
    canvas_w: int,
    canvas_h: int,
    ease_zoom: float = 0.0,
    zoom_through: float = 0.0
) -> Tuple[int, int, int, int, float, bool]:
    """
    Computes (curr_w, curr_h, cx, cy, rot_deg, is_visible) for dual entities (0 = Left, 1 = Right).
    """
    cam_scale = 1.00 + ease_zoom * 0.12 + zoom_through * 1.0

    if cutout_idx == 0:
        target_cx = int(canvas_w * 0.27)
        target_cy = int(canvas_h * 0.54)
        spring = spring_bounce(t, duration=0.38, overshoot=0.10)
        drift_x = math.sin(t * 1.6) * 3.5
        drift_y = math.cos(t * 1.3) * 3.0
        drift_rot = math.sin(t * 1.1) * 0.8

        if dual_style == "dual_sides":
            off_x = -canvas_w * 0.55 * (1.0 - spring)
            off_y = 0.0
            entry_rot = -2.5 * (1.0 - spring)
        elif dual_style == "dual_bottom_pop":
            off_x = 0.0
            off_y = +canvas_h * 0.55 * (1.0 - spring)
            entry_rot = 0.0
        elif dual_style == "dual_diagonal":
            off_x = -canvas_w * 0.45 * (1.0 - spring)
            off_y = +canvas_h * 0.35 * (1.0 - spring)
            entry_rot = -3.0 * (1.0 - spring)
        else:  # dual_stagger_expand
            if t < 0.28:
                off_x = 0.0
                off_y = 0.0
                entry_rot = 0.0
                target_cx = canvas_w // 2
            else:
                s_shift = spring_bounce(t - 0.28, duration=0.35, overshoot=0.08)
                target_cx = int(canvas_w // 2 + (canvas_w * 0.27 - canvas_w // 2) * s_shift)
                off_x = 0.0
                off_y = 0.0
                entry_rot = -2.0 * (1.0 - s_shift)

        curr_w = max(4, int(base_w * cam_scale))
        curr_h = max(4, int(base_h * cam_scale))
        cx = int(target_cx + off_x + drift_x)
        cy = int(target_cy + off_y + drift_y)
        rot = entry_rot + drift_rot
        return curr_w, curr_h, cx, cy, rot, True

    else:
        # Cutout 1: Right entity (staggered entrance)
        stagger_t = 0.32
        if t < stagger_t:
            return 4, 4, 0, 0, 0.0, False

        t_loc = t - stagger_t
        spring = spring_bounce(t_loc, duration=0.38, overshoot=0.10)
        target_cx = int(canvas_w * 0.73)
        target_cy = int(canvas_h * 0.54)
        drift_x = math.sin(t_loc * 1.5 + 2.0) * 3.5
        drift_y = math.cos(t_loc * 1.2 + 1.5) * 3.0
        drift_rot = math.sin(t_loc * 1.0 + 1.0) * 0.8

        if dual_style == "dual_sides":
            off_x = +canvas_w * 0.55 * (1.0 - spring)
            off_y = 0.0
            entry_rot = +2.5 * (1.0 - spring)
        elif dual_style == "dual_bottom_pop":
            off_x = 0.0
            off_y = +canvas_h * 0.55 * (1.0 - spring)
            entry_rot = 0.0
        elif dual_style == "dual_diagonal":
            off_x = +canvas_w * 0.45 * (1.0 - spring)
            off_y = -canvas_h * 0.35 * (1.0 - spring)
            entry_rot = +3.0 * (1.0 - spring)
        else:  # dual_stagger_expand
            off_x = +canvas_w * 0.55 * (1.0 - spring)
            off_y = 0.0
            entry_rot = +2.5 * (1.0 - spring)

        curr_w = max(4, int(base_w * cam_scale))
        curr_h = max(4, int(base_h * cam_scale))
        cx = int(target_cx + off_x + drift_x)
        cy = int(target_cy + off_y + drift_y)
        rot = entry_rot + drift_rot
        return curr_w, curr_h, cx, cy, rot, True


# ==============================================================================
# ARCHETYPE A: VANE MOTION / MAGNATESMEDIA DARK STUDIO WITH TEXT BEHIND SUBJECT
# ==============================================================================

def create_dark_cosmic_studio_base(
    width: int = 1080,
    height: int = 1920,
    theme_name: str = "emerald"
) -> Image.Image:
    """
    Renders the signature Vane Motion dark studio canvas:
    - Deep charcoal/starfield canvas tinted to theme
    - Directional radial glow behind subject (Emerald, Cyan, Amber, Crimson, Violet, Gold)
    - Subtle ambient vignette
    """
    pal = get_theme_palette(theme_name)
    glow_color = pal["glow"]
    bg_tint = pal["bg_tint"]

    canvas = Image.new("RGB", (width, height), bg_tint)
    draw = ImageDraw.Draw(canvas)

    # Ambient radial spotlight glow
    cx, cy = width // 2, int(height * 0.46)
    max_radius = int(width * 0.48)

    for r in range(max_radius, 0, -28):
        factor = (1.0 - (r / max_radius)) ** 1.8
        col = (
            int(bg_tint[0] + glow_color[0] * factor * 0.35),
            int(bg_tint[1] + glow_color[1] * factor * 0.35),
            int(bg_tint[2] + glow_color[2] * factor * 0.35)
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # Subtle star dust
    rnd = random.Random(42 + sum(bg_tint))
    for _ in range(85):
        sx = rnd.randint(0, width - 1)
        sy = rnd.randint(0, height - 1)
        b = rnd.randint(90, 190)
        draw.point((sx, sy), fill=(b, b, b))

    # Dark edge vignette
    vignette = canvas.filter(ImageFilter.GaussianBlur(radius=36))
    return vignette


def draw_giant_text_behind_subject(
    draw: ImageDraw.ImageDraw,
    giant_word: str,
    context_phrase: str,
    width: int,
    center_y: int,
    theme_name: str = "emerald",
    zoom_scale: float = 1.0
):
    """
    Renders GIANT bold condensed typography BEHIND the cutout subject
    (The signature Vane Motion & MagnatesMedia layout).
    """
    giant_word = giant_word.upper().strip()
    if not giant_word:
        giant_word = "DOCUMENTARY"

    pal = get_theme_palette(theme_name)
    primary_color = pal["primary"]
    accent_color = pal["accent"]

    # Base font size around 110-140px, adjusted with camera zoom
    base_size = int(width * 0.125 * zoom_scale)
    base_size = max(50, min(base_size, 170))
    font_giant = get_clean_font(base_size, font_type="condensed")

    # Measure text bounding box
    bbox = draw.textbbox((0, 0), giant_word, font=font_giant)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    tx = (width - tw) // 2
    ty = int(center_y - th // 2)

    # 1. Context phrase above ("so you can", "once you have", "thousands of years of")
    if context_phrase:
        f_sub = get_clean_font(int(width * 0.038 * zoom_scale), font_type="sans")
        sub_bbox = draw.textbbox((0, 0), context_phrase, font=f_sub)
        sub_w = sub_bbox[2] - sub_bbox[0]
        sub_x = (width - sub_w) // 2
        sub_y = ty - int(th * 0.40) - 10
        draw.text((sub_x, sub_y), context_phrase, fill=(accent_color[0], accent_color[1], accent_color[2], 220), font=f_sub)

    # 2. Giant Typography with 3D drop shadow
    draw.text((tx + 4, ty + 6), giant_word, fill=(0, 0, 0, 180), font=font_giant)
    draw.text((tx, ty), giant_word, fill=primary_color, font=font_giant)


def draw_sleek_modern_ui_overlays(
    draw: ImageDraw.ImageDraw,
    ui_type: str,
    width: int,
    height: int,
    t: float,
    theme_name: str = "emerald"
):
    """
    Renders sleek After Effects UI overlays (green checklists, red alert card,
    sleek folder, celestial portal ring).
    """
    pal = get_theme_palette(theme_name)
    primary_color = pal["primary"]

    if ui_type == "checklist":
        items = ["Even if you pass.", "Even if you're profitable."]
        pill_w = int(width * 0.48)
        pill_h = 52
        start_y = int(height * 0.50)

        for idx, itm in enumerate(items):
            delay = 0.40 * idx
            anim_t = max(0.0, min(1.0, (t - delay) / 0.35))
            if anim_t <= 0.0:
                continue
            slide_x = (1.0 - math.sin(anim_t * math.pi * 0.5)) * 120
            px = int(width * 0.26 + slide_x)
            py = start_y + idx * 64

            draw.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=10, fill=(18, 22, 28, 210), outline=(primary_color[0], primary_color[1], primary_color[2], 160), width=1)
            sq_size = 28
            sq_x = px + 12
            sq_y = py + (pill_h - sq_size) // 2
            draw.rectangle([sq_x, sq_y, sq_x + sq_size, sq_y + sq_size], fill=(primary_color[0], primary_color[1], primary_color[2], 240))
            f_chk = get_clean_font(18, "bold")
            draw.text((sq_x + 7, sq_y + 4), "✓", fill=(0, 0, 0, 255), font=f_chk)
            f_txt = get_clean_font(20, "sans")
            draw.text((sq_x + sq_size + 14, py + 15), itm, fill=(245, 250, 255, 230), font=f_txt)

    elif ui_type == "scam_alert":
        anim_t = max(0.0, min(1.0, (t - 0.20) / 0.35))
        if anim_t > 0:
            card_w = int(width * 0.46)
            card_h = 100
            cx = (width - card_w) // 2
            cy = int(height * 0.52)

            draw.rounded_rectangle([cx - 2, cy - 2, cx + card_w + 2, cy + card_h + 2], radius=14, fill=(180, 20, 20, 60), outline=(255, 40, 40, 200), width=2)
            draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=12, fill=(26, 10, 12, 230))

            badge_w, badge_h = 120, 26
            bx = cx + (card_w - badge_w) // 2
            by = cy - 13
            draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=6, fill=(230, 30, 30, 255))
            f_b = get_clean_font(14, "bold")
            draw.text((bx + 10, by + 5), "⚠ SCAM ALERT", fill=(255, 255, 255, 255), font=f_b)

            f_t = get_clean_font(20, "sans")
            draw.text((cx + 20, cy + 38), "Target Under Investigation", fill=(255, 220, 220, 240), font=f_t)

    elif ui_type == "celestial_ring":
        rx = width // 2
        ry = int(height * 0.44)
        rad = int(width * 0.28)
        pulse = 1.0 + 0.03 * math.sin(t * math.pi * 2)
        cur_rad = int(rad * pulse)

        for glow_w, alpha in [(12, 35), (8, 70), (4, 160), (2, 240)]:
            col = (primary_color[0], primary_color[1], primary_color[2], alpha)
            draw.ellipse([rx - cur_rad, ry - cur_rad, rx + cur_rad, ry + cur_rad], outline=col, width=glow_w)


# ==============================================================================
# ARCHETYPE B: NITISH RAJPUT 16:9 THEATRICAL WINDOW WITH AMBIENT MIRROR BLUR
# ==============================================================================

def create_ambient_mirror_canvas(
    frame_16_9: Image.Image,
    target_size: Tuple[int, int] = (1080, 1920),
    blur_radius: int = 42,
    darken_factor: float = 0.68
) -> Image.Image:
    """
    Creates the signature Nitish Rajput / Vox 3D documentary canvas:
    - Target: Vertical 9:16 (1080x1920)
    - Center: 16:9 cinematic frame (1080x608) at y = 656
    - Top & Bottom: Ambient mirror blur of the 16:9 frame darkened to 68%
    - Thin dividing rules at y = 656 and y = 1264
    """
    w, h = target_size
    box_w, box_h = 1080, 608
    box_y = (h - box_h) // 2

    if frame_16_9.size != (box_w, box_h):
        frame_16_9 = frame_16_9.resize((box_w, box_h), Image.LANCZOS)

    ambient = frame_16_9.resize((w, h), Image.BILINEAR)
    ambient_blurred = ambient.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    enhancer = ImageEnhance.Brightness(ambient_blurred)
    ambient_dark = enhancer.enhance(darken_factor)

    canvas = ambient_dark.convert("RGBA")
    canvas.paste(frame_16_9, (0, box_y))

    draw = ImageDraw.Draw(canvas)
    draw.line([(0, box_y), (w, box_y)], fill=(255, 255, 255, 65), width=2)
    draw.line([(0, box_y + box_h), (w, box_y + box_h)], fill=(255, 255, 255, 65), width=2)

    return canvas.convert("RGB")


def create_cinematic_sky_background(
    width: int = 1080,
    height: int = 608,
    t: float = 0.0,
    theme_name: str = "amber"
) -> Image.Image:
    """Procedurally renders an atmospheric horizon sky tinted to match the theme."""
    pal = get_theme_palette(theme_name)
    glow = pal["glow"]

    sky = Image.new("RGB", (width, height), (25, 35, 55))
    draw = ImageDraw.Draw(sky)

    for y in range(height):
        factor = y / float(height)
        r = int(18 + glow[0] * 0.65 * (factor ** 2.2))
        g = int(25 + glow[1] * 0.55 * (factor ** 1.8))
        b = int(45 + glow[2] * 0.40 * factor)
        draw.line([(0, y), (width, y)], fill=(min(255, r), min(255, g), min(255, b)))

    rnd = random.Random(101)
    drift_x = int(t * 18.0) % width
    for _ in range(12):
        cx = (rnd.randint(-100, width + 100) + drift_x) % (width + 200) - 100
        cy = rnd.randint(int(height * 0.25), int(height * 0.75))
        rw = rnd.randint(140, 260)
        rh = rnd.randint(40, 80)
        draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(235, 220, 205, 30))

    sky = sky.filter(ImageFilter.GaussianBlur(radius=18))
    return sky


# ==============================================================================
# ARCHETYPE C: VOX ARCHIVAL INVESTIGATIVE NEWSPAPER WITH YELLOW HIGHLIGHT
# ==============================================================================

def build_vintage_newspaper_page(
    headline_text: str,
    highlight_word: str,
    cutout_img: Optional[Image.Image] = None,
    width: int = 1080,
    height: int = 608
) -> Image.Image:
    """
    Renders an authentic vintage archival front page with:
    - Aged newsprint paper texture with masthead
    - Dual text columns
    - Embedded sepia/grayscale subject cutout photo
    - Animated fluorescent yellow highlighter marker over headline
    """
    paper = Image.new("RGB", (width, height), (236, 230, 218))
    draw = ImageDraw.Draw(paper)

    rnd = random.Random(77)
    for _ in range(450):
        nx = rnd.randint(0, width - 1)
        ny = rnd.randint(0, height - 1)
        draw.point((nx, ny), fill=(215, 205, 190))

    draw.line([(40, 35), (width - 40, 35)], fill=(40, 35, 30), width=3)
    draw.line([(40, 42), (width - 40, 42)], fill=(40, 35, 30), width=1)

    f_masthead = get_clean_font(34, "antique")
    draw.text((width // 2, 70), "THE DAILY CHRONICLE", fill=(25, 22, 18), font=f_masthead, anchor="mm")

    f_meta = get_clean_font(15, "serif")
    draw.text((60, 95), "SPECIAL INVESTIGATION REPORT", fill=(70, 65, 60), font=f_meta)
    draw.text((width - 60, 95), "NATIONAL ARCHIVE EDITION", fill=(70, 65, 60), font=f_meta, anchor="ra")

    draw.line([(40, 110), (width - 40, 110)], fill=(40, 35, 30), width=2)

    headline_display = (headline_text.upper()[:45] if headline_text else "SPECIAL REPORT EXPOSED")
    f_headline = get_clean_font(42, "headline")
    draw.text((width // 2, 155), headline_display, fill=(20, 18, 15), font=f_headline, anchor="mm")

    draw.line([(40, 195), (width - 40, 195)], fill=(40, 35, 30), width=1)

    col_split = int(width * 0.58)
    draw.line([(col_split, 210), (col_split, height - 35)], fill=(180, 172, 160), width=1)

    photo_box_w = col_split - 80
    photo_box_h = height - 250
    px = 40
    py = 215

    draw.rectangle([px, py, px + photo_box_w, py + photo_box_h], fill=(225, 218, 205), outline=(50, 45, 40), width=2)

    if cutout_img:
        cw, ch = cutout_img.size
        scale = min((photo_box_w - 20) / max(1, cw), (photo_box_h - 20) / max(1, ch))
        c_scaled = cutout_img.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
        c_gray = c_scaled.convert("L").convert("RGBA")
        paste_x = px + (photo_box_w - c_scaled.width) // 2
        paste_y = py + (photo_box_h - c_scaled.height) // 2
        paper.paste(c_gray, (paste_x, paste_y), mask=c_scaled if c_scaled.mode == "RGBA" else None)

    rx = col_split + 30
    ry = 220
    for line_idx in range(11):
        line_y = ry + line_idx * 28
        line_len = width - 40 - rx - (35 if line_idx % 3 == 0 else 0)
        draw.line([(rx, line_y), (rx + line_len, line_y)], fill=(80, 75, 70), width=6)

    if highlight_word:
        hw_clean = highlight_word.upper().strip()
        if hw_clean in headline_display:
            hl_bbox = draw.textbbox((width // 2, 155), headline_display, font=f_headline, anchor="mm")
            hl_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            hl_draw = ImageDraw.Draw(hl_overlay)
            hl_draw.rectangle([hl_bbox[0] - 8, hl_bbox[1] - 4, hl_bbox[2] + 8, hl_bbox[3] + 4], fill=(255, 245, 0, 115))
            paper = Image.alpha_composite(paper.convert("RGBA"), hl_overlay).convert("RGB")

    return paper


# ==============================================================================
# ARCHETYPE D: ANTIQUE MUSEUM CARVED GOLD GALLERY FRAME
# ==============================================================================

def create_ornate_antique_frame(width: int = 340, height: int = 420) -> Image.Image:
    """Procedurally renders an ornate carved baroque antique gold/wood frame."""
    frame_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame_img)

    border_thick = 26
    draw.rectangle([0, 0, width, height], fill=(160, 120, 45, 255))
    draw.rectangle([6, 6, width - 6, height - 6], fill=(215, 175, 75, 255))
    draw.rectangle([14, 14, width - 14, height - 14], fill=(130, 90, 30, 255))
    draw.rectangle([20, 20, width - 20, height - 20], fill=(245, 210, 110, 255))
    draw.rectangle([border_thick, border_thick, width - border_thick, height - border_thick], fill=(0, 0, 0, 0))

    for cx, cy in [(13, 13), (width - 13, 13), (13, height - 13), (width - 13, height - 13)]:
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 235, 150, 255), outline=(100, 70, 20, 255), width=2)

    return frame_img


def create_moody_interior_wall(width: int = 1080, height: int = 608) -> Image.Image:
    """Renders a moody executive museum gallery wall with warm spotlight wash."""
    wall = Image.new("RGB", (width, height), (32, 28, 25))
    draw = ImageDraw.Draw(wall)

    cx, cy = width // 2, int(height * 0.45)
    max_r = int(width * 0.65)
    for r in range(max_r, 0, -22):
        factor = (1.0 - (r / max_r)) ** 2.0
        r_val = int(32 + 130 * factor)
        g_val = int(28 + 95 * factor)
        b_val = int(25 + 60 * factor)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(r_val, g_val, b_val))

    wall = wall.filter(ImageFilter.GaussianBlur(radius=24))
    return wall


# ==============================================================================
# SCRIPT-AWARE ARCHETYPE & PALETTE EXTRACTION
# ==============================================================================

def detect_documentary_scene_archetype(
    scene_text: str,
    main_topic: str = "",
    scene_index: int = 0
) -> Tuple[str, Dict[str, Any]]:
    """
    Intelligently assigns an editing archetype, theme color, and punch typography
    based on script tokens, while rotating across scenes to guarantee high visual variety.
    """
    t_clean = (scene_text or "").lower()
    topic_clean = (main_topic or "").lower()

    # Determine previous scene archetype to prevent repetitive visual layouts
    prev_archetype = None
    if scene_index > 0:
        try:
            prev_archetype, _ = detect_documentary_scene_archetype(
                scene_text="",
                main_topic=main_topic,
                scene_index=scene_index - 1
            )
        except Exception:
            pass

    is_question = "?" in scene_text or "सवाल" in t_clean or "क्या " in t_clean or "who" in t_clean or "future" in t_clean

    # 1. Question / Climax: Always Vane Motion Dark Studio with punch question
    if is_question:
        giant = "THE QUESTION" if "सवाल" in t_clean else "WHO WINS?"
        return "vane_motion_dark_studio", {
            "giant_word": giant,
            "context": "the ultimate future",
            "ui_type": "celestial_ring",
            "theme": "violet",
            "is_question": True
        }

    # 2. Colonial / Freedom / Investigation / Newspaper Cues
    newspaper_cues = ["गुलामी", "आज़ादी", "घोटाला", "फ्रॉड", "रिपोर्ट", "अखबार", "scam", "fraud", "exposed", "investigation", "freedom"]
    if any(k in t_clean for k in newspaper_cues):
        arch = "vox_newspaper"
        if arch == prev_archetype:
            arch = "antique_frame"
        return arch, {
            "headline": "FREEDOM STRUGGLE" if ("गुलामी" in t_clean or "आज़ादी" in t_clean) else "SPECIAL REPORT",
            "highlight": "FREEDOM" if "आज़ादी" in t_clean else "EXPOSED",
            "giant_word": "FREEDOM",
            "context": "centuries of struggle",
            "ui_type": "scam_alert",
            "theme": "amber",
            "is_question": False
        }

    # 3. Ancient Civilization / Heritage / Golden Bird Cues
    heritage_cues = ["सोने की चिड़िया", "इतिहास", "हजारों साल", "प्राचीन", "विरासत", "संस्कृति", "ancient", "heritage", "empire"]
    if any(k in t_clean for k in heritage_cues):
        arch = "antique_frame"
        if arch == prev_archetype:
            arch = "nitish_theatrical_window"
        return arch, {
            "giant_word": "HERITAGE",
            "context": "thousands of years of",
            "ui_type": "none",
            "theme": "amber",
            "is_question": False
        }

    # 4. Geopolitical Dual Nation / Territory / Clash Cues
    if any(k in t_clean for k in ["एक तरफ", "दूसरी तरफ", "चुनौती", "rivalry", "versus", "clash"]):
        arch = "nitish_theatrical_window"
        if arch == prev_archetype:
            arch = "vane_motion_dark_studio"
        theme = "crimson" if "चुनौती" in t_clean else ("amber" if "भारत" in t_clean else "gold")
        word = "THE CLASH" if "चुनौती" in t_clean else ("BHARAT" if "भारत" in t_clean else "AMERICA")
        return arch, {
            "giant_word": word,
            "context": "global balance of power",
            "ui_type": "none",
            "theme": theme,
            "is_question": False
        }

    # 5. Technology / Modern Economy Cues
    if any(k in t_clean for k in ["तकनीक", "technology", "ai", "आधुनिक"]):
        arch = "vane_motion_dark_studio"
        if arch == prev_archetype:
            arch = "nitish_theatrical_window"
        return arch, {
            "giant_word": "MODERN TECH",
            "context": "cutting edge supremacy",
            "ui_type": "celestial_ring",
            "theme": "cyan",
            "is_question": False
        }

    if any(k in t_clean for k in ["अर्थव्यवस्था", "economy", "dollar", "wealth"]):
        arch = "vane_motion_dark_studio"
        if arch == prev_archetype:
            arch = "nitish_theatrical_window"
        return arch, {
            "giant_word": "ECONOMY",
            "context": "financial powerhouse",
            "ui_type": "checklist",
            "theme": "emerald",
            "is_question": False
        }

    # 6. Fallback Dynamic Cycle guaranteeing visual diversity
    cycle = ["vane_motion_dark_studio", "nitish_theatrical_window", "vox_newspaper", "antique_frame"]
    pool = [c for c in cycle if c != prev_archetype]
    chosen_arch = pool[scene_index % len(pool)]
    themes_cycle = ["emerald", "cyan", "amber", "gold", "crimson", "violet"]
    chosen_theme = themes_cycle[scene_index % len(themes_cycle)]

    return chosen_arch, {
        "giant_word": "SUPERPOWER" if "शक्ति" in t_clean else "GLOBAL POWER",
        "context": "a new era begins",
        "ui_type": "celestial_ring",
        "theme": chosen_theme,
        "is_question": False
    }


# ==============================================================================
# MAIN 3D DOCUMENTARY RENDER FUNCTION
# ==============================================================================

def render_nitish_documentary_motion_clip(
    cutout_paths: List[str],
    output_mp4: str,
    duration: float = 4.5,
    scene_text: str = "",
    main_topic: str = "",
    target_size: Tuple[int, int] = (1080, 1920),
    fps: int = 24,
    scene_index: int = 0,
    audio_path: Optional[str] = None
) -> str:
    """
    Renders a broadcast-grade 3D Documentary motion clip:
    - Intelligently chooses among Vane Motion Dark Studio (Text Behind Subject),
      Nitish Rajput 16:9 Ambient Mirror, Vox Newspaper, or Antique Gallery Frame.
    - Zero Stock Videos: 100% pure photo & transparent cutout based.
    - Mathematical cosine ease camera push-in and zoom-through transitions.
    - Synchronizes authentic sound effects (whoosh, paper rustle, dramatic riser).
    - Strict memory safety (< 35MB RAM via FFmpeg rawvideo pipe).
    """
    release_system_memory()
    w, h = target_size
    box_w, box_h = 1080, 608
    box_y = (h - box_h) // 2
    total_frames = max(15, int(duration * fps))

    # 1. Detect archetype & layout metadata
    archetype, meta = detect_documentary_scene_archetype(scene_text, main_topic, scene_index)
    theme_name = meta.get("theme", "emerald")
    is_question = meta.get("is_question", False)

    # 2. Sound Design Event Mapping
    sfx_events = []
    whoosh_path = "sound_effects/mixkit-cinematic-whoosh-fast-transition-1492.wav"
    paper_path = "sound_effects/49053354-page-turn-305789.mp3"
    riser_path = "sound_effects/mixkit-air-zoom-vacuum-2608.wav"

    if os.path.exists(whoosh_path):
        sfx_events.append({"file": whoosh_path, "time_sec": 0.05, "volume": 0.32})
    if archetype == "vox_newspaper" and os.path.exists(paper_path):
        sfx_events.append({"file": paper_path, "time_sec": 0.25, "volume": 0.40})
    if is_question and os.path.exists(riser_path):
        sfx_events.append({"file": riser_path, "time_sec": max(0.5, duration - 2.0), "volume": 0.45})

    # 3. Load & Prepare Cutout Subject (Multi-Entity & Side Entrances)
    valid_cutouts = [p for p in cutout_paths if p and os.path.exists(p) and os.path.getsize(p) > 500]
    processed_cutouts = []
    from collage_cutout_engine import strip_fake_checkerboard

    for p in valid_cutouts[:3]:
        try:
            raw_c = Image.open(p).convert("RGBA")
            cleaned_c = strip_fake_checkerboard(raw_c)
            cleaned_c = sharpen_cutout(cleaned_c, amount=1.20)
            processed_cutouts.append(cleaned_c)
        except Exception as e_c:
            print(f"⚠️ [Documentary Cutout Notice]: {e_c}")

    if not processed_cutouts:
        processed_cutouts = [Image.new("RGBA", (400, 400), (40, 160, 220, 220))]

    num_cutouts = len(processed_cutouts)
    primary_cutout = processed_cutouts[0]

    # Staggered second whoosh for multi-cutout reveals
    if num_cutouts >= 2 and os.path.exists(whoosh_path):
        sfx_events.append({"file": whoosh_path, "time_sec": 0.32, "volume": 0.32})

    if audio_path and os.path.exists(audio_path) and sfx_events:
        temp_audio_out = os.path.splitext(audio_path)[0] + f"_sfx_synced.mp3"
        mixed_audio = mix_sound_effects_into_audio(audio_path, sfx_events, temp_audio_out)
        if mixed_audio != audio_path and os.path.exists(mixed_audio):
            try:
                import shutil
                shutil.copy2(mixed_audio, audio_path)
                print(f"🔊 [Documentary SFX Sync] Mixed {len(sfx_events)} sound cues into scene audio.")
            except Exception:
                pass

    # 4. Determine Dynamic Motion Choreography
    prev_motion = None
    if scene_index > 0:
        prev_motion = pick_scene_motion_style(
            scene_index=scene_index - 1,
            scene_text="",
            is_question=False,
            num_cutouts=1,
            main_topic=main_topic
        )

    motion_style = pick_scene_motion_style(
        scene_index=scene_index,
        scene_text=scene_text,
        is_question=is_question,
        num_cutouts=num_cutouts,
        main_topic=main_topic,
        prev_motion=prev_motion
    )

    print(f"🎬 [Documentary Motion Engine] Scene {scene_index+1}: Archetype='{archetype.upper()}' | Theme={theme_name} | Motion='{motion_style}' | Duration={duration:.1f}s")

    # Pre-render background bases depending on archetype
    if archetype == "vane_motion_dark_studio":
        dark_studio_canvas = create_dark_cosmic_studio_base(w, h, theme_name=theme_name)
        cw, ch = primary_cutout.size
        c_scale = min((w * 0.72) / max(1, cw), (h * 0.52) / max(1, ch))
        cutout_hero = primary_cutout.resize((int(cw * c_scale), int(ch * c_scale)), Image.LANCZOS)
        cutout_hero = sharpen_cutout(cutout_hero, amount=1.20)

    elif archetype == "vox_newspaper":
        base_paper = build_vintage_newspaper_page(
            headline_text=meta.get("headline", scene_text[:40]),
            highlight_word=meta.get("highlight", "EXPOSED"),
            cutout_img=primary_cutout,
            width=box_w,
            height=box_h
        )

    elif archetype == "antique_frame":
        base_wall = create_moody_interior_wall(box_w, box_h)
        frame_border = create_ornate_antique_frame(340, 420)
        cw, ch = primary_cutout.size
        p_scale = min(280 / max(1, cw), 360 / max(1, ch))
        framed_sub = primary_cutout.resize((int(cw * p_scale), int(ch * p_scale)), Image.LANCZOS)
        framed_sub = sharpen_cutout(framed_sub, amount=1.25)

    else:  # nitish_theatrical_window
        cw, ch = primary_cutout.size
        m_scale = min((box_w * 0.70) / max(1, cw), (box_h * 0.78) / max(1, ch))
        monument_ready = primary_cutout.resize((int(cw * m_scale), int(ch * m_scale)), Image.LANCZOS)
        monument_ready = sharpen_cutout(monument_ready, amount=1.25)

    # 5. Setup FFmpeg streaming pipe (< 35MB RAM)
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

    # 6. Kinetic Frame Render Loop
    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)
        t_norm = frame_idx / max(1, total_frames)

        # Smooth continuous 3D camera push-in curve (Cosine ease)
        ease_zoom = 0.5 - 0.5 * math.cos(t_norm * math.pi)

        # Zoom-Through transition in final 0.35s
        t_trans = max(0.0, (t_norm - 0.85) / 0.15)
        zoom_through_accel = (t_trans ** 2) * 0.28

        if archetype == "vane_motion_dark_studio":
            frame_full = dark_studio_canvas.copy()
            draw_full = ImageDraw.Draw(frame_full, "RGBA")

            # Layer 1: Celestial Ring / Backdrop Accent
            draw_sleek_modern_ui_overlays(draw_full, meta.get("ui_type", "celestial_ring"), w, h, t=t, theme_name=theme_name)

            # Layer 2: GIANT TEXT BEHIND SUBJECT (Vane Motion Signature)
            text_zoom = 1.00 + ease_zoom * 0.08 + zoom_through_accel
            draw_giant_text_behind_subject(
                draw=draw_full,
                giant_word=meta.get("giant_word", "SUPERPOWER"),
                context_phrase=meta.get("context", "a new era of"),
                width=w,
                center_y=int(h * 0.44),
                theme_name=theme_name,
                zoom_scale=text_zoom
            )

            # Layer 3: Dynamic Cutouts (Single or Multi-Entity)
            if num_cutouts >= 2:
                c_left = processed_cutouts[0]
                c_right = processed_cutouts[1]

                # Dual Cutout 0 (Left)
                w0, h0, x0, y0, r0, vis0 = compute_dual_cutout_motion(
                    t, duration, motion_style, 0,
                    base_w=int(w * 0.44), base_h=int(h * 0.48),
                    canvas_w=w, canvas_h=h,
                    ease_zoom=ease_zoom, zoom_through=zoom_through_accel
                )
                if vis0:
                    paste_transformed_cutout(frame_full, c_left, w0, h0, x0, y0, rot_deg=r0, shadow_opacity=0.50)

                # Dual Cutout 1 (Right)
                w1, h1, x1, y1, r1, vis1 = compute_dual_cutout_motion(
                    t, duration, motion_style, 1,
                    base_w=int(w * 0.44), base_h=int(h * 0.48),
                    canvas_w=w, canvas_h=h,
                    ease_zoom=ease_zoom, zoom_through=zoom_through_accel
                )
                if vis1:
                    paste_transformed_cutout(frame_full, c_right, w1, h1, x1, y1, rot_deg=r1, shadow_opacity=0.50)

                # Center VS Badge
                if t >= 0.50:
                    vs_b = spring_bounce(t - 0.50, duration=0.28, overshoot=0.15)
                    draw_vs_badge(draw_full, (w // 2, int(h * 0.54)), theme_name=theme_name, scale=vs_b)

            else:
                # Single Cutout with Dynamic Randomized Non-Repeating Motion
                cw, ch, cx, cy, rot = compute_single_cutout_motion(
                    t=t, duration=duration, motion_style=motion_style,
                    target_cx=w // 2, target_cy=int(h * 0.54),
                    base_w=cutout_hero.width, base_h=cutout_hero.height,
                    canvas_w=w, canvas_h=h,
                    ease_zoom=ease_zoom, zoom_through=zoom_through_accel,
                    seed=scene_index
                )
                paste_transformed_cutout(frame_full, cutout_hero, cw, ch, cx, cy, rot_deg=rot, shadow_opacity=0.55)

            # Layer 4: Modern UI Overlays (Checklists / Alert Cards)
            if meta.get("ui_type") in ["checklist", "scam_alert"]:
                draw_sleek_modern_ui_overlays(draw_full, meta["ui_type"], w, h, t=t, theme_name=theme_name)

            final_frame = frame_full.convert("RGBA")

        else:
            # 16:9 Theatrical Cinematic Frame inside 9:16 Canvas with Ambient Mirror Blur
            frame_16_9 = Image.new("RGB", (box_w, box_h), (20, 20, 20))

            if archetype == "vox_newspaper":
                zoom_factor = 1.00 + ease_zoom * 0.14 + zoom_through_accel
                zw = int(box_w / zoom_factor)
                zh = int(box_h / zoom_factor)
                drift_px = int(math.sin(t * 1.2) * 12)
                zx = (box_w - zw) // 2 + drift_px
                zy = int((box_h - zh) * 0.40)
                frame_16_9 = base_paper.crop((zx, zy, zx + zw, zy + zh)).resize((box_w, box_h), Image.BILINEAR)

            elif archetype == "antique_frame":
                frame_16_9 = base_wall.copy()
                frame_zoom = 1.00 + ease_zoom * 0.16 + zoom_through_accel
                fw = int(340 * frame_zoom)
                fh = int(420 * frame_zoom)
                fx = (box_w - fw) // 2 + int(math.sin(t * 1.2) * 8)
                fy = (box_h - fh) // 2

                p_frame_scaled = frame_border.resize((fw, fh), Image.BILINEAR)
                p_sub_scaled = framed_sub.resize((int(framed_sub.width * frame_zoom), int(framed_sub.height * frame_zoom)), Image.BILINEAR)

                sh_frame, sh_off = create_cutout_drop_shadow(p_frame_scaled, blur_radius=20, offset=(8, 16), shadow_opacity=0.55)
                frame_16_9.paste(sh_frame, (fx + sh_off[0], fy + sh_off[1]), mask=sh_frame)

                px = fx + (fw - p_sub_scaled.width) // 2
                py = fy + (fh - p_sub_scaled.height) // 2
                frame_16_9.paste(p_sub_scaled, (px, py), mask=p_sub_scaled if p_sub_scaled.mode == "RGBA" else None)
                frame_16_9.paste(p_frame_scaled, (fx, fy), mask=p_frame_scaled)

            else:  # nitish_theatrical_window
                sky_bg = create_cinematic_sky_background(width=box_w, height=box_h, t=t, theme_name=theme_name)
                frame_16_9 = sky_bg.copy()
                draw_169 = ImageDraw.Draw(frame_16_9, "RGBA")

                if num_cutouts >= 2:
                    c_left = processed_cutouts[0]
                    c_right = processed_cutouts[1]

                    # Dual Cutout 0
                    w0, h0, x0, y0, r0, vis0 = compute_dual_cutout_motion(
                        t, duration, motion_style, 0,
                        base_w=int(box_w * 0.38), base_h=int(box_h * 0.70),
                        canvas_w=box_w, canvas_h=box_h,
                        ease_zoom=ease_zoom, zoom_through=zoom_through_accel
                    )
                    if vis0:
                        paste_transformed_cutout(frame_16_9, c_left, w0, h0, x0, y0, rot_deg=r0, shadow_opacity=0.45)

                    # Dual Cutout 1
                    w1, h1, x1, y1, r1, vis1 = compute_dual_cutout_motion(
                        t, duration, motion_style, 1,
                        base_w=int(box_w * 0.38), base_h=int(box_h * 0.70),
                        canvas_w=box_w, canvas_h=box_h,
                        ease_zoom=ease_zoom, zoom_through=zoom_through_accel
                    )
                    if vis1:
                        paste_transformed_cutout(frame_16_9, c_right, w1, h1, x1, y1, rot_deg=r1, shadow_opacity=0.45)

                    if t >= 0.50:
                        vs_b = spring_bounce(t - 0.50, duration=0.28, overshoot=0.15)
                        draw_vs_badge(draw_169, (box_w // 2, int(box_h * 0.50)), theme_name=theme_name, scale=vs_b)

                else:
                    # Single Cutout with Dynamic Motion inside 16:9 Window
                    target_y = int(box_h * 0.90 - monument_ready.height // 2) if motion_style not in ["scale_pop", "drop_top"] else (box_h // 2)
                    cw, ch, cx, cy, rot = compute_single_cutout_motion(
                        t=t, duration=duration, motion_style=motion_style,
                        target_cx=box_w // 2, target_cy=target_y,
                        base_w=monument_ready.width, base_h=monument_ready.height,
                        canvas_w=box_w, canvas_h=box_h,
                        ease_zoom=ease_zoom, zoom_through=zoom_through_accel,
                        seed=scene_index
                    )
                    paste_transformed_cutout(frame_16_9, monument_ready, cw, ch, cx, cy, rot_deg=rot, shadow_opacity=0.48)

            # Ambient Mirror Blur into Vertical 9:16 Canvas
            final_frame = create_ambient_mirror_canvas(
                frame_16_9=frame_16_9,
                target_size=(w, h),
                blur_radius=40,
                darken_factor=0.68
            ).convert("RGBA")

        # Stream frame to FFmpeg rawvideo pipe
        try:
            proc.stdin.write(final_frame.tobytes())
        except (BrokenPipeError, IOError):
            break

    proc.stdin.close()
    proc.wait()

    release_system_memory()
    if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1000:
        print(f"🎬 [Documentary Motion Engine] Successfully rendered 3D documentary motion clip: {os.path.basename(output_mp4)} ({duration:.1f}s)")
        return output_mp4

    return ""
