import os
import torch
from pathlib import Path
import whisper
from whisper.utils import get_writer

# Initialize Whisper model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("medium.en").to(DEVICE)

def transcribe_audio_file(audio_file_path):
    file_path = Path(audio_file_path)
    print(f"Transcribing file: {file_path}\n")
    output_directory = file_path.parent
    result = model.transcribe(audio_file_path,fp16=False)
    txt_path = file_path.with_suffix(".txt")
    print(f"Creating text file")
    with open(txt_path, "w", encoding="utf-8") as txt:
        txt.write(result["text"])
    return txt_path
