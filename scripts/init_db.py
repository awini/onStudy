from os import makedirs
from os.path import exists, abspath, dirname
from pathlib import Path
from sys import exit, path

if __name__=='__main__':
    path.append('')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import User, Base
from handlers.auth import RegisterHandler
from settings import sets

ENGINE = create_engine(sets.DB_SCHEME + sets.DB_NAME)

def create_bd_dir():
    path = dirname(abspath(sets.DB_NAME))
    if not exists(path):
        makedirs(path)

def check_bd_file():
    return exists(sets.DB_NAME)


def rm_bd_file():
    bd_fl = Path(sets.DB_NAME)
    try:
        bd_fl.unlink()  # remove file
    except Exception as e:
        print('\tError with removing file {}!'.format(sets.DB_NAME))
        print('\tError description: \n {}'.format(e))
        exit()
    print('\tFile {} was removed'.format(sets.DB_NAME))


def fill_credits(answers):
    print('\tFill user credits')
    username = answers["username"] if "username" in answers else input('Enter username(admin): ')
    if not username:
        username = 'admin'
    email = answers["email"] if "email" in answers else input('Enter email(admin@admin.ru): ')
    if not email:
        email = 'admin@admin.ru'

    while 1:
        password = answers["password"] if "password" in answers else input('Enter password:')
        if password:
            break
        print('\tPassword can`t be empty!')

    return username, email, RegisterHandler.generate_password(password)


def add_user(username, email, password):
    print('\tAdd user {}'.format(username))
    u = User(name=username, password=password, email=email)
    Session = sessionmaker(bind=ENGINE)
    session = Session()
    session.add(u)
    session.commit()


def prepare_db_dir(answers):
    #print('\tSearch for file {} in current directory'.format(sets.DB_NAME))
    if check_bd_file():
        user_ans = answers["remove_existed"] if "remove_existed" in answers else input('Find file "{}"! Remove it? y/n \n'.format(sets.DB_NAME))

        if 'y' not in user_ans.lower():
            #print('Exit program, can not initialize when file exist!')
            exit()

        rm_bd_file()
    else:
        print('\tFile not found')

    create_bd_dir()


def reinit_db(answers={}):
    prepare_db_dir(answers)

    print('\tStart initialize DB')
    Base.metadata.create_all(ENGINE)

    add_user(*fill_credits(answers))

    print('\tSuccess')


if __name__ == '__main__':
    import sys

    answers = {}
    if 'dont_remove' in sys.argv:
        answers['remove_existed'] = 'n'

    reinit_db(answers)