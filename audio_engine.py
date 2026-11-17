import asyncio
import edge_tts
import json
import os
import random
import subprocess
import requests

try:
    from gtts import gTTS
except Exception:
    gTTS = None

# Optional local Kokoro models if installed
try:
    from kokoro import KPipeline
    import soundfile as sf
    _HAS_KOKORO_LOCAL = True
except Exception:
    _HAS_KOKORO_LOCAL = False

try:
    from kokoro_onnx import Kokoro as KokoroONNX
    import soundfile as sf
    _HAS_KOKORO_ONNX = True
except Exception:
    _HAS_KOKORO_ONNX = False

_kokoro_local_pipeline = None
_kokoro_onnx_instance = None

KOKORO_VOICES = {
    # American Female
    "af_heart": "af_heart",
    "af_bella": "af_bella",
    "af_sarah": "af_sarah",
    "af_nicole": "af_nicole",
    "af_sky": "af_sky",
    "af_alloy": "af_alloy",
    "af_aoede": "af_aoede",
    "af_jessica": "af_jessica",
    "af_kore": "af_kore",
    "af_river": "af_river",
    # American Male
    "am_adam": "am_adam",
    "am_michael": "am_michael",
    "am_eric": "am_eric",
    "am_echo": "am_echo",
    "am_fenrir": "am_fenrir",
    "am_liam": "am_liam",
    "am_onyx": "am_onyx",
    "am_puck": "am_puck",
    "am_santa": "am_santa",
    # British Female
    "bf_emma": "bf_emma",
    "bf_isabella": "bf_isabella",
    "bf_alice": "bf_alice",
    "bf_lily": "bf_lily",
    # British Male
    "bm_george": "bm_george",
    "bm_daniel": "bm_daniel",
    "bm_fable": "bm_fable",
    "bm_lewis": "bm_lewis",
    # Hindi Female
    "hf_alpha": "hf_alpha",
    "hf_beta": "hf_beta",
    # Hindi Male
    "hm_omega": "hm_omega",
    "hm_psi": "hm_psi",
}


def is_kokoro_voice(voice_id: str) -> bool:
    """Check if the requested voice_id corresponds to a Kokoro voice."""
    if not voice_id:
        return False
    v = str(voice_id).strip().lower()
    return "kokoro" in v or v in KOKORO_VOICES or any(v.startswith(f"{k}-") or v.endswith(f"-{k}") for k in KOKORO_VOICES)


def extract_kokoro_voice_name(voice_id: str) -> str:
    """Extract standard voice identifier for Kokoro (e.g. 'hf_alpha', 'hm_omega', 'af_heart', 'am_adam')."""
    if not voice_id:
        return "af_heart"
    v = str(voice_id).strip().lower()
    for name in KOKORO_VOICES:
        if name in v:
            return name
    # Detect Hindi Kokoro requests
    if any(h in v for h in ["hindi", "india", "hind", "hf", "hm"]):
        if any(m in v for m in ["male", "man", "boy", "guy", "omega", "psi"]):
            return "hm_omega"
        return "hf_alpha"
    # Default female or male based on hints
    if any(m in v for m in ["male", "man", "adam", "boy", "guy"]):
        return "am_adam"
    return "af_heart"


