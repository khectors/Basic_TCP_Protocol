#TCPserver

TCPserver is a package that allows you to setup a TCP socket server and connect a client to that server. The package 
includes an implementation of a message protocol that allows you to send and receive packages as a whole. This is not 
garuanteed for a standard implementation as the TCP protocol is a stream orient protocol. This means that you have 
an API (send/recv and similar) that gives you the ability to send or receive a byte stream. There is no preservation
of message boundaries, TCP can bundle up data from many send() calls into one segment, or it could break down data 
from one send() call into many segments - but that's transparent to applications sitting on top of TCP, and recv() just 
gives you back data, with no relation to how many send() calls produced the data you get back.
 
## Usage

First run the server.py script. This will setup the server. Next, in a different terminal, run the client.py
script to connect to the server. Once connected, you will be prompted to enter a message.
This message will be send to the server and printed. In order to disconnect from the server enter '!DISCONNECT'.

## Requirements

Python version 3.x

### Required libraries
	socketserver
	socket
	threading
	sys
	os
	json
	time
	numpy
	datetime



