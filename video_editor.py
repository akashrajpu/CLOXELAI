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

try:
    from bg_remover import remove_background
except ImportError:
    remove_background = None

try:
    from web_image_fetcher import fetch_web_image
except ImportError:
    fetch_web_image = None


COLOR_PALETTES = [
    "#FFEE00", # Vivid Yellow
    "#00FFFF", # Neon Cyan
    "#FF0055", # Hot Pink
    "#00FF66", # Electric Green
    "#FF9900", # Deep Amber
    "#FFFFFF"  # Pure White
]

POSITIONS = ["center", "bottom", "top"]


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
        devanagari_font_candidates = [
            "./fonts/NotoSansDevanagari-Bold.ttf",
            "./fonts/NotoSansDevanagari-Regular.ttf",
            "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc",
            "/System/Library/Fonts/Supplemental/DevanagariMT.ttc",
            "/System/Library/Fonts/Supplemental/Devanagari Sangam MN.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
        ]
        
        if has_devanagari:
            for df_path in devanagari_font_candidates:
                if os.path.exists(df_path):
                    try:
                        return ImageFont.truetype(df_path, fs)
                    except Exception:
                        pass
                        
        try:
            return ImageFont.truetype(font_path, fs)
        except Exception:
            pass

        fallback_candidates = devanagari_font_candidates + [
            "arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf"
        ]
        for font_candidate in fallback_candidates:
            if os.path.exists(font_candidate):
                try:
                    return ImageFont.truetype(font_candidate, fs)
                except Exception:
                    pass
                    
        return ImageFont.load_default()

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
    char_list = scene_info.get("characters", []) # List of dicts: [{"name": "Karna", "image": "...", "pos": "left"}]
    
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
            else: # center
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

def create_history_spotlight_overlay(base_img: Image.Image, progress: float) -> Image.Image:
    """
    Creates the dynamic moving dark mask spotlight reveal animation for History Mode (matching user screenshots 1, 2, 3):
      - Outer region: Darkened monochromatic / vignette overlay (0.28x brightness + desaturated).
      - Inner spotlight window: Moves dynamically across the frame revealing warm colored image with glowing organic reveal border.
    """
    w, h = base_img.size
    
    dark_bg = base_img.copy().convert("L").convert("RGB")
    dark_bg = ImageEnhance.Brightness(dark_bg).enhance(0.28)
    
    spotlight_mask = Image.new("L", (w, h), 0)
    # Fast High-Speed Downscaled Spotlight Mask Calculation (16x Faster Rendering!)
    mw, mh = w // 4, h // 4
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
    box_w = int(w * 0.78)
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
    
    font_candidates = [
        "./fonts/BetsyFlanagan.ttf",
        "./fonts/RaceFlow.ttf",
        "./fonts/CarbonBlock.ttf",
        "./fonts/bebas.ttf",
        "./fonts/anton.ttf"
    ]
    chosen_font = None
    for fc in font_candidates:
        if os.path.exists(fc):
            try:
                chosen_font = ImageFont.truetype(fc, int(font_size * 0.38))
                break
            except Exception:
                pass
    if not chosen_font:
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
    y_pos = int(box_h * 0.16)
    line_h = int(chosen_font.size * 1.20)
    
    for line in lines:
        tb = draw_p.textbbox((0, 0), line, font=chosen_font)
        lw = tb[2] - tb[0]
        x_pos = (box_w - lw) // 2
        draw_p.text((x_pos + 2, y_pos + 2), line, font=chosen_font, fill=(70, 15, 0, 180))
        draw_p.text((x_pos, y_pos), line, font=chosen_font, fill=text_color)
        y_pos += line_h

    return parchment

