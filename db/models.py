from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

from db.custom_types import Choice


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=30))
    password = Column(String(length=60))
    email = Column(String(length=60))

    _course = relationship('Course', back_populates='_owner')
    _lesson_member = relationship("LessonMembers", back_populates="_member")


class Course(Base):
    __tablename__ = 'course'

    OPEN = 'Open'
    CLOSED = 'Closed'
    PRIVATE = 'Private'
    COURSE_MODES = {
        OPEN: 'O',
        CLOSED: 'C',
        PRIVATE: 'P',
    }
    CREATED = 'Created'
    PUBLISHED = 'Published'
    LIVE = 'Live'
    INTERRUPTED = 'Interrupted'
    ENDED = 'Ended'
    COURSE_STATES = {
        CREATED: 'C',
        PUBLISHED: 'P',
        LIVE: 'L',
        INTERRUPTED: 'I',
        ENDED: 'E',
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(length=30))
    description = Column(Text)
    owner = Column(Integer, ForeignKey('user.id'))
    mode = Column(Choice(COURSE_MODES))
    state = Column(Choice(COURSE_STATES))

    _owner = relationship("User", back_populates="_course")
    _lesson = relationship("Lesson", back_populates="_course")


class Lesson(Base):
    __tablename__ = 'lesson'

    LIVE = 'Live'
    WAITING = 'Waiting'
    INTERRUPTED = 'Interrupted'
    ENDED = 'Ended'

    LESSON_STATE = {
        LIVE: 'L',
        WAITING: 'W',
        INTERRUPTED: 'I',
        ENDED: 'E',
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(length=30))
    description = Column(Text)
    start_time = Column(DateTime)
    duration = Column(Integer)
    state = Column(Choice(LESSON_STATE))
    course = Column(Integer, ForeignKey('course.id'))

    stream_key = Column(String(length=36))
    stream_pw  = Column(String(length=12))

    _course = relationship("Course", back_populates="_lesson")
    _lesson_member = relationship("LessonMembers", back_populates="_lesson")


class LessonMembers(Base):
    __tablename__ = 'lesson_member'

    id = Column(Integer, primary_key=True)

    lesson = Column(Integer, ForeignKey('lesson.id'))
    member = Column(Integer, ForeignKey('user.id'))
    assign_type = Column(Choice(Course.COURSE_MODES))

    _lesson = relationship("Lesson", back_populates="_lesson_member")
    _member = relationship("User", back_populates="_lesson_member")

