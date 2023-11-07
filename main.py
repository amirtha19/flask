from record_audio import record_audio
from transcribe import transcribe_audio_file
from sentimental_analysis import sentiment_analysis
from similarity import similarity

if __name__ == "__main__":
    output_file = record_audio()  # Record audio and get the output file name
    text = transcribe_audio_file(output_file)  # Transcribe the recorded audio
    sentiment_analysis(text)
    similarity(text,"text.txt")