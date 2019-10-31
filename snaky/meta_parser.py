import os
import json
import urllib
import random
import tools.parsing as parsing
from snaky.commands import commands


class MetaParser:
    '''
        The MetaParser is used to parsed Meta Values placed inside the emotes.
        It will thus change something like $Name(args) to the appropriate value.
        The meta_tags is a dict containing the tag as keys and their equivalent as value.
        The only default value is Tags which allows to get a tag thanks to its name.

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

        The only default MetaTag is "Tags", which is the dict containing every MetaTag
    '''

    def __init__(self, meta_tags):
        self.meta_tags = meta_tags
        self.meta_tags["Tags"] = self.meta_tags

    def parse_dict(self, items):
        for field in items:
            if type(items[field]) is dict:
                self.parse_dict(items[field])
            elif type(items[field]) is list:
                self.parse_list(items[field])
            elif type(items[field]) is str:
                item = items[field]
                items[field] = self.parse_item(item)

    def parse_list(self, items):
        for i in range(len(items)):
            item = items[i]
            if type(item) is dict:
                self.parse_dict(item)
            elif type(item) is list:
                self.parse_list(item)
            elif type(item) is str:
                items[i] = self.parse_item(item)

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
                result = self.parse_statement(meta_statement)
                is_json = isinstance(result, dict) or isinstance(result, list)
                result = json.dumps(result) if is_json else str(result)
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
        args = []
        cursor += 1
        while cursor < len(statement):
            begin_arg = cursor
            while statement[cursor] != ")" or previous == '\\':
                previous = statement[cursor]
                cursor += 1
            args.append(statement[begin_arg:cursor])
            cursor += 2
        if not tag in self.meta_tags:
            self.meta_tags[tag] = parsing.try_parse_json(args.pop(0))[0]
        meta = self.meta_tags[tag]
        for arg in args:
            arg = arg.replace("\\(", "(").replace("\\)", ")")
            meta = self.parse_meta(meta, arg)

        return meta

    def parse_meta(self, meta, arguments):
        if callable(meta):
            return meta(arguments)
        elif not arguments:
            return meta
        elif type(meta) is list:
            parsed = parsing.try_parse_int(arguments)
            if arguments == "all":
                return ' '.join(map(str, meta))
            elif parsed[1]:
                return meta[parsed[0]]
        elif isinstance(meta, dict):
            return meta[arguments]
        return getattr(meta, arguments)

    @staticmethod
    def random_number(args):
        '''
            Args is either "min_born max_born" or "max_born"
            min_born defaults to 0 and max_born defaults to 1
            Returns a random number on [min_born; max_born]
        '''
        args = args.split(',', 1)
        min_born = 0
        max_born = 1
        if len(args) > 1:
            min_born = parsing.parse_int(args[0], 0)
            max_born = parsing.parse_int(args[1], 1)
        else:
            max_born = parsing.parse_int(args[0], 1)

        return random.randint(min_born, max_born)

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
        search_query = search_query.replace(' ', '%20')
        gif_url = "https://media1.tenor.com/images/4cf708c3935a0755bbe1e9d52ef8378d/tenor.gif?itemid=13009757"
        api_key = os.getenv("API_TENOR")
        limit = 50

        request_gifs = urllib.request.urlopen(
            f"https://api.tenor.com/v1/search?q={search_query}&key={api_key}&limit={limit}")

        request_gifs_content = json.loads(request_gifs.read())

        if request_gifs.code == 200:
            gif_url = random.choice(request_gifs_content["results"])[
                "media"][0]["gif"]["url"]

        return gif_url

    @staticmethod
    def no_return(args):
        '''
            Returns an empty string
        '''
        return ""
