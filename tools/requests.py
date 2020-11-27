import json
import random
import urllib
import urllib.request
import urllib.parse


def get_request(url):
    url = urllib.parse.quote(url, safe="/:=?&")
    headers = {
        'User-Agent': 'Snaky/6.1'
    }

    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    response_content = response.read()

    return response_content.decode()


def get_gif(search_query):
    search_query = urllib.parse.quote(search_query)
    gif_url = "https://media1.tenor.com/images/4cf708c3935a0755bbe1e9d52ef8378d/tenor.gif?itemid=13009757"

    request_gifs = urllib.request.urlopen(f"https://api.tenor.com/v1/search?q={search_query}&limit=50")

    request_gifs_content = json.loads(request_gifs.read())

    if request_gifs.code == 200:
        gif_url = random.choice(request_gifs_content["results"])[
            "media"][0]["gif"]["url"]

    return gif_url


def get_bytes_request(url):
    url = urllib.parse.quote(url, safe="/:=?&")
    headers = {
        'User-Agent': 'Snaky/6.1'
    }

    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    return response.read()
