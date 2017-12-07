
from os.path import join, dirname


DEBUG = True

BOWER_COMPONENTS = 'bower_components'

DB_NAME = 'data/tmp/sqlite.db'
DB_SCHEME = 'sqlite:///'


STATIC_PATH = join(dirname(__file__), "static")

COOKIE_SECRET = "RjBvp2+FSHqRQkKqHjAQdzWsLsq2kUu+lEc28GdAaLA="   # change in production!!!