# coding: utf-8
from os.path import join

import tornado.ioloop
import tornado.web

from settings import sets

from handlers.MainHandler import MainHandler, RoomHandler
from handlers.auth import LogoutHandler, LoginHandler, RegisterHandler
from handlers.static_handlers import CssHandler, AssetsLibHandler


if __name__ == "__main__" and sets.DEBUG:
    from subprocess import call, DEVNULL, check_output
    import sys

    if check_output([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], shell=True).count(b'already satisfied') != 6:
        raise Exception('!!')

    call([sys.executable, join("scripts", "install.py")], shell=True)
    call([sys.executable, join("scripts", "init_db.py")], shell=True)



class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
            (r"/", MainHandler),
            (r"/room", RoomHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/(.*)/(.*)/(.*)", AssetsLibHandler),
            (r"/css/(.*)", CssHandler),
            (r"/register", RegisterHandler),
        ]

        settings = {
            "static_path": sets.STATIC_PATH,
            "cookie_secret": sets.COOKIE_SECRET,
            "login_url": "/login",
            "xsrf_cookies": True,
            'template_path': 'template/',
            'debug': sets.DEBUG,
        }

        tornado.web.Application.__init__(self, handlers, **settings)



if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

