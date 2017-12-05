# coding: utf-8
from os.path import join, exists

import tornado.ioloop
import tornado.web


BOWER_COMPONENTS = 'bower_components'


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        return self.render("template/main.html")


class AssetsLibHandler(tornado.web.RequestHandler):

    def get(self, type, lib, filename):
        dist_variants = ()
        if type == "js":
            dist_variants = ("dist", "dist/js", "dest")
            self.set_header("Content-Type", "text/js")
        elif type == "css":
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
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/([^/]*)/([^/]*)/([^/]*)", AssetsLibHandler),
        (r"/css/([^/]*)", CssHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
