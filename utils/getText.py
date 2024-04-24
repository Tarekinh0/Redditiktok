import httpcore
setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')

from googletrans import Translator
import xml.etree.ElementTree as ET




def translate_text(title, text):
    translator = Translator(service_urls=['translate.googleapis.com'])
    return translator.translate(title, src="en", dest='fr').text, translator.translate(text, dest='fr').text

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
