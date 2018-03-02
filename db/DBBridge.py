from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from uuid import uuid4
from datetime import datetime, timedelta

from db.models import User, Lesson, CourseMembers, Course, CourseInvites
from settings import sets

from logging import getLogger
log = getLogger(__name__)

DB_SESSIONS = scoped_session(sessionmaker(bind=create_engine(sets.DB_SCHEME + sets.DB_NAME)))


class DbHandlerBase:

    def __init__(self, dbb):
        self.dbb = dbb

class CourseMembersHandler(DbHandlerBase):

    def get_all_study_course(self, username):
        user = self.dbb.get_user(username)
        user_in = self.dbb.query(CourseMembers).filter(CourseMembers.member == user.id)
        return user_in




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
        self.CourseMembers = CourseMembersHandler(self)

    @staticmethod
    def get_instance():
        if DBBridge.__instance:
            return DBBridge.__instance
        return DBBridge()

    @staticmethod
    def get_session(func):
        def wrapper(*args, **kwargs):
            return func(DBBridge.__db_sessions, *args, **kwargs)
        return wrapper

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

    def get_owner_course(self, course_name, username):
        user = self.get_user(username)
        lessons = []
        members = []
        with self as query:
            course = query(Course).filter(Course.name == course_name, Course.owner == user.id).one()
            for l in course._lesson:
                lessons.append(l)
            for member in course._course_member:
                members.append(member._member.name)
        return course, lessons, members

    def get_course(self, course_name):
        with self as query:
            course = query(Course).filter(Course.name == course_name).one()
        return course

    def get_course_by_stream(self, key):
        with self as query:
            try:
                course = query(Course).filter(Course.stream_key == key)
            except NoResultFound:
                course = None
        return course

    def get_open_course_live_lesson(self):
        lives = []
        try:
            courses = self.query(Course).filter(
                Course.mode == Course.OPEN,
                Course.state == Course.LIVE,
            )
            for c in courses:
                for lesson in c._lesson:
                    if lesson.state == Lesson.LIVE or lesson.state == Lesson.INTERRUPTED:
                        lives.append(lesson)
        except NoResultFound:
            print('No LIVE course')
            pass
        return lives

    def get_all_course(self, username):
        user = self.get_user(username)
        open_courses = []
        closed_courses = []
        try:
            courses = self.query(Course).filter(
                or_(Course.state == Course.LIVE, Course.state == Course.PUBLISHED),
                or_(Course.mode == Course.OPEN, Course.mode == Course.CLOSED),
            )
            for c in courses:
                already_member = False
                for member in c._course_member:
                    if member.member == user.id:
                        already_member = True
                if already_member:
                    continue
                if c.mode == Course.OPEN:
                    open_courses.append(c)
                else:
                    closed_courses.append(c)
        except NoResultFound:
            print('NO open or closed courses on server ;(')
        return open_courses, closed_courses

    def get_all_owner_course(self, username):
        user = self.get_user(username)
        with self as query:
            try:
                courses = query(Course).filter(Course.owner == user.id)
            except NoResultFound:
                courses = None
        return courses

    # def get_all_study_course(self, username):
    #     return CourseMembers.get_all_study_course(self, username)

    def get_lesson_by_stream(self, stream_key, stream_pw):
        return self.activate_lesson(stream_key, stream_pw)

    def get_user_invites(self, username):
        user = self.get_user(username)
        invites = self.query(CourseInvites).filter(CourseInvites.member == user.id)
        return invites

    @modify_db
    def invite_on_accept(self, course_name, invited_user):
        self.invite_on_decline(course_name, invited_user)
        self.associate_with_course(invited_user, course_name)

    @modify_db
    def invite_on_decline(self, course_name, invited_user):
        user = self.get_user(invited_user)
        with self as query:
            user_course = query(CourseInvites).filter(CourseInvites.member == user.id)
            for c in user_course:
                if c._course.name == course_name:
                    self.__rm_from_db(c)
                    return
        log.warning('No association for user "{}" and course "{}" in CourseInvites'.format(invited_user, course_name))

    @modify_db
    def activate_lesson(self, stream_key, stream_pw):
        with self as query:
            try:
                lesson = query(Lesson).filter(
                    Lesson.stream_key == stream_key,
                    Lesson.stream_pw == stream_pw,
                    or_(Lesson.state == Lesson.WAITING, Lesson.state == Lesson.LIVE, Lesson.state == Lesson.INTERRUPTED)
                ).one()
                accept_start = lesson.start_time - timedelta(minutes=sets.STREAM_WINDOW)
                accept_end = lesson.start_time + timedelta(minutes=lesson.duration) + \
                             timedelta(minutes=sets.STREAM_WINDOW)
                if accept_start < datetime.now() < accept_end:
                    if lesson.state == Lesson.WAITING or lesson.state == Lesson.INTERRUPTED:
                        lesson.state = Lesson.LIVE
                        print('change lesson "{}" state from "{}" to "Live"'.format(lesson.name, lesson.state))
                        if lesson._course.state != Course.LIVE:
                            lesson._course.state = Course.LIVE
                            print('Change course "{}" state to live'.format(lesson._course.name))
                        self.__db_sessions.commit()
                else:
                    lesson = None
            except NoResultFound:
                lesson = None
        return lesson

    @modify_db
    def stop_lesson(self, stream_key, stream_pw):
        with self as query:
            lesson = query(Lesson).filter(Lesson.stream_key == stream_key, Lesson.stream_pw == stream_pw).one()
            if lesson.state != Lesson.LIVE:
                # this can`t be possible on normal request
                return
            lesson.state = Lesson.INTERRUPTED
            self.__db_sessions.commit()

    @modify_db
    def create_invite(self, course_name, owner, user_to_invite):
        # TODO: check if user_to_invite already invited to this course
        with self as query:
            course = query(Course).filter(Course.name == course_name).one()
            if course._owner.name != owner:
                return 'Bad Request'
        user = self.get_user(user_to_invite)
        if not user:
            return 'User with that name doesn`t exist!'
        i = CourseInvites(course=course.id, member=user.id)
        try:
            self.__add_in_db(i)
        except IntegrityError:
            return 'User "{}" already invited to course "{}"'.format(user_to_invite, course_name)

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
            owner= user.id,
            mode=mode,
            state=Course.CREATED,
        )
        self.__add_in_db(c)

    @modify_db
    def create_lesson(self, username, course_name, l_name, l_descr, start_time, dur):
        # TODO: check if 'l_name' not already exist in lessons 'course_name'
        # TODO: check start_time (not cross with other lessons and in future)
        # TODO: check dur (must be non zero posivite value)
        course, _ = self.get_owner_course(course_name, username)
        l = Lesson(
            name=l_name,
            description=l_descr,
            start_time=start_time,
            duration=dur,
            state=Lesson.WAITING,
            course=course.id,
            stream_key=str(uuid4()),
            stream_pw=str(uuid4()).split('-')[-1]  # last string after '-' in ******-****-****-****-******
        )
        self.__add_in_db(l)

    @modify_db
    def associate_with_course(self, username, course_name):
        # TODO: verify if username already member of course_name
        # TODO: verify if username CAN be a member of course_name
        user = self.get_user(username)
        course = self.get_course(course_name)
        with self as query:
            try:
                query(CourseMembers).filter(CourseMembers.course == course.id, CourseMembers.member == user.id).one()
                return False
            except NoResultFound:
                cm = CourseMembers(
                    course=course.id,
                    member=user.id,
                    assign_type=course.mode,
                )
                self.__add_in_db(cm)
                log.info('Associate user "{}" with course "{}"'.format(username, course_name))
                return True

    @modify_db
    def delete_lesson(self, username, course_name, lesson_name):
        course, lessons, _ = self.get_owner_course(course_name, username)
        for l in lessons:
            if l.name == lesson_name:
                self.__rm_from_db(l)

    @modify_db
    def change_course_state(self, username, course_name, state):
        user = self.get_user(username)
        with self as query:
            course = query(Course).filter(Course.name == course_name, Course.owner == user.id).one()
            course.state = state #course.state = Course.COURSE_STATES[state]
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
