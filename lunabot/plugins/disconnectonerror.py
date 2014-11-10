from lunabot.handler import Handler, UNKNOWN_PRIORITY

def disconnect(connection, line):
    connection.disconnect()

disconnect_on_error = Handler("ERROR", UNKNOWN_PRIORITY, disconnect)
