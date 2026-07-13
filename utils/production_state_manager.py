import json
import os
from pathlib import Path

# ==========================================================
# SHARP TALK STUDIO
# PRODUCTION STATE MANAGER -- Dynamic project support
#
# Set project in PowerShell before running:
#   $env:SHARP_TALK_PROJECT="Spain vs Portugal FIFA 2026"
#
# Falls back to "Premier League Final" if not set.
# ==========================================================

PROJECT_NAME    = os.getenv("SHARP_TALK_PROJECT", "Premier League Final")
BASE_DIR        = Path("projects") / PROJECT_NAME
PRODUCTION_JSON = BASE_DIR / "master_production.json"


def load_production_json():
    if not PRODUCTION_JSON.exists():
        raise FileNotFoundError(
            f"master_production.json not found: {PRODUCTION_JSON}\n"
            f"Make sure you set the project name:\n"
            f'$env:SHARP_TALK_PROJECT="Your Project Name"'
        )
    with open(PRODUCTION_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_production_json(data):
    with open(PRODUCTION_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_next_pending_scene():
    """Returns the next scene with status == 'pending' only."""
    data = load_production_json()
    for scene in data.get("scenes", []):
        if scene.get("status", "pending") == "pending":
            return data, scene
    return data, None


def get_next_actionable_scene():
    """
    Returns the next scene that needs any action:
    pending → image_generated → video_generated → voice_generated → completed
    Used by production_engine to drive the full pipeline.
    """
    data = load_production_json()
    for scene in data.get("scenes", []):
        if scene.get("status", "pending") != "completed":
            return data, scene
    return data, None


def update_scene_asset(scene_number, key, value, **kwargs):
    data = load_production_json()
    for scene in data.get("scenes", []):
        if scene.get("scene_number") == scene_number:
            scene[key] = value
            break
    save_production_json(data)


def mark_scene_completed(scene_number):
    data = load_production_json()
    for scene in data.get("scenes", []):
        if scene.get("scene_number") == scene_number:
            scene["status"] = "completed"
            break
    save_production_json(data)


if __name__ == "__main__":
    print(f"\nProduction State Manager ✅")
    print(f"Project : {PROJECT_NAME}")
    print(f"JSON    : {PRODUCTION_JSON}")
    data, scene = get_next_pending_scene()
    if scene:
        print(f"Next pending scene: {scene['scene_number']}")
    else:
        print("No pending scenes — all images generated or completed ✅")