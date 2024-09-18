class Message():
    def __init__(self, message, estampille):
        self.message=message
        self.estampille=estampille

    def getMessage(self):
        return self.message

    def getEstampille(self):
        return self.estampille

class BroadcastMessage(Message):
    def __init__(self, message, estampille, sender):
        super().__init__(message, estampille)
        self.sender=sender
    
    def isSender(self, sender):
        return self.sender == sender
    
    def getSender(self):
        return self.sender
        
class MessageTo(BroadcastMessage):
    def __init__(self, message, estampille, sender, reciever):
        super().__init__(message, estampille, sender)
        self.reciever=reciever
        
    def isReciever(self, reciever):
        return self.reciever == reciever
    
    def getReciever(self):
        return self.reciever

class Token():
    def __init__(self, nextId):
        self.nextId=nextId
    def haveToken(self, myId):
        return myId==self.nextId
        
class MessageSyncro(Message):
    def __init__(self,estampille):
        super().__init__("sync", estampille)
        