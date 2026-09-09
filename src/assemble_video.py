import os
import tarfile
import tempfile
import subprocess
import shutil
from vocab_lookup import lookup_word, CISLR_VIDEO_DIR, SIGN_DICT_DIR

FINGERSPELL_DIR = "data/fingerspelling/Indian"
WORDS_OUTPUT_DIR = "outputs/words"  # permanent, servable copies

os.makedirs(WORDS_OUTPUT_DIR, exist_ok=True)

def extract_sign_dict_video(shard_name, asset_id, out_dir):
    shard_path = os.path.join(SIGN_DICT_DIR, shard_name)
    target_name = f"{asset_id}.mp4"
    with tarfile.open(shard_path, "r") as tar:
        member = tar.getmember(target_name)
        tar.extract(member, path=out_dir)
    return os.path.join(out_dir, target_name)

def image_to_video_clip(image_path, out_path, duration=0.6):
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", image_path,
        "-t", str(duration), "-vf", "scale=640:480",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", out_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path

def get_letter_image_path(letter):
    """Return the raw jpg path for a fingerspelling letter (for UI display)."""
    letter_dir = os.path.join(FINGERSPELL_DIR, letter)
    if not os.path.isdir(letter_dir):
        return None
    images = [f for f in os.listdir(letter_dir) if f.endswith(".jpg")]
    return os.path.join(letter_dir, images[0]) if images else None

def resolve_gloss_to_clips(gloss_tokens, temp_dir, session_id):
    """
    Returns:
      clip_paths: ordered list of temp file paths (for final concatenation)
      word_breakdown: list of dicts describing each token for UI display
    """
    clip_paths = []
    word_breakdown = []

    for idx, token in enumerate(gloss_tokens):
        clean_token = token.replace("DESC-", "").replace("X-", "").strip().lower()
        if not clean_token:
            continue

        match = lookup_word(clean_token)
        entry = {"token": token, "match_type": match["match_type"], "source": match["source"]}

        if match["source"] == "cislr":
            path = os.path.join(CISLR_VIDEO_DIR, f"{match['uid']}.mp4")
            clip_paths.append(path)

            # Copy a permanent, servable version for the UI's per-word preview
            permanent_name = f"{session_id}_word{idx}.mp4"
            permanent_path = os.path.join(WORDS_OUTPUT_DIR, permanent_name)
            reencode_for_web(path, permanent_path)
            entry["video_url"] = f"/outputs/words/{permanent_name}"
            entry["is_fingerspell"] = False

        elif match["source"] == "sign_dictionary":
            path = extract_sign_dict_video(match["shard"], match["asset_id"], temp_dir)
            clip_paths.append(path)

            permanent_name = f"{session_id}_word{idx}.mp4"
            permanent_path = os.path.join(WORDS_OUTPUT_DIR, permanent_name)
            reencode_for_web(path, permanent_path)
            entry["video_url"] = f"/outputs/words/{permanent_name}"
            entry["is_fingerspell"] = False

        else:
            # Fingerspelling — collect per-letter image URLs, and still build video clips for concatenation
            letters_info = []
            for i, letter in enumerate(clean_token.upper()):
                if not letter.isalpha():
                    continue
                image_path = get_letter_image_path(letter)
                if not image_path:
                    continue

                clip_out = os.path.join(temp_dir, f"fs_{clean_token}_{i}_{letter}.mp4")
                image_to_video_clip(image_path, clip_out)
                clip_paths.append(clip_out)

                permanent_img_name = f"{session_id}_word{idx}_letter{i}.jpg"
                permanent_img_path = os.path.join(WORDS_OUTPUT_DIR, permanent_img_name)
                shutil.copy(image_path, permanent_img_path)
                letters_info.append({"letter": letter, "image_url": f"/outputs/words/{permanent_img_name}"})

            entry["is_fingerspell"] = True
            entry["letters"] = letters_info

        word_breakdown.append(entry)
        print(f"'{token}' -> {match['source']} ({match['match_type']})")

    return clip_paths, word_breakdown

def reencode_for_web(input_path, output_path):
    """Re-encode into a guaranteed browser-safe mp4 (fixes files ffmpeg tolerates but browsers reject)."""
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", input_path,
        "-vf", "scale=480:360,setsar=1",
        "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-an",
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path

def concatenate_videos(clip_paths, output_path, target_fps=25):
    if not clip_paths:
        print("No clips to assemble!")
        return None

    inputs = []
    filter_parts = []
    for i, path in enumerate(clip_paths):
        inputs.extend(["-i", path])
        filter_parts.append(f"[{i}:v]scale=640:480,setsar=1,fps={target_fps}[v{i}]")

    concat_refs = "".join(f"[v{i}]" for i in range(len(clip_paths)))
    filter_complex = ";".join(filter_parts) + f";{concat_refs}concat=n={len(clip_paths)}:v=1:a=0[outv]"

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path