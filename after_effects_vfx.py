"""
Ultra After Effects Scene VFX Overlay Engine (`vfx_overlays/`).

Strictly gated to `mode == "ultra"` and After Effects / VFX / Motion Graphics
category ONLY. Removes diverse backgrounds (native ProRes alpha, split-duration
track matte, solid chroma screens, luminance paint key, and fast NumPy
barrier-preserving pyramid flood-fill for gradient/studio backgrounds) cleanly
without Halo/Holes and composites overlays onto scene clips at matched script cues.
"""

import os
import random
import re
import subprocess
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageFilter

_VFX_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_VFX_DIR = os.path.join(_VFX_BASE_DIR, "vfx_overlays")
_VFX_SPLIT_RE = re.compile(r'[\s,.\-!?;:"\'()\[\]{}<>/\\|~`@#$%^&*_+=।॥]+')
_VFX_RNG = random.SystemRandom()

HELLO_VFX_FILES: Tuple[str, ...] = (
    "hello.mp4",
    "hello2.mp4",
    "hello3.mp4",
    "hello4.mp4",
    "hello5.mp4",
    "hello6.mp4",
    "hello7.mp4",
    "hello8.mp4",
)

# Generic greeting cues intentionally pool across ALL 8 hello*.mp4 effects randomly.
_HELLO_GREETING_CUES = frozenset({
    "hello", "hi", "hey", "welcome", "greetings", "greet", "everyone",
    "friends", "guys", "dost", "dosto", "bhaiyo", "namaste", "namaskar",
    "swagat", "intro", "meet",
    "हेलो", "नमस्ते", "नमस्कार", "स्वागत", "दोस्तों", "भाइयों", "मित्रों",
})

# Common grammar/filler/neutral words excluded from partial/fuzzy matching so neutral sentences stay clean.
_VFX_STOPWORDS = frozenset({
    "hai", "hain", "tha", "the", "thi", "mein", "main", "me", "aur", "par",
    "se", "ko", "ka", "ki", "ke", "ne", "yeh", "woh", "yah", "yha", "wha",
    "kya", "jab", "tab", "ab", "ek", "do", "bhi", "toh", "gya", "gaya",
    "gayi", "raha", "rahi", "rha", "rhe", "wala", "wali", "wale", "hota",
    "hoti", "hote", "nahi", "nhi", "kar", "karo", "kiya", "diya", "liya",
    "hua", "hui", "hue", "liye", "kuch", "bahut", "sab", "aaj", "kal",
    "baat", "tarah", "jaise", "jese", "uska", "uski", "unke", "hum", "aap",
    "tum", "mera", "meri", "mere", "apna", "apni", "apne", "badal", "badalna",
    "badlaav", "badle", "naya", "nayi", "naye", "bada", "badi", "bade",
    "beta", "beti", "jana", "jaana", "fir", "phir", "rakhe", "rakha", "rakhi",
    "samay", "waqt", "paisa", "dhandha", "parso", "sabhi", "yahi", "wahi",
    "kahan", "jahan", "chota", "choti", "chote", "insaan", "shehar",
    "parivar", "yaar", "kaam", "raat", "shaam", "subah", "bahar", "andar",
    "upar", "niche", "peeche", "aage", "ghar", "nikalta", "nikal", "nikla",
    "laga", "lagi", "lage", "lagta", "lagti", "lagte", "bharat", "maana",
    "mana", "batao", "bataya", "batate", "jaante", "jante", "mausam",
    "suhavna", "nadi", "beh", "rehta", "chalta", "chalti", "rakhta", "khulne",
    "this", "that", "these", "those", "there", "here", "with", "from", "into",
    "about", "after", "before", "have", "has", "had", "will", "would", "could",
    "should", "they", "them", "their", "what", "when", "where", "which",
    "while", "chapter", "history", "monument", "explains", "person", "people",
    "place", "thing", "change", "changed", "changing", "story", "stories",
    "work", "working", "night", "morning", "great", "best", "first", "second",
    "last", "very", "most", "another", "every", "both", "mobile", "phone",
    "present", "future", "world", "india", "life", "system", "is", "are",
    "was", "were", "been", "for", "and", "not", "but", "you", "your", "his",
    "her", "she", "its", "our", "all", "can", "part", "same", "came",
})


def is_ultra_after_effects(mode: str, category: str) -> bool:
    """Return True strictly when mode is Ultra AND category is After Effects / VFX."""
    if str(mode or "").strip().lower() != "ultra":
        return False
    cat_low = str(category or "").strip().lower()
    return any(
        k in cat_low
        for k in ("after effect", "after iffect", "after effects", "vfx", "motion graphic")
    )


def resolve_vfx_path(filename: str) -> Optional[str]:
    """Resolve a VFX clip primarily from `vfx_overlays/`, falling back to repo root."""
    if not filename:
        return None
    base = os.path.basename(filename)
    for candidate in (
        os.path.join(_VFX_DIR, base),
        os.path.abspath(os.path.join("vfx_overlays", base)),
        os.path.join(_VFX_BASE_DIR, filename),
        os.path.abspath(filename),
    ):
        if os.path.exists(candidate) and os.path.getsize(candidate) > 1000:
            return candidate
    return None


