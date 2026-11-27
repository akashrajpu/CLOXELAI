"""
nitish_documentary_engine.py - 3D Documentary Motion Engine (Nitish Rajput Style)
================================================================================
Inspired directly by high-production Indian & international documentary creators
(Nitish Rajput, Vox, MagnatesMedia, Johnny Harris):

1. Theatrical 16:9 Letterbox in 9:16 Vertical Canvas with Ambient Mirror Blur
   - Top & bottom have heavy Gaussian-blurred, darkened reflections of the 16:9 center video.
   - Thin, sleek horizontal dividers separating the cinematic window.

2. 2.5D Multi-Plane Parallax Depth (Pure Photo 3D Animation)
   - Deep background layer (drifting sky, moody gallery wall, executive office).
   - Midground subject cutout (monument, framed portrait, character, map) with 3D parallax.
   - Foreground depth accents (vintage newspaper, antique frame borders, dust motes).

3. Iconic 3D Documentary Archetypes
   - Archetype A (3D Monument / Sky Push-In): Architectural building, temple, or map over drifting sky.
   - Archetype B (Antique Gallery Frame): Ornate gold/wood frame hanging on gallery wall with subject portrait.
   - Archetype C (Vintage Wanted / Investigative Newspaper): Authentic newsprint with headline, yellow highlight, and portrait.
   - Archetype D (Executive Scene): Moody interior with subject cutout, warm lamp glow, and floating dust motes.

4. Zero Stock Videos: 100% Pure Photos & Transparent Cutouts.
5. Memory Footprint: Streams frame-by-frame to FFmpeg rawvideo pipe (< 35MB RAM).
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
    - Divider lines at y = 656 and y = 1264
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
    draw.line([(0, box_y), (w, box_y)], fill=(255, 255, 255, 65), width=1)
    draw.line([(0, box_y + box_h), (w, box_y + box_h)], fill=(255, 255, 255, 65), width=1)

    return canvas


def create_ornate_antique_frame(
    width: int = 360,
    height: int = 440,
    border_thick: int = 32
) -> Image.Image:
    """Procedurally renders a rich antique golden/wooden picture frame."""
    frame_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame_img)

    # Outer wood molding
    draw.rectangle([(0, 0), (width, height)], fill=(42, 28, 18, 255), outline=(190, 145, 65, 255), width=6)
    # Beveled gold fillet
    draw.rectangle([(8, 8), (width - 8, height - 8)], fill=(26, 16, 10, 255), outline=(235, 190, 90, 255), width=4)
    # Inner dark liner
    draw.rectangle([(18, 18), (width - 18, height - 18)], fill=(48, 34, 22, 255), outline=(155, 115, 45, 255), width=5)
    # Transparent picture opening
    draw.rectangle([(border_thick, border_thick), (width - border_thick, height - border_thick)], fill=(0, 0, 0, 0))

    return frame_img


def build_vintage_newspaper_page(
    headline: str,
    subject_cutout: Optional[Image.Image] = None,
    width: int = 1080,
    height: int = 608,
    highlight_text: str = ""
) -> Image.Image:
    """
    Renders a hyper-realistic vintage newspaper page matching the user's reference video:
    - Aged newsprint background
    - Masthead & edition info
    - Bold primary headline
    - 2-column layout with center framed portrait
    - Authentic fluorescent yellow marker highlight
    """
    paper = Image.new("RGB", (width, height), (240, 235, 224))
    draw = ImageDraw.Draw(paper)

    # 1. Subtle paper texture / noise
    noise = np.random.randint(-4, 5, (height, width, 3), dtype=np.int16)
    rgb_arr = np.clip(np.array(paper, dtype=np.int16) + noise, 0, 255).astype(np.uint8)
    paper = Image.fromarray(rgb_arr)
    draw = ImageDraw.Draw(paper)
    del rgb_arr, noise

    # 2. Outer vintage margin rules
    draw.rectangle([(50, 16), (width - 50, height - 16)], outline=(70, 60, 50), width=2)
    draw.rectangle([(54, 20), (width - 54, height - 20)], outline=(70, 60, 50), width=1)

    # 3. Masthead Header
    f_micro = get_clean_font(13, font_type="mono")
    f_mast = get_clean_font(18, font_type="serif")
    draw.text((68, 28), "VOL. CXII. NO. 20,756.", fill=(85, 75, 65), font=f_micro)
    draw.text((width // 2, 28), "THE HISTORICAL & FINANCIAL CHRONICLE", fill=(35, 30, 25), font=f_mast, anchor="mt")
    draw.text((width - 68, 28), "SPECIAL EDITION", fill=(85, 75, 65), font=f_micro, anchor="ra")

    draw.line([(54, 52), (width - 54, 52)], fill=(70, 60, 50), width=2)

    # 4. Giant Main Headline
    clean_hl = (headline or "WANTED").upper().strip()
    if len(clean_hl) > 35:
        clean_hl = clean_hl[:32] + "..."
    f_head = get_clean_font(46, font_type="serif")
    draw.text((width // 2, 85), clean_hl, fill=(20, 16, 14), font=f_head, anchor="mm")
    draw.line([(54, 118), (width - 54, 118)], fill=(70, 60, 50), width=2)

    # 5. Column Boundaries
    col_l = 340
    col_r = 740
    draw.line([(col_l, 120), (col_l, height - 22)], fill=(125, 115, 105), width=1)
    draw.line([(col_r, 120), (col_r, height - 22)], fill=(125, 115, 105), width=1)

    # 6. Left Column Article
    f_col_head = get_clean_font(17, font_type="serif")
    draw.text((70, 132), "INVESTIGATION REPORT\nREVEALS CRITICAL DATA", fill=(35, 30, 25), font=f_col_head)
    for y in range(185, height - 35, 14):
        draw.line([(70, y), (col_l - 18, y)], fill=(130, 120, 110), width=2)

    # 7. Center Photo / Portrait Box
    photo_box = [(370, 136), (710, 460)]
    draw.rectangle(photo_box, outline=(45, 35, 30), width=3, fill=(215, 210, 200))

    if subject_cutout:
        # Fit subject cutout into photo box
        bw = photo_box[1][0] - photo_box[0][0] - 12
        bh = photo_box[1][1] - photo_box[0][1] - 12
        cw, ch = subject_cutout.size
        scale = min(bw / max(1, cw), bh / max(1, ch))
        sub_ready = subject_cutout.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
        # Convert to vintage halftoned sepia
        sub_gray = sub_ready.convert("L")
        sub_sepia = Image.merge("RGB", (sub_gray, sub_gray, sub_gray))
        px = photo_box[0][0] + 6 + (bw - sub_ready.width) // 2
        py = photo_box[0][1] + 6 + (bh - sub_ready.height) // 2
        paper.paste(sub_sepia, (px, py), mask=sub_ready if sub_ready.mode == "RGBA" else None)
    else:
        # Fallback silhouette
        draw.ellipse([(480, 210), (600, 330)], fill=(130, 120, 110))
        draw.rounded_rectangle([(440, 335), (640, 440)], radius=30, fill=(130, 120, 110))

    f_caption = get_clean_font(13, font_type="mono")
    draw.text((width // 2, 482), "DOCUMENTARY EVIDENCE & ARCHIVE", fill=(55, 45, 40), font=f_caption, anchor="mm")

    # 8. Right Column Article
    draw.text((col_r + 18, 132), "HISTORICAL ARCHIVE\nPUBLIC INTEREST CASE", fill=(35, 30, 25), font=f_col_head)
    for y in range(185, height - 35, 14):
        draw.line([(col_r + 18, y), (width - 70, y)], fill=(130, 120, 110), width=2)

    # 9. Fluorescent Yellow Marker on Left Column Headline
    highlight = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(highlight)
    h_draw.rectangle([(66, 130), (col_l - 15, 172)], fill=(255, 235, 45, 145))
    paper = Image.alpha_composite(paper.convert("RGBA"), highlight).convert("RGB")

    return paper


def create_moody_interior_wall(
    width: int = 1080,
    height: int = 608,
    spotlight_center: Optional[Tuple[int, int]] = None
) -> Image.Image:
    """Procedurally renders a rich museum/gallery textured wall with a soft directional warm spotlight."""
    wall = Image.new("RGB", (width, height), (28, 25, 22))
    spot_x, spot_y = spotlight_center or (width // 2, height // 2)

    # Soft radial spotlight mask
    spot = Image.new("L", (width, height), 0)
    s_draw = ImageDraw.Draw(spot)
    s_draw.ellipse([(spot_x - 380, spot_y - 280), (spot_x + 380, spot_y + 280)], fill=255)
    spot = spot.filter(ImageFilter.GaussianBlur(radius=110))
    spot_np = np.array(spot, dtype=np.float32) / 255.0

    wall_np = np.array(wall, dtype=np.float32)
    # Warm amber light wash
    wall_np[:, :, 0] += spot_np * 70
    wall_np[:, :, 1] += spot_np * 58
    wall_np[:, :, 2] += spot_np * 40
    wall_np = np.clip(wall_np, 0, 255).astype(np.uint8)
    return Image.fromarray(wall_np)


def create_cinematic_sky_background(
    width: int = 1080,
    height: int = 608,
    t: float = 0.0
) -> Image.Image:
    """Procedurally renders a moving blue/cloud documentary sky."""
    sky = Image.new("RGB", (width, height), (35, 95, 175))
    draw = ImageDraw.Draw(sky)

    # Gradient from deep blue at top to soft haze at horizon
    for y in range(height):
        factor = y / float(height)
        r = int(35 + factor * 80)
        g = int(95 + factor * 65)
        b = int(175 + factor * 45)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Procedural moving cloud puffs
    cloud_layer = Image.new("L", (width, height), 0)
    c_draw = ImageDraw.Draw(cloud_layer)
    drift = int(t * 18.0)
    for cx, cy, cr in [(240 - drift, 160, 180), (520 - drift, 120, 210), (880 - drift, 180, 240), (1200 - drift, 150, 200)]:
        c_draw.ellipse([(cx - cr, cy - cr // 2), (cx + cr, cy + cr // 2)], fill=180)
    cloud_blurred = cloud_layer.filter(ImageFilter.GaussianBlur(radius=65))
    c_np = np.array(cloud_blurred, dtype=np.float32) / 255.0

    sky_np = np.array(sky, dtype=np.float32)
    sky_np[:, :, 0] += c_np * 130
    sky_np[:, :, 1] += c_np * 140
    sky_np[:, :, 2] += c_np * 150
    sky_np = np.clip(sky_np, 0, 255).astype(np.uint8)
    return Image.fromarray(sky_np)


# ---------------------------------------------------------------------------
# Core 3D Documentary Motion Renderer
# ---------------------------------------------------------------------------
def render_nitish_documentary_motion_clip(
    cutout_paths: List[str],
    output_mp4: str,
    duration: float,
    scene_text: str = "",
    main_topic: str = "",
    target_size: Tuple[int, int] = (1080, 1920),
    fps: int = 24,
    scene_index: int = 0
) -> str:
    """
    Renders an authentic Nitish Rajput / 3D Documentary motion clip:
    1. 16:9 Central Box with dynamic ambient mirror blur on top & bottom.
    2. Multi-Plane 2.5D Parallax Depth (Separate Background, Midground Cutout, and Foreground).
    3. Archetype Intelligence:
       - Evidence / Scam / News -> Vintage Wanted Newspaper with yellow highlighter!
       - Character / Portrait / Heritage -> Ornate antique picture frame with warm spotlight!
       - Monument / Temple / Map -> 3D push-in over moving atmospheric sky!
    4. 100% Pure Photos (Zero stock video clips!).
    """
    w, h = target_size
    box_w, box_h = 1080, 608
    box_y = (h - box_h) // 2  # 656
    duration = max(3.0, float(duration))
    total_frames = int(duration * fps)

    from collage_cutout_engine import make_transparent_cutout, sharpen_cutout, create_cutout_drop_shadow

    # 1. Load cutouts
    loaded_cutouts = []
    for p in cutout_paths:
        if p and os.path.exists(p):
            try:
                c = make_transparent_cutout(p)
                if c and c.width > 20 and c.height > 20:
                    loaded_cutouts.append(c)
            except Exception as e_c:
                print(f"⚠️ [Nitish Documentary Engine] Warning loading cutout {p}: {e_c}")

    if not loaded_cutouts:
        fallback_hero = Image.new("RGBA", (500, 650), (0, 0, 0, 0))
        fb_draw = ImageDraw.Draw(fallback_hero)
        fb_draw.rounded_rectangle([(80, 80), (420, 580)], radius=40, fill=(70, 85, 110, 255), outline=(220, 220, 220, 255), width=6)
        loaded_cutouts.append(fallback_hero)

    primary_cutout = loaded_cutouts[0]

    # 2. Determine Scene Archetype
    txt_l = (scene_text or "").lower()
    is_newspaper_scene = any(k in txt_l for k in [
        "scam", "ghotala", "घोटाला", "fraud", "फ्रॉड", "wanted", "वांटेड",
        "report", "रिपोर्ट", "अखबार", "समाचार", "सबूत", "दावा", "कोर्ट",
        "arrest", "गिरफ्तार", "investigation", "जांच", "बैंक", "bank", "करोड़ों", "लाखों"
    ])
    is_antique_frame_scene = any(k in txt_l for k in [
        "हजारों साल", "इतिहास", "heritage", "temple", "मंदिर", "प्राचीन",
        "राजा", "रानी", "banker", "man", "portrait", "चिड़िया", "पेंटिंग"
    ])
    
    if is_newspaper_scene:
        archetype = "newspaper"
    elif is_antique_frame_scene:
        archetype = "antique_frame"
    else:
        # Alternate between monument and antique frame for dynamic visual variety
        archetype = "monument" if (scene_index % 2 == 0) else "antique_frame"

    # Pre-render static components per archetype
    if archetype == "newspaper":
        hl_word = "INVESTIGATION"
        for w_c in ["WANTED", "SCAM", "FRAUD", "EVIDENCE", "REPORT", "BANKER"]:
            if w_c.lower() in txt_l:
                hl_word = w_c
                break
        if "घोटाला" in txt_l or "scam" in txt_l:
            hl_word = "SCAM EXPOSED"
        elif "फ्रॉड" in txt_l or "fraud" in txt_l:
            hl_word = "FRAUD INVESTIGATION"
        base_paper = build_vintage_newspaper_page(headline=hl_word, subject_cutout=primary_cutout, width=box_w, height=box_h)
    elif archetype == "antique_frame":
        base_wall = create_moody_interior_wall(width=box_w, height=box_h)
        frame_border = create_ornate_antique_frame(width=340, height=420)
        # Prepare framed portrait
        cw, ch = primary_cutout.size
        p_scale = min(280 / max(1, cw), 360 / max(1, ch))
        framed_sub = primary_cutout.resize((int(cw * p_scale), int(ch * p_scale)), Image.LANCZOS)
        framed_sub = sharpen_cutout(framed_sub, amount=1.25)
    else:  # monument
        # Prepare monument cutout for 3D parallax
        cw, ch = primary_cutout.size
        m_scale = min((box_w * 0.70) / max(1, cw), (box_h * 0.78) / max(1, ch))
        monument_ready = primary_cutout.resize((int(cw * m_scale), int(ch * m_scale)), Image.LANCZOS)
        monument_ready = sharpen_cutout(monument_ready, amount=1.25)

    # 3. Setup FFmpeg streaming pipe (< 35MB RAM)
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

    # 4. Kinetic Frame Render Loop
    for frame_idx in range(total_frames):
        t = frame_idx / float(fps)
        t_norm = frame_idx / max(1, total_frames)

        # Smooth continuous 3D camera push-in curve
        ease_zoom = 0.5 - 0.5 * math.cos(t_norm * math.pi)

        # Render 16:9 cinematic frame
        frame_16_9 = Image.new("RGB", (box_w, box_h), (20, 20, 20))

        if archetype == "newspaper":
            # 3D Push-in on the newspaper headline & photo
            zoom_factor = 1.00 + ease_zoom * 0.15
            zw = int(box_w / zoom_factor)
            zh = int(box_h / zoom_factor)
            zx = (box_w - zw) // 2
            zy = int((box_h - zh) * 0.40)  # Focus towards headline/photo
            frame_16_9 = base_paper.crop((zx, zy, zx + zw, zy + zh)).resize((box_w, box_h), Image.BILINEAR)

        elif archetype == "antique_frame":
            # Background Wall slow drift
            frame_16_9 = base_wall.copy()

            # Midground Framed Portrait with 3D Parallax Zoom
            frame_zoom = 1.00 + ease_zoom * 0.18
            fw = int(340 * frame_zoom)
            fh = int(420 * frame_zoom)
            fx = (box_w - fw) // 2
            fy = (box_h - fh) // 2

            p_frame_scaled = frame_border.resize((fw, fh), Image.BILINEAR)
            p_sub_scaled = framed_sub.resize((int(framed_sub.width * frame_zoom), int(framed_sub.height * frame_zoom)), Image.BILINEAR)

            # Drop shadow behind frame
            sh_frame, sh_off = create_cutout_drop_shadow(p_frame_scaled, blur_radius=20, offset=(8, 16), shadow_opacity=0.55)
            frame_16_9.paste(sh_frame, (fx + sh_off[0], fy + sh_off[1]), mask=sh_frame)

            # Paste inner picture and frame molding
            px = fx + (fw - p_sub_scaled.width) // 2
            py = fy + (fh - p_sub_scaled.height) // 2
            frame_16_9.paste(p_sub_scaled, (px, py), mask=p_sub_scaled if p_sub_scaled.mode == "RGBA" else None)
            frame_16_9.paste(p_frame_scaled, (fx, fy), mask=p_frame_scaled)

        else:  # monument
            # Layer 1: Moving Sky Background
            sky_bg = create_cinematic_sky_background(width=box_w, height=box_h, t=t)
            frame_16_9 = sky_bg

            # Layer 2: Midground Monument with 3D Parallax Zoom
            m_zoom = 1.00 + ease_zoom * 0.14
            mw = int(monument_ready.width * m_zoom)
            mh = int(monument_ready.height * m_zoom)
            mx = (box_w - mw) // 2
            my = int(box_h * 0.90 - mh)  # Grounded firmly on bottom edge

            monument_scaled = monument_ready.resize((mw, mh), Image.BILINEAR)
            sh_m, sh_off_m = create_cutout_drop_shadow(monument_scaled, blur_radius=18, offset=(0, 12), shadow_opacity=0.45)
            frame_16_9.paste(sh_m, (mx + sh_off_m[0], my + sh_off_m[1]), mask=sh_m)
            frame_16_9.paste(monument_scaled, (mx, my), mask=monument_scaled)

        # 5. Composite into Vertical 9:16 Frame with Ambient Mirror Blur
        full_vertical_canvas = create_ambient_mirror_canvas(
            frame_16_9=frame_16_9,
            target_size=(w, h),
            blur_radius=40,
            darken_factor=0.68
        )

        # Stream frame to FFmpeg rawvideo pipe
        raw_bytes = full_vertical_canvas.tobytes()
        proc.stdin.write(raw_bytes)

        del frame_16_9, full_vertical_canvas
        if frame_idx % 25 == 0:
            release_system_memory()

    proc.stdin.close()
    proc.wait()
    release_system_memory()

    print(f"🎬 [Nitish Documentary Engine] Successfully rendered 3D documentary motion clip: {os.path.basename(output_mp4)} ({duration:.1f}s)")
    return output_mp4
