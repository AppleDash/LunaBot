from argparse import ArgumentParser
import errno
from json import load as json_load, dump as json_dump
from os import makedirs
import os.path

from lunabot.default_config import default_config
from lunabot.handler import HandlerManager
from lunabot.connection import Connection

config = None
handlers = None

def main():
    arg_parser = ArgumentParser(prog="lunabot")
    arg_parser.add_argument("-d", "--config-dir", "--configuration-directory",
                            dest="config_dir")
    args = arg_parser.parse_args()

    # According to the docs, makedirs() gets confused if the path you give it
    # has `..` in it. So normpath() it just in case.
    config_dir = os.path.abspath(os.path.normpath(args.config_dir))
    config_file_name = os.path.join(config_dir, 'lunabot.json')

    global config
    try:
        with open(config_file_name, "r") as config_file:
            config = json_load(config_file)
    except FileNotFoundError:
        config = default_config.copy()
        try:
            with open(config_file_name, "x") as config_file:
                json_dump(config, config_file, sort_keys=True, indent=4, separators=(',', ': '))
        except FileNotFoundError:
            try:
                makedirs(config_dir, exist_ok=True)
            except OSError as exception:
                if exception.errno == errno.EEXIST and os.path.isdir(config_dir):
                    pass
                else:
                    raise

    for network_name in config["networks"]:
        network = config["networks"][network_name]
        c = Connection(network_name)
        c.start()
