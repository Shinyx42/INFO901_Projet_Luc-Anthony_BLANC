from pyeventbus3.pyeventbus3 import *
from Messages import *
from threading import Lock
from Debug import log

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
            
    def broadcast(self, o):
        self.inc_clock()
        msg=BroadcastMessage(o,self.getClock(),self.myId)
        log(str(self.getMyId()) + " broadcast: " + o + " estampile: " + str(msg.getEstampille()),3)
        PyBus.Instance().post(msg)
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, m):
        if not m.isSender(self.getMyId()):
            log(str(self.getMyId()) + ' Processes broadcast: ' + m.getMessage() + " estampile: " + str(m.getEstampille()) + " from " + str(m.getSender()),3)
            self.inc_clock(m.getEstampille())
            self.mailbox.addMsg(m)
    
    def sendTo(self, o, to):
        self.inc_clock()
        message = MessageTo(o,self.getClock(),self.getMyId(),to)
        log(str(self.getMyId()) + " sent: " + o + " estampile: " + str(message.getEstampille()) + " to " + str(to), 3)
        PyBus.Instance().post(message)
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, m):
        if m.isReciever(self.getMyId()):
            log(str(self.getMyId()) + ' Recieve: ' + m.getMessage() + " estampile: " + str(m.getEstampille()) + " from " + str(m.getSender()),3)
            self.inc_clock(m.getEstampille())
            self.mailbox.addMsg(m)
            
class MailBox():
    def __init__(self):
        self.container = []
        self.lockContainer = Lock()
    
    def isEmpty(self):
        return self.container == [] #mutex?
        
    def getMsg(self):
        with self.lockContainer:
            return self.container.pop(0)
            
    def addMsg(self, msg):
        with self.lockContainer:
            self.container.append(msg)
            log(self.container, 4)