import json
import os
import time
from pathlib import Path

import requests
from moviepy import VideoFileClip, concatenate_videoclips

from utils.production_state_manager import (
    PROJECT_NAME,
    get_next_actionable_scene,
    update_scene_asset,
)

# ==========================================================
# SHARP TALK STUDIO
# AI VIDEO GENERATOR -- RunPod Pod + ComfyUI + Wan 2.2
# Two-stage pipeline (HIGH + LOW noise) matching pod workflow
# ==========================================================

# PROJECT_NAME comes from production_state_manager
BASE_DIR  = Path("projects") / PROJECT_NAME
VIDEO_DIR = BASE_DIR / "03_AI_Videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_POD_ID  = os.getenv("RUNPOD_POD_ID", "85ts43xl3ysstm")

if not RUNPOD_API_KEY:
    raise ValueError(
        "\n❌ RUNPOD_API_KEY not found.\n"
        "PowerShell:\n"
        '$env:RUNPOD_API_KEY="your_key_here"\n'
        '$env:RUNPOD_POD_ID="85ts43xl3ysstm"\n'
    )

RUNPOD_HEADERS = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type":  "application/json",
}

COMFY_BASE = f"https://{RUNPOD_POD_ID}-8188.proxy.runpod.net"

WAN_HIGH_MODEL = "I2V/Wan2_2-I2V-A14B-HIGH_fp8_e4m3fn_scaled_KJ.safetensors"
WAN_LOW_MODEL  = "I2V/Wan2_2-I2V-A14B-LOW_fp8_e4m3fn_scaled_KJ.safetensors"
WAN_VAE        = "Wan2_1_VAE_bf16.safetensors"
WAN_CLIP       = "umt5-xxl-enc-bf16.safetensors"

WAN_NEGATIVE   = "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走"

WAN_CLIP_SECONDS     = 5
POD_START_TIMEOUT    = 300
COMFY_READY_TIMEOUT  = 300
GENERATION_TIMEOUT   = 900
POLL_INTERVAL        = 10


# ----------------------------------------------------------
# RunPod pod management
# ----------------------------------------------------------

def get_pod_status():
    url  = f"https://rest.runpod.io/v1/pods/{RUNPOD_POD_ID}"
    resp = requests.get(url, headers=RUNPOD_HEADERS, timeout=30)
    resp.raise_for_status()
    data    = resp.json()
    runtime = data.get("runtime")
    if runtime:
        return "RUNNING"
    return data.get("desiredStatus", data.get("status", "EXITED"))


def start_pod():
    print("Starting RunPod pod...")
    url  = f"https://rest.runpod.io/v1/pods/{RUNPOD_POD_ID}/start"
    resp = requests.post(url, headers=RUNPOD_HEADERS, timeout=30)
    resp.raise_for_status()
    print("Pod start requested.")


def stop_pod():
    print("\nStopping RunPod pod...")
    url  = f"https://rest.runpod.io/v1/pods/{RUNPOD_POD_ID}/stop"
    resp = requests.post(url, headers=RUNPOD_HEADERS, timeout=30)
    resp.raise_for_status()
    print("Pod stopped ✅")


def wait_for_pod_running():
    print("Waiting for pod to start...")
    waited = 0
    while waited < POD_START_TIMEOUT:
        status = get_pod_status()
        print(f"  Pod status: {status} ({waited}s)")
        if status == "RUNNING":
            print("Pod is running ✅")
            return
        time.sleep(15)
        waited += 15
    raise TimeoutError("Pod did not start within timeout.")


# ----------------------------------------------------------
# ComfyUI connection
# ----------------------------------------------------------

def wait_for_comfyui():
    print("Waiting for ComfyUI to come online...")
    waited = 0
    while waited < COMFY_READY_TIMEOUT:
        try:
            resp = requests.get(f"{COMFY_BASE}/system_stats", timeout=10)
            if resp.status_code == 200:
                print("ComfyUI is ready ✅")
                return
        except Exception:
            pass
        print(f"  ComfyUI not ready yet... ({waited}s)")
        time.sleep(15)
        waited += 15
    raise TimeoutError("ComfyUI did not come online within timeout.")


def upload_image(image_path: Path) -> str:
    print(f"Uploading image: {image_path.name}")
    with open(image_path, "rb") as f:
        files = {"image": (image_path.name, f, "image/png")}
        resp  = requests.post(f"{COMFY_BASE}/upload/image",
                              files=files, timeout=60)
    resp.raise_for_status()
    name = resp.json().get("name", image_path.name)
    print(f"Uploaded as: {name} ✅")
    return name


