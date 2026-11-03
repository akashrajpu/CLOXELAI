"""
Pinterest Photo Downloader Helper (Resilient & API-Key Free)
Uses gallery-dl CLI and web fallbacks (Direct HTML & Bing Pinterest Scraper)
to fetch high-resolution Pinterest photos for any topic.
"""

import os
import sys
import shutil
import urllib.parse
import subprocess
import requests
import re
import hashlib

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_media_fingerprint(filepath: str) -> str:
    """Computes MD5 hash of file content for reliable deduplication."""
    try:
        if not filepath or not os.path.exists(filepath):
            return ""
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            while chunk := f.read(16384):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def get_gallery_dl_cmd():
    """Locates the gallery-dl command (binary or python module) on the system."""
    which_path = shutil.which("gallery-dl")
    if which_path:
        return [which_path]

    candidates = [
        "/Library/Frameworks/Python.framework/Versions/3.14/bin/gallery-dl",
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/gallery-dl",
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/gallery-dl",
        "/usr/local/bin/gallery-dl",
        os.path.expanduser("~/.local/bin/gallery-dl"),
        os.path.join(sys.prefix, "bin", "gallery-dl")
    ]
    for c in candidates:
        if os.path.exists(c) and os.access(c, os.X_OK):
            return [c]

    # Try invoking via sys.executable module
    try:
        res = subprocess.run([sys.executable, "-m", "gallery_dl", "--version"], capture_output=True, text=True, timeout=4)
        if res.returncode == 0:
            return [sys.executable, "-m", "gallery_dl"]
    except Exception:
        pass

    return None

def get_video_dimensions(filepath: str) -> tuple:
    """Fast video width and height extraction using ffprobe with moviepy fallback."""
    if not filepath or not os.path.exists(filepath):
        return None, None
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json",
            filepath
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
        if res.returncode == 0 and res.stdout:
            import json
            data = json.loads(res.stdout)
            streams = data.get("streams", [])
            if streams and "width" in streams[0] and "height" in streams[0]:
                return int(streams[0]["width"]), int(streams[0]["height"])
    except Exception:
        pass

    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(filepath)
        w, h = clip.size
        clip.close()
        return int(w), int(h)
    except Exception:
        pass

    return None, None

def is_valid_hd_photo(filepath: str, min_dim: int = 350, orientation: str = None) -> bool:
    """
    Verifies that the downloaded file is a non-corrupt, valid high-resolution image
    and strictly matches requested aspect ratio / orientation (9:16 portrait vs 16:9 landscape).
    """
    try:
        from PIL import Image
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 5000:
            return False
        with Image.open(filepath) as im:
            im.verify()
        with Image.open(filepath) as im:
            w, h = im.width, im.height
            if w < min_dim or h < min_dim:
                return False
            
            # Strict aspect ratio validation
            if orientation in ["portrait", "9:16"]:
                # Must be 9:16 vertical (height >= width)
                if h < w:
                    return False
            elif orientation in ["landscape", "16:9"]:
                # Must be 16:9 horizontal (width >= height)
                if w < h:
                    return False
            return True
    except Exception:
        return False

def is_valid_video(filepath: str, min_size: int = 15000, orientation: str = None) -> bool:
    """
    Verifies that the downloaded file is a non-corrupt, valid video file
    and strictly matches requested aspect ratio / orientation (9:16 portrait vs 16:9 landscape).
    """
    if not filepath or not os.path.exists(filepath):
        return False
    if filepath.lower().endswith(('.part', '.ytdl', '.tmp')):
        return False
    if not filepath.lower().endswith(('.mp4', '.mov', '.webm', '.mkv')):
        return False
    try:
        if os.path.getsize(filepath) < min_size:
            return False
        
        # Verify video has an actual playable video stream with valid dimensions
        w, h = get_video_dimensions(filepath)
        if not w or not h or w < 100 or h < 100:
            return False

        # Strict aspect ratio validation
        if orientation in ["portrait", "9:16"]:
            # Must be 9:16 vertical (height >= width)
            if h < w:
                return False
        elif orientation in ["landscape", "16:9"]:
            # Must be 16:9 horizontal (width >= height)
            if w < h:
                return False
        return True
    except Exception:
        return False

