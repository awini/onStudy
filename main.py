# coding: utf-8
from os.path import join

import tornado.ioloop
import tornado.web
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import settings as sets
from handlers.MainHandler import MainHandler
from handlers.auth import LogoutHandler, LoginHandler
from handlers.static_handlers import CssHandler, AssetsLibHandler


if __name__ == "__main__" and sets.DEBUG:
    from subprocess import call
    import sys
    call(sys.executable + " " + join("scripts", "init_db.py"), shell=True)


from db.DBBridge import DBBridge


class Application(tornado.web.Application):

    def __init__(self):
        engine = create_engine(sets.DB_SCHEME + sets.DB_NAME)
        db_bridge = dict(db_bridge=DBBridge(scoped_session(sessionmaker(bind=engine))))

        handlers = [
            (r"/", MainHandler, db_bridge),
            (r"/login", LoginHandler, db_bridge),
            (r"/logout", LogoutHandler, db_bridge),
            (r"/(.*)/(.*)/(.*)", AssetsLibHandler, db_bridge),
            (r"/css/(.*)", CssHandler, db_bridge),
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
