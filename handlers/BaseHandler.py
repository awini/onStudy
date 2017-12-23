from tornado.web import RequestHandler
from db.DBBridge import DBBridge
from settings import sets


class BaseHandler(RequestHandler):
    '''
    Base class for all handlers in project.
    '''

    def get_current_user(self):
        '''
        get username from cookie called "user"
        :return: username
        '''
        return self.get_secure_cookie("user")

    @property
    def dbb(self):
        return DBBridge.get_instance()

    def get_template_path(self):
        # Default behavior for handlers - return path 'template/'
        return sets.TEMPLATE_PATH