"""
Web Image Downloader Helper (Polished & Resilient)
Downloads high-resolution web images for any character or scene query.
"""

import requests
import urllib.parse
import os
import random
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Comprehensive Stop Words (Devanagari & Hinglish) to prevent meaningless fragments like 'यह' or 'woh' in photo searches
HINDI_STOPWORDS = {
    # Devanagari Stopwords
    "यह", "वह", "ये", "वे", "था", "थी", "थे", "है", "हैं", "हो", "हुआ", "हुई", "हुए", "होता", "होती", "होते",
    "का", "के", "की", "को", "से", "में", "ने", "पर", "और", "एक", "दो", "भी", "तो", "जो", "कर", "दिया", "लिया",
    "गया", "गई", "गए", "कि", "इस", "उस", "अपने", "अपनी", "अपना", "इन", "उन", "सकते", "सकता", "सकती", "रहा",
    "रही", "रहे", "तक", "जब", "तब", "अब", "सब", "क्या", "क्यों", "कहा", "कहते", "जैसे", "किए", "गए", "गया",
    "कहा", "वहां", "यहाँ", "किसी", "कुछ", "बहुत", "मगर", "लेकिन", "परंतु", "ताकि", "क्योंकि", "तथा", "एवं",
    # Hinglish Stopwords
    "yeh", "woh", "ye", "wo", "tha", "thi", "the", "hai", "hain", "ho", "hua", "hui", "hue", "hota", "hoti", "hote",
    "ka", "ke", "ki", "ko", "se", "me", "mein", "ne", "par", "aur", "ek", "bhi", "to", "toh", "jo", "kar", "diya",
    "liya", "gaya", "gayi", "gaye", "is", "us", "apne", "apni", "apna", "in", "un", "sakte", "sakta", "sakti",
    "raha", "rahi", "rahe", "tak", "jab", "tab", "ab", "sab", "kya", "kyon", "kaha", "kahte", "jaise", "kuch",
    "bahut", "lekin", "magar", "bina", "sirf", "wali", "wale", "wala", "mil", "sakti", "rahe", "the", "gaya"
}

