import os
import sys
import math
import random
import re
import subprocess
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def release_system_memory():
    """Immediately triggers garbage collection to keep RAM < 50MB."""
    try:
        import gc
        gc.collect()
        try:
            import ctypes
            ctypes.CDLL('libc.so.6').malloc_trim(0)
        except Exception:
            pass
    except Exception:
        pass


# Regex patterns to detect reports, official statistics, years, court/police cases, surveys
_EVIDENCE_KEYWORDS = [
    r'\breport\b', r'\briport\b', r'\breports\b', r'\banusar\b', r'\bmutabik\b',
    r'\baccording to\b', r'\bstudy\b', r'\bsurvey\b', r'\bsurvekshan\b', r'\bresearch\b',
    r'\bofficial\b', r'\bsarkari\b', r'\bdata\b', r'\baankde\b', r'\brecord\b',
    r'\barchives?\b', r'\bfindings?\b', r'\bnews\b', r'\bkhabar\b', r'\bakhbar\b',
    r'\bnewspaper\b', r'\barticle\b', r'\bheadline\b', r'\bwikipedia\b', r'\bwikimidia\b',
    r'\bwikimedia\b', r'\bcourt\b', r'\bsupreme court\b', r'\bhigh court\b', r'\badalat\b',
    r'\bpolice\b', r'\bfir\b', r'\bchargesheet\b', r'\bcharge sheet\b', r'\bcbi\b',
    r'\bed\b', r'\bcid\b', r'\binvestigation\b', r'\bprobe\b', r'\bpostmortem\b',
    r'\barrest\b', r'\bgiraftaar\b', r'\bhiraasat\b', r'\bdetained\b', r'\bjudgement\b',
    r'\bsaboot\b', r'\bevidence\b', r'\bgawah\b', r'\bproof\b', r'\bdocument\b', r'\bdastavez\b'
]

_STAT_PATTERNS = [
    r'\b(19\d\d|20\d\d)\b', # Years like 2002, 1999, 2024
    r'\b\d+\s*(?:lakh|crore|million|billion|hazaar|thousand|percent|%)\b',
    r'\b(?:lakh|crore|million|hazaar)\b',
    r'\b(?:murder|marder|hatya|death|maut|ghotala|scam|kaand|accident|tragedy|incident)\b'
]


