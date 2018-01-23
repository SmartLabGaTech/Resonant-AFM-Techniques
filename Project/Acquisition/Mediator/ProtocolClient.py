## Written by Micah Terrell
## Updated for Protocol Version 0.2
## This file contains functions for constructing and sending protocol messages over TCP

import socket
import json

###### Public Functions

#   Sends a tcp message to the specified port on the given host
# Parameters
#   message: a list of bytes to be sent over tcp. The 0th index is the first byte sent
#   host: the host to send the message to
#   port: the port of the host to send the message to
# Returns
#   True if the message was sent succesfully, False otherwise
def sendTCPMessage(message, host, port):
	#Create the socket and connect to it
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))

	#Encode the message
	encodedMessage = message.encode("utf_8")

	#Send the message
	sock.sendall(encodedMessage)

	sock.close()

# def sendTestTCP():
# 	host = socket.gethostname()
# 	port = 12345

# 	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 	s.connect((host, port))
# 	s.sendall(b'Hello, world')
# 	data = s.recv(1024)
# 	s.close()
# 	print("GOT ", repr(data))

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

#### Private Functions


#### Test Script
# print(buildConnectMessage())
# print(buildSetParamMessage("TestParam", 42))
# print(buildStartExperimentMessage())
# print(buildStopExperimentMessage())
sendTCPMessage(buildConnectMessage(), socket.gethostname(), 12345)