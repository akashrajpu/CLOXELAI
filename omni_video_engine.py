#!/usr/bin/env python3
"""
===============================================================================
    OMNI VIDEO ENGINE (GEMINI AI AUTOMATIC HINGLISH MULTI-CLIP MP4 GENERATOR)
===============================================================================
Description : High-Speed Gemini AI Multi-Clip Video Generator:
              1. User inputs raw Hinglish prompt.
              2. Gemini AI filters prompt & breaks story into micro-scenes with action scripts.
              3. Each micro-scene generates its own voiceover audio & line stick figure animation clip.
              4. FFmpeg concatenates all micro-clips into 1 complete MP4 Video!

Author      : Antigravity AI Engine
===============================================================================
"""

import os
import time
import uuid
import json
import shutil
from typing import Dict, Any, Optional, Callable

from gemini_engine import generate_gemini_video_script
from audio_engine import make_audio
from rapid_story_engine import export_rapid_story_video


class OmniVideoEngine:
    """
    Main Orchestrator for Gemini AI Automatic Hinglish Multi-Clip Video Generation.
    """

    def __init__(self, output_dir: str = "static"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_video(self, prompt: str, target_duration: int = 30,
                       api_key: Optional[str] = None, aspect_ratio: str = "16:9",
                       log_callback: Optional[Callable[[str, int], None]] = None) -> Dict[str, Any]:
        """
        Processes Hinglish prompt with Gemini AI, generates micro-scene voiceovers & video clips,
        and concatenates them into 1 final MP4 video.
        """
        job_id = str(uuid.uuid4())[:8]

        def log(msg: str, progress: int = 0):
            timestamp = time.strftime("%H:%M:%S")
            formatted_msg = f"[{timestamp}] {msg}"
            print(formatted_msg)
            if log_callback:
                log_callback(formatted_msg, progress)

        t_start = time.time()
        log(f"🎬 Starting Gemini AI Multi-Clip Job #{job_id}", 5)
        log(f"Prompt: '{prompt[:60]}...' | Duration: {target_duration}s", 10)

        # 1. Gemini AI API prompt filtering & micro-scene breakdown
        log("🤖 [Step 1/3] Gemini AI filtering Hinglish prompt into micro-scenes...", 15)
        script_data = generate_gemini_video_script(prompt, target_duration, api_key)
        scenes = script_data.get('scenes', [])

        if not scenes:
            log("❌ Error: Failed to generate scenes from prompt.", 100)
            raise ValueError("Failed to parse scenes.")

        log(f"✅ [Step 1/3] Gemini AI created {len(scenes)} distinct micro-scenes!", 25)

        # 2. Synthesize audio voiceovers for each micro-scene
        audio_files = []
        for idx, scene in enumerate(scenes):
            narration_text = scene.get('narration') or scene.get('text') or prompt
            audio_path = os.path.join(self.output_dir, f"audio_scene_{job_id}_{idx}.mp3")
            log(f"🗣️ [Scene {idx+1}/{len(scenes)}] Synthesizing voiceover: '{narration_text[:35]}...'", 30 + idx * 5)
            make_audio(narration_text, audio_path, voice_id="hi-IN-MadhurNeural")
            audio_files.append(audio_path)

        # 3. Export & concatenate micro-scene clips to final MP4 video
        output_mp4_name = os.path.join(self.output_dir, f"omni_video_{job_id}.mp4")
        static_main_path = os.path.join(self.output_dir, "omni_video.mp4")
        target_size = (1280, 720) if aspect_ratio == "16:9" else (720, 1280)

        log(f"🎬 [Step 3/3] Rendering {len(scenes)} micro-clips & Concatenating with FFmpeg...", 50)
        export_rapid_story_video(
            prompt=prompt,
            scenes=scenes,
            audio_files=audio_files,
            output_name=output_mp4_name,
            target_size=target_size,
            log_callback=log
        )

        if os.path.exists(output_mp4_name):
            shutil.copyfile(output_mp4_name, static_main_path)

        timestamp = int(time.time() * 1000)
        video_url = f"/static/omni_video.mp4?v={timestamp}"

        t_end = time.time()
        elapsed = t_end - t_start
        log(f"🎉 [Success] Gemini AI Multi-Clip Video exported in {elapsed:.2f} seconds!", 100)

        return {
            'status': 'success',
            'video_url': video_url,
            'title': script_data.get('title', "Multi-Clip Story Video"),
            'duration': target_duration,
            'scenes': scenes
        }


if __name__ == "__main__":
    engine = OmniVideoEngine()
    print("Testing OmniVideoEngine Gemini AI Multi-Clip Generator...")
