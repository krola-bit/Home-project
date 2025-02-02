import numpy as np
import librosa

def szur_hang(pcm_data, profile):
    """Egyéni zajszűrő modell a felhasználó hangja alapján."""
    mfcc = librosa.feature.mfcc(y=pcm_data.astype(np.float32), sr=16000, n_mfcc=13)
    
    # Profil eltéréseket kiszámoljuk
    diff = np.abs(np.mean(mfcc) - profile["mfcc_mean"])
    
    # Ha az eltérés túl nagy, elutasítjuk
    if diff > 20:
        return None  # Nem a felhasználó hangja
    
    return pcm_data  # Továbbküldjük feldolgozásra