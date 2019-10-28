import os
import json
import urllib
import random
from snaky.commands import commands


class MetaParser:
    '''
        The MetaParser is used to parsed Meta Values placed inside the emotes.
        It will thus change something like $Name(args) to the appropriate value.
        The metaTags is a dict containing the tag as keys and their equivalent as value.

        The way that things work is using the following structure:

        Dict: a dict containing everything (the emote)
        |- Item: a value of a specific field from the Dict
           |- Statement: a full meta statement that looks like $Name(arg)(arg)(arg), 
                        there might be nested arguments $Name($Name(arg))
              |- Meta: the tag of the meta statement, between $ and the first bracket
              |- Arguments: an array of arguments, located between brackets
                 |- Arg 1
                 |- Arg 2
                 |- ... 
        The class is divided in methods accordingly.
    '''

    def __init__(self, meta_tags):
        self.meta_tags = meta_tags

    def parse_dict(self, items):
        for field in items:
            if type(items[field]) is dict:
                self.parse_dict(items[field])
            elif type(items[field]) is str:
                item = items[field]
                items[field] = self.parse_item(item)

    def parse_item(self, item):
        cursor = 0
        previous = ''
        begin = []
        while cursor < len(item):
            current = item[cursor]
            end_statement = (cursor + 1 == len(item)
                             or item[cursor + 1] != '(')
            if current == '$' and previous != '\\':
                begin.append(cursor)
            elif current == ')' and end_statement and previous != '\\' and len(begin) != 0:
                last_begin = begin[-1]
                end = cursor
                meta_statement = item[last_begin:end] + current
                result = str(self.parse_statement(meta_statement))
                cursor = last_begin + len(result) - 1
                item = item.replace(meta_statement, result)
                begin.pop()
            previous = current
            cursor += 1
        return item

    def parse_statement(self, statement):
        cursor = 1
        previous = '$'
        while statement[cursor] != "(" or previous == '\\':
            previous = statement[cursor]
            cursor += 1
        tag = statement[1:cursor]
        if not tag in self.meta_tags:
            return statement
        args = []
        cursor += 1
        while cursor < len(statement):
            begin_arg = cursor
            while statement[cursor] != ")" or previous == '\\':
                previous = statement[cursor]
                cursor += 1
            args.append(statement[begin_arg:cursor])
            cursor += 2
        meta = self.meta_tags[tag]
        for arg in args:
            arg = arg.replace("\\(", "(").replace("\\)", ")")
            meta = self.parse_meta(meta, arg)

        return meta

    def parse_meta(self, meta, arguments):
        if callable(meta):
            result = meta(arguments)
        elif type(meta) is list:
            if arguments == "all":
                separator = " "
                result = separator.join(map(str, meta))
            else:
                result = meta[int(arguments)]
        elif isinstance(meta, dict):
            result = meta[arguments]
        else:
            result = getattr(meta, arguments)

        return result

    @staticmethod
    def random_number(max):
        '''
            Returns a random number on [0; max[
        '''
        try:
            max = int(max)
        except:
            max = 100

        return random.randint(0, max)

    @staticmethod
    def get_response(url):
        '''
            Allows retrieving content from the web thanks to a given URL
        '''
        url = url.replace(' ', '%20')
        headers = {
            'User-Agent': 'Snaky/5.3'
        }

        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        response_content = response.read()

        return response_content.decode("utf-8").replace('(', '\\(').replace(')', '\\)').replace('$', '\\$')

    @staticmethod
    def get_gif(search_query):
        '''
            Returns a gif from tenor with a given search query.
            This is the function normally used when using the Gif meta tag.
        '''
        gif_url = "https://media1.tenor.com/images/4cf708c3935a0755bbe1e9d52ef8378d/tenor.gif?itemid=13009757"
        api_key = os.getenv("API_TENOR")
        limit = 50

        request_gifs = urllib.request.urlopen(
            "https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" %
            (search_query.replace(' ', '%20'), api_key, limit))

        request_gifs_content = json.loads(request_gifs.read())

        if request_gifs.code == 200:
            gif_url = random.choice(request_gifs_content["results"])[
                "media"][0]["gif"]["url"]

        return gif_url
