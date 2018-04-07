from datetime import timedelta, datetime, date
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_

from db.models import CourseMembers, Course, User, Lesson, CourseInvites, LessonMaterial, HomeWork
from db.DBBridge import DBBridge
from settings import sets

from logging import getLogger
log = getLogger(__name__)


class DbHandlerBase:

    def __init__(self, dbb: DBBridge):
        self.dbb = dbb


class UserHandler(DbHandlerBase):

    @staticmethod
    @DBBridge.query_db
    def get(session, username: str):
        user = session.query(User).filter(User.name == username).one_or_none()
        return user

    @staticmethod
    @DBBridge.query_db
    def get_by_email(session, email):
        return session.query(User).filter(User.email == email).one_or_none()

    @staticmethod
    @DBBridge.modife_db
    def create(session, username, password, email):
        # TODO: check if username/email already exist
        user = User(name=username, password=password, email=email)
        session.add(user)


class CourseHandler(DbHandlerBase):

    @staticmethod
    @DBBridge.query_db
    def get_by_owner(session, course_name, username):
        user = UserHandler.get(username)
        lessons = []
        members = []
        course = session.query(Course).filter(Course.name == course_name, Course.owner == user.id).one()
        for l in course._lesson:
            lessons.append(l)
        for member in course._course_member:
            members.append(member._member.name)
        return course, lessons, members

    @staticmethod
    @DBBridge.query_db
    def get_by_id(session, course_id, username):
        user = UserHandler.get(username)
        course = session.query(Course).filter(Course.id == course_id, Course.owner == user.id).one()
        return course

    @staticmethod
    @DBBridge.query_db
    def get(session, course_name):
        course = session.query(Course).filter(Course.name == course_name).one_or_none()
        return course

    @staticmethod
    @DBBridge.query_db
    def get_by_invite_url(session, invite_url):
        return session.query(Course).filter(Course.invite_url == invite_url).one_or_none()

    @staticmethod
    @DBBridge.query_db
    def get_by_stream_key(session, key):
        return session.query(Course).filter(Course.stream_key == key).one_or_none()

    @staticmethod
    @DBBridge.query_db
    def get_open_course_live_lesson(session):
        lives = []
        try:
            courses = session.query(Course).filter(
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

    @staticmethod
    @DBBridge.query_db
    def get_all_course(session, username):
        user = UserHandler.get(username)
        open_courses = []
        closed_courses = []
        try:
            courses = session.query(Course).filter(
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

    @staticmethod
    @DBBridge.query_db
    def get_all_by_owner(session, username):
        user = UserHandler.get(username)
        try:
            courses = session.query(Course).filter(Course.owner == user.id)
        except NoResultFound:
            courses = None
        return courses

    @staticmethod
    @DBBridge.query_db
    def get_course_by_id(session, course_id):
        course = session.query(Course).filter(Course.id == course_id).one_or_none()
        return course

    @staticmethod
    @DBBridge.modife_db
    def create(session, username, course_name, course_descr, mode):
        user = UserHandler.get(username)

        c = None
        if not CourseHandler.get(course_name):
            invite_url = str(uuid4()) if mode == Course.PRIVATE else None
            c = Course(
                name=course_name,
                description=course_descr,
                owner= user.id,
                mode=mode,
                state=Course.CREATED,
                invite_url=invite_url,
            )
            session.add(c)
        return c

    @staticmethod
    @DBBridge.modife_db
    def associate_with_course(session, username, course_name):
        # TODO: verify if username CAN be a member of course_name
        user = UserHandler.get(username)
        course = CourseHandler.get(course_name)
        if not CourseMembersHandler.get_member_by_course(course.id, user.id):
            cm = CourseMembers(
                course=course.id,
                member=user.id,
                assign_type=course.mode,
            )
            log.info('Associate user "{}" with course "{}"'.format(username, course_name))
            session.add(cm)
            return cm

    @staticmethod
    @DBBridge.modife_db
    def associate_with_invite_url(session, username, invite_url):
        # TODO: verify if username CAN be a member of course_name
        user = UserHandler.get(username)
        course = CourseHandler.get_by_invite_url(invite_url)
        if not CourseMembersHandler.get_member_by_course(course.id, user.id):
            cm = CourseMembers(
                course=course.id,
                member=user.id,
                assign_type=course.mode,
            )
            log.info('Associate user "{}" with course "{}"'.format(username, course.name))
            session.add(cm)
            return cm



    @staticmethod
    @DBBridge.modife_db
    def change_state(session, username, course_name, state):
        course = CourseHandler.get(course_name)
        course.state = state


class LessonHandler(DbHandlerBase):

    @staticmethod
    @DBBridge.query_db
    def get_by_id(session, lesson_id):
        return session.query(Lesson).filter(Lesson.id == lesson_id).one()

    @staticmethod
    @DBBridge.query_db
    def get_by_keys(session, stream_key, stream_pw):
        return session.query(Lesson).filter(
            Lesson.stream_key == stream_key, Lesson.stream_pw == stream_pw
        ).one_or_none()

    @staticmethod
    @DBBridge.query_db
    def check_in_course(session, lec_name, course_name):
        return session.query(Lesson).join(Course).filter(
            Lesson.name == lec_name, Course.name == course_name
        ).one_or_none()

    @staticmethod
    def check_owner(username, lesson_id):
        lesson = LessonHandler.get_by_id(lesson_id)
        if lesson._course._owner.name == username:
            return lesson


    @staticmethod
    @DBBridge.query_db
    def get_all_by_course(session, course_name):
        lessons = []
        for l in CourseHandler.get(course_name)._lesson:
            lessons.append(l)
        return lessons

    @staticmethod
    @DBBridge.modife_db
    def activate_lesson(session, stream_key, stream_pw):
        lesson = LessonHandler.get_by_keys(stream_key, stream_pw)
        if lesson and lesson.state != lesson.ENDED:
            accept_start = lesson.start_time - timedelta(minutes=sets.STREAM_WINDOW)
            accept_end = lesson.start_time + timedelta(minutes=lesson.duration) + timedelta(minutes=sets.STREAM_WINDOW)
            if accept_start < datetime.now() < accept_end:
                if lesson.state == Lesson.WAITING or lesson.state == Lesson.INTERRUPTED:
                    lesson.state = Lesson.LIVE
                    log.debug('change lesson "{}" state from "{}" to "Live"'.format(lesson.name, lesson.state))
                    if lesson._course.state != Course.LIVE:
                        lesson._course.state = Course.LIVE
                        log.debug('Change course "{}" state to live'.format(lesson._course.name))
            else:
                lesson = None
        return lesson

    @staticmethod
    @DBBridge.modife_db
    def stop_lesson(session, stream_key, stream_pw):
        lesson = LessonHandler.get_by_keys(stream_key, stream_pw)
        if lesson.state != Lesson.LIVE:
            # this can`t be possible on normal request
            return
        lesson.state = Lesson.INTERRUPTED

    @staticmethod
    @DBBridge.modife_db
    def create_lesson(session, username, course_name, l_name, l_descr, start_time, dur):
        course, _, _ = CourseHandler.get_by_owner(course_name, username)
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
        session.add(l)
        return l

    @staticmethod
    @DBBridge.modife_db
    def delete_lesson(session, username, course_name, lesson_name):
        course, lessons, _ = CourseHandler.get_by_owner(course_name, username)
        for l in lessons:
            if l.name == lesson_name:
                LessonMaterialHandler.delete_by_lesson(l)
                session.delete(l)
                return l

    @staticmethod
    @DBBridge.modife_db
    def modify_lesson(session, username, les_id, les_name, les_descr, start_time, dur, course_name):
        # TODO: check if new data valid
        # TODO: check owner
        lesson = session.query(Lesson).filter(Lesson.id == les_id).one()
        if lesson._course._owner.name != username:
            return None  # not possible in valid request
        lesson.name = les_name
        lesson.description = les_descr
        lesson.start_time = start_time
        lesson.duration = dur
        return lesson


class CourseMembersHandler(DbHandlerBase):

    @staticmethod
    @DBBridge.query_db
    def get_member_by_course(session, course_id, user_id):
        return session.query(CourseMembers).filter(
            CourseMembers.course == course_id, CourseMembers.member == user_id
        ).one_or_none()

    @staticmethod
    @DBBridge.query_db
    def get_all_study_course(session, username):
        user = UserHandler.get(username)
        user_in = session.query(CourseMembers).filter(CourseMembers.member == user.id)
        return user_in


class CourseInvitesHandler(DbHandlerBase):

    @staticmethod
    @DBBridge.query_db
    def get_user_invites(session, username):
        user = UserHandler.get(username)
        invites = session.query(CourseInvites).filter(CourseInvites.member == user.id)
        return invites

    @staticmethod
    @DBBridge.modife_db
    def invite_on_decline(session, course_name, invited_user):
        user_course = CourseInvitesHandler.get_user_invites(invited_user)
        for c in user_course:
            if c._course.name == course_name:
                session.delete(c)
                return c
        log.warning('No association for user "{}" and course "{}" in CourseInvites'.format(invited_user, course_name))

    @staticmethod
    @DBBridge.modife_db
    def invite_on_accept(session, course_name, invited_user):
        CourseInvitesHandler.invite_on_decline(course_name, invited_user)
        CourseHandler.associate_with_course(invited_user, course_name)

    @staticmethod
    @DBBridge.modife_db
    def create_invite(session, course_name, owner, user_to_invite):
        # TODO: check if user_to_invite already invited to this course
        course = CourseHandler.get(course_name)
        if course._owner.name != owner:
            log.debug('Bad Request')
            return
        user = UserHandler.get(owner)
        if not user:
            log.debug('User with that name doesn`t exist!')
        i = CourseInvites(course=course.id, member=user.id)
        session.add(i)
        return i


class LessonMaterialHandler(DbHandlerBase):

    @staticmethod
    @DBBridge.query_db
    def check_material(session, username, lesson_id, material_id):
        lesson = LessonHandler.get_by_id(lesson_id)
        if lesson._course._owner.name != username:
            return False
        if not material_id:
            return True
        material_id = int(material_id)
        for m in lesson._lesson_material:
            if m.id == material_id:
                return True

    @staticmethod
    @DBBridge.query_db
    def get_with_path(session, file_name):
        material = session.query(LessonMaterial).filter(LessonMaterial.real_name == file_name).one_or_none()
        if material:
            return Path(sets.MEDIA_DIR) / material.parent_dir / file_name, material


    @staticmethod
    @DBBridge.modife_db
    def add_file(session, file_name, file_data, lesson):
        file_dir = Path(sets.MEDIA_DIR) / str(date.today())
        if not file_dir.is_dir():
            file_dir.mkdir()

        file_path = file_dir / str(uuid4())
        file_path.write_bytes(file_data)

        les_material = LessonMaterial(
            pretty_name=file_name,
            real_name=file_path.name,
            parent_dir=file_path.parts[-2],
            lesson=lesson.id,
        )
        session.add(les_material)

    @staticmethod
    @DBBridge.modife_db
    def delete_by_material_id(session, material_id):
        material = session.query(LessonMaterial).filter(LessonMaterial.id == material_id).one()
        session.delete(material)
        f_path = Path(sets.MEDIA_DIR) / material.parent_dir / material.real_name
        f_path.unlink()

    @staticmethod
    @DBBridge.modife_db
    def delete_by_lesson(session, lesson):
        files = session.query(LessonMaterial).filter(LessonMaterial.lesson == lesson.id)
        for fl in files:
            f_path = Path(sets.MEDIA_DIR) / fl.parent_dir / fl.real_name
            f_path.unlink()
            session.delete(fl)


class HomeWorkHandler(DbHandlerBase):

    @staticmethod
    def check_in_lesson(lesson, hw_id):
        hw_id = int(hw_id)
        for hw in lesson._home_work:
            if hw.id == hw_id:
                return True

    @staticmethod
    @DBBridge.modife_db
    def add(session, hw_title, hw_desct, lesson):
        hw = HomeWork(
            title=hw_title,
            description=hw_desct,
            lesson=lesson.id,
        )
        session.add(hw)
        return hw

    @staticmethod
    @DBBridge.modife_db
    def delete_by_id(session, hw_id):
        hw = session.query(HomeWork).filter(HomeWork.id == hw_id).one()
        session.delete(hw)