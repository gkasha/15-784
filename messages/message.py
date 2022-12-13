# File for the message object used between clients and servers

# Opcode info
'''
0 = Registration, data is empty
1 = Registration, list of users given via connections
2 = Start an auction, list of items
3 = Send bid, dictionary mapping names to values
4 = Receive allocated task, list of names
'''
class Message(object):

    name = ""
    opcode = 0
    data = None

    def __init__(self, name, opcode, data):
        self.name = name
        self.opcode = opcode
        self.data = data

class User(object):
    connection = None
    server_address = None

    def User(self, conn, server_addr):
        self.connection = conn
        self.server_address = server_addr