import os
import cv2
import threading
import base64
import time
import requests
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play
import google.generativeai as genai
from PIL import Image
import numpy as np
import errno

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Set the API keys for Google AI and ElevenLabs
GOOGLE_API_KEY = 'YOUR KEY HERE'
ELEVENLABS_API_KEY = 'YOUR KEY HERE'
# Voice ID for ElevenLabs API (I using a standard voice but make sure you have access to it)
VOICE_ID = 'lNHyfbhlVgOTtlbts3eH'

# Configure the Google AI client
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

# Folder to save frames
folder = "frames"
if not os.path.exists(folder):
    os.makedirs(folder)

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Queue to store text responses
text_queue = Queue()

# Flag to indicate when audio playback is in progress
audio_playing = threading.Event()

# Global variables
running = True
capture_interval = 2  # Default interval in seconds

def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
        except IOError as e:
            if e.errno == errno.EACCES:
                print("Permission denied, retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Error {e.errno}: {e.strerror}")
                return None

def generate_audio(text, filename):
    if len(text) > 2500:
        raise ValueError("Text exceeds the character limit of 2500 characters.")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    with open(filename, 'wb') as f:
        f.write(response.content)

def play_audio():
    global audio_playing
    current_audio = "voice_current.mp3"
    next_audio = "voice_next.mp3"
    while True:
        text = text_queue.get()
        if text is None:
            break
        audio_playing.set()
        try:
            generate_audio(text, next_audio)
            os.rename(next_audio, current_audio)

            audio = AudioSegment.from_file(current_audio, format="mp3")
            play(audio)
        except Exception as e:
            print(f"Error in play_audio: {e}")
        finally:
            audio_playing.clear()

def generate_new_line(encoded_image):
    return [
        {
            "role": "user",
            "content": {
                "parts": [
                    {
                        "text": "Please describe what you see in max 30 words. You are an helpful and friendly assistant called Astra. If you see questions visually answer them is very important! "
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }
        }
    ]

def analyze_image(encoded_image, script):
    try:
        messages = script + generate_new_line(encoded_image)
        content_messages = [
            {
                "role": message["role"],
                "parts": [
                    {"text": part["text"]} if "text" in part else {"inline_data": part["inline_data"]}
                    for part in message["content"]["parts"]
                ]
            }
            for message in messages
        ]
        response = model.generate_content(content_messages)
        return response.text
    except Exception as e:
        print(f"Error in analyze_image: {e}")
        return ""

def capture_images():
    global capture_interval
    global script
    script = []
    cap = cv2.VideoCapture(0)
    while running:
        try:
            ret, frame = cap.read()
            if ret:
                # Encode the frame to base64
                _, buffer = cv2.imencode('.jpg', frame)
                encoded_image = base64.b64encode(buffer).decode('utf-8')
                socketio.emit('stream', {'image': encoded_image})
                
                # Analyze the frame
                response_text = analyze_image(encoded_image, script)
                print(f"Jarvis's response: {response_text}")

                with text_queue.mutex:
                    text_queue.queue.clear()  # Clear the queue

                text_queue.put(response_text)
                socketio.emit('text', {'message': response_text})
                script.append(
                    {
                        "role": "model",
                        "content": {
                            "parts": [
                                {
                                    "text": response_text
                                }
                            ]
                        }
                    }
                )
            else:
                print("Failed to capture image")

            time.sleep(capture_interval)
        except Exception as e:
            print(f"Error in capture_images: {e}")
    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stop')
def stop():
    global running
    running = False
    return jsonify({"status": "stopped"})

@app.route('/resume')
def resume():
    global running
    global capture_thread
    running = True
    if not capture_thread.is_alive():
        capture_thread = threading.Thread(target=capture_images)
        capture_thread.start()
    return jsonify({"status": "resumed"})

@app.route('/set_interval', methods=['POST'])
def set_interval():
    global capture_interval
    interval = request.json.get('interval')
    if interval:
        capture_interval = interval
        return jsonify({"status": "interval updated", "interval": capture_interval})
    return jsonify({"status": "failed", "message": "Invalid interval"}), 400

import webbrowser

if __name__ == '__main__':
    global capture_thread
    global audio_thread
    running = True
    capture_thread = threading.Thread(target=capture_images)
    capture_thread.start()
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()
    
    # Open the default web browser to the server link
    webbrowser.open('http://localhost:5001')
    
    socketio.run(app, host='0.0.0.0', port=5001)
    capture_thread.join()
    text_queue.put(None)
    audio_thread.join()
