import pyaudio
import wave
import audioop
import os
import threading

# Global variable to control silence detection
silence_detected = False

def reset_silence_flag():
    global silence_detected
    silence_detected = False

def record_audio():
    global silence_detected

    # Parameters for audio recording
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    SILENCE_THRESHOLD = 300  # Adjust as needed
    SILENCE_DURATION = 4
    # 4 seconds of silence
    p = pyaudio.PyAudio()

    # Find the last recorded file number
    file_number = 1
    while os.path.exists(f'test{file_number}.wav'):
        file_number += 1

    output_filename = f'test{file_number}.wav'

    # Open the audio stream
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    silence_counter = 0  # Initialize a silence counter

    print("Recording...")

    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        # Calculate the RMS energy of the audio
        rms = audioop.rms(data, 2)

        # Check if the audio is below the silence threshold
        if rms < SILENCE_THRESHOLD:
            silence_counter += 1
            if silence_counter >= int(SILENCE_DURATION * RATE / CHUNK) and not silence_detected:
                print("Please speak")
                silence_detected = True
                # Start a timer thread to reset the silence flag after 4 seconds
                reset_timer = threading.Timer(4, reset_silence_flag)
                reset_timer.start()
        else:
            silence_counter = 0

        # Check if the specified duration of silence has been detected
        if silence_counter >= int(SILENCE_DURATION * RATE / CHUNK):
            print("Silence detected. Recording finished.")
            break

    # Close the audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a WAV file
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved as {output_filename}")

    return output_filename
