from handlers.BaseHandler import BaseHandler, RequestHandler
import tornado.web
from tornado import gen, web, httpclient
from handlers.auth import StreamRegHandler
from settings import sets


class StreamTstHandler(RequestHandler):

    @tornado.web.authenticated
    def get(self):
        key = StreamRegHandler.get_user_key(self.get_current_user())
        return self.render("stream_tst.html", key=key)

    def get_current_user(self):
        '''
        get username from cookie called "user"
        :return: username
        '''
        username = self.get_secure_cookie(sets.SECURITY_COOKIE)
        if username:
            return username.decode()


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