import timetracker
import timetracker.models as models
import re
from typing import *


class Matcher:
    """
    Base class for the various matchers.

    Provides some useful functions to build upon.
    """

    def match_string(self, matcher, string) -> bool:
        """
        Handle matching the string with whatever the matcher is.
        :param matcher: The matcher object, a list of regexes, strings, etc.
        :param string: The string to match against
        :return: If the string matches
        """
        if isinstance(matcher, list):
            return any(map(lambda x: self.match_string(x, string), matcher))
        elif isinstance(matcher, re.Pattern):
            return matcher.match(string)
        else:
            m = matcher if self.case_sensitive else matcher.lower()
            s = string if self.case_sensitive else string.lower()
            return m in s

    def as_json(self, t: str) -> dict:
        m = self.matcher
        if issubclass(type(self.matcher[0]), Matcher):
            m = list(map(lambda x: x.as_json(), m))
        else:
            r = []
            for i, v in enumerate(m):
                if isinstance(v, re.Pattern):
                    r.append({'type': 'regex', 'value': v.pattern})
                else:
                    r.append(v)
            m = r
        return {'type': t,
                'matcher': m,
                'tags': self.tags if self.tags else []}


class NameTagger(Matcher):
    """
    Provides matching on the :py:attr:`timetracker.models.WindowEvent.window_name`. by the window's name

    """
    __slots__ = ['matcher', 'tags', 'case_sensitive']
    matcher: Union[str, re.Pattern]
    tags: list[str]

    def __init__(self, match: Union[str, re.Pattern], tags: list[str], case_sensitive: bool = False):
        super().__init__()
        self.matcher = match
        self.tags = list(filter(lambda x: len(x) > 0, tags))
        self.case_sensitive = case_sensitive

    def matches(self, window_event: models.WindowEvent) -> tuple[bool, Optional[list[str]]]:
        wn = window_event.window_name.lower(
        ) if not self.case_sensitive else window_event.window_name
        is_match = self.match_string(self.matcher, wn)
        return is_match, self.tags

    def as_json(self, name='name'):
        return super().as_json('name')

    def to_form(self):
        el_id = id(self)
        return f'Matches: <input id="{el_id}" type="text" value="{self.matchers}"/>'


class ClassMatcher(Matcher):
    matcher: Union[str, re.Pattern]

    tags: Optional[list[str]]

    def __init__(self, matcher: Union[str, re.Pattern], tags: Optional[list[str]], case_sensitive=False):
        super().__init__()
        self.matcher = matcher
        self.tags = tags
        self.case_sensitive = case_sensitive

    def matches(self, window_event: models.WindowEvent) -> tuple[bool, Optional[list[str]]]:
        is_match = any(map(lambda y: self.match_string(
            self.matcher, y.name), window_event.classes))
        return is_match, self.tags

    def as_json(self, name='class'):
        return super().as_json('class')


class CompoundMatcher(Matcher):
    """
    Base class for match classes where the outcome is determined by other kinds of sub matchers 
    """
    pass


class AndMatcher(CompoundMatcher):
    """
    Matches against a group of matchers, only matching if every submatcher matches.

    Concatenates subtags.
    """
    __slots__ = ['matcher', 'tags']
    tags: Optional[list[str]]

    def __init__(self, matchers, tags):
        self.tags = tags if tags else []
        self.matcher = matchers

    def matches(self, window_event: models.WindowEvent) -> tuple[bool, Optional[list[str]]]:
        l = list(map(lambda x: x.matches(window_event), self.matcher))
        t = self.tags.copy()

        for (matches, tags) in l:
            if not matches or tags is None:
                continue
            # Take the union of all subordinate matching tags.
            t.extend(tags)
        return all(map(lambda x: x[0], l)), t

    def as_json(self, name='and'):
        return super().as_json('and')


class OrMatcher(CompoundMatcher):
    """
    Matches when any of the submatchers match

    Concatenates submatcher tags.
    """
    # __slots__ = ['matcher', 'tags']
    tags: list[str]

    def __init__(self, matchers, tags):
        self.matcher = matchers
        self.tags = tags if tags else []

    def matches(self, event: models.WindowEvent):
        t = self.tags.copy()
        evtmatch = list(map(lambda x: (x.matches(event)), self.matcher))
        for (matches, tags) in filter(lambda x: x is not None, evtmatch):
            if matches:
                t.extend(tags if tags else [])
        return any(map(lambda x: x and x[0], evtmatch)), t

    def as_json(self, name='or'):
        return super().as_json('or')


class NotMatcher(CompoundMatcher):
    """
    Matches a window that does not contain any of the submatchers.
    This is probably most useful in combination with other compound matchers to add additional
    discrimination ability
    """

    # __slots__ = ['matcher', 'tags']

    def __init__(self, matches, tags):
        """

        :param matches: The constituent matchers that should not match
        :param tags: The tags produced on a successful match
        """
        self.matcher = matches or []
        self.tags = tags or []

    def matches(self, event) -> tuple[bool, list[str]]:
        evtmatch = list(map(lambda x: (x.matches(event)), self.matcher))
        if any(evtmatch):
            return False, self.tags
        else:
            return True, self.tags

    def as_json(self, name='not'):
        return super().as_json('not')


__types = {'or': OrMatcher, 'and': AndMatcher,
           'name': NameTagger, 'class': ClassMatcher, 'not': NotMatcher}


def from_json(obj: dict) -> Matcher:
    match_type = obj['type'] or 'name'
    if match_type not in __types.keys():
        raise f"Invalid match type: {match_type}"
    MatcherType = __types[match_type]
    if issubclass(MatcherType, CompoundMatcher):
        return MatcherType(list(map(from_json, obj['matcher'])), obj['tags'] if 'tags' in obj.keys() else [])
    return MatcherType(
        [re.compile(i['value']) if isinstance(i, dict) else i for i in obj['matcher']] if isinstance(obj['matcher'],
                                                                                                     list) else obj[
            'matcher'],
        obj['tags'] if 'tags' in obj.keys() else [])


def process_events(matchers, events: Iterable[models.WindowEvent]) -> list[tuple[models.WindowEvent, list[str]]]:
    r = []
    for e in events:
        l = []
        for m in matchers:
            matches, tags = m.matches(e)
            if matches and tags:
                l.extend(tags)
        if not l:
            l.append('unlabelled')
        r.append((e, l))
    return r


class TagPrioritizer:
    """
    A structure to replace any number of tags with the most 'important' one.

    If no tags match it returns the existing list unmodified.
    """

    def __init__(self):
        """
        Initialize the tagprioritizer
        """
        self.priorities: dict[str, int] = {}

    def set_priority(self, tag: str, pr: Optional[int]):
        self.priorities[tag] = pr

    def handle_tags(self, tags: list[str]):
        l = tags
        if any(lambda x: x in self.priorities.keys(), tags):
            l = [max(tags, key=lambda x: self.priorities[x]
                     if x in self.priorities.keys() else 0)]
        return l


class TagSupercedes:
    """
    A tag processor that, in the presence of a specific tag, removes a number of other tags from the list.

    If the tag is not present the list of tags is not modified.
    """

    supercedes: list[str]
    tag: str

    def __init__(self, tag: str, supercedes: list[str]):
        self.tag = tag
        self.supercedes = supercedes

    def handle_tags(self, tags: list[str]) -> list[str]:
        if self.tag in tags:
            return [x for x in tags if x not in self.supercedes]
        return tags
