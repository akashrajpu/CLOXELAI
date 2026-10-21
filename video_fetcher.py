import requests
import os

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "jqGZN1a4uHQFpxqdFAdVaD1l1eyjW1kzHqtdlNJ1TPkSmOEXcbAL7yhN")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "39827606-4df15a6b0c26bbef50352ef2e")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "")

GLOBAL_USED_MEDIA_IDS = set()

def fetch_pexels_videos(keyword, job_id, count=1, orientation="portrait", used_media_ids=None):
    """Pexels API se HD stock video clips download karta hai with zero-duplicate protection"""
    key = os.getenv("PEXELS_API_KEY") or PEXELS_API_KEY
    if not key:
        return []
        
    print(f"📥 [Pexels] '{keyword}' ke liye video clip ({orientation}) dhoondh rahe hain...")
    headers = {"Authorization": key}
    per_page = max(15, count * 4)
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(keyword)}&per_page={per_page}&orientation={orientation}"
    
    if used_media_ids is None:
        used_media_ids = set()

    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code != 200:
            return []
        data = res.json()
        video_paths = []
        videos = data.get('videos', [])
        if videos:
            selected_videos = []
            # Pass 1: Fresh videos never seen globally or in this job
            for video_data in videos:
                vid_id = str(video_data.get('id', ''))
                if vid_id and (vid_id in used_media_ids or vid_id in GLOBAL_USED_MEDIA_IDS):
                    continue
                valid_files = [vf for vf in video_data.get('video_files', []) if vf.get('link')]
                if not valid_files:
                    continue
                video_url = valid_files[0]['link']
                if video_url in used_media_ids or video_url in GLOBAL_USED_MEDIA_IDS:
                    continue
                selected_videos.append(video_data)
                if len(selected_videos) >= count:
                    break

            # Pass 2: If needed, allow videos unused in current video job
            if len(selected_videos) < count:
                for video_data in videos:
                    vid_id = str(video_data.get('id', ''))
                    if vid_id and vid_id in used_media_ids:
                        continue
                    if video_data not in selected_videos:
                        selected_videos.append(video_data)
                        if len(selected_videos) >= count:
                            break

            dir_name = os.path.dirname(job_id)
            base_name = os.path.basename(job_id)

            for i, video_data in enumerate(selected_videos):
                vid_id = str(video_data.get('id', ''))
                valid_files = [vf for vf in video_data.get('video_files', []) if vf.get('link')]
                valid_files.sort(key=lambda x: abs(x.get('height', 720) - 720))
                best_file = valid_files[0]
                video_url = best_file['link']
                filename = os.path.join(dir_name, f"clip_{base_name}_{i}.mp4") if dir_name else f"clip_{base_name}_{i}.mp4"
                
                with requests.get(video_url, stream=True, timeout=20) as r_vid:
                    r_vid.raise_for_status()
                    with open(filename, "wb") as f:
                        for chunk in r_vid.iter_content(chunk_size=64*1024):
                            if chunk:
                                f.write(chunk)
                                
                if vid_id:
                    used_media_ids.add(vid_id)
                    GLOBAL_USED_MEDIA_IDS.add(vid_id)
                used_media_ids.add(video_url)
                GLOBAL_USED_MEDIA_IDS.add(video_url)
                
                video_paths.append(filename)
                print(f"✅ [Pexels] Video clip downloaded (ID: {vid_id}): {filename}")
                
            if len(GLOBAL_USED_MEDIA_IDS) > 500:
                to_remove = len(GLOBAL_USED_MEDIA_IDS) - 250
                for _ in range(to_remove):
                    GLOBAL_USED_MEDIA_IDS.pop()
                    
            return video_paths
    except Exception as e:
        print(f"⚠️ [Pexels] Error: {e}")
    return []

