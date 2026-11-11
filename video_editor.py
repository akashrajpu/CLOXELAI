"""
=============================================================================
PRO DYNAMIC SCENE & MULTI-CHARACTER ULTRA VIDEO EDITOR
=============================================================================
Description: Advanced video editor supporting:
  1. Script-driven Dynamic Multi-Character Cutout Overlay (Left / Right / Center).
  2. Selective Background Removal (Remove BG ONLY for dialogue characters, keep full BG for scene backdrop).
  3. Dynamic Auto-Positioning Subtitles & Color Animations (Top, Center, Bottom, Rainbow/Gold/White).
  4. Web & AI Character Photo Fetching.
=============================================================================
"""

import os
import re
import math
import random
import gc
import warnings
import numpy as np
import textwrap
import subprocess
try:
    from gemini_animator import generate_gemini_cartoon_animation
except Exception:
    generate_gemini_cartoon_animation = None

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, VideoClip, concatenate_audioclips, concatenate_videoclips, CompositeAudioClip
    from moviepy.audio.fx.all import audio_loop
except ImportError:
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        from moviepy.video.VideoClip import ImageClip, ColorClip, VideoClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        from moviepy.audio.audio_clip import concatenate_audioclips, CompositeAudioClip
        from moviepy.audio.fx.audio_loop import audio_loop
    except ImportError:
        from moviepy import VideoFileClip, AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, VideoClip
        concatenate_audioclips = None
        concatenate_videoclips = None
        CompositeAudioClip = None
        audio_loop = None
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

warnings.filterwarnings("ignore")

if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

def release_system_memory():
    """
    Forces Python Garbage Collection + Linux C-heap memory reclamation (malloc_trim).
    Prevents Render 512MB RAM Out-Of-Memory (OOM) crashes.
    """
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL('libc.so.6').malloc_trim(0)
    except Exception:
        pass

try:
    from bg_remover import remove_background
except ImportError:
    remove_background = None

try:
    from web_image_fetcher import fetch_web_image
except ImportError:
    fetch_web_image = None

COLOR_PALETTES = [
    "#FFEE00",
    "#00FFFF",
    "#FF0055",
    "#00FF66",
    "#FF9900",
    "#FFFFFF"
]

POSITIONS = ["center", "bottom", "top"]

_FONT_CACHE = {}

def check_font_supports_devanagari(f_obj):
    if f_obj is None:
        return False
    try:
        bbox = f_obj.getbbox("शिव")
        return bool(bbox and (bbox[3] - bbox[1]) > 0 and (bbox[2] - bbox[0]) > 0)
    except Exception:
        return False

def get_font(font_path_arg: str, fs: int, has_devanagari: bool):
    cache_key = (font_path_arg, fs, has_devanagari)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    font_obj = None
    
    hindi_font_candidates = [
        "./fonts/YatraOne-Regular.ttf",
        "./fonts/RozhaOne-Regular.ttf",
        "./fonts/Kalam-Bold.ttf",
        "./fonts/Mukta-Bold.ttf",
        "./fonts/NotoSansDevanagari-Bold.ttf",
        "./fonts/NotoSansDevanagari-Regular.ttf",
        "./fonts/Modak-Regular.ttf",
        "./fonts/Ranga-Bold.ttf",
        "./fonts/TiroDevanagariHindi-Regular.ttf",
        "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc",
        "/System/Library/Fonts/Supplemental/DevanagariMT.ttc",
        "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
    ]

    base_name = os.path.basename(font_path_arg or "").lower()
    is_default_generic_font = (not font_path_arg or "arial" in base_name or "default" in base_name)

    # 1. If user explicitly chose a font, try loading it
    if font_path_arg and os.path.exists(font_path_arg):
        if not (has_devanagari and is_default_generic_font):
            try:
                font_obj = ImageFont.truetype(font_path_arg, fs)
                # CRITICAL: Verify that the loaded font can actually render Devanagari text!
                # If font cannot render Devanagari (like legacy non-Unicode AMS fonts with 0 height), discard it!
                if has_devanagari and not check_font_supports_devanagari(font_obj):
                    font_obj = None
            except Exception:
                font_obj = None

    # 2. If text contains Hindi/Devanagari and no working font loaded yet
    if font_obj is None and has_devanagari:
        for df_path in hindi_font_candidates:
            if os.path.exists(df_path):
                try:
                    candidate_obj = ImageFont.truetype(df_path, fs)
                    if check_font_supports_devanagari(candidate_obj):
                        font_obj = candidate_obj
                        break
                except Exception:
                    pass

    # 3. If still None, try font_path_arg as requested
    if font_obj is None and font_path_arg and os.path.exists(font_path_arg):
        try:
            font_obj = ImageFont.truetype(font_path_arg, fs)
        except Exception:
            pass

    # 4. Fallback candidates if still None
    if font_obj is None:
        fallback_candidates = hindi_font_candidates + [
            "arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf"
        ]
        for font_candidate in fallback_candidates:
            if os.path.exists(font_candidate):
                try:
                    font_obj = ImageFont.truetype(font_candidate, fs)
                    break
                except Exception:
                    pass

    if font_obj is None:
        font_obj = ImageFont.load_default()

    _FONT_CACHE[cache_key] = font_obj
    return font_obj

