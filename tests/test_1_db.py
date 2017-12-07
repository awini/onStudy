from os.path import abspath, join, dirname, exists
import sys
from shutil import rmtree

from unittest import main, TestCase

HERE_PATH = dirname(abspath(__file__))
PROJECT_PATH = abspath(join(HERE_PATH, '..'))

sys.path.insert(0, PROJECT_PATH)


from settings import sets
sets.TESTING = True

from scripts.init_db import reinit_db


class Test_1_db_simples(TestCase):

    def setUp(self):
        if exists("tests/data"):
            rmtree("tests/data")
        self.assertFalse(exists("tests/data"))

    def test_1_create_db(self):
        reinit_db(answers={
            "username" : "admin",
            "password" : "1234",
            "email" : "admin@admin.ru",
            "remove_existed" : "y"
        })

    def tearDown(self):
        self.assertTrue(exists("tests/data/tmp/sqlite.db"))
        rmtree("tests/data")
        self.assertFalse(exists("tests/data"))


if __name__=='__main__':
    main()