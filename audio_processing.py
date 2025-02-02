import librosa
import numpy as np

def analyze_audio(pcm_data, sample_rate=16000):
    """Hangprofil elemzése MFCC alapján."""
    if len(pcm_data) < 512:
        raise ValueError("Az audio adat túl rövid az elemzéshez.")
    mfccs = librosa.feature.mfcc(y=pcm_data.astype(float), sr=sample_rate, n_fft = max(512, min(2048, len(pcm_data))))
    mfcc_mean = np.mean(mfccs, axis=1)  # Átlagérték az MFCC-kből
    mfcc_var = np.var(mfccs, axis=1)   # Szórás az MFCC-kből
    return {"mfcc_mean": mfcc_mean.tolist(), "mfcc_var": mfcc_var.tolist()}

# Kezdeti toleranciaértékek
mean_tolerance = 12.0
var_tolerance = 1000.0
hiba_szamlalo = 0  # Hány sikertelen felismerés történt?

def find_matching_profile(profile, profiles):
    global mean_tolerance, var_tolerance, hiba_szamlalo  # Globálisan követjük az értékeket
    for name, stored_profile in profiles.items():
        if "mfcc_mean" not in stored_profile or "mfcc_var" not in stored_profile:
            continue
        mfcc_mean_diff = np.abs(np.array(profile["mfcc_mean"]) - np.array(stored_profile["mfcc_mean"]))
        mfcc_var_diff = np.abs(np.array(profile["mfcc_var"]) - np.array(stored_profile["mfcc_var"]))
        
        mean_diff_avg = np.mean(mfcc_mean_diff)
        var_diff_avg = np.mean(mfcc_var_diff)

        print(f"Profil ellenőrzése: {name}")
        print(f"🔍 Átlagos mfcc_mean eltérés: {mean_diff_avg}, Átlagos mfcc_var eltérés: {var_diff_avg}")

        if mean_diff_avg <= mean_tolerance and var_diff_avg <= var_tolerance:
            print("✅ Profil sikeresen beazonosítva.")
            hiba_szamlalo = 0  # Ha sikeres azonosítás történt, lenullázzuk a számlálót
            return name
    
    # Ha nem volt találat, növeljük a toleranciát 3 sikertelen próbálkozás után
    hiba_szamlalo += 1
    if hiba_szamlalo >= 3:
        mean_tolerance += 1.0  # Finomhangolás
        var_tolerance += 200.0
        print(f"⚠️ Tolerancia növelve: mean_tolerance={mean_tolerance}, var_tolerance={var_tolerance}")
        hiba_szamlalo = 0  # Visszaállítjuk a számlálót
    
    return None
