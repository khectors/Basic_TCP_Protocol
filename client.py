import socket

HEADER = 64
PORT = 5052
FORMAT = 'utf-8'
DISCONNECT_MESSAGE ='!DISCONNECT'
SERVER = socket.gethostbyname(socket.gethostname()) # --> Get the IPv4 Address dynamically
ADDR = (SERVER, PORT)

# Setup the socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def receive_msg():
    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        return msg


def send(msg):
    '''
    Send a message through the socket from the client to the server
    First a messag is send that contains the length of
    the actual message that will be send.
    '''
    # Encode the string in to a bytes like object so it can be send through the socket
    message = msg.encode(FORMAT)

    # Get the length of the message that will be send
    msg_length = len(message)

    # Encode the length of the message that we want to send as a string
    send_length = str(msg_length).encode(FORMAT)

    # Find the length of the first message and pad it to length 64
    send_length += b' ' * (HEADER - len(send_length))

    # Send the lenght of the actual message over the socket
    client.send(send_length)

    # Send the actual message
    client.send(message)

    print(receive_msg())


send('Hello World!')
#input()
send("I'm Kris")