def build_workflow(image_filename: str, prompt: str, scene_number: int) -> dict:
    """
    Builds the exact two-stage Wan 2.2 I2V workflow matching the pod's
    wanvideo_2_2_I2V_A14B_example_WIP workflow, with LoRA nodes bypassed.
    Node IDs match the original workflow for easy debugging.
    """
    output_prefix = f"STS_Scene_{scene_number:03d}"
    seed          = scene_number * 1000

    return {
        "prompt": {
            # T5 Text Encoder Loader
            "11": {
                "class_type": "LoadWanVideoT5TextEncoder",
                "inputs": {
                    "model_name":    WAN_CLIP,
                    "precision":     "bf16",
                    "load_device":   "offload_device",
                    "quantization":  "disabled",
                }
            },
            # Text Encode
            "16": {
                "class_type": "WanVideoTextEncode",
                "inputs": {
                    "positive_prompt": prompt,
                    "negative_prompt": WAN_NEGATIVE,
                    "force_offload":  True,
                    "use_disk_cache": False,
                    "device":         "gpu",
                    "t5":             ["11", 0],
                }
            },
            # Torch Compile Settings (fullgraph=false = no compile, safer)
            "35": {
                "class_type": "WanVideoTorchCompileSettings",
                "inputs": {
                    "backend":                     "inductor",
                    "fullgraph":                   False,
                    "mode":                        "default",
                    "dynamic":                     False,
                    "dynamo_cache_size_limit":     64,
                    "compile_transformer_blocks_only": True,
                    "dynamo_recompile_limit":      128,
                    "force_parameter_static_shapes": False,
                }
            },
            # VAE Loader
            "38": {
                "class_type": "WanVideoVAELoader",
                "inputs": {
                    "model_name":  WAN_VAE,
                    "precision":   "bf16",
                    "load_device": "offload_device",
                }
            },
            # Block Swap Args
            "39": {
                "class_type": "WanVideoBlockSwap",
                "inputs": {
                    "blocks_to_swap":             20,
                    "offload_txt_in":             False,
                    "offload_img_in":             False,
                    "offload_txt_emb":            False,
                    "offload_img_emb":            False,
                    "offload_single_blocks":      False,
                    "use_non_blocking_offload":   1,
                }
            },
            # HIGH Noise Model Loader
            "22": {
                "class_type": "WanVideoModelLoader",
                "inputs": {
                    "model":           WAN_HIGH_MODEL,
                    "base_precision":  "fp16_fast",
                    "quantization":    "fp8_e4m3fn_scaled",
                    "load_device":     "offload_device",
                    "attention_mode":  "sdpa",
                    "compile_args":    ["35", 0],
                }
            },
            # LOW Noise Model Loader
            "71": {
                "class_type": "WanVideoModelLoader",
                "inputs": {
                    "model":           WAN_LOW_MODEL,
                    "base_precision":  "fp16_fast",
                    "quantization":    "fp8_e4m3fn_scaled",
                    "load_device":     "offload_device",
                    "attention_mode":  "sdpa",
                    "compile_args":    ["35", 0],
                }
            },
            # Set Block Swap HIGH (node 92 — bypassing LoRA node 80)
            "92": {
                "class_type": "WanVideoSetBlockSwap",
                "inputs": {
                    "model":            ["22", 0],
                    "block_swap_args":  ["39", 0],
                }
            },
            # Set Block Swap LOW (node 93 — bypassing LoRA node 79)
            "93": {
                "class_type": "WanVideoSetBlockSwap",
                "inputs": {
                    "model":            ["71", 0],
                    "block_swap_args":  ["39", 0],
                }
            },
            # Load Image
            "67": {
                "class_type": "LoadImage",
                "inputs": {
                    "image":  image_filename,
                    "upload": "image",
                }
            },
            # Resize Image to 720x720
            "68": {
                "class_type": "ImageResizeKJv2",
                "inputs": {
                    "image":           ["67", 0],
                    "width":           720,
                    "height":          720,
                    "upscale_method":  "lanczos",
                    "keep_proportion": "crop",
                    "pad_color":       "0, 0, 0",
                    "crop_position":   "center",
                    "divisible_by":    32,
                    "device":          "cpu",
                }
            },
            # Image to Video Encode
            "89": {
                "class_type": "WanVideoImageToVideoEncode",
                "inputs": {
                    "vae":                     ["38", 0],
                    "start_image":             ["68", 0],
                    "width":                   ["68", 1],
                    "height":                  ["68", 2],
                    "num_frames":              81,
                    "noise_aug_strength":      0,
                    "clip_embed_strength":     1,
                    "start_latent_strength":   1,
                    "end_latent_strength":     1,
                    "image_interp_mode":       1,
                    "latent_interpolation_mode": True,
                    "force_offload":           True,
                    "mask_frames":             False,
                    "use_hires_fix":           False,
                }
            },
            # Steps Constant (= 6)
            "94": {
                "class_type": "INTConstant",
                "inputs": {"value": 6}
            },
            # Split Step Constant (= 3)
            "91": {
                "class_type": "INTConstant",
                "inputs": {"value": 3}
            },
            # CFG Schedule
            "95": {
                "class_type": "CreateCFGScheduleFloatList",
                "inputs": {
                    "cfg_scale_start":   2,
                    "cfg_scale_end":     2,
                    "start_percent":     0.0,
                    "end_percent":       1.0,
                    "interpolation":     "linear",
                    "min_cfg":           0,
                    "distilled_cfg_scale": 0.01,
                    "steps":             ["94", 0],
                }
            },
            # HIGH Noise Sampler (steps 0 → split_step)
            "27": {
                "class_type": "WanVideoSampler",
                "inputs": {
                    "model":                  ["92", 0],
                    "image_embeds":           ["89", 0],
                    "text_embeds":            ["16", 0],
                    "steps":                  ["94", 0],
                    "cfg":                    ["95", 0],
                    "end_step":               ["91", 0],
                    "seed":                   seed,
                    "force_offload":          True,
                    "scheduler":              "dpm++_sde",
                    "shift":                  8,
                    "riflex_freq_index":      0,
                    "denoise_strength":       1,
                    "add_noise_to_sample":    False,
                    "noise_type":             "comfy",
                    "max_frames_per_forward": 10,
                    "noise_std":              -1,
                    "rope_function":          "comfy",
                }
            },
            # LOW Noise Sampler (steps split_step → end)
            "90": {
                "class_type": "WanVideoSampler",
                "inputs": {
                    "model":                  ["93", 0],
                    "image_embeds":           ["89", 0],
                    "text_embeds":            ["16", 0],
                    "samples":                ["27", 0],
                    "steps":                  ["94", 0],
                    "cfg":                    ["95", 0],
                    "start_step":             ["91", 0],
                    "seed":                   seed + 1,
                    "force_offload":          True,
                    "scheduler":              "dpm++_sde",
                    "shift":                  8,
                    "riflex_freq_index":      0,
                    "denoise_strength":       1,
                    "add_noise_to_sample":    False,
                    "noise_type":             "comfy",
                    "max_frames_per_forward": 10,
                    "noise_std":              -1,
                    "rope_function":          "comfy",
                }
            },
            # VAE Decode
            "28": {
                "class_type": "WanVideoDecode",
                "inputs": {
                    "vae":                          ["38", 0],
                    "samples":                      ["90", 0],
                    "enable_vae_tiling":            True,
                    "tile_x":                       272,
                    "tile_y":                       272,
                    "tile_stride_x":                144,
                    "tile_stride_y":                144,
                    "auto_tile_size":               True,
                }
            },
            # Get Image Size & Count
            "69": {
                "class_type": "GetImageSizeAndCount",
                "inputs": {
                    "image": ["28", 0],
                }
            },
            # Video Combine — save_output TRUE so file is saved to disk
            "60": {
                "class_type": "VHS_VideoCombine",
                "inputs": {
                    "images":          ["69", 0],
                    "frame_rate":      16,
                    "loop_count":      0,
                    "filename_prefix": output_prefix,
                    "format":          "video/h264-mp4",
                    "pix_fmt":         "yuv420p",
                    "crf":             19,
                    "save_metadata":   True,
                    "trim_to_audio":   False,
                    "pingpong":        False,
                    "save_output":     True,
                }
            },
        }
    }


