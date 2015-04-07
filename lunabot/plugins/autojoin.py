from lunabot.handler import Handler, HandlerPriority

# TODO: we need a way to add these back on connect

autojoin_handlers = []

def join_channels(connection, line):
    with connection.config_lock:
        channels = connection.config["channels"]
    connection.send_join(",".join(channels))
    connection.handlers.remove(*autojoin_handlers)

autojoin_handlers[:] = [
    Handler("376", HandlerPriority.normal, join_channels),
    Handler("422", HandlerPriority.normal, join_channels),
    ]