def create_dynamic_animated_text(
    full_text: str,
    size: tuple,
    duration: float,
    font_path: str = "./fonts/Arial.ttf",
    font_size: int = 220,
    text_color: str = "random",
    text_position: str = "random",
    fps: int = 20,
    is_ultra_mode: bool = False,
    category_style: str = "history"
) -> VideoClip:
    """
    Generates dynamic multi-color subtitles.
    Category Style:
      - 'history' / 'ancient': Renders torn parchment paper box behind text (Photo #1).
      - 'cartoon' / 'modern' / 'clean': Renders dynamic white text with highlighted keywords (Photo #2).
    """
    total_frames = int(duration * fps)
    if total_frames <= 0: total_frames = 1
    
    has_devanagari = any('\u0900' <= char <= '\u097F' for char in full_text)
    full_text = full_text.strip()
    words = full_text.split()
    
    target_width = int(size[0] * 0.78)
    max_font_size = int(size[1] * 0.075) if size[0] > size[1] else int(size[0] * 0.08)
    user_font_size = min(font_size, max_font_size) if font_size > 50 else max_font_size

    highlight_color = random.choice(COLOR_PALETTES) if text_color == "random" else text_color
    chosen_pos = random.choice(POSITIONS) if text_position == "random" else text_position
    ultra_side_mode = "center"

    def load_font(fs):
        return get_font(font_path, fs, has_devanagari)

    cache = {'t': -1, 'img': None}

    def get_img(t):
        if cache['t'] == t:
            return cache['img']
            
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if not words:
            cache['t'] = t
            cache['img'] = img
            return img
            
        words_per_chunk = 3
        total_chunks = max(1, (len(words) + words_per_chunk - 1) // words_per_chunk)
        
        progress = min(0.999, max(0.0, t / float(duration))) if duration > 0 else 0.0
        chunk_idx = min(total_chunks - 1, int(progress * total_chunks))
        chunk_words = words[chunk_idx * words_per_chunk : (chunk_idx + 1) * words_per_chunk]
        
        rel_t = (progress * total_chunks) - chunk_idx
        word_in_chunk_idx = min(len(chunk_words) - 1, max(0, int(rel_t * len(chunk_words))))
            
        active_font = load_font(user_font_size)

        if is_ultra_mode and category_style in ["history", "ancient"]:
            chunk_str = " ".join(chunk_words)
            parchment_img = create_parchment_subtitle_box(chunk_str, size, font_size=user_font_size)
            px = (size[0] - parchment_img.width) // 2
            py = size[1] - parchment_img.height - int(size[1] * 0.06)
            img.paste(parchment_img, (px, py), mask=parchment_img)
            cache['t'] = t
            cache['img'] = img
            return img

        scene_theme_color = highlight_color if (highlight_color and highlight_color != "random") else "#FFD700"

        line_total_w = 0
        word_font_data = []
        for w_i, w in enumerate(chunk_words):
            is_active = (w_i == word_in_chunk_idx)
            if is_ultra_mode:
                base_sz = int(user_font_size * (1.20 if is_active else 0.85))
            else:
                base_sz = user_font_size
            w_f = load_font(base_sz)
            wb = draw.textbbox((0, 0), w, font=w_f)
            word_w = wb[2] - wb[0]
            sb = draw.textbbox((0, 0), " ", font=w_f)
            space_w = sb[2] - sb[0]
            word_font_data.append((w, base_sz, word_w, space_w, is_active))
            line_total_w += word_w + space_w

        if word_font_data:
            line_total_w -= word_font_data[-1][3]

        scale_down = 1.0
        if line_total_w > target_width and line_total_w > 0:
            scale_down = target_width / float(line_total_w)

        actual_line_w = 0
        final_render_data = []
        for w, base_sz, _, _, is_active in word_font_data:
            scaled_sz = max(14, int(base_sz * scale_down))
            w_font = load_font(scaled_sz)
            wb = draw.textbbox((0, 0), w, font=w_font)
            word_w = wb[2] - wb[0]
            sb = draw.textbbox((0, 0), " ", font=w_font)
            space_w = sb[2] - sb[0]
            final_render_data.append((w, w_font, word_w, space_w, is_active))
            actual_line_w += word_w + space_w

        if final_render_data:
            actual_line_w -= final_render_data[-1][3]

        if actual_line_w > target_width and actual_line_w > 0:
            adj = target_width / float(actual_line_w)
            actual_line_w = 0
            adjusted_render_data = []
            for w, w_font, _, _, is_active in final_render_data:
                adj_sz = max(12, int(w_font.size * adj))
                w_font_adj = load_font(adj_sz)
                wb = draw.textbbox((0, 0), w, font=w_font_adj)
                word_w = wb[2] - wb[0]
                sb = draw.textbbox((0, 0), " ", font=w_font_adj)
                space_w = sb[2] - sb[0]
                adjusted_render_data.append((w, w_font_adj, word_w, space_w, is_active))
                actual_line_w += word_w + space_w
            if adjusted_render_data:
                actual_line_w -= adjusted_render_data[-1][3]
            final_render_data = adjusted_render_data

        line_spacing = int(active_font.size * 1.25)
        if chosen_pos == "top":
            y_text = int(size[1] * 0.12)
        elif chosen_pos == "bottom":
            y_text = size[1] - line_spacing - int(size[1] * 0.12)
        else:
            y_text = (size[1] - line_spacing) // 2

        current_x = (size[0] - actual_line_w) // 2
        min_x_margin = int(size[0] * 0.12)
        current_x = max(min_x_margin, current_x)

        for w, w_font, word_w, curr_space_w, is_active in final_render_data:
            if is_ultra_mode:
                if is_active:
                    color = scene_theme_color
                else:
                    color = "#FFFFFF"
            else:
                color = highlight_color if is_active else "#FFFFFF"

            shadow_offset = max(2, int(w_font.size * 0.05))
            draw.text((current_x + shadow_offset, y_text + shadow_offset), w, font=w_font, fill=(0, 0, 0, 240))
            draw.text((current_x, y_text), w, font=w_font, fill=color)

            current_x += word_w + curr_space_w
            
        cache['t'] = t
        cache['img'] = img
        return img
        
    def make_frame(t):
        return np.array(get_img(t).convert('RGB'))
        
    def make_mask(t):
        return np.array(get_img(t).split()[3]) / 255.0
    
    clip = VideoClip(make_frame, duration=duration).set_fps(fps)
    mask_clip = VideoClip(make_mask, ismask=True, duration=duration).set_fps(fps)
    return clip.set_mask(mask_clip)

def create_multi_character_ultra_clip(
    scene_info: dict,
    duration: float,
    size: tuple = (1920, 1080),
    fps: int = 20
) -> VideoClip:
    """
    Creates a Multi-Character Ultra Scene:
      - 1 Full Backdrop Image (Background intact, NO BG removal).
      - Selective Dialogue Characters Cutout (BG removed for characters like Karna, Angad, Arjuna).
      - Character Auto-Positioning (Left / Right / Center side by side).
    """
    w, h = size
    bg_img_path = scene_info.get("background_image") or scene_info.get("video")
    char_list = scene_info.get("characters", [])
    
    if bg_img_path and os.path.exists(bg_img_path):
        bg_pil = Image.open(bg_img_path).convert("RGBA").resize(size, Image.LANCZOS)
    else:
        bg_pil = Image.new("RGBA", size, (25, 18, 12, 255))
        
    processed_chars = []
    
    for idx, c_info in enumerate(char_list):
        c_path = c_info.get("image")
        c_pos = c_info.get("pos", "left" if idx % 2 == 0 else "right")
        
        if c_path and os.path.exists(c_path):
            char_pil = Image.open(c_path).convert("RGBA")
            if remove_background:
                fg_cutout = remove_background(char_pil)
            else:
                fg_cutout = char_pil
                
            target_h = int(h * 0.82)
            aspect = fg_cutout.width / fg_cutout.height
            target_w = int(target_h * aspect)
            fg_resized = fg_cutout.resize((target_w, target_h), Image.LANCZOS)
            
            if c_pos == "left":
                pos_x = int(w * 0.04)
            elif c_pos == "right":
                pos_x = w - target_w - int(w * 0.04)
            else:
                pos_x = (w - target_w) // 2
                
            pos_y = h - target_h
            processed_chars.append({"img": fg_resized, "x": pos_x, "y": pos_y, "pos": c_pos})

    def get_frame(t):
        progress = t / duration if duration > 0 else 0
        
        bg_scale = 1.0 + (0.06 * progress)
        bg_w_s = int(w * bg_scale)
        bg_h_s = int(h * bg_scale)
        bg_s = bg_pil.resize((bg_w_s, bg_h_s), Image.BILINEAR)
        
        crop_x = (bg_w_s - w) // 2
        crop_y = (bg_h_s - h) // 2
        canvas = bg_s.crop((crop_x, crop_y, crop_x + w, crop_y + h)).convert("RGBA")
        
        for c in processed_chars:
            c_img = c["img"]
            float_y = int(8 * math.sin(progress * math.pi * 2))
            final_x = c["x"]
            final_y = c["y"] + float_y
            
            canvas.paste(c_img, (final_x, final_y), mask=c_img)
            
        return np.array(canvas.convert("RGB"))

    return VideoClip(get_frame, duration=duration).set_fps(fps)

def generate_ink_brush_mask(size: tuple) -> Image.Image:
    """Generates a procedural high-resolution Ink Brush / Paint Reveal Mask PNG with rough organic edges."""
    w, h = size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    
    margin_w = int(w * 0.04)
    margin_h = int(h * 0.04)
    draw.rectangle([margin_w, margin_h, w - margin_w, h - margin_h], fill=255)
    
    random.seed(42)
    for x in range(margin_w, w - margin_w, 8):
        jitter_top = random.randint(-18, 25)
        jitter_bot = random.randint(-18, 25)
        draw.line([(x, margin_h + jitter_top), (x, margin_h)], fill=255, width=6)
        draw.line([(x, h - margin_h), (x, h - margin_h + jitter_bot)], fill=255, width=6)
        
    for y in range(margin_h, h - margin_h, 8):
        jitter_left = random.randint(-18, 25)
        jitter_right = random.randint(-18, 25)
        draw.line([(margin_w + jitter_left, y), (margin_w, y)], fill=255, width=6)
        draw.line([(w - margin_w, y), (w - margin_w + jitter_right, y)], fill=255, width=6)
        
    return mask.filter(ImageFilter.GaussianBlur(radius=6))

def create_parchment_background(size, color_theme="warm"):
    w, h = size
    if color_theme == "warm":
        base_color = (245, 230, 210)
    else:
        base_color = (220, 230, 240)
    img = Image.new("RGB", (w, h), base_color)
    np_noise = np.random.randint(-15, 15, (h, w, 3), dtype=np.int16)
    np_img = np.array(img, dtype=np.int16) + np_noise
    np_img = np.clip(np_img, 0, 255).astype(np.uint8)
    return Image.fromarray(np_img)

def apply_color_filter(pil_img: Image.Image, filter_style: str = "warm_epic") -> Image.Image:
    """Applies premium cinematic color grading LUTs, Film Grain, Dust, Haze Smoke & Vintage Paper Textures."""
    if not filter_style or str(filter_style).lower() in ["none", "normal", "original", "clean", "no_filter", "raw"]:
        return pil_img.copy().convert("RGB")

    img = pil_img.copy().convert("RGB")
    w, h = img.size

    if filter_style == "warm_epic":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.30)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.20)
        overlay = Image.new("RGB", img.size, (255, 185, 110))
        img = Image.blend(img, overlay, alpha=0.15)
    elif filter_style == "vintage_parchment":
        gray = img.convert("L")
        sepia = ImageOps.colorize(gray, "#261508", "#ffe6cc")
        img = Image.blend(img, sepia, alpha=0.80)
    elif filter_style == "dramatic_cinematic":
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.35)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.15)
    elif filter_style == "cyber_teal_orange":
        gray = img.convert("L")
        teal_orange = ImageOps.colorize(gray, "#0d2b3a", "#ff9e42")
        img = Image.blend(img, teal_orange, alpha=0.60)
    elif filter_style == "royal_gold":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.40)
        overlay = Image.new("RGB", img.size, (255, 215, 0))
        img = Image.blend(img, overlay, alpha=0.18)
    elif filter_style == "dark_gothic":
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.45)
        gray = img.convert("L")
        gothic = ImageOps.colorize(gray, "#110b18", "#d1c4e9")
        img = Image.blend(img, gothic, alpha=0.55)
    elif filter_style == "neon_cyberpunk":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.60)
        overlay = Image.new("RGB", img.size, (0, 255, 230))
        img = Image.blend(img, overlay, alpha=0.12)
    elif filter_style == "golden_sunburst":
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.10)
        overlay = Image.new("RGB", img.size, (255, 140, 0))
        img = Image.blend(img, overlay, alpha=0.16)
    elif filter_style == "emerald_fantasy":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.35)
        gray = img.convert("L")
        emerald = ImageOps.colorize(gray, "#042014", "#a7f3d0")
        img = Image.blend(img, emerald, alpha=0.45)
    elif filter_style == "crimson_warrior":
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.40)
        gray = img.convert("L")
        crimson = ImageOps.colorize(gray, "#2b0404", "#fca5a5")
        img = Image.blend(img, crimson, alpha=0.50)
    elif filter_style == "vintage_sepia_film":
        gray = img.convert("L")
        sepia = ImageOps.colorize(gray, "#3b220b", "#fde68a")
        img = Image.blend(img, sepia, alpha=0.70)
    elif filter_style == "ice_blue_cyber":
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.50)
        overlay = Image.new("RGB", img.size, (56, 189, 248))
        img = Image.blend(img, overlay, alpha=0.18)

    paper_tex = create_parchment_background((w, h), color_theme="warm")
    img = Image.blend(img, paper_tex, alpha=0.18)

    light_leak = Image.new("RGB", (w, h), (255, 130, 40))
    glow_mask = Image.new("L", (w, h), 0)
    g_draw = ImageDraw.Draw(glow_mask)
    g_draw.ellipse([-int(w*0.2), -int(h*0.2), int(w*0.6), int(h*0.6)], fill=180)
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(radius=80))
    img = Image.composite(light_leak, img, glow_mask)

    return img

