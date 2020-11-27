import discord
import os
import json
import urllib
import random
import xmltodict
import tools.collections as collections
import tools.parsing as parsing


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
        if item == None:
            return item
        parsed = parsing.try_parse_json(item)
        if parsed[1]:
            item = parsed[0]
            if isinstance(item, dict):
                self.parse_dict(item)
            elif type(item) is list:
                self.parse_list(item)
            return item
        statements = self.find_statements(item)
        while len(statements) > 0:
            statement = statements.pop(0)
            begin = statement["begin"]
            end = statement["end"]
            tag = statement["tag"]
            inner = statement["inner"]
            follow_ups = statement["follow_ups"]
            length = statement["length"]

            inner = self.parse_item(inner)
            result = None
            if not tag in self.meta_tags:
                self.meta_tags[tag] = inner
                result = self.meta_tags[tag]
            else:
                result = self.parse_meta(self.meta_tags[tag], inner)
            for follow_up in follow_ups:
                follow_up = self.parse_item(follow_up)
                result = self.parse_meta(result, follow_up)
            if len(item) == length:
                item = result
            else:
                is_json = isinstance(result, dict) or isinstance(result, list) or isinstance(result, tuple)
                result = (json.dumps(result, default=lambda o: str(o)) if is_json else str(result)).replace('(', '\\\\(').replace(')', '\\\\)').replace('$', '\\\\$')
                item = f"{item[0:begin]}{result}{item[end:]}"
                for next_statement in statements:
                    shift = (length - len(result))
                    next_statement["begin"] -= shift
                    next_statement["end"] -= shift
        return item

    def find_statements(self, item):
        cursor = 0
        previous = ''
        statements = []
        while cursor < len(item):
            current = item[cursor]
            if current == '$' and previous != '\\':
                begin = cursor
                cursor += 1

                tag_search = self.find_tag(item, cursor, previous)
                tag = tag_search[0]
                cursor = tag_search[1]
                previous = tag_search[2]
                current = item[cursor - 1] 

                inner = None
                follow_ups = []
                if current == '(':
                    inner_search = self.find_inner(item, cursor, previous)
                    inner = inner_search[0]
                    cursor = inner_search[1]
                    previous = inner_search[2]

                    follow_ups_search = self.find_follow_ups(item, cursor, previous)
                    follow_ups = follow_ups_search[0]
                    cursor = follow_ups_search[1]
                    previous = follow_ups_search[2]

                current = item[cursor - 1]    
                end = cursor
                statements.append({"begin": begin, "end": end, "tag": tag,
                                   "inner": inner, "follow_ups": follow_ups, "length": end - begin})
            previous = current
            cursor += 1
        return statements

    def find_tag(self, item, cursor, previous):
        tag = ""
        current = item[cursor]
        while cursor < len(item) and current != '(' and current != ' ' or previous == '\\':
            current = item[cursor]
            if current != '(' and current != ' ' or previous == '\\':
                tag += current
            previous = current
            cursor += 1
        return (tag, cursor, previous)

    def find_inner(self, item, cursor, previous):
        current = item[cursor]
        bracket_count = 1
        inner = ""
        while bracket_count != 0 and cursor < len(item):
            current = item[cursor]
            if current == '(' and previous != '\\':
                bracket_count += 1
            elif current == ')' and previous != '\\':
                bracket_count -= 1
            if bracket_count != 0:
                inner += current
            previous = current
            cursor += 1
        return (inner, cursor, previous, current)

    def find_follow_ups(self, item, cursor, previous):
        follow_ups = []
        while cursor < len(item) and item[cursor] == '(':
            bracket_count = 1
            cursor += 1
            follow_up = ""
            while bracket_count != 0 and cursor < len(item):
                current = item[cursor]
                if current == '(' and previous != '\\':
                    bracket_count += 1
                elif current == ')' and previous != '\\':
                    bracket_count -= 1
                if bracket_count != 0:
                    follow_up += current
                previous = current
                cursor += 1 
            follow_ups.append(follow_up)
        return (follow_ups, cursor, previous)

    def parse_meta(self, meta, arguments):
        if arguments == None:
            return meta
        if callable(meta):
            if type(arguments) is str and not arguments:
                arguments = {}
            parsed = parsing.try_parse_json(arguments)
            param = parsed[0] if parsed[1] else arguments
            is_json = parsed[1] or isinstance(arguments, dict)
            if meta == json.loads and is_json:
                return param
            try:
                return meta(**param)
            except:
                try:
                    return meta(param)
                except:
                    return meta(str(param))
        elif type(arguments) is str and not arguments:
            return meta
        elif type(meta) is list or type(meta) is tuple:
            parsed = parsing.try_parse_int(arguments)
            if arguments == "all":
                return ' '.join(map(str, meta))
            elif parsed[1]:
                return meta[parsed[0]]
        elif isinstance(meta, dict) and arguments in meta:
            return meta[arguments]
        return getattr(meta, arguments)

    @staticmethod
    def is_end_statement(item, previous, cursor):
        '''
            This method returns a boolean indicating if the cursor is at the end of a 
            Meta statement in an item,
            a Meta statement being something as "$Name(arg)(arg1)(arg2)" 
        '''
        current = item[cursor]
        return ((cursor + 1 == len(item) or item[cursor + 1] != '(')
                and current == ')'
                and previous != '\\')

    @staticmethod
    def random_number(args):
        '''
            Args is either "min_born max_born" or "max_born"
            min_born defaults to 0 and max_born defaults to 1
            Returns a random number on [min_born; max_born]
        '''
        args = str(args).split(',', 1)
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
        url = urllib.parse.quote(url, safe="/:=?&")
        headers = {
            'User-Agent': 'Snaky/5.5'
        }

        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        response_content = response.read()

        return response_content.decode()

    @staticmethod
    def get_gif(search_query):
        '''
            Returns a gif from tenor with a given search query.
            This is the function normally used when using the Gif meta tag.
        '''
        search_query = urllib.parse.quote(search_query)
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


