"""
Provide the common functionality required by the various chart types such
as providing the ability to set a title/color-scheme, helper functions, etc
"""

import svgwrite.drawing
from . import color_chooser

from svgwrite import Drawing, cm


class ChartPartBase:
    color_chooser: color_chooser.ColorChooser
    title: str

    def draw_title(self):
        pass

    def draw(self, drw: Drawing, width: float, height: float, vertical_offset: float, horizontal_offset: float,
             *args) -> svgwrite.drawing.SVG:
        """
        Draw the base chart, returning the group that all items should be added to.

        :param drw: The svg drawing to add this chart to.
        :param width: The width of the chart in centimeters
        :param height: The height of the chart in centimeters
        :returns: The group that should contain all elements of the chart.
        """
        ret = drw.add(drw.g())
        ret.add(drw.rect(insert=(horizontal_offset*cm,
                vertical_offset*cm), size=(width*cm, height*cm), fill=self.color_chooser.background))
        ret.add(drw.text(self.title, x=[
                horizontal_offset*cm], y=[(vertical_offset+0.5)*cm],
            fill=self.color_chooser.lines))
        return ret
