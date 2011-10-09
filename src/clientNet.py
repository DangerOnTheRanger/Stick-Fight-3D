import errno
import struct
import socket

BUFSIZE=2048

class Network():
    def __init__(self, host, port=5432):
        self.server = (host, port)
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.setblocking(0)

    def send(self, data ):
        self.socket.sendto( data, self.server)

    def receive(self):
         try:
                data, addr = self.socket.recvfrom(BUFSIZE)
                if  addr == self.server :
                    #print 'packet recv: '+str(data)
                    return data
                else:
                    #print "watt? wer bist du denn?"
                    return None
         except:
                return None

if __name__ == '__main__':
    from time import time,sleep
    print "connecting..."
    connection = Network( "127.0.0.1" , 5432)
    print "connected"
    i = 0
    connection.send("connecting")
    while 1:
        #connection.send("test"+str(i))
        i += 1
        sleep(0.1)
        data = connection.receive()
        if data != None:
            if data == "SRV_ALIVE_":
                connection.send("CLI_ALIVE_")
            print data
