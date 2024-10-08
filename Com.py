#Luc-Anthony BLANC
from pyeventbus3.pyeventbus3 import *
from Messages import *
from threading import Lock, Semaphore
from Debug import log
from time import sleep, time
from random import randrange

#TODO: vérifier les message renvoyer
class Com():
    """
    Classe Com: Gère la communication entre différents processus en utilisant un bus d'événements, des messages horodatés, et un algorithme de passage de jeton pour la section critique.

    Attributs:
    ----------
    npProcess : int
        Nombre de processus.
    horloge : int
        Horloge logique pour l'horodatage des événements.
    lockHorloge : Lock
        Verrou pour protéger l'accès à l'horloge.
    haveToken : Lock
        Verrou pour indiquer si le processus possède le jeton.
    waitToken : Lock
        Verrou pour attendre le jeton.
    cmptSync : int
        Compteur de synchronisation.
    semaCmptSync : Semaphore
        Sémaphore pour la synchronisation des processus.
    mailbox : MailBox
        Boîte aux lettres pour stocker les messages reçus.
    alive : bool
        Indique si le processus est actif.
    myId : int
        Identifiant du processus.
    idList : list
        Liste des ID des processus.
    
    Méthodes:
    ---------
    initialize():
        Initialisation du processus à appeler avant toute les autre méthodes
    
    getNbProcess() -> int:
        Retourne le nombre de processus.

    getMyId() -> int:
        Retourne l'identifiant du processus actuel.

    inc_clock(val=0):
        Incrémente l'horloge logique du processus en prenant en compte une valeur externe.

    getClock() -> int:
        Retourne la valeur de l'horloge logique du processus.

    broadcast(o: object):
        Diffuse un message à tous les processus avec horodatage.

    onBroadcast(m: BroadcastMessage):
        Réceptionne et traite un message diffusé par un autre processus.

    sendTo(o: object, to: int):
        Envoie un message direct à un autre processus.

    onReceive(m: MessageTo):
        Réceptionne un message direct et l'ajoute à la boîte aux lettres.

    sendToken():
        Envoie le jeton au processus suivant.

    onToken(t: Token):
        Traite la réception du jeton et gère la section critique.

    requestSC():
        Demande l'accès à la section critique (attente du jeton).

    releaseSC():
        Libère la section critique et passe le jeton.

    synchronize():
        Synchronise les horloges des processus.

    onSync(s: MessageSync):
        Réceptionne un message de synchronisation et met à jour l'horloge.

    broadcastSync(o: object, sender: int) -> BroadcastMessageSyncro:
        Diffuse un message de synchronisation à tous les processus.

    onBroadcastSyncro(m: BroadcastMessageSyncro):
        Traite la réception d'un message de synchronisation diffusé.

    sendToSync(o: object, to: int):
        Envoie un message de synchronisation direct à un autre processus.

    recevFromSync(msg: MessageToSynchro, sender: int):
        Traite la réception d'un message de synchronisation direct.

    onMessageToSynchro(m: MessageToSynchro):
        Traite la réception d'un message direct de synchronisation.

    choseId() -> int:
        Choisit un identifiant unique pour le processus actuel.

    onChoseId(m: ChoseId):
        Traite la réception d'une proposition d'ID d'un autre processus.

    stop():
        Arrête le processus en le mettant hors service.
    """
    
    def __init__(self, npProcess):
        log("init com",3)
        PyBus.Instance().register(self, self)
        
        self.idList = []
        
        self.npProcess = npProcess
        self.lockIdList = Lock()
        
        
        self.horloge = 0
        self.lockHorloge = Lock()
        self.haveToken = Lock()
        self.waitToken = Lock()
        self.cmptSync = 0
        self.semaCmptSync = Semaphore(0)
        
        self.mailbox = MailBox()
        
        self.alive = True
        
        self.myId = -1
        self.tempId = 0
        
        
    def initialize(self):
        sleep(2)
        log("initialize")
        self.myId = self.choseId()
        log(str(self.myId))
        self.synchronize()
        if self.myId == 0:
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
        log("token",4)
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
            
    def synchronize(self): #A verifier
        self.inc_clock()
        PyBus.Instance().post(MessageSync(self.getClock(),self.getMyId()))
        #sleep(1)
        for _ in range(self.npProcess):
            self.semaCmptSync.acquire(timeout=2)
            log(str(self.getMyId())+" acquire a semaCmptSync "+" cmpt="+str(self.cmptSync),3)
            if not self.alive:
                return
        log(str(self.getMyId())+" is synchronized!",3)
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageSync)
    def onSync(self, s):
        self.semaCmptSync.release()
        self.cmptSync +=1
        log(str(self.getMyId())+" receive synchro from "+str(s.getSender())+" cmpt="+str(self.cmptSync),3)
        if self.cmptSync == self.npProcess:
            self.cmptSync = 0
        self.inc_clock(s.getEstampille()) 
        
    def broadcastSync(self, o,sender): #A verifier
        if self.getMyId() == sender:
            self.inc_clock()
            msg=BroadcastMessageSyncro(o,self.getClock(),self.myId)
            log(str(self.getMyId()) + " broadcast syncro: " + o + " estampile: " + str(msg.getEstampille()),3)
            PyBus.Instance().post(msg)
            self.synchronize()
            return msg
        else:
            log(str(self.getMyId())+" is alive? "+ str(self.alive),3)
            msg = self.mailbox.getMsgSyncro()
            log(isinstance(msg, BroadcastMessageSyncro),4)
            self.synchronize()
            return msg
            
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessageSyncro)
    def onBroadcastSyncro(self, m):
        if not m.isSender(self.getMyId()):
            log(str(self.getMyId()) + ' Processes broadcast synchro: ' + m.getMessage() + " estampile: " + str(m.getEstampille()) + " from " + str(m.getSender()),3)
            self.inc_clock(m.getEstampille())
            self.mailbox.addMsgSyncro(m)
            
    def sendToSync(self, o, to):
        self.inc_clock()
        msg=MessageToSynchro(o,self.getClock(),self.myId,to)
        log(str(self.getMyId()) + " message to " +str(to)+ " syncro: " + o + " estampile: " + str(msg.getEstampille()),3)
        PyBus.Instance().post(msg)
        msg=self.mailbox.getMsgSyncro()
        log(isinstance(msg, MessageToSynchro), 4)
        
    def recevFromSync(self, sender): #A modifier
        self.inc_clock()
        msg=self.mailbox.getMsgSyncro()
        log(str(self.getMyId()) + " recieved from " +str(msg.getSender())+ " syncro: " + msg.getMessage() + " estampile: " + str(msg.getEstampille()),3)
        log(isinstance(msg, MessageToSynchro),4)
        ack=MessageToSynchro("ack",self.getClock(),self.myId,sender)
        PyBus.Instance().post(ack)
        return msg
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageToSynchro)
    def onMessageToSynchro(self, m):
        if m.isReciever(self.getMyId()):
            log(str(self.getMyId()) + ' Processes messageTo synchro: ' + m.getMessage() + " estampile: " + str(m.getEstampille()) + " from " + str(m.getSender()),3)
            self.inc_clock(m.getEstampille())
            self.mailbox.addMsgSyncro(m)
    
    def choseId(self): #bug: n'assure pas un id unique
        while True:
            myTry = randrange(255)
            log("my try: "+str(myTry))
            PyBus.Instance().post(ChoseId(myTry))
            sleep(2)
            with self.lockIdList:
                self.idList.sort()
                for i in range(len(self.idList)):
                    if self.idList[i]==myTry:
                        return i
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=ChoseId)
    def onChoseId(self, m):
        log("receive try: "+ str(m.myTry))
        with self.lockIdList:
            if m.myTry in self.idList:
                self.idList.remove(m.myTry)
            else:
                self.idList.append(m.myTry)

    def stop(self):
        self.alive = False

class MailBox():
    def __init__(self):
        self.container = []
        self.lockContainer = Lock()
        self.msgSyncro = []
        self.lockMsgSynchro = Lock()
        self.semaMsgSynchro = Semaphore(0)
    
    def isEmpty(self):
        return self.container == [] #mutex?
    
    def flush(self):
        while not self.isEmpty():
            msg=self.getMsg()
            log("FLUSH: " + msg.getMessage() + " from " + str(msg.getSender()),3)
    
    def getMsg(self):
        with self.lockContainer:
            return self.container.pop(0)
            
    def addMsg(self, msg):
        with self.lockContainer:
            self.container.append(msg)
            log(self.container, 4)
        
    def addMsgSyncro(self, msg):
        with self.lockMsgSynchro:
            self.msgSyncro.append(msg)
            self.semaMsgSynchro.release()
            log(self.msgSyncro, 4)
        
    def getMsgSyncro(self): #A ameliorer
        self.semaMsgSynchro.acquire(timeout=2)
        with self.lockMsgSynchro:
            if self.haveMsgSyncro():
                return self.msgSyncro.pop(0)
            else:
                return Message()
    
    def haveMsgSyncro(self):
        return self.msgSyncro != []