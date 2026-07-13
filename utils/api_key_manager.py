# =====================================================
# Sharp Talk Sport Studio
# Gemini API Key Manager
# Phase 3 Step 3A
# =====================================================

import json
import os


SETTINGS_FILE = "database/api_settings.json"


def ensure_settings():

    if not os.path.exists("database"):
        os.makedirs("database")

    if not os.path.exists(SETTINGS_FILE):

        data = {
            "gemini_api_key": "",
            "api_status": "Not Configured"
        }

        with open(SETTINGS_FILE, "w") as file:
            json.dump(data, file, indent=4)


def load_settings():

    ensure_settings()

    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)


def save_api_key(api_key):

    ensure_settings()

    data = load_settings()

    data["gemini_api_key"] = api_key

    if api_key.strip() == "":
        data["api_status"] = "Not Configured"
    else:
        data["api_status"] = "Configured"

    with open(SETTINGS_FILE, "w") as file:
        json.dump(data, file, indent=4)


def get_api_key():

    data = load_settings()

    return data["gemini_api_key"]


def get_status():

    data = load_settings()

    return data["api_status"]


if __name__ == "__main__":

    print(load_settings())