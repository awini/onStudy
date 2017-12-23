from handlers.BaseHandler import BaseHandler
import tornado.web

import bcrypt

from settings import sets


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html', err='')

    def get_template_path(self):
        return sets.TEMPLATE_PATH + 'auth'

    def post(self):
        user = self.dbb.get_user(self.get_argument('username'))
        if not user:
            self.render('login.html', err='Wrong user/password')
            return

        pw = self.get_argument('password')
        if self.check_password(pw, user.password):
            self.set_secure_cookie(sets.SECURITY_COOKIE, user.name)
            self.redirect('/')
        else:
            self.render('login.html', err='Wrong user/password')

    def check_password(self, user_pw, db_pw):
        hash_pw = bcrypt.hashpw(user_pw.encode('utf-8'), db_pw.encode('utf-8'))
        if hash_pw.decode('utf-8') == db_pw:
            return True
        else:
            return False


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect('/')


class RegisterHandler(BaseHandler):
    def get(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

    @staticmethod
    def generate_password(pw):
        return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
