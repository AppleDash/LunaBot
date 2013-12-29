from re import compile as re_compile
from operator import attrgetter

class Handler:
    def __init__(self, event, priority, pattern, callback):
        self.event = event
        self.priority = priority
        # If you pass re.compile() a compile()d regex object, it returns it
        # (presumably without further processing).
        # Thus, /pattern/ may be either a string or a regex object.
        self.pattern = re_compile(pattern)
        self.callback = callback

    def __str__(self):
        return "Handler(event=%s, priority=%d, pattern=%s, callback=%s)" % (
            repr(self.event), self.priority,
            repr(self.pattern.pattern), self.callback,
            )

    def __repr__(self):
        return self.__str__()

class HandlerManager:
    def __init__(self):
        self.handler_lists = {}

    def add_handlers(self, *handlers):
        changed_events = set()
        for handler in handlers:
            changed_events.add(handler.event)
            try:
                self.handler_lists[handler.event].append(handler)
            except KeyError:
                self.handler_lists[handler.event] = [handler]
        for event in changed_events:
            self.handler_lists[event].sort(key=attrgetter("priority"))

    def remove_handlers(self, *handlers):
        changed_events = set()
        for handler in handlers:
            changed_events.add(handler.event)
            try:
                self.handler_lists[handler.event].remove(handler)
            except ValueError:
                # The Handler wasn't in the list. That's perfectly fine.
                pass
        for event in changed_events:
            if not self.handler_lists[event]:
                del self.handler_lists[event]

# TODO: Enum for event priorities or something?
