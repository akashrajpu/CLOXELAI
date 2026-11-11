"""
GLSL Shader-Driven Scene Transition Engine for Ultra, Long, and Short Videos.

Reads and parses gl-transitions `.glsl` shader files directly from `glsl_shaders/`
and executes their transition math in vectorized NumPy, keeping 100% A/V sync and low
memory footprint compatible with headless Linux/macOS FFmpeg pipelines.

Strict Mode Rules:
  - Ultra (`mode == "ultra"`): Uses ONLY `.glsl` shaders whose names match glitch
    (`glich*`) or light/color (`light*` / `color*`), pairing ONLY glitch transitions
    with Mixkit glitch SFX (from `sound_effects/`).
  - Long & Short (`mode in ("long", "short")`): Randomly selects across ALL `.glsl`
    transition shaders in `glsl_shaders/` without adding glitch SFX.
  - Script-Triggered Only: Never applies transitions blindly on every cut; triggers
    only when script pause/tense/narrative-shift cues warrant a transition, with
    anti-consecutive spacing.
"""

import math
import os
import random
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_GLSL_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_GLSL_SHADERS_DIR = os.path.join(_GLSL_BASE_DIR, "glsl_shaders")
_GLSL_SPLIT_RE = re.compile(r'[\s,.\-!?;:"\'()\[\]{}<>/\\|~`@#$%^&*_+=।॥]+')

# Exact `.glsl` transition files in `glsl_shaders/`
GLSL_TRANSITION_FILES = {
    "glitch": [
        "glich2_tranjection.glsl",
        "glich_trajection_effect.glsl",
        "glich_tranjectiion.glsl",
    ],
    "light_color": [
        "light_coloring_effect.glsl",
        "color_tranjection.glsl",
    ],
    "other": [
        "click_photo_type_tranjection.glsl",
        "filter_tranjection.glsl",
        "smoke_transition.glsl",
        "water_type_tranjection.glsl",
    ],
}

GLITCH_TRANSITION_SFX = [
    "mixkit-cinematic-glitch-trailer-1021.wav",
    "mixkit-glitch-static-1457.wav",
    "mixkit-small-electric-glitch-2595.wav",
]

# Multi-word & single-word pause / tense / transition triggers (Devanagari, Hinglish, English)
_SCRIPT_PAUSE_PHRASES = (
    # User-specified Hindi / Hinglish tense & state-change markers + variants
    ("ho raha tha", 4.0), ("ho rha tha", 4.0), ("ho rahi thi", 4.0), ("ho rhi thi", 4.0),
    ("ho rahe the", 4.0), ("ho rhe the", 4.0),
    ("ho sakta hai", 4.0), ("ho skta hai", 4.0), ("ho skta he", 4.0), ("ho sakta he", 4.0),
    ("ho sakti hai", 4.0), ("ho sakte hain", 4.0), ("ho skta h", 4.0),
    ("ho chuka tha", 4.2), ("ho chuki thi", 4.2), ("ho chuke the", 4.2),
    ("ho chuka hai", 4.0), ("ho chuka he", 4.0), ("ho chuka", 3.5),
    ("hone wala hai", 4.2), ("hone wala he", 4.2), ("hone wala tha", 4.2),
    ("hone wali hai", 4.2), ("hone wali thi", 4.2), ("hone wale hain", 4.2), ("hone wale hai", 4.2),
    ("rahe honge", 4.0), ("rhe honge", 4.0),
    ("raha hoga", 4.0), ("rha hoga", 4.0), ("rahi hogi", 4.0), ("rhi hogi", 4.0),
    ("ho raha hai", 4.0), ("ho rha hai", 4.0), ("ho rha he", 4.0), ("ho raha he", 4.0),
    ("ho rahi hai", 4.0), ("ho rahe hain", 4.0), ("ho rhe hai", 4.0),
    ("raha tha", 3.2), ("rha tha", 3.2), ("rahi thi", 3.2), ("rhi thi", 3.2),
    ("rahe the", 3.2), ("rhe the", 3.2),
    ("kar raha tha", 3.2), ("kar rha tha", 3.2), ("kar rahe the", 3.2),
    ("ho gaya", 2.8), ("ho gya", 2.8), ("hone laga", 3.0),
    ("uske baad", 3.2), ("iske baad", 3.0), ("agle pal", 3.5),
    ("dusri taraf", 3.2), ("doosri taraf", 3.2), ("jaise hi", 3.0),
    ("kya hua", 3.2), ("toh kya", 2.8), ("to kya", 2.8),
    # Hindi Devanagari exact phrases
    ("हो रहा था", 4.0), ("हो रही थी", 4.0), ("हो रहे थे", 4.0),
    ("हो सकता है", 4.0), ("हो सकती है", 4.0), ("हो सकते हैं", 4.0),
    ("हो चुका था", 4.2), ("हो चुकी थी", 4.2), ("हो चुके थे", 4.2), ("हो चुका है", 4.0),
    ("होने वाला है", 4.2), ("होने वाली है", 4.2), ("होने वाले हैं", 4.2),
    ("होने वाला था", 4.2), ("होने वाली थी", 4.2),
    ("रहे होंगे", 4.0), ("रहा होगा", 4.0), ("रही होगी", 4.0),
    ("हो रहा है", 4.0), ("हो रही है", 4.0), ("हो रहे हैं", 4.0),
    ("रहा था", 3.2), ("रही थी", 3.2), ("रहे थे", 3.2),
    ("कर रहा था", 3.2), ("कर रहे थे", 3.2),
    ("हो गया", 2.8), ("होने लगा", 3.0), ("जा रहा है", 3.0), ("आ रहा है", 3.0),
    ("उसके बाद", 3.2), ("इसके बाद", 3.0), ("अगले पल", 3.5),
    ("दूसरी तरफ", 3.2), ("जैसे ही", 3.0), ("क्या हुआ", 3.2),
    ("गया था", 3.0), ("गई थी", 3.0), ("गए थे", 3.0), ("बन गया", 2.8), ("बदल गया", 3.0),
    # English transition / tense / pause cues
    ("was happening", 3.8), ("were happening", 3.8),
    ("could be", 3.2), ("would be", 3.2), ("will be", 3.2), ("might be", 3.2),
    ("had already", 3.8), ("has already", 3.6), ("had been", 3.4), ("has been", 3.2),
    ("about to", 3.8), ("was going to", 3.8), ("going to happen", 4.0),
    ("after that", 3.2), ("on the other hand", 3.5), ("what happened next", 4.0),
    ("moment later", 3.5), ("moments later", 3.5), ("years later", 3.5),
    ("but then", 3.2), ("turns out", 3.4), ("all of a sudden", 3.6),
)

_SCRIPT_PAUSE_SINGLE_TOKENS = {
    # Hinglish & Hindi tokens
    "hoga": 3.5, "hogi": 3.5, "honge": 3.5, "chuka": 3.0,
    "lekin": 2.8, "magar": 2.8, "tabhi": 3.2, "achanak": 3.4,
    "phir": 2.5, "fir": 2.5, "halanki": 2.8, "jabki": 2.8, "darasal": 2.6,
    "khatam": 2.8, "sochiye": 3.0, "aakhirkar": 3.0,
    "होगा": 3.5, "होगी": 3.5, "होंगे": 3.5, "चुका": 3.0, "चुकी": 3.0, "चुके": 3.0,
    "लेकिन": 2.8, "मगर": 2.8, "तभी": 3.2, "अचानक": 3.4,
    "फिर": 2.5, "हालांकि": 2.8, "जबकि": 2.8, "दरअसल": 2.6,
    "परंतु": 2.8, "किन्तु": 2.8, "आखिरकार": 3.0, "सोचिए": 3.0, "बल्कि": 2.6,
    # English tokens
    "however": 3.0, "meanwhile": 3.2, "suddenly": 3.4, "eventually": 3.0,
    "finally": 2.8, "until": 2.6, "instead": 2.6, "later": 2.6, "imagine": 2.8,
}


def resolve_glsl_path(filename: str) -> Optional[str]:
    """Resolve a `.glsl` shader file path from `glsl_shaders/` (with repo-root fallback)."""
    if not filename:
        return None
    base = os.path.basename(filename)
    for candidate in (
        os.path.join(_GLSL_SHADERS_DIR, base),
        os.path.abspath(os.path.join("glsl_shaders", base)),
        os.path.join(_GLSL_BASE_DIR, filename),
        os.path.abspath(filename),
    ):
        if os.path.exists(candidate) and os.path.getsize(candidate) > 20:
            return candidate
    return None


