import praw
import re
import json
import praw.models
from bs4 import BeautifulSoup
from socket import socket
import utils.classes
import hashlib
import utils

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    
redditConfig = config['reddit']

reddit = praw.Reddit(client_id=redditConfig["client_id"],
                        client_secret=redditConfig["client_secret"],
                        user_agent=redditConfig["user_agent"])    

# def get_proxies():
#     proxy_link = "https://proxylist.geonode.com/api/proxy-list?limit=10&page=1&sort_by=country&sort_type=asc"
#     proxy_json = requests.get(proxy_link).json()
#     https_proxy = {}
#     proxy_ip = proxy_json["data"][0]["ip"]
#     proxy_port = proxy_json["data"][0]["port"]
#     https_proxy["https"]=f"https://{proxy_ip}:{proxy_port}"
#     return https_proxy

LANGUAGES = config["languages"]

def fetch_top_posts_in_subreddit(subreddit_string, number_of_stories_per_day_per_subreddit):
    subreddit = reddit.subreddit(subreddit_string)
    top_post = subreddit.top(time_filter="day", limit = number_of_stories_per_day_per_subreddit)
    stories = [utils.classes.Story()]
    for post in top_post:
        for language_code, language_details in LANGUAGES.items() :
            new_hashed_title = hashlib.md5(post.title.encode('utf-8')).hexdigest()+f"-{language_code}"
            is_already_done = utils.utils.check_if_is_already_done(new_hashed_title)
            if is_already_done:
                print(f"The story '{post.title}' was already done in the past.")
            else:
                story = utils.classes.Story(post.title, post.selftext, language_details, new_hashed_title)
                stories.append(story)
    return stories
        

def fetch_reddit_content(url):
    # Extract the post ID from the URL
    # Fetch the post using praw
    post_id = url.split('/')[-3]
    post = reddit.submission(id=post_id)
    for language_code, language_details in LANGUAGES.items() :
        new_hashed_title = hashlib.md5(post.title.encode('utf-8')).hexdigest()+f"-{language_code}"
        story = utils.classes.Story(post.title, post.selftext, language_details, new_hashed_title)

    return story

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
        r"\b/\b" : ""  
        # Add more replacements as needed
    }

    # Apply each replacement
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
        title = re.sub(pattern, replacement, title)
    
    return title, text


def gender_detector(title, content):
    text = title+content
    # Define the regex patterns for female and male relationships
    female_pattern = r"\bmy\s(?:[a-zA-Z]+\s)?(?:wife|fiancée|girlfriend)\b"
    male_pattern = r"\bmy\s(?:[a-zA-Z]+\s)?(?:husband|fiancé|boyfriend)\b"

    # Find all occurrences in the text
    female_matches = re.findall(female_pattern, text, re.IGNORECASE)
    male_matches = re.findall(male_pattern, text, re.IGNORECASE)

    # Determine the gender of the speaker based on the matches
    if len(female_matches) > len(male_matches):
        return "man"
    elif len(male_matches) > len(female_matches):
        return "Female"
    else:
        return "man"


# # DEPRECATED
# def scrape_reddit_post(url):

#     if "/comments/" in url:
#         post_id = url.split('/')[-3]
#     else:
#         url = requests.get(url).url
#         post_id = url.split('/')[-3]

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/88.0'
#     }
#     try:
#         get_proxies()
#         response = requests.get(url, headers=headers, proxies = get_proxies())
#         response.raise_for_status()  # Raises an HTTPError for bad responses

#         if "/comments/" in url:
#             post_id = url.split('/')[-3]
#         else:
#             url = response.url
#             post_id = url.split('/')[-3]
        
#         # Parse the content with BeautifulSoup
#         soup = BeautifulSoup(response.content, 'html.parser')
#         title = ''
#         content = ''
#         # Find the post title and content using the appropriate HTML selectors
#         # These selectors are based on Reddit’s current HTML layout and might need updating if the layout changes
#         for item in soup.find_all('h1'):
#             title = title + item.get_text(strip=True)
#         for item in soup.find_all('div', id=f't3_{post_id}-post-rtjson-content'): # id_=f't3_{post_id}-post-rtjson-content'
#             content = content + item.get_text(strip=True)
        
#         return title, content

#     except requests.RequestException as e:
#         print(f"Request failed: {e}")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    # url = 'https://www.reddit.com/r/cybersecurity/comments/1ccmx56/my_it_department_knows_all_our_passwords/'
    title, content = fetch_top_posts_in_subreddit("AITAH")
    print(f"Title: {title}\nContent: {content}")
