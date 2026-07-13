import random
import subprocess
from pathlib import Path

from utils.production_state_manager import (
    PROJECT_NAME,
    get_next_actionable_scene,
    update_scene_asset,
)

# ==========================================================
# SHARP TALK STUDIO
# KEN BURNS GENERATOR  -- FREE, NO GPU, NO API
# Animates a still image with cinematic pan/zoom using ffmpeg.
# Used for regular scenes (type: "ken_burns") and for
# YouTube Shorts and Instagram Reels (type: "youtube_short"
# or "instagram_reel") — zero cost, runs on your own PC.
# ==========================================================

BASE_DIR = Path("projects") / PROJECT_NAME
VIDEO_DIR = BASE_DIR / "03_AI_Videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

# Output specs per scene type
SPECS = {
    "ken_burns": {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "description": "Main video (16:9 1080p)",
    },
    "youtube_short": {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "description": "YouTube Short (9:16 1080p)",
    },
    "instagram_reel": {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "description": "Instagram Reel (9:16 1080p)",
    },
}

# Ken Burns motion styles — picked randomly per scene for variety
MOTION_STYLES = [
    "zoom_in",
    "zoom_out",
    "pan_left",
    "pan_right",
    "pan_up",
    "pan_down",
    "zoom_in_pan_right",
    "zoom_in_pan_left",
    "zoom_out_pan_right",
    "zoom_out_pan_left",
]


def build_zoompan_filter(motion: str, duration: float, w: int, h: int) -> str:
    """
    Builds an ffmpeg zoompan filter string for the given motion style.
    The zoompan filter works at 25fps internally — we re-wrap to target fps.
    """
    total_frames = int(duration * 25)
    d = total_frames

    filters = {
        "zoom_in": f"zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
        "zoom_out": f"zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0015))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
        "pan_left": f"zoompan=z=1.3:x='iw/2-(iw/zoom/2)+((iw/zoom/2)*on/{d})':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
        "pan_right": f"zoompan=z=1.3:x='iw/2-(iw/zoom/2)-((iw/zoom/2)*on/{d})':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
        "pan_up": f"zoompan=z=1.3:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+((ih/zoom/2)*on/{d})':d={d}:s={w}x{h}:fps=25",
        "pan_down": f"zoompan=z=1.3:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)-((ih/zoom/2)*on/{d})':d={d}:s={w}x{h}:fps=25",
        "zoom_in_pan_right": f"zoompan=z='min(zoom+0.001,1.4)':x='iw/2-(iw/zoom/2)-((iw/zoom/2)*on/{d}/3)':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
        "zoom_in_pan_left": f"zoompan=z='min(zoom+0.001,1.4)':x='iw/2-(iw/zoom/2)+((iw/zoom/2)*on/{d}/3)':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
        "zoom_out_pan_right": f"zoompan=z='if(lte(zoom,1.0),1.4,max(1.001,zoom-0.001))':x='iw/2-(iw/zoom/2)-((iw/zoom/2)*on/{d}/3)':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
        "zoom_out_pan_left": f"zoompan=z='if(lte(zoom,1.0),1.4,max(1.001,zoom-0.001))':x='iw/2-(iw/zoom/2)+((iw/zoom/2)*on/{d}/3)':y='ih/2-(ih/zoom/2)':d={d}:s={w}x{h}:fps=25",
    }

    return filters.get(motion, filters["zoom_in"])


def generate_ken_burns(
    image_path: Path,
    output_path: Path,
    duration: float,
    scene_type: str,
    motion: str = None,
):
    spec = SPECS.get(scene_type, SPECS["ken_burns"])
    w = spec["width"]
    h = spec["height"]

    if motion is None:
        motion = random.choice(MOTION_STYLES)

    print(f"Motion style : {motion}")
    print(f"Output spec  : {spec['description']} ({w}x{h})")

    zoompan = build_zoompan_filter(motion, duration, w, h)

    # For portrait (9:16) reels, crop/pad the image to fill the frame
    if scene_type in ("youtube_short", "instagram_reel"):
        scale_filter = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
        vf = f"{scale_filter},{zoompan},fps={spec['fps']}"
    else:
        scale_filter = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
        vf = f"{scale_filter},{zoompan},fps={spec['fps']}"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    print("Running ffmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")


def main():
    data, scene = get_next_actionable_scene()

    if scene is None:
        print("\n✅ All scenes completed.")
        return

    scene_number = scene["scene_number"]
    scene_type = scene.get("type", "ken_burns")

    # Only handle ken_burns / reel types — skip ai_video scenes
    if scene_type not in SPECS:
        print(f"\nScene {scene_number} type is '{scene_type}' — skipping Ken Burns.")
        print("This scene will be handled by ai_video_generator.")
        return

    duration = float(scene.get("duration", 8))
    motion = scene.get("motion_style", None)
    generated_image = scene.get("generated_image", "")

    if not generated_image:
        raise ValueError(f"Scene {scene_number} has no generated_image path.")

    image_file = Path(generated_image)
    if not image_file.exists():
        raise FileNotFoundError(f"Image not found: {image_file}")

    # Name output file clearly by type
    if scene_type == "youtube_short":
        video_file = VIDEO_DIR / f"Scene_{scene_number:03d}_YT_Short.mp4"
    elif scene_type == "instagram_reel":
        video_file = VIDEO_DIR / f"Scene_{scene_number:03d}_IG_Reel.mp4"
    else:
        video_file = VIDEO_DIR / f"Scene_{scene_number:03d}.mp4"

    print("\n=========================================")
    print("SHARP TALK STUDIO")
    print("KEN BURNS GENERATOR (Free - ffmpeg)")
    print("=========================================\n")

    print(f"Scene   : {scene_number}")
    print(f"Type    : {scene_type}")
    print(f"Image   : {image_file}")
    print(f"Duration: {duration}s")
    print(f"Output  : {video_file}")

    generate_ken_burns(
        image_path=image_file,
        output_path=video_file,
        duration=duration,
        scene_type=scene_type,
        motion=motion,
    )

    update_scene_asset(scene_number, "generated_video", str(video_file))
    update_scene_asset(scene_number, "status", "video_generated")

    print("\n=========================================")
    print("KEN BURNS VIDEO CREATED ✅")
    print(video_file)
    print("MASTER JSON UPDATED ✅")
    print("=========================================")


if __name__ == "__main__":
    main()