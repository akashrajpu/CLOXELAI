import requests
import os

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "jqGZN1a4uHQFpxqdFAdVaD1l1eyjW1kzHqtdlNJ1TPkSmOEXcbAL7yhN")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "")

def fetch_pexels_videos(keyword, job_id, count=1, orientation="portrait"):
    """Pexels API se HD stock video clips download karta hai"""
    key = os.getenv("PEXELS_API_KEY") or PEXELS_API_KEY
    if not key:
        return []
        
    print(f"📥 [Pexels] '{keyword}' ke liye video clip ({orientation}) dhoondh rahe hain...")
    headers = {"Authorization": key}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page={count}&orientation={orientation}"
    
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code != 200:
            return []
        data = res.json()
        video_paths = []
        if 'videos' in data and len(data['videos']) > 0:
            for i, video_data in enumerate(data['videos']):
                valid_files = [vf for vf in video_data.get('video_files', []) if vf.get('link')]
                if not valid_files: continue
                valid_files.sort(key=lambda x: x.get('width', 0) * x.get('height', 0))
                best_file = valid_files[0]
                for vf in valid_files:
                    if 720 <= vf.get('height', 0) <= 1080:
                        best_file = vf
                        break
                video_url = best_file['link']
                dir_name = os.path.dirname(job_id)
                base_name = os.path.basename(job_id)
                filename = os.path.join(dir_name, f"clip_{base_name}_{i}.mp4") if dir_name else f"clip_{base_name}_{i}.mp4"
                
                with requests.get(video_url, stream=True, timeout=20) as r_vid:
                    r_vid.raise_for_status()
                    with open(filename, "wb") as f:
                        for chunk in r_vid.iter_content(chunk_size=64*1024):
                            if chunk:
                                f.write(chunk)
                video_paths.append(filename)
                print(f"✅ [Pexels] Video clip downloaded: {filename}")
            return video_paths
    except Exception as e:
        print(f"⚠️ [Pexels] Error: {e}")
    return []

def fetch_pixabay_videos(keyword, job_id, count=1, orientation="portrait"):
    """Pixabay API se free HD stock videos download karta hai"""
    key = os.getenv("PIXABAY_API_KEY") or PIXABAY_API_KEY
    if not key:
        return []
        
    print(f"📥 [Pixabay] '{keyword}' ke liye video clip ({orientation}) dhoondh rahe hain...")
    v_type = "film" if orientation == "landscape" else "all"
    url = f"https://pixabay.com/api/videos/?key={key}&q={requests.utils.quote(keyword)}&video_type={v_type}&per_page=5"
    
    try:
        res = requests.get(url, timeout=12)
        if res.status_code != 200:
            return []
        data = res.json()
        video_paths = []
        hits = data.get('hits', [])
        if hits:
            for i, hit in enumerate(hits[:count]):
                videos = hit.get('videos', {})
                best_vid = videos.get('medium') or videos.get('large') or videos.get('small')
                if not best_vid or not best_vid.get('url'): continue
                video_url = best_vid['url']
                dir_name = os.path.dirname(job_id)
                base_name = os.path.basename(job_id)
                filename = os.path.join(dir_name, f"pixabay_{base_name}_{i}.mp4") if dir_name else f"pixabay_{base_name}_{i}.mp4"
                
                with requests.get(video_url, stream=True, timeout=20) as r_vid:
                    r_vid.raise_for_status()
                    with open(filename, "wb") as f:
                        for chunk in r_vid.iter_content(chunk_size=64*1024):
                            if chunk:
                                f.write(chunk)
                video_paths.append(filename)
                print(f"✅ [Pixabay] Video clip downloaded: {filename}")
            return video_paths
    except Exception as e:
        print(f"⚠️ [Pixabay] Error: {e}")
    return []

