import timetracker.models as models
import re
from typing import *


class Matcher:

    def match_string(self, matcher, string) -> bool:
        if isinstance(matcher, list):
            return any(map(lambda x: self.match_string(x, string), matcher))
        elif isinstance(matcher, re.Pattern):
            return matcher.match(string)
        else:
            m = matcher if self.case_sensitive else matcher.lower()
            s = string if self.case_sensitive else string.lower()
            return m in s


class NameTagger(Matcher):
    __slots__ = ['matcher', 'tags', 'case_sensitive']
    matcher: Union[str, re.Pattern]
    tags: list[str]

    def __init__(self, match: Union[str, re.Pattern], tags: list[str], case_sensitive: bool = False):
        self.matcher = match
        self.tags = tags
        self.case_sensitive = case_sensitive

    def matches(self, window_event: models.WindowEvent) -> tuple[bool, Optional[list[str]]]:
        wn = window_event.window_name.lower() if not self.case_sensitive else window_event.window_name
        is_match = self.match_string(self.matcher, wn)
        return is_match, self.tags


class ClassMatcher(Matcher):
    matcher: Union[str, re.Pattern]
    tags: Optional[list[str]]

    def __init__(self, matcher: Union[str, re.Pattern], tags: Optional[list[str]], case_sensitive=False):
        self.matcher = matcher
        self.tags = tags
        self.case_sensitive = case_sensitive

    def matches(self, window_event: models.WindowEvent) -> tuple[bool, Optional[list[str]]]:
        is_match = any(map(lambda y: self.match_string(self.matcher, y.name), window_event.classes))
        return is_match, self.tags


class AndMatcher:
    __slots__ = ['matchers', 'tags']
    tags: Optional[list[str]]

    def __init__(self, matchers, tags):
        self.tags = tags if tags else []
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
        for (matches, tags) in filter(lambda x: x is not None, evtmatch):
            if matches:
                t.extend(tags if tags else [])
        return any(map(lambda x: x and x[0], evtmatch)), t


__types = {'or': OrMatcher, 'and': AndMatcher, 'name': NameTagger, 'class': ClassMatcher}


def process_events(matchers, events: Iterable[models.WindowEvent]) -> list[tuple[models.WindowEvent, list[str]]]:
    r = []
    for e in events:
        l = []
        for m in matchers:
            matches, tags = m.matches(e)
            if matches and tags:
                l.extend(tags)
        r.append((e, l))
    return r
