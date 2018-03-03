from handlers.BaseHandler import BaseHandler
from settings import sets

from logging import getLogger
log = getLogger(__name__)


class BaseStudyHandler(BaseHandler):
    def get_template_path(self):
        return sets.TEMPLATE_PATH + 'study'


class StudyLiveHandler(BaseStudyHandler):

    def get(self):
        lessons = self.Course.get_open_course_live_lesson()
        return self.render('live.html', lessons=lessons)

    def post(self):
        pass


class StudyFindHandler(BaseStudyHandler):
    def get(self):
        open_courses, closed_courses = self.Course.get_all_course(self.get_current_user())
        return self.render('find.html', open_c=open_courses, closed_c=closed_courses)

    def post(self):
        # TODO: must be different behaviour for different: course_type = self.get_argument('courseType')
        course_name = self.get_argument('courseName')
        user_name = self.get_current_user()
        if not self.Course.associate_with_course(user_name, course_name):
            # association already exist!!!
            self.set_status(400)


class StudyManageHandler(BaseStudyHandler):
    def get(self):
        user_in = self.CourseMembers.get_all_study_course(self.get_current_user())
        return self.render('manage.html', user_in=user_in)

    def post(self):
        pass


class StudyInviteHandler(BaseStudyHandler):
    def get(self):
        invites = self.CourseInvites.get_user_invites(self.get_current_user())
        return self.render('invite.html', invites=invites)

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
