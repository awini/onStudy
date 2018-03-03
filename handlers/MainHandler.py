from handlers.BaseHandler import BaseHandler
import tornado.web
from tornado import gen, web, httpclient

from logging import getLogger
log = getLogger(__name__)


class MainHandler(BaseHandler):

    def get(self):
        # TODO: put here info from db
        open_lecs = [
            {'title':'frontend anywere', 'course':'frontend', 'lector':'Kirill', 'time':'today 16:00', 'long':'01:00'},
            {'title':'powerful alghoritms', 'course':'c++', 'lector':'Alex', 'time':'tomorrow 20:00', 'long':'01:00'}
        ]

        return self.render("main.html", open_lecs=open_lecs)


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