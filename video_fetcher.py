import requests
import os
import re
import hashlib

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "jqGZN1a4uHQFpxqdFAdVaD1l1eyjW1kzHqtdlNJ1TPkSmOEXcbAL7yhN")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "39827606-4df15a6b0c26bbef50352ef2e")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN", "")

GLOBAL_USED_MEDIA_IDS = set()
GLOBAL_USED_FILE_HASHES = set()
GLOBAL_USED_FILE_SIZES = set()

GENERIC_SLUGS = {"video", "free-video", "stock-video", "pexels", "pexels-video", "clip"}

def extract_pexels_slug(url):
    """Extracts base title slug from Pexels webpage URL stripping trailing ID numbers"""
    if not url:
        return ""
    parts = url.rstrip("/").split("/")
    last_part = parts[-1].split("?")[0]
    # Remove trailing digits like -1234567
    slug = re.sub(r'-\d+$', '', last_part).strip().lower()
    return slug

def compute_quick_file_hash(filepath):
    """Calculates MD5 hash using file size + sample chunks for instant duplicate file detection"""
    try:
        size = os.path.getsize(filepath)
        if size == 0:
            return None
        h = hashlib.md5()
        h.update(str(size).encode())
        with open(filepath, "rb") as f:
            if size <= 1024 * 1024:
                h.update(f.read())
            else:
                h.update(f.read(512 * 1024))
                f.seek(size - 512 * 1024)
                h.update(f.read(512 * 1024))
        return h.hexdigest()
    except Exception:
        return None

