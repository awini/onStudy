from handlers.BaseHandler import BaseHandler
import tornado.web

class MainHandler(BaseHandler):

    def get(self):
        return self.render("main.html")