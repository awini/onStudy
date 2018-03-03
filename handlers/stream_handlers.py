from uuid import uuid4
from datetime import datetime
import tornado.web

from handlers.BaseHandler import BaseHandler
from settings import sets

from logging import getLogger
log = getLogger(__name__)

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
        call_type = self.get_argument('call')
        if call_type == 'publish':
            #  server parse

            stream_key = self.get_argument('name')
            stream_pw = self.get_argument('pphrs')

            lesson = self.Lesson.activate_lesson(stream_key, stream_pw)
            if lesson:
                # TODO: WHEN lesson must be close???
                log.info('server success auth')
                self.set_status(200)
            else:
                log.info('Server false auth (wrong user/stream key)')
                self.set_status(401)
            return

        elif call_type == 'play':
            #  client parse
            if self.request.arguments['key'][0].decode() in StreamAuthHandler.user_keys.values():
                log.info('Client success auth')
                self.set_status(200)
            else:
                log.info('Client false auth')
                self.set_status(401)
            return

        self.set_status(401)
        log.error('unknown call type "{}"'.format(call_type))


class StreamUpdateHandler(BaseHandler):

    def check_xsrf_cookie(self):
        return True

    def get(self):
        self.set_status(404)

    def post(self, *args, **kwargs):
        call_type = self.get_argument('call')
        if call_type == 'update_play':
            #  skip check update from clients
            # TODO: or we can add check if stream not alive - send alert to user
            self.set_status(200)
            return

        elif call_type == 'update_publish':
            stream_key = self.get_argument('name')
            stream_pw = self.get_argument('pphrs')
            lesson = self.Lesson.get_by_keys(stream_key, stream_pw)
            pass_time = (datetime.now() - lesson.start_time).total_seconds() / 60
            if 0 < pass_time < (lesson.duration + sets.STREAM_WINDOW):
                self.set_status(200)
            else:
                # TODO: change lesson status to close
                self.set_status(404)  # any 4xx will break stream
            self.set_status(200)
            return

        log.error('unknown call type "{}"'.format(call_type))
        self.set_status(401)


class StreamDoneHandler(BaseHandler):

    def check_xsrf_cookie(self):
        return True

    def get(self):
        self.set_status(404)

    def post(self):
        pphrs = self.get_argument('pphrs', default=None)  # pphrs can be only in streamer side
        stream_key = self.get_argument('name', default=None)
        key = self.get_argument('key', default=None)  # key can be only in client side
        if pphrs:
            #  streamer send DONE
            log.info('interrupt lesson ""'.format(stream_key))
            self.Lesson.stop_lesson(stream_key, pphrs)
        elif key:
            #  client send DONE
            pass


class StreamTstHandler(tornado.web.RequestHandler):

    @tornado.web.authenticated
    def get(self):
        stream_key = self.get_argument('stream_key', default='')
        key = StreamAuthHandler.get_user_key(self.get_current_user())
        return self.render("stream_tst.html", key=key, stream_key=stream_key, rtmp_server=sets.RTMP_SERVER)

    def get_current_user(self):
        '''
        get username from cookie called "user"
        :return: username
        '''
        username = self.get_secure_cookie(sets.SECURITY_COOKIE)
        if username:
            return username.decode()