# Semantic catalog mapped directly to each clip's inspected visual content & intent.
AFTER_EFFECTS_VFX_CATALOG: List[Dict[str, Any]] = [
    {
        "file": "FootageCrate-Sparks_Burst_Ground_Wide_4-LQ.mov",
        "key_mode": "native_alpha",
        "layout": "full_bottom",
        "scale_frac": 0.92,
        "max_dur": 3.35,
        "opacity": 0.95,
        "weight": 4.6,
        "keywords": [
            "spark", "sparks", "sparkle", "fireworks", "firework", "diwali",
            "cracker", "crackers", "rocket", "welding", "blaze", "festival",
            "victory sparks", "roshni", "chingari", "patakha", "aag",
            "चिंगारी", "पटाखा", "दिवाली", "रोशनी", "आतिशबाजी",
        ],
    },
    {
        "file": "FootageCrate-Whirling_Paper_1-LQ.mov",
        "key_mode": "native_alpha",
        "layout": "full_bottom",
        "scale_frac": 0.95,
        "max_dur": 5.40,
        "opacity": 0.92,
        "weight": 4.3,
        "keywords": [
            "paper", "papers", "page", "pages", "exam", "newspaper", "news",
            "office", "contract", "notes", "bill", "wind", "storm", "chaos",
            "library", "archive", "courtroom", "files flying",
            "kaagaz", "panna", "kitaab", "tufan", "hawa", "patra", "akhbar",
            "कागज", "पन्ना", "किताब", "अखबार", "नोट", "तूफान", "हवा",
        ],
    },
    {
        "file": "shoping_efect.mp4",
        "key_mode": "split_track_matte",
        "matte_offset": 6.0,
        "crop_norm": (0.20, 0.06, 0.3406, 0.94),
        "layout": "peek_right",
        "height_frac_land": 0.44,
        "height_frac_vert": 0.30,
        "max_dur": 5.80,
        "weight": 4.8,
        "keywords": [
            "shopping", "shoping", "shop", "buy", "purchase", "store", "market", "mall",
            "sale", "discount", "deal", "price", "order", "product", "ecommerce",
            "amazon", "flipkart", "cart", "bag", "retail", "grocery", "online",
            "spend", "spending", "customer", "buyer",
            "kharid", "khrid", "kharidna", "kharidari", "bazaar", "dukaan", "sasta", "mahanga",
            "शॉपिंग", "खरीद", "बाजार", "दुकान", "कीमत", "ऑफर", "डिस्काउंट", "सेल",
        ],
    },
    {
        "file": "gift.mp4",
        "key_mode": "pyramid_flood",
        "flood_kind": "neutral_grey",
        "crop_norm": (0.18, 0.10, 0.3606, 0.90),
        "layout": "peek_right",
        "height_frac_land": 0.44,
        "height_frac_vert": 0.30,
        "max_dur": 5.60,
        "weight": 4.8,
        "keywords": [
            "gift", "gifts", "present", "surprise", "reward", "bonus", "prize",
            "offer", "free", "birthday", "anniversary", "celebration", "giveaway",
            "treasure", "blessing", "donate", "charity",
            "tohfa", "uphaar", "inaam", "saugat", "khushkhabri",
            "तोहफा", "उपहार", "इनाम", "सरप्राइज", "बोनस", "सौगात",
        ],
    },
    {
        "file": "gym.mp4",
        "key_mode": "pyramid_flood",
        "flood_kind": "yellow_screen",
        "crop_norm": (0.29, 0.05, 0.42, 0.92),
        "layout": "corner_right",
        "height_frac_land": 0.44,
        "height_frac_vert": 0.30,
        "max_dur": 5.20,
        "weight": 4.8,
        "keywords": [
            "gym", "workout", "exercise", "fitness", "muscle", "strength",
            "strong", "dumbbell", "weight", "weights", "training", "bodybuilding",
            "health", "healthy", "stamina", "diet", "protein", "athlete", "pushup",
            "kasrat", "vyayam", "sehat", "mazboot", "taqat", "body",
            "जिम", "कसरत", "व्यायाम", "ताकत", "सेहत", "मजबूत", "बॉडी", "वर्कआउट",
        ],
    },
    {
        "file": "qutiion_efect.mp4",
        "key_mode": "pyramid_flood",
        "flood_kind": "vertical_gradient",
        "crop_norm": (0.28, 0.06, 0.44, 0.92),
        "layout": "corner_right",
        "height_frac_land": 0.44,
        "height_frac_vert": 0.30,
        "max_dur": 5.60,
        "weight": 4.3,
        "keywords": [
            "question", "why", "how", "doubt", "mystery", "reason", "fact",
            "research", "problem", "solution", "think", "ponder", "investigation",
            "evidence", "curious", "explain why", "why did", "how did", "what is", "secret",
            "sawaal", "sawal", "kyu", "kyon", "kaise", "akhir", "socho", "rahasya",
            "सवाल", "क्यों", "कैसे", "आखिर", "सोचो", "रहस्य", "सबूत",
        ],
    },
    {
        "file": "qution_mark_effect.mp4",
        "key_mode": "pyramid_flood",
        "flood_kind": "teal_gradient",
        "crop_norm": (0.26, 0.12, 0.48, 0.88),
        "layout": "corner_left",
        "height_frac_land": 0.42,
        "height_frac_vert": 0.28,
        "max_dur": 5.40,
        "weight": 4.3,
        "keywords": [
            "confused", "confusion", "puzzle", "puzzled", "wonder", "unbelievable",
            "really", "seriously", "strange", "weird", "baffled", "shocked",
            "why", "how", "what happened", "doubt", "question",
            "hairan", "pareshan", "samajh", "kya hua", "sach mein", "kyon",
            "हैरान", "परेशान", "समझ", "क्या हुआ", "सच", "आश्चर्य", "अजीब",
        ],
    },
    {
        "file": "pent_type_efect2.mp4",
        "key_mode": "luma_screen",
        "clip_start": 1.30,
        "layout": "full_center",
        "scale_frac": 1.0,
        "opacity": 0.42,
        "max_dur": 2.15,
        "weight": 4.4,
        "keywords": [
            "paint", "pent", "penting", "painting", "brush", "art", "artist", "draw", "drawing",
            "sketch", "design", "creative", "color", "colors", "canvas", "ink",
            "stroke", "artwork", "illustrate",
            "rang", "kala", "chitra", "tasveer", "banao",
            "पेंट", "रंग", "कला", "चित्र", "तस्वीर", "ड्राइंग", "ब्रश",
        ],
    },
    {
        "file": "hello5.mp4",
        "key_mode": "chromakey_despill",
        "chroma_hex": "0x009CFF",
        "similarity": 0.20,
        "blend": 0.07,
        "despill": "blue",
        "crop_norm": (0.14, 0.08, 0.62, 0.92),
        "layout": "corner_right",
        "height_frac_land": 0.42,
        "height_frac_vert": 0.28,
        "max_dur": 5.20,
        "weight": 4.6,
        "keywords": [
            "vampire", "dracula", "ghost", "horror", "scary", "spooky",
            "halloween", "monster", "devil", "demon", "haunted", "evil",
            "nightmare", "darkness", "creepy", "thriller",
            "bhoot", "pret", "darawna", "shaitan", "andhera",
            "भूत", "डरावना", "शैतान", "राक्षस", "अंधेरा", "खौफनाक",
        ],
    },
    {
        "file": "hello4.mp4",
        "key_mode": "chromakey_despill",
        "chroma_hex": "0x009CFF",
        "similarity": 0.16,
        "blend": 0.06,
        "despill": "blue",
        "crop_norm": (0.18, 0.0, 0.58, 1.0),
        "layout": "corner_left",
        "height_frac_land": 0.42,
        "height_frac_vert": 0.28,
        "max_dur": 5.20,
        "weight": 4.4,
        "keywords": [
            "warrior", "king", "emperor", "soldier", "army", "fighter", "hero",
            "viking", "vikings", "medieval", "empire", "kingdom", "brave", "legend",
            "conqueror", "shield", "sword", "commander",
            "raja", "yodha", "sena", "bahadur", "veer", "shoorveer", "maharaja",
            "राजा", "योद्धा", "सेना", "वीर", "बहादुर", "सम्राट", "महाराजा",
        ],
    },
    {
        "file": "hello6.mp4",
        "key_mode": "chromakey_despill",
        "chroma_hex": "0x00CCFF",
        "similarity": 0.20,
        "blend": 0.07,
        "despill": "blue",
        "crop_norm": (0.16, 0.04, 0.58, 0.96),
        "layout": "corner_left",
        "height_frac_land": 0.42,
        "height_frac_vert": 0.28,
        "max_dur": 5.20,
        "weight": 4.5,
        "keywords": [
            "lion", "tiger", "jungle", "forest", "animal", "animals", "wildlife",
            "safari", "nature", "beast", "roar", "wild", "predator",
            "sher", "janwar", "jangal", "van",
            "शेर", "जंगल", "जानवर", "वन", "शिकार", "प्रकृति",
        ],
    },
    {
        "file": "hello7.mp4",
        "key_mode": "chromakey_despill",
        "chroma_hex": "0x00CCFF",
        "similarity": 0.16,
        "blend": 0.06,
        "despill": "blue",
        "crop_norm": (0.22, 0.04, 0.58, 0.92),
        "layout": "corner_right",
        "height_frac_land": 0.42,
        "height_frac_vert": 0.28,
        "max_dur": 5.20,
        "weight": 4.4,
        "keywords": [
            "sailor", "ship", "ocean", "sea", "boat", "voyage", "cruise",
            "navy", "pirate", "port", "island", "wave", "waves", "captain",
            "pig", "cartoon", "comedy",
            "samundar", "jahaz", "naav", "pani",
            "समुद्र", "जहाज", "नाव", "सागर", "नाविक",
        ],
    },
    {
        "file": "hello8.mp4",
        "key_mode": "chromakey_despill",
        "chroma_hex": "0xFFA200",
        "similarity": 0.16,
        "blend": 0.06,
        "despill": None,
        "crop_norm": (0.14, 0.04, 0.60, 0.96),
        "layout": "corner_left",
        "height_frac_land": 0.42,
        "height_frac_vert": 0.28,
        "max_dur": 5.20,
        "weight": 4.5,
        "keywords": [
            "dog", "dogs", "puppy", "pet", "pets", "christmas", "santa",
            "holiday", "holidays", "winter", "festival", "loyal", "companion",
            "kutta", "wafadar", "tyohar", "jashn",
            "कुत्ता", "पिल्ला", "पालतू", "क्रिसमस", "त्योहार", "वफादार",
        ],
    },
    {
        "file": "hello2.mp4",
        "key_mode": "chromakey_despill",
        "chroma_hex": "0x44DA00",
        "similarity": 0.22,
        "blend": 0.08,
        "despill": "green",
        "crop_norm": (0.18, 0.26, 0.72, 0.60),
        "layout": "corner_right",
        "height_frac_land": 0.44,
        "height_frac_vert": 0.30,
        "max_dur": 5.40,
        "weight": 4.0,
        "keywords": [
            "girl", "anime", "cute", "student", "school", "kid", "kids",
            "child", "children", "daughter", "sister", "teen", "hello", "hi",
            "hey", "welcome", "namaste", "namaskar",
            "ladki", "bacche", "bacha", "beti", "behen", "swagat",
            "लड़की", "बच्चे", "छात्र", "स्कूल", "बहन", "स्वागत", "नमस्ते",
        ],
    },
    {
        "file": "hello3.mp4",
        "key_mode": "chromakey_despill",
        "chroma_hex": "0xFFFFFF",
        "similarity": 0.10,
        "blend": 0.04,
        "despill": None,
        "crop_norm": (0.62, 0.26, 0.38, 0.74),
        "layout": "peek_right",
        "height_frac_land": 0.44,
        "height_frac_vert": 0.30,
        "max_dur": 4.90,
        "weight": 3.8,
        "keywords": [
            "hello", "hey", "hi", "look", "look here", "attention", "notice",
            "wait", "listen", "peek",
            "dekho", "suno", "dhyan", "ek minute", "ruko", "idhar",
            "देखो", "सुनो", "ध्यान", "रुको", "हेलो",
        ],
    },
    {
        "file": "hello.mp4",
        "key_mode": "chromakey_despill",
        "chroma_hex": "0x68D944",
        "similarity": 0.22,
        "blend": 0.08,
        "despill": "green",
        "crop_norm": (0.30, 0.08, 0.40, 0.92),
        "layout": "corner_right",
        "height_frac_land": 0.44,
        "height_frac_vert": 0.30,
        "max_dur": 5.40,
        "weight": 3.6,
        "keywords": [
            "hello", "hi", "hey", "welcome", "greetings", "greet", "everyone",
            "friends", "guys", "dost", "dosto", "bhaiyo", "namaste", "namaskar",
            "swagat", "intro", "meet",
            "हेलो", "नमस्ते", "नमस्कार", "स्वागत", "दोस्तों", "भाइयों", "मित्रों",
        ],
    },
    {
        "file": "FootageCrate-Jail_Door_Slam_4-LQ.mov",
        "key_mode": "native_alpha",
        "layout": "full_cover",
        "clip_start": 0.25,
        "max_dur": 3.00,
        "opacity": 0.95,
        "weight": 5.4,
        "keywords": [
            "jail", "jailer", "jailor", "jailed", "jel", "prison", "prisoner", "thana",
            "police station", "lockup", "behind bars",
            "arrest", "arrested", "imprisoned", "convict", "criminal", "guilty",
            "verdict", "sentence", "custody", "crime", "culprit", "court", "kachehri",
            "qaid", "qaidi", "kaid", "kaidi", "hiraasat", "saza", "mukadma", "jailkhana", "giraftar",
            "जेल", "थाना", "क़ैद", "कैदी", "हिरासत", "सज़ा", "गिरफ़्तार", "अरेस्ट",
            "लॉकअप", "अदालत", "मुजरिम", "अपराधी",
        ],
    },
    {
        "file": "FootageCrate-Police_Car_Double_Drift_1-LQ.mov",
        "key_mode": "native_alpha",
        "layout": "mid_bottom",
        "scale_frac": 0.72,
        "scale_frac_vert": 0.96,
        "y_offset_frac": 0.21,
        "clip_start": 0.60,
        "max_dur": 4.40,
        "opacity": 0.95,
        "weight": 5.2,
        "keywords": [
            "police", "pulis", "policewala", "policeman", "cop", "cops", "patrol", "siren",
            "chase", "chasing", "pursuit", "drift", "car chase", "mafia", "gangster", "escape",
            "flee", "robbery", "heist", "highway", "smuggler", "encounter",
            "sipahi", "daroga", "thanedar", "picha", "bhaga", "chori", "dakaiti", "chor", "dakait",
            "पुलिस", "सिपाही", "दरोगा", "चोर", "डकैती", "पीछा", "माफिया", "गैंगस्टर", "सायरन",
        ],
    },
    {
        "file": "folder_gallery.mp4",
        "key_mode": "pyramid_flood",
        "flood_kind": "peach_pink",
        "crop_norm": (0.21, 0.12, 0.58, 0.82),
        "layout": "corner_right",
        "height_frac_land": 0.48,
        "height_frac_vert": 0.34,
        "max_w_frac_land": 0.42,
        "clip_start": 1.60,
        "max_dur": 4.35,
        "weight": 5.3,
        "keywords": [
            "leak", "leaked", "leek", "document", "documents", "file", "files", "folder",
            "gallery", "data", "hack", "hacked", "hacker", "haker", "password", "privacy",
            "expose", "exposed", "scandal", "database", "classified", "confidential",
            "passport", "backup", "dossier", "secret file",
            "khulasa", "parda", "faash", "dastavez",
            "फ़ाइल", "दस्तावेज़", "डॉक्यूमेंट", "लीक", "हैक", "खुलासा", "डेटा", "गैलरी", "पासवर्ड",
        ],
    },
    {
        "file": "FootageCrate-Building_Destruction_Impact_2_2-LQ.mov",
        "key_mode": "native_alpha",
        "crop_norm": (0.14, 0.05, 0.74, 0.92),
        "layout": "corner_right",
        "height_frac_land": 0.56,
        "height_frac_vert": 0.38,
        "max_w_frac_land": 0.44,
        "clip_start": 0.40,
        "max_dur": 5.60,
        "opacity": 0.95,
        "weight": 5.1,
        "keywords": [
            "building", "earthquake", "collapse", "collapsed", "demolition",
            "destroy", "destroyed", "destruction", "ruin", "disaster", "crash",
            "impact", "tower", "skyscraper", "debris", "rubble", "shatter",
            "devastation", "crumble",
            "bhukamp", "tabahi", "barbad", "imaarat", "makan", "toot",
            "ढह", "भूकंप", "तबाही", "बर्बाद", "इमारत", "मकान", "टूटना", "मलबा",
        ],
    },
    {
        "file": "FootageCrate-Nuclear_Explosion_1-LQ.mov",
        "key_mode": "native_alpha",
        "crop_norm": (0.16, 0.06, 0.70, 0.92),
        "layout": "corner_right",
        "height_frac_land": 0.60,
        "height_frac_vert": 0.42,
        "max_w_frac_land": 0.44,
        "clip_start": 0.00,
        "max_dur": 4.00,
        "opacity": 0.96,
        "weight": 5.2,
        "keywords": [
            "nuclear", "atomic", "atom", "bomb", "bamb", "explosion", "explode", "blast",
            "mushroom cloud", "hiroshima", "nagasaki", "warhead", "apocalypse",
            "radiation", "detonate",
            "parmanu", "visphot", "vishphot", "bam", "dhamaka",
            "परमाणु", "बम", "विस्फोट", "धमाका", "हमला",
        ],
    },
    {
        "file": "FootageCrate-Fighter_Jet_Fly_Away_6-4K.mov",
        "key_mode": "native_alpha",
        "layout": "full_center",
        "scale_frac": 0.98,
        "clip_start": 0.00,
        "max_dur": 2.30,
        "opacity": 0.96,
        "weight": 5.1,
        "keywords": [
            "fighter", "jet", "plane", "aircraft", "airforce", "air force",
            "rafale", "f16", "missile", "flight", "fly", "pilot", "aviation",
            "supersonic", "aerial", "airstrike", "mission", "cockpit", "squadron",
            "udaan", "jahaj", "vimaan", "fauj",
            "सेना", "फाइटर", "जेट", "विमान", "जहाज", "वायुसेना", "उड़ान", "मिसाइल",
        ],
    },
    {
        "file": "FootageCrate-Comic_Zap_Lightning-LQ.mov",
        "key_mode": "native_alpha",
        "crop_norm": (0.20, 0.04, 0.76, 0.92),
        "layout": "corner_right",
        "height_frac_land": 0.48,
        "height_frac_vert": 0.32,
        "max_w_frac_land": 0.42,
        "clip_start": 0.10,
        "max_dur": 0.90,
        "opacity": 0.97,
        "weight": 5.0,
        "keywords": [
            "zap", "lightning", "thunder", "thunderbolt", "electric", "electricity",
            "shock", "shocking", "voltage", "current", "charge", "bolt",
            "bijli", "jhatka", "karant", "shok",
            "बिजली", "झटका", "करंट", "शॉक", "तड़ित",
        ],
    },
    {
        "file": "FootageCrate-Comic_Words_Style_2_Thud-LQ.mov",
        "key_mode": "native_alpha",
        "crop_norm": (0.14, 0.04, 0.72, 0.92),
        "layout": "corner_left",
        "height_frac_land": 0.46,
        "height_frac_vert": 0.30,
        "max_w_frac_land": 0.42,
        "clip_start": 0.00,
        "max_dur": 1.00,
        "opacity": 0.97,
        "weight": 5.0,
        "keywords": [
            "thud", "punch", "slap", "knockout", "bang", "boom", "hit", "smash",
            "collision", "accident", "dropped", "slammed", "knock",
            "mukka", "thappad", "takkar", "gira", "dhadam",
            "चोट", "मुक्का", "थप्पड़", "टक्कर", "धड़ाम",
        ],
    },
    {
        "file": "FootageCrate-Looping_Busterbeam_8-LQ.mov",
        "key_mode": "native_alpha",
        "layout": "full_center",
        "scale_frac": 0.98,
        "clip_start": 0.00,
        "max_dur": 2.00,
        "opacity": 0.94,
        "weight": 4.9,
        "keywords": [
            "laser", "beam", "energy", "power", "superpower", "plasma",
            "scifi", "sci fi", "alien", "portal", "superhero", "weapon",
            "shakti", "urja", "kiran",
            "शक्ति", "ऊर्जा", "लेज़र", "किरण", "सुपरपावर", "एलियन",
        ],
    },
    {
        "file": "FootageCrate-Brief_Aerial_Fire_Burst.mov",
        "key_mode": "native_alpha",
        "crop_norm": (0.20, 0.12, 0.62, 0.78),
        "layout": "corner_left",
        "height_frac_land": 0.54,
        "height_frac_vert": 0.36,
        "max_w_frac_land": 0.44,
        "clip_start": 0.05,
        "max_dur": 1.95,
        "opacity": 0.94,
        "weight": 4.8,
        "keywords": [
            "fire", "flame", "flames", "fireball", "burst", "inferno", "heat",
            "hell", "volcano", "eruption", "lava", "ignite",
            "aag", "jwala", "aggan", "shola",
            "आग", "ज्वाला", "आगज़नी", "धधक", "शोला", "लावा",
        ],
    },
    {
        "file": "FootageCrate-Burning_Away_Ember_Particle_2.mov",
        "key_mode": "native_alpha",
        "crop_norm": (0.24, 0.08, 0.52, 0.64),
        "layout": "corner_right",
        "height_frac_land": 0.48,
        "height_frac_vert": 0.32,
        "clip_start": 0.00,
        "max_dur": 4.50,
        "opacity": 0.95,
        "weight": 4.7,
        "keywords": [
            "ash", "ashes", "burn", "burning", "burnt", "burn away", "smoke",
            "torch", "candle", "pyre", "cremation", "dissolve", "vanish",
            "raakh", "jalna", "jala", "dhuaan", "bhasm",
            "राख", "जल", "जलाना", "धुआँ", "गायब", "भस्म",
        ],
    },
    {
        "file": "FootageCrate-Slow_Motion_Embers_Hit_14-LQ.mov",
        "key_mode": "native_alpha",
        "layout": "full_cover",
        "clip_start": 0.05,
        "max_dur": 1.50,
        "opacity": 0.95,
        "weight": 4.3,
        "keywords": [
            "embers", "ember", "war", "battle", "sword", "warrior", "fight",
            "battlefield", "forge", "brave", "courage", "attack", "combat",
            "yudh", "ladai", "jang", "veer", "talwar",
            "युद्ध", "जंग", "लड़ाई", "वीर", "योद्धा", "तलवार",
        ],
    },
    {
        "file": "FootageCrate-Slow_Motion_Embers_Hit_15-LQ.mov",
        "key_mode": "native_alpha",
        "layout": "full_cover",
        "clip_start": 0.45,
        "max_dur": 3.50,
        "opacity": 0.92,
        "weight": 4.2,
        "keywords": [
            "fury", "rage", "anger", "revenge", "passion", "clash", "defeat",
            "sacrifice", "campfire", "bonfire", "angare",
            "gussa", "krodh", "badla", "balidan", "junoon",
            "गुस्सा", "क्रोध", "बदला", "बलिदान", "आक्रोश", "अंगारे",
        ],
    },
    {
        "file": "FootageCrate-Film_Burn_Overlay_2-LQ.mov",
        "key_mode": "native_alpha",
        "layout": "full_cover",
        "clip_start": 0.25,
        "max_dur": 2.05,
        "opacity": 0.78,
        "weight": 4.5,
        "keywords": [
            "film", "camera", "movie", "cinema", "retro", "vintage", "flashback",
            "memory", "memories", "past", "nostalgia", "ancient", "decade",
            "century", "puraana", "yaad", "yaadein", "beeta",
            "याद", "यादें", "पुराना", "अतीत", "सिनेमा", "फ़िल्म",
        ],
    },
    {
        "file": "footagecrate-ink-drip-transtion-3.mp4",
        "key_mode": "luma_ink_matte",
        "layout": "full_cover",
        "clip_start": 0.00,
        "max_dur": 1.20,
        "opacity": 0.68,
        "weight": 4.5,
        "keywords": [
            "ink", "darkness", "shadow", "dark", "horror", "ghost", "haunted",
            "curse", "evil", "devil", "black", "diary", "written", "inkblot",
            "syahi", "kala", "andhera", "bhoot", "shraap", "shaitaan",
            "स्याही", "काला", "अंधेरा", "भूत", "डरावना", "ख़ौफ़", "डायरी",
        ],
    },
]


