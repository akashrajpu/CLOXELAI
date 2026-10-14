"""
===============================================================================
     OMNI VIDEO WEB SERVER (GEMINI AI MP4 GENERATOR WITH LIVE TERMINAL LOGS)
===============================================================================
Description : Web server with background job execution and live real-time
              terminal log streaming so users see exactly what the video generator
              is doing step-by-step!

Author      : Antigravity AI Engine
===============================================================================
"""

import os
import time
import uuid
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from omni_video_engine import OmniVideoEngine

app = Flask(__name__, template_folder='templates', static_folder='static')
os.makedirs('static', exist_ok=True)

video_engine = OmniVideoEngine(output_dir="static")

JOBS = {}

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
def home():
    return render_template('omni_index.html')

def run_video_job(job_id: str, prompt: str, duration: int, api_key: str, aspect_ratio: str):
    """
    Background worker thread running video generation and updating live logs.
    """
    def log_callback(message: str, progress: int):
        if job_id in JOBS:
            JOBS[job_id]['logs'].append(message)
            if progress > 0:
                JOBS[job_id]['progress'] = progress

    try:
        JOBS[job_id]['status'] = 'processing'
        result = video_engine.generate_video(
            prompt=prompt,
            target_duration=duration,
            api_key=api_key,
            aspect_ratio=aspect_ratio,
            log_callback=log_callback
        )
        JOBS[job_id]['status'] = 'completed'
        JOBS[job_id]['progress'] = 100
        JOBS[job_id]['result'] = result
    except Exception as e:
        err_msg = f"❌ [Error] Video generation failed: {str(e)}"
        print(err_msg)
        JOBS[job_id]['status'] = 'error'
        JOBS[job_id]['logs'].append(err_msg)
        JOBS[job_id]['error'] = str(e)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '').strip()
        duration = int(data.get('duration', 30))
        api_key = data.get('api_key', '').strip() or None
        aspect_ratio = data.get('aspect_ratio', '16:9')

        if not prompt:
            return jsonify({'status': 'error', 'message': 'Prompt cannot be empty'}), 400

        job_id = str(uuid.uuid4())[:8]
        JOBS[job_id] = {
            'status': 'starting',
            'progress': 0,
            'logs': [f"[{time.strftime('%H:%M:%S')}] 🎬 Job #{job_id} queued for processing..."],
            'result': None,
            'error': None
        }

        thread = threading.Thread(
            target=run_video_job,
            args=(job_id, prompt, duration, api_key, aspect_ratio),
            daemon=True
        )
        thread.start()

        return jsonify({
            'status': 'processing',
            'job_id': job_id
        })

    except Exception as e:
        print(f"[Web Server Error] {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/job_status/<job_id>', methods=['GET'])
def job_status(job_id):
    """
    Returns live progress status, percentage, and real-time terminal logs for job_id.
    """
    job = JOBS.get(job_id)
    if not job:
        return jsonify({'status': 'error', 'message': 'Job not found'}), 404

    return jsonify({
        'status': job['status'],
        'progress': job['progress'],
        'logs': job['logs'],
        'result': job['result'],
        'error': job['error']
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("=" * 70)
    print(" 🚀 Omni MP4 Video Web Server 8.0 Running at: http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host='127.0.0.1', port=5000, debug=False, load_dotenv=False)
