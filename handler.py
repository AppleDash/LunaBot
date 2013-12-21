from operator import attrgetter

class Handler():
    def __init__(self, event, priority, callback):
        self.event = event
        self.priority = priority
        self.callback = callback
        self.hid = -1

    def __str__(self):
        return "Handler(event='%s', priority=%d, callback='%s')" % (self.event, self.priority, self.callback)

    def __repr__(self):
        return self.__str__()

class HandlerManager():
    def __init__(self):
        self.handler_lists = {}
        self._counter = 0

    def add_handler(self, handler):
        self._counter += 1
        handler.hid = self._counter
        try:
            self.handler_lists[handler.event].append(handler)
        except:
            self.handler_lists[handler.event] = [handler]
        return self._counter

    def remove_handler(self, hid):
        for handler_list in self.handler_lists.values():
            # TODO: make this loop Pythonic:
            for i in range(len(handler_list) - 1):
                if handler_list[i].hid == hid:
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
