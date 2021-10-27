from typing import *

from functools import lru_cache
from operator import itemgetter


def longest_common_substring(x: str, y: str) -> (int, int, int):
    """
    Get the longest common substring  of two strings

    :param x: The first string
    :param y: The second string
    :return: The length of each match
             the index of the match in the first string
             and the index of the match in the second string
    """
    @lru_cache(maxsize=1)
    def longest_common_prefix(i: int, j: int) -> int:
        if 0 <= i < len(x) and 0 <= j < len(y) and x[i] == y[j]:
            return 1 + longest_common_prefix(i + 1, j + 1)
        else:
            return 0

    def diagonal_computation():
        for k in range(len(x)):
            yield from ((longest_common_prefix(i, j), i, j)
                        for i, j in zip(range(k, -1, -1),
                                        range(len(y) - 1, -1, -1)))
        for k in range(len(y)):
            yield from ((longest_common_prefix(i, j), i, j)
                        for i, j in zip(range(k, -1, -1),
                                        range(len(x) - 1, -1, -1)))

    return max(diagonal_computation(), key=itemgetter(0), default=(0, 0, 0))
