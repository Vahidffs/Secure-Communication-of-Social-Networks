import select
import socket
import sys
import queue as Queue
import threading
from ast import literal_eval
from packages.DiffieHellman import keyCreation,dhfunc
import time
import pyDHE
import pickle
import packages.AES as AES
from Crypto.Hash import SHA256
# Create a TCP/IP socket
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
neighbour_conns = {}
is_initiator = False
conn.setblocking(0)

neighbour_list = [('localhost',10000),('localhost',10001),('localhost',10002)]
address = ('localhost', 10003)

new_neighbour_list = []
old_neighbour_list = []
AES_key_list = []
sharedkey_list = {}
DH_object = pyDHE.new()
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
nonces = {}
macs = {}
    # Sockets from which we expect to read
outputs_available = threading.Event()
Stree_available = threading.Event()
DH_available = threading.Event()
Stree_completed = False
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
                send_via_socket("Hello",0,neighbour_list)
    Stree_available.wait() 
    print(new_neighbour_list)
    print(old_neighbour_list)   
    print("Spanning Tree Created")
    public_key = DH_object.getPublicKey()
    send_via_socket("DHKey" , public_key,new_neighbour_list)
        #print(len(str(key)))
    DH_available.wait()
    for neighbour in new_neighbour_list:    
        h = SHA256.new()
        h.update((sharedkey_list[neighbour]).to_bytes(256,byteorder='big'))
        AES_key = AES.AES_Key_Creator(h.digest())
        AES_key_list.append(AES_key)
    print(AES_key_list)
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
                data = s.recv(4096)
                if data:
                    while data:
                        #print('received "%s" from %s' % (data, s.getpeername()))
                        length = int.from_bytes(data[:4],byteorder='big')
                        print(length) 
                        data_list = pickle.loads(data[4:length + 4])
                        data = data[length+4:]
                        #time.sleep(10)
                        print(data_list)
                        input_queues[s].put(data_list)
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
            Stree_completed = True
            Stree_available.set()
            if len(sharedkey_list) == len(new_neighbour_list):
                print(len(sharedkey_list))
                DH_available.set()

def hello_recieved(data):
    if data[-1] in new_neighbour_list:
        send_via_socket("Old",0,[data[-1]])
    else:
        new_neighbour_list.append(data[-1])
        send_via_socket("New",0,[data[-1]])
        send_via_socket("Hello",0,[send_hello for send_hello in neighbour_list if send_hello != data[-1]])


def new_recieved(data):
    if data[-1] not in new_neighbour_list: 
        new_neighbour_list.append(data[-1])


def old_recieved(data):
    if data[-1] not in new_neighbour_list or old_neighbour_list:   
        old_neighbour_list.append(data[-1])
def key_recieved(data):
    key = data[1]
    sharedkey_list[data[-1]] = DH_object.update(key)
def decrypt_cipher(data):
    cipher = data[1]
    h = SHA256.new()
    h.update(sharedkey_list[data[-1]])
    plaintext = AES.decryptfunc(h.digest(),cipher,nonces[data[-1]],macs[data[-1]])
    print(plaintext)
def store_mac(data):
    mac = data[1]
    macs[data[-1]] = mac
def store_nonce(data):
    nonce = data[1]
    nonces[data[-1]] = nonce
def check_input_string(s):
    while not input_queues[s].empty():
        try:
            data = input_queues[s].get(False)
        except Queue.Empty:
        # Handle empty queue here
            pass
        else:
            
            if Stree_completed == False:
                if data[0] == 'Hello':
                    hello_recieved(data)
                if data[0] == 'New':
                    new_recieved(data)
                if data[0] == 'Old':
                    old_recieved(data)
                if data[0] == 'DHKey':
                    key_recieved(data)
                if data[0] == 'Ciphertext':
                    decrypt_cipher(data)
                if data[0] == 'MAC':
                    store_mac(data)
                if data[0] == 'Nonce':
                    store_nonce(data)
def send_via_socket(data_type,data,address_list):
    #print("sending this",data,"to this",address_list)
    for name,socket in neighbour_conns.items():
            if name in address_list:
                tupled_data = (data_type,data,address)
                serialized_data = pickle.dumps(tupled_data)
                length_data = len(serialized_data)
                final_data = (length_data).to_bytes(4,byteorder='big') + serialized_data
                output_queues[socket].put(final_data)
                with output_lock:
                    outputs.append(socket)

if __name__ == '__main__':
    main()
