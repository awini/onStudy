from handlers.BaseHandler import BaseHandler
from settings import sets


class BaseStudyHandler(BaseHandler):
    def get_template_path(self):
        return sets.TEMPLATE_PATH + 'study'


class StudyLiveHandler(BaseStudyHandler):

    def get(self):
        lessons = self.dbb.get_open_course_live_lesson()
        return self.render('live.html', lessons=lessons)

    def post(self):
        pass

    def on_finish(self):
        self.dbb.finish_query()


class StudyFindHandler(BaseStudyHandler):
    def get(self):
        open_courses, closed_courses = self.dbb.get_all_course(self.get_current_user())
        return self.render('find.html', open_c=open_courses, closed_c=closed_courses)

    def post(self):
        # TODO: must be different behaviour for different: course_type = self.get_argument('courseType')
        course_name = self.get_argument('courseName')
        user_name = self.get_current_user()
        if not self.dbb.associate_with_course(user_name, course_name):
            # association already exist!!!
            self.set_status(400)

    def on_finish(self):
        if self.request.method == 'GET':
            self.dbb.finish_query()


class StudyManageHandler(BaseStudyHandler):
    def get(self):
        user_in = self.dbb.get_all_study_course(self.get_current_user())
        return self.render('manage.html', user_in=user_in)

    def post(self):
        pass

    def on_finish(self):
        if self.request.method == 'GET':
            self.dbb.finish_query()


