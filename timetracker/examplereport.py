import svgwrite

from timetracker import models as models
from timetracker.report import NameTagger, OrMatcher, AndMatcher, ClassMatcher, process_events
from typing import *


def group_by(iter: Iterable[Any], func: Callable[[Any], Any]) -> list[list[Any]]:
    r = {}
    for i in iter:
        key = func(i)
        if key not in r.keys():
            r[key] = []
        r[key].append(i)
    return [r[k] for k in sorted(r.keys())]


def example():
    browsermatch = NameTagger('Firefox', ['browser'])
    web = OrMatcher([NameTagger(['Vulpine Club',
                                 'Mastodon'], ['social media', 'mastodon']),
                     NameTagger('Reddit', ['social media', 'reddit']),
                     NameTagger('Stack Overflow', ['documentation']),
                     AndMatcher([browsermatch, NameTagger('Documentation', [])], ['documentation']),
                     NameTagger('— Python', ['documentation', 'python'])], [])
    programming = OrMatcher([NameTagger('.py', ['python']),
                             AndMatcher([NameTagger('timetracker', ['timetracker']),
                                         NameTagger('.py', [])], []),
                             NameTagger('.lisp', ['lisp', 'common lisp']),
                             NameTagger('JuCi++', ['c++']),
                             ClassMatcher('jetbrains', ['pycharm'])], ['programming'])

    gemcraft = NameTagger('GemCraft', ['Games'])
    telegram = NameTagger('Telegram', ['social media', 'chat'])
    terminal = ClassMatcher('kitty', ['terminal'])
    m = [browsermatch, web, programming, gemcraft, telegram, NameTagger('Discord', ['social media', 'chat']), terminal]
    r = process_events(m, models.session.query(models.WindowEvent))

    import timetracker.chart as chart
    eg = svgwrite.Drawing('example.svg')
    offset = 0
    x = group_by(r, lambda x: x[0].date_of())
    from svgwrite import cm
    for day, pos in zip(x, chart.grid_iterator(len(x), 2, 40, 30)):
        print(pos)
        print(day[0][0].date_of())
        c = chart.ChartPart(day[0][0].time_start.strftime("%d/%m/%y"), day)
        c.draw(eg, 40, 30, pos[1], pos[0] + 1 if pos[0] != 0 else 0)
        offset += 30
    eg['height'] = f"{30 * len(x)}cm"
    eg['width'] = '80cm'
    eg['style'] = 'background-color:#2e2e2e'
    eg.save()
