from handlers.BaseHandler import BaseHandler
from tornado.web import authenticated

from logging import getLogger
log = getLogger(__name__)


class MaterialHandler(BaseHandler):
    
    @authenticated
    def get(self, file_name):
        # TODO: materials for private and closed courses can be downloaded only by users, that registred on this courses
        file_path, material = self.LessonMaterial.get_with_path(file_name)
        if not file_path:
            self.set_status(400)
            return
        self.set_header('Content-Type', 'application/force-download')
        self.set_header('Content-Disposition', 'attachment; filename={}'.format(material.pretty_name))
        file = file_path.open(mode='rb')
        while True:
            try:
                _buffer = file.read(4096)
                if _buffer:
                    self.write(_buffer)
                else:
                    file.close()
                    self.finish()
            except Exception as E:
                log.error(E)
                self.set_status(404)
                return