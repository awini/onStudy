from handlers.BaseHandler import BaseHandler
import tornado.web

import bcrypt
from uuid import uuid4

from settings import sets


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html', msg='')

    def get_template_path(self):
        return sets.TEMPLATE_PATH + 'auth'

    def post(self):
        user = self.dbb.get_user(self.get_argument('username'))
        if not user:
            self.render('login.html', msg='Wrong user/password')
            return

        pw = self.get_argument('password')
        if self.check_password(pw, user.password):
            self.set_secure_cookie(sets.SECURITY_COOKIE, user.name)
            self.redirect('/')
        else:
            self.render('login.html', msg='Wrong user/password')

    @staticmethod
    def check_password(user_pw, db_pw):
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
        self.render('register.html', msg='')

    def post(self):
        user = self.get_argument('username')
        password = self.get_argument('password')
        password2 = self.get_argument('password2')
        email = self.get_argument('email')
        err = ''
        if password != password2:
            err += 'Passworm mistmatch\n'
        if self.dbb.get_user(user):
            err += 'User with this name already exist\n'
        if self.dbb.get_user_by_email(email):
            err += 'This email already used\n'
        if err:
            self.render('register.html', msg=err)
            return
        self.dbb.create_user(user, self.generate_password(password), email)
        self.render('login.html', msg='Успешная регистрация!')

    def get_template_path(self):
        return sets.TEMPLATE_PATH + 'auth'

    @staticmethod
    def generate_password(pw):
        return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


class StreamRegHandler(BaseHandler):
    user_keys = {}

    @staticmethod
    def get_user_key(name):
        key = StreamRegHandler.user_keys.get(name)
        if not key:
            key = str(uuid4())
            StreamRegHandler.user_keys[name] = key
        return key

    def check_xsrf_cookie(self):
        return True

    def get(self):
        pass

    def post(self, *args, **kwargs):
        call_type = self.get_argument('call')  # 'publish' for server and 'play' for client
        if call_type == 'publish':
            #  server parse
            stream_key = self.get_argument('name')
            pw = self.get_argument('password')

            user = self.dbb.get_user(self.get_argument('username'))
            course = self.dbb.get_course_by_stream(stream_key)
            if course and user:
                if LoginHandler.check_password(pw, user.password):
                    print('server success auth')
                    self.set_status(200)
                else:
                    print('server false auth (wrong user/password)')
                    self.set_status(401)
                    return
            else:
                print('Server false auth (wrong user/stream key)')
                self.set_status(401)
            return

        elif call_type == 'play':
            #  client parse
            if self.request.arguments['key'][0].decode() in StreamRegHandler.user_keys.values():
                print('Client success auth')
                self.set_status(200)
            else:
                print('Client false auth')
                self.set_status(401)
            return
        self.set_status(401)
        print('unknown call type')
