from uuid import uuid4
from datetime import datetime
import tornado.web

from handlers.BaseHandler import BaseHandler
from handlers.auth import LoginHandler
from settings import sets


# TODO: add support for on_publish_done nginx directive (change lesson state to ended)


class StreamAuthHandler(BaseHandler):
    user_keys = {}

    @staticmethod
    def get_user_key(name):
        key = StreamAuthHandler.user_keys.get(name)
        if not key:
            key = str(uuid4())
            StreamAuthHandler.user_keys[name] = key
        return key

    def check_xsrf_cookie(self):
        return True

    def get(self):
        self.set_status(404)

    def post(self, *args, **kwargs):
        # TODO: it is better to generate unique key for server and display it in course page
        # TODO: and then send this key as ?key= when start strem. This method avoid sending real password/username
        call_type = self.get_argument('call')
        if call_type == 'publish':
            #  server parse
            stream_key = self.get_argument('name')
            pw = self.get_argument('password')

            user = self.dbb.get_user(self.get_argument('username'))

            lesson = self.dbb.activate_lesson(stream_key)
            if lesson and user:
                if LoginHandler.check_password(pw, user.password):
                    # TODO: change lesson status to close
                    # TODO: check lesson time
                    print('server success auth')
                    self.set_status(200)
                else:
                    print('server false auth (wrong user/password)')
                    self.set_status(401)
                    return
            else:
                print('Server false auth (wrong user/stream key)')
                self.set_status(401)
            return

        elif call_type == 'play':
            #  client parse
            if self.request.arguments['key'][0].decode() in StreamAuthHandler.user_keys.values():
                print('Client success auth')
                self.set_status(200)
            else:
                print('Client false auth')
                self.set_status(401)
            return

        print(self.request.arguments)
        self.set_status(401)
        print('unknown call type "{}"'.format(call_type))


class StreamUpdateHandler(BaseHandler):

    def check_xsrf_cookie(self):
        return True

    def get(self):
        self.set_status(404)

    def post(self, *args, **kwargs):
        call_type = self.get_argument('call')
        if call_type == 'update_play':
            #  skip check update from clients
            self.set_status(200)
            return

        elif call_type == 'update_publish':
            stream_key = self.get_argument('name')
            lessons = self.dbb.get_lessons_by_stream(stream_key)
            for l in lessons:
                pass_time = (datetime.now() - l.start_time).total_seconds() / 60  # value in minutes
                print(l.name)
                print(l.start_time)
                print(pass_time, l.duration, sets.STREAM_WINDOW)
                if 0 < pass_time < (l.duration + sets.STREAM_WINDOW):
                    # TODO: change lesson status to close
                    break
            else:
                self.set_status(404)  # any 4xx will break stream
                return
            self.set_status(200)
            return

        print(self.request.arguments)
        print('unknown call type "{}"'.format(call_type))
        self.set_status(401)


class StreamTstHandler(tornado.web.RequestHandler):

    @tornado.web.authenticated
    def get(self):
        key = StreamAuthHandler.get_user_key(self.get_current_user())
        return self.render("stream_tst.html", key=key)

    def get_current_user(self):
        '''
        get username from cookie called "user"
        :return: username
        '''
        username = self.get_secure_cookie(sets.SECURITY_COOKIE)
        if username:
            return username.decode()
