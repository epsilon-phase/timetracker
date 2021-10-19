from typing import *


class color_cycle:
    colors: list[str]

    def __init__(self, l: list[str]):
        self.colors = l

    def choose(self, index: int) -> str:
        return self.colors[index % len(self.colors)]


monokai = color_cycle(['#797979', '#d6d6d6', '#e5b567', '#b4d273', '#e87d3e', '#9e86c8', '#b05279', '#6c99bb'])
