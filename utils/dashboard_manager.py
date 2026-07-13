# =====================================================
# Sharp Talk Sport Studio
# Dashboard Manager
# STEP 4C
# =====================================================

import os

from utils.progress_tracker import get_project_progress


def get_dashboard_data():

    projects_folder = "projects"

    data = []

    if not os.path.exists(projects_folder):
        return data

    for project in sorted(os.listdir(projects_folder)):

        path = os.path.join(
            projects_folder,
            project
        )

        if not os.path.isdir(path):
            continue

        progress = get_project_progress(project)

        data.append({

            "name": project,

            "completed": progress["completed"],

            "total": progress["total"],

            "percent": progress["percent"]

        })

    data.sort(
        key=lambda x: x["percent"],
        reverse=True
    )

    return data


# =====================================================
# Manual Test
# =====================================================

if __name__ == "__main__":

    projects = get_dashboard_data()

    for project in projects:

        print(project)