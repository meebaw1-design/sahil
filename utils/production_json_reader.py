# =====================================================
# Sharp Talk Sport Studio
# Master JSON Reader
# Phase 3 Step 3D-1
# =====================================================

import json
import os


def load_production_json(json_path):

    if not os.path.exists(json_path):
        return False, "JSON file not found.", None

    try:
        with open(json_path, "r", encoding="utf8") as file:
            data = json.load(file)

        if "project" not in data:
            return False, "Missing project section.", None

        if "scenes" not in data:
            return False, "Missing scenes section.", None

        if not isinstance(data["scenes"], list):
            return False, "Scenes must be a list.", None

        for scene in data["scenes"]:

            required_fields = [
                "scene_number",
                "duration",
                "voice_over",
                "image_prompt",
                "video_prompt",
                "audio_prompt"
            ]

            for field in required_fields:
                if field not in scene:
                    return False, f"Scene missing field: {field}", None

            if scene["duration"] > 8:
                return False, f"Scene {scene['scene_number']} exceeds 8 seconds.", None

        return True, "Production JSON loaded successfully.", data

    except json.JSONDecodeError as error:
        return False, f"Invalid JSON format: {error}", None

    except Exception as error:
        return False, f"Error: {error}", None