def resolve_glitch_sfx_path(filename: str) -> Optional[str]:
    """Resolve a glitch SFX file from `sound_effects/` or repo root."""
    if not filename:
        return None
    for candidate in (
        os.path.join(_GLSL_BASE_DIR, "sound_effects", filename),
        os.path.abspath(os.path.join("sound_effects", filename)),
        os.path.join(_GLSL_BASE_DIR, filename),
        os.path.abspath(filename),
    ):
        if os.path.exists(candidate) and os.path.getsize(candidate) > 500:
            return candidate
    return None


def get_glsl_category(filename: str) -> str:
    """Classify a `.glsl` filename strictly by naming rule (`glitch`, `light_color`, `other`)."""
    low = os.path.basename(filename).lower()
    if "glich" in low or "glitch" in low:
        return "glitch"
    if "light" in low or "color" in low:
        return "light_color"
    return "other"


def get_allowed_glsl_pool(mode: str) -> List[Tuple[str, str]]:
    """
    Return available `(filename, category)` tuples allowed for `mode`:
      - `ultra`: STRICTLY ONLY `glitch` (`glich*`) and `light_color` (`light*`/`color*`) `.glsl` files.
      - `long` / `short` (or others): ALL 9 `.glsl` files in the repo.
    """
    is_ultra = str(mode or "").strip().lower() == "ultra"
    allowed_cats = ("glitch", "light_color") if is_ultra else ("glitch", "light_color", "other")
    pool: List[Tuple[str, str]] = []
    for cat in allowed_cats:
        for fname in GLSL_TRANSITION_FILES[cat]:
            if resolve_glsl_path(fname):
                pool.append((fname, cat))
    return pool


def parse_glsl_shader_meta(filename: str) -> Dict[str, Any]:
    """
    Read the `.glsl` shader file from disk, validate `transition(...)` entry point,
    and parse `uniform <type> <name>; // = <default>` parameter values.
    """
    path = resolve_glsl_path(filename)
    if not path:
        return {}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            src = f.read()
    except Exception:
        return {}

    uniforms: Dict[str, Any] = {}
    uniform_re = re.compile(
        r'uniform\s+(float|int|vec2|vec4)\s+(\w+)\s*;\s*//\s*=\s*([^\r\n]+)'
    )
    for utype, uname, raw_val in uniform_re.findall(src):
        val_str = raw_val.strip()
        try:
            if utype == "float":
                uniforms[uname] = float(val_str.split()[0])
            elif utype == "int":
                uniforms[uname] = int(float(val_str.split()[0]))
            elif utype in ("vec2", "vec4"):
                nums = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', val_str)]
                if utype == "vec2" and len(nums) >= 2:
                    uniforms[uname] = (nums[0], nums[1])
                elif utype == "vec4" and len(nums) >= 4:
                    uniforms[uname] = tuple(nums[:4])
        except Exception:
            pass

    return {
        "file": os.path.basename(filename),
        "path": path,
        "category": get_glsl_category(filename),
        "has_transition_fn": "transition" in src,
        "uniforms": uniforms,
    }


def score_script_transition_boundary(outgoing_text: str, incoming_text: str = "") -> Tuple[float, str]:
    """
    Evaluate whether the script boundary between `outgoing_text` and `incoming_text`
    represents a pause, tense completion, or narrative shift needing a transition.
    Returns `(score, matched_reason)`.
    """
    out_raw = str(outgoing_text or "").strip()
    in_raw = str(incoming_text or "").strip()
    if not out_raw and not in_raw:
        return 0.0, ""

    out_low = out_raw.lower()
    in_low = in_raw.lower()

    out_tokens = [t for t in _GLSL_SPLIT_RE.split(out_low) if t]
    in_tokens = [t for t in _GLSL_SPLIT_RE.split(in_low) if t]
    joined_out = f" {' '.join(out_tokens)} " if out_tokens else ""
    joined_in = f" {' '.join(in_tokens)} " if in_tokens else ""

    score = 0.0
    best_reason = ""
    best_w = 0.0

    # Phrase checks (outgoing text carries higher natural pause weight at scene cut)
    for phrase, w in _SCRIPT_PAUSE_PHRASES:
        needle = f" {phrase} "
        if needle in joined_out:
            # Extra bonus if phrase sits near the end of outgoing line
            pos = joined_out.rfind(needle)
            tail_bonus = 1.25 if pos >= len(joined_out) * 0.45 else 1.0
            eff_w = w * tail_bonus
            score += eff_w
            if eff_w > best_w:
                best_w = eff_w
                best_reason = phrase
        elif needle in joined_in:
            # Opening shift phrase on incoming line (first half of sentence)
            pos = joined_in.find(needle)
            head_bonus = 1.15 if pos <= len(joined_in) * 0.50 else 0.75
            eff_w = w * head_bonus
            score += eff_w
            if eff_w > best_w:
                best_w = eff_w
                best_reason = phrase

    # Single token cues
    for tok in set(out_tokens + in_tokens[:5]):
        if tok in _SCRIPT_PAUSE_SINGLE_TOKENS:
            w = _SCRIPT_PAUSE_SINGLE_TOKENS[tok]
            score += w
            if w > best_w:
                best_w = w
                best_reason = tok

    # Dramatic pause punctuation at end of outgoing line (`...`, `—`, `?`)
    if "..." in out_raw or "…" in out_raw or "—" in out_raw or out_raw.endswith("?"):
        p_w = 2.6
        score += p_w
        if p_w > best_w:
            best_reason = "script_pause"

    return round(score, 2), best_reason


def plan_glsl_transitions(
    scene_texts: List[str],
    scene_durations: List[float],
    mode: str = "ultra",
    rng_seed: Optional[int] = None,
) -> Dict[int, Dict[str, Any]]:
    """
    Select sparse, script-driven GLSL transitions for boundaries `i -> i+1`.
    Returns a dict mapping boundary index `i` to transition plan info.
    """
    n = len(scene_durations)
    if n < 2:
        return {}

    pool = get_allowed_glsl_pool(mode)
    if not pool:
        return {}

    rng = random.Random(rng_seed) if rng_seed is not None else random.Random()

    scored_candidates: List[Tuple[int, float, str]] = []
    for i in range(n - 1):
        # Skip overly short clips to avoid trimming below safe narration duration
        if scene_durations[i] < 1.8 or scene_durations[i + 1] < 1.8:
            continue
        out_txt = scene_texts[i] if i < len(scene_texts) else ""
        in_txt = scene_texts[i + 1] if (i + 1) < len(scene_texts) else ""
        sc, reason = score_script_transition_boundary(out_txt, in_txt)
        if sc >= 2.5:
            scored_candidates.append((i, sc, reason))

    if not scored_candidates:
        return {}

    # Cap total transitions so they stay sparse & attractive ("hr bar nhi lgana")
    num_cuts = n - 1
    max_transitions = max(1, math.ceil(num_cuts * 0.42))

    # Shuffle with score weight so selection stays random across qualifying scenes
    weighted_order = sorted(
        scored_candidates,
        key=lambda item: item[1] * rng.uniform(0.65, 1.35),
        reverse=True,
    )

    chosen_indices: List[int] = []
    for idx, _, _ in weighted_order:
        if len(chosen_indices) >= max_transitions:
            break
        # Strictly forbid consecutive transitions (minimum gap of 2 cuts)
        if any(abs(idx - existing) < 2 for existing in chosen_indices):
            continue
        chosen_indices.append(idx)

    chosen_indices.sort()
    reason_map = {idx: reason for idx, _, reason in scored_candidates}

    plans: Dict[int, Dict[str, Any]] = {}
    last_shader = None
    is_ultra = str(mode or "").strip().lower() == "ultra"

    for b_idx in chosen_indices:
        choices = [p for p in pool if p[0] != last_shader] or pool
        fname, cat = rng.choice(choices)
        last_shader = fname
        meta = parse_glsl_shader_meta(fname)
        if not meta or not meta.get("has_transition_fn"):
            continue

        # Pair glitch SFX ONLY for Ultra + glitch shaders ("unke sath glich wala saund waki ke ko mt krna")
        sfx_path = None
        if is_ultra and cat == "glitch":
            avail_sfx = [resolve_glitch_sfx_path(s) for s in GLITCH_TRANSITION_SFX]
            avail_sfx = [s for s in avail_sfx if s]
            if avail_sfx:
                sfx_path = rng.choice(avail_sfx)

        plans[b_idx] = {
            "boundary_idx": b_idx,
            "file": fname,
            "category": cat,
            "meta": meta,
            "reason": reason_map.get(b_idx, "script_cue"),
            "sfx_path": sfx_path,
            "duration": 0.64,
        }

    return plans


# =============================================================================
# Vectorized NumPy Shader Math Helpers & 9 GLSL Transition Renderers
# =============================================================================

