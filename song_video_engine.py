"""
=============================================================================
CLOXEL AI - ULTRA SONG & MUSIC VIDEO ENGINE
=============================================================================
Automated YouTube Song Audio Downloader, Synced Lyrics Extractor & 
Dual-Engine (Stock Video Clips / 3D Photo Motion) Music Video Generator.
=============================================================================
"""

import os
import re
import glob
import math
import random
import subprocess
from typing import Optional, List, Dict, Any

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, ImageClip, ColorClip, 
        CompositeVideoClip, concatenate_videoclips
    )
except ImportError:
    try:
        from moviepy import VideoFileClip, AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, concatenate_videoclips
    except ImportError:
        VideoFileClip = None

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


def download_youtube_song_audio(
    source_type: str = "url",
    song_url: Optional[str] = None,
    singer_name: Optional[str] = None,
    song_title: Optional[str] = None,
    target_dir: str = "temp_song"
) -> Dict[str, Any]:
    """
    Downloads official song audio from YouTube via URL or Singer/Song search.
    Returns dict: {'audio_path': str, 'title': str, 'duration': float}
    """
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, "master_song_audio.mp3")

    # If already downloaded in this job directory, return immediately
    if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
        return {"audio_path": target_path, "title": song_title or singer_name or "Song", "duration": 60.0}

    download_target = None
    if source_type == "url" and song_url and song_url.strip():
        raw_u = song_url.strip()
        # Clean YouTube tracking parameters (e.g. ?si=...)
        vid_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', raw_u)
        if vid_match:
            download_target = f"https://www.youtube.com/watch?v={vid_match.group(1)}"
        else:
            download_target = raw_u
    elif singer_name and singer_name.strip():
        clean_singer = re.sub(r'[^\w\s]', '', singer_name).strip()
        clean_title = re.sub(r'[^\w\s]', '', song_title or "").strip()
        download_target = f"ytsearch1:{clean_singer} {clean_title} official audio song".strip()
    elif song_url and song_url.strip():
        raw_u = song_url.strip()
        vid_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', raw_u)
        if vid_match:
            download_target = f"https://www.youtube.com/watch?v={vid_match.group(1)}"
        else:
            download_target = raw_u
    else:
        download_target = "ytsearch1:trending lofi romantic song instrumental"

    print(f"🎵 [Song Engine] Target Audio Search/URL: '{download_target}'...")

    extracted_title = song_title or singer_name or "Official Song"
    extracted_duration = 60.0

    if yt_dlp:
        out_template = os.path.join(target_dir, "raw_song.%(ext)s")
        client_configs = [
            (['android'], 'com.google.android.youtube/19.29.37 (Linux; U; Android 11)'),
            (['tv_embedded'], 'Mozilla/5.0 (SMART-TV; LINUX; Tizen 6.0) AppleWebkit/537.36 (KHTML, like Gecko)'),
            (['android_vr'], 'com.google.android.youtube/19.29.37 (Linux; U; Android 11)')
        ]

        for clients, ua in client_configs:
            ydl_opts = {
                'format': '18/bestaudio/best',
                'outtmpl': out_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'socket_timeout': 35,
                'max_filesize': 70 * 1024 * 1024,
                'extractor_args': {
                    'youtube': {
                        'player_client': clients,
                    }
                },
                'http_headers': {
                    'User-Agent': ua
                }
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(download_target, download=True)
                    if 'entries' in info and info['entries']:
                        entry = info['entries'][0]
                    else:
                        entry = info
                    
                    if entry:
                        extracted_title = entry.get('title') or extracted_title
                        extracted_duration = float(entry.get('duration') or 60.0)

                # Locate downloaded mp3
                possible_files = glob.glob(os.path.join(target_dir, "raw_song*.mp3")) + glob.glob(os.path.join(target_dir, "*.mp3"))
                valid_files = [f for f in possible_files if os.path.getsize(f) > 5000]
                if valid_files:
                    actual_mp3 = valid_files[0]
                    if actual_mp3 != target_path:
                        import shutil
                        shutil.copy2(actual_mp3, target_path)
                    print(f"✅ [Song Engine] Downloaded Audio Successfully via {clients[0]}: '{extracted_title}' ({os.path.getsize(target_path)} bytes)")
                    return {
                        "audio_path": target_path,
                        "title": extracted_title,
                        "duration": extracted_duration
                    }
            except Exception as e:
                print(f"⚠️ [Song Engine] yt-dlp client {clients[0]} exception: {e}")

    # Fallback to local background music if YouTube download failed
    print("⚠️ [Song Engine] Using local melodic music track fallback...")
    fallback_sources = [
        os.path.join("static", "cool.mp3"),
        os.path.join("static", "cool1.mp3"),
        os.path.join("static", "cool2.mp3")
    ]
    for fb in fallback_sources:
        if os.path.exists(fb):
            import shutil
            shutil.copy2(fb, target_path)
            return {"audio_path": target_path, "title": extracted_title, "duration": 60.0}

    return {"audio_path": target_path, "title": extracted_title, "duration": 60.0}


def generate_song_lyric_scenes(
    user_lyrics: Optional[str] = None,
    singer_name: Optional[str] = None,
    song_title: Optional[str] = None,
    target_duration: int = 30
) -> List[Dict[str, Any]]:
    """
    Prepares lyrical scenes with duration, text, and visual search keyword.
    """
    lines = []
    # If user provided actual custom lyrics (ignore generic placeholder title strings)
    generic_placeholders = {"singer song video", "song video", "youtube song video", "youtube music video", "song"}
    if user_lyrics and user_lyrics.strip() and user_lyrics.strip().lower() not in generic_placeholders:
        raw_lines = [l.strip() for l in user_lyrics.splitlines() if len(l.strip()) > 1 and l.strip().lower() not in generic_placeholders]
        if raw_lines:
            lines = raw_lines

    if not lines:
        # Generate musical visual hook lines matching the vibe
        singer = (singer_name or "").strip()
        title = (song_title or "").strip()
        # Clean YouTube video title suffixes like "(Lyrical)", "| Full Song", etc.
        clean_title = re.sub(r'\(.*?\)|\[.*?\]', '', title).split('|')[0].split(' - ')[0].strip()
        display_name = f"{clean_title} — {singer}".strip(' —') if singer and clean_title != singer else (clean_title or singer or "Sirf Tum")
        lines = [
            f"✨ {display_name}",
            "🌙 Teri yaadon ka ek haseen aalam",
            "💫 Har lafz mein bas tera hi ehsaas",
            "❤️ Dil ki har dhadkan pe tera hi naam",
            "🌟 Jab saath ho tera, toh har pal mehez ek khwaab"
        ]

    # Target 3 to 6 scenes
    if len(lines) > 8:
        lines = lines[:8]
    num_scenes = max(1, len(lines))
    per_scene_dur = max(3.0, round(target_duration / num_scenes, 2))

    scenes = []
    for idx, line in enumerate(lines):
        # Extract visual search keywords from line
        clean_words = [w for w in re.findall(r'[a-zA-Z]+', line) if len(w) >= 4 and w.lower() not in {
            "this", "that", "with", "from", "have", "been", "will", "would", "could", "every",
            "when", "what", "where", "into", "your", "they", "them", "feel", "lost"
        }]
        if clean_words:
            keyword = " ".join(clean_words[:2]) + " cinematic aesthetic"
        else:
            keyword = f"{singer_name or 'music'} aesthetic concert stage night"
        
        scenes.append({
            "index": idx,
            "text": line,
            "keyword": keyword,
            "duration": per_scene_dur
        })

    return scenes


def render_lyrics_overlay(
    text: str,
    target_size: tuple,
    font_path: str = "./fonts/Arial.ttf",
    font_color: str = "yellow"
) -> Image.Image:
    """
    Renders high-definition glowing lyrics subtitle image with black stroke and drop shadow.
    """
    tw, th = target_size
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Determine font size dynamically based on target width
    font_size = max(28, int(tw * 0.048))
    loaded_font = None
    if font_path and os.path.exists(font_path):
        try:
            loaded_font = ImageFont.truetype(font_path, font_size)
        except Exception:
            pass
    if not loaded_font:
        try:
            loaded_font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            loaded_font = ImageFont.load_default()

    # Color map
    color_map = {
        "yellow": (253, 224, 71, 255),
        "white": (255, 255, 255, 255),
        "cyan": (56, 189, 248, 255),
        "pink": (244, 114, 182, 255),
        "gold": (251, 191, 36, 255),
    }
    fill_color = color_map.get(font_color.lower(), (253, 224, 71, 255))
    stroke_color = (15, 23, 42, 240)

    # Wrap text cleanly
    max_chars = 32 if tw < th else 54
    words = text.split()
    wrapped_lines = []
    current_line = []
    current_len = 0
    for w in words:
        if current_len + len(w) + 1 > max_chars:
            wrapped_lines.append(" ".join(current_line))
            current_line = [w]
            current_len = len(w)
        else:
            current_line.append(w)
            current_len += len(w) + 1
    if current_line:
        wrapped_lines.append(" ".join(current_line))

    # Calculate height and center
    line_height = int(font_size * 1.35)
    total_h = len(wrapped_lines) * line_height
    y_start = int(th * 0.72)  # Place in bottom-third for music video subtitle style

    for i, line_text in enumerate(wrapped_lines):
        try:
            bbox = draw.textbbox((0, 0), line_text, font=loaded_font)
            line_w = bbox[2] - bbox[0]
        except Exception:
            line_w = len(line_text) * (font_size * 0.5)

        x = (tw - line_w) // 2
        y = y_start + (i * line_height)

        # Draw dark translucent backdrop pill behind lyrics
        pad_x = 18
        pad_y = 6
        draw.rounded_rectangle(
            [x - pad_x, y - pad_y, x + line_w + pad_x, y + line_height + pad_y],
            radius=12,
            fill=(10, 10, 18, 160)
        )

        # Draw thick stroke for crystal-clear readability
        draw.text(
            (x, y), line_text,
            font=loaded_font,
            fill=fill_color,
            stroke_width=max(2, int(font_size * 0.08)),
            stroke_fill=stroke_color
        )

    return img


def create_photo_motion_scene_clip(
    img_path: str,
    duration: float,
    target_size: tuple,
    direction: str = "zoom_in"
) -> Any:
    """
    Creates a cinematic Ken Burns zoom/motion VideoClip from a photo.
    """
    tw, th = target_size
    try:
        orig = Image.open(img_path).convert("RGB")
        # Pre-scale so image fits canvas nicely
        aspect_orig = orig.width / orig.height
        aspect_target = tw / th
        if aspect_orig > aspect_target:
            new_h = int(th * 1.25)
            new_w = int(new_h * aspect_orig)
        else:
            new_w = int(tw * 1.25)
            new_h = int(new_w / aspect_orig)
        
        orig_resized = orig.resize((new_w, new_h), Image.Resampling.LANCZOS)
        base_np = np.array(orig_resized)

        def make_frame(t):
            progress = min(1.0, max(0.0, t / max(0.1, duration)))
            if direction == "zoom_in":
                scale = 1.0 + (0.15 * progress)
            else:
                scale = 1.15 - (0.15 * progress)

            cur_w = int(tw * scale)
            cur_h = int(th * scale)
            
            # Crop center
            cx = base_np.shape[1] // 2
            cy = base_np.shape[0] // 2
            x1 = max(0, cx - cur_w // 2)
            y1 = max(0, cy - cur_h // 2)
            x2 = min(base_np.shape[1], x1 + cur_w)
            y2 = min(base_np.shape[0], y1 + cur_h)

            crop = base_np[y1:y2, x1:x2]
            im_crop = Image.fromarray(crop).resize((tw, th), Image.Resampling.BILINEAR)
            return np.array(im_crop)

        from moviepy.editor import VideoClip
        return VideoClip(make_frame, duration=duration)
    except Exception as e:
        print(f"⚠️ Photo motion frame fallback: {e}")
        from moviepy.editor import ColorClip
        return ColorClip(size=target_size, color=(20, 15, 35), duration=duration)


def build_full_song_video(
    req: Any,
    job_id: str,
    job_dir: str,
    output_path: str
) -> str:
    """
    Full pipeline to generate Ultra Song & Music Video.
    """
    target_duration = int(req.duration if hasattr(req, 'duration') and req.duration else 30)
    target_aspect = getattr(req, 'aspect_ratio', '9:16') or '9:16'
    
    if target_aspect == '16:9':
        target_size = (1280, 720)
        orientation = "landscape"
    elif target_aspect == '1:1':
        target_size = (720, 720)
        orientation = "portrait"
    else:
        target_size = (720, 1280)
        orientation = "portrait"

    print(f"\n==================================================")
    print(f"🎵 [ULTRA SONG VIDEO PIPELINE] Job ID: {job_id}")
    print(f"📊 Target Duration: {target_duration}s | Aspect: {target_aspect} | Size: {target_size}")
    print(f"==================================================")

    # 1. Download Master Song Audio from YouTube
    song_source_type = getattr(req, 'song_source_type', 'url') or 'url'
    song_url = getattr(req, 'song_url', '') or ''
    singer_name = getattr(req, 'singer_name', '') or ''
    song_title = getattr(req, 'song_title', '') or ''
    song_lyrics = getattr(req, 'song_lyrics', '') or getattr(req, 'full_script', '')

    audio_res = download_youtube_song_audio(
        source_type=song_source_type,
        song_url=song_url,
        singer_name=singer_name,
        song_title=song_title,
        target_dir=job_dir
    )
    master_audio_path = audio_res.get('audio_path')

    # 2. Extract or Generate Synced Lyric Scenes
    scenes = generate_song_lyric_scenes(
        user_lyrics=song_lyrics,
        singer_name=singer_name,
        song_title=song_title or audio_res.get('title'),
        target_duration=target_duration
    )
    print(f"📝 [Song Engine] Prepared {len(scenes)} lyrics scenes for video production.")

    # 3. Visual Assets & Video Clips Generation
    visual_mode = getattr(req, 'song_visual_mode', 'motion') or getattr(req, 'mode', 'ultra')
    is_stock_video = (visual_mode in ['video', 'standard'])

    scene_clips = []
    font_path = f"./fonts/{req.font_name}" if hasattr(req, 'font_name') and req.font_name else "./fonts/Arial.ttf"
    font_color = getattr(req, 'font_color', 'yellow') or 'yellow'

    from video_fetcher import fetch_videos
    from web_image_fetcher import fetch_web_image

    for sc in scenes:
        idx = sc["index"]
        sc_dur = sc["duration"]
        lyric_text = sc["text"]
        kw = sc["keyword"]
        print(f"\n🎬 [Scene {idx+1}/{len(scenes)}] Mode: {visual_mode.upper()} | Duration: {sc_dur}s | Text: '{lyric_text}'")

        v_clip = None
        if is_stock_video:
            # 🎥 Stock Video Clips (Pexels / Pixabay)
            v_temp = os.path.join(job_dir, f"stock_vid_{idx}.mp4")
            v_paths = fetch_videos(
                kw, v_temp,
                orientation=orientation,
                category="Music",
                video_type="short" if target_aspect == "9:16" else "long",
                topic=singer_name or song_title or "music"
            )
            if v_paths and os.path.exists(v_paths[0]) and os.path.getsize(v_paths[0]) > 5000:
                try:
                    loaded = VideoFileClip(v_paths[0])
                    # Crop / resize to target_size
                    loaded = loaded.resize(height=target_size[1]) if loaded.h < target_size[1] else loaded.resize(width=target_size[0])
                    loaded = loaded.crop(x_center=loaded.w/2, y_center=loaded.h/2, width=target_size[0], height=target_size[1])
                    if loaded.duration < sc_dur:
                        # Loop video if shorter than scene duration
                        n_loops = int(math.ceil(sc_dur / loaded.duration))
                        loaded = concatenate_videoclips([loaded] * n_loops).subclip(0, sc_dur)
                    else:
                        loaded = loaded.subclip(0, sc_dur)
                    v_clip = loaded
                except Exception as e_v:
                    print(f"⚠️ Stock video clip load failed: {e_v}")

        if not v_clip:
            # ⚡ Ultra 3D Photo Motion
            img_path = os.path.join(job_dir, f"motion_photo_{idx}.jpg")
            photo_query = f"{kw} 4k aesthetic wallpaper photo"
            fetch_web_image(photo_query, img_path)
            
            direction = "zoom_in" if idx % 2 == 0 else "zoom_out"
            v_clip = create_photo_motion_scene_clip(img_path, sc_dur, target_size, direction=direction)

        # 4. Generate & Composite Lyrics Subtitle Overlay
        overlay_pil = render_lyrics_overlay(
            text=lyric_text,
            target_size=target_size,
            font_path=font_path,
            font_color=font_color
        )
        overlay_path = os.path.join(job_dir, f"lyrics_overlay_{idx}.png")
        overlay_pil.save(overlay_path)

        overlay_clip = ImageClip(overlay_path).set_duration(sc_dur)
        composite_scene = CompositeVideoClip([v_clip, overlay_clip], size=target_size).set_duration(sc_dur)
        scene_clips.append(composite_scene)

    # 5. Concatenate Video Scenes
    print(f"\n🎞️ [Song Engine] Concatenating {len(scene_clips)} scene clips...")
    final_video = concatenate_videoclips(scene_clips, method="compose")

    # 6. Attach Master Song Audio
    if os.path.exists(master_audio_path) and os.path.getsize(master_audio_path) > 5000:
        try:
            full_audio = AudioFileClip(master_audio_path)
            # Trim to video duration
            if full_audio.duration > final_video.duration:
                trimmed_audio = full_audio.subclip(0, final_video.duration)
            else:
                trimmed_audio = full_audio
            final_video = final_video.set_audio(trimmed_audio)
            print(f"🎶 [Song Engine] Attached Master Song Audio Track ({trimmed_audio.duration}s)")
        except Exception as e_aud:
            print(f"⚠️ Audio attachment warning: {e_aud}")

    # 7. Export Final Video
    print(f"🚀 [Song Engine] Rendering Final Song Video -> {output_path}...")
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
        logger=None
    )

    # Close clips to free memory
    try:
        final_video.close()
        for sc_c in scene_clips:
            sc_c.close()
    except Exception:
        pass

    print(f"🎉 SUCCESS! Ultra Song Video Produced -> {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path
