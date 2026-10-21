import requests
import os

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "jqGZN1a4uHQFpxqdFAdVaD1l1eyjW1kzHqtdlNJ1TPkSmOEXcbAL7yhN")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "39827606-4df15a6b0c26bbef50352ef2e")
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
                valid_files.sort(key=lambda x: abs(x.get('height', 720) - 720))
                best_file = valid_files[0]
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
    """Pinterest HD Pins media download karta hai using gallery-dl & fail-safe API/scraper"""
    dir_name = os.path.dirname(job_id) if job_id else ""
    base_name = os.path.basename(job_id) if job_id else "pinterest_media"
    target_dir = dir_name if dir_name else "."

    try:
        from pinterest_downloader import fetch_pinterest_photos_via_gallery_dl
        downloaded = fetch_pinterest_photos_via_gallery_dl(keyword, limit=count, output_dir=target_dir)
        if downloaded:
            media_paths = []
            for i, p_file in enumerate(downloaded):
                ext = os.path.splitext(p_file)[1] or ".jpg"
                target_filename = os.path.join(target_dir, f"pinterest_{base_name}_{i}{ext}") if target_dir != "." else f"pinterest_{base_name}_{i}{ext}"
                if p_file != target_filename:
                    import shutil
                    shutil.move(p_file, target_filename)
                media_paths.append(target_filename)
                print(f"✅ [Pinterest gallery-dl] Pin media saved: {target_filename}")
            return media_paths
    except Exception as e_dl:
        print(f"⚠️ [Pinterest gallery-dl fallback]: {e_dl}")

    token = os.getenv("PINTEREST_ACCESS_TOKEN") or PINTEREST_ACCESS_TOKEN
    if not token or str(token).strip() == "":
        return []
        
    print(f"📥 [Pinterest API] '{keyword}' ke liye Pins search kar rahe hain...")
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
                filename = os.path.join(dir_name, f"pinterest_{base_name}_{i}.jpg") if dir_name else f"pinterest_{base_name}_{i}.jpg"
                
                img_data = requests.get(img_url, timeout=10).content
                with open(filename, "wb") as f:
                    f.write(img_data)
                media_paths.append(filename)
                print(f"✅ [Pinterest API] Pin media downloaded: {filename}")
            return media_paths
    except Exception as e:
        print(f"⚠️ [Pinterest Non-Blocking Warning]: {e}. Falling back to next provider...")
    return []

def fetch_videos(keyword, job_id, count=1, orientation="portrait", category="Random", video_type="short", topic=""):
    """
    Multi-Provider Media Fetcher:
    - For short and long video modes (video_type in ['short', 'long']): ALWAYS fetch real HD video clips from Pexels & Pixabay!
    - Uses rich, descriptive multi-word scene search queries so Pexels precisely matches the script context.
    - Contextual fallbacks based on topic & category instead of random footage.
    """
    cat_lower = str(category).lower()
    is_ultra_mode = (str(video_type).lower() == "ultra")

    noise_words = {"category", "random", "concept", "impact"}
    clean_words = [w for w in keyword.replace('🎨', '').replace('🎲', '').replace('✍️', '').split() if w.lower() not in noise_words]
    video_query = " ".join(clean_words) if clean_words else keyword

    if is_ultra_mode:
        prefer_pinterest = any(c in cat_lower for c in ['cartoon', 'animation', 'documentary', 'comedy', 'horror', 'mythology', 'history', 'anime', 'art', 'photo'])
        if prefer_pinterest:
            try:
                print(f"🎨 [Ultra Mode Priority: {category}] Trying Pinterest HD Pins...")
                search_term = f"{keyword} {category.replace('🎲', '').replace('🎨', '').replace('✍️', '').strip()}"
                pins = fetch_pinterest_pins(search_term, job_id, count=count, orientation=orientation)
                if not pins:
                    pins = fetch_pinterest_pins(keyword, job_id, count=count, orientation=orientation)
                if pins:
                    return pins
            except Exception as e_p:
                print(f"⚠️ [Pinterest Skip]: {e_p}")

    # Build prioritized list of search queries from most specific to broader
    search_queries = []
    if video_query:
        search_queries.append(video_query)
    if topic and topic.strip() and topic.lower() not in video_query.lower():
        search_queries.insert(0, f"{topic.strip()} {video_query}".strip())
    
    words_list = video_query.split()
    if len(words_list) > 3:
        search_queries.append(" ".join(words_list[:3]))
    if topic and topic.strip() and topic.strip() not in search_queries:
        search_queries.append(topic.strip())

    # Deduplicate queries preserving order
    seen_q = set()
    queries_to_try = []
    for q in search_queries:
        ql = q.lower().strip()
        if ql and ql not in seen_q:
            seen_q.add(ql)
            queries_to_try.append(q.strip())

    for q_item in queries_to_try:
        try:
            clips = fetch_pexels_videos(q_item, job_id, count=count, orientation=orientation)
            if clips:
                return clips
        except Exception as e_px:
            print(f"⚠️ [Pexels Query Skip]: {e_px}")
            
        try:
            clips = fetch_pixabay_videos(q_item, job_id, count=count, orientation=orientation)
            if clips:
                return clips
        except Exception as e_pb:
            print(f"⚠️ [Pixabay Query Skip]: {e_pb}")

    # Contextual fallbacks based on topic and category
    contextual_fallbacks = []
    if topic and topic.strip():
        contextual_fallbacks.append(topic.strip())
    if category and category.lower() not in ["random", "all"]:
        contextual_fallbacks.append(f"{category} cinematic footage")
    if clean_words:
        contextual_fallbacks.append(clean_words[0])
    contextual_fallbacks.extend(["cinematic atmospheric backdrop", "abstract background motion"])

    for fallback_kw in contextual_fallbacks:
        if fallback_kw.lower() not in seen_q:
            try:
                print(f"🔄 Retrying with contextual fallback video clip keyword: '{fallback_kw}'...")
                clips = fetch_pexels_videos(fallback_kw, job_id, count=count, orientation=orientation)
                if not clips:
                    clips = fetch_pixabay_videos(fallback_kw, job_id, count=count, orientation=orientation)
                if clips:
                    return clips
            except Exception:
                continue

    if is_ultra_mode:
        try:
            pins = fetch_pinterest_pins(keyword, job_id, count=count, orientation=orientation)
            if pins:
                return pins
        except Exception as e_p2:
            print(f"⚠️ [Pinterest Fallback Skip]: {e_p2}")

    print(f"⚠️ [Media Fetcher] No online media found for '{keyword}'. Using internal canvas background...")
    return []
