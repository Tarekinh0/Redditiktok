import httpcore
setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')
import xml.etree.ElementTree as ET
import boto3
import json

BUCKET_NAME = "tiktelegram-bucket"
DESTINATION_LANGUAGE = 'fr'

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def translate_text(title, text):
    
    comprehend = boto3.client('comprehend', region_name="eu-west-1", aws_access_key_id = config['aws']['key'], aws_secret_access_key = config['aws']['token'])
    response = comprehend.batch_detect_dominant_language(TextList=[title])
    source_language = response["ResultList"][0]["Languages"][0]["LanguageCode"]

    if source_language != DESTINATION_LANGUAGE:
        translate = boto3.client('translate', region_name="eu-west-1", aws_access_key_id = config['aws']['key'], aws_secret_access_key = config['aws']['token'])
        title = translate.translate_text(Text=title, SourceLanguageCode=source_language, TargetLanguageCode=DESTINATION_LANGUAGE )["TranslatedText"]
        text = translate.translate_text(Text=text, SourceLanguageCode=source_language, TargetLanguageCode=DESTINATION_LANGUAGE )["TranslatedText"]
    
    return title, text

#  deprecated
# from googletrans import Translator
# def translate_text(title, text):
#     translator = Translator(service_urls=['translate.googleapis.com'])
#     return translator.translate(title, src="en", dest='fr').text, translator.translate(text, dest='fr').text

def split_into_chunks(title, text, chunk_length=1000):
    """Splits text into chunks where each is roughly <= chunk_length characters, 
    trying not to split in the middle of a sentence."""
    sentences = text.split('. ')
    chunks = []
    current_chunk = ''

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_length:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + '. '
    chunks.append(current_chunk)  # Add the last chunk

    xmls = []
    for i in range(len(chunks)):

        speak = ET.Element("speak")
        intro = ET.SubElement(speak, "p").text = f"{title}, partie {i+1} sur {len(chunks)}!"
        content = ET.SubElement(speak, "p").text = chunks[i]

        if i == len(chunks)-1:
            outro = ET.SubElement(speak, "p").text = "Abonnez-vous pour d'autres histoires !"
        else:
            outro = ET.SubElement(speak, "p").text = f"Abonnez-vous pour la partie {i+2} !"
        xmls.append(speak)

    
    return xmls, len(chunks)
