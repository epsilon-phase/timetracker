"""
This is an implemntation of the chart generation that the :py:mod:`timetracker.examplereport` uses.
It is written from scratch because I didn't feel like figuring out how to get matplotlib to do it.
"""
from __future__ import annotations

import datetime

import svgwrite
from .. import models
from svgwrite import cm, mm
from . import color_chooser
from typing import *


class ChartPart:
    """
    A single part of the chart. At this point, just a single sort.
    A single day, in this case usually.
    """
    data: list[tuple[models.WindowEvent, list[str]]]
    range: datetime.timedelta
    range_start: datetime.datetime
    range_end: datetime.datetime
    title: str

    def __init__(self, title: str, data: list[tuple[models.WindowEvent, list[str]]], cc=color_chooser.monokai):
        """
        Create a new chartpart.
        :param title: The title applied to the chart
        :param data: The data contained within
        :param cc: The color chooser/palette
        """
        self.title = title
        self.data = data.copy()
        self.data.sort(key=lambda x: x[0].time_end)
        self.data.sort(key=lambda x: x[0].time_start)
        self.range = data[-1][0].time_end - data[0][0].time_start
        self.range_start = data[0][0].time_start
        self.range_end = data[-1][0].time_end
        self.tagindex = {}
        self.color_chooser = cc

    def chooseColor(self, tag: str) -> str:
        """
        Obtain a color that is consistent for a given tag with a given style
        :param tag: The tag to color
        :returns: The hex code of the color.
        """
        if tag not in self.tagindex.keys():
            self.tagindex[tag] = hash(tag)
        return self.color_chooser.choose(self.tagindex[tag])

    def draw(self, drw: svgwrite.Drawing, width: float, height: float, height_offset, horizontal_offset,
             show_titles: bool = False) -> None:
        """
        Draw the chart
        :param drw: The svg drawing
        :param width: The width of the chart part in centimeters
        :param height: The height of the chart part in centimeters
        :param height_offset: The vertical offset in centimeters
        :param horizontal_offset: The horizontal offset in centimeters
        :param show_titles: Add titles to the blocks, providing mouseovers displaying the window titles.
        :return: None
        """
        from . import color_chooser
        from functools import reduce
        import copy
        from itertools import chain
        chart: svgwrite.drawing.SVG = drw.add(drw.g())

        annotation_color = color_chooser.monokai.lines
        chart.add(drw.rect(insert=(horizontal_offset * cm, height_offset * cm), size=(width * cm, height * cm),
                           fill=color_chooser.monokai.background))
        chart.add(svgwrite.text.Text(self.title, x=[horizontal_offset * cm], y=[(height_offset + 0.5) * cm],
                                     fill=annotation_color))

        vticks: svgwrite.drawing.SVG = chart.add(drw.g(id="vticks"))
        blocks: svgwrite.drawing.SVG = chart.add(drw.g(id='blocks'))
        labels: svgwrite.drawing.SVG = chart.add(drw.g(id='labels'))

        tags = set(chain.from_iterable(map(lambda x: x[1], self.data)))
        offset = 3.5
        padding = 0.5
        delta = datetime.timedelta(hours=1)

        vscale = (height - 1) / len(tags)
        current = self.range_start
        ordinals = {name: number for (name, number) in zip(sorted(tags, key=str.lower), range(len(tags)))}
        # Ensures consistent numbering between different charts
        for i in ordinals.keys():
            self.chooseColor(i)
        pos = {}
        block_groups = {}
        current = current.replace(minute=0, second=0)
        end_time = (self.range_end + datetime.timedelta(hours=1)).replace(minute=0, second=0)
        start_time = current.replace()
        scale = (width - offset - padding) / (end_time - start_time).total_seconds()
        vticks.add(drw.line(start=((offset + horizontal_offset) * cm, height_offset * cm),
                            end=((horizontal_offset + offset) * cm, (height_offset + height) * cm),
                            stroke=annotation_color))

        # Provide a convenient means to make vertical lines.
        def vline(x1, y1, l, **e):
            """

            :param x1: The starting X position
            :param y1: the starting y position
            :param e: the keyword arguments you want to pass along to the line method
            :return: The line entity
            """
            return drw.line(start=(x1 * cm, y1 * cm), end=(x1 * cm, (y1 + l) * cm), **e)

        hour = 3600 * scale
        now = datetime.datetime.now()

        while current <= end_time:
            cx = horizontal_offset + offset + scale * (current - start_time).total_seconds()
            vticks.add(vline(cx, height_offset, 1, stroke=annotation_color))
            vticks.add(vline(cx + (hour * 3) / 4, height_offset, .25, stroke=annotation_color))
            vticks.add(vline(cx + (hour * 1) / 4, height_offset, .25, stroke=annotation_color))
            vticks.add(
                vline(cx + hour / 2, height_offset, 0.5, stroke=annotation_color))
            timetext = f"{current.hour}:{current.minute}:{current.second}"
            vticks.add(
                svgwrite.text.Text(timetext, x=[cx * cm], y=[(height_offset + 1) * cm],
                                   fill=annotation_color, font_size=10, text_anchor='middle'))
            current += delta

        for index, value in enumerate(self.data):
            for i in value[1]:
                if i in pos.keys():
                    v = pos[i]
                else:
                    pos[i] = ordinals[i]
                    v = pos[i]
                    block_groups[i] = blocks.add(
                        drw.g(id=f"block{v}", fill=self.chooseColor(i), stroke=self.chooseColor(i)))
                    block_groups[i].add(
                        drw.line(
                            start=((offset + horizontal_offset) * cm, (1 + height_offset + (.5 + v) * vscale) * cm),
                            end=(
                                (horizontal_offset + width + hour - offset) * cm,
                                (1 + height_offset + (0.5 + v) * vscale) * cm),
                            stroke=annotation_color,
                            stroke_dasharray="5", stroke_width=".2mm"))
                    f = list(filter(lambda x: i in x[1], self.data))
                    s = sum(map(lambda x: (x[0].time_end - x[0].time_start).total_seconds(), f))
                    total_strokes = sum(map(lambda x: x[0].keystrokes if x[0].keystrokes else 0, f))
                    l = labels.add(
                        svgwrite.text.Text("", x=[horizontal_offset * cm],
                                           y=[(v * vscale + vscale / 2.0 + height_offset + 1) * cm],
                                           fill=annotation_color))
                    l.add(svgwrite.text.TSpan(i))
                    addendum = f"{round(s, ndigits=2)} seconds"

                    l.add(
                        svgwrite.text.TSpan(addendum, dy=['1.2em'], x=[horizontal_offset * cm],
                                            font_size=10))
                    if show_titles:
                        addendum = f'{total_strokes} keypresses'
                        l.add(svgwrite.text.TSpan(addendum, dy=['1.2em'], x=[horizontal_offset * cm],
                                            font_size=10))
                start = v * vscale + height_offset + 1
                block_width = scale * (value[0].time_end - value[0].time_start).total_seconds()
                startx = (value[0].time_start - start_time).total_seconds() * scale + offset + horizontal_offset
                r = drw.rect(insert=(startx * cm, start * cm), size=(block_width * cm, vscale * cm),
                             ry=(vscale / 2.0) * cm, rx=0.1 * cm)
                r['class'] = i
                if show_titles:
                    addend = ""
                    if value[0].keystrokes:
                        addend += f"{value[0].keystrokes} keystrokes"
                    if value[0].mouse_motion:
                        addend += f'  {round(value[0].mouse_motion, ndigits=2)} pixels moved'
                    r.set_desc(title=f"{value[0].window_name} {addend}",
                               desc=f"{(value[0].time_end - value[0].time_start).total_seconds()} seconds")

                block_groups[i].add(r)

        chart.add(drw.line(start=(horizontal_offset * cm, (height_offset + height) * cm),
                           end=((width + horizontal_offset) * cm, (height_offset + height) * cm),
                           stroke=annotation_color))
        if self.data[0][0].time_start.date() == now.date():
            s = (now - start_time).total_seconds() * scale + horizontal_offset + offset
            line = chart.add(vline(s, height_offset + 1, height, stroke='#FF0000'))


