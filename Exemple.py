from threading import Lock, Thread

from time import sleep

from Com import Com
from Messages import Message
class Process(Thread):
    
    def __init__(self,name, nbProcess):  #Pas npProcess?
        Thread.__init__(self)

        self.com = Com(nbProcess)
        
        self.nbProcess = self.com.getNbProcess()

        self.myId = self.com.getMyId()
        self.setName(name)


        self.alive = True
        self.start()
    

    def run(self):
        loop = 0
        while self.alive:
            msg = Message()
            print(self.getName() + " Loop: " + str(loop) + " id:" + str(self.myId))
            print(self.getName() + " Horloge: " + str(self.com.getClock()))
            #while not self.com.mailbox.isEmpty():
            #    msg=self.com.mailbox.getMsg()
            #    print(self.getName() + " get " + msg.getMessage() + " from " + str(msg.getSender()))
            sleep(1)
            self.com.inc_clock()
            self.com.inc_clock()
            if self.getName() == "P1":
                self.com.broadcast("Hello!")
            self.com.sendTo("I'm "+self.getName()+" and I sendTo P1", 1)
            
            if self.getName() == "P0":
                self.com.sendTo("j'appelle 2 et je te recontacte après", 1)
                
                self.com.sendToSync("J'ai laissé un message à 2, je le rappellerai après, on se sychronise tous et on attaque la partie ?", 2)
                self.com.recevFromSync(msg, 2)
               
                self.com.sendToSync("2 est OK pour jouer, on se synchronise et c'est parti!",1)
                    
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
                    self.com.recevFromSync(msg, 0)

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
                self.com.recevFromSync(msg, 0)
                self.com.sendToSync("OK", 0)

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
                self.com.synchronize()
            loop+=1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.com.stop()
        self.join()

    def waitStopped(self): #supprimer?
        self.join()