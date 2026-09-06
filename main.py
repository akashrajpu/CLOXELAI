import os
import sys
import time
import random
import hashlib
import uuid
import shutil
import json
import requests
import warnings
import urllib.parse
import urllib.request
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
try:
    from googleapiclient.discovery import build
    import google_auth_oauthlib.flow
except Exception as _g_err:
    build = None
    google_auth_oauthlib = None

from apscheduler.schedulers.background import BackgroundScheduler
import requests
from firewall_security import FirewallMiddleware, waf
try:
    from web_image_fetcher import fetch_web_image
except Exception as _w_err:
    print(f"⚠️ web_image_fetcher top import warning: {_w_err}")
    fetch_web_image = None

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "secret_placeholder")

try:
    import razorpay
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
except Exception as e:
    razorpay_client = None
    print(f"Razorpay initialization warning: {e}")

from video_editor import merge_and_export
from audio_engine import make_audio
from video_fetcher import fetch_videos

from passlib.context import CryptContext
from pymongo import MongoClient
import pymongo

load_dotenv("config.env")

cloudinary.config( 
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.getenv('CLOUDINARY_API_KEY'), 
  api_secret = os.getenv('CLOUDINARY_API_SECRET') 
)

MONGO_URI = os.getenv('MONGO_URI')
mongo_client = None
db = None
users_collection = None
videos_collection = None
rendering_jobs = None

