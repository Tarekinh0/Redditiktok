import json
from utils.classes import Story, YoutubeArgs
import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import google.oauth2.credentials
import google_auth_oauthlib.flow

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

LANGUAGES = config["languages"]
YT_CLIENT_SECRETS_FILE = "client_secret.json"


def publish_and_delete_story(story):
    hashtags = story.language["platforms"]["hashtags"]
    for platform, platform_settings in story.language["platforms"].items():
        if platform == "instagram":
            publish_story_instagram(story, platform_settings, hashtags)
        if platform == "tiktok":
            publish_story_tiktok(story, platform_settings, hashtags)
        if platform == "youtube":
            publish_story_youtube(story, platform_settings, hashtags)
        if platform == "facebook":
            publish_story_facebook(story, platform_settings, hashtags)

    for file in story.hashed_video_paths:
       os.remove(file)
       
    del story




def publish_story_facebook(story, platform_settings, hashtags):
    settings = story.language["platforms"]["instagram"]
    print(f"{story.title} was succesfully published on Tiktok")


def publish_story_instagram(story, platform_settings, hashtags):
    settings = story.language["platforms"]["instagram"]
    print(f"{story.title} was succesfully published on Tiktok")

def publish_story_tiktok(story, platform_settings, hashtags):
    settings = story.language["platforms"]["tiktok"]
    print(f"{story.title} was succesfully published on Tiktok")


def publish_story_youtube(story, platform_settings, hashtags):
    with open(YT_CLIENT_SECRETS_FILE, 'w') as f:
        json.dump(platform_settings, f)

    yt_args = YoutubeArgs()

    for i, video in enumerate(story.hashed_video_paths, 1):
        yt_args.file += video
        yt_args.title += story.title + f"{i}/{len(story.hashed_video_paths)}"
        yt_args.description += story.title + hashtags
        # yt_args.category = "42"
        yt_args.keywords = "#Shorts, " + hashtags.replace(" ", ",")
        yt_args.privacyStatus = "public"
        
        youtube = get_authenticated_service(yt_args)

        try:
            initialize_upload(youtube, yt_args)
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))

        print(f"{story.title} was succesfully published on Youtube")

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(YT_CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message="MISSING_CLIENT_SECRETS")


  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)


  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(" ")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print("Video id '%s' was successfully uploaded." % response['id'])
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print(error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)

# story = Story()
# story.title = "Test Title"
# story.hashed_video_paths = ["generatedVideos/VideoPlayback.mp4"]

# hashtags = "#RedditContent #RedditTips #RedditHumor #ViralContent #ShortVideos #TrendingReddit #RedditDiscoveries #English #QuickVideo #WeirdReddit #RedditCommunity #CultureWeb #OnlineCommunity #RedditTrends #YouTubeShorts"
# platform_settings = ""
# publish_story_youtube(story=story, platform_settings=platform_settings, hashtags=hashtags)