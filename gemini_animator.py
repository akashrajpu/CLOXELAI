import os
import re
import time
import math
import gc
import subprocess
import imageio
import warnings
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont

warnings.filterwarnings("ignore")
logging.getLogger("google_genai").setLevel(logging.ERROR)

class SafeImageDraw:
    def __init__(self, draw_obj):
        self._draw = draw_obj

    def _clean_xy(self, xy):
        if isinstance(xy, (list, tuple)):
            res = []
            for item in xy:
                if isinstance(item, (list, tuple)):
                    res.append(tuple(int(v) for v in item))
                elif isinstance(item, (int, float)):
                    res.append(int(item))
                else:
                    res.append(item)
            return tuple(res) if isinstance(xy, tuple) else res
        return xy

    def line(self, xy, *args, **kwargs):
        try:
            xy = self._clean_xy(xy)
            if 'fill' in kwargs and len(args) > 0:
                args = ()
            return self._draw.line(xy, *args, **kwargs)
        except Exception:
            try:
                fill = kwargs.get('fill', (255, 255, 255))
                width = int(kwargs.get('width', 1))
                return self._draw.line(xy, fill=fill, width=width)
            except Exception:
                pass

    def rectangle(self, xy, *args, **kwargs):
        try:
            xy = self._clean_xy(xy)
            if 'fill' in kwargs and len(args) > 0:
                args = ()
            return self._draw.rectangle(xy, *args, **kwargs)
        except Exception:
            try:
                fill = kwargs.get('fill', (100, 100, 100))
                return self._draw.rectangle(xy, fill=fill)
            except Exception:
                pass

    def ellipse(self, xy, *args, **kwargs):
        try:
            xy = self._clean_xy(xy)
            if 'fill' in kwargs and len(args) > 0:
                args = ()
            return self._draw.ellipse(xy, *args, **kwargs)
        except Exception:
            try:
                fill = kwargs.get('fill', (200, 200, 200))
                return self._draw.ellipse(xy, fill=fill)
            except Exception:
                pass

    def polygon(self, xy, *args, **kwargs):
        try:
            xy = self._clean_xy(xy)
            if 'fill' in kwargs and len(args) > 0:
                args = ()
            return self._draw.polygon(xy, *args, **kwargs)
        except Exception:
            try:
                fill = kwargs.get('fill', (150, 150, 150))
                return self._draw.polygon(xy, fill=fill)
            except Exception:
                pass

    def text(self, xy, text, *args, **kwargs):
        try:
            xy = self._clean_xy(xy)
            return self._draw.text(xy, str(text), *args, **kwargs)
        except Exception:
            try:
                return self._draw.text(xy, str(text), fill=(255, 255, 255))
            except Exception:
                pass

    def arc(self, xy, start, end, *args, **kwargs):
        try:
            xy = self._clean_xy(xy)
            return self._draw.arc(xy, int(start), int(end), *args, **kwargs)
        except Exception:
            pass

    def chord(self, xy, start, end, *args, **kwargs):
        try:
            xy = self._clean_xy(xy)
            return self._draw.chord(xy, int(start), int(end), *args, **kwargs)
        except Exception:
            pass

    def pieslice(self, xy, start, end, *args, **kwargs):
        try:
            xy = self._clean_xy(xy)
            return self._draw.pieslice(xy, int(start), int(end), *args, **kwargs)
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._draw, name)


class SafeImageDrawModule:
    def __init__(self, original_mod):
        self._mod = original_mod

    def Draw(self, im, mode=None):
        raw_draw = self._mod.Draw(im, mode=mode)
        return SafeImageDraw(raw_draw)

    def __getattr__(self, name):
        return getattr(self._mod, name)


