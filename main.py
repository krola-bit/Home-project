from wake_word_detector import WakeWordDetector
from audio_filter import szur_hang
from ai_processor import ertelmez_parancs
from mqtt_handler import kuld_home_assistant
from speech_handler import listen

def main():
    detector = WakeWordDetector()

    while True:
        pcm_data = detector.wait_for_wake_word()
        
        # Zajszűrés és azonosítás
        szurt_hang = szur_hang(pcm_data, profile={"mfcc_mean": 20})
        if szurt_hang is None:
            print("Nem a felhasználó beszél, figyelmen kívül hagyva.")
            continue

        print("Figyelek a kérésedre vagy utasításodra...")
        szoveg = listen()
        if not szoveg:
            continue
        
        kategoria = ertelmez_parancs(szoveg)

        if kategoria == "Vezérlés":
            if "lámpa" in szoveg:
                kuld_home_assistant("home/lampa", "on")
                print("💡 Lámpa felkapcsolva")
            else:
                print("🔄 Parancsot nem ismerem")
        elif kategoria == "Kérés":
            print(f"🤖 AI válasz: {szoveg}")

if __name__ == "__main__":
    main()