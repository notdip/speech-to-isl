import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import gradio as gr
from pipeline import text_to_gloss, do_generate_video, do_transcribe

def process_text(text):
    if not text or not text.strip():
        return None, "Please enter a sentence."
    gloss = text_to_gloss(text)
    result = do_generate_video(gloss)
    return result["video_url"].lstrip("/"), f"Gloss: {gloss}"

def process_audio(audio_path):
    if not audio_path:
        return None, "Please record or upload audio."
    transcript_result = do_transcribe(audio_path)
    text = transcript_result["text"]
    gloss = text_to_gloss(text)
    result = do_generate_video(gloss)
    return result["video_url"].lstrip("/"), f"Transcript: {text}\nGloss: {gloss}"

with gr.Blocks(title="Speech to ISL") as demo:
    gr.Markdown("# Speak. See it signed.")
    gr.Markdown("Convert English text or speech into Indian Sign Language.")

    with gr.Tab("Text Input"):
        text_input = gr.Textbox(label="Enter a sentence", placeholder="I am going to school tomorrow")
        text_btn = gr.Button("Translate", variant="primary")
        text_video = gr.Video(label="Sign Language Output")
        text_info = gr.Textbox(label="Details", interactive=False)
        text_btn.click(process_text, inputs=text_input, outputs=[text_video, text_info])

    with gr.Tab("Speech Input"):
        audio_input = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Record or upload audio")
        audio_btn = gr.Button("Translate", variant="primary")
        audio_video = gr.Video(label="Sign Language Output")
        audio_info = gr.Textbox(label="Details", interactive=False)
        audio_btn.click(process_audio, inputs=audio_input, outputs=[audio_video, audio_info])

if __name__ == "__main__":
    demo.launch()