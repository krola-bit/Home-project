import signal
import sys

class ShutdownHandler:
    """A program biztonságos leállítását végző osztály."""

    def __init__(self, detector=None, authenticator=None):
        """Inicializálja a jelkezelőt és az erőforrásokat."""
        self.detector = detector
        self.authenticator = authenticator
        signal.signal(signal.SIGINT, self.signal_handler)  # CTRL + C jelkezelő regisztrálása

    def signal_handler(self, sig, frame):
        """Kezeli a SIGINT (CTRL + C) jelet, és biztonságosan leállítja a programot."""
        print("\nA program leállítása...")

        # Ébresztő szó felismerő bezárása
        if self.detector:
            self.detector.cleanup()

        # Jövőbeni bővítés: más erőforrások bezárása, ha szükséges
        if self.authenticator:
            print("Felhasználói azonosító modul bezárása...")

        sys.exit(0)  # Kilépés a programból