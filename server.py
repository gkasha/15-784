import socket, os, time, select, pickle, sys
from _thread import *
from messages.message import Message
from messages.message import User

def process_msg(msg, user_map):
    if msg.opcode == 0:
        print("Opcode is 0")
    elif msg.opcode == 1:
        # Do nothing
        print("Opcode is 1")
    elif msg.opcode == 2:
        # Received auction signal, data is list of items
        print("Forwarding auction items to bidders")

        # Send out auction item to bidders
        for user in user_map:
            if user == msg.name:
                continue
            new_msg = Message(msg.name, 2, msg.data)
            data = pickle.dumps(new_msg)
            user_map[user][0].sendall(data)

        # Send number of bidders to auctioneer
        user_map[msg.name][1] = True
        new_msg = Message("server", 1, len(user_map)-1)
        data = pickle.dumps(new_msg)
        user_map[msg.name][0].sendall(data)
    elif msg.opcode == 3:
        # Received a bid, need to forward to auctioneer
        print("Forwarding bid to auctioneer")
        auctioneer = ""
        for user in user_map:
            if user_map[user][1]:
                auctioneer = user
                break
        new_msg = Message(msg.name, 3, msg.data)
        data = pickle.dumps(new_msg)
        user_map[auctioneer][0].sendall(data)

        print("Sent bid from " + msg.name + " to auctioneer: " + auctioneer)
    elif msg.opcode == 4:
        # Received map of assignments
        
        for bidder in msg.data:
            new_msg = Message(msg.name, 4, msg.data[bidder])
            data = pickle.dumps(new_msg)
            user_map[bidder][0].sendall(data)
    else:
        pass

def multi_threaded_client(connection, client_id, user_map, ):
    timeout = 10

    data = connection.recv(2048)
    msg = pickle.loads(data)
    if msg.opcode == 0:
        user_map[msg.name] = [connection,False]
        print("Received hi from " + msg.name + ". Num users: " + str(len(user_map)))

    while True:
        try:
            readable,_,_ = select.select([connection], [],[],10)
            if readable:
                data = connection.recv(2048)
                recv_data = pickle.loads(data)
                process_msg(recv_data, user_map)
        except Exception as e:
            print(str(e))
            break

        
    print("Closing connection for client: " + str(client_id))
    connection.close()
    del user_map[msg.name]

def server_program(port):
    # get the hostname
    host = socket.gethostname()
    server_socket = socket.socket()  # get instance
    ThreadCount = 0

    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together
    server_socket.listen()
    user_map = {}
    
    while True:
        client, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        start_new_thread(multi_threaded_client, (client, ThreadCount, user_map, ))
        ThreadCount += 1
        print("Thread number: " + str(ThreadCount))

    server_socket.close()


if __name__ == '__main__':
    port = (int)(sys.argv[1])
    server_program(port)