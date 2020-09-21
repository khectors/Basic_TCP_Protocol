
# Standard imports
import socket
import sys
import json
import time
from datetime import datetime

'''
This module deals with communication to the server
A class client is defined which can connect to and communicate with the server
'''

class Client():

    def __init__(self, port=8888):
        '''
        Initialize the client side of the socket

        *Args
            inputs, Input instance: instance of the class inputs
        '''
        # initialize socket, host/server and the port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = socket.gethostbyname(socket.gethostname())
        self.PORT = port
        self.FORMAT = 'UTF-8'
        self.HEADER = 5000
        self.listening = False

        # Blocking code which checks if the a server connection can be made
        self.connect_to_server()

    @property
    def address(self):
        return (self.HOST, self.PORT)

    @property
    def time(self):
        '''
        return the current date and time in
        DD/MM/YYYY HH/MM/SS format

        *Return
            string
        '''
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def connect_to_server(self):
        '''
        Keep trying to connect to the server until succesfull
        '''
        self.serverRunning = False
        while not self.serverRunning:
            try:
                self.client.connect(self.address)
                self.client.close()
                self.serverRunning = True
                print("{} [CONNECTION ESTABLISHED] The server is running".format(self.time))

            except: pass

    def send(self, package):
        '''
        Send a message through the socket from the client to the server
        First a message is send that contains the length of
        the actual message that will be send.

        *Args
            package, tuple of length two: package has the form (action, data)
                action, string: action that the server has to perform
                data: data that has to be send to the server
        *Note
            TCP message protocol
        '''
        # Encode the package in to a bytes like object if it is a string so it can be send through the socket
        if isinstance(package, str):
            package = package.encode(self.FORMAT)

        # Get the size of the package that will be send
        data_size = len(package)

        # Encode the length of the message that we want to send as a string or json serialized object
        data_size = str(data_size).encode(self.FORMAT)

        # Pad the data_size message to the HEADER length, such that it is received as one
        data_size += b' ' * (self.HEADER - len(data_size))

        # Send the size of the package over the socket
        self.client.sendall(data_size)

        # Send the actual package
        self.client.sendall(package)

    def receive(self):
        '''
        Receive message that was send using the TCP message protocol
        defined in the send method. As TCP is a byte stream protocol,
        the receiver should check if the received package is complete
        based on the size of the received data.

        *Note
            self.client is the TCP socket connected to the client
        '''
        # First receive the size of the data that will be send
        data_size = self.client.recv(self.HEADER).decode(self.FORMAT)

        # Make empty byte string for concatenating byte stream that will be received
        byte_stream = b""

        # If a package will be, get the data length
        if data_size:
            data_size = int(data_size)

            # Keep receiving until the received data size is larger than
            # or equal to the data that is being send
            while data_size > len(byte_stream):
                # Concatenate the byte stream
                byte_stream +=self.client.recv(data_size)

            # Decode the byte stream to get the package data
            data = byte_stream.decode(self.FORMAT)
            return data

    def listen(self, sleep_time=1):
        '''
        Listen to the server for incomming messages,
        behaviour depends on the message:

        *Actions
            !END = break the loop, close the active socket
            !DATA = next message contains ouput data. Wait for next message, then close the active socket
        '''
        # Set listening to active.
        self.listening = True

        # As long as client is listening, it can receive messages from the server
        while self.listening:
            # Needed to limit CPU resources
            time.sleep(sleep_time)

            # blocking code waiting to receive message
            response = self.receive()

            # If message of server = !END, the connection is closed
            if response == '!END':
                self.listening = False
                self.client.close()
                return None

            # if response = !DATA, data will be send back from the server
            if response == '!DATA':
                self.listening = False

                # Receive and unjsonify the data
                data = json.loads(self.receive())

                self.client.close()

                # Return the received data
                return data

            # Responses that provide an update to the client of the server status
            elif response is not None:
                print(response)
        return None

    def do(self, action, data):
        '''
        send command to server to perform the given action

        *Args
            action, String: action that has to be performed. Check server module for allowed actions
            data, tuple of jsonifyable data structures: data that has to be serialized and send to the server
        '''
        # Create new socket and connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.address)

        # Serialize inputs using json
        package = (action, data)
        serialized_package = json.dumps(package)

        with open("serialized_package.json", "w") as jsonfile:
            json.dump(package, jsonfile, indent=4)

        # Send action and serialized data to server using message protocol
        self.send(serialized_package)

        return

    def initialization(self, inputs, material):
        '''
        Send command to server to open and initialize the FEA model, pass
        the necessary variables

        *Args
            inputs: Inputs class instance
            material: Material class instance
        '''
        # Data that has to go to the server
        # = attributes of inputs and material as dict
        data = (vars(inputs), vars(material))
        action = 'initialization'

        # Send command to server
        self.do(action, data)

    def stop(self):
        '''
        Send the command to the server to shutdown.
        '''
        action, data = "stop", None
        self.do(action, data)
        return

if __name__ == "__main__":
    client = Client()

    # Run loop that allows a user to enter
    # messages, these will be printed at the server side.
    # To end the loop enter "!DISCONNNECT"
    while True:
        print("\nWhat's the message that you want to send to server?")
        message = input()
        client.do(None, message)


