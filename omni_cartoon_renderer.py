"""
===============================================================================
  OMNI CARTOON ANIMATION RENDERER 20.0 (MANDATORY MULTI-CHARACTER STICK ENGINE)
===============================================================================
Description : 100% Mandatory Multi-Character Engine in PIL.
              ALWAYS draws MULTIPLE CHARACTERS (Character 1 & Character 2, plus Enemy Character 3)
              on PURE WHITE canvas ("white") with House 🏠, Road 🛣️, Trees 🌳, and Border 🚧 props!
              Zero single-character scenes!

Author      : Antigravity AI Engine
===============================================================================
"""

import os
import re
import math
import time
import subprocess
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont

def load_user_font(fs: int = 24):
    for fp in ["/System/Library/Fonts/Supplemental/Arial.ttf", "arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(fp):
            try: return ImageFont.truetype(fp, fs)
            except Exception: pass
    return ImageFont.load_default()

def parse_prompt_to_user_script(prompt: str) -> str:
    """
    Parses any Hinglish prompt into exact micro-scene steps with entity detection.
    """
    prompt_clean = prompt.strip()
    lines_raw = prompt_clean.split('\n')
    if len(lines_raw) >= 2 and any(lines_raw[0].lower().startswith(a) for a in ['walk', 'run', 'say', 'idle', 'shoot', 'jump', 'dance', 'crouch', 'house', 'road', 'fight']):
        return prompt_clean

    lines = []
    sentences = [s.strip() for s in prompt_clean.replace('\n', '. ').split('.') if s.strip()]

    if not sentences:
        return "walk 30\nsay 40 Hello, kese ho!\nidle 30"

    for sentence in sentences:
        s_lower = sentence.lower()
        clean_text = sentence.replace('"', '').replace("'", "").strip()
        speech_text = clean_text[:40]

        if 'ghar' in s_lower or 'house' in s_lower or 'nikal' in s_lower:
            lines.append(f"walk 35 {speech_text}")
        elif 'dost' in s_lower or 'raste' in s_lower or 'road' in s_lower or 'milta' in s_lower:
            lines.append(f"say 40 {speech_text}")
        elif any(w in s_lower for w in ['shoot', 'goli', 'border', 'soldier', 'gun', 'position']):
            lines.append(f"shoot 35 {speech_text}")
        elif any(w in s_lower for w in ['counter-attack', 'dushman', 'attack', 'fight', 'ladai']):
            lines.append(f"fight 35 {speech_text}")
        elif any(w in s_lower for w in ['wave', 'tiranga', 'successful', 'victory']):
            lines.append(f"wave 35 {speech_text}")
        else:
            lines.append(f"say 35 {speech_text}")

    return "\n".join(lines)

class DynamicEntityRenderer:
    """
    Draws script-mentioned environments (House 🏠, Road 🛣️, Trees 🌳, Border 🚧, Cars 🚗)
    and handles dynamic multi-character stick figure interactions!
    """

    @staticmethod
    def draw_script_environment(draw: ImageDraw.ImageDraw, prompt_text: str, size: Tuple[int, int] = (1280, 720)):
        w, h = size
        text_lower = prompt_text.lower()
        y_ground = h - 180

        draw.rectangle([0, y_ground, w, h], fill='#475569')
        for rx in range(0, w, 70):
            draw.rectangle([rx, y_ground + 80, rx + 40, y_ground + 90], fill='white')

        hx, hy = 70, y_ground - 220
        draw.rectangle([hx, hy, hx + 220, y_ground], fill='#FDE047', outline='black', width=4)
        draw.polygon([(hx - 20, hy), (hx + 110, hy - 110), (hx + 240, hy)], fill='#DC2626', outline='black', width=4)
        draw.rectangle([hx + 80, y_ground - 120, hx + 140, y_ground], fill='#78350F', outline='black', width=3)
        draw.rectangle([hx + 20, hy + 30, hx + 60, hy + 70], fill='#93C5FD', outline='black', width=3)

        for tx in [420, 1040]:
            draw.rectangle([tx, y_ground - 180, tx + 40, y_ground], fill='#78350F', outline='black', width=3)
            draw.ellipse([tx - 60, y_ground - 300, tx + 100, y_ground - 140], fill='#22C55E', outline='black', width=3)

        if any(kw in text_lower for kw in ['border', 'soldier', 'army', 'fauj', 'goli', 'position', 'dushman']):
            for fx in range(100, w, 160):
                draw.rectangle([fx, y_ground - 140, fx + 16, y_ground], fill='#334155')
            draw.line([(0, y_ground - 100), (w, y_ground - 100)], fill='#64748B', width=3)
            draw.line([(0, y_ground - 50), (w, y_ground - 50)], fill='#64748B', width=3)

    @staticmethod
    def draw_stick_character(draw: ImageDraw.ImageDraw, x: float, y_pos: float,
                             action: str, frame_idx: int, facing_right: bool = True,
                             line_thickness: int = 8, is_speaker: bool = False,
                             speech_text: str = "", font: Any = None, char_label: str = ""):
        t = frame_idx / 30.0
        cx = float(x)
        dir_mult = 1 if facing_right else -1

        breath_offset = int(math.sin(frame_idx * 0.4) * 6) if action in ["idle", "say", "shoot", "crouch", "fight", "wave"] else 0
        jump_offset = -int(math.sin(((frame_idx % 20) / 20.0) * math.pi) * 80) if action == "jump" else 0

        head_y = y_pos - 80 + breath_offset + jump_offset
        body_end_y = y_pos + 160 + jump_offset

        draw.ellipse((cx - 40, head_y, cx + 40, head_y + 80), outline="black", width=line_thickness)

        draw.line((cx, head_y + 80, cx, body_end_y), fill="black", width=line_thickness)

        if action == "shoot":
            recoil = math.sin(frame_idx * 1.5) * 4
            draw.line((cx, head_y + 110, cx + dir_mult * (70 + recoil), head_y + 110), fill="black", width=line_thickness)
            draw.line((cx + dir_mult * 40, head_y + 110, cx + dir_mult * (95 + recoil), head_y + 105), fill="black", width=line_thickness + 2)
            if frame_idx % 4 < 2:
                draw.ellipse((cx + dir_mult * 98 - 6, head_y + 98, cx + dir_mult * 98 + 8, head_y + 112), fill="black")

        elif action == "fight":
            punch = math.sin(frame_idx * 1.2) * 45
            draw.line((cx, head_y + 110, cx - dir_mult * 30, y_pos + 140 + jump_offset), fill="black", width=line_thickness)
            draw.line((cx, head_y + 110, cx + dir_mult * (55 + punch), head_y + 105), fill="black", width=line_thickness + 1)

        elif action == "wave":
            wave_arm = math.sin(frame_idx * 0.6) * 30
            draw.line((cx, head_y + 110, cx - dir_mult * 40, y_pos + 150 + jump_offset), fill="black", width=line_thickness)
            draw.line((cx, head_y + 110, cx + dir_mult * (50 + wave_arm), head_y + 30), fill="black", width=line_thickness)

        elif action == "idle":
            draw.line((cx, head_y + 110, cx - 40, y_pos + 150 + jump_offset), fill="black", width=line_thickness)
            draw.line((cx, head_y + 110, cx + 40, y_pos + 150 + jump_offset), fill="black", width=line_thickness)

        else:
            arm_swing = math.sin(frame_idx * 0.5) * 25 if action in ["walk", "run"] else 0
            draw.line((cx, head_y + 110, cx - dir_mult * (50 + arm_swing), y_pos + 100 + jump_offset), fill="black", width=line_thickness)
            draw.line((cx, head_y + 110, cx + dir_mult * (50 + arm_swing), y_pos + 100 + jump_offset), fill="black", width=line_thickness)

        if action == "walk":
            if frame_idx % 6 < 3:
                draw.line((cx, body_end_y, cx - 40, body_end_y + 100), fill="black", width=line_thickness)
                draw.line((cx, body_end_y, cx + 40, body_end_y + 100), fill="black", width=line_thickness)
            else:
                draw.line((cx, body_end_y, cx - 20, body_end_y + 90), fill="black", width=line_thickness)
                draw.line((cx, body_end_y, cx + 20, body_end_y + 90), fill="black", width=line_thickness)
        elif action == "run":
            if frame_idx % 4 < 2:
                draw.line((cx, body_end_y, cx - 60, body_end_y + 80), fill="black", width=line_thickness)
                draw.line((cx, body_end_y, cx + 60, body_end_y + 80), fill="black", width=line_thickness)
            else:
                draw.line((cx, body_end_y, cx - 30, body_end_y + 95), fill="black", width=line_thickness)
                draw.line((cx, body_end_y, cx + 30, body_end_y + 95), fill="black", width=line_thickness)
        else:
            draw.line((cx, body_end_y, cx - 25, body_end_y + 100), fill="black", width=line_thickness)
            draw.line((cx, body_end_y, cx + 25, body_end_y + 100), fill="black", width=line_thickness)

        if is_speaker and speech_text:
            if font is None: font = load_user_font(24)
            bubble_x = cx - 20 if dir_mult == 1 else cx - 180
            bubble_y = head_y - 70
            bw = max(180, len(speech_text) * 11 + 30)
            bh = 55
            draw.rectangle((bubble_x, bubble_y, bubble_x + bw, bubble_y + bh), outline="black", fill="white", width=3)
            draw.polygon([(bubble_x + 30, bubble_y + bh), (bubble_x + 50, bubble_y + bh), (bubble_x + 20, bubble_y + bh + 20)], fill="black")
            draw.text((bubble_x + 15, bubble_y + 14), speech_text, fill="black", font=font)

class UserLineStickRenderer:
    @staticmethod
    def generate_frames_from_script(script_text: str, size: Tuple[int, int] = (1280, 720),
                                   line_thickness: int = 8) -> List[Image.Image]:
        width, height = size
        frames = []
        c1_x = 350
        c2_x = 650
        c3_x = 960
        y_pos = height - 320
        font = load_user_font(24)

        lines = script_text.strip().split('\n')
        for line in lines:
            if not line.strip(): continue
            parts = line.strip().split(maxsplit=2)
            action = parts[0].lower()
            duration = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 30
            speech_text = parts[2] if len(parts) > 2 else ''

            for i in range(duration):
                img = Image.new("RGB", (width, height), "white")
                draw = ImageDraw.Draw(img, "RGBA")

                DynamicEntityRenderer.draw_script_environment(draw, script_text + " " + speech_text, size=size)

                if action == "walk":
                    c1_x += 5
                    c2_x += 4
                    if c1_x > width - 300: c1_x = 350; c2_x = 650
                elif action == "fight":
                    c1_x += 6
                    c2_x += 6
                    c3_x += 10
                    if c3_x > width + 100: c3_x = width + 100

                DynamicEntityRenderer.draw_stick_character(
                    draw, x=c1_x, y_pos=y_pos, action=action, frame_idx=i,
                    facing_right=True, line_thickness=line_thickness,
                    is_speaker=True, speech_text=speech_text, font=font,
                    char_label="Hero"
                )

                c2_action = "wave" if action in ["say", "idle"] else action
                DynamicEntityRenderer.draw_stick_character(
                    draw, x=c2_x, y_pos=y_pos, action=c2_action, frame_idx=i,
                    facing_right=True if action in ["walk", "fight"] else False,
                    line_thickness=line_thickness,
                    is_speaker=False, font=font, char_label="Dost"
                )

                text_lower = (script_text + " " + speech_text).lower()
                if any(kw in text_lower for kw in ['dushman', 'enemy', 'soldier', 'fauj', 'border', 'goli', 'position', 'fight', 'attack']):
                    c3_action = "run" if action == "fight" else ("shoot" if action == "shoot" else "idle")
                    c3_facing = True if action == "fight" else False
                    DynamicEntityRenderer.draw_stick_character(
                        draw, x=c3_x, y_pos=y_pos, action=c3_action, frame_idx=i,
                        facing_right=c3_facing, line_thickness=line_thickness,
                        is_speaker=False, font=font, char_label="Enemy"
                    )

                frames.append(img)

        return frames

class CartoonSceneRenderer:
    @staticmethod
    def render_scene(scene_id: int, scene_text: str, frame_idx: int,
                     total_frames: int = 60, size: Tuple[int, int] = (1280, 720)) -> Image.Image:
        script = parse_prompt_to_user_script(scene_text)
        frames = UserLineStickRenderer.generate_frames_from_script(script, size=size)
        if frames:
            idx = int((frame_idx / max(1, total_frames - 1)) * (len(frames) - 1))
            return frames[min(idx, len(frames) - 1)]
        return Image.new("RGB", size, "white")

if __name__ == "__main__":
    script = "Ek ladka ghar se nikal kr raste me dost se milta he aur hello kehta he"
    frames = UserLineStickRenderer.generate_frames_from_script(script)
    os.makedirs("scratch", exist_ok=True)
    frames[0].save("scratch/test_mandatory_multi_character.png")
    print(f"Saved test_mandatory_multi_character.png ({len(frames)} frames)!")