def submit_workflow(workflow: dict) -> str:
    print("Submitting Wan 2.2 workflow to ComfyUI...")
    resp = requests.post(f"{COMFY_BASE}/prompt", json=workflow, timeout=60)

    if resp.status_code != 200:
        # Print the actual error body so we can debug
        print(f"❌ ComfyUI returned {resp.status_code}")
        try:
            print("Error detail:", json.dumps(resp.json(), indent=2))
        except Exception:
            print("Error body:", resp.text[:1000])
        resp.raise_for_status()

    prompt_id = resp.json()["prompt_id"]
    print(f"Submitted — prompt_id: {prompt_id} ✅")
    return prompt_id


def wait_for_generation(prompt_id: str) -> dict:
    print("Generating video with Wan 2.2...")
    waited = 0
    while waited < GENERATION_TIMEOUT:
        resp    = requests.get(f"{COMFY_BASE}/history/{prompt_id}", timeout=30)
        resp.raise_for_status()
        history = resp.json()

        if prompt_id in history:
            job    = history[prompt_id]
            status = job.get("status", {})
            if status.get("completed"):
                print(f"Generation complete ✅ ({waited}s elapsed)")
                return job.get("outputs", {})
            if status.get("status_str") == "error":
                msgs = status.get("messages", [])
                raise RuntimeError(f"ComfyUI generation error: {msgs}")

        print(f"  Generating... ({waited}s)")
        time.sleep(POLL_INTERVAL)
        waited += POLL_INTERVAL

    raise TimeoutError(f"Generation timed out after {GENERATION_TIMEOUT}s")


