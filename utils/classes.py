import shutil, os, json
from utils.getText import translate_text, split_into_chunks
from utils.getImage import generate_main_images
from utils.srtGenerator import jsons_to_srts
from utils.text2mp3 import generate_tts_chunks
from utils.audio2srt import transcribe_audios
from utils.audiosrt2mp4 import generate_videos
import utils.reddit as reddit
from utils.utils import check_if_is_already_done


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

LANGUAGES = config["languages"]


class YoutubeArgs():
  title = ""
  file = ""
  description = "#Shorts #Short"
  category = ""
  privacyStatus = "public"
  keywords = "#Shorts #Short"
  logging_level = "INFO"
  noauth_local_webserver=True
  auth_host_name="localhost"
  

class Story:
  def __init__(self, *args):
    if len(args) == 0 :
       pass
    else:
      # title, content, language, new_hashed_title
      self.title = args[0]
      self.content = args[1]
      self.language = args[2]
      self.new_hashed_title = args[3]

      self.title, self.content = reddit.replace_text(self.title, self.content)

      self.is_already_done = check_if_is_already_done(self.new_hashed_title)

      self.gender = reddit.gender_detector(self.title, self.content)

      self.xmls, self.nb_of_chunks = split_into_chunks(self.title, self.content)

      self.title, self.content = translate_text(self.gender, self.language, self.title, self.content)

      self.image_paths = generate_main_images(self.title, self.nb_of_chunks)

      self.audio_paths = generate_tts_chunks(self.language, self.gender, self.xmls)

      self.sub_paths = transcribe_audios(self.audio_paths, self.language["language_code"])

      self.srt_paths = jsons_to_srts(self.sub_paths)

      self.video_paths = generate_videos(self.title, self.audio_paths, self.image_paths, self.srt_paths)

      self.hashed_video_paths = []

      for i, path in enumerate(self.video_paths):
          self.hashed_path = f'generatedVideos/{self.new_hashed_title}-partie{i+1}.mov'
          shutil.move(path, self.hashed_path)
          self.hashed_video_paths.append(self.hashed_path)
        