import ProtocolClient
import ProtocolServer
import threading
import socket
import sys


def main():
	ProtocolClient.sendTCPMessage("Hello", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Bye", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Hello", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Bye", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Hello", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Bye", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Hello", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Bye", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Hello", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Bye", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Hello", socket.gethostname() , 12345)
	ProtocolClient.sendTCPMessage("Bye", socket.gethostname() , 12345)

main()