import whisper

_model = None  # loaded once, reused across calls

def load_whisper_model(size="small"):
    global _model
    if _model is None:
        print(f"Loading Whisper model: {size}...")
        _model = whisper.load_model(size)
    return _model

def transcribe_audio(audio_path, model_size="small"):
    model = load_whisper_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"].strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python speech_to_text.py <path_to_audio_file>")
        sys.exit(1)

    audio_path = sys.argv[1]
    text = transcribe_audio(audio_path)
    print(f"\nTranscribed text: {text}")