def _vfx_tokenize(text: str) -> List[str]:
    if not text:
        return []
    return [t for t in _VFX_SPLIT_RE.split(str(text).lower()) if t]


def _vfx_keyword_score(tokens: List[str], joined_text: str, kw: str) -> float:
    """
    Return keyword match confidence in `[0.0, 1.0]` (`>= 0.70` means valid trigger).
    Supports exact tokens, stems/compounds (e.g. `jailer`, `jai`), and ~70%+ fuzzy
    spelling matches while blocking stopwords & suffix-only traps (`monument`/`document`).
    """
    if not tokens or not kw:
        return 0.0
    kw_clean = kw.strip().lower()
    if not kw_clean:
        return 0.0

    if " " in kw_clean:
        if f" {kw_clean} " in joined_text:
            return 1.0
        parts = [p for p in kw_clean.split() if p]
        if len(parts) >= 2:
            scores = [_vfx_keyword_score(tokens, joined_text, p) for p in parts]
            if all(s >= 0.75 for s in scores):
                return sum(scores) / float(len(scores))
        return 0.0

    is_ascii = kw_clean.isascii()
    valid = {kw_clean}
    if is_ascii:
        if len(kw_clean) >= 3:
            valid.add(kw_clean + "s")
        if len(kw_clean) >= 4:
            valid.update((
                kw_clean + "es",
                kw_clean + "ed",
                kw_clean + "ing",
                kw_clean + "ly",
                kw_clean + "er",
                kw_clean + "ers",
            ))

    best_sim = 0.0
    for tok in tokens:
        if is_ascii and tok in valid:
            return 1.0
        if (not is_ascii) and (tok == kw_clean or (len(kw_clean) >= 3 and tok.startswith(kw_clean))):
            return 1.0

        # 70%+ partial prefix / stem or high-precision typo match (never on stopwords or ultra-short words)
        if tok in _VFX_STOPWORDS or kw_clean in _VFX_STOPWORDS:
            continue
        if is_ascii and tok.isascii():
            if len(kw_clean) >= 4 and tok.startswith(kw_clean):
                return 1.0
            # 1) Leading stem/truncation covering >= 70% of keyword (e.g. "jai" -> "jail" 0.75, "polic" -> "police" 0.83)
            if len(tok) >= 3 and len(kw_clean) >= 4 and kw_clean.startswith(tok):
                prefix_ratio = len(tok) / float(len(kw_clean))
                if prefix_ratio >= 0.70:
                    best_sim = max(best_sim, prefix_ratio)
                    continue
            # 2) Long-word typo/omitted-letter tolerance (e.g. "shoping" -> "shopping", "qution" -> "question", "haker" -> "hacker")
            if len(tok) >= 5 and len(kw_clean) >= 6 and tok[0] == kw_clean[0]:
                if abs(len(tok) - len(kw_clean)) <= 3:
                    ratio = SequenceMatcher(None, tok, kw_clean).ratio()
                    if ratio >= 0.80:
                        best_sim = max(best_sim, ratio)
        elif (not is_ascii) and (not tok.isascii()):
            if len(tok) >= 3 and len(kw_clean) >= 3 and tok[0] == kw_clean[0]:
                ratio = SequenceMatcher(None, tok, kw_clean).ratio()
                if ratio >= 0.75:
                    best_sim = max(best_sim, ratio)

    return best_sim if best_sim >= 0.70 else 0.0


