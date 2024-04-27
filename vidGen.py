from aiohttp import ClientSession
import httpcore
import random
import shutil, os
import json
import utils.utils
from utils.reddit import fetch_top_posts_in_subreddit
from utils.publishing import publish_and_delete_story
setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

LANGUAGES = config["languages"]

SUBREDDIT_NAMES = config["reddit"]["subreddits"]
NUMBER_OF_STROIES_PER_DAY_PER_SUBREDDIT = config["reddit"]["number_of_stories_per_day_per_subreddit"]


def generate():
    utils.utils.erase_temp_folder()
    for subreddit_string in SUBREDDIT_NAMES:
        stories = fetch_top_posts_in_subreddit(subreddit_string, NUMBER_OF_STROIES_PER_DAY_PER_SUBREDDIT)
        for story in stories:
            if story.is_already_done:
                continue
            else:
                with open('index.txt', 'a') as file:
                    file.write(story.new_hashed_title)
                publish_and_delete_story(story)

generate()