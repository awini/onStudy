from handlers.BaseHandler import BaseHandler
from db.models import Course
import tornado.web
from datetime import datetime
import json

from settings import sets

from logging import getLogger
log = getLogger(__name__)

COURSE_MODES = Course.COURSE_MODES


class BaseCourseHandler(BaseHandler):
    def get_template_path(self):
        return sets.TEMPLATE_PATH + 'courses'


class CreateCourseHandler(BaseCourseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        return self.render('create_course.html', modes=COURSE_MODES)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        course_name = self.get_argument('courseName')
        course_description = self.get_argument('courseDescription')
        mode = self.get_argument('courseMode')

        self.Course.create(self.get_current_user(), course_name, course_description, mode)
        self.set_status(200)


class ManageCourseHandler(BaseCourseHandler):

    def __init__(self, *args, **kwargs):
        self.COURSE_ACTIONS = (
            'Published',
            'Interrupted',
            'InviteMember',
        )
        super().__init__(*args, **kwargs)

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        # TODO: add showing registred/invited users table for private/closed course
        course_name = self.get_argument('course')
        course, lessons, members = self.Course.get_by_owner(course_name, self.get_current_user())
        return self.render('manage_course.html', course=course, lessons=lessons, members=members)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        course_name = self.get_argument('courseName')
        action = self.get_argument('action')
        user = self.get_current_user()
        if action not in self.COURSE_ACTIONS:
            self.set_status(400)
            return
        if action == 'InviteMember':
            user_to_invite = self.get_argument('userToInvite')
            err = self.CourseInvites.create_invite(course_name, user, user_to_invite)
            if err:
                self.write(err)
                self.set_status(400)
                log.debug('Failed adding invite')
            else:
                log.debug('Success adding invite')
        else:
            self.Course.change_state(user, course_name, action)


class CourseHandler(BaseCourseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        user_courses = self.Course.get_all_by_owner(self.get_current_user())
        return self.render('courses.html', courses=user_courses)


class LessonHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        self.ACTIONS = {
            'add': self.__add_lesson,
            'remove': self.__remove_lesson,
            'change': self.__change_lesson,
        }
        super().__init__(*args, **kwargs)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        action = self.get_argument('action')
        self.ACTIONS[action]()

    def __add_lesson(self):
        les_name = self.get_argument('lessonName')
        les_descr = self.get_argument('lessonDescription')
        start_time = self.__parse_datetime(self.get_argument('lessonStartTime'))
        dur = self.get_argument('lessonDuration')
        course_name = self.get_argument('courseName')

        self.Lesson.create_lesson(
            self.get_current_user(),
            course_name,
            les_name,
            les_descr,
            start_time,
            dur,
        )

    def __remove_lesson(self):
        course_name = self.get_argument('courseName')
        lesson_name = self.get_argument('lessonName')
        username = self.get_current_user()
        self.Lesson.delete_lesson(username, course_name, lesson_name)

    def __change_lesson(self):
        print('change lesson')
        raise NotImplementedError

    def __parse_datetime(self, datetime_str):
        date_processing = datetime_str.replace('T', '-').replace(':', '-').split('-')
        return datetime(*[int(v) for v in date_processing])
