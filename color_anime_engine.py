"""
=============================================================================
COLOR ANIME / AFTER EFFECTS KINETIC MOTION ENGINE (V2.0 PRO)
=============================================================================
Matches the user's signature visual aesthetic from the After Effects tutorial:
"Master the CLEAN Edit Under 60 Minutes" (Render.rrush) & Instagram reference reel:
1. Snappy Elastic Entrance & Recoil (Bounce Script damped harmonic oscillation).
2. Dynamic Parallax Flying 3D Props (Tumbling Dollar Bills, Asteroids, Gold Trophies, Cyber Nodes, Torn Tape).
3. Dynamic Camera Motion (Snap Punch Zooms on scene start + Ken Burns continuous drift + Impact micro-shakes).
4. Kinetic Explosive Typography (Giant 3D Words layered BEHIND character cutouts with scale slam & bloom).
5. Snappy Viewfinder Reticles & Target Guides (Brackets snap shut onto subject + pulsing HUD telemetry).
6. Animated Frosted Glass UI Badges, Stacked Checklists & SCAM ALERT Cards.
7. Dual Presentation Modes:
   - Dark Cosmic VFX (Astronaut, Space, Giant 'PRACTICE', Flying Cash, Halo Ring)
   - Retro Bauhaus / Showcase Window Mockup (Warm cream, 'after' golden pill, concentric sun arcs, curved pointer arrows).
8. 100% Pure Photo Cutouts (Background-removed PNGs) - ZERO stock video clips!
9. Low RAM Streaming via FFmpeg rawvideo pipe (< 35MB RAM, Render 512MB safe).
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
# After Effects Bounce Script / Damped Harmonic Spring Physics
# ---------------------------------------------------------------------------
def spring_bounce(
    t: float,
    duration: float = 0.40,
    overshoot: float = 0.22,
    freq: float = 14.0,
    decay: float = 7.5
) -> float:
    """
    Standard After Effects Bounce Script expression (Dan Ebberts / MotionScript).
    Returns value from 0.0 at t=0, overshooting to ~1.20, bouncing back to ~0.96,
    and settling smoothly to 1.0 at t >= duration.
    """
    if t <= 0.0:
        return 0.0
    if t >= duration:
        return 1.0
    t_n = t / duration
    val = 1.0 - math.exp(-decay * t_n) * math.cos(freq * t_n)
    return val


def get_purposeful_camera_zoom(
    t: float,
    duration: float,
    scene_text: str = "",
    arrival_times: Optional[List[float]] = None
) -> float:
    """
    Computes purposeful, dynamic After Effects camera zoom (Zoom In / Zoom Out):
    1. Focus Push-In (1.00 -> 1.075): Heightens tension for questions, climax, punchline ('सवाल', '?', 'रहस्य', 'क्या', 'क्यों').
    2. Grand Reveal Pull-Out (1.055 -> 1.00): Reveals vast scale for historical heritage, universe, ancient eras ('हजारों साल', 'इतिहास', 'प्राचीन', 'ब्रह्मांड').
    3. Cinematic Subtle Push-In (1.00 -> 1.045): For default storytelling and comparisons.
    4. Optical Arrival Punch Scale Bump (+0.022 over 0.35s): Dynamic camera hit triggered whenever a new entity arrives!
    5. Zero Shaking / Zero Jitter: Camera center is mathematically locked (shake_x=0, shake_y=0). Background never wobbles.
    """
    txt = (scene_text or "").lower()
    is_climax_or_question = any(k in txt for k in ["सवाल", "?", "क्यों", "कैसे", "क्या", "कहाँ", "question", "who", "why", "how", "climax", "secret", "रहस्य", "लेकिन"])
    is_grand_reveal = any(k in txt for k in ["हजारों साल", "इतिहास", "प्राचीन", "ancient", "heritage", "universe", "ब्रह्मांड", "संसार", "दुनिया", "सैकड़ों", "विशाल"])

    t_norm = min(1.0, max(0.0, t / max(0.1, duration)))
    # Smooth sinusoidal ease curve (zero abrupt starts/stops)
    ease_t = 0.5 - 0.5 * math.cos(t_norm * math.pi)

    if is_climax_or_question:
        base_zoom = 1.00 + ease_t * 0.075
    elif is_grand_reveal:
        base_zoom = 1.055 - ease_t * 0.055
    else:
        base_zoom = 1.00 + ease_t * 0.045

    arrival_bump = 0.0
    if arrival_times:
        for t_arr in arrival_times:
            if t >= t_arr:
                dt = t - t_arr
                if dt < 0.35:
                    p = dt / 0.35
                    arrival_bump += 0.022 * math.exp(-6.0 * p) * math.cos(9.0 * p)

    return base_zoom + arrival_bump


def get_camera_punch_transform(t: float, duration: float, w: int, h: int) -> Tuple[float, int, int]:
    """Backward compatibility wrapper returning (scale, shake_x, shake_y) with ZERO shake."""
    z = get_purposeful_camera_zoom(t, duration)
    return z, 0, 0


# ---------------------------------------------------------------------------
# Color Anime Atmospheric Palettes (Emerald Space, Cyan Cyber, Bauhaus Minimal, Crimson Alert)
# ---------------------------------------------------------------------------
COLOR_ANIME_THEMES = {
    "emerald_space": {
        "name": "emerald_space",
        "is_dark": True,
        "bg": (8, 10, 15),
        "primary_neon": (0, 230, 118, 255),    # Vibrant emerald neon green (#00e676)
        "glow_rgb": (0, 230, 118),
        "accent": (255, 255, 255, 255),
        "card_bg": (15, 23, 42, 235),
        "card_border": (0, 230, 118, 190),
        "halo_color": (255, 255, 255, 220),
        "prop_type": "dollar_bill"
    },
    "cyan_cyber": {
        "name": "cyan_cyber",
        "is_dark": True,
        "bg": (6, 12, 22),
        "primary_neon": (0, 229, 255, 255),    # Electric cyan (#00e5ff)
        "glow_rgb": (0, 229, 255),
        "accent": (255, 255, 255, 255),
        "card_bg": (12, 24, 42, 235),
        "card_border": (0, 229, 255, 190),
        "halo_color": (200, 245, 255, 220),
        "prop_type": "cyber_hex"
    },
    "space_cosmos": {
        "name": "space_cosmos",
        "is_dark": True,
        "bg": (6, 8, 14),
        "primary_neon": (0, 230, 118, 255),
        "glow_rgb": (0, 200, 120),
        "accent": (255, 255, 255, 255),
        "card_bg": (14, 20, 36, 235),
        "card_border": (0, 230, 118, 190),
        "halo_color": (255, 255, 255, 230),
        "prop_type": "asteroid"
    },
    "gold_luxury": {
        "name": "gold_luxury",
        "is_dark": True,
        "bg": (12, 10, 8),
        "primary_neon": (255, 215, 0, 255),    # Metallic gold (#ffd700)
        "glow_rgb": (255, 190, 30),
        "accent": (255, 255, 255, 255),
        "card_bg": (30, 24, 16, 235),
        "card_border": (255, 215, 0, 190),
        "halo_color": (255, 245, 210, 220),
        "prop_type": "gold_trophy"
    },
    "crimson_alert": {
        "name": "crimson_alert",
        "is_dark": True,
        "bg": (18, 6, 8),
        "primary_neon": (244, 63, 94, 255),    # Neon crimson red (#f43f5e)
        "glow_rgb": (239, 68, 68),
        "accent": (255, 255, 255, 255),
        "card_bg": (38, 12, 16, 235),
        "card_border": (244, 63, 94, 190),
        "halo_color": (255, 200, 210, 220),
        "prop_type": "warning_tri"
    },
    "bauhaus_minimal": {
        "name": "bauhaus_minimal",
        "is_dark": False,
        "bg": (244, 240, 230),                  # Warm vintage cream paper
        "primary_neon": (230, 40, 30, 255),     # Bauhaus primary red
        "secondary": (245, 166, 35, 255),       # Bauhaus warm amber/yellow
        "glow_rgb": (245, 166, 35),
        "accent": (20, 24, 30, 255),            # Deep architectural ink black
        "card_bg": (255, 255, 255, 245),
        "card_border": (220, 215, 200, 200),
        "halo_color": (245, 166, 35, 220),
        "prop_type": "paper_tape"
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
# Procedural 3D Flying Sprites (Dollar Bills, Asteroids, Gold Trophies, Paper Tape)
# ---------------------------------------------------------------------------
_SPRITE_CACHE: Dict[str, Image.Image] = {}

def get_dollar_bill_sprite(w: int = 180, h: int = 90) -> Image.Image:
    """Procedurally renders a detailed US Dollar $100 Banknote sprite with crisp borders and numerals."""
    key = f"dollar_{w}x{h}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Banknote rich green body with metallic rim
    d.rounded_rectangle([(2, 2), (w - 2, h - 2)], radius=8, fill=(28, 68, 42, 255), outline=(90, 210, 130, 255), width=3)
    d.rounded_rectangle([(7, 7), (w - 7, h - 7)], radius=5, outline=(50, 130, 75, 210), width=2)
    # Center oval portrait area
    cx, cy = w // 2, h // 2
    d.ellipse([(cx - 28, cy - 24), (cx + 28, cy + 24)], fill=(18, 48, 30, 255), outline=(130, 240, 170, 255), width=2)
    # Large center dollar symbol
    font_bold = get_clean_font(28, font_type="bold")
    d.text((cx, cy), "$", fill=(180, 255, 210, 255), anchor="mm", font=font_bold)
    # Corner numerals
    font_sm = get_clean_font(13, font_type="bold")
    d.text((15, 14), "100", fill=(130, 235, 160, 255), anchor="mm", font=font_sm)
    d.text((w - 15, h - 14), "100", fill=(130, 235, 160, 255), anchor="mm", font=font_sm)
    d.text((15, h - 14), "100", fill=(130, 235, 160, 255), anchor="mm", font=font_sm)
    d.text((w - 15, 14), "100", fill=(130, 235, 160, 255), anchor="mm", font=font_sm)

    _SPRITE_CACHE[key] = img
    return img


def get_asteroid_sprite(size: int = 140) -> Image.Image:
    """Procedurally renders a 3D faceted space asteroid rock with craters and rim highlight."""
    key = f"asteroid_{size}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [
        (int(size * 0.30), int(size * 0.08)),
        (int(size * 0.72), int(size * 0.06)),
        (int(size * 0.94), int(size * 0.35)),
        (int(size * 0.88), int(size * 0.76)),
        (int(size * 0.64), int(size * 0.96)),
        (int(size * 0.24), int(size * 0.92)),
        (int(size * 0.06), int(size * 0.60)),
        (int(size * 0.10), int(size * 0.28))
    ]
    d.polygon(pts, fill=(90, 96, 110, 255), outline=(190, 205, 225, 240))
    # Crater indentations
    d.ellipse([(int(size * 0.35), int(size * 0.35)), (int(size * 0.55), int(size * 0.50))], fill=(58, 62, 72, 255), outline=(38, 42, 48, 255))
    d.ellipse([(int(size * 0.62), int(size * 0.62)), (int(size * 0.78), int(size * 0.74))], fill=(64, 68, 78, 255))
    _SPRITE_CACHE[key] = img
    return img


def get_gold_trophy_sprite(w: int = 120, h: int = 150) -> Image.Image:
    """Procedurally renders a metallic 3D gold trophy cup."""
    key = f"trophy_{w}x{h}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w // 2
    # Cup body
    d.polygon([(cx - 38, 20), (cx + 38, 20), (cx + 28, 80), (cx - 28, 80)], fill=(255, 215, 0, 255), outline=(255, 245, 180, 255), width=2)
    # Handles
    d.arc([(cx - 52, 25), (cx - 24, 65)], start=90, end=270, fill=(255, 200, 0, 255), width=5)
    d.arc([(cx + 24, 25), (cx + 52, 65)], start=270, end=90, fill=(255, 200, 0, 255), width=5)
    # Stem & Base
    d.rectangle([(cx - 8, 80), (cx + 8, 110)], fill=(230, 180, 0, 255))
    d.rounded_rectangle([(cx - 30, 110), (cx + 30, 135)], radius=6, fill=(40, 35, 25, 255), outline=(255, 215, 0, 255), width=2)
    _SPRITE_CACHE[key] = img
    return img


def get_cyber_hex_sprite(size: int = 100) -> Image.Image:
    """Procedurally renders a neon electric cyber data node."""
    key = f"cyber_{size}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = size // 2 - 6
    pts = []
    for i in range(6):
        ang = i * (math.pi / 3.0)
        pts.append((int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))))
    d.polygon(pts, fill=(10, 28, 48, 220), outline=(0, 229, 255, 255), width=3)
    # Inner tech cross
    d.line([(cx - 14, cy), (cx + 14, cy)], fill=(0, 229, 255, 240), width=2)
    d.line([(cx, cy - 14), (cx, cy + 14)], fill=(0, 229, 255, 240), width=2)
    _SPRITE_CACHE[key] = img
    return img


def get_paper_tape_sprite(w: int = 180, h: int = 45, color_name: str = "red") -> Image.Image:
    """Procedurally renders a ripped paper tape strip with jagged edges (Bauhaus / Collage style)."""
    key = f"tape_{color_name}_{w}x{h}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    base_c = (220, 50, 45, 225) if color_name == "red" else (40, 90, 180, 225)
    # Draw jagged top & bottom edges
    pts = [(8, 4)]
    for x in range(16, w - 8, 12):
        pts.append((x, 4 + (x % 6) - 3))
    pts.append((w - 8, 4))
    for y in [15, 30, h - 6]:
        pts.append((w - 8 + (y % 4), y))
    for x in range(w - 16, 8, -12):
        pts.append((x, h - 6 + (x % 5) - 2))
    pts.append((8, h - 6))
    for y in [30, 15]:
        pts.append((8 - (y % 4), y))

    d.polygon(pts, fill=base_c, outline=(255, 255, 255, 120), width=1)
    _SPRITE_CACHE[key] = img
    return img


# ---------------------------------------------------------------------------
# Multi-Plane Flying 3D Props Engine (Parallax, 3D Tumbling & Depth Blur)
# ---------------------------------------------------------------------------
class FlyingPropInstance:
    def __init__(
        self,
        prop_type: str,
        start_x: float,
        start_y: float,
        vx: float,
        vy: float,
        rot0: float,
        rot_spd: float,
        flip0: float,
        flip_spd: float,
        scale: float,
        depth_plane: str = "bg",  # "bg" or "fg"
        extra: str = ""
    ):
        self.prop_type = prop_type
        self.start_x = start_x
        self.start_y = start_y
        self.vx = vx
        self.vy = vy
        self.rot0 = rot0
        self.rot_spd = rot_spd
        self.flip0 = flip0
        self.flip_spd = flip_spd
        self.scale = scale
        self.depth_plane = depth_plane
        self.extra = extra


class FlyingPropsEngine:
    """
    Manages 5-7 dynamic 3D flying props with realistic physics:
    - 3D tumbling (perspective scale compression along X).
    - 2D rotation with velocity.
    - Multi-plane depth parallax (foreground props move faster with depth blur; background move slower).
    """
    def __init__(self, theme_name: str, width: int, height: int):
        self.width = width
        self.height = height
        self.theme_name = theme_name
        self.props: List[FlyingPropInstance] = []
        self._init_props()

    def _init_props(self):
        theme = COLOR_ANIME_THEMES.get(self.theme_name, COLOR_ANIME_THEMES["emerald_space"])
        p_type = theme.get("prop_type", "dollar_bill")

        # Deterministic seed per theme for smooth render consistency
        rng = np.random.RandomState(hash(self.theme_name) % 100000)

        # Create 3 background props (smaller, slower) and 2 foreground props (larger, faster)
        configs = [
            # Background props
            {"depth": "bg", "scale": 0.65, "y_range": (0.15, 0.45), "vx": 45, "vy": -30},
            {"depth": "bg", "scale": 0.75, "y_range": (0.35, 0.70), "vx": -50, "vy": -25},
            {"depth": "bg", "scale": 0.80, "y_range": (0.60, 0.85), "vx": 60, "vy": -35},
            # Foreground props (dramatic 3D pass)
            {"depth": "fg", "scale": 1.25, "y_range": (0.20, 0.60), "vx": 120, "vy": -65},
            {"depth": "fg", "scale": 1.40, "y_range": (0.50, 0.88), "vx": -110, "vy": -60},
        ]

        for cfg in configs:
            sx = int(rng.uniform(self.width * 0.1, self.width * 0.85))
            sy = int(rng.uniform(self.height * cfg["y_range"][0], self.height * cfg["y_range"][1]))
            r0 = float(rng.uniform(-30, 30))
            rspd = float(rng.uniform(15, 35)) * (1 if rng.rand() > 0.5 else -1)
            f0 = float(rng.uniform(0, math.pi))
            fspd = float(rng.uniform(2.5, 4.5))
            extra = "red" if rng.rand() > 0.5 else "blue"

            self.props.append(FlyingPropInstance(
                prop_type=p_type,
                start_x=sx,
                start_y=sy,
                vx=cfg["vx"],
                vy=cfg["vy"],
                rot0=r0,
                rot_spd=rspd,
                flip0=f0,
                flip_spd=fspd,
                scale=cfg["scale"],
                depth_plane=cfg["depth"],
                extra=extra
            ))

    def render_layer(self, canvas: Image.Image, t: float, plane: str = "bg"):
        """Renders either background or foreground props onto the canvas."""
        for p in self.props:
            if p.depth_plane != plane:
                continue

            # 1. Base Sprite
            if p.prop_type == "dollar_bill":
                base_sprite = get_dollar_bill_sprite(180, 90)
            elif p.prop_type == "asteroid":
                base_sprite = get_asteroid_sprite(140)
            elif p.prop_type == "gold_trophy":
                base_sprite = get_gold_trophy_sprite(120, 150)
            elif p.prop_type == "cyber_hex":
                base_sprite = get_cyber_hex_sprite(100)
            elif p.prop_type == "paper_tape":
                base_sprite = get_paper_tape_sprite(180, 45, color_name=p.extra)
            else:
                base_sprite = get_dollar_bill_sprite(180, 90)

            # 2. Scale & 3D Tumbling Factor
            flip_val = abs(math.cos(p.flip0 + t * p.flip_spd))
            flip_scale_x = max(0.12, flip_val)

            bw, bh = base_sprite.size
            cur_w = max(8, int(bw * p.scale * flip_scale_x))
            cur_h = max(8, int(bh * p.scale))

            sprite_dyn = base_sprite.resize((cur_w, cur_h), Image.BILINEAR)

            # 3. 2D Rotation
            cur_angle = p.rot0 + t * p.rot_spd
            sprite_rot = sprite_dyn.rotate(cur_angle, expand=True, resample=Image.BICUBIC)

            # 4. Foreground subtle depth blur for cinematic depth of field
            if plane == "fg":
                sprite_rot = sprite_rot.filter(ImageFilter.GaussianBlur(radius=1.2))

            # 5. Position & Screen wrap
            curr_x = (p.start_x + p.vx * t) % (self.width + 300) - 150
            curr_y = (p.start_y + p.vy * t) % (self.height + 300) - 150

            px = int(curr_x - sprite_rot.width // 2)
            py = int(curr_y - sprite_rot.height // 2)

            canvas.paste(sprite_rot, (px, py), mask=sprite_rot)


# ---------------------------------------------------------------------------
# Background Canvas Generators (Dark Cosmic Starry Space & Vintage Bauhaus Clean)
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
        star_c = (230, 245, 255, alpha) if rng.rand() > 0.3 else (glow_rgb[0], glow_rgb[1], glow_rgb[2], alpha)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=star_c)

    # 3. Soft Volumetric Nebula Glow (Radial Gaussian Glow)
    glow_mask = Image.new("L", (width, height), 0)
    g_draw = ImageDraw.Draw(glow_mask)
    gcx = width // 2
    gcy = int(height * 0.48)
    gr = int(width * 0.52)
    g_draw.ellipse([gcx - gr, gcy - gr, gcx + gr, gcy + gr], fill=255)
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(radius=int(width * 0.22)))

    glow_np = np.zeros((height, width, 4), dtype=np.uint8)
    glow_np[:, :, 0] = glow_rgb[0]
    glow_np[:, :, 1] = glow_rgb[1]
    glow_np[:, :, 2] = glow_rgb[2]
    glow_np[:, :, 3] = (np.array(glow_mask, dtype=np.float32) * 0.38).astype(np.uint8)
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


def create_bauhaus_clean_base(width: int, height: int) -> Tuple[Image.Image, Dict[str, Any]]:
    """Creates a vintage warm cream paper canvas with minimalist crosshairs (Bauhaus / Architecture style)."""
    theme = COLOR_ANIME_THEMES["bauhaus_minimal"]
    canvas = Image.new("RGBA", (width, height), theme["bg"] + (255,))
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Minimalist grid crosses (+)
    step_x = width // 6
    step_y = height // 10
    cross_col = (180, 175, 160, 160)
    arm = 6
    for gx in range(step_x, width, step_x):
        for gy in range(step_y, height, step_y):
            draw.line([(gx - arm, gy), (gx + arm, gy)], fill=cross_col, width=1)
            draw.line([(gx, gy - arm), (gx, gy + arm)], fill=cross_col, width=1)

    return canvas, theme


# ---------------------------------------------------------------------------
# Snappy Viewfinder Reticles & Dynamic Tracking Brackets (AE Kinetic Guides)
# ---------------------------------------------------------------------------
def draw_dynamic_viewfinder_reticles(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    theme: Dict[str, Any],
    t: float,
    duration: float
):
    """
    Renders kinetic viewfinder tracking brackets with elastic snap-shut entrance,
    pulsing tracking dots, and active HUD telemetry.
    Matches Render.rrush tutorial viewfinder brackets!
    """
    primary_color = theme["primary_neon"]
    is_dark = theme.get("is_dark", True)

    # 1. Snap-shut entrance physics: starts wide (1.35x), snaps shut with spring bounce in first 0.35s
    bounce_val = spring_bounce(t, duration=0.35, overshoot=0.20)
    snap_factor = 1.35 - 0.35 * bounce_val

    base_mx = int(width * 0.065)
    base_my = int(height * 0.055)
    mx = int(base_mx * snap_factor)
    my = int(base_my * snap_factor)

    arm_len = int(width * 0.065)
    w_line = 3
    dot_r = 5

    # Pulsing anchor dots
    dot_pulse = 180 + int(70 * math.sin(t * math.pi * 4))
    dot_color = (primary_color[0], primary_color[1], primary_color[2], dot_pulse)

    corners = [
        (mx, my, 1, 1),                           # Top Left
        (width - mx, my, -1, 1),                  # Top Right
        (mx, height - my, 1, -1),                 # Bottom Left
        (width - mx, height - my, -1, -1)         # Bottom Right
    ]

    for cx, cy, dx, dy in corners:
        draw.line([(cx, cy), (cx + dx * arm_len, cy)], fill=primary_color, width=w_line)
        draw.line([(cx, cy), (cx, cy + dy * arm_len)], fill=primary_color, width=w_line)
        draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=dot_color)

    # 2. Sleek HUD Telemetry Labels
    font_hud = get_clean_font(int(width * 0.024), font_type="bold")
    text_color = (255, 255, 255, 210) if is_dark else (40, 45, 55, 210)

    # Blinking REC dot
    rec_blink = (int(t * 3) % 2 == 0)
    rec_dot_color = (244, 63, 94, 255) if rec_blink else (244, 63, 94, 60)
    draw.ellipse([mx + arm_len + 12, my - 6, mx + arm_len + 22, my + 4], fill=rec_dot_color)
    draw.text((mx + arm_len + 28, my - 1), "REC", fill=text_color, font=font_hud, anchor="lm")

    # Frame / Tech counter in top right
    frame_num = int(t * 60)
    draw.text((width - mx - arm_len - 12, my - 1), f"60 FPS // {frame_num:04d}", fill=text_color, font=font_hud, anchor="rm")


# ---------------------------------------------------------------------------
# Glowing Planetary Halo Ring & Bauhaus Concentric Arcs
# ---------------------------------------------------------------------------
def draw_planetary_halo_ring(
    draw: ImageDraw.ImageDraw,
    center: Tuple[int, int],
    radius: int,
    theme: Dict[str, Any],
    scale_factor: float = 1.0,
    t: float = 0.0
):
    """
    Renders high-intensity glowing planetary halo ring behind character.
    Matches user reference screenshots 1 & 6!
    """
    cx, cy = center
    curr_r = int(radius * scale_factor)
    primary_c = theme["primary_neon"]
    halo_c = (255, 255, 255, 220)  # Clean celestial white core ring

    # 1. Subtle Outer Glow
    glow_alpha = int(45 + 15 * math.sin(t * math.pi * 2))
    draw.ellipse([cx - curr_r - 4, cy - curr_r - 4, cx + curr_r + 4, cy + curr_r + 4], outline=(primary_c[0], primary_c[1], primary_c[2], glow_alpha), width=6)
    # 2. Sleek Thin Core Ring (Vane Motion / Astronaut Reference)
    draw.ellipse([cx - curr_r, cy - curr_r, cx + curr_r, cy + curr_r], outline=halo_c, width=2)


def draw_bauhaus_concentric_arcs(
    draw: ImageDraw.ImageDraw,
    center: Tuple[int, int],
    base_radius: int,
    t: float = 0.0
):
    """
    Renders bold concentric Bauhaus sun arcs / rings in yellow, amber, and red.
    Matches user reference screenshot 4 (Bauhaus poster)!
    """
    cx, cy = center
    r_outer = base_radius
    r_mid = int(base_radius * 0.72)
    r_inner = int(base_radius * 0.44)

    # Outer pale amber ring
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=(245, 195, 80, 240))
    # Mid warm amber ring
    draw.ellipse([cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid], fill=(240, 140, 30, 255))
    # Inner vivid crimson circle
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=(225, 45, 40, 255))


# ---------------------------------------------------------------------------
# Giant Kinetic Typography (Scale Slam Entrance + Neon Bloom)
# ---------------------------------------------------------------------------
def draw_giant_kinetic_background_text(
    draw: ImageDraw.ImageDraw,
    giant_word: str,
    intro_phrase: str,
    width: int,
    center_y: int,
    theme: Dict[str, Any],
    t: float,
    duration: float
):
    """
    Renders massive kinetic typography BEHIND the character cutout.
    Scale slams down from 1.8x to 1.0x with elastic recoil (Text Exploder effect).
    Matches user reference screenshots 2 ('so you can PRACTICE') and 3 ('DESCRIPTION BOX')!
    """
    if not giant_word:
        return

    word_clean = giant_word.upper().strip()
    primary_color = theme["primary_neon"]
    is_dark = theme.get("is_dark", True)

    # 1. Staggered Entrance Physics: slams down between t=0.08 and t=0.45s
    t_text = max(0.0, t - 0.08)
    bounce_val = spring_bounce(t_text, duration=0.36, overshoot=0.20)
    # Scale slams from 1.7x down to 1.0x with spring recoil
    slam_scale = 1.0 + (1.0 - bounce_val) * 0.7
    # Subtle ongoing breathing
    breathe = 1.0 + 0.02 * math.sin(t * math.pi * 2)
    final_scale = slam_scale * breathe

    # 2. Font Sizing to fill ~88% of canvas width
    max_text_w = int(width * 0.88)
    base_font_size = int(width * 0.18)
    font_giant = get_clean_font(int(base_font_size * final_scale), font_type="giant")

    tb = font_giant.getbbox(word_clean)
    curr_tw = tb[2] - tb[0]
    if curr_tw > max_text_w and curr_tw > 0:
        ratio = max_text_w / curr_tw
        adjusted_size = max(34, int(base_font_size * final_scale * ratio))
        font_giant = get_clean_font(adjusted_size, font_type="giant")

    # 3. Intro Context Phrase above
    if intro_phrase:
        intro_font_size = int(width * 0.040)
        font_intro = get_clean_font(intro_font_size, font_type="sans")
        intro_y = center_y - int(width * 0.14)
        intro_color = (255, 255, 255, 235) if is_dark else (30, 35, 45, 235)
        draw.text((width // 2, intro_y), intro_phrase, fill=intro_color, font=font_intro, anchor="mm")

    # 4. Giant Kinetic Word with 3D Drop Shadow & Impact Flash Bloom
    shadow_col = (0, 0, 0, 190) if is_dark else (180, 170, 150, 180)
    text_color = primary_color if is_dark else (20, 24, 30, 255)

    # Drop shadow
    draw.text((width // 2 + 5, center_y + 6), word_clean, fill=shadow_col, font=font_giant, anchor="mm")
    # Main bold word
    draw.text((width // 2, center_y), word_clean, fill=text_color, font=font_giant, anchor="mm")


# ---------------------------------------------------------------------------
# Frosted Glass UI Badges, Checklists & SCAM ALERT Cards (Slide-up Spring Pop-in)
# ---------------------------------------------------------------------------
def draw_glassmorphism_pill_badge(
    draw: ImageDraw.ImageDraw,
    text: str,
    width: int,
    y_pos: int,
    theme: Dict[str, Any],
    t: float,
    badge_type: str = "pill"  # "pill" or "after"
):
    """
    Renders sleek frosted-glass pill badge with elastic spring slide-up from bottom.
    Supports standard $150 Edit pill and iconic golden Bauhaus 'after' pill badge!
    """
    if not text:
        return

    # Elastic entrance physics: slides up from y + 240px
    t_badge = max(0.0, t - 0.16)
    bounce_val = spring_bounce(t_badge, duration=0.38, overshoot=0.18)
    curr_y = int(y_pos + 220 * (1.0 - bounce_val))

    if badge_type == "after":
        # Golden Bauhaus 'after' pill badge (Matches user screenshots 1, 2, 4!)
        font_after = get_clean_font(int(width * 0.038), font_type="bold")
        badge_w = int(width * 0.28)
        badge_h = 44
        x1 = int(width * 0.08)
        x2 = x1 + badge_w
        y1 = curr_y - badge_h // 2
        y2 = curr_y + badge_h // 2
        draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=22, fill=(245, 175, 35, 255), outline=(255, 220, 80, 255), width=2)
        draw.text(((x1 + x2) // 2, curr_y), "after", fill=(20, 20, 20, 255), font=font_after, anchor="mm")
        return

    # Standard Frosted Glass / Dark Mode Pill Badge
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
    y1 = curr_y - card_h // 2
    y2 = curr_y + card_h // 2

    # Draw frosted body & glowing neon border
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=16, fill=theme["card_bg"], outline=theme["card_border"], width=2)
    # Glowing neon square indicator
    icon_s = 14
    ix = x1 + 18
    iy = curr_y - icon_s // 2
    draw.rectangle([(ix, iy), (ix + icon_s, iy + icon_s)], fill=theme["primary_neon"])
    # Badge text
    draw.text((ix + icon_s + 14, curr_y), text, fill=(255, 255, 255, 255), font=font_badge, anchor="lm")


def draw_stacked_checklist_cards(
    draw: ImageDraw.ImageDraw,
    items: List[str],
    width: int,
    y_pos: int,
    theme: Dict[str, Any],
    t: float
):
    """
    Renders stacked sleek dark UI notification cards with green checkboxes & cascade spring bounce.
    Matches user reference screenshot 6 panel 2!
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
        # Staggered cascade entrance
        t_card = max(0.0, t - 0.15 - idx * 0.10)
        bounce_val = spring_bounce(t_card, duration=0.35, overshoot=0.18)
        offset_y = int(180 * (1.0 - bounce_val))

        cy = start_y + idx * (card_h + spacing) + offset_y
        x1 = cx - card_w // 2
        x2 = cx + card_w // 2
        y1 = cy
        y2 = cy + card_h

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
    theme: Dict[str, Any],
    t: float
):
    """
    Renders sleek red warning modal card with alert icon and spring pop-in.
    Matches user reference screenshot 6 panel 3!
    """
    t_alert = max(0.0, t - 0.12)
    bounce_val = spring_bounce(t_alert, duration=0.38, overshoot=0.22)
    curr_y = int(y_pos + 260 * (1.0 - bounce_val))

    card_w = int(width * 0.76)
    card_h = 110
    cx = width // 2
    x1 = cx - card_w // 2
    x2 = cx + card_w // 2
    y1 = curr_y - card_h // 2
    y2 = curr_y + card_h // 2

    alert_theme = COLOR_ANIME_THEMES["crimson_alert"]
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=16, fill=alert_theme["card_bg"], outline=alert_theme["card_border"], width=2)

    # Top Alert Badge Icon
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


