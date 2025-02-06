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

def handle_new_user(self, profile):
    """Kezeli az új felhasználó azonosítását és esetleges mentését."""

    # 1️⃣ Első üzenet: A beazonosítás sikertelen, kérjük a nevet
    os.system('say "Nem ismerlek. Kérlek, mondd meg a neved!"')

    # 2️⃣ Név bekérése és ellenőrzése
    name = get_valid_name()  # 🔹 Csak akkor tér vissza, ha valódi nevet kapunk!

    # 3️⃣ Második körös azonosítás: összehasonlítás a mentett nevekkel
    if name in self.profiles:
        os.system(f'say "Üdv újra, {name}! Miben segíthetek?"')
        self.update_existing_profile(name, profile)
        return name  # 🔹 Sikeres azonosítás után kilépünk

    # 4️⃣ Ha a név nem szerepel a mentett profilok között: jelezzük, hogy nem sikerült
    os.system('say "Továbbra sem sikerült azonosítani. Szeretnéd, ha menteném a neved?"')
    response = listen()

    # 5️⃣ Ha igen, mentjük a profilt
    if response == "igen":
        self.profiles[name] = profile
        save_profiles(self.profiles)
        os.system(f'say "Profil elmentve. Miben segíthetek, {name}?"')
        return name

    # 6️⃣ Ha nem, továbblépünk
    os.system('say "Rendben. Miben segíthetek?"')
    return None  # 🔹 A felhasználót nem mentettük, de további kéréseket kezelhet

def get_valid_name():
    """Megkérdezi a felhasználót a nevéről, és ellenőrzi, hogy valódi név-e."""
    while True:
        name = listen()

        # Ellenőrizzük, hogy a válasz egy név-e (csak betűket tartalmazzon)
        if name and name.replace(" ", "").isalpha():
            return name  # 🔹 Érvényes név esetén visszatérünk

        # Ha nem volt felismerhető név, újra kérdezzük
        os.system('say "Nem értettem a neved. Kérlek, mondd el érthetően."')