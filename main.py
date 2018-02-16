# coding: utf-8
import sys
from os.path import join

from settings import sets


if __name__ == "__main__" and sets.DEBUG:
    for a in ('help', '-h', '--help'):
        if a in sys.argv:
            print('''python main.py [init]\n\nCommands:
    init     - for init project on start or reinit on changed requirements.''')
            sys.exit(0)

    if 'init' in sys.argv:
        from scripts.init import init_all
        init_all()


import tornado.ioloop
import tornado.web

from handlers.MainHandler import MainHandler, RoomHandler, AboutHandler
from handlers.auth import LogoutHandler, LoginHandler, RegisterHandler
from handlers.static_handlers import CssHandler, AssetsLibHandler
from handlers.course_manager import CreateCourseHandler, ManageCourseHandler, CourseHandler, LessonHandler
from handlers.stream_handlers import StreamAuthHandler, StreamUpdateHandler, StreamTstHandler
from handlers.study_handlers import StudyFindHandler, StudyLiveHandler, StudyManageHandler


class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
            (r"/", MainHandler),
            (r"/about", AboutHandler),
            (r"/room", RoomHandler),

            (r"/stream", StreamTstHandler),
            (r"/stream/auth", StreamAuthHandler),
            (r"/stream/update", StreamUpdateHandler),

            (r"/auth/login", LoginHandler),
            (r"/auth/logout", LogoutHandler),
            (r"/auth/register", RegisterHandler),

            (r"/(.*)/(.*)/(.*)", AssetsLibHandler),
            (r"/css/(.*)", CssHandler),

            (r"/course", CourseHandler),
            (r"/course/create", CreateCourseHandler),
            (r"/course/manage", ManageCourseHandler),
            (r"/course/lesson", LessonHandler),

            (r"/study/live", StudyLiveHandler),
            ("/study/find", StudyFindHandler),
            ("/study/manage", StudyManageHandler),
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

