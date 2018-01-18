## Written by Micah Terrell
## Updated for Protocol Version 0.1
## This file contains functions for constructing and sending protocol messages over TCP

###### Public Functions


#   Sends a tcp message to the specified port on the given host
# Parameters
#   message: a list of bytes to be sent over tcp. The 0th index is the first byte sent
#   host: the host to send the message to
#   port: the port of the host to send the message to
# Returns
#   True if the message was sent succesfully, False otherwise

def sendTCPMessage(message, host, port):
	print("TODO: Implement sendTCPMessage(message, host, port)")

#   Builds a byte list that represents a BE TCP Control Protocol CONNECT message
# Parameters
#   TODO
# Returns
#   A byte list containing a CONNECT message
def buildConnectMessage(TODO):
	print("TODO")

#   Builds a byte list that represents a BE TCP Control Protocol GET_OPTION message
# Parameters
#   TODO
# Returns
#   A byte list containing a GET_OPTION message
def buildGetOptionMessage(TODO):
	print("TODO")

#   Builds a byte list that represents a BE TCP Control Protocol SET_PARAM message
# Parameters
#   TODO
# Returns
#   A byte list containing a SET_PARAM message
def buildSetParamMessage(TODO):
	print("TODO")

#   Builds a byte list that represents a BE TCP Control Protocol START_EXPERIMENT message
# Parameters
#   TODO
# Returns
#   A byte list containing a START_EXPERIMENT message
def buildStartExperimentMessage(TODO):
	print("TODO")

#   Builds a byte list that represents a BE TCP Control Protocol STOP_EXPERIMENT message
# Parameters
#   TODO
# Returns
#   A byte list containing a STOP_EXPERIMENT message
def buildStopExperimentMessage(TODO):
	print("TODO")

#### Private Functions