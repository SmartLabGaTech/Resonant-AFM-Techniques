## Written by Micah Terrell
## Updated for Protocol Version 0.2
## This file contains functions that listen for TCP messages

import socket

###### Public Functions ######

#   Listens indefinitely on the given port for TCP messages. When a message is
#   recieved, messageHandler(message) is called
# Parameters
#   port: the port to listen on
#   messageHandler: the function to call on recieved data. Must accept one argument.
# Returns
#   None
def listenOnPort(port, messageHandler):
	host = ''

	messages = 0

	# Create the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((host, port))
	sock.listen(1)

	while(True):
		#Wait for a connection
		connection, clientAddress = sock.accept()

		print("Connection from ", clientAddress)

		while(True):
			data = connection.recv(1024)

			if(data):
				messageHandler(data)
				connection.close()
				if(messages == 9):
					return
				else:
					messages = messages + 1
					break
