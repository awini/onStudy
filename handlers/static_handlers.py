from handlers.BaseHandler import BaseHandler

from os.path import join, exists
from settings import sets


class AssetsLibHandler(BaseHandler):

    def get(self, static_type, lib, filename):
        dist_variants = ()
        if static_type == "js":
            dist_variants = ("dist", "dist/js", "dest")
            self.set_header("Content-Type", "text/js")
        elif static_type == "css":
            dist_variants = ("dist/css",)
            self.set_header("Content-Type", "text/css")

        for dist in dist_variants:
            fullpath = join(sets.BOWER_COMPONENTS, lib, dist, filename)
            if exists(fullpath):
                self.write(open(fullpath).read())
                return
        self.send_error(404)


class CssHandler(BaseHandler):

    def get(self, filename):
        self.set_header("Content-Type", "text/css")

        fullpath = join(sets.STATIC_PATH, "css", filename)
        if exists(fullpath):
            self.write(open(fullpath).read())
            return
        self.send_error(404)