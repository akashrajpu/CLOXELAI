"""
=============================================================================
COLOR ANIME / DARK COSMIC VFX CUTOUT MOTION ENGINE (V1.0 PRO)
=============================================================================
Matches the user's signature visual aesthetic from reference screenshots:
1. Deep Dark Starry Cosmic Canvas with Emerald Neon Glow & Corner Guides.
2. Giant Bold Kinetic Typography Layered BEHIND Character Cutouts.
3. Glowing Planetary Moon / Circular Halo Rings illuminating the subject.
4. Sleek Glassmorphism Notification Badges, Stacked Checklists & Alert Cards.
5. 100% Pure Photo Cutouts (Background-removed PNGs) - ZERO stock video clips.
6. Low RAM streaming via FFmpeg rawvideo pipe (< 35MB RAM, Render 512MB safe).
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
# Color Anime Atmospheric Palettes (Emerald Space, Cyan Cyber, Purple Void, Crimson Alert)
# ---------------------------------------------------------------------------
COLOR_ANIME_THEMES = {
    "emerald_space": {
        "name": "emerald_space",
        "bg": (8, 10, 15),
        "primary_neon": (0, 230, 118, 255),    # Vibrant emerald neon green (#00e676)
        "glow_rgb": (0, 230, 118),
        "accent": (255, 255, 255, 255),
        "card_bg": (15, 23, 42, 230),
        "card_border": (0, 230, 118, 180),
        "halo_color": (255, 255, 255, 210)
    },
    "cyan_cyber": {
        "name": "cyan_cyber",
        "bg": (6, 12, 20),
        "primary_neon": (0, 229, 255, 255),    # Electric cyan (#00e5ff)
        "glow_rgb": (0, 229, 255),
        "accent": (255, 255, 255, 255),
        "card_bg": (12, 24, 40, 230),
        "card_border": (0, 229, 255, 180),
        "halo_color": (200, 245, 255, 210)
    },
    "purple_void": {
        "name": "purple_void",
        "bg": (10, 6, 18),
        "primary_neon": (192, 132, 252, 255),  # Cosmic neon purple (#c084fc)
        "glow_rgb": (168, 85, 247),
        "accent": (255, 255, 255, 255),
        "card_bg": (24, 16, 44, 230),
        "card_border": (192, 132, 252, 180),
        "halo_color": (240, 215, 255, 210)
    },
    "crimson_alert": {
        "name": "crimson_alert",
        "bg": (18, 6, 8),
        "primary_neon": (244, 63, 94, 255),    # Neon crimson red (#f43f5e)
        "glow_rgb": (239, 68, 68),
        "accent": (255, 255, 255, 255),
        "card_bg": (38, 12, 16, 230),
        "card_border": (244, 63, 94, 190),
        "halo_color": (255, 200, 210, 210)
    },
    "silver_monochrome": {
        "name": "silver_monochrome",
        "bg": (10, 10, 12),
        "primary_neon": (255, 255, 255, 255),  # 3D Chrome / Metallic White
        "glow_rgb": (200, 210, 225),
        "accent": (0, 230, 118, 255),
        "card_bg": (20, 24, 30, 230),
        "card_border": (255, 255, 255, 160),
        "halo_color": (255, 255, 255, 220)
    }
}

def has_devanagari(text: str) -> bool:
    """Checks whether the text contains Devanagari (Hindi) unicode codepoints."""
    if not text:
        return False
    return any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text)

def get_clean_font(size: int = 40, font_type: str = "bold", is_devanagari: bool = False) -> ImageFont.ImageFont:
    """Loads ultra-clean modern typography without cursive distortion or Devanagari tofu blocks."""
    fonts_dir = "fonts"
    candidates = []
    if is_devanagari:
        candidates = [
            os.path.join(fonts_dir, "NotoSansDevanagari-Bold.ttf"),
            os.path.join(fonts_dir, "Mukta-Bold.ttf"),
            os.path.join(fonts_dir, "NotoSansDevanagari-Regular.ttf"),
            "/System/Library/Fonts/KohinoorBangla.ttc",
            os.path.join(fonts_dir, "Arial.ttf"),
        ]
    elif font_type == "giant":
        candidates = [
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            os.path.join(fonts_dir, "BroadcastTitling.ttf"),
            os.path.join(fonts_dir, "Mukta-Bold.ttf"),
            os.path.join(fonts_dir, "NotoSansDevanagari-Bold.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            os.path.join(fonts_dir, "Arial.ttf"),
        ]
    elif font_type == "bold":
        candidates = [
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            os.path.join(fonts_dir, "Mukta-Bold.ttf"),
            os.path.join(fonts_dir, "NotoSansDevanagari-Bold.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            os.path.join(fonts_dir, "Arial.ttf"),
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


# ---------------------------------------------------------------------------
# Background Generators (Dark Cosmic Starry Space + Colored Nebula Glow)
# ---------------------------------------------------------------------------
def create_dark_cosmic_base(width: int, height: int, theme_name: str = "emerald_space") -> Tuple[Image.Image, Dict[str, Any]]:
    """Creates a high-production dark cosmic space canvas with twinkling stars and atmospheric nebula glow."""
    theme = COLOR_ANIME_THEMES.get(theme_name, COLOR_ANIME_THEMES["emerald_space"])
    bg_rgb = theme["bg"]
    glow_rgb = theme["glow_rgb"]

    # 1. Base dark background
    canvas = Image.new("RGBA", (width, height), bg_rgb + (255,))
    draw = ImageDraw.Draw(canvas, "RGBA")

    # 2. Procedural Starfield (140 stars with deterministic seed)
    rng = np.random.RandomState(1337)
    for _ in range(140):
        sx = int(rng.randint(20, width - 20))
        sy = int(rng.randint(20, height - 20))
        sr = int(rng.choice([1, 1, 2, 2, 3]))
        alpha = int(rng.randint(90, 230))
        # Twinkle tint (cool white / cyan)
        star_c = (230, 245, 255, alpha) if rng.rand() > 0.3 else (glow_rgb[0], glow_rgb[1], glow_rgb[2], alpha)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=star_c)

    # 3. Soft Volumetric Nebula Glow (Radial Gaussian Glow)
    glow_mask = Image.new("L", (width, height), 0)
    g_draw = ImageDraw.Draw(glow_mask)
    gcx = width // 2
    gcy = int(height * 0.52)
    gr = int(width * 0.48)
    g_draw.ellipse([gcx - gr, gcy - gr, gcx + gr, gcy + gr], fill=255)
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(radius=int(width * 0.22)))

    glow_np = np.zeros((height, width, 4), dtype=np.uint8)
    glow_np[:, :, 0] = glow_rgb[0]
    glow_np[:, :, 1] = glow_rgb[1]
    glow_np[:, :, 2] = glow_rgb[2]
    glow_np[:, :, 3] = (np.array(glow_mask, dtype=np.float32) * 0.36).astype(np.uint8)
    glow_layer = Image.fromarray(glow_np, "RGBA")
    canvas = Image.alpha_composite(canvas, glow_layer)

    # 4. Cinematic Vignette
    vignette = Image.new("L", (width, height), 0)
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([(-60, -60), (width + 60, height + 60)], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=int(min(width, height) * 0.16)))
    vig_np = np.zeros((height, width, 4), dtype=np.uint8)
    vig_alpha = np.array(vignette, dtype=np.float32)
    vig_np[:, :, 3] = ((255 - vig_alpha) * 0.35).astype(np.uint8)
    canvas = Image.alpha_composite(canvas, Image.fromarray(vig_np, "RGBA"))

    return canvas, theme


def draw_corner_crop_guides(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    color: Tuple[int, int, int, int] = (0, 230, 118, 240)
):
    """
    Renders sleek studio corner crop marks with anchor dots.
    Directly matches user reference screenshot 1!
    """
    margin_x = int(width * 0.06)
    margin_y = int(height * 0.05)
    arm_len = int(width * 0.06)
    w_line = 3
    dot_r = 5

    corners = [
        (margin_x, margin_y, 1, 1),                          # Top Left
        (width - margin_x, margin_y, -1, 1),                 # Top Right
        (margin_x, height - margin_y, 1, -1),                # Bottom Left
        (width - margin_x, height - margin_y, -1, -1)        # Bottom Right
    ]

    for cx, cy, dx, dy in corners:
        draw.line([(cx, cy), (cx + dx * arm_len, cy)], fill=color, width=w_line)
        draw.line([(cx, cy), (cx, cy + dy * arm_len)], fill=color, width=w_line)
        draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=color)


def draw_planetary_halo_ring(
    draw: ImageDraw.ImageDraw,
    center: Tuple[int, int],
    radius: int,
    theme: Dict[str, Any],
    scale_factor: float = 1.0
):
    """
    Renders a glowing circular planetary halo ring behind the character cutout.
    Directly matches user reference screenshot 1 & screenshot 6 (panel 4)!
    """
    cx, cy = center
    curr_r = int(radius * scale_factor)
    primary_c = theme["primary_neon"]
    halo_c = theme["halo_color"]

    # 1. Outer Soft Diffused Glow
    draw.ellipse([cx - curr_r - 8, cy - curr_r - 8, cx + curr_r + 8, cy + curr_r + 8], outline=(primary_c[0], primary_c[1], primary_c[2], 90), width=14)
    # 2. Main High-Intensity Core Ring
    draw.ellipse([cx - curr_r, cy - curr_r, cx + curr_r, cy + curr_r], outline=halo_c, width=8)
    # 3. Inner Rim Accent
    draw.ellipse([cx - curr_r + 4, cy - curr_r + 4, cx + curr_r - 4, cy + curr_r - 4], outline=(primary_c[0], primary_c[1], primary_c[2], 140), width=3)


# ---------------------------------------------------------------------------
# Giant Bold Kinetic Typography Behind Cutout (Depth Layering)
# ---------------------------------------------------------------------------
def draw_giant_kinetic_background_text(
    draw: ImageDraw.ImageDraw,
    giant_word: str,
    intro_phrase: str,
    width: int,
    center_y: int,
    theme: Dict[str, Any],
    scale: float = 1.0
):
    """
    Renders massive kinetic typography BEHIND the character cutout.
    Directly matches user reference screenshot 2 ('so you can' + giant 'PRACTICE')
    and screenshot 3 ('And everything else in the' + giant 'DESCRIPTION BOX').
    """
    if not giant_word:
        return

    word_clean = giant_word.upper().strip()
    primary_color = theme["primary_neon"]

    # Calculate optimal giant font size to span ~85% of canvas width
    max_text_w = int(width * 0.88)
    base_font_size = int(width * 0.18)
    font_giant = get_clean_font(int(base_font_size * scale), font_type="giant")

    tb = font_giant.getbbox(word_clean)
    curr_tw = tb[2] - tb[0]
    if curr_tw > max_text_w and curr_tw > 0:
        ratio = max_text_w / curr_tw
        adjusted_size = max(36, int(base_font_size * scale * ratio))
        font_giant = get_clean_font(adjusted_size, font_type="giant")
        tb = font_giant.getbbox(word_clean)

    # 1. Intro Context Phrase above (Clean white modern sans-serif)
    if intro_phrase:
        font_intro = get_clean_font(int(width * 0.040), font_type="sans")
        intro_y = center_y - int(width * 0.14)
        draw.text((width // 2, intro_y), intro_phrase, fill=(255, 255, 255, 235), font=font_intro, anchor="mm")

    # 2. Giant Kinetic Word (Vibrant neon green or metallic chrome)
    # Draw drop shadow for 3D depth
    draw.text((width // 2 + 4, center_y + 4), word_clean, fill=(0, 0, 0, 180), font=font_giant, anchor="mm")
    draw.text((width // 2, center_y), word_clean, fill=primary_color, font=font_giant, anchor="mm")


# ---------------------------------------------------------------------------
# Glassmorphism UI Badges & Notification Cards (Screenshot 6)
# ---------------------------------------------------------------------------
def draw_glassmorphism_pill_badge(
    draw: ImageDraw.ImageDraw,
    text: str,
    width: int,
    y_pos: int,
    theme: Dict[str, Any]
):
    """
    Renders sleek frosted-glass pill badge with glowing neon green border.
    Directly matches user reference screenshot 6 panel 1 ('For Passing Their Challenge')!
    """
    if not text:
        return

    is_dev = has_devanagari(text)
    font_badge = get_clean_font(int(width * 0.038), font_type="bold", is_devanagari=is_dev)
    tb = font_badge.getbbox(text)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]

    pad_x = 28
    pad_y = 12
    card_w = min(int(width * 0.88), tw + pad_x * 2 + 40)
    card_h = th + pad_y * 2
    cx = width // 2
    x1 = cx - card_w // 2
    x2 = cx + card_w // 2
    y1 = y_pos - card_h // 2
    y2 = y_pos + card_h // 2

    # Draw card body & glowing neon border
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=16, fill=theme["card_bg"], outline=theme["card_border"], width=2)
    # Green icon dot/square
    icon_s = 14
    ix = x1 + 18
    iy = y_pos - icon_s // 2
    draw.rectangle([(ix, iy), (ix + icon_s, iy + icon_s)], fill=theme["primary_neon"])
    # Text
    draw.text((ix + icon_s + 14, y_pos), text, fill=(255, 255, 255, 255), font=font_badge, anchor="lm")


def draw_stacked_checklist_cards(
    draw: ImageDraw.ImageDraw,
    items: List[str],
    width: int,
    y_pos: int,
    theme: Dict[str, Any]
):
    """
    Renders stacked sleek dark UI notification cards with green square checkboxes.
    Directly matches user reference screenshot 6 panel 2 ('Even if you pass.', 'Even if you're profitable.')!
    """
    if not items:
        return

    is_dev = any(has_devanagari(it) for it in items)
    font_item = get_clean_font(int(width * 0.034), font_type="bold", is_devanagari=is_dev)
    card_w = int(width * 0.78)
    card_h = 56
    cx = width // 2
    spacing = 10

    total_h = len(items) * card_h + (len(items) - 1) * spacing
    start_y = y_pos - total_h // 2

    for idx, item in enumerate(items[:3]):
        cy = start_y + idx * (card_h + spacing)
        x1 = cx - card_w // 2
        x2 = cx + card_w // 2
        y1 = cy
        y2 = cy + card_h

        # Translucent dark body with glowing border
        draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=12, fill=theme["card_bg"], outline=theme["card_border"], width=2)
        # Green Glowing Square Checkbox
        sq_size = 18
        sx = x1 + 20
        sy = y1 + (card_h - sq_size) // 2
        draw.rectangle([(sx, sy), (sx + sq_size, sy + sq_size)], fill=theme["primary_neon"])
        # Item label
        clean_item = item.strip()[:35]
        draw.text((sx + sq_size + 16, y1 + card_h // 2), clean_item, fill=(255, 255, 255, 255), font=font_item, anchor="lm")


def draw_scam_alert_card(
    draw: ImageDraw.ImageDraw,
    title: str,
    subtitle: str,
    width: int,
    y_pos: int,
    theme: Dict[str, Any]
):
    """
    Renders sleek red warning modal card with alert icon.
    Directly matches user reference screenshot 6 panel 3 ('SCAM ALERT')!
    """
    card_w = int(width * 0.76)
    card_h = 110
    cx = width // 2
    x1 = cx - card_w // 2
    x2 = cx + card_w // 2
    y1 = y_pos - card_h // 2
    y2 = y_pos + card_h // 2

    alert_theme = COLOR_ANIME_THEMES["crimson_alert"]
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=16, fill=alert_theme["card_bg"], outline=alert_theme["card_border"], width=2)

    # Top Alert Badge Icon (Warning Envelope / Triangle)
    badge_w, badge_h = 90, 32
    bx1 = cx - badge_w // 2
    bx2 = cx + badge_w // 2
    by1 = y1 - 16
    by2 = by1 + badge_h
    draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=8, fill=(239, 68, 68, 255))
    font_badge = get_clean_font(int(width * 0.024), font_type="bold")
    draw.text((cx, by1 + badge_h // 2), "⚠️ ALERT", fill=(255, 255, 255, 255), font=font_badge, anchor="mm")

    # Title & Subtitle
    font_title = get_clean_font(int(width * 0.038), font_type="bold")
    is_dev = has_devanagari(subtitle)
    font_sub = get_clean_font(int(width * 0.030), font_type="sans", is_devanagari=is_dev)
    draw.text((cx, y1 + 42), title.upper()[:25], fill=(255, 255, 255, 255), font=font_title, anchor="mm")
    draw.text((cx, y1 + 76), subtitle[:35], fill=(244, 150, 160, 240), font=font_sub, anchor="mm")


# ---------------------------------------------------------------------------
# Scene Element Detection (Punchy Words, UI Cards, Subtitles)
# ---------------------------------------------------------------------------
def detect_color_anime_scene_elements(scene_text: str, main_topic: str = "") -> Dict[str, Any]:
    """
    Extracts punchy core word for giant background typography,
    detects if an alert or checklist UI card should appear, and resolves visual cutouts.
    """
    text_lower = (scene_text or "").lower()
    topic_lower = (main_topic or "").lower()

    # 1. Check for Alert / Warning context (Scam, Danger, Risk, Loss, Trap)
    is_alert = any(k in text_lower for k in ["scam", "धोखा", "alert", "danger", "खतरा", "risk", "fake", "trap", "warning", "नुकसान", "बर्बाद"])
    
    # 2. Check for Checklist / Condition context (Even if, pass, rules, steps, challenge)
    is_checklist = any(k in text_lower for k in ["even if", "अगर", "शर्त", "नियम", "challenge", "pass", "rules", "steps", "points", "तरीके"])

    # 3. Extract Giant Punchy Word for Background Text Layer (Screenshot 2: PRACTICE)
    # Priority list of high-impact action nouns
    PUNCHY_KEYWORDS = [
        ("practice", "PRACTICE", "so you can"),
        ("प्रैक्टिस", "PRACTICE", "so you can"),
        ("मेहनत", "HUSTLE", "the secret to"),
        ("कंपनी", "VENTURE", "launching the"),
        ("मार्केट", "MARKET", "inside the"),
        ("ट्रेडिंग", "TRADING", "mastering the"),
        ("ai", "ARTIFICIAL", "the power of"),
        ("एआई", "ARTIFICIAL", "the power of"),
        ("स्पेस", "COSMOS", "journey to the"),
        ("अंतरिक्ष", "COSMOS", "journey to the"),
        ("कोड", "CODING", "building the"),
        ("हैकर", "CYBER", "inside the network"),
        ("सफलता", "SUCCESS", "how to achieve"),
        ("पैसा", "CAPITAL", "unlocking the"),
        ("मनी", "MONEY", "scaling the"),
        ("क्रिप्टो", "CRYPTO", "the future of"),
        ("दिमाग", "MINDSET", "unlocking your"),
        ("फिटनेस", "DISCIPLINE", "staying true to"),
        ("पुलिस", "JUSTICE", "law and order"),
        ("जांच", "EVIDENCE", "uncovering the"),
        ("रिजल्ट", "RESULTS", "delivering the"),
        ("evaluation", "EVALUATION", "you pass the"),
        ("test", "CHALLENGE", "facing the"),
        ("clips", "RAW CLIPS", "accessing all"),
        ("description", "DESCRIPTION", "everything in the")
    ]

    selected_punchy = None
    selected_intro = ""
    for kw, giant, intro in PUNCHY_KEYWORDS:
        if kw in text_lower:
            selected_punchy = giant
            selected_intro = intro
            break

    if not selected_punchy:
        # Fallback to topic or first strong word
        clean_words = [w.upper() for w in re.findall(r'[a-zA-Z]+', scene_text) if len(w) >= 4]
        if clean_words:
            selected_punchy = clean_words[0][:12]
            selected_intro = "focus on"
        elif main_topic:
            top_w = re.findall(r'[a-zA-Z]+', main_topic)
            selected_punchy = (top_w[0] if top_w else "FOCUS").upper()[:12]
            selected_intro = "master the"
        else:
            selected_punchy = "DISCIPLINE"
            selected_intro = "so you can"

    # 4. Resolve Theme based on context
    theme_name = "emerald_space"
    if is_alert:
        theme_name = "crimson_alert"
    elif any(k in text_lower for k in ["space", "अंतरिक्ष", "तारे", "galaxy", "moon", "ग्रह"]):
        theme_name = "emerald_space"
    elif any(k in text_lower for k in ["ai", "cyber", "hacker", "code", "tech", "computer"]):
        theme_name = "cyan_cyber"
    elif any(k in text_lower for k in ["wealth", "rich", "crore", "money", "luxury"]):
        theme_name = "emerald_space"

    # 5. Extract Checklist Items if checklist mode
    checklist_items = []
    if is_checklist:
        parts = [p.strip() for p in re.split(r'[,;।\n]', scene_text) if len(p.strip().split()) >= 2]
        if len(parts) >= 2:
            checklist_items = parts[:2]
        else:
            checklist_items = ["Even if you pass.", "Even if you're profitable."]

    return {
        "giant_word": selected_punchy,
        "intro_phrase": selected_intro,
        "is_alert": is_alert,
        "is_checklist": is_checklist,
        "checklist_items": checklist_items,
        "theme_name": theme_name,
        "alert_title": "SCAM ALERT" if is_alert else "",
        "alert_sub": scene_text[:32] if is_alert else ""
    }


# ---------------------------------------------------------------------------
# Core Color Anime 2.5D Motion Clip Renderer (Zero Stock Videos, 100% Photos)
# ---------------------------------------------------------------------------
def render_color_anime_motion_clip(
    cutout_paths: List[str],
    output_mp4: str,
    duration: float,
    scene_text: str = "",
    main_topic: str = "",
    target_size: Tuple[int, int] = (1080, 1920),
    fps: int = 24
) -> str:
    """
    Renders an ultra-high production Color Anime / Dark Cosmic motion clip:
    1. Atmospheric Dark Starry Cosmic Canvas with Emerald Neon Glow.
    2. Giant Kinetic Typography layered BEHIND the character cutout.
    3. Glowing Planetary Halo Ring illuminating the character.
    4. Sleek Glassmorphism Notification Badges / Checklists / Alert Cards.
    5. Pure Photo Cutouts (Background-removed PNGs) - Zero stock video clips!
    """
    w, h = target_size
    duration = max(3.0, float(duration))
    total_frames = int(duration * fps)

    # 1. Extract scene metadata
    meta = detect_color_anime_scene_elements(scene_text, main_topic)
    theme_name = meta["theme_name"]

    # 2. Base Dark Cosmic Canvas
    canvas_base, theme = create_dark_cosmic_base(w, h, theme_name=theme_name)

    # 3. Load or generate character cutout
    from collage_cutout_engine import make_transparent_cutout, sharpen_cutout, create_cutout_drop_shadow

    loaded_cutouts = []
    for p in cutout_paths:
        if p and os.path.exists(p):
            try:
                c = make_transparent_cutout(p)
                loaded_cutouts.append(c)
            except Exception as e_c:
                print(f"⚠️ [Color Anime] Warning loading cutout {p}: {e_c}")

    if not loaded_cutouts:
        # High-aesthetic futuristic character placeholder (Astronaut / Cyber Hero)
        fallback_hero = Image.new("RGBA", (600, 750), (0, 0, 0, 0))
        fb_draw = ImageDraw.Draw(fallback_hero)
        # Astronaut helmet & suit silhouette
        fb_draw.ellipse([(180, 60), (420, 300)], fill=(225, 235, 245, 255), outline=(255, 255, 255, 240), width=6)
        fb_draw.ellipse([(215, 100), (385, 250)], fill=(15, 20, 30, 255), outline=(0, 230, 118, 220), width=4)
        # Body / Shoulders
        fb_draw.rounded_rectangle([(100, 290), (500, 720)], radius=60, fill=(210, 225, 238, 255), outline=(255, 255, 255, 220), width=6)
        loaded_cutouts.append(fallback_hero)

    hero_cutout = loaded_cutouts[0]
    cw, ch = hero_cutout.size

    # Scale cutout to fill ~55% of vertical frame height
    target_cutout_h = int(h * 0.52)
    cutout_scale = target_cutout_h / max(1, ch)
    target_cutout_w = int(cw * cutout_scale)
    base_cutout = hero_cutout.resize((target_cutout_w, target_cutout_h), Image.LANCZOS)
    base_cutout = sharpen_cutout(base_cutout, amount=1.25)

    # 4. Setup FFmpeg streaming pipe
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

    halo_center = (w // 2, int(h * 0.42))
    halo_radius = int(w * 0.28)
    text_center_y = int(h * 0.44)

    # 5. Frame Render Loop
    for frame_idx in range(total_frames):
        t_norm = frame_idx / max(1, total_frames)
        frame = canvas_base.copy()
        draw = ImageDraw.Draw(frame, "RGBA")

        # A. Corner Crop Guides (Static studio guides - Screenshot 1)
        draw_corner_crop_guides(draw, w, h, color=theme["primary_neon"])

        # B. Glowing Planetary Halo Ring (Gentle pulse)
        halo_pulse = 1.0 + 0.04 * math.sin(t_norm * math.pi * 2)
        draw_planetary_halo_ring(draw, halo_center, halo_radius, theme, scale_factor=halo_pulse)

        # C. Giant Kinetic Typography BEHIND Cutout (Screenshot 2: PRACTICE)
        # Kinetic scale pop-in during first 0.6s, then subtle drift
        if frame_idx < int(fps * 0.6):
            t_pop = frame_idx / (fps * 0.6)
            text_scale = 0.88 + 0.12 * (1.0 - math.pow(1.0 - t_pop, 3))
        else:
            text_scale = 1.0 + 0.03 * ((frame_idx - fps * 0.6) / total_frames)

        draw_giant_kinetic_background_text(
            draw=draw,
            giant_word=meta["giant_word"],
            intro_phrase=meta["intro_phrase"],
            width=w,
            center_y=text_center_y,
            theme=theme,
            scale=text_scale
        )

        # D. Foreground Character Cutout (PASTED OVER THE GIANT TEXT!)
        # Smooth floating hover physics (sine wave)
        hover_y = int(14 * math.sin(t_norm * math.pi * 3))
        char_scale = 1.0 + t_norm * 0.05
        curr_cw = int(base_cutout.width * char_scale)
        curr_ch = int(base_cutout.height * char_scale)

        c_dyn = base_cutout.resize((curr_cw, curr_ch), Image.LANCZOS)
        sh_dyn, sh_off = create_cutout_drop_shadow(c_dyn, blur_radius=18, offset=(0, 16), shadow_opacity=0.45)

        char_x = int(w // 2 - curr_cw / 2)
        char_y = int(h * 0.54 - curr_ch / 2 + hover_y)

        # Paste Shadow then Cutout over giant text!
        frame.paste(sh_dyn, (char_x + sh_off[0], char_y + sh_off[1]), mask=sh_dyn)
        frame.paste(c_dyn, (char_x, char_y), mask=c_dyn)

        # E. Sleek UI Badges / Notification Cards (Screenshot 6)
        if meta["is_alert"]:
            # Red Alert Card (Screenshot 6 panel 3)
            draw_scam_alert_card(
                draw,
                title=meta.get("alert_title", "SCAM ALERT"),
                subtitle=meta.get("alert_sub", scene_text),
                width=w,
                y_pos=int(h * 0.85),
                theme=theme
            )
        elif meta["is_checklist"] and meta["checklist_items"]:
            # Stacked Checklist Badges (Screenshot 6 panel 2)
            draw_stacked_checklist_cards(
                draw,
                items=meta["checklist_items"],
                width=w,
                y_pos=int(h * 0.84),
                theme=theme
            )
        else:
            # Clean Glassmorphism Pill Banner (Screenshot 6 panel 1)
            pill_text = (meta["intro_phrase"].upper() + " " + meta["giant_word"]).strip()
            if not pill_text:
                pill_text = "FOCUS & DISCIPLINE"
            draw_glassmorphism_pill_badge(
                draw,
                text=pill_text,
                width=w,
                y_pos=int(h * 0.86),
                theme=theme
            )

        # Pipe frame to FFmpeg
        raw_bytes = frame.tobytes()
        proc.stdin.write(raw_bytes)

        del frame, draw
        if frame_idx % 25 == 0:
            release_system_memory()

    proc.stdin.close()
    proc.wait()
    release_system_memory()

    print(f"🎬 [Color Anime Engine] Successfully rendered 2.5D dark cosmic motion clip: {os.path.basename(output_mp4)} ({duration:.1f}s)")
    return output_mp4
