import select
import socket
import sys
import queue as Queue
import threading
# Create a TCP/IP socket
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
neighbour_conns = []
is_initiator = False
conn.setblocking(0)
neighbour_list = [('localhost',10000),('localhost',10003)]
Stree_neighbour_list = []
for _ in neighbour_list:
    neighbour_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    neighbour_conns.append(neighbour_conn)
    # Bind the socket to the port
address = ('localhost', 10001)
print('starting up on %s port %s' % address)
conn.bind(address)

    # Listen for incoming connections
conn.listen(5)
socket_list = []
outputs = []
    # Sockets from which we expect to read
outputs_available = threading.Event()
input_queues = {}
output_queues = {}
def main():
    t_socket = threading.Thread(target=sockets)
    t_socket.start()
    outputs_available.wait()
    print("back to main #################################################")
    if len(output_queues.keys()) == len(neighbour_list):
            if is_initiator == True:
                initiator()
    t_socket.join()

def sockets():

    while True:
        try:
            for index, connection in enumerate(neighbour_conns):
                if connection not in socket_list:
                    connection.connect(neighbour_list[index])
                    socket_list.append(connection)
                    #outputs.append(connection)
                    # Give the connection a queue for data we want to send
                    output_queues[connection] = Queue.Queue()
                    #print(connection)
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
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs,1)
        for s in readable:

            if s is conn:
                # A "readable" server socket is ready to accept a connection
                # if conn in outputs:
                # outputs.remove(conn)
                connection, client_address = s.accept()
                print('new connection from', client_address)
                connection.setblocking(0)
                inputs.append(connection)
                
                # Give the connection a queue for data we want to send
                input_queues[connection] = Queue.Queue()
                print(connection)
            else:
                data = s.recv(1024)
                if data:
                    # A readable client socket has data
                    print('received "%s" from %s' % (data, s.getpeername()))
                    if b'Hello' in data:
                        hello_recieve(data)
                    input_queues[s].put(data)
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
        


def hello_recieve(string):
    pass


def initiator():
    for conn in socket_list:
        output_queues[conn].put(("Hello" + str(address)).encode())
        outputs.append(conn)



if __name__ == '__main__':
    main()
