from flask import Flask, request, jsonify
from deepface import DeepFace
import speech_recognition as sr
from pydub import AudioSegment
import base64
import io
import os
import tempfile
import smtplib
from email.message import EmailMessage
import cv2
import numpy as np
import webbrowser
import random
import pyttsx3
import logging
import pathlib
import threading

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('emoticare')

app = Flask(__name__)

# Create a temporary directory for file operations
TEMP_DIR = tempfile.mkdtemp(prefix="emoticare_")
logger.info(f"Using temporary directory: {TEMP_DIR}")

# Enable CORS for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# List of keywords to detect emotion from speech
EMOTION_KEYWORDS = {
    "happy": ["happy", "glad", "joy", "excited", "optimistic", "great", "wonderful", "amazing", "fantastic"],
    "sad": ["sad", "depressed", "upset", "down", "unhappy", "miserable", "disappointed", "heartbroken"],
    "angry": ["angry", "mad", "annoyed", "irritated", "furious", "frustrated", "rage"],
    "neutral": ["okay", "fine", "alright", "normal", "average"]
}

# Map emotions to song URLs
SONGS = {
    "happy": [
        "https://youtu.be/fRD_3vJagxk?si=EfiIimaOZSNyshwN",  # Vaathi Coming
        "https://youtu.be/KUN5Uf9mObQ?si=1tW4ETDRyQHCxt8n",  # Arabic Kuthu
        "https://youtu.be/PhxfspwMdww?si=1F13ol5V8VQgkT7_",  # jollyo gymkhana
    ],
    "sad": [
        "https://youtu.be/EhhiY11Z9-U?si=Vfe1vr1xWSxnvxLV",  # Ennodu Nee Irundhaal
        "https://youtu.be/laoJjq7-WGQ?si=b1IQprBXC3d6HWbX",  # Kanmani Anbodu
        "https://youtu.be/fYkQzTAx3Yo?si=aP1QhVB72punJnYl",  # Neeyum Naanum
    ],
    "angry": [
        "https://youtu.be/0zz172zODiY?si=Ne0lwBzfaYtmAcYX",  # Surviva
        "https://youtu.be/y3tfpBxoci4?si=tMVYIeaE3ss7XWHc",  # Vikram - Wasted
        "https://youtu.be/WWr9086eWtY?si=n0l9eT9nhfFQ9d1i",  # Yaanji (Soothing to calm)
    ],
    "neutral": [
        "https://youtu.be/WWr9086eWtY?si=n0l9eT9nhfFQ9d1i",  # Calm music
    ]
}

# Email configuration
MENTOR_EMAIL = "harshanaa.c.r.it26@psvpec.in"
SENDER_EMAIL = "harshanaaramesh@gmail.com"
SENDER_PASSWORD = "tjrc qiuk jzwa ykal"  # App password, not actual account password

def analyze_text(text):
    """
    Analyzes text to detect emotion from keywords
    """
    try:
        # Log the received text
        logger.info(f"Analyzing text: {text}")
        
        # Check for keywords in the text
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if any(word in text.lower() for word in keywords):
                logger.info(f"Detected emotion from text: {emotion}")
                return emotion
                
        # If no keywords matched, use default
        return "neutral"
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return "neutral"

