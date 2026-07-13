# =====================================================
# Sharp Talk Sport Studio
# Gemini API Connection Test
# Phase 3 Step 3C (Advanced Diagnostics)
# =====================================================

import json
import urllib.request
import urllib.error

from utils.api_key_manager import get_api_key


MODEL = "gemini-3.1-flash-lite"


def test_gemini_connection():

    api_key = get_api_key().strip()

    if api_key == "":
        return False, "No API key saved."

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{MODEL}:generateContent?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Reply with exactly: connection successful"
                    }
                ]
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(request, timeout=30) as response:

            body = response.read().decode("utf-8")

            return (
                True,
                f"Connected successfully.\n\nModel: {MODEL}"
            )

    except urllib.error.HTTPError as error:

        try:

            error_body = error.read().decode("utf-8")

            error_json = json.loads(error_body)

            message = error_json.get("error", {}).get("message", "Unknown error")

            status = error_json.get("error", {}).get("status", "")

            return (
                False,
                f"""
HTTP {error.code}

Status:
{status}

Message:
{message}
""".strip()
            )

        except Exception:

            return False, f"HTTP Error {error.code}"

    except urllib.error.URLError as error:

        return False, f"Network Error:\n{error.reason}"

    except Exception as error:

        return False, str(error)