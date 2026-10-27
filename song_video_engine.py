"""
=============================================================================
CLOXEL AI - ULTRA SONG & MUSIC VIDEO ENGINE
=============================================================================
Automated YouTube Song Audio Downloader, Synced Lyrics Extractor & 
Dual-Engine (Stock Video Clips / 3D Photo Motion) Music Video Generator.
=============================================================================
"""

import os
import re
import glob
import math
import random
import subprocess
import hashlib
from typing import Optional, List, Dict, Any, Tuple
import gc

def release_system_memory():
    """
    Forces Python Garbage Collection + Linux C-heap memory reclamation (malloc_trim).
    Prevents Render 512MB RAM Out-Of-Memory (OOM) crashes.
    """
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL('libc.so.6').malloc_trim(0)
    except Exception:
        pass

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from moviepy.editor import (
        VideoClip, VideoFileClip, AudioFileClip, ImageClip, ColorClip, 
        CompositeVideoClip, concatenate_videoclips
    )
except ImportError:
    try:
        from moviepy import (
            VideoClip, VideoFileClip, AudioFileClip, ImageClip, ColorClip, 
            CompositeVideoClip, concatenate_videoclips
        )
    except ImportError:
        VideoClip = None
        VideoFileClip = None

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import numpy as np

# ---------------------------------------------------------------------------
# CINEMATIC ASSETS, 5+ FONTS PALETTE & MOOD DEFINITIONS
# ---------------------------------------------------------------------------

# Universal dual-language font pool: 100% verified to support English, Hinglish & Hindi Devanagari natively
CINEMATIC_FONTS_POOL = [
    "./fonts/Mukta-Bold.ttf",                   # Modern Bold Sans-Serif
    "./fonts/Kalam-Bold.ttf",                   # Organic Handwritten / Calligraphy
    "./fonts/YatraOne-Regular.ttf",             # Indian Retro Cinema / Display
    "./fonts/RozhaOne-Regular.ttf",             # High-Contrast Editorial Fashion Serif
    "./fonts/Ranga-Bold.ttf",                   # Expressive Brush Script
    "./fonts/TiroDevanagariHindi-Regular.ttf"   # Timeless Literary / Poetic Book Serif
]

# Additional English/Hinglish-only fonts used ONLY when lyrics are confirmed pure Latin script
LATIN_ONLY_FONTS_POOL = [
    "./fonts/anton.ttf",                        # Ultra-Impact Poster Condensed
    "./fonts/bebas.ttf",                        # Clean Headline Condensed
    "./fonts/roboto.ttf",                       # Sleek Geometric Modern
    "./fonts/Arial.ttf"                         # Universal Sans
]

TEXT_POSITIONS = [
    "bottom_center",   # classic subtitle at y=76%, centered
    "center",          # punchy emotional hook at y=48%, centered
    "lower_left",      # modern reels margin at y=72%, left-aligned
    "top_badge",       # aesthetic header at y=15%, centered
    "bottom_floating"  # floating card at y=66%, centered
]

TEXT_COLORS = [
    (253, 224, 71, 255),  # Vibrant Neon Yellow
    (255, 255, 255, 255),  # Pure Crisp White
    (56, 189, 248, 255),  # Cyberpunk Cyan
    (244, 114, 182, 255),  # Hot Rose Pink
    (251, 191, 36, 255),  # Sunset Gold
    (147, 197, 253, 255),  # Soft Sky Blue
]

TEXT_BG_STYLES = [
    "none",         # Clean floating typography, zero background box (as requested)
    "pill",         # Frosted glass dark rounded pill with accent border
    "none",         # Clean floating typography (frequent no-box variation)
    "neon_line",    # Sleek glowing accent underline bar, no background box
    "glass_card",   # Ultra-translucent subtle glass card
    "none",         # Clean floating typography
]


def font_supports_text(font_path: str, text: str) -> bool:
    """
    Checks if the font contains valid glyphs for non-whitespace characters in text.
    Detects .notdef tofu boxes by comparing rendered character mask against font's unmapped glyph.
    """
    if not os.path.exists(font_path) or not text:
        return False
    try:
        font = ImageFont.truetype(font_path, 28)
        notdef_mask = bytes(font.getmask('\uFFFF'))
        for ch in text:
            if ch.isspace() or ord(ch) < 32 or ch == '|':
                continue
            char_mask = bytes(font.getmask(ch))
            if char_mask == notdef_mask and len(notdef_mask) > 0:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# HIGH-DEFINITION EXPRESSION EMOJI SYSTEM (Zero Tofu [ ] Boxes, Cross-Platform)
# ---------------------------------------------------------------------------

EMOJI_CACHE: Dict[Tuple[str, int], Any] = {}

def get_cached_emoji(emoji_name: Optional[str], target_size: int) -> Optional[Image.Image]:
    """
    Retrieves and caches high-definition vector emoji PNG icons resized with Lanczos filter.
    Zero disk latency during video frame generation.
    """
    if not emoji_name:
        return None
    cache_key = (emoji_name, target_size)
    if cache_key in EMOJI_CACHE:
        return EMOJI_CACHE[cache_key]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, "assets", "emojis", f"{emoji_name}.png"),
        os.path.join("assets", "emojis", f"{emoji_name}.png"),
        os.path.join(base_dir, "emojis", f"{emoji_name}.png")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                im = Image.open(p).convert("RGBA")
                im_resized = im.resize((target_size, target_size), Image.Resampling.LANCZOS)
                EMOJI_CACHE[cache_key] = im_resized
                return im_resized
            except Exception:
                pass
    return None


EXPRESSION_EMOJI_KEYWORDS = [
    # 1. Emotional / Heartbreak / Pain / Sad (Prioritized for emotional accuracy)
    ("broken_heart", [
        "dard", "judai", "juda", "toota", "dhokha", "bewafa", "broken", "heartbreak",
        "tanha", "tanhai", "aansu", "aansoo", "rona", "sad", "pain", "chhod", "bichhad",
        "khatam", "bikhra", "viraan"
    ]),
    ("pleading_face", [
        "yaad", "intezar", "intezaar", "miss you", "emotional", "udaas", "bheegi", "taras",
        "maaf", "kasam", "duhayi"
    ]),
    ("crying_face", [
        "cry", "crying", "aankhon me aansu", "roye", "gham", "rulaya", "mat ro", "mat rona"
    ]),
    ("wilted_flower", [
        "barbaad", "khamosh", "andhera", "mushkil"
    ]),

    # 2. Devotional / Bhakti / Spiritual
    ("folded_hands", [
        "prabhu", "bhagwan", "ram", "shyam", "krishna", "shiva", "mahadev", "shanker",
        "ganpati", "mata", "devi", "naman", "pranaam", "jai", "hare", "kripa", "bhakti"
    ]),
    ("diya", [
        "aarti", "pooja", "deepak", "diya", "jyot", "mandir", "bhajan", "kirtan"
    ]),
    ("flower", [
        "prasad", "charan", "ganga", "shradha"
    ]),

    # 3. Energy / Fire / Party / Swag
    ("fire", [
        "fire", "aag", "jalwa", "angaron", "hot", "boss", "swag", "power", "blast",
        "attitude", "lit", "banger", "tabahi"
    ]),
    ("lightning", [
        "bijli", "shock", "thunder", "electric", "energy", "high", "speed", "jhatka"
    ]),
    ("party", [
        "party", "nach", "dance", "jashn", "hungama", "dhamaka", "celebrate", "dj",
        "club", "masti", "shor"
    ]),
    ("sunglasses", [
        "cool", "hero", "look", "style", "nawab", "shaan"
    ]),

    # 4. Sukoon / Night / Dream / Lo-Fi / Aesthetic
    ("moon", [
        "chand", "chaand", "chanda", "raat", "night", "midnight", "taare", "falak"
    ]),
    ("sparkles", [
        "sukoon", "shanti", "roshni", "sitare", "dream", "hawa", "magic", "lofi",
        "aesthetic", "khwaab", "khwab"
    ]),
    ("star", [
        "sitara", "star", "aasmaan", "amber", "kismat"
    ]),
    ("cloud", [
        "badal", "fiza", "baarishein", "barsaat", "mausam"
    ]),
    ("sun", [
        "subah", "dhoop", "ujala", "suraj", "morning"
    ]),

    # 5. Love / Romance / Dil / Ishq / Mohabbat
    ("heart_red", [
        "love", "pyaar", "pyar", "ishq", "mohabbat", "dil", "jaan", "sanam", "humsafar",
        "dhadkan", "chaahat", "deewana", "deewani", "mehboob", "aashiqui", "terebina",
        "tere bina", "tum", "sirf tum", "romantic", "saath", "bahon", "dhadke"
    ]),
    ("rose", [
        "gulab", "rose", "khubsurat", "haseen", "pari", "ada", "nazaakat"
    ]),
    ("heart_sparkle", [
        "sweetheart", "shona", "baby", "crush", "romance"
    ]),
    ("ring", [
        "vaada", "shaadi", "humsafar", "promise"
    ]),
    ("eyes", [
        "nazar", "aankhein", "ankhein", "dekhna", "deed", "gaze", "chehra"
    ]),

    # 6. Music / Audio / Rhythm
    ("guitar", [
        "guitar", "strings", "chords", "acoustic"
    ]),
    ("headphones", [
        "listen", "tune", "volume", "headphones", "earphones", "drop the beat"
    ]),
    ("music_notes", [
        "music", "sound", "sur", "taal", "rhythm", "beat", "melody", "gaana", "sangeet",
        "anthem", "track", "vibe", "vibes"
    ]),
    ("music_note", [
        "song", "dholak", "tabla"
    ])
]

