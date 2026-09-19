#!/usr/bin/env python3
"""
===============================================================================
  RAPID STORY ENGINE 15.0 (GEMINI AI MULTI-CLIP LINE STICK MP4 CONCATENATOR)
===============================================================================
Description : High-Speed Multi-Clip Engine. Takes Gemini AI filtered micro-scenes,
              renders each micro-clip with the user's exact PIL line stick figure code
              on PURE WHITE canvas ("white"), and concatenates them with FFmpeg!

Author      : Antigravity AI Engine
===============================================================================
"""

import os
import math
import time
import subprocess
from typing import List, Dict, Tuple, Any
from PIL import Image, ImageDraw
from omni_cartoon_renderer import UserLineStickRenderer, parse_prompt_to_user_script


def render_single_micro_clip(script_text: str, audio_path: str, output_mp4: str,
                             target_size: Tuple[int, int] = (1280, 720)) -> str:
    """
    Renders 1 micro-clip MP4 from action script + audio narration.
    """
    job_dir = os.path.dirname(output_mp4) if os.path.dirname(output_mp4) else "."
    os.makedirs(job_dir, exist_ok=True)

    frames = UserLineStickRenderer.generate_frames_from_script(script_text, size=target_size, line_thickness=8)
    if not frames:
        frames = [Image.new("RGB", target_size, "white")]

    temp_frames_dir = os.path.join(job_dir, f"temp_frames_{os.path.basename(output_mp4)}")
    os.makedirs(temp_frames_dir, exist_ok=True)

    for idx, frame_img in enumerate(frames):
        frame_img.save(os.path.join(temp_frames_dir, f"frame_{idx:04d}.png"), format="PNG")

    temp_video_only = os.path.abspath(os.path.join(job_dir, f"temp_v_{os.path.basename(output_mp4)}"))

    cmd = [
        "ffmpeg", "-y", "-r", "20",
        "-i", os.path.join(temp_frames_dir, "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        temp_video_only
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if audio_path and os.path.exists(audio_path) and os.path.getsize(audio_path) > 500:
        cmd = [
            "ffmpeg", "-y", "-i", temp_video_only, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-shortest", output_mp4
        ]
    else:
        cmd = ["ffmpeg", "-y", "-i", temp_video_only, "-c:v", "copy", output_mp4]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    import shutil
    shutil.rmtree(temp_frames_dir, ignore_errors=True)
    if os.path.exists(temp_video_only): os.remove(temp_video_only)

    return output_mp4


def release_system_memory():
    """Forces Python Garbage Collection + Linux C-heap memory reclamation (malloc_trim)."""
    import gc
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL('libc.so.6').malloc_trim(0)
    except Exception:
        pass

def export_rapid_story_video(prompt: str, scenes: List[Dict[str, Any]], audio_files: List[str],
                             output_name: str, target_size: Tuple[int, int] = (1280, 720),
                             log_callback: Any = None) -> str:
    """
    Renders each Gemini AI micro-scene clip and concatenates them with FFmpeg!
    """
    t0 = time.time()
    job_dir = os.path.dirname(output_name) if os.path.dirname(output_name) else "."
    os.makedirs(job_dir, exist_ok=True)

    print(f"\n⚡ [Gemini Multi-Clip Engine] Processing {len(scenes)} micro-scenes...")

    temp_scene_mp4s = []

    for idx, scene in enumerate(scenes):
        action_script = scene.get('action_script') or parse_prompt_to_user_script(scene.get('narration', prompt))
        audio_path = audio_files[idx] if idx < len(audio_files) else ""

        scene_mp4 = os.path.abspath(os.path.join(job_dir, f"temp_micro_scene_{idx}.mp4"))
        render_single_micro_clip(action_script, audio_path, scene_mp4, target_size=target_size)
        temp_scene_mp4s.append(scene_mp4)
        release_system_memory()

        msg = f"⚡ [Micro-Clip {idx+1}/{len(scenes)}] Rendered scene clip successfully!"
        print(f"   {msg}")
        if log_callback:
            pct = 50 + int(((idx + 1) / len(scenes)) * 45)
            log_callback(msg, pct)

    # Concat all micro-clip MP4 files
    concat_list_txt = os.path.abspath(os.path.join(job_dir, "concat_micro_clips.txt"))
    with open(concat_list_txt, "w") as f:
        for mp4_f in temp_scene_mp4s:
            f.write(f"file '{mp4_f}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_txt, "-c", "copy", output_name]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(concat_list_txt): os.remove(concat_list_txt)
    for mp4_f in temp_scene_mp4s:
        if os.path.exists(mp4_f): os.remove(mp4_f)

    t1 = time.time()
    print(f"\n🎉 [Gemini Multi-Clip Engine] Exported Complete Video in {t1 - t0:.2f} seconds!")
    return output_name


if __name__ == "__main__":
    print("Testing rapid_story_engine 15.0...")
