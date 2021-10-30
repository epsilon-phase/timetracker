"""
Implements a few baseclasses that are useful in coloring the data's shapes.
"""

from typing import *
from timetracker.models import WindowEvent
from math import floor


class DataColorer:
    def __init__(self, evts, keyfunc):
        self.events = list(filter(lambda x: keyfunc(x), evts))
        self.key_func = keyfunc
        self.max = max(self.events, key=self.key_func)
        self.min = min(self.events, key=self.key_func)

    def color(self, w: WindowEvent) -> str:
        pass

    @staticmethod
    def fromtuple(tuple) -> str:
        return f"rgb({abs(tuple[0])},{abs(tuple[1])},{abs(tuple[2])})"


color = tuple[float, float, float]


class Gradient(DataColorer):
    """
    Provide coloring for a dataset based on the result of a function extracting a value from the dataset.
    Interpolates two colors linearly.
    """

    def __init__(self, evts: Iterable[WindowEvent], keyfunc: Callable[[WindowEvent], float],
                 start: color, end: color):
        super().__init__(evts, keyfunc)
        self.start, self.end = start, end

    def from_fraction_base(self, t: float):
        c = tuple(map(lambda x, y: round((y - x) * t + x), self.start, self.end))
        return c

    def from_fraction(self, t: float):
        mn, mx = self.key_func(self.min), self.key_func(self.max)
        t = (t - mn) / (mx - mn)
        return self.from_fraction_base(t)

    def color(self, w: WindowEvent) -> str:
        t = self.key_func(w)
        return self.fromtuple(self.from_fraction(t))


class MultiGradient(DataColorer):
    """
    An extension of the gradient to more than two colors. This is experimental and not at all well considered.
    """

    def __init__(self, evts, keyfunc, colors: list[color]):
        super().__init__(evts, keyfunc)
        parts = [self.events[i:i + len(colors)] for i in
                 range(0, len(self.events), len(self.events) // len(colors))]
        self.colors = list(map(lambda x, y, z: Gradient(x, keyfunc, y, z), parts, colors, colors[1:]))

    def color(self, w: WindowEvent):
        # TODO This may not be a correct implementation.
        # If it isn't, then I will have to figure out a better option.
        t = ((self.key_func(w) - self.key_func(self.min)) / (self.key_func(self.max) - self.key_func(self.min))) * (len(
            self.colors))
        idx = floor(t) - 1 if floor(t) == len(self.colors) else 0
        return self.colors[idx].from_fraction(t)
