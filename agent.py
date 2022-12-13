import socket, select, pickle, time, sys, random
from messages.message import Message
from messages.message import User
from pyhop import hop

'''
We will simulate a distributed environment

So, there will be a singular world server through which all messages go
through.

Agents will interact with the server by messages

At a later stage, they will send actions for execution and whatnot
to the server

Currently, they will just be able to signal the start of an auction,
make bids on items available for auction
'''

name = ""
auction = {}
curr_bids = 0
num_bidders = 0

# Need in connections and out connecitons
def process_msg(conn, data):
    global curr_bids
    global num_bidders
    global auction

    if data.opcode == 0:
        # Registration opcode
        print("Opcode is 0")
    elif data.opcode == 1:
        # Response from server to auction, data is number of bidders
        num_bidders = data.data
        print("Num bidders: " + str(num_bidders))
        
    elif data.opcode == 2:
        # Auction was signaled, data is a list of items for sale
        print("Generating bid for auction")
        time.sleep(0.1)
        # Generate bids
        bids = {}
        for item in data.data:
            bids[item] = random.randint(0,100)
            print("Bid " + str(bids[item]) + " on " + item)
        
        # Send bids
        msg = Message(name, 3, bids)
        send_data = pickle.dumps(msg)
        conn.sendall(send_data)
        
    elif data.opcode == 3:
        # Bid, data is map of items to values
        print("Storing bids")
        # Store new bids
        curr_bids += 1
        for item in data.data:
            auction[item].append((data.name,data.data[item]))

        
        # If all bids collected, choose winners
        if curr_bids >= num_bidders:
            print("Generating assignments")
            winners = {}
            for item in auction:
                min_bid = 100000
                min_bidder = None
                for bid in auction[item]:
                    if bid[1] < min_bid:
                        min_bid = bid[1]
                        min_bidder = bid[0]
                if not min_bidder in winners:
                    winners[min_bidder] = [item]
                else:
                    winners[min_bidder].append(item)
                print("Bidder: " + min_bidder + " won task " + item)
            # Send winners
            msg = Message(name,4,winners)
            send_data = pickle.dumps(msg)
            conn.sendall(send_data)
        
    elif data.opcode == 4:
        # List of assignments
    
        for item in data.data:
            print("Assigned task " + item)
        
    else:
        pass


def client_program(port, signal_auction):
    global auction
    global curr_bids
    global num_bidders
    
    host = socket.gethostname()  # as both code is running on same pc
    server = socket.socket()  # instantiate
    server.connect((host, port))  # connect to the server

    msg = Message(name, 0, "hi")
    data = pickle.dumps(msg)
    server.sendall(data)
    # Listen continuously for new active users and other messages
    while True:
        # See if there is any incoming data from environment
        while True:
            readable,_,_ = select.select([server],[],[],1)
            if readable:
                raw_data = server.recv(2048)
                recv_data = pickle.loads(raw_data)
                process_msg(server, recv_data)
            else:
                break
        
        if signal_auction:
            auction_items = ["move1", "move2", "move3"]
            signal_auction = 0
            curr_bids = 0
            num_bidders = 0

            for item in auction_items:
                auction[item] = []
            msg = Message(name, 2, auction_items)
            data = pickle.dumps(msg)
            server.sendall(data)
            

    server.close()  # close the connection


if __name__ == '__main__':
    port = (int)(sys.argv[1])
    name = sys.argv[2]
    signal_auction = (int)(sys.argv[3])
    client_program(port, signal_auction)