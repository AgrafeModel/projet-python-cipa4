from elevenlabs.client import ElevenLabs
import tempfile
import os

elevenlabs = ElevenLabs(
    api_key="sk_fb21325049523b8b2cd89663ff9d9faf4d2811343225f912",
)

texte = """
Le village est silencieux...
La lune éclaire faiblement les rues vides...
Un hurlement retentit dans la forêt...
Les villageois se cachent, le souffle court...
Quelque chose rôde dans l’ombre...
"""

# Convert renvoie un générateur → on collecte tous les chunks
audio_bytes = b"".join(
    elevenlabs.text_to_speech.convert(
        text=texte,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )
)

# Sauvegarder dans un fichier temporaire
with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
    tmpfile.write(audio_bytes)
    tmpfile.flush()
    # Lecture directe sur Windows
    os.startfile(tmpfile.name)
