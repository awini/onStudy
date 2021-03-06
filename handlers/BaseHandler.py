from tornado.web import RequestHandler
from db.DBBridge import DBBridge
from settings import sets
from db.models_handlers import (UserHandler, LessonHandler, CourseHandler, CourseMembersHandler, OwnerAccess,
                                CourseInvitesHandler, LessonMaterialHandler, HomeWorkHandler,
                                HomeWorkAnswerHandler, CourseAccessHandler, LessonAccessHandler)


class BaseHandler(RequestHandler):
    '''
    Base class for all handlers in project.
    '''

    User = UserHandler
    CourseAccess = CourseAccessHandler
    LessonAccess = LessonAccessHandler
    Lesson = LessonHandler
    Course = CourseHandler
    CourseMembers = CourseMembersHandler
    CourseInvites = CourseInvitesHandler
    LessonMaterial = LessonMaterialHandler
    HomeWork = HomeWorkHandler
    HomeWorkAnswer = HomeWorkAnswerHandler
    OwnerAccess = OwnerAccess

    def get_current_user(self):
        '''
        get username from cookie called "user"
        :return: username
        '''
        username = self.get_secure_cookie(sets.SECURITY_COOKIE)
        if username:
            return username.decode()
        return

    @property
    def db(self):
        return self.dbb

    @property
    def dbb(self):
        return DBBridge.get_instance()

    def get_template_path(self):
        # Default behavior for handlers - return path 'template/'
        return sets.TEMPLATE_PATH
