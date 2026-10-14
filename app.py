from audio_engine import make_audio
from video_fetcher import fetch_videos
from video_editor import merge_and_export

def main():
    print("\n🚀 --- Zobbly Manual Engine (No-API Mode) ---")
    
    print("\n🚀 --- Cloxel Manual Engine (No-API Mode) ---")
    
    topic = "Black Holes Facts"
    print(f"🎬 Generating script for topic: '{topic}'...")
    
    raw_script = get_ai_script(topic)
    print("\n📝 Generated Script:\n", raw_script)

    parsed_scenes = parse_script_to_scenes(raw_script)
    print(f"\n🧩 Total Scenes Extracted: {len(parsed_scenes)}")

    taiyaar_scenes = []
    for idx, scene in enumerate(parsed_scenes):
        print(f"\n--- Scene {idx + 1} Processing ---")
        text = scene['text']
        kw = scene['keyword']
        
        voice_file = f"voice_{idx}.mp3"
        generate_voiceover(text, voice_file, voice_id="hi-IN-MadhurNeural")
        
        video_file = f"bg_{idx}.mp4"
        download_pexels_video(kw, video_file)

        if os.path.exists(voice_file) and os.path.exists(video_file):
            taiyaar_scenes.append({
                "text": text,
                "video_file": video_file,
                "voice_file": voice_file
            })

    if taiyaar_scenes:
        print("\n✅ Video successfully ban gayi: cloxel_manual_video.mp4")
    else:
        print("❌ Ek bhi scene taiyaar nahi ho paya!")

if __name__ == "__main__":
    main()