def detect_evidence_scene(scene_text: str, main_topic: str = "") -> Tuple[bool, Dict[str, Any]]:
    """
    Detects if a script line is presenting evidence, statistics, investigative reports,
    Wikipedia documentation, or official records.
    Returns (is_evidence, metadata_dict).
    """
    scene_lower = (scene_text or "").lower()
    topic_lower = (main_topic or "").lower()
    combined = f"{scene_lower} {topic_lower}"

    evidence_hits = [k for k in _EVIDENCE_KEYWORDS if re.search(k, scene_lower)]
    stat_hits = [p for p in _STAT_PATTERNS if re.search(p, scene_lower)]

    is_evidence = False
    # If report/news/official keyword is present OR year + stat/incident is present
    if len(evidence_hits) >= 1 or (re.search(r'\b(19\d\d|20\d\d)\b', scene_lower) and len(stat_hits) >= 2):
        is_evidence = True

    if not is_evidence:
        return False, {}

    # Extract detected year
    year_match = re.search(r'\b(19\d\d|20\d\d)\b', scene_lower)
    year_str = year_match.group(1) if year_match else "OFFICIAL ARCHIVE"

    # Determine whether Wikipedia or Newspaper style
    is_wikipedia = any(w in scene_lower for w in ["wikipedia", "wikimidia", "wikimedia", "encyclopedia"])

    # Extract key phrases that must be highlighted in yellow marker
    phrases_to_highlight = []
    
    # 1. Extract year report phrase e.g. "2002 ki report ke anusar" or "report of 2002"
    rep_m = re.search(r'(?:(?:19\d\d|20\d\d)\s*(?:ki\s+)?(?:report|riport)(?:\s+ke\s+anusar|\s+ke\s+mutabik)?|(?:according\s+to\s+)?(?:19\d\d|20\d\d)\s+report)', scene_lower)
    if rep_m:
        phrases_to_highlight.append(rep_m.group(0).strip())

    # 2. Extract number / stat phrases e.g. "4 lakh se bhi jyada murder", "400,000 cases"
    stat_pat = r'(\d+[\d,]*\s*(?:lakh|crore|million|billion|hazaar|thousand|%|percent)?(?:\s+se\s+bhi\s+j(?:i)?yada|\s+se\s+j(?:i)?yada)?\s*(?:murder|marder|hatya|death|cases|incidents|arrests|crimes)?)'
    for sm in re.finditer(stat_pat, scene_lower):
        m_str = sm.group(0).strip()
        # Avoid capturing only a bare year like '2002' if year is already captured
        if m_str and m_str != year_str and len(m_str) > 2:
            phrases_to_highlight.append(m_str)

    # 3. Extract legal / police / incident actions e.g. "further probe was on", "driver detained", "investigation initiated"
    action_m = re.search(r'(?:police\s+investigation|further\s+probe|driver\s+detained|postmortem|inquiry\s+commission|chargesheet\s+filed|court\s+orders?|arrested|hiraasat|critically\s+injured|collided)', scene_lower)
    if action_m:
        phrases_to_highlight.append(action_m.group(0).strip())

    # Fallback if list is short: capture key clauses
    if not phrases_to_highlight:
        words = scene_text.split()
        if len(words) >= 4:
            phrases_to_highlight.append(" ".join(words[:min(6, len(words))]))

    # Generate authoritative newspaper headline
    clean_topic = re.sub(r'[^\w\s]', '', main_topic).strip().upper() or "NATIONAL INVESTIGATION"
    if year_str != "OFFICIAL ARCHIVE":
        headline = f"OFFICIAL REPORT {year_str}: CRITICAL FINDINGS DOCUMENTED ACROSS REGIONAL RECORDS"
    else:
        headline = f"OFFICIAL INVESTIGATIVE REPORT: {clean_topic[:40]} EVIDENCE REVEALED"

    # Journalistic body text structured into realistic paragraphs
    paragraphs = _build_journalistic_paragraphs(scene_text, main_topic, year_str, phrases_to_highlight)

    # Check for news soundbite tag
    is_news_soundbite = any(k in scene_lower for k in ["news anchor", "breaking news", "news bulletin", "live broadcast", "soundbite", "press conference"])

    metadata = {
        "is_evidence": True,
        "is_wikipedia": is_wikipedia,
        "year": year_str,
        "headline": headline,
        "source": "WIKIPEDIA: THE FREE ENCYCLOPEDIA" if is_wikipedia else "THE DAILY INVESTIGATIVE CHRONICLE",
        "date_str": f"OFFICIAL RECORD ARCHIVE • {year_str} SPECIAL REPORT • EDITION NO. 48",
        "paragraphs": paragraphs,
        "phrases_to_highlight": phrases_to_highlight,
        "is_news_soundbite": is_news_soundbite
    }

    return True, metadata


def _build_journalistic_paragraphs(scene_text: str, topic: str, year: str, highlights: List[str]) -> List[str]:
    """
    Constructs authentic newspaper article paragraphs featuring the reported facts.
    """
    clean_text = scene_text.strip()
    # Paragraph 1: Lead paragraph with location, source, and exact findings
    p1 = f"NEW DELHI — According to the comprehensive official investigation report released for {year}, records verified that {clean_text}. The documentation was verified across state investigative registries."
    # Paragraph 2: Specific statistics and impact
    p2 = f"Official archives and police bulletins corroborated the statistics, indicating critical systemic developments that prompted parliamentary commissions to review institutional oversight."
    # Paragraph 3: Investigation and proceedings
    p3 = f"Senior investigative officers confirmed that detailed evidentiary affidavits and case documents were submitted to the competent authority, and further inquiry was placed on official record."
    return [p1, p2, p3]