def _vfx_keyword_hit(tokens: List[str], joined_text: str, kw: str) -> bool:
    """Return True when `_vfx_keyword_score` clears the 70% threshold."""
    return _vfx_keyword_score(tokens, joined_text, kw) >= 0.70


def _pick_random_hello(used_set: set, last_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Randomly pick one of the 8 `hello*.mp4` VFX clips across videos."""
    all_hellos = [
        e for e in AFTER_EFFECTS_VFX_CATALOG
        if e["file"] in HELLO_VFX_FILES and resolve_vfx_path(e["file"])
    ]
    if not all_hellos:
        return None
    unused = [e for e in all_hellos if e["file"] not in used_set]
    if unused:
        return _VFX_RNG.choice(unused)
    non_last = [e for e in all_hellos if e["file"] != last_file]
    return _VFX_RNG.choice(non_last or all_hellos)


def select_after_effects_vfx(
    scene_text: str,
    scene_keyword: str = "",
    scene_idx: int = 0,
    total_scenes: int = 1,
    clip_duration: float = 5.0,
    used_vfx: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Choose the best VFX overlay from `vfx_overlays/` matching the scene script (>= 70% keyword similarity).
    Ensures one of the 8 `hello*.mp4` effects is picked randomly per multi-scene video.
    """
    if float(clip_duration or 0.0) < 1.6:
        return None

    used_vfx = used_vfx or []
    tokens = _vfx_tokenize(scene_text)
    joined_text = f" {' '.join(tokens)} " if tokens else ""
    kw_tokens = _vfx_tokenize(scene_keyword)
    joined_kw = f" {' '.join(kw_tokens)} " if kw_tokens else ""
    raw_text = str(scene_text or "").strip()

    if not tokens and not kw_tokens:
        return None

    last_file = used_vfx[-1] if used_vfx else None
    used_set = set(used_vfx)
    has_used_hello = any(f in used_set for f in HELLO_VFX_FILES)

    best_entry = None
    best_rank_score = -999.0
    best_raw_score = 0.0
    best_reason = ""
    best_has_theme = False
    best_is_weak_q = False

    for entry in AFTER_EFFECTS_VFX_CATALOG:
        fname = entry["file"]
        resolved = resolve_vfx_path(fname)
        if not resolved:
            continue

        raw_score = 0.0
        matched_kws: List[str] = []
        matched_non_greeting = False

        for kw in entry["keywords"]:
            if kw in matched_kws:
                continue
            sim = _vfx_keyword_score(tokens, joined_text, kw)
            if sim >= 0.70:
                matched_kws.append(kw)
                raw_score += float(entry["weight"]) * sim
                if kw.strip().lower() not in _HELLO_GREETING_CUES:
                    matched_non_greeting = True
                continue
            if kw_tokens:
                kw_sim = _vfx_keyword_score(kw_tokens, joined_kw, kw)
                if kw_sim >= 0.70:
                    matched_kws.append(f"kw:{kw}")
                    raw_score += float(entry["weight"]) * 0.80 * kw_sim
                    if kw.strip().lower() not in _HELLO_GREETING_CUES:
                        matched_non_greeting = True

        # Direct '?' punctuation boost for question VFX
        q_only = False
        if "?" in raw_text and fname in ("qutiion_efect.mp4", "qution_mark_effect.mp4"):
            if raw_text.endswith("?"):
                q_only = (raw_score <= 0.0)
                raw_score += 2.6
                if not matched_kws:
                    matched_kws.append("?")

        if raw_score < 2.5:
            continue

        # Never repeat the exact same VFX on back-to-back scenes
        if fname == last_file:
            continue

        rank_score = raw_score - (2.0 if fname in used_set else 0.0)
        if scene_idx == 0 and fname in HELLO_VFX_FILES:
            rank_score += 0.3

        is_weak_q = (
            fname in ("qutiion_efect.mp4", "qution_mark_effect.mp4")
            and (q_only or raw_score < 6.0)
        )

        if rank_score > best_rank_score:
            best_rank_score = rank_score
            best_raw_score = raw_score
            best_entry = entry
            best_reason = matched_kws[0] if matched_kws else "script_match"
            best_has_theme = matched_non_greeting
            best_is_weak_q = is_weak_q

    # Generic greeting hit (without a specific character theme like vampire/lion/sailor) rotates across ALL 8 hello effects
    if best_entry is not None and best_entry["file"] in HELLO_VFX_FILES and not best_has_theme:
        picked = _pick_random_hello(used_set, last_file)
        if picked:
            best_entry = picked

    # Every multi-scene video picks a random hello effect from the 8-clip pool (preferring Scene 0 intro)
    if total_scenes >= 2 and not has_used_hello:
        should_inject_hello = (
            (scene_idx == 0 and (best_entry is None or best_is_weak_q))
            or (scene_idx > 0 and best_entry is None)
        )
        if should_inject_hello:
            picked = _pick_random_hello(used_set, last_file)
            if picked:
                best_entry = picked
                best_raw_score = float(picked["weight"])
                best_reason = "video_intro_hello" if scene_idx == 0 else "video_random_hello"

    if best_entry is None or best_raw_score < 2.5:
        return None

    return {
        **best_entry,
        "path": resolve_vfx_path(best_entry["file"]),
        "reason": best_reason,
        "score": round(best_raw_score, 2),
    }


def _dilate_bool(mask: np.ndarray, steps: int = 1) -> np.ndarray:
    out = mask.copy()
    for _ in range(steps):
        n = out.copy()
        n[1:, :] |= out[:-1, :]
        n[:-1, :] |= out[1:, :]
        n[:, 1:] |= out[:, :-1]
        n[:, :-1] |= out[:, 1:]
        n[1:, 1:] |= out[:-1, :-1]
        n[:-1, :-1] |= out[1:, 1:]
        n[1:, :-1] |= out[:-1, 1:]
        n[:-1, 1:] |= out[1:, :-1]
        out = n
    return out


def _downsample_all(mask: np.ndarray, factor: int) -> np.ndarray:
    h, w = mask.shape
    nh, nw = h // factor, w // factor
    if nh < 4 or nw < 4:
        return mask
    return mask[:nh * factor, :nw * factor].reshape(nh, factor, nw, factor).all(axis=(1, 3))


def _upsample_nearest(mask: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    im = Image.fromarray(mask.astype(np.uint8) * 255).resize((target_w, target_h), Image.Resampling.NEAREST)
    return np.array(im) > 127


def _pyramid_geodesic_flood(seed: np.ndarray, trav: np.ndarray) -> np.ndarray:
    """Fast 3-level barrier-safe flood-fill in pure NumPy (~15-35ms/frame)."""
    h, w = trav.shape
    t4 = _downsample_all(trav, 4)
    s4 = np.zeros_like(t4)
    if np.any(seed[0, :]):
        s4[0, :] = True
    if np.any(seed[-1, :]):
        s4[-1, :] = True
    if np.any(seed[:, 0]):
        s4[:, 0] = True
    if np.any(seed[:, -1]):
        s4[:, -1] = True

    m4 = s4 & t4
    prev = -1
    for _ in range(110):
        nxt = _dilate_bool(m4, 1) & t4
        c = int(nxt.sum())
        if c == prev:
            break
        prev = c
        m4 = nxt

    t2 = _downsample_all(trav, 2)
    h2, w2 = t2.shape
    m2 = _upsample_nearest(m4, h2, w2) & t2
    if np.any(seed[0, :]):
        m2[0, :] |= t2[0, :]
    if np.any(seed[-1, :]):
        m2[-1, :] |= t2[-1, :]
    if np.any(seed[:, 0]):
        m2[:, 0] |= t2[:, 0]
    if np.any(seed[:, -1]):
        m2[:, -1] |= t2[:, -1]
    for _ in range(12):
        m2 = _dilate_bool(m2, 1) & t2

    m0 = _upsample_nearest(m2, h, w) & trav
    m0 |= (seed & trav)
    for _ in range(10):
        m0 = _dilate_bool(m0, 1) & trav
    return m0


def _remove_bg_flood_frame(rgb_u8: np.ndarray, flood_kind: str) -> np.ndarray:
    """Return RGBA uint8 frame with gradient/complex background cleanly removed."""
    f = rgb_u8.astype(np.float32)
    h, w, _ = f.shape
    out_rgb = f.copy()

    if flood_kind == "yellow_screen":
        ref = np.median(np.vstack([f[:4, :4].reshape(-1, 3), f[:4, -4:].reshape(-1, 3)]), axis=0)
        dist = np.linalg.norm(f - ref[None, None, :], axis=2)
        trav = dist < 52.0
        seed = np.zeros_like(trav)
        seed[0, :] = seed[-1, :] = seed[:, 0] = seed[:, -1] = True
        bg = _pyramid_geodesic_flood(seed, trav)
        near = _dilate_bool(bg, 2) & (~bg)
        alpha = np.where(bg, 0.0, 1.0).astype(np.float32)
        rim = near & (dist < 75.0)
        alpha = np.where(rim, np.clip((dist - 42.0) / 33.0, 0.0, 1.0), alpha)
        out_rgb[..., 1] = np.where(
            near,
            np.minimum(out_rgb[..., 1], np.maximum(out_rgb[..., 0], out_rgb[..., 2])),
            out_rgb[..., 1],
        )

    elif flood_kind == "neutral_grey":
        chroma = f.max(axis=2) - f.min(axis=2)
        luma = f.mean(axis=2)
        trav = (chroma <= 16.0) & (luma >= 92.0)
        seed = np.zeros_like(trav)
        seed[0, :] = seed[-1, :] = seed[:, 0] = True
        # Protect gripping fingers on right split edge; seed right border only where bright white wall shows
        seed[:, -1] = (chroma[:, -1] <= 12.0) & (luma[:, -1] >= 220.0)
        bg = _pyramid_geodesic_flood(seed, trav)
        near = _dilate_bool(bg, 2) & (~bg)
        alpha = np.where(bg, 0.0, 1.0).astype(np.float32)
        rim = near & (chroma <= 22.0) & (luma >= 92.0)
        alpha = np.where(rim, 0.35, alpha)

    elif flood_kind == "vertical_gradient":
        row_ref = np.median(np.concatenate([f[:, :6, :], f[:, -6:, :]], axis=1), axis=1)
        row_dist = np.linalg.norm(f - row_ref[:, None, :], axis=2)
        luma = f.mean(axis=2)
        gx = np.abs(np.diff(luma, axis=1, prepend=luma[:, :1]))
        gy = np.abs(np.diff(luma, axis=0, prepend=luma[:1, :]))
        edge = (gx + gy) > 22.0
        trav = (row_dist < 22.0) & (luma >= 95.0) & (~edge)
        seed = np.zeros_like(trav)
        seed[0, :] = seed[-1, :] = seed[:, 0] = seed[:, -1] = True
        bg = _pyramid_geodesic_flood(seed, trav)
        near = _dilate_bool(bg, 2) & (~bg)
        alpha = np.where(bg, 0.0, 1.0).astype(np.float32)
        soft = near & (row_dist < 38.0) & (luma >= 95.0)
        alpha = np.where(soft, np.clip((row_dist - 16.0) / 22.0, 0.0, 1.0), alpha)

    elif flood_kind == "peach_pink":
        ref = np.median(
            np.vstack([
                f[:4, :4].reshape(-1, 3),
                f[:4, -4:].reshape(-1, 3),
                f[-4:, :4].reshape(-1, 3),
                f[-4:, -4:].reshape(-1, 3),
            ]),
            axis=0,
        )
        dist = np.linalg.norm(f - ref[None, None, :], axis=2)
        luma = f.mean(axis=2)
        # Walk across flat peach backdrop and soft outer peach drop shadow while stopping cleanly at dark bezel & blue folder
        trav = (dist < 44.0) | ((dist < 84.0) & (luma > 142.0) & (f[..., 0] > f[..., 1] + 6.0))
        seed = np.zeros_like(trav)
        seed[0, :] = seed[-1, :] = seed[:, 0] = seed[:, -1] = True
        bg = _pyramid_geodesic_flood(seed, trav)
        near = _dilate_bool(bg, 3) & (~bg)
        alpha = np.where(bg, 0.0, 1.0).astype(np.float32)
        rim = near & (dist < 110.0) & (luma > 110.0)
        alpha = np.where(rim, np.clip((dist - 70.0) / 40.0, 0.0, 1.0), alpha)
        out_rgb[..., 0] = np.where(
            near & (f[..., 0] > f[..., 1] + 8.0),
            np.minimum(out_rgb[..., 0], np.maximum(out_rgb[..., 1], out_rgb[..., 2]) + 6.0),
            out_rgb[..., 0],
        )

    else:  # teal_gradient (`qution_mark_effect.mp4`)
        r_ch, g_ch, b_ch = f[..., 0], f[..., 1], f[..., 2]
        excess = np.maximum(g_ch - r_ch, b_ch - r_ch)
        trav = (r_ch < 82.0) & (excess > 28.0) & ((g_ch > r_ch + 20.0) | (b_ch > r_ch + 32.0))
        seed = np.zeros_like(trav)
        seed[0, :] = seed[:, 0] = seed[:, -1] = True
        bg = _pyramid_geodesic_flood(seed, trav)
        near = _dilate_bool(bg, 2) & (~bg)
        soft_edge = near & (r_ch < 95.0) & (excess > 16.0)
        alpha = np.where(bg, 0.0, 1.0).astype(np.float32)
        alpha = np.where(soft_edge, np.clip((38.0 - excess) / 22.0, 0.0, 1.0), alpha)
        out_rgb[..., 1] = np.where(
            near,
            np.minimum(out_rgb[..., 1], np.maximum(out_rgb[..., 0], out_rgb[..., 2]) + 10.0),
            out_rgb[..., 1],
        )
        out_rgb[..., 2] = np.where(
            near,
            np.minimum(out_rgb[..., 2], out_rgb[..., 0] + 22.0),
            out_rgb[..., 2],
        )

    a_u8 = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    a_img = Image.fromarray(a_u8).filter(ImageFilter.GaussianBlur(radius=0.65))
    rgba = np.dstack([np.clip(out_rgb, 0, 255).astype(np.uint8), np.array(a_img)])
    return rgba


def _compute_overlay_geometry(vfx_info: Dict[str, Any], target_size: Tuple[int, int]) -> Dict[str, Any]:
    """Compute crisp responsive overlay `(w, h, x_expr, y_expr)` for 16:9 and 9:16 targets."""
    tw, th = target_size
    is_vertical = th > tw
    layout = vfx_info.get("layout", "corner_right")

    if layout == "full_cover":
        return {
            "scale_filter": f"scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th}",
            "x_expr": "0",
            "y_expr": "0",
            "ow": tw,
            "oh": th,
        }

    if layout in ("full_bottom", "full_center", "mid_bottom"):
        sf = float(
            vfx_info.get("scale_frac_vert" if is_vertical else "scale_frac", 0.95)
            or vfx_info.get("scale_frac", 0.95)
        )
        ow = max(64, int(round(tw * sf)) & ~1)
        if layout == "full_bottom":
            y_expr = "H-h"
        elif layout == "mid_bottom":
            y_off = max(8, int(round(th * float(vfx_info.get("y_offset_frac", 0.20)))))
            y_expr = f"H-h-{y_off}"
        else:
            y_expr = "(H-h)/2"
        return {
            "scale_filter": f"scale={ow}:-2",
            "x_expr": "(W-w)/2",
            "y_expr": y_expr,
            "ow": tw,
            "oh": th,
        }

    h_frac = float(vfx_info.get("height_frac_vert" if is_vertical else "height_frac_land", 0.42))
    oh = max(96, int(round(th * h_frac)) & ~1)
    # Conservative max width so character never covers center subtitles
    max_w_frac = float(
        vfx_info.get("max_w_frac_vert" if is_vertical else "max_w_frac_land", 0.44 if is_vertical else 0.34)
    )
    max_w = int(tw * max_w_frac) & ~1
    margin_x = max(8, int(tw * 0.015))

    if layout == "peek_right":
        y_expr = f"{int(th * 0.42)}" if is_vertical else "H-h"
        x_expr = "W-w"
    elif layout == "corner_left":
        y_expr = "H-h"
        x_expr = str(margin_x)
    else:  # corner_right
        y_expr = "H-h"
        x_expr = f"W-w-{margin_x}"

    return {
        "scale_filter": f"scale=-2:{oh}",
        "x_expr": x_expr,
        "y_expr": y_expr,
        "oh": oh,
        "max_w": max_w,
    }


def _probe_video_dims(path: str) -> Tuple[int, int, float]:
    """Return `(width, height, duration)` of a video file."""
    try:
        res = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height:format=duration",
                "-of", "csv=p=0:s=,", path,
            ],
            capture_output=True, text=True, timeout=15,
        )
        lines = [ln.strip() for ln in res.stdout.splitlines() if ln.strip()]
        w, h, dur = 1280, 720, 5.0
        for ln in lines:
            parts = ln.split(",")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                w, h = int(parts[0]), int(parts[1])
            elif len(parts) == 1:
                try:
                    dur = float(parts[0])
                except Exception:
                    pass
        return w, h, dur
    except Exception:
        return 1280, 720, 5.0


