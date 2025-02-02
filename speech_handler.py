import os
import speech_recognition as sr

# Beszédfelismerés inicializálása
recognizer = sr.Recognizer()

def listen():
    """Figyeli a mikrofont és visszatér a felismert szöveggel."""
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

def handle_commands_or_requests():
    """Folyamatosan figyeli a parancsokat vagy kéréseket az azonosítás után."""
    while True:
        os.system('say "Várok parancsra vagy kérésre. Mondd, mit szeretnél!"')
        user_input = listen()
        
        if not user_input:
            continue  # Ha nem érkezik bemenet, folytatja a várakozást
        
        # Parancsok vagy kérések kategorizálása
        if "kapcsold" in user_input or "indítsd" in user_input:
            os.system(f'say "Parancs észlelve: {user_input}"')
            print(f"Végrehajtandó parancs: {user_input}")
        elif "mennyi" in user_input or "hogyan" in user_input:
            os.system(f'say "Kérés észlelve: {user_input}"')
            print(f"Feldolgozandó kérés: {user_input}")
        elif "kilépés" in user_input:
            os.system('say "Kilépés a figyelő módból."')
            break  # Figyelőmód leállítása
        else:
            os.system(f'say "Nem értem, mit szeretnél: {user_input}"')