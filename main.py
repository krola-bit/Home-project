import os
import sys
from wake_word_detector import WakeWordDetector  # Ébresztő szó figyelő
from user_authenticator import UserAuthenticator  # Azonosítási modul
from shutdown_handler import ShutdownHandler  # Leállítás kezelő
from command_handler import handle_user_commands  # Kérések és utasítások kezelése

# Globális változók
detector = None
authenticator = None
shutdown_handler = None  # Új leállítási kezelő objektum

def main():
    """A program belépési pontja."""
    global detector, authenticator, shutdown_handler
    access_key = os.getenv("PORCUPINE_ACCESS_KEY")
    if not access_key:
        raise ValueError("Hiányzik a Porcupine 'access_key'. Állítsd be környezeti változóként!")

    # Ébresztő szó és azonosítás kezelő objektumok inicializálása
    detector = WakeWordDetector(access_key)
    authenticator = UserAuthenticator()
    shutdown_handler = ShutdownHandler(detector, authenticator)  # Leállítás kezelő inicializálása

    while True:
        # Az ébresztő szóra várás, és PCM adatok visszaadása
        pcm_data = detector.wait_for_wake_word()  # 🚀 Vár az ébresztő szóra és PCM adatokat ad vissza

        # PCM adatok átadása az autentikációs modulnak
        user = authenticator.authenticate_user(pcm_data)  # 🔑 Felhasználó azonosítása

        if user:
            os.system(f'say "Mit szeretnél, {user}?"')
            # Itt lehetőség van további parancsok vagy kérések kezelésére
            handle_user_commands(user)  # ➡️ Átirányítás a kérések vagy utasítások kezelésére

if __name__ == "__main__":
    main()

