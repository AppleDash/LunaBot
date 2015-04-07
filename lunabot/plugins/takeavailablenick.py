from lunabot.handler import Handler, HandlerPriority

# TODO: handle 432s from when we try to set nicks that are too long

_SUFFIX_CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"
_SUFFIX_LEN = 8  # TODO: make this a config option, maybe?
_TRIES_PER_NICK = 64

handlers = []

def find_available_nick(connection):
    with connection.config_lock:
        nicks = self.config["nicks"]
    for nick in nicks:
        yield nick
    for nick in nicks:
        tried_suffixes = set()
        for _ in range(_TRIES_PER_NICK):
            suffix = "".join(random.choice(_SUFFIX_CHARS) for _ in range(_SUFFIX_LEN))
            yield nick + "_" + suffix
            tried_suffixes.add(suffix)

def take_available_nick(connection, line):
    for nick in find_available_nick():
        connection.send_nick(nick)
        yield

def unload_handlers(connection, line):
    connection.handlers.remove(*handlers)

handlers[:] = [
    Handler("433", HandlerPriority.normal, take_available_nick),
    Handler("NICK", HandlerPriority.normal, unload_handlers),
    ]
