from requests import RequestException
import requests
import random
import json
import traceback

keywords = "/home/nl/PROJECTS/scrapybing/keywords.txt"
serpapi_keys = "/home/nl/PROJECTS/scrapybing/serpapi_keys.txt"

with open(keywords) as fin:
    domains = [x.strip() for x in fin.readlines()]
with open(serpapi_keys) as fin:
    api_keys = [x.strip() for x in fin.readlines()]


def get_image_results(query):
    key = random.choice(api_keys)
    print(f"Choose key : {key}")
    url_base = "https://serpapi.com/search"
    params = {
        'q': query,
        'tbm': 'isch',
        'engine': 'google',
        'api_key': key,
    }
    try:
        r = requests.get(url_base, params=params)
        data = r.json()
        if data['search_information']:
            return r.json()
        else:
            print(f"Failed with key : {key} ==> remove")
            api_keys.remove(key)
            print(f"Remaining keys : {len(api_keys)}")
            return get_image_results(query)
    except (RequestException, KeyError):
        traceback.print_exc()
        print(f"Failed with key : {key} ==> remove")
        api_keys.remove(key)
        print(f"Remaining keys : {len(api_keys)}")
        return get_image_results(query)


if __name__=="__main__":
    results = []
    for idx, dom in enumerate(domains):
        print(f"{idx}. {dom}")
        serp = get_image_results(query=f"hình ảnh {dom}")
        try:
            total_result = serp['search_information']['total_results']
        except:
            total_result = ""
        item = {
            "domain": dom,
            "response": serp,
            "total_result": total_result,
        }
        results.append(item)
        with open("/home/nl/PROJECTS/scrapybing/bingcrawl/serpapi-adthrive2.json", "w") as fout:
            json.dump(results, fout, indent=2)
    

