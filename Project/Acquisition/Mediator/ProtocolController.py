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

messageQueue = queue.Queue(20)

###### Public Functions ######

def connectToLabView(port):
	print("Connecting on port " + str(port))
	connectMessage = buildConnectMessage()
	ProtocolClient.sendTCPMessage(connectMessage, socket.gethostname(), port)
	##TODO Handle handshakes
##TODO Implement state machine


##TODO: document
def listen(port):
	threadTargetArgs = (port, decodeAndQueueMessage)
	listenThread = threading.Thread(target=ProtocolServer.listenOnPort, args=threadTargetArgs)
	listenThread.start()

###### Private Functions ######

##TODO: Document
def decodeAndQueueMessage(message):
	decodedMessage = message.decode("utf_8")
	messageQueue.put(decodedMessage, True, 20)
	print("TODO: DOC decodeAndQueue: There are ", messageQueue.qsize(), "elements in the q")


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




#### Test Script
#listen(12345)
# print(buildConnectMessage())
# print(buildSetParamMessage("TestParam", 42))
# print(buildStartExperimentMessage())
# print(buildStopExperimentMessage())
# sendTCPMessage(buildConnectMessage(), socket.gethostname(), 12345)