def analyze_audio(audio_blob):
    """
    Analyzes audio data to detect emotion from speech
    """
    recognizer = sr.Recognizer()
    
    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(suffix=".wav", dir=TEMP_DIR, delete=False) as temp_audio:
            temp_audio.write(audio_blob)
            audio_path = temp_audio.name
            
        logger.info(f"Saved audio to: {audio_path}")
        
        # Convert to format compatible with speech_recognition
        audio = AudioSegment.from_file(audio_path)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", dir=TEMP_DIR, delete=False) as temp_converted:
            converted_path = temp_converted.name
            
        audio.export(converted_path, format="wav")
        logger.info(f"Converted audio to: {converted_path}")

        with sr.AudioFile(converted_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                logger.info(f"Transcribed Text: {text}")
                
                # Basic sentiment analysis based on keywords
                return analyze_text(text)
            except sr.UnknownValueError:
                logger.warning("Could not understand the audio")
                return "neutral"
            except Exception as e:
                logger.error(f"Error in speech recognition: {e}")
                return "neutral"
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return "neutral"
    finally:
        # Clean up temporary files
        try:
            os.remove(audio_path)
            os.remove(converted_path)
        except:
            pass

def analyze_image(image_data):
    """
    Analyzes image data to detect emotion from facial expressions
    """
    try:
        # Decode base64 image
        img_bytes = base64.b64decode(image_data.split(",")[1])
        
        # Create a temporary file for the image
        with tempfile.NamedTemporaryFile(suffix=".jpg", dir=TEMP_DIR, delete=False) as temp_img:
            temp_img.write(img_bytes)
            image_path = temp_img.name
            
        logger.info(f"Saved image to: {image_path}")
        
        # Convert to OpenCV format
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Could not decode image")
            return "neutral"
        
        # Analyze with DeepFace
        result = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        
        # Get dominant emotion
        dominant_emotion = result[0]["dominant_emotion"]
        logger.info(f"Detected face emotion: {dominant_emotion}")
        
        # Map DeepFace emotions to our simplified set if needed
        emotion_mapping = {
            "happy": "happy",
            "sad": "sad",
            "angry": "angry",
            "neutral": "sad",
            "fear": "sad",  # Map fear to sad for simplicity
            "surprise": "sad",
            "disgust": "angry"  # Map disgust to angry for simplicity
        }
        
        return emotion_mapping.get(dominant_emotion, "neutral")
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return "neutral"
    finally:
        # Clean up temporary file
        try:
            os.remove(image_path)
        except:
            pass

def play_music(emotion):
    """
    Selects and attempts to play a song based on detected emotion
    """
    if emotion in SONGS and SONGS[emotion]:
        url = random.choice(SONGS[emotion])
        try:
            # Start the browser in a new thread to avoid blocking the server
            thread = threading.Thread(target=webbrowser.open, args=(url,))
            thread.daemon = True
            thread.start()
            logger.info(f"Opening music URL for {emotion}: {url}")
            return url
        except Exception as e:
            logger.error(f"Error opening URL: {e}")
            return None
    return None

def interact_with_user(emotion):
    """
    Provides verbal feedback to the user based on detected emotion
    """
    try:
        responses = {
            "happy": "I'm so glad you're feeling happy! Keep spreading those positive vibes!",
            "sad": "I'm here for you. It's okay to feel sad sometimes. You're not alone.",
            "angry": "Take a deep breath... Let's calm down together. Things will get better.",
            "neutral": "Hope you're having a peaceful day! Let me know if you need anything.",
            "surprise": "Wow, you seem surprised! Hope it's a good one!",
            "fear": "Don't worry, you're safe. I'm right here with you.",
            "disgust": "Yikes! That doesn't sound great. Let's try to turn things around."
        }

        message = responses.get(emotion, "I'm here with you no matter how you feel.")
        logger.info(f"Assistant responds to {emotion}: {message}")

        def speak():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0)
                
                # Try to set female voice if available
                voices = engine.getProperty('voices')
                for voice in voices:
                    if "female" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                
                engine.say(message)
                engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS thread error: {e}")

        thread = threading.Thread(target=speak)
        thread.daemon = True
        thread.start()
        return True
    except Exception as e:
        logger.error(f"Error in text-to-speech setup: {e}")
        return False

def send_alert_email(emotion):
    """
    Sends an alert email to the mentor if the user appears sad
    """
    if emotion != "sad":
        return False
        
    try:
        msg = EmailMessage()
        msg.set_content(f"Alert: The user appears to be feeling {emotion}. Please check on them.")
        msg['Subject'] = "Emotion Alert from EmotiCare"
        msg['From'] = SENDER_EMAIL
        msg['To'] = MENTOR_EMAIL

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        logger.info("Alert email sent to mentor!")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

