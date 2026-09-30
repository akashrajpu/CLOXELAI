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


def get_gallery_dl_binary():
    """Locates the gallery-dl executable on the system across common install paths."""
    which_path = shutil.which("gallery-dl")
    if which_path:
        return which_path

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
            return c
    return None


def fetch_pinterest_photos_via_gallery_dl(query: str, limit: int = 3, output_dir: str = "pinterest_photos") -> list:
    """
    Programmatic helper: Downloads HD Pinterest photos using gallery-dl / direct web scraping.
    Returns list of downloaded file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    encoded_query = urllib.parse.quote(query)
    pinterest_url = f"https://www.pinterest.com/search/pins/?q={encoded_query}"

    print(f"📥 [Pinterest Engine] Searching and downloading HD photos for: '{query}'...")

    downloaded_files = []
    gallery_binary = get_gallery_dl_binary()

    # Method 1: gallery-dl CLI execution
    if gallery_binary:
        try:
            cmd = [
                gallery_binary,
                "--directory", output_dir,
                "--range", f"1-{limit}",
                pinterest_url
            ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # Collect downloaded image files recursively from output_dir
            for root, _, files in os.walk(output_dir):
                for f in files:
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        full_p = os.path.join(root, f)
                        if full_p not in downloaded_files:
                            downloaded_files.append(full_p)

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
        print("ℹ️ [Pinterest gallery-dl] CLI executable not found in PATH, using web scraper fallbacks...")

    # Method 2: Direct Pinterest web HTML scraper fallback
    try:
        resp = requests.get(pinterest_url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            found_urls = re.findall(r'https://i\.pinimg\.com/(?:originals|736x|564x|236x)/[a-f0-9/]+/[a-f0-9]+\.(?:jpg|png|webp)', resp.text, re.IGNORECASE)
            unique_hd_urls = []
            for u in set(found_urls):
                hd_u = re.sub(r'/(?:236x|564x)/', '/736x/', u)
                if hd_u not in unique_hd_urls:
                    unique_hd_urls.append(hd_u)

            for i, img_url in enumerate(unique_hd_urls[:limit]):
                try:
                    ext = ".png" if img_url.lower().endswith(".png") else ".jpg"
                    save_path = os.path.join(output_dir, f"pinterest_pin_{i+1}{ext}")
                    img_req = requests.get(img_url, headers=HEADERS, timeout=8)
                    if img_req.status_code == 200 and len(img_req.content) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        downloaded_files.append(save_path)
                except Exception:
                    continue

            if downloaded_files:
                print(f"✅ [Pinterest Direct Scraper] Successfully fetched {len(downloaded_files)} photos for '{query}'.")
                return downloaded_files
    except Exception as e_scrape:
        print(f"⚠️ [Pinterest Scraper warning]: {e_scrape}")

    # Method 3: Bing Pinterest image search fallback
    try:
        bing_url = f"https://www.bing.com/images/search?q={encoded_query}%20site:pinterest.com"
        b_resp = requests.get(bing_url, headers=HEADERS, timeout=8)
        if b_resp.status_code == 200:
            b_urls = re.findall(r'https://i\.pinimg\.com/(?:originals|736x|564x|236x)/[a-f0-9/]+/[a-f0-9]+\.(?:jpg|png|webp)', b_resp.text, re.IGNORECASE)
            unique_b_urls = []
            for u in set(b_urls):
                hd_u = re.sub(r'/(?:236x|564x)/', '/736x/', u)
                if hd_u not in unique_b_urls:
                    unique_b_urls.append(hd_u)

            for i, img_url in enumerate(unique_b_urls[:limit]):
                try:
                    ext = ".png" if img_url.lower().endswith(".png") else ".jpg"
                    save_path = os.path.join(output_dir, f"pinterest_bing_{i+1}{ext}")
                    img_req = requests.get(img_url, headers=HEADERS, timeout=8)
                    if img_req.status_code == 200 and len(img_req.content) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        downloaded_files.append(save_path)
                except Exception:
                    continue

            if downloaded_files:
                print(f"✅ [Pinterest Bing Fallback] Successfully fetched {len(downloaded_files)} photos for '{query}'.")
                return downloaded_files
    except Exception as e_bing:
        print(f"⚠️ [Pinterest Bing Scraper warning]: {e_bing}")

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
