#Luc-Anthony BLANC
LOGLVL = 0 #Modifiable pour avoir plus ou moins de logs

from datetime import datetime

def log(msg, lvl=0):
    if lvl<LOGLVL:
        print(datetime.now(), msg)
        