@app.route("/api/analyze/text", methods=["POST"])
def text_analysis():
    """
    New endpoint for text emotion analysis
    """
    try:
        if not request.json:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Get the transcript from the client
        transcript = request.json.get("transcript", "")
        client_emotion = request.json.get("detectedEmotion", "neutral")
        
        # Server-side verification of the emotion
        server_emotion = analyze_text(transcript)
        
        # Final emotion - we can choose to trust the client or use our server detection
        # Here we're using the server detection, but you could also use the client's
        final_emotion = server_emotion
        
        # For sad emotion, always send an alert email
        if final_emotion == "sad":
            send_alert_email(final_emotion)
            
        # Always interact with user based on emotion (motivational response)
        interact_with_user(final_emotion)
        
        # Play music based on emotion and get the URL
        song_url = play_music(final_emotion)
        
        return jsonify({
            "emotion": final_emotion,
            "transcript": transcript,
            "song_url": song_url,
            "alert_sent": final_emotion == "sad",
            "motivation_provided": True,
            "music_triggered": song_url is not None
        })
    except Exception as e:
        logger.error(f"Error in text analysis endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze/audio", methods=["POST"])
def audio_analysis():
    """
    Endpoint for audio emotion analysis
    """
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
            
        audio = request.files["audio"].read()
        emotion = analyze_audio(audio)
        
        # Send alert for sad emotion
        if emotion == "sad":
            send_alert_email(emotion)
            
        # Always interact with user based on emotion (motivational response)
        interact_with_user(emotion)
        
        # Play music based on emotion and get the URL
        song_url = play_music(emotion)
        
        return jsonify({
            "emotion": emotion,
            "song_url": song_url,
            "alert_sent": emotion == "sad",
            "motivation_provided": True,
            "music_triggered": song_url is not None
        })
    except Exception as e:
        logger.error(f"Error in audio analysis endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze/video", methods=["POST"])
def video_analysis():
    """
    Endpoint for facial emotion analysis
    """
    try:
        if not request.json or 'image' not in request.json:
            return jsonify({"error": "No image data provided"}), 400
            
        image_data = request.json["image"]
        emotion = analyze_image(image_data)
        
        # Send alert for sad emotion
        if emotion == "sad":
            send_alert_email(emotion)
        if emotion == "neutral":
            send_alert_email('sad')
            
        # Always interact with user based on emotion (motivational response)
        interact_with_user(emotion)
        
        # Play music based on emotion and get the URL
        song_url = play_music(emotion if emotion != "neutral" else "sad")
        
        return jsonify({
            "emotion": emotion,
            "song_url": song_url,
            "alert_sent": emotion == "sad" or emotion == "neutral",
            "motivation_provided": True,
            "music_triggered": song_url is not None
        })
    except Exception as e:
        logger.error(f"Error in video analysis endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze/both", methods=["POST"])
def combined_analysis():
    """
    Endpoint for combined audio and video emotion analysis
    """
    try:
        if 'audio' not in request.files or 'image' not in request.form:
            return jsonify({"error": "Missing audio or image data"}), 400
            
        audio = request.files["audio"].read()
        image_data = request.form["image"]
        
        audio_emotion = analyze_audio(audio)
        video_emotion = analyze_image(image_data)
        
        # Prioritize sad emotion if either source detects it
        final_emotion = "sad" if "sad" in [audio_emotion, video_emotion] else (audio_emotion or video_emotion)
        
        # Send alert for sad emotion
        if final_emotion == "sad":
            send_alert_email(final_emotion)
            
        # Always interact with user based on emotion (motivational response)
        interact_with_user(final_emotion)
        
        # Play music based on emotion and get the URL
        song_url = play_music(final_emotion)
        
        return jsonify({
            "emotion": final_emotion,
            "audio_emotion": audio_emotion,
            "video_emotion": video_emotion,
            "song_url": song_url,
            "alert_sent": final_emotion == "sad",
            "motivation_provided": True,
            "music_triggered": song_url is not None
        })
    except Exception as e:
        logger.error(f"Error in combined analysis endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/play_music/<emotion>", methods=["GET"])
def play_specific_music(emotion):
    """
    Endpoint to directly trigger music playback for a specific emotion
    """
    try:
        song_url = play_music(emotion)
        return jsonify({
            "emotion": emotion,
            "song_url": song_url,
            "music_triggered": song_url is not None
        })
    except Exception as e:
        logger.error(f"Error in play music endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok", "service": "EmotiCare API"})

if __name__ == "__main__":
    # Ensure temp directory exists with proper permissions
    pathlib.Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)
    
    # Start Flask server
    app.run(host="0.0.0.0", port=5000, debug=True)