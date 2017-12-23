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

    recom = lambda com: com if sys.platform.startswith("win") else ' '.join(com)

    if check_output(recom([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]),
                    shell=True).count(b'already satisfied') != 6:
        raise Exception('!!')

    call(recom([sys.executable, join("scripts", "install.py")]), shell=True)
    call(recom([sys.executable, join("scripts", "init_db.py"), "dont_remove"]), shell=True)



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
    print('server on 0.0.0.0:8888 started.')
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

