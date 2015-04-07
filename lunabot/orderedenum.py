import enum
from functools import total_ordering

@total_ordering
class OrderedEnum(enum.Enum):
    def __lt__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        # At this point, we know the operands are both from the same enum.
        try:
            return self.value < other.value
        except TypeError as exception:
            # So if we get here, there's nothing that could possibly take over the comparison
            # if we were to return NotImplemented.
            raise TypeError(
                "unorderable enumeration values: {} (type {}), {} (type {})".format(
                    str(self), type(self.value).__name__, str(other), type(other.value).__name__,
                    )
                ) from exception