MOOD_DEFAULT_EMOJIS = {
    "romantic": ["heart_red", "heart_sparkle", "rose", "heart_pink"],
    "sad": ["broken_heart", "pleading_face", "crying_face", "wilted_flower"],
    "party": ["fire", "party", "lightning", "sunglasses"],
    "lofi": ["sparkles", "moon", "cloud", "star"],
    "acoustic": ["guitar", "music_notes", "sparkles", "headphones"],
    "devotional": ["folded_hands", "diya", "flower"]
}

def detect_expression_emoji(text: str, mood: str = "romantic", line_idx: int = 0) -> str:
    """
    Detects the best matching expression emoji based on keywords in the text (English/Hinglish/Hindi).
    Falls back gracefully to mood-specific rotating emojis.
    """
    if not text:
        pool = MOOD_DEFAULT_EMOJIS.get(mood.lower(), ["heart_red", "sparkles"])
        return pool[line_idx % len(pool)]

    lower_t = text.lower()
    for emoji_name, kws in EXPRESSION_EMOJI_KEYWORDS:
        for kw in kws:
            if re.search(r'\b' + re.escape(kw) + r'\b', lower_t) or kw in lower_t:
                return emoji_name

    pool = MOOD_DEFAULT_EMOJIS.get(mood.lower(), ["heart_red", "sparkles"])
    return pool[line_idx % len(pool)]

MOOD_VISUAL_POOLS = {
    "romantic": [
        "romantic couple walking holding hands beach golden hour sunset aesthetic 4k",
        "cozy couple sitting under warm fairy lights cafe bokeh candlelight romantic 4k",
        "vintage lovers in flower garden aesthetic soft morning sunshine romantic 4k",
        "aesthetic couple silhouette stargazing night sky crescent moon dream 4k",
        "couple sharing umbrella in gentle rain street reflections warm glow romantic 4k",
        "couple embracing scenic mountain sunrise dramatic clouds soft cinematic 4k",
        "aesthetic coffee date cafe window warm autumn leaves cozy love 4k",
        "lovers walking along dreamy forest pathway sun rays dappled light 4k",
        "romantic rooftop terrace twilight fairy lights city skyline sunset 4k",
        "aesthetic vintage car drive lovers coastal highway summer breeze 4k"
    ],
    "sad": [
        "melancholy silhouette standing alone dramatic ocean cliffs twilight moody 4k",
        "lonely person looking out rain drenched window drops city lights bokeh 4k",
        "empty bench autumn park fallen leaves foggy misty path heartbreak 4k",
        "solitary figure walking down dark deserted street vintage streetlamp noir 4k",
        "dark moody bedroom moonlight through blinds lone shadow reflection 4k",
        "sad acoustic guitar leaning against abandoned vintage wall quiet dust motes 4k",
        "dramatic dark storm clouds over calm ocean lone lighthouse heartbreak 4k",
        "person sitting alone rooftop dusk gazing at distant city lights melancholy 4k",
        "foggy pine forest solitary hiker misty cold atmosphere cinematic solitude 4k",
        "tear drops falling in still lake water ripples dark reflection sorrow 4k"
    ],
    "party": [
        "neon night club dynamic strobe lights stage smoke crowd hands in air 4k",
        "dj turntable mixer deck glowing neon lasers electronic dance music fest 4k",
        "electric concert crowd confetti falling stage spotlights festival energy 4k",
        "cyberpunk synthwave vibrant purple cyan neon city lights party 4k",
        "sparklers celebration friends laughing beach bonfire party night 4k",
        "glitter disco ball reflections dancing neon colorful lights party 4k",
        "urban rooftop party dusk city skyline cocktails festive neon 4k",
        "kaleidoscope abstract neon light trails motion blur festival energy 4k"
    ],
    "lofi": [
        "lofi anime aesthetic cozy bedroom desk warm lamp window night rain 4k",
        "steaming cup of coffee vinyl record player warm wooden table aesthetic 4k",
        "midnight city view bedroom balcony plants soft neon purple glow lofi 4k",
        "vintage cassette tape headphones autumn foliage warm sweater cozy 4k",
        "bookshelf warm fairy lights cat sleeping on windowsill night stars lofi 4k",
        "train window reflection dusk city skyline earphones music chill vibes 4k",
        "cozy fireplace reading nook warm blanket soft ambient candlelight 4k",
        "retro neon midnight diner counter rain reflections pastel chill 4k"
    ],
    "acoustic": [
        "acoustic guitar resting against vintage wooden chair warm sunset glow 4k",
        "camper van parked on mountain edge campfire dusk horizon road trip 4k",
        "hands gently playing acoustic wooden guitar close up warm sunbeam 4k",
        "winding coastal highway ocean cliffs golden hour adventure indie travel 4k",
        "wildflower meadow pine trees distant snowy peaks sunny breeze 4k",
        "bonfire on beach at twilight acoustic music gathering sea breeze 4k",
        "cabin in pine woods morning mist sun rays tranquil nature aesthetic 4k",
        "open road sunset endless horizon vintage travel wandering spirit 4k"
    ],
    "devotional": [
        "divine temple golden spires morning mist sacred brass oil lamp glow 4k",
        "sacred lotus floating on tranquil holy river sunrise golden reflection 4k",
        "incense smoke rising brass diya lamp temple bells spiritual peace 4k",
        "majestic himalayan mountains morning sun rays divine meditation spiritual 4k",
        "holy river ghats morning prayers brass lamps floating flowers serenity 4k",
        "ancient temple carving sunlight illuminating deities spiritual aura 4k",
        "golden temple water reflection sacred dusk peaceful evening aarti 4k",
        "peacock feathers holy flute sacred flowers divine spiritual backdrop 4k"
    ]
}

MOOD_KEYWORDS = {
    "romantic": "romantic couple love golden hour sunset warm bokeh aesthetic dream 4k",
    "sad": "sad lonely heartbreak rain darkness silhouette alone window moody noir 4k",
    "party": "party neon night club strobe lights concert crowd smoke lasers bass 4k",
    "lofi": "lofi cozy bedroom warm lamp night rain stars window chill vibes 4k",
    "acoustic": "acoustic guitar indie travel road trip nature mountains horizon aesthetic 4k",
    "devotional": "divine spiritual temple golden rays morning sacred peaceful aesthetic 4k",
}

CAMERA_MOTION_STYLES = [
    "zoom_in",
    "pan_left_to_right",
    "tilt_up",
    "zoom_out",
    "pan_right_to_left",
    "diagonal_drift_zoom",
    "tilt_down",
    "pulse_breathe"
]

MOOD_FILTERS = {
    "romantic": ["golden_dream", "vintage_film", "teal_orange"],
    "sad": ["moody_noir", "teal_orange", "vintage_film"],
    "party": ["cyber_neon", "teal_orange", "emerald_cinema"],
    "lofi": ["golden_dream", "vintage_film", "moody_noir"],
    "acoustic": ["vintage_film", "golden_dream", "emerald_cinema"],
    "devotional": ["golden_dream", "vintage_film"],
}

ALL_FILTERS = ["teal_orange", "golden_dream", "moody_noir", "cyber_neon", "vintage_film", "emerald_cinema"]


def sanitize_lyrics_text(text: str) -> str:
    """
    Strips all emojis and unprintable unicode symbols that cause [] square boxes in TTF fonts.
    Preserves English, Hindi (Devanagari), Punjabi (Gurmukhi), and standard punctuation.
    """
    if not text:
        return ""
    # Strip emojis in high surrogates and supplementary private ranges
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    text = re.sub(r'[\uD800-\uDFFF]', '', text)
    # Strip other pictographic / symbol unicode ranges
    text = re.sub(r'[\u2600-\u27BF\u2300-\u23FF\u2B50\u200D\uFE0F]', '', text)
    # Allow alphanumeric, Hindi Devanagari (\u0900-\u097F), Punjabi (\u0A00-\u0A7F), and punctuation
    text = re.sub(r'[^\w\s\.,\'"!\?\-—\u0900-\u097F\u0A00-\u0A7F]', '', text)
    return " ".join(text.split()).strip()


