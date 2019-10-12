import os
import json
import urllib
import random
import xmltodict


class MetaParser:
    """
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
    """

    def __init__(self, metaTags):
        self.metaTags = metaTags

    def parseDict(self, items):
        for field in items:
            if type(items[field]) is dict:
                self.parseDict(items[field])
            elif type(items[field]) is str:
                item = items[field]
                items[field] = self.parseItem(item)

    def parseItem(self, item):
        cursor = 0
        previous = ''
        begin = []
        while cursor < len(item):
            current = item[cursor]
            endStatement = (cursor + 1 == len(item) or item[cursor + 1] != '(')
            if current == '$' and previous != '\\':
                begin.append(cursor)
            elif current == ')' and endStatement and previous != '\\' and len(begin) != 0:
                lastBegin = begin[-1]
                end = cursor
                metaStatement = item[lastBegin:end] + current
                result = str(self.parseStatement(metaStatement))
                cursor = lastBegin + len(result) - 1
                item = item.replace(metaStatement, result)
                begin.pop()
            previous = current
            cursor += 1
        return item

    def parseStatement(self, statement):
        cursor = 1
        previous = '$'
        while statement[cursor] != "(" or previous == '\\':
            previous = statement[cursor]
            cursor += 1
        tag = statement[1:cursor]
        if not tag in self.metaTags:
            return statement
        args = []
        cursor += 1
        while cursor < len(statement):
            beginArg = cursor
            while statement[cursor] != ")" or previous == '\\':
                previous = statement[cursor]
                cursor += 1
            args.append(statement[beginArg:cursor])
            cursor += 2
        meta = self.metaTags[tag]
        for arg in args:
            arg = arg.replace("\\(", "(").replace("\\)", ")")
            meta = self.parseMeta(meta, arg)

        return meta

    def parseMeta(self, meta, arguments):
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
        try:
            max = int(max)
        except:
            max = 100

        return random.randint(0, max)

    @staticmethod
    def get_api(apiUrl):
        apiUrl = apiUrl.replace(' ', '%20')

        response = urllib.request.urlopen(apiUrl)
        contentType = response.info().items()[1][1]
        responseContent = response.read()
        if "json" in contentType:
            return json.loads(responseContent)
        elif "xml" in contentType:
            return xmltodict.parse(responseContent)
        return responseContent

    @staticmethod
    def get_gif(searchQuery):
        """
            Returns a gif from tenor with a given search query.
            This is the function normally used when using the Gif meta tag.
        """
        gifUrl = "https://media1.tenor.com/images/4cf708c3935a0755bbe1e9d52ef8378d/tenor.gif?itemid=13009757"
        apiKey = os.getenv("API_TENOR")
        limit = 50

        requestGifs = urllib.request.urlopen(
            "https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" %
            (searchQuery.replace(' ', '%20'), apiKey, limit))

        requestGifsContent = json.loads(requestGifs.read())

        if requestGifs.code == 200:
            gifUrl = random.choice(requestGifsContent["results"])[
                "media"][0]["gif"]["url"]

        return gifUrl
