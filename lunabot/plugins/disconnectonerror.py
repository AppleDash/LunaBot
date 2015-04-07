from lunabot.handler import Handler, HandlerPriority

def disconnect(connection, line):
    connection.disconnect()

disconnect_on_error = Handler("ERROR", HandlerPriority.normal, disconnect)
