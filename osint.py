import requests
from bs4 import BeautifulSoup
import tweepy
import whois
import json
import time
from dotenv import load_dotenv
import os

# بارگذاری متغیرهای محیطی
load_dotenv()

# Twitter API credentials (replace with your actual keys)
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

def twitter_auth():
    """Authenticate with Twitter API."""
    try:
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        return api
    except Exception as e:
        print(f"Twitter authentication failed: {e}")
        return None

def search_google(name):
    """Search Google for a name and return the top results."""
    url = f"https://www.google.com/search?q={name}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('h3')
        return [result.text for result in results[:5]]  # Limit to top 5 results
    except Exception as e:
        print(f"Google search failed: {e}")
        return []

def search_twitter(api, name):
    """Search Twitter for recent tweets related to a name."""
    if not api:
        return []
    try:
        tweets = api.search(q=name, count=10, lang='en')
        return [tweet.text for tweet in tweets]
    except Exception as e:
        print(f"Twitter search failed: {e}")
        return []

def get_whois_info(domain):
    """Fetch WHOIS information for a given domain."""
    try:
        domain_info = whois.whois(domain)
        return domain_info
    except Exception as e:
        print(f"WHOIS lookup failed for {domain}: {e}")
        return None

def search_people_engines(name):
    """Search multiple people search engines for information."""
    urls = [
        f"https://www.pipl.com/search/?q={name}",
        f"https://thatsthem.com/name/{name.replace(' ', '%20')}"
    ]
    results = {}
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            results[url] = soup.title.text if soup.title else "No title found"
        except Exception as e:
            results[url] = f"Error fetching data: {e}"
    return results

def search_facebook(name):
    """Search Facebook for profiles related to a name."""
    url = f"https://www.facebook.com/public/{name.replace(' ', '-')}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        profiles = [link['href'] for link in soup.find_all('a', href=True) if 'profile.php' in link['href']]
        return profiles
    except Exception as e:
        print(f"Facebook search failed: {e}")
        return []

def format_output(name, google_results, twitter_results, whois_info, people_search_results, facebook_profiles):
    """Format the search results into a readable structure."""
    output = {
        "Name Searched": name,
        "Google Results": google_results,
        "Twitter Posts": twitter_results,
        "WHOIS Info": whois_info,
        "People Search Engines": people_search_results,
        "Facebook Profiles": facebook_profiles
    }
    return json.dumps(output, indent=4)

def main():
    name = input("Enter the name to search: ")
    domain = input("Enter a domain to look up (or leave blank to skip): ") or None
    
    # Authenticate Twitter
    twitter_api = twitter_auth()
    
    # Collect data from each source
    print("\nStarting searches...")
    
    google_results = search_google(name)
    twitter_results = search_twitter(twitter_api, name)
    
    whois_info = get_whois_info(domain) if domain else None

    people_search_results = search_people_engines(name)
    facebook_profiles = search_facebook(name)
    
    # Format and print output
    formatted_output = format_output(name, google_results, twitter_results, whois_info, people_search_results, facebook_profiles)
    print("\nSearch Results:")
    print(formatted_output)

# Run the code
if __name__ == "__main__":
    main()