def _clamp01(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


def _smoothstep(edge0: float, edge1: float, x: np.ndarray) -> np.ndarray:
    if edge1 == edge0:
        return (x >= edge0).astype(np.float32)
    t = _clamp01((x - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def _sample_uv_bilinear(img_f32: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Bilinearly sample `(H, W, 3)` float32 image at OpenGL UVs `(u, v)` (`v=0` bottom, `v=1` top)."""
    h, w, _ = img_f32.shape
    x = np.clip(u, 0.0, 1.0) * (w - 1)
    y = np.clip(1.0 - v, 0.0, 1.0) * (h - 1)

    x0 = np.floor(x).astype(np.int32)
    y0 = np.floor(y).astype(np.int32)
    x1 = np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)

    fx = (x - x0)[..., None].astype(np.float32)
    fy = (y - y0)[..., None].astype(np.float32)

    top = img_f32[y0, x0] * (1.0 - fx) + img_f32[y0, x1] * fx
    bot = img_f32[y1, x0] * (1.0 - fx) + img_f32[y1, x1] * fx
    return top * (1.0 - fy) + bot * fy


def _make_uv_grids(h: int, w: int) -> Tuple[np.ndarray, np.ndarray]:
    u = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]
    v = np.linspace(1.0, 0.0, h, dtype=np.float32)[:, None]
    return np.broadcast_to(u, (h, w)), np.broadcast_to(v, (h, w))


def _hash12(px: np.ndarray, py: np.ndarray) -> np.ndarray:
    p3x = np.mod(px * 0.1031, 1.0)
    p3y = np.mod(py * 0.1031, 1.0)
    p3z = p3x.copy()
    d = p3x * (p3y + 33.33) + p3y * (p3z + 33.33) + p3z * (p3x + 33.33)
    return np.mod((p3x + p3y) * (p3z + d), 1.0)


def _hash12_alt(px: np.ndarray, py: np.ndarray) -> np.ndarray:
    p_x = np.mod(px * 443.8975, 1.0)
    p_y = np.mod(py * 397.2973, 1.0)
    d = p_x * (p_y + 19.19) + p_y * (p_x + 19.19)
    return np.mod((p_x + d) * (p_y + d), 1.0)


def _vnoise(vx: np.ndarray, vy: np.ndarray) -> np.ndarray:
    ix = np.floor(vx)
    iy = np.floor(vy)
    fx = vx - ix
    fy = vy - iy
    fx = fx * fx * (3.0 - 2.0 * fx)
    fy = fy * fy * (3.0 - 2.0 * fy)
    a = _hash12(ix, iy)
    b = _hash12(ix + 1.0, iy)
    c = _hash12(ix, iy + 1.0)
    d = _hash12(ix + 1.0, iy + 1.0)
    return (a * (1.0 - fx) + b * fx) * (1.0 - fy) + (c * (1.0 - fx) + d * fx) * fy


def _fbm(vx: np.ndarray, vy: np.ndarray) -> np.ndarray:
    total = np.zeros_like(vx, dtype=np.float32)
    amp = 0.5
    x, y = vx.copy(), vy.copy()
    for _ in range(4):
        total += amp * _vnoise(x, y)
        nx = 1.6 * x - 1.2 * y + 5.3
        ny = 1.2 * x + 1.6 * y + 5.3
        x, y = nx, ny
        amp *= 0.5
    return total / 0.9375


def _render_glich2(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    if p <= 0.0:
        return img_from
    if p >= 1.0:
        return img_to

    frame_rate = float(uniforms.get("frameRate", 24.0))
    rgb_offset = float(uniforms.get("rgbOffset", 0.014))
    block_amt = float(uniforms.get("blockAmount", 0.72))
    ghost_amt = float(uniforms.get("ghostAmount", 0.62))
    red_cyan = float(uniforms.get("redCyan", 0.58))
    scanline = float(uniforms.get("scanline", 0.075))

    f = math.floor(p * frame_rate)
    reveal_tbl = [0.00, 0.28, 0.43, 0.46, 0.38, 0.48, 0.26, 0.10, 0.00, 0.00, 0.30, 0.58,
                  1.00, 0.70, 0.42, 0.55, 0.72, 0.88, 0.34, 0.48, 0.56, 0.76, 0.93, 1.00]
    fi = int(min(max(0, round(f)), len(reveal_tbl) - 1))
    reveal = reveal_tbl[fi]

    if f < 0.5: glitch = 0.00
    elif f < 6.5: glitch = 0.92
    elif f < 10.5: glitch = 0.38
    elif f < 11.5: glitch = 0.78
    elif f < 12.5: glitch = 0.12
    elif f < 17.5: glitch = 0.74
    elif f < 22.5: glitch = 0.88
    elif f < 23.5: glitch = 0.28
    else: glitch = 0.00

    def _s_hash(x: float, y: float) -> float:
        px = math.fmod(x * 443.8975, 1.0)
        py = math.fmod(y * 397.2973, 1.0)
        if px < 0: px += 1.0
        if py < 0: py += 1.0
        d = px * (py + 19.19) + py * (px + 19.19)
        r = math.fmod((px + d) * (py + d), 1.0)
        return r + 1.0 if r < 0 else r

    jitter_x = (_s_hash(f, 9.13) - 0.5) * 0.042 * glitch
    jitter_y = (_s_hash(f, 2.71) - 0.5) * 0.010 * glitch
    from_u = np.clip(u + jitter_x, 0.001, 0.999)
    from_v = np.clip(v + jitter_y, 0.001, 0.999)
    to_u = np.clip(u - jitter_x * 0.55, 0.001, 0.999)
    to_v = np.clip(v - jitter_y * 0.55, 0.001, 0.999)

    big_x = np.floor(u * 4.0)
    small_x = np.floor(u * 8.0)
    small_y = np.floor(v * 4.0)
    wide = (_hash12_alt(big_x, np.full_like(big_x, f * 1.37)) >= 0.48).astype(np.float32)
    chunks = (_hash12_alt(small_x + f * 2.11, small_y + f * 0.73) >= 0.56).astype(np.float32)
    vcut = _smoothstep(-0.035, 0.035, u - (0.18 + 0.60 * _s_hash(f, 4.7)))
    block = _clamp01((wide * 0.62 + chunks * 0.38) * 0.72 + vcut * 0.28)

    row_noise = _hash12_alt(np.full_like(v, f), np.floor(v * 9.0))
    local_rev = _clamp01(reveal + (block - 0.5) * block_amt * glitch + (row_noise - 0.5) * 0.18 * glitch)
    local_rev = _smoothstep(0.22, 0.78, local_rev)

    amt = rgb_offset * glitch
    old_c = _sample_uv_bilinear(img_from, from_u, from_v)
    if amt > 1e-5:
        old_c = np.stack([
            _sample_uv_bilinear(img_from, np.clip(from_u + amt, 0.001, 0.999), from_v)[..., 0],
            old_c[..., 1],
            _sample_uv_bilinear(img_from, np.clip(from_u - amt, 0.001, 0.999), from_v)[..., 2],
        ], axis=-1)
    new_c = _sample_uv_bilinear(img_to, to_u, to_v)
    if amt > 1e-5:
        new_c = np.stack([
            _sample_uv_bilinear(img_to, np.clip(to_u - amt, 0.001, 0.999), to_v)[..., 0],
            new_c[..., 1],
            _sample_uv_bilinear(img_to, np.clip(to_u + amt, 0.001, 0.999), to_v)[..., 2],
        ], axis=-1)

    color = old_c * (1.0 - local_rev[..., None]) + new_c * local_rev[..., None]

    left_wash = (1.0 - _smoothstep(0.10, 0.78, u)) * glitch
    cyan_wash = _smoothstep(0.08, 0.62, u) * (1.0 - _smoothstep(0.86, 1.0, u)) * glitch
    red_ghost = old_c * np.array([1.34, 0.42, 0.38], dtype=np.float32)
    cyan_ghost = new_c * np.array([0.48, 1.12, 1.24], dtype=np.float32)

    lw = (left_wash * red_cyan * 0.42)[..., None]
    cw = (cyan_wash * red_cyan * 0.30)[..., None]
    color = color * (1.0 - lw) + red_ghost * lw
    color = color * (1.0 - cw) + cyan_ghost * cw

    old_ret = glitch * (1.0 - float(_smoothstep(0.94, 1.0, np.array(reveal))))
    old_ret_map = old_ret * (0.18 + 0.52 * (1.0 - np.abs(local_rev - 0.5) * 2.0)) * ghost_amt
    color = color * (1.0 - old_ret_map[..., None]) + old_c * old_ret_map[..., None]

    lines = np.sin((v + f * 0.017) * 1080.0) * scanline * glitch
    exp_pulse = (_s_hash(f, 12.4) - 0.35) * 0.10 * glitch
    color = color + lines[..., None] + exp_pulse
    return _clamp01(color)


def _render_glich_vhs(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    bands = int(uniforms.get("bands", 3))
    noise_amt = float(uniforms.get("noise", 0.6))
    bleed = float(uniforms.get("bleed", 0.5))
    wobble = float(uniforms.get("wobble", 0.5))

    LINES = 220.0
    FRAMES = 40.0
    BAND = 0.11
    STRIP = 0.06

    h_val = min(1.0, max(0.0, 2.5 * (1.0 - abs(2.0 * p - 1.0))))
    env = h_val * h_val * (3.0 - 2.0 * h_val)
    f_val = min(1.0, max(0.0, 1.0 - abs(p - 0.5) / 0.04))
    flash = f_val * f_val * (3.0 - 2.0 * f_val)

    frame = math.floor(p * FRAMES)
    line = np.floor(v * LINES)
    jitter = _hash12(line, np.full_like(line, frame + 7.0)) - 0.5

    c0 = (1.0 + 1.2 * BAND) * (1.0 - p) + (-1.2 * BAND) * p
    fresh = v > (c0 + 0.8 * BAND * jitter)

    def _band_dens(y: np.ndarray, c: float, w: float) -> np.ndarray:
        return 1.0 - _smoothstep(0.0, 1.0, np.abs(y - c) / w + 0.35 * jitter)

    dens = _band_dens(v, c0, BAND)
    tear = 1.0 - _smoothstep(0.0, 1.0, np.abs(v - c0) / (2.5 * BAND))
    for i in range(1, min(4, max(1, bands))):
        k = float(i)
        r_w = math.fmod((k * 0.1031) * (3.0 + 33.33), 1.0)
        w = BAND * (0.35 + 0.2 * r_w)
        speed = 1.3 + 0.9 * k
        cy = -w + (1.0 + 2.0 * w) * math.fmod(abs(math.fmod((k * 0.1031) * (5.0 + 33.33), 1.0) - speed * p), 1.0)
        dens = np.maximum(dens, 0.6 * _band_dens(v, cy, w))
        tear = np.maximum(tear, 0.5 * (1.0 - _smoothstep(0.0, 1.0, np.abs(v - cy) / (2.5 * w))))

    dens *= env
    tear *= env

    row_tear = _hash12(np.floor(v * LINES * 0.5), np.full_like(v, frame + 31.0)) - 0.5
    dx = wobble * env * (0.006 * np.sin(v * 7.0 + p * 23.0) + 0.004 * jitter)
    dx += (0.3 + 0.7 * noise_amt) * tear * 0.18 * row_tear
    strip = env * (1.0 - _smoothstep(0.0, STRIP, v))
    head_jit = _hash12(np.array([[frame]], dtype=np.float32), np.array([[41.0]], dtype=np.float32))[0, 0]
    dx += strip * (0.03 + 0.06 * np.maximum(0.0, 1.0 - v / STRIP)) * (0.6 + 0.8 * head_jit)

    qu = 1.0 - np.abs(1.0 - np.mod(u + dx, 2.0))
    qv = 1.0 - np.abs(1.0 - np.mod(v, 2.0))

    samp_from = _sample_uv_bilinear(img_from, qu, qv)
    samp_to = _sample_uv_bilinear(img_to, qu, qv)
    c = np.where(fresh[..., None], samp_to, samp_from)

    # Chroma bleed + fade
    bleed_len = bleed * (0.02 + 0.05 * dens) * env
    luma_w = np.array([0.299, 0.587, 0.114], dtype=np.float32)
    luma_c = np.sum(c * luma_w, axis=-1, keepdims=True)
    if np.max(bleed_len) > 1e-4:
        bu = 1.0 - np.abs(1.0 - np.mod(qu - bleed_len * 0.75, 2.0))
        b_from = _sample_uv_bilinear(img_from, bu, qv)
        b_to = _sample_uv_bilinear(img_to, bu, qv)
        avg = np.where(fresh[..., None], b_to, b_from)
        luma_avg = np.sum(avg * luma_w, axis=-1, keepdims=True)
        c = _clamp01(luma_c + (avg - luma_avg))
    rgb = c * (1.0 - (0.6 * dens)[..., None]) + luma_c * (0.6 * dens)[..., None]

    # Tape snow streaks + sparkles + dropout lines
    cell_x = np.floor(u * LINES * 0.3 * ratio + 40.0 * jitter)
    n_snow = _hash12(cell_x + frame * 37.0, line + frame * 17.0)
    amount = _clamp01(noise_amt * np.maximum(1.3 * dens, 0.8 * strip) + 0.35 * flash)
    snow = np.where(amount > 0.0, _smoothstep(0.0, 1.0, (n_snow - (1.0 - amount)) / np.maximum(0.4 * amount, 1e-4)), 0.0)
    snow *= 0.55 + 0.45 * _hash12(line + frame, cell_x)
    g = _hash12(np.floor(u * LINES * ratio) + frame * 13.0, line + frame * 29.0)
    snow = np.maximum(snow, np.where(amount > 0.0, 0.7 * _smoothstep(0.0, 1.0, (g - (1.0 - 0.4 * amount)) / np.maximum(0.4 * amount, 1e-4)), 0.0))
    dark = (g < 0.1 * amount).astype(np.float32)
    group = np.floor(v * LINES / 3.0)
    drop_rnd = _hash12(group, np.floor(u * 6.0 + 5.0 * _hash12(group, np.full_like(group, frame))) + frame * 7.0)
    drop = (drop_rnd >= (1.0 - 0.15 * flash)).astype(np.float32)

    rgb = rgb * (1.0 - 0.5 * dark[..., None])
    white_mix = _clamp01(snow + drop + 0.12 * flash)[..., None]
    rgb = rgb + white_mix * (1.0 - rgb)
    return _clamp01(rgb)


def _render_glich_displace(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    def _rand_vec(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        sn = np.mod(x * 12.9898 + y * 78.233, 3.14)
        return np.mod(np.sin(sn) * 43758.5453, 1.0)

    def _voronoi(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        px = np.floor(x)
        py = np.floor(y)
        fx = x - px
        fy = y - py
        res = np.full_like(x, 8.0)
        for j in (-1.0, 0.0, 1.0):
            for i in (-1.0, 0.0, 1.0):
                rnd = _rand_vec(px + i, py + j)
                rx = i - fx + rnd
                ry = j - fy + rnd
                res = np.minimum(res, rx * rx + ry * ry)
        return np.sqrt(res)

    def _ease1(t: float) -> float:
        if t <= 0.0 or t >= 1.0:
            return t
        return 0.5 * pow(2.0, 20.0 * t - 10.0) if t < 0.5 else -0.5 * pow(2.0, 10.0 - 20.0 * t) + 1.0

    def _ease2(t: float) -> float:
        return t if t >= 1.0 else 1.0 - pow(2.0, -10.0 * t)

    # Evaluate Voronoi displacement cleanly on downscaled field for high speed
    vb = _voronoi(0.003 * u + 2.0, 0.003 * v + 2.0)
    vg = _voronoi(0.2 * u, 0.2 * v)
    vr = _voronoi(u - 1.0, v - 1.0)
    vor_base = (vg + vr + vb) / 3.0

    e1 = _ease1(p)
    e2 = _ease2(p)
    dis1_x = ((img_from[..., 0] * 0.33 + 1.0 - img_from[..., 0] * 0.7 - 1.0 + 0.33 * 0.7 + (vor_base - 0.5) * 0.4) * (1.0 - e1))
    dis1_y = ((img_from[..., 1] * 0.33 + 1.0 - img_from[..., 1] * 0.7 - 1.0 + 0.33 * 0.7 + (vor_base - 0.5) * 0.4) * (1.0 - e1))
    dis2_x = ((img_to[..., 0] * 0.33 + 1.0 - img_to[..., 0] * 0.5 - 1.0 + 0.33 * 0.5 + (vor_base - 0.5) * 0.4) * e2)
    dis2_y = ((img_to[..., 1] * 0.33 + 1.0 - img_to[..., 1] * 0.5 - 1.0 + 0.33 * 0.5 + (vor_base - 0.5) * 0.4) * e2)

    d_col1 = _sample_uv_bilinear(img_to, u + dis1_x, v + dis1_y)
    d_col2 = _sample_uv_bilinear(img_from, u + dis2_x, v + dis2_y)

    luma_w = np.array([0.299, 0.587, 0.114], dtype=np.float32)
    gray = np.sum(np.minimum(d_col1, d_col2) * luma_w, axis=-1, keepdims=True)
    d_col2_g = np.repeat(_clamp01(gray * 2.0), 3, axis=-1)

    m1 = float(_smoothstep(0.0, 0.5, np.array(p)))
    m2 = float(_smoothstep(1.0, 0.5, np.array(p)))
    c1 = img_from * (1.0 - m1) + d_col2_g * m1
    c2 = img_to * (1.0 - m2) + d_col1 * m2
    return _clamp01(c1 * (1.0 - e1) + c2 * e1)


def _render_light_coloring(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    seed = float(uniforms.get("Seed", 2.31))

    def _sig(x: float, a: float) -> float:
        if x <= 0.5:
            return pow(max(x * 2.0, 0.0), a) / 2.0
        return 1.0 - pow(max(2.0 - x * 2.0, 0.0), a) / 2.0

    def _rand_f(co: float) -> float:
        r = math.fmod(math.sin(co * 24.9898 + seed) * 43758.5453, 1.0)
        return r + 1.0 if r < 0 else r

    def _s_rand_1d(px: float, shft: float) -> float:
        fl = math.floor(shft)
        fr = shft - fl
        r0 = math.fmod(math.sin((px * 12.9898 + fl * 0.5 + seed) * 78.233) * 43758.5453, 1.0)
        r1 = math.fmod(math.sin((px * 12.9898 + (fl + 1.0) * 0.5 + seed) * 78.233) * 43758.5453, 1.0)
        r0 = r0 + 1.0 if r0 < 0 else r0
        r1 = r1 + 1.0 if r1 < 0 else r1
        return r0 * (1.0 - _sig(fr, 2.0)) + r1 * _sig(fr, 2.0)

    # 13 film-burn light-leak waves + glowing hotspots
    f_acc = np.zeros_like(u, dtype=np.float32)
    for i in range(13):
        fi = float(i)
        r0 = _rand_f(fi)
        r1 = _rand_f(fi + 1.43)
        r2 = _rand_f(fi + 4.4)
        r3 = _rand_f(fi + 2.4)
        f_acc += np.sin(u * r0 * 6.0 + p * 8.0 + r1) * np.sin(v * r2 * 6.0 + p * 6.0 + r3)
        cx = _s_rand_1d(p * 1.3, fi + 1.0)
        cy = _s_rand_1d(p * 0.5, fi + 6.25)
        dist = np.sqrt((u - cx) ** 2 + (v - cy) ** 2) * (20.0 * (1.0 - r0) + 70.0 * r0)
        f_acc += 1.0 - _clamp01(dist)

    f_norm = (f_acc + 4.0) / 11.0
    sin_pi = math.sin(p * math.pi)
    base_rgb = np.stack([
        f_norm * 1.0,
        f_norm * 0.7,
        f_norm * 0.6,
    ], axis=-1)
    exps = np.array([1.0, 2.0 - sin_pi, 1.3], dtype=np.float32)
    f_col = (np.power(np.abs(base_rgb), exps) * np.sign(base_rgb)) * sin_pi

    zoom = 1.0 + _s_rand_1d(p * 5.0, 6.3) * sin_pi * 0.05
    zu = (u - 0.5) * zoom + 0.5
    zv = (v - 0.5) * zoom + 0.5

    m_sig = _sig(p, 10.0)
    blended = _sample_uv_bilinear(img_from, zu, zv) * (1.0 - m_sig) + _sample_uv_bilinear(img_to, zu, zv) * m_sig

    # Smooth circular bokeh blur (12 evenly distributed angles)
    blur_amt = sin_pi * 0.022
    if blur_amt > 1e-4:
        acc_img = blended.copy()
        n_taps = 8
        for k in range(n_taps):
            ang = 2.0 * math.pi * k / n_taps
            du = math.cos(ang) * blur_amt
            dv = math.sin(ang) * blur_amt
            acc_img += _sample_uv_bilinear(img_from, zu + du, zv + dv) * (1.0 - m_sig) + _sample_uv_bilinear(img_to, zu + du, zv + dv) * m_sig
        blended = acc_img / (n_taps + 1.0)

    return _clamp01(blended + f_col)


def _render_color_panels(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    direction = uniforms.get("direction", (1.0, 0.0))
    panels = max(1, min(3, int(uniforms.get("panels", 3))))
    c1 = np.array(uniforms.get("color1", (0.98, 0.76, 0.22, 1.0))[:3], dtype=np.float32)
    c2 = np.array(uniforms.get("color2", (0.93, 0.33, 0.36, 1.0))[:3], dtype=np.float32)
    c3 = np.array(uniforms.get("color3", (0.16, 0.20, 0.42, 1.0))[:3], dtype=np.float32)
    stagger = max(0.0, min(1.0, float(uniforms.get("stagger", 0.35))))
    skew = max(-1.0, min(1.0, float(uniforms.get("skew", 0.25))))

    dx, dy = float(direction[0]), float(direction[1])
    dlen = math.hypot(dx, dy)
    dir_x, dir_y = (dx / dlen, dy / dlen) if dlen > 0.0 else (1.0, 0.0)
    k = skew
    norm_a = math.sqrt(1.0 + k * k)
    ax = (dir_x + k * (-dir_y)) / norm_a
    ay = (dir_y + k * dir_x) / norm_a

    x = (u - 0.5) * ratio * ax + (v - 0.5) * ay
    e = 0.5 * (abs(ax) * ratio + abs(ay))
    aa = 0.0015
    start = -e - 2.0 * aa
    span = 2.0 * (e + 2.0 * aa)

    cut, hold = 0.46, 0.01
    m = float(panels - 1)
    dx_dur = (cut - hold) / (1.0 + m * stagger)
    dy_dur = (1.0 - cut - hold) / (1.0 + m * stagger)

    def _ease(t: float) -> float:
        s = min(1.0, max(0.0, t))
        u_e = 1.0 - s * s * (3.0 - 2.0 * s)
        return 1.0 - u_e * u_e * u_e

    def _cover(x_arr: np.ndarray, back: float, front: float) -> np.ndarray:
        return (_smoothstep(back - aa, back + aa, x_arr) * (1.0 - _smoothstep(front - aa, front + aa, x_arr)))[..., None]

    front0 = start + span * _ease(p / max(dx_dur, 1e-4))
    back0 = start + span * _ease((p - 1.0 + dy_dur) / max(dy_dur, 1e-4))
    mid_cut = 0.5 * (front0 + back0)
    out = np.where((x >= mid_cut)[..., None], img_from, img_to)
    cov0 = _cover(x, back0, front0)
    out = out * (1.0 - cov0) + c1 * cov0

    panel_colors = [c1, c2, c3]
    for i in range(1, panels):
        tx = i * stagger * dx_dur
        ty = i * stagger * dy_dur
        front = start + span * _ease((p - tx) / max(dx_dur, 1e-4))
        back = start + span * _ease((p - 1.0 + dy_dur + ty) / max(dy_dur, 1e-4))
        cov = _cover(x, back, front)
        out = out * (1.0 - cov) + panel_colors[i] * cov

    return _clamp01(out)


def _render_filter_wrap(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    strength = np.array([
        float(uniforms.get("r_strength", 1.0)),
        float(uniforms.get("g_strength", 1.0)),
        float(uniforms.get("b_strength", 1.0)),
    ], dtype=np.float32)
    wrapped = np.mod(img_from + strength * p, 1.0)
    wrap_mix = float(_smoothstep(0.0, 0.1, np.array(p)))
    from_fx = img_from * (1.0 - wrap_mix) + wrapped * wrap_mix
    return _clamp01(from_fx * (1.0 - p) + img_to * p)


def _render_click_photo(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    tilt = float(uniforms.get("tilt", 0.35))
    border = float(uniforms.get("border", 0.04))
    flash_str = float(uniforms.get("flash", 0.85))
    shadow_str = float(uniforms.get("shadow", 0.45))
    border_col = np.array(uniforms.get("borderColor", (0.96, 0.94, 0.89, 1.0))[:3], dtype=np.float32)

    SHRINK = 0.24
    RADIUS = 0.008
    AA = 0.0015

    qx = (u - 0.5) * ratio
    qy = v - 0.5
    half_img_x, half_img_y = 0.5 * ratio, 0.5
    half_card_x, half_card_y = half_img_x + border, half_img_y + border

    k = float(_smoothstep(0.05, 0.4, np.array(p)))
    t = min(1.0, max(0.0, (p - 0.3) / 0.7))
    fall = t * t
    s = 1.0 - SHRINK * k
    a = -tilt * (0.12 * k + 0.88 * fall)
    bound = (abs(math.sin(tilt)) * half_card_x + abs(math.cos(tilt)) * half_card_y) * (1.0 - SHRINK)
    lift = 0.035 * k * (1.0 - fall)
    cx, cy = 0.08 * fall, lift - (0.5 + bound + 0.1) * fall
    rad = RADIUS * k

    ca, sa = math.cos(a), math.sin(a)

    def _rounded_box(rx: np.ndarray, ry: np.ndarray, bx: float, by: float, r: float) -> np.ndarray:
        dx = np.abs(rx) - bx + r
        dy = np.abs(ry) - by + r
        outside = np.sqrt(np.maximum(dx, 0.0) ** 2 + np.maximum(dy, 0.0) ** 2)
        inside = np.minimum(np.maximum(dx, dy), 0.0)
        return outside + inside - r

    col = img_to.copy()
    sh = shadow_str * k
    if sh > 0.0:
        sx = (qx - cx - 0.012 * k)
        sy = (qy - cy + 0.022 * k)
        rsx = (ca * sx + sa * sy) / s
        rsy = (-sa * sx + ca * sy) / s
        ds = _rounded_box(rsx, rsy, half_card_x, half_card_y, rad) * s
        blur = 0.035 * s
        col = col * (1.0 - sh * (1.0 - _smoothstep(-blur, blur, ds)))[..., None]

    tx = qx - cx
    ty = qy - cy
    rx = (ca * tx + sa * ty) / s
    ry = (-sa * tx + ca * ty) / s
    d_card = _rounded_box(rx, ry, half_card_x, half_card_y, rad) * s
    d_img = _rounded_box(rx, ry, half_img_x, half_img_y, 0.0) * s
    card_cov = _clamp01(1.5 - d_card / AA)[..., None]
    img_cov = _clamp01(1.5 - d_img / AA)[..., None]

    photo = _sample_uv_bilinear(img_from, np.clip(rx / ratio + 0.5, 0.0, 1.0), np.clip(ry + 0.5, 0.0, 1.0))
    card = border_col * (1.0 - img_cov) + photo * img_cov
    col = col * (1.0 - card_cov) + card * card_cov

    f_bloom = flash_str * float(_smoothstep(0.0, 0.05, np.array(p))) * (1.0 - float(_smoothstep(0.05, 0.3, np.array(p))))
    col = 1.0 - (1.0 - col) * (1.0 - f_bloom)
    return _clamp01(col)


def _render_smoke(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    direction = uniforms.get("direction", (0.5, 0.1))
    scale = float(uniforms.get("scale", 2.5))
    spread = float(uniforms.get("spread", 0.4))
    softness = max(0.05, float(uniforms.get("softness", 0.5)))
    smoke_col = np.array(uniforms.get("color", (0.86, 0.86, 0.88, 1.0))[:3], dtype=np.float32)

    dx, dy = float(direction[0]), float(direction[1])
    dlen = math.hypot(dx, dy)
    dir_x, dir_y = (dx / dlen, dy / dlen) if dlen > 1e-4 else (0.0, 0.0)
    ext = 0.5 * (abs(dir_x) * ratio + abs(dir_y)) + 1e-4

    px = (u - 0.5) * ratio
    py = v - 0.5
    along = (0.5 + 0.5 * (px * dir_x + py * dir_y) / ext) if dlen > 1e-4 else np.full_like(u, 0.5)

    arrive = (p / 0.45) * (1.0 + spread) - spread * along
    leave = ((p - 0.55) / 0.45) * (1.0 + spread) - spread * along
    body = _smoothstep(0.0, 1.0, arrive) * (1.0 - _smoothstep(0.0, 1.0, leave))
    m = float(_smoothstep(0.48, 0.52, np.array(p)))
    base = img_from * (1.0 - m) + img_to * m
    if float(np.max(body)) <= 0.0:
        return base

    qx = (px - dx * (p - 0.5)) * scale
    qy = (py - dy * (p - 0.5)) * scale
    churn_x, churn_y = 0.5 * p, -0.35 * p
    warp_x = _fbm(qx + 3.1 + churn_x, qy + 1.7 + churn_y)
    warp_y = _fbm(qx + 8.3 - churn_x, qy + 2.8 - churn_y)
    wx = qx + 1.1 * (warp_x - 0.5)
    wy = qy + 1.1 * (warp_y - 0.5)
    n = _fbm(wx, wy)
    lit = 0.53 * (_vnoise(wx, wy) - _vnoise(wx, wy + 0.2))
    wisp = _vnoise(wx * 3.3 - 2.0 * churn_x, wy * 3.3 - 2.0 * churn_y) - 0.5

    edge = 2.0 * body - (1.0 - _smoothstep(0.1, 0.6, n)) + 1.6 * body * (1.0 - body) * wisp
    d = _smoothstep(0.0, softness, edge) * (0.5 + 0.5 * _smoothstep(0.2, 0.9, body))
    shade = (0.92 + 1.3 * lit) * (0.76 + 0.28 * _smoothstep(0.25, 0.75, n))
    shade = 1.0 * (1.0 - (0.3 + 0.7 * d)) + shade * (0.3 + 0.7 * d)
    smoke_rgb = _clamp01(smoke_col[None, None, :] * shade[..., None])
    d_m = d[..., None]
    return _clamp01(base * (1.0 - d_m) + smoke_rgb * d_m)


def _render_water(img_from: np.ndarray, img_to: np.ndarray, p: float, u: np.ndarray, v: np.ndarray, ratio: float, uniforms: Dict[str, Any]) -> np.ndarray:
    if p <= 0.0:
        return img_from
    if p >= 1.0:
        return img_to

    direction = uniforms.get("direction", (0.0, 1.0))
    amp_base = max(0.0, float(uniforms.get("amplitude", 0.06)))
    waves = max(0.01, float(uniforms.get("waves", 1.5)))
    hl = uniforms.get("highlight", (1.0, 1.0, 1.0, 0.8))
    hl_rgb = np.array(hl[:3], dtype=np.float32)
    hl_a = float(hl[3]) if len(hl) >= 4 else 0.8
    refraction = float(uniforms.get("refraction", 0.03))
    bubbles = float(uniforms.get("bubbles", 0.5))

    AA = 0.0015
    LINE = 0.006
    CELL = 0.08
    dx, dy = float(direction[0]), float(direction[1])
    dlen = math.hypot(dx, dy)
    dir_x, dir_y = (dx / dlen, dy / dlen) if dlen > 0.0 else (0.0, 1.0)
    ac_x, ac_y = -dir_y, dir_x

    px = (u - 0.5) * ratio
    py = v - 0.5
    e = 0.5 * (abs(dir_x) * ratio + abs(dir_y))
    w = 0.5 * (abs(dir_y) * ratio + abs(dir_x))
    d = px * dir_x + py * dir_y
    x = px * ac_x + py * ac_y

    stir = math.sin(math.pi * p)
    amp = amp_base * (0.35 + 0.65 * stir)
    margin = amp_base + 2.0 * LINE + AA
    smooth_p = p * p * (3.0 - 2.0 * p)
    blend_p = 0.5 * p + 0.5 * smooth_p
    mean = (-e - margin) * (1.0 - blend_p) + (e + margin) * blend_p

    k = math.pi * waves
    xw = x / max(w, 1e-4)
    surf = 0.6 * np.sin(k * xw + 0.5 * math.pi) * math.cos(2.0 * math.pi * 1.3 * p) + 0.4 * np.sin(1.7 * k * xw - 9.0 * p + 1.3)
    level = mean + amp * surf
    depth = level - d
    m = _smoothstep(-AA, AA, depth)

    bend = refraction * stir * np.exp(-np.maximum(depth, 0.0) / 0.06)
    off_x = bend * (dir_x * np.sin(18.0 * x - 7.0 * p) + ac_x * np.cos(13.0 * x + 5.0 * p))
    off_y = bend * (dir_y * np.sin(18.0 * x - 7.0 * p) + ac_y * np.cos(13.0 * x + 5.0 * p))
    b = _sample_uv_bilinear(img_to, np.clip(u + off_x / ratio, 0.0, 1.0), np.clip(v + off_y, 0.0, 1.0))

    # Rising glowing bubbles
    rise = mean + 0.5 * p
    bqx = x / CELL
    bqy = (d - rise) / CELL
    cell_x = np.floor(bqx)
    cell_y = np.floor(bqy)
    hs = _hash12(cell_x + 7.1, cell_y + 7.1)
    r_bub = (0.12 + 0.18 * _hash12(cell_x + 3.7, cell_y + 3.7)) * stir
    px_c = AA / CELL
    mask_b = (hs < bubbles * 0.6) & (r_bub > px_c)
    cx = cell_x + 0.5 + (0.42 - r_bub - px_c) * (_hash12(cell_x + 1.3, cell_y + 1.3) * 2.0 - 1.0) + 0.08 * np.sin(6.0 * p + 6.28 * hs)
    cy = cell_y + 0.5 + (0.42 - r_bub - px_c) * (_hash12(cell_x + 9.4, cell_y + 9.4) * 2.0 - 1.0)
    dist = np.sqrt((bqx - cx) ** 2 + (bqy - cy) ** 2)
    rim = _smoothstep(0.0, 1.0, (dist - (0.7 * r_bub - px_c)) / max(2 * px_c, 1e-4)) * (1.0 - _smoothstep(0.0, 1.0, (dist - (r_bub - px_c)) / max(2 * px_c, 1e-4)))
    glint_dist = np.sqrt((bqx - cx + 0.45 * r_bub * 0.7) ** 2 + (bqy - cy - 0.45 * r_bub * 0.7) ** 2)
    glint = 1.0 - _smoothstep(0.0, 1.0, (glint_dist - (0.25 * r_bub - px_c)) / max(2 * px_c, 1e-4))
    glow = np.where(mask_b, np.maximum(rim * 0.6, glint) * _smoothstep(0.0, 0.05, depth) * stir, 0.0)

    line = 1.0 - _smoothstep(LINE - AA, LINE + AA, np.abs(depth - LINE))
    line = line + 0.35 * stir * np.exp(-np.maximum(depth, 0.0) / 0.03) * m
    light = (hl_a * _clamp01(np.maximum(line, glow)) * (0.4 + 0.6 * stir))[..., None]
    b = b * (1.0 - light) + hl_rgb * light

    m3 = m[..., None]
    return _clamp01(img_from * (1.0 - m3) + b * m3)


_SHADER_DISPATCH = {
    "glich2_tranjection.glsl": _render_glich2,
    "glich_trajection_effect.glsl": _render_glich_vhs,
    "glich_tranjectiion.glsl": _render_glich_displace,
    "light_coloring_effect.glsl": _render_light_coloring,
    "color_tranjection.glsl": _render_color_panels,
    "filter_tranjection.glsl": _render_filter_wrap,
    "click_photo_type_tranjection.glsl": _render_click_photo,
    "smoke_transition.glsl": _render_smoke,
    "water_type_tranjection.glsl": _render_water,
}


def render_glsl_transition_frame(
    shader_filename: str,
    img_from_u8: np.ndarray,
    img_to_u8: np.ndarray,
    progress: float,
    uniforms: Optional[Dict[str, Any]] = None,
) -> np.ndarray:
    """Render a single uint8 RGB frame `(H, W, 3)` using the selected `.glsl` shader's algorithm."""
    fname = os.path.basename(shader_filename)
    renderer = _SHADER_DISPATCH.get(fname)
    if renderer is None:
        p = float(min(1.0, max(0.0, progress)))
        return np.clip(img_from_u8 * (1.0 - p) + img_to_u8 * p, 0, 255).astype(np.uint8)

    h, w, _ = img_from_u8.shape
    ratio = float(w) / max(1.0, float(h))
    u, v = _make_uv_grids(h, w)
    from_f = img_from_u8.astype(np.float32) / 255.0
    to_f = img_to_u8.astype(np.float32) / 255.0
    out_f = renderer(from_f, to_f, float(min(1.0, max(0.0, progress))), u, v, ratio, uniforms or {})
    return np.clip(out_f * 255.0, 0, 255).astype(np.uint8)


# =============================================================================
# FFmpeg Clip Trimming, Bridge Rendering & Sync-Locked Stitching
# =============================================================================

def _probe_media_info(clip_path: str) -> Tuple[float, bool]:
    """Return `(duration_seconds, has_audio_stream)` for an MP4 file."""
    dur = 0.0
    has_audio = False
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", os.path.abspath(clip_path)],
            stderr=subprocess.DEVNULL, timeout=15
        ).decode().strip()
        dur = float(out)
    except Exception:
        dur = 0.0
    try:
        aout = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=codec_type", "-of", "csv=p=0", os.path.abspath(clip_path)],
            stderr=subprocess.DEVNULL, timeout=15
        ).decode().strip()
        has_audio = len(aout) > 0
    except Exception:
        has_audio = False
    return dur, has_audio


def _extract_clip_frames(clip_path: str, start_sec: float, dur_sec: float, w: int, h: int, fps: int, n_frames: int) -> List[np.ndarray]:
    """Decode `n_frames` RGB24 frames of `(h, w, 3)` cleanly via FFmpeg pipe."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{max(0.0, start_sec):.3f}",
        "-t", f"{max(0.1, dur_sec):.3f}",
        "-i", os.path.abspath(clip_path),
        "-vf", f"scale={w}:{h}:flags=bilinear,fps={fps}",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "pipe:1",
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=60)
    frame_bytes = w * h * 3
    raw = res.stdout or b""
    count = len(raw) // frame_bytes
    frames: List[np.ndarray] = []
    for k in range(count):
        arr = np.frombuffer(raw[k * frame_bytes:(k + 1) * frame_bytes], dtype=np.uint8).reshape((h, w, 3))
        frames.append(arr)
    if not frames:
        return []
    while len(frames) < n_frames:
        frames.append(frames[-1])
    if len(frames) > n_frames:
        # Uniformly pick n_frames indices across extracted window
        idxs = [int(round(i * (len(frames) - 1) / max(1, n_frames - 1))) for i in range(n_frames)]
        frames = [frames[idx] for idx in idxs]
    return frames


def _render_bridge_clip(
    from_clip: str,
    to_clip: str,
    from_dur: float,
    plan: Dict[str, Any],
    lead_sec: float,
    trail_sec: float,
    target_w: int,
    target_h: int,
    fps: int,
    has_audio: bool,
    out_mp4: str,
) -> bool:
    """Render exact `.glsl` transition bridge MP4 preserving exact `lead_sec + trail_sec` A/V duration."""
    trans_dur = lead_sec + trail_sec
    n_frames = max(6, int(round(trans_dur * fps)))

    # Cap internal shader computation to <= 800px long edge so RAM stays tiny on 512MB containers
    scale = min(1.0, 800.0 / max(1, max(target_w, target_h)))
    work_w = max(64, (int(round(target_w * scale)) // 2) * 2)
    work_h = max(64, (int(round(target_h * scale)) // 2) * 2)

    tail_start = max(0.0, from_dur - trans_dur)
    from_frames = _extract_clip_frames(from_clip, tail_start, trans_dur, work_w, work_h, fps, n_frames)
    to_frames = _extract_clip_frames(to_clip, 0.0, trans_dur, work_w, work_h, fps, n_frames)
    if not from_frames or not to_frames:
        return False

    uniforms = dict(plan.get("meta", {}).get("uniforms", {}))
    # Randomize Seed slightly on light coloring leaks so repeated uses look organic
    if plan["file"] == "light_coloring_effect.glsl":
        uniforms["Seed"] = round(random.uniform(1.1, 9.8), 2)

    sfx_path = plan.get("sfx_path")
    use_sfx = bool(has_audio and sfx_path and os.path.exists(sfx_path))

    inputs: List[str] = [
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{work_w}x{work_h}", "-r", f"{fps}",
        "-i", "pipe:0",
    ]
    filter_parts: List[str] = [
        f"[0:v]scale={target_w}:{target_h}:flags=bilinear,setsar=1,format=yuv420p[vout]"
    ]

    if has_audio:
        a_tail_start = max(0.0, from_dur - lead_sec)
        inputs.extend(["-ss", f"{a_tail_start:.3f}", "-t", f"{lead_sec:.3f}", "-i", os.path.abspath(from_clip)])
        inputs.extend(["-ss", "0.000", "-t", f"{trail_sec:.3f}", "-i", os.path.abspath(to_clip)])
        filter_parts.append(
            "[1:a]aresample=44100,aformat=channel_layouts=stereo[a1];"
            "[2:a]aresample=44100,aformat=channel_layouts=stereo[a2];"
            "[a1][a2]concat=n=2:v=0:a=1[abase]"
        )
        if use_sfx:
            inputs.extend(["-i", os.path.abspath(sfx_path)])
            fade_len = min(0.22, trans_dur * 0.35)
            fade_st = max(0.0, trans_dur - fade_len)
            filter_parts.append(
                f"[3:a]aresample=44100,aformat=channel_layouts=stereo,"
                f"atrim=0:{trans_dur:.3f},asetpts=PTS-STARTPTS,"
                f"afade=t=in:st=0:d=0.02,afade=t=out:st={fade_st:.3f}:d={fade_len:.3f},"
                f"volume=0.36[asfx];"
                f"[abase][asfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
                f"alimiter=limit=0.96:level=disabled[aout]"
            )
        else:
            filter_parts.append("[abase]anull[aout]")

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "[vout]",
    ]
    if has_audio:
        cmd.extend(["-map", "[aout]", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2"])
    else:
        cmd.append("-an")

    cmd.extend([
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24", "-r", f"{fps}",
        "-threads", "1", "-pix_fmt", "yuv420p",
        "-t", f"{trans_dur:.3f}",
        os.path.abspath(out_mp4),
    ])

    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        err_b = b""
        try:
            for k in range(n_frames):
                prog = (k + 0.5) / float(n_frames)
                frame_u8 = render_glsl_transition_frame(plan["file"], from_frames[k], to_frames[k], prog, uniforms)
                if proc.stdin:
                    try:
                        proc.stdin.write(frame_u8.tobytes())
                    except (BrokenPipeError, ValueError, OSError):
                        break
        finally:
            if proc.stdin:
                try:
                    proc.stdin.flush()
                except Exception:
                    pass
                try:
                    proc.stdin.close()
                except Exception:
                    pass
                proc.stdin = None
            if proc.stderr:
                try:
                    err_b = proc.stderr.read()
                except Exception:
                    err_b = b""
                try:
                    proc.stderr.close()
                except Exception:
                    pass
                proc.stderr = None
            try:
                proc.wait(timeout=90)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        ok = proc.returncode == 0 and os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 1000
        if not ok and err_b:
            print(f"⚠️ [GLSL Bridge Warning]: {err_b.decode(errors='ignore')[-220:]}")
        return ok
    except Exception as e_b:
        print(f"⚠️ [GLSL Bridge Error]: {e_b}")
        return False


def _trim_scene_segment(src_mp4: str, start_sec: float, dur_sec: float, fps: int, has_audio: bool, out_mp4: str) -> bool:
    """Trim a scene edge cleanly with re-encode so final concat remains frame-accurate."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{max(0.0, start_sec):.3f}",
        "-t", f"{max(0.1, dur_sec):.3f}",
        "-i", os.path.abspath(src_mp4),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24", "-r", f"{fps}",
        "-threads", "1", "-pix_fmt", "yuv420p",
    ]
    if has_audio:
        cmd.extend(["-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2"])
    else:
        cmd.append("-an")
    cmd.append(os.path.abspath(out_mp4))
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        return res.returncode == 0 and os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 1000
    except Exception:
        return False


def apply_glsl_transitions_to_segments(
    segment_paths: List[str],
    scene_texts: List[str],
    mode: str,
    target_size: Tuple[int, int],
    job_dir: str,
    fps: int = 25,
) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """
    Insert script-driven GLSL shader transitions cleanly between qualifying segments.

    Returns:
      - `final_segments`: Updated list of MP4 paths ready for concat.
      - `temp_created`: Temporary bridge/trimmed files created in `job_dir` for cleanup.
      - `sfx_events`: List of `{time, sfx_path, file}` (useful when segments have no audio stream yet, e.g. Song Engine).
    """
    if len(segment_paths) < 2:
        return segment_paths, [], []

    durations: List[float] = []
    audio_flags: List[bool] = []
    for p in segment_paths:
        d, has_a = _probe_media_info(p)
        durations.append(d)
        audio_flags.append(has_a)

    plans = plan_glsl_transitions(scene_texts, durations, mode=mode)
    if not plans:
        return segment_paths, [], []

    w, h = int(target_size[0]), int(target_size[1])
    final_segments: List[str] = []
    temp_created: List[str] = []
    sfx_events: List[Dict[str, Any]] = []

    cum_time = 0.0
    n = len(segment_paths)
    prev_bridged = False

    for i in range(n):
        orig_path = segment_paths[i]
        d_i = durations[i]
        has_a_i = audio_flags[i]

        has_in_bridge = prev_bridged and ((i - 1) in plans)
        has_out_bridge = i in plans

        trim_start = 0.0
        if has_in_bridge:
            prev_plan = plans[i - 1]
            trim_start = prev_plan["duration"] * 0.5

        trim_end = d_i
        out_bridge_path = None
        if has_out_bridge:
            out_plan = plans[i]
            lead = out_plan["duration"] * 0.5
            trail = out_plan["duration"] - lead
            next_has_a = audio_flags[i + 1]
            has_a = has_a_i and next_has_a
            out_bridge_path = os.path.join(job_dir, f"temp_glsl_bridge_{i}.mp4")

            ok_bridge = _render_bridge_clip(
                from_clip=orig_path,
                to_clip=segment_paths[i + 1],
                from_dur=d_i,
                plan=out_plan,
                lead_sec=lead,
                trail_sec=trail,
                target_w=w,
                target_h=h,
                fps=fps,
                has_audio=has_a,
                out_mp4=out_bridge_path,
            )
            if ok_bridge:
                trim_end = max(trim_start + 0.2, d_i - lead)
                temp_created.append(out_bridge_path)
            else:
                out_bridge_path = None
                has_out_bridge = False

        # Segment i itself (trimmed only if incoming or outgoing bridge succeeded)
        if has_in_bridge or out_bridge_path:
            seg_dur = max(0.2, trim_end - trim_start)
            trimmed_path = os.path.join(job_dir, f"temp_glsl_trim_{i}.mp4")
            if _trim_scene_segment(orig_path, trim_start, seg_dur, fps, has_a_i, trimmed_path):
                final_segments.append(trimmed_path)
                temp_created.append(trimmed_path)
                cum_time += seg_dur
            else:
                # Roll back outgoing bridge if segment trim failed so A/V sync stays safe
                final_segments.append(orig_path)
                cum_time += d_i
                out_bridge_path = None
                has_out_bridge = False
        else:
            final_segments.append(orig_path)
            cum_time += d_i

        if out_bridge_path:
            out_plan = plans[i]
            if out_plan.get("sfx_path"):
                sfx_events.append({
                    "time": round(cum_time, 3),
                    "sfx_path": out_plan["sfx_path"],
                    "shader": out_plan["file"],
                    "reason": out_plan["reason"],
                })
            print(
                f"✨ [GLSL Transition] Cut {i+1}->{i+2} ({mode.upper()}): '{out_plan['file']}' "
                f"(reason='{out_plan['reason']}'"
                + (f", sfx='{os.path.basename(out_plan['sfx_path'])}'" if out_plan.get("sfx_path") else "")
                + ")"
            )
            final_segments.append(out_bridge_path)
            cum_time += out_plan["duration"]
            prev_bridged = True
        else:
            prev_bridged = False

    return final_segments, temp_created, sfx_events


def overlay_glitch_sfx_events_on_video(video_path: str, sfx_events: List[Dict[str, Any]]) -> bool:
    """
    Overlay timed glitch SFX ticks onto a completed MP4 video using `-c:v copy`
    without altering primary audio loudness (`normalize=0`) or existing audio logic.
    """
    if not video_path or not os.path.exists(video_path) or not sfx_events:
        return False

    valid_events = [
        ev for ev in sfx_events
        if ev.get("sfx_path") and os.path.exists(ev["sfx_path"])
    ]
    if not valid_events:
        return False

    dur, has_a = _probe_media_info(video_path)
    if not has_a or dur <= 0.1:
        return False

    tmp_out = f"{os.path.splitext(video_path)[0]}_sfx_tmp.mp4"
    inputs = ["-i", os.path.abspath(video_path)]
    filter_parts = ["[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[abase]"]
    mix_labels = ["[abase]"]

    for idx, ev in enumerate(valid_events, start=1):
        inputs.extend(["-i", os.path.abspath(ev["sfx_path"])])
        delay_ms = max(0, int(round(float(ev.get("time", 0.0)) * 1000.0)))
        lbl = f"asfx{idx}"
        filter_parts.append(
            f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo,"
            f"atrim=0:0.65,asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=0.02,afade=t=out:st=0.45:d=0.20,"
            f"volume=0.35,adelay={delay_ms}|{delay_ms}[{lbl}]"
        )
        mix_labels.append(f"[{lbl}]")

    n_in = len(mix_labels)
    filter_parts.append(
        f"{''.join(mix_labels)}amix=inputs={n_in}:duration=first:dropout_transition=0:normalize=0,"
        f"alimiter=limit=0.96:level=disabled[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "0:v:0",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-t", f"{dur:.3f}",
        "-movflags", "+faststart",
        os.path.abspath(tmp_out),
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        if res.returncode == 0 and os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 1000:
            os.replace(tmp_out, video_path)
            return True
    except Exception as e_ov:
        print(f"⚠️ [GLSL Song SFX Overlay Warning]: {e_ov}")
    finally:
        if os.path.exists(tmp_out):
            try:
                os.remove(tmp_out)
            except Exception:
                pass
    return False

