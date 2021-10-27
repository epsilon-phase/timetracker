"""
Implements a mostly complete example of how one might use the timetracker report system to
generate charts and present them to the user.


"""

import svgwrite

from timetracker import models as models
from timetracker.report import NameTagger, OrMatcher, AndMatcher, ClassMatcher, process_events

from itertools import groupby
from typing import *
import cherrypy

from timetracker.common import Config
import timetracker

# Set up the matcher loading/saving function. This is where the 'magic' happens :)
Config.add_transform("matchers", input=lambda x: list(map(timetracker.report.from_json, x)),
                     output=lambda x: list(map(lambda y: y.as_json(), x)))


def group_by(iterable: Iterable[Any], func: Callable[[Any], Any]) -> list[list[Any]]:
    """
    An independent implementation of itertools.group_by that does the same thing but worse :)

    :param iterable: The iterable to group
    :param func: The function that returns the key by which to group them
    :return: a list of lists for each group, sorted by the keys
    """
    r = {}
    for i in iterable:
        key = func(i)
        if key not in r.keys():
            r[key] = []
        r[key].append(i)
    return [r[k] for k in sorted(r.keys())]


def example(width: int = 25, height: int = 20, show_titles: bool = False, max_charts: int = 6):
    """
    Generate the example chart configuration, this is from prior to json configurability, so it may not be a relevant example to imitate

    :param width: The width of the chart in centimeters
    :param height: The height of the chart in centimeters
    :param max_charts: The maximum number of charts to include in this. Having this set is
    :return: The svg document containing the charts
    """

    v = Config.get("matchers", None) is None
    m = Config.get("matchers", None)
    print(Config.get.cache_info())
    max_charts = int(max_charts)
    if not m:
        browsermatch = NameTagger('Firefox', ['browser'])
        web = OrMatcher([NameTagger(['Vulpine Club',
                                     'Mastodon'], ['social media', 'mastodon']),
                         NameTagger('Reddit', ['social media', 'reddit']),
                         NameTagger('Stack Overflow', ['documentation']),
                         AndMatcher([browsermatch, NameTagger('Documentation', [])], ['documentation']),
                         AndMatcher([browsermatch, NameTagger(['Gmail', 'Protonmail'], ['email', 'social media'])], []),
                         AndMatcher([browsermatch, NameTagger(['Indeed'], ['work search'])], []),
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
        m = [browsermatch, web, programming, gemcraft, telegram,
             NameTagger('Discord', ['social media', 'chat']), terminal,
             NameTagger('LyX', ['writing'])]
    if v:
        Config.set("matchers", m)
    r = process_events(m, models.session.query(models.WindowEvent))

    import timetracker.chart as chart
    eg = svgwrite.Drawing('example.svg')
    x = group_by(r, lambda z: z[0].date_of)
    if max_charts != 0:
        x = x[-max_charts:]
    cc = chart.Chart.from_data(x, height=height, width=width, show_titles=show_titles)

    cc.draw(eg)
    return eg


class Hoster:
    @cherrypy.expose
    def index(self, width: float = 25, height: float = 20, show_titles: bool = False, max_charts: int = 6):
        """
        This is the method that serves the chart up to the browser/whatever asks for it.
        :param width: The width of each chart in centimeters
        :param height: The height of each chart in centimeters
        :param show_titles: Whether or not to show the window titles in the chart's alt-texts
        :param max_charts: The maximum number of charts to display at once
        :return: The page
        """
        ex = example(width=float(width), height=float(height), show_titles=show_titles, max_charts=int(max_charts))
        script = ex.script(content="setTimeout(function(){location.reload();},30000);")
        script['type'] = 'text/javascript'
        ex.add(script)
        cherrypy.response.headers['no-cache'] = 1
        return str(ex.tostring())


def host():
    cherrypy.quickstart(Hoster(), '')


if __name__ == '__main__':
    host()
