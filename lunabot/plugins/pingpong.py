from lunabot.handler import Handler, UNKNOWN_PRIORITY

def pingpong_callback(connection, line):
    connection.send_raw(str(line).replace("PING", "PONG", 1))
    return True

pingpong = Handler("PING", UNKNOWN_PRIORITY, pingpong_callback)
