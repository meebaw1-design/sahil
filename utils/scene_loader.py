# =====================================================
# Sharp Talk Sport Studio
# Scene Loader
# =====================================================

import os


class SceneLoader:

    def __init__(self, project_folder):

        self.project_folder = project_folder

        self.script_folder = os.path.join(
            project_folder,
            "01_Scripts"
        )

    # ---------------------------------------------

    def scene_path(self, scene_number):

        filename = f"Scene_{scene_number:02}.md"

        return os.path.join(
            self.script_folder,
            filename
        )

    # ---------------------------------------------

    def load_scene(self, scene_number):

        path = self.scene_path(scene_number)

        if not os.path.exists(path):

            return ""

        with open(
            path,
            "r",
            encoding="utf8"
        ) as file:

            return file.read()

    # ---------------------------------------------

    def save_scene(self, scene_number, text):

        path = self.scene_path(scene_number)

        with open(
            path,
            "w",
            encoding="utf8"
        ) as file:

            file.write(text)
            # =====================================================
# Manual Test
# =====================================================

if __name__ == "__main__":

    loader = SceneLoader(
        "projects/Premier League Final"
    )

    print(loader.load_scene(1))