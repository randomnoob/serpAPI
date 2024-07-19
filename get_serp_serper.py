import requests
import json
import itertools
from config import SERPER_API_KEY

api_keys = [SERPER_API_KEY, "f2262d553f5691749a5420e2a5d3a2b36c84aa62",
            "dd89053d2e8cc63b76bef11f70a31f2d09b50252"]
api_key_cycle = itertools.cycle(api_keys)

def make_request(query, api_key, **kwargs):
    endpoint = "https://google.serper.dev/search"
    options = {
            "q": query,
            }
    options.update(kwargs)
    payload = json.dumps(options)
    headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
            }

    response = requests.post(endpoint, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json(), None
    else:
        return None, response.status_code

def get_serp_serper(query, **kwargs):
    retries = 3
    for _ in range(retries):
        api_key = next(api_key_cycle)
        data, error = make_request(query, api_key, **kwargs)
        if data:
            # Assuming the SERP data you need is in the response JSON under 'serp_data'
            # Adjust according to the actual response structure
            print(f"Success with key {api_key} for {query}")
            return data
        else:
            print(f"Error fetching SERP data with key {api_key}: {error}")
    return "Error fetching SERP data after multiple retries"



if __name__=="__main__":
    c = get_serp_serper("https://animalvivid.com/contact/")
    print(c)