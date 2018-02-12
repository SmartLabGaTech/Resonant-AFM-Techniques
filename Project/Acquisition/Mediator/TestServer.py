import socket
import codecs
import json

host = ''        # Symbolic name meaning all available interfaces
sendPort = 4021     # Arbitrary non-privileged port
receivePort = 4020
conn = None


def startTestServer():
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
            decodedData = json.loads(codecs.decode(data, "utf_8"))
            if(decodedData['message_name'] == 'disconnect'):
                print("Recieved disconnect, killing test server")
                conn.close()
                return
            elif(not connected):
                connected = handleConnectMessage(decodedData)
            
                

            print("Client Says: "+ codecs.decode(data, "utf_8"))
            
        
def handleConnectMessage(message):

    if(message['message_name'] == 'connect'):               
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', sendPort))

        response = {
            "message_name" : "connectAck"
        }

        encodedResponse = json.dumps(response).encode("utf_8")
        sock.sendall(encodedResponse)
        print("Sent message: " + json.dumps(response))
        sock.close()
        return True
    else:
        return False

def handleSetParamMessage(data):
    pass

startTestServer()