def download_clip(outputs: dict, out_path: Path):
    print("Downloading generated video...")
    for node_id, node_output in outputs.items():
        for item in node_output.get("gifs", []):
            filename  = item.get("filename", "")
            subfolder = item.get("subfolder", "")
            if filename.endswith(".mp4"):
                url  = (f"{COMFY_BASE}/view?filename={filename}"
                        f"&subfolder={subfolder}&type=output")
                resp = requests.get(url, timeout=120, stream=True)
                resp.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded: {out_path.name} ✅")
                return
    raise RuntimeError(
        f"No .mp4 found in outputs.\nOutputs: {json.dumps(outputs, indent=2)}"
    )


def generate_scene_video(image_path: Path, prompt: str,
                          duration: int, scene_number: int,
                          image_filename: str) -> Path:
    clips_needed = max(1, round(duration / WAN_CLIP_SECONDS))
    tmp_dir      = VIDEO_DIR / f"_tmp_scene_{scene_number:03d}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    clip_paths   = []

    print(f"\nScene {scene_number}: generating {clips_needed} clips "
          f"({WAN_CLIP_SECONDS}s each) → {duration}s total")

    for i in range(clips_needed):
        clip_path  = tmp_dir / f"clip_{i+1:02d}.mp4"
        # Give each clip a unique scene_number offset for different seeds
        clip_scene = scene_number * 100 + i
        print(f"\n--- Clip {i+1}/{clips_needed} ---")
        workflow   = build_workflow(image_filename, prompt, clip_scene)
        prompt_id  = submit_workflow(workflow)
        outputs    = wait_for_generation(prompt_id)
        download_clip(outputs, clip_path)
        clip_paths.append(clip_path)

    final_path = VIDEO_DIR / f"Scene_{scene_number:03d}.mp4"

    if len(clip_paths) == 1:
        clip_paths[0].replace(final_path)
    else:
        print(f"\nStitching {len(clip_paths)} clips → {final_path.name}")
        clips = [VideoFileClip(str(p)) for p in clip_paths]
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(str(final_path), fps=24,
                              codec="libx264", audio_codec="aac")
        final.close()
        for c in clips:
            c.close()

    for f in tmp_dir.glob("*"):
        f.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except Exception:
        pass

    return final_path


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():
    data, scene = get_next_actionable_scene()

    if scene is None:
        print("\n✅ All scenes completed.")
        return

    scene_number = scene["scene_number"]
    scene_type   = scene.get("type", "ai_video")

    if scene_type != "ai_video":
        print(f"\nScene {scene_number} is '{scene_type}' — not ai_video.")
        return

    video_prompt    = scene["video_prompt"]
    duration        = int(scene.get("duration", 20))
    generated_image = scene.get("generated_image", "")

    if not generated_image:
        raise ValueError(f"Scene {scene_number} has no generated_image.")

    image_file = Path(generated_image)
    if not image_file.exists():
        raise FileNotFoundError(image_file)

    print("\n=========================================")
    print("SHARP TALK STUDIO")
    print("AI VIDEO GENERATOR (RunPod + Wan 2.2)")
    print(f"Project: {PROJECT_NAME}")
    print("=========================================\n")
    print(f"Scene    : {scene_number}")
    print(f"Duration : {duration}s")
    print(f"Image    : {image_file}")
    print(f"Prompt   : {video_prompt}")
    print(f"Pod      : {RUNPOD_POD_ID}")

    pod_was_stopped = False

    try:
        status = get_pod_status()
        print(f"\nPod status: {status}")

        if status != "RUNNING":
            start_pod()
            wait_for_pod_running()
            pod_was_stopped = True
            print("Waiting 45s for ComfyUI to boot...")
            time.sleep(45)

        wait_for_comfyui()
        image_filename = upload_image(image_file)
        video_file     = generate_scene_video(
            image_file, video_prompt, duration,
            scene_number, image_filename
        )

    finally:
        if pod_was_stopped:
            try:
                stop_pod()
            except Exception as e:
                print(f"Warning: could not auto-stop pod: {e}")
                print("Please stop it manually at console.runpod.io !")

    update_scene_asset(scene_number, "generated_video", str(video_file))
    update_scene_asset(scene_number, "status", "video_generated")

    print("\n=========================================")
    print("VIDEO CREATED SUCCESSFULLY ✅")
    print(video_file)
    print("MASTER JSON UPDATED ✅")
    print("=========================================")


if __name__ == "__main__":
    main()