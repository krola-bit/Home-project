import openai

openai.api_key = "SAJÁT_OPENAI_KULCS"

def ertelmez_parancs(szoveg):
    """Az AI értelmezi a szöveget és eldönti, hogy kérés vagy vezérlés."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Te egy magyar nyelvű hangalapú asszisztens vagy. Mondd meg, hogy az alábbi mondat KÉRÉS vagy VEZÉRLÉS!"},
            {"role": "user", "content": f"A mondat: '{szoveg}'"}
        ]
    )
    
    return response["choices"][0]["message"]["content"]