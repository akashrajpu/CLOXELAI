import os
import re
import time
import requests
import subprocess
import uuid
import tempfile
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def generate_world_news_ultra_video(user_prompt, output_mp4, duration, target_size=(1080, 1920), fps=60):
    # CIRCUIT BREAKER: Prevent OOM on 512MB RAM servers.
    # The actual HTML/WebGL WebM recording code is fully intact below.
    # To enable it in the future when RAM is upgraded, simply remove this raise statement.
    raise Exception("Just pending for funding")
    
    print(f"🌍 [World News WebGL Engine] Initiating 3D Cinematic Animation for {duration:.1f}s...")
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("AI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not set. Cannot generate World News WebGL.")
        return None

    w, h = target_size
    
    # 1. AI Prompt Construction
    system_instruction = f"""Act as a Senior Motion Graphics Designer and WebGL/Frontend Developer specializing in After Effects style programmatic animations.
I have a {duration}-second vertical video script. I need a single-file, production-grade standalone HTML + CSS + JS code that renders a fully synced cinematic motion graphics video.

Key Technical Requirements:
1. Aspect Ratio & Resolution:
   - {w}x{h} canvas scaling with dark, premium cinematic background (#02040a / vignette / subtle grid).
2. Motion & Visual FX (After Effects Style):
   - Canvas 2D / WebGL integration for 3D elements (particle dust, glowing wireframes, data nodes, waveforms).
   - Post-processing effects: Chromatic aberration, subtle camera shake/glitch on impacts, scanlines, lens flare.
   - Dynamic UI HUD elements: Glassmorphism cards, glowing status badges, counting metrics, and kinetic typography.
3. Script Timeline Synchronization:
   - An exact {duration}-second timeline engine with an auto-playing progress bar and millisecond timer.
   - Clean scene switching based on the script timestamps provided below.
4. Export:
   - You MUST auto-start the animation immediately on load.
   - Use MediaRecorder to record the canvas at {fps} FPS. Set mimeType to 'video/webm'.
   - When the timeline reaches exactly {duration} seconds, you MUST automatically stop the recording, trigger a download of the recorded webm file by creating an anchor tag with the download attribute as 'output.webm', append it to body, and click it. Do NOT wait for user input.

Here is the exact {duration}-second script to animate:
{user_prompt}

Output ONLY the complete, copy-paste ready, single-file HTML code without placeholders or omissions. Start directly with <!DOCTYPE html>.
"""

    max_retries = 3
    generated_code = ""
    used_model = None

    for attempt in range(max_retries):
        print(f"   🤖 Calling Gemini API for HTML WebGL (attempt {attempt+1}/{max_retries})...")
        models_to_try = ['gemini-3.8-flash', 'gemini-3.6-flash', 'gemini-flash-latest', 'gemini-3.5-flash', 'gemini-3.1-pro-preview']
        for m_name in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": system_instruction}]}]}
                r_rest = requests.post(url, json=payload, timeout=300.0)
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
            print(f"   ✅ Gemini API returned WebGL code ({len(generated_code)} chars) using model: {used_model}")
            break
        else:
            print(f"⚠️ All Gemini models failed on attempt {attempt+1}. Sleeping 2s before retry...")
            time.sleep(2)

    if not generated_code:
        print("⚠️ Gemini API offline or 503. WebGL Generation Failed.")
        return None

    clean_code = re.sub(r"^```html\n?", "", generated_code, flags=re.MULTILINE)
    clean_code = re.sub(r"^```\n?", "", clean_code, flags=re.MULTILINE)
    clean_code = clean_code.strip()

    job_id = str(uuid.uuid4())[:8]
    job_dir = os.path.dirname(output_mp4) or "."
    html_path = os.path.join(job_dir, f"world_news_{job_id}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(clean_code)
        
    print(f"   🌐 Saved HTML to {html_path}. Launching headless Selenium browser to record...")

    download_dir = os.path.abspath(os.path.join(job_dir, f"dl_{job_id}"))
    os.makedirs(download_dir, exist_ok=True)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--window-size={w},{h}")
    options.add_experimental_option("prefs", {
      "download.default_directory": download_dir,
      "download.prompt_for_download": False,
    })
    
    try:
        import shutil
        system_driver = shutil.which("chromedriver")
        if system_driver:
            print(f"   ⚙️ Using system chromedriver at {system_driver}")
            service = Service(system_driver)
            sys_browser = shutil.which("chromium-browser") or shutil.which("google-chrome")
            if sys_browser:
                options.binary_location = sys_browser
        else:
            service = Service(ChromeDriverManager().install())
            
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("file://" + os.path.abspath(html_path))
        
        # Wait for duration + 10 seconds for the download to trigger and finish
        wait_time = duration + 10
        print(f"   ⏱️ Waiting {wait_time:.1f}s for WebGL animation and MediaRecorder download...")
        time.sleep(wait_time)
        driver.quit()
        
        files = os.listdir(download_dir)
        webm_file = None
        for file in files:
            if file.endswith(".webm"):
                webm_file = os.path.join(download_dir, file)
                break
                
        if webm_file:
            print(f"   🎥 Successfully captured WebM! Converting to MP4...")
            # Convert webm to mp4 using ffmpeg
            try:
                subprocess.run([
                    "ffmpeg", "-y", "-i", webm_file, 
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
                    "-vf", f"scale={w}:{h},format=yuv420p",
                    output_mp4
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"   ✅ Final World News MP4 saved to {output_mp4}")
                
                # Cleanup
                os.remove(html_path)
                os.remove(webm_file)
                os.rmdir(download_dir)
                return output_mp4
            except Exception as e:
                print(f"   ❌ FFmpeg conversion failed: {e}")
                return None
        else:
            print("   ❌ MediaRecorder failed to download the webm file. Code might be buggy.")
            return None
    except Exception as e:
        print(f"   ❌ Selenium headless recording failed: {e}")
        return None

if __name__ == "__main__":
    pass
