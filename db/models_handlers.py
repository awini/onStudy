from db.models import CourseMembers, Course, User, Lesson, CourseInvites
from db.DBBridge import DBBridge


class DbHandlerBase:

    def __init__(self, dbb: DBBridge):
        self.dbb = dbb


class UserHandler(DbHandlerBase):

    @staticmethod
    @DBBridge.get_session
    def get_user(session, username: str):
        user = session.query(User).filter(User.name == username).one_or_none()
        return user