def create_history_spotlight_overlay(base_img: Image.Image, progress: float, dark_bg: Image.Image = None) -> Image.Image:
    """
    Creates the dynamic moving dark mask spotlight reveal animation for History Mode (matching user screenshots 1, 2, 3):
      - Outer region: Darkened monochromatic / vignette overlay (0.28x brightness + desaturated).
      - Inner spotlight window: Moves dynamically across the frame revealing warm colored image with glowing organic reveal border.
    """
    w, h = base_img.size
    
    if dark_bg is None:
        dark_bg = base_img.convert("L").convert("RGB")
        dark_bg = ImageEnhance.Brightness(dark_bg).enhance(0.28)
    
    mw, mh = max(1, w // 4), max(1, h // 4)
    spotlight_mask = Image.new("L", (mw, mh), 0)
    s_draw = ImageDraw.Draw(spotlight_mask)
    
    spotlight_cx = int(mw * (0.35 + 0.30 * math.sin(progress * math.pi)))
    spotlight_cy = int(mh * (0.45 + 0.10 * math.cos(progress * math.pi)))
    
    spotlight_radius_x = int(mw * (0.34 + 0.05 * math.sin(progress * math.pi * 2)))
    spotlight_radius_y = int(mh * (0.44 + 0.05 * math.cos(progress * math.pi * 2)))
    
    s_draw.ellipse([
        spotlight_cx - spotlight_radius_x,
        spotlight_cy - spotlight_radius_y,
        spotlight_cx + spotlight_radius_x,
        spotlight_cy + spotlight_radius_y
    ], fill=255)

    spotlight_mask = spotlight_mask.filter(ImageFilter.GaussianBlur(radius=6))
    spotlight_mask = spotlight_mask.resize((w, h), Image.BILINEAR)
    
    result_img = Image.composite(base_img.convert("RGB"), dark_bg, spotlight_mask)
    return result_img.convert("RGBA")

def create_parchment_subtitle_box(text: str, size: tuple, font_size: int = 180) -> Image.Image:
    """
    Renders subtitles inside an authentic Off-White Cream Torn Paper Scroll Banner
    with bold distressed Crimson Rust Red font (matching user screenshots 1, 2, 3!).
    """
    w, h = size
    box_w = int(w * 0.85)
    box_h = int(h * 0.22)
    
    parchment = Image.new("RGBA", (box_w, box_h), (255, 253, 232, 245))
    
    torn_mask = Image.new("L", (box_w, box_h), 255)
    t_draw = ImageDraw.Draw(torn_mask)
    
    random.seed(101)
    for x in range(0, box_w, 6):
        jitter_t = random.randint(0, 14)
        jitter_b = random.randint(0, 14)
        t_draw.line([(x, 0), (x, jitter_t)], fill=0, width=4)
        t_draw.line([(x, box_h - jitter_b), (x, box_h)], fill=0, width=4)
        
    for y in range(0, box_h, 6):
        jitter_l = random.randint(0, 14)
        jitter_r = random.randint(0, 14)
        t_draw.line([(0, y), (jitter_l, y)], fill=0, width=4)
        t_draw.line([(box_w - jitter_r, y), (box_w, y)], fill=0, width=4)
        
    torn_mask = torn_mask.filter(ImageFilter.GaussianBlur(radius=2))
    parchment.putalpha(torn_mask)
    
    has_dev = any('\u0900' <= char <= '\u097F' for char in text)
    if has_dev:
        font_candidates = [
            "./fonts/NotoSansDevanagari-Bold.ttf",
            "./fonts/NotoSansDevanagari-Regular.ttf",
            "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc",
            "/System/Library/Fonts/Supplemental/DevanagariMT.ttc"
        ]
    else:
        font_candidates = [
            "./fonts/anton.ttf",
            "./fonts/bebas.ttf",
            "./fonts/RaceFlow.ttf",
            "./fonts/CarbonBlock.ttf"
        ]
    
    optimal_font_size = int(box_h * 0.35)
    
    chosen_font = None
    for fc in font_candidates:
        if os.path.exists(fc):
            try:
                chosen_font = ImageFont.truetype(fc, optimal_font_size)
                break
            except Exception:
                pass
    if not chosen_font:
        try:
            chosen_font = get_font("./fonts/Arial.ttf", optimal_font_size, has_dev)
        except Exception:
            chosen_font = ImageFont.load_default()

    words = text.upper().split()
    mid = max(1, (len(words) + 1) // 2)
    l1 = " ".join(words[:mid])
    l2 = " ".join(words[mid:])
    lines = [l1]
    if l2:
        lines.append(l2)

    text_color = (200, 50, 0, 255)
    
    draw_p = ImageDraw.Draw(parchment)
    
    if hasattr(chosen_font, "size"):
        line_h = int(chosen_font.size * 1.20)
    else:
        line_h = int(optimal_font_size * 1.20)
        
    y_pos = (box_h - (len(lines) * line_h)) // 2
    
    for line in lines:
        try:
            tb = draw_p.textbbox((0, 0), line, font=chosen_font)
            lw = tb[2] - tb[0]
        except Exception:
            lw = len(line) * optimal_font_size * 0.5
            
        x_pos = (box_w - lw) // 2
        draw_p.text((x_pos + 2, y_pos + 2), line, font=chosen_font, fill=(70, 15, 0, 180))
        draw_p.text((x_pos, y_pos), line, font=chosen_font, fill=text_color)
        y_pos += line_h

    return parchment

def create_ultra_photo_motion_clip(
    photo_path: str,
    fg_photo_path: str = None,
    duration: float = 5.0,
    size: tuple = (540, 960),
    filter_style: str = "warm_epic",
    cutout_pos: str = "left",
    motion_type: str = "zoom_in",
    fps: int = 15
) -> VideoClip:
    """Creates an Ultra Photo Motion Video Clip with Ink Brush Mask Edges, Smoke Haze, Particles, & Dynamic Zoom/Pan."""
    w, h = size
    print(f"🎨 [Ultra Engine] Generating 3D Ultra Clip (BG: {photo_path}, FG: {fg_photo_path}, Filter: {filter_style}, Motion: {motion_type.upper()})...")
    
    # Robust asset discovery: If photo_path is missing or invalid, check fg_photo_path or any valid image in the directory
    if not photo_path or not os.path.exists(photo_path) or os.path.getsize(photo_path) < 1000:
        if fg_photo_path and os.path.exists(fg_photo_path) and os.path.getsize(fg_photo_path) > 1000:
            print(f"🔄 [Ultra Motion Fallback] Primary photo '{photo_path}' missing, using secondary asset '{fg_photo_path}' as base photo.")
            photo_path = fg_photo_path
            fg_photo_path = None
        else:
            p_dir = os.path.dirname(photo_path) if photo_path else "."
            if p_dir and os.path.exists(p_dir):
                for candidate in os.listdir(p_dir):
                    if candidate.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) and not candidate.startswith("tmp_sub"):
                        cand_full = os.path.join(p_dir, candidate)
                        if os.path.getsize(cand_full) > 5000:
                            photo_path = cand_full
                            print(f"🔄 [Ultra Motion Fallback] Discovered valid photo candidate in job dir: '{photo_path}'")
                            break

    if not photo_path or not os.path.exists(photo_path):
        bg_pil = create_parchment_background(size, color_theme="warm")
        def get_fallback_frame(t):
            return np.array(bg_pil.convert("RGB"))
        return VideoClip(get_fallback_frame, duration=duration).set_fps(fps)

    is_video_file = str(photo_path).lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))
    orig_pil = None
    if is_video_file and os.path.exists(photo_path):
        try:
            v_temp = VideoFileClip(photo_path)
            frame_t = min(1.0, v_temp.duration / 2.0)
            raw_frame = v_temp.get_frame(frame_t)
            orig_pil = Image.fromarray(raw_frame).convert("RGBA")
            v_temp.close()
        except Exception:
            orig_pil = None
    else:
        try:
            orig_pil = Image.open(photo_path).convert("RGBA")
        except Exception:
            orig_pil = None

    if orig_pil is None and fg_photo_path and os.path.exists(fg_photo_path):
        try:
            orig_pil = Image.open(fg_photo_path).convert("RGBA")
            print(f"🔄 [Ultra Motion Fallback] Successfully opened secondary asset '{fg_photo_path}' as base photo.")
            fg_photo_path = None
        except Exception:
            orig_pil = None

    if orig_pil is None:
        bg_pil = create_parchment_background(size, color_theme="warm")
        def get_fallback_frame(t):
            return np.array(bg_pil.convert("RGB"))
        return VideoClip(get_fallback_frame, duration=duration).set_fps(fps)

    if orig_pil.width > 1280 or orig_pil.height > 1280:
        orig_pil.thumbnail((1280, 1280), Image.LANCZOS)

    bg_pil = apply_color_filter(orig_pil.convert("RGB"), filter_style=filter_style)
    aspect_bg = bg_pil.width / bg_pil.height
    canvas_aspect = w / h
    if aspect_bg > canvas_aspect:
        bg_h_fit = h
        bg_w_fit = int(h * aspect_bg)
    else:
        bg_w_fit = w
        bg_h_fit = int(w / aspect_bg)
    bg_pil = bg_pil.resize((bg_w_fit, bg_h_fit), Image.LANCZOS)

    has_cutout = False
    fg_resized = None
    cutout_src_path = fg_photo_path if (fg_photo_path and os.path.exists(fg_photo_path) and fg_photo_path != photo_path) else None
    
    if remove_background and cutout_src_path:
        try:
            char_orig = Image.open(cutout_src_path).convert("RGBA")
            if char_orig.width > 1280 or char_orig.height > 1280:
                char_orig.thumbnail((1280, 1280), Image.LANCZOS)
            fg_pil = remove_background(char_orig)
            if fg_pil.mode == "RGBA" and fg_pil.getextrema()[3][0] < 255:
                fg_filtered = apply_color_filter(fg_pil.convert("RGB"), filter_style=filter_style)
                fg_filtered.putalpha(fg_pil.split()[3])
                target_fg_h = int(h * 0.85)
                aspect_fg = fg_filtered.width / fg_filtered.height
                target_fg_w = int(target_fg_h * aspect_fg)
                fg_resized = fg_filtered.resize((target_fg_w, target_fg_h), Image.LANCZOS)
                
                ink_mask = generate_ink_brush_mask((fg_resized.width, fg_resized.height))
                cur_alpha = fg_resized.split()[3]
                combined_alpha = Image.composite(cur_alpha, Image.new("L", cur_alpha.size, 0), ink_mask)
                fg_resized.putalpha(combined_alpha)
                has_cutout = True
        except Exception as e_cut:
            print(f"⚠️ Character cutout extraction skip: {e_cut}")
            has_cutout = False

    bg_base_scaled = bg_pil.resize((int(bg_w_fit * 1.25), int(bg_h_fit * 1.25)), Image.LANCZOS)
    bg_w_scaled, bg_h_scaled = bg_base_scaled.size

    dark_bg_full = bg_base_scaled.convert("L").convert("RGB")
    dark_bg_full = ImageEnhance.Brightness(dark_bg_full).enhance(0.28)

    def get_frame(t):
        progress = t / duration if duration > 0 else 0
        
        if motion_type == "zoom_in":
            pan_x_factor = 0.5
            pan_y_factor = 0.5
        elif motion_type == "zoom_out":
            pan_x_factor = 0.5
            pan_y_factor = 0.5
        elif motion_type == "pan_right":
            pan_x_factor = 0.20 + (0.60 * progress)
            pan_y_factor = 0.5
        elif motion_type == "pan_left":
            pan_x_factor = 0.80 - (0.60 * progress)
            pan_y_factor = 0.5
        elif motion_type == "diagonal_fast":
            pan_x_factor = 0.20 + (0.60 * progress)
            pan_y_factor = 0.20 + (0.60 * progress)
        else:
            pan_x_factor = 0.5 + 0.20 * math.sin(progress * math.pi * 2)
            pan_y_factor = 0.5 + 0.20 * math.cos(progress * math.pi * 2)
            
        crop_x = int((bg_w_scaled - w) * pan_x_factor)
        crop_y = int((bg_h_scaled - h) * pan_y_factor)
        crop_x = max(0, min(bg_w_scaled - w, crop_x))
        crop_y = max(0, min(bg_h_scaled - h, crop_y))
        
        frame_canvas = bg_base_scaled.crop((crop_x, crop_y, crop_x + w, crop_y + h)).convert("RGBA")
        
        if filter_style in ["warm_epic", "vintage_parchment", "history", "dramatic_cinematic"]:
            dark_crop = dark_bg_full.crop((crop_x, crop_y, crop_x + w, crop_y + h))
            frame_canvas = create_history_spotlight_overlay(frame_canvas, progress, dark_bg=dark_crop)
        
        if has_cutout and fg_resized:
            cur_fg_w = fg_resized.width
            cur_fg_h = fg_resized.height
            entrance_factor = min(1.0, progress * 4.0)
            slide_offset = int((1.0 - math.pow(entrance_factor, 2)) * w * 0.25)
            
            if cutout_pos == "right":
                fg_x = (w - cur_fg_w) + slide_offset
            else:
                fg_x = 0 - slide_offset
                
            fg_y = h - cur_fg_h
            frame_canvas.paste(fg_resized, (fg_x, fg_y), mask=fg_resized)
            
        return np.array(frame_canvas.convert("RGB"))

    return VideoClip(get_frame, duration=duration).set_fps(fps)

def get_audio_duration_fast(audio_path: str, fallback: float = 5.0) -> float:
    """Uses ffprobe to instantly get audio duration without loading audio into memory."""
    if not audio_path or not os.path.exists(audio_path):
        return fallback
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", os.path.abspath(audio_path)]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        val = float(out)
        if val > 0.3:
            return val
    except Exception:
        pass
    try:
        if AudioFileClip:
            ac = AudioFileClip(audio_path)
            d = float(ac.duration)
            ac.close()
            return d
    except Exception:
        pass
    return fallback

def has_video_stream(filepath: str) -> bool:
    """Verifies that a video file has at least one valid, playable video stream via ffprobe."""
    if not filepath or not os.path.exists(filepath):
        return False
    if str(filepath).lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        return True
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_type",
            "-of", "default=noprint_wrappers=1:nokey=1",
            os.path.abspath(filepath)
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=4).decode().strip()
        return "video" in out.lower()
    except Exception:
        return False

