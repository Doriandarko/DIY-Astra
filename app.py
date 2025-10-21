import os
import cv2
import threading
import base64
import time
import requests
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play
from PIL import Image
import numpy as np
import errno

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Set the API keys for OpenRouter and ElevenLabs
OPENROUTER_API_KEY = 'YOUR KEY HERE'
ELEVENLABS_API_KEY = 'YOUR KEY HERE'
# Voice ID for ElevenLabs API (I using a standard voice but make sure you have access to it)
VOICE_ID = 'lNHyfbhlVgOTtlbts3eH'

# Configure OpenRouter API
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Model options: anthropic/claude-sonnet-4, anthropic/claude-3.5-sonnet, anthropic/claude-3.7-sonnet
MODEL_NAME = "anthropic/claude-sonnet-4"

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
    """Generate a new message with image for OpenRouter API"""
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Please describe what you see in max 30 words. You are a helpful and friendly assistant called Astra. If you see questions visually answer them - this is very important!"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            }
        ]
    }

def analyze_image(encoded_image, script):
    """Send image to OpenRouter API (Claude) for analysis"""
    try:
        # Build messages array - convert script + new message
        messages = script + [generate_new_line(encoded_image)]

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5001",  # Optional, for rankings
            "X-Title": "DIY-Astra"  # Optional, shows in rankings
        }

        # Prepare request payload
        payload = {
            "model": MODEL_NAME,
            "messages": messages
        }

        # Make API request
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        # Extract response text
        result = response.json()
        return result['choices'][0]['message']['content']

    except Exception as e:
        print(f"Error in analyze_image: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
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
                # Resize and compress the image
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                max_size = 250
                ratio = max_size / max(pil_img.size)
                new_size = tuple([int(x * ratio) for x in pil_img.size])
                resized_img = pil_img.resize(new_size, Image.LANCZOS)
                frame = cv2.cvtColor(np.array(resized_img), cv2.COLOR_RGB2BGR)

                path = f"{folder}/frame.jpg"
                cv2.imwrite(path, frame)
                print("📸 Saving photo.")

                encoded_image = encode_image(path)
                print(f"Encoded image: {encoded_image[:30]}...")  # Debug print

                if not encoded_image:
                    print("Failed to encode image. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue

                socketio.emit('stream', {'image': encoded_image})
                
                response_text = analyze_image(encoded_image, script)
                print(f"Jarvis's response: {response_text}")

                with text_queue.mutex:
                    text_queue.queue.clear()  # Clear the queue

                text_queue.put(response_text)
                socketio.emit('text', {'message': response_text})
                # Add assistant's response to conversation history (OpenAI format)
                script.append(
                    {
                        "role": "assistant",
                        "content": response_text
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
