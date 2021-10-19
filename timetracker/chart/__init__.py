import datetime
import random

import svgwrite
from .. import models
from svgwrite import cm, mm


class ChartPart:
    data: list[tuple[models.WindowEvent, list[str]]]
    range: datetime.timedelta
    range_start: datetime.datetime
    range_end: datetime.datetime
    title: str

    def __init__(self, title: str, data: list[tuple[models.WindowEvent, list[str]]]):
        self.title = title
        self.data = data.copy()
        self.data.sort(key=lambda x: x[0].time_end)
        self.data.sort(key=lambda x: x[0].time_start)
        self.range = data[-1][0].time_end - data[0][0].time_start
        self.range_start = data[0][0].time_start
        self.range_end = data[-1][0].time_end
        self.tagindex = {}

    def chooseColor(self, tag: str) -> str:
        from . import color_chooser
        if tag not in self.tagindex.keys():
            self.tagindex[tag] = len(self.tagindex)
        return color_chooser.monokai.choose(self.tagindex[tag])

    def draw(self, drw: svgwrite.Drawing, width: float, height: float, height_offset) -> None:
        chart: svgwrite.drawing.SVG = drw.add(drw.g())
        vticks: svgwrite.drawing.SVG = chart.add(drw.g(id="vticks"))
        blocks: svgwrite.drawing.SVG = chart.add(drw.g(id='blocks'))
        labels: svgwrite.drawing.SVG = chart.add(drw.g(id='labels'))
        offset = 2
        delta = datetime.timedelta(hours=1)
        scale = (width - offset) / self.range.total_seconds()
        vscale = (height - 1) / max(map(lambda x: 1.0 * len(x[1]) + 1, self.data))
        current = self.range_start
        pos = {}
        while current < self.range_end:
            print("Ongoing")

            cx = scale * (current - self.range_start).total_seconds()
            vticks.add(
                drw.line(start=(cx * cm, height_offset * cm), end=(cx * cm, (height_offset + 1) * cm), stroke='black'))
            timetext = f"{current.hour}:{current.minute}:{current.second}"

            vticks.add(svgwrite.text.Text(timetext, x=[cx * cm], y=[(height_offset + 1) * cm], stroke='black'))
            for index, value in enumerate(self.data):
                for i in value[1]:
                    if i in pos.keys():
                        v = pos[i]
                    else:
                        pos[i] = len(pos)
                        v = pos[i]
                        labels.add(
                            svgwrite.text.Text(i, x=[0 * cm], y=[(v * vscale + vscale / 2.0 + height_offset + 1) * cm]))
                    start = v * vscale + height_offset + 1
                    end = vscale
                    block_width = scale * (value[0].time_end - value[0].time_start).total_seconds()
                    startx = (value[0].time_start - self.range_start).total_seconds() * scale + offset
                    endx = (value[0].time_end - self.range_start).total_seconds() * scale
                    color = self.chooseColor(i)
                    blocks.add(
                        drw.rect(insert=(startx * cm, start * cm), size=(block_width * cm, vscale * cm), fill=color))
            current += delta

        drw.save()


def test():
    delta = datetime.timedelta(hours=1)
    chart = ChartPart("", [(models.WindowEvent(time_start=datetime.datetime.now() + delta * (i - 1),
                                               time_end=datetime.datetime.now() + delta * i),
                            ["hello" + str(j) for j in range(i + 1)]) for i in
                           range(1, 8)])
    drw = svgwrite.Drawing("Hello.svg")
    chart.draw(drw, 15, 10, 0)
