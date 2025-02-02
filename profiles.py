import json
import os

PROFILE_FILE = "audio_profiles.json"

def load_profiles():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}

def save_profiles(profiles):
    """Profilok mentése ideiglenes fájlon keresztül, hibák elkerülése érdekében."""
    temp_file = PROFILE_FILE + ".tmp"
    try:
        with open(temp_file, "w") as file:
            json.dump(profiles, file, indent=4)
        os.replace(temp_file, PROFILE_FILE)
        print(f"🔹 JSON fájl sikeresen mentve: {PROFILE_FILE}")
    except Exception as e:
        print(f"Hiba történt a mentés során: {e}")