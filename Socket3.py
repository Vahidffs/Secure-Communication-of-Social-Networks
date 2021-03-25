import select
import socket
import sys
import queue as Queue
import threading
from ast import literal_eval
# Create a TCP/IP socket
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
neighbour_conns = {}
is_initiator = False
conn.setblocking(0)
neighbour_list = [('localhost',10000),('localhost',10001),('localhost',10002)]
address = ('localhost', 10003)
new_neighbour_list = []
old_neighbour_list = []

for neighbour in neighbour_list:
    neighbour_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    neighbour_conns[neighbour] = neighbour_conn
    # Bind the socket to the port
print('starting up on %s port %s' % address)
conn.bind(address)

    # Listen for incoming connections
conn.listen(5)
socket_list = []
outputs = []
    # Sockets from which we expect to read
outputs_available = threading.Event()
Stree_available = threading.Event()
input_queues = {}
output_queues = {}
output_lock = threading.Lock()
def main():
    t_socket = threading.Thread(target=sockets)
    t_socket.start()
    outputs_available.wait()
    print("back to main #################################################")
    if len(output_queues.keys()) == len(neighbour_list):
            if is_initiator == True:
                send_via_socket("Hello",neighbour_list)
    Stree_available.wait()    
    print("Spanning Tree Created")
    t_socket.join()

def sockets():

    while True:
        try:
            for name,socket in neighbour_conns.items():
                if socket not in socket_list:
                    socket.connect(name)
                    socket_list.append(socket)
                    #outputs.append(connection)
                    # Give the connection a queue for data we want to send
                    output_queues[socket] = Queue.Queue()
                    print(socket)
        except:
            continue
        else:
            break
    outputs_available.set()
    inputs = [conn]
    # Sockets to which we expect to write
    # Outgoing message queues (socket:Queue)
    # Handle inputs
    while inputs:

        # Wait for at least one of the sockets to be ready for processing
        #print( '\nwaiting for the next event')
        with output_lock:
            readable, writable, exceptional = select.select(
                inputs, outputs, inputs,1)
        for s in readable:

            if s is conn:
                # A "readable" server socket is ready to accept a connection
                # if conn in outputs:
                # outputs.remove(conn)
                connection, client_address = s.accept()
                #print('new connection from', client_address)
                connection.setblocking(0)
                inputs.append(connection)
                
                # Give the connection a queue for data we want to send
                input_queues[connection] = Queue.Queue()
                #print(connection)
            else:
                data = s.recv(2048)
                if data:
                    # A readable client socket has data
                    print('received "%s" from %s' % (data, s.getpeername()))
                    data_list =  str(data).split("~") 
                    for data_chunk in data_list:
                        if data_chunk[-1] != '"':
                            input_queues[s].put(data_chunk + '"')
                        else:
                            input_queues[s].put(data_chunk)
                    check_input_string(s)
                    # Add output channel for response
                    # if s not in outputs:
                    # outputs.append(s)
                else:
                    # Interpret empty result as closed connection
                    print('closing', client_address, 'after reading no data')
                    # Stop listening for input on the connection
                    #if s in outputs:
                        #outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    #del message_queues[s]
        # Handle outputs
        for s in writable:
            if s in output_queues and not output_queues[s].empty():
                try:
                    next_msg = output_queues[s].get_nowait()
                except Queue.Empty:
                    # No messages waiting so stop checking for writability.
                    print('output queue for', s.getpeername(), 'is empty')
                    # outputs.remove(s)
                else:
                    print('sending "%s" to %s' % (next_msg, s.getpeername()))
                    s.send(next_msg)
                    outputs.remove(s)
        # Handle "exceptional conditions"
        for s in exceptional:
            print('handling exceptional condition for', s.getpeername())
            # Stop listening for input on the connection
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()

            # Remove message queue
            del output_queues[s]
        if len(neighbour_list) == (len(new_neighbour_list) + len(old_neighbour_list)):
            Stree_available.set()


def hello_recieved(data):
    str_address = '"' + data.split("from ",1)[1]
    address_tuple = ('localhost',int(''.join(c for c in str_address if c.isdigit())))
    if address_tuple in new_neighbour_list:
        send_via_socket("Old",[address_tuple,])
    else:
        new_neighbour_list.append(address_tuple,)
        send_via_socket('New',[address_tuple,])
        send_via_socket("Hello",[send_hello for send_hello in neighbour_list if send_hello != address_tuple])


def new_recieved(data):
    str_address = '"' + data.split("from ",1)[1]
    address_tuple = ('localhost',int(''.join(c for c in str_address if c.isdigit())))  
    if address_tuple not in new_neighbour_list: 
        new_neighbour_list.append(address_tuple)


def old_recieved(data):
    str_address = '"' + data.split("from ",1)[1]
    address_tuple = ('localhost',int(''.join(c for c in str_address if c.isdigit())))
    if address_tuple not in new_neighbour_list or old_neighbour_list:   
        old_neighbour_list.append(address_tuple,)
def check_input_string(s):
    while not input_queues[s].empty():
        try:
            data = input_queues[s].get(False)
        except Queue.Empty:
        # Handle empty queue here
            pass
        else:
            if 'Hello' in data:
                hello_recieved(data)
            if 'New' in data:
                new_recieved(data)
            if 'Old' in data:
                old_recieved(data)
def send_via_socket(data,address_list):
    for name,socket in neighbour_conns.items():
            if name in address_list:
                output_queues[socket].put((data +" from " + str(address) + "~").encode())
                with output_lock:
                    outputs.append(socket)

if __name__ == '__main__':
    main()
