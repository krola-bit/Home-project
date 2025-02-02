import pvporcupine
import pyaudio
import numpy as np
import webrtcvad
import time
import os
import json
import pyttsx3
import speech_recognition as sr
import librosa

# Konstansok
PROFILE_FILE = "audio_profiles.json"
INACTIVITY_TIMEOUT = 10  # Másodperc
SPEECH_END_TIMEOUT = 2  # Másodperc

# TTS inicializálása
tts_engine = pyttsx3.init()

def speak(text):
    """Szöveg felolvasása."""
    tts_engine.say(text)
    tts_engine.runAndWait()

# Beszédfelismerés inicializálása
recognizer = sr.Recognizer()

def listen():
    """Hangalapú válasz meghallgatása és feldolgozása."""
    with sr.Microphone() as source:
        print("Figyelek a válaszodra...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language="hu-HU")  # Magyar nyelv
            print(f"Felismert szöveg: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Nem értettem a választ.")
            speak("Elnézést, nem értettem. Kérlek, mondd újra.")
            return None
        except sr.RequestError as e:
            print(f"Hiba a beszédfelismerésben: {e}")
            return None

# Porcupine inicializálása
access_key = os.getenv("PORCUPINE_ACCESS_KEY")
if not access_key:
    raise ValueError("Hiányzik a Porcupine 'access_key'.")

porcupine = pvporcupine.create(
    access_key=access_key,
    keywords=["alexa", "computer"]
)

# WebRTC VAD inicializálása
vad = webrtcvad.Vad()
vad.set_mode(3)

pa = pyaudio.PyAudio()

audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

vad_frame_length = int(porcupine.sample_rate * 0.03)
vad_sample_rate = 16000

# Profilkezelés
def load_profiles():
    """Profilok betöltése."""
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as file:
            return json.load(file)
    return {}

def save_profiles(profiles):
    """Profilok mentése."""
    with open(PROFILE_FILE, "w") as file:
        json.dump(profiles, file, indent=4)

def analyze_audio(pcm_data, sample_rate=16000):
    """Hangprofil elemzése MFCC alapján."""
    if len(pcm_data) < 512:
        raise ValueError("Az audio adat túl rövid az elemzéshez.")
    mfccs = librosa.feature.mfcc(y=pcm_data.astype(float), sr=sample_rate, n_mfcc=13, n_fft=min(2048, len(pcm_data)))
    mfcc_mean = np.mean(mfccs, axis=1)  # Átlagérték az MFCC-kből
    mfcc_var = np.var(mfccs, axis=1)   # Szórás az MFCC-kből
    return {"mfcc_mean": mfcc_mean.tolist(), "mfcc_var": mfcc_var.tolist()}

def find_matching_profile(profile, profiles):
    """Profil keresése az adatbázisban MFCC alapján."""
    for name, stored_profile in profiles.items():
        if "mfcc_mean" not in stored_profile or "mfcc_var" not in stored_profile:
            continue  # Ha a régi profilok nem tartalmazzák az új kulcsokat, kihagyjuk
        mfcc_mean_diff = np.abs(np.array(profile["mfcc_mean"]) - np.array(stored_profile["mfcc_mean"]))
        mfcc_var_diff = np.abs(np.array(profile["mfcc_var"]) - np.array(stored_profile["mfcc_var"]))
        if np.all(mfcc_mean_diff <= 0.5) and np.all(mfcc_var_diff <= 0.5):
            return name
    return None

# Állapotkezelés
is_awake = False
is_recording = False
current_user = "NAN"
last_speech_time = time.time()
profiles = load_profiles()
frames = []

print("Listening for wake words...")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = np.frombuffer(pcm, dtype=np.int16)

        # Ébresztő szó felismerése
        if not is_awake:
            result = porcupine.process(pcm)
            if result >= 0:
                print("Ébresztő szó felismerve!")
                speak("Ébresztő szó felismerve!")
                profile = analyze_audio(pcm)
                match = find_matching_profile(profile, profiles)

                if match:
                    current_user = match
                    speak(f"Miben segíthetek, {current_user}?")
                else:
                    speak("Nem ismertem fel a hangod. Szeretnéd, ha menteném a hangod?")
                    while True:
                        response = listen()
                        if response in ["igen", "nem"]:
                            break

                    if response == "igen":
                        speak("Hogy hívhatlak?")
                        while True:
                            name = listen()
                            if name:
                                profiles[name] = profile
                                save_profiles(profiles)
                                current_user = name
                                speak(f"Profil elmentve. Miben segíthetek, {current_user}?")
                                break
                    elif response == "nem":
                        speak("Elárulod a neved, vagy elmondod, mit szeretnél?")
                        while True:
                            name = listen()
                            if name:
                                if name in profiles:
                                    current_user = name
                                    speak(f"Üdv újra, {current_user}! Profilod betöltve. Miben segíthetek?")
                                else:
                                    speak("Nem ismertem fel a nevedhez tartozó profilt.")
                                    current_user = "NAN"
                                break
                        break
                is_awake = True

        # Beszéd figyelése
        if is_awake:
            vad_pcm = audio_stream.read(vad_frame_length, exception_on_overflow=False)
            vad_pcm = np.frombuffer(vad_pcm, dtype=np.int16)

            if vad.is_speech(vad_pcm.tobytes(), vad_sample_rate):
                print("Beszéd detektálva.")
                last_speech_time = time.time()
                if not is_recording:
                    frames = []
                    is_recording = True
                frames.append(vad_pcm.tobytes())
            elif is_recording and time.time() - last_speech_time > SPEECH_END_TIMEOUT:
                is_recording = False
                if frames:
                    pcm_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                    profile = analyze_audio(pcm_data)
                    profiles[current_user] = profile
                    save_profiles(profiles)
                    speak("A beszéd rögzítése kész.")

            if time.time() - last_speech_time > INACTIVITY_TIMEOUT:
                print("Visszatérés inaktív módba.")
                speak("Visszatérek inaktív módba.")
                is_awake = False

finally:
    audio_stream.close()
    pa.terminate()
    porcupine.delete()

