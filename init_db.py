import sqlalchemy
from sqlalchemy import create_engine




if __name__ == '__main__':
    engine = create_engine('sqlite:///sqlite.db')