DIY-Astra
DIY-Astra is a Flask application that utilizes computer vision and natural language processing to create an interactive AI assistant. The application captures live video feed from a webcam, analyzes the captured images using the Google AI API, and generates text responses based on the visual input. The generated text responses are then converted to audio using the ElevenLabs API and played back to the user.
Features

Live video feed capture from the webcam
Image analysis using the Google AI API
Text generation based on visual input
Text-to-speech conversion using the ElevenLabs API
Real-time audio playback of generated responses
Web-based user interface for interaction and control

Requirements
To run the DIY-Astra application, you need to have the following dependencies installed:

Python 3.x
Flask
Flask-SocketIO
OpenCV (cv2)
Pydub
Google Generative AI Client Library
Pillow (PIL)
Requests

You also need to have valid API keys for the following services:

Google AI API (GOOGLE_API_KEY)
ElevenLabs API (ELEVENLABS_API_KEY)

Installation

Clone the repository:
Copy codegit clone https://github.com/your-username/diy-astra.git

Navigate to the project directory:
Copy codecd diy-astra

Install the required dependencies:
Copy codepip install -r requirements.txt

Set up the API keys:

Replace GOOGLE_API_KEY in app.py with your Google AI API key.
Replace ELEVENLABS_API_KEY in app.py with your ElevenLabs API key.


Run the application:
Copy codepython app.py

Open your web browser and navigate to http://localhost:5001 to access the DIY-Astra interface.

Usage

Make sure your webcam is connected and accessible.
Launch the DIY-Astra application by running python app.py.
The application will open in your default web browser.
The live video feed from your webcam will be displayed in the interface.
DIY-Astra will continuously capture images, analyze them using the Google AI API, and generate text responses based on the visual input.
The generated text responses will be displayed in the text container below the video feed.
The text responses will also be converted to audio using the ElevenLabs API and played back in real-time.
You can stop the application by clicking the "Stop" button in the interface. To resume, click the "Resume" button.

File Structure

app.py: The main Flask application file containing the server-side logic.
templates/index.html: The HTML template for the user interface.
static/css/styles.css: The CSS stylesheet for styling the user interface.
static/js/script.js: The JavaScript file for client-side interactions and socket communication.
requirements.txt: The list of required Python dependencies.

Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.
License
This project is licensed under the MIT License.
