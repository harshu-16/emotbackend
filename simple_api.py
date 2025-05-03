from flask import Flask, request, jsonify
from flask_cors import CORS
from face_emotion import analyze_emotion_from_image
import threading
import time
import base64
import os
import json
import speech_recognition as sr  # Added for speech to text

# Mock facial emotion analyzer
def mock_analyze_face_emotion(image_path=None):
    print(f"Mock analyzing face from image: {image_path}")
    return "happy"

# NEW: Voice emotion analysis using keyword-based text analysis
def keyword_based_voice_emotion(audio_path=None):
    print(f"Analyzing voice emotion (keyword-based) from: {audio_path}")
    
    emotion_keywords = {
        "happy": "happy",
        "glad": "happy",
        "joy": "happy",
        "enjoy": "happy",
        "sad": "sad",
        "unhappy": "sad",
        "depressed": "sad",
        "angry": "angry",
        "upset": "angry",
        "mad": "angry",
        "scared": "fear",
        "afraid": "fear",
        "nervous": "fear"
    }

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening for voice input...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        
        text = recognizer.recognize_google(audio)
        print(f"Recognized Text: {text}")
        
        detected_emotion = "neutral"
        for keyword, emotion in emotion_keywords.items():
            if keyword in text.lower():
                detected_emotion = emotion
                break

        return detected_emotion

    except sr.UnknownValueError:
        return "neutral"
    except Exception as e:
        print(f"Voice recognition error: {e}")
        return "neutral"

# Other mock interactions (same as before)
def mock_interact_based_on_emotion(emotion):
    print(f"Mock interacting with user based on emotion: {emotion}")
    time.sleep(2)
    return True

def mock_send_alert_email(emotion):
    print(f"Mock sending alert email for emotion: {emotion}")
    time.sleep(1)
    return True

def mock_play_music_based_on_emotion(emotion):
    print(f"Mock playing music for emotion: {emotion}")
    time.sleep(1)
    return True

app = Flask(__name__)
CORS(app)

ongoing_analysis = {
    "face_emotion": None,
    "voice_emotion": None,
    "final_emotion": None,
    "status": "idle",
    "message": ""
}

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(ongoing_analysis)

@app.route('/api/reset', methods=['GET'])
def reset_status():
    global ongoing_analysis
    ongoing_analysis = {
        "face_emotion": None,
        "voice_emotion": None,
        "final_emotion": None,
        "status": "idle",
        "message": ""
    }
    return jsonify({"status": "reset successful"})

@app.route('/api/analyze_face', methods=['POST'])
def api_analyze_face():
    global ongoing_analysis
    
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        ongoing_analysis["status"] = "analyzing_face"
        ongoing_analysis["message"] = "Analyzing facial expression..."

        def analyze_face_thread():
            try:
                # For now, just pass None (or later save image and pass its path)
                emotion = analyze_emotion_from_image(None)
                ongoing_analysis["face_emotion"] = emotion
                update_final_emotion()
            except Exception as e:
                ongoing_analysis["message"] = f"Face analysis error: {str(e)}"
        
        thread = threading.Thread(target=analyze_face_thread)
        thread.start()

        return jsonify({"status": "Face analysis started"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze_voice', methods=['POST'])
def api_analyze_voice():
    global ongoing_analysis
    
    try:
        ongoing_analysis["status"] = "analyzing_voice"
        ongoing_analysis["message"] = "Analyzing voice emotion..."

        def analyze_voice_thread():
            try:
                emotion = keyword_based_voice_emotion()  # UPDATED function call
                ongoing_analysis["voice_emotion"] = emotion
                update_final_emotion()
            except Exception as e:
                ongoing_analysis["message"] = f"Voice analysis error: {str(e)}"
        
        thread = threading.Thread(target=analyze_voice_thread)
        thread.start()

        return jsonify({"status": "Voice analysis started"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/interact', methods=['POST'])
def api_interact():
    emotion = request.json.get('emotion')
    if not emotion:
        return jsonify({"error": "No emotion provided"}), 400

    def interact_thread():
        try:
            mock_interact_based_on_emotion(emotion)
        except Exception as e:
            print(f"Interaction error: {e}")

    thread = threading.Thread(target=interact_thread)
    thread.start()

    return jsonify({"status": "Interaction started"})

@app.route('/api/play_music', methods=['POST'])
def api_play_music():
    emotion = request.json.get('emotion')
    if not emotion:
        return jsonify({"error": "No emotion provided"}), 400

    def music_thread():
        try:
            mock_play_music_based_on_emotion(emotion)
        except Exception as e:
            print(f"Music play error: {e}")

    thread = threading.Thread(target=music_thread)
    thread.start()

    return jsonify({"status": "Music playing started"})

@app.route('/api/send_alert', methods=['POST'])
def api_send_alert():
    emotion = request.json.get('emotion')
    if not emotion:
        return jsonify({"error": "No emotion provided"}), 400

    def alert_thread():
        mock_send_alert_email(emotion)

    thread = threading.Thread(target=alert_thread)
    thread.start()

    return jsonify({"status": "Alert email sent"})

def update_final_emotion():
    global ongoing_analysis
    face_emotion = ongoing_analysis["face_emotion"]
    voice_emotion = ongoing_analysis["voice_emotion"]
    
    if face_emotion in ['sad', 'angry', 'disgust'] or voice_emotion in ['sad', 'angry', 'disgust']:
        final_emotion = face_emotion if face_emotion in ['sad', 'angry', 'disgust'] else voice_emotion
        ongoing_analysis["final_emotion"] = final_emotion
        ongoing_analysis["status"] = "alert_needed"
        ongoing_analysis["message"] = f"User seems {final_emotion}. Alert may be needed."
    elif face_emotion or voice_emotion:
        final_emotion = face_emotion or voice_emotion
        ongoing_analysis["final_emotion"] = final_emotion
        ongoing_analysis["status"] = "completed"
        ongoing_analysis["message"] = "Analysis complete. User seems fine."

    if ongoing_analysis["final_emotion"]:
        if ongoing_analysis["status"] != "alert_needed":
            ongoing_analysis["status"] = "completed"

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "API is running",
        "endpoints": [
            "/api/status", 
            "/api/reset",
            "/api/analyze_face",
            "/api/analyze_voice",
            "/api/interact",
            "/api/play_music",
            "/api/send_alert"
        ]
    })

if __name__ == '__main__':
    # Bind to the PORT environment variable on Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
