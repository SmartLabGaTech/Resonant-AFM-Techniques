## Written by Micah Terrell
## Updated for Protocol Version 0.2
## This file contains functions for sending TCP messages

import socket

###### Public Functions ######

#   Sends a tcp message to the specified port on the given host
# Parameters
#   message: a list of bytes to be sent over tcp. The 0th index is the first byte sent
#   host: the host to send the message to
#   port: the port of the host to send the message to
# Returns
#   None
def sendTCPMessage(message, host, port):
	#Create the socket and connect to it
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))

	#Encode the message
	encodedMessage = message.encode("utf_8")

	#Send the message
	sock.sendall(encodedMessage)

	sock.close()



