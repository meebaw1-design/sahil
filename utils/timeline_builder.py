from pathlib import Path

# ==========================================================
# SHARP TALK STUDIO
# TIMELINE BUILDER
# ==========================================================

PROJECT_NAME = "Premier League Final"

BASE_DIR = Path("projects") / PROJECT_NAME

IMAGE_DIR = BASE_DIR / "02_AI_Images"
VIDEO_DIR = BASE_DIR / "03_AI_Videos"
VOICE_DIR = BASE_DIR / "04_AI_Voice"
TIMELINE_DIR = BASE_DIR / "05_Timeline"

TIMELINE_DIR.mkdir(parents=True, exist_ok=True)

SCENE_NUMBER = 1

IMAGE_FILE = IMAGE_DIR / f"Scene_{SCENE_NUMBER:03d}.png"
VIDEO_FILE = VIDEO_DIR / f"Scene_{SCENE_NUMBER:03d}.mp4"
VOICE_FILE = VOICE_DIR / f"Scene_{SCENE_NUMBER:03d}.mp3"

print("\n=========================================")
print("SHARP TALK STUDIO")
print("TIMELINE BUILDER")
print("=========================================\n")

print("Checking Assets...\n")

assets_ok = True

for label, file in [
    ("Image", IMAGE_FILE),
    ("Video", VIDEO_FILE),
    ("Voice", VOICE_FILE),
]:
    if file.exists():
        print(f"✅ {label}: {file}")
    else:
        print(f"❌ {label}: Missing")
        assets_ok = False

if not assets_ok:
    raise SystemExit("\nTimeline cannot be created because assets are missing.")

timeline_file = TIMELINE_DIR / "timeline.txt"

with open(timeline_file, "w", encoding="utf-8") as f:
    f.write("SHARP TALK STUDIO TIMELINE\n")
    f.write("==========================\n\n")
    f.write(f"Scene : {SCENE_NUMBER}\n")
    f.write(f"Image : {IMAGE_FILE}\n")
    f.write(f"Video : {VIDEO_FILE}\n")
    f.write(f"Voice : {VOICE_FILE}\n")

print("\n=========================================")
print("TIMELINE CREATED SUCCESSFULLY ✅")
print(timeline_file)
print("=========================================")