def fetch_pixabay_videos(keyword, job_id, count=1, orientation="portrait", used_media_ids=None):
    """Pixabay API se free HD stock videos download karta hai with zero-duplicate protection"""
    key = os.getenv("PIXABAY_API_KEY") or PIXABAY_API_KEY
    if not key:
        return []
        
    print(f"📥 [Pixabay] '{keyword}' ke liye video clip ({orientation}) dhoondh rahe hain...")
    v_type = "film" if orientation == "landscape" else "all"
    per_page = max(15, count * 4)
    url = f"https://pixabay.com/api/videos/?key={key}&q={requests.utils.quote(keyword)}&video_type={v_type}&per_page={per_page}"
    
    if used_media_ids is None:
        used_media_ids = set()

    try:
        res = requests.get(url, timeout=12)
        if res.status_code != 200:
            return []
        data = res.json()
        video_paths = []
        hits = data.get('hits', [])
        if hits:
            selected_hits = []
            for hit in hits:
                hit_id = str(hit.get('id', ''))
                if hit_id and (hit_id in used_media_ids or hit_id in GLOBAL_USED_MEDIA_IDS):
                    continue
                videos = hit.get('videos', {})
                best_vid = videos.get('medium') or videos.get('large') or videos.get('small')
                if not best_vid or not best_vid.get('url'):
                    continue
                if best_vid['url'] in used_media_ids or best_vid['url'] in GLOBAL_USED_MEDIA_IDS:
                    continue
                selected_hits.append(hit)
                if len(selected_hits) >= count:
                    break

            if len(selected_hits) < count:
                for hit in hits:
                    hit_id = str(hit.get('id', ''))
                    if hit_id and hit_id in used_media_ids:
                        continue
                    if hit not in selected_hits:
                        selected_hits.append(hit)
                        if len(selected_hits) >= count:
                            break

            dir_name = os.path.dirname(job_id)
            base_name = os.path.basename(job_id)

            for i, hit in enumerate(selected_hits):
                hit_id = str(hit.get('id', ''))
                videos = hit.get('videos', {})
                best_vid = videos.get('medium') or videos.get('large') or videos.get('small')
                if not best_vid or not best_vid.get('url'): continue
                video_url = best_vid['url']
                filename = os.path.join(dir_name, f"pixabay_{base_name}_{i}.mp4") if dir_name else f"pixabay_{base_name}_{i}.mp4"
                
                with requests.get(video_url, stream=True, timeout=20) as r_vid:
                    r_vid.raise_for_status()
                    with open(filename, "wb") as f:
                        for chunk in r_vid.iter_content(chunk_size=64*1024):
                            if chunk:
                                f.write(chunk)
                                
                if hit_id:
                    used_media_ids.add(hit_id)
                    GLOBAL_USED_MEDIA_IDS.add(hit_id)
                used_media_ids.add(video_url)
                GLOBAL_USED_MEDIA_IDS.add(video_url)
                
                video_paths.append(filename)
                print(f"✅ [Pixabay] Video clip downloaded (ID: {hit_id}): {filename}")
            return video_paths
    except Exception as e:
        print(f"⚠️ [Pixabay] Error: {e}")
    return []

