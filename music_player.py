import webbrowser
import random

# Tamil song collections based on mood
tamil_music = {
    "sad": [
        "https://youtu.be/EhhiY11Z9-U?si=Vfe1vr1xWSxnvxLV",  # Ennodu Nee Irundhaal
        "https://youtu.be/laoJjq7-WGQ?si=b1IQprBXC3d6HWbX",  # Kanmani Anbodu
        "https://youtu.be/fYkQzTAx3Yo?si=aP1QhVB72punJnYl",  # Neeyum Naanum
    ],
    "happy": [
        "https://youtu.be/fRD_3vJagxk?si=EfiIimaOZSNyshwN",  # Vaathi Coming
        "https://youtu.be/KUN5Uf9mObQ?si=1tW4ETDRyQHCxt8n",  # Arabic Kuthu
        "https://youtu.be/PhxfspwMdww?si=1F13ol5V8VQgkT7_",  # jollyo gymkhana
    ],
    "angry": [
        "https://youtu.be/0zz172zODiY?si=Ne0lwBzfaYtmAcYX",  # Surviva
        "https://youtu.be/y3tfpBxoci4?si=tMVYIeaE3ss7XWHc",  # Vikram - Wasted
        "https://youtu.be/WWr9086eWtY?si=n0l9eT9nhfFQ9d1i",  # Yaanji (Soothing to calm)
    ]
}

def play_music_based_on_emotion(emotion):
    if emotion in tamil_music:
        url = random.choice(tamil_music[emotion])
        print(f"🎵 Playing music for {emotion} mood: {url}")
        webbrowser.open(url)
    else:
        print("No music found for this emotion.")
