from datetime import datetime
import sys
from subprocess import call, DEVNULL, check_output, Popen, PIPE
from datetime import datetime
from os.path import join


def init_all():
    print('[ INIT ]')
    init_start = datetime.now()

    print('check requirements...')
    _text = install(sys.executable, "-m pip install -r requirements.txt")
    if _text.count(b'already satisfied') != 6 and not (
            b'Successfully installed' in _text and b'fail' not in _text.lower()):
        raise Exception('Wrong requirements:\n\t' + _text.decode('utf-8'))

    print('check frontend requirements...')
    _text = install(sys.executable, join("scripts", "init_frontend.py"), ok_lines=(b'ok:',))
    if _text.count(b'ok:') != 7:
        raise Exception('Wrong frontend requirements:\n\t' + _text.decode('utf-8'))

    print('check db...')
    call(_com([sys.executable, join("scripts", "init_db.py"), "dont_remove"]), shell=True)
    print('[ INIT ] fin into: ', datetime.now() - init_start)


def install(*args, **kwargs):
    ok_lines = kwargs.get('ok_lines', (b'Requirement already satisfied',))

    init_start = datetime.now()
    lines = []
    command = com(*args)

    p = Popen(command, shell=True, stdout=PIPE)

    count = 0
    while True:
        line = p.stdout.readline()
        if len(line) == 0:
            break
        ok = False
        for li in ok_lines:
            if li in line:
                ok = True
                break
        lines.append(line)
        if ok:
            continue
        line = line.decode('utf-8').rstrip()
        print('\t' + line)
        count += 1

    p.stdout.close()
    p.terminate()

    if count > 0:
        print('[ OK ]', '"'+com2str(command)+'"', 'in:', datetime.now() - init_start)

    return b''.join(lines)


_com = lambda com: com if sys.platform.startswith("win") else ' '.join(com)


def com(*args):
    pp = []
    for a in args:
        pp += a.split(' ')
    return _com(pp)


def com2str(command):
    if type(command) in (list, tuple):
        command = ' '.join(command)
    return command