import praw
import re
import json


config = json.load(open("config.json"))
redditConfig = config['reddit']


def fetch_reddit_content(url):

    reddit = praw.Reddit(client_id=redditConfig["client_id"],
                        client_secret=redditConfig["client_secret"],
                        user_agent=redditConfig["user_agent"])    
    # Extract the post ID from the URL
    # Fetch the post using praw
    if "/comments/" in url:
        post_id = url.split('/')[-3]
        post = reddit.submission(id=post_id)
    else:
        post_id = url.split('/')[-1]
        post = reddit.submission(id=post_id)
    
    # Return the post's title and selftext
    return post.title, post.selftext

def replace_text(title, text):
    # Dictionary of patterns and their replacements
    replacements = {
        r"\bAITA\b": "Am I an Asshole",
        r"\btw\b": "Warning ! contains: ",
        r"\bAITAH\b": "Am I an Asshole",
        r"\bWIBTA\b": "Would I be an Asshole",
        r"\bWIBTAH\b": "Would I be an Asshole",
        r"(\d+)(M|m)\b": r"\1 Man",
        r"(\d+)(F|f)\b": r"\1 Woman",
        r"\bNTA\b": "Not an Asshole",
        r"\bYTA\b": "You're an Asshole",
        r"\bESH\b": "Everyone Sucks Here",
        r"\bNAH\b": "No Assholes Here",
        r"\bINFO\b": "Information",
        r"\bOP\b": "Original Poster",   
        # Add more replacements as needed
    }

    # Apply each replacement
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
        title = re.sub(pattern, replacement, title)
    
    return title, text
