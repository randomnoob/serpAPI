import requests
import itertools
from config import API_KEYS

API_KEYS = [
    "a417c75840f5b0aabab2ffdf6f0ee103e072bad3a9182c0fef468cf534772362",
    "868547210328e6b4e89af777029200c2c8a5e40f388124ffd1eadc0a704b3684",
]

# Create a cycle iterator for round-robin API key usage
api_key_cycle = itertools.cycle(API_KEYS)


def make_request(domain, api_key):
    endpoint = "https://serpapi.com/search.json"
    params = {
        "engine":"google",
        "location":"Austin,+Texas,+United+States",
        "hl":"en",
        "gl":"us",
        "google_domain":"google.com",
        "q": domain,
        "apikey": api_key,
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json(), None
    else:
        return None, response.status_code

def get_serp(domain):
    retries = 3
    for _ in range(retries):
        api_key = next(api_key_cycle)
        data, error = make_request(domain, api_key)
        if data:
            # Assuming the SERP data you need is in the response JSON under 'serp_data'
            # Adjust according to the actual response structure
            return data.get('serp_data', 'No SERP data available')
        else:
            print(f"Error fetching SERP data with key {api_key}: {error}")
    return "Error fetching SERP data after multiple retries"