# Comprehensive Concept Dictionary (Devanagari & Hinglish -> Rich English visual search keywords)
CONCEPT_MAP = {
    # History, Kings, Warriors, Battles
    "इतिहास": "ancient history historical",
    "itihaas": "ancient history historical",
    "history": "ancient history historical",
    "राजा": "ancient king emperor royal",
    "raja": "ancient king emperor royal",
    "king": "ancient king emperor royal",
    "सम्राट": "emperor royal monarch",
    "samrat": "emperor royal monarch",
    "emperor": "emperor royal monarch",
    "रानी": "royal queen princess",
    "rani": "royal queen princess",
    "queen": "royal queen princess",
    "योद्धा": "ancient warrior hero fighter",
    "yoddha": "ancient warrior hero fighter",
    "warrior": "ancient warrior hero fighter",
    "वीर": "brave heroic warrior",
    "veer": "brave heroic warrior",
    "hero": "brave heroic warrior",
    "युद्ध": "epic battlefield war combat",
    "yuddh": "epic battlefield war combat",
    "war": "epic battlefield war combat",
    "battle": "epic battlefield war combat",
    "रणभूमि": "ancient battlefield combat war",
    "ranbhoomi": "ancient battlefield combat war",
    "सेना": "ancient army soldiers warriors",
    "sena": "ancient army soldiers warriors",
    "army": "ancient army soldiers warriors",
    "soldiers": "ancient army soldiers warriors",
    "सैनिक": "brave soldiers ancient army",
    "sainik": "brave soldiers ancient army",
    "किला": "ancient majestic fort castle",
    "kila": "ancient majestic fort castle",
    "fort": "ancient majestic fort castle",
    "castle": "ancient majestic fort castle",
    "महल": "grand royal palace kingdom",
    "mahal": "grand royal palace kingdom",
    "palace": "grand royal palace kingdom",
    "तलवार": "warrior sword weapon armor",
    "talwar": "warrior sword weapon armor",
    "sword": "warrior sword weapon armor",
    "घोड़ा": "war horse stallion battle",
    "ghoda": "war horse stallion battle",
    "horse": "war horse stallion battle",
    "हाथी": "ancient war elephant royalty",
    "hathi": "ancient war elephant royalty",
    "elephant": "ancient war elephant royalty",
    "मंदिर": "ancient sacred stone temple",
    "mandir": "ancient sacred stone temple",
    "temple": "ancient sacred stone temple",
    "प्रताप": "Maharana Pratap warrior king",
    "pratap": "Maharana Pratap warrior king",
    "शिवाजी": "Chhatrapati Shivaji Maharaj king",
    "shivaji": "Chhatrapati Shivaji Maharaj king",
    "चंद्रगुप्त": "Chandragupta Maurya emperor ancient",
    "chandragupta": "Chandragupta Maurya emperor ancient",
    "मौर्य": "Maurya ancient empire India",
    "maurya": "Maurya ancient empire India",
    "चाणक्य": "Chanakya ancient royal scholar",
    "chanakya": "Chanakya ancient royal scholar",
    "अशोक": "Emperor Ashoka ancient Maurya",
    "ashoka": "Emperor Ashoka ancient Maurya",
    "हल्दीघाटी": "Haldighati battlefield battle warrior",
    "haldighati": "Haldighati battlefield battle warrior",
    "मुगल": "historical ancient medieval empire",
    "mughal": "historical ancient medieval empire",
    "साम्राज्य": "vast ancient kingdom empire",
    "samrajya": "vast ancient kingdom empire",
    "empire": "vast ancient kingdom empire",
    "kingdom": "vast ancient kingdom empire",
    "विजय": "triumphant victory celebration",
    "vijay": "triumphant victory celebration",
    "victory": "triumphant victory celebration",
    "शौर्य": "heroic valor courage bravery",
    "shaurya": "heroic valor courage bravery",
    "साहस": "courage bravery warrior",
    "sahas": "courage bravery warrior",
    "बलिदान": "sacrifice heroic honor",
    "balidan": "sacrifice heroic honor",
    "मातृभूमि": "motherland ancient india heritage",
    "matribhumi": "motherland ancient india heritage",
    "देश": "motherland india patriotism heritage",
    "desh": "motherland india patriotism heritage",
    "क्रांति": "historic freedom revolution",
    "kranti": "historic freedom revolution",
    "आजादी": "independence freedom movement",
    "azadi": "independence freedom movement",
    "अंग्रेज": "colonial historical era",
    "british": "colonial historical era",
    
    # Mythology & Divine
    "शिव": "Lord Shiva cosmic meditation Himalayas",
    "shiva": "Lord Shiva cosmic meditation Himalayas",
    "mahadev": "Lord Shiva cosmic meditation Himalayas",
    "राम": "Lord Rama divine warrior king Ayodhya",
    "rama": "Lord Rama divine warrior king Ayodhya",
    "कृष्ण": "Lord Krishna divine flute aura",
    "krishna": "Lord Krishna divine flute aura",
    "हनुमान": "Lord Hanuman mighty divine warrior",
    "hanuman": "Lord Hanuman mighty divine warrior",
    "गणेश": "Lord Ganesha divine blessing sacred",
    "ganesha": "Lord Ganesha divine blessing sacred",
    "बुद्ध": "Lord Buddha peaceful meditation golden statue",
    "buddha": "Lord Buddha peaceful meditation golden statue",
    "भगवान": "sacred divine golden deity aura",
    "bhagwan": "sacred divine golden deity aura",
    "दानव": "ancient mythical demon dark entity",
    "danav": "ancient mythical demon dark entity",
    
    # Space & Science
    "अंतरिक्ष": "deep outer space galaxy cosmos nebula",
    "antariksh": "deep outer space galaxy cosmos nebula",
    "space": "deep outer space galaxy cosmos nebula",
    "ब्रह्मांड": "infinite universe deep cosmos galaxy",
    "universe": "infinite universe deep cosmos galaxy",
    "cosmos": "infinite universe deep cosmos galaxy",
    "तारे": "starry night galaxy cosmos nebula",
    "tare": "starry night galaxy cosmos nebula",
    "stars": "starry night galaxy cosmos nebula",
    "पृथ्वी": "planet earth deep space blue planet",
    "prithvi": "planet earth deep space blue planet",
    "earth": "planet earth deep space blue planet",
    "चांद": "full glowing moon night space",
    "chand": "full glowing moon night space",
    "moon": "full glowing moon night space",
    "सूरज": "blazing sun solar flare space",
    "surya": "blazing sun solar flare space",
    "sun": "blazing sun solar flare space",
    "विज्ञान": "scientific high tech laboratory",
    "vigyan": "scientific high tech laboratory",
    "science": "scientific high tech laboratory",
    "वैज्ञानिक": "scientist research laboratory equipment",
    "scientist": "scientist research laboratory equipment",
    "रोबोट": "futuristic humanoid robot artificial intelligence",
    "robot": "futuristic humanoid robot artificial intelligence",
    "रॉकेट": "space rocket launch flame trail",
    "rocket": "space rocket launch flame trail",
    "ब्लैक होल": "mysterious black hole cosmic vortex",
    
    # Medical, Everyday, Nature
    "डॉक्टर": "medical surgeon doctor hospital theater",
    "doctor": "medical surgeon doctor hospital theater",
    "अस्पताल": "modern hospital operating room medical",
    "hospital": "modern hospital operating room medical",
    "रहस्य": "mysterious dramatic enigma cinematic",
    "rahasya": "mysterious dramatic enigma cinematic",
    "mystery": "mysterious dramatic enigma cinematic",
    "जंगल": "dense lush green rainforest nature",
    "jungle": "dense lush green rainforest nature",
    "forest": "dense lush green rainforest nature",
    "पहाड़": "majestic dramatic mountain peak landscape",
    "pahad": "majestic dramatic mountain peak landscape",
    "mountain": "majestic dramatic mountain peak landscape",
    "नदी": "scenic river flowing nature landscape",
    "nadi": "scenic river flowing nature landscape",
    "river": "scenic river flowing nature landscape",
    "समुद्र": "deep blue ocean waves cinematic",
    "samudra": "deep blue ocean waves cinematic",
    "ocean": "deep blue ocean waves cinematic",
    "खजाना": "ancient glowing golden treasure artifacts",
    "khazana": "ancient glowing golden treasure artifacts",
    "treasure": "ancient glowing golden treasure artifacts",
    "गुफा": "mysterious dark underground cavern",
    "gufa": "mysterious dark underground cavern",
    "cave": "mysterious dark underground cavern",
    "भूत": "dark eerie haunted spooky night mist",
    "bhoot": "dark eerie haunted spooky night mist",
    "horror": "dark eerie haunted spooky night mist",
    "कार": "luxury supercar vehicle dynamic motion",
    "gaadi": "luxury supercar vehicle dynamic motion",
    "car": "luxury supercar vehicle dynamic motion",
    "शहर": "modern metropolis skyline illuminated night",
    "shahar": "modern metropolis skyline illuminated night",
    "city": "modern metropolis skyline illuminated night"
}

