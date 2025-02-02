import spacy

# Betöltjük a magyar nyelvi modellt
nlp = spacy.load("hu_core_news_lg")

def categorize_input(text):
    """Eldönti, hogy a szöveg kérés vagy vezérlés."""
    doc = nlp(text.lower())  # Tokenizálás és kisbetűsítés

    # Egyszerű kulcsszavas módszer
    request_keywords = ["mennyi", "mi", "hogyan", "mutasd", "tudsz"]
    command_keywords = ["kapcsold", "indítsd", "nyisd", "zárd", "állítsd"]

    # Keresünk egyezést
    for token in doc:
        if token.text in request_keywords:
            return "Kérés"
        if token.text in command_keywords:
            return "Vezérlés"

    return "Ismeretlen"

# Teszt
if __name__ == "__main__":
    print(categorize_input("Kapcsold fel a lámpát!"))  # Vezérlés
    print(categorize_input("Mennyi az idő?"))  # Kérés
    print(categorize_input("Indítsd el a zenét!"))  # Vezérlés
    print(categorize_input("Mi az időjárás?"))  # Kérés
