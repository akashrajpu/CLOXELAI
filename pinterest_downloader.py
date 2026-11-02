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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

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

def is_valid_hd_photo(filepath: str, min_dim: int = 350) -> bool:
    """Verifies that the downloaded file is a non-corrupt, valid high-resolution image."""
    try:
        from PIL import Image
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 5000:
            return False
        with Image.open(filepath) as im:
            im.verify()
        with Image.open(filepath) as im:
            if im.width >= min_dim and im.height >= min_dim:
                return True
        return False
    except Exception:
        return False

def fetch_pinterest_photos_via_gallery_dl(query: str, limit: int = 3, output_dir: str = "pinterest_photos") -> list:
    """
    Programmatic helper: Downloads HD Pinterest photos using gallery-dl / direct web scraping.
    Returns list of verified, valid HD downloaded file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    encoded_query = urllib.parse.quote(query)
    pinterest_url = f"https://www.pinterest.com/search/pins/?q={encoded_query}"

    print(f"📥 [Pinterest Engine] Searching and downloading HD photos for: '{query}'...")

    downloaded_files = []
    gallery_cmd = get_gallery_dl_cmd()

    if gallery_cmd:
        try:
            cmd = gallery_cmd + [
                "--directory", output_dir,
                "--range", f"1-{max(limit, 3)}",
                pinterest_url
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            for root, _, files in os.walk(output_dir):
                for f in files:
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        full_p = os.path.join(root, f)
                        if full_p not in downloaded_files:
                            if is_valid_hd_photo(full_p, min_dim=350):
                                downloaded_files.append(full_p)
                            else:
                                try:
                                    os.remove(full_p)
                                except Exception:
                                    pass

            downloaded_files.sort(key=os.path.getmtime, reverse=True)

            if len(downloaded_files) > limit:
                for extra in downloaded_files[limit:]:
                    try:
                        os.remove(extra)
                    except Exception:
                        pass
                downloaded_files = downloaded_files[:limit]

            if downloaded_files:
                print(f"✅ [Pinterest gallery-dl] Successfully fetched {len(downloaded_files)} photos for '{query}'.")
                return downloaded_files

        except Exception as e:
            print(f"⚠️ [Pinterest gallery-dl warning]: {e}. Trying direct web scraper fallback...")
    else:
        print("ℹ️ [Pinterest gallery-dl] CLI executable not found, using web scraper fallbacks...")

    # Fallback 1: Direct Pinterest Scraper
    try:
        resp = requests.get(pinterest_url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            found_urls = re.findall(r'https://i\.pinimg\.com/(?:originals|736x|564x|474x|236x)/[a-f0-9/]+/[a-f0-9]+\.(?:jpg|png|webp)', resp.text, re.IGNORECASE)
            # Filter out Pinterest logo / placeholder assets
            filtered_urls = [u for u in found_urls if "d53b014d86a6b6761bf649a0ed813c2b" not in u and "avatar" not in u.lower()]
            unique_hd_urls = []
            for u in set(filtered_urls):
                hd_u = re.sub(r'/(?:236x|474x|564x)/', '/originals/', u)
                if hd_u not in unique_hd_urls:
                    unique_hd_urls.append(hd_u)

            for i, img_url in enumerate(unique_hd_urls[:limit * 2]):
                if len(downloaded_files) >= limit:
                    break
                try:
                    ext = ".png" if img_url.lower().endswith(".png") else ".jpg"
                    save_path = os.path.join(output_dir, f"pinterest_pin_{len(downloaded_files)+1}{ext}")
                    img_req = requests.get(img_url, headers=HEADERS, timeout=8)
                    if img_req.status_code == 200 and len(img_req.content) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        if is_valid_hd_photo(save_path, min_dim=350):
                            downloaded_files.append(save_path)
                        else:
                            try:
                                os.remove(save_path)
                            except Exception:
                                pass
                except Exception:
                    continue

            if downloaded_files:
                print(f"✅ [Pinterest Direct Scraper] Successfully fetched {len(downloaded_files)} photos for '{query}'.")
                return downloaded_files
    except Exception as e_scrape:
        print(f"⚠️ [Pinterest Scraper warning]: {e_scrape}")

    # Fallback 2: Bing Pinterest Image Scraper
    try:
        bing_url = f"https://www.bing.com/images/search?q={encoded_query}%20site:pinterest.com"
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

            for i, img_url in enumerate(candidate_urls[:limit * 3]):
                if len(downloaded_files) >= limit:
                    break
                try:
                    ext = ".png" if img_url.lower().endswith(".png") else ".jpg"
                    save_path = os.path.join(output_dir, f"pinterest_bing_{len(downloaded_files)+1}{ext}")
                    img_req = requests.get(img_url, headers=HEADERS, timeout=8)
                    if img_req.status_code == 200 and len(img_req.content) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        if is_valid_hd_photo(save_path, min_dim=350):
                            downloaded_files.append(save_path)
                        else:
                            try:
                                os.remove(save_path)
                            except Exception:
                                pass
                except Exception:
                    continue

            if downloaded_files:
                print(f"✅ [Pinterest Bing Fallback] Successfully fetched {len(downloaded_files)} photos for '{query}'.")
                return downloaded_files
    except Exception as e_bing:
        print(f"⚠️ [Pinterest Bing Scraper warning]: {e_bing}")

    # Fallback 3: Google Images Pinterest Scraper
    try:
        g_url = f"https://www.google.com/search?q={encoded_query}+site:pinterest.com&tbm=isch"
        g_resp = requests.get(g_url, headers=HEADERS, timeout=6)
        if g_resp.status_code == 200:
            g_urls = re.findall(r'https?://[^"\s]+\.(?:jpg|jpeg|png|webp)', g_resp.text, re.IGNORECASE)
            valid_g_urls = [u for u in g_urls if "gstatic" not in u and "google" not in u]
            for i, img_url in enumerate(valid_g_urls[:limit * 2]):
                if len(downloaded_files) >= limit:
                    break
                try:
                    ext = ".png" if img_url.lower().endswith(".png") else ".jpg"
                    save_path = os.path.join(output_dir, f"pinterest_google_{len(downloaded_files)+1}{ext}")
                    img_req = requests.get(img_url, headers=HEADERS, timeout=6)
                    if img_req.status_code == 200 and len(img_req.content) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        if is_valid_hd_photo(save_path, min_dim=350):
                            downloaded_files.append(save_path)
                        else:
                            try:
                                os.remove(save_path)
                            except Exception:
                                pass
                except Exception:
                    continue

            if downloaded_files:
                print(f"✅ [Pinterest Google Fallback] Successfully fetched {len(downloaded_files)} photos for '{query}'.")
                return downloaded_files
    except Exception as e_google:
        print(f"⚠️ [Pinterest Google Scraper warning]: {e_google}")

    return downloaded_files

def download_pinterest_photos():
    query = input("Aapko kis tarah ki photo chahiye? (jaise: spider man comic vintage): ")

    try:
        limit = int(input("Aapko kitni photos download karni hain? (jaise: 3): "))
    except ValueError:
        print("Kripya ek valid number dalein. Default 3 photos set ki ja rahi hain.")
        limit = 3

    output_dir = "pinterest_photos"
    os.makedirs(output_dir, exist_ok=True)

    files = fetch_pinterest_photos_via_gallery_dl(query, limit=limit, output_dir=output_dir)
    if files:
        print(f"\nSuccess! Exact {len(files)} photos successfully '{output_dir}' folder mein save ho gayi hain.")
    else:
        print(f"\nError: Could not download photos for '{query}'. Please check gallery-dl or internet connection.")

if __name__ == "__main__":
    download_pinterest_photos()
