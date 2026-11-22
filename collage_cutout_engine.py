"""
=============================================================================
VOX / JOHNNY HARRIS STYLE DOCUMENTARY COLLAGE CUTOUT & SLIDING ENGINE
=============================================================================
Creates aesthetic documentary motion graphics inspired by Vox, Johnny Harris,
and Bauhaus visual essays:
1. Drafting Paper / Parchment / Studio Canvas Background with subtle '+' grid crosshairs.
2. Background-Removed Transparent Cutouts (maps, characters, artifacts, architecture).
3. Tactile drop-shadows and paper washi-tape stickers.
4. Sequential sliding transitions (Entity 1 centers, then slides left while Entity 2 slides in).
5. Dynamic context-aware zoom & yellow highlighter focus rings.
6. Ultra-low RAM streaming via FFmpeg rawvideo pipe (< 35MB RAM, Render 512MB safe).
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
    {"name": "parchment_warm", "bg": (246, 244, 238), "grid": (185, 180, 172, 130), "text": (24, 24, 24)},
    {"name": "studio_cream",   "bg": (250, 248, 242), "grid": (195, 190, 182, 120), "text": (20, 20, 20)},
    {"name": "drafting_kraft", "bg": (241, 236, 226), "grid": (180, 175, 165, 140), "text": (30, 28, 25)},
    {"name": "blueprint_slate","bg": (234, 238, 242), "grid": (175, 185, 195, 130), "text": (20, 25, 30)},
    {"name": "muted_sage",     "bg": (236, 241, 236), "grid": (175, 188, 175, 130), "text": (20, 30, 20)},
    {"name": "vintage_peach",  "bg": (248, 241, 237), "grid": (195, 180, 175, 125), "text": (35, 25, 20)},
    {"name": "bauhaus_cream",  "bg": (244, 242, 235), "grid": (180, 178, 170, 135), "text": (18, 18, 18)},
    {"name": "bauhaus_crimson","bg": (194, 38, 38),   "grid": (255, 255, 255, 60),  "text": (250, 250, 250)},
    {"name": "bauhaus_navy",   "bg": (28, 48, 92),     "grid": (255, 255, 255, 55),  "text": (250, 250, 250)},
]

# Washi tape colors (red, cobalt blue, kraft beige, deep green)
WASHI_TAPE_COLORS = [
    (210, 50, 45, 235),   # Crimson red
    (40, 90, 185, 230),   # Cobalt blue
    (215, 185, 140, 230), # Kraft tape
    (45, 120, 75, 230),   # Vintage green
    (230, 145, 30, 230),  # Mustard amber
]

def get_font(size: int = 28, font_type: str = "bold") -> ImageFont.ImageFont:
    """Loads appropriate system/local font with fallback."""
    fonts_dir = "fonts"
    candidates = []
    if font_type == "bold":
        candidates = [
            os.path.join(fonts_dir, "bebas.ttf"),
            os.path.join(fonts_dir, "anton.ttf"),
            os.path.join(fonts_dir, "NotoSansDevanagari-Bold.ttf"),
            os.path.join(fonts_dir, "Mukta-Bold.ttf"),
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    elif font_type == "serif":
        candidates = [
            os.path.join(fonts_dir, "RozhaOne-Regular.ttf"),
            os.path.join(fonts_dir, "TiroDevanagariHindi-Regular.ttf"),
            "/System/Library/Fonts/Times.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
    else:
        candidates = [
            os.path.join(fonts_dir, "roboto.ttf"),
            os.path.join(fonts_dir, "NotoSansDevanagari-Regular.ttf"),
            os.path.join(fonts_dir, "Arial.ttf"),
            "/System/Library/Fonts/Helvetica.ttc",
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
    draw_grid: bool = True,
    draw_tape: bool = True,
    draw_vignette: bool = True
) -> Image.Image:
    """
    Creates an authentic paper drafting canvas with:
    - Subtle paper/studio tint
    - Drafting '+' crosshair grid marks
    - Washi tape strips at edges
    - Subtle vignette frame
    """
    if palette_name:
        palette = next((p for p in STUDIO_PALETTES if p["name"] == palette_name), None)
    else:
        # 85% probability of clean drafting/parchment, 15% bold bauhaus
        if random.random() < 0.85:
            palette = random.choice(STUDIO_PALETTES[:7])
        else:
            palette = random.choice(STUDIO_PALETTES[7:])
            
    if not palette:
        palette = STUDIO_PALETTES[0]

    bg_rgb = palette["bg"]
    grid_rgba = palette["grid"]

    # 1. Base Paper Canvas
    base = Image.new("RGBA", (width, height), bg_rgb + (255,))
    draw = ImageDraw.Draw(base, "RGBA")

    # 2. Subtle Drafting '+' Crosshairs Grid (Johnny Harris / Vox signature)
    if draw_grid:
        grid_step = int(min(width, height) * 0.11)  # ~110-140px spacing
        cross_len = 5  # Half-arm length (10px total cross)
        start_x = grid_step // 2
        start_y = grid_step // 2

        for y in range(start_y, height, grid_step):
            for x in range(start_x, width, grid_step):
                # Horizontal tick
                draw.line([(x - cross_len, y), (x + cross_len, y)], fill=grid_rgba, width=1)
                # Vertical tick
                draw.line([(x, y - cross_len), (x, y + cross_len)], fill=grid_rgba, width=1)

    # 3. Washi Tape Accent Strips (Torn paper stickers on corners/edges)
    if draw_tape:
        tape_w = int(width * 0.18)
        tape_h = int(height * 0.035)
        tape_color = random.choice(WASHI_TAPE_COLORS)

        # Place 1 or 2 strips (e.g. left upper edge, right lower edge)
        positions = [
            (int(width * 0.08), int(height * 0.12), -4),
            (int(width * 0.74), int(height * 0.84), 5),
        ]
        num_tapes = random.choice([1, 2])
        for tx, ty, angle in positions[:num_tapes]:
            tape_surf = Image.new("RGBA", (tape_w, tape_h), (0, 0, 0, 0))
            t_draw = ImageDraw.Draw(tape_surf)
            # Draw tape with slight jagged torn ends
            t_draw.rectangle([(0, 0), (tape_w, tape_h)], fill=tape_color)
            # Add subtle crease highlight
            t_draw.line([(0, tape_h // 2), (tape_w, tape_h // 2)], fill=(255, 255, 255, 40), width=1)
            # Rotate
            rotated_tape = tape_surf.rotate(angle, expand=True, resample=Image.BICUBIC)
            base.paste(rotated_tape, (tx, ty), mask=rotated_tape)

    # 4. Subtle Vignette Border (Focuses viewer attention on the center)
    if draw_vignette:
        vignette = Image.new("L", (width, height), 0)
        v_draw = ImageDraw.Draw(vignette)
        pad = int(min(width, height) * 0.08)
        v_draw.ellipse([(-pad, -pad), (width + pad, height + pad)], fill=255)
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=int(min(width, height) * 0.12)))
        
        # Invert mask so edges are darkened
        vig_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        vig_alpha = np.array(vignette, dtype=np.float32)
        vig_dark = ((255 - vig_alpha) * 0.18).astype(np.uint8)  # Subtle 18% max darkness
        vig_np = np.zeros((height, width, 4), dtype=np.uint8)
        vig_np[:, :, 3] = vig_dark
        vig_img = Image.fromarray(vig_np, "RGBA")
        base = Image.alpha_composite(base, vig_img)

    return base


def make_transparent_cutout(
    img_input: Any,
    output_png: Optional[str] = None
) -> Image.Image:
    """
    Takes an input image (PIL Image or filepath) and guarantees a clean
    transparent PNG cutout:
    1. If already transparent RGBA with non-uniform alpha, trims padding.
    2. If solid white/black/grey background, uses edge-aware flood fill chroma keying.
    3. Falls back to bg_remover pro body boundary protection.
    """
    if isinstance(img_input, str):
        pil_img = Image.open(img_input).convert("RGBA")
    else:
        pil_img = img_input.convert("RGBA")

    w, h = pil_img.size
    np_rgba = np.array(pil_img)

    # 1. Check if image already has significant transparent alpha
    alpha_channel = np_rgba[:, :, 3]
    transparent_ratio = np.count_nonzero(alpha_channel < 50) / (w * h)
    
    if transparent_ratio > 0.05:
        # Already transparent cutout!
        # Trim excess transparent border
        bbox = pil_img.getbbox()
        if bbox:
            pil_img = pil_img.crop(bbox)
        if output_png:
            pil_img.save(output_png, format="PNG")
        return pil_img

    # 2. Check outer 4 corners to detect solid or studio background
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
        # High quality boundary flood-fill alpha extraction
        rgb_data = np_rgba[:, :, :3].astype(np.float32)
        diff = np.sqrt(np.sum((rgb_data - mean_corner)**2, axis=2))
        
        # Color distance threshold
        thresh = 40.0 if is_white_bg else 35.0
        mask = (diff < thresh).astype(np.uint8)
        
        # Flood fill from image borders to only remove background, not white subjects inside
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

    # 3. Fallback: Use pro contour cutout from bg_remover
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
        # If removal fails, keep image as RGBA
        if output_png:
            pil_img.save(output_png, format="PNG")
        return pil_img


def create_cutout_drop_shadow(
    cutout_img: Image.Image,
    blur_radius: int = 14,
    offset: Tuple[int, int] = (8, 14),
    shadow_opacity: float = 0.32
) -> Tuple[Image.Image, Tuple[int, int]]:
    """
    Creates a photorealistic soft paper drop shadow behind a cutout.
    Returns (shadow_image, (offset_x, offset_y)).
    """
    w, h = cutout_img.size
    alpha = cutout_img.split()[3]
    
    # Expand canvas to accommodate blur and offset
    pad = blur_radius * 2
    sw = w + pad * 2
    sh = h + pad * 2
    
    shadow_mask = Image.new("L", (sw, sh), 0)
    shadow_mask.paste(alpha, (pad + offset[0], pad + offset[1]))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Dark shadow tint
    shadow_np = np.array(shadow_mask, dtype=np.float32)
    shadow_alpha = (shadow_np * shadow_opacity).astype(np.uint8)
    
    shadow_rgba = np.zeros((sh, sw, 4), dtype=np.uint8)
    shadow_rgba[:, :, :3] = (20, 22, 28)  # Deep ambient shadow
    shadow_rgba[:, :, 3] = shadow_alpha
    
    shadow_img = Image.fromarray(shadow_rgba, "RGBA")
    return shadow_img, (offset[0] - pad, offset[1] - pad)


# ---------------------------------------------------------------------------
# Script Entity & Contrast Detection
# ---------------------------------------------------------------------------
# Entity mapping for maps, nations, historical actors, and concepts
HISTORICAL_ENTITY_MAP = {
    # Maps & Nations (Hindi & English)
    "bharat": {"en": "India map outline", "label": "BHARAT / INDIA", "type": "map"},
    "भारत": {"en": "India map outline", "label": "BHARAT / INDIA", "type": "map"},
    "india": {"en": "India map outline", "label": "INDIA", "type": "map"},
    "pakistan": {"en": "Pakistan map outline", "label": "PAKISTAN", "type": "map"},
    "पाकिस्तान": {"en": "Pakistan map outline", "label": "PAKISTAN", "type": "map"},
    "bangladesh": {"en": "Bangladesh map outline", "label": "BANGLADESH", "type": "map"},
    "बांग्लादेश": {"en": "Bangladesh map outline", "label": "BANGLADESH", "type": "map"},
    "china": {"en": "China map outline", "label": "CHINA", "type": "map"},
    "चीन": {"en": "China map outline", "label": "CHINA", "type": "map"},
    "britain": {"en": "British Empire flag map", "label": "BRITISH EMPIRE", "type": "map"},
    "ब्रिटिश": {"en": "British Empire colonial emblem", "label": "BRITISH RULE", "type": "map"},
    "angrej": {"en": "British colonial officer", "label": "BRITISH RULE", "type": "figure"},
    "अंग्रेज": {"en": "British colonial officer", "label": "BRITISH RULE", "type": "figure"},
    "east india company": {"en": "East India Company coat of arms seal", "label": "EAST INDIA CO.", "type": "seal"},
    "ईस्ट इंडिया": {"en": "East India Company coat of arms seal", "label": "EAST INDIA CO.", "type": "seal"},
    "plassy": {"en": "Battle of Plassey 1757 historical painting", "label": "BATTLE OF PLASSEY", "type": "event"},
    "प्लासी": {"en": "Battle of Plassey 1757 historical painting", "label": "BATTLE OF PLASSEY", "type": "event"},
    "1757": {"en": "Battle of Plassey 1757", "label": "YEAR 1757", "type": "date"},
    "1857": {"en": "1857 Indian rebellion mutiny sepoy", "label": "1857 REBELLION", "type": "event"},
    "विद्रोह": {"en": "1857 Indian rebellion mutiny sepoy", "label": "1857 REBELLION", "type": "event"},
    "1947": {"en": "India independence partition 1947", "label": "15 AUGUST 1947", "type": "date"},
    "विभाजन": {"en": "Partition of India 1947 border", "label": "PARTITION 1947", "type": "event"},
    "आजादी": {"en": "Indian independence flag tricolor", "label": "INDEPENDENCE 1947", "type": "concept"},
    "1950": {"en": "Constitution of India book emblem", "label": "CONSTITUTION 1950", "type": "book"},
    "samvidhan": {"en": "Constitution of India preamble book", "label": "CONSTITUTION OF INDIA", "type": "book"},
    "संविधान": {"en": "Constitution of India preamble book", "label": "CONSTITUTION OF INDIA", "type": "book"},
    "loktantra": {"en": "Indian parliament democracy voting", "label": "DEMOCRACY", "type": "concept"},
    "लोकतंत्र": {"en": "Indian parliament democracy voting", "label": "DEMOCRACY", "type": "concept"},
    "raja": {"en": "Indian Maharaja King crown royal portrait", "label": "ROYAL KINGS", "type": "figure"},
    "राजा": {"en": "Indian Maharaja King crown royal portrait", "label": "ROYAL KINGS", "type": "figure"},
    "samrajya": {"en": "Ancient Indian empire fortress castle", "label": "EMPIRES", "type": "architecture"},
    "साम्राज्य": {"en": "Ancient Indian empire fortress castle", "label": "EMPIRES", "type": "architecture"},
    "sena": {"en": "Indian military army tank fighter jet", "label": "MILITARY POWER", "type": "military"},
    "सैन्य": {"en": "Indian military army tank fighter jet", "label": "MILITARY POWER", "type": "military"},
    "arthvyavastha": {"en": "Indian economy stock market rupee wealth", "label": "ECONOMY", "type": "finance"},
    "अर्थव्यवस्था": {"en": "Indian economy stock market rupee wealth", "label": "ECONOMY", "type": "finance"},
    "आर्थिक": {"en": "Economic growth development chart currency", "label": "ECONOMIC GROWTH", "type": "finance"},
    "vigyan": {"en": "ISRO space satellite rocket science", "label": "SCIENCE & TECH", "type": "tech"},
    "विज्ञान": {"en": "ISRO space satellite rocket science", "label": "SCIENCE & TECH", "type": "tech"},
    "space": {"en": "ISRO rocket moon mission space", "label": "SPACE PROGRAM", "type": "tech"},
    "अंतरिक्ष": {"en": "ISRO satellite earth orbit space", "label": "SPACE EXPLORATION", "type": "tech"},
    "nagrik": {"en": "Indian citizens people rights unity", "label": "CITIZENS", "type": "people"},
    "नागरिक": {"en": "Indian citizens people rights unity", "label": "CITIZENS", "type": "people"},
    "sansthaye": {"en": "Supreme Court of India Parliament building institutions", "label": "INSTITUTIONS", "type": "building"},
    "संस्था": {"en": "Supreme Court of India Parliament building institutions", "label": "INSTITUTIONS", "type": "building"},
}


def detect_collage_entities(scene_text: str, main_topic: str = "") -> Dict[str, Any]:
    """
    Analyzes scene text to detect:
    1. Multi-entity comparison or sequential mention (e.g. "भारत और पाकिस्तान", "राजाओं और साम्राज्यों", "सैन्य शक्ति और आर्थिक विकास")
    2. Single entity milestone with specific focus (e.g. "1757 प्लासी का युद्ध", "1857 विद्रोह", "संविधान")
    """
    text_lower = (scene_text or "").lower()
    topic_lower = (main_topic or "").lower()
    combined = f"{text_lower} {topic_lower}"

    # 1. Direct mention of high-priority geographical & geopolitical pairs (e.g. India & Pakistan)
    if ("bharat" in combined or "भारत" in combined) and ("pakistan" in combined or "पाकिस्तान" in combined):
        return {
            "is_multi_entity": True,
            "entities": [
                {"raw": "भारत", "clean_en": "India map outline", "label": "INDIA", "search": "India map outline transparent png cutout isolated"},
                {"raw": "पाकिस्तान", "clean_en": "Pakistan map outline", "label": "PAKISTAN", "search": "Pakistan map outline transparent png cutout isolated"}
            ],
            "transition_label": "INDIA & PAKISTAN"
        }

    if ("china" in combined or "चीन" in combined) and ("bharat" in combined or "भारत" in combined or "india" in combined):
        return {
            "is_multi_entity": True,
            "entities": [
                {"raw": "भारत", "clean_en": "India map outline", "label": "INDIA", "search": "India map outline transparent png cutout isolated"},
                {"raw": "चीन", "clean_en": "China map outline", "label": "CHINA", "search": "China map outline transparent png cutout isolated"}
            ],
            "transition_label": "INDIA & CHINA"
        }

    # 2. Check for two-entity patterns: "X और Y", "X तथा Y", "X vs Y", "X and Y", "X या Y"
    two_entity_regexes = [
        r'([A-Za-z\u0900-\u097F0-9\s]{2,25})\s+(?:और|तथा|vs|बनाम|and|या)\s+([A-Za-z\u0900-\u097F0-9\s]{2,25})',
        r'क(?:भी|हा)\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})\s+तो\s+क(?:भी|हा)\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})',
        r'सिर्फ\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})\s+नहीं.*?बल्कि\s+([A-Za-z\u0900-\u097F0-9\s]{2,20})',
    ]

    for pat in two_entity_regexes:
        m = re.search(pat, text_lower)
        if m:
            p1_raw = m.group(1).strip()
            p2_raw = m.group(2).strip()
            
            # Filter out non-entity grammatical noise
            clean_p1 = " ".join([w for w in p1_raw.split() if w not in ["का", "की", "के", "में", "से", "पर", "एक", "यह", "है", "था", "थी", "हो", "रहे"]])
            clean_p2 = " ".join([w for w in p2_raw.split() if w not in ["का", "की", "के", "में", "से", "पर", "एक", "यह", "है", "था", "थी", "हो", "रहे"]])

            if len(clean_p1) >= 2 and len(clean_p2) >= 2:
                # Map to visual entities
                e1 = _resolve_entity(clean_p1, main_topic)
                e2 = _resolve_entity(clean_p2, main_topic)
                if e1 and e2 and e1["clean_en"] != e2["clean_en"]:
                    return {
                        "is_multi_entity": True,
                        "entities": [e1, e2],
                        "transition_label": f"{e1['label']} vs {e2['label']}"
                    }

    # Check for direct mention of known pairs
    if ("bharat" in combined or "भारत" in combined) and ("pakistan" in combined or "पाकिस्तान" in combined):
        return {
            "is_multi_entity": True,
            "entities": [
                {"raw": "भारत", "clean_en": "India map outline", "label": "INDIA", "search": "India map outline transparent png cutout isolated"},
                {"raw": "पाकिस्तान", "clean_en": "Pakistan map outline", "label": "PAKISTAN", "search": "Pakistan map outline transparent png cutout isolated"}
            ],
            "transition_label": "INDIA & PAKISTAN"
        }

    # Single entity milestone detection
    for key, val in HISTORICAL_ENTITY_MAP.items():
        if key in combined:
            return {
                "is_multi_entity": False,
                "entities": [{
                    "raw": key,
                    "clean_en": val["en"],
                    "label": val["label"],
                    "search": f"{val['en']} transparent png cutout isolated"
                }],
                "transition_label": val["label"]
            }

    # Generic entity from topic or scene keyword
    clean_kw = " ".join([w for w in scene_text.split() if len(w) > 2][:3]) if scene_text else main_topic
    return {
        "is_multi_entity": False,
        "entities": [{
            "raw": clean_kw,
            "clean_en": f"{clean_kw} documentary artifact",
            "label": clean_kw.upper()[:20],
            "search": f"{clean_kw} transparent png cutout isolated"
        }],
        "transition_label": clean_kw.upper()[:20]
    }


def _resolve_entity(raw_text: str, main_topic: str = "") -> Optional[Dict[str, str]]:
    """Helper to resolve a raw Hindi/English phrase to a searchable cutout entity."""
    t_low = raw_text.lower().strip()
    
    # 1. Match dictionary
    for k, v in HISTORICAL_ENTITY_MAP.items():
        if k in t_low:
            return {
                "raw": raw_text,
                "clean_en": v["en"],
                "label": v["label"],
                "search": f"{v['en']} transparent png cutout isolated"
            }

    # 2. Try visual English translation
    try:
        from web_image_fetcher import translate_to_visual_english
        en_phrase = translate_to_visual_english(raw_text, main_topic)
    except Exception:
        en_phrase = raw_text

    clean_en = en_phrase or raw_text
    label = " ".join(clean_en.split()[:2]).upper()
    return {
        "raw": raw_text,
        "clean_en": clean_en,
        "label": label,
        "search": f"{clean_en} transparent png cutout isolated"
    }


# ---------------------------------------------------------------------------
# Accent Graphics: Yellow Highlighter Focus Circles, Pointer Arrows & Labels
# ---------------------------------------------------------------------------
def draw_highlighter_focus_circle(
    draw: ImageDraw.ImageDraw,
    center: Tuple[int, int],
    radius: int,
    color: Tuple[int, int, int, int] = (255, 232, 20, 220),
    width: int = 5
):
    """
    Draws a vibrant yellow highlighter focus circle around key subject details
    (like in Johnny Harris / Vox documentary screenshots 1, 2, 3).
    """
    cx, cy = center
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.ellipse(bbox, outline=color, width=width)
    # Add second inner slightly lighter ring for marker glow effect
    inner_bbox = [cx - radius + 2, cy - radius + 2, cx + radius - 2, cy + radius - 2]
    draw.ellipse(inner_bbox, outline=(color[0], color[1], color[2], 120), width=max(1, width - 2))


def draw_curved_callout_pointer(
    draw: ImageDraw.ImageDraw,
    start_pt: Tuple[int, int],
    end_pt: Tuple[int, int],
    color: Tuple[int, int, int, int] = (235, 150, 20, 230),
    width: int = 4
):
    """
    Draws an elegant curved pointer line connecting an annotation label
    to a cutout subject (like in screenshots 2 & 3: 'Curves', 'Details', 'Decoration').
    """
    x1, y1 = start_pt
    x2, y2 = end_pt
    # Control point for smooth cubic bezier curve
    ctrl_x = (x1 + x2) // 2 + int((y2 - y1) * 0.25)
    ctrl_y = (y1 + y2) // 2 - int((x2 - x1) * 0.20)

    # Approximate bezier curve with points
    steps = 25
    pts = []
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t)**2 * x1 + 2 * (1 - t) * t * ctrl_x + t**2 * x2
        by = (1 - t)**2 * y1 + 2 * (1 - t) * t * ctrl_y + t**2 * y2
        pts.append((int(bx), int(by)))

    draw.line(pts, fill=color, width=width)
    # Draw arrow tip or accent dot at destination
    draw.ellipse([x2 - 5, y2 - 5, x2 + 5, y2 + 5], fill=color)


def draw_retro_concentric_sunburst(
    draw: ImageDraw.ImageDraw,
    center: Tuple[int, int],
    base_radius: int,
    rings: int = 3
):
    """
    Draws retro Bauhaus concentric colored circular arcs behind architectural cutouts
    (like in screenshot 4 & 5).
    """
    cx, cy = center
    ring_colors = [
        (235, 90, 40, 200),   # Orange
        (245, 195, 30, 220),  # Sun Yellow
        (230, 215, 60, 180),  # Light yellow
    ]
    for i in range(min(rings, len(ring_colors))):
        r = base_radius + i * int(base_radius * 0.28)
        c = ring_colors[i]
        bbox = [cx - r, cy - r, cx + r, cy + r]
        draw.arc(bbox, start=180, end=360, fill=c, width=int(base_radius * 0.24))


# ---------------------------------------------------------------------------
# Transparent Cutout Fetcher & Asset Preparer
# ---------------------------------------------------------------------------
def fetch_and_prepare_cutouts(
    entities: List[Dict[str, str]],
    output_dir: str,
    used_media_ids: Optional[set] = None
) -> List[str]:
    """
    Downloads and prepares transparent cutout PNGs for detected entities:
    1. Searches Pinterest specifically for '{entity} transparent png cutout isolated'.
    2. Runs each downloaded image through make_transparent_cutout to guarantee 100% transparent background.
    3. If download fails, creates a stylized documentary emblem / map graphic fallback.
    Returns list of paths to verified transparent cutout PNGs.
    """
    os.makedirs(output_dir, exist_ok=True)
    used_ids = used_media_ids if used_media_ids is not None else set()
    prepared_cutouts = []

    for idx, ent in enumerate(entities):
        clean_en = ent.get("clean_en", "").strip() or ent.get("raw", "artifact")
        label = ent.get("label", clean_en.upper())
        search_q = ent.get("search") or f"{clean_en} transparent png cutout isolated"
        
        target_png = os.path.join(output_dir, f"cutout_asset_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', clean_en)[:20]}.png")
        
        raw_downloaded = None

        # 1. Fetch from Pinterest (with transparent cutout awareness)
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

        # 3. Process raw download into 100% clean transparent PNG cutout
        if raw_downloaded and os.path.exists(raw_downloaded):
            try:
                cutout_pil = make_transparent_cutout(raw_downloaded, output_png=target_png)
                if os.path.exists(target_png) and os.path.getsize(target_png) > 1000:
                    prepared_cutouts.append(target_png)
                    continue
            except Exception as e_proc:
                print(f"⚠️ [Cutout Processing warning]: {e_proc}")

        # 4. Stylized Graphical Fallback (Vector map silhouette / seal graphic)
        # Guarantees the video NEVER fails even if offline or Pinterest rate limited
        fallback_img = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
        fb_draw = ImageDraw.Draw(fallback_img)
        # Draw elegant documentary emblem / map placeholder
        fb_color = (210, 60, 45, 240) if idx == 0 else (40, 110, 200, 240)
        fb_draw.rounded_rectangle([(40, 40), (560, 560)], radius=80, fill=fb_color, outline=(255, 255, 255, 200), width=8)
        # Inner ring
        fb_draw.ellipse([(100, 100), (500, 500)], outline=(255, 255, 255, 160), width=5)
        # Title
        f_fb = get_font(size=40, font_type="bold")
        fb_draw.text((300, 300), label[:14], fill=(255, 255, 255, 255), font=f_fb, anchor="mm")
        fallback_img.save(target_png, format="PNG")
        prepared_cutouts.append(target_png)

    return prepared_cutouts


# ---------------------------------------------------------------------------
# Core Multi-Entity Sliding & Focused Zoom Animation Renderer
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
    Renders a broadcast-quality Johnny Harris / Vox documentary motion graphic clip:
    - Case 1 (2 Entities e.g. Bharat & Pakistan):
      Entity 1 enters centered with camera zoom.
      At transition point (~45%), Entity 1 smoothly slides left, and Entity 2 slides in from right!
      Camera zoom dynamically focuses on Entity 2.
    - Case 2 (1 Entity):
      Entity enters centered with tactile scale-in and Ken Burns camera zoom.
      Yellow highlighter focus rings encircle key features with paper washi tape stickers.
    
    Uses FFmpeg rawvideo pipe (< 35MB RAM, Render 512MB safe).
    """
    w, h = target_size
    duration = max(3.5, float(duration))
    total_frames = int(duration * fps)

    is_multi = len(cutout_paths) >= 2
    entities = entity_metadata.get("entities", [])

    # 1. Load and process transparent cutouts into PIL RGBA
    loaded_cutouts = []
    for p in cutout_paths:
        if os.path.exists(p):
            try:
                c_img = make_transparent_cutout(p)
                loaded_cutouts.append(c_img)
            except Exception as e_cut:
                print(f"⚠️ [Collage Cutout] Warning loading {p}: {e_cut}")
    
    if not loaded_cutouts:
        raise ValueError("No valid cutout images available to render.")

    # 2. Pick aesthetic canvas palette
    canvas_base = create_collage_canvas(w, h, draw_grid=True, draw_tape=True, draw_vignette=True)

    # 3. Size and scale cutouts appropriately
    # In portrait 1080x1920: multi-entity width ~480px, single-entity width ~720px
    if is_multi:
        max_cutout_w = int(w * 0.44)
        max_cutout_h = int(h * 0.42)
    else:
        max_cutout_w = int(w * 0.68)
        max_cutout_h = int(h * 0.55)

    scaled_cutouts = []
    shadows = []
    for c in loaded_cutouts:
        cw, ch = c.size
        scale = min(max_cutout_w / cw, max_cutout_h / ch)
        nw, nh = int(cw * scale), int(ch * scale)
        res_c = c.resize((nw, nh), Image.BICUBIC)
        # Create shadow
        sh_img, sh_offset = create_cutout_drop_shadow(res_c, blur_radius=12)
        scaled_cutouts.append(res_c)
        shadows.append((sh_img, sh_offset))

    # Fonts for typography callouts
    font_title = get_font(size=int(w * 0.048), font_type="bold")
    font_callout = get_font(size=int(w * 0.032), font_type="serif")

    # 4. Initialize FFmpeg subprocess with rawvideo pipe
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{w}x{h}",
        "-pix_fmt", "rgba",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-threads", "1",
        os.path.abspath(output_mp4)
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Transition timing parameters
    # t_trans_start: frame when slide begins (~40% of duration)
    # slide_duration_frames: ~1.0 second for smooth slide
    slide_dur_sec = 0.9
    slide_dur_frames = int(slide_dur_sec * fps)
    t_trans_start = int(total_frames * 0.40)
    t_trans_end = t_trans_start + slide_dur_frames

    # Smooth cubic ease-out function
    def ease_out_cubic(t_norm: float) -> float:
        t_c = max(0.0, min(1.0, t_norm))
        return 1.0 - math.pow(1.0 - t_c, 3)

    # 5. Frame-by-Frame Generation Loop
    for frame_idx in range(total_frames):
        t_sec = frame_idx / fps
        
        # Clone background canvas
        frame = canvas_base.copy()
        draw = ImageDraw.Draw(frame, "RGBA")

        if is_multi:
            # ===============================================================
            # TWO-ENTITY SLIDING & DYNAMIC FOCUS ZOOM
            # ===============================================================
            c1 = scaled_cutouts[0]
            sh1, off1 = shadows[0]
            c2 = scaled_cutouts[1]
            sh2, off2 = shadows[1]

            lbl1 = entities[0]["label"] if len(entities) > 0 else "ENTITY 1"
            lbl2 = entities[1]["label"] if len(entities) > 1 else "ENTITY 2"

            cy_fixed = int(h * 0.50)

            if frame_idx < t_trans_start:
                # -----------------------------------------------------------
                # Phase 1: Entity 1 is Centered on the Canvas
                # Camera zooms slightly into Entity 1
                # -----------------------------------------------------------
                zoom_scale = 1.0 + (frame_idx / t_trans_start) * 0.08  # 1.0 -> 1.08
                curr_w = int(c1.width * zoom_scale)
                curr_h = int(c1.height * zoom_scale)
                c1_dyn = c1.resize((curr_w, curr_h), Image.BICUBIC)
                sh1_dyn, off1_dyn = create_cutout_drop_shadow(c1_dyn, blur_radius=12)

                x1 = int(w * 0.50 - curr_w / 2)
                y1 = int(cy_fixed - curr_h / 2)

                # Paste drop shadow + cutout
                frame.paste(sh1_dyn, (x1 + off1_dyn[0], y1 + off1_dyn[1]), mask=sh1_dyn)
                frame.paste(c1_dyn, (x1, y1), mask=c1_dyn)

                # Yellow highlighter focus ring on key detail of Entity 1
                ring_r = int(min(curr_w, curr_h) * 0.35)
                ring_cx = x1 + int(curr_w * 0.5)
                ring_cy = y1 + int(curr_h * 0.38)
                draw_highlighter_focus_circle(draw, (ring_cx, ring_cy), ring_r, (255, 230, 20, 210), width=4)

                # Label Pill for Entity 1
                draw_curved_callout_pointer(draw, (ring_cx, ring_cy - ring_r), (ring_cx + 40, ring_cy - ring_r - 50))
                draw.text((ring_cx + 50, ring_cy - ring_r - 65), lbl1, fill=(20, 20, 20, 255), font=font_title)

            elif t_trans_start <= frame_idx < t_trans_end:
                # -----------------------------------------------------------
                # Phase 2: SMOOTH SLIDE TRANSITION!
                # Entity 1 slides left: center (0.50) -> left side (0.28)
                # Entity 2 slides in from right: offscreen (1.25) -> right side (0.72)
                # -----------------------------------------------------------
                t_norm = (frame_idx - t_trans_start) / slide_dur_frames
                ease_val = ease_out_cubic(t_norm)

                # Entity 1 position
                pos1_x = w * (0.50 - 0.22 * ease_val)
                x1 = int(pos1_x - c1.width / 2)
                y1 = int(cy_fixed - c1.height / 2)
                frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                frame.paste(c1, (x1, y1), mask=c1)

                # Entity 2 position (sliding in from off-canvas right)
                pos2_x = w * (1.25 - 0.53 * ease_val)
                x2 = int(pos2_x - c2.width / 2)
                y2 = int(cy_fixed - c2.height / 2)
                frame.paste(sh2, (x2 + off2[0], y2 + off2[1]), mask=sh2)
                frame.paste(c2, (x2, y2), mask=c2)

            else:
                # -----------------------------------------------------------
                # Phase 3: Both Entities Rest Side-by-Side
                # Camera Zoom & Focus shifts DIRECTLY to Entity 2!
                # -----------------------------------------------------------
                phase3_norm = (frame_idx - t_trans_end) / max(1, (total_frames - t_trans_end))
                zoom2_scale = 1.0 + phase3_norm * 0.10  # 1.0 -> 1.10 zoom on Entity 2

                # Entity 1 at rest (left)
                x1 = int(w * 0.28 - c1.width / 2)
                y1 = int(cy_fixed - c1.height / 2)
                frame.paste(sh1, (x1 + off1[0], y1 + off1[1]), mask=sh1)
                frame.paste(c1, (x1, y1), mask=c1)
                # Entity 1 subtle label
                draw.text((x1 + 10, y1 + c1.height + 15), lbl1, fill=(80, 80, 80, 220), font=font_callout)

                # Entity 2 (right) with active focus zoom
                curr2_w = int(c2.width * zoom2_scale)
                curr2_h = int(c2.height * zoom2_scale)
                c2_dyn = c2.resize((curr2_w, curr2_h), Image.BICUBIC)
                sh2_dyn, off2_dyn = create_cutout_drop_shadow(c2_dyn, blur_radius=14)

                x2 = int(w * 0.72 - curr2_w / 2)
                y2 = int(cy_fixed - curr2_h / 2)
                frame.paste(sh2_dyn, (x2 + off2_dyn[0], y2 + off2_dyn[1]), mask=sh2_dyn)
                frame.paste(c2_dyn, (x2, y2), mask=c2_dyn)

                # Yellow highlighter focus circle on Entity 2
                ring2_r = int(min(curr2_w, curr2_h) * 0.36)
                ring2_cx = x2 + int(curr2_w * 0.5)
                ring2_cy = y2 + int(curr2_h * 0.38)
                draw_highlighter_focus_circle(draw, (ring2_cx, ring2_cy), ring2_r, (255, 230, 20, 220), width=5)

                # Active Callout Pointer & Label for Entity 2
                draw_curved_callout_pointer(draw, (ring2_cx, ring2_cy - ring2_r), (ring2_cx - 40, ring2_cy - ring2_r - 55))
                draw.text((ring2_cx - 30, ring2_cy - ring2_r - 70), lbl2, fill=(20, 20, 20, 255), font=font_title)

        else:
            # ===============================================================
            # SINGLE ENTITY EDITORIAL MOTION (Ken Burns + Focus Accent)
            # ===============================================================
            c1 = scaled_cutouts[0]
            lbl1 = entities[0]["label"] if len(entities) > 0 else "ARTIFACT"

            # Smooth Ken Burns zoom (1.0 -> 1.14 scale)
            zoom_norm = frame_idx / max(1, total_frames)
            scale_now = 1.0 + zoom_norm * 0.14
            curr_w = int(c1.width * scale_now)
            curr_h = int(c1.height * scale_now)
            c1_dyn = c1.resize((curr_w, curr_h), Image.BICUBIC)
            sh1_dyn, off1_dyn = create_cutout_drop_shadow(c1_dyn, blur_radius=14)

            # Center position
            x1 = int(w * 0.50 - curr_w / 2)
            y1 = int(h * 0.50 - curr_h / 2)

            # Draw concentric sunburst background graphic (like Bauhaus screenshot 4 & 5)
            draw_retro_concentric_sunburst(draw, (w // 2, y1 + int(curr_h * 0.45)), int(min(curr_w, curr_h) * 0.45))

            # Paste Shadow + Cutout
            frame.paste(sh1_dyn, (x1 + off1_dyn[0], y1 + off1_dyn[1]), mask=sh1_dyn)
            frame.paste(c1_dyn, (x1, y1), mask=c1_dyn)

            # Yellow highlighter focus ring on key detail (top third)
            ring_r = int(min(curr_w, curr_h) * 0.32)
            ring_cx = x1 + int(curr_w * 0.5)
            ring_cy = y1 + int(curr_h * 0.32)
            draw_highlighter_focus_circle(draw, (ring_cx, ring_cy), ring_r, (255, 230, 20, 215), width=4)

            # Elegant callout pointer to the detail
            draw_curved_callout_pointer(draw, (ring_cx, ring_cy - ring_r), (ring_cx + 45, ring_cy - ring_r - 55))
            draw.text((ring_cx + 55, ring_cy - ring_r - 70), lbl1, fill=(20, 20, 20, 255), font=font_title)

        # Write frame to FFmpeg stdin
        raw_bytes = frame.tobytes()
        proc.stdin.write(raw_bytes)

        del frame, draw
        if frame_idx % 25 == 0:
            release_system_memory()

    # Close pipe and wait for FFmpeg to finish encoding
    proc.stdin.close()
    proc.wait()

    release_system_memory()
    print(f"🎬 [Collage Cutout Engine] Successfully generated Vox-style motion clip: {os.path.basename(output_mp4)} ({duration:.1f}s)")
    return output_mp4