def clean_topic_title(topic: str) -> str:
    """Fix common word splits like 'i ndians' -> 'indians' and normalize spaces."""
    if not topic:
        return "ancient cinematic"
    t = re.sub(r'\bi\s+ndia', 'india', str(topic), flags=re.IGNORECASE)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def extract_rich_scene_visual_keywords(topic: str, scene_text: str, scene_kw: str = "", scene_idx: int = 0, category: str = "") -> tuple:
    """
    Builds rich, comprehensive, multi-word descriptive queries for Background and Foreground photo downloads.
    Guarantees 'bade bade keyword' according to the script so exact photos download without tiny fragments.
    Returns: (bg_query, fg_query, scene_visual_phrase)
    """
    topic_clean = clean_topic_title(topic)
    cat_lower = str(category or "").lower()
    
    combined_raw = f"{scene_kw or ''} {scene_text or ''}"
    tokens = [t.strip('.,!?:;"\'()[]{}') for t in combined_raw.split() if t.strip('.,!?:;"\'()[]{}')]
    
    matched_concepts = []
    english_keywords = []
    
    for tok in tokens:
        tok_lower = tok.lower()
        if tok_lower in HINDI_STOPWORDS or tok in HINDI_STOPWORDS:
            continue
            
        if tok_lower in CONCEPT_MAP:
            matched_concepts.append(CONCEPT_MAP[tok_lower])
        elif tok in CONCEPT_MAP:
            matched_concepts.append(CONCEPT_MAP[tok])
        elif tok.isascii() and len(tok) >= 4 and tok.isalpha():
            if tok_lower not in {
                "this", "that", "with", "from", "have", "been", "will", "would", "could", "should",
                "what", "when", "where", "which", "there", "their", "about", "your", "they", "them",
                "more", "some", "into", "then", "than", "very", "also", "just", "like"
            }:
                english_keywords.append(tok_lower)
                
    visual_parts = []
    for concept in matched_concepts:
        for w in concept.split():
            if w.lower() not in [p.lower() for p in visual_parts]:
                visual_parts.append(w)
                if len(visual_parts) >= 6:
                    break
        if len(visual_parts) >= 6:
            break
            
    for ew in english_keywords:
        if ew.lower() not in [p.lower() for p in visual_parts]:
            visual_parts.append(ew)
            if len(visual_parts) >= 6:
                break
                
    # Fallback visual context if script didn't match known dictionary
    if not visual_parts:
        t_low = topic_clean.lower()
        if any(k in t_low or k in cat_lower for k in ["history", "war", "battle", "king", "warrior", "temple", "fort", "ancient"]):
            visual_angles = [
                ["ancient", "historic", "battlefield", "warriors", "kingdom"],
                ["grand", "royal", "palace", "fort", "ancient", "emperor"],
                ["legendary", "brave", "warrior", "hero", "sword", "army"],
                ["ancient", "sacred", "stone", "temple", "monument", "heritage"],
                ["historic", "triumphant", "victory", "empire", "statue"]
            ]
            visual_parts = visual_angles[scene_idx % len(visual_angles)]
        elif any(k in t_low or k in cat_lower for k in ["space", "universe", "galaxy", "cosmos", "science"]):
            visual_parts = ["deep", "outer", "space", "nebula", "galaxy", "stars"]
        elif any(k in t_low or k in cat_lower for k in ["cartoon", "anime", "animation", "comic"]):
            visual_parts = ["vibrant", "3d", "animated", "colorful", "cartoon", "adventure"]
        else:
            visual_parts = ["cinematic", "dramatic", "atmospheric", "detailed"]
            
    scene_visual_phrase = " ".join(visual_parts)
    
    # Context-aware suffixes
    is_cartoon = any(k in cat_lower or k in topic_clean.lower() for k in ["cartoon", "anime", "animation", "comic"])
    is_space = any(k in cat_lower or k in topic_clean.lower() for k in ["space", "galaxy", "universe", "cosmos"])
    is_history = any(k in cat_lower or k in topic_clean.lower() for k in ["history", "war", "battle", "king", "warrior", "ancient"])
    
    if is_cartoon:
        bg_suffix = "vibrant 3D colorful environment wallpaper photo"
        fg_suffix = "3D animated expressive hero character portrait"
    elif is_space:
        bg_suffix = "deep space cosmos detailed wallpaper photo"
        fg_suffix = "astronaut scientist explorer character portrait"
    elif is_history:
        bg_suffix = "ancient dramatic battlefield landscape wallpaper photo"
        fg_suffix = "brave hero warrior king armor sword character portrait"
    else:
        bg_suffix = "cinematic dramatic landscape wallpaper photo"
        fg_suffix = "detailed realistic hero character portrait"
        
    bg_query = f"{topic_clean} {scene_visual_phrase} {bg_suffix}".strip()
    fg_query = f"{topic_clean} {scene_visual_phrase} {fg_suffix}".strip()
    
    return bg_query, fg_query, scene_visual_phrase

