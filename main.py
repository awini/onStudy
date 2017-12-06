# coding: utf-8
from os.path import join, dirname

import tornado.ioloop
import tornado.web

from handlers.auth import LogoutHandler, LoginHandler
from handlers.static_handlers import CssHandler, AssetsLibHandler
from handlers.MainHandler import MainHandler

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from settings import DB_NAME, DB_SCHEME


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/([^/]*)/([^/]*)/([^/]*)", AssetsLibHandler),
            (r"/css/([^/]*)", CssHandler),
        ]

        settings = {
            "static_path": join(dirname(__file__), "static"),
            "cookie_secret": "RjBvp2+FSHqRQkKqHjAQdzWsLsq2kUu+lEc28GdAaLA=",  # change in production!!!
            "login_url": "/login",
            "xsrf_cookies": True,
            'template_path': 'template/',
            'debug': True,
        }

        tornado.web.Application.__init__(self, handlers, **settings)
        engine = create_engine(DB_SCHEME + DB_NAME)
        self.db = scoped_session(sessionmaker(bind=engine))


if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
