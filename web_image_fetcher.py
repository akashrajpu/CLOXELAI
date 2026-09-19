"""
Web Image Downloader Helper (Polished & Resilient)
Downloads high-resolution web images for any character or scene query.
"""

import requests
import urllib.parse
import os
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

KEYWORD_TRANSLATIONS = {
    "matribhumi": "motherland india warrior",
    "yodha": "warrior warrior king",
    "sena": "ancient army battle",
    "pratap": "Maharana Pratap warrior king",
    "samrat": "emperor king royal palace",
    "killa": "ancient fort castle",
    "yuddh": "battlefield war battle",
    "antariksh": "outer space universe galaxy",
    "dharati": "earth nature landscape",
    "shanti": "meditation peace nature",
    "himmat": "courage bravery warrior",
    "balidhan": "sacrifice honor warrior",
    "sahas": "bravery warrior hero",
    "lalkar": "battle cry warrior",
    "akash": "starry sky galaxy",
    "prithvi": "planet earth space"
}

def translate_query(query: str) -> str:
    """Translates Hinglish keywords to English for optimal web image search results."""
    words = query.lower().split()
    translated = [KEYWORD_TRANSLATIONS.get(w, w) for w in words]
    return " ".join(translated)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "563492ad6f917000010000013b5bf9583b2744799017ae70ec86ca93")

def clean_search_term(text: str) -> str:
    """Cleans search terms for Pexels and Unsplash API lookups."""
    stops = {"landscape", "wallpaper", "portrait", "background", "scene", "photo", "hd", "character"}
    words = [w for w in text.split() if w.lower() not in stops]
    return " ".join(words) if words else text

def optimize_image_for_ram(file_path: str):
    """Resizes downloaded web photo to max 1280x1280 to save server RAM memory."""
    try:
        from PIL import Image
        if os.path.exists(file_path):
            with Image.open(file_path) as img:
                if img.width > 1280 or img.height > 1280:
                    img.thumbnail((1280, 1280), Image.LANCZOS)
                    img.save(file_path, quality=88, optimize=True)
    except Exception:
        pass

def fetch_web_image(query: str, save_path: str) -> bool:
    """
    Searches and downloads a high-resolution photo for any topic/character query using Pexels Photo API, Unsplash HD, Google Images, Wikimedia & Pollinations AI.
    """
    english_query = translate_query(query)
    clean_q_term = clean_search_term(english_query)
    print(f"🔎 [Web Image Search Engine] Searching HD Photos for: '{clean_q_term}' (Original Query: '{query}')...")

    if PEXELS_API_KEY:
        try:
            p_url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(clean_q_term)}&per_page=5&orientation=landscape"
            p_res = requests.get(p_url, headers={"Authorization": PEXELS_API_KEY}, timeout=5)
            if p_res.status_code == 200:
                data = p_res.json()
                photos = data.get("photos", [])
                if photos:
                    best_photo = random.choice(photos[:3])
                    img_url = best_photo.get("src", {}).get("large2x") or best_photo.get("src", {}).get("landscape") or best_photo.get("src", {}).get("original")
                    if img_url:
                        img_req = requests.get(img_url, timeout=6)
                        if img_req.status_code == 200 and len(img_req.content) > 15000:
                            with open(save_path, "wb") as f:
                                f.write(img_req.content)
                            optimize_image_for_ram(save_path)
                            print(f"✅ [Pexels HD Photo API] Successfully downloaded: {save_path}")
                            return True
        except Exception as e_pex:
            print(f"⚠️ Pexels photo search skip: {e_pex}")

    try:
        clean_prompt = urllib.parse.quote(f"epic cinematic photo of {clean_q_term}, 8k resolution, detailed background")
        poll_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1280&height=720&nologo=true"
        u_res = requests.get(poll_url, headers=HEADERS, timeout=5)
        if u_res.status_code == 200 and len(u_res.content) > 15000:
            with open(save_path, "wb") as f:
                f.write(u_res.content)
            optimize_image_for_ram(save_path)
            print(f"✅ [Pollinations HD Engine] Successfully downloaded: {save_path}")
            return True
    except Exception as e_u:
        print(f"⚠️ Pollinations search skip: {e_u}")

    try:
        clean_q = urllib.parse.quote(f"{english_query} HD wallpaper photo")
        google_url = f"https://www.google.com/search?q={clean_q}&tbm=isch"
        res = requests.get(google_url, headers=HEADERS, timeout=4)
        if res.status_code == 200:
            import re
            img_urls = re.findall(r'https?://[^"\s]+\.(?:jpg|jpeg|png|webp)', res.text, re.IGNORECASE)
            valid_urls = [u for u in img_urls if "gstatic" not in u and "google" not in u]
            if not valid_urls:
                valid_urls = img_urls
            
            for img_url in valid_urls[:4]:
                try:
                    img_req = requests.get(img_url, headers=HEADERS, timeout=4)
                    if img_req.status_code == 200 and len(img_req.content) > 15000:
                        with open(save_path, "wb") as f:
                            f.write(img_req.content)
                        optimize_image_for_ram(save_path)
                        print(f"✅ [Google Images HD] Successfully downloaded: {save_path}")
                        return True
                except Exception:
                    continue
    except Exception as e_g:
        print(f"⚠️ Google Images search skip: {e_g}")

    try:
        wiki_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(english_query)}&gsrlimit=5&prop=imageinfo&iiprop=url&format=json"
        res = requests.get(wiki_url, headers=HEADERS, timeout=4)
        if res.status_code == 200:
            pages = res.json().get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                imageinfo = page_data.get("imageinfo", [])
                if imageinfo and imageinfo[0].get("url"):
                    img_url = imageinfo[0]["url"]
                    if img_url.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
                        img_data = requests.get(img_url, headers=HEADERS, timeout=4).content
                        if len(img_data) > 12000:
                            with open(save_path, "wb") as f:
                                f.write(img_data)
                            optimize_image_for_ram(save_path)
                            print(f"✅ [Wikimedia] Downloaded image: {save_path}")
                            return True
    except Exception as e_w:
        print(f"⚠️ Wikimedia search skip: {e_w}")

    try:
        print(f"🎨 [AI Generator Fallback] Generating exact HD image for: '{english_query}'...")
        clean_prompt = urllib.parse.quote(f"epic cinematic wallpaper photo of {english_query}, 8k resolution, detailed background")
        poll_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1280&height=720&nologo=true"
        img_data = requests.get(poll_url, headers=HEADERS, timeout=10).content
        if len(img_data) > 12000:
            with open(save_path, "wb") as f:
                f.write(img_data)
            print(f"✅ [Pollinations AI Engine] Generated exact HD image: {save_path}")
            return True
    except Exception as e_p:
        print(f"⚠️ Pollinations search skip: {e_p}")

    try:
        print(f"🎨 [Picsum HD Photo Fallback] Downloading fallback HD photo...")
        picsum_url = f"https://picsum.photos/1280/720"
        p_res = requests.get(picsum_url, headers=HEADERS, timeout=6)
        if p_res.status_code == 200 and len(p_res.content) > 15000:
            with open(save_path, "wb") as f:
                f.write(p_res.content)
            print(f"✅ [Picsum HD Photo Fallback] Successfully downloaded: {save_path}")
            return True
    except Exception as e_picsum:
        print(f"⚠️ Picsum fallback skip: {e_picsum}")

    return False

if __name__ == "__main__":
    fetch_web_image("Karna Mahabharata warrior", "test_karna_warrior.jpg")
