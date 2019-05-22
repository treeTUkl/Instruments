import socket
import ximcStage
#from  xxxxx import PIStage.py
LOCALHOST = ''
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
print("Server listening...")
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


    # Receive the data in small chunks and retransmit it

        data = connection.recv(4)#we might need more than 4? but labview sagt 4

        print('received "%s"' % data)
        data = data.decode('utf-8') #might not needed if data ist already in string format
        # TODO: POS Befehl Output! DONE
        # TODO: ximcStage befehle einfügen Done

        if data[:3] == "POS":
            print('POS')
            POS = stage.POS()
            print('pos in as: ' + POS)
            print('sending data back to the client')
            connection.sendall(POS)

        elif data[:3]=="MOV":
            new_position_in_as = data[3:]/10
            print('MOV' + new_position_in_as)
            stage.move_absolute_in_as(new_position_in_as)
            POS = stage.POS()
            print('pos in as: ' + POS)
            print('sending data back to the client')
            connection.sendall(POS)

        elif data[:3]=="MVR":
            new_position_in_as = data[3:]/10
            print('MVR' + new_position_in_as)
            stage.move_relative_in_as(new_position_in_as)
            POS = stage.POS()
            print('pos in as: ' + POS)
            print('sending data back to the client')
            connection.sendall(POS)

        elif data[:3]=="SDN":
            print('SDN')
            stage.in_case_terra_sends_SDN()
            POS = stage.POS()
            print('pos in as: ' + POS)
            print('sending data back to the client')
            connection.sendall(POS)

        elif data[:3]=="GOH":
            print('GOH')
            stage.go_home()
            POS = stage.POS()
            print('pos in as: ' + POS)
            print('sending data back to the client')
            connection.sendall(POS)

        elif data[:3]=="DEH":
            print('DEH')
            stage.set_zero_position()
            POS = stage.POS()
            print('pos in as: ' + POS)
            print('sending data back to the client')
            connection.sendall(POS)

        else:
            print('got strange data' + data + 'do nothing with it')
            break

    except socket.error:
            print("Error Occured")

            connection.close()

    finally:
        # Clean up the connection
        connection.close()