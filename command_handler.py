import os
from categorize import categorize_input  # Kategorizálás kérésre vagy vezérlésre
from speech_handler import listen  # Hangfelismeréshez szükséges

def handle_user_commands(user):
    """Figyelő mód, ahol a felhasználó kéréseit és utasításait dolgozza fel."""
    while True:
        print("Figyelek a kérésedre vagy utasításodra...")
        text = listen()  # A mikrofonból beolvasott szöveg
        if not text:
            continue  # Ha nem érkezett szöveg, újra figyel

        # Kategorizáljuk a bemenetet kérésre vagy utasításra
        category = categorize_input(text)
        print(f"Felismert kategória: {category}")

        if category == "Kérés":
            os.system(f'say "Megértettem a kérésedet, {user}."')
            # Itt feldolgozhatjuk a kérés logikáját
        elif category == "Vezérlés":
            os.system(f'say "Elvégzem az utasításod, {user}."')
            # Itt végrehajtjuk az utasításokat
        else:
            os.system('say "Nem értettem, kérlek mondd újra."')

        # Speciális utasítás: Kilépés a figyelő módból
        if "vissza" in text or "befejez" in text:
            os.system('say "Visszatérek az ébresztő szó figyeléséhez."')
            break  # Visszatérés az ébresztő szó figyeléséhez