async def execute_command(custom_command, message, arguments, parser=None, depth=0, **kwargs):
    if not parser:
        parser = MetaParser({
            "Author": message.author,
            "Message": message,
            "Guild": message.guild,
            "Arguments": [] if not arguments else arguments.split(' '),
            "Gif": MetaParser.get_gif,
            "Mentions": message.mentions,
            "Request": MetaParser.get_response,
            "List": list,
            "Str": str,
            "Int": int,
            "Json": json.loads,
            "Xml": xmltodict.parse,
            "Random": MetaParser.random_number,
            "Choice": random.choice,
            "Choices": random.choices,
            "Len": len,
            "Find": collections.find,
            "Find_All": collections.find_all,
            "Get": collections.get,
            "Get_All": collections.get_all,
            "No_Return": MetaParser.no_return
        })
    try:
        await send_custom_command(custom_command, message, parser, depth)
    except Exception as e:
        error = {
            "title": type(e).__name__,
            "description": f"```{e}```"
        }
        if "error" in custom_command:
            error = custom_command["error"]
        await execute_command(error, message, arguments, parser, depth + 1)


async def send_custom_command(custom_command, message, parser, depth=0):
    if type(custom_command) is str:
        if depth < 5:
            custom_command = parser.parse_item(custom_command)
        if not type(custom_command) is str:
            await message.channel.send(str(custom_command))
        elif custom_command:
            await message.channel.send(custom_command)
    else:
        custom_command["color"] = 9276813
        custom_command["author"] = {
            "name": str(message.author),
            "icon_url": str(message.author.avatar_url_as(static_format='png'))
        }
        if ("image") in custom_command and ("$Gif(") in custom_command["image"]["url"]:
            custom_command["footer"] = {
                "text": "Powered by https://tenor.com",
                "icon_url": "https://tenor.com/assets/img/favicon/favicon-16x16.png"
            }

        before = custom_command.pop("before", None)
        after = custom_command.pop("after", None)
        variables = custom_command.pop("vars", {})

        if before != None:
            await send_custom_command(before, message, parser, depth + 1)

        if depth < 100:
            parse_variables(variables, parser)

            parser.parse_dict(custom_command)

        if has_content(custom_command):
            custom_command = parsing.serialize(custom_command)
            await message.channel.send(embed=discord.Embed.from_dict(custom_command))

        if after != None:
            await send_custom_command(after, message, parser, depth + 1)


def has_content(command):
    return ("image" in command
            or "title" in command
            or "description" in command
            or "fields" in command
            or "thumbnail" in command
            or "video" in command)


def parse_variables(variables, parser):
    if isinstance(variables, dict):
        for variable in variables:
            if isinstance(variables[variable], dict):
                parser.parse_dict(variables[variable])
            elif type(variables[variable]) is list:
                parser.parse_list(variables[variable])
            else:
                variables[variable] = parser.parse_item(variables[variable])
            parser.meta_tags[variable] = variables[variable]
    elif type(variables) is list:
        for declaration in variables:
            parse_variables(declaration, parser)
