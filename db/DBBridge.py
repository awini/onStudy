from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from settings import sets

from logging import getLogger
log = getLogger(__name__)

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

    @staticmethod
    def query_db(func):
        def wrapper(*args, **kwargs):
            return func(DBBridge.__db_sessions, *args, **kwargs)
        return wrapper

    @staticmethod
    def modife_db(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(DBBridge.__db_sessions, *args, **kwargs)
                DBBridge.__db_sessions.commit()
                return result
            except:
                DB_SESSIONS.rollback()
                raise
        return wrapper

    @staticmethod
    def add_to_db(func):
        # NOT USED NOW!! Use DBBridge.modife_db
        def wrapper(*args, **kwargs):
            try:
                model = func(*args, **kwargs)
                if model:
                    DBBridge.__db_sessions.add(model)
                    DBBridge.__db_sessions.commit()
                return model
            except IntegrityError:
                log.exception('IntegrityError from func "{}" on model "{}"'.format(func, model))
                raise
            except:
                DB_SESSIONS.rollback()
                raise
        return wrapper

    @staticmethod
    def rm_from_db(func):
        # NOT USED NOW!! Use DBBridge.modife_db
        def wrapper(*args, **kwargs):
            try:
                model = func(*args, **kwargs)
                if model:
                    DBBridge.__db_sessions.delete(model)
                    DBBridge.__db_sessions.commit()
                return model
            except:
                DB_SESSIONS.rollback()
                raise
        return wrapper



