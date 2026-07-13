# =====================================================
# Sharp Talk Sport Studio
# Production Queue Manager
# Phase 3 Step 3D-2
# =====================================================

import json
import os

from utils.production_json_reader import load_production_json


class ProductionQueue:

    def __init__(self, json_path):

        self.json_path = json_path
        self.data = None
        self.scenes = []

    def load(self):

        success, message, data = load_production_json(self.json_path)

        if not success:
            return False, message

        self.data = data
        self.scenes = data["scenes"]

        return True, "Production queue loaded."

    def get_project_info(self):

        if self.data is None:
            return {}

        return self.data.get("project", {})

    def get_all_scenes(self):

        return self.scenes

    def get_pending_scenes(self):

        return [
            scene for scene in self.scenes
            if scene.get("status", "pending") == "pending"
        ]

    def get_next_pending_scene(self):

        pending = self.get_pending_scenes()

        if len(pending) == 0:
            return None

        return pending[0]

    def update_scene(self, scene_number, updates):

        for scene in self.scenes:

            if scene["scene_number"] == scene_number:

                for key, value in updates.items():
                    scene[key] = value

                return True

        return False

    def save(self):

        if self.data is None:
            return False, "No production data loaded."

        with open(self.json_path, "w", encoding="utf8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

        return True, "Production JSON saved."

    def mark_scene_completed(self, scene_number):

        updated = self.update_scene(
            scene_number,
            {
                "status": "completed"
            }
        )

        if not updated:
            return False, "Scene not found."

        return self.save()

    def attach_generated_image(self, scene_number, image_path):

        updated = self.update_scene(
            scene_number,
            {
                "generated_image": image_path,
                "status": "image_generated"
            }
        )

        if not updated:
            return False, "Scene not found."

        return self.save()


if __name__ == "__main__":

    queue = ProductionQueue(
        "projects/Premier League Final/master_production.json"
    )

    success, message = queue.load()

    print(success)
    print(message)

    print("Project:")
    print(queue.get_project_info())

    print("Next Pending Scene:")
    print(queue.get_next_pending_scene())