from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys, os, shutil, tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from pipeline import do_transcribe, do_translate, do_generate_video

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("outputs/words", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.post("/api/transcribe")
def transcribe(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    result = do_transcribe(tmp_path)
    os.unlink(tmp_path)
    return result

@app.post("/api/translate")
def translate(text: str = Form(...), model: str = Form("llama3.1:8b")):
    return do_translate(text, model=model)

@app.post("/api/generate-video")
def generate_video(gloss: str = Form(...)):
    return do_generate_video(gloss)