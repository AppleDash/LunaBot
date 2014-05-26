from itertools import chain
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

    def __repr__(self):
        return "Handler(event=%s, priority=%d, pattern=%s, callback=%s)" % (
            repr(self.event), self.priority,
            repr(self.pattern.pattern), self.callback,
            )

    def __str__(self):
        return repr(self)

class HandlerManager:
    def __init__(self, *handlers):
        self.handler_lists = {}
        self.add(*handlers)

    def __repr__(self):
        return repr(list(chain(*self.handler_lists.values())))

    def __str__(self):
        return object.__repr__(self)

    def __len__(self):
        return sum([len(handler_list) for handler_list in handler_lists])

    def __iter__(self):
        return chain(*self.handler_lists.values())

    def add(self, *handlers):
        changed_events = set()
        for handler in handlers:
            changed_events.add(handler.event)
            try:
                self.handler_lists[handler.event].append(handler)
            except KeyError:
                self.handler_lists[handler.event] = [handler]
        for event in changed_events:
            self.handler_lists[event].sort(key=attrgetter("priority"))

    def remove(self, *handlers):
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

    def clear(self):
        self.handler_lists.clear()

    def __getitem__(self, index):
        return [item for item in self.handler_lists.get(index, [])]

# TODO: Enum for event priorities or something?
UNKNOWN_PRIORITY = -1