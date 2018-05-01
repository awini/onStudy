import tornado.web

from datetime import datetime, timedelta
import json

from handlers.BaseHandler import BaseHandler
from db.models import Course, LessonAccess
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
        username = self.get_current_user()

        course = self.Course.create(username, course_name, course_description, mode)
        if course:
            self.set_status(200)
            self.write(json.dumps({'course_id': str(course.id)}))
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
        course_id = self.get_argument('course')
        username = self.get_current_user()
        course, course_access, user = self.Course.get_by_partner(course_id, username)
        lesson_access = self.LessonAccess.get_all_by_partner_and_course(username, course_id)
        return self.render(
            'manage_course.html',
            course=course,
            course_access=course_access,
            user=user,
            lesson_access=lesson_access,
        )

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        course_id = self.get_argument('courseid')
        action = self.get_argument('action')
        user = self.get_current_user()
        if action not in self.COURSE_ACTIONS:
            self.set_status(400)
            return
        if action == 'InviteMember':
            user_to_invite = self.get_argument('userToInvite')
            err = self.CourseInvites.create_learn_invite(course_id, user, user_to_invite)
            if err:
                self.write(err)
                self.set_status(400)
                log.debug('Failed adding invite')
            else:
                log.debug('Success adding invite')
        else:
            if self.Lesson.get_all_by_course(course_id):
                if self.Course.change_state(user, course_id, action):
                    self.set_status(200)
                else:
                    self.set_status(400)
            else:
                self.set_status(400)
                self.write('Before "{}" Course you must create atleast one lection'.format(action))


class CoursesHandler(BaseCourseHandler):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        username = self.get_current_user()
        courses = self.Course.get_all_by_partner(username)
        # return self.render('courses.html', owner_courses=owner_courses, other_course=other_course )
        return self.render('courses.html', courses=courses)

class LessonHandler(BaseCourseHandler):

    def __init__(self, *args, **kwargs):
        self.ACTIONS = {
            'add': self.__add_lesson,
            'remove': self.__remove_lesson,
            'modify': self.__modify_lesson,
        }
        super().__init__(*args, **kwargs)

    @tornado.web.authenticated
    def get(self):
        lesson = self.Lesson.get_by_id(self.get_argument('lesson'))
        access = self.LessonAccess.check_any_access(self.get_current_user(), lesson)
        if not access or access.access == LessonAccess.VIEW:
            self.set_status(400)
            return
        return self.render('lesson_manage.html', lesson=lesson, access=access)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        action = self.get_argument('action')
        self.ACTIONS[action]()

    def __add_lesson(self):
        les_name, les_descr, start_time, dur, course_id = self.__collect_lesson_data()
        if not self.CourseAccess.check_write_access(self.get_current_user(), course_id):
            self.set_status(400)
            return

        err = self.__check_lesson(les_name, les_descr, start_time, dur, course_id)
        if err:
            self.set_status(400)
            self.write(err)
            return
        else:
            l = self.Lesson.create_lesson(
                course_id,
                les_name,
                les_descr,
                start_time,
                dur,
            )
            self.LessonAccess.add_access_to_all_partners(course_id, l.id)
        self.set_status(200)

    def __check_lesson(self, les_name, les_descr, start_time, dur, course_id):
        err_descr = None
        if start_time < datetime.now():
            err_descr = 'Lesson can`t start in past!'
        if 300 < dur or dur < 10:
            err_descr = 'Lessond duration must be in diaposon (10, 300)'
        if self.Lesson.check_in_course(les_name, course_id):
            err_descr = 'Lesson "{}" already exist in course.'.format(les_name)
        if not les_descr:
            err_descr = 'Description must contain some characters...'
        les_end = start_time + timedelta(minutes=dur)
        for lesson in self.Lesson.get_all_by_course(course_id):
            if lesson.start_time <= start_time <= lesson.start_time + timedelta(minutes=lesson.duration):
                err_descr = 'New lesson start time cross {} lesson'.format(lesson.name)
                continue
            if lesson.start_time <= les_end <= lesson.start_time + timedelta(minutes=lesson.duration):
                err_descr = 'New lesson end time cross {} lesson'.format(lesson.name)
        return err_descr

    def __remove_lesson(self):
        lesson = self.Lesson.get_by_id(self.get_argument('lessonid'))
        if not self.LessonAccess.check_write_access(self.get_current_user(), lesson):
            self.set_status(400)
            return
        self.Lesson.delete_lesson(lesson)
        self.redirect('/teach/manage?course={}'.format(lesson.course))

    def __modify_lesson(self):
        # TODO: check if new values is valid
        lesson_data = self.__collect_lesson_data()
        lesson = self.Lesson.get_by_id(self.get_argument('lessonid'))
        if not self.LessonAccess.check_write_access(self.get_current_user(), lesson):
            self.set_status(400)
            return
        lesson = self.Lesson.modify_lesson(lesson, *lesson_data)
        if not lesson:
            self.set_status(400)
            return
        self.redirect('/teach/lesson?lesson={}'.format(lesson.id))

    def __collect_lesson_data(self):
        les_name = self.get_argument('lessonName')
        les_descr = self.get_argument('lessonDescription')
        start_time = self.__parse_datetime(self.get_argument('lessonStartTime'))
        dur = int(self.get_argument('lessonDuration'))
        course_id = self.get_argument('courseid', default=None)
        return les_name, les_descr, start_time, dur, course_id

    def __parse_datetime(self, datetime_str):
        date_processing = datetime_str.replace('T', '-').replace(':', '-').split('-')
        return datetime(*[int(v) for v in date_processing])


