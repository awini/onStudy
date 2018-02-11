# coding: utf-8
from os.path import join

import tornado.ioloop
import tornado.web

from settings import sets

from handlers.MainHandler import MainHandler, RoomHandler, AboutHandler, StreamTstHandler
from handlers.auth import LogoutHandler, LoginHandler, RegisterHandler, StreamRegHandler
from handlers.static_handlers import CssHandler, AssetsLibHandler
from handlers.course_manager import CreateCourseHandler, ManageCourseHandler, CourseHandler, LessonHandler


if __name__ == "__main__" and sets.DEBUG:
    from subprocess import call, DEVNULL, check_output
    import sys

    recom = lambda com: com if sys.platform.startswith("win") else ' '.join(com)

    _text = check_output(recom([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]),
                    shell=True)
    if _text.count(b'already satisfied') != 6:
        raise Exception('Wrong requirements:\n\t' + _text.decode('utf-8'))

    call(recom([sys.executable, join("scripts", "install.py")]), shell=True)
    call(recom([sys.executable, join("scripts", "init_db.py"), "dont_remove"]), shell=True)


class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
            (r"/", MainHandler),
            (r"/about", AboutHandler),
            (r"/room", RoomHandler),
            (r"/stream", StreamTstHandler),
            (r"/auth/login", LoginHandler),
            (r"/auth/logout", LogoutHandler),
            (r"/auth/register", RegisterHandler),
            (r"/auth/stream", StreamRegHandler),
            (r"/(.*)/(.*)/(.*)", AssetsLibHandler),
            (r"/css/(.*)", CssHandler),
            (r"/course", CourseHandler),
            (r"/course/create", CreateCourseHandler),
            (r"/course/manage", ManageCourseHandler),
            (r"/course/lesson", LessonHandler),
        ]

        settings = {
            "static_path": sets.STATIC_PATH,
            "cookie_secret": sets.COOKIE_SECRET,
            "login_url": "/auth/login",
            "xsrf_cookies": True,
            'template_path': sets.TEMPLATE_PATH,
            'debug': sets.DEBUG,
        }

        tornado.web.Application.__init__(self, handlers, **settings)



if __name__ == "__main__":
    print('server on 0.0.0.0:8888 started.')
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

