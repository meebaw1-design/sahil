import random
import urllib.parse
from pathlib import Path

import requests

from utils.production_state_manager import (
    PROJECT_NAME,
    get_next_pending_scene,
    update_scene_asset,
)

# ==========================================================
# SHARP TALK STUDIO
# AI IMAGE GENERATOR -- Pollinations.ai (free, no API key)
#
# Wide angle prompts generate excellent results.
# No setup needed - works immediately.
# ==========================================================

BASE_DIR  = Path("projects") / PROJECT_NAME
IMAGE_DIR = BASE_DIR / "02_AI_Images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"
MAX_RETRIES = 3


def generate_image(prompt: str, seed: int) -> bytes:
    encoded = urllib.parse.quote(prompt)
    url = POLLINATIONS_URL.format(prompt=encoded)
    for attempt in range(1, MAX_RETRIES + 1):
        # NOTE: seed is now randomized per attempt (was previously fixed to
        # scene_number, which meant retries/regenerations with a changed
        # prompt could still land on a near-identical composition because
        # Flux is seed-deterministic). Each attempt now gets a fresh seed
        # so a bad first result doesn't get reproduced on retry.
        attempt_seed = random.randint(1, 2_147_483_647)
        params = {
            "width": 1920,
            "height": 1080,
            "nologo": "true",
            "seed": attempt_seed,
            "model": "flux",
        }
        try:
            print(f"Requesting image... (attempt {attempt}/{MAX_RETRIES}, seed={attempt_seed})")
            resp = requests.get(url, params=params, timeout=120)
            resp.raise_for_status()
            if "image" not in resp.headers.get("content-type", ""):
                raise RuntimeError("Response is not an image")
            return resp.content
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt == MAX_RETRIES:
                raise


def main():
    data, scene = get_next_pending_scene()

    if scene is None:
        print("\n✅ All scenes completed. No image needed.")
        return

    scene_number = scene["scene_number"]
    image_prompt = scene["image_prompt"]
    image_file   = IMAGE_DIR / f"Scene_{scene_number:03d}.png"

    print("\n=========================================")
    print("SHARP TALK STUDIO")
    print("AI IMAGE GENERATOR (Pollinations.ai - Free)")
    print(f"Project: {PROJECT_NAME}")
    print("=========================================\n")
    print(f"Scene  : {scene_number}")
    print(f"Prompt : {image_prompt}")
    print(f"Output : {image_file}")

    image_bytes = generate_image(image_prompt, scene_number)
    image_file.write_bytes(image_bytes)

    update_scene_asset(scene_number, "generated_image", str(image_file))
    update_scene_asset(scene_number, "status", "image_generated")

    print("\n=========================================")
    print("IMAGE CREATED SUCCESSFULLY ✅")
    print(image_file)
    print("MASTER JSON UPDATED ✅")
    print("=========================================")


if __name__ == "__main__":
    main()