# =====================================================
# Sharp Talk Sport Studio
# STEP 3
# Project Creator
# =====================================================

import json
import os


DATABASE = "database/recent_projects.json"


def save_recent_project(project_name):

    if not os.path.exists(DATABASE):

        with open(DATABASE, "w") as f:

            json.dump([], f)

    with open(DATABASE, "r") as f:

        data = json.load(f)

    if project_name not in data:

        data.append(project_name)

    with open(DATABASE, "w") as f:

        json.dump(data, f, indent=4)


def create_project(base_folder, project_name):

    project_path = os.path.join(base_folder, project_name)

    os.makedirs(project_path, exist_ok=True)

    folders = [

        "01_Scripts",
        "02_AI_Images",
        "03_AI_Videos",
        "04_Voice",
        "05_Music",
        "06_SFX",
        "07_Thumbnails",
        "08_Exports",
        "09_Final_Video"

    ]

    for folder in folders:

        os.makedirs(

            os.path.join(project_path, folder),

            exist_ok=True

        )

    scripts = os.path.join(

        project_path,

        "01_Scripts"

    )

    for i in range(1,11):

        filename = f"Scene_{i:02}.md"

        with open(

            os.path.join(scripts, filename),

            "w",

            encoding="utf8"

        ) as f:

            f.write(f"# Scene {i:02}\n")

    with open(

        os.path.join(project_path,"Project_Brief.md"),

        "w",

        encoding="utf8"

    ) as f:

        f.write(f"# {project_name}")

    with open(

        os.path.join(project_path,"Production_Checklist.md"),

        "w",

        encoding="utf8"

    ) as f:

        f.write("# Production Checklist")

    save_recent_project(project_name)

    return project_path