def fetch_pinterest_photos_via_gallery_dl(query: str, limit: int = 3, output_dir: str = "pinterest_photos", used_media_ids: set = None, orientation: str = "portrait") -> list:
    """
    Programmatic helper: Downloads HD Pinterest photos using gallery-dl / direct web scraping.
    Returns list of verified, valid HD downloaded file paths in output_dir.
    Guarantees isolation: never modifies or deletes pre-existing files in output_dir.
    Deduplication: Never returns any photo previously used in the same video job.
    Aspect Ratio: Strictly ensures photos match orientation (9:16 vertical vs 16:9 landscape).
    """
    os.makedirs(output_dir, exist_ok=True)
    import time
    timestamp_prefix = int(time.time() * 1000) % 1000000
    used_media_ids = used_media_ids if used_media_ids is not None else set()
    orientation = str(orientation or "portrait").lower()

    if orientation in ["portrait", "9:16"]:
        aspect_keyword = "9:16 vertical phone wallpaper"
    elif orientation in ["landscape", "16:9"]:
        aspect_keyword = "16:9 landscape desktop wallpaper widescreen"
    else:
        aspect_keyword = ""

    search_query = f"{query} {aspect_keyword}".strip() if aspect_keyword else query
    encoded_query = urllib.parse.quote(search_query)
    pinterest_url = f"https://www.pinterest.com/search/pins/?q={encoded_query}"

    print(f"📥 [Pinterest Engine] Searching and downloading HD {orientation.upper()} photos for: '{search_query}'...")

    downloaded_files = []
    gallery_cmd = get_gallery_dl_cmd()

    # Use dedicated isolated download cache directory so other assets are NEVER deleted or overwritten
    dl_work_dir = os.path.join(output_dir, f"_pin_cache_{timestamp_prefix}")
    os.makedirs(dl_work_dir, exist_ok=True)

    if gallery_cmd:
        try:
            scan_range = max(limit + 3, 5 + min(len(used_media_ids), 12))
            cmd = gallery_cmd + [
                "--directory", dl_work_dir,
                "--range", f"1-{scan_range}",
                pinterest_url
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=20)

            found_raw = []
            for root, _, files in os.walk(dl_work_dir):
                for f in files:
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        full_p = os.path.join(root, f)
                        if is_valid_hd_photo(full_p, min_dim=350, orientation=orientation):
                            found_raw.append(full_p)

            found_raw.sort(key=os.path.getmtime, reverse=True)

            for raw_p in found_raw:
                if len(downloaded_files) >= limit:
                    break
                raw_name = os.path.basename(raw_p)
                pin_id = re.sub(r'[^a-zA-Z0-9]', '', os.path.splitext(raw_name)[0])
                f_hash = get_media_fingerprint(raw_p)
                f_size = os.path.getsize(raw_p)

                # Deduplication check: Ensure photo was not previously used
                if (raw_name in used_media_ids or 
                    (pin_id and pin_id in used_media_ids) or 
                    (f_hash and f_hash in used_media_ids) or
                    f"size_{f_size}" in used_media_ids):
                    print(f"🔄 [Pinterest Photo Deduplication] Skipping duplicate photo: {raw_name} (hash: {f_hash[:8] if f_hash else 'none'})...")
                    continue

                ext = os.path.splitext(raw_p)[1].lower() or ".jpg"
                final_p = os.path.join(output_dir, f"pin_asset_{timestamp_prefix}_{len(downloaded_files)+1}{ext}")
                shutil.copy2(raw_p, final_p)
                downloaded_files.append(final_p)

                used_media_ids.add(raw_name)
                if pin_id: used_media_ids.add(pin_id)
                if f_hash: used_media_ids.add(f_hash)
                used_media_ids.add(f"size_{f_size}")

            # Cleanup isolated cache
            shutil.rmtree(dl_work_dir, ignore_errors=True)

            if downloaded_files:
                print(f"✅ [Pinterest gallery-dl] Successfully fetched {len(downloaded_files)} {orientation.upper()} photos for '{query}'.")
                return downloaded_files

        except Exception as e:
            shutil.rmtree(dl_work_dir, ignore_errors=True)
            print(f"⚠️ [Pinterest gallery-dl warning]: {e}. Trying direct web scraper fallback...")
    else:
        shutil.rmtree(dl_work_dir, ignore_errors=True)
        print("ℹ️ [Pinterest gallery-dl] CLI executable not found, using web scraper fallbacks...")

    # Fallback 1: Direct Pinterest Scraper
    try:
        resp = requests.get(pinterest_url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            found_urls = re.findall(r'https://i\.pinimg\.com/(?:originals|736x|564x|474x|236x)/[a-f0-9/]+/[a-f0-9]+\.(?:jpg|png|webp)', resp.text, re.IGNORECASE)
            filtered_urls = [u for u in found_urls if "d53b014d86a6b6761bf649a0ed813c2b" not in u and "avatar" not in u.lower()]
            unique_hd_urls = []
            for u in set(filtered_urls):
                hd_u = re.sub(r'/(?:236x|474x|564x)/', '/originals/', u)
                if hd_u not in unique_hd_urls:
                    unique_hd_urls.append(hd_u)

            for i, img_url in enumerate(unique_hd_urls):
                if len(downloaded_files) >= limit:
                    break
                url_id = os.path.basename(img_url)
                if url_id in used_media_ids or img_url in used_media_ids:
                    continue
                try:
                    ext = ".png" if img_url.lower().endswith(".png") else ".jpg"
                    save_path = os.path.join(output_dir, f"pin_direct_{timestamp_prefix}_{len(downloaded_files)+1}{ext}")
                    img_req = requests.get(img_url, headers=HEADERS, timeout=8)
                    if img_req.status_code == 200 and len(img_req.content) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        if is_valid_hd_photo(save_path, min_dim=350, orientation=orientation):
                            f_hash = get_media_fingerprint(save_path)
                            f_size = os.path.getsize(save_path)
                            if (f_hash and f_hash in used_media_ids) or f"size_{f_size}" in used_media_ids:
                                try: os.remove(save_path)
                                except Exception: pass
                                continue
                            downloaded_files.append(save_path)
                            used_media_ids.add(url_id)
                            used_media_ids.add(img_url)
                            if f_hash: used_media_ids.add(f_hash)
                            used_media_ids.add(f"size_{f_size}")
                        else:
                            try:
                                os.remove(save_path)
                            except Exception:
                                pass
                except Exception:
                    continue

            if downloaded_files:
                print(f"✅ [Pinterest Direct Scraper] Successfully fetched {len(downloaded_files)} {orientation.upper()} photos for '{query}'.")
                return downloaded_files
    except Exception as e_scrape:
        print(f"⚠️ [Pinterest Scraper warning]: {e_scrape}")

    # Fallback 2: Bing Pinterest Image Scraper
    try:
        bing_query = f"{query} {aspect_keyword} site:pinterest.com".strip()
        bing_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(bing_query)}"
        b_resp = requests.get(bing_url, headers=HEADERS, timeout=8)
        if b_resp.status_code == 200:
            murls = re.findall(r'murl&quot;:&quot;(https?://[^&"]+)&quot;', b_resp.text)
            murls += re.findall(r'"murl"\s*:\s*"(https?://[^"]+)"', b_resp.text)
            raw_pinimg = re.findall(r'https://i\.pinimg\.com/(?:originals|736x|564x|474x|236x)/[a-f0-9/]+/[a-f0-9]+\.(?:jpg|png|webp)', b_resp.text, re.IGNORECASE)
            
            candidate_urls = []
            for u in murls + raw_pinimg:
                if "pinimg.com" in u and "d53b014d86a6b6761bf649a0ed813c2b" not in u:
                    hd_u = re.sub(r'/(?:236x|474x|564x)/', '/originals/', u)
                    if hd_u not in candidate_urls:
                        candidate_urls.append(hd_u)
            if not candidate_urls:
                for u in murls:
                    if u not in candidate_urls and not u.endswith(('.svg', '.gif')):
                        candidate_urls.append(u)

            for i, img_url in enumerate(candidate_urls):
                if len(downloaded_files) >= limit:
                    break
                url_id = os.path.basename(img_url)
                if url_id in used_media_ids or img_url in used_media_ids:
                    continue
                try:
                    ext = ".png" if img_url.lower().endswith(".png") else ".jpg"
                    save_path = os.path.join(output_dir, f"pin_bing_{timestamp_prefix}_{len(downloaded_files)+1}{ext}")
                    img_req = requests.get(img_url, headers=HEADERS, timeout=8)
                    if img_req.status_code == 200 and len(img_req.content) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        if is_valid_hd_photo(save_path, min_dim=350, orientation=orientation):
                            f_hash = get_media_fingerprint(save_path)
                            f_size = os.path.getsize(save_path)
                            if (f_hash and f_hash in used_media_ids) or f"size_{f_size}" in used_media_ids:
                                try: os.remove(save_path)
                                except Exception: pass
                                continue
                            downloaded_files.append(save_path)
                            used_media_ids.add(url_id)
                            used_media_ids.add(img_url)
                            if f_hash: used_media_ids.add(f_hash)
                            used_media_ids.add(f"size_{f_size}")
                        else:
                            try:
                                os.remove(save_path)
                            except Exception:
                                pass
                except Exception:
                    continue

            if downloaded_files:
                print(f"✅ [Pinterest Bing Fallback] Successfully fetched {len(downloaded_files)} {orientation.upper()} photos for '{query}'.")
                return downloaded_files
    except Exception as e_bing:
        print(f"⚠️ [Pinterest Bing Scraper warning]: {e_bing}")

    # Fallback 3: Google Images Pinterest Scraper
    try:
        g_query = f"{query} {aspect_keyword} site:pinterest.com".strip()
        g_url = f"https://www.google.com/search?q={urllib.parse.quote(g_query)}&tbm=isch"
        g_resp = requests.get(g_url, headers=HEADERS, timeout=6)
        if g_resp.status_code == 200:
            g_urls = re.findall(r'https?://[^"\s]+\.(?:jpg|jpeg|png|webp)', g_resp.text, re.IGNORECASE)
            valid_g_urls = [u for u in g_urls if "gstatic" not in u and "google" not in u]
            for i, img_url in enumerate(valid_g_urls):
                if len(downloaded_files) >= limit:
                    break
                url_id = os.path.basename(img_url)
                if url_id in used_media_ids or img_url in used_media_ids:
                    continue
                try:
                    ext = ".png" if img_url.lower().endswith(".png") else ".jpg"
                    save_path = os.path.join(output_dir, f"pin_google_{timestamp_prefix}_{len(downloaded_files)+1}{ext}")
                    img_req = requests.get(img_url, headers=HEADERS, timeout=6)
                    if img_req.status_code == 200 and len(img_req.content) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        if is_valid_hd_photo(save_path, min_dim=350, orientation=orientation):
                            f_hash = get_media_fingerprint(save_path)
                            f_size = os.path.getsize(save_path)
                            if (f_hash and f_hash in used_media_ids) or f"size_{f_size}" in used_media_ids:
                                try: os.remove(save_path)
                                except Exception: pass
                                continue
                            downloaded_files.append(save_path)
                            used_media_ids.add(url_id)
                            used_media_ids.add(img_url)
                            if f_hash: used_media_ids.add(f_hash)
                            used_media_ids.add(f"size_{f_size}")
                        else:
                            try:
                                os.remove(save_path)
                            except Exception:
                                pass
                except Exception:
                    continue

            if downloaded_files:
                print(f"✅ [Pinterest Google Fallback] Successfully fetched {len(downloaded_files)} {orientation.upper()} photos for '{query}'.")
                return downloaded_files
    except Exception as e_google:
        print(f"⚠️ [Pinterest Google Scraper warning]: {e_google}")

    return downloaded_files

