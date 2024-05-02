from aiohttp import ClientSession
import json
import utils.utils
from utils.classes import Story
from utils.reddit import fetch_top_posts_in_subreddit, fetch_reddit_content
from utils.publishing import publish_and_delete_story
# setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')

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
            with open('index.txt', 'a') as file:
                file.write(story.new_hashed_title)
                file.write("\n")
            try:
                publish_and_delete_story(story)
            except:
                print(f"Unknown error while publishing story {story.title}")
                continue

generate()