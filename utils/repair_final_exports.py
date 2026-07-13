from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from utils.production_state_manager import load_production_json, save_production_json

PROJECT_NAME = "Premier League Final"

BASE_DIR = Path("projects") / PROJECT_NAME
EXPORT_DIR = BASE_DIR / "06_Final_Export"
FINAL_DIR = BASE_DIR / "07_Final_Movie"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

FINAL_MOVIE = FINAL_DIR / "Premier_League_Final_Complete_FIXED.mp4"

data = load_production_json()

final_scene_files = []

for scene in data["scenes"]:
    scene_number = scene["scene_number"]

    video_path = Path(scene["generated_video"])
    voice_path = Path(scene["generated_voice"])

    output_path = EXPORT_DIR / f"Scene_{scene_number:03d}_Final_FIXED.mp4"

    print(f"\nRepairing Scene {scene_number}")

    video = VideoFileClip(str(video_path))
    voice = AudioFileClip(str(voice_path))

    video_duration = video.duration
    voice_duration = voice.duration

    print("Video duration:", video_duration)
    print("Voice duration:", voice_duration)

    if voice_duration > video_duration:
        voice = voice.subclipped(0, video_duration)

    final_scene = video.with_audio(voice)

    final_scene.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio_codec="aac"
    )

    video.close()
    voice.close()
    final_scene.close()

    scene["final_scene_video"] = str(output_path)
    final_scene_files.append(output_path)

print("\nBuilding fixed final movie...")

clips = [VideoFileClip(str(file)) for file in final_scene_files]

final_movie = concatenate_videoclips(clips, method="compose")

final_movie.write_videofile(
    str(FINAL_MOVIE),
    fps=30,
    codec="libx264",
    audio_codec="aac"
)

for clip in clips:
    clip.close()

final_movie.close()

data["project"]["final_movie"] = str(FINAL_MOVIE)
save_production_json(data)

print("\n=========================================")
print("FIXED FINAL MOVIE CREATED ✅")
print(FINAL_MOVIE)
print("=========================================")