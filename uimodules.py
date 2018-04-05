import tornado.web


class CursEntry(tornado.web.UIModule):

    def render(self, curs, show_comments=False, button_title="Add to study list"):
        return self.render_string(
            "modules/curs-entry.html", curs=curs, show_comments=show_comments, button_title=button_title)


class LessonEntry(tornado.web.UIModule):

    def render(self, lesson, show_comments=False):
        return self.render_string(
            "modules/lesson-entry.html", lesson=lesson, show_comments=show_comments)
