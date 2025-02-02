import os
import numpy as np
from audio_processing import analyze_audio, find_matching_profile
from profiles import load_profiles, save_profiles
from speech_handler import listen

class UserAuthenticator:
    """Felhasználó azonosítása és kezelése az ébresztő szó felismerése után."""

    def __init__(self):
        """Betölti a profilokat az indításkor."""
        self.profiles = load_profiles()
        self.weight = 0.7  # Az új hangminta súlya

    def authenticate_user(self, pcm_data):
        """Az ébresztő szó felismerése után azonosítja a felhasználót."""
        profile = analyze_audio(pcm_data)  # Hangprofil elemzés
        match = find_matching_profile(profile, self.profiles)

        if match:
            os.system(f'say "Üdv, {match}! Miben segíthetek?"')
            self.update_existing_profile(match, profile)
            return match  # Visszaadjuk a felhasználó nevét
        else:
            return self.handle_new_user(profile)

    def update_existing_profile(self, username, profile):
        """Frissíti a meglévő felhasználó profilját az új hangmintával."""
        current_profile = self.profiles.get(username, {})

        for key in ["mfcc_mean", "mfcc_var"]:
            if key in profile:
                current_values = np.array(current_profile.get(key, []))
                new_values = np.array(profile[key])
                updated_values = (self.weight * new_values + (1 - self.weight) * current_values)
                current_profile[key] = updated_values.tolist()
        
        self.profiles[username] = current_profile
        save_profiles(self.profiles)
        print(f"A {username} profil frissítve az új hangminta alapján.")

    def handle_new_user(self, profile):
        """Új felhasználót hoz létre, ha az azonosítás sikertelen."""
        os.system('say "Nem ismerlek. Szeretnéd, ha menteném a hangod?"')
        response = listen()

        if response == "igen":
            os.system('say "Hogy hívhatlak?"')
            name = listen()
            if name:
                self.profiles[name] = profile
                save_profiles(self.profiles)
                os.system(f'say "Profil elmentve. Miben segíthetek, {name}?"')
                return name
        elif response == "nem":
            os.system('say "Elárulod a neved, vagy elmondod, mit szeretnél?"')
            name = listen()
            if name in self.profiles:
                os.system(f'say "Üdv újra, {name}!"')
                self.update_existing_profile(name, profile)
                return name

        return None  # Ha nincs azonosított vagy új felhasználó, None-t ad vissza.