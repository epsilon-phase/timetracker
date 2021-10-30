from __future__ import annotations

import datetime
import os
import time
from functools import cached_property

import sqlalchemy.orm
from sqlalchemy import create_engine, Column, Integer, DateTime as DT, ForeignKey, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, scoped_session

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
    event_id = Column(Integer, ForeignKey('WindowEvent.id', ondelete='cascade'), primary_key=True)
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

    def should_merge(self, b: WindowEvent, threshold: int):
        return b.window_name == self.window_name and \
               (b.time_start - self.time_end).total_seconds() < threshold

    def merge(self, b: WindowEvent, threshold: int = 10):
        self.time_end = b.time_end
        self.keystrokes = (self.keystrokes or 0) + (b.keystrokes or 0)
        self.mouse_motion = (self.mouse_motion or 0.0) + (b.mouse_motion or 0.0)

    @staticmethod
    def merge_within(ses: sqlalchemy.orm.Session, threshold: float) -> int:
        """
        Merge all mostly identical events within threshold seconds of each other.

        :param ses: The sqlalchemy session object to make the queries and changes in
        :param threshold: The number of seconds apart two otherwise identical events may be to be merged
        :return: The number of events removed in the consolidation process
        """
        idx = 0
        deletions = 0
        with ses.begin() as s:
            l = list(ses.query(WindowEvent).order_by(WindowEvent.time_start))
            while idx < len(l) - 1:
                a = l[idx]
                b = l[idx + 1]

                delete = a.should_merge(b, threshold)
                if delete:
                    a.merge(b, threshold)
                    del l[idx + 1]
                    ses.delete(b)
                    deletions += 1
                else:
                    idx += 1
        return deletions

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

    def duration(self) -> datetime.timedelta:
        return self.time_end - self.time_start


current_time = time.monotonic_ns()


def session_object():
    for i in session.query(SessionObject).where(SessionObject.id == current_time):
        return i
    return SessionObject(id=current_time)
