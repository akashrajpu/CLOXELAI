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

    def _normalize_box(self, xy):
        if isinstance(xy, (tuple, list)):
            flat = []
            for item in xy:
                if isinstance(item, (tuple, list)):
                    flat.extend(item)
                elif isinstance(item, (int, float)):
                    flat.append(int(item))
                else:
                    try:
                        flat.append(int(item))
                    except Exception:
                        pass
            if len(flat) == 2:
                x, y = flat
                return [(x - 10, y - 10), (x + 10, y + 10)]
            elif len(flat) == 3:
                x, y, r = flat
                return [(x - r, y - r), (x + r, y + r)]
            elif len(flat) >= 4:
                return [(flat[0], flat[1]), (flat[2], flat[3])]
        return xy

    def _normalize_points(self, xy):
        if isinstance(xy, (tuple, list)):
            flat = []
            for item in xy:
                if isinstance(item, (tuple, list)):
                    flat.extend(item)
                elif isinstance(item, (int, float)):
                    flat.append(int(item))
                else:
                    try:
                        flat.append(int(item))
                    except Exception:
                        pass
            if len(flat) >= 4:
                return [(flat[i], flat[i+1]) for i in range(0, len(flat)-1, 2)]
            elif len(flat) == 2:
                x, y = flat
                return [(x, y), (x + 10, y + 10)]
        return xy

    def _extract_target_and_args(self, args):
        if not args:
            return self._draw, []
        first = args[0]
        if hasattr(first, '_draw'):
            return first._draw, list(args[1:])
        elif hasattr(first, 'line') or hasattr(first, 'im'):
            return first, list(args[1:])
        return self._draw, list(args)

    def line(self, *args, **kwargs):
        draw_obj, rem_args = self._extract_target_and_args(args)
        if not rem_args:
            return None
        xy = rem_args[0]
        pts = self._normalize_points(xy)
        
        fill = kwargs.get('fill')
        if fill is None and len(rem_args) > 1:
            fill = rem_args[1]
        if fill is None:
            fill = (255, 255, 255)

        width = kwargs.get('width')
        if width is None and len(rem_args) > 2 and isinstance(rem_args[2], (int, float)):
            width = rem_args[2]
        if width is None:
            width = 1

        try:
            return draw_obj.line(pts, fill=fill, width=int(width))
        except Exception:
            try:
                return draw_obj.line(pts, fill=(255, 255, 255), width=1)
            except Exception:
                pass

    def draw_line(self, *args, **kwargs):
        return self.line(*args, **kwargs)

    def rectangle(self, *args, **kwargs):
        draw_obj, rem_args = self._extract_target_and_args(args)
        if not rem_args:
            return None
        xy = rem_args[0]
        box = self._normalize_box(xy)

        fill = kwargs.get('fill')
        if fill is None and len(rem_args) > 1:
            fill = rem_args[1]

        outline = kwargs.get('outline')
        if outline is None and len(rem_args) > 2:
            outline = rem_args[2]

        width = kwargs.get('width', 1)

        try:
            return draw_obj.rectangle(box, fill=fill, outline=outline, width=int(width))
        except Exception:
            try:
                return draw_obj.rectangle(box, fill=(100, 100, 100))
            except Exception:
                pass

    def draw_rectangle(self, *args, **kwargs):
        return self.rectangle(*args, **kwargs)

    def ellipse(self, *args, **kwargs):
        draw_obj, rem_args = self._extract_target_and_args(args)
        if not rem_args:
            return None
        xy = rem_args[0]
        box = self._normalize_box(xy)

        fill = kwargs.get('fill')
        if fill is None and len(rem_args) > 1:
            fill = rem_args[1]

        outline = kwargs.get('outline')
        if outline is None and len(rem_args) > 2:
            outline = rem_args[2]

        width = kwargs.get('width', 1)

        try:
            return draw_obj.ellipse(box, fill=fill, outline=outline, width=int(width))
        except Exception:
            try:
                return draw_obj.ellipse(box, fill=(200, 200, 200))
            except Exception:
                pass

    def draw_ellipse(self, *args, **kwargs):
        return self.ellipse(*args, **kwargs)

    def polygon(self, *args, **kwargs):
        draw_obj, rem_args = self._extract_target_and_args(args)
        if not rem_args:
            return None
        xy = rem_args[0]
        pts = self._normalize_points(xy)

        fill = kwargs.get('fill')
        if fill is None and len(rem_args) > 1:
            fill = rem_args[1]

        outline = kwargs.get('outline')
        if outline is None and len(rem_args) > 2:
            outline = rem_args[2]

        try:
            return draw_obj.polygon(pts, fill=fill, outline=outline)
        except Exception:
            try:
                return draw_obj.polygon(pts, fill=(150, 150, 150))
            except Exception:
                pass

    def draw_polygon(self, *args, **kwargs):
        return self.polygon(*args, **kwargs)

    def text(self, *args, **kwargs):
        draw_obj, rem_args = self._extract_target_and_args(args)
        if not rem_args:
            return None
        xy = rem_args[0]
        pts = self._normalize_points(xy)
        pos = pts[0] if isinstance(pts, (list, tuple)) and len(pts) > 0 else (20, 20)

        text_val = kwargs.get('text', "")
        if not text_val and len(rem_args) > 1:
            text_val = rem_args[1]

        fill = kwargs.get('fill')
        if fill is None and len(rem_args) > 2:
            fill = rem_args[2]
        if fill is None:
            fill = (255, 255, 255)

        font = kwargs.get('font')

        try:
            if font:
                return draw_obj.text(pos, str(text_val), fill=fill, font=font)
            return draw_obj.text(pos, str(text_val), fill=fill)
        except Exception:
            try:
                return draw_obj.text((20, 20), str(text_val), fill=(255, 255, 255))
            except Exception:
                pass

    def draw_text(self, *args, **kwargs):
        return self.text(*args, **kwargs)

    def arc(self, *args, **kwargs):
        draw_obj, rem_args = self._extract_target_and_args(args)
        if not rem_args:
            return None
        xy = rem_args[0]
        box = self._normalize_box(xy)
        start = kwargs.get('start', rem_args[1] if len(rem_args) > 1 else 0)
        end = kwargs.get('end', rem_args[2] if len(rem_args) > 2 else 360)
        fill = kwargs.get('fill', rem_args[3] if len(rem_args) > 3 else (255, 255, 255))
        try:
            return draw_obj.arc(box, int(start), int(end), fill=fill)
        except Exception:
            pass

    def draw_arc(self, *args, **kwargs):
        return self.arc(*args, **kwargs)

    def chord(self, *args, **kwargs):
        draw_obj, rem_args = self._extract_target_and_args(args)
        if not rem_args:
            return None
        xy = rem_args[0]
        box = self._normalize_box(xy)
        start = kwargs.get('start', rem_args[1] if len(rem_args) > 1 else 0)
        end = kwargs.get('end', rem_args[2] if len(rem_args) > 2 else 360)
        fill = kwargs.get('fill', rem_args[3] if len(rem_args) > 3 else (255, 255, 255))
        try:
            return draw_obj.chord(box, int(start), int(end), fill=fill)
        except Exception:
            pass

    def draw_chord(self, *args, **kwargs):
        return self.chord(*args, **kwargs)

    def pieslice(self, *args, **kwargs):
        draw_obj, rem_args = self._extract_target_and_args(args)
        if not rem_args:
            return None
        xy = rem_args[0]
        box = self._normalize_box(xy)
        start = kwargs.get('start', rem_args[1] if len(rem_args) > 1 else 0)
        end = kwargs.get('end', rem_args[2] if len(rem_args) > 2 else 360)
        fill = kwargs.get('fill', rem_args[3] if len(rem_args) > 3 else (255, 255, 255))
        try:
            return draw_obj.pieslice(box, int(start), int(end), fill=fill)
        except Exception:
            pass

    def draw_pieslice(self, *args, **kwargs):
        return self.pieslice(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._draw, name)


