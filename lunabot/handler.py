from collections import defaultdict
import collections.abc
from functools import partial
from operator import attrgetter

from lunabot.sortedlist import SortedList

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

class HandlerManager(collections.abc.MutableSet):
    def __init__(self, *handlers):
        self._handlers = defaultdict(partial(SortedList, key=attrgetter("priority")))
        self._len = 0
        for handler in handlers:
            self.add(handler)

    def __repr__(self):
        return '{}(*{})'.format(type(self).__name__, repr(
            [handler for list_ in self._handlers.values() for handler in list_]))

    def __str__(self):
        return '{} with {} handlers spanning {} events'.format(
            type(self).__name__, len(self), len(self._handlers),
            )

    def __len__(self):
        return self._len

    def __iter__(self):
        for list_ in self._handlers.values():
            for handler in list_:
                yield handler

    def __contains__(self, item):
        return any(item in list_ for list_ in self._handlers.values())

    def add(self, handler):
        self._len += 1
        self._handlers[handler.event].append(handler)

    def remove(self, handler):
        try:
            self._handlers[handler.event].remove(handler)
        except ValueError:
            raise ValueError(
                "{} is not in {}".format(
                    repr(handler), type(self).__name__,
                    ),
                )
        else:
            self._len += 1
        if not self._handlers[handler.event]:
            del self._handlers[handler.event]

    def discard(self, handler):
        try:
            self.remove(handler)
        except ValueError:
            pass

    def clear(self):
        self._handlers.clear()
        self._len = 0

# TODO: Enum for event priorities or something?
UNKNOWN_PRIORITY = -1