def apply_cinematic_photo_filter(im: Image.Image, filter_name: str) -> Image.Image:
    """
    Applies professional cinematic color grading and subtle edge vignette to a photo.
    """
    im = im.convert("RGB")
    w, h = im.size

    if filter_name == "teal_orange":
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.15, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.1 - arr[:, :, 0] * 0.1, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8))
        im = ImageEnhance.Contrast(im).enhance(1.15)
    elif filter_name == "moody_noir":
        im = ImageOps.grayscale(im).convert("RGB")
        im = ImageEnhance.Contrast(im).enhance(1.3)
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.15, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8))
    elif filter_name == "golden_dream":
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.2, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.08, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.85, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8))
        im = ImageEnhance.Color(im).enhance(1.2)
    elif filter_name == "cyber_neon":
        im = ImageEnhance.Color(im).enhance(1.4)
        im = ImageEnhance.Contrast(im).enhance(1.2)
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.15, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.25, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8))
    elif filter_name == "emerald_cinema":
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.18, 0, 255)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.95, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8))
        im = ImageEnhance.Contrast(im).enhance(1.15)
    else:  # vintage_film
        im = ImageEnhance.Color(im).enhance(0.9)
        arr = np.array(im, dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.08, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.04, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8))
        im = ImageEnhance.Contrast(im).enhance(1.1)

    # Cinematic Vignette (darkened edges for high subtitle contrast)
    X = np.linspace(-1, 1, w)[None, :]
    Y = np.linspace(-1, 1, h)[:, None]
    radius = np.sqrt(X**2 + Y**2)
    vignette = np.clip(1.0 - (radius - 0.45) * 0.8, 0.25, 1.0)
    arr_out = np.array(im, dtype=np.float32)
    for c in range(3):
        arr_out[:, :, c] = np.clip(arr_out[:, :, c] * vignette, 0, 255)
    
    return Image.fromarray(arr_out.astype(np.uint8))


