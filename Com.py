from pyeventbus3.pyeventbus3 import *
from Messages import *
from threading import Lock

class Com():
    
    nbProcessCreated = 0 #A Supprimer
    def __init__(self, npProcess):
        print("init com")
        PyBus.Instance().register(self, self)
        
        #A Modifier
        self.npProcess = npProcess
        self.myId = Com.nbProcessCreated
        Com.nbProcessCreated +=1
        
        self.horloge = 0
        self.lockHorloge = Lock()
        
        self.mailbox = MailBox()
        
    def getNbProcess(self):
        return self.npProcess
        
    def getMyId(self):
        return self.myId
        
    def inc_clock(self, val=0):
        with self.lockHorloge:
            self.horloge = max(val,self.horloge)+1
            
    def getClock(self):
        with self.lockHorloge:
            return self.horloge
            
class MailBox():
    def __init__(self):
        self.empty = True
        self.container = []
        self.lockContainer = Lock()
    
    def isEmpty(self):
        return self.empty #mutex?
        
    def getMsg(self):
        with self.lockContainer:
            return self.container.pop(0)
            
    def addMsg(self, msg):
        with self.lockContainer:
            self.container.append(msg)