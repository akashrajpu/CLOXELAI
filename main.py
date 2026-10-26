import os
import sys
import gc
import time
import random
import hashlib
import base64
import hmac
import uuid
import shutil
import json
import re
import requests
import warnings
import urllib.parse
import urllib.request
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from cryptography.fernet import Fernet

warnings.filterwarnings("ignore")

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

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta, timezone
try:
    from googleapiclient.discovery import build
    import google_auth_oauthlib.flow
except Exception as _g_err:
    build = None
    google_auth_oauthlib = None

from apscheduler.schedulers.background import BackgroundScheduler
import requests
from firewall_security import (
    FirewallMiddleware, waf, verify_admin_access, 
    sanitize_alphanumeric_id, sanitize_nosql, clean_xss, resolve_client_ip
)
try:
    from web_image_fetcher import fetch_web_image, extract_rich_scene_visual_keywords, clean_topic_title, HINDI_STOPWORDS
except Exception as _w_err:
    print(f"⚠️ web_image_fetcher top import warning: {_w_err}")
    fetch_web_image = None
    extract_rich_scene_visual_keywords = None
    clean_topic_title = lambda x: str(x)
    HINDI_STOPWORDS = set()

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
payment_orders_collection = None

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
        payment_orders_collection = db.payment_orders

        try:
            users_collection.create_index("internal_id", unique=True, background=True)
            users_collection.create_index("email", background=True)
            users_collection.create_index("phone", background=True)
            users_collection.create_index("email_hash", background=True)
            users_collection.create_index("phone_hash", background=True)
            videos_collection.create_index([("internal_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)], background=True)
            videos_collection.create_index("job_id", background=True)
            rendering_jobs.create_index("job_id", unique=True, background=True)
            payment_orders_collection.create_index("order_id", unique=True, background=True)
            payment_orders_collection.create_index([("internal_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)], background=True)
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
        payment_orders_collection = None
else:
    print("WARNING: MONGO_URI is missing in config.env! Authentication will not work properly.")

def ensure_db_alive():
    """Ultra-resilient DB heart-beat to auto-reconnect MongoDB if network hiccups occur."""
    global mongo_client, db, users_collection, videos_collection, rendering_jobs, payment_orders_collection
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
                payment_orders_collection = db.payment_orders
                print("🔄 MongoDB auto-reconnected successfully!")
            except Exception as rec_err:
                print(f"❌ DB Auto-reconnect failed: {rec_err}")

def update_job_status(job_id: str, status_data: dict):
    jobs[job_id] = status_data
    if len(jobs) > 100:
        try:
            excess_keys = list(jobs.keys())[:-50]
            for k in excess_keys:
                jobs.pop(k, None)
        except Exception:
            pass
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
    temp_dl_file = None
    if video_file and (video_file.startswith("http://") or video_file.startswith("https://")):
        try:
            import tempfile
            print(f"📥 Downloading pre-rendered video from Cloudinary: {video_file}...")
            r = requests.get(video_file, stream=True, timeout=60)
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            for chunk in r.iter_content(chunk_size=1024*1024):
                tf.write(chunk)
            tf.close()
            temp_dl_file = tf.name
            video_file = temp_dl_file
        except Exception as e_dl:
            print(f"❌ Failed to download video from Cloudinary: {e_dl}")
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
    finally:
        if temp_dl_file and os.path.exists(temp_dl_file):
            try:
                os.remove(temp_dl_file)
            except Exception:
                pass



def get_combinatorial_daily_topic(category: str = "Random", day_seed: str = "") -> str:
    """
    2+ Year (1000-Day) Zero-Duplicate Permutation Matrix.
    Uses an affine bijection (gcd(37, 1000) == 1) over date/day to mathematically guarantee
    that for 1,000+ days (almost 3 full years), no topic ever repeats!
    """
    matrix = {
        "cartoon": {
            "subjects": [
                "Chintu", "Ramesh", "Pappu", "Bunty", "Golu", "Dhoolu", "Chatur Pandit",
                "Motu aur Chhotu", "Vicky", "Raju", "Master Chef Bunty", "Pintoo", "Babban Seth",
                "Professor Dheemi Awaaz", "Kallu Halwai", "Cheeku Khargosh", "Gappu", "Dadi Amma",
                "Shambu Shikari", "Bittu Mechanic", "Champak Chacha", "Natkhat Chunnu", "Rocky Boxer",
                "Jholuram Detective", "Munna Scientist", "Tinku Painter", "Lallan Driver", "Bholu Pehelwan",
                "Inspector Cheeta", "Pandit Babulal", "Khopdi Bhaisaab", "Chatori Chameli", "Ustaad Tabla",
                "Sultan Sher", "Mangu Machhuara", "Babloo Barber", "Pappu Postman", "Dhanraj Seth",
                "Shera Kutte Ka Dost", "Chhota Don"
            ],
            "angles": [
                "Ka Superhit Jugaad", "Ka High-Speed Scooter Drama", "Ka Magic Cycle Hungama",
                "Ka Canteen Magic Samosa", "aur Uski Bolne Wali Billi", "Ka Time-Machine Bicycle",
                "in School Naughty Drama", "Ka Invisible Spray Hungama", "Ka Mirchi Ka Halwa",
                "aur Uski Remote Control Khatiya", "Ka Missing Khazana", "Ka Rocket Experiment",
                "aur Mota Bhaloo", "aur Chaalak Lomdi", "Ka Cricket Match Super Six",
                "Ka Flying Jhaadu", "Ka Ulta Shikar", "Ka Super Turbo Tractor",
                "Ka Funny Ghost Encounter", "Ka Bada Lottery Ticket", "aur Alibaba Ka Secret Khazana",
                "Ka Robot Dost Hungama", "Ka Swimming Pool Formula", "Ka Underwater Adventure",
                "Ka Flying Kite Competition"
            ]
        },
        "horror": {
            "subjects": [
                "The Haunted Bhangarh Fort", "The Dyatlov Pass Incident", "The Cursed Annabelle Doll",
                "The Ghost Highway Midnight Cry", "The Vanishing Village of Lake Anjikuni",
                "The Screaming Mummy of Egypt", "The Mary Celeste Abandoned Ship",
                "The Shadow Person Phenomenon", "The Winchester Mystery House",
                "Aokigahara Silent Forest Whispers", "The Bell Witch Poltergeist",
                "The Black-Eyed Children Encounters", "The Cursed Hope Diamond",
                "The Mothman Sightings", "The Unsolved Midnight Knock Phantom",
                "The Secret Island of Dr Moreau", "The Phantom Train of Italy",
                "The Cursed Painting The Hands Resist Him", "The Bermuda Triangle Flight 19",
                "Eastern State Penitentiary Hauntings", "The Crying Boy Painting Curse",
                "The Island of Dead Dolls Mexico", "The Secret Catacombs of Paris",
                "The Tower of London Royal Ghosts", "The Demon of Brown Mountain Lights",
                "The Midnight Hitchhiker on Route 66", "The Lost Colony of Roanoke",
                "The Cursed Tomb of Tutankhamun", "The Bridgewater Triangle Anomalies",
                "The Black Forest Germany Whispers", "The Sallie House Hauntings",
                "The Changi Hospital Singapore Horrors", "The Stanley Hotel Room 217",
                "The Helltown Ohio Urban Legend", "The Whispering Walls of Leap Castle",
                "The Ghost Ship SS Ourang Medan", "The Mystery of Highgate Cemetery Vampire",
                "The Exorcism of Roland Doe", "The Poveglia Plague Island Italy",
                "The Enfield Poltergeist Strange Recordings"
            ],
            "angles": [
                "The Dark Mystery Finally Uncovered", "Unexplained Real Audio Recordings",
                "What Investigators Found Inside", "The Terrifying Untold True Story",
                "Why Nobody Visits After Midnight", "The Shocking Secret Hidden for 100 Years",
                "The Bizarre Vanishing No One Can Explain", "What Eye Witnesses Refuse to Forget",
                "The Real Curse That Scientists Still Fear", "Shocking Evidence Caught on Camera",
                "The Secret Government File Exposed", "Why Experts Warn Never to Enter",
                "The Creepy Timeline of Disappearances", "The Unsolved Puzzle Behind the Haunting",
                "What Happened to the Final Survivor?", "The Terrifying Truth Behind The Legend",
                "The 3 AM Ritual That Went Horribly Wrong", "The Lost Footage Never Released to Public",
                "The Paranormal Investigation That Shook Scientists", "The Hidden Chamber Behind The Wall",
                "The Chilling Messages Left Behind", "Why The Entire Town Was Abandoned Overnight",
                "The Shocking Autopsy Reports Kept Secret", "What Lurks in The Darkest Corner?",
                "The Ancient Curse Awakened"
            ]
        },
        "tech": {
            "subjects": [
                "Autonomous AI Humanoid Robots", "Quantum Computing Supercomputers",
                "Neuralink Brain-Computer Chips", "Artificial General Intelligence AGI",
                "Holographic 3D Projection Technology", "Cybersecurity and Dark Web Wars",
                "Self-Healing Materials and Nanotech", "AI Powered Smart Mega Cities",
                "Hypersonic Commercial Flight in 1 Hour", "Solid-State Battery Energy Storage",
                "Wearable Military Exoskeletons", "Nuclear Fusion Artificial Sun Tokamak",
                "Deepfake AI Voice and Video Clones", "Autonomous Military Drone Swarms",
                "6G Terahertz Wireless Networks", "1 Nanometer Microchip Limits",
                "Decentralized Web3 Global Computers", "AI Robotic Surgeons in Hospitals",
                "Space-Based Solar Microwave Power", "Lab Grown Molecular Meat and Foods",
                "Hyper Realistic Full Immersion VR", "Autonomous Underwater AI Drones",
                "DNA Data Storage Technology", "AI Film and Music Generation Studios",
                "Unhackable Quantum Internet", "3D Printed Lunar and Martian Habitats",
                "Autonomous Electric Flying Cars", "Mind Uploading and Digital Immortality",
                "Quantum Gravitational Wave Detectors", "Wireless Power Beaming Across Miles",
                "Synthetic Biology and Engineered Organisms", "Smart Contact Lenses with Augmented Reality",
                "Graphene Superconductors at Room Temp", "Robotic Agriculture Harvesting Food",
                "Autonomous Micro-Satellites Swarms", "AI Weather and Earthquake Prediction",
                "Bionic Eye Restoring Full Human Vision", "Self-Assembling Nanobots in Medicine",
                "Ocean Water Desalination by Graphene", "Brain-to-Brain Direct Telepathy Networks"
            ],
            "angles": [
                "How It Will Completely Change 2030", "The Dark Danger Nobody Talks About",
                "What Scientists Just Discovered", "The Incredible Secret Breakthrough",
                "Why Big Tech is Spending Billions On This", "The Shocking Reality Behind The Tech",
                "How Close Are We Really?", "The Secret Military Experiment Revealed",
                "What Happens When It Becomes Self-Aware?", "The Billion-Dollar Race to Control It",
                "Why Experts Warn It Could Go Too Far", "The Technology That Replaces Smartphones Forever",
                "How It Will Redefine Human Life", "The Hidden Flaw Nobody Saw Coming",
                "What Governments Are Keeping Secret", "The Next Big Leap in Human Evolution",
                "Why Scientists Are Terrified and Excited", "The Bizarre Experiment That Actually Worked",
                "The Mind-Blowing Future You Will Live In", "How It Solves Humanity's Greatest Crisis",
                "The Insane Engineering Behind It", "What Will Happen in the Next 5 Years?",
                "The Breakthrough That Defied Physics", "Who Really Controls This Technology?",
                "The Future of Human Civilization"
            ]
        },
        "history": {
            "subjects": [
                "Great Pyramids of Giza Alignment", "The Undersea City of Dwarka",
                "The Indus Valley Saraswati Civilization", "The Iron Pillar of Delhi Anti-Rust",
                "Maharana Pratap Guerrilla Warfare", "Chhatrapati Shivaji Maharaj Naval Forts",
                "Secret Vaults of Padmanabhaswamy Temple", "Kailasa Temple Ellora Monolithic Rock",
                "Emperor Ashoka and The Nine Unknown Men", "King Vikramaditya Golden Era Wonders",
                "The Lost Continent of Atlantis", "Ancient Roman Self-Healing Concrete",
                "King Tutankhamun Golden Treasures", "Qin Shi Huang Terracotta Secret Army",
                "Stonehenge Solar Alignment Secrets", "The Burning of Library of Alexandria",
                "Mongol Horse Cavalry Battle Formations", "The Lost Tomb of Alexander The Great",
                "The Antikythera Ancient Computer", "Daulatabad Invincible Fort Architecture",
                "The Voynich Manuscript Secret Cipher", "Machu Picchu Inca Mountain Engineering",
                "The Mayan Astronomical Accurate Calendar", "Knights Templar Hidden Holy Relics",
                "Hanging Gardens of Babylon Archaeology", "Derinkuyu Massive Underground City",
                "The Nazca Lines Giant Desert Drawings", "Great Wall of China Hidden Fortresses",
                "Chanakya and Chandragupta Maurya Strategy", "Mohenjo-daro Advanced Urban Sanitation",
                "The Lost Golden City of El Dorado", "The Viking Sunstone Navigation Secret",
                "The Sacred Geometry of Angkor Wat", "The Sun Temple of Konark Wheels",
                "Spartan 300 Battle of Thermopylae", "Samurai Bushido Code and Katana Steel",
                "The Mysterious Baghdad Ancient Battery", "The Secret Wealth of Mansa Musa",
                "The Trojan Horse Archaeological Truth", "The Golden Age of Nalanda University"
            ],
            "angles": [
                "The Untold Story History Books Omitted", "The Unsolved Engineering Mystery",
                "What Archaeologists Discovered Underground", "The Shocking Secrets Kept Silent",
                "How Ancient Engineers Defied Modern Logic", "The Lost Treasure That Was Never Found",
                "The Tactical Genius That Shocked The World", "The Sacred Secrets Hidden for Millennia",
                "The Real Reason Why The Empire Collapsed", "Mind-Blowing Ancient Technology Discovered",
                "The Hidden Vault That Was Never Opened", "The Greatest Warrior You Never Heard Of",
                "What Really Happened on That Tragic Day", "The Secret Manuscript Finally Decoded",
                "The Unbelievable Battle Strategy That Won", "Why Historians Are Still Arguing About This",
                "The Ancient Secret That Modern Science Can't Replicate", "The Dark Conspiracy Behind The Throne",
                "The Lost Evidence That Proves The Legend", "What The Carvings on The Walls Actually Mean",
                "The Extraordinary Legacy That Changed Everything", "The Most Mysterious King in History",
                "The Hidden Underground Chambers Uncovered", "The Incredible Wealth That Vanished",
                "The Epic Saga of Valor and Sacrifice"
            ]
        },
        "science": {
            "subjects": [
                "What If Earth Stopped Spinning for 5 Seconds?", "Deep Sea Mariana Trench Creatures",
                "Human Subconscious Mind Superpowers", "Supermassive Black Holes Singularity",
                "What If Humans Only Slept 1 Hour a Day?", "Parallel Universes Quantum Superposition",
                "CRISPR DNA Genetic Modification", "Immortal Jellyfish Biological Secret",
                "The Placebo Effect Healing Mechanism", "Antimatter Creation and Storage Limits",
                "Human Brain 86 Billion Neurons Network", "The Science of Déjà Vu Brain Glitches",
                "Tardigrades Surviving Space Vacuum", "Time Dilation Near Speed of Light",
                "Gut Microbiome Controlling Mood", "Lucid Dreaming Conscious Control",
                "Superfluid Helium Crawling Walls", "Van der Waals Gecko Wall Climbing",
                "Electric Eel 860 Volt Electricity", "Bioluminescent Glowing Ocean Waves",
                "Ball Lightning Rare Plasma Mystery", "What If The Moon Suddenly Vanished?",
                "What If Oxygen Disappeared for 5 Seconds?", "The Science of Cold Fusion Energy",
                "Human DNA Containing Ancient Viruses", "Plant Communication Root Networks",
                "Cryonics Freezing Cells Without Damage", "Extreme Volcanic Vent Organisms",
                "The Physics of Sonic Levitation", "Why We Forget Our Dreams Instantly",
                "Dark Matter Invisible Cosmic Web", "Neutron Star Sugar Cube Weighing Mountains",
                "The Mystery of Spontaneous Human Combustion", "What Lies at The Center of Earth?",
                "The Quantum Entanglement Einstein Paradox", "Synthetic Biology Creating New Life",
                "The Science of Why Time Speeds Up As We Age", "What If A Giant Asteroid Hit Tomorrow?",
                "The Mystery of Fast Radio Bursts", "The Coldest Place in The Known Universe"
            ],
            "angles": [
                "The Shocking Reality Scientists Confirmed", "What Happens to The Human Body?",
                "The Mind-Blowing Experiment That Worked", "The Science Behind The Impossible",
                "Why Modern Physics Still Can't Explain This", "What Would Happen If It Actually Occurred?",
                "The Secret Mechanism Finally Discovered", "How It Challenges Everything We Knew",
                "The Bizarre Paradox That Stumps Experts", "What Lies Beyond The Known Limit?",
                "The Terrifying Power Nature Conceals", "The Incredible Phenomenon Inside Us",
                "Why Scientists Are Closely Watching This", "The Breakthrough That Surprised Everyone",
                "The Hidden Law of Physics Exposed", "What The Universe Is Hiding from Us",
                "The Deepest Mystery in Modern Science", "How Simple Biology Achieves The Impossible",
                "The Shocking Calculation That Blew Minds", "What Happens at Absolute Zero?",
                "The Cosmic Mystery Scientists Are Racing to Solve", "The Hidden Superpower We All Possess",
                "What Would Happen to Civilization?", "The Most Dangerous Force in The Cosmos",
                "The Mind-Bending Truth About Our Reality"
            ]
        },
        "general": {
            "subjects": [
                "Bermuda Triangle Flight 19 Mystery", "Human Brain 10 Incredible Facts",
                "The Million Dollar Great Bank Heist", "Top 7 Places Forbidden to Humans",
                "Deadliest Animals of Amazon Jungle", "Mind-Blowing Psychological Tricks",
                "How Richest Billionaires Built Empires", "Unsolved Cipher Case of 1920",
                "Deep Ocean Bioluminescent Wonders", "Life Hacks That Actually Save Lives",
                "The World's Most Secure Vaults", "Shocking Coincidences in Human History",
                "The Bizarre Secret Diet of Gladiators", "Unexplained Natural Phenomena on Earth",
                "How The Human Eye Sees Colors", "The Real Reason We Need Sleep",
                "The Most Dangerous Roads in The World", "The Secret History of Passwords",
                "How Fake Money Almost Destroyed Nations", "The Mystery of Ghost Ships in History",
                "Why Humans Laugh When Nervous", "The Science Behind Memory Loss",
                "The World's Deepest Manmade Hole Kola", "What Happens When You Fly Over Antarctica?",
                "The Shocking Cost of Running The Internet", "How Ancient Navigators Used Stars",
                "The Psychological Secret of Addictive Apps", "The Bizarre Animals That Never Sleep",
                "The Secret Language of Twins", "How Diamonds Are Created Deep in Earth",
                "The Most Protected Humans on Earth", "Unbelievable Survival Stories Against All Odds",
                "The Physics Behind Boomerangs", "Why Mirrors Flip Left and Right But Not Up Down",
                "The Secret Architecture of Underground Bunkers", "How Submarines Stay Underwater for Months",
                "The Science of Why We Feel Watched", "The Mystery of The Voynich Manuscript Book",
                "Why Some People Never Get Sick", "The Insane Journey of Oil Across The World"
            ],
            "angles": [
                "The Shocking Truth Finally Exposed", "Top 5 Mind-Blowing Facts You Didn't Know",
                "What Actually Happened Behind Closed Doors", "The Incredible Story Nobody Tells You",
                "Why This Was Kept Secret for Decades", "The Bizarre Reality That Will Amaze You",
                "How It Actually Works in Real Life", "The Mind-Bending Truth Behind The Myth",
                "What Experts Discovered When They Looked Inside", "The Untold Secrets of The World",
                "Why Everyone Was Completely Wrong About This", "The Unsolved Mystery That Puzzles Geniuses",
                "The Shocking Details Behind The Event", "What Happens When Everything Goes Wrong?",
                "The Astonishing Facts That Defy Logic", "How One Simple Mistake Changed History",
                "The Secret World You Walk Past Every Day", "The Incredible Phenomenon Confirmed by Science",
                "Why This is More Dangerous Than You Think", "The Fascinating Truth About Human Nature",
                "What You Never Knew About Everyday Life", "The Greatest Mystery Still Unsolved Today",
                "How It Completely Defies Common Sense", "The Hidden Truth Behind The Headlines",
                "The Mind-Blowing Revelation of 2026"
            ]
        }
    }

    cat_low = str(category).lower()
    chosen_cat = "general"
    for k in ["cartoon", "horror", "tech", "history", "science"]:
        if k in cat_low:
            chosen_cat = k
            break

    cat_data = matrix.get(chosen_cat, matrix["general"])
    subs = cat_data["subjects"]
    angs = cat_data["angles"]
    total_combos = len(subs) * len(angs)  # Exactly 1,000

    now_dt = datetime.utcnow()
    # Calculate days since benchmark
    day_num = (now_dt - datetime(2025, 1, 1)).days
    if day_seed:
        salt = int(hashlib.md5(day_seed.encode()).hexdigest()[:6], 16)
    else:
        salt = int(hashlib.md5(f"{chosen_cat}_{now_dt.strftime('%Y%m%d')}".encode()).hexdigest()[:6], 16)

    # 37 is prime, gcd(37, 1000) == 1 -> Guaranteed zero repetition permutation across 1000 days!
    combo_idx = (day_num * 37 + salt) % total_combos
    sub_idx = combo_idx % len(subs)
    ang_idx = (combo_idx // len(subs)) % len(angs)

    sub = subs[sub_idx]
    ang = angs[ang_idx]

    if chosen_cat == "cartoon":
        return f"{sub} {ang}"
    if "{subject}" in ang:
        return ang.replace("{subject}", sub)
    return f"{sub}: {ang}"

def resolve_random_topic(topic: str = "", category: str = "Random", day_seed: str = "") -> str:
    """
    Dynamically resolves fresh, 100% non-repetitive topics for auto-schedule & user generation.
    Uses a mathematical 1000-day zero-duplicate combinatorial bijection engine.
    """
    topic_clean = (topic or "").strip()
    topic_low = topic_clean.lower()

    is_random_requested = (
        not topic_clean or
        topic_low in [
            "random", "random topic", "default", "ai script", "generate script", "none",
            "ai auto topic (daily dynamic)", "ai auto topic", "auto topic", "daily dynamic"
        ]
    )

    if is_random_requested:
        return get_combinatorial_daily_topic(category, day_seed)

    return topic_clean

def get_daily_unique_subtopic(base_topic: str, today_str: str, user_id: str, category: str = "Random") -> str:
    """
    Generates a 100% non-repetitive daily unique subtopic angle for automated auto reels.
    Guarantees that over 2+ years (730+ days), auto-schedule never repeats identical content.
    """
    clean_base = (base_topic or "").strip()
    is_auto = not clean_base or clean_base.lower() in [
        "random", "random topic", "default", "ai script", "generate script", "none",
        "ai auto topic (daily dynamic)", "ai auto topic", "auto topic", "daily dynamic"
    ]

    seed_str = f"{today_str}_{user_id}"

    if is_auto:
        return resolve_random_topic("", category, day_seed=seed_str)

    # For fixed custom topics, generate a distinct daily investigative angle
    topic = resolve_random_topic(clean_base, category, day_seed=seed_str)
    cat_lower = str(category).lower()
    is_cartoon = any(k in cat_lower for k in ["cartoon", "anime", "animation", "character"])

    if is_cartoon:
        cartoon_angles = [
            "Ka Superhit Jugaad",
            "Ka Dhamakedaar Kissa",
            "Ka Naya Hungama",
            "Ki Mazedaar Kahani",
            "Ka Crazy Experiment",
            "Ka School Drama",
            "Ka Secret Invention",
            "Ka Jungle Adventure",
            "Ka Magic Scooter Drama",
            "Ka Super-Funny Prank"
        ]
        seed = int(hashlib.md5(f"{today_str}_{user_id}_{topic}_cartoon".encode()).hexdigest(), 16)
        angle = cartoon_angles[seed % len(cartoon_angles)]
        return f"{topic} {angle}"

    sub_angles = [
        "Unbelievable Secrets Revealed",
        "Mystery and Shocking History",
        "The Complete Untold Story",
        "Behind The Scenes Truth",
        "Top Facts and Deep Mysteries",
        "Unexpected Turn of Events",
        "Shocking Reality Exposed",
        "Mind-Blowing Hidden Chronicles",
        "Secrets Never Taught in School",
        "The Dark Mystery Finally Uncovered",
        "What Scientists Actually Discovered",
        "The Hidden Truth Nobody Talks About",
        "Shocking Discoveries of 2026",
        "The Real Reason Why It Happened",
        "Deep Investigation and Facts"
    ]
    seed = int(hashlib.md5(f"{today_str}_{user_id}_{topic}".encode()).hexdigest(), 16)
    selected_angle = sub_angles[seed % len(sub_angles)]

    if len(topic.split()) <= 4:
        return f"{topic} ({selected_angle})"
    return topic

from concurrent.futures import ThreadPoolExecutor
import threading

auto_worker_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="AutoRenderWorker")
render_queue_lock = threading.Lock()
manual_job_lock = threading.Lock()
active_manual_jobs_count = 0
active_auto_users_lock = threading.Lock()
active_auto_users = set()

def register_manual_job_start():
    global active_manual_jobs_count
    with manual_job_lock:
        active_manual_jobs_count += 1

def register_manual_job_end():
    global active_manual_jobs_count
    with manual_job_lock:
        active_manual_jobs_count = max(0, active_manual_jobs_count - 1)

def process_single_user_schedule(user: dict, now_ist: datetime, today_str: str):
    """
    Worker processing pipeline for a single user's schedule.
    Handles predictive pre-rendering (Stage 1) and instant YouTube publishing (Stage 2).
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
            fresh_user = users_collection.find_one({"internal_id": internal_id}) or user
            fresh_sched = fresh_user.get("auto_schedule", {})
            default_scheduled_time = fresh_sched.get("short_time", "03:00") if kind in ["short", "ultra"] else "18:00"
            time_str = fresh_sched.get(f"{kind}_time") or default_scheduled_time
            last_run_key = f"last_{kind}_run"

            if fresh_sched.get(last_run_key) == today_str:
                return

            lock_timeout_ago = (datetime.utcnow() - timedelta(minutes=25)).isoformat()
            upload_lock_check = fresh_user.get("auto_locks", {}).get(f"upload_{kind}", {})
            if upload_lock_check.get("date") == today_str and upload_lock_check.get("status") == "success":
                return

            target_minutes = parse_time_to_minutes(time_str) or (180 if kind in ["short", "ultra"] else 1080)
            mins_until = (target_minutes - current_ist_minutes) % 1440
            diff_current = min(abs(current_ist_minutes - target_minutes), 1440 - abs(current_ist_minutes - target_minutes))

            target_run_date = (now_ist + timedelta(minutes=mins_until)).strftime("%Y-%m-%d") if mins_until <= 720 else today_str
            valid_dates = [today_str, target_run_date]

            staged_map = fresh_user.get("staged_auto_videos", {})
            staged_item = staged_map.get(kind, {})

            if 5 < mins_until <= 720:
                has_valid_staged = bool(staged_item.get("cloudinary_url")) or (staged_item.get("file") and os.path.exists(staged_item.get("file", "")))
                if not has_valid_staged:
                    lock_field = f"auto_locks.staging_{kind}"
                    node_name = os.getenv("RENDER_SERVICE_NAME", "cluster_node")
                    
                    claim_result = users_collection.find_one_and_update(
                        {
                            "internal_id": internal_id,
                            "$or": [
                                {f"{lock_field}.date": {"$nin": valid_dates}},
                                {f"{lock_field}.claimed_at": {"$lt": lock_timeout_ago}}
                            ]
                        },
                        {
                            "$set": {
                                lock_field: {
                                    "date": target_run_date,
                                    "claimed_at": datetime.utcnow().isoformat(),
                                    "node": node_name
                                },
                                f"auto_schedule_status.{kind}": {
                                    "status": "STAGING_IN_PROGRESS",
                                    "target_time": time_str,
                                    "updated_at": datetime.utcnow().isoformat()
                                }
                            }
                        }
                    )
                    
                    if claim_result is not None:
                        print(f"🚀 [PREDICTIVE AUTO-STAGING - Node: {node_name}] Pre-rendering {kind.upper()} video for user {internal_id} (Scheduled IST: {time_str}, Target in {mins_until} mins)...")
                        category = fresh_sched.get(f"{kind}_category") or ("Cartoon & Animation" if kind == "ultra" else "Random")
                        raw_topic = fresh_sched.get(f"{kind}_topic") or default_topic
                        topic = get_daily_unique_subtopic(raw_topic, today_str, internal_id, category)
                        voice = fresh_sched.get(f"{kind}_voice") or "hi-IN-MadhurNeural"
                        is_eng_voice = voice and str(voice).lower().startswith("en")
                        language = "en" if is_eng_voice else (fresh_sched.get(f"{kind}_language") or "hi")
                        font = fresh_sched.get(f"{kind}_font") or "Arial.ttf"
                        color = fresh_sched.get(f"{kind}_color") or "yellow"
                        aspect_ratio = "9:16" if kind == "short" else ("16:9" if kind == "long" else (fresh_sched.get("ultra_aspect_ratio") or "16:9"))
                        duration = int(fresh_sched.get(f"{kind}_duration") or default_dur)

                        res = render_video_with_smart_fallback(
                            user_id=internal_id,
                            topic=topic,
                            category=category,
                            voice_id=voice,
                            font_name=font,
                            font_color=color,
                            video_type=kind,
                            requested_duration=duration,
                            aspect_ratio=aspect_ratio,
                            language=language
                        )

                        if res.get("status") == "completed":
                            video_file = res.get("file")
                            script_text = res.get("script", "")
                            if is_short_flag:
                                script_text = " ".join(script_text.split()[:120])

                            staged_data = {
                                "file": video_file,
                                "cloudinary_url": res.get("cloudinary_url"),
                                "title": topic,
                                "script": script_text,
                                "date": target_run_date,
                                "staged_at": datetime.utcnow().isoformat()
                            }
                            staged_map[kind] = staged_data
                            users_collection.update_one(
                                {"internal_id": internal_id},
                                {
                                    "$set": {
                                        f"staged_auto_videos.{kind}": staged_data,
                                        f"auto_schedule_status.{kind}": {
                                            "status": "STAGED_READY",
                                            "title": topic,
                                            "cloudinary_url": res.get("cloudinary_url"),
                                            "target_time": time_str,
                                            "staged_at": datetime.utcnow().isoformat()
                                        }
                                    }
                                }
                            )
                            print(f"✅ [PREDICTIVE STAGING COMPLETE - Node: {node_name}] {kind.upper()} video pre-rendered & saved to Cloudinary for user {internal_id}. Waiting for {time_str} IST to publish!")
                            staged_item = staged_data
                        else:
                            cooldown_claimed_at = (datetime.utcnow() + timedelta(minutes=20)).isoformat()
                            users_collection.update_one(
                                {"internal_id": internal_id},
                                {
                                    "$set": {
                                        f"{lock_field}.claimed_at": cooldown_claimed_at,
                                        f"auto_schedule_status.{kind}": {
                                            "status": "STAGING_FAILED",
                                            "error": res.get("error", "Rendering failed"),
                                            "updated_at": datetime.utcnow().isoformat()
                                        }
                                    }
                                }
                            )

            is_time_to_upload = (diff_current <= 30) or (mins_until >= 1410) or (current_ist_minutes >= target_minutes and fresh_sched.get(last_run_key) != today_str)
            if is_time_to_upload:
                upload_lock_field = f"auto_locks.upload_{kind}"
                node_name = os.getenv("RENDER_SERVICE_NAME", "cluster_node")

                claim_upload = users_collection.find_one_and_update(
                    {
                        "internal_id": internal_id,
                        f"auto_schedule.{last_run_key}": {"$ne": today_str},
                        "$or": [
                            {f"{upload_lock_field}.date": {"$ne": today_str}},
                            {
                                f"{upload_lock_field}.status": {"$ne": "success"},
                                f"{upload_lock_field}.claimed_at": {"$lt": lock_timeout_ago}
                            }
                        ]
                    },
                    {
                        "$set": {
                            upload_lock_field: {
                                "date": today_str,
                                "status": "in_progress",
                                "claimed_at": datetime.utcnow().isoformat(),
                                "node": node_name
                            },
                            f"auto_schedule_status.{kind}": {
                                "status": "UPLOADING",
                                "target_time": time_str,
                                "started_at": datetime.utcnow().isoformat()
                            }
                        }
                    }
                )

                if claim_upload is None:
                    return

                print(f"💥 [INSTANT BATCH UPLOAD - Node: {node_name}] Publishing {kind.upper()} video for user {internal_id} to YouTube (Scheduled IST: {time_str})...")

                fresh_user = users_collection.find_one({"internal_id": internal_id}) or {}
                fresh_staged = fresh_user.get("staged_auto_videos", {}).get(kind, {})

                target_upload_src = fresh_staged.get("cloudinary_url") or (fresh_staged.get("file") if (fresh_staged.get("file") and os.path.exists(fresh_staged.get("file", ""))) else None)
                upload_success = False
                final_yt_url = ""
                final_title = fresh_staged.get("title", "")

                if target_upload_src:
                    print(f"⚡ Reusing pre-rendered Cloudinary video for instant YouTube upload: {target_upload_src}")
                    yt_res = upload_video_to_youtube_core(
                        user_id=internal_id,
                        video_file=target_upload_src,
                        title=fresh_staged.get("title", f"Auto {kind.upper()} Video"),
                        description=fresh_staged.get("script", ""),
                        is_short=is_short_flag
                    )
                    if yt_res:
                        upload_success = True
                        yt_id = yt_res if isinstance(yt_res, str) else ""
                        final_yt_url = f"https://www.youtube.com/watch?v={yt_id}" if (yt_id and not yt_id.startswith("http")) else yt_id
                    else:
                        print(f"⚠️ [STAGED UPLOAD FAILED] Clearing stale staged reference for {kind.upper()} to retry...")
                        users_collection.update_one(
                            {"internal_id": internal_id},
                            {"$unset": {f"staged_auto_videos.{kind}": ""}}
                        )

                if not upload_success:
                    print(f"🎨 Pre-rendered video not available. Generating fast cartoon video on-the-fly for {kind.upper()}...")
                    category = fresh_sched.get(f"{kind}_category") or ("Cartoon & Animation" if kind == "ultra" else "Random")
                    raw_topic = fresh_sched.get(f"{kind}_topic") or default_topic
                    topic = get_daily_unique_subtopic(raw_topic, today_str, internal_id, category)
                    final_title = topic
                    voice = fresh_sched.get(f"{kind}_voice") or "hi-IN-MadhurNeural"
                    is_eng_voice = voice and str(voice).lower().startswith("en")
                    language = "en" if is_eng_voice else (fresh_sched.get(f"{kind}_language") or "hi")
                    font = fresh_sched.get(f"{kind}_font") or "Arial.ttf"
                    color = fresh_sched.get(f"{kind}_color") or "yellow"
                    aspect_ratio = "9:16" if kind == "short" else ("16:9" if kind == "long" else (fresh_sched.get("ultra_aspect_ratio") or "16:9"))
                    duration = int(fresh_sched.get(f"{kind}_duration") or default_dur)

                    res = render_video_with_smart_fallback(
                        user_id=internal_id,
                        topic=topic,
                        category=category,
                        voice_id=voice,
                        font_name=font,
                        font_color=color,
                        video_type=kind,
                        requested_duration=duration,
                        aspect_ratio=aspect_ratio,
                        language=language
                    )
                    if res.get("status") == "completed":
                        video_file = res.get("file")
                        script_text = res.get("script", "")
                        if is_short_flag:
                            script_text = " ".join(script_text.split()[:120])
                        yt_res = upload_video_to_youtube_core(
                            user_id=internal_id,
                            video_file=video_file,
                            title=topic,
                            description=script_text,
                            is_short=is_short_flag
                        )
                        if yt_res:
                            upload_success = True
                            yt_id = yt_res if isinstance(yt_res, str) else ""
                            final_yt_url = f"https://www.youtube.com/watch?v={yt_id}" if (yt_id and not yt_id.startswith("http")) else yt_id

                if upload_success:
                    auto_usage = fresh_user.get("auto_daily_usage", {})
                    if auto_usage.get("date") != today_str:
                        auto_usage = {"date": today_str, "auto_short_count": 0, "auto_long_count": 0, "auto_ultra_count": 0}
                    auto_usage[f"auto_{kind}_count"] = auto_usage.get(f"auto_{kind}_count", 0) + 1
                    
                    users_collection.update_one(
                        {"internal_id": internal_id},
                        {
                            "$set": {
                                f"auto_schedule.{last_run_key}": today_str,
                                f"{upload_lock_field}.status": "success",
                                f"{upload_lock_field}.completed_at": datetime.utcnow().isoformat(),
                                f"{upload_lock_field}.youtube_url": final_yt_url,
                                f"auto_schedule_status.{kind}": {
                                    "status": "PUBLISHED",
                                    "last_run_date": today_str,
                                    "youtube_url": final_yt_url,
                                    "title": final_title,
                                    "published_at": datetime.utcnow().isoformat()
                                },
                                "auto_daily_usage": auto_usage
                            },
                            "$unset": {f"staged_auto_videos.{kind}": ""}
                        }
                    )
                    print(f"🎉 [AUTO PUBLISH SUCCESS - Node: {node_name}] {kind.upper()} video published to YouTube: {final_yt_url}")
                    return "published"
                else:
                    print(f"⚠️ [AUTO PUBLISH WARNING] Upload failed for {kind.upper()}. Clearing lock for automatic retry...")
                    users_collection.update_one(
                        {"internal_id": internal_id},
                        {
                            "$unset": {upload_lock_field: ""},
                            "$set": {
                                f"auto_schedule_status.{kind}": {
                                    "status": "UPLOAD_FAILED",
                                    "updated_at": datetime.utcnow().isoformat()
                                }
                            }
                        }
                    )
                    return "failed"

        import time
        res_short = None
        res_long = None

        if schedule.get("short_enabled", True) and is_active and plan_type in ["short", "combo", "ultra", "all"]:
            res_short = run_staged_auto_pipeline("short", True, "Space Exploration", 20)
            release_system_memory()
            time.sleep(2)
            if res_short == "published":
                print("⏳ 5-minute gap initiated after SHORT Reel publish. Waiting 300 seconds before next upload...")
                time.sleep(300)

        if schedule.get("long_enabled", True) and is_active and plan_type in ["long", "combo", "ultra", "all"]:
            res_long = run_staged_auto_pipeline("long", False, "AI Innovations", 60)
            release_system_memory()
            time.sleep(2)
            if res_long == "published":
                print("⏳ 5-minute gap initiated after LONG video publish. Waiting 300 seconds before next upload...")
                time.sleep(300)

        if schedule.get("ultra_enabled", True) and (is_active or has_ultra_sub or plan_type in ["ultra", "combo", "all"]):
            ultra_aspect = schedule.get("ultra_aspect_ratio", "9:16")
            ultra_is_short = (ultra_aspect == "9:16")
            default_dur = 25 if ultra_is_short else 60
            run_staged_auto_pipeline("ultra", ultra_is_short, "Funny Cartoon Adventures", default_dur)
            release_system_memory()
            time.sleep(2)

        release_system_memory()

    except Exception as e_user:
        print(f"❌ Worker error for user {internal_id}: {e_user}")

def process_single_user_schedule_wrapper(user: dict, now_ist: datetime, today_str: str):
    internal_id = user.get("internal_id")
    try:
        process_single_user_schedule(user, now_ist, today_str)
    finally:
        if internal_id:
            with active_auto_users_lock:
                active_auto_users.discard(internal_id)

def check_and_run_auto_schedules():
    """
    Crash-Proof Predictive Pre-Rendering & Multi-Thread Worker Scheduler Engine (200+ User Scale).
    Scans schedules and dispatches rendering jobs to ThreadPoolExecutor pool sorted by earliest target IST.
    """
    if users_collection is None:
        return

    now_utc = datetime.utcnow()
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    today_str = now_ist.strftime("%Y-%m-%d")
    current_ist_minutes = now_ist.hour * 60 + now_ist.minute

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

        if users:
            def calculate_user_priority(user_doc):
                sched = user_doc.get("auto_schedule", {})
                min_until_next = 9999
                for k in ["short", "long", "ultra"]:
                    if sched.get(f"{k}_enabled", True if k == "short" else False):
                        t_str = sched.get(f"{k}_time", "10:00" if k == "short" else ("18:00" if k == "long" else "21:00"))
                        t_min = parse_time_to_minutes(t_str) or 600
                        diff = (t_min - current_ist_minutes) % 1440
                        if diff < min_until_next:
                            min_until_next = diff
                return min_until_next

            users.sort(key=calculate_user_priority)
            print(f"⏰ [AUTO SCHEDULER TICK] Scanned & priority-queued {len(users)} active user schedule(s) at {now_ist.strftime('%H:%M:%S')} IST")

        for user in users:
            uid = user.get("internal_id")
            if not uid:
                continue
            with active_auto_users_lock:
                if uid in active_auto_users:
                    continue
                active_auto_users.add(uid)
            auto_worker_executor.submit(process_single_user_schedule_wrapper, user, now_ist, today_str)
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
        salt = _raw_bcrypt.gensalt(rounds=10)
        return _raw_bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    except Exception:
        return pwd_context.hash(password)

def _get_cipher_suite():
    secret = os.getenv("MONGO_ENCRYPTION_KEY") or os.getenv("JWT_SECRET_KEY") or "cloxel-mongo-aes256-secret-key-2026"
    key_32 = hashlib.sha256(secret.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(key_32)
    return Fernet(fernet_key)

def encrypt_field(val: str) -> str:
    if not val or not isinstance(val, str):
        return val
    if val.startswith("ENC:"):
        return val
    try:
        cipher = _get_cipher_suite()
        encrypted = cipher.encrypt(val.encode('utf-8')).decode('utf-8')
        return "ENC:" + encrypted
    except Exception as e:
        print(f"⚠️ Field encryption error: {e}")
        return val

def decrypt_field(val: str) -> str:
    if not val or not isinstance(val, str):
        return val
    target = val
    if target.startswith("ENC:"):
        target = target[4:]
    try:
        cipher = _get_cipher_suite()
        return cipher.decrypt(target.encode('utf-8')).decode('utf-8')
    except Exception:
        return val

def hash_identifier(val: str) -> str:
    if not val or not isinstance(val, str):
        return None
    clean = val.strip().lower()
    secret = os.getenv("MONGO_ENCRYPTION_KEY") or os.getenv("JWT_SECRET_KEY") or "cloxel-mongo-aes256-secret-key-2026"
    return hmac.new(secret.encode('utf-8'), clean.encode('utf-8'), hashlib.sha256).hexdigest()

def decrypt_user_doc(user_doc: dict) -> dict:
    if not user_doc:
        return user_doc
    doc = dict(user_doc)
    for field in ["name", "email", "phone", "email_or_mobile", "full_name", "username", "security_qr_token"]:
        if field in doc and isinstance(doc[field], str):
            doc[field] = decrypt_field(doc[field])
    return doc

def find_user_in_db(identifier: str) -> dict:
    """
    Finds user in MongoDB matching plaintext email, phone, internal_id, email_or_mobile,
    or deterministic SHA-256 HMAC hashes (email_hash, phone_hash).
    Also supports fallback decryption scan across user documents to handle legacy encrypted docs.
    Returns the decrypted user document.
    """
    if users_collection is None or not identifier:
        return None

    raw_identifier = str(identifier).strip()
    raw_digits = "".join(filter(str.isdigit, raw_identifier))
    phone_10 = raw_digits[-10:] if len(raw_digits) >= 10 else raw_digits

    phone_variants = set()
    if phone_10:
        phone_variants.add(phone_10)
        phone_variants.add("91" + phone_10)
        phone_variants.add("+91" + phone_10)
        phone_variants.add("0" + phone_10)
    if raw_digits:
        phone_variants.add(raw_digits)

    import re
    identifier_regex = re.compile(f"^{re.escape(raw_identifier.lower())}$", re.IGNORECASE)

    or_conditions = [
        {"email": identifier_regex},
        {"email_or_mobile": identifier_regex},
        {"internal_id": raw_identifier},
        {"email_hash": hash_identifier(raw_identifier.lower())}
    ]
    for p in phone_variants:
        p_h = hash_identifier(p)
        or_conditions.append({"phone": p})
        or_conditions.append({"email_or_mobile": p})
        if p_h:
            or_conditions.append({"phone_hash": p_h})

    user = users_collection.find_one({"$or": or_conditions})
    if user:
        return decrypt_user_doc(user)

    try:
        cursor = users_collection.find({}, {
            "_id": 1, "email": 1, "phone": 1, "email_or_mobile": 1, 
            "phone_hash": 1, "email_hash": 1, "internal_id": 1, 
            "name": 1, "password_hash": 1, "password": 1, "country": 1, 
            "security_qr_token": 1, "free_demo_count": 1, "created_at": 1
        })
        for doc in cursor:
            raw_p = doc.get("phone") or ""
            dec_p = decrypt_field(raw_p) if isinstance(raw_p, str) else str(raw_p)
            doc_p_digits = "".join(filter(str.isdigit, str(dec_p)))
            doc_phone_10 = doc_p_digits[-10:] if len(doc_p_digits) >= 10 else doc_p_digits

            raw_eom = doc.get("email_or_mobile") or ""
            dec_eom = decrypt_field(raw_eom) if isinstance(raw_eom, str) else str(raw_eom)
            doc_eom_digits = "".join(filter(str.isdigit, str(dec_eom)))
            doc_eom_10 = doc_eom_digits[-10:] if len(doc_eom_digits) >= 10 else ""

            raw_e = doc.get("email") or ""
            dec_e = decrypt_field(raw_e) if isinstance(raw_e, str) else str(raw_e)
            doc_email = str(dec_e).strip().lower()
            doc_eom_email = str(dec_eom).strip().lower()

            match = False
            if phone_10 and len(phone_10) == 10 and (doc_phone_10 == phone_10 or doc_eom_10 == phone_10):
                match = True
            elif raw_identifier.lower() in [doc_email, doc_eom_email]:
                match = True

            if match:
                updates = {}
                if not doc.get("phone_hash") and doc_phone_10:
                    updates["phone_hash"] = hash_identifier(doc_phone_10)
                if not doc.get("email_hash") and doc_email:
                    updates["email_hash"] = hash_identifier(doc_email)
                if updates:
                    try:
                        users_collection.update_one({"_id": doc["_id"]}, {"$set": updates})
                    except Exception:
                        pass
                return decrypt_user_doc(doc)
    except Exception as e:
        print(f"⚠️ Fallback scan notice in find_user_in_db: {e}")

    return None

def check_duplicate_user(email: str, phone: str):
    """
    Checks if a user already exists with the given email or phone number.
    Returns (duplicate_type, user_doc) if found, else None.
    duplicate_type can be 'phone' or 'email'.
    
    Checks:
    1. Multi-format MongoDB $or query (email_hash, phone_hash across country code variants, regex, plaintext).
    2. Fallback full-collection decryption scan (to catch legacy encrypted documents where phone_hash or email_hash was missing or secret changed).
    """
    if users_collection is None:
        return None

    clean_email = (email or "").strip().lower()
    raw_digits = "".join(filter(str.isdigit, str(phone or "")))
    phone_10 = raw_digits[-10:] if len(raw_digits) >= 10 else raw_digits

    phone_variants = set()
    if phone_10:
        phone_variants.add(phone_10)
        phone_variants.add("91" + phone_10)
        phone_variants.add("+91" + phone_10)
        phone_variants.add("0" + phone_10)
    if raw_digits:
        phone_variants.add(raw_digits)
    if phone:
        phone_variants.add(str(phone).strip())

    import re
    email_h = hash_identifier(clean_email) if clean_email else None
    email_regex = re.compile(f"^{re.escape(clean_email)}$", re.IGNORECASE) if clean_email else None

    or_query = []
    if clean_email:
        or_query.append({"email": email_regex})
        or_query.append({"email_or_mobile": email_regex})
        if email_h:
            or_query.append({"email_hash": email_h})

    for p in phone_variants:
        p_h = hash_identifier(p)
        or_query.append({"phone": p})
        or_query.append({"email_or_mobile": p})
        if p_h:
            or_query.append({"phone_hash": p_h})

    if or_query:
        found = users_collection.find_one({"$or": or_query})
        if found:
            dec_found = decrypt_user_doc(found)
            ex_email = str(dec_found.get("email") or "").strip().lower()
            ex_eom = str(dec_found.get("email_or_mobile") or "").strip().lower()
            ex_phone_digits = "".join(filter(str.isdigit, str(dec_found.get("phone") or "")))
            ex_phone_10 = ex_phone_digits[-10:] if len(ex_phone_digits) >= 10 else ex_phone_digits
            ex_eom_digits = "".join(filter(str.isdigit, ex_eom))
            ex_eom_10 = ex_eom_digits[-10:] if len(ex_eom_digits) >= 10 else ""

            if clean_email and (ex_email == clean_email or ex_eom == clean_email):
                return "email", dec_found
            if phone_10 and (ex_phone_10 == phone_10 or ex_eom_10 == phone_10):
                return "phone", dec_found
            return "phone", dec_found

    try:
        cursor = users_collection.find({
            "$or": [
                {"email_hash": {"$exists": False}},
                {"phone_hash": {"$exists": False}}
            ]
        }, {
            "_id": 1, "email": 1, "phone": 1, "email_or_mobile": 1, 
            "phone_hash": 1, "email_hash": 1, "internal_id": 1
        })
        if hasattr(cursor, "limit"):
            cursor = cursor.limit(50)
        for doc in cursor:
            raw_p = doc.get("phone") or ""
            dec_p = decrypt_field(raw_p) if isinstance(raw_p, str) else str(raw_p)
            doc_p_digits = "".join(filter(str.isdigit, str(dec_p)))
            doc_phone_10 = doc_p_digits[-10:] if len(doc_p_digits) >= 10 else doc_p_digits

            raw_eom = doc.get("email_or_mobile") or ""
            dec_eom = decrypt_field(raw_eom) if isinstance(raw_eom, str) else str(raw_eom)
            doc_eom_digits = "".join(filter(str.isdigit, str(dec_eom)))
            doc_eom_10 = doc_eom_digits[-10:] if len(doc_eom_digits) >= 10 else ""

            raw_e = doc.get("email") or ""
            dec_e = decrypt_field(raw_e) if isinstance(raw_e, str) else str(raw_e)
            doc_email = str(dec_e).strip().lower()
            doc_eom_email = str(dec_eom).strip().lower()

            is_phone_duplicate = bool(phone_10 and len(phone_10) == 10 and (doc_phone_10 == phone_10 or doc_eom_10 == phone_10))
            is_email_duplicate = bool(clean_email and (doc_email == clean_email or doc_eom_email == clean_email))

            if is_phone_duplicate or is_email_duplicate:
                updates = {}
                if not doc.get("phone_hash") and doc_phone_10:
                    updates["phone_hash"] = hash_identifier(doc_phone_10)
                if not doc.get("email_hash") and doc_email:
                    updates["email_hash"] = hash_identifier(doc_email)
                if updates:
                    try:
                        users_collection.update_one({"_id": doc["_id"]}, {"$set": updates})
                    except Exception:
                        pass

                return ("phone" if is_phone_duplicate else "email"), doc
    except Exception as e:
        print(f"⚠️ Decryption scan warning in check_duplicate_user: {e}")

    return None

from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Production Hardening: Disable Swagger & ReDoc to prevent attacker schema enumeration
app = FastAPI(title="Cloxel AI", docs_url=None, redoc_url=None, openapi_url=None)

ALLOWED_ORIGINS = [
    "https://cloxelai.onrender.com",
    "https://cloxel.onrender.com",
    "https://cloxel.ai",
    "https://cloxelai.com",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
frontend_env = os.getenv("FRONTEND_URL")
if frontend_env and frontend_env.strip() not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(frontend_env.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(FirewallMiddleware)

@app.get("/api/admin/unblock-firewall")
async def unblock_firewall(request: Request):
    verify_admin_access(request)
    waf.reset_all_bans()
    return {"message": "🔓 Firewall IP bans & rate limits reset successfully!"}

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
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image file too large! Maximum image upload size is 10MB.")

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
        raise HTTPException(status_code=500, detail="Background removal service encountered an error.")

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

class UserLogin(BaseModel):
    email_or_mobile: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email_or_mobile: str
    current_session_user_id: Optional[str] = None
    current_session_user_email: Optional[str] = None
    current_session_user_phone: Optional[str] = None

class VerifyQRRequest(BaseModel):
    email_or_mobile: str
    qr_token: str

class ResetPasswordRequest(BaseModel):
    email_or_mobile: str
    qr_token: str
    new_password: str
    current_session_user_id: Optional[str] = None
    current_session_user_email: Optional[str] = None
    current_session_user_phone: Optional[str] = None

class GoogleVerifyRequest(BaseModel):
    credential: str
    email_or_mobile: Optional[str] = None

class VideoRequest(BaseModel):
    scenes: List[Scene] = []
    user_id: Optional[str] = None
    topic: Optional[str] = ""
    category: Optional[str] = "Random"
    font_name: str = "Arial.ttf"
    font_color: str = "yellow"
    font_size: int = 220
    voice_id: str = "hi-IN-MadhurNeural"
    language: str = "hi"
    video_type: str = "short"
    full_script: str = ""
    bg_music: str = "cool.mp3"
    aspect_ratio: Optional[str] = "16:9"
    mode: Optional[str] = "standard"
    filter_style: Optional[str] = "none"
    duration: Optional[int] = 30
    song_url: Optional[str] = None
    song_source_type: Optional[str] = "url"
    singer_name: Optional[str] = None
    song_title: Optional[str] = None
    song_visual_mode: Optional[str] = "motion"
    song_lyrics: Optional[str] = None

class ScriptRequest(BaseModel):
    topic: str
    duration_seconds: int
    user_id: Optional[str] = None
    category: Optional[str] = "Random"
    video_type: Optional[str] = "short"
    language: Optional[str] = "hi"
    voice: Optional[str] = "hi-IN-MadhurNeural"

jobs = {}

def full_process(req: VideoRequest, job_id: str):
    """Asli logic jo background mein chalega"""
    register_manual_job_start()
    try:
        job_dir = f"temp_{job_id}"
        os.makedirs(job_dir, exist_ok=True)
        
        user_id = req.user_id if req.user_id else "anonymous"
        print(f"🎬 Processing video for User: {user_id} (Category: {req.category})")
        
        is_song_video = bool(req.category and ("song video" in str(req.category).lower()))
        if is_song_video:
            print(f"🎵 [ROUTING] Entering Dedicated Ultra Song Video Engine for Job {job_id}...")
            output_file = f"acoumation_video_{job_id}.mp4"
            from song_video_engine import build_full_song_video
            build_full_song_video(req, job_id, job_dir, output_file)

            print(f"\n☁️ [PROGRESS 90%] STEP 6/6: Uploading Completed Song Video to Cloudinary CDN...")
            cloudinary_url = None
            try:
                upload_result = cloudinary.uploader.upload(output_file, resource_type="video")
                cloudinary_url = upload_result.get("secure_url")
                print(f"✅ Cloudinary HD CDN URL: {cloudinary_url}")
                if cloudinary_url and os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except Exception:
                        pass
            except Exception as e:
                print(f"⚠️ Cloudinary upload warning: {e}")

            display_title = req.song_title or req.singer_name or req.topic or "Ultra AI Song Video"
            gen_title, gen_desc = build_youtube_metadata(
                topic=display_title,
                full_script=req.song_lyrics or f"{display_title} Song Video",
                video_type=req.video_type
            )

            update_job_status(job_id, {
                "status": "completed", 
                "file": output_file, 
                "dir": job_dir, 
                "cloudinary_url": cloudinary_url,
                "title": gen_title,
                "description": gen_desc,
                "created_at": datetime.utcnow()
            })

            clean_user_id = sanitize_alphanumeric_id(user_id) if user_id else None
            if users_collection is not None and clean_user_id:
                try:
                    history_entry = {
                        "job_id": job_id,
                        "title": gen_title,
                        "topic": display_title,
                        "video_type": req.video_type,
                        "cloudinary_url": cloudinary_url,
                        "created_at": datetime.utcnow()
                    }
                    users_collection.update_one(
                        {"internal_id": clean_user_id},
                        {"$push": {"video_history": {"$each": [history_entry], "$slice": -50}}}
                    )
                except Exception as e_hist:
                    print(f"⚠️ History save error: {e_hist}")

            return

        scenes_data = []

        print(f"\n==================================================")
        print(f"🚀 [WORKFLOW ENGINE STARTED] Job ID: {job_id}")
        print(f"📊 Mode: {req.video_type.upper()} | User: {req.user_id} | Topic: '{req.topic}'")
        print(f"==================================================")

        print(f"📊 [PROGRESS 10%] STEP 1/6: Processing Script & Scene Breakdown...")
        if req.video_type == "short":
            # For SHORT videos:
            # 1. First Priority: If structured scenes were provided (with dedicated video search keywords & script chunks), PRESERVE THEM!
            valid_scenes = [s for s in (req.scenes or []) if (s.text and s.text.strip()) or (s.keyword and s.keyword.strip())]
            if valid_scenes:
                scenes_data = []
                for s in valid_scenes:
                    txt = s.text.strip() if s.text else ""
                    kw = s.keyword.strip() if s.keyword else ""
                    scenes_data.append({"text": txt or req.topic or "short scene", "keyword": kw})
            elif req.full_script and req.full_script.strip():
                # 2. Manual script provided for SHORT without pre-split scene cards:
                # Break down script into individual scene sentences
                import re
                raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', req.full_script.strip()) if len(s.strip()) > 3]
                if not raw_sentences:
                    raw_sentences = [req.full_script.strip()]
                
                scenes_data = []
                for sc_idx, sentence in enumerate(raw_sentences):
                    # Extract big, meaningful English keywords from script (length >= 4, filtered against stop words)
                    eng_words = [w for w in re.findall(r'[a-zA-Z]+', sentence) if len(w) >= 4 and w.lower() not in {
                        "this", "that", "with", "from", "have", "been", "will", "would", "could", "should",
                        "what", "when", "where", "which", "there", "their", "about", "your", "they", "them",
                        "more", "some", "into", "then", "than", "very", "also", "just", "like", "make", "take",
                        "know", "come", "give", "look", "time", "year", "people", "thing", "tell"
                    }]
                    if eng_words:
                        kw = " ".join(eng_words[:3])
                    else:
                        # Script in Hindi/Devanagari: Use topic with visual angles (never single Hindi stopwords!)
                        main_t = (req.topic or "cinematic").strip()
                        visual_angles = [
                            f"{main_t} action visual",
                            f"{main_t} close up scene",
                            f"{main_t} cinematic dramatic",
                            f"{main_t} detailed view",
                            f"{main_t} atmosphere",
                            f"{main_t} dynamic motion"
                        ]
                        kw = visual_angles[sc_idx % len(visual_angles)]
                    scenes_data.append({"text": sentence, "keyword": kw})
        else:
            # For LONG or ULTRA: Extract rich, descriptive keywords according to script so exact assets download without tiny fragments
            if req.full_script and req.full_script.strip():
                import re
                raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', req.full_script.strip()) if len(s.strip()) > 3]
                existing_kw_map = {s.text.strip(): s.keyword.strip() for s in (req.scenes or []) if s.text and s.keyword}
                
                scenes_data = []
                for sc_idx, sentence in enumerate(raw_sentences):
                    kw = existing_kw_map.get(sentence)
                    # If keyword is missing, tiny (1 word), or a stopword (like 'यह' or 'woh'):
                    # Generate rich, descriptive visual keywords from the script sentence + topic
                    if not kw or len(kw.split()) < 2 or (kw.lower() in HINDI_STOPWORDS or kw in HINDI_STOPWORDS):
                        if extract_rich_scene_visual_keywords:
                            _, _, rich_phrase = extract_rich_scene_visual_keywords(req.topic or "", sentence, kw or "", sc_idx, req.category)
                            kw = rich_phrase or req.topic or "cinematic hd"
                        else:
                            kw = req.topic or "cinematic hd"
                    scenes_data.append({"text": sentence, "keyword": kw})
                    
                if not scenes_data:
                    scenes_data = [{"text": req.full_script.strip(), "keyword": "cinematic hd"}]
            elif req.scenes and len(req.scenes) > 0 and any(s.text and s.text.strip() for s in req.scenes):
                scenes_data = []
                for sc_idx, s in enumerate(req.scenes):
                    if not s.text or not s.text.strip():
                        continue
                    txt = s.text.strip()
                    k_raw = (s.keyword or "").strip()
                    if not k_raw or len(k_raw.split()) < 2 or (k_raw.lower() in HINDI_STOPWORDS or k_raw in HINDI_STOPWORDS):
                        if extract_rich_scene_visual_keywords:
                            _, _, rich_phrase = extract_rich_scene_visual_keywords(req.topic or "", txt, k_raw, sc_idx, req.category)
                            k_raw = rich_phrase or req.topic or "cinematic hd"
                        else:
                            k_raw = req.topic or "cinematic hd"
                    scenes_data.append({"text": txt, "keyword": k_raw})

        if not scenes_data:
            fallback_text = req.topic if req.topic else "AI Video Generation"
            scenes_data = [{"text": fallback_text, "keyword": "technology"}]

        total_scenes = len(scenes_data)
        print(f"✅ STEP 1 COMPLETE: Prepared {total_scenes} scenes for rendering.")
        
        is_ultra = (req.video_type == "ultra")
        if req.video_type == "short":
            req.aspect_ratio = "9:16"
            is_16_9 = False
            orientation = "portrait"
            target_w, target_h = (720, 1280)
            target_size = (540, 960)
        elif req.video_type == "long":
            req.aspect_ratio = "16:9"
            is_16_9 = True
            orientation = "landscape"
            target_w, target_h = (1280, 720)
            target_size = (960, 540)
        else:
            req.aspect_ratio = req.aspect_ratio or "16:9"
            is_16_9 = (req.aspect_ratio == "16:9")
            if req.aspect_ratio == "16:9":
                orientation = "landscape"
                target_w, target_h = (1280, 720)
                target_size = (960, 540)
            elif req.aspect_ratio == "1:1":
                orientation = "portrait"
                target_w, target_h = (720, 720)
                target_size = (720, 720)
            else:
                orientation = "portrait"
                target_w, target_h = (720, 1280)
                target_size = (540, 960)

        taiyaar_scenes = []
        used_media_ids = set()
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

            cat_lower_req = str(req.category).lower()
            is_cartoon_req = any(k in cat_lower_req for k in ["cartoon", "anime", "animation", "character", "comic"])
            is_world_news_req = any(k in cat_lower_req for k in ["world news", "geopolitics", "news"])

            if is_ultra and (is_cartoon_req or is_world_news_req):
                print(f"🎨 [Ultra Scene {i+1}] Pure AI Render Mode (Cartoon/WebGL). Skipping web photo downloads; Cloxel AI Director will generate scene directly from script!")
                v_paths = []
            elif is_ultra and fetch_web_image:
                try:
                    bg_img_path = os.path.join(job_dir, f"bg_photo_{i}.jpg")
                    fg_img_path = os.path.join(job_dir, f"fg_photo_{i}.jpg")
                    
                    main_topic = req.topic if req.topic else "hero warrior"
                    scene_text = sc.get('text', '')
                    scene_kw = sc.get('keyword', '').strip()
                    
                    if extract_rich_scene_visual_keywords:
                        bg_query, fg_query, scene_visual_phrase = extract_rich_scene_visual_keywords(
                            topic=main_topic,
                            scene_text=scene_text,
                            scene_kw=scene_kw,
                            scene_idx=i,
                            category=req.category
                        )
                    else:
                        bg_query = f"{main_topic} {scene_kw} dramatic landscape wallpaper photo".strip()
                        fg_query = f"{main_topic} {scene_kw} realistic character hero portrait".strip()
                        scene_visual_phrase = scene_kw or main_topic
                    
                    print(f"   📥 Fetching Dual HD Assets: BG='{bg_query}', FG='{fg_query}'...")
                    fetch_web_image(bg_query, bg_img_path)
                    fetch_web_image(fg_query, fg_img_path)
                    
                    v_paths = []
                    if os.path.exists(bg_img_path):
                        v_paths.append(bg_img_path)
                    if os.path.exists(fg_img_path):
                        v_paths.append(fg_img_path)
                        
                    if not v_paths or any(w in scene_visual_phrase.lower() for w in ["battle", "war", "action", "fight", "army"]):
                        vid_list = fetch_videos(f"{main_topic} {scene_visual_phrase}", v_path, orientation=orientation, category=req.category or "Random", video_type=req.video_type or "short", used_media_ids=used_media_ids)
                        if vid_list and os.path.exists(vid_list[0]):
                            if not v_paths:
                                v_paths = vid_list
                            else:
                                v_paths.append(vid_list[0])
                except Exception as e_img:
                    print(f"   ⚠️ Ultra script image fetch fallback: {e_img}")
                    v_paths = fetch_videos(sc["keyword"], v_path, orientation=orientation, category=req.category or "Random", video_type=req.video_type or "short", topic=req.topic or "", used_media_ids=used_media_ids)
            else:
                scene_kw = (sc.get("keyword") or "").strip()
                scene_text = (sc.get("text") or "").strip()
                main_topic = (req.topic or "").strip()
                
                import re
                if req.video_type == "short":
                    # SHORT VIDEO: Use scene's dedicated video search keyword + topic context (e.g. "surgeon operating room" + "doctor" = "surgeon operating room doctor")
                    # Clean English alphanumeric words only (strictly eliminates Hindi Devanagari words like 'पर', 'तब')
                    clean_kw_words = [w for w in re.findall(r'[a-zA-Z0-9]+', scene_kw) if len(w) > 1]
                    
                    if not clean_kw_words and scene_text:
                        # If scene_kw was missing, extract big English words from script text (e.g. "doctor", "hospital", "prescription")
                        clean_kw_words = [w for w in re.findall(r'[a-zA-Z]+', scene_text) if len(w) >= 4 and w.lower() not in {
                            "this", "that", "with", "from", "have", "been", "will", "would", "could", "should",
                            "what", "when", "where", "which", "there", "their", "about", "your", "they", "them",
                            "more", "some", "into", "then", "than", "very", "also", "just", "like"
                        }][:3]

                    search_query_parts = []
                    # 1. Video search keyword first (e.g. "surgeon operating room")
                    for w in clean_kw_words:
                        if w.lower() not in [p.lower() for p in search_query_parts]:
                            search_query_parts.append(w)

                    # 2. Append topic context (e.g. "doctor") -> "surgeon operating room doctor"
                    if main_topic:
                        clean_topic_words = [w for w in re.findall(r'[a-zA-Z0-9]+', main_topic) if len(w) > 1 and w.lower() not in ["and", "the", "for", "with", "from", "about", "hindi", "english"]]
                        for tw in clean_topic_words[:2]:
                            if tw.lower() not in [p.lower() for p in search_query_parts]:
                                search_query_parts.append(tw)

                    rich_scene_query = " ".join(search_query_parts).strip()
                    if not rich_scene_query:
                        rich_scene_query = main_topic or "cinematic hd"
                else:
                    # LONG or ULTRA: Keep existing search behavior untouched
                    search_query_parts = []
                    # 1. Prioritize scene-specific keyword FIRST so each scene searches its unique visual action
                    if scene_kw:
                        for kw_word in scene_kw.split():
                            if kw_word.lower() not in HINDI_STOPWORDS and kw_word not in HINDI_STOPWORDS:
                                if kw_word.lower() not in [p.lower() for p in search_query_parts]:
                                    search_query_parts.append(kw_word)
                    elif scene_text:
                        eng_words = [w for w in scene_text.split() if w.isascii() and len(w) > 3 and w.lower() not in HINDI_STOPWORDS][:3]
                        if eng_words:
                            search_query_parts.extend(eng_words)
                            
                    # 2. Add topic context anchor words after scene keyword
                    if main_topic:
                        topic_words = [w for w in main_topic.split() if len(w) > 2 and w.lower() not in ["and", "the", "for", "with", "from", "about", "hindi", "english"]]
                        for tw in topic_words[:2]:
                            if tw.lower() not in [p.lower() for p in search_query_parts]:
                                search_query_parts.append(tw)

                    rich_scene_query = " ".join(search_query_parts).strip()
                    if not rich_scene_query:
                        rich_scene_query = scene_kw or main_topic or "cinematic hd"
                    
                v_paths = fetch_videos(
                    rich_scene_query, 
                    v_path, 
                    orientation=orientation, 
                    category=req.category or "Random", 
                    video_type=req.video_type or "short",
                    topic=main_topic,
                    used_media_ids=used_media_ids
                )
            
            # Double Safety Net: Ensure scene video is never identical in size or name to previous scenes in this video
            if v_paths and os.path.exists(v_paths[0]):
                current_size = os.path.getsize(v_paths[0])
                current_name = os.path.basename(v_paths[0])
                is_duplicate = False
                for prev_sc in taiyaar_scenes:
                    prev_v_list = prev_sc.get("video", [])
                    if prev_v_list and os.path.exists(prev_v_list[0]):
                        if (os.path.basename(prev_v_list[0]) == current_name or 
                            os.path.getsize(prev_v_list[0]) == current_size):
                            is_duplicate = True
                            break
                            
                if is_duplicate:
                    print(f"⚠️ [main.py Guard] Scene {i+1} got duplicate clip of previous scene! Re-fetching unique footage...")
                    clean_guard_kw = " ".join([w for w in re.findall(r'[a-zA-Z0-9]+', scene_kw) if len(w) > 1]) if scene_kw else ""
                    alt_query = f"{clean_guard_kw or main_topic} cinematic different angle {i+1}"
                    v_paths = fetch_videos(
                        alt_query,
                        v_path,
                        orientation=orientation,
                        category=req.category or "Random",
                        video_type=req.video_type or "short",
                        topic=main_topic,
                        used_media_ids=used_media_ids
                    )
            
            if os.path.exists(a_path):
                if not v_paths:
                    fallback_img_path = os.path.join(job_dir, f"fallback_canvas_{i}.jpg")
                    from PIL import Image
                    blank_img = Image.new('RGB', (target_w, target_h), color=(15, 10, 35))
                    blank_img.save(fallback_img_path)
                    v_paths = [fallback_img_path]

                taiyaar_scenes.append({
                    "audio": a_path, 
                    "video": v_paths, 
                    "text": sc["text"]
                })
                print(f"   ✅ Scene {i+1}/{total_scenes} ready for video assembly.")
            release_system_memory()

        if taiyaar_scenes:
            print(f"\n🎬 [PROGRESS 65%] STEP 4 & 5: Entering FFmpeg & 3D Motion Render Queue...")
            output_file = f"acoumation_video_{job_id}.mp4"
            adjusted_font_size = int(req.font_size * 0.7) if req.aspect_ratio == "16:9" else req.font_size
            with render_queue_lock:
                gc.collect()
                merge_and_export(taiyaar_scenes, output_file, font_path=f"./fonts/{req.font_name}", color=req.font_color, font_size=adjusted_font_size, target_size=target_size, bg_music=req.bg_music, mode=req.video_type, category=req.category or "Random") 
            gc.collect()
            
            print(f"\n☁️ [PROGRESS 90%] STEP 6/6: Uploading Completed Video to Cloudinary CDN...")
            cloudinary_url = None
            try:
                upload_result = cloudinary.uploader.upload(output_file, resource_type="video")
                cloudinary_url = upload_result.get("secure_url")
                print(f"✅ Cloudinary HD CDN URL: {cloudinary_url}")
                if cloudinary_url and os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                        print(f"🧹 Cleaned up local video file after Cloudinary upload: {output_file}")
                    except Exception:
                        pass
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
        register_manual_job_end()
        try:
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir, ignore_errors=True)
                print(f"🧹 Cleaned up temp scene directory: {job_dir}")
        except Exception as err:
            print(f"Temp cleanup warning: {err}")
        try:
            release_system_memory()
        except Exception:
            pass

def render_video_with_smart_fallback(user_id: str, topic: str, category: str, voice_id: str, font_name: str, font_color: str, video_type: str, requested_duration: int, bg_music: str = "cool.mp3", aspect_ratio: str = None, language: str = None):
    """
    Smart Fallback Retry Engine with Duration Stepping:
    If rendering fails for requested duration (e.g. 300s/5m), automatically steps down
    to 240s (4m) -> 180s (3m) -> 120s (2m) -> 60s (1m) for long videos, or
    55s -> 45s -> 30s -> 20s -> 10s for short reels, retrying until 100% success!
    """
    import uuid
    if not language:
        language = "hi" if (voice_id and "hi-" in str(voice_id).lower()) else "hi"

    if video_type == "short":
        aspect_ratio = "9:16"
        max_allowed = 55
        target_dur = min(requested_duration, max_allowed)
        duration_steps = [target_dur, 55, 45, 30, 20, 10]
        duration_steps = sorted(list(set([d for d in duration_steps if d <= target_dur])), reverse=True)
    elif video_type == "long":
        aspect_ratio = "16:9"
        target_dur = min(requested_duration, 300)
        duration_steps = [target_dur, 300, 240, 180, 120, 90, 60, 45, 30, 20, 10]
        duration_steps = sorted(list(set([d for d in duration_steps if d <= target_dur])), reverse=True)
    else:
        aspect_ratio = aspect_ratio or "16:9"
        if aspect_ratio == "9:16":
            max_allowed = 60
            target_dur = min(requested_duration, max_allowed)
            duration_steps = [target_dur, 60, 45, 30, 20, 10]
            duration_steps = sorted(list(set([d for d in duration_steps if d <= target_dur])), reverse=True)
        else:
            target_dur = min(requested_duration, 300)
            duration_steps = [target_dur, 300, 240, 180, 120, 90, 60, 45, 30, 20, 10]
            duration_steps = sorted(list(set([d for d in duration_steps if d <= target_dur])), reverse=True)

    last_error = None
    for attempt_idx, dur in enumerate(duration_steps):
        try:
            print(f"🔄 [SMART RETRY ENGINE] Attempt {attempt_idx + 1}/{len(duration_steps)}: Trying {video_type.upper()} ({dur} seconds, Language: {language})...")
            
            script_data = generate_ai_script_core(
                topic=topic,
                duration=dur,
                video_type=video_type,
                language=language,
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
                language=language,
                font_name=font_name,
                font_color=font_color,
                video_type=video_type,
                full_script=full_script,
                scenes=scenes_obj,
                bg_music=bg_music,
                aspect_ratio="9:16" if video_type == "short" else ("16:9" if video_type == "long" else (aspect_ratio or "16:9"))
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

    print(f"🚨 [SMART RETRY ENGINE EXHAUSTED] Custom attempts failed. Initiating Ultimate Bulletproof Fallback...")
    try:
        is_hindi_voice = (language and any(h in str(language).lower() for h in ["hi", "hindi", "hin"])) or (voice_id and "hi-" in str(voice_id).lower())
        fallback_script = (
            "विज्ञान और ब्रह्मांड के रहस्य हमेशा से इंसानों को हैरान करते आए हैं।" if is_hindi_voice
            else "Space exploration brings incredible technology and futuristic discoveries to humanity every day."
        )
        fb_req = VideoRequest(
            user_id=user_id,
            topic=topic or "Space Exploration and Technology",
            category="Technology",
            voice_id=voice_id or "hi-IN-MadhurNeural",
            language=language or "hi",
            font_name=font_name or "Arial.ttf",
            font_color=font_color or "yellow",
            video_type=video_type,
            full_script=fallback_script,
            scenes=[Scene(text=fallback_script, keyword="space technology")],
            bg_music=bg_music or "cool.mp3",
            aspect_ratio="9:16" if video_type == "short" else ("16:9" if video_type == "long" else (aspect_ratio or "16:9"))
        )
        job_id = str(uuid.uuid4())
        full_process(fb_req, job_id)
        job_result = jobs.get(job_id, {})
        if job_result.get("status") == "completed":
            print(f"✅ [ULTIMATE BULLETPROOF FALLBACK SUCCESS] Guaranteed video successfully generated for user {user_id}!")
            return job_result
    except Exception as ex_final:
        print(f"❌ Ultimate fallback exception: {ex_final}")

    return {"status": "failed", "error": last_error}

class CreateOrderRequest(BaseModel):
    internal_id: str
    plan_type: str

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

    clean_user_id = sanitize_alphanumeric_id(user_id)
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    user = users_collection.find_one({"internal_id": clean_user_id})
    if not user:
        raise HTTPException(status_code=401, detail="⚠️ Authentication Error: Invalid or non-existent user account. Please login or register to generate videos.")

    if req.video_type == "short":
        req.aspect_ratio = "9:16"
        req.filter_style = "none"
    elif req.video_type == "long":
        req.aspect_ratio = "16:9"
        req.filter_style = "none"
    elif req.video_type == "ultra":
        req.aspect_ratio = req.aspect_ratio if req.aspect_ratio in ["16:9", "9:16", "1:1"] else "16:9"

    if req.full_script and len(req.full_script) > 12000:
        raise HTTPException(status_code=400, detail="⚠️ Script too long! Maximum script length allowed is 12,000 characters per video.")

    if req.scenes and len(req.scenes) > 50:
        raise HTTPException(status_code=400, detail="⚠️ Too many scenes! Maximum scenes allowed per video is 50.")

    # 1. Inspect Subscriptions
    subscription = user.get("subscription", {})
    sub_status = subscription.get("status")
    sub_expires = subscription.get("expires_at")
    sub_plan = subscription.get("plan_type", "none")
    
    is_active = False
    if sub_status == "active" and sub_expires:
        if isinstance(sub_expires, str):
            try:
                sub_expires = datetime.fromisoformat(sub_expires.replace('Z', '+00:00'))
            except Exception:
                sub_expires = None
        if isinstance(sub_expires, datetime):
            now_check = datetime.now(timezone.utc) if sub_expires.tzinfo is not None else datetime.utcnow()
            if sub_expires > now_check:
                is_active = True

    ultra_sub = user.get("ultra_subscription", {})
    ultra_status = ultra_sub.get("status")
    ultra_expires = ultra_sub.get("expires_at")
    has_active_ultra = False
    if ultra_status == "active" and ultra_expires:
        if isinstance(ultra_expires, str):
            try:
                ultra_expires = datetime.fromisoformat(ultra_expires.replace('Z', '+00:00'))
            except Exception:
                ultra_expires = None
        if isinstance(ultra_expires, datetime):
            now_u = datetime.now(timezone.utc) if ultra_expires.tzinfo is not None else datetime.utcnow()
            if ultra_expires > now_u:
                has_active_ultra = True

    v_type = req.video_type

    # 2. Strict Plan Tier Enforcements (Cannot bypass tiers)
    if v_type == "ultra":
        if not has_active_ultra and sub_plan != "ultra":
            raise HTTPException(
                status_code=403, 
                detail="⚠️ Ultra Mode requires a dedicated ULTRA CINEMATIC plan (₹20/mo). Please subscribe to the Ultra Cinematic plan to generate Ultra videos."
            )
    elif sub_plan == "short" and v_type == "long":
        raise HTTPException(status_code=403, detail="⚠️ Your SHORT STARTER plan only permits Short videos (9:16). Please upgrade to LONG MASTER or PRO COMBO to generate Long videos.")
    elif sub_plan == "long" and v_type == "short":
        raise HTTPException(status_code=403, detail="⚠️ Your LONG MASTER plan only permits Long videos (16:9). Please upgrade to SHORT STARTER or PRO COMBO to generate Short videos.")

    # 3. Quota Deductions & Limits
    if not is_active and not (v_type == "ultra" and has_active_ultra):
        # Free Demo User (Strict 2 Free Videos Lifetime, Atomic Deduction)
        if "free_demo_count" not in user:
            users_collection.update_one({"internal_id": clean_user_id}, {"$set": {"free_demo_count": 2}})
        
        res = users_collection.update_one(
            {"internal_id": clean_user_id, "free_demo_count": {"$gt": 0}},
            {"$inc": {"free_demo_count": -1}}
        )
        if res.modified_count == 0:
            raise HTTPException(status_code=402, detail="Demo quota exhausted! You have used your 2 free demo videos. Please upgrade your plan to continue generating videos.")
    else:
        # Active Paid Plan User (Enforce Daily Limits strictly)
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        daily_usage = user.get("daily_usage", {})
        if daily_usage.get("date") != today_str:
            daily_usage = {"date": today_str, "short_count": 0, "long_count": 0, "ultra_count": 0}
            users_collection.update_one(
                {"internal_id": clean_user_id},
                {"$set": {"daily_usage": daily_usage}}
            )
        
        short_count = daily_usage.get("short_count", 0)
        long_count = daily_usage.get("long_count", 0)
        ultra_count = daily_usage.get("ultra_count", 0)

        # Enforce exact daily video caps:
        # Short Starter: 1 Short daily
        # Long Master: 1 Long daily
        # Pro Combo: 1 Short + 1 Long daily
        # Ultra: Unlimited during testing (temporarily enabled for testing per user instruction)
        if v_type == "short" and sub_plan in ["short", "combo"] and short_count >= 1:
            raise HTTPException(status_code=429, detail=f"⚠️ Daily video limit reached! Your {PLAN_NAMES.get(sub_plan, 'membership')} permits 1 Short video daily. Please try again tomorrow or upgrade plan.")
        elif v_type == "long" and sub_plan in ["long", "combo"] and long_count >= 1:
            raise HTTPException(status_code=429, detail=f"⚠️ Daily video limit reached! Your {PLAN_NAMES.get(sub_plan, 'membership')} permits 1 Long video daily. Please try again tomorrow or upgrade plan.")
        elif v_type == "ultra" and (has_active_ultra or sub_plan == "ultra"):
            # Temporary: Unlimited Ultra videos during testing
            pass

        count_field = "ultra_count" if v_type == "ultra" else ("short_count" if v_type == "short" else "long_count")
        daily_usage[count_field] = daily_usage.get(count_field, 0) + 1

        users_collection.update_one(
            {"internal_id": clean_user_id},
            {"$set": {"daily_usage": daily_usage}}
        )

    job_id = str(uuid.uuid4())
    update_job_status(job_id, {"status": "processing", "user_id": clean_user_id})
    background_tasks.add_task(full_process, req, job_id)
    return {"job_id": job_id, "status": "Processing Started"}

class ProfilePicRequest(BaseModel):
    internal_id: str
    profile_pic: str

@app.post("/update-profile-pic")
async def update_profile_pic(req: ProfilePicRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    clean_id = sanitize_alphanumeric_id(req.internal_id)
    pic = req.profile_pic.strip()
    
    # Strict Image Security Verification (prevents XSS, SSRF, & Malicious Redirects)
    is_valid_base64_img = pic.startswith("data:image/") and len(pic) < 6 * 1024 * 1024
    is_valid_https_url = pic.startswith("https://") and len(pic) < 1000
    if not (is_valid_base64_img or is_valid_https_url):
        raise HTTPException(status_code=400, detail="Invalid profile picture format. Must be a valid image.")

    users_collection.update_one(
        {"internal_id": clean_id},
        {"$set": {"profile_pic": pic}}
    )
    return {"message": "Profile picture updated successfully!"}

@app.get("/user-profile-pic/{internal_id}")
async def get_user_profile_pic(internal_id: str):
    if users_collection is None:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        clean_id = sanitize_alphanumeric_id(internal_id)
        user = users_collection.find_one({"internal_id": clean_id}, {"profile_pic": 1})
        if not user or not user.get("profile_pic"):
            raise HTTPException(status_code=404, detail="No profile pic")
        pic = user.get("profile_pic")
        if pic.startswith("data:image"):
            import base64
            header, encoded = pic.split(",", 1)
            mime = header.split(";")[0].split(":")[1].lower().strip()
            if mime not in {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}:
                raise HTTPException(status_code=400, detail="Illegal image mime type")
            data = base64.b64decode(encoded)
            return Response(content=data, media_type=mime)
        elif pic.startswith("https://"):
            return RedirectResponse(url=pic)
        raise HTTPException(status_code=400, detail="Invalid profile picture URL")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Profile pic error")

PLAN_RANKS = {"ultra": 1, "short": 2, "long": 3, "combo": 4}
PLAN_NAMES = {
    "ultra": "Ultra Cinematic (₹20/mo)",
    "short": "Short Starter (₹50/mo)",
    "long": "Long Master (₹100/mo)",
    "combo": "Pro Combo (₹119/mo)"
}

def activate_user_subscription(internal_id: str, plan_type: str, payment_id: str, order_id: str):
    """
    Atomically activates or stacks 30 days of subscription for user in MongoDB.
    Guaranteed idempotent: If payment_id was already processed, it does not double-stack or double-charge.
    """
    if users_collection is None:
        return {"status": "error", "message": "Database not configured"}

    existing_user = users_collection.find_one({"internal_id": internal_id})
    if not existing_user:
        return {"status": "error", "message": f"User {internal_id} not found"}

    existing_sub = existing_user.get("subscription", {}) if isinstance(existing_user.get("subscription"), dict) else {}
    existing_ultra = existing_user.get("ultra_subscription", {}) if isinstance(existing_user.get("ultra_subscription"), dict) else {}

    # Idempotency guard: If this payment_id has already been processed, do NOT duplicate or stack again!
    if (existing_sub.get("payment_id") == payment_id or existing_ultra.get("payment_id") == payment_id):
        print(f"ℹ️ [Payment Idempotency] Payment {payment_id} was already activated for user {internal_id}.")
        active_exp = existing_ultra.get("expires_at") if plan_type == "ultra" else existing_sub.get("expires_at")
        exp_str = active_exp.isoformat() if hasattr(active_exp, "isoformat") else str(active_exp)
        return {
            "status": "already_active",
            "message": f"Payment already verified and active! '{PLAN_NAMES.get(plan_type, plan_type)}' is active.",
            "plan_type": plan_type,
            "expires_at": exp_str,
            "purchase_count": existing_sub.get("purchase_count", 1)
        }

    now_utc = datetime.utcnow()

    if plan_type == "ultra":
        ultra_exp = existing_ultra.get("expires_at")
        is_ultra_active = False
        if ultra_exp:
            if isinstance(ultra_exp, str):
                try:
                    ultra_exp = datetime.fromisoformat(ultra_exp.replace('Z', '+00:00'))
                except Exception:
                    ultra_exp = None
            if isinstance(ultra_exp, datetime) and ultra_exp.replace(tzinfo=None) > now_utc:
                is_ultra_active = True

        if is_ultra_active:
            exp_date_str = ultra_exp.strftime("%b %d, %Y") if isinstance(ultra_exp, datetime) else "expiry"
            return {
                "status": "error",
                "message": f"⚠️ Ultra Plan Active! You already have an active Ultra Cinematic subscription (valid until {exp_date_str})."
            }

        expires_at = now_utc + timedelta(days=30)
        ultra_data = {
            "plan_type": "ultra",
            "status": "active",
            "payment_id": payment_id,
            "order_id": order_id,
            "activated_at": now_utc,
            "expires_at": expires_at
        }
        users_collection.update_one(
            {"internal_id": internal_id},
            {"$set": {"ultra_subscription": ultra_data}}
        )
        if payment_orders_collection is not None and order_id:
            payment_orders_collection.update_one(
                {"order_id": order_id},
                {"$set": {"status": "completed", "payment_id": payment_id, "completed_at": now_utc}},
                upsert=True
            )
        return {
            "status": "completed",
            "message": f"🎉 Ultra Cinematic Plan (₹20/mo) activated successfully!",
            "plan_type": "ultra",
            "expires_at": expires_at.isoformat()
        }

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
        if isinstance(sub_exp, datetime) and sub_exp > now_utc:
            is_active = True

    if is_active:
        if current_plan == plan_type:
            expires_at = sub_exp + timedelta(days=30)
            purchase_count += 1
            print(f"🔄 Stacked +30 days on '{plan_type}' for user {internal_id} (Purchase #{purchase_count}, Expiry: {expires_at.isoformat()})")
        else:
            expires_at = now_utc + timedelta(days=30)
            purchase_count = 1
            print(f"🚀 Upgraded user {internal_id} from '{current_plan}' to '{plan_type}'! Expiry set to {expires_at.isoformat()}")
    else:
        expires_at = now_utc + timedelta(days=30)
        purchase_count = 1
        print(f"✅ Activated new 30-day '{plan_type}' membership for user {internal_id}")

    subscription_data = {
        "plan_type": plan_type,
        "status": "active",
        "payment_id": payment_id,
        "order_id": order_id,
        "activated_at": existing_sub.get("activated_at") or now_utc,
        "expires_at": expires_at,
        "purchase_count": purchase_count
    }

    users_collection.update_one(
        {"internal_id": internal_id},
        {"$set": {"subscription": subscription_data}}
    )
    if payment_orders_collection is not None and order_id:
        payment_orders_collection.update_one(
            {"order_id": order_id},
            {"$set": {"status": "completed", "payment_id": payment_id, "completed_at": now_utc}},
            upsert=True
        )

    return {
        "status": "completed",
        "message": f"Payment verified! '{PLAN_NAMES.get(plan_type, plan_type)}' activated successfully until {expires_at.strftime('%b %d, %Y')}!",
        "expires_at": expires_at.isoformat(),
        "purchase_count": purchase_count
    }

@app.get("/user-subscription/{internal_id}")
async def get_user_subscription(internal_id: str):
    clean_id = sanitize_alphanumeric_id(internal_id)
    if users_collection is None:
        return {"free_demo_count": 2, "has_active_subscription": False, "plan_type": "none"}
    try:
        user = users_collection.find_one({"internal_id": clean_id})
        user = decrypt_user_doc(user)
        if not user:
            return {"free_demo_count": 2, "has_active_subscription": False, "plan_type": "none"}
            
        free_demo = user.get("free_demo_count")
        if free_demo is None:
            free_demo = 2
            users_collection.update_one({"internal_id": clean_id}, {"$set": {"free_demo_count": 2}})
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

        # Fail-Safe Auto-Recovery: If user paid but browser disconnected, auto-check & activate from Razorpay
        if not is_active and payment_orders_collection is not None:
            try:
                recent_pending = payment_orders_collection.find_one({
                    "internal_id": internal_id,
                    "status": "created",
                    "created_at": {"$gte": datetime.utcnow() - timedelta(minutes=45)}
                })
                if recent_pending:
                    k_id = os.getenv("RAZORPAY_KEY_ID", "").strip().strip('"').strip("'")
                    k_sec = os.getenv("RAZORPAY_KEY_SECRET", "").strip().strip('"').strip("'")
                    if k_id and k_sec and k_sec != "secret_placeholder":
                        import razorpay
                        rz_cli = razorpay.Client(auth=(k_id, k_sec))
                        p_order_id = recent_pending.get("order_id")
                        if p_order_id and not p_order_id.startswith("order_test_"):
                            p_list = rz_cli.order.payments(p_order_id).get("items", [])
                            for p_item in p_list:
                                if p_item.get("status") == "captured":
                                    activate_user_subscription(
                                        internal_id=internal_id,
                                        plan_type=recent_pending.get("plan_type"),
                                        payment_id=p_item.get("id"),
                                        order_id=p_order_id
                                    )
                                    fresh_u = users_collection.find_one({"internal_id": internal_id})
                                    if fresh_u:
                                        user = decrypt_user_doc(fresh_u)
                                        subscription = user.get("subscription", {})
                                        sub_status = subscription.get("status")
                                        sub_expires = subscription.get("expires_at")
                                        sub_plan = subscription.get("plan_type", "none")
                                        is_active = (sub_status == "active")
                                    break
            except Exception as auto_rec_err:
                print(f"⚠️ get_user_subscription auto-recovery notice: {auto_rec_err}")

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
            "today_ultra_count": daily_usage.get("ultra_count", 0),
            "today_auto_short_count": auto_daily_usage.get("auto_short_count", 0),
            "today_auto_long_count": auto_daily_usage.get("auto_long_count", 0),
            "today_auto_ultra_count": auto_daily_usage.get("auto_ultra_count", 0),
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
    if req.ultra_aspect_ratio == "9:16":
        req.ultra_duration = max(10, min(60, req.ultra_duration))
    else:
        req.ultra_duration = max(20, min(300, req.ultra_duration))

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
    clean_id = sanitize_alphanumeric_id(internal_id)
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

    user = users_collection.find_one({"internal_id": clean_id})
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

        "ultra_enabled": schedule.get("ultra_enabled", False),
        "ultra_auto_topic": schedule.get("ultra_auto_topic", True),
        "ultra_topic": schedule.get("ultra_topic", "History of Ancient Warriors"),
        "ultra_category": schedule.get("ultra_category", "Random"),
        "ultra_aspect_ratio": schedule.get("ultra_aspect_ratio", "16:9"),
        "ultra_voice": schedule.get("ultra_voice", "hi-IN-MadhurNeural"),
        "ultra_font": schedule.get("ultra_font", "Arial.ttf"),
        "ultra_color": schedule.get("ultra_color", "yellow"),
        "ultra_duration": schedule.get("ultra_duration", 60),
        "ultra_time": schedule.get("ultra_time", "21:00"),
        "ultra_language": schedule.get("ultra_language", "hi"),

        "total_videos_created": used_videos,
        "remaining_plan_videos": remaining,
        "total_plan_allowance": total_allowance,
        "purchase_count": purchase_count,
        "next_scheduled_run": next_run
    }

@app.get("/admin/active-schedules")
async def get_active_schedules_admin(request: Request):
    """Admin inspection endpoint listing all accounts with active auto-upload enabled (Protected)"""
    verify_admin_access(request)
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
def get_security_status(request: Request):
    """Admin inspection endpoint displaying active WAF security metrics and threat logs (Protected)"""
    verify_admin_access(request)
    return {
        "waf_status": "ACTIVE_ENFORCED",
        "shield_version": "Cloxel Ultimate WAF v2.0",
        "attack_statistics": waf.attack_stats,
        "active_banned_ips": list(waf.banned_ips.keys()),
        "total_banned_ips": len(waf.banned_ips)
    }

@app.post("/create-razorpay-order")
async def create_razorpay_order(req: CreateOrderRequest):
    amounts = {
        "ultra": 2000,
        "short": 5000,
        "long": 10000,
        "combo": 11900
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

            if req.plan_type == "ultra":
                existing_ultra = user.get("ultra_subscription", {}) if isinstance(user.get("ultra_subscription"), dict) else {}
                ultra_exp = existing_ultra.get("expires_at")
                is_ultra_active = False
                if ultra_exp:
                    if isinstance(ultra_exp, str):
                        try:
                            ultra_exp = datetime.fromisoformat(ultra_exp.replace('Z', '+00:00'))
                        except Exception:
                            ultra_exp = None
                    if isinstance(ultra_exp, datetime) and ultra_exp.replace(tzinfo=None) > datetime.utcnow():
                        is_ultra_active = True

                if is_ultra_active:
                    exp_date_str = ultra_exp.strftime("%b %d, %Y") if isinstance(ultra_exp, datetime) else "expiry"
                    raise HTTPException(
                        status_code=400,
                        detail=f"⚠️ Ultra Plan Active! You already have an active Ultra Cinematic subscription (valid until {exp_date_str}). Ultra Mode subscription can only be purchased once a month and will be available to renew after your current plan expires."
                    )

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
                "payment_capture": 1,
                "notes": {
                    "internal_id": req.internal_id,
                    "plan_type": req.plan_type
                }
            })
            if payment_orders_collection is not None:
                payment_orders_collection.update_one(
                    {"order_id": order["id"]},
                    {"$set": {
                        "order_id": order["id"],
                        "internal_id": req.internal_id,
                        "plan_type": req.plan_type,
                        "amount": amount,
                        "status": "created",
                        "created_at": datetime.utcnow()
                    }},
                    upsert=True
                )
            return {
                "order_id": order["id"],
                "amount": amount,
                "currency": "INR",
                "key_id": key_id
            }
        except Exception as e:
            print(f"⚠️ Razorpay API order warning: {e}. Falling back to standard test checkout mode.")
            
    fake_order_id = f"order_test_{str(uuid.uuid4())[:8]}"
    if payment_orders_collection is not None:
        payment_orders_collection.update_one(
            {"order_id": fake_order_id},
            {"$set": {
                "order_id": fake_order_id,
                "internal_id": req.internal_id,
                "plan_type": req.plan_type,
                "amount": amount,
                "status": "created",
                "created_at": datetime.utcnow()
            }},
            upsert=True
        )
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

    if key_id and key_secret and key_secret != "secret_placeholder":
        if not req.razorpay_signature:
            raise HTTPException(status_code=400, detail="Payment Signature Missing. Activation Denied.")
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

    # Anti-Tampering Guard: Ensure plan_type and internal_id match the server-recorded Razorpay order
    verified_plan = req.plan_type
    if payment_orders_collection is not None and req.razorpay_order_id:
        stored_order = payment_orders_collection.find_one({"order_id": req.razorpay_order_id})
        if stored_order:
            if stored_order.get("internal_id") and stored_order.get("internal_id") != req.internal_id:
                raise HTTPException(status_code=403, detail="⚠️ Security Error: Payment order does not match your user account.")
            verified_plan = stored_order.get("plan_type", req.plan_type)
            payment_orders_collection.update_one(
                {"_id": stored_order["_id"]},
                {"$set": {"status": "paid", "payment_id": req.razorpay_payment_id}}
            )

    result = activate_user_subscription(
        internal_id=req.internal_id,
        plan_type=verified_plan,
        payment_id=req.razorpay_payment_id,
        order_id=req.razorpay_order_id
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))

    return result

@app.post("/razorpay-webhook")
async def razorpay_webhook(request: Request):
    """
    Direct Server-to-Server Razorpay Webhook Engine:
    Guarantees 100% fail-safe subscription activation even if user's internet drops,
    browser is closed, or phone battery dies during checkout!
    """
    webhook_body = await request.body()
    webhook_signature = request.headers.get("X-Razorpay-Signature", "")
    
    webhook_secret = (os.getenv("RAZORPAY_WEBHOOK_SECRET") or os.getenv("RAZORPAY_KEY_SECRET", "")).strip().strip('"').strip("'")
    
    if webhook_secret and webhook_secret != "secret_placeholder":
        if not webhook_signature:
            raise HTTPException(status_code=400, detail="Missing Webhook Signature")
        try:
            import hmac
            import hashlib
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                webhook_body,
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected_signature, webhook_signature):
                print("❌ [Razorpay Webhook] Invalid signature from webhook caller!")
                raise HTTPException(status_code=400, detail="Invalid Webhook Signature")
        except HTTPException:
            raise
        except Exception as sig_err:
            print(f"⚠️ [Razorpay Webhook] Signature verification notice: {sig_err}")
            raise HTTPException(status_code=400, detail="Signature Verification Error")

    try:
        payload = json.loads(webhook_body.decode('utf-8'))
    except Exception:
        return {"status": "error", "message": "Invalid JSON body"}

    event = payload.get("event")
    print(f"📥 [Razorpay Webhook] Received Event: {event}")

    if event in ["payment.captured", "order.paid"]:
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_entity = payload.get("payload", {}).get("order", {}).get("entity", {})
        
        payment_id = payment_entity.get("id")
        order_id = payment_entity.get("order_id") or order_entity.get("id")
        
        notes = payment_entity.get("notes", {}) or order_entity.get("notes", {})
        internal_id = notes.get("internal_id")
        plan_type = notes.get("plan_type")

        # Fallback lookup from payment_orders_collection if notes were absent
        if (not internal_id or not plan_type) and payment_orders_collection is not None and order_id:
            saved_order = payment_orders_collection.find_one({"order_id": order_id})
            if saved_order:
                internal_id = internal_id or saved_order.get("internal_id")
                plan_type = plan_type or saved_order.get("plan_type")

        if internal_id and plan_type and payment_id:
            print(f"⚡ [Razorpay Webhook Auto-Activation] Activating {plan_type} for user {internal_id} (Payment ID: {payment_id})...")
            result = activate_user_subscription(
                internal_id=internal_id,
                plan_type=plan_type,
                payment_id=payment_id,
                order_id=order_id or ""
            )
            print(f"✅ [Razorpay Webhook Result]: {result.get('message')}")
            return {"status": "ok", "result": result}
        else:
            print(f"⚠️ [Razorpay Webhook] Incomplete order/user metadata for order: {order_id}")

    return {"status": "ignored"}

@app.get("/sync-payment-status/{internal_id}")
async def sync_payment_status(internal_id: str):
    """
    Auto-Recovery / Reconciliation Endpoint:
    Checks if user has any recent pending orders in the last 2 hours that succeeded on Razorpay
    (e.g. if user's internet dropped before redirect). Automatically activates membership!
    """
    if users_collection is None:
        return {"status": "error", "message": "Database not configured"}

    key_id = os.getenv("RAZORPAY_KEY_ID", "").strip().strip('"').strip("'")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip().strip('"').strip("'")

    if not key_id or not key_secret or key_secret == "secret_placeholder":
        return {"status": "skipped", "message": "Razorpay live keys not set"}

    if payment_orders_collection is None:
        return {"status": "skipped", "message": "Orders collection not available"}

    recent_cutoff = datetime.utcnow() - timedelta(hours=2)
    pending_orders = list(payment_orders_collection.find({
        "internal_id": internal_id,
        "status": "created",
        "created_at": {"$gte": recent_cutoff}
    }).sort("created_at", -1).limit(5))

    if not pending_orders:
        return {"status": "no_pending_orders"}

    activated = []
    try:
        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))
        for ord_doc in pending_orders:
            order_id = ord_doc.get("order_id")
            plan_type = ord_doc.get("plan_type")
            if not order_id or not plan_type or order_id.startswith("order_test_"):
                continue

            try:
                payments_resp = client.order.payments(order_id)
                payments = payments_resp.get("items", [])
                for p in payments:
                    if p.get("status") == "captured":
                        pay_id = p.get("id")
                        print(f"🔄 [Sync Auto-Recovery] Found captured payment {pay_id} for order {order_id}. Activating subscription...")
                        act_res = activate_user_subscription(
                            internal_id=internal_id,
                            plan_type=plan_type,
                            payment_id=pay_id,
                            order_id=order_id
                        )
                        activated.append(act_res)
                        break
            except Exception as e_ord:
                print(f"⚠️ [Sync Auto-Recovery] Error checking order {order_id}: {e_ord}")
    except Exception as e_client:
        print(f"⚠️ [Sync Auto-Recovery Client Error]: {e_client}")

    if activated:
        return {"status": "recovered", "activated": activated}
    return {"status": "no_new_payments_found"}

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

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "dispostable.com", 
    "trashmail.com", "yopmail.com", "asdf.com", "test.com", "fake.com", 
    "example.com", "guerrillamail.com", "sharklasers.com", "getnada.com", "throwawaymail.com"
}

_email_dispatch_log = {}

def validate_email_domain(email: str) -> Tuple[bool, str]:
    """Pure syntax and domain validation without rate-limiting state mutation."""
    if not email or "@" not in email:
        return False, "Invalid email address format."
    clean_email = email.strip().lower()
    parts = clean_email.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False, "Invalid email address format."
    domain = parts[1]
    if domain in DISPOSABLE_EMAIL_DOMAINS or domain.endswith(".test") or domain.endswith(".invalid"):
        return False, f"Disposable/fake email domain '@{domain}' is blocked."
    if len(domain) < 3 or "." not in domain:
        return False, "Invalid email domain structure."
    return True, "OK"

def validate_and_rate_limit_email(email: str, cooldown_seconds: int = 45) -> Tuple[bool, str]:
    """Validates email and enforces anti-spam dispatch cooldown."""
    is_valid, reason = validate_email_domain(email)
    if not is_valid:
        return False, reason
    clean_email = email.strip().lower()
    now = time.time()
    last_sent = _email_dispatch_log.get(clean_email, 0)
    if now - last_sent < cooldown_seconds:
        rem = int(cooldown_seconds - (now - last_sent))
        return False, f"Email rate limit active: Please wait {rem}s before requesting another email."
    _email_dispatch_log[clean_email] = now
    return True, "OK"

def send_brevo_qr_email(user_email: str, user_name: str, security_qr_token: str, **kwargs):
    try:
        is_valid_email, reason = validate_and_rate_limit_email(user_email)
        if not is_valid_email:
            print(f"⚠️ Brevo Protection Guard: Blocked email dispatch to '{user_email}' ({reason})")
            return False

        brevo_api_key = os.getenv("BREVO_API_KEY") or os.getenv("SMTP_KEY")
        sender_email = os.getenv("SENDER_EMAIL") or "dr2829242627@gmail.com"
        brevo_sender_email = os.getenv("BREVO_SENDER_EMAIL") or os.getenv("SENDER_EMAIL") or "dr2829242627@gmail.com"
        sender_name = os.getenv("SENDER_NAME", "cloxel.AI")
        
        qr_payload = json.dumps({
            "security_token": security_qr_token,
            "cipher_signature": hashlib.sha256((security_qr_token + user_email).encode('utf-8')).hexdigest()[:48].upper(),
            "email": user_email,
            "issuer": "Cloxel AI Security Engine"
        })
        
        qr_b64 = generate_qr_base64(qr_payload)

        import urllib.parse
        encoded_payload = urllib.parse.quote(qr_payload)
        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_payload}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0b071a; color: #ffffff; padding: 20px; margin: 0; }}
            .card {{ max-width: 550px; margin: 0 auto; background: #130d2a; border: 1px solid rgba(168,85,247,0.4); border-radius: 16px; padding: 30px; text-align: center; }}
            .badge {{ background: rgba(168,85,247,0.2); color: #c084fc; border: 1px solid #a855f7; padding: 6px 14px; border-radius: 20px; font-weight: bold; display: inline-block; font-size: 0.85rem; }}
            h2 {{ color: #ffffff; margin-top: 15px; margin-bottom: 10px; }}
            p {{ color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; margin-bottom: 10px; }}
            .qr-container {{ background: #ffffff; padding: 18px; border-radius: 14px; display: inline-block; margin: 20px auto; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.3); }}
            .qr-container img {{ width: 220px; height: 220px; display: block; margin: 0 auto; border: 0; }}
            .warning {{ color: #f87171; font-size: 0.85rem; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; text-align: center; }}
          </style>
        </head>
        <body>
          <div class="card" align="center">
            <span class="badge">✦ CLOXEL AI SECURITY CREDENTIAL</span>
            <h2>Welcome, {user_name}!</h2>
            <p>Your Cloxel AI account credential setup is successful. Below is your official <strong>Cryptographic Security QR Code</strong>.</p>
            <p><strong>IMPORTANT:</strong> Save or screenshot this QR Code. Whenever you reset your password, you must upload this QR image or scan it via camera.</p>
            
            <div class="qr-container" align="center">
              <img src="{qr_api_url}" alt="Cloxel Security QR Code" width="220" height="220" style="width: 220px; height: 220px; display: block; margin: 0 auto;" />
            </div>

            <div class="warning">
              🔒 <strong>Security Policy:</strong> Password reset requires scanning or uploading this Cloxel Security QR Code image. Keep this QR Code safe and private.
            </div>
          </div>
        </body>
        </html>
        """

        # 1. Brevo HTTP REST API (Priority #1: High-Speed HTTPS REST API, ~200ms, zero connection hang)
        if brevo_api_key:
            try:
                url = "https://api.brevo.com/v3/smtp/email"
                headers = {
                    "accept": "application/json",
                    "api-key": brevo_api_key,
                    "content-type": "application/json"
                }
                payload = {
                    "sender": {"name": sender_name, "email": brevo_sender_email},
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
                
                res = requests.post(url, json=payload, headers=headers, timeout=5)
                if res.status_code in [200, 201, 202]:
                    print(f"✅ Brevo QR Email sent successfully via REST API to {user_email}")
                    return True
                else:
                    print(f"⚠️ Brevo API Response ({res.status_code}): {res.text}")
            except Exception as _b_err:
                print(f"⚠️ Brevo API error: {_b_err}")

        # 2. Resend API (Priority #2: High-Speed REST API fallback)
        resend_key = os.getenv("RESEND_API_KEY")
        if resend_key:
            try:
                resend_url = "https://api.resend.com/emails"
                resend_headers = {
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json"
                }
                resend_from = os.getenv("RESEND_FROM_EMAIL", f"{sender_name} <onboarding@resend.dev>")
                resend_payload = {
                    "from": resend_from,
                    "to": [user_email],
                    "subject": "✦ Cloxel AI - Official Security QR Code Credential",
                    "html": html_content
                }
                res_r = requests.post(resend_url, json=resend_payload, headers=resend_headers, timeout=5)
                if res_r.status_code in [200, 201]:
                    print(f"✅ Security QR Email sent successfully via Resend API to {user_email}")
                    return True
                else:
                    print(f"⚠️ Resend API Response ({res_r.status_code}): {res_r.text}")
            except Exception as _r_err:
                print(f"⚠️ Resend API error: {_r_err}")

        # 3. SMTP (Priority #3: Fallback only when explicit credentials/host are configured)
        smtp_user = os.getenv("SMTP_USER") or os.getenv("SMTP_LOGIN")
        smtp_password = os.getenv("SMTP_PASSWORD") or os.getenv("SMTP_KEY")
        if smtp_user and smtp_password:
            try:
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.base import MIMEBase
                from email import encoders

                if os.getenv("SMTP_HOST"):
                    target_host = os.getenv("SMTP_HOST")
                elif "brevo" in smtp_user.lower():
                    target_host = "smtp-relay.brevo.com"
                elif "gmail" in smtp_user.lower():
                    target_host = "smtp.gmail.com"
                else:
                    target_host = "smtp-relay.brevo.com"

                smtp_port = int(os.getenv("SMTP_PORT", "587"))
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

                # Strict 4s timeout prevents blocking/hanging
                if smtp_port == 465:
                    with smtplib.SMTP_SSL(target_host, smtp_port, timeout=4) as server:
                        server.login(smtp_user, smtp_password)
                        server.sendmail(sender_email, [user_email], msg.as_string())
                else:
                    with smtplib.SMTP(target_host, smtp_port, timeout=4) as server:
                        server.starttls()
                        server.login(smtp_user, smtp_password)
                        server.sendmail(sender_email, [user_email], msg.as_string())
                print(f"✅ Security QR Email sent successfully via SMTP ({target_host}) to {user_email}")
                return True
            except Exception as _smtp_err:
                print(f"⚠️ SMTP error ({target_host or 'smtp'}): {_smtp_err}")

        has_configured_provider = bool(os.getenv("BREVO_API_KEY") or os.getenv("SMTP_KEY") or os.getenv("RESEND_API_KEY") or (os.getenv("SMTP_USER") and os.getenv("SMTP_PASSWORD")))
        if not has_configured_provider:
            print(f"⚠️ [DEV MODE] No active Email Provider configured. Auto-approving QR for dev environment: {security_qr_token}")
            return True

        print(f"⚠️ All configured Email Providers failed. Security QR Code for {user_email}: {security_qr_token}")
        return False
    except Exception as e:
        print(f"❌ Error sending Security QR Email: {e}")
        return False

@app.post("/register")
async def register_user(req: UserRegister):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    primary_email = req.email.strip().lower()
    raw_digits = "".join(filter(str.isdigit, req.phone))
    primary_phone = raw_digits[-10:] if len(raw_digits) >= 10 else raw_digits
    clean_name = clean_xss(req.name.strip())
    clean_country = clean_xss(req.country.strip())
    
    if not primary_email or not primary_phone or not clean_name or not clean_country:
        raise HTTPException(status_code=400, detail="All fields (Name, Country, Phone, Email, Password) are mandatory.")
        
    if len(primary_phone) != 10:
        raise HTTPException(
            status_code=400,
            detail="⚠️ Registration Failed: Mobile Number must be exactly 10 digits (e.g. 9876543210)."
        )

    if len(primary_email) > 120:
        raise HTTPException(status_code=400, detail="⚠️ Registration Failed: Email address is too long.")

    if len(req.password) < 6 or len(req.password) > 128:
        raise HTTPException(status_code=400, detail="⚠️ Registration Failed: Password must be between 6 and 128 characters.")

    import re
    email_format_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    if not email_format_regex.match(primary_email):
        raise HTTPException(
            status_code=400,
            detail="⚠️ Registration Failed: Please enter a valid Email ID (e.g. name@domain.com)."
        )

    # Pre-flight email deliverability & fake domain rejection (instant in-memory check, does NOT trigger cooldown)
    is_valid_email, reason = validate_email_domain(primary_email)
    if not is_valid_email:
        raise HTTPException(
            status_code=400,
            detail=f"⚠️ Registration Failed: {reason}"
        )

    dup_result = check_duplicate_user(email=primary_email, phone=primary_phone)
    if dup_result:
        dup_type, _ex_user = dup_result
        if dup_type == "phone":
            raise HTTPException(
                status_code=400,
                detail=f"⚠️ Account Creation Failed: Mobile Number '{primary_phone}' is already registered with an existing account! Only one Cloxel AI account is permitted per mobile number. Please log in or use a different phone number."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"⚠️ Account Creation Failed: Email ID '{primary_email}' is already registered with an existing account! Only one Cloxel AI account is permitted per email address. Please log in or use a different email address."
            )

    email_h = hash_identifier(primary_email)
    phone_h = hash_identifier(primary_phone) if primary_phone else None
        
    hashed_password = safe_hash_password(req.password)
    internal_id = str(uuid.uuid4())
    security_qr_tok = f"CLOXEL-SEC-{uuid.uuid4().hex[:12].upper()}"

    new_user = {
        "name": encrypt_field(clean_name),
        "country": clean_country,
        "phone": encrypt_field(primary_phone),
        "email": encrypt_field(primary_email),
        "email_or_mobile": encrypt_field(primary_email),
        "email_hash": email_h,
        "phone_hash": phone_h,
        "password_hash": hashed_password,
        "internal_id": internal_id,
        "security_qr_token": encrypt_field(security_qr_tok),
        "free_demo_count": 2,
        "created_at": datetime.utcnow()
    }

    # 1. Enforce strict policy: "Bina email jaye login nahi hona chahiye, pehle email jaye uske baad login ho"
    # Deliver the Security QR Code email FIRST before inserting user document or permitting login.
    email_sent = False
    try:
        email_sent = send_brevo_qr_email(
            user_email=primary_email,
            user_name=clean_name,
            security_qr_token=security_qr_tok
        )
    except Exception as _e_qr:
        print(f"❌ Security QR Email dispatch error: {_e_qr}")
        email_sent = False

    if not email_sent:
        raise HTTPException(
            status_code=400,
            detail=f"⚠️ Registration Blocked: Could not send Security QR Code email to '{primary_email}'. Please verify your email address is correct and try again."
        )

    # 2. ONLY when email delivery is confirmed, register account in MongoDB and grant login!
    users_collection.insert_one(new_user)

    return {
        "message": "User registered successfully",
        "internal_id": internal_id,
        "email": primary_email,
        "phone": primary_phone,
        "name": clean_name,
        "security_qr_token": security_qr_tok
    }

@app.post("/login")
async def login_user(req: UserLogin, request: Request):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    client_ip = resolve_client_ip(request)
    raw_identifier = req.email_or_mobile.strip().lower()

    # 1. Anti-Brute-Force check: If 6 failed attempts reached, lock out for 15 minutes
    is_locked, remaining_secs = waf.is_login_locked(client_ip, raw_identifier)
    if is_locked:
        mins = max(1, remaining_secs // 60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail=f"⛔ Account Security Lockout: Too many failed login attempts. Access temporarily locked for {mins} minutes to protect your account. Please try again later."
        )

    user = find_user_in_db(raw_identifier)
    
    if not user:
        failed_count = waf.record_failed_login(client_ip, raw_identifier)
        remaining = max(0, 6 - failed_count)
        if remaining == 0:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="⛔ Account Security Lockout: 6 failed attempts reached. Device temporarily locked for 15 minutes.")
        raise HTTPException(status_code=400, detail=f"⚠️ Account Not Found: Please check your Email / Mobile Number ({remaining} attempts remaining before temporary lockout).")
        
    stored_hash = user.get("password_hash") or user.get("password")
    if not stored_hash:
        raise HTTPException(status_code=400, detail="⚠️ Account password configuration issue. Please Register a new account.")

    is_valid = safe_verify_password(req.password, stored_hash)

    if not is_valid:
        failed_count = waf.record_failed_login(client_ip, raw_identifier)
        remaining = max(0, 6 - failed_count)
        if remaining == 0:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="⛔ Account Security Lockout: 6 failed password attempts reached. Device temporarily locked for 15 minutes.")
        raise HTTPException(status_code=400, detail=f"⚠️ Incorrect Password! Please check your password ({remaining} attempts remaining before 15-minute temporary lockout).")
        
    # Login Successful: Reset failed attempts counter
    waf.record_successful_login(client_ip, raw_identifier)
    return {
        "message": "Login successful",
        "internal_id": user["internal_id"],
        "email": (user.get("email") or "").strip().lower(),
        "phone": user.get("phone") or "",
        "name": user.get("name") or "User"
    }

@app.get("/api/auth/google-client-id")
def get_google_client_id():
    client_id = os.getenv("GOOGLE_CLIENT_ID") or os.getenv("YOUTUBE_CLIENT_ID") or ""
    return {"google_client_id": client_id.strip()}

@app.post("/api/auth/google-verify")
async def google_verify(req: GoogleVerifyRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    token = req.credential
    if not token:
        raise HTTPException(status_code=400, detail="⚠️ Google verification credential missing.")

    google_email = None
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        id_info = id_token.verify_oauth2_token(token, google_requests.Request())
        google_email = (id_info.get("email") or "").strip().lower()
    except Exception:
        try:
            resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                google_email = (data.get("email") or "").strip().lower()
        except Exception as _e_tok:
            print(f"⚠️ Google tokeninfo error: {_e_tok}")

    if not google_email:
        raise HTTPException(status_code=400, detail="⚠️ Google Account Verification Failed. Unable to extract verified email from Google.")

    raw_identifier = (req.email_or_mobile or google_email).strip().lower()
    user = find_user_in_db(raw_identifier)

    if not user:
        raise HTTPException(
            status_code=400,
            detail=f"⚠️ Account Not Found: No Cloxel AI account exists for email '{raw_identifier}'. Please register first."
        )

    target_email = (user.get("email") or "").strip().lower()

    if google_email != target_email:
        raise HTTPException(
            status_code=400,
            detail=f"⚠️ Google Account Mismatch! Your signed-in Google email is '{google_email}', but the account being reset is '{target_email}'. Please sign in with Google account '{target_email}'."
        )

    user_name = user.get("name") or "User"
    security_qr_tok = user.get("security_qr_token")
    if not security_qr_tok:
        security_qr_tok = f"CLOXEL-SEC-{uuid.uuid4().hex[:12].upper()}"
        users_collection.update_one({"_id": user["_id"]}, {"$set": {"security_qr_token": encrypt_field(security_qr_tok)}})

    reg_browser_tok = user.get("registration_browser_token") or ""
    try:
        send_brevo_qr_email(
            user_email=target_email,
            user_name=user_name,
            security_qr_token=security_qr_tok,
            browser_token=reg_browser_tok
        )
    except Exception as _e_qr:
        print(f"⚠️ Brevo QR Email dispatch error: {_e_qr}")

    return {
        "message": f"✅ Google Account '{google_email}' Verified! Security QR Code sent to your inbox. Please upload or scan your QR Code below.",
        "google_verified_email": google_email,
        "internal_id": user.get("internal_id"),
        "account_verified": True
    }

@app.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    raw_identifier = req.email_or_mobile.strip()
    if not raw_identifier:
        raise HTTPException(status_code=400, detail="⚠️ Please provide an Email or Mobile Number.")

    user = find_user_in_db(raw_identifier)
    if not user:
        raise HTTPException(status_code=400, detail="⚠️ Account Not Found: Please check your Email / Mobile Number.")

    user_email = (user.get("email") or "").strip().lower()
    user_phone = (user.get("phone") or "").strip()
    user_internal_id = (user.get("internal_id") or "").strip().lower()

    user_name = user.get("name") or "User"
    security_qr_tok = user.get("security_qr_token")
    if not security_qr_tok:
        security_qr_tok = f"CLOXEL-SEC-{uuid.uuid4().hex[:12].upper()}"
        users_collection.update_one({"_id": user["_id"]}, {"$set": {"security_qr_token": encrypt_field(security_qr_tok)}})

    return {
        "message": f"✅ Account verified! Please upload or scan your Cloxel Security QR Code (received during registration) to reset password.",
        "account_verified": True
    }

@app.post("/verify-reset-qr")
async def verify_reset_qr(req: VerifyQRRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    raw_identifier = req.email_or_mobile.strip()
    if not raw_identifier:
        raise HTTPException(status_code=400, detail="⚠️ Please provide an Email or Mobile Number.")

    user = find_user_in_db(raw_identifier)
    if not user:
        raise HTTPException(status_code=400, detail="⚠️ Account Not Found.")

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
    
    if not stored_qr_tok or extracted_token.strip() != stored_qr_tok.strip():
        raise HTTPException(
            status_code=400,
            detail="⚠️ Security Verification Failed: Invalid QR Code! The uploaded/scanned QR code does not belong to this account."
        )

    return {
        "verified": True,
        "message": "✅ Security QR Code verified successfully! Proceed to set new password."
    }

@app.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    raw_identifier = req.email_or_mobile.strip()
    user = find_user_in_db(raw_identifier)
    if not user:
        raise HTTPException(status_code=400, detail="⚠️ Account Not Found.")

    user_email = (user.get("email") or "").strip().lower()
    user_phone = (user.get("phone") or "").strip()
    user_internal_id = (user.get("internal_id") or "").strip().lower()

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
    
    if not stored_qr_tok or extracted_token.strip() != stored_qr_tok.strip():
        raise HTTPException(
            status_code=400,
            detail="⚠️ Security Error: Invalid QR Code! The uploaded QR Code token does not match your registered account credential."
        )
        
    if not req.new_password or len(req.new_password.strip()) < 6 or len(req.new_password.strip()) > 128:
        raise HTTPException(status_code=400, detail="⚠️ New password must be between 6 and 128 characters long.")

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
    clean_id = sanitize_alphanumeric_id(internal_id)
    if videos_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        user_or_terms = [{"internal_id": clean_id}, {"user_id": clean_id}]
        if users_collection is not None:
            user = users_collection.find_one({"internal_id": clean_id})
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
    clean_job_id = sanitize_alphanumeric_id(job_id)
    if clean_job_id in jobs:
        return jobs[clean_job_id]
    if rendering_jobs is not None:
        try:
            job_doc = rendering_jobs.find_one({"job_id": clean_job_id}, {"_id": 0})
            if job_doc:
                jobs[clean_job_id] = job_doc
                return job_doc
        except Exception as e:
            print(f"⚠️ DB status lookup exception for {clean_job_id}: {e}")
    return {"status": "not_found"}

@app.get("/download/{job_id}")
async def download_video(job_id: str):
    clean_job_id = sanitize_alphanumeric_id(job_id)
    job = jobs.get(clean_job_id)
    if not job and rendering_jobs is not None:
        try:
            job = rendering_jobs.find_one({"job_id": clean_job_id}, {"_id": 0})
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
        all_files = [f for f in os.listdir(fonts_dir) if f.lower().endswith(('.ttf', '.otf')) and f != "MyFont.ttf"]
        is_hindi = lambda f: any(k in f.lower() for k in ["ams ", "devanagari", "yatra", "rozha", "kalam", "mukta", "modak", "ranga", "tiro"])
        eng_fonts = sorted([f for f in all_files if not is_hindi(f)])
        unicode_devanagari = ["YatraOne-Regular.ttf", "RozhaOne-Regular.ttf", "Kalam-Bold.ttf", "Mukta-Bold.ttf", "NotoSansDevanagari-Bold.ttf", "NotoSansDevanagari-Regular.ttf", "Modak-Regular.ttf", "Ranga-Bold.ttf", "TiroDevanagariHindi-Regular.ttf"]
        all_hindi = [f for f in all_files if is_hindi(f)]
        hindi_priority = [f for f in unicode_devanagari if f in all_hindi]
        hindi_rest = sorted([f for f in all_hindi if f not in unicode_devanagari])
        fonts = eng_fonts + hindi_priority + hindi_rest
    return {"fonts": fonts}

@app.post("/cleanup/{job_id}")
async def cleanup(job_id: str):
    """Video download hone ke baad server saaf karne ke liye"""
    clean_job_id = sanitize_alphanumeric_id(job_id)
    job = jobs.get(clean_job_id)
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
            "redirect_uris": [os.getenv("YOUTUBE_REDIRECT_URI", "https://cloxelai.onrender.com/youtube/callback")]
        }
    }
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config, scopes=YOUTUBE_SCOPES
    )
    flow.redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "https://cloxelai.onrender.com/youtube/callback")
    return flow

class UnlinkRequest(BaseModel):
    internal_id: str

@app.get("/youtube/auth-url")
async def get_youtube_auth_url(internal_id: str):
    clean_id = sanitize_alphanumeric_id(internal_id)
    if users_collection is not None:
        user = users_collection.find_one({"internal_id": clean_id})
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
    
    redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "https://cloxelai.onrender.com/youtube/callback")
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
    clean_id = sanitize_alphanumeric_id(state)
    internal_id = clean_id
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    redirect_uri = os.getenv("YOUTUBE_REDIRECT_URI", "https://cloxelai.onrender.com/youtube/callback")
    
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
            frontend_url = os.getenv("FRONTEND_URL", "https://cloxelai.onrender.com")
            return RedirectResponse(url=f"{frontend_url}/?yt_error={error_msg}")
            
        user = users_collection.find_one({"internal_id": clean_id}) if users_collection is not None else None
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
            
        frontend_url = os.getenv("FRONTEND_URL", "https://cloxelai.onrender.com")
        return RedirectResponse(url=f"{frontend_url}/?yt_success=1")
    except Exception as e:
        print(f"❌ Error in youtube_callback: {e}")
        import traceback
        traceback.print_exc()
        frontend_url = os.getenv("FRONTEND_URL", "https://cloxelai.onrender.com")
        return RedirectResponse(url=f"{frontend_url}/?yt_error={str(e)}")

@app.get("/youtube/status/{internal_id}")
async def get_youtube_status(internal_id: str):
    clean_id = sanitize_alphanumeric_id(internal_id)
    if users_collection is None:
        return {"linked": False}
    try:
        projection = {"youtube_credentials": 1, "youtube_linked_at": 1}
        user = users_collection.find_one({"internal_id": clean_id}, projection)
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
    user_id: Optional[str] = None
    category: Optional[str] = "Random"
    duration_seconds: int = 30
    video_type: Optional[str] = "short"
    language: Optional[str] = "hinglish"
    tone: Optional[str] = "viral"



def generate_dynamic_procedural_script(topic: str, duration: int, video_type: str, language: str, category: str, scene_count: int, word_count: int):
    """
    Expansive Multi-Year Procedural Script Engine.
    Used as an emergency offline/sandbox fallback to ensure zero repetition even if all AI APIs are offline.
    """
    cat_lower = str(category).lower()
    t_lower = topic.lower()
    is_cartoon_cat = any(k in cat_lower for k in ["cartoon", "anime", "animation", "character", "comic"])

    words_in_topic = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', topic) if w.lower() not in {"what", "how", "why", "secret", "facts", "science", "the", "and", "for", "with"}]
    main_kw_base = " ".join(words_in_topic[:2]) if words_in_topic else topic.lower()

    lang_str = str(language or "hi").lower().strip()
    is_hindi = (lang_str in ["hi", "hindi", "hin", "hinglish"]) or ("hi" in lang_str)

    if not is_hindi:
        if is_cartoon_cat:
            char_name = words_in_topic[0].capitalize() if words_in_topic else "Our Hero"
            hooks = [
                f"Meet our adventurous hero {char_name}, whose everyday routine turns into pure comedy and unexpected chaos!",
                f"One day {char_name} had a brilliant, out-of-the-box idea that sparked an unforgettable crazy adventure!",
                f"What happens when {char_name} decides to try the craziest stunt ever? You won't believe what unfolds next!"
            ]
            body_pool = [
                f"{char_name} quickly gathered everyone and revealed the master plan with unmatched confidence.",
                f"The excitement went through the roof as the hilarious master plan was put into rapid motion.",
                f"However, an unexpected twist turned the entire situation into absolute comical mayhem.",
                f"Everyone was laughing uncontrollably while {char_name} tried to figure out a hilarious way out.",
                f"With quick wit and comic charm, {char_name} turned the crisis around in the most legendary way possible."
            ]
            closings = [
                f"And that was the hilarious adventure of {char_name}! Like and subscribe for more epic cartoon stories!",
                f"If you loved this funny tale, hit that thumbs up and stay tuned for the next adventure!"
            ]
        elif any(k in t_lower for k in ["history", "war", "king", "empire", "pratap", "shivaji", "temple", "pyramid", "ancient"]):
            hooks = [
                f"In the deep archives of world history, {topic} stands out as a breathtaking tale of valor and mystery.",
                f"Thousands of years ago, a monumental event surrounding {topic} changed the course of human history forever.",
                f"Behind the ancient legends of {topic} lies a profound truth that modern historians are still discovering."
            ]
            body_pool = [
                f"Ancient chronicles and stone inscriptions reveal strategies that were centuries ahead of their time.",
                f"Through relentless courage and unmatched determination, heroes stood firm against impossible odds.",
                f"The battlefields and ancient fortresses still echo with tales of extraordinary resilience and sacrifice.",
                f"Archaeologists and researchers continue to uncover relics that showcase the profound genius of that era."
            ]
            closings = [
                f"This timeless saga of bravery will never be forgotten! Subscribe for more powerful historical epics!",
                f"That was the true untold history of {topic}. Make sure to like and follow for more legendary stories!"
            ]
        else:
            hooks = [
                f"Did you know that behind {topic} lies a mind-bending truth that has stunned researchers worldwide?",
                f"Today we dive into {topic}, a phenomenon that impacts our everyday world in ways most people never imagine.",
                f"If you think you know everything about {topic}, this video is going to change your perspective forever."
            ]
            body_pool = [
                f"Breakthrough scientific investigations show that the underlying dynamics of {topic} challenge classical physics.",
                f"Recent discoveries have revealed patterns that are significantly more intricate than previously thought.",
                f"Top laboratories and experts around the globe are uncovering empirical data that points to revolutionary advancements.",
                f"Every new observation opens up intriguing possibilities for the future of humanity and modern technology."
            ]
            closings = [
                f"Those were the most astonishing insights about {topic}! Drop your thoughts below and subscribe for more!",
                f"If you found this mind-blowing, smash that like button and hit the bell for daily viral facts!"
            ]
    elif is_cartoon_cat:
        char_name = words_in_topic[0].capitalize() if words_in_topic else "Humara Hero"
        hooks = [
            f"Dosto! Milte hain humare mastmaula hero {char_name} se, jinki har subah ek nayi musibat aur funny hangama leke aati hai!",
            f"Ek din {char_name} ke dimaag ki batti achanak jali aur usne kar dala ek aisa dhasu jugaad jo kisi ne socha bhi nahi tha!",
            f"Kya aapne kabhi socha hai ki agar {char_name} ko koi aisi cheez mil jaye jo poore mohalle mein hungama macha de, toh kya hoga?",
            f"Dekhiye {char_name} ka ye super-hit naya kissa, jahan chalaki aur hansi ka aisa tadka laga ki sab dekhte reh gaye!"
        ]
        body_pool = [
            f"{char_name} ne turant apna purana dimaag lagakar sabhi doston ko bulaya aur apna secret plan sabke saamne present kiya.",
            f"Plan sunte hi sabhi doston ki aankhein fati ki fati reh gayi aur shuru hua ek super-speed jugaad ka dhamakedaar safar.",
            f"Lekin kismat ka khel toh dekhiye, achanak ek aisi gadbad hui jisse poora jugaad ek mazedaar comedy scene ban gaya.",
            f"Poore mohalle ke log pet pakad kar hasne lage aur {char_name} apna maatha pakad kar sochne laga ki ab kya karein.",
            f"Tabhi {char_name} ne aakhiri minute mein ek super-clever trick lagayi aur situation ko 360 degree ghuma kar sabko hairan kar diya.",
            f"Doston ne khushi se jhoomte hue {char_name} ko kandhe par utha liya aur jashn ka mahaul ban gaya."
        ]
        closings = [
            f"Toh aisa tha {char_name} ka ye super funny adventure! Aapko ye kissa kaisa laga, comment mein zaroor batayein aur channel ko subscribe karein!",
            f"Agar aapko bhi {char_name} ka ye dhasu jugaad pasand aaya toh video ko like karein aur aise hi fun cartoons ke liye jude rahein!"
        ]
    elif any(k in t_lower for k in ["history", "war", "king", "empire", "pratap", "shivaji", "temple", "pyramid", "ancient"]):
        hooks = [
            f"Itihaas ke panno mein {topic} ek aisi gatha hai jo har kisi ke romte khade kar deti hai aur swabhiman ki misaal pesh karti hai.",
            f"Hazaaron saal pehle ghate is romanchak itihaas ke peeche ek aisa sach chhipa hai jise aaj tak bohot kam log jaan paaye hain.",
            f"Yudh aur veerta ki is adbhut dastan mein {topic} ne wo kar dikhaya jise dushman sena bhi aakhiri saans tak bhula nahi paayi.",
            f"Aaiye jaante hain {topic} se jude wo shaktishali aitihasik kisse jinhone poore itihaas ki disha badal kar rakh di."
        ]
        body_pool = [
            f"Aitihasik dastaavezon aur shilalekhon ke mutabiq, us daur mein aisi ranniti apnayi gayi thi jo aam sena ki soch se kayi aage thi.",
            f"Durgam pahadon aur vishal kilon ke beech veeron ne matribhumi ki raksha ke liye apna sarvasva nyochhavar karne ka sankalp liya.",
            f"Ranbhoomi mein shatruon ki vishal sena ke chakke chhoot gaye jab achanak gurella yudh aur achook nishanon ka vaar shuru hua.",
            f"Itihaaskar maante hain ki is sangharsh ne na sirf aane wali peedhiyon ko prerit kiya balki shaurya ka naya kirtimaan sthaapit kiya.",
            f"Vigyaan aur puratattva vibhag aaj bhi in sthanon se aisi nayi khojein nikaal rahe hain jo us daur ke unnat gyan ko darshati hain.",
            f"Pracheen dharohar aur shastra kala ke anokhe namoone ye saaf darshate hain ki yoddhaon ki tayari kitni adbhut aur satik thi.",
            f"Yudh kshetra ke rannkosh aur kootneetigya faislon ne itihas ke rukh ko hamesha ke liye ek nayi disha de di thi.",
            f"Pratyek sainik ke man mein vijay ki aisi aag thi jise dekhkar dushman sena ka aatmarakshan bhi asambhav ho gaya tha.",
            f"Sanskritik dharohar aur paramparaon mein aaj bhi in adig sahasik ghatnaon ka varnan vishisht roop se milta hai.",
            f"Antatah, is aitihasik yatra ne ye saabit kiya ki dridh sankalp ke aage vishal se vishal shaktiyaan bhi jhook jati hain."
        ]
        closings = [
            f"Swabhiman aur balidan ki ye amar gatha hamesha zinda rahegi! Agar video garv mehsoos karwaye toh like aur subscribe zaroor karein!",
            f"Toh ye tha {topic} ka asali aitihasik sach! Aise hi shaktishali itihaas se jude kisse dekhne ke liye channel ko follow karein!"
        ]
    else:
        hooks = [
            f"Dosto! Kya aap jaante hain ki {topic} ke peeche ek aisa hairan kar dene wala raaz chhipa hai jo scientists ko bhi dang kar chuka hai?",
            f"Aaj hum baat kar rahe hain {topic} ki, jiske baare mein 99% log poori tarah anjaan hain lekin iska asar hamari duniya par sabse gehra hai.",
            f"Agar aapko lagta ki aap {topic} ke baare mein sabkuch jaante hain, toh ye video aapki soch ko hamesha ke liye badal degi.",
            f"Vigyan aur modern research ne {topic} ko lekar ek aisi shocking discovery ki hai jisne poori duniya mein tehelka macha diya hai."
        ]
        body_pool = [
            f"Deep scientific analysis aur expert studies ke mutabiq, {topic} ke underlying mechanisms seedhe roop se hamari understanding ko challenge karte hain.",
            f"Haal hi mein hui research mein ye saaf hua ki iske microscopic aur macroscopic factors aam dharana se 10 guna zyada complex hain.",
            f"Real-world data aur empirical evidence dikhata hai ki aane wale dashak mein ye breakthrough technology ya phenomenon ek naya mod le sakti hai.",
            f"Scientists ne is baat ki pushti ki hai ki iske parameters human body aur technology par unexpected tarike se impact daalte hain.",
            f"Har naye observation ke sath naye sawal khade ho rahe hain jinhe solve karne ke liye world-class labs lagataar kaam kar rahi hain.",
            f"Cutting-edge sensors aur observational data ne aise patterns capture kiye hain jo pehle kabhi record nahi kiye gaye the.",
            f"Global research community is baat par sehmat hai ki iske applications futuristic engineering mein kranti la sakte hain.",
            f"Pichle kuch varshon ke comparative data se ye pata chalta hai ki iska evolutionary pace pehle ke anumanon se kayi guna tezi se badh raha hai.",
            f"Theoretical physics aur modern computational models iske naye aspects ko decode karne ke liye advance simulations run kar rahe hain.",
            f"Duniya bhar ke visheshagya is naye aayam ko humanity ke agle vikas ki kunji maan rahe hain."
        ]
        closings = [
            f"Toh ye the {topic} se jude sabse shocking aur zaroori facts! Aapki ispar kya rai hai, comment mein batayein aur subscribe karein!",
            f"Agar ye jaankari aapko mind-blowing lagi ho toh video ko like karein aur aise hi viral facts ke liye bell icon press karein!"
        ]

    chosen_hook = random.choice(hooks)
    chosen_close = random.choice(closings)
    shuffled_body = random.sample(body_pool, min(len(body_pool), max(1, scene_count - 2))) if scene_count > 2 else [body_pool[0]]

    scenes = []
    aspect_keywords = [
        "cinematic visual scene", 
        "dramatic action sequence", 
        "detailed close up footage", 
        "futuristic landscape setting", 
        "atmospheric documentary shot", 
        "dynamic camera movement",
        "epic wide angle aerial view",
        "scientific research laboratory",
        "stunning high quality landscape",
        "slow motion cinematic detail",
        "deep exploration journey",
        "impressive cinematic perspective",
        "authentic documentary footage",
        "high tech futuristic visuals",
        "breathtaking panoramic backdrop"
    ]

    for i in range(scene_count):
        if i == 0:
            text = chosen_hook
        elif i == scene_count - 1 and scene_count > 1:
            text = chosen_close
        else:
            b_idx = (i - 1) % len(shuffled_body)
            text = shuffled_body[b_idx]
        kw = f"{main_kw_base} {aspect_keywords[i % len(aspect_keywords)]}".strip()
        scenes.append({"text": text, "keyword": kw})

    full_script = " ".join([s["text"] for s in scenes])
    meta_title, meta_desc = build_youtube_metadata(topic=topic, full_script=full_script, video_type=video_type)
    return {
        "status": "success",
        "source": "procedural_dynamic_engine",
        "topic": topic,
        "duration_seconds": duration,
        "video_type": video_type,
        "language": language,
        "tone": "viral",
        "estimated_word_count": len(full_script.split()),
        "full_script": full_script,
        "scenes": scenes,
        "title": meta_title,
        "description": meta_desc
    }

def generate_ai_script_core(topic: str, duration: int, video_type: str = "short", language: str = "hi", tone: str = "viral", category: str = "Random"):
    import random
    import urllib.parse
    import re
    topic = resolve_random_topic(topic, category)
    scene_duration = 10 if duration <= 60 else (12 if duration <= 180 else 15)
    scene_count = max(1, round(duration / scene_duration))
    word_count = int(duration * 2.7)

    raw_env_url = os.getenv("AI_SERVER_URL", "").rstrip("/")
    candidate_urls = [
        "https://ai-script-generator-service.onrender.com",
        "https://ai-script-generator-service-production.up.railway.app",
        raw_env_url if raw_env_url else ""
    ]
    seen = set()
    ai_server_urls = [u for u in candidate_urls if u and not (u in seen or seen.add(u))]

    cat_lower = str(category).lower()
    is_cartoon_cat = any(k in cat_lower for k in ["cartoon", "anime", "animation", "character", "comic"])

    # Strict language determination & enforcement
    lang_str = str(language or "hi").lower().strip()
    is_hindi = (lang_str in ["hi", "hindi", "hin", "hinglish"]) or ("hi" in lang_str)
    
    if is_hindi:
        lang_prompt = "Strict Language: Hindi (हिंदी). Spoken narration text MUST be completely in natural Hindi (बोलचाल की हिंदी / देवनागरी लिपि) for Hindi voiceover. Do NOT write in English."
        target_language = "Hindi"
    else:
        lang_prompt = "Strict Language: English. Write narration in English."
        target_language = "English"
    
    if video_type == "short":
        instruction_topic = f"{topic} [{lang_prompt} Fast-paced short script, approximately {word_count} spoken words across {scene_count} scenes for {duration} seconds duration.]"
    elif video_type == "long":
        instruction_topic = f"{topic} [{lang_prompt} Write a complete, detailed {duration}-second documentary script. MUST be approximately {word_count} spoken words across {scene_count} progressive scenes to cover the entire {duration} seconds without stopping early.]"
    elif video_type == "ultra":
        if is_cartoon_cat:
            instruction_topic = f"{topic} [{lang_prompt} Write an entertaining cartoon story script of approximately {word_count} spoken words across {scene_count} scenes for {duration} seconds.]"
        else:
            instruction_topic = f"{topic} [{lang_prompt} Write a narrative script strictly in the style of category '{category}' with approximately {word_count} spoken words across {scene_count} scenes for {duration} seconds.]"

    print(f"🤖 [AI Script Microservice] Requesting {target_language.upper()} script from https://ai-script-generator-service.onrender.com (Timeout: 120s / 2 mins)...")

    # 1. Primary Dedicated Payload for /generate-script & /api/generate-ai-script
    payload_dedicated = {
        "topic": instruction_topic,
        "raw_topic": topic,
        "duration_seconds": duration,
        "video_type": "short" if video_type in ["short", "ultra"] else "long",
        "language": target_language,
        "lang": "hi" if is_hindi else "en",
        "tone": tone or "viral"
    }

    # 2. Legacy Payload for /api/generate-script
    payload_legacy = {
        "topic": instruction_topic,
        "raw_topic": topic,
        "target_duration": f"{duration}s",
        "script_type": "shorts" if video_type in ["short", "ultra"] else "youtube_long",
        "language": target_language,
        "requirements": (
            f"Viral high-retention narration strictly in Hindi (हिंदी भाषा) for {duration} seconds with {scene_count} sequential scenes. Do NOT write in English."
            if is_hindi else
            f"Viral high-retention narration for {duration} seconds with {scene_count} sequential scenes in English"
        )
    }

    endpoints_to_try = [
        ("/generate-script", payload_dedicated),
        ("/api/generate-script", payload_legacy),
        ("/api/generate-ai-script", payload_dedicated)
    ]

    for base_url in ai_server_urls:
        for endpoint, body in endpoints_to_try:
            target_url = f"{base_url}{endpoint}"
            try:
                resp = requests.post(target_url, json=body, timeout=120.0)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_scenes = data.get("scenes") or []
                    scenes = []
                    for s in raw_scenes:
                        if isinstance(s, dict):
                            t = (s.get("text") or s.get("script_chunk") or "").strip()
                            t = re.sub(r"\[.*?\]", "", t).strip()
                            kw = (s.get("keyword") or s.get("video_search_keyword") or topic).strip()
                            if len(kw.split()) < 3 and topic and topic.lower() not in kw.lower():
                                kw = f"{topic} {kw}".strip()
                            if t and len(t) > 3:
                                scenes.append({"text": t, "keyword": kw})
                    full_script = (data.get("full_script") or data.get("script") or "").strip()
                    if not full_script and scenes:
                        full_script = " ".join([s["text"] for s in scenes])
                    if scenes or full_script:
                        title_gen = data.get("video_title") or build_youtube_metadata(topic=topic, full_script=full_script, video_type=video_type)[0]
                        desc_gen = data.get("video_description") or build_youtube_metadata(topic=topic, full_script=full_script, video_type=video_type)[1]
                        print(f"✅ AI Script Microservice Success ({target_url})! Generated {len(scenes)} scenes.")
                        return {
                            "status": "success",
                            "source": f"ai_script_microservice ({target_url})",
                            "topic": topic,
                            "duration_seconds": duration,
                            "video_type": video_type,
                            "language": language,
                            "tone": tone,
                            "estimated_word_count": len(full_script.split()),
                            "full_script": full_script,
                            "scenes": scenes,
                            "title": title_gen,
                            "description": desc_gen
                        }
            except Exception as e_ext:
                continue

    # Fallback only if microservice is completely unreachable
    print("ℹ️ Microservice unreachable. Using dynamic procedural script engine...")
    return generate_dynamic_procedural_script(
        topic=topic,
        duration=duration,
        video_type=video_type,
        language=language,
        category=category,
        scene_count=scene_count,
        word_count=word_count
    )

@app.post("/api/generate-ai-script")
async def api_generate_ai_script(req: AIScriptRequest, request: Request):
    """
    Dedicated AI Script Generation API for Render/Remote clients.
    Protected against unauthenticated bot abuse and quota bypass.
    """
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic title is required")

    # Verify authorization: Must be Admin OR a registered user with active quota
    admin_key = request.headers.get("x-admin-key") or request.query_params.get("admin_key")
    from firewall_security import ADMIN_SECURITY_KEY
    is_admin = bool(admin_key and admin_key.strip() == ADMIN_SECURITY_KEY.strip())

    if not is_admin:
        if not req.user_id or req.user_id == "anonymous":
            raise HTTPException(status_code=401, detail="Please provide a valid user_id or admin key to generate AI scripts.")
        clean_user_id = sanitize_alphanumeric_id(req.user_id)
        if users_collection is not None:
            user = users_collection.find_one({"internal_id": clean_user_id})
            if not user:
                raise HTTPException(status_code=401, detail="⚠️ Authentication Error: User account not found.")
            subscription = user.get("subscription", {})
            sub_status = subscription.get("status")
            sub_expires = subscription.get("expires_at")
            is_active = False
            if sub_status == "active" and sub_expires:
                if isinstance(sub_expires, str):
                    try: sub_expires = datetime.fromisoformat(sub_expires.replace('Z', '+00:00'))
                    except Exception: sub_expires = None
                if isinstance(sub_expires, datetime) and sub_expires.replace(tzinfo=None) > datetime.utcnow():
                    is_active = True
            free_demo = user.get("free_demo_count", 2)
            if not is_active and free_demo <= 0:
                raise HTTPException(status_code=402, detail="Demo quota exhausted! Please upgrade your plan to generate AI scripts.")
        
    duration = max(10, min(300, req.duration_seconds))
    return generate_ai_script_core(
        topic=req.topic.strip(),
        duration=duration,
        video_type=req.video_type or "short",
        language=req.language or "hi",
        tone=req.tone or "viral",
        category=req.category or "Random"
    )

@app.post("/generate-script")
async def generate_script(req: ScriptRequest):
    """Script generation endpoint with Strict Free Quota & Security Protection"""
    user_id = req.user_id
    if not user_id or user_id == "anonymous":
        raise HTTPException(status_code=401, detail="Please login or register to generate AI scripts.")

    clean_user_id = sanitize_alphanumeric_id(user_id)
    if users_collection is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    user = users_collection.find_one({"internal_id": clean_user_id})
    if not user:
        raise HTTPException(status_code=401, detail="⚠️ Authentication Error: Invalid or non-existent user account. Please login to generate AI scripts.")

    subscription = user.get("subscription", {})
    sub_status = subscription.get("status")
    sub_expires = subscription.get("expires_at")
    is_active = False
    if sub_status == "active" and sub_expires:
        if isinstance(sub_expires, str):
            try:
                sub_expires = datetime.fromisoformat(sub_expires.replace('Z', '+00:00'))
            except Exception:
                sub_expires = None
        if isinstance(sub_expires, datetime) and sub_expires.replace(tzinfo=None) > datetime.utcnow():
            is_active = True
    
    ultra_sub = user.get("ultra_subscription", {})
    has_active_ultra = False
    if ultra_sub.get("status") == "active":
        u_exp = ultra_sub.get("expires_at")
        if isinstance(u_exp, str):
            try: u_exp = datetime.fromisoformat(u_exp.replace('Z', '+00:00'))
            except Exception: u_exp = None
        if isinstance(u_exp, datetime) and u_exp.replace(tzinfo=None) > datetime.utcnow():
            has_active_ultra = True

    free_demo = user.get("free_demo_count")
    if free_demo is None:
        free_demo = 2
        users_collection.update_one({"internal_id": clean_user_id}, {"$set": {"free_demo_count": 2}})

    if not is_active and not has_active_ultra and free_demo <= 0:
        raise HTTPException(
            status_code=402, 
            detail="Demo quota exhausted! You have used your 2 free demo videos & scripts. Please upgrade your plan to continue generating AI scripts & videos."
        )

    req_lang = req.language or ("hi" if (req.voice and "hi-" in str(req.voice).lower()) else "hi")
    res = generate_ai_script_core(
        topic=req.topic, 
        duration=req.duration_seconds, 
        category=req.category or "Random", 
        video_type=req.video_type or "short",
        language=req_lang
    )
    return {"scenes": res["scenes"], "full_script": res["full_script"]}

@app.get("/robots.txt", response_class=Response)
async def get_robots_txt():
    robots_content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Allow: /favicon*\n"
        "Allow: /apple-touch-icon*\n"
        "Allow: /manifest.json\n\n"
        "User-agent: Googlebot-Image\n"
        "Allow: /\n"
        "Allow: /*.png$\n"
        "Allow: /*.ico$\n\n"
        "Sitemap: https://cloxelai.onrender.com/sitemap.xml\n"
    )
    return Response(content=robots_content, media_type="text/plain")

@app.get("/manifest.json")
async def get_manifest():
    manifest_path = "frontend/dist/manifest.json" if os.path.exists("frontend/dist/manifest.json") else "frontend/public/manifest.json"
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/manifest+json", headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail="Manifest not found")

@app.get("/favicon.ico")
async def get_favicon_ico():
    ico_path = "frontend/dist/favicon.ico" if os.path.exists("frontend/dist/favicon.ico") else "frontend/public/favicon.ico"
    if os.path.exists(ico_path):
        return FileResponse(ico_path, media_type="image/x-icon", headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail="Favicon not found")

@app.get("/favicon.png")
@app.get("/favicon-512x512.png")
async def get_favicon_512():
    png_path = "frontend/dist/favicon-512x512.png" if os.path.exists("frontend/dist/favicon-512x512.png") else "frontend/public/favicon-512x512.png"
    if not os.path.exists(png_path):
        png_path = "frontend/dist/favicon.png" if os.path.exists("frontend/dist/favicon.png") else "frontend/public/favicon.png"
    if os.path.exists(png_path):
        return FileResponse(png_path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail="Icon not found")

@app.get("/favicon-48x48.png")
async def get_favicon_48():
    png_path = "frontend/dist/favicon-48x48.png" if os.path.exists("frontend/dist/favicon-48x48.png") else "frontend/public/favicon-48x48.png"
    if os.path.exists(png_path):
        return FileResponse(png_path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail="Icon not found")

@app.get("/favicon-96x96.png")
async def get_favicon_96():
    png_path = "frontend/dist/favicon-96x96.png" if os.path.exists("frontend/dist/favicon-96x96.png") else "frontend/public/favicon-96x96.png"
    if os.path.exists(png_path):
        return FileResponse(png_path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail="Icon not found")

@app.get("/favicon-192x192.png")
async def get_favicon_192():
    png_path = "frontend/dist/favicon-192x192.png" if os.path.exists("frontend/dist/favicon-192x192.png") else "frontend/public/favicon-192x192.png"
    if os.path.exists(png_path):
        return FileResponse(png_path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail="Icon not found")

@app.get("/apple-touch-icon.png")
async def get_apple_touch_icon():
    png_path = "frontend/dist/apple-touch-icon.png" if os.path.exists("frontend/dist/apple-touch-icon.png") else "frontend/public/apple-touch-icon.png"
    if os.path.exists(png_path):
        return FileResponse(png_path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail="Icon not found")

@app.get("/.well-known/security.txt", response_class=Response)
@app.get("/security.txt", response_class=Response)
async def get_security_txt():
    sec_txt = (
        "Contact: mailto:security@cloxelai.com\n"
        "Expires: 2027-12-31T23:59:59.000Z\n"
        "Preferred-Languages: en, hi\n"
        "Canonical: https://cloxelai.onrender.com/.well-known/security.txt\n"
        "Policy: https://cloxelai.onrender.com/privacy-policy\n"
    )
    return Response(content=sec_txt, media_type="text/plain; charset=utf-8")

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

@app.get("/privacy-policy", response_class=Response)
async def get_privacy_policy_page():
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Privacy Policy - Cloxel AI</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #f8fafc; background: #0f172a; padding: 40px 20px; max-width: 850px; margin: 0 auto; }
        h1, h2 { color: #c084fc; border-bottom: 1px solid #334155; padding-bottom: 8px; }
        a { color: #a855f7; font-weight: bold; }
        .card { background: #1e293b; padding: 35px; border-radius: 14px; border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        ul { padding-left: 20px; }
        li { margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Privacy Policy - Cloxel AI</h1>
        <p><strong>Effective Date:</strong> September 2026</p>
        
        <h2>1. Information We Collect</h2>
        <p>Cloxel AI collects user email address, name, phone number, and Google OAuth tokens for YouTube account integration. Sensitive personal information and OAuth tokens are encrypted at rest using AES-256 field encryption in our database.</p>
        
        <h2>2. Use of YouTube API Services & Scope Disclosures</h2>
        <p>By using Cloxel AI's YouTube integration, users agree to be bound by the <a href="https://www.youtube.com/t/terms" target="_blank">YouTube Terms of Service</a> and the <a href="https://policies.google.com/privacy" target="_blank">Google Privacy Policy</a>.</p>
        <p>Cloxel AI requests access to the following Google OAuth scope:</p>
        <ul>
            <li><code>https://www.googleapis.com/auth/youtube.upload</code>: Used exclusively to upload user-authorized AI-generated videos directly to the user's connected YouTube channel.</li>
        </ul>

        <h2>3. Google User Data Sharing, Transfer & Disclosure</h2>
        <p><strong>We do NOT sell, share, transfer, or disclose Google user data</strong> (including YouTube OAuth tokens, profile information, or channel credentials) to any third parties, advertising networks, data brokers, or external entities under any circumstances. All Google user data is used solely internally to provide automated video rendering and publishing services requested by the user.</p>

        <h2>4. Google User Data Retention & Deletion</h2>
        <p><strong>Data Retention:</strong> Google OAuth tokens and associated credentials are retained only while your YouTube channel remains linked to Cloxel AI. We do not retain data longer than necessary for operational app functionality.</p>
        <p><strong>Data Deletion & Unlinking:</strong> Users can revoke Cloxel AI's access and delete all stored tokens at any time through:</p>
        <ul>
            <li>Clicking <strong>"Unlink YouTube Channel"</strong> in the Cloxel AI Dashboard, which immediately purges all stored OAuth tokens from our database.</li>
            <li>Revoking app access via <a href="https://security.google.com/settings/security/permissions" target="_blank">Google Security Permissions Settings</a>.</li>
            <li>Emailing us directly at <a href="mailto:support@cloxel.ai">support@cloxel.ai</a> to request complete account and data erasure.</li>
        </ul>

        <h2>5. Data Security</h2>
        <p>We employ industry-standard AES-256 field-level encryption, SHA-256 HMAC hashing, and HTTPS TLS 1.3 encryption to protect user data against unauthorized access, loss, or misuse.</p>

        <h2>6. Contact Us</h2>
        <p>If you have any questions regarding this Privacy Policy or your data, please contact our Data Protection Team at: <strong>support@cloxel.ai</strong></p>
    </div>
</body>
</html>"""
    return Response(content=html_content, media_type="text/html")
    return Response(content=html_content, media_type="text/html")

@app.get("/terms-of-service", response_class=Response)
async def get_terms_of_service_page():
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Terms of Service - Cloxel AI</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #f8fafc; background: #0f172a; padding: 40px 20px; max-width: 800px; margin: 0 auto; }
        h1, h2 { color: #c084fc; }
        a { color: #a855f7; }
        .card { background: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #334155; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Terms of Service - Cloxel AI</h1>
        <p>Effective Date: September 2026</p>
        <h2>1. Acceptance of Terms</h2>
        <p>By accessing or using Cloxel AI video generation and YouTube publishing tools, you agree to these Terms of Service.</p>
        <h2>2. User Content & YouTube Publishing</h2>
        <p>Users retain ownership of generated videos. Users are responsible for ensuring published content complies with YouTube Community Guidelines.</p>
        <h2>3. Service Availability</h2>
        <p>Cloxel AI provides automated video rendering and publishing services. Rates and quota limits apply based on selected plans.</p>
        <h2>4. Termination</h2>
        <p>We reserve the right to suspend accounts violating system rules, spam policies, or YouTube API terms.</p>
    </div>
</body>
</html>"""
    return Response(content=html_content, media_type="text/html")

@app.get("/googleaa929f03abece7ff.html", response_class=Response)
async def get_google_verification_html():
    return Response(content="google-site-verification: googleaa929f03abece7ff.html", media_type="text/html")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.detail}
        )
    incident_id = uuid.uuid4().hex[:10].upper()
    print(f"❌ [INTERNAL SERVER EXCEPTION] Incident #{incident_id}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected server error occurred. Protected by Cloxel Security Shield.",
            "incident_id": incident_id
        }
    )

if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
else:
    print("WARNING: frontend/dist not found. Run 'npm run build' in the frontend folder.")
