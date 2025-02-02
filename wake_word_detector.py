import os
import pvporcupine
import pyaudio
import numpy as np
import librosa

def resample_audio(audio_data, input_rate=48000, output_rate=16000, target_length=512):
    """Átméretezi az audio adatokat pontosan Porcupine által várt frame-méretre."""
    resampled = librosa.resample(audio_data.astype(np.float32), orig_sr=input_rate, target_sr=output_rate)
    resampled = np.round(resampled).astype(np.int16)
    if len(resampled) < target_length:
        resampled = np.pad(resampled, (0, target_length - len(resampled)), mode='constant')
    return resampled[:target_length]

class WakeWordDetector:
    """Ébresztő szó felismerő, amely addig figyel, amíg a szót nem észleli."""
    
    def __init__(self, access_key):
        self.access_key = access_key
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self._initialize_porcupine()
    
    def _initialize_porcupine(self):
        """Inicializálja a Porcupine ébresztőszó felismerőt."""
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keywords=["alexa", "computer"]
        )

        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=48000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=1024
        )
        self.audio_stream.start_stream()

    def wait_for_wake_word(self):
        """Folyamatosan figyel, amíg az ébresztő szót nem érzékeli."""
        print("Figyelek az ébresztő szóra...")

        while True:
            try:
                pcm = self.audio_stream.read(1024, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)

                if 48000 != self.porcupine.sample_rate:
                    pcm = resample_audio(pcm, input_rate=48000, output_rate=self.porcupine.sample_rate)

                if len(pcm) != self.porcupine.frame_length:
                    print(f"HIBA: A Porcupine {self.porcupine.frame_length} hosszú frame-eket vár, de {len(pcm)} érkezett!")
                    continue

                result = self.porcupine.process(pcm)

                if result >= 0:
                    print("Ébresztő szó felismerve!")
                    os.system('say "Ébresztő szó felismerve!"')
                    return pcm  # Visszatér a PCM adatokkal
            except Exception as e:
                print(f"Hiba történt a felismerés során: {e}")

    def cleanup(self):
        """Erőforrások felszabadítása a program leállításakor."""
        if self.audio_stream:
            try:
                self.audio_stream.close()
            except Exception as e:
                print(f"Hiba az audio_stream lezárása közben: {e}")
        if self.pa:
            try:
                self.pa.terminate()
            except Exception as e:
                print(f"Hiba a pyaudio leállítása közben: {e}")
        if self.porcupine:
            try:
                self.porcupine.delete()
            except Exception as e:
                print(f"Hiba a porcupine törlése közben: {e}")