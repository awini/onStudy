from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.exc import NoResultFound
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=30))
    password = Column(String(length=60))
    email = Column(String(length=60))


def get_user(session: scoped_session, username: str):
    try:
        user = session.query(User).filter(User.name == username).one()
    except NoResultFound:
        user = None
    finally:
        session.remove()
    return user