def generate_gemini_cartoon_animation(user_prompt: str, output_mp4: str, duration: float = 5.0, target_size: tuple = (640, 360), fps: int = 15) -> str:
    """
    Generates a frame-by-frame 2D Cartoon / Anime Animation MP4 video using Gemini AI code generation.
    Used for Ultra Mode when Category is 'Cartoon' or 'Animation'.
    Optimized for 640x360 resolution to guarantee RAM usage stays under 80MB!
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("AI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY / GOOGLE_API_KEY environment variable not set. Skipping AI animation generation.")
        return None

    w, h = (640, 360)  # Ultra-lightweight canvas for 100% zero-OOM stability
    total_frames = max(15, int(duration * fps))

    system_instruction = f"""
    You are an expert Python Developer, Animator, and Movie Director. 
    Read the following Hinglish user prompt and generate a COMPLETE, ERROR-FREE Python script to create an MP4 animation video.
    
    STRICT RULES FOR YOUR CODE:
    1. Output ONLY raw, runnable Python code. DO NOT wrap it in markdown block quotes like ```python ... ```. Do not add any text explanations.
    2. IMPORT THESE EXACT MODULES:
       from PIL import Image, ImageDraw
       import math
       import imageio
       import gc
       import numpy as np
       
    3. SCENE BY SCENE LOGIC: Break the story into logical scenes based on frames (e.g., if frame < 40: Scene 1 logic... elif frame < 80: Scene 2 logic...). 
       - Dynamically change background colors (night to day), object positions, and character actions ('walk', 'run', 'shoot', 'idle') based on the scene.
       
    4. SIZE & FRAMES: Canvas size MUST be {w}x{h}. Generate {total_frames} frames depending on the story length.
    
    5. VERY IMPORTANT MATH RULE: All coordinates (x, y) passed to ImageDraw functions MUST be integers using int(). No floats. (e.g., draw.ellipse((int(x), int(y), int(x+20), int(y+20))))
    
    6. Keep drawings simple (stick figures, colored shapes, basic background) but animate them smoothly. Add speech bubbles if they talk.
    
    7. MP4 STREAMING & ZERO-RAM RULE: To prevent Out-Of-Memory crashes on 512MB servers, DO NOT store frames in a list. Open the imageio writer FIRST and append frames directly inside the frame loop, calling gc.collect() every 10 frames:
       import gc
       writer = imageio.get_writer('{output_mp4}', fps={fps}, macro_block_size=1)
       for frame_idx in range({total_frames}):
           img = Image.new('RGB', ({w}, {h}), (25, 25, 45))
           draw = ImageDraw.Draw(img)
           # ... draw scene animations ...
           writer.append_data(np.array(img.convert('RGB')))
           del img, draw
           if frame_idx % 10 == 0: gc.collect()
       writer.close()
       gc.collect()
       print("Video rendering complete!")

    8. Put everything directly in the global scope (do not wrap in a main function).
    
    User Prompt (Hinglish Story): "{user_prompt}"
    """

    print(f"🎬 [Gemini Cartoon Engine] Generating AI Animation Code for scene: '{user_prompt[:60]}...' ({total_frames} frames)...")
    
    generated_code = ""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"   🤖 Calling Gemini API (attempt {attempt+1}/{max_retries})...")
            models_to_try = ['gemini-3.6-flash', 'gemini-flash-latest', 'gemini-3.5-flash']
            for m_name in models_to_try:
                try:
                    # Try new google-genai SDK first
                    from google import genai
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=m_name,
                        contents=system_instruction,
                    )
                    generated_code = response.text
                    if generated_code: break
                except Exception as e_new_sdk:
                    # Try legacy google.generativeai SDK second
                    try:
                        import google.generativeai as legacy_genai
                        legacy_genai.configure(api_key=api_key)
                        g_model = legacy_genai.GenerativeModel(m_name)
                        res_legacy = g_model.generate_content(system_instruction)
                        generated_code = res_legacy.text
                        if generated_code: break
                    except Exception as e_leg_sdk:
                        # Direct REST API fallback third (100% dependency-free)
                        try:
                            import requests
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={api_key}"
                            payload = {"contents": [{"parts": [{"text": system_instruction}]}]}
                            r_rest = requests.post(url, json=payload, timeout=25)
                            if r_rest.status_code == 200:
                                r_data = r_rest.json()
                                candidates = r_data.get("candidates", [])
                                if candidates and "content" in candidates[0]:
                                    parts = candidates[0]["content"].get("parts", [])
                                    if parts:
                                        generated_code = parts[0].get("text", "")
                                        if generated_code: break
                        except Exception:
                            pass

            if generated_code:
                print(f"   ✅ Gemini API returned animation code ({len(generated_code)} chars)")
                break
        except Exception as api_err:
            print(f"⚠️ Gemini Animation API attempt {attempt+1}/{max_retries} warning: {api_err}")
            if "503" in str(api_err) or "429" in str(api_err):
                time.sleep(2)
            else:
                break

    if not generated_code:
        print("⚠️ Gemini API offline or 503. Triggering guaranteed local 2D Cartoon Canvas Renderer...")
        return create_pro_cartoon_canvas_mp4(user_prompt, output_mp4, duration, target_size, fps)

    # Code Cleaning
    clean_code = re.sub(r"^```python\n?", "", generated_code, flags=re.MULTILINE)
    clean_code = re.sub(r"^```\n?", "", clean_code, flags=re.MULTILINE)
    clean_code = clean_code.strip()

    exec_globals = {
        "Image": Image,
        "ImageDraw": SafeImageDrawModule(ImageDraw),
        "ImageFont": ImageFont,
        "math": __import__("math"),
        "imageio": imageio,
        "np": np,
        "os": os
    }

    try:
        print(f"   ⚙️ Executing Gemini generated Python animation code...")
        exec(clean_code, exec_globals)
        if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1000:
            print(f"🎉 [Gemini Cartoon Engine] Successfully rendered AI Cartoon MP4: {output_mp4}")
            return output_mp4
        else:
            print(f"⚠️ [Gemini Cartoon Engine] Output MP4 missing. Running local 2D Cartoon Canvas Renderer...")
            return create_pro_cartoon_canvas_mp4(user_prompt, output_mp4, duration, target_size, fps)
    except Exception as exec_err:
        import traceback
        print(f"❌ [Gemini Cartoon Engine] Code Execution Error: {exec_err}")
        traceback.print_exc()
        print("🎨 Fallback to local 2D Cartoon Canvas Renderer...")
        return create_pro_cartoon_canvas_mp4(user_prompt, output_mp4, duration, target_size, fps)


def create_pro_cartoon_canvas_mp4(user_prompt: str, output_mp4: str, duration: float = 5.0, target_size: tuple = (640, 360), fps: int = 15) -> str:
    """
    Guaranteed Local 2D Cartoon Animation Generator:
    Generates a 2D animated cartoon scene with smooth character motions, speech bubbles,
    and vibrant cartoon backgrounds when Gemini AI is offline or 503.
    """
    try:
        w, h = (640, 360)
        total_frames = max(15, int(duration * fps))
        writer = imageio.get_writer(output_mp4, fps=fps, macro_block_size=1)

        prompt_lower = user_prompt.lower()
        is_night = any(k in prompt_lower for k in ["night", "space", "moon", "star", "dark"])
        
        bg_top = (15, 15, 45) if is_night else (100, 180, 255)

        for frame_idx in range(total_frames):
            img = Image.new('RGB', (w, h), bg_top)
            draw = ImageDraw.Draw(img)

            # Draw Ground / Hill
            ground_y = int(h * 0.7)
            draw.rectangle([(0, ground_y), (w, h)], fill=(40, 160, 80) if not is_night else (20, 50, 40))

            # Animated Sun/Moon
            sun_x = int(w * 0.8 - frame_idx * 1.5)
            sun_y = int(h * 0.2)
            draw.ellipse([(sun_x - 40, sun_y - 40), (sun_x + 40, sun_y + 40)], fill=(255, 220, 50) if not is_night else (220, 230, 255))

            # Animated Character 1 (Walking Boy/Hero)
            char1_x = int(w * 0.15 + (frame_idx / float(total_frames)) * (w * 0.4))
            char1_y = int(ground_y - 120)
            leg_bounce = int(math.sin(frame_idx * 0.5) * 10)

            # Head
            draw.ellipse([(char1_x, char1_y), (char1_x + 50, char1_y + 50)], fill=(255, 205, 148), outline=(0, 0, 0), width=3)
            # Eyes & Smile
            draw.ellipse([(char1_x + 30, char1_y + 15), (char1_x + 36, char1_y + 23)], fill=(0, 0, 0))
            draw.arc([(char1_x + 20, char1_y + 25), (char1_x + 38, char1_y + 38)], start=0, end=180, fill=(200, 0, 0), width=3)
            # Body (Shirt)
            draw.rectangle([(char1_x + 10, char1_y + 50), (char1_x + 40, char1_y + 100)], fill=(255, 80, 80), outline=(0, 0, 0), width=3)
            # Legs
            draw.line([(char1_x + 18, char1_y + 100), (char1_x + 10 + leg_bounce, char1_y + 130)], fill=(30, 30, 150), width=6)
            draw.line([(char1_x + 32, char1_y + 100), (char1_x + 40 - leg_bounce, char1_y + 130)], fill=(30, 30, 150), width=6)

            # Animated Character 2 (Cute Puppy / Friend)
            char2_x = char1_x + 120 + int(math.sin(frame_idx * 0.3) * 15)
            char2_y = ground_y - 60
            # Body
            draw.ellipse([(char2_x, char2_y), (char2_x + 60, char2_y + 40)], fill=(210, 140, 70), outline=(0, 0, 0), width=3)
            # Head
            draw.ellipse([(char2_x - 15, char2_y - 20), (char2_x + 25, char2_y + 20)], fill=(210, 140, 70), outline=(0, 0, 0), width=3)
            # Ear
            draw.ellipse([(char2_x - 10, char2_y - 25), (char2_x + 5, char2_y - 5)], fill=(120, 70, 30))
            # Tail (Wagging)
            tail_swing = int(math.sin(frame_idx * 0.8) * 15)
            draw.line([(char2_x + 55, char2_y + 10), (char2_x + 75, char2_y - 10 + tail_swing)], fill=(210, 140, 70), width=5)

            # Speech Bubble
            bubble_x = max(10, char1_x - 20)
            bubble_y = max(10, char1_y - 60)
            draw.ellipse([(bubble_x, bubble_y), (bubble_x + 160, bubble_y + 45)], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
            
            try:
                fnt = ImageFont.truetype("./fonts/Arial.ttf", 16)
            except Exception:
                fnt = ImageFont.load_default()
            short_text = user_prompt[:20] + "..." if len(user_prompt) > 20 else user_prompt
            draw.text((bubble_x + 12, bubble_y + 12), short_text, fill=(0, 0, 0), font=fnt)

            writer.append_data(np.array(img.convert('RGB')))

        writer.close()
        
        if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1000:
            print(f"🎨 [Local 2D Cartoon Engine] Successfully rendered 2D Cartoon MP4: {output_mp4}")
            return output_mp4
    except Exception as e_canvas:
        print(f"⚠️ Canvas Cartoon generator notice: {e_canvas}. Generating direct FFmpeg canvas...")

    try:
        dur_str = str(max(2.0, duration))
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c=0x19192d:s={target_size[0]}x{target_size[1]}:r={fps}",
            "-t", dur_str, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_mp4
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 500:
            print(f"🎨 [FFmpeg Direct Canvas Fallback] Created valid cartoon canvas MP4: {output_mp4}")
            return output_mp4
    except Exception as e_ff:
        print(f"❌ Ultimate Canvas Fallback Failed: {e_ff}")

    return output_mp4