def fetch_wikipedia_evidence_snippet(query: str, topic: str = "") -> Optional[Dict[str, str]]:
    """
    Attempts to fetch lead extract from Wikipedia API.
    Gracefully handles offline/sandbox environments with zero exceptions.
    """
    try:
        import urllib.request
        import urllib.parse
        import json
        import ssl

        search_q = f"{query} {topic}".strip()
        encoded_q = urllib.parse.quote(search_q[:80])
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_q}&format=json&utf8=1"
        
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(
            api_url,
            headers={"User-Agent": "CloxelDocumentaryEvidenceEngine/2.0 (cloxelai@gmail.com)"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            search_items = data.get("query", {}).get("search", [])
            if search_items:
                top_item = search_items[0]
                clean_snippet = re.sub(r'<[^>]+>', '', top_item.get("snippet", "")).strip()
                return {
                    "title": top_item.get("title", "Historical Document"),
                    "snippet": clean_snippet
                }
    except Exception:
        pass
    return None


def generate_newspaper_evidence_image(
    meta: Dict[str, Any],
    output_path: str,
    target_size: Tuple[int, int] = (1920, 1080)
) -> str:
    """
    Generates a high-resolution, photorealistic Newspaper Article / Wikipedia Document Clipping:
    - Aged newsprint paper background with paper grain texture.
    - Authentic masthead / header, edition info, and double rule divider lines.
    - Classic Serif headline.
    - Multi-column article layout with vertical dotted column rule (matching user's uploaded image).
    - Authentic FLUORESCENT YELLOW MARKER HIGHLIGHTING over the target evidence phrases.
    - Crisp black ink text printed over the marker for 100% clarity.
    """
    width, height = target_size
    is_portrait = height > width
    is_wikipedia = meta.get("is_wikipedia", False)

    # Base paper color
    if is_wikipedia:
        bg_color = (250, 250, 250)
    else:
        # Authentic newsprint cream/off-white (244, 241, 233)
        bg_color = (244, 241, 233)

    img = Image.new("RGBA", (width, height), (*bg_color, 255))
    
    # 1. Subtle Paper Grain / Micro-texture
    noise = np.random.randint(-5, 6, (height, width, 3), dtype=np.int16)
    rgb_arr = np.clip(np.array(img.convert("RGB"), dtype=np.int16) + noise, 0, 255).astype(np.uint8)
    base_img = Image.fromarray(rgb_arr).convert("RGBA")
    del rgb_arr, noise

    # 2. Font Loading
    serif_bold_path = "./fonts/RozhaOne-Regular.ttf"
    serif_body_path = "./fonts/TiroDevanagariHindi-Regular.ttf"
    sans_path = "./fonts/Arial.ttf"
    if not os.path.exists(sans_path):
        sans_path = "./fonts/NotoSansDevanagari-Bold.ttf"

    scale_factor = 1.0 if not is_portrait else 0.85
    f_mast_size = int(42 * scale_factor)
    f_sub_size = int(16 * scale_factor)
    f_head_size = int(48 * scale_factor)
    f_body_size = int(28 * scale_factor)
    f_side_size = int(20 * scale_factor)

    try: font_masthead = ImageFont.truetype(serif_bold_path, f_mast_size)
    except Exception: font_masthead = ImageFont.load_default()

    try: font_sub = ImageFont.truetype(sans_path, f_sub_size)
    except Exception: font_sub = ImageFont.load_default()

    try: font_headline = ImageFont.truetype(serif_bold_path, f_head_size)
    except Exception: font_headline = ImageFont.load_default()

    try: font_body = ImageFont.truetype(serif_body_path, f_body_size)
    except Exception: font_body = ImageFont.load_default()

    try: font_side = ImageFont.truetype(serif_body_path, f_side_size)
    except Exception: font_side = ImageFont.load_default()

    draw_base = ImageDraw.Draw(base_img)

    margin_x = int(60 * scale_factor)
    content_w = width - (margin_x * 2)

    # 3. Masthead / Header
    mast_text = meta.get("source", "THE DAILY INVESTIGATIVE CHRONICLE")
    meta_sub = meta.get("date_str", "OFFICIAL RECORD ARCHIVE • SPECIAL REPORT")
    
    y_mast = int(50 * scale_factor)
    draw_base.text((width // 2, y_mast), mast_text, fill=(28, 28, 28, 255), font=font_masthead, anchor="mm")
    
    y_sub = y_mast + int(38 * scale_factor)
    draw_base.text((width // 2, y_sub), meta_sub, fill=(75, 75, 75, 255), font=font_sub, anchor="mm")
    
    # Header double lines
    y_line1 = y_sub + int(20 * scale_factor)
    draw_base.line([(margin_x, y_line1), (width - margin_x, y_line1)], fill=(40, 40, 40, 255), width=3)
    draw_base.line([(margin_x, y_line1 + 6), (width - margin_x, y_line1 + 6)], fill=(50, 50, 50, 255), width=1)

    # 4. Bold Headline
    y_head = y_line1 + int(22 * scale_factor)
    hl_text = meta.get("headline", "OFFICIAL REPORT DOCUMENTATION")
    
    # Word wrap headline
    hl_words = hl_text.split()
    hl_lines = []
    cur_hl = []
    for hw in hl_words:
        test_h = " ".join(cur_hl + [hw])
        bb = font_headline.getbbox(test_h)
        if (bb[2] - bb[0]) > content_w and cur_hl:
            hl_lines.append(" ".join(cur_hl))
            cur_hl = [hw]
        else:
            cur_hl.append(hw)
    if cur_hl:
        hl_lines.append(" ".join(cur_hl))

    for hl_l in hl_lines[:2]:
        draw_base.text((margin_x, y_head), hl_l, fill=(18, 18, 18, 255), font=font_headline)
        y_head += int(56 * scale_factor)

    # Divider below headline
    draw_base.line([(margin_x, y_head + 6), (width - margin_x, y_head + 6)], fill=(120, 120, 120, 255), width=1)

    # 5. Columns Layout
    y_cols = y_head + int(22 * scale_factor)
    if not is_portrait:
        col1_w = int(content_w * 0.64)
        col1_x = margin_x
        col2_x = col1_x + col1_w + int(45 * scale_factor)
        col2_w = width - margin_x - col2_x
        
        # Vertical dotted rule separating columns (exact feature from user's newspaper photo)
        dot_x = col1_x + col1_w + int(22 * scale_factor)
        for y_dot in range(y_cols, height - int(50 * scale_factor), 8):
            draw_base.line([(dot_x, y_dot), (dot_x, y_dot + 3)], fill=(135, 135, 135, 255), width=2)
            
        # Draw side column adjacent articles
        side_items = [
            ("PARLIAMENTARY INQUIRY COMMITTEE", "Special session convened to review historical case statistics and administrative records across state law enforcement departments."),
            ("SUPREME COURT BENCH DIRECTIVE", "Judicial bench issues stringent guidelines on record preservation and evidentiary standard verification."),
            ("SPECIAL INVESTIGATION BUREAU", "Independent investigative agencies corroborate statistical figures and submit verified archives.")
        ]
        y_s = y_cols
        for stitle, sbody in side_items:
            draw_base.text((col2_x, y_s), stitle, fill=(22, 22, 22, 255), font=font_side)
            y_s += int(26 * scale_factor)
            # wrap body words
            sw_words = sbody.split()
            c_sl = []
            for sww in sw_words:
                test_sl = " ".join(c_sl + [sww])
                if (font_side.getbbox(test_sl)[2] - font_side.getbbox(test_sl)[0]) > col2_w and c_sl:
                    draw_base.text((col2_x, y_s), " ".join(c_sl), fill=(80, 80, 80, 255), font=font_side)
                    y_s += int(22 * scale_factor)
                    c_sl = [sww]
                else:
                    c_sl.append(sww)
            if c_sl:
                draw_base.text((col2_x, y_s), " ".join(c_sl), fill=(80, 80, 80, 255), font=font_side)
                y_s += int(22 * scale_factor)
            y_s += int(16 * scale_factor)
            draw_base.line([(col2_x, y_s), (width - margin_x, y_s)], fill=(185, 185, 185, 255), width=1)
            y_s += int(18 * scale_factor)
    else:
        # Mobile 9:16 portrait: Single prominent focus column
        col1_w = content_w
        col1_x = margin_x

    # 6. Flow Article Paragraphs & Compute Yellow Marker Highlights
    paragraphs = meta.get("paragraphs", [])
    raw_highlights = meta.get("phrases_to_highlight", [])
    # Flatten highlights into search phrases and tokens
    search_highlights = []
    for rh in raw_highlights:
        rh_clean = rh.strip().lower()
        if rh_clean:
            search_highlights.append(rh_clean)
            for part in rh_clean.split():
                if len(part) >= 4 and part not in ["this", "that", "with", "from", "were", "been", "have"]:
                    search_highlights.append(part)

    # Line formatting
    line_h = int(42 * scale_factor)
    y_cur = y_cols
    all_lines = [] # (line_text, y_pos)

    for p in paragraphs:
        words = p.split()
        cur_line = []
        for w in words:
            test_l = " ".join(cur_line + [w])
            bb = font_body.getbbox(test_l)
            if (bb[2] - bb[0]) > col1_w and cur_line:
                all_lines.append((" ".join(cur_line), y_cur))
                cur_line = [w]
                y_cur += line_h
            else:
                cur_line.append(w)
        if cur_line:
            all_lines.append((" ".join(cur_line), y_cur))
            y_cur += line_h + int(14 * scale_factor)

    # 7. Layers for Marker and Text
    highlight_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    hl_draw = ImageDraw.Draw(highlight_layer)

    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(text_layer)

    # Fluorescent Yellow Marker Color (Stabilo Boss neon yellow: 255, 240, 20 with 195 alpha)
    hl_color = (255, 238, 20, 195)
    space_w = font_body.getbbox(" ")[2] - font_body.getbbox(" ")[0]

    for line_text, y in all_lines:
        line_lower = line_text.lower()
        # Find matched spans for highlights
        matched_spans = []
        for sh in search_highlights:
            pos = line_lower.find(sh)
            while pos != -1:
                matched_spans.append((pos, pos + len(sh)))
                pos = line_lower.find(sh, pos + len(sh))

        words = line_text.split()
        x_offset = col1_x
        char_idx = 0

        for w in words:
            w_bbox = font_body.getbbox(w)
            w_w = w_bbox[2] - w_bbox[0]
            w_start = char_idx
            w_end = char_idx + len(w)

            # Check if this word overlaps with any highlight span
            is_hl = any(not (w_end <= s or w_start >= e) for s, e in matched_spans)

            if is_hl:
                pad_x = int(4 * scale_factor)
                pad_y = int(3 * scale_factor)
                box_y1 = y - pad_y
                box_y2 = y + line_h - int(10 * scale_factor) + pad_y
                hl_draw.rounded_rectangle(
                    [(x_offset - pad_x, box_y1), (x_offset + w_w + pad_x, box_y2)],
                    radius=int(4 * scale_factor),
                    fill=hl_color
                )

            # Draw black text
            txt_draw.text((x_offset, y), w, fill=(22, 22, 22, 255), font=font_body)

            x_offset += w_w + space_w
            char_idx += len(w) + 1

    # 8. Composite: Base Newsprint -> Yellow Highlighter -> Black Text
    final_img = Image.alpha_composite(base_img, highlight_layer)
    final_img = Image.alpha_composite(final_img, text_layer).convert("RGB")
    final_img.save(output_path, quality=92)
    
    del base_img, highlight_layer, text_layer, final_img
    release_system_memory()
    return output_path


def generate_documentary_evidence_clip(
    image_path: str,
    output_mp4: str,
    duration: float,
    target_size: Tuple[int, int] = (1920, 1080),
    fps: int = 20
) -> str:
    """
    Renders a smooth Ken Burns documentary camera zoom right into the highlighted evidence text
    using native C FFmpeg (takes < 20MB RAM and completes in ~1 second).
    """
    w, h = target_size
    duration = max(3.0, float(duration))
    total_frames = int(duration * fps)

    # Smooth zoom into column 1 highlighted text area (approx x=25% width, y=30% height)
    # Uses zoompan with smooth ease
    vf_filter = (
        f"zoompan=z='min(zoom+0.0010,1.14)':"
        f"x='iw*0.22*(1-1/zoom)':"
        f"y='ih*0.28*(1-1/zoom)':"
        f"d={total_frames}:s={w}x{h}:fps={fps}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", os.path.abspath(image_path),
        "-vf", vf_filter,
        "-t", f"{duration:.2f}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-threads", "1",
        os.path.abspath(output_mp4)
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    except Exception as e:
        print(f"⚠️ Notice: Ken Burns zoompan fallback ({e}), creating static loop...")
        fb_cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", os.path.abspath(image_path),
            "-t", f"{duration:.2f}",
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-threads", "1",
            os.path.abspath(output_mp4)
        ]
        subprocess.run(fb_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    release_system_memory()
    return output_mp4
