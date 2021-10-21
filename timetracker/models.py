from __future__ import annotations
import datetime
import time

import sqlalchemy.orm
from sqlalchemy import create_engine, Column, Integer, DateTime as DT, ForeignKey, String
from sqlalchemy.orm import sessionmaker, declarative_base, relationship,scoped_session
from sqlalchemy.pool import SingletonThreadPool

engine = create_engine('sqlite:///timetracker.db')
session = scoped_session(sessionmaker(bind=engine))
#session = Session()
Base = declarative_base()


class SessionObject(Base):
    """
    Timetracker session
    """
    __tablename__ = 'Session'
    id = Column(Integer, primary_key=True)
    date = Column(DT)
    events = relationship('WindowEvent', back_populates='session')

    @staticmethod
    def collect_within_time(ses, td: datetime.timedelta) -> list[SessionObject]:
        return ses.query(SessionObject).where(SessionObject.date >= datetime.datetime.now() - td)


class WindowClass(Base):
    __tablename__ = 'WindowClass'
    id = Column(Integer, primary_key=True)
    name = Column(Integer, unique=True)
    events = relationship('WindowEvent', secondary='EventClass', backref='classes')


class EventClass(Base):
    __tablename__ = 'EventClass'
    event_id = Column(Integer, ForeignKey('WindowEvent.id'), primary_key=True)
    class_id = Column(Integer, ForeignKey('WindowClass.id'), primary_key=True)


class WindowEvent(Base):
    __tablename__ = 'WindowEvent'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('Session.id'), nullable=False)
    window_name = Column(String)
    window_id = Column(Integer)
    time_start = Column(DT)
    time_end = Column(DT)
    session = relationship('SessionObject', back_populates='events')
    classes: list[WindowClass]

    def date_of(self) -> tuple[int, int, int]:
        year = self.time_start.year
        month = self.time_start.month
        day = self.time_start.day
        return year, month, day


current_time = time.monotonic_ns()


@property
def session_object():
    for i in session.query(SessionObject).where(SessionObject.id == current_time):
        return i
    return SessionObject(id=current_time)
