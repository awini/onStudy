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
        raise NotImplementedError
        return self.render('find.html')

    def post(self):
        pass


class StudyManageHandler(BaseStudyHandler):
    def get(self):
        raise NotImplementedError
        return self.render('manage.html')

    def post(self):
        pass


