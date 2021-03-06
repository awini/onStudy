
from os.path import join, dirname


class _Sets:

    _DEBUG = True
    TESTING = False

    BOWER_COMPONENTS = 'bower_components'

    @property
    def DEBUG(self):
        return self._DEBUG

    @DEBUG.setter
    def DEBUG(self, val):
        self._DEBUG = val

    @property
    def DB_NAME(self):
        if self.TESTING:
            return 'tests/data/tmp/sqlite.db'
        return 'data/tmp/sqlite.db'

    DB_SCHEME = 'sqlite:///'

    MEDIA_DIR = join(dirname(__file__), "media", "")

    STATIC_PATH = join(dirname(__file__), "static")

    COOKIE_SECRET = "RjBvp2+FSHqRQkKqHjAQdzWsLsq2kUu+lEc28GdAaLA="   # change in production!!!

    TEMPLATE_PATH = join(dirname(__file__), "template", "")

    SECURITY_COOKIE = 'user'

    STREAM_WINDOW = 15  # val in minutes, that define allowed interval before lesson start and after lesson duration

    RTMP_SERVER = '192.168.100.104'  # nginx rtmp server address (MUST use in any js, templates files)


sets = _Sets()