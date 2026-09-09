import tempfile
import uuid
from speech_to_text import transcribe_audio
from gloss_translate import build_prompt, generate_ollama, clean_gloss
from assemble_video import resolve_gloss_to_clips, concatenate_videos

def do_transcribe(audio_path):
    import whisper
    from speech_to_text import load_whisper_model
    model = load_whisper_model()
    result = model.transcribe(audio_path)
    return {"text": result["text"].strip(), "language": result.get("language", "unknown")}

def text_to_gloss(text, model="llama3.1:8b"):
    prompt = build_prompt(text)
    gloss_output = generate_ollama(prompt, model=model)
    gloss_output = gloss_output.strip().rstrip(".").strip()
    return clean_gloss(gloss_output)

def do_translate(text, model="llama3.1:8b"):
    gloss = text_to_gloss(text, model=model)
    return {"gloss": gloss}

def do_generate_video(gloss_text, output_dir="outputs"):
    session_id = uuid.uuid4().hex[:10]
    gloss_tokens = gloss_text.split()
    output_path = f"{output_dir}/final_{session_id}.mp4"

    with tempfile.TemporaryDirectory() as temp_dir:
        clip_paths, word_breakdown = resolve_gloss_to_clips(gloss_tokens, temp_dir, session_id)
        concatenate_videos(clip_paths, output_path)

    return {
        "video_url": f"/{output_path}",
        "word_breakdown": word_breakdown
    }