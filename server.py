import socket
import threading

# All the message handeling will be put in separate threads for the different clients that connect to the server so that the client
# is not waiting for another client to sent/receive a message before it is able to communicate with the server

# First a port  is defined, which is where the server has to run
HEADER = 64
PORT = 5052

# Local server --> cmd --> run ipconfig --> copy IPv4 Address
SERVER = "172.18.119.160"
SERVER = socket.gethostbyname(socket.gethostname()) # --> Get the IPv4 Address dynamically
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE ='!DISCONNECT'


# Make a socket that allows to open the device to other connections
# Pick the socket and bind the socket to the server address
# make a new socket, socket.AF_INET = socket family; AF_INIT = over internet
# socket familiy tells the socket what type of IP address or connection we will be looking for.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to an adress, anything that connects to the socket will hit that adress
server.bind(ADDR)

def send(conn, msg):
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

    # Send the length of the actual message over the socket
    conn.send(send_length)

    # Send the actual message
    conn.send(message)


def handle_client(conn, addr):
    '''
    Handle all the communication between the individual clients and the server
    '''
    print(f'[NEW CONNECTION] {addr} connected.')

    connected = True
    while connected:
        # Code waits here until a message is received from the client over the socket
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            send(conn, "Msg received")

    conn.close()

def start():
    '''
    Start socket server. This method contains the code that allows our server
    to start listening for connections and then handeling these connections and
    passing them to handle_client which will run in a new thread. i.e. this handles
    new connections and distributes them to where they need to go.
    '''
    # Start listening to requests
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        # Wait for new connection to server
        conn, addr = server.accept()
        # When a new connection occurs, pass that connection to handle_client
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        # Print the number of active client - server connections
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')


print("[STARTING] server is starting...")
start()