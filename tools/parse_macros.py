import json
import random
import xmltodict
from tools.requests import get_request, get_gif

glob = {
    "random": random,
    "get_request": get_request,
    "get_gif": get_gif,
    "xmltodict": xmltodict,
    "json": json
}


def parse_variables(variables=None, base=None):
    if base is None:
        base = {}
    if variables is None:
        variables = {}
    for key, value in variables.items():
        if type(value) == str:
            base[key] = eval(value, glob, base)
    return base


def parse_embed(embed, variables):
    for key, val in embed.items():
        if type(val) == str:
            embed[key] = eval(val, glob, variables)
        elif type(val) == dict:
            embed[key] = parse_embed(val, variables)
        elif type(val) == list:
            embed[key] = [parse_embed(sub, variables) for sub in val]
    return embed


def parse_macro(macro, base_variables=None):
    if base_variables is None:
        base_variables = {}
    try:
        variables = parse_variables(({} if "vars" not in macro else macro["vars"]), base_variables)
        if "content" in macro:
            macro["content"] = eval(macro["content"], glob, variables)
        if "embed" in macro:
            macro["embed"] = parse_embed(macro["embed"], variables)
        return macro
    except Exception as e:
        return {
            "embed": {
                "title": type(e).__name__,
                "description": f"```{e}```"
            }
        } if "error" not in macro else parse_macro(macro["error"], base_variables)
