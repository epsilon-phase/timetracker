import svgwrite

import timetracker.models as models
import re
from typing import *


class NameTagger:
    __slots__ = ['matcher', 'tags']
    matcher: Union[str, re.Pattern]
    tags: list[str]

    def __init__(self, match: Union[str, re.Pattern], tags: list[str]):
        self.matcher = match
        self.tags = tags

    def matches(self, window_event: models.WindowEvent) -> tuple[bool, Optional[list[str]]]:
        print(window_event.window_name)
        if isinstance(self.matcher, re.Pattern):
            print("im a regex")
            if self.matcher.match(window_event.window_name):
                return True, self.tags.copy()
        else:
            if self.matcher in window_event.window_name:
                return True, self.tags.copy()
        return False, self.tags.copy()


class ClassMatcher:
    matcher: Union[str, re.Pattern]
    tags: Optional[list[str]]

    def __init__(self, matcher: Union[str, re.Pattern], tags: Optional[list[str]]):
        self.matcher = matcher
        self.tags = tags

    def matches(self, window_event: models.WindowEvent) -> tuple[bool, Optional[list[str]]]:
        if isinstance(self.matcher, re.Pattern):
            m: re.Pattern = self.matcher
            for wclass in window_event.classes:
                if m.match(wclass.name):
                    return True, self.tags
        else:
            for wclass in window_event.classes:
                if self.matcher in wclass.name:
                    return True, self.tags


class AndMatcher:
    __slots__ = ['matchers', 'tags']
    tags: Optional[list[str]]

    def __init__(self, matchers, tags):
        if tags is None:
            self.tags = []
        self.matchers = matchers

    def matches(self, window_event: models.WindowEvent) -> tuple[bool, Optional[list[str]]]:
        l = list(map(lambda x: x.matches(window_event), self.matchers))
        t = self.tags.copy()

        for (matches, tags) in l:
            if not matches or tags is None:
                continue
            # Take the union of all submatcher tags.
            t.extend(tags)
        return all(map(lambda x: x[0], l)), t


class OrMatcher:
    __slots__ = ['matchers', 'tags']
    tags: list[str]

    def __init__(self, matchers, tags):
        self.matchers = matchers
        self.tags = tags if tags else []

    def matches(self, event: models.WindowEvent):
        t = self.tags.copy()
        evtmatch = list(map(lambda x: (x.matches(event)), self.matchers))
        print(evtmatch)
        for (matches,tags) in filter(lambda x:x is not None, evtmatch):
            if matches:
                t.extend(tags if tags else [])
        return any(map(lambda x: x and x[0], evtmatch)), t


def process_events(matchers, events: Iterable[models.WindowEvent]):
    r = []
    for e in events:
        l = []
        for m in matchers:
            matches, tags = m.matches(e)
            if matches and tags:
                l.extend(tags)
        r.append((e, l))
    return r


def example():
    browsermatch = NameTagger('Firefox', ['browser'])
    vulpine = NameTagger('Vulpine Club', ['social media'])
    programming = OrMatcher([NameTagger('.py', ['python']),
                             NameTagger('.lisp', ['lisp', 'common lisp']),
                             ClassMatcher('jetbrains', [])], ['programming'])

    gemcraft = NameTagger('GemCraft', ['Games'])
    telegram = NameTagger('Telegram', ['social media', 'chat'])
    m = [browsermatch, vulpine, programming, gemcraft, telegram]
    r = process_events(m, models.session.query(models.WindowEvent))
    import timetracker.chart as chart
    c = chart.ChartPart("Thingy", r)
    eg = svgwrite.Drawing('example.svg')
    c.draw(eg, 40, 10, 0)
