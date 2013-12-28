import re
from operator import attrgetter

class Handler():
    def __init__(self, event, priority, pattern, callback):
        self.event = event
        self.priority = priority
        self.pattern = re.compile(pattern)
        self.callback = callback

    def __str__(self):
        return "Handler(event=%s, priority=%d, pattern=%s callback=%s)" % (repr(self.event), self.priority, repr(self.pattern.pattern), self.callback)

    def __repr__(self):
        return self.__str__()

class HandlerManager():
    def __init__(self):
        self.handler_lists = {}

    def add_handlers(self, *handlers):
        for handler in handlers:
            try:
                self.handler_lists[handler.event].append(handler)
            except KeyError:
                self.handler_lists[handler.event] = [handler]

    def remove_handlers(self, *handler_ids):
        for handler_list in self.handler_lists.values():
            # TODO: make this loop Pythonic:
            for i in range(len(handler_list) - 1):
                if id(handler_list[i]) in handler_ids:
                    del handler_list[i]

    def sort_handlers(self):
        for event in self.handler_lists.keys():
            self.handler_lists[event].sort(key=attrgetter("priority"), reverse=True)

    def print_handlers(self):
        for event in self.handler_lists.keys():
            handler_list = self.handler_lists[event]
            print("%s: %s" % (event, repr(handler_list)))

# TODO: Enum for event priorities or something?
