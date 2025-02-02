import os

def speak(text):
    """Szöveg felolvasása a macOS beépített szövegfelolvasójával."""
    os.system(f'say "{text}"')