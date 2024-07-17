import requests
import itertools

with open("./working_keys.txt") as fin:
    API_KEYS = [x.strip() for x in fin.readlines()]
    # API_KEYS = [
    #     "a417c75840f5b0aabab2ffdf6f0ee103e072bad3a9182c0fef468cf534772362",
    #     "868547210328e6b4e89af777029200c2c8a5e40f388124ffd1eadc0a704b3684",
    #     "44b17b65ee540422ab534938e98391794fc242b5fb946d672b7e785b18a99386",
    #     "fd47a1058ed9175aa8539692a9ce77d94bd5e810b91b7c9b47e309fa3529d08b",
    # ]

# Create a cycle iterator for round-robin API key usage
api_key_cycle = itertools.cycle(API_KEYS)


def make_request(url, api_key):
    endpoint = "https://serpapi.com/search.json"
    params = {
        "engine":"google",
        "location":"Austin,+Texas,+United+States",
        "hl":"en",
        "gl":"us",
        "google_url":"google.com",
        "q": url,
        "apikey": api_key,
    }

    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json(), None
    else:
        return None, response.status_code

def get_serp(url):
    retries = 3
    for _ in range(retries):
        api_key = next(api_key_cycle)
        data, error = make_request(url, api_key)
        if data:
            # Assuming the SERP data you need is in the response JSON under 'serp_data'
            # Adjust according to the actual response structure
            print(f"Success with key {api_key} for {url}")
            return data
        else:
            print(f"Error fetching SERP data with key {api_key}: {error}")
    return "Error fetching SERP data after multiple retries"



if __name__=="__main__":
    c = get_serp("ostechnix.com")
    # print(c)