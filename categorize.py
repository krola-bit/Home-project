import spacy

# Betöltjük a magyar nyelvi modellt
nlp = spacy.load("hu_core_news_lg")

def categorize_input(text):
    """Eldönti, hogy a szöveg kérés vagy vezérlés."""
    doc = nlp(text.lower())  # Tokenizálás és lemmatizálás

    # Egyszerű kulcsszavas módszer
    request_keywords = ["mennyi", "mi", "hogyan", "mutasd", "tudsz"]
    command_keywords = ["kapcsold", "fel", "lámpa", "indítsd", "zárd", "állítsd"]

    # Tokenek vizsgálata
    lemmatized_tokens = [token.lemma_ for token in doc]
    print(f"Lemmatizált szavak: {lemmatized_tokens}")

    # Többszavas kifejezés vizsgálata
    if "kapcsold" in lemmatized_tokens and "lámpa" in lemmatized_tokens:
        return "Vezérlés"

    # Egyszavas keresések
    for lemma in lemmatized_tokens:
        if lemma in request_keywords:
            return "Kérés"
        if lemma in command_keywords:
            return "Vezérlés"

    return "Ismeretlen"

# Teszt
if __name__ == "__main__":
    print(categorize_input("Kapcsold fel a lámpát!"))  # Vezérlés
    print(categorize_input("Mennyi az idő?"))  # Kérés
    print(categorize_input("Indítsd el a zenét!"))  # Vezérlés
    print(categorize_input("Mi az időjárás?"))  # Kérés
