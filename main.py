import signal
import sys
import pvporcupine
import pyaudio
import numpy as np
import time
import os
import librosa
from audio_processing import analyze_audio, find_matching_profile
from profiles import load_profiles, save_profiles
import speech_recognition as sr

def resample_audio(audio_data, input_rate=48000, output_rate=16000, target_length=512):
    """Átméretezi az audio adatokat pontosan Porcupine által várt frame-méretre."""
    resampled = librosa.resample(audio_data.astype(np.float32), orig_sr=input_rate, target_sr=output_rate)
    resampled = np.round(resampled).astype(np.int16)
    if len(resampled) < target_length:
        resampled = np.pad(resampled, (0, target_length - len(resampled)), mode='constant')
    return resampled[:target_length]

# Globális változók
pa = None
audio_stream = None
porcupine = None

def signal_handler(sig, frame):
    print("\nA program leállítása...")
    global pa, audio_stream, porcupine
    if audio_stream:
        try:
            audio_stream.stop_stream()
            audio_stream.close()
        except Exception as e:
            print(f"Hiba az audio_stream lezárása közben: {e}")
    if pa:
        try:
            pa.terminate()
        except Exception as e:
            print(f"Hiba a pyaudio leállítása közben: {e}")
    if porcupine:
        try:
            porcupine.delete()
        except Exception as e:
            print(f"Hiba a porcupine törlése közben: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Beszédfelismerés inicializálása
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Figyelek a válaszodra...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language="hu-HU")
            print(f"Felismert szöveg: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Nem értettem a választ.")
            os.system('say "Elnézést, nem értettem. Kérlek, mondd újra."')
            return None
        except sr.WaitTimeoutError:
            print("Időtúllépés történt, nem kaptam választ.")
            os.system('say "Időtúllépés. Kérlek, válaszolj újra."')
            return None

def main():
    global pa, audio_stream, porcupine
    
    access_key = os.getenv("PORCUPINE_ACCESS_KEY")
    if not access_key:
        raise ValueError("Hiányzik a Porcupine 'access_key'. Állítsd be környezeti változóként!")
    
    profiles = load_profiles()
    porcupine = pvporcupine.create(
        access_key=access_key,
        keywords=["alexa", "computer"]
    )
    
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=48000,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=1024
    )
    audio_stream.start_stream()

    print("Figyelek az ébresztő szóra...")

    try:
        while True:
            try:
                pcm = audio_stream.read(1024, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)
                
                if 48000 != porcupine.sample_rate:
                    pcm = resample_audio(pcm, input_rate=48000, output_rate=porcupine.sample_rate)
                
                if len(pcm) != porcupine.frame_length:
                    print(f"HIBA: A Porcupine {porcupine.frame_length} hosszú frame-eket vár, de {len(pcm)} érkezett!")
                    continue
                
                result = porcupine.process(pcm)
                
                if result >= 0:
                    print("Ébresztő szó felismerve!")
                    os.system('say "Ébresztő szó felismerve!"')
                    
                    profile = analyze_audio(pcm)
                    match = find_matching_profile(profile, profiles)
                    weight = 0.7  # Az új minta súlya
                    
                    if match:
                        os.system(f'say "Üdv, {match}! Miben segíthetek?"')

                        # Hozzáadjuk az új mintát a meglévő profilhoz súlyozottan
                        current_profile = profiles.get(match, {})

                        for key in ["mfcc_mean", "mfcc_var"]:
                            if key in profile:
                                current_values = np.array(current_profile.get(key, []))
                                new_values = np.array(profile[key])
                                updated_values = (weight * new_values + (1 - weight) * current_values)
                                current_profile[key] = updated_values.tolist()
                        profiles[match] = current_profile
                        save_profiles(profiles)
                        print(f"A {match} profil frissítve az ébresztő szó hangminta alapján.")
                    else:
                        os.system('say "Nem ismerlek. Szeretnéd, ha menteném a hangod?"')
                        response = listen()
                        if response == "igen":
                            os.system('say "Hogy hívhatlak?"')
                            name = listen()
                            if name:
                                profiles[name] = profile
                                save_profiles(profiles)
                                os.system(f'say "Profil elmentve. Miben segíthetek, {name}?"')
                        elif response == "nem":
                            os.system('say "Elárulod a neved, vagy elmondod, mit szeretnél?"')
                            name = listen()
                            if name in profiles:
                                os.system(f'say "Üdv újra, {name}!"')
                                
                                current_profile = profiles[name]
                                for key in ["mfcc_mean", "mfcc_var"]:
                                    if key in profile:
                                        current_values = np.array(current_profile[key])
                                        new_values = np.array(profile[key])
                                        updated_values = (weight * new_values + (1 - weight) * current_values)
                                        current_profile[key] = updated_values.tolist()
                                profiles[name] = current_profile
                                save_profiles(profiles)
            except Exception as e:
                print(f"Hiba történt a feldolgozás során: {e}")
    
    finally:
        if audio_stream:
            try:
                audio_stream.close()
            except Exception as e:
                print(f"Hiba az audio_stream lezárása közben: {e}")
        if pa:
            try:
                pa.terminate()
            except Exception as e:
                print(f"Hiba a pyaudio leállítása közben: {e}")
        if porcupine:
            try:
                porcupine.delete()
            except Exception as e:
                print(f"Hiba a porcupine törlése közben: {e}")

if __name__ == "__main__":
    main()
