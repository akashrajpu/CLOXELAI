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
    "कहा", "वहां", "यहाँ", "किसी", "कुछ", "बहुत", "मगर", "लेकिन", "परंतु", "ताकि", "क्योंकि", "तथा", "एवं", "या", "अथवा",
    # Hinglish Stopwords
    "yeh", "woh", "ye", "wo", "tha", "thi", "the", "hai", "hain", "ho", "hua", "hui", "hue", "hota", "hoti", "hote",
    "ka", "ke", "ki", "ko", "se", "me", "mein", "ne", "par", "pe", "aur", "ek", "bhi", "to", "toh", "jo", "kar", "diya",
    "liya", "gaya", "gayi", "gaye", "is", "us", "apne", "apni", "apna", "in", "un", "sakte", "sakta", "sakti",
    "raha", "rahi", "rahe", "tak", "jab", "tab", "ab", "sab", "kya", "kyon", "kyu", "kaha", "kahte", "jaise", "kuch",
    "bahut", "lekin", "magar", "bina", "sirf", "wali", "wale", "wala", "mil", "sakti", "rahe", "the", "gaya", "fir",
    "phir", "kaise", "kahan", "kisne", "jisko", "jisme", "jahan", "wahan", "yahan", "unka", "unki", "unke", "iska", "iski", "iske",
    "ya", "athwa", "unhone", "inhone", "sabka", "sabki", "sabke", "puri", "poori", "akele", "kisi", "aisa", "aisi", "aise", "shuru", "khatam",
    "nahi", "na", "samne", "saamne", "karte", "karta", "karti", "pata", "baad", "pehle", "hi"
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
    "city": "modern metropolis skyline illuminated night",
    
    # Motivation, Life, Success, Time & Philosophy
    "जिंदगी": "life journey destiny human path",
    "ज़िंदगी": "life journey destiny human path",
    "zindagi": "life journey destiny human path",
    "life": "life journey destiny human path",
    "समय": "time clock hourglass passing ticking",
    "samay": "time clock hourglass passing ticking",
    "time": "time clock hourglass passing ticking",
    "वक्त": "time clock ticking passing destiny",
    "waqt": "time clock ticking passing destiny",
    "इंसान": "human solitary person thinking silhouette",
    "insan": "human solitary person thinking silhouette",
    "आदमी": "human solitary person thinking silhouette",
    "सफल": "success summit mountain victory triumph champion",
    "सफलता": "success summit mountain victory triumph champion",
    "safalta": "success summit mountain victory triumph champion",
    "success": "success summit mountain victory triumph champion",
    "कामयाबी": "success triumph victory achievement celebration",
    "kamyabi": "success triumph victory achievement celebration",
    "अमीर": "wealth luxury gold rich lifestyle mansion",
    "ameer": "wealth luxury gold rich lifestyle mansion",
    "rich": "wealth luxury gold rich lifestyle mansion",
    "गरीब": "humble struggle rain solitary road",
    "gareeb": "humble struggle rain solitary road",
    "poor": "humble struggle rain solitary road",
    "फर्क": "decision crossroads choice two paths balance",
    "fark": "decision crossroads choice two paths balance",
    "मेहनत": "hardwork dedication gym focus sweat",
    "mehnat": "hardwork dedication gym focus sweat",
    "संघर्ष": "struggle uphill climb perseverance endurance",
    "sangharsh": "struggle uphill climb perseverance endurance",
    "सपना": "dream ambition stars galaxy visionary",
    "सपने": "dream ambition stars galaxy visionary",
    "sapna": "dream ambition stars galaxy visionary",
    "sapne": "dream ambition stars galaxy visionary",
    "dream": "dream ambition stars galaxy visionary",
    "लक्ष्य": "target focus goal arrow archery",
    "lakshya": "target focus goal arrow archery",
    "goal": "target focus goal arrow archery",
    "हार": "defeat failure rising comeback perseverance",
    "haar": "defeat failure rising comeback perseverance",
    "जीत": "victory triumphant winner trophy glory",
    "jeet": "victory triumphant winner trophy glory",
    "सोच": "mind thoughts brain neural deep thinking",
    "soch": "mind thoughts brain neural deep thinking",
    "डर": "dark storm lightning fear courage overcoming",
    "dar": "dark storm lightning fear courage overcoming",
    "घंटे": "clock ticking 24 hours sunrise sunset",
    "ghante": "clock ticking 24 hours sunrise sunset",
    "दिन": "bright daylight morning sunrise horizon",
    "din": "bright daylight morning sunrise horizon",
    "रात": "dark starry night moonlight shadow",
    "raat": "dark starry night moonlight shadow",

    # Political, Leaders, After Effects & Contrast Keywords
    "dictator": "authoritarian dictator ruler throne",
    "taanashah": "authoritarian dictator ruler throne",
    "tanashah": "authoritarian dictator ruler throne",
    "तानाशाह": "authoritarian dictator ruler throne",
    "hero": "national hero visionary savior champion",
    "हीरो": "national hero visionary savior champion",
    "नायक": "national hero visionary savior champion",
    "asli": "authentic real true heroic",
    "असली": "authentic real true heroic",
    "nakli": "fake fraudulent illusion deceptive",
    "नकली": "fake fraudulent illusion deceptive",
    "sach": "hidden truth revelation mystery light",
    "sacchai": "hidden truth revelation mystery light",
    "सच्चाई": "hidden truth revelation mystery light",
    "सच": "hidden truth revelation mystery light",
    "satya": "hidden truth revelation mystery light",
    "सत्य": "hidden truth revelation mystery light",
    "jhooth": "dark lie deceit illusion shadow",
    "झूठ": "dark lie deceit illusion shadow",
    "neta": "powerful politician leader speech podium",
    "नेता": "powerful politician leader speech podium",
    "rajneeti": "political election power struggle",
    "राजनीति": "political election power struggle",
    "modi": "Narendra Modi Prime Minister leader",
    "मोदी": "Narendra Modi Prime Minister leader",
    "gandhi": "Mahatma Gandhi freedom struggle",
    "गांधी": "Mahatma Gandhi freedom struggle",
    "bhashan": "leader speech podium stage address crowd",
    "भाषण": "leader speech podium stage address crowd",
    "chunav": "election political campaign rally crowd",
    "चुनाव": "election political campaign rally crowd",
    "sansad": "parliament building capitol democracy",
    "संसद": "parliament building capitol democracy",
    "shaktishali": "powerful mighty colossal majestic",

    # Comprehensive Historical, Civilizational, Modern & Constitutional Expansions
    "सभ्यताओं": "ancient civilization indus valley majestic heritage temples architecture",
    "सभ्यता": "ancient civilization indus valley majestic heritage temples architecture",
    "सभ्यताएं": "ancient civilization indus valley majestic heritage temples architecture",
    "civilization": "ancient civilization indus valley majestic heritage temples architecture",
    "हजारों सालों": "ancient history thousands of years golden era",
    "हजारों": "ancient historical heritage thousands of years",
    "आक्रमणों": "foreign invasion historical conquerors medieval warfare battle",
    "आक्रमण": "foreign invasion historical conquerors medieval warfare battle",
    "गुलामी": "colonial oppression captivity chains historical era",
    "गुलाम": "colonial oppression captivity historical era",
    "समृद्ध": "flourishing prosperous golden era rich heritage",
    "राजाओं": "royal ancient maharajas kings throne dynasty emperor",
    "साम्राज्यों": "grand royal empire ancient dynasties kingdoms majestic",
    "कहानियां": "legendary historical saga epic chronicle",
    "दास्तान": "epic historical chronicle long journey",
    "सत्ता": "royal throne power crown emperor palace",
    "बदलाव": "historical transformation revolution new era",
    "अंग्रेजों": "british colonial raj east india company 18th century historical fleet",
    "अंग्रेज": "british colonial raj east india company historical era",
    "ब्रिटिश": "british empire colonial rule historical fleet maps",
    "प्रभाव": "expanding colonial influence historical maps empire",
    "अधीन": "colonial dominion historical empire rule",
    "विद्रोह": "historic revolt rebellion 1857 soldiers freedom fighters",
    "प्रथम स्वतंत्रता संग्राम": "first war of independence 1857 freedom struggle battle",
    "विभाजन": "historic partition of india 1947 refugee migration historical documentary",
    "लाखों लोगों": "millions of people historical migration documentary",
    "लाखों": "millions of people historical migration documentary",
    "संविधान": "constitution of india preamble supreme court sacred law book",
    "लोकतांत्रिक": "democratic sovereign republic parliament citizens voting",
    "गणराज्य": "sovereign republic celebration national emblem ashoka",
    "विज्ञान": "modern science laboratory research technology innovation",
    "तकनीक": "modern advanced technology digital tech innovation",
    "अंतरिक्ष": "isro satellite rocket launch space cosmos galaxy exploration",
    "अर्थव्यवस्था": "modern economy financial growth stock market city skyline",
    "पहचान": "global recognition international pride modern power",
    "सैन्य शक्ति": "indian military armed forces army tanks missiles defense warship",
    "सैन्य": "indian military armed forces army tanks missiles defense warship",
    "शक्ति": "powerful national strength military defense force",
    "आर्थिक विकास": "modern economic growth city skyscrapers financial power infrastructure",
    "आर्थिक": "modern economic growth city skyscrapers financial power infrastructure",
    "विकास": "infrastructure high-tech modern development cityscape",
    "लोकतंत्र": "democracy parliament voting citizens people rights freedom",
    "नागरिकों": "proud citizens people of india unity diversity democracy",
    "नागरिक": "proud citizen people of india democracy",
    "अधिकार": "fundamental citizen rights human freedom equality law",
    "न्याय व्यवस्था": "supreme court justice scales balance lady justice law and order",
    "न्याय": "supreme court justice scales balance lady justice law and order",
    "व्यवस्था": "legal judicial system supreme court constitution law",
    "संस्थाएं": "national democratic institutions parliament supreme court ashoka pillar",
    "संस्थान": "national democratic institutions parliament supreme court",
    "संस्था": "national democratic institutions parliament supreme court",
    "सवाल": "deep philosophical mystery question thinker reflection",
    "कहानी": "epic historical journey narrative chronicle",
    "अगला अध्याय": "futuristic rising india new chapter golden era horizon",
    "आने वाला समय": "future vision rising nation sunrise golden horizon",
    "भविष्य": "futuristic high-tech modern india shining horizon",
    "शक्तिशाली": "powerful mighty colossal majestic",
    "dushman": "enemy fierce rival opponent",
    "दुश्मन": "enemy fierce rival opponent",
    "dost": "trusted allies friends companion",
    "दोस्त": "trusted allies friends companion",
    "kahaani": "epic story legend chronicle",
    "कहानी": "epic story legend chronicle",
    "katha": "mythological legend epic chronicle",
    "कथा": "mythological legend epic chronicle",

    # Characters, Epics, Battles, Nature & Monuments
    "नरेंद्र": "Narendra Modi leader",
    "मोदी": "Narendra Modi leader",
    "pratap": "Maharana Pratap warrior king",
    "प्रताप": "Maharana Pratap warrior king",
    "maharana": "Maharana Pratap warrior king",
    "महाराणा": "Maharana Pratap warrior king",
    "shivaji": "Shivaji Maharaj warrior king",
    "शिवाजी": "Shivaji Maharaj warrior king",
    "सेना": "mighty army soldiers battalion",
    "sena": "mighty army soldiers battalion",
    "yudh": "epic battle warrior conflict",
    "yuddh": "epic battle warrior conflict",
    "युद्ध": "epic battle warrior conflict",
    "larai": "fierce battle war clash",
    "लड़ाई": "fierce battle war clash",
    "kila": "ancient fort castle fortress",
    "किला": "ancient fort castle fortress",
    "mahal": "royal palace kingdom castle",
    "महल": "royal palace kingdom castle",
    "talwar": "ancient sword warrior blade",
    "तलवार": "ancient sword warrior blade",
    "ghoda": "war horse stallion galloping",
    "घोड़ा": "war horse stallion galloping",
    "sher": "lion fierce predator royal",
    "शेर": "lion fierce predator royal",
    "ram": "Lord Ram divine bow radiance",
    "राम": "Lord Ram divine bow radiance",
    "krishna": "Lord Krishna divine flute aura",
    "कृष्ण": "Lord Krishna divine flute aura",
    "shiva": "Lord Shiva mahadev cosmic meditation",
    "शिव": "Lord Shiva mahadev cosmic meditation",
    "mahadev": "Lord Shiva mahadev cosmic meditation",
    "महादेव": "Lord Shiva mahadev cosmic meditation",
    "hanuman": "Lord Hanuman mace power aura",
    "हनुमान": "Lord Hanuman mace power aura",
    "aag": "fiery burning flames inferno",
    "आग": "fiery burning flames inferno",
    "pani": "flowing water ocean river",
    "पानी": "flowing water ocean river",
    "bijli": "thunderstorm lightning neon sparks",
    "बिजली": "thunderstorm lightning neon sparks",
    "dhoka": "dark betrayal treason shadow",
    "धोखा": "dark betrayal treason shadow",
    "desh": "nation patriotic homeland",
    "देश": "nation patriotic homeland",
    "bharat": "India national heritage",
    "भारत": "India national heritage"
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
        elif any(k in t_low or k in cat_lower for k in ["after effect", "after iffect", "after effects", "vfx", "motion graphic"]):
            ae_angles = [
                ["futuristic", "neon", "cyberpunk", "hologram", "cinematic"],
                ["motion", "abstract", "particles", "glow", "artistic"],
                ["epic", "energy", "burst", "quantum", "sci-fi"],
                ["dynamic", "speed", "light", "tunnel", "hyperdrive"],
                ["dark", "techno", "glitch", "digital", "matrix"],
                ["golden", "luxury", "streak", "plexus", "nebula"],
                ["surreal", "fluid", "smoke", "waves", "atmospheric"],
                ["geometric", "laser", "prism", "cyber", "vortex"]
            ]
            visual_parts = ae_angles[scene_idx % len(ae_angles)]
        elif any(k in t_low or k in cat_lower for k in ["cartoon", "anime", "animation", "comic"]):
            visual_parts = ["vibrant", "3d", "animated", "colorful", "cartoon", "adventure"]
        else:
            visual_parts = ["cinematic", "dramatic", "atmospheric", "detailed"]
            
    scene_visual_phrase = " ".join(visual_parts)
    
    # Context-aware suffixes
    is_after_effects = any(k in cat_lower or k in topic_clean.lower() for k in ["after effect", "after iffect", "after effects", "vfx", "motion graphic", "cgi"])
    is_cartoon = any(k in cat_lower or k in topic_clean.lower() for k in ["cartoon", "anime", "animation", "comic"])
    is_space = any(k in cat_lower or k in topic_clean.lower() for k in ["space", "galaxy", "universe", "cosmos"])
    is_history = any(k in cat_lower or k in topic_clean.lower() for k in ["history", "war", "battle", "king", "warrior", "ancient"])
    
    if is_after_effects:
        bg_suffix = "cinematic 3D VFX motion graphics dramatic wallpaper 8k"
        fg_suffix = "epic cinematic VFX character motion portrait 8k"
    elif is_cartoon:
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


