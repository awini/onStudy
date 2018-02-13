from handlers.BaseHandler import BaseHandler
import tornado.web
from tornado import gen, web, httpclient


class MainHandler(BaseHandler):

    def get(self):
        return self.render("main.html")


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