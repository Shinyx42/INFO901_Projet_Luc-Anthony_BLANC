LOGLVL = 4
def log(msg, lvl=0):
    if lvl<LOGLVL:
        print(msg)