ENG_VISUAL_STOPS = {
    'the', 'is', 'was', 'were', 'are', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'a', 'an', 'and',
    'or', 'but', 'if', 'because', 'as', 'what', 'which', 'this', 'that', 'these', 'those', 'then',
    'so', 'than', 'such', 'both', 'through', 'about', 'for', 'with', 'by', 'at', 'from', 'into',
    'over', 'after', 'beneath', 'under', 'above', 'of', 'to', 'in', 'on', 'it', 'its', 'he', 'she',
    'they', 'them', 'their', 'his', 'her', 'my', 'your', 'our', 'we', 'you', 'i', 'me', 'him',
    'who', 'whom', 'whose', 'how', 'when', 'where', 'why', 'all', 'any', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'very', 'else',
    'either', 'neither', 'vs', 'versus', 'ya'
}


def translate_to_visual_english(text: str, topic: str = "") -> str:
    """
    Translates Hindi and Hinglish script/scene text into rich, highly descriptive English visual keywords (8-12 words)
    for Pinterest and web media search in Ultra After Effects mode.
    Guarantees detailed, scene-specific English visual phrases covering micro-details,
    without generic topic overshadowing.
    """
    raw = (text or '').strip()
    topic_raw = (topic or '').strip()
    if not raw and not topic_raw:
        return "cinematic animation"

    has_devanagari = bool(re.search(r'[\u0900-\u097F]', raw))
    raw_lower = raw.lower()

    translated_scene_text = raw
    
    # 1. Live Dynamic Translation for arbitrary Hindi/Hinglish text
    if has_devanagari or any(w in raw_lower.split() for w in HINDI_STOPWORDS):
        # Try Google Translate first (most accurate for complete sentences)
        try:
            g_url = 'https://translate.googleapis.com/translate_a/single'
            g_params = {'client': 'gtx', 'sl': 'auto', 'tl': 'en', 'dt': 't', 'q': raw[:280]}
            g_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            g_resp = requests.get(g_url, params=g_params, headers=g_headers, timeout=3.5)
            if g_resp.status_code == 200:
                g_data = g_resp.json()
                g_tr = "".join([segment[0] for segment in g_data[0] if segment and segment[0]])
                if g_tr and g_tr.strip():
                    translated_scene_text = g_tr.strip()
        except Exception:
            pass

        # Secondary API: MyMemory
        if translated_scene_text == raw:
            try:
                url = 'https://api.mymemory.translated.net/get'
                params = {'q': raw[:250], 'langpair': 'hi|en'}
                resp = requests.get(url, params=params, timeout=3.0)
                if resp.status_code == 200:
                    tr = resp.json().get('responseData', {}).get('translatedText', '')
                    if tr and not tr.startswith('MYMEMORY WARNING') and tr.strip():
                        translated_scene_text = tr.strip()
            except Exception:
                pass

    # 2. Extract concepts directly from the scene text (sorted longest key first)
    extracted_visual_words = []
    seen = set()

    sorted_concept_keys = sorted(CONCEPT_MAP.keys(), key=lambda x: len(x), reverse=True)
    for ck in sorted_concept_keys:
        if ck in raw_lower:
            concept_expansion = CONCEPT_MAP[ck]
            for cw in concept_expansion.split():
                cw_l = cw.lower()
                if cw_l not in seen and cw_l not in ENG_VISUAL_STOPS:
                    seen.add(cw_l)
                    extracted_visual_words.append(cw)

    # 3. If live translation succeeded, extract substantive English visual words from translated text
    if translated_scene_text and translated_scene_text != raw:
        tr_words = [re.sub(r'[^a-zA-Z0-9]', '', w) for w in translated_scene_text.split()]
        for tw in tr_words:
            tw_l = tw.lower()
            if len(tw_l) >= 3 and tw_l not in seen and tw_l not in ENG_VISUAL_STOPS and tw_l not in HINDI_STOPWORDS:
                seen.add(tw_l)
                extracted_visual_words.append(tw)

    # 4. Context anchor (e.g. India) if not already present
    if "india" not in seen and topic_raw and "india" in topic_raw.lower():
        extracted_visual_words.append("India")
        seen.add("india")

    # Retain up to 10-12 rich, descriptive words (instead of previous 5 words)
    res = ' '.join(extracted_visual_words[:11]).strip()
    return res or (re.sub(r'[^a-zA-Z0-9\s]', '', translated_scene_text).strip() or "cinematic animation")


PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "jqGZN1a4uHQFpxqdFAdVaD1l1eyjW1kzHqtdlNJ1TPkSmOEXcbAL7yhN")

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
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
            return False
            
        with Image.open(file_path) as img:
            img.verify()
            
        with Image.open(file_path) as img:
            if img.width < 350 or img.height < 350:
                raise ValueError("Image is too small (likely a thumbnail or tracking pixel)")
                
            needs_resave = False
            # If saving to .jpg / .jpeg, ensure mode is RGB (not RGBA/P/LA) to prevent OSError
            is_jpeg = file_path.lower().endswith(('.jpg', '.jpeg'))
            if is_jpeg and img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    rgb_img.paste(img, mask=img.split()[3])
                else:
                    rgb_img.paste(img.convert('RGB'))
                img = rgb_img
                needs_resave = True

            if img.width > 1280 or img.height > 1280:
                img.thumbnail((1280, 1280), Image.LANCZOS)
                needs_resave = True

            if needs_resave:
                if is_jpeg:
                    img.save(file_path, format="JPEG", quality=88, optimize=True)
                else:
                    img.save(file_path, optimize=True)
        return True
    except Exception as e:
        print(f"⚠️ optimize_image_for_ram notice for {file_path}: {e}")
        # Only remove if the file is completely corrupt / 0-byte
        if os.path.exists(file_path) and os.path.getsize(file_path) < 1000:
            try:
                os.remove(file_path)
            except Exception:
                pass
        return False