def fetch_pinterest_pins(keyword, job_id, count=1, orientation="portrait"):
    """Pinterest API se HD Pins media download karta hai (100% Optional & Fail-Safe)"""
    token = os.getenv("PINTEREST_ACCESS_TOKEN") or PINTEREST_ACCESS_TOKEN
    if not token or str(token).strip() == "":
        return []
        
    print(f"📥 [Pinterest] '{keyword}' ke liye Pins search kar rahe hain...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.pinterest.com/v5/search/pins?query={requests.utils.quote(keyword)}&page_size=5"
    
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code != 200:
            print(f"⚠️ [Pinterest] Token/API response ({res.status_code}). Skipping to next provider...")
            return []
        data = res.json()
        pins = data.get('items', [])
        media_paths = []
        if pins:
            for i, pin in enumerate(pins[:count]):
                images = pin.get('images', {})
                img_url = (images.get('originals') or {}).get('url') or (images.get('1200x') or {}).get('url')
                if not img_url: continue
                dir_name = os.path.dirname(job_id)
                base_name = os.path.basename(job_id)
                filename = os.path.join(dir_name, f"pinterest_{base_name}_{i}.jpg") if dir_name else f"pinterest_{base_name}_{i}.jpg"
                
                img_data = requests.get(img_url, timeout=10).content
                with open(filename, "wb") as f:
                    f.write(img_data)
                media_paths.append(filename)
                print(f"✅ [Pinterest] Pin media downloaded: {filename}")
            return media_paths
    except Exception as e:
        print(f"⚠️ [Pinterest Non-Blocking Warning]: {e}. Falling back to next provider...")
    return []

def fetch_videos(keyword, job_id, count=1, orientation="portrait", category="Random"):
    """
    100% Optional & Non-Blocking Multi-Provider Media Fetcher:
    - Never crashes video generation even if ALL keys are missing or invalid!
    - Try order: Pinterest (optional) -> Pexels -> Pixabay -> Generic Fallback
    """
    cat_lower = str(category).lower()
    
    prefer_pinterest = any(c in cat_lower for c in ['cartoon', 'animation', 'documentary', 'comedy', 'horror', 'mythology', 'history', 'anime', 'art', 'photo'])
    
    if prefer_pinterest:
        try:
            print(f"🎨 [Category: {category}] Trying Pinterest HD Pins (Optional Priority)...")
            search_term = f"{keyword} {category.replace('🎲', '').replace('🎨', '').replace('✍️', '').strip()}"
            pins = fetch_pinterest_pins(search_term, job_id, count=count, orientation=orientation)
            if not pins:
                pins = fetch_pinterest_pins(keyword, job_id, count=count, orientation=orientation)
            if pins:
                return pins
        except Exception as e_p:
            print(f"⚠️ [Pinterest Skip]: {e_p}")

    try:
        clips = fetch_pexels_videos(keyword, job_id, count=count, orientation=orientation)
        if clips:
            return clips
    except Exception as e_px:
        print(f"⚠️ [Pexels Skip]: {e_px}")
        
    try:
        clips = fetch_pixabay_videos(keyword, job_id, count=count, orientation=orientation)
        if clips:
            return clips
    except Exception as e_pb:
        print(f"⚠️ [Pixabay Skip]: {e_pb}")

    try:
        pins = fetch_pinterest_pins(keyword, job_id, count=count, orientation=orientation)
        if pins:
            return pins
    except Exception as e_p2:
        print(f"⚠️ [Pinterest Fallback Skip]: {e_p2}")

    for fallback_kw in ["nature", "technology", "abstract", "city"]:
        if fallback_kw != keyword.lower():
            try:
                print(f"🔄 Retrying with fallback keyword: '{fallback_kw}'...")
                clips = fetch_pexels_videos(fallback_kw, job_id, count=count, orientation=orientation)
                if clips:
                    return clips
            except Exception:
                continue
                
    print(f"⚠️ [Media Fetcher] No online media found for '{keyword}'. Using internal canvas background...")
    return []