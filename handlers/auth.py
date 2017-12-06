from handlers.BaseHandler import BaseHandler
import tornado.web

from models import get_user

import bcrypt


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        user = get_user(self.application.db, self.get_argument('username'))
        if not user:
            self.write('Wrong user/password')
            return

        pw = self.get_argument('password')
        if check_password(pw, user.password):
            self.write('User and pass OK')
        else:
            self.write('Wrong user/password')


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect('/')


def check_password(user_pw, db_pw):
    hash_pw = bcrypt.hashpw(user_pw.encode('utf-8'), db_pw.encode('utf-8'))
    if hash_pw.decode('utf-8') == db_pw:
        return True
    else:
        return False


def generate_password(pw):
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')