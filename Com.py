from pyeventbus3.pyeventbus3 import *
from Messages import *
from threading import Lock
from Debug import log
from time import sleep

class Com():
    
    nbProcessCreated = 0 #A Supprimer
    def __init__(self, npProcess):
        log("init com",3)
        PyBus.Instance().register(self, self)
        
        #A Modifier
        self.npProcess = npProcess
        self.myId = Com.nbProcessCreated
        Com.nbProcessCreated +=1
        
        self.horloge = 0
        self.lockHorloge = Lock()
        self.haveToken = False
        self.waitToken = False
        
        self.mailbox = MailBox()
        
        self.alive = True
        if self.myId == npProcess-1:
            self.sendToken()
        
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
            
    def sendToken(self):
        t = Token((self.myId+1)%self.npProcess)
        if self.alive: #TOOD
            PyBus.Instance().post(t)
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, t):
        if t.haveToken(self.getMyId()):
            log(str(self.getMyId())+" has the token!",4)
            if self.waitToken:
                self.haveToken=True
            else:
                self.sendToken()
                
    def requestSC(self):
        self.waitToken=True
        while self.alive and not self.haveToken: #utiliser mutex + expt
            sleep(0.5)
            
    def releaseSC(self):
        self.waitToken=False
        if self.haveToken:
            self.haveToken=False
            self.sendToken()
            
    def synchronize(self):
        pass
    def broadcastSync(self, o,sender):
        pass
    def sendToSync(self, o, to):
        pass
    def recevFromSync(self, msg, sender):
        pass
    
    def stop(self):
        self.alive = False

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