def translate_query(query: str) -> str:
    """Translates Hindi/Hinglish keywords to English and removes stop words for optimal web image search results."""
    q = clean_topic_title(query)
    tokens = [t.strip('.,!?:;"\'()[]{}') for t in q.split() if t.strip('.,!?:;"\'()[]{}')]
    result_words = []
    for tok in tokens:
        tok_lower = tok.lower()
        if tok_lower in HINDI_STOPWORDS or tok in HINDI_STOPWORDS:
            continue
        if tok_lower in CONCEPT_MAP:
            result_words.extend(CONCEPT_MAP[tok_lower].split())
        elif tok in CONCEPT_MAP:
            result_words.extend(CONCEPT_MAP[tok].split())
        else:
            result_words.append(tok)
            
    seen = set()
    dedup = []
    for w in result_words:
        if w.lower() not in seen:
            seen.add(w.lower())
            dedup.append(w)
    return " ".join(dedup) if dedup else query

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "563492ad6f917000010000013b5bf9583b2744799017ae70ec86ca93")

def clean_search_term(text: str) -> str:
    """Cleans search terms for Pexels, Pinterest, and Unsplash lookups while maintaining rich, multi-word queries."""
    stops = {"landscape", "wallpaper", "portrait", "background", "scene", "photo", "hd", "character"}
    words = [w for w in text.split() if w.lower() not in stops]
    # Retain at least 3 descriptive words to prevent tiny 1-2 word queries
    if len(words) >= 3:
        return " ".join(words)
    return text

