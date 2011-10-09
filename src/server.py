import socket
from time import time
class Player:
    def __init__(self, addr):
        self.addr = addr
        self.connectMessage = ''
        self.lastMsg = time()
        
    def addConnect(self, data):
        self.connectData = data
        
    def update(self):
        self.lastMsg = time()
        print "updating timestamp"
        
class GameServer:
    def __init__(self):

        self.host = ""
        self.port = 5432
        self.bufsize = 2048
        self.addr = (self.host,self.port)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socket.setblocking(0)
        self.socket.settimeout(3)
        self.socket.bind(self.addr)

        self.players = {}

    def testTimout(self):
        for client_addr in self.players.keys():
            print "ckecking times"
            if time() > self.players[client_addr].lastMsg + 10:
                pass #disconnect that laggy guy already...
                print "disconnecting,end game, gone for good."  
                if len(self.players) ==1:
                    self.shutdown()
                    pass
                    #quite the server both players disconnected
                self.players.pop(client_addr)   
                break
            if time() > self.players[client_addr].lastMsg + 5: #if nothing we heared nothing from the client for 5 seconds... send a alive-request
                self.socket.sendto("SRV_ALIVE_", client_addr)    
    
    def process(self):
        # Receive messages
        while True:
            self.testTimout()           
            try:
                data,addr = self.socket.recvfrom(self.bufsize)
            except Exception, e:
                continue

            if not data:
                print "Client has exited!"
                break
            else:
                #NEW CLIENT
                if not addr in self.players and len(self.players)<2:
                    print "New Client!", addr
                    connect = ''
                    for client_addr in self.players.keys():
                        connect += self.players[client_addr].connectData
                    if connect != '':
                        self.socket.sendto(connect, addr)
                    print("New Client Synced")
                    self.players[addr] = Player(addr)
                    self.players[addr].addConnect(data)
                #########
                
                player = self.players[addr]
                player.update()
                for client_addr in self.players.keys():
                    #if client_addr != addr:
                        #echo packet
                    self.socket.sendto(data, client_addr)
            

    def shutdown(self):
        # Close socket
        self.socket.close()


server = GameServer()
print"Server started successfully!"
server.process()


