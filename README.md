
# DIY-Astra

DIY-Astra is a Flask application that utilizes computer vision and natural language processing to create an interactive AI assistant. The application captures live video feed from a webcam, analyzes the captured images using OpenRouter API (with Claude Sonnet 4), and generates text responses based on the visual input. The generated text responses are then converted to audio using the ElevenLabs API and played back to the user.

## Features
- Live video feed capture from the webcam
- Image analysis using OpenRouter API with Claude Sonnet 4 (supports 400+ AI models)
- Text generation based on visual input with context-aware conversation memory
- Text-to-speech conversion using the ElevenLabs API
- Real-time audio playback of generated responses
- Web-based user interface for interaction and control
- Flexible model selection (Claude Sonnet 4, Claude 3.5 Sonnet, Claude 3.7 Sonnet, and more)

## Requirements
To run the DIY-Astra application, you need to have the following dependencies installed:
- Python 3.x
- Flask
- Flask-SocketIO
- OpenCV (cv2)
- Pydub
- Pillow (PIL)
- Requests

You also need to have valid API keys for the following services:
- OpenRouter API (OPENROUTER_API_KEY) - Get your free key at https://openrouter.ai/keys
- ElevenLabs API (ELEVENLABS_API_KEY) - For text-to-speech conversion

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/diy-astra.git
   ```

2. Navigate to the project directory:
   ```bash
   cd diy-astra
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the API keys:
   - Replace `OPENROUTER_API_KEY` in `app.py` with your OpenRouter API key.
   - Replace `ELEVENLABS_API_KEY` in `app.py` with your ElevenLabs API key.
   - (Optional) Change `MODEL_NAME` to use different AI models like:
     - `anthropic/claude-sonnet-4` (default, most capable)
     - `anthropic/claude-3.5-sonnet` (faster, cheaper)
     - `anthropic/claude-3.7-sonnet` (balanced)
     - Or any other vision-capable model from OpenRouter's 400+ models

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your web browser and navigate to `http://localhost:5001` to access the DIY-Astra interface.

## Usage
1. Make sure your webcam is connected and accessible.
2. Launch the DIY-Astra application by running `python app.py`.
3. The application will open in your default web browser.
4. The live video feed from your webcam will be displayed in the interface.
5. DIY-Astra will continuously capture images, analyze them using OpenRouter API (Claude Sonnet 4), and generate text responses based on the visual input.
6. The generated text responses will be displayed in the text container below the video feed.
7. The text responses will also be converted to audio using the ElevenLabs API and played back in real-time.
8. You can stop the application by clicking the "Stop" button in the interface. To resume, click the "Resume" button.
9. Adjust the capture interval (in seconds) to control how frequently Astra analyzes new images.

## File Structure
- `app.py`: The main Flask application file containing the server-side logic.
- `templates/index.html`: The HTML template for the user interface.
- `static/css/styles.css`: The CSS stylesheet for styling the user interface.
- `static/js/script.js`: The JavaScript file for client-side interactions and socket communication.
- `requirements.txt`: The list of required Python dependencies.

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.

