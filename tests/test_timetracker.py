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
        self.assertEqual(r.date_of(), (t.year, t.month, t.day))
