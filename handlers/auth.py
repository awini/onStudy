from handlers.BaseHandler import BaseHandler
import tornado.web

import bcrypt

TST_PASS = b'$2b$12$mjV5cDEl7g6N0xMZcjNwFO5By3CnxCPQH.O1aW/TU9tzcDZUi5bDq'
TST_USER = 'admin'

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument('username')
        pw = self.get_argument('password')
        get_pw = bcrypt.hashpw(pw.encode('utf-8'), TST_PASS)
        if username != TST_USER:
            self.write('WRONG LOGIN!')
            return
        if get_pw != TST_PASS:
            self.write('WRONG PASSWORD')
            return
        self.set_secure_cookie("user", self.get_argument("username"))
        self.redirect("/")


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect('/')