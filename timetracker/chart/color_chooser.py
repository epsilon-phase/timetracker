from typing import *


class ColorChooser:
    background: str
    lines: str

    def choose(self, index: int) -> str:
        return ""


class color_cycle(ColorChooser):
    colors: list[str]
    lines: str
    background: str

    def __init__(self, l: list[str], lines: str, background: str):
        self.colors = l
        self.lines = lines
        self.background = background

    def choose(self, index: int) -> str:
        if isinstance(index, str):
            index = hash(index)
        return self.colors[index % len(self.colors)]


monokai = color_cycle(['#797979', '#d6d6d6', '#e5b567', '#b4d273', '#e87d3e', '#9e86c8', '#b05279', '#6c99bb'],
                      '#d6d6d6', '#2e2e2e')

randomly_generated = color_cycle(['#8AF3FF', '#18A999', '#109648'], '#F7F0F0', '#484349')

