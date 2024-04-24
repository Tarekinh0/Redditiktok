import os
from google.cloud import texttospeech

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'sa-text-to-speech-key.json'

def list_voices():
    """Lists the available voices."""

    client = texttospeech.TextToSpeechClient()

    # Performs the list voices request
    voices = client.list_voices()

    for voice in voices.voices:
        for language_code in voice.language_codes:
            if language_code == "fr-FR":
                # Display the voice's name. Example: tpc-vocoded
                print(f"Name: {voice.name}")
                print(f"Supported language: {language_code}")

                # Display the supported language codes for this voice. Example: "en-US"

                ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)

                # Display the SSML Voice Gender
                print(f"SSML Voice Gender: {ssml_gender.name}")

                # Display the natural sample rate hertz for this voice. Example: 24000
                print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")

list_voices()