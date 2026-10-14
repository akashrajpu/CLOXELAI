from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
import uuid
import os
import json
import threading

from video_editor import merge_and_export
from audio_engine import make_audio
from video_fetcher import fetch_videos 
from ai_script import generate_daily_script
from datetime import datetime, timedelta

app = FastAPI(title="Cloxel AI Video Generation Engine")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class VideoRequest(BaseModel):
    script: str
    topic: str
    duration: int
    font_name: str = "BebasNeue-Regular.ttf"
    text_color: str = "white"
    voice_id: str = "hi-IN-MadhurNeural"
    username: str = "guest"
    clip_count: int = 0
    mode: str = "standard"
    filter_style: str = "warm_epic"
    aspect_ratio: str = "9:16"

class ScheduleRequest(BaseModel):
    username: str
    topic: str
    target_time: str = "12:00"
    duration: int = 30
    clip_count: int = 0
    font_name: str = "BebasNeue-Regular.ttf"
    text_color: str = "white"
    voice_id: str = "hi-IN-MadhurNeural"
    mode: str = "standard"
    filter_style: str = "warm_epic"
    aspect_ratio: str = "9:16"

jobs = {}
TOPICS_FILE = "topics.json"

def load_topics():
    if os.path.exists(TOPICS_FILE):
        with open(TOPICS_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_topics(topics):
    with open(TOPICS_FILE, "w") as f:
        json.dump(topics, f, indent=4)

scheduler = BackgroundScheduler()

def refresh_scheduler():
    scheduler.remove_all_jobs()
    topics = load_topics()
    for t in topics:
        target_time_str = t.get("target_time", "12:00")
        try:
            target_dt = datetime.strptime(target_time_str, "%H:%M")
            run_dt = target_dt - timedelta(minutes=20)
            
            scheduler.add_job(
                generate_single_video_job,
                'cron',
                hour=run_dt.hour,
                minute=run_dt.minute,
                args=[t]
            )
            print(f"✅ Scheduled '{t['topic']}' daily at {run_dt.hour:02d}:{run_dt.minute:02d} (Target Video Time: {target_time_str})")
        except Exception as e:
            print(f"❌ Error scheduling topic {t['topic']}: {e}")

def generate_single_video_job(topic_data):
    username = topic_data.get("username", "guest")
    topic_name = topic_data["topic"]
    duration = topic_data.get("duration", 30)
    clip_count_override = topic_data.get("clip_count", 0)
    print(f"🌅 Generating script & video for user '{username}' on topic: {topic_name}")
    
    new_script = generate_daily_script(topic_name, duration)
    
    req = VideoRequest(
        script=new_script,
        topic=topic_name,
        duration=duration,
        font_name=topic_data.get("font_name", "BebasNeue-Regular.ttf"),
        text_color=topic_data.get("text_color", "white"),
        voice_id=topic_data.get("voice_id", "hi-IN-MadhurNeural"),
        username=username,
        clip_count=clip_count_override,
        mode=topic_data.get("mode", "standard"),
        filter_style=topic_data.get("filter_style", "warm_epic"),
        aspect_ratio=topic_data.get("aspect_ratio", "9:16")
    )
    
    job_id = f"daily_{uuid.uuid4().hex[:8]}"
    threading.Thread(target=process_video_task, args=(job_id, req)).start()

@app.on_event("startup")
def startup_event():
    scheduler.start()
    refresh_scheduler()
    print("📅 Daily Video Scheduler Started!")

def process_video_task(job_id, data: VideoRequest):
    try:
        jobs[job_id] = {"status": "Generating Master Audio...", "username": data.username, "topic": data.topic}
        a_path = f"voice_{job_id}.mp3"
        out_path = f"final_{job_id}.mp4"

        make_audio(data.script, a_path, voice_id=data.voice_id)
        
        if data.aspect_ratio == "16:9":
            target_size = (1920, 1080)
        elif data.aspect_ratio == "1:1":
            target_size = (1080, 1080)
        else:
            target_size = (1080, 1920)

        if data.clip_count > 0:
            clip_count = data.clip_count
        else:
            d = data.duration
            if d <= 15: clip_count = 2
            elif d <= 30: clip_count = 4
            elif d <= 40: clip_count = 5
            elif d <= 50: clip_count = 7
            else: clip_count = 10 

        jobs[job_id]["status"] = f"Fetching {clip_count} media assets for {d}s video..."
        video_clips = fetch_videos(data.topic, job_id, count=clip_count)

        if not video_clips:
            raise Exception("Media assets download nahi ho payin")

        jobs[job_id]["status"] = f"Rendering {data.mode.upper()} Video ({data.aspect_ratio})..."
        scene_list = []
        for v_path in video_clips:
            scene_list.append({
                "video": v_path,
                "audio": a_path,
                "text": data.script
            })
        
        merge_and_export(
            scene_list=scene_list, 
            output_name=out_path, 
            font_path=f"./fonts/{data.font_name}" if os.path.exists(f"./fonts/{data.font_name}") else "./fonts/Arial.ttf", 
            color=data.text_color,
            target_size=target_size,
            mode=data.mode,
            filter_style=data.filter_style
        ) 

        jobs[job_id] = {"status": "completed", "file": out_path}
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        jobs[job_id] = {"status": "failed", "error": str(e)}

@app.post("/generate")
async def generate(req: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued"}
    background_tasks.add_task(process_video_task, job_id, req)
    return {"job_id": job_id}

@app.post("/schedule_topic")
async def schedule_topic(req: ScheduleRequest):
    topics = load_topics()
    if any(t.get("username") == req.username and t["topic"].lower() == req.topic.lower() for t in topics):
        return {"status": "Already scheduled for this user", "topic": req.topic}
    
    topics.append(req.dict())
    save_topics(topics)
    refresh_scheduler()
    return {"status": "Topic scheduled successfully for daily videos", "topic": req.topic, "runs_at_approx": f"20 mins before {req.target_time}"}

@app.get("/user_videos/{username}")
async def get_user_videos(username: str):
    user_jobs = []
    for j_id, j_data in jobs.items():
        if j_data.get("username") == username:
            user_jobs.append({"job_id": j_id, **j_data})
    return {"username": username, "videos": user_jobs}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})

@app.get("/download/{job_id}")
async def download(job_id: str):
    job = jobs.get(job_id)
    if job and job.get("status") == "completed":
        return FileResponse(job["file"])
    return {"error": "File not ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
