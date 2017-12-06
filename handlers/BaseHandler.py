from tornado.web import RequestHandler


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