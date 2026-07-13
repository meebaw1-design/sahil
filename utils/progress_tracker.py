# =====================================================
# Sharp Talk Sport Studio
# Progress Tracker
# STEP 4B
# =====================================================

import os


def get_project_progress(project_name):

    project_path = os.path.join("projects", project_name)
    scripts_path = os.path.join(project_path, "01_Scripts")

    if not os.path.exists(scripts_path):
        return {
            "total": 0,
            "completed": 0,
            "percent": 0
        }

    scene_files = [
        file for file in os.listdir(scripts_path)
        if file.startswith("Scene_") and file.endswith(".md")
    ]

    total = len(scene_files)
    completed = 0

    for file in scene_files:

        path = os.path.join(scripts_path, file)

        with open(path, "r", encoding="utf8") as f:
            content = f.read().strip()

        # Default files only contain a heading like "# Scene 01"
        # If the file has more than 30 characters, we count it as started/completed.
        if len(content) > 30:
            completed += 1

    percent = 0

    if total > 0:
        percent = int((completed / total) * 100)

    return {
        "total": total,
        "completed": completed,
        "percent": percent
    }


# =====================================================
# Manual Test
# =====================================================

if __name__ == "__main__":

    result = get_project_progress("Premier League Final")

    print(result)