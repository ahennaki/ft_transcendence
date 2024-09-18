import socket

HOST = '0.0.0.0' # Listen to all network interfaces
PORT = 7777 # Port to listen to 

def echo_server():
	""" an echo server """
	# Create a TCP socket
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
	
		# Enable reuse address/port
		server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# Bind the socket to the port
		server_address = (HOST, PORT)
		print ("Starting up echo server on %s port %s" % server_address)
		server_sock.bind(server_address)

		# Listen to clients. 7 is the number of queued connections
		server_sock.listen(7)

		while True:
			client_sock, client_addr = server_sock.accept()
			print (f"Connection from {client_addr}")

			with client_sock:
				while True:
					data = client_sock.recv(1024)
					print (f"Data {data}")
					if data.decode()=='\n':
						break
					client_sock.sendall(data)

echo_server()