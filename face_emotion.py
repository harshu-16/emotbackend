import cv2
from deepface import DeepFace
import os
import time

def analyze_emotion_from_image(image_path):
    """
    Analyzes the emotion from a facial image using DeepFace
    
    Args:
        image_path: Path to the image file
        
    Returns:
        String representing the detected emotion
    """
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            print("Error: Could not read the image.")
            return "neutral"
            
        # Analyze emotions
        result = DeepFace.analyze(img_path=image_path, 
                                  actions=['emotion'], 
                                  enforce_detection=False)
        
        # Get all emotions with their scores
        emotions = result[0]['emotion']
        
        # Get the dominant emotion
        dominant_emotion = result[0]['dominant_emotion']
        
        # Print all emotions with their scores
        print("Emotion Analysis Results:")
        for emotion, score in emotions.items():
            print(f"{emotion}: {score:.2f}%")
        
        print(f"\nDominant Emotion: {dominant_emotion}")
        
        # Map to simplified emotions if needed
        emotion_mapping = {
            "happy": "happy",
            "sad": "sad",
            "angry": "angry",
            "neutral": "neutral",
            "fear": "sad",  # Map fear to sad
            "surprise": "neutral",
            "disgust": "angry"  # Map disgust to angry
        }
        
        return emotion_mapping.get(dominant_emotion, "neutral")
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return "neutral"

def capture_and_analyze():
    """
    Captures an image from webcam and analyzes the emotion
    
    Returns:
        String representing the detected emotion
    """
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return "neutral"
    
    # Create directory for saving images if it doesn't exist
    if not os.path.exists('captured_images'):
        os.makedirs('captured_images')
    
    print("Capturing image in 3 seconds...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    
    # Capture frame
    ret, frame = cap.read()
    
    # Release webcam
    cap.release()
    
    if not ret or frame is None:
        print("Error: Failed to capture image.")
        return "neutral"
    
    # Save the captured image
    timestamp = int(time.time())
    image_path = f"captured_images/capture_{timestamp}.jpg"
    cv2.imwrite(image_path, frame)
    
    print(f"Image saved to {image_path}")
    
    # Analyze the captured image
    emotion = analyze_emotion_from_image(image_path)
    
    return emotion

if __name__ == "__main__":
    # If the script is run directly, capture and analyze
    emotion = capture_and_analyze()
    print(f"Final detected emotion: {emotion}")