def render_scene_native_ffmpeg(
    scene_output: str,
    video_path: str,
    audio_path: str,
    duration: float,
    text: str,
    target_size: tuple = (960, 540),
    font_path: str = "./fonts/Arial.ttf",
    font_size: int = 40,
    category_style: str = "clean",
    highlight_color: str = "random",
    job_dir: str = "."
) -> bool:
    """
    Ultra-High Speed, Zero-OOM Native FFmpeg Scene Renderer.
    Bypasses MoviePy's heavy in-memory frame processing entirely.
    Uses less than 30MB RAM (Render 512MB RAM safe, 10x faster).
    Renders background video/image, audio sync, and multi-word karaoke animated subtitles natively in C.
    """
    w, h = target_size
    text = (text or "").strip()
    words = text.split()
    
    sub_overlay_files = []
    
    if words:
        ideal_wpc = 3 if (w < h) else 4
        total_chunks = max(1, (len(words) + ideal_wpc - 1) // ideal_wpc)
        words_per_chunk = max(1, (len(words) + total_chunks - 1) // total_chunks)
        chunk_dur = duration / float(total_chunks)
        
        has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
        base_fs = int(h * 0.065) if w > h else int(w * 0.062)
        base_fs = max(18, min(base_fs, 36))
        
        resolved_highlight = random.choice(COLOR_PALETTES) if (not highlight_color or highlight_color == "random") else highlight_color
        
        state_counter = 0
        for c_idx in range(total_chunks):
            c_words = words[c_idx * words_per_chunk : (c_idx + 1) * words_per_chunk]
            if not c_words:
                continue
            c_start = c_idx * chunk_dur
            c_end = (c_idx + 1) * chunk_dur
            
            if category_style in ["history", "ancient"] and not has_devanagari:
                chunk_str = " ".join(c_words)
                try:
                    parchment_img = create_parchment_subtitle_box(chunk_str, (w, h), font_size=base_fs)
                    sub_canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                    px = (w - parchment_img.width) // 2
                    py = h - parchment_img.height - int(h * 0.06)
                    sub_canvas.paste(parchment_img, (px, py), mask=parchment_img)
                    sub_path = os.path.abspath(os.path.join(job_dir, f"tmp_sub_{state_counter}_{random.randint(100, 999)}.png"))
                    sub_canvas.save(sub_path, "PNG")
                    try: sub_canvas.close()
                    except Exception: pass
                    del sub_canvas
                    sub_overlay_files.append((sub_path, c_start, c_end))
                    state_counter += 1
                except Exception as e_p:
                    category_style = "clean"
                    
            if category_style not in ["history", "ancient"] or has_devanagari:
                sub_canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(sub_canvas)
                
                max_box_w = int(w * 0.88)
                pad_x = min(22, max(12, int(w * 0.04)))
                pad_y = 10
                max_text_w = max_box_w - pad_x * 2

                fs = base_fs
                active_font = get_font(font_path, fs, has_devanagari)
                
                # Dynamic shrink
                tot_w = 0
                while fs > 18:
                    active_font = get_font(font_path, fs, has_devanagari)
                    tot_w = sum(draw.textbbox((0, 0), cw, font=active_font)[2] - draw.textbbox((0, 0), cw, font=active_font)[0] for cw in c_words)
                    sp_w = draw.textbbox((0, 0), " ", font=active_font)[2] - draw.textbbox((0, 0), " ", font=active_font)[0]
                    tot_w += sp_w * max(0, len(c_words) - 1)
                    if tot_w <= max_text_w:
                        break
                    fs -= 2
                    
                lines = []
                if tot_w <= max_text_w:
                    lines = [c_words]
                else:
                    mid = max(1, (len(c_words) + 1) // 2)
                    lines = [c_words[:mid], c_words[mid:]]
                    fs = min(30, base_fs)
                    while fs > 16:
                        active_font = get_font(font_path, fs, has_devanagari)
                        max_lw = 0
                        for lw in lines:
                            lw_w = sum(draw.textbbox((0, 0), cw, font=active_font)[2] - draw.textbbox((0, 0), cw, font=active_font)[0] for cw in lw)
                            sp_w = draw.textbbox((0, 0), " ", font=active_font)[2] - draw.textbbox((0, 0), " ", font=active_font)[0]
                            lw_w += sp_w * max(0, len(lw) - 1)
                            if lw_w > max_lw:
                                max_lw = lw_w
                        if max_lw <= max_text_w:
                            break
                        fs -= 2

                rendered_lines = []
                max_line_w = 0
                first_word_done = False
                for line_words in lines:
                    line_metrics = []
                    lw_total = 0
                    for cw in line_words:
                        wb = draw.textbbox((0, 0), cw, font=active_font)
                        ww = wb[2] - wb[0]
                        sb = draw.textbbox((0, 0), " ", font=active_font)
                        sw = sb[2] - sb[0]
                        is_active = (not first_word_done)
                        first_word_done = True
                        line_metrics.append((cw, ww, sw, is_active))
                        lw_total += ww + sw
                    if line_metrics:
                        lw_total -= line_metrics[-1][2]
                    rendered_lines.append((line_metrics, lw_total))
                    if lw_total > max_line_w:
                        max_line_w = lw_total

                box_w = min(max_box_w, max_line_w + pad_x * 2)
                line_height = int(fs * 1.25)
                box_h = (len(rendered_lines) * line_height) + pad_y * 2
                
                margin = int(w * 0.05)
                box_x = (w - box_w) // 2
                box_x = max(margin, min(box_x, w - box_w - margin))
                box_y = int(h * 0.74)
                if box_y + box_h > int(h * 0.90):
                    box_y = int(h * 0.90) - box_h
                
                draw.rounded_rectangle(
                    [(box_x, box_y), (box_x + box_w, box_y + box_h)],
                    radius=12,
                    fill=(10, 6, 24, 215),
                    outline=(255, 215, 0, 230),
                    width=2
                )
                
                curr_y = box_y + pad_y
                for line_metrics, lw_total in rendered_lines:
                    line_start_x = box_x + (box_w - lw_total) // 2
                    curr_x = line_start_x
                    for cw, ww, sw, is_active in line_metrics:
                        col = resolved_highlight if is_active else "#FFFFFF"
                        draw.text((curr_x + 2, curr_y + 2), cw, font=active_font, fill=(0, 0, 0, 230))
                        draw.text((curr_x, curr_y), cw, font=active_font, fill=col)
                        curr_x += ww + sw
                    curr_y += line_height
                    
                sub_path = os.path.abspath(os.path.join(job_dir, f"tmp_sub_{state_counter}_{random.randint(100, 999)}.png"))
                sub_canvas.save(sub_path, "PNG")
                try: sub_canvas.close()
                except Exception: pass
                del sub_canvas
                del draw
                sub_overlay_files.append((sub_path, c_start, c_end))
                state_counter += 1

    input_args = []
    fallback_created = None
    audio_input_idx = 1
    
    if isinstance(video_path, (list, tuple)) and len(video_path) >= 2 and has_video_stream(video_path[0]) and has_video_stream(video_path[1]):
        # Dual-asset rapid cut montage (e.g. contrasting photos/clips cut halfway through scene)
        p0, p1 = video_path[0], video_path[1]
        half_dur = max(0.5, duration / 2.0)
        
        if str(p0).lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            input_args.extend(["-loop", "1", "-t", f"{half_dur:.2f}", "-i", os.path.abspath(p0)])
        else:
            input_args.extend(["-ss", "0", "-t", f"{half_dur:.2f}", "-i", os.path.abspath(p0)])
            
        if str(p1).lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            input_args.extend(["-loop", "1", "-t", f"{half_dur:.2f}", "-i", os.path.abspath(p1)])
        else:
            input_args.extend(["-ss", "0", "-t", f"{half_dur:.2f}", "-i", os.path.abspath(p1)])
            
        input_args.extend(["-i", os.path.abspath(audio_path)])
        audio_input_idx = 2
        
        for sub_path, _, _ in sub_overlay_files:
            input_args.extend(["-i", sub_path])
            
        filter_parts = [
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=25,trim=duration={half_dur:.2f}[v0]",
            f"[1:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=25,trim=duration={half_dur:.2f}[v1]",
            f"[v0][v1]concat=n=2:v=1:a=0[vbg]"
        ]
    else:
        v_single = video_path[0] if isinstance(video_path, (list, tuple)) and video_path else video_path
        if v_single and os.path.exists(v_single) and os.path.getsize(v_single) > 500 and has_video_stream(v_single):
            if str(v_single).lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                input_args.extend(["-loop", "1", "-i", os.path.abspath(v_single)])
            else:
                input_args.extend(["-stream_loop", "-1", "-fflags", "+genpts", "-i", os.path.abspath(v_single)])
        else:
            fallback_created = os.path.abspath(os.path.join(job_dir, f"tmp_fallback_canvas_{random.randint(1000, 9999)}.png"))
            fb_img = Image.new("RGB", (w, h), (15, 10, 35))
            fb_img.save(fallback_created, "PNG")
            input_args.extend(["-loop", "1", "-i", fallback_created])
            
        input_args.extend(["-i", os.path.abspath(audio_path)])
        audio_input_idx = 1
        
        for sub_path, _, _ in sub_overlay_files:
            input_args.extend(["-i", sub_path])
            
        filter_parts = [f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1[vbg]"]
        
    last_v = "vbg"
    for idx, (_, t_s, t_e) in enumerate(sub_overlay_files):
        next_v = f"vsub{idx}" if idx < len(sub_overlay_files) - 1 else "outv"
        sub_input_idx = idx + (audio_input_idx + 1)
        filter_parts.append(f"[{last_v}][{sub_input_idx}:v]overlay=0:0:enable='between(t,{t_s:.2f},{t_e:.2f})'[{next_v}]")
        last_v = next_v
        
    if not sub_overlay_files:
        filter_parts.append(f"[vbg]null[outv]")
        
    filter_complex = ";".join(filter_parts)
    
    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", f"{audio_input_idx}:a",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "26",
        "-r", "25",
        "-g", "50",
        "-threads", "1",
        "-max_muxing_queue_size", "1024",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        "-t", f"{duration:.2f}",
        os.path.abspath(scene_output)
    ]
    
    release_system_memory()
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=240)
        success = (res.returncode == 0 and os.path.exists(scene_output) and os.path.getsize(scene_output) > 1000)
        if not success and res.stderr:
            err_msg = res.stderr.decode(errors="ignore")[-400:]
            print(f"⚠️ Native FFmpeg render notice: {err_msg}")
    except Exception as e_run:
        print(f"⚠️ Native FFmpeg render exception: {e_run}")
        success = False
    finally:
        for sub_path, _, _ in sub_overlay_files:
            if os.path.exists(sub_path):
                try: os.remove(sub_path)
                except Exception: pass
        if fallback_created and os.path.exists(fallback_created):
            try: os.remove(fallback_created)
            except Exception: pass
            
    release_system_memory()
    return success


_AE_SFX_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_AE_SFX_DIR = os.path.join(_AE_SFX_BASE_DIR, "sound_effects")
_AE_SFX_SPLIT_RE = re.compile(r'[\s,.\-!?;:"\'()\[\]{}<>/\\|~`@#$%^&*_+=।॥]+')

# Catalog of Mixkit & local SFX assets mapped directly by filename intent and script context.
# Used EXCLUSIVELY when mode == "ultra" and category is After Effects / VFX / Motion Graphics.
AFTER_EFFECTS_SFX_CATALOG = [
    {
        "file": "mixkit-intro-text-glitch-2950.wav",
        "kind": "intro",
        "volume": 0.34,
        "weight": 4.0,
        "max_clip_dur": 8.0,
        "keywords": [
            "title", "glitch", "breaking", "cyber", "hack", "secret", "mystery",
            "dark", "shocking", "truth", "exposed", "hidden", "ai", "technology",
            "matrix", "digital", "rahasya", "sach", "khulasa", "gupt", "tech",
            "रहस्य", "खुलासा", "गुप्त", "सच", "टेक्नोलॉजी",
        ],
    },
    {
        "file": "mixkit-intro-transition-1146.wav",
        "kind": "intro",
        "volume": 0.34,
        "weight": 3.5,
        "max_clip_dur": 8.0,
        "keywords": [
            "intro", "welcome", "today", "imagine", "beginning", "did you know",
            "swagat", "aaj", "shuru", "kya aap jante", "sochiye",
            "स्वागत", "शुरू", "कल्पना", "क्या आप जानते",
        ],
    },
    {
        "file": "49053354-page-turn-305789.mp3",
        "kind": "event",
        "volume": 0.42,
        "weight": 4.0,
        "keywords": [
            "page", "book", "chapter", "read", "reading", "diary", "journal",
            "notebook", "manuscript", "document", "letter", "note", "archive",
            "story", "ancient", "history", "rule", "lesson", "record", "paper",
            "kitaab", "kitab", "panna", "panne", "kahani", "itihas", "itihaas", "patra",
            "किताब", "पन्ना", "पन्ने", "कहानी", "इतिहास", "डायरी", "चिट्ठी", "दस्तावेज", "नियम",
        ],
    },
    {
        "file": "mixkit-classic-alarm-995.wav",
        "kind": "event",
        "volume": 0.28,
        "weight": 4.5,
        "keywords": [
            "alarm", "siren", "warning", "danger", "dangerous", "alert", "red alert",
            "emergency", "caution", "threat", "security", "breach", "police",
            "red flag", "hazard", "risk", "fatal", "deadly", "wake up",
            "khatra", "khatarnak", "chetavni", "savdhan", "jaanleva",
            "खतरा", "खतरनाक", "चेतावनी", "सावधान", "अलार्म", "पुलिस", "आपातकाल", "जानलेवा",
        ],
    },
    {
        "file": "mixkit-clock-countdown-bleeps-916.wav",
        "kind": "event",
        "volume": 0.32,
        "weight": 4.5,
        "keywords": [
            "countdown", "3 2 1", "seconds left", "minutes left", "deadline",
            "last chance", "limited time", "timer", "hurry", "running out of time",
            "race against time", "count down", "final seconds",
            "akhiri mauka", "jaldi", "time khatam", "kam samay", "ginti",
            "गिनती", "आखिरी मौका", "समय खत्म", "जल्दी", "डेडलाइन",
        ],
    },
    {
        "file": "mixkit-tick-tock-clock-timer-1045.wav",
        "kind": "ambient",
        "volume": 0.25,
        "weight": 3.5,
        "keywords": [
            "clock", "tick", "tock", "hour", "hours", "years", "decade", "decades",
            "century", "centuries", "wait", "waiting", "patience", "timeline",
            "aging", "eternity", "slowly", "every day", "time passed", "ghadi",
            "samay", "waqt", "saal", "sadi", "intezar",
            "घड़ी", "समय", "वक्त", "साल", "सदी", "इंतज़ार", "इंतजार",
        ],
    },
    {
        "file": "mixkit-female-astonished-gasp-964.wav",
        "kind": "event",
        "volume": 0.36,
        "weight": 4.0,
        "keywords": [
            "gasp", "shock", "shocking", "shocked", "unbelievable", "omg",
            "mind blowing", "stunned", "surprised", "surprise", "jaw dropping",
            "cant believe", "cannot believe", "impossible", "astonished", "twist",
            "hairan", "chaunk", "chaukane", "ashcharya", "gajab",
            "हैरान", "चौंक", "चौकाने", "आश्चर्य", "असंभव", "यकीन", "गजब",
        ],
    },
    {
        "file": "mixkit-glitch-roar-1033.wav",
        "kind": "event",
        "volume": 0.34,
        "weight": 4.5,
        "keywords": [
            "roar", "monster", "beast", "dragon", "dinosaur", "lion", "tiger",
            "demon", "devil", "ghost", "horror", "terrifying", "nightmare",
            "predator", "scary", "haunted", "creature", "rage", "angry", "evil",
            "dahad", "sher", "rakshas", "bhoot", "shaitan", "darawna", "bhayanak",
            "दहाड़", "शेर", "राक्षस", "भूत", "शैतान", "डरावना", "भयानक", "खूंखार",
        ],
    },
    {
        "file": "mixkit-dog-barking-twice-1.wav",
        "kind": "event",
        "volume": 0.38,
        "weight": 5.0,
        "keywords": [
            "dog", "puppy", "bark", "barking", "hound", "wolf", "canine", "pet",
            "kutta", "kutte", "pilla", "bhonk", "bhediya",
            "कुत्ता", "कुत्ते", "पिल्ला", "भौंक", "भेड़िया",
        ],
    },
    {
        "file": "mixkit-little-birds-singing-in-the-trees-17.wav",
        "kind": "ambient",
        "volume": 0.26,
        "weight": 4.0,
        "keywords": [
            "bird", "birds", "chirp", "morning", "sunrise", "dawn", "nature",
            "tree", "trees", "garden", "peace", "peaceful", "calm", "spring",
            "village", "paradise", "sunshine", "forest", "fresh air",
            "chidiya", "pakshi", "panchi", "subah", "prakriti", "ped", "bagicha", "shanti",
            "चिड़िया", "पक्षी", "पंछी", "सुबह", "प्रकृति", "पेड़", "बगीचा", "शांति", "गाँव",
        ],
    },
    {
        "file": "mixkit-light-rain-loop-2393.wav",
        "kind": "ambient",
        "volume": 0.25,
        "weight": 4.2,
        "keywords": [
            "rain", "raining", "rainy", "monsoon", "drizzle", "umbrella", "tears",
            "cry", "crying", "sad", "lonely", "loneliness", "heartbreak", "sorrow",
            "grief", "gloomy", "emotional", "depressed", "stormy", "wet",
            "barish", "baarish", "barsat", "aansu", "rona", "dukh", "udas", "akela",
            "बारिश", "बरसात", "आँसू", "आंसू", "रोना", "दुख", "उदास", "अकेला", "मौसम",
        ],
    },
    {
        "file": "mixkit-footsteps-on-tall-grass-532.wav",
        "kind": "ambient",
        "volume": 0.28,
        "weight": 4.0,
        "keywords": [
            "footstep", "footsteps", "walk", "walking", "grass", "jungle",
            "trail", "path", "journey", "hike", "sneak", "follow", "following",
            "chase", "escape", "woods", "explore", "stepped", "kadam", "chalna",
            "chalne", "rasta", "junglee", "safar", "yatra", "picha",
            "कदम", "चलना", "रास्ता", "जंगल", "सफर", "यात्रा", "पीछा", "घास",
        ],
    },
    {
        "file": "mixkit-keyboard-typing-1386.wav",
        "kind": "ambient",
        "volume": 0.26,
        "weight": 4.0,
        "keywords": [
            "typing", "keyboard", "code", "coding", "programming", "programmer",
            "developer", "software", "laptop", "computer", "internet", "online",
            "website", "search", "google", "email", "message", "chat", "algorithm",
            "database", "server", "terminal", "type", "office",
            "कंप्यूटर", "लैपटॉप", "टाइपिंग", "कोडिंग", "इंटरनेट", "वेबसाइट", "डेटा", "संदेश",
        ],
    },
    {
        "file": "mixkit-fast-rocket-whoosh-1714.wav",
        "kind": "event",
        "volume": 0.35,
        "weight": 4.5,
        "keywords": [
            "rocket", "space", "astronaut", "nasa", "isro", "moon", "mars",
            "planet", "galaxy", "universe", "orbit", "launch", "blast off", "jet",
            "supersonic", "airplane", "flight", "fly", "flying", "skyrocket", "soar",
            "antariksh", "chand", "mangal", "grah", "brahmand", "udaan",
            "रॉकेट", "अंतरिक्ष", "चाँद", "मंगल", "ग्रह", "ब्रह्मांड", "उड़ान", "आकाश",
        ],
    },
    {
        "file": "mixkit-arrow-whoosh-1491.wav",
        "kind": "event",
        "volume": 0.40,
        "weight": 4.2,
        "keywords": [
            "arrow", "bow", "archery", "target", "bullseye", "aim", "spear",
            "sword", "warrior", "battle", "war", "fight", "strike", "bullet",
            "precision", "sharp", "weapon", "hit", "teer", "dhanush", "lakshya",
            "nishana", "talwar", "yoddha", "yudh", "ladai", "vaar",
            "तीर", "धनुष", "लक्ष्य", "निशाना", "तलवार", "योद्धा", "युद्ध", "लड़ाई", "वार",
        ],
    },
    {
        "file": "mixkit-cinematic-laser-gun-thunder-1287.wav",
        "kind": "event",
        "volume": 0.32,
        "weight": 4.5,
        "keywords": [
            "thunder", "lightning", "laser", "explosion", "explode", "blast",
            "bomb", "gun", "shoot", "meteor", "asteroid", "destroy", "destruction",
            "nuclear", "beam", "storm", "boom", "collide", "collision", "impact",
            "dhamaka", "visfot", "toofan", "gadgadahat", "tabahi", "hamla",
            "धमाका", "विस्फोट", "तूफान", "तबाही", "गड़गड़ाहट", "हमला", "लेजर",
        ],
    },
    {
        "file": "mixkit-small-electric-glitch-2595.wav",
        "kind": "event",
        "volume": 0.38,
        "weight": 4.2,
        "keywords": [
            "electric", "electricity", "voltage", "spark", "circuit", "short circuit",
            "wire", "battery", "charge", "zap", "current", "neuron", "pulse",
            "energy", "power grid", "magnet", "bijli", "jhatka", "tar",
            "बिजली", "करंट", "झटका", "चिंगारी", "सर्किट", "ऊर्जा",
        ],
    },
    {
        "file": "mixkit-cinematic-glitch-trailer-1021.wav",
        "kind": "event",
        "volume": 0.38,
        "weight": 3.8,
        "keywords": [
            "glitch", "hack", "hacker", "matrix", "illusion", "fake", "corrupt",
            "virus", "bug", "simulation", "conspiracy", "shadow", "trap",
            "plot twist", "control", "brainwash", "dhoka", "jaal", "mayajaal", "bharam",
            "धोखा", "भ्रम", "माया", "साजिश", "वायरस", "हैक", "जाल",
        ],
    },
    {
        "file": "mixkit-glitch-static-1457.wav",
        "kind": "event",
        "volume": 0.34,
        "weight": 4.2,
        "keywords": [
            "static", "signal", "offline", "disconnected", "error", "crash",
            "freeze", "froze", "television", "tv", "cctv", "footage", "radio",
            "transmission", "broken", "interference", "distortion", "lost connection",
            "kharab", "band", "सिग्नल", "टीवी", "कैमरा", "फ़ुटेज", "त्रुटि", "खराब",
        ],
    },
    {
        "file": "mixkit-arcade-retro-game-over-213.wav",
        "kind": "event",
        "volume": 0.36,
        "weight": 4.2,
        "keywords": [
            "fail", "failed", "failure", "lose", "lost", "loser", "game over",
            "mistake", "wrong", "defeat", "bankrupt", "ruin", "ruined", "quit",
            "arcade", "retro", "video game", "regret", "loss", "collapse",
            "haar", "haara", "nakaam", "galti", "barbad", "nuksan", "khatam",
            "हार", "नाकाम", "गलती", "बर्बाद", "नुकसान", "खेल खत्म", "गेम",
        ],
    },
    {
        "file": "mixkit-cartoon-toy-whistle-616.wav",
        "kind": "event",
        "volume": 0.36,
        "weight": 4.2,
        "keywords": [
            "funny", "joke", "comedy", "laugh", "laughing", "prank", "silly",
            "toy", "whistle", "weird", "absurd", "meme", "oops", "clown",
            "hilarious", "kid", "cartoon", "mazak", "hasi", "masti", "khilona", "ajeeb",
            "मजाक", "हंसी", "खिलौना", "अजीब", "कॉमेडी",
        ],
    },
    {
        "file": "mixkit-epic-orchestra-transition-2290.wav",
        "kind": "intro",
        "volume": 0.32,
        "weight": 3.8,
        "keywords": [
            "epic", "orchestra", "king", "queen", "emperor", "empire", "kingdom",
            "victory", "win", "won", "champion", "hero", "legend", "glory",
            "triumph", "conquer", "billionaire", "success", "powerful", "crown",
            "miracle", "god", "divine", "raja", "maharaja", "samrat", "jeet",
            "vijay", "safalta", "baadshah", "mahan",
            "राजा", "महाराजा", "सम्राट", "साम्राज्य", "जीत", "विजय", "महान", "सफलता", "शक्तिशाली", "बादशाह",
        ],
    },
    {
        "file": "mixkit-air-zoom-vacuum-2608.wav",
        "kind": "transition",
        "volume": 0.38,
        "weight": 3.5,
        "keywords": [
            "zoom", "closer", "deep dive", "vacuum", "black hole", "gravity",
            "absorb", "disappear", "vanish", "suck", "focus", "detail", "micro",
            "inside", "center", "secret inside", "andar", "gahrai", "gayab", "dhyaan",
            "अंदर", "गहराई", "गायब", "ध्यान", "ब्लैक होल", "फोकस",
        ],
    },
    {
        "file": "mixkit-air-woosh-1489.wav",
        "kind": "transition",
        "volume": 0.35,
        "weight": 2.4,
        "keywords": [
            "wind", "breeze", "air", "breath", "breathe", "atmosphere", "sky",
            "float", "drift", "shift", "change", "meanwhile", "transform",
            "hawa", "saans", "badlav", "agla", "हवा", "सांस", "बदलाव", "आसमान",
        ],
    },
    {
        "file": "mixkit-cinematic-whoosh-fast-transition-1492.wav",
        "kind": "transition",
        "volume": 0.38,
        "weight": 2.2,
        "keywords": [
            "fast", "quick", "quickly", "rapid", "instant", "speed", "suddenly",
            "however", "but wait", "switch", "flash", "next", "reason", "fact",
            "tez", "tezi", "turant", "fatafat", "achanak", "lekin",
            "तेज", "तुरंत", "फटाफट", "अचानक", "लेकिन",
        ],
    },
    {
        "file": "mixkit-fast-small-sweep-transition-166.wav",
        "kind": "transition",
        "volume": 0.38,
        "weight": 2.0,
        "keywords": [
            "point", "tip", "hack", "trick", "step", "method", "first", "second",
            "third", "also", "look", "check", "number", "baat", "tarika", "dekho",
            "पहला", "दूसरा", "तीसरा", "तरीका", "देखो",
        ],
    },
]


def _resolve_ae_sfx_path(filename: str):
    """Resolve an SFX file path primarily from the sound_effects/ folder."""
    if not filename:
        return None
    for candidate in (
        os.path.join(_AE_SFX_DIR, filename),
        os.path.abspath(os.path.join("sound_effects", filename)),
        os.path.join(_AE_SFX_BASE_DIR, filename),
        os.path.abspath(filename),
    ):
        if os.path.exists(candidate) and os.path.getsize(candidate) > 500:
            return candidate
    return None


def _ae_tokenize(text: str) -> list:
    if not text:
        return []
    return [t for t in _AE_SFX_SPLIT_RE.split(str(text).lower()) if t]


def _ae_find_keyword_hit(tokens: list, joined_text: str, kw: str):
    """
    Match a keyword against normalized tokens safely without false substrings
    (e.g., prevents 'rain' from matching 'brain' or 'war' from matching 'warning').
    Supports English inflections and Hindi Devanagari prefixes cleanly.
    Returns (matched: bool, first_token_idx: int).
    """
    if not tokens or not kw:
        return False, -1

    kw_clean = kw.strip().lower()
    if " " in kw_clean:
        needle = f" {kw_clean} "
        pos = joined_text.find(needle)
        if pos != -1:
            word_idx = len(joined_text[:pos].strip().split()) if joined_text[:pos].strip() else 0
            return True, word_idx
        return False, -1

    is_ascii = kw_clean.isascii()
    valid_ascii = {kw_clean}
    if is_ascii:
        if len(kw_clean) >= 3:
            valid_ascii.add(kw_clean + "s")
        if len(kw_clean) >= 4:
            valid_ascii.update((kw_clean + "es", kw_clean + "ed", kw_clean + "ing", kw_clean + "ly"))

    for idx, tok in enumerate(tokens):
        if is_ascii:
            if tok in valid_ascii:
                return True, idx
        else:
            if tok == kw_clean or (len(kw_clean) >= 3 and tok.startswith(kw_clean)):
                return True, idx

    return False, -1


def select_after_effects_sfx(
    scene_text: str,
    scene_keyword: str = "",
    scene_idx: int = 0,
    total_scenes: int = 1,
    clip_duration: float = 5.0,
    used_sfx: list = None,
):
    """
    Selects the best matching Mixkit/local SFX for an Ultra After Effects scene
    using the SFX filename's intended role and multi-lingual script analysis.
    """
    used_sfx = used_sfx or []
    tokens = _ae_tokenize(scene_text)
    joined_text = f" {' '.join(tokens)} " if tokens else ""
    kw_tokens = _ae_tokenize(scene_keyword)
    joined_kw = f" {' '.join(kw_tokens)} " if kw_tokens else ""

    last_file = used_sfx[-1] if used_sfx else None
    used_set = set(used_sfx)

    best_entry = None
    best_score = -1.0
    best_hit_idx = 0
    best_matched_kw = ""

    # Scene 0 cues for tech/mystery cyber glitch intro vs grand cinematic intro
    tech_mystery_cues = {"ai", "tech", "technology", "cyber", "hack", "glitch", "secret", "mystery", "dark", "rahasya", "gupt", "रहस्य", "गुप्त", "सच"}
    tech_intro_bias = any(t in tech_mystery_cues for t in (tokens + kw_tokens))

    for entry in AFTER_EFFECTS_SFX_CATALOG:
        fname = entry["file"]
        resolved = _resolve_ae_sfx_path(fname)
        if not resolved:
            continue

        # Reserve intro SFX primarily for Scene 0 unless explicitly matched in script
        is_intro_file = fname in ("mixkit-intro-transition-1146.wav", "mixkit-intro-text-glitch-2950.wav")
        if is_intro_file and scene_idx > 0:
            explicit_intro_hits = 0
            for kw in entry["keywords"][:4]:
                m, _ = _ae_find_keyword_hit(tokens, joined_text, kw)
                if m:
                    explicit_intro_hits += 1
            if explicit_intro_hits == 0:
                continue

        score = 0.0
        first_idx = len(tokens)
        matched_kw = ""
        matched_kws = set()

        for kw in entry["keywords"]:
            hit, idx = _ae_find_keyword_hit(tokens, joined_text, kw)
            if hit:
                matched_kws.add(kw)
                score += entry["weight"]
                if idx < first_idx:
                    first_idx = idx
                    matched_kw = kw
            elif kw_tokens:
                kw_hit, _ = _ae_find_keyword_hit(kw_tokens, joined_kw, kw)
                if kw_hit and kw not in matched_kws:
                    matched_kws.add(kw)
                    score += entry["weight"] * 0.6
                    if not matched_kw:
                        matched_kw = f"[kw:{kw}]"

        # Scene 0 opening hook affinity (matching intro filenames directly)
        if scene_idx == 0:
            if fname == "mixkit-intro-text-glitch-2950.wav":
                score += 4.2 if tech_intro_bias else 2.0
                if not matched_kw:
                    matched_kw = "scene0_intro_glitch"
                    first_idx = 0
            elif fname == "mixkit-intro-transition-1146.wav":
                score += 2.2 if tech_intro_bias else 4.2
                if not matched_kw:
                    matched_kw = "scene0_intro"
                    first_idx = 0

        # Climax finishing boost for orchestral hit on final scene
        if scene_idx > 0 and total_scenes >= 3 and scene_idx == total_scenes - 1:
            if fname == "mixkit-epic-orchestra-transition-2290.wav":
                score += 2.0
                if not matched_kw:
                    matched_kw = "final_climax"
                    first_idx = 0

        if score <= 0.0:
            continue

        # Penalize back-to-back or repeated SFX to keep edits dynamic
        if fname == last_file:
            score -= 5.0
        elif fname in used_set:
            score -= 1.5

        if score > best_score:
            best_score = score
            best_entry = entry
            best_hit_idx = first_idx if first_idx < len(tokens) else 0
            best_matched_kw = matched_kw

    # Clean After Effects cut transitions when no specific SFX matched strongly
    if best_entry is None or best_score < 1.0:
        short_transitions = [
            "mixkit-cinematic-whoosh-fast-transition-1492.wav",
            "mixkit-fast-small-sweep-transition-166.wav",
            "mixkit-air-zoom-vacuum-2608.wav",
        ]
        if clip_duration >= 2.2:
            short_transitions.append("mixkit-air-woosh-1489.wav")

        if scene_idx == 0:
            preferred_order = [
                "mixkit-intro-text-glitch-2950.wav" if tech_intro_bias else "mixkit-intro-transition-1146.wav",
                "mixkit-intro-transition-1146.wav",
            ]
        else:
            rot = scene_idx % len(short_transitions)
            preferred_order = short_transitions[rot:] + short_transitions[:rot]

        chosen_fname = None
        for cand in preferred_order:
            if cand != last_file and _resolve_ae_sfx_path(cand):
                chosen_fname = cand
                break
        if not chosen_fname:
            for cand in preferred_order:
                if _resolve_ae_sfx_path(cand):
                    chosen_fname = cand
                    break

        if not chosen_fname:
            return None

        best_entry = next((e for e in AFTER_EFFECTS_SFX_CATALOG if e["file"] == chosen_fname), None)
        if not best_entry:
            return None
        best_hit_idx = 0
        best_matched_kw = "scene_transition"

    resolved_path = _resolve_ae_sfx_path(best_entry["file"])
    if not resolved_path:
        return None

    sfx_dur = get_audio_duration_fast(resolved_path, fallback=1.5)
    onset_sec = 0.0

    # Sync punctual event SFX to the spoken position inside the scene script
    if best_entry["kind"] == "event" and tokens and not str(best_matched_kw).startswith("[kw:") and clip_duration >= 2.2:
        word_ratio = best_hit_idx / max(1, len(tokens))
        if word_ratio > 0.22:
            usable_tail = min(max(sfx_dur, 0.8), 1.35)
            max_onset = max(0.0, clip_duration - usable_tail)
            onset_sec = min(max_onset, word_ratio * clip_duration * 0.82)

    return {
        "path": resolved_path,
        "file": best_entry["file"],
        "kind": best_entry["kind"],
        "volume": best_entry["volume"],
        "onset_sec": round(onset_sec, 3),
        "sfx_duration": sfx_dur,
        "reason": best_matched_kw or "context",
    }


def mix_sfx_into_scene_audio(voice_audio_path: str, sfx_info: dict, clip_duration: float, out_audio_path: str) -> str:
    """
    Mixes a selected SFX track cleanly into a scene's voice narration using FFmpeg
    without lowering the primary voiceover volume, safely falling back on any error.
    """
    if not sfx_info or not voice_audio_path or not os.path.exists(voice_audio_path):
        return voice_audio_path

    sfx_path = sfx_info.get("path")
    if not sfx_path or not os.path.exists(sfx_path):
        return voice_audio_path

    try:
        kind = sfx_info.get("kind", "event")
        vol = float(sfx_info.get("volume", 0.34))
        onset_sec = max(0.0, float(sfx_info.get("onset_sec", 0.0)))
        sfx_dur = float(sfx_info.get("sfx_duration") or get_audio_duration_fast(sfx_path, fallback=1.5))

        safe_clip_dur = max(0.5, float(clip_duration))
        play_window = max(0.25, safe_clip_dur - onset_sec)

        sfx_input_args = []
        if kind == "ambient" and sfx_dur > 0.2 and sfx_dur < play_window:
            sfx_input_args.extend(["-stream_loop", "-1"])
            trim_len = play_window
        else:
            trim_len = min(sfx_dur, play_window)

        trim_len = max(0.20, trim_len)
        fade_in = 0.22 if kind == "ambient" else 0.02
        fade_out = min(0.55 if kind in ("ambient", "intro") else 0.30, max(0.05, trim_len * 0.30))
        fade_out_start = max(0.0, trim_len - fade_out)

        sfx_chain = (
            f"[1:a]aresample=44100,aformat=channel_layouts=stereo,"
            f"atrim=0:{trim_len:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={fade_in:.3f},"
            f"afade=t=out:st={fade_out_start:.3f}:d={fade_out:.3f},"
            f"volume={vol:.2f}"
        )
        if onset_sec >= 0.05:
            delay_ms = int(round(onset_sec * 1000))
            sfx_chain += f",adelay={delay_ms}|{delay_ms}"
        sfx_chain += "[sfx]"

        filter_complex = (
            f"[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[voice];"
            f"{sfx_chain};"
            f"[voice][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
            f"alimiter=limit=0.96:level=disabled[aout]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", os.path.abspath(voice_audio_path),
            *sfx_input_args,
            "-i", os.path.abspath(sfx_path),
            "-filter_complex", filter_complex,
            "-map", "[aout]",
            "-c:a", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            os.path.abspath(out_audio_path),
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
        if res.returncode == 0 and os.path.exists(out_audio_path) and os.path.getsize(out_audio_path) > 1000:
            return out_audio_path

        if res.stderr:
            err_tail = res.stderr.decode(errors="ignore")[-250:]
            print(f"⚠️ [After Effects SFX Mix Warning]: {err_tail}")
    except Exception as e_sfx:
        print(f"⚠️ [After Effects SFX Mix Error]: {e_sfx}")

    return voice_audio_path

def merge_and_export(
    scene_list: list,
    output_name: str,
    font_path: str = "./fonts/Arial.ttf",
    color: str = "random",
    font_size: int = 220,
    target_size: tuple = (1920, 1080),
    bg_music: str = "cool.mp3",
    mode: str = "ultra",
    category: str = "Random",
    log_callback: callable = None
):
    """
    Merges scene clips, audio narration, subtitles, and background music into a final MP4 video.
    Supports Multi-Character Dialogue Scenes & Selective BG Removal.
    Category-based Subtitle Styling:
      - 'History / Mythology' or 'ancient' theme -> Torn Parchment Paper Subtitle Box.
      - 'Cartoon / Animated', 'Modern', 'Technology' or others -> Sleek Kinetic Clean White & Color Text Subtitles.
    """
    print(f"\n🎬 Rendering {len(scene_list)} scenes (Mode: {mode.upper()}, Category: {category}, Size: {target_size})...")
    
    temp_scene_files = []
    used_sfx_history = []
    job_dir = os.path.dirname(output_name) if os.path.dirname(output_name) else "."

    cat_lower = str(category).lower()
    is_cartoon_cat = any(k in cat_lower for k in ["cartoon", "anime", "animation", "character", "comic"])
    is_world_news_cat = any(k in cat_lower for k in ["world news", "geopolitics", "news"])

    if mode == "ultra" and (is_cartoon_cat or is_world_news_cat):
        if is_world_news_cat:
            print(f"\n🌍 [Ultra World News Engine] Triggering WebGL API Call for full video ({len(scene_list)} scenes)...")
        else:
            print(f"\n🎬 [Ultra Cartoon Single-API Engine] Triggering 1 SINGLE Gemini API Call for full video ({len(scene_list)} scenes)...")
            
        scene_durations = []
        start_frames = []
        end_frames = []
        audio_paths = []
        current_frame = 0
        total_audio_duration = 0.0
        prompt_lines = []

        for idx, sc in enumerate(scene_list):
            a_path = sc.get('audio')
            sc_dur = 5.0
            if a_path and os.path.exists(a_path) and os.path.getsize(a_path) > 1000:
                try:
                    ac = AudioFileClip(a_path)
                    sc_dur = ac.duration
                    ac.close()
                except Exception:
                    pass
            sc_dur = max(3.0, sc_dur)
            sc_frames = int(sc_dur * 15)
            start_frames.append(current_frame)
            current_frame += sc_frames
            end_frames.append(current_frame)
            scene_durations.append(sc_dur)
            total_audio_duration += sc_dur
            audio_paths.append(a_path)

            sc_text = sc.get('text', '')
            prompt_lines.append(f"Scene {idx+1} (Frames {start_frames[-1]} to {end_frames[-1]}, Duration {sc_dur:.1f}s): Dialogue & Action: '{sc_text}'")

        full_prompt_story = "\n".join(prompt_lines)
        full_anim_mp4 = os.path.join(job_dir, "gemini_full_ultra_video.mp4")
        anim_result = None

        if is_world_news_cat:
            try:
                from world_news_ultra_engine import generate_world_news_ultra_video
                print(f"🌍 [Ultra World News Engine] Requesting WebGL MP4 ({total_audio_duration:.1f}s total)...")
                anim_result = generate_world_news_ultra_video(
                    user_prompt=full_prompt_story,
                    output_mp4=full_anim_mp4,
                    duration=total_audio_duration,
                    target_size=target_size,
                    fps=60
                )
            except ImportError:
                print("⚠️ world_news_ultra_engine not found! Falling back.")
        elif generate_gemini_cartoon_animation:
            print(f"🤖 [Single Gemini API Call] Requesting 1 full 2D Cartoon Animation MP4 ({total_audio_duration:.1f}s total)...")
            anim_result = generate_gemini_cartoon_animation(
                user_prompt=full_prompt_story,
                output_mp4=full_anim_mp4,
                duration=total_audio_duration,
                target_size=target_size,
                fps=15
            )

        if not anim_result or not os.path.exists(anim_result) or os.path.getsize(anim_result) < 500:
            print(f"⚠️ Generating emergency fallback 2D canvas MP4 -> {full_anim_mp4}...")
            from gemini_animator import create_pro_cartoon_canvas_mp4
            anim_result = create_pro_cartoon_canvas_mp4(
                user_prompt=full_prompt_story,
                output_mp4=full_anim_mp4,
                duration=total_audio_duration,
                target_size=target_size,
                fps=15
            )

        full_vclip = VideoFileClip(anim_result)

        for i, scene in enumerate(scene_list):
            sc_dur = scene_durations[i]
            sc_start_t = sum(scene_durations[:i])
            sc_end_t = sc_start_t + sc_dur

            a_path = audio_paths[i]
            if not a_path or not os.path.exists(a_path) or os.path.getsize(a_path) < 1000:
                safe_audio_path = os.path.join(job_dir, f"safe_audio_{i}.mp3")
                try:
                    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(sc_dur), "-q:a", "9", "-acodec", "libmp3lame", safe_audio_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    a_path = safe_audio_path
                except Exception:
                    pass

            a_clip = AudioFileClip(a_path)
            actual_a_dur = a_clip.duration

            sub_vclip = full_vclip.subclip(min(sc_start_t, max(0, full_vclip.duration - 0.1)), min(sc_end_t, full_vclip.duration))
            sub_vclip = sub_vclip.set_duration(actual_a_dur).set_audio(a_clip)

            scene_combined = sub_vclip
            scene_output = os.path.join(job_dir, f"temp_rendered_scene_{i}.mp4")

            print(f"🎬 [FFMPEG RENDER] Stitching Ultra Cartoon Scene {i+1}/{len(scene_list)} (1-to-1 Sync Duration: {actual_a_dur:.1f}s)...")
            try:
                scene_combined.write_videofile(
                    scene_output,
                    codec="libx264",
                    audio_codec="aac",
                    fps=15,
                    preset="ultrafast",
                    threads=1,
                    ffmpeg_params=["-crf", "26", "-pix_fmt", "yuv420p"],
                    logger=None
                )
            except Exception as e_stitch:
                print(f"⚠️ Warning during Ultra scene {i+1} stitch: {e_stitch}. Retrying with single thread fallback...")
                scene_combined.write_videofile(
                    scene_output,
                    codec="libx264",
                    audio_codec="aac",
                    fps=15,
                    preset="ultrafast",
                    threads=1,
                    ffmpeg_params=["-crf", "28", "-pix_fmt", "yuv420p"],
                    logger=None
                )

            scene_combined.close()
            sub_vclip.close()
            a_clip.close()
            try:
                if 'txt_clip' in locals() and txt_clip:
                    txt_clip.close()
            except Exception:
                pass
            gc.collect()

            temp_scene_files.append(scene_output)

        full_vclip.close()

        valid_temp_files = [tf for tf in temp_scene_files if os.path.exists(tf) and os.path.getsize(tf) > 500]
        if not valid_temp_files:
            raise RuntimeError("No valid scene video files generated for assembly!")

        list_path = os.path.abspath(os.path.join(job_dir, "concat_list.txt"))
        with open(list_path, "w", encoding="utf-8") as f:
            for tf in valid_temp_files:
                f.write(f"file '{os.path.abspath(tf)}'\n")

        temp_merged = os.path.abspath(os.path.join(job_dir, "temp_merged_final.mp4"))
        try:
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", temp_merged], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e_c_copy:
            print(f"⚠️ Notice: FFmpeg concat copy mode failed ({e_c_copy}). Retrying with re-encode fallback...")
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c:v", "libx264", "-preset", "ultrafast", "-threads", "1", "-c:a", "aac", temp_merged], check=True)

        if bg_music and str(bg_music).lower() != "none":
            bg_music_file = bg_music if os.path.exists(bg_music) else (os.path.join(".", bg_music) if os.path.exists(os.path.join(".", bg_music)) else None)
            if bg_music_file and os.path.exists(bg_music_file):
                cmd = [
                    "ffmpeg", "-y",
                    "-i", temp_merged,
                    "-i", bg_music_file,
                    "-filter_complex", "[1:a]volume=0.12[a1];[0:a][a1]amix=inputs=2:duration=first[a]",
                    "-map", "0:v",
                    "-map", "[a]",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    output_name
                ]
                subprocess.run(cmd, check=True)
                if os.path.exists(temp_merged): os.remove(temp_merged)
            else:
                if os.path.exists(temp_merged): os.rename(temp_merged, output_name)
        else:
            if os.path.exists(temp_merged): os.rename(temp_merged, output_name)

        if os.path.exists(list_path): os.remove(list_path)
        for f in temp_scene_files:
            if os.path.exists(f): os.remove(f)

        return output_name

    for i, scene in enumerate(scene_list):
        release_system_memory()
        audio_path = scene['audio']
        
        if not audio_path or not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
            print(f"⚠️ Warning: Invalid or 0-byte audio file {audio_path}. Generating silent audio fallback...")
            safe_audio_path = os.path.join(job_dir, f"safe_audio_{i}.mp3")
            try:
                subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "5.0", "-q:a", "9", "-acodec", "libmp3lame", safe_audio_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                audio_path = safe_audio_path
            except Exception:
                pass

        clip_duration = get_audio_duration_fast(audio_path, fallback=5.0)
        
        cat_lower = str(category).lower()
        is_cartoon_cat = any(k in cat_lower for k in ["cartoon", "anime", "animation", "character", "comic"])
        is_after_effects_cat = any(k in cat_lower for k in ["after effect", "after iffect", "after effects", "vfx", "motion graphic"])

        if any(k in cat_lower for k in ["history", "mythology", "ancient", "historical", "purana", "epic", "warrior"]):
            cat_style = "history"
        elif is_cartoon_cat:
            cat_style = "cartoon"
        elif is_after_effects_cat:
            cat_style = "clean"
        elif any(k in cat_lower for k in ["random", "all"]):
            cat_style = random.choice(["history", "cartoon", "clean"])
        else:
            cat_style = "clean"

        clip_text_segment = scene.get('text', '')
        current_sfx_mixed_path = None
        if str(mode).strip().lower() == "ultra" and is_after_effects_cat:
            scene_kw = scene.get('keyword') or scene.get('keywords') or scene.get('visual_prompt') or ''
            sfx_choice = select_after_effects_sfx(
                scene_text=clip_text_segment,
                scene_keyword=scene_kw,
                scene_idx=i,
                total_scenes=len(scene_list),
                clip_duration=clip_duration,
                used_sfx=used_sfx_history,
            )
            if sfx_choice:
                sfx_out_wav = os.path.join(job_dir, f"temp_sfx_mixed_{i}.wav")
                mixed_res = mix_sfx_into_scene_audio(audio_path, sfx_choice, clip_duration, sfx_out_wav)
                if mixed_res != audio_path and os.path.exists(mixed_res):
                    audio_path = mixed_res
                    current_sfx_mixed_path = mixed_res
                    used_sfx_history.append(sfx_choice["file"])
                    print(f"🔊 [Ultra After Effects SFX] Scene {i+1}/{len(scene_list)}: Applied '{sfx_choice['file']}' (kind={sfx_choice['kind']}, onset={sfx_choice['onset_sec']}s, trigger={sfx_choice['reason']})")

        scene_output = os.path.join(job_dir, f"temp_rendered_scene_{i}.mp4")
        step_pct = int(((i + 1) / len(scene_list)) * 100)
        print(f"🎬 [FFMPEG HARDWARE RENDER {step_pct}%] Stitching Scene {i+1}/{len(scene_list)} (Duration: {clip_duration:.1f}s) -> {scene_output}...")

        rendered_successfully = False

        if mode == "ultra":
            if "characters" in scene:
                print(f"🎭 Scene {i+1}: Generating Multi-Character Dialogue Ultra Clip...")
                try:
                    v_clip = create_multi_character_ultra_clip(scene, clip_duration, size=target_size)
                    temp_ultra_base = os.path.join(job_dir, f"temp_ultra_base_{i}.mp4")
                    v_clip.write_videofile(temp_ultra_base, fps=15, preset="ultrafast", threads=1, logger=None)
                    try: v_clip.close()
                    except Exception: pass
                    release_system_memory()
                    rendered_successfully = render_scene_native_ffmpeg(
                        scene_output=scene_output,
                        video_path=temp_ultra_base,
                        audio_path=audio_path,
                        duration=clip_duration,
                        text=clip_text_segment,
                        target_size=target_size,
                        font_path=font_path,
                        font_size=font_size,
                        category_style=cat_style,
                        highlight_color=color,
                        job_dir=job_dir
                    )
                    if os.path.exists(temp_ultra_base):
                        try: os.remove(temp_ultra_base)
                        except Exception: pass
                except Exception as e_mc:
                    print(f"⚠️ Multi-char render notice: {e_mc}")
            elif is_cartoon_cat:
                print(f"🎨 Scene {i+1}: Ultra Cartoon Mode detected. Triggering Gemini AI Cartoon Animation Engine STRICTLY...")
                ai_mp4_path = os.path.join(job_dir, f"gemini_cartoon_scene_{i}.mp4")
                anim_result = None
                if generate_gemini_cartoon_animation:
                    anim_result = generate_gemini_cartoon_animation(
                        user_prompt=scene.get("text", "Cartoon animation scene"),
                        output_mp4=ai_mp4_path,
                        duration=clip_duration,
                        target_size=target_size,
                        fps=15
                    )
                if not anim_result or not os.path.exists(anim_result):
                    print(f"🎨 Scene {i+1}: Running Guaranteed Local 2D Cartoon Canvas Renderer...")
                    from gemini_animator import create_pro_cartoon_canvas_mp4
                    anim_result = create_pro_cartoon_canvas_mp4(
                        user_prompt=scene.get("text", "Cartoon animation scene"),
                        output_mp4=ai_mp4_path,
                        duration=clip_duration,
                        target_size=target_size,
                        fps=15
                    )
                rendered_successfully = render_scene_native_ffmpeg(
                    scene_output=scene_output,
                    video_path=anim_result,
                    audio_path=audio_path,
                    duration=clip_duration,
                    text=clip_text_segment,
                    target_size=target_size,
                    font_path=font_path,
                    font_size=font_size,
                    category_style=cat_style,
                    highlight_color=color,
                    job_dir=job_dir
                )
            else:
                video_paths = scene['video'] if isinstance(scene['video'], list) else [scene['video']]
                valid_paths = [p for p in video_paths if p and os.path.exists(p) and os.path.getsize(p) > 1000]
                show_cutout = (i % 2 == 0) and (i < 6)
                if valid_paths:
                    bg_path = valid_paths[0]
                    fg_path = valid_paths[1] if (show_cutout and len(valid_paths) > 1) else None
                else:
                    bg_path = video_paths[0] if video_paths else None
                    fg_path = None
                if is_after_effects_cat:
                    filters = ["none"]
                    motions = ["diagonal_fast", "spiral_zoom", "zoom_in", "pan_right", "zoom_out"]
                else:
                    filters = [
                        "warm_epic", "cyber_teal_orange", "vintage_parchment", 
                        "royal_gold", "dramatic_cinematic", "dark_gothic", 
                        "neon_cyberpunk", "golden_sunburst", "emerald_fantasy", 
                        "crimson_warrior", "vintage_sepia_film", "ice_blue_cyber"
                    ]
                    motions = ["zoom_in", "zoom_out", "pan_right", "pan_left", "diagonal_fast", "spiral_zoom"]
                is_bg_video = bg_path and str(bg_path).lower().endswith(('.mp4', '.mov', '.avi', '.webm', '.mkv')) and has_video_stream(bg_path)
                # Case 1: After Effects Dual Photo/Asset Rapid Contrast Cut (e.g. 2 contrasting photos like Modi dictator vs real hero)
                if is_after_effects_cat and len(valid_paths) >= 2 and all(not str(p).lower().endswith(('.mp4', '.mov', '.avi', '.webm', '.mkv')) for p in valid_paths[:2]):
                    print(f"🎬 Scene {i+1}: Ultra After Effects Mode - Rapid Dual Photo Contrast Cut ({valid_paths[0]} & {valid_paths[1]})...")
                    try:
                        rendered_successfully = render_scene_native_ffmpeg(
                            scene_output=scene_output,
                            video_path=valid_paths[:2],
                            audio_path=audio_path,
                            duration=clip_duration,
                            text=clip_text_segment,
                            target_size=target_size,
                            font_path=font_path,
                            font_size=font_size,
                            category_style=cat_style,
                            highlight_color=color,
                            job_dir=job_dir
                        )
                    except Exception as e_ae_dual:
                        print(f"⚠️ Ultra After Effects dual cut notice: {e_ae_dual}")
                        rendered_successfully = False

                elif is_after_effects_cat and is_bg_video:
                    print(f"🎬 Scene {i+1}: Ultra After Effects Mode - Rendering Real Motion Graphics Video via Native FFmpeg (Trimmed to {clip_duration:.1f}s)...")
                    try:
                        rendered_successfully = render_scene_native_ffmpeg(
                            scene_output=scene_output,
                            video_path=bg_path,
                            audio_path=audio_path,
                            duration=clip_duration,
                            text=clip_text_segment,
                            target_size=target_size,
                            font_path=font_path,
                            font_size=font_size,
                            category_style=cat_style,
                            highlight_color=color,
                            job_dir=job_dir
                        )
                    except Exception as e_ae_render:
                        print(f"⚠️ Ultra After Effects real video render notice: {e_ae_render}")
                        rendered_successfully = False

                if not rendered_successfully:
                    filter_choice = random.choice(filters)
                    side_pos = "left" if i % 2 == 0 else "right"
                    motion_choice = random.choice(motions)
                    filter_str = "None (Original Raw Colors)" if filter_choice == "none" else filter_choice
                    print(f"✨ Scene {i+1}: Generating Ultra Motion Clip (Filter: {filter_str}, Motion: {motion_choice.upper()}, Cutout: {show_cutout}, Side: {side_pos.upper()})...")
                    try:
                        v_clip = create_ultra_photo_motion_clip(bg_path, fg_photo_path=fg_path, duration=clip_duration, size=target_size, filter_style=filter_choice, cutout_pos=side_pos, motion_type=motion_choice)
                        temp_ultra_base = os.path.join(job_dir, f"temp_ultra_base_{i}.mp4")
                        v_clip.write_videofile(temp_ultra_base, fps=15, preset="ultrafast", threads=1, logger=None)
                        try: v_clip.close()
                        except Exception: pass
                        release_system_memory()
                        rendered_successfully = render_scene_native_ffmpeg(
                            scene_output=scene_output,
                            video_path=temp_ultra_base,
                            audio_path=audio_path,
                            duration=clip_duration,
                            text=clip_text_segment,
                            target_size=target_size,
                            font_path=font_path,
                            font_size=font_size,
                            category_style=cat_style,
                            highlight_color=color,
                            job_dir=job_dir
                        )
                        if os.path.exists(temp_ultra_base):
                            try: os.remove(temp_ultra_base)
                            except Exception: pass
                    except Exception as e_um:
                        print(f"⚠️ Ultra motion render notice: {e_um}")
        else:
            video_path = scene['video'][0] if isinstance(scene['video'], list) else scene['video']
            rendered_successfully = render_scene_native_ffmpeg(
                scene_output=scene_output,
                video_path=video_path,
                audio_path=audio_path,
                duration=clip_duration,
                text=clip_text_segment,
                target_size=target_size,
                font_path=font_path,
                font_size=font_size,
                category_style=cat_style,
                highlight_color=color,
                job_dir=job_dir
            )

        if not rendered_successfully or not os.path.exists(scene_output) or os.path.getsize(scene_output) < 1000:
            print(f"⚠️ Native FFmpeg fallback to Zero-RAM Stream Stitch for Scene {i+1}...")
            video_path = scene['video'][0] if isinstance(scene['video'], list) else scene['video']
            inp_v = os.path.abspath(video_path) if (video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 500) else None
            
            fb_args = []
            if inp_v:
                if str(inp_v).lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    fb_args.extend(["-loop", "1", "-i", inp_v])
                else:
                    fb_args.extend(["-stream_loop", "-1", "-fflags", "+genpts", "-i", inp_v])
            else:
                fb_args.extend(["-f", "lavfi", "-i", f"color=c=0x0f0a23:s={target_size[0]}x{target_size[1]}:r=25"])
                
            fb_args.extend(["-i", os.path.abspath(audio_path)])
            fb_filter = f"[0:v]scale={target_size[0]}:{target_size[1]}:force_original_aspect_ratio=increase,crop={target_size[0]}:{target_size[1]},setsar=1[outv]"
            
            fb_cmd = [
                "ffmpeg", "-y",
                *fb_args,
                "-filter_complex", fb_filter,
                "-map", "[outv]",
                "-map", "1:a",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "26",
                "-threads", "1",
                "-max_muxing_queue_size", "1024",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "128k",
                "-ar", "44100",
                "-ac", "2",
                "-t", f"{clip_duration:.2f}",
                os.path.abspath(scene_output)
            ]
            try:
                subprocess.run(fb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            except Exception as e_fb:
                print(f"⚠️ Emergency fallback error: {e_fb}")

        if not os.path.exists(scene_output) or os.path.getsize(scene_output) < 1000:
            print(f"⚠️ Video stream corrupted or stalled. Using Instant Solid Canvas for Scene {i+1}...")
            ultra_safe_cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"color=c=0x0f0a23:s={target_size[0]}x{target_size[1]}:r=25",
                "-i", os.path.abspath(audio_path),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
                "-threads", "1",
                "-c:a", "aac", "-b:a", "96k",
                "-t", f"{clip_duration:.2f}",
                os.path.abspath(scene_output)
            ]
            try:
                subprocess.run(ultra_safe_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
            except Exception as e_us:
                print(f"⚠️ Ultra safe canvas fallback notice: {e_us}")

        release_system_memory()
        
        if current_sfx_mixed_path and os.path.exists(current_sfx_mixed_path):
            try: os.remove(current_sfx_mixed_path)
            except Exception: pass

        temp_scene_files.append(scene_output)
        msg = f"✅ [Scene {i+1}/{len(scene_list)}] Encoded HD scene clip successfully!"
        print(f"   {msg}")
        if log_callback:
            pct = 75 + int(((i + 1) / len(scene_list)) * 20)
            log_callback(msg, pct)

    print(f"\n🔗 [FFMPEG CONCAT] Merging all {len(temp_scene_files)} scenes + Background Music track...")
    valid_temp_files = [tf for tf in temp_scene_files if os.path.exists(tf) and os.path.getsize(tf) > 500]
    if not valid_temp_files:
        raise RuntimeError("No valid scene video files generated for assembly!")

    list_path = os.path.abspath(os.path.join(job_dir, "concat_list.txt"))
    with open(list_path, "w", encoding="utf-8") as f:
        for tf in valid_temp_files:
            f.write(f"file '{os.path.abspath(tf)}'\n")
            
    temp_merged = os.path.abspath(os.path.join(job_dir, "temp_merged_final.mp4"))
    try:
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24", "-r", "25",
            "-threads", "1",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
            temp_merged
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e_c_re:
        print(f"⚠️ Concat re-encode notice: {e_c_re}. Falling back to copy...")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", temp_merged], check=True)

    bg_music_file = None
    if bg_music and str(bg_music).lower() != "none":
        if os.path.exists(bg_music):
            bg_music_file = bg_music
        elif os.path.exists(os.path.join(".", bg_music)):
            bg_music_file = os.path.join(".", bg_music)
        else:
            search_dirs = [".", "./songs", "./songs copy"]
            possible = []
            for d in search_dirs:
                if os.path.exists(d):
                    found = [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith(('.mp3', '.wav'))]
                    possible.extend(found)
            
            if possible:
                bg_music_file = possible[0]

    if bg_music_file and os.path.exists(bg_music_file):
        print(f"🎬 Adding background music with exact sync & smooth fade: {bg_music_file}...")
        video_dur = get_audio_duration_fast(temp_merged, fallback=0.0)
        fade_start = max(0.0, video_dur - 2.5) if video_dur > 2.5 else 0.0
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_merged,
            "-i", bg_music_file,
            "-filter_complex", f"[1:a]volume=0.10,afade=t=out:st={fade_start:.2f}:d=2.5[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            "-t", f"{video_dur:.2f}",
            "-shortest",
            output_name
        ]
        subprocess.run(cmd, check=True)
        if os.path.exists(temp_merged): os.remove(temp_merged)
    else:
        print("🎬 Exporting final video...")
        if os.path.exists(temp_merged): os.rename(temp_merged, output_name)
    
    if os.path.exists(list_path): os.remove(list_path)
    for f in temp_scene_files: 
        if os.path.exists(f): os.remove(f)
    
    return output_name
