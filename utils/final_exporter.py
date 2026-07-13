import random
from pathlib import Path

from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, afx

from utils.production_state_manager import (
    PROJECT_NAME,
    get_next_actionable_scene,
    update_scene_asset,
    mark_scene_completed,
)

# ==========================================================
# SHARP TALK STUDIO
# FINAL SCENE EXPORTER -- combines video + voice + music
# ==========================================================

BASE_DIR   = Path("projects") / PROJECT_NAME
EXPORT_DIR = BASE_DIR / "06_Final_Export"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

MUSIC_DIR     = Path("Music") / PROJECT_NAME / "Background Music"
MUSIC_VOLUME  = 0.12
VOICE_VOLUME  = 1.0


def pick_music_track():
    if not MUSIC_DIR.exists():
        return None
    tracks = [p for p in MUSIC_DIR.glob("*")
              if p.suffix.lower() in (".mp3", ".wav", ".m4a")]
    return random.choice(tracks) if tracks else None


def build_audio(video_duration, voice_clip):
    music_path = pick_music_track()
    if music_path is None:
        print("ℹ️  No background music found — exporting voice only.")
        print(f"    Drop .mp3 files into: {MUSIC_DIR}")
        return voice_clip

    print(f"🎵 Music: {music_path.name}")
    music = AudioFileClip(str(music_path))

    if music.duration < video_duration:
        music = music.with_effects([afx.AudioLoop(duration=video_duration)])
    else:
        music = music.subclipped(0, video_duration)

    music = music.with_effects([afx.MultiplyVolume(MUSIC_VOLUME)])
    voice = voice_clip.with_effects([afx.MultiplyVolume(VOICE_VOLUME)])
    return CompositeAudioClip([music, voice])


def main():
    data, scene = get_next_actionable_scene()

    if scene is None:
        print("\n✅ All scenes completed.")
        return

    scene_number = scene["scene_number"]
    status       = scene.get("status", "pending")

    if status != "voice_generated":
        print(f"\nScene {scene_number} status is '{status}' — not ready for export.")
        return

    video_file  = Path(scene["generated_video"])
    voice_file  = Path(scene["generated_voice"])
    output_file = EXPORT_DIR / f"Scene_{scene_number:03d}_Final.mp4"

    print("\n=========================================")
    print("SHARP TALK STUDIO")
    print("FINAL SCENE EXPORTER")
    print(f"Project: {PROJECT_NAME}")
    print("=========================================\n")
    print(f"Scene  : {scene_number}")
    print(f"Video  : {video_file}")
    print(f"Voice  : {voice_file}")
    print(f"Output : {output_file}")

    if not video_file.exists():
        raise FileNotFoundError(f"Video not found: {video_file}")
    if not voice_file.exists():
        raise FileNotFoundError(f"Voice not found: {voice_file}")

    video = VideoFileClip(str(video_file))
    voice = AudioFileClip(str(voice_file))

    mixed_audio = build_audio(video.duration, voice)
    final       = video.with_audio(mixed_audio)

    print("\nExporting scene...")
    final.write_videofile(
        str(output_file),
        fps=30,
        codec="libx264",
        audio_codec="aac",
    )

    video.close()
    voice.close()
    final.close()

    update_scene_asset(scene_number, "final_scene_video", str(output_file))
    mark_scene_completed(scene_number)

    print("\n=========================================")
    print("FINAL SCENE CREATED ✅")
    print(output_file)
    print("MASTER JSON UPDATED ✅")
    print("SCENE MARKED COMPLETED ✅")
    print("=========================================")


if __name__ == "__main__":
    main()