from __future__ import annotations
import subprocess
from typing import *
import datetime
import time

from timetracker.models import engine, session, Base, WindowClass, WindowEvent, session_object

_IDLE_TIMES = 30
_SAMPLE_INTERVAL = 10

Base.metadata.create_all(engine)


def GetEventClasses(wmclass: str) -> WindowClass:
    wclass = session.query(WindowClass).where(WindowClass.name == wmclass)
    if wclass is None:
        wclass = WindowClass(name=wmclass)
    else:
        for i in wclass:
            return i
        wclass = WindowClass(name=wmclass)
    return wclass


def GetActiveWindowTitle(last: Optional[WindowEvent]) -> WindowEvent:
    v = subprocess.Popen(["xprop",
                          "-root",
                          "_NET_ACTIVE_WINDOW"],
                         stdout=subprocess.PIPE).communicate()[0].strip().split()[-1].decode('utf-8')
    name = subprocess.Popen([b"xprop", b"-id",
                             v, b"WM_NAME"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE) \
               .communicate()[0].strip().split(b'"', 1)[-1][:-1].decode('utf8')
    wclass = subprocess.Popen(['xprop', '-id', v, 'WM_CLASS'], stdout=subprocess.PIPE).communicate()[0].split(b'"', 1)[
        -1].decode('utf-8')
    wclass = set(map(lambda x: x.replace('"', '').strip(), wclass.split(',')))
    wclass = list(map(lambda x: GetEventClasses(x), wclass))
    now = datetime.datetime.now()
    later = now + datetime.timedelta(seconds=_SAMPLE_INTERVAL)
    if last and last.window_id == int(v, base=16) and last.window_name == name:
        last.time_end = later
        return last
    result = WindowEvent(window_name=name, window_id=int(v, base=16),
                         time_start=now,
                         time_end=later, session=session_object,
                         classes=wclass)
    return result


def GetMouseLocation() -> tuple[int, int]:
    raw = subprocess.Popen(['xdotool', 'getmouselocation'],
                           stdout=subprocess.PIPE).communicate()[0].strip().decode('utf-8')
    raw = raw.split(' ')[0:2]
    return tuple(map(lambda x: int(x.split(':')[1]), raw))


def track():
    last = None
    c = 0
    last_pos = GetMouseLocation()
    while True:
        current_pos = GetMouseLocation()
        if current_pos == last_pos:
            c += 1
        else:
            c = 0
            last_pos = current_pos
        if c >= _IDLE_TIMES:
            print(f"No movement for {_SAMPLE_INTERVAL * c} seconds, pausing sampling until activity")
            # Forget the former activity, we'll have to note it
            # individually later anyway
            last = None
            time.sleep(_SAMPLE_INTERVAL)
            continue
        current = GetActiveWindowTitle(last)
        if current:
            session.add(current)
            if last != current:
                print("new event")
                last = current
        session.commit()
        time.sleep(_SAMPLE_INTERVAL)
