# game/tts_helper.py
from __future__ import annotations

import re
import tempfile
import pygame
import threading
import time
from queue import Queue
from typing import Optional, TYPE_CHECKING

import audio_config
import game.constants

# Note : This module handles text-to-speech generation and playback using ElevenLabs API and pygame mixer.
# It runs two background threads: one for generating audio from text, and another for playing the
if TYPE_CHECKING:
    from elevenlabs.client import ElevenLabs as ElevenLabsClient
else:
    ElevenLabsClient = None

try:
    from elevenlabs.client import ElevenLabs
except Exception:
    ElevenLabs = None

# Music setup (pygame mixer)
pygame.mixer.init()
audio_config.voice_channel = pygame.mixer.Channel(1)
audio_config.voice_channel.set_volume(audio_config.voice_volume)

# Global state for TTS management
_ENABLED = True
_LAST_TTS_ERROR: Optional[str] = None
_client: Optional["ElevenLabsClient"] = None

audio_generation_queue = Queue()
audio_ready_list = []
generation_lock = threading.Lock()

# Helper function to ensure we have a valid ElevenLabs client instance
def _ensure_client():
    global _client
    if not _ENABLED:
        return None
    if _client is not None:
        return _client
    if ElevenLabs is None:
        return None

    key = getattr(game.constants, "ELEVENLABS_API_KEY", "")
    if not key or "TON_API_KEY" in key:
        return None

    try:
        _client = ElevenLabs(api_key=key)
        return _client
    except Exception:
        _client = None
        return None

# Public API for TTS management
def set_enabled(value: bool):
    global _ENABLED
    _ENABLED = bool(value)

    if not _ENABLED:
        disable_and_stop()

# Public function to update the ElevenLabs API key at runtime
def set_api_key(new_key: str):
    # update constant + reset client
    game.constants.ELEVENLABS_API_KEY = new_key
    global _client
    _client = None

# Last error
def pop_last_error() -> Optional[str]:
    global _LAST_TTS_ERROR
    err = _LAST_TTS_ERROR
    _LAST_TTS_ERROR = None
    return err

def _is_tts_key_or_quota_error(msg: str) -> bool:
    m = msg.lower()
    # Search an error
    return (
        "unauthorized" in m
        or "forbidden" in m
        or "invalid_api_key" in m
        or "api key" in m and "invalid" in m
        or "quota" in m
        or "insufficient" in m
        or "payment" in m
        or "402" in m
        or "401" in m
        or "403" in m
        or "too many requests" in m
        or "429" in m
        or "reported as leaked" in m
    )

# Validates the provided API key by attempting to create a client and fetch voices
def validate_api_key(api_key: str) -> bool:
    api_key = (api_key or "").strip()
    if len(api_key) < 10:
        return False

    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=api_key)

        # Get a voice
        voices = client.voices.get_all()
        if not voices or not getattr(voices, "voices", None) or len(voices.voices) == 0:
            return False

        voice_id = voices.voices[0].voice_id

        # Speaker
        text = "Bienvenue dans le monde du Loup Garou"
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
        )

        for _ in audio:
            break

        return True

    except Exception as e:
        # quota/leak/key : invalid
        msg = str(e)
        return False


# Background worker for TTS generation: listens to the queue, generates audio, and stores ready files
def _tts_worker():
    while True:
        text, voice_id = audio_generation_queue.get()
        if text is None:
            break

        client = _ensure_client()
        if client is None:
            # TTS is not available, skip processing but mark task as done to prevent blocking
            audio_generation_queue.task_done()
            continue

        try:
            audio_bytes = b"".join(
                client.text_to_speech.convert(
                    text=text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
            )

            # Save the audio to a temporary file and add its path to the ready list
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
                tmpfile.write(audio_bytes)
                tmpfile.flush()
                mp3_path = tmpfile.name

            with generation_lock:
                audio_ready_list.append(mp3_path)

        # Handle any exceptions during TTS generation gracefully
        except Exception as e:
            print("TTS generation error:", e)

            global _LAST_TTS_ERROR
            msg = str(e)

            if _is_tts_key_or_quota_error(msg):
                _LAST_TTS_ERROR = "Clé API du TTS n'est plus valide, nombre de tokens insuffisant."
                set_enabled(False)

        audio_generation_queue.task_done()

# Background worker for audio playback: checks for ready audio files and plays them sequentially
def _audio_player_worker():
    while True:
        mp3_path = None
        with generation_lock:
            if audio_ready_list:
                mp3_path = audio_ready_list.pop(0)

        if mp3_path and audio_config.voice_channel:
            try:
                sound = pygame.mixer.Sound(mp3_path)
                audio_config.voice_channel.play(sound)
                audio_config.voice_channel.set_volume(audio_config.voice_volume)
                while audio_config.voice_channel.get_busy():
                    time.sleep(0.01)
            except Exception as e:
                print("Audio playback error:", e)
        else:
            time.sleep(0.05)

# Start the background threads for TTS generation and audio playback
threading.Thread(target=_tts_worker, daemon=True).start()
threading.Thread(target=_audio_player_worker, daemon=True).start()


# Public function to speak text using TTS: enqueues the text and voice ID for processing
def speak_text(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"):
    if not _ENABLED:
        return
    if _ensure_client() is None:
        return

    audio_generation_queue.put((text, voice_id))


# Public function to stop all currently playing voices and clear pending audio
def stop_all_voices():
    if audio_config.voice_channel:
        audio_config.voice_channel.stop()
    with generation_lock:
        audio_ready_list.clear()

# Public function to disable TTS functionality and stop any ongoing audio
def disable_and_stop():
    global _ENABLED
    _ENABLED = False

    # Stop current audio
    if audio_config.voice_channel:
        audio_config.voice_channel.stop()

    # Clear pending audio
    with generation_lock:
        audio_ready_list.clear()

    # Clear generation queue
    while not audio_generation_queue.empty():
        try:
            audio_generation_queue.get_nowait()
            audio_generation_queue.task_done()
        except Exception:
            break