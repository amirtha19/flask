from flask import render_template, request, Blueprint, Response, redirect, url_for, jsonify, send_file,flash
from flaskblog.models import Post
import subprocess
from flask import Flask, request
import pyaudio
import wave
import audioop
import os
import threading
import torch
import whisper
from whisper.utils import get_writer
from pathlib import Path
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import re

model1 = SentenceTransformer('stsb-roberta-large')

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("medium.en").to(DEVICE)

silence_detected = False
audio_chunks = []

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', title='About')

@main.route('/addoption', methods=['GET', 'POST'])
def options():
    return render_template('option.html')

# Route to handle form submission and save options to a text file
@main.route('/submit_options', methods=['POST'])
def submit_options():
    if request.method == 'POST':
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')

        # Save the options to a text file
        with open('options.txt', 'a') as file:
            file.write(f'a) {option1}\n')
            file.write(f'b) {option2}\n')
            file.write(f'c) {option3}\n')
            file.write(f'd) {option4}\n')

        return redirect(url_for('main.about'))

def reset_silence_flag():
    global silence_detected
    silence_detected = False

@main.route('/start_record', methods=['POST'])
def record_audio():
    # Parameters for audio recording
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 15  # You can adjust the recording time as needed
    OUTPUT_FILENAME = "recorded_audio.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a WAV file
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    flash("Audio recorded successfully!", "success")  # Inform the user

    # Redirect to the transcribe_audio route
    return redirect(url_for('main.transcribe_audio', audio_file=OUTPUT_FILENAME))

@main.route('/transcribe_audio/<audio_file>', methods=['GET'])
def transcribe_audio(audio_file):
    # Path to the recorded audio file
    audio_file_path = audio_file

    # Transcribe the audio
    result = model.transcribe(audio_file_path, fp16=False)
    txt_path = "C:\\Users\\amirt\\Downloads\\Auth-20231104T123608Z-002\\Auth\\transcription.txt"
    with open(txt_path, "w", encoding="utf-8") as txt:
        txt.write(result["text"])
    # Get the transcription text
    transcription_message = result["text"]

    return render_template('about.html', title='About', transcription_message=transcription_message)

@main.route('/get_transcription', methods=['GET'])
def get_transcription():
    # You need to replace this with the actual path to your transcription.txt file
    txt_path = "C:\\Users\\amirt\\Downloads\\Auth-20231104T123608Z-002\\Auth\\transcription.txt"

    try:
        with open(txt_path, "r", encoding="utf-8") as txt:
            transcription_message = txt.read()
    except FileNotFoundError:
        transcription_message = "Transcription not available."

    return jsonify(transcription_message=transcription_message,redirect_url='/sentiment_analysis')

sentiment_analysis_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

@main.route('/sentiment_analysis', methods=['POST'])
def sentiment_analysis():
    txt_path = "C:\\Users\\amirt\\Downloads\\Auth-20231104T123608Z-002\\Auth\\transcription.txt"
    
    # Read the transcription message from the file
    with open(txt_path, "r", encoding="utf-8") as txt:
        transcription_message = txt.read()

    # Split the text into sentences using periods as delimiters
    sentences = transcription_message.split('.')

    # Initialize lists to store sentiment and confidence for each sentence
    sentence_sentiments = []
    sentence_confidences = []

    # Predict the sentiment for each sentence
    for sentence in sentences:
        # Remove leading and trailing spaces from the sentence
        sentence = sentence.strip()

        if sentence:
            # Predict the sentiment of the sentence
            result = sentiment_analysis_pipeline(sentence)

            if result:
                # Access the sentiment prediction
                sentiment = result[0]["label"]
                confidence = result[0]["score"]

                # Append the sentiment and confidence to the lists
                sentence_sentiments.append(sentiment)
                sentence_confidences.append(confidence)

    # Prepare the response as a list of dictionaries for each sentence
    sentence_results = []
    for i, sentence in enumerate(sentences):
        if i < len(sentence_sentiments):
            result = {
                'sentence': sentence,
                'sentiment': sentence_sentiments[i],
                'confidence': sentence_confidences[i]
            }
            sentence_results.append(result)

    # Return the sentiment analysis results as JSON
    return jsonify(sentence_results=sentence_results,redirect_url='/calculate_similarity')

@main.route('/calculate_similarity', methods=['POST'])
def calculate_similarity():
    if request.method == 'POST':
        
        with open('options,txt','r') as f:
            options_content = f.read()
        with open('transcription.txt','r') as d:
            text =d.read()
        # Split the options using the patterns "a)", "b)", "c)", etc.
        options = re.split(r'([a-z]\))', options_content)

        # Filter out empty strings and whitespace
        options = [option.strip() for option in options if option.strip()]

        max_similarity_score = -1  # Initialize with a low value
        most_similar_option = None
        similar_options = []

        for i in range(1, len(options), 2):
            option = options[i]  # Get the option text

            # Calculate the similarity between the text and the current option
            embeddings = model.encode([text, option], convert_to_tensor=True)
            similarity_score = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

            if similarity_score > max_similarity_score:
                max_similarity_score = similarity_score
                most_similar_option = option

            if similarity_score < 0.5:
                similar_options.append((option, similarity_score))

        response = {
            'text_content': text,
            'most_similar_option': most_similar_option,
            'max_similarity_score': max_similarity_score,
            'similar_options': similar_options
        }

        return jsonify(response)

