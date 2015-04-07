import bisect

identity = (lambda x: x)

class SortedList:
    def __init__(self, iterable=None, key=identity):
        self._key = key
        self._items = []
        self._keys = []
        if iterable:
            for item in iterable:
                self.append(item)

    def __repr__(self):
        return '{}({}{})'.format(type(self).__name__, repr(self._items), (
            ', key={}'.format(repr(self._key)) if self._key is not identity else ''))

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self._items)

    def __contains__(self, item):
        try:
            self.index(item)
        except ValueError:
            return False
        return True

    def __getitem__(self, key):
        return self._items[key]

    def __delitem__(self, key):
        del self._items[key]
        del self._keys[key]

    __hash__ = None

    def __eq__(self, other):
        return self._items == other

    def __ne__(self, other):
        return self._items != other

    def __add__(self, other):
        new = self.copy()
        new += other
        return new

    def __radd__(self, other):
        return self + other

    def __iadd__(self, other):
        for item in other:
            self.append(item)

    def __mul__(self, count):
        new = type(self)()
        for item in self:
            for _ in range(count):
                new.append(item)
        return new

    def __rmul__(self, count):
        return self * count

    def __imul__(self, count):
        for item in self:
            for _ in range(count - 1):
                self.append(item)

    def index(self, item, start=0, stop=None):
        start, stop, _ = slice(start, stop).indices(len(self))
        key = self._key(item)
        index = max(bisect.bisect_left(self._keys, key), start)
        while index < stop and self._keys[index] == key:
            if self._items[index] == item:
                return index
            index += 1
        raise ValueError("{0} is not in {2}{1}".format(repr(item), type(self).__name__, (
            "slice [{}:{}] of ".format(start, stop) if (start, stop) != (0, len(self)) else "")))

    def count(self, item, start=0, stop=None):
        count = 0
        index = start
        while True:
            try:
                index = self.index(item, start=index, stop=stop) + 1
            except ValueError:
                return count
            else:
                count += 1

    def append(self, item):
        key = self._key(item)
        index = bisect.bisect_right(self._keys, key)
        self._items.insert(index, item)
        self._keys.insert(index, key)

    def insert(self, index, item):
        if index >= len(self):
            self.append(item)
            return
        key = self._key(item)
        if self._keys[index] < key:
            index = bisect.bisect_left(self._keys, key)
        elif self._keys[index] > key:
            index = bisect.bisect_right(self._keys, key)
        self._items.insert(index, item)
        self._keys.insert(index, key)

    def pop(self, index=None):
        if index is None:
            index = len(self)
        item = self[index]
        del self[index]
        return item

    def extend(self, iterable):
        self += iterable

    def remove(self, item, start=0, stop=None):
        del self[self.index(item, start, stop)]

    def discard(self, item, start=0, stop=None):
        try:
            self.remove(item, start, stop)
        except ValueError:
            pass

    def copy(self):
        return type(self)(self, self._key)

    def clear(self):
        self._items.clear()
        self._keys.clear()