def draw_curved_pointer_callouts(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    callouts: List[Tuple[Tuple[int, int], str]],
    theme: Dict[str, Any],
    t: float
):
    """
    Renders yellow curved pointer lines with circular target rings & clean labels.
    Directly matches user reference screenshots 2 & 3 ('curves', 'details', 'decoration')!
    """
    if not callouts:
        return

    accent_col = (245, 175, 35, 255)
    font_callout = get_clean_font(int(width * 0.032), font_type="bold")

    for idx, (target_pt, label) in enumerate(callouts[:3]):
        t_call = max(0.0, t - 0.20 - idx * 0.12)
        if t_call <= 0.0:
            continue
        bounce_val = spring_bounce(t_call, duration=0.32, overshoot=0.15)

        tx, ty = target_pt
        # Yellow target circle around point of interest
        circ_r = int(24 * bounce_val)
        draw.ellipse([tx - circ_r, ty - circ_r, tx + circ_r, ty + circ_r], outline=accent_col, width=3)

        # Curved pointer arc leading to text label above
        label_y = ty - 60
        label_x = tx + (25 if tx < width // 2 else -25)

        # Draw curved arc line
        draw.arc([(min(tx, label_x) - 10, label_y), (max(tx, label_x) + 10, ty + 10)], start=0, end=180, fill=accent_col, width=3)
        draw.text((label_x, label_y - 12), label, fill=(30, 35, 45, 255), font=font_callout, anchor="mm")


# ---------------------------------------------------------------------------
# Scene Element Detection (Punchy Words, Themes & Layout Resolvers)
# ---------------------------------------------------------------------------
def detect_color_anime_scene_elements(scene_text: str, main_topic: str = "") -> Dict[str, Any]:
    """
    Resolves theme palette, punchy kinetic word, and UI layout type based on scene text.
    """
    text_lower = (scene_text or "").lower()
    topic_lower = (main_topic or "").lower()

    # 1. Alert / Warning Context
    is_alert = any(k in text_lower for k in ["scam", "धोखा", "alert", "danger", "खतरा", "risk", "fake", "trap", "warning", "नुकसान", "बर्बाद"])

    # 2. Checklist / Condition Context
    is_checklist = any(k in text_lower for k in ["even if", "अगर", "शर्त", "नियम", "challenge", "pass", "rules", "steps", "points", "तरीके"])

    # 3. Bauhaus / Minimalist Architecture Context
    is_bauhaus = any(k in text_lower for k in ["bauhaus", "architecture", "design", "curves", "details", "minimal", "building", "नक्शा", "आर्किटेक्चर"])

    # 4. Wealth / Cash / Money Context
    is_wealth = any(k in text_lower for k in ["money", "cash", "dollar", "पैसा", "कमाई", "profit", "trading", "crypto", "rich", "wealth", "अमीर"])

    # 5. Extract Giant Punchy Word for Kinetic Typography Layer
    PUNCHY_KEYWORDS = [
        # Specific High-Drama Phrases (Check FIRST)
        ("पीछे छोड़ पाएगा", "INDIA VS USA", "the ultimate question"),
        ("पीछे छोड़", "SUPREMACY", "the race for"),
        ("सवाल", "WHO WINS?", "the ultimate question"),
        ("अस्तित्व", "UNEXPLORED", "back when america was"),
        ("सोने की चिड़िया", "GOLDEN BIRD", "once known as"),
        ("चिड़िया", "GOLDEN BIRD", "once known as"),
        ("हजारों साल", "HERITAGE", "thousands of years of"),
        ("आधुनिक तकनीक", "INNOVATION", "power of cutting edge"),
        ("पुरानी ताकत", "RISING BHARAT", "reclaiming ancient"),
        # Core Topical Words
        ("तकनीक", "INNOVATION", "power of cutting edge"),
        ("आधुनिक", "FUTURISTIC", "advancing through"),
        ("technology", "TECHNOLOGY", "cutting edge"),
        ("tech", "INNOVATION", "cutting edge"),
        ("सोना", "GOLDEN ERA", "revisiting the"),
        ("इतिहास", "HERITAGE", "thousands of years of"),
        ("heritage", "HERITAGE", "rich ancient"),
        ("ancient", "ANCIENT", "deep rooted in"),
        ("संभावना", "POTENTIAL", "unlimited economic"),
        ("अमेरिका", "SUPERPOWER", "rise of the modern"),
        ("america", "SUPERPOWER", "rise of the modern"),
        ("usa", "SUPERPOWER", "rise of the modern"),
        ("शक्ति", "GLOBAL MIGHT", "the ultimate"),
        ("ताकत", "GLOBAL POWER", "reclaiming the"),
        ("superpower", "SUPERPOWER", "rise of the modern"),
        ("भारत", "BHARAT", "the rise of"),
        ("bharat", "BHARAT", "the rise of"),
        ("india", "BHARAT", "the rise of"),
        # Standard Motivation & Hustle
        ("practice", "PRACTICE", "so you can"),
        ("प्रैक्टिस", "PRACTICE", "so you can"),
        ("अनुशासन", "DISCIPLINE", "staying true to"),
        ("discipline", "DISCIPLINE", "staying true to"),
        ("मेहनत", "HUSTLE", "the secret to"),
        ("hustle", "HUSTLE", "the power of"),
        ("कंपनी", "VENTURE", "launching the"),
        ("मार्केट", "MARKET", "inside the"),
        ("ट्रेडिंग", "TRADING", "mastering the"),
        ("trading", "TRADING", "mastering the"),
        ("profit", "PROFIT", "scaling your"),
        ("ai", "ARTIFICIAL", "the power of"),
        ("एआई", "ARTIFICIAL", "the power of"),
        ("स्पेस", "COSMOS", "journey to the"),
        ("अंतरिक्ष", "COSMOS", "journey to the"),
        ("कोड", "CODING", "building the"),
        ("सफलता", "SUCCESS", "how to achieve"),
        ("success", "SUCCESS", "how to achieve"),
        ("पैसा", "CAPITAL", "unlocking the"),
        ("capital", "CAPITAL", "unlocking the"),
        ("क्रिप्टो", "CRYPTO", "the future of"),
        ("दिमाग", "MINDSET", "unlocking your"),
        ("mindset", "MINDSET", "unlocking your"),
        ("रिजल्ट", "RESULTS", "delivering the"),
        ("results", "RESULTS", "delivering the"),
        ("challenge", "CHALLENGE", "facing the"),
        ("clips", "RAW CLIPS", "accessing all"),
        ("raw clips", "RAW CLIPS", "accessing all"),
        ("description", "DESCRIPTION", "everything in the"),
        ("bauhaus", "BAUHAUS", "master the clean")
    ]

    selected_punchy = None
    selected_intro = ""
    for kw, giant, intro in PUNCHY_KEYWORDS:
        if kw in text_lower:
            selected_punchy = giant
            selected_intro = intro
            break

    if not selected_punchy:
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

    # 6. Resolve Theme based on scene context
    if is_alert:
        theme_name = "crimson_alert"
    elif is_bauhaus:
        theme_name = "bauhaus_minimal"
    elif any(k in text_lower for k in ["चिड़िया", "सोना", "gold", "golden", "इतिहास", "heritage", "हजारों साल"]):
        theme_name = "gold_luxury"
    elif any(k in text_lower for k in ["तकनीक", "tech", "technology", "आधुनिक", "ai", "cyber", "digital", "microchip"]):
        theme_name = "cyan_cyber"
    elif any(k in text_lower for k in ["पीछे छोड़", "सवाल", "who wins", "clash", "vs", "race"]):
        theme_name = "crimson_alert"
    elif is_wealth:
        theme_name = "emerald_space"
    elif any(k in text_lower for k in ["space", "अंतरिक्ष", "तारे", "galaxy", "moon", "ग्रह"]):
        theme_name = "space_cosmos"
    else:
        theme_name = "emerald_space"

    # 7. Extract Checklist Items if checklist mode
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
        "is_bauhaus": is_bauhaus,
        "checklist_items": checklist_items,
        "theme_name": theme_name,
        "alert_title": "SCAM ALERT" if is_alert else "",
        "alert_sub": scene_text[:32] if is_alert else ""
    }