def _resolve_crop_box(src_w: int, src_h: int, vfx_info: Dict[str, Any]) -> Tuple[str, int, int]:
    """Compute even-dimension FFmpeg crop prefix and effective `(eff_w, eff_h)` from `crop_norm`."""
    cn = vfx_info.get("crop_norm")
    if not cn or len(cn) != 4:
        return "", src_w, src_h
    xf, yf, wf, hf = cn
    cx = max(0, int(round(src_w * float(xf))) & ~1)
    cy = max(0, int(round(src_h * float(yf))) & ~1)
    cw = max(32, min(src_w - cx, int(round(src_w * float(wf))) & ~1))
    ch = max(32, min(src_h - cy, int(round(src_h * float(hf))) & ~1))
    return f"crop={cw}:{ch}:{cx}:{cy},", cw, ch


def apply_after_effects_vfx_overlay(
    scene_mp4: str,
    vfx_info: Dict[str, Any],
    clip_duration: float,
    target_size: Tuple[int, int],
    job_dir: str = ".",
) -> bool:
    """
    Remove background from `vfx_info['path']` and overlay it on top of `scene_mp4`,
    preserving exact `scene_mp4` duration, `target_size`, and Narration+SFX audio.
    """
    if not scene_mp4 or not os.path.exists(scene_mp4) or not vfx_info:
        return False
    vfx_path = vfx_info.get("path") or resolve_vfx_path(vfx_info.get("file", ""))
    if not vfx_path or not os.path.exists(vfx_path):
        return False

    tw, th = target_size
    safe_dur = max(0.5, float(clip_duration or 5.0))
    key_mode = vfx_info.get("key_mode", "chromakey_despill")
    clip_start = float(vfx_info.get("clip_start", 0.0))
    max_dur = float(vfx_info.get("max_dur", 5.5))
    overlay_dur = min(safe_dur, max_dur)
    src_w, src_h, src_dur = _probe_video_dims(vfx_path)
    if src_dur > clip_start + 0.30:
        overlay_dur = min(overlay_dur, max(0.45, src_dur - clip_start - 0.02))
    fade_in = min(0.20, overlay_dur * 0.15)
    fade_out = min(0.30 if key_mode not in ("luma_screen", "luma_ink_matte") else 0.45, overlay_dur * 0.25)
    fade_out_st = max(fade_in, overlay_dur - fade_out)

    geom = _compute_overlay_geometry(vfx_info, target_size)
    crop_filter, eff_w, eff_h = _resolve_crop_box(src_w, src_h, vfx_info)

    # Compute responsive target size honoring max_w guard on narrow 9:16 screens
    if vfx_info.get("layout", "corner_right") not in ("full_bottom", "full_center", "full_cover", "mid_bottom"):
        oh = int(geom["oh"]) & ~1
        ow = max(32, int(round(oh * (eff_w / max(1, eff_h)))) & ~1)
        max_w = int(geom.get("max_w", tw)) & ~1
        if ow > max_w:
            ow = max_w
            oh = max(32, int(round(ow * (eff_h / max(1, eff_w)))) & ~1)
        scale_filter = f"scale={ow}:{oh}:flags=lanczos"
    else:
        ow = oh = 0
        scale_filter = geom["scale_filter"]

    tmp_out = os.path.abspath(os.path.join(job_dir, f"tmp_vfx_out_{os.getpid()}_{id(vfx_info)}.mp4"))

    try:
        if key_mode == "pyramid_flood":
            fps = 15
            dec_cmd = [
                "ffmpeg", "-y", "-ss", f"{clip_start:.3f}", "-t", f"{overlay_dur:.3f}",
                "-i", os.path.abspath(vfx_path),
                "-vf", f"{crop_filter}scale={ow}:{oh}:flags=lanczos,fps={fps}",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1",
            ]
            enc_cmd = [
                "ffmpeg", "-y",
                "-i", os.path.abspath(scene_mp4),
                "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{ow}x{oh}", "-r", str(fps), "-i", "pipe:0",
                "-filter_complex", f"[0:v][1:v]overlay=x={geom['x_expr']}:y={geom['y_expr']}:eof_action=pass[outv]",
                "-map", "[outv]", "-map", "0:a?",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
                "-pix_fmt", "yuv420p", "-threads", "1", "-c:a", "copy",
                "-t", f"{safe_dur:.3f}",
                tmp_out,
            ]
            dec_proc = subprocess.Popen(dec_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            enc_proc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

            frame_bytes = ow * oh * 3
            total_frames = max(1, int(round(overlay_dur * fps)))
            flood_kind = vfx_info.get("flood_kind", "neutral_grey")
            idx = 0
            enc_err = b""
            try:
                while idx < total_frames:
                    raw = dec_proc.stdout.read(frame_bytes)
                    if not raw or len(raw) < frame_bytes:
                        break
                    rgb = np.frombuffer(raw, dtype=np.uint8).reshape((oh, ow, 3))
                    rgba = _remove_bg_flood_frame(rgb, flood_kind)
                    t_cur = idx / float(fps)
                    f_mul = 1.0
                    if t_cur < fade_in and fade_in > 0:
                        f_mul = t_cur / fade_in
                    elif t_cur > fade_out_st and fade_out > 0:
                        f_mul = max(0.0, (overlay_dur - t_cur) / fade_out)
                    if f_mul < 0.999:
                        rgba = rgba.copy()
                        rgba[..., 3] = np.clip(rgba[..., 3].astype(np.float32) * f_mul, 0, 255).astype(np.uint8)
                    try:
                        enc_proc.stdin.write(rgba.tobytes())
                    except (BrokenPipeError, ValueError, OSError):
                        break
                    idx += 1
            finally:
                if dec_proc.stdout:
                    try:
                        dec_proc.stdout.close()
                    except Exception:
                        pass
                    dec_proc.stdout = None
                if enc_proc.stdin:
                    try:
                        enc_proc.stdin.flush()
                    except Exception:
                        pass
                    try:
                        enc_proc.stdin.close()
                    except Exception:
                        pass
                    enc_proc.stdin = None
                if enc_proc.stderr:
                    try:
                        enc_err = enc_proc.stderr.read()
                    except Exception:
                        enc_err = b""
                    try:
                        enc_proc.stderr.close()
                    except Exception:
                        pass
                    enc_proc.stderr = None
                try:
                    dec_proc.wait(timeout=30)
                except Exception:
                    pass
                try:
                    enc_proc.wait(timeout=180)
                except Exception:
                    try:
                        enc_proc.kill()
                    except Exception:
                        pass

            if enc_proc.returncode == 0 and os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 1000:
                os.replace(tmp_out, scene_mp4)
                return True
            if enc_err:
                print(f"⚠️ [Ultra VFX Overlay Notice]: {enc_err.decode(errors='ignore')[-250:]}")
            return False

        # Pure FFmpeg C filter chains (`native_alpha`, `split_track_matte`, `chromakey_despill`, `luma_screen`)
        input_args = ["-i", os.path.abspath(scene_mp4)]
        fade_chain = (
            f"setpts=PTS-STARTPTS,"
            f"fade=t=in:st=0:d={fade_in:.3f}:alpha=1,"
            f"fade=t=out:st={fade_out_st:.3f}:d={fade_out:.3f}:alpha=1"
        )

        if key_mode == "split_track_matte":
            m_off = float(vfx_info.get("matte_offset", 6.0))
            input_args.extend(["-ss", f"{clip_start:.3f}", "-t", f"{overlay_dur:.3f}", "-i", os.path.abspath(vfx_path)])
            input_args.extend(["-ss", f"{clip_start + m_off:.3f}", "-t", f"{overlay_dur:.3f}", "-i", os.path.abspath(vfx_path)])
            fg_chain = (
                f"[1:v]{crop_filter}setpts=PTS-STARTPTS,format=yuva420p[vfill];"
                f"[2:v]{crop_filter}setpts=PTS-STARTPTS,format=gray[vmatte];"
                f"[vfill][vmatte]alphamerge,{scale_filter},{fade_chain}[vfx];"
                f"[0:v][vfx]overlay=x={geom['x_expr']}:y={geom['y_expr']}:eof_action=pass[outv]"
            )
        elif key_mode == "native_alpha":
            input_args.extend(["-ss", f"{clip_start:.3f}", "-t", f"{overlay_dur:.3f}", "-i", os.path.abspath(vfx_path)])
            op = float(vfx_info.get("opacity", 0.95))
            fg_chain = (
                f"[1:v]{crop_filter}format=rgba,{scale_filter},colorchannelmixer=aa={op:.2f},"
                f"{fade_chain}[vfx];"
                f"[0:v][vfx]overlay=x={geom['x_expr']}:y={geom['y_expr']}:eof_action=pass[outv]"
            )
        elif key_mode == "luma_screen":
            input_args.extend(["-ss", f"{clip_start:.3f}", "-t", f"{overlay_dur:.3f}", "-i", os.path.abspath(vfx_path)])
            op = float(vfx_info.get("opacity", 0.42))
            fg_chain = (
                f"[1:v]lumakey=threshold=0.14:tolerance=0.20:softness=0.15,"
                f"format=rgba,colorchannelmixer=aa={op:.2f},scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},"
                f"{fade_chain}[vfx];"
                f"[0:v][vfx]overlay=x=0:y=0:eof_action=pass[outv]"
            )
        elif key_mode == "luma_ink_matte":
            input_args.extend(["-ss", f"{clip_start:.3f}", "-t", f"{overlay_dur:.3f}", "-i", os.path.abspath(vfx_path)])
            op = float(vfx_info.get("opacity", 0.78))
            fg_chain = (
                f"[1:v]format=rgb24,negate,format=rgba,"
                f"lumakey=threshold=0.06:tolerance=0.24:softness=0.22,"
                f"lutrgb=r=10:g=10:b=16,colorchannelmixer=aa={op:.2f},"
                f"scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},"
                f"{fade_chain}[vfx];"
                f"[0:v][vfx]overlay=x=0:y=0:eof_action=pass[outv]"
            )
        else:  # chromakey_despill
            input_args.extend(["-ss", f"{clip_start:.3f}", "-t", f"{overlay_dur:.3f}", "-i", os.path.abspath(vfx_path)])
            chex = vfx_info.get("chroma_hex", "0x00FF00")
            sim = float(vfx_info.get("similarity", 0.20))
            bld = float(vfx_info.get("blend", 0.07))
            desp = vfx_info.get("despill")
            desp_flt = f",despill=type={desp}:mix=0.85:expand=0.15" if desp in ("green", "blue") else ""
            fg_chain = (
                f"[1:v]{crop_filter}colorkey={chex}:{sim:.2f}:{bld:.2f}{desp_flt},"
                f"{scale_filter},{fade_chain}[vfx];"
                f"[0:v][vfx]overlay=x={geom['x_expr']}:y={geom['y_expr']}:eof_action=pass[outv]"
            )

        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-filter_complex", fg_chain,
            "-map", "[outv]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-pix_fmt", "yuv420p", "-threads", "1", "-c:a", "copy",
            "-t", f"{safe_dur:.3f}",
            tmp_out,
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=180)
        if res.returncode == 0 and os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 1000:
            os.replace(tmp_out, scene_mp4)
            return True
        if res.stderr:
            print(f"⚠️ [Ultra VFX Overlay Notice]: {res.stderr.decode(errors='ignore')[-250:]}")
    except Exception as e_vfx:
        print(f"⚠️ [Ultra VFX Overlay Error]: {e_vfx}")
    finally:
        if os.path.exists(tmp_out):
            try:
                os.remove(tmp_out)
            except Exception:
                pass
    return False
