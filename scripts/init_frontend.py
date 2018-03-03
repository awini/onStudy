from os.path import exists
from subprocess import call


def install_frontend():
    run('npm i -g bower', check=lambda: not exists("bower.json"))
    run('bower init', check=lambda: not exists("bower.json"))

    add_module('bootstrap')
    add_module('jquery')
    add_module('html5shiv')
    add_module('respond')
    # add_module('videojs')

    add_module('mocha', step='D')


def run(com, check=None):
    if check:
        if not check():
            print('ok:', com)
            return
    ret = call(com, shell=True)
    if ret != 0:
        raise Exception('cant install: ' + com + '\n\n\tMaybe you have no Node.js installed? Please install and put to PATH it.\n')
    print('\tok:', com)


def add_module(name, step='S'):
    run('bower i -' + step + ' '+name, check=lambda: not exists("bower_components/"+name))


if __name__=='__main__':

    install_frontend()
