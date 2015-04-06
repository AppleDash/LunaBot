from itertools import chain
from operator import attrgetter

class Handler:
    def __init__(self, event, priority, callback):
        self.event = event
        self.priority = priority
        self.callback = callback

    def __repr__(self):
        return "Handler(event=%s, priority=%d, callback=%s)" % (
            repr(self.event), self.priority, self.callback,
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
        # Not repr(self) because we want `object`s representation.
        return object.__repr__(self)

    def __len__(self):
        return sum(len(handler_list) for handler_list in self.handler_lists)

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
        for handler in handlers:
            try:
                self.handler_lists[handler.event].remove(handler)
            except (KeyError, ValueError):
                # The Handler wasn't in the list, or there were no Handlers
                # for that event. That's perfectly fine.
                pass
            if not self.handler_lists[handler.event]:
                del self.handler_lists[handler.event]

    def clear(self):
        self.handler_lists.clear()

    def __getitem__(self, key):
        return self.handler_lists.get(key, [])

# TODO: Enum for event priorities or something?
UNKNOWN_PRIORITY = -1
