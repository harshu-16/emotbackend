from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys
import time
import random
import webbrowser
import smtplib
from email.message import EmailMessage

# Import emotion detection modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from face_emotion import analyze_emotion_from_image
from voice_emotion import keyword_based_analysis

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wav', 'mp3'}
MENTOR_EMAIL = "harshanaa.c.r.it26@psvpec.in"
SENDER_EMAIL = "harshanaaramesh@gmail.com"
SENDER_PASSWORD = "tjrc qiuk jzwa ykal"  # App password, not actual password

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Tamil song collections based on mood
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

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(prefix, ext):
    timestamp = int(time.time())
    return f"{prefix}_{timestamp}.{ext}"

def play_music_based_on_emotion(emotion):
    """
    Opens a web browser to play a song based on detected emotion
    """
    if emotion in SONGS and SONGS[emotion]:
        url = random.choice(SONGS[emotion])
        print(f"🎵 Playing music for {emotion} mood: {url}")
        try:
            webbrowser.open(url)
            return url
        except Exception as e:
            print(f"Error opening browser: {e}")
            return None
    else:
        print("No music found for this emotion.")
        return None

def send_alert_email(emotion):
    """
    Sends an alert email to the mentor if the user is detected to be sad
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
        print("Alert email sent to mentor!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# API Routes
@app.route('/api/analyze/audio', methods=['POST'])
def process_audio():
    """
    Endpoint to process uploaded audio and detect emotion
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    
    file = request.files['audio']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(generate_filename('audio', 'wav'))
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the audio file - here we use a simplified approach with keyword analysis
            # In a full implementation you'd use the recorded audio for proper analysis
            
            # For demo purposes we're using a random emotion
            # In production, you'd process the actual audio file
            emotions = ['happy', 'sad', 'angry', 'neutral']
            emotion = random.choice(emotions)
            
            # Send alert email if sad
            if emotion == 'sad':
                send_alert_email(emotion)
            
            # Play appropriate music
            song_url = play_music_based_on_emotion(emotion)
            
            return jsonify({
                'status': 'success',
                'emotion': emotion,
                'song_url': song_url
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/api/analyze/video', methods=['POST'])
def process_image():
    """
    Endpoint to process uploaded image and detect emotion
    """
    if not request.json or 'image' not in request.json:
        return jsonify({'error': 'No image data found'}), 400
    
    try:
        # Get base64 image data
        image_data = request.json['image']
        
        # Extract the base64 part (remove data:image/jpeg;base64,)
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Save as image file
        filename = generate_filename('face', 'jpg')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        import base64
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(image_data))
        
        # Analyze face emotion
        emotion = analyze_emotion_from_image(filepath)
        
        # Send alert email if sad
        if emotion == 'sad':
            send_alert_email(emotion)
        
        # Play appropriate music
        song_url = play_music_based_on_emotion(emotion)
        
        return jsonify({
            'status': 'success',
            'emotion': emotion,
            'song_url': song_url
        })
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/both', methods=['POST'])
def process_both():
    """
    Endpoint to process both audio and image for combined emotion analysis
    """
    # This would be a more complex implementation combining both 
    # For now, we'll just return a placeholder response
    return jsonify({
        'status': 'error',
        'message': 'Combined analysis not implemented yet'
    }), 501

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve uploaded files
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Handle CORS for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == '__main__':
    # Run app
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)