from handlers.BaseHandler import BaseHandler
import tornado.web

class MainHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        # self.clear_cookie("user")
        return self.render("main.html")