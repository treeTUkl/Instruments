import socket
import sys

import ximcStage
'from  xxxxx import PIStage.py
LOCALHOST = "xxx.xxx.xxx.xxx"
PORT = 2161

# Initialize stage:
stage = ximcStage.StandaStage()

"""This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket."""
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


""" Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000."""
# Bind the socket to the port
server_address = (LOCALHOST, PORT)
print( 'starting up on %s port %s' % server_address)
sock.bind(server_address)


"""Calling listen() puts the socket into server mode, and accept() waits for an incoming connection."""
# Listen for incoming connections
sock.listen(1)
print("Server started")
print("Server listening to: "LOCALHOST)
print("Waiting for client request..")
while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
"""accept() returns an open connection between the server and client, along with the address of the client.
 The connection is actually a different socket on another port (assigned by the kernel).
  Data is read from the connection with recv() and transmitted with sendall()."""

try:
    print('connection from', client_address)
    if client_address == LOCALHOST:

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(4)#we might need more than 4? but labview sagt 4

            print('received "%s"' % data)
            data = data.decode('utf-8') #might not needed if data ist already in string format

            """
            if data =POV 
            
            
            if data= MOV
                stage.move_absolute(self, new_position, sync=False):
            
            
                print >> sys.stderr, 'sending data back to the client'
                connection.sendall(data)
            else:
                print >> sys.stderr, 'no more data from', client_address
                """
            break
    else:
        print( sys.stderr, 'wrong connection. connection gets terminated')
        connection.close()

finally:
    # Clean up the connection
    connection.close()