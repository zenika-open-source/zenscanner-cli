from datetime import datetime
from os import environ


def log(module, info):
    print("[{}] [{}]: {}".format(datetime.now(), module, info))

def dbg(module, info):
    if "DEBUG" in environ and environ["DEBUG"]:
        print("[{}] [{}]: {}".format(datetime.now(), module, info))
