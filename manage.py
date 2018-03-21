from sys import argv, executable
from subprocess import call

SCRIPTS = (
    'init_db',
    'init_content',
)

def execute(script_name):
    com = executable + " scripts/" + script_name + ".py"
    ret = call(com, shell=True)
    return ret == 0

for script_name in SCRIPTS:
    if script_name not in argv:
        continue
    if not execute(script_name):
        break