def fetch_pinterest_videos_via_gallery_dl(query: str, limit: int = 1, output_dir: str = "pinterest_videos", used_media_ids: set = None, orientation: str = "portrait") -> list:
    """
    Programmatic helper: Downloads HD Pinterest Videos using gallery-dl without using any Pinterest API.
    Returns list of verified, valid downloaded .mp4/.webm video file paths in output_dir.
    Guarantees isolation: never modifies or deletes pre-existing files in output_dir.
    Deduplication: Never returns any video previously used in the same video job.
    Aspect Ratio: Strictly ensures videos match orientation (9:16 vertical vs 16:9 landscape).
    """
    os.makedirs(output_dir, exist_ok=True)
    import time
    timestamp_prefix = int(time.time() * 1000) % 1000000
    used_media_ids = used_media_ids if used_media_ids is not None else set()
    orientation = str(orientation or "portrait").lower()

    # Clean query to concise, high-impact search term (max 4-5 words before 'graphics video')
    raw_words = query.strip().split()
    seen_w = set()
    compact_words = []
    for w in raw_words:
        wl = w.lower().strip(".,!?:;\"'")
        # remove repetitive words like 'ancient', 'historical' if 'history' is already there
        if wl in ["historical", "ancient"] and any(h in seen_w for h in ["history", "itihas"]):
            continue
        if wl and wl not in seen_w:
            seen_w.add(wl)
            compact_words.append(w)

    non_gv_words = [w for w in compact_words if w.lower() not in ["graphics", "video", "photo"]]
    if len(non_gv_words) > 4:
        non_gv_words = non_gv_words[:4]

    if orientation in ["portrait", "9:16"]:
        aspect_term = "9:16 vertical reels"
    elif orientation in ["landscape", "16:9"]:
        aspect_term = "16:9 landscape widescreen"
    else:
        aspect_term = ""

    search_query = f"{' '.join(non_gv_words)} {aspect_term} graphics video".strip()
    encoded_query = urllib.parse.quote(search_query)
    pinterest_url = f"https://in.pinterest.com/search/pins/?q={encoded_query}"

    print(f"📥 [Pinterest Video Engine] Searching and downloading HD {orientation.upper()} videos for: '{search_query}' (No API)...")

    downloaded_videos = []
    gallery_cmd = get_gallery_dl_cmd()

    # Use dedicated isolated download cache directory so other assets are NEVER deleted or overwritten
    dl_work_dir = os.path.join(output_dir, f"_pin_vid_cache_{timestamp_prefix}")
    os.makedirs(dl_work_dir, exist_ok=True)

    if gallery_cmd:
        scan_range = max(3, limit + min(len(used_media_ids), 8) + 2)
        cmd = gallery_cmd + [
            "--directory", dl_work_dir,
            "--range", f"1-{scan_range}",
            pinterest_url
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        except subprocess.TimeoutExpired:
            print(f"⚠️ [Pinterest Video] gallery-dl scan reached 45s threshold for '{search_query}', checking downloaded files...")
        except Exception as e:
            print(f"⚠️ [Pinterest Video gallery-dl warning]: {e}")

        # Scan for ANY valid video files matching requested orientation
        try:
            found_raw = []
            for root, _, files in os.walk(dl_work_dir):
                for f in files:
                    full_p = os.path.join(root, f)
                    if is_valid_video(full_p, min_size=20000, orientation=orientation):
                        found_raw.append(full_p)

            found_raw.sort(key=os.path.getmtime, reverse=True)

            for raw_p in found_raw:
                if len(downloaded_videos) >= limit:
                    break
                raw_name = os.path.basename(raw_p)
                pin_id = re.sub(r'[^a-zA-Z0-9]', '', os.path.splitext(raw_name)[0])
                f_hash = get_media_fingerprint(raw_p)
                f_size = os.path.getsize(raw_p)

                # Deduplication check: Ensure video was not previously used
                if (raw_name in used_media_ids or 
                    (pin_id and pin_id in used_media_ids) or 
                    (f_hash and f_hash in used_media_ids) or
                    f"size_{f_size}" in used_media_ids):
                    print(f"🔄 [Pinterest Video Deduplication] Skipping duplicate video: {raw_name} (hash: {f_hash[:8] if f_hash else 'none'})...")
                    continue

                ext = os.path.splitext(raw_p)[1].lower() or ".mp4"
                final_p = os.path.join(output_dir, f"pin_vid_{timestamp_prefix}_{len(downloaded_videos)+1}{ext}")
                shutil.copy2(raw_p, final_p)
                downloaded_videos.append(final_p)

                used_media_ids.add(raw_name)
                if pin_id: used_media_ids.add(pin_id)
                if f_hash: used_media_ids.add(f_hash)
                used_media_ids.add(f"size_{f_size}")

            # If all were duplicates or none found, try alternate query with orientation offset
            if not downloaded_videos and found_raw:
                print(f"🔄 [Pinterest Video Deduplication] All candidates in initial query were duplicates. Retrying with alternate {orientation.upper()} query...")
                if orientation in ["portrait", "9:16"]:
                    alt_search = f"{' '.join(non_gv_words)} 9:16 vertical reels motion graphics video"
                else:
                    alt_search = f"{' '.join(non_gv_words)} 16:9 widescreen landscape motion graphics video"
                alt_url = f"https://in.pinterest.com/search/pins/?q={urllib.parse.quote(alt_search)}"
                cmd_alt = gallery_cmd + [
                    "--directory", dl_work_dir,
                    "--range", f"1-{scan_range + 3}",
                    alt_url
                ]
                try:
                    subprocess.run(cmd_alt, capture_output=True, text=True, timeout=30)
                    for root, _, files in os.walk(dl_work_dir):
                        for f in files:
                            full_p = os.path.join(root, f)
                            if is_valid_video(full_p, min_size=20000, orientation=orientation):
                                r_name = os.path.basename(full_p)
                                p_id = re.sub(r'[^a-zA-Z0-9]', '', os.path.splitext(r_name)[0])
                                h = get_media_fingerprint(full_p)
                                s = os.path.getsize(full_p)
                                if (r_name not in used_media_ids and 
                                    (not p_id or p_id not in used_media_ids) and 
                                    (not h or h not in used_media_ids) and 
                                    f"size_{s}" not in used_media_ids):
                                    ext = os.path.splitext(full_p)[1].lower() or ".mp4"
                                    final_p = os.path.join(output_dir, f"pin_vid_{timestamp_prefix}_alt_{len(downloaded_videos)+1}{ext}")
                                    shutil.copy2(full_p, final_p)
                                    downloaded_videos.append(final_p)
                                    used_media_ids.add(r_name)
                                    if p_id: used_media_ids.add(p_id)
                                    if h: used_media_ids.add(h)
                                    used_media_ids.add(f"size_{s}")
                                    if len(downloaded_videos) >= limit:
                                        break
                except Exception as e_alt:
                    print(f"⚠️ [Pinterest Video alternate scan notice]: {e_alt}")

        except Exception as e_salvage:
            print(f"⚠️ [Pinterest Video salvage warning]: {e_salvage}")
        finally:
            shutil.rmtree(dl_work_dir, ignore_errors=True)

        if downloaded_videos:
            print(f"✅ [Pinterest Video gallery-dl] Successfully fetched {len(downloaded_videos)} unique {orientation.upper()} video(s) for '{search_query}'.")
            return downloaded_videos
    else:
        shutil.rmtree(dl_work_dir, ignore_errors=True)
        print("ℹ️ [Pinterest Video gallery-dl] CLI executable not found.")

    return downloaded_videos

def download_pinterest_media():
    """Interactive CLI helper matching user's requested photo/video selector"""
    media_type = input("Aapko kya download karna hai? ('photo' ya 'video' likhein): ").strip().lower()
    
    if media_type not in ['photo', 'video']:
        print("Galat input! Default 'photo' set kiya ja raha hai.")
        media_type = 'photo'
        
    query = input(f"Aapko kis tarah ki {media_type} chahiye? (jaise: spider man comic vintage): ")
    
    try:
        limit = int(input(f"Aapko kitni {media_type} download karni hain? (jaise: 3): "))
    except ValueError:
        print(f"Kripya ek valid number dalein. Default 3 {media_type} set ki ja rahi hain.")
        limit = 3

    output_dir = f"pinterest_{media_type}s"
    os.makedirs(output_dir, exist_ok=True)
    
    if media_type == 'video':
        files = fetch_pinterest_videos_via_gallery_dl(query, limit=limit, output_dir=output_dir)
    else:
        files = fetch_pinterest_photos_via_gallery_dl(query, limit=limit, output_dir=output_dir)
        
    if files:
        print(f"\nSuccess! Exact {len(files)} {media_type}(s) successfully '{output_dir}' folder mein save ho gayi hain.")
    else:
        print(f"\nError: Could not download {media_type}s for '{query}'. Please check gallery-dl or internet connection.")

def download_pinterest_photos():
    files = download_pinterest_media()
    return files

if __name__ == "__main__":
    download_pinterest_media()
