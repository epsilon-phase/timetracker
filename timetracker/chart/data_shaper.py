"""
Provides a basic way to transform a data object into a shape that in, some way, represents it.
"""
import svgwrite

from timetracker.models import WindowEvent
from svgwrite import cm


class RectangleShaper:
    def shape(self, svg: svgwrite.Drawing, scale,
              horizontal_offset, start_time, vertpos, vscale, v_offset, w: WindowEvent,
              color
              ):
        start_y = vertpos * vscale + v_offset + 1
        start_x = (w.time_start - start_time).total_seconds() * scale + horizontal_offset
        width = scale * (w.time_end - w.time_start).total_seconds()
        r = svg.rect(insert=(start_x * cm, start_y * cm), size=(width * cm, vscale * cm),
                     ry=(vscale / 2.0) * cm, rx=0.1 * cm,
                     stroke=color, stroke_width=min(width / 2, 1))
        return r


class CircleShaper:
    def shape(self, svg: svgwrite.Drawing, scale,
              horizontal_offset, start_time, vertpos, vscale, v_offset, w: WindowEvent,
              color
              ):
        start_y = vertpos * vscale + v_offset + 1
        start_x = (w.time_start - start_time).total_seconds() * scale + horizontal_offset
        c_y = start_y + vscale / 2.0  # The center of the ellipse
        width = scale * (w.time_end - w.time_start).total_seconds()
        r_x = width / 2.0
        cx = start_x + r_x
        e = svg.ellipse(center=(cx * cm, c_y * cm), r=(r_x * cm, vscale / 2.0 * cm),
                        stroke=color)
        return e
