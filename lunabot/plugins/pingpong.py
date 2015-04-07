from lunabot.handler import Handler, HandlerPriority

def pingpong_callback(connection, line):
    connection.send_raw(str(line).replace("PING", "PONG", 1))
    return True

pingpong = Handler("PING", HandlerPriority.normal, pingpong_callback)