def optimize_image_for_ram(file_path: str) -> bool:
    """Resizes downloaded web photo and verifies it is a valid, high-resolution image. Returns True if valid."""
    try:
        from PIL import Image
        import os
        if not os.path.exists(file_path):
            return False
            
        with Image.open(file_path) as img:
            img.verify()
            
        with Image.open(file_path) as img:
            if img.width < 400 or img.height < 400:
                raise ValueError("Image is too small (likely a thumbnail or tracking pixel)")
                
            if img.width > 1280 or img.height > 1280:
                img.thumbnail((1280, 1280), Image.LANCZOS)
                img.save(file_path, quality=88, optimize=True)
        return True
    except Exception as e:
        import os
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        return False

def fetch_web_image(query: str, save_path: str) -> bool:
    """
    Searches and downloads a high-resolution photo for any topic/character query using Pinterest HD, Pexels Photo API, Unsplash HD, Google Images, Wikimedia & Pollinations AI.
    """
    import shutil
    english_query = translate_query(query)
    clean_q_term = clean_search_term(english_query)
    print(f"🔎 [Web Image Search Engine] Searching HD Photos for: '{clean_q_term}' (Original Query: '{query}')...")

    try:
        from pinterest_downloader import fetch_pinterest_photos_via_gallery_dl
        temp_p_dir = os.path.join(os.path.dirname(save_path) or ".", "pinterest_temp")
        p_files = fetch_pinterest_photos_via_gallery_dl(clean_q_term, limit=1, output_dir=temp_p_dir)
        if p_files and os.path.exists(p_files[0]):
            shutil.copy(p_files[0], save_path)
            if optimize_image_for_ram(save_path):
                print(f"✅ [Pinterest HD Engine] Successfully downloaded: {save_path}")
                return True
            else:
                print("⚠️ [Pinterest HD Engine] Downloaded file was invalid/corrupt. Falling back...")
    except Exception as e_pin:
        print(f"⚠️ Pinterest HD search skip: {e_pin}")

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
                            if optimize_image_for_ram(save_path):
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
            if optimize_image_for_ram(save_path):
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
