from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from uuid import uuid4
from datetime import datetime, timedelta

from db.models import User, Lesson, LessonMembers, Course
from settings import sets


DB_SESSIONS = scoped_session(sessionmaker(bind=create_engine(sets.DB_SCHEME + sets.DB_NAME)))


def modify_db(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            DB_SESSIONS.rollback()
            raise
    return wrapper


class DBBridge:
    '''
    DBBridge (Data Base Bridge) uses for recieve/send data to/from DB
    '''

    __instance = None
    __db_sessions = DB_SESSIONS

    def __init__(self):
        if DBBridge.__instance:
            raise BaseException('Use get_instance method!')

    @staticmethod
    def get_instance():
        if DBBridge.__instance:
            return DBBridge.__instance
        return DBBridge()

    def query(self, *args, **kwargs):
        return DBBridge.__db_sessions.query(*args, **kwargs)

    def finish_query(self):
        DBBridge.__db_sessions.remove()

    def get_user(self, username: str):
        with self as query:
            try:
                user = query(User).filter(User.name == username).one()
            except NoResultFound:
                user = None
        return user

    def get_user_by_email(self, email):
        with self as query:
            try:
                user = query(User).filter(User.email == email).one()
            except NoResultFound:
                user = None
        return user

    def get_course(self, course_name, username):
        user = self.get_user(username)
        lessons = []
        with self as query:
            course = query(Course).filter(Course.name == course_name, Course.owner == user.id).one()
            for l in course._lesson:
                lessons.append(l)
        return course, lessons

    def get_course_by_stream(self, key):
        with self as query:
            try:
                course = query(Course).filter(Course.stream_key == key)
            except NoResultFound:
                course = None
        return course

    def get_all_user_course(self, username):
        user = self.get_user(username)
        with self as query:
            try:
                courses = query(Course).filter(Course.owner == user.id)
            except NoResultFound:
                courses = None
        return courses

    def get_lessons_by_stream(self, stream_key):
        lessons = []
        with self as query:
            courses = query(Course).filter(Course.stream_key == stream_key).one()
            for l in courses._lesson:
                lessons.append(l)
        return lessons

    @modify_db
    def activate_lesson(self, stream_key):
        lesson = None
        with self as query:
            courses = query(Course).filter(Course.stream_key == stream_key).one()
            for l in courses._lesson:
                dif_time = (datetime.now() - l.start_time).total_seconds() / 60  # value in minutes
                allow_time = dif_time + sets.STREAM_WINDOW
                is_possible = dif_time < (l.duration + sets.STREAM_WINDOW)
                try:
                    if allow_time > 0 and is_possible and (l.state == 'Waiting' or l.state == 'Live') :
                        if lesson.start_time > l.start_time:
                            # find the nearest lesson
                            lesson = l
                except AttributeError:
                    lesson = l

            if lesson and lesson.state == 'Waiting':
                lesson.state = Lesson.LESSON_STATE['Live']
                self.__db_sessions.commit()
                print('change lesson "{}" state from "{}" to "Live"'.format(lesson.name, lesson.state))
        return lesson

    @modify_db
    def create_user(self, username, password, email):
        # TODO: check if username/email already exist
        u = User(name=username, password=password, email=email)
        self.__add_in_db(u)

    @modify_db
    def create_course(self, username, course_name, course_descr, mode):
        # TODO: check if course_name already exist
        user = self.get_user(username)
        c = Course(
            name=course_name,
            description=course_descr,
            stream_key=str(uuid4()),
            owner= user.id,
            mode=Course.COURSE_MODES[mode],
            state=Course.COURSE_STATES['Created'],
        )
        self.__add_in_db(c)

    @modify_db
    def create_lesson(self, username, course_name, l_name, l_descr, start_time, dur):
        # TODO: check if 'l_name' not already exist in lessons 'course_name'
        # TODO: check start_time (not cross with other lessons and in future)
        # TODO: check dur (must be non zero posivite value)
        course, _ = self.get_course(course_name, username)
        l = Lesson(
            name=l_name,
            description=l_descr,
            start_time=start_time,
            duration=dur,
            state=Lesson.LESSON_STATE['Waiting'],
            course=course.id,
        )
        self.__add_in_db(l)

    @modify_db
    def delete_lesson(self, username, course_name, lesson_name):
        course, lessons = self.get_course(course_name, username)
        for l in lessons:
            if l.name == lesson_name:
                self.__rm_from_db(l)

    @modify_db
    def change_course_state(self, username, course_name, state):
        user = self.get_user(username)
        with self as query:
            course = query(Course).filter(Course.name == course_name, Course.owner == user.id).one()
            course.state = Course.COURSE_STATES[state]
            self.__db_sessions.commit()

    def __rm_from_db(self, model):
        self.__db_sessions.delete(model)
        self.__db_sessions.commit()
        self.finish_query()

    def __add_in_db(self, created_object):
        self.__db_sessions.add(created_object)
        self.__db_sessions.commit()
        self.finish_query()

    def __enter__(self):
        return DBBridge.__db_sessions.query

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish_query()

