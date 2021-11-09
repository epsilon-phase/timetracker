from typing import *


class ColorChooser:
    background: str
    """
    The background color for charts made with this color chooser(pronounced palette)
    """
    lines: str
    """
    The color of the axis lines in the chart.
    """

    def choose(self, index: int) -> str:
        return ""


class ColorCycle(ColorChooser):
    """
    The most basic kind of colorchooser, makes a selection from the
    list of colors it knows about.
    """
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


class AssignedColors(ColorChooser):
    """
    Provides a simpler colorchooser implementation, assign colors to the tags that are displayed.
    """
    colors: dict[str, str]
    """The association between the tags and the colors"""
    lines: str
    """The color for the lines of the chart"""
    background: str
    """The background color of the chart"""
    fallthrough: ColorChooser
    """The `Colorchooser`_ that chooses the color if it's not assigned"""

    def __init__(self, tagged: dict[str, str], lines: str, background: str, fallthrough: ColorChooser):
        self.colors, self.lines, self.background, self.fallthrough = tagged, lines, background, fallthrough

    def choose(self, index: str) -> str:
        if index not in self.colors.keys():
            return self.fallthrough.choose(index)
        return self.colors[index]


monokai = ColorCycle(['#797979', '#d6d6d6', '#e5b567', '#b4d273', '#e87d3e', '#9e86c8', '#b05279', '#6c99bb'],
                     '#d6d6d6', '#2e2e2e')

randomly_generated = ColorCycle(['#8AF3FF', '#18A999', '#109648'], '#F7F0F0', '#484349')
