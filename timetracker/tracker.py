from __future__ import annotations
import subprocess
import sys
from typing import *
import datetime
import time

from timetracker.models import engine, session, Base, WindowClass, WindowEvent, session_object
import timetracker.models as models

from timetracker import Config

import libinput

_IDLE_TIMES = 30
_SAMPLE_INTERVAL: float = Config.get("sample_interval", 10)

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
    encoding = sys.getfilesystemencoding()
    v = subprocess.Popen(["xprop",
                          "-root",
                          "_NET_ACTIVE_WINDOW"],
                         stdout=subprocess.PIPE).communicate()[0].strip().split()[-1].decode(sys.getdefaultencoding())
    name = subprocess.Popen([b"xprop", b"-id",
                             v, b"WM_NAME"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE) \
               .communicate()[0].strip().split(b'"', 1)[-1][:-1].decode()
    wclass = subprocess.Popen(['xprop', '-id', v, 'WM_CLASS'], stdout=subprocess.PIPE).communicate()[0].split(b'"', 1)[
        -1].decode('utf-8')
    wclass = set(map(lambda x: x.replace('"', '').strip(), wclass.split(',')))
    wclass = list(map(lambda x: GetEventClasses(x), wclass))
    now = datetime.datetime.now()
    later = now + datetime.timedelta(seconds=_SAMPLE_INTERVAL)
    if last and last.window_id == int(v, base=16) and last.window_name == name:
        if (now - last.time_end).total_seconds() <= 3 * _SAMPLE_INTERVAL:
            last.time_end = later
            return last

    result = WindowEvent(window_name=name, window_id=int(v, base=16),
                         time_start=now,
                         time_end=later, session=models.session_object(),
                         classes=wclass)
    return result


def GetMouseLocation() -> tuple[int, int]:
    raw = subprocess.Popen(['xdotool', 'getmouselocation'],
                           stdout=subprocess.PIPE).communicate()[0].strip().decode('utf-8')
    raw = raw.split(' ')[0:2]
    return tuple(map(lambda x: int(x.split(':')[1]), raw))


def track():
    """
    Start tracking the window usage of the system.
    :return: None
    """
    last = None
    c = 0
    context = libinput.LibInput(context_type=libinput.constant.ContextType.UDEV)
    context.assign_seat('seat0')
    event = context.events
    last_time = datetime.datetime.now()-datetime.timedelta(seconds=20)
    for i in event:
        if i.type.is_pointer() or i.type.is_keyboard:
            elapsed = (datetime.datetime.now() - last_time).total_seconds()
            if elapsed >= _SAMPLE_INTERVAL * 3 and last:
                print(f"No movement for {elapsed} seconds")
                last = None
            # Debounce the command invocation, as this could get very expensive if it is called on each event
            if elapsed >= _SAMPLE_INTERVAL:
                current = GetActiveWindowTitle(last)
                session.add(current)
                last_time = datetime.datetime.now()
                session.commit()
                if last != current:
                    print("New event")
                    last = current
                else:
                    print("old event")