# ---------------------------------------------------------------------------
# Specialized Background & Card Layout Elements
# ---------------------------------------------------------------------------
def draw_spotlight_horizon_bg(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    theme: Dict[str, Any],
    t: float = 0.0
):
    """Sleek horizontal cinematic laser line & soft center spotlight (NO cheesy circle ring)."""
    glow_c = theme.get("glow_rgb", (0, 230, 118))
    cy = int(height * 0.44)
    pulse = 0.85 + 0.15 * math.sin(t * math.pi * 2)
    alpha_line = int(110 * pulse)
    # Sleek horizontal neon flare line
    draw.line([(int(width * 0.08), cy), (int(width * 0.92), cy)], fill=(glow_c[0], glow_c[1], glow_c[2], alpha_line), width=2)
    # Center bright flare
    flare_w = int(width * 0.28)
    draw.ellipse([(width // 2 - flare_w, cy - 6), (width // 2 + flare_w, cy + 6)], fill=(glow_c[0], glow_c[1], glow_c[2], int(140 * pulse)))
    draw.ellipse([(width // 2 - flare_w // 2, cy - 3), (width // 2 + flare_w // 2, cy + 3)], fill=(255, 255, 255, int(190 * pulse)))


def draw_heritage_pedestal_bg(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    t: float = 0.0
):
    """Soft warm golden radial pedestal glow beneath architectural heritage cutouts."""
    base_y = int(height * 0.68)
    r_ped = int(width * 0.36)
    pulse = 0.90 + 0.10 * math.sin(t * math.pi * 1.5)
    # Outer diffused gold glow
    draw.ellipse([
        (width // 2 - int(r_ped * 1.15), base_y - 25),
        (width // 2 + int(r_ped * 1.15), base_y + 35)
    ], fill=(212, 175, 55, int(45 * pulse)))
    # Core warm amber reflection
    draw.ellipse([
        (width // 2 - int(r_ped * 0.70), base_y - 12),
        (width // 2 + int(r_ped * 0.70), base_y + 18)
    ], fill=(255, 215, 0, int(80 * pulse)))


def draw_sleek_floating_topic_card(
    draw: ImageDraw.ImageDraw,
    title: str,
    subtitle: str,
    width: int,
    y_pos: int,
    theme: Dict[str, Any],
    t: float = 0.0
):
    """Sleek dark glassmorphism card with spring pop-in (matches reference screenshot 7)."""
    slide_val = spring_bounce(max(0.0, t - 0.15), duration=0.35, overshoot=0.10)
    card_w = int(width * 0.84)
    card_h = int(width * 0.16)
    cx = width // 2
    offset_y = int(60 * (1.0 - slide_val))
    cy = y_pos + offset_y

    x0 = cx - card_w // 2
    y0 = cy - card_h // 2
    x1 = cx + card_w // 2
    y1 = cy + card_h // 2

    # Dark frosted card body with glowing neon border
    draw.rounded_rectangle([(x0, y0), (x1, y1)], radius=16, fill=(12, 18, 30, 235), outline=theme["card_border"], width=2)
    # Top accent line
    draw.line([(x0 + 20, y0), (x0 + 100, y0)], fill=theme["primary_neon"], width=3)

    # Sanitize subtitle to ensure clean Latin characters (avoid tofu rectangles)
    if re.search(r'[\u0900-\u097F]', subtitle):
        subtitle = "RECLAIMING ANCIENT STRENGTH & GLORY"

    # Title & Subtitle inside card
    font_title = get_clean_font(int(width * 0.038), font_type="bold")
    font_sub = get_clean_font(int(width * 0.025), font_type="sans")
    draw.text((x0 + 24, y0 + 16), title.upper()[:28], fill=theme["primary_neon"], font=font_title, anchor="lt")
    draw.text((x0 + 24, y0 + 48), subtitle[:45], fill=(220, 230, 245, 230), font=font_sub, anchor="lt")


# ---------------------------------------------------------------------------
# Cutout Identifier Badge Helper
# ---------------------------------------------------------------------------
def draw_cutout_name_pill(draw: ImageDraw.ImageDraw, label: str, cx: int, bottom_y: int, theme: Dict[str, Any], alpha: float = 1.0):
    """Draws a sleek frosted glassmorphism identifier badge beneath a cutout."""
    if not label:
        return
    clean_lbl = label.upper().strip()
    f_lbl = get_clean_font(20, font_type="bold")
    tb = f_lbl.getbbox(clean_lbl)
    tw = tb[2] - tb[0]
    th = tb[3] - tb[1]
    pad_x, pad_y = 14, 6
    bx1 = cx - tw // 2 - pad_x
    by1 = bottom_y + 12
    bx2 = cx + tw // 2 + pad_x
    by2 = by1 + th + pad_y * 2
    p_a = int(220 * max(0.0, min(1.0, alpha)))
    if p_a <= 0:
        return
    neon_c = theme["primary_neon"][:3] + (p_a,)
    draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=12, fill=(12, 18, 30, p_a), outline=neon_c, width=2)
    draw.text((cx, (by1 + by2) // 2), clean_lbl, fill=(255, 255, 255, int(250 * max(0.0, min(1.0, alpha)))), font=f_lbl, anchor="mm")


# ---------------------------------------------------------------------------
# Core Color Anime / After Effects Motion Clip Renderer
# ---------------------------------------------------------------------------
def render_color_anime_motion_clip(
    cutout_paths: List[str],
    output_mp4: str,
    duration: float,
    scene_text: str = "",
    main_topic: str = "",
    target_size: Tuple[int, int] = (1080, 1920),
    fps: int = 24,
    scene_index: int = 0,
    layout_style: str = "auto",
    entity_labels: Optional[List[str]] = None
) -> str:
    """
    Renders an ultra-high production After Effects Kinetic Motion Clip:
    1. Arbitrary Multi-Entity Staggered Entrance (N = 1, 2, 3, 4+) in ONE frame with smooth spring physics!
    2. Dynamic Purposeful Camera Zoom In / Zoom Out (zero jitter/shake, focus zoom-in on climax, reveal zoom-out on heritage, scale arrival bumps).
    3. Dynamic Parallax Flying 3D Props (Tumbling Dollar Bills, Asteroids, Trophies, Cyber Nodes).
    4. Multi-Layout Scene Diversity (portal_halo, hero_typography, spotlight_minimal, floating_card, heritage_pedestal, dual_vs).
    5. 100% Pure Photo Cutouts (Zero stock video clips!).
    """
    w, h = target_size
    duration = max(3.0, float(duration))
    total_frames = int(duration * fps)

    # 1. Resolve Scene Metadata & Theme
    meta = detect_color_anime_scene_elements(scene_text, main_topic)
    theme_name = meta["theme_name"]
    is_bauhaus = meta.get("is_bauhaus", False)

    # 2. Base Canvas Generator
    if is_bauhaus:
        canvas_base, theme = create_bauhaus_clean_base(w, h)
    else:
        canvas_base, theme = create_dark_cosmic_base(w, h, theme_name=theme_name)

    # 3. Initialize Flying 3D Props Engine
    props_engine = FlyingPropsEngine(theme_name=theme_name, width=w, height=h)

    # 4. Prepare and clean character/object cutouts
    from collage_cutout_engine import make_transparent_cutout, sharpen_cutout, create_cutout_drop_shadow

    loaded_cutouts = []
    for p in cutout_paths:
        if p and os.path.exists(p):
            try:
                c = make_transparent_cutout(p)
                if c and c.width > 20 and c.height > 20:
                    loaded_cutouts.append(c)
            except Exception as e_c:
                print(f"⚠️ [Color Anime Engine] Warning loading cutout {p}: {e_c}")

    if not loaded_cutouts:
        # High-aesthetic fallback hero silhouette
        fallback_hero = Image.new("RGBA", (600, 750), (0, 0, 0, 0))
        fb_draw = ImageDraw.Draw(fallback_hero)
        fb_draw.ellipse([(180, 60), (420, 300)], fill=(225, 235, 245, 255), outline=(255, 255, 255, 240), width=6)
        fb_draw.ellipse([(215, 100), (385, 250)], fill=(15, 20, 30, 255), outline=(0, 230, 118, 220), width=4)
        fb_draw.rounded_rectangle([(100, 290), (500, 720)], radius=60, fill=(210, 225, 238, 255), outline=(255, 255, 255, 220), width=6)
        loaded_cutouts.append(fallback_hero)

    num_cutouts = min(4, len(loaded_cutouts))
    is_multi = num_cutouts >= 2
    processed_cutouts = []

    for idx, c_raw in enumerate(loaded_cutouts[:num_cutouts]):
        cw_r, ch_r = c_raw.size
        if num_cutouts == 1:
            target_ch = int(h * 0.50)
            max_cw = int(w * 0.85)
        elif num_cutouts == 2:
            target_ch = int(h * 0.42)
            max_cw = int(w * 0.44)
        elif num_cutouts == 3:
            target_ch = int(h * 0.38)
            max_cw = int(w * 0.30)
        else:
            target_ch = int(h * 0.28)
            max_cw = int(w * 0.40)

        c_scale = target_ch / max(1, ch_r)
        target_cw = int(cw_r * c_scale)
        if target_cw > max_cw:
            target_cw = max_cw
            target_ch = int(ch_r * (max_cw / cw_r))
        c_ready = c_raw.resize((max(10, target_cw), max(10, target_ch)), Image.LANCZOS)
        c_ready = sharpen_cutout(c_ready, amount=1.20)
        processed_cutouts.append(c_ready)

    # Staggered entrance arrival times for each entity in the frame
    if num_cutouts == 1:
        arrival_times = [0.0]
    elif num_cutouts == 2:
        arrival_times = [0.0, 0.65]
    elif num_cutouts == 3:
        arrival_times = [0.0, 0.60, 1.20]
    else:
        arrival_times = [0.0, 0.45, 0.90, 1.35]

    # 5. Resolve Layout Mode for Visual Diversity
    txt_lower = (scene_text or "").lower()
    if is_multi or " vs " in txt_lower:
        layout_mode = "dual_vs"
    elif layout_style and layout_style != "auto":
        layout_mode = layout_style
    else:
        if any(k in txt_lower for k in ["चिड़िया", "bird", "gold"]):
            layout_mode = "portal_halo"
        elif any(k in txt_lower for k in ["superpower", "शक्ति", "तकनीक", "technology", "ai", "modern"]):
            layout_mode = "hero_typography"
        elif any(k in txt_lower for k in ["इतिहास", "heritage", "temple", "हजारों", "civilization"]):
            layout_mode = "heritage_pedestal"
        elif any(k in txt_lower for k in ["भारत", "bharat", "राह पर", "country"]):
            layout_mode = "floating_card"
        elif any(k in txt_lower for k in ["अमेरिका", "america", "अस्तित्व"]):
            layout_mode = "spotlight_minimal"
        else:
            candidates = ["portal_halo", "spotlight_minimal", "hero_typography", "floating_card", "heritage_pedestal"]
            layout_mode = candidates[scene_index % len(candidates)]

    # 6. Setup FFmpeg streaming pipe (< 35MB RAM)
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

    # Alternate slide entrance direction for single cutouts (Left or Right)
    slide_dir = -1 if (hash(scene_text) % 2 == 0) else 1

    # Bauhaus callout points of interest
    bauhaus_callouts = [
        ((int(w * 0.35), int(h * 0.38)), "curves"),
        ((int(w * 0.65), int(h * 0.42)), "details"),
        ((int(w * 0.50), int(h * 0.62)), "structure")
    ]

    # 7. Kinetic Frame Render Loop
    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)
        t_norm = frame_idx / max(1, total_frames)

        frame = canvas_base.copy()
        draw = ImageDraw.Draw(frame, "RGBA")

        # -------------------------------------------------------------------
        # LAYER 1: Background Layout Graphics (Dynamic Variety per Layout Mode)
        # -------------------------------------------------------------------
        if is_bauhaus:
            draw_bauhaus_concentric_arcs(draw, halo_center, halo_radius, t=t)
        elif layout_mode == "portal_halo":
            halo_pulse = 1.0 + 0.04 * math.sin(t * math.pi * 2)
            draw_planetary_halo_ring(draw, halo_center, halo_radius, theme, scale_factor=halo_pulse, t=t)
        elif layout_mode == "spotlight_minimal":
            draw_spotlight_horizon_bg(draw, w, h, theme, t=t)
        elif layout_mode == "heritage_pedestal":
            draw_heritage_pedestal_bg(draw, w, h, t=t)
        elif layout_mode in ["floating_card", "hero_typography"]:
            pass

        # -------------------------------------------------------------------
        # LAYER 2: Background Flying 3D Props (Distant Dollar Bills / Asteroids)
        # -------------------------------------------------------------------
        props_engine.render_layer(frame, t=t, plane="bg")

        # -------------------------------------------------------------------
        # LAYER 3: Kinetic Typography BEHIND Cutouts
        # -------------------------------------------------------------------
        if layout_mode == "hero_typography":
            draw_giant_kinetic_background_text(
                draw=draw,
                giant_word=meta["giant_word"],
                intro_phrase=meta["intro_phrase"],
                width=w,
                center_y=text_center_y,
                theme=theme,
                t=t,
                duration=duration
            )
        elif layout_mode in ["portal_halo", "heritage_pedestal", "spotlight_minimal"]:
            intro_clean = meta.get("intro_phrase", "").strip()
            title_clean = meta.get("giant_word", "").strip()
            if title_clean:
                font_title = get_clean_font(int(w * 0.12), font_type="giant")
                f_intro = get_clean_font(int(w * 0.038), font_type="sans")
                intro_y = text_center_y - int(w * 0.12)
                if intro_clean:
                    draw.text((w // 2, intro_y), intro_clean, fill=(240, 245, 255, 220), font=f_intro, anchor="mm")
                draw.text((w // 2 + 4, text_center_y + 4), title_clean, fill=(0, 0, 0, 180), font=font_title, anchor="mm")
                draw.text((w // 2, text_center_y), title_clean, fill=theme["primary_neon"], font=font_title, anchor="mm")

        # -------------------------------------------------------------------
        # LAYER 4: Foreground Character/Object Cutouts (Arbitrary Multi-Entity Staggered Entrance)
        # -------------------------------------------------------------------
        if num_cutouts == 1:
            c_main = processed_cutouts[0]
            slide_val = spring_bounce(t, duration=0.35, overshoot=0.08)
            offset_x = int(w * 0.80 * (1.0 - slide_val) * slide_dir)
            
            char_x = int(w // 2 - c_main.width // 2 + offset_x)
            char_y = int(h * 0.54 - c_main.height // 2)

            if layout_mode == "heritage_pedestal":
                char_y = int(h * 0.68 - c_main.height)
            elif layout_mode == "floating_card":
                char_y = int(h * 0.44 - c_main.height // 2)

            sh_main, sh_off = create_cutout_drop_shadow(c_main, blur_radius=18, offset=(8, 16), shadow_opacity=0.45)
            frame.paste(sh_main, (char_x + sh_off[0], char_y + sh_off[1]), mask=sh_main)
            frame.paste(c_main, (char_x, char_y), mask=c_main)

        elif num_cutouts == 2:
            c_left = processed_cutouts[0]
            c_right = processed_cutouts[1]

            # Cutout 1: Slides in from LEFT at t=0.0s
            slide_1 = spring_bounce(t, duration=0.35, overshoot=0.08)
            target_x1 = int(w * 0.28 - c_left.width // 2)
            x1 = int(target_x1 - w * 0.60 * (1.0 - slide_1))
            y1 = int(h * 0.54 - c_left.height // 2)

            sh_l, sh_off_l = create_cutout_drop_shadow(c_left, blur_radius=16, offset=(6, 14), shadow_opacity=0.42)
            frame.paste(sh_l, (x1 + sh_off_l[0], y1 + sh_off_l[1]), mask=sh_l)
            frame.paste(c_left, (x1, y1), mask=c_left)
            if entity_labels and len(entity_labels) > 0 and slide_1 > 0.5:
                draw_cutout_name_pill(draw, entity_labels[0], int(w * 0.28), y1 + c_left.height, theme, alpha=slide_1)

            # Cutout 2: Slides in from RIGHT at staggered t_1
            t_arr2 = arrival_times[1]
            if t >= t_arr2:
                t_sub2 = max(0.0, t - t_arr2)
                slide_2 = spring_bounce(t_sub2, duration=0.35, overshoot=0.08)
                target_x2 = int(w * 0.72 - c_right.width // 2)
                x2 = int(target_x2 + w * 0.60 * (1.0 - slide_2))
                y2 = int(h * 0.54 - c_right.height // 2)

                sh_r, sh_off_r = create_cutout_drop_shadow(c_right, blur_radius=16, offset=(6, 14), shadow_opacity=0.42)
                frame.paste(sh_r, (x2 + sh_off_r[0], y2 + sh_off_r[1]), mask=sh_r)
                frame.paste(c_right, (x2, y2), mask=c_right)
                if entity_labels and len(entity_labels) > 1 and slide_2 > 0.5:
                    draw_cutout_name_pill(draw, entity_labels[1], int(w * 0.72), y2 + c_right.height, theme, alpha=slide_2)

            # Center VS Badge if comparison / conflict
            if t >= 0.75 and (" vs " in txt_lower or "बनाम" in txt_lower or "मुकाबला" in txt_lower or "पीछे" in txt_lower or "शक्तियों" in txt_lower):
                t_vs = max(0.0, t - 0.75)
                bounce_vs = spring_bounce(t_vs, duration=0.30, overshoot=0.15)
                r_vs = int(28 * bounce_vs)
                cx_vs, cy_vs = w // 2, int(h * 0.54)
                draw.ellipse([(cx_vs - r_vs, cy_vs - r_vs), (cx_vs + r_vs, cy_vs + r_vs)], fill=(15, 23, 42, 240), outline=theme["primary_neon"], width=3)
                font_vs = get_clean_font(int(22 * bounce_vs), font_type="bold")
                draw.text((cx_vs, cy_vs), "VS", fill=theme["primary_neon"], font=font_vs, anchor="mm")

        elif num_cutouts == 3:
            # Trio Stage Lineup (e.g. Rohan on left, Mother in center hero, Brother on right)
            c_1, c_2, c_3 = processed_cutouts[0], processed_cutouts[1], processed_cutouts[2]

            # Entity 1 (Left): enters at t=0.0s
            slide_1 = spring_bounce(t, duration=0.35, overshoot=0.08)
            tx1 = int(w * 0.20 - c_1.width // 2)
            x1 = int(tx1 - w * 0.50 * (1.0 - slide_1))
            y1 = int(h * 0.54 - c_1.height // 2)
            sh_1, off_1 = create_cutout_drop_shadow(c_1, blur_radius=14, offset=(5, 12), shadow_opacity=0.40)
            frame.paste(sh_1, (x1 + off_1[0], y1 + off_1[1]), mask=sh_1)
            frame.paste(c_1, (x1, y1), mask=c_1)
            if entity_labels and len(entity_labels) > 0 and slide_1 > 0.5:
                draw_cutout_name_pill(draw, entity_labels[0], int(w * 0.20), y1 + c_1.height, theme, alpha=slide_1)

            # Entity 2 (Center Hero): enters at t=0.60s (staggered!)
            t_arr2 = arrival_times[1]
            if t >= t_arr2:
                t_sub2 = max(0.0, t - t_arr2)
                slide_2 = spring_bounce(t_sub2, duration=0.35, overshoot=0.08)
                tx2 = int(w * 0.50 - c_2.width // 2)
                x2 = tx2
                y2 = int((h * 0.50 - c_2.height // 2) + h * 0.25 * (1.0 - slide_2))
                sh_2, off_2 = create_cutout_drop_shadow(c_2, blur_radius=16, offset=(6, 14), shadow_opacity=0.45)
                frame.paste(sh_2, (x2 + off_2[0], y2 + off_2[1]), mask=sh_2)
                frame.paste(c_2, (x2, y2), mask=c_2)
                if entity_labels and len(entity_labels) > 1 and slide_2 > 0.5:
                    draw_cutout_name_pill(draw, entity_labels[1], int(w * 0.50), y2 + c_2.height, theme, alpha=slide_2)

            # Entity 3 (Right): enters at t=1.20s (staggered!)
            t_arr3 = arrival_times[2]
            if t >= t_arr3:
                t_sub3 = max(0.0, t - t_arr3)
                slide_3 = spring_bounce(t_sub3, duration=0.35, overshoot=0.08)
                tx3 = int(w * 0.80 - c_3.width // 2)
                x3 = int(tx3 + w * 0.50 * (1.0 - slide_3))
                y3 = int(h * 0.54 - c_3.height // 2)
                sh_3, off_3 = create_cutout_drop_shadow(c_3, blur_radius=14, offset=(5, 12), shadow_opacity=0.40)
                frame.paste(sh_3, (x3 + off_3[0], y3 + off_3[1]), mask=sh_3)
                frame.paste(c_3, (x3, y3), mask=c_3)
                if entity_labels and len(entity_labels) > 2 and slide_3 > 0.5:
                    draw_cutout_name_pill(draw, entity_labels[2], int(w * 0.80), y3 + c_3.height, theme, alpha=slide_3)

        else:
            # 4 Entities: 2x2 Clean Staggered Grid
            quad_positions = [
                (int(w * 0.28), int(h * 0.38), -1),
                (int(w * 0.72), int(h * 0.38), 1),
                (int(w * 0.28), int(h * 0.64), -1),
                (int(w * 0.72), int(h * 0.64), 1),
            ]
            for qi, (target_cx, target_cy, sdir) in enumerate(quad_positions[:num_cutouts]):
                t_arr = arrival_times[qi]
                if t >= t_arr:
                    c_q = processed_cutouts[qi]
                    t_sub = max(0.0, t - t_arr)
                    s_val = spring_bounce(t_sub, duration=0.35, overshoot=0.08)
                    qx = int((target_cx - c_q.width // 2) + sdir * w * 0.40 * (1.0 - s_val))
                    qy = int(target_cy - c_q.height // 2)
                    sh_q, off_q = create_cutout_drop_shadow(c_q, blur_radius=14, offset=(4, 10), shadow_opacity=0.40)
                    frame.paste(sh_q, (qx + off_q[0], qy + off_q[1]), mask=sh_q)
                    frame.paste(c_q, (qx, qy), mask=c_q)
                    if entity_labels and len(entity_labels) > qi and s_val > 0.5:
                        draw_cutout_name_pill(draw, entity_labels[qi], target_cx, qy + c_q.height, theme, alpha=s_val)

        # -------------------------------------------------------------------
        # LAYER 5: Foreground Flying 3D Props (Close-up tumbling cash with motion blur)
        # -------------------------------------------------------------------
        props_engine.render_layer(frame, t=t, plane="fg")

        # -------------------------------------------------------------------
        # LAYER 6: Viewfinder Brackets / Camera Reticles: COMPLETELY OMITTED
        # -------------------------------------------------------------------

        # -------------------------------------------------------------------
        # LAYER 7: Sleek Glassmorphism Badges / Stacked Cards per Layout Mode
        # -------------------------------------------------------------------
        if layout_mode == "floating_card":
            card_title = meta.get("giant_word", "KEY INSIGHT")
            card_sub = "RECLAIMING ANCIENT STRENGTH & GLORY"
            draw_sleek_floating_topic_card(draw, title=card_title, subtitle=card_sub, width=w, y_pos=int(h * 0.16), theme=theme, t=t)
        elif layout_mode == "portal_halo":
            pill_text = (meta["intro_phrase"].upper() + " " + meta["giant_word"]).strip() or "ANCIENT ERA"
            draw_glassmorphism_pill_badge(draw, text=pill_text, width=w, y_pos=int(h * 0.86), theme=theme, t=t, badge_type="pill")
        elif layout_mode == "heritage_pedestal":
            draw_glassmorphism_pill_badge(draw, text="THOUSANDS OF YEARS OF HERITAGE", width=w, y_pos=int(h * 0.86), theme=theme, t=t, badge_type="pill")
        elif meta.get("is_alert"):
            draw_scam_alert_card(draw, title=meta.get("alert_title", "SCAM ALERT"), subtitle=meta.get("alert_sub", scene_text), width=w, y_pos=int(h * 0.85), theme=theme, t=t)
        elif is_bauhaus:
            draw_glassmorphism_pill_badge(draw, text="after", width=w, y_pos=int(h * 0.12), theme=theme, t=t, badge_type="after")
            draw_curved_pointer_callouts(draw, w, h, bauhaus_callouts, theme, t=t)

        # -------------------------------------------------------------------
        # LAYER 8: Dynamic Purposeful Camera Zoom In / Zoom Out (Zero Jitter)
        # -------------------------------------------------------------------
        cam_scale = get_purposeful_camera_zoom(t, duration, scene_text=scene_text, arrival_times=arrival_times)
        if abs(cam_scale - 1.0) > 0.001:
            crop_w = int(w / cam_scale)
            crop_h = int(h / cam_scale)
            crop_x = max(0, min(w - crop_w, (w - crop_w) // 2))
            crop_y = max(0, min(h - crop_h, int((h - crop_h) * 0.50)))
            frame = frame.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)).resize((w, h), Image.BILINEAR)

        # Stream frame to FFmpeg rawvideo pipe
        raw_bytes = frame.tobytes()
        proc.stdin.write(raw_bytes)

        del frame, draw
        if frame_idx % 25 == 0:
            release_system_memory()

    proc.stdin.close()
    proc.wait()
    release_system_memory()

    print(f"🎬 [Color Anime Engine V2.5] Successfully rendered kinetic motion clip: {os.path.basename(output_mp4)} ({duration:.1f}s)")
    return output_mp4