def fetch_pexels_photo(query: str, save_path: str, orientation: str = "landscape") -> bool:
    """
    Downloads an HD photo directly from Pexels Photo API matching topic and orientation (landscape/portrait).
    Returns True if successfully downloaded and validated.
    """
    api_key = os.getenv("PEXELS_API_KEY") or PEXELS_API_KEY
    if not api_key:
        return False

    orient = "portrait" if "port" in str(orientation).lower() or orientation == "9:16" else "landscape"
    clean_term = clean_search_term(translate_query(query))
    queries_to_try = [clean_term]
    trans_q = translate_query(query)
    if trans_q != clean_term and trans_q not in queries_to_try:
        queries_to_try.append(trans_q)
    queries_to_try.append(f"{clean_term} cinematic")

    for q in queries_to_try:
        try:
            p_url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=8&orientation={orient}"
            p_res = requests.get(p_url, headers={"Authorization": api_key}, timeout=6)
            if p_res.status_code == 200:
                data = p_res.json()
                photos = data.get("photos", [])
                if photos:
                    candidates = photos[:5]
                    random.shuffle(candidates)
                    for photo in candidates:
                        src = photo.get("src", {})
                        img_url = src.get("large2x") or src.get(orient) or src.get("large") or src.get("original")
                        if not img_url:
                            continue
                        img_req = requests.get(img_url, timeout=7)
                        if img_req.status_code == 200 and len(img_req.content) > 15000:
                            with open(save_path, "wb") as f:
                                f.write(img_req.content)
                            if optimize_image_for_ram(save_path):
                                print(f"✅ [Pexels HD Photo API] Successfully downloaded HD ({orient}): {save_path} for '{q}'")
                                return True
            elif p_res.status_code == 401:
                print("⚠️ [Pexels API] Unauthorized (401), invalid API key.")
                break
        except Exception as e_pex:
            print(f"⚠️ Pexels photo search note for '{q}': {e_pex}")

    return False

def fetch_web_image(query: str, save_path: str, prefer_source: str = "auto", orientation: str = "landscape") -> bool:
    """
    Searches and downloads a high-resolution photo for any topic/character query.
    If prefer_source == "pexels", it uses Pexels directly and strictly bypasses Pinterest.
    """
    import shutil
    english_query = translate_query(query)
    clean_q_term = clean_search_term(english_query)
    print(f"🔎 [Web Image Search Engine] Searching HD Photos for: '{clean_q_term}' (Original Query: '{query}', Prefer: {prefer_source})...")

    # Priority 1 for Ultra Songs: Strict Pexels API (bypassing Pinterest completely)
    if prefer_source == "pexels":
        if fetch_pexels_photo(query, save_path, orientation=orientation):
            return True
        print("⚠️ [Pexels Direct] Could not find specific photo on Pexels, proceeding to direct image generators...")

    # For standard requests, try Pinterest first
    if prefer_source != "pexels":
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

        # If Pinterest didn't succeed, try Pexels Photo API
        if fetch_pexels_photo(query, save_path, orientation=orientation):
            return True

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