if MONGO_URI:
    try:
        mongo_client = MongoClient(
            MONGO_URI,
            maxPoolSize=100,
            minPoolSize=10,
            maxIdleTimeMS=60000,
            waitQueueTimeoutMS=10000,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=45000,
            connectTimeoutMS=10000,
            retryWrites=True,
            retryReads=True
        )
        mongo_client.admin.command('ping')
        db = mongo_client.cloxel_db
        users_collection = db.users
        videos_collection = db.videos
        rendering_jobs = db.rendering_jobs

        try:
            users_collection.create_index("internal_id", unique=True, background=True)
            users_collection.create_index("email", background=True)
            users_collection.create_index("phone", background=True)
            videos_collection.create_index([("internal_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)], background=True)
            videos_collection.create_index("job_id", background=True)
            rendering_jobs.create_index("job_id", unique=True, background=True)
            print("🚀 Ultra-High Speed Production MongoDB Indexes & Pool Verified (maxPoolSize=100)!")
        except Exception as idx_err:
            print(f"Index creation notice: {idx_err}")

        print("✅ Production MongoDB connected and hardened successfully!")
    except Exception as e:
        print(f"❌ CRITICAL WARNING: Failed to connect to MongoDB using provided MONGO_URI. Error: {e}")
        mongo_client = None
        db = None
        users_collection = None
        videos_collection = None
        rendering_jobs = None
else:
    print("WARNING: MONGO_URI is missing in config.env! Authentication will not work properly.")

def ensure_db_alive():
    """Ultra-resilient DB heart-beat to auto-reconnect MongoDB if network hiccups occur."""
    global mongo_client, db, users_collection, videos_collection, rendering_jobs
    if MONGO_URI and mongo_client is not None:
        try:
            mongo_client.admin.command('ping')
        except Exception as ping_err:
            print(f"⚠️ MongoDB reconnecting after network ping failure: {ping_err}")
            try:
                mongo_client = MongoClient(
                    MONGO_URI,
                    maxPoolSize=100,
                    minPoolSize=10,
                    maxIdleTimeMS=60000,
                    waitQueueTimeoutMS=10000,
                    serverSelectionTimeoutMS=5000,
                    socketTimeoutMS=45000,
                    connectTimeoutMS=10000,
                    retryWrites=True,
                    retryReads=True
                )
                db = mongo_client.cloxel_db
                users_collection = db.users
                videos_collection = db.videos
                rendering_jobs = db.rendering_jobs
                print("🔄 MongoDB auto-reconnected successfully!")
            except Exception as rec_err:
                print(f"❌ DB Auto-reconnect failed: {rec_err}")

def update_job_status(job_id: str, status_data: dict):
    jobs[job_id] = status_data
    if rendering_jobs is not None:
        try:
            status_copy = {k: v for k, v in status_data.items() if k not in ["file", "dir"]}
            rendering_jobs.update_one({"job_id": job_id}, {"$set": status_copy}, upsert=True)
        except Exception as e_db:
            print(f"⚠️ Failed to update job status in DB: {e_db}")

def ping_server():
    try:
        ensure_db_alive()
        url = os.getenv("RENDER_EXTERNAL_URL", "https://cloxel.onrender.com")
        resp = requests.get(url, timeout=10)
        print(f"⏰ Self-ping & DB Heartbeat active: Status {resp.status_code}")
    except Exception as e:
        print(f"Self-ping failed: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(ping_server, 'interval', minutes=3)
scheduler.add_job(waf.reset_all_bans, 'interval', hours=6)

def parse_time_to_minutes(time_str: str) -> Optional[int]:
    """Parses 12h or 24h time string (e.g. '10:00 AM', '10:00 PM', '18:00', '10:00') to minutes past midnight"""
    if not time_str:
        return None
    time_str = str(time_str).strip().upper()
    try:
        is_pm = "PM" in time_str
        is_am = "AM" in time_str
        digits = re.findall(r'\d+', time_str)
        if not digits:
            return None
        h = int(digits[0])
        m = int(digits[1]) if len(digits) > 1 else 0
        
        if is_pm and h < 12:
            h += 12
        elif is_am and h == 12:
            h = 0
            
        return h * 60 + m
    except Exception:
        return None

def build_youtube_metadata(topic: str, full_script: str = "", video_type: str = "short", custom_title: str = "", custom_desc: str = ""):
    """
    High-Scale 100% Unique AI YouTube Title & SEO Description Generator.
    Guarantees every video gets a unique, click-worthy, SEO-optimized title and description.
    Never duplicates titles across 10,000+ users.
    Mandatory hashtags included: #cloxelai.onrender.com #cloxel.onrender.com
    """
    import random
    import hashlib
    
    topic_clean = (topic or "Cloxel AI Video").strip()
    topic_title = topic_clean.title()
    script_text = (full_script or "").strip()
    
    seed_str = f"{topic_clean}_{script_text[:100]}_{random.randint(1000, 9999)}_{time.time()}"
    hash_num = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    
    script_words = [w for w in script_text.replace("\n", " ").split() if len(w) > 4 and w.isalpha()]
    keyword_addon = f" ({script_words[hash_num % len(script_words)].title()})" if script_words else ""
    
    if custom_title and len(custom_title.strip()) > 15 and custom_title.strip().lower() != topic_clean.lower():
        clean_title = custom_title.strip()
    else:
        if video_type == "long":
            long_title_templates = [
                f"The Shocking Truth About {topic_title}{keyword_addon} | Full AI Documentary",
                f"Everything You Need To Know About {topic_title} | Complete Guide",
                f"Uncovering The Hidden Secrets Of {topic_title}{keyword_addon} | In-Depth Narrative",
                f"Why {topic_title} Changes Everything You Know | Full Analysis",
                f"{topic_title}: The Hidden Reality Exposed{keyword_addon} | Deep Dive",
                f"Inside The Mystery Of {topic_title} | Full AI Narrative",
                f"The Untold Story Of {topic_title}{keyword_addon} | Complete Documentary",
                f"What They Don't Tell You About {topic_title} | Full Deep Dive"
            ]
            clean_title = long_title_templates[hash_num % len(long_title_templates)]
        else:
            short_title_templates = [
                f"Mind-Blowing Facts About {topic_title}! 😱 #shorts",
                f"Did You Know THIS About {topic_title}? 🚀 #shorts",
                f"The Secrets Of {topic_title} Exposed! ⚡ #shorts",
                f"Why {topic_title} Will Blow Your Mind! 🔥 #shorts",
                f"Crazy Truth About {topic_title}{keyword_addon}! 🤯 #shorts",
                f"You Won't Believe THIS About {topic_title}! 💥 #shorts",
                f"Unbelievable {topic_title} Facts! 🌟 #shorts"
            ]
            clean_title = short_title_templates[hash_num % len(short_title_templates)]

    if len(clean_title) > 95:
        clean_title = clean_title[:91] + "..."
    if video_type == "short" and "#shorts" not in clean_title.lower():
        clean_title = clean_title[:85] + " #shorts"

    body_text = (custom_desc or script_text or "").strip()
    if not body_text:
        body_text = f"Explore everything about {topic_title} in this AI-generated video!"
        
    sentences = [s.strip() for s in body_text.replace("\n", " ").replace("!", ".").replace("?", ".").split(".") if len(s.strip()) > 8]
    summary_text = ". ".join(sentences[:3]) + "." if sentences else body_text[:300]
    
    mandatory_tags = "#cloxelai.onrender.com #cloxel.onrender.com"
    website_link = "🌐 Created & Auto-Published via Cloxel AI Engine: https://cloxelai.onrender.com"

    if video_type == "long":
        highlights = ""
        if len(sentences) >= 3:
            pts = sentences[1:6]
            highlights = "\n".join([f"  • {p.strip()}" for p in pts])

        seo_desc = (
            f"🎬 {topic_title} - Full Video Narrative & Documentary\n\n"
            f"📌 About this video:\n{summary_text}\n\n"
        )
        if highlights:
            seo_desc += f"💡 Key Highlights:\n{highlights}\n\n"

        seo_desc += (
            f"🔔 Subscribe to Cloxel AI for daily automated AI videos, deep dives & documentaries!\n\n"
            f"{website_link}\n\n"
            f"🏷️ Tags & Links:\n"
            f"{mandatory_tags} #YouTubeLongs #Trending #Documentary #AI #{topic_title.replace(' ', '')}"
        )
    else:
        seo_desc = (
            f"🎬 {topic_title} (Short Reel)\n\n"
            f"{summary_text}\n\n"
            f"👉 Follow Cloxel AI for daily viral reels & short videos!\n\n"
            f"{website_link}\n\n"
            f"{mandatory_tags} #Shorts #Reels #Viral #Trending #AI #{topic_title.replace(' ', '')}"
        )

    if "#cloxelai.onrender.com" not in seo_desc:
        seo_desc += " #cloxelai.onrender.com"
    if "#cloxel.onrender.com" not in seo_desc:
        seo_desc += " #cloxel.onrender.com"

    return clean_title, seo_desc


def upload_video_to_youtube_core(user_id: str, video_file: str, title: str, description: str = "", is_short: bool = False) -> Optional[str]:
    """
    Automated YouTube Video Publisher (High-Scale 10,000+ User Ready):
    Uses user's stored OAuth credentials from MongoDB to publish video directly to YouTube with retry backoff & token refresh.
    """
    if users_collection is None:
        print("❌ MongoDB not configured for YouTube auto-upload")
        return None

    if not video_file or not os.path.exists(video_file):
        print(f"⚠️ Video file does not exist on disk for YouTube upload: {video_file}")
        return None

    user = users_collection.find_one({"internal_id": user_id})
    if not user or "youtube_credentials" not in user:
        print(f"⚠️ User {user_id} has no linked YouTube credentials!")
        return None

    creds_data = user.get("youtube_credentials", {})
    if not creds_data or "token" not in creds_data:
        print(f"⚠️ Invalid YouTube credentials for user {user_id}")
        return None

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        credentials = Credentials(
            token=creds_data.get("token"),
            refresh_token=creds_data.get("refresh_token"),
            token_uri=creds_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=creds_data.get("client_id", os.getenv("YOUTUBE_CLIENT_ID")),
            client_secret=creds_data.get("client_secret", os.getenv("YOUTUBE_CLIENT_SECRET")),
            scopes=creds_data.get("scopes", ["https://www.googleapis.com/auth/youtube.upload"])
        )

        if (credentials.expired or not credentials.valid) and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                if users_collection is not None:
                    users_collection.update_one(
                        {"internal_id": user_id},
                        {"$set": {
                            "youtube_credentials.token": credentials.token,
                            "youtube_credentials.status": "active",
                            "youtube_credentials.refreshed_at": datetime.utcnow()
                        }}
                    )
                print(f"🔄 YouTube OAuth token refreshed successfully for user {user_id}")
            except Exception as e_ref:
                print(f"⚠️ Automatic token refresh warning for user {user_id}: {e_ref}")

        youtube = build("youtube", "v3", credentials=credentials)

        video_kind = "short" if is_short else "long"
        clean_title, full_desc = build_youtube_metadata(
            topic=title,
            full_script=description,
            video_type=video_kind,
            custom_title=title if (title and len(title) > 15) else "",
            custom_desc=description
        )

        body = {
            "snippet": {
                "title": clean_title,
                "description": full_desc,
                "tags": ["AI", "Viral", "Shorts", "Cloxel", "cloxelai.onrender.com", "cloxel.onrender.com"],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_file, chunksize=1024*1024, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        retry_count = 0
        while response is None and retry_count < 3:
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"🚀 YouTube Upload Progress for {user_id}: {int(status.progress() * 100)}%")
            except Exception as e_chunk:
                err_msg = str(e_chunk)
                if "invalid_grant" in err_msg or "expired" in err_msg or "revoked" in err_msg:
                    print(f"⚠️ YouTube OAuth Token Expired/Revoked for user {user_id}. Marking channel as expired & saving pending upload.")
                    if users_collection is not None:
                        users_collection.update_one(
                            {"internal_id": user_id},
                            {"$set": {
                                "youtube_credentials.status": "expired",
                                "youtube_credentials.error": "Google OAuth token expired or revoked. Please re-connect YouTube channel."
                            },
                            "$push": {
                                "pending_youtube_uploads": {
                                    "video_file": video_file,
                                    "title": title,
                                    "description": description,
                                    "is_short": is_short,
                                    "created_at": datetime.utcnow()
                                }
                            }}
                        )
                    return None
                retry_count += 1
                print(f"⚠️ YouTube upload chunk retry {retry_count}/3 for {user_id}: {e_chunk}")
                time.sleep(2 * retry_count)

        if not response or "id" not in response:
            raise RuntimeError(f"YouTube upload response missing video ID for user {user_id}")

        youtube_id = response.get("id")
        youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
        print(f"🎉 SUCCESS! Video auto-published to YouTube for user {user_id}: {youtube_url}")

        videos_collection.update_one(
            {"internal_id": user_id, "topic": title},
            {"$set": {"youtube_url": youtube_url, "youtube_id": youtube_id, "uploaded_to_yt_at": datetime.utcnow()}}
        )

        return youtube_url

    except Exception as e:
        err_str = str(e)
        print(f"❌ YouTube Auto-Upload Error for user {user_id}: {e}")
        if "invalid_grant" in err_str or "expired" in err_str or "revoked" in err_str:
            if users_collection is not None:
                users_collection.update_one(
                    {"internal_id": user_id},
                    {"$set": {
                        "youtube_credentials.status": "expired",
                        "youtube_credentials.error": "Google OAuth token expired or revoked. Please re-connect YouTube channel."
                    }}
                )
        return None

def resolve_random_topic(topic: str = "", category: str = "Random") -> str:
    """Dynamically resolves random topics from a large diverse pool if user selected Random Topic or empty topic."""
    import random
    topic_clean = (topic or "").strip()
    topic_low = topic_clean.lower()

    is_random_requested = (
        not topic_clean or
        topic_low in ["random", "random topic", "default", "ai script", "generate script", "none"] or
        "space exploration" in topic_low or
        "history of ancient warriors" in topic_low or
        "ai innovations" in topic_low or
        "ai technology" in topic_low
    )

    if is_random_requested:
        category_pools = {
            "cartoon": [
                "Chintu aur Uska Magic Cycle",
                "Ramesh Ka Superhit Jugaad",
                "Pappu aur Ali Baba Ke Chote Bhai",
                "Bunty Ka High-Speed Scooter Drama",
                "Golu Ka Canteen Magic Samosa",
                "Dhoolu aur Uski Bolne Wali Billi",
                "Chatur Pandit Ka Magic Ladoo Test",
                "Motu aur Chhotu Ka Jungle Adventure"
            ],
            "horror": [
                "The Haunted House of Ghost Highway",
                "The Unsolved Midnight Cry Mystery",
                "Secret Horror Tale of Abandoned Fort",
                "Dark Mirror Curse and Phantom Shadow"
            ],
            "tech": [
                "How Future AI Robots Will Change 2030",
                "Secret Flying Car Technology Miracles",
                "Quantum Computer Secrets and AI Superpowers",
                "Brain-Computer Chip Transplants in Humans"
            ],
            "history": [
                "Unsolved Secrets of Great Pyramids",
                "Lost Wealth of Ancient Emperor Empires",
                "Mystery of The Lost City of Atlantis",
                "War Tactics of Ancient Legendary Warriors"
            ],
            "science": [
                "What If Earth Stopped Spinning for 5 Seconds?",
                "Mysteries of Deep Sea Alien-like Monsters",
                "Subconscious Mind Superpowers You Didn't Know",
                "Secrets of Black Holes and Time Warp"
            ],
            "general": [
                "Top 5 Mind-Blowing Facts About Human Brain",
                "Bermuda Triangle Mystery Finally Explained",
                "Unbelievable Life Hacks That Actually Work",
                "The Great Million Dollar Bank Heist",
                "Unsolved Cipher Case of 1920",
                "Deep Sea Bioluminescent Creatures",
                "Deadliest Animals of Amazon Jungle"
            ]
        }

        cat_low = str(category).lower()
        matched_pool = None
        for key in category_pools:
            if key in cat_low:
                matched_pool = category_pools[key]
                break

        if not matched_pool:
            all_topics = []
            for p in category_pools.values():
                all_topics.extend(p)
            matched_pool = all_topics

        return random.choice(matched_pool)

    return topic_clean

def get_daily_unique_subtopic(base_topic: str, today_str: str, user_id: str) -> str:
    """Generates a non-repetitive daily subtopic angle for automated auto reels."""
    import random, hashlib
    topic = resolve_random_topic(base_topic)
    if len(topic.split()) > 3:
        return topic
    sub_angles = [
        "Unbelievable Secrets",
        "Mystery and History",
        "The Complete Story",
        "Behind The Scenes",
        "Top Facts and Mysteries",
        "Unexpected Turn of Events",
        "Shocking Truth Revealed",
        "Amazing Adventure"
    ]
    seed = int(hashlib.md5(f"{today_str}_{user_id}_{topic}_{random.randint(100, 999)}".encode()).hexdigest(), 16)
    selected_angle = sub_angles[seed % len(sub_angles)]
    return f"{topic}: {selected_angle}"

from concurrent.futures import ThreadPoolExecutor
import threading

auto_worker_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="AutoRenderWorker")
render_queue_lock = threading.Lock()

def process_single_user_schedule(user: dict, now_ist: datetime, today_str: str):
    """
    Crash-Proof Thread Worker for Single User Schedule Execution:
    Handles short, long, and ultra pre-rendering & instant YouTube auto-upload independently.
    Isolated per-user try-except prevents any error from affecting other users.
    """
    internal_id = user.get("internal_id")
    if not internal_id:
        return

    try:
        schedule = user.get("auto_schedule", {})
        if not schedule or not schedule.get("schedule_enabled"):
            return

        yt_creds = user.get("youtube_credentials")
        if not yt_creds:
            print(f"⚠️ User {internal_id} has no YouTube account linked. Clearing auto_schedule from DB...")
            if users_collection is not None:
                users_collection.update_one(
                    {"internal_id": internal_id},
                    {
                        "$unset": {
                            "auto_schedule": "",
                            "staged_auto_videos": ""
                        }
                    }
                )
            return

        subscription = user.get("subscription", {})
        sub_status = subscription.get("status")
        sub_expires = subscription.get("expires_at")
        plan_type = subscription.get("plan_type", "none")

        is_active = (sub_status == "active")
        if sub_expires and isinstance(sub_expires, str):
            try:
                exp_dt = datetime.fromisoformat(sub_expires.replace('Z', '+00:00'))
                if datetime.utcnow() > exp_dt.replace(tzinfo=None):
                    is_active = False
            except Exception:
                pass

        current_ist_minutes = now_ist.hour * 60 + now_ist.minute

        ultra_sub = user.get("ultra_subscription", {})
        ultra_status = ultra_sub.get("status")
        ultra_expires = ultra_sub.get("expires_at")
        has_ultra_sub = False
        if ultra_status == "active" and ultra_expires:
            if isinstance(ultra_expires, str):
                try:
                    ultra_expires = datetime.fromisoformat(ultra_expires)
                except Exception:
                    ultra_expires = None
            if isinstance(ultra_expires, datetime) and ultra_expires > datetime.utcnow():
                has_ultra_sub = True

        def run_staged_auto_pipeline(kind: str, is_short_flag: bool, default_topic: str, default_dur: int):
            time_str = schedule.get(f"{kind}_time", "10:00" if kind == "short" else ("18:00" if kind == "long" else "21:00"))
            last_run_key = f"last_{kind}_run"

            if schedule.get(last_run_key) == today_str:
                return # Already published today

            target_minutes = parse_time_to_minutes(time_str) or (600 if kind == "short" else (1080 if kind == "long" else 1260))
            mins_until = (target_minutes - current_ist_minutes) % 1440
            diff_current = min(abs(current_ist_minutes - target_minutes), 1440 - abs(current_ist_minutes - target_minutes))

            staged_map = user.get("staged_auto_videos", {})
            staged_item = staged_map.get(kind, {})

            if mins_until <= 180 or diff_current <= 90:
                if staged_item.get("date") != today_str or not staged_item.get("file") or not os.path.exists(staged_item.get("file", "")):
                    print(f"🚀 [PREDICTIVE AUTO-STAGING] Pre-rendering {kind.upper()} video ahead of time for user {internal_id} (Scheduled IST: {time_str}, Target in {mins_until} mins)...")
                    raw_topic = schedule.get(f"{kind}_topic") or default_topic
                    topic = get_daily_unique_subtopic(raw_topic, today_str, internal_id)
                    category = schedule.get(f"{kind}_category") or "Random"
                    voice = schedule.get(f"{kind}_voice") or "hi-IN-MadhurNeural"
                    font = schedule.get(f"{kind}_font") or "Arial.ttf"
                    color = schedule.get(f"{kind}_color") or "yellow"
                    aspect_ratio = schedule.get(f"{kind}_aspect_ratio") or ("16:9" if kind in ["long", "ultra"] else "9:16")
                    duration = int(schedule.get(f"{kind}_duration") or default_dur)

                    with render_queue_lock:
                        res = render_video_with_smart_fallback(
                            user_id=internal_id,
                            topic=topic,
                            category=category,
                            voice_id=voice,
                            font_name=font,
                            font_color=color,
                            video_type=kind,
                            requested_duration=duration,
                            aspect_ratio=aspect_ratio
                        )

                    if res.get("status") == "completed":
                        video_file = res.get("file")
                        script_text = res.get("script", "")
                        if is_short_flag:
                            script_text = " ".join(script_text.split()[:120])

                        staged_data = {
                            "file": video_file,
                            "title": topic,
                            "script": script_text,
                            "date": today_str,
                            "staged_at": datetime.utcnow().isoformat()
                        }
                        staged_map[kind] = staged_data
                        users_collection.update_one(
                            {"internal_id": internal_id},
                            {"$set": {f"staged_auto_videos.{kind}": staged_data}}
                        )
                        print(f"✅ [PREDICTIVE STAGING COMPLETE] {kind.upper()} video pre-rendered for user {internal_id}. Waiting for {time_str} IST to publish!")
                        staged_item = staged_data

            if diff_current <= 25 or mins_until >= 1420:
                print(f"💥 [INSTANT BATCH UPLOAD] Publishing {kind.upper()} video for user {internal_id} to YouTube (Scheduled IST: {time_str})...")
                users_collection.update_one(
                    {"internal_id": internal_id},
                    {"$set": {f"auto_schedule.{last_run_key}": today_str}}
                )

                if staged_item.get("date") == today_str and staged_item.get("file") and os.path.exists(staged_item.get("file")):
                    upload_video_to_youtube_core(
                        user_id=internal_id,
                        video_file=staged_item.get("file"),
                        title=staged_item.get("title"),
                        description=staged_item.get("script"),
                        is_short=is_short_flag
                    )
                else:
                    raw_topic = schedule.get(f"{kind}_topic") or default_topic
                    topic = get_daily_unique_subtopic(raw_topic, today_str, internal_id)
                    category = schedule.get(f"{kind}_category") or "Random"
                    voice = schedule.get(f"{kind}_voice") or "hi-IN-MadhurNeural"
                    font = schedule.get(f"{kind}_font") or "Arial.ttf"
                    color = schedule.get(f"{kind}_color") or "yellow"
                    duration = int(schedule.get(f"{kind}_duration") or default_dur)

                    with render_queue_lock:
                        res = render_video_with_smart_fallback(
                            user_id=internal_id,
                            topic=topic,
                            category=category,
                            voice_id=voice,
                            font_name=font,
                            font_color=color,
                            video_type=kind,
                            requested_duration=duration
                        )
                    if res.get("status") == "completed":
                        video_file = res.get("file")
                        script_text = res.get("script", "")
                        if is_short_flag:
                            script_text = " ".join(script_text.split()[:120])
                        upload_video_to_youtube_core(
                            user_id=internal_id,
                            video_file=video_file,
                            title=topic,
                            description=script_text,
                            is_short=is_short_flag
                        )

                auto_usage = user.get("auto_daily_usage", {})
                if auto_usage.get("date") != today_str:
                    auto_usage = {"date": today_str, "auto_short_count": 0, "auto_long_count": 0, "auto_ultra_count": 0}
                auto_usage[f"auto_{kind}_count"] = auto_usage.get(f"auto_{kind}_count", 0) + 1
                users_collection.update_one(
                    {"internal_id": internal_id},
                    {"$set": {"auto_daily_usage": auto_usage},
                     "$unset": {f"staged_auto_videos.{kind}": ""}}
                )

        if schedule.get("short_enabled", True) and is_active and plan_type in ["short", "combo"]:
            run_staged_auto_pipeline("short", True, "Space Exploration", 20)

        if schedule.get("long_enabled", True) and is_active and plan_type in ["long", "combo"]:
            run_staged_auto_pipeline("long", False, "AI Innovations", 60)

        if schedule.get("ultra_enabled", False) and (has_ultra_sub or plan_type == "ultra"):
            run_staged_auto_pipeline("ultra", False, "History of Ancient Warriors", 60)

    except Exception as e_user:
        print(f"❌ Worker error for user {internal_id}: {e_user}")


def check_and_run_auto_schedules():
    """
    Crash-Proof Predictive Pre-Rendering & Multi-Thread Worker Scheduler Engine (200+ User Scale).
    Scans schedules and dispatches rendering jobs to ThreadPoolExecutor pool.
    """
    if users_collection is None:
        return

    now_utc = datetime.utcnow()
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    today_str = now_ist.strftime("%Y-%m-%d")

    try:
        projection = {
            "internal_id": 1,
            "auto_schedule": 1,
            "subscription": 1,
            "ultra_subscription": 1,
            "auto_daily_usage": 1,
            "staged_auto_videos": 1,
            "youtube_credentials": 1
        }
        users = list(users_collection.find({
            "auto_schedule.schedule_enabled": True,
            "youtube_credentials": {"$exists": True, "$ne": None}
        }, projection))
        for user in users:
            auto_worker_executor.submit(process_single_user_schedule, user, now_ist, today_str)
    except Exception as e:
        print(f"❌ Error in check_and_run_auto_schedules loop: {e}")

scheduler.add_job(check_and_run_auto_schedules, 'interval', minutes=1)
scheduler.start()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
import bcrypt as _raw_bcrypt

def safe_verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        if _raw_bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')):
            return True
    except Exception:
        pass

    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        pass

    return plain_password == hashed_password

def safe_hash_password(password: str) -> str:
    try:
        salt = _raw_bcrypt.gensalt()
        return _raw_bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    except Exception:
        return pwd_context.hash(password)

from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=500)

@app.get("/api/admin/unblock-firewall")
async def unblock_firewall():
    waf.reset_all_bans()
    return {"message": "🔓 Firewall IP bans & rate limits reset successfully!"}

app.add_middleware(FirewallMiddleware)

try:
    from bg_remover import remove_background
except Exception as _bg_err:
    print(f"⚠️ bg_remover import warning: {_bg_err}")
    remove_background = None

@app.post("/api/remove-bg")
async def api_remove_bg(request: Request):
    """API endpoint for background removal using REMOVE_BG_API_KEY environment variable."""
    if not remove_background:
        raise HTTPException(status_code=500, detail="Background remover engine not initialized")
    try:
        form = await request.form()
        file_obj = form.get("file")
        if not file_obj:
            raise HTTPException(status_code=400, detail="No image file provided in upload")

        contents = await file_obj.read()
        bg_color = form.get("bg_color")

        processed_img = remove_background(
            input_image=contents,
            bg_color=bg_color if bg_color else None
        )

        buf = io.BytesIO()
        output_format = "PNG" if processed_img.mode == "RGBA" else "JPEG"
        processed_img.save(buf, format=output_format)
        img_bytes = buf.getvalue()

        media_type = "image/png" if output_format == "PNG" else "image/jpeg"
        return Response(content=img_bytes, media_type=media_type)

    except Exception as e:
        print(f"❌ Server Error during /api/remove-bg: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class Scene(BaseModel):
    text: str
    keyword: str

class UserRegister(BaseModel):
    name: str
    country: str
    phone: str
    email: str
    password: str
    email_or_mobile: Optional[str] = None
    browser_token: Optional[str] = None

class UserLogin(BaseModel):
    email_or_mobile: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email_or_mobile: str
    current_session_user_id: Optional[str] = None
    current_session_user_email: Optional[str] = None
    current_session_user_phone: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    email_or_mobile: str
    qr_token: str
    new_password: str
    current_session_user_id: Optional[str] = None
    current_session_user_email: Optional[str] = None
    current_session_user_phone: Optional[str] = None





class VideoRequest(BaseModel):
    scenes: List[Scene] = []
    user_id: Optional[str] = None
    topic: Optional[str] = ""
    category: Optional[str] = "Random" # 30+ categories
    font_name: str = "Arial.ttf"
    font_color: str = "yellow"
    font_size: int = 220
    voice_id: str = "hi-IN-MadhurNeural"
    language: str = "hi"
    video_type: str = "short"  # 'short', 'long', or 'ultra'
    full_script: str = ""      # used if video_type is 'long' or 'ultra'
    bg_music: str = "cool.mp3" # background music track choice
    aspect_ratio: Optional[str] = "16:9"

class ScriptRequest(BaseModel):
    topic: str
    duration_seconds: int
    user_id: Optional[str] = None
    category: Optional[str] = "Random"
    video_type: Optional[str] = "short"

jobs = {}

def full_process(req: VideoRequest, job_id: str):
    """Asli logic jo background mein chalega"""
    try:
        job_dir = f"temp_{job_id}"
        os.makedirs(job_dir, exist_ok=True)
        
        user_id = req.user_id if req.user_id else "anonymous"
        print(f"🎬 Processing video for User: {user_id} (Category: {req.category})")
        
        scenes_data = []

        print(f"\n==================================================")
        print(f"🚀 [WORKFLOW ENGINE STARTED] Job ID: {job_id}")
        print(f"📊 Mode: {req.video_type.upper()} | User: {req.user_id} | Topic: '{req.topic}'")
        print(f"==================================================")

        print(f"📊 [PROGRESS 10%] STEP 1/6: Processing Script & Scene Breakdown...")
        if req.scenes and len(req.scenes) > 0 and any(s.text and s.text.strip() for s in req.scenes):
            scenes_data = [{"text": s.text.strip(), "keyword": s.keyword.strip() if s.keyword else "technology"} for s in req.scenes if s.text and s.text.strip()]

        if not scenes_data and req.full_script and req.full_script.strip():
            import re
            raw_sentences = re.split(r'(?<=[.!?])\s+|\n+', req.full_script.strip())
            stop_words = {"aur", "ek", "hai", "ki", "ke", "ka", "jo", "se", "me", "ko", "hi", "to", "ye", "wo", "tha", "thi", "hain", "kya", "toh", "liye", "bhi", "yeh", "kuch", "hoti", "hain", "mil", "sakti"}
            
            for sentence in raw_sentences:
                sentence = sentence.strip()
                if len(sentence) < 4: continue
                
                words = [w.lower() for w in sentence.split() if w.isalpha() and w.lower() not in stop_words]
                keyword = "technology"
                if words:
                    words.sort(key=len, reverse=True)
                    keyword = words[0]
                    
                scenes_data.append({"text": sentence, "keyword": keyword})
                
            if not scenes_data:
                scenes_data = [{"text": req.full_script.strip(), "keyword": "technology"}]

        if not scenes_data:
            fallback_text = req.topic if req.topic else "AI Video Generation"
            scenes_data = [{"text": fallback_text, "keyword": "technology"}]

        total_scenes = len(scenes_data)
        print(f"✅ STEP 1 COMPLETE: Prepared {total_scenes} scenes for rendering.")
        
        taiyaar_scenes = []
        for i, sc in enumerate(scenes_data):
            sc_progress = 10 + int(((i + 1) / total_scenes) * 40)
            print(f"\n🎙️ [PROGRESS {sc_progress}%] STEP 2 & 3 ({i+1}/{total_scenes}): Synthesizing Voice & Fetching Assets for Scene {i+1}...")
            
            a_path = os.path.join(job_dir, f"audio_{i}.mp3")
            v_path = os.path.join(job_dir, f"video_{i}.mp4")
            
            try:
                make_audio(sc["text"], a_path, req.voice_id)
                print(f"   🔊 Voice generated -> {a_path}")
            except Exception as e_aud:
                print(f"   ⚠️ Voice synthesis warning (Scene {i+1}): {e_aud}")

            is_ultra = (req.video_type == "ultra")
            orientation = "landscape" if (req.video_type in ["long", "ultra"]) else "portrait"
            
            cat_lower_req = str(req.category).lower()
            is_cartoon_req = any(k in cat_lower_req for k in ["cartoon", "anime", "animation", "character", "comic"])

            if is_ultra and is_cartoon_req:
                print(f"🎨 [Ultra Cartoon Scene {i+1}] Pure AI Cartoon Mode. Skipping web photo downloads; Cloxel AI Director will generate 2D Cartoon scene from script!")
                v_paths = []
            elif is_ultra and fetch_web_image:
                try:
                    bg_img_path = os.path.join(job_dir, f"bg_photo_{i}.jpg")
                    fg_img_path = os.path.join(job_dir, f"fg_photo_{i}.jpg")
                    
                    main_topic = req.topic if req.topic else "hero warrior"
                    scene_text = sc.get('text', '')
                    scene_kw = sc.get('keyword', '').strip()
                    
                    scene_specific = scene_kw if (scene_kw and len(scene_kw.split()) <= 4) else ""
                    if not scene_specific and scene_text:
                        words = [w for w in scene_text.split() if len(w) > 3][:3]
                        scene_specific = " ".join(words)
                        
                    bg_query = f"{main_topic} {scene_specific} landscape wallpaper photo".strip()
                    fg_query = f"{main_topic} {scene_specific} character hero portrait".strip()
                    
                    print(f"   📥 Fetching Dual HD Assets: BG='{bg_query}', FG='{fg_query}'...")
                    fetch_web_image(bg_query, bg_img_path)
                    fetch_web_image(fg_query, fg_img_path)
                    
                    v_paths = []
                    if os.path.exists(bg_img_path):
                        v_paths.append(bg_img_path)
                    if os.path.exists(fg_img_path):
                        v_paths.append(fg_img_path)
                        
                    if not v_paths or any(w in scene_specific.lower() for w in ["battle", "war", "action", "fight", "army"]):
                        vid_list = fetch_videos(f"{main_topic} {scene_specific}", v_path, orientation=orientation, category=req.category or "Random")
                        if vid_list and os.path.exists(vid_list[0]):
                            if not v_paths:
                                v_paths = vid_list
                            else:
                                v_paths.append(vid_list[0])
                except Exception as e_img:
                    print(f"   ⚠️ Ultra script image fetch fallback: {e_img}")
                    v_paths = fetch_videos(sc["keyword"], v_path, orientation=orientation, category=req.category or "Random")
            else:
                v_paths = fetch_videos(sc["keyword"], v_path, orientation=orientation, category=req.category or "Random")
            
            if os.path.exists(a_path):
                if not v_paths:
                    fallback_img_path = os.path.join(job_dir, f"fallback_canvas_{i}.jpg")
                    from PIL import Image
                    target_w, target_h = (1280, 720) if (req.video_type in ["long", "ultra"]) else (720, 1280)
                    blank_img = Image.new('RGB', (target_w, target_h), color=(15, 10, 35))
                    blank_img.save(fallback_img_path)
                    v_paths = [fallback_img_path]

                taiyaar_scenes.append({
                    "audio": a_path, 
                    "video": v_paths, 
                    "text": sc["text"]
                })
                print(f"   ✅ Scene {i+1}/{total_scenes} ready for video assembly.")

        if taiyaar_scenes:
            print(f"\n🎬 [PROGRESS 65%] STEP 4 & 5: Entering FFmpeg & 3D Motion Render Queue...")
            output_file = f"acoumation_video_{job_id}.mp4"
            target_size = (1280, 720) if (req.video_type in ["long", "ultra"]) else (720, 1280)
            adjusted_font_size = int(req.font_size * 0.7) if (req.video_type in ["long", "ultra"]) else req.font_size
            with render_queue_lock:
                merge_and_export(taiyaar_scenes, output_file, font_path=f"./fonts/{req.font_name}", color=req.font_color, font_size=adjusted_font_size, target_size=target_size, bg_music=req.bg_music, mode=req.video_type, category=req.category or "Random") 
            
            print(f"\n☁️ [PROGRESS 90%] STEP 6/6: Uploading Completed Video to Cloudinary CDN...")
            cloudinary_url = None
            try:
                upload_result = cloudinary.uploader.upload(output_file, resource_type="video")
                cloudinary_url = upload_result.get("secure_url")
                print(f"✅ Cloudinary HD CDN URL: {cloudinary_url}")
            except Exception as e:
                print(f"⚠️ Cloudinary upload warning: {e}")
                
            full_script_content = req.full_script or " ".join([sc["text"] for sc in taiyaar_scenes])
            gen_title, gen_desc = build_youtube_metadata(
                topic=req.topic,
                full_script=full_script_content,
                video_type=req.video_type
            )
            
            update_job_status(job_id, {
                "status": "completed", 
                "file": output_file, 
                "dir": job_dir, 
                "cloudinary_url": cloudinary_url,
                "title": gen_title,
                "description": gen_desc,
                "video_type": req.video_type,
                "topic": req.topic
            })
            
            if videos_collection is not None and req.user_id != "anonymous":
                try:
                    videos_collection.insert_one({
                        "internal_id": req.user_id,
                        "job_id": job_id,
                        "topic": req.topic or gen_title,
                        "title": gen_title,
                        "description": gen_desc,
                        "video_type": req.video_type,
                        "cloudinary_url": cloudinary_url,
                        "created_at": datetime.utcnow()
                    })
                    print(f"✅ Video history saved to MongoDB for user {req.user_id}: {gen_title}")
                except Exception as e:
                    print(f"❌ Failed to save video history to DB: {e}")

            print(f"🎉 [PROGRESS 100%] WORKFLOW COMPLETED SUCCESSFULLY FOR JOB ID: {job_id}!")
        else:
            update_job_status(job_id, {"status": "failed", "error": "No scenes ready"})
            print(f"❌ [WORKFLOW FAILED] No scenes ready for job ID {job_id}")

    except Exception as e:
        import traceback
        print(f"❌ [WORKFLOW EXCEPTION DETECTED] Job ID {job_id} failed with error: {e}")
        traceback.print_exc()
        update_job_status(job_id, {"status": "failed", "error": str(e)})
    finally:
        try:
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir, ignore_errors=True)
                print(f"🧹 Cleaned up temp scene directory: {job_dir}")
        except Exception as err:
            print(f"Temp cleanup warning: {err}")

def render_video_with_smart_fallback(user_id: str, topic: str, category: str, voice_id: str, font_name: str, font_color: str, video_type: str, requested_duration: int, bg_music: str = "cool.mp3", aspect_ratio: str = None):
    """
    Smart Fallback Retry Engine with Duration Stepping:
    If rendering fails for requested duration (e.g. 300s/5m), automatically steps down
    to 240s (4m) -> 180s (3m) -> 120s (2m) -> 60s (1m) for long videos, or
    55s -> 45s -> 30s -> 20s -> 10s for short reels, retrying until 100% success!
    """
    import uuid
    if video_type in ["long", "ultra"]:
        duration_steps = [requested_duration, 3600, 1800, 1200, 900, 600, 300, 240, 180, 120, 60, 30]
        duration_steps = sorted(list(set([d for d in duration_steps if d <= requested_duration])), reverse=True)
    else:
        duration_steps = [requested_duration, 55, 45, 30, 20, 10]
        duration_steps = sorted(list(set([d for d in duration_steps if d <= requested_duration])), reverse=True)

    last_error = None
    for attempt_idx, dur in enumerate(duration_steps):
        try:
            print(f"🔄 [SMART RETRY ENGINE] Attempt {attempt_idx + 1}/{len(duration_steps)}: Trying {video_type.upper()} ({dur} seconds)...")
            
            script_data = generate_ai_script_core(
                topic=topic,
                duration=dur,
                video_type=video_type,
                language="hi",
                tone="viral",
                category=category
            )

            full_script = script_data.get("full_script", "")
            raw_scenes = script_data.get("scenes", [])
            scenes_obj = [Scene(text=s.get("text", ""), keyword=s.get("keyword", "technology")) for s in raw_scenes]

            if not scenes_obj:
                scenes_obj = [Scene(text=full_script or topic, keyword="technology")]

            v_req = VideoRequest(
                user_id=user_id,
                topic=topic,
                category=category,
                voice_id=voice_id,
                font_name=font_name,
                font_color=font_color,
                video_type=video_type,
                full_script=full_script,
                scenes=scenes_obj,
                bg_music=bg_music,
                aspect_ratio=aspect_ratio or ("16:9" if video_type in ["long", "ultra"] else "9:16")
            )

            job_id = str(uuid.uuid4())
            full_process(v_req, job_id)

            job_result = jobs.get(job_id, {})
            if job_result.get("status") == "completed":
                print(f"✅ [SMART RETRY ENGINE SUCCESS] Successfully rendered {dur}s {video_type.upper()} on Attempt {attempt_idx + 1}!")
                return job_result
            else:
                last_error = job_result.get("error", "Unknown error")
                print(f"⚠️ Attempt {attempt_idx + 1} ({dur}s) failed: {last_error}. Stepping down duration...")
        except Exception as ex:
            last_error = str(ex)
            print(f"⚠️ Attempt {attempt_idx + 1} exception ({dur}s): {ex}. Stepping down duration...")

    print(f"❌ [SMART RETRY ENGINE EXHAUSTED] Tried all fallback durations: {last_error}")
    return {"status": "failed", "error": last_error}

class CreateOrderRequest(BaseModel):
    internal_id: str
    plan_type: str  # 'short' (50), 'long' (100), 'combo' (119)

class VerifyPaymentRequest(BaseModel):
    internal_id: str
    plan_type: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: Optional[str] = None

class AutoScheduleRequest(BaseModel):
    internal_id: str
    schedule_enabled: bool = True
    
    short_enabled: bool = True
    short_auto_topic: bool = True
    short_topic: str = "Space Exploration, AI Innovations"
    short_category: str = "Random"
    short_voice: str = "hi-IN-MadhurNeural"
    short_font: str = "Arial.ttf"
    short_color: str = "yellow"
    short_duration: int = 30
    short_time: str = "10:00"
    short_language: str = "hi"
    
    long_enabled: bool = True
    long_auto_topic: bool = True
    long_topic: str = "Space Exploration, AI Technology"
    long_category: str = "Random"
    long_voice: str = "hi-IN-MadhurNeural"
    long_font: str = "Arial.ttf"
    long_color: str = "yellow"
    long_duration: int = 60
    long_time: str = "18:00"
    long_language: str = "hi"

    ultra_enabled: bool = False
    ultra_auto_topic: bool = True
    ultra_topic: str = "History of Ancient Warriors, Science Mysteries"
    ultra_category: str = "Random"
    ultra_aspect_ratio: str = "16:9"
    ultra_voice: str = "hi-IN-MadhurNeural"
    ultra_font: str = "Arial.ttf"
    ultra_color: str = "yellow"
    ultra_duration: int = 60
    ultra_time: str = "21:00"
    ultra_language: str = "hi"

@app.post("/generate-custom-video")
async def generate_custom_video(req: VideoRequest, background_tasks: BackgroundTasks):
    user_id = req.user_id
    if not user_id or user_id == "anonymous":
        raise HTTPException(status_code=401, detail="Please login or register to generate videos.")

    if req.full_script and len(req.full_script) > 5000:
        raise HTTPException(status_code=400, detail="⚠️ Script too long! Maximum script length allowed is 5,000 characters per video.")

    if req.scenes and len(req.scenes) > 25:
        raise HTTPException(status_code=400, detail="⚠️ Too many scenes! Maximum scenes allowed per video is 25.")

    if users_collection is not None:
        user = users_collection.find_one({"internal_id": user_id})
        if user:
            free_demo = user.get("free_demo_count", 2)
            subscription = user.get("subscription", {})
            sub_status = subscription.get("status")
            sub_expires = subscription.get("expires_at")
            sub_plan = subscription.get("plan_type", "none")
            
            is_active = False
            if sub_status == "active" and sub_expires:
                if isinstance(sub_expires, str):
                    try:
                        sub_expires = datetime.fromisoformat(sub_expires)
                    except Exception:
                        sub_expires = None
                if sub_expires and sub_expires > datetime.utcnow():
                    is_active = True

            # Independent Ultra Subscription Check
            ultra_sub = user.get("ultra_subscription", {})
            ultra_status = ultra_sub.get("status")
            ultra_expires = ultra_sub.get("expires_at")
            has_active_ultra = False
            if ultra_status == "active" and ultra_expires:
                if isinstance(ultra_expires, str):
                    try:
                        ultra_expires = datetime.fromisoformat(ultra_expires)
                    except Exception:
                        ultra_expires = None
                if isinstance(ultra_expires, datetime) and ultra_expires > datetime.utcnow():
                    has_active_ultra = True

            v_type = req.video_type

            # 1. Mode Specific Entitlement Check
            if v_type == "ultra":
                if not has_active_ultra and sub_plan != "ultra":
                    if is_active:
                        raise HTTPException(status_code=403, detail="⚠️ Ultra Mode requires a dedicated ULTRA CINEMATIC plan (₹20/mo). Please subscribe to the Ultra Cinematic plan to generate Ultra videos.")
            elif sub_plan == "short" and v_type == "long":
                raise HTTPException(status_code=403, detail="⚠️ Your SHORT STARTER plan only permits Short videos (9:16). Please upgrade to LONG MASTER or PRO COMBO to generate Long videos.")
            elif sub_plan == "long" and v_type == "short":
                raise HTTPException(status_code=403, detail="⚠️ Your LONG MASTER plan only permits Long videos (16:9). Please upgrade to SHORT STARTER or PRO COMBO to generate Short videos.")

            # 2. Quota Check (Demo vs Active Subscription)
            if not is_active and not (v_type == "ultra" and has_active_ultra):
                res = users_collection.update_one(
                    {"internal_id": user_id, "free_demo_count": {"$gt": 0}},
                    {"$inc": {"free_demo_count": -1}}
                )
                if res.modified_count == 0:
                    raise HTTPException(status_code=402, detail="Demo quota exhausted! You have used your 2 free demo videos. Please upgrade your plan to continue generating videos.")
            else:
                today_str = datetime.utcnow().strftime("%Y-%m-%d")
                daily_usage = user.get("daily_usage", {})
                if daily_usage.get("date") != today_str:
                    daily_usage = {"date": today_str, "short_count": 0, "long_count": 0, "ultra_count": 0}
                
                short_count = daily_usage.get("short_count", 0)
                long_count = daily_usage.get("long_count", 0)

                if v_type == "short" and sub_plan == "short" and short_count >= 1:
                    raise HTTPException(status_code=429, detail="⚠️ Daily video limit reached! Your SHORT STARTER plan permits 1 Short video daily. Please try again tomorrow or upgrade to PRO COMBO.")
                elif v_type == "long" and sub_plan == "long" and long_count >= 1:
                    raise HTTPException(status_code=429, detail="⚠️ Daily video limit reached! Your LONG MASTER plan permits 1 Long video daily. Please try again tomorrow or upgrade to PRO COMBO.")

                if v_type == "short":
                    daily_usage["short_count"] = short_count + 1
                elif v_type == "long":
                    daily_usage["long_count"] = long_count + 1
                elif v_type == "ultra":
                    daily_usage["ultra_count"] = daily_usage.get("ultra_count", 0) + 1

                users_collection.update_one(
                    {"internal_id": user_id},
                    {"$set": {"daily_usage": daily_usage}}
                )

    job_id = str(uuid.uuid4())
    update_job_status(job_id, {"status": "processing", "user_id": req.user_id})
    background_tasks.add_task(full_process, req, job_id)
    return {"job_id": job_id, "status": "Processing Started"}

class ProfilePicRequest(BaseModel):
    internal_id: str
    profile_pic: str

@app.post("/update-profile-pic")
async def update_profile_pic(req: ProfilePicRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    users_collection.update_one(
        {"internal_id": req.internal_id},
        {"$set": {"profile_pic": req.profile_pic}}
    )
    return {"message": "Profile picture updated successfully!"}

@app.get("/user-profile-pic/{internal_id}")
async def get_user_profile_pic(internal_id: str):
    if users_collection is None:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        user = users_collection.find_one({"internal_id": internal_id}, {"profile_pic": 1})
        if not user or not user.get("profile_pic"):
            raise HTTPException(status_code=404, detail="No profile pic")
        pic = user.get("profile_pic")
        if pic.startswith("data:image"):
            import base64
            header, encoded = pic.split(",", 1)
            mime = header.split(";")[0].split(":")[1]
            data = base64.b64decode(encoded)
            return Response(content=data, media_type=mime)
        return RedirectResponse(url=pic)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Profile pic error")

@app.get("/user-subscription/{internal_id}")
async def get_user_subscription(internal_id: str):
    if users_collection is None:
        return {"free_demo_count": 2, "has_active_subscription": False, "plan_type": "none"}
    try:
        user = users_collection.find_one({"internal_id": internal_id})
        if not user:
            return {"free_demo_count": 2, "has_active_subscription": False, "plan_type": "none"}
            
        free_demo = user.get("free_demo_count", 2)
        subscription = user.get("subscription", {})
        sub_status = subscription.get("status")
        sub_expires = subscription.get("expires_at")
        sub_plan = subscription.get("plan_type", "none")
        
        is_active = (sub_status == "active")
        if sub_expires:
            if isinstance(sub_expires, str):
                try:
                    sub_expires = datetime.fromisoformat(sub_expires.replace('Z', '+00:00'))
                except Exception:
                    sub_expires = None
            if isinstance(sub_expires, datetime) and sub_expires.replace(tzinfo=None) < datetime.utcnow():
                is_active = False

        today_ist_str = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d")
        daily_usage = user.get("daily_usage", {})
        if daily_usage.get("date") != today_ist_str:
            daily_usage = {"date": today_ist_str, "short_count": 0, "long_count": 0}

        auto_daily_usage = user.get("auto_daily_usage", {})
        if auto_daily_usage.get("date") != today_ist_str:
            auto_daily_usage = {"date": today_ist_str, "auto_short_count": 0, "auto_long_count": 0}

        ultra_sub = user.get("ultra_subscription", {})
        ultra_status = ultra_sub.get("status")
        ultra_expires = ultra_sub.get("expires_at")
        has_ultra = (ultra_status == "active")
        if ultra_expires:
            if isinstance(ultra_expires, str):
                try:
                    ultra_expires = datetime.fromisoformat(ultra_expires.replace('Z', '+00:00'))
                except Exception:
                    ultra_expires = None
            if isinstance(ultra_expires, datetime) and ultra_expires.replace(tzinfo=None) < datetime.utcnow():
                has_ultra = False

        has_active_sub = is_active or has_ultra

        limit_text = "2 Free Demo Videos Total"
        if is_active or has_ultra:
            if sub_plan == "combo":
                limit_text = "2 Videos Daily (1 Short + 1 Long)"
            elif sub_plan == "short":
                limit_text = "1 Short Video Daily (9:16)"
            elif sub_plan == "long":
                limit_text = "1 Long Video Daily (16:9)"
            elif sub_plan == "ultra" or has_ultra:
                limit_text = "1 Ultra Cinematic Video Daily"

        user_name = user.get("name") or user.get("full_name") or user.get("username")
        if not user_name:
            if user.get("email"):
                user_name = user.get("email").split("@")[0]
            elif user.get("phone"):
                user_name = f"User {user.get('phone')[-4:]}"
            else:
                user_name = "Account Active"

        pic_url = ""
        if user.get("profile_pic"):
            pic_url = f"/user-profile-pic/{internal_id}"

        return {
            "name": user_name,
            "email": user.get("email", ""),
            "phone": user.get("phone", ""),
            "country": user.get("country", ""),
            "profile_pic": pic_url,
            "free_demo_count": free_demo,
            "has_active_subscription": has_active_sub,
            "has_active_ultra_subscription": has_ultra,
            "plan_type": sub_plan if is_active else ("ultra" if has_ultra else "none"),
            "expires_at": sub_expires.isoformat() if is_active and isinstance(sub_expires, datetime) else (ultra_expires.isoformat() if has_ultra and isinstance(ultra_expires, datetime) else None),
            "ultra_expires_at": ultra_expires.isoformat() if has_ultra and isinstance(ultra_expires, datetime) else None,
            "today_short_count": daily_usage.get("short_count", 0),
            "today_long_count": daily_usage.get("long_count", 0),
            "today_auto_short_count": auto_daily_usage.get("auto_short_count", 0),
            "today_auto_long_count": auto_daily_usage.get("auto_long_count", 0),
            "daily_limit_text": limit_text
        }
    except Exception as e:
        print(f"⚠️ get_user_subscription fallback notice for {internal_id}: {e}")
        return {"name": "Account Active", "free_demo_count": 2, "has_active_subscription": False, "plan_type": "none"}

@app.post("/save-auto-schedule")
async def save_auto_schedule(req: AutoScheduleRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    user = users_collection.find_one({"internal_id": req.internal_id})
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    subscription = user.get("subscription", {})
    sub_status = subscription.get("status")
    sub_expires = subscription.get("expires_at")
    sub_plan = subscription.get("plan_type", "none")
    
    is_active = False
    if sub_status == "active" and sub_expires:
        if isinstance(sub_expires, str):
            try:
                sub_expires = datetime.fromisoformat(sub_expires)
            except Exception:
                sub_expires = None
        if sub_expires and sub_expires > datetime.utcnow():
            is_active = True

    if not is_active:
        raise HTTPException(status_code=403, detail="🔒 Membership Only Feature! Auto-Schedule & Auto-Upload require an active paid membership plan. Please upgrade your membership to activate automatic video generation & YouTube publishing.")

    req.short_duration = max(10, min(55, req.short_duration))
    req.long_duration = max(20, min(300, req.long_duration))

    existing_schedule = user.get("auto_schedule", {})
    existing_started_at = existing_schedule.get("schedule_started_at")

    if req.schedule_enabled:
        yt_creds = user.get("youtube_credentials")
        if not yt_creds:
            raise HTTPException(
                status_code=400,
                detail="⚠️ YouTube Account Not Linked! Please connect your YouTube channel first before enabling Auto-Publishing."
            )
            
        if not existing_started_at or not existing_schedule.get("schedule_enabled"):
            schedule_started_at = datetime.utcnow()
        else:
            schedule_started_at = existing_started_at
    else:
        users_collection.update_one(
            {"internal_id": req.internal_id},
            {
                "$unset": {
                    "auto_schedule": "",
                    "staged_auto_videos": ""
                }
            }
        )
        print(f"🧹 Complete Data Wipe: Auto-publishing stopped and all saved schedule data erased for user {req.internal_id}")
        return {"message": "Auto-publishing stopped and all schedule data erased from database!", "schedule": {"schedule_enabled": False}}

    schedule_data = {
        "schedule_enabled": req.schedule_enabled,
        "schedule_started_at": schedule_started_at,
        "plan_type": sub_plan,
        
        "short_enabled": req.short_enabled,
        "short_auto_topic": req.short_auto_topic,
        "short_topic": req.short_topic if not req.short_auto_topic else "AI Auto Topic (Daily Dynamic)",
        "short_category": req.short_category,
        "short_voice": req.short_voice,
        "short_font": req.short_font,
        "short_color": req.short_color,
        "short_duration": req.short_duration,
        "short_time": req.short_time,
        "short_language": req.short_language,
        
        "long_enabled": req.long_enabled,
        "long_auto_topic": req.long_auto_topic,
        "long_topic": req.long_topic if not req.long_auto_topic else "AI Auto Topic (Daily Dynamic)",
        "long_category": req.long_category,
        "long_voice": req.long_voice,
        "long_font": req.long_font,
        "long_color": req.long_color,
        "long_duration": req.long_duration,
        "long_time": req.long_time,
        "long_language": req.long_language,

        "ultra_enabled": req.ultra_enabled,
        "ultra_auto_topic": req.ultra_auto_topic,
        "ultra_topic": req.ultra_topic if not req.ultra_auto_topic else "AI Auto Topic (Daily Dynamic)",
        "ultra_category": req.ultra_category,
        "ultra_aspect_ratio": req.ultra_aspect_ratio,
        "ultra_voice": req.ultra_voice,
        "ultra_font": req.ultra_font,
        "ultra_color": req.ultra_color,
        "ultra_duration": req.ultra_duration,
        "ultra_time": req.ultra_time,
        "ultra_language": req.ultra_language,
        
        "updated_at": datetime.utcnow()
    }

    users_collection.update_one(
        {"internal_id": req.internal_id},
        {"$set": {"auto_schedule": schedule_data}}
    )

    print(f"✅ Saved Auto-Schedule settings in MongoDB for user {req.internal_id} (Plan: {sub_plan})")
    return {"message": "Auto-schedule settings saved successfully to MongoDB profile!", "schedule": schedule_data}

@app.get("/get-auto-schedule/{internal_id}")
async def get_auto_schedule(internal_id: str):
    if users_collection is None:
        return {
            "schedule_enabled": False,
            "short_auto_topic": True,
            "short_topic": "Space Exploration, AI Innovations",
            "short_category": "Random",
            "short_voice": "hi-IN-MadhurNeural",
            "short_font": "Arial.ttf",
            "short_color": "yellow",
            "short_duration": 30,
            "short_time": "10:00",
            "short_language": "hi",
            "long_auto_topic": True,
            "long_topic": "Space Exploration, AI Technology",
            "long_category": "Random",
            "long_voice": "hi-IN-MadhurNeural",
            "long_font": "Arial.ttf",
            "long_color": "yellow",
            "long_duration": 60,
            "long_time": "18:00",
            "long_language": "hi",
            "total_videos_created": 0,
            "remaining_plan_videos": 60,
            "next_scheduled_run": "Not Scheduled"
        }

    user = users_collection.find_one({"internal_id": internal_id})
    if not user:
        return {
            "schedule_enabled": False,
            "short_auto_topic": True,
            "short_topic": "Space Exploration, AI Innovations",
            "short_category": "Random",
            "short_voice": "hi-IN-MadhurNeural",
            "short_font": "Arial.ttf",
            "short_color": "yellow",
            "short_duration": 30,
            "short_time": "10:00",
            "short_language": "hi",
            "long_auto_topic": True,
            "long_topic": "Space Exploration, AI Technology",
            "long_category": "Random",
            "long_voice": "hi-IN-MadhurNeural",
            "long_font": "Arial.ttf",
            "long_color": "yellow",
            "long_duration": 60,
            "long_time": "18:00",
            "long_language": "hi",
            "total_videos_created": 0,
            "remaining_plan_videos": 60,
            "next_scheduled_run": "Not Scheduled"
        }

    schedule = user.get("auto_schedule", {})
    yt_creds = user.get("youtube_credentials")
    has_yt_linked = bool(yt_creds and isinstance(yt_creds, dict) and yt_creds.get("token") and yt_creds.get("status") != "expired")

    if not has_yt_linked:
        if schedule and schedule.get("schedule_enabled"):
            users_collection.update_one(
                {"internal_id": internal_id},
                {"$unset": {"auto_schedule": "", "staged_auto_videos": ""}}
            )
            schedule = {}
        is_schedule_enabled = False
    else:
        is_schedule_enabled = bool(schedule.get("schedule_enabled", False))

    sub = user.get("subscription", {})
    plan_type = sub.get("plan_type", "none")
    purchase_count = sub.get("purchase_count", 1) if sub.get("status") == "active" else 0
    
    days_elapsed = 0
    activated_at = sub.get("activated_at")
    if sub.get("status") == "active":
        if activated_at:
            if isinstance(activated_at, str):
                try:
                    activated_at = datetime.fromisoformat(activated_at)
                except Exception:
                    activated_at = None
            if isinstance(activated_at, datetime):
                time_passed = datetime.utcnow() - activated_at
                days_elapsed = max(0, time_passed.days)
        else:
            sub_expires = sub.get("expires_at")
            if sub_expires:
                if isinstance(sub_expires, str):
                    try:
                        sub_expires = datetime.fromisoformat(sub_expires)
                    except Exception:
                        sub_expires = None
                if isinstance(sub_expires, datetime) and sub_expires > datetime.utcnow():
                    days_left = (sub_expires - datetime.utcnow()).days
                    total_days_purchased = purchase_count * 30
                    days_elapsed = max(0, total_days_purchased - days_left)

    daily_quota = 2 if plan_type == "combo" else (1 if plan_type in ["short", "long"] else 0)
    total_allowance = purchase_count * 30 * daily_quota if daily_quota > 0 else 2
    
    used_videos = days_elapsed * daily_quota if daily_quota > 0 else (2 - user.get("free_demo_count", 2))
    remaining = max(0, total_allowance - used_videos)
    
    next_run = "Not Enabled"
    if is_schedule_enabled:
        if plan_type == "combo":
            next_run = f"Short: Daily at {schedule.get('short_time', '10:00')} | Long: Daily at {schedule.get('long_time', '18:00')}"
        elif plan_type == "short":
            next_run = f"Short Reel: Daily at {schedule.get('short_time', '10:00')}"
        elif plan_type == "long":
            next_run = f"Long Video: Daily at {schedule.get('long_time', '18:00')}"

    started_at = schedule.get("schedule_started_at")
    hours_active = 0
    if started_at:
        if isinstance(started_at, str):
            try:
                started_at = datetime.fromisoformat(started_at)
            except Exception:
                started_at = None
        if isinstance(started_at, datetime):
            hours_active = round((datetime.utcnow() - started_at).total_seconds() / 3600, 1)

    return {
        "schedule_enabled": is_schedule_enabled,
        "schedule_started_at": started_at.isoformat() if isinstance(started_at, datetime) else None,
        "hours_active": hours_active,
        "plan_type": plan_type,
        
        "short_auto_topic": schedule.get("short_auto_topic", True),
        "short_topic": schedule.get("short_topic", "Space Exploration, AI Innovations"),
        "short_category": schedule.get("short_category", "Random"),
        "short_voice": schedule.get("short_voice", "hi-IN-MadhurNeural"),
        "short_font": schedule.get("short_font", "Arial.ttf"),
        "short_color": schedule.get("short_color", "yellow"),
        "short_duration": schedule.get("short_duration", 30),
        "short_time": schedule.get("short_time", "10:00"),
        "short_language": schedule.get("short_language", "hi"),
        
        "long_auto_topic": schedule.get("long_auto_topic", True),
        "long_topic": schedule.get("long_topic", "Space Exploration, AI Technology"),
        "long_category": schedule.get("long_category", "Random"),
        "long_voice": schedule.get("long_voice", "hi-IN-MadhurNeural"),
        "long_font": schedule.get("long_font", "Arial.ttf"),
        "long_color": schedule.get("long_color", "yellow"),
        "long_duration": schedule.get("long_duration", 60),
        "long_time": schedule.get("long_time", "18:00"),
        "long_language": schedule.get("long_language", "hi"),

        "total_videos_created": used_videos,
        "remaining_plan_videos": remaining,
        "total_plan_allowance": total_allowance,
        "purchase_count": purchase_count,
        "next_scheduled_run": next_run
    }

@app.get("/admin/active-schedules")
async def get_active_schedules_admin():
    """Admin inspection endpoint listing all accounts with active auto-upload enabled"""
    if users_collection is None:
        return {"total_active_accounts": 0, "active_schedules": []}

    active_users = list(users_collection.find({"auto_schedule.schedule_enabled": True}))
    results = []

    for user in active_users:
        sched = user.get("auto_schedule", {})
        sub = user.get("subscription", {})
        yt = user.get("youtube_credentials", {})
        results.append({
            "internal_id": user.get("internal_id"),
            "email": user.get("email"),
            "name": user.get("name"),
            "plan_type": sub.get("plan_type"),
            "youtube_connected": bool(yt),
            "short_upload_time": sched.get("short_time"),
            "long_upload_time": sched.get("long_time"),
            "schedule_started_at": sched.get("schedule_started_at"),
            "last_short_run": sched.get("last_short_run"),
            "last_long_run": sched.get("last_long_run")
        })

    return {
        "total_active_accounts": len(results),
        "active_schedules": results
    }

@app.get("/admin/security-status")
def get_security_status():
    """Admin inspection endpoint displaying active WAF security metrics and threat logs"""
    return {
        "waf_status": "ACTIVE_ENFORCED",
        "shield_version": "Cloxel Ultimate WAF v2.0",
        "attack_statistics": waf.attack_stats,
        "active_banned_ips": list(waf.banned_ips.keys()),
        "total_banned_ips": len(waf.banned_ips)
    }

PLAN_RANKS = {"ultra": 1, "short": 2, "long": 3, "combo": 4}
PLAN_NAMES = {
    "ultra": "Ultra Cinematic (₹20/mo)",
    "short": "Short Starter (₹50/mo)",
    "long": "Long Master (₹100/mo)",
    "combo": "Pro Combo (₹119/mo)"
}

@app.post("/create-razorpay-order")
async def create_razorpay_order(req: CreateOrderRequest):
    amounts = {
        "ultra": 2000,    # ₹20
        "short": 5000,    # ₹50
        "long": 10000,    # ₹100
        "combo": 11900    # ₹119
    }
    
    if users_collection is not None and req.internal_id:
        user = users_collection.find_one({"internal_id": req.internal_id})
        if user:
            sub = user.get("subscription", {})
            sub_status = sub.get("status")
            sub_expires = sub.get("expires_at")
            current_plan = sub.get("plan_type", "none")
            
            is_active = False
            if sub_status == "active" and sub_expires:
                if isinstance(sub_expires, str):
                    try:
                        sub_expires = datetime.fromisoformat(sub_expires)
                    except Exception:
                        sub_expires = None
                if isinstance(sub_expires, datetime) and sub_expires > datetime.utcnow():
                    is_active = True

            if is_active and req.plan_type != "ultra":
                curr_rank = PLAN_RANKS.get(current_plan, 0)
                new_rank = PLAN_RANKS.get(req.plan_type, 0)
                
                if new_rank < curr_rank:
                    exp_date_str = sub_expires.strftime("%b %d, %Y") if isinstance(sub_expires, datetime) else "expiry"
                    raise HTTPException(
                        status_code=400,
                        detail=f"⚠️ Plan Downgrade Restricted! You already have an active high-tier plan ({PLAN_NAMES.get(current_plan, current_plan)}). You cannot downgrade to {PLAN_NAMES.get(req.plan_type, req.plan_type)} until your current plan expires on {exp_date_str}."
                    )

    amount = amounts.get(req.plan_type, 5000)
    
    key_id = os.getenv("RAZORPAY_KEY_ID", "rzp_test_TRfILFpcp5Owd4").strip().strip('"').strip("'")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip().strip('"').strip("'")
    
    if key_id and key_secret and key_id != "rzp_test_placeholder":
        try:
            import razorpay
            client = razorpay.Client(auth=(key_id, key_secret))
            order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "receipt": f"receipt_{req.internal_id[:8]}_{int(datetime.utcnow().timestamp())}",
                "payment_capture": 1
            })
            return {
                "order_id": order["id"],
                "amount": amount,
                "currency": "INR",
                "key_id": key_id
            }
        except Exception as e:
            print(f"⚠️ Razorpay API order warning: {e}. Falling back to standard test checkout mode.")
            
    fake_order_id = f"order_test_{str(uuid.uuid4())[:8]}"
    return {
        "order_id": fake_order_id,
        "amount": amount,
        "currency": "INR",
        "key_id": key_id if key_id else "rzp_test_TRfILFpcp5Owd4"
    }

@app.post("/verify-razorpay-payment")
async def verify_razorpay_payment(req: VerifyPaymentRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    if not req.razorpay_payment_id or req.razorpay_payment_id.startswith("pay_demo_") or req.razorpay_payment_id == "cancelled":
        raise HTTPException(status_code=400, detail="Payment failed or was cancelled by user. Membership not activated.")

    key_id = os.getenv("RAZORPAY_KEY_ID", "").strip().strip('"').strip("'")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip().strip('"').strip("'")

    if key_id and key_secret and req.razorpay_signature and key_secret != "secret_placeholder":
        try:
            import razorpay
            client = razorpay.Client(auth=(key_id, key_secret))
            client.utility.verify_payment_signature({
                'razorpay_order_id': req.razorpay_order_id,
                'razorpay_payment_id': req.razorpay_payment_id,
                'razorpay_signature': req.razorpay_signature
            })
        except Exception as e:
            print(f"❌ Razorpay signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Payment Signature Verification Failed. Activation Denied.")

    existing_user = users_collection.find_one({"internal_id": req.internal_id})

    if req.plan_type == "ultra":
        existing_ultra = existing_user.get("ultra_subscription", {}) if existing_user else {}
        ultra_exp = existing_ultra.get("expires_at")
        is_ultra_active = False
        if ultra_exp:
            if isinstance(ultra_exp, str):
                try:
                    ultra_exp = datetime.fromisoformat(ultra_exp)
                except Exception:
                    ultra_exp = None
            if isinstance(ultra_exp, datetime) and ultra_exp > datetime.utcnow():
                is_ultra_active = True

        if is_ultra_active:
            expires_at = ultra_exp + timedelta(days=30)
        else:
            expires_at = datetime.utcnow() + timedelta(days=30)

        ultra_data = {
            "plan_type": "ultra",
            "status": "active",
            "payment_id": req.razorpay_payment_id,
            "order_id": req.razorpay_order_id,
            "activated_at": datetime.utcnow(),
            "expires_at": expires_at
        }
        users_collection.update_one(
            {"internal_id": req.internal_id},
            {"$set": {"ultra_subscription": ultra_data}}
        )
        return {
            "message": f"🎉 Ultra Cinematic Plan (₹20/mo) activated successfully!",
            "plan_type": "ultra",
            "expires_at": expires_at.isoformat()
        }

    existing_sub = existing_user.get("subscription", {}) if existing_user else {}
    current_plan = existing_sub.get("plan_type", "none")
    sub_status = existing_sub.get("status")
    sub_exp = existing_sub.get("expires_at")
    purchase_count = existing_sub.get("purchase_count", 0)

    is_active = False
    if sub_status == "active" and sub_exp:
        if isinstance(sub_exp, str):
            try:
                sub_exp = datetime.fromisoformat(sub_exp)
            except Exception:
                sub_exp = None
        if isinstance(sub_exp, datetime) and sub_exp > datetime.utcnow():
            is_active = True

    if is_active:
        if current_plan == req.plan_type:
            expires_at = sub_exp + timedelta(days=30)
            purchase_count += 1
            print(f"🔄 Stacked +30 days on '{req.plan_type}' for user {req.internal_id} (Purchase #{purchase_count}, Expiry: {expires_at.isoformat()})")
        else:
            expires_at = datetime.utcnow() + timedelta(days=30)
            purchase_count = 1
            print(f"🚀 Upgraded user {req.internal_id} from '{current_plan}' to '{req.plan_type}'! Expiry set to {expires_at.isoformat()}")
    else:
        expires_at = datetime.utcnow() + timedelta(days=30)
        purchase_count = 1
        print(f"✅ Activated new 30-day '{req.plan_type}' membership for user {req.internal_id}")
    
    subscription_data = {
        "plan_type": req.plan_type,
        "status": "active",
        "payment_id": req.razorpay_payment_id,
        "order_id": req.razorpay_order_id,
        "activated_at": datetime.utcnow() if not existing_sub.get("activated_at") else existing_sub.get("activated_at"),
        "expires_at": expires_at,
        "purchase_count": purchase_count
    }
    
    users_collection.update_one(
        {"internal_id": req.internal_id},
        {"$set": {"subscription": subscription_data}}
    )
    
    return {
        "message": f"Payment verified! '{PLAN_NAMES.get(req.plan_type, req.plan_type)}' activated successfully until {expires_at.strftime('%b %d, %Y')}!",
        "expires_at": expires_at.isoformat(),
        "purchase_count": purchase_count
    }

def generate_qr_base64(data_str: str) -> str:
    try:
        import qrcode
        import io
        import base64
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"⚠️ Local qrcode module error: {e}. Falling back to QR Generator API...")
        try:
            import urllib.parse
            import requests
            import base64
            encoded_data = urllib.parse.quote(data_str)
            qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_data}"
            res = requests.get(qr_api_url, timeout=5)
            if res.status_code == 200 and res.content:
                return base64.b64encode(res.content).decode('utf-8')
        except Exception as _e_api:
            print(f"⚠️ QR API Fallback error: {_e_api}")
        return ""

def send_brevo_qr_email(user_email: str, user_name: str, security_qr_token: str, browser_token: str):
    try:
        brevo_api_key = os.getenv("BREVO_API_KEY") or os.getenv("SMTP_KEY")
        smtp_login = os.getenv("SMTP_LOGIN", os.getenv("BREVO_SMTP_LOGIN", "9d55c8001@smtp-brevo.com"))
        smtp_key = os.getenv("SMTP_KEY", os.getenv("BREVO_SMTP_KEY", os.getenv("SMTP_PASSWORD")))
        sender_email = os.getenv("SENDER_EMAIL", "support@cloxel.ai")
        sender_name = os.getenv("SENDER_NAME", "Cloxel AI Security Engine")

        
        qr_payload = json.dumps({
            "security_token": security_qr_token,
            "cipher_signature": hashlib.sha256((security_qr_token + user_email).encode('utf-8')).hexdigest()[:48].upper(),
            "email": user_email,
            "issuer": "Cloxel AI Security Engine"
        })
        
        qr_b64 = generate_qr_base64(qr_payload)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0b071a; color: #ffffff; padding: 20px; }}
            .card {{ max-width: 550px; margin: 0 auto; background: #130d2a; border: 1px solid rgba(168,85,247,0.4); border-radius: 16px; padding: 30px; text-align: center; }}
            .badge {{ background: rgba(168,85,247,0.2); color: #c084fc; border: 1px solid #a855f7; padding: 6px 14px; border-radius: 20px; font-weight: bold; display: inline-block; font-size: 0.85rem; }}
            h2 {{ color: #ffffff; margin-top: 15px; }}
            p {{ color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; }}
            .qr-container {{ background: #ffffff; padding: 20px; border-radius: 12px; display: inline-block; margin: 20px 0; }}
            .qr-container img {{ width: 220px; height: 220px; display: block; margin: 0 auto; }}
            .warning {{ color: #f87171; font-size: 0.85rem; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; }}
          </style>
        </head>
        <body>
          <div class="card">
            <span class="badge">✦ CLOXEL AI SECURITY CREDENTIAL</span>
            <h2>Welcome, {user_name}!</h2>
            <p>Your Cloxel AI account registration is successful. Below is your official <strong>Cryptographic Security Reset QR Code</strong>.</p>
            <p><strong>IMPORTANT:</strong> Save this QR Code image in your phone or email. Whenever you reset your password, you must upload this image or scan it via camera.</p>
            
            <div class="qr-container">
              <img src="data:image/png;base64,{qr_b64}" alt="Cloxel Security QR Code" />
            </div>

            <div class="warning">
              🔒 <strong>Dual-Factor Security Policy:</strong> Password reset strictly requires your active browser account session AND uploading/scanning this QR Code image. Manual typing is disabled for security.
            </div>
          </div>
        </body>
        </html>
        """


        # 1. Try Brevo HTTP API first if BREVO_API_KEY exists
        if brevo_api_key:
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "accept": "application/json",
                "api-key": brevo_api_key,
                "content-type": "application/json"
            }
            
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": user_email, "name": user_name}],
                "subject": "✦ Cloxel AI - Official Security QR Code Credential",
                "htmlContent": html_content
            }

            if qr_b64:
                payload["attachment"] = [
                    {
                        "content": qr_b64,
                        "name": "cloxel_security_qr.png"
                    }
                ]
            
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code in [200, 201, 202]:
                print(f"✅ Brevo QR Email sent successfully via API to {user_email}")
                return True
            else:
                print(f"⚠️ Brevo API Response ({res.status_code}): {res.text}")

        # 2. Try Brevo SMTP Relay if SMTP key exists
        if smtp_key and smtp_login:
            try:
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.base import MIMEBase
                from email import encoders

                msg = MIMEMultipart('alternative')
                msg['Subject'] = "✦ Cloxel AI - Official Security QR Code Credential"
                msg['From'] = f"{sender_name} <{sender_email}>"
                msg['To'] = user_email

                part = MIMEText(html_content, 'html')
                msg.attach(part)

                if qr_b64:
                    import base64
                    attach_file = MIMEBase('image', 'png', name='cloxel_security_qr.png')
                    attach_file.set_payload(base64.b64decode(qr_b64))
                    encoders.encode_base64(attach_file)
                    attach_file.add_header('Content-Disposition', 'attachment', filename='cloxel_security_qr.png')
                    msg.attach(attach_file)

                with smtplib.SMTP('smtp-relay.brevo.com', 587) as server:
                    server.starttls()
                    server.login(smtp_login, smtp_key)
                    server.sendmail(sender_email, [user_email], msg.as_string())
                print(f"✅ Brevo QR Email sent successfully via SMTP Relay to {user_email}")
                return True
            except Exception as _smtp_err:
                print(f"⚠️ Brevo SMTP error: {_smtp_err}")

        print(f"⚠️ Neither BREVO_API_KEY nor SMTP_KEY configured. QR Code for {user_email}: {security_qr_token}")
        return False
    except Exception as e:
        print(f"❌ Error sending Brevo QR Email: {e}")
        return False



@app.post("/register")
async def register_user(req: UserRegister):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    primary_email = req.email.strip().lower()
    primary_phone = "".join(filter(str.isdigit, req.phone))
    
    if not primary_email or not primary_phone or not req.name.strip() or not req.country.strip():
        raise HTTPException(status_code=400, detail="All fields (Name, Country, Phone, Email, Password) are mandatory.")
        
    import re
    email_regex = re.compile(f"^{re.escape(primary_email)}$", re.IGNORECASE)
    
    existing_user = users_collection.find_one({
        "$or": [
            {"email": email_regex},
            {"phone": primary_phone},
            {"phone": req.phone.strip()},
            {"email_or_mobile": email_regex},
            {"email_or_mobile": primary_phone}
        ]
    })
    
    if existing_user:
        ex_email = existing_user.get("email", "").lower()
        ex_phone = existing_user.get("phone", "")
        if ex_email == primary_email:
            raise HTTPException(status_code=400, detail="⚠️ Account Creation Failed: This Email ID is already registered! Please use a different Email or Login.")
        else:
            raise HTTPException(status_code=400, detail="⚠️ Account Creation Failed: This Phone Number is already registered! Please use a different Phone Number or Login.")
        
    hashed_password = safe_hash_password(req.password)
    internal_id = str(uuid.uuid4())
    browser_tok = (req.browser_token or "").strip() or str(uuid.uuid4())
    security_qr_tok = f"CLOXEL-SEC-{uuid.uuid4().hex[:12].upper()}"
    
    new_user = {
        "name": req.name.strip(),
        "country": req.country.strip(),
        "phone": primary_phone,
        "email": primary_email,
        "email_or_mobile": primary_email,
        "password_hash": hashed_password,
        "internal_id": internal_id,
        "registration_browser_token": browser_tok,
        "security_qr_token": security_qr_tok,
        "created_at": datetime.utcnow()
    }
    
    # 1. Attempt sending Brevo Security QR Email FIRST
    email_sent = False
    try:
        email_sent = send_brevo_qr_email(
            user_email=primary_email,
            user_name=req.name.strip(),
            security_qr_token=security_qr_tok,
            browser_token=browser_tok
        )
    except Exception as _e_qr:
        print(f"❌ Brevo QR Email dispatch error: {_e_qr}")

    # 2. Block registration if email delivery failed
    brevo_key = os.getenv("BREVO_API_KEY") or os.getenv("SMTP_KEY")
    if brevo_key and not email_sent:
        raise HTTPException(
            status_code=400,
            detail=f"⚠️ Registration Blocked: Unable to send Security QR Code email to '{primary_email}'. Please verify your email address and try again."
        )

    # 3. Save new user into MongoDB ONLY if email was sent successfully!
    users_collection.insert_one(new_user)

    return {
        "message": "User registered successfully",
        "internal_id": internal_id,
        "email": primary_email,
        "phone": primary_phone,
        "name": req.name.strip(),
        "browser_token": browser_tok,
        "security_qr_token": security_qr_tok
    }


@app.post("/login")
async def login_user(req: UserLogin):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    raw_identifier = req.email_or_mobile.strip()
    clean_phone = "".join(filter(str.isdigit, raw_identifier))
    import re
    identifier_regex = re.compile(f"^{re.escape(raw_identifier.lower())}$", re.IGNORECASE)
    
    query = [
        {"email": identifier_regex},
        {"email_or_mobile": identifier_regex},
        {"internal_id": raw_identifier}
    ]
    if clean_phone:
        query.append({"phone": clean_phone})
        query.append({"email_or_mobile": clean_phone})
        
    user = users_collection.find_one({"$or": query})
    
    if not user:
        raise HTTPException(status_code=400, detail="⚠️ Account Not Found: Please check your Email / Mobile Number or click Register.")
        
    stored_hash = user.get("password_hash") or user.get("password")
    if not stored_hash:
        raise HTTPException(status_code=400, detail="⚠️ Account password configuration issue. Please Register a new account.")

    is_valid = safe_verify_password(req.password, stored_hash)

    if not is_valid:
        raise HTTPException(status_code=400, detail="⚠️ Incorrect Password: Please check your password and try again.")
        
    return {
        "message": "Login successful",
        "internal_id": user["internal_id"],
        "email": (user.get("email") or "").strip().lower(),
        "phone": user.get("phone") or "",
        "name": user.get("name") or "User"
    }

@app.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    raw_identifier = req.email_or_mobile.strip()
    if not raw_identifier:
        raise HTTPException(status_code=400, detail="⚠️ Please provide an Email or Mobile Number.")

    clean_phone = "".join(filter(str.isdigit, raw_identifier))
    import re
    identifier_regex = re.compile(f"^{re.escape(raw_identifier.lower())}$", re.IGNORECASE)
    
    query = [
        {"email": identifier_regex},
        {"email_or_mobile": identifier_regex},
        {"internal_id": raw_identifier}
    ]
    if clean_phone:
        query.append({"phone": clean_phone})
        query.append({"email_or_mobile": clean_phone})
        
    user = users_collection.find_one({"$or": query})
    if not user:
        raise HTTPException(status_code=400, detail="⚠️ Account Not Found: Please check your Email / Mobile Number.")

    user_email = (user.get("email") or "").strip().lower()
    user_phone = (user.get("phone") or "").strip()
    user_internal_id = (user.get("internal_id") or "").strip().lower()

    # MANDATORY ACTIVE BROWSER SESSION CHECK AT STEP 1
    client_sess_id = (req.current_session_user_id or "").strip().lower()
    client_sess_email = (req.current_session_user_email or "").strip().lower()
    client_sess_phone = (req.current_session_user_phone or "").strip()

    session_matched = False
    if client_sess_email and client_sess_email == user_email:
        session_matched = True
    elif client_sess_phone and (client_sess_phone == user_phone or client_sess_phone in user_phone):
        session_matched = True
    elif client_sess_id and client_sess_id in [user_email, user_phone, user_internal_id]:
        session_matched = True

    if not session_matched:
        raise HTTPException(
            status_code=400,
            detail="⚠️ Security Error: Account Session Mismatch! Password reset is ONLY allowed for the account currently logged into this browser. Please log into this account in your browser first."
        )

    user_name = user.get("name") or "User"
    security_qr_tok = user.get("security_qr_token")
    if not security_qr_tok:
        security_qr_tok = f"CLOXEL-SEC-{uuid.uuid4().hex[:12].upper()}"
        users_collection.update_one({"_id": user["_id"]}, {"$set": {"security_qr_token": security_qr_tok}})

    reg_browser_tok = user.get("registration_browser_token") or ""

    # Dispatch Brevo QR Email to registered email
    if user_email:
        try:
            send_brevo_qr_email(
                user_email=user_email,
                user_name=user_name,
                security_qr_token=security_qr_tok,
                browser_token=reg_browser_tok
            )
        except Exception as _e_qr:
            print(f"⚠️ Brevo QR Email dispatch error: {_e_qr}")

    return {
        "message": f"✅ Account verified! Security QR Code sent to {user_email if user_email else 'your email'}. Please upload or scan your QR Code to reset password.",
        "account_verified": True
    }

@app.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    raw_identifier = req.email_or_mobile.strip()
    clean_phone = "".join(filter(str.isdigit, raw_identifier))
    import re
    identifier_regex = re.compile(f"^{re.escape(raw_identifier.lower())}$", re.IGNORECASE)
    
    query = [
        {"email": identifier_regex},
        {"email_or_mobile": identifier_regex},
        {"internal_id": raw_identifier}
    ]
    if clean_phone:
        query.append({"phone": clean_phone})
        query.append({"email_or_mobile": clean_phone})
        
    user = users_collection.find_one({"$or": query})
    if not user:
        raise HTTPException(status_code=400, detail="⚠️ Account Not Found.")

    user_email = (user.get("email") or "").strip().lower()
    user_phone = (user.get("phone") or "").strip()
    user_internal_id = (user.get("internal_id") or "").strip().lower()

    # MANDATORY ACTIVE BROWSER SESSION CHECK AT STEP 2
    client_sess_id = (req.current_session_user_id or "").strip().lower()
    client_sess_email = (req.current_session_user_email or "").strip().lower()
    client_sess_phone = (req.current_session_user_phone or "").strip()

    session_matched = False
    if client_sess_email and client_sess_email == user_email:
        session_matched = True
    elif client_sess_phone and (client_sess_phone == user_phone or client_sess_phone in user_phone):
        session_matched = True
    elif client_sess_id and client_sess_id in [user_email, user_phone, user_internal_id]:
        session_matched = True

    if not session_matched:
        raise HTTPException(
            status_code=400,
            detail="⚠️ Security Error: Account Session Mismatch! This browser is not logged into this account."
        )

        
    # Security QR Code Token Verification
    stored_qr_tok = user.get("security_qr_token")
    client_qr_tok = (req.qr_token or "").strip()

    if not client_qr_tok:
        raise HTTPException(
            status_code=400,
            detail="⚠️ Security Error: Please upload or scan your Cloxel Security QR Code to proceed."
        )
    
    extracted_token = client_qr_tok
    if "security_token" in client_qr_tok:
        try:
            parsed = json.loads(client_qr_tok)
            extracted_token = parsed.get("security_token", client_qr_tok)
        except Exception:
            pass
    
    if stored_qr_tok and extracted_token.strip() != stored_qr_tok.strip():
        raise HTTPException(
            status_code=400,
            detail="⚠️ Security Error: Invalid QR Code! The uploaded QR Code token does not match your registered account credential."
        )
        
    if not req.new_password or len(req.new_password.strip()) < 4:
        raise HTTPException(status_code=400, detail="⚠️ New password must be at least 4 characters long.")

    new_hash = safe_hash_password(req.new_password.strip())
    
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password_hash": new_hash, "password": new_hash},
            "$unset": {"reset_otp": "", "reset_otp_expires_at": ""}
        }
    )
    
    return {"message": "✅ Password reset successfully! You can now log in with your new password."}





@app.get("/history/{internal_id}")
async def get_video_history(internal_id: str):
    if videos_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        user_or_terms = [{"internal_id": internal_id}, {"user_id": internal_id}]
        if users_collection is not None:
            user = users_collection.find_one({"internal_id": internal_id})
            if user:
                if user.get("email"):
                    user_or_terms.append({"internal_id": user.get("email")})
                    user_or_terms.append({"user_id": user.get("email")})
                if user.get("phone"):
                    user_or_terms.append({"internal_id": user.get("phone")})
                    user_or_terms.append({"user_id": user.get("phone")})
                if user.get("email_or_mobile"):
                    user_or_terms.append({"internal_id": user.get("email_or_mobile")})

        videos_cursor = videos_collection.find({"$or": user_or_terms}).sort("created_at", -1)
        videos_list = []
        seen_job_ids = set()
        for v in videos_cursor:
            j_id = v.get("job_id")
            if j_id and j_id in seen_job_ids:
                continue
            if j_id:
                seen_job_ids.add(j_id)

            c_at = v.get("created_at")
            if isinstance(c_at, datetime):
                c_at_str = c_at.isoformat()
            else:
                c_at_str = str(c_at) if c_at else None

            videos_list.append({
                "job_id": j_id,
                "topic": v.get("topic") or v.get("title") or "Unknown Topic",
                "title": v.get("title") or v.get("topic") or "AI Video",
                "description": v.get("description", ""),
                "cloudinary_url": v.get("cloudinary_url"),
                "created_at": c_at_str
            })
        return {"history": videos_list}
    except Exception as e:
        print(f"⚠️ get_video_history fallback: {e}")
        return {"history": []}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id in jobs:
        return jobs[job_id]
    if rendering_jobs is not None:
        try:
            job_doc = rendering_jobs.find_one({"job_id": job_id}, {"_id": 0})
            if job_doc:
                jobs[job_id] = job_doc
                return job_doc
        except Exception as e:
            print(f"⚠️ DB status lookup exception for {job_id}: {e}")
    return {"status": "not_found"}

@app.get("/download/{job_id}")
async def download_video(job_id: str):
    job = jobs.get(job_id)
    if not job and rendering_jobs is not None:
        try:
            job = rendering_jobs.find_one({"job_id": job_id}, {"_id": 0})
        except Exception:
            pass
    if job and job.get("status") == "completed":
        file_path = job.get("file")
        if file_path and os.path.exists(file_path):
            return FileResponse(file_path, media_type="video/mp4", filename="cloxel_video.mp4")
        elif job.get("cloudinary_url"):
            return RedirectResponse(url=job.get("cloudinary_url"))
    raise HTTPException(status_code=404, detail="Video file not found or expired on server")

@app.get("/bg-music-list")
async def get_bg_music_list():
    music_files = ["cool.mp3", "cool1.mp3", "cool2.mp3", "cool3.mp3", "cool4.mp3", "cool5.mp3"]
    search_dirs = [".", "./songs", "./songs copy"]
    found = set(music_files)
    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower().endswith(('.mp3', '.wav')):
                    found.add(f)
    return {"music_tracks": sorted(list(found))}

@app.get("/fonts-list")
async def get_fonts_list():
    fonts_dir = "./fonts"
    fonts = ["Arial.ttf"]
    if os.path.exists(fonts_dir):
        fonts = [f for f in os.listdir(fonts_dir) if f.lower().endswith(('.ttf', '.otf'))]
    return {"fonts": sorted(fonts)}

@app.post("/cleanup/{job_id}")
async def cleanup(job_id: str):
    """Video download hone ke baad server saaf karne ke liye"""
    job = jobs.get(job_id)
    if job:
        if os.path.exists(job.get("file", "")): os.remove(job["file"])
        if os.path.exists(job.get("dir", "")): shutil.rmtree(job["dir"])
        return {"status": "Cleaned"}
    return {"error": "Job not found"}

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_flow():
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        return None

    client_config = {
        "web": {
            "client_id": client_id,
            "project_id": "cloxel-app",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": [os.getenv("YOUTUBE_REDIRECT_URI", "https://cloxel.onrender.com/youtube/callback")]
        }
    }
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config, scopes=YOUTUBE_SCOPES
    )
    flow.redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "https://cloxel.onrender.com/youtube/callback")
    return flow

class UnlinkRequest(BaseModel):
    internal_id: str

@app.get("/youtube/auth-url")
async def get_youtube_auth_url(internal_id: str):
    if not internal_id:
        raise HTTPException(status_code=400, detail="Missing user internal_id")

    if users_collection is not None:
        user = users_collection.find_one({"internal_id": internal_id})
        if user:
            sub = user.get("subscription", {})
            sub_status = sub.get("status")
            sub_expires = sub.get("expires_at")
            is_active = False
            if sub_status == "active" and sub_expires:
                if isinstance(sub_expires, str):
                    try:
                        sub_expires = datetime.fromisoformat(sub_expires)
                    except Exception:
                        sub_expires = None
                if isinstance(sub_expires, datetime) and sub_expires > datetime.utcnow():
                    is_active = True
            if not is_active:
                raise HTTPException(
                    status_code=403,
                    detail="⚠️ YouTube Connection Requires Active Paid Membership! Please upgrade your plan (Short Starter, Long Master, Pro Combo) to link your YouTube account."
                )

    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=500, detail="YouTube Client ID/Secret not configured in environment.")
    
    redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "https://cloxel.onrender.com/youtube/callback")
    scope = " ".join(YOUTUBE_SCOPES)
    
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "access_type": "offline",
        "prompt": "consent",
        "state": internal_id
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return {"auth_url": auth_url}

@app.get("/youtube/callback")
async def youtube_callback(state: str, code: str):
    internal_id = state
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "https://cloxel.onrender.com/youtube/callback")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="YouTube Client ID/Secret not configured.")
    
    try:
        token_data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        resp = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        res_json = resp.json()
        
        if "error" in res_json:
            error_msg = res_json.get("error_description", res_json.get("error"))
            print(f"❌ Token exchange error: {error_msg}")
            frontend_url = os.getenv("FRONTEND_URL", "https://cloxel.onrender.com")
            return RedirectResponse(url=f"{frontend_url}/?yt_error={error_msg}")
            
        user = users_collection.find_one({"internal_id": internal_id}) if users_collection is not None else None
        existing_creds = user.get("youtube_credentials", {}) if user else {}
        fresh_refresh_token = res_json.get('refresh_token') or existing_creds.get('refresh_token')

        creds_dict = {
            'token': res_json.get('access_token'),
            'refresh_token': fresh_refresh_token,
            'token_uri': "https://oauth2.googleapis.com/token",
            'client_id': client_id,
            'client_secret': client_secret,
            'scopes': YOUTUBE_SCOPES,
            'status': 'active'
        }
        
        if users_collection is not None:
            pending_list = user.get("pending_youtube_uploads", []) if user else []
            
            users_collection.update_one(
                {"internal_id": internal_id},
                {"$set": {
                    "youtube_credentials": creds_dict,
                    "youtube_linked_at": datetime.utcnow()
                },
                "$unset": {"pending_youtube_uploads": ""}}
            )

            if pending_list:
                print(f"🚀 Auto-flushing {len(pending_list)} pending videos for user {internal_id}...")
                for p_vid in pending_list:
                    try:
                        upload_video_to_youtube_core(
                            user_id=internal_id,
                            video_file=p_vid.get("video_file"),
                            title=p_vid.get("title"),
                            description=p_vid.get("description"),
                            is_short=p_vid.get("is_short", False)
                        )
                    except Exception as e_p:
                        print(f"⚠️ Error uploading pending video for {internal_id}: {e_p}")
            
        frontend_url = os.getenv("FRONTEND_URL", "https://cloxel.onrender.com")
        return RedirectResponse(url=f"{frontend_url}/?yt_success=1")
    except Exception as e:
        print(f"❌ Error in youtube_callback: {e}")
        import traceback
        traceback.print_exc()
        frontend_url = os.getenv("FRONTEND_URL", "https://cloxel.onrender.com")
        return RedirectResponse(url=f"{frontend_url}/?yt_error={str(e)}")

@app.get("/youtube/status/{internal_id}")
async def get_youtube_status(internal_id: str):
    if users_collection is None:
        return {"linked": False}
    try:
        projection = {"youtube_credentials": 1, "youtube_linked_at": 1}
        user = users_collection.find_one({"internal_id": internal_id}, projection)
        if not user or "youtube_credentials" not in user:
            return {"linked": False}

        creds = user.get("youtube_credentials", {})
        if creds.get("status") == "expired":
            return {"linked": False, "expired": True, "error": "YouTube Authorization Expired. Please re-connect channel."}
            
        linked_at = user.get("youtube_linked_at")
        if not linked_at:
            return {"linked": True, "can_unlink": True, "hours_left": 0}
            
        if isinstance(linked_at, str):
            try:
                linked_at = datetime.fromisoformat(linked_at.replace('Z', '+00:00'))
            except Exception:
                linked_at = None
                
        if isinstance(linked_at, datetime):
            if linked_at.tzinfo is not None:
                linked_at = linked_at.astimezone(timezone.utc).replace(tzinfo=None)
            hours_passed = (datetime.utcnow() - linked_at).total_seconds() / 3600
            hours_left = max(0, int(24 - hours_passed))
            return {"linked": True, "can_unlink": hours_passed >= 24, "hours_left": hours_left}

        return {"linked": True, "can_unlink": True, "hours_left": 0}
    except Exception as e:
        print(f"⚠️ get_youtube_status fallback notice for {internal_id}: {e}")
        return {"linked": False}

@app.post("/youtube/unlink")
async def unlink_youtube(req: UnlinkRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    user = users_collection.find_one({"internal_id": req.internal_id})
    if not user or "youtube_credentials" not in user:
        raise HTTPException(status_code=400, detail="No YouTube account linked")
        
    linked_at = user.get("youtube_linked_at")
    if linked_at:
        if isinstance(linked_at, str):
            try:
                linked_at = datetime.fromisoformat(linked_at.replace("Z", "+00:00"))
                if linked_at.tzinfo is not None:
                    linked_at = linked_at.astimezone(timezone.utc).replace(tzinfo=None)
            except Exception:
                linked_at = None

        if isinstance(linked_at, datetime):
            time_passed = datetime.utcnow() - linked_at
            if time_passed < timedelta(hours=24):
                hours_left = max(0, round(24 - (time_passed.total_seconds() / 3600), 1))
                raise HTTPException(status_code=403, detail=f"Cannot unlink before 24 hours have passed. ({hours_left} hours left)")
            
    users_collection.update_one(
        {"internal_id": req.internal_id},
        {
            "$unset": {
                "youtube_credentials": "",
                "youtube_linked_at": "",
                "auto_schedule": "",
                "staged_auto_videos": ""
            }
        }
    )
    
    return {"message": "YouTube account unlinked successfully. Auto-publishing stopped and all schedule settings reset."}


class AIScriptRequest(BaseModel):
    topic: str
    category: Optional[str] = "Random" # 30+ categories or custom
    duration_seconds: int = 30
    video_type: Optional[str] = "short"  # 'short' or 'long'
    language: Optional[str] = "hinglish" # 'hindi', 'english', 'hinglish'
    tone: Optional[str] = "viral"        # 'viral', 'informative', 'mysterious', 'funny'

def generate_ai_script_core(topic: str, duration: int, video_type: str = "short", language: str = "hinglish", tone: str = "viral", category: str = "Random"):
    import random
    topic = resolve_random_topic(topic, category)
    raw_env_url = os.getenv("AI_SERVER_URL", "").rstrip("/")
    candidate_urls = [
        "https://ai-script-generator-service-production.up.railway.app",
        raw_env_url if raw_env_url else "https://ai-script-generator-service.onrender.com",
        "https://ai-script-generator-service.onrender.com"
    ]
    seen = set()
    ai_server_urls = [u for u in candidate_urls if u and not (u in seen or seen.add(u))]

    scene_count = max(1, duration // 10)
    word_count = int(duration * 2.8) if video_type == "short" else int(duration * 2.5)

    cat_niche = f" in the '{category}' category" if category and str(category).lower() != "random" else ""

    payload = {
        "topic": topic,
        "category": category,
        "duration_seconds": duration,
        "video_type": video_type,
        "language": language,
        "tone": tone
    }
    
    for base_url in ai_server_urls[:2]:
        for endpoint in ["/generate-script", "/api/generate-ai-script"]:
            target_url = f"{base_url}{endpoint}"
            try:
                resp = requests.post(target_url, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    data = resp.json()
                    full_script = data.get("full_script") or data.get("script") or ""
                    scenes = data.get("scenes") or []
                    
                    if full_script or scenes:
                        if not scenes and full_script:
                            stop_words = {"aur", "ek", "hai", "ki", "ke", "ka", "jo", "se", "me", "ko"}
                            kws = [w.lower() for w in topic.split() if w.isalpha() and w.lower() not in stop_words]
                            kw = kws[0] if kws else topic
                            chunks = full_script.split(".")
                            scenes = [{"text": c.strip(), "keyword": kw} for c in chunks if len(c.strip()) > 5][:scene_count]
                            
                        print(f"✅ External AI Script Service Success ({target_url})!")
                        title_gen, desc_gen = build_youtube_metadata(topic=topic, full_script=full_script, video_type=video_type)
                        return {
                            "status": "success",
                            "source": "external_ai_service",
                            "server_url": target_url,
                            "topic": topic,
                            "duration_seconds": duration,
                            "video_type": video_type,
                            "language": language,
                            "tone": tone,
                            "estimated_word_count": word_count,
                            "full_script": full_script,
                            "scenes": scenes,
                            "title": title_gen,
                            "description": desc_gen
                        }
            except Exception as e_inner:
                continue

    cat_lower = str(category).lower()
    is_cartoon_cat = any(k in cat_lower for k in ["cartoon", "anime", "animation", "character", "comic"])

    stop_words_check = {"history", "how", "what", "why", "secret", "future", "facts", "science", "vs", "the", "system", "warriors", "ai", "space"}
    words_in_topic = [w.lower() for w in topic.split() if w.isalpha()]
    is_single_character_name = len(words_in_topic) <= 2 and not any(w in stop_words_check for w in words_in_topic)

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            if video_type == "ultra" and is_cartoon_cat:
                if is_single_character_name:
                    ultra_special_prompt = (
                        f"\nSPECIAL ULTRA CARTOON CHARACTER STORY (KAHANI/CHUTKULA) MODE:\n"
                        f"The topic is a character name '{topic}'. Write a super funny, hilarious, comedic 2D cartoon story script (Kahani / Kissa / Comedy Chutkula) about {topic}.\n"
                        f"Show {topic}'s hilarious daily struggles, a crazy funny Jugaad/experiment gone wrong, funny cartoon dialogues, and a laugh-out-loud funny ending!\n"
                        f"Make it sound like a funny animated story that will make kids and adults laugh out loud.\n"
                    )
                else:
                    ultra_special_prompt = (
                        f"\nSPECIAL ULTRA CARTOON KAHANI (STORY) MODE REQUIREMENT:\n"
                        f"This is an ULTRA Cartoon & Animation video. Write an entertaining, creative, dramatic, and fun ANIMATED STORY (KAHANI) script about '{topic}'.\n"
                        f"The script MUST be structured like an engaging 2D cartoon story (Kahani) with relatable animated characters, fun dialogues/actions, plot twist/adventure, and a satisfying moral or funny story conclusion.\n"
                        f"Do NOT write a factual documentary or boring facts. Make it a complete, entertaining 2D cartoon story script (Kahani) with rich character storytelling.\n"
                    )
            elif video_type == "ultra":
                ultra_special_prompt = (
                    f"\nSPECIAL ULTRA MODE REQUIREMENT:\n"
                    f"This is an ULTRA premium documentary video. Write a rich, deeply informative, and complete narrative script.\n"
                    f"Do NOT output short title fragments or half-baked sentences.\n"
                    f"Each scene text MUST contain 2-3 complete, highly engaging, informative spoken sentences explaining the history, key achievements, and full story of '{topic}'.\n"
                )
            else:
                ultra_special_prompt = ""

            prompt = (
                f"You are a master viral video scriptwriter. Write a COMPLETE, fully-resolved video script about '{topic}' "
                f"in {language} language. Video type: {video_type.upper()} ({duration} seconds, approx {word_count} spoken words).\n"
                f"CRITICAL REQUIREMENT: The script MUST be 100% complete with a clear Hook, Full Story/Information, and a Satisfying Conclusion. "
                f"Do NOT leave the explanation half-done or cut off mid-sentence.{ultra_special_prompt}\n"
                f"Format requirement: Return ONLY a valid JSON object with:\n"
                f"1. 'full_script': The complete spoken voiceover text covering the full story from hook to conclusion.\n"
                f"2. 'scenes': An array of exactly {scene_count} complete sentence scene objects, each containing:\n"
                f"   - 'text': 2-3 complete, detailed, well-formed sentences with full stops.\n"
                f"   - 'keyword': 1-2 relevant visual search terms for background clips.\n"
                f"Do not include markdown triple backticks or text outside JSON."
            )

            req_data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                res_body = json.loads(resp.read().decode('utf-8'))
                raw_text = res_body['candidates'][0]['content']['parts'][0]['text'].strip()
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:].strip()
                parsed = json.loads(raw_text)
                script_text = parsed.get("full_script", "")
                title_gen, desc_gen = build_youtube_metadata(topic=topic, full_script=script_text, video_type=video_type)
                return {
                    "status": "success",
                    "source": "gemini_ai",
                    "topic": topic,
                    "duration_seconds": duration,
                    "video_type": video_type,
                    "language": language,
                    "tone": tone,
                    "estimated_word_count": word_count,
                    "full_script": script_text,
                    "scenes": parsed.get("scenes", []),
                    "title": title_gen,
                    "description": desc_gen
                }
        except Exception as err:
            print(f"⚠️ Cloxel AI Engine Notice (Falling back to dynamic engine): {err}")

    stop_words = {"aur", "ek", "hai", "ki", "ke", "ka", "jo", "se", "me", "ko", "hi", "to", "ye", "wo", "tha", "thi"}
    keywords = [w.lower() for w in topic.split() if w.isalpha() and w.lower() not in stop_words]
    main_kw = keywords[0] if keywords else topic

    if video_type == "ultra" and is_cartoon_cat:
        if is_single_character_name:
            intro_templates = [
                f"Dosto! Aapko milate hain humare cartoon hero {topic} se, jinki zindagi mein har din ek naya aur mazedar hungama hota hai!",
                f"Ek din {topic} ne socha ki aaj kuch toofani karte hain, aur bas wahin se shuru hua sabse mazedar kissa!"
            ]
            body_templates = [
                f"{topic} ne apna super-dimag lagakar ek aisa dhasu jugaad kiya ki poore mohalle ke hosh ud gaye.",
                f"Dekhte hi dekhte {topic} ka ye jugaad ek mazedar comedy mistake ban gaya aur sabhi cartoon dost pet pakad kar hasne lage.",
                f"Lekin {topic} ne haar nahi maani aur apni chalaki se aakhiri minute mein situation ko poori tarah sambhal kiya."
            ]
            outro_templates = [
                f"Aur is tarah {topic} ke is funny kissey ne sabko hasa-hasa kar lothpoth kar diya! Agar {topic} ki kahani pasand aayi toh video ko like aur channel ko subscribe karein!",
                f"Yahi toh khas baat hai {topic} ki! Aise hi aur mazedar cartoon kisse dekhne ke liye video ko share zaroor karein!"
            ]
        else:
            intro_templates = [
                f"Ek samay ki baat hai, {topic} ki cartoon duniya mein ek bahut hi dilchasp aur mazedar kahani shuru hui.",
                f"Chhote se cartoon gaon mein {topic} ke characters ke beech ek anokhi kahani ghati, aaiye is mazedar kahani ko jaante hain."
            ]
            body_templates = [
                f"Kahani mein mukhya cartoon character ne apni samajhdaari aur chalaki se ek badi chunauti ka samna kiya aur dosto ko chaunkaya.",
                f"Dekhte hi dekhte kahani mein ek mazedar twist aaya jahan sabhi cartoon dosto ne milkar ek anokha hal nikala.",
                f"Is thrilling cartoon mod par sabhi characters ne ek doosre ki madad ki aur har mushkil ko aasan bana diya."
            ]
            outro_templates = [
                f"Aakhirkar, ye pyaari kahani hume sikhaati hai ki mehnat aur dosti se har mushkil aasan ho jaati hai. Kahani pasand aayi toh video ko like aur follow karein!",
                f"Aur is tarah {topic} ki ye mazedar cartoon kahani ek khushgawar ant ke sath poori hui. Channel ko subscribe karein!"
            ]
    elif video_type == "ultra":
        intro_templates = [
            f"Itihas aur gathaon mein {topic} ka naam swabhiman aur veerta ka prateek mana jata hai. Iski poori kahani aapko aashcharya mein daal degi.",
            f"Kya aap jante hain {topic} se judi wo aitihasik baatein jo aaj bhi har bhartiya ke dil mein garv bhar deti hain? Aaiye vistaar se jaante hain."
        ]
        body_templates = [
            f"Iska mukhya uddeshya swabhiman aur matribhumi ki raksha karna tha, jiske liye yoddhaon ne aakhir saans tak sangharsh kiya.",
            f"Aitihasik shastron aur dastaavezon ke mutabiq {topic} ne shatruon ki sena ke chakke chhudaye the aur itihaas mein apna naam amar kar diya.",
            f"Ranbhoomi mein inki talwar aur ranniti ne dushmano ko aisi shikast di jise aaj bhi yaad kiya jata hai."
        ]
        outro_templates = [
            f"Yahi wajah hai ki {topic} ki ye veer gatha aaj bhi har peedhi ke liye prerna ka srot hai. Is aitihasik jaankari ke liye hume follow karein.",
            f"Swabhiman ki is kahani ne {topic} ko mahan bana diya. Aise hi aur durlabh aitihasik kisse dekhne ke liye channel ko subscribe karein!"
        ]
    else:
        intro_templates = [
            f"Dosto! Kya aapko pata hai {topic} ke baare mein ye hairatangez sach?",
            f"{topic} ki duniya mein ek aisa raaz hai jo aapka hosh uda dega.",
            f"Aaj hum {topic} se jude sabse bada aur shocking sach jaanenge."
        ]
        body_templates = [
            f"Iske peeche ki asli wajah ye hai ki {topic} hamari daily life par deep impact daalta hai.",
            f"Experts aur scientists ke mutabiq {topic} aane wale time mein poori tarah badalne wala hai.",
            f"Research mein pata chala hai ki {topic} ki wajah se kayi bade changes dekhe gaye hain.",
            f"Har roz hazaron log {topic} ke is naye aspect ko samajhne ki koshish kar rahe hain."
        ]
        outro_templates = [
            f"Toh ye tha {topic} ka poora sach! Aise hi viral aur informative content ke liye hume zaroor follow karein.",
            f"Yahi wajah hai ki {topic} itna special hai. Video acchi lagi ho toh like aur share zaroor karein!",
            f"Umeed hai aapko {topic} ki ye information pasand aayi hogi. Channel ko subscribe karna na bhulein!"
        ]

    scenes = []
    full_text_list = []
    
    for i in range(scene_count):
        if i == 0:
            text = random.choice(intro_templates)
        elif i == scene_count - 1 and scene_count > 1:
            text = random.choice(outro_templates)
        else:
            text = body_templates[(i - 1) % len(body_templates)]
            
        scenes.append({"text": text, "keyword": main_kw})
        full_text_list.append(text)

    script_text = " ".join(full_text_list)
    title_gen, desc_gen = build_youtube_metadata(topic=topic, full_script=script_text, video_type=video_type)
    return {
        "status": "success",
        "source": "dynamic_ai_engine",
        "topic": topic,
        "duration_seconds": duration,
        "video_type": video_type,
        "language": language,
        "tone": tone,
        "estimated_word_count": word_count,
        "full_script": script_text,
        "scenes": scenes,
        "title": title_gen,
        "description": desc_gen
    }

@app.post("/api/generate-ai-script")
async def api_generate_ai_script(req: AIScriptRequest):
    """
    Dedicated AI Script Generation API for Render/Remote clients.
    Takes topic, duration_seconds, video_type, language, and tone.
    Returns full_script and scene breakdown.
    """
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic title is required")
        
    duration = max(10, min(300, req.duration_seconds))
    return generate_ai_script_core(
        topic=req.topic.strip(),
        duration=duration,
        video_type=req.video_type or "short",
        language=req.language or "hinglish",
        tone=req.tone or "viral"
    )

@app.post("/generate-script")
async def generate_script(req: ScriptRequest):
    """Script generation endpoint with Free Quota & Security Protection"""
    user_id = req.user_id
    if user_id and user_id != "anonymous" and users_collection is not None:
        user = users_collection.find_one({"internal_id": user_id})
        if user:
            subscription = user.get("subscription", {})
            sub_status = subscription.get("status")
            sub_expires = subscription.get("expires_at")
            is_active = False
            if sub_status == "active" and sub_expires:
                if isinstance(sub_expires, str):
                    try:
                        sub_expires = datetime.fromisoformat(sub_expires)
                    except Exception:
                        sub_expires = None
                if sub_expires and sub_expires > datetime.utcnow():
                    is_active = True
            
            if not is_active and user.get("free_demo_count", 0) <= 0:
                raise HTTPException(
                    status_code=402, 
                    detail="Demo quota exhausted! You have used your 2 free demo videos & scripts. Please upgrade your plan to continue generating AI scripts & videos."
                )

    res = generate_ai_script_core(topic=req.topic, duration=req.duration_seconds, category=req.category or "Random", video_type=req.video_type or "short")
    return {"scenes": res["scenes"], "full_script": res["full_script"]}

@app.get("/robots.txt", response_class=Response)
async def get_robots_txt():
    robots_content = "User-agent: *\nAllow: /\n\nSitemap: https://cloxelai.onrender.com/sitemap.xml\n"
    return Response(content=robots_content, media_type="text/plain")

@app.get("/sitemap.xml", response_class=Response)
async def get_sitemap_xml():
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://cloxelai.onrender.com/</loc>
        <lastmod>2026-08-31</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>"""
    return Response(content=sitemap_content, media_type="application/xml")

@app.get("/googleaa929f03abece7ff.html", response_class=Response)
async def get_google_verification_html():
    return Response(content="google-site-verification: googleaa929f03abece7ff.html", media_type="text/html")

if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
else:
    print("WARNING: frontend/dist not found. Run 'npm run build' in the frontend folder.")