# tts_helper.py
from elevenlabs.client import ElevenLabs
import tempfile
import pygame
import threading
import time
from queue import Queue
import os
import audio_config

# -------------------------------------------------------------------
# Initialisation du mixer et du canal TTS
# -------------------------------------------------------------------
pygame.mixer.init()
audio_config.voice_channel = pygame.mixer.Channel(1)
audio_config.voice_channel.set_volume(audio_config.voice_volume)

# Client ElevenLabs
elevenlabs = ElevenLabs(api_key="sk_bdd154038f47224bf83993e05313dd3a3f7a44fb107f428b")

# -------------------------------------------------------------------
# Queue et lock pour la génération et lecture TTS
# -------------------------------------------------------------------
audio_generation_queue = Queue()      # textes à générer
audio_ready_list = []                 # fichiers audio prêts
generation_lock = threading.Lock()    # verrou pour accès thread-safe

APP = None  # variable globale pour référence à l'app


# -------------------------------------------------------------------
# Initialisation de l'app (optionnelle)
# -------------------------------------------------------------------
def init(app):
    global APP
    APP = app


# -------------------------------------------------------------------
# Thread de génération TTS
# -------------------------------------------------------------------
def _tts_worker():
    """Thread qui génère les fichiers audio en arrière-plan"""
    while True:
        text, voice_id = audio_generation_queue.get()
        if text is None:
            break  # signal d'arrêt

        try:
            # Génération TTS via ElevenLabs
            audio_bytes = b"".join(
                elevenlabs.text_to_speech.convert(
                    text=text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
            )

            # Sauvegarde dans un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
                tmpfile.write(audio_bytes)
                tmpfile.flush()
                mp3_path = tmpfile.name

            # Ajout à la liste des audios prêts (thread-safe)
            with generation_lock:
                audio_ready_list.append(mp3_path)

        except Exception as e:
            print("Erreur génération TTS :", e)

        audio_generation_queue.task_done()


# -------------------------------------------------------------------
# Thread de lecture audio
# -------------------------------------------------------------------
def _audio_player_worker():
    """Joue les audios dès qu'ils sont prêts, séquentiellement"""
    while True:
        mp3_path = None
        with generation_lock:
            if audio_ready_list:
                mp3_path = audio_ready_list.pop(0)

        if mp3_path:
            try:
                sound = pygame.mixer.Sound(mp3_path)
                audio_config.voice_channel.play(sound)
                audio_config.voice_channel.set_volume(audio_config.voice_volume)

                while audio_config.voice_channel.get_busy():
                    time.sleep(0.01)

            except Exception as e:
                print("Erreur lecture audio :", e)

        else:
            time.sleep(0.05)


# -------------------------------------------------------------------
# Lancer les threads
# -------------------------------------------------------------------
threading.Thread(target=_tts_worker, daemon=True).start()
threading.Thread(target=_audio_player_worker, daemon=True).start()


# -------------------------------------------------------------------
# Fonctions publiques
# -------------------------------------------------------------------
def speak_text(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"):
    """Ajoute un texte à la queue pour génération TTS"""
    audio_generation_queue.put((text, voice_id))


def stop_all_voices():
    """Stoppe tout audio en cours et vide la queue"""
    if audio_config.voice_channel:
        audio_config.voice_channel.stop()

    with generation_lock:
        audio_ready_list.clear()