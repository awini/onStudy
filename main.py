# coding: utf-8
from os.path import join, exists, dirname

import tornado.ioloop
import tornado.web


BOWER_COMPONENTS = 'bower_components'


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        return self.render("main.html")


class AssetsLibHandler(tornado.web.RequestHandler):

    def get(self, static_type, lib, filename):
        dist_variants = ()
        if static_type == "js":
            dist_variants = ("dist", "dist/js", "dest")
            self.set_header("Content-Type", "text/js")
        elif static_type == "css":
            dist_variants = ("dist/css",)
            self.set_header("Content-Type", "text/css")

        for dist in dist_variants:
            fullpath = join(BOWER_COMPONENTS, lib, dist, filename)
            if exists(fullpath):
                self.write(open(fullpath).read())
                return
        self.send_error(404)

class CssHandler(tornado.web.RequestHandler):

    def get(self, filename):
        self.set_header("Content-Type", "text/css")

        fullpath = join("template", "css", filename)
        if exists(fullpath):
            self.write(open(fullpath).read())
            return
        self.send_error(404)


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
        (r"/([^/]*)/([^/]*)/([^/]*)", AssetsLibHandler),
        (r"/css/([^/]*)", CssHandler),
    ], **settings)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
