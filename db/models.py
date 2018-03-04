from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, UniqueConstraint
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
    _course_member = relationship("CourseMembers", back_populates="_member")
    _course_invites = relationship("CourseInvites", back_populates="_member")


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
    invite_url = Column(String(length=36))

    _owner = relationship("User", back_populates="_course")
    _lesson = relationship("Lesson", back_populates="_course")
    _course_member = relationship('CourseMembers', back_populates='_course')
    _course_invites = relationship("CourseInvites", back_populates="_course")


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


class CourseMembers(Base):
    __tablename__ = 'course_member'

    id = Column(Integer, primary_key=True)

    course = Column(Integer, ForeignKey('course.id'))
    member = Column(Integer, ForeignKey('user.id'))
    assign_type = Column(Choice(Course.COURSE_MODES))

    _course = relationship("Course", back_populates="_course_member")
    _member = relationship("User", back_populates="_course_member")


class CourseInvites(Base):
    __tablename__ = 'course_invites'

    id = Column(Integer, primary_key=True)
    course = Column(Integer, ForeignKey('course.id'))
    member = Column(Integer, ForeignKey('user.id'))

    __table_args__ = UniqueConstraint('course', 'member', name='_course_course_uc'),  # must be tupple!

    _course = relationship("Course", back_populates="_course_invites")
    _member = relationship("User", back_populates="_course_invites")
