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
# Mixer and TTS channel initialization
# -------------------------------------------------------------------
pygame.mixer.init()
audio_config.voice_channel = pygame.mixer.Channel(1)
audio_config.voice_channel.set_volume(audio_config.voice_volume)

# ElevenLabs Client
# NOTE: It is recommended to use an environment variable for the API key
elevenlabs = ElevenLabs(api_key="sk_824915de33371e1b74d7f1fced13c61c3cb962ef61a45bc2")

# -------------------------------------------------------------------
# Queue and lock for TTS generation and playback
# -------------------------------------------------------------------
audio_generation_queue = Queue()      # Texts waiting to be generated
audio_ready_list = []                 # Ready audio file paths
generation_lock = threading.Lock()    # Thread-safe lock for list access

APP = None  # Global variable for app reference


# -------------------------------------------------------------------
# App initialization (optional)
# -------------------------------------------------------------------
def init(app):
    global APP
    APP = app


# -------------------------------------------------------------------
# TTS Generation Thread
# -------------------------------------------------------------------
def _tts_worker():
    """Background thread that generates audio files"""
    while True:
        text, voice_id = audio_generation_queue.get()
        if text is None:
            break  # Stop signal

        try:
            # Generate TTS via ElevenLabs
            audio_bytes = b"".join(
                elevenlabs.text_to_speech.convert(
                    text=text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
            )

            # Save to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
                tmpfile.write(audio_bytes)
                tmpfile.flush()
                mp3_path = tmpfile.name

            # Add to the ready list (thread-safe)
            with generation_lock:
                audio_ready_list.append(mp3_path)

        except Exception as e:
            print("TTS generation error:", e)

        audio_generation_queue.task_done()


# -------------------------------------------------------------------
# Audio Playback Thread
# -------------------------------------------------------------------
def _audio_player_worker():
    """Plays audio files sequentially as soon as they are ready"""
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

                # Wait for playback to finish
                while audio_config.voice_channel.get_busy():
                    time.sleep(0.01)

            except Exception as e:
                print("Audio playback error:", e)

        else:
            time.sleep(0.05)


# -------------------------------------------------------------------
# Start threads
# -------------------------------------------------------------------
threading.Thread(target=_tts_worker, daemon=True).start()
threading.Thread(target=_audio_player_worker, daemon=True).start()


# -------------------------------------------------------------------
# Public functions
# -------------------------------------------------------------------
def speak_text(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"):
    """Adds text to the queue for TTS generation"""
    audio_generation_queue.put((text, voice_id))


def stop_all_voices():
    """Stops any currently playing audio and clears the queue"""
    if audio_config.voice_channel:
        audio_config.voice_channel.stop()

    with generation_lock:
        audio_ready_list.clear()