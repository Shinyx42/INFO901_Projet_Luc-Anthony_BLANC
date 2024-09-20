LOGLVL = 0

from datetime import datetime

def log(msg, lvl=0):
    if lvl<LOGLVL:
        print(datetime.now(), msg)
        