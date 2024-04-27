from google.cloud import texttospeech
import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import json
import xml.etree.ElementTree as ET
import sys
from tempfile import gettempdir


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "sa-text-to-speech-key.json"


# ttsClient = texttospeech.TextToSpeechClient()

def generate_tts_chunks(language, gender, xmls):

    """Generates TTS for each chunk and saves to separate MP3 files."""
    paths = []


    for i, xml in enumerate(xmls):
        # path = old_generate_wav(i, chunk, voice)
        path = aws_generate_wav(language, i, xml, gender)
        paths.append(path)
    return paths


# deprecated, the second variable (content) is now an xml elementTree, not a text string
# def old_generate_wav(i, content, gender):

#     if gender == "man":
#         voice = "fr-FR-Neural2-D"
#     else:
#         voice = "fr-FR-Neural2-E"	

#     synthesisInput = texttospeech.SynthesisInput(text=content)

#     voice = texttospeech.VoiceSelectionParams(language_code = "fr-FR", name=voice)

#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.MP3,
#         speaking_rate = 1.1,
#         pitch = 0.9,
#     )

#     response = ttsClient.synthesize_speech(
#         input = synthesisInput,
#         voice = voice,
#         audio_config=audio_config
#     )
#     path = f"./temp/part{i}.mp3"
#     with open(path, "wb") as output:
#         output.write(response.audio_content)
#         print(f"Audio file written to {path}")

#     return path



def aws_generate_wav(language, i, content, gender):

    if gender == "man":
        voice = language["male_voice"]
    else:
        voice = language["female_voice"]
    


    content = ET.tostring(content, encoding="ASCII").decode("ASCII")

    polly = boto3.Session(region_name = "eu-west-1", 
                         aws_access_key_id = config['aws']['key'], aws_secret_access_key = config['aws']['token']).client('polly')    
    try :
        response = polly.synthesize_speech(Engine="neural", SampleRate = "24000", Text=content, OutputFormat="mp3", VoiceId=voice, TextType = "ssml")
    
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    path = f"./temp/audio{i}.mp3"
    # Access the audio stream from the response
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            data = stream.read()
            fo = open(path, "wb")
            fo.write( data )
            fo.close()

    return path
