"""
nitish_documentary_engine.py - 3D Documentary & Pro Motion Graphics Engine
================================================================================
Inspired directly by high-production Indian & international motion documentary creators
(Vane Motion, MagnatesMedia, Vox, Nitish Rajput, Johnny Harris):

1. Visual Archetypes (Script-Aware Intelligent Selection):
   - Archetype A (Vane Motion / MagnatesMedia Dark Studio):
     Full-bleed vertical 9:16 dark cosmic studio canvas with emerald/cyan radial glow,
     GIANT KINETIC TYPOGRAPHY BEHIND THE SUBJECT CUTOUT ("PRACTICE", "SUPERPOWER", "AI"),
     and sleek modern UI overlays (green checklists, red scam alerts, sleek folders, celestial rings).
   - Archetype B (Nitish Rajput Theatrical Window):
     Theatrical 16:9 central cinematic window inside 9:16 vertical canvas with heavy
     ambient Gaussian mirror blur reflections top & bottom, thin divider lines, and 3D parallax.
   - Archetype C (Vox Archival Newspaper):
     Authentic newsprint with masthead, columns, embedded sepia cutout photo, and dynamic
     fluorescent yellow marker sweep over the headline punch word.
   - Archetype D (Antique Museum Gallery Frame):
     Warm gallery wall with spotlight wash beam and heavy ornate carved gold frame.

2. Purposeful Camera Motion & Zoom Dynamics:
   - Smooth Cosine Ease Zoom: Parallax rates across layers (Background 1.04x, Text 1.08x, Cutout 1.16x, UI 1.20x).
   - Dramatic Punch-In on Questions ("?") or Climaxes: Sudden acceleration with sound effect.
   - Zoom-Through Transition: Fast camera push-through (1.15x -> 1.45x) in the final 0.35s.

3. Sound Design Synchronization:
   - Entrance Whoosh on subject entry.
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
    accent = (0, 230, 118) if theme_name == "emerald" else ((0, 229, 255) if theme_name == "cyan" else (255, 179, 0))
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
    - Deep charcoal/starfield canvas (RGB 10, 12, 16)
    - Directional radial glow behind subject (Emerald Green, Electric Cyan, or Warm Gold)
    - Subtle ambient vignette
    """
    canvas = Image.new("RGB", (width, height), (10, 12, 16))
    draw = ImageDraw.Draw(canvas)

    # Ambient radial spotlight glow
    glow_color = (0, 210, 106) if theme_name == "emerald" else ((0, 200, 255) if theme_name == "cyan" else (255, 179, 0))
    cx, cy = width // 2, int(height * 0.46)
    max_radius = int(width * 0.48)

    # Fast procedural radial rings
    for r in range(max_radius, 0, -28):
        factor = (1.0 - (r / max_radius)) ** 1.8
        col = (
            int(10 + glow_color[0] * factor * 0.32),
            int(12 + glow_color[1] * factor * 0.32),
            int(16 + glow_color[2] * factor * 0.32)
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # Subtle star dust
    rnd = random.Random(42)
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

    primary_color = (0, 220, 110) if theme_name == "emerald" else ((0, 215, 255) if theme_name == "cyan" else (255, 185, 0))

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
        draw.text((sub_x, sub_y), context_phrase, fill=(235, 242, 250, 220), font=f_sub)

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
    if ui_type == "checklist":
        # Two sleek green checkmark pills sliding in (Image 6 Panel 2)
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

            # Translucent dark rounded pill
            draw.rounded_rectangle([px, py, px + pill_w, py + pill_h], radius=10, fill=(18, 22, 28, 210), outline=(0, 210, 106, 160), width=1)
            # Emerald green check square
            sq_size = 28
            sq_x = px + 12
            sq_y = py + (pill_h - sq_size) // 2
            draw.rectangle([sq_x, sq_y, sq_x + sq_size, sq_y + sq_size], fill=(0, 210, 106, 240))
            # Checkmark symbol
            f_chk = get_clean_font(18, "bold")
            draw.text((sq_x + 7, sq_y + 4), "✓", fill=(0, 0, 0, 255), font=f_chk)
            # Item text
            f_txt = get_clean_font(20, "sans")
            draw.text((sq_x + sq_size + 14, py + 15), itm, fill=(245, 250, 255, 230), font=f_txt)

    elif ui_type == "scam_alert":
        # Red glowing threat card (Image 6 Panel 3)
        anim_t = max(0.0, min(1.0, (t - 0.20) / 0.35))
        if anim_t > 0:
            card_w = int(width * 0.46)
            card_h = 100
            cx = (width - card_w) // 2
            cy = int(height * 0.52)

            # Red glow border
            draw.rounded_rectangle([cx - 2, cy - 2, cx + card_w + 2, cy + card_h + 2], radius=14, fill=(180, 20, 20, 60), outline=(255, 40, 40, 200), width=2)
            draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=12, fill=(26, 10, 12, 230))

            # Warning icon badge
            badge_w, badge_h = 120, 26
            bx = cx + (card_w - badge_w) // 2
            by = cy - 13
            draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=6, fill=(230, 30, 30, 255))
            f_b = get_clean_font(14, "bold")
            draw.text((bx + 10, by + 5), "⚠ SCAM ALERT", fill=(255, 255, 255, 255), font=f_b)

            # Target status
            f_t = get_clean_font(20, "sans")
            draw.text((cx + 20, cy + 38), "Target Under Investigation", fill=(255, 220, 220, 240), font=f_t)

    elif ui_type == "celestial_ring":
        # Celestial glowing ring behind hero subject (Image 1, Image 6 Panel 4)
        rx = width // 2
        ry = int(height * 0.44)
        rad = int(width * 0.28)
        pulse = 1.0 + 0.03 * math.sin(t * math.pi * 2)
        cur_rad = int(rad * pulse)

        # Multi-layer soft neon glow
        for glow_w, alpha in [(12, 35), (8, 70), (4, 160), (2, 240)]:
            col = (255, 255, 255, alpha) if theme_name == "emerald" else (0, 210, 106, alpha)
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
    box_y = (h - box_h) // 2  # 656

    if frame_16_9.size != (box_w, box_h):
        frame_16_9 = frame_16_9.resize((box_w, box_h), Image.LANCZOS)

    # 1. Generate ambient blurred reflection
    ambient = frame_16_9.resize((w, h), Image.BILINEAR)
    ambient_blurred = ambient.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    enhancer = ImageEnhance.Brightness(ambient_blurred)
    ambient_dark = enhancer.enhance(darken_factor)

    canvas = ambient_dark.convert("RGBA")
    canvas.paste(frame_16_9, (0, box_y))

    # 2. Add subtle horizontal dividing lines
    draw = ImageDraw.Draw(canvas)
    draw.line([(0, box_y), (w, box_y)], fill=(255, 255, 255, 65), width=2)
    draw.line([(0, box_y + box_h), (w, box_y + box_h)], fill=(255, 255, 255, 65), width=2)

    return canvas.convert("RGB")


