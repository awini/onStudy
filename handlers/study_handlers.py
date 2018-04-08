from tornado.web import authenticated

from db.models import Course
from handlers.BaseHandler import BaseHandler
from settings import sets

from logging import getLogger
log = getLogger(__name__)


class BaseStudyHandler(BaseHandler):
    def get_template_path(self):
        return sets.TEMPLATE_PATH + 'study'


# FIXME: I need it cause using module inside
class BaseStudyHandlerClear(BaseHandler):

    def get_template_path(self):
        return sets.TEMPLATE_PATH


class StudyLiveHandler(BaseStudyHandlerClear):
    
    def get(self):
        lessons = self.Course.get_open_course_live_lesson()
        return self.render('study/live.html', lessons=lessons)

    def post(self):
        pass


class StudyFindHandler(BaseStudyHandlerClear):
    @authenticated
    def get(self):
        open_courses, closed_courses = self.Course.get_all_course(self.get_current_user())
        return self.render('study/find.html', open_c=open_courses, closed_c=closed_courses)

    @authenticated
    def post(self):
        # TODO: must be different behaviour for different: course_type = self.get_argument('courseType')
        course_name = self.get_argument('courseName')
        user_name = self.get_current_user()
        if not self.Course.associate_with_course(user_name, course_name):
            # association already exist!!!
            self.set_status(400)


class StudyManageHandler(BaseStudyHandler):
    @authenticated
    def get(self):
        user_in = self.CourseMembers.get_all_study_course(self.get_current_user())
        return self.render('manage.html', user_in=user_in)

    @authenticated
    def post(self):
        pass


class StudyInviteHandler(BaseStudyHandler):
    @authenticated
    def get(self):
        invites = self.CourseInvites.get_user_invites(self.get_current_user())
        return self.render('invite.html', invites=invites)

    @authenticated
    def post(self):
        username = self.get_current_user()
        action = self.get_argument('action')
        course_name = self.get_argument('courseName')
        if action == 'accept':
            self.CourseInvites.invite_on_accept(course_name, username)
        elif action == 'decline':
            self.CourseInvites.invite_on_decline(course_name, username)
        else:
            log.warning('Unknown action {}'.format(action))
            self.set_status(400)


class StudyRegisterHandler(BaseStudyHandler):
    @authenticated
    def get(self, invite_url):
        course = self.Course.get_by_invite_url(invite_url)
        if course:
            self.render('register.html', course=course)
        else:
            self.set_status(400)

    @authenticated
    def post(self, invite_url):
        course = self.Course.get_by_invite_url(invite_url)
        if course:
            assoc = self.Course.associate_with_invite_url(self.get_current_user(), invite_url)
            if not assoc:
                self.set_status(400)
        else:
            self.set_status(400)


class StudyCourseHandler(BaseStudyHandler):

    def get(self, course_id, *args, **kwargs):
        course = self.Course.get_course_by_id(course_id)
        if course.mode == Course.OPEN:
            return self.get_open_course(course)
        return self.get_not_open_course(course)

    def get_open_course(self, course):
        self.render_course(course)

    @authenticated
    def get_not_open_course(self, course):
        self.render_course(course)

    def render_course(self, course):
        return self.render('course.html', course=course)


class StudyHomeWorkHandler(BaseStudyHandler):

    @authenticated
    def get(self):
        # TODO: check if user had registred on this course
        lesson_id = self.get_argument('lesson')
        homeworks = self.HomeWork.get_all_in_lesson(lesson_id)
        answers = self.HomeWorkAnswer.get_user_anwers(self.get_current_user(), homeworks)
        return self.render('homework.html', homeworks=homeworks, answers=answers)

    @authenticated
    def post(self):
        # TODO: check if user already write answer for hw_id
        user = self.get_current_user()
        answer = self.get_argument('answer')
        hw_id = self.get_argument('homeworkid')
        lesson = self.HomeWork.check_by_listener(user, hw_id)
        if not lesson:
            self.set_status(400)
            return

        self.HomeWorkAnswer.add_answer(user, hw_id, answer)
        self.redirect('/study/homework?lesson={}'.format(lesson.id))
