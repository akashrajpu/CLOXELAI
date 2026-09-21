"""
Pinterest Photo Downloader Helper (Resilient & API-Key Free)
Uses gallery-dl CLI and web fallback to fetch high-resolution Pinterest photos for any topic.
"""

import os
import sys
import shutil
import urllib.parse
import subprocess
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


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

    # Method 1: gallery-dl CLI execution
    try:
        cmd = [
            "gallery-dl",
            "--directory", output_dir,
            "--range", f"1-{limit}",
            pinterest_url
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Collect all downloaded image files recursively from output_dir
        for root, _, files in os.walk(output_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    full_p = os.path.join(root, f)
                    if full_p not in downloaded_files:
                        downloaded_files.append(full_p)

        downloaded_files.sort(key=os.path.getmtime, reverse=True)

        if len(downloaded_files) > limit:
            # Clean up extra files beyond requested limit
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

    # Method 2: Direct web image search fallback if gallery-dl did not return images
    try:
        search_api = f"https://www.pinterest.com/resource/BaseSearchResource/get/?source_url=/search/pins/?q={encoded_query}&data=%7B%22options%22%3A%7B%22query%22%3A%22{encoded_query}%22%2C%22scope%22%3A%22pins%22%7D%7D"
        resp = requests.get(search_api, headers=HEADERS, timeout=6)
        if resp.status_code == 200:
            import json
            data = resp.json()
            results = data.get("resource_response", {}).get("data", {}).get("results", [])
            for i, item in enumerate(results[:limit]):
                images = item.get("images", {})
                img_url = (images.get("orig") or images.get("736x") or images.get("564x") or {}).get("url")
                if img_url:
                    save_path = os.path.join(output_dir, f"pinterest_fallback_{i+1}.jpg")
                    img_data = requests.get(img_url, headers=HEADERS, timeout=8).content
                    if len(img_data) > 10000:
                        with open(save_path, "wb") as f:
                            f.write(img_data)
                        downloaded_files.append(save_path)
            if downloaded_files:
                print(f"✅ [Pinterest Direct Scraper] Successfully fetched {len(downloaded_files)} photos for '{query}'.")
                return downloaded_files
    except Exception as e_scrape:
        print(f"⚠️ [Pinterest Scraper warning]: {e_scrape}")

    return downloaded_files


def download_pinterest_photos():
    # User se input lena
    query = input("Aapko kis tarah ki photo chahiye? (jaise: spider man comic vintage): ")

    try:
        limit = int(input("Aapko kitni photos download karni hain? (jaise: 3): "))
    except ValueError:
        print("Kripya ek valid number dalein. Default 3 photos set ki ja rahi hain.")
        limit = 3

    output_dir = "pinterest_photos"
    
    files = fetch_pinterest_photos_via_gallery_dl(query, limit=limit, output_dir=output_dir)
    if files:
        print(f"\nSuccess! Exact {len(files)} photos successfully '{output_dir}' folder mein save ho gayi hain.")
    else:
        print(f"\nError: Could not download photos for '{query}'. Please check gallery-dl or internet connection.")


if __name__ == "__main__":
    download_pinterest_photos()
