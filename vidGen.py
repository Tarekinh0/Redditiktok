from aiohttp import ClientSession
import httpcore
import random
import shutil
from utils.text2mp3 import generate_tts_chunks
from utils.audio2srt import transcribe_audios
from utils.audiosrt2mp4 import generate_videos
from utils.reddit import replace_text, fetch_reddit_content
from utils.getText import translate_text, split_into_chunks
from utils.getImage import generate_main_images
from utils.srtGenerator import jsons_to_srts


setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')

def generate(gender, url):
    shutil.rmtree('./temp', ignore_errors=False, onerror=None)

    title, content = fetch_reddit_content(url)

    title, content = replace_text(title, content)

    title, content = translate_text(title, content)

    # title = title.replace('.', '')

    xmls, nb_of_chunks = split_into_chunks(title, content)

    image_paths = generate_main_images(title, nb_of_chunks);

    audio_paths = generate_tts_chunks(gender, xmls)

    sub_paths = transcribe_audios(audio_paths)

    srt_paths = jsons_to_srts(sub_paths)

    video_paths = generate_videos(title, audio_paths, image_paths, srt_paths)

    return video_paths
