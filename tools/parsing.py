import json


def parse_int(value, default=-1):
    '''
        Parses a value into an int,
        If it is impossible to do, this will return a default value.
    '''
    try:
        return int(value)
    except:
        return default


def try_parse_int(value):
    '''
        Try parsing a value into an int,
        Will return a Tuple containing the parsed or not parsed value,
        and a bool indicating the success of the parsing.
    '''
    try:
        return int(value), True
    except:
        return value, False

def parse_json(value, default={}):
    '''
        Parses a value into a dict/json,
        If it is impossible to do, this will return a default value.
    '''
    try:
        return json.loads(value)
    except:
        return default

def try_parse_json(value):
    '''
        Try parsing a value into a dict/json,
        Will return a Tuple containing the parsed or not parsed value,
        and a bool indicating the success of the parsing.
    '''
    try:
        return json.loads(value), True
    except:
        return value, False