from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from db.models import User
from settings import sets


DB_SESSIONS = scoped_session(sessionmaker(bind=create_engine(sets.DB_SCHEME + sets.DB_NAME)))

class DBBridge:
    '''
    DBBridge (Data Base Bridge) uses for recieve/send data to/from DB
    '''

    __instance = None
    __db_sessions = DB_SESSIONS

    def __init__(self):
        if DBBridge.__instance:
            raise BaseException('Use get_instance method!')

    @staticmethod
    def get_instance():
        if DBBridge.__instance:
            return DBBridge.__instance
        return DBBridge()

    def query(self, *args, **kwargs):
        return DBBridge.__db_sessions.query(*args, **kwargs)

    def finish_query(self):
        DBBridge.__db_sessions.remove()

    def get_user(self, username: str):
        with self as query:
            try:
                user = query(User).filter(User.name == username).one()
            except NoResultFound:
                user = None
        return user

    def get_user_by_email(self, email):
        with self as query:
            try:
                user = query(User).filter(User.email == email).one()
            except NoResultFound:
                user = None
        return user

    def create_user(self, username, password, email):
        u = User(name=username, password=password, email=email)
        self.__db_sessions.add(u)
        self.__db_sessions.commit()
        self.finish_query()

    def __enter__(self):
        return DBBridge.__db_sessions.query

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish_query()