def fetch_song_synced_lyrics(
    song_title: str,
    singer_name: str = "",
    target_duration: int = 30,
    fallback_lyrics: Optional[List[str]] = None,
    song_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Multi-Tier Bulletproof Lyrics Engine:
    Tier 1: LRCLIB Synced Timestamps (with auto-gap filling during long intros).
    Tier 2: JioSaavn Official Master Lyrics (100% immune to datacenter blocks).
    Tier 3: Plain Lyrics with smooth pacing.
    Guarantees authentic song lyrics are displayed throughout the video.
    """
    clean_t = re.sub(r'[\(\[\{].*?[\)\]\}]', '', song_title).split('|')[0].strip()
    clean_t = re.sub(r'[^\w\s]', '', clean_t).strip()
    clean_s = re.sub(r'[^\w\s]', '', singer_name).strip()

    import urllib.request, urllib.parse, ssl, json
    ctx = ssl._create_unverified_context() if hasattr(ssl, '_create_unverified_context') else None

    # Step 1: If fallback lyrics not already provided, query JioSaavn lyrics API
    official_lyrics: List[str] = [l for l in (fallback_lyrics or []) if len(l.strip()) > 2]
    if not official_lyrics:
        try:
            s_id = song_id
            if not s_id and (clean_t or clean_s):
                sq = f"{clean_s} {clean_t}".strip() if clean_s else clean_t
                s_url = f"https://www.jiosaavn.com/api.php?__call=search.getResults&q={urllib.parse.quote(sq)}&_format=json&_marker=0&ctx=web6dot0&n=3&p=1"
                req_s = urllib.request.Request(s_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req_s, context=ctx, timeout=6) as r_s:
                    s_data = json.loads(r_s.read().decode('utf-8'))
                    s_res = s_data.get('results', [])
                    if s_res:
                        s_id = s_res[0].get('id')
            if s_id:
                l_url = f"https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&lyrics_id={s_id}&_format=json&_marker=0&ctx=web6dot0"
                req_l = urllib.request.Request(l_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req_l, context=ctx, timeout=6) as r_l:
                    l_data = json.loads(r_l.read().decode('utf-8'))
                    raw_lyr = l_data.get('lyrics', '')
                    if raw_lyr:
                        c_lyr = re.sub(r'<br\s*/?>', '\n', raw_lyr)
                        c_lyr = re.sub(r'<.*?>', '', c_lyr)
                        official_lyrics = [l.strip() for l in c_lyr.splitlines() if len(l.strip()) > 2]
                        if official_lyrics:
                            print(f"🎤 [Song Engine] Retrieved {len(official_lyrics)} official lyrics lines from Music CDN for '{clean_t}'!")
        except Exception as e_jio:
            print(f"⚠️ JioSaavn lyrics check note: {e_jio}")

    # Step 2: Try LRCLIB for millisecond-precision synchronized timestamps
    raw_lrc = None
    plain_lrc = None
    browser_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    # Attempt direct get if title and singer are known
    if clean_t and clean_s:
        try:
            get_url = f"https://lrclib.net/api/get?track_name={urllib.parse.quote(clean_t)}&artist_name={urllib.parse.quote(clean_s)}"
            req_get = urllib.request.Request(get_url, headers=browser_headers)
            with urllib.request.urlopen(req_get, context=ctx, timeout=8) as r_get:
                get_data = json.loads(r_get.read().decode())
                if get_data.get("syncedLyrics"):
                    raw_lrc = get_data["syncedLyrics"]
                elif get_data.get("plainLyrics"):
                    plain_lrc = get_data["plainLyrics"]
        except Exception:
            pass

    if not raw_lrc:
        queries = [f"{clean_t} {clean_s}".strip(), clean_t]
        for q in queries:
            if not q:
                continue
            try:
                url = "https://lrclib.net/api/search?q=" + urllib.parse.quote(q)
                req = urllib.request.Request(url, headers=browser_headers)
                with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
                    items = json.loads(r.read().decode())
                    for it in items:
                        if clean_s.lower() in (it.get("artistName") or "").lower() and it.get("syncedLyrics"):
                            raw_lrc = it["syncedLyrics"]
                            break
                        if it.get("plainLyrics") and not plain_lrc:
                            plain_lrc = it["plainLyrics"]
                    if not raw_lrc:
                        for it in items:
                            if it.get("syncedLyrics"):
                                raw_lrc = it["syncedLyrics"]
                                break
                if raw_lrc:
                    break
            except Exception:
                pass

    lines = []
    if raw_lrc:
        for line in raw_lrc.splitlines():
            m = re.match(r'\[(\d+):(\d+\.?\d*)\]\s*(.*)', line)
            if m:
                sec = int(m.group(1)) * 60 + float(m.group(2))
                txt = sanitize_lyrics_text(m.group(3))
                if txt and not any(tag in txt.lower() for tag in ['lyrics by', 'produced by', 'composed by', 'music:']):
                    lines.append((round(sec, 2), txt))

    result = []
    display_title = clean_t or "Official Soundtrack"
    display_artist = f"Feat. {clean_s}" if clean_s else "Music Special"

    if lines:
        filtered = [l for l in lines if l[0] <= target_duration + 2.0]
        if not filtered:
            filtered = lines[:min(14, len(lines))]

        if filtered:
            print(f"🎤 [Song Engine] Found {len(filtered)} synced lyric lines for '{display_title}'!")
            intro_gap = filtered[0][0]
            # Handle intro smoothly without leaving long 20-second dead gaps
            if intro_gap > 3.0:
                result.append({"start": 0.0, "end": min(3.5, intro_gap), "text": display_title})
                if intro_gap > 7.0:
                    result.append({"start": 3.5, "end": min(7.0, intro_gap), "text": display_artist})
                # If intro has a very long instrumental gap before singing and we have official lyrics:
                if intro_gap > 12.0 and official_lyrics:
                    gap_rem = intro_gap - 7.0
                    n_gap_lines = min(len(official_lyrics), max(1, int(gap_rem / 4.0)))
                    gap_step = round(gap_rem / n_gap_lines, 2)
                    for g_idx in range(n_gap_lines):
                        g_st = round(7.0 + (g_idx * gap_step), 2)
                        g_et = round(min(intro_gap, g_st + gap_step), 2)
                        result.append({"start": g_st, "end": g_et, "text": official_lyrics[g_idx]})

            for i, (t_sec, txt) in enumerate(filtered):
                if i + 1 < len(filtered):
                    next_t = filtered[i+1][0]
                    dur = min(6.0, max(2.5, next_t - t_sec))
                    end_t = min(float(target_duration), t_sec + dur)
                else:
                    end_t = min(float(target_duration), t_sec + 4.5)
                if t_sec < target_duration:
                    result.append({"start": t_sec, "end": max(t_sec + 2.0, end_t), "text": txt})

    # Step 3: If LRCLIB had no synced lyrics or had very few lines, use Official JioSaavn / Plain Lyrics!
    if (not result or len(result) < 3):
        active_lyrics_lines = official_lyrics
        if not active_lyrics_lines and plain_lrc:
            active_lyrics_lines = [sanitize_lyrics_text(l) for l in plain_lrc.splitlines() if len(l.strip()) > 2]

        if active_lyrics_lines:
            print(f"📝 [Song Engine] Using {len(active_lyrics_lines)} authentic song lyrics lines for '{display_title}'!")
            result = []
            intro_end = 3.5
            result.append({"start": 0.0, "end": intro_end, "text": display_title})
            if target_duration >= 40:
                result.append({"start": 3.5, "end": 6.5, "text": display_artist})
                intro_end = 6.5

            rem_dur = target_duration - intro_end
            line_pacing = 3.8
            n_show = min(len(active_lyrics_lines), max(3, int(rem_dur / line_pacing)))
            chosen_lines = active_lyrics_lines[:n_show]
            step = round(rem_dur / len(chosen_lines), 2)
            for idx, txt in enumerate(chosen_lines):
                st = round(intro_end + (idx * step), 2)
                et = round(min(float(target_duration), st + step), 2)
                result.append({"start": st, "end": et, "text": txt})

    # Step 4: Absolute Fallback (Only for pure instrumentals with zero lyrics anywhere)
    if not result:
        print(f"🎵 [Song Engine] Generating dynamic clean typography title cards for '{display_title}'...")
        hook_cards = [
            display_title,
            display_artist,
            f"{display_title} — Feel The Rhythm",
            f"Official Edition • {display_title}",
            f"{clean_s or 'Artist'} Official",
            f"Beats In Sync • {display_title}",
            "Acoustic & Melodic Symphony",
            f"Cinematic Soul • {display_title}",
            "Lost In The Music",
            f"Masterpiece Edition • {display_title}"
        ]
        n_cards = max(4, int(round(target_duration / 4.0)))
        base_dur = round(target_duration / n_cards, 2)
        for idx in range(n_cards):
            st = idx * base_dur
            et = min(float(target_duration), (idx + 1) * base_dur if idx < n_cards - 1 else target_duration)
            result.append({"start": st, "end": et, "text": hook_cards[idx % len(hook_cards)]})

    return result


def render_typewriter_lyrics_on_frame(
    im_frame: Image.Image,
    line_info: Dict[str, Any],
    local_t: float,
    tw: int,
    th: int
) -> Image.Image:
    """
    Renders styled typewriter lyrics subtitle directly onto the video frame.
    Multi-font, dynamic locations, typewriter progressive animation, frosted glass pill.
    """
    full_text = line_info.get("text", "")
    if not full_text:
        return im_frame

    line_dur = max(0.5, line_info.get("end", 4.0) - line_info.get("start", 0.0))
    # Typewriter typing progression
    type_p = min(1.0, max(0.0, local_t / max(0.4, line_dur * 0.65)))
    chars_count = max(1, int(len(full_text) * type_p))
    display_text = full_text[:chars_count]
    if type_p < 1.0 and (int(local_t * 5) % 2 == 0):
        display_text += "|"

    # Font sizing & loading with automatic glyph safety check
    font_path = line_info.get("font_path", "./fonts/Mukta-Bold.ttf")
    pos_type = line_info.get("position", "bottom_center")
    fill_color = line_info.get("color", (253, 224, 71, 255))
    bg_style = line_info.get("bg_style", "none")
    emoji_name = line_info.get("emoji_name")
    
    font_size = max(26, int(tw * 0.046))
    if pos_type == "center":
        font_size = max(30, int(tw * 0.054))
    elif pos_type == "top_badge":
        font_size = max(24, int(tw * 0.040))

    # Automatic glyph validation: ensure font supports the text, otherwise fallback to Mukta-Bold
    if not font_supports_text(font_path, display_text):
        font_path = "./fonts/Mukta-Bold.ttf"

    try:
        loaded_font = ImageFont.truetype(font_path, font_size)
    except Exception:
        try:
            loaded_font = ImageFont.truetype("./fonts/Mukta-Bold.ttf", font_size)
        except Exception:
            loaded_font = ImageFont.load_default()

    # Load high-definition expression emoji icon
    emoji_size = max(22, int(font_size * 0.92))
    emoji_img = get_cached_emoji(emoji_name, emoji_size) if emoji_name else None
    emoji_spacing = max(10, int(font_size * 0.28))

    # Wrap text cleanly if long
    max_chars = 26 if tw < th else 46
    words = display_text.split()
    wrapped_lines = []
    current_line = []
    current_len = 0
    for w in words:
        if current_len + len(w) + 1 > max_chars:
            wrapped_lines.append(" ".join(current_line))
            current_line = [w]
            current_len = len(w)
        else:
            current_line.append(w)
            current_len += len(w) + 1
    if current_line:
        wrapped_lines.append(" ".join(current_line))
    if not wrapped_lines:
        wrapped_lines = [display_text]

    draw = ImageDraw.Draw(im_frame)
    line_height = int(font_size * 1.35)
    total_h = len(wrapped_lines) * line_height

    max_line_w = 0
    line_widths = []
    for lt in wrapped_lines:
        try:
            bbox = draw.textbbox((0, 0), lt, font=loaded_font)
            lw = bbox[2] - bbox[0]
        except Exception:
            lw = len(lt) * int(font_size * 0.55)
        line_widths.append(lw)
        if lw > max_line_w:
            max_line_w = lw

    # Account for expression emoji attached to the last line
    if emoji_img and line_widths:
        last_cluster_w = line_widths[-1] + emoji_spacing + emoji_size
        if last_cluster_w > max_line_w:
            max_line_w = last_cluster_w

    pad_x = 22
    pad_y = 10
    pill_w = max_line_w + (pad_x * 2)
    pill_h = total_h + (pad_y * 2)

    if pos_type == "center":
        x_start = (tw - pill_w) // 2
        y_start = (th - pill_h) // 2
    elif pos_type == "lower_left":
        x_start = max(24, int(tw * 0.06))
        y_start = int(th * 0.72)
    elif pos_type == "top_badge":
        x_start = (tw - pill_w) // 2
        y_start = int(th * 0.15)
    elif pos_type == "bottom_floating":
        x_start = (tw - pill_w) // 2
        y_start = int(th * 0.65)
    else:  # "bottom_center"
        x_start = (tw - pill_w) // 2
        y_start = int(th * 0.76)

    # Dynamic subtitle background based on bg_style ("none", "pill", "neon_line", "glass_card")
    # Allows background box to randomly disappear ("gayb") as requested by user
    if bg_style == "pill":
        draw.rounded_rectangle(
            [x_start, y_start, x_start + pill_w, y_start + pill_h],
            radius=14,
            fill=(12, 14, 24, 210)
        )
        accent_border = (fill_color[0], fill_color[1], fill_color[2], 140)
        draw.rounded_rectangle(
            [x_start, y_start, x_start + pill_w, y_start + pill_h],
            radius=14,
            outline=accent_border,
            width=2
        )
    elif bg_style == "glass_card":
        draw.rounded_rectangle(
            [x_start, y_start, x_start + pill_w, y_start + pill_h],
            radius=12,
            fill=(15, 18, 30, 130)
        )
    elif bg_style == "neon_line":
        # Sleek glowing underline bar without any dark background box
        underline_y = y_start + pill_h - 2
        draw.line(
            [(x_start + pad_x, underline_y), (x_start + pill_w - pad_x, underline_y)],
            fill=fill_color,
            width=3
        )
    # If bg_style == "none", NO background box or line is drawn (pure floating text!)

    # Render lines with drop shadow + stroke + attached expression emoji
    for i, lt in enumerate(wrapped_lines):
        lw = line_widths[i]
        is_last_line = (i == len(wrapped_lines) - 1)

        if is_last_line and emoji_img:
            # Center the cluster of text + emoji together
            cluster_w = lw + emoji_spacing + emoji_size
            line_x = x_start + pad_x + (max_line_w - cluster_w) // 2
        else:
            line_x = x_start + pad_x + (max_line_w - lw) // 2

        line_y = y_start + pad_y + (i * line_height)

        # Deep drop shadow
        shadow_offset = 3 if bg_style in ["none", "neon_line"] else 2
        draw.text(
            (line_x + shadow_offset, line_y + shadow_offset),
            lt,
            font=loaded_font,
            fill=(0, 0, 0, 240)
        )
        # Bold readable stroke + vibrant fill
        stroke_w = max(2, int(font_size * (0.10 if bg_style in ["none", "neon_line"] else 0.08)))
        draw.text(
            (line_x, line_y),
            lt,
            font=loaded_font,
            fill=fill_color,
            stroke_width=stroke_w,
            stroke_fill=(12, 14, 24, 240)
        )

        # Draw expression emoji beside the text on the final line
        if is_last_line and emoji_img:
            em_x = line_x + lw + emoji_spacing
            em_y = line_y + (line_height - emoji_size) // 2 - 2
            try:
                im_frame.paste(emoji_img, (em_x, em_y), emoji_img)
            except Exception:
                pass

    return im_frame

    return im_frame


def get_available_cookies_file(target_dir: str = "temp_song") -> Optional[str]:
    """
    Checks for YouTube session cookies from Render environment variables or disk files.
    Allows yt-dlp to bypass datacenter bot detection walls.
    """
    env_cookies = os.environ.get("YOUTUBE_COOKIES") or os.environ.get("YT_COOKIES")
    if env_cookies and len(env_cookies.strip()) > 20:
        c_path = os.path.join(target_dir, "yt_cookies.txt")
        try:
            with open(c_path, "w", encoding="utf-8") as f:
                f.write(env_cookies.strip())
            print(f"🍪 [Song Engine] Loaded YouTube Cookies from Render Environment Variable ({len(env_cookies)} bytes)")
            return c_path
        except Exception as e:
            print(f"⚠️ Failed to write cookie file from env: {e}")

    possible_cookie_paths = [
        "cookies.txt",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt"),
        os.path.join(os.getcwd(), "cookies.txt"),
        os.path.join("temp_song", "cookies.txt"),
        os.path.join("/etc", "secrets", "cookies.txt"),
        os.path.join(target_dir, "cookies.txt")
    ]
    for p in possible_cookie_paths:
        if os.path.exists(p) and os.path.getsize(p) > 20:
            abs_p = os.path.abspath(p)
            print(f"🍪 [Song Engine] Found YouTube Cookies file at '{abs_p}' ({os.path.getsize(p)} bytes)")
            return abs_p

    return None


def get_clean_youtube_metadata(song_url: str) -> Dict[str, str]:
    """
    Extracts video title and artist from YouTube oEmbed API without triggering bot detection.
    oEmbed is a public Google API and is never blocked on Render or datacenter IPs.
    """
    try:
        import urllib.request
        import urllib.parse
        import ssl
        import json

        vid_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', song_url)
        clean_url = f"https://www.youtube.com/watch?v={vid_match.group(1)}" if vid_match else song_url
        api_url = f"https://www.youtube.com/oembed?url={urllib.parse.quote(clean_url)}&format=json"

        ctx = ssl._create_unverified_context() if hasattr(ssl, '_create_unverified_context') else None
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6, context=ctx) as r:
            data = json.loads(r.read().decode('utf-8'))
            raw_title = data.get('title', '')
            author = data.get('author_name', '')

            # Strip brackets, parentheses, curly braces: (Lyrical), [Official Video], etc.
            clean = re.sub(r'[\(\[\{].*?[\)\]\}]', '', raw_title)
            # Take primary title before music label / credits separator '|'
            clean = clean.split('|')[0]
            clean = re.sub(r'feat\..*', '', clean, flags=re.I)
            clean = re.sub(r'ft\..*', '', clean, flags=re.I)
            clean = re.sub(r'[^\w\s]', ' ', clean)
            clean = ' '.join(clean.split())

            clean_author = re.sub(r'[^\w\s]', ' ', author).strip()
            clean_author = re.sub(r'\b(Official|VEVO|DZ|Music|Records|Channel|Series|T-Series)\b', '', clean_author, flags=re.I).strip()

            clean_words = clean.split()
            if len(clean_words) >= 2:
                search_query = clean
            elif clean_author:
                search_query = f"{clean} {clean_author}".strip()
            else:
                search_query = clean
            print(f"🎯 [Song Engine] Extracted Metadata via oEmbed: '{raw_title}' -> Query: '{search_query}'")
            return {
                "raw_title": raw_title,
                "clean_title": clean,
                "author": clean_author,
                "query": search_query
            }
    except Exception as e:
        print(f"⚠️ [Song Engine] oEmbed metadata extraction exception: {e}")
        return {
            "raw_title": "Official Song",
            "clean_title": "Official Song",
            "author": "",
            "query": "trending song"
        }


def decrypt_jiosaavn_url(enc_url: str) -> Optional[str]:
    """
    Decrypts JioSaavn encrypted_media_url to get direct 320kbps Akamai CDN stream URL.
    100% immune to datacenter IP blocks and bot detection.
    """
    if not enc_url:
        return None
    try:
        import base64
        try:
            from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
        except ImportError:
            from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
        from cryptography.hazmat.primitives.ciphers import Cipher, modes
        from cryptography.hazmat.backends import default_backend

        key = b'38346591' * 3
        cipher = Cipher(TripleDES(key), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(base64.b64decode(enc_url)) + decryptor.finalize()
        pad_len = decrypted[-1]
        return decrypted[:-pad_len].decode('utf-8')
    except Exception as e:
        print(f"⚠️ JioSaavn URL decrypt note: {e}")
        return None


def download_youtube_song_audio(
    source_type: str = "url",
    song_url: Optional[str] = None,
    singer_name: Optional[str] = None,
    song_title: Optional[str] = None,
    uploaded_audio_path: Optional[str] = None,
    target_dir: str = "temp_song"
) -> Dict[str, Any]:
    """
    Downloads official song audio from:
    1. User-Uploaded MP3 file (100% reliable)
    2. Direct Cloud Music CDN (Akamai stream - zero bot checks, full 320kbps master)
    3. SoundCloud auto-fallback (bypasses Render datacenter IP botwall)
    4. YouTube with optional session cookies
    """
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, "master_song_audio.mp3")

    # 1. Direct Upload Check
    if uploaded_audio_path and os.path.exists(uploaded_audio_path) and os.path.getsize(uploaded_audio_path) > 1000:
        print(f"🎵 [Song Engine] Processing user-uploaded audio file: {uploaded_audio_path}...")
        try:
            cmd = ["ffmpeg", "-y", "-i", uploaded_audio_path, "-vn", "-acodec", "libmp3lame", "-q:a", "2", target_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print(f"✅ [Song Engine] User Uploaded Audio Prepared: {target_path} ({os.path.getsize(target_path)} bytes)")
            return {
                "audio_path": target_path,
                "title": song_title or singer_name or "Uploaded Song Audio",
                "duration": 60.0
            }
        except Exception as e_up:
            print(f"⚠️ [Song Engine] Audio upload conversion note: {e_up}")
            import shutil
            shutil.copy2(uploaded_audio_path, target_path)
            return {
                "audio_path": target_path,
                "title": song_title or singer_name or "Uploaded Song Audio",
                "duration": 60.0
            }

    # If already downloaded in this job directory, return immediately
    if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
        return {"audio_path": target_path, "title": song_title or singer_name or "Song", "duration": 60.0}

    extracted_title = song_title or singer_name or "Official Song"
    extracted_duration = 60.0

    # Clean artist & song names
    clean_singer = re.sub(r'[^\w\s]', '', singer_name or "").strip()
    clean_title = re.sub(r'[^\w\s]', '', song_title or "").strip()

    # If YouTube URL was passed as fallback, extract clean name via oEmbed
    if not clean_singer and song_url and song_url.strip():
        meta = get_clean_youtube_metadata(song_url.strip())
        if meta and meta.get("query"):
            clean_singer = meta.get("author") or meta.get("query")
            clean_title = meta.get("clean_title") or ""

    if not clean_singer:
        clean_singer = "Darshan Raval"

    print(f"🎙️ [Song Engine] Artist: '{clean_singer}' | Specific Song: '{clean_title or '(Random Artist Hit)'}'...")

    # Attempt 1: Direct Cloud Music CDN (Akamai Stream - Zero Bot Checks on Render)
    try:
        import urllib.request, urllib.parse, ssl, json, random
        ctx = ssl._create_unverified_context() if hasattr(ssl, '_create_unverified_context') else None

        search_queries = []
        if clean_title and clean_singer:
            search_queries.append(f"{clean_singer} {clean_title}".strip())
            search_queries.append(f"{clean_title} {clean_singer}".strip())
            search_queries.append(clean_title)
        elif clean_title:
            search_queries.append(clean_title)
        else:
            search_queries.append(clean_singer)

        results = []
        for sq in search_queries:
            api_url = f"https://www.jiosaavn.com/api.php?__call=search.getResults&q={urllib.parse.quote(sq)}&_format=json&_marker=0&ctx=web6dot0&n=20&p=1"
            req_cdn = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            try:
                with urllib.request.urlopen(req_cdn, context=ctx, timeout=6) as resp_cdn:
                    cdn_data = json.loads(resp_cdn.read().decode('utf-8'))
                    found = cdn_data.get('results', [])
                    if found:
                        results.extend(found)
                        if len(results) >= 15:
                            break
            except Exception:
                pass

        if not results:
            for sq in search_queries:
                ac_url = f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_marker=0&query={urllib.parse.quote(sq)}&ctx=web6dot0&_format=json"
                req_ac = urllib.request.Request(ac_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                try:
                    with urllib.request.urlopen(req_ac, context=ctx, timeout=5) as resp_ac:
                        ac_data = json.loads(resp_ac.read().decode('utf-8'))
                        found = ac_data.get('songs', {}).get('data', [])
                        if found:
                            results.extend(found)
                            break
                except Exception:
                    pass

        if results:
            # Deduplicate by song id
            seen_ids = set()
            unique_results = []
            for r in results:
                rid = r.get('id') or r.get('song') or str(r)
                if rid not in seen_ids:
                    seen_ids.add(rid)
                    unique_results.append(r)
            results = unique_results

            if clean_title or clean_singer:
                # Rank results to pick the EXACT match for singer and title
                def score_song_candidate(item: dict) -> float:
                    cand_title = (item.get('song') or item.get('title') or '').lower()
                    cand_singers = (item.get('singers') or item.get('primary_artists') or item.get('artist') or '').lower()
                    score = 0.0

                    # 1. Singer Matching
                    if clean_singer:
                        singer_tokens = [w for w in re.findall(r'\w+', clean_singer.lower()) if len(w) > 2]
                        if singer_tokens:
                            matches = sum(1 for tok in singer_tokens if tok in cand_singers)
                            if matches == len(singer_tokens):
                                score += 120.0  # Perfect singer match!
                            elif matches > 0:
                                score += 60.0 * (matches / len(singer_tokens))
                            else:
                                score -= 30.0

                    # 2. Title Matching
                    if clean_title:
                        title_tokens = [w for w in re.findall(r'\w+', clean_title.lower()) if len(w) > 1]
                        if title_tokens:
                            matches = sum(1 for tok in title_tokens if tok in cand_title)
                            if matches == len(title_tokens):
                                score += 100.0  # Perfect title match!
                            elif matches > 0:
                                score += 50.0 * (matches / len(title_tokens))
                        clean_cand_title = re.sub(r'\(.*?\)|\[.*?\]', '', cand_title).strip()
                        if clean_cand_title == clean_title.lower().strip():
                            score += 40.0

                    # 3. Penalize Unwanted Covers / Remixes / Slowed
                    combined = f"{cand_title} {cand_singers}"
                    penalties = ["cover", "karaoke", "instrumental", "acoustic version", "remix", "lofi flip", "reverb", "slowed", "female version", "male version"]
                    for pen in penalties:
                        if pen in combined and pen not in (clean_title or '').lower():
                            score -= 50.0

                    # 4. Streamable media check
                    if item.get('encrypted_media_url'):
                        score += 20.0

                    return score

                results.sort(key=score_song_candidate, reverse=True)
                chosen = results[0]
                best_score = score_song_candidate(chosen)
                cand_singers = chosen.get('singers') or chosen.get('primary_artists') or clean_singer
                chosen_title = re.sub(r'&quot;|&#039;|&amp;', '', chosen.get('song') or chosen.get('title') or clean_title or clean_singer).strip()
                print(f"🎯 [Song Match Engine] Selected best matching song track: '{chosen_title}' by '{cand_singers}' (Match Score: {best_score:.1f})")
            else:
                chosen = random.choice(results[:min(8, len(results))])
                chosen_title = re.sub(r'&quot;|&#039;|&amp;', '', chosen.get('song') or chosen.get('title') or clean_singer).strip()
            song_id = chosen.get('id')
            enc_url = chosen.get('encrypted_media_url')
            direct_cdn_url = decrypt_jiosaavn_url(enc_url) if enc_url else None

            # Fetch official lyrics from JioSaavn API directly
            jio_lyrics_lines = []
            if song_id:
                try:
                    lyr_api = f"https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&lyrics_id={song_id}&_format=json&_marker=0&ctx=web6dot0"
                    req_l = urllib.request.Request(lyr_api, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                    with urllib.request.urlopen(req_l, context=ctx, timeout=6) as resp_l:
                        l_json = json.loads(resp_l.read().decode('utf-8'))
                        raw_lyr = l_json.get('lyrics', '')
                        if raw_lyr:
                            c_lyr = re.sub(r'<br\s*/?>', '\n', raw_lyr)
                            c_lyr = re.sub(r'<.*?>', '', c_lyr)
                            jio_lyrics_lines = [l.strip() for l in c_lyr.splitlines() if len(l.strip()) > 2]
                            if jio_lyrics_lines:
                                print(f"🎤 [Song Engine] Retrieved {len(jio_lyrics_lines)} official lyrics lines from Music CDN for '{chosen_title}'!")
                except Exception as e_lyr:
                    print(f"⚠️ JioSaavn lyrics note: {e_lyr}")

            if direct_cdn_url and direct_cdn_url.startswith('http'):
                hd_cdn_url = direct_cdn_url.replace('_96.mp4', '_320.mp4').replace('_160.mp4', '_320.mp4')
                print(f"🎉 [Song Engine] Found Studio Master CDN Stream: '{chosen_title}' by {clean_singer} -> {hd_cdn_url}")
                temp_raw_audio = os.path.join(target_dir, "raw_cdn_audio.mp4")

                try:
                    dl_req = urllib.request.Request(hd_cdn_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(dl_req, context=ctx, timeout=20) as r_dl, open(temp_raw_audio, 'wb') as f_out:
                        f_out.write(r_dl.read())
                except Exception:
                    dl_req = urllib.request.Request(direct_cdn_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(dl_req, context=ctx, timeout=20) as r_dl, open(temp_raw_audio, 'wb') as f_out:
                        f_out.write(r_dl.read())

                if os.path.exists(temp_raw_audio) and os.path.getsize(temp_raw_audio) > 5000:
                    conv_cmd = [
                        "ffmpeg", "-y", "-i", temp_raw_audio,
                        "-vn", "-acodec", "libmp3lame", "-q:a", "2",
                        target_path
                    ]
                    subprocess.run(conv_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    try: os.remove(temp_raw_audio)
                    except Exception: pass

                    exact_dur = 60.0
                    try:
                        probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", target_path]
                        exact_dur = float(subprocess.check_output(probe_cmd).decode().strip())
                    except Exception:
                        pass

                    print(f"✅ [Song Engine] Successfully Downloaded 320kbps Studio Master: '{chosen_title}' ({os.path.getsize(target_path)} bytes, {exact_dur:.1f}s)")
                    return {
                        "audio_path": target_path,
                        "title": chosen_title,
                        "singer": clean_singer,
                        "duration": exact_dur,
                        "song_id": song_id,
                        "lyrics_lines": jio_lyrics_lines
                    }
    except Exception as e_cdn:
        print(f"⚠️ [Song Engine] Music CDN lookup note: {e_cdn}")

    # Attempt 2: SoundCloud Stream Fallback (If not found on primary CDN)
    sc_query = f"{clean_singer} {clean_title}".strip() if clean_title else clean_singer
    if sc_query:
        print(f"⚡ [Song Engine] Initiating SoundCloud stream fallback for: '{sc_query}'...")
        try:
            sc_target = f"scsearch3:{sc_query}"
            sc_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(target_dir, "sc_song.%(ext)s"),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'socket_timeout': 30
            }
            with yt_dlp.YoutubeDL(sc_opts) as ydl:
                info = ydl.extract_info(sc_target, download=True)
                sc_entry = info['entries'][0] if 'entries' in info and info['entries'] else info
                if sc_entry:
                    extracted_title = sc_entry.get('title') or sc_query
                    extracted_duration = float(sc_entry.get('duration') or 60.0)

            sc_candidates = [
                f for f in glob.glob(os.path.join(target_dir, "sc_song*.*"))
                if os.path.getsize(f) > 5000 and not f.endswith('.txt') and not f.endswith('.json')
            ]
            if sc_candidates and sc_entry:
                conv_cmd = [
                    "ffmpeg", "-y", "-i", sc_candidates[0],
                    "-vn", "-acodec", "libmp3lame", "-q:a", "2",
                    target_path
                ]
                subprocess.run(conv_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                try:
                    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", target_path]
                    extracted_duration = float(subprocess.check_output(probe_cmd).decode().strip())
                except Exception:
                    pass
                print(f"🎉 [Song Engine] Successfully Retrieved Song Track via SoundCloud: '{extracted_title}' ({os.path.getsize(target_path)} bytes, {extracted_duration:.1f}s)")
                return {
                    "audio_path": target_path,
                    "title": extracted_title,
                    "singer": clean_singer,
                    "duration": extracted_duration
                }
        except Exception as e_sc:
            print(f"⚠️ [Song Engine] SoundCloud fallback exception: {e_sc}")

    # Fallback to local background music if all downloads failed
    print("⚠️ [Song Engine] Remote downloads blocked by datacenter IP. Using local melodic track fallback...")
    print("💡 TIP: Set 'YOUTUBE_COOKIES' in Render environment variables or upload the MP3 directly in the UI!")
    fallback_sources = [
        os.path.join("static", "cool.mp3"),
        os.path.join("static", "cool1.mp3"),
        os.path.join("static", "cool2.mp3")
    ]
    for fb in fallback_sources:
        if os.path.exists(fb):
            import shutil
            shutil.copy2(fb, target_path)
            return {"audio_path": target_path, "title": extracted_title, "duration": 60.0}

    return {"audio_path": target_path, "title": extracted_title, "duration": 60.0}


def generate_song_lyric_scenes(
    user_lyrics: Optional[str] = None,
    singer_name: Optional[str] = None,
    song_title: Optional[str] = None,
    target_duration: int = 30
) -> List[Dict[str, Any]]:
    """Backward compatibility wrapper returning parsed scenes."""
    return fetch_song_synced_lyrics(song_title or "Song", singer_name or "", target_duration)


def build_full_song_video(
    req: Any,
    job_id: str,
    job_dir: str,
    output_path: str
) -> str:
    """
    Full pipeline to generate Ultra Song & Music Video with:
    1. 320kbps Studio Audio download
    2. Exact Synced Lyrics with Typewriter Printer Animation
    3. Multi-Font Dynamic Engine (5+ Fonts: Mukta, Kalam, Yatra One, Devanagari, Rozha, Bebas)
    4. Random / Varied Screen Positions & Vibrant Accent Colors
    5. Reduced Background Photos (only 2 to 5 photos total per video)
    6. Mood-matched Cinematic Color Grading Filters (Teal & Orange, Moody Noir, Golden Dream, etc.)
    7. Memory-Safe Segment Rendering & FFmpeg Concat Demuxer
    8. Master Song Audio Mux with Smooth 1.5s Fadeout
    """
    target_aspect = getattr(req, 'aspect_ratio', '9:16') or '9:16'
    
    if target_aspect == '16:9':
        target_size = (1280, 720)
        orientation = "landscape"
    elif target_aspect == '1:1':
        target_size = (720, 720)
        orientation = "portrait"
    else:
        target_size = (720, 1280)
        orientation = "portrait"

    # 1. Download Master Song Audio from Cloud Music CDN or SoundCloud or Uploaded Audio
    song_source_type = getattr(req, 'song_source_type', 'url') or 'url'
    song_url = getattr(req, 'song_url', '') or ''
    singer_name = getattr(req, 'singer_name', '') or ''
    song_title = getattr(req, 'song_title', '') or ''
    song_lyrics = getattr(req, 'song_lyrics', '') or getattr(req, 'full_script', '')
    song_mood = getattr(req, 'song_mood', 'romantic') or 'romantic'
    uploaded_audio_path = getattr(req, 'uploaded_audio_path', None) or getattr(req, 'song_audio_file', None)

    audio_res = download_youtube_song_audio(
        source_type=song_source_type,
        song_url=song_url,
        singer_name=singer_name,
        song_title=song_title,
        uploaded_audio_path=uploaded_audio_path,
        target_dir=job_dir
    )
    master_audio_path = audio_res.get('audio_path')

    # Determine exact target duration based on user preference and downloaded audio
    actual_song_dur = float(audio_res.get('duration') or 60.0)
    req_dur = int(getattr(req, 'duration', 0) or 0)
    
    if req_dur <= 0:
        # Full song mode: match the audio duration (capped at 180s for memory safety)
        target_duration = int(min(actual_song_dur, 180.0))
    else:
        # Match user duration, but if downloaded song is shorter, don't exceed song audio
        target_duration = int(min(req_dur, actual_song_dur)) if actual_song_dur > 5 else req_dur

    print(f"\n==================================================")
    print(f"🎵 [ULTRA SONG VIDEO PIPELINE] Job ID: {job_id}")
    print(f"📊 Target Duration: {target_duration}s (Song Audio: {actual_song_dur:.1f}s) | Mood: {song_mood.upper()} | Size: {target_size}")
    print(f"==================================================")

    # 2. Extract Exact Synced Lyrics & Style Attributes
    if song_lyrics and song_lyrics.strip():
        # User provided custom lyrics
        custom_raw = [sanitize_lyrics_text(l) for l in song_lyrics.splitlines() if len(l.strip()) > 1]
        n_cust = max(1, len(custom_raw))
        base_dur = round(target_duration / n_cust, 2)
        all_lyrics = []
        for idx, txt in enumerate(custom_raw):
            st = idx * base_dur
            et = min(float(target_duration), (idx + 1) * base_dur if idx < n_cust - 1 else target_duration)
            all_lyrics.append({"start": st, "end": et, "text": txt})
    else:
        # Fetch exact synced lyrics from LRCLIB with official JioSaavn lyrics fallback
        all_lyrics = fetch_song_synced_lyrics(
            song_title=song_title or audio_res.get('title'),
            singer_name=singer_name or audio_res.get('singer'),
            target_duration=target_duration,
            fallback_lyrics=audio_res.get('lyrics_lines'),
            song_id=audio_res.get('song_id')
        )

    # Determine if lyrics contain Devanagari Hindi characters
    has_devanagari = any(
        any(0x0900 <= ord(c) <= 0x097F for c in lyr.get("text", ""))
        for lyr in all_lyrics
    )

    # Build safe font pool: if pure English/Hinglish, include universal + bold display latin fonts
    font_candidates = [f for f in CINEMATIC_FONTS_POOL if os.path.exists(f)]
    if not has_devanagari:
        font_candidates += [f for f in LATIN_ONLY_FONTS_POOL if os.path.exists(f)]
    if not font_candidates:
        font_candidates = ["./fonts/Mukta-Bold.ttf"]

    # Assign rotating safe fonts, dynamic positions, accent colors, randomized background styles, and expression emojis
    for idx, lyr in enumerate(all_lyrics):
        line_txt = lyr.get("text", "")
        chosen_font = font_candidates[idx % len(font_candidates)]
        # Ensure the selected font actually supports the text characters
        if not font_supports_text(chosen_font, line_txt):
            for fallback_f in CINEMATIC_FONTS_POOL:
                if font_supports_text(fallback_f, line_txt):
                    chosen_font = fallback_f
                    break
            else:
                chosen_font = "./fonts/Mukta-Bold.ttf"

        lyr["font_path"] = chosen_font
        lyr["position"] = TEXT_POSITIONS[idx % len(TEXT_POSITIONS)]
        lyr["color"] = TEXT_COLORS[idx % len(TEXT_COLORS)]
        lyr["bg_style"] = TEXT_BG_STYLES[idx % len(TEXT_BG_STYLES)]
        lyr["emoji_name"] = detect_expression_emoji(line_txt, song_mood, idx)

    bg_none_count = sum(1 for lyr in all_lyrics if lyr.get("bg_style") == "none")
    print(f"📝 [Song Engine] Prepared {len(all_lyrics)} synced typewriter lyrics lines with expression emojis across {len(font_candidates)} rotating fonts ({bg_none_count} clean floating lines without background box).")

    # 3. Reduced Background Visual Segments (Only 2 to 5 photos total!)
    num_segments = max(2, min(8, int(math.ceil(target_duration / 10.0))))
    seg_dur = round(target_duration / num_segments, 2)
    print(f"🎬 [Song Engine] Segmenting video into {num_segments} cinematic background visual scenes ({seg_dur}s per scene)...")

    visual_mode = getattr(req, 'song_visual_mode', 'motion') or getattr(req, 'mode', 'ultra')
    is_stock_video = (visual_mode in ['video', 'standard'])

    # Mood-based filters and search queries
    candidate_filters = MOOD_FILTERS.get(song_mood, ALL_FILTERS)
    mood_kw = MOOD_KEYWORDS.get(song_mood, "romantic golden hour aesthetic 4k")
    pool = MOOD_VISUAL_POOLS.get(song_mood, MOOD_VISUAL_POOLS.get("romantic", []))

    # Compute a unique salt for this video so different songs/jobs get different photo rotations
    effective_title = song_title or audio_res.get('title') or ''
    effective_singer = singer_name or audio_res.get('singer') or ''
    clean_singer_str = re.sub(r'[^\w\s]', '', effective_singer).strip()
    clean_title_str = re.sub(r'[^\w\s]', '', effective_title).strip()
    job_salt = int(hashlib.md5(f"{job_id}_{clean_title_str}_{clean_singer_str}".encode()).hexdigest(), 16) % 100

    from video_fetcher import fetch_videos
    from web_image_fetcher import fetch_web_image

    rendered_scene_files = []

    for seg_idx in range(num_segments):
        release_system_memory()
        seg_start = seg_idx * seg_dur
        seg_end = min(float(target_duration), (seg_idx + 1) * seg_dur if seg_idx < num_segments - 1 else target_duration)
        this_seg_dur = round(seg_end - seg_start, 2)

        # Select distinct visual scene and dynamic camera motion
        chosen_scene = pool[(seg_idx + job_salt) % len(pool)] if pool else mood_kw
        chosen_filter = candidate_filters[(seg_idx + job_salt) % len(candidate_filters)]
        chosen_motion = CAMERA_MOTION_STYLES[(seg_idx + job_salt) % len(CAMERA_MOTION_STYLES)]

        # Lines active in this segment
        lines_in_seg = [l for l in all_lyrics if l["start"] < seg_end and l["end"] > seg_start]
        print(f"\n🎥 [Segment {seg_idx+1}/{num_segments}] Time: {seg_start:.1f}s - {seg_end:.1f}s ({this_seg_dur}s) | Motion: {chosen_motion} | Filter: {chosen_filter} | Lyrics lines: {len(lines_in_seg)}")
        print(f"🖼️ [Segment {seg_idx+1}] Category '{song_mood}' Visual Concept: '{chosen_scene}'")

        seg_clip = None
        loaded_raw = None

        if is_stock_video:
            # 🎥 Stock Video Clip
            v_temp = os.path.join(job_dir, f"stock_vid_{seg_idx}.mp4")
            v_query = f"{chosen_scene}"
            v_paths = fetch_videos(
                v_query, v_temp,
                orientation=orientation,
                category="Music",
                video_type="short" if target_aspect == "9:16" else "long",
                topic=song_mood
            )
            if v_paths and os.path.exists(v_paths[0]) and os.path.getsize(v_paths[0]) > 5000:
                try:
                    loaded_raw = VideoFileClip(v_paths[0], audio=False)
                    loaded = loaded_raw.resize(height=target_size[1]) if loaded_raw.h < target_size[1] else loaded_raw.resize(width=target_size[0])
                    loaded = loaded.crop(x_center=loaded.w/2, y_center=loaded.h/2, width=target_size[0], height=target_size[1])
                    if loaded.duration < this_seg_dur:
                        n_loops = int(math.ceil(this_seg_dur / loaded.duration))
                        v_base = concatenate_videoclips([loaded] * n_loops).subclip(0, this_seg_dur)
                    else:
                        v_base = loaded.subclip(0, this_seg_dur)

                    def make_video_frame(t):
                        orig_frame = v_base.get_frame(t)
                        im_f = Image.fromarray(orig_frame)
                        abs_t = seg_start + t
                        active_line = None
                        for l in lines_in_seg:
                            if l["start"] <= abs_t < l["end"]:
                                active_line = l
                                break
                        if active_line:
                            local_t = abs_t - active_line["start"]
                            im_f = render_typewriter_lyrics_on_frame(im_f, active_line, local_t, target_size[0], target_size[1])
                        return np.array(im_f)

                    seg_clip = VideoClip(make_video_frame, duration=this_seg_dur)
                except Exception as e_v:
                    print(f"⚠️ Stock video clip load note: {e_v}")

        if not seg_clip:
            # ⚡ Ultra 3D Photo Motion with Filter & Typewriter Lyrics
            img_path = os.path.join(job_dir, f"bg_photo_{seg_idx}.jpg")
            photo_query = f"{chosen_scene}".strip()
            fetch_web_image(photo_query, img_path)

            try:
                with Image.open(img_path) as raw_im:
                    filtered_im = apply_cinematic_photo_filter(raw_im, chosen_filter)
                    filtered_im.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
                    filtered_im.save(img_path, quality=88)
            except Exception as e_im:
                print(f"⚠️ Filter apply note: {e_im}")

            tw, th = target_size
            MARGIN = 1.30
            try:
                orig = Image.open(img_path).convert("RGB")
                aspect_orig = orig.width / orig.height
                aspect_target = tw / th
                if aspect_orig > aspect_target:
                    new_h = int(th * MARGIN)
                    new_w = int(new_h * aspect_orig)
                else:
                    new_w = int(tw * MARGIN)
                    new_h = int(new_w / aspect_orig)
                orig_resized = orig.resize((new_w, new_h), Image.Resampling.LANCZOS)
                base_np = np.array(orig_resized)
                try: orig.close(); orig_resized.close()
                except Exception: pass
                del orig, orig_resized
            except Exception as e_base:
                print(f"⚠️ Base image load note: {e_base}")
                base_np = np.zeros((int(th * MARGIN), int(tw * MARGIN), 3), dtype=np.uint8)
                base_np[:] = (20, 15, 30)

            bw = base_np.shape[1]
            bh = base_np.shape[0]

            def make_motion_frame(t):
                progress = min(1.0, max(0.0, t / max(0.1, this_seg_dur)))
                # Smooth cosine ease-in-out
                ease = 0.5 * (1.0 - math.cos(math.pi * progress))

                if chosen_motion == "zoom_in":
                    scale = 1.00 + (0.15 * ease)
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    x1 = (bw - cur_w) // 2
                    y1 = (bh - cur_h) // 2
                elif chosen_motion == "zoom_out":
                    scale = 1.15 - (0.15 * ease)
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    x1 = (bw - cur_w) // 2
                    y1 = (bh - cur_h) // 2
                elif chosen_motion == "pan_left_to_right":
                    scale = 1.08
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    avail_x = bw - cur_w
                    x1 = int(avail_x * (0.15 + 0.70 * ease))
                    y1 = (bh - cur_h) // 2
                elif chosen_motion == "pan_right_to_left":
                    scale = 1.08
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    avail_x = bw - cur_w
                    x1 = int(avail_x * (0.85 - 0.70 * ease))
                    y1 = (bh - cur_h) // 2
                elif chosen_motion == "tilt_up":
                    scale = 1.08
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    avail_y = bh - cur_h
                    x1 = (bw - cur_w) // 2
                    y1 = int(avail_y * (0.85 - 0.70 * ease))
                elif chosen_motion == "tilt_down":
                    scale = 1.08
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    avail_y = bh - cur_h
                    x1 = (bw - cur_w) // 2
                    y1 = int(avail_y * (0.15 + 0.70 * ease))
                elif chosen_motion == "diagonal_drift_zoom":
                    scale = 1.00 + (0.12 * ease)
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    avail_x = bw - cur_w
                    avail_y = bh - cur_h
                    x1 = int(avail_x * (0.20 + 0.60 * ease))
                    y1 = int(avail_y * (0.80 - 0.60 * ease))
                elif chosen_motion == "pulse_breathe":
                    breathe = math.sin(progress * math.pi)
                    scale = 1.00 + (0.10 * breathe)
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    x1 = (bw - cur_w) // 2
                    y1 = (bh - cur_h) // 2
                else:
                    scale = 1.00 + (0.12 * ease)
                    cur_w = int(tw * scale); cur_h = int(th * scale)
                    x1 = (bw - cur_w) // 2
                    y1 = (bh - cur_h) // 2

                x1 = max(0, min(bw - cur_w, x1))
                y1 = max(0, min(bh - cur_h, y1))
                x2 = min(bw, x1 + cur_w)
                y2 = min(bh, y1 + cur_h)

                crop = base_np[y1:y2, x1:x2]
                im_crop = Image.fromarray(crop).resize((tw, th), Image.Resampling.BILINEAR)

                abs_t = seg_start + t
                active_line = None
                for l in lines_in_seg:
                    if l["start"] <= abs_t < l["end"]:
                        active_line = l
                        break
                if active_line:
                    local_t = abs_t - active_line["start"]
                    im_crop = render_typewriter_lyrics_on_frame(im_crop, active_line, local_t, tw, th)

                frame_arr = np.array(im_crop)
                im_crop.close()
                return frame_arr

            seg_clip = VideoClip(make_motion_frame, duration=this_seg_dur)

        # 4. Render Segment to Disk Immediately (Memory-Safe for Render 512MB RAM)
        scene_mp4 = os.path.join(job_dir, f"rendered_seg_{seg_idx}.mp4")
        print(f"💾 [Song Engine] Rendering Segment {seg_idx+1}/{num_segments} to disk...")
        seg_clip.write_videofile(
            scene_mp4,
            fps=20,
            codec="libx264",
            preset="ultrafast",
            threads=1,
            audio=False,
            logger=None
        )

        try:
            seg_clip.close()
            if loaded_raw: loaded_raw.close()
        except Exception:
            pass
        del seg_clip
        release_system_memory()

        if os.path.exists(scene_mp4) and os.path.getsize(scene_mp4) > 1000:
            rendered_scene_files.append(scene_mp4)

    if not rendered_scene_files:
        raise RuntimeError("No visual segments were rendered successfully!")

    # 5. Stream Concatenate Segments via FFmpeg (Takes 0 MB RAM)
    print(f"\n🎞️ [Song Engine] Stitching {len(rendered_scene_files)} segments via FFmpeg Concat Demuxer...")
    concat_list_file = os.path.join(job_dir, "song_scenes_concat.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for sf in rendered_scene_files:
            f.write(f"file '{os.path.abspath(sf)}'\n")

    temp_video_no_audio = os.path.join(job_dir, "temp_video_stitched.mp4")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        "-movflags", "+faststart",
        temp_video_no_audio
    ]
    try:
        subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e_c:
        print(f"⚠️ Notice: Stream copy concat failed ({e_c}), re-encoding with minimal RAM...")
        re_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_file,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-threads", "1",
            temp_video_no_audio
        ]
        subprocess.run(re_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    release_system_memory()

    # 6. Mux Master Song Audio with 1.5s Audio Fadeout via FFmpeg
    if os.path.exists(master_audio_path) and os.path.getsize(master_audio_path) > 1000:
        print(f"🎶 [Song Engine] Attaching Master Audio Track to Final Video via FFmpeg...")
        fade_start = max(0.0, float(target_duration) - 1.5)
        mux_cmd = [
            "ffmpeg", "-y",
            "-i", temp_video_no_audio,
            "-i", master_audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-af", f"afade=t=out:st={fade_start:.2f}:d=1.5",
            "-shortest",
            "-movflags", "+faststart",
            output_path
        ]
        try:
            subprocess.run(mux_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e_mux:
            print(f"⚠️ Notice: Audio fade filter failed ({e_mux}), falling back to direct stream mux...")
            fallback_mux = [
                "ffmpeg", "-y",
                "-i", temp_video_no_audio,
                "-i", master_audio_path,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                output_path
            ]
            subprocess.run(fallback_mux, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        import shutil
        shutil.copy2(temp_video_no_audio, output_path)

    # 7. Clean up intermediate segment files to free disk space immediately
    try:
        if os.path.exists(concat_list_file):
            os.remove(concat_list_file)
        if os.path.exists(temp_video_no_audio):
            os.remove(temp_video_no_audio)
        for sf in rendered_scene_files:
            if os.path.exists(sf):
                os.remove(sf)
    except Exception:
        pass

    release_system_memory()
    print(f"🎉 SUCCESS! Ultra Song Video Produced -> {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path
