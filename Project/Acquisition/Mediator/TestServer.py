import socket
import codecs
import json

host = ''        # Symbolic name meaning all available interfaces
sendPort = 4021     # Arbitrary non-privileged port
receivePort = 4020
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, receivePort))

print (host , receivePort)
s.listen(1)
connected = False

while True:
    conn, addr = s.accept()
    print('Connected by', addr)
    data = conn.recv(1024)

    if not data:
        pass

    if(data):
        if(not connected):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', sendPort))

            message = {
                "message_name" : "connectAck"
            }
            encodedMessage = json.dumps(message).encode("utf_8")
            sock.sendall(encodedMessage)
            print("sent ack")

            connected = True


        print ("Client Says: "+ codecs.decode(data, "utf_8"))
        sock.close()
        



conn.close()