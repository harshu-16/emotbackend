# interaction.py
import pyttsx3

def interact_based_on_emotion(emotion):
    engine = pyttsx3.init()

    # Set properties
    engine.setProperty('rate', 150)     # speed of speech (default: 200)
    engine.setProperty('volume', 1.0)   # max volume (0.0 to 1.0)

    # Optional: Set voice to female (if available)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "female" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

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
    print("Assistant says:", message)
    engine.say(message)
    engine.runAndWait()
