import json
import os
import webbrowser

STATUS_FILE = "database/google_flow_status.json"
FLOW_URL = "https://labs.google/fx/tools/flow"


def ensure_status_file():
    if not os.path.exists("database"):
        os.makedirs("database")

    if not os.path.exists(STATUS_FILE):
        save_status(False)


def save_status(connected):
    data = {
        "connected": connected,
        "service": "Google Flow",
        "credits": "Unknown",
        "queue": "Idle"
    }

    with open(STATUS_FILE, "w") as file:
        json.dump(data, file, indent=4)


def load_status():
    ensure_status_file()

    with open(STATUS_FILE, "r") as file:
        return json.load(file)


def open_google_flow():
    webbrowser.open(FLOW_URL)


def verify_connection():
    save_status(True)


def disconnect_flow():
    save_status(False)