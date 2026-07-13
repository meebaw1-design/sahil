# =====================================================
# Sharp Talk Sport Studio
# Project List Helper
# =====================================================

import os


def get_projects():

    folder = "projects"

    if not os.path.exists(folder):
        return []

    projects = []

    for item in os.listdir(folder):

        path = os.path.join(folder, item)

        if os.path.isdir(path):

            projects.append(item)

    projects.sort()

    return projects