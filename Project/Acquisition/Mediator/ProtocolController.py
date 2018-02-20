## Written by Micah Terrell
## Updated for Protocol Version 0.2
## This file contains functions that provide a layer of abstraction for sending 
## and recieving BE TCP Control Protocol messages as the Mediator

import json
import queue
import threading
import ProtocolServer
import ProtocolClient
import socket
import time

messageQueue = queue.Queue(20)

#Note: Each buffer should always contain plain text
sendBuffer = queue.Queue(20)
receiveBuffer = queue.Queue(20)
timeout = 1

sendPortNumber = None
receivePortNumber = None

keepListening = False
keepSending = False

###### Public Functions ######

def runProtocol(sendPort, receivePort):
	# Create an event to control the listening thread
	keepListening = threading.Event()
	keepListening.set()

	# Create a lock to protect the listen socket
	listenSocketLock = threading.Lock()

	# Create the socket
	listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listenSocket.settimeout(0.2)
	listenSocket.bind(('', receivePort))
	listenSocket.listen(1)

	# Start listener thread
	listenThreadArgs = (listenSocket, keepListening, listenSocketLock)
	listenThread = threading.Thread(target=listenThreadFunction, args=listenThreadArgs)
	listenThread.daemon = True
	listenThread.start()

	# TODO: the send thread socket is contained in the thread itself, this seems wrong, but it works for now and I'm not sure what would be better
	# Start sending thread
	sendThreadArgs = ('127.0.0.1', sendPort)
	sendThread = threading.Thread(target=sendThreadFunction, args=sendThreadArgs)
	sendThread.daemon = True
	sendThread.start()
	
	#Send initial connection message
	print("Sending connection message to " + str(sendPort))
	sendConnectMessage()

	if(not connected()):
		print("Connection not found. Exiting Protocol.")
		keepListening.clear()

		listenSocketLock.acquire()
		listenSocket.close()

		return False
	
	#TODO: These globals look bad
	global sendPortNumber
	global receivePortNumber

	sendPortNumber = sendPort
	receivePortNumber = receivePort
	

	print("Connected")
	return True

def connected():
	start = time.time()
	#Wait for timeout seconds for a response
	while(True):
		if(time.time() - start >= timeout):
			print("Connection timed out")
			return False
		elif(not receiveBuffer.empty()):
			#Pop the message and check its type
			try:
				message = receiveBuffer.get(False)
				if(getMessageName(message) == 'connectAck'):
					return True
				else:
					print("Dropped message during connection: " + message)
				#While connecting, drop all none Ack messages
			except Empty:
				pass

#Takes a plain text json message and returns the message name
def getMessageName(message):
	return json.loads(message)['message_name']

def sendConnectMessage():
	sendBuffer.put(buildConnectMessage(), False)

def sendSetParamMessage(parameterName, parameterValue):
	sendBuffer.put(buildSetParamMessage(parameterName, parameterValue))

def sendStartExperimentMessage():
	sendBuffer.put(buildStartExperimentMessage())

def sendDisconnectMessage():
	#Send the kill message directly

	global sendPortNumber

	# Create the socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# If there is a message, encode and sent it
	sock.connect(('127.0.0.1', sendPortNumber))

	message = buildDisconnectMessage()

	encodedMessage = message.encode("utf_8")
	sock.sendall(encodedMessage)

	sock.close()

def listenThreadFunction(listenSocket, listeningEvent, listenSocketLock):
	#Acquire the lock to protect the socket
	listenSocketLock.acquire()

	while(listeningEvent.isSet()):
		try:
			#Wait for a connection
			connection, clientAddress = listenSocket.accept()
			print("Connection from ", clientAddress)

			while(True):
				data = connection.recv(1024)

				if(data):

					# Decode the message
					decodedMessage = data.decode("utf_8")
					print(decodedMessage)
					# Buffer the message
					# Currently if the buffer is full an exception is raised.
					# TODO: handle dropped messages
					# TODO: handle exception
					receiveBuffer.put(decodedMessage, False)
		except socket.timeout:
			pass
	#The thread is done with the socket
	listenSocketLock.release()	

def sendThreadFunction(host, port):
	while(1):
		#Wait for messages in sendBuffer
		if(not sendBuffer.empty()):
			message = sendBuffer.get()
			# Create the socket
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				
				# If there is a message, encode and sent it
				sock.connect((host, port))

				encodedMessage = message.encode("utf_8")
				sock.sendall(encodedMessage)
				print("sent " + message)
				
			except ConnectionRefusedError:
				sendBuffer.put(message)
				time.sleep(.1)
			sock.close()
		else:
			# Sleep for a bit
			time.sleep(.1)

###### Private Functions ######

#   Builds a BE TCP Control Protocol connect message
# Parameters
#   None
# Returns
#   a JSON string representing a connect message
def buildConnectMessage():
	message = {
		"message_name" : "connect"
	}
	return json.dumps(message)

#   Builds a BE TCP Control Protocol setParam message
# Parameters
#   parameterName: The name of the parameter to change
#	parameterValue: The value the parameter should be set to
# Returns
#   a JSON string representing a setParam message
def buildSetParamMessage(parameterName, parameterValue):
	message = {
		"message_name" : "setParam",
		"param_name" : parameterName,
		"param_value" : parameterValue
	}
	return json.dumps(message)

#   Builds a BE TCP Control Protocol startExperiment message
# Parameters
#   None
# Returns
#   a JSON string representing a startExperiment message
def buildStartExperimentMessage():
	message = {
		"message_name" : "startExperiment"
	}
	return json.dumps(message)

#   Builds a BE TCP Control Protocol stopExperiment message
# Parameters
#   None
# Returns
#   a JSON string representing a stopExperiment message
def buildStopExperimentMessage():
	message = {
		"message_name" : "stopExperiment"
	}
	return json.dumps(message)

def buildDisconnectMessage():
	message = {
		"message_name" : "disconnect"
	}
	return json.dumps(message)