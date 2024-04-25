import praw
import re
import json
import requests
from bs4 import BeautifulSoup
from socket import socket

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    
redditConfig = config['reddit']

def get_proxies():
    proxy_link = "https://proxylist.geonode.com/api/proxy-list?limit=10&page=1&sort_by=country&sort_type=asc"
    proxy_json = requests.get(proxy_link).json()
    https_proxy = {}
    proxy_ip = proxy_json["data"][0]["ip"]
    proxy_port = proxy_json["data"][0]["port"]
    https_proxy["https"]=f"https://{proxy_ip}:{proxy_port}"
    return https_proxy

        

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
        url = requests.get(url).url
        post_id = url.split('/')[-3]
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

def scrape_reddit_post(url):

    if "/comments/" in url:
        post_id = url.split('/')[-3]
    else:
        url = requests.get(url).url
        post_id = url.split('/')[-3]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/88.0'
    }
    try:
        get_proxies()
        response = requests.get(url, headers=headers, proxies = get_proxies())
        response.raise_for_status()  # Raises an HTTPError for bad responses

        if "/comments/" in url:
            post_id = url.split('/')[-3]
        else:
            url = response.url
            post_id = url.split('/')[-3]
        
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        title = ''
        content = ''
        # Find the post title and content using the appropriate HTML selectors
        # These selectors are based on Reddit’s current HTML layout and might need updating if the layout changes
        for item in soup.find_all('h1'):
            title = title + item.get_text(strip=True)
        for item in soup.find_all('div', id=f't3_{post_id}-post-rtjson-content'): # id_=f't3_{post_id}-post-rtjson-content'
            content = content + item.get_text(strip=True)
        
        return title, content

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    url = 'https://www.reddit.com/r/cybersecurity/comments/1ccmx56/my_it_department_knows_all_our_passwords/'
    title, content = scrape_reddit_post(url)
    print(f"Title: {title}\nContent: {content}")
