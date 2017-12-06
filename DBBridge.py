from models import User
from sqlalchemy.orm.exc import NoResultFound


class DBBridge:
    '''
    DBBridge (Data Base Bridge) uses for recieve/send data to/from DB
    '''

    def __init__(self, scoped_session):
        self.s = scoped_session

    def get_user(self, username: str):
        try:
            user = self.s.query(User).filter(User.name == username).one()
        except NoResultFound:
            user = None
        finally:
            self.s.remove()
        return user