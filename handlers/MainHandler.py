from handlers.BaseHandler import BaseHandler
import tornado.web


class MainHandler(BaseHandler):

    def get(self):
        return self.render("main.html")


class RoomHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('''<html><header>
</header>
<body>
hello!
</body>
</html>''')