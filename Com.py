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
        
    def getNbProcess(self):
        return self.npProcess
        
    def getMyId(self):
        return self.myId