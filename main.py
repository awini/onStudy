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

from DBBridge import DBBridge

class Application(tornado.web.Application):
    def __init__(self):
        engine = create_engine(DB_SCHEME + DB_NAME)
        db_bridge = dict(db_bridge=DBBridge(scoped_session(sessionmaker(bind=engine))))

        handlers = [
            (r"/", MainHandler, db_bridge),
            (r"/login", LoginHandler, db_bridge),
            (r"/logout", LogoutHandler, db_bridge),
            (r"/([^/]*)/([^/]*)/([^/]*)", AssetsLibHandler, db_bridge),
            (r"/css/([^/]*)", CssHandler, db_bridge),
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



if __name__ == "__main__":
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
