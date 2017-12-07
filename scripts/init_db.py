from os import makedirs
from os.path import exists, abspath, dirname
from pathlib import Path
from sys import exit, path

if __name__=='__main__':
    path.append('')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import User, Base
from handlers.auth import generate_password
from settings import DB_NAME, DB_SCHEME

ENGINE = create_engine(DB_SCHEME + DB_NAME)

def create_bd_dir():
    path = dirname(abspath(DB_NAME))
    if not exists(path):
        makedirs(path)

def check_bd_file():
    return exists(DB_NAME)


def rm_bd_file():
    bd_fl = Path(DB_NAME)
    try:
        bd_fl.unlink()  # remove file
    except Exception as e:
        print('Error with removing file {}!'.format(DB_NAME))
        print('Error description: \n {}'.format(e))
        exit()
    print('File {} was removed'.format(DB_NAME))


def fill_credits():
    print('Fill user credits')
    username = input('Enter username(admin): ')
    if not username:
        username = 'admin'
    email = input('Enter email(admin@admin.ru): ')
    if not email:
        email = 'admin@admin.ru'

    while 1:
        password = input('Enter password:')
        if password:
            break
        print('Password can`t be empty!')

    return username, email, generate_password(password)


def add_user(username, email, password):
    print('Add user {}'.format(username))
    u = User(name=username, password=password, email=email)
    Session = sessionmaker(bind=ENGINE)
    session = Session()
    session.add(u)
    session.commit()


if __name__ == '__main__':

    print('Search for file {} in current directory'.format(DB_NAME))
    if check_bd_file():
        user_ans = input('Find file "{}"! Remove it? y/n \n'.format(DB_NAME))
        if 'y' not in user_ans.lower():
            print('Exit program, can not initialize when file exist!')
            exit()
        rm_bd_file()
    else:
        print('File not found')

    create_bd_dir()


    print('Start initialize DB')
    Base.metadata.create_all(ENGINE)

    add_user(*fill_credits())

    print('Success')