def test():
    delta = datetime.timedelta(hours=1)
    chart = ChartPart("", [(models.WindowEvent(time_start=datetime.datetime.now() + delta * (i - 1),
                                               time_end=datetime.datetime.now() + delta * i),
                            ["hello" + str(j) for j in range(i + 1)]) for i in
                           range(1, 8)])
    drw = svgwrite.Drawing("Hello.svg")
    chart.draw(drw, 15, 10, 0)


def grid_iterator(n: int, columns: int, width: float, height: float) -> Iterable[tuple[float, float]]:
    """
    Convenience function to generate the appropriate grid positions

    :param n: The number of positions to iterate through
    :param columns: The number of columns to a row
    :param width: The width of the positions in centimeters
    :param height: The height increments in centimeters
    :return: The positions to place the charts on the grid
    """
    x = 0
    y = 0
    for i in range(n):
        yield x * width, height * y
        if x == columns - 1:
            x = 0
            y += 1
        else:
            x += 1


class Chart:
    parts: list[ChartPart]
    """
    The component sub charts.
    """
    columns: int
    """
    The number of columns that the chart will have
    """
    show_titles: bool
    """
    Whether or not to display the window names of the event.
    """

    def __init__(self, width: int, height: int, show_titles: bool = False):
        self.parts = []
        self.columns = 2
        self.height = height
        self.width = width
        self.show_titles = show_titles

    @staticmethod
    def from_data(data: list[list[tuple[models.WindowEvent, list[str]]]], width: int = 20, height: int = 10,
                  show_titles=False) -> Chart:
        """
        Convert a grouped list of data and labels into a series of charts of a given size.
        :param data: The list of lists of data
        :param width: The width in centimeters
        :param height: The height in centimeters
        :param show_titles: Add alt text to the data rectangles, this is a potentially unwanted information leak, so it is disabled by default
        :return: The resulting compound chart
        """
        c = Chart(width, height, show_titles)
        for day in reversed(data):
            c.parts.append(ChartPart(day[0][0].time_start.strftime("%m/%d/%y"), day))
        return c

    def draw(self, svg):

        mw = self.width * min(self.columns, len(self.parts))
        mh = self.height * max(len(self.parts) // self.columns, 1)
        for chart, pos in zip(self.parts, grid_iterator(len(self.parts), self.columns, self.width, self.height)):
            print(pos)
            # mw, mh = max(mw, pos[0]), max(mh, pos[1])
            chart.draw(svg, self.width, self.height, pos[1], pos[0] + 1 if pos[0] != 0 else 0,
                       show_titles=self.show_titles)
        svg['height'] = (mh) * cm
        svg['width'] = (mw + self.columns) * cm
        return svg