class MaterialManageHandler(BaseCourseHandler):

    def __init__(self, *args, **kwargs):
        self.ACTIONS = {
            'delete': self.__delete_material,
            'addMaterial': self.__add_material,
        }
        super().__init__(*args, **kwargs)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        username = self.get_current_user()
        lesson_id = self.get_argument('lessonid')
        material_id = self.get_argument('materialid', default=None)
        if not self.LessonMaterial.check_material(username, lesson_id, material_id):
            self.set_status(400)
            return

        self.ACTIONS[self.get_argument('action')](lesson_id=lesson_id, material_id=material_id)
        self.redirect('/teach/lesson?lesson={}'.format(lesson_id))

    def __add_material(self, **kwargs):
        lesson = self.Lesson.get_by_id(kwargs['lesson_id'])
        try:
            files = self.request.files['lessonMaterials']
        except KeyError:
            files = []
        for fl in files:
            self.LessonMaterial.add_file(fl['filename'], fl['body'], lesson)

    def __delete_material(self, **kwargs):
        self.LessonMaterial.delete_by_material_id(kwargs['material_id'])


class HomeWorkManageHandler(BaseCourseHandler):

    def __init__(self, *args, **kwargs):
        self.ACTIONS = {
            'addHomeWork': self.__add_homework,
            'delHomeWork': self.__delete_homework,
        }
        super().__init__(*args, **kwargs)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        username = self.get_current_user()
        action = self.get_argument('action')
        lesson = self.Lesson.get_by_id(self.get_argument('lessonid'))
        access = self.LessonAccess.check_any_access(username, lesson)

        if access.access == LessonAccess.VIEW or lesson._course.mode == lesson._course.OPEN:
            self.set_status(400)
            return
        self.ACTIONS[action](lesson)
        self.redirect('/teach/lesson?lesson={}'.format(lesson.id))

    def __add_homework(self, lesson):
        hw_descr = self.get_argument('homeWorkDescr')
        hw_title = self.get_argument('HWTitle')
        self.HomeWork.add(hw_title, hw_descr, lesson)

    def __delete_homework(self, lesson):
        hw_id = self.get_argument('homeworkid')
        if self.HomeWork.check_in_lesson(lesson, hw_id):
            self.HomeWork.delete_by_id(hw_id)


class HomeWorkCheckHandler(BaseCourseHandler):
    @tornado.web.authenticated
    def get(self):
        # TODO: check owner
        # TODO: fix error if no homework...
        hw_id = self.get_argument('homework')
        answers = self.HomeWorkAnswer.get_all_homework_answers(hw_id)
        self.render('homework_check.html', answers=answers)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        # TODO: check it is valid id for valid homework
        # TODO: check if already graded
        answer_id = self.get_argument('answerid')
        grade = self.get_argument('gradeValue')
        if 0 > int(grade) > 100:
            self.set_status(400)
            return
        answer = self.HomeWorkAnswer.grade_answer(answer_id, grade)
        self.redirect('/teach/lesson/homework/check?homework={}'.format(answer.home_work))


class LectorRegisterHandler(BaseCourseHandler):
    @tornado.web.authenticated
    def get(self):
        key = self.get_argument('key')
        course = self.Course.get_by_invite_teach_url(key)
        if course:
            self.render('register.html', course=course)
        else:
            self.set_status(400)

    @tornado.web.authenticated
    def post(self):
        key = self.get_argument('key')
        course = self.Course.get_by_invite_teach_url(key)
        if course:
            user = self.User.get(self.get_current_user())
            if self.CourseAccess.check_any_access(user, course):
                #  user already have access
                self.set_status(400)
                return
            assoc = self.CourseAccess.add_browse_access(user.name, course)
            if not assoc:
                log.debug('Access to course not added')
                self.set_status(400)
                return
            self.LessonAccess.add_access_to_all_lesson(user.name, course, LessonAccess.VIEW)
            self.write(json.dumps({'course_id': course.id}))
        else:
            self.set_status(400)


class ManageRightsHandler(BaseCourseHandler):
    def __init__(self, *args, **kwargs):
        self.ACTIONS = {
            'showLessons': self.__show_lessons,
            'modifyLesson': self.__modify_lesson,
            'modifyCourse': self.__modify_course,
        }
        super().__init__(*args, **kwargs)

    @tornado.web.authenticated
    def get(self):
        course_id = self.get_argument('course')
        username = self.get_current_user()
        if not self.CourseAccess.check_write_access(username, course_id):
            self.set_status(400)
            return
        course_right = self.CourseAccess.get_all_by_course(course_id)
        self.render('rights_manage.html', course_right=course_right)

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        course_id = self.get_argument('course')
        if not self.CourseAccess.check_write_access(self.get_current_user(), course_id):
            self.set_status(400)
            return
        self.ACTIONS[self.get_argument('action')](course_id)

    def __modify_course(self, course_id):
        # TODO: check if owner try change his rights...
        # TODO: lesson right must be change as for course rights
        # TODO: User can`t change right for themselves!!
        new_rights = json.loads(self.get_argument('newRight'))
        self.CourseAccess.modify_access_many(course_id, new_rights)

    def __modify_lesson(self, course_id):
        # TODO: check if owner try change his rights...
        # TODO: User can`t change right for themselves!!
        username = self.get_argument('user')
        new_rights = json.loads(self.get_argument('newRight'))
        self.LessonAccess.modify_access_many(course_id, username, new_rights)
        self.__show_lessons(course_id)

    def __show_lessons(self, course_id):
        username = self.get_argument('user')
        lesson_rights = {}
        for access in self.LessonAccess.get_all_by_partner_and_course(username, course_id).values():
            lesson_rights[access._lesson.name] = access.access
        self.write(json.dumps(lesson_rights))
