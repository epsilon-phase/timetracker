import datetime
import random

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
        :returns: The hex of the color.
        """
        if tag not in self.tagindex.keys():
            self.tagindex[tag] = hash(tag)
        return self.color_chooser.choose(self.tagindex[tag])

    def draw(self, drw: svgwrite.Drawing, width: float, height: float, height_offset, horizontal_offset,
             add_titles: bool = False) -> None:
        """
        Draw the chart
        :param drw: The svg drawing
        :param width: The width of the chart part in centimeters
        :param height: The height of the chart part in centimeters
        :param height_offset: The vertical offset in centimeters
        :param horizontal_offset: The horizontal offset in centimeters
        :param add_titles: Add titles to the blocks, providing mouseovers displaying the window titles.
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
        vline = lambda x1, y1, l, **e: drw.line(start=(x1 * cm, y1 * cm), end=(x1 * cm, (y1 + l) * cm), **e)
        hour = 3600 * scale
        while current <= end_time:
            cx = horizontal_offset + offset + scale * (current - start_time).total_seconds()
            vticks.add(vline(cx, height_offset, 1, stroke=annotation_color))
            vticks.add(vline(cx + (hour * 3) / 4, height_offset, .25, stroke=annotation_color))
            vticks.add(vline(cx + (hour * 1) / 4, height_offset, .25, stroke=annotation_color))
            vticks.add(
                vline(cx + hour / 2, height_offset, 0.5, stroke=annotation_color))
            timetext = f"{current.hour}:{current.minute}:{current.second}"
            textoffset = -0.5 if current != start_time else 0.0
            vticks.add(
                svgwrite.text.Text(timetext, x=[(cx + textoffset) * cm], y=[(height_offset + 1) * cm],
                                   fill=annotation_color))
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
                    f = filter(lambda x: i in x[1], self.data)
                    s = sum(map(lambda x: (x[0].time_end - x[0].time_start).total_seconds(), f))
                    l = labels.add(
                        svgwrite.text.Text("", x=[horizontal_offset * cm],
                                           y=[(v * vscale + vscale / 2.0 + height_offset + 1) * cm],
                                           fill=annotation_color))
                    l.add(svgwrite.text.TSpan(i))
                    l.add(
                        svgwrite.text.TSpan(f"{round(s, ndigits=2)} seconds", dy=['1.2em'], x=[horizontal_offset * cm]))
                start = v * vscale + height_offset + 1
                block_width = scale * (value[0].time_end - value[0].time_start).total_seconds()
                startx = (value[0].time_start - start_time).total_seconds() * scale + offset + horizontal_offset
                r = drw.rect(insert=(startx * cm, start * cm), size=(block_width * cm, vscale * cm),
                             ry=(vscale / 2.0) * cm, rx=0.1 * cm)
                if add_titles:
                    r.set_desc(title=value[0].window_name,
                               desc=f"{(value[0].time_end - value[0].time_start).total_seconds()} seconds")
                block_groups[i].add(r)

        chart.add(drw.line(start=(horizontal_offset * cm, (height_offset + height) * cm),
                           end=((width + horizontal_offset) * cm, (height_offset + height) * cm),
                           stroke=annotation_color))

        drw.save()


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
    columns: int

    def __init__(self):
        self.parts = []
        self.columns = 2

    @staticmethod
    def from_data(data: list[list[tuple[models.WindowEvent, list[str]]]]):
        c = Chart()
        for day in data:
            c.parts.append(ChartPart(day[0][0].time_start.strftime("%d/%m/%y"), day))
        return c

    def draw(self, svg):

        mw = 0
        mh = 0
        for chart, pos in zip(self.parts, grid_iterator(len(self.parts), self.columns, 40, 30)):
            print(pos)
            mw, mh = max(mw, pos[0]), max(mh, pos[1])
            chart.draw(svg, 40, 30, pos[1], pos[0] + 1 if pos[0] != 0 else 0)
        svg['height'] = (mh+30) * cm
        svg['width'] = (mw+40) * cm
        return svg