def fetch_pinterest_pins(keyword, job_id, count=1, orientation="portrait", used_media_ids=None):
    """Pinterest HD Pins media download karta hai using gallery-dl & fail-safe API/scraper"""
    dir_name = os.path.dirname(job_id) if job_id else ""
    base_name = os.path.basename(job_id) if job_id else "pinterest_media"
    target_dir = dir_name if dir_name else "."
    
    if used_media_ids is None:
        used_media_ids = set()

    try:
        from pinterest_downloader import fetch_pinterest_photos_via_gallery_dl
        downloaded = fetch_pinterest_photos_via_gallery_dl(keyword, limit=count * 3, output_dir=target_dir)
        if downloaded:
            media_paths = []
            for p_file in downloaded:
                if p_file in used_media_ids or p_file in GLOBAL_USED_MEDIA_IDS:
                    continue
                ext = os.path.splitext(p_file)[1] or ".jpg"
                target_filename = os.path.join(target_dir, f"pinterest_{base_name}_{len(media_paths)}{ext}") if target_dir != "." else f"pinterest_{base_name}_{len(media_paths)}{ext}"
                if p_file != target_filename:
                    import shutil
                    shutil.move(p_file, target_filename)
                media_paths.append(target_filename)
                used_media_ids.add(target_filename)
                GLOBAL_USED_MEDIA_IDS.add(target_filename)
                print(f"✅ [Pinterest gallery-dl] Pin media saved: {target_filename}")
                if len(media_paths) >= count:
                    break
            if media_paths:
                return media_paths
    except Exception as e_dl:
        print(f"⚠️ [Pinterest gallery-dl fallback]: {e_dl}")

    token = os.getenv("PINTEREST_ACCESS_TOKEN") or PINTEREST_ACCESS_TOKEN
    if not token or str(token).strip() == "":
        return []
        
    print(f"📥 [Pinterest API] '{keyword}' ke liye Pins search kar rahe hain...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.pinterest.com/v5/search/pins?query={requests.utils.quote(keyword)}&page_size=15"
    
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code != 200:
            print(f"⚠️ [Pinterest] Token/API response ({res.status_code}). Skipping to next provider...")
            return []
        data = res.json()
        pins = data.get('items', [])
        media_paths = []
        if pins:
            for pin in pins:
                pin_id = str(pin.get('id', ''))
                if pin_id and (pin_id in used_media_ids or pin_id in GLOBAL_USED_MEDIA_IDS):
                    continue
                images = pin.get('images', {})
                img_url = (images.get('originals') or {}).get('url') or (images.get('1200x') or {}).get('url')
                if not img_url or img_url in used_media_ids or img_url in GLOBAL_USED_MEDIA_IDS:
                    continue
                filename = os.path.join(dir_name, f"pinterest_{base_name}_{len(media_paths)}.jpg") if dir_name else f"pinterest_{base_name}_{len(media_paths)}.jpg"
                
                img_data = requests.get(img_url, timeout=10).content
                with open(filename, "wb") as f:
                    f.write(img_data)
                if pin_id:
                    used_media_ids.add(pin_id)
                    GLOBAL_USED_MEDIA_IDS.add(pin_id)
                used_media_ids.add(img_url)
                GLOBAL_USED_MEDIA_IDS.add(img_url)
                media_paths.append(filename)
                print(f"✅ [Pinterest API] Pin media downloaded: {filename}")
                if len(media_paths) >= count:
                    break
            return media_paths
    except Exception as e:
        print(f"⚠️ [Pinterest Non-Blocking Warning]: {e}. Falling back to next provider...")
    return []

def fetch_videos(keyword, job_id, count=1, orientation="portrait", category="Random", video_type="short", topic="", used_media_ids=None):
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
            clips = fetch_pexels_videos(q_item, job_id, count=count, orientation=orientation, used_media_ids=used_media_ids)
            if clips:
                return clips
        except Exception as e_px:
            print(f"⚠️ [Pexels Query Skip]: {e_px}")
            
        try:
            clips = fetch_pixabay_videos(q_item, job_id, count=count, orientation=orientation, used_media_ids=used_media_ids)
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
                clips = fetch_pexels_videos(fallback_kw, job_id, count=count, orientation=orientation, used_media_ids=used_media_ids)
                if not clips:
                    clips = fetch_pixabay_videos(fallback_kw, job_id, count=count, orientation=orientation, used_media_ids=used_media_ids)
                if clips:
                    return clips
            except Exception:
                continue

    if is_ultra_mode:
        try:
            pins = fetch_pinterest_pins(keyword, job_id, count=count, orientation=orientation, used_media_ids=used_media_ids)
            if pins:
                return pins
        except Exception as e_p2:
            print(f"⚠️ [Pinterest Fallback Skip]: {e_p2}")

    print(f"⚠️ [Media Fetcher] No online media found for '{keyword}'. Using internal canvas background...")
    return []
