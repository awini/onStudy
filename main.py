# coding: utf-8
from os.path import join, dirname

import tornado.ioloop
import tornado.web

from handlers.auth import LogoutHandler, LoginHandler
from handlers.static_handlers import CssHandler, AssetsLibHandler
from handlers.MainHandler import MainHandler


BOWER_COMPONENTS = 'bower_components'


def make_app():
    settings = {
        "static_path": join(dirname(__file__), "static"),
        "cookie_secret": "RjBvp2+FSHqRQkKqHjAQdzWsLsq2kUu+lEc28GdAaLA=",  # change in production!!!
        "login_url": "/login",
        "xsrf_cookies": True,
        'template_path': 'template/',
        'debug': True,
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/([^/]*)/([^/]*)/([^/]*)", AssetsLibHandler),
        (r"/css/([^/]*)", CssHandler),
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
