import asyncio
import edge_tts
import os
import random
import subprocess
try:
    from gtts import gTTS
except Exception:
    gTTS = None

def make_audio(text, output_path, voice_id='hi-IN-MadhurNeural'):
    """
    Multi-Level Fail-Safe Audio Engine:
    1. EdgeTTS (Microsoft Edge Neural Voice)
    2. gTTS (Google Text-to-Speech Fallback)
    3. FFmpeg Silent Audio Fallback (Zero-crash guarantee for 2+ parallel users)
    """
    print(f"🎙️ Generating Voice: {text[:30]}...")
    if not text or not text.strip():
        text = "Welcome to the video."
        
    async def run_edge_tts():
        communicate = edge_tts.Communicate(text, voice_id)
        await communicate.save(output_path)

    try:
        asyncio.run(run_edge_tts())
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"✅ EdgeTTS Audio saved: {output_path}")
            return output_path
    except Exception as e:
        print(f"⚠️ EdgeTTS Failed: {e}. Switching to gTTS Fallback...")

    if gTTS is not None:
        try:
            lang = "hi" if any('\u0900' <= char <= '\u097F' for char in text) else "en"
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"✅ gTTS Audio saved: {output_path}")
                return output_path
        except Exception as e:
            print(f"⚠️ gTTS Fallback Failed: {e}. Generating Silent Audio Fallback...")

    try:
        dur = max(3.0, len(text.split()) / 2.5)
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", 
            "-t", str(dur), "-q:a", "9", "-acodec", "libmp3lame", output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
            print(f"✅ Silent Audio Fallback created: {output_path}")
            return output_path
    except Exception as e:
        print(f"❌ Ultimate Audio Fallback Failed: {e}")

    return None