def generate_kokoro_audio(text: str, output_path: str, voice_name: str = "af_heart") -> bool:
    """
    Synthesize audio using Kokoro Neural TTS:
    1. Local KPipeline / Kokoro-ONNX if packages/weights are present.
    2. Custom KOKORO_API_URL (OpenAI-compatible /v1/audio/speech).
    3. Public Hugging Face Space endpoint (hexgrad/Kokoro-TTS).
    Returns True if successfully saved to output_path.
    """
    global _kokoro_local_pipeline, _kokoro_onnx_instance
    print(f"🎙️ [Kokoro TTS Engine] Generating neural voice '{voice_name}': {text[:40]}...")

    # 1. Custom KOKORO_API_URL (OpenAI-compatible /v1/audio/speech or custom microservice)
    custom_api_url = os.environ.get("KOKORO_API_URL", "").strip()
    if custom_api_url:
        try:
            endpoint = custom_api_url if custom_api_url.endswith(("/audio/speech", "/speech", "/generate")) else f"{custom_api_url.rstrip('/')}/v1/audio/speech"
            headers = {"Content-Type": "application/json"}
            api_key = os.environ.get("KOKORO_API_KEY", "").strip()
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            payload = {
                "model": "kokoro",
                "input": text,
                "voice": voice_name,
                "response_format": "mp3",
                "speed": 1.0
            }
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=12)
            if resp.status_code == 200 and len(resp.content) > 1000:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    print(f"✅ [Kokoro TTS API] Audio saved: {output_path} ({os.path.getsize(output_path)} bytes)")
                    return True
        except Exception as e_api:
            print(f"⚠️ [Kokoro TTS API Warning]: {e_api}")

    # 2. Local KPipeline (if kokoro and weights are installed locally)
    if _HAS_KOKORO_LOCAL:
        try:
            has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
            if voice_name.startswith("h") or has_devanagari:
                lang_code = "h"
            elif voice_name.startswith("b"):
                lang_code = "b"
            else:
                lang_code = "a"
            if _kokoro_local_pipeline is None or getattr(_kokoro_local_pipeline, "lang_code", "") != lang_code:
                _kokoro_local_pipeline = KPipeline(lang_code=lang_code)
            generator = _kokoro_local_pipeline(text, voice=voice_name, speed=1.0)
            audio_segments = []
            for _, _, audio in generator:
                audio_segments.append(audio)
            if audio_segments:
                import numpy as np
                full_audio = np.concatenate(audio_segments) if len(audio_segments) > 1 else audio_segments[0]
                tmp_wav = output_path.rsplit(".", 1)[0] + "_tmp.wav"
                sf.write(tmp_wav, full_audio, 24000)
                cmd = ["ffmpeg", "-y", "-i", tmp_wav, "-q:a", "2", "-acodec", "libmp3lame", output_path]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                try: os.remove(tmp_wav)
                except Exception: pass
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    print(f"✅ [Kokoro Local Engine] Audio saved: {output_path}")
                    return True
        except Exception as e_loc:
            print(f"⚠️ [Kokoro Local Engine Notice]: {e_loc}")

    # 3. Local Kokoro-ONNX (if kokoro-onnx installed and model files present)
    if _HAS_KOKORO_ONNX:
        try:
            model_path = os.environ.get("KOKORO_ONNX_MODEL", "kokoro-v1.0.onnx")
            voices_path = os.environ.get("KOKORO_ONNX_VOICES", "voices-v1.0.bin")
            if os.path.exists(model_path) and os.path.exists(voices_path):
                if _kokoro_onnx_instance is None:
                    _kokoro_onnx_instance = KokoroONNX(model_path, voices_path)
                samples, sample_rate = _kokoro_onnx_instance.create(
                    text, voice=voice_name, speed=1.0, lang="en-us"
                )
                tmp_wav = output_path.rsplit(".", 1)[0] + "_tmp.wav"
                sf.write(tmp_wav, samples, sample_rate)
                cmd = ["ffmpeg", "-y", "-i", tmp_wav, "-q:a", "2", "-acodec", "libmp3lame", output_path]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                try: os.remove(tmp_wav)
                except Exception: pass
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    print(f"✅ [Kokoro ONNX Engine] Audio saved: {output_path}")
                    return True
        except Exception as e_onnx:
            print(f"⚠️ [Kokoro ONNX Notice]: {e_onnx}")

    # 4. Hugging Face Space endpoint (Kokoro Native Neural Engine)
    try:
        try:
            from gradio_client import Client
            has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
            is_hindi = voice_name.startswith("h") or has_devanagari

            if is_hindi:
                # Dedicated Native Kokoro Hindi Space (hf_alpha, hf_beta, hm_omega, hm_psi)
                valid_hindi_voices = ['hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi']
                target_voice = voice_name if voice_name in valid_hindi_voices else ('hf_alpha' if 'f' in voice_name or 'swara' in voice_name else 'hm_omega')
                client = Client("leonelhs/kokoro-tts-hindi")
                pred_res = client.predict(text=text, voice=target_voice, speed=1.0, api_name="/predict")
                wav_file = pred_res[0] if isinstance(pred_res, (list, tuple)) else pred_res
                if wav_file and os.path.exists(wav_file) and os.path.getsize(wav_file) > 1000:
                    cmd = ["ffmpeg", "-y", "-i", wav_file, "-q:a", "2", "-acodec", "libmp3lame", output_path]
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                        print(f"✅ [Kokoro Hindi Gradio Engine] Audio saved: {output_path} ({os.path.getsize(output_path)} bytes)")
                        return True
            else:
                # Official hexgrad Kokoro-TTS Space (American & British English)
                client = Client("hexgrad/Kokoro-TTS")
                if 4 in client.endpoints:
                    client.endpoints[4].is_valid = True
                    pred_res = client.predict(text, voice_name, 1.0, False, fn_index=4)
                    wav_file = pred_res[0] if isinstance(pred_res, (list, tuple)) else pred_res
                    if wav_file and os.path.exists(wav_file) and os.path.getsize(wav_file) > 1000:
                        cmd = ["ffmpeg", "-y", "-i", wav_file, "-q:a", "2", "-acodec", "libmp3lame", output_path]
                        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                            print(f"✅ [Kokoro Gradio Engine] Audio saved: {output_path} ({os.path.getsize(output_path)} bytes)")
                            return True
        except Exception as e_gc:
            print(f"⚠️ [Kokoro Gradio Client Notice]: {e_gc}")

        hf_url = "https://hexgrad-kokoro-tts.hf.space/api/predict"
        hf_payload = {"data": [text, voice_name, 1.0]}
        hf_resp = requests.post(hf_url, json=hf_payload, timeout=8)
        if hf_resp.status_code == 200:
            res_json = hf_resp.json()
            data_arr = res_json.get("data", [])
            if data_arr and isinstance(data_arr[0], dict) and "name" in data_arr[0]:
                file_rel = data_arr[0]["name"]
                file_url = f"https://hexgrad-kokoro-tts.hf.space/file={file_rel}"
                file_resp = requests.get(file_url, timeout=10)
                if file_resp.status_code == 200 and len(file_resp.content) > 1000:
                    tmp_wav = output_path.rsplit(".", 1)[0] + "_tmp.wav"
                    with open(tmp_wav, "wb") as f:
                        f.write(file_resp.content)
                    cmd = ["ffmpeg", "-y", "-i", tmp_wav, "-q:a", "2", "-acodec", "libmp3lame", output_path]
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    try: os.remove(tmp_wav)
                    except Exception: pass
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                        print(f"✅ [Kokoro HF Space] Audio saved: {output_path}")
                        return True
    except Exception as e_hf:
        print(f"⚠️ [Kokoro HF Space Notice]: {e_hf}")

    return False


