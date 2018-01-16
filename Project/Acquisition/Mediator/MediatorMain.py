import threading
import socket

def sendTestTCP():
	host = socket.gethostname()
	port = 12345

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	s.sendall(b'Hello, world')
	data = s.recv(1024)
	s.close()
	print("GOT ", repr(data))

def main():
	print("TODO: Implement main")
	sendTestTCP()

main()