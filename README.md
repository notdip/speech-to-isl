# Speech to ISL

Convert English speech or text into Indian Sign Language (ISL) video, via LLM-based gloss translation and a multi-source sign-video pipeline.

## Pipeline
Audio/Text → Whisper (ASR) → LLM Gloss Translation (few-shot) → Gloss Cleanup → Fuzzy Vocabulary Matching → Video Assembly → Fingerspelling Fallback → Output Video

## Stack
- **Backend:** FastAPI, Ollama (Llama 3.1 8B / Qwen2.5 7B), Whisper, ffmpeg, rapidfuzz
- **Frontend:** React + Vite, motion, react-spring, Three.js
- **Datasets:** ASLG-PC12, CISLR, ISL Sign Dictionary, ISL Fingerspelling, iSign

## Setup
See `report.tex` / project report for full dataset acquisition and environment setup steps.

## Team
Dipesh & Associates — Generative AI Course Project