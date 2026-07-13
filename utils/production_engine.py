import os
import subprocess
import sys
import traceback
from pathlib import Path

from moviepy import VideoFileClip, concatenate_videoclips

from utils.production_state_manager import (
    get_next_actionable_scene,
    PROJECT_NAME,
    load_production_json,
    save_production_json,
)

# ==========================================================
# SHARP TALK STUDIO
# PRODUCTION ENGINE -- Hybrid Pipeline
#
# Set project before running:
#   $env:SHARP_TALK_PROJECT="Spain vs Portugal FIFA 2026"
#   $env:GEMINI_API_KEY="your_google_key"
#   $env:RUNPOD_API_KEY="your_runpod_key"
#   $env:RUNPOD_POD_ID="vqjslvtee3qje8"
#   python -m utils.production_engine
# ==========================================================

BASE_DIR       = Path("projects") / PROJECT_NAME
FINAL_MOVIE_DIR = BASE_DIR / "07_Final_Movie"
FINAL_MOVIE_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MOVIE    = FINAL_MOVIE_DIR / f"{PROJECT_NAME}_Complete.mp4"

KEN_BURNS_TYPES = {"ken_burns", "youtube_short", "instagram_reel"}
AI_VIDEO_TYPES  = {"ai_video"}


def run_module(module_name):
    print(f"\n--- RUNNING: {module_name} ---")
    result = subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=Path.cwd(),
        env={**os.environ},
    )
    if result.returncode != 0:
        raise RuntimeError(f"{module_name} failed with code {result.returncode}")


def production_complete(data):
    return all(s.get("status") == "completed"
               for s in data.get("scenes", []))


def build_final_movie():
    data = load_production_json()
    files = []

    for scene in data.get("scenes", []):
        if scene.get("type") in ("youtube_short", "instagram_reel"):
            continue
        path = scene.get("final_scene_video", "")
        if not path:
            raise FileNotFoundError(
                f"Scene {scene['scene_number']} missing final_scene_video")
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        files.append(p)

    print(f"\nAssembling {len(files)} scenes into final movie...")
    clips = []
    try:
        for f in files:
            print(f"  Adding: {f.name}")
            clips.append(VideoFileClip(str(f)))
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(str(FINAL_MOVIE), fps=30,
                              codec="libx264", audio_codec="aac")
        final.close()
    finally:
        for c in clips:
            c.close()

    data["project"]["final_movie"] = str(FINAL_MOVIE)
    data["project"]["production_status"] = "completed"
    save_production_json(data)

    print(f"\n✅ FINAL MOVIE: {FINAL_MOVIE}")


def run_production_engine():
    print("\n=========================================")
    print("SHARP TALK STUDIO")
    print(f"PROJECT: {PROJECT_NAME}")
    print("PRODUCTION ENGINE — HYBRID PIPELINE")
    print("=========================================")

    while True:
        data = load_production_json()

        if production_complete(data):
            print("\n✅ All scenes completed.")
            break

        data, scene_to_process = get_next_actionable_scene()
        if scene_to_process is None:
            break


        scene_number = scene_to_process["scene_number"]
        status       = scene_to_process.get("status", "pending")
        scene_type   = scene_to_process.get("type", "ken_burns")

        print(f"\n=========================================")
        print(f"SCENE {scene_number} | TYPE: {scene_type.upper()} | STATUS: {status}")
        print(f"=========================================")

        try:
            if status == "pending":
                run_module("utils.ai_image_generator")

            elif status == "image_generated":
                if scene_type in AI_VIDEO_TYPES:
                    print(f"→ Wan 2.2 hero shot")
                    run_module("utils.ai_video_generator")
                else:
                    print(f"→ Ken Burns (free)")
                    run_module("utils.ken_burns_generator")

            elif status == "video_generated":
                run_module("utils.ai_voice_generator")

            elif status == "voice_generated":
                run_module("utils.final_exporter")

            else:
                raise ValueError(f"Unknown status: {status}")

        except Exception as e:
            data = load_production_json()
            for scene in data.get("scenes", []):
                if scene["scene_number"] == scene_number:
                    scene["error"] = str(e)
                    break
            data["project"]["production_status"] = "error"
            save_production_json(data)

            print(f"\n❌ PRODUCTION ERROR")
            print(f"Scene  : {scene_number}")
            print(f"Type   : {scene_type}")
            print(f"Status : {status}")
            print(f"Error  : {e}")
            traceback.print_exc()
            raise SystemExit(1)

    build_final_movie()

    print("\n=========================================")
    print("✅ PRODUCTION COMPLETE")
    print(f"📁 {FINAL_MOVIE}")
    print("=========================================")


if __name__ == "__main__":
    run_production_engine()