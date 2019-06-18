import socket
import sys
import time

class standalclient:

    def __init__(self):
        self.sock = 0
        self.connect()

    def connect(self):
        if self.sock == 0:
            HOST = 'localhost'
            PORT = 54545
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # self.sock.setblocking(0)
                self.sock.connect((HOST, PORT))
                print('connected to server')

            except ConnectionRefusedError:
                print('ConnectionRefused! Server might not ready')
                i = 0
                while i == 0:
                    q = input(
                        "Do you want to try again? (Y/N)")
                    if q == "N" or q == "n":
                        print("stopping....")
                        i = 1
                        self.sock.close()
                        sys.exit()
                    elif q == "Y" or q == "y":
                        print("then, keep runnig.")
                        self.sock=0
                        self.connect()
                        i = 1
                    else:
                        print("Invalid answer. Try again.")

    def send(self, message):
        if self.sock == 0:
            print('no socked, try connect first..')
        else:
            # Send data
            print('\nsending:' + message)
            message = message.encode()
            self.sock.sendall(message)
            message = message.decode()
            # reciveing
            if not message == "close":
                data = self.sock.recv(24)
                data = data.decode()
                print('received: ', data)
            elif message ==" ":
                print('nothing received.\nseems to be an error on server')
                self.sock.close()
            else:
                pass

    def close(self):
        print('\nclosing socket')
        self.send("close")


if __name__ == "__main__":
    c = standalclient()
    c.send("POS")
    c.send("MOV60000")
    c.send("DEH")
    c.send("MVR-50000")
    c.send("GOH")
    c.send("POS")
    """
    c.send("LMOVE")
    time.sleep(5)
    c.send("STOPMOVE")  # stops with deceleration speed
    c.send("RMOVE")
    time.sleep(5)
    c.send("STOPMOVE")#stops with deceleration speed
    c.send("STOPFAST")#immediatley stop engine
    """
    c.close()
    print("finish")