def make_audio(text, output_path, voice_id='hi-IN-MadhurNeural'):
    """
    Multi-Level Fail-Safe Audio Engine:
    1. Kokoro Neural TTS (when Kokoro voice requested, e.g. kokoro-af_heart, kokoro-am_adam)
    2. EdgeTTS (Microsoft Edge Neural Voice, ultra high fidelity)
    3. gTTS (Google Text-to-Speech Fallback)
    4. FFmpeg Silent Audio Fallback (Zero-crash guarantee under any circumstance)
    """
    if not text or not str(text).strip():
        text = "Welcome to the video."
    text = str(text).strip()

    # Step 1: Kokoro TTS Handling
    if is_kokoro_voice(voice_id):
        kokoro_voice_name = extract_kokoro_voice_name(voice_id)
        kokoro_ok = generate_kokoro_audio(text, output_path, kokoro_voice_name)
        if kokoro_ok and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return output_path

        # If Kokoro synthesis is unavailable or timed out, intelligently fall back to matched EdgeTTS
        print(f"⚠️ Kokoro TTS service unavailable. Seamlessly activating high-fidelity EdgeTTS neural fallback...")
        has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
        is_female = kokoro_voice_name.startswith(("af_", "bf_", "hf_"))
        is_hindi = kokoro_voice_name.startswith("h") or has_devanagari
        if is_hindi:
            voice_id = "hi-IN-SwaraNeural" if is_female else "hi-IN-MadhurNeural"
        else:
            voice_id = "en-US-JennyNeural" if is_female else "en-US-GuyNeural"
        print(f"   🔄 Switched to EdgeTTS Neural Voice: {voice_id}")

    # Step 2: EdgeTTS (Microsoft Edge Neural Voice)
    print(f"🎙️ Generating EdgeTTS Voice ({voice_id}): {text[:30]}...")
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

    # Step 3: gTTS Fallback
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

    # Step 4: FFmpeg Silent Audio Fallback
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
