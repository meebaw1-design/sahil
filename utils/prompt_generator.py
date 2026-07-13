# =====================================================
# Sharp Talk Sport Studio
# Google Flow Prompt Generator
# Phase 3 - Step 2
# =====================================================

import os


def create_prompt_package(project_name, video_title, duration="40 seconds"):

    project_path = os.path.join("projects", project_name)
    prompt_folder = os.path.join(project_path, "10_Google_Flow_Prompts")

    os.makedirs(prompt_folder, exist_ok=True)

    master_prompt = f"""# Google Flow Prompt Package

Project:
{project_name}

Video Title:
{video_title}

Duration:
{duration}

Style:
Cinematic football analysis video, realistic stadium atmosphere, broadcast sports visuals, dramatic lighting, high energy editing.

Goal:
Create short cinematic football scenes that can be used for a YouTube football analysis video.
"""

    scene_1 = f"""# Scene 01 Prompt

Create a cinematic opening shot for a football analysis video titled "{video_title}".

Visual:
A packed football stadium at night, dramatic floodlights, fans waving flags, players walking onto the pitch, high-energy atmosphere.

Camera:
Wide establishing shot, slow push-in, cinematic movement.

Mood:
Epic, intense, professional sports broadcast.

Duration:
8-10 seconds.
"""

    scene_2 = f"""# Scene 02 Prompt

Create a tactical football analysis scene for "{video_title}".

Visual:
Animated tactical board, football pitch lines, player movement arrows, passing lanes, formations appearing on screen.

Camera:
Clean top-down tactical view with smooth zoom and transitions.

Mood:
Smart, analytical, professional.

Duration:
8-10 seconds.
"""

    scene_3 = f"""# Scene 03 Prompt

Create a dramatic football match moment for "{video_title}".

Visual:
Fast counterattack, players sprinting, crowd reacting, ball moving quickly through midfield, intense stadium lights.

Camera:
Dynamic tracking shot, sports broadcast style, motion blur, realistic action.

Mood:
Fast, exciting, unpredictable.

Duration:
8-10 seconds.
"""

    scene_4 = f"""# Scene 04 Prompt

Create a final prediction scene for "{video_title}".

Visual:
Football trophy under stadium lights, scoreboard-style graphics, emotional crowd, cinematic slow-motion football atmosphere.

Camera:
Slow zoom toward trophy, dramatic reveal.

Mood:
Epic finale, suspenseful, premium sports documentary.

Duration:
8-10 seconds.
"""

    negative_prompt = """# Negative Prompt

Avoid:
low quality, blurry visuals, distorted players, extra limbs, broken faces, unreadable text, fake logos, copyrighted broadcast overlays, unrealistic football physics, messy crowd, bad anatomy, cartoon style unless requested.
"""

    audio_prompt = """# Audio Prompt

Music:
Epic cinematic sports music, rising tension, powerful drums, stadium atmosphere.

Sound Effects:
Crowd roar, whistle, camera whoosh, football kick, stadium ambience, cinematic boom.
"""

    files = {
        "Master_Prompt.md": master_prompt,
        "Scene_01_Flow_Prompt.md": scene_1,
        "Scene_02_Flow_Prompt.md": scene_2,
        "Scene_03_Flow_Prompt.md": scene_3,
        "Scene_04_Flow_Prompt.md": scene_4,
        "Negative_Prompt.md": negative_prompt,
        "Audio_Prompt.md": audio_prompt
    }

    for filename, content in files.items():

        path = os.path.join(prompt_folder, filename)

        with open(path, "w", encoding="utf8") as file:
            file.write(content)

    return prompt_folder


if __name__ == "__main__":

    folder = create_prompt_package(
        "Premier League Final",
        "Premier League Final Tactical Prediction",
        "40 seconds"
    )

    print("Prompt package created:")
    print(folder)