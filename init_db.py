from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Base

from pathlib import Path
from sys import exit


FILE_NAME = 'sqlite.db'


def check_bd_file():
    cur_dir = Path()
    for file in cur_dir.iterdir():
        if str(file) == FILE_NAME:
            return True
    else:
        return False


def rm_bd_file():
    bd_fl = Path(FILE_NAME)
    try:
        bd_fl.unlink()  # remove file
    except Exception as e:
        print('Erorr with removing file {}!'.format(FILE_NAME))
        print('Error description: \n {}'.format(e))
        exit()
    print('File {} was removed'.format(FILE_NAME))


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

    return username, email, password


def add_user(username, password, email):
    print('Add user {}'.format(username))
    u = User(name=username, password=password, email=email)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(u)
    session.commit()


if __name__ == '__main__':
    engine = create_engine('sqlite:///{}'.format(FILE_NAME))

    print('Search for file {} in current directory'.format(FILE_NAME))
    if check_bd_file():
        user_ans = input('Find file "{}"! Remove it? y/n \n'.format(FILE_NAME))
        if 'y' not in user_ans.lower():
            print('Exit program, can not initialize when file exist!')
            exit()
        rm_bd_file()
    else:
        print('File not found')


    print('Start initialize DB')
    Base.metadata.create_all(engine)

    add_user(*fill_credits())

    print('Success')