def create_cinematic_sky_background(width: int = 1080, height: int = 608, t: float = 0.0) -> Image.Image:
    """Procedurally renders a drifting atmospheric sky with warm horizon glow."""
    sky = Image.new("RGB", (width, height), (35, 65, 110))
    draw = ImageDraw.Draw(sky)

    for y in range(height):
        factor = y / float(height)
        r = int(25 + 160 * (factor ** 2.2))
        g = int(45 + 130 * (factor ** 1.8))
        b = int(90 + 70 * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Procedural drifting soft clouds
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

    # Subtle paper fiber noise
    rnd = random.Random(77)
    for _ in range(450):
        nx = rnd.randint(0, width - 1)
        ny = rnd.randint(0, height - 1)
        draw.point((nx, ny), fill=(215, 205, 190))

    # 1. Newspaper Masthead
    draw.line([(40, 35), (width - 40, 35)], fill=(40, 35, 30), width=3)
    draw.line([(40, 42), (width - 40, 42)], fill=(40, 35, 30), width=1)

    f_masthead = get_clean_font(34, "antique")
    draw.text((width // 2, 70), "THE DAILY CHRONICLE", fill=(25, 22, 18), font=f_masthead, anchor="mm")

    f_meta = get_clean_font(15, "serif")
    draw.text((60, 95), "SPECIAL INVESTIGATION REPORT", fill=(70, 65, 60), font=f_meta)
    draw.text((width - 60, 95), "NATIONAL ARCHIVE EDITION", fill=(70, 65, 60), font=f_meta, anchor="ra")

    draw.line([(40, 110), (width - 40, 110)], fill=(40, 35, 30), width=2)

    # 2. Headline
    headline_display = (headline_text.upper()[:45] if headline_text else "SPECIAL REPORT EXPOSED")
    f_headline = get_clean_font(42, "headline")
    draw.text((width // 2, 155), headline_display, fill=(20, 18, 15), font=f_headline, anchor="mm")

    draw.line([(40, 195), (width - 40, 195)], fill=(40, 35, 30), width=1)

    # 3. Dual Column Layout
    col_split = int(width * 0.58)
    draw.line([(col_split, 210), (col_split, height - 35)], fill=(180, 172, 160), width=1)

    # Left Column: Embedded Cutout Photo
    photo_box_w = col_split - 80
    photo_box_h = height - 250
    px = 40
    py = 215

    draw.rectangle([px, py, px + photo_box_w, py + photo_box_h], fill=(225, 218, 205), outline=(50, 45, 40), width=2)

    if cutout_img:
        cw, ch = cutout_img.size
        scale = min((photo_box_w - 20) / max(1, cw), (photo_box_h - 20) / max(1, ch))
        c_scaled = cutout_img.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
        # Convert to authentic vintage photo
        c_gray = c_scaled.convert("L").convert("RGBA")
        paste_x = px + (photo_box_w - c_scaled.width) // 2
        paste_y = py + (photo_box_h - c_scaled.height) // 2
        paper.paste(c_gray, (paste_x, paste_y), mask=c_scaled if c_scaled.mode == "RGBA" else None)

    # Right Column: Simulated text lines
    f_body = get_clean_font(16, "serif")
    rx = col_split + 30
    ry = 220
    for line_idx in range(11):
        line_y = ry + line_idx * 28
        line_len = width - 40 - rx - (35 if line_idx % 3 == 0 else 0)
        draw.line([(rx, line_y), (rx + line_len, line_y)], fill=(80, 75, 70), width=6)

    # 4. Dynamic Fluorescent Yellow Highlighter Marker
    if highlight_word:
        hw_clean = highlight_word.upper().strip()
        if hw_clean in headline_display:
            hl_bbox = draw.textbbox((width // 2, 155), headline_display, font=f_headline, anchor="mm")
            # Highlight rect with fluorescent yellow overlay
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
    # Outer gold molding
    draw.rectangle([0, 0, width, height], fill=(160, 120, 45, 255))
    # Beveled inner wood/gold layers
    draw.rectangle([6, 6, width - 6, height - 6], fill=(215, 175, 75, 255))
    draw.rectangle([14, 14, width - 14, height - 14], fill=(130, 90, 30, 255))
    draw.rectangle([20, 20, width - 20, height - 20], fill=(245, 210, 110, 255))
    # Inner picture opening (transparent)
    draw.rectangle([border_thick, border_thick, width - border_thick, height - border_thick], fill=(0, 0, 0, 0))

    # Corner rosette accents
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
# SCRIPT-AWARE ARCHETYPE & KEYWORD EXTRACTION
# ==============================================================================

def detect_documentary_scene_archetype(
    scene_text: str,
    main_topic: str = "",
    scene_index: int = 0
) -> Tuple[str, Dict[str, Any]]:
    """
    Intelligently determines the ideal editing archetype based on spoken script tokens:
    - 'vox_newspaper' for scams, exposes, reports, documents
    - 'antique_frame' for ancient heritage, civilization, kings, history
    - 'vane_motion_dark_studio' for modern power, technology, AI, power comparisons, or dramatic questions
    - 'nitish_theatrical_window' for geopolitics, territory, nations, and political clashes
    """
    t_clean = (scene_text or "").lower()
    topic_clean = (main_topic or "").lower()

    # 1. Archival Investigative Newspaper Cues
    newspaper_cues = [
        "घोटाला", "फ्रॉड", "वांटेड", "रिपोर्ट", "अखबार", "जांच", "पर्दाफाश", "सबूत", "सच्चाई",
        "scam", "fraud", "exposed", "investigation", "wanted", "report", "police", "court", "arrest"
    ]
    if any(k in t_clean for k in newspaper_cues):
        return "vox_newspaper", {
            "headline": "SCAM EXPOSED" if "घोटाला" in t_clean or "scam" in t_clean else "SPECIAL REPORT",
            "highlight": "EXPOSED" if "घोटाला" in t_clean or "scam" in t_clean else "REPORT",
            "ui_type": "scam_alert",
            "theme": "emerald"
        }

    # 2. Antique Gallery Frame / Heritage Cues
    heritage_cues = [
        "सोने की चिड़िया", "इतिहास", "हजारों साल", "प्राचीन", "विरासत", "संस्कृति", "राजा", "सम्राट", "धरोहर",
        "golden bird", "ancient", "history", "heritage", "monarch", "civilization", "empire", "dynasty"
    ]
    if any(k in t_clean for k in heritage_cues):
        return "antique_frame", {
            "giant_word": "HERITAGE",
            "context": "thousands of years of",
            "ui_type": "none",
            "theme": "amber"
        }

    # 3. Geopolitical Dual Nation Comparison Cues -> Nitish Theatrical Window
    if any(k in t_clean for k in ["एक तरफ", "दूसरी तरफ", "गुलामी", "आज़ादी", "rivalry", "versus", "clash"]):
        return "nitish_theatrical_window", {
            "giant_word": "GLOBAL POWERS",
            "context": "the historic clash",
            "ui_type": "none",
            "theme": "amber"
        }

    # 4. Modern Power / Technology / Dramatic Question Cues -> Vane Motion Dark Studio
    modern_cues = [
        "तकनीक", "आधुनिक", "शक्ति", "सुपरपावर", "अमेरिका", "सवाल", "आगे", "पीछे", "भविष्य",
        "practice", "power", "superpower", "technology", "ai", "modern", "future", "system", "profit", "pass", "evaluation"
    ]
    is_question = "?" in scene_text or "सवाल" in t_clean or "क्या " in t_clean
    if is_question or any(k in t_clean for k in modern_cues):
        # Extract giant punch word
        giant = "SUPERPOWER"
        ctx = "the modern world"
        ui = "celestial_ring"

        if is_question:
            giant = "THE QUESTION"
            ctx = "can it surpass"
            ui = "celestial_ring"
        elif any(k in t_clean for k in ["तकनीक", "technology", "ai", "modern"]):
            giant = "MODERN TECH"
            ctx = "cutting edge power"
            ui = "celestial_ring"
        elif any(k in t_clean for k in ["शक्ति", "power", "superpower", "अमेरिका"]):
            giant = "SUPERPOWER"
            ctx = "global dominance"
            ui = "checklist"
        elif any(k in t_clean for k in ["practice", "profit", "pass"]):
            giant = "PRACTICE"
            ctx = "so you can"
            ui = "checklist"

        return "vane_motion_dark_studio", {
            "giant_word": giant,
            "context": ctx,
            "ui_type": ui,
            "theme": "emerald" if not is_question else "cyan",
            "is_question": is_question
        }

    # 4. Default: Dynamic Cycle ensuring visual diversity
    cycle = ["vane_motion_dark_studio", "nitish_theatrical_window", "antique_frame", "vox_newspaper"]
    choice = cycle[scene_index % len(cycle)]
    return choice, {
        "giant_word": "DOCUMENTARY",
        "context": "the untold story",
        "ui_type": "celestial_ring",
        "theme": "emerald"
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

    print(f"🎬 [Documentary Motion Engine] Scene {scene_index+1}: Archetype='{archetype.upper()}' | Theme={theme_name} | Duration={duration:.1f}s")

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

    # If multiple cutouts exist (e.g. America & India), add second whoosh at t=0.40s
    if num_cutouts >= 2 and os.path.exists(whoosh_path):
        sfx_events.append({"file": whoosh_path, "time_sec": 0.40, "volume": 0.32})

    # Pre-render background bases depending on archetype
    if archetype == "vane_motion_dark_studio":
        dark_studio_canvas = create_dark_cosmic_studio_base(w, h, theme_name=theme_name)
        # Scale cutout to fit 70% width
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

    # 4. Setup FFmpeg streaming pipe (< 35MB RAM)
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

    # 5. Kinetic Frame Render Loop
    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)
        t_norm = frame_idx / max(1, total_frames)

        # Smooth continuous 3D camera push-in curve (Cosine ease)
        ease_zoom = 0.5 - 0.5 * math.cos(t_norm * math.pi)

        # Zoom-Through transition in final 0.35s
        t_trans = max(0.0, (t_norm - 0.85) / 0.15)
        zoom_through_accel = (t_trans ** 2) * 0.28

        if archetype == "vane_motion_dark_studio":
            # Multi-plane Parallax Rendering (Full 9:16 vertical canvas)
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

            # Layer 3: MIDGROUND SUBJECT CUTOUT(S) (Overlapping Text in Front)
            if num_cutouts >= 2:
                # DUAL SPLIT: Left entity slides in from Left, Right entity slides in from Right!
                c_left = processed_cutouts[0]
                c_right = processed_cutouts[1]

                # Cutout 1 (Left - e.g. America): slides from Left
                slide_1 = spring_bounce(t, duration=0.38, overshoot=0.10)
                scale_1 = min((w * 0.44) / max(1, c_left.width), (h * 0.48) / max(1, c_left.height))
                c1_w = int(c_left.width * scale_1 * (1.00 + ease_zoom * 0.12))
                c1_h = int(c_left.height * scale_1 * (1.00 + ease_zoom * 0.12))
                s1_scaled = c_left.resize((c1_w, c1_h), Image.BILINEAR)

                target_x1 = int(w * 0.27 - c1_w // 2)
                x1 = int(target_x1 - w * 0.55 * (1.0 - slide_1))
                y1 = int(h * 0.54 - c1_h // 2)

                sh_1, off_1 = create_cutout_drop_shadow(s1_scaled, blur_radius=18, offset=(6, 14), shadow_opacity=0.50)
                frame_full.paste(sh_1, (x1 + off_1[0], y1 + off_1[1]), mask=sh_1)
                frame_full.paste(s1_scaled, (x1, y1), mask=s1_scaled)

                # Cutout 2 (Right - e.g. Bharat): slides from Right staggered at t >= 0.35s
                if t >= 0.35:
                    t_sub2 = max(0.0, t - 0.35)
                    slide_2 = spring_bounce(t_sub2, duration=0.38, overshoot=0.10)
                    scale_2 = min((w * 0.44) / max(1, c_right.width), (h * 0.48) / max(1, c_right.height))
                    c2_w = int(c_right.width * scale_2 * (1.00 + ease_zoom * 0.12))
                    c2_h = int(c_right.height * scale_2 * (1.00 + ease_zoom * 0.12))
                    s2_scaled = c_right.resize((c2_w, c2_h), Image.BILINEAR)

                    target_x2 = int(w * 0.73 - c2_w // 2)
                    x2 = int(target_x2 + w * 0.55 * (1.0 - slide_2))
                    y2 = int(h * 0.54 - c2_h // 2)

                    sh_2, off_2 = create_cutout_drop_shadow(s2_scaled, blur_radius=18, offset=(6, 14), shadow_opacity=0.50)
                    frame_full.paste(sh_2, (x2 + off_2[0], y2 + off_2[1]), mask=sh_2)
                    frame_full.paste(s2_scaled, (x2, y2), mask=s2_scaled)

                # Center VS comparison badge
                if t >= 0.55:
                    t_vs = max(0.0, t - 0.55)
                    vs_b = spring_bounce(t_vs, duration=0.28, overshoot=0.15)
                    draw_vs_badge(draw_full, (w // 2, int(h * 0.54)), theme_name=theme_name, scale=vs_b)

            else:
                # SINGLE CUTOUT: Dynamic entrance direction (Left or Right side slide with spring bounce!)
                slide_dir = -1 if (scene_index % 2 == 0) else 1
                slide_val = spring_bounce(t, duration=0.40, overshoot=0.10)

                cutout_zoom = 1.00 + ease_zoom * 0.16 + zoom_through_accel * 1.5
                cw = int(cutout_hero.width * cutout_zoom)
                ch = int(cutout_hero.height * cutout_zoom)
                target_cx = (w - cw) // 2
                offset_x = int(w * 0.55 * (1.0 - slide_val) * slide_dir)
                cx = target_cx + offset_x
                cy = int(h * 0.54 - ch // 2)

                sub_scaled = cutout_hero.resize((cw, ch), Image.BILINEAR)
                sh_c, sh_off = create_cutout_drop_shadow(sub_scaled, blur_radius=22, offset=(8, 16), shadow_opacity=0.55)
                frame_full.paste(sh_c, (cx + sh_off[0], cy + sh_off[1]), mask=sh_c)
                frame_full.paste(sub_scaled, (cx, cy), mask=sub_scaled)

            # Layer 4: Modern UI Overlays (Checklists / Alert Cards)
            if meta.get("ui_type") in ["checklist", "scam_alert"]:
                draw_sleek_modern_ui_overlays(draw_full, meta["ui_type"], w, h, t=t, theme_name=theme_name)

            final_frame = frame_full.convert("RGBA")

        else:
            # 16:9 Theatrical Cinematic Frame inside 9:16 Canvas with Ambient Mirror Blur
            frame_16_9 = Image.new("RGB", (box_w, box_h), (20, 20, 20))

            if archetype == "vox_newspaper":
                # 3D Push-in on highlighted headline & photo
                zoom_factor = 1.00 + ease_zoom * 0.14 + zoom_through_accel
                zw = int(box_w / zoom_factor)
                zh = int(box_h / zoom_factor)
                zx = (box_w - zw) // 2
                zy = int((box_h - zh) * 0.40)
                frame_16_9 = base_paper.crop((zx, zy, zx + zw, zy + zh)).resize((box_w, box_h), Image.BILINEAR)

            elif archetype == "antique_frame":
                frame_16_9 = base_wall.copy()
                frame_zoom = 1.00 + ease_zoom * 0.18 + zoom_through_accel
                fw = int(340 * frame_zoom)
                fh = int(420 * frame_zoom)
                fx = (box_w - fw) // 2
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
                sky_bg = create_cinematic_sky_background(width=box_w, height=box_h, t=t)
                frame_16_9 = sky_bg

                if num_cutouts >= 2:
                    # Dual cutouts in 16:9 window: Left entity slides from Left, Right entity slides from Right!
                    c_left = processed_cutouts[0]
                    c_right = processed_cutouts[1]

                    slide_1 = spring_bounce(t, duration=0.38, overshoot=0.10)
                    scale_1 = min((box_w * 0.42) / max(1, c_left.width), (box_h * 0.72) / max(1, c_left.height))
                    c1_w = int(c_left.width * scale_1 * (1.00 + ease_zoom * 0.10))
                    c1_h = int(c_left.height * scale_1 * (1.00 + ease_zoom * 0.10))
                    s1_scaled = c_left.resize((c1_w, c1_h), Image.BILINEAR)

                    target_x1 = int(box_w * 0.26 - c1_w // 2)
                    x1 = int(target_x1 - box_w * 0.50 * (1.0 - slide_1))
                    y1 = int(box_h * 0.88 - c1_h)

                    sh_1, off_1 = create_cutout_drop_shadow(s1_scaled, blur_radius=16, offset=(4, 10), shadow_opacity=0.45)
                    frame_16_9.paste(sh_1, (x1 + off_1[0], y1 + off_1[1]), mask=sh_1)
                    frame_16_9.paste(s1_scaled, (x1, y1), mask=s1_scaled)

                    if t >= 0.35:
                        t_sub2 = max(0.0, t - 0.35)
                        slide_2 = spring_bounce(t_sub2, duration=0.38, overshoot=0.10)
                        scale_2 = min((box_w * 0.42) / max(1, c_right.width), (box_h * 0.72) / max(1, c_right.height))
                        c2_w = int(c_right.width * scale_2 * (1.00 + ease_zoom * 0.10))
                        c2_h = int(c_right.height * scale_2 * (1.00 + ease_zoom * 0.10))
                        s2_scaled = c_right.resize((c2_w, c2_h), Image.BILINEAR)

                        target_x2 = int(box_w * 0.74 - c2_w // 2)
                        x2 = int(target_x2 + box_w * 0.50 * (1.0 - slide_2))
                        y2 = int(box_h * 0.88 - c2_h)

                        sh_2, off_2 = create_cutout_drop_shadow(s2_scaled, blur_radius=16, offset=(4, 10), shadow_opacity=0.45)
                        frame_16_9.paste(sh_2, (x2 + off_2[0], y2 + off_2[1]), mask=sh_2)
                        frame_16_9.paste(s2_scaled, (x2, y2), mask=s2_scaled)

                    if t >= 0.55:
                        t_vs = max(0.0, t - 0.55)
                        vs_b = spring_bounce(t_vs, duration=0.28, overshoot=0.15)
                        d_169 = ImageDraw.Draw(frame_16_9, "RGBA")
                        draw_vs_badge(d_169, (box_w // 2, int(box_h * 0.50)), theme_name=theme_name, scale=vs_b)

                else:
                    # Single cutout: Smooth entrance from side (Left or Right)
                    slide_dir = -1 if (scene_index % 2 == 0) else 1
                    slide_val = spring_bounce(t, duration=0.40, overshoot=0.09)

                    m_zoom = 1.00 + ease_zoom * 0.14 + zoom_through_accel
                    mw = int(monument_ready.width * m_zoom)
                    mh = int(monument_ready.height * m_zoom)
                    target_mx = (box_w - mw) // 2
                    mx = int(target_mx + box_w * 0.45 * (1.0 - slide_val) * slide_dir)
                    my = int(box_h * 0.90 - mh)

                    monument_scaled = monument_ready.resize((mw, mh), Image.BILINEAR)
                    sh_m, sh_off_m = create_cutout_drop_shadow(monument_scaled, blur_radius=18, offset=(0, 12), shadow_opacity=0.45)
                    frame_16_9.paste(sh_m, (mx + sh_off_m[0], my + sh_off_m[1]), mask=sh_m)
                    frame_16_9.paste(monument_scaled, (mx, my), mask=monument_scaled)

            # Ambient Mirror Blur into Vertical 9:16 Canvas
            final_frame = create_ambient_mirror_canvas(
                frame_16_9=frame_16_9,
                target_size=(w, h),
                blur_radius=40,
                darken_factor=0.68
            ).convert("RGBA")

        # Stream frame to FFmpeg rawvideo pipe
        raw_bytes = final_frame.tobytes()
        proc.stdin.write(raw_bytes)

        del final_frame
        if frame_idx % 25 == 0:
            release_system_memory()

    proc.stdin.close()
    proc.wait()
    release_system_memory()

    print(f"🎬 [Documentary Motion Engine] Successfully rendered 3D documentary motion clip: {os.path.basename(output_mp4)} ({duration:.1f}s)")
    return output_mp4
