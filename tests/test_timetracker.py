import timetracker.configurable
from timetracker import __version__


def test_version():
    assert __version__ == '0.1.0'


from unittest import TestCase


class UtilityTests(TestCase):
    def test_substring(self):
        from timetracker.util.substrings import longest_common_substring
        self.assertEqual(longest_common_substring('aaa', 'baabaaaab'), (2, 0, 6))


class ModelTests(TestCase):
    def test_date_of(self):
        from timetracker.models import WindowEvent
        import datetime
        r = WindowEvent(time_start=datetime.datetime.now())
        t = datetime.datetime.now()
        self.assertEqual(r.date_of, (t.year, t.month, t.day))


class ChartTests(TestCase):
    def test_chart(self):
        import timetracker.chart
        timetracker.chart.test()

    def test_grid_iterator(self):
        from timetracker.chart import grid_iterator
        l = list(grid_iterator(5, 3, 10, 10))
        self.assertEqual(l, [(0, 0), (10, 0), (20, 0), (0, 10), (10, 10)])


class ConfigurableTest(TestCase):
    def test_config_basic(self):
        c = timetracker.configurable.ConfigStore(None)
        c.set("hello", 2)
        self.assertEqual(c.get('hello', None), 2)

    def test_config_transformer(self):
        c = timetracker.configurable.ConfigStore(None)
        c.add_transform("thing", lambda x: x + 2, lambda x: x - 2)
        c.set('thing', 2)
        self.assertEqual(c.get('thing', None), 2)
        self.assertEqual(c.data['thing'], 0)
