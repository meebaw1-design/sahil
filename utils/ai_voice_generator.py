import asyncio
import random
from pathlib import Path

import edge_tts

from utils.production_state_manager import (
    PROJECT_NAME,
    get_next_actionable_scene,
    update_scene_asset,
)

# ==========================================================
# SHARP TALK STUDIO
# AI VOICE GENERATOR -- edge_tts (free, no API key)
# ==========================================================

BASE_DIR  = Path("projects") / PROJECT_NAME
VOICE_DIR = BASE_DIR / "04_AI_Voice"
VOICE_DIR.mkdir(parents=True, exist_ok=True)

# Rotate between two male voices for variety
VOICES = [
    "en-US-GuyNeural",
    "en-US-ChristopherNeural",
]


async def generate_voice():
    data, scene = get_next_actionable_scene()

    if scene is None:
        print("\n✅ All scenes completed. No voice needed.")
        return

    scene_number = scene["scene_number"]
    status       = scene.get("status", "pending")

    # Only handle scenes that have video but no voice yet
    if status != "video_generated":
        print(f"\nScene {scene_number} status is '{status}' — not ready for voice.")
        return

    voice_text  = scene.get("voice_over", "")
    voice_name  = random.choice(VOICES)
    voice_file  = VOICE_DIR / f"Scene_{scene_number:03d}.mp3"

    print("\n=========================================")
    print("SHARP TALK STUDIO")
    print("AI VOICE GENERATOR (edge_tts - Free)")
    print(f"Project: {PROJECT_NAME}")
    print("=========================================\n")
    print(f"Scene  : {scene_number}")
    print(f"Voice  : {voice_name}")
    print(f"Text   : {voice_text[:80]}...")
    print(f"Output : {voice_file}")

    communicate = edge_tts.Communicate(
        text=voice_text,
        voice=voice_name,
        rate="+5%",
        volume="+0%",
    )

    await communicate.save(str(voice_file))

    update_scene_asset(scene_number, "generated_voice", str(voice_file))
    update_scene_asset(scene_number, "status", "voice_generated")

    print("\n=========================================")
    print("VOICE CREATED SUCCESSFULLY ✅")
    print(voice_file)
    print("MASTER JSON UPDATED ✅")
    print("=========================================")


if __name__ == "__main__":
    asyncio.run(generate_voice())