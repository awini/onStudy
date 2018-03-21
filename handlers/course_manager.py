import tornado.web

from datetime import datetime, timedelta

from handlers.BaseHandler import BaseHandler
from db.models import Course
from settings import sets

from logging import getLogger
log = getLogger(__name__)


class BaseCourseHandler(BaseHandler):
    def get_template_path(self):
        return sets.TEMPLATE_PATH + 'teach'


class CreateCourseHandler(BaseCourseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        return self.render('create_course.html', modes=Course.COURSE_MODES)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        course_name = self.get_argument('courseName')
        course_description = self.get_argument('courseDescription')
        mode = self.get_argument('courseMode')

        course = self.Course.create(self.get_current_user(), course_name, course_description, mode)
        if course:
            self.set_status(200)
        else:
            self.set_status(400)
            self.write('Course with this name already exist')


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
            if self.Lesson.get_all_by_course(course_name):
                self.Course.change_state(user, course_name, action)
            else:
                self.set_status(400)
                self.write('Before "{}" Course you must create atleast one lection'.format(action))


class CoursesHandler(BaseCourseHandler):

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
        # TODO: check owner
        # TODO: add option for remove material
        action = self.get_argument('action')
        self.ACTIONS[action]()

    def __add_lesson(self):
        les_name = self.get_argument('lessonName')
        les_descr = self.get_argument('lessonDescription')
        start_time = self.__parse_datetime(self.get_argument('lessonStartTime'))
        dur = int(self.get_argument('lessonDuration'))
        course_name = self.get_argument('lessonCursename')

        try:
            files = self.request.files['lessonMaterials']
        except KeyError:
            files = []

        err = self.__err_before_add(les_name, start_time, dur, course_name, files)
        if err:
            self.set_status(400)
            self.write(err)
            return
        else:
            lesson = self.Lesson.create_lesson(
                self.get_current_user(),
                course_name,
                les_name,
                les_descr,
                start_time,
                dur,
            )
            if lesson._course.mode != Course.OPEN:
                if self.get_argument('isHomeWork', default=None) == 'on':
                    hw_text = self.get_argument('homeWorkDescr')
                    if hw_text:
                        self.HomeWork.add(hw_text, lesson)
            # TODO: FIX: if LessonMaterail fail to create, lesson was already created anyway!!!
            for fl in files:
                self.LessonMaterial.add_file(fl['filename'], fl['body'], lesson)

        self.redirect('/teach/manage?course={}'.format(course_name))

    def __err_before_add(self, les_name, start_time, dur, course_name, files):
        err_descr = None
        if start_time < datetime.now():
            err_descr = 'Lesson can`t start in past!'
        if 300 < dur or dur < 10:
            err_descr = 'Lessond duration must be in diaposon (10, 300)'
        if self.Lesson.check_in_course(les_name, course_name):
            err_descr = 'Lesson "{}" already exist in course "{}"'.format(les_name, course_name)
        les_end = start_time + timedelta(minutes=dur)
        for lesson in self.Lesson.get_all_by_course(course_name):
            if lesson.start_time <= start_time <= lesson.start_time + timedelta(minutes=lesson.duration):
                err_descr = 'New lesson start time cross {} lesson'.format(lesson.name)
                continue
            if lesson.start_time <= les_end <= lesson.start_time + timedelta(minutes=lesson.duration):
                err_descr = 'New lesson end time cross {} lesson'.format(lesson.name)
        for fl in files:
            if len(fl['filename']) > 255:
                err_descr = 'File "{}" name must be < 255'.format(fl['filename'])
        return err_descr

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
