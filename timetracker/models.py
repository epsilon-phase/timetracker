from __future__ import annotations
import datetime
import time
import os
from functools import cached_property

import sqlalchemy.orm
from sqlalchemy import create_engine, Column, Integer, DateTime as DT, ForeignKey, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, scoped_session
from sqlalchemy.pool import SingletonThreadPool

backend = 'sqlite'
tail, prefix = '', ''
try:
    import pysqlcipher3

    print("Encryption is available")
    backend += '+pysqlcipher'
    key = os.getenv('TIMETRACKER_PASSWORD', None)
    if key:
        print("Key found, using encryption")
        encryption = os.getenv("TIMETRACKER_CIPHER", "aes-256")
        kdf_iter = os.getenv("TIMETRACKER_KDF", "64000")
        tail = f"?cipher={encryption}&kdf_iter={kdf_iter}"
        prefix = f"{key}@/"
except ImportError:
    pass

engine = create_engine(f'{backend}://{prefix}/timetracker.db{tail}')
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


class SessionObject(Base):
    """
    Timetracker session
    """
    __tablename__ = 'Session'
    id = Column(Integer, primary_key=True)
    date = Column(DT)
    "The time when the session started"
    events = relationship('WindowEvent', back_populates='session')

    @staticmethod
    def collect_within_time(ses, td: datetime.timedelta) -> list[SessionObject]:
        return ses.query(SessionObject).where(SessionObject.date >= datetime.datetime.now() - td)


class WindowClass(Base):
    "The classes of the windows seen before"
    __tablename__ = 'WindowClass'
    id = Column(Integer, primary_key=True)
    name = Column(Integer, unique=True)
    events = relationship('WindowEvent', secondary='EventClass', backref='classes')


class EventClass(Base):
    "The association between `WindowEvent` and `WindowClass`"
    __tablename__ = 'EventClass'
    event_id = Column(Integer, ForeignKey('WindowEvent.id'), primary_key=True)
    class_id = Column(Integer, ForeignKey('WindowClass.id'), primary_key=True)


class WindowEvent(Base):
    """
    A single measurement of usage duration of a single window.
    """
    __tablename__ = 'WindowEvent'
    id = Column(Integer, primary_key=True)
    "The id"
    session_id = Column(Integer, ForeignKey('Session.id'), nullable=False)
    "The id of the session this event was recorded during. used anywhere yet."
    window_name = Column(String)
    "The title of the focused window during the measurement"
    window_id = Column(Integer)
    "The id of the window during the measurement"
    time_start = Column(DT)
    "The start of the measurement interval"
    time_end = Column(DT)
    "The end of the measuremetn interval"
    session = relationship('SessionObject', back_populates='events')
    "Relationship with the session"
    classes: list[WindowClass]
    "The list of associated classes."
    mouse_motion = Column(Float, default=None)
    "The number of pixels that the mouse pointer has traversed"
    keystrokes = Column(Integer, default=None)
    "The number of keypresses recorded"

    @cached_property
    def date_of(self) -> tuple[int, int, int]:
        """
        Get the date component of the thing.

        :return: A tuple containing, the year, the month, and the day
        """
        year = self.time_start.year
        month = self.time_start.month
        day = self.time_start.day
        return year, month, day


current_time = time.monotonic_ns()


def session_object():
    for i in session.query(SessionObject).where(SessionObject.id == current_time):
        return i
    return SessionObject(id=current_time)
