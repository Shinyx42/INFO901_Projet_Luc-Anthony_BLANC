from pyeventbus3.pyeventbus3 import *
from Messages import *
from threading import Lock
from Debug import log
from time import sleep
#TODO: vérifier les message renvoyer
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
        self.haveToken = Lock()
        self.waitToken = Lock()
        self.cmptSync = 0
        self.lockCmptSync = Lock()
        
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
        if self.alive:
            PyBus.Instance().post(t)
    
    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, t):
        if t.haveToken(self.getMyId()):
            if self.haveToken.locked():
                self.haveToken.release()
            log(str(self.getMyId())+" has the token!",4)
            self.waitToken.acquire(timeout=4)
            self.haveToken.acquire(timeout=4)
            self.waitToken.release()
            self.sendToken()
                
    def requestSC(self):
        self.waitToken.acquire(timeout=4)
        self.haveToken.acquire(timeout=4)
            
    def releaseSC(self):
        if self.haveToken.locked() and self.waitToken.locked():
            self.waitToken.release()
            self.haveToken.release()
            
    def synchronize(self): #A corriger
        self.inc_clock()
        PyBus.Instance().post(MessageSync(self.getClock(),self.getMyId()))
        self.lockCmptSync.acquire()
        while self.alive and self.cmptSync < self.npProcess: #TOOD
            self.lockCmptSync.release()
            sleep(0.5)
            self.lockCmptSync.acquire()
        self.cmptSync -= self.npProcess
        assert(self.cmptSync>=0 or not self.alive)
        self.lockCmptSync.release()
        log(str(self.getMyId())+" is synchronized!",3)
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSync)
    def onSync(self, s):
        self.lockCmptSync.acquire()
        self.cmptSync +=1
        self.lockCmptSync.release()
        log(str(self.getMyId())+" receive synchro from "+str(s.getSender())+" cmpt="+str(self.cmptSync),3)
        self.inc_clock(s.getEstampille()) 
        
    def broadcastSync(self, o,sender): #A modifier
        if self.getMyId() == sender:
            self.inc_clock()
            msg=BroadcastMessageSyncro(o,self.getClock(),self.myId)
            log(str(self.getMyId()) + " broadcast syncro: " + o + " estampile: " + str(msg.getEstampille()),3)
            PyBus.Instance().post(msg)
            self.synchronize()
            return msg
        else:
            while self.alive and not self.mailbox.haveMsgSyncro: #TOOD
                sleep(0.5)
            msg = self.mailbox.getMsgSyncro()
            o = msg.getMessage()
            self.synchronize()
            return msg
            
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessageSyncro)
    def onBroadcastSyncro(self, m):
        if not m.isSender(self.getMyId()):
            log(str(self.getMyId()) + ' Processes broadcast synchro: ' + m.getMessage() + " estampile: " + str(m.getEstampille()) + " from " + str(m.getSender()),3)
            self.inc_clock(m.getEstampille())
            self.mailbox.addMsgSyncro(m)
            
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
        self.msgSyncro = None
        self.haveMsgSyncro = False
    
    def isEmpty(self):
        return self.container == [] #mutex?
        
    def getMsg(self):
        with self.lockContainer:
            return self.container.pop(0)
            
    def addMsg(self, msg):
        with self.lockContainer:
            self.container.append(msg)
            log(self.container, 4)
        
    def addMsgSyncro(self, msg):
        self.msgSyncro = msg
        self.haveMsgSyncro = True
        
    def getMsgSyncro(self):
        self.haveMsgSyncro = False
        return self.msgSyncro