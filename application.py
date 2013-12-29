from argparse import ArgumentParser
import errno
from json import load as json_load, dump as json_dump
from os import makedirs
from os.path import dirname, isdir, normpath

from lunabot.default_config import default_config

config = None

def main():
    arg_parser = ArgumentParser(prog="lunabot")
    arg_parser.add_argument("-c", "--config", dest="config_file_name")
    args = arg_parser.parse_args()

    # According to the docs, makedirs() gets confused if
    # the path you give it has `..` in it. So, just in case...
    config_file_name = normpath(args.config_file_name)

    global config
    try:
        with open(config_file_name, "r") as config_file:
            config = json_load(config_file)
    except FileNotFoundError:
        config_file_parent = dirname(config_file_name)
        try:
            makedirs(config_file_parent, exist_ok=True)
        except OSError as exception:
            if exception.errno == errno.EEXIST and isdir(config_file_parent):
                pass
            else:
                raise
        config = dict(default_config)
        with open(config_file_name, "w") as config_file:
            json_dump(config, config_file)