class SafeImageDrawModule:
    def __init__(self, original_mod):
        self._mod = original_mod

    def Draw(self, im, mode=None):
        raw_draw = self._mod.Draw(im, mode=mode)
        return SafeImageDraw(raw_draw)

    def _delegate_draw_call(self, method_name, args, kwargs):
        if args and (hasattr(args[0], '_draw') or hasattr(args[0], 'im') or hasattr(args[0], 'line')):
            d = args[0]
            if isinstance(d, SafeImageDraw):
                return getattr(d, method_name)(*args[1:], **kwargs)
            else:
                return getattr(SafeImageDraw(d), method_name)(*args[1:], **kwargs)
        return None

    def line(self, *args, **kwargs):
        return self._delegate_draw_call("line", args, kwargs)

    def draw_line(self, *args, **kwargs):
        return self.line(*args, **kwargs)

    def rectangle(self, *args, **kwargs):
        return self._delegate_draw_call("rectangle", args, kwargs)

    def draw_rectangle(self, *args, **kwargs):
        return self.rectangle(*args, **kwargs)

    def ellipse(self, *args, **kwargs):
        return self._delegate_draw_call("ellipse", args, kwargs)

    def draw_ellipse(self, *args, **kwargs):
        return self.ellipse(*args, **kwargs)

    def polygon(self, *args, **kwargs):
        return self._delegate_draw_call("polygon", args, kwargs)

    def draw_polygon(self, *args, **kwargs):
        return self.polygon(*args, **kwargs)

    def text(self, *args, **kwargs):
        return self._delegate_draw_call("text", args, kwargs)

    def draw_text(self, *args, **kwargs):
        return self.text(*args, **kwargs)

    def arc(self, *args, **kwargs):
        return self._delegate_draw_call("arc", args, kwargs)

    def draw_arc(self, *args, **kwargs):
        return self.arc(*args, **kwargs)

    def chord(self, *args, **kwargs):
        return self._delegate_draw_call("chord", args, kwargs)

    def draw_chord(self, *args, **kwargs):
        return self.chord(*args, **kwargs)

    def pieslice(self, *args, **kwargs):
        return self._delegate_draw_call("pieslice", args, kwargs)

    def draw_pieslice(self, *args, **kwargs):
        return self.pieslice(*args, **kwargs)

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

    if target_size and len(target_size) == 2:
        if target_size[1] > target_size[0]:
            w, h = (360, 640)
        else:
            w, h = (640, 360)
    else:
        w, h = (640, 360)

    total_frames = max(15, int(duration * fps))
    aspect_desc = "Vertical Shorts (9:16 aspect ratio)" if h > w else "Horizontal Video (16:9 aspect ratio)"

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
       
    4. SIZE & FRAMES: Canvas size MUST be {w}x{h} ({aspect_desc}). Generate {total_frames} frames depending on the story length.
    
    5. VERY IMPORTANT MATH & DRAW RULE:
       - All coordinates (x, y) passed to ImageDraw functions MUST be integers using int(). No floats.
       - DO NOT pass both positional color and fill= keyword argument to draw functions! Use draw.line(xy, fill=color, width=2) or draw.rectangle(box, fill=color).
    
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
                    from google import genai
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=m_name,
                        contents=system_instruction,
                    )
                    generated_code = response.text
                    if generated_code: break
                except Exception:
                    try:
                        import google.generativeai as legacy_genai
                        legacy_genai.configure(api_key=api_key)
                        g_model = legacy_genai.GenerativeModel(m_name)
                        res_legacy = g_model.generate_content(system_instruction)
                        generated_code = res_legacy.text
                        if generated_code: break
                    except Exception:
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
            else:
                import time
                print(f"⚠️ Gemini API failed to return code. Sleeping before next attempt...")
                time.sleep(3)
        except Exception as api_err:
            print(f"⚠️ Gemini Animation API attempt {attempt+1}/{max_retries} warning: {api_err}")
            if "503" in str(api_err) or "429" in str(api_err):
                time.sleep(2)
            else:
                break

    if not generated_code:
        print("⚠️ Gemini API offline or 503. Triggering guaranteed local 2D Cartoon Canvas Renderer...")
        return create_pro_cartoon_canvas_mp4(user_prompt, output_mp4, duration, target_size, fps)

    clean_code = re.sub(r"^```python\n?", "", generated_code, flags=re.MULTILINE)
    clean_code = re.sub(r"^```\n?", "", clean_code, flags=re.MULTILINE)
    clean_code = clean_code.strip()

    import random, sys, colorsys, copy
    exec_globals = {
        "Image": Image,
        "ImageDraw": SafeImageDrawModule(ImageDraw),
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


def render_pil_frames_to_mp4(frames: list, output_mp4: str, w: int, h: int, fps: int = 15) -> bool:
    """Pipes PIL Image frames directly into FFmpeg rawvideo stdin to guarantee zero-dependency MP4 creation."""
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{w}x{h}",
            "-pix_fmt", "rgb24",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_mp4
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for img in frames:
            proc.stdin.write(img.convert("RGB").tobytes())
        proc.stdin.close()
        proc.wait()
        return os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1000
    except Exception as e_pipe:
        print(f"⚠️ FFmpeg rawvideo pipe error: {e_pipe}")
        return False


def create_pro_cartoon_canvas_mp4(user_prompt: str, output_mp4: str, duration: float = 5.0, target_size: tuple = (640, 360), fps: int = 15) -> str:
    """
    Guaranteed Local 2D Cartoon Animation Generator:
    Generates a 2D animated cartoon scene with smooth character motions, speech bubbles,
    and vibrant cartoon backgrounds when Gemini AI is offline or 503.
    Ultra-low RAM memory footprint (< 50MB RAM).
    """
    if target_size and len(target_size) == 2:
        if target_size[1] > target_size[0]:
            w, h = (360, 640)
        else:
            w, h = (640, 360)
    else:
        w, h = (640, 360)

    total_frames = max(15, int(duration * fps))

    prompt_lower = user_prompt.lower()
    is_night = any(k in prompt_lower for k in ["night", "space", "moon", "star", "dark"])
    bg_top = (15, 15, 45) if is_night else (100, 180, 255)

    writer = None
    try:
        writer = imageio.get_writer(output_mp4, fps=fps, macro_block_size=1)
    except Exception:
        writer = None

    frames_fallback = [] if writer is None else None

    for frame_idx in range(total_frames):
        img = Image.new('RGB', (w, h), bg_top)
        draw = ImageDraw.Draw(img)

        # Draw Ground / Hill
        ground_y = int(h * 0.7)
        draw.rectangle([(0, ground_y), (w, h)], fill=(40, 160, 80) if not is_night else (20, 50, 40))

        # Animated Sun/Moon
        sun_x = int(w * 0.8 - (frame_idx / float(total_frames)) * (w * 0.4))
        sun_y = int(h * 0.2)
        draw.ellipse([(sun_x - 30, sun_y - 30), (sun_x + 30, sun_y + 30)], fill=(255, 220, 50) if not is_night else (220, 230, 255))

        # Animated Character 1 (Walking Boy/Hero)
        char1_x = int(w * 0.1 + (frame_idx / float(total_frames)) * (w * 0.35))
        char1_y = int(ground_y - 110)
        leg_bounce = int(math.sin(frame_idx * 0.5) * 8)

        # Head
        draw.ellipse([(char1_x, char1_y), (char1_x + 45, char1_y + 45)], fill=(255, 205, 148), outline=(0, 0, 0), width=3)
        # Eyes & Smile
        draw.ellipse([(char1_x + 28, char1_y + 14), (char1_x + 34, char1_y + 22)], fill=(0, 0, 0))
        draw.arc([(char1_x + 18, char1_y + 22), (char1_x + 35, char1_y + 35)], start=0, end=180, fill=(200, 0, 0), width=3)
        # Body (Shirt)
        draw.rectangle([(char1_x + 8, char1_y + 45), (char1_x + 37, char1_y + 90)], fill=(255, 80, 80), outline=(0, 0, 0), width=3)
        # Legs
        draw.line([(char1_x + 15, char1_y + 90), (char1_x + 8 + leg_bounce, char1_y + 115)], fill=(30, 30, 150), width=5)
        draw.line([(char1_x + 30, char1_y + 90), (char1_x + 37 - leg_bounce, char1_y + 115)], fill=(30, 30, 150), width=5)

        # Animated Character 2 (Cute Puppy / Friend)
        char2_x = min(int(w - 75), char1_x + int(w * 0.25) + int(math.sin(frame_idx * 0.3) * 10))
        char2_y = ground_y - 50
        # Body
        draw.ellipse([(char2_x, char2_y), (char2_x + 50, char2_y + 35)], fill=(210, 140, 70), outline=(0, 0, 0), width=3)
        # Head
        draw.ellipse([(char2_x - 12, char2_y - 15), (char2_x + 20, char2_y + 15)], fill=(210, 140, 70), outline=(0, 0, 0), width=3)
        # Ear
        draw.ellipse([(char2_x - 8, char2_y - 20), (char2_x + 4, char2_y - 4)], fill=(120, 70, 30))
        # Tail (Wagging)
        tail_swing = int(math.sin(frame_idx * 0.8) * 10)
        draw.line([(char2_x + 45, char2_y + 8), (char2_x + 60, char2_y - 8 + tail_swing)], fill=(210, 140, 70), width=4)

        # Speech Bubble
        bubble_x = max(5, char1_x - 15)
        bubble_y = max(5, char1_y - 55)
        bubble_w = min(150, w - bubble_x - 5)
        draw.ellipse([(bubble_x, bubble_y), (bubble_x + bubble_w, bubble_y + 40)], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        
        try:
            fnt = ImageFont.truetype("./fonts/Arial.ttf", 14)
        except Exception:
            fnt = ImageFont.load_default()
        short_text = user_prompt[:18] + "..." if len(user_prompt) > 18 else user_prompt
        draw.text((bubble_x + 10, bubble_y + 10), short_text, fill=(0, 0, 0), font=fnt)

        if writer:
            try:
                writer.append_data(np.array(img.convert('RGB')))
            except Exception:
                pass
            del img, draw
            if frame_idx % 15 == 0:
                gc.collect()
        else:
            frames_fallback.append(img)

    if writer:
        try:
            writer.close()
        except Exception:
            pass
        gc.collect()

    if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1000:
        print(f"🎨 [Local 2D Cartoon Engine] Successfully rendered 2D Cartoon MP4 via ImageIO: {output_mp4}")
        return output_mp4

    if frames_fallback:
        print("🎨 Rendering 2D Cartoon Canvas MP4 via FFmpeg rawvideo pipe...")
        if render_pil_frames_to_mp4(frames_fallback, output_mp4, w, h, fps):
            print(f"🎨 [FFmpeg Raw Pipe Canvas] Created valid 2D cartoon animation MP4: {output_mp4}")
            return output_mp4

    try:
        dur_str = str(max(2.0, duration))
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c=0x64b4ff:s={w}x{h}:r={fps}",
            "-vf", "drawtext=text='2D Cartoon Scene':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2",
            "-t", dur_str, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_mp4
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_mp4
    except Exception as e_ff:
        print(f"❌ Ultimate Canvas Fallback Failed: {e_ff}")

    return output_mp4
