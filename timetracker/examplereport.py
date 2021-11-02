"""
Implements a mostly complete example of how one might use the timetracker report system to
generate charts and present them to the user.


"""
import json
import os
from functools import lru_cache
import timetracker.chart as chart
import timetracker.chart.data_colorer as data_colorer

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


def example(width: int = 25, height: int = 20, show_titles: bool = False, max_charts: int = 6, patterns=None):
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
    if patterns:
        m = patterns
    if not m:
        browsermatch = NameTagger(['Firefox', 'Google Chrome',
                                   'Chromium', 'Vivaldi'], ['browser'])
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


    eg = svgwrite.Drawing('example.svg')
    x = group_by(r, lambda z: z[0].date_of)
    if max_charts != 0:
        x = x[-max_charts:]
    cc = chart.Chart.from_data(x, height=height, width=width, show_titles=show_titles)

    cc.draw(eg)
    return eg


class Hoster:
    @cherrypy.expose
    def svg(self, width: float = 25, height: float = 20, show_titles: bool = False, max_charts: int = 6,
              patterns=None,id=None):
        """
        This is the method that serves the chart up to the browser/whatever asks for it.
        :param width: The width of each chart in centimeters
        :param height: The height of each chart in centimeters
        :param show_titles: Whether or not to show the window titles in the chart's alt-texts
        :param max_charts: The maximum number of charts to display at once
        :param patterns: The json-encoded reporting configuration to display.
        :return: The page
        """
        print(f"patterns:{type(patterns)}")

        @lru_cache(10)
        def load_patterns(s: str):
            return list(timetracker.report.from_json(i) for i in json.loads(s))

        if patterns:
            patterns = load_patterns(patterns)
        ex = example(width=float(width), height=float(height), show_titles=show_titles, max_charts=int(max_charts),
                     patterns=patterns)
        script = ex.script(content="setTimeout(function(){location.reload();},30000);")
        script['type'] = 'text/javascript'
        # ex.add(script)
        cherrypy.response.headers['no-cache'] = 1
        cherrypy.response.headers['Content-Type'] = 'image/svg+xml'
        return bytes(ex.tostring(), 'utf-8')

    @cherrypy.expose
    def index(self):
        import json
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../assets/config.html")) as f:
            k = f.read().replace('%%REPLACE%%', json.dumps(Config.data['matchers']))
            return k


def host():
    cherrypy.quickstart(Hoster(), '',
                        {
                            'global': {'server.socket_host': '127.0.0.1',
                                       'server.socket_port': 8080,
                                       'server.thread_pool': 8,
                                       'tools.gzip.on': True},
                            '/assets': {
                                'tools.staticdir.on': True,
                                'tools.staticdir.dir': os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                                    "../assets"),
                            }
                        })


if __name__ == '__main__':
    host()
