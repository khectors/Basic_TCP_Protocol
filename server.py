# pylint: disable=E0602

import socketserver
import socket
import threading
import sys
import os
import json
import time
import numpy as np

from datetime import datetime


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    @property
    def time(self):
        '''
        return the current date and time in
        DD/MM/YYYY HH/MM/SS format

        *Return
            string
        '''
        return datetime.now().strftime("%d-%m-%Y %H-%M-%S")

    def setup(self):
        '''
        Called before the handle() method to perform any initialization actions required.
        '''
        self.FORMAT = 'UTF-8'
        self.HEADER = 5000

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

        # Encode the length of the message that we want to send as a string
        data_size = str(data_size).encode(self.FORMAT)

        # Pad the data_size message to the HEADER length, such that it is received as one
        data_size += b' ' * (self.HEADER - len(data_size))

        # Send the size of the package over the socket
        self.request.sendall(data_size)

        # Send the actual package
        self.request.sendall(package)

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
        data_size = self.request.recv(self.HEADER).decode(self.FORMAT)

        # Make empty byte string for concatenating byte stream that will be received
        byte_stream = b""

        # If a package will be, get the data length
        if data_size:
            data_size = int(data_size)

            # Keep receiving until the received data size is larger than
            # or equal to the data that is being send
            while data_size > len(byte_stream):
                # Concatenate the byte stream
                byte_stream +=self.request.recv(data_size)

            # Decode the byte stream to get the package data
            data = byte_stream.decode(self.FORMAT)
            return data

    def handle(self):
        '''
        Handle what has to happen when a package (message or data) is send
        to the server over the TCP socket server.
        '''

        # Receive package send by the client
        package = self.receive()

        if package is not None:
            # Deserialize package if pickled
            action, data = json.loads(package)

            # Print message/data.
            print(data)

            # the client signals the end of the connection.
            if action == "stop" or data == "!DISCONNECT":
                self.handle_stop()

    def handle_stop(self):
        '''
        Stop the server
        '''
        def delayedStop():
            time.sleep(0.5)
            self.server.shutdown()
        thread = threading.Thread(target=delayedStop)
        thread.start()


if __name__ == "__main__":

    # Create the server, binding to localhost on port 8888
    print("[STARTING] server is starting...")
    HOST, PORT = socket.gethostbyname(socket.gethostname()), 8888
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    print("[LISTENING] Server is listening on {}".format(server.server_address))

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
