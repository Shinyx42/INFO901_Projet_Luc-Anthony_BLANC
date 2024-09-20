class Message():
    def __init__(self, message="", estampille=0, sender=0):
        self.message=message
        self.estampille=estampille
        self.sender=sender
        
    def getMessage(self):
        return self.message

    def getEstampille(self):
        return self.estampille
        
    def isSender(self, sender):
        return self.sender == sender
    
    def getSender(self):
        return self.sender

class BroadcastMessage(Message):
    def __init__(self, message, estampille, sender):
        super().__init__(message, estampille, sender)
        
class BroadcastMessageSyncro(BroadcastMessage):
    def __init__(self, message, estampille, sender):
        super().__init__(message, estampille, sender)
        
class MessageTo(Message):
    def __init__(self, message, estampille, sender, reciever):
        super().__init__(message, estampille, sender)
        self.reciever=reciever
        
    def isReciever(self, reciever):
        return self.reciever == reciever
    
    def getReciever(self):
        return self.reciever

class MessageToSynchro(MessageTo):
    def __init__(self, message, estampille, sender, reciever):
        super().__init__(message, estampille, sender, reciever)

class Token():
    def __init__(self, nextId):
        self.nextId=nextId
    def haveToken(self, myId):
        return myId==self.nextId

class ChoseId():
    def __init__(self, myTry):
        self.myTry=myTry

class MessageSync(Message):
    def __init__(self,estampille,sender):
        super().__init__("sync", estampille,sender)