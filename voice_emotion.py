import speech_recognition as sr

def keyword_based_analysis(text):
    """
    Simple keyword-based emotion detection

    Args:
        text: Transcribed text to analyze

    Returns:
        String representing the detected emotion
    """
    emotion_keywords = {
        "happy": ["happy", "glad", "joy", "excited", "great", "wonderful", "fantastic", "awesome"],
        "sad": ["sad", "depressed", "upset", "down", "unhappy", "miserable", "disappointed"],
        "angry": ["angry", "mad", "annoyed", "irritated", "furious", "hate", "frustrated"],
    }

    text_lower = text.lower()

    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return emotion

    return "neutral"

def analyze_audio_file(audio_path):
    """
    Transcribes and analyzes emotion from an audio file

    Args:
        audio_path: Path to the audio file

    Returns:
        Detected emotion based on keywords
    """
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(f"Transcribed text: {text}")

            emotion = keyword_based_analysis(text)
            print(f"Detected Emotion: {emotion}")
            return emotion

    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return "neutral"
    except sr.RequestError as e:
        print(f"Speech Recognition error: {e}")
        return "neutral"
    except Exception as e:
        print(f"Error processing the audio file: {e}")
        return "neutral"

if __name__ == "__main__":
    # Update this path with your actual audio file
    audio_file_path = r"C:\Users\John Paul\Desktop\codeflex\emoit\emoit\emoticare\temp\audio_sample.wav"
    analyze_audio_file(audio_file_path)
