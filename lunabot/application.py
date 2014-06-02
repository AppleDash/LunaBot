from argparse import ArgumentParser
import errno
from json import load as json_load, dump as json_dump
from os import makedirs
import os.path

import lunabot.config
from lunabot.connection import Connection
from lunabot.handler import HandlerManager

def main():
    arg_parser = ArgumentParser(prog="lunabot")
    arg_parser.add_argument("-d", "--config-dir", "--configuration-directory",
                            default=os.path.expanduser("~/.lunabot"), dest="config_dir")
    args = arg_parser.parse_args()

    # According to the docs, makedirs() gets confused if the path you give it
    # has `..` in it. So normpath() it just in case.
    config_dir = os.path.abspath(os.path.normpath(args.config_dir))
    config_file_name = os.path.join(config_dir, 'lunabot.json')

    # TODO: this is hackish and there's probably a better way:
    lunabot.config.dir = config_dir
    lunabot.config.load(config_file_name)

    global_handlers = HandlerManager()

    with lunabot.config.current_lock:
        for network_name, _ in lunabot.config.current.get("networks", {}).items():
            Connection(network_name, lunabot.config.current, lunabot.config.current_lock, global_handlers).start()
