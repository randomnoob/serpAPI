import requests
import json
import itertools
from config import SERPER_API_KEY

api_keys = [SERPER_API_KEY]
api_key_cycle = itertools.cycle(api_keys)

def make_request(query, api_key, **kwargs):
    endpoint = "https://serp_4_4011.aiktp.com/"
    options = {
            "task": "getResultFromGoogle",
            "query": query,
            "userKey": "3907dec36a6f62f3dc02baea531d3878",
            }
    options.update(kwargs)
    payload = json.dumps(options)
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            }

    response = requests.post(endpoint, headers=headers, data=payload, verify=False)
    if response.status_code == 200:
        return response.json(), None
    else:
        print(response.text)
        return None, response.status_code

def get_serp_aiktp(query, **kwargs):
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
    c = get_serp_aiktp("https://animalvivid.com/contact/")
    print(c)