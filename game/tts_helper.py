# tts_helper.py
from elevenlabs.client import ElevenLabs
import tempfile
import pygame
import threading
import time
from queue import Queue
import os
import audio_config

pygame.mixer.init()

elevenlabs = ElevenLabs(api_key="sk_5a815614c98dc05c14d6a4a117c5728dd15d5eab51b14a2f")

# Queue pour générer les audios (asynchrone)
audio_generation_queue = Queue()
# Liste des audios prêts à être joués
audio_ready_list = []
generation_lock = threading.Lock()

script_dir = os.path.dirname(__file__)
sound_path = os.path.join(script_dir, "audio", "voix.mp3")

APP = None  # variable globale interne

def init(app):
    global APP
    APP = app

def _tts_worker():
    """Thread qui génère les fichiers audio en arrière-plan"""
    while True:
        text, voice_id = audio_generation_queue.get()
        if text is None:
            break  # signal d'arrêt

        try:
            # Génération TTS
            audio_bytes = b"".join(
                elevenlabs.text_to_speech.convert(
                    text=text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
            )

            # Sauvegarde temporaire
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
                tmpfile.write(audio_bytes)
                tmpfile.flush()
                mp3_path = tmpfile.name

            # Ajouter à la liste des audios prêts
            with generation_lock:
                audio_ready_list.append(mp3_path)

        except Exception as e:
            print("Erreur génération TTS :", e)

        audio_generation_queue.task_done()


# Thread dédié à la lecture des audios
def _audio_player_worker():
    """Joue les audios dès qu'ils sont prêts, séquentiellement"""
    while True:
        mp3_path = None
        with generation_lock:
            if audio_ready_list:
                mp3_path = audio_ready_list.pop(0)

        if mp3_path:
            try:
                # Créer le Sound à partir du fichier
                sound = pygame.mixer.Sound(mp3_path)

                sound.set_volume(audio_config.voice_volume)

                # Jouer le sound
                channel = sound.play()

                # Attendre que le sound se termine
                while channel.get_busy():
                    time.sleep(0.01)

            except Exception as e:
                print("Erreur lecture audio :", e)

        else:
            time.sleep(0.05)  # petit délai pour éviter boucle trop rapide


# Lancer les threads
threading.Thread(target=_tts_worker, daemon=True).start()
threading.Thread(target=_audio_player_worker, daemon=True).start()


def speak_text(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"):
    """Ajoute un texte à la queue pour génération TTS"""
    audio_generation_queue.put((text, voice_id))