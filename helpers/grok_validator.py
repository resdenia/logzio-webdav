from pygrok import Grok
from decouple import config
import ast


def gr_validator(current_line):
    result = None
    try:
        patterns = ast.literal_eval(
            config('GROK_PATTERNS'))
        for pattern in patterns:
            grok = Grok(pattern)
            result = grok.match(current_line)
            if not result == None:
                break
    except:
        print(
            "Please check If your grok array have right syntax ['GROK_PATTERN' ...]")
    return result