def fetch_pexels_videos(keyword, job_id, count=1, orientation="portrait", used_media_ids=None):
    """Pexels API se HD stock video clips download karta hai with zero-duplicate protection"""
    key = os.getenv("PEXELS_API_KEY") or PEXELS_API_KEY
    if not key:
        return []
        
    print(f"📥 [Pexels] '{keyword}' ke liye video clip ({orientation}) dhoondh rahe hain...")
    headers = {"Authorization": key}
    per_page = 40 if orientation == "landscape" else max(25, count * 4)
    
    if used_media_ids is None:
        used_media_ids = set()

    page = 1
    if used_media_ids:
        page = min(5, 1 + (len(used_media_ids) // 25))

    video_paths = []
    dir_name = os.path.dirname(job_id)
    base_name = os.path.basename(job_id)

    pages_to_query = [page]
    if page < 5:
        pages_to_query.append(page + 1)

    try:
        for current_page in pages_to_query:
            if len(video_paths) >= count:
                break
                
            url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(keyword)}&per_page={per_page}&page={current_page}&orientation={orientation}"
            try:
                res = requests.get(url, headers=headers, timeout=12)
                data = res.json() if res.status_code == 200 else {}
                videos = data.get('videos', [])
            except Exception as e_req:
                print(f"⚠️ [Pexels Page {current_page} Fetch Error]: {e_req}")
                continue

            if not videos and current_page > 1:
                continue

            for video_data in videos:
                if len(video_paths) >= count:
                    break

                vid_id = str(video_data.get('id', '')).strip()
                page_url = (video_data.get('url') or '').strip()
                slug = extract_pexels_slug(page_url)
                
                user_id = str(video_data.get('user', {}).get('id', '')).strip()
                dur = int(video_data.get('duration') or 0)
                creator_sig = f"user_{user_id}_dur_{dur}" if (user_id and dur > 0) else None

                # Pre-download duplicate checks
                if vid_id and (vid_id in used_media_ids or vid_id in GLOBAL_USED_MEDIA_IDS):
                    continue

                if page_url and (page_url in used_media_ids or page_url in GLOBAL_USED_MEDIA_IDS):
                    continue

                if slug and slug not in GENERIC_SLUGS and len(slug) > 3:
                    if slug in used_media_ids or slug in GLOBAL_USED_MEDIA_IDS:
                        continue

                if creator_sig and (creator_sig in used_media_ids or creator_sig in GLOBAL_USED_MEDIA_IDS):
                    continue

                valid_files = [vf for vf in video_data.get('video_files', []) if vf.get('link')]
                if not valid_files:
                    continue

                is_link_used = False
                for vf in valid_files:
                    link = vf.get('link', '')
                    if link and (link in used_media_ids or link in GLOBAL_USED_MEDIA_IDS):
                        is_link_used = True
                        break
                if is_link_used:
                    continue

                valid_files.sort(key=lambda x: abs(x.get('height', 720) - 720))
                best_file = valid_files[0]
                video_url = best_file['link']

                clip_idx = len(video_paths)
                temp_filename = os.path.join(dir_name, f"clip_{base_name}_{clip_idx}.mp4") if dir_name else f"clip_{base_name}_{clip_idx}.mp4"

                # Download candidate clip
                try:
                    with requests.get(video_url, stream=True, timeout=20) as r_vid:
                        r_vid.raise_for_status()
                        with open(temp_filename, "wb") as f:
                            for chunk in r_vid.iter_content(chunk_size=64*1024):
                                if chunk:
                                    f.write(chunk)
                except Exception as e_dl:
                    print(f"⚠️ [Pexels Download Error (ID: {vid_id})]: {e_dl}")
                    if os.path.exists(temp_filename):
                        try:
                            os.remove(temp_filename)
                        except Exception:
                            pass
                    continue

                # Post-download duplicate & integrity verification
                f_size = os.path.getsize(temp_filename) if os.path.exists(temp_filename) else 0
                if f_size < 1000:
                    if os.path.exists(temp_filename):
                        try:
                            os.remove(temp_filename)
                        except Exception:
                            pass
                    continue

                f_hash = compute_quick_file_hash(temp_filename)

                # Check if file size or hash matches any previously used video
                if (f_size in GLOBAL_USED_FILE_SIZES or 
                    f_hash in GLOBAL_USED_FILE_HASHES or 
                    f"size_{f_size}" in used_media_ids or 
                    (f_hash and f"hash_{f_hash}" in used_media_ids)):
                    print(f"⚠️ [Pexels Duplicate Detected] Video file matches already used footage (ID: {vid_id}, Size: {f_size} bytes). Discarding duplicate and taking next candidate...")
                    if os.path.exists(temp_filename):
                        try:
                            os.remove(temp_filename)
                        except Exception:
                            pass
                    if vid_id:
                        used_media_ids.add(vid_id)
                        GLOBAL_USED_MEDIA_IDS.add(vid_id)
                    continue

                # Candidate successfully passed all tests! Register signatures
                if vid_id:
                    used_media_ids.add(vid_id)
                    GLOBAL_USED_MEDIA_IDS.add(vid_id)
                if page_url:
                    used_media_ids.add(page_url)
                    GLOBAL_USED_MEDIA_IDS.add(page_url)
                if slug and slug not in GENERIC_SLUGS and len(slug) > 3:
                    used_media_ids.add(slug)
                    GLOBAL_USED_MEDIA_IDS.add(slug)
                if creator_sig:
                    used_media_ids.add(creator_sig)
                    GLOBAL_USED_MEDIA_IDS.add(creator_sig)
                for vf in valid_files:
                    if vf.get('link'):
                        used_media_ids.add(vf['link'])
                        GLOBAL_USED_MEDIA_IDS.add(vf['link'])

                GLOBAL_USED_FILE_SIZES.add(f_size)
                used_media_ids.add(f"size_{f_size}")
                if f_hash:
                    GLOBAL_USED_FILE_HASHES.add(f_hash)
                    used_media_ids.add(f"hash_{f_hash}")

                video_paths.append(temp_filename)
                print(f"✅ [Pexels] Fresh unique video clip downloaded (ID: {vid_id}, Size: {f_size} bytes): {temp_filename}")

        if len(GLOBAL_USED_MEDIA_IDS) > 600:
            to_remove = len(GLOBAL_USED_MEDIA_IDS) - 300
            for _ in range(to_remove):
                GLOBAL_USED_MEDIA_IDS.pop()
        if len(GLOBAL_USED_FILE_SIZES) > 600:
            to_remove = len(GLOBAL_USED_FILE_SIZES) - 300
            for _ in range(to_remove):
                GLOBAL_USED_FILE_SIZES.pop()
        if len(GLOBAL_USED_FILE_HASHES) > 600:
            to_remove = len(GLOBAL_USED_FILE_HASHES) - 300
            for _ in range(to_remove):
                GLOBAL_USED_FILE_HASHES.pop()

        return video_paths
    except Exception as e:
        print(f"⚠️ [Pexels] Error: {e}")
    return video_paths

def fetch_pixabay_videos(keyword, job_id, count=1, orientation="portrait", used_media_ids=None):
    """Pixabay API se free HD stock videos download karta hai with zero-duplicate protection"""
    key = os.getenv("PIXABAY_API_KEY") or PIXABAY_API_KEY
    if not key:
        return []
        
    print(f"📥 [Pixabay] '{keyword}' ke liye video clip ({orientation}) dhoondh rahe hain...")
    v_type = "film" if orientation == "landscape" else "all"
    per_page = max(20, count * 5)
    
    if used_media_ids is None:
        used_media_ids = set()

    page = 1
    if used_media_ids:
        page = min(5, 1 + (len(used_media_ids) // 25))

    url = f"https://pixabay.com/api/videos/?key={key}&q={requests.utils.quote(keyword)}&video_type={v_type}&per_page={per_page}&page={page}"

    try:
        res = requests.get(url, timeout=12)
        if res.status_code != 200:
            return []
        data = res.json()
        hits = data.get('hits', [])
        if not hits and page > 1:
            url_p1 = f"https://pixabay.com/api/videos/?key={key}&q={requests.utils.quote(keyword)}&video_type={v_type}&per_page={per_page}&page=1"
            res_p1 = requests.get(url_p1, timeout=12)
            if res_p1.status_code == 200:
                hits = res_p1.json().get('hits', [])

        video_paths = []
        dir_name = os.path.dirname(job_id)
        base_name = os.path.basename(job_id)

        for hit in hits:
            if len(video_paths) >= count:
                break
                
            hit_id = str(hit.get('id', '')).strip()
            page_url = (hit.get('pageURL') or '').strip()
            user_id = str(hit.get('user_id', '')).strip()
            dur = int(hit.get('duration') or 0)
            creator_sig = f"pixabay_user_{user_id}_dur_{dur}" if (user_id and dur > 0) else None

            if hit_id and (hit_id in used_media_ids or hit_id in GLOBAL_USED_MEDIA_IDS):
                continue
            if page_url and (page_url in used_media_ids or page_url in GLOBAL_USED_MEDIA_IDS):
                continue
            if creator_sig and (creator_sig in used_media_ids or creator_sig in GLOBAL_USED_MEDIA_IDS):
                continue

            videos = hit.get('videos', {})
            best_vid = videos.get('medium') or videos.get('large') or videos.get('small')
            if not best_vid or not best_vid.get('url'):
                continue
            video_url = best_vid['url']
            if video_url in used_media_ids or video_url in GLOBAL_USED_MEDIA_IDS:
                continue

            clip_idx = len(video_paths)
            filename = os.path.join(dir_name, f"pixabay_{base_name}_{clip_idx}.mp4") if dir_name else f"pixabay_{base_name}_{clip_idx}.mp4"

            try:
                with requests.get(video_url, stream=True, timeout=20) as r_vid:
                    r_vid.raise_for_status()
                    with open(filename, "wb") as f:
                        for chunk in r_vid.iter_content(chunk_size=64*1024):
                            if chunk:
                                f.write(chunk)
            except Exception as e_dl:
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception:
                        pass
                continue

            f_size = os.path.getsize(filename) if os.path.exists(filename) else 0
            if f_size < 1000:
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception:
                        pass
                continue

            f_hash = compute_quick_file_hash(filename)
            if (f_size in GLOBAL_USED_FILE_SIZES or 
                f_hash in GLOBAL_USED_FILE_HASHES or 
                f"size_{f_size}" in used_media_ids or 
                (f_hash and f"hash_{f_hash}" in used_media_ids)):
                print(f"⚠️ [Pixabay Duplicate Detected] Video file matches already used clip (ID: {hit_id}). Discarding duplicate and taking next candidate...")
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception:
                        pass
                if hit_id:
                    used_media_ids.add(hit_id)
                    GLOBAL_USED_MEDIA_IDS.add(hit_id)
                continue

            if hit_id:
                used_media_ids.add(hit_id)
                GLOBAL_USED_MEDIA_IDS.add(hit_id)
            if page_url:
                used_media_ids.add(page_url)
                GLOBAL_USED_MEDIA_IDS.add(page_url)
            if creator_sig:
                used_media_ids.add(creator_sig)
                GLOBAL_USED_MEDIA_IDS.add(creator_sig)
            used_media_ids.add(video_url)
            GLOBAL_USED_MEDIA_IDS.add(video_url)

            GLOBAL_USED_FILE_SIZES.add(f_size)
            used_media_ids.add(f"size_{f_size}")
            if f_hash:
                GLOBAL_USED_FILE_HASHES.add(f_hash)
                used_media_ids.add(f"hash_{f_hash}")

            video_paths.append(filename)
            print(f"✅ [Pixabay] Fresh unique video clip downloaded (ID: {hit_id}): {filename}")

        return video_paths
    except Exception as e:
        print(f"⚠️ [Pixabay] Error: {e}")
    return video_paths

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
                pins = fetch_pinterest_pins(search_term, job_id, count=count, orientation=orientation, used_media_ids=used_media_ids)
                if not pins:
                    pins = fetch_pinterest_pins(keyword, job_id, count=count, orientation=orientation, used_media_ids=used_media_ids)
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
        if orientation == "landscape" or str(video_type).lower() == "long":
            contextual_fallbacks.append(f"{topic.strip()} documentary scene")
            contextual_fallbacks.append(f"{topic.strip()} cinematic landscape")
    if category and category.lower() not in ["random", "all"]:
        contextual_fallbacks.append(f"{category} cinematic footage")
    if clean_words:
        contextual_fallbacks.append(clean_words[0])
    if orientation == "landscape" or str(video_type).lower() == "long":
        contextual_fallbacks.extend(["cinematic documentary landscape", "atmospheric wide angle scene", "epic landscape backdrop"])
    else:
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
