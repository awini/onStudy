from handlers.BaseHandler import BaseHandler
import tornado.web, tornado.websocket
from tornado import gen, web, httpclient

from logging import getLogger
log = getLogger(__name__)


class MainHandler(BaseHandler):

    def get(self):
        # TODO: Example of courses
        # open_lecs = [
        #     {'title':'frontend anywere', 'course':'frontend', 'lector':'Kirill', 'time':'today 16:00', 'long':'01:00'},
        #     {'title':'powerful alghoritms', 'course':'c++', 'lector':'Alex', 'time':'tomorrow 20:00', 'long':'01:00'}
        # ]

        lessons = self.Course.get_open_course_live_lesson()

        return self.render("main.html", lessons=lessons)

class WsUpdateMainHandler(tornado.websocket.WebSocketHandler):
    all_waiters = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        self.all_waiters.add(self)

    def on_close(self):
        self.all_waiters.remove(self)

    def send_update(self, message):
        encoded_message = tornado.escape.json_encode(message)
        self.write_encoded_to_waiter(self, encoded_message)

    def on_message(self, message):
        message = message.replace('\n',r'\n') # FIXME
        message = tornado.escape.json_decode(message)
        self.send_update_to_waiters(self.all_waiters, message)

    @classmethod
    def send_update_to_waiters(cls, waiters, message):
        encoded_message = tornado.escape.json_encode(message)
        for waiter in waiters:
            cls.write_encoded_to_waiter(waiter, encoded_message)

    @classmethod
    def write_encoded_to_waiter(cls, waiter, encoded_message):
        try:
            waiter.write_message(encoded_message)
        except:
            pass


class AboutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        return self.render("about.html")


class RoomHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('''<html><header>
</header>
<body>
hello!
</body>
</html>''')


class StreamingHandler(web.RequestHandler):

    @web.asynchronous
    @gen.coroutine
    def get(self):
        client = httpclient.AsyncHTTPClient()

        #self.write('some opening')
        #self.flush()

        requests = [
            httpclient.HTTPRequest(
                url='http://localhost:8889',
                streaming_callback=self.on_chunk
            )
        ]

        # `map()` doesn't return a list in Python 3
        yield list(map(client.fetch, requests))

        #self.write('some closing')
        self.finish()

    def on_chunk(self, chunk):
        self.write('some chunk')
        self.flush()