def create_ultra_photo_motion_clip(
    photo_path: str,
    fg_photo_path: str = None,
    duration: float = 5.0,
    size: tuple = (1920, 1080),
    filter_style: str = "warm_epic",
    cutout_pos: str = "left",
    motion_type: str = "zoom_in",
    fps: int = 15
) -> VideoClip:
    """Creates an Ultra Photo Motion Video Clip with Ink Brush Mask Edges, Smoke Haze, Particles, & Dynamic Zoom/Pan."""
    w, h = size
    print(f"🎨 [Ultra Engine] Generating 3D Ultra Clip (BG: {photo_path}, FG: {fg_photo_path}, Filter: {filter_style}, Motion: {motion_type.upper()})...")
    
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

    if orig_pil is None:
        bg_pil = create_parchment_background(size, color_theme="warm")
        def get_fallback_frame(t):
            return np.array(bg_pil.convert("RGB"))
        return VideoClip(get_fallback_frame, duration=duration).set_fps(fps)

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
        else: # spiral_zoom
            pan_x_factor = 0.5 + 0.20 * math.sin(progress * math.pi * 2)
            pan_y_factor = 0.5 + 0.20 * math.cos(progress * math.pi * 2)
            
        crop_x = int((bg_w_scaled - w) * pan_x_factor)
        crop_y = int((bg_h_scaled - h) * pan_y_factor)
        crop_x = max(0, min(bg_w_scaled - w, crop_x))
        crop_y = max(0, min(bg_h_scaled - h, crop_y))
        
        frame_canvas = bg_base_scaled.crop((crop_x, crop_y, crop_x + w, crop_y + h)).convert("RGBA")
        
        if filter_style in ["warm_epic", "vintage_parchment", "history", "dramatic_cinematic"]:
            frame_canvas = create_history_spotlight_overlay(frame_canvas, progress)
        
        if has_cutout and fg_resized:
            cur_fg_w = fg_resized.width
            cur_fg_h = fg_resized.height
            entrance_factor = min(1.0, progress * 4.0)
            slide_offset = int((1.0 - math.pow(entrance_factor, 2)) * w * 0.25)
            
            if cutout_pos == "right":
                fg_x = (w - cur_fg_w) + slide_offset
            else: # left
                fg_x = 0 - slide_offset
                
            fg_y = h - cur_fg_h
            frame_canvas.paste(fg_resized, (fg_x, fg_y), mask=fg_resized)
            
        return np.array(frame_canvas.convert("RGB"))

    return VideoClip(get_frame, duration=duration).set_fps(fps)

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
    job_dir = os.path.dirname(output_name) if os.path.dirname(output_name) else "."

    cat_lower = str(category).lower()
    is_cartoon_cat = any(k in cat_lower for k in ["cartoon", "anime", "animation", "character", "comic"])

    if mode == "ultra" and is_cartoon_cat:
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
        full_anim_mp4 = os.path.join(job_dir, "gemini_full_cartoon_video.mp4")
        anim_result = None

        if generate_gemini_cartoon_animation:
            print(f"🤖 [Single Gemini API Call] Requesting 1 full 2D Cartoon Animation MP4 ({total_audio_duration:.1f}s total)...")
            anim_result = generate_gemini_cartoon_animation(
                user_prompt=full_prompt_story,
                output_mp4=full_anim_mp4,
                duration=total_audio_duration,
                target_size=target_size,
                fps=15
            )

        if not anim_result or not os.path.exists(anim_result) or os.path.getsize(anim_result) < 500:
            print(f"⚠️ Generating emergency FFmpeg cartoon canvas MP4 -> {full_anim_mp4}...")
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"color=c=0x19192d:s={target_size[0]}x{target_size[1]}:r=15",
                "-t", str(total_audio_duration), "-c:v", "libx264", "-pix_fmt", "yuv420p", full_anim_mp4
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            anim_result = full_anim_mp4

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

            # Clean Ultra Cartoon animation without font/text overlay
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
                    threads=2,
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

        list_path = os.path.join(job_dir, "concat_list.txt")
        with open(list_path, "w") as f:
            for tf in temp_scene_files:
                f.write(f"file '{os.path.abspath(tf)}'\n")

        temp_merged = os.path.join(job_dir, "temp_merged_final.mp4")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", temp_merged], check=True)

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
        audio_path = scene['audio']
        
        if not audio_path or not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
            print(f"⚠️ Warning: Invalid or 0-byte audio file {audio_path}. Generating silent audio fallback...")
            safe_audio_path = os.path.join(job_dir, f"safe_audio_{i}.mp3")
            try:
                subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "5.0", "-q:a", "9", "-acodec", "libmp3lame", safe_audio_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                audio_path = safe_audio_path
            except Exception:
                pass

        a_clip = AudioFileClip(audio_path)
        clip_duration = a_clip.duration
        
        cat_lower = str(category).lower()
        is_cartoon_cat = any(k in cat_lower for k in ["cartoon", "anime", "animation", "character", "comic"])

        if mode == "ultra":
            if "characters" in scene:
                print(f"🎭 Scene {i+1}: Generating Multi-Character Dialogue Ultra Clip...")
                v_clip = create_multi_character_ultra_clip(scene, clip_duration, size=target_size)
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
                if not anim_result or not os.path.exists(anim_result) or os.path.getsize(anim_result) < 500:
                    cmd = [
                        "ffmpeg", "-y", "-f", "lavfi",
                        "-i", f"color=c=0x19192d:s={target_size[0]}x{target_size[1]}:r=15",
                        "-t", str(clip_duration), "-c:v", "libx264", "-pix_fmt", "yuv420p", ai_mp4_path
                    ]
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    anim_result = ai_mp4_path

                v_clip = VideoFileClip(anim_result)
            else:
                video_paths = scene['video'] if isinstance(scene['video'], list) else [scene['video']]
                bg_path = video_paths[0]
                
                show_cutout = (i % 2 == 0) and (i < 6)
                fg_path = video_paths[1] if (show_cutout and len(video_paths) > 1) else None
                
                filters = [
                    "warm_epic", "cyber_teal_orange", "vintage_parchment", 
                    "royal_gold", "dramatic_cinematic", "dark_gothic", 
                    "neon_cyberpunk", "golden_sunburst", "emerald_fantasy", 
                    "crimson_warrior", "vintage_sepia_film", "ice_blue_cyber"
                ]
                filter_choice = random.choice(filters)
                side_pos = "left" if i % 2 == 0 else "right"
                motions = ["zoom_in", "zoom_out", "pan_right", "pan_left", "diagonal_fast", "spiral_zoom"]
                motion_choice = random.choice(motions)
                print(f"✨ Scene {i+1}: Generating Ultra Motion Clip (Filter: {filter_choice}, Motion: {motion_choice.upper()}, Cutout: {show_cutout}, Side: {side_pos.upper()})...")
                v_clip = create_ultra_photo_motion_clip(bg_path, fg_photo_path=fg_path, duration=clip_duration, size=target_size, filter_style=filter_choice, cutout_pos=side_pos, motion_type=motion_choice)
        else:
            video_path = scene['video'][0] if isinstance(scene['video'], list) else scene['video']
            is_image = str(video_path).lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
            
            if is_image and os.path.exists(video_path):
                v_clip = ImageClip(video_path).resize(height=target_size[1])
            elif os.path.exists(video_path):
                v_clip = VideoFileClip(video_path, audio=False).resize(height=target_size[1])
            else:
                v_clip = ColorClip(size=target_size, color=(15, 10, 35))

            if v_clip.w > target_size[0]:
                v_clip = v_clip.crop(x_center=v_clip.w/2, width=target_size[0])
            elif v_clip.w < target_size[0]:
                v_clip = v_clip.resize(width=target_size[0])
                v_clip = v_clip.crop(y_center=v_clip.h/2, height=target_size[1])

        v_clip = v_clip.set_duration(clip_duration)
        v_clip = v_clip.set_audio(a_clip)

        cat_lower = str(category).lower()
        if any(k in cat_lower for k in ["history", "mythology", "ancient", "historical", "purana", "epic", "warrior"]):
            cat_style = "history"
        elif any(k in cat_lower for k in ["cartoon", "anime", "animation", "character", "comic"]):
            cat_style = "cartoon"
        elif any(k in cat_lower for k in ["random", "all"]):
            cat_style = random.choice(["history", "cartoon", "clean"])
        else:
            cat_style = "clean"

        clip_text_segment = scene['text']
        txt_clip = create_dynamic_animated_text(
            full_text=clip_text_segment,
            size=target_size,
            duration=clip_duration,
            font_path=font_path,
            font_size=font_size,
            text_position="random",
            text_color="random",
            is_ultra_mode=(mode == "ultra"),
            category_style=cat_style
        )
        
        if mode == "ultra" and is_cartoon_cat:
            scene_combined = v_clip
        else:
            scene_combined = CompositeVideoClip([v_clip, txt_clip.set_position('center')])
        
        scene_output = os.path.join(job_dir, f"temp_rendered_scene_{i}.mp4")
        step_pct = int(((i + 1) / len(scene_list)) * 100)
        print(f"🎬 [FFMPEG RENDER {step_pct}%] Stitching Scene {i+1}/{len(scene_list)} (Duration: {clip_duration:.1f}s) -> {scene_output}...")
        try:
            scene_combined.write_videofile(
                scene_output, 
                codec="libx264", 
                audio_codec="aac", 
                fps=15, 
                preset="ultrafast", 
                threads=2, 
                ffmpeg_params=["-crf", "28", "-pix_fmt", "yuv420p"],
                logger=None
            )
        except Exception as e_sc_stitch:
            print(f"⚠️ Notice during scene {i+1} write: {e_sc_stitch}. Retrying with single thread...")
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
        
        try: scene_combined.close()
        except Exception: pass
        try: v_clip.close()
        except Exception: pass
        try: a_clip.close()
        except Exception: pass
        try:
            if 'txt_clip' in locals() and txt_clip:
                txt_clip.close()
        except Exception: pass
        gc.collect()
        
        temp_scene_files.append(scene_output)
        msg = f"✅ [Scene {i+1}/{len(scene_list)}] Encoded HD scene clip successfully!"
        print(f"   {msg}")
        if log_callback:
            pct = 75 + int(((i + 1) / len(scene_list)) * 20)
            log_callback(msg, pct)

    print(f"\n🔗 [FFMPEG CONCAT] Merging all {len(temp_scene_files)} scenes + Background Music track...")
    list_path = os.path.join(job_dir, "concat_list.txt")
    with open(list_path, "w") as f:
        for tf in temp_scene_files:
            f.write(f"file '{os.path.abspath(tf)}'\n")
            
    temp_merged = os.path.join(job_dir, "temp_merged_final.mp4")
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
        print(f"🎬 Adding background music: {bg_music_file}...")
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
        print("🎬 Exporting final video...")
        if os.path.exists(temp_merged): os.rename(temp_merged, output_name)
    
    if os.path.exists(list_path): os.remove(list_path)
    for f in temp_scene_files: 
        if os.path.exists(f): os.remove(f)
    
    return output_name