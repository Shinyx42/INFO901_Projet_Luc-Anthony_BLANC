#Luc-Anthony BLANC
from threading import Lock, Thread

from time import sleep

from Com import Com

class Process(Thread):
    
    def __init__(self,name, nbProcess): 
        Thread.__init__(self)

        self.com = Com(nbProcess)
        self.nbProcess = self.com.getNbProcess()

        self.myId = -1
        self.setName(name)


        self.alive = True
        self.start()
    

    def run(self):
        loop = 0
        self.com.initialize()
        self.myId = self.com.getMyId()
        msg = self.com.broadcastSync("test",3)
        print(msg.getMessage() + " from " + str(msg.getSender()) + " to " + str(self.com.getMyId()))
        
        while self.alive:
            print(self.getName() + " Loop: " + str(loop) + " id:" + str(self.myId))
            print(self.getName() + " Horloge: " + str(self.com.getClock()))
            self.com.inc_clock()
            self.com.inc_clock()
            if self.getName() == "P1":
                self.com.broadcast("Hello!")
            self.com.broadcastSync("Hello sync!", 3)
            self.com.sendTo("I'm "+self.getName()+" and I sendTo P1", 1)
            
            if self.getName() == "P0":
                self.com.sendTo("j'appelle 2 et je te recontacte après", 1)
                
                self.com.sendToSync("J'ai laissé un message à 2, je le rappellerai après, on se sychronise tous et on attaque la partie ?", 2)
                msg=self.com.recevFromSync( 2)
               
                self.com.sendToSync("2 est OK pour jouer, on se synchronise et c'est parti!",1)
                self.com.mailbox.flush()
                self.com.synchronize()
                    
                self.com.requestSC()
                if self.com.mailbox.isEmpty():
                    print("Catched !")
                    self.com.broadcast("J'ai gagné !!!")
                else:
                    msg = self.com.mailbox.getMsg();
                    print(str(msg.getSender())+" à eu le jeton en premier")
                self.com.releaseSC()


            if self.getName() == "P1":
                if not self.com.mailbox.isEmpty():
                    self.com.mailbox.getMsg()
                    msg = self.com.recevFromSync( 0)
                    self.com.mailbox.flush()
                    self.com.synchronize()
                    
                    self.com.requestSC()
                    if self.com.mailbox.isEmpty():
                        print("Catched !")
                        self.com.broadcast("J'ai gagné !!!")
                    else:
                        msg = self.com.mailbox.getMsg();
                        print(str(msg.getSender())+" à eu le jeton en premier")
                    self.com.releaseSC()
                    
            if self.getName() == "P2":
                msg = self.com.recevFromSync( 0)
                self.com.sendToSync("OK", 0)
                self.com.mailbox.flush()
                self.com.synchronize()
                    
                self.com.requestSC()
                if self.com.mailbox.isEmpty():
                    print("Catched !")
                    self.com.broadcast("J'ai gagné !!!")
                else:
                    msg = self.com.mailbox.getMsg();
                    print(str(msg.getSender())+" à eu le jeton en premier")
                self.com.releaseSC()
            if self.getName() == "P3":
                self.com.mailbox.flush()
                self.com.synchronize()
            loop+=1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.com.stop()
        self.join()

    def waitStopped(self): #supprimer?
        self.join()