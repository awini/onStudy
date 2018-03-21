from sys import path, exit
from pathlib import Path
from datetime import datetime, timedelta, date
from uuid import uuid4

if __name__=='__main__':
    path.append('')

from db.DBBridge import DBBridge
from db.models import *
from handlers.auth import RegisterHandler
from settings import sets


NOW = datetime.now()

INIT_DATA = {
    'Peter Parker': {
        'All About Python': {
            'description': 'In this course you learn all about Python',
            'mode': Course.OPEN,
            'state': Course.LIVE,
            'lessons': {
                'Part 1': {
                    'description': 'Some basic concept...',
                    'position': 0,  # 0 = today (NOW), -1 = yesterday, 1 = tomorow, 2 = add 2 days
                    'materials': {
                        'presentation1.txt': 'Just some text in presentation1.txt',
                        'blablabla': 'Just some text in presentation2.txt',
                    }
                },
                'Part 2': {
                    'description': 'Some aditional concept...',
                    'position': 1,
                },
            },
        },
        'All About Golang': {
            'description': 'In this course you learn all about Golang',
            'mode': Course.OPEN,
            'state': Course.LIVE,
            'lessons': {
                'Intro in GO': {
                    'description': 'Why, Where, Who, How',
                    'position': -1,
                },
                'Try Go': {
                    'description': 'standart operatorors and library',
                    'position': 0,
                },
                'Deep in Go': {
                    'description': 'In this course you will know about interface, multithreading, methods...',
                    'position': 1,
                }
            },
        },
    },
    'Tony Stark': {
        'Tornado OR Django?': {
                'description': 'Comparison two framework, their cons and pros',
                'mode': Course.CLOSED,
                'state': Course.LIVE,
                'lessons': {
                    'What about Django?': {
                        'description': 'Deep in Django framework, discuss pros and cons...',
                        'position': 0,  # 0 = today (NOW), -1 = yesterday, 1 = tomorow
                    },
                    'And what about tornado?': {
                        'description': 'Deep in Tornado framework, discuss pros and cons...',
                        'position': 1,
                    },
                    'So what I must choose!?': {
                        'description': 'How to make right dessision base on your requerements',
                        'position': 2
                    },
                },
        },
    },
    'Bruce Wayne': {
        'Databases: SQL and NoSQL': {
            'description': 'In this course you learn all about databases',
            'mode': Course.OPEN,
            'state': Course.LIVE,
            'lessons': {
                'Part 1': {
                    'description': 'Some basic concept...',
                    'position': 1,  # 0 = today (NOW), -1 = yesterday, 1 = tomorow
                    'materials': {
                        'presentation1.txt': 'Just some text in presentation1.txt',
                        'blablabla': 'Just some text in presentation2.txt',
                    }
                },
                'Part 2': {
                    'description': 'Some aditional concept...',
                    'position': 2,
                },
            },
        },
        'Frontend': {
            'description': 'In this course you learn how to make frontend',
            'mode': Course.OPEN,
            'state': Course.LIVE,
            'lessons': {
                'Intro in GO': {
                    'description': 'Why, Where, Who, How',
                    'position': -1,
                },
                'Try Go': {
                    'description': 'standart operatorors and library',
                    'position': 0,
                },
                'Deep in Go': {
                    'description': 'In this course you will know about interface, multithreading, methods...',
                    'position': 1,
                }
            },
        },
    },
}


@DBBridge.modife_db
def fill(session):
    for u in INIT_DATA:
        user = User(name=u, password=RegisterHandler.generate_password(u), email='{}@{}.ru'.format(u, u))
        session.add(user)
        session.commit()
        for c, c_args in INIT_DATA[u].items():
            invite_url = str(uuid4()) if c_args['mode'] == Course.PRIVATE else None
            course = Course(
                name=c,
                description=c_args['description'],
                owner=user.id,
                mode=c_args['mode'],
                state=c_args['state'],
                invite_url=invite_url,
            )
            session.add(course)
            session.commit()
            if 'lessons' not in c_args:
                continue

            for l, l_args in INIT_DATA[u][c]['lessons'].items():
                start_time = NOW + timedelta(days=l_args['position'])
                if start_time.day == NOW.day:
                    state = Lesson.LIVE
                elif start_time.day > NOW.day:
                    state = Lesson.WAITING
                else:
                    state = Lesson.ENDED

                lesson = Lesson(
                    name=l,
                    description=l_args['description'],
                    start_time=start_time,
                    duration=60,
                    state=state,
                    course=course.id,
                    stream_key=str(uuid4()),
                    stream_pw=str(uuid4()).split('-')[-1],
                )
                session.add(lesson)
                session.commit()
                if 'materials' not in l_args:
                    continue
                for m_name, m_content in l_args['materials'].items():
                    file_dir = Path(sets.MEDIA_DIR) / str(date.today())
                    if not file_dir.is_dir():
                        file_dir.mkdir()

                    file_path = file_dir / str(uuid4())
                    file_path.write_text(m_content)

                    material = LessonMaterial(
                        pretty_name=m_name,
                        real_name=file_path.name,
                        parent_dir=file_path.parts[-2],
                        lesson=lesson.id,
                    )
                    session.add(material)
                    session.commit()


def check_db():
    bd_path = Path() / sets.DB_NAME
    if not bd_path.is_file():
        print('Can`t find BD file on {}. Did you forgot to init db?'.format(bd_path))
        exit(1)


if __name__ == '__main__':
    check_db()
    fill()
