from operator import attrgetter

class Handler():
    def __init__(self, event, priority, callback):
        self.event = event
        self.priority = priority
        self.callback = callback

    def __str__(self):
        return "Handler(event='%s', priority=%d, callback='%s')" % (self.event, self.priority, self.callback)

    def __repr__(self):
        return self.__str__()

class HandlerManager():
    def __init__(self):
        self.handler_lists = {}

    def add_handler(self, handler):
        try:
            self.handler_lists[handler.event].append(handler)
        except:
            self.handler_lists[handler.event] = [handler]
        return id(handler)

    def remove_handler(self, handler_id):
        for handler_list in self.handler_lists.values():
            # TODO: make this loop Pythonic:
            for i in range(len(handler_list) - 1):
                if id(handler_list[i]) == handler_id:
                    del handler_list[i]
                    return True
        return False

    def sort_handlers(self):
        for event in self.handler_lists.keys():
            self.handler_lists[event].sort(key=attrgetter('priority'), reverse=True)

    def print_handlers(self):
        for event in self.handler_lists.keys():
            handler_list = self.handler_lists[event]
            print("%s: %s" % (event, repr(handler_list)))

# TODO: Enum for event priorities or something?
