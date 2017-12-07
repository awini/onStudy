from os.path import exists
from subprocess import call


def run(com, check=None):
    if check:
        if not check():
            return
    call(com, shell=True)


if __name__=='__main__':

    run('npm i -g bower', check = lambda: not exists("bower_components"))
    run('bower init', check = lambda: not exists("bower_components") or not exists("bower.json"))
    run('bower i -S bootstrap', check = lambda: not exists("bower_components/bootstrap"))
    run('bower i -S jquery', check = lambda: not exists("bower_components/jquery"))
    run('bower i -S html5shiv', check = lambda: not exists("bower_components/html5shiv"))
    run('bower i -S respond', check = lambda: not exists("bower_components/respond"))
    run('bower i -D mocha', check = lambda: not exists("bower_components/mocha"))