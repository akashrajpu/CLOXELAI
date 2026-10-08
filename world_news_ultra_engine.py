import os
import re
import time
import requests
import uuid
import numpy as np
import imageio
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random
import sys
import colorsys
import copy
import traceback

class SafeImageDrawModule:
    """Pass-through wrapper for ImageDraw"""
    def __init__(self, original_module):
        self._original = original_module
    def __getattr__(self, name):
        return getattr(self._original, name)

def create_emergency_world_news_mp4(prompt, output_mp4, duration, target_size, fps=15):
    """Fallback generator in case Gemini fails"""
    w, h = target_size
    writer = imageio.get_writer(output_mp4, fps=fps, codec='libx264', macro_block_size=None)
    total_frames = int(duration * fps)
    
    for i in range(total_frames):
        img = Image.new('RGB', (w, h), (10, 10, 20))
        draw = ImageDraw.Draw(img)
        
        # Draw some grid
        for x in range(0, w, 50):
            draw.line([(x, 0), (x, h)], fill=(30, 40, 60), width=1)
        for y in range(0, h, 50):
            draw.line([(0, y), (w, y)], fill=(30, 40, 60), width=1)
            
        progress = i / total_frames
        draw.text((w//2 - 150, h//2), "WORLD NEWS ENGINE FALLBACK", fill=(200, 50, 50), font=None)
        draw.text((w//2 - 100, h//2 + 50), f"Frame {i}/{total_frames}", fill=(200, 200, 200), font=None)
        
        frame = np.array(img)
        writer.append_data(frame)
    writer.close()
    return output_mp4

def generate_world_news_ultra_video(user_prompt, output_mp4, duration, target_size=(1080, 1920), fps=15):
    print(f"🌍 [World News Python Engine] Initiating Cinematic Python-based Animation for {duration:.1f}s...")
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("AI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not set.")
        return create_emergency_world_news_mp4(user_prompt, output_mp4, duration, target_size, fps)

    w, h = target_size
    total_frames = int(duration * fps)
    
    system_instruction = f"""Act as a Senior Motion Graphics Developer and Python Expert specializing in programmatic animations.
I have a {duration}-second vertical video script. I need a single-file, production-ready Python script that renders a fully synced cinematic 'World News & Geopolitics' motion graphics video directly to MP4.

Key Technical Requirements:
1. Environment & Output:
   - Use Python's `Pillow` (Image, ImageDraw, ImageFilter, ImageFont), `numpy`, and `imageio`.
   - Output video resolution MUST be {w}x{h} at {fps} fps.
   - You MUST write the MP4 exactly to the variable path `output_mp4_path` provided in your namespace.
   - The video duration MUST be exactly {duration} seconds (i.e. exactly {total_frames} frames).

2. Visual Style (World News & Geopolitics):
   - Dark, premium cinematic background (deep navy #02040a, vignette, glowing grid lines).
   - Use procedural geometric elements like glowing data nodes, connection lines, animated bar charts, or digital maps.
   - Post-processing effects: Add subtle chromatic aberration (using numpy channel shifting), lens flares, or scanlines.
   - Dynamic UI HUD elements: Glowing status badges, counting metrics, and sharp kinetic typography.

3. Script Timeline Synchronization:
   - Clean scene switching based on the exact script timestamps provided below.
   - Make transitions dynamic.

4. Constraints:
   - Do NOT use network requests, moviepy, Pygame, or external assets (except default fonts).
   - Output ONLY the raw Python code block. NO markdown formatting around the code if possible, but if you do, use ```python.
   - The code MUST execute from top to bottom, generate the frames, and save using `imageio.get_writer`.
   
Available global variables injected into your namespace:
- `output_mp4_path`: String path where you must save the MP4 (value: '{output_mp4}')
- `duration`: Float ({duration})
- `w`, `h`: Int ({w}, {h})
- `fps`: Int ({fps})
- `total_frames`: Int ({total_frames})
- `Image`, `ImageDraw`, `ImageFilter`, `ImageFont`, `np`, `imageio`, `math`, `random`

Here is the {duration}-second script to animate:
{user_prompt}
"""

    max_retries = 3
    generated_code = ""
    used_model = None

    for attempt in range(max_retries):
        print(f"   🤖 Calling Gemini API for Python Code (attempt {attempt+1}/{max_retries})...")
        models_to_try = ['gemini-3.8-flash', 'gemini-3.6-flash', 'gemini-flash-latest', 'gemini-3.5-flash', 'gemini-3.1-pro-preview']
        for m_name in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": system_instruction}]}]}
                r_rest = requests.post(url, json=payload, timeout=120.0)
                if r_rest.status_code == 200:
                    r_data = r_rest.json()
                    candidates = r_data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            generated_code = parts[0].get("text", "")
                            if generated_code: 
                                used_model = m_name
                                break
                else:
                    print(f"      ⚠️ Model {m_name} failed (HTTP {r_rest.status_code}) - skipping...")
            except Exception as e:
                print(f"      ⚠️ Model {m_name} exception: {e} - skipping...")
                
        if generated_code:
            print(f"   ✅ Gemini API returned Python Code ({len(generated_code)} chars) using model: {used_model}")
            break
        else:
            print(f"⚠️ All Gemini models failed on attempt {attempt+1}. Sleeping 2s before retry...")
            time.sleep(2)

    if not generated_code:
        print("⚠️ Gemini API offline or 503. Python Generation Failed.")
        return create_emergency_world_news_mp4(user_prompt, output_mp4, duration, target_size, fps)

    clean_code = re.sub(r"^```python\n?", "", generated_code, flags=re.MULTILINE)
    clean_code = re.sub(r"^```\n?", "", clean_code, flags=re.MULTILINE)
    clean_code = clean_code.strip()

    exec_globals = {
        "Image": Image,
        "ImageDraw": SafeImageDrawModule(ImageDraw),
        "ImageFilter": ImageFilter,
        "ImageFont": ImageFont,
        "math": math,
        "random": random,
        "sys": sys,
        "time": time,
        "re": re,
        "colorsys": colorsys,
        "copy": copy,
        "imageio": imageio,
        "np": np,
        "os": os,
        "output_mp4_path": output_mp4,
        "duration": duration,
        "w": w,
        "h": h,
        "fps": fps,
        "total_frames": total_frames
    }

    try:
        print(f"   ⚙️ Executing Gemini generated Python World News animation code...")
        exec(clean_code, exec_globals)
        if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1000:
            print(f"🎉 [World News Python Engine] Successfully rendered AI MP4: {output_mp4}")
            return output_mp4
        else:
            print(f"⚠️ [World News Python Engine] Output MP4 missing. Running emergency fallback...")
            return create_emergency_world_news_mp4(user_prompt, output_mp4, duration, target_size, fps)
    except Exception as exec_err:
        print(f"❌ [World News Python Engine] Code Execution Error: {exec_err}")
        traceback.print_exc()
        return create_emergency_world_news_mp4(user_prompt, output_mp4, duration, target_size, fps)

if